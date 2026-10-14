/* HighestPeak offline support. The app itself is kept on the phone, so it opens with no signal.
   The page is checked for a newer version each time it opens with a connection; no more than a few seconds are spent waiting for it. */
const CACHE = 'highestpeak-20261014192928-1a33b9ba';
const SHELL = ['./', './index.html', './manifest.webmanifest', './apple-touch-icon.png', './icon-192.png', './icon-512.png', './icon-maskable-512.png'];
self.addEventListener('install', e => { e.waitUntil(caches.open(CACHE).then(c => c.addAll(SHELL)).then(() => self.skipWaiting())); });
self.addEventListener('activate', e => { e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k.indexOf('highestpeak-') === 0 && k !== CACHE).map(k => caches.delete(k)))).then(() => self.clients.claim())); });
const fresh = req => new Promise((resolve, reject) => {
  const timer = setTimeout(() => reject(new Error('slow')), 3500);
  fetch(req, { cache: 'no-store' }).then(res => { clearTimeout(timer); if (res && res.ok) { const copy = res.clone(); caches.open(CACHE).then(c => c.put('./index.html', copy)); resolve(res); } else reject(new Error('bad')); }, err => { clearTimeout(timer); reject(err); });
});
self.addEventListener('fetch', e => {
  const r = e.request; if (r.method !== 'GET') return;
  const u = new URL(r.url); if (u.origin !== self.location.origin) return;
  if (r.mode === 'navigate') { e.respondWith(fresh(r).catch(() => caches.match('./index.html').then(m => m || caches.match('./')))); return; }
  e.respondWith(caches.match(r, { ignoreSearch: true }).then(m => m || fetch(r)));
});
