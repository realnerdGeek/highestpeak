// Test 5 (V3): name, video covers, custom covers, playlist pictures, backgrounds, lock-screen wiring.
const { chromium } = require('./pw.js'); require('./legacy');
const http = require('http'), fs = require('fs'), path = require('path');
const sharp = (() => { for (const t of [process.env.SHARP_PATH, '/opt/npm-tools/node_modules/sharp', 'sharp'].filter(Boolean)) { try { return require(t); } catch (e) { /* next */ } } throw new Error('sharp not found: npm i sharp'); })();
const DIR = __dirname, blobs = new Map(), types = new Map();
const sleep = ms => new Promise(r => setTimeout(r, ms));
let pass = 0, fail = 0; const ok = (label, cond, extra) => { cond ? pass++ : fail++; console.log((cond ? 'PASS ' : 'FAIL ') + label + (extra !== undefined ? '  -> ' + JSON.stringify(extra) : '')); };

const server = http.createServer((req, res) => { res.writeHead(200, { 'content-type': 'text/html' }); res.end(fs.readFileSync(path.join(DIR, 'index.html'))); });
const FAKE = () => {
  const ACCEPT = ['image/png', 'image/jpeg', 'image/gif', 'image/webp', 'video/mp4', 'video/webm', 'application/pdf'];
  const state = JSON.parse(localStorage.getItem('fakeDb') || '{}'), subs = {};
  const save = () => localStorage.setItem('fakeDb', JSON.stringify(state));
  const snap = c => ({ docs: Object.keys(state[c] || {}).sort().map(id => ({ id, exists: true, data: () => Object.freeze(JSON.parse(JSON.stringify(state[c][id]))) })) });
  const fire = c => (subs[c] || []).forEach(fn => setTimeout(() => fn(snap(c)), 5));
  const merge = (a, b) => { for (const k in b) { if (b[k] && typeof b[k] === 'object' && !Array.isArray(b[k]) && a[k] && typeof a[k] === 'object') merge(a[k], b[k]); else a[k] = b[k]; } };
  const doc = (c, id) => ({ id, path: c + '/' + id,
    async set(d) { await new Promise(r => setTimeout(r, 15)); (state[c] = state[c] || {})[id] = JSON.parse(JSON.stringify(d)); save(); fire(c); },
    async update(d) { await new Promise(r => setTimeout(r, 15)); if (!state[c] || !state[c][id]) throw { code: 'invalid_argument' }; merge(state[c][id], JSON.parse(JSON.stringify(d))); save(); fire(c); },
    async delete() { if (state[c]) delete state[c][id]; save(); fire(c); } });
  const db = { collection: c => ({ path: c, doc: id => doc(c, id || 'd' + Math.random().toString(36).slice(2, 12)), onSnapshot(fn) { (subs[c] = subs[c] || []).push(fn); setTimeout(() => fn(snap(c)), 30); return () => {}; } }) };
  const assets = {
    async upload(blob, o) {
      const type = (o && o.type) || blob.type;
      if (ACCEPT.indexOf(type) < 0) throw { code: 'unsupported_type' };
      const u8 = new Uint8Array(await blob.arrayBuffer()); let s = ''; for (let i = 0; i < u8.length; i += 32768) s += String.fromCharCode.apply(null, u8.subarray(i, i + 32768));
      const id = Array.from({ length: 32 }, () => 'abcdef0123456789'[Math.floor(Math.random() * 16)]).join('');
      await window.__putBlob(id, btoa(s), type);
      return { id, url: '/_blob/' + id, sizeBytes: blob.size, contentType: type };
    },
    async list() { return { assets: [], usage: { files: 1, bytes: 1000000, maxFiles: 500, maxBytes: 1073741824 } }; },
    async delete(id) { return { deleted: await window.__delBlob(id) }; }
  };
  window.claude = { use: name => new Promise(r => setTimeout(() => r(name === 'db' ? db : name === 'assets' ? assets : null), 120)) };
};

(async () => {
  await new Promise(r => server.listen(8768, r));
  const browser = await chromium.launch({ args: ['--autoplay-policy=no-user-gesture-required'] });
  const ctx = await browser.newContext({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 2, hasTouch: true });
  await ctx.exposeFunction('__putBlob', (id, b64, type) => { blobs.set(id, Buffer.from(b64, 'base64')); types.set(id, type); });
  await ctx.exposeFunction('__delBlob', id => blobs.delete(id));
  await ctx.addInitScript(FAKE);
  await ctx.route('**/_blob/*', route => {
    const id = route.request().url().split('/_blob/')[1], buf = blobs.get(id);
    if (!buf) return route.fulfill({ status: 404, body: '' });
    const range = route.request().headers()['range'], m = range && /bytes=(\d+)-(\d*)/.exec(range), type = types.get(id) || 'video/mp4';
    if (m) { const a = +m[1], b = m[2] ? +m[2] : buf.length - 1; return route.fulfill({ status: 206, headers: { 'content-type': type, 'accept-ranges': 'bytes', 'content-range': `bytes ${a}-${b}/${buf.length}` }, body: buf.subarray(a, b + 1) }); }
    route.fulfill({ status: 200, headers: { 'content-type': type, 'accept-ranges': 'bytes' }, body: buf });
  });
  const page = await ctx.newPage(); const errors = [];
  page.on('pageerror', e => errors.push('pageerror: ' + e.message));
  page.on('console', m => { if (m.type() === 'error' && !/fonts\.g|ERR_|Failed to load resource/.test(m.text())) errors.push('console: ' + m.text()); });
  const G = (fn, a) => page.evaluate(fn, a);
  const ready = () => page.waitForFunction(() => window.__gymTapes && window.__gymTapes.S.ready);
  const trackBy = title => G(t => window.__gymTapes.S.tracks.find(x => x.title === t), title);
  const settingsDoc = () => G(() => JSON.parse(localStorage.getItem('fakeDb') || '{}').settings);
  const imgInfo = async id => { const m = await sharp(blobs.get(id)).metadata(), st = await sharp(blobs.get(id)).stats(); return { type: types.get(id), w: m.width, h: m.height, format: m.format, mean: Math.round((st.channels[0].mean + st.channels[1].mean + st.channels[2].mean) / 3), kb: Math.round(blobs.get(id).length / 1024) }; };

  await page.goto('http://localhost:8768/'); await ready();
  ok('name is EarWorm in the page title and header (V13 Ear Worm, one word since V14)', (await page.title()) === 'EarWorm' && /EarWorm/.test(await page.textContent('h1')), await page.textContent('h1'));
  ok('logo mark is in the header (V13: the Ear Worm icon)', await page.isVisible('h1 .brand-ic svg'));

  // cover from the video
  await page.setInputFiles('#fileInput', DIR + '/media/blue-scene.mp4');
  await page.waitForFunction(() => window.__gymTapes.S.tracks.length === 1, null, { timeout: 60000 }); await sleep(300);
  let t = await trackBy('blue-scene');
  const ci = t.cover ? await imgInfo(t.cover) : null;
  ok('upload made a cover from a video frame', !!ci && ci.type === 'image/jpeg' && ci.format === 'jpeg' && ci.w === ci.h && ci.w >= 200 && ci.mean > 15, ci);
  if (t.cover) fs.writeFileSync(DIR + '/out/cover-from-video.jpg', blobs.get(t.cover));
  ok('end clip was still removed on that upload', t.dur < 40.3 && t.dur > 39.5, t.dur);
  ok('the row shows the picture', await G(() => { const im = document.querySelector('.row .cover.img img'); return !!im && im.complete && im.naturalWidth > 0; }));
  // a video that is black all the way through gets the generated cover
  await page.setInputFiles('#fileInput', DIR + '/media/all-black.mp4');
  await page.waitForFunction(() => window.__gymTapes.S.tracks.length === 2, null, { timeout: 60000 }); await sleep(300);
  t = await trackBy('all-black'); ok('an all-black video falls back to the generated cover', !!t && !t.cover);
  await page.screenshot({ path: DIR + '/shots/30-covers.png' });

  // custom cover on a track
  await page.click('.row:has-text("all-black") .more'); await page.click('[data-act="m-cover"]'); await page.setInputFiles('#imgInput', DIR + '/media/photo.png');
  await page.waitForFunction(() => { const x = window.__gymTapes.S.tracks.find(x => x.title === 'all-black'); return x && x.cover; }, null, { timeout: 15000 });
  t = await trackBy('all-black'); const cc = await imgInfo(t.cover);
  ok('"Change cover" saves a square picture', cc.w === 480 && cc.h === 480 && cc.type === 'image/jpeg', cc);
  // play it: player shows the picture, lock screen gets title + artwork + the right buttons
  await page.click('.row:has-text("all-black") .row-hit'); await sleep(900);
  const ms = await G(() => { const m = navigator.mediaSession.metadata; return { title: m && m.title, artist: m && m.artist, art: m && m.artwork && m.artwork[0] && m.artwork[0].src.slice(0, 22), playerImg: !!document.querySelector('#pCover .cover.img img'), playing: !document.getElementById('audio').paused }; });
  ok('player and lock screen use the cover', ms.title === 'all-black' && ms.artist === 'EarWorm' && /^data:image\/(jpeg|png)/.test(ms.art) && ms.playerImg && ms.playing, ms);
  await page.screenshot({ path: DIR + '/shots/31-player-cover.png' });
  await page.click('#playBtn');
  const old = t.cover;
  await page.click('.row:has-text("all-black") .more'); await page.click('[data-act="m-uncover"]');
  await page.waitForFunction(() => { const x = window.__gymTapes.S.tracks.find(x => x.title === 'all-black'); return x && !x.cover; }); await sleep(200);
  ok('"Remove cover" goes back to the generated one and deletes the picture', !blobs.has(old));

  // playlist with a picture
  await page.click('#tabLibrary'); await page.click('#libPlaylists'); await page.click('[data-act="pl-new"]');
  await page.fill('#plNameInput', 'Summit set'); await page.click('[data-act="pl-pick"]'); await page.setInputFiles('#imgInput', DIR + '/media/photo.png');
  await page.waitForSelector('#plPreview .cover.img img'); await page.screenshot({ path: DIR + '/shots/32-playlist-form.png' });
  await page.click('form[data-form="playlist"] button[type=submit]');
  await page.waitForFunction(() => window.__gymTapes.S.playlists.length === 1 && window.__gymTapes.S.playlists[0].cover, null, { timeout: 15000 });
  let p = await G(() => window.__gymTapes.S.playlists[0]);
  ok('playlist saved with name and picture', p.name === 'Summit set' && blobs.has(p.cover) && types.get(p.cover) === 'image/jpeg', { name: p.name });
  await page.click('[data-act="pl-add"]'); await page.click('#sheetPanel .opt:has-text("blue-scene")'); await sleep(150); await page.click('[data-act="sheet-close"]');
  await page.screenshot({ path: DIR + '/shots/33-playlist.png' });
  await page.click('[data-act="pl-back"]'); await sleep(100); await page.screenshot({ path: DIR + '/shots/34-playlists.png' });
  await page.click('[data-act="pl-open"]:has-text("Summit set")'); await page.click('[data-act="pl-menu"]'); await page.click('[data-act="pl-edit"]');
  await page.fill('#plNameInput', 'Summit'); await page.click('[data-act="pl-unpick"]'); await page.click('label:has(#plColor-green)'); await page.click('form[data-form="playlist"] button[type=submit]');
  await page.waitForFunction(() => window.__gymTapes.S.playlists[0].name === 'Summit' && !window.__gymTapes.S.playlists[0].cover); await sleep(200);
  ok('edit playlist: rename, recolor, remove picture', !blobs.has(p.cover) && (await G(() => window.__gymTapes.S.playlists[0].color)) === 'green');

  // backgrounds
  const look = () => G(() => { const r = document.documentElement, w = document.getElementById('wall'); return { skin: r.getAttribute('data-skin'), bg: r.style.getPropertyValue('--bg'), wall: !w.hidden, photo: w.classList.contains('photo'), ink: getComputedStyle(document.body).color, paint: w.style.background.slice(0, 30) }; });
  await page.click('#tabLibrary'); await page.click('#libUploads'); await page.click('#tabSettings'); await sleep(200); await page.screenshot({ path: DIR + '/shots/35-settings.png' });
  await page.click('.sw[data-id="midnight"]'); await sleep(300);
  let L = await look(); ok('Midnight background: dark palette, gradient painted, saved', L.skin === 'dark' && L.wall && /gradient/.test(L.paint) && ((await settingsDoc()).ui.bg.id === 'midnight'), L);
  ok('chosen circle is marked', (await page.getAttribute('.sw[data-id="midnight"]', 'aria-pressed')) === 'true');
  await page.click('#tabLibrary'); await page.click('#libUploads'); await page.click('.row:has-text("blue-scene") .row-hit'); await sleep(700);
  await page.screenshot({ path: DIR + '/shots/36-midnight.png' }); await page.click('#playBtn');
  await page.reload(); await ready(); await sleep(200);
  L = await look(); ok('background is still there after a reload', L.skin === 'dark' && L.wall, L);
  await page.click('#tabSettings'); await page.click('.sw[data-id="sand"]'); await sleep(300);
  L = await look(); ok('Sand background switches to the light palette', L.skin === 'light' && /rgb\(13, 13, 18\)/.test(L.ink), L);
  await page.click('#tabLibrary'); await page.click('#libUploads'); await page.screenshot({ path: DIR + '/shots/37-sand.png' });
  await page.click('#tabSettings');
  await G(() => { const i = document.getElementById('bgColor'); i.value = '#0b3d2e'; i.dispatchEvent(new Event('input', { bubbles: true })); i.dispatchEvent(new Event('change', { bubbles: true })); }); await sleep(300);
  L = await look(); ok('any custom color works and picks readable text (dark green -> light text)', L.skin === 'dark' && L.bg === '#0b3d2e' && (await settingsDoc()).ui.bg.value === '#0b3d2e', L);
  await G(() => { const i = document.getElementById('bgColor'); i.value = '#ffe9a8'; i.dispatchEvent(new Event('input', { bubbles: true })); i.dispatchEvent(new Event('change', { bubbles: true })); }); await sleep(300);
  L = await look(); ok('light custom color -> dark text', L.skin === 'light', L);
  await page.click('[data-act="bg-photo"]'); await page.setInputFiles('#imgInput', DIR + '/media/photo.png');
  await page.waitForFunction(() => document.getElementById('wall').classList.contains('photo'), null, { timeout: 15000 }); await sleep(400);
  L = await look(); const wallId = (await settingsDoc()).ui.bg.asset, wi = await imgInfo(wallId);
  ok('photo background: stored, painted, dark overlay', L.photo && L.skin === 'dark' && /url\(/.test(L.paint) && wi.type === 'image/jpeg' && wi.w === 1400, wi);
  await page.screenshot({ path: DIR + '/shots/38-settings-photo.png' }); await page.click('#tabLibrary'); await page.click('#libUploads');
  await page.click('.row:has-text("blue-scene") .row-hit'); await sleep(700); await page.screenshot({ path: DIR + '/shots/39-photo-bg.png' });
  await page.click('.row:has-text("blue-scene") .more'); await page.click('[data-act="m-edit"]');
  await page.waitForFunction(() => window.__gymTapes.ED.seq && !window.__gymTapes.ED.busy, null, { timeout: 15000 }); await page.focus('#hdA'); for (let i = 0; i < 40; i++) await page.keyboard.press('ArrowRight');
  await sleep(100); await page.screenshot({ path: DIR + '/shots/40-editor-photo-bg.png' }); await page.click('[data-act="ed-close"]');
  await page.click('#tabSettings'); await page.click('.sw[data-id="default"]'); await sleep(300);
  L = await look(); ok('Default puts everything back and deletes the stored photo', !L.skin && !L.wall && !blobs.has(wallId), L);
  await page.click('#tabLibrary'); await page.click('#libUploads');
  ok('no sideways scroll', await G(() => document.documentElement.scrollWidth <= window.innerWidth));
  ok('lock-screen handlers re-registered when playback starts (no page errors from it)', errors.length === 0, errors);
  await page.emulateMedia({ colorScheme: 'dark' }); await sleep(150); await page.screenshot({ path: DIR + '/shots/41-dark.png' });
  console.log(`\n${pass} passed, ${fail} failed`);
  await browser.close(); server.close();
})().catch(e => { console.error('TEST FAILED', e); process.exit(1); });
