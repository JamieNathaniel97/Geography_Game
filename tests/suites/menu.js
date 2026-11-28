// The New game menu and the country maps around it: the Countries list, Belgium's two sets, Spain's, a Belgium regions
// game, the stats tabs, Focus on Austria from the world Learning map, South Africa's enclaves, Sweden's coats of arms,
// the US and Russia timelines.
T.run(async () => {
  const { $, W } = T;
  await T.ready();
  if ($("setup").hidden) $("menuBtn").click(); await W(300);
  $("segData").querySelector('[data-v="countries"]').click(); await W(300);
  const want = ["AUT", "CZE", "POL", "NLD", "BEL", "SWE", "ZAF", "NZL", "PRT", "COL", "CHE", "CHL", "MYS", "KOR", "PER", "EGY",
    "USA", "CAN", "GBR", "IRL", "IND", "CHN", "RUS", "AUS", "MEX", "BRA", "DEU", "JPN", "FRA", "ITA", "ESP", "NGA", "ARG"];
  const missing = want.filter(k => { const b = $("countryList").querySelector(`[data-v="${k}"]`); return !b || b.disabled; });
  T.check("every country map is listed and can be opened", !missing.length, missing.join(", "));
  T.check("Belgium's regions set isn't listed on its own", !$("countryList").querySelector('[data-v="ber"]'));
  const open = async k => { $("countryList").querySelector(`[data-v="${k}"]`).click(); await W(300); };
  const setTxt = () => [...$("cpES").querySelectorAll("button")].map(b => b.textContent + (b.classList.contains("on") ? "*" : "")).join(" | ");
  await open("BEL");
  T.check("Belgium's page shows the set switch", !$("cpESField").hidden);
  T.eq("Belgium's sets", setTxt(), "Provinces (11)* | Regions (3)");
  T.check("Belgium's flag games are shown", !$("cpGames").querySelector('[data-v="findflag"]').hidden);
  $("cpES").querySelector('[data-v="ber"]').click(); await W(300);
  T.eq("Belgium's sets after choosing Regions", setTxt(), "Provinces (11) | Regions (3)*");
  T.eq("the Find button says Regions", $("cpGames").querySelector('[data-v="find"]').textContent, "Regions");
  $("cpGames").querySelector('[data-v="find"]').click(); await W(200);
  $("startBtn").click();
  await T.until(() => GG.debug.geo && GG.debug.geo.kind === "ber", 8000); await W(800);
  T.eq("a Belgium regions game loads the regions map", GG.debug.geo.kind, "ber");
  $("statsBtn").click(); await W(400);
  T.eq("stats open on that game's map, labelled", $("statsSkill").querySelector('[data-v="country"]').textContent, "Regions");
  for (const d of ["at", "cz", "pl", "nl", "be"]) { $("statsData").querySelector(`[data-v="${d}"]`).click(); await W(150); }
  T.eq("stats tabs switch (last: Belgium's provinces)", $("statsSkill").querySelector('[data-v="country"]').textContent, "Provinces");
  $("statsClose").click(); await W(200);
  $("menuBtn").click(); await W(300); $("segData").querySelector('[data-v="countries"]').click(); await W(300);
  if (!$("countryPage").hidden) { $("cpBack").click(); await W(200); }
  await open("ESP");
  T.eq("Spain's sets", setTxt(), "Communities (19)* | Provinces (52)");
  $("setupClose").click(); await W(300);
  // the world Learning map: a tap on Austria, then Focus on Austria
  await T.start("explore", "world", "flat", "world"); await W(800);
  const m = GG.debug.main, at = GG.debug.geo.byIso.AUT;
  m.lookAt(14, 47.5, 20, false); await W(500);
  const p = T.screenOf(d3.geoCentroid(at.feature)); T.tap(p[0], p[1]); await W(500);
  T.eq("a tap on Austria opens its card", T.card(), "Austria");
  T.eq("the Focus button", $("focusBtn").hidden ? "hidden" : $("focusBtn").textContent, "Focus on Austria ›");
  $("focusBtn").click(); await T.until(() => GG.debug.geo.kind === "at", 8000); await W(500);
  T.eq("Focus opens Austria's map", GG.debug.geo.kind, "at");
  T.eq("the back button", $("worldBtn").hidden ? "hidden" : $("worldBtn").textContent, "‹ World map");
  // South Africa: Lesotho and Eswatini are in Learning mode only
  await T.start("find", "southafrica", "flat", "za"); await W(400);
  { const g = GG.debug.geo, mm = GG.debug.main;
    T.check("South Africa's game leaves out Lesotho and Eswatini", !mm.active(g.byIso["ZA-LS"]) && !mm.active(g.byIso["ZA-SZ"]) && mm.active(g.byIso["ZA-GT"])); }
  await T.start("explore", "southafrica", "flat", "za"); await W(400);
  T.check("South Africa's Learning map has Lesotho", GG.debug.main.active(GG.debug.geo.byIso["ZA-LS"]));
  // Sweden: coats of arms, not flags
  await T.start("findflag", "sweden", "flat", "se"); await W(400);
  T.eq("Sweden's emblem game is by coat of arms", $("eyebrow").textContent, "Find by coat of arms · Sweden");
  // the US and Russia Learning maps have their timelines
  for (const [reg, d] of [["usa", "us"], ["russia", "ru"]]) {
    await T.start("explore", reg, "flat", d); await W(400);
    T.eq(`${d}: the Learning map loads`, GG.debug.geo.kind, d);
    T.check(`${d}: the timeline is shown`, !$("timeline").hidden);
  }
});
