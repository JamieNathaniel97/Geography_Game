// The live earthquake module (js/quakes-live.js, not in the app yet): the USGS feed, the cache, the offline fallback.
// Needs the internet: python tests/run.py --online
T.run(async () => {
  await new Promise((res, rej) => { const s = document.createElement("script"); s.src = "js/quakes-live.js"; s.onload = res; s.onerror = rej; document.head.appendChild(s); });
  const Q = GG.QuakesLive;
  const a = await Q.load({ range: "month", mag: "4.5", force: true });
  T.check("the month's M4.5+ quakes load", !a.offline && a.count > 50, `${a.count} quakes`);
  T.check("each quake has a place, a time and a magnitude", a.quakes.every(q => isFinite(q.mag) && q.time && isFinite(q.lon) && isFinite(q.lat)));
  T.check("biggest first", a.quakes.every((q, i) => i === 0 || a.quakes[i - 1].mag >= q.mag));
  const b = await Q.load({ range: "month", mag: "4.5" });
  T.check("a second call within 5 minutes uses the cache", b.generated === a.generated);
  const orig = window.fetch; window.fetch = () => Promise.reject(new Error("offline"));
  const c = await Q.load({ range: "month", mag: "4.5", force: true }), d = await Q.load({ range: "week", mag: "1.0", force: true });
  window.fetch = orig;
  T.check("offline: the cached copy, marked as old", c.stale && c.count === a.count);
  T.check("offline with nothing cached: an empty, offline answer", d.offline && d.count === 0);
  T.eq("the dot size grows with the magnitude", Q.radius(6.5) > Q.radius(4.5), true);
  T.eq("depth bands", [Q.depthBand(10), Q.depthBand(100), Q.depthBand(500)].join(","), "shallow,intermediate,deep");
});
