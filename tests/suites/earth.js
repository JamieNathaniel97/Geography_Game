// Earth mode (jobs/geoscience.md, stage 1): the menu tab, the layers, taps on every kind of feature on the globe and
// the flat map, the Layers panel, leaving and coming back.
T.run(async () => {
  const { $, W } = T;
  await T.ready();
  const m = GG.debug.main, E = GG.Earth;
  $("menuBtn").click(); await W(300);
  $("setupTabs").querySelector('[data-v="earth"]').click(); await W(200);
  T.eq("the Earth tab's title", $("setupTitle").textContent, "Earth");
  T.check("the Earth tab shows its panel, not the world games", !$("earthPanel").hidden && $("segData").hidden && $("worldPanel").hidden);
  $("startBtn").click(); await W(400);
  T.eq("Earth mode's banner", $("eyebrow").textContent, "Earth");
  T.check("the Layers button is shown and the Borders chip hidden", !$("layersBtn").hidden && $("bordersBtn").hidden);
  T.check("the map is in Earth mode (layers drawn, no country markers, no borders)", m.earth === E && m.noMarkers && !m.borders);
  const all = ["plates", "boundaries", "features", "volcanoes", "hotspots", "ring", "seas"];
  E.state.on = new Set(all);
  await Promise.all(all.map(id => E.need(id)));
  m.requestDraw(); await W(500);
  // every plate and sea the right way round: the plates add up to the whole sphere
  const pa = E.state.data.plates.features.map(f => d3.geoArea(f));
  T.check("the plates cover the sphere exactly once", Math.abs(pa.reduce((a, b) => a + b, 0) / (4 * Math.PI) - 1) < 0.001);
  const inside = E.state.data.seas.features.filter(f => d3.geoArea(f) > 2 * Math.PI).map(f => f.properties.name);
  T.check("no sea is inside out", !inside.length, inside.join(", "));
  T.metric("named features", E.state.data.features.features.length);
  T.metric("volcanoes", E.state.data.volcanoes.length);
  const tapLL = async ll => { m.lookAt(ll[0], ll[1], 40, false); await W(450); const p = T.screenOf(ll); T.tap(p[0], p[1]); await W(350); return T.card(); };
  const lineMid = f => { const g = f.geometry, l = g.type === "LineString" ? g.coordinates : g.coordinates.slice().sort((a, b) => b.length - a.length)[0]; return l[Math.floor(l.length / 2)]; };
  const feat = id => E.state.data.features.features.find(f => f.properties.id === id);
  const layers = ids => { E.state.on = new Set(ids); m.requestDraw(); return W(300); };
  for (const view of ["globe", "flat"]) {
    if (m.mode !== view) { m.setMode(view); await W(500); }
    await layers(all);
    m.lookAt(15, 37.7, 6, false); await W(600);
    const h = E.state.hits.volc.find(h => h.v.name === "Etna");
    if (T.check(`${view}: Etna is drawn`, !!h)) { T.tap(h.x, h.y); await W(400); T.eq(`${view}: a tap on Etna`, T.card(), "Etna"); }
    await T.until(() => /Sicily|Etna/.test($("lcMore").textContent), 5000);
    T.check(`${view}: Etna's card has the Smithsonian's summary`, /Sicily|Etna/.test($("lcMore").textContent));
    T.eq(`${view}: a hotspot over a volcano (Hawaii)`, await tapLL([-155.3, 19.4]), "Hawaii hotspot");
    for (const [id, name] of [["mar", "Mid-Atlantic Ridge"], ["mariana", "Mariana Trench"], ["sanandreas", "San Andreas Fault"], ["ear", "East African Rift"], ["epr", "East Pacific Rise"]])
      T.eq(`${view}: ${name}`, await tapLL(lineMid(feat(id))), name);
    await layers(all.filter(id => id !== "features"));
    const b = E.state.data.boundaries.features.find(f => f.properties.plates.includes("NZ") && f.properties.plates.includes("PA"));
    T.eq(`${view}: a plain boundary`, await tapLL(lineMid(b)), "Nazca–Pacific boundary");
    await layers(["ring"]);
    T.eq(`${view}: the Ring of Fire`, await tapLL([142.2, 11.3]), "Ring of Fire");
    await layers(["plates", "seas"]);
    T.eq(`${view}: a sea`, await tapLL([-75, 15]), "Caribbean Sea");
    T.eq(`${view}: an ocean`, await tapLL([-40, 35]), "North Atlantic Ocean");
    T.eq(`${view}: a plate, on land`, await tapLL([20, 5]), "Africa plate");
    await layers(["plates"]);
    T.eq(`${view}: the Pacific plate`, await tapLL([-150, 0]), "Pacific plate");
    T.eq(`${view}: the Nazca plate`, await tapLL([-90, -15]), "Nazca plate");
    await layers(["volcanoes"]);
    T.eq(`${view}: empty sea with only Volcanoes on`, await tapLL([-30, -40]), "(no card)");
  }
  // the Layers panel: a group, a checkbox, country borders, the back button
  $("layersBtn").click(); await W(200);
  $("layerGroups").querySelector('[data-g="1"]').click(); await W(200);
  T.eq("the Ring of Fire group ticks its layers", [...E.state.on].sort().join(","), "features,ring,volcanoes");
  T.eq("…and the checkboxes follow", [...$("layerList").querySelectorAll("input:checked")].map(i => i.dataset.l).sort().join(","), "features,ring,volcanoes");
  T.check("…and the group is lit", $("layerGroups").querySelector('[data-g="1"]').classList.contains("on"));
  const cb = $("layerList").querySelector('[data-l="countries"]'); cb.click(); await W(100);
  T.check("the Country borders checkbox shows the borders", m.borders); cb.click(); await W(100);
  const bk = GG.testBack ? GG.testBack() : false; await W(300);
  T.check("back closes the Layers panel", bk && $("layerPanel").hidden);
  // leaving Earth mode puts the map back
  await T.start("find", "world", "globe", "world");
  T.check("leaving Earth mode: layers off, markers and the Borders chip back", !m.earth && !m.noMarkers && !$("bordersBtn").hidden && $("layersBtn").hidden && m.borders);
  await T.start("earth", "world", "flat", "world");
  $("menuBtn").click(); await W(300);
  T.eq("the menu reopens on the Earth tab", ($("setupTabs").querySelector(".on") || {}).dataset.v, "earth");
});
