// Confirm the app's own code can open the preloaded track for trimming (parse + rebuild + ffprobe).
const { chromium } = require('./pw.js'); require('./legacy');
const fs = require('fs'), { execSync } = require('child_process');
(async () => {
  const b = await chromium.launch(); const p = await b.newPage();
  await p.setContent(fs.readFileSync(__dirname + '/index.html', 'utf8'));
  await p.waitForFunction(() => window.__gymTapes);
  const b64 = fs.readFileSync(__dirname + '/seed/workout-loop.mp4').toString('base64');
  const r = await p.evaluate(async b64 => {
    const M = window.__gymTapes.MP4, u8 = Uint8Array.from(atob(b64), c => c.charCodeAt(0));
    const src = await M.parse(M.bufReader(u8));
    const seq = new Uint32Array(src.n - 200); for (let i = 0; i < seq.length; i++) seq[i] = i + 100;   // trim 100 frames off each end
    const out = M.mux(src, seq, M.gather(u8, src, seq));
    const o = new Uint8Array(await out.blob.arrayBuffer()); let s = ''; for (let i = 0; i < o.length; i += 32768) s += String.fromCharCode.apply(null, o.subarray(i, i + 32768));
    return { n: src.n, codec: src.codec, prime: src.prime, ts: src.timescale, dur: out.dur, b64: btoa(s) };
  }, b64);
  fs.writeFileSync(__dirname + '/out/seed-trim.mp4', Buffer.from(r.b64, 'base64'));
  console.log({ frames: r.n, codec: r.codec, prime: r.prime, timescale: r.ts, trimmedDur: r.dur });
  console.log(execSync(`ffprobe -v error -show_entries format=duration:stream=codec_name,nb_frames -of default=nw=1 "${__dirname}/out/seed-trim.mp4"`).toString().trim().replace(/\n/g, ' '));
  console.log('decode errors:', execSync(`ffmpeg -v error -i "${__dirname}/out/seed-trim.mp4" -f null - 2>&1 | head -3`).toString().trim() || 'none');
  await b.close();
})().catch(e => { console.error('FAILED', e); process.exit(1); });
