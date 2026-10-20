// Test 6 (V4): Settings tab, speed, stop timer, loop count, sections, leveling, fade, search, sort, select, bulk end clips, export.
const { chromium } = require('./pw.js'); require('./legacy');
const http = require('http'), fs = require('fs'), path = require('path');
const { execSync } = require('child_process');
const DIR = __dirname, blobs = new Map(), types = new Map();
const sleep = ms => new Promise(r => setTimeout(r, ms));
let pass = 0, fail = 0; const ok = (label, cond, extra) => { cond ? pass++ : fail++; console.log((cond ? 'PASS ' : 'FAIL ') + label + (extra !== undefined ? '  -> ' + JSON.stringify(extra) : '')); };
const server = http.createServer((req, res) => { res.writeHead(200, { 'content-type': 'text/html' }); res.end(fs.readFileSync(path.join(DIR, 'index.html'))); });
const FAKE = () => {
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
      const u8 = new Uint8Array(await blob.arrayBuffer()); let s = ''; for (let i = 0; i < u8.length; i += 32768) s += String.fromCharCode.apply(null, u8.subarray(i, i + 32768));
      const id = Array.from({ length: 32 }, () => 'abcdef0123456789'[Math.floor(Math.random() * 16)]).join('');
      await window.__putBlob(id, btoa(s), type); return { id, url: '/_blob/' + id, sizeBytes: blob.size, contentType: type };
    },
    async list() { return { assets: [], usage: { files: 1, bytes: 2500000, maxFiles: 500, maxBytes: 1073741824 } }; },
    async delete(id) { return { deleted: await window.__delBlob(id) }; }
  };
  window.__saves = [];
  const downloads = { async save(r) { if (!/\.(mp4|webm|png|jpg|txt|json)$/.test(r.filename)) throw { code: 'rejected_extension' }; window.__saves.push({ filename: r.filename, size: r.data.size }); return { status: 'saved' }; } };
  window.claude = { use: name => new Promise(r => setTimeout(() => r(name === 'db' ? db : name === 'assets' ? assets : name === 'downloads' ? downloads : null), 120)) };
};
(async () => {
  await new Promise(r => server.listen(8769, r));
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
  const optsDoc = () => G(() => (JSON.parse(localStorage.getItem('fakeDb') || '{}').settings || {}).opts);
  const A = () => G(() => { const g = window.__gymTapes, a = g.audio; return { el: a.id, src: (a.getAttribute('src') || '').slice(0, 12), t: a.currentTime, d: a.duration, paused: a.paused, loop: a.loop, rate: a.playbackRate, pitch: a.preservesPitch, sec: g.P.sec, pending: g.P.pendingSec, loops: g.T.loops, at: g.T.at, fx: !!g.FX.ctx, base: g.FX.base, faded: g.FX.faded, gain: g.FX.gain ? g.FX.gain.gain.value : null, chips: Array.from(document.querySelectorAll('#pChips .chip')).map(c => c.textContent) }; });
  const nearEnd = s => G(s => { const a = window.__gymTapes.audio; a.currentTime = a.duration - s; }, s);
  const setting = async fn => { await page.click('#tabSettings'); await fn(); await page.click('#tabLibrary'); await page.click('#libUploads'); };

  await page.goto('http://localhost:8769/'); await ready();
  await page.setInputFiles('#fileInput', [DIR + '/media/Leg-day-beeps.mp4', DIR + '/media/blue-scene.mp4']);
  await page.waitForFunction(() => window.__gymTapes.S.tracks.length === 2, null, { timeout: 60000 }); await sleep(300);
  let t = await trackBy('Leg-day-beeps'); ok('new uploads get a loudness reading for leveling', typeof t.gain === 'number', { beeps: t.gain, blue: (await trackBy('blue-scene')).gain });

  // --- default path: plain element, no extra processing created ---
  await page.click('.row:has-text("Leg-day-beeps") .row-hit'); await sleep(700);
  let a = await A(); ok('default playback uses the plain player, nothing extra created', a.el === 'audio' && !a.fx && !a.paused && a.rate === 1, a);

  // --- settings tab ---
  await page.click('#tabSettings'); await sleep(200);
  ok('Settings tab shows its seven groups', (await page.locator('.group h3').allTextContents()).join('|') === 'Playback|Sound|Uploads|Look|Home|Library|Backup', await page.locator('.group h3').allTextContents());
  ok('settings page fits the phone width', await G(() => document.documentElement.scrollWidth <= window.innerWidth));
  await page.screenshot({ path: DIR + '/shots/50-settings.png', fullPage: true });

  // speed + pitch
  await page.click('[data-k="speed"][data-v="0.75"]'); await sleep(300);
  a = await A(); ok('speed 0.75: rate applied, pitch follows speed, shown in the player', a.rate === 0.75 && a.pitch === false && a.chips.indexOf('0.75×') >= 0 && (await optsDoc()).speed === 0.75, a);
  await page.click('#sw-keepPitch'); await sleep(150);
  a = await A(); ok('keep original pitch switch', a.pitch === true && (await optsDoc()).keepPitch === true);
  await page.click('[data-k="speed"][data-v="1"]'); await page.click('#sw-keepPitch');

  // stop timer
  await page.click('[data-k="timer"][data-v="15"]'); await sleep(200);
  a = await A(); ok('stop timer set for 15 minutes', a.at > Date.now() + 14 * 60000 && a.chips.indexOf('15 min') >= 0 && /stops in about 15 min/.test(await page.textContent('#view')), a.chips);
  await G(() => { window.__gymTapes.T.at = Date.now() - 1; }); await sleep(700);
  a = await A(); ok('when the time is up, playback stops', a.paused && a.at === 0, { toast: await page.textContent('#toast') });

  // stop after loops (loop track mode)
  await page.click('#loopBtn'); await page.click('#loopBtn');   // off -> all -> track
  await page.click('[data-act="loops"][data-d="1"]'); await page.click('[data-act="loops"][data-d="1"]');
  ok('loop counter set to 2', (await page.textContent('#loopsOut')) === '2');
  await page.click('#playBtn'); await sleep(400); await nearEnd(0.5); await sleep(1500);
  a = await A(); ok('after the first full play: one loop left, still playing', a.loops === 1 && !a.paused && a.loop === false && a.t < 3, a);
  await nearEnd(0.5); await sleep(1300);
  a = await A(); ok('after the second play it stops by itself', a.loops === 0 && a.paused, { toast: await page.textContent('#toast') });
  await page.click('#tabLibrary'); await page.click('#libUploads');

  // --- sections ---
  await page.click('.row:has-text("Leg-day-beeps") .more'); await page.click('[data-act="m-edit"]');
  await page.waitForFunction(() => window.__gymTapes.ED.seq && !window.__gymTapes.ED.busy, null, { timeout: 15000 });
  ok('section button waits until a part is marked', await page.isDisabled('#edSec'));
  await page.focus('#hdB'); for (let i = 0; i < 120; i++) await page.keyboard.press('ArrowLeft');    // end: 24 -> 12
  await page.focus('#hdA'); for (let i = 0; i < 60; i++) await page.keyboard.press('ArrowRight');   // start: 0 -> 6
  await page.screenshot({ path: DIR + '/shots/51-editor-section.png' });
  await page.click('#edSec'); await page.waitForFunction(() => document.getElementById('editor').hidden); await sleep(700);
  t = await trackBy('Leg-day-beeps');
  ok('section saved on the track, audio file untouched', t.sec && Math.abs(t.sec.a - 6) < 0.1 && Math.abs(t.sec.b - 12) < 0.1 && Math.abs(t.dur - 24) < 0.1, t.sec);
  ok('track row shows the section length', /0:06, section of 0:24/.test(await page.textContent('.row:has-text("Leg-day-beeps") .meta')));
  await page.click('#playBtn'); await sleep(900);
  a = await A(); ok('plays only the section, from its own file', a.sec && a.src.indexOf('blob:') === 0 && Math.abs(a.d - 6) < 0.15 && !a.paused && a.chips.indexOf('Section') >= 0, a);
  const secB64 = await G(async () => { const r = await fetch(window.__gymTapes.audio.src), u8 = new Uint8Array(await r.arrayBuffer()); let s = ''; for (let i = 0; i < u8.length; i += 32768) s += String.fromCharCode.apply(null, u8.subarray(i, i + 32768)); return btoa(s); });
  fs.writeFileSync(DIR + '/out/section.mp4', Buffer.from(secB64, 'base64'));
  const freq = (f, at) => { const raw = execSync(`ffmpeg -v error -ss ${at} -t 1 -i "${f}" -f s16le -ac 1 -ar 48000 -`, { maxBuffer: 1 << 26 }); let z = 0, prev = 0; for (let i = 0; i + 1 < raw.length; i += 2) { const v = raw.readInt16LE(i); if (prev <= 0 && v > 0) z++; prev = v; } return z; };
  const sdur = +execSync(`ffprobe -v error -show_entries format=duration -of csv=p=0 "${DIR}/out/section.mp4"`).toString();
  ok('the section file is the right 6 seconds (low tone, 330 Hz)', Math.abs(sdur - 6) < 0.15 && Math.abs(freq(DIR + '/out/section.mp4', 1) - 330) < 15 && Math.abs(freq(DIR + '/out/section.mp4', 4.5) - 330) < 15, { sdur, hz: freq(DIR + '/out/section.mp4', 1) });
  await nearEnd(0.4); await sleep(1300);
  a = await A(); ok('loop track loops the section', !a.paused && a.t < 3 && a.sec, { t: a.t });
  await setting(async () => { await page.click('#sw-sections'); await sleep(600); });
  a = await A(); ok('switching sections off plays the whole track again, without stopping', !a.sec && a.src.indexOf('/_blob/') === 0 && Math.abs(a.d - 24) < 0.2 && !a.paused && a.t >= 6, a);
  await setting(async () => { await page.click('#sw-sections'); await sleep(600); });
  a = await A(); ok('switching sections back on returns to the section', a.sec && Math.abs(a.d - 6) < 0.15 && !a.paused, a);
  await page.reload(); await ready(); await sleep(900);
  await page.click('.row:has-text("Leg-day-beeps") .row-hit'); await sleep(700);
  a = await A(); ok('after a reload the section is ready before the first tap', a.sec && !a.pending && Math.abs(a.d - 6) < 0.15, a);

  // --- sound options: leveling and fade ---
  await setting(async () => { await page.click('#sw-level'); await sleep(900); });
  a = await A(); t = await trackBy('Leg-day-beeps');
  ok('volume leveling: switches to the processed player and keeps playing', a.el === 'audioFx' && a.fx && !a.paused && Math.abs(a.base - Math.pow(10, t.gain / 20)) < 0.01, { gainDb: t.gain, base: a.base });
  const before = a.t; await sleep(700); a = await A(); ok('sound is running through the processing', a.t !== before && a.gain > 0.01, { gain: a.gain });
  await setting(async () => { await page.click('[data-k="fade"][data-v="300"]'); await sleep(300); });
  await nearEnd(0.75); await sleep(650);
  a = await A(); ok('loop fade: volume dips at the loop point', a.faded || a.gain < a.base * 0.8, { gain: a.gain, base: a.base, faded: a.faded });
  await sleep(1200); a = await A(); ok('and comes back after it', Math.abs(a.gain - a.base) < 0.08 && !a.paused, { gain: a.gain, base: a.base });
  await setting(async () => { await page.click('#sw-level'); await page.click('[data-k="fade"][data-v="0"]'); await sleep(700); });
  a = await A(); ok('turning both off goes back to the plain player, still playing', a.el === 'audio' && !a.paused, a);
  await page.click('#playBtn');

  // --- search, sort, select ---
  await page.setInputFiles('#fileInput', DIR + '/media/all-black.mp4');
  await page.waitForFunction(() => window.__gymTapes.S.tracks.length === 3, null, { timeout: 60000 }); await sleep(300);
  await page.click('#tabSearch'); await page.fill('#q', 'BLUE'); await sleep(150);
  ok('search narrows the results as you type', (await page.locator('#searchOut .row .title').allTextContents()).join() === 'blue-scene' && (await G(() => document.activeElement.id)) === 'q');
  await page.fill('#q', 'zzz'); await sleep(100); ok('no match message', /Nothing matches/.test(await page.textContent('#searchOut')));
  await page.fill('#q', ''); await sleep(100);
  await page.click('#tabLibrary'); await page.click('#libUploads');
  await page.click('[data-act="sort"]'); await page.screenshot({ path: DIR + '/shots/52-sort.png' }); await page.click('.opt:has-text("A to Z")'); await sleep(200);
  ok('sort A to Z', (await page.locator('#trackList .row .title').allTextContents()).join() === 'all-black,blue-scene,Leg-day-beeps' && (await optsDoc()).sort === 'az');
  await page.click('[data-act="sort"]'); await page.click('.opt:has-text("Shortest first")'); await sleep(200);
  ok('sort shortest first counts a section as its own length', (await page.locator('#trackList .row .title').allTextContents()).join() === 'Leg-day-beeps,all-black,blue-scene');
  await page.click('[data-act="sel-start"]'); await page.click('.row:has-text("all-black") .row-hit'); await page.click('.row:has-text("blue-scene") .row-hit'); await sleep(100);
  ok('select mode counts picks', (await page.textContent('#selCount')) === '2 selected'); await page.screenshot({ path: DIR + '/shots/53-select.png' });
  await page.click('[data-act="sel-add"]'); await page.click('[data-act="sel-new"]'); await page.fill('#plNameInput', 'Mix'); await page.click('form[data-form="playlist"] button[type=submit]');
  await page.waitForFunction(() => window.__gymTapes.S.playlists.length === 1); const pl = await G(() => window.__gymTapes.S.playlists[0]);
  ok('several tracks into a new playlist at once', pl.name === 'Mix' && pl.tracks.length === 2, pl.tracks.length);
  await page.click('#tabLibrary'); await page.click('#libUploads'); await page.click('[data-act="sel-start"]'); await page.click('.row:has-text("all-black") .row-hit'); await page.click('[data-act="sel-del"]');
  await page.waitForFunction(() => window.__gymTapes.S.tracks.length === 2); await sleep(300);
  ok('delete several at once leaves select mode and offers Undo', /Undo/.test(await page.textContent('#toast')) && !(await page.isVisible('#selCount')));
  await page.waitForFunction(() => window.__gymTapes.S.trash.length === 1 && window.__gymTapes.S.playlists[0].tracks.filter(id => window.__gymTapes.S.tracks.some(t => t.id === id)).length === 1, null, { timeout: 15000 });
  ok('once the Undo offer runs out they go to Recently deleted, out of sight in playlists too', true);

  // --- export ---
  await page.click('.row:has-text("blue-scene") .more'); await page.click('[data-act="m-export"]'); await sleep(600);
  const saves = await G(() => window.__saves); ok('Save as a file hands over the audio', saves.length === 1 && saves[0].filename === 'blue-scene.mp4' && saves[0].size > 100000, saves);

  // --- bulk end clips ---
  await setting(async () => { await page.click('#autoTrimSwitch'); });
  await page.setInputFiles('#fileInput', DIR + '/media/opus-clip.mp4');
  await page.waitForFunction(() => window.__gymTapes.S.tracks.length === 3, null, { timeout: 60000 }); await sleep(300);
  t = await trackBy('opus-clip'); const full = t.dur;
  await page.click('#tabSettings'); await page.click('[data-act="trim-all"]');
  await page.waitForFunction(() => /end clip/i.test(document.getElementById('toast').textContent) && !document.getElementById('toast').hidden, null, { timeout: 60000 });
  t = await trackBy('opus-clip'); ok('"Check every track" removes the end clip where there is one', full > 31 && t.dur < 27.2 && t.dur > 26.5 && /from 1 upload/.test(await page.textContent('#toast')), { before: full, after: t.dur, toast: await page.textContent('#toast') });
  await page.click('#autoTrimSwitch');

  // --- options are remembered ---
  await page.click('[data-k="speed"][data-v="1.15"]'); await sleep(200);
  await page.reload(); await ready(); await sleep(300);
  const o = await G(() => window.__gymTapes.S.opt); ok('options come back after a reload', o.speed === 1.15 && o.sort === 'short' && o.autoTrim === true && o.sections === true && o.level === false, o);
  await page.click('#tabSettings'); await page.emulateMedia({ colorScheme: 'dark' }); await sleep(200); await page.screenshot({ path: DIR + '/shots/54-settings-dark.png', fullPage: true });
  await page.click('#tabLibrary'); await page.click('#libUploads'); await page.click('.row:has-text("Leg-day-beeps") .row-hit'); await sleep(600); await page.screenshot({ path: DIR + '/shots/55-tracks-dark.png' });
  ok('no page errors', errors.length === 0, errors);
  console.log(`\n${pass} passed, ${fail} failed`);
  await browser.close(); server.close();
})().catch(e => { console.error('TEST FAILED', e); process.exit(1); });
