// One country map (?d=<dataset>&r=<region>), in Learning mode: every part opens its own card from its anchor; names,
// unaccented names and capitals are accepted; capitals have dots; flags load; the tap test (tools/tap_test.js) at the
// whole map and zoomed in, where the detail level loads. Counts, accuracy and the known name and capital quirks of the
// older maps are metrics, compared with tests/baseline.json (they mustn't change without a reason).
T.run(async () => {
  const { $, W, Q } = T, D = Q.get("d"), R = Q.get("r");
  await T.ready();
  const m = GG.debug.main;
  // the UK's county maps open by nation in Learning mode (the whole UK is the nations' map)
  const regions = D === "uk" || D === "ukc" ? ["-eng", "-sco", "-wal", "-ire"].map(s => D + s) : [R];
  const settle = async () => { for (let i = 0, k = ""; i < 40; i++) { await W(60); const n = m.t.x + "," + m.t.y + "," + m.t.k; if (n === k) return; k = n; } };
  const pointOf = c => { const r = m.hits.rings.find(h => h.c === c); if (r) return [r.x, r.y]; return m.projection()(c.anchorLL || d3.geoCentroid(c.feature)); };
  let ok = 0, n = 0; const bad = [];
  for (const reg of regions) {
    await T.start("explore", reg, "flat", D); await W(700);
    if (!T.eq(`the map loads (${reg})`, GG.debug.geo.kind, D)) return;
    // 1. every part's own card from its anchor (its name first: Japan's cards add the Japanese name)
    for (const c of GG.debug.geo.countries.filter(c => m.active(c))) {
      await settle(); const p = pointOf(c); T.tap(p[0], p[1]); await W(150); n++;
      if (T.card() === c.name || T.card().startsWith(c.name + " ")) ok++; else bad.push(c.name + " > " + T.card());
    }
  }
  const g = GG.debug.geo;
  T.metric("parts", g.countries.length);
  // (by design: the middle of a small part's circle counts as the small part, and the City of London's circle is at
  // Greater London's middle)
  const KNOWN = ["Greater London > City of London"];
  const unexpected = bad.filter(b => !KNOWN.includes(b));
  T.check("every part opens its own card", !unexpected.length, unexpected.slice(0, 8).join(", "));
  if (bad.length > unexpected.length) T.info("known: " + bad.filter(b => KNOWN.includes(b)).join(", "));
  T.metric("parts opening their card", ok);
  // 2. names: each part's names, unaccented names and capitals are accepted; the old maps' known cross-matches are a metric
  const fold = s => s.normalize("NFD").replace(/[̀-ͯ]/g, "").replace(/ł/g, "l").replace(/Ł/g, "L");
  const nBad = [], cross = [];
  for (const c of g.countries) {
    for (const s of c.names) { if (!GG.nameMatches(c, s)) nBad.push(`${c.name}: ${s}`); if (!GG.nameMatches(c, fold(s))) nBad.push(`${c.name} unaccented: ${fold(s)}`); }
    for (const s of c.capitals) { if (!GG.nameMatches(c, s, "capitals")) nBad.push(`${c.name} capital: ${s}`); if (!GG.nameMatches(c, fold(s), "capitals")) nBad.push(`${c.name} capital unaccented: ${fold(s)}`); }
    for (const t of c.notTypo || []) if (GG.nameMatches(c, t)) cross.push(`${c.name} accepts ${t}`);
    for (const o of g.countries) if (o !== c) for (const s of o.names) if (GG.nameMatches(c, s)) cross.push(`${c.name} accepts ${o.name}'s ${s}`);
  }
  T.check("every part's names, unaccented names and capitals are accepted", !nBad.length, nBad.slice(0, 8).join(" | "));
  T.metric("names accepted for another part", cross.sort().join(" | ") || "none");
  // 3. capitals and flags
  T.metric("capitals without a dot", g.countries.filter(c => c.capitals.length && !(c.capLL && c.capLL.length)).map(c => c.name).sort().join(", ") || "none");
  let fOk = 0; const fBad = [];
  for (const c of g.countries) if (c.info.flag) { const r = await fetch(`data/flags/${c.flagKey}.webp`); if (r.ok) fOk++; else fBad.push(c.name); }
  T.check("every flag listed loads", !fBad.length, fBad.join(", "));
  T.metric("flags", fOk);
  // 4. the tap test, at the whole map and zoomed in (where the detail level takes over)
  const src = await (await fetch("tools/tap_test.js")).text();
  (0, eval)(src.slice(0, src.indexOf("setTimeout(()=>{try{const m=GG.debug.main")));
  const pct = s => { const x = /([\d.]+)%/.exec(s); return x ? +x[1] : 0; };
  if (!$("learnCard").hidden) $("lcClose").click();
  await settle();
  let r = run(m, g, "whole map"); T.info(r);
  T.check("the canvas and the map agree on size", /size OK/.test(r));
  T.metric("tap accuracy, whole map (%)", pct(r));
  const big = g.countries.filter(c => m.active(c) && !c.info.enclave).sort((a, b) => (b.info.pop || 0) - (a.info.pop || 0))[0];
  const zoomIn = f => { const q = pointOf(big); m.sel.call(m.zoom.transform, d3.zoomIdentity.translate(m.w / 2 - (q[0] - m.t.x) * f, m.h / 2 - (q[1] - m.t.y) * f).scale(m.t.k * f)); };
  zoomIn(2.5); await W(1500); m.draw();
  r = run(m, g, "zoom x2.5"); T.info(r); T.metric("tap accuracy, zoom x2.5 (%)", pct(r));
  zoomIn(3); for (let i = 0; i < 30 && !m.detailOn; i++) { await W(200); m.draw(); }
  if (!m.detailOn) { zoomIn(3); for (let i = 0; i < 30 && !m.detailOn; i++) { await W(200); m.draw(); } }
  T.metric("detail level loads zoomed in", m.detailOn ? "yes" : "no");
  const saved = new Map();
  if (m.detailOn && m.detailFcs) for (const c of g.countries) {
    const fs = m.detailFcs.flatMap(fc => fc.features.filter(f => f.c === c));
    if (fs.length) { saved.set(c, c.feature); c.feature = { type: "FeatureCollection", features: fs }; }
  }
  r = run(m, g, "zoomed in"); T.info(r); T.metric("tap accuracy, zoomed in (%)", pct(r));
  saved.forEach((f, c) => { c.feature = f; });
});
