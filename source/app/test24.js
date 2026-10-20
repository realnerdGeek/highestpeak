// Test 24 (V18): library + computer and Android. Tags (one upload, many at once, the Library filter, search), smart
// playlists (rules, joining on their own, no adding or dragging by hand), folders (grouped, closed folders stay closed),
// the source link (saved, opened in a new tab, bad links refused), pictures on the empty screens, rows that lift when
// dragged, a whole folder picked at once, Open with on a computer, and in the home screen version: the manifest's file
// handlers and share target, sharing a video and a link to EarWorm the way Android does it, and a backup that keeps tags,
// links, folders and smart rules.
const { chromium } = require('./pw.js');
const http = require('http'), fs = require('fs'), path = require('path');
const { execFileSync } = require('child_process');
const DIR = __dirname, OUT = DIR + '/out/', SITE = path.join(DIR, '..', 'pwa', 'site');
const sleep = ms => new Promise(r => setTimeout(r, ms));
let pass = 0, fail = 0; const ok = (label, cond, extra) => { cond ? pass++ : fail++; console.log((cond ? 'PASS ' : 'FAIL ') + label + (extra !== undefined ? '  -> ' + JSON.stringify(extra) : '')); };
const TYPES = { '.html': 'text/html', '.js': 'text/javascript', '.png': 'image/png', '.webmanifest': 'application/manifest+json' };
const server = http.createServer((req, res) => {
  let p = decodeURIComponent(req.url.split('?')[0]);
  if (p.startsWith('/highestpeak/')) {       // the home screen version, served from a sub-folder like GitHub Pages
    p = p.slice('/highestpeak/'.length) || 'index.html';
    const f = path.join(SITE, p); if (!fs.existsSync(f)) { res.writeHead(404); return res.end(); }
    res.writeHead(200, { 'content-type': TYPES[path.extname(f)] || 'application/octet-stream' }); return res.end(fs.readFileSync(f));
  }
  res.writeHead(200, { 'content-type': 'text/html' }); res.end(fs.readFileSync(path.join(DIR, 'index.html')));
});
const allErrors = [];
const ff = (expr, d, name) => { const f = OUT + name; execFileSync('ffmpeg', ['-v', 'error', '-y', '-f', 'lavfi', '-i', 'aevalsrc=' + expr + ':s=44100:d=' + d, '-c:a', 'libopus', '-b:a', '96k', '-f', 'mp4', f]); return f; };
const QUIET = () => { window.HP_STANDALONE = true; window.__HP_QUIET = true; window.__HP_RT_OFF = true; window.__HP_SETTINGS_ALL = true; try { localStorage.setItem('hp.syncAsked', '1'); localStorage.setItem('hp.guided', '1'); localStorage.setItem('hp.seenVersion', 'V18'); } catch (e) { /* blank */ } };

(async () => {
  fs.mkdirSync(OUT, { recursive: true });
  const click = bpm => { const L = (60 / bpm).toFixed(6); return '0.9*sin(2*PI*60*t)*exp(-mod(t\\,' + L + ')*30)*lt(mod(t\\,' + L + ')\\,0.15)+0.25*sin(2*PI*2000*t)*exp(-mod(t+' + (60 / bpm / 2).toFixed(6) + '\\,' + L + ')*80)'; };
  const C140 = ff(click(140), 10, 'click-140.mp4'), C100 = ff(click(100), 10, 'click-100.mp4');
  const TA = ff('0.4*sin(2*PI*262*t)', 6, 'tone-a.mp4'), TB = ff('0.4*sin(2*PI*294*t)', 6, 'tone-b.mp4'), TC = ff('0.4*sin(2*PI*330*t)', 6, 'tone-c.mp4');
  // a folder like one on a computer: two clips in a sub-folder and a note that isn't sound
  const FOLD = OUT + 'folder-test'; fs.rmSync(FOLD, { recursive: true, force: true }); fs.mkdirSync(FOLD + '/gym/more', { recursive: true });
  fs.copyFileSync(ff('0.4*sin(2*PI*392*t)', 5, 'tone-d.mp4'), FOLD + '/gym/tone-d.mp4'); fs.copyFileSync(ff('0.4*sin(2*PI*440*t)', 5, 'tone-e.mp4'), FOLD + '/gym/more/tone-e.mp4');
  fs.writeFileSync(FOLD + '/gym/notes.txt', 'not a video');
  await new Promise(r => server.listen(8792, r));
  const browser = await chromium.launch({ args: ['--autoplay-policy=no-user-gesture-required'] });
  const ctx = await browser.newContext({ viewport: { width: 440, height: 956 }, deviceScaleFactor: 2, hasTouch: true, colorScheme: 'dark' });
  await ctx.addInitScript(QUIET);
  await ctx.route('https://www.tiktok.com/**', r => r.fulfill({ status: 200, contentType: 'text/html', body: '<p>source</p>' }));
  const page = await ctx.newPage();
  const watch = p => { p.on('pageerror', e => allErrors.push('pageerror: ' + e.message)); p.on('console', m => { if (m.type() === 'error' && !/ERR_|Failed to load resource|MEDIA_ERR|PIPELINE|DEMUXER|NotSupported|CONNECTION_REFUSED/.test(m.text())) allErrors.push('console: ' + m.text()); }); };
  watch(page);
  const G = (fn, a) => page.evaluate(fn, a), until = (fn, a, ms) => page.waitForFunction(fn, a, { timeout: ms || 8000 }).then(() => true, () => false);
  const add = async (files, n) => { await page.setInputFiles('#fileInput', files); await page.waitForFunction(k => window.__gymTapes.S.tracks.length === k && document.getElementById('upDot').hidden, n, { timeout: 120000 }); await sleep(300); };
  const T = title => G(t => { const x = window.__gymTapes.S.tracks.find(y => y.title === t); return x && { id: x.id, tags: x.tags || [], link: x.link || null, bpm: x.bpm }; }, title);
  const menu = async title => { const id = (await T(title)).id; await page.click('#trackList .row[data-key="' + id + '"] [data-act="menu"]'); await sleep(350); };
  const titles = sel => G(s => [...document.querySelectorAll(s + ' .title')].map(x => x.textContent), sel);
  const toastText = () => G(() => document.getElementById('toast').textContent);
  await page.goto('http://localhost:8792/'); await page.waitForFunction(() => window.__gymTapes && window.__gymTapes.S.ready);
  ok('V18 or later', +String(await G(() => window.__gymTapes.VERSION)).replace(/^V/, '') >= 18);
  await add([C140, C100, TA, TB, TC], 5);
  await page.click('#tabLibrary'); await sleep(300);

  /* ===== tags ===== */
  await menu('click-140');
  ok('the upload menu has Tags and Add source link', await page.isVisible('[data-act="m-tags"]') && await page.isVisible('[data-act="m-link"]'));
  await page.click('[data-act="m-tags"]'); await sleep(300);
  await page.fill('#tagInput', '  #Leg   Day '); await page.click('form[data-form="tag"] button[type="submit"]'); await sleep(400);
  await page.fill('#tagInput', 'hype'); await page.press('#tagInput', 'Enter'); await sleep(400);
  let t = await T('click-140');
  ok('tags are added from the menu, tidied up (no #, one space, lower case)', t.tags.join('|') === 'leg day|hype', t.tags);
  ok('and show as chips, on for this upload', (await G(() => [...document.querySelectorAll('#tagChips .gym-chip')].map(b => b.textContent + ':' + b.getAttribute('aria-pressed')))).join() === 'hype:true,leg day:true');
  await page.click('#tagChips [data-k="hype"]'); await sleep(400);
  ok('tapping a chip takes the tag off again', (await T('click-140')).tags.join() === 'leg day');
  await page.click('#tagChips [data-k="hype"]'); await sleep(400);
  await page.click('[data-act="sheet-close"]'); await sleep(300);
  await menu('click-140');
  ok('the menu shows the tags next to Tags', /leg day, hype/.test(await page.textContent('[data-act="m-tags"]')));
  await page.click('[data-act="sheet-close"]'); await sleep(300);
  // many at once
  await page.click('#libSelect'); await sleep(250);
  for (const n of ['tone-a', 'tone-b']) { await page.click('#trackList .row[data-key="' + (await T(n)).id + '"] .row-hit'); await sleep(120); }
  await page.click('#selTag'); await sleep(300);
  ok('Select, then Tag, opens the tags for the 2 picked', /2 uploads selected/.test(await page.textContent('#sheetPanel .sub')));
  await page.click('#tagChips [data-k="leg day"]'); await sleep(500);
  ok('a tag goes on every picked upload in one tap', (await T('tone-a')).tags.join() === 'leg day' && (await T('tone-b')).tags.join() === 'leg day' && (await T('tone-c')).tags.length === 0);
  ok('and the chip is on once all of them have it', await page.getAttribute('#tagChips [data-k="leg day"]', 'aria-pressed') === 'true');
  await page.click('#tagChips [data-k="leg day"]'); await sleep(500);
  ok('tapping it again takes it off all of them', (await T('tone-a')).tags.length === 0 && (await T('tone-b')).tags.length === 0 && (await T('click-140')).tags.join('|') === 'leg day|hype', [await T('tone-a'), await T('tone-b'), await T('click-140')]);
  await page.click('#tagChips [data-k="leg day"]'); await sleep(500);
  await page.click('[data-act="sheet-close"]'); await sleep(200); await page.click('[data-act="sel-done"]'); await sleep(300);
  // the Library filter
  ok('Library has filter chips: 140+ BPM, then each tag (most used first)', (await G(() => [...document.querySelectorAll('#libFilter .gym-chip')].map(b => b.textContent))).join('|') === '140+ BPM|leg day|hype');
  await page.click('#libFilter [data-k="leg day"]'); await sleep(300);
  ok('a tag chip shows only the uploads with that tag', (await titles('#trackList')).sort().join() === 'click-140,tone-a,tone-b' && /tagged leg day/.test(await page.textContent('#trackCount')), await titles('#trackList'));
  await page.click('#bpmFilter'); await sleep(300);
  ok('a tag and 140+ BPM together', (await titles('#trackList')).join() === 'click-140');
  await page.click('#bpmFilter'); await sleep(300);
  await page.click('#view .bar [data-act="play-all"]'); await sleep(500);
  ok('Play in Library with a tag on plays just those, and says so', (await G(() => window.__gymTapes.P.order.length)) === 3 && (await G(() => window.__gymTapes.P.label)) === 'Tagged leg day', await G(() => [window.__gymTapes.P.order.length, window.__gymTapes.P.label]));
  await page.click('#tabHome'); await sleep(300); await page.click('[data-act="shuffle-all"]'); await sleep(500);
  ok('but Home\'s Shuffle everything is still everything', (await G(() => window.__gymTapes.P.order.length)) === 5);
  await G(() => { const a = window.__gymTapes.audio; if (a && !a.paused) a.pause(); });
  await page.click('#tabLibrary'); await sleep(300);
  await page.click('#libFilter [data-k="leg day"]'); await sleep(300);
  ok('tapping the chip again shows everything', (await titles('#trackList')).length === 5);
  // search finds tags
  await page.click('#tabSearch'); await sleep(250);
  ok('an empty search has a picture', await page.isVisible('#searchOut .empty .cover.ic'));
  await page.fill('#q', 'hype'); await sleep(400);
  ok('search finds uploads by tag', (await titles('#searchOut')).join() === 'click-140');
  await page.fill('#q', ''); await sleep(200);

  /* ===== a plain playlist, then a smart one ===== */
  await page.click('#tabLibrary'); await sleep(200); await page.click('#libPlaylists'); await sleep(250);
  await page.click('[data-act="pl-new"]'); await sleep(300);
  ok('a new playlist can go in a folder (with the ones already used offered)', await page.isVisible('#plFolderInput') && (await page.$('#plFolders')) !== null);
  await page.fill('#plNameInput', 'Gym'); await page.fill('#plFolderInput', '  Workouts '); await page.click('form[data-form="playlist"] button[type="submit"]'); await sleep(500);
  let gym = await G(() => window.__gymTapes.S.playlists.find(p => p.name === 'Gym'));
  ok('the folder is saved on the playlist', gym && gym.folder === 'Workouts', gym);
  ok('an empty playlist has a picture', await page.isVisible('#view .empty .cover.ic'));
  await G(async id => { const g = window.__gymTapes; await g.store.update('playlists', id, { tracks: g.S.tracks.map(t => t.id) }); }, gym.id); await sleep(300);
  // dragging lifts the row
  const grip = await page.$('#plList .row:nth-child(2) .grip'), gb = await grip.boundingBox();
  await page.mouse.move(gb.x + gb.width / 2, gb.y + gb.height / 2); await page.mouse.down(); await page.mouse.move(gb.x + gb.width / 2, gb.y + gb.height / 2 + 12, { steps: 3 }); await sleep(100);
  const lift = await G(() => { const r = document.querySelector('#plList .row.drag'); return r ? r.style.transform : ''; });
  await page.mouse.up(); await sleep(300);
  ok('a row being dragged lifts a little', /scale\(1\.02\)/.test(lift), lift);
  await page.click('[data-act="pl-back"]'); await sleep(250);
  await page.click('#smartNew'); await sleep(300);
  ok('New smart playlist starts at 140 and up when there are fast uploads, and says how many match', await page.inputValue('#smart-sbpm') === '140' && /Matches 1 upload/.test(await page.textContent('#smartCount')), await page.textContent('#smartCount'));
  await page.selectOption('#smart-stag', 'leg day'); await sleep(150);
  ok('the count follows the rules as they change', /Matches 1 upload/.test(await page.textContent('#smartCount')));
  await page.selectOption('#smart-sbpm', '0'); await sleep(150);
  ok('(leg day, any BPM: 3)', /Matches 3 uploads/.test(await page.textContent('#smartCount')));
  await page.selectOption('#smart-stag', ''); await page.selectOption('#smart-sbpm', '140'); await page.click('form[data-form="smart"] button[type="submit"]'); await sleep(500);
  let sm = await G(() => window.__gymTapes.S.playlists.find(p => p.smart));
  ok('a smart playlist is made, named after its rule, and opens', sm && sm.name === '140+ BPM' && sm.smart.bpm === 140 && (await titles('#plList')).join() === 'click-140', sm);
  ok('it says Smart and its rule, and has Rules instead of Add', /Smart/.test(await page.textContent('.pl-head .meta')) && /140\+ BPM/.test(await page.textContent('.pl-head .meta')) && await page.isVisible('.pl-actions [data-act="smart-edit"]') && !(await page.$('.pl-actions [data-act="pl-add"]')));
  ok('its rows have no drag handles', !(await page.$('#plList .grip')) && !(await page.getAttribute('#plList', 'data-sortlist')));
  await G(async () => { const g = window.__gymTapes, c = g.S.tracks.find(t => t.title === 'tone-c'); await g.store.update('tracks', c.id, { bpm: 150 }); }); await sleep(400);
  ok('an upload that starts matching joins on its own', (await titles('#plList')).sort().join() === 'click-140,tone-c', await titles('#plList'));
  await page.click('#plList .row:first-child [data-act="menu"]'); await sleep(300);
  ok('the upload menu inside a smart playlist has no Move or Remove', !(await page.$('[data-act="m-remove"]')) && !(await page.$('[data-act="m-up"]')));
  await page.click('[data-act="sheet-close"]'); await sleep(250);
  await page.click('[data-act="pl-play"]'); await sleep(600);
  ok('Play plays what the rules picked', (await G(() => window.__gymTapes.P.order.map(id => window.__gymTapes.S.tracks.find(t => t.id === id).title))).sort().join() === 'click-140,tone-c');
  await page.click('.pl-actions [data-act="smart-edit"]'); await sleep(300);
  await page.selectOption('#smart-stag', 'leg day'); await page.selectOption('#smart-sbpm', '0'); await page.selectOption('#smart-ssort', 'az'); await page.fill('#smartName', 'Leg day'); await page.click('form[data-form="smart"] button[type="submit"]'); await sleep(500);
  ok('editing the rules changes what is in it (and the order)', (await titles('#plList')).join() === 'click-140,tone-a,tone-b' && /Leg day/.test(await page.textContent('.pl-head h2')), await titles('#plList'));
  // a smart playlist can't take uploads by hand
  await page.click('[data-act="pl-back"]'); await sleep(200); await page.click('#libUploads'); await sleep(200);
  await menu('tone-c'); await page.click('[data-act="m-addpl"]'); await sleep(300);
  ok('Add to playlist only offers playlists you fill by hand', (await G(() => [...document.querySelectorAll('#sheetPanel [data-act="toggle-in"]')].map(b => b.textContent.replace(/Added$/, '')))).join() === 'Gym');
  await page.click('[data-act="sheet-close"]'); await sleep(250);

  /* ===== folders ===== */
  await page.click('#libPlaylists'); await sleep(250);
  await page.click('[data-act="pl-new"]'); await sleep(300); await page.fill('#plNameInput', 'Chill'); await page.fill('#plFolderInput', 'Moods'); await page.click('form[data-form="playlist"] button[type="submit"]'); await sleep(500);
  await page.click('[data-act="pl-back"]'); await sleep(250);
  const groups = () => G(() => ({ loose: [...document.querySelectorAll('#view > .grid .pl-row .title')].map(x => x.textContent), folders: [...document.querySelectorAll('.pl-folder')].map(f => f.querySelector('.fold-h').firstChild.textContent + ':' + [...f.querySelectorAll('.pl-row .title')].map(x => x.textContent).join('+')) }));
  let gr = await groups();
  ok('Playlists: the ones without a folder first, then each folder with its playlists', gr.loose.join() === 'Liked,Leg day' && gr.folders.join() === 'Moods:Chill,Workouts:Gym', gr);
  await page.click('.fold-h[data-k="Workouts"]'); await sleep(300);
  gr = await groups();
  ok('tapping a folder closes it', gr.folders.join() === 'Moods:Chill,Workouts:' && await page.getAttribute('.fold-h[data-k="Workouts"]', 'aria-expanded') === 'false', gr);
  await page.reload(); await page.waitForFunction(() => window.__gymTapes && window.__gymTapes.S.ready); await sleep(300);
  await page.click('#tabLibrary'); await sleep(200); await page.click('#libPlaylists'); await sleep(250);
  ok('and it stays closed on this device', (await groups()).folders.join() === 'Moods:Chill,Workouts:');
  await page.screenshot({ path: DIR + '/shots/v18-phone-playlists.png' });
  await page.click('.fold-h[data-k="Workouts"]'); await sleep(250);
  await page.click('#libUploads'); await sleep(250);

  /* ===== source link ===== */
  await menu('tone-a'); await page.click('[data-act="m-link"]'); await sleep(300);
  await page.fill('#linkInput', 'not a link'); await page.click('form[data-form="link"] button[type="submit"]'); await sleep(300);
  ok('a bad link is refused, and nothing is saved', /doesn't look like a link/.test(await toastText()) && !(await T('tone-a')).link);
  await page.fill('#linkInput', 'www.tiktok.com/@someone/video/7400000000001'); await page.click('form[data-form="link"] button[type="submit"]'); await sleep(400);
  ok('a link without https:// gets it added', (await T('tone-a')).link === 'https://www.tiktok.com/@someone/video/7400000000001', await T('tone-a'));
  await menu('tone-a');
  ok('the menu then has Open source link, with the site name', /Open source link\s*tiktok\.com/.test(await page.textContent('[data-act="m-link-open"]')));
  const [pop] = await Promise.all([ctx.waitForEvent('page', { timeout: 5000 }).catch(() => null), page.click('[data-act="m-link-open"]')]);
  ok('it opens in a new tab', !!pop && /tiktok\.com\/@someone\/video\/7400000000001/.test(pop.url()), pop && pop.url());
  if (pop) await pop.close();
  await page.click('[data-act="sheet-close"]').catch(() => {}); await sleep(200);
  await menu('tone-a'); await page.click('[data-act="m-link"]'); await sleep(300); await page.click('[data-act="link-remove"]'); await sleep(400);
  ok('Remove takes the link off', !(await T('tone-a')).link);
  await page.screenshot({ path: DIR + '/shots/v18-phone-library.png' });

  /* ===== a whole folder, Open with ===== */
  await page.setInputFiles('#folderInput', FOLD);
  await until(() => window.__gymTapes.S.tracks.length === 7 && document.getElementById('upDot').hidden, null, 60000); await sleep(300);
  ok('a picked folder adds the videos and sound inside it, sub-folders too', (await G(() => window.__gymTapes.S.tracks.map(t => t.title).filter(n => /tone-[de]/.test(n)))).sort().join() === 'tone-d,tone-e');
  const walked = await G(async () => {
    const f = n => ({ isFile: true, file: ok => ok(new File(['x'], n, { type: /\.mp4$/.test(n) ? 'video/mp4' : 'text/plain' })) });
    const dir = (kids) => ({ isDirectory: true, createReader: () => { let done = false; return { readEntries: ok => { const out = done ? [] : kids; done = true; ok(out); } }; } });
    const files = await window.__gymTapes.filesFromEntries([dir([f('a.mp4'), dir([f('b.mp4'), f('c.txt')])])]);
    return files.map(x => x.name + ':' + window.__gymTapes.isMedia(x));
  });
  ok('a dropped folder is read all the way down, and only video and sound count', walked.join() === 'a.mp4:true,b.mp4:true,c.txt:false', walked);
  const opened = await G(async () => {
    const g = window.__gymTapes, t = g.S.tracks.find(x => x.title === 'click-100'), b = await g.store.blob(t.asset);
    await g.launchFiles([{ getFile: async () => new File([b], 'click-100-again.mp4', { type: 'video/mp4' }) }]);
    const n0 = g.S.tracks.length;
    for (let i = 0; i < 150 && !g.UP.jobs.some(j => j.ask) && g.S.tracks.length === n0; i++) await new Promise(r => setTimeout(r, 100));
    return { ask: g.UP.jobs.some(j => j.ask && /click-100/.test(j.ask)), added: g.S.tracks.length === n0 + 1, tab: g.S.tab, jobs: g.UP.jobs.map(j => [j.name, j.status, j.error, j.ask]), titles: g.S.tracks.map(x => x.title) };
  });
  ok('Open with on a computer brings the file in like any upload', (opened.ask || opened.added) && opened.tab === 'upload', opened);
  await page.click('[data-act="imp-dismiss"]').catch(() => {}); await sleep(300);
  ok('no errors on the phone', !allErrors.length, allErrors.slice(0, 5));

  /* ===== computer: the folder button ===== */
  await page.setViewportSize({ width: 1440, height: 900 }); await sleep(400);
  await page.click('#tabUpload'); await sleep(300);
  ok('on a computer, Upload has Choose a folder, and says files and folders can be dropped or opened with EarWorm', await page.isVisible('#folderBtn') && /whole folder/.test(await page.textContent('.drop .works')) && /Open with/.test(await page.textContent('.drop .works')));
  await page.screenshot({ path: DIR + '/shots/v18-pc-upload.png' });
  await page.click('#tabLibrary'); await sleep(300); await page.click('#libPlaylists'); await sleep(300);
  await page.screenshot({ path: DIR + '/shots/v18-pc-playlists.png' });
  await page.setViewportSize({ width: 440, height: 956 }); await sleep(300);

  /* ===== the home screen version ===== */
  const URL0 = 'http://localhost:8792/highestpeak/';
  const man = await (await page.request.get(URL0 + 'manifest.webmanifest')).json();
  const fh = man.file_handlers && man.file_handlers[0];
  ok('the manifest lists EarWorm for video and sound files (Open with), into the open window', fh && fh.action === './' && fh.accept['video/mp4'].indexOf('.mp4') >= 0 && fh.accept['video/quicktime'].indexOf('.mov') >= 0 && fh.accept['audio/mpeg'].indexOf('.mp3') >= 0 && man.launch_handler.client_mode[0] === 'focus-existing', fh);
  const stg = man.share_target;
  ok('and as a place to share videos and sound to (Android)', stg && stg.action === './share-target' && stg.method === 'POST' && stg.enctype === 'multipart/form-data' && stg.params.files[0].name === 'media' && stg.params.files[0].accept.indexOf('video/*') >= 0, stg);
  const c2 = await browser.newContext({ viewport: { width: 412, height: 915 }, deviceScaleFactor: 2, hasTouch: true, colorScheme: 'dark', acceptDownloads: true });
  await c2.addInitScript(QUIET);
  const p2 = await c2.newPage(); watch(p2);
  const G2 = (fn, a) => p2.evaluate(fn, a), ready2 = () => p2.waitForFunction(() => window.__gymTapes && window.__gymTapes.S.ready, null, { timeout: 15000 });
  await p2.goto(URL0); await ready2();
  await p2.waitForFunction(() => navigator.serviceWorker && navigator.serviceWorker.controller || false, null, { timeout: 10000 }).catch(() => {});
  if (!(await G2(() => !!navigator.serviceWorker.controller))) { await p2.reload(); await ready2(); }
  ok('(the offline helper is running)', await G2(() => !!navigator.serviceWorker.controller));
  // Android sends a shared video as a form post to the share target; the offline helper keeps it and opens the app
  const share = async fill => {
    await G2(() => { const f = document.createElement('form'); f.id = 'shareForm'; f.method = 'POST'; f.enctype = 'multipart/form-data'; f.action = './share-target'; f.innerHTML = '<input type="file" name="media" id="shareFile" multiple><input name="text" id="shareText"><input name="title" value="Shared">'; document.body.appendChild(f); });
    await fill();
    await Promise.all([p2.waitForNavigation({ timeout: 15000 }), G2(() => document.getElementById('shareForm').submit())]);
    await ready2();
  };
  await share(() => p2.setInputFiles('#shareFile', [C140]));
  ok('after a share the app opens without ?share in the address', !/share/.test(await G2(() => location.search)));
  ok('a video shared to EarWorm becomes an upload', await p2.waitForFunction(() => window.__gymTapes.S.tracks.length === 1 && window.__gymTapes.S.tracks[0].title === 'click-140' && document.getElementById('upDot').hidden, null, { timeout: 30000 }).then(() => true, () => false));
  ok('and what was shared is cleaned up', !(await G2(() => caches.has('earworm-share'))));
  await share(() => p2.fill('#shareText', 'Check this https://www.tiktok.com/@a/video/123 lol'));
  ok('sharing a link says it has to be a saved video, not a link', await p2.waitForFunction(() => !document.getElementById('sheet').hidden && /can't download from links \(tiktok\.com\)/.test(document.getElementById('sheetPanel').textContent), null, { timeout: 8000 }).then(() => true, () => false));
  await p2.screenshot({ path: DIR + '/shots/v18-android-link.png' });
  await p2.click('[data-act="sheet-close"]'); await sleep(300);

  /* ===== a backup keeps tags, links, folders and smart rules ===== */
  await p2.setInputFiles('#fileInput', [TA]); await p2.waitForFunction(() => window.__gymTapes.S.tracks.length === 2 && document.getElementById('upDot').hidden, null, { timeout: 60000 }); await sleep(300);
  await G2(async () => {
    const g = window.__gymTapes, a = g.S.tracks.find(t => t.title === 'tone-a'), c = g.S.tracks.find(t => t.title === 'click-140');
    await g.store.update('tracks', a.id, { tags: ['warm up'], link: 'https://www.tiktok.com/@a/video/9' });
    await g.store.set('playlists', 'plsmart', { name: 'Warm up', color: 'green', tracks: [], smart: { tag: 'warm up', bpm: 0, liked: false, sort: 'new', max: 0 }, created: Date.now() });
    await g.store.set('playlists', 'plfold', { name: 'Fast', color: 'red', tracks: [c.id], folder: 'Gym', created: Date.now() + 1 });
  });
  await p2.click('#tabSettings'); await sleep(300);
  const [dl] = await Promise.all([p2.waitForEvent('download', { timeout: 30000 }), p2.click('#backupBtn').then(async () => { await sleep(400); if (await p2.isVisible('[data-act="bk-audio"]')) await p2.click('[data-act="bk-audio"]'); })]);
  const zip = OUT + 'v18-backup.zip'; await dl.saveAs(zip);
  const c3 = await browser.newContext({ viewport: { width: 412, height: 915 }, colorScheme: 'dark' });
  await c3.addInitScript(QUIET);
  const p3 = await c3.newPage(); watch(p3);
  await p3.goto('http://localhost:8792/'); await p3.waitForFunction(() => window.__gymTapes && window.__gymTapes.S.ready);
  await p3.click('#tabSettings'); await sleep(300);
  await p3.setInputFiles('#backupInput', zip);
  await p3.waitForFunction(() => /Restored/.test((document.getElementById('backupStatus') || {}).textContent || ''), null, { timeout: 30000 }).catch(() => {}); await sleep(400);
  const back = await p3.evaluate(() => { const g = window.__gymTapes, a = g.S.tracks.find(t => t.title === 'tone-a'), s = g.S.playlists.find(p => p.name === 'Warm up'), f = g.S.playlists.find(p => p.name === 'Fast');
    return { n: g.S.tracks.length, tags: a && a.tags, link: a && a.link, smart: s && s.smart, smartN: s && g.smartTracks(s.smart).length, folder: f && f.folder }; });
  ok('a backup brings back tags, source links, smart rules and folders', back.n === 2 && back.tags.join() === 'warm up' && back.link === 'https://www.tiktok.com/@a/video/9' && back.smart && back.smart.tag === 'warm up' && back.smartN === 1 && back.folder === 'Gym', back);

  ok('no errors anywhere', !allErrors.length, allErrors.slice(0, 5));
  console.log(`\n${pass} passed, ${fail} failed`);
  await browser.close(); server.close();
  process.exit(fail ? 1 : 0);
})().catch(async e => { console.error('TEST FAILED', e); process.exit(1); });
