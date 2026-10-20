// Test 2: saved-library mode with a stand-in for the viewer's db + assets. Playback, loop, shuffle, playlists, trim/cut, save, reload.
const { chromium } = require('./pw.js'); require('./legacy');
const http = require('http'), fs = require('fs'), path = require('path');
const { execSync } = require('child_process');
const DIR = __dirname, blobs = new Map();
const sleep = ms => new Promise(r => setTimeout(r, ms));

const server = http.createServer((req, res) => {
  const f = path.join(DIR, req.url === '/' ? 'index.html' : decodeURIComponent(req.url.split('?')[0]));
  if (!fs.existsSync(f)) { res.writeHead(404); return res.end(); }
  res.writeHead(200, { 'content-type': 'text/html' }); res.end(fs.readFileSync(f));
});

const FAKE = () => {
  const ACCEPT = ['image/png', 'image/jpeg', 'image/gif', 'image/webp', 'video/mp4', 'video/webm', 'application/pdf'];
  const load = () => JSON.parse(localStorage.getItem('fakeDb') || '{}');
  const state = load(), subs = {};
  const save = () => localStorage.setItem('fakeDb', JSON.stringify(state));
  const snap = c => ({ docs: Object.keys(state[c] || {}).sort().map(id => ({ id, exists: true, data: () => Object.freeze(JSON.parse(JSON.stringify(state[c][id]))) })) });
  const fire = c => (subs[c] || []).forEach(fn => setTimeout(() => fn(snap(c)), 5));
  const merge = (a, b) => { for (const k in b) { if (b[k] && typeof b[k] === 'object' && !Array.isArray(b[k]) && a[k] && typeof a[k] === 'object') merge(a[k], b[k]); else a[k] = b[k]; } };
  const doc = (c, id) => ({ id, path: c + '/' + id,
    async set(d) { await new Promise(r => setTimeout(r, 20)); (state[c] = state[c] || {})[id] = JSON.parse(JSON.stringify(d)); save(); fire(c); },
    async update(d) { await new Promise(r => setTimeout(r, 20)); if (!state[c] || !state[c][id]) throw { code: 'invalid_argument' }; merge(state[c][id], JSON.parse(JSON.stringify(d))); save(); fire(c); },
    async delete() { if (state[c]) delete state[c][id]; save(); fire(c); } });
  const db = { collection: c => ({ path: c, doc: id => doc(c, id || 'd' + Math.random().toString(36).slice(2, 12)), onSnapshot(fn) { (subs[c] = subs[c] || []).push(fn); setTimeout(() => fn(snap(c)), 30); return () => {}; } }) };
  const assets = {
    async upload(blob, o) {
      const type = (o && o.type) || blob.type;
      if (ACCEPT.indexOf(type) < 0) throw { code: 'unsupported_type' };
      if (blob.size > 20 * 1024 * 1024) throw { code: 'too_large' };
      const u8 = new Uint8Array(await blob.arrayBuffer()); let s = ''; for (let i = 0; i < u8.length; i += 32768) s += String.fromCharCode.apply(null, u8.subarray(i, i + 32768));
      const id = Array.from({ length: 32 }, () => 'abcdef0123456789'[Math.floor(Math.random() * 16)]).join('');
      await window.__putBlob(id, btoa(s)); window.__uploads = (window.__uploads || 0) + 1;
      return { id, url: '/_blob/' + id, sizeBytes: blob.size, contentType: type };
    },
    async list() { const u = await window.__usage(); return { assets: [], usage: { files: u.files, bytes: u.bytes, maxFiles: 500, maxBytes: 1073741824 } }; },
    async delete(id) { return { deleted: await window.__delBlob(id) }; }
  };
  window.claude = { use: name => new Promise(r => setTimeout(() => r(name === 'db' ? db : name === 'assets' ? assets : null), 150)) };
};

(async () => {
  await new Promise(r => server.listen(8766, r));
  const browser = await chromium.launch({ args: ['--autoplay-policy=no-user-gesture-required'] });
  const ctx = await browser.newContext({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 2, hasTouch: true });
  await ctx.exposeFunction('__putBlob', (id, b64) => { blobs.set(id, Buffer.from(b64, 'base64')); });
  await ctx.exposeFunction('__delBlob', id => blobs.delete(id));
  await ctx.exposeFunction('__usage', () => ({ files: blobs.size, bytes: [...blobs.values()].reduce((a, b) => a + b.length, 0) }));
  await ctx.addInitScript(FAKE);
  await ctx.route('**/_blob/*', route => {
    const id = route.request().url().split('/_blob/')[1], buf = blobs.get(id);
    if (!buf) return route.fulfill({ status: 404, body: '' });
    const range = route.request().headers()['range'], m = range && /bytes=(\d+)-(\d*)/.exec(range);
    if (m) { const a = +m[1], b = m[2] ? +m[2] : buf.length - 1; return route.fulfill({ status: 206, headers: { 'content-type': 'video/mp4', 'accept-ranges': 'bytes', 'content-range': `bytes ${a}-${b}/${buf.length}` }, body: buf.subarray(a, b + 1) }); }
    route.fulfill({ status: 200, headers: { 'content-type': 'video/mp4', 'accept-ranges': 'bytes' }, body: buf });
  });
  const page = await ctx.newPage();
  const errors = [];
  page.on('pageerror', e => errors.push('pageerror: ' + e.message));
  page.on('console', m => { if (m.type() === 'error' && !/fonts\.g|ERR_|Failed to load resource/.test(m.text())) errors.push('console: ' + m.text()); });
  const G = fn => page.evaluate(fn);
  const ready = () => page.waitForFunction(() => window.__gymTapes && window.__gymTapes.S.ready);
  const ok = (label, cond, extra) => console.log((cond ? 'PASS ' : 'FAIL ') + label + (extra !== undefined ? '  -> ' + JSON.stringify(extra) : ''));

  await page.goto('http://localhost:8766/');
  await page.screenshot({ path: DIR + '/shots/10-loading.png' });
  await ready();
  ok('saved-library mode, no notice', !(await page.isVisible('#notice')));

  // import three tracks (one multi-select)
  await page.setInputFiles('#fileInput', [DIR + '/media/opus-clip.mp4', DIR + '/media/Leg-day-beeps.mp4', DIR + '/media/33966784-v29025g50000datbdifog65qur5e1a6g.mp4']);
  await page.waitForFunction(() => window.__gymTapes.S.tracks.length === 3, null, { timeout: 40000 });
  await sleep(300);
  ok('3 tracks imported, uploads went to asset store (plus the kept videos)', blobs.size === 3 + (await G(() => window.__gymTapes.S.tracks.filter(t => t.video).length)), await G(() => window.__gymTapes.S.tracks.map(t => t.title)));
  await page.click('#tabSettings'); await sleep(400); ok('storage line in settings', /storage used/.test(await page.textContent('#setStorage')), await page.textContent('#setStorage')); await page.screenshot({ path: DIR + '/shots/10b-settings.png', fullPage: true }); await page.click('#tabLibrary'); await page.click('#libUploads');

  // rename via menu
  await page.click('.row:has-text("Upload 3") .more');
  await page.click('[data-act="m-rename"]'); await page.fill('#renameInput', 'Workout loop'); await page.click('form[data-form="rename"] button[type=submit]');
  await page.waitForFunction(() => window.__gymTapes.S.tracks.some(t => t.title === 'Workout loop'));
  ok('rename', true);

  // play a track: src is the asset url, time advances
  await page.click('.row:has-text("opus-clip") .row-hit');
  await sleep(1500);
  let st = await G(() => { const a = document.getElementById('audio'); return { src: a.getAttribute('src'), t: a.currentTime, paused: a.paused, dur: a.duration, title: document.getElementById('pTitle').textContent, meta: document.getElementById('pMeta').textContent }; });
  ok('plays from /_blob/ url and time advances', /^\/_blob\/[0-9a-f]{32}$/.test(st.src) && st.t > 0.5 && !st.paused, st);
  await page.screenshot({ path: DIR + '/shots/11-playing.png' });

  // loop button cycles; loop-one sets native loop
  await page.click('#loopBtn'); const l1 = await page.textContent('#loopLab');
  await page.click('#loopBtn'); const l2 = await page.textContent('#loopLab');
  const nativeLoop = await G(() => document.getElementById('audio').loop);
  ok('loop cycles off -> all -> track, native loop on', l1 === 'Loop all' && l2 === 'Loop one' && nativeLoop, [l1, l2]);
  // seek near the end and confirm it wraps around on its own
  await G(() => { const a = document.getElementById('audio'); a.currentTime = a.duration - 0.6; });
  await sleep(1800);
  st = await G(() => { const a = document.getElementById('audio'); return { t: a.currentTime, paused: a.paused, title: document.getElementById('pTitle').textContent }; });
  ok('loop track: wrapped to the start and kept playing same track', st.t < 3 && !st.paused && st.title === 'opus-clip', st);
  // loop off + end of track -> advances to next track automatically
  await page.click('#loopBtn');
  await G(() => { const a = document.getElementById('audio'); a.currentTime = a.duration - 0.5; });
  await sleep(1500);
  st = await G(() => ({ paused: document.getElementById('audio').paused, pos: window.__gymTapes.P.pos }));
  ok('loop off: stops at the end of the last track', st.paused && st.pos === 2, st);
  await page.click('.row:has-text("Leg-day-beeps") .row-hit'); await sleep(700);
  const firstTitle = await page.textContent('#pTitle');
  await G(() => { const a = document.getElementById('audio'); a.currentTime = a.duration - 0.5; });
  await sleep(1800);
  st = await G(() => ({ title: document.getElementById('pTitle').textContent, paused: document.getElementById('audio').paused, pos: window.__gymTapes.P.pos, t: document.getElementById('audio').currentTime }));
  ok('auto-advance to next track at end', st.title === 'opus-clip' && firstTitle === 'Leg-day-beeps' && st.pos === 2 && !st.paused && st.t > 0, st);
  // next / prev / pause
  await page.click('[data-act="prev"]'); await sleep(300); await page.click('#playBtn'); await sleep(200);
  ok('pause works', await G(() => document.getElementById('audio').paused));
  // seek by tapping the waveform
  { const wb = await page.locator('#wave').boundingBox(); await page.click('#wave', { position: { x: wb.width / 2, y: 15 } }); } await sleep(200);
  st = await G(() => { const a = document.getElementById('audio'); return { frac: a.currentTime / a.duration }; });
  ok('tap waveform seeks to ~50%', Math.abs(st.frac - 0.5) < 0.05, st);

  // shuffle: order is a permutation and covers every track
  await page.click('#shufBtn');
  st = await G(() => ({ sh: window.__gymTapes.S.shuffle, order: window.__gymTapes.P.order.slice(), n: window.__gymTapes.P.queue.length, q: window.__gymTapes.P.queue.slice(), lab: document.getElementById('shufLab').textContent }));
  ok('shuffle on, order is a full permutation', st.sh && st.order.length === st.n && new Set(st.order).size === st.n && st.order.slice().sort().join() === st.q.slice().sort().join() && st.lab === 'Shuffle on', st);
  await page.click('#shufBtn');

  // playlists
  await page.click('#tabLibrary'); await page.click('#libPlaylists'); await page.click('[data-act="pl-new"]');
  await page.screenshot({ path: DIR + '/shots/12-new-playlist.png' });
  await page.fill('#plNameInput', 'Leg day'); await page.click('label:has(#plColor-red)'); await page.click('form[data-form="playlist"] button[type=submit]');
  await page.waitForSelector('.pl-head'); await page.click('[data-act="pl-add"]');
  await page.click('#sheetPanel .opt:has-text("Workout loop")'); await sleep(150);
  await page.click('#sheetPanel .opt:has-text("Leg-day-beeps")'); await sleep(150);
  await page.screenshot({ path: DIR + '/shots/13-add-tracks.png' });
  await page.click('[data-act="sheet-close"]');
  st = await G(() => { const p = window.__gymTapes.S.playlists[0]; return { name: p.name, color: p.color, n: p.tracks.length }; });
  ok('playlist created with 2 tracks', st.name === 'Leg day' && st.color === 'red' && st.n === 2, st);
  // move down, then play playlist
  await page.click('.row:has-text("Workout loop") .more'); await page.click('[data-act="m-down"]'); await sleep(200);
  const order = await G(() => { const g = window.__gymTapes, p = g.S.playlists[0]; return p.tracks.map(id => g.S.tracks.find(t => t.id === id).title); });
  ok('reorder inside playlist', order.join() === 'Leg-day-beeps,Workout loop', order);
  await page.click('[data-act="pl-play"]'); await sleep(900);
  st = await G(() => ({ title: document.getElementById('pTitle').textContent, meta: document.getElementById('pMeta').textContent, paused: document.getElementById('audio').paused }));
  ok('playlist plays its first track', st.title === 'Leg-day-beeps' && /Leg day, 1 of 2/.test(st.meta) && !st.paused, st);
  await page.screenshot({ path: DIR + '/shots/14-playlist.png' });
  // add from a track's menu, into a new playlist
  await page.click('#tabLibrary'); await page.click('#libUploads'); await page.click('.row:has-text("opus-clip") .more'); await page.click('[data-act="m-addpl"]'); await page.click('[data-act="pl-new-with"]');
  await page.fill('#plNameInput', 'Cardio'); await page.click('form[data-form="playlist"] button[type=submit]');
  await page.waitForFunction(() => window.__gymTapes.S.playlists.length === 2);
  ok('new playlist from track menu holds the track', await G(() => window.__gymTapes.S.playlists.find(p => p.name === 'Cardio').tracks.length === 1));
  await page.click('#tabLibrary'); await page.click('#libPlaylists'); await sleep(100); await page.screenshot({ path: DIR + '/shots/15-playlists.png' });

  // editor: Leg-day-beeps is 12 s of low tone then 12 s of high tone (24 s)
  await page.click('#tabLibrary'); await page.click('#libUploads'); await page.click('.row:has-text("Leg-day-beeps") .more'); await page.click('[data-act="m-edit"]');
  await page.waitForFunction(() => window.__gymTapes.ED.seq && !window.__gymTapes.ED.busy, null, { timeout: 15000 });
  ok('opening the editor pauses the player', await G(() => document.getElementById('audio').paused));
  st = await G(() => ({ dur: window.__gymTapes.ED.dur, keepDisabled: document.getElementById('edKeep').disabled, saveDisabled: document.getElementById('edSave').disabled }));
  ok('editor loaded, keep/cut/save disabled until a part is marked', Math.abs(st.dur - 24) < 0.1 && st.keepDisabled && st.saveDisabled, st);
  // drag the start handle to ~25% and the end handle to ~50% with real pointer input
  const box = await page.locator('#edTrack').boundingBox();
  const drag = async (sel, toFrac, side) => { const h = await page.locator(sel).boundingBox(); const sx = side === 'a' ? h.x + h.width - 12 : h.x + 12, sy = h.y + h.height / 2; await page.mouse.move(sx, sy); await page.mouse.down(); await page.mouse.move(box.x + box.width * toFrac + (sx - (side === 'a' ? h.x + h.width : h.x)), sy, { steps: 6 }); await page.mouse.up(); };
  await drag('#hdB', 0.5, 'b'); await drag('#hdA', 0.25, 'a');
  st = await G(() => ({ a: window.__gymTapes.ED.a, b: window.__gymTapes.ED.b, sel: document.getElementById('edSel').textContent }));
  ok('handles dragged to 6 s and 12 s', Math.abs(st.a - 6) < 0.25 && Math.abs(st.b - 12) < 0.25, st);
  await page.click('[data-act="nudge"][data-w="a"][data-d="0.1"]');
  ok('nudge moves start by 0.1 s', Math.abs((await G(() => window.__gymTapes.ED.a)) - st.a - 0.1) < 0.001);
  await page.screenshot({ path: DIR + '/shots/16-editor.png' });
  // preview the selection: starts at a, stops at b
  await page.click('#edPlay'); await sleep(700);
  st = await G(() => { const p = document.getElementById('previewAudio'); return { t: p.currentTime, paused: p.paused, lab: document.getElementById('edPlay').textContent, a: window.__gymTapes.ED.a }; });
  ok('preview plays from the start handle', !st.paused && st.t >= st.a - 0.2 && st.t < st.a + 1.5 && st.lab === 'Stop', st);
  await page.click('#edPlay'); await sleep(100);
  // cut 6-12 s out -> 18 s left; then keep only the first 9 s of what is left
  await page.click('#edCut'); await sleep(200);
  st = await G(() => ({ dur: window.__gymTapes.ED.dur, undo: window.__gymTapes.ED.undo.length, save: document.getElementById('edSave').disabled }));
  ok('cut removes the marked 6 s', Math.abs(st.dur - 17.9) < 0.25 && st.undo === 1 && !st.save, st);
  await page.focus('#hdB'); for (let i = 0; i < 20; i++) await page.keyboard.press('ArrowLeft');
  await page.click('#edKeep'); await sleep(200);
  st = await G(() => ({ dur: window.__gymTapes.ED.dur }));
  ok('keep-only trims to the selection', Math.abs(st.dur - 15.9) < 0.25, st);
  await page.click('#edUndo'); await sleep(150);
  ok('undo restores previous length', Math.abs((await G(() => window.__gymTapes.ED.dur)) - 17.9) < 0.25);
  // close with unsaved edits asks first
  await page.click('[data-act="ed-close"]'); ok('closing with unsaved edits asks before discarding', await page.isVisible('#sheet'));
  await page.click('[data-act="sheet-close"]');
  // save over the track
  const before = await G(() => window.__gymTapes.S.tracks.find(t => t.title === 'Leg-day-beeps').asset);
  await page.click('#edSave');
  await page.waitForFunction(() => document.getElementById('editor').hidden, null, { timeout: 15000 }); await sleep(300);
  st = await G(() => { const t = window.__gymTapes.S.tracks.find(t => t.title === 'Leg-day-beeps'); return { asset: t.asset, dur: t.dur, bytes: t.bytes }; });
  ok('save replaced the audio, old file deleted', st.asset !== before && !blobs.has(before) && blobs.has(st.asset) && Math.abs(st.dur - 17.9) < 0.25, st);
  fs.writeFileSync(DIR + '/out/edited.mp4', blobs.get(st.asset));
  const probe = execSync(`ffprobe -v error -show_entries format=duration:stream=codec_name,nb_frames -of default=nw=1 "${DIR}/out/edited.mp4"`).toString().trim().replace(/\n/g, ' ');
  const decErr = execSync(`ffmpeg -v error -i "${DIR}/out/edited.mp4" -f null - 2>&1 | head -3`).toString().trim();
  // content check: first 6 s low tone (330 Hz), then high tone (660 Hz) from 6 s on, because 6-12 s of low tone was removed
  const freq = at => { const raw = execSync(`ffmpeg -v error -ss ${at} -t 1 -i "${DIR}/out/edited.mp4" -f s16le -ac 1 -ar 48000 -`, { maxBuffer: 1 << 26 }); let z = 0, prev = 0; for (let i = 0; i + 1 < raw.length; i += 2) { const v = raw.readInt16LE(i); if (prev <= 0 && v > 0) z++; prev = v; } return z; };
  const f1 = freq(2), f2 = freq(9);
  ok('edited file is valid and the right audio was removed', /duration=18\.0/.test(probe) && !decErr && Math.abs(f1 - 330) < 15 && Math.abs(f2 - 660) < 15, { probe, decErr, hzAt2s: f1, hzAt9s: f2 });

  // save as new track
  await page.click('.row:has-text("opus-clip") .more'); await page.click('[data-act="m-edit"]');
  await page.waitForFunction(() => window.__gymTapes.ED.seq && !window.__gymTapes.ED.busy);
  await page.focus('#hdA'); for (let i = 0; i < 50; i++) await page.keyboard.press('ArrowRight');
  await page.click('#edKeep'); await page.click('#edSaveNew');
  await page.waitForFunction(() => window.__gymTapes.S.tracks.some(t => t.title === 'opus-clip (edit)'), null, { timeout: 15000 });
  st = await G(() => window.__gymTapes.S.tracks.filter(t => /opus-clip/.test(t.title)).map(t => t.title + ' ' + t.dur));
  ok('save as new keeps the original', st.length === 2, st);

  // delete a track: gone from library, playlists and storage
  const delAsset = await G(() => window.__gymTapes.S.tracks.find(t => t.title === 'Workout loop').asset);
  await page.click('.row:has-text("Workout loop") .more'); await page.click('[data-act="m-delete"]');
  await page.waitForFunction(() => !window.__gymTapes.S.tracks.some(t => t.title === 'Workout loop')); await sleep(300);
  await page.screenshot({ path: DIR + '/shots/17-undo.png' });
  st = await G(() => ({ toast: document.getElementById('toast').textContent, row: !!Array.from(document.querySelectorAll('#view .row .title')).find(e => e.textContent === 'Workout loop'), inDb: Object.values(JSON.parse(localStorage.getItem('fakeDb')).tracks).some(t => t.title === 'Workout loop') }));
  ok('delete hides the upload at once and offers Undo, nothing is erased yet', /deleted/.test(st.toast) && /Undo/.test(st.toast) && !st.row && st.inDb && blobs.has(delAsset), st);
  await page.click('#toast [data-act="toast-act"]');
  await page.waitForFunction(() => window.__gymTapes.S.tracks.some(t => t.title === 'Workout loop')); await sleep(200);
  st = await G(() => ({ legDay: window.__gymTapes.S.playlists.find(p => p.name === 'Leg day').tracks.length, shown: window.__gymTapes.S.tracks.filter(t => t.title === 'Workout loop').length }));
  ok('Undo puts it back, still in its playlist, file untouched', st.shown === 1 && st.legDay === 2 && blobs.has(delAsset), st);
  await page.click('.row:has-text("Workout loop") .more'); await page.click('[data-act="m-delete"]');
  await page.waitForFunction(() => Object.values(JSON.parse(localStorage.getItem('fakeDb')).tracks).some(t => t.title === 'Workout loop' && t.trashed), null, { timeout: 15000 }); await sleep(500);
  st = await G(() => ({ trash: window.__gymTapes.S.trash.map(t => t.title), shown: window.__gymTapes.S.tracks.some(t => t.title === 'Workout loop') }));
  ok('when the Undo offer runs out the upload goes to Recently deleted, its file kept', st.trash.join() === 'Workout loop' && !st.shown && blobs.has(delAsset), st);
  await page.click('#tabSettings'); await sleep(200); await page.click('#binBtn'); await sleep(200); await page.click('[data-act="bin-purge"]'); await page.click('[data-act="bin-purge-go"]');
  await page.waitForFunction(() => !Object.values(JSON.parse(localStorage.getItem('fakeDb')).tracks).some(t => t.title === 'Workout loop'), null, { timeout: 15000 }); await sleep(500);
  st = await G(() => window.__gymTapes.S.playlists.find(p => p.name === 'Leg day').tracks.length);
  ok('Delete for good removes the upload, its file and its playlist entry', !blobs.has(delAsset) && st === 1, { legDayTracks: st });
  await page.click('#tabLibrary'); await sleep(200);

  // reload: library comes back from the store and plays
  await page.reload(); await ready(); await sleep(200);
  st = await G(() => ({ tracks: window.__gymTapes.S.tracks.map(t => t.title), playlists: window.__gymTapes.S.playlists.map(p => p.name + ':' + p.tracks.length), loop: window.__gymTapes.S.loop }));
  ok('library survives a reload', st.tracks.length === 3 && st.playlists.length === 2, st);
  await page.click('[data-act="shuffle-all"]'); await sleep(1000);
  ok('shuffle all starts playback', await G(() => !document.getElementById('audio').paused && window.__gymTapes.S.shuffle));
  ok('lock-screen controls registered', await G(() => 'mediaSession' in navigator && !!navigator.mediaSession.metadata && navigator.mediaSession.metadata.title.length > 0), await G(() => navigator.mediaSession.metadata && navigator.mediaSession.metadata.title));

  // dark theme + desktop width, no sideways scroll
  await page.emulateMedia({ colorScheme: 'dark' }); await sleep(150); await page.screenshot({ path: DIR + '/shots/18-dark.png' });
  ok('no horizontal scroll at phone width', await G(() => document.documentElement.scrollWidth <= window.innerWidth));
  await page.click('.row .more >> nth=0'); await page.click('[data-act="m-edit"]');
  await page.waitForFunction(() => window.__gymTapes.ED.seq && !window.__gymTapes.ED.busy); await page.focus('#hdA'); for (let i = 0; i < 30; i++) await page.keyboard.press('ArrowRight');
  await sleep(100); await page.screenshot({ path: DIR + '/shots/19-editor-dark.png' });
  await page.click('[data-act="ed-close"]');
  await page.setViewportSize({ width: 1200, height: 800 }); await sleep(150); await page.screenshot({ path: DIR + '/shots/20-desktop-dark.png' });
  console.log('errors:', errors.length ? errors : 'none');
  await browser.close(); server.close();
})().catch(e => { console.error('TEST FAILED', e); process.exit(1); });
