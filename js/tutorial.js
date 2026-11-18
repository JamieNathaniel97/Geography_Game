// Gaia Quest – the Learning mode demo (Learning_mode_clip.md). Runs only with ?demo=learning in the address:
// the real app plays a short storyboard, with a pretend fingertip showing each tap and captions at the top.
// tools/record_clip.py records it, frame by frame, into the clip on the Learning mode tab.
(function () {
  "use strict";
  if (!/[?&]demo=learning\b/.test(location.search)) return;
  const $ = id => document.getElementById(id);
  const W = ms => new Promise(r => setTimeout(r, ms));
  const frame = () => new Promise(r => requestAnimationFrame(r));
  const ease = t => (t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2); // ease-in-out
  const captions = !/[?&]captions=0\b/.test(location.search);
  document.documentElement.classList.add("demo");

  // ----- the pieces drawn over the app: fingertip, ripple, caption, fade -----
  const css = document.createElement("style");
  css.textContent = `
    .demo .jumpbar, .demo #toast, .demo .credit { display: none !important; }
    .demofinger { position: fixed; left: 0; top: 0; width: 44px; height: 44px; margin: -22px 0 0 -22px; border-radius: 50%;
      background: radial-gradient(circle at 40% 35%, rgba(255,255,255,.95), rgba(225,232,235,.85) 60%, rgba(160,175,180,.8));
      box-shadow: 0 3px 10px rgba(0,0,0,.35), inset 0 0 0 1px rgba(0,0,0,.08); z-index: 60; pointer-events: none; opacity: 0; }
    .demoripple { position: fixed; width: 44px; height: 44px; margin: -22px 0 0 -22px; border-radius: 50%; border: 3px solid rgba(255,255,255,.9);
      box-shadow: 0 0 0 1px rgba(0,0,0,.25); z-index: 59; pointer-events: none; }
    .democap { position: fixed; left: 50%; top: 64px; transform: translate(-50%, -50%); z-index: 58; pointer-events: none; display: flex; gap: 8px;
      align-items: center; padding: 7px 14px 7px 8px; border-radius: 999px; background: var(--panel); color: var(--fg);
      box-shadow: 0 4px 16px rgba(0,0,0,.3); font: 700 17px var(--display); white-space: nowrap; opacity: 0; transition: opacity .3s; }
    .democap .n { width: 26px; height: 26px; border-radius: 50%; background: var(--accent); color: var(--accent-fg); display: grid; place-items: center; font-size: 14px; }
    .democap.on { opacity: 1; }
    .demofade { position: fixed; inset: 0; background: var(--bg); z-index: 57; pointer-events: none; opacity: 0; }
    .demoblock { position: fixed; inset: 0; z-index: 56; }`;
  document.head.appendChild(css);
  const add = cls => { const e = document.createElement("div"); e.className = cls; document.body.appendChild(e); return e; };
  const finger = add("demofinger"), cap = add("democap"), fade = add("demofade");
  add("demoblock"); // real touches do nothing while the demo plays
  let fx = innerWidth / 2, fy = innerHeight - 60, fs = 1, fo = 0;
  const place = () => { finger.style.transform = `translate(${fx}px, ${fy}px) scale(${fs})`; finger.style.opacity = fo; };
  place();

  async function tween(ms, fn) {
    const t0 = performance.now();
    for (;;) {
      const k = Math.min(1, (performance.now() - t0) / ms);
      fn(ease(k), k);
      if (k >= 1) return;
      await frame();
    }
  }
  const fingerFade = (to, ms = 400) => { const from = fo; return tween(ms, e => { fo = from + (to - from) * e; place(); }); };
  // glide on a gentle curve (bowed to one side), never jumping
  async function moveTo(x, y, ms = 700) {
    const x0 = fx, y0 = fy, bow = Math.min(60, Math.hypot(x - x0, y - y0) * 0.18);
    const nx = -(y - y0), ny = x - x0, nl = Math.hypot(nx, ny) || 1;
    await tween(ms, e => {
      const b = Math.sin(Math.PI * e) * bow;
      fx = x0 + (x - x0) * e + nx / nl * b; fy = y0 + (y - y0) * e + ny / nl * b; place();
    });
  }
  async function press(target) {
    await tween(110, e => { fs = 1 - 0.18 * e; place(); });
    const r = add("demoripple");
    r.style.left = fx + "px"; r.style.top = fy + "px";
    target();
    tween(450, e => { r.style.transform = `scale(${1 + 1.4 * e})`; r.style.opacity = 1 - e; }).then(() => r.remove());
    await tween(140, e => { fs = 0.82 + 0.18 * e; place(); });
  }
  const centreOf = el => { const r = el.getBoundingClientRect(); return [r.left + r.width / 2, r.top + r.height / 2]; };
  async function tapEl(el, ms) { const [x, y] = centreOf(el); await moveTo(x, y, ms); await press(() => el.click()); }
  // a tap that changes map: the finger taps, the screen fades, and only then does the button act (no jump cut)
  async function tapThroughFade(el, ms, ready) {
    const [x, y] = centreOf(el); await moveTo(x, y, ms); await press(() => {});
    await crossFade(async () => { el.click(); await until(ready); });
  }
  async function tapMap(lonlat, ms) {
    const m = GG.debug.main, c = m.canvas.getBoundingClientRect(), p = m.projection()(lonlat);
    await moveTo(c.left + p[0], c.top + p[1], ms);
    await press(() => m.canvas.dispatchEvent(new MouseEvent("click", { clientX: fx, clientY: fy, bubbles: true })));
  }
  function caption(n, text) {
    if (!captions) return;
    // level with the world map's Borders button, measured once, then fixed (it doesn't follow the button on other maps)
    if (!cap.dataset.top) { const b = $("bordersBtn"), r = b && b.getBoundingClientRect(); cap.dataset.top = r && r.height ? r.top + r.height / 2 : 64; }
    cap.style.top = cap.dataset.top + "px";
    if (!text) { cap.classList.remove("on"); return; }
    cap.innerHTML = (n ? `<span class="n">${n}</span>` : "") + `<span>${text}</span>`;
    cap.style.paddingLeft = n ? "8px" : "14px";
    cap.classList.add("on");
  }
  // the globe turns and zooms in one continuous move
  async function fly(lon, lat, k, ms) {
    const m = GG.debug.main, s = m.globeState(), lon0 = -s.rotate[0], lat0 = -s.rotate[1], k0 = m.t.k;
    let L = lon; while (L - lon0 > 180) L -= 360; while (lon0 - L > 180) L += 360;
    await tween(ms, e => m.sel.call(m.zoom.transform, m.globeTransform(lon0 + (L - lon0) * e, lat0 + (lat - lat0) * e, k0 * Math.pow(k / k0, e))));
  }
  // map changes (globe <-> a country's map) cross a short fade; the new map is drawn and settled before it fades in
  const crossFade = async change => {
    await tween(260, e => { fade.style.opacity = e; });
    await change(); await frame(); await frame(); await W(250); // the new map drawn and settled before it fades in
    await tween(320, e => { fade.style.opacity = 1 - e; });
  };
  const until = async test => { while (!test()) await W(50); };

  // ----- the storyboard -----
  async function play() {
    await until(() => window.GG && GG.debug && GG.debug.main && GG.debug.main.geo && GG.debug.startGame);
    const splash = $("splash");
    while (splash && document.body.contains(splash) && !splash.classList.contains("out")) { splash.click(); await W(100); }
    if (!$("setup").hidden) $("setupClose").click();
    const m = GG.debug.main;
    await GG.debug.startGame("explore", "world", "globe", "world");
    await GG.debug.preload("us");
    const k1 = 1; // position 1: the splash's view, the globe over Europe and Africa
    m.sel.call(m.zoom.transform, m.globeTransform(18, 22, k1));
    await W(700);
    const loopStart = performance.now();
    window.__demoStart = loopStart;
    // 1. hold; the finger fades in near the bottom
    fingerFade(1, 600);
    await W(1000);
    // 2. zoom to the US
    const side = Math.min(m.w, m.h) * 0.9, kUS = side / (52 * m.R0 * Math.PI / 180);
    await fly(-98, 39, kUS, 3000);
    // 3. tap the USA
    caption(1, "Tap a Country");
    await tapMap([-98.5, 38.6], 800);
    // 4. hold on the card
    await W(1500);
    // 5. more facts
    caption(2, "Country Information");
    await tapEl($("lcMoreBtn"), 650);
    // 6. hold, and scroll the card a little
    await W(700);
    const card = $("learnCard"), top0 = card.scrollTop, room = Math.min(220, card.scrollHeight - card.clientHeight);
    if (room > 20) { await tween(1100, e => { card.scrollTop = top0 + room * e; }); await W(300); }
    // 7. fewer facts (the pinned arrow, top left of the card)
    await tapEl($("lcLess"), 650);
    await W(300);
    // 8. focus on the US
    caption(3, "Zoom to Country");
    await tapThroughFade($("focusBtn"), 650, () => GG.debug.main.geo && GG.debug.main.geo.kind === "us");
    // 9. tap Colorado
    caption(4, "Tap a Region");
    await W(300);
    await tapMap([-105.5, 39.0], 800);
    // 10. hold on the state card, then open its facts and scroll, as with the country
    await W(1300);
    caption(5, "Regional Information");
    await tapEl($("lcMoreBtn"), 650);
    await W(600);
    const card2 = $("learnCard"), top2 = card2.scrollTop, room2 = Math.min(200, card2.scrollHeight - card2.clientHeight);
    if (room2 > 20) { await tween(1000, e => { card2.scrollTop = top2 + room2 * e; }); await W(300); }
    await tapEl($("lcLess"), 650);
    await W(400);
    // 11. back to the world map
    caption(6, "Return to World Map");
    await tapThroughFade($("worldBtn"), 700, () => !GG.debug.main.geo.kind && $("lcName").textContent === "United States");
    // back where we left: the US, its card open again. Close it
    await W(500);
    caption(0, "");
    await tapEl($("lcClose"), 650);
    await W(250);
    await moveTo(innerWidth / 2, innerHeight - 60, 800);
    // 12. smooth return to position 1
    await fly(18, 22, k1, 3000);
    // 13. hold; the finger fades out
    await fingerFade(0, 600);
    await W(400);
    window.__demoLength = performance.now() - loopStart;
    window.__demoDone = true;
  }
  play().catch(e => { window.__demoError = String(e && e.stack || e); });
})();
