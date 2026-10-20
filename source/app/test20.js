// Test 20 (V14.2): the big player opens without a double take on phones, the computer's full-screen player is laid out
// like the approved mockup at every common screen size (and nothing scrolls behind it), scrollbars with no arrow buttons,
// the Tab bar setting (Full, Shrinks when scrolling, Always small), and the first-open guide for brand new accounts.
const { chromium } = require('./pw.js');
const http = require('http'), fs = require('fs'), path = require('path');
const makeMock = require('./mocksb.js');
const DIR = __dirname, M = DIR + '/media/';
const sleep = ms => new Promise(r => setTimeout(r, ms));
let pass = 0, fail = 0; const ok = (label, cond, extra) => { cond ? pass++ : fail++; console.log((cond ? 'PASS ' : 'FAIL ') + label + (extra !== undefined ? '  -> ' + JSON.stringify(extra) : '')); };
const server = http.createServer((req, res) => { res.writeHead(200, { 'content-type': 'text/html' }); res.end(fs.readFileSync(path.join(DIR, 'index.html'))); });
const mock = makeMock(), SB = 'https://pkibuxnxnirvjznmcnyo.supabase.co/**';
const allErrors = [];

async function device(browser, name, o) {
  o = o || {};
  const ctx = await browser.newContext(Object.assign({ colorScheme: 'dark' }, o.pc ? { viewport: o.vp || { width: 1920, height: 969 } } : { viewport: { width: 440, height: 956 }, deviceScaleFactor: 2, hasTouch: true }));
  await ctx.addInitScript(q => { window.HP_STANDALONE = true; if (q.quiet) window.__HP_QUIET = true; window.__HP_RT_OFF = true; window.__HP_KEEP_SILENCE = true; try { if (q.asked) localStorage.setItem('hp.syncAsked', '1'); localStorage.setItem('hp.seenVersion', 'V15'); } catch (e) { /* blank page */ } }, { quiet: o.quiet !== false, asked: o.asked !== false });
  await ctx.route('https://o4512286113660928.ingest.us.sentry.io/**', route => route.fulfill({ status: 200, body: '{}' }));
  await ctx.route(SB, route => mock.handle(route));
  const page = await ctx.newPage();
  page.on('pageerror', e => allErrors.push(name + ' pageerror: ' + e.message));
  page.on('console', m => { if (m.type() === 'error' && !/ERR_|Failed to load resource|MEDIA_ERR|PIPELINE|DEMUXER|NotSupported|CONNECTION_REFUSED/.test(m.text())) allErrors.push(name + ' console: ' + m.text()); });
  const G = (fn, a) => page.evaluate(fn, a);
  const D = {
    page, G, ctx,
    ready: () => page.waitForFunction(() => window.__gymTapes && window.__gymTapes.S.ready),
    add: async (files, n) => { await page.setInputFiles('#fileInput', files); await page.waitForFunction(k => window.__gymTapes.S.tracks.length === k && document.getElementById('upDot').hidden, n, { timeout: 120000 }); await sleep(300); },
    box: sel => G(s => { const e = document.querySelector(s); if (!e) return null; const b = e.getBoundingClientRect(); return { x: Math.round(b.x), y: Math.round(b.y), w: Math.round(b.width), h: Math.round(b.height), b: Math.round(b.bottom), r: Math.round(b.right) }; }, sel),
    min: () => G(() => document.body.classList.contains('nav-min')),
    // a finger scrolling: touchstart, then the page moves in steps
    scroll: (to, step) => G(([to, step]) => new Promise(r => { document.dispatchEvent(new TouchEvent('touchstart', { touches: [] })); let y = window.scrollY; const dir = to > y ? 1 : -1;
      const go = () => { y = dir > 0 ? Math.min(to, y + step) : Math.max(to, y - step); window.scrollTo(0, y); if (y !== to) requestAnimationFrame(go); else setTimeout(() => { document.dispatchEvent(new TouchEvent('touchend', { touches: [] })); r(); }, 80); }; go(); }), [to, step]),
    shot: n => page.screenshot({ path: DIR + '/shots/' + n + '.png' })
  };
  await page.goto('http://localhost:8796/'); await D.ready();
  return D;
}

(async () => {
  await new Promise(r => server.listen(8796, r));
  const browser = await chromium.launch({ args: ['--autoplay-policy=no-user-gesture-required'] });
  const files = [M + 'two-tones.mp3', M + 'mono-low.wav', M + 'Leg-day-beeps.mp4', M + 'all-black.mp4'];

  /* ===== phone: the big player opens once, no double take ===== */
  const P = await device(browser, 'phone');
  ok('this is V14.2 or later', /^V1[4-9]/.test(await P.G(() => window.__gymTapes.VERSION)));
  await P.add(files, 4);
  await P.page.click('#tabLibrary'); await sleep(200); await P.page.click('.list .row-hit >> nth=0'); await sleep(700);
  const track = () => P.G(() => { window.__log = []; const f = document.getElementById('full'), t0 = performance.now();
    const tick = () => { window.__log.push({ t: Math.round(performance.now() - t0), y: f.hidden ? null : Math.round(f.getBoundingClientRect().top), vt: document.documentElement.classList.contains('vt-on') }); if (performance.now() - t0 < 1200) requestAnimationFrame(tick); };
    requestAnimationFrame(tick); });
  await track(); await P.page.click('#player .now-open'); await sleep(1400);
  let log = await P.G(() => window.__log), shown = log.filter(x => x.y !== null);
  const usedVt = log.some(x => x.vt), back = shown.findIndex((x, i) => i && shown.slice(0, i).some(p => p.y < 5) && x.y > 40);
  ok('opening the big player: the cover grows into it once, and it never drops back down and slides up again', usedVt && back === -1 && shown.length && shown[shown.length - 1].y === 0, { usedVt, back: back >= 0 ? shown[back] : null, frames: shown.length });
  await P.page.click('[data-act="full-close"]:visible'); await sleep(800);
  await track(); await P.page.click('#player .now-open'); await sleep(1400);
  log = await P.G(() => window.__log); shown = log.filter(x => x.y !== null);
  ok('and the second time too', shown.findIndex((x, i) => i && shown.slice(0, i).some(p => p.y < 5) && x.y > 40) === -1 && shown[shown.length - 1].y === 0);
  await P.page.click('[data-act="full-close"]:visible'); await sleep(800);
  ok('closing still works', await P.G(() => document.getElementById('full').hidden));

  /* ===== the editor's start and end buttons (V14's backup reminder had borrowed their class name and stacked them) ===== */
  await P.page.click('#tabLibrary'); await sleep(200); await P.page.click('#trackList [data-act="menu"] >> nth=0'); await sleep(400); await P.page.click('[data-act="m-edit"]'); await sleep(900);
  const ed = await P.G(() => [...document.querySelectorAll('.nudge')].map(n => { const b = [...n.querySelectorAll('button')].map(x => x.getBoundingClientRect()); return { n: b.length, row: b.length === 2 && Math.abs(b[0].top - b[1].top) < 2, border: getComputedStyle(n).borderTopWidth }; }));
  ok('editor: the minus and plus buttons for start and end sit side by side, with no box around them', ed.length === 2 && ed.every(x => x.row && x.border === '0px'), ed);
  await P.page.click('[data-act="ed-close"]'); await sleep(500);

  /* ===== phone: the tab bar ===== */
  await P.page.click('#tabHome'); await sleep(300);
  await P.G(() => { const s = document.createElement('div'); s.id = 'pad'; s.style.height = '2400px'; document.getElementById('view').appendChild(s); });
  await P.G(() => window.scrollTo(0, 300)); await sleep(1400);           // moved there without a finger: nothing changes
  await P.scroll(315, 15);
  ok('Shrinks when scrolling is the default, and a small nudge (15px) does not flip it', (await P.G(() => window.__gymTapes.S.opt.nav)) === 'scroll' && !(await P.min()));
  await P.scroll(480, 40);
  ok('a real scroll down shrinks it', await P.min());
  await P.scroll(470, 5);
  ok('a few pixels back up does not bring it back', await P.min());
  await P.scroll(300, 40);
  ok('a real scroll up brings it back', !(await P.min()));
  await sleep(500);
  const mid = await P.G(() => new Promise(r => { document.body.classList.add('nav-min');
    setTimeout(() => { const b = [...document.querySelectorAll('#nav button')].map(x => Math.round(x.getBoundingClientRect().width)); document.body.classList.remove('nav-min'); r(b); }, 70); }));
  ok('it shrinks smoothly: part way through, the other tabs are still narrowing (not gone at once)', mid.filter(w => w > 2 && w < 60).length >= 2, mid);
  await P.G(() => { document.getElementById('pad').remove(); window.scrollTo(0, 0); }); await sleep(400);
  await P.page.click('#tabSettings'); await sleep(300); await P.page.click('[data-act="set-sec"][data-sec="look"]'); await sleep(300);
  const seg = await P.G(() => { const b = [...document.querySelectorAll('[data-k="nav"]')]; return { opts: b.map(x => x.textContent), on: (b.find(x => x.getAttribute('aria-checked') === 'true') || {}).textContent, fit: b.every(x => x.scrollWidth <= x.clientWidth + 1) }; });
  ok('Settings, Look has Tab bar: Full, On scroll (on), Small, and the three fit side by side', seg.opts.join('|') === 'Full|On scroll|Small' && seg.on === 'On scroll' && seg.fit, seg);
  await P.page.click('[data-k="nav"][data-v="small"]'); await sleep(500);
  ok('Always small: the tab bar is the round button right away, even at the top', await P.min());
  await P.page.click('#nav button[aria-selected="true"]'); await sleep(450);
  ok('tapping the round button opens the full bar (and stays on the same page)', !(await P.min()) && (await P.G(() => window.__gymTapes.S.tab)) === 'settings');
  await P.page.click('#tabHome'); await sleep(1000);
  ok('picking a tab goes there and tucks the bar back in', (await P.G(() => window.__gymTapes.S.tab)) === 'home' && await P.min());
  await P.page.click('#nav button[aria-selected="true"]'); await sleep(4500);
  ok('opened and left alone, it tucks back in after a few seconds', await P.min());
  await P.page.click('#nav button[aria-selected="true"]'); await sleep(300); await P.page.click('#tabSettings'); await sleep(900);
  await P.page.click('[data-act="set-sec"][data-sec="look"]').catch(() => {}); await sleep(300);
  await P.page.click('[data-k="nav"][data-v="full"]'); await sleep(400);
  await P.page.click('#tabHome'); await sleep(300);
  await P.G(() => { const s = document.createElement('div'); s.id = 'pad'; s.style.height = '2400px'; document.getElementById('view').appendChild(s); });
  await P.scroll(800, 40);
  ok('Full: scrolling never shrinks it', !(await P.min()));
  await P.G(() => { document.getElementById('pad').remove(); window.scrollTo(0, 0); window.__gymTapes.S.opt.nav = 'scroll'; }); await sleep(200);
  await P.shot('v142-phone-home');

  /* ===== computer: the full-screen player like the mockup ===== */
  const C = await device(browser, 'pc', { pc: true });
  await C.add(files, 4);
  await C.page.click('#tabLibrary'); await sleep(200); await C.page.click('.list .row-hit >> nth=0'); await sleep(700);
  await C.page.click('.np-head [data-act="full-open"]'); await sleep(900);
  const sizes = [];
  for (const [w, h] of [[2560, 1329], [1920, 969], [1470, 860], [1366, 657], [1280, 720], [1024, 700]]) {
    await C.page.setViewportSize({ width: w, height: h }); await sleep(450);
    sizes.push(await C.G(([w, h]) => { const b = s => document.querySelector('#full ' + s).getBoundingClientRect(), f = document.getElementById('full');
      const art = b('.f-art'), info = b('.f-info'), play = b('.ctl .big'), vol = b('.vol'), watch = b('.f-watch'), side = b('.f-side'), keys = b('.f-keys');
      return { w, h, coverLeft: art.right <= info.left, coverTall: Math.round(art.height), watchOnCover: watch.left >= art.left && watch.right <= art.right && watch.bottom <= art.bottom && watch.top >= art.top,
        playOk: play.bottom <= h && Math.abs(play.width - play.height) < 2, volOk: vol.bottom <= h && vol.width > 90, sideOk: side.height >= 80, keys: keys.bottom <= h && /Space plays and pauses/.test(document.querySelector('#full .f-keys').textContent),
        noScroll: f.scrollHeight <= f.clientHeight + 1, pageLocked: getComputedStyle(document.documentElement).overflow === 'hidden', usesWidth: (info.right - art.left) / w }; }, [w, h]));
    await C.shot('v142-pc-full-' + w);
  }
  const bad = sizes.filter(s => !(s.coverLeft && s.watchOnCover && s.playOk && s.volOk && s.sideOk && s.keys && s.noScroll && s.pageLocked && s.usesWidth > 0.6));
  ok('full-screen player at 2560x1329, 1920x969, 1470x860, 1366x657, 1280x720 and 1024x700: big cover on the left with Watch original on it; name, controls, volume, Up next and the keys hint on the right; everything on screen, nothing scrolls, nothing behind it scrolls', !bad.length, bad.length ? bad : sizes.map(s => s.w + ':' + s.coverTall));
  await C.page.setViewportSize({ width: 1920, height: 969 }); await sleep(300);
  await C.page.click('#fCover'); await sleep(900);
  const gym = await C.G(() => { const a = document.querySelector('#full .f-art').getBoundingClientRect(), t = document.querySelector('#full .f-title').getBoundingClientRect(); return { center: Math.abs((a.left + a.right) / 2 - innerWidth / 2) < 4, gap: Math.round(t.top - a.bottom) }; });
  ok('gym mode on a computer: the cover in the middle with the name right under it', gym.center && gym.gap >= 0 && gym.gap < 60, gym);
  await C.page.click('#fCover'); await sleep(400);
  await C.page.keyboard.press('Escape'); await sleep(600);
  ok('closed, the page scrolls again', (await C.G(() => getComputedStyle(document.documentElement).overflow)) !== 'hidden');
  // (this test browser hides scrollbars, so check the rules: the standard scrollbar properties, which make Chrome ignore
  // the EarWorm ones and draw its own with Windows arrow buttons, are not set; the arrow buttons are hidden)
  const bar = await C.G(() => { const rules = []; for (const s of document.styleSheets) { try { for (const r of s.cssRules) collect(r); } catch (e) { /* other origin */ } }
    function collect(r) { if (r.selectorText) rules.push(r.cssText); else if (r.cssRules && !(r.conditionText && /not selector/.test(r.conditionText))) [...r.cssRules].forEach(collect); }
    return { std: getComputedStyle(document.documentElement).scrollbarWidth, std2: getComputedStyle(document.querySelector('.f-side') || document.body).scrollbarWidth, thumb: rules.some(x => /::-webkit-scrollbar-thumb/.test(x)), noButtons: rules.some(x => /::-webkit-scrollbar-button/.test(x) && /display: none/.test(x)) }; });
  ok('computer scrollbars are the thin EarWorm ones with no arrow buttons, not the browser\'s own', bar.std === 'auto' && bar.std2 === 'auto' && bar.thumb && bar.noButtons, bar);

  /* ===== the first-open guide for a brand new account ===== */
  const N = await device(browser, 'new-person', { quiet: false, asked: false });
  await N.page.waitForSelector('#askNew', { timeout: 6000 }).catch(() => {});
  ok('a new person first sees the account invite, not the guide', !!(await N.page.$('#askNew')) && !(await N.page.$('#guide')));
  await N.page.click('#askNew'); await sleep(300);
  await N.page.fill('#authEmail', 'newbie@example.com'); await N.page.fill('#authPw', 'pass-1234'); await N.page.click('#authGo'); await sleep(600);
  mock.confirm('newbie@example.com');
  await N.page.fill('#authPw', 'pass-1234'); await N.page.click('#authGo');
  await N.page.waitForFunction(() => window.__gymTapes.SYNC && window.__gymTapes.SYNC.okAt, null, { timeout: 15000 }).catch(() => {});
  await N.page.waitForSelector('#unameIn', { timeout: 8000 }).catch(() => {});
  if (await N.page.$('#unameIn')) { await N.page.fill('#unameIn', 'newbie_1'); await sleep(500); await N.page.click('#authGo'); await sleep(800); }
  await N.page.waitForSelector('#guide', { timeout: 8000 }).catch(() => {});
  ok('after making an account and the first sync coming back empty, the guide shows', !!(await N.page.$('#guide')), await N.G(() => ({ signedIn: !!window.__gymTapes.SYNC.sess, sheet: !document.getElementById('sheet').hidden, n: window.__gymTapes.S.tracks.length })));
  await N.page.click('#guideSkip').catch(() => {}); await sleep(400);
  ok('skipping it is for good', (await N.G(() => [localStorage.getItem('hp.guided'), localStorage.getItem('hp.newAcct')])).join() === '1,');
  await N.add([M + 'two-tones.mp3'], 1); if (await N.page.$('#nameSkip')) { await N.page.click('#nameSkip'); await sleep(300); }
  await N.page.waitForFunction(() => !window.__gymTapes.SYNC.busy && window.__gymTapes.SYNC.okAt > Date.now() - 4000, null, { timeout: 20000 }).catch(() => {});
  await sleep(1500);
  const O = await device(browser, 'other-device', { quiet: false, asked: false });
  await O.page.waitForSelector('#askIn', { timeout: 6000 }).catch(() => {});
  await O.page.click('#askIn'); await sleep(300);
  await O.page.fill('#authEmail', 'newbie@example.com'); await O.page.fill('#authPw', 'pass-1234'); await O.page.click('#authGo');
  await O.page.waitForFunction(() => window.__gymTapes.S.tracks.length === 1, null, { timeout: 20000 }).catch(() => {});
  await sleep(1500);
  ok('signing in to an account that already has uploads, on another device, never shows the guide', !(await O.page.$('#guide')) && (await O.G(() => window.__gymTapes.S.tracks.length)) === 1);

  ok('no errors on any device', !allErrors.length, allErrors.slice(0, 5));
  console.log(`\n${pass} passed, ${fail} failed`);
  await browser.close(); server.close();
  process.exit(fail ? 1 : 0);
})().catch(e => { console.error('TEST FAILED', e); process.exit(1); });
