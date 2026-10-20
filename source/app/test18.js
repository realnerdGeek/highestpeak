// Test 18 (V13): the Ear Worm name and logo (EarWorm, one word, since V14), the username in the greeting, selecting several uploads (Home, Library,
// long-press, Select all), quick settings, the settings search, and the computer app's icon shortcuts.
const { chromium } = require('./pw.js');
const http = require('http'), fs = require('fs'), path = require('path');
const { PNG } = (() => { try { return require('/opt/npm-tools/node_modules/pngjs'); } catch (e) { return {}; } })();
const makeMock = require('./mocksb.js');
const DIR = __dirname, SITE = path.join(DIR, '..', 'pwa', 'site');
const sleep = ms => new Promise(r => setTimeout(r, ms));
let pass = 0, fail = 0; const ok = (label, cond, extra) => { cond ? pass++ : fail++; console.log((cond ? 'PASS ' : 'FAIL ') + label + (extra !== undefined ? '  -> ' + JSON.stringify(extra) : '')); };
const server = http.createServer((req, res) => { res.writeHead(200, { 'content-type': 'text/html' }); res.end(fs.readFileSync(path.join(DIR, 'index.html'))); });
const mock = makeMock(), SB = 'https://pkibuxnxnirvjznmcnyo.supabase.co/**', PW = 'gym-tapes-1', EMAIL = 'matt@example.com';
const allErrors = [];

async function device(browser, name, o) {
  o = o || {};
  const ctx = await browser.newContext(o.pc ? { viewport: { width: 1440, height: 900 } } : { viewport: { width: 390, height: 844 }, deviceScaleFactor: 2 });
  await ctx.addInitScript(a => { window.HP_STANDALONE = true; window.__HP_QUIET = true; try { if (a) localStorage.setItem('hp.syncAsked', '1'); } catch (e) { /* blank page */ } }, !!o.asked);
  await ctx.route(SB, route => mock.handle(route));
  const page = await ctx.newPage();
  page.on('pageerror', e => allErrors.push(name + ' pageerror: ' + e.message));
  page.on('console', m => { if (m.type() === 'error' && !/ERR_|Failed to load resource|MEDIA_ERR|PIPELINE|DEMUXER|NotSupported|CONNECTION_REFUSED/.test(m.text())) allErrors.push(name + ' console: ' + m.text()); });
  const G = (fn, a) => page.evaluate(fn, a);
  const D = {
    page, G,
    ready: () => page.waitForFunction(() => window.__gymTapes && window.__gymTapes.S.ready),
    add: async (files, n) => { await page.setInputFiles('#fileInput', files); await page.waitForFunction(k => window.__gymTapes.S.tracks.length === k && document.getElementById('upDot').hidden, n, { timeout: 120000 }); await sleep(400); },
    text: sel => G(s => { const e = document.querySelector(s); return e ? e.textContent.trim() : null; }, sel),
    vis: sel => page.isVisible(sel),
    msg: re => page.waitForFunction(r => new RegExp(r).test((document.getElementById('authMsg') || {}).textContent || ''), re, { timeout: 15000 }),
    toastSays: re => page.waitForFunction(r => new RegExp(r).test(document.getElementById('toast').textContent) && !document.getElementById('toast').hidden, re, { timeout: 20000 }),
    shot: n => page.screenshot({ path: DIR + '/shots/' + n + '.png' })
  };
  await page.goto('http://localhost:8788' + (o.path || '/')); await D.ready();
  return D;
}

(async () => {
  await new Promise(r => server.listen(8788, r));
  const browser = await chromium.launch({ args: ['--autoplay-policy=no-user-gesture-required'] });

  /* ===== the name and logo ===== */
  const P = await device(browser, 'phone');
  await P.page.waitForSelector('#askNew', { timeout: 6000 }).catch(() => {});
  const inv = await P.G(() => ({ logo: !!document.querySelector('.ask-head .brand-ic svg'), text: document.getElementById('sheetPanel').textContent }));
  ok('the sync invite has the Ear Worm icon and name', inv.logo && /Or keep using EarWorm/.test(inv.text), inv);
  await P.page.click('#askLater'); await sleep(300);
  await P.add([DIR + '/media/two-tones.mp3', DIR + '/media/mono-low.wav', DIR + '/media/Leg-day-beeps.mp4'], 3);
  await P.page.click('#tabHome'); await sleep(300);
  const brand = await P.G(() => ({ title: document.title, h1: document.querySelector('h1').textContent.trim(), icon: !!document.querySelector('h1 .brand-ic svg'), worm: getComputedStyle(document.querySelector('h1 .brand-t b')).color, ear: getComputedStyle(document.querySelector('h1 .brand-t')).color, old: /HighestPeak/.test(document.body.innerText) }));
  ok('the page title and header say Ear Worm, with the sound wave icon, and HighestPeak is gone from the screen', brand.title === 'EarWorm' && brand.h1 === 'EarWorm' && brand.icon && !brand.old, brand);
  ok('in light mode "Worm" is the same dark ink as "Ear"', brand.worm === brand.ear, brand);
  await P.shot('v13-home-light');
  await P.page.emulateMedia({ colorScheme: 'dark' }); await sleep(200);
  const dark = await P.G(() => ({ worm: getComputedStyle(document.querySelector('h1 .brand-t b')).color, ear: getComputedStyle(document.querySelector('h1 .brand-t')).color }));
  ok('in dark mode "Ear" is white and "Worm" is lime', dark.worm === 'rgb(200, 241, 53)' && dark.ear === 'rgb(245, 245, 247)', dark);
  await P.shot('v13-home-dark');
  await P.page.emulateMedia({ colorScheme: 'light' });

  /* ===== select and delete on Home ===== */
  ok('Home has a Select button next to the greeting', await P.vis('#homeSelect') && (await P.text('#homeSelect')) === 'Select');
  await P.page.click('#homeSelect'); await sleep(250);
  const hs = await P.G(() => ({ t: document.querySelector('.page-t').textContent, rows: document.querySelectorAll('#homeSel .row').length, checks: document.querySelectorAll('#homeSel .check').length, count: document.getElementById('selCount').textContent }));
  ok('Select on Home lists every upload with a tick circle', hs.t === 'Select uploads' && hs.rows === 3 && hs.checks === 3 && hs.count === '0 selected', hs);
  await P.page.click('#homeSel .row:has-text("two-tones") .row-hit'); await P.page.click('#homeSel .row:has-text("mono-low") .row-hit'); await sleep(150);
  ok('tapping uploads ticks them, and Delete shows how many', (await P.text('#selCount')) === '2 selected' && (await P.text('#selDel')) === 'Delete 2' && (await P.G(() => window.__gymTapes.audio.paused)));
  await P.shot('v13-home-select');
  await P.page.click('#selAll'); await sleep(150);
  ok('Select all ticks every upload, and then reads Select none', (await P.text('#selCount')) === '3 selected' && (await P.text('#selAll')) === 'Select none');
  await P.page.click('#selAll'); await sleep(150);
  ok('Select none clears them', (await P.text('#selCount')) === '0 selected');
  await P.page.click('#homeSel .row:has-text("two-tones") .row-hit'); await P.page.click('#homeSel .row:has-text("mono-low") .row-hit');
  await P.page.click('#selDel'); await P.toastSays('Undo'); await sleep(300);
  ok('Delete removes them (with Undo) and Home goes back to normal', (await P.G(() => window.__gymTapes.S.tracks.length)) === 1 && !(await P.vis('#homeSel')) && await P.vis('#hello'));
  await P.page.click('[data-act="toast-act"]'); await P.page.waitForFunction(() => window.__gymTapes.S.tracks.length === 3, null, { timeout: 10000 });
  ok('(Undo brings them back)', true);
  // long-press
  const row = '.list .row:has-text("Leg-day-beeps") .row-hit';
  await P.page.hover(row); await P.page.mouse.down(); await sleep(650); await P.page.mouse.up(); await sleep(250);
  const lp = await P.G(() => ({ sel: window.__gymTapes.S.sel ? Array.from(window.__gymTapes.S.sel) : null, ids: window.__gymTapes.S.tracks.filter(t => t.title === 'Leg-day-beeps').map(t => t.id), cur: window.__gymTapes.P.cur, view: !!document.getElementById('homeSel') }));
  ok('long-pressing an upload starts selecting with it ticked, and does not play it', lp.view && lp.sel && lp.sel.length === 1 && lp.sel[0] === lp.ids[0] && !lp.cur, lp);
  await P.page.keyboard.press('Escape'); await sleep(200);
  ok('Escape (or Done) leaves select mode', !(await P.vis('#homeSel')));
  await P.page.click(row); await P.page.waitForFunction(() => !!window.__gymTapes.P.cur, null, { timeout: 8000 }).catch(() => {});
  ok('a normal tap still plays', !!(await P.G(() => window.__gymTapes.P.cur)) && !(await P.G(() => window.__gymTapes.S.sel)));
  await P.G(() => window.__gymTapes.audio.pause());

  /* ===== and in Library ===== */
  await P.page.click('#tabLibrary'); await P.page.click('#libUploads'); await sleep(200);
  ok('Library has a labeled Select button instead of the hidden icon', await P.vis('#libSelect') && (await P.text('#libSelect')) === 'Select');
  await P.page.click('#libSelect'); await P.page.click('#selAll'); await sleep(150);
  ok('Library select has Select all too', (await P.text('#selCount')) === '3 selected');
  await P.shot('v13-library-select');
  await P.page.click('[data-act="sel-done"]'); await sleep(150);
  ok('Done leaves it', !(await P.vis('#selCount')));

  /* ===== the username in the greeting ===== */
  await P.page.click('#tabHome'); await sleep(200);
  ok('signed out, the greeting has no name', /^(Good morning|Good afternoon|Good evening|Up late)$/.test(await P.text('#hello')), await P.text('#hello'));
  await P.page.click('#tabSettings'); await P.page.click('#set-account'); await P.page.click('#acctNew'); await P.page.fill('#authEmail', EMAIL); await P.page.fill('#authPw', PW); await P.page.click('#authGo');
  await P.msg('Check your email'); mock.confirm(EMAIL); await P.page.fill('#authPw', PW); await P.page.click('#authGo');
  await P.page.waitForSelector('#unameIn', { timeout: 30000 }); await P.page.fill('#unameIn', 'matt_w'); await P.page.click('#authGo'); await P.toastSays('@matt_w');
  await P.page.click('#tabHome'); await sleep(300);
  ok('signed in with a username, the greeting says it', /^(Good morning|Good afternoon|Good evening|Up late), matt_w$/.test(await P.text('#hello')), await P.text('#hello'));
  await P.shot('v13-greeting');

  /* ===== quick settings and the settings search (phone) ===== */
  await P.page.click('#tabSettings'); await sleep(250);
  const qs = await P.G(() => { const g = Array.from(document.querySelectorAll('.group')).find(x => /Quick settings/.test(x.textContent)); return g ? Array.from(g.querySelectorAll('.set-t')).map(e => e.textContent) : null; });
  ok('Settings opens with search and Quick settings (speed, start delay, stop timer) above the list', await P.vis('#setQ') && qs && qs.join() === 'Speed,Start delay,Stop timer' && await P.vis('#setList'), qs);
  await P.page.click('.group:has-text("Quick settings") [data-k="speed"][data-v="1.25"]'); await P.page.click('.group:has-text("Quick settings") [data-k="timer"][data-v="15"]'); await sleep(200);
  ok('quick settings work right there', (await P.G(() => window.__gymTapes.S.opt.speed)) === 1.25 && (await P.G(() => window.__gymTapes.T.at > 0)) && /Playback stops in about 15 min/.test(await P.page.textContent('.group:has-text("Quick settings") .card')));
  await P.page.click('.group:has-text("Quick settings") [data-k="timer"][data-v="0"]');
  await P.shot('v13-settings');
  await P.page.fill('#setQ', 'tiktok'); await sleep(200);
  const hits = await P.G(() => Array.from(document.querySelectorAll('#setHits .set-t')).map(e => e.textContent));
  ok('searching "tiktok" finds the end clip settings', hits.indexOf('Remove end clips') >= 0 && hits.indexOf('Check every upload for an end clip') >= 0 && !(await P.vis('#setList')), hits);
  await P.shot('v13-settings-search');
  await P.page.fill('#setQ', 'zzzz'); await sleep(150);
  ok('nothing matching says so', await P.vis('#setNone'));
  await P.page.fill('#setQ', 'password'); await sleep(150);
  ok('it finds account settings too', (await P.G(() => Array.from(document.querySelectorAll('#setHits .set-go')).map(e => e.textContent))).some(t => /^Password.*Account/.test(t)));
  await P.page.fill('#setQ', 'end clip'); await sleep(150);
  await P.page.click('#setHits .set-go:has-text("Remove end clips")'); await sleep(400);
  const found = await P.G(() => ({ page: document.querySelector('.page-t').textContent, back: !!document.getElementById('setBack'), flash: Array.from(document.querySelectorAll('.set.found')).map(s => s.querySelector('.set-t').textContent), q: window.__gymTapes.S.setQ }));
  ok('tapping a result opens its page and points at the setting', found.page === 'Uploads and videos' && found.back && found.flash.join() === 'Remove end clips' && found.q === '', found);
  await P.page.click('#tabHome'); await P.page.click('#tabSettings'); await sleep(200);
  await P.page.fill('#setQ', 'username'); await sleep(150); await P.page.click('#setHits .set-go:has-text("Username")'); await sleep(400);
  ok('"username" jumps to your username in Account', (await P.text('.page-t')) === 'Account' && (await P.G(() => !!document.querySelector('.set.found #acctUser'))));

  /* ===== the computer ===== */
  const C = await device(browser, 'pc', { pc: true, asked: true });
  await C.add([DIR + '/media/two-tones.mp3', DIR + '/media/mono-low.wav'], 2);
  ok('the computer sidebar shows the Ear Worm logo', (await C.text('.nav-logo .brand-t')) === 'EarWorm' && await C.vis('.nav-logo .brand-ic svg'));
  await C.page.click('#tabSettings'); await sleep(250);
  const side = await C.G(() => ({ first: document.querySelector('.set-side button').textContent, cur: document.querySelector('.set-side [aria-current="true"]').textContent, h: document.querySelector('#setMain .sec-t').textContent, speed: !!document.querySelector('#setMain [data-k="speed"]') }));
  ok('Settings on a computer opens on Quick settings, first in the side list', side.first === 'Quick settings' && side.cur === 'Quick settings' && side.h === 'Quick settings' && side.speed, side);
  await C.shot('v13-pc-settings');
  await C.page.fill('#setQ', 'fade'); await sleep(200);
  ok('the search box sits in the side list and shows results next to it', (await C.G(() => Array.from(document.querySelectorAll('#setHits .set-t')).map(e => e.textContent))).indexOf('Loop fade') >= 0);
  await C.shot('v13-pc-search');
  await C.page.click('#setHits .set-go:has-text("Loop fade")'); await sleep(400);
  ok('clicking a result opens that page with the setting pointed out', (await C.text('#setMain .sec-t')) === 'Sound' && (await C.G(() => Array.from(document.querySelectorAll('.set.found .set-t')).map(e => e.textContent).join())) === 'Loop fade');
  await C.page.click('#tabHome'); await sleep(250); await C.shot('v13-pc-home');
  // the icon shortcuts open the app at the right place
  const goTo = async q => { await C.page.goto('http://localhost:8788/' + q); await C.ready(); await sleep(600); return C.G(() => ({ tab: window.__gymTapes.S.tab, url: location.search, focus: document.activeElement && document.activeElement.id, playing: !!window.__gymTapes.P.cur, shuffle: window.__gymTapes.S.shuffle })); };
  let g = await goTo('?go=upload'); ok('the Upload shortcut opens Upload (and tidies the address)', g.tab === 'upload' && g.url === '', g);
  g = await goTo('?go=library'); ok('the Library shortcut opens Library', g.tab === 'library', g);
  g = await goTo('?go=search'); ok('the Search shortcut opens Search, ready to type', g.tab === 'search' && g.focus === 'q', g);
  g = await goTo('?go=shuffle'); ok('the Shuffle shortcut shuffles everything', g.playing && g.shuffle, g);

  /* ===== the home screen app files ===== */
  const man = JSON.parse(fs.readFileSync(path.join(SITE, 'manifest.webmanifest'), 'utf8'));
  ok('the app manifest is named Ear Worm and has the four icon shortcuts', man.name === 'EarWorm' && man.short_name === 'EarWorm' && man.shortcuts.map(s => s.url).join() === './?go=shuffle,./?go=upload,./?go=library,./?go=search', man.shortcuts);
  const site = fs.readFileSync(path.join(SITE, 'index.html'), 'utf8');
  ok('the home screen title is Ear Worm', /<title>EarWorm<\/title>/.test(site) && /apple-mobile-web-app-title" content="EarWorm"/.test(site));
  ok('the code sheet tells people an older authenticator entry may still say HighestPeak', /If you set it up before the name changed, it may be listed as HighestPeak/.test(site));
  if (PNG) {
    const png = PNG.sync.read(fs.readFileSync(path.join(SITE, 'apple-touch-icon.png'))), px = (x, y) => { const i = (png.width * y + x) << 2; return [png.data[i], png.data[i + 1], png.data[i + 2]]; };
    const corner = px(1, 1), mid = px(Math.round(png.width * 0.75), Math.round(png.height * 0.44));
    ok('the home screen icon is the dark square edge to edge with the lime worm', png.width === 180 && Math.abs(corner[0] - 23) < 4 && Math.abs(corner[2] - 31) < 4 && mid[1] > 200, { corner, mid });
  } else {
    const r = require('child_process').execFileSync('python3', ['-c', 'from PIL import Image;im=Image.open(' + JSON.stringify(path.join(SITE, 'apple-touch-icon.png')) + ').convert("RGB");print(im.size[0],*im.getpixel((1,1)),*im.getpixel((135,79)))']).toString().trim().split(' ').map(Number);
    ok('the home screen icon is the dark square edge to edge with the lime worm', r[0] === 180 && Math.abs(r[1] - 23) < 4 && Math.abs(r[3] - 31) < 4 && r[5] > 200, r);
  }

  ok('no page errors', allErrors.length === 0, allErrors);
  console.log(`\n${pass} passed, ${fail} failed`);
  await browser.close(); server.close();
})().catch(e => { console.error('TEST FAILED', e); console.log(allErrors); process.exit(1); });
