// Keeps the app working offline. Bump CACHE when releasing a new version,
// or installed phones keep the old files.
const CACHE = "gaia-quest-v29";
const SHELL = [
  "./", "index.html", "manifest.webmanifest", "css/app.css",
  "js/splash.js", "js/names.js", "js/stats.js", "js/geo.js", "js/mapview.js", "js/app.js",
  "vendor/d3.min.js", "vendor/topojson-client.min.js", "vendor/d3-geo-projection.min.js",
  "data/world-50m.json", "data/world-110m.json", "data/countries.json", "data/relief.jpg",
  "data/us-states.json", "data/states.json", "data/lakes.json", "data/tribal-us.json",
  "data/ca-provinces.json", "data/provinces.json", "data/tribal-ca.json",
  "icons/icon-192.png", "icons/icon-512.png", "icons/icon-maskable-192.png", "icons/icon-maskable-512.png", "icons/apple-touch-icon.png",
];

// straight from the network: the browser's own copy of a file can be up to 10 minutes old after a release
const fresh = url => new Request(url, { cache: "reload" });

self.addEventListener("install", event => {
  // only what the app needs, so the update is ready quickly (the terrain tiles follow after it's switched on)
  event.waitUntil(caches.open(CACHE).then(async cache => {
    await cache.addAll(SHELL.map(fresh));
    // the flags (Learning mode), one per country in the country list
    try {
      const cs = await (await fetch(fresh("data/countries.json"))).json();
      await cache.addAll(cs.map(c => fresh(`data/flags/${c.iso}.webp`)));
      const st = await (await fetch(fresh("data/states.json"))).json();
      await cache.addAll(st.map(s => fresh(`data/flags/us/${s.iso}.webp`)));
      const pv = await (await fetch(fresh("data/provinces.json"))).json();
      await cache.addAll(pv.map(s => fresh(`data/flags/ca/${s.iso}.webp`)));
    } catch (e) { /* they'll be cached as they're viewed */ }
  }));
  self.skipWaiting();
});

self.addEventListener("activate", event => {
  event.waitUntil((async () => {
    const cache = await caches.open(CACHE);
    // the sharper terrain tiles (about 9 MB) don't change between versions: keep the ones already on the phone
    for (const k of await caches.keys()) {
      if (k === CACHE) continue;
      const old = await caches.open(k);
      for (const req of await old.keys()) {
        if (new URL(req.url).pathname.includes("/data/relief/")) { const res = await old.match(req); if (res) await cache.put(req, res); }
      }
      await caches.delete(k);
    }
    await self.clients.claim();
  })());
  // then fetch any tiles still missing, in the background (terrain works offline when zoomed in)
  (async () => {
    try {
      const cache = await caches.open(CACHE);
      const ix = await (await fetch("data/relief/index.json")).json();
      await cache.add("data/relief/index.json");
      const urls = ix.levels.flatMap(l => l.tiles.map(n => `data/relief/${l.w}/${n}.jpg`));
      for (const u of urls) if (!(await cache.match(u))) await cache.add(u);
    } catch (e) { /* tiles are optional; they'll be cached as they're viewed */ }
  })();
});

// Serve from the phone's cache straight away (so it opens instantly with no signal),
// and refresh the cache in the background when online, so updates arrive next time.
self.addEventListener("fetch", event => {
  const req = event.request;
  if (req.method !== "GET") return;
  const url = new URL(req.url);
  const isFont = url.hostname === "fonts.googleapis.com" || url.hostname === "fonts.gstatic.com";
  if (url.origin !== location.origin && !isFont) return;

  event.respondWith(caches.open(CACHE).then(async cache => {
    const cached = await cache.match(req, { ignoreSearch: url.origin === location.origin });
    const network = fetch(req).then(res => {
      if (res && (res.ok || res.type === "opaque")) cache.put(req, res.clone());
      return res;
    }).catch(() => null);
    if (cached) { event.waitUntil(network); return cached; }
    const res = await network;
    if (res) return res;
    if (req.mode === "navigate") return cache.match("index.html");
    return new Response("", { status: 504, statusText: "Offline" });
  }));
});
