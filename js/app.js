// Game logic and screen wiring. Build 1: game 1 (Find the country) for the whole world, one continent
// or the Caribbean, plus Free tap. Game modes and regions are kept separate so more can be added (PLAN.md).
(function () {
  const GG = window.GG;
  const $ = id => document.getElementById(id);

  // data: "world" (countries), or a country map: "us" (US states, build 3), "ca" (Canada's provinces and territories),
  // "uk" / "ukc" (Britain and Ireland's historic or ceremonial counties, build 4). cd: Crown Dependencies in UK games.
  const S = { mode: "find", region: "world", magnify: false, data: "world", cd: false };
  let geoWorld = null, geoUS = null, geoCA = null, geoIN = null, geoCN = null;
  const geoUK = {}; // "uk", "ukc", "ukn" (the countries view)
  // each country map: what its parts are called, its region key and map style, and how its data loads
  const DATASETS = {
    world: { noun: "country", nouns: "countries", Nouns: "Countries" },
    us: { noun: "state", nouns: "states", Nouns: "States", region: "usa", style: "usa", count: 50,
      load: async () => (geoUS = geoUS || await GG.loadUS()) },
    ca: { noun: "province or territory", nouns: "provinces and territories", Nouns: "Provinces & territories",
      region: "canada", style: "canada", count: 13, load: async () => (geoCA = geoCA || await GG.loadCA(geoWorld.lakes)) },
    // India: 28 states and 8 union territories (a toggle leaves the UTs out); no flags, so no flag games
    in: { noun: "state or union territory", nouns: "states and union territories", Nouns: "States & UTs", region: "india",
      style: "india", count: 36, noFlags: true, load: async () => (geoIN = geoIN || await GG.loadIN(geoWorld.lakes)) },
    // China: 22 provinces, 5 autonomous regions, 4 municipalities and 2 SARs (Taiwan is grey); only Hong Kong and Macau
    // have flags, so no flag games
    cn: { noun: "province", nouns: "provinces", Nouns: "Provinces", region: "china", style: "china", count: 33, noFlags: true,
      load: async () => (geoCN = geoCN || await GG.loadCN(geoWorld.lakes)) },
    // Britain and Ireland: the parts are counties, and county towns stand in for capitals
    uk: { noun: "county", nouns: "counties", Nouns: "Counties", cap: "county town", caps: "county towns", region: "uk", style: "uk",
      set: "Historic", load: async () => (geoUK.uk = geoUK.uk || await GG.loadUK("historic", geoWorld.lakes)) },
    ukc: { noun: "county", nouns: "counties", Nouns: "Counties", cap: "county town", caps: "county towns", region: "ukc", style: "uk",
      set: "Ceremonial", load: async () => (geoUK.ukc = geoUK.ukc || await GG.loadUK("ceremonial", geoWorld.lakes)) },
    // Learning mode's view of the UK and Ireland: just the five countries, each with a card and "Focus on ..." to its counties
    ukn: { noun: "country", nouns: "countries", Nouns: "Countries", region: "ukn", style: "uk",
      load: async () => (geoUK.ukn = geoUK.ukn || await GG.loadUKNations(geoWorld.lakes)) },
  };
  const isCountryMap = d => !!DATASETS[d] && d !== "world";
  const geoFor = d => (d === "us" ? geoUS : d === "ca" ? geoCA : d === "in" ? geoIN : d === "cn" ? geoCN : geoUK[d] || (DATASETS[d] && d !== "world" ? null : geoWorld)); // null until loaded
  const dataOfRegion = r => (REGIONS[r] && REGIONS[r].data) || Object.keys(DATASETS).find(k => DATASETS[k].region === r) || "world";
  const capWord = (n = 1) => (n === 1 ? DATASETS[S.data].cap || "capital" : DATASETS[S.data].caps || "capitals");
  const noun = () => DATASETS[S.data].noun;
  // Big names (the top-bar title: countries, states, provinces, capitals; the Learning card's name) keep their full
  // size when they fit, and shrink only as far as they must (e.g. Newfoundland and Labrador, Saint Vincent and the
  // Grenadines). Refitted whenever the text or the width changes.
  // A name that would need to go below about 17 px on one line wraps onto two lines instead, as large as fits.
  // The top-bar title keeps its fixed height either way (its second line overlaps the score row below).
  function fitText(el) {
    if (!el.offsetParent) return; // hidden: fitted when it's shown
    el.style.fontSize = ""; el.style.whiteSpace = ""; el.style.lineHeight = ""; el.style.overflow = "";
    // exact text width (fractions of a pixel) against the room available, with 1 px to spare: rounded widths let a
    // name overflow by a fraction and still be cut off with "…"
    const range = document.createRange(), room = el.parentElement.getBoundingClientRect().width - 1;
    const wide = () => { range.selectNodeContents(el); return range.getBoundingClientRect().width > room; };
    const max = parseFloat(getComputedStyle(el).fontSize);
    let size = max;
    while (wide() && size > 17) { size -= 1; el.style.fontSize = size + "px"; }
    if (!wide()) return;
    el.style.whiteSpace = "normal"; el.style.lineHeight = "1.1"; el.style.overflow = "visible";
    size = Math.round(max * 0.85); el.style.fontSize = size + "px";
    while ((wide() || el.scrollHeight > size * 1.1 * 2 + 2) && size > 13) { size -= 1; el.style.fontSize = size + "px"; }
  }
  const FIT = ["target", "lcName"].map(id => $(id));
  const fitAll = () => FIT.forEach(fitText);
  FIT.forEach(el => {
    const fit = () => fitText(el);
    new MutationObserver(fit).observe(el, { childList: true, characterData: true, subtree: true });
    if (window.ResizeObserver) { const ro = new ResizeObserver(fit); ro.observe(el.parentElement); ro.observe(el); }
  });
  // the app's font arrives after the first fit (it was measured in the stand-in font): fit again once it's here
  if (document.fonts) { document.fonts.ready.then(fitAll); document.fonts.addEventListener("loadingdone", fitAll); }
  // shorter wording for a country map's top-bar title, if one is ever too long even on two lines (DATASETS[..].titles)
  const title = (key, usual) => (DATASETS[S.data].titles || {})[key] || usual;
  const phWord = () => ({ world: "Country", us: "State", ca: "Province", in: "State", uk: "County", ukc: "County", ukn: "Country" })[S.data]; // flag grid boxes
  const nouns = () => DATASETS[S.data].nouns;

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
    europe:   { name: "Europe",        test: c => c.cont.includes("Europe"),        view: { globe: [9, 55, 46],        flat: [9, 55, 66] },        crop: [[-26, 33], [50, 72]] }, // wide enough for Iceland
    asia:     { name: "Asia",          test: c => c.cont.includes("Asia"),          view: { globe: [88, 22.5, 88],     flat: [88, 22.5, 114.6] },  crop: [[24, -12], [150, 62]] },
    africa:   { name: "Africa",        test: c => c.cont.includes("Africa"),        view: { globe: [17, 1, 72],        flat: [17, 1, 86] },        crop: [[-27, -37], [60, 38]] },
    namerica: { name: "North America", test: c => c.cont.includes("North America"), view: { globe: [-90, 25, 69],      flat: [-104, 39.5, 90.3] }, crop: [[-170, 5], [-50, 75]] },
    carib:    { name: "Caribbean",     test: c => c.car,                            view: { globe: [-72.5, 18, 25.7],  flat: [-72.5, 18, 25.7] },  crop: [[-87, 9], [-58, 28]] },
    samerica: { name: "South America", test: c => c.cont.includes("South America"), view: { globe: [-58, -21.5, 44.7], flat: [-58, -24, 56] },     crop: [[-93, -57], [-33, 14]] },
    usa:      { name: "United States", us: true, test: () => true }, // the whole US map (US states games)
    canada:   { name: "Canada", us: true, test: () => true },        // the whole Canada map (provinces games)
    // India: with the union territories switched off, only the 28 states (Learning mode always shows all 36)
    india:    { name: "India", us: true, test: c => S.ut !== false || S.mode === "explore" || c.info.kind === "State" },
    china:    { name: "China", us: true, test: () => true },
    // Britain and Ireland, for each county set (added below): the whole map, England, Scotland, Wales and Ireland
    oceania:  { name: "Oceania",       test: c => c.cont.includes("Oceania"),       view: { globe: [167, -16, 74.3],   flat: [167, -16, 74.3] },   crop: [[110, -50], [212, 22]] },
  };
  // Britain and Ireland's regions, for both county sets. The Crown Dependencies are only in the whole-map games, when
  // switched on (and always in Learning mode).
  [["uk", "historic"], ["ukc", "ceremonial"]].forEach(([d]) => {
    const all = c => !c.info.cd || S.cd || S.mode === "explore";
    REGIONS[d] = { name: "Britain & Ireland", us: true, data: d, test: all };
    REGIONS[d + "-eng"] = { name: "England", us: true, data: d, test: c => c.info.nation === "England",
      view: { flat: [-1.6, 52.9, 6.6] }, crop: [[-6.6, 49.8], [2.2, 55.9]] };
    REGIONS[d + "-sco"] = { name: "Scotland", us: true, data: d, test: c => c.info.nation === "Scotland",
      view: { flat: [-4.3, 58.0, 6.6] }, crop: [[-8.9, 54.5], [-0.5, 61]] };
    REGIONS[d + "-wal"] = { name: "Wales", us: true, data: d, test: c => c.info.nation === "Wales",
      view: { flat: [-3.75, 52.4, 2.9] }, crop: [[-5.6, 51.3], [-2.6, 53.5]] };
    REGIONS[d + "-ire"] = { name: "Ireland", us: true, data: d, test: c => c.info.island === "Ireland",
      view: { flat: [-7.9, 53.45, 5.2] }, crop: [[-10.8, 51.3], [-5.3, 55.5]] };
    // for Learning mode's "Focus on Northern Ireland" / "Focus on the Republic of Ireland"
    REGIONS[d + "-nir"] = { name: "Northern Ireland", us: true, data: d, test: c => c.info.nation === "Northern Ireland",
      view: { flat: [-6.7, 54.65, 2.4] }, crop: [[-8.4, 53.9], [-5.2, 55.45]] };
    REGIONS[d + "-roi"] = { name: "Republic of Ireland", us: true, data: d, test: c => c.info.nation === "Republic of Ireland",
      view: { flat: [-8.0, 53.3, 5.0] }, crop: [[-10.8, 51.3], [-5.7, 55.5]] };
  });
  REGIONS.ukn = { name: "UK & Ireland", us: true, data: "ukn", test: () => true };
  // a country on the countries view -> its counties (in the county set last used), as a region of that set
  const NATION_REGION = { "N-ENG": "-eng", "N-SCO": "-sco", "N-WAL": "-wal", "N-NIR": "-nir", "N-IRL": "-roi" };
  const ukSet = () => (prefs.ukSet === "ukc" ? "ukc" : "uk");
  // Flag games leave out the counties with no registered flag
  const inRegion = c => (S.region === "world" || REGIONS[S.region].test(c)) && !(tlYear < 1959 && c.info && c.info.year > tlYear)
    && !(flags() && c.info && c.info.flag === false);
  const regionCountries = () => geo.countries.filter(inRegion);

  // Games: find = Find the country, name = Name the countries, findcap = Find the country by its capital,
  // namecap = Name the capitals, explore = Free tap
  const isFind = () => S.mode === "find" || S.mode === "findcap" || S.mode === "findflag";
  const isName = () => S.mode === "name" || S.mode === "namecap" || S.mode === "nameflag";
  const caps = () => S.mode === "findcap" || S.mode === "namecap";
  const flags = () => S.mode === "findflag" || S.mode === "nameflag";
  // flag image (the single-page test build carries the flags inside the page, in window.GG_FLAGS)
  const flagSrc = c => {
    const key = c.flagKey || c.iso; // states and provinces have their own folder (us/, ca/)
    return (window.GG_FLAGS && window.GG_FLAGS[key]) || `data/flags/${key}.webp`;
  };
  const capital = c => c.capitals[0] || "";
  const label = c => (caps() ? `${c.name}: ${capital(c)}` : c.name);
  let selected = null;   // naming games: the country whose name or capital is being typed
  // statehood timeline (US Learning mode): the year shown; states that join that year are highlighted
  let tlYear = 1959, tlTimer = null;
  const isUnformed = c => tlYear < 1959 && !!c.info && c.info.year > tlYear;
  const tlBorders = new Map(); // year -> borders that existed then (between two states, or a state and land not yet a state)
  // reviewing a finished game: the tapped country is shown in dark green (right), dark red (missed) or blue
  const getState = c => (flashing[c.iso] ? "flash" : finished && c === reviewSel ? (state[c.iso] === "good" ? "goodSel" : state[c.iso] === "bad" ? "badSel" : "sel")
    : c === selected ? "sel" : state[c.iso] ||
    (tlYear < 1959 && c.info && c.info.year === tlYear ? "sel" : null));
  // still to answer (Free tap, or a finished naming game: any country in the region); taps near small
  // open countries snap to them
  // once a game is finished every country in the region is open again, for reviewing the answers
  // capitals games: show a capital's dot once its country or state has been answered (right, wrong, or given up)
  const showCapital = c => caps() && (state[c.iso] === "good" || state[c.iso] === "bad");
  const isOpen = c => inRegion(c) && (S.mode === "explore" || finished || !state[c.iso]);

  // `order` holds the countries still to answer. Find the country: the arrows move through it with no penalty.
  let order = [], idx = 0, target = null, nGood = 0, nBad = 0, finished = false, gaveUp = false, total = 0, reviewSel = null;
  let startTime = 0, endTime = 0;

  function newGame() {
    Object.keys(state).forEach(k => delete state[k]);
    let list = regionCountries();
    if (S.weak && isFind()) list = weakest(list, WEAK_COUNT);
    total = list.length;
    order = d3.shuffle(list); idx = 0; nGood = nBad = 0; finished = gaveUp = false; selected = null; reviewSel = null; $("reviewBar").hidden = true;
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
      t.textContent = title("tapAny", `Tap any ${noun()}`);
      $("score").textContent = `Tap any ${noun()} to learn about it.`;
    } else if (isName()) {
      $("eyebrow").textContent = (finished ? "Finished" : flags() ? "Name the flags" : caps() ? `Name the ${capWord(2)}` : `Name the ${nouns()}`) + where;
      if (finished) {
        t.textContent = `${nGood} of ${total} named`;
        $("score").textContent = flags() ? "Missed flags are shown in red." : `Tap any ${noun()} to see its ${caps() ? capWord() : "name"}.`;
        $("giveup").textContent = "Play again";
      } else {
        if (!typing) t.textContent = flags() ? title("flagEach", `Type each flag's ${noun()}`) : title("tapOne", `Tap a ${noun()}`);
        $("score").innerHTML = `<b>${nGood}</b> / ${total} named`;
      }
    } else if (finished) {
      $("eyebrow").textContent = "Finished" + where;
      t.textContent = `${nGood} of ${total} right`;
      $("score").innerHTML = `<b>${nGood}</b> / ${total} <span class="wrong">· ${nBad} wrong</span> · tap any ${noun()} to see it`;
      $("giveup").textContent = "Play again";
    } else {
      $("eyebrow").textContent = (S.mode === "findflag" ? "Find by flag" : caps() ? `Find by ${capWord()}` : "Find") + where + (S.weak ? " · knowledge gaps" : "");
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
      // Reservations layer: name the reserved land under the tap (the card still shows the country or state)
      const res = main.reserves && view.lastTap ? view.reserveAt(view.lastTap[0], view.lastTap[1]) : null;
      if (res) toast(`${res.properties.n} · ${RES_KIND[res.properties.k] || ""}`, 3000);
      // world Learning map zoomed into the US: a tap on a state shows the state
      const f = c.iso === "USA" && view.sub && view.lastTap ? view.subAt(view.lastTap[0], view.lastTap[1]) : null;
      selectSub(f);
      flashName(f ? f.c : c);
      if (!f) state[c.iso] = "flash";
      showLearnCard(f ? f.c : c);
      showFocus(c);
      redraw(); return;
    }
    if (finished) { reviewSel = c; flashName(c); redraw(); return; } // reviewing: tap any country to see its name (or capital)
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
  const facts = rows => rows.filter(r => r[1]).map(([k, v, html]) => `<dt>${esc(k)}</dt><dd>${html ? v : esc(v)}</dd>`).join("");
  let learnMore = false;
  function showLearnCard(c) {
    const i = c.info || {};
    $("lcFlag").hidden = false; // (a county with no flag hides it)
    if (geoUS && geoUS.byIso[c.iso] === c) { showStateCard(c, i); return; }
    if (geoCA && geoCA.byIso[c.iso] === c) { showProvinceCard(c, i); return; }
    if (geoIN && geoIN.byIso[c.iso] === c) { showIndiaCard(c, i); return; }
    if (geoCN && geoCN.byIso[c.iso] === c) { showChinaCard(c, i); return; }
    if (i.kind === "nation") { showNationCard(c, i); return; }
    if (Object.values(geoUK).some(g => g.byIso[c.iso] === c)) { showCountyCard(c, i); return; }
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
  // the UK and Ireland's countries (Learning mode's countries view)
  function showNationCard(c, i) {
    $("lcFlag").src = flagSrc(c); $("lcFlag").alt = c.iso === "N-NIR" ? "Union Flag" : `Flag of ${c.name}`;
    $("lcName").textContent = c.name;
    $("lcSub").textContent = c.iso === "N-IRL" ? "Independent country · Europe" : "Country of the United Kingdom";
    $("lcMain").innerHTML = facts([["Capital", c.capitals[0]], ["Population", fmtPop(i.pop, i.popYear)]]);
    $("lcMore").innerHTML =
      factGroup("People", [
        ["Largest city", i.city || `${c.capitals[0]} (the capital)`],
        [/,/.test(i.langs) ? "Languages" : "Language", i.langs],
        ["Patron saint", i.saint],
      ]) +
      factGroup("Land", [
        ["Area", `${num(i.area)} km² (${num(Math.round(i.area / 2.589988))} sq mi)`],
        ["Highest point", `${i.high[0]}, ${num(i.high[1])} m (${num(Math.round(i.high[1] * 3.28084))} ft)`],
        ["Counties", c.iso === "N-NIR" || c.iso === "N-IRL" ? `${i.historic} traditional counties` : `${i.historic} historic, ${i.ceremonial} ${c.iso === "N-WAL" ? "preserved" : c.iso === "N-SCO" ? "lieutenancy areas" : "ceremonial"}`],
      ]) +
      factGroup("History", [
        ["Story", i.history],
        ["Governed by", i.gov],
      ]) +
      factGroup("Symbols", [
        ["Flag", c.iso === "N-NIR" ? "No official flag of its own: the Union Flag is used" : ""],
        ["Emblem", i.flower],
      ]);
    setLearnMore(learnMore);
    $("learnCard").hidden = false;
  }
  // Britain and Ireland's counties: what kind of area it is, its county town, nation (and province, Irish name), area
  function showCountyCard(c, i) {
    $("lcFlag").hidden = !i.flag; // only counties with a registered flag have one
    if (i.flag) { $("lcFlag").src = flagSrc(c); $("lcFlag").alt = `Flag of ${c.name}`; }
    $("lcName").textContent = c.name;
    const what = i.cd ? "Crown Dependency" : i.kind === "ireland" ? "Traditional county"
      : i.kind === "historic" ? "Historic county"
      : i.nation === "Wales" ? "Preserved county" : i.nation === "Scotland" ? "Lieutenancy area" : "Ceremonial county";
    $("lcSub").textContent = [what, i.cd ? "" : i.nation, i.province ? `${i.province}` : ""].filter(Boolean).join(" · ");
    const n = (geoUK[S.data] || geoUK.uk).countries.length;
    $("lcMain").innerHTML = facts([[i.cd ? "Capital" : "County town", c.capitals[0]], ["Area", `${num(i.area)} km² (${num(Math.round(i.area / 2.589988))} sq mi)`]]);
    const f = i.facts || {}; // tools/uk_facts.py
    const [gaaColours, gaaName] = (f.gaa || "").split(" · ");
    $("lcMore").innerHTML =
      factGroup("Names", [
        ["In Irish", i.irish],
        ["Also called", c.names.filter(x => x !== c.name && !/^(County|Co) /.test(x)).join(", ")],
        ["Other county towns", c.capitals.slice(1).filter(t => !/^(Kingston|Newcastle|Appleby|Port Laoise|Saint )$/.test(t)).join(", ")],
        ["Locals are called", f.people],
      ]) +
      factGroup("History", [
        ["Historic kingdom", f.kingdom],
        ["Clans", f.clans],
      ]) +
      factGroup("Culture", [
        ["County flower", f.flower],
        ["County day", f.day],
        ["Famous food", f.food],
        ["Landmark", f.landmark],
        ["Motto", f.motto],
      ]) +
      factGroup("Gaelic games", [
        ["County colours", gaaColours],
        ["Nickname", gaaName],
      ]) +
      factGroup("Land", [
        ["Size", S.data === "ukn" ? "" : `#${i.areaRank} of ${n} by area`],
      ]) +
      factGroup("Flag", [
        ["Shows", i.flag ? f.flag : ""],
        ["Status", i.flag ? (i.cd ? "Official flag" : "Registered in the UK Flag Registry") : i.cd ? "" : "No registered flag yet"],
      ]);
    setLearnMore(learnMore);
    $("learnCard").hidden = false;
  }
  // India's states and union territories (2011 census, the latest published)
  function showIndiaCard(c, i) {
    $("lcFlag").hidden = true; // Indian states and UTs have no official flags
    $("lcName").textContent = c.name;
    $("lcSub").textContent = `${i.kind} · ${i.region} India · ${i.abbr}`;
    $("lcMain").innerHTML = facts([[/ (in|and|also) /.test(i.capNote || "") ? "Capitals" : "Capital", i.capNote || c.capitals[0]],
      ["Population", fmtPop(i.pop, i.popYear)]]);
    const f = i.facts || {}; // tools/in_facts.py
    $("lcMore").innerHTML =
      factGroup("Names", [
        [f.scriptName ? `In ${f.scriptName}` : "", f.script ? `<span class="native">${esc(f.script)}</span>` : "", true],
        ["The name means", f.origin],
        [/,/.test(f.langs || "") ? "Languages" : "Language", f.langs],
      ]) +
      factGroup("People and culture", [
        ["Largest city", f.city || ""],
        ["Famous dish", f.dish],
        ["Textile", f.textile],
        ["Biggest festival", f.festival],
      ]) +
      factGroup("Land and nature", [
        ["Area", `${num(i.area)} km² (${num(Math.round(i.area / 2.589988))} sq mi), #${i.areaRank} of 36`],
        ["Highest point", f.high],
        ["Coast", i.coastal === undefined ? "" : i.coastal ? "Yes" : "Landlocked"],
        ["Borders", (i.borders || []).join(", ")],
        ["Main river", f.river],
        ["Climate", f.climate],
        ["National park", f.park],
      ]) +
      factGroup("History and landmarks", [
        ["In its present shape since", String(i.year)],
        ["Formed from", i.origin],
        ["Grew from", f.kingdom],
        ["UNESCO World Heritage", f.unesco],
        ["Pilgrimage", f.pilgrimage],
      ]) +
      factGroup("Symbols", [
        ["Animal", f.animal], ["Bird", f.bird], ["Flower", f.flower], ["Tree", f.tree],
      ]) +
      factGroup("Economy", [["Known for", f.economy]]);
    setLearnMore(learnMore);
    $("learnCard").hidden = false;
  }
  // China's provincial-level divisions (2020 census; Hong Kong and Macau 2021). Names in Chinese characters and pinyin.
  function showChinaCard(c, i) {
    const f = i.facts || {}; // tools/cn_facts.py
    $("lcFlag").hidden = !i.flag; // only Hong Kong and Macau have their own flags
    if (i.flag) { $("lcFlag").src = flagSrc(c); $("lcFlag").alt = `Flag of ${c.name}`; }
    $("lcName").textContent = c.name;
    $("lcSub").textContent = `${i.kind} · ${i.region} China · ${i.abbr}`;
    const city = i.kind === "Municipality" || i.kind === "Special administrative region";
    $("lcMain").innerHTML = facts([[city ? "City" : "Capital", city ? "The whole area is one city" : c.capitals[0]],
      ["Population", fmtPop(i.pop, i.popYear)]]);
    $("lcMore").innerHTML =
      factGroup("Names", [
        ["In Chinese", f.zh ? `<span class="native">${esc(f.zh)}</span> ${esc(f.py || "")}` : "", true],
        ["One-character name", f.short ? `<span class="native">${esc(f.short)}</span> (on number plates)` : "", true],
      ]) +
      factGroup("People and culture", [
        ["Largest city", f.city || ""],
        [/,| and /.test(f.langs || "") ? "Languages" : "Language", f.langs],
        ["Peoples", f.ethnic],
        ["Food", f.cuisine],
        ["Traditional art", f.art],
        ["Festival", f.festival],
      ]) +
      factGroup("Land and nature", [
        ["Area", `${num(i.area)} km² (${num(Math.round(i.area / 2.589988))} sq mi), #${i.areaRank} of 33`],
        ["Highest point", f.high],
        ["Coast", i.coastal === undefined ? "" : i.coastal ? "Yes" : "Landlocked"],
        ["Borders", (i.borders || []).join(", ")],
        ["Main river", f.river],
        ["Climate", f.climate],
        ["Scenic spot", f.scenic],
        ["Wildlife", f.animal],
      ]) +
      factGroup("History and landmarks", [
        ["Long ago", f.ancient],
        ["In its present form since", f.year],
        ["UNESCO World Heritage", f.unesco],
        ["Great Wall", f.wall],
      ]) +
      factGroup("Economy", [["Known for", f.industry]]);
    setLearnMore(learnMore);
    $("learnCard").hidden = false;
  }
  // Canada's provinces and territories (2021 census, areas from Statistics Canada)
  function showProvinceCard(c, i) {
    $("lcFlag").src = flagSrc(c); $("lcFlag").alt = `Flag of ${c.name}`;
    $("lcName").textContent = c.name;
    $("lcSub").textContent = `${i.kind} · ${i.region} · ${i.abbr}`;
    $("lcMain").innerHTML = facts([["Capital", c.capitals[0]], ["Population", fmtPop(i.pop, i.popYear)]]);
    const hi = i.high;
    const joined = i.year === 1867 ? "1867, at Confederation (a founding province)"
      : c.iso === "NU" ? "1999, split from the Northwest Territories"
      : c.iso === "YT" ? "1898, split from the Northwest Territories" : String(i.year);
    $("lcMore").innerHTML =
      factGroup("People", [
        ["Largest city", i.city || `${c.capitals[0]} (the capital)`],
      ]) +
      factGroup("Land", [
        ["Area", i.area ? `${num(i.area)} km² (${num(Math.round(i.area / 2.589988))} sq mi), #${i.areaRank} of 13` : ""],
        ["Highest point", hi ? `${hi[0]}, ${num(hi[1])} m (${num(Math.round(hi[1] * 3.28084))} ft)` : ""],
        [/;/.test(i.tz || "") ? "Time zones" : "Time zone", i.tz],
      ]) +
      factGroup("History", [
        ["Part of Canada since", joined],
        ["Name comes from", i.origin],
      ]) +
      factGroup(i.kind === "Territory" ? "Territorial symbols" : "Provincial symbols", [
        ["Bird", i.bird],
        ["Flower", i.flower],
      ]);
    setLearnMore(learnMore);
    $("learnCard").hidden = false;
  }
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
    $("lcWrap").classList.toggle("expanded", on);
    $("lcLess").hidden = !on; // the pinned "fewer facts" arrow, top left
  }
  $("lcLess").onclick = () => { setLearnMore(false); $("learnCard").scrollTop = 0; };
  $("lcMoreBtn").onclick = () => setLearnMore(!learnMore);
  function hideLearnCard() { $("learnCard").hidden = true; $("focusBtn").hidden = true; }
  // Focus: a button above the card that opens a country's own map in Learning mode ("Focus on <name> ›").
  // Only the US has its own map so far; the plan is one for every country (PLAN.md).
  // Countries with their own map: the Countries tab in the New game menu and the Focus button both use this list.
  // `unit` names the parts (States, Provinces, Counties); `soon` ones are listed but can't be opened yet.
  const COUNTRY_MAPS = {
    USA: { name: "United States", focus: "The U.S.", cont: "North America", unit: "States", data: "us", region: "usa" },
    CAN: { name: "Canada", focus: "Canada", cont: "North America", unit: "Provinces & territories", data: "ca", region: "canada" },
    // the UK and Ireland share one map of Britain and Ireland's counties (Ireland opens on its own region)
    GBR: { name: "United Kingdom", focus: "the UK", cont: "Europe", unit: "Counties", data: "uk", region: "uk", page: "Britain & Ireland" },
    IRL: { name: "Ireland", focus: "Ireland", cont: "Europe", unit: "Counties", data: "uk", region: "uk-ire", page: "Britain & Ireland" },
    // coming next (India_plan.md, China_plan.md, Russia_plan.md, Australia_plan.md); Russia is in Europe and Asia
    IND: { name: "India", focus: "India", cont: "Asia", unit: "States & UTs", data: "in", region: "india" },
    CHN: { name: "China", focus: "China", cont: "Asia", unit: "Provinces", data: "cn", region: "china" },
    RUS: { name: "Russia", focus: "Russia", cont: ["Europe", "Asia"], unit: "Oblasts", soon: true },
    AUS: { name: "Australia", focus: "Australia", cont: "Oceania", unit: "States & territories", soon: true },
  };
  // from the world Learning map, the UK and Ireland open the countries view first
  const FOCUS_INTO = { GBR: { region: "ukn", data: "ukn" }, IRL: { region: "ukn", data: "ukn" },
  };
  let focusOn = null;
  function showFocus(c) {
    const m = S.data === "world" ? COUNTRY_MAPS[c.iso] : null;
    focusOn = m && !m.soon ? m : null;
    // the UK & Ireland countries view: each country opens its own counties
    if (S.data === "ukn" && NATION_REGION[c.iso]) {
      const d = ukSet();
      focusOn = { focus: c.iso === "N-IRL" ? "the Republic" : c.name, region: d + NATION_REGION[c.iso], data: d };
    }
    $("focusBtn").hidden = !focusOn;
    if (focusOn) $("focusBtn").textContent = `Focus on ${focusOn.focus} ›`;
  }
  $("focusBtn").onclick = () => {
    if (!focusOn) return;
    const into = S.data === "world" && FOCUS_INTO[Object.keys(COUNTRY_MAPS).find(k => COUNTRY_MAPS[k] === focusOn)];
    startGame("explore", (into || focusOn).region, "flat", (into || focusOn).data);
  };
  $("worldBtn").onclick = () => S.data === "uk" || S.data === "ukc" ? startGame("explore", "ukn", "flat", "ukn")
    : startGame("explore", "world", prefs.worldView || "globe", "world");
  $("lcClose").onclick = () => { hideLearnCard(); selectSub(null); Object.keys(state).forEach(k => delete state[k]); redraw(); };
  // ---------- Reservations layer (country Learning maps only; too heavy for the world globe) ----------
  // US: reservations and Oklahoma tribal areas (US Census). Canada: First Nations reserves, and Indigenous settlement
  // and owned lands (Natural Resources Canada). One file per country, loaded the first time it's needed.
  const RES = {
    us: { file: "data/tribal-us.json", label: "Reservations", credit: "Reservations: US Census Bureau." },
    ca: { file: "data/tribal-ca.json", label: "Reserves",
      credit: "Reserves: Natural Resources Canada. Contains information licensed under the Open Government Licence – Canada." },
  };
  const tribal = {}, tribalLoading = {};
  let resAfterSplash = false, resOn = !!prefs.reserves;
  function showReserves() {
    const d = S.data, learning = S.mode === "explore" && !!RES[d];
    // not loaded under the splash (preparing them made the splash jumpy)
    if (learning && resOn && !tribal[d] && GG.splashShowing) resAfterSplash = true;
    else if (learning && resOn && !tribal[d] && !tribalLoading[d]) {
      tribalLoading[d] = true; toast(`Loading ${RES[d].label.toLowerCase()}…`);
      fetch(RES[d].file).then(r => r.json()).then(g => { tribal[d] = GG.fixWinding(g); toast(null); showReserves(); })
        .catch(() => { toast(`Couldn't load the ${RES[d].label.toLowerCase()}.`, 2000); resOn = false; showReserves(); })
        .finally(() => { tribalLoading[d] = false; });
    }
    $("resBtn").hidden = !learning;
    if (learning) { $("resBtn").textContent = RES[d].label; $("resCredit").textContent = RES[d].credit; }
    const on = learning && resOn && tribal[d];
    $("resBtn").classList.toggle("on", learning && resOn); $("resBtn").setAttribute("aria-pressed", learning && resOn);
    $("resCredit").hidden = !on;
    main.setReserves(on ? tribal[d] : null);
  }
  $("resBtn").onclick = () => { resOn = !resOn; savePrefs({ reserves: resOn }); showReserves(); };
  const RES_KIND = { Reservation: "Reservation, United States", "Oklahoma tribal area": "Oklahoma tribal statistical area, United States",
    Reserve: "Indigenous reserve or settlement land, Canada" };

  // US states on the world Learning map (loaded the first time they're needed)
  function useSub(on) {
    if (!on) { main.setSub(null); return; }
    const set = () => { if (S.mode === "explore" && S.data === "world") main.setSub({ features: geoUS.f50.filter(f => f.c), borders: subBorders(), selected: null }); };
    if (geoUS) set(); else GG.loadUS().then(g => { geoUS = geoUS || g; set(); }).catch(() => {});
  }
  // the state borders, simplified once: the full detail made zooming into the US jittery on the world map
  let subBordersCache = null;
  const subBorders = () => subBordersCache || (subBordersCache = GG.simplify(geoUS.borders50, 0.02));
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
    if (year >= 1959 || !geo.bordersWhere) main.setBordersOverride(null);
    else {
      if (!tlBorders.has(year)) tlBorders.set(year, geo.bordersWhere((a, b) => (a && a.info.year <= year) || (b && b.info.year <= year)));
      main.setBordersOverride(tlBorders.get(year));
    }
    redraw();
  }
  function stopTimeline() { clearInterval(tlTimer); tlTimer = null; $("tlPlay").textContent = "▶"; $("tlPlay").setAttribute("aria-label", "Play the timeline"); }
  function showTimeline(on) {
    stopTimeline();
    $("timeline").hidden = !on;
    $("mapwrap").classList.toggle("hastl", on);
    tlYear = 1959;
    main.setBordersOverride(null);
    if (on) setTimeline(1959);
  }
  $("tlRange").addEventListener("input", e => { stopTimeline(); setTimeline(+e.target.value); });
  // the arrows jump to the previous or next year a state joined
  const joinYears = () => [...new Set(geo.countries.map(c => c.info.year))].sort((a, b) => a - b);
  $("tlPrev").onclick = () => { stopTimeline(); const y = joinYears().filter(y => y < tlYear).pop(); setTimeline(y || 1787); };
  $("tlNext").onclick = () => { stopTimeline(); const y = joinYears().find(y => y > tlYear); setTimeline(y || 1959); };
  $("tlPlay").onclick = () => {
    if (tlTimer) { stopTimeline(); return; }
    const years = joinYears();
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
  const modeName = (m, region) => { const d = DATASETS[dataOfRegion(region)];
    return MODE_NAMES[m].replace("countries", d.nouns).replace("capitals", d.caps || "capitals").replace("capital", d.cap || "capital"); };
  let statsSkill = "country", statsData = "world";
  const fmtTime = s => `${Math.floor(s / 60)}:${String(s % 60).padStart(2, "0")}`;
  function openStats() { statsData = S.data === "ukn" ? "uk" : S.data; renderStats(); $("stats").hidden = false; }
  function closeStats() { $("stats").hidden = true; resetStatsReset(); }
  function renderStats() {
    const skill = statsSkill, St = GG.Stats, ds = DATASETS[statsData], sub = isCountryMap(statsData);
    document.querySelectorAll("#statsSkill button").forEach(b => b.classList.toggle("on", b.dataset.v === skill));
    document.querySelectorAll("#statsData button").forEach(b => b.classList.toggle("on", b.dataset.v === statsData));
    $("statsSkill").querySelector('[data-v="country"]').textContent = ({ us: "States", ca: "Provinces", in: "States", cn: "Provinces", uk: "Counties", ukc: "Counties" })[statsData] || "Countries";
    $("statsSkill").querySelector('[data-v="capital"]').textContent = ds.caps ? "County towns" : "Capitals";
    // no flags (India): no Flags tab
    $("statsSkill").querySelector('[data-v="flag"]').hidden = !!ds.noFlags;
    if (ds.noFlags && statsSkill === "flag") { statsSkill = "country"; renderStats(); return; }
    if (sub && !geoFor(statsData)) { ds.load().then(renderStats).catch(() => {}); return; }
    const g = geoFor(statsData);
    // games of this map: a country map's own region, or any world region
    const ofThis = rg => dataOfRegion(rg) === statsData;
    const acc = c => { const e = St.entry(skill, c.iso); return e && e.a ? e.c / e.a : null; };
    const known = c => { const a = acc(c); return a !== null && a >= 0.75; };
    // regions
    const rows = Object.entries(REGIONS).filter(([key]) => dataOfRegion(key) === statsData).map(([key, r]) => {
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
    }).join("") : `<li class="empty">Nothing yet. Play a ${skill === "capital" ? "capitals" : skill === "flag" ? "flags" : ds.nouns} game and your weakest ones will show here.</li>`;
    // bests (for this skill's games)
    const modes = skill === "capital" ? ["findcap", "namecap"] : skill === "flag" ? ["findflag", "nameflag"] : ["find", "name"];
    const bests = Object.entries(St.bests()).filter(([k]) => modes.includes(k.split("|")[0]) && ofThis(k.split("|")[1]))
      .map(([k, v]) => { const [m, rg] = k.split("|"); return `<li><span>${modeName(m, rg)} · ${REGIONS[rg] ? REGIONS[rg].name : rg}</span><span class="snum">${v.pct}% · ${fmtTime(v.secs)}</span></li>`; });
    $("statsBests").innerHTML = bests.length ? bests.join("") : `<li class="empty">No games finished yet.</li>`;
    // recent games
    const games = St.games().filter(gm => modes.includes(gm.mode) && ofThis(gm.region)).slice(0, 8);
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
        `autocapitalize="off" spellcheck="false" enterkeyhint="next" aria-label="${phWord()} with this flag" placeholder="${(prefs.perRow || 4) >= 6 ? "…" : phWord()}">`;
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
    $("flagGrid").querySelectorAll("input").forEach(i => { i.placeholder = n >= 6 ? "…" : phWord(); });
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
    $("resultsWhat").textContent = named ? (flags() ? "flags named" : caps() ? `${capWord(2)} named` : `${nouns()} named`) : "right first time";
    const missed = total - nGood;
    $("resultsDetail").textContent = `${pct}% · ${missed} ${named ? "not named" : "missed"} · ${time}`;
    $("resultsBest").hidden = !newBest;
    $("results").hidden = false;
  }
  function closeResults() { $("results").hidden = true; }
  $("reviewBtn").onclick = () => { closeResults(); $("reviewBar").hidden = false; toast(`Tap any ${noun()} to see its answer.`, 2500); };
  $("reviewBar").onclick = () => { $("reviewBar").hidden = true; openSetup(); };
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
  const WORLD_JUMPS = $("jumps").innerHTML; // the continent buttons (the UK Learning map swaps in its own)
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
  // Countries tab: continent headings (the Caribbean is part of North America) with a button per country map
  function buildCountryList() {
    const conts = ["Europe", "Asia", "Africa", "North America", "South America", "Oceania"];
    $("countryList").innerHTML = conts.map(ct => {
      const inCont = m => (Array.isArray(m.cont) ? m.cont.includes(ct) : m.cont === ct);
      const btns = Object.entries(COUNTRY_MAPS).filter(([, m]) => inCont(m)).map(([iso, m]) => {
        const c = geoWorld.byIso[iso];
        return `<button type="button" data-v="${iso}"${m.soon ? " disabled" : ""}>${c ? `<img src="${flagSrc(c)}" alt="">` : ""}` +
          `<span>${esc(m.name)}</span>${m.soon ? "<small>soon</small>" : ""}</button>`;
      }).join("");
      return `<section><h3>${ct}</h3>${btns ? `<div class="cbtns">${btns}</div>` : `<p class="none">More countries to come</p>`}</section>`;
    }).join("");
  }
  // World, the list of countries, or one country's page (its Find and Name games)
  function showData() {
    const countries = pick.tab === "countries";
    segSelect($("segData"), pick.tab);
    $("worldPanel").hidden = countries;
    $("countryList").hidden = !countries || !!pick.country;
    $("countryPage").hidden = !countries || !pick.country;
    if (countries && pick.country) {
      const m = COUNTRY_MAPS[pick.country], ds = DATASETS[pick.data];
      $("cpName").textContent = m.page || m.name;
      $("cpGames").querySelectorAll('[data-v="find"], [data-v="name"]').forEach(b => { b.textContent = m.unit; });
      const capsLabel = ds.caps ? ds.caps[0].toUpperCase() + ds.caps.slice(1) : "Capitals";
      $("cpGames").querySelectorAll('[data-v="findcap"], [data-v="namecap"]').forEach(b => { b.textContent = capsLabel; });
      segSelect($("cpGames"), pick.mode);
      // Britain and Ireland: county set, region and the Crown Dependencies, chosen before each game
      const uk = pick.data === "uk" || pick.data === "ukc";
      $("cpOpts").hidden = !uk;
      // no county in Ireland has a registered flag: no flag games there (shown again for every other choice)
      const noFlags = (uk && /-ire$/.test(pick.region)) || !!DATASETS[pick.data].noFlags;
      // India: union territories on or off
      $("cpUTField").hidden = pick.data !== "in";
      if (pick.data === "in") segSelect($("cpUT"), pick.ut === false ? "off" : "on");
      $("cpGames").querySelectorAll('[data-v="findflag"], [data-v="nameflag"]').forEach(b => { b.hidden = noFlags; });
      if (noFlags && /flag$/.test(pick.mode)) { pick.mode = pick.mode.replace("flag", ""); segSelect($("cpGames"), pick.mode); }
      if (uk) {
        segSelect($("cpSet"), pick.data);
        segSelect($("cpRegion"), pick.region.replace(/^ukc?/, "") || "all");
        segSelect($("cpCD"), pick.cd ? "on" : "off");

        $("cpCDField").hidden = pick.region !== pick.data; // whole map only
      }
    }
    $("startBtn").hidden = countries && !pick.country; // pick a country first
    if (!countries) { segSelect($("segGame"), pick.mode); showGameGroup(pick.mode); $("viewField").hidden = pick.region !== "world"; }
  }
  $("segData").addEventListener("click", e => {
    const b = e.target.closest("button"); if (!b) return;
    pick.tab = b.dataset.v; pick.country = null;
    if (pick.tab === "world") { pick.data = "world"; if (REGIONS[pick.region].us) pick.region = "world"; segSelect($("regions"), pick.region); }
    showData(); showOptions();
  });
  $("countryList").addEventListener("click", e => {
    const b = e.target.closest("button"); if (!b || b.disabled) return;
    const m = COUNTRY_MAPS[b.dataset.v];
    pick.country = b.dataset.v; pick.data = m.data; pick.region = m.region;
    showData(); showOptions();
  });
  $("cpBack").onclick = () => { pick.country = null; showData(); };
  $("setBtn").onclick = () => { const d = S.data === "uk" ? "ukc" : "uk"; savePrefs({ ukSet: d }); startGame("explore", d + S.region.replace(/^ukc?/, ""), "flat", d); };
  const ukRegionPart = r => r.replace(/^ukc?/, "");
  $("cpSet").addEventListener("click", e => {
    const b = e.target.closest("button"); if (!b) return;
    pick.region = b.dataset.v + ukRegionPart(pick.region); pick.data = b.dataset.v;
    showData(); showOptions();
  });
  $("cpRegion").addEventListener("click", e => {
    const b = e.target.closest("button"); if (!b) return;
    pick.region = pick.data + (b.dataset.v === "all" ? "" : b.dataset.v);
    showData(); showOptions();
  });
  $("cpUT").addEventListener("click", e => {
    const b = e.target.closest("button"); if (!b) return;
    pick.ut = b.dataset.v === "on"; showData(); showOptions();
  });
  $("cpCD").addEventListener("click", e => {
    const b = e.target.closest("button"); if (!b) return;
    pick.cd = b.dataset.v === "on"; showData(); showOptions();
  });
  // how many a game would ask: the region's parts (UK: with or without the Crown Dependencies; flags: only those with one)
  function countFor(data, region, mode, cd) {
    const g = geoFor(data);
    if (!g) return null;
    const keep = [S.cd, S.mode, S.ut]; S.cd = cd; S.mode = mode; S.ut = pick.ut;
    const n = g.countries.filter(c => region === "world" || REGIONS[region].test(c))
      .filter(c => !((mode === "findflag" || mode === "nameflag") && c.info && c.info.flag === false)).length;
    [S.cd, S.mode, S.ut] = keep;
    return n;
  }
  $("cpGames").addEventListener("click", e => {
    const b = e.target.closest("button"); if (!b) return;
    pick.mode = b.dataset.v; segSelect($("cpGames"), pick.mode); showOptions();
  });
  // the cog: Options (knowledge gaps, timer) in place of the games
  function showOptPanel(on) {
    $("tabOptions").hidden = !on; $("tabGame").hidden = on; $("setupTabs").hidden = on;
    $("setupTitle").textContent = on ? "Options" : "New game";
    $("optBtn").classList.toggle("on", on); $("optBtn").setAttribute("aria-pressed", on);
  }
  $("optBtn").onclick = () => showOptPanel($("tabOptions").hidden);
  $("optBack").onclick = () => showOptPanel(false);
  function openSetup() {
    // Learning mode has its own tab now, so the menu opens on a scored game
    pick.mode = S.mode === "explore" ? "find" : S.mode;
    pick.region = S.region; pick.view = S.region === "world" ? main.mode : "globe"; pick.data = S.data;
    pick.tab = S.data === "world" ? "world" : "countries";
    const mapData = S.data === "ukc" ? "uk" : S.data; // both county sets are one entry in the list
    pick.country = S.data === "world" ? null : /-ire$/.test(S.region) ? "IRL"
      : Object.keys(COUNTRY_MAPS).find(k => COUNTRY_MAPS[k].data === mapData) || null;
    pick.cd = !!S.cd; pick.ut = S.ut !== false;
    if (!$("countryList").childElementCount) buildCountryList();
    segSelect($("segGame"), pick.mode); segSelect($("regions"), pick.region); segSelect($("segView"), pick.view);
    showGameGroup(pick.mode);
    $("viewField").hidden = pick.region !== "world";
    pick.weak = !!S.weak; pick.timer = !!S.timer;
    pick.paceFind = S.paceFind || 5; pick.paceName = S.paceName || 10;
    segSelect($("segQuestions"), pick.weak ? "weak" : "all"); segSelect($("segTimer"), pick.timer ? "on" : "off");
    $("regionGroup").open = false;
    showOptPanel(false);
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
    const r = REGIONS[pick.region];
    let all = countFor(pick.data, pick.region, pick.mode, pick.cd);
    if (all === null) { DATASETS[pick.data].load().then(showOptions).catch(() => {}); all = DATASETS[pick.data].count || 0; }
    const n = find && pick.weak ? Math.min(20, all) : all, secs = n * pace;
    $("paceTotal").textContent = `${r.name}: ${n} × ${pace} s = ${Math.floor(secs / 60)}:${String(secs % 60).padStart(2, "0")}`;
    $("regionSummary").textContent = `${r.name} · ${all}`;
    const parts = [find && pick.weak ? "Knowledge gaps" : "", pick.timer && pick.mode !== "explore" ? `Timer ${pace} s` : ""].filter(Boolean);
    $("optBadge").hidden = !parts.length; $("optBadge").textContent = parts.length; // options switched on
    $("optBtn").setAttribute("aria-label", parts.length ? `Options: ${parts.join(", ")}` : "Options");
  }
  // the Learning mode tab goes straight to the Learning globe
  $("setupTabs").addEventListener("click", e => {
    const b = e.target.closest("button");
    if (b && b.dataset.v === "learn") { closeSetup(); closeInset(); startGame("explore", "world", "globe", "world"); }
  });
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
    S.weak = pick.weak; S.timer = pick.timer; S.paceFind = pick.paceFind; S.paceName = pick.paceName; S.cd = !!pick.cd; S.ut = pick.ut !== false;
    startGame(pick.mode, pick.region, pick.region === "world" ? pick.view : "flat", pick.data);
  };

  // switch between the world and US states maps (US data loads the first time it's needed)
  async function useData(data) {
    if (isCountryMap(data)) await DATASETS[data].load();
    S.data = data;
    geo = geoFor(data);
    const style = isCountryMap(data) ? DATASETS[data].style : "patterson";
    main.setGeo(geo, style);
    if (insetView) insetView.setGeo(geo, style);
    GG.debug.geo = geo;
  }
  function startGame(mode, region, view, data = S.data) {
    // Learning mode's whole UK & Ireland is the countries view (no county lines); counties come after "Focus on ..."
    if (mode === "explore" && (data === "uk" || data === "ukc") && (region === "uk" || region === "ukc")) { data = "ukn"; region = "ukn"; }
    if (data !== S.data || !geo) return useData(data).then(() => startGame(mode, region, view, data));
    // a country map's own regions (England, Scotland...), or else the whole map
    if (isCountryMap(data)) { if (dataOfRegion(region) !== data) region = DATASETS[data].region; view = "flat"; }
    S.mode = mode; S.region = region;
    savePrefs({ game: { mode, region, data, cd: !!S.cd, ut: S.ut !== false, weak: !!S.weak, timer: !!S.timer, paceFind: S.paceFind || 5, paceName: S.paceName || 10 },
      ...(region === "world" ? { worldView: view } : {}) });
    // region games are cropped to the region; the jump bar is swapped for a "Whole region" button
    main.setCrop(region === "world" ? null : REGIONS[region].crop);
    $("jumpbar").hidden = region !== "world" || mode === "nameflag"; // no map in Name the flags
    $("regionBtn").hidden = region === "world" || mode === "explore"; // no "Whole US" in Learning mode
    $("magBtn").hidden = mode === "explore"; // no magnifier in Learning mode
    if (mode === "explore" && S.magnify) setMag(false);
    $("regionBtn").textContent = data === "us" ? "Whole US" : data === "ca" ? "Whole Canada" : data === "in" ? "Whole India" : data === "cn" ? "Whole China" : region === DATASETS[data].region ? "Whole map" : isCountryMap(data) ? `Whole of ${REGIONS[region].name}` : "Whole region";
    $("viewBtn").hidden = region !== "world"; // no globe for region games
    $("worldBtn").hidden = !(mode === "explore" && isCountryMap(data)); // back from Focus on a country
    $("worldBtn").textContent = data === "uk" || data === "ukc" ? "‹ UK & Ireland" : "‹ World map"; // counties -> countries view
    // Britain and Ireland's Learning map: switch between the two county sets
    // Britain and Ireland: the sources' credit lines (required by their licences), on the map in every UK game
    const ukMap = data === "uk" || data === "ukc" || data === "ukn";
    $("mapCredit").hidden = !ukMap;
    if (ukMap) $("mapCredit").innerHTML = (data !== "ukc"
      ? 'Counties: <a href="https://www.county-borders.co.uk" target="_blank" rel="noopener">Historic County Borders Project</a>'
      : "Contains OS data © Crown copyright and database right 2026") +
      '. Ireland © <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener">OpenStreetMap</a> contributors. Flags: UK Flag Registry.';
    const ukLearn = mode === "explore" && (data === "uk" || data === "ukc");
    $("setBtn").hidden = !ukLearn;
    if (ukLearn) $("setBtn").textContent = data === "uk" ? "Ceremonial counties" : "Historic counties";
    if (main.mode !== view) { main.setMode(view); setViewButton(); }
    goTo(region, false);
    hideLearnCard();
    $("reviewBar").hidden = true; reviewSel = null;
    showTimeline(mode === "explore" && data === "us");
    useSub(mode === "explore" && data === "world");
    showReserves();
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
      isTarget: c => c === target, isActive: inRegion, isOpen, showCapital, isUnformed });
    main.lookAt(15, 25, 120, false);
    buildRegionButtons();
    GG.debug = { main, geo, startGame, inset: () => insetView, get geoUS() { return geoUS; }, get geoCA() { return geoCA; } };
    setViewButton();
    // testing hooks: ?region=europe&view=flat starts that game; ?at=lon,lat,span and ?terrain=1 adjust the view
    if (REGIONS[q.get("region")] || q.get("view") || q.get("data")) {
      const region = REGIONS[q.get("region")] ? q.get("region") : "world";
      startGame("find", region, region === "world" ? q.get("view") || "globe" : "flat", isCountryMap(q.get("data")) ? q.get("data") : "world");
    } else {
      // reopen where you left off: your last game starts behind the New game screen, ready to go
      if (prefs.borders === false) setBorders(false);
      if (prefs.terrain) setTerrainOn(true);
      const g = prefs.game || {};
      S.weak = !!g.weak; S.cd = !!g.cd; S.ut = g.ut !== false; S.timer = !!g.timer; S.paceFind = g.paceFind || 5; S.paceName = g.paceName || 10;
      const region = REGIONS[g.region] ? g.region : "world";
      const mode = ["find", "name", "findcap", "namecap", "findflag", "nameflag", "explore"].includes(g.mode) ? g.mode : "find";
      const ready = startGame(mode, region, region === "world" ? (prefs.worldView === "flat" ? "flat" : "globe") : "flat", isCountryMap(g.data) ? g.data : "world");
      Promise.resolve(ready).then(openSetup); // first screen: choose a game
    }
    if (q.get("terrain")) $("terrainBtn").click();
    if (q.get("at")) { const [lo, la, sp] = q.get("at").split(",").map(Number); main.lookAt(lo, la, sp, false); }
    GG.onSplashGone = () => { main.requestDraw(); if (resAfterSplash) { resAfterSplash = false; showReserves(); } };
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
