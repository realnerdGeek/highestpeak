// Test 17 (V12): the computer layout, Settings in sections, the sync invite, usernames, two-step sign-in,
// deleting the account and clearing one device. Several "devices" (separate browsers) share accounts through the Supabase stand-in.
const { chromium } = require('./pw.js');
const http = require('http'), fs = require('fs'), path = require('path'), crypto = require('crypto');
const makeMock = require('./mocksb.js');
const DIR = __dirname;
const sleep = ms => new Promise(r => setTimeout(r, ms));
let pass = 0, fail = 0; const ok = (label, cond, extra) => { cond ? pass++ : fail++; console.log((cond ? 'PASS ' : 'FAIL ') + label + (extra !== undefined ? '  -> ' + JSON.stringify(extra) : '')); };
const server = http.createServer((req, res) => { res.writeHead(200, { 'content-type': 'text/html' }); res.end(fs.readFileSync(path.join(DIR, req.url.startsWith('/v11') ? 'index-v11.html' : 'index.html'))); });
const mock = makeMock(), SB = 'https://pkibuxnxnirvjznmcnyo.supabase.co/**', PW = 'gym-tapes-1';
const EMAIL = 'matt@example.com', OLD = 'early@example.com', DEL = 'spare@example.com';
const allErrors = [];
const aalOf = at => { try { return JSON.parse(Buffer.from(String(at).split('.')[1], 'base64').toString()).aal; } catch (e) { return null; } };

async function device(browser, name, o) {
  o = o || {};
  const ctx = await browser.newContext(o.pc ? { viewport: { width: 1440, height: 900 } } : { viewport: { width: 390, height: 844 }, deviceScaleFactor: 2 });
  await ctx.addInitScript(a => { window.HP_STANDALONE = true; try { if (a.asked) localStorage.setItem('hp.syncAsked', '1'); if (a.auth && !sessionStorage.getItem('t17')) { localStorage.setItem('hp.auth', JSON.stringify(a.auth)); sessionStorage.setItem('t17', '1'); } } catch (e) { /* blank page */ } }, { asked: !!o.asked, auth: o.auth || null });
  await ctx.route(SB, route => mock.handle(route));
  const page = await ctx.newPage();
  page.on('pageerror', e => allErrors.push(name + ' pageerror: ' + e.message));
  page.on('console', m => { if (m.type() === 'error' && !/ERR_|Failed to load resource|MEDIA_ERR|PIPELINE|DEMUXER|NotSupported|CONNECTION_REFUSED/.test(m.text())) allErrors.push(name + ' console: ' + m.text()); });
  const G = (fn, a) => page.evaluate(fn, a);
  const D = {
    ctx, page, G,
    ready: () => page.waitForFunction(() => window.__gymTapes && window.__gymTapes.S.ready),
    titles: () => G(() => window.__gymTapes.S.tracks.map(t => t.title).sort()),
    add: async (files, n) => { await page.setInputFiles('#fileInput', files); await page.waitForFunction(k => window.__gymTapes.S.tracks.length === k && document.getElementById('upDot').hidden, n, { timeout: 120000 }); await sleep(400); },
    synced: () => page.waitForFunction(() => { const s = window.__gymTapes.SYNC; return s.on && s.okAt > 0 && !s.busy && s.st && Object.keys(s.st.out).length === 0; }, null, { timeout: 90000 }),
    sync: async () => {
      const t0 = await G(() => window.__gymTapes.SYNC.okAt);
      await G(() => window.__gymTapes.syncNow());
      await page.waitForFunction(t => { const s = window.__gymTapes.SYNC; return s.okAt > t && !s.busy && Object.keys(s.st.out).length === 0; }, t0, { timeout: 90000 }); await sleep(300);
    },
    section: async k => { await page.click('#tabSettings'); await sleep(150); if (!(await G(() => window.__gymTapes.isPC()))) { await page.click('#set-' + k); } else await page.click('#side-' + k); await sleep(200); },
    msg: re => page.waitForFunction(r => new RegExp(r).test((document.getElementById('authMsg') || {}).textContent || ''), re, { timeout: 15000 }),
    toastSays: re => page.waitForFunction(r => new RegExp(r).test(document.getElementById('toast').textContent) && !document.getElementById('toast').hidden, re, { timeout: 20000 }),
    sheetOpen: () => G(() => !document.getElementById('sheet').hidden),
    shot: n => page.screenshot({ path: DIR + '/shots/' + n + '.png' })
  };
  await page.goto('http://localhost:8786' + (o.path || '/')); await D.ready();
  return D;
}
async function signIn(D, email) { await D.section('account'); await D.page.click('#acctIn'); await D.page.fill('#authEmail', email); await D.page.fill('#authPw', PW); await D.page.click('#authGo'); }
async function makeAccount(D, email) {
  await D.section('account'); await D.page.click('#acctNew'); await D.page.fill('#authEmail', email); await D.page.fill('#authPw', PW); await D.page.click('#authGo');
  await D.msg('Check your email'); mock.confirm(email); await D.page.fill('#authPw', PW); await D.page.click('#authGo');
}

(async () => {
  await new Promise(r => server.listen(8786, r));
  const browser = await chromium.launch({ args: ['--autoplay-policy=no-user-gesture-required'] });

  /* ===== the phone: the sync invite, once per device ===== */
  const P = await device(browser, 'phone');
  await P.page.waitForSelector('#askNew', { timeout: 6000 }).catch(() => {});
  const inv = await P.G(() => ({ text: document.getElementById('sheetPanel').textContent, n: !!document.getElementById('askNew'), i: !!document.getElementById('askIn'), l: !!document.getElementById('askLater') }));
  ok('a new visitor gets the sync invite: Create account, Sign in, Not now', /Sync your library across your devices/.test(inv.text) && inv.n && inv.i && inv.l, inv);
  await P.shot('v12-invite');
  await P.page.click('#askLater'); await sleep(400);
  ok('Not now closes it', !(await P.sheetOpen()));
  await P.page.reload(); await P.ready(); await sleep(1600);
  ok('it does not come back on the same device', !(await P.sheetOpen()));

  /* ===== Settings in sections, on the phone ===== */
  await P.add([DIR + '/media/two-tones.mp3', DIR + '/media/Leg-day-beeps.mp4'], 2);
  await P.page.click('#tabSettings'); await sleep(250);
  const rows = await P.G(() => Array.from(document.querySelectorAll('#setList .set-go .set-t')).map(e => e.textContent));
  ok('Settings opens to a list of sections', rows.join() === 'Account,Playback,Sound,Uploads and videos,Look,Home,Library and storage,Backup', rows);
  await P.shot('v12-settings-list');
  await P.page.click('#set-playback'); await sleep(250);
  const pb = await P.G(() => ({ t: document.querySelector('.page-t').textContent, back: !!document.getElementById('setBack'), speed: !!document.querySelector('[data-k="speed"]'), list: !!document.getElementById('setList'), other: !!document.querySelector('[data-act="trim-all"]') }));
  ok('tapping one opens its own page with a back arrow, and only its settings', pb.t === 'Playback' && pb.back && pb.speed && !pb.list && !pb.other, pb);
  await P.page.click('[data-k="speed"][data-v="1.15"]'); await sleep(150);
  ok('the settings on it work as before', (await P.G(() => window.__gymTapes.S.opt.speed)) === 1.15);
  await P.shot('v12-settings-playback');
  await P.page.click('#setBack'); await sleep(200);
  ok('the back arrow returns to the list', await P.page.isVisible('#setList'));
  await P.page.click('#set-library'); await sleep(200);
  ok('Library and storage has Recently deleted and Clear library', await P.page.isVisible('#binBtn') && await P.page.isVisible('#clearBtn'));
  await P.page.click('#tabHome'); await P.page.click('#tabSettings'); await sleep(200);
  ok('leaving Settings and coming back starts at the list', await P.page.isVisible('#setList'));

  /* ===== a new account picks a username ===== */
  mock.profiles.set(crypto.randomUUID(), 'taken_name');
  await makeAccount(P, EMAIL);
  await P.page.waitForSelector('#unameIn', { timeout: 30000 }).catch(() => {});
  const uid = mock.users.get(EMAIL).id;
  ok('after making an account and signing in, it asks for a username', /Pick a username/.test(await P.page.textContent('#sheetPanel')));
  await P.shot('v12-username');
  await P.page.fill('#unameIn', 'ab'); await sleep(200); const quiet = await P.page.textContent('#authMsg');
  await P.page.click('#authGo'); await P.msg('At least 3 characters');
  ok('too short is not nagged about mid-typing, only on Save', quiet === '', quiet);
  await P.page.fill('#unameIn', 'no spaces!'); await P.msg('Only letters, numbers, dots and underscores');
  await P.page.fill('#unameIn', 'taken_name'); await P.msg('@taken_name is taken');
  await P.page.fill('#unameIn', 'Matt.W'); await P.msg('@matt.w is available');
  ok('it checks the rules and whether a name is free as you type, in lowercase', (await P.page.inputValue('#unameIn')) === 'matt.w');
  await P.page.click('#authGo'); await P.toastSays('Username saved: @matt.w');
  await P.section('account');
  ok('the username is saved to the account and shows in Account', mock.profiles.get(uid) === 'matt.w' && (await P.page.textContent('#acctUser')) === '@matt.w' && (await P.page.textContent('#acctEmail')) === EMAIL);
  await P.shot('v12-account');
  await P.page.click('#unameBtn'); await P.page.fill('#unameIn', 'taken_name'); await P.page.click('#authGo'); await P.msg('That username is taken');
  ok('changing it to one that is taken is refused', mock.profiles.get(uid) === 'matt.w');
  await P.page.fill('#unameIn', 'matt_w'); await P.page.click('#authGo'); await P.toastSays('@matt_w');
  ok('it can be changed later in Account', mock.profiles.get(uid) === 'matt_w' && (await P.page.textContent('#acctUser')) === '@matt_w');
  await P.synced();

  /* ===== an account made before V12 is asked the first time V12 opens, without signing out ===== */
  mock.users.set(OLD, { id: crypto.randomUUID(), email: OLD, pw: PW, confirmed: true });
  const O = await device(browser, 'old-phone', { path: '/v11' });
  await O.page.click('#tabSettings'); await O.page.click('#acctIn'); await O.page.fill('#authEmail', OLD); await O.page.fill('#authPw', PW); await O.page.click('#authGo');
  await O.page.waitForFunction(() => window.__gymTapes.SYNC.on && window.__gymTapes.SYNC.okAt > 0 && !window.__gymTapes.SYNC.busy, null, { timeout: 60000 });
  ok('(V11, signed in, has no usernames)', !(await O.G(() => !!document.getElementById('unameIn'))));
  await O.page.goto('http://localhost:8786/'); await O.ready();
  await O.page.waitForSelector('#unameIn', { timeout: 20000 }).catch(() => {});
  ok('the first time V12 opens it asks for a username, still signed in', (await O.G(() => window.__gymTapes.SYNC.sess && window.__gymTapes.SYNC.sess.email)) === OLD && await O.page.isVisible('#unameIn'));
  await O.page.click('#sheetPanel [data-act="sheet-close"]'); await sleep(300);
  await O.section('account');
  ok('Later leaves it for now; Account shows No username yet and Pick one', (await O.page.textContent('#acctUser')) === 'No username yet' && (await O.page.textContent('#unameBtn')) === 'Pick one');

  /* ===== two-step sign-in ===== */
  const B = await device(browser, 'tablet', { asked: true });
  await signIn(B, EMAIL); await B.synced(); await sleep(500);
  ok('(another device signed in to the same account first)', (await B.G(() => window.__gymTapes.S.raw.tracks.length)) === 2 && !(await B.sheetOpen()));
  await P.section('account');
  ok('Account has a Two-step sign-in switch, off', (await P.page.getAttribute('#mfaSwitch', 'aria-checked')) === 'false' && !(await P.page.isDisabled('#mfaSwitch')));
  await P.page.click('#mfaSwitch'); await P.page.waitForSelector('#mfaKey', { timeout: 15000 }).catch(() => {}); await sleep(400);
  const setup = await P.G(() => { const i = document.getElementById('mfaQr'), a = document.getElementById('mfaOpen'); return { qr: !!(i && i.complete && i.naturalWidth > 0), key: document.getElementById('mfaKey').textContent, href: a ? a.getAttribute('href') : '' }; });
  ok('setting it up shows a code to scan, the setup key, and Open in authenticator', setup.qr && setup.key.replace(/\s/g, '').length >= 16 && /^otpauth:\/\/totp\//.test(setup.href) && /issuer=Ear%20Worm/.test(setup.href), setup);
  await P.shot('v12-2fa-setup');
  await P.page.fill('#mfaCode', '000000'); await P.page.click('#authGo'); await P.msg('That code did not work');
  ok('a wrong code does not turn it on', !(mock.users.get(EMAIL).factors || []).some(f => f.status === 'verified'));
  await P.page.fill('#mfaCode', mock.code(EMAIL)); await P.page.click('#authGo'); await P.toastSays('Two-step sign-in is on');
  ok('the right code turns it on, and this device is signed in at the two-step level', (mock.users.get(EMAIL).factors || []).some(f => f.status === 'verified') && aalOf(await P.G(() => window.__gymTapes.SYNC.sess.at)) === 'aal2' && (await P.page.getAttribute('#mfaSwitch', 'aria-checked')) === 'true');
  await P.G(async () => { const g = window.__gymTapes; await g.store.set('playlists', 'pl2fa', { name: 'After 2FA', color: 'red', tracks: [], created: Date.now() }); });
  await P.sync();
  ok('syncing keeps working on this device', mock.rows(uid).some(r => r.coll === 'playlists' && r.data && r.data.name === 'After 2FA'));

  // the other device's sign-in ended when it was turned on
  await B.G(() => { window.__gymTapes.SYNC.checkedAt = 0; window.__gymTapes.syncNow(); });
  await B.page.waitForFunction(() => !window.__gymTapes.SYNC.sess, null, { timeout: 20000 }).catch(() => {});
  ok('another device that was signed in is signed out and told to sign in again', !(await B.G(() => window.__gymTapes.SYNC.sess)) && /Sign in again/.test(await B.page.textContent('#toast')), await B.page.textContent('#toast'));
  ok('and it keeps its library', (await B.titles()).length === 2);
  await signIn(B, EMAIL); await B.page.waitForSelector('#mfaCode', { timeout: 15000 }).catch(() => {});
  ok('signing in asks for the code before anything is saved or synced', /Enter your code/.test(await B.page.textContent('#sheetPanel')) && !(await B.G(() => window.__gymTapes.SYNC.sess)) && !(await B.G(() => window.__gymTapes.SYNC.on)));
  await B.shot('v12-2fa-code');
  await B.page.click('[data-act="mfa-code-cancel"]'); await sleep(300);
  ok('Cancel leaves it signed out', !(await B.G(() => window.__gymTapes.SYNC.sess)) && !(await B.sheetOpen()));
  await signIn(B, EMAIL); await B.page.waitForSelector('#mfaCode', { timeout: 15000 });
  await B.page.fill('#mfaCode', '123 456'); ok('the code box keeps digits only', (await B.page.inputValue('#mfaCode')) === '123456');
  await B.page.fill('#mfaCode', '000000'); await B.page.click('#authGo'); await B.msg('That code did not work');
  await B.page.fill('#mfaCode', mock.code(EMAIL)); await B.page.click('#authGo'); await B.synced(); await sleep(400);
  ok('with the right code it is signed in and syncing', aalOf(await B.G(() => window.__gymTapes.SYNC.sess.at)) === 'aal2' && (await B.G(() => window.__gymTapes.S.playlists.some(p => p.name === 'After 2FA'))));

  // a device still holding a sign-in from before two-step was on
  const s1 = mock.sessionFor(EMAIL, 'aal1');
  const N = await device(browser, 'laptop', { asked: true, auth: { at: s1.access_token, rt: s1.refresh_token, exp: s1.expires_at * 1000, uid, email: EMAIL } });
  await N.page.waitForSelector('#mfaCode', { timeout: 20000 }).catch(() => {});
  ok('a device still on an older sign-in is asked for the code, and nothing syncs until then', (await N.G(() => window.__gymTapes.SYNC.needCode)) && (await N.titles()).length === 0);
  await N.page.fill('#mfaCode', mock.code(EMAIL)); await N.page.click('#authGo');
  await N.page.waitForFunction(() => window.__gymTapes.S.tracks.length === 2 && !window.__gymTapes.SYNC.needCode, null, { timeout: 60000 }).catch(() => {});
  ok('after the code its library comes down', (await N.titles()).length === 2 && aalOf(await N.G(() => window.__gymTapes.SYNC.sess.at)) === 'aal2');

  // turning it off
  await P.section('account'); await P.page.click('#mfaSwitch'); await P.page.click('[data-act="mfa-off-go"]'); await P.toastSays('Two-step sign-in is off');
  ok('it can be turned off again', !(mock.users.get(EMAIL).factors || []).length && (await P.page.getAttribute('#mfaSwitch', 'aria-checked')) === 'false');

  /* ===== clearing the library on this device only ===== */
  await P.sync();
  const cloudRows = mock.rows(uid).length, cloudFiles = Array.from(mock.files.keys()).filter(f => f.indexOf(uid + '/') === 0).length;
  await P.section('library'); await P.page.click('#clearBtn');
  ok('Clear asks you to type CLEAR, and says the cloud keeps everything', (await P.page.isDisabled('#authGo')) && /cloud copy and your other devices keep everything/.test(await P.page.textContent('#sheetPanel')));
  await P.page.fill('#clearConfirm', 'clea'); ok('(not until the whole word)', await P.page.isDisabled('#authGo'));
  await P.page.fill('#clearConfirm', 'clear'); await P.shot('v12-clear');
  await P.page.click('#authGo');
  await P.page.waitForFunction(() => window.__gymTapes && window.__gymTapes.S.ready && /Library cleared/.test(document.getElementById('toast').textContent), null, { timeout: 30000 }).catch(() => {});
  const after = await P.G(() => ({ t: window.__gymTapes.S.raw.tracks.length, p: window.__gymTapes.S.playlists.length, sess: !!window.__gymTapes.SYNC.sess, auth: localStorage.getItem('hp.auth'), speed: window.__gymTapes.S.opt.speed, blobs: window.__gymTapes.store.blobIds().length }));
  ok('this device is wiped and signed out', after.t === 0 && after.p === 0 && after.blobs === 0 && !after.sess && !after.auth, after);
  ok('your settings stay', after.speed === 1.15);
  ok('the cloud keeps everything', mock.rows(uid).length === cloudRows && Array.from(mock.files.keys()).filter(f => f.indexOf(uid + '/') === 0).length === cloudFiles);
  await signIn(P, EMAIL);
  await P.page.waitForFunction(() => window.__gymTapes.S.tracks.length === 2 && window.__gymTapes.SYNC.okAt > 0, null, { timeout: 60000 }).catch(() => {});
  ok('signing in again brings the library back', (await P.titles()).join() === 'Leg-day-beeps,two-tones' && (await P.G(() => window.__gymTapes.S.playlists.some(p => p.name === 'After 2FA'))), await P.titles());

  /* ===== deleting an account ===== */
  const E = await device(browser, 'spare', { asked: true });
  await E.add([DIR + '/media/two-tones.mp3'], 1);
  await makeAccount(E, DEL); await E.page.waitForSelector('#unameIn', { timeout: 30000 });
  await E.page.fill('#unameIn', 'spare.one'); await E.page.click('#authGo'); await E.toastSays('@spare.one'); await E.synced();
  const duid = mock.users.get(DEL).id, dfiles = () => Array.from(mock.files.keys()).filter(f => f.indexOf(duid + '/') === 0).length;
  ok('(the spare account has a username, records and files in the cloud)', mock.profiles.get(duid) === 'spare.one' && mock.rows(duid).length > 0 && dfiles() > 0);
  await E.section('account'); await E.page.click('#delAcctBtn');
  ok('Delete account asks you to type DELETE and says the library on this device stays', (await E.page.isDisabled('#authGo')) && /library on this device stays/.test(await E.page.textContent('#sheetPanel')));
  await E.page.fill('#delConfirm', 'DELETE'); await E.shot('v12-delete');
  await E.page.click('#authGo'); await E.toastSays('Account deleted');
  ok('the account, its username, its records and its files are gone', !mock.users.has(DEL) && !mock.profiles.has(duid) && mock.rows(duid).length === 0 && dfiles() === 0);
  ok('the library on this device stays, signed out', (await E.titles()).join() === 'two-tones' && !(await E.G(() => window.__gymTapes.SYNC.sess)) && await E.page.isVisible('#acctIn'));
  ok('the other account was not touched', mock.users.has(EMAIL) && mock.rows(uid).length >= cloudRows);
  await signIn(E, DEL); await E.msg('Wrong email or password');
  ok('a message showing when a sheet opens moves out of the way of its buttons', await E.G(() => document.getElementById('toast').hidden || document.getElementById('toast').classList.contains('up')));
  ok('its login no longer works', true);
  await E.page.click('#sheetPanel [data-act="sheet-close"]'); await sleep(300);
  await E.section('library'); await E.page.click('#clearBtn');
  ok('signed out, Clear warns it is for good', /for good/.test(await E.page.textContent('#sheetPanel')));
  await E.page.fill('#clearConfirm', 'CLEAR'); await E.page.click('#authGo');
  await E.page.waitForFunction(() => window.__gymTapes && window.__gymTapes.S.ready && /Library cleared/.test(document.getElementById('toast').textContent), null, { timeout: 30000 }).catch(() => {});
  ok('and empties this device', (await E.G(() => window.__gymTapes.S.raw.tracks.length)) === 0);

  /* ===== the computer layout ===== */
  const C = await device(browser, 'pc', { pc: true, asked: true });
  await C.add([DIR + '/media/two-tones.mp3', DIR + '/media/clip-with-ending.mp3'], 2);
  const box = sel => C.G(s => { const e = document.querySelector(s); if (!e) return null; const b = e.getBoundingClientRect(); return { x: Math.round(b.x), y: Math.round(b.y), w: Math.round(b.width), h: Math.round(b.height) }; }, sel);
  const L = await C.G(() => ({ pc: window.__gymTapes.isPC(), vw: innerWidth, vh: innerHeight, title: getComputedStyle(document.querySelector('.page-t')).fontSize, body: getComputedStyle(document.body).fontSize, scroll: document.documentElement.scrollWidth }));
  let nav = await box('#nav'); const app = await box('#app'), view = await box('#view');
  ok('on a computer the tabs become a sidebar on the left, with the logo', L.pc && nav.x === 0 && nav.w > 200 && nav.w < 300 && nav.h >= L.vh - 2 && await C.page.isVisible('.nav-logo'), { nav, L });
  ok('the page uses the whole width, with no empty bars at the sides', app.x >= nav.w - 1 && app.x + app.w >= L.vw - 1 && view.w > L.vw - nav.w - 120 && L.scroll <= L.vw, { app, view });
  ok('text and buttons are bigger', L.title === '40px' && L.body === '17px', L);
  await C.page.click('.list .row-hit'); await C.page.waitForFunction(() => !window.__gymTapes.audio.paused, null, { timeout: 15000 }).catch(() => {});
  const bar = await box('.player-in'); nav = await box('#nav');
  ok('the player is a bar across the bottom, the full width, and the sidebar stops above it', bar.x <= 1 && bar.w >= L.vw - 2 && bar.y + bar.h >= L.vh - 1 && bar.h < 140 && nav.h <= L.vh - bar.h + 2, { bar, nav });
  const parts = await C.G(() => { const r = s => document.querySelector('#player ' + s).getBoundingClientRect(); return { now: r('.now').x, ctl: r('.ctl').x, wave: r('.wave').width, vh: document.querySelector('#player .ctl').getBoundingClientRect().y }; });
  ok('now playing on the left, the controls in the middle above the waveform', parts.now < parts.ctl && parts.wave > 250, parts);
  await C.page.click('#tabHome'); await sleep(400); await C.shot('v12-pc-home');
  const tb = await box('#toast'); await C.page.click('#tabLibrary'); await sleep(200);
  await C.G(() => document.activeElement && document.activeElement.blur());
  await C.page.keyboard.press(' '); await sleep(300); const p1 = await C.G(() => window.__gymTapes.audio.paused);
  await C.page.keyboard.press(' '); await sleep(300); const p2 = await C.G(() => window.__gymTapes.audio.paused);
  ok('the space bar pauses and plays', p1 === true && p2 === false, { p1, p2 });
  await C.page.click('#player .now-open'); await sleep(500);
  const fm = await box('.f-main'), fs2 = await box('.f-side');
  ok('the big player has the picture and controls on the left, up next on the right', fm && fs2 && fs2.x >= fm.x + fm.w - 2 && Math.abs(fs2.y - fm.y) < 60, { fm, fs2 });
  await C.shot('v12-pc-full');
  await C.page.keyboard.press('Escape'); await sleep(400);
  await C.page.click('#tabLibrary'); await sleep(300); await C.shot('v12-pc-library');
  await C.page.click('#tabSettings'); await sleep(300);
  const side = await C.G(() => ({ n: document.querySelectorAll('.set-side button').length, h: document.querySelector('#setMain .sec-t').textContent }));
  ok('Settings on a computer: the sections down the side, Quick settings open first (V13)', side.n === 9 && side.h === 'Quick settings', side);
  await C.page.click('#side-sound'); await sleep(250);
  ok('clicking one shows it next to the list', (await C.page.textContent('#setMain .sec-t')) === 'Sound' && await C.page.isVisible('#sw-level') && await C.page.isVisible('.set-side'));
  await C.shot('v12-pc-settings');
  await C.page.click('#side-account'); await C.page.click('#acctIn'); await sleep(400);
  const sp = await box('#sheetPanel');
  ok('sheets open as a window in the middle', sp.w <= 520 && Math.abs(sp.y + sp.h / 2 - L.vh / 2) < 80 && sp.x > nav.w, sp);
  await C.shot('v12-pc-signin');
  await C.page.keyboard.press('Escape'); await sleep(300);
  await C.page.setViewportSize({ width: 390, height: 844 }); await sleep(500);
  const narrow = await box('#nav');
  ok('made narrow, it goes back to the phone layout (the open section becomes a page with a back arrow)', !(await C.G(() => window.__gymTapes.isPC())) && narrow.y > 700 && narrow.w === 390 && await C.page.isVisible('#setBack') && (await C.page.textContent('.page-t')) === 'Account', narrow);

  ok('no page errors', allErrors.length === 0, allErrors);
  console.log(`\n${pass} passed, ${fail} failed`);
  await browser.close(); server.close();
})().catch(e => { console.error('TEST FAILED', e); console.log(allErrors); process.exit(1); });
