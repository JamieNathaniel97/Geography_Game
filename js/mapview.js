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
  };
  const NORTH = 85, SOUTH = -60, CURVED_CENTRE = 10;
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
      this.hits = { islands: [], bubbles: [] };
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
      this.resize();
    }

    readColours() {
      const cs = getComputedStyle(document.documentElement), v = n => cs.getPropertyValue(n).trim();
      this.col = { bg: v("--bg"), sea: v("--sea"), land: v("--land"), border: v("--border"), coast: v("--coast"),
        terr: v("--terr"), good: v("--good"), bad: v("--bad"), flash: v("--flash"), marker: v("--marker"),
        panel: v("--panel"), fg: v("--fg"), halo: v("--halo"), off: v("--off") };
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
        if (!this.wrap) p.rotate(this.flat.rotate());
        return p;
      }
      const g = this.globeState();
      return this.globe.rotate([g.rotate[0], g.rotate[1], 0]).scale(g.scale).translate([this.w / 2, this.h / 2]);
    }
    pxPerDeg() {
      return this.mode === "flat" ? this.t.k * this.BW / 360 : this.R0 * this.t.k * RAD;
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
        const k = Math.max(this.zoom.scaleExtent()[0], Math.min(MAX_K, side / (spanDeg * this.BW / 360)));
        const p = this.flat([lon, Math.max(SOUTH + 1, Math.min(NORTH - 1, lat))]);
        let x = p[0];
        if (this.crop) { const [x0, , x1] = this.cropRect(); while (x < x0) x += this.BW; while (x > x1) x -= this.BW; }
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
        this.setTransform(d3.zoomIdentity.translate(this.w / 2 - x, (this.h - this.BH) / 2).scale(1), animate);
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
        if (this.wrap) sphere.rect(0, 0, this.BW, this.BH); else sphere.addPath(new Path2D(path({ type: "Sphere" })));
        this.flatPaths = {
          sphere,
          features: this.geo.f50.map(f => ({ f, p: new Path2D(path(f) || "") })),
          borders: new Path2D(path(this.geo.borders50) || ""),
          coast: new Path2D(path(this.geo.coast50) || ""),
        };
      }
      const P = this.flatPaths;
      const groups = new Map();
      P.features.forEach(({ f, p }) => { const c = this.fillFor(f); if (!groups.has(c)) groups.set(c, []); groups.get(c).push(p); });
      this.copies().forEach(dx => {
        ctx.setTransform(this.dpr * t.k, 0, 0, this.dpr * t.k, this.dpr * (t.x + dx), this.dpr * t.y);
        ctx.fillStyle = col.sea; ctx.fill(P.sphere);
        groups.forEach((ps, c) => { ctx.fillStyle = c; ps.forEach(p => ctx.fill(p)); });
        if (this.terrain && this.relief && this.wrap) {
          this.drawFlatRelief(dx);
          ctx.setTransform(this.dpr * t.k, 0, 0, this.dpr * t.k, this.dpr * (t.x + dx), this.dpr * t.y);
        }
        ctx.lineJoin = "round";
        ctx.strokeStyle = col.coast; ctx.lineWidth = 0.6 / t.k; ctx.stroke(P.coast);
        if (this.borders) { ctx.strokeStyle = col.border; ctx.lineWidth = 0.7 / t.k; ctx.stroke(P.borders); }
      });
    }
    drawGlobe() {
      const ctx = this.ctx, col = this.col, proj = this.projection();
      const path = d3.geoPath(proj, ctx);
      // full detail is too slow to redraw every frame on a phone, so spin with the lighter outlines
      const light = this.moving && this.t.k < 4;
      const feats = light ? this.geo.f110 : this.geo.f50;
      const centre = this.centre();
      const R = proj.scale(), half = Math.hypot(this.w, this.h) / 2;
      const view = half >= R ? Math.PI / 2 : Math.asin(half / R);
      ctx.beginPath(); path({ type: "Sphere" }); ctx.fillStyle = col.sea; ctx.fill();
      const groups = new Map();
      feats.forEach(f => {
        if (d3.geoDistance(f.centroid, centre) > view + f.radius) return;
        const c = this.fillFor(f); if (!groups.has(c)) groups.set(c, []); groups.get(c).push(f);
      });
      groups.forEach((fs, c) => { ctx.beginPath(); fs.forEach(f => path(f)); ctx.fillStyle = c; ctx.fill(); });
      if (this.terrain && this.relief) {
        ctx.globalCompositeOperation = "multiply";
        ctx.imageSmoothingEnabled = true;
        ctx.drawImage(this.globeRelief(this.moving ? 2.5 : 1), 0, 0, this.w, this.h); // 0.4 resolution while spinning
        ctx.globalCompositeOperation = "source-over";
      }
      ctx.lineJoin = "round";
      ctx.beginPath(); path(light ? this.geo.coast110 : this.geo.coast50); ctx.strokeStyle = col.coast; ctx.lineWidth = 0.6; ctx.stroke();
      if (this.borders) { ctx.beginPath(); path(light ? this.geo.borders110 : this.geo.borders50); ctx.strokeStyle = col.border; ctx.lineWidth = 0.7; ctx.stroke(); }
      ctx.beginPath(); path({ type: "Sphere" }); ctx.strokeStyle = col.halo; ctx.lineWidth = 1.5; ctx.stroke();
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
      const ppd0 = this.mode === "flat" ? this.BW / 360 : this.R0 * RAD * 0.9;
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
      geo.clusters.forEach(cl => {
        if (!cl.members.every(c => this.active(c))) return;
        const ms = cl.members.map(shapeOf).filter(Boolean);
        if (ms.length < 2) return;
        let overlap = false;
        for (let i = 0; i < ms.length && !overlap; i++) for (let j = i + 1; j < ms.length; j++)
          if ((ms[i].f > 1 || ms[j].f > 1) && Math.hypot(ms[i].x - ms[j].x, ms[i].y - ms[j].y) < (ms[i].r + ms[j].r) / 2) { overlap = true; break; }
        if (!overlap) return;
        cl.members.forEach(c => hidden.add(c));
        const bx = d3.mean(ms, s => s.x), by = d3.mean(ms, s => s.y);
        offsets.forEach(dx => { if (onScreen(bx + dx, by, 13)) bubbles.push({ cl, x: bx + dx, y: by, r: 13 }); });
      });
      geo.countries.forEach(c => {
        if (hidden.has(c) || !this.active(c)) return;
        if (c.shape) {
          const s = shapeOf(c); if (!s) return;
          offsets.forEach(dx => { if (onScreen(s.x + dx, s.y, s.r)) islands.push(shift(s, dx)); });
        } else if (c.ring && this.visible(c.anchor)) {
          const px = c.sizeDeg * ppd;
          let d;
          if (c.ringAdaptive) {
            // 8 px fully zoomed out, growing more slowly than the map (zoom^0.45), up to 90 px;
            // it goes once the country itself is 40 px across and easy to tap
            if (px >= 40) return;
            d = Math.min(90, 8 * Math.pow(Math.max(1, ppd / ppd0), 0.45));
          } else {
            // the ring grows as you zoom in (22 px up to 36 px) and goes once the country is that big
            if (px >= RING_MAX) return;
            d = ringSize(px);
          }
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
      this.hits = { islands: islands.slice().reverse(), bubbles, rings };
    }

    // ----- tapping -----
    handleClick(e) {
      const r = this.canvas.getBoundingClientRect();
      const x = e.clientX - r.left, y = e.clientY - r.top;
      if (this.opts.onPoint && this.opts.onPoint(this, x, y)) return; // e.g. the magnifier
      const b = this.hits.bubbles.find(b => Math.hypot(b.x - x, b.y - y) <= b.r + 4);
      if (b) { this.zoomToCountries(b.cl.members); return; }
      const c = this.resolveTap(x, y);
      if (c) this.opts.onTap(c, this);
    }
    // A tap on an open (not yet answered) country counts as that country. A tap anywhere else (sea, an
    // answered or greyed-out country) goes to the nearest open small country within reach, so tiny
    // countries are easy to hit once their neighbours are done.
    resolveTap(x, y) {
      const open = this.opts.isOpen || (() => true);
      // 1. inside the ring of a small country: always that country (even over land, e.g. Vatican in Italy)
      const ring = this.hits.rings.filter(r => open(r.c) && Math.hypot(r.x - x, r.y - y) <= r.d / 2 + 3)
        .sort((a, b) => Math.hypot(a.x - x, a.y - y) - Math.hypot(b.x - x, b.y - y))[0];
      if (ring) return ring.c;
      // 2. inside an island oval, or on the country itself
      const direct = this.countryAt(x, y);
      if (direct && open(direct)) return direct;
      // 3. near a small open country or island oval: snap to the nearest one within reach
      const proj = this.projection(), ppd = this.pxPerDeg(), offsets = this.copies();
      let best = null, bd = Infinity;
      this.hits.islands.forEach(s => {
        if (!open(s.c)) return;
        const gap = d3.polygonContains(s.pts, [x, y]) ? 0 : edgeDistance(s.pts, x, y);
        if (gap < 20 && gap < bd) { bd = gap; best = s.c; }
      });
      for (const c of this.geo.countries) {
        if (c.shape || !c.anchor || !open(c)) continue;
        const size = c.sizeDeg * ppd;
        if (size >= 44 || !this.visible(c.anchor)) continue;
        const reach = Math.max(22, size / 2 + 14);
        const p = proj(c.anchor);
        for (const dx of offsets) {
          const d = Math.hypot(p[0] + dx - x, p[1] - y);
          if (d < reach && d < bd) { bd = d; best = c; }
        }
      }
      return best || direct;
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
