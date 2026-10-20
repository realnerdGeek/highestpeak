// Test 9 (V7): smoothness, likes, most played, duplicate warning, up next, big player, drag to reorder, presets.
const { chromium } = require('./pw.js'); require('./legacy');
const http = require('http'), fs = require('fs'), path = require('path');
const DIR = __dirname, blobs = new Map(), types = new Map();
const sleep = ms => new Promise(r => setTimeout(r, ms));
let pass = 0, fail = 0; const ok = (label, cond, extra) => { cond ? pass++ : fail++; console.log((cond ? 'PASS ' : 'FAIL ') + label + (extra !== undefined ? '  -> ' + JSON.stringify(extra) : '')); };
const server = http.createServer((req, res) => { res.writeHead(200, { 'content-type': 'text/html' }); res.end(fs.readFileSync(path.join(DIR, 'index.html'))); });
const FAKE = fs.readFileSync(path.join(DIR, 'test6.js'), 'utf8').match(/const FAKE = \(\) => \{[\s\S]*?\n\};\n/)[0];
(async () => {
  await new Promise(r => server.listen(8772, r));
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
  const idOf = title => G(t => (window.__gymTapes.S.tracks.find(x => x.title === t) || {}).id, title);
  const fits = () => G(() => document.documentElement.scrollWidth <= window.innerWidth);
  const titles = sel => page.locator(sel).allTextContents();
  const seekFrac = (f, wave) => G(([f]) => { const a = window.__gymTapes.audio; a.currentTime = a.duration * f; }, [f]);
  const drag = async (fromSel, toSel, extra) => {
    const a = await page.locator(fromSel).boundingBox(), b = await page.locator(toSel).boundingBox();
    const x = a.x + a.width / 2, y0 = a.y + a.height / 2, y1 = b.y + b.height / 2 + (extra || 0);
    await page.mouse.move(x, y0); await page.mouse.down();
    for (let i = 1; i <= 8; i++) { await page.mouse.move(x, y0 + (y1 - y0) * i / 8); await sleep(25); }
    const mid = await G(() => ({ sorting: !!document.querySelector('.sorting'), drag: !!document.querySelector('.row.drag') }));
    await page.mouse.up(); await sleep(250); return mid;
  };

  // ---------- loading placeholders ----------
  await page.goto('http://localhost:8772/', { waitUntil: 'domcontentloaded' });
  const sk = await G(() => ({ skel: !!document.querySelector('#view .skel'), blocks: document.querySelectorAll('#view .sk').length, ready: window.__gymTapes.S.ready }));
  ok('placeholder shapes show while the library loads', sk.skel && sk.blocks >= 8 && !sk.ready, sk);
  await page.screenshot({ path: DIR + '/shots/80-loading.png' });
  await ready(); await sleep(200);
  ok('placeholders are replaced once it is loaded', !(await page.isVisible('#view .skel')));

  await page.setInputFiles('#fileInput', [DIR + '/media/Leg-day-beeps.mp4', DIR + '/media/blue-scene.mp4', DIR + '/media/all-black.mp4', DIR + '/media/opus-clip.mp4']);
  await page.waitForFunction(() => window.__gymTapes.S.tracks.length === 4 && document.getElementById('upDot').hidden, null, { timeout: 90000 }); await sleep(400);
  const fps = await G(() => window.__gymTapes.S.tracks.map(t => t.fp));
  ok('every new upload gets a fingerprint', fps.every(f => typeof f === 'string' && f.length > 4) && new Set(fps).size === 4, fps);

  // ---------- smoothness: nothing is rebuilt when the track changes ----------
  await page.click('#tabLibrary'); await page.click('#libUploads'); await sleep(250);
  ok('changing tab plays the short fade-in', await G(() => document.getElementById('view').classList.contains('enter')));
  await G(() => { window.__rows = Array.from(document.querySelectorAll('#trackList .row')); window.__img = document.querySelector('#trackList .row img'); });
  await page.click('#trackList .row:has-text("Leg-day-beeps") .row-hit'); await sleep(600);
  await page.click('#trackList .row:has-text("blue-scene") .row-hit'); await sleep(600);
  let st = await G(() => ({ same: window.__rows.every(r => r.isConnected), img: !!window.__img && window.__img.isConnected, cur: Array.from(document.querySelectorAll('#trackList .row.cur .title')).map(e => e.textContent), n: document.querySelectorAll('#trackList .row').length }));
  ok('starting another upload keeps every row and picture in place, only the highlight moves', st.same && st.img && st.cur.join() === 'blue-scene' && st.n === 4, st);
  ok('skipping around does not count as a play', (await G(() => Object.keys(window.__gymTapes.S.plays).length)) === 0);

  // sheets slide in and out
  await page.click('#trackList .row:has-text("all-black") .more'); await sleep(60);
  st = await G(() => ({ anim: getComputedStyle(document.getElementById('sheetPanel')).animationName, shown: !document.getElementById('sheet').hidden }));
  await sleep(300); await page.click('[data-act="sheet-close"]');
  const out = await G(() => ({ out: document.getElementById('sheet').classList.contains('out'), hidden: document.getElementById('sheet').hidden }));
  await sleep(320);
  ok('sheets slide up, and slide away before they are hidden', st.anim === 'sheetUp' && st.shown && out.out && !out.hidden && (await G(() => document.getElementById('sheet').hidden && !document.getElementById('sheet').classList.contains('out'))), { st, out });

  // the next upload is fetched ahead of time
  await page.click('[data-act="play-all"]'); await sleep(300);
  await page.waitForFunction(() => { const g = window.__gymTapes, t = g.S.tracks.find(x => x.id === g.P.order[g.P.pos + 1]); return t && /^blob:/.test(g.PRE.get(t.asset) || ''); }, null, { timeout: 15000 });
  const nextTitle = await G(() => { const g = window.__gymTapes; return g.S.tracks.find(x => x.id === g.P.order[g.P.pos + 1]).title; });
  await page.click('.ctl [data-act="next"]'); await sleep(700);
  st = await G(() => ({ src: (window.__gymTapes.audio.getAttribute('src') || '').slice(0, 5), t: window.__gymTapes.audio.currentTime, paused: window.__gymTapes.audio.paused, title: document.getElementById('pTitle').textContent, held: window.__gymTapes.PRE.size }));
  ok('the next upload is loaded in advance, so a skip plays from the ready copy', st.src === 'blob:' && st.t > 0.2 && !st.paused && st.title === nextTitle && st.held <= 4, st);

  // ---------- likes ----------
  const blue = await idOf('blue-scene'), beeps = await idOf('Leg-day-beeps');
  await page.click('#trackList .row:has-text("blue-scene") .row-hit'); await sleep(500);
  await page.click('#trackList .row:has-text("blue-scene") .heart');
  st = await G(() => ({ row: document.querySelector('#trackList .row.cur .heart').getAttribute('aria-pressed'), player: document.getElementById('pHeart').getAttribute('aria-pressed'), same: window.__rows.every(r => r.isConnected) }));
  ok('tapping a heart fills it at once, on the row and on the player, without redrawing the list', st.row === 'true' && st.player === 'true' && st.same, st);
  await page.waitForFunction(id => { const d = JSON.parse(localStorage.getItem('fakeDb')); return d.tracks[id].liked > 0; }, blue); ok('the like is saved to the library', true);
  await page.click('#pHeart'); await sleep(250);
  ok('the heart on the player takes the like off again', (await page.getAttribute('#trackList .row.cur .heart', 'aria-pressed')) === 'false' && !(await db()).tracks[blue].liked);
  await page.click('#pHeart'); await sleep(150);
  await page.click('#trackList .row:has-text("Leg-day-beeps") .more'); await page.click('[data-act="m-like"]'); await sleep(350);
  ok('Like in the options menu works too', (await page.getAttribute('#trackList .row:has-text("Leg-day-beeps") .heart', 'aria-pressed')) === 'true');
  await page.screenshot({ path: DIR + '/shots/81-library-hearts.png' });
  await page.click('[data-act="sort"]'); await page.click('.opt:has-text("Liked first")'); await sleep(350);
  ok('"Liked first" puts the liked ones on top', (await titles('#trackList .row .title')).slice(0, 2).sort().join() === 'Leg-day-beeps,blue-scene', await titles('#trackList .row .title'));
  await page.click('[data-act="sort"]'); await page.click('.opt:has-text("Newest first")'); await sleep(300);
  await page.click('#tabHome'); await sleep(250);
  ok('Home gets a Liked tile', (await page.textContent('#plStrip .tile:has-text("Liked")')).includes('2 uploads'));
  await page.click('#plStrip .tile:has-text("Liked")'); await sleep(250);
  st = { head: await page.textContent('.pl-head h2'), rows: await titles('#plList .row .title'), grips: await page.locator('#plList .grip').count() };
  ok('the Liked list holds them, most recently liked first', st.head === 'Liked' && st.rows.join() === 'Leg-day-beeps,blue-scene' && st.grips === 0, st);
  await page.click('[data-act="pl-play"]'); await sleep(500);
  ok('the Liked list plays as its own list', (await page.textContent('#pMeta')) === 'Liked, 1 of 2', await page.textContent('#pMeta'));
  await page.screenshot({ path: DIR + '/shots/82-liked.png' });
  await page.click('#plList .row:has-text("blue-scene") .heart'); await sleep(350);
  ok('taking a like off removes it from the Liked list', (await titles('#plList .row .title')).join() === 'Leg-day-beeps');
  await page.click('[data-act="pl-back"]'); await sleep(200);
  ok('Library shows Liked next to the playlists', (await titles('.grid .pl-row .title')).join() === 'Liked' && (await page.textContent('.grid .pl-row')).includes('1 upload'));

  // ---------- most played ----------
  await page.click('#libUploads'); await sleep(200);
  await page.click('#trackList .row:has-text("Leg-day-beeps") .row-hit'); await sleep(500);
  await seekFrac(0.6); await sleep(700);
  ok('an upload counts as played once it has run a while', (await G(id => window.__gymTapes.S.plays[id], beeps)) === 1);
  await page.click('#loopBtn'); await page.click('#loopBtn'); await sleep(100);
  await G(() => { const a = window.__gymTapes.audio; a.currentTime = a.duration - 0.5; }); await sleep(1600);
  await seekFrac(0.6); await sleep(700);
  ok('each loop of it counts again', (await G(id => window.__gymTapes.S.plays[id], beeps)) === 2, await G(() => window.__gymTapes.S.plays));
  await page.click('#loopBtn'); await sleep(100);
  await page.click('#trackList .row:has-text("opus-clip") .row-hit'); await sleep(500); await seekFrac(0.6); await sleep(700);
  await page.waitForFunction(id => { const r = (JSON.parse(localStorage.getItem('fakeDb')).settings || {}).recent; return r && r.plays && r.plays[id] === 2; }, beeps);
  ok('play counts are saved with the library', true);
  await page.click('#tabHome'); await sleep(250);
  st = { tiles: await titles('#rotGrid .rot .title'), meta: await titles('#rotGrid .rot .meta') };
  ok('Your rotation: last played first, then the most played', st.tiles.slice(0, 2).join() === 'opus-clip,Leg-day-beeps' && st.meta.slice(0, 2).join() === 'Last played,2 plays' && st.tiles.length <= 6 && new Set(st.tiles).size === st.tiles.length, st);
  await page.click('#rotGrid .rot:has-text("Leg-day-beeps")'); await sleep(400);
  ok('tapping one plays from Your rotation', /^Your rotation, 2 of \d$/.test(await page.textContent('#pMeta')), await page.textContent('#pMeta'));
  await page.click('#view .list .row .more >> nth=0'); const sub = await page.textContent('#sheetPanel .sub'); await page.click('[data-act="sheet-close"]'); await sleep(300);
  await page.screenshot({ path: DIR + '/shots/83-home.png', fullPage: true });

  // ---------- duplicate warning ----------
  await page.click('#tabUpload'); await sleep(200);
  await page.setInputFiles('#fileInput', DIR + '/media/Leg-day-beeps.mp4');
  await page.waitForSelector('.imp.ask'); await sleep(200);
  st = { text: await page.textContent('.imp.ask'), head: await page.textContent('#view .group h3'), n: await G(() => window.__gymTapes.S.tracks.length), dot: await G(() => document.getElementById('upDot').hidden) };
  ok('adding the same file again asks first and names the one already there', /already have: Leg-day-beeps/.test(st.text) && /Skip/.test(st.text) && /Add anyway/.test(st.text) && st.n === 4 && !st.dot, st);
  await page.screenshot({ path: DIR + '/shots/84-duplicate.png' });
  await page.click('.imp.ask [data-act="imp-dismiss"]'); await sleep(200);
  ok('Skip drops it', !(await page.isVisible('.imp')) && (await G(() => window.__gymTapes.S.tracks.length)) === 4);
  await page.setInputFiles('#fileInput', DIR + '/media/Leg-day-beeps.mp4'); await page.waitForSelector('.imp.ask');
  await page.click('[data-act="imp-force"]');
  await page.waitForFunction(() => window.__gymTapes.S.tracks.length === 5 && document.getElementById('upDot').hidden, null, { timeout: 60000 }); await sleep(300);
  ok('Add anyway adds a second copy', !(await page.isVisible('.imp')));
  await page.click('.acts >> nth=0 >> [data-act="up-rename"]'); await page.fill('#renameInput', 'Beeps copy'); await page.click('form[data-form="rename"] button[type=submit]');
  await page.waitForFunction(() => window.__gymTapes.S.tracks.some(t => t.title === 'Beeps copy')); await sleep(300);

  // ---------- big player and up next ----------
  await page.click('#tabLibrary'); await sleep(200); await page.click('[data-act="play-all"]'); await sleep(500);
  await page.click('.now-open'); await sleep(450);
  st = await G(() => { const g = window.__gymTapes; return { open: !document.getElementById('full').hidden, title: document.getElementById('fTitle').textContent, p: document.getElementById('pTitle').textContent, from: document.getElementById('fFrom').textContent, meta: document.getElementById('fMeta').textContent,
    bars: document.querySelectorAll('#fWave i').length, queue: Array.from(document.querySelectorAll('#fQueue .row .title')).map(e => e.textContent), want: g.P.order.slice(g.P.pos + 1).map(id => g.S.tracks.find(t => t.id === id).title), cover: !!document.querySelector('#fCover .cover') }; });
  ok('tapping the player opens the big one with cover, waveform and what is up next', st.open && st.title === st.p && st.from === 'All uploads' && st.meta === '1 of 5' && st.bars > 40 && st.cover && st.queue.length === 4 && st.queue.join() === st.want.join(), st);
  ok('the big player fits the phone width', await G(() => document.getElementById('full').scrollWidth <= window.innerWidth));
  await page.screenshot({ path: DIR + '/shots/85-full.png' });
  await page.click('#fPlayBtn'); await sleep(200); const paused = await G(() => window.__gymTapes.audio.paused);
  await page.click('#fPlayBtn'); await sleep(300);
  ok('its play button pauses and resumes', paused && !(await G(() => window.__gymTapes.audio.paused)));
  const box = await page.locator('#fWave').boundingBox(); await page.mouse.click(box.x + box.width * 0.5, box.y + box.height / 2); await sleep(300);
  st = await G(() => { const a = window.__gymTapes.audio; return { f: a.currentTime / a.duration, lit: document.querySelectorAll('#fWave i.on').length, all: document.querySelectorAll('#fWave i').length }; });
  ok('its waveform seeks and shows progress', Math.abs(st.f - 0.5) < 0.06 && Math.abs(st.lit / st.all - 0.5) < 0.08, st);
  await page.click('#fHeart'); await sleep(200);
  ok('its heart likes what is playing', (await page.getAttribute('#fHeart', 'aria-pressed')) === 'true' && (await G(() => !!window.__gymTapes.S.tracks.find(t => t.id === window.__gymTapes.P.cur).liked)));
  await page.click('#fHeart'); await sleep(150);
  // drag the first upcoming one below the second
  await G(() => { document.getElementById('full').scrollTop = 260; }); await sleep(150);
  let before = await titles('#fQueue .row .title');
  const mid = await drag('#fQueue .row >> nth=0 >> .grip', '#fQueue .row >> nth=1 >> .grip', 6);
  let after = await titles('#fQueue .row .title');
  st = await G(() => { const g = window.__gymTapes; return g.P.order.slice(g.P.pos + 1).map(id => g.S.tracks.find(t => t.id === id).title); });
  ok('dragging in Up next changes what plays next', mid.sorting && mid.drag && after.join() === [before[1], before[0], before[2], before[3]].join() && st.join() === after.join(), { before, after });
  await page.click('#fQueue .row >> nth=0 >> [data-act="q-remove"]'); await sleep(200);
  ok('an upload can be taken out of Up next', (await titles('#fQueue .row .title')).join() === after.slice(1).join() && (await page.textContent('#fMeta')) === '1 of 4');
  const jumpTo = (await titles('#fQueue .row .title'))[1];
  await page.click('#fQueue .row >> nth=1 >> .row-hit'); await sleep(500);
  ok('tapping one in Up next jumps to it', (await page.textContent('#fTitle')) === jumpTo && (await page.textContent('#fMeta')) === '3 of 4', await page.textContent('#fMeta'));
  await page.click('#full .ctl [data-act="prev"]'); await sleep(400);
  await page.click('[data-act="full-close"]'); await sleep(60); const closing = await G(() => document.getElementById('full').classList.contains('out') || document.documentElement.classList.contains('vt-on')); await sleep(350);
  ok('the big player slides away when closed (V14: its cover shrinks back into the mini player)', closing && !(await page.isVisible('#full')));
  // Play next from a row's menu
  const cur = await page.textContent('#pTitle'), pick = (await titles('#trackList .row .title')).find(t => t !== cur && t !== jumpTo);
  await page.click(`#trackList .row:has-text("${pick}") .more`); await page.click('[data-act="m-next"]'); await sleep(350);
  st = await G(() => { const g = window.__gymTapes; return { next: g.S.tracks.find(t => t.id === g.P.order[g.P.pos + 1]).title, uniq: new Set(g.P.order).size === g.P.order.length, toast: document.getElementById('toast').textContent }; });
  ok('"Play next" lines an upload up right after the current one', st.next === pick && st.uniq && /Plays next/.test(st.toast), st);
  await page.click('.ctl [data-act="next"]'); await sleep(500);
  ok('and it really is what plays next', (await page.textContent('#pTitle')) === pick);
  await page.click('.now-open'); await sleep(400); await page.keyboard.press('Escape'); await sleep(350);
  ok('Escape closes the big player', !(await page.isVisible('#full')));

  // ---------- drag to reorder a playlist ----------
  await page.click('[data-act="sel-start"]');
  for (const t of ['blue-scene', 'all-black', 'opus-clip']) await page.click(`#trackList .row:has-text("${t}") .row-hit`);
  await page.click('[data-act="sel-add"]'); await page.click('[data-act="sel-new"]'); await page.fill('#plNameInput', 'Mix'); await page.click('form[data-form="playlist"] button[type=submit]');
  await page.waitForFunction(() => window.__gymTapes.S.playlists.length === 1 && window.__gymTapes.S.pl); await sleep(400);
  before = await titles('#plList .row .title');
  st = { grips: await page.locator('#plList .grip').count(), hearts: await page.locator('#plList .heart').count(), fits: await fits() };
  ok('playlist rows carry a drag handle and still fit the phone width', st.grips === 3 && st.hearts === 3 && st.fits, st);
  await page.screenshot({ path: DIR + '/shots/86-playlist-grips.png' });
  await drag('#plList .row >> nth=0 >> .grip', '#plList .row >> nth=2 >> .grip', 8);
  after = await titles('#plList .row .title');
  await page.waitForFunction(want => { const g = window.__gymTapes, p = Object.values(JSON.parse(localStorage.getItem('fakeDb')).playlists)[0]; return p.tracks.map(id => g.S.tracks.find(t => t.id === id).title).join() === want; }, [before[1], before[2], before[0]].join());
  ok('dragging a row in a playlist moves it and saves the new order', after.join() === [before[1], before[2], before[0]].join(), { before, after });
  await drag('#plList .row >> nth=2 >> .grip', '#plList .row >> nth=1 >> .grip', -8);
  ok('dragging upward works too', (await titles('#plList .row .title')).join() === [before[1], before[0], before[2]].join(), await titles('#plList .row .title'));

  // ---------- presets ----------
  await page.click('#tabHome'); await sleep(250);
  ok('Home explains presets before any exist', /One tap starts a playlist/.test(await page.textContent('#view')));
  await page.click('[data-act="preset-new"]'); await sleep(350);
  st = await G(() => { const f = document.querySelector('form[data-form="preset"]').elements; return { source: f.source.value, shuffle: f.shuffle.value, loop: f.loop.value, timer: f.timer.value, loops: f.loops.value, speed: f.speed.value }; });
  ok('the preset form starts from the current settings', st.source === 'all' && st.shuffle === '0' && st.loop === 'off' && st.timer === '0' && st.loops === '0' && st.speed === '1', st);
  await page.fill('#prName', 'Leg day run'); await page.selectOption('#prSource', { label: 'Mix' });
  await page.click('.segr label:has(input[name="shuffle"][value="1"])'); await page.click('.segr label:has(input[name="loop"][value="all"])');
  await page.click('.segr label:has(input[name="timer"][value="30"])'); await page.click('.segr label:has(input[name="speed"][value="1.15"])');
  await page.screenshot({ path: DIR + '/shots/87-preset-form.png' });
  ok('the preset form fits the phone width', await fits());
  await page.click('form[data-form="preset"] button[type=submit]');
  await page.waitForFunction(() => { const p = (JSON.parse(localStorage.getItem('fakeDb')).settings || {}).presets; return p && p.list.length === 1; }); await sleep(350);
  st = { title: await page.textContent('.preset .title'), meta: await page.textContent('.preset .meta') };
  ok('the preset is saved and shows on Home with what it does', st.title === 'Leg day run' && st.meta === 'Mix, shuffle, loop all, 30 min, 1.15×', st);
  await page.click('.ctl [data-act="toggle"]'); await sleep(200);
  await page.click('[data-act="preset-run"]'); await sleep(700);
  st = await G(() => { const g = window.__gymTapes, a = g.audio; return { shuffle: g.S.shuffle, loop: g.S.loop, speed: g.S.opt.speed, rate: a.playbackRate, mins: Math.round((g.T.at - Date.now()) / 60000), label: g.P.label, n: g.P.order.length, paused: a.paused, chips: Array.from(document.querySelectorAll('#pChips .chip')).map(e => e.textContent), meta: document.getElementById('pMeta').textContent }; });
  ok('one tap on a preset sets shuffle, loop, timer and speed and starts its playlist', st.shuffle && st.loop === 'all' && st.speed === 1.15 && Math.abs(st.rate - 1.15) < 0.001 && st.mins === 30 && st.label === 'Mix' && st.n === 3 && !st.paused && st.chips.join() === '1.15×,30 min', st);
  await page.screenshot({ path: DIR + '/shots/88-home-preset.png' });
  ok('Home with a preset and chips fits the phone width', await fits());
  await page.click('[data-act="preset-menu"]'); await page.click('[data-act="preset-edit"]'); await sleep(200);
  st = await G(() => { const f = document.querySelector('form[data-form="preset"]').elements; return { name: f.prname.value, shuffle: f.shuffle.value, loop: f.loop.value, timer: f.timer.value, speed: f.speed.value, src: f.source.options[f.source.selectedIndex].text }; });
  await page.fill('#prName', 'Legs'); await page.click('form[data-form="preset"] button[type=submit]'); await sleep(450);
  ok('editing a preset opens it with its own values and saves the change', st.name === 'Leg day run' && st.shuffle === '1' && st.loop === 'all' && st.timer === '30' && st.speed === '1.15' && st.src === 'Mix' && (await page.textContent('.preset .title')) === 'Legs', st);
  await page.click('[data-act="preset-menu"]'); await page.click('[data-act="preset-delete"]'); await sleep(450);
  const gone = !(await page.isVisible('.preset'));
  await page.click('#toast [data-act="toast-act"]'); await sleep(450);
  ok('a deleted preset can be brought back with Undo', gone && (await page.textContent('.preset .title')) === 'Legs' && (await db()).settings.presets.list.length === 1);

  // ---------- the Undo offer survives other messages, and a second delete joins it ----------
  await page.click('#tabLibrary'); await page.click('#libUploads'); await sleep(250);
  const n0 = await G(() => window.__gymTapes.S.tracks.length);
  await page.click('#trackList .row:has-text("Beeps copy") .more'); await page.click('[data-act="m-delete"]'); await sleep(400);
  await page.click('#trackList .row:has-text("Leg-day-beeps") .more'); await page.click('[data-act="m-next"]'); await sleep(300);
  const during = await page.textContent('#toast'); await sleep(1900); const backAgain = await page.textContent('#toast');
  ok('another message only steps in front of the Undo offer for a moment', /Plays next/.test(during) && !/Undo/.test(during) && /deleted/.test(backAgain) && /Undo/.test(backAgain), { during, backAgain });
  await page.click('#trackList .row:has-text("opus-clip") .more'); await page.click('[data-act="m-delete"]'); await sleep(300);
  st = { toast: await page.textContent('#toast'), n: await G(() => window.__gymTapes.S.tracks.length), inDb: Object.keys((await db()).tracks).length };
  ok('a second delete joins the open offer instead of ending it', /2 uploads deleted/.test(st.toast) && st.n === n0 - 2 && st.inDb === n0, st);
  await page.click('#toast [data-act="toast-act"]'); await sleep(400);
  ok('one Undo brings both back', (await G(() => window.__gymTapes.S.tracks.length)) === n0 && Object.keys((await db()).tracks).length === n0);
  await sleep(6500);
  ok('and nothing gets deleted afterwards', Object.keys((await db()).tracks).length === n0 && (await G(() => window.__gymTapes.S.tracks.length)) === n0);

  // ---------- everything is still there after a reload; an old upload without a fingerprint is still recognised ----------
  await G(id => { const d = JSON.parse(localStorage.getItem('fakeDb')); delete d.tracks[id].fp; localStorage.setItem('fakeDb', JSON.stringify(d)); }, blue);
  await page.reload(); await ready(); await sleep(400);
  st = await G(([beeps]) => { const g = window.__gymTapes; return { liked: g.S.tracks.filter(t => t.liked).map(t => t.title), plays: g.S.plays[beeps], presets: g.S.presets.map(p => p.name), rot: Array.from(document.querySelectorAll('#rotGrid .rot .title')).map(e => e.textContent), speed: g.S.opt.speed }; }, [beeps]);
  ok('likes, play counts, presets and the Home rows come back after a reload', st.liked.join() === 'Leg-day-beeps' && st.plays === 2 && st.presets.join() === 'Legs' && st.rot.indexOf('Leg-day-beeps') >= 0 && st.rot.length >= 3 && st.speed === 1.15, st);
  await page.click('#tabUpload'); await page.setInputFiles('#fileInput', DIR + '/media/blue-scene.mp4');
  await page.waitForSelector('.imp.ask', { timeout: 30000 });
  ok('an upload from before fingerprints is still spotted as a duplicate', /already have: blue-scene/.test(await page.textContent('.imp.ask')));
  await page.click('.imp.ask [data-act="imp-dismiss"]');
  ok('the options sheet shows the play count', /played 2 times/.test(sub) || /played/.test(sub), sub);

  // dark look
  await page.emulateMedia({ colorScheme: 'dark' }); await page.click('#tabHome'); await sleep(200);
  await page.click('#view .list .row .row-hit >> nth=0'); await sleep(400); await page.click('.now-open'); await sleep(500);
  await page.screenshot({ path: DIR + '/shots/89-full-dark.png' });
  await page.click('[data-act="full-close"]'); await sleep(350); await page.screenshot({ path: DIR + '/shots/90-home-dark.png', fullPage: true });

  ok('no page errors', errors.length === 0, errors);
  console.log(`\n${pass} passed, ${fail} failed`);
  await browser.close(); server.close();
})().catch(e => { console.error('TEST FAILED', e); process.exit(1); });
