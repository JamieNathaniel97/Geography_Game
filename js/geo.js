// Loads the bundled map data and works out everything the map needs about each country:
// its shapes, where to put its marker, how big it is, and the tiny-country shapes from PLAN.md.
// All geometry here is in longitude/latitude, so it works on both the globe and the flat map.
(function () {
  const GG = (window.GG = window.GG || {});

  // ----- tiny-country settings (PLAN.md, "Tiny countries") -----
  const ISLANDS = new Set(("FJI KIR MHL FSM NRU PLW WSM SLB TON TUV VUT " +
    "ATG BHS BRB DMA GRD KNA LCA VCT TTO CPV STP COM MUS SYC MDV MLT SGP BHR").split(" "));
  const RINGS = new Set("VAT SMR MCO LIE AND QAT BRN TLS".split(" "));
  // rings that start at 8 px fully zoomed out and grow smoothly with zoom (2026-11-14)
  const ADAPTIVE_RINGS = new Set("VAT SMR MCO LIE AND BRN TLS QAT".split(" "));
  const MIN_PX = { WSM: 16, NRU: 16, CPV: 16, COM: 16, MUS: 16, SYC: 16, STP: 22, MDV: 30 };
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

  // country shapes from the topology, in batches with pauses between them (see `pause` below)
  async function featuresOf(topo, byId, object = "countries") {
    const groups = {};
    topo.objects[object].geometries.forEach(g => (groups[g.id] = groups[g.id] || []).push(g));
    const out = [];
    for (const [n, [id, gs]] of Object.entries(groups).entries()) {
      if (n % 12 === 11) await new Promise(r => setTimeout(r, 0));
      const geometry = gs.length > 1 ? topojson.merge(topo, gs) : topojson.feature(topo, gs[0]).geometry;
      out.push({ type: "Feature", id, geometry, c: byId[id] || null });
    }
    return out;
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

  // Terrain: data/relief.jpg is a 4096x2048 whole-world shaded relief (plate carree) where white = flat.
  // Returns the image plus its grey values for the globe, which re-projects it pixel by pixel.
  let reliefPromise = null;
  GG.loadRelief = function () {
    if (!reliefPromise) reliefPromise = new Promise((resolve, reject) => {
      const img = new Image();
      img.onload = () => {
        const w = img.naturalWidth, h = img.naturalHeight, cv = document.createElement("canvas");
        cv.width = w; cv.height = h;
        const cx = cv.getContext("2d"); cx.drawImage(img, 0, 0);
        const rgba = cx.getImageData(0, 0, w, h).data, grey = new Uint8Array(w * h);
        for (let i = 0, j = 0; i < grey.length; i++, j += 4) grey[i] = rgba[j];
        // smaller, averaged copies (mip levels) so the globe can read the one that suits the zoom
        const levels = [{ w, h, grey }];
        while (levels[levels.length - 1].w > 256) {
          const p = levels[levels.length - 1], nw = p.w >> 1, nh = p.h >> 1, g = new Uint8Array(nw * nh);
          for (let y = 0; y < nh; y++) for (let x = 0; x < nw; x++) {
            const i = 2 * y * p.w + 2 * x;
            g[y * nw + x] = (p.grey[i] + p.grey[i + 1] + p.grey[i + p.w] + p.grey[i + p.w + 1] + 2) >> 2;
          }
          levels.push({ w: nw, h: nh, grey: g });
        }
        // sharper tiles for the zoomed-in flat map (optional: terrain still works without them)
        fetch("data/relief/index.json").then(r => r.ok ? r.json() : null).catch(() => null).then(ix => {
          const tiles = ix && { size: ix.tile, levels: ix.levels.map(l => ({ w: l.w, h: l.h, set: new Set(l.tiles) })) };
          resolve({ img, w, h, grey, levels, tiles });
        });
      };
      img.onerror = () => { reliefPromise = null; reject(new Error("Could not load terrain")); };
      img.src = "data/relief.jpg";
    });
    return reliefPromise;
  };

  // Loading is split into small steps with a pause between them, so the splash animation can keep drawing
  // (on a phone, doing it all in one go froze the splash for the best part of a second).
  const pause = () => new Promise(r => setTimeout(r, 0));

  // ----- US states (build 3): the same shape of data as the world map, so the map and games work unchanged -----
  const US_RINGS = new Set(["RI", "DE"]); // small states with an adaptive circle
  GG.loadUS = async function () {
    const [topo, states] = await Promise.all([getJSON("data/us-states.json"), getJSON("data/states.json")]);
    const byId = {}, byIso = {};
    states.forEach(c => { byId[c.id] = c; byIso[c.iso] = c; });
    await pause();
    const feats = await featuresOf(topo, byId, "states");
    prepareParts(feats, US_RINGS, "us/");
    const borders = topojson.feature(topo, topo.objects.borders), coast = topojson.feature(topo, topo.objects.coast);
    return { kind: "us", countries: states, byIso, f50: feats, f110: feats, borders50: borders, borders110: borders,
      coast50: coast, coast110: coast, clusters: [], ringPx: DEFAULT_MIN_PX,
      // borders between just some of the states (the statehood timeline only draws the ones that existed)
      bordersWhere: test => topojson.mesh(topo, topo.objects.states, (a, b) => a !== b && test(byId[a.id], byId[b.id])) };
  };
  // the parts of a country map (states, provinces): tap and label data, like the world map's countries
  // `ringDeg`: parts smaller than this (degrees across) also get a circle, e.g. the City of London or Sark
  function prepareParts(feats, rings, flagDir, ringDeg = 0) {
    for (const f of feats) {
      f.centroid = d3.geoCentroid(f); f.radius = Math.PI;
      const c = f.c; if (!c) continue;
      c.feature = f;
      c.flagKey = c.flagKey || flagDir + c.iso; // data/flags/<flagKey>.webp (the UK data names it: several share a flag)
      c.bounds = d3.geoBounds(f);
      const polys = f.geometry.type === "MultiPolygon" ? f.geometry.coordinates : [f.geometry.coordinates];
      let best = polys[0], bestA = -1;
      polys.forEach(p => { const a = d3.geoArea({ type: "Polygon", coordinates: p }); if (a > bestA) { bestA = a; best = p; } });
      const main = { type: "Polygon", coordinates: best }, mb = d3.geoBounds(main);
      c.anchor = c.anchorLL || d3.geoCentroid(main); // (the build gives a point inside when the centre falls outside, e.g. Gansu)
      c.sizeDeg = Math.max((mb[1][0] - mb[0][0]) * Math.cos((mb[0][1] + mb[1][1]) / 2 * Math.PI / 180), mb[1][1] - mb[0][1]);
      c.minPx = DEFAULT_MIN_PX;
      c.ring = c.ringAdaptive = rings.has(c.iso) || c.sizeDeg < ringDeg;
    }
  }
  // a country map stored as plain GeoJSON with its border and coast lines (tools/build_ca.py, tools/build_uk.py)
  async function loadShapes(shapesUrl, itemsUrl, kind, flagDir, rings, lakes, ringDeg) {
    const [fc, items] = await Promise.all([getJSON(shapesUrl), getJSON(itemsUrl)]);
    GG.fixWinding(fc);
    const byId = {}, byIso = {};
    items.forEach(c => { byId[c.id] = c; byIso[c.iso] = c; });
    await pause();
    const feats = fc.features.map(f => ({ type: "Feature", id: f.id, geometry: f.geometry, c: byId[f.id] || null }));
    prepareParts(feats, rings, flagDir, ringDeg);
    // with each border's two parts recorded (Australia), a timeline can draw only the borders that existed then
    const bordersWhere = fc.pairs ? test => ({ type: "MultiLineString", coordinates: fc.pairs
      .filter(([a, b]) => test(byId[a], byId[b])).flatMap(([, , g]) => g.type === "LineString" ? [g.coordinates] : g.coordinates) }) : null;
    return { kind, countries: items, byIso, f50: feats, f110: feats, borders50: fc.borders, borders110: fc.borders, bordersWhere,
      detail: fc.detail || null, // the detail level's tile index (tools/detail.py), if the map has one
      coast50: fc.coast, coast110: fc.coast, clusters: [], ringPx: DEFAULT_MIN_PX,
      lakes: lakes || null, lakes110: lakes || null,
      nationBorders: fc.nations || null, // UK: between England, Scotland, Wales (and NI and the Republic), drawn bolder
      scaleBars: fc.scaleBars || null, // insets' own fixed scale bars (tools/build_country.py, tools/build_es.py)
      frames: fc.frames || null, // insets' frames, drawn straight (tools/build_es.py: the Canaries)
      disputed: fc.disputed || null }; // India and others: disputed borders, drawn dotted
  }
  // ----- Britain and Ireland's counties (build 4): set = "historic" or "ceremonial"; each includes Ireland's 32
  // counties and the Crown Dependencies, with France as a grey area. Small counties (the City of London, the
  // Channel Islands, Clackmannanshire...) get a circle.
  // the UK and Ireland's five countries (Learning mode's first view; the counties come after "Focus on ...")
  GG.loadUKNations = async lakes => {
    const g = await loadShapes("data/uk-nations.json", "data/uk-nations-info.json", "ukn", "uk/", new Set(), lakes, 0.25);
    g.nationBorders = g.borders50; // every border here is between countries: drawn bold
    return g;
  };
  GG.loadUK = (set, lakes) => loadShapes(`data/uk-${set}.json`, `data/counties-${set}.json`, set === "historic" ? "uk" : "ukc",
    "uk/", new Set(), lakes, 0.25);

  // ----- Canada's provinces and territories: plain GeoJSON with the border and coast lines made by tools/build_ca.py.
  // The US and Greenland are grey areas around them (ids "T-..."). `lakes` = the world map's lakes (Great Lakes etc.).
  const CA_RINGS = new Set(["PE"]); // Prince Edward Island is a sliver at full-Canada zoom
  GG.loadCA = lakes => loadShapes("data/ca-provinces.json", "data/provinces.json", "ca", "ca/", CA_RINGS, lakes);
  // India's 28 states and 8 union territories (tools/build_in.py); the small ones get circles
  const IN_RINGS = new Set(["IN-CH", "IN-DL", "IN-GA", "IN-PY", "IN-DH", "IN-LD"]);
  GG.loadIN = lakes => loadShapes("data/in-states.json", "data/in-parts.json", "in", "in/", IN_RINGS, lakes);
  // China's 33 provincial-level divisions (tools/build_cn.py); Hong Kong and Macau are specks, so they get circles
  const CN_RINGS = new Set(["CN-HK", "CN-MO"]);
  GG.loadCN = lakes => loadShapes("data/cn-provinces.json", "data/cn-parts.json", "cn", "cn/", CN_RINGS, lakes);
  // Russia's 83 federal subjects (tools/build_ru.py; longitudes past 180° in the far east); the two federal cities and the
  // smallest North Caucasus republics get circles
  const RU_RINGS = new Set(["RU-MOW", "RU-SPE", "RU-IN", "RU-SE", "RU-AD", "RU-KB", "RU-KC", "RU-CE"]);
  // Australia's 6 states, 2 mainland territories and Jervis Bay (tools/build_au.py); the ACT and Jervis Bay get circles
  const AU_RINGS = new Set(["AU-ACT", "AU-JBT"]);
  GG.loadAU = lakes => loadShapes("data/au-states.json", "data/au-parts.json", "au", "au/", AU_RINGS, lakes);
  // Mexico's 31 states and Mexico City (tools/build_mx.py), with a detail level; the small central ones get circles
  const MX_RINGS = new Set(["MX-CMX", "MX-TLA", "MX-MOR", "MX-AGU", "MX-COL"]);
  GG.loadMX = lakes => loadShapes("data/mx-states.json", "data/mx-parts.json", "mx", "mx/", MX_RINGS, lakes);
  // Airport codes (Misc_games.md, idea_01): the airports chosen for a game (a random pick from a pot: js/app.js) on the
  // world map. Each airport is a part with no shape, drawn as a dot (c.dot) and tapped like a small country's circle;
  // the countries are a grey background. Airports sharing a city code (LON, NYC) are a cluster: a numbered bubble
  // while their dots overlap, splitting as you zoom in. name = the code; capitals = the city and its other names.
  let airportData = null;
  GG.airportData = async () => (airportData = airportData || await getJSON("data/airport-sets.json"));
  GG.loadAirports = async (world, codes, place = null) => {
    const A = await GG.airportData(), byIso = {};
    const items = codes.map(code => {
      const a = A.airports[code], ll = place ? place(code) : a.l; // (place: where it's drawn, e.g. moved into an inset)
      const c = { iso: "AP-" + code, id: "AP-" + code, code, name: code, names: [code].concat(a.y ? [a.y] : []),
        capitals: [a.c].concat(a.a || []), cont: a.k, car: false, capLL: [], anchor: ll, bounds: [ll, ll], sizeDeg: 0, ring: true, dot: true,
        minPx: DEFAULT_MIN_PX, flagKey: a.i || "",
        info: { kind: "Airport", full: a.n, city: a.c, ciso: a.i, flag: false },
        feature: { type: "Feature", geometry: { type: "Point", coordinates: ll } } };
      byIso[c.iso] = c;
      return c;
    });
    const groups = {};
    items.forEach(c => { const cc = A.airports[c.code].y; if (cc) (groups[cc] = groups[cc] || []).push(c); });
    const ctx = fs => fs.map(f => ({ ...f, c: null })); // the countries, as background (no part of the game)
    return { kind: "ap", countries: items, byIso, f50: ctx(world.f50), f110: ctx(world.f110), borders50: world.borders50,
      borders110: world.borders110, coast50: world.coast50, coast110: world.coast110, lakes: world.lakes, lakes110: world.lakes110,
      clusters: Object.entries(groups).filter(([, m]) => m.length > 1).map(([name, members]) => ({ name, members })), ringPx: DEFAULT_MIN_PX };
  };
  // Argentina's 23 provinces and the City of Buenos Aires (tools/build_ar.py), with a detail level; the city gets a circle
  GG.loadAR = lakes => loadShapes("data/ar-states.json", "data/ar-parts.json", "ar", "ar/", new Set(["AR-C"]), lakes);
  // Nigeria's 36 states and the FCT (tools/build_ng.py), with a detail level; Lagos (the smallest) gets a circle
  GG.loadNG = lakes => loadShapes("data/ng-states.json", "data/ng-parts.json", "ng", "ng/", new Set(["NG-LA"]), lakes);
  // Spain's two sets (tools/build_es.py): the 17 communities and 2 cities, and the 50 provinces and 2 cities; Ceuta and
  // Melilla get circles; the Canaries are in an inset (their coordinates moved: see tools/build_es.py, SHIFT)
  GG.loadES = lakes => loadShapes("data/es-states.json", "data/es-parts.json", "es", "es/", new Set(["ES-CE", "ES-ML"]), lakes);
  GG.loadESP = lakes => loadShapes("data/esp-states.json", "data/esp-parts.json", "esp", "esp/", new Set(["ESP-CE", "ESP-ML"]), lakes);
  // Italy's 20 regions (tools/build_it.py), with a detail level; Vatican City and San Marino as coloured circles
  const IT_RINGS = new Set(["IT-VA", "IT-SM"]);
  GG.loadIT = lakes => loadShapes("data/it-states.json", "data/it-parts.json", "it", "it/", IT_RINGS, lakes);
  // France's 13 metropolitan regions (tools/build_fr.py), with a detail level; no circles needed
  GG.loadFR = lakes => loadShapes("data/fr-states.json", "data/fr-parts.json", "fr", "fr/", new Set(), lakes);
  // Japan's 47 prefectures (tools/build_jp.py), with a detail level; the smallest (Osaka, Kagawa, Tokyo) get circles
  const JP_RINGS = new Set(["JP-27", "JP-37", "JP-13"]);
  GG.loadJP = lakes => loadShapes("data/jp-states.json", "data/jp-parts.json", "jp", "jp/", JP_RINGS, lakes);
  // The country maps built by tools/build_country.py (jobs/overnight_v2.md): one loader. Rings: the capital cities that
  // sit inside a bigger part (Vienna, Prague, Brussels). `flagDir`: the flags' folder, if not the code (Belgium's regions).
  const C_RINGS = { at: ["AT-9"], cz: ["CZ-PR"], be: ["BE-BRU"], ber: ["BER-BRU"], ch: ["CH-BS", "CH-AI", "CH-ZG"], co: ["CO-DC"] };
  GG.loadCountry = (code, lakes, flagDir) => loadShapes(`data/${code}-states.json`, `data/${code}-parts.json`, code,
    (flagDir || code) + "/", new Set(C_RINGS[code] || []), lakes);
  // Germany's 16 states (tools/build_de.py), with a detail level; Berlin and Bremen get circles
  const DE_RINGS = new Set(["DE-BE", "DE-HB"]);
  GG.loadDE = lakes => loadShapes("data/de-states.json", "data/de-parts.json", "de", "de/", DE_RINGS, lakes);
  // Brazil's 26 states and the Federal District (tools/build_br.py), with a detail level; the Federal District gets a circle
  const BR_RINGS = new Set(["BR-DF"]);
  GG.loadBR = lakes => loadShapes("data/br-states.json", "data/br-parts.json", "br", "br/", BR_RINGS, lakes);
  // Russia's expansion timeline (tools/build_ru.py history): approximate pieces with the years Russia held them
  GG.loadRUHistory = () => getJSON("data/ru-history.json");
  // "held" (Russia's that year), "lost" (held earlier), "annexed" (annexed since, not recognised), or null
  GG.heldIn = (f, y) => {
    const pr = f.properties;
    if (pr.annexed && y >= pr.annexed) return "annexed";
    if (pr.held.some(([a, b]) => a <= y && (b === null || y < b))) return "held";
    return pr.held.some(([a]) => a <= y) ? "lost" : null;
  };
  // (the North Caucasus republics have their own circles; no numbered bubble, removed 2026-11-17)
  GG.loadRU = lakes => loadShapes("data/ru-regions.json", "data/ru-parts.json", "ru", "ru/", RU_RINGS, lakes);

  // Fewer points in lines and outlines (Douglas–Peucker, tolerance in degrees), for things redrawn every frame
  GG.simplify = function (g, tol) {
    const line = pts => {
      if (pts.length < 3) return pts;
      const keep = new Uint8Array(pts.length); keep[0] = keep[pts.length - 1] = 1;
      const stack = [[0, pts.length - 1]];
      while (stack.length) {
        const [a, b] = stack.pop(), [ax, ay] = pts[a], [bx, by] = pts[b], dx = bx - ax, dy = by - ay, L = dx * dx + dy * dy;
        let best = -1, bd = tol * tol;
        for (let i = a + 1; i < b; i++) {
          const [px, py] = pts[i];
          const u = L ? Math.max(0, Math.min(1, ((px - ax) * dx + (py - ay) * dy) / L)) : 0;
          const ex = ax + u * dx - px, ey = ay + u * dy - py, d = ex * ex + ey * ey;
          if (d > bd) { bd = d; best = i; }
        }
        if (best > 0) { keep[best] = 1; stack.push([a, best], [best, b]); }
      }
      return pts.filter((_, i) => keep[i]);
    };
    const ring = r => { const out = line(r); return out.length >= 4 ? out : null; };
    const geom = gm => {
      const t = gm.type, c = gm.coordinates;
      if (t === "LineString") return { type: t, coordinates: line(c) };
      if (t === "MultiLineString") return { type: t, coordinates: c.map(line) };
      if (t === "Polygon") return { type: t, coordinates: c.map(ring).filter(Boolean) };
      if (t === "MultiPolygon") return { type: t, coordinates: c.map(p => p.map(ring).filter(Boolean)).filter(p => p.length) };
      return gm;
    };
    if (g.type === "FeatureCollection") return { type: g.type, features: g.features.map(f => ({ ...f, geometry: geom(f.geometry) })) };
    if (g.type === "Feature") return { ...g, geometry: geom(g.geometry) };
    return geom(g);
  };

  // d3 wants clockwise outer rings: a polygon wound the other way reads as the whole world except that area.
  // Each part that d3 sees as bigger than half the globe is turned round.
  GG.fixWinding = function (fc) {
    fc.features.forEach(f => {
      const g = f.geometry; if (!g) return;
      const polys = g.type === "Polygon" ? [g.coordinates] : g.type === "MultiPolygon" ? g.coordinates : [];
      polys.forEach(p => { if (d3.geoArea({ type: "Polygon", coordinates: p }) > 2 * Math.PI) p.forEach(r => r.reverse()); });
    });
    return fc;
  };

  GG.loadGeo = async function () {
    const [t50, t110, countries, lakes] = await Promise.all([
      getJSON("data/world-50m.json"), getJSON("data/world-110m.json"), getJSON("data/countries.json"),
      getJSON("data/lakes.json").catch(() => null)]); // the big lakes (optional: the map works without them)
    if (lakes) GG.fixWinding(lakes);
    const byId = {}, byIso = {};
    countries.forEach(c => { byId[c.id] = c; byIso[c.iso] = c; });
    await pause();
    const f110 = await featuresOf(t110, byId);
    await pause();
    const f50 = await featuresOf(t50, byId);
    await pause();
    // border and coastline lines are prepared in advance by tools/build_data.py
    const borders50 = topojson.feature(t50, t50.objects.borders), borders110 = topojson.feature(t110, t110.objects.borders);
    const coast50 = topojson.feature(t50, t50.objects.coast), coast110 = topojson.feature(t110, t110.objects.coast);
    await pause();

    // per-feature culling data for the globe: centroid and angular radius
    for (const fs of [f110, f50]) for (const [n, f] of fs.entries()) {
      if (n % 25 === 24) await pause();
      f.centroid = d3.geoCentroid(f);
      const b = d3.geoBounds(f);
      f.radius = Math.max(...[[b[0][0], b[0][1]], [b[1][0], b[1][1]], [b[0][0], b[1][1]], [b[1][0], b[0][1]]]
        .map(p => d3.geoDistance(p, f.centroid)));
      if (b[0][0] > b[1][0]) f.radius = Math.PI; // crosses the date line: never cull
    }
    await pause();

    for (const [n, f] of f50.entries()) {
      if (n % 12 === 11) await pause();
      const c = f.c; if (!c) continue;
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
    }
    f110.forEach(f => { if (f.c) f.c.feature110 = f; });

    const tuv = byIso.TUV;
    tuv.shape = islandShape(tuv, TUVALU.map(p => [p]));
    tuv.anchor = tuv.shape.center; tuv.sizeDeg = 0; tuv.bounds = d3.geoBounds({ type: "MultiPoint", coordinates: TUVALU });

    countries.forEach(c => {
      c.minPx = MIN_PX[c.iso] || DEFAULT_MIN_PX;
      c.ring = RINGS.has(c.iso);
      c.ringAdaptive = ADAPTIVE_RINGS.has(c.iso);
    });
    return {
      countries, byIso, f50, f110, borders50, borders110, coast50, coast110, lakes,
      lakes110: lakes && GG.simplify(lakes, 0.08), // lighter lakes while the globe spins
      clusters: CLUSTERS.map(cl => ({ name: cl.name, members: cl.members.map(i => byIso[i]) })),
      ringPx: DEFAULT_MIN_PX,
    };
  };
})();
