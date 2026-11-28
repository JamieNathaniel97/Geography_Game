// (used by tests/run.py --full / --maps): reports every country map and its region, so the runner can open each one
T.run(async () => {
  await T.until(() => window.GG && GG.debug && GG.debug.datasets, 30000);
  T.metric("datasets", GG.debug.datasets());
});
