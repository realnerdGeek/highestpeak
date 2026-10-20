// Test 4: end-clip removal on the 8 real videos (AAC). This test browser cannot decode AAC itself,
// so decoding is handed to ffmpeg; everything else is the app's own code path.
const { chromium } = require('./pw.js'); require('./legacy');
const http = require('http'), fs = require('fs'), path = require('path'), os = require('os');
const { execSync, execFileSync } = require('child_process');
const DIR = __dirname, CH = path.join(DIR, '../chime');
const Ending = require(path.join(CH, 'ending.js'));
const truth = { 1: 27.1577, 2: 28.5841, 3: 26.8179, 4: 26.3535, 5: 36.1524, 6: 23.8937, 7: 40.2623, 8: 26.4943 };
const sleep = ms => new Promise(r => setTimeout(r, ms));
let pass = 0, fail = 0; const ok = (c, m, x) => { c ? pass++ : fail++; console.log((c ? 'PASS ' : 'FAIL ') + m + (x !== undefined ? '  -> ' + JSON.stringify(x) : '')); };

const server = http.createServer((req, res) => { res.writeHead(200, { 'content-type': 'text/html' }); res.end(fs.readFileSync(path.join(DIR, 'index.html'))); });
const pcmOf = file => { const b = execFileSync('ffmpeg', ['-v', 'error', '-i', file, '-f', 'f32le', '-ac', '1', '-ar', '44100', '-'], { maxBuffer: 1 << 28 }); return new Float32Array(b.buffer, b.byteOffset, b.length / 4); };

async function run(dropPriming) {
  const browser = await chromium.launch();
  const ctx = await browser.newContext({ viewport: { width: 390, height: 844 } });
  let n = 0;
  await ctx.exposeFunction('__ffdecode', b64 => {
    const tmp = path.join(os.tmpdir(), `dec-${process.pid}-${n++}.mp4`); fs.writeFileSync(tmp, Buffer.from(b64, 'base64'));
    try { return execFileSync('ffmpeg', ['-v', 'error', '-i', tmp, '-f', 'f32le', '-ac', '2', '-ar', '44100', '-'], { maxBuffer: 1 << 28 }).toString('base64'); } finally { fs.unlinkSync(tmp); }
  });
  await ctx.addInitScript(drop => {
    const C = window.OfflineAudioContext || window.webkitOfflineAudioContext;
    C.prototype.decodeAudioData = function (buf, okCb, noCb) {
      const u8 = new Uint8Array(buf); let s = ''; for (let i = 0; i < u8.length; i += 32768) s += String.fromCharCode.apply(null, u8.subarray(i, i + 32768));
      return window.__ffdecode(btoa(s)).then(b64 => {
        const bin = atob(b64), bytes = new Uint8Array(bin.length); for (let i = 0; i < bin.length; i++) bytes[i] = bin.charCodeAt(i);
        const f = new Float32Array(bytes.buffer), len = f.length / 2 - drop;      // drop > 0 imitates a decoder that silently trims encoder priming
        const ab = new AudioBuffer({ length: len, numberOfChannels: 2, sampleRate: 44100 }), c0 = ab.getChannelData(0), c1 = ab.getChannelData(1);
        for (let i = 0; i < len; i++) { c0[i] = f[2 * (i + drop)]; c1[i] = f[2 * (i + drop) + 1]; }
        if (okCb) okCb(ab); return ab;
      }, e => { if (noCb) noCb(e); throw e; });
    };
  }, dropPriming);
  const page = await ctx.newPage(); const errors = [];
  page.on('pageerror', e => errors.push(e.message));
  await page.goto('http://localhost:8767/');
  await page.waitForFunction(() => window.__gymTapes && window.__gymTapes.S.ready);
  const stored = async id => { const b64 = await page.evaluate(async id => { const t = window.__gymTapes.S.tracks.find(t => t.id === id); const db = await new Promise(r => { const q = indexedDB.open('gym-tapes', 1); q.onsuccess = () => r(q.result); }); const blob = await new Promise(r => { const q = db.transaction('blobs').objectStore('blobs').get(t.asset); q.onsuccess = () => r(q.result); }); const u8 = new Uint8Array(await blob.arrayBuffer()); let s = ''; for (let i = 0; i < u8.length; i += 32768) s += String.fromCharCode.apply(null, u8.subarray(i, i + 32768)); return btoa(s); }, id); return Buffer.from(b64, 'base64'); };
  const importOne = async file => { const before = await page.evaluate(() => window.__gymTapes.S.tracks.map(t => t.id)); await page.setInputFiles('#fileInput', file); await page.waitForFunction(n => window.__gymTapes.S.tracks.length > n || document.querySelector('[data-act="imp-force"]'), before.length, { timeout: 60000 }); if (await page.isVisible('[data-act="imp-force"]')) { await page.click('[data-act="imp-force"]'); await page.waitForFunction(n => window.__gymTapes.S.tracks.length > n, before.length, { timeout: 60000 }); } await sleep(150); if (await page.isVisible('#sheet')) await page.click('[data-act="sheet-close"]'); return page.evaluate(b => window.__gymTapes.S.tracks.find(t => b.indexOf(t.id) < 0), before); };

  console.log(`\n--- decoder ${dropPriming ? 'that trims ' + dropPriming + ' priming samples' : 'that returns every sample'} ---`);
  for (let i = 1; i <= 8; i++) {
    const t = await importOne(path.join(CH, `v${i}.mp4`));
    const out = path.join(DIR, 'out', `trim-v${i}-${dropPriming}.mp4`); fs.writeFileSync(out, await stored(t.id));
    const pcm = pcmOf(out), dur = pcm.length / 44100, left = Ending.find(pcm, 44100, 0.3);
    // loudest 5 ms block in the final 60 ms, compared with the chime's attack (about -5 dB): anything near that is leftover chime
    let peak = 0; const blk = 220; for (let s = Math.max(0, pcm.length - 2646); s + blk <= pcm.length; s += blk) { let e = 0; for (let j = s; j < s + blk; j++) e += pcm[j] * pcm[j]; peak = Math.max(peak, Math.sqrt(e / blk)); }
    const orig = pcmOf(path.join(CH, `v${i}.mp4`)); const at = Math.floor(truth[i] * 44100); let eC = 0; for (let j = at; j < at + 2205; j++) eC += orig[j] * orig[j]; const chimeLevel = Math.sqrt(eC / 2205);
    const lost = truth[i] - dur;
    ok(dur <= truth[i] + 0.001 && lost < 0.5 && !left, `v${i}: ${t.dur}s kept, cut ${(lost * 1000).toFixed(0)} ms before the chime starts, chime left over: ${left ? 'YES' : 'none'}, peaks ${t.peaks.length}`, { endLevel: +peak.toFixed(4), chimeLevel: +chimeLevel.toFixed(3) });
    const dec = execSync(`ffmpeg -v error -i "${out}" -f null - 2>&1 | head -2`).toString().trim(); if (dec) ok(false, `v${i} output decodes cleanly`, dec);
  }
  if (!dropPriming) {
    // a video with no end clip is left alone
    const b = await importOne(path.join(DIR, 'media/Leg-day-beeps.mp4')); ok(Math.abs(b.dur - 24) < 0.05, 'video without an end clip is left untouched', b.dur);
    // switch off -> nothing is removed; then the menu option removes it afterwards
    await page.click('#tabSettings'); await page.click('#autoTrimSwitch'); const sw = await page.getAttribute('#autoTrimSwitch', 'aria-checked'); await page.click('#tabLibrary'); await page.click('#libUploads');
    const full = await importOne(path.join(CH, 'v4.mp4'));
    ok(sw === 'false' && Math.abs(full.dur - 30.37) < 0.06, 'with the switch off the whole audio is kept', { switch: sw, dur: full.dur });
    await page.click(`.row:has([data-id="${full.id}"]) .more`); await page.click('[data-act="m-trimend"]');
    await page.waitForFunction(id => { const t = window.__gymTapes.S.tracks.find(t => t.id === id); return t && t.dur < 27; }, full.id, { timeout: 30000 });
    const after = await page.evaluate(id => window.__gymTapes.S.tracks.find(t => t.id === id), full.id);
    ok(after.dur <= truth[4] && truth[4] - after.dur < 0.5, '"Remove end clip" on an existing track cuts the same place', after.dur);
    await sleep(3400);
    await page.click(`.row:has([data-id="${b.id}"]) .more`); await page.click('[data-act="m-trimend"]'); await page.waitForFunction(() => /No end clip/.test(document.getElementById('toast').textContent), null, { timeout: 20000 });
    ok(true, '"Remove end clip" on a track without one says so and changes nothing', await page.textContent('#toast'));
    // the track preloaded into the live app (chime still on the end, silence already cut)
    const seed = await importOne(path.join(DIR, 'seed/workout-loop.mp4'));   // switch is still off, so it comes in whole
    await sleep(3400); await page.click(`.row:has([data-id="${seed.id}"]) .more`); await page.click('[data-act="m-trimend"]');
    await page.waitForFunction(id => { const t = window.__gymTapes.S.tracks.find(t => t.id === id); return t && t.dur < 27.5; }, seed.id, { timeout: 30000 });
    const seed2 = await page.evaluate(id => window.__gymTapes.S.tracks.find(t => t.id === id), seed.id);
    ok(seed.dur > 28.4 && seed2.dur <= truth[1] && truth[1] - seed2.dur < 0.5, 'the preloaded "Workout loop" file (chime at the very end) gets fixed by "Remove end clip"', { before: seed.dur, after: seed2.dur });
    await page.reload(); await page.waitForFunction(() => window.__gymTapes && window.__gymTapes.S.ready);
    ok(await page.evaluate(() => window.__gymTapes.S.opt.autoTrim === false), 'the switch setting is remembered after a reload');
  }
  ok(errors.length === 0, 'no page errors', errors);
  await browser.close();
}
(async () => {
  await new Promise(r => server.listen(8767, r));
  await run(0); await run(2112);
  console.log(`\n${pass} passed, ${fail} failed`); server.close();
})().catch(e => { console.error('TEST FAILED', e); process.exit(1); });
