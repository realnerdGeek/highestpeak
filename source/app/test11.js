// Test 11 (V8): Your rotation, Home switches, playlist collages, stats, pick up where you left off, start delay, volume, swipes, join.
const { chromium } = require('./pw.js'); require('./legacy');
const http = require('http'), fs = require('fs'), path = require('path');
const { execFileSync } = require('child_process');
const DIR = __dirname, OUT = path.join(DIR, 'out'), blobs = new Map(), types = new Map();
const sleep = ms => new Promise(r => setTimeout(r, ms));
let pass = 0, fail = 0; const ok = (label, cond, extra) => { cond ? pass++ : fail++; console.log((cond ? 'PASS ' : 'FAIL ') + label + (extra !== undefined ? '  -> ' + JSON.stringify(extra) : '')); };
const server = http.createServer((req, res) => { res.writeHead(200, { 'content-type': 'text/html' }); res.end(fs.readFileSync(path.join(DIR, 'index.html'))); });
const FAKE = fs.readFileSync(path.join(DIR, 'test6.js'), 'utf8').match(/const FAKE = \(\) => \{[\s\S]*?\n\};\n/)[0];
const probe = buf => { const f = path.join(OUT, 'join-' + Date.now() + '.mp4'); fs.writeFileSync(f, buf); const info = execFileSync('ffprobe', ['-v', 'error', '-show_entries', 'stream=codec_name,channels:format=duration', '-of', 'json', f]).toString(); const errs = execFileSync('ffmpeg', ['-v', 'error', '-i', f, '-f', 'null', '-']).toString() + ''; return Object.assign(JSON.parse(info), { errs }); };

(async () => {
  await new Promise(r => server.listen(8774, r));
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
  const db = () => G(() => JSON.parse(localStorage.getItem('fakeDb') || '{}'));
  const titles = sel => page.locator(sel).allTextContents();
  const fits = () => G(() => document.documentElement.scrollWidth <= window.innerWidth);
  const seekFrac = f => G(f => { const a = window.__gymTapes.audio; a.currentTime = a.duration * f; }, f);
  const A = () => G(() => { const g = window.__gymTapes, a = g.audio; return { src: (a.getAttribute('src') || '').slice(0, 6), t: a.currentTime, paused: a.paused, cur: (g.S.tracks.find(t => t.id === g.P.cur) || {}).title, count: !!g.P.countIn }; });
  const cdp = await ctx.newCDPSession(page);
  const touch = (type, x, y) => cdp.send('Input.dispatchTouchEvent', { type, touchPoints: type === 'touchEnd' ? [] : [{ x, y }] });
  const swipe = async (x0, y0, x1, y1, steps = 10) => { await touch('touchStart', x0, y0); for (let i = 1; i <= steps; i++) { await touch('touchMove', x0 + (x1 - x0) * i / steps, y0 + (y1 - y0) * i / steps); await sleep(16); } await touch('touchEnd'); await sleep(320); };
  const rowBox = async sel => { await page.locator(sel).scrollIntoViewIfNeeded(); const b = await page.locator(sel).boundingBox(); return { x: b.x + b.width * 0.45, y: b.y + b.height / 2, w: b.width }; };

  await page.goto('http://localhost:8774/'); await ready();
  await page.setInputFiles('#fileInput', [DIR + '/media/Leg-day-beeps.mp4', DIR + '/media/blue-scene.mp4', DIR + '/media/all-black.mp4', DIR + '/media/opus-clip.mp4']);
  await page.waitForFunction(() => window.__gymTapes.S.tracks.length === 4 && document.getElementById('upDot').hidden, null, { timeout: 90000 }); await sleep(400);
  await page.click('#tabHome'); await sleep(200);
  ok('before anything is played there is no Your rotation and no stats', !/Your rotation/.test(await page.textContent('#view')) && !(await page.isVisible('.stat-chips')));

  // ---------- Your rotation ----------
  await page.click('#tabLibrary'); await page.click('#libUploads'); await sleep(200);
  for (const t of ['Leg-day-beeps', 'blue-scene']) { await page.click(`#trackList .row:has-text("${t}") .row-hit`); await sleep(500); await seekFrac(0.6); await sleep(700); }
  await page.click('#trackList .row:has-text("all-black") .row-hit'); await sleep(500);
  await page.click('#tabHome'); await sleep(250);
  let st = { titles: await titles('#rotGrid .rot .title'), metas: await titles('#rotGrid .rot .meta'), cols: await G(() => getComputedStyle(document.getElementById('rotGrid')).gridTemplateColumns.split(' ').length), jump: /Jump back in|Most played/.test(await page.textContent('#view')) };
  ok('Your rotation: last played first, then the most played, in a two-column grid', st.titles.join() === 'all-black,Leg-day-beeps,blue-scene' && st.metas.join() === 'Last played,1 play,1 play' && st.cols === 2 && !st.jump, st);
  ok('Home fits the phone width', await fits());
  await page.click('#rotGrid .rot:has-text("blue-scene")'); await sleep(400);
  ok('tapping a card plays it from Your rotation', /^Your rotation, 3 of 3$/.test(await page.textContent('#pMeta')), await page.textContent('#pMeta'));
  await page.screenshot({ path: DIR + '/shots/a0-home-rotation.png' });

  // ---------- Home switches ----------
  await page.click('#tabSettings'); await sleep(200);
  ok('Settings has a Home group with five switches, all on', (await page.locator('.group:has(h3:text-is("Home")) .switch[aria-checked="true"]').count()) === 5);
  await page.click('#sw-hRotation'); await page.click('#sw-hNewest'); await page.click('#sw-hPresets'); await sleep(200);
  await page.click('#tabHome'); await sleep(200);
  let txt = await page.textContent('#view');
  ok('switched-off sections leave Home, the rest stay', !/Your rotation/.test(txt) && !/Newest uploads/.test(txt) && !/Presets/.test(txt) && /Playlists/.test(txt) && /Shuffle everything/.test(txt));
  await page.waitForFunction(() => { const o = (JSON.parse(localStorage.getItem('fakeDb')).settings || {}).opts; return o && o.hRotation === false && o.hNewest === false; });
  ok('the Home layout is saved with the other settings', true);
  await page.click('#tabSettings'); await page.click('#sw-hRotation'); await page.click('#sw-hNewest'); await page.click('#sw-hPresets'); await sleep(150);

  // ---------- playlist covers ----------
  await page.click('#tabLibrary'); await page.click('#libUploads'); await page.click('[data-act="sel-start"]');
  for (const t of ['Leg-day-beeps', 'blue-scene', 'all-black', 'opus-clip']) await page.click(`#trackList .row:has-text("${t}") .row-hit`);
  await page.click('[data-act="sel-add"]'); await page.click('[data-act="sel-new"]'); await page.fill('#plNameInput', 'Four'); await page.click('form[data-form="playlist"] button[type=submit]');
  await page.waitForFunction(() => window.__gymTapes.S.playlists.length === 1); await sleep(300);
  st = await G(() => { const c = document.querySelector('.pl-head .cover'), cells = c.querySelectorAll(':scope > .cover'); return { mosaic: c.classList.contains('mosaic'), cells: cells.length, w: c.offsetWidth, cw: cells[0] && cells[0].offsetWidth, imgs: c.querySelectorAll('img').length }; });
  ok('a playlist with four uploads and no picture gets a 2x2 collage of their covers', st.mosaic && st.cells === 4 && Math.abs(st.cw - st.w / 2) <= 1 && st.imgs >= 1, st);
  await page.screenshot({ path: DIR + '/shots/a1-collage.png' });
  await page.click('[data-act="pl-back"]'); await page.click('[data-act="pl-new"]'); await page.fill('#plNameInput', 'Empty'); await page.click('form[data-form="playlist"] button[type=submit]'); await sleep(400);
  await page.click('[data-act="pl-add"]'); await page.click('#sheetPanel .opt:has-text("blue-scene")'); await sleep(250); await page.click('[data-act="sheet-close"]'); await sleep(250);
  st = await G(() => { const c = document.querySelector('.pl-head .cover'); return { mosaic: c.classList.contains('mosaic'), img: !!c.querySelector('img'), letter: !!c.querySelector('b') }; });
  ok('with fewer than four it shows the first upload\'s cover instead of a letter', !st.mosaic && st.img && !st.letter, st);
  await page.click('[data-act="pl-back"]'); await sleep(200);
  ok('the Library grid shows the collage too', (await page.locator('.grid .pl-row:has-text("Four") .cover.mosaic > .cover').count()) === 4);

  // ---------- stats ----------
  await G(() => { const g = window.__gymTapes, k = n => { const d = new Date(); d.setHours(12, 0, 0, 0); d.setDate(d.getDate() - n); return d.getFullYear() + '-' + String(d.getMonth() + 1).padStart(2, '0') + '-' + String(d.getDate()).padStart(2, '0'); };
    g.ST.days[k(1)] = { s: 900, p: {} }; g.ST.days[k(2)] = { s: 300, p: {} }; g.ST.days[k(4)] = { s: 1200, p: {} }; g.ST.total += 2400; g.addListen(600); });
  await page.click('#tabSettings'); await page.click('#tabHome'); await sleep(250);
  st = { chips: await titles('.stat-chips .stat-chip') };
  ok('Home shows the streak and time listened', st.chips.length === 2 && /^3 day streak$/.test(st.chips[0].trim()) && /^50 min listened$/.test(st.chips[1].trim()), st);
  await page.click('.stat-chip >> nth=0'); await sleep(350);
  st = await G(() => ({ big: Array.from(document.querySelectorAll('.stats-big b')).map(e => e.textContent), bars: document.querySelectorAll('#weekChart button').length, today: (document.querySelector('#weekChart .today .v') || {}).textContent, read: document.getElementById('weekRead').textContent,
    top: Array.from(document.querySelectorAll('#sheetPanel .opt.static')).map(e => e.querySelector('.grow').textContent + ':' + e.querySelector('.tick').textContent), h: Array.from(document.querySelectorAll('#weekChart i')).map(i => i.style.height) }));
  ok('the stats sheet: totals, a 7-day chart labelled only on today, and the week\'s most played', st.big[2] === '3 days' && st.bars === 7 && st.today === '10' && /^Today: 10 min$/.test(st.read) && st.top.join() === 'Leg-day-beeps:1 play,blue-scene:1 play' && st.h[2] === '100%' && st.h[3] === '0%' && /^5[0-3]%$/.test(st.h[6]), st);
  await page.screenshot({ path: DIR + '/shots/a2-stats.png' });
  await page.click('#weekChart button >> nth=5'); await sleep(250);
  ok('tapping a day shows its minutes', /: 15 min$/.test(await page.textContent('#weekRead')), await page.textContent('#weekRead'));
  await page.click('[data-act="sheet-close"]'); await sleep(250);
  await G(() => window.__gymTapes.saveStats());
  await page.waitForFunction(() => { const s = (JSON.parse(localStorage.getItem('fakeDb')).settings || {}).stats; return s && s.total >= 3000 && Object.keys(s.days).length >= 4; });
  ok('stats are saved with the library', true);

  // ---------- pick up where you left off ----------
  await page.click('#tabLibrary'); await page.click('#libUploads'); await page.click('#trackList .row:has-text("opus-clip") .row-hit'); await sleep(500);
  await seekFrac(0.4); await sleep(400); await page.click('.ctl [data-act="toggle"]'); await sleep(300);
  const before = await G(() => ({ t: window.__gymTapes.audio.currentTime, order: window.__gymTapes.P.order.slice(), label: window.__gymTapes.P.label }));
  await page.reload(); await ready(); await sleep(900);
  st = await G(() => { const g = window.__gymTapes; return { title: document.getElementById('pTitle').textContent, shown: !document.getElementById('player').hidden, paused: g.audio.paused, t: g.audio.currentTime, order: g.P.order.slice(), label: g.P.label, tcur: document.getElementById('tCur').textContent, chips: document.querySelectorAll('.stat-chip').length }; });
  ok('after a reload the last upload, its queue and its spot are back, paused', st.title === 'opus-clip' && st.shown && st.paused && Math.abs(st.t - before.t) < 0.6 && st.order.join() === before.order.join() && st.label === before.label, { before: before.t, st });
  ok('stats come back after a reload too', st.chips === 2);
  await page.click('.ctl [data-act="toggle"]'); await sleep(600);
  st = await A(); ok('one tap carries on from that spot', !st.paused && st.cur === 'opus-clip' && st.t > before.t && st.t < before.t + 2, { st, before: before.t });

  // ---------- start delay ----------
  await page.click('.ctl [data-act="toggle"]'); await sleep(200);
  await page.click('#tabSettings'); await page.click('[data-k="delay"][data-v="3"]'); await sleep(200);
  ok('Start delay is in Settings and is saved', (await G(() => window.__gymTapes.S.opt.delay)) === 3 && /Counts down 3 seconds/.test(await page.textContent('#view')));
  await page.click('#tabLibrary'); await page.click('#libUploads'); await page.click('#trackList .row:has-text("Leg-day-beeps") .row-hit'); await sleep(300);
  st = await G(() => ({ count: !!window.__gymTapes.P.countIn, shown: !document.getElementById('countdown').hidden, num: document.getElementById('cdNum').textContent, name: document.getElementById('cdTitle').textContent, meta: document.getElementById('pMeta').textContent, playing: !window.__gymTapes.audio.paused, title: document.getElementById('pTitle').textContent, tcur: document.getElementById('tCur').textContent }));
  ok('tapping play with nothing playing starts a 3 second count-in', st.count && st.shown && st.num === '3' && st.name === 'Leg-day-beeps' && st.meta === 'Starting in 3' && st.playing && st.title === 'Leg-day-beeps' && st.tcur === '0:00', st);
  await page.screenshot({ path: DIR + '/shots/a3-countdown.png' });
  await sleep(1200); const mid = await G(() => document.getElementById('cdNum').textContent);
  await page.waitForFunction(() => !window.__gymTapes.P.countIn, null, { timeout: 6000 }); await sleep(500);
  st = await A();
  ok('it counts down, then the upload plays from the start', /^[12]$/.test(mid) && !st.count && !st.paused && st.cur === 'Leg-day-beeps' && st.t > 0.1 && st.t < 1.5 && (await page.isHidden('#countdown')), { mid, st });
  await page.click('#trackList .row:has-text("all-black") .row-hit'); await sleep(400);
  st = await A(); ok('switching while something plays starts at once', !st.count && st.cur === 'all-black' && !st.paused, st);
  await seekFrac(0.5); await sleep(300); await page.click('.ctl [data-act="toggle"]'); await sleep(200);
  const pausedAt = await G(() => window.__gymTapes.audio.currentTime);
  await page.click('.ctl [data-act="toggle"]'); await sleep(300);
  ok('resuming from pause counts in again', await G(() => !!window.__gymTapes.P.countIn));
  await page.waitForFunction(() => !window.__gymTapes.P.countIn, null, { timeout: 6000 }); await sleep(500);
  st = await A(); ok('then picks up where it was paused', st.cur === 'all-black' && !st.paused && st.t >= pausedAt - 0.1 && st.t < pausedAt + 1.5, { pausedAt, st });
  await G(() => { const a = window.__gymTapes.audio; a.currentTime = a.duration - 0.4; }); await sleep(1500);
  st = await A(); ok('the next upload in line starts right away, no count-in', !st.count && st.cur !== 'all-black' && !st.paused, st);
  await page.click('.ctl [data-act="toggle"]'); await sleep(150);
  await page.click('#tabSettings'); await page.click('[data-k="delay"][data-v="0"]'); await sleep(150);

  // ---------- volume (a computer browser can set it) ----------
  await page.click('#tabLibrary'); await page.click('#libUploads'); await page.click('#trackList .row:has-text("blue-scene") .row-hit'); await sleep(400);
  ok('the volume bar shows on a computer', await page.isVisible('#player .vol .js-vol'));
  await page.locator('#player .js-vol').fill('35'); await sleep(100);
  st = await G(() => ({ a0: document.getElementById('audio').volume, a1: document.getElementById('audioFx').volume, saved: localStorage.getItem('gymtapes.vol'), other: document.querySelector('#full .js-vol').value }));
  ok('moving it sets the app\'s own volume and keeps both bars in step', Math.abs(st.a0 - 0.35) < 0.01 && Math.abs(st.a1 - 0.35) < 0.01 && st.saved === '0.35' && st.other === '35', st);
  await page.click('#player .js-vol-ic'); await sleep(100); const muted = await G(() => document.getElementById('audio').volume);
  await page.click('#player .js-vol-ic'); await sleep(100);
  ok('the speaker button mutes and brings it back', muted === 0 && Math.abs((await G(() => document.getElementById('audio').volume)) - 0.35) < 0.01, { muted });
  await page.screenshot({ path: DIR + '/shots/a4-volume.png' });

  // ---------- swipes ----------
  let r = await rowBox('#trackList .row:has-text("opus-clip")');
  await swipe(r.x, r.y, r.x + 160, r.y + 4);
  st = await G(() => { const g = window.__gymTapes; return { next: (g.S.tracks.find(t => t.id === g.P.order[g.P.pos + 1]) || {}).title, toast: document.getElementById('toast').textContent, cur: document.getElementById('pTitle').textContent }; });
  ok('swiping a row right lines it up next, without playing it', st.next === 'opus-clip' && /Plays next/.test(st.toast) && st.cur === 'blue-scene', st);
  r = await rowBox('#trackList .row:has-text("all-black")');
  await touch('touchStart', r.x, r.y); for (let i = 1; i <= 6; i++) { await touch('touchMove', r.x - 20 * i, r.y + 1); await sleep(16); }
  await page.screenshot({ path: DIR + '/shots/a5-swipe.png' }); const under = await G(() => { const u = document.querySelector('.swipe-under'); return u && { text: u.textContent, cls: u.className }; });
  await touch('touchEnd'); await sleep(400);
  st = await G(() => ({ rows: Array.from(document.querySelectorAll('#trackList .row .title')).map(e => e.textContent), toast: document.getElementById('toast').textContent, inDb: Object.values(JSON.parse(localStorage.getItem('fakeDb')).tracks).some(t => t.title === 'all-black') }));
  ok('swiping a row left deletes it, with Undo', under && under.text === 'Delete' && /del/.test(under.cls) && st.rows.indexOf('all-black') < 0 && /deleted/.test(st.toast) && /Undo/.test(st.toast) && st.inDb, { under, st });
  await page.click('#toast [data-act="toast-act"]'); await sleep(400);
  ok('Undo brings the swiped one back', (await titles('#trackList .row .title')).indexOf('all-black') >= 0);
  const p0 = await G(() => window.__gymTapes.P.cur);
  r = await rowBox('#trackList .row:has-text("Leg-day-beeps")'); await swipe(r.x, r.y, r.x - 40, r.y, 4);
  ok('a short swipe springs back and does nothing', (await titles('#trackList .row .title')).indexOf('Leg-day-beeps') >= 0 && (await G(() => !document.querySelector('.swipe-under') && !document.querySelector('.row.swiping'))));
  r = await rowBox('#trackList .row:has-text("Leg-day-beeps")'); await swipe(r.x, r.y, r.x + 30, r.y + 140, 8);
  ok('a mostly up-and-down drag is left to scrolling', (await titles('#trackList .row .title')).indexOf('Leg-day-beeps') >= 0 && (await G(() => window.__gymTapes.P.cur)) === p0);
  await page.click('[data-act="lib"][data-lib="playlists"]'); await page.click('.grid .pl-row:has-text("Four")'); await sleep(300);
  r = await rowBox('#plList .row:has-text("opus-clip")'); await swipe(r.x, r.y, r.x - 200, r.y + 2);
  st = { toast: await page.textContent('#toast'), rows: await titles('#plList .row .title'), still: (await G(() => window.__gymTapes.S.tracks.length)) };
  ok('in a playlist, swiping left only takes it out of the playlist', /Removed from Four/.test(st.toast) && st.rows.length === 3 && st.still === 4, st);
  await page.click('#toast [data-act="toast-act"]'); await sleep(500);
  ok('and Undo puts it back in its place', (await titles('#plList .row .title')).length === 4 && (await db()).playlists[(await G(() => window.__gymTapes.S.playlists.find(p => p.name === 'Four').id))].tracks.length === 4);
  await page.click('.now-open'); await sleep(450);
  const up0 = await titles('#fQueue .row .title');
  r = await rowBox('#fQueue .row >> nth=0'); await swipe(r.x, r.y, r.x - 200, r.y + 2);
  ok('in Up next, swiping left takes it out of the queue', (await titles('#fQueue .row .title')).join() === up0.slice(1).join(), { up0, now: await titles('#fQueue .row .title') });
  await G(() => { document.getElementById('full').scrollTop = 0; }); await sleep(100);
  const cb = await page.locator('#fCover').boundingBox();
  await swipe(cb.x + cb.width / 2, cb.y + 40, cb.x + cb.width / 2, cb.y + 300, 10); await sleep(200);
  ok('pulling the big player down closes it', !(await page.isVisible('#full')) && (await G(() => !window.__gymTapes.S.full)));

  // ---------- join ----------
  await page.click('#tabLibrary'); await page.click('#libUploads'); await page.click('#trackList .row:has-text("Leg-day-beeps") .more');
  ok('Join is hidden until it is switched on', !(await page.isVisible('[data-act="m-join"]'))); await page.click('[data-act="sheet-close"]'); await sleep(250);
  await page.click('#tabSettings'); await page.click('#sw-join'); await sleep(150);
  await page.click('#tabLibrary'); await page.click('#libUploads'); await page.click('#trackList .row:has-text("Leg-day-beeps") .more'); await page.click('[data-act="m-join"]'); await sleep(300);
  await page.click('#sheetPanel .opt:has-text("all-black")'); await sleep(150);
  st = { tick: await page.textContent('#sheetPanel .opt:has-text("all-black") .tick'), btn: await page.textContent('[data-act="join-go"]') };
  ok('the join sheet numbers the picks in play order', st.tick === '2' && st.btn === 'Join 2', st);
  await page.screenshot({ path: DIR + '/shots/a6-join.png' });
  const n0 = await G(() => window.__gymTapes.S.tracks.length);
  await page.click('[data-act="join-go"]');
  await page.waitForFunction(n => window.__gymTapes.S.tracks.length === n + 1, n0, { timeout: 30000 }); await sleep(300);
  let j = await G(() => window.__gymTapes.S.tracks.find(t => t.title === 'Leg-day-beeps + all-black'));
  let pr = j && probe(blobs.get(j.asset));
  ok('two uploads in the same format are joined as they are: one upload, both lengths, decodes cleanly', !!j && Math.abs(j.dur - 38) < 0.1 && pr.streams[0].codec_name === 'opus' && Math.abs(+pr.format.duration - 38) < 0.1 && !pr.errs, { dur: j && j.dur, probe: pr && pr.format, errs: pr && pr.errs });
  ok('the originals are untouched', (await G(() => ['Leg-day-beeps', 'all-black'].every(n => window.__gymTapes.S.tracks.some(t => t.title === n)))) && (await G(() => window.__gymTapes.S.tracks.length)) === n0 + 1);
  await page.click('#trackList .row:has-text("Leg-day-beeps + all-black") .row-hit'); await sleep(700);
  st = await A(); ok('the joined upload plays', st.cur === 'Leg-day-beeps + all-black' && !st.paused && st.t > 0.2, st);
  await page.click('#trackList .row:has-text("Leg-day-beeps") >> nth=-1 >> .more').catch(() => {});
  await page.click('[data-act="sheet-close"]').catch(() => {}); await sleep(250);
  const beepsRow = '#trackList .row:has(.title:text-is("Leg-day-beeps"))';
  await page.click(beepsRow + ' .more'); await page.click('[data-act="m-join"]'); await sleep(300); await page.click('#sheetPanel .opt:has-text("blue-scene")'); await page.click('[data-act="join-go"]');
  await page.waitForFunction(n => window.__gymTapes.S.tracks.length === n + 2, n0, { timeout: 60000 }); await sleep(300);
  j = await G(() => window.__gymTapes.S.tracks.find(t => t.title === 'Leg-day-beeps + blue-scene'));
  pr = j && probe(blobs.get(j.asset));
  const blue = await G(() => window.__gymTapes.S.tracks.find(t => t.title === 'blue-scene'));
  ok('mono and stereo uploads are joined by re-encoding, and the result decodes cleanly', !!j && Math.abs(j.dur - (24 + blue.dur)) < 0.3 && pr.streams[0].channels === 2 && !pr.errs, { dur: j && j.dur, want: 24 + blue.dur, probe: pr && pr.streams, errs: pr && pr.errs });
  ok('the joined upload gets its own copy of a cover', !!j.cover && j.cover !== blue.cover && blobs.has(j.cover) && types.get(j.cover) === 'image/jpeg');

  // ---------- review fixes ----------
  // a playlist Undo only puts back the swiped one
  await page.click('[data-act="lib"][data-lib="playlists"]').catch(() => {}); await page.click('#tabLibrary'); await page.click('[data-act="lib"][data-lib="playlists"]'); await page.click('.grid .pl-row:has-text("Four")'); await sleep(300);
  r = await rowBox('#plList .row:has-text("all-black")'); await swipe(r.x, r.y, r.x - 200, r.y + 2); await sleep(200);
  await page.click('[data-act="pl-add"]'); await page.click('#sheetPanel .opt:has(.grow:text-is("blue-scene"))'); await sleep(300); await page.click('[data-act="sheet-close"]'); await sleep(300);
  await page.click('#toast [data-act="toast-act"]').catch(() => {}); await sleep(600);
  st = await titles('#plList .row .title');
  ok('Undo after a playlist swipe puts back only that one, other changes stay', st.indexOf('all-black') >= 0 && st.indexOf('blue-scene') < 0 && st.length === 3, st);
  // changing Loop during the count-in does not trap it
  await page.click('#tabSettings'); await page.click('[data-k="delay"][data-v="3"]'); await sleep(150);
  await page.click('#tabLibrary'); await page.click('#libUploads'); await sleep(200);
  if (!(await G(() => window.__gymTapes.audio.paused))) { await page.click('.ctl [data-act="toggle"]'); await sleep(200); }
  await page.click('#trackList .row:has(.title:text-is("opus-clip")) .row-hit'); await sleep(300);
  await page.click('#loopBtn'); await page.click('#loopBtn'); await sleep(100);
  ok('Loop can be changed during the count-in', (await G(() => window.__gymTapes.S.loop)) === 'one' && (await G(() => !!window.__gymTapes.P.countIn)));
  await page.waitForFunction(() => !window.__gymTapes.P.countIn, null, { timeout: 6000 }).catch(() => {}); await sleep(500);
  st = await A(); ok('and the upload still starts after it', !st.count && st.cur === 'opus-clip' && !st.paused && (await G(() => window.__gymTapes.audio.loop)) === true, st);
  await page.click('#loopBtn'); await sleep(100);
  // a resumed session does not count the same listen twice, and its count-in runs in full
  await seekFrac(0.6); await sleep(700); await page.click('.ctl [data-act="toggle"]'); await sleep(300);
  const plays0 = await G(() => { const g = window.__gymTapes; return g.S.plays[g.P.cur]; });
  await page.reload({ waitUntil: 'domcontentloaded' });
  await G(() => window.dispatchEvent(new Event('pagehide')));          // leaving the app while it is still loading
  await ready(); await sleep(500);
  st = await G(() => ({ sess: !!localStorage.getItem('gymtapes.session'), stats: ((JSON.parse(localStorage.getItem('fakeDb')).settings || {}).stats || {}).total, plays: ((JSON.parse(localStorage.getItem('fakeDb')).settings || {}).recent || {}).plays }));
  ok('leaving while the app is still loading wipes nothing', st.sess && st.stats >= 3000 && st.plays && Object.keys(st.plays).length >= 2, st);
  await page.click('.ctl [data-act="toggle"]'); await sleep(1500);
  const mid2 = await G(() => !!window.__gymTapes.P.countIn);
  await page.waitForFunction(() => !window.__gymTapes.P.countIn, null, { timeout: 6000 }).catch(() => {}); await sleep(900);
  st = await G(() => { const g = window.__gymTapes; return { plays: g.S.plays[g.P.cur], t: g.audio.currentTime, d: g.audio.duration, paused: g.audio.paused }; });
  ok('the count-in after a reload runs in full, then it resumes at the saved spot', mid2 && !st.paused && Math.abs(st.t - st.d * 0.6) < 2, st);
  ok('the resumed listen is not counted a second time', st.plays === plays0, { before: plays0, after: st.plays });
  await page.click('.ctl [data-act="toggle"]'); await page.click('#tabSettings'); await page.click('[data-k="delay"][data-v="0"]'); await sleep(150);

  ok('no page errors', errors.length === 0, errors);
  await ctx.close();

  // ---------- a phone browser that will not let a page set the volume: the bar stays hidden ----------
  const c2 = await browser.newContext({ viewport: { width: 390, height: 844 }, hasTouch: true });
  await c2.addInitScript(() => { const d = Object.getOwnPropertyDescriptor(HTMLMediaElement.prototype, 'volume'); Object.defineProperty(HTMLMediaElement.prototype, 'volume', { get() { return 1; }, set() { /* ignored, like an iPhone */ }, configurable: true }); });
  const p2 = await c2.newPage(); await p2.goto('http://localhost:8774/'); await p2.waitForFunction(() => window.__gymTapes && window.__gymTapes.S.ready);
  await p2.setInputFiles('#fileInput', DIR + '/media/Leg-day-beeps.mp4'); await p2.waitForFunction(() => window.__gymTapes.S.tracks.length === 1, null, { timeout: 30000 });
  await p2.click('#tabLibrary'); await p2.click('#trackList .row .row-hit'); await sleep(400);
  ok('where a page cannot set the volume, the bar still shows and drives the sound processing instead', (await p2.evaluate(() => document.querySelectorAll('.vol:not([hidden])').length)) === 2 && (await p2.isVisible('#player .js-vol')));
  await c2.close();

  console.log(`\n${pass} passed, ${fail} failed`);
  await browser.close(); server.close();
})().catch(e => { console.error('TEST FAILED', e); process.exit(1); });
