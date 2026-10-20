// Test 10 (V7): back up the library to one file, and restore it: into the same library, after a delete, into an empty one, and from a re-zipped copy.
const { chromium } = require('./pw.js'); require('./legacy');
const http = require('http'), fs = require('fs'), path = require('path'), crypto = require('crypto');
const { execFileSync } = require('child_process');
const DIR = __dirname, OUT = path.join(DIR, 'out'), blobs = new Map(), types = new Map(), saved = [];
const sleep = ms => new Promise(r => setTimeout(r, ms));
const sha = b => crypto.createHash('sha1').update(b).digest('hex');
let pass = 0, fail = 0; const ok = (label, cond, extra) => { cond ? pass++ : fail++; console.log((cond ? 'PASS ' : 'FAIL ') + label + (extra !== undefined ? '  -> ' + JSON.stringify(extra) : '')); };
const server = http.createServer((req, res) => { res.writeHead(200, { 'content-type': 'text/html' }); res.end(fs.readFileSync(path.join(DIR, 'index.html'))); });
let FAKE = fs.readFileSync(path.join(DIR, 'test6.js'), 'utf8').match(/const FAKE = \(\) => \{[\s\S]*?\n\};\n/)[0];
const A = "if (!/\\.(mp4|webm|png|jpg|txt|json)$/.test(r.filename)) throw { code: 'rejected_extension' }; window.__saves.push({ filename: r.filename, size: r.data.size });";
if (FAKE.indexOf(A) < 0) throw new Error('fake downloads changed');
FAKE = FAKE.replace(A, "if (window.__declineNext) { window.__declineNext = false; throw { code: 'declined' }; } if (!/\\.(mp4|webm|png|jpg|txt|json|zip)$/.test(r.filename)) throw { code: 'rejected_extension' }; window.__saves.push({ filename: r.filename, size: r.data.size });" +
  " if (/\\.zip$/.test(r.filename)) { const u8 = new Uint8Array(await r.data.arrayBuffer()); let s = ''; for (let i = 0; i < u8.length; i += 32768) s += String.fromCharCode.apply(null, u8.subarray(i, i + 32768)); await window.__saveFile(r.filename, btoa(s)); }");
const pickAudio = async pg => { try { await pg.waitForSelector('[data-act="bk-audio"]', { timeout: 1500 }); await pg.click('[data-act="bk-audio"]'); } catch (e) { /* no videos: no question */ } };
const py = code => execFileSync('python3', ['-c', code], { maxBuffer: 1 << 26 }).toString();

(async () => {
  await new Promise(r => server.listen(8773, r));
  const browser = await chromium.launch({ args: ['--autoplay-policy=no-user-gesture-required'] });
  const ctx = await browser.newContext({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 2, hasTouch: true });
  await ctx.exposeFunction('__putBlob', (id, b64, type) => { blobs.set(id, Buffer.from(b64, 'base64')); types.set(id, type); });
  await ctx.exposeFunction('__delBlob', id => blobs.delete(id));
  await ctx.exposeFunction('__saveFile', (name, b64) => { const p = path.join(OUT, name); fs.writeFileSync(p, Buffer.from(b64, 'base64')); saved.push(p); });
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
  const status = () => page.textContent('#backupStatus');
  const waitStatus = re => page.waitForFunction(src => new RegExp(src).test(document.getElementById('backupStatus') ? document.getElementById('backupStatus').textContent : ''), re.source, { timeout: 60000 });
  const lib = () => G(() => { const g = window.__gymTapes; return { tracks: g.S.tracks.map(t => ({ id: t.id, title: t.title, dur: t.dur, bytes: t.bytes, asset: t.asset, cover: t.cover || null, liked: !!t.liked, fp: t.fp || null, gain: t.gain, peaks: (t.peaks || []).length, created: t.created })),
    playlists: g.S.playlists.map(p => ({ id: p.id, name: p.name, color: p.color, tracks: p.tracks, cover: p.cover || null })), presets: g.S.presets, bg: g.S.ui && g.S.ui.bg, speed: g.S.opt.speed, plays: g.S.plays, recent: g.S.recent }; });
  const wipe = async () => { await G(() => { localStorage.clear(); }); blobs.clear(); types.clear(); await page.reload(); await ready(); await sleep(300); };

  // ---------- build a library worth backing up ----------
  await page.goto('http://localhost:8773/'); await ready();
  await page.click('#tabSettings'); await sleep(200);
  ok('an empty library has nothing to back up', await page.isDisabled('#backupBtn') && !(await page.isDisabled('#restoreBtn')));
  await page.setInputFiles('#fileInput', [DIR + '/media/blue-scene.mp4', DIR + '/media/Leg-day-beeps.mp4', DIR + '/media/opus-clip.mp4']);
  await page.waitForFunction(() => window.__gymTapes.S.tracks.length === 3 && document.getElementById('upDot').hidden, null, { timeout: 90000 }); await sleep(400);
  await page.click('#tabLibrary'); await page.click('#libUploads'); await sleep(200);
  await page.click('#trackList .row:has-text("blue-scene") .heart'); await sleep(200);
  await page.click('[data-act="sel-start"]'); await page.click('#trackList .row:has-text("blue-scene") .row-hit'); await page.click('#trackList .row:has-text("opus-clip") .row-hit');
  await page.click('[data-act="sel-add"]'); await page.click('[data-act="sel-new"]'); await page.fill('#plNameInput', 'Mix');
  await page.click('[data-act="pl-pick"]'); await page.setInputFiles('#imgInput', DIR + '/media/photo.png'); await page.waitForSelector('#plPreview img'); await page.click('label:has(#plColor-green)');
  await page.click('form[data-form="playlist"] button[type=submit]');
  await page.waitForFunction(() => window.__gymTapes.S.playlists.length === 1 && window.__gymTapes.S.playlists[0].cover); await sleep(300);
  await page.click('#tabHome'); await page.click('[data-act="preset-new"]'); await sleep(300); await page.fill('#prName', 'Run'); await page.selectOption('#prSource', { label: 'Mix' });
  await page.click('.segr label:has(input[name="loop"][value="all"])'); await page.click('form[data-form="preset"] button[type=submit]');
  await page.waitForFunction(() => window.__gymTapes.S.presets.length === 1); await sleep(400);
  await page.click('#tabSettings'); await sleep(200); await page.click('[data-act="bg-skin"][data-id="violet"]'); await page.click('[data-k="speed"][data-v="1.15"]'); await sleep(300);
  await page.click('#tabLibrary'); await page.click('#libUploads'); await page.click('#trackList .row:has-text("Leg-day-beeps") .row-hit'); await sleep(500);
  await G(() => { const a = window.__gymTapes.audio; a.currentTime = a.duration * 0.6; }); await sleep(700);
  await page.click('.ctl [data-act="toggle"]'); await sleep(200);
  const L0 = await lib(), orig = new Map(L0.tracks.map(t => [t.id, sha(blobs.get(t.asset))]));
  ok('library is set up: 3 uploads, a like, a playlist with a picture, a preset, a look, a play count', L0.tracks.length === 3 && L0.tracks.filter(t => t.liked).length === 1 && L0.playlists[0].tracks.length === 2 && L0.playlists[0].cover && L0.presets.length === 1 && L0.bg.id === 'violet' && L0.speed === 1.15 && Object.values(L0.plays).join() === '1', { plays: L0.plays });

  // ---------- back up ----------
  await page.click('#tabSettings'); await sleep(200);
  await G(() => { window.__declineNext = true; }); await page.click('#backupBtn'); await pickAudio(page); await waitStatus(/not saved/);
  ok('saying no to the save is handled quietly', (await status()) === 'Backup not saved.' && saved.length === 0);
  await page.click('#backupBtn'); await pickAudio(page); await waitStatus(/Backup saved/);
  const zipPath = saved[0], stText = await status();
  ok('Back up library saves one zip file and says what is in it', saved.length === 1 && /EarWorm-backup-\d{4}-\d\d-\d\d\.zip$/.test(zipPath) && /Backup saved: 3 uploads, [\d.]+ MB\./.test(stText), { file: path.basename(zipPath || ''), status: stText });
  await page.screenshot({ path: DIR + '/shots/91-backup.png', fullPage: true });
  const info = JSON.parse(py(`
import zipfile, json, hashlib
z = zipfile.ZipFile(${JSON.stringify(zipPath)})
lib = json.loads(z.read('library.json'))
print(json.dumps({'bad': z.testzip(), 'names': z.namelist(), 'methods': sorted(set(i.compress_type for i in z.infolist())), 'app': lib['app'], 'v': lib['v'],
  'tracks': [{'id': t['id'], 'title': t['title'], 'asset': t['asset'], 'liked': bool(t.get('liked')), 'sha': hashlib.sha1(z.read('audio/' + t['asset'] + '.mp4')).hexdigest()} for t in lib['tracks']],
  'playlists': lib['playlists'], 'settings': lib['settings']}))`));
  const audioOk = info.tracks.every(t => orig.get(t.id) === t.sha);
  ok('the file is a valid zip that any unzip tool can open', info.bad === null && info.methods.join() === '0' && info.names[0] === 'library.json', { entries: info.names.length });
  ok('it holds every upload bit for bit, the covers, the playlist, the like and the settings', info.app === 'HighestPeak' && info.tracks.length === 3 && audioOk && info.tracks.filter(t => t.liked).length === 1 &&
    info.names.filter(n => /^audio\/.+\.mp4$/.test(n)).length === 3 && info.names.filter(n => /^img\/.+\.jpg$/.test(n)).length === L0.tracks.filter(t => t.cover).length + 1 &&
    info.playlists.length === 1 && info.playlists[0].name === 'Mix' && info.settings.presets.length === 1 && info.settings.bg.id === 'violet' && info.settings.opts.speed === 1.15 && Object.values(info.settings.plays).join() === '1',
    { names: info.names.map(n => n.split('/')[0]).join(' ') });

  // ---------- restore into the same library: nothing doubles up ----------
  const blobCount = blobs.size;
  await page.setInputFiles('#backupInput', zipPath); await waitStatus(/Nothing new|Restored/); await sleep(300);
  let L = await lib();
  ok('restoring over the same library skips everything already here', /^Nothing new to restore\. 3 were already here\.$/.test(await status()) && L.tracks.length === 3 && L.playlists.length === 1 && L.presets.length === 1 && blobs.size === blobCount, { status: await status() });

  // ---------- delete one for good, then restore brings just that one back ----------
  const victim = L0.tracks.find(t => t.title === 'opus-clip');
  await page.click('#tabLibrary'); await page.click('#libUploads'); await page.click('#trackList .row:has-text("opus-clip") .more'); await page.click('[data-act="m-delete"]');
  await page.waitForFunction(id => (JSON.parse(localStorage.getItem('fakeDb')).tracks[id] || {}).trashed, victim.id, { timeout: 15000 }); await sleep(300);
  await page.click('#tabSettings'); await sleep(200); await page.click('#binBtn'); await sleep(200); await page.click('[data-act="bin-purge"]'); await page.click('[data-act="bin-purge-go"]');
  await page.waitForFunction(id => !JSON.parse(localStorage.getItem('fakeDb')).tracks[id], victim.id, { timeout: 15000 }); await sleep(600);
  ok('the upload is really gone first', !blobs.has(victim.asset) && (await lib()).playlists[0].tracks.length === 1);
  await page.click('#tabSettings'); await sleep(200); await page.setInputFiles('#backupInput', zipPath); await waitStatus(/Restored 1 upload/); await sleep(500);
  L = await lib(); const back = L.tracks.find(t => t.id === victim.id);
  ok('restore puts back the missing upload, same name and audio, and returns it to its playlist', /^Restored 1 upload\. 2 were already here\.$/.test(await status()) && L.tracks.length === 3 && !!back && back.title === 'opus-clip' && back.dur === victim.dur && back.fp === victim.fp &&
    sha(blobs.get(back.asset)) === orig.get(victim.id) && L.playlists[0].tracks.join() === L0.playlists[0].tracks.join(), { status: await status(), pl: L.playlists[0].tracks, want: L0.playlists[0].tracks, back, victim: { dur: victim.dur, fp: victim.fp }, sha: back && sha(blobs.get(back.asset)) === orig.get(victim.id) });

  // ---------- an empty library gets everything, settings included ----------
  await wipe();
  ok('wiped: the library is empty', (await lib()).tracks.length === 0 && blobs.size === 0 && !(await G(() => document.documentElement.hasAttribute('data-skin'))));
  await page.click('#tabSettings'); await sleep(200); await page.setInputFiles('#backupInput', zipPath);
  await page.waitForFunction(() => /Restoring \d of 3/.test(document.getElementById('backupStatus').textContent), null, { timeout: 20000 }).catch(() => {});
  await waitStatus(/Restored 3 uploads/); await sleep(600);
  L = await lib();
  const sameTracks = L0.tracks.every(o => { const t = L.tracks.find(x => x.id === o.id); return t && t.title === o.title && t.dur === o.dur && t.bytes === o.bytes && t.liked === o.liked && t.fp === o.fp && t.gain === o.gain && t.peaks === o.peaks && t.created === o.created && sha(blobs.get(t.asset)) === orig.get(o.id) && !!t.cover === !!o.cover && (!t.cover || (blobs.has(t.cover) && types.get(t.cover) === 'image/jpeg')); });
  ok('every upload is back with its name, length, like, cover and identical audio', /^Restored 3 uploads and 1 playlist\.$/.test(await status()) && L.tracks.length === 3 && sameTracks, { status: await status() });
  const p0 = L0.playlists[0], p1 = L.playlists[0] || {};
  ok('the playlist is back with its order, color and picture', p1.id === p0.id && p1.name === 'Mix' && p1.color === 'green' && p1.tracks.join() === p0.tracks.join() && blobs.has(p1.cover));
  ok('the preset, the look, the speed and the play history are back too', L.presets.length === 1 && L.presets[0].name === 'Run' && L.presets[0].source === 'pl:' + p0.id && L.bg && L.bg.id === 'violet' && (await G(() => document.documentElement.getAttribute('data-skin'))) === 'dark' && L.speed === 1.15 &&
    JSON.stringify(L.plays) === JSON.stringify(L0.plays) && L.recent.join() === L0.recent.join(), { presets: L.presets.length, bg: L.bg, speed: L.speed, plays: L.plays });
  await page.click('#tabHome'); await sleep(300); await page.screenshot({ path: DIR + '/shots/92-restored-home.png', fullPage: true });
  await page.click('[data-act="preset-run"]'); await sleep(900);
  const a = await G(() => { const g = window.__gymTapes; return { t: g.audio.currentTime, paused: g.audio.paused, label: g.P.label, n: g.P.order.length }; });
  ok('restored uploads play, and the restored preset starts its playlist', a.t > 0.3 && !a.paused && a.label === 'Mix' && a.n === 2, a);
  await page.reload(); await ready(); await sleep(300); L = await lib();
  ok('the restored library is really saved: all there after a reload', L.tracks.length === 3 && L.playlists.length === 1 && L.presets.length === 1 && L.bg.id === 'violet');

  // ---------- a copy that was unzipped and zipped again by another tool (compressed, inside a folder) ----------
  const rezip = path.join(OUT, 'rezipped.zip');
  py(`
import zipfile
src = zipfile.ZipFile(${JSON.stringify(zipPath)}); out = zipfile.ZipFile(${JSON.stringify(rezip)}, 'w', zipfile.ZIP_DEFLATED)
for n in src.namelist(): out.writestr('My backup/' + n, src.read(n))
out.close()`);
  await wipe(); await page.click('#tabSettings'); await sleep(200); await page.setInputFiles('#backupInput', rezip); await waitStatus(/Restored 3 uploads/); await sleep(400);
  L = await lib();
  ok('a re-zipped, compressed copy restores just the same', L.tracks.length === 3 && L0.tracks.every(o => { const t = L.tracks.find(x => x.id === o.id); return t && sha(blobs.get(t.asset)) === orig.get(o.id); }) && L.playlists.length === 1);

  // ---------- wrong files ----------
  await page.setInputFiles('#backupInput', DIR + '/media/photo.png'); await waitStatus(/not an EarWorm backup/);
  const other = path.join(OUT, 'other.zip'); py(`
import zipfile
z = zipfile.ZipFile(${JSON.stringify(other)}, 'w'); z.writestr('hello.txt', 'hi'); z.close()`);
  await G(() => { document.getElementById('backupStatus').textContent = ''; });
  await page.setInputFiles('#backupInput', other); await waitStatus(/not an EarWorm backup/);
  ok('a file that is not a backup is refused and nothing changes', (await lib()).tracks.length === 3);
  // ---------- two copies of the same file kept on purpose both survive a backup and restore ----------
  await page.click('#tabUpload'); await page.setInputFiles('#fileInput', DIR + '/media/Leg-day-beeps.mp4'); await page.waitForSelector('.imp.ask'); await page.click('[data-act="imp-force"]');
  await page.waitForFunction(() => window.__gymTapes.S.tracks.length === 4 && document.getElementById('upDot').hidden, null, { timeout: 60000 }); await sleep(300);
  await page.click('#tabSettings'); await sleep(200); await G(() => { document.getElementById('backupStatus').textContent = ''; }); await page.click('#backupBtn'); await pickAudio(page); await waitStatus(/Backup saved: 4 uploads/);
  const zip2 = saved[saved.length - 1]; fs.renameSync(zip2, path.join(OUT, 'four.zip'));
  await wipe(); await page.click('#tabSettings'); await sleep(200); await page.setInputFiles('#backupInput', path.join(OUT, 'four.zip')); await waitStatus(/Restored/); await sleep(400);
  L = await lib();
  ok('a second copy that was added on purpose comes back as well', /^Restored 4 uploads and 1 playlist\.$/.test(await status()) && L.tracks.length === 4 && L.tracks.filter(t => t.title === 'Leg-day-beeps').length === 2, { status: await status() });
  await page.setInputFiles('#backupInput', path.join(OUT, 'four.zip')); await waitStatus(/Nothing new/); await sleep(300);
  ok('and restoring again still adds nothing', /4 were already here/.test(await status()) && (await lib()).tracks.length === 4, { status: await status() });
  ok('no page errors', errors.length === 0, errors);
  await ctx.close();

  // ---------- on-device mode (no saved library): the backup downloads as a file, and restores into a fresh browser ----------
  const c2 = await browser.newContext({ viewport: { width: 390, height: 844 }, acceptDownloads: true });
  const p2 = await c2.newPage(); const e2 = []; p2.on('pageerror', e => e2.push(e.message));
  await p2.goto('http://localhost:8773/'); await p2.waitForFunction(() => window.__gymTapes && window.__gymTapes.S.ready);
  await p2.setInputFiles('#fileInput', [DIR + '/media/Leg-day-beeps.mp4', DIR + '/media/all-black.mp4']);
  await p2.waitForFunction(() => window.__gymTapes.S.tracks.length === 2 && document.getElementById('upDot').hidden, null, { timeout: 60000 }); await sleep(300);
  await p2.click('#tabSettings'); await sleep(200);
  const [dl] = await Promise.all([p2.waitForEvent('download'), p2.click('#backupBtn').then(() => pickAudio(p2))]);
  const localZip = path.join(OUT, 'local-backup.zip'); await dl.saveAs(localZip);
  const names = JSON.parse(py(`
import zipfile, json
z = zipfile.ZipFile(${JSON.stringify(localZip)}); print(json.dumps([z.testzip(), len(z.namelist())]))`));
  ok('on-device mode: the backup downloads as a zip', /\.zip$/.test(dl.suggestedFilename()) && names[0] === null && names[1] >= 3, { name: dl.suggestedFilename(), entries: names[1] });
  await c2.close();
  const c3 = await browser.newContext({ viewport: { width: 390, height: 844 } }); const p3 = await c3.newPage(); p3.on('pageerror', e => e2.push(e.message));
  await p3.goto('http://localhost:8773/'); await p3.waitForFunction(() => window.__gymTapes && window.__gymTapes.S.ready);
  await p3.click('#tabSettings'); await sleep(200); await p3.setInputFiles('#backupInput', localZip);
  await p3.waitForFunction(() => /Restored 2 uploads/.test(document.getElementById('backupStatus').textContent), null, { timeout: 30000 }); await sleep(300);
  await p3.click('#tabLibrary'); await p3.click('[data-act="play-all"]'); await sleep(800);
  const a3 = await p3.evaluate(() => ({ n: window.__gymTapes.S.tracks.length, t: window.__gymTapes.audio.currentTime, paused: window.__gymTapes.audio.paused, order: window.__gymTapes.P.order.length, meta: document.getElementById('pMeta').textContent }));
  ok('on-device mode: it restores into a fresh browser and plays as a full list', a3.n === 2 && a3.t > 0.2 && !a3.paused && a3.order === 2 && a3.meta === 'All uploads, 1 of 2' && e2.length === 0, { a3, e2 });
  await p3.click('#trackList .row >> nth=1 >> .more'); await p3.click('[data-act="m-delete"]'); await sleep(6900);
  const gone3 = await p3.evaluate(() => ({ shown: window.__gymTapes.S.tracks.length, stored: window.__gymTapes.S.raw.tracks.length, bin: window.__gymTapes.S.trash.length }));
  await p3.click('#tabSettings'); await sleep(200); await p3.setInputFiles('#backupInput', localZip);
  await p3.waitForFunction(() => /Restored 1 upload/.test(document.getElementById('backupStatus').textContent), null, { timeout: 30000 }); await sleep(300);
  const back3 = await p3.evaluate(() => ({ shown: window.__gymTapes.S.tracks.length, stored: window.__gymTapes.S.raw.tracks.length, hidden: window.__gymTapes.S.gone.size, bin: window.__gymTapes.S.trash.length, files: window.__gymTapes.store.blobIds().length }));
  ok('on-device mode: an upload in Recently deleted shows up again right after a restore', gone3.shown === 1 && gone3.stored === 2 && gone3.bin === 1 && back3.shown === 2 && back3.stored === 2 && back3.hidden === 0 && back3.bin === 0, { gone3, back3 });
  await c3.close();

  console.log(`\n${pass} passed, ${fail} failed`);
  await browser.close(); server.close();
})().catch(e => { console.error('TEST FAILED', e); process.exit(1); });
