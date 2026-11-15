// Keeps the app working offline. Bump CACHE when releasing a new version,
// or installed phones keep the old files.
const CACHE = "geography-game-v9";
const SHELL = [
  "./", "index.html", "manifest.webmanifest", "css/app.css",
  "js/names.js", "js/stats.js", "js/geo.js", "js/mapview.js", "js/app.js",
  "vendor/d3.min.js", "vendor/topojson-client.min.js", "vendor/d3-geo-projection.min.js",
  "data/world-50m.json", "data/world-110m.json", "data/countries.json", "data/relief.jpg",
  "icons/icon-192.png", "icons/icon-512.png", "icons/apple-touch-icon.png",
];

self.addEventListener("install", event => {
  event.waitUntil(caches.open(CACHE).then(async cache => {
    await cache.addAll(SHELL);
    // the flags (Learning mode), one per country in the country list
    try {
      const cs = await (await fetch("data/countries.json")).json();
      await cache.addAll(cs.map(c => `data/flags/${c.iso}.svg`));
    } catch (e) { /* they'll be cached as they're viewed */ }
    // the sharper terrain tiles (about 9 MB), listed in their index, so terrain works offline when zoomed in
    try {
      const ix = await (await fetch("data/relief/index.json")).json();
      await cache.add("data/relief/index.json");
      const urls = ix.levels.flatMap(l => l.tiles.map(n => `data/relief/${l.w}/${n}.jpg`));
      for (let i = 0; i < urls.length; i += 40) await cache.addAll(urls.slice(i, i + 40));
    } catch (e) { /* tiles are optional; they'll be cached as they're viewed */ }
  }));
  self.skipWaiting();
});

self.addEventListener("activate", event => {
  event.waitUntil(caches.keys().then(keys =>
    Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k)))));
  self.clients.claim();
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
