// One map on a <canvas>: either a spinnable 3D globe or a flat world map, with pinch zoom,
// tap detection, and the tiny-country overlays (island ovals, rings, the Lesser Antilles bubble).
(function () {
  const GG = (window.GG = window.GG || {});
  const RAD = Math.PI / 180, DEG = 180 / Math.PI;
  const FLAT_CENTRE_LON = 10;
  const MAX_K = 800;
  const smoothLine = d3.line().curve(d3.curveCatmullRomClosed);

  GG.MapView = class MapView {
    // opts: { geo, mode: 'globe'|'flat', getState(c) -> 'good'|'bad'|'flash'|null, onTap(c), borders }
    constructor(canvas, opts) {
      this.canvas = canvas;
      this.ctx = canvas.getContext("2d");
      this.geo = opts.geo;
      this.opts = opts;
      this.mode = opts.mode || "globe";
      this.borders = opts.borders !== false;
      this.moving = false;
      this.t = d3.zoomIdentity;
      this.hits = { islands: [], bubbles: [] };
      this.readColours();
      this.zoom = d3.zoom().scaleExtent([1, MAX_K]).clickDistance(8)
        .on("start", () => { this.moving = true; clearTimeout(this.settle); })
        .on("zoom", e => { this.t = e.transform; this.requestDraw(); })
        .on("end", () => { clearTimeout(this.settle); this.settle = setTimeout(() => { this.moving = false; this.requestDraw(); }, 140); });
      this.sel = d3.select(canvas).call(this.zoom).on("dblclick.zoom", null);
      canvas.addEventListener("click", e => this.handleClick(e));
      this.resize();
    }

    readColours() {
      const cs = getComputedStyle(document.documentElement), v = n => cs.getPropertyValue(n).trim();
      this.col = { bg: v("--bg"), sea: v("--sea"), land: v("--land"), border: v("--border"), coast: v("--coast"),
        terr: v("--terr"), good: v("--good"), bad: v("--bad"), flash: v("--flash"), marker: v("--marker"),
        panel: v("--panel"), fg: v("--fg"), halo: v("--halo") };
    }

    // ----- size and projections -----
    resize() {
      const r = this.canvas.getBoundingClientRect();
      this.w = Math.max(50, r.width); this.h = Math.max(50, r.height);
      this.dpr = Math.min(window.devicePixelRatio || 1, 2.5);
      this.canvas.width = Math.round(this.w * this.dpr); this.canvas.height = Math.round(this.h * this.dpr);
      // flat base projection, fitted to the width
      this.flat = d3.geoNaturalEarth1().rotate([-FLAT_CENTRE_LON, 0]).fitWidth(this.w, { type: "Sphere" });
      const b = d3.geoPath(this.flat).bounds({ type: "Sphere" });
      this.BW = b[1][0]; this.BH = b[1][1];
      this.flatPaths = null; // rebuilt lazily for the new size
      // globe base radius
      this.R0 = Math.min(this.w, this.h) * 0.44;
      this.globe = d3.geoOrthographic().clipAngle(90).precision(0.3);
      this.zoom.extent([[0, 0], [this.w, this.h]]);
      this.applyMode();
    }

    applyMode() {
      if (this.mode === "flat") {
        this.zoom.scaleExtent([Math.min(1, this.h / this.BH), MAX_K])
          .translateExtent([[-this.BW * 0.08, -this.BH * 0.1], [this.BW * 1.08, this.BH * 1.1]]);
      } else {
        this.zoom.scaleExtent([0.9, MAX_K]).translateExtent([[-Infinity, -Infinity], [Infinity, Infinity]]);
      }
    }

    // globe rotation comes from the zoom transform: panning by D px turns the globe so the
    // ground under the finger follows it, and pinching zooms towards the fingers
    globeState(t = this.t) {
      const u = (t.x - this.w / 2) / t.k, v = (t.y - this.h / 2) / t.k;
      const lam = u / this.R0 * DEG;
      const phi = Math.max(-89, Math.min(89, -v / this.R0 * DEG));
      return { rotate: [lam, phi], scale: this.R0 * t.k };
    }
    globeTransform(lon, lat, k) {
      return d3.zoomIdentity.translate(this.w / 2 + k * this.R0 * (-lon) * RAD, this.h / 2 + k * this.R0 * lat * RAD).scale(k);
    }
    projection() {
      if (this.mode === "flat") {
        const t = this.t;
        return this.flat.copy().scale(this.flat.scale() * t.k)
          .translate([this.flat.translate()[0] * t.k + t.x, this.flat.translate()[1] * t.k + t.y]);
      }
      const g = this.globeState();
      return this.globe.rotate([g.rotate[0], g.rotate[1], 0]).scale(g.scale).translate([this.w / 2, this.h / 2]);
    }
    pxPerDeg() {
      return this.mode === "flat" ? this.t.k * this.BW / 360 : this.R0 * this.t.k * RAD;
    }
    centre() {
      if (this.mode === "flat") return this.flat.invert(this.t.invert([this.w / 2, this.h / 2]));
      const r = this.globeState().rotate;
      return [-r[0], -r[1]];
    }
    visible(ll) {
      if (this.mode === "flat") return true;
      return d3.geoDistance(ll, this.centre()) < Math.PI / 2 - 0.01;
    }

    // ----- moving the view -----
    setTransform(t, animate) {
      (animate ? this.sel.transition().duration(650) : this.sel).call(this.zoom.transform, t);
    }
    // centre on lon/lat with `spanDeg` degrees across the shorter side of the screen
    lookAt(lon, lat, spanDeg, animate = true) {
      const side = Math.min(this.w, this.h) * 0.9;
      if (this.mode === "flat") {
        const k = Math.max(this.zoom.scaleExtent()[0], Math.min(MAX_K, side / (spanDeg * this.BW / 360)));
        const p = this.flat([lon, lat]);
        this.setTransform(d3.zoomIdentity.translate(this.w / 2 - k * p[0], this.h / 2 - k * p[1]).scale(k), animate);
      } else {
        const k = Math.max(0.9, Math.min(MAX_K, side / (spanDeg * this.R0 * RAD)));
        // keep the turn short: pick the longitude nearest the current one
        const cur = this.centre()[0];
        let L = lon; while (L - cur > 180) L -= 360; while (cur - L > 180) L += 360;
        this.setTransform(this.globeTransform(L, lat, k), animate);
      }
    }
    // fit a lon/lat box [[w,s],[e,n]] (e may be > 180 for boxes crossing the date line)
    fitBox(box, animate = true) {
      const [[w, s], [e, n]] = box;
      const lon = (w + e) / 2, lat = (s + n) / 2;
      const span = Math.max((e - w) * Math.cos(lat * RAD) * Math.min(this.w, this.h) / this.w,
        (n - s) * Math.min(this.w, this.h) / this.h);
      this.lookAt(lon > 180 ? lon - 360 : lon, lat, span, animate);
    }
    world(animate = true) {
      if (this.mode === "flat") {
        const k = this.zoom.scaleExtent()[0] > 1 ? this.zoom.scaleExtent()[0] : 1;
        this.setTransform(d3.zoomIdentity.translate((this.w - this.BW * k) / 2, (this.h - this.BH * k) / 2).scale(k), animate);
      } else {
        const c = this.centre();
        this.setTransform(this.globeTransform(c[0], 15, 1), animate);
      }
    }
    // switch globe <-> flat, keeping the same place and roughly the same zoom
    setMode(mode) {
      if (mode === this.mode) return;
      const c = this.centre(), ppd = this.pxPerDeg();
      this.mode = mode;
      this.applyMode();
      const span = Math.min(this.w, this.h) * 0.9 / ppd;
      this.lookAt(c[0], c[1], span, false);
      this.requestDraw();
    }

    // ----- drawing -----
    requestDraw() {
      if (this.frame) return;
      this.frame = requestAnimationFrame(() => { this.frame = null; this.draw(); });
    }
    fillFor(f) {
      if (!f.c) return this.col.terr;
      const s = this.opts.getState(f.c);
      return s ? this.col[s] : this.col.land;
    }
    draw() {
      const ctx = this.ctx, dpr = this.dpr, col = this.col;
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      ctx.fillStyle = col.bg; ctx.fillRect(0, 0, this.w, this.h);
      if (this.mode === "flat") this.drawFlat(); else this.drawGlobe();
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      this.drawOverlays();
    }
    drawFlat() {
      const ctx = this.ctx, t = this.t, col = this.col;
      if (!this.flatPaths) {
        const path = d3.geoPath(this.flat);
        this.flatPaths = {
          sphere: new Path2D(path({ type: "Sphere" })),
          features: this.geo.f50.map(f => ({ f, p: new Path2D(path(f) || "") })),
          borders: new Path2D(path(this.geo.borders50) || ""),
          coast: new Path2D(path(this.geo.coast50) || ""),
        };
      }
      const P = this.flatPaths;
      ctx.setTransform(this.dpr * t.k, 0, 0, this.dpr * t.k, this.dpr * t.x, this.dpr * t.y);
      ctx.fillStyle = col.sea; ctx.fill(P.sphere);
      const groups = new Map();
      P.features.forEach(({ f, p }) => { const c = this.fillFor(f); if (!groups.has(c)) groups.set(c, []); groups.get(c).push(p); });
      groups.forEach((ps, c) => { ctx.fillStyle = c; ps.forEach(p => ctx.fill(p)); });
      ctx.lineJoin = "round";
      ctx.strokeStyle = col.coast; ctx.lineWidth = 0.6 / t.k; ctx.stroke(P.coast);
      if (this.borders) { ctx.strokeStyle = col.border; ctx.lineWidth = 0.7 / t.k; ctx.stroke(P.borders); }
    }
    drawGlobe() {
      const ctx = this.ctx, col = this.col, proj = this.projection();
      const path = d3.geoPath(proj, ctx);
      const light = this.moving && this.t.k < 4;
      const feats = light ? this.geo.f110 : this.geo.f50;
      const centre = this.centre();
      // what part of the globe is on screen (for skipping countries out of view)
      const R = proj.scale(), half = Math.hypot(this.w, this.h) / 2;
      const view = half >= R ? Math.PI / 2 : Math.asin(half / R);
      ctx.beginPath(); path({ type: "Sphere" }); ctx.fillStyle = col.sea; ctx.fill();
      const groups = new Map();
      feats.forEach(f => {
        if (d3.geoDistance(f.centroid, centre) > view + f.radius) return;
        const c = this.fillFor(f); if (!groups.has(c)) groups.set(c, []); groups.get(c).push(f);
      });
      groups.forEach((fs, c) => { ctx.beginPath(); fs.forEach(f => path(f)); ctx.fillStyle = c; ctx.fill(); });
      ctx.lineJoin = "round";
      ctx.beginPath(); path(light ? this.geo.coast110 : this.geo.coast50); ctx.strokeStyle = col.coast; ctx.lineWidth = 0.6; ctx.stroke();
      if (this.borders) { ctx.beginPath(); path(light ? this.geo.borders110 : this.geo.borders50); ctx.strokeStyle = col.border; ctx.lineWidth = 0.7; ctx.stroke(); }
      // soft rim so the globe reads as a ball
      ctx.beginPath(); path({ type: "Sphere" }); ctx.strokeStyle = col.halo; ctx.lineWidth = 1.5; ctx.stroke();
    }

    // island ovals, rings and the cluster bubble, all in screen pixels
    drawOverlays() {
      const ctx = this.ctx, col = this.col, proj = this.projection(), ppd = this.pxPerDeg(), geo = this.geo;
      const W = this.w, H = this.h, m = 40;
      const islands = [], rings = [], bubbles = [], hidden = new Set();
      // on the flat map, project a shape's points without splitting it at the map edge (Kiribati)
      const flat = this.mode === "flat", s0 = proj.scale(), tr = proj.translate();
      const norm = lon => { const l = lon - FLAT_CENTRE_LON; return ((l + 540) % 360) - 180; };
      const flatPt = (ll, ref) => {
        let l = norm(ll[0]);
        while (l - ref > 180) l -= 360;
        while (ref - l > 180) l += 360;
        const q = d3.geoNaturalEarth1Raw(l * RAD, ll[1] * RAD);
        return [tr[0] + s0 * q[0], tr[1] - s0 * q[1]];
      };
      const shapeOf = c => {
        if (!this.visible(c.shape.center)) return null;
        const ref = norm(c.shape.center[0]);
        const P = flat ? (ll => flatPt(ll, ref)) : proj;
        const [x, y] = P(c.shape.center);
        let pts = c.shape.ring.map(p => P(p));
        const xs = pts.map(p => p[0]), ys = pts.map(p => p[1]);
        const size = Math.max(d3.max(xs) - d3.min(xs), d3.max(ys) - d3.min(ys));
        const f = Math.max(1, c.minPx / Math.max(size, 0.01));
        if (f > 1) pts = pts.map(([px, py]) => [x + (px - x) * f, y + (py - y) * f]);
        const r = d3.max(pts, p => Math.hypot(p[0] - x, p[1] - y));
        return { c, x, y, r, f, pts };
      };
      geo.clusters.forEach(cl => {
        const ms = cl.members.map(shapeOf).filter(Boolean);
        if (ms.length < 2) return;
        let overlap = false;
        for (let i = 0; i < ms.length && !overlap; i++) for (let j = i + 1; j < ms.length; j++)
          if ((ms[i].f > 1 || ms[j].f > 1) && Math.hypot(ms[i].x - ms[j].x, ms[i].y - ms[j].y) < (ms[i].r + ms[j].r) / 2) { overlap = true; break; }
        if (!overlap) return;
        cl.members.forEach(c => hidden.add(c));
        bubbles.push({ cl, x: d3.mean(ms, s => s.x), y: d3.mean(ms, s => s.y), r: 13 });
      });
      geo.countries.forEach(c => {
        if (hidden.has(c)) return;
        if (c.shape) {
          const s = shapeOf(c);
          if (!s || s.x + s.r < -m || s.x - s.r > W + m || s.y + s.r < -m || s.y - s.r > H + m) return;
          islands.push(s);
        } else if (c.ring && c.sizeDeg * ppd < geo.ringPx && this.visible(c.anchor)) {
          const [x, y] = proj(c.anchor);
          if (x > -m && x < W + m && y > -m && y < H + m) rings.push({ c, x, y });
        }
      });
      islands.sort((a, b) => b.r - a.r); // bigger first, so smaller ones draw on top
      ctx.lineWidth = 1.3;
      islands.forEach(s => {
        const st = this.opts.getState(s.c);
        ctx.beginPath(); smoothLine.context(ctx)(s.pts);
        ctx.setLineDash(st ? [] : [4, 3]);
        ctx.globalAlpha = st ? 0.45 : 0.10; ctx.fillStyle = st ? col[st] : col.marker; ctx.fill();
        ctx.globalAlpha = 1; ctx.strokeStyle = st ? col[st] : col.marker; ctx.stroke();
      });
      ctx.setLineDash([]);
      rings.forEach(d => {
        const st = this.opts.getState(d.c);
        ctx.beginPath(); ctx.arc(d.x, d.y, geo.ringPx / 2, 0, 2 * Math.PI);
        ctx.lineWidth = st ? 2.5 : 1.5; ctx.strokeStyle = st ? col[st] : col.marker; ctx.stroke();
      });
      bubbles.forEach(b => {
        const sts = b.cl.members.map(c => this.opts.getState(c));
        const allGood = sts.every(s => s === "good"), anyBad = b.cl.members.some(c => this.opts.getState(c) === "bad" && this.opts.isTarget && this.opts.isTarget(c));
        ctx.beginPath(); ctx.arc(b.x, b.y, b.r, 0, 2 * Math.PI);
        ctx.globalAlpha = anyBad ? 0.35 : 0.9; ctx.fillStyle = anyBad ? col.bad : col.panel; ctx.fill(); ctx.globalAlpha = 1;
        ctx.setLineDash(allGood || anyBad ? [] : [4, 3]);
        ctx.lineWidth = anyBad ? 3 : allGood ? 2.5 : 1.6; ctx.strokeStyle = anyBad ? col.bad : allGood ? col.good : col.marker; ctx.stroke();
        ctx.setLineDash([]);
        ctx.fillStyle = col.fg; ctx.font = "600 12px Barlow, system-ui, sans-serif"; ctx.textAlign = "center"; ctx.textBaseline = "middle";
        ctx.fillText(String(b.cl.members.length), b.x, b.y);
      });
      this.hits = { islands: islands.slice().reverse(), bubbles };
    }

    // ----- tapping -----
    handleClick(e) {
      const r = this.canvas.getBoundingClientRect();
      const x = e.clientX - r.left, y = e.clientY - r.top;
      if (this.opts.onPoint && this.opts.onPoint(this, x, y)) return; // e.g. the magnifier
      const b = this.hits.bubbles.find(b => Math.hypot(b.x - x, b.y - y) <= b.r + 4);
      if (b) { this.zoomToCountries(b.cl.members); return; }
      const c = this.countryAt(x, y);
      if (c) this.opts.onTap(c, this);
    }
    countryAt(x, y) {
      const isl = this.hits.islands.find(s => d3.polygonContains(s.pts, [x, y]));
      if (isl) return isl.c;
      const ll = this.lonLatAt(x, y);
      if (!ll) return null;
      for (const c of this.geo.countries) {
        if (!c.feature || !inBounds(c.bounds, ll)) continue;
        if (d3.geoContains(c.feature, ll)) return c;
      }
      return null;
    }
    lonLatAt(x, y) {
      if (this.mode === "flat") {
        const p = this.t.invert([x, y]), ll = this.flat.invert(p);
        if (!ll || !isFinite(ll[0])) return null;
        // reject points outside the map outline
        return Math.abs(ll[1]) <= 90 && this.flat(ll) && Math.hypot(this.flat(ll)[0] - p[0], this.flat(ll)[1] - p[1]) < 1 ? ll : null;
      }
      const proj = this.projection();
      if (Math.hypot(x - this.w / 2, y - this.h / 2) > proj.scale()) return null;
      const ll = proj.invert([x, y]);
      return ll && isFinite(ll[0]) ? ll : null;
    }
    zoomToCountries(cs) {
      const pts = cs.flatMap(c => c.shape ? c.shape.ring : [c.bounds[0], c.bounds[1]]);
      const lls = pts.map(p => p.slice());
      if (lls.some(p => p[0] > 90) && lls.some(p => p[0] < -90)) lls.forEach(p => { if (p[0] < 0) p[0] += 360; });
      const w = d3.min(lls, p => p[0]), e = d3.max(lls, p => p[0]), s = d3.min(lls, p => p[1]), n = d3.max(lls, p => p[1]);
      this.fitBox([[w - 0.3, s - 0.3], [e + 0.3, n + 0.3]]);
    }
  };

  function inBounds(b, [lon, lat]) {
    if (lat < b[0][1] - 0.01 || lat > b[1][1] + 0.01) return false;
    if (b[0][0] <= b[1][0]) return lon >= b[0][0] - 0.01 && lon <= b[1][0] + 0.01;
    return lon >= b[0][0] - 0.01 || lon <= b[1][0] + 0.01; // crosses the date line
  }
})();
