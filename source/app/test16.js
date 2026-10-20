// Test 16 (V11): accounts and sync. A "phone" and a "PC" (two separate browsers) share one account through a stand-in for Supabase.
const { chromium } = require('./pw.js'); require('./legacy');
const http = require('http'), fs = require('fs'), path = require('path');
const makeMock = require('./mocksb.js');
const DIR = __dirname, VT = path.join(DIR, '..', 'vtest');
const sleep = ms => new Promise(r => setTimeout(r, ms));
let pass = 0, fail = 0; const ok = (label, cond, extra) => { cond ? pass++ : fail++; console.log((cond ? 'PASS ' : 'FAIL ') + label + (extra !== undefined ? '  -> ' + JSON.stringify(extra) : '')); };
const server = http.createServer((req, res) => { res.writeHead(200, { 'content-type': 'text/html' }); res.end(fs.readFileSync(path.join(DIR, 'index.html'))); });
const mock = makeMock(); mock.state.autoProfile = true; const EMAIL = 'matt@example.com', PW = 'gym-tapes-1', SB = 'https://pkibuxnxnirvjznmcnyo.supabase.co/**';

async function device(browser, name) {
  const ctx = await browser.newContext({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 2 });
  await ctx.addInitScript(() => { window.HP_STANDALONE = true; });
  await ctx.route(SB, route => mock.handle(route));
  const page = await ctx.newPage(), errors = [];
  page.on('pageerror', e => errors.push(name + ' pageerror: ' + e.message));
  page.on('console', m => { if (m.type() === 'error' && !/ERR_|Failed to load resource|MEDIA_ERR|PIPELINE|DEMUXER|NotSupported|CONNECTION_REFUSED/.test(m.text())) errors.push(name + ' console: ' + m.text()); });
  const G = (fn, a) => page.evaluate(fn, a);
  const D = {
    ctx, page, errors, G,
    ready: () => page.waitForFunction(() => window.__gymTapes && window.__gymTapes.S.ready),
    T: title => G(t => { const x = window.__gymTapes.S.tracks.find(y => y.title === t); return x ? JSON.parse(JSON.stringify(x)) : null; }, title),
    titles: () => G(() => window.__gymTapes.S.tracks.map(t => t.title).sort()),
    add: async (files, n) => { await page.setInputFiles('#fileInput', files); await page.waitForFunction(k => window.__gymTapes.S.tracks.length === k && document.getElementById('upDot').hidden, n, { timeout: 120000 }); await sleep(400); },
    /* one full sync from this device, and wait for it to finish cleanly */
    sync: async () => {
      const t0 = await G(() => window.__gymTapes.SYNC.okAt);
      await G(() => window.__gymTapes.syncNow());
      await page.waitForFunction(t => { const s = window.__gymTapes.SYNC; return s.okAt > t && !s.busy && Object.keys(s.st.out).length === 0; }, t0, { timeout: 120000 });
      await sleep(300);
    },
    settings: async () => { await page.click('#tabSettings'); await sleep(200); },
    status: () => G(() => { const e = document.getElementById('syncStatus'); return e ? e.textContent : null; }),
    pls: () => G(() => window.__gymTapes.S.playlists.map(p => ({ name: p.name, tracks: (p.tracks || []).map(id => { const t = window.__gymTapes.S.tracks.find(x => x.id === id); return t ? t.title : '?'; }) })))
  };
  await page.goto('http://localhost:8784/'); await D.ready();
  return D;
}
async function signInUI(D, email, pw) {
  await D.settings(); await D.page.click('#acctIn'); await D.page.fill('#authEmail', email); await D.page.fill('#authPw', pw); await D.page.click('#authGo');
}

(async () => {
  await new Promise(r => server.listen(8784, r));
  const browser = await chromium.launch({ args: ['--autoplay-policy=no-user-gesture-required'] });

  /* ===== the phone: a library made before signing in ===== */
  const P = await device(browser, 'phone');
  await P.add([DIR + '/media/Leg-day-beeps.mp4', VT + '/tt-vp9.mp4'], 2);
  await P.G(async () => { const g = window.__gymTapes, ids = g.S.tracks.map(t => t.id); await g.store.set('playlists', 'plgym', { name: 'Gym', color: 'blue', tracks: ids.slice().reverse(), created: Date.now() }); await g.store.update('tracks', g.S.tracks.find(t => t.title === 'Leg-day-beeps').id, { liked: Date.now() }); });
  await P.settings();
  await P.page.click('[data-k="speed"][data-v="1.15"]'); await P.page.click('[data-k="delay"][data-v="5"]'); await sleep(200);
  ok('Settings shows Sync your library with Sign in and Create account when signed out', await P.page.isVisible('#acctIn') && await P.page.isVisible('#acctNew'));
  await P.page.screenshot({ path: DIR + '/shots/e0-account.png' });

  // create the account: a confirm email, then sign in
  await P.page.click('#acctNew'); await P.page.fill('#authEmail', EMAIL); await P.page.fill('#authPw', PW); await P.page.click('#authGo');
  await P.page.waitForFunction(() => /Check your email/.test(document.getElementById('authMsg') ? document.getElementById('authMsg').textContent : ''), null, { timeout: 15000 });
  ok('Create account sends a confirm email (back to the app) and says to check it', mock.mail.length === 1 && mock.mail[0].type === 'signup' && mock.mail[0].redirect === 'http://localhost:8784/', mock.mail);
  await P.page.fill('#authPw', PW); await P.page.click('#authGo');
  await P.page.waitForFunction(() => /Confirm your email first/.test(document.getElementById('authMsg').textContent), null, { timeout: 15000 });
  ok('signing in before confirming says to confirm first', true);
  mock.confirm(EMAIL);
  await P.page.fill('#authPw', 'wrong-pass'); await P.page.click('#authGo');
  await P.page.waitForFunction(() => /Wrong email or password/.test(document.getElementById('authMsg').textContent), null, { timeout: 15000 });
  ok('a wrong password says so', true);
  await P.page.fill('#authPw', PW); await P.page.click('#authGo');
  await P.page.waitForFunction(() => window.__gymTapes.SYNC.on && window.__gymTapes.SYNC.okAt > 0 && !window.__gymTapes.SYNC.busy, null, { timeout: 60000 }); await sleep(500);
  const uid = Array.from(mock.users.values())[0].id;
  let rows = mock.rows(uid), files = Array.from(mock.files.keys());
  const pTracks = await P.G(() => window.__gymTapes.S.tracks.map(t => ({ id: t.id, asset: t.asset, cover: t.cover || null, video: t.video ? t.video.parts : null, title: t.title })));
  ok('signed in, the phone\'s library goes up: both uploads, the playlist and the settings', rows.filter(r => r.coll === 'tracks').length === 2 && rows.some(r => r.coll === 'playlists' && r.data.name === 'Gym') && rows.some(r => r.coll === 'settings' && r.id === 'opts' && r.data.speed === 1.15), rows.map(r => r.coll + '/' + r.id));
  ok('their sound and covers go up into this account\'s own folder, the kept video does not (Sync videos is off)', pTracks.every(t => mock.files.has(uid + '/' + t.asset)) && files.every(f => f.indexOf(uid + '/') === 0) && pTracks.filter(t => t.video).every(t => t.video.every(v => !mock.files.has(uid + '/' + v))), files);
  await P.settings();
  ok('Settings shows the account, that it is synced, and the cloud space used', (await P.page.textContent('#acctEmail')) === EMAIL && /Synced just now/.test(await P.status()) && /of 1 GB cloud space used/.test(await P.page.textContent('#syncStorage')), { status: await P.status() });
  await P.page.screenshot({ path: DIR + '/shots/e1-signed-in.png' });

  /* ===== the PC: its own library, one upload the same file as the phone's, a playlist with the same name ===== */
  const C = await device(browser, 'pc');
  await C.add([DIR + '/media/Leg-day-beeps.mp4', DIR + '/media/two-tones.mp3'], 2);
  await C.G(async () => { const g = window.__gymTapes; await g.store.set('playlists', 'plpc', { name: 'gym', color: 'red', tracks: g.S.tracks.map(t => t.id), created: Date.now() }); });
  await signInUI(C, EMAIL, PW);
  await C.page.waitForFunction(() => window.__gymTapes.SYNC.on && window.__gymTapes.SYNC.okAt > 0 && !window.__gymTapes.SYNC.busy && window.__gymTapes.S.tracks.length >= 3, null, { timeout: 90000 }); await sleep(800);
  let titles = await C.titles(), pls = await C.pls();
  ok('the PC gets the phone\'s library, and the same file on both becomes one upload', JSON.stringify(titles) === JSON.stringify(['Leg-day-beeps', 'tt-vp9', 'two-tones']), titles);
  ok('playlists with the same name become one, with the uploads of both', pls.length === 1 && pls[0].name === 'Gym' && pls[0].tracks.length === 3 && pls[0].tracks.indexOf('two-tones') >= 0, pls);
  ok('the like and the speed came over, the start delay stayed this device\'s own', (await C.T('Leg-day-beeps')).liked > 0 && (await C.G(() => window.__gymTapes.S.opt.speed)) === 1.15 && (await C.G(() => window.__gymTapes.S.opt.delay)) === 0);
  const ctv = await C.T('tt-vp9');
  ok('uploads from the phone play here: their sound was downloaded', await C.G(id => window.__gymTapes.store.has(id), ctv.asset) && await C.G(id => window.__gymTapes.store.has(id), (await C.T('Leg-day-beeps')).asset));
  await C.page.click('#tabLibrary'); await C.page.click('#libUploads'); await C.page.click('#trackList .row:has(.title:text-is("tt-vp9")) .more'); await sleep(250);
  ok('the phone\'s kept video is not here (videos do not sync yet), so no Watch original on the PC', !(await C.page.isVisible('[data-act="m-watch"]')));
  await C.page.click('[data-act="sheet-close"]'); await sleep(200);
  await C.page.click('#trackList .row:has(.title:text-is("Leg-day-beeps")) .row-hit'); await sleep(900);
  ok('and the phone\'s upload plays on the PC', await C.G(() => !window.__gymTapes.audio.paused && window.__gymTapes.audio.currentTime > 0.2));
  await C.G(() => window.__gymTapes.audio.pause());

  // the phone catches up
  await P.sync();
  ok('the phone gets the PC\'s upload and the merged playlist', JSON.stringify(await P.titles()) === JSON.stringify(['Leg-day-beeps', 'tt-vp9', 'two-tones']) && (await P.pls())[0].tracks.length === 3 && (await P.G(() => window.__gymTapes.S.opt.delay)) === 5, { titles: await P.titles(), pls: await P.pls() });

  // edits go both ways
  await C.G(async () => { const g = window.__gymTapes; await g.store.update('tracks', g.S.tracks.find(t => t.title === 'two-tones').id, { title: 'Two Tones' }); });
  await C.sync(); await P.sync();
  ok('a rename on the PC shows up on the phone', !!(await P.T('Two Tones')));
  await P.G(async () => { const g = window.__gymTapes; await g.store.update('tracks', g.S.tracks.find(t => t.title === 'Two Tones').id, { liked: Date.now() }); });
  await P.sync(); await C.sync();
  ok('a like on the phone shows up on the PC', (await C.T('Two Tones')).liked > 0);

  /* ===== Recently deleted ===== */
  await P.page.click('#tabLibrary'); await P.page.click('#libUploads'); await P.page.click('#trackList .row:has(.title:text-is("tt-vp9")) .more'); await sleep(250); await P.page.click('[data-act="m-delete"]'); await sleep(300);
  await P.G(() => { document.getElementById('toast').hidden = true; }); await sleep(6700);
  ok('deleting puts the upload in Recently deleted on the phone', !(await P.T('tt-vp9')) && (await P.G(() => window.__gymTapes.S.trash.map(t => t.title))).join() === 'tt-vp9');
  await P.sync(); await C.sync();
  ok('and on the PC too, out of sight in its playlist', !(await C.T('tt-vp9')) && (await C.G(() => window.__gymTapes.S.trash.map(t => t.title))).join() === 'tt-vp9' && (await C.pls())[0].tracks.filter(t => t !== '?').length === 2, { trash: await C.G(() => window.__gymTapes.S.trash.map(t => t.title)), pls: await C.pls() });
  await C.settings(); ok('Settings shows it under Recently deleted', /1 upload, kept for 14 days/.test(await C.page.textContent('#binCount')));
  await C.page.click('#binBtn'); await sleep(300); await C.page.screenshot({ path: DIR + '/shots/e2-bin.png' });
  await C.page.click('[data-act="bin-restore"]'); await sleep(500);
  await C.sync(); await P.sync();
  ok('Put back on the PC brings it back on both, in its playlist too', !!(await P.T('tt-vp9')) && !!(await C.T('tt-vp9')) && (await P.pls())[0].tracks.length === 3);
  await C.page.click('[data-act="sheet-close"]').catch(() => {}); await sleep(200);

  // gone for good
  const leg = await P.T('Leg-day-beeps');
  await P.page.click('#tabLibrary'); await P.page.click('#libUploads'); await P.page.click('#trackList .row:has(.title:text-is("Leg-day-beeps")) .more'); await sleep(250); await P.page.click('[data-act="m-delete"]'); await sleep(300);
  await P.G(() => { document.getElementById('toast').hidden = true; }); await sleep(6700);
  await P.settings(); await P.page.click('#binBtn'); await sleep(300); await P.page.click('[data-act="bin-purge"]'); await sleep(200); await P.page.click('[data-act="bin-purge-go"]'); await sleep(800);
  await P.sync();
  ok('Delete for good removes it from the cloud, file and all', !mock.files.has(uid + '/' + leg.asset) && mock.rows(uid).some(r => r.id === leg.id && r.deleted));
  await C.sync();
  ok('and from the PC, including its downloaded copy, and from the playlist', !(await C.T('Leg-day-beeps')) && (await C.G(() => window.__gymTapes.S.trash.length)) === 0 && !(await C.G(id => window.__gymTapes.store.has(id), leg.asset)) && (await C.pls())[0].tracks.indexOf('Leg-day-beeps') < 0);

  /* ===== Sync videos ===== */
  await P.settings(); await P.page.click('#sw-syncVideo'); await sleep(300);
  await P.sync();
  const tvp = await P.T('tt-vp9');
  ok('with Sync videos on, the phone\'s kept video goes up', tvp.video.parts.every(v => mock.files.has(uid + '/' + v)));
  await C.sync();
  ok('the switch came over to the PC, and the video came down, so Watch original works there', (await C.G(() => window.__gymTapes.S.opt.syncVideo)) === true && await C.G(t => { const g = window.__gymTapes; return g.S.tracks.find(x => x.title === t).video.parts.every(id => g.store.has(id)); }, 'tt-vp9'));
  await C.page.click('#tabLibrary'); await C.page.click('#libUploads'); await C.page.click('#trackList .row:has(.title:text-is("tt-vp9")) .more'); await sleep(250);
  ok('Watch original shows on the PC now', await C.page.isVisible('[data-act="m-watch"]'));
  await C.page.click('[data-act="sheet-close"]'); await sleep(200);

  /* ===== no connection ===== */
  mock.state.down = true;
  await C.G(async () => { const g = window.__gymTapes; await g.store.update('tracks', g.S.tracks.find(t => t.title === 'Two Tones').id, { title: 'Two Tones (offline edit)' }); });
  await C.G(() => window.__gymTapes.syncNow()); await C.page.waitForFunction(() => !window.__gymTapes.SYNC.busy && window.__gymTapes.SYNC.err, null, { timeout: 30000 });
  await C.settings();
  ok('when the cloud can\'t be reached it says so, with what to do', /Can't reach your cloud library/.test(await C.status()), await C.status());
  ok('and the change waits here', (await C.G(() => Object.keys(window.__gymTapes.SYNC.st.out).length)) >= 1 && !!(await C.T('Two Tones (offline edit)')));
  await C.page.screenshot({ path: DIR + '/shots/e3-offline.png' });
  mock.state.down = false;
  await C.sync(); await P.sync();
  ok('back online, it goes up and reaches the phone', !!(await P.T('Two Tones (offline edit)')));

  /* ===== sign-ins that run out ===== */
  await P.G(() => { const s = window.__gymTapes.SYNC.sess; s.exp = Date.now(); });
  const oldAt = await P.G(() => window.__gymTapes.SYNC.sess.at);
  await P.sync();
  ok('an expiring sign-in renews itself quietly', (await P.G(() => window.__gymTapes.SYNC.sess.at)) !== oldAt && (await P.G(() => window.__gymTapes.SYNC.on)));
  await P.G(() => { const s = window.__gymTapes.SYNC.sess; s.exp = Date.now(); s.rt = 'no-longer-valid'; });
  await P.G(() => window.__gymTapes.syncNow()); await P.page.waitForFunction(() => !window.__gymTapes.SYNC.on, null, { timeout: 20000 }); await sleep(300);
  await P.settings();
  const so = { toast: await P.page.textContent('#toast'), btn: await P.page.isVisible('#acctIn'), titles: await P.titles() };
  ok('one that no longer works signs the device out and says so, keeping the library', /sign-in ran out/.test(so.toast) && so.btn && so.titles.length === 2, so);
  await signInUI(P, EMAIL, PW);
  await P.page.waitForFunction(() => window.__gymTapes.SYNC.on && window.__gymTapes.SYNC.okAt > 0 && !window.__gymTapes.SYNC.busy, null, { timeout: 60000 }); await sleep(500);
  ok('signing back in brings no duplicates', JSON.stringify(await P.titles()) === JSON.stringify(['Two Tones (offline edit)', 'tt-vp9']), await P.titles());

  /* ===== forgot password ===== */
  await P.settings(); await P.page.click('#acctOut'); await P.page.click('[data-act="acct-out-go"]'); await sleep(400);
  ok('Sign out keeps the uploads on the device', await P.page.isVisible('#acctIn') && (await P.titles()).length === 2 && !(await P.G(() => window.__gymTapes.SYNC.on)));
  await P.page.click('#acctIn'); await P.page.fill('#authEmail', EMAIL); await P.page.click('[data-act="acct-forgot"]'); await sleep(200);
  ok('Forgot password carries the email over', (await P.page.inputValue('#authEmail')) === EMAIL);
  await P.page.click('#authGo'); await P.page.waitForFunction(() => /reset link is on its way/.test(document.getElementById('authMsg').textContent), null, { timeout: 15000 });
  ok('it sends the reset email, back to the app', mock.mail.some(m => m.type === 'recovery' && m.to === EMAIL && m.redirect === 'http://localhost:8784/'));
  await P.page.goto('about:blank'); await P.page.goto('http://localhost:8784/' + mock.link(EMAIL, 'recovery')); await P.ready();      // the email link opens the app fresh
  await P.page.waitForSelector('form[data-form="newpw"]', { timeout: 15000 });
  ok('the reset link opened in a browser tab (as on iPhone) shows Set a new password without signing that tab in, link cleaned out of the address', !/access_token/.test(P.page.url()) && !(await P.G(() => !!window.__gymTapes.SYNC.sess)) && !(await P.G(() => window.__gymTapes.SYNC.on)));
  await P.page.fill('#authPw', 'brand-new-pass'); await P.page.click('#authGo'); await sleep(600);
  ok('the new password is saved, and it says to sign in in the app', Array.from(mock.users.values())[0].pw === 'brand-new-pass' && /Sign in with it in the EarWorm app/.test(await P.page.textContent('#toast')));
  await signInUI(P, EMAIL, 'brand-new-pass');
  await P.page.waitForFunction(() => window.__gymTapes.SYNC.on && window.__gymTapes.SYNC.okAt > 0 && !window.__gymTapes.SYNC.busy, null, { timeout: 60000 }); await sleep(500);
  ok('signing in with the new password works', (await P.titles()).length === 2);
  // a confirm link opened in a browser tab only confirms
  await P.page.goto('about:blank'); await P.page.goto('http://localhost:8784/' + mock.link(EMAIL, 'signup')); await P.ready(); await sleep(400);
  ok('a confirm link opened in a browser tab says to sign in in the app, and leaves the sign-in that was there alone', /Now sign in in the EarWorm app/.test(await P.page.textContent('#toast')) && (await P.G(() => window.__gymTapes.SYNC.on)));

  /* ===== 14 days in the bin ===== */
  await P.G(async () => { const g = window.__gymTapes, t = g.S.tracks.find(x => x.title === 'tt-vp9'); await g.store.update('tracks', t.id, { trashed: Date.now() - 15 * 86400000 }); });
  await sleep(2500);
  await P.page.reload(); await P.ready(); await P.page.waitForFunction(() => window.__gymTapes.S.trash.length === 0 && !window.__gymTapes.S.raw.tracks.some(t => t.title === 'tt-vp9'), null, { timeout: 15000 });
  ok('after 14 days in the bin an upload is gone for good by itself', true);
  await P.sync(); await C.sync();
  ok('everywhere', !(await C.T('tt-vp9')) && (await C.G(() => window.__gymTapes.S.trash.length)) === 0);

  /* ===== new accounts turned off ===== */
  mock.state.signupsOff = true;
  const X = await device(browser, 'stranger');
  await X.settings(); await X.page.click('#acctNew'); await X.page.fill('#authEmail', 'stranger@example.com'); await X.page.fill('#authPw', 'whatever1'); await X.page.click('#authGo');
  await X.page.waitForFunction(() => /New accounts are turned off/.test(document.getElementById('authMsg').textContent), null, { timeout: 15000 });
  ok('with sign-ups turned off, a stranger can not make an account', mock.users.size === 1);

  ok('every record in the cloud belongs to the account, every file is in its folder', Array.from(mock.docs.values()).every(r => r.user_id === uid) && Array.from(mock.files.keys()).every(f => f.indexOf(uid + '/') === 0));
  ok('no page errors', P.errors.length + C.errors.length + X.errors.length === 0, P.errors.concat(C.errors, X.errors));
  console.log(`\n${pass} passed, ${fail} failed`);
  await browser.close(); server.close();
})().catch(e => { console.error('TEST FAILED', e); process.exit(1); });
