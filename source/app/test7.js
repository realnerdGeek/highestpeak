// Test 7 (V5): bottom bar, Home, Library, Search, Upload tab, smaller player, wording.
const { chromium } = require('./pw.js'); require('./legacy');
const http = require('http'), fs = require('fs'), path = require('path');
const DIR = __dirname, blobs = new Map(), types = new Map();
const sleep = ms => new Promise(r => setTimeout(r, ms));
let pass = 0, fail = 0; const ok = (label, cond, extra) => { cond ? pass++ : fail++; console.log((cond ? 'PASS ' : 'FAIL ') + label + (extra !== undefined ? '  -> ' + JSON.stringify(extra) : '')); };
const server = http.createServer((req, res) => { res.writeHead(200, { 'content-type': 'text/html' }); res.end(fs.readFileSync(path.join(DIR, 'index.html'))); });
const FAKE = fs.readFileSync(path.join(DIR, 'test6.js'), 'utf8').match(/const FAKE = \(\) => \{[\s\S]*?\n\};\n/)[0];
(async () => {
  await new Promise(r => server.listen(8770, r));
  const browser = await chromium.launch({ args: ['--autoplay-policy=no-user-gesture-required'] });
  const ctx = await browser.newContext({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 2, hasTouch: true });
  await ctx.exposeFunction('__putBlob', (id, b64, type) => { blobs.set(id, Buffer.from(b64, 'base64')); types.set(id, type); });
  await ctx.exposeFunction('__delBlob', id => blobs.delete(id));
  await ctx.addInitScript(FAKE + '; FAKE();');
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
  const sel = id => page.getAttribute(id, 'aria-selected');
  const text = () => page.textContent('#view');
  const fits = () => G(() => document.documentElement.scrollWidth <= window.innerWidth);

  await page.goto('http://localhost:8770/'); await ready(); await sleep(200);
  ok('opens on Home with the five-item bar', (await sel('#tabHome')) === 'true' && (await page.locator('#nav button').allTextContents()).map(s => s.trim()).join('|') === 'Home|Library|Upload|Search|Settings', await page.locator('#nav button').allTextContents());
  ok('empty Home points to Upload', /Nothing here yet/.test(await text()) && await page.isVisible('#view [data-tab="upload"]'));
  await page.screenshot({ path: DIR + '/shots/60-home-empty.png' });
  await page.click('#view [data-tab="upload"]');
  ok('that button opens the Upload tab', (await sel('#tabUpload')) === 'true' && /Add videos or audio/.test(await text()) && await page.isVisible('#addBtn') && await page.isVisible('#upTrimSwitch'));
  await page.screenshot({ path: DIR + '/shots/61-upload-empty.png' });

  // upload three at once from the Upload tab and watch the queue
  await page.setInputFiles('#fileInput', [DIR + '/media/blue-scene.mp4', DIR + '/media/Leg-day-beeps.mp4', DIR + '/media/notes.mp4', DIR + '/media/opus-clip.mp4']);
  await sleep(250);
  const q0 = await G(() => ({ rows: document.querySelectorAll('#imports .imp').length, dot: !document.getElementById('upDot').hidden, head: (document.querySelector('.group h3') || {}).textContent }));
  ok('queue shows every file and the bar shows work in progress', q0.rows >= 3 && q0.dot && /Working on/.test(q0.head), q0);
  await page.screenshot({ path: DIR + '/shots/62-upload-working.png' });
  await page.click('#tabHome'); await sleep(200);     // leave while it works
  await page.waitForFunction(() => window.__gymTapes.S.tracks.length === 3 && document.getElementById('upDot').hidden, null, { timeout: 90000 }); await sleep(300);
  ok('uploads keep going after leaving the tab', true);
  await page.click('#tabUpload'); await sleep(200);
  const up = await G(() => ({ err: document.querySelector('#imports .imp.err .st') ? document.querySelector('#imports .imp.err .st').textContent : null, done: Array.from(document.querySelectorAll('#view .list .row .title')).map(e => e.textContent), acts: document.querySelectorAll('#view .acts').length }));
  ok('finished ones are listed under Just added with their options, the bad file shows why', up.done.length === 3 && up.acts === 3 && /Could not read this file/.test(up.err || '') && /Just added/.test(await text()), up);
  await page.screenshot({ path: DIR + '/shots/63-upload-done.png', fullPage: true });
  await page.click('[data-act="imp-dismiss"]'); ok('dismissing the failed one clears it', !(await page.isVisible('#imports .imp')));
  await page.click('.acts >> nth=0 >> [data-act="up-rename"]'); await page.fill('#renameInput', 'Cooldown'); await page.click('form[data-form="rename"] button[type=submit]');
  await page.waitForFunction(() => window.__gymTapes.S.tracks.some(t => t.title === 'Cooldown'));
  ok('rename straight from the Upload tab', true);
  await page.click('.acts >> nth=0 >> [data-act="up-pl"]'); await page.click('[data-act="pl-new-with"]'); await page.fill('#plNameInput', 'Leg day'); await page.click('form[data-form="playlist"] button[type=submit]');
  await page.waitForFunction(() => window.__gymTapes.S.playlists.length === 1 && window.__gymTapes.S.playlists[0].tracks.length === 1);
  ok('add to a playlist straight from the Upload tab', true);
  await page.click('#upTrimSwitch'); ok('end clip switch on the Upload tab is the same setting', (await G(() => window.__gymTapes.S.opt.autoTrim)) === false); await page.click('#upTrimSwitch');

  // Home
  await page.click('#tabHome'); await sleep(200);
  let h = await text();
  ok('Home shows greeting, totals, playlists and newest uploads', /Good (morning|afternoon|evening)|Up late/.test(h) && /3 uploads/.test(h) && /Shuffle everything/.test(h) && /Playlists/.test(h) && /Newest uploads/.test(h) && !(await page.$('#rotGrid')));
  await page.click('#view .list .row:has-text("blue-scene") .row-hit'); await sleep(700);
  await page.click('#view .list .row:has-text("Leg-day-beeps") .row-hit'); await sleep(700);
  ok('Home does not rearrange itself while it is open', !(await page.$('#rotGrid')));
  await page.click('#tabHome'); await sleep(200);
  h = await text(); const strip = await page.locator('#rotGrid .rot .title').allTextContents(), meta = await page.locator('#rotGrid .rot .meta').allTextContents();
  ok('after playing, Your rotation shows them, last played first (V14: as quick picks with no heading)', !!(await page.$('#rotGrid')) && strip.join() === 'Leg-day-beeps,blue-scene' && meta[0] === 'Last played', { strip, meta });
  ok('Home fits the phone width', await fits());
  await page.screenshot({ path: DIR + '/shots/64-home.png', fullPage: true });
  await page.click('#rotGrid .rot:has-text("blue-scene")'); await sleep(600);
  ok('tapping one in Your rotation plays it from that list', (await page.textContent('#pTitle')) === 'blue-scene' && /Your rotation/.test(await page.textContent('#pMeta')), await page.textContent('#pMeta'));
  await page.click('#plStrip .tile:has-text("Leg day")'); await sleep(200);
  ok('tapping a playlist on Home opens it in Library', (await sel('#tabLibrary')) === 'true' && await page.isVisible('.pl-head'));
  await page.click('[data-act="pl-back"]'); ok('back lands on the Library playlists', (await sel('#libPlaylists')) === 'true');

  // smaller player
  const bigH = await G(() => document.getElementById('player').offsetHeight);
  await page.click('#sizeBtn'); await sleep(150);
  const mini = await G(() => ({ h: document.getElementById('player').offsetHeight, wave: getComputedStyle(document.getElementById('wave')).display, play: getComputedStyle(document.getElementById('miniPlay')).display, pad: getComputedStyle(document.getElementById('app')).paddingBottom }));
  ok('player shrinks to one row with play and next', mini.h < bigH - 80 && mini.wave === 'none' && mini.play !== 'none', { bigH, mini });
  await page.click('#miniPlay'); await sleep(200); ok('small play button works', await G(() => window.__gymTapes.audio.paused));
  await page.screenshot({ path: DIR + '/shots/65-library-mini.png' });
  await page.reload(); await ready(); await sleep(300);
  ok('player size and Your rotation are remembered, and the last upload is back in the player', (await G(() => window.__gymTapes.S.mini)) === true && (await page.locator('#rotGrid .rot .title').allTextContents())[0] === 'blue-scene' && (await page.textContent('#pTitle')) === 'blue-scene' && !(await page.isHidden('#player')) && (await G(() => window.__gymTapes.audio.paused)));
  await page.click('.strip .tile >> nth=0'); await sleep(500); await page.click('#sizeBtn'); await sleep(150);
  ok('and it grows back', (await G(() => getComputedStyle(document.getElementById('wave')).display)) !== 'none');
  await page.click('#playBtn');

  // Library
  await page.click('#tabLibrary'); await page.click('#libUploads'); await sleep(150);
  ok('Library lists all uploads with play, shuffle, sort and select', (await page.locator('#trackList .row').count()) === 3 && await page.isVisible('[data-act="sort"]') && await page.isVisible('[data-act="sel-start"]') && /3 uploads/.test(await page.textContent('#trackCount')), await page.textContent('#trackCount'));
  await page.screenshot({ path: DIR + '/shots/66-library.png' });
  await page.click('#libPlaylists'); ok('Library playlists side: the Liked list plus the one playlist', (await page.locator('.grid .pl-row .title').allTextContents()).join() === 'Liked,Leg day');

  // Search
  await page.click('#tabSearch'); await sleep(150);
  ok('Search starts with a hint', /Type a name/.test(await page.textContent('#searchOut')));
  await page.fill('#q', 'leg'); await sleep(150);
  const sr = await G(() => ({ heads: Array.from(document.querySelectorAll('#searchOut .sec-h h3')).map(e => e.textContent), titles: Array.from(document.querySelectorAll('#searchOut .row .title')).map(e => e.textContent) }));
  ok('one search finds both the playlist and the upload', sr.heads.join() === 'Playlists,Uploads' && sr.titles.join() === 'Leg day,Leg-day-beeps', sr);
  await page.screenshot({ path: DIR + '/shots/67-search.png' });
  await page.click('#searchOut .row:has-text("Leg-day-beeps") .row-hit'); await sleep(600);
  ok('playing from search', (await page.textContent('#pTitle')) === 'Leg-day-beeps' && /Search results/.test(await page.textContent('#pMeta')));
  await page.click('#searchOut .row:has-text("Leg day") .row-hit'); await sleep(200);
  ok('tapping a playlist result opens it', await page.isVisible('.pl-head') && (await sel('#tabLibrary')) === 'true');
  await page.click('#playBtn');

  // wording
  const words = [];
  for (const tab of ['#tabHome', '#tabLibrary', '#tabUpload', '#tabSearch', '#tabSettings']) { await page.click(tab); await sleep(120); words.push(await text()); }
  await page.click('#tabLibrary'); await page.click('#libUploads'); await page.click('.row .more >> nth=0'); words.push(await page.textContent('#sheetPanel')); await page.click('[data-act="sheet-close"]');
  const bad = words.join(' ').match(/\btracks?\b/gi);
  ok('no screen still says "track"', !bad, bad);
  await page.click('#loopBtn'); await page.click('#loopBtn'); ok('loop label reads Loop one', (await page.textContent('#loopLab')) === 'Loop one'); await page.click('#loopBtn');
  // dark + desktop
  await page.click('#tabHome'); await page.emulateMedia({ colorScheme: 'dark' }); await sleep(200); await page.screenshot({ path: DIR + '/shots/68-home-dark.png' });
  await page.setViewportSize({ width: 1100, height: 800 }); await sleep(200); ok('fits a wide screen too', await fits()); await page.screenshot({ path: DIR + '/shots/69-desktop.png' });
  ok('no page errors', errors.length === 0, errors);
  console.log(`\n${pass} passed, ${fail} failed`);
  await browser.close(); server.close();
})().catch(e => { console.error('TEST FAILED', e); process.exit(1); });
