// Game logic and screen wiring. Build 1: game 1 (Find the country) for the whole world, one continent
// or the Caribbean, plus Free tap. Game modes and regions are kept separate so more can be added (PLAN.md).
(function () {
  const GG = window.GG;
  const $ = id => document.getElementById(id);

  // data: "world" (countries), or a country map: "us" (US states, build 3), "ca" (Canada's provinces and territories),
  // "uk" / "ukc" (Britain and Ireland's historic or ceremonial counties, build 4). cd: Crown Dependencies in UK games.
  const S = { mode: "find", region: "world", magnify: false, data: "world", cd: false };
  let geoWorld = null, geoUS = null, geoCA = null, geoIN = null, geoCN = null, geoRU = null, geoAU = null, geoMX = null, geoBR = null, geoDE = null, geoJP = null, geoFR = null, geoIT = null, geoES = null, geoESP = null, geoNG = null, geoAR = null;
  const geoC = {}; // the maps built by tools/build_country.py (NEW_MAPS below), by dataset code
  const geoAP = {}; // airport sets, by dataset key
  let apCodes = [], apRegion = "world"; // the airports in this airport game (a random pick: startAirports), and its region
  const apShown = new Set(); // airports whose dot the hint has shown (Location dots off)
  const apTries = new Map(); // Name the code: wrong tries per airport (two allowed)
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
    // Russia: 83 federal subjects (all called "oblasts" in the menus; the card shows each one's real kind), every one with a flag
    // Mexico: 31 states and Mexico City; games 5 and 6 use the coats of arms (most states have no official flag)
    mx: { noun: "state", nouns: "states", Nouns: "States", region: "mexico", style: "mexico", count: 32, emblem: "coat of arms",
      emblems: "coats of arms", load: async () => (geoMX = geoMX || await GG.loadMX(geoWorld.lakes)) },
    // Airport codes (Misc_games.md): the world map with a dot per airport, the airports a random pick from a pot (the
    // airport options: Easy, Hard or Capitals, and the region); `world` (not a country map: globe and flat, continents
    // as regions); `prompted` Name games ask one airport at a time. name = code, capital = city.
    ap: { noun: "airport", nouns: "airports", Nouns: "Airports", world: true, prompted: true, noFlags: true, count: 0,
      cap: "city", caps: "cities", load: async () => {
        const A = await GG.airportData();
        return (geoAP.ap = await GG.loadAirports(geoWorld, apCodes, code => apPlace(A, code, apRegion)));
      } },
    // Argentina: 23 provinces and the City of Buenos Aires, all with flags (no Falklands)
    ar: { noun: "province", nouns: "provinces", Nouns: "Provinces", region: "argentina", style: "argentina", count: 24,
      load: async () => (geoAR = geoAR || await GG.loadAR(geoWorld.lakes)) },
    // Nigeria: 36 states and the Federal Capital Territory; no flag games (state flags are mostly unofficial; seals shelved)
    ng: { noun: "state", nouns: "states", Nouns: "States", region: "nigeria", style: "nigeria", count: 37, noFlags: true,
      load: async () => (geoNG = geoNG || await GG.loadNG(geoWorld.lakes)) },
    // Spain: two sets, like the UK's: the communities (17 and the 2 cities, with flags) and the provinces (50 and the 2 cities)
    es: { noun: "community", nouns: "communities", Nouns: "Communities", region: "spain", style: "spain", count: 19,
      load: async () => (geoES = geoES || await GG.loadES(geoWorld.lakes)) },
    esp: { noun: "province", nouns: "provinces", Nouns: "Provinces", region: "spainp", style: "spain", count: 52, noFlags: true,
      load: async () => (geoESP = geoESP || await GG.loadESP(geoWorld.lakes)) },
    // Italy: 20 regions, all with flags; Vatican City and San Marino as circles in Learning mode only
    it: { noun: "region", nouns: "regions", Nouns: "Regions", region: "italy", style: "italy", count: 20,
      load: async () => (geoIT = geoIT || await GG.loadIT(geoWorld.lakes)) },
    // France: the 13 metropolitan regions; no flag games (most regions have only a logo)
    fr: { noun: "region", nouns: "regions", Nouns: "Regions", region: "france", style: "france", count: 13, noFlags: true,
      load: async () => (geoFR = geoFR || await GG.loadFR(geoWorld.lakes)) },
    // Japan: 47 prefectures, all with flags
    jp: { noun: "prefecture", nouns: "prefectures", Nouns: "Prefectures", region: "japan", style: "japan", count: 47,
      load: async () => (geoJP = geoJP || await GG.loadJP(geoWorld.lakes)) },
    // Germany: 16 states, all with flags
    de: { noun: "state", nouns: "states", Nouns: "States", region: "germany", style: "germany", count: 16,
      load: async () => (geoDE = geoDE || await GG.loadDE(geoWorld.lakes)) },
    // Brazil: 26 states and the Federal District, all with flags
    br: { noun: "state", nouns: "states", Nouns: "States", region: "brazil", style: "brazil", count: 27,
      load: async () => (geoBR = geoBR || await GG.loadBR(geoWorld.lakes)) },
    // Australia: 6 states, 2 mainland territories and Jervis Bay (no capital and no flag: left out of those games)
    au: { noun: "state or territory", nouns: "states and territories", Nouns: "States & territories", region: "australia",
      style: "australia", count: 9, load: async () => (geoAU = geoAU || await GG.loadAU(geoWorld.lakes)) },
    ru: { noun: "oblast", nouns: "oblasts", Nouns: "Oblasts", region: "russia", style: "russia", count: 83,
      load: async () => (geoRU = geoRU || await GG.loadRU(geoWorld.lakes)) },
    // Britain and Ireland: the parts are counties, and county towns stand in for capitals
    uk: { noun: "county", nouns: "counties", Nouns: "Counties", cap: "county town", caps: "county towns", region: "uk", style: "uk",
      set: "Historic", load: async () => (geoUK.uk = geoUK.uk || await GG.loadUK("historic", geoWorld.lakes)) },
    ukc: { noun: "county", nouns: "counties", Nouns: "Counties", cap: "county town", caps: "county towns", region: "ukc", style: "uk",
      set: "Ceremonial", load: async () => (geoUK.ukc = geoUK.ukc || await GG.loadUK("ceremonial", geoWorld.lakes)) },
    // Learning mode's view of the UK and Ireland: just the five countries, each with a card and "Focus on ..." to its counties
    ukn: { noun: "country", nouns: "countries", Nouns: "Countries", region: "ukn", style: "uk",
      load: async () => (geoUK.ukn = geoUK.ukn || await GG.loadUKNations(geoWorld.lakes)) },
  };
  // The country maps built by tools/build_country.py (jobs/overnight_v2.md): one row each, one loader
  // (GG.loadCountry) and one Learning card (showCountryCard). `special`: the card's country-specific fact (`specials`: several, [label, fact key]); `set`: the
  // dataset that's the other set of the same country (Belgium's provinces and regions); `sub`: a second set, not
  // listed on its own in the Countries tab.
  const NEW_MAPS = {
    at: { a3: "AUT", name: "Austria", noun: "state", nouns: "states", Nouns: "States", style: "austria", count: 9, lang: "German", special: "Ski resorts and peaks" },
    cz: { a3: "CZE", name: "Czechia", noun: "region", nouns: "regions", Nouns: "Regions", style: "czechia", count: 14, lang: "Czech", special: "Historic land" },
    pl: { a3: "POL", name: "Poland", noun: "voivodeship", nouns: "voivodeships", Nouns: "Voivodeships", style: "poland", count: 16, lang: "Polish", special: "Before 1918" },
    // the Netherlands: land areas (the provinces' totals include the IJsselmeer and the Wadden Sea)
    nl: { a3: "NLD", name: "Netherlands", noun: "province", nouns: "provinces", Nouns: "Provinces", style: "netherlands", count: 12, lang: "Dutch",
      landArea: true, special: "Land from the sea" },
    // Belgium: two sets, like Spain's: the 10 provinces and Brussels, and the 3 regions (flags in data/flags/be/)
    be: { a3: "BEL", name: "Belgium", noun: "province", nouns: "provinces", Nouns: "Provinces", style: "belgium", count: 11,
      special: "Language community", set: "ber" },
    ber: { a3: "BEL", name: "Belgium", noun: "region", nouns: "regions", Nouns: "Regions", style: "belgium", region: "belgiumr", count: 3,
      special: "Language community", set: "be", sub: true, flagDir: "be" },
    // Sweden: games 5 and 6 use the county coats of arms
    se: { a3: "SWE", name: "Sweden", noun: "county", nouns: "counties", Nouns: "Counties", style: "sweden", count: 21, lang: "Swedish", emblems: true,
      specials: [["Historic land", "land"], ["Sámi area", "sami"], ["Swedish invention", "invention"]] },
    // South Africa: no flag games (no official provincial flags); Lesotho and Eswatini drawn in their own colours, in Learning mode
    za: { a3: "ZAF", name: "South Africa", noun: "province", nouns: "provinces", Nouns: "Provinces", style: "southafrica", count: 9, cont: "Africa",
      noFlags: true, lang: "the main local language", specials: [["Home languages", "langs"], ["Wildlife", "wildlife"], ["Before 1994", "before"]] },
    // New Zealand: the 16 regions and the Chatham Islands (moved across the date line, with an oval); no flag games
    nz: { a3: "NZL", name: "New Zealand", noun: "region", nouns: "regions", Nouns: "Regions", style: "newzealand", count: 17, cont: "Oceania",
      noFlags: true, lang: "Māori", specials: [["Māori name and iwi", "maori"], ["Island", "island"], ["Film location", "film"]] },
    // Portugal: 18 districts and the Azores and Madeira (in insets); no games 5 and 6 (the districts have no arms of their own)
    pt: { a3: "PRT", name: "Portugal", noun: "district", nouns: "districts", Nouns: "Districts", style: "portugal", count: 20, noFlags: true,
      lang: "Portuguese", specials: [["Wine region", "wine"], ["Historic province", "province"], ["Age of Discovery", "discovery"]] },
    // Colombia: 32 departments and Bogotá (a circle); San Andrés in an inset; flag games
    co: { a3: "COL", name: "Colombia", noun: "department", nouns: "departments", Nouns: "Departments", style: "colombia", count: 33, cont: "South America",
      lang: "Spanish", specials: [["Natural region", "region"], ["Famous crop", "crop"], ["Music", "music"]] },
    // Switzerland: 26 cantons, flag games; circles for Basel-Stadt, Appenzell Innerrhoden and Zug
    ch: { a3: "CHE", name: "Switzerland", noun: "canton", nouns: "cantons", Nouns: "Cantons", style: "switzerland", count: 26,
      lang: "the local language", specials: [["Language", "language"], ["Joined the Confederation", "joined"], ["Cheese or chocolate", "cheese"]] },
    // Chile: 16 regions, flag games; Easter Island (enlarged) and the Juan Fernández Islands in insets
    cl: { a3: "CHL", name: "Chile", noun: "region", nouns: "regions", Nouns: "Regions", style: "chile", count: 16, cont: "South America",
      lang: "Spanish", specials: [["Climate", "climate"], ["Wine valley or mine", "valley"], ["Indigenous peoples", "peoples"]] },
    // Malaysia: 13 states and 3 federal territories; East Malaysia in an inset below the peninsula; flag games
    my: { a3: "MYS", name: "Malaysia", noun: "state", nouns: "states and territories", Nouns: "States", style: "malaysia", count: 16, cont: "Asia",
      lang: "Malay", specials: [["Ruler", "ruler"], ["Main ethnic groups", "ethnic"], ["Peninsula or Borneo", "half"]] },
    // South Korea: 16 divisions (Gwangju and South Jeolla merged in July 2026); Hangul names on the cards; Dokdo dotted
    kr: { a3: "KOR", name: "South Korea", noun: "province", nouns: "provinces and cities", Nouns: "Provinces & cities", style: "southkorea", count: 16,
      cont: "Asia", lang: "Korean (Hangul)", specials: [["Famous food", "food"], ["Historic kingdom", "kingdom"]] },
    // Peru: 24 departments, Lima Province and Callao (circles for both); flag games
    pe: { a3: "PER", name: "Peru", noun: "department", nouns: "departments", Nouns: "Departments", style: "peru", count: 26, cont: "South America",
      lang: "Spanish", specials: [["Natural region", "region"], ["Ancient civilisation", "civ"], ["Quechua or Aymara", "quechua"]] },
    // Egypt: 27 governorates; games 5 and 6 use flags, or the emblem where there is no flag; Arabic names; Hala'ib dotted, Bir Tawil grey
    eg: { a3: "EGY", name: "Egypt", noun: "governorate", nouns: "governorates", Nouns: "Governorates", style: "egypt", count: 27, cont: "Africa",
      emblem: "flag or emblem", emblems: "flags and emblems", lang: "Arabic", specials: [["Part of Egypt", "part"], ["Ancient sites", "sites"]] },
  };
  Object.entries(NEW_MAPS).forEach(([d, m]) => {
    DATASETS[d] = { noun: m.noun, nouns: m.nouns, Nouns: m.Nouns, region: m.region || m.style, style: m.style, count: m.count,
      noFlags: !!m.noFlags, ...(m.emblems ? { emblem: m.emblem || "coat of arms", emblems: typeof m.emblems === "string" ? m.emblems : "coats of arms" } : {}),
      load: async () => (geoC[d] = geoC[d] || await GG.loadCountry(d, geoWorld.lakes, m.flagDir)) };
  });
  // countries with two sets of parts: the Set switch on the country page, and in Learning mode
  const SETS = { es: ["es", "esp"], esp: ["es", "esp"] };
  Object.entries(NEW_MAPS).forEach(([d, m]) => { if (m.set) SETS[d] = m.sub ? [m.set, d] : [d, m.set]; });
  const isCountryMap = d => !!DATASETS[d] && d !== "world" && !DATASETS[d].world;
  const isAirports = (d = S.data) => !!(DATASETS[d] && DATASETS[d].world);
  // Name games that ask one at a time (airports): the next one is chosen for you, and the arrows skip
  const prompted = () => !!(DATASETS[S.data] && DATASETS[S.data].prompted) && isName();
  const geoFor = d => (DATASETS[d] && DATASETS[d].world ? geoAP[d] : d === "us" ? geoUS : d === "ca" ? geoCA : d === "in" ? geoIN : d === "cn" ? geoCN : d === "ru" ? geoRU : d === "au" ? geoAU : d === "mx" ? geoMX : d === "br" ? geoBR : d === "de" ? geoDE : d === "jp" ? geoJP : d === "fr" ? geoFR : d === "it" ? geoIT : d === "es" ? geoES : d === "esp" ? geoESP : d === "ng" ? geoNG : d === "ar" ? geoAR : geoC[d] || geoUK[d] || (DATASETS[d] && d !== "world" ? null : geoWorld)); // null until loaded
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
    // (History games: down to 11 px, so a long battle name is always readable in full on its two lines)
    const minTwo = S.mode === "hist" && el.id === "target" ? 11 : 13;
    while ((wide() || el.scrollHeight > size * 1.1 * 2 + 2) && size > minTwo) { size -= 1; el.style.fontSize = size + "px"; }
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
    russia:   { name: "Russia", us: true, test: () => true },
    australia: { name: "Australia", us: true, test: () => true },
    mexico:   { name: "Mexico", us: true, test: () => true },
    brazil:   { name: "Brazil", us: true, test: () => true },
    germany:  { name: "Germany", us: true, test: () => true },
    japan:    { name: "Japan", us: true, test: () => true },
    france:   { name: "France", us: true, test: () => true },
    // Italy: the enclaves (Vatican City, San Marino) are independent countries, so only in Learning mode
    italy:    { name: "Italy", us: true, test: c => !c.info.enclave || S.mode === "explore" },
    spain:    { name: "Spain", us: true, test: () => true },
    nigeria:  { name: "Nigeria", us: true, test: () => true },
    argentina: { name: "Argentina", us: true, test: () => true },
    spainp:   { name: "Spain (provinces)", us: true, data: "esp", test: () => true },
    // Britain and Ireland, for each county set (added below): the whole map, England, Scotland, Wales and Ireland
    oceania:  { name: "Oceania",       test: c => c.cont.includes("Oceania"),       view: { globe: [167, -16, 74.3],   flat: [167, -16, 74.3] },   crop: [[110, -50], [212, 22]] },
  };
  // Britain and Ireland's regions, for both county sets. The Crown Dependencies are only in the whole-map games, when
  // switched on (and always in Learning mode).
  Object.entries(NEW_MAPS).forEach(([d, m]) => {
    // (enclaves, independent countries drawn on the map: Learning mode only, like Italy's)
    REGIONS[m.region || m.style] = { name: m.name + (m.sub ? ` (${m.nouns})` : ""), us: true, data: d,
      test: c => !c.info.enclave || S.mode === "explore" };
  });
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
  const inRegion = c => (S.region === "world" || REGIONS[S.region].test(c)) && !(tlOn() && c.info && c.info.year > tlYear)
    && !(flags() && c.info && c.info.flag === false) && !(caps() && !c.capitals.length);
  const regionCountries = () => geo.countries.filter(inRegion);

  // Games: find = Find the country, name = Name the countries, findcap = Find the country by its capital,
  // namecap = Name the capitals, explore = Free tap
  const isFind = () => S.mode === "find" || S.mode === "findcap" || S.mode === "findflag";
  const isName = () => S.mode === "name" || S.mode === "namecap" || S.mode === "nameflag";
  const caps = () => S.mode === "findcap" || S.mode === "namecap";
  const flags = () => S.mode === "findflag" || S.mode === "nameflag";
  // what games 5 and 6 show: flags, or coats of arms (Mexico)
  const emblem = (d = S.data) => (DATASETS[d] && DATASETS[d].emblem) || "flag";
  const emblems = (d = S.data) => (DATASETS[d] && DATASETS[d].emblems) || "flags";
  // flag image (the single-page test build carries the flags inside the page, in window.GG_FLAGS)
  const flagSrc = c => {
    const key = c.flagKey || c.iso; // states and provinces have their own folder (us/, ca/)
    return (window.GG_FLAGS && window.GG_FLAGS[key]) || `data/flags/${key}.webp`;
  };
  const capital = c => c.capitals[0] || "";
  const label = c => (c.dot ? `${c.code}: ${c.info.full}` : caps() ? `${c.name}: ${capital(c)}` : c.name);
  let selected = null;   // naming games: the country whose name or capital is being typed
  // statehood timeline (US Learning mode): the year shown; states that join that year are highlighted
  let tlYear = 1959, tlTimer = null, tlKind = "us";
  // a statehood-style timeline (US, Australia) is showing a year before its end
  const TL_MAX = { us: 1959, au: 1915, br: 1988, ru: 2023 };
  const tlOn = () => tlKind !== "ru" && tlYear < TL_MAX[tlKind];
  const isUnformed = c => tlOn() && !!c.info && c.info.year > tlYear;
  const tlBorders = new Map(); // year -> borders that existed then (between two states, or a state and land not yet a state)
  // reviewing a finished game: the tapped country is shown in dark green (right), dark red (missed) or blue
  const getState = c => (flashing[c.iso] ? "flash" : finished && c === reviewSel ? (state[c.iso] === "good" ? "goodSel" : state[c.iso] === "bad" ? "badSel" : "sel")
    : c === selected ? "sel" : state[c.iso] ||
    (tlOn() && c.info && c.info.year === tlYear ? "sel" : null));
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
    apShown.clear(); apTries.clear(); apHintFor = null;
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
    if (!(isFind() || prompted()) || order.length < 2) return;
    idx = (idx + d + order.length) % order.length;
    if (prompted()) { selected = order[idx]; $("nameInput").value = ""; }
    show();
  }
  function show() {
    const mode = S.mode, where = S.region === "world" ? "" : " · " + REGIONS[S.region].name;
    target = isFind() && !finished ? order[idx] || null : null;
    // airports' Name games: always asking one (the next is chosen for you)
    if (prompted() && !finished && order.length && !order.includes(selected)) { idx = Math.min(idx, order.length - 1); selected = order[idx]; }
    const t = $("target"); t.className = "target";
    const typing = isName() && !flags() && selected && !finished;
    // Find by flag shows the flag instead of a name
    $("targetFlag").hidden = !(S.mode === "findflag" && target);
    if (S.mode === "findflag" && target) { $("targetFlag").src = flagSrc(target); $("targetFlag").alt = `Which ${noun()} has this flag?`; }
    $("prev").hidden = $("fwd").hidden = !(isFind() || prompted()) || finished;
    $("hintBtn").hidden = !isAirports() || finished || S.mode === "explore";
    showApBig();
    // the airport Name games: the typing box goes on its own row at the bottom of the banner, under the prompt
    // (Name the code: it goes under the airport's name, in the middle of the screen)
    const bar = document.querySelector(".bar"), inp = $("nameInput"), big = !$("apBig").hidden, wide = prompted() && !big;
    const home = big ? $("apBigInput") : wide ? bar : document.querySelector(".prompt");
    if (inp.parentNode !== home) home.appendChild(inp);
    bar.classList.toggle("wideinput", wide);
    $("nameInput").placeholder = isAirports() ? (caps() ? "Type the city" : "Type the code")
      : caps() ? `Capital of ${selected ? selected.name : ""}` : "Type the name";
    $("giveup").hidden = mode === "explore" || mode === "earth";
    $("nameInput").hidden = !typing;
    // ✕ closes the box in the tap-any-country Name games; the airport games always ask one, so it isn't shown there
    $("nameClose").hidden = !typing || prompted();
    t.hidden = typing && !prompted();
    if (typing && prompted()) t.textContent = caps() ? selected.code : "What's its code?"; // (Name the code: the airport is in big letters below)
    resetGiveUp();
    if (mode === "earth") {
      $("eyebrow").textContent = "Earth";
      t.textContent = "Tap anything";
      $("score").textContent = "Plates, volcanoes, seas… tap one to learn about it. Layers: top right.";
    } else if (mode === "explore") {
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
        if (prompted() && selected) setTimeout(keepSelectedInView, 50);
        $("score").innerHTML = `<b>${nGood}</b> / ${total} named` + (nBad ? ` <span class="wrong">· ${nBad} wrong</span>` : "");
      }
    } else if (finished) {
      $("eyebrow").textContent = "Finished" + where;
      t.textContent = `${nGood} of ${total} right`;
      $("score").innerHTML = `<b>${nGood}</b> / ${total} <span class="wrong">· ${nBad} wrong</span> · tap any ${noun()} to see it`;
      $("giveup").textContent = "Play again";
    } else {
      $("eyebrow").textContent = (S.mode === "findflag" ? `Find by ${emblem()}` : caps() ? `Find by ${capWord()}` : "Find") + where + (S.weak ? " · knowledge gaps" : "");
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
      if (res) toast(`${res.properties.n} · ${RES_KIND[res.properties.k] || res.properties.k || ""}`, 3000);
      // world Learning map zoomed into the US: a tap on a state shows the state
      const f = c.iso === "USA" && view.sub && view.lastTap ? view.subAt(view.lastTap[0], view.lastTap[1]) : null;
      selectSub(f);
      flashName(f ? f.c : c);
      if (!f) state[c.iso] = "flash";
      showLearnCard(f ? f.c : c);
      if (view.lastDispute) addDisputeToCard(view.lastDispute); // (Kashmir in India, Crimea in Ukraine: the card and the dispute)
      showFocus(c);
      redraw(); return;
    }
    if (finished) { reviewSel = c; flashName(c); redraw(); return; } // reviewing: tap any country to see its name (or capital)
    if (isName()) { tapName(c, view); return; }
    if (!target || state[c.iso] === "good" || state[c.iso] === "bad") return; // already-correct (green) and missed (red) countries do nothing
    // the next country appears instantly; the map keeps the green/red result
    GG.Stats.answer(S.mode, target.iso, c === target);
    if (c === target) { state[c.iso] = "good"; nGood++; }
    else {
      state[target.iso] = "bad"; nBad++;
      flashing[c.iso] = true; // the tapped country flashes yellow once
      setTimeout(() => { delete flashing[c.iso]; redraw(); }, 450);
      toast(isAirports() ? `Missed: ${target.code} is ${target.info.full}` : S.mode === "findflag" ? `Missed: that was the ${emblem()} of ${target.name}` : caps() ? `Missed: ${capital(target)} is in ${target.name}` : "Missed: " + target.name,
        caps() || S.mode === "findflag" ? 2400 : 1800);
    }
    if (inset && view === inset) closeInset();
    next();
  }

  // ---------- airport games: the hint (no penalty), and Name the code's plain screen ----------
  const AP_NEAR = 100; // km: Find the airport with no dots, a tap this close counts
  let apHintFor = null;
  // the airport being asked: Find's target, or the Name games' selected one
  const apAsked = () => (S.mode === "find" ? target : selected);
  $("hintBtn").onclick = () => {
    const c = apAsked(); if (!c || finished) return;
    if (S.mode === "name") { apHintFor = c; showApBig(); return; }   // Name the code: its first letter
    // Find / Name the city: zoom to the area (a generous frame, a little off-centre so it doesn't give it away)
    const span = 12, jx = (Math.random() - 0.5) * span * 0.5, jy = (Math.random() - 0.5) * span * 0.5;
    main.fitBox([[c.anchor[0] + jx - span / 2, c.anchor[1] + jy - span / 2], [c.anchor[0] + jx + span / 2, c.anchor[1] + jy + span / 2]]);
    if (S.mode === "namecap") apShown.add(c); // Name the city: show its dot
    redraw();
  };
  // the Europe inset: each island group's land (moved like its airports) inside a frame, with its name
  async function apInsetDrawer() {
    const A = await GG.airportData();
    const groups = AP_INSETS.filter(g => apCodes.some(c => insetOf(A.airports[c].l) === g));
    if (!groups.length) return null;
    const move = (g, c) => (typeof c[0] === "number" ? [c[0] + g.shift[0], c[1] + g.shift[1]] : c.map(x => move(g, x)));
    const parts = groups.map(g => {
      const polys = [];
      geoWorld.f50.filter(f => f.c && (f.c.iso === "ESP" || f.c.iso === "PRT")).forEach(f => {
        const ps = f.geometry.type === "MultiPolygon" ? f.geometry.coordinates : [f.geometry.coordinates];
        ps.forEach(p => { const ll = d3.geoCentroid({ type: "Polygon", coordinates: p }); if (insetOf(ll) === g) polys.push(move(g, p)); });
      });
      const [w, s0, e, n] = g.box, pad = 0.3, W = w + g.shift[0] - pad, E = e + g.shift[0] + pad, S0 = s0 + g.shift[1] - pad, N = n + g.shift[1] + pad;
      const frame = { type: "LineString", coordinates: [[W, S0], [W, N], [E, N], [E, S0], [W, S0]] };
      return { g, land: { type: "MultiPolygon", coordinates: polys }, frame, label: [W + 0.2, N - 0.2] };
    });
    return (ctx, pt, proj) => {
      const path = d3.geoPath(proj, ctx), col = main.col;
      parts.forEach(p => {
        ctx.beginPath(); path(p.land); ctx.fillStyle = col.land; ctx.fill(); ctx.lineWidth = 0.8; ctx.strokeStyle = col.coast; ctx.stroke();
        ctx.beginPath(); path(p.frame); ctx.lineWidth = 1.2; ctx.setLineDash([5, 3]); ctx.strokeStyle = col.border; ctx.stroke(); ctx.setLineDash([]);
        const q = pt(p.label); if (!q) return;
        ctx.font = "600 10px Barlow, system-ui, sans-serif"; ctx.textAlign = "left"; ctx.textBaseline = "top";
        ctx.fillStyle = col.fg; ctx.fillText(p.g.name, q[0], q[1]);
      });
    };
  }
  function showApBig() {
    const on = isAirports() && S.mode === "name" && !finished && !!selected;
    $("apBig").hidden = !on;
    document.querySelector(".mapctl").classList.toggle("overbig", on); // just the lightbulb, above the plain screen
    if (!on) return;
    $("apBigName").textContent = selected.info.full;
    $("apBigSub").textContent = selected.info.city;
    $("apBigHint").textContent = apTries.get(selected) ? "1 attempt left" + (apHintFor === selected ? ` · starts with ${selected.code[0]}` : "")
      : apHintFor === selected ? `Starts with ${selected.code[0]}` : "";
    if (document.activeElement !== $("nameInput") && !overlayOpen() && document.hasFocus()) setTimeout(() => $("nameInput").focus(), 0); // the keyboard stays open
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
    if (isAirports() && !S.apDots) return; // (the dots are hidden: moving the map would give the airport away)
    if (!selected || !main.visible(selected.anchor)) return;
    const p = main.projection()(selected.anchor);
    if (p[0] < 20 || p[0] > main.w - 20 || p[1] < 20 || p[1] > main.h - 20) {
      main.lookAt(selected.anchor[0], selected.anchor[1], Math.min(main.w, main.h) * 0.9 / main.pxPerDeg());
    }
  }
  $("nameInput").addEventListener("input", () => {
    const typed = $("nameInput").value, match = selected && GG.nameMatches(selected, typed, caps() ? "capitals" : "names");
    // Name the code: three letters that aren't its code (or its city's code) are wrong: a red flash, and try again
    // (two tries: the first wrong one says "1 attempt left"; the second marks it wrong and moves on)
    if (!match && isAirports() && S.mode === "name" && selected && /^[a-z]{3}$/i.test(typed.trim())) {
      const inp = $("nameInput"), c = selected;
      inp.classList.remove("wrongflash"); void inp.offsetWidth; inp.classList.add("wrongflash");
      apTries.set(c, (apTries.get(c) || 0) + 1);
      if (apTries.get(c) < 2) {
        $("apBigHint").textContent = "1 attempt left";
        setTimeout(() => { inp.classList.remove("wrongflash"); inp.value = ""; }, 450);
        return;
      }
      GG.Stats.answer(S.mode, c.iso, false);
      state[c.iso] = "bad"; nBad++;
      toast(`Missed: ${c.info.full} is ${c.code}`, 2600);
      order = order.filter(o => o !== c); selected = null;
      setTimeout(() => { inp.classList.remove("wrongflash"); inp.value = ""; if (!order.length) { inp.blur(); finish(); } else show(); }, 450);
      return;
    }
    if (!match) return; // no reaction until it's right
    // accepted with a typo: show how it was typed and how it's spelled
    if (!match.exact) toast(`You typed “${typed.trim()}” — it's spelled “${match.name}”`, 4000);
    state[selected.iso] = "good"; nGood++;
    order = order.filter(c => c !== selected);
    selected = null;
    $("nameInput").value = "";
    if (!prompted()) $("nameInput").blur();
    if (!order.length) { $("nameInput").blur(); finish(); return; }
    show();
    if (prompted()) $("nameInput").focus();
  });
  $("nameInput").addEventListener("keydown", e => { if (e.key === "Escape") { e.preventDefault(); closeName(); } });
  // Name the code: keep the keyboard open (tapping elsewhere doesn't close it while the game is on)
  const overlayOpen = () => !$("setup").hidden || !$("stats").hidden || !$("results").hidden;
  $("nameInput").addEventListener("blur", () => {
    // (only while the page itself has focus: otherwise, e.g. switching apps, focus can't stick and this would loop)
    setTimeout(() => { if (!$("apBig").hidden && !overlayOpen() && document.hasFocus()) $("nameInput").focus(); }, 0);
  });
  function closeName() { selected = null; $("nameInput").blur(); show(); }
  $("nameClose").onclick = closeName;
  window.addEventListener("resize", () => setTimeout(keepSelectedInView, 50));

  // Give up: tap once to arm, again to confirm; the rest are shown in red
  let giveUpTimer;
  function resetGiveUp() { clearTimeout(giveUpTimer); const b = $("giveup"); b.classList.remove("confirm"); b.textContent = "Give up"; }
  $("giveup").onclick = () => {
    if (S.mode === "hist") { GG.History.giveUp(); return; }
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
    if (main && main.selDispute) { main.selDispute = null; main.requestDraw(); } // (a disputed territory's grey highlight goes)
    $("lcMoreBtn").hidden = false; // (a timeline card hides it)
    $("lcFlag").hidden = false; // (a county with no flag hides it)
    if (geoUS && geoUS.byIso[c.iso] === c) { showStateCard(c, i); return; }
    if (geoCA && geoCA.byIso[c.iso] === c) { showProvinceCard(c, i); return; }
    if (geoIN && geoIN.byIso[c.iso] === c) { showIndiaCard(c, i); return; }
    if (geoCN && geoCN.byIso[c.iso] === c) { showChinaCard(c, i); return; }
    if (geoRU && geoRU.byIso[c.iso] === c) { showRussiaCard(c, i); return; }
    if (geoAU && geoAU.byIso[c.iso] === c) { showAustraliaCard(c, i); return; }
    if (geoMX && geoMX.byIso[c.iso] === c) { showMexicoCard(c, i); return; }
    if (geoBR && geoBR.byIso[c.iso] === c) { showBrazilCard(c, i); return; }
    if (geoDE && geoDE.byIso[c.iso] === c) { showGermanyCard(c, i); return; }
    if (geoJP && geoJP.byIso[c.iso] === c) { showJapanCard(c, i); return; }
    if (geoFR && geoFR.byIso[c.iso] === c) { showFranceCard(c, i); return; }
    if (geoIT && geoIT.byIso[c.iso] === c) { showItalyCard(c, i); return; }
    if (geoES && geoES.byIso[c.iso] === c) { showSpainCard(c, i); return; }
    if (geoNG && geoNG.byIso[c.iso] === c) { showNigeriaCard(c, i); return; }
    if (geoAR && geoAR.byIso[c.iso] === c) { showArgentinaCard(c, i); return; }
    if (geoESP && geoESP.byIso[c.iso] === c) { showSpainProvinceCard(c, i); return; }
    const nm = Object.keys(geoC).find(d => geoC[d].byIso[c.iso] === c);
    if (nm) { showCountryCard(c, i, NEW_MAPS[nm]); return; }
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
      ]) +
      disputesFor(c.iso).map(d => `<h4>Disputed: ${esc(d.name)}</h4><dl class="lcfacts">${facts(disputeRows(d))}</dl>` +
        (d.info ? `<p class="dspnote">${esc(d.info)}</p>` : "")).join("");
    setLearnMore(learnMore);
    $("learnCard").hidden = false;
  }
  // A disputed territory (data/disputes.json): a small card saying who governs it, who claims it, since when, and why.
  // Tapping one in Learning mode opens it; the whole-country disputes (Taiwan, Kosovo...) go on that country's card instead.
  let disputesList = [];
  const disputesFor = iso => disputesList.filter(d => d.country === iso);
  const disputeRows = d => [["Governed by", d.admin], ["Claimed by", d.claim], ["Disputed since", d.since]];
  // a card for a place that's (partly) disputed: a short line under the main facts, and the full dispute in More facts;
  // the disputed area is highlighted grey
  function addDisputeToCard(d) {
    $("lcMain").insertAdjacentHTML("beforeend", facts([["Disputed", `${d.name}: governed by ${d.admin}, claimed by ${d.claim}`]]));
    $("lcMore").insertAdjacentHTML("afterbegin", `<h4>Disputed: ${esc(d.name)}</h4><dl class="lcfacts">${facts(disputeRows(d))}` +
      (d.info ? `<p class="dspnote">${esc(d.info)}</p>` : "") + "</dl>");
    $("lcMoreBtn").hidden = false;
    main.selDispute = d;
  }
  function showDisputeCard(d) {
    selected = null;
    $("lcFlag").hidden = true;
    $("lcName").textContent = d.name;
    $("lcSub").textContent = "Disputed territory";
    $("lcMain").innerHTML = facts(disputeRows(d)) + (d.info ? `<p class="dspnote">${esc(d.info)}</p>` : "");
    $("lcMore").innerHTML = "";
    $("lcMoreBtn").hidden = true;
    setLearnMore(false);
    $("focusBtn").hidden = true;
    $("learnCard").hidden = false;
  }
  GG.loadDisputes().then(ds => { disputesList = ds || []; if (main) { main.disputes = S.mode === "explore" ? disputesList.filter(d => !d.country) : null; main.requestDraw(); } });
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
  // Mexico's states and Mexico City (2020 census, INEGI). The picture is the coat of arms.
  function showMexicoCard(c, i) {
    const f = i.facts || {}; // tools/mx_facts.py, with the census languages added by tools/build_mx.py
    $("lcFlag").hidden = !i.flag;
    if (i.flag) { $("lcFlag").src = flagSrc(c); $("lcFlag").alt = `Coat of arms of ${c.name}`; }
    $("lcName").textContent = c.name;
    $("lcSub").textContent = [i.kind, i.region, i.abbr].filter(Boolean).join(" · ");
    $("lcMain").innerHTML = facts([[c.capitals.length ? "Capital" : "City", c.capitals[0] || "The capital of Mexico itself"],
      ["Population", fmtPop(i.pop, i.popYear)]]);
    const share = f.speakers && i.pop ? ` (${(100 * f.speakers / i.pop).toFixed(f.speakers / i.pop < 0.01 ? 1 : 0)}% speak one)` : "";
    $("lcMore").innerHTML =
      factGroup("People and culture", [
        ["Largest city", f.city || ""], ["Indigenous peoples", f.peoples],
        ["Indigenous languages", f.langs ? f.langs + share : ""], ["Famous dish", f.dish], ["Drink", f.drink],
        ["Music and dance", f.music], ["Biggest festival", f.festival],
      ]) +
      factGroup("Land and nature", [
        ["Area", `${num(i.area)} km² (${num(Math.round(i.area / 2.589988))} sq mi), #${i.areaRank} of 32`],
        ["Highest point", f.high], ["Coast", i.coastal === undefined ? "" : i.coastal ? "Yes" : "Landlocked"],
        ["Borders", (i.borders || []).join(", ")], ["Water", f.river], ["Climate", f.climate], ["Time zone", f.tz],
        ["Natural wonder", f.wonder], ["Animal", f.animal],
      ]) +
      factGroup("History and landmarks", [
        ["Became a state", i.year ? `${i.year}${i.order ? ` (the ${ordinal(i.order)} state)` : ""}` : ""],
        ["Ancient civilisation", f.ancient], ["UNESCO World Heritage", f.unesco], ["The name", f.origin],
      ]) +
      factGroup("Economy", [["Known for", f.industry]]);
    setLearnMore(learnMore);
    $("learnCard").hidden = false;
  }
  // Argentina's provinces (2022 census, INDEC)
  function showArgentinaCard(c, i) {
    const f = i.facts || {}; // tools/ar_facts.py
    $("lcFlag").src = flagSrc(c); $("lcFlag").alt = `Flag of ${c.name}`;
    $("lcName").textContent = c.name;
    $("lcSub").textContent = [i.kind, i.region].filter(Boolean).join(" · ");
    $("lcMain").innerHTML = facts([["Capital", c.capitals[0]], ["Population", fmtPop(i.pop, i.popYear)]]);
    $("lcMore").innerHTML =
      factGroup("People and culture", [
        ["People are called", f.demonym], ["Largest city", f.city || ""], ["Famous food", f.food], ["Drink", f.drink], ["Music or dance", f.music],
        ["Biggest festival", f.festival], ["Indigenous peoples", f.indigenous], ["Football", f.club], ["Famous person", f.person],
      ]) +
      factGroup("Land and nature", [
        ["Area", `${num(i.area)} km² (${num(Math.round(i.area / 2.589988))} sq mi), #${i.areaRank} of 24`],
        ["Region", i.region], ["Highest point", f.high], ["River or lake", f.river], ["Natural wonder", f.wonder], ["Climate", f.climate],
        ["Animal", f.animal], ["Coast", i.coastal === undefined ? "" : i.coastal ? "Yes" : "Landlocked"], ["Borders", (i.borders || []).join(", ")],
      ]) +
      factGroup("History", [["Became a province", f.became], ["UNESCO World Heritage", f.unesco]]) +
      factGroup("Economy", [["Known for", f.industry]]);
    setLearnMore(learnMore);
    $("learnCard").hidden = false;
  }
  // Nigeria's states (NBS 2019 estimates)
  function showNigeriaCard(c, i) {
    const f = i.facts || {}; // tools/ng_facts.py
    $("lcFlag").hidden = true; // no official state flags
    $("lcName").textContent = c.name;
    $("lcSub").textContent = [i.kind, i.region].filter(Boolean).join(" · ");
    $("lcMain").innerHTML = facts([["Capital", c.capitals[0]], ["Population", fmtPop(i.pop, i.popYear)]]);
    $("lcMore").innerHTML =
      factGroup("People and culture", [
        ["Nickname", f.nickname], ["Largest city", f.city || ""], ["Main ethnic groups", f.ethnic], ["Main languages", f.languages],
        ["Religion", f.religion], ["Famous dish", f.dish], ["Festival", f.festival], ["Traditional ruler", f.ruler], ["Famous person", f.person],
      ]) +
      factGroup("Land and nature", [
        ["Area", `${num(i.area)} km² (${num(Math.round(i.area / 2.589988))} sq mi), #${i.areaRank} of 37`],
        ["Zone", i.region], ["Main river", f.river], ["Climate", f.climate], ["Highest point", f.high], ["Natural wonder", f.wonder],
        ["Coast", i.coastal === undefined ? "" : i.coastal ? "Yes" : "Landlocked"], ["Borders", (i.borders || []).join(", ")],
      ]) +
      factGroup("History", [["Created", f.created], ["Old kingdom or empire", f.kingdom], ["UNESCO World Heritage", f.unesco]]) +
      factGroup("Economy", [["Known for", f.industry]]);
    setLearnMore(learnMore);
    $("learnCard").hidden = false;
  }
  // Spain's communities (INE, 1 January 2025)
  function showSpainCard(c, i) {
    const f = i.facts || {}; // tools/es_facts.py
    $("lcFlag").src = flagSrc(c); $("lcFlag").alt = `Flag of ${c.name}`;
    $("lcName").textContent = c.name;
    $("lcSub").textContent = [i.kind, f.own || (f.spanish !== c.name ? f.spanish : "")].filter(Boolean).join(" · ");
    $("lcMain").innerHTML = facts([[c.capitals.length > 1 && c.iso === "ES-CN" ? "Capitals" : "Capital",
      c.iso === "ES-CN" ? "Santa Cruz de Tenerife and Las Palmas de Gran Canaria" : c.capitals[0]], ["Population", fmtPop(i.pop, i.popYear)]]);
    $("lcMore").innerHTML =
      factGroup("People and culture", [
        ["Name in Spanish", f.spanish], ["In its own language", f.own], ["Co-official language", f.language], ["People are called", f.demonym],
        ["Largest city", f.city || ""], ["Famous dish", f.dish], ["Drink", f.drink], ["Biggest fiesta", f.fiesta], ["Music or dance", f.music], ["Football", f.club],
      ]) +
      factGroup("Land and nature", [
        ["Area", `${num(i.area)} km² (${num(Math.round(i.area / 2.589988))} sq mi), #${i.areaRank} of 19`],
        ["Provinces", i.provinces > 1 ? String(i.provinces) : ""], ["Highest point", f.high], ["Main river", f.river], ["Coast", f.coast],
        ["Borders", (i.borders || []).join(", ")], ["Natural wonder", f.wonder],
      ]) +
      factGroup("History and landmarks", [
        ["Old kingdom", f.kingdom], ["Moorish heritage", f.moorish], ["Landmark", f.landmark], ["UNESCO World Heritage", f.unesco],
      ]) +
      factGroup("Economy", [["Known for", f.industry]]) +
      (i.inset ? `<p class="lcnote">Shown in the box at the lower left: the Canaries are really about 1,000 km south-west of the mainland, off Africa.</p>` : "");
    setLearnMore(learnMore);
    $("learnCard").hidden = false;
  }
  // Spain's provinces: a shorter card
  function showSpainProvinceCard(c, i) {
    const f = i.facts || {};
    $("lcFlag").hidden = true;
    $("lcName").textContent = c.name;
    $("lcSub").textContent = [i.kind, i.community].filter(Boolean).join(" · ");
    $("lcMain").innerHTML = facts([["Capital", c.capitals[0]], ["Population", fmtPop(i.pop, i.popYear)]]);
    $("lcMore").innerHTML = factGroup("About", [
      ["Community", i.community], ["Area", `${num(i.area)} km² (#${i.areaRank} of 52)`], ["Landmark", f.landmark],
      ["Coast", i.coastal === undefined ? "" : i.coastal ? "Yes" : "Landlocked"],
    ]);
    setLearnMore(learnMore);
    $("learnCard").hidden = false;
  }
  // Italy's regions (ISTAT, 1 January 2026), and the enclaves' short cards
  function showItalyCard(c, i) {
    const f = i.facts || {}; // tools/it_facts.py
    $("lcFlag").hidden = !i.flag;
    if (i.flag) { $("lcFlag").src = flagSrc(c); $("lcFlag").alt = `Flag of ${c.name}`; }
    $("lcName").textContent = c.name;
    if (i.enclave) {
      $("lcSub").textContent = [i.kind, f.italian].filter(Boolean).join(" · ");
      $("lcMain").innerHTML = facts([["Capital", c.capitals[0]], ["Population", fmtPop(i.pop, i.popYear)], ["Area", f.area]]);
      $("lcMore").innerHTML = factGroup("About", [["Known for", f.about], ["Its own map", "Coming soon"]]);
      setLearnMore(learnMore);
      $("learnCard").hidden = false;
      return;
    }
    $("lcSub").textContent = [i.kind, f.italian && f.italian !== c.name ? f.italian : ""].filter(Boolean).join(" · ");
    $("lcMain").innerHTML = facts([["Capital", c.capitals[0]], ["Population", fmtPop(i.pop, i.popYear)]]);
    $("lcMore").innerHTML =
      factGroup("People and culture", [
        ["Name in Italian", f.italian], ["People are called", f.demonym], ["Dialect or language", f.dialect], ["Largest city", f.city || ""],
        ["Famous dish", f.dish], ["Protected food", f.dop], ["Wine", f.wine], ["Biggest festival", f.festival], ["Famous person", f.person],
      ]) +
      factGroup("Land and nature", [
        ["Area", `${num(i.area)} km² (${num(Math.round(i.area / 2.589988))} sq mi), #${i.areaRank} of 20`],
        ["Highest point", f.high], ["River or lake", f.river], ["Natural wonder", f.wonder], ["Coast", f.coast],
        ["Borders", (i.borders || []).join(", ")],
      ]) +
      factGroup("History and landmarks", [
        ["Special statute", i.kind === "Autonomous region" ? "Yes" : "No"], ["Before unification", f.before], ["Landmark", f.landmark],
        ["UNESCO World Heritage", f.unesco],
      ]) +
      factGroup("Economy", [["Known for", f.industry]]);
    setLearnMore(learnMore);
    $("learnCard").hidden = false;
  }
  // France's regions (INSEE legal populations)
  function showFranceCard(c, i) {
    const f = i.facts || {}; // tools/fr_facts.py
    $("lcFlag").hidden = true; // most regions have no official flag
    $("lcName").textContent = c.name;
    $("lcSub").textContent = [i.kind, f.french && f.french !== c.name ? f.french : ""].filter(Boolean).join(" · ");
    $("lcMain").innerHTML = facts([["Capital", c.capitals[0]], ["Population", fmtPop(i.pop, i.popYear)]]);
    $("lcMore").innerHTML =
      factGroup("People and culture", [
        ["Name in French", f.french], ["People are called", f.demonym], ["Regional language", f.language], ["Largest city", f.city || ""],
        ["Famous dish", f.dish], ["Cheese", f.cheese], ["Wine or drink", f.drink], ["Biggest festival", f.festival], ["Famous person", f.person],
      ]) +
      factGroup("Land and nature", [
        ["Area", `${num(i.area)} km² (${num(Math.round(i.area / 2.589988))} sq mi), #${i.areaRank} of 13`],
        ["Highest point", f.high], ["Main river", f.river], ["Coast", f.coast], ["Borders", (i.borders || []).join(", ")],
        ["Natural wonder", f.wonder],
      ]) +
      factGroup("History and landmarks", [
        ["Historic provinces", f.provinces], ["Formed", f.formed], ["Landmark", f.landmark], ["UNESCO World Heritage", f.unesco],
      ]) +
      factGroup("Economy", [["Known for", f.industry]]);
    setLearnMore(learnMore);
    $("learnCard").hidden = false;
  }
  // Japan's prefectures (2020 census)
  function showJapanCard(c, i) {
    const f = i.facts || {}; // tools/jp_facts.py
    $("lcFlag").src = flagSrc(c); $("lcFlag").alt = `Flag of ${c.name}`;
    $("lcName").innerHTML = `${esc(c.name)}${f.kanji ? ` <span class="native-ja">${esc(f.kanji)}</span>` : ""}`;
    $("lcSub").textContent = [i.kind, i.region ? `${i.region} region` : ""].filter(Boolean).join(" · ");
    $("lcMain").innerHTML = facts([["Capital", c.capitals[0]], ["Population", fmtPop(i.pop, i.popYear)]]);
    $("lcMore").innerHTML =
      factGroup("Name", [
        ["In Japanese", f.kanji ? `<span class="native-ja">${esc(f.kanji)}</span> ${esc(f.reading || "")}` : "", true],
        ["The name means", f.meaning], ["Old province", f.province],
      ]) +
      factGroup("People and culture", [
        ["Largest city", f.city || ""], ["Famous food", f.food], ["Festival", f.festival], ["Traditional craft", f.craft],
        ["Dialect", f.dialect], ["Mascot", f.mascot],
      ]) +
      factGroup("Land and nature", [
        ["Area", `${num(i.area)} km² (${num(Math.round(i.area / 2.589988))} sq mi), #${i.areaRank} of 47`],
        ["Highest point", f.high], ["River or lake", f.river], ["Natural wonder", f.wonder], ["Hot springs", f.onsen],
        ["Symbols", f.symbols],
      ]) +
      factGroup("History and landmarks", [["Castle or temple", f.castle], ["UNESCO World Heritage", f.unesco]]) +
      factGroup("Economy", [["Known for", f.industry]]);
    setLearnMore(learnMore);
    $("learnCard").hidden = false;
  }
  // Germany's states (Destatis, on the 2022 census basis)
  function showGermanyCard(c, i) {
    const f = i.facts || {}; // tools/de_facts.py
    $("lcFlag").src = flagSrc(c); $("lcFlag").alt = `Flag of ${c.name}`;
    $("lcName").textContent = c.name;
    $("lcSub").textContent = [i.kind, f.german && f.german !== c.name ? f.german : "", i.abbr].filter(Boolean).join(" · ");
    $("lcMain").innerHTML = facts([["Capital", c.capitals[0]], ["Population", fmtPop(i.pop, i.popYear)]]);
    $("lcMore").innerHTML =
      factGroup("People and culture", [
        ["Name in German", f.german], ["People are called", f.demonym], ["Dialect", f.dialect], ["Largest city", f.city || ""],
        ["Famous dish", f.dish], ["Beer or wine", f.drink], ["Biggest festival", f.festival], ["Football", f.club],
      ]) +
      factGroup("Land and nature", [
        ["Area", `${num(i.area)} km² (${num(Math.round(i.area / 2.589988))} sq mi), #${i.areaRank} of 16`],
        ["Highest point", f.high], ["Coast", f.coast], ["Borders", (i.borders || []).join(", ")], ["Main river", f.river],
        ["Natural wonder", f.wonder],
      ]) +
      factGroup("History and landmarks", [
        ["State since", i.year ? String(i.year) : ""], ["Before", f.before], ["Before 1990", f.side], ["Landmark", f.landmark],
        ["UNESCO World Heritage", f.unesco],
      ]) +
      factGroup("Economy", [["Known for", f.industry], ["Famous company", f.company]]);
    setLearnMore(learnMore);
    $("learnCard").hidden = false;
  }
  // The maps built by tools/build_country.py (Austria, Czechia, Poland, the Netherlands, Belgium): the same 18 facts
  // (tools/<code>_facts.py), plus each country's own (`special`)
  function showCountryCard(c, i, m) {
    const f = i.facts || {};
    $("lcFlag").hidden = !i.flag;
    if (i.flag) { $("lcFlag").src = flagSrc(c); $("lcFlag").alt = `${m.emblems && !i.enclave ? "Coat of arms" : "Flag"} of ${c.name}`; }
    $("lcName").textContent = c.name;
    if (i.enclave) { // an independent country inside the map (Lesotho, Eswatini): a short card
      $("lcSub").textContent = i.kind;
      $("lcMain").innerHTML = facts([["Capital", c.capitals[0]], ["Population", fmtPop(i.pop, i.popYear)],
        ["Area", i.area ? `${num(i.area)} km² (${num(Math.round(i.area / 2.589988))} sq mi)` : ""]]);
      $("lcMore").innerHTML = factGroup("About", [["Known for", f.about], ["Borders", (i.borders || []).join(", ")], ["Its own map", "Coming soon"]]);
      setLearnMore(learnMore);
      $("learnCard").hidden = false;
      return;
    }
    $("lcSub").textContent = [i.kind, f.local && f.local !== c.name ? f.local : ""].filter(Boolean).join(" · ");
    const capNote = i.capNote || c.capitals[0] || "";
    $("lcMain").innerHTML = facts([[/ and /.test(i.capNote || "") ? "Capitals" : "Capital", capNote],
      ["Population", fmtPop(i.pop, i.popYear)]]);
    $("lcMore").innerHTML =
      factGroup("People and culture", [
        // (a name in another script, such as Hangul or Arabic, in the cards' script font, laid out right to left where needed)
        [`Name in ${f.lang || m.lang || "the local language"}`, /[^\u0000-\u024F\u1E00-\u1EFF]/.test(f.local || "") ? `<span class="native" dir="auto">${esc(f.local)}</span>` : f.local,
          /[^\u0000-\u024F\u1E00-\u1EFF]/.test(f.local || "")], ["People are called", f.demonym], ["Dialect or language", f.dialect],
        ["Largest city", f.city || ""], ["Famous dish", f.dish], ["Famous drink", f.drink], ["Biggest festival", f.festival],
        ["Football", f.club], ["Famous person", f.person],
      ]) +
      factGroup("Land and nature", [
        [m.landArea ? "Land area" : "Area", `${num(i.area)} km² (${num(Math.round(i.area / 2.589988))} sq mi), #${i.areaRank} of ${i.of}`],
        ["Highest point", f.high], ["Coast", i.coastal === undefined ? "" : i.coastal ? "Yes" : "Landlocked"],
        ["Borders", (i.borders || []).join(", ")], ["Main river", f.river], ["Natural wonder", f.wonder],
      ]) +
      factGroup("History and landmarks", [
        ["Historic region", f.historic], ...(m.specials || [[m.special, "special"]]).map(([label, k]) => [label, f[k]]),
        ["Landmark", f.landmark], ["UNESCO World Heritage", f.unesco],
      ]) +
      factGroup("Economy", [["Known for", f.known], ["Famous company", f.company]]);
    setLearnMore(learnMore);
    $("learnCard").hidden = false;
  }
  // Brazil's states and the Federal District (2022 census, IBGE)
  function showBrazilCard(c, i) {
    const f = i.facts || {}; // tools/br_facts.py
    $("lcFlag").src = flagSrc(c); $("lcFlag").alt = `Flag of ${c.name}`;
    $("lcName").textContent = c.name;
    $("lcSub").textContent = [i.kind, i.region, i.abbr].filter(Boolean).join(" · ");
    $("lcMain").innerHTML = facts([["Capital", c.capitals[0]], ["Population", fmtPop(i.pop, i.popYear)]]);
    $("lcMore").innerHTML =
      factGroup("People and culture", [
        ["People are called", f.demonym], ["Largest city", f.city || ""], ["Famous dish", f.dish], ["Music and dance", f.music],
        ["Biggest festival", f.festival], ["Football", f.club],
      ]) +
      factGroup("Land and nature", [
        ["Area", `${num(i.area)} km² (${num(Math.round(i.area / 2.589988))} sq mi), #${i.areaRank} of 27`],
        ["Highest point", f.high], ["Coast", i.coastal === undefined ? "" : i.coastal ? "Yes" : "Landlocked"],
        ["Borders", (i.borders || []).join(", ")], ["Main river", f.river], ["Biome", f.biome], ["Time zone", f.tz],
        ["Natural wonder", f.wonder], ["Animal", f.animal],
      ]) +
      factGroup("History and landmarks", [
        ["Since", i.year ? String(i.year) : ""], ["Before", f.before], ["UNESCO World Heritage", f.unesco], ["The name", f.origin],
      ]) +
      factGroup("Economy", [["Known for", f.industry]]);
    setLearnMore(learnMore);
    $("learnCard").hidden = false;
  }
  const ordinal = n => n + (n % 10 === 1 && n % 100 !== 11 ? "st" : n % 10 === 2 && n % 100 !== 12 ? "nd" : n % 10 === 3 && n % 100 !== 13 ? "rd" : "th");
  // Australia's states and territories (2021 census; areas from Geoscience Australia)
  function showAustraliaCard(c, i) {
    const f = i.facts || {}; // tools/au_facts.py
    $("lcFlag").hidden = !i.flag; // Jervis Bay has no flag of its own
    if (i.flag) { $("lcFlag").src = flagSrc(c); $("lcFlag").alt = `Flag of ${c.name}`; }
    $("lcName").textContent = c.name;
    $("lcSub").textContent = `${i.kind} · ${i.abbr}`;
    $("lcMain").innerHTML = facts([["Capital", c.capitals[0] || "None (run from Canberra)"], ["Population", fmtPop(i.pop, i.popYear)]]);
    $("lcMore").innerHTML =
      factGroup("People and culture", [
        ["Nickname", f.nickname], ["People are called", f.demonym], ["Largest city", f.city || ""],
        ["First Nations", f.first], ["Food and drink", f.food], ["Football", f.football],
      ]) +
      factGroup("Land and nature", [
        ["Area", `${num(i.area)} km² (${num(Math.round(i.area / 2.589988))} sq mi), #${i.areaRank} of 9`],
        ["Highest point", f.high],
        ["Coast", i.coastal === undefined ? "" : i.coastal ? "Yes" : "Landlocked"],
        ["Water", f.water], ["Climate", f.climate], ["Time zone", f.tz], ["Natural wonder", f.wonder],
        ["Animal", f.animal], ["Bird", f.bird], ["Flower", f.flower], ["Watch out for", f.danger],
      ]) +
      factGroup("History and landmarks", [
        ["Began", f.founded], ["The name", f.origin], ["UNESCO World Heritage", f.unesco], ["Number plates", f.plate],
      ]) +
      factGroup("Economy", [["Known for", f.industry]]);
    setLearnMore(learnMore);
    $("learnCard").hidden = false;
  }
  // Russia's federal subjects (2021 census). Names in Russian (Cyrillic).
  function showRussiaCard(c, i) {
    const f = i.facts || {}; // tools/ru_facts.py
    $("lcFlag").src = flagSrc(c); $("lcFlag").alt = `Flag of ${c.name}`;
    $("lcName").textContent = c.name;
    $("lcSub").textContent = `${i.kind} · ${i.region} Federal District · ${i.abbr}`;
    const city = i.kind === "Federal city";
    const capNote = c.iso === "RU-MOS" ? "Krasnogorsk (the government's seat; there's no official capital)"
      : c.iso === "RU-LEN" ? "Gatchina (since 2021; the government still sits in Saint Petersburg)" : c.capitals[0];
    $("lcMain").innerHTML = facts([[city ? "City" : "Capital", city ? "A city in its own right" : capNote],
      ["Population", fmtPop(i.pop, i.popYear)]]);
    $("lcMore").innerHTML =
      factGroup("Names", [
        ["In Russian", f.ru ? `<span class="native">${esc(f.ru)}</span>` : "", true],
        ["Soviet name", f.soviet],
      ]) +
      factGroup("People and culture", [
        ["Largest city", f.city || ""],
        ["Peoples", f.ethnic],
        [/,| and /.test(f.langs || "") ? "Languages" : "Language", f.langs],
        ["Religion", f.religion],
        ["Food", f.dish],
        ["Traditional craft", f.craft],
      ]) +
      factGroup("Land and nature", [
        ["Area", `${num(i.area)} km² (${num(Math.round(i.area / 2.589988))} sq mi), #${i.areaRank} of 83`],
        ["Highest point", f.high],
        ["Coast", i.coastal === undefined ? "" : i.coastal ? "Yes" : "Landlocked"],
        ["Borders", (i.borders || []).join(", ")],
        ["Main river", f.river],
        ["Climate", f.climate],
        ["Coldest", f.cold],
        [/ and /.test(f.tz || "") ? "Time zones" : "Time zone", f.tz ? `${f.tz}${f.tz === "UTC+3" ? " (Moscow time)" : ""}` : ""],
        ["Natural wonder", f.nature],
        ["Wildlife", f.animal],
      ]) +
      factGroup("History and landmarks", [
        ["Became part of Russia", f.joined],
        [city ? "Founded" : "In its present form since", f.year ? String(f.year) : ""],
        ["UNESCO World Heritage", f.unesco],
        ["Trans-Siberian Railway", f.transsib ? "Passes through" : ""],
      ]) +
      factGroup("Economy", [["Known for", f.industry]]);
    setLearnMore(learnMore);
    $("learnCard").hidden = false;
  }
  // a piece of Russia's timeline: when Russia held it and who from (approximate: drawn with today's borders)
  function showHistoryCard(f) {
    const pr = f.properties, y = tlYear;
    const span = ([a, b]) => b === null ? `${a} to today` : `${a}–${b}`;
    $("lcFlag").hidden = true;
    $("lcName").textContent = pr.name;
    const st = GG.heldIn(f, y);
    $("lcSub").textContent = st === "held" ? `Part of Russia in ${y}` : st === "annexed" ? "Annexed by Russia; most countries don't recognise it" : `No longer Russia's in ${y}`;
    $("lcMain").innerHTML = facts([["Part of Russia", pr.held.map(span).join(", and ")],
      ["Gained from", pr.from], ["Annexed", pr.annexed ? `${pr.annexed} (not recognised by most countries)` : ""]]);
    $("lcMain").innerHTML += '<p class="lcnote">Approximate: drawn with today\'s borders, not the old ones.</p>';
    setLearnMore(false); $("lcMore").innerHTML = ""; $("lcMoreBtn").hidden = true;
    $("focusBtn").hidden = true;
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
  // Earth mode's cards (js/earth.js): a name, a line under it, facts, a note; More facts: more rows, a longer text, the credit
  function earthCard(c) {
    selected = null;
    $("lcFlag").hidden = true;
    $("lcName").textContent = c.name;
    $("lcSub").textContent = c.sub || "";
    $("lcMain").innerHTML = facts(c.rows || []) + (c.note ? `<p class="dspnote">${esc(c.note)}</p>` : "");
    earthCardMore(null, c);
    setLearnMore(false);
    $("focusBtn").hidden = true;
    $("learnCard").hidden = false;
    $("learnCard").scrollTop = 0;
  }
  let earthCardNow = null;
  function earthCardMore(text, c = earthCardNow) { // (text: a volcano's summary, which arrives after the card opens)
    earthCardNow = c;
    const rows = facts((c && c.more) || []);
    $("lcMore").innerHTML = (rows ? `<dl class="lcfacts">${rows}</dl>` : "") + (text ? `<p class="dspnote">${esc(text)}</p>` : "")
      + (c && c.credit ? `<p class="hint2">${esc(c.credit)}</p>` : "");
    $("lcMoreBtn").hidden = !(rows || text);
  }
  function hideLearnCard() { if (GG.Earth) GG.Earth.clearSel(); $("learnCard").hidden = true; $("focusBtn").hidden = true; setLearnMore(false); if (main && main.selDispute) { main.selDispute = null; main.requestDraw(); } } // the next card opens collapsed
  // Focus: a button above the card that opens a country's own map in Learning mode ("Focus on <name> ›").
  // Only the US has its own map so far; the plan is one for every country (PLAN.md).
  // Countries with their own map: the Countries tab in the New game menu and the Focus button both use this list.
  // `unit` names the parts (States, Provinces, Counties); `soon` ones are listed but can't be opened yet.
  const COUNTRY_MAPS = {
    USA: { name: "United States", focus: "The U.S.", cont: "North America", unit: "States", data: "us", region: "usa" },
    CAN: { name: "Canada", focus: "Canada", cont: "North America", unit: "Provinces & territories", data: "ca", region: "canada" },
    // the UK and Ireland share one map of Britain and Ireland's counties (Ireland opens on its own region)
    // (games use the ceremonial counties; the historic ones are in Learning mode only)
    GBR: { name: "United Kingdom", focus: "the UK", cont: "Europe", unit: "Counties", data: "ukc", region: "ukc", page: "Britain & Ireland" },
    IRL: { name: "Ireland", focus: "Ireland", cont: "Europe", unit: "Counties", data: "ukc", region: "ukc-ire", page: "Ireland", own: true },
    // coming next (India_plan.md, China_plan.md, Russia_plan.md, Australia_plan.md); Russia is in Europe and Asia
    IND: { name: "India", focus: "India", cont: "Asia", unit: "States & UTs", data: "in", region: "india" },
    CHN: { name: "China", focus: "China", cont: "Asia", unit: "Provinces", data: "cn", region: "china" },
    RUS: { name: "Russia", focus: "Russia", cont: ["Europe", "Asia"], unit: "Oblasts", data: "ru", region: "russia" },
    AUS: { name: "Australia", focus: "Australia", cont: "Oceania", unit: "States & territories", data: "au", region: "australia" },
    // coming next (Mexico_plan.md, Brazil_plan.md)
    MEX: { name: "Mexico", focus: "Mexico", cont: "North America", unit: "States", data: "mx", region: "mexico" },
    BRA: { name: "Brazil", focus: "Brazil", cont: "South America", unit: "States", data: "br", region: "brazil" },
    // the next wave (jobs/build_countries.md)
    DEU: { name: "Germany", focus: "Germany", cont: "Europe", unit: "States", data: "de", region: "germany" },
    FRA: { name: "France", focus: "France", cont: "Europe", unit: "Regions", data: "fr", region: "france" },
    ITA: { name: "Italy", focus: "Italy", cont: "Europe", unit: "Regions", data: "it", region: "italy" },
    ESP: { name: "Spain", focus: "Spain", cont: "Europe", unit: "Communities", data: "es", region: "spain" },
    JPN: { name: "Japan", focus: "Japan", cont: "Asia", unit: "Prefectures", data: "jp", region: "japan" },
    NGA: { name: "Nigeria", focus: "Nigeria", cont: "Africa", unit: "States", data: "ng", region: "nigeria" },
    ARG: { name: "Argentina", focus: "Argentina", cont: "South America", unit: "Provinces", data: "ar", region: "argentina" },
  };
  Object.entries(NEW_MAPS).forEach(([d, m]) => {
    if (!m.sub) COUNTRY_MAPS[m.a3] = { name: m.name, focus: m.focus || m.name, cont: m.cont || "Europe", unit: m.Nouns, data: d, region: m.region || m.style };
  });
  // from the world Learning map, the UK and Ireland open the countries view first
  // (Ireland opens straight on its own counties, in the county set last used in Learning mode)
  const FOCUS_INTO = { GBR: { region: "ukn", data: "ukn" }, IRL: { get region() { return ukSet() + "-ire"; }, get data() { return ukSet(); } },
  };
  let focusOn = null;
  let focusFrom = null; // the country whose "Focus on" button is showing
  function showFocus(c) {
    focusFrom = c;
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
  // the view you left when you focused on a country (per map: the world, or the UK & Ireland countries view),
  // so the back button returns to exactly that, with the country's card open again
  const viewBefore = {};
  $("focusBtn").onclick = () => {
    if (!focusOn) return;
    viewBefore[S.data] = { t: main.t, mode: main.mode, iso: focusFrom && focusFrom.iso };
    if (S.data === "world") delete viewBefore.ukn; // (a fresh trip from the world map: back goes to the world)
    const into = S.data === "world" && FOCUS_INTO[Object.keys(COUNTRY_MAPS).find(k => COUNTRY_MAPS[k] === focusOn)];
    startGame("explore", (into || focusOn).region, "flat", (into || focusOn).data);
  };
  $("worldBtn").onclick = () => {
    // (counties go back to the UK & Ireland countries view, unless Ireland was opened straight from the world map)
    const irlFromWorld = /-ire$/.test(S.region) && !viewBefore.ukn;
    const back = (S.data === "uk" || S.data === "ukc") && !irlFromWorld ? "ukn" : "world", v = viewBefore[back];
    const view = back === "world" ? (v ? v.mode : prefs.worldView || "globe") : "flat";
    Promise.resolve(startGame("explore", back, view, back)).then(() => {
      if (!v || S.data !== back) return;
      main.setTransform(v.t, false);
      const c = v.iso && geo.byIso[v.iso];
      if (c) { state[c.iso] = "flash"; flashName(c); showLearnCard(c); showFocus(c); }
      redraw();
    });
  };
  $("lcClose").onclick = () => { hideLearnCard(); selectSub(null); Object.keys(state).forEach(k => delete state[k]); redraw(); };
  // ---------- Reservations layer (country Learning maps only; too heavy for the world globe) ----------
  // US: reservations and Oklahoma tribal areas (US Census). Canada: First Nations reserves, and Indigenous settlement
  // and owned lands (Natural Resources Canada). One file per country, loaded the first time it's needed.
  const RES = {
    us: { file: "data/tribal-us.json", label: "Reservations", credit: "Reservations: US Census Bureau." },
    ca: { file: "data/tribal-ca.json", label: "Reserves",
      credit: "Reserves: Natural Resources Canada. Contains information licensed under the Open Government Licence – Canada." },
    // Australia: native title determinations (where native title exists) and Indigenous Protected Areas
    // Mexico: municipalities shaded by the share who speak an Indigenous language
    mx: { file: "data/tribal-mx.json", label: "Indigenous languages",
      credit: "Indigenous languages: INEGI, 2020 census. Municipal boundaries: geoBoundaries (CC BY 4.0)." },
    // Brazil: FUNAI's Indigenous territories
    br: { file: "data/tribal-br.json", label: "Indigenous lands", credit: "Indigenous territories: FUNAI (Fundação Nacional dos Povos Indígenas)." },
    au: { file: "data/tribal-au.json", label: "Aboriginal land",
      credit: "Native title: National Native Title Tribunal (CC BY 4.0). Indigenous Protected Areas: DCCEEW (CC BY 4.0)." },
  };
  // the layer's name inside a sentence ("Loading reservations…"; Aboriginal keeps its capital)
  const resWord = d => (d === "au" || d === "mx" || d === "br" ? RES[d].label : RES[d].label.toLowerCase());
  const tribal = {}, tribalLoading = {};
  let resAfterSplash = false, resOn = !!prefs.reserves;
  function showReserves() {
    const d = S.data, learning = S.mode === "explore" && !!RES[d];
    // not loaded under the splash (preparing them made the splash jumpy)
    if (learning && resOn && !tribal[d] && GG.splashShowing) resAfterSplash = true;
    else if (learning && resOn && !tribal[d] && !tribalLoading[d]) {
      tribalLoading[d] = true; toast(`Loading ${resWord(d)}…`);
      fetch(RES[d].file).then(r => r.json()).then(g => { tribal[d] = GG.fixWinding(g); toast(null); showReserves(); })
        .catch(() => { toast(`Couldn't load the ${resWord(d)}.`, 2000); resOn = false; showReserves(); })
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
    Reserve: "Indigenous reserve or settlement land, Canada",
    NT: "Native title over the whole area", NTP: "Native title in parts of this area", IPA: "Indigenous Protected Area" };

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
  // Russia: 1300 to today (2023 = today: the plain map; the stops come from data/ru-history.json)
  let ruHist = null;
  // Australia: colonies split from New South Wales, then Federation and the territories (Australia_plan.md)
  const AU_TL = { 1788: "New South Wales, the first colony (the First Fleet)", 1825: "Van Diemen's Land (Tasmania) splits from New South Wales",
    1829: "The Swan River Colony (Western Australia), a free settlement", 1836: "South Australia, a free colony with no convicts",
    1851: "Victoria splits from New South Wales", 1859: "Queensland splits from New South Wales",
    1901: "Federation: the six colonies become the states of Australia",
    1911: "The Northern Territory (from South Australia) and the ACT (from New South Wales)",
    1915: "Jervis Bay Territory: a seaport for Canberra" };
  // Brazil: how today's states formed (Brazil_plan.md), from the first captaincies to the 1988 constitution
  const BR_TL = { 1534: "The first captaincies: Bahia, Maranhão and Pernambuco", 1565: "Rio de Janeiro founded",
    1616: "Grão-Pará, at the mouth of the Amazon", 1709: "São Paulo", 1720: "Minas Gerais, in the gold rush",
    1748: "Goiás and Mato Grosso", 1760: "Rio Grande do Sul", 1799: "Ceará and Paraíba split off", 1810: "Espírito Santo",
    1811: "Piauí", 1817: "Alagoas and Rio Grande do Norte split off", 1820: "Sergipe", 1821: "Santa Catarina",
    1850: "Amazonas", 1853: "Paraná", 1960: "Brasília, the new capital: the Federal District", 1962: "Acre becomes a state",
    1979: "Mato Grosso do Sul splits from Mato Grosso", 1982: "Rondônia becomes a state",
    1988: "The new constitution: Amapá, Roraima and Tocantins" };
  const TL_CAPTIONS = { au: AU_TL, br: BR_TL };
  function setRuTimeline(year) {
    tlYear = year;
    $("tlRange").value = year;
    const today = year >= TL_MAX.ru;
    const stop = ruHist ? ruHist.stops.filter(s => s[0] <= year).pop() : null;
    $("tlLabel").innerHTML = today ? "<b>Today</b> Drag back through Russia's history"
      : `<b>${year}</b> ${stop ? esc(stop[0] === year ? stop[1] : `No change since ${stop[0]}`) : ""}`;
    $("tlLegend").hidden = today;
    main.setHistory(today || !ruHist ? null : { fc: ruHist, year });
    if (!today) hideLearnCard();
  }
  function setTimeline(year) {
    if (tlKind === "ru") { setRuTimeline(year); return; }
    tlYear = year;
    $("tlRange").value = year;
    const states = geo.countries.filter(c => c.info && c.info.year <= year);
    const joined = states.filter(c => c.info.year === year).sort((a, b) => a.info.order - b.info.order);
    const n = states.length;
    const note = joined.length ? `${joined.map(c => c.name).join(", ")} joined` : "";
    if (TL_CAPTIONS[tlKind]) {
      const caps = TL_CAPTIONS[tlKind], stop = Object.keys(caps).map(Number).filter(y => y <= year).pop();
      $("tlLabel").innerHTML = `<b>${year}</b> ${esc(stop === year ? caps[year] : `No change since ${stop}`)}`;
    } else $("tlLabel").innerHTML = `<b>${year}</b> ${n === 50 ? "All 50 states" : `${n} state${n === 1 ? "" : "s"}`}${note ? " · " + esc(note) : ""}`;
    if (year >= TL_MAX[tlKind] || !geo.bordersWhere) main.setBordersOverride(null);
    else {
      if (!tlBorders.has(year)) tlBorders.set(year, geo.bordersWhere((a, b) => (a && a.info.year <= year) || (b && b.info.year <= year)));
      main.setBordersOverride(tlBorders.get(year));
    }
    redraw();
  }
  function stopTimeline() { clearInterval(tlTimer); tlTimer = null; $("tlPlay").textContent = "▶"; $("tlPlay").setAttribute("aria-label", "Play the timeline"); }
  function showTimeline(on, kind = "us") {
    stopTimeline();
    tlKind = kind;
    $("timeline").hidden = !on;
    $("timeline").classList.toggle("tl2", kind === "ru");
    $("tlLegend").hidden = true;
    $("mapwrap").classList.toggle("hastl", on);
    tlYear = TL_MAX[kind]; // at its end: a switched-off timeline mustn't hide parts formed later (Brazil's 1988 states)
    main.setBordersOverride(null);
    main.setHistory(null);
    const r = $("tlRange");
    r.min = kind === "ru" ? 1300 : kind === "au" ? 1788 : kind === "br" ? 1534 : 1787; r.max = TL_MAX[kind];
    $("tlPrev").setAttribute("aria-label", kind === "ru" ? "Previous change" : "Previous state to join");
    $("tlNext").setAttribute("aria-label", kind === "ru" ? "Next change" : "Next state to join");
    if (on && kind === "ru" && !ruHist) GG.loadRUHistory().then(h => { ruHist = h; if (tlKind === "ru") setTimeline(+r.value); }).catch(() => {});
    if (on) setTimeline(TL_MAX[kind]);
  }
  $("tlRange").addEventListener("input", e => { stopTimeline(); setTimeline(+e.target.value); });
  // the arrows jump to the previous or next year a state joined
  const joinYears = () => tlKind === "ru" ? (ruHist ? ruHist.stops.map(s => s[0]).concat(TL_MAX.ru) : [TL_MAX.ru])
    : TL_CAPTIONS[tlKind] ? Object.keys(TL_CAPTIONS[tlKind]).map(Number)
    : [...new Set(geo.countries.map(c => c.info.year))].sort((a, b) => a - b);
  const tlMin = () => +$("tlRange").min, tlMax = () => TL_MAX[tlKind];
  $("tlPrev").onclick = () => { stopTimeline(); const y = joinYears().filter(y => y < tlYear).pop(); setTimeline(y || tlMin()); };
  $("tlNext").onclick = () => { stopTimeline(); const y = joinYears().find(y => y > tlYear); setTimeline(y || tlMax()); };
  $("tlPlay").onclick = () => {
    if (tlTimer) { stopTimeline(); return; }
    const years = joinYears();
    let i = tlYear >= tlMax() ? 0 : years.findIndex(y => y > tlYear);
    if (i < 0) i = 0;
    setTimeline(years[i]);
    $("tlPlay").textContent = "❚❚"; $("tlPlay").setAttribute("aria-label", "Pause the timeline");
    tlTimer = setInterval(() => {
      i++;
      if (i >= years.length) { stopTimeline(); return; }
      setTimeline(years[i]);
      if (i === years.length - 1) stopTimeline();
    }, tlKind === "ru" ? 1100 : 700);
  };

  // ---------- stats page ----------
  const MODE_NAMES = { find: "Find countries", name: "Name countries", findcap: "Find by capital", namecap: "Name capitals",
    findflag: "Find by flag", nameflag: "Name the flags" };
  const modeName = (m, region) => { const d = DATASETS[dataOfRegion(region)];
    return MODE_NAMES[m].replace("countries", d.nouns).replace("capitals", d.caps || "capitals").replace("capital", d.cap || "capital")
      .replace("flags", d.emblems || "flags").replace("flag", d.emblem || "flag"); };
  let statsSkill = "country", statsData = "world";
  const fmtTime = s => `${Math.floor(s / 60)}:${String(s % 60).padStart(2, "0")}`;
  function openStats() { statsData = S.data === "ukn" || S.data === "uk" ? "ukc" : S.data; renderStats(); $("stats").hidden = false; } // (UK games are ceremonial)
  function closeStats() { $("stats").hidden = true; resetStatsReset(); }
  function renderStats() {
    const skill = statsSkill, St = GG.Stats, ds = DATASETS[statsData], sub = isCountryMap(statsData);
    document.querySelectorAll("#statsSkill button").forEach(b => b.classList.toggle("on", b.dataset.v === skill));
    document.querySelectorAll("#statsData button").forEach(b => b.classList.toggle("on", b.dataset.v === statsData));
    $("statsSkill").querySelector('[data-v="country"]').textContent = ({ us: "States", ca: "Provinces", in: "States", cn: "Provinces", ru: "Oblasts", au: "States", mx: "States", br: "States", de: "States", jp: "Prefectures", fr: "Regions", it: "Regions", es: "Communities", esp: "Provinces", ng: "States", ar: "Provinces", uk: "Counties", ukc: "Counties" })[statsData] || (NEW_MAPS[statsData] || {}).Nouns || "Countries";
    $("statsSkill").querySelector('[data-v="capital"]').textContent = ds.caps ? "County towns" : "Capitals";
    // no flags (India): no Flags tab
    $("statsSkill").querySelector('[data-v="flag"]').hidden = !!ds.noFlags;
    $("statsSkill").querySelector('[data-v="flag"]').textContent = ds.emblems ? ds.emblems[0].toUpperCase() + ds.emblems.slice(1) : "Flags";
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
        `autocapitalize="off" spellcheck="false" enterkeyhint="next" aria-label="${phWord()} with this ${emblem()}" placeholder="${(prefs.perRow || 4) >= 6 ? "…" : phWord()}">`;
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
    if (isAirports() && S.mode === "find" && !S.apDots && target && !finished && view === main) {
      const ll = main.lonLatAt(x, y); if (!ll) return true;
      const d = d3.geoDistance(ll, target.anchor) * 6371;
      if (d <= AP_NEAR) { tap(target, view); return true; }
      GG.Stats.answer(S.mode, target.iso, false);
      state[target.iso] = "bad"; nBad++;
      toast(`Missed: ${target.code} is ${target.info.full}, ${Math.round(d).toLocaleString("en-GB")} km away`, 2600);
      next(); return true;
    }
    if (S.mode === "hist" && view === main && GG.History) return GG.History.onPoint(view, x, y);
    // Russia's timeline: a tap shows when that land was Russia's
    if (view === main && main.history) {
      const f = main.historyAt(x, y);
      if (f) { showHistoryCard(f); return true; }
    }
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
  // ---------- the World game: choose the region, then the game (one box, two steps; 2026-11-18) ----------
  // Both steps sit in the same place in the box (the hidden one keeps its space), so the menu never changes size.
  const steps = { region: false, game: false, at: "region" };
  function showStep(at) {
    steps.at = at;
    $("regions").classList.toggle("stepoff", at !== "region");
    $("segGame").classList.toggle("stepoff", at !== "game");
    $("stepInstr").textContent = at === "region" ? "Choose region" : "Choose game";
    $("stepBack").hidden = at !== "game";
    $("stepChosen").textContent = at === "game" && steps.region ? REGIONS[pick.region].name : "";
    setStartReady();
  }
  // Start: greyed until the region and the game are both chosen (World games only)
  const worldGameStep = () => pick.tab === "world" && !pick.learn && !pick.earth;
  const startReady = () => !worldGameStep() || (steps.region && steps.game);
  function setStartReady() { $("startBtn").classList.toggle("notready", !startReady()); if (startReady()) $("startWarn").hidden = true; }
  $("stepBack").onclick = () => showStep("region");
  const GAME_NAMES = { find: "Find · Countries", findcap: "Find · By capital", findflag: "Find · By flag",
    name: "Name · Countries", namecap: "Name · Capitals", nameflag: "Name · Flags" };
  // Countries tab: continent headings (the Caribbean is part of North America) with a button per country map
  function buildCountryList() {
    const conts = ["Europe", "Asia", "Africa", "North America", "South America", "Oceania"];
    $("countryList").innerHTML = conts.map(ct => {
      const inCont = m => (Array.isArray(m.cont) ? m.cont.includes(ct) : m.cont === ct);
      const btns = Object.entries(COUNTRY_MAPS).filter(([, m]) => inCont(m)).sort(([, a], [, b]) => a.name.localeCompare(b.name, "en")).map(([iso, m]) => {
        const c = geoWorld.byIso[iso];
        return `<button type="button" data-v="${iso}"${m.soon ? " disabled" : ""}>${c ? `<img src="${flagSrc(c)}" alt="">` : ""}` +
          `<span>${esc(m.name)}</span>${m.soon ? "<small>soon</small>" : ""}</button>`;
      }).join("");
      const n = Object.values(COUNTRY_MAPS).filter(inCont).length;
      const open = (prefs.openConts || []).includes(ct);
      return `<details data-cont="${ct}"${open ? " open" : ""}><summary><h3>${ct}</h3><span class="ccount">${n}</span></summary>` +
        `${btns ? `<div class="cbtns">${btns}</div>` : `<p class="none">More countries to come</p>`}</details>`;
    }).join("");
    $("countryList").querySelectorAll("details").forEach(d => d.addEventListener("toggle", () => {
      savePrefs({ openConts: [...$("countryList").querySelectorAll("details[open]")].map(x => x.dataset.cont) });
    }));
  }
  // World, the list of countries, or one country's page (its Find and Name games)
  // the menu's title: the tab you're on
  const setupName = () => (pick.earth ? "Earth" : pick.learn ? "Learning mode" : "New game");
  function showData() {
    const earth = !!pick.earth, countries = pick.tab === "countries" && !earth, learn = pick.learn && !earth;
    segSelect($("segData"), pick.tab);
    segSelect($("setupTabs"), earth ? "earth" : learn ? "learn" : "game");
    $("setupTitle").textContent = setupName();
    $("segData").hidden = earth;
    $("earthPanel").hidden = !earth;
    $("worldPanel").hidden = countries || learn || earth;
    $("learnPanel").hidden = countries || !learn;
    // Learning mode's Countries: just the list (a tap opens that country's map)
    $("countryList").hidden = !countries || (!learn && !!pick.country);
    $("countryPage").hidden = !countries || learn || !pick.country;
    playClip(!countries && learn);
    if (countries && pick.country) {
      const m = COUNTRY_MAPS[pick.country], ds = DATASETS[pick.data];
      $("cpName").textContent = m.page || m.name;
      $("cpGames").querySelectorAll('[data-v="find"], [data-v="name"]').forEach(b => { b.textContent = m.unit; });
      const capsLabel = ds.caps ? ds.caps[0].toUpperCase() + ds.caps.slice(1) : "Capitals";
      $("cpGames").querySelectorAll('[data-v="findcap"], [data-v="namecap"]').forEach(b => { b.textContent = capsLabel; });
      segSelect($("cpGames"), pick.mode);
      // Britain and Ireland: county set, region and the Crown Dependencies, chosen before each game
      const uk = pick.data === "uk" || pick.data === "ukc";
      $("cpOpts").hidden = !uk || !!m.own; // (Ireland's own page: just its counties)
      // no county in Ireland has a registered flag: no flag games there (shown again for every other choice)
      const noFlags = (uk && /-ire$/.test(pick.region)) || !!DATASETS[pick.data].noFlags;
      // India: union territories on or off
      $("cpUTField").hidden = pick.data !== "in";
      // Spain: communities or provinces
      const sets = SETS[pick.data];
      $("cpESField").hidden = !sets;
      if (sets) {
        $("cpES").innerHTML = sets.map(d => `<button data-v="${d}" type="button">${DATASETS[d].Nouns} (${DATASETS[d].count})</button>`).join("");
        segSelect($("cpES"), pick.data);
        $("cpGames").querySelectorAll('[data-v="find"], [data-v="name"]').forEach(b => { b.textContent = DATASETS[pick.data].Nouns; });
      }
      if (pick.data === "in") segSelect($("cpUT"), pick.ut === false ? "off" : "on");
      $("cpGames").querySelectorAll('[data-v="findflag"], [data-v="nameflag"]').forEach(b => {
        b.hidden = noFlags; b.textContent = ds.emblems ? ds.emblems[0].toUpperCase() + ds.emblems.slice(1) : "Flags"; });
      if (noFlags && /flag$/.test(pick.mode)) { pick.mode = pick.mode.replace("flag", ""); segSelect($("cpGames"), pick.mode); }
      if (uk) {
        $("cpSetField").hidden = true; // games use the ceremonial counties (the historic ones: Learning mode only)
        segSelect($("cpSet"), pick.data);
        segSelect($("cpRegion"), pick.region.replace(/^ukc?/, "") || "all");
        segSelect($("cpCD"), pick.cd ? "on" : "off");

        $("cpCDField").hidden = pick.region !== pick.data; // whole map only
      }
    }
    $("startBtn").hidden = countries && (learn || !pick.country); // pick a country first
    $("startBtn").textContent = learn ? "Discover" : "Start";
    setStartReady();
    if (!countries && !learn) { segSelect($("segGame"), steps.game ? pick.mode : ""); $("viewField").hidden = pick.region !== "world"; }
    $("gameRow").hidden = countries || learn || earth; // the switch and More games: the Game tab's World view
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
    // Learning mode: straight to that country's own map (the UK and Ireland open on their countries view)
    if (pick.learn) {
      const to = FOCUS_INTO[b.dataset.v] || m;
      delete viewBefore.ukn; // (from the list: back goes to the world map)
      closeSetup(); closeInset(); startGame("explore", to.region, "flat", to.data); return;
    }
    pick.country = b.dataset.v; pick.data = m.data; pick.region = m.region;
    showData(); showOptions();
  });
  $("cpBack").onclick = () => { pick.country = null; showData(); };
  $("setBtn").onclick = () => {
    if (SETS[S.data]) { const d = SETS[S.data].find(x => x !== S.data); startGame("explore", DATASETS[d].region, "flat", d); return; }
    const d = S.data === "uk" ? "ukc" : "uk"; savePrefs({ ukSet: d }); startGame("explore", d + S.region.replace(/^ukc?/, ""), "flat", d);
  };
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
  $("cpES").addEventListener("click", e => {
    const b = e.target.closest("button"); if (!b) return;
    pick.data = b.dataset.v; pick.region = DATASETS[pick.data].region;
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
    $("gameRow").hidden = on || pick.tab === "countries" || pick.learn || pick.earth;
    $("setupTitle").textContent = on ? "Options" : setupName();
    $("optBtn").classList.toggle("on", on); $("optBtn").setAttribute("aria-pressed", on);
  }
  $("optBtn").onclick = () => { if (!$("tabHelp").hidden) showHelpPanel(false); showOptPanel($("tabOptions").hidden); };
  $("optBack").onclick = () => showOptPanel(false);
  function openSetup() {
    $("nameInput").blur(); // (the keyboard goes while the menu is open)
    // opens on the tab you're playing in: Learning mode, or a scored game
    pick.learn = S.mode === "explore"; pick.earth = S.mode === "earth";
    pick.mode = S.mode === "explore" ? (prefs.game && prefs.game.mode !== "explore" ? prefs.game.mode : "find") : S.mode;
    pick.region = S.region; pick.view = S.region === "world" ? main.mode : "globe"; pick.data = S.data;
    pick.tab = "world"; // the menu always opens on Game › World (2026-11-18)
    const mapData = S.data === "ukc" ? "uk" : S.data; // both county sets are one entry in the list
    pick.country = S.data === "world" ? null : /-ire$/.test(S.region) ? "IRL"
      : Object.keys(COUNTRY_MAPS).find(k => COUNTRY_MAPS[k].data === mapData) || null;
    pick.cd = !!S.cd; pick.ut = S.ut !== false;
    if (S.data !== "world") { pick.data = "world"; pick.region = "world"; pick.view = "globe"; pick.country = null; }
    if (!MODE_NAMES[pick.mode]) pick.mode = "find"; // (after a History game)
    if (!$("countryList").childElementCount) buildCountryList();
    segSelect($("segGame"), pick.mode); segSelect($("regions"), pick.region); setViewSwitch();
    if (pick.learn && pick.region !== "world" && !isCountryMap(pick.data)) pick.region = "world";
    $("viewField").hidden = pick.region !== "world";
    segSelect($("segTheme"), prefs.theme === "light" || prefs.theme === "dark" ? prefs.theme : "auto");
    pick.weak = !!S.weak; pick.timer = !!S.timer;
    pick.paceFind = S.paceFind || 5; pick.paceName = S.paceName || 10;
    segSelect($("segQuestions"), pick.weak ? "weak" : "all"); segSelect($("segTimer"), pick.timer ? "on" : "off");
    steps.region = steps.game = false; segSelect($("segGame"), ""); segSelect($("regions"), ""); $("startWarn").hidden = true; showStep("region");
    $("tabMore").hidden = true; $("tabHelp").hidden = true; $("helpBtn").classList.remove("on");
    showOptPanel(false);
    showData();
    showOptions();
    $("setup").hidden = false;
    // playing an airport or History game: that game's options first (More games › …)
    if (isAirports() || S.mode === "hist") {
      $("startBtn").dataset.wasHidden = $("startBtn").hidden ? "1" : "";
      showMorePanel(true);
      if (isAirports()) showAirportPanel(true); else showHistPanel(true);
    }
  }
  function closeSetup() {
    $("setup").hidden = true; playClip(false);
    if (!$("apBig").hidden && document.hasFocus()) setTimeout(() => $("nameInput").focus(), 0); // back to Name the code: the keyboard again
  }
  // ---------- theme: Auto (the phone's light or dark mode), Light or Dark (Options) ----------
  const isDark = () => document.documentElement.dataset.theme ? document.documentElement.dataset.theme === "dark"
    : !!(window.matchMedia && matchMedia("(prefers-color-scheme: dark)").matches);
  function setTheme(t) {
    if (t === "light" || t === "dark") document.documentElement.dataset.theme = t; else delete document.documentElement.dataset.theme;
    savePrefs({ theme: t === "light" || t === "dark" ? t : null });
    segSelect($("segTheme"), t === "light" || t === "dark" ? t : "auto");
    themeChanged();
  }
  // the map and inset re-read their colours, and the clip switches to the matching version
  function themeChanged() {
    if (GG.Earth) GG.Earth.readColours();
    main.readColours(); if (insetView) insetView.readColours(); redraw();
    clipSource();
  }
  $("segTheme").addEventListener("click", e => { const b = e.target.closest("button"); if (b) setTheme(b.dataset.v); });
  // the clip in the theme's colours (media/Learning_mode_clip*.webm|mp4|jpg, recorded by tools/record_clip.py)
  function clipSource() {
    const v = $("learnClip"); if (!v) return;
    const base = "media/Learning_mode_clip" + (isDark() ? "" : "_light");
    if (v.dataset.base === base) return;
    const playing = !v.paused;
    v.dataset.base = base; v.poster = base + ".jpg";
    v.innerHTML = `<source src="${base}.webm" type="video/webm"><source src="${base}.mp4" type="video/mp4">`;
    v.load();
    if (playing) { const p = v.play(); if (p && p.catch) p.catch(() => {}); }
  }
  // the Learning mode clip loops only while it's on screen; with reduced motion it waits for a tap on play
  function playClip(on) {
    const v = $("learnClip"); if (!v) return;
    clipSource();
    const still = window.matchMedia && matchMedia("(prefers-reduced-motion: reduce)").matches;
    v.controls = still;
    if (on && !still) { if (v.preload === "none") v.preload = "auto"; const p = v.play(); if (p && p.catch) p.catch(() => {}); }
    else if (!on) v.pause();
  }
  $("menuBtn").onclick = openSetup;
  $("setupClose").onclick = closeSetup;
  $("setup").addEventListener("click", e => { if (e.target === $("setup")) closeSetup(); });
  $("segGame").addEventListener("click", e => { const b = e.target.closest("button"); if (b && !b.disabled) { pick.mode = b.dataset.v; segSelect($("segGame"), pick.mode); steps.game = true; setStartReady(); showOptions(); } });
  // Options tab: knowledge gaps only for the Find games; the timer for every scored game
  function showOptions() {
    const find = pick.mode === "find" || pick.mode === "findcap" || pick.mode === "findflag";
    // Learning mode: only what applies there (the World map's globe or flat view)
    const learn = !!pick.learn || !!pick.earth; // (Earth mode: only the map's view, like Learning mode)
    $("questionsField").hidden = !find || learn;
    $("questionsNA").hidden = find || learn;
    $("timerField").hidden = pick.mode === "explore" || learn;
    $("learnViewField").hidden = !learn || (pick.tab !== "world" && !pick.earth);
    segSelect($("segLearnView"), pick.view);
    $("gameSummary").textContent = GAME_NAMES[pick.mode] || "";
    $("paceBox").hidden = !pick.timer;
    const pace = isNameMode(pick.mode) ? pick.paceName : pick.paceFind;
    segSelect($("segPace"), String(pace));
    const r = REGIONS[pick.region];
    let all = countFor(pick.data, pick.region, pick.mode, pick.cd);
    if (all === null) { DATASETS[pick.data].load().then(showOptions).catch(() => {}); all = DATASETS[pick.data].count || 0; }
    const n = find && pick.weak ? Math.min(20, all) : all, secs = n * pace;
    $("paceTotal").textContent = `${r.name}: ${n} × ${pace} s = ${Math.floor(secs / 60)}:${String(secs % 60).padStart(2, "0")}`;
    $("regionSummary").textContent = `${r.name} · ${all}`;
    const parts = learn ? [] : [find && pick.weak ? "Knowledge gaps" : "", pick.timer && pick.mode !== "explore" ? `Timer ${pace} s` : ""].filter(Boolean);
    $("optBadge").hidden = !parts.length; $("optBadge").textContent = parts.length; // options switched on
    $("optBtn").setAttribute("aria-label", parts.length ? `Options: ${parts.join(", ")}` : "Options");
  }
  // Game or Learning mode (both keep the World / Countries choice)
  $("setupTabs").addEventListener("click", e => {
    const b = e.target.closest("button"); if (!b) return;
    pick.learn = b.dataset.v === "learn"; pick.earth = b.dataset.v === "earth";
    if (pick.learn) pick.country = null;
    showData(); showOptions();
  });
  $("segLearnView").addEventListener("click", e => { const b = e.target.closest("button"); if (b) { pick.view = b.dataset.v; setViewSwitch(); showOptions(); } });
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
    steps.region = true; showStep("game");
    showOptions();
  });
  // the Globe / Flat switch (on = globe)
  function setViewSwitch() {
    $("viewSwitch").checked = pick.view !== "flat";
    $("viewLabel").textContent = pick.view === "flat" ? "Flat map" : "Globe";
  }
  $("viewSwitch").addEventListener("change", () => { pick.view = $("viewSwitch").checked ? "globe" : "flat"; setViewSwitch(); segSelect($("segLearnView"), pick.view); });
  // More games: History and Misc, in place of the game choices (all "soon" until they're built)
  function showMorePanel(on) {
    $("tabMore").hidden = !on; $("tabGame").hidden = on; $("setupTabs").hidden = on; $("startBtn").hidden = on || $("startBtn").dataset.wasHidden === "1";
    $("gameRow").hidden = on || pick.tab === "countries" || pick.learn || pick.earth;
    $("setupTitle").textContent = on ? "More games" : setupName();
  }
  $("moreBtn").onclick = () => {
    $("startBtn").dataset.wasHidden = $("startBtn").hidden ? "1" : "";
    $("apPanel").hidden = $("histPanel").hidden = true; document.querySelector("#tabMore .moregames").hidden = false; // the list first
    showMorePanel(true);
  };
  $("moreBack").onclick = () => {
    if (!$("apPanel").hidden) { showAirportPanel(false); return; }
    if (!$("histPanel").hidden) { showHistPanel(false); return; }
    showMorePanel(false);
  };
  // ---------- Airport codes (Misc_games.md, idea_01): the game, Easy / Hard / Capitals, the rounds, location dots ----------
  const ap = { mode: "find", level: "easy", region: "world", length: "10", dots: "off", ...(prefs.airports || {}) };
  if (!["easy", "hard", "capitals"].includes(ap.level)) ap.level = "easy";
  const AP_HINTS = { find: "A code comes up: tap where its airport is.", name: "An airport comes up: type its three-letter code.",
    namecap: "A code comes up: type the city it serves." };
  const AP_LEVELS = { easy: "The best-known airports.",
    hard: "Any airport with scheduled flights (3,268 in the world).", capitals: "The main airport of each country's capital city." };
  // Easy: the top of the best-known list for the region (a bigger region, a bigger pot)
  const AP_EASY = { world: 200, europe: 60, asia: 60, namerica: 60, samerica: 40, africa: 40, oceania: 20 };
  // Europe's Atlantic islands lie outside the Europe map: each group is drawn in its own framed inset, moved by `shift`
  // (degrees east, north) into the sea inside the map. Only in Europe games; the world map has them where they are.
  const AP_INSETS = [
    { name: "Canary Islands", box: [-18.6, 27.4, -13.0, 29.6], shift: [3.5, 7.2] },
    { name: "Madeira", box: [-17.6, 32.3, -16.0, 33.3], shift: [0, 2.6] },
    { name: "Azores", box: [-31.6, 36.5, -24.5, 40.1], shift: [6.0, 0] },
  ];
  const insetOf = ll => AP_INSETS.find(g => ll[0] >= g.box[0] && ll[0] <= g.box[2] && ll[1] >= g.box[1] && ll[1] <= g.box[3]);
  // where an airport is drawn in a region's game (moved into an inset in Europe), and whether it's on that region's map
  const apPlace = (A, code, region) => { const ll = A.airports[code].l, g = region === "europe" && insetOf(ll);
    return g ? [ll[0] + g.shift[0], ll[1] + g.shift[1]] : ll; };
  const onRegionMap = (ll, region) => { const c = REGIONS[region] && REGIONS[region].crop;
    return !c || (ll[0] >= c[0][0] && ll[0] <= c[1][0] && ll[1] >= c[0][1] && ll[1] <= c[1][1]); };
  const AP_DOTS = { off: "The airports aren't shown until you've answered them.", on: "A dot marks every airport in the game." };
  const AP_CONT = { europe: "Europe", asia: "Asia", africa: "Africa", namerica: "North America", samerica: "South America", oceania: "Oceania" };
  async function airportPot(level, region) {
    const A = await GG.airportData(), cont = AP_CONT[region];
    const inR = code => !cont || (A.airports[code].k.includes(cont) && onRegionMap(apPlace(A, code, region), region));
    if (level === "capitals") return A.capitals.filter(inR);
    if (level === "hard") return Object.keys(A.airports).filter(inR);
    return A.rank.filter(inR).slice(0, AP_EASY[region] || 60);
  }
  async function showAirportPanel(on) {
    $("apPanel").hidden = !on; document.querySelector("#tabMore .moregames").hidden = on;
    $("setupTitle").textContent = on ? "Airport codes" : "More games";
    if (!on) return;
    segSelect($("apGame"), ap.mode); segSelect($("apLevel"), ap.level); segSelect($("apRegion"), ap.region);
    segSelect($("apLength"), ap.length); segSelect($("apDots"), ap.dots);
    $("apGameHint").textContent = AP_HINTS[ap.mode];
    $("apLevelHint").textContent = AP_LEVELS[ap.level];
    $("apDotsField").hidden = ap.mode === "name"; // Name the code has no map
    $("apDotsHint").textContent = AP_DOTS[ap.dots];
    const n = (await airportPot(ap.level, ap.region)).length;
    $("apLength").querySelectorAll("button").forEach(b => { b.disabled = b.dataset.v !== "all" && +b.dataset.v > n; });
    if (ap.length !== "all" && +ap.length > n) { ap.length = "all"; segSelect($("apLength"), "all"); }
    $("apLengthHint").textContent = `${n.toLocaleString("en-GB")} airports to pick from${ap.length === "all" ? ": Marathon asks them all" : ", chosen at random"}.`;
  }
  $("apOpen").onclick = () => showAirportPanel(true);
  [["apGame", "mode"], ["apLevel", "level"], ["apRegion", "region"], ["apLength", "length"], ["apDots", "dots"]].forEach(([id, key]) => $(id).addEventListener("click", e => {
    const b = e.target.closest("button"); if (!b) return;
    ap[key] = b.dataset.v; showAirportPanel(true);
  }));
  $("apStart").onclick = async () => {
    savePrefs({ airports: { ...ap } });
    closeSetup(); closeInset(); showAirportPanel(false); showMorePanel(false);
    S.weak = false; S.timer = pick.timer; S.paceFind = pick.paceFind; S.paceName = pick.paceName;
    S.apDots = ap.dots === "on";
    const pot = await airportPot(ap.level, ap.region);
    apCodes = d3.shuffle(pot.slice()).slice(0, ap.length === "all" ? pot.length : +ap.length);
    S.data = null; apRegion = ap.region; // (a new pick each game: the map is made again)
    await startGame(ap.mode, ap.region, ap.region === "world" ? pick.view : "flat", "ap");
    main.overlay = ap.region === "europe" ? await apInsetDrawer() : null;
    main.requestDraw();
  };
  // ---------- History games (History_games.md, js/history.js): the game and what's in it, then Start ----------
  const hp = { topic: "people", game: "where", kind: "all", era: "all", region: "world", length: "10", mc: "off", level: "easy", ...(prefs.history || {}) };
  if (hp.mc !== "on") hp.mc = "off";
  const H_FIELDS = [["hGame", "game"], ["hLevel", "level"], ["hKind", "kind"], ["hEra", "era"], ["hRegion", "region"], ["hLength", "length"], ["hMC", "mc"]];
  // a grid of buttons with no empty grey cells: 4 options make a 2×2, 6 a 3×2
  const gridCols = n => (n === 4 ? 2 : n % 3 === 0 ? 3 : n <= 3 ? n : 4);
  async function showHistPanel(on) {
    $("histPanel").hidden = !on; document.querySelector("#tabMore .moregames").hidden = on;
    const T = GG.History.TOPICS[hp.topic];
    $("setupTitle").innerHTML = on ? `${T.title}<span class="beta">Beta</span>` : "More games";
    if (!on) return;
    const eras = GG.History.ERAS.filter(([v]) => !T.eras || T.eras.includes(v));
    if (!T.kinds.some(k => k[0] === hp.kind)) hp.kind = "all";
    if (!eras.some(e => e[0] === hp.era)) hp.era = "all";
    $("hWhichBtn").textContent = T.whichBtn;
    $("hKindLabel").textContent = T.kindLabel;
    $("hKind").innerHTML = T.kinds.map(([v, l]) => `<button data-v="${v}" type="button">${l}</button>`).join("");
    $("hEra").innerHTML = eras.map(([v, l]) => `<button data-v="${v}" type="button">${l}</button>`).join("");
    $("hKind").style.gridTemplateColumns = `repeat(${gridCols(T.kinds.length)}, 1fr)`;
    $("hEra").style.gridTemplateColumns = `repeat(${gridCols(eras.length)}, 1fr)`;
    $("hLevelField").hidden = !T.levels;
    $("hLevelHint").textContent = hp.level === "easy" ? "Famous" : "Obscure";
    H_FIELDS.forEach(([id, k]) => segSelect($(id), hp[k]));
    $("hGameHint").textContent = hp.game === "where" ? T.where : T.which;
    $("hAnswerField").hidden = hp.game !== "which";
    $("hMCHint").textContent = hp.mc === "on" ? "Choose from two answers." : "Type the answer.";
    // grey out the choices that would give too few (they stay readable, just can't be tapped)
    const cfgOf = over => ({ ...hp, ...over, box: (over.region || hp.region) === "world" ? null : REGIONS[over.region || hp.region].crop,
      level: T.levels ? (over.level || hp.level) : null });
    for (const [id, key] of [["hKind", "kind"], ["hEra", "era"], ["hRegion", "region"], ["hLevel", "level"]]) {
      if (key === "level" && !T.levels) continue;
      for (const b of $(id).querySelectorAll("button")) b.disabled = (await GG.History.count(cfgOf({ [key]: b.dataset.v }))) < GG.History.MIN;
    }
    const n = await GG.History.count(cfgOf({}));
    $("hLength").querySelectorAll("button").forEach(b => { b.disabled = b.dataset.v !== "all" && +b.dataset.v > n; });
    $("hStart").disabled = n < GG.History.MIN;
    $("hGameHint").textContent += ` (${n} to choose from)`;
  }
  document.querySelectorAll("#tabMore [data-topic]").forEach(b => { b.onclick = () => { hp.topic = b.dataset.topic; showHistPanel(true); }; });
  H_FIELDS.forEach(([id, key]) => $(id).addEventListener("click", e => {
    const b = e.target.closest("button"); if (!b || b.disabled) return;
    hp[key] = b.dataset.v; showHistPanel(true);
  }));
  $("hStart").onclick = async () => {
    savePrefs({ history: { ...hp } });
    closeSetup(); closeInset(); showHistPanel(false); showMorePanel(false);
    await startHistory({ ...hp, box: hp.region === "world" ? null : REGIONS[hp.region].crop });
  };
  // a History game on the world map (its own rounds and scoring: js/history.js); built on Learning mode's map
  async function startHistory(cfg) {
    await startGame("explore", cfg.region, cfg.region === "world" ? pick.view : "flat", "world");
    S.mode = "hist";
    $("jumpbar").hidden = true; // (no continent bar in the History games)
    $("giveup").hidden = false; resetGiveUp();
    $("magBtn").hidden = true; $("clock").hidden = true;
    const ok = await GG.History.start(cfg, {
      main, toast,
      home: () => goTo(cfg.region),
      // (the zoom used to be held still in these games; the user wanted to zoom in on the globe, 2026-11-18)
      lockZoom: () => {},
      unlockZoom: () => { clearTimeout(histLock); main.setCrop(cfg.region === "world" ? null : REGIONS[cfg.region].crop); },
      openMenu: () => { GG.History.stop(); openSetup(); },
    });
    if (!ok) { GG.History.stop(); S.mode = "explore"; show(); }
  }
  let histLock = null;

  // help: a short "how to play" pane, in place of the games (like More games)
  function showHelpPanel(on) {
    if (on) { $("startBtn").dataset.wasHidden = $("startBtn").hidden ? "1" : ""; showOptPanel(false); $("tabMore").hidden = true; }
    $("tabHelp").hidden = !on; $("tabGame").hidden = on; $("setupTabs").hidden = on;
    $("startBtn").hidden = on || $("startBtn").dataset.wasHidden === "1";
    $("gameRow").hidden = on || pick.tab === "countries" || pick.learn || pick.earth;
    $("helpBtn").classList.toggle("on", on);
    $("setupTitle").textContent = on ? "How to play" : setupName();
  }
  $("helpBtn").onclick = () => showHelpPanel($("tabHelp").hidden);
  $("helpBack").onclick = () => showHelpPanel(false);

  // ---------- the phone's back button: it closes what's on top instead of leaving the app ----------
  // Chrome: a CloseWatcher takes the back press (no history entry, so no page-slide animation); each press
  // closes one thing and a new watcher goes in. Other browsers: a spare history entry does the same job.
  // With nothing left to close: "Press back again to exit" (no new watcher or spare, so the next press leaves).
  // (Chrome limits watchers and history entries made without a tap, so a tap also puts one in.)
  const shown = id => $(id) && !$(id).hidden;
  function backStep() {
    if (shown("stats")) { closeStats(); return true; }
    if (shown("results")) { $("reviewBtn").click(); return true; }
    if (shown("setup")) {
      if (shown("tabHelp")) $("helpBack").click();
      else if (shown("tabOptions")) $("optBack").click();
      else if (shown("tabMore")) $("moreBack").click();
      else if (shown("countryPage")) $("cpBack").click();
      else if (shown("stepBack")) $("stepBack").click();
      else closeSetup();
      return true;
    }
    if (shown("inset")) { closeInset(); return true; }
    if (shown("layerPanel")) { GG.Earth.closePanel(); return true; }
    if (shown("learnCard")) { $("lcClose").click(); return true; }
    if (shown("nameClose")) { closeName(); return true; }
    if (shown("worldBtn")) { $("worldBtn").click(); return true; }   // a country map in Learning mode: back to the world
    if (S.mode !== "explore" && S.mode !== "earth") { openSetup(); return true; } // in a game: the menu
    return false;
  }
  const backNothing = () => toast("Press back again to exit", 2000);
  if ("CloseWatcher" in window) {
    let watcher = null;
    const arm = () => {
      if (watcher) return;
      try { watcher = new CloseWatcher(); } catch (e) { watcher = null; return; }
      watcher.onclose = () => { watcher = null; if (backStep()) arm(); else backNothing(); };
    };
    arm();
    document.addEventListener("pointerdown", arm, true);
    GG.testBack = () => (watcher ? (watcher.requestClose(), true) : false); // (tests: a back press)
  } else {
    let backSpare = false;
    const addSpare = () => { if (backSpare) return; backSpare = true; history.pushState({ gqBack: 1 }, ""); };
    document.addEventListener("pointerdown", addSpare, true);
    document.addEventListener("keydown", addSpare, true);
    window.addEventListener("popstate", () => {
      backSpare = false;
      if (backStep()) addSpare();
      else backNothing();
    });
  }
  $("startBtn").onclick = () => {
    if (!startReady()) {
      $("startWarn").textContent = `Please choose a ${!steps.region || steps.at === "region" ? "region" : "game"}`;
      $("startWarn").hidden = false;
      return;
    }
    closeSetup(); closeInset();
    if (pick.earth) { startGame("earth", "world", pick.view, "world"); return; } // Earth mode (js/earth.js)
    if (pick.learn) { magnifierIntro(() => startGame("explore", "world", pick.view, "world")); return; } // Discover: through a magnifying glass
    S.weak = pick.weak; S.timer = pick.timer; S.paceFind = pick.paceFind; S.paceName = pick.paceName; S.cd = !!pick.cd; S.ut = pick.ut !== false;
    startGame(pick.mode, pick.region, pick.region === "world" ? pick.view : "flat", pick.data);
  };

  // ---------- the start of Learning mode ("Discover"): a magnifying glass in the middle of the screen rushes towards
  // you; the map shows through its lens (magnified at first), and the rim passes out around the edges of the screen.
  // Order: the screen is covered (lens closed) and `whenShown` opens the Learning map behind it; once that's drawn,
  // the glass pops in with the new map in its lens, holds a moment, then rushes past. (Switching the map inside an
  // open lens made the globe jump.) Skipped for reduced motion.
  function magnifierIntro(whenShown) {
    if (window.matchMedia && matchMedia("(prefers-reduced-motion: reduce)").matches) { whenShown(); return; }
    const old = document.querySelector(".magintro"); if (old) old.remove();
    const W = innerWidth, H = innerHeight, cx = W / 2, cy = H / 2;
    const r0 = Math.min(W, H) * 0.17, rEnd = Math.hypot(W, H) * 0.62 + r0; // lens radius at rest, and once it's past the corners
    const ns = "http://www.w3.org/2000/svg", el = document.createElement("div");
    el.className = "magintro"; el.setAttribute("aria-hidden", "true");
    el.innerHTML = `<svg xmlns="${ns}" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}">
      <defs><mask id="magHole"><rect width="${W}" height="${H}" fill="#fff"/><circle id="magHoleC" cx="${cx}" cy="${cy}" r="0" fill="#000"/></mask></defs>
      <rect class="magshade" width="${W}" height="${H}" mask="url(#magHole)"/>
      <g id="magGlass" transform="translate(${cx} ${cy}) scale(.55)" style="opacity:0">
        <line class="maghandle" x1="${r0 * 0.74}" y1="${r0 * 0.74}" x2="${r0 * 1.62}" y2="${r0 * 1.62}"/>
        <circle class="magring" r="${r0}"/>
      </g></svg>`;
    document.body.appendChild(el);
    // no zooming while it plays: a pinch on the overlay zoomed the whole page (which then couldn't be undone), and the
    // map mustn't take gestures while it's scaled by CSS
    const block = e => e.preventDefault();
    ["wheel", "touchstart", "touchmove", "gesturestart", "gesturechange", "dblclick"].forEach(t => el.addEventListener(t, block, { passive: false }));
    main.locked = true;
    const hole = el.querySelector("#magHoleC"), glass = el.querySelector("#magGlass"), map = $("map");
    const ease = t => (t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2); // ease-in-out
    const set = (s, shadeA, glassA, lensOpen, zoom) => {
      hole.setAttribute("r", Math.max(0, r0 * s - 3) * lensOpen);
      glass.setAttribute("transform", `translate(${cx} ${cy}) scale(${s})`);
      el.querySelector(".magshade").style.opacity = shadeA; glass.style.opacity = glassA;
      map.style.transform = zoom > 1.001 ? `scale(${zoom})` : "";
    };
    const T_IN = 380, T_HOLD = 300, T_GO = 950;
    let t0 = null, holdFrom = null, goFrom = null; // (timed from animation frames, not performance.now())
    const frame = now => {
      if (t0 === null) t0 = now;
      const t = now - t0;
      if (t < T_IN) { const k = ease(t / T_IN); set(0.55 + 0.45 * k, 1, k, k, 1.35); requestAnimationFrame(frame); return; } // pops in
      if (holdFrom === null) { holdFrom = now; set(1, 1, 1, 1, 1.35); }                                                  // holds still
      if (goFrom === null) { if (now - holdFrom >= T_HOLD) goFrom = now; else { requestAnimationFrame(frame); return; } }
      const k = Math.min(1, (now - goFrom) / T_GO), e = k * k * (3 - 2 * k);                                             // rushes past
      set(Math.pow(rEnd / r0, Math.pow(e, 1.6)), 1 - Math.max(0, (e - 0.55) / 0.45), 1, 1, 1 + 0.35 * (1 - e));
      if (k < 1) requestAnimationFrame(frame); else { el.remove(); map.style.transform = ""; main.locked = false; }
    };
    set(0.55, 1, 0, 0, 1.35); // covered, lens closed
    // the map changes now, out of sight; the glass starts once it's drawn
    requestAnimationFrame(() => Promise.resolve(whenShown()).then(() => requestAnimationFrame(() => requestAnimationFrame(frame))));
  }

  // switch between the world and US states maps (US data loads the first time it's needed)
  async function useData(data) {
    if (isCountryMap(data) || isAirports(data)) await DATASETS[data].load();
    S.data = data;
    geo = geoFor(data);
    const style = isCountryMap(data) ? DATASETS[data].style : "patterson";
    main.setGeo(geo, style);
    if (insetView) insetView.setGeo(geo, style);
    GG.debug.geo = geo;
  }
  function startGame(mode, region, view, data = S.data) {
    if (main && main.overlay && S.mode !== "hist") main.overlay = null;
    if (GG.History && S.mode === "hist") { GG.History.stop(); clearTimeout(histLock); main.setCrop(null); }
    // Learning mode's whole UK & Ireland is the countries view (no county lines); counties come after "Focus on ..."
    if (mode === "explore" && (data === "uk" || data === "ukc") && (region === "uk" || region === "ukc")) { data = "ukn"; region = "ukn"; }
    // the historic counties are in Learning mode only: a game (e.g. a remembered one) uses the ceremonial counties
    if (mode !== "explore" && data === "uk") { data = "ukc"; region = region.replace(/^uk(?!c)/, "ukc"); }
    if (data !== S.data || !geo) return useData(data).then(() => startGame(mode, region, view, data));
    // a country map's own regions (England, Scotland...), or else the whole map
    if (isCountryMap(data)) { if (dataOfRegion(region) !== data) region = DATASETS[data].region; view = "flat"; }
    S.mode = mode; S.region = region;
    savePrefs({ game: { mode, region, data, cd: !!S.cd, ut: S.ut !== false, weak: !!S.weak, timer: !!S.timer, paceFind: S.paceFind || 5, paceName: S.paceName || 10 },
      ...(region === "world" ? { worldView: view } : {}) });
    // region games are cropped to the region (no jump bar there)
    main.setCrop(region === "world" ? null : REGIONS[region].crop);
    // (no map in Name the flags; no continent bar in the airport games, 2026-11-18)
    $("jumpbar").hidden = region !== "world" || mode === "nameflag" || isAirports(data);
    $("magBtn").hidden = mode === "explore" || mode === "earth"; // no magnifier in Learning mode or Earth mode
    // Earth mode (js/earth.js): its layers on the world map; its own country-borders switch in the Layers panel
    $("bordersBtn").hidden = mode === "earth";
    if (mode === "earth") GG.Earth.enter(main);
    else if (main.earth) { GG.Earth.leave(main); setBorders(prefs.borders !== false); }
    if (mode === "explore" && S.magnify) setMag(false);
    $("viewBtn").hidden = region !== "world"; // no globe for region games
    $("worldBtn").hidden = !(mode === "explore" && isCountryMap(data)); // back from Focus on a country
    // counties -> the countries view (Ireland opened on its own goes back to the world map)
    $("worldBtn").textContent = (data === "uk" || data === "ukc") && !(/-ire$/.test(region) && !viewBefore.ukn) ? "‹ UK & Ireland" : "‹ World map";
    // Britain and Ireland's Learning map: switch between the two county sets
    // Britain and Ireland: the sources' credit lines (required by their licences), on the map in every UK game
    const ukMap = data === "uk" || data === "ukc" || data === "ukn";
    $("mapCredit").hidden = !ukMap;
    if (ukMap) $("mapCredit").innerHTML = (data !== "ukc"
      ? 'Counties: <a href="https://www.county-borders.co.uk" target="_blank" rel="noopener">Historic County Borders Project</a>'
      : "Contains OS data © Crown copyright and database right 2026") +
      '. Ireland © <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener">OpenStreetMap</a> contributors. Flags: UK Flag Registry.';
    main.disputes = mode === "explore" ? disputesList.filter(d => !d.country) : null; // disputed territories: Learning mode only
    const ukLearn = mode === "explore" && (data === "uk" || data === "ukc");
    // (and the countries with two sets built by tools/build_country.py: Belgium's provinces and regions)
    const setLearn = mode === "explore" && !!SETS[data] && !!NEW_MAPS[data];
    $("setBtn").hidden = !ukLearn && !setLearn;
    if (ukLearn) $("setBtn").textContent = data === "uk" ? "Ceremonial counties" : "Historic counties";
    if (setLearn) $("setBtn").textContent = DATASETS[SETS[data].find(x => x !== data)].Nouns;
    if (main.mode !== view) { main.setMode(view); setViewButton(); }
    goTo(region, false);
    hideLearnCard();
    $("reviewBar").hidden = true; reviewSel = null;
    showTimeline(mode === "explore" && ["us", "ru", "au", "br"].includes(data), ["ru", "au", "br"].includes(data) ? data : "us");
    useSub(false); // no state lines on the world Learning map: states are on each country's own map ("Focus on ...")
    showReserves();
    if (mode !== "nameflag") hideFlagGrid();
    if (mode === "explore" || mode === "earth") { Object.keys(state).forEach(k => delete state[k]); selected = null; startTime = 0; clearInterval(clockTimer); tickClock(); show(); } else newGame();
  }

  document.addEventListener("keydown", e => {
    if (e.key === "Escape") { e.preventDefault(); closeSetup(); closeInset(); closeResults(); closeStats(); }
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
    main = new GG.MapView($("map"), { geo, mode: "globe", flatStyle: style, getState, onTap: tap, onPoint, onDispute: (d) => { if (S.mode === "explore") { Object.keys(state).forEach(k => delete state[k]); selectSub(null); showDisputeCard(d); main.selDispute = d; redraw(); } },
      isTarget: c => c === target, isActive: inRegion, isOpen, showCapital, isUnformed,
      dotShown: c => S.apDots || finished || !!state[c.iso] || apShown.has(c) });
    main.lookAt(15, 25, 120, false);
    GG.Earth.init({ card: earthCard, cardMore: text => earthCardMore(text), hideCard: hideLearnCard, toast, setBorders });
    buildRegionButtons();
    GG.debug = { main, geo, startGame, preload: d => DATASETS[d].load(), inset: () => insetView, get geoUS() { return geoUS; }, get geoCA() { return geoCA; } };
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
      const mode = ["find", "name", "findcap", "namecap", "findflag", "nameflag", "explore", "earth"].includes(g.mode) ? g.mode : "find";
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
    window.matchMedia("(prefers-color-scheme: dark)").addEventListener("change", themeChanged);
  }
  start();
})();
