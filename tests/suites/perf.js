// Speed: how long the app takes to start, and how long one draw of the map takes in each main view (the average of
// 30 draws, called directly). Metrics ending "(ms)" are lower-is-better: tests/run.py fails one that's more than 30%
// slower than its baseline (timings vary from run to run). The runner runs this suite on its own, after the others.
T.run(async () => {
  const { W } = T;
  await T.ready();
  T.metric("startup (ms)", Math.round(T.startedMs));
  const m = GG.debug.main;
  const time = async (label, setup, moving = false) => {
    await setup(); await W(800);
    m.moving = moving; m.draw(); m.draw(); // (warm up: paths built, tiles loaded)
    const n = 30, t0 = performance.now();
    for (let i = 0; i < n; i++) m.draw();
    T.metric(`draw: ${label} (ms)`, +((performance.now() - t0) / n).toFixed(2));
  };
  await time("world globe, Find", () => T.start("find", "world", "globe", "world"));
  await time("world flat, Find", () => T.start("find", "world", "flat", "world"));
  await time("world flat zoomed in (Europe)", async () => { await T.start("explore", "world", "flat", "world"); m.lookAt(10, 50, 25, false); });
  await time("world globe, Learning mode", () => T.start("explore", "world", "globe", "world"));
  const E = GG.Earth, all = ["plates", "boundaries", "features", "volcanoes", "hotspots", "ring", "seas"];
  await time("Earth mode, globe, every layer", async () => { await T.start("earth", "world", "globe", "world"); E.state.on = new Set(all); await Promise.all(all.map(id => E.need(id))); });
  await time("Earth mode, flat, every layer", async () => { m.setMode("flat"); m.lookAt(0, 20, 300, false); });
  await time("Russia's map (85 regions)", () => T.start("explore", "russia", "flat", "ru"));
  await time("the UK's historic counties", () => T.start("explore", "uk", "flat", "uk"));
  // a spin on the globe: draws while moving (the lighter outlines)
  await time("world globe while spinning", () => T.start("find", "world", "globe", "world"), true);
  m.moving = false;
});
