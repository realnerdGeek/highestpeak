/* EarWorm offline support. The app itself is kept on the phone, so it opens with no signal.
   The page is checked for a newer version each time it opens with a connection; no more than a few seconds are spent waiting for it. */
const CACHE = 'highestpeak-20261020034143-86ba3cff';
const SHELL = ['./', './index.html', './manifest.webmanifest', './apple-touch-icon.png', './icon-192.png', './icon-512.png', './icon-maskable-512.png'];
self.addEventListener('install', e => { e.waitUntil(caches.open(CACHE).then(c => c.addAll(SHELL)).then(() => self.skipWaiting())); });
self.addEventListener('activate', e => { e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k.indexOf('highestpeak-') === 0 && k !== CACHE).map(k => caches.delete(k)))).then(() => self.clients.claim())); });
const fresh = req => new Promise((resolve, reject) => {
  const timer = setTimeout(() => reject(new Error('slow')), 3500);
  fetch(req, { cache: 'no-store' }).then(res => { clearTimeout(timer); if (res && res.ok) { const copy = res.clone(); caches.open(CACHE).then(c => c.put('./index.html', copy)); resolve(res); } else reject(new Error('bad')); }, err => { clearTimeout(timer); reject(err); });
});
/* Android share sheet (V18): what was shared is kept for the app in its own cache, then the app opens with ?share=1 */
const SHARE = 'earworm-share';
async function shared(req) {
  const scope = self.registration.scope;
  try {
    const fd = await req.formData(), files = fd.getAll('media').filter(f => f && typeof f !== 'string' && f.size > 0);     // an empty file field comes through as a nameless empty file
    await caches.delete(SHARE); const c = await caches.open(SHARE);
    for (let i = 0; i < files.length; i++) await c.put(new URL('share/' + i, scope).href, new Response(files[i], { headers: { 'content-type': files[i].type || 'application/octet-stream', 'x-name': encodeURIComponent(files[i].name || 'Shared video') } }));
    await c.put(new URL('share/meta', scope).href, new Response(JSON.stringify({ n: files.length, title: String(fd.get('title') || ''), text: String(fd.get('text') || ''), url: String(fd.get('url') || ''), at: Date.now() }), { headers: { 'content-type': 'application/json' } }));
  } catch (err) { /* nothing readable came through: the app just opens */ }
  return Response.redirect(new URL('./?share=1', scope).href, 303);
}
self.addEventListener('fetch', e => {
  const r = e.request;
  if (r.method === 'POST' && new URL(r.url).pathname.endsWith('/share-target')) { e.respondWith(shared(r)); return; }
  if (r.method !== 'GET') return;
  const u = new URL(r.url); if (u.origin !== self.location.origin) return;
  if (r.mode === 'navigate') { e.respondWith(fresh(r).catch(() => caches.match('./index.html').then(m => m || caches.match('./')))); return; }
  e.respondWith(caches.match(r, { ignoreSearch: true }).then(m => m || fetch(r)));
});
