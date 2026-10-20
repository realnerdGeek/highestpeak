// Test 1: local mode (no viewer). Import each format, pull the stored audio file back out, verify with ffprobe.
const { chromium } = require('./pw.js'); require('./legacy');
const http = require('http'), fs = require('fs'), path = require('path');
const { execSync } = require('child_process');
const DIR = __dirname;

const server = http.createServer((req, res) => {
  const f = path.join(DIR, req.url === '/' ? 'index.html' : decodeURIComponent(req.url.split('?')[0]));
  if (!fs.existsSync(f)) { res.writeHead(404); return res.end(); }
  res.writeHead(200, { 'content-type': f.endsWith('.html') ? 'text/html' : 'application/octet-stream' }); res.end(fs.readFileSync(f));
});

(async () => {
  await new Promise(r => server.listen(8765, r));
  const browser = await chromium.launch({ args: ['--autoplay-policy=no-user-gesture-required'] });
  const ctx = await browser.newContext({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 2 });
  const page = await ctx.newPage();
  const errors = [];
  page.on('pageerror', e => errors.push('pageerror: ' + e.message));
  page.on('console', m => { if (m.type() === 'error' && !/fonts\.g|ERR_|Failed to load resource/.test(m.text())) errors.push('console: ' + m.text()); });
  await page.goto('http://localhost:8765/');
  await page.waitForFunction(() => window.__gymTapes && window.__gymTapes.S.ready);
  console.log('AAC playable here:', await page.evaluate(() => document.createElement('audio').canPlayType('audio/mp4; codecs="mp4a.40.2"') || 'no'),
    '| Opus-in-MP4:', await page.evaluate(() => document.createElement('audio').canPlayType('audio/mp4; codecs="opus"') || 'no'));
  console.log('notice:', await page.textContent('#notice'));
  await page.screenshot({ path: path.join(DIR, 'shots/01-empty.png') });

  const good = ['33966784-v29025g50000datbdifog65qur5e1a6g.mp4', 'qt.mov', 'moov-at-end.mp4', 'opus-clip.mp4', 'Leg-day-beeps.mp4'];
  for (const name of good) {
    const before = await page.evaluate(() => window.__gymTapes.S.tracks.length);
    await page.setInputFiles('#fileInput', path.join(DIR, 'media', name));
    await page.waitForFunction(n => window.__gymTapes.S.tracks.length > n, before, { timeout: 30000 });
    if (await page.isVisible('#sheet')) { await page.click('[data-act="sheet-close"]'); }
    const info = await page.evaluate(async () => {
      const t = window.__gymTapes.S.tracks[0];
      const db = await new Promise(r => { const q = indexedDB.open('gym-tapes', 1); q.onsuccess = () => r(q.result); });
      const blob = await new Promise(r => { const q = db.transaction('blobs').objectStore('blobs').get(t.asset); q.onsuccess = () => r(q.result); });
      const u8 = new Uint8Array(await blob.arrayBuffer()); let s = ''; for (let i = 0; i < u8.length; i += 32768) s += String.fromCharCode.apply(null, u8.subarray(i, i + 32768));
      return { title: t.title, dur: t.dur, bytes: t.bytes, peaks: t.peaks.length, peakMax: Math.max(...t.peaks), peakMin: Math.min(...t.peaks), b64: btoa(s) };
    });
    const out = path.join(DIR, 'out', name.replace(/\.[^.]+$/, '') + '.audio.mp4');
    fs.writeFileSync(out, Buffer.from(info.b64, 'base64'));
    const probe = execSync(`ffprobe -v error -show_entries stream=codec_type,codec_name,sample_rate,channels,nb_frames:format=duration,format_name -of default=nw=1 "${out}" 2>&1`).toString().trim().replace(/\n/g, ' ');
    const decodeErr = execSync(`ffmpeg -v error -i "${out}" -f null - 2>&1 | head -3`).toString().trim();
    console.log(`\n[${name}] -> "${info.title}" dur=${info.dur}s bytes=${info.bytes} peaks=${info.peaks} (${info.peakMin}..${info.peakMax})\n   ffprobe: ${probe}\n   decode errors: ${decodeErr || 'none'}`);
  }
  // bit-exact check against ffmpeg's own lossless extraction
  execSync(`ffmpeg -v error -y -i "${DIR}/out/33966784-v29025g50000datbdifog65qur5e1a6g.audio.mp4" -f s16le -ac 2 -ar 44100 "${DIR}/out/mine.pcm"`);
  const a = fs.readFileSync(DIR + '/out/ref.pcm'), b = fs.readFileSync(DIR + '/out/mine.pcm');
  console.log(`\nPCM vs ffmpeg reference: ref=${a.length} mine=${b.length} identical=${a.equals(b)}`);

  for (const name of ['silent.mp4', 'notes.mp4']) {
    await page.setInputFiles('#fileInput', path.join(DIR, 'media', name));
    await page.waitForSelector('.imp.err', { timeout: 15000 });
    console.log(`[${name}] error shown: ${await page.textContent('.imp.err .st')}`);
    await page.click('.imp.err [data-act="imp-dismiss"]');
  }
  // persistence across reload (IndexedDB)
  await page.reload(); await page.waitForFunction(() => window.__gymTapes && window.__gymTapes.S.ready);
  console.log('\nafter reload, tracks:', await page.evaluate(() => window.__gymTapes.S.tracks.map(t => t.title + ' ' + t.dur)));
  await page.screenshot({ path: path.join(DIR, 'shots/02-tracks.png') });
  console.log('errors:', errors.length ? errors : 'none');
  await browser.close(); server.close();
})().catch(e => { console.error('TEST FAILED', e); process.exit(1); });
