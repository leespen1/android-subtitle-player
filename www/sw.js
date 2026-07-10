/* Service worker for Subtitle Player.
 *
 * The app is a handful of static files with no backend, so we precache the whole
 * shell on install and serve it cache-first. That makes the installed PWA launch
 * instantly and work with no network at all.
 *
 * Bump CACHE whenever index.html (or any precached asset) changes: the new
 * worker precaches fresh copies on install and deletes the old cache on
 * activate, which is what pushes an update out to already-installed clients.
 */
const CACHE = "subtitle-player-v14";

const ASSETS = [
  ".",
  "index.html",
  "manifest.json",
  "icon-192.png",
  "icon-512.png",
  "icon-maskable-512.png",
  "apple-touch-icon.png",
];

self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(CACHE).then((cache) => cache.addAll(ASSETS)).then(() => self.skipWaiting())
  );
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys()
      .then((keys) => Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener("fetch", (event) => {
  const req = event.request;
  // Only same-origin GETs are part of the app shell; let everything else
  // (e.g. cross-origin requests) fall straight through to the network.
  if (req.method !== "GET" || new URL(req.url).origin !== self.location.origin) return;

  event.respondWith(
    caches.match(req).then((cached) => {
      const network = fetch(req)
        .then((res) => {
          // Refresh the cache in the background so the next launch is current.
          if (res && res.ok) {
            const copy = res.clone();
            caches.open(CACHE).then((cache) => cache.put(req, copy));
          }
          return res;
        })
        .catch(() => cached); // offline: fall back to whatever we cached
      return cached || network;
    })
  );
});
