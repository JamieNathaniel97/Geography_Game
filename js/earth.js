// Earth mode (jobs/geoscience.md, stage 1): the solid Earth's layers on the world map, each with its own checkbox.
// Plates, plate boundaries, named ridges and trenches, volcanoes, seas, hotspots and the Ring of Fire; tap anything
// for its card (the Learning card, filled by the app's hooks). Data: data/earth/ (tools/build_earth.py), loaded the
// first time a layer is switched on. The map (js/mapview.js) calls draw(view) after the base map and tap(view, x, y)
// for every tap while Earth mode is on (view.earth = this module).
(function () {
  const GG = (window.GG = window.GG || {});
  const $ = id => document.getElementById(id);
  const LAYERS = [
    { id: "plates", label: "Plates" },
    { id: "boundaries", label: "Plate boundaries" },
    { id: "features", label: "Ridges & trenches" },
    { id: "volcanoes", label: "Volcanoes" },
    { id: "hotspots", label: "Hotspots" },
    { id: "ring", label: "Ring of Fire" },
    { id: "seas", label: "Seas & oceans" },
  ];
  // ready-made groups: each ticks exactly its layers (every layer still has its own checkbox)
  const GROUPS = [
    { label: "Plates", on: ["plates", "boundaries", "features"] },
    { label: "Ring of Fire", on: ["ring", "features", "volcanoes"] },
    { label: "Volcanoes", on: ["volcanoes", "hotspots"] },
    { label: "Oceans", on: ["seas", "features"] },
  ];
  const DEFAULT = ["plates", "boundaries", "features"];
  const FILES = { plates: "plates.json", boundaries: "boundaries.json", features: "features.json", volcanoes: "volcanoes.json",
    seas: "seas.json", hotspots: "hotspots.json", ring: "ring.json" };
  const KEY = "gq.earth";
  const saved = (() => { try { return JSON.parse(localStorage.getItem(KEY)) || {}; } catch (e) { return {}; } })();
  const save = () => { try { localStorage.setItem(KEY, JSON.stringify({ on: [...E.on], countries: E.countries })); } catch (e) { /* private mode */ } };

  const E = {
    on: new Set(Array.isArray(saved.on) ? saved.on.filter(id => FILES[id]) : DEFAULT),
    countries: !!saved.countries, // country borders over the Earth layers (off: coasts only)
    data: {}, loading: {}, sel: null, view: null, hooks: {}, col: {},
    hits: { volc: [], hot: [] },
  };

  // ----- data -----
  function need(id) {
    if (E.data[id] || E.loading[id]) return E.loading[id];
    E.loading[id] = fetch("data/earth/" + FILES[id]).then(r => { if (!r.ok) throw new Error(r.status); return r.json(); })
      .then(d => { E.data[id] = prep(id, d); if (E.view) E.view.requestDraw(); return E.data[id]; })
      .catch(() => { delete E.loading[id]; if (E.hooks.toast) E.hooks.toast("That layer didn't load. Check your connection.", 2600); });
    return E.loading[id];
  }
  const plateName = code => { const p = E.data.plates && E.data.plates.byCode[code]; return p ? p.properties.name.replace(/ plate$/, "") : code; };
  // a shape d3 reads inside out (more than half the sphere: the Southern Ocean, which rings the globe) is turned round
  function fixWinding(f) {
    if (d3.geoArea(f) <= 2 * Math.PI) return;
    const g = f.geometry, polys = g.type === "Polygon" ? [g.coordinates] : g.coordinates;
    polys.forEach(rings => rings.forEach(r => r.reverse()));
  }
  function prep(id, d) {
    if (id === "plates" || id === "seas") d.features.forEach(fixWinding);
    // seas: the area as d3 measures it (the build's figure is wrong for the ring-shaped Southern Ocean)
    if (id === "seas") d.features.forEach(f => { f.properties.area = Math.round(d3.geoArea(f) * 6371 * 6371 / 100) * 100; });
    if (id === "plates") {
      d.byCode = {}; d.byColour = [[], [], [], [], [], []];
      d.features.forEach(f => { d.byCode[f.properties.code] = f; d.byColour[f.properties.colour].push(f); });
      d.features.sort((a, b) => a.properties.area - b.properties.area); // (taps: the smallest plate that holds the point)
    }
    if (id === "boundaries") {
      d.byType = { divergent: [], convergent: [], transform: [] };
      d.features.forEach(f => d.byType[f.properties.type].push(f));
    }
    if (id === "features") {
      d.byGroup = { divergent: [], convergent: [], transform: [] };
      d.features.forEach(f => { f.properties.group = groupOf(f.properties.kind); d.byGroup[f.properties.group].push(f); });
    }
    if (id === "volcanoes") {
      const c = d.cols.reduce((o, k, i) => (o[k] = i, o), {});
      return d.rows.map(r => ({ num: r[c.num], name: r[c.name], ll: [r[c.lon], r[c.lat]], elev: r[c.elev], type: d.types[r[c.type]],
        last: r[c.last], country: d.countries[r[c.country]], pri: r[c.pri], setting: d.settings[r[c.setting]], rock: d.rocks[r[c.rock]],
        famous: r[c.famous] }));
    }
    if (id === "hotspots") {
      d.forEach(h => { h.line = h.chain ? { type: "LineString", coordinates: h.chain.map(p => [p[0], p[1]]) } : null; });
    }
    return d;
  }
  const groupOf = kind => (/ridge|rift/i.test(kind) ? "divergent" : /transform/i.test(kind) ? "transform" : "convergent");

  // ----- colours (CSS tokens, light and dark) -----
  function readColours() {
    const cs = getComputedStyle(document.documentElement), v = n => cs.getPropertyValue(n).trim();
    E.col = { plates: [0, 1, 2, 3, 4, 5].map(i => v("--e-plate-" + i)), divergent: v("--e-div"), convergent: v("--e-conv"),
      transform: v("--e-trans"), volc: v("--e-volc"), hot: v("--e-hot"), ring: v("--e-ring"), sea: v("--e-sea"),
      fg: v("--fg"), halo: v("--halo"), panel: v("--panel"), sel: v("--flash"), bg: v("--bg") };
  }

  // ----- drawing helpers -----
  // Flat map: each group's shapes as one Path2D in the flat map's own (zoom 1) coordinates, made once per map size
  // and drawn into every copy on screen; globe: drawn afresh each frame.
  let cacheFor = null, cache = new Map();
  function flatPath(view, key, objs) {
    if (cacheFor !== view.flat) { cacheFor = view.flat; cache = new Map(); }
    let p = cache.get(key);
    if (!p) {
      const path = d3.geoPath(view.flat); p = new Path2D();
      objs.forEach(o => { const s = path(o); if (s) p.addPath(new Path2D(s)); });
      cache.set(key, p);
    }
    return p;
  }
  // fill or stroke a group of shapes; widths and dashes in screen pixels
  function paint(view, key, objs, st) {
    if (!objs || !objs.length) return;
    const ctx = view.ctx, dpr = view.dpr, t = view.t;
    ctx.save();
    ctx.globalAlpha = st.alpha == null ? 1 : st.alpha;
    ctx.lineJoin = "round"; ctx.lineCap = "round";
    const go = (k, p) => {
      if (st.fill) { ctx.fillStyle = st.fill; if (p) ctx.fill(p); else ctx.fill(); }
      if (st.stroke) {
        ctx.strokeStyle = st.stroke; ctx.lineWidth = st.width / k; ctx.setLineDash(st.dash ? st.dash.map(d => d / k) : []);
        if (p) ctx.stroke(p); else ctx.stroke();
      }
    };
    if (view.mode === "flat") {
      const p = flatPath(view, key, objs), Wk = view.BW * t.k;
      view.copies().filter(dx => t.x + dx + Wk > 0 && t.x + dx < view.w).forEach(dx => {
        ctx.setTransform(dpr * t.k, 0, 0, dpr * t.k, dpr * (t.x + dx), dpr * t.y); go(t.k, p);
      });
    } else {
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      const path = d3.geoPath(view.projection(), ctx);
      ctx.beginPath(); objs.forEach(o => path(o)); go(1, null);
    }
    ctx.restore();
  }
  // a point's places on screen: one per flat copy, or one on the globe's near side
  function screenPts(view, ll, margin = 40) {
    if (view.mode === "flat") {
      const b = view.flat(ll); if (!b || b[1] < 0 || b[1] > view.BH) return [];
      const t = view.t, out = [];
      view.copies().forEach(dx => {
        const x = t.x + dx + b[0] * t.k, y = t.y + b[1] * t.k;
        if (x > -margin && x < view.w + margin && y > -margin && y < view.h + margin) out.push([x, y]);
      });
      return out;
    }
    if (!view.visible(ll)) return [];
    const p = view.projection()(ll);
    return p ? [p] : [];
  }
  // a line feature's pieces on screen, as lists of [x, y] (split where the globe hides it)
  function linesOf(g) { return g.type === "LineString" ? [g.coordinates] : g.type === "MultiLineString" ? g.coordinates : []; }
  function screenLines(view, f) {
    const out = [];
    if (view.mode === "flat") {
      if (f._bv !== view.flat) { f._b = linesOf(f.geometry || f).map(l => l.map(p => view.flat(p))); f._bv = view.flat; }
      const t = view.t;
      view.copies().forEach(dx => f._b.forEach(l => out.push(l.map(b => [t.x + dx + b[0] * t.k, t.y + b[1] * t.k]))));
      return out;
    }
    const P = view.projection(), c = view.centre();
    linesOf(f.geometry || f).forEach(l => {
      let cur = [];
      l.forEach(p => {
        if (d3.geoDistance(p, c) < Math.PI / 2 - 0.02) { const q = P(p); if (q) { cur.push(q); return; } }
        if (cur.length > 1) out.push(cur); cur = [];
      });
      if (cur.length > 1) out.push(cur);
    });
    return out;
  }
  function segDist(x, y, a, b) {
    const ex = b[0] - a[0], ey = b[1] - a[1], L = ex * ex + ey * ey;
    const u = L ? Math.max(0, Math.min(1, ((x - a[0]) * ex + (y - a[1]) * ey) / L)) : 0;
    return Math.hypot(a[0] + u * ex - x, a[1] + u * ey - y);
  }
  function nearestLine(view, feats, x, y, reach) {
    let best = null, bd = reach;
    feats.forEach(f => screenLines(view, f).forEach(l => {
      for (let i = 1; i < l.length; i++) {
        const a = l[i - 1], b = l[i];
        if (Math.min(a[0], b[0]) > x + bd || Math.max(a[0], b[0]) < x - bd || Math.min(a[1], b[1]) > y + bd || Math.max(a[1], b[1]) < y - bd) continue;
        const d = segDist(x, y, a, b); if (d < bd) { bd = d; best = f; }
      }
    }));
    return best;
  }

  // ----- the layers, in drawing order -----
  function draw(view) {
    if (!E.col.fg) readColours();
    const D = E.data, on = id => E.on.has(id) && D[id], col = E.col, ppd = view.pxPerDeg(), sel = E.sel;
    if (on("plates")) {
      D.plates.byColour.forEach((fs, i) => paint(view, "plates" + i, fs, { fill: col.plates[i], alpha: 0.24 }));
      if (!E.on.has("boundaries")) paint(view, "plateEdges", D.plates.features, { stroke: col.fg, width: 0.8, alpha: 0.35 });
    }
    if (sel && (sel.kind === "plate" || sel.kind === "sea")) paint(view, "sel:" + sel.kind + sel.id, [sel.o], { fill: col.sel, alpha: 0.22, stroke: col.sel, width: 2 });
    if (on("ring")) paint(view, "ring", [D.ring], { stroke: col.ring, width: ringWidth(ppd), alpha: sel && sel.kind === "ring" ? 0.55 : 0.3 });
    if (on("boundaries")) ["divergent", "convergent", "transform"].forEach(t => paint(view, "b-" + t, D.boundaries.byType[t], { stroke: col[t], width: 1.5, alpha: 0.85 }));
    if (on("features")) {
      const all = D.features.features;
      paint(view, "f-halo", all, { stroke: col.halo, width: 5, alpha: 0.55 });
      ["divergent", "convergent", "transform"].forEach(g => paint(view, "f-" + g, D.features.byGroup[g], { stroke: col[g], width: 2.8, alpha: 0.95 }));
    }
    if (sel && (sel.kind === "feature" || sel.kind === "boundary")) {
      paint(view, "sel:" + sel.kind + sel.id, [sel.o], { stroke: col.sel, width: 6, alpha: 0.9 });
    }
    if (on("hotspots")) paint(view, "chains", D.hotspots.filter(h => h.line).map(h => h.line), { stroke: col.hot, width: 1.6, dash: [1, 4], alpha: 0.85 });
    const ctx = view.ctx;
    ctx.save(); ctx.setTransform(view.dpr, 0, 0, view.dpr, 0, 0);
    const boxes = [];
    const fits = (x0, y0, x1, y1) => {
      if (boxes.some(b => x0 < b[2] && x1 > b[0] && y0 < b[3] && y1 > b[1])) return false;
      boxes.push([x0, y0, x1, y1]); return true;
    };
    E.hits = { volc: [], hot: [] };
    if (on("volcanoes")) drawVolcanoes(view, ctx, ppd);
    if (on("hotspots")) drawHotspots(view, ctx, ppd);
    // labels: oceans and plates first, then the named lines, the seas, the volcanoes
    if (on("seas")) drawSeaLabels(view, ctx, ppd, fits, true);
    if (on("plates")) drawPlateLabels(view, ctx, ppd, fits);
    if (on("features")) drawLineLabels(view, ctx, fits);
    if (on("seas")) drawSeaLabels(view, ctx, ppd, fits, false);
    if (on("hotspots") && ppd > 5) E.hits.hot.forEach(h => label(ctx, h.o.name.replace(/ hotspot$/, ""), h.x + 9, h.y, fits, { colour: col.hot, align: "left" }));
    if (on("volcanoes") && ppd > 6) E.hits.volc.forEach(h => { if (h.v.pri === 0 || ppd > 25) label(ctx, h.v.name, h.x + 7, h.y + 1, fits, { colour: col.fg, align: "left", size: 10 }); });
    ctx.restore();
  }
  const ringWidth = ppd => Math.max(9, Math.min(22, ppd * 1.6));
  function drawVolcanoes(view, ctx, ppd) {
    // world zoom: one per screen cell (the famous, then the recent, first); zoomed in: all of them
    const cell = ppd < 2 ? 16 : ppd < 6 ? 11 : ppd < 16 ? 7 : 0, used = new Set(), col = E.col;
    ctx.lineWidth = 1; ctx.strokeStyle = col.panel; ctx.fillStyle = col.volc;
    for (const v of E.data.volcanoes) {
      for (const [x, y] of screenPts(view, v.ll, 10)) {
        if (cell) { const k = Math.floor(x / cell) + "," + Math.floor(y / cell); if (used.has(k)) continue; used.add(k); }
        const s = v.pri === 0 ? 6 : 4.6, sel = E.sel && E.sel.kind === "volcano" && E.sel.o === v;
        ctx.beginPath(); ctx.moveTo(x, y - s); ctx.lineTo(x + s * 0.95, y + s * 0.7); ctx.lineTo(x - s * 0.95, y + s * 0.7); ctx.closePath();
        ctx.fillStyle = sel ? col.sel : col.volc; ctx.fill(); ctx.stroke();
        E.hits.volc.push({ v, x, y });
      }
    }
  }
  function drawHotspots(view, ctx, ppd) {
    const col = E.col;
    E.data.hotspots.forEach(h => {
      if (h.chain && ppd > 4) h.chain.slice(1).forEach(c => screenPts(view, [c[0], c[1]]).forEach(([x, y]) => {
        ctx.beginPath(); ctx.arc(x, y, 2.2, 0, 2 * Math.PI); ctx.fillStyle = col.hot; ctx.globalAlpha = 0.8; ctx.fill(); ctx.globalAlpha = 1;
        if (ppd > 12) { ctx.font = "600 9px Barlow, system-ui, sans-serif"; ctx.fillStyle = col.hot; ctx.textAlign = "left"; ctx.textBaseline = "middle"; ctx.fillText(c[2] + " Ma", x + 4, y); }
      }));
      screenPts(view, h.ll, 12).forEach(([x, y]) => {
        const sel = E.sel && E.sel.kind === "hotspot" && E.sel.o === h;
        ctx.beginPath(); ctx.arc(x, y, 9, 0, 2 * Math.PI); ctx.strokeStyle = sel ? col.sel : col.hot; ctx.lineWidth = sel ? 3 : 1.6; ctx.globalAlpha = 0.7; ctx.stroke(); ctx.globalAlpha = 1;
        ctx.beginPath(); ctx.arc(x, y, 4.5, 0, 2 * Math.PI); ctx.fillStyle = sel ? col.sel : col.hot; ctx.fill();
        ctx.lineWidth = 1; ctx.strokeStyle = col.panel; ctx.stroke();
        E.hits.hot.push({ o: h, x, y });
      });
    });
  }
  // a label with a halo; skipped where it would overlap one already drawn
  function label(ctx, text, x, y, fits, o = {}) {
    const size = o.size || 11;
    ctx.font = `${o.italic ? "italic " : ""}${o.weight || 600} ${size}px Barlow, system-ui, sans-serif`;
    if ("letterSpacing" in ctx) ctx.letterSpacing = o.spacing || "0px";
    const w = ctx.measureText(text).width, x0 = o.align === "left" ? x : x - w / 2;
    if (!fits(x0 - 2, y - size * 0.6, x0 + w + 2, y + size * 0.6)) { if ("letterSpacing" in ctx) ctx.letterSpacing = "0px"; return false; }
    ctx.textAlign = o.align || "center"; ctx.textBaseline = "middle";
    ctx.lineWidth = 2.5; ctx.strokeStyle = E.col.halo; ctx.globalAlpha = o.alpha || 1; ctx.strokeText(text, x, y);
    ctx.fillStyle = o.colour || E.col.fg; ctx.fillText(text, x, y); ctx.globalAlpha = 1;
    if ("letterSpacing" in ctx) ctx.letterSpacing = "0px";
    return true;
  }
  function drawPlateLabels(view, ctx, ppd, fits) {
    E.data.plates.features.slice().sort((a, b) => b.properties.area - a.properties.area).forEach(f => {
      const p = f.properties, px = Math.sqrt(p.area) / 111 * ppd; // the plate's size on screen
      if (px < 80) return;
      screenPts(view, p.label, 0).forEach(([x, y]) => label(ctx, plateName(p.code).toUpperCase(), x, y, fits, { size: px > 300 ? 13 : 11, spacing: "1.5px", alpha: 0.75 }));
    });
  }
  function drawSeaLabels(view, ctx, ppd, fits, oceans) {
    const maxRank = ppd < 4 ? 2 : ppd < 8 ? 3 : ppd < 16 ? 5 : 10;
    E.data.seas.features.forEach(f => {
      const p = f.properties;
      if ((p.kind === "Ocean") !== oceans || p.rank > maxRank || (!oceans && p.kind !== "Sea" && ppd < 8)) return;
      screenPts(view, p.label, 0).forEach(([x, y]) => label(ctx, oceans ? p.name.toUpperCase() : p.name, x, y, fits,
        { italic: true, size: oceans ? 13 : 11, spacing: oceans ? "2px" : "0px", colour: E.col.sea }));
    });
  }
  // a name along its line: at the middle of its longest stretch on screen, turned to follow it (kept upright)
  function drawLineLabels(view, ctx, fits) {
    E.data.features.features.forEach(f => {
      let best = null, bl = 0;
      screenLines(view, f).forEach(l => {
        const on = l.filter(p => p[0] > 0 && p[0] < view.w && p[1] > 0 && p[1] < view.h);
        if (on.length < 2) return;
        let L = 0; for (let i = 1; i < on.length; i++) L += Math.hypot(on[i][0] - on[i - 1][0], on[i][1] - on[i - 1][1]);
        if (L > bl) { bl = L; best = on; }
      });
      if (!best) return;
      const name = f.properties.name;
      ctx.font = "italic 600 10.5px Barlow, system-ui, sans-serif";
      const w = ctx.measureText(name).width;
      if (bl < w + 24) return;
      // the point half way along, and the direction over the text's length there
      let half = bl / 2, i = 1;
      for (; i < best.length; i++) { const d = Math.hypot(best[i][0] - best[i - 1][0], best[i][1] - best[i - 1][1]); if (half <= d) break; half -= d; }
      const a = best[Math.max(0, i - 1)], b = best[Math.min(best.length - 1, i)];
      const seg = Math.hypot(b[0] - a[0], b[1] - a[1]) || 1, u = half / seg;
      const x = a[0] + (b[0] - a[0]) * u, y = a[1] + (b[1] - a[1]) * u;
      const back = pointAt(best, bl / 2 - w / 2), fwd = pointAt(best, bl / 2 + w / 2);
      let ang = Math.atan2(fwd[1] - back[1], fwd[0] - back[0]);
      if (ang > Math.PI / 2) ang -= Math.PI; if (ang < -Math.PI / 2) ang += Math.PI;
      const r = Math.max(w / 2, 8) * Math.abs(Math.cos(ang)) + 6 * Math.abs(Math.sin(ang)), h = Math.max(w / 2, 8) * Math.abs(Math.sin(ang)) + 6;
      if (!fits(x - r, y - h, x + r, y + h)) return;
      ctx.save(); ctx.translate(x, y); ctx.rotate(ang); ctx.translate(0, -7);
      ctx.textAlign = "center"; ctx.textBaseline = "middle";
      ctx.lineWidth = 3; ctx.strokeStyle = E.col.halo; ctx.strokeText(name, 0, 0);
      ctx.fillStyle = E.col.fg; ctx.fillText(name, 0, 0);
      ctx.restore();
    });
  }
  function pointAt(l, d) {
    for (let i = 1; i < l.length; i++) {
      const s = Math.hypot(l[i][0] - l[i - 1][0], l[i][1] - l[i - 1][1]);
      if (d <= s) { const u = s ? d / s : 0; return [l[i - 1][0] + (l[i][0] - l[i - 1][0]) * u, l[i - 1][1] + (l[i][1] - l[i - 1][1]) * u]; }
      d -= s;
    }
    return l[l.length - 1];
  }

  // ----- taps: points first, then the named lines, the Ring of Fire, any boundary, then seas (over water) and plates
  function hitTest(view, x, y) {
    const D = E.data, on = id => E.on.has(id) && D[id];
    let best = null, bd = 14;
    if (on("hotspots")) E.hits.hot.forEach(h => { const d = Math.hypot(h.x - x, h.y - y); if (d < bd) { bd = d; best = { kind: "hotspot", o: h.o, id: h.o.id }; } });
    if (!best && on("volcanoes")) { bd = 12; E.hits.volc.forEach(h => { const d = Math.hypot(h.x - x, h.y - y); if (d < bd) { bd = d; best = { kind: "volcano", o: h.v, id: h.v.num }; } }); }
    if (best) return best;
    if (on("features")) { const f = nearestLine(view, D.features.features, x, y, 10); if (f) return { kind: "feature", o: f, id: f.properties.id }; }
    if (on("ring") && nearestLine(view, [D.ring], x, y, ringWidth(view.pxPerDeg()) / 2 + 2)) return { kind: "ring", o: D.ring, id: "ring" };
    if (on("boundaries")) { const b = nearestLine(view, D.boundaries.features, x, y, 8); if (b) return { kind: "boundary", o: b, id: D.boundaries.features.indexOf(b) }; }
    const ll = view.lonLatAt(x, y);
    if (!ll) return null;
    if (on("seas") && !view.landAt(x, y)) {
      const s = D.seas.features.filter(f => d3.geoContains(f, ll)).sort((a, b) => a.properties.area - b.properties.area)[0];
      if (s) return { kind: "sea", o: s, id: s.properties.name };
    }
    if (on("plates")) { const p = D.plates.features.find(f => d3.geoContains(f, ll)); if (p) return { kind: "plate", o: p, id: p.properties.code }; }
    return null;
  }
  function tap(view, x, y) {
    const h = hitTest(view, x, y);
    E.sel = h;
    if (h) showCard(h); else if (E.hooks.hideCard) E.hooks.hideCard();
    view.requestDraw();
    return h;
  }

  // ----- cards -----
  const num = n => Math.round(n).toLocaleString("en-GB");
  const km2 = a => (a >= 1e6 ? `about ${(a / 1e6).toFixed(a >= 1e7 ? 0 : 1)} million km²` : `about ${num(Math.round(a / 1000) * 1000)} km²`);
  const speed = mm => (mm >= 10 ? `about ${(mm / 10).toFixed(mm >= 100 ? 0 : 1)} cm a year` : `about ${mm.toFixed(0)} mm a year`);
  const depthTxt = m => (m < 0 ? `about ${num(-m)} m below sea level` : `about ${num(m)} m above sea level`);
  const TYPE_TXT = { divergent: "Divergent: the plates move apart", convergent: "Convergent: the plates move together", transform: "Transform: the plates slide past each other" };
  const TYPE_NOTE = {
    divergent: "New crust forms here as the plates pull apart and magma rises to fill the gap.",
    convergent: "One plate sinks under the other (subduction), or two continents crumple into mountains.",
    transform: "The plates grind sideways past each other, building up strain that is released in earthquakes.",
  };
  const yearTxt = y => (y == null ? "Unknown" : y < 0 ? `${num(-y)} BCE` : String(y));
  function showCard(h) {
    const card = E.hooks.card; if (!card) return;
    const p = h.o.properties || {};
    if (h.kind === "plate") {
      const lens = plateBoundaryLengths(p.code);
      card({ name: p.name, sub: p.kind + (p.alias ? ` · also called the ${p.alias}` : ""),
        rows: [["Area", km2(p.area)], ["Moves", p.motion], ["Neighbours", p.neighbours.slice(0, 7).map(plateName).join(", ") + (p.neighbours.length > 7 ? "…" : "")]],
        note: p.note,
        more: lens ? [["Spreading ridges", lens.divergent], ["Subduction and collision", lens.convergent], ["Transform faults", lens.transform]] : [],
        credit: "Plate model: Bird (2003), PB2002." });
    } else if (h.kind === "boundary") {
      card({ name: `${plateName(p.plates[0])}–${plateName(p.plates[1])} boundary`, sub: (E.data.boundaries.classes || {})[p.cls] || "Plate boundary",
        rows: [["Type", TYPE_TXT[p.type]], ["Speed", speed(p.rate)], ["This stretch", `about ${num(p.len)} km`], [p.depth < 0 ? "Depth" : "Height", depthTxt(p.depth) + " on average"],
          ["Ocean floor age", p.age ? `about ${p.age} million years` : ""]],
        note: TYPE_NOTE[p.type], credit: "Measured from PB2002 (Bird 2003)." });
    } else if (h.kind === "feature") {
      card({ name: p.name, sub: p.kind,
        rows: [["Plates", p.plates.slice(0, 4).map(plateName).join(", ")], ["Length", `about ${num(Math.round(p.len / 100) * 100)} km`], ["Speed", speed(p.rate)],
          ["Deepest", p.depthMax ? `about ${num(p.depthMax)} m` : ""], ...p.facts],
        note: p.note,
        more: [[p.depth < 0 ? "Average depth" : "Average height", depthTxt(p.depth)], ["Fastest", speed(p.rateMax)], ["Ocean floor age", p.age ? `about ${p.age} million years on average` : ""]],
        credit: "Lengths, speeds and depths measured from PB2002 (Bird 2003)." });
    } else if (h.kind === "ring") {
      card({ name: p.name, sub: p.kind, rows: [...p.facts, ["Subduction zones in it", `about ${num(Math.round(p.len / 100) * 100)} km (PB2002)`]], note: p.note });
    } else if (h.kind === "volcano") {
      const v = h.o;
      card({ name: v.name, sub: [v.type, v.country].filter(Boolean).join(" · "),
        rows: [["Height", v.elev == null ? "" : v.elev < 0 ? `${num(-v.elev)} m below sea level (under the sea)` : `${num(v.elev)} m`],
          ["Last eruption", yearTxt(v.last)], ["Known for", v.famous]],
        more: [["Setting", v.setting], ["Main rock", v.rock]],
        credit: "Global Volcanism Program, Smithsonian Institution: Volcanoes of the World." });
      volcanoNote(v).then(text => { if (text && E.sel && E.sel.o === v && E.hooks.cardMore) E.hooks.cardMore(text); });
    } else if (h.kind === "hotspot") {
      const o = h.o, oldest = o.chain ? o.chain[o.chain.length - 1][2] : null;
      card({ name: o.name, sub: "Hotspot (mantle plume)", rows: [...(o.facts || []), ["Oldest part of its trail", oldest ? `about ${oldest} million years` : ""]], note: o.note });
    } else if (h.kind === "sea") {
      card({ name: p.name, sub: p.lake ? "Lake (called a sea)" : p.kind + (p.ocean ? ` · part of the ${p.ocean}` : ""),
        rows: [["Area", km2(p.area)], ["Deepest point", p.deepest]], credit: "Seas: Natural Earth." });
    }
  }
  function plateBoundaryLengths(code) {
    const B = E.data.boundaries; if (!B) return null;
    const L = { divergent: 0, convergent: 0, transform: 0 };
    B.features.forEach(f => { if (f.properties.plates.includes(code)) L[f.properties.type] += f.properties.len; });
    const fmt = v => (v ? `about ${num(Math.round(v / 100) * 100)} km` : "");
    return { divergent: fmt(L.divergent), convergent: fmt(L.convergent), transform: fmt(L.transform) };
  }
  const notes = {};
  function volcanoNote(v) {
    const k = Math.floor(v.num / 10000);
    if (!notes[k]) notes[k] = fetch(`data/earth/vnotes/${k}.json`).then(r => r.json()).catch(() => { delete notes[k]; return {}; });
    return notes[k].then(n => n[v.num] || "");
  }

  // ----- the Layers panel -----
  function buildPanel() {
    $("layerGroups").innerHTML = GROUPS.map((g, i) => `<button class="chip" data-g="${i}" type="button">${g.label}</button>`).join("");
    $("layerList").innerHTML = LAYERS.map(l => `<label class="lprow"><input type="checkbox" data-l="${l.id}"><span class="lpsw lpsw-${l.id}" aria-hidden="true"></span>${l.label}</label>`).join("")
      + `<label class="lprow lpcountries"><input type="checkbox" data-l="countries"><span class="lpsw lpsw-countries" aria-hidden="true"></span>Country borders</label>`;
    $("layerList").addEventListener("change", e => {
      const id = e.target.dataset.l; if (!id) return;
      if (id === "countries") { E.countries = e.target.checked; if (E.hooks.setBorders) E.hooks.setBorders(E.countries); }
      else if (e.target.checked) { E.on.add(id); need(id); } else E.on.delete(id);
      if (E.sel && !layerOf(E.sel.kind)) { E.sel = null; if (E.hooks.hideCard) E.hooks.hideCard(); }
      save(); syncPanel(); if (E.view) E.view.requestDraw();
    });
    $("layerGroups").addEventListener("click", e => {
      const b = e.target.closest("button"); if (!b) return;
      E.on = new Set(GROUPS[+b.dataset.g].on); E.on.forEach(need);
      if (E.sel && !layerOf(E.sel.kind)) { E.sel = null; if (E.hooks.hideCard) E.hooks.hideCard(); }
      save(); syncPanel(); if (E.view) E.view.requestDraw();
    });
    $("layersBtn").onclick = () => setPanel($("layerPanel").hidden);
    $("layerClose").onclick = () => setPanel(false);
  }
  const KIND_LAYER = { plate: "plates", boundary: "boundaries", feature: "features", volcano: "volcanoes", hotspot: "hotspots", ring: "ring", sea: "seas" };
  const layerOf = kind => E.on.has(KIND_LAYER[kind]);
  function syncPanel() {
    $("layerList").querySelectorAll("input").forEach(i => { i.checked = i.dataset.l === "countries" ? E.countries : E.on.has(i.dataset.l); });
    $("layerGroups").querySelectorAll("button").forEach(b => {
      const g = GROUPS[+b.dataset.g], same = g.on.length === E.on.size && g.on.every(id => E.on.has(id));
      b.classList.toggle("on", same);
    });
  }
  function setPanel(open) {
    $("layerPanel").hidden = !open;
    $("layersBtn").classList.toggle("on", open); $("layersBtn").setAttribute("aria-expanded", open);
    if (open) syncPanel();
  }

  // ----- entering and leaving Earth mode -----
  function init(hooks) { E.hooks = hooks || {}; buildPanel(); }
  function enter(view) {
    E.view = view; view.earth = api; view.noMarkers = true;
    readColours();
    need("plates"); E.on.forEach(need);
    $("layersBtn").hidden = false;
    if (E.hooks.setBorders) E.hooks.setBorders(E.countries);
    view.requestDraw();
  }
  function leave(view) {
    if (view.earth !== api) return;
    view.earth = null; view.noMarkers = false; E.sel = null; E.view = null;
    $("layersBtn").hidden = true; setPanel(false);
    view.requestDraw();
  }
  function clearSel() { if (E.sel) { E.sel = null; if (E.view) E.view.requestDraw(); } }

  const api = { init, enter, leave, draw, tap, hitTest, readColours, clearSel, closePanel: () => setPanel(false), need, state: E, LAYERS, GROUPS };
  GG.Earth = api;
})();
