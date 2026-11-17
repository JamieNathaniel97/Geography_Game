// One map on a <canvas>: either a spinnable 3D globe or a flat world map, with pinch zoom,
// tap detection, and the tiny-country overlays (island ovals, rings, the Lesser Antilles bubble).
// Rectangular flat maps wrap around east-west, so there is no edge to get stuck at (Oceania).
(function () {
  const GG = (window.GG = window.GG || {});
  const RAD = Math.PI / 180, DEG = 180 / Math.PI;
  const MAX_K = 800;
  const smoothLine = d3.line().curve(d3.curveCatmullRomClosed);

  // Flat map styles. Rectangular ones wrap around and are cropped to 85N-60S (Antarctica isn't in the quiz).
  GG.FLAT_STYLES = {
    patterson: { name: "Patterson", factory: () => d3.geoPatterson(), raw: d3.geoPattersonRaw, wrap: true },
    miller: { name: "Miller", factory: () => d3.geoMiller(), raw: d3.geoMillerRaw, wrap: true },
    mercator: { name: "Mercator", factory: () => d3.geoMercator(), raw: d3.geoMercatorRaw, wrap: true },
    equirect: { name: "Plain grid", factory: () => d3.geoEquirectangular(), raw: d3.geoEquirectangularRaw, wrap: true },
    natural: { name: "Curved (old)", factory: () => d3.geoNaturalEarth1(), raw: d3.geoNaturalEarth1Raw, wrap: false },
    // the usual US map: Albers projection with Alaska and Hawaii as insets, fitted to the states themselves
    usa: { name: "US states", factory: () => d3.geoAlbersUsa(), wrap: false, fit: true },
    // Canada: Lambert conformal conic, as Statistics Canada draws it (standard parallels 49°N and 77°N)
    canada: { name: "Canada", factory: () => d3.geoConicConformal().parallels([49, 77]).rotate([91.87, 0]), wrap: false, fit: true },
    // Britain and Ireland: transverse Mercator centred on 2°W, like the Ordnance Survey's National Grid
    uk: { name: "Britain and Ireland", factory: () => d3.geoTransverseMercator().rotate([2, 0]), wrap: false, fit: true },
    // India: Lambert conformal conic, standard parallels 12°N and 28°N, centred on 80°E
    india: { name: "India", factory: () => d3.geoConicConformal().parallels([12, 28]).rotate([-80, 0]), wrap: false, fit: true },
    // China: Albers equal-area conic, standard parallels 25°N and 47°N, centred on 105°E
    china: { name: "China", factory: () => d3.geoConicEqualArea().parallels([25, 47]).rotate([-105, 0]), wrap: false, fit: true },
    // Australia: Albers equal-area conic, standard parallels 18°S and 36°S, centred on 132°E
    australia: { name: "Australia", factory: () => d3.geoConicEqualArea().parallels([-18, -36]).rotate([-132, 0]), wrap: false, fit: true },
    // Russia: Albers equal-area conic, standard parallels 52°N and 68°N, centred on 100°E (Kaliningrad to Chukotka)
    russia: { name: "Russia", factory: () => d3.geoConicEqualArea().parallels([52, 68]).rotate([-100, 0]), wrap: false, fit: true },
  };
  const NORTH = 85, SOUTH = -60, CURVED_CENTRE = 10;
  const SEA_REACH = 12;                                            // px: how far out to sea a tap still counts for the nearest country
  const RING_MAX = 36;                                              // px
  // ring diameter: 22 px when the country is a dot, growing to 36 px; the whole ring is the tap area
  const ringSize = px => Math.min(RING_MAX, Math.max(22, px * 1.5 + 18));
  // d3-zoom's own rule for keeping the view inside translateExtent
  function defaultConstrain(t, extent, te) {
    const dx0 = t.invertX(extent[0][0]) - te[0][0], dx1 = t.invertX(extent[1][0]) - te[1][0];
    const dy0 = t.invertY(extent[0][1]) - te[0][1], dy1 = t.invertY(extent[1][1]) - te[1][1];
    return t.translate(dx1 > dx0 ? (dx0 + dx1) / 2 : Math.min(0, dx0) || Math.max(0, dx1),
      dy1 > dy0 ? (dy0 + dy1) / 2 : Math.min(0, dy0) || Math.max(0, dy1));
  }

  const p_scaled = (p, k) => { const out = new Path2D(); out.addPath(p, new DOMMatrix([k, 0, 0, k, 0, 0])); return out; };
  GG.MapView = class MapView {
    // opts: { geo, mode: 'globe'|'flat', flatStyle, getState(c), onTap(c, view), onPoint(view,x,y), isTarget(c), borders }
    constructor(canvas, opts) {
      this.canvas = canvas;
      this.ctx = canvas.getContext("2d");
      this.geo = opts.geo;
      this.opts = opts;
      this.mode = opts.mode || "globe";
      this.styleKey = opts.flatStyle || "patterson";
      this.borders = opts.borders !== false;
      this.moving = false;
      this.t = d3.zoomIdentity;
      this.hits = { islands: [], bubbles: [], rings: [] }; // filled in by each draw
      this.readColours();
      this.crop = null;
      this.zoom = d3.zoom().scaleExtent([1, MAX_K]).clickDistance(8)
        .constrain((t, extent, te) => this.constrain(t, extent, te))
        // only switch to the lighter outlines once the view really moves, so a plain tap
        // (which also starts a zoom gesture) never drops the detail
        .on("start", () => { clearTimeout(this.settle); })
        .on("zoom", e => {
          const a = this.t, b = e.transform;
          if (a.x !== b.x || a.y !== b.y || a.k !== b.k) this.moving = true;
          this.t = b; this.requestDraw();
        })
        .on("end", () => { clearTimeout(this.settle); this.settle = setTimeout(() => { this.moving = false; this.requestDraw(); }, 140); });
      this.sel = d3.select(canvas).call(this.zoom).on("dblclick.zoom", null);
      canvas.addEventListener("click", e => this.handleClick(e));
      // redraw at the right size whenever the canvas changes size (e.g. the jump bar is hidden in region
      // games): otherwise the picture is stretched and taps land in the wrong place
      if (window.ResizeObserver) {
        new ResizeObserver(() => {
          const r = canvas.getBoundingClientRect();
          if (Math.abs(r.width - this.w) > 0.5 || Math.abs(r.height - this.h) > 0.5) { this.resize(); this.requestDraw(); }
        }).observe(canvas);
      }
      this.resize();
    }

    readColours() {
      const cs = getComputedStyle(document.documentElement), v = n => cs.getPropertyValue(n).trim();
      this.col = { bg: v("--bg"), sea: v("--sea"), land: v("--land"), border: v("--border"), coast: v("--coast"),
        terr: v("--terr"), good: v("--good"), bad: v("--bad"), goodSel: v("--good-sel"), badSel: v("--bad-sel"), flash: v("--flash"), marker: v("--marker"),
        panel: v("--panel"), fg: v("--fg"), halo: v("--halo"), off: v("--off"), sel: v("--sel"), capital: v("--capital"), unformed: v("--unformed"), reserve: v("--reserve"), hist: v("--hist") };
    }

    // ----- size and projections -----
    resize() {
      const r = this.canvas.getBoundingClientRect();
      this.w = Math.max(50, r.width); this.h = Math.max(50, r.height);
      this.dpr = Math.min(window.devicePixelRatio || 1, 2.5);
      this.canvas.width = Math.round(this.w * this.dpr); this.canvas.height = Math.round(this.h * this.dpr);
      // the flat map's size depends only on the width, so height-only changes (a phone's address bar
      // sliding in and out) keep the prepared paths and terrain
      if (this.w !== this.builtW) { this.buildFlat(); this.builtW = this.w; }
      this.R0 = Math.min(this.w, this.h) * 0.44;
      this.globe = d3.geoOrthographic().clipAngle(90).precision(0.3);
      this.zoom.extent([[0, 0], [this.w, this.h]]);
      this.applyMode();
    }

    // flat base projection at zoom 1: the whole world is exactly the screen width
    buildFlat() {
      const st = (this.style = GG.FLAT_STYLES[this.styleKey] || GG.FLAT_STYLES.patterson);
      this.wrap = st.wrap;
      this.flatCentre = st.wrap ? 0 : CURVED_CENTRE;
      if (st.wrap) {
        const unit = st.factory().scale(1).translate([0, 0]).precision(0.2);
        const s = this.w / (2 * unit([179.999999, 0])[0]);
        const p = st.factory().scale(s).translate([this.w / 2, 0]).precision(0.2);
        const top = p([0, NORTH])[1], bottom = p([0, SOUTH])[1];
        p.translate([this.w / 2, -top]).clipExtent([[-1, 0], [this.w + 1, bottom - top]]);
        this.flat = p; this.BW = this.w; this.BH = bottom - top;
      } else if (st.fit) {
        // fitted to the map's own shapes (US states): the shapes fill the width with a small margin
        const fc = { type: "FeatureCollection", features: this.geo.f50.filter(f => f.c) }, pad = this.w * 0.03;
        this.flat = st.factory().fitWidth(this.w - 2 * pad, fc);
        const tr = this.flat.translate();
        this.flat.translate([tr[0] + pad, tr[1] + pad]);
        const b = d3.geoPath(this.flat).bounds(fc);
        this.BW = this.w; this.BH = b[1][1] + pad;
      } else {
        this.flat = st.factory().rotate([-CURVED_CENTRE, 0]).fitWidth(this.w, { type: "Sphere" });
        const b = d3.geoPath(this.flat).bounds({ type: "Sphere" });
        this.BW = b[1][0]; this.BH = b[1][1];
      }
      this.flatPaths = null; // rebuilt lazily
      this.flatRelief = null;
      this.tileCache = null;
    }

    // ----- terrain -----
    setTerrain(on) {
      this.terrain = on;
      if (on && !this.relief) {
        GG.loadRelief().then(r => { this.relief = r; this.requestDraw(); }).catch(() => { this.terrain = false; });
      }
      this.requestDraw();
    }
    // the relief re-drawn into the flat map's own shape once, row by row (Patterson is cylindrical:
    // each map row is one latitude, and longitude runs evenly across)
    buildFlatRelief() {
      const r = this.relief, TW = Math.min(4096, Math.round(this.BW * 6)), TH = Math.round(TW * this.BH / this.BW);
      const cv = document.createElement("canvas"); cv.width = TW; cv.height = TH;
      const cx = cv.getContext("2d");
      for (let y = 0; y < TH; y++) {
        const ll = this.flat.invert([this.BW / 2, (y + 0.5) * this.BH / TH]);
        const sy = Math.max(0, Math.min(r.h - 1, Math.floor((90 - ll[1]) / 180 * r.h)));
        cx.drawImage(r.img, 0, sy, r.w, 1, 0, y, TW, 1);
      }
      this.flatRelief = cv;
    }
    // Terrain on one copy of the flat map. Zoomed out it uses the whole-world image; zoomed in it adds
    // sharper 512 px tiles for just the area on screen (loaded as needed). Both are stacked on a
    // screen-sized layer first, then multiplied onto the map once, so the shading never doubles up.
    drawFlatRelief(dx) {
      if (!this.flatRelief) this.buildFlatRelief();
      const ctx = this.ctx, t = this.t, dpr = this.dpr, ox = t.x + dx;
      const toMap = c => c.setTransform(dpr * t.k, 0, 0, dpr * t.k, dpr * ox, dpr * t.y);
      const lvl = this.tileLevel();
      ctx.globalCompositeOperation = "multiply";
      if (!lvl) {
        toMap(ctx); ctx.drawImage(this.flatRelief, 0, 0, this.BW, this.BH);
        ctx.globalCompositeOperation = "source-over";
        return;
      }
      const W = this.canvas.width, H = this.canvas.height;
      if (!this.reliefLayer || this.reliefLayer.width !== W || this.reliefLayer.height !== H) {
        this.reliefLayer = document.createElement("canvas"); this.reliefLayer.width = W; this.reliefLayer.height = H;
      }
      const rc = this.reliefLayer.getContext("2d");
      rc.setTransform(1, 0, 0, 1, 0, 0); rc.fillStyle = "#fff"; rc.fillRect(0, 0, W, H);
      toMap(rc);
      rc.save(); rc.beginPath(); rc.rect(0, 0, this.BW, this.BH); rc.clip();
      rc.drawImage(this.flatRelief, 0, 0, this.BW, this.BH);
      // which tiles are on screen
      const k = t.k, BW = this.BW, BH = this.BH, tileDeg = this.relief.tiles.size * 360 / lvl.w;
      const bx0 = Math.max(0, -ox / k), bx1 = Math.min(BW, (this.w - ox) / k);
      const by0 = Math.max(0, -t.y / k), by1 = Math.min(BH, (this.h - t.y) / k);
      if (bx1 > bx0 && by1 > by0) {
        const lon0 = bx0 / BW * 360 - 180, lon1 = bx1 / BW * 360 - 180;
        const latT = this.flat.invert([BW / 2, by0])[1], latB = this.flat.invert([BW / 2, by1])[1];
        const nx = lvl.w / this.relief.tiles.size;
        for (let ty = Math.floor((90 - latT) / tileDeg); ty <= Math.floor((90 - latB) / tileDeg); ty++) {
          for (let tx = Math.floor((lon0 + 180) / tileDeg); tx <= Math.min(nx - 1, Math.floor((lon1 + 180) / tileDeg)); tx++) {
            if (!lvl.set.has(tx + "_" + ty)) continue; // all flat or sea: nothing to add
            const tile = this.getTile(lvl, tx, ty, tileDeg);
            if (!tile) continue;
            rc.drawImage(tile.cv, tx * tileDeg / 360 * BW, tile.yT, tileDeg / 360 * BW, tile.yB - tile.yT);
          }
        }
      }
      rc.restore();
      ctx.setTransform(1, 0, 0, 1, 0, 0);
      ctx.drawImage(this.reliefLayer, 0, 0);
      ctx.globalCompositeOperation = "source-over";
    }
    // sharpest tile level needed at this zoom, or null when the whole-world image is sharp enough
    tileLevel() {
      const tiles = this.relief.tiles;
      if (!tiles) return null;
      const need = this.BW * this.t.k * this.dpr; // screen pixels across the whole world
      if (need <= this.flatRelief.width * 1.3) return null;
      return tiles.levels.find(l => l.w >= need * 0.8) || tiles.levels[tiles.levels.length - 1];
    }
    // a tile, re-drawn into the flat map's row spacing; null while it's still loading
    getTile(lvl, tx, ty, tileDeg) {
      const cache = (this.tileCache = this.tileCache || new Map()), key = lvl.w + "/" + tx + "_" + ty;
      let e = cache.get(key);
      if (e) { cache.delete(key); cache.set(key, e); return e.cv ? e : null; } // keep recently used at the end
      e = {}; cache.set(key, e);
      while (cache.size > 64) cache.delete(cache.keys().next().value);
      const img = new Image();
      img.onload = () => {
        const S = this.relief.tiles.size, latT = 90 - ty * tileDeg, latB = latT - tileDeg;
        const yT = this.flat([0, latT])[1], yB = this.flat([0, latB])[1];
        const Hpx = Math.max(1, Math.round(S * (yB - yT) / (tileDeg / 360 * this.BW)));
        const cv = document.createElement("canvas"); cv.width = S; cv.height = Hpx;
        const cx = cv.getContext("2d");
        for (let r = 0; r < Hpx; r++) {
          const lat = this.flat.invert([this.BW / 2, yT + (r + 0.5) / Hpx * (yB - yT)])[1];
          const sr = Math.max(0, Math.min(S - 1, Math.floor((latT - lat) / tileDeg * S)));
          cx.drawImage(img, 0, sr, S, 1, 0, r, S, 1);
        }
        e.cv = cv; e.yT = yT; e.yB = yB; // in this map size's coordinates (the cache is cleared on resize)
        this.requestDraw();
      };
      img.onerror = () => cache.delete(key);
      img.src = "data/relief/" + lvl.w + "/" + tx + "_" + ty + ".jpg";
      return null;
    }

    // Terrain for the US map (Albers, with the Alaska and Hawaii insets moved in), so it can't be drawn row by
    // row like the world map. Built once per map size: each pixel is turned back into lon/lat and read from the
    // sharpest relief tiles, then trimmed to the states' outlines. Done in slices so the app stays responsive.
    // The US map is fitted to its width, so a size change just scales it: one layer is stretched to fit, and
    // only rebuilt when the screen needs a much sharper one.
    drawUSRelief() {
      const want = Math.min(3072, Math.round(this.BW * this.dpr * 2.5)), u = this.usRelief;
      if (!u || u.geo !== this.geo || u.cv.width < want * 0.6) this.buildUSRelief(want);
      if (!u || u.geo !== this.geo) return;
      this.ctx.globalCompositeOperation = "multiply";
      this.ctx.drawImage(u.cv, 0, 0, this.BW, this.BH);
      this.ctx.globalCompositeOperation = "source-over";
    }
    async buildUSRelief(TW) {
      if (this.usReliefBusy) return;
      this.usReliefBusy = true;
      try { await this.makeUSRelief(TW); } finally { this.usReliefBusy = false; }
    }
    async makeUSRelief(TW) {
      const geo = this.geo;
      const flat = this.flat, BW = this.BW, BH = this.BH, r = this.relief;
      const TH = Math.round(TW * BH / BW), sc = BW / TW;
      const pause = () => new Promise(res => setTimeout(res, 0));
      const back = (x, y) => { // lon/lat under a map point, or null off the map (checked by projecting it again)
        const ll = flat.invert([x, y]);
        if (!ll || !isFinite(ll[0])) return null;
        const q = flat(ll);
        return q && Math.abs(q[0] - x) + Math.abs(q[1] - y) < 0.5 ? ll : null;
      };
      // lon/lat on a coarse grid; pixels in between are blended from its corners (the projection is smooth),
      // except in cells where a corner is off the map, which are worked out pixel by pixel
      const G = 8, gw = Math.ceil(TW / G) + 1, gh = Math.ceil(TH / G) + 1, grid = new Array(gw * gh);
      for (let j = 0; j < gh; j++) {
        if (j % 24 === 0) { await pause(); if (this.geo !== geo) return; }
        for (let i = 0; i < gw; i++) grid[j * gw + i] = back(i * G * sc, j * G * sc);
      }
      // the relief source: the sharpest tile level if there is one, else the whole-world image
      const tl = r.tiles && r.tiles.levels[r.tiles.levels.length - 1];
      let sample;
      if (tl) {
        const S = r.tiles.size, deg = S * 360 / tl.w, need = new Set(), tiles = (this.usTiles = this.usTiles || new Map());
        grid.forEach(ll => { if (ll) need.add(Math.floor((ll[0] + 180) / deg) + "_" + Math.floor((90 - ll[1]) / deg)); });
        await Promise.all([...need].filter(n => tl.set.has(n) && !tiles.has(n)).map(n => new Promise(res => {
          const img = new Image();
          img.onload = () => {
            const cv = document.createElement("canvas"); cv.width = cv.height = S;
            const cx = cv.getContext("2d"); cx.drawImage(img, 0, 0);
            const d = cx.getImageData(0, 0, S, S).data, g = new Uint8Array(S * S);
            for (let i = 0; i < g.length; i++) g[i] = d[i * 4];
            tiles.set(n, g); res();
          };
          img.onerror = res;
          img.src = "data/relief/" + tl.w + "/" + n + ".jpg";
        })));
        sample = (lon, lat) => {
          const fx = (lon + 180) / deg, fy = (90 - lat) / deg, tx = Math.floor(fx), ty = Math.floor(fy);
          const g = tiles.get(tx + "_" + ty);
          if (!g) return 255;
          const u = Math.max(0, Math.min(S - 1.001, (fx - tx) * S - 0.5)), v = Math.max(0, Math.min(S - 1.001, (fy - ty) * S - 0.5));
          const u0 = u | 0, v0 = v | 0, du = u - u0, dv = v - v0, a = v0 * S + u0, b = a + S;
          const top = g[a] + (g[a + 1] - g[a]) * du, bot = g[b] + (g[b + 1] - g[b]) * du;
          return top + (bot - top) * dv;
        };
      } else {
        const lev = r.levels[0], g = lev.grey, rw = lev.w, rh = lev.h;
        sample = (lon, lat) => g[Math.min(rh - 1, Math.floor((90 - lat) / 180 * rh)) * rw + Math.min(rw - 1, Math.floor((lon + 180) / 360 * rw))];
      }
      const cv = document.createElement("canvas"); cv.width = TW; cv.height = TH;
      const cx = cv.getContext("2d"), img = cx.createImageData(TW, TH), d = img.data;
      for (let y = 0; y < TH; y++) {
        if (y % 48 === 0) { await pause(); if (this.geo !== geo) return; }
        const j = Math.floor(y / G), fy = y / G - j;
        for (let x = 0, i = y * TW * 4; x < TW; x++, i += 4) {
          const k = Math.floor(x / G), fx = x / G - k;
          const p00 = grid[j * gw + k], p10 = grid[j * gw + k + 1], p01 = grid[(j + 1) * gw + k], p11 = grid[(j + 1) * gw + k + 1];
          let lon, lat;
          if (p00 && p10 && p01 && p11 && Math.abs(p00[0] - p11[0]) < 5) {
            lon = (p00[0] * (1 - fx) + p10[0] * fx) * (1 - fy) + (p01[0] * (1 - fx) + p11[0] * fx) * fy;
            lat = (p00[1] * (1 - fx) + p10[1] * fx) * (1 - fy) + (p01[1] * (1 - fx) + p11[1] * fx) * fy;
          } else {
            const ll = back((x + 0.5) * sc, (y + 0.5) * sc);
            if (!ll) { d[i + 3] = 0; continue; }
            lon = ll[0]; lat = ll[1];
          }
          d[i] = d[i + 1] = d[i + 2] = sample(lon, lat); d[i + 3] = 255;
        }
      }
      cx.putImageData(img, 0, 0);
      // keep the shading on the states only (not on Canada or Mexico, which are drawn as sea here)
      cx.globalCompositeOperation = "destination-in";
      cx.setTransform(1 / sc, 0, 0, 1 / sc, 0, 0);
      cx.beginPath(); d3.geoPath(flat, cx)({ type: "FeatureCollection", features: this.geo.f50 }); cx.fill();
      if (this.geo !== geo) return;
      this.usRelief = { geo, cv };
      this.requestDraw();
    }

    // the relief on the globe: each screen pixel is turned back into lon/lat (inverse orthographic)
    // and looked up in the relief. `step` > 1 works at lower resolution while the globe is moving.
    globeRelief(step) {
      const r = this.relief, g = this.globeState(), R = g.scale;
      const cw = Math.ceil(this.w / step), ch = Math.ceil(this.h / step);
      if (!this.reliefCv || this.reliefCv.width !== cw || this.reliefCv.height !== ch) {
        this.reliefCv = document.createElement("canvas"); this.reliefCv.width = cw; this.reliefCv.height = ch;
        this.reliefImg = this.reliefCv.getContext("2d").createImageData(cw, ch);
      }
      // pick the mip level whose detail matches how far apart the samples are, so fine ridges
      // don't flicker as the globe turns; then blend the 4 nearest texels (bilinear)
      const samplesPerDeg = R * RAD / step;
      let L = Math.ceil(Math.log2((r.w / 360) / samplesPerDeg));
      L = Math.max(0, Math.min(r.levels.length - 1, L));
      const lev = r.levels[L], grey = lev.grey, rw = lev.w, rh = lev.h;
      const d = this.reliefImg.data;
      const lon0 = -g.rotate[0], phi0 = -g.rotate[1] * RAD, sp = Math.sin(phi0), cp = Math.cos(phi0);
      const cxs = this.w / 2, cys = this.h / 2;
      for (let j = 0, i = 0; j < ch; j++) {
        const y = (cys - (j + 0.5) * step) / R;
        for (let k = 0; k < cw; k++, i += 4) {
          const x = ((k + 0.5) * step - cxs) / R, rho2 = x * x + y * y;
          let v = 255;
          if (rho2 < 1) {
            const cc = Math.sqrt(1 - rho2);
            const lat = Math.asin(cc * sp + y * cp) * DEG;
            let lon = lon0 + Math.atan2(x, cc * cp - y * sp) * DEG;
            lon = ((lon + 180) % 360 + 360) % 360;
            const fu = lon / 360 * rw - 0.5, fv = Math.max(0, Math.min(rh - 1.001, (90 - lat) / 180 * rh - 0.5));
            const u0 = Math.floor(fu), v0 = fv | 0, du = fu - u0, dv = fv - v0;
            const ua = (u0 + rw) % rw, ub = (u0 + 1) % rw, ra = v0 * rw, rb = ra + rw;
            const top = grey[ra + ua] + (grey[ra + ub] - grey[ra + ua]) * du;
            const bot = grey[rb + ua] + (grey[rb + ub] - grey[rb + ua]) * du;
            v = top + (bot - top) * dv;
          }
          d[i] = d[i + 1] = d[i + 2] = v; d[i + 3] = 255;
        }
      }
      this.reliefCv.getContext("2d").putImageData(this.reliefImg, 0, 0);
      return this.reliefCv;
    }
    // switch to another set of shapes (world countries or US states) and flat map style
    setGeo(geo, styleKey) {
      this.geo = geo;
      this.styleKey = styleKey;
      this.crop = null; // a region crop belongs to the old map (Europe's box means nothing on the US map); the game sets a new one
      this.buildFlat();
      this.hits = { islands: [], bubbles: [], rings: [] };
      this.applyMode();
      this.requestDraw();
    }
    setFlatStyle(key) {
      if (key === this.styleKey) return;
      const c = this.centre(), ppd = this.pxPerDeg();
      this.styleKey = key;
      this.buildFlat();
      this.applyMode();
      if (this.mode === "flat") this.lookAt(c[0], c[1], Math.min(this.w, this.h) * 0.9 / ppd, false);
      this.requestDraw();
    }

    // ----- cropped region maps -----
    // box: [[west, south], [east, north]] (east may be > 180). The view can't leave the box or zoom out past it,
    // and everything outside it is faded out.
    setCrop(box) {
      if (!box) { this.crop = null; this.applyMode(); this.requestDraw(); return; }
      const [[w, s], [e, n]] = box, ring = [];
      const N = 24;
      for (let i = 0; i <= N; i++) ring.push([w, s + (n - s) * i / N]);
      for (let i = 1; i <= N; i++) ring.push([w + (e - w) * i / N, n]);
      for (let i = 1; i <= N; i++) ring.push([e, n - (n - s) * i / N]);
      for (let i = 1; i < N; i++) ring.push([e - (e - w) * i / N, s]);
      ring.push(ring[0]);
      this.crop = { box, polygon: { type: "Polygon", coordinates: [ring.map(([lo, la]) => [lo > 180 ? lo - 360 : lo, la])] } };
      this.applyMode();
      this.requestDraw();
    }
    cropRect() { // the box on the flat map, in zoom-1 map coordinates (x unwrapped)
      // a fitted country map (conic, transverse Mercator): lines of longitude aren't straight, so use the box's outline
      if (!this.wrap) { const b = d3.geoPath(this.flat).bounds(this.crop.polygon); return [b[0][0], b[0][1], b[1][0], b[1][1]]; }
      const [[w, s], [e, n]] = this.crop.box, x0 = this.flat([w, 0])[0];
      return [x0, this.flat([0, Math.min(n, NORTH)])[1], x0 + (e - w) / 360 * this.BW, this.flat([0, Math.max(s, SOUTH)])[1]];
    }
    constrain(t, extent, te) {
      if (!(this.crop && this.mode === "globe")) return defaultConstrain(t, extent, te);
      // globe: keep the centre of the view inside the box
      const [[w, s], [e, n]] = this.crop.box;
      let lon = -((t.x - this.w / 2) / t.k / this.R0 * DEG), lat = (t.y - this.h / 2) / t.k / this.R0 * DEG;
      const mid = (w + e) / 2;
      while (lon - mid > 180) lon -= 360;
      while (mid - lon > 180) lon += 360;
      lon = Math.max(w, Math.min(e, lon)); lat = Math.max(s, Math.min(n, lat));
      return this.globeTransform(lon, lat, t.k);
    }
    applyMode() {
      if (this.crop) {
        const [[w, s], [e, n]] = this.crop.box;
        if (this.mode === "flat") {
          const [x0, y0, x1, y1] = this.cropRect();
          const minK = Math.min(this.w / (x1 - x0), this.h / (y1 - y0));
          this.zoom.scaleExtent([minK, MAX_K]).translateExtent([[x0, y0], [x1, y1]]);
        } else {
          const span = Math.max((e - w) * Math.cos((s + n) / 2 * RAD), n - s);
          const minK = Math.min(this.w, this.h) / (span * this.R0 * RAD);
          this.zoom.scaleExtent([Math.max(0.9, minK * 0.95), MAX_K]).translateExtent([[-Infinity, -Infinity], [Infinity, Infinity]]);
        }
        return;
      }
      if (this.mode === "flat") {
        const minK = this.wrap ? 1 : Math.min(1, this.h / this.BH);
        const xr = this.wrap ? [-Infinity, Infinity] : [-this.BW * 0.08, this.BW * 1.08];
        this.zoom.scaleExtent([minK, MAX_K]).translateExtent([[xr[0], -this.BH * 0.06], [xr[1], this.BH * 1.06]]);
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
        const t = this.t, tr = this.flat.translate();
        const p = this.style.factory().scale(this.flat.scale() * t.k).translate([tr[0] * t.k + t.x, tr[1] * t.k + t.y]);
        if (!this.wrap && p.rotate && this.flat.rotate) p.rotate(this.flat.rotate());
        return p;
      }
      const g = this.globeState();
      return this.globe.rotate([g.rotate[0], g.rotate[1], 0]).scale(g.scale).translate([this.w / 2, this.h / 2]);
    }
    pxPerDeg() {
      return this.mode === "flat" ? this.t.k * this.flat.scale() * RAD : this.R0 * this.t.k * RAD;
    }
    // base (zoom 1) x of the screen centre, unwrapped
    baseCentreX() { return this.t.invert([this.w / 2, this.h / 2])[0]; }
    centre() {
      if (this.mode === "flat") {
        const p = this.t.invert([this.w / 2, this.h / 2]);
        if (this.wrap) p[0] = mod(p[0], this.BW);
        p[1] = Math.max(0.5, Math.min(this.BH - 0.5, p[1]));
        return this.flat.invert(p) || [0, 0];
      }
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
        const k = Math.max(this.zoom.scaleExtent()[0], Math.min(MAX_K, side / (spanDeg * this.flat.scale() * RAD)));
        const p = this.flat([lon, Math.max(SOUTH + 1, Math.min(NORTH - 1, lat))]);
        if (!p) { this.world(animate); return; } // outside this map (e.g. not part of the US layout)
        let x = p[0];
        if (this.crop && this.wrap) { const [x0, , x1] = this.cropRect(); while (x < x0) x += this.BW; while (x > x1) x -= this.BW; }
        else if (this.wrap) { const cx = this.baseCentreX(); while (x - cx > this.BW / 2) x -= this.BW; while (cx - x > this.BW / 2) x += this.BW; }
        this.setTransform(d3.zoomIdentity.translate(this.w / 2 - k * x, this.h / 2 - k * p[1]).scale(k), animate);
      } else {
        const k = Math.max(0.9, Math.min(MAX_K, side / (spanDeg * this.R0 * RAD)));
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
        const x = this.wrap ? this.baseCentreX() : this.BW / 2;
        // a fitted country map taller than the screen (Britain and Ireland, Canada) zooms out to show all of it
        const k = !this.wrap && this.style.fit ? Math.min(1, this.h / this.BH) : 1;
        this.setTransform(d3.zoomIdentity.translate(this.w / 2 - k * x, (this.h - k * this.BH) / 2).scale(k), animate);
      } else {
        this.setTransform(this.globeTransform(this.centre()[0], 15, 1), animate);
      }
    }
    // switch globe <-> flat, keeping the same place and roughly the same zoom
    setMode(mode) {
      if (mode === this.mode) return;
      const c = this.centre(), ppd = this.pxPerDeg();
      this.mode = mode;
      this.applyMode();
      this.lookAt(c[0], c[1], Math.min(this.w, this.h) * 0.9 / ppd, false);
      this.requestDraw();
    }

    // which copies of a wrapping flat map are on screen: list of screen x offsets
    copies() {
      if (this.mode !== "flat" || !this.wrap) return [0];
      const Wk = this.BW * this.t.k, out = [];
      const i0 = Math.floor((-this.t.x) / Wk) - 1, i1 = Math.floor((this.w - this.t.x) / Wk) + 1;
      for (let i = i0; i <= i1; i++) out.push(i * Wk);
      return out;
    }

    // ----- drawing -----
    requestDraw() {
      if (this.frame) return;
      this.frame = requestAnimationFrame(() => { this.frame = null; this.draw(); });
    }
    active(c) { return !this.opts.isActive || this.opts.isActive(c); }
    fillFor(f) {
      if (!f.c) return this.col.terr;
      if (this.opts.isUnformed && this.opts.isUnformed(f.c)) return this.col.unformed; // statehood timeline: not a state yet
      if (!this.active(f.c)) return this.col.off; // outside the quiz region
      const s = this.opts.getState(f.c);
      return s ? this.col[s] : this.col.land;
    }
    draw() {
      const ctx = this.ctx, dpr = this.dpr;
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      ctx.fillStyle = this.col.bg; ctx.fillRect(0, 0, this.w, this.h);
      if (this.mode === "flat") this.drawFlat(); else this.drawGlobe();
      if (this.crop) this.drawCropMask();
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      this.drawOverlays();
    }
    drawFlat() {
      const ctx = this.ctx, t = this.t, col = this.col;
      if (!this.flatPaths) {
        const path = d3.geoPath(this.flat);
        const sphere = new Path2D();
        if (this.wrap) sphere.rect(0, 0, this.BW, this.BH);
        else if (this.style.fit) sphere.rect(-this.BW, -this.BH, this.BW * 3, this.BH * 3); // sea all round the US
        else sphere.addPath(new Path2D(path({ type: "Sphere" })));
        this.flatPaths = {
          sphere, path,
          features: this.geo.f50.map(f => ({ f, p: new Path2D(path(f) || "") })),
          borders: new Path2D(path(this.geo.borders50) || ""),
          coast: new Path2D(path(this.geo.coast50) || ""),
          // zoomed right out, the 1:50m detail is finer than a pixel and slow to stroke: lighter lines then
          coastLo: this.geo.coast110 ? new Path2D(path(this.geo.coast110) || "") : null,
          bordersLo: this.geo.borders110 ? new Path2D(path(this.geo.borders110) || "") : null,
          lakes: this.geo.lakes ? new Path2D(path(this.geo.lakes) || "") : null,
          nations: this.geo.nationBorders ? new Path2D(path(this.geo.nationBorders) || "") : null,
          disputed: this.geo.disputed ? new Path2D(path(this.geo.disputed) || "") : null,
        };
      }
      const P = this.flatPaths;
      // zoomed in: pieces (one polygon or line each, with its box) so the ones off screen can be skipped
      const cull = t.k >= 2.5;
      if (cull && !P.pieces) {
        const piece = g => { const d = P.path(g); return d ? { p: new Path2D(d), b: P.path.bounds(g) } : null; };
        const linePieces = g => g ? piecesOf(g).map(piece).filter(Boolean) : [];
        P.pieces = {
          features: new Map(P.features.map(({ f }) => [f, piecesOf(f).map(piece).filter(Boolean)])),
          coast: linePieces(this.geo.coast50), borders: linePieces(this.geo.borders50), lakes: linePieces(this.geo.lakes),
        };
      }
      const groups = new Map();
      P.features.forEach(({ f, p }) => { const c = this.fillFor(f); if (!groups.has(c)) groups.set(c, []); groups.get(c).push({ f, p }); });
      const lo = t.k < 1.6 && P.coastLo && this.geo.coast110 !== this.geo.coast50;
      const Wk = this.BW * t.k;
      this.copies().filter(dx => t.x + dx + Wk > 0 && t.x + dx < this.w).forEach(dx => { // only copies on screen
        ctx.setTransform(this.dpr * t.k, 0, 0, this.dpr * t.k, this.dpr * (t.x + dx), this.dpr * t.y);
        // the part of the base map on screen for this copy
        const x0 = (-t.x - dx) / t.k, x1 = (this.w - t.x - dx) / t.k, y0 = -t.y / t.k, y1 = (this.h - t.y) / t.k;
        const on = b => b[1][0] >= x0 && b[0][0] <= x1 && b[1][1] >= y0 && b[0][1] <= y1;
        const visible = list => { const out = new Path2D(); list.forEach(o => { if (on(o.b)) out.addPath(o.p); }); return out; };
        ctx.fillStyle = col.sea; ctx.fill(P.sphere);
        groups.forEach((ps, c) => {
          ctx.fillStyle = c;
          const seams = c === col.unformed; // land not yet a state: stroke in its own colour to hide the seams between areas
          if (seams) { ctx.strokeStyle = c; ctx.lineWidth = 1 / t.k; }
          if (cull) { const v = visible(ps.flatMap(({ f }) => P.pieces.features.get(f))); ctx.fill(v); if (seams) ctx.stroke(v); }
          else ps.forEach(({ p }) => { ctx.fill(p); if (seams) ctx.stroke(p); });
        });
        if (this.terrain && this.relief && (this.wrap || this.style.fit)) {
          if (this.wrap) this.drawFlatRelief(dx); else this.drawUSRelief();
          ctx.setTransform(this.dpr * t.k, 0, 0, this.dpr * t.k, this.dpr * (t.x + dx), this.dpr * t.y);
        }
        ctx.lineJoin = "round";
        if (P.lakes) { const lakes = cull ? visible(P.pieces.lakes) : P.lakes; ctx.fillStyle = col.sea; ctx.fill(lakes); ctx.strokeStyle = col.coast; ctx.lineWidth = 0.5 / t.k; ctx.stroke(lakes); }
        ctx.strokeStyle = col.coast; ctx.lineWidth = 0.6 / t.k; ctx.stroke(cull ? visible(P.pieces.coast) : lo ? P.coastLo : P.coast);
        if (this.borders) {
          ctx.strokeStyle = col.border; ctx.lineWidth = 0.7 / t.k;
          ctx.stroke(this.bordersOverride ? this.overridePath(P) : cull ? visible(P.pieces.borders) : lo ? P.bordersLo : P.borders);
          // the borders between the UK's nations, bolder so England, Scotland and Wales stand out
          if (P.nations) { ctx.strokeStyle = col.fg; ctx.globalAlpha = 0.55; ctx.lineWidth = 2 / t.k; ctx.stroke(P.nations); ctx.globalAlpha = 1; }
        }
        // disputed borders (India's Kashmir and China lines): dotted, shown even with Borders off
        if (P.disputed) {
          ctx.strokeStyle = col.fg; ctx.globalAlpha = 0.7; ctx.lineWidth = 1.4 / t.k; ctx.lineCap = "round";
          ctx.setLineDash([0.1 / t.k, 3.2 / t.k]); ctx.stroke(P.disputed); ctx.setLineDash([]); ctx.lineCap = "butt"; ctx.globalAlpha = 1;
        }
        this.drawSub(ctx, null, t.k);
        this.drawReserves(ctx, null, t.k, cull ? on : null);
        this.drawHistory(ctx, t.k);
      });
    }
    drawGlobe() {
      const ctx = this.ctx, col = this.col, proj = this.projection();
      const path = d3.geoPath(proj, ctx);
      // full detail is too slow to redraw every frame on a phone, so spin with the lighter outlines
      // lighter outlines while spinning, and while the splash screen covers the map (keeps the splash smooth)
      const light = (this.moving && this.t.k < 4) || GG.splashShowing;
      const feats = light ? this.geo.f110 : this.geo.f50;
      const centre = this.centre();
      const R = proj.scale(), half = Math.hypot(this.w, this.h) / 2;
      const view = half >= R ? Math.PI / 2 : Math.asin(half / R);
      ctx.beginPath(); path({ type: "Sphere" }); ctx.fillStyle = col.sea; ctx.fill();
      const groups = new Map();
      // zoomed in (much less than a hemisphere on screen): draw only the pieces in view
      const cull = !light && view < 1.2, inView = o => d3.geoDistance(o.centroid, centre) <= view + o.radius;
      const lines = g => { if (!cull) { path(g); return; } piecesOf(g).forEach(o => { if (inView(o)) path(o); }); };
      feats.forEach(f => {
        if (!inView(f)) return;
        const c = this.fillFor(f); if (!groups.has(c)) groups.set(c, []);
        if (cull) piecesOf(f).forEach(o => { if (inView(o)) groups.get(c).push(o); }); else groups.get(c).push(f);
      });
      groups.forEach((fs, c) => { ctx.beginPath(); fs.forEach(f => path(f)); ctx.fillStyle = c; ctx.fill(); });
      if (this.terrain && this.relief) {
        ctx.globalCompositeOperation = "multiply";
        ctx.imageSmoothingEnabled = true;
        ctx.drawImage(this.globeRelief(this.moving ? 2.5 : 1), 0, 0, this.w, this.h); // 0.4 resolution while spinning
        ctx.globalCompositeOperation = "source-over";
      }
      ctx.lineJoin = "round";
      if (this.geo.lakes) { ctx.beginPath(); lines(light ? this.geo.lakes110 : this.geo.lakes); ctx.fillStyle = col.sea; ctx.fill(); ctx.strokeStyle = col.coast; ctx.lineWidth = 0.5; ctx.stroke(); }
      ctx.beginPath(); lines(light ? this.geo.coast110 : this.geo.coast50); ctx.strokeStyle = col.coast; ctx.lineWidth = 0.6; ctx.stroke();
      if (this.borders) { ctx.beginPath(); lines(light ? this.geo.borders110 : this.geo.borders50); ctx.strokeStyle = col.border; ctx.lineWidth = 0.7; ctx.stroke(); }
      this.drawSub(ctx, path, 1, cull ? lines : null);
      this.drawReserves(ctx, path, 1, null);
      ctx.beginPath(); path({ type: "Sphere" }); ctx.strokeStyle = col.halo; ctx.lineWidth = 1.5; ctx.stroke();
    }

    // A history layer (Russia's timeline): `h` = { fc, year } or null. Each piece is tinted by whether Russia held it in
    // that year (strong), held it earlier but lost it (pale), or annexed it later without recognition (hatched);
    // today's border is outlined to compare with.
    setHistory(h) { this.history = h; this.requestDraw(); }
    drawHistory(ctx, k) {
      const h = this.history; if (!h) return;
      if (!this.histPaths || this.histPaths.flat !== this.flat || this.histPaths.fc !== h.fc) {
        const p = d3.geoPath(this.flat);
        this.histPaths = { flat: this.flat, fc: h.fc, today: new Path2D(p(h.fc.today) || ""),
          pieces: h.fc.features.map(f => ({ f, p: new Path2D(p(f) || "") })) };
      }
      if (!this.hatch) { // diagonal lines, for land annexed without recognition
        const c = document.createElement("canvas"); c.width = c.height = 8;
        const x = c.getContext("2d"); x.strokeStyle = this.col.hist; x.lineWidth = 1.6;
        x.beginPath(); x.moveTo(-2, 10); x.lineTo(10, -2); x.moveTo(-2, 2); x.lineTo(2, -2); x.moveTo(6, 10); x.lineTo(10, 6); x.stroke();
        this.hatch = ctx.createPattern(c, "repeat");
      }
      const y = h.year, col = this.col;
      ctx.save();
      this.histPaths.pieces.forEach(({ f, p }) => {
        const st = GG.heldIn(f, y); if (!st) return;
        ctx.fillStyle = col.hist; ctx.globalAlpha = st === "held" ? 0.55 : 0.16; ctx.fill(p);
        if (st === "annexed") {
          ctx.globalAlpha = 0.8; ctx.save(); ctx.scale(1 / k, 1 / k); // keep the hatching a fixed size on screen
          ctx.fillStyle = this.hatch; ctx.fill(p_scaled(p, k)); ctx.restore();
        }
      });
      ctx.globalAlpha = 0.85; ctx.strokeStyle = col.fg; ctx.lineWidth = 1.3 / k; ctx.setLineDash([5 / k, 3 / k]);
      ctx.stroke(this.histPaths.today); ctx.setLineDash([]);
      ctx.restore();
    }
    // the history piece under a screen point (taps on the timeline), or null
    historyAt(x, y) {
      if (!this.history) return null;
      const ll = this.lonLatAt(x, y); if (!ll) return null;
      return this.history.fc.features.find(f => GG.heldIn(f, this.history.year) && d3.geoContains(f, ll)) || null;
    }

    // Indigenous reserved lands (Learning mode layer): shapes tinted and outlined; the smallest ones are dots,
    // drawn with the overlays so they stay a fixed size. `fc` = GeoJSON FeatureCollection, or null.
    setReserves(fc) {
      this.reserves = fc;
      if (fc && !fc._split) {
        fc._split = {
          shapes: { type: "FeatureCollection", features: fc.features.filter(f => f.geometry.type !== "Point") },
          dots: fc.features.filter(f => f.geometry.type === "Point"),
        };
      }
      this.resPaths = null;
      this.requestDraw();
    }
    drawReserves(ctx, path, k, onBox) {
      if (!this.reserves) return;
      const shapes = this.reserves._split.shapes, col = this.col;
      ctx.save();
      let shape = null;
      const specks = []; // shapes too small to outline at this zoom: screen points, drawn as 1.5 px specks
      if (path) { // globe: a copy simplified to this zoom, only the pieces facing us (full detail was ~250 ms a frame)
        const proj = path.projection(), R = proj.scale(), centre = this.centre(), half = Math.hypot(this.w, this.h) / 2;
        // while the globe moves, a coarser copy (like the lighter coastlines)
        const view = half >= R ? Math.PI / 2 : Math.asin(half / R), lv = this.resLevel(shapes, this.moving ? R / 3 : R);
        ctx.beginPath();
        lv.pieces.forEach(o => { if (d3.geoDistance(o.centroid, centre) <= view + o.radius) path(o); });
        const c = unitVec(centre), cv = Math.cos(Math.min(Math.PI / 2, view + 0.01));
        lv.specks.forEach(o => {
          const v = o._v || (o._v = unitVec(o.centroid));
          if (v[0] * c[0] + v[1] * c[1] + v[2] * c[2] < cv) return; // on the far side or off screen
          const p = proj(o.centroid); if (p) specks.push(p);
        });
      } else {
        if (!this.resPaths || this.resPaths.flat !== this.flat) {
          const p = d3.geoPath(this.flat);
          this.resPaths = { flat: this.flat, lv: new Map() };
        }
        // a lighter copy for this zoom, in base map units so it's built once per level
        const lv = this.resLevel(shapes, this.pxPerDeg() / RAD);
        let lp = this.resPaths.lv.get(lv);
        if (!lp) {
          const p = d3.geoPath(this.flat);
          lp = { all: new Path2D(p({ type: "GeometryCollection", geometries: lv.pieces }) || ""),
            pieces: lv.pieces.map(g => { const d = p(g); return d ? { p: new Path2D(d), b: p.bounds(g) } : null; }).filter(Boolean),
            specks: lv.specks.map(o => this.flat(o.centroid)).filter(Boolean) };
          this.resPaths.lv.set(lv, lp);
        }
        if (onBox) { shape = new Path2D(); lp.pieces.forEach(o => { if (onBox(o.b)) shape.addPath(o.p); }); } // zoomed in: only the pieces on screen
        else shape = lp.all;
        const m = ctx.getTransform(), d = this.dpr;
        lp.specks.forEach(b => specks.push([(m.a * b[0] + m.e) / d, (m.d * b[1] + m.f) / d]));
      }
      ctx.globalAlpha = 0.35; ctx.fillStyle = col.reserve;
      if (path) ctx.fill(); else ctx.fill(shape);
      ctx.globalAlpha = 0.9; ctx.strokeStyle = col.reserve; ctx.lineWidth = 0.8 / k;
      if (path) ctx.stroke(); else ctx.stroke(shape);
      if (specks.length) { // one speck per 1.5 px cell: zoomed out, thousands land on the same few pixels
        ctx.setTransform(this.dpr, 0, 0, this.dpr, 0, 0); ctx.fillStyle = col.reserve; ctx.beginPath();
        const seen = new Set(), W = this.w, H = this.h;
        specks.forEach(([x, y]) => {
          if (x < -2 || y < -2 || x > W + 2 || y > H + 2) return;
          const key = Math.round(x / 1.5) * 65536 + Math.round(y / 1.5);
          if (seen.has(key)) return; seen.add(key);
          ctx.rect(x - 0.75, y - 0.75, 1.5, 1.5);
        });
        ctx.fill();
      }
      ctx.restore();
    }
    // The reserves for a globe of radius R px, cached per zoom level: outlines simplified to about 0.6 px,
    // and shapes under about 1.5 px across kept only as a centre point (a speck).
    resLevel(shapes, R) {
      const L = Math.max(0, Math.ceil(Math.log2(0.6 / R / 2e-5))); // tolerance 2e-5 rad (about 130 m) x 2^L
      const cache = shapes._lv || (shapes._lv = new Map());
      if (cache.has(L)) return cache.get(L);
      const tol = 2e-5 * 2 ** L, tolDeg = tol * 180 / Math.PI, pieces = [], specks = [];
      piecesOf(shapes).forEach(o => {
        if (o.radius - 0.002 < 1.25 * tol) { specks.push(o); return; } // capOf pads the radius by 0.002
        // simplifying can flip which way a ring runs, and on the globe a flipped outline fills the rest of the world:
        // outlines must enclose less than a hemisphere, holes (on their own) more
        const ring = r => ({ type: "Polygon", coordinates: [r] });
        let outer = simplifyRing(o.coordinates[0], tolDeg);
        if (outer.length < 4) { specks.push(o); return; }
        if (d3.geoArea(ring(outer)) > 2 * Math.PI) outer = outer.slice().reverse();
        const holes = o.coordinates.slice(1).map(r => simplifyRing(r, tolDeg)).filter(r => r.length >= 4)
          .map(r => d3.geoArea(ring(r)) < 2 * Math.PI ? r.slice().reverse() : r);
        // last check: tiny triangles with no area (a few in the data) can still read as "the whole world"
        if (d3.geoArea({ type: "Polygon", coordinates: [outer, ...holes] }) > 2 * Math.PI) { specks.push(o); return; }
        pieces.push({ type: "Polygon", coordinates: [outer, ...holes], centroid: o.centroid, radius: o.radius });
      });
      const lv = { pieces, specks };
      cache.set(L, lv);
      return lv;
    }
    drawReserveDots(ctx, proj) {
      if (!this.reserves) return;
      const offsets = this.copies(), W = this.w, H = this.h;
      ctx.fillStyle = this.col.reserve; ctx.strokeStyle = this.col.panel; ctx.lineWidth = 1;
      const r = Math.max(1.5, Math.min(3.5, this.pxPerDeg() / 6));
      const globe = this.mode !== "flat", c = globe ? unitVec(this.centre()) : null, cv = Math.cos(Math.PI / 2 - 0.01);
      const seen = new Set(); // one dot per spot: zoomed out, many overlap exactly
      ctx.beginPath();
      this.reserves._split.dots.forEach(f => {
        const ll = f.geometry.coordinates;
        if (globe) { const v = f._v || (f._v = unitVec(ll)); if (v[0] * c[0] + v[1] * c[1] + v[2] * c[2] < cv) return; }
        const p = proj(ll); if (!p) return;
        offsets.forEach(dx => {
          const x = p[0] + dx;
          if (x < -5 || x > W + 5 || p[1] < -5 || p[1] > H + 5) return;
          const key = Math.round(x / r) * 65536 + Math.round(p[1] / r);
          if (seen.has(key)) return; seen.add(key);
          ctx.moveTo(x + r, p[1]); ctx.arc(x, p[1], r, 0, 2 * Math.PI);
        });
      });
      ctx.fill();
    }
    // the reserved land under a screen point (a shape, or a dot within reach), or null
    reserveAt(x, y) {
      if (!this.reserves) return null;
      const proj = this.projection(), offsets = this.copies();
      let best = null, bd = 10;
      this.reserves._split.dots.forEach(f => {
        const ll = f.geometry.coordinates;
        if (!this.visible(ll)) return;
        const p = proj(ll); if (!p) return;
        offsets.forEach(dx => { const d = Math.hypot(p[0] + dx - x, p[1] - y); if (d < bd) { bd = d; best = f; } });
      });
      if (best) return best;
      const ll = this.lonLatAt(x, y);
      if (!ll) return null;
      return this.reserves._split.shapes.features.find(f => {
        const b = f._b || (f._b = d3.geoBounds(f));
        return ll[0] >= b[0][0] && ll[0] <= b[1][0] && ll[1] >= b[0][1] && ll[1] <= b[1][1] && d3.geoContains(f, ll);
      }) || null;
    }
    // Other borders in place of the usual ones (the statehood timeline: only borders that existed that year)
    setBordersOverride(g) { this.bordersOverride = g; this.requestDraw(); }
    overridePath(P) {
      const cache = P.override || (P.override = new Map());
      let p = cache.get(this.bordersOverride);
      if (!p) { p = new Path2D(P.path(this.bordersOverride) || ""); cache.set(this.bordersOverride, p); }
      return p;
    }
    // Subdivisions (US states on the world Learning map): their borders fade in as you zoom in, and the
    // tapped one is highlighted. `sub` = { features, borders, selected }.
    setSub(sub) { this.sub = sub; this.subPaths = null; this.requestDraw(); }
    subAlpha() {
      if (!this.sub || this.styleKey === "usa") return 0;
      return Math.max(0, Math.min(1, (this.pxPerDeg() - 3) / 2.5)); // from about 3 px per degree; fully shown by 5.5
    }
    drawSub(ctx, path, k, lines) {
      const a = this.subAlpha(), sub = this.sub;
      if (!a) return;
      ctx.save();
      ctx.globalAlpha = a;
      if (path) { // globe: projected each frame
        if (sub.selected) { ctx.beginPath(); path(sub.selected); ctx.fillStyle = this.col.flash; ctx.fill(); }
        ctx.beginPath(); (lines || path)(sub.borders);
      } else { // flat map: paths in base map units, prepared once
        if (!this.subPaths || this.subPaths.flat !== this.flat) {
          const p = d3.geoPath(this.flat);
          this.subPaths = { flat: this.flat, borders: new Path2D(p(sub.borders) || ""), sel: new Map() };
        }
        if (sub.selected) {
          let sp = this.subPaths.sel.get(sub.selected);
          if (!sp) { sp = new Path2D(d3.geoPath(this.flat)(sub.selected) || ""); this.subPaths.sel.set(sub.selected, sp); }
          ctx.fillStyle = this.col.flash; ctx.fill(sp);
        }
      }
      ctx.strokeStyle = this.col.border; ctx.lineWidth = 0.6 / k;
      if (!this.moving) ctx.setLineDash([3 / k, 2 / k]); // dashes are slow to draw: solid while the map moves
      if (path) ctx.stroke(); else ctx.stroke(this.subPaths.borders);
      ctx.restore();
    }
    // the subdivision under a screen point (only while they're shown), or null
    subAt(x, y) {
      if (this.subAlpha() < 0.5) return null;
      const ll = this.lonLatAt(x, y);
      if (!ll) return null;
      return this.sub.features.find(f => d3.geoContains(f, ll)) || null;
    }

    // fade out everything outside the region's box
    drawCropMask() {
      const ctx = this.ctx, dpr = this.dpr;
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      ctx.beginPath();
      if (this.mode === "flat") {
        const [x0, y0, x1, y1] = this.cropRect(), t = this.t;
        ctx.rect(0, 0, this.w, this.h);
        ctx.rect(t.applyX(x0), t.applyY(y0), (x1 - x0) * t.k, (y1 - y0) * t.k);
      } else {
        const path = d3.geoPath(this.projection(), ctx);
        ctx.rect(0, 0, this.w, this.h);
        path(this.crop.polygon);
      }
      ctx.fillStyle = this.col.bg; ctx.globalAlpha = 0.88; ctx.fill("evenodd"); ctx.globalAlpha = 1;
    }

    // island ovals, rings and the cluster bubble, all in screen pixels
    drawOverlays() {
      const ctx = this.ctx, col = this.col, proj = this.projection(), ppd = this.pxPerDeg(), geo = this.geo;
      // pixels per degree when fully zoomed out on the world map (the baseline for growing rings)
      const ppd0 = this.mode === "flat" ? this.flat.scale() * RAD : this.R0 * RAD * 0.9;
      const W = this.w, H = this.h, m = 40;
      const flat = this.mode === "flat", s0 = proj.scale(), tr = proj.translate(), raw = this.style.raw;
      const norm = lon => { const l = lon - (flat ? this.flatCentre : 0); return ((l + 540) % 360) - 180; };
      // on the flat map, project a shape's points without splitting it at the map edge (Kiribati)
      const flatPt = (ll, ref) => {
        let l = norm(ll[0]);
        while (l - ref > 180) l -= 360;
        while (ref - l > 180) l += 360;
        const q = raw(l * RAD, ll[1] * RAD);
        return [tr[0] + s0 * q[0], tr[1] - s0 * q[1]];
      };
      const offsets = this.copies();
      const onScreen = (x, y, r) => x + r > -m && x - r < W + m && y + r > -m && y - r < H + m;
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
      const shift = (s, dx) => dx === 0 ? s : Object.assign({}, s, { x: s.x + dx, pts: s.pts.map(p => [p[0] + dx, p[1]]) });
      const islands = [], rings = [], bubbles = [], hidden = new Set();
      // a small part's circle: its diameter in pixels, or 0 once the part is big enough to tap by itself
      const ringD = c => {
        const px = c.sizeDeg * ppd;
        if (c.ringAdaptive) {
          // 8 px fully zoomed out, growing more slowly than the map (zoom^0.45), up to 90 px;
          // it goes once the country itself is 40 px across and easy to tap
          return px >= 40 ? 0 : Math.min(90, 8 * Math.pow(Math.max(1, ppd / ppd0), 0.45));
        }
        // the ring grows as you zoom in (22 px up to 36 px) and goes once the country is that big
        return px >= RING_MAX ? 0 : ringSize(px);
      };
      // a cluster member as a circle (island oval, or ring: e.g. the North Caucasus republics)
      const memberOf = c => {
        if (c.shape) return shapeOf(c);
        if (!c.ring || !this.visible(c.anchor)) return null;
        const d = ringD(c); if (!d) return null;
        const [x, y] = proj(c.anchor);
        return { c, x, y, r: d / 2, f: 2, ring: true };
      };
      geo.clusters.forEach(cl => {
        if (!cl.members.every(c => this.active(c))) return;
        const ms = cl.members.map(memberOf).filter(Boolean);
        if (ms.length < 2) return;
        let overlap = false;
        for (let i = 0; i < ms.length && !overlap; i++) for (let j = i + 1; j < ms.length; j++) {
          const gap = ms[i].ring && ms[j].ring ? ms[i].r + ms[j].r : (ms[i].r + ms[j].r) / 2; // rings: any overlap
          if ((ms[i].f > 1 || ms[j].f > 1) && Math.hypot(ms[i].x - ms[j].x, ms[i].y - ms[j].y) < gap) { overlap = true; break; }
        }
        if (!overlap) return;
        cl.members.forEach(c => hidden.add(c));
        // the bubble sits at the members' middle, or where the cluster says (e.g. offshore, clear of a big neighbour)
        const at = cl.at && this.visible(cl.at) ? proj(cl.at) : null;
        const bx = at ? at[0] : d3.mean(ms, s => s.x), by = at ? at[1] : d3.mean(ms, s => s.y);
        offsets.forEach(dx => { if (onScreen(bx + dx, by, 13)) bubbles.push({ cl, x: bx + dx, y: by, r: 13 }); });
      });
      geo.countries.forEach(c => {
        if (hidden.has(c) || !this.active(c)) return;
        if (c.shape) {
          const s = shapeOf(c); if (!s) return;
          offsets.forEach(dx => { if (onScreen(s.x + dx, s.y, s.r)) islands.push(shift(s, dx)); });
        } else if (c.ring && this.visible(c.anchor)) {
          const d = ringD(c); if (!d) return;
          const [x, y] = proj(c.anchor);
          offsets.forEach(dx => { if (onScreen(x + dx, y, d)) rings.push({ c, x: x + dx, y, d }); });
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
        ctx.beginPath(); ctx.arc(d.x, d.y, d.d / 2, 0, 2 * Math.PI);
        ctx.lineWidth = st ? 2.5 : 1.5; ctx.strokeStyle = st ? col[st] : col.marker; ctx.stroke();
      });
      bubbles.forEach(b => {
        const sts = b.cl.members.map(c => this.opts.getState(c));
        const allGood = sts.every(s => s === "good");
        const anyBad = b.cl.members.some(c => this.opts.getState(c) === "bad" && this.opts.isTarget && this.opts.isTarget(c));
        ctx.beginPath(); ctx.arc(b.x, b.y, b.r, 0, 2 * Math.PI);
        ctx.globalAlpha = anyBad ? 0.35 : 0.9; ctx.fillStyle = anyBad ? col.bad : col.panel; ctx.fill(); ctx.globalAlpha = 1;
        ctx.setLineDash(allGood || anyBad ? [] : [4, 3]);
        ctx.lineWidth = anyBad ? 3 : allGood ? 2.5 : 1.6; ctx.strokeStyle = anyBad ? col.bad : allGood ? col.good : col.marker; ctx.stroke();
        ctx.setLineDash([]);
        ctx.fillStyle = col.fg; ctx.font = "600 12px Barlow, system-ui, sans-serif"; ctx.textAlign = "center"; ctx.textBaseline = "middle";
        ctx.fillText(String(b.cl.members.length), b.x, b.y);
      });
      // capital dots (capitals games): a small dark green dot, no outline, at each capital of an answered country or state
      this.drawReserveDots(ctx, proj);
      if (this.opts.showCapital) {
        ctx.fillStyle = col.capital;
        geo.countries.forEach(c => {
          if (!c.capLL || !this.opts.showCapital(c)) return;
          c.capLL.forEach(ll => {
            if (!this.visible(ll)) return;
            const p = proj(ll); if (!p) return;
            offsets.forEach(dx => {
              if (!onScreen(p[0] + dx, p[1], 6)) return;
              ctx.beginPath(); ctx.arc(p[0] + dx, p[1], 3, 0, 2 * Math.PI); ctx.fill();
            });
          });
        });
      }
      this.hits = { islands: islands.slice().reverse(), bubbles, rings };
    }

    // ----- tapping -----
    handleClick(e) {
      const r = this.canvas.getBoundingClientRect();
      const x = e.clientX - r.left, y = e.clientY - r.top;
      if (this.opts.onPoint && this.opts.onPoint(this, x, y)) return; // e.g. the magnifier
      // a bubble opens its cluster, unless the tap is on an open small part's circle (e.g. Adygea next to the North Caucasus bubble)
      const open = this.opts.isOpen || (() => true);
      const b = this.hits.bubbles.find(b => Math.hypot(b.x - x, b.y - y) <= b.r + 4);
      const onRing = this.hits.rings.some(r => open(r.c) && Math.hypot(r.x - x, r.y - y) <= r.d / 2 + 3);
      if (b && !onRing) { this.zoomToCountries(b.cl.members); return; }
      const c = this.resolveTap(x, y);
      this.lastTap = [x, y];
      if (c) this.opts.onTap(c, this);
    }
    // Which country a tap means. The rules, in order:
    //  1. Land comes first: a tap on a country that's still open counts as that country. The one exception is
    //     the inner part of a small country's circle (e.g. San Marino inside Italy), which counts as the small country.
    //  2. Otherwise (sea, or a country already answered or greyed out): a circle or island oval under the
    //     finger counts as its country; where they overlap, the one whose centre is nearest wins.
    //  3. Otherwise: snap to the nearest open small country or oval close to the tap.
    resolveTap(x, y) {
      const open = this.opts.isOpen || (() => true);
      const near = (a, b) => Math.hypot(a.x - x, a.y - y) - Math.hypot(b.x - x, b.y - y);
      const rings = this.hits.rings.filter(r => open(r.c) && Math.hypot(r.x - x, r.y - y) <= r.d / 2 + 3).sort(near);
      const ovals = this.hits.islands.filter(s => open(s.c) && d3.polygonContains(s.pts, [x, y])).sort(near);
      const land = this.landAt(x, y);
      if (land && open(land)) {
        const inner = rings.find(r => Math.hypot(r.x - x, r.y - y) <= r.d * 0.3);
        return inner && inner.c !== land ? inner.c : land;
      }
      // circles and ovals under the finger: the one whose centre is nearest wins
      const under = rings.concat(ovals).sort(near)[0];
      if (under) return under.c;
      // snap (sea taps): the country whose coastline is nearest wins, as long as it's still open and the tap
      // is within SEA_REACH px of that coast. Answered or greyed-out countries count when finding the nearest,
      // so a tap just off Vietnam never jumps across to Cambodia.
      if (land) return land; // answered land: nothing new to pick
      const ll = this.lonLatAt(x, y), ppd = this.pxPerDeg();
      let best = null, bd = SEA_REACH;
      this.hits.islands.forEach(s => {
        const gap = edgeDistance(s.pts, x, y);
        if (gap < bd) { bd = gap; best = s.c; }
      });
      if (ll) {
        // every shape on the map counts, including grey non-quiz land (Greenland, territories): a tap on or
        // nearest to those picks nothing
        const m = (SEA_REACH + 4) / ppd;
        for (const f of this.geo.f50) {
          if (f.c && f.c.shape) continue; // island ovals are handled above
          const b = f.bounds || (f.bounds = d3.geoBounds(f));
          if (!inBounds([[b[0][0] - m, b[0][1] - m], [b[1][0] + m, b[1][1] + m]], ll)) continue;
          if (!f.c && d3.geoContains(f, ll)) return null;
          const gap = this.coastGap(f, x, y, bd);
          if (gap < bd) { bd = gap; best = f.c; }
        }
      }
      return best && open(best) ? best : null;
    }
    // screen distance from a point to a shape's outline (segments further than `limit` away are skipped)
    coastGap(f, x, y, limit) {
      const proj = this.projection(), offsets = this.copies();
      const g = f.geometry, polys = g.type === "Polygon" ? [g.coordinates] : g.coordinates;
      let best = Infinity;
      for (const poly of polys) for (const ring of poly) {
        let prev = null;
        for (const ll of ring) {
          const p = this.visible(ll) ? proj(ll) : null;
          if (p && prev) {
            for (const dx of offsets) {
              const ax = prev[0] + dx, ay = prev[1], bx = p[0] + dx, by = p[1];
              if (Math.min(ax, bx) > x + limit || Math.max(ax, bx) < x - limit || Math.min(ay, by) > y + limit || Math.max(ay, by) < y - limit) continue;
              const ex = bx - ax, ey = by - ay, L = ex * ex + ey * ey;
              const u = L ? Math.max(0, Math.min(1, ((x - ax) * ex + (y - ay) * ey) / L)) : 0;
              best = Math.min(best, Math.hypot(ax + u * ex - x, ay + u * ey - y));
            }
          }
          prev = p;
        }
      }
      return best;
    }
    // the country whose land is under the point (true borders only, no circles or ovals)
    landAt(x, y) {
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
        const p = this.t.invert([x, y]);
        if (this.wrap) {
          p[0] = mod(p[0], this.BW);
          if (p[1] < 0 || p[1] > this.BH) return null;
          const ll = this.flat.invert(p);
          return ll && isFinite(ll[0]) ? ll : null;
        }
        const ll = this.flat.invert(p);
        if (!ll || !isFinite(ll[0]) || Math.abs(ll[1]) > 90) return null;
        const back = this.flat(ll); // reject points outside the curved outline
        return back && Math.hypot(back[0] - p[0], back[1] - p[1]) < 1 ? ll : null;
      }
      const proj = this.projection();
      if (Math.hypot(x - this.w / 2, y - this.h / 2) > proj.scale()) return null;
      const ll = proj.invert([x, y]);
      return ll && isFinite(ll[0]) ? ll : null;
    }
    zoomToCountries(cs) {
      const lls = cs.flatMap(c => c.shape ? c.shape.ring : [c.bounds[0], c.bounds[1]]).map(p => p.slice());
      if (lls.some(p => p[0] > 90) && lls.some(p => p[0] < -90)) lls.forEach(p => { if (p[0] < 0) p[0] += 360; });
      const w = d3.min(lls, p => p[0]), e = d3.max(lls, p => p[0]), s = d3.min(lls, p => p[1]), n = d3.max(lls, p => p[1]);
      this.fitBox([[w - 0.3, s - 0.3], [e + 0.3, n + 0.3]]);
    }
  };

  function mod(a, n) { return ((a % n) + n) % n; }
  // Zoomed in, most of the world is off screen, so shapes and lines are split into pieces (one polygon or line
  // each) that can be skipped when they're out of view. Made once per geometry, the first time it's needed.
  function piecesOf(g) {
    if (g._pieces) return g._pieces;
    const out = [], add = (type, coordinates) => out.push(capOf({ type, coordinates }));
    const walk = gm => {
      if (!gm) return;
      if (gm.type === "FeatureCollection") gm.features.forEach(f => walk(f.geometry));
      else if (gm.type === "Feature") walk(gm.geometry);
      else if (gm.type === "Polygon" || gm.type === "LineString") add(gm.type, gm.coordinates);
      else if (gm.type === "MultiPolygon") gm.coordinates.forEach(c => add("Polygon", c));
      else if (gm.type === "MultiLineString") gm.coordinates.forEach(c => add("LineString", c));
      else if (gm.type === "GeometryCollection") gm.geometries.forEach(walk);
    };
    walk(g);
    return (g._pieces = out);
  }
  // a [lon, lat] point as a unit vector (dot products give the cosine of the angle between two points)
  function unitVec([lo, la]) {
    const l = lo * RAD, p = la * RAD, cp = Math.cos(p);
    return [cp * Math.cos(l), cp * Math.sin(l), Math.sin(p)];
  }
  // Douglas-Peucker on a closed ring (lon/lat degrees); returns the points kept, first and last included
  function simplifyRing(pts, tol) {
    const n = pts.length;
    if (n <= 4) return pts;
    const keep = new Uint8Array(n); keep[0] = keep[n - 1] = 1;
    let far = 0, fd = -1; // split the ring at the point farthest from the start
    for (let i = 1; i < n - 1; i++) { const d = (pts[i][0] - pts[0][0]) ** 2 + (pts[i][1] - pts[0][1]) ** 2; if (d > fd) { fd = d; far = i; } }
    keep[far] = 1;
    const stack = [[0, far], [far, n - 1]];
    while (stack.length) {
      const [a, b] = stack.pop(), [ax, ay] = pts[a], [bx, by] = pts[b], dx = bx - ax, dy = by - ay, L = dx * dx + dy * dy;
      let md = 0, mi = -1;
      for (let i = a + 1; i < b; i++) {
        const [x, y] = pts[i], u = L ? Math.max(0, Math.min(1, ((x - ax) * dx + (y - ay) * dy) / L)) : 0;
        const d = Math.hypot(ax + u * dx - x, ay + u * dy - y);
        if (d > md) { md = d; mi = i; }
      }
      if (md > tol) { keep[mi] = 1; stack.push([a, mi], [mi, b]); }
    }
    return pts.filter((_, i) => keep[i]);
  }
  // a piece's centre and angular radius (every point is within `radius` of `centre`)
  function capOf(geom) {
    const pts = geom.type === "Polygon" ? geom.coordinates[0] : geom.coordinates;
    let x = 0, y = 0, z = 0;
    for (const [lo, la] of pts) {
      const l = lo * Math.PI / 180, p = la * Math.PI / 180, cp = Math.cos(p);
      x += cp * Math.cos(l); y += cp * Math.sin(l); z += Math.sin(p);
    }
    const n = Math.hypot(x, y, z);
    geom.centroid = n < 1e-9 ? [0, 0] : [Math.atan2(y, x) * 180 / Math.PI, Math.asin(z / n) * 180 / Math.PI];
    let r = 0;
    for (const pt of pts) r = Math.max(r, d3.geoDistance(geom.centroid, pt));
    geom.radius = n < 1e-9 ? Math.PI : r + 0.002;
    return geom;
  }
  // shortest distance from a point to a closed outline
  function edgeDistance(pts, x, y) {
    let best = Infinity;
    for (let i = 0, j = pts.length - 1; i < pts.length; j = i++) {
      const [ax, ay] = pts[j], [bx, by] = pts[i], dx = bx - ax, dy = by - ay, L = dx * dx + dy * dy;
      const u = L ? Math.max(0, Math.min(1, ((x - ax) * dx + (y - ay) * dy) / L)) : 0;
      best = Math.min(best, Math.hypot(ax + u * dx - x, ay + u * dy - y));
    }
    return best;
  }
  function inBounds(b, [lon, lat]) {
    if (lat < b[0][1] - 0.01 || lat > b[1][1] + 0.01) return false;
    if (b[0][0] <= b[1][0]) return lon >= b[0][0] - 0.01 && lon <= b[1][0] + 0.01;
    return lon >= b[0][0] - 0.01 || lon <= b[1][0] + 0.01; // crosses the date line
  }
})();
