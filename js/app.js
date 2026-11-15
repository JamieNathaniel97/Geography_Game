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

  // Games: find = Find the country, name = Name the countries, findcap = Find the country by its capital,
  // namecap = Name the capitals, explore = Free tap
  const isFind = () => S.mode === "find" || S.mode === "findcap";
  const isName = () => S.mode === "name" || S.mode === "namecap";
  const caps = () => S.mode === "findcap" || S.mode === "namecap";
  const capital = c => c.capitals[0] || "";
  const label = c => (caps() ? `${c.name}: ${capital(c)}` : c.name);
  let selected = null;   // naming games: the country whose name or capital is being typed
  const getState = c => (flashing[c.iso] ? "flash" : c === selected ? "sel" : state[c.iso] || null);
  // still to answer (Free tap, or a finished naming game: any country in the region); taps near small
  // open countries snap to them
  // once a game is finished every country in the region is open again, for reviewing the answers
  const isOpen = c => inRegion(c) && (S.mode === "explore" || finished || !state[c.iso]);

  // `order` holds the countries still to answer. Find the country: the arrows move through it with no penalty.
  let order = [], idx = 0, target = null, nGood = 0, nBad = 0, finished = false, gaveUp = false, total = 0;
  let startTime = 0, endTime = 0;

  function newGame() {
    Object.keys(state).forEach(k => delete state[k]);
    const list = regionCountries();
    total = list.length;
    order = d3.shuffle(list); idx = 0; nGood = nBad = 0; finished = gaveUp = false; selected = null;
    startTime = Date.now();
    closeResults();
    show();
  }
  function next() {
    order.splice(idx, 1);
    if (idx >= order.length) idx = 0;
    if (!order.length) { finish(); return; }
    show();
  }
  function step(d) {
    if (!isFind() || order.length < 2) return;
    idx = (idx + d + order.length) % order.length;
    show();
  }
  function show() {
    const mode = S.mode, where = S.region === "world" ? "" : " · " + REGIONS[S.region].name;
    target = isFind() && !finished ? order[idx] || null : null;
    const t = $("target"); t.className = "target";
    const typing = isName() && selected && !finished;
    $("prev").hidden = $("fwd").hidden = !isFind() || finished;
    $("nameInput").placeholder = caps() ? `Capital of ${selected ? selected.name : ""}` : "Type the name";
    $("giveup").hidden = mode === "explore";
    $("nameInput").hidden = $("nameClose").hidden = !typing;
    t.hidden = typing;
    resetGiveUp();
    if (mode === "explore") {
      $("eyebrow").textContent = "Learning mode" + where;
      t.textContent = "Tap any country";
      $("score").textContent = "Tap any country to learn about it.";
    } else if (isName()) {
      $("eyebrow").textContent = (finished ? "Finished" : caps() ? "Name the capitals" : "Name the countries") + where;
      if (finished) {
        t.textContent = `${nGood} of ${total} named`;
        $("score").textContent = `Tap any country to see its ${caps() ? "capital" : "name"}.`;
        $("giveup").textContent = "Play again";
      } else {
        if (!typing) t.textContent = "Tap a country";
        $("score").innerHTML = `<b>${nGood}</b> / ${total} named`;
      }
    } else if (finished) {
      $("eyebrow").textContent = "Finished" + where;
      t.textContent = `${nGood} of ${total} right`;
      $("score").innerHTML = `<b>${nGood}</b> right · <b>${nBad}</b> missed · tap any country to see it`;
      $("giveup").textContent = "Play again";
    } else {
      $("eyebrow").textContent = (caps() ? "Find by capital" : "Find") + where;
      t.textContent = caps() ? capital(target) : target.name;
      $("score").innerHTML = `<b>${nGood}</b> right · <b>${nBad}</b> missed · ${order.length} to go`;
    }
    redraw();
  }
  function redraw() { main.requestDraw(); if (inset) inset.requestDraw(); }
  function flashName(c) {
    Object.keys(state).forEach(k => { if (state[k] === "flash") delete state[k]; });
    $("target").hidden = false; $("target").textContent = label(c);
  }

  function tap(c, view) {
    if (!inRegion(c)) return; // countries outside the region are greyed out and do nothing
    if (S.mode === "explore") { flashName(c); state[c.iso] = "flash"; showLearnCard(c); redraw(); return; }
    if (finished) { flashName(c); return; } // reviewing: tap any country to see its name (or capital)
    if (isName()) { tapName(c, view); return; }
    if (!target || state[c.iso] === "good") return; // already-correct countries do nothing
    // the next country appears instantly; the map keeps the green/red result
    GG.Stats.answer(S.mode, target.iso, c === target);
    if (c === target) { state[c.iso] = "good"; nGood++; }
    else {
      state[target.iso] = "bad"; nBad++;
      flashing[c.iso] = true; // the tapped country flashes yellow once
      setTimeout(() => { delete flashing[c.iso]; redraw(); }, 450);
      toast(caps() ? `Missed: ${capital(target)} is in ${target.name}` : "Missed: " + target.name, caps() ? 2400 : 1800);
    }
    if (inset && view === inset) closeInset();
    next();
  }

  // ---------- game 2: Name the countries ----------
  // Tap any country, type its name; it goes green as soon as the name is right. No submit, no wrong answers.
  function tapName(c, view) {
    if (state[c.iso] === "good") return;          // already named
    selected = c;                                 // switching countries clears what was typed
    $("nameInput").value = "";
    if (inset && view === inset) closeInset();
    show();
    $("nameInput").focus();
    setTimeout(keepSelectedInView, 400);          // after the keyboard has opened and the map has resized
  }
  function keepSelectedInView() {
    if (!selected || !main.visible(selected.anchor)) return;
    const p = main.projection()(selected.anchor);
    if (p[0] < 20 || p[0] > main.w - 20 || p[1] < 20 || p[1] > main.h - 20) {
      main.lookAt(selected.anchor[0], selected.anchor[1], Math.min(main.w, main.h) * 0.9 / main.pxPerDeg());
    }
  }
  $("nameInput").addEventListener("input", () => {
    const typed = $("nameInput").value, match = selected && GG.nameMatches(selected, typed, caps() ? "capitals" : "names");
    if (!match) return; // no reaction until it's right
    // accepted with a typo: show how it was typed and how it's spelled
    if (!match.exact) toast(`You typed “${typed.trim()}” — it's spelled “${match.name}”`, 4000);
    state[selected.iso] = "good"; nGood++;
    order = order.filter(c => c !== selected);
    selected = null;
    $("nameInput").value = ""; $("nameInput").blur();
    if (!order.length) { finish(); return; }
    show();
  });
  $("nameInput").addEventListener("keydown", e => { if (e.key === "Escape") closeName(); });
  function closeName() { selected = null; $("nameInput").blur(); show(); }
  $("nameClose").onclick = closeName;
  window.addEventListener("resize", () => setTimeout(keepSelectedInView, 50));

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
    order = []; gaveUp = true; selected = null; $("nameInput").blur();
    finish();
  };

  // ---------- Learning mode card ----------
  const esc = s => String(s).replace(/[&<>"]/g, ch => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[ch]));
  const num = n => n.toLocaleString("en-GB");
  function fmtPop(n, year) {
    if (!n) return "";
    const s = n >= 1e9 ? `${(n / 1e9).toFixed(2)} billion` : n >= 1e6 ? `${(n / 1e6).toFixed(n >= 1e7 ? 1 : 2)} million` : n >= 1e4 ? num(Math.round(n / 1000) * 1000) : `about ${num(n)}`;
    return year ? `${s} (${year})` : s;
  }
  const facts = rows => rows.filter(r => r[1]).map(([k, v]) => `<dt>${esc(k)}</dt><dd>${esc(v)}</dd>`).join("");
  let learnMore = false;
  function showLearnCard(c) {
    const i = c.info || {};
    // (the single-page test build carries the flags inside the page, in window.GG_FLAGS)
    $("lcFlag").src = (window.GG_FLAGS && window.GG_FLAGS[c.iso]) || `data/flags/${c.iso}.svg`;
    $("lcFlag").alt = `Flag of ${c.name}`;
    $("lcName").textContent = c.name;
    $("lcSub").textContent = [c.cont.join(" and "), i.sub, ...(i.areas || [])].filter(Boolean)
      .filter((v, n, a) => a.indexOf(v) === n).join(" · ");
    $("lcMain").innerHTML = facts([
      [c.capitalNote ? "Capitals" : "Capital", c.capitalNote || c.capitals[0] || "None"],
      ["Population", fmtPop(i.pop, i.popYear)],
    ]);
    const group = (title, rows) => { const h = facts(rows); return h ? `<h4>${title}</h4><dl class="lcfacts">${h}</dl>` : ""; };
    $("lcMore").innerHTML =
      group("People", [
        [i.langs && i.langs.length > 1 ? "Languages" : "Language", (i.langs || []).join(", ")],
        ["People are called", i.demonym],
        ["Largest city", i.city],
        ["Currency", i.currency],
      ]) +
      group("Land", [
        ["Area", i.area ? `${num(Math.round(i.area))} km² (#${i.areaRank} of 197)` : ""],
        ["Coast", i.coast || "Landlocked"],
        ["Highest point", i.high],
        [/ to /.test(i.tz || "") ? "Time zones" : "Time zone", i.tz],
        ["Drives on the", i.drive && i.drive.toLowerCase()],
      ]) +
      group("History and status", [
        ["Formerly", i.former],
        ["Independence", i.ind],
        ["Government", i.gov],
        ["Recognition", i.rec],
        ["Income level", [i.income, i.gdppc ? `$${num(i.gdppc)} per person (${i.gdpYear})` : ""].filter(Boolean).join(", ")],
      ]);
    setLearnMore(learnMore);
    $("learnCard").hidden = false;
  }
  function setLearnMore(on) {
    learnMore = on;
    $("lcMore").hidden = !on;
    $("lcMoreBtn").textContent = on ? "Fewer facts" : "More facts";
    $("lcMoreBtn").setAttribute("aria-expanded", on);
    $("learnCard").classList.toggle("expanded", on);
  }
  $("lcMoreBtn").onclick = () => setLearnMore(!learnMore);
  function hideLearnCard() { $("learnCard").hidden = true; }
  $("lcClose").onclick = () => { hideLearnCard(); Object.keys(state).forEach(k => delete state[k]); redraw(); };

  // ---------- stats page ----------
  const MODE_NAMES = { find: "Find countries", name: "Name countries", findcap: "Find by capital", namecap: "Name capitals" };
  let statsSkill = "country";
  const fmtTime = s => `${Math.floor(s / 60)}:${String(s % 60).padStart(2, "0")}`;
  function openStats() { renderStats(); $("stats").hidden = false; }
  function closeStats() { $("stats").hidden = true; resetStatsReset(); }
  function renderStats() {
    const skill = statsSkill, St = GG.Stats;
    document.querySelectorAll("#statsSkill button").forEach(b => b.classList.toggle("on", b.dataset.v === skill));
    const acc = c => { const e = St.entry(skill, c.iso); return e && e.a ? e.c / e.a : null; };
    const known = c => { const a = acc(c); return a !== null && a >= 0.75; };
    // regions
    const rows = Object.entries(REGIONS).map(([key, r]) => {
      const cs = key === "world" ? geo.countries : geo.countries.filter(r.test);
      const k = cs.filter(known).length, seen = cs.filter(c => acc(c) !== null).length, pct = Math.round(100 * k / cs.length);
      return `<div class="srow"><div class="sname">${r.name}</div><div class="sbar"><i style="width:${pct}%"></i></div>` +
        `<div class="snum">${k}/${cs.length}</div><div class="ssub">${seen} seen</div></div>`;
    }).join("");
    $("statsRegions").innerHTML = rows;
    // weakest
    const weak = geo.countries.filter(c => acc(c) !== null && acc(c) < 1)
      .sort((a, b) => acc(a) - acc(b) || St.entry(skill, b.iso).a - St.entry(skill, a.iso).a).slice(0, 15);
    $("statsWeak").innerHTML = weak.length ? weak.map(c => {
      const e = St.entry(skill, c.iso);
      const what = skill === "capital" ? `${c.name} <small>${c.capitals[0]}</small>` : c.name;
      return `<li><span>${what}</span><span class="snum">${e.c} of ${e.a} right</span></li>`;
    }).join("") : `<li class="empty">Nothing yet. Play a ${skill === "capital" ? "capitals" : "countries"} game and your weakest ones will show here.</li>`;
    // bests (for this skill's games)
    const modes = skill === "capital" ? ["findcap", "namecap"] : ["find", "name"];
    const bests = Object.entries(St.bests()).filter(([k]) => modes.includes(k.split("|")[0]))
      .map(([k, v]) => { const [m, rg] = k.split("|"); return `<li><span>${MODE_NAMES[m]} · ${REGIONS[rg] ? REGIONS[rg].name : rg}</span><span class="snum">${v.pct}% · ${fmtTime(v.secs)}</span></li>`; });
    $("statsBests").innerHTML = bests.length ? bests.join("") : `<li class="empty">No games finished yet.</li>`;
    // recent games
    const games = St.games().filter(g => modes.includes(g.mode)).slice(0, 8);
    $("statsGames").innerHTML = games.length ? games.map(g => {
      const d = new Date(g.date), day = d.toLocaleDateString(undefined, { day: "numeric", month: "short" });
      return `<li><span>${MODE_NAMES[g.mode]} · ${REGIONS[g.region] ? REGIONS[g.region].name : g.region}${g.gaveUp ? " <small>gave up</small>" : ""}</span>` +
        `<span class="snum">${g.score}/${g.total} · ${day}</span></li>`;
    }).join("") : `<li class="empty">No games yet.</li>`;
  }
  $("statsBtn").onclick = openStats;
  $("statsClose").onclick = closeStats;
  $("stats").addEventListener("click", e => { if (e.target === $("stats")) closeStats(); });
  $("statsSkill").addEventListener("click", e => { const b = e.target.closest("button"); if (b) { statsSkill = b.dataset.v; renderStats(); } });
  let statsResetTimer;
  function resetStatsReset() { clearTimeout(statsResetTimer); $("statsReset").textContent = "Reset all stats"; $("statsReset").classList.remove("confirm"); }
  $("statsReset").onclick = () => {
    const b = $("statsReset");
    if (!b.classList.contains("confirm")) {
      b.classList.add("confirm"); b.textContent = "Tap again to delete all stats";
      statsResetTimer = setTimeout(resetStatsReset, 3000); return;
    }
    GG.Stats.reset(); resetStatsReset(); renderStats();
  };

  // ---------- end of a game: results pop-up ----------
  let newBest = false;
  function finish() {
    finished = true; endTime = Date.now();
    // naming games: record every country in the region once, named or not
    if (isName()) regionCountries().forEach(c => GG.Stats.answer(S.mode, c.iso, state[c.iso] === "good"));
    newBest = GG.Stats.game(S.mode, S.region, nGood, total, Math.round((endTime - startTime) / 1000), gaveUp);
    show();
    openResults();
  }
  function openResults() {
    const secs = Math.round((endTime - startTime) / 1000), time = `${Math.floor(secs / 60)}:${String(secs % 60).padStart(2, "0")}`;
    const pct = Math.round(100 * nGood / Math.max(1, total));
    const named = isName();
    $("resultsTitle").textContent = gaveUp ? "Game over" : pct === 100 ? "Perfect!" : "Finished!";
    $("resultsScore").textContent = `${nGood} / ${total}`;
    $("resultsWhat").textContent = named ? (caps() ? "capitals named" : "countries named") : "right first time";
    const missed = total - nGood;
    $("resultsDetail").textContent = `${pct}% · ${missed} ${named ? "not named" : "missed"} · ${time}`;
    $("resultsBest").hidden = !newBest;
    $("results").hidden = false;
  }
  function closeResults() { $("results").hidden = true; }
  $("reviewBtn").onclick = () => { closeResults(); toast("Tap any country to see its answer.", 2500); };
  $("replayBtn").onclick = () => { closeResults(); newGame(); };
  $("listBtn").onclick = () => { closeResults(); openSetup(); };
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
  // open the game group that holds the chosen game, close the others
  function showGameGroup(mode) {
    document.querySelectorAll("#segGame details").forEach(d => { d.open = !!d.querySelector(`button[data-v="${mode}"]`); });
  }
  document.querySelectorAll("#segGame details").forEach(d => d.addEventListener("toggle", () => {
    if (d.open) document.querySelectorAll("#segGame details").forEach(o => { if (o !== d) o.open = false; });
  }));
  function openSetup() {
    pick.mode = S.mode; pick.region = S.region; pick.view = S.region === "world" ? main.mode : "globe";
    segSelect($("segGame"), pick.mode); segSelect($("regions"), pick.region); segSelect($("segView"), pick.view);
    showGameGroup(pick.mode);
    $("viewField").hidden = pick.region !== "world";
    $("setup").hidden = false;
  }
  function closeSetup() { $("setup").hidden = true; }
  $("menuBtn").onclick = openSetup;
  $("setupClose").onclick = closeSetup;
  $("setup").addEventListener("click", e => { if (e.target === $("setup")) closeSetup(); });
  $("segGame").addEventListener("click", e => { const b = e.target.closest("button"); if (b && !b.disabled) { pick.mode = b.dataset.v; segSelect($("segGame"), pick.mode); } });
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
    hideLearnCard();
    if (mode === "explore") { Object.keys(state).forEach(k => delete state[k]); selected = null; show(); } else newGame();
  }

  document.addEventListener("keydown", e => {
    if (e.key === "Escape") { closeSetup(); closeInset(); closeResults(); closeStats(); }
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
