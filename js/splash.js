// Splash screen: a globe over Europe and Africa turns slowly while its countries light up green, with the
// app's name and tagline. It plays while the map data loads, stays for at least one full animation, and can be
// tapped away once the app is ready. app.js calls GG.splashDone() when the map has loaded (or failed to).
(function () {
  const GG = (window.GG = window.GG || {});
  const el = document.getElementById("splash");
  if (!el) { GG.splashDone = () => {}; return; }
  const canvas = el.querySelector("canvas"), ctx = canvas.getContext("2d");
  const DURATION = 3.4, FILL_START = 0.35, FILL_SPREAD = 2.4, FILL_FADE = 0.3;
  const SHADES = d3.range(9).map(s => d3.interpolateRgb("#2e464c", "#3fbf6a")(s / 8));
  const GRATICULE = d3.geoGraticule10();
  const still = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  let feats = null, order = [], start = performance.now(), raf = 0, ready = false, gone = false;
  GG.splashShowing = true; // the map behind draws with light outlines until the splash goes

  fetch("data/world-110m.json").then(r => r.json()).then(t => {
    feats = topojson.feature(t, t.objects.countries).features;
    order = feats.map(() => Math.random());
    start = performance.now();
    el.classList.add("play");
    raf = requestAnimationFrame(frame);
  }).catch(() => { el.classList.add("play"); });

  // one drawing loop only: each frame schedules the next
  function frame() {
    if (gone) return;
    draw();
    if ((performance.now() - start) / 1000 < DURATION + 0.1) raf = requestAnimationFrame(frame);
    else maybeHide();
  }
  function draw() {
    // a slightly lower resolution than the screen: invisible on a moving globe, and much less work per frame
    const r = canvas.getBoundingClientRect(), dpr = Math.min(window.devicePixelRatio || 1, 1.5);
    const cw = Math.round(r.width * dpr), ch = Math.round(r.height * dpr);
    if (canvas.width !== cw || canvas.height !== ch) { canvas.width = cw; canvas.height = ch; }
    const W = r.width, H = r.height;
    const t = still ? DURATION : (performance.now() - start) / 1000, p = Math.min(1, t / DURATION);
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    ctx.clearRect(0, 0, W, H);
    const R = Math.min(W * 0.4, H * 0.27), cx = W / 2, cy = H * 0.38;
    const proj = d3.geoOrthographic().rotate([-(4 + 14 * p), -22]).scale(R).translate([cx, cy]);
    const path = d3.geoPath(proj, ctx);
    const glow = ctx.createRadialGradient(cx, cy, R * 0.9, cx, cy, R * 1.25);
    glow.addColorStop(0, "rgba(79,179,212,.22)"); glow.addColorStop(1, "rgba(79,179,212,0)");
    ctx.fillStyle = glow; ctx.fillRect(0, 0, W, H);
    ctx.beginPath(); path({ type: "Sphere" }); ctx.fillStyle = "#1c3c47"; ctx.fill();
    ctx.beginPath(); path(GRATICULE); ctx.strokeStyle = "rgba(127,208,234,.12)"; ctx.lineWidth = 0.6; ctx.stroke();
    // countries grouped into 8 shades from dim to green, so each frame is a handful of fills, not hundreds
    const STEPS = 8, buckets = Array.from({ length: STEPS + 1 }, () => []);
    feats.forEach((f, i) => {
      const lit = Math.max(0, Math.min(1, (t - FILL_START - order[i] * FILL_SPREAD) / FILL_FADE));
      buckets[Math.round(lit * STEPS)].push(f);
    });
    buckets.forEach((fs, s) => {
      if (!fs.length) return;
      ctx.beginPath(); fs.forEach(f => path(f));
      ctx.fillStyle = SHADES[s]; ctx.fill();
    });
    ctx.beginPath(); feats.forEach(f => path(f)); ctx.strokeStyle = "#1c3c47"; ctx.lineWidth = 0.5; ctx.stroke();
    ctx.beginPath(); path({ type: "Sphere" }); ctx.strokeStyle = "rgba(127,208,234,.35)"; ctx.lineWidth = 1; ctx.stroke();
  }

  function maybeHide(force) {
    if (gone || !ready) return;
    const t = (performance.now() - start) / 1000;
    if (force || t >= DURATION || !feats) hide();
    else setTimeout(maybeHide, (DURATION - t) * 1000 + 30);
  }
  function hide() {
    gone = true; cancelAnimationFrame(raf);
    GG.splashShowing = false;
    if (GG.onSplashGone) GG.onSplashGone(); // redraw the map in full detail
    el.classList.add("out");
    setTimeout(() => el.remove(), 450);
  }
  el.addEventListener("click", () => maybeHide(true)); // tap to skip, once the app is ready
  GG.splashDone = () => { ready = true; maybeHide(); };
})();
