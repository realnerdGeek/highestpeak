// Test 15 (V10.1): end clips on .mov photo-post videos. The page's audio decoder is swapped for one that behaves like an iPhone's:
// it turns away QuickTime-style sound, and decodes everything else (AAC included) the way a phone would, with ffmpeg doing the work.
// V10 misses the end clip under it; V10.1 cuts it, and "Check every upload" fixes uploads made before the fix.
const { chromium } = require('./pw.js'); require('./legacy');
const http = require('http'), fs = require('fs'), path = require('path');
const { execFileSync } = require('child_process');
const DIR = __dirname, PH = path.join(DIR, '..', 'photo'), TMP = path.join(DIR, 'out');
const sleep = ms => new Promise(r => setTimeout(r, ms));
let pass = 0, fail = 0; const ok = (label, cond, extra) => { cond ? pass++ : fail++; console.log((cond ? 'PASS ' : 'FAIL ') + label + (extra !== undefined ? '  -> ' + JSON.stringify(extra) : '')); };
const server = http.createServer((req, res) => { res.writeHead(200, { 'content-type': 'text/html' }); res.end(fs.readFileSync(path.join(DIR, req.url.startsWith('/old') ? 'index-v10.html' : 'index.html'))); });
let nDec = 0;
const ffdecode = (b64, sr) => {
  const f = path.join(TMP, 'v15-dec-' + (nDec++ % 4) + '.bin'); fs.writeFileSync(f, Buffer.from(b64, 'base64'));
  try { const raw = execFileSync('ffmpeg', ['-v', 'error', '-i', f, '-ac', '2', '-ar', String(sr || 44100), '-f', 'f32le', '-'], { maxBuffer: 1 << 29 }); return raw.length ? { sr: sr || 44100, ch: 2, data: raw.toString('base64') } : null; }
  catch (e) { return null; }
};
const SAFARI_LIKE = () => {
  const C = window.OfflineAudioContext;
  /* a QuickTime file, or QuickTime-style sound inside the index ("wave" box), is what an iPhone's decoder turns away */
  const quicktime = u8 => {
    if (String.fromCharCode(...u8.subarray(4, 12)) === 'ftypqt  ') return true;
    let o = 0; const dv = new DataView(u8.buffer, u8.byteOffset, u8.length);
    while (o + 8 <= u8.length) {
      const size = dv.getUint32(o), type = String.fromCharCode(...u8.subarray(o + 4, o + 8));
      if (type === 'moov') { for (let i = o; i + 4 < Math.min(u8.length, o + size); i++) if (u8[i] === 0x77 && u8[i + 1] === 0x61 && u8[i + 2] === 0x76 && u8[i + 3] === 0x65) return true; return false; }
      if (size < 8) return false; o += size;
    }
    return false;
  };
  window.__turnedAway = 0;
  C.prototype.decodeAudioData = function (buf, ok, no) {
    const u8 = new Uint8Array(buf.slice(0)), sr = this.sampleRate;
    const p = (async () => {
      if (quicktime(u8)) { window.__turnedAway++; throw new DOMException('Decoding failed', 'EncodingError'); }
      let s = ''; for (let i = 0; i < u8.length; i += 32768) s += String.fromCharCode.apply(null, u8.subarray(i, i + 32768));
      const r = await window.__ffdecode(btoa(s), sr);
      if (!r) throw new DOMException('Decoding failed', 'EncodingError');
      const bin = atob(r.data), raw = new Uint8Array(bin.length); for (let i = 0; i < bin.length; i++) raw[i] = bin.charCodeAt(i);
      const f = new Float32Array(raw.buffer), n = Math.max(1, Math.floor(f.length / r.ch)), ab = new AudioBuffer({ length: n, numberOfChannels: r.ch, sampleRate: r.sr });
      for (let c = 0; c < r.ch; c++) { const ch = new Float32Array(n); for (let i = 0; i < n; i++) ch[i] = f[i * r.ch + c]; ab.copyToChannel(ch, c); }
      return ab;
    })();
    if (ok || no) p.then(ok, no);
    return p;
  };
};

(async () => {
  await new Promise(r => server.listen(8782, r));
  const browser = await chromium.launch();
  const ctx = await browser.newContext({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 2 });
  await ctx.exposeFunction('__ffdecode', ffdecode);
  await ctx.addInitScript(SAFARI_LIKE);
  const page = await ctx.newPage(), errors = [];
  page.on('pageerror', e => errors.push('pageerror: ' + e.message));
  page.on('console', m => { if (m.type() === 'error' && !/ERR_|Failed to load resource|MEDIA_ERR|PIPELINE|DEMUXER|NotSupported/.test(m.text())) errors.push('console: ' + m.text()); });
  const G = (fn, a) => page.evaluate(fn, a);
  const ready = () => page.waitForFunction(() => window.__gymTapes && window.__gymTapes.S.ready);
  const T = title => G(t => { const x = window.__gymTapes.S.tracks.find(y => y.title === t); return x ? JSON.parse(JSON.stringify(x)) : null; }, title);
  const add = async (files, n) => { await page.setInputFiles('#fileInput', files); await page.waitForFunction(k => window.__gymTapes.S.tracks.length === k && document.getElementById('upDot').hidden, n, { timeout: 120000 }); await sleep(500); };
  const named = [];
  for (const i of [1, 2, 3]) { const f = path.join(TMP, 'photo-post-' + i + '.mov'); fs.copyFileSync(path.join(PH, 'p' + i + '.mov'), f); named.push(f); }

  // V10, with an iPhone-like decoder: the end clip of a .mov photo post is missed
  await page.goto('http://localhost:8782/old'); await ready();
  await add([named[0]], 1);
  let a = await T('photo-post-1');
  ok('V10 misses the end clip on a .mov photo post (the bug, reproduced)', a && a.dur > 17.5 && a.video && !a.video.end && (await G(() => window.__turnedAway)) > 0, { dur: a && a.dur, video: a && a.video, turnedAway: await G(() => window.__turnedAway) });

  // V10.1 on the same phone: "Check every upload" fixes it, the sound and the kept video
  await page.goto('http://localhost:8782/'); await ready(); await sleep(300);
  await G(() => { window.__turnedAway = 0; });
  await page.click('#tabSettings'); await page.click('[data-act="trim-all"]');
  await page.waitForFunction(() => /Removed the end clip|No end clips/.test(document.getElementById('toast').textContent), null, { timeout: 60000 }); const msg = await page.textContent('#toast'); await sleep(400);
  a = await T('photo-post-1');
  ok('after the fix, Check every upload cuts it off an upload made before', /Removed the end clip from 1 upload/.test(msg) && a.dur > 14.8 && a.dur < 15.1, { msg, dur: a.dur });
  ok('and marks where the kept video\'s end clip starts', a.video && a.video.end > 14.8 && a.video.end < 15.1, a.video);
  ok('nothing was turned away by the iPhone-like decoder this time', (await G(() => window.__turnedAway)) === 0, await G(() => window.__turnedAway));

  // new .mov uploads: cut on the way in
  await add(named.slice(1), 3);
  const b = await T('photo-post-2'), c = await T('photo-post-3'), toastNow = await page.textContent('#toast');
  ok('new .mov photo posts get their end clip cut automatically', b.dur > 14.8 && b.dur < 15.1 && c.dur > 14.8 && c.dur < 15.1 && /End clips removed from 2/.test(toastNow), { b: b.dur, c: c.dur, toastNow });
  ok('their kept videos know where the end clip starts', b.video && c.video && Math.abs(b.video.end - b.dur) < 0.1 && Math.abs(c.video.end - c.dur) < 0.1, { b: b.video, c: c.video });

  // the sound is stored the standard MP4 way, with the exact same audio frames
  const b64 = await G(async id => { const u8 = await window.__gymTapes.store.bytes(id); let s = ''; for (let i = 0; i < u8.length; i += 32768) s += String.fromCharCode.apply(null, u8.subarray(i, i + 32768)); return btoa(s); }, b.asset);
  const stored = path.join(TMP, 'v15-stored.m4a'); fs.writeFileSync(stored, Buffer.from(b64, 'base64'));
  const info = JSON.parse(execFileSync('python3', ['-c', `
import struct,json,sys
d=open(${JSON.stringify(stored)},'rb').read()
def boxes(o,e):
    while o+8<=e:
        sz,t=struct.unpack('>I4s',d[o:o+8])
        if sz<8: return
        yield t.decode('latin1'),o,o+8,o+sz; o+=sz
def find(o,e,path):
    for t,s,b,en in boxes(o,e):
        if t==path[0]:
            return (s,b,en) if len(path)==1 else find(b,en,path[1:])
st=find(0,len(d),['moov','trak','mdia','minf','stbl','stsd'])
minf=find(0,len(d),['moov','trak','mdia','minf'])
eb=st[1]+8
print(json.dumps({'brand':d[8:12].decode('latin1'),'entry':d[eb+4:eb+8].decode('latin1'),'version':struct.unpack('>H',d[eb+16:eb+18])[0],'wave':b'wave' in d[st[0]:st[2]],'minf':[t for t,_,_,_ in boxes(minf[1],minf[2])]}))
`]).toString());
  ok('the stored sound is a standard MP4 (no QuickTime-style description left)', info.brand === 'isom' && info.entry === 'mp4a' && info.version === 0 && !info.wave && info.minf.join() === 'smhd,dinf,stbl', info);
  const fm = f => execFileSync('ffmpeg', ['-v', 'error', '-i', f, '-map', '0:a', '-c', 'copy', '-f', 'framemd5', '-'], { maxBuffer: 1 << 26 }).toString().split('\n').filter(l => l && l[0] !== '#').map(l => l.split(',').pop().trim());
  const s1 = fm(stored), o1 = fm(named[1]).slice(0, s1.length);
  ok('and every audio frame kept is byte for byte the original', s1.length > 600 && s1.join() === o1.join(), { kept: s1.length });
  ok('it decodes cleanly', !execFileSync('ffmpeg', ['-v', 'error', '-i', stored, '-f', 'null', '-'], { stdio: ['ignore', 'pipe', 'pipe'] }).toString().trim());

  // the kept video, cut without the end card, from the HEVC .mov
  const vb = await G(async title => { const g = window.__gymTapes, t = g.S.tracks.find(x => x.title === title), r = await g.prepVideo(t), u8 = new Uint8Array(await r.blob.arrayBuffer()); let s = ''; for (let i = 0; i < u8.length; i += 32768) s += String.fromCharCode.apply(null, u8.subarray(i, i + 32768)); return { cut: r.cut, b64: btoa(s) }; }, 'photo-post-2');
  const vf = path.join(TMP, 'v15-video.mp4'); fs.writeFileSync(vf, Buffer.from(vb.b64, 'base64'));
  const vd = +execFileSync('ffprobe', ['-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', vf]).toString().trim();
  ok('Watch original and Save video get the video with the end card cut off', vb.cut && Math.abs(vd - b.video.end) < 0.1 && !execFileSync('ffmpeg', ['-v', 'error', '-i', vf, '-f', 'null', '-'], { stdio: ['ignore', 'pipe', 'pipe'] }).toString().trim(), { cut: vb.cut, vd });

  // a normal MP4 TikTok save still works the same
  await add([DIR + '/media/opus-clip.mp4'], 4);
  const o = await T('opus-clip');
  ok('a normal MP4 still gets its end clip cut as before', o.dur > 26.8 && o.dur < 27.3 && o.video && Math.abs(o.video.end - o.dur) < 0.1, { dur: o.dur, end: o.video && o.video.end });
  ok('no page errors', errors.length === 0, errors);
  console.log(`\n${pass} passed, ${fail} failed`);
  await browser.close(); server.close();
})().catch(e => { console.error('TEST FAILED', e); process.exit(1); });
