// Loads the bundled map data and works out everything the map needs about each country:
// its shapes, where to put its marker, how big it is, and the tiny-country shapes from PLAN.md.
// All geometry here is in longitude/latitude, so it works on both the globe and the flat map.
(function () {
  const GG = (window.GG = window.GG || {});

  // ----- tiny-country settings (PLAN.md, "Tiny countries") -----
  const ISLANDS = new Set(("FJI KIR MHL FSM NRU PLW WSM SLB TON TUV VUT " +
    "ATG BHS BRB DMA GRD KNA LCA VCT TTO CPV STP COM MUS SYC MDV MLT SGP BHR").split(" "));
  const RINGS = new Set("VAT SMR MCO LIE AND QAT BRN TLS".split(" "));
  const MIN_PX = { WSM: 16, NRU: 16, CPV: 16, COM: 16, MUS: 16, SYC: 16, STP: 22, MDV: 14 };
  const DEFAULT_MIN_PX = 8;
  const CLUSTERS = [{ name: "Lesser Antilles", members: "ATG KNA DMA LCA VCT GRD BRB TTO".split(" ") }];
  const PAD = 0.25; // degrees of sea around island shapes
  // Tuvalu is missing from the 1:50m data, so its atolls are listed here
  const TUVALU = [[176.12, -5.68], [176.31, -6.29], [177.15, -7.48], [178.69, -7.47], [177.33, -7.21],
    [178.42, -8.0], [179.2, -8.52], [179.47, -10.78], [179.8, -9.4]];

  async function getJSON(url) {
    const r = await fetch(url);
    if (!r.ok) throw new Error("Could not load " + url);
    return r.json();
  }

  function featuresOf(topo, byId) {
    const groups = {};
    topo.objects.countries.geometries.forEach(g => (groups[g.id] = groups[g.id] || []).push(g));
    return Object.entries(groups).map(([id, gs]) => {
      const geometry = gs.length > 1 ? topojson.merge(topo, gs) : topojson.feature(topo, gs[0]).geometry;
      return { type: "Feature", id, geometry, c: byId[id] || null };
    });
  }

  // ----- small helpers for shapes in a local flat plane (degrees, x scaled by cos(lat)) -----
  function unwrap(lls) {
    const spans = lls.some(p => p[0] > 90) && lls.some(p => p[0] < -90);
    return spans ? lls.map(([lo, la]) => [lo < 0 ? lo + 360 : lo, la]) : lls.map(p => p.slice());
  }
  function makePlane(lls) {
    const lon0 = d3.mean(lls, p => p[0]), lat0 = d3.mean(lls, p => p[1]), k = Math.cos(lat0 * Math.PI / 180);
    return {
      to: ([lo, la]) => [(lo - lon0) * k, la],
      from: ([x, y]) => { let lo = lon0 + x / k; if (lo > 180) lo -= 360; return [lo, y]; },
    };
  }
  // oval along the islands' main direction (PCA), so chains get a squashed, tilted ellipse
  function ellipseFor(pts, pad) {
    const mx = d3.mean(pts, p => p[0]), my = d3.mean(pts, p => p[1]);
    let sxx = 0, syy = 0, sxy = 0;
    pts.forEach(([x, y]) => { const dx = x - mx, dy = y - my; sxx += dx * dx; syy += dy * dy; sxy += dx * dy; });
    const th = 0.5 * Math.atan2(2 * sxy, sxx - syy), cs = Math.cos(th), sn = Math.sin(th);
    const uv = pts.map(([x, y]) => [(x - mx) * cs + (y - my) * sn, -(x - mx) * sn + (y - my) * cs]);
    const u0 = d3.min(uv, p => p[0]), u1 = d3.max(uv, p => p[0]), v0 = d3.min(uv, p => p[1]), v1 = d3.max(uv, p => p[1]);
    const cu = (u0 + u1) / 2, cv = (v0 + v1) / 2;
    let a = (u1 - u0) / 2 + pad, b = (v1 - v0) / 2 + pad;
    b = Math.max(b, a * 0.3);
    let s = 1; uv.forEach(([u, v]) => { s = Math.max(s, ((u - cu) / a) ** 2 + ((v - cv) / b) ** 2); });
    a *= Math.sqrt(s); b *= Math.sqrt(s);
    return { cx: mx + cu * cs - cv * sn, cy: my + cu * sn + cv * cs, a, b, th };
  }
  function ellipsePts(e, n = 72) {
    const cs = Math.cos(e.th), sn = Math.sin(e.th), out = [];
    for (let i = 0; i < n; i++) {
      const t = i / n * 2 * Math.PI, u = e.a * Math.cos(t), v = e.b * Math.sin(t);
      out.push([e.cx + u * cs - v * sn, e.cy + u * sn + v * cs]);
    }
    return out;
  }
  // Kiribati: a sideways figure 8. West lobe = Gilbert Islands, larger east lobe = Phoenix + Line Islands,
  // joined by a waist that narrows without pinching shut, smoothed into one outline.
  function kiribatiShape(polys, toPlane, splitX) {
    const west = [], east = [];
    polys.forEach(pts => (d3.mean(pts, p => p[0]) < splitX ? west : east).push(...pts.map(toPlane)));
    const w = ellipseFor(west, PAD * 1.3); w.a *= 0.94; w.b *= 0.9;
    // pull the west end in towards Banaba (away from Nauru), keeping every island inside
    const sgn = Math.cos(w.th) >= 0 ? 1 : -1, ux = Math.cos(w.th) * sgn, uy = Math.sin(w.th) * sgn;
    const inside = e => west.every(([x, y]) => {
      const cs = Math.cos(e.th), sn = Math.sin(e.th), u = (x - e.cx) * cs + (y - e.cy) * sn, v = -(x - e.cx) * sn + (y - e.cy) * cs;
      return (u / (e.a - PAD * 0.5)) ** 2 + (v / (e.b - PAD * 0.5)) ** 2 <= 1;
    });
    for (let step = 0.035; step > 0.004; step -= 0.005) {
      const d = w.a * step, e = Object.assign({}, w, { cx: w.cx + ux * d, cy: w.cy + uy * d, a: w.a - d });
      if (inside(e)) { Object.assign(w, e); break; }
    }
    const eastE = ellipseFor(east, PAD * 2);
    const parts = [w, eastE];
    const dx = eastE.cx - w.cx, dy = eastE.cy - w.cy;
    parts.push({ cx: (w.cx + eastE.cx) / 2, cy: (w.cy + eastE.cy) / 2, a: Math.hypot(dx, dy) / 2,
      b: Math.min(w.b / 0.9, eastE.b) * 0.9, th: Math.atan2(dy, dx) });
    // smooth union of the three ovals, traced with d3.contours
    const ext = d3.max(parts, e => Math.max(e.a, e.b));
    const x0 = d3.min(parts, e => e.cx) - ext * 1.3, x1 = d3.max(parts, e => e.cx) + ext * 1.3;
    const y0 = d3.min(parts, e => e.cy) - ext * 1.3, y1 = d3.max(parts, e => e.cy) + ext * 1.3;
    const n = 240, m = Math.max(40, Math.round(n * (y1 - y0) / (x1 - x0))), K = 1.8, vals = new Array(n * m);
    for (let j = 0; j < m; j++) for (let i = 0; i < n; i++) {
      const x = x0 + (i + 0.5) * (x1 - x0) / n, y = y0 + (j + 0.5) * (y1 - y0) / m;
      let s = 0;
      parts.forEach(e => {
        const cs = Math.cos(e.th), sn = Math.sin(e.th), u = (x - e.cx) * cs + (y - e.cy) * sn, v = -(x - e.cx) * sn + (y - e.cy) * cs;
        s += Math.exp(-K * (Math.hypot(u / e.a, v / e.b) - 1));
      });
      vals[j * n + i] = Math.log(s) / K;
    }
    const cont = d3.contours().size([n, m]).thresholds([0])(vals)[0];
    const ring = cont.coordinates.map(p => p[0]).sort((p, q) => q.length - p.length)[0];
    return ring.slice(0, -1).filter((_, i) => i % 2 === 0).map(([gx, gy]) => [x0 + gx * (x1 - x0) / n, y0 + gy * (y1 - y0) / m]);
  }

  function islandShape(c, polys) {
    const all = unwrap(polys.flat());
    const plane = makePlane(all);
    let ringPlane;
    if (c.iso === "KIR") {
      let i = 0;
      const per = polys.map(p => { const s = all.slice(i, i + p.length); i += p.length; return s; });
      try { ringPlane = kiribatiShape(per, plane.to, 180); }
      catch (e) { console.error(e); ringPlane = ellipsePts(ellipseFor(all.map(plane.to), PAD)); }
    } else {
      ringPlane = ellipsePts(ellipseFor(all.map(plane.to), PAD));
    }
    const ring = ringPlane.map(plane.from);
    const cPlane = d3.polygonCentroid(ringPlane);
    return { ring, center: plane.from(cPlane) };
  }

  GG.loadGeo = async function () {
    const [t50, t110, countries] = await Promise.all([
      getJSON("data/world-50m.json"), getJSON("data/world-110m.json"), getJSON("data/countries.json")]);
    const byId = {}, byIso = {};
    countries.forEach(c => { byId[c.id] = c; byIso[c.iso] = c; });
    const f50 = featuresOf(t50, byId), f110 = featuresOf(t110, byId);
    const borders50 = topojson.mesh(t50, t50.objects.countries, (a, b) => a !== b);
    const borders110 = topojson.mesh(t110, t110.objects.countries, (a, b) => a !== b);
    const coast50 = topojson.mesh(t50, t50.objects.countries, (a, b) => a === b);
    const coast110 = topojson.mesh(t110, t110.objects.countries, (a, b) => a === b);

    // per-feature culling data for the globe: centroid and angular radius
    [f50, f110].forEach(fs => fs.forEach(f => {
      f.centroid = d3.geoCentroid(f);
      const b = d3.geoBounds(f);
      f.radius = Math.max(...[[b[0][0], b[0][1]], [b[1][0], b[1][1]], [b[0][0], b[1][1]], [b[1][0], b[0][1]]]
        .map(p => d3.geoDistance(p, f.centroid)));
      if (b[0][0] > b[1][0]) f.radius = Math.PI; // crosses the date line: never cull
    }));

    f50.forEach(f => {
      const c = f.c; if (!c) return;
      c.feature = f;
      c.bounds = d3.geoBounds(f);
      const polys = f.geometry.type === "MultiPolygon" ? f.geometry.coordinates : [f.geometry.coordinates];
      let best = polys[0], bestA = -1;
      polys.forEach(p => { const a = d3.geoArea({ type: "Polygon", coordinates: p }); if (a > bestA) { bestA = a; best = p; } });
      const main = { type: "Polygon", coordinates: best };
      c.anchor = d3.geoCentroid(main);
      const mb = d3.geoBounds(main);
      const latMid = (mb[0][1] + mb[1][1]) / 2;
      c.sizeDeg = Math.max((mb[1][0] - mb[0][0]) * Math.cos(latMid * Math.PI / 180), mb[1][1] - mb[0][1]);
      if (ISLANDS.has(c.iso)) c.shape = islandShape(c, polys.map(p => p[0]));
    });
    f110.forEach(f => { if (f.c) f.c.feature110 = f; });

    const tuv = byIso.TUV;
    tuv.shape = islandShape(tuv, TUVALU.map(p => [p]));
    tuv.anchor = tuv.shape.center; tuv.sizeDeg = 0; tuv.bounds = d3.geoBounds({ type: "MultiPoint", coordinates: TUVALU });

    countries.forEach(c => {
      c.minPx = MIN_PX[c.iso] || DEFAULT_MIN_PX;
      c.ring = RINGS.has(c.iso);
    });
    return {
      countries, byIso, f50, f110, borders50, borders110, coast50, coast110,
      clusters: CLUSTERS.map(cl => ({ name: cl.name, members: cl.members.map(i => byIso[i]) })),
      ringPx: DEFAULT_MIN_PX,
    };
  };
})();
