// Test 13: the home screen version. Served from a sub-folder like GitHub Pages, on-device library, works offline, backup through the share sheet.
const { chromium } = require('./pw.js'); require('./legacy');
const http = require('http'), fs = require('fs'), path = require('path');
const DIR = __dirname, SITE = path.join(DIR, '..', 'pwa', 'site');
const sleep = ms => new Promise(r => setTimeout(r, ms));
let pass = 0, fail = 0; const ok = (label, cond, extra) => { cond ? pass++ : fail++; console.log((cond ? 'PASS ' : 'FAIL ') + label + (extra !== undefined ? '  -> ' + JSON.stringify(extra) : '')); };
const TYPES = { '.html': 'text/html', '.js': 'text/javascript', '.png': 'image/png', '.webmanifest': 'application/manifest+json' };
const server = http.createServer((req, res) => {
  let p = decodeURIComponent(req.url.split('?')[0]);
  if (!p.startsWith('/highestpeak/')) { res.writeHead(404); return res.end(); }
  p = p.slice('/highestpeak/'.length) || 'index.html';
  const f = path.join(SITE, p); if (!fs.existsSync(f)) { res.writeHead(404); return res.end(); }
  res.writeHead(200, { 'content-type': TYPES[path.extname(f)] || 'application/octet-stream' }); res.end(fs.readFileSync(f));
});
(async () => {
  await new Promise(r => server.listen(8790, r));
  const URL0 = 'http://localhost:8790/highestpeak/';
  const browser = await chromium.launch({ args: ['--autoplay-policy=no-user-gesture-required'] });
  const ctx = await browser.newContext({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 2, hasTouch: true, acceptDownloads: true });
  await ctx.addInitScript(() => { window.__shared = []; if (window.__fakeShare) return; });
  const page = await ctx.newPage(); const errors = [];
  page.on('pageerror', e => errors.push('pageerror: ' + e.message));
  page.on('console', m => { if (m.type() === 'error' && !/ERR_|Failed to load resource|ERR_INTERNET_DISCONNECTED/.test(m.text())) errors.push('console: ' + m.text()); });
  const G = (fn, a) => page.evaluate(fn, a);
  const ready = () => page.waitForFunction(() => window.__gymTapes && window.__gymTapes.S.ready);

  const man = await (await page.request.get(URL0 + 'manifest.webmanifest')).json();
  const icons = await Promise.all(man.icons.map(i => page.request.get(URL0 + i.src).then(r => r.status())));
  ok('the app manifest is valid, opens full screen, and every icon is there', man.display === 'standalone' && man.start_url === './' && man.name === 'Ear Worm' && icons.every(s => s === 200) && (await page.request.get(URL0 + 'apple-touch-icon.png')).status() === 200, { icons });

  await page.goto(URL0); await ready(); await sleep(300);
  let st = await G(() => ({ notice: !document.getElementById('notice').hidden, kind: window.__gymTapes && 'local', standalone: window.HP_STANDALONE === true, title: document.title, manifest: !!document.querySelector('link[rel=manifest]'), touch: !!document.querySelector('link[rel=apple-touch-icon]') }));
  ok('it opens with the library on the phone and no "not connected" warning', !st.notice && st.standalone && st.title === 'Ear Worm' && st.manifest && st.touch, st);
  const bar = await G(() => ({ style: document.querySelector('meta[name=apple-mobile-web-app-status-bar-style]').content, light: document.querySelector('meta[name=theme-color][media*=light]').content, dark: document.querySelector('meta[name=theme-color][media*=dark]').content, bg: getComputedStyle(document.documentElement).getPropertyValue('--bg').trim(), navGap: innerHeight - document.querySelector('nav').getBoundingClientRect().bottom }));
  ok('solid status bar in the page colours (avoids the iOS short-screen bug), tab bar flush with the bottom', bar.style === 'default' && bar.light === bar.bg && bar.dark === '#0A0A0D' && Math.abs(bar.navGap) < 1, bar);
  await page.waitForFunction(() => navigator.serviceWorker && navigator.serviceWorker.controller || false, null, { timeout: 10000 }).catch(() => {});
  if (!(await G(() => !!navigator.serviceWorker.controller))) { await page.reload(); await ready(); }
  ok('the offline helper is installed', await G(() => !!navigator.serviceWorker.controller));

  // move a library over with a backup from the Claude version
  const zip = path.join(DIR, 'out', 'four.zip');      // 4 uploads (two named Leg-day-beeps) and 1 playlist
  await page.click('#tabSettings'); await sleep(200);
  await page.setInputFiles('#backupInput', zip);
  await page.waitForFunction(() => /Restored/.test(document.getElementById('backupStatus').textContent), null, { timeout: 30000 }); await sleep(400);
  st = await G(() => ({ n: window.__gymTapes.S.tracks.length, pl: window.__gymTapes.S.playlists.length, status: document.getElementById('backupStatus').textContent, storage: document.getElementById('setStorage').textContent }));
  ok('a backup made in the Claude version restores into it', st.n === 4 && st.pl === 1 && /Restored 4 uploads and 1 playlist/.test(st.status), st);
  ok('Settings shows the phone storage used', /storage used/.test(st.storage), st.storage);
  await page.setInputFiles('#fileInput', DIR + '/media/all-black.mp4');
  await page.waitForFunction(() => window.__gymTapes.S.tracks.length === 5 && document.getElementById('upDot').hidden, null, { timeout: 30000 }); await sleep(300);
  ok('new uploads work too', true);
  await page.click('#tabLibrary'); await page.click('#libUploads'); await page.click('#trackList .row >> nth=1 >> .row-hit'); await sleep(800);
  st = await G(() => ({ t: window.__gymTapes.audio.currentTime, paused: window.__gymTapes.audio.paused, src: (window.__gymTapes.audio.getAttribute('src') || '').slice(0, 5) }));
  ok('uploads play from the phone', !st.paused && st.t > 0.2 && st.src === 'blob:', st);
  await page.click('.ctl [data-act="toggle"]'); await sleep(200);

  // no signal at all
  await ctx.setOffline(true);
  await page.reload(); await ready(); await sleep(500);
  st = await G(() => ({ n: window.__gymTapes.S.tracks.length, title: document.getElementById('pTitle').textContent }));
  ok('with no signal it still opens, with the whole library and the last upload ready', st.n === 5 && st.title.length > 0, st);
  await page.click('.ctl [data-act="toggle"]'); await sleep(800);
  st = await G(() => ({ t: window.__gymTapes.audio.currentTime, paused: window.__gymTapes.audio.paused }));
  ok('and it plays offline', !st.paused && st.t > 0.2, st);
  await page.click('.ctl [data-act="toggle"]'); await sleep(200);
  await ctx.setOffline(false);

  // backup with no share sheet: a normal download
  await page.click('#tabSettings'); await sleep(200);
  const [dl] = await Promise.all([page.waitForEvent('download', { timeout: 30000 }), page.click('#backupBtn').then(() => page.click('[data-act="bk-audio"]'))]);
  ok('Back up library downloads the file where there is no share sheet', /^EarWorm-backup-.*\.zip$/.test(dl.suggestedFilename()), dl.suggestedFilename());
  await page.close();

  // backup with a share sheet, like an iPhone: it is packed first, then a second tap opens the sheet
  const p2 = await ctx.newPage(); p2.on('pageerror', e => errors.push('pageerror: ' + e.message));
  await p2.addInitScript(() => { window.__shared = []; navigator.canShare = d => !!(d && d.files && d.files.length); navigator.share = d => { window.__shared.push(d.files.map(f => f.name + ':' + f.size + ':' + f.type)); return Promise.resolve(); }; });
  await p2.goto(URL0); await p2.waitForFunction(() => window.__gymTapes && window.__gymTapes.S.ready); await sleep(300);
  await p2.click('#tabSettings'); await sleep(150); await p2.click('#backupBtn'); await p2.click('[data-act="bk-video"]');      // the new upload kept its video, so it asks
  await p2.waitForSelector('#backupSave', { timeout: 30000 });
  const msg = await p2.textContent('#backupStatus');
  await p2.click('#backupSave'); await sleep(400);
  st = await p2.evaluate(() => ({ shared: window.__shared, status: document.getElementById('backupStatus').textContent, btn: !!document.getElementById('backupSave') }));
  ok('on an iPhone the backup goes out through the share sheet (Save to Files) on a second tap, videos included', /5 uploads, 1 video, .*Tap Save backup file/.test(msg) && st.shared.length === 1 && /^EarWorm-backup-.*\.zip:\d+:application\/zip$/.test(st.shared[0][0]) && /Backup saved/.test(st.status) && !st.btn, { msg, st });
  await p2.click('#tabLibrary'); await p2.click('#libUploads'); await p2.click('#trackList .row >> nth=0 >> .more'); await p2.click('[data-act="m-export"]'); await sleep(500);
  st = await p2.evaluate(() => window.__shared);
  ok('Save as a file uses the share sheet too', st.length === 2 && /\.m4a:\d+:audio\/mp4$/.test(st[1][0]), st);
  await p2.screenshot({ path: DIR + '/shots/c0-pwa.png' });
  ok('no page errors', errors.length === 0, errors);
  console.log(`\n${pass} passed, ${fail} failed`);
  await browser.close(); server.close();
})().catch(e => { console.error('TEST FAILED', e); process.exit(1); });
