// Live earthquakes for Earth mode (jobs/geoscience.md, stage 3). Written ahead (2026-11-28) and NOT loaded by
// index.html yet: the Earth tab will add it and draw the dots. It reads the USGS real-time feed (public domain,
// https://earthquake.usgs.gov/earthquakes/feed/v1.0/geojson.php), which needs the network: the last good answer
// is kept in localStorage so the layer still shows something offline (marked as old). The service worker must not
// cache the feed URL (it changes every minute): leave it to this module.
(function () {
  const GG = (window.GG = window.GG || {});
  const BASE = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/";
  // the feed's ranges and lower magnitudes (USGS names: e.g. 4.5_month)
  const RANGES = ["hour", "day", "week", "month"], MAGS = ["significant", "4.5", "2.5", "1.0", "all"];
  const KEY = r => "gq.quakes." + r; // localStorage key per feed
  const FRESH = 5 * 60 * 1000;      // a feed fetched less than 5 minutes ago isn't fetched again

  // one quake: what the layer and the card need
  function quake(f) {
    const p = f.properties || {}, c = (f.geometry && f.geometry.coordinates) || [];
    return {
      id: f.id, mag: p.mag, place: p.place || "", time: p.time, depth: c[2], lon: c[0], lat: c[1],
      url: p.url, tsunami: !!p.tsunami, alert: p.alert || null, felt: p.felt || 0, title: p.title || "",
    };
  }
  function parse(json) {
    const qs = (json.features || []).map(quake).filter(q => isFinite(q.lon) && isFinite(q.lat) && isFinite(q.mag));
    qs.sort((a, b) => b.mag - a.mag || b.time - a.time); // biggest first (drawn last, on top, by the layer)
    return { generated: (json.metadata && json.metadata.generated) || Date.now(), count: qs.length, quakes: qs };
  }
  function readCache(feed) {
    try { const s = localStorage.getItem(KEY(feed)); return s ? JSON.parse(s) : null; } catch (e) { return null; }
  }
  function writeCache(feed, data) {
    try { localStorage.setItem(KEY(feed), JSON.stringify({ fetched: Date.now(), data })); } catch (e) { /* full or blocked */ }
  }

  // load({ range: "month", mag: "4.5" }) -> { quakes, generated, count, stale, offline }
  //   stale: the cached copy (the network failed); offline: nothing at all could be had
  async function load(opts) {
    const range = RANGES.includes(opts && opts.range) ? opts.range : "month";
    const mag = MAGS.includes(opts && opts.mag) ? opts.mag : "4.5";
    const feed = `${mag}_${range}`, cached = readCache(feed);
    if (cached && Date.now() - cached.fetched < FRESH && !(opts && opts.force)) return { ...cached.data, stale: false, offline: false };
    try {
      const ctl = typeof AbortController === "function" ? new AbortController() : null;
      const timer = ctl && setTimeout(() => ctl.abort(), 15000);
      const res = await fetch(BASE + feed + ".geojson", { cache: "no-store", signal: ctl && ctl.signal });
      if (timer) clearTimeout(timer);
      if (!res.ok) throw new Error("HTTP " + res.status);
      const data = parse(await res.json());
      writeCache(feed, data);
      return { ...data, stale: false, offline: false };
    } catch (e) {
      if (cached) return { ...cached.data, stale: true, offline: false };
      return { generated: null, count: 0, quakes: [], stale: false, offline: true };
    }
  }

  // the dot's radius in pixels for a magnitude (each step ~1.6x wider: energy grows 32x per step, area can't)
  const radius = (mag, base = 2.5) => base * Math.pow(1.6, Math.max(0, mag - 4.5));
  // its colour by depth (shallow quakes are the damaging ones): the layer maps these to theme tokens
  const depthBand = d => (d < 70 ? "shallow" : d < 300 ? "intermediate" : "deep");
  // "3 hours ago", "2 days ago"
  function ago(t, now = Date.now()) {
    const m = Math.round((now - t) / 60000);
    if (m < 60) return m <= 1 ? "just now" : m + " minutes ago";
    const h = Math.round(m / 60); if (h < 48) return h + (h === 1 ? " hour ago" : " hours ago");
    return Math.round(h / 24) + " days ago";
  }

  GG.QuakesLive = { load, parse, radius, depthBand, ago, RANGES, MAGS };
})();
