// Test 12 (V9): the volume bar on an iPhone, where a page's own volume is ignored, so the bar drives the sound processing.
const { chromium } = require('./pw.js'); require('./legacy');
const http = require('http'), fs = require('fs'), path = require('path');
const DIR = __dirname, blobs = new Map(), types = new Map();
const sleep = ms => new Promise(r => setTimeout(r, ms));
let pass = 0, fail = 0; const ok = (label, cond, extra) => { cond ? pass++ : fail++; console.log((cond ? 'PASS ' : 'FAIL ') + label + (extra !== undefined ? '  -> ' + JSON.stringify(extra) : '')); };
const server = http.createServer((req, res) => { res.writeHead(200, { 'content-type': 'text/html' }); res.end(fs.readFileSync(path.join(DIR, 'index.html'))); });
const FAKE = fs.readFileSync(path.join(DIR, 'test6.js'), 'utf8').match(/const FAKE = \(\) => \{[\s\S]*?\n\};\n/)[0];
const IPHONE_UA = 'Mozilla/5.0 (iPhone; CPU iPhone OS 18_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148';

(async () => {
  await new Promise(r => server.listen(8775, r));
  const browser = await chromium.launch({ args: ['--autoplay-policy=no-user-gesture-required'] });
  const ctx = await browser.newContext({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 2, hasTouch: true, userAgent: IPHONE_UA });
  await ctx.exposeFunction('__putBlob', (id, b64, type) => { blobs.set(id, Buffer.from(b64, 'base64')); types.set(id, type); });
  await ctx.exposeFunction('__delBlob', id => blobs.delete(id));
  // like the Claude app on iPhone: setting the volume is accepted and reads back, but the sound does not change
  await ctx.addInitScript(() => { const seen = new WeakMap(); Object.defineProperty(HTMLMediaElement.prototype, 'volume', { get() { return seen.has(this) ? seen.get(this) : 1; }, set(v) { seen.set(this, v); }, configurable: true }); });
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
  const S = () => G(() => { const g = window.__gymTapes, a = g.audio; return { el: a.id, t: +a.currentTime.toFixed(2), paused: a.paused, gain: g.FX.gain ? +g.FX.gain.gain.value.toFixed(2) : null, ctx: g.FX.ctx ? g.FX.ctx.state : null, title: document.getElementById('pTitle').textContent, count: !!g.P.countIn, vol: g.VOL.v, fx: g.VOL.useFx }; });
  const setBar = async v => { await page.locator('#player .js-vol').fill(String(v)); await sleep(350); };

  await page.goto('http://localhost:8775/'); await ready();
  await page.setInputFiles('#fileInput', [DIR + '/media/Leg-day-beeps.mp4', DIR + '/media/blue-scene.mp4']);
  await page.waitForFunction(() => window.__gymTapes.S.tracks.length === 2 && document.getElementById('upDot').hidden, null, { timeout: 60000 }); await sleep(300);
  await page.click('#tabLibrary'); await page.click('#libUploads'); await page.click('#trackList .row:has-text("blue-scene") .row-hit'); await sleep(800);
  let st = await S();
  ok('on iPhone the volume bar shows, and at full volume the plain player is used (safe with the phone locked)', (await page.isVisible('#player .js-vol')) && st.el === 'audio' && !st.paused && !st.fx, st);

  const t0 = (await S()).t;
  await setBar(40); st = await S();
  ok('lowering it moves the sound to the processing, carries on from the same spot, at 40 percent', st.el === 'audioFx' && !st.paused && st.gain === 0.4 && st.ctx === 'running' && st.t >= t0 && st.t < t0 + 2 && st.title === 'blue-scene', { t0, st });
  ok('the first time, it says what that means for a locked phone', /lock the phone/.test(await page.textContent('#toast')));
  const lid = await G(() => window.__gymTapes.P.lid);
  await setBar(70); st = await S();
  ok('after that the bar follows the finger with no reload', st.el === 'audioFx' && st.gain === 0.7 && (await G(() => window.__gymTapes.P.lid)) === lid && !st.paused, st);
  await page.click('#player .js-vol-ic'); await sleep(300); const muted = (await S()).gain;
  await page.click('#player .js-vol-ic'); await sleep(300);
  ok('the speaker button mutes it and brings it back', muted === 0 && (await S()).gain === 0.7, { muted });
  await setBar(100); st = await S();
  ok('back at full it stays on the same player for now, at full volume', st.el === 'audioFx' && st.gain === 1 && !st.paused, st);
  await page.click('.ctl [data-act="next"]'); await sleep(700); st = await S();
  ok('the next tap on play goes back to the plain player', st.el === 'audio' && !st.paused && !st.fx && st.title === 'Leg-day-beeps', st);

  await page.click('.ctl [data-act="toggle"]'); await sleep(200);
  await setBar(30); st = await S();
  ok('lowering it while paused does not start anything', st.paused, st);
  const t1 = st.t;
  await page.click('.ctl [data-act="toggle"]'); await sleep(700); st = await S();
  ok('pressing play then uses the processing at 30 percent, from the same spot', st.el === 'audioFx' && !st.paused && st.gain === 0.3 && st.t >= t1 && st.t < t1 + 2, { t1, st });
  ok('the heads-up is only shown once', await G(() => { const t = document.getElementById('toast'); return t.hidden || !/lock the phone/.test(t.textContent); }));

  // start delay with a lowered volume: the count-in plays on the same player, at the same volume
  await page.click('.ctl [data-act="toggle"]'); await sleep(200);
  await page.click('#tabSettings'); await page.click('[data-k="delay"][data-v="3"]'); await sleep(150); await page.click('#tabLibrary'); await page.click('#libUploads');
  await page.click('.ctl [data-act="toggle"]'); await sleep(400); st = await S();
  ok('the count-in plays through the processing at the lowered volume', st.count && st.el === 'audioFx' && st.gain === 0.3 && !st.paused, st);
  await page.waitForFunction(() => !window.__gymTapes.P.countIn, null, { timeout: 6000 }); await sleep(600); st = await S();
  ok('then the upload carries on, same player, same volume', !st.count && st.el === 'audioFx' && st.gain === 0.3 && !st.paused, st);
  await page.click('.ctl [data-act="toggle"]'); await sleep(200);
  await page.click('#tabSettings'); await page.click('[data-k="delay"][data-v="0"]'); await sleep(150);

  // the volume is remembered on this phone
  await page.reload(); await ready(); await sleep(600);
  ok('after a reload the bar is where it was left', (await page.locator('#player .js-vol').inputValue()) === '30' && (await G(() => window.__gymTapes.VOL.v)) === 0.3);
  await page.click('.ctl [data-act="toggle"]'); await sleep(800); st = await S();
  ok('and the first tap plays at that volume', st.el === 'audioFx' && !st.paused && st.gain === 0.3 && st.ctx === 'running', st);
  ok('no page errors', errors.length === 0, errors);
  await page.screenshot({ path: DIR + '/shots/b0-iphone-volume.png' });

  console.log(`\n${pass} passed, ${fail} failed`);
  await browser.close(); server.close();
})().catch(e => { console.error('TEST FAILED', e); process.exit(1); });
