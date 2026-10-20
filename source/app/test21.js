// Test 21 (V15): Play anywhere. A phone and a computer signed in to the same account share one private live channel
// (a stand-in for Supabase Realtime with the same rule as sql/v15.sql). Only one plays at a time; either one controls
// the one that is playing (play and pause, next, volume, scrub, what plays); playing moves between them at the same
// spot; another account can't join; a computer that isn't allowed to start sound says so; the switch turns it off.
const { chromium } = require('./pw.js');
const http = require('http'), fs = require('fs'), path = require('path'), crypto = require('crypto');
const makeMock = require('./mocksb.js'), makeRealtime = require('./mockrt.js');
const DIR = __dirname, M = DIR + '/media/';
const sleep = ms => new Promise(r => setTimeout(r, ms));
let pass = 0, fail = 0; const ok = (label, cond, extra) => { cond ? pass++ : fail++; console.log((cond ? 'PASS ' : 'FAIL ') + label + (extra !== undefined ? '  -> ' + JSON.stringify(extra) : '')); };
const server = http.createServer((req, res) => { res.writeHead(200, { 'content-type': 'text/html' }); res.end(fs.readFileSync(path.join(DIR, 'index.html'))); });
const mock = makeMock(), rt = makeRealtime(mock), SB = 'https://pkibuxnxnirvjznmcnyo.supabase.co/**';
const allErrors = [];
const EMAIL = 'matt@example.com', OTHER = 'someone@example.com';
function account(email, name) {
  const u = { id: crypto.randomUUID(), email, pw: 'pass-1234', confirmed: true }; mock.users.set(email, u); mock.profiles.set(u.id, name); return u;
}
async function device(browser, name, o) {
  const ctx = await browser.newContext(Object.assign({ colorScheme: 'dark' }, o.pc ? { viewport: { width: 1440, height: 900 } } : { viewport: { width: 440, height: 956 }, deviceScaleFactor: 2, hasTouch: true }));
  const s = mock.sessionFor(o.email), sess = { at: s.access_token, rt: s.refresh_token, exp: s.expires_at * 1000, uid: s.user.id, email: s.user.email };
  await ctx.addInitScript(q => { window.HP_STANDALONE = true; window.__HP_QUIET = true;
    try { if (!sessionStorage.getItem('t21')) { sessionStorage.setItem('t21', '1'); localStorage.setItem('hp.auth', JSON.stringify(q.sess)); localStorage.setItem('hp.devName', q.dev); }
      localStorage.setItem('hp.syncAsked', '1'); localStorage.setItem('hp.guided', '1'); localStorage.setItem('hp.seenVersion', 'V15'); } catch (e) { /* blank page */ } }, { sess, dev: o.dev });
  await ctx.route(SB, route => mock.handle(route));
  await ctx.route('https://o4512286113660928.ingest.us.sentry.io/**', route => route.fulfill({ status: 200, body: '{}' }));
  await rt.attach(ctx);
  const page = await ctx.newPage();
  page.on('pageerror', e => allErrors.push(name + ' pageerror: ' + e.message));
  page.on('console', m => { if (m.type() === 'error' && !/ERR_|Failed to load resource|MEDIA_ERR|PIPELINE|DEMUXER|NotSupported|CONNECTION_REFUSED/.test(m.text())) allErrors.push(name + ' console: ' + m.text()); });
  const G = (fn, a) => page.evaluate(fn, a);
  const D = { page, G, ctx, uid: s.user.id,
    ready: () => page.waitForFunction(() => window.__gymTapes && window.__gymTapes.S.ready),
    until: (fn, a, ms) => page.waitForFunction(fn, a, { timeout: ms || 8000 }).then(() => true, () => false),
    st: () => G(() => { const g = window.__gymTapes, t = g.S.tracks.find(x => x.id === g.P.cur); return { cur: g.P.cur, title: t && t.title, playing: !g.audio.paused, abs: Math.round((g.audio.currentTime || 0) * 10) / 10, vol: g.VOL.v, joined: g.RT.joined, active: g.RT.active, remote: g.RT.remote && { from: g.RT.remote.from, title: g.RT.remote.title, playing: g.RT.remote.playing }, devices: [...g.RT.devices.values()].map(d => d.name) }; }),
    shot: n => page.screenshot({ path: DIR + '/shots/' + n + '.png' })
  };
  await page.goto('http://localhost:8795/'); await D.ready();
  return D;
}

(async () => {
  await new Promise(r => server.listen(8795, r));
  const browser = await chromium.launch({ args: ['--autoplay-policy=no-user-gesture-required'] });
  const me = account(EMAIL, 'matt_w'); account(OTHER, 'someone');

  /* ===== the computer adds three uploads and syncs them; the phone signs in and gets them ===== */
  const C = await device(browser, 'pc', { pc: true, email: EMAIL, dev: 'Windows PC' });
  await C.page.setInputFiles('#fileInput', [M + 'two-tones.mp3', M + 'all-black.mp4', M + 'Leg-day-beeps.mp4']);
  await C.until(() => window.__gymTapes.S.tracks.length === 3 && document.getElementById('upDot').hidden, null, 60000);
  await C.until(() => !window.__gymTapes.SYNC.busy && window.__gymTapes.SYNC.okAt > 0, null, 20000);
  await C.G(() => window.__gymTapes.syncNow()); await C.until(() => !window.__gymTapes.SYNC.busy, null, 20000); await sleep(500);
  ok('V15', (await C.G(() => window.__gymTapes.VERSION)) === 'V15');
  const P = await device(browser, 'phone', { email: EMAIL, dev: 'iPhone' });
  ok('the phone gets the three uploads from the account', await P.until(() => window.__gymTapes.S.tracks.length === 3, null, 30000));
  const both = await P.until(() => window.__gymTapes.RT.joined && window.__gymTapes.RT.devices.size === 1, null, 10000) && await C.until(() => window.__gymTapes.RT.devices.size === 1, null, 5000);
  let c = await C.st(), p = await P.st();
  ok('both join the account\'s private live channel and see each other by name', both && c.joined && p.joined && c.devices.join() === 'iPhone' && p.devices.join() === 'Windows PC', { c: c.devices, p: p.devices });
  ok('the channel is the account\'s own: ew:<account id>, private', rt.online('realtime:ew:' + me.id).sort().join() === 'Windows PC,iPhone');
  ok('the Devices button shows once another device is online', await P.G(() => document.body.classList.contains('rt-devs')) && await C.G(() => document.body.classList.contains('rt-devs')));

  /* ===== the computer plays; the phone shows it and controls it ===== */
  await C.page.click('#tabLibrary'); await sleep(200); await C.page.click('.list .row-hit >> nth=0');
  await C.until(() => !window.__gymTapes.audio.paused, null, 8000);
  ok('on the computer, the Devices button sits in the Now playing panel', await C.page.isVisible('#player .np-head .rt-devbtn'));
  const shown = await P.until(() => document.body.classList.contains('rt-remote') && !document.getElementById('remote').hidden, null, 6000);
  c = await C.st(); p = await P.st();
  ok('the phone shows "Playing on Windows PC" with what is playing, in place of its own player', shown && p.remote && p.remote.title === c.title && p.remote.playing && !p.playing && /Playing on Windows PC/.test(await P.page.textContent('#remote')) && !(await P.page.isVisible('#player')), p.remote);
  await P.shot('v15-phone-remote');
  await P.page.click('#rtToggle');
  ok('pause on the phone pauses the computer', await C.until(() => window.__gymTapes.audio.paused, null, 4000));
  ok('and the phone shows Play', await P.until(() => /^Play on/.test(document.getElementById('rtToggle').getAttribute('aria-label')), null, 3000));
  await P.page.click('#rtToggle');
  ok('play on the phone plays the computer again', await C.until(() => !window.__gymTapes.audio.paused, null, 4000));
  const before = (await C.st()).cur; await P.page.click('#rtNext');
  ok('next on the phone skips on the computer', await C.until(b => window.__gymTapes.P.cur !== b, before, 4000));
  ok('and the phone follows along', await P.until(() => { const g = window.__gymTapes; return g.RT.remote && document.getElementById('rtTitle').textContent === g.RT.remote.title; }, null, 3000) && (await P.st()).remote.title === (await C.st()).title);
  await P.page.click('#remote .rt-open'); await sleep(400);
  ok('tapping the bar opens the full controls: scrub, volume, Play here, Devices, Up next', await P.page.isVisible('#sheetPanel #rtSeek') && await P.page.isVisible('#sheetPanel #rtVol') && await P.page.isVisible('#sheetPanel #rtHere') && await P.page.isVisible('#sheetPanel #rtDevs'));
  await P.shot('v15-phone-remote-sheet');
  await P.G(() => { const v = document.querySelector('#sheetPanel #rtVol'); v.value = 40; v.dispatchEvent(new Event('input', { bubbles: true })); });
  ok('the volume slider on the phone sets the computer\'s volume', await C.until(() => Math.abs(window.__gymTapes.VOL.v - 0.4) < 0.02, null, 3000), (await C.st()).vol);
  const half = await P.G(() => { const d = window.__gymTapes.RT.remote.dur, s = document.querySelector('#sheetPanel #rtSeek'); s.value = Math.round(d * 5); s.dispatchEvent(new Event('change', { bubbles: true })); return Math.round(d * 5) / 10; });
  ok('scrubbing on the phone moves the computer to that spot', await C.until(h => Math.abs((window.__gymTapes.audio.currentTime || 0) - h) < 1.2, half, 3000), { half, pc: (await C.st()).abs });
  await P.page.click('#sheetPanel [data-act="sheet-close"]'); await sleep(400);
  const pick = await P.G(() => { const g = window.__gymTapes; return g.S.tracks.find(t => t.id !== g.RT.remote.id).id; });
  await P.page.click('#tabLibrary'); await sleep(300); await P.page.click('#trackList .row[data-key="' + pick + '"] .row-hit').catch(() => P.page.click('.list .row-hit >> nth=2'));
  ok('picking an upload on the phone plays it on the computer, not on the phone', await C.until(id => window.__gymTapes.P.cur === id && !window.__gymTapes.audio.paused, pick, 5000) && !(await P.st()).playing);

  /* ===== Play here: it moves to the phone at the same spot ===== */
  await sleep(1500); const spot = (await C.st()).abs;
  await P.page.click('#remote .rt-open'); await sleep(400); await P.page.click('#sheetPanel #rtHere');
  const moved = await P.until(() => !window.__gymTapes.audio.paused, null, 6000);
  await sleep(600); c = await C.st(); p = await P.st();
  ok('Play here: the phone plays the same upload from about the same spot, and the computer stops', moved && p.cur === pick && Math.abs(p.abs - spot) < 2.5 && !c.playing, { spot, phone: p.abs, pc: c.playing });
  ok('now the computer shows "Playing on iPhone" in its panel', await C.until(() => document.body.classList.contains('rt-remote') && /Playing on iPhone/.test(document.getElementById('remote').textContent), null, 4000));
  await C.shot('v15-pc-remote');
  ok('and the phone is back to its own player', !(await P.G(() => document.body.classList.contains('rt-remote'))) && await P.page.isVisible('#player'));

  /* ===== Play here on the computer takes it back: the phone stops ===== */
  await C.page.click('#remote #rtHere'); await sleep(300);
  ok('Play here on the computer: it plays and the phone stops', await C.until(() => !window.__gymTapes.audio.paused, null, 6000) && await P.until(() => window.__gymTapes.audio.paused, null, 4000));
  ok('and the phone shows the computer again', await P.until(() => document.body.classList.contains('rt-remote'), null, 4000));

  /* ===== Devices: move it from the computer to the phone ===== */
  await C.page.click('#player .np-head .rt-devbtn'); await sleep(400);
  const rows = await C.G(() => [...document.querySelectorAll('#sheetPanel .dev-row')].map(r => r.textContent));
  ok('the Devices sheet lists this computer (playing) and the iPhone', rows.length === 2 && /This computer \(Windows PC\)/.test(rows[0]) && /Playing here/.test(rows[0]) && /iPhone/.test(rows[1]), rows);
  await C.shot('v15-pc-devices');
  const at = (await C.st()).abs;
  await C.page.click('#sheetPanel .dev-row:has-text("iPhone")');
  ok('tapping the iPhone moves playing there, same spot', await P.until(() => !window.__gymTapes.audio.paused, null, 6000) && await C.until(() => window.__gymTapes.audio.paused, null, 4000) && Math.abs((await P.st()).abs - at) < 3, { at, phone: (await P.st()).abs });

  /* ===== a computer that may not start sound yet says so ===== */
  await P.page.click('#player [data-act="toggle"]').catch(() => P.G(() => window.__gymTapes.audio.pause()));       // the phone pauses itself
  await sleep(300);
  await C.page.click('#remote #rtHere'); await C.until(() => !window.__gymTapes.audio.paused, null, 6000); await sleep(300);
  await P.until(() => document.body.classList.contains('rt-remote'), null, 4000);
  await P.page.click('#rtToggle'); await C.until(() => window.__gymTapes.audio.paused, null, 4000); await sleep(400);
  await C.G(() => { const orig = HTMLMediaElement.prototype.play; HTMLMediaElement.prototype.play = function () { HTMLMediaElement.prototype.play = orig; return Promise.reject(new DOMException('not allowed', 'NotAllowedError')); }; });
  await P.page.click('#rtToggle');
  ok('if the computer is not allowed to start sound, the phone says to click in EarWorm on it', await P.until(() => /needs one click in EarWorm/.test(document.getElementById('toast').textContent) && !document.getElementById('toast').hidden, null, 5000));

  /* ===== another account ===== */
  const X = await device(browser, 'other-account', { email: OTHER, dev: 'Not mine' });
  await X.until(() => window.__gymTapes.RT.joined, null, 8000);
  ok('another account gets its own channel and sees none of these devices', (await X.st()).devices.length === 0 && (await P.st()).devices.join() === 'Windows PC' && (await C.st()).devices.join() === 'iPhone');
  const sneak = await X.G(uid => new Promise(res => { const tok = JSON.parse(localStorage.getItem('hp.auth')).at, w = new WebSocket('wss://pkibuxnxnirvjznmcnyo.supabase.co/realtime/v1/websocket?apikey=x&vsn=1.0.0');
    w.onopen = () => w.send(JSON.stringify({ topic: 'realtime:ew:' + uid, event: 'phx_join', ref: '1', join_ref: '1', payload: { config: { private: true, presence: { key: 'sneak' }, broadcast: { self: false } }, access_token: tok } }));
    w.onmessage = e => { const m = JSON.parse(e.data); if (m.event === 'phx_reply') { res(m.payload.status); w.close(); } }; setTimeout(() => res('timeout'), 4000); }), me.id);
  ok('another account trying to join this account\'s channel is turned away', sneak === 'error', sneak);
  const pub = await X.G(uid => new Promise(res => { const w = new WebSocket('wss://pkibuxnxnirvjznmcnyo.supabase.co/realtime/v1/websocket?apikey=x&vsn=1.0.0');
    w.onopen = () => w.send(JSON.stringify({ topic: 'realtime:ew:' + uid, event: 'phx_join', ref: '1', join_ref: '1', payload: { config: { private: false } } }));
    w.onmessage = e => { const m = JSON.parse(e.data); if (m.event === 'phx_reply') { res(m.payload.status); w.close(); } }; setTimeout(() => res('timeout'), 4000); }), me.id);
  ok('and so is anyone trying it as a public channel', pub === 'error', pub);

  /* ===== Settings: the switch and the device name ===== */
  await P.page.click('#tabSettings'); await sleep(300); await P.page.click('[data-act="set-sec"][data-sec="account"]').catch(() => {}); await sleep(400);
  const acct = await P.G(() => ({ sw: (document.getElementById('sw-anywhere') || {}).getAttribute ? document.getElementById('sw-anywhere').getAttribute('aria-checked') : null, status: (document.getElementById('rtStatus') || {}).textContent }));
  ok('Account has Play anywhere (on) and This device: iPhone, online now: Windows PC', acct.sw === 'true' && /^iPhone\. Online now: Windows PC\./.test(acct.status || ''), acct);
  await P.shot('v15-phone-account');
  await P.page.click('#rtNameBtn'); await sleep(300); await P.page.fill('#rtNameIn', 'Matt iPhone'); await P.page.click('#rtNameSave'); await sleep(800);
  ok('renaming this device shows the new name on the computer', await C.until(() => [...window.__gymTapes.RT.devices.values()].some(d => d.name === 'Matt iPhone'), null, 4000));
  await P.page.click('#sw-anywhere'); await sleep(300);
  ok('turning Play anywhere off leaves the channel: the computer no longer sees the phone', await C.until(() => window.__gymTapes.RT.devices.size === 0, null, 6000) && !(await P.st()).joined);
  ok('and the phone stops showing the computer', !(await P.G(() => document.body.classList.contains('rt-remote'))));
  await P.page.click('#sw-anywhere'); await sleep(300);
  ok('turning it back on joins again', await P.until(() => window.__gymTapes.RT.joined, null, 8000) && await C.until(() => window.__gymTapes.RT.devices.size === 1, null, 6000));

  ok('no errors on any device', !allErrors.length, allErrors.slice(0, 5));
  console.log(`\n${pass} passed, ${fail} failed`);
  await browser.close(); server.close();
  process.exit(fail ? 1 : 0);
})().catch(e => { console.error('TEST FAILED', e); process.exit(1); });
