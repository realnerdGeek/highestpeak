# Builds the home screen version of EarWorm (formerly HighestPeak) from the same page the Claude version uses.
import os, json, time, hashlib
from PIL import Image
here = os.path.dirname(os.path.abspath(__file__)); app = os.path.join(os.path.dirname(here), 'app'); out = os.path.join(here, 'site')
os.makedirs(out, exist_ok=True)
page = open(os.path.join(app, 'gym-tapes.html'), encoding='utf8').read()
title = '<title>EarWorm</title>'
assert page.startswith(title)
body = page[len(title):]
build = time.strftime('%Y%m%d%H%M%S') + '-' + hashlib.sha1(page.encode()).hexdigest()[:8]

head = '''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>EarWorm</title>
<meta name="description" content="Turn videos into sounds you can loop, shuffle and trim.">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="mobile-web-app-capable" content="yes">
<!-- keep the status bar solid: on iOS 26 and later a see-through one makes the home screen app a status bar short at the bottom (WebKit bug 301108) -->
<meta name="apple-mobile-web-app-status-bar-style" content="default">
<meta name="apple-mobile-web-app-title" content="EarWorm">
<meta name="theme-color" content="#F5F5F7" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#0A0A0D" media="(prefers-color-scheme: dark)">
<meta name="color-scheme" content="light dark">
<meta name="hp-build" content="BUILD">
<link rel="manifest" href="manifest.webmanifest">
<link rel="apple-touch-icon" href="apple-touch-icon.png">
<link rel="icon" type="image/png" href="icon-192.png">
<style>:root{padding:env(safe-area-inset-top,0px) 0 env(safe-area-inset-bottom,0px)}body{margin:0}[hidden]{display:none!important}</style>
<script>
window.HP_STANDALONE = true;
if ('serviceWorker' in navigator) addEventListener('load', () => { navigator.serviceWorker.register('./sw.js', { updateViaCache: 'none' }).catch(() => {}); });
</script>
</head>
<body>
'''.replace('BUILD', build)
open(os.path.join(out, 'index.html'), 'w', encoding='utf8').write(head + body.lstrip('\n') + '\n</body>\n</html>\n')

manifest = {
  "name": "EarWorm", "short_name": "EarWorm", "description": "Turn videos into sounds you can loop, shuffle and trim.",
  "id": "./", "start_url": "./", "scope": "./", "display": "standalone", "orientation": "portrait",
  "background_color": "#17121F", "theme_color": "#0A0A0D",
  "icons": [
    {"src": "icon-192.png", "sizes": "192x192", "type": "image/png", "purpose": "any"},
    {"src": "icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any"},
    {"src": "icon-maskable-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"}
  ],
  "shortcuts": [
    {"name": "Shuffle everything", "short_name": "Shuffle", "url": "./?go=shuffle", "icons": [{"src": "icon-192.png", "sizes": "192x192", "type": "image/png"}]},
    {"name": "Upload", "url": "./?go=upload", "icons": [{"src": "icon-192.png", "sizes": "192x192", "type": "image/png"}]},
    {"name": "Library", "url": "./?go=library", "icons": [{"src": "icon-192.png", "sizes": "192x192", "type": "image/png"}]},
    {"name": "Search", "url": "./?go=search", "icons": [{"src": "icon-192.png", "sizes": "192x192", "type": "image/png"}]}
  ],
  # V18: the installed computer app shows up under Open with for these files, and an open window takes them
  "file_handlers": [{"action": "./", "accept": {
    "video/mp4": [".mp4", ".m4v"], "video/quicktime": [".mov"], "video/webm": [".webm"],
    "audio/mpeg": [".mp3"], "audio/mp4": [".m4a"], "audio/wav": [".wav"], "audio/aac": [".aac"], "audio/flac": [".flac"], "audio/ogg": [".ogg", ".opus"]}}],
  "launch_handler": {"client_mode": ["focus-existing", "auto"]},
  # V18: Android's share sheet lists EarWorm (once installed) for videos and sound; a shared link is caught too
  "share_target": {"action": "./share-target", "method": "POST", "enctype": "multipart/form-data",
    "params": {"title": "title", "text": "text", "url": "url", "files": [{"name": "media", "accept": ["video/*", "audio/*", ".mp4", ".mov", ".m4a", ".mp3", ".wav"]}]}}
}
open(os.path.join(out, 'manifest.webmanifest'), 'w', encoding='utf8').write(json.dumps(manifest, indent=2))

# icons: the EarWorm icon, drawn edge to edge on its dark square; the phone rounds the corners itself
src = Image.open(os.path.join(app, 'logo', 'earworm-icon-1024.png')).convert('RGB')
def square(size): return src.resize((size, size), Image.LANCZOS)
square(180).save(os.path.join(out, 'apple-touch-icon.png'))
square(192).save(os.path.join(out, 'icon-192.png'))
square(512).save(os.path.join(out, 'icon-512.png'))
square(512).save(os.path.join(out, 'icon-maskable-512.png'))

sw = '''/* EarWorm offline support. The app itself is kept on the phone, so it opens with no signal.
   The page is checked for a newer version each time it opens with a connection; no more than a few seconds are spent waiting for it. */
const CACHE = 'highestpeak-BUILD';
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
'''.replace('BUILD', build)
open(os.path.join(out, 'sw.js'), 'w', encoding='utf8').write(sw)
open(os.path.join(out, '.nojekyll'), 'w').write('')
print('built', build, sorted(os.listdir(out)))
