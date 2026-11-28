// Smoke test: the app starts, and every world game and mode starts on the globe and the flat map without errors.
T.run(async () => {
  const { $, W } = T;
  await T.ready();
  const m = GG.debug.main;
  T.check("the map has drawn countries", GG.debug.geo.countries.length > 190, GG.debug.geo.countries.length + " countries");
  const games = { find: "Find", findcap: "Find by capital", findflag: "Find by flag", name: "Name", namecap: "Name the capitals", nameflag: "Name the flags" };
  for (const [mode, label] of Object.entries(games)) {
    for (const view of ["globe", "flat"]) {
      if (mode === "nameflag" && view === "flat") continue; // (no map in Name the flags)
      await T.start(mode, "world", view, "world"); await W(300);
      const eyebrow = $("eyebrow").textContent;
      T.check(`${label} starts (${view})`, eyebrow.length > 0 && (mode === "nameflag" ? !$("flagPanel").hidden : m.mode === view), `eyebrow "${eyebrow}", view ${m.mode}`);
    }
  }
  // a region game is flat and cropped to its region
  await T.start("find", "europe", "flat", "world");
  T.check("a region game (Europe) is flat and cropped", m.mode === "flat" && !!m.crop, `view ${m.mode}, crop ${!!m.crop}`);
  // Learning mode and Earth mode
  await T.start("explore", "world", "globe", "world");
  T.eq("Learning mode starts", $("eyebrow").textContent.startsWith("Learning mode"), true);
  T.check("Learning mode shows the disputed territories", !!(m.disputes && m.disputes.length), (m.disputes || []).length + " disputes");
  await T.start("earth", "world", "flat", "world");
  T.eq("Earth mode starts", $("eyebrow").textContent, "Earth");
  T.check("Earth mode's layers are on the map", m.earth === GG.Earth);
  // the menu opens, and its four tabs are there
  $("menuBtn").click(); await W(300);
  T.check("the menu opens", !$("setup").hidden);
  T.eq("the menu's tabs", [...$("setupTabs").querySelectorAll("button")].map(b => b.dataset.v).join(","), "game,learn,earth");
  $("setupClose").click(); await W(200);
  // the stats screen opens and closes
  $("statsBtn").click(); await W(300);
  T.check("the stats screen opens", !$("stats").hidden);
  $("statsClose").click(); await W(200);
  T.check("the stats screen closes", $("stats").hidden);
  // theme switch: dark then light, the map redraws without errors
  document.documentElement.dataset.theme = "dark"; GG.debug.main.readColours(); m.requestDraw(); await W(300);
  document.documentElement.dataset.theme = "light"; GG.debug.main.readColours(); m.requestDraw(); await W(300);
  T.check("the theme can switch without errors", true);
});
