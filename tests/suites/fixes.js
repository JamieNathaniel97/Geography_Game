// The fixes of 2026-11-27: a missed (red) country doesn't count as a guess; Ireland has its own page; the Countries list
// is alphabetical in each continent; the historic counties are in Learning mode only.
T.run(async () => {
  const { $, W } = T;
  await T.ready();
  const m = GG.debug.main;
  if ($("setup").hidden) $("menuBtn").click(); await W(300);
  $("setupTabs").querySelector('[data-v="game"]').click(); await W(200);
  $("segData").querySelector('[data-v="countries"]').click(); await W(300);
  for (const det of $("countryList").querySelectorAll("details")) {
    const names = [...det.querySelectorAll("button span")].map(s => s.textContent);
    const sorted = [...names].sort((a, b) => a.localeCompare(b, "en"));
    T.check(`the Countries list is alphabetical (${det.dataset.cont})`, JSON.stringify(names) === JSON.stringify(sorted), names.join(", "));
  }
  $("countryList").querySelector('[data-v="IRL"]').click(); await W(300);
  T.eq("Ireland's page title", $("cpName").textContent, "Ireland");
  T.check("Ireland's page has no UK options", $("cpOpts").hidden);
  T.check("Ireland's page has no flag games", $("cpGames").querySelector('[data-v="findflag"]').hidden);
  $("cpGames").querySelector('[data-v="find"]').click(); await W(150); $("startBtn").click();
  await T.until(() => GG.debug.geo && /^uk/.test(GG.debug.geo.kind || ""), 8000); await W(1200);
  T.eq("an Ireland game uses the ceremonial counties' map", GG.debug.geo.kind, "ukc");
  T.eq("an Ireland game has its 32 counties", GG.debug.geo.countries.filter(c => m.active(c)).length, 32);
  $("menuBtn").click(); await W(300); $("segData").querySelector('[data-v="countries"]').click(); await W(300);
  if (!$("countryPage").hidden) { $("cpBack").click(); await W(200); }
  $("countryList").querySelector('[data-v="GBR"]').click(); await W(300);
  T.eq("the UK page title", $("cpName").textContent, "Britain & Ireland");
  T.check("the UK page has its options", !$("cpOpts").hidden);
  T.check("the UK page has no county-set switch (games: ceremonial only)", $("cpSetField").hidden);
  T.eq("the UK page's regions", [...$("cpRegion").querySelectorAll("button")].map(b => b.textContent).join("/"), "All/England/Scotland/Wales/Ireland");
  $("setupClose").click(); await W(300);
  // a missed (red) country: tapping it again counts nothing
  await T.start("find", "europe", "flat", "world"); await W(700);
  const g = GG.debug.geo, tgt = () => g.countries.find(c => c.name === $("target").textContent.trim());
  const tapC = async c => { const p = T.screenOf(c.anchor || d3.geoCentroid(c.feature)); T.tap(p[0], p[1]); await W(400); };
  const missed = [], used = new Set();
  for (let i = 0; i < 5; i++) {
    const t = tgt(); missed.push(t); used.add(t);
    const w = g.countries.find(c => m.active(c) && !used.has(c) && c !== t && c.feature && c.name !== "Russia" && d3.geoArea(c.feature) > 3e-4);
    used.add(w); await tapC(w);
  }
  const before = $("score").textContent;
  const red = missed.filter(c => c.feature).sort((a, b) => d3.geoArea(b.feature) - d3.geoArea(a.feature))[0];
  await tapC(red);
  T.eq(`tapping a missed (red) country (${red.name}) counts nothing`, $("score").textContent, before);
  // Learning mode: Ireland from the Countries list opens its counties; back goes to the world map
  $("menuBtn").click(); await W(300); $("setupTabs").querySelector('[data-v="learn"]').click(); await W(200);
  $("segData").querySelector('[data-v="countries"]').click(); await W(300);
  $("countryList").querySelector('[data-v="IRL"]').click();
  await T.until(() => GG.debug.geo && /^uk/.test(GG.debug.geo.kind || ""), 8000); await W(1200);
  T.check("Learning mode: Ireland opens on its counties", /^ukc?$/.test(GG.debug.geo.kind), GG.debug.geo.kind);
  T.eq("Learning mode: Ireland's back button", $("worldBtn").textContent, "‹ World map");
  T.eq("stats: the UK has one tab", [...$("statsData").querySelectorAll("button")].map(b => b.dataset.v).filter(v => /^uk/.test(v)).join(","), "ukc");
});
