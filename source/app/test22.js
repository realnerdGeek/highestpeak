// Test 22 (V16): gym tools and the share card. Rest (the music dips, beeps count down, it comes back up, or jumps to
// the hype part, or pauses and resumes), +15 s, Skip, Stop; intervals (get ready, work, rest, rounds, done) with the dip
// during rests; Hype (the loudest stretch, looped); the countdown on the mini player; the row on computers; the share
// card for the month (a 1080x1920 picture to share or save); months counted for it; the streak flame.
const { chromium } = require('./pw.js');
const http = require('http'), fs = require('fs'), path = require('path');
const DIR = __dirname, M = DIR + '/media/';
const sleep = ms => new Promise(r => setTimeout(r, ms));
let pass = 0, fail = 0; const ok = (label, cond, extra) => { cond ? pass++ : fail++; console.log((cond ? 'PASS ' : 'FAIL ') + label + (extra !== undefined ? '  -> ' + JSON.stringify(extra) : '')); };
const server = http.createServer((req, res) => { res.writeHead(200, { 'content-type': 'text/html' }); res.end(fs.readFileSync(path.join(DIR, 'index.html'))); });
const allErrors = [];
async function device(browser, name, o) {
  const ctx = await browser.newContext(Object.assign({ colorScheme: 'dark', acceptDownloads: true }, o.pc ? { viewport: { width: 1440, height: 900 } } : { viewport: { width: 440, height: 956 }, deviceScaleFactor: 2, hasTouch: true }));
  await ctx.addInitScript(() => { window.HP_STANDALONE = true; window.__HP_QUIET = true; window.__HP_RT_OFF = true;
    // count the beeps the app schedules
    window.__beeps = 0; const C = window.AudioContext; if (C) { const make = C.prototype.createOscillator; C.prototype.createOscillator = function () { window.__beeps++; return make.call(this); }; }
    try { localStorage.setItem('hp.syncAsked', '1'); localStorage.setItem('hp.guided', '1'); localStorage.setItem('hp.seenVersion', 'V16'); } catch (e) { /* blank page */ } });
  const page = await ctx.newPage();
  page.on('pageerror', e => allErrors.push(name + ' pageerror: ' + e.message));
  page.on('console', m => { if (m.type() === 'error' && !/ERR_|Failed to load resource|MEDIA_ERR|PIPELINE|DEMUXER|NotSupported|CONNECTION_REFUSED/.test(m.text())) allErrors.push(name + ' console: ' + m.text()); });
  const G = (fn, a) => page.evaluate(fn, a);
  const D = { page, G, ctx,
    ready: () => page.waitForFunction(() => window.__gymTapes && window.__gymTapes.S.ready),
    until: (fn, a, ms) => page.waitForFunction(fn, a, { timeout: ms || 8000 }).then(() => true, () => false),
    add: async (files, n) => { await page.setInputFiles('#fileInput', files); await page.waitForFunction(k => window.__gymTapes.S.tracks.length === k && document.getElementById('upDot').hidden, n, { timeout: 120000 }); await sleep(300); },
    box: sel => G(s => { const e = document.querySelector(s); if (!e) return null; const b = e.getBoundingClientRect(); return { x: Math.round(b.x), y: Math.round(b.y), w: Math.round(b.width), h: Math.round(b.height), b: Math.round(b.bottom) }; }, sel),
    vol: () => G(() => { const g = window.__gymTapes; return Math.round(g.audio.volume * 100) / 100; }),
    abs: () => G(() => Math.round((window.__gymTapes.audio.currentTime || 0) * 10) / 10),
    shot: n => page.screenshot({ path: DIR + '/shots/' + n + '.png' })
  };
  await page.goto('http://localhost:8794/'); await D.ready();
  return D;
}

(async () => {
  await new Promise(r => server.listen(8794, r));
  const browser = await chromium.launch({ args: ['--autoplay-policy=no-user-gesture-required'] });
  const P = await device(browser, 'phone', {});
  ok('V16 or later', +String(await P.G(() => window.__gymTapes.VERSION)).replace(/^V/, '') >= 16);
  await P.add([M + 'Leg-day-beeps.mp4', M + 'all-black.mp4'], 2);
  await P.page.click('#tabLibrary'); await sleep(200); await P.page.click('.list .row-hit >> nth=0'); await P.until(() => !window.__gymTapes.audio.paused);
  await P.page.click('#player .now-open'); await sleep(900);
  const row = await P.G(() => [...document.querySelectorAll('#fGym button')].map(b => b.textContent || b.getAttribute('aria-label')));
  ok('the big player has a gym row: Hype, Rest 1:00, intervals 40/20 × 8, and the options', row.join('|') === 'Hype|Rest 1:00|40/20 × 8|Gym options', row);
  await P.shot('v16-phone-gym-row');

  /* ===== Hype ===== */
  const w = await P.G(() => { const g = window.__gymTapes, t = g.S.tracks.find(x => x.id === g.P.cur); return Object.assign(g.hypeWindow(t), { dur: t.dur }); });
  ok('Hype finds a stretch of up to 15 seconds inside the upload', w.b > w.a && w.b - w.a <= 15.1 && w.a >= 0 && w.b <= w.dur, w);
  await P.page.click('#fGym [data-act="hype"]'); await sleep(400);
  ok('tapping Hype jumps there and lights up', Math.abs((await P.abs()) - w.a) < 1 && (await P.page.getAttribute('#fGym [data-act="hype"]', 'aria-pressed')) === 'true', { at: await P.abs(), a: w.a });
  await P.G(b => { window.__gymTapes.audio.currentTime = b - 0.4; }, w.b); await sleep(1200);
  const looped = await P.abs();
  ok('and it loops that part: past the end it goes back to the start of it', looped >= w.a - 0.1 && looped < w.b, { looped, w });
  await P.page.click('#fGym [data-act="hype"]'); await sleep(300);
  ok('tapping again lets it play on', (await P.page.getAttribute('#fGym [data-act="hype"]', 'aria-pressed')) === 'false' && !(await P.G(() => window.__gymTapes.GYM.hype)));

  /* ===== Rest ===== */
  await P.page.click('#fGym [data-act="gym-opts"]'); await sleep(400);
  ok('the options: rest length, music while resting, when it is over, intervals, voice', await P.page.isVisible('[data-act="gym-set"][data-k="rest"][data-v="30"]') && await P.page.isVisible('[data-k="music"][data-v="pause"]') && await P.page.isVisible('[data-k="end"][data-v="hype"]') && await P.page.isVisible('[data-k="rounds"][data-v="12"]') && await P.page.isVisible('#sw-gymVoice'));
  await P.shot('v16-phone-gym-options');
  await P.page.click('[data-act="gym-set"][data-k="rest"][data-v="30"]'); await sleep(300);
  ok('picking 0:30 updates the Rest button', (await P.G(() => document.querySelector('#fGym [data-act="gym-rest"]').textContent)) === 'Rest 0:30');
  await P.page.click('#sheetPanel [data-act="sheet-close"]'); await sleep(400);
  const v0 = await P.vol(), b0 = await P.G(() => window.__beeps);
  await P.page.click('#fGym [data-act="gym-rest"]'); await sleep(500);
  let live = await P.G(() => ({ mode: window.__gymTapes.GYM.mode, label: (document.querySelector('#fGym .gym-l') || {}).textContent, time: (document.querySelector('#fGym .gym-t') || {}).textContent }));
  ok('Rest starts: the countdown shows in the big player', live.mode === 'rest' && live.label === 'Rest' && /^0:(30|29)$/.test(live.time), live);
  ok('the music dips to a quarter while resting', Math.abs((await P.vol()) - v0 * 0.25) < 0.03, { before: v0, now: await P.vol() });
  ok('four beeps are lined up: three short, one long at the end', (await P.G(() => window.__beeps)) - b0 === 4, (await P.G(() => window.__beeps)) - b0);
  await P.shot('v16-phone-rest');
  await P.page.click('#fGym [data-act="gym-more"]'); await sleep(300);
  ok('+15 s adds fifteen seconds', /^0:(45|44)$/.test(await P.G(() => document.querySelector('#fGym .gym-t').textContent)));
  await P.page.click('[data-act="full-close"]:visible'); await sleep(800);
  ok('the mini player shows the countdown too', /^Rest 0:4\d$/.test(await P.G(() => document.getElementById('pMeta').textContent)), await P.G(() => document.getElementById('pMeta').textContent));
  await P.page.click('#player .now-open'); await sleep(800);
  await P.page.click('#fGym [data-act="gym-skip"]'); await sleep(500);
  ok('Skip ends the rest: the music comes back up and it says go', !(await P.G(() => window.__gymTapes.GYM.mode)) && Math.abs((await P.vol()) - v0) < 0.02 && /Rest is over/.test(await P.G(() => document.getElementById('toast').textContent)));
  await P.page.click('#fGym [data-act="gym-opts"]'); await sleep(300); await P.page.click('[data-k="end"][data-v="hype"]'); await sleep(200); await P.page.click('#sheetPanel [data-act="sheet-close"]'); await sleep(300);
  await P.page.click('#fGym [data-act="gym-rest"]'); await sleep(400); await P.page.click('#fGym [data-act="gym-skip"]'); await sleep(600);
  const hy = await P.G(() => window.__gymTapes.GYM.hype);
  ok('with "Jump to the hype part", the end of the rest jumps there', !!hy && Math.abs((await P.abs()) - hy.a) < 1.2, { hy, at: await P.abs() });
  await P.page.click('#fGym [data-act="hype"]'); await sleep(200);
  await P.page.click('#fGym [data-act="gym-opts"]'); await sleep(300); await P.page.click('[data-k="end"][data-v="beep"]'); await P.page.click('[data-k="music"][data-v="pause"]'); await sleep(200); await P.page.click('#sheetPanel [data-act="sheet-close"]'); await sleep(300);
  await P.page.click('#fGym [data-act="gym-rest"]'); await sleep(400);
  ok('with "Pause", the music stops for the rest', await P.G(() => window.__gymTapes.audio.paused));
  await P.page.click('#fGym [data-act="gym-skip"]'); await sleep(800);
  ok('and plays again after it', await P.until(() => !window.__gymTapes.audio.paused, null, 3000));
  await P.page.click('#fGym [data-act="gym-opts"]'); await sleep(300); await P.page.click('[data-k="music"][data-v="dip"]'); await sleep(200); await P.page.click('#sheetPanel [data-act="sheet-close"]'); await sleep(300);
  await P.page.click('#fGym [data-act="gym-rest"]'); await sleep(300); await P.page.click('#fGym [data-act="gym-stop"]'); await sleep(300);
  ok('Stop ends it with the music back up, no toast about going', !(await P.G(() => window.__gymTapes.GYM.mode)) && Math.abs((await P.vol()) - v0) < 0.02);

  /* ===== intervals (shortened for the test: 3 s get ready, 2 s work, 1 s rest, 2 rounds) ===== */
  const b1 = await P.G(() => window.__beeps);
  await P.G(() => window.__gymTapes.gymStart('hiit', { work: 2, hrest: 1, rounds: 2 }));
  const seen = []; const t0 = Date.now();
  while (Date.now() - t0 < 9500) { const s = await P.G(() => ({ l: (document.querySelector('#fGym .gym-l') || {}).textContent || '', mode: window.__gymTapes.GYM.mode, v: Math.round(window.__gymTapes.audio.volume * 100) / 100 })); if (!seen.length || seen[seen.length - 1].l !== s.l) seen.push(s); if (!s.mode) break; await sleep(150); }
  const labels = seen.map(s => s.l);
  ok('intervals go: Get ready, Work round 1, Rest round 1, Work round 2, then done', JSON.stringify(labels.filter(Boolean)) === JSON.stringify(['Get ready', 'Work · Round 1 of 2', 'Rest · Round 1 of 2', 'Work · Round 2 of 2']) && !seen[seen.length - 1].mode, labels);
  const restV = (seen.find(s => /^Rest/.test(s.l)) || {}).v, workV = (seen.find(s => /^Work/.test(s.l)) || {}).v;
  ok('the music dips in the rest and is full while working', restV < workV * 0.4 && workV > 0.9 * v0, { restV, workV });
  ok('beeps before every change: 4 changes, 4 beeps each', (await P.G(() => window.__beeps)) - b1 === 16, (await P.G(() => window.__beeps)) - b1);
  ok('and it says it is done', /Intervals done/.test(await P.G(() => document.getElementById('toast').textContent)));

  /* ===== the share card ===== */
  await P.page.click('[data-act="full-close"]:visible'); await sleep(700);
  const ms = await P.G(() => { const g = window.__gymTapes, k = g.monthKey(); return { k, months: !!(g.ST.months && g.ST.months[k]), s: g.ST.months && g.ST.months[k] ? g.ST.months[k].s : 0, plays: g.ST.months && g.ST.months[k] ? Object.keys(g.ST.months[k].p).length : 0 }; });
  ok('listening counts into this month too (time and plays), for the card', ms.months && ms.s > 5 && ms.plays >= 1, ms);
  const card = await P.G(async () => { const g = window.__gymTapes, c = await g.shareCard(g.monthKey()), u = URL.createObjectURL(c.blob), im = new Image(); im.src = u; await im.decode(); return { w: im.naturalWidth, h: im.naturalHeight, size: c.blob.size, name: c.name, label: c.label }; });
  const MON = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'], now = new Date();
  ok('the month card is a 1080 by 1920 picture named after the month', card.w === 1080 && card.h === 1920 && card.size > 30000 && card.label === 'Your ' + MON[now.getMonth()] && card.name === 'EarWorm-' + MON[now.getMonth()] + '-' + now.getFullYear() + '.png', card);
  await P.G(() => { const g = window.__gymTapes, k = g.ST.days; const d = new Date(), key = d.getFullYear() + '-' + String(d.getMonth() + 1).padStart(2, '0') + '-' + String(d.getDate()).padStart(2, '0'); k[key] = k[key] || { s: 0, p: {} }; k[key].s = Math.max(k[key].s, 120); g.ST.total = Math.max(g.ST.total, 120); });
  await P.page.click('#tabLibrary'); await sleep(200); await P.page.click('#tabHome'); await sleep(400);
  ok('Home: the streak chip has the flame lit', !!(await P.page.$('.stat-chip.lit')));
  await P.page.click('.stat-chip.lit'); await sleep(500);
  ok('Stats has Share my month', await P.page.isVisible('#shareBtn'));
  await P.page.click('#shareBtn'); await P.page.waitForSelector('#sharePrev', { timeout: 8000 }).catch(() => {});
  const prev = await P.G(() => { const i = document.getElementById('sharePrev'); return i && { w: i.naturalWidth, picks: [...document.querySelectorAll('[data-act="share-pick"]')].map(b => b.textContent) }; });
  ok('the share sheet shows the card, this month and last month (the year only in December)', !!prev && prev.w === 1080 && prev.picks.length === (now.getMonth() === 11 ? 3 : 2) && prev.picks[0] === MON[now.getMonth()], prev);
  await P.shot('v16-phone-share');
  const dl = P.page.waitForEvent('download', { timeout: 5000 }).catch(() => null); await P.page.click('#shareSave'); const file = await dl;
  if (file) await file.saveAs(DIR + '/shots/v16-card.png');
  ok('Save downloads the picture', !!file && /^EarWorm-.*\.png$/.test(file.suggestedFilename()), file && file.suggestedFilename());
  const dl2 = P.page.waitForEvent('download', { timeout: 5000 }).catch(() => null); await P.page.click('#shareGo'); const file2 = await dl2;
  ok('Share falls back to saving where the browser cannot share pictures', !!file2);
  await P.page.click('[data-act="share-pick"] >> nth=1'); await P.page.waitForFunction(() => /^Your /.test((document.querySelector('#sheetPanel h2') || {}).textContent || '') && document.getElementById('sharePrev'), null, { timeout: 8000 }).catch(() => {});
  const last = new Date(now.getFullYear(), now.getMonth() - 1, 15);
  ok('last month makes its own card', (await P.G(() => document.querySelector('#sheetPanel h2').textContent)) === 'Your ' + MON[last.getMonth()]);
  await P.page.click('#sheetPanel [data-act="sheet-close"]'); await sleep(300);

  /* ===== computer: the row in the Now playing panel and in the full-screen player ===== */
  const C = await device(browser, 'pc', { pc: true });
  await C.add([M + 'Leg-day-beeps.mp4', M + 'two-tones.mp3'], 2);
  await C.page.click('#tabLibrary'); await sleep(200); await C.page.click('.list .row-hit >> nth=0'); await sleep(700);
  ok('computer: the gym row is in the Now playing panel', await C.page.isVisible('#pGym [data-act="gym-rest"]'));
  await C.page.click('.np-head [data-act="full-open"]'); await sleep(900);
  const lay = await C.G(() => { const b = s => document.querySelector('#full ' + s).getBoundingClientRect(); return { ctl: Math.round(b('.ctl').bottom), gym: Math.round(b('#fGym').top), gymB: Math.round(b('#fGym').bottom), side: Math.round(b('.f-side').top) }; });
  ok('and in the full-screen player, between the controls and Up next', lay.gym > lay.ctl && lay.gymB <= lay.side + 1, lay);
  await C.page.click('#fGym [data-act="gym-rest"]'); await sleep(400);
  ok('a rest on the computer shows its countdown there', await C.page.isVisible('#fGym .gym-live') && !!(await C.page.$('#pGym .gym-live')));
  await C.shot('v16-pc-rest');
  await C.page.click('#fGym [data-act="gym-stop"]'); await sleep(300);

  ok('no errors', !allErrors.length, allErrors.slice(0, 5));
  console.log(`\n${pass} passed, ${fail} failed`);
  await browser.close(); server.close();
  process.exit(fail ? 1 : 0);
})().catch(e => { console.error('TEST FAILED', e); process.exit(1); });
