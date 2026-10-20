// Test 19 (V14): the redesign (glass tab bar and mini player, quick picks and big covers, the bar shrinking while
// scrolling, swipes, gym mode, double-tap to like, drag down to close, the Glass effects switch, the computer's
// Now playing panel and full-screen player, thin scrollbars, the Settings search highlight fix), the EarWorm name, the
// first-open guide and sample beat, Name it, whether the library is protected, the backup nudge, cloud space in Recently deleted,
// the anonymous weekly count, crash reports to Sentry, the Help improve switch, Send feedback, and What's new.
const { chromium } = require('./pw.js');
const http = require('http'), fs = require('fs'), path = require('path');
const makeMock = require('./mocksb.js');
const DIR = __dirname;
const sleep = ms => new Promise(r => setTimeout(r, ms));
let pass = 0, fail = 0; const ok = (label, cond, extra) => { cond ? pass++ : fail++; console.log((cond ? 'PASS ' : 'FAIL ') + label + (extra !== undefined ? '  -> ' + JSON.stringify(extra) : '')); };
const server = http.createServer((req, res) => { res.writeHead(200, { 'content-type': 'text/html' }); res.end(fs.readFileSync(path.join(DIR, 'index.html'))); });
const mock = makeMock(), SB = 'https://pkibuxnxnirvjznmcnyo.supabase.co/**';
const allErrors = [], sentryHits = [];
const LIME = 'rgb(200, 241, 53)';

async function device(browser, name, o) {
  o = o || {};
  const ctx = await browser.newContext(Object.assign({ colorScheme: 'dark' }, o.pc ? { viewport: { width: 1440, height: 900 } } : { viewport: { width: 390, height: 844 }, deviceScaleFactor: 2, hasTouch: true }));
  await ctx.addInitScript(q => { window.HP_STANDALONE = true; if (q.quiet) window.__HP_QUIET = true; if (q.report) window.__HP_REPORT_TEST = true; try { localStorage.setItem('hp.syncAsked', '1'); } catch (e) { /* blank page */ } }, { quiet: o.quiet !== false, report: !!o.report });
  await ctx.route('https://o4512286113660928.ingest.us.sentry.io/**', route => { sentryHits.push({ url: route.request().url(), body: route.request().postData() }); route.fulfill({ status: 200, body: '{}' }); });
  await ctx.route(SB, route => mock.handle(route));
  const page = await ctx.newPage();
  page.on('pageerror', e => allErrors.push(name + ' pageerror: ' + e.message));
  page.on('console', m => { if (m.type() === 'error' && !/ERR_|Failed to load resource|MEDIA_ERR|PIPELINE|DEMUXER|NotSupported|CONNECTION_REFUSED/.test(m.text())) allErrors.push(name + ' console: ' + m.text()); });
  const G = (fn, a) => page.evaluate(fn, a);
  const D = {
    page, G,
    ready: () => page.waitForFunction(() => window.__gymTapes && window.__gymTapes.S.ready),
    add: async (files, n) => { await page.setInputFiles('#fileInput', files); await page.waitForFunction(k => window.__gymTapes.S.tracks.length === k && document.getElementById('upDot').hidden, n, { timeout: 120000 }); await sleep(300); },
    css: (sel, prop) => G(([s, p]) => { const e = document.querySelector(s); return e ? getComputedStyle(e)[p] : null; }, [sel, prop]),
    box: sel => G(s => { const e = document.querySelector(s); if (!e) return null; const b = e.getBoundingClientRect(); return { x: Math.round(b.x), y: Math.round(b.y), w: Math.round(b.width), h: Math.round(b.height) }; }, sel),
    // a finger: touch events with real Touch points
    touch: (sel, pts) => G(([s, ps]) => {
      const el = document.querySelector(s), t = (x, y) => new Touch({ identifier: 7, target: el, clientX: x, clientY: y });
      const fire = (type, x, y) => el.dispatchEvent(new TouchEvent(type, { bubbles: true, cancelable: true, touches: type === 'touchend' ? [] : [t(x, y)], changedTouches: [t(x, y)] }));
      fire('touchstart', ps[0][0], ps[0][1]); for (let i = 1; i < ps.length; i++) fire('touchmove', ps[i][0], ps[i][1]); const l = ps[ps.length - 1]; fire('touchend', l[0], l[1]);
    }, [sel, pts]),
    shot: n => page.screenshot({ path: DIR + '/shots/' + n + '.png' })
  };
  await page.goto('http://localhost:8797' + (o.path || '/')); await D.ready();
  return D;
}

(async () => {
  await new Promise(r => server.listen(8797, r));
  const browser = await chromium.launch({ args: ['--autoplay-policy=no-user-gesture-required'] });

  /* ===== phone: the floating glass tab bar and mini player ===== */
  const P = await device(browser, 'phone', { report: true });
  const VER = await P.G(() => window.__gymTapes.VERSION);   // V14, V14.1, V14.2...
  await P.add([DIR + '/media/two-tones.mp3', DIR + '/media/mono-low.wav', DIR + '/media/Leg-day-beeps.mp4', DIR + '/media/all-black.mp4'], 4);
  await P.page.click('#tabHome'); await sleep(300);
  const nav = await P.box('#nav'), navCss = await P.G(() => { const s = getComputedStyle(document.getElementById('nav')); return { blur: s.backdropFilter || s.webkitBackdropFilter, r: s.borderRadius }; });
  ok('the tab bar floats: off the edges, rounded, frosted glass', nav.x >= 10 && nav.x + nav.w <= 380 && nav.y + nav.h <= 844 - 10 && parseFloat(navCss.r) >= 30 && /blur/.test(navCss.blur), { nav, navCss });
  ok('Shuffle everything is EarWorm lime', (await P.css('[data-act="shuffle-all"]', 'backgroundColor')) === LIME);
  ok('headings use the rounded font', /rounded|Nunito/i.test(await P.css('.page-t', 'fontFamily')));
  await P.page.click('[data-act="shuffle-all"]'); await P.page.waitForFunction(() => !window.__gymTapes.audio.paused, null, { timeout: 15000 }).catch(() => {});
  await sleep(1500);
  const mini = await P.G(() => ({ mini: document.getElementById('player').classList.contains('mini'), prog: parseFloat(document.getElementById('pProg').style.width) || 0, line: getComputedStyle(document.querySelector('.mini-prog')).display }));
  ok('a fresh install starts on the mini player, with a progress line that moves', mini.mini && mini.line === 'block' && mini.prog > 0, mini);
  const pl = await P.box('#player .player-in');
  ok('the mini player floats just above the tab bar', pl && pl.y + pl.h <= nav.y && nav.y - (pl.y + pl.h) < 24, { pl, nav });

  /* swipe the mini player */
  const before = await P.G(() => window.__gymTapes.P.cur);
  await P.touch('#player .now-open', [[300, 760], [260, 760], [200, 760], [150, 762]]); await sleep(700);
  const after = await P.G(() => window.__gymTapes.P.cur);
  ok('swiping the mini player left skips to the next upload', after && after !== before, { before, after });
  ok('the end of the swipe is not also a tap that opens the big player', !(await P.G(() => window.__gymTapes.S.full)));

  /* Home: quick picks, then the big covers of what was played lately */
  for (let i = 0; i < 3; i++) { await P.page.click('#tabLibrary'); await sleep(200); await P.page.click('.list .row-hit >> nth=' + i); await sleep(500); }
  await P.page.click('#tabHome'); await sleep(400);
  const home = await P.G(() => {
    const v = document.getElementById('view'), rot = document.getElementById('rotGrid'), rec = document.getElementById('recentStrip');
    const heads = Array.from(v.querySelectorAll('.sec-h h3')).map(h => h.textContent);
    return { rot: rot ? rot.querySelectorAll('.rot').length : 0, rec: rec ? rec.querySelectorAll('.tile').length : 0, heads, rotFirst: rot && rec ? !!(rot.compareDocumentPosition(rec) & Node.DOCUMENT_POSITION_FOLLOWING) : false,
      cover: rec ? Math.round(rec.querySelector('.cover').getBoundingClientRect().width) : 0 };
  });
  ok('Home: quick picks (Your rotation) right under the buttons, then Recently played with big covers', home.rot >= 3 && home.rec >= 3 && home.rotFirst && home.heads.indexOf('Recently played') >= 0 && home.cover >= 130, home);
  await P.shot('v14-home');

  /* scrolling down with a finger shrinks the tab bar; back at the top it comes back */
  await P.G(() => { document.dispatchEvent(new TouchEvent('touchstart', { touches: [] })); window.scrollTo(0, 0); });
  await P.G(() => new Promise(r => { let y = 0; const step = () => { y += 60; window.scrollTo(0, y); if (y < 360) requestAnimationFrame(step); else setTimeout(r, 100); }; step(); }));
  const shrunk = await P.G(() => document.body.classList.contains('nav-min')); await sleep(450);
  const navMin = await P.box('#nav'), plMin = await P.box('#player .player-in');
  ok('scrolling down shrinks the tab bar to one round button with the mini player next to it', shrunk && navMin.w < 80 && plMin.x > navMin.x + navMin.w && Math.abs((plMin.y + plMin.h) - (navMin.y + navMin.h)) < 8, { shrunk, navMin, plMin });
  await P.shot('v14-home-scrolled');
  await P.G(() => { window.scrollTo(0, 0); document.dispatchEvent(new TouchEvent('touchend', { touches: [] })); }); await sleep(450);
  ok('back at the top the full tab bar returns', !(await P.G(() => document.body.classList.contains('nav-min'))));
  await P.G(() => { document.dispatchEvent(new TouchEvent('touchstart', { touches: [] })); window.scrollTo(0, 300); }); await P.G(() => new Promise(r => setTimeout(r, 50)));
  await P.G(() => { window.scrollTo(0, 420); }); await sleep(100);
  await P.page.click('#nav button[aria-selected="true"]'); await sleep(300);
  ok('tapping the shrunk bar opens it again', !(await P.G(() => document.body.classList.contains('nav-min'))));
  await P.G(() => { window.scrollTo(0, 0); document.dispatchEvent(new TouchEvent('touchend', { touches: [] })); }); await sleep(300);

  /* the big player: gym mode, double-tap to like, drag down to close */
  await P.page.click('#player .now-open'); await sleep(800);
  ok('tapping the mini player opens the big player', await P.G(() => window.__gymTapes.S.full && !document.getElementById('full').hidden));
  const fb = await P.css('#full', 'backgroundImage');
  ok('the big player takes its colors from the cover', /radial-gradient/.test(fb) && /hsl|rgb/.test(fb), fb.slice(0, 90));
  await P.page.click('#fCover'); await sleep(700);
  const gym = await P.G(() => ({ on: document.getElementById('full').classList.contains('gym'), ctl: getComputedStyle(document.querySelector('#full .ctl')).display, top: getComputedStyle(document.querySelector('.f-top')).display, line: getComputedStyle(document.querySelector('.gym-prog')).display, hint: document.querySelector('.gym-hint').textContent }));
  ok('one tap on the cover: gym mode, just the cover, the name and a thin line', gym.on && gym.ctl === 'none' && gym.top === 'none' && gym.line === 'block' && /show controls/.test(gym.hint), gym);
  await P.shot('v14-gym');
  await P.page.click('.f-title'); await sleep(300);
  ok('any tap brings the controls back', !(await P.G(() => document.getElementById('full').classList.contains('gym'))) && (await P.css('#full .ctl', 'display')) !== 'none');
  const curId = await P.G(() => window.__gymTapes.P.cur);
  await P.G(id => { const t = window.__gymTapes.S.tracks.find(x => x.id === id); if (t && t.liked) window.__gymTapes.toggleLike ? window.__gymTapes.toggleLike(id) : null; }, curId);
  await P.page.click('#fCover'); await sleep(120); await P.page.click('#fCover'); await sleep(250);
  const liked = await P.G(id => ({ liked: !!(window.__gymTapes.S.tracks.find(x => x.id === id) || {}).liked, burst: !!document.querySelector('#fCover .burst'), gym: document.getElementById('full').classList.contains('gym') }), curId);
  ok('two quick taps on the cover like it, with a heart burst, and no gym mode', liked.liked && liked.burst && !liked.gym, liked);
  await sleep(500);
  await P.touch('.f-top', [[195, 80], [195, 120], [195, 220], [195, 330]]); await sleep(500);
  ok('dragging the big player down far enough closes it', !(await P.G(() => window.__gymTapes.S.full)) && await P.G(() => document.getElementById('full').hidden));
  await P.page.click('#player .now-open'); await sleep(700);
  await P.touch('.f-top', [[195, 80], [195, 95], [195, 110]]); await sleep(500);
  ok('a short drag snaps back and stays open', await P.G(() => window.__gymTapes.S.full && !document.getElementById('full').hidden && !document.getElementById('full').style.transform));
  await P.page.click('[data-act="full-close"]'); await sleep(500);

  /* the Glass effects switch */
  await P.page.click('#tabSettings'); await sleep(300); await P.page.click('#set-look'); await sleep(300);
  ok('Look has a Glass effects switch, on', (await P.G(() => { const s = document.getElementById('sw-glass'); return s && s.getAttribute('aria-checked'); })) === 'true');
  await P.page.click('#sw-glass'); await sleep(300);
  const solid = await P.G(() => ({ cls: document.body.classList.contains('no-glass'), blur: getComputedStyle(document.getElementById('nav')).backdropFilter, opt: window.__gymTapes.S.opt.glass }));
  ok('turning it off makes the bars solid', solid.cls && (solid.blur === 'none' || !solid.blur) && solid.opt === false, solid);
  await P.page.click('#sw-glass'); await sleep(200);
  ok('and back on', !(await P.G(() => document.body.classList.contains('no-glass'))));
  await P.page.click('#setBack'); await sleep(200);
  await P.page.fill('#setQ', 'frosted'); await sleep(300);
  ok('searching "frosted" finds Glass effects', /Glass effects/.test(await P.G(() => (document.getElementById('setHits') || {}).textContent || '')));
  await P.page.fill('#setQ', ''); await sleep(200);

  /* ===== computer: the Now playing panel ===== */
  const C = await device(browser, 'pc', { pc: true });
  await C.add([DIR + '/media/two-tones.mp3', DIR + '/media/mono-low.wav', DIR + '/media/Leg-day-beeps.mp4', DIR + '/media/all-black.mp4'], 4);
  await C.page.click('#tabHome'); await sleep(200);
  const appW = (await C.box('#app')).w;
  await C.page.click('[data-act="play-all"]'); await C.page.waitForFunction(() => !window.__gymTapes.audio.paused, null, { timeout: 15000 }).catch(() => {}); await sleep(600);
  const np = await C.box('#player .player-in'), app2 = await C.box('#app'), npq = await C.G(() => document.querySelectorAll('#pQueue .row').length);
  ok('on a computer, Now playing is a panel down the right side, full height', np.x + np.w >= 1438 && np.w >= 320 && np.w <= 360 && np.h >= 896 && np.y <= 1, np);
  ok('the page makes room for it', app2.w <= appW - 300, { appW, app2 });
  ok('the panel has a big cover, the controls and Up next', (await C.box('#pCover .cover')).w >= 280 && await C.page.isVisible('#player .ctl .big') && npq >= 2, { npq });
  ok('the sidebar still runs the full height', (await C.box('#nav')).h >= 898);
  await C.shot('v14-pc-home');
  await C.page.click('#pQueue .row-hit >> nth=0'); await sleep(500);
  ok('Up next in the panel works (jumping to an upload)', (await C.G(() => document.querySelectorAll('#pQueue .row').length)) === npq - 1);
  await C.page.click('.np-head [data-act="full-open"]'); await sleep(600);
  const fs2 = await C.G(() => { const s = document.querySelector('.f-side'); return { sw: s.scrollWidth, cw: s.clientWidth, blur: getComputedStyle(s).backdropFilter }; });
  ok('the full-screen player: Up next in a glass panel with no sideways scrollbar', fs2.sw <= fs2.cw && /blur/.test(fs2.blur), fs2);
  await C.shot('v14-pc-full');
  // V14.1: play, the volume and the chips fit on the screen, down to small laptop screens
  const fits = [];
  for (const [w, h] of [[1440, 900], [1366, 768], [1280, 720]]) {
    await C.page.setViewportSize({ width: w, height: h }); await sleep(400);
    fits.push(await C.G(h => { const b = s => document.querySelector('#full ' + s).getBoundingClientRect(); return { h, play: Math.round(b('.ctl .big').bottom), vol: Math.round(b('.vol').bottom), scroll: document.getElementById('full').scrollTop }; }, h));
  }
  await C.page.setViewportSize({ width: 1440, height: 900 }); await sleep(300);
  ok('the full-screen player fits: play and the volume are on screen at 1440x900, 1366x768 and 1280x720 (V14.1)', fits.every(f => f.play <= f.h && f.vol <= f.h && f.scroll === 0), fits);
  await C.page.keyboard.press('Escape'); await sleep(400);
  const sb = await C.G(() => { const d = document.createElement('div'); d.style.cssText = 'position:fixed;width:100px;height:100px;overflow:scroll'; d.innerHTML = '<div style="height:500px"></div>'; document.body.appendChild(d); const w = d.offsetWidth - d.clientWidth; d.remove(); return w; });
  ok('scrollbars are thin on a computer (10px, since V14.2 without the browser\'s arrow buttons)', sb === 10, sb);

  /* Settings search: no section stays highlighted while searching */
  await C.page.click('#tabSettings'); await sleep(300);
  await C.page.click('#side-sound'); await sleep(200);
  await C.page.fill('#setQ', 'speed'); await sleep(300);
  const cur = await C.G(() => Array.from(document.querySelectorAll('.set-side button[aria-current="true"]')).map(b => b.textContent.trim()));
  ok('while searching, no section in the side list is highlighted', cur.length === 0, cur);
  await C.page.fill('#setQ', ''); await sleep(300);
  const cur2 = await C.G(() => Array.from(document.querySelectorAll('.set-side button[aria-current="true"]')).map(b => b.textContent.trim()));
  ok('clearing the search highlights the open section again', cur2.length === 1 && cur2[0] === 'Sound', cur2);


  /* ===== V14 chunk B: the name, the first-open guide, Name it, not losing uploads ===== */
  const brand = await P.G(() => ({ title: document.title, h1: document.querySelector('h1').textContent.trim(), side: document.querySelector('.nav-logo .brand-t').textContent }));
  ok('the name is EarWorm, one word, in the title, the header and the sidebar', brand.title === 'EarWorm' && brand.h1 === 'EarWorm' && brand.side === 'EarWorm', brand);
  const site = fs.readFileSync(path.join(DIR, '..', 'pwa', 'site', 'index.html'), 'utf8'), man = JSON.parse(fs.readFileSync(path.join(DIR, '..', 'pwa', 'site', 'manifest.webmanifest'), 'utf8'));
  ok('the home screen and computer app are named EarWorm', /<title>EarWorm<\/title>/.test(site) && /apple-mobile-web-app-title" content="EarWorm"/.test(site) && man.name === 'EarWorm' && man.short_name === 'EarWorm');
  ok('new authenticator setups say EarWorm', /issuer: 'EarWorm', friendly_name: 'EarWorm '/.test(site) && !/Ear Worm'/.test(site));

  const F = await device(browser, 'fresh', { quiet: false });
  await F.page.waitForSelector('#guide', { timeout: 5000 }).catch(() => {});
  let g = await F.G(() => ({ on: !!document.getElementById('guide'), t: (document.getElementById('guideTitle') || {}).textContent, dots: document.querySelectorAll('.g-dots i').length, skip: !!document.getElementById('guideSkip'), works: (document.querySelector('.g-works') || {}).textContent || '' }));
  ok('a first open with nothing uploaded shows the guide: step 1 of 3, with Skip', g.on && g.t === 'Save the video to your phone' && g.dots === 3 && g.skip, g);
  ok('the guide is for any video, not one app', /Screen recordings/.test(g.works) && /Voice memos/.test(g.works) && !/TikTok/i.test(await F.G(() => document.getElementById('guide').textContent)), g.works);
  await sleep(500); ok('the guide covers the screen (not see-through once it is in)', (await F.G(() => getComputedStyle(document.getElementById('guide')).opacity)) === '1');
  await F.shot('v14-guide-1');
  await F.page.click('#guideNext'); await sleep(200);
  ok('Next: step 2, uploading', (await F.G(() => document.getElementById('guideTitle').textContent)) === 'Upload it to EarWorm');
  await F.page.click('#guideNext'); await sleep(200);
  ok('Next: step 3, with Try the sample beat', (await F.G(() => document.getElementById('guideTitle').textContent)) === 'Loop it your way' && await F.page.isVisible('#guideSample'));
  await F.page.click('#guideSample');
  await F.page.waitForFunction(() => window.__gymTapes.S.tracks.length === 1 && !window.__gymTapes.audio.paused, null, { timeout: 60000 }).catch(() => {});
  await sleep(500);
  const smp = await F.G(() => { const g2 = window.__gymTapes, t = g2.S.tracks[0]; return { guide: !!document.getElementById('guide'), done: localStorage.getItem('hp.guided'), title: t && t.title, dur: t && t.dur, playing: !!t && g2.P.cur === t.id && !g2.audio.paused, tab: g2.S.tab, sheet: !document.getElementById('sheet').hidden }; });
  await sleep(1500); ok("a brand new person who tries the sample doesn't get the What's new popup (V14.1)", !(await F.G(() => !!document.getElementById('newsOk'))));
  ok('Try the sample beat: the guide closes for good, a Sample beat upload is made and starts playing on Home', !smp.guide && smp.done === '1' && smp.title === 'Sample beat' && smp.dur > 5 && smp.playing && smp.tab === 'home' && !smp.sheet, smp);
  await F.page.reload(); await F.ready(); await sleep(700);
  ok('after that, the guide does not come back on its own', !(await F.G(() => !!document.getElementById('guide'))));
  await F.page.click('#tabSettings'); await sleep(200); await F.page.click('#set-uploads'); await sleep(200);
  await F.page.click('#guideShow'); await sleep(200);
  ok('Settings, Uploads and videos: Show brings the guide back', await F.G(() => !!document.getElementById('guide')));
  await F.page.click('#guideSkip'); await sleep(200);
  ok('Skip closes it', !(await F.G(() => !!document.getElementById('guide'))));

  /* Name it */
  await F.page.setInputFiles('#fileInput', [DIR + '/media/two-tones.mp3']);
  await F.page.waitForSelector('#nameSave', { timeout: 60000 }).catch(() => {});
  await F.page.waitForFunction(() => document.activeElement && document.activeElement.id === 'renameInput', null, { timeout: 3000 }).catch(() => {});
  const ni = await F.G(() => ({ open: !document.getElementById('sheet').hidden, head: (document.querySelector('.nameit-t') || {}).textContent, val: (document.getElementById('renameInput') || {}).value, focus: document.activeElement && document.activeElement.id }));
  ok('one upload: the Name it box pops up, ready to type', ni.open && ni.head === 'Upload added' && ni.focus === 'renameInput', ni);
  ok('with no Upload added toast on top of it, the box already says it (V14.1)', !(await F.G(() => { const t = document.getElementById('toast'); return !t.hidden && /Upload added/.test(t.textContent); })));
  await F.shot('v14-name-it');
  await F.page.fill('#renameInput', 'Phonk leg day'); await F.page.click('#nameSave'); await sleep(400);
  ok('Save names it', await F.G(() => window.__gymTapes.S.tracks.some(t => t.title === 'Phonk leg day')));
  await F.page.setInputFiles('#fileInput', [DIR + '/media/mono-low.wav']);
  await F.page.waitForSelector('#nameSkip', { timeout: 60000 }).catch(() => {}); await F.page.click('#nameSkip'); await sleep(400);
  ok('Skip keeps the name it came with', await F.G(() => window.__gymTapes.S.tracks.length === 3 && window.__gymTapes.S.tracks.some(t => t.title === 'mono-low')));
  await F.page.click('#tabSettings'); await sleep(200); await F.page.click('#set-uploads'); await sleep(200); await F.page.click('#sw-nameIt'); await sleep(200);
  await F.page.setInputFiles('#fileInput', [DIR + '/media/Leg-day-beeps.mp4']);
  await F.page.waitForFunction(() => window.__gymTapes.S.tracks.length === 4 && document.getElementById('upDot').hidden, null, { timeout: 90000 }); await sleep(700);
  ok('with Name new uploads off, no box', await F.G(() => document.getElementById('sheet').hidden));

  /* is the library protected on this device, and the backup nudge */
  await F.G(() => { localStorage.setItem('hp.since', String(Date.now() - 40 * 86400000)); localStorage.removeItem('hp.lastBackup'); localStorage.removeItem('hp.nudgeLater'); });
  await F.page.reload(); await F.ready(); await sleep(500);
  await F.page.click('#tabSettings'); await sleep(300);
  const nd = await F.G(() => ({ on: !!document.getElementById('nudge'), text: (document.getElementById('nudge') || {}).textContent || '', lib: (document.querySelector('#set-library .sub') || {}).textContent || '' }));
  ok('not signed in, no backup in over a month: Settings asks to back up', nd.on && /not made a backup yet/.test(nd.text) && /only copy/.test(nd.text), nd);
  ok('the Library and storage row says whether this device protects the library', /Protected on this device|Not protected yet/.test(nd.lib), nd.lib);
  await F.shot('v14-settings-nudge');
  await F.page.click('#nudgeLater'); await sleep(300);
  ok('Not now hides it for two weeks', !(await F.G(() => !!document.getElementById('nudge'))) && (await F.G(() => +localStorage.getItem('hp.nudgeLater'))) > Date.now() + 13 * 86400000);
  await F.G(() => { localStorage.removeItem('hp.nudgeLater'); localStorage.setItem('hp.lastBackup', String(Date.now() - 3 * 86400000)); }); await F.page.click('#tabHome'); await sleep(200); await F.page.click('#tabSettings'); await sleep(300);
  ok('a recent backup: no nudge', !(await F.G(() => !!document.getElementById('nudge'))));
  await F.page.click('#set-library'); await sleep(300);
  const pr = await F.G(() => ({ t: (document.querySelector('#protectSub') || {}).textContent || '', btn: !!document.getElementById('protectBtn') }));
  ok('Library and storage explains it (and offers Protect when it is not)', /keeps your library|could clear the library/.test(pr.t) && (pr.btn === /could clear/.test(pr.t)), pr);

  /* cloud space sitting in Recently deleted */
  const cl = await F.G(() => {
    const g2 = window.__gymTapes, t = g2.S.tracks[0], old = { st: g2.SYNC.st, trash: g2.S.trash };
    g2.SYNC.st = Object.assign({}, old.st || {}, { up: new Set(g2.S.tracks.map(x => x.asset)) }); g2.S.trash = [t];
    const r = { text: g2.cloudText(), tb: g2.trashCloudBytes() };
    g2.SYNC.st = old.st; g2.S.trash = old.trash; return r;
  });
  ok('the cloud space line says how much of it is sitting in Recently deleted', /of 1 GB cloud space used, .+ of it in Recently deleted/.test(cl.text) && cl.tb > 0, cl);

  /* ===== V14 chunk C: tester tools ===== */
  const pg = mock.pings.slice();
  ok('once a week each device sends an anonymous count: a random id, the week, the version, phone or computer, nothing else', pg.length === 1 && /^[A-Za-z0-9]{8,64}$/.test(pg[0].device) && pg[0].week === await P.G(() => window.__gymTapes.isoWeek(new Date())) && pg[0].version === VER && pg[0].kind === 'phone' && Object.keys(pg[0]).length === 4, pg);
  await P.page.reload(); await P.ready(); await sleep(2200);
  ok('not twice in the same week', mock.pings.length === 1, mock.pings.length);
  await P.G(() => window.__gymTapes.report(new Error('V14 test crash'), 'test')); await sleep(400);
  const hit = sentryHits.find(h => /V14 test crash/.test(h.body || '')), lines = hit ? hit.body.trim().split('\n').map(l => JSON.parse(l)) : [];
  const ev = lines[2] || {};
  ok('a crash report goes to the EarWorm project in Sentry', !!hit && /\/api\/4512286125588480\/envelope\//.test(hit.url) && /sentry_key=cc25cb6e30f18962f6c732604894a377/.test(hit.url) && lines[1] && lines[1].type === 'event', hit && hit.url);
  ok('it says what broke and which version, and nothing about the person', ev.exception && ev.exception.values[0].value === 'V14 test crash' && ev.release === 'earworm@' + VER && ev.tags && ev.tags.device === 'phone' && !ev.user && !JSON.stringify(ev).match(/ip_address|email/), { release: ev.release, tags: ev.tags, user: ev.user });
  ok('and it tells Sentry not to keep the IP address', !!(ev.sdk && ev.sdk.settings && ev.sdk.settings.infer_ip === 'never'), ev.sdk);
  ok('with a stack trace Sentry can read', ev.exception && ev.exception.values[0].stacktrace.frames.length > 0 && ev.exception.values[0].stacktrace.frames.every(f => f.lineno > 0));
  await P.page.click('#tabSettings'); await sleep(300);
  const ab = await P.G(() => ({ sw: (document.getElementById('sw-improve') || {}).getAttribute && document.getElementById('sw-improve').getAttribute('aria-checked'), v: (document.getElementById('aboutVersion') || {}).textContent, sub: (document.querySelector('.about .sub') || {}).textContent }));
  ok('Settings: Help improve EarWorm is on, says what it sends, and shows the version', ab.sw === 'true' && /No names, no emails/.test(ab.sub) && ab.v === 'EarWorm ' + VER, ab);
  await P.shot('v14-settings');
  await P.page.click('#sw-improve'); await sleep(200);
  const before2 = sentryHits.length; await P.G(() => { window.__gymTapes.report(new Error('should not send'), 'test'); localStorage.removeItem('hp.pinged'); }); await sleep(300);
  await P.page.reload(); await P.ready(); await sleep(2200);
  ok('switched off: no crash reports and no count', sentryHits.length === before2 && mock.pings.length === 1, { hits: sentryHits.length - before2, pings: mock.pings.length });
  await P.page.click('#tabSettings'); await sleep(300); await P.page.click('#sw-improve'); await sleep(1200);
  ok('switched back on: the count is sent once (a repeat in the same week is ignored)', mock.pings.length === 1 && await P.G(() => localStorage.getItem('hp.pinged') === window.__gymTapes.isoWeek(new Date())));
  /* feedback */
  await P.page.click('#feedbackBtn'); await sleep(300);
  await P.page.click('#fbSend'); await sleep(150);
  ok('Send feedback: an empty message asks for something first', /Type something first/.test(await P.G(() => document.getElementById('fbMsg').textContent)));
  await P.page.fill('#fbText', 'Gym mode is fire'); await P.page.fill('#fbEmail', 'nope'); await P.page.click('#fbSend'); await sleep(150);
  ok('a bad email is caught before sending', /does not look right/.test(await P.G(() => document.getElementById('fbMsg').textContent)) && mock.feedback.length === 0);
  await P.page.fill('#fbEmail', 'tester@example.com'); await P.page.click('#fbSend'); await sleep(800);
  const fbk = mock.feedback[0] || {};
  ok('it sends the message (and the email for a reply), then says thanks', mock.feedback.length === 1 && fbk.message === 'Gym mode is fire' && fbk.email === 'tester@example.com' && fbk.version === VER && /Thanks, it is sent/.test(await P.G(() => document.getElementById('toast').textContent)), fbk);
  /* what's new */
  await P.page.click('#newsBtn'); await sleep(300);
  const nw = await P.G(() => ({ h: document.querySelector('#sheetPanel h2').textContent, n: document.querySelectorAll('.news li').length }));
  ok("What's new lists what changed in V14", nw.h === "What's new in V14" && nw.n >= 5, nw);
  await P.page.click('#newsOk'); await sleep(300);
  await F.G(() => localStorage.removeItem('hp.seenVersion')); await F.page.reload(); await F.ready();
  await F.page.waitForSelector('#newsOk', { timeout: 6000 }).catch(() => {});
  ok("after updating, someone who already uses the app sees What's new once", await F.G(() => !!document.getElementById('newsOk')));
  await F.page.click('#newsOk'); await sleep(300); await F.page.reload(); await F.ready(); await sleep(2200);
  ok('and not again', !(await F.G(() => !!document.getElementById('newsOk'))));

  ok('no page errors', allErrors.length === 0, allErrors);
  console.log(`\n${pass} passed, ${fail} failed`);
  await browser.close(); server.close();
})().catch(e => { console.error('TEST FAILED', e); console.log(allErrors); process.exit(1); });
