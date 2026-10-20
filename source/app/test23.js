// Test 23 (V17): sound. BPM worked out for new uploads (140 and 100 BPM click tracks), shown on rows, the 140+ filter
// and the BPM sort, older uploads filled in the background; silence cut from the start and end of new uploads (and
// left when the switch is off); the Sound sheet presets (Slowed + reverb, Sped up, Bass boost, 8D, Normal) set the
// speed and the EQ, reverb and 8D on the processing; the fade between uploads; section edges snap to the beat.
const { chromium } = require('./pw.js');
const http = require('http'), fs = require('fs'), path = require('path');
const { execFileSync } = require('child_process');
const DIR = __dirname, OUT = DIR + '/out/';
const sleep = ms => new Promise(r => setTimeout(r, ms));
let pass = 0, fail = 0; const ok = (label, cond, extra) => { cond ? pass++ : fail++; console.log((cond ? 'PASS ' : 'FAIL ') + label + (extra !== undefined ? '  -> ' + JSON.stringify(extra) : '')); };
const server = http.createServer((req, res) => { res.writeHead(200, { 'content-type': 'text/html' }); res.end(fs.readFileSync(path.join(DIR, 'index.html'))); });
const allErrors = [];
const ff = (expr, d, name) => { const f = OUT + name; execFileSync('ffmpeg', ['-v', 'error', '-y', '-f', 'lavfi', '-i', 'aevalsrc=' + expr + ':s=44100:d=' + d, '-c:a', 'libopus', '-b:a', '96k', '-f', 'mp4', f]); return f; };

(async () => {
  fs.mkdirSync(OUT, { recursive: true });
  // click tracks: a kick-like thump on every beat, and a quieter tick in between (so it sounds like music, not a metronome)
  const click = bpm => { const L = (60 / bpm).toFixed(6); return '0.9*sin(2*PI*60*t)*exp(-mod(t\\,' + L + ')*30)*lt(mod(t\\,' + L + ')\\,0.15)+0.25*sin(2*PI*2000*t)*exp(-mod(t+' + (60 / bpm / 2).toFixed(6) + '\\,' + L + ')*80)'; };
  const C140 = ff(click(140), 14, 'click-140.mp4'), C100 = ff(click(100), 14, 'click-100.mp4');
  const PAD = ff('if(between(t\\,1.2\\,7.2)\\,0.5*sin(2*PI*330*t)\\,0)', 8.4, 'silence-pad.mp4');
  const PAD2 = ff('if(between(t\\,1.2\\,7.2)\\,0.5*sin(2*PI*220*t)\\,0)', 8.4, 'silence-pad-2.mp4');
  await new Promise(r => server.listen(8793, r));
  const browser = await chromium.launch({ args: ['--autoplay-policy=no-user-gesture-required'] });
  const ctx = await browser.newContext({ viewport: { width: 440, height: 956 }, deviceScaleFactor: 2, hasTouch: true, colorScheme: 'dark' });
  await ctx.addInitScript(() => { window.HP_STANDALONE = true; window.__HP_QUIET = true; window.__HP_RT_OFF = true; try { localStorage.setItem('hp.syncAsked', '1'); localStorage.setItem('hp.guided', '1'); localStorage.setItem('hp.seenVersion', 'V17'); } catch (e) { /* blank */ } });
  const page = await ctx.newPage();
  page.on('pageerror', e => allErrors.push('pageerror: ' + e.message));
  page.on('console', m => { if (m.type() === 'error' && !/ERR_|Failed to load resource|MEDIA_ERR|PIPELINE|DEMUXER|NotSupported|CONNECTION_REFUSED/.test(m.text())) allErrors.push('console: ' + m.text()); });
  const G = (fn, a) => page.evaluate(fn, a), until = (fn, a, ms) => page.waitForFunction(fn, a, { timeout: ms || 8000 }).then(() => true, () => false);
  const add = async (files, n) => { await page.setInputFiles('#fileInput', files); await page.waitForFunction(k => window.__gymTapes.S.tracks.length === k && document.getElementById('upDot').hidden, n, { timeout: 120000 }); await sleep(300); };
  const T = title => G(t => { const x = window.__gymTapes.S.tracks.find(y => y.title === t); return x && { id: x.id, bpm: x.bpm, beat: x.beat, dur: x.dur }; }, title);
  await page.goto('http://localhost:8793/'); await page.waitForFunction(() => window.__gymTapes && window.__gymTapes.S.ready);
  ok('V17 or later', +String(await G(() => window.__gymTapes.VERSION)).replace(/^V/, '') >= 17);

  /* ===== BPM ===== */
  await add([C140, C100], 2);
  const a = await T('click-140'), b = await T('click-100');
  ok('a 140 BPM upload is worked out as 140 BPM', a && Math.abs(a.bpm - 140) <= 2, a);
  ok('a 100 BPM upload as 100 BPM', b && Math.abs(b.bpm - 100) <= 2, b);
  const noBeat = await G(() => {
    const make = fn => { const c = new OfflineAudioContext(1, 22050 * 12, 22050), buf = c.createBuffer(1, 22050 * 12, 22050), x = buf.getChannelData(0); for (let i = 0; i < x.length; i++) x[i] = fn(i / 22050); return buf; };
    let s = 1; const rnd = () => (s = (s * 16807) % 2147483647) / 2147483647 - 0.5;
    return { tone: window.__gymTapes.bpmFrom(make(t => 0.5 * Math.sin(2 * Math.PI * 330 * t))), hiss: window.__gymTapes.bpmFrom(make(() => 0.3 * rnd())), two: window.__gymTapes.bpmFrom(make(t => 0.5 * Math.sin(2 * Math.PI * (t < 6 ? 330 : 660) * t))) };
  });
  ok('no beat, no number: a steady tone, hiss, or two tones get no BPM', noBeat.tone === null && noBeat.hiss === null && noBeat.two === null, noBeat);
  ok('and where the beats fall is saved too', a && typeof a.beat === 'number' && a.beat >= 0 && a.beat < 60 / 140 + 0.02, a);
  await page.click('#tabLibrary'); await sleep(300);
  ok('rows show the BPM', /0:14 · 14\d BPM/.test(await G(() => document.querySelector('#trackList .row[data-key="' + window.__gymTapes.S.tracks.find(y => y.title === 'click-140').id + '"] .meta').textContent)));
  await page.click('#bpmFilter'); await sleep(300);
  ok('the 140+ BPM filter shows only the fast one', (await G(() => [...document.querySelectorAll('#trackList .title')].map(x => x.textContent))).join() === 'click-140');
  await page.click('[data-act="play-all"]'); await sleep(600);
  ok('and Play plays just those', (await G(() => { const g = window.__gymTapes; return g.P.order.map(id => g.S.tracks.find(t => t.id === id).title).join(); })) === 'click-140');
  await page.click('#bpmFilter'); await sleep(200);
  await page.click('[data-act="sort"]'); await sleep(300); await page.click('[data-act="sort-pick"][data-id="bpm"]'); await sleep(300);
  ok('sorting by BPM puts the fastest first', (await G(() => [...document.querySelectorAll('#trackList .title')].map(x => x.textContent))).join() === 'click-140,click-100');
  await G(() => { const g = window.__gymTapes; g.S.opt.sort = 'new'; });
  // an upload from before V17 (no BPM yet) gets one in the background
  await G(id => { const g = window.__gymTapes; return g.store.update('tracks', id, { bpm: null }); }, b.id); await G(() => window.__gymTapes.BPMQ.tried.clear());
  ok('an older upload without a BPM gets one in the background', await until(id => { const t = window.__gymTapes.S.tracks.find(x => x.id === id); return t && t.bpm >= 98 && t.bpm <= 102; }, b.id, 12000));

  /* ===== silence at the start and end ===== */
  await add([PAD], 3);
  const p1 = await T('silence-pad');
  ok('1.2 s of silence at each end is cut from a new upload (8.4 s becomes about 6.1 s)', p1 && p1.dur > 5.9 && p1.dur < 6.5, p1);
  await G(() => { window.__gymTapes.S.opt.trimSilence = false; });
  await add([PAD2], 4);
  const p2 = await T('silence-pad-2');
  ok('with Trim silence off, it is left as it was', p2 && p2.dur > 8.2, p2);
  await G(() => { window.__gymTapes.S.opt.trimSilence = true; });

  /* ===== Sound ===== */
  await page.click('#tabLibrary'); await sleep(200); await page.click('#trackList .row[data-key="' + a.id + '"] .row-hit'); await sleep(500);
  if (await G(() => window.__gymTapes.audio.paused)) await page.click('#trackList .row[data-key="' + a.id + '"] .row-hit');      // it was already playing: that tap paused it
  await until(() => !window.__gymTapes.audio.paused);
  await page.click('#player .now-open'); await sleep(900);
  ok('the tools row in the big player has Sound', /Sound/.test(await G(() => document.querySelector('#fGym [data-act="sound"]').textContent)));
  await page.click('#fGym [data-act="sound"]'); await sleep(400);
  const tiles = await G(() => [...document.querySelectorAll('.snd-tile b')].map(x => x.textContent));
  ok('Sound: Normal, Slowed + reverb, Sped up, Bass boost, 8D, then EQ, Reverb, 8D, Speed, Fade', tiles.join('|') === 'Normal|Slowed + reverb|Sped up|Bass boost|8D' && await page.isVisible('[data-k="eq"][data-v="vocal"]') && await page.isVisible('[data-k="verb"][data-v="hall"]') && await page.isVisible('#sw-d8') && await page.isVisible('[data-k="xfade"][data-v="6"]'), tiles);
  await page.screenshot({ path: DIR + '/shots/v17-phone-sound.png' });
  const fx = () => G(() => { const g = window.__gymTapes, n = g.FX.n || {}; return { a1: g.audio === document.getElementById('audioFx'), rate: g.audio.playbackRate, pitch: g.audio.preservesPitch, speed: g.S.opt.speed, eq: g.S.opt.eq, verb: g.S.opt.verb, d8: g.S.opt.d8, wet: n.wet ? Math.round(n.wet.gain.value * 100) / 100 : null, low: n.low ? Math.round(n.low.gain.value) : null, depth: n.depth ? Math.round(n.depth.gain.value * 100) / 100 : null, preset: g.sndPreset(), playing: !g.audio.paused }; });
  await page.click('[data-act="snd-pick"][data-k="slowed"]'); await sleep(1500);
  let f = await fx();
  ok('Slowed + reverb: 0.85 speed with the pitch going down too, and the hall reverb on the processing', f.a1 && f.speed === 0.85 && Math.abs(f.rate - 0.85) < 0.01 && f.pitch === false && f.verb === 'hall' && f.wet > 0.35 && f.playing, f);
  ok('the Sound button says Slowed (its short name), and Sound: Slowed + reverb to screen readers', /^Slowed$/.test(await G(() => document.querySelector('#fGym [data-act="sound"]').textContent)) && /Slowed \+ reverb/.test(await G(() => document.querySelector('#fGym [data-act="sound"]').getAttribute('aria-label'))));
  await page.click('[data-act="snd-pick"][data-k="bass"]'); await sleep(1200); f = await fx();
  ok('Bass boost: normal speed, the low end up 8 dB, no reverb', f.speed === 1 && f.low === 8 && f.verb === 'off' && f.wet < 0.05, f);
  await page.click('[data-act="snd-pick"][data-k="d8"]'); await sleep(1500); f = await fx();
  ok('8D: the sound sweeps between the ears, with a little room', f.d8 && f.depth > 0.8 && f.verb === 'room', f);
  await page.click('[data-act="snd-pick"][data-k="sped"]'); await sleep(800); f = await fx();
  ok('Sped up: 1.25 speed, higher', f.speed === 1.25 && Math.abs(f.rate - 1.25) < 0.01 && f.pitch === false, f);
  await page.click('[data-k="eq"][data-v="vocal"]'); await sleep(500); f = await fx();
  ok('changing one part makes it Custom', f.eq === 'vocal' && f.preset === '' && /Custom sound/.test(await G(() => document.querySelector('#fGym [data-act="sound"]').textContent)), f);
  await page.click('[data-act="snd-pick"][data-k="normal"]'); await sleep(800); f = await fx();
  ok('Normal: back to the plain player and normal speed', !f.a1 && f.speed === 1 && f.eq === 'flat' && f.verb === 'off' && !f.d8 && f.playing, f);

  /* ===== the fade between uploads ===== */
  await page.click('[data-k="xfade"][data-v="3"]'); await sleep(800);
  ok('the fade moves the sound onto the processing', (await fx()).a1);
  await page.click('#sheetPanel [data-act="sheet-close"]'); await sleep(300);
  await G(() => { const g = window.__gymTapes; g.S.loop = 'all'; if (g.audio.paused) g.audio.play(); });      // the presets above took a while: keep it going
  await sleep(600);
  await G(() => { const g = window.__gymTapes; g.S.loop = 'all'; g.audio.currentTime = Math.max(0, g.audio.duration - 2.6); }); await sleep(1300);
  const fadeV = await G(() => { const g = window.__gymTapes; return Math.round(g.FX.gain.gain.value * 100) / 100; });
  ok('near the end it fades out', fadeV < 0.8, fadeV);
  await until(() => { const a = window.__gymTapes.audio; return !a.paused && a.currentTime > 0.2 && a.currentTime < 0.9; }, null, 6000);      // the next one (here the same upload again) has started
  const inV = await G(() => { const g = window.__gymTapes; return Math.round(g.FX.gain.gain.value * 100) / 100; });
  await sleep(2600);
  const upV = await G(() => { const g = window.__gymTapes; return Math.round(g.FX.gain.gain.value * 100) / 100; });
  ok('and the next one fades in', inV < upV && upV > 0.9, { inV, upV });
  await G(() => { window.__gymTapes.S.opt.xfade = 0; });

  /* ===== the editor: section edges snap to the beat ===== */
  await page.click('[data-act="full-close"]:visible').catch(() => {}); await sleep(600);
  await page.click('#tabLibrary'); await sleep(200);
  await page.click('#trackList .row[data-key="' + a.id + '"] [data-act="menu"]'); await sleep(400); await page.click('[data-act="m-edit"]'); await sleep(1200);
  const box = await G(() => { const r = document.getElementById('edTrack').getBoundingClientRect(), h = document.getElementById('hdA').getBoundingClientRect(); return { x: r.left, w: r.width, y: r.top + r.height / 2, hx: h.left + h.width / 2, hy: h.top + h.height / 2 }; });
  const target = 3.1, dur = await G(() => window.__gymTapes.ED.dur);
  await page.mouse.move(box.hx, box.hy); await page.mouse.down(); await page.mouse.move(box.x + box.w * target / dur, box.hy, { steps: 6 }); await page.mouse.up(); await sleep(300);
  const ea = await G(() => window.__gymTapes.ED.a), L = 60 / a.bpm, k = Math.round((ea - a.beat) / L);
  ok('dragging a section edge near a beat puts it right on the beat', ea > 1 && Math.abs(ea - (a.beat + k * L)) < 0.02, { ea, beat: a.beat, L });
  await page.focus('#hdA'); await page.keyboard.press('ArrowRight'); await page.keyboard.press('ArrowRight'); await sleep(100);
  const ea2 = await G(() => window.__gymTapes.ED.a);
  await page.click('[data-act="nudge"][data-w="a"][data-d="-0.1"]').catch(() => {}); await sleep(100);
  const ea3 = await G(() => window.__gymTapes.ED.a);
  ok('the arrow keys and the - button still move exactly 0.1 s (no snapping)', Math.abs(ea2 - ea - 0.2) < 0.011 && Math.abs(ea3 - ea - 0.1) < 0.011, { ea, ea2, ea3 });
  await page.screenshot({ path: DIR + '/shots/v17-phone-editor.png' });
  await page.click('[data-act="ed-close"]'); await sleep(400);

  ok('no errors', !allErrors.length, allErrors.slice(0, 5));
  console.log(`\n${pass} passed, ${fail} failed`);
  await browser.close(); server.close();
  process.exit(fail ? 1 : 0);
})().catch(e => { console.error('TEST FAILED', e); process.exit(1); });
