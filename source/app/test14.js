// Test 14 (V10): original videos. Kept on upload (video files only), watched full screen, saved with or without the end clip,
// split into pieces for the saved library, left out when storage is full, backed up and restored, deleted with the upload,
// and the same on this device (the home screen app) with the share sheet.
const { chromium } = require('./pw.js'); require('./legacy');
const http = require('http'), fs = require('fs'), path = require('path'), crypto = require('crypto');
const { execFileSync } = require('child_process');
const DIR = __dirname, OUT = path.join(DIR, 'out'), VT = path.join(DIR, '..', 'vtest'), blobs = new Map(), types = new Map(), saved = [];
const sleep = ms => new Promise(r => setTimeout(r, ms));
const sha = b => crypto.createHash('sha1').update(b).digest('hex');
let pass = 0, fail = 0; const ok = (label, cond, extra) => { cond ? pass++ : fail++; console.log((cond ? 'PASS ' : 'FAIL ') + label + (extra !== undefined ? '  -> ' + JSON.stringify(extra) : '')); };
const server = http.createServer((req, res) => { res.writeHead(200, { 'content-type': 'text/html' }); res.end(fs.readFileSync(path.join(DIR, 'index.html'))); });
let FAKE = fs.readFileSync(path.join(DIR, 'test6.js'), 'utf8').match(/const FAKE = \(\) => \{[\s\S]*?\n\};\n/)[0];
/* like the real library: 20 MB a file, no file that starts like a web page, and a full store when asked */
const U = "const type = (o && o.type) || blob.type;";
if (FAKE.indexOf(U) < 0) throw new Error('fake upload changed');
FAKE = FAKE.replace(U, U + " window.__ups = window.__ups || []; if (blob.size > 20 * 1048576) throw { code: 'too_large' }; if (window.__vidQuota && blob.size > 1500000) throw { code: 'quota_or_state' };" +
  " { const h = new Uint8Array(await blob.slice(0, 64).arrayBuffer()); let k = 0; while (k < h.length && (h[k] === 32 || (h[k] >= 9 && h[k] <= 13))) k++; if (h[k] === 60) throw { code: 'unsupported_type' }; } window.__ups.push(blob.size);");
const A = "if (!/\\.(mp4|webm|png|jpg|txt|json)$/.test(r.filename)) throw { code: 'rejected_extension' }; window.__saves.push({ filename: r.filename, size: r.data.size });";
if (FAKE.indexOf(A) < 0) throw new Error('fake downloads changed');
FAKE = FAKE.replace(A, "if (!/\\.(mp4|webm|png|jpg|txt|json|zip)$/.test(r.filename)) throw { code: 'rejected_extension' }; window.__saves.push({ filename: r.filename, size: r.data.size });" +
  " { const u8 = new Uint8Array(await r.data.arrayBuffer()); let s = ''; for (let i = 0; i < u8.length; i += 32768) s += String.fromCharCode.apply(null, u8.subarray(i, i + 32768)); await window.__saveFile(window.__saves.length + '-' + r.filename, btoa(s)); }");
const py = code => execFileSync('python3', ['-c', code], { maxBuffer: 1 << 26 }).toString();
const probe = f => { const o = execFileSync('ffprobe', ['-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', f]).toString().trim(); const e = execFileSync('ffmpeg', ['-v', 'error', '-i', f, '-f', 'null', '-'], { stdio: ['ignore', 'pipe', 'pipe'] }).toString(); return { dur: +o, clean: !e.trim() }; };
const waitSaved = async n => { for (let i = 0; i < 400 && saved.length < n; i++) await sleep(150); await sleep(200); };
const VP9 = path.join(VT, 'tt-vp9.mp4'), BIG = path.join(VT, 'big.mp4');

async function setup(browser, opts) {
  const ctx = await browser.newContext(Object.assign({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 2, hasTouch: true, acceptDownloads: true }, opts.ctx || {}));
  if (opts.cloud) {
    await ctx.exposeFunction('__putBlob', (id, b64, type) => { blobs.set(id, Buffer.from(b64, 'base64')); types.set(id, type); });
    await ctx.exposeFunction('__delBlob', id => blobs.delete(id));
    await ctx.exposeFunction('__saveFile', (name, b64) => { const p = path.join(OUT, 'v14-' + name); fs.writeFileSync(p, Buffer.from(b64, 'base64')); saved.push(p); });
    await ctx.addInitScript(FAKE + '; FAKE();');
    await ctx.route('**/_blob/*', route => {
      const id = route.request().url().split('/_blob/')[1], buf = blobs.get(id);
      if (!buf) return route.fulfill({ status: 404, body: '' });
      const range = route.request().headers()['range'], m = range && /bytes=(\d+)-(\d*)/.exec(range), type = types.get(id) || 'video/mp4';
      if (m) { const a = +m[1], b = m[2] ? +m[2] : buf.length - 1; return route.fulfill({ status: 206, headers: { 'content-type': type, 'accept-ranges': 'bytes', 'content-range': `bytes ${a}-${b}/${buf.length}` }, body: buf.subarray(a, b + 1) }); }
      route.fulfill({ status: 200, headers: { 'content-type': type, 'accept-ranges': 'bytes' }, body: buf });
    });
  }
  if (opts.share) await ctx.addInitScript(() => { window.__shared = []; navigator.canShare = d => !!(d && d.files && d.files.length); navigator.share = d => { window.__shared.push(d.files.map(f => f.name + ':' + f.size + ':' + f.type)); return Promise.resolve(); }; });
  const page = await ctx.newPage(), errors = [];
  page.on('pageerror', e => errors.push('pageerror: ' + e.message));
  page.on('console', m => { if (m.type() === 'error' && !/fonts\.g|ERR_|Failed to load resource|MEDIA_ERR|PIPELINE|DEMUXER/.test(m.text())) errors.push('console: ' + m.text()); });
  const G = (fn, a) => page.evaluate(fn, a);
  const ready = () => page.waitForFunction(() => window.__gymTapes && window.__gymTapes.S.ready);
  const T = title => G(t => { const x = window.__gymTapes.S.tracks.find(y => y.title === t); return x ? JSON.parse(JSON.stringify(x)) : null; }, title);
  const add = async (files, n) => { await page.setInputFiles('#fileInput', files); await page.waitForFunction(k => window.__gymTapes.S.tracks.length === k && document.getElementById('upDot').hidden, n, { timeout: 120000 }); await sleep(400); };
  const menu = async title => { await page.click('#tabLibrary'); await page.click('#libUploads'); await page.click('#trackList .row:has(.title:text-is("' + title + '")) .more'); await sleep(250); };
  const vid = () => G(() => { const v = document.getElementById('vVideo'); return { shown: !document.getElementById('vview').hidden, src: (v.getAttribute('src') || '').slice(0, 5), dur: +(+v.duration || 0).toFixed(2), t: +v.currentTime.toFixed(2), paused: v.paused, note: document.getElementById('vNote').textContent, msg: document.getElementById('vMsg').hidden ? '' : document.getElementById('vMsg').textContent, err: v.error ? v.error.code : 0 }; });
  const waitVid = () => page.waitForFunction(() => { const v = document.getElementById('vVideo'); return v.readyState >= 1 || v.error; }, null, { timeout: 30000 });
  return { ctx, page, errors, G, ready, T, add, menu, vid, waitVid };
}

(async () => {
  await new Promise(r => server.listen(8780, r));
  const browser = await chromium.launch({ args: ['--autoplay-policy=no-user-gesture-required'] });

  /* ===== the Claude version: the saved library ===== */
  let X = await setup(browser, { cloud: true });
  let { page, G, T, add, menu, vid, waitVid } = X;
  await page.goto('http://localhost:8780/'); await X.ready();
  ok('Keep original videos and Cut end clips from videos are on to begin with', await G(() => window.__gymTapes.S.opt.keepVideo === true && window.__gymTapes.S.opt.videoEnd === true));
  await add([VP9, DIR + '/media/Leg-day-beeps.mp4', DIR + '/media/two-tones.mp3'], 3);
  let tv = await T('tt-vp9'), leg = await T('Leg-day-beeps'), mp3 = await T('two-tones');
  const vp9Size = fs.statSync(VP9).size;
  ok('the video file keeps its video, in one piece, with where its end clip starts', tv && tv.video && tv.video.parts.length === 1 && tv.video.bytes === vp9Size && tv.video.end > 25.5 && tv.video.end < 27.5, tv && tv.video);
  ok('the sound still has its end clip cut off as before', tv && tv.dur > 25.5 && tv.dur < 27.5 && Math.abs(tv.dur - tv.video.end) < 0.1, { dur: tv && tv.dur });
  ok('audio files and sound-only MP4s keep nothing extra', leg && !leg.video && mp3 && !mp3.video);
  ok('the stored piece is the original file, byte for byte', sha(blobs.get(tv.video.parts[0])) === sha(fs.readFileSync(VP9)));
  const T0 = tv.video.end;

  await menu('tt-vp9');
  const opts1 = await G(() => Array.from(document.querySelectorAll('#sheetPanel .opt')).map(b => b.dataset.act));
  await page.click('[data-act="sheet-close"]'); await sleep(250);
  await menu('Leg-day-beeps');
  const opts2 = await G(() => Array.from(document.querySelectorAll('#sheetPanel .opt')).map(b => b.dataset.act));
  await page.click('[data-act="sheet-close"]'); await sleep(250);
  ok('the options of a video upload have Watch original and Save video, others do not', opts1.indexOf('m-watch') >= 0 && opts1.indexOf('m-savevid') >= 0 && opts2.indexOf('m-watch') < 0 && opts2.indexOf('m-savevid') < 0, { opts1 });
  ok('the options show the size of the video too', /video 2\.\d MB/.test(await (async () => { await menu('tt-vp9'); const s = await page.textContent('#sheetPanel .sub'); await page.click('[data-act="sheet-close"]'); await sleep(250); return s; })()));

  // something playing, then Watch original: the sound stops, the video plays full screen without its end clip
  await page.click('#trackList .row:has(.title:text-is("Leg-day-beeps")) .row-hit'); await sleep(800);
  const wasPlaying = await G(() => !window.__gymTapes.audio.paused);
  await menu('tt-vp9'); await page.click('[data-act="m-watch"]'); await waitVid(); await sleep(1200);
  let v = await vid();
  ok('Watch original opens the video full screen and the music stops', wasPlaying && v.shown && v.src === 'blob:' && !v.err && (await G(() => window.__gymTapes.audio.paused)), v);
  ok('it is cut where the end clip starts, and says so', Math.abs(v.dur - T0) < 0.12 && /End clip cut off/.test(v.note), { v, T0 });
  ok('and it plays', !v.paused && v.t > 0.3, v);
  await page.screenshot({ path: DIR + '/shots/d0-watch.png' });
  await page.click('[data-act="v-close"]'); await sleep(200);
  v = await vid();
  ok('closing it stops and unloads the video', !v.shown && !v.src, v);

  // Save video from the saved library
  saved.length = 0;
  await menu('tt-vp9'); await page.click('[data-act="m-savevid"]');
  await page.waitForFunction(() => window.__saves.some(s => /\.mp4$/.test(s.filename)), null, { timeout: 30000 }); await waitSaved(1);
  let sv = await G(() => window.__saves.filter(s => /\.mp4$/.test(s.filename)).pop());
  let p1 = probe(saved[saved.length - 1]);
  ok('Save video saves an MP4 that stops where the end clip starts, and plays cleanly', sv.filename === 'tt-vp9.mp4' && Math.abs(p1.dur - T0) < 0.12 && p1.clean && sv.size < vp9Size, { sv, p1 });

  // the switch for videos: off gives the whole thing
  await page.click('#tabSettings'); await sleep(200);
  const sw = await G(() => ({ keep: document.getElementById('sw-keepVideo') && document.getElementById('sw-keepVideo').getAttribute('aria-checked'), end: document.getElementById('sw-videoEnd') && document.getElementById('sw-videoEnd').getAttribute('aria-checked'), autoTrim: document.getElementById('autoTrimSwitch').getAttribute('aria-checked') }));
  ok('Settings has both switches, next to Remove end clips', sw.keep === 'true' && sw.end === 'true' && sw.autoTrim === 'true', sw);
  await page.click('#sw-videoEnd'); await sleep(200);
  saved.length = 0;
  await menu('tt-vp9'); await page.click('[data-act="m-savevid"]');
  await page.waitForFunction(() => window.__saves.filter(s => /\.mp4$/.test(s.filename)).length === 2, null, { timeout: 30000 }); await waitSaved(1);
  ok('with it off, Save video gives the untouched original', sha(fs.readFileSync(saved[saved.length - 1])) === sha(fs.readFileSync(VP9)));
  await menu('tt-vp9'); await page.click('[data-act="m-watch"]'); await waitVid(); await sleep(300); v = await vid();
  ok('and Watch original plays it to the very end', Math.abs(v.dur - 31.18) < 0.15 && !v.note, v);
  await page.click('[data-act="v-close"]'); await sleep(150);
  await page.click('#tabSettings'); await page.click('#sw-videoEnd'); await sleep(150);
  ok('the sound upload is not touched by that switch', (await T('tt-vp9')).dur === tv.dur);

  // the big player
  await page.click('#tabLibrary'); await page.click('#libUploads'); await page.click('#trackList .row:has(.title:text-is("tt-vp9")) .row-hit'); await sleep(600);
  await page.click('[data-act="full-open"]:visible'); await sleep(400); // V14 added a second one for the computer's Now playing panel
  const fw1 = await page.isVisible('#fWatch');
  await page.screenshot({ path: DIR + '/shots/d1-full-watch.png' });
  await page.click('#fWatch'); await waitVid(); await sleep(400); v = await vid();
  ok('the big player has a Watch original button for a video upload, and it opens the video', fw1 && v.shown && Math.abs(v.dur - T0) < 0.12, v);
  await page.click('[data-act="v-close"]'); await sleep(150);
  await page.click('#full .ctl [data-act="next"]'); await sleep(600);
  ok('and none for an upload without a video', (await page.textContent('#fTitle')) !== 'tt-vp9' && !(await page.isVisible('#fWatch')), await page.textContent('#fTitle'));
  await page.click('[data-act="full-close"]'); await sleep(300);
  await page.click('.ctl [data-act="toggle"]').catch(() => {}); await G(() => window.__gymTapes.audio.pause());

  // a video over 20 MB goes in as pieces, and comes back out whole
  X.page.evaluate(() => { window.__ups = []; });
  await add([BIG], 4);
  const big = await T('big'), ups = await G(() => window.__ups);
  ok('a 29 MB video is kept as pieces under 20 MB each', big && big.video && big.video.parts.length === 2 && big.video.bytes === 29180712 && ups.filter(x => x > 1500000).every(x => x <= 20 * 1048576), { parts: big && big.video && big.video.parts.length, ups });
  ok('the pieces put together are the original file', sha(Buffer.concat(big.video.parts.map(id => blobs.get(id)))) === sha(fs.readFileSync(BIG)));
  saved.length = 0;
  await menu('big'); await page.click('[data-act="m-savevid"]');
  await page.waitForFunction(() => window.__saves.filter(s => /^big\.mp4$/.test(s.filename)).length === 1, null, { timeout: 60000 }); await waitSaved(1);
  p1 = probe(saved[saved.length - 1]);
  ok('saving it puts the pieces back together and cuts the end clip off, and it plays cleanly', Math.abs(p1.dur - big.video.end) < 0.12 && p1.clean && big.video.end > 85, { p1, end: big.video.end });

  // storage full: the upload still goes in, without its video, and says so
  await G(() => { window.__vidQuota = true; });
  await add([DIR + '/media/qt.mov'], 5);
  const qt = await T('qt'), msg = await page.textContent('#toast');
  ok('when storage is full the upload is still added, without its video, and it says why', qt && !qt.video && /video could not be kept, storage is full/.test(msg), { msg, video: qt && qt.video });
  await G(() => { window.__vidQuota = false; });

  // Keep original videos off: only the sound
  await page.click('#tabSettings'); await page.click('#sw-keepVideo'); await sleep(150);
  await page.click('#tabUpload'); const upText = await page.textContent('.drop p');
  await add([DIR + '/media/moov-at-end.mp4'], 6);
  ok('with Keep original videos off, a video upload keeps only the sound', !(await T('moov-at-end')).video && /Only the sound is kept/.test(upText), upText);
  await page.click('#tabSettings'); await page.click('#sw-keepVideo'); await sleep(150);

  // backups: a choice when there are videos
  saved.length = 0;
  await page.click('#tabSettings'); await page.click('#backupBtn'); await sleep(300);
  const choice = await G(() => ({ opts: Array.from(document.querySelectorAll('#sheetPanel .opt')).map(b => b.textContent), sub: document.querySelector('#sheetPanel .sub').textContent }));
  ok('Back up library asks: with videos or audio only, with the size of each', choice.opts.length === 2 && /With videos.*about 3\d\.\d MB/.test(choice.opts[0]) && /Audio only.*about \d\.\d MB/.test(choice.opts[1]) && /2 uploads have their original video/.test(choice.sub), choice);
  await page.click('[data-act="bk-audio"]');
  await page.waitForFunction(() => /Backup saved/.test(document.getElementById('backupStatus').textContent), null, { timeout: 60000 }); await waitSaved(1);
  const zA = saved[saved.length - 1], namesA = JSON.parse(py(`import zipfile,json;print(json.dumps(zipfile.ZipFile(${JSON.stringify(zA)}).namelist()))`));
  ok('Audio only leaves the videos out', !namesA.some(n => /^video\//.test(n)) && namesA.filter(n => /^audio\//.test(n)).length === 6, namesA.length);
  await page.click('#backupBtn'); await sleep(300); await page.click('[data-act="bk-video"]');
  await page.waitForFunction(() => /Backup saved: 6 uploads, 2 videos/.test(document.getElementById('backupStatus').textContent), null, { timeout: 120000 }); await waitSaved(2);
  const zV = saved[saved.length - 1];
  const zinfo = JSON.parse(py(`import zipfile,json,hashlib;z=zipfile.ZipFile(${JSON.stringify(zV)});print(json.dumps({'n':z.testzip(),'v':{x:hashlib.sha1(z.read(x)).hexdigest() for x in z.namelist() if x.startswith('video/')}}))`));
  ok('With videos puts both videos in the backup, exact copies, and the file checks out', zinfo.n === null && Object.keys(zinfo.v).length === 2 && zinfo.v['video/' + tv.id + '.mp4'] === sha(fs.readFileSync(VP9)) && zinfo.v['video/' + big.id + '.mp4'] === sha(fs.readFileSync(BIG)), zinfo);

  // deleting an upload deletes its video
  const vpart = tv.video.parts[0];
  await menu('tt-vp9'); await page.click('[data-act="m-delete"]'); await sleep(300);
  await G(() => { document.getElementById('toast').hidden = true; }); await sleep(6600);
  ok('a deleted upload keeps its video while it waits in Recently deleted', blobs.has(vpart) && !(await T('tt-vp9')));
  await page.click('#tabSettings'); await sleep(200); await page.click('#binBtn'); await sleep(200); await page.click('[data-act="bin-purge"]'); await page.click('[data-act="bin-purge-go"]'); await sleep(1500);
  ok('deleting it for good deletes its video too', !blobs.has(vpart));
  ok('no page errors (Claude version)', X.errors.length === 0, X.errors);
  await X.ctx.close();

  /* ===== restore the backup with videos into an empty library ===== */
  X = await setup(browser, { cloud: true }); ({ page, G, T, add, menu, vid, waitVid } = X);
  await page.goto('http://localhost:8780/'); await X.ready(); await G(() => { localStorage.removeItem('fakeDb'); }); await page.reload(); await X.ready();
  await page.click('#tabSettings'); await page.setInputFiles('#backupInput', zV);
  await page.waitForFunction(() => /Restored/.test(document.getElementById('backupStatus').textContent), null, { timeout: 120000 }); await sleep(500);
  const rst = await page.textContent('#backupStatus'), rt = await T('tt-vp9'), rb = await T('big');
  ok('restoring brings the uploads back with their videos', /Restored 6 uploads/.test(rst) && /2 videos put back too/.test(rst) && rt && rt.video && rb && rb.video && rb.video.parts.length === 2 && Math.abs(rt.video.end - T0) < 0.001, rst);
  ok('the restored videos are exact copies', sha(Buffer.concat(rb.video.parts.map(id => blobs.get(id)))) === sha(fs.readFileSync(BIG)) && sha(blobs.get(rt.video.parts[0])) === sha(fs.readFileSync(VP9)));
  await menu('tt-vp9'); await page.click('[data-act="m-watch"]'); await waitVid(); await sleep(300); v = await vid();
  ok('and they play, end clip cut off', v.shown && !v.err && Math.abs(v.dur - T0) < 0.12, v);
  await page.click('[data-act="v-close"]');
  ok('no page errors (restore)', X.errors.length === 0, X.errors);
  await X.ctx.close();

  /* ===== the home screen app: everything on this phone, saving through the share sheet ===== */
  X = await setup(browser, { share: true }); ({ page, G, T, add, menu, vid, waitVid } = X);
  await page.goto('http://localhost:8780/'); await X.ready();
  await add([VP9], 1);
  await page.reload(); await X.ready(); await sleep(300);
  tv = await T('tt-vp9');
  ok('on this phone the video is kept whole and is still there after closing the app', tv && tv.video && tv.video.parts.length === 1 && tv.video.bytes === vp9Size, tv && tv.video);
  await menu('tt-vp9'); await sleep(300); await page.click('[data-act="m-savevid"]'); await sleep(500);
  let sh = await G(() => window.__shared), toastNow = await page.textContent('#toast');
  ok('Save video opens the share sheet straight away, with the end clip cut off', sh.length === 1 && /^tt-vp9\.mp4:\d+:video\/mp4$/.test(sh[0][0]) && +sh[0][0].split(':')[1] < vp9Size && !/Video ready/.test(toastNow), { sh, toastNow });
  await menu('tt-vp9'); await page.click('[data-act="m-watch"]'); await waitVid(); await sleep(400); v = await vid();
  ok('Watch original works from the phone too', v.shown && !v.err && Math.abs(v.dur - T0) < 0.12, v);
  await page.click('#vSave'); await sleep(400); sh = await G(() => window.__shared);
  ok('and Save video in the video view opens the share sheet', sh.length === 2 && /^tt-vp9\.mp4:/.test(sh[1][0]), sh);
  await page.keyboard.press('Escape'); await sleep(200);
  ok('Escape closes the video', !(await vid()).shown);
  await page.screenshot({ path: DIR + '/shots/d2-local.png' });
  ok('no page errors (home screen app)', X.errors.length === 0, X.errors);
  await X.ctx.close();

  /* ===== a computer with no share sheet: a download ===== */
  X = await setup(browser, {}); ({ page, G, T, add, menu } = X);
  await page.goto('http://localhost:8780/'); await X.ready();
  await add([VP9], 1);
  await menu('tt-vp9'); await sleep(300);
  const [dl] = await Promise.all([page.waitForEvent('download', { timeout: 30000 }), page.click('[data-act="m-savevid"]')]);
  const dlp = path.join(OUT, 'v14-dl.mp4'); await dl.saveAs(dlp); const pd = probe(dlp);
  ok('with no share sheet, Save video downloads the cut video', dl.suggestedFilename() === 'tt-vp9.mp4' && Math.abs(pd.dur - T0) < 0.12 && pd.clean, { name: dl.suggestedFilename(), pd });
  await page.click('#tabSettings'); await page.click('#backupBtn'); await sleep(300);
  const [dl2] = await Promise.all([page.waitForEvent('download', { timeout: 60000 }), page.click('[data-act="bk-video"]')]);
  const zl = path.join(OUT, 'v14-local.zip'); await dl2.saveAs(zl);
  const ln = JSON.parse(py(`import zipfile,json;z=zipfile.ZipFile(${JSON.stringify(zl)});print(json.dumps([z.testzip(), z.namelist()]))`));
  ok('a backup with videos from this device has the video in it', ln[0] === null && ln[1].some(n => /^video\/.+\.mp4$/.test(n)), ln);
  // the phone's storage is full: the upload goes in without its video, and it says so, instead of looking kept until the app is closed
  await G(() => { const orig = IDBObjectStore.prototype.put; IDBObjectStore.prototype.put = function (v, k) { if (v instanceof Blob && v.size > 1500000) throw new DOMException('full', 'QuotaExceededError'); return orig.call(this, v, k); }; });
  await add([DIR + '/media/blue-scene.mp4'], 2);
  const bs = await T('blue-scene'), bmsg = await page.textContent('#toast');
  ok('when the phone is full, the upload is added without its video and it says so', bs && !bs.video && /video could not be kept, storage is full/.test(bmsg), { bmsg, video: bs && bs.video });
  ok('no page errors (computer)', X.errors.length === 0, X.errors);

  console.log(`\n${pass} passed, ${fail} failed`);
  await browser.close(); server.close();
})().catch(e => { console.error('TEST FAILED', e); process.exit(1); });
