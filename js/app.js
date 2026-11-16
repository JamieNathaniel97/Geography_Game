// Game logic and screen wiring. Build 1: game 1 (Find the country) for the whole world, one continent
// or the Caribbean, plus Free tap. Game modes and regions are kept separate so more can be added (PLAN.md).
(function () {
  const GG = window.GG;
  const $ = id => document.getElementById(id);

  // data: "world" (countries) or "us" (US states, build 3)
  const S = { mode: "find", region: "world", magnify: false, data: "world" };
  let geoWorld = null, geoUS = null;
  const noun = () => (S.data === "us" ? "state" : "country");
  const nouns = () => (S.data === "us" ? "states" : "countries");

  // Remembered between visits, on this phone: map toggles and the last game's settings.
  const PREFS_KEY = "gg.prefs.v1";
  let prefs = {};
  try { prefs = JSON.parse(localStorage.getItem(PREFS_KEY)) || {}; } catch (e) { prefs = {}; }
  function savePrefs(changes) {
    Object.assign(prefs, changes);
    try { localStorage.setItem(PREFS_KEY, JSON.stringify(prefs)); } catch (e) { /* storage blocked: just don't remember */ }
  }
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
    usa:      { name: "United States", us: true, test: () => true }, // the whole US map (US states games)
    oceania:  { name: "Oceania",       test: c => c.cont.includes("Oceania"),       view: { globe: [167, -16, 74.3],   flat: [167, -16, 74.3] },   crop: [[110, -50], [212, 22]] },
  };
  const inRegion = c => (S.region === "world" || REGIONS[S.region].test(c)) && !(tlYear < 1959 && c.info && c.info.year > tlYear);
  const regionCountries = () => geo.countries.filter(inRegion);

  // Games: find = Find the country, name = Name the countries, findcap = Find the country by its capital,
  // namecap = Name the capitals, explore = Free tap
  const isFind = () => S.mode === "find" || S.mode === "findcap" || S.mode === "findflag";
  const isName = () => S.mode === "name" || S.mode === "namecap" || S.mode === "nameflag";
  const caps = () => S.mode === "findcap" || S.mode === "namecap";
  const flags = () => S.mode === "findflag" || S.mode === "nameflag";
  // flag image (the single-page test build carries the flags inside the page, in window.GG_FLAGS)
  const flagSrc = c => {
    const key = (geoUS && geoUS.byIso[c.iso] === c ? "us/" : "") + c.iso; // a state (also shown on the world Learning map)
    return (window.GG_FLAGS && window.GG_FLAGS[key]) || `data/flags/${key}.webp`;
  };
  const capital = c => c.capitals[0] || "";
  const label = c => (caps() ? `${c.name}: ${capital(c)}` : c.name);
  let selected = null;   // naming games: the country whose name or capital is being typed
  // statehood timeline (US Learning mode): the year shown; states that join that year are highlighted
  let tlYear = 1959, tlTimer = null;
  const getState = c => (flashing[c.iso] ? "flash" : c === selected ? "sel" : state[c.iso] ||
    (tlYear < 1959 && c.info && c.info.year === tlYear ? "sel" : null));
  // still to answer (Free tap, or a finished naming game: any country in the region); taps near small
  // open countries snap to them
  // once a game is finished every country in the region is open again, for reviewing the answers
  // capitals games: show a capital's dot once its country or state has been answered (right, wrong, or given up)
  const showCapital = c => caps() && (state[c.iso] === "good" || state[c.iso] === "bad");
  const isOpen = c => inRegion(c) && (S.mode === "explore" || finished || !state[c.iso]);

  // `order` holds the countries still to answer. Find the country: the arrows move through it with no penalty.
  let order = [], idx = 0, target = null, nGood = 0, nBad = 0, finished = false, gaveUp = false, total = 0;
  let startTime = 0, endTime = 0;

  function newGame() {
    Object.keys(state).forEach(k => delete state[k]);
    let list = regionCountries();
    if (S.weak && isFind()) list = weakest(list, WEAK_COUNT);
    total = list.length;
    order = d3.shuffle(list); idx = 0; nGood = nBad = 0; finished = gaveUp = false; selected = null;
    if (S.mode === "nameflag") buildFlagGrid(); else hideFlagGrid();
    startTime = Date.now();
    startClock();
    closeResults();
    show();
  }

  // ---------- knowledge gaps ("weak spots" in PLAN.md): the countries most worth practising ----------
  // Each country gets a score: how often it's been wrong (smoothed, so one miss isn't everything), raised the
  // longer it's been since you last saw it (simple spaced repetition). Never-asked countries sit in the middle,
  // above ones you already know well.
  const WEAK_COUNT = 20;
  function weakness(c) {
    const e = GG.Stats.entry(GG.Stats.skillOf(S.mode), c.iso);
    if (!e || !e.a) return 0.45;
    const wrong = (e.a - e.c + 1) / (e.a + 2);
    const days = (Date.now() - e.t) / 864e5;
    return wrong * (1 + Math.min(days / 7, 2));
  }
  function weakest(list, n) {
    return list.map(c => ({ c, w: weakness(c) + Math.random() * 0.02 })).sort((a, b) => b.w - a.w).slice(0, n).map(x => x.c);
  }

  // ---------- timer: elapsed time, or an optional countdown ----------
  let clockTimer = null, timeLimit = 0;
  function startClock() {
    clearInterval(clockTimer);
    timeLimit = S.timer && S.mode !== "explore" ? total * (isName() ? S.paceName || 10 : S.paceFind || 5) : 0;
    tickClock();
    clockTimer = setInterval(tickClock, 250);
  }
  function tickClock() {
    const el = $("clock");
    if (S.mode === "explore" || !startTime) { el.hidden = true; return; }
    const secs = Math.floor(((finished ? endTime : Date.now()) - startTime) / 1000);
    const shown = timeLimit ? Math.max(0, timeLimit - secs) : secs;
    el.hidden = false;
    el.textContent = `${Math.floor(shown / 60)}:${String(shown % 60).padStart(2, "0")}`;
    el.classList.toggle("low", !!timeLimit && shown <= 10 && !finished);
    if (timeLimit && !finished && shown <= 0) timeUp();
  }
  function timeUp() {
    order.forEach(c => { if (!state[c.iso]) { state[c.iso] = "bad"; nBad++; } });
    order = []; gaveUp = "time"; selected = null; $("nameInput").blur();
    finish();
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
    const typing = isName() && !flags() && selected && !finished;
    // Find by flag shows the flag instead of a name
    $("targetFlag").hidden = !(S.mode === "findflag" && target);
    if (S.mode === "findflag" && target) { $("targetFlag").src = flagSrc(target); $("targetFlag").alt = `Which ${noun()} has this flag?`; }
    $("prev").hidden = $("fwd").hidden = !isFind() || finished;
    $("nameInput").placeholder = caps() ? `Capital of ${selected ? selected.name : ""}` : "Type the name";
    $("giveup").hidden = mode === "explore";
    $("nameInput").hidden = $("nameClose").hidden = !typing;
    t.hidden = typing;
    resetGiveUp();
    if (mode === "explore") {
      $("eyebrow").textContent = "Learning mode" + where;
      t.textContent = `Tap any ${noun()}`;
      $("score").textContent = `Tap any ${noun()} to learn about it.`;
    } else if (isName()) {
      $("eyebrow").textContent = (finished ? "Finished" : flags() ? "Name the flags" : caps() ? "Name the capitals" : `Name the ${nouns()}`) + where;
      if (finished) {
        t.textContent = `${nGood} of ${total} named`;
        $("score").textContent = flags() ? "Missed flags are shown in red." : `Tap any ${noun()} to see its ${caps() ? "capital" : "name"}.`;
        $("giveup").textContent = "Play again";
      } else {
        if (!typing) t.textContent = flags() ? `Type each flag's ${noun()}` : `Tap a ${noun()}`;
        $("score").innerHTML = `<b>${nGood}</b> / ${total} named`;
      }
    } else if (finished) {
      $("eyebrow").textContent = "Finished" + where;
      t.textContent = `${nGood} of ${total} right`;
      $("score").innerHTML = `<b>${nGood}</b> / ${total} <span class="wrong">· ${nBad} wrong</span> · tap any ${noun()} to see it`;
      $("giveup").textContent = "Play again";
    } else {
      $("eyebrow").textContent = (S.mode === "findflag" ? "Find by flag" : caps() ? "Find by capital" : "Find") + where + (S.weak ? " · knowledge gaps" : "");
      t.textContent = S.mode === "findflag" ? "" : caps() ? capital(target) : target.name;
      $("score").innerHTML = `<b>${nGood}</b> / ${total} <span class="wrong">· ${nBad} wrong</span>`;
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
    if (S.mode === "explore") {
      // world Learning map zoomed into the US: a tap on a state shows the state
      const f = c.iso === "USA" && view.sub && view.lastTap ? view.subAt(view.lastTap[0], view.lastTap[1]) : null;
      selectSub(f);
      flashName(f ? f.c : c);
      if (!f) state[c.iso] = "flash";
      showLearnCard(f ? f.c : c); redraw(); return;
    }
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
      toast(S.mode === "findflag" ? `Missed: that was the flag of ${target.name}` : caps() ? `Missed: ${capital(target)} is in ${target.name}` : "Missed: " + target.name,
        caps() || S.mode === "findflag" ? 2400 : 1800);
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
    if (geoUS && geoUS.byIso[c.iso] === c) { showStateCard(c, i); return; }
    // (the single-page test build carries the flags inside the page, in window.GG_FLAGS)
    $("lcFlag").src = flagSrc(c);
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
  // US states: flag, region and abbreviation, capital, population; More facts in groups, like the country card
  const factGroup = (title, rows) => { const h = facts(rows); return h ? `<h4>${title}</h4><dl class="lcfacts">${h}</dl>` : ""; };
  function showStateCard(c, i) {
    $("lcFlag").src = flagSrc(c); $("lcFlag").alt = `Flag of ${c.name}`;
    $("lcName").textContent = c.name;
    $("lcSub").textContent = `${i.region} · ${i.abbr}`;
    $("lcMain").innerHTML = facts([["Capital", c.capitals[0]], ["Population", fmtPop(i.pop, i.popYear)]]);
    const ord = n => n + (n % 10 === 1 && n !== 11 ? "st" : n % 10 === 2 && n !== 12 ? "nd" : n % 10 === 3 && n !== 13 ? "rd" : "th");
    const hi = i.high;
    $("lcMore").innerHTML =
      factGroup("People", [
        ["Largest city", i.city || `${c.capitals[0]} (the capital)`],
        ["Nickname", i.nickname],
      ]) +
      factGroup("Land", [
        ["Area", i.areaSqMi ? `${num(Math.round(i.areaSqMi * 2.589988))} km² (${num(i.areaSqMi)} sq mi), #${i.areaRank} of 50` : ""],
        ["Highest point", hi ? `${hi[0]}, ${num(hi[2])} m (${num(hi[1])} ft)` : ""],
        [/;/.test(i.tz || "") ? "Time zones" : "Time zone", i.tz],
      ]) +
      factGroup("History", [
        ["Joined the Union", `${i.year} (the ${ord(i.order)} state)`],
        ["Name comes from", i.origin],
      ]) +
      factGroup("State symbols", [
        ["Bird", i.bird],
        ["Flower", i.flower],
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
  $("lcClose").onclick = () => { hideLearnCard(); selectSub(null); Object.keys(state).forEach(k => delete state[k]); redraw(); };
  // US states on the world Learning map (loaded the first time they're needed)
  function useSub(on) {
    if (!on) { main.setSub(null); return; }
    const set = () => { if (S.mode === "explore" && S.data === "world") main.setSub({ features: geoUS.f50.filter(f => f.c), borders: geoUS.borders50, selected: null }); };
    if (geoUS) set(); else GG.loadUS().then(g => { geoUS = geoUS || g; set(); }).catch(() => {});
  }
  function selectSub(f) { if (main.sub) { main.sub.selected = f; main.requestDraw(); } }

  // ---------- statehood timeline (US Learning mode) ----------
  // Drag through 1787 to 1959: states not yet in the Union are grey, the ones joining that year are highlighted.
  // Play steps through each year a state joined.
  function setTimeline(year) {
    tlYear = year;
    $("tlRange").value = year;
    const states = geo.countries.filter(c => c.info && c.info.year <= year);
    const joined = states.filter(c => c.info.year === year).sort((a, b) => a.info.order - b.info.order);
    const n = states.length;
    const note = joined.length ? `${joined.map(c => c.name).join(", ")} joined` : "";
    $("tlLabel").innerHTML = `<b>${year}</b> ${n === 50 ? "All 50 states" : `${n} state${n === 1 ? "" : "s"}`}${note ? " · " + esc(note) : ""}`;
    redraw();
  }
  function stopTimeline() { clearInterval(tlTimer); tlTimer = null; $("tlPlay").textContent = "▶"; $("tlPlay").setAttribute("aria-label", "Play the timeline"); }
  function showTimeline(on) {
    stopTimeline();
    $("timeline").hidden = !on;
    $("mapwrap").classList.toggle("hastl", on);
    tlYear = 1959;
    if (on) setTimeline(1959);
  }
  $("tlRange").addEventListener("input", e => { stopTimeline(); setTimeline(+e.target.value); });
  $("tlPlay").onclick = () => {
    if (tlTimer) { stopTimeline(); return; }
    const years = [...new Set(geo.countries.map(c => c.info.year))].sort((a, b) => a - b);
    let i = tlYear >= 1959 ? 0 : years.findIndex(y => y > tlYear);
    if (i < 0) i = 0;
    setTimeline(years[i]);
    $("tlPlay").textContent = "❚❚"; $("tlPlay").setAttribute("aria-label", "Pause the timeline");
    tlTimer = setInterval(() => {
      i++;
      if (i >= years.length) { stopTimeline(); return; }
      setTimeline(years[i]);
      if (i === years.length - 1) stopTimeline();
    }, 700);
  };

  // ---------- stats page ----------
  const MODE_NAMES = { find: "Find countries", name: "Name countries", findcap: "Find by capital", namecap: "Name capitals",
    findflag: "Find by flag", nameflag: "Name the flags" };
  const modeName = (m, region) => region === "usa" ? MODE_NAMES[m].replace("countries", "states") : MODE_NAMES[m];
  let statsSkill = "country", statsData = "world";
  const fmtTime = s => `${Math.floor(s / 60)}:${String(s % 60).padStart(2, "0")}`;
  function openStats() { statsData = S.data; renderStats(); $("stats").hidden = false; }
  function closeStats() { $("stats").hidden = true; resetStatsReset(); }
  function renderStats() {
    const skill = statsSkill, St = GG.Stats, us = statsData === "us";
    document.querySelectorAll("#statsSkill button").forEach(b => b.classList.toggle("on", b.dataset.v === skill));
    document.querySelectorAll("#statsData button").forEach(b => b.classList.toggle("on", b.dataset.v === statsData));
    $("statsSkill").querySelector('[data-v="country"]').textContent = us ? "States" : "Countries";
    if (us && !geoUS) { GG.loadUS().then(g => { geoUS = geoUS || g; renderStats(); }); return; }
    const g = us ? geoUS : geoWorld;
    const acc = c => { const e = St.entry(skill, c.iso); return e && e.a ? e.c / e.a : null; };
    const known = c => { const a = acc(c); return a !== null && a >= 0.75; };
    // regions
    const rows = Object.entries(REGIONS).filter(([, r]) => !!r.us === us).map(([key, r]) => {
      const cs = key === "world" ? g.countries : g.countries.filter(r.test);
      const k = cs.filter(known).length, seen = cs.filter(c => acc(c) !== null).length, pct = Math.round(100 * k / cs.length);
      return `<div class="srow"><div class="sname">${r.name}</div><div class="sbar"><i style="width:${pct}%"></i></div>` +
        `<div class="snum">${k}/${cs.length}</div><div class="ssub">${seen} seen</div></div>`;
    }).join("");
    $("statsRegions").innerHTML = rows;
    // weakest
    const weak = g.countries.filter(c => acc(c) !== null && acc(c) < 1)
      .sort((a, b) => acc(a) - acc(b) || St.entry(skill, b.iso).a - St.entry(skill, a.iso).a).slice(0, 15);
    $("statsWeak").innerHTML = weak.length ? weak.map(c => {
      const e = St.entry(skill, c.iso);
      const what = skill === "capital" ? `${c.name} <small>${c.capitals[0]}</small>` : c.name;
      return `<li><span>${what}</span><span class="snum">${e.c} of ${e.a} right</span></li>`;
    }).join("") : `<li class="empty">Nothing yet. Play a ${skill === "capital" ? "capitals" : skill === "flag" ? "flags" : us ? "states" : "countries"} game and your weakest ones will show here.</li>`;
    // bests (for this skill's games)
    const modes = skill === "capital" ? ["findcap", "namecap"] : skill === "flag" ? ["findflag", "nameflag"] : ["find", "name"];
    const bests = Object.entries(St.bests()).filter(([k]) => modes.includes(k.split("|")[0]) && (k.split("|")[1] === "usa") === us)
      .map(([k, v]) => { const [m, rg] = k.split("|"); return `<li><span>${modeName(m, rg)} · ${REGIONS[rg] ? REGIONS[rg].name : rg}</span><span class="snum">${v.pct}% · ${fmtTime(v.secs)}</span></li>`; });
    $("statsBests").innerHTML = bests.length ? bests.join("") : `<li class="empty">No games finished yet.</li>`;
    // recent games
    const games = St.games().filter(gm => modes.includes(gm.mode) && (gm.region === "usa") === us).slice(0, 8);
    $("statsGames").innerHTML = games.length ? games.map(g => { // (g here is one game)
      const d = new Date(g.date), day = d.toLocaleDateString(undefined, { day: "numeric", month: "short" });
      return `<li><span>${modeName(g.mode, g.region)} · ${REGIONS[g.region] ? REGIONS[g.region].name : g.region}${g.weak ? " <small>knowledge gaps</small>" : ""}${g.gaveUp ? " <small>gave up</small>" : ""}</span>` +
        `<span class="snum">${g.score}/${g.total} · ${day}</span></li>`;
    }).join("") : `<li class="empty">No games yet.</li>`;
  }
  $("statsBtn").onclick = openStats;
  $("statsClose").onclick = closeStats;
  $("stats").addEventListener("click", e => { if (e.target === $("stats")) closeStats(); });
  $("statsSkill").addEventListener("click", e => { const b = e.target.closest("button"); if (b) { statsSkill = b.dataset.v; renderStats(); } });
  $("statsData").addEventListener("click", e => { const b = e.target.closest("button"); if (b) { statsData = b.dataset.v; renderStats(); } });
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

  // ---------- game 6: Name the flags (a grid of flags, no map) ----------
  // Type the country under each flag; it goes green as soon as the name is right and the cursor moves on to
  // the next unanswered flag. Answer in any order. Same forgiving matching as the other naming games.
  function buildFlagGrid() {
    const grid = $("flagGrid");
    grid.innerHTML = "";
    order.forEach(c => {
      const card = document.createElement("div");
      card.className = "fcard"; card.dataset.iso = c.iso;
      card.innerHTML = `<img src="${flagSrc(c)}" alt="A flag" loading="lazy"><input type="text" autocomplete="off" autocorrect="off" ` +
        `autocapitalize="off" spellcheck="false" enterkeyhint="next" aria-label="${S.data === "us" ? "State" : "Country"} with this flag" placeholder="${(prefs.perRow || 4) >= 6 ? "…" : S.data === "us" ? "State" : "Country"}">`;
      grid.appendChild(card);
    });
    $("flagPanel").hidden = false;
    $("flagPanel").scrollTop = 0;
  }
  $("flagGrid").addEventListener("click", e => {
    const img = e.target.closest(".fcard img"); if (!img) return;
    const input = img.closest(".fcard").querySelector("input");
    if (input) input.focus();
  });
  // flags per row (3-7), remembered between visits
  function setPerRow(n) {
    $("flagGrid").style.setProperty("--per-row", n);
    $("flagGrid").classList.toggle("dense", n >= 6);
    $("flagGrid").querySelectorAll("input").forEach(i => { i.placeholder = n >= 6 ? "…" : S.data === "us" ? "State" : "Country"; });
    $("segPerRow").querySelectorAll("button").forEach(b => b.classList.toggle("on", +b.dataset.v === n));
  }
  setPerRow(prefs.perRow || 4);
  $("segPerRow").addEventListener("click", e => {
    const b = e.target.closest("button"); if (!b) return;
    setPerRow(+b.dataset.v); savePrefs({ perRow: +b.dataset.v });
  });
  function hideFlagGrid() { $("flagPanel").hidden = true; $("flagGrid").innerHTML = ""; }
  $("flagGrid").addEventListener("input", e => {
    const input = e.target, card = input.closest(".fcard"); if (!card || finished) return;
    const c = geo.byIso[card.dataset.iso], typed = input.value, match = GG.nameMatches(c, typed, "names");
    if (!match) return; // no reaction until it's right
    if (!match.exact) toast(`You typed \u201c${typed.trim()}\u201d \u2014 it's spelled \u201c${match.name}\u201d`, 4000);
    state[c.iso] = "good"; nGood++;
    order = order.filter(x => x !== c);
    card.classList.add("good");
    input.replaceWith(Object.assign(document.createElement("div"), { className: "fname", textContent: c.name }));
    if (!order.length) { finish(); return; }
    // move on to the next unanswered flag after this one (wrapping round)
    const cards = [...$("flagGrid").children], i = cards.indexOf(card);
    const nextCard = cards.slice(i + 1).concat(cards.slice(0, i)).find(k => !k.classList.contains("good"));
    const nextInput = nextCard && nextCard.querySelector("input");
    if (nextInput) { nextInput.focus({ preventScroll: true }); nextCard.scrollIntoView({ block: "nearest", behavior: "smooth" }); }
    show();
  });
  function revealFlagGrid() { // after giving up: missed names in red
    [...$("flagGrid").children].forEach(card => {
      if (card.classList.contains("good")) return;
      card.classList.add("bad");
      const input = card.querySelector("input");
      if (input) input.replaceWith(Object.assign(document.createElement("div"), { className: "fname", textContent: geo.byIso[card.dataset.iso].name }));
    });
  }

  // ---------- end of a game: results pop-up ----------
  let newBest = false;
  function finish() {
    finished = true; endTime = Date.now();
    if (S.mode === "nameflag") { revealFlagGrid(); document.activeElement && document.activeElement.blur(); }
    // naming games: record every country in the region once, named or not
    if (isName()) regionCountries().forEach(c => GG.Stats.answer(S.mode, c.iso, state[c.iso] === "good"));
    newBest = GG.Stats.game(S.mode, S.region, nGood, total, Math.round((endTime - startTime) / 1000), gaveUp, S.weak && isFind());
    tickClock();
    show();
    openResults();
  }
  function openResults() {
    const secs = Math.round((endTime - startTime) / 1000), time = `${Math.floor(secs / 60)}:${String(secs % 60).padStart(2, "0")}`;
    const pct = Math.round(100 * nGood / Math.max(1, total));
    const named = isName();
    $("resultsTitle").textContent = gaveUp === "time" ? "Time's up!" : gaveUp ? "Game over" : pct === 100 ? "Perfect!" : "Finished!";
    $("resultsScore").textContent = `${nGood} / ${total}`;
    $("resultsWhat").textContent = named ? (flags() ? "flags named" : caps() ? "capitals named" : `${nouns()} named`) : "right first time";
    const missed = total - nGood;
    $("resultsDetail").textContent = `${pct}% · ${missed} ${named ? "not named" : "missed"} · ${time}`;
    $("resultsBest").hidden = !newBest;
    $("results").hidden = false;
  }
  function closeResults() { $("results").hidden = true; }
  $("reviewBtn").onclick = () => { closeResults(); toast(`Tap any ${noun()} to see its answer.`, 2500); };
  $("replayBtn").onclick = () => { closeResults(); newGame(); };
  $("listBtn").onclick = () => { closeResults(); openSetup(); };
  $("prev").onclick = () => step(-1);
  $("fwd").onclick = () => step(1);

  // ---------- map controls ----------
  function setViewButton() { $("viewBtn").textContent = main.mode === "globe" ? "Flat map" : "Globe"; }
  $("viewBtn").onclick = () => {
    main.setMode(main.mode === "globe" ? "flat" : "globe"); setViewButton();
    if (S.region === "world") savePrefs({ worldView: main.mode });
  };
  function setBorders(on) {
    main.borders = on;
    $("bordersBtn").classList.toggle("on", on); $("bordersBtn").setAttribute("aria-pressed", on);
    if (inset) inset.borders = on;
    redraw();
  }
  function setTerrainOn(on) {
    main.setTerrain(on); if (inset) inset.setTerrain(on);
    $("terrainBtn").classList.toggle("on", on); $("terrainBtn").setAttribute("aria-pressed", on);
  }
  $("bordersBtn").onclick = () => { setBorders(!main.borders); savePrefs({ borders: main.borders }); };
  $("terrainBtn").onclick = () => { setTerrainOn(!main.terrain); savePrefs({ terrain: !!main.terrain }); };
  function setMag(on) {
    S.magnify = on;
    $("magBtn").classList.toggle("on", on); $("magBtn").setAttribute("aria-pressed", on);
    toast(on ? "Tap where you want to magnify." : null);
  }
  $("magBtn").onclick = () => setMag(!S.magnify);
  function goTo(key, animate = true) {
    if (key === "world" || !REGIONS[key].view) { main.world(animate); return; }
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
  // The magnifier's map is built once and reused: building a new one each time left the old ones listening to
  // the same taps, so one tap could be answered twice (right, then "wrong" for the next question).
  let insetView = null;
  function openInset(ll, span) {
    $("inset").hidden = false;
    if (!insetView) {
      insetView = new GG.MapView($("insetMap"), { geo, mode: "flat", flatStyle: main.styleKey, getState,
        onTap: (c, v) => { if (inset) tap(c, v); }, isTarget: c => c === target, isActive: inRegion, isOpen, showCapital, borders: main.borders });
    } else {
      insetView.resize();
    }
    inset = insetView;
    inset.borders = main.borders;
    inset.setTerrain(!!main.terrain);
    inset.lookAt(ll[0], ll[1], span, false);
    inset.requestDraw();
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
  const pick = { mode: "find", region: "world", view: "globe", weak: false, timer: false, paceFind: 5, paceName: 10, data: "world" };
  const STATE_COUNT = 50;
  const isNameMode = m => m === "name" || m === "namecap" || m === "nameflag";
  function segSelect(el, v) { el.querySelectorAll("button").forEach(b => b.classList.toggle("on", b.dataset.v === v)); }
  function buildRegionButtons() {
    $("regions").innerHTML = "";
    Object.entries(REGIONS).filter(([, r]) => !r.us).forEach(([key, r]) => {
      const n = key === "world" ? geoWorld.countries.length : geoWorld.countries.filter(r.test).length;
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
  // World or US states: relabel the games and show only the choices that apply
  function showData() {
    segSelect($("segData"), pick.data);
    const us = pick.data === "us";
    document.querySelectorAll('#segGame button[data-v="find"], #segGame button[data-v="name"]').forEach(b => { b.textContent = us ? "States" : "Countries"; });
    $("regionGroup").hidden = us;
    $("viewField").hidden = us || pick.region !== "world";
  }
  $("segData").addEventListener("click", e => {
    const b = e.target.closest("button"); if (!b) return;
    pick.data = b.dataset.v;
    if (pick.data === "us") pick.region = "usa";
    else if (pick.region === "usa") pick.region = "world";
    segSelect($("regions"), pick.region);
    showData(); showOptions();
  });
  function openSetup() {
    pick.mode = S.mode; pick.region = S.region; pick.view = S.region === "world" ? main.mode : "globe"; pick.data = S.data;
    segSelect($("segGame"), pick.mode); segSelect($("regions"), pick.region); segSelect($("segView"), pick.view);
    showGameGroup(pick.mode);
    $("viewField").hidden = pick.region !== "world";
    pick.weak = !!S.weak; pick.timer = !!S.timer;
    pick.paceFind = S.paceFind || 5; pick.paceName = S.paceName || 10;
    segSelect($("segQuestions"), pick.weak ? "weak" : "all"); segSelect($("segTimer"), pick.timer ? "on" : "off");
    $("regionGroup").open = false;
    showTab("game");
    showData();
    showOptions();
    $("setup").hidden = false;
  }
  function closeSetup() { $("setup").hidden = true; }
  $("menuBtn").onclick = openSetup;
  $("setupClose").onclick = closeSetup;
  $("setup").addEventListener("click", e => { if (e.target === $("setup")) closeSetup(); });
  $("segGame").addEventListener("click", e => { const b = e.target.closest("button"); if (b && !b.disabled) { pick.mode = b.dataset.v; segSelect($("segGame"), pick.mode); showOptions(); } });
  // Options tab: knowledge gaps only for the Find games; the timer for every scored game
  function showOptions() {
    const find = pick.mode === "find" || pick.mode === "findcap" || pick.mode === "findflag";
    $("questionsField").hidden = !find;
    $("questionsNA").hidden = find;
    $("timerField").hidden = pick.mode === "explore";
    $("paceBox").hidden = !pick.timer;
    const pace = isNameMode(pick.mode) ? pick.paceName : pick.paceFind;
    segSelect($("segPace"), String(pace));
    const r = REGIONS[pick.region], all = pick.data === "us" ? STATE_COUNT : pick.region === "world" ? geoWorld.countries.length : geoWorld.countries.filter(r.test).length;
    const n = find && pick.weak ? Math.min(20, all) : all, secs = n * pace;
    $("paceTotal").textContent = `${r.name}: ${n} × ${pace} s = ${Math.floor(secs / 60)}:${String(secs % 60).padStart(2, "0")}`;
    $("regionSummary").textContent = `${r.name} · ${all}`;
    const parts = [find && pick.weak ? "Knowledge gaps" : "", pick.timer && pick.mode !== "explore" ? `Timer ${pace} s` : ""].filter(Boolean);
    $("setupTabs").querySelector('[data-v="options"]').textContent = parts.length ? `Options · ${parts.length}` : "Options";
  }
  function showTab(tab) {
    segSelect($("setupTabs"), tab);
    $("tabGame").hidden = tab !== "game";
    $("tabOptions").hidden = tab !== "options";
  }
  $("setupTabs").addEventListener("click", e => { const b = e.target.closest("button"); if (b) showTab(b.dataset.v); });
  $("segQuestions").addEventListener("click", e => { const b = e.target.closest("button"); if (b) { pick.weak = b.dataset.v === "weak"; segSelect($("segQuestions"), b.dataset.v); showOptions(); } });
  $("segTimer").addEventListener("click", e => { const b = e.target.closest("button"); if (b) { pick.timer = b.dataset.v === "on"; segSelect($("segTimer"), b.dataset.v); showOptions(); } });
  $("segPace").addEventListener("click", e => {
    const b = e.target.closest("button"); if (!b) return;
    if (isNameMode(pick.mode)) pick.paceName = +b.dataset.v; else pick.paceFind = +b.dataset.v;
    showOptions();
  });
  $("regions").addEventListener("click", e => {
    const b = e.target.closest("button"); if (!b) return;
    pick.region = b.dataset.v; segSelect($("regions"), pick.region);
    $("viewField").hidden = pick.region !== "world"; // region games are always flat (chosen 2026-11-14)
    $("regionGroup").open = false;
    showOptions();
  });
  $("segView").addEventListener("click", e => { const b = e.target.closest("button"); if (b) { pick.view = b.dataset.v; segSelect($("segView"), pick.view); } });
  $("startBtn").onclick = () => {
    closeSetup(); closeInset();
    S.weak = pick.weak; S.timer = pick.timer; S.paceFind = pick.paceFind; S.paceName = pick.paceName;
    startGame(pick.mode, pick.region, pick.region === "world" ? pick.view : "flat", pick.data);
  };

  // switch between the world and US states maps (US data loads the first time it's needed)
  async function useData(data) {
    if (data === "us" && !geoUS) geoUS = await GG.loadUS();
    S.data = data;
    geo = data === "us" ? geoUS : geoWorld;
    const style = data === "us" ? "usa" : "patterson";
    main.setGeo(geo, style);
    if (insetView) insetView.setGeo(geo, style);
    GG.debug.geo = geo;
  }
  function startGame(mode, region, view, data = S.data) {
    if (data !== S.data || !geo) return useData(data).then(() => startGame(mode, region, view, data));
    if (data === "us") { region = "usa"; view = "flat"; }
    S.mode = mode; S.region = region;
    savePrefs({ game: { mode, region, data, weak: !!S.weak, timer: !!S.timer, paceFind: S.paceFind || 5, paceName: S.paceName || 10 },
      ...(region === "world" ? { worldView: view } : {}) });
    // region games are cropped to the region; the jump bar is swapped for a "Whole region" button
    main.setCrop(region === "world" ? null : REGIONS[region].crop);
    $("jumpbar").hidden = region !== "world" || mode === "nameflag"; // no map in Name the flags
    $("regionBtn").hidden = region === "world";
    $("regionBtn").textContent = data === "us" ? "Whole US" : "Whole region";
    $("viewBtn").hidden = region !== "world"; // no globe for region games
    if (main.mode !== view) { main.setMode(view); setViewButton(); }
    goTo(region, false);
    hideLearnCard();
    showTimeline(mode === "explore" && data === "us");
    useSub(mode === "explore" && data === "world");
    if (mode !== "nameflag") hideFlagGrid();
    if (mode === "explore") { Object.keys(state).forEach(k => delete state[k]); selected = null; startTime = 0; clearInterval(clockTimer); tickClock(); show(); } else newGame();
  }

  document.addEventListener("keydown", e => {
    if (e.key === "Escape") { closeSetup(); closeInset(); closeResults(); closeStats(); }
    if (e.key === "ArrowLeft") step(-1);
    if (e.key === "ArrowRight") step(1);
  });

  // ---------- start ----------
  async function start() {
    try {
      geo = geoWorld = await GG.loadGeo();
    } catch (err) {
      console.error(err);
      $("eyebrow").textContent = "Problem";
      $("target").textContent = "The map data didn't load. Check your connection and reload.";
      GG.splashDone();
      return;
    }
    // flat map is Patterson (chosen 2026-11-14); ?proj= still picks another style for testing
    const q = new URLSearchParams(location.search);
    const style = GG.FLAT_STYLES[q.get("proj")] ? q.get("proj") : "patterson";
    main = new GG.MapView($("map"), { geo, mode: "globe", flatStyle: style, getState, onTap: tap, onPoint,
      isTarget: c => c === target, isActive: inRegion, isOpen, showCapital });
    main.lookAt(15, 25, 120, false);
    buildRegionButtons();
    GG.debug = { main, geo, startGame, inset: () => insetView };
    setViewButton();
    // testing hooks: ?region=europe&view=flat starts that game; ?at=lon,lat,span and ?terrain=1 adjust the view
    if (REGIONS[q.get("region")] || q.get("view") || q.get("data")) {
      const region = REGIONS[q.get("region")] ? q.get("region") : "world";
      startGame("find", region, region === "world" ? q.get("view") || "globe" : "flat", q.get("data") === "us" ? "us" : "world");
    } else {
      // reopen where you left off: your last game starts behind the New game screen, ready to go
      if (prefs.borders === false) setBorders(false);
      if (prefs.terrain) setTerrainOn(true);
      const g = prefs.game || {};
      S.weak = !!g.weak; S.timer = !!g.timer; S.paceFind = g.paceFind || 5; S.paceName = g.paceName || 10;
      const region = REGIONS[g.region] ? g.region : "world";
      const mode = ["find", "name", "findcap", "namecap", "findflag", "nameflag", "explore"].includes(g.mode) ? g.mode : "find";
      const ready = startGame(mode, region, region === "world" ? (prefs.worldView === "flat" ? "flat" : "globe") : "flat", g.data === "us" ? "us" : "world");
      Promise.resolve(ready).then(openSetup); // first screen: choose a game
    }
    if (q.get("terrain")) $("terrainBtn").click();
    if (q.get("at")) { const [lo, la, sp] = q.get("at").split(",").map(Number); main.lookAt(lo, la, sp, false); }
    GG.onSplashGone = () => main.requestDraw();
    GG.splashDone();
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
