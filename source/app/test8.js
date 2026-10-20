// Test 8 (V6): MP3, WAV and other plain audio uploads.
const { chromium } = require('./pw.js'); require('./legacy');
const http = require('http'), fs = require('fs'), path = require('path');
const { execSync } = require('child_process');
const DIR = __dirname;
const sleep = ms => new Promise(r => setTimeout(r, ms));
let pass = 0, fail = 0; const ok = (label, cond, extra) => { cond ? pass++ : fail++; console.log((cond ? 'PASS ' : 'FAIL ') + label + (extra !== undefined ? '  -> ' + JSON.stringify(extra) : '')); };
const server = http.createServer((req, res) => { res.writeHead(200, { 'content-type': 'text/html' }); res.end(fs.readFileSync(path.join(DIR, 'index.html'))); });
const probe = f => execSync(`ffprobe -v error -show_entries stream=codec_name,sample_rate,channels:format=duration -of default=nw=1 "${f}"`).toString().trim().replace(/\n/g, ' ');
const decErr = f => execSync(`ffmpeg -v error -i "${f}" -f null - 2>&1 | head -2`).toString().trim();
const freq = (f, at) => { const raw = execSync(`ffmpeg -v error -ss ${at} -t 1 -i "${f}" -f s16le -ac 1 -ar 48000 -`, { maxBuffer: 1 << 26 }); let z = 0, prev = 0; for (let i = 0; i + 1 < raw.length; i += 2) { const v = raw.readInt16LE(i); if (prev <= 0 && v > 0) z++; prev = v; } return z; };
(async () => {
  await new Promise(r => server.listen(8771, r));
  const browser = await chromium.launch({ args: ['--autoplay-policy=no-user-gesture-required'] });
  const ctx = await browser.newContext({ viewport: { width: 390, height: 844 } });
  const page = await ctx.newPage(); const errors = [];
  page.on('pageerror', e => errors.push('pageerror: ' + e.message));
  page.on('console', m => { if (m.type() === 'error' && !/fonts\.g|ERR_|Failed to load resource/.test(m.text())) errors.push('console: ' + m.text()); });
  const G = (fn, a) => page.evaluate(fn, a);
  await page.goto('http://localhost:8771/'); await page.waitForFunction(() => window.__gymTapes && window.__gymTapes.S.ready);
  console.log('encoder this test browser offers:', JSON.stringify(await G(async () => { const p = await window.__gymTapes.pickEncoder(); return p && p.codec; })));
  const stored = async title => { const b64 = await G(async title => { const t = window.__gymTapes.S.tracks.find(t => t.title === title); const db = await new Promise(r => { const q = indexedDB.open('gym-tapes', 1); q.onsuccess = () => r(q.result); }); const blob = await new Promise(r => { const q = db.transaction('blobs').objectStore('blobs').get(t.asset); q.onsuccess = () => r(q.result); }); const u8 = new Uint8Array(await blob.arrayBuffer()); let s = ''; for (let i = 0; i < u8.length; i += 32768) s += String.fromCharCode.apply(null, u8.subarray(i, i + 32768)); return btoa(s); }, title); const f = path.join(DIR, 'out', 'conv-' + title.replace(/\W+/g, '_') + '.mp4'); fs.writeFileSync(f, Buffer.from(b64, 'base64')); return f; };
  const add = async (file, n) => { await page.setInputFiles('#fileInput', path.join(DIR, 'media', file)); await page.waitForFunction(n => window.__gymTapes.S.tracks.length === n, n, { timeout: 90000 }); await sleep(250); };
  const T = title => G(t => window.__gymTapes.S.tracks.find(x => x.title === t), title);

  ok('upload screen mentions MP3 and WAV', /MP3, WAV or M4A/.test(await (async () => { await page.click('#tabUpload'); return page.textContent('#view'); })()));
  await add('two-tones.mp3', 1);
  let t = await T('two-tones'), f = await stored('two-tones');
  ok('MP3 becomes an upload with the right length, sound and waveform', Math.abs(t.dur - 12) < 0.15 && !decErr(f) && Math.abs(freq(f, 2) - 330) < 15 && Math.abs(freq(f, 9) - 660) < 15 && t.peaks.length === 96 && typeof t.gain === 'number', { dur: t.dur, probe: probe(f), hz: [freq(f, 2), freq(f, 9)] });
  await G(() => { const g = window.__gymTapes; g.S.tracks.forEach(x => {}); });
  await page.setInputFiles('#fileInput', path.join(DIR, 'media', 'two-tones.wav')); await page.waitForFunction(() => window.__gymTapes.S.tracks.length === 2, null, { timeout: 90000 }); await sleep(250);
  const wavT = await G(() => window.__gymTapes.S.tracks[0]); fs.writeFileSync(DIR + '/out/_w.txt', wavT.title);
  await G(id => { const g = window.__gymTapes; }, wavT.id);
  // rename the WAV one so the two can be told apart
  await page.click('.acts >> nth=0 >> [data-act="up-rename"]'); await page.fill('#renameInput', 'from-wav'); await page.click('form[data-form="rename"] button[type=submit]'); await page.waitForFunction(() => window.__gymTapes.S.tracks.some(x => x.title === 'from-wav'));
  t = await T('from-wav'); f = await stored('from-wav');
  ok('WAV becomes an upload the same way', Math.abs(t.dur - 12) < 0.15 && !decErr(f) && Math.abs(freq(f, 2) - 330) < 15 && Math.abs(freq(f, 9) - 660) < 15 && t.bytes < 400000, { dur: t.dur, kb: Math.round(t.bytes / 1024), probe: probe(f) });
  await add('mono-low.wav', 3); t = await T('mono-low'); f = await stored('mono-low');
  ok('mono, low sample rate WAV works too', Math.abs(t.dur - 3) < 0.15 && !decErr(f) && Math.abs(freq(f, 1) - 440) < 15, { dur: t.dur, probe: probe(f) });
  // it then behaves like any other upload: plays, and can be trimmed
  await page.click('.row:has-text("from-wav") .row-hit'); await sleep(900);
  ok('a converted upload plays', await G(() => !window.__gymTapes.audio.paused && window.__gymTapes.audio.currentTime > 0.3));
  await page.click('#playBtn');
  await page.click('.row:has-text("from-wav") .more'); await page.click('[data-act="m-edit"]');
  await page.waitForFunction(() => window.__gymTapes.ED.seq && !window.__gymTapes.ED.busy, null, { timeout: 15000 });
  await page.focus('#hdA'); for (let i = 0; i < 60; i++) await page.keyboard.press('ArrowRight');
  await page.click('#edKeep'); await page.click('#edSave'); await page.waitForFunction(() => document.getElementById('editor').hidden, null, { timeout: 15000 }); await sleep(300);
  t = await T('from-wav'); f = await stored('from-wav');
  ok('and can be trimmed like the rest', Math.abs(t.dur - 6) < 0.2 && !decErr(f) && Math.abs(freq(f, 2) - 660) < 15, { dur: t.dur });
  // an MP3 made from one of the real videos still gets its end clip removed
  await add('clip-with-ending.mp3', 4); t = await T('clip-with-ending');
  ok('end clip is still found and removed on an MP3', t.dur < 26.4 && t.dur > 25.9, { dur: t.dur, toast: await page.textContent('#toast') });
  // something that is not audio at all
  await page.setInputFiles('#fileInput', path.join(DIR, 'media', 'notes.txt')); await page.waitForSelector('.imp.err', { timeout: 20000 });
  ok('a file that is not audio gets a clear message', /Could not read this file/.test(await page.textContent('.imp.err .st')), await page.textContent('.imp.err .st'));
  await page.screenshot({ path: DIR + '/shots/70-upload-audio.png', fullPage: true });

  // the AAC route (what an iPhone would use): real AAC frames, with and without the extra per-frame header, through the same file builder
  const adts = fs.readFileSync(DIR + '/media/two-tones.aac').toString('base64');
  for (const keepHeader of [true, false]) {
    const b64 = await G(async ({ adts, keepHeader }) => {
      const g = window.__gymTapes, u8 = Uint8Array.from(atob(adts), c => c.charCodeAt(0)), frames = [];
      for (let o = 0; o + 7 < u8.length;) { const len = ((u8[o + 3] & 3) << 11) | (u8[o + 4] << 3) | (u8[o + 5] >> 5); if (u8[o] !== 0xFF || len < 8) break; const whole = u8.slice(o, o + len); frames.push({ b: keepHeader ? g.stripAdts(whole) : whole.subarray(7), dur: 1024 }); o += len; }
      const r = g.MP4.audioSrc('aac', 44100, 2, frames, 1024, 160000), out = g.MP4.mux(r.full, Uint32Array.from(frames, (_, i) => i), r.payload);
      const o8 = new Uint8Array(await out.blob.arrayBuffer()); let s = ''; for (let i = 0; i < o8.length; i += 32768) s += String.fromCharCode.apply(null, o8.subarray(i, i + 32768));
      const back = await g.MP4.parse(g.MP4.bufReader(o8));
      return { b64: btoa(s), n: frames.length, back: back.n, codec: back.codec, dur: out.dur };
    }, { adts, keepHeader });
    const file = DIR + '/out/aac-route-' + keepHeader + '.mp4'; fs.writeFileSync(file, Buffer.from(b64.b64, 'base64'));
    ok(`AAC frames ${keepHeader ? 'with the extra header stripped by the app' : 'already bare'} build a valid file`, /codec_name=aac/.test(probe(file)) && /channels=2/.test(probe(file)) && /sample_rate=44100/.test(probe(file)) && !decErr(file) && Math.abs(freq(file, 2) - 330) < 15 && Math.abs(freq(file, 9) - 660) < 15 && b64.back === b64.n && b64.codec === 'mp4a', { frames: b64.n, dur: +b64.dur.toFixed(2), probe: probe(file) });
  }
  ok('no page errors', errors.length === 0, errors);
  console.log(`\n${pass} passed, ${fail} failed`);
  await browser.close(); server.close();
})().catch(e => { console.error('TEST FAILED', e); process.exit(1); });
