// The test harness, loaded into the app's page before a suite (tests/run.py serves /_test/<suite> as index.html with
// this file and tests/suites/<suite>.js added). A suite reports through T:
//   T.check(name, ok, detail)   a pass or a fail
//   T.metric(name, value)       a number or text the runner compares with tests/baseline.json (it must not get worse)
//   T.info(text)                shown with -v
//   T.done()                    the suite has finished (the runner waits for it)
// Messages go to the runner in order (/_t?run=..&k=..&m=..). A script error or unhandled rejection is a fail.
(function () {
  const Q = new URLSearchParams(location.search), RUN = Q.get("run") || "manual";
  let chain = Promise.resolve();
  const post = (k, m) => {
    chain = chain.then(() => fetch("/_t?" + new URLSearchParams({ run: RUN, k, m: String(m) }), { keepalive: true }).catch(() => {}));
    return chain;
  };
  const W = ms => new Promise(r => setTimeout(r, ms));
  const $ = id => document.getElementById(id);
  (window.__gqErrors || []).forEach(m => post("fail", "script error before the tests started: " + m));
  window.addEventListener("error", e => post("fail", `script error: ${e.message} @ ${(e.filename || "").split("/").pop()}:${e.lineno}`));
  window.addEventListener("unhandledrejection", e => post("fail", `unhandled rejection: ${e.reason && (e.reason.stack || e.reason.message || e.reason)}`));
  const T = {
    Q, W, $,
    check(name, ok, detail) { post(ok ? "pass" : "fail", name + (detail !== undefined && detail !== "" ? ` (${detail})` : "")); return !!ok; },
    // equal: a check that shows what it got when it fails
    eq(name, got, want) { return T.check(name, got === want, got === want ? "" : `got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`); },
    metric(name, value) { post("metric", JSON.stringify([name, value])); },
    info(text) { post("info", text); },
    done() { return post("done", ""); },
    // run a suite body: catches exceptions as a fail, always ends with done
    async run(body) {
      try { await body(); } catch (e) { post("fail", "exception: " + (e.stack || e.message || e)); }
      await T.done();
    },
    // wait for fn() to be true (polling), up to ms; returns whether it became true
    async until(fn, ms = 10000, step = 100) {
      const t0 = Date.now();
      while (Date.now() - t0 < ms) { try { if (fn()) return true; } catch (e) { /* not yet */ } await W(step); }
      return false;
    },
    // the app has started (map data loaded, splash gone); the New game menu it opens with is closed
    async ready() {
      if (Q.get("theme")) document.documentElement.dataset.theme = Q.get("theme");
      const t0 = Date.now();
      const ok = await T.until(() => window.GG && GG.debug && GG.debug.main && GG.debug.main.geo, 120000);
      T.startedMs = performance.now(); // (from the page's start: the perf suite reports it)
      T.info(`the app started in ${(T.startedMs / 1000).toFixed(1)} s`);
      if (!ok) throw new Error("the app didn't start: " + JSON.stringify({ GG: !!window.GG, debug: !!(window.GG && GG.debug), main: !!(window.GG && GG.debug && GG.debug.main), target: (document.getElementById("target") || {}).textContent, splash: !!document.querySelector(".splash:not([hidden])") }));
      await W(4000);
      if (!$("setup").hidden) $("setupClose").click();
      await W(200);
    },
    // a tap on the main map at screen point (x, y), relative to the canvas
    tap(x, y) {
      const m = GG.debug.main, r = m.canvas.getBoundingClientRect();
      m.canvas.dispatchEvent(new MouseEvent("click", { clientX: r.left + x, clientY: r.top + y, bubbles: true }));
    },
    // where a [lon, lat] is on screen (on a wrapping flat map: the copy that's on screen)
    screenOf(ll) {
      const m = GG.debug.main, p = m.projection()(ll);
      if (p && m.mode === "flat" && m.wrap) { const Wk = m.BW * m.t.k; while (p[0] < 0) p[0] += Wk; while (p[0] > m.w) p[0] -= Wk; }
      return p;
    },
    // the card's name and the line under it, or "(no card)"
    card() { return $("learnCard").hidden ? "(no card)" : $("lcName").textContent; },
    // start a game or mode and wait for its map
    async start(mode, region, view, data) {
      GG.debug.startGame(mode, region, view, data);
      await T.until(() => GG.debug.geo && (data === "world" ? !GG.debug.geo.kind || GG.debug.geo.kind === "world" : GG.debug.geo.kind === data), 15000);
      await W(800);
    },
  };
  window.T = T;
})();
