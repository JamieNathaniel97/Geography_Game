// Game logic and screen wiring. Build 1: game 1 (Find the country) for the whole world, one continent
// or the Caribbean, plus Free tap. Game modes and regions are kept separate so more can be added (PLAN.md).
(function () {
  const GG = window.GG;
  const $ = id => document.getElementById(id);

  const S = { mode: "find", region: "world", magnify: false };
  const state = {};     // iso -> 'good' | 'bad' | 'flash'
  const flashing = {};  // iso -> true while a wrong tap flashes yellow
  let geo, main, inset = null;

  // Regions for quizzes and the jump bar. `view` is tuned separately for the globe and the flat map:
  // [centre longitude, centre latitude, degrees across the screen's shorter side].
  // `crop` is the region game's box, [[west, south], [east, north]]: the map can't leave it.
  // Russia and Turkey count in Europe and Asia; Caribbean countries also count in North America.
  const REGIONS = {
    world:    { name: "World" },
    europe:   { name: "Europe",        test: c => c.cont.includes("Europe"),        view: { globe: [13, 53, 38],       flat: [15, 53, 50] },       crop: [[-26, 33], [50, 72]] },
    asia:     { name: "Asia",          test: c => c.cont.includes("Asia"),          view: { globe: [88, 22.5, 88],     flat: [88, 22.5, 114.6] },  crop: [[24, -12], [150, 62]] },
    africa:   { name: "Africa",        test: c => c.cont.includes("Africa"),        view: { globe: [17, 1, 72],        flat: [17, 1, 86] },        crop: [[-27, -37], [60, 38]] },
    namerica: { name: "North America", test: c => c.cont.includes("North America"), view: { globe: [-90, 25, 69],      flat: [-104, 39.5, 90.3] }, crop: [[-170, 5], [-50, 75]] },
    carib:    { name: "Caribbean",     test: c => c.car,                            view: { globe: [-72.5, 18, 25.7],  flat: [-72.5, 18, 25.7] },  crop: [[-87, 9], [-58, 28]] },
    samerica: { name: "South America", test: c => c.cont.includes("South America"), view: { globe: [-58, -21.5, 44.7], flat: [-58, -24, 56] },     crop: [[-93, -57], [-33, 14]] },
    oceania:  { name: "Oceania",       test: c => c.cont.includes("Oceania"),       view: { globe: [167, -16, 74.3],   flat: [167, -16, 74.3] },   crop: [[110, -50], [212, 22]] },
  };
  const inRegion = c => S.region === "world" || REGIONS[S.region].test(c);
  const regionCountries = () => geo.countries.filter(inRegion);

  const getState = c => (flashing[c.iso] ? "flash" : state[c.iso] || null);
  // still to answer (Free tap: any country in the region); taps near small open countries snap to them
  const isOpen = c => inRegion(c) && (S.mode === "explore" || !state[c.iso]);

  // ---------- game: Find the country ----------
  // `order` holds the countries still to answer; the arrows move through it with no penalty
  let order = [], idx = 0, target = null, nGood = 0, nBad = 0, finished = false, total = 0;

  function newGame() {
    Object.keys(state).forEach(k => delete state[k]);
    const list = regionCountries();
    total = list.length;
    order = d3.shuffle(list); idx = 0; nGood = nBad = 0; finished = false;
    show();
  }
  function next() {
    order.splice(idx, 1);
    if (idx >= order.length) idx = 0;
    if (!order.length) finished = true;
    show();
  }
  function step(d) {
    if (S.mode !== "find" || order.length < 2) return;
    idx = (idx + d + order.length) % order.length;
    show();
  }
  function show() {
    const explore = S.mode === "explore";
    const where = S.region === "world" ? "" : " · " + REGIONS[S.region].name;
    target = !explore && !finished ? order[idx] || null : null;
    const t = $("target"); t.className = "target";
    $("prev").hidden = $("fwd").hidden = explore || finished;
    $("giveup").hidden = explore;
    resetGiveUp();
    if (explore) {
      $("eyebrow").textContent = "Free tap" + where;
      t.textContent = "Tap any country";
      $("score").textContent = "Shows the name of whatever you tap.";
    } else if (finished) {
      $("eyebrow").textContent = "Finished" + where;
      t.textContent = `${nGood} of ${total} right`;
      $("score").innerHTML = `<b>${nGood}</b> right · <b>${nBad}</b> missed`;
      $("giveup").textContent = "Play again";
    } else {
      $("eyebrow").textContent = "Find" + where;
      t.textContent = target.name;
      $("score").innerHTML = `<b>${nGood}</b> right · <b>${nBad}</b> missed · ${order.length} to go`;
    }
    redraw();
  }
  function redraw() { main.requestDraw(); if (inset) inset.requestDraw(); }

  function tap(c, view) {
    if (!inRegion(c)) return; // countries outside the region are greyed out and do nothing
    if (S.mode === "explore") {
      Object.keys(state).forEach(k => { if (state[k] === "flash") delete state[k]; });
      state[c.iso] = "flash"; $("target").textContent = c.name; redraw();
      return;
    }
    if (!target || state[c.iso] === "good") return; // already-correct countries do nothing
    // the next country appears instantly; the map keeps the green/red result
    if (c === target) { state[c.iso] = "good"; nGood++; }
    else {
      state[target.iso] = "bad"; nBad++;
      flashing[c.iso] = true; // the tapped country flashes yellow once
      setTimeout(() => { delete flashing[c.iso]; redraw(); }, 450);
      toast("Missed: " + target.name, 1800);
    }
    if (inset && view === inset) closeInset();
    next();
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
  $("terrainBtn").onclick = () => {
    const on = !main.terrain;
    main.setTerrain(on); if (inset) inset.setTerrain(on);
    $("terrainBtn").classList.toggle("on", on); $("terrainBtn").setAttribute("aria-pressed", on);
  };
  function setMag(on) {
    S.magnify = on;
    $("magBtn").classList.toggle("on", on); $("magBtn").setAttribute("aria-pressed", on);
    toast(on ? "Tap where you want to magnify." : null);
  }
  $("magBtn").onclick = () => setMag(!S.magnify);
  function goTo(key, animate = true) {
    if (key === "world") { main.world(animate); return; }
    const [lon, lat, span] = REGIONS[key].view[main.mode];
    main.lookAt(lon, lat, span, animate);
  }
  $("regionBtn").onclick = () => goTo(S.region);
  $("jumps").addEventListener("click", e => {
    const b = e.target.closest("button"); if (b) goTo(b.dataset.v);
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
    inset = new GG.MapView($("insetMap"), { geo, mode: "flat", flatStyle: main.styleKey, getState, onTap: tap,
      isTarget: c => c === target, isActive: inRegion, isOpen, borders: main.borders });
    if (main.terrain) inset.setTerrain(true);
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

  // ---------- setup screen (New game) ----------
  const pick = { mode: "find", region: "world", view: "globe" };
  function segSelect(el, v) { el.querySelectorAll("button").forEach(b => b.classList.toggle("on", b.dataset.v === v)); }
  function buildRegionButtons() {
    $("regions").innerHTML = "";
    Object.entries(REGIONS).forEach(([key, r]) => {
      const n = key === "world" ? geo.countries.length : geo.countries.filter(r.test).length;
      const b = document.createElement("button");
      b.type = "button"; b.dataset.v = key;
      b.innerHTML = `<span>${r.name}</span><small>${n}</small>`;
      $("regions").appendChild(b);
    });
  }
  function openSetup() {
    pick.mode = S.mode; pick.region = S.region; pick.view = S.region === "world" ? main.mode : "globe";
    segSelect($("segGame"), pick.mode); segSelect($("regions"), pick.region); segSelect($("segView"), pick.view);
    $("viewField").hidden = pick.region !== "world";
    $("setup").hidden = false;
  }
  function closeSetup() { $("setup").hidden = true; }
  $("menuBtn").onclick = openSetup;
  $("setupClose").onclick = closeSetup;
  $("setup").addEventListener("click", e => { if (e.target === $("setup")) closeSetup(); });
  $("segGame").addEventListener("click", e => { const b = e.target.closest("button"); if (b) { pick.mode = b.dataset.v; segSelect($("segGame"), pick.mode); } });
  $("regions").addEventListener("click", e => {
    const b = e.target.closest("button"); if (!b) return;
    pick.region = b.dataset.v; segSelect($("regions"), pick.region);
    $("viewField").hidden = pick.region !== "world"; // region games are always flat (chosen 2026-11-14)
  });
  $("segView").addEventListener("click", e => { const b = e.target.closest("button"); if (b) { pick.view = b.dataset.v; segSelect($("segView"), pick.view); } });
  $("startBtn").onclick = () => {
    closeSetup(); closeInset();
    startGame(pick.mode, pick.region, pick.region === "world" ? pick.view : "flat");
  };
  function startGame(mode, region, view) {
    S.mode = mode; S.region = region;
    // region games are cropped to the region; the jump bar is swapped for a "Whole region" button
    main.setCrop(region === "world" ? null : REGIONS[region].crop);
    $("jumpbar").hidden = region !== "world";
    $("regionBtn").hidden = region === "world";
    $("viewBtn").hidden = region !== "world"; // no globe for region games
    if (main.mode !== view) { main.setMode(view); setViewButton(); }
    goTo(region, false);
    if (mode === "find") newGame(); else { Object.keys(state).forEach(k => delete state[k]); show(); }
  }

  document.addEventListener("keydown", e => {
    if (e.key === "Escape") { closeSetup(); closeInset(); }
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
    // flat map is Patterson (chosen 2026-11-14); ?proj= still picks another style for testing
    const q = new URLSearchParams(location.search);
    const style = GG.FLAT_STYLES[q.get("proj")] ? q.get("proj") : "patterson";
    main = new GG.MapView($("map"), { geo, mode: "globe", flatStyle: style, getState, onTap: tap, onPoint,
      isTarget: c => c === target, isActive: inRegion, isOpen });
    main.lookAt(15, 25, 120, false);
    buildRegionButtons();
    GG.debug = { main, geo, startGame };
    setViewButton();
    // testing hooks: ?region=europe&view=flat starts that game; ?at=lon,lat,span and ?terrain=1 adjust the view
    if (REGIONS[q.get("region")] || q.get("view")) {
      const region = REGIONS[q.get("region")] ? q.get("region") : "world";
      startGame("find", region, region === "world" ? q.get("view") || "globe" : "flat");
    } else {
      newGame();
      openSetup(); // first screen: choose a game
    }
    if (q.get("terrain")) $("terrainBtn").click();
    if (q.get("at")) { const [lo, la, sp] = q.get("at").split(",").map(Number); main.lookAt(lo, la, sp, false); }
    let lastW = main.w;
    window.addEventListener("resize", () => {
      main.resize();
      if (Math.abs(main.w - lastW) > 40) { lastW = main.w; goTo(S.region, false); }
      main.requestDraw();
      if (inset) { inset.resize(); inset.requestDraw(); }
    });
    window.matchMedia("(prefers-color-scheme: dark)").addEventListener("change", () => {
      main.readColours(); if (inset) inset.readColours(); redraw();
    });
  }
  start();
})();
