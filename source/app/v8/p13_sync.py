# V11: accounts and sync (home screen app), and the Recently deleted bin.
# The library on each device stays the real copy (works offline); signed in, it is kept in step with the cloud (Supabase).
CSS = r'''
/* accounts */
input[type="email"],input[type="password"]{font:inherit;font-size:16px;width:100%;min-height:50px;padding:0 14px;border-radius:14px;border:1px solid transparent;background:var(--raise);color:var(--ink)}
form.auth{display:flex;flex-direction:column;gap:10px}
.auth-msg{min-height:1.2em;margin:0}
.auth-msg.bad{color:var(--danger)}
.link-btn{align-self:center;background:none;color:var(--muted);font-weight:600;font-size:14px;padding:8px 10px;text-decoration:underline}
/* recently deleted */
.bin-row{gap:10px}
.bin-row .grow{display:flex;flex-direction:column;min-width:0}
.bin-t{font-weight:600;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
'''

SYNC = r'''/* ---------- accounts and sync: one library on every device ---------- */
/* Every device keeps its own full copy, so it plays offline. Signed in, changes go up to the cloud and come down on the
   other devices: the library's records in one table, the files in a private folder for the account. */
const SB = { url: 'https://pkibuxnxnirvjznmcnyo.supabase.co', key: 'sb_publishable_ASIb16kL2C7ldVxfw4-KTA_OC_Dbc77' };
const SYNC_MAX = 50 * 1048576, COLLS = ['tracks', 'playlists', 'settings'];
const SYNC = { avail: false, on: false, sess: null, st: null, busy: false, again: false, applying: false, timer: 0, every: 0, phase: '', err: '', okAt: 0,
  upLeft: 0, downLeft: 0, tooBig: 0, missing: new Set(), refreshing: null, recovery: null };
const appUrl = () => location.origin + location.pathname;
const inApp = () => !!((window.matchMedia && window.matchMedia('(display-mode: standalone)').matches) || navigator.standalone === true);
function sbErr(j, status) {
  const c = (j && (j.error_code || j.code || j.error)) || status, e = err('sb_' + c, String((j && (j.msg || j.message || j.error_description)) || ''));
  e.status = status; return e;
}
async function sbFetch(path, o) {
  o = o || {};
  const headers = Object.assign({ apikey: SB.key }, o.json !== undefined ? { 'Content-Type': 'application/json' } : {}, o.headers || {});
  if (o.auth) headers.Authorization = 'Bearer ' + (await authToken());
  const ctl = window.AbortController ? new AbortController() : null, timer = setTimeout(() => { if (ctl) ctl.abort(); }, o.wait || 30000);
  try {
    const r = await fetch(SB.url + path, { method: o.method || 'GET', headers, body: o.json !== undefined ? JSON.stringify(o.json) : o.body, signal: ctl ? ctl.signal : undefined });
    if (o.raw && r.ok) return r;
    const text = await r.text(); let j = null; try { j = text ? JSON.parse(text) : null; } catch (e) { j = null; }
    if (!r.ok) throw sbErr(j, r.status);
    return j;
  } catch (e) { if (e && typeof e.code === 'string' && e.code.indexOf('sb_') === 0) throw e; throw err('offline', e && e.message); }
  finally { clearTimeout(timer); }
}
/* ----- signing in ----- */
function saveSess(s) { SYNC.sess = s; try { if (s) localStorage.setItem('hp.auth', JSON.stringify(s)); else localStorage.removeItem('hp.auth'); } catch (e) { /* not kept */ } }
const sessFrom = j => ({ at: j.access_token, rt: j.refresh_token, exp: j.expires_at ? j.expires_at * 1000 : Date.now() + (j.expires_in || 3600) * 1000, uid: j.user && j.user.id, email: j.user && j.user.email });
async function authToken() {
  const s = SYNC.sess; if (!s) throw err('sb_signed_out');
  if (s.exp - Date.now() > 60000) return s.at;
  if (!SYNC.refreshing) SYNC.refreshing = (async () => {
    try { const n = sessFrom(await sbFetch('/auth/v1/token?grant_type=refresh_token', { method: 'POST', json: { refresh_token: s.rt } })); n.uid = n.uid || s.uid; n.email = n.email || s.email; saveSess(n); return n.at; }
    catch (e) { if (e.status >= 400 && e.status < 500) signedOut('Your sign-in ran out. Sign in again to keep syncing.'); throw e; }      // a sign-in that no longer works; a sleeping server is not that
    finally { SYNC.refreshing = null; }
  })();
  return SYNC.refreshing;
}
async function signIn(email, pw) { saveSess(sessFrom(await sbFetch('/auth/v1/token?grant_type=password', { method: 'POST', json: { email, password: pw } }))); }
const signUp = (email, pw) => sbFetch('/auth/v1/signup?redirect_to=' + encodeURIComponent(appUrl()), { method: 'POST', json: { email, password: pw } });
const sendReset = email => sbFetch('/auth/v1/recover?redirect_to=' + encodeURIComponent(appUrl()), { method: 'POST', json: { email } });
async function newPassword(pw) { const r = SYNC.recovery; await sbFetch('/auth/v1/user', r ? { method: 'PUT', json: { password: pw }, headers: { Authorization: 'Bearer ' + r } } : { method: 'PUT', json: { password: pw }, auth: true }); SYNC.recovery = null; }
function authText(e) {
  const c = String((e && e.code) || '').replace(/^sb_/, ''), m = String((e && e.message) || '');
  if (c === 'offline') return 'Can\'t reach the account service. Check your connection and try again.';
  if (c === 'invalid_credentials' || /invalid login/i.test(m)) return 'Wrong email or password.';
  if (c === 'email_not_confirmed' || /not confirmed/i.test(m)) return 'Confirm your email first: tap the link in the email that was sent to you.';
  if (c === 'user_already_exists' || /already registered/i.test(m)) return 'There is already an account with that email. Sign in instead.';
  if (c === 'signup_disabled' || /signups? not allowed/i.test(m)) return 'New accounts are turned off for this app.';
  if (c === 'weak_password' || /password should/i.test(m)) return 'Pick a longer password, at least 6 characters.';
  if (c === 'same_password') return 'That is your current password. Pick a new one.';
  if (c === 'email_address_not_authorized' || /not authorized/i.test(m)) return 'The app\'s email can only go to the email on your Supabase team. Use that email.';
  if (c === 'email_address_invalid' || /invalid format|is invalid/i.test(m)) return 'That email does not look right.';
  if (/rate.?limit|too many/i.test(c + ' ' + m)) return 'Too many tries. Wait a bit, then try again.';
  return 'That did not work. Try again.';
}
/* a confirm or reset link from an email lands back here with the sign-in in the address */
function readAuthLink() {
  const h = location.hash || ''; if (!/access_token=|error=|error_code=/.test(h)) return null;
  const q = new URLSearchParams(h.slice(1));
  try { history.replaceState(null, '', location.pathname + location.search); } catch (e) { /* fine */ }
  if (q.get('error') || q.get('error_code')) return { error: (q.get('error_code') || '') + ' ' + (q.get('error_description') || q.get('error') || '') };
  return { at: q.get('access_token'), rt: q.get('refresh_token'), exp: q.get('expires_at') ? +q.get('expires_at') * 1000 : Date.now() + (+q.get('expires_in') || 3600) * 1000, type: q.get('type') };
}
function signedOut(msg) {
  syncStop(); saveSess(null); render();
  if (msg) toast(msg);
}
/* ----- what this device still has to send, kept per account ----- */
const stKey = () => 'hp.sync.' + SYNC.sess.uid;
function loadSt() {
  let s = null; try { s = JSON.parse(localStorage.getItem(stKey()) || 'null'); } catch (e) { s = null; }
  s = s || {}; SYNC.st = { cursor: s.cursor || '', out: s.out || {}, up: new Set(s.up || []), gone: new Set(s.gone || []), merged: !!s.merged };
}
function saveSt() {
  const s = SYNC.st; if (!s || !SYNC.sess) return;
  try { localStorage.setItem(stKey(), JSON.stringify({ cursor: s.cursor, out: s.out, up: Array.from(s.up), gone: Array.from(s.gone), merged: s.merged })); } catch (e) { /* not kept */ }
}
/* the library tells sync about every change made here */
function syncHook(kind, a, b) {
  if (!SYNC.on || SYNC.applying || !SYNC.st) return;
  if (kind === 'doc') { SYNC.st.out[a + '/' + b] = Date.now(); saveSt(); soon(); }
  else if (kind === 'delblob' && SYNC.st.up.has(a)) { SYNC.st.up.delete(a); SYNC.st.gone.add(a); saveSt(); soon(); }
}
/* the files a record points at; with all, kept videos too even when they do not sync */
function blobRefs(coll, d, all) {
  const r = []; if (!d) return r;
  if (coll === 'tracks') { if (d.asset) r.push(d.asset); if (d.cover) r.push(d.cover); if (d.video && Array.isArray(d.video.parts) && (all || S.opt.syncVideo)) d.video.parts.forEach(p => r.push(p)); }
  else if (coll === 'playlists') { if (d.cover) r.push(d.cover); }
  else if (coll === 'settings' && d.bg && d.bg.kind === 'wall' && d.bg.asset) r.push(d.bg.asset);
  return r;
}
function allRefs(all) { const s = new Set(); COLLS.forEach(c => store.docs[c].forEach(d => blobRefs(c, d, all).forEach(id => s.add(id)))); return s; }
/* "2026-10-15T20:41:10.123456+00:00" in milliseconds, without leaning on the browser's own date reading */
function isoMs(s) {
  const m = /^(\d{4})-(\d\d)-(\d\d)T(\d\d):(\d\d):(\d\d)(\.\d+)?(Z|([+-])(\d\d):?(\d\d))?$/.exec(String(s || '')); if (!m) return 0;
  let t = Date.UTC(+m[1], +m[2] - 1, +m[3], +m[4], +m[5], +m[6]) + (m[7] ? Math.floor(parseFloat(m[7]) * 1000) : 0);
  if (m[9]) t -= (m[9] === '+' ? 1 : -1) * ((+m[10]) * 60 + (+m[11])) * 60000;
  return t;
}
function soon(ms) { if (!SYNC.on) return; clearTimeout(SYNC.timer); SYNC.timer = setTimeout(syncNow, ms == null ? 1500 : ms); }
async function syncNow() {
  if (!SYNC.on) return;
  if (SYNC.busy) { SYNC.again = true; return; }
  SYNC.busy = true; SYNC.err = ''; syncShow();
  try {
    if (!SYNC.st.merged) await firstMerge(); else applyRows(await pullRows(SYNC.st.cursor ? new Date(isoMs(SYNC.st.cursor) - 10000).toISOString() : ''));
    await pushBlobs(); await pushDocs(); await dropRemote(); await fetchBlobs(); localGc();
    SYNC.okAt = Date.now();
  } catch (e) { if (SYNC.on) SYNC.err = syncErrText(e); }
  finally {
    SYNC.busy = false; SYNC.phase = ''; SYNC.upLeft = SYNC.downLeft = 0; syncShow();
    if (SYNC.again && SYNC.on) { SYNC.again = false; soon(300); }
  }
}
function syncErrText(e) {
  if (navigator.onLine === false) return 'Offline. Changes sync when you are back online.';
  if (e && (e.code === 'offline' || e.status >= 500)) return 'Can\'t reach your cloud library. If it has not been used for a week it may be asleep: open supabase.com, restore the project, then tap Sync now.';
  if (e && (e.status === 401 || e.status === 403)) return 'The cloud turned this device away. Sign out and in again.';
  return 'Sync hit a problem. It will try again in a moment.';
}
async function pullRows(since) {
  const rows = []; let after = since;
  for (let i = 0; i < 400; i++) {
    const page = await sbFetch('/rest/v1/docs?select=coll,id,data,m,deleted,updated_at&order=updated_at.asc&limit=500' + (after ? '&updated_at=gt.' + encodeURIComponent(after) : ''), { auth: true }) || [];
    rows.push.apply(rows, page); if (page.length < 500) break; after = page[page.length - 1].updated_at;
  }
  return rows;
}
/* changes from the other devices. Whichever device changed a record last wins; the start delay stays per device. */
function applyRows(rows) {
  const out = SYNC.st.out; let n = 0;
  SYNC.applying = true;
  try {
    for (const r of rows) {
      if (!r || COLLS.indexOf(r.coll) < 0 || typeof r.id !== 'string') continue;
      const key = r.coll + '/' + r.id, mine = out[key];
      if (mine && mine >= (+r.m || 0)) continue;           // changed here after that: this copy wins and goes up next
      if (mine) delete out[key];
      const cur = store.docs[r.coll].get(r.id);
      if (r.deleted || !r.data) { if (cur) { store.apply(r.coll, r.id, null); n++; } continue; }
      let d = r.data;
      if (r.coll === 'settings' && r.id === 'opts') d = Object.assign({}, d, { delay: cur && cur.delay != null ? cur.delay : S.opt.delay });
      if (cur && JSON.stringify(cur) === JSON.stringify(d)) continue;
      store.apply(r.coll, r.id, d); n++;
    }
  } finally { SYNC.applying = false; }
  rows.forEach(r => { if (r && r.updated_at > (SYNC.st.cursor || '')) SYNC.st.cursor = r.updated_at; });
  saveSt();
  if (n) store.emit();
  return n;
}
async function pushBlobs() {
  const need = allRefs(false), todo = Array.from(need).filter(id => !SYNC.st.up.has(id) && store.has(id));
  SYNC.upLeft = todo.length; SYNC.tooBig = 0; if (todo.length) { SYNC.phase = 'up'; syncShow(); }
  for (const id of todo) {
    const b = await store.blob(id);
    if (b.size > SYNC_MAX) { SYNC.tooBig++; SYNC.upLeft--; continue; }
    await sbFetch('/storage/v1/object/media/' + SYNC.sess.uid + '/' + encodeURIComponent(id), { method: 'POST', body: b, auth: true, raw: true, wait: 300000, headers: { 'Content-Type': b.type || 'application/octet-stream', 'x-upsert': 'true' } });
    SYNC.st.up.add(id); SYNC.upLeft--; saveSt(); syncShow();
  }
}
async function pushDocs() {
  const out = SYNC.st.out, keys = Object.keys(out); if (!keys.length) return;
  for (let i = 0; i < keys.length; i += 100) {
    const part = keys.slice(i, i + 100), snap = {};
    const rows = part.map(k => {
      const j = k.indexOf('/'), coll = k.slice(0, j), id = k.slice(j + 1), d = store.docs[coll] ? store.docs[coll].get(id) : null; snap[k] = out[k];
      return { user_id: SYNC.sess.uid, coll, id, data: d || null, m: out[k], deleted: !d };
    }).filter(r => COLLS.indexOf(r.coll) >= 0);
    if (rows.length) await sbFetch('/rest/v1/docs?on_conflict=user_id,coll,id', { method: 'POST', json: rows, auth: true, headers: { Prefer: 'resolution=merge-duplicates,return=minimal' } });
    part.forEach(k => { if (out[k] === snap[k]) delete out[k]; }); saveSt();
  }
}
async function dropRemote() {
  const ids = Array.from(SYNC.st.gone); if (!ids.length) return;
  await sbFetch('/storage/v1/object/media', { method: 'DELETE', json: { prefixes: ids.map(id => SYNC.sess.uid + '/' + id) }, auth: true });
  ids.forEach(id => SYNC.st.gone.delete(id)); saveSt();
}
/* files from the other devices: the sound first, so new uploads show up sooner */
async function fetchBlobs() {
  const sound = [], rest = [];
  store.docs.tracks.forEach(d => { if (d.asset) sound.push(d.asset); });
  allRefs(false).forEach(id => { if (sound.indexOf(id) < 0) rest.push(id); });
  const todo = sound.concat(rest).filter(id => !store.has(id) && !SYNC.missing.has(id));
  SYNC.downLeft = todo.length; if (todo.length) { SYNC.phase = 'down'; syncShow(); }
  let got = 0, bg = false;
  for (const id of todo) {
    try {
      const r = await sbFetch('/storage/v1/object/authenticated/media/' + SYNC.sess.uid + '/' + encodeURIComponent(id), { auth: true, raw: true, wait: 300000 });
      const b = await r.blob();
      await store.putBlobAs(id, b.type ? b : new Blob([b], { type: 'video/mp4' }));
      SYNC.st.up.add(id); got++;
      if (curBg().kind === 'wall' && curBg().asset === id) bg = true;
      if (got % 3 === 0) { saveSt(); store.emit(); }
    } catch (e) { if (e && (e.status === 400 || e.status === 404)) SYNC.missing.add(id); else throw e; }
    finally { SYNC.downLeft--; syncShow(); }
  }
  if (got) { saveSt(); store.emit(); }
  if (bg) applyBg();
}
/* a file nothing points at any more, that came from or went to the cloud, is dropped here too */
function localGc() {
  const keep = allRefs(true); let n = 0;
  store.blobIds().forEach(id => { if (!keep.has(id) && SYNC.st.up.has(id)) { store.dropBlob(id); SYNC.st.up.delete(id); n++; } });
  if (n) saveSt();
}
/* The first sign-in on a device: what is already in the cloud comes down, what is only here goes up.
   The same file added on two devices becomes one upload, and playlists with the same name become one. */
async function firstMerge() {
  SYNC.phase = 'merge'; syncShow();
  const rows = await pullRows(''), now = Date.now(), out = SYNC.st.out;
  const remote = { tracks: new Map(), playlists: new Map(), settings: new Map() };
  rows.forEach(r => { if (r && remote[r.coll] && !r.deleted && r.data) remote[r.coll].set(r.id, r.data); });
  const local = { tracks: new Map(store.docs.tracks), playlists: new Map(store.docs.playlists), settings: new Map(store.docs.settings) };
  const remoteFiles = new Set(); remote.tracks.forEach(d => blobRefs('tracks', d, true).forEach(id => remoteFiles.add(id)));
  const dupes = new Map(), byFp = new Map();
  remote.tracks.forEach((d, id) => { if (d.fp && !d.trashed) byFp.set(d.fp, id); });
  SYNC.applying = true;
  try {
    remote.tracks.forEach((d, id) => store.apply('tracks', id, d));
    local.tracks.forEach((d, id) => {
      if (remote.tracks.has(id)) return;
      const twin = d.fp && !d.trashed ? byFp.get(d.fp) : null, tw = twin && remote.tracks.get(twin);
      const keepsVideo = d.video && Array.isArray(d.video.parts) && d.video.parts.every(p => store.has(p)) && !(tw && tw.video && Array.isArray(tw.video.parts) && tw.video.parts.every(p => store.has(p)));
      if (twin && !keepsVideo) {          // the same file: keep the cloud's, drop this copy
        dupes.set(id, twin); store.apply('tracks', id, null);
        blobRefs('tracks', d, true).forEach(b => { if (!remoteFiles.has(b)) store.dropBlob(b); });
      } else out['tracks/' + id] = now;
    });
    const plByName = new Map(); remote.playlists.forEach((d, id) => { store.apply('playlists', id, d); plByName.set(String(d.name || '').trim().toLowerCase(), id); });
    local.playlists.forEach((d, id) => {
      if (remote.playlists.has(id)) return;
      const tracks = (d.tracks || []).map(t => dupes.get(t) || t).filter((t, i, a) => a.indexOf(t) === i), twin = plByName.get(String(d.name || '').trim().toLowerCase());
      if (twin) {
        const r = remote.playlists.get(twin), list = (r.tracks || []).slice(); tracks.forEach(t => { if (list.indexOf(t) < 0) list.push(t); });
        const merged = Object.assign({}, r, { tracks: list }); if (d.cover && !r.cover) merged.cover = d.cover; else if (d.cover) store.dropBlob(d.cover);
        store.apply('playlists', twin, merged); remote.playlists.set(twin, merged); out['playlists/' + twin] = now; store.apply('playlists', id, null);
      } else { store.apply('playlists', id, Object.assign({}, d, { tracks })); out['playlists/' + id] = now; }
    });
    /* settings: the cloud's options and look (the start delay stays per device), every preset from both, the higher play counts */
    const ls = local.settings, rs = remote.settings, mapIds = ids => (ids || []).map(x => dupes.get(x) || x);
    rs.forEach((d, id) => { if (['opts', 'presets', 'recent'].indexOf(id) < 0) store.apply('settings', id, d); });
    ls.forEach((d, id) => { if (['opts', 'presets', 'recent', 'stats'].indexOf(id) < 0 && !rs.has(id)) out['settings/' + id] = now; });
    if (rs.has('opts')) { const lo = ls.get('opts'); store.apply('settings', 'opts', Object.assign({}, rs.get('opts'), { delay: lo && lo.delay != null ? lo.delay : S.opt.delay })); }
    else if (ls.has('opts')) out['settings/opts'] = now;
    const lp = (ls.get('presets') || {}).list || [], rp = (rs.get('presets') || {}).list || [];
    if (lp.length || rp.length) { const list = rp.concat(lp.filter(p => p && !rp.some(q => q && q.id === p.id))); store.apply('settings', 'presets', { list }); if (list.length !== rp.length || !rs.has('presets')) out['settings/presets'] = now; }
    const lr = ls.get('recent') || {}, rr = rs.get('recent') || {}, plays = {};
    [rr.plays || {}, lr.plays || {}].forEach((p, k) => { for (const id in p) { const to = k ? dupes.get(id) || id : id, c = Math.round(+p[id] || 0); if (c > (plays[to] || 0)) plays[to] = c; } });
    if (ls.has('recent') || rs.has('recent')) { const ids = (rr.ids && rr.ids.length ? rr.ids : mapIds(lr.ids)).filter((x, i, a) => a.indexOf(x) === i).slice(0, 12); store.apply('settings', 'recent', { ids, plays }); out['settings/recent'] = now; }
    if (!rs.has('stats') && ls.has('stats')) out['settings/stats'] = now;
  } finally { SYNC.applying = false; }
  for (const k in S.plays) { const to = dupes.get(k); if (to) { S.plays[to] = Math.max(S.plays[to] || 0, S.plays[k]); delete S.plays[k]; } }
  rows.forEach(r => { if (r && r.updated_at > (SYNC.st.cursor || '')) SYNC.st.cursor = r.updated_at; });
  SYNC.st.merged = true; saveSt();
  store.emit();
  saveStats(true);            // the counts from both, merged when they came in, go back up
}
/* ----- starting and stopping ----- */
function syncStart() {
  if (!SYNC.sess || !store || store.kind !== 'local') return;
  SYNC.on = true; loadSt();
  store.hidden = t => !!(SYNC.on && t.asset && !store.has(t.asset));      // an upload from another device shows once its sound is here
  clearInterval(SYNC.every); SYNC.every = setInterval(() => { if (document.visibilityState === 'visible') syncNow(); }, 45000);
  store.emit(); syncNow();
}
function syncStop() { SYNC.on = false; clearInterval(SYNC.every); clearTimeout(SYNC.timer); if (store) { store.hidden = null; store.emit(); } }
document.addEventListener('visibilitychange', () => { if (SYNC.on && document.visibilityState === 'visible') soon(300); });
window.addEventListener('online', () => { if (SYNC.on) soon(300); });
async function syncBoot() {
  SYNC.avail = true; store.hook = syncHook;
  try { const s = JSON.parse(localStorage.getItem('hp.auth') || 'null'); if (s && s.at && s.rt && s.uid) SYNC.sess = s; } catch (e) { /* signed out */ }
  const link = readAuthLink();
  if (link && link.error) toast(/expired/i.test(link.error) ? 'That link has expired. Ask for a new one.' : 'That link did not work. Ask for a new one.');
  else if (link && link.at) {
    /* On iPhone an email link opens in Safari, which keeps its own storage apart from the home screen app. There the link only
       confirms the email or sets a new password; signing in and syncing happen in the app, so Safari never downloads the library. */
    if (!inApp() && link.type === 'recovery') { SYNC.recovery = link.at; if (SYNC.sess) syncStart(); render(); newPwSheet(); return; }
    if (!inApp()) { if (SYNC.sess) syncStart(); render(); toast('Email confirmed. Now sign in in the HighestPeak app.'); return; }
    try {
      const u = await sbFetch('/auth/v1/user', { headers: { Authorization: 'Bearer ' + link.at } });
      saveSess({ at: link.at, rt: link.rt, exp: link.exp, uid: u.id, email: u.email });
      syncStart(); render();
      if (link.type === 'recovery') newPwSheet(); else toast('Email confirmed. You are signed in.');
      return;
    } catch (e) { toast('That link did not work. Try signing in.'); }
  }
  if (SYNC.sess) syncStart();
  render();
}
/* ----- what Settings shows ----- */
function syncText() {
  if (!SYNC.on || !SYNC.st) return '';
  if (SYNC.phase === 'merge') return 'Setting up sync';
  if (SYNC.upLeft) return 'Syncing: ' + SYNC.upLeft + (SYNC.upLeft === 1 ? ' file' : ' files') + ' to go up';
  if (SYNC.downLeft) return 'Getting ' + SYNC.downLeft + (SYNC.downLeft === 1 ? ' file' : ' files') + ' from your other devices';
  if (SYNC.busy) return 'Syncing';
  if (SYNC.err) return SYNC.err;
  const left = Object.keys(SYNC.st.out).length; if (left) return left + (left === 1 ? ' change' : ' changes') + ' waiting to sync';
  const ago = SYNC.okAt ? Math.floor((Date.now() - SYNC.okAt) / 60000) : -1;
  let t = ago < 0 ? 'Not synced yet' : ago < 1 ? 'Synced just now' : 'Synced ' + ago + ' min ago';
  if (SYNC.tooBig) t += '. ' + SYNC.tooBig + (SYNC.tooBig === 1 ? ' file is' : ' files are') + ' over 50 MB and stay on this device';
  if (SYNC.missing.size) t += '. ' + SYNC.missing.size + (SYNC.missing.size === 1 ? ' file was' : ' files were') + ' not found in the cloud';
  return t + '.';
}
function cloudText() { if (!SYNC.st) return ''; let b = 0; SYNC.st.up.forEach(id => { b += store.blobSize(id); }); return 'About ' + fmtBytes(b) + ' of 1 GB cloud space used'; }
function syncShow() {
  const a = document.getElementById('syncStatus'); if (a) a.textContent = syncText();
  const b = document.getElementById('syncStorage'); if (b) b.textContent = cloudText();
  const c = document.getElementById('syncNowBtn'); if (c) c.disabled = SYNC.busy;
}
function accountGroup() {
  if (!SYNC.avail) return '';
  if (!SYNC.sess) return group('Account', '<div class="set col"><div><div class="set-t">Sync your library</div><p class="sub">Sign in to keep your uploads, playlists and likes the same on your phone and your computer. Without an account everything stays on this device, like now.</p></div>' +
    '<div class="pair"><button class="btn sm" id="acctIn" data-act="acct-in">Sign in</button><button class="btn sm primary" id="acctNew" data-act="acct-new">Create account</button></div></div>');
  return group('Account',
    '<div class="set col"><div><div class="set-t" id="acctEmail">' + esc(SYNC.sess.email || 'Signed in') + '</div><p class="sub" id="syncStatus" aria-live="polite">' + esc(syncText()) + '</p><p class="sub" id="syncStorage">' + esc(cloudText()) + '</p></div>' +
    '<div class="pair"><button class="btn sm" id="syncNowBtn" data-act="sync-now"' + (SYNC.busy ? ' disabled' : '') + '>Sync now</button><button class="btn sm" id="acctOut" data-act="acct-out">Sign out</button></div></div>' +
    setRow('Sync videos', 'Kept videos go to your other devices too. Uses a lot more cloud space. Videos over 50 MB stay on the device they were added on.', swBtn('syncVideo', 'Sync videos')));
}
const AUTHF = { email: '', busy: false };
const authForm = (form, title, fields, go, extra) => sheet('<h2>' + title + '</h2><form class="auth" data-form="' + form + '">' + fields + '<p class="sub auth-msg" id="authMsg" aria-live="polite"></p><button type="submit" class="btn primary" id="authGo">' + go + '</button>' + (extra || '') + '</form><button class="btn" data-act="sheet-close">Cancel</button>', { kind: 'auth' });
const emailField = () => '<input type="email" id="authEmail" name="email" autocomplete="username" placeholder="Email" aria-label="Email" required data-focus value="' + esc(AUTHF.email) + '">';
function signInSheet(msg) {
  authForm('signin', 'Sign in', emailField() + '<input type="password" id="authPw" name="pw" autocomplete="current-password" placeholder="Password" aria-label="Password" required>', 'Sign in', '<button type="button" class="link-btn" data-act="acct-forgot">Forgot password?</button>');
  if (msg) authSay(msg, false);
}
function signUpSheet() { authForm('signup', 'Create account', emailField() + '<input type="password" id="authPw" name="pw" autocomplete="new-password" placeholder="Password, at least 6 characters" aria-label="Password" minlength="6" required><p class="sub">You get an email with a link to confirm it.</p>', 'Create account'); }
function forgotSheet() { authForm('forgot', 'Reset your password', emailField() + '<p class="sub">You get an email with a link to set a new one.</p>', 'Send reset link'); }
function newPwSheet() { authForm('newpw', 'Set a new password', '<input type="password" id="authPw" name="pw" autocomplete="new-password" placeholder="New password, at least 6 characters" aria-label="New password" minlength="6" required data-focus>', 'Save new password'); }
function authSay(msg, bad) { const el = document.getElementById('authMsg'); if (el) { el.textContent = msg || ''; el.classList.toggle('bad', !!bad); } }
async function authRun(f, fn) {
  if (AUTHF.busy) return; AUTHF.busy = true;
  const go = f.querySelector('#authGo'); if (go) go.disabled = true; authSay('One moment');
  try { await fn(); } catch (e) { authSay(authText(e), true); }
  finally { AUTHF.busy = false; if (go && go.isConnected) go.disabled = false; }
}

/* ---------- recently deleted: a deleted upload waits here for 14 days, on every device, before it is gone for good ---------- */
const BIN_DAYS = 14, BIN_MS = BIN_DAYS * 86400000;
function binRow() {
  const n = S.trash.length;
  return '<div class="set"><div class="grow"><div class="set-t">Recently deleted</div><p class="sub" id="binCount">' + (n ? countText(n) + ', kept for ' + BIN_DAYS + ' days' : 'Nothing deleted lately') + '</p></div><button class="btn sm" id="binBtn" data-act="bin-open"' + (n ? '' : ' disabled') + '>Open</button></div>';
}
function binSheet() {
  const list = S.trash.slice().sort((a, b) => (b.trashed || 0) - (a.trashed || 0));
  const left = t => Math.max(0, Math.ceil(((t.trashed || 0) + BIN_MS - Date.now()) / 86400000));
  sheet('<h2>Recently deleted</h2><p class="sub">Deleted uploads stay here for ' + BIN_DAYS + ' days, then they are gone for good' + (SYNC.on ? ' on every device' : '') + '.</p>' +
    (list.length ? '<div class="opts">' + list.map(t => '<div class="opt static bin-row" data-key="' + esc(t.id) + '">' + trackCover(t) + '<span class="grow"><span class="bin-t">' + esc(t.title) + '</span><span class="sub">' + (left(t) <= 1 ? 'Gone within a day' : left(t) + ' days left') + '</span></span>' +
      '<button class="btn xs" data-act="bin-restore" data-id="' + esc(t.id) + '">Put back</button><button class="btn xs warn" data-act="bin-purge" data-id="' + esc(t.id) + '">Delete</button></div>').join('') + '</div><button class="btn warn" data-act="bin-empty">Delete all for good</button>'
      : '<p class="sub">Nothing here.</p>') +
    '<button class="btn" data-act="sheet-close">Close</button>', { kind: 'bin' });
}
function restoreUpload(id) {
  S.gone.delete(id); DEL.done.delete(id);
  guard(async () => { await store.update('tracks', id, { trashed: null }); toast('Put back.'); if (sheetCtx && sheetCtx.kind === 'bin') binSheet(); });
}
async function purgeOld() {
  if (!S.ready || !store || !store.canWrite) return;
  const old = S.trash.filter(t => t.trashed && Date.now() - t.trashed > BIN_MS);
  for (const t of old) { try { await purgeUpload(t.id); } catch (e) { /* next time */ } }
  if (old.length) refreshUsage();
}
setInterval(purgeOld, 6 * 3600000);

'''

PURGE = r'''async function deleteUpload(id) {
  const raw = S.raw || { tracks: [], playlists: [] }, t = raw.tracks.find(x => x.id === id); if (!t) { S.gone.delete(id); return; }
  DEL.done.add(id);                     // stays hidden until the library confirms it is in the bin
  await store.update('tracks', id, { trashed: Date.now() });
}
/* gone for good: out of the bin, out of every playlist, and its files deleted */
async function purgeUpload(id) {
  const raw = S.raw || { tracks: [], playlists: [] }, t = raw.tracks.find(x => x.id === id); if (!t) return;
  await store.del('tracks', id);        // the upload itself goes first, so a delete that gets cut short never leaves it half removed from playlists
  for (const p of raw.playlists) if ((p.tracks || []).indexOf(id) >= 0) { const now = playlist(p.id) || p; await setPlaylistTracks(p.id, (now.tracks || []).filter(x => x !== id)); }
  await store.delBlob(t.asset); if (t.cover) store.delBlob(t.cover);
  if (t.video && Array.isArray(t.video.parts)) t.video.parts.forEach(p => store.delBlob(p));
  const u = PRE.get(t.asset); if (u) URL.revokeObjectURL(u); PRE.delete(t.asset);
  if (S.plays[id]) delete S.plays[id];
  S.gone.delete(id); DEL.done.delete(id);
}
'''

def apply(d):
    d.before('</style>', CSS)
    # the device's library: tells sync about changes, takes changes from the cloud without echoing them back, and keeps
    # an upload from another device out of sight until its sound has arrived
    d.rep("  const emit = () => cb({ tracks: list(docs.tracks), playlists: list(docs.playlists), settings: list(docs.settings) });",
          "  const emit = () => cb({ tracks: list(docs.tracks).filter(t => !st.hidden || !st.hidden(t)), playlists: list(docs.playlists), settings: list(docs.settings) });\n"
          "  const hook = (k, a, b) => { if (st.hook) st.hook(k, a, b); };")
    d.rep("    async set(c, id, d) { docs[c].set(id, d); emit(); await run('docs', 'readwrite', s => s.put(d, c + '/' + id)).catch(() => {}); },",
          "    async set(c, id, d) { docs[c].set(id, d); emit(); hook('doc', c, id); await run('docs', 'readwrite', s => s.put(d, c + '/' + id)).catch(() => {}); },")
    d.rep("    async del(c, id) { docs[c].delete(id); emit(); await run('docs', 'readwrite', s => s.delete(c + '/' + id)).catch(() => {}); },",
          "    async del(c, id) { docs[c].delete(id); emit(); hook('doc', c, id); await run('docs', 'readwrite', s => s.delete(c + '/' + id)).catch(() => {}); },")
    d.rep("    async delBlob(id) { blobs.delete(id); const u = urls.get(id); if (u) { URL.revokeObjectURL(u); urls.delete(id); } await run('blobs', 'readwrite', s => s.delete(id)).catch(() => {}); },",
          "    async delBlob(id) { hook('delblob', id); return st.dropBlob(id); },\n"
          "    async dropBlob(id) { blobs.delete(id); const u = urls.get(id); if (u) { URL.revokeObjectURL(u); urls.delete(id); } await run('blobs', 'readwrite', s => s.delete(id)).catch(() => {}); },\n"
          "    async putBlobAs(id, blob) { blobs.set(id, blob); await run('blobs', 'readwrite', s => s.put(blob, id)).catch(() => {}); },\n"
          "    apply(c, id, d) { if (d) docs[c].set(id, d); else docs[c].delete(id); run('docs', 'readwrite', s => (d ? s.put(d, c + '/' + id) : s.delete(c + '/' + id))).catch(() => {}); },\n"
          "    emit() { emit(); }, docs, hook: null, hidden: null,\n"
          "    has: id => blobs.has(id), blobIds: () => Array.from(blobs.keys()), blobSize: id => { const b = blobs.get(id); return b ? b.size : 0; },")
    # options: Sync videos, off to begin with
    d.rep("hNewest: true, keepVideo: true, videoEnd: true };", "hNewest: true, keepVideo: true, videoEnd: true, syncVideo: false };")
    d.rep("'hNewest', 'keepVideo', 'videoEnd'].forEach(k =>", "'hNewest', 'keepVideo', 'videoEnd', 'syncVideo'].forEach(k =>")
    d.rep("  if (k === 'speed' || k === 'keepPitch') applyRate();", "  if (k === 'speed' || k === 'keepPitch') applyRate();\n  if (k === 'syncVideo') soon(200);")
    # a kept video only counts as here when its files are on this device (one added on another device may not be)
    d.rep("function hasVideo(t) { return !!(t && t.video && Array.isArray(t.video.parts) && t.video.parts.length); }",
          "function hasVideo(t) { return !!(t && t.video && Array.isArray(t.video.parts) && t.video.parts.length && (!store || !store.has || t.video.parts.every(id => store.has(id)))); }")
    d.before("/* ---------- loudness, for volume leveling ---------- */", SYNC)
    # deleting goes to the bin; purging is the old delete
    d.cut("async function deleteUpload(id) {", "window.addEventListener('pagehide', () => { flushDelete();", PURGE)
    d.rep("  DEL.done.forEach(id => { if (!d.tracks.some(t => t.id === id)) { DEL.done.delete(id); S.gone.delete(id); } });\n  S.tracks = d.tracks.filter(t => !S.gone.has(t.id)).sort((a, b) => (b.created || 0) - (a.created || 0));",
          "  DEL.done.forEach(id => { if (!d.tracks.some(t => t.id === id && !t.trashed)) { DEL.done.delete(id); S.gone.delete(id); } });\n"
          "  S.tracks = d.tracks.filter(t => !S.gone.has(t.id) && !t.trashed).sort((a, b) => (b.created || 0) - (a.created || 0));\n"
          "  S.trash = d.tracks.filter(t => t.trashed);")
    d.rep("  if (first) { freezeHome(); restoreSession(); }", "  if (first) { freezeHome(); restoreSession(); setTimeout(purgeOld, 3000); }")
    d.rep("plays: {}, gone: new Set(), raw: null,", "plays: {}, gone: new Set(), trash: [], raw: null,")
    # a restore does not count an upload in the bin as already here
    d.rep("have = () => (S.raw ? S.raw.tracks : S.tracks).filter(t => !S.gone.has(t.id))", "have = () => (S.raw ? S.raw.tracks : S.tracks).filter(t => !S.gone.has(t.id) && !t.trashed)")
    # Settings: the account at the top, the bin under Library
    d.rep("  return pageTitle('Settings') + group('Playback',", "  return pageTitle('Settings') + accountGroup() + group('Playback',")
    d.rep("id=\"setStorage\">' + esc(storageText()) + '</p></div></div>') +",
          "id=\"setStorage\">' + esc(storageText()) + '</p></div></div>' + binRow()) +")
    d.after("const ACT = {\n",
            "  'acct-in'() { signInSheet(); },\n"
            "  'acct-new'() { signUpSheet(); },\n"
            "  'acct-forgot'() { const e = document.getElementById('authEmail'); if (e) AUTHF.email = e.value.trim(); forgotSheet(); },\n"
            "  'acct-out'() { confirmSheet('Sign out', 'Your uploads stay on this device. Sign in again any time to keep syncing.', 'Sign out', 'acct-out-go', {}); },\n"
            "  'acct-out-go'() { closeSheet(); const s = SYNC.sess; if (SYNC.st) { SYNC.st.merged = false; saveSt(); } if (s) sbFetch('/auth/v1/logout', { method: 'POST', headers: { Authorization: 'Bearer ' + s.at } }).catch(() => {}); signedOut('Signed out. Your uploads stay on this device.'); },\n"
            "  'sync-now'() { syncNow(); },\n"
            "  'bin-open'() { binSheet(); },\n"
            "  'bin-restore'(d) { restoreUpload(d.id); },\n"
            "  'bin-purge'(d) { const t = (S.raw ? S.raw.tracks : []).find(x => x.id === d.id); if (t) confirmSheet('Delete for good', '\"' + t.title + '\" will be gone for good' + (SYNC.on ? ' on every device' : '') + '.', 'Delete', 'bin-purge-go', { kind: 'binconfirm', id: d.id }); },\n"
            "  'bin-purge-go'() { const c = sheetCtx; if (!c) return; guard(async () => { await purgeUpload(c.id); refreshUsage(); if (S.trash.length) binSheet(); else closeSheet(); toast('Deleted for good.'); }); },\n"
            "  'bin-empty'() { confirmSheet('Delete all for good', countText(S.trash.length) + ' will be gone for good' + (SYNC.on ? ' on every device' : '') + '.', 'Delete all', 'bin-empty-go', { kind: 'binconfirm' }); },\n"
            "  'bin-empty-go'() { closeSheet(); const ids = S.trash.map(t => t.id); guard(async () => { for (const id of ids) await purgeUpload(id); refreshUsage(); toast('Recently deleted is empty.'); }); },\n")
    d.after("const FORM = {\n",
            "  signin(f) { const email = f.elements.email.value.trim(), pw = f.elements.pw.value; AUTHF.email = email; authRun(f, async () => { await signIn(email, pw); closeSheet(); syncStart(); render(); toast('Signed in. Syncing your library.'); }); },\n"
            "  signup(f) {\n"
            "    const email = f.elements.email.value.trim(), pw = f.elements.pw.value; AUTHF.email = email;\n"
            "    authRun(f, async () => { const j = await signUp(email, pw); if (j && j.access_token) { saveSess(sessFrom(j)); closeSheet(); syncStart(); render(); toast('Account made. Syncing your library.'); } else signInSheet('Check your email and tap the link to confirm your account, then sign in here.'); });\n"
            "  },\n"
            "  forgot(f) { const email = f.elements.email.value.trim(); AUTHF.email = email; authRun(f, async () => { await sendReset(email); authSay('If that email has an account, a reset link is on its way. Open it on this device.'); }); },\n"
            "  newpw(f) { const pw = f.elements.pw.value, here = !!SYNC.sess && !SYNC.recovery; authRun(f, async () => { await newPassword(pw); closeSheet(); toast(here ? 'Password changed.' : 'Password changed. Sign in with it in the HighestPeak app.'); }); },\n")
    d.rep("  store.watch(onData, () => note('Lost the connection to your library. Reload the page.'));\n  refreshUsage();",
          "  store.watch(onData, () => note('Lost the connection to your library. Reload the page.'));\n  refreshUsage();\n"
          "  if (store.kind === 'local' && window.HP_STANDALONE && window.fetch) syncBoot();")
    # restoring an upload that sits in the bin brings it back, and the bin copy's files are cleaned up
    d.rep("        await again(() => store.set('tracks', bt.id, doc)); idMap.set(bt.id, bt.id); fresh.add(bt.id); added++;",
          "        const binned = (S.raw ? S.raw.tracks : []).find(t => t.id === bt.id && t.trashed);\n"
          "        await again(() => store.set('tracks', bt.id, doc)); idMap.set(bt.id, bt.id); fresh.add(bt.id); added++;\n"
          "        if (binned) [binned.asset, binned.cover].concat(binned.video && binned.video.parts || []).forEach(b => { if (b && b !== doc.asset && b !== doc.cover && !(doc.video && doc.video.parts.indexOf(b) >= 0)) store.delBlob(b); });")
    d.rep("window.__gymTapes = { MP4, VCUT, VID, prepVideo, videoBlob, S,", "window.__gymTapes = { MP4, VCUT, VID, SYNC, syncNow: () => syncNow(), prepVideo, videoBlob, S,")
