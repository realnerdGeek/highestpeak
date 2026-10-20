// A small stand-in for Supabase, answered inside the test browser: accounts (with email confirmation), the docs table with
// its per-account rules, and private file folders. Behaves like the real one where the app depends on it.
// V12: usernames (profiles), two-step sign-in with an authenticator app (TOTP, aal2 rules), listing files, deleting the account.
// V14: the anonymous weekly count (pings) and feedback: anyone can add a row, nobody can read them back.
const crypto = require('crypto');
const KEY = 'sb_publishable_ASIb16kL2C7ldVxfw4-KTA_OC_Dbc77';
module.exports = function makeMock() {
  const users = new Map(), tokens = new Map(), refresh = new Map(), docs = new Map(), files = new Map(), mail = [], profiles = new Map(), challenges = new Map(), deadSessions = new Set();
  const pings = [], feedback = [];
  const state = { signupsOff: false, down: false, ttl: 3600, requests: 0, uploads: [], autoProfile: false, log: [] };
  let seq = 0;
  const rid = p => p + crypto.randomBytes(12).toString('hex');
  const stamp = () => { seq++; const d = new Date(); return d.toISOString().replace('Z', String(seq % 1000).padStart(3, '0') + '+00:00'); };
  const cors = { 'access-control-allow-origin': '*', 'access-control-allow-headers': '*', 'access-control-allow-methods': 'GET,POST,PUT,PATCH,DELETE,OPTIONS', 'access-control-expose-headers': '*' };
  const json = (route, status, body) => route.fulfill({ status, headers: Object.assign({ 'content-type': 'application/json' }, cors), body: body === undefined ? '' : JSON.stringify(body) });
  const b64u = o => Buffer.from(JSON.stringify(o)).toString('base64').replace(/=+$/, '').replace(/\+/g, '-').replace(/\//g, '_');
  function session(u, aal, sid) {
    aal = aal || 'aal1'; sid = sid || crypto.randomUUID();
    const exp = Math.floor(Date.now() / 1000) + state.ttl, at = b64u({ alg: 'HS256', typ: 'JWT' }) + '.' + b64u({ sub: u.id, aal, exp, role: 'authenticated', session_id: sid, n: rid('') }) + '.' + rid('sig'), rt = rid('rt');
    tokens.set(at, { uid: u.id, exp: exp * 1000, aal, sid }); refresh.set(rt, { uid: u.id, aal, sid });
    return { access_token: at, token_type: 'bearer', expires_in: state.ttl, expires_at: exp, refresh_token: rt, user: { id: u.id, email: u.email } };
  }
  const userById = id => Array.from(users.values()).find(u => u.id === id);
  function tok(req) {
    const h = req.headers()['authorization'] || '', t = tokens.get(h.replace(/^Bearer /, ''));
    return !t || t.exp < Date.now() ? null : t;
  }
  function who(req) { const t = tok(req); return t ? t.uid : null; }
  /* the two-step rule on every table and the files: once an account has a verified authenticator, only an aal2 sign-in gets in */
  function locked(req) { const t = tok(req), u = t && userById(t.uid); return !!(u && (u.factors || []).some(f => f.status === 'verified') && t.aal !== 'aal2'); }
  /* the 6-digit code an authenticator shows for a base32 secret */
  function totp(secret, at) {
    const al = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ234567', bits = String(secret).replace(/=+$/, '').toUpperCase().split('').map(c => al.indexOf(c).toString(2).padStart(5, '0')).join(''), key = [];
    for (let i = 0; i + 8 <= bits.length; i += 8) key.push(parseInt(bits.slice(i, i + 8), 2));
    const ctr = Buffer.alloc(8); ctr.writeBigUInt64BE(BigInt(Math.floor((at || Date.now()) / 30000)));
    const h = crypto.createHmac('sha1', Buffer.from(key)).update(ctr).digest(), o = h[19] & 15;
    return String(((h.readUInt32BE(o) & 0x7fffffff) % 1000000)).padStart(6, '0');
  }
  const factorsOut = u => (u.factors || []).map(f => ({ id: f.id, friendly_name: f.name, factor_type: 'totp', status: f.status, created_at: f.at, updated_at: f.at }));
  async function handle(route) {
    const req = route.request(), url = new URL(req.url()), path = url.pathname, method = req.method();
    if (method === 'OPTIONS') return route.fulfill({ status: 204, headers: cors, body: '' });
    state.requests++;
    if (state.down) return route.abort('connectionrefused');
    if (req.headers()['apikey'] !== KEY) return json(route, 401, { message: 'Invalid API key' });
    const body = () => { try { return JSON.parse(req.postData() || 'null'); } catch (e) { return null; } };
    /* ----- accounts ----- */
    if (path === '/auth/v1/signup' && method === 'POST') {
      const b = body() || {}, email = String(b.email || '').toLowerCase();
      if (state.signupsOff) return json(route, 422, { code: 422, error_code: 'signup_disabled', msg: 'Signups not allowed for this instance' });
      if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) return json(route, 400, { code: 400, error_code: 'email_address_invalid', msg: 'Email address "' + email + '" is invalid' });
      if (String(b.password || '').length < 6) return json(route, 422, { code: 422, error_code: 'weak_password', msg: 'Password should be at least 6 characters.' });
      let u = users.get(email);
      if (!u) { u = { id: crypto.randomUUID(), email, pw: b.password, confirmed: false }; users.set(email, u); }
      mail.push({ to: email, type: 'signup', redirect: url.searchParams.get('redirect_to') });
      return json(route, 200, { id: u.id, email, confirmation_sent_at: new Date().toISOString(), identities: [] });
    }
    if (path === '/auth/v1/token' && method === 'POST') {
      const g = url.searchParams.get('grant_type'), b = body() || {};
      if (g === 'password') {
        const u = users.get(String(b.email || '').toLowerCase());
        if (!u || u.pw !== b.password) return json(route, 400, { code: 400, error_code: 'invalid_credentials', msg: 'Invalid login credentials' });
        if (!u.confirmed) return json(route, 400, { code: 400, error_code: 'email_not_confirmed', msg: 'Email not confirmed' });
        return json(route, 200, session(u));
      }
      if (g === 'refresh_token') {
        const r = refresh.get(b.refresh_token); if (!r || !userById(r.uid)) return json(route, 400, { code: 400, error_code: 'refresh_token_not_found', msg: 'Invalid Refresh Token: Refresh Token Not Found' });
        refresh.delete(b.refresh_token); return json(route, 200, session(userById(r.uid), r.aal, r.sid));
      }
    }
    if (path === '/auth/v1/recover' && method === 'POST') { const b = body() || {}; mail.push({ to: String(b.email || '').toLowerCase(), type: 'recovery', redirect: url.searchParams.get('redirect_to') }); return json(route, 200, {}); }
    if (path.indexOf('/auth/v1/') === 0 && path !== '/auth/v1/token' && path !== '/auth/v1/logout') { const t = tok(req); if (t && deadSessions.has(t.sid)) return json(route, 403, { code: 403, error_code: 'session_not_found', msg: 'Session from session_id claim in JWT does not exist' }); }
    if (path === '/auth/v1/user') {
      const uid = who(req); if (!uid) return json(route, 401, { code: 401, error_code: 'bad_jwt', msg: 'invalid JWT' });
      const u = userById(uid); if (!u) return json(route, 403, { code: 403, error_code: 'user_not_found', msg: 'User from sub claim in JWT does not exist' });
      if (method === 'PUT') { const b = body() || {}; if (b.password) { if (b.password === u.pw) return json(route, 422, { code: 422, error_code: 'same_password', msg: 'New password should be different from the old password.' }); u.pw = b.password; } }
      return json(route, 200, { id: u.id, email: u.email, factors: factorsOut(u) });
    }
    if (path === '/auth/v1/logout') return json(route, 204);
    /* ----- two-step sign-in ----- */
    const fm = /^\/auth\/v1\/factors(?:\/([^/]+))?(?:\/(challenge|verify))?$/.exec(path);
    if (fm) {
      const t = tok(req), u = t && userById(t.uid); if (!u) return json(route, 401, { code: 401, error_code: 'bad_jwt', msg: 'invalid JWT' });
      u.factors = u.factors || [];
      const b = body() || {}, f = fm[1] ? u.factors.find(x => x.id === fm[1]) : null;
      state.log.push(method + ' ' + path);
      if (!fm[1] && method === 'POST') {
        if (b.factor_type !== 'totp') return json(route, 422, { code: 422, error_code: 'validation_failed', msg: 'factor_type needs to be totp or phone' });
        if (u.factors.some(x => x.name === b.friendly_name)) return json(route, 422, { code: 422, error_code: 'mfa_factor_name_conflict', msg: 'A factor with the friendly name already exists' });
        const secret = Array.from(crypto.randomBytes(20)).map(x => 'ABCDEFGHIJKLMNOPQRSTUVWXYZ234567'[x % 32]).join(''), nf = { id: crypto.randomUUID(), name: b.friendly_name, status: 'unverified', secret, at: new Date().toISOString() };
        u.factors.push(nf);
        const uri = 'otpauth://totp/' + encodeURIComponent((b.issuer || 'app') + ':' + u.email) + '?secret=' + secret + '&issuer=' + encodeURIComponent(b.issuer || '');
        return json(route, 200, { id: nf.id, type: 'totp', friendly_name: nf.name, totp: { qr_code: 'data:image/svg+xml;utf-8,<svg xmlns="http://www.w3.org/2000/svg" width="29" height="29" viewBox="0 0 29 29"><rect width="29" height="29" fill="#fff"/><path d="M1 1h7v7H1zM21 1h7v7h-7zM1 21h7v7H1zM12 12h5v5h-5z" fill="#000"/></svg>', secret, uri } });
      }
      if (!f) return json(route, 404, { code: 404, error_code: 'mfa_factor_not_found', msg: 'Factor not found' });
      if (fm[2] === 'challenge' && method === 'POST') { const id = crypto.randomUUID(); challenges.set(id, { factor: f.id, exp: Date.now() + 300000 }); return json(route, 200, { id, type: 'totp', expires_at: Math.floor(Date.now() / 1000) + 300 }); }
      if (fm[2] === 'verify' && method === 'POST') {
        const ch = challenges.get(b.challenge_id); if (!ch || ch.factor !== f.id) return json(route, 404, { code: 404, error_code: 'mfa_challenge_not_found', msg: 'Challenge not found' });
        challenges.delete(b.challenge_id);
        if (ch.exp < Date.now()) return json(route, 422, { code: 422, error_code: 'mfa_challenge_expired', msg: 'MFA challenge has expired' });
        const now = Date.now(); if (![now - 30000, now, now + 30000].some(x => totp(f.secret, x) === String(b.code))) return json(route, 422, { code: 422, error_code: 'mfa_verification_failed', msg: 'Invalid TOTP code entered' });
        if (f.status !== 'verified') { f.status = 'verified'; refresh.forEach((r, k) => { if (r.uid === u.id && r.aal !== 'aal2' && r.sid !== t.sid) { refresh.delete(k); deadSessions.add(r.sid); } }); }      // turning it on ends the other, lower sign-ins
        refresh.forEach((r, k) => { if (r.sid === t.sid) refresh.delete(k); });
        return json(route, 200, session(u, 'aal2', t.sid));
      }
      if (!fm[2] && method === 'DELETE') {
        if (f.status === 'verified' && t.aal !== 'aal2') return json(route, 403, { code: 403, error_code: 'insufficient_aal', msg: 'AAL2 required to unenroll verified factor' });
        u.factors = u.factors.filter(x => x !== f); return json(route, 200, { id: f.id });
      }
    }
    /* ----- usernames, and the two account functions ----- */
    if (path === '/rest/v1/profiles') {
      const uid = who(req); if (!uid) return json(route, 401, { code: 'PGRST301', message: 'JWT expired' });
      if (method === 'GET') {
        if (locked(req)) return json(route, 200, []);
        const want = (url.searchParams.get('user_id') || '').replace(/^eq\./, '');
        if (want && want !== uid) return json(route, 200, []);
        const n = profiles.get(uid) || (state.autoProfile ? 'user_' + uid.slice(0, 6) : null);
        return json(route, 200, n ? [{ username: n }] : []);
      }
      if (method === 'POST') {
        const r = body() || {}, n = r.username;
        if (locked(req) || (r.user_id && r.user_id !== uid)) return json(route, 403, { code: '42501', message: 'new row violates row-level security policy for table "profiles"' });
        if (!/^[a-z0-9._]{3,20}$/.test(String(n || ''))) return json(route, 400, { code: '23514', message: 'new row for relation "profiles" violates check constraint "profiles_username_check"' });
        for (const [k, v] of profiles) if (v === n && k !== uid) return json(route, 409, { code: '23505', message: 'duplicate key value violates unique constraint "profiles_username_key"' });
        profiles.set(uid, n); return json(route, 201);
      }
    }
    if (path === '/rest/v1/rpc/username_taken' && method === 'POST') {
      const uid = who(req); if (!uid) return json(route, 401, { code: 'PGRST301', message: 'JWT expired' });
      const n = String((body() || {}).name || '').toLowerCase(); for (const [k, v] of profiles) if (v === n && k !== uid) return json(route, 200, true);
      return json(route, 200, false);
    }
    if (path === '/rest/v1/rpc/delete_my_account' && method === 'POST') {
      const uid = who(req); if (!uid) return json(route, 401, { code: 'PGRST301', message: 'JWT expired' });
      if (locked(req)) return json(route, 400, { code: 'P0001', message: 'two-step code needed' });
      if (Array.from(files.keys()).some(n => n.indexOf(uid + '/') === 0)) return json(route, 409, { code: '23503', message: 'the user still owns files in storage' });
      const u = userById(uid); users.delete(u.email); profiles.delete(uid);
      Array.from(docs.keys()).forEach(k => { if (docs.get(k).user_id === uid) docs.delete(k); });
      refresh.forEach((r, k) => { if (r.uid === uid) refresh.delete(k); });
      state.log.push('deleted ' + uid); return json(route, 204);
    }
    /* ----- the library's records ----- */
    if (path === '/rest/v1/docs') {
      const uid = who(req); if (!uid) return json(route, 401, { code: 'PGRST301', message: 'JWT expired' });
      if (locked(req)) { if (method === 'GET') return json(route, 200, []); return json(route, 403, { code: '42501', message: 'new row violates row-level security policy "two-step when on" for table "docs"' }); }
      if (method === 'GET') {
        const gt = (url.searchParams.get('updated_at') || '').replace(/^gt\./, ''), limit = +url.searchParams.get('limit') || 1000;
        const rows = Array.from(docs.values()).filter(r => r.user_id === uid && (!gt || r.updated_at > normal(gt))).sort((a, b) => (a.updated_at < b.updated_at ? -1 : 1)).slice(0, limit)
          .map(r => ({ coll: r.coll, id: r.id, data: r.data, m: r.m, deleted: r.deleted, updated_at: r.updated_at }));
        return json(route, 200, rows);
      }
      if (method === 'POST') {
        const rows = [].concat(body() || []);
        for (const r of rows) {
          if ((r.user_id || uid) !== uid) return json(route, 403, { code: '42501', message: 'new row violates row-level security policy for table "docs"' });
          if (['tracks', 'playlists', 'settings'].indexOf(r.coll) < 0) return json(route, 400, { code: '23514', message: 'violates check constraint "docs_coll_check"' });
        }
        rows.forEach(r => docs.set(uid + '|' + r.coll + '|' + r.id, { user_id: uid, coll: r.coll, id: r.id, data: r.data == null ? null : JSON.parse(JSON.stringify(r.data)), m: +r.m || 0, deleted: !!r.deleted, updated_at: stamp() }));
        return json(route, 201);
      }
    }
    /* ----- files ----- */
    const up = /^\/storage\/v1\/object\/media\/(.+)$/.exec(path), down = /^\/storage\/v1\/object\/authenticated\/media\/(.+)$/.exec(path);
    if ((up && method === 'POST') || down || (path === '/storage/v1/object/media' && method === 'DELETE') || (path === '/storage/v1/object/list/media' && method === 'POST')) {
      const uid = who(req); if (!uid) return json(route, 400, { statusCode: '403', error: 'Unauthorized', message: 'invalid jwt' });
      if (locked(req)) return json(route, 400, { statusCode: '403', error: 'Unauthorized', message: 'new row violates row-level security policy' });
      if (path === '/storage/v1/object/list/media') {
        const b = body() || {}; let pre = String(b.prefix || ''); if (pre && !pre.endsWith('/')) pre += '/';
        if (pre.split('/')[0] !== uid) return json(route, 200, []);
        const all = Array.from(files.keys()).filter(n => n.indexOf(pre) === 0 && n.slice(pre.length).indexOf('/') < 0).sort();
        state.log.push('list ' + all.length);
        return json(route, 200, all.slice(+b.offset || 0, (+b.offset || 0) + (+b.limit || 100)).map(n => ({ name: n.slice(pre.length), id: crypto.createHash('md5').update(n).digest('hex'), metadata: { size: files.get(n).buf.length } })));
      }
      if (up) {
        const name = decodeURIComponent(up[1]); if (name.split('/')[0] !== uid) return json(route, 400, { statusCode: '403', error: 'Unauthorized', message: 'new row violates row-level security policy' });
        const buf = req.postDataBuffer() || Buffer.alloc(0); if (buf.length > 52428800) return json(route, 413, { statusCode: '413', error: 'Payload too large', message: 'The object exceeded the maximum allowed size' });
        files.set(name, { buf, type: req.headers()['content-type'] || 'application/octet-stream' }); state.uploads.push(name);
        return json(route, 200, { Key: 'media/' + name });
      }
      if (down) {
        const name = decodeURIComponent(down[1]), f = files.get(name);
        if (name.split('/')[0] !== uid || !f) return json(route, 400, { statusCode: '404', error: 'not_found', message: 'Object not found' });
        return route.fulfill({ status: 200, headers: Object.assign({ 'content-type': f.type }, cors), body: f.buf });
      }
      const b = body() || {}; (b.prefixes || []).forEach(n => { if (String(n).split('/')[0] === uid) files.delete(n); });
      return json(route, 200, []);
    }
    /* ----- V14: pings and feedback, add-only ----- */
    if (path === '/rest/v1/pings' || path === '/rest/v1/feedback') {
      if (method !== 'POST') return json(route, 401, { code: '42501', message: 'permission denied for table ' + path.slice(9) });
      const b = body() || {}, prefer = req.headers()['prefer'] || '';
      if (path === '/rest/v1/pings') {
        if (!/^[A-Za-z0-9]{8,64}$/.test(String(b.device || '')) || !/^\d{4}-W\d{2}$/.test(String(b.week || '')) || String(b.version || '').length > 16 || ['phone', 'computer'].indexOf(b.kind) < 0) return json(route, 400, { code: '23514', message: 'new row violates check constraint' });
        if (pings.some(p => p.device === b.device && p.week === b.week)) return /ignore-duplicates/.test(prefer) ? json(route, 201) : json(route, 409, { code: '23505', message: 'duplicate key value violates unique constraint "pings_pkey"' });
        pings.push({ device: b.device, week: b.week, version: b.version, kind: b.kind });
        return json(route, 201);
      }
      const msg = String(b.message || ''), email = b.email == null ? null : String(b.email);
      if (!msg.length || msg.length > 2000 || (email !== null && (email.length > 200 || !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)))) return json(route, 400, { code: '23514', message: 'new row violates check constraint' });
      feedback.push({ message: msg, email, version: b.version || null, kind: b.kind || null });
      return json(route, 201);
    }
    return json(route, 404, { message: 'no route ' + method + ' ' + path });
  }
  const normal = s => { const t = Date.parse(s); return isNaN(t) ? s : new Date(t).toISOString().replace('Z', '000+00:00'); };      // timestamps compared as times, like the database does
  return {
    handle, users, docs, files, mail, state, profiles, totp, pings, feedback,
    sessionFor(email, aal) { const u = users.get(email); return u ? session(u, aal) : null; },
    code(email) { const u = users.get(email), f = u && (u.factors || []).slice(-1)[0]; return f ? totp(f.secret) : null; },
    confirm(email) { const u = users.get(email); if (u) u.confirmed = true; },
    link(email, type) { const u = users.get(email), s = session(u); return '#access_token=' + s.access_token + '&expires_at=' + s.expires_at + '&expires_in=' + s.expires_in + '&refresh_token=' + s.refresh_token + '&token_type=bearer&type=' + type; },
    rows(uid) { return Array.from(docs.values()).filter(r => r.user_id === uid); }
  };
};
