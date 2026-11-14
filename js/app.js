// Game logic and screen wiring. Build 1 foundation: game 1 (Find the country) for the whole world,
// plus Free tap for checking taps. Game modes are kept separate so more can be added (PLAN.md).
(function () {
  const GG = window.GG;
  const $ = id => document.getElementById(id);

  const S = { mode: "find", magnify: false };
  const state = {};     // iso -> 'good' | 'bad' | 'flash'
  const flashing = {};  // iso -> true while a wrong tap flashes yellow
  let geo, main, inset = null;

  // regions for the jump bar: [[west, south], [east, north]]
  const JUMPS = {
    europe: [[-12, 35], [42, 71]], asia: [[26, -11], [150, 56]], africa: [[-19, -36], [53, 38]],
    namerica: [[-169, 7], [-52, 72]], carib: [[-86, 9], [-59, 27]], samerica: [[-82, -56], [-34, 13]],
    oceania: [[112, -48], [189.5, 15]],
  };

  const getState = c => (flashing[c.iso] ? "flash" : state[c.iso] || null);

  // ---------- game: Find the country ----------
  // `order` holds the countries still to answer; the arrows move through it with no penalty
  let order = [], idx = 0, target = null, busy = false, nGood = 0, nBad = 0, finished = false;

  function newGame() {
    Object.keys(state).forEach(k => delete state[k]);
    order = d3.shuffle(geo.countries.slice()); idx = 0; nGood = nBad = 0; busy = false; finished = false;
    show();
  }
  function next() {
    order.splice(idx, 1);
    if (idx >= order.length) idx = 0;
    if (!order.length) finished = true;
    show();
  }
  function step(d) {
    if (busy || S.mode !== "find" || order.length < 2) return;
    idx = (idx + d + order.length) % order.length;
    show();
  }
  function show() {
    busy = false;
    const explore = S.mode === "explore";
    target = !explore && !finished ? order[idx] || null : null;
    const t = $("target"); t.className = "target";
    $("prev").hidden = $("fwd").hidden = explore || finished;
    $("giveup").hidden = explore;
    resetGiveUp();
    if (explore) {
      $("eyebrow").textContent = "Free tap";
      t.textContent = "Tap any country";
      $("score").textContent = "Shows the name of whatever you tap.";
    } else if (finished) {
      $("eyebrow").textContent = "Finished";
      t.textContent = `${nGood} of ${geo.countries.length} right`;
      $("score").innerHTML = `<b>${nGood}</b> right · <b>${nBad}</b> missed`;
      $("giveup").textContent = "Play again";
    } else {
      $("eyebrow").textContent = "Find";
      t.textContent = target.name;
      $("score").innerHTML = `<b>${nGood}</b> right · <b>${nBad}</b> missed · ${order.length} to go`;
    }
    redraw();
  }
  function redraw() { main.requestDraw(); if (inset) inset.requestDraw(); }

  function tap(c, view) {
    if (S.mode === "explore") {
      Object.keys(state).forEach(k => { if (state[k] === "flash") delete state[k]; });
      state[c.iso] = "flash"; $("target").textContent = c.name; redraw();
      return;
    }
    if (!target || busy || state[c.iso] === "good") return; // already-correct countries do nothing
    busy = true;
    const t = $("target");
    if (c === target) { state[c.iso] = "good"; nGood++; t.classList.add("good"); }
    else {
      state[target.iso] = "bad"; nBad++; t.classList.add("bad");
      flashing[c.iso] = true; // the tapped country flashes yellow once
      setTimeout(() => { delete flashing[c.iso]; redraw(); }, 450);
    }
    redraw();
    setTimeout(() => { if (inset && view === inset) closeInset(); next(); }, c === target ? 650 : 1400);
  }

  // Give up: tap once to arm, again to confirm; the rest are shown in red
  let giveUpTimer;
  function resetGiveUp() { clearTimeout(giveUpTimer); const b = $("giveup"); b.classList.remove("confirm"); b.textContent = "Give up"; }
  $("giveup").onclick = () => {
    if (finished) { newGame(); return; }
    const b = $("giveup");
    if (!b.classList.contains("confirm")) {
      b.classList.add("confirm"); b.textContent = "Tap again to give up";
      giveUpTimer = setTimeout(resetGiveUp, 3000);
      return;
    }
    order.forEach(c => { if (!state[c.iso]) { state[c.iso] = "bad"; nBad++; } });
    order = []; finished = true; show();
  };
  $("prev").onclick = () => step(-1);
  $("fwd").onclick = () => step(1);

  // ---------- map controls ----------
  function setViewButton() { $("viewBtn").textContent = main.mode === "globe" ? "Flat map" : "Globe"; }
  $("viewBtn").onclick = () => { main.setMode(main.mode === "globe" ? "flat" : "globe"); setViewButton(); };
  $("bordersBtn").onclick = () => {
    main.borders = !main.borders;
    $("bordersBtn").classList.toggle("on", main.borders); $("bordersBtn").setAttribute("aria-pressed", main.borders);
    if (inset) inset.borders = main.borders;
    redraw();
  };
  function setMag(on) {
    S.magnify = on;
    $("magBtn").classList.toggle("on", on); $("magBtn").setAttribute("aria-pressed", on);
    toast(on ? "Tap where you want to magnify." : null);
  }
  $("magBtn").onclick = () => setMag(!S.magnify);
  $("jumps").addEventListener("click", e => {
    const b = e.target.closest("button"); if (!b) return;
    if (b.dataset.v === "world") main.world(); else main.fitBox(JUMPS[b.dataset.v]);
  });

  let toastTimer;
  function toast(text, ms) {
    const el = $("toast"); clearTimeout(toastTimer);
    if (!text) { el.hidden = true; return; }
    el.textContent = text; el.hidden = false;
    if (ms) toastTimer = setTimeout(() => (el.hidden = true), ms);
  }

  // ---------- magnifier inset ----------
  function openInset(ll, span) {
    $("inset").hidden = false;
    inset = new GG.MapView($("insetMap"), { geo, mode: "flat", getState, onTap: tap, isTarget: c => c === target, borders: main.borders });
    inset.lookAt(ll[0], ll[1], span, false);
  }
  function closeInset() { $("inset").hidden = true; inset = null; }
  $("insetClose").onclick = closeInset;
  $("inset").addEventListener("click", e => { if (e.target === $("inset")) closeInset(); });
  function onPoint(view, x, y) {
    if (!S.magnify || view !== main) return false;
    const ll = main.lonLatAt(x, y);
    setMag(false);
    if (ll) openInset(ll, Math.min(main.w, main.h) * 0.9 / main.pxPerDeg() / 6);
    return true;
  }

  // ---------- menu ----------
  $("menuBtn").onclick = () => { $("menu").hidden = false; };
  $("menuClose").onclick = () => { $("menu").hidden = true; };
  $("menu").addEventListener("click", e => { if (e.target === $("menu")) $("menu").hidden = true; });
  $("segMode").addEventListener("click", e => {
    const b = e.target.closest("button"); if (!b) return;
    $("segMode").querySelectorAll("button").forEach(x => x.classList.toggle("on", x === b));
    S.mode = b.dataset.v;
    Object.keys(state).forEach(k => delete state[k]);
    if (S.mode === "find") newGame(); else show();
    $("menu").hidden = true;
  });
  $("newGame").onclick = () => { $("menu").hidden = true; newGame(); };
  document.addEventListener("keydown", e => {
    if (e.key === "Escape") { $("menu").hidden = true; closeInset(); }
    if (e.key === "ArrowLeft") step(-1);
    if (e.key === "ArrowRight") step(1);
  });

  // ---------- start ----------
  async function start() {
    try {
      geo = await GG.loadGeo();
    } catch (err) {
      console.error(err);
      $("eyebrow").textContent = "Problem";
      $("target").textContent = "The map data didn't load. Check your connection and reload.";
      return;
    }
    main = new GG.MapView($("map"), { geo, mode: "globe", getState, onTap: tap, onPoint, isTarget: c => c === target });
    main.lookAt(15, 25, 120, false);
    setViewButton();
    newGame();
    let lastW = main.w;
    window.addEventListener("resize", () => {
      main.resize();
      if (Math.abs(main.w - lastW) > 40) { lastW = main.w; main.world(false); }
      main.requestDraw();
      if (inset) { inset.resize(); inset.requestDraw(); }
    });
    window.matchMedia("(prefers-color-scheme: dark)").addEventListener("change", () => {
      main.readColours(); if (inset) inset.readColours(); redraw();
    });
  }
  start();
})();
