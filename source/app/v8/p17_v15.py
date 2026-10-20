# V15: Play anywhere. Your signed-in devices share one private live channel (Supabase Realtime, topic "ew:<account id>").
# Only one plays at a time: when one starts, the others stop. Any of them can control the one that is playing (play and
# pause, skip, scrub, volume, shuffle, loop, Up next, what plays), and playing can move to another device at the same spot.

CSS = r'''
/* ===================== V15: Play anywhere ===================== */
.rt-devbtn{display:none}
body.rt-devs .rt-devbtn{display:inline-flex}
body.rt-remote .player{display:none!important}
.rt-bar[hidden]{display:none}
.rt-bar{position:fixed;z-index:10}   /* where the player sits: under sheets, the big player and toasts */
.rt-on{display:flex;align-items:center;gap:5px;color:var(--accent-ink);font-size:12.5px;font-weight:700;min-width:0;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.rt-on svg{flex:none}
.rt-nocov{display:block;background:var(--raise)}
.rt-full{display:flex;flex-direction:column;gap:12px}
.rt-head{display:flex;align-items:center;gap:8px;color:var(--accent-ink);font-weight:700;font-size:14px}
.rt-head b{color:var(--ink)}
.rt-cover .cover{width:min(100%,280px);height:auto;aspect-ratio:1;margin:0 auto;border-radius:20px;box-shadow:0 20px 44px var(--shadow)}
.rt-name .title{font:800 22px/1.2 var(--round);letter-spacing:-.02em;overflow-wrap:anywhere}
.rt-name .meta{color:var(--muted);font-size:13px;margin-top:2px}
.rt-seek{width:100%;accent-color:var(--accent)}
.rt-full .times{display:flex;justify-content:space-between;color:var(--muted);font-size:12px;margin-top:-6px}
.rt-full .ctl{display:flex;align-items:center;justify-content:space-between}
.rt-full .tog[aria-pressed="true"]{color:var(--accent-ink)}
.rt-full .vol{display:flex;align-items:center;gap:10px}
.rt-full .vol input{flex:1;accent-color:var(--accent)}
.rt-q{display:flex;flex-direction:column}
.rt-qrow{display:grid;grid-template-columns:42px minmax(0,1fr);gap:11px;align-items:center;min-height:54px;text-align:left}
.rt-qrow .cover{width:42px;height:42px;border-radius:8px}
.rt-qrow .tt{display:flex;flex-direction:column;min-width:0}
.rt-qrow .title{font-weight:600;font-size:15px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.rt-qrow .meta{color:var(--muted);font-size:12.5px}
.dev-list{display:flex;flex-direction:column;gap:6px;margin:4px 0 14px}
.dev-row{display:grid;grid-template-columns:40px minmax(0,1fr) auto;gap:12px;align-items:center;min-height:58px;padding:0 12px;border-radius:14px;background:var(--raise);text-align:left}
.dev-row .dev-ic{width:40px;height:40px;border-radius:12px;display:grid;place-items:center;background:color-mix(in srgb,var(--ink) 8%,transparent)}
.dev-row .dev-n{font-weight:700}
.dev-row .dev-s{color:var(--muted);font-size:12.5px}
.dev-row.on .dev-ic{background:var(--accent);color:var(--on-accent)}
.dev-row.on .dev-s{color:var(--accent-ink);font-weight:700}
/* phones: the remote bar sits where the mini player sits */
@media (max-width: 899.98px){
  .rt-bar{left:50%;transform:translateX(-50%);width:min(520px,calc(100% - 24px));bottom:calc(var(--nav-h,66px) + 20px + env(safe-area-inset-bottom,0px));
    transition:left .34s cubic-bezier(.2,.9,.25,1.1),width .34s cubic-bezier(.2,.9,.25,1.1),transform .34s cubic-bezier(.2,.9,.25,1.1),bottom .34s cubic-bezier(.2,.9,.25,1.1)}
  .rt-in{position:relative;display:grid;grid-template-columns:minmax(0,1fr) auto auto;gap:6px;align-items:center;padding:8px;border-radius:20px;overflow:hidden;
    background:var(--g-bg);-webkit-backdrop-filter:blur(22px) saturate(180%);backdrop-filter:blur(22px) saturate(180%);border:1px solid var(--g-line);box-shadow:inset 0 1px 0 var(--g-hi),var(--g-sh)}
  body.no-glass .rt-in{background:var(--g-solid);-webkit-backdrop-filter:none;backdrop-filter:none}
  .rt-open{display:grid;grid-template-columns:46px minmax(0,1fr);gap:11px;align-items:center;min-width:0;text-align:left}
  .rt-open .cover{width:46px;height:46px;border-radius:11px}
  .rt-t{display:flex;flex-direction:column;min-width:0;gap:2px}
  .rt-t .title{font-weight:700;font-size:15px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
  .rt-in .mini-prog{display:block;position:absolute;left:16px;right:16px;bottom:0;height:3px;border-radius:2px;background:color-mix(in srgb,var(--ink) 14%,transparent);overflow:hidden}
  .rt-in .mini-prog i{display:block;height:100%;width:0;background:var(--accent);border-radius:2px}
  body.nav-min .rt-bar{left:84px;transform:none;width:calc(100% - 96px);bottom:calc(12px + env(safe-area-inset-bottom,0px))}
  body.nav-min .rt-in{border-radius:31px}
  .sheet-panel .rt-full{padding-top:4px}
}
/* computers: the remote panel sits where the Now playing panel sits */
@media (min-width: 900px){
  body.rt-remote{--np-w:340px}
  body.rt-remote .app{margin-right:var(--np-w)}
  .rt-bar{z-index:13;top:0;right:0;bottom:0;width:var(--np-w,340px);box-sizing:border-box;padding:22px 20px 24px;overflow-y:auto;background:var(--sheet);border-left:1px solid var(--line)}
  .rt-bar .np-head{display:flex;align-items:center;justify-content:space-between}
  .rt-bar .np-head span{font:800 16px/1.2 var(--round);color:var(--accent-ink)}
  .rt-bar .rt-cover .cover{width:100%}
  .rt-bar .mini-prog{display:none}
}
'''

ICONS = r'''
const RT_IC = {
  dev: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="2" y="4" width="13" height="10" rx="2"/><path d="M6 18h5M8.5 14v4"/><rect x="17" y="7" width="5" height="12" rx="1.5"/><path d="M19.5 16.5h0"/></svg>',
  phone: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="6.5" y="2.5" width="11" height="19" rx="2.5"/><path d="M11 18.5h2"/></svg>',
  computer: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="3" y="4" width="18" height="12" rx="2"/><path d="M8 20h8M12 16v4"/></svg>',
  play: '<svg width="22" height="22" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M8 5v14l11-7z"/></svg>',
  pause: '<svg width="22" height="22" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M7 5h4v14H7zM13 5h4v14h-4z"/></svg>',
  next: '<svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M6 5l10 7-10 7zM16.5 5h2.5v14h-2.5z"/></svg>',
  prev: '<svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M18 5L8 12l10 7zM5 5h2.5v14H5z"/></svg>',
  loop: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.1" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M17 2l3 3-3 3"/><path d="M4 11V9a4 4 0 014-4h12"/><path d="M7 22l-3-3 3-3"/><path d="M20 13v2a4 4 0 01-4 4H4"/></svg>'
};
'''

RT_JS = r'''
/* ===================== V15: Play anywhere =====================
   Your signed-in devices share one private live channel (Supabase Realtime, "ew:<account id>", private, so only your
   own devices can join it). Only one plays at a time: when one starts, the others stop. Any of them can control the one
   that is playing, and playing can move to another device at the same spot. The sound always comes from the playing
   device's own copy. */
var RT = { ws: null, ref: 0, jref: '', topic: '', joined: false, hb: 0, back: 0, retry: 0, devices: new Map(), remote: null, active: false,
  sentSig: '', soonT: 0, tick: 0, tokenSent: '', stopped: true, lastErr: '', lastMsg: 0, local: false, volT: 0 };
const rtUrl = () => (window.__HP_RT_URL || SB.url.replace(/^https/, 'wss') + '/realtime/v1/websocket') + '?apikey=' + encodeURIComponent(SB.key) + '&vsn=1.0.0';
function devGuess() {
  const u = navigator.userAgent || '';
  if (/iPhone/.test(u)) return 'iPhone';
  if (/iPad/.test(u) || (/Macintosh/.test(u) && navigator.maxTouchPoints > 1)) return 'iPad';
  if (/Android/.test(u)) return /Mobile/.test(u) ? 'Android phone' : 'Android tablet';
  if (/CrOS/.test(u)) return 'Chromebook';
  if (/Windows/.test(u)) return 'Windows PC';
  if (/Mac/.test(u)) return 'Mac';
  return isPC() ? 'Computer' : 'Phone';
}
function devName() { let n = ''; try { n = localStorage.getItem('hp.devName') || ''; } catch (e) { /* fine */ } return n.trim().slice(0, 30) || devGuess(); }
const rtDev = id => RT.devices.get(id) || { id, name: 'another device', kind: 'phone' };
const rtWanted = () => !!(window.WebSocket && !window.__HP_RT_OFF && SYNC.on && SYNC.sess && SYNC.sess.uid && S.opt.anywhere !== false && !SYNC.needCode);
function rtSync() { if (!RT) return; if (rtWanted()) { if (!RT.ws && RT.stopped !== 'starting') rtStart(); } else if (RT.ws || RT.remote || RT.joined) rtStop(); }
function rtSend(event, payload, topic) {
  const ws = RT.ws; if (!ws || ws.readyState !== 1) return false;
  RT.ref++; ws.send(JSON.stringify({ topic: topic || RT.topic, event, payload, ref: String(RT.ref), join_ref: topic === 'phoenix' ? null : RT.jref })); return true;
}
function rtCast(event, data) { return RT.joined && rtSend('broadcast', { type: 'broadcast', event, payload: Object.assign({ from: deviceId(), name: devName(), kind: devKind() }, data || {}) }); }
const rtMe = () => ({ name: devName(), kind: devKind(), at: Date.now() });
async function rtStart() {
  clearTimeout(RT.back); if (!rtWanted() || RT.ws) return;
  RT.stopped = 'starting';
  let token; try { token = await authToken(); } catch (e) { RT.stopped = false; return rtRetry(); }
  if (!rtWanted() || RT.ws) { RT.stopped = false; return; }
  RT.stopped = false; RT.topic = 'realtime:ew:' + SYNC.sess.uid; RT.joined = false;
  let ws; try { ws = new WebSocket(rtUrl()); } catch (e) { return rtRetry(); }
  RT.ws = ws; RT.lastMsg = Date.now();
  ws.onopen = () => {
    if (RT.ws !== ws) return;
    RT.ref++; RT.jref = String(RT.ref); RT.tokenSent = token;
    ws.send(JSON.stringify({ topic: RT.topic, event: 'phx_join', ref: RT.jref, join_ref: RT.jref,
      payload: { config: { broadcast: { ack: false, self: false }, presence: { enabled: true, key: deviceId() }, private: true }, access_token: token } }));
    clearInterval(RT.hb); RT.hb = setInterval(rtBeat, 25000);
  };
  ws.onmessage = e => { if (RT.ws !== ws) return; RT.lastMsg = Date.now(); let m; try { m = JSON.parse(e.data); } catch (x) { return; } if (m && m.topic === RT.topic) rtOn(m); };
  ws.onclose = () => { if (RT.ws !== ws) return; RT.ws = null; RT.joined = false; clearInterval(RT.hb); RT.devices.clear(); rtRemote(null); rtDraw(); if (!RT.stopped) rtRetry(); };
  ws.onerror = () => { /* the close comes next */ };
}
function rtRetry() { clearTimeout(RT.back); if (!rtWanted()) return; const waits = [1000, 2000, 5000, 10000, 30000, 60000]; RT.back = setTimeout(rtStart, waits[Math.min(RT.retry++, waits.length - 1)]); }
function rtStop() {
  RT.stopped = true; clearTimeout(RT.back); clearInterval(RT.hb);
  const ws = RT.ws; RT.ws = null; RT.joined = false; if (ws) { try { ws.close(); } catch (e) { /* fine */ } }
  RT.devices.clear(); RT.active = false; rtRemote(null); rtDraw();
}
function rtDrop() { const ws = RT.ws; RT.ws = null; RT.joined = false; clearInterval(RT.hb); if (ws) { try { ws.close(); } catch (e) { /* fine */ } } RT.devices.clear(); rtRemote(null); rtDraw(); if (!RT.stopped) rtRetry(); }
async function rtBeat() {
  rtSend('heartbeat', {}, 'phoenix');
  if (SYNC.sess && SYNC.sess.exp - Date.now() < 5 * 60000) { try { await authToken(); } catch (e) { /* tried */ } }
  if (RT.joined && SYNC.sess && SYNC.sess.at !== RT.tokenSent) { RT.tokenSent = SYNC.sess.at; rtSend('access_token', { access_token: SYNC.sess.at }); }
  if (RT.active && !audio.paused) rtState(true);          // a regular update while playing keeps the others in step
}
function rtOn(m) {
  const p = m.payload || {};
  if (m.event === 'phx_reply' && m.ref === RT.jref) {
    if (p.status === 'ok') {
      RT.joined = true; RT.retry = 0; RT.lastErr = '';
      rtSend('presence', { type: 'presence', event: 'track', payload: rtMe() });
      rtCast('hello');
      if (!audio.paused && track(P.cur)) { RT.active = true; rtCast('took', { state: rtStateObj() }); }
      rtDraw();
    } else { RT.lastErr = String((p.response && p.response.reason) || 'refused'); RT.retry = Math.max(RT.retry, 3); rtDrop(); }
    return;
  }
  if (m.event === 'presence_state') { RT.devices.clear(); rtPresence(p, {}); return; }
  if (m.event === 'presence_diff') { rtPresence(p.joins || {}, p.leaves || {}); return; }
  if (m.event === 'phx_close' || m.event === 'phx_error') { rtDrop(); return; }
  if (m.event !== 'broadcast' || !p.payload) return;
  const d = p.payload; if (!d || typeof d.from !== 'string' || d.from === deviceId()) return;
  rtMessage(String(p.event || ''), d);
}
function rtSeen(id, m) { if (id && id !== deviceId() && m) RT.devices.set(id, { id, name: String(m.name || 'Device').slice(0, 30), kind: m.kind === 'computer' ? 'computer' : 'phone' }); }
function rtPresence(joins, leaves) {
  Object.keys(leaves).forEach(k => { if (!joins[k]) RT.devices.delete(k); });
  Object.keys(joins).forEach(k => { const metas = (joins[k] && joins[k].metas) || []; rtSeen(k, metas[metas.length - 1]); });
  if (RT.remote && !RT.devices.has(RT.remote.from)) rtRemote(null);         // the playing device went away
  rtDraw();
}
function rtMessage(ev, d) {
  rtSeen(d.from, d);
  if (ev === 'hello') { if (RT.active && track(P.cur)) rtState(true); rtDraw(); return; }
  if (ev === 'took') {                                        // another device started playing: this one stops
    RT.active = false;
    if (!audio.paused) audio.pause();
    rtRemote(d.state || null, d.from); return;
  }
  if (ev === 'state') {
    if (RT.active && !audio.paused) return;                   // this one is playing: it decides
    if (d.playing || (RT.remote && RT.remote.from === d.from)) { RT.active = false; rtRemote(d, d.from); }
    return;
  }
  if (ev === 'blocked') { if (RT.remote && RT.remote.from === d.from) toast(rtDev(d.from).name + ' needs one click in EarWorm before it can play sound sent from here.'); return; }
  if (ev === 'missing') { if (d.to === deviceId()) toast('That upload is not on ' + rtDev(d.from).name + ' yet. It will be once it syncs.'); return; }
  if (ev === 'cmd' && d.to === deviceId()) rtCommand(d);
}
/* what this device is playing, for the others */
function rtStateObj() {
  const t = track(P.cur); if (!t) return null;
  const up = P.order.slice(P.pos + 1);
  return { id: t.id, title: t.title, playing: !audio.paused, abs: Math.round(curAbs() * 10) / 10, dur: t.dur || 0, vol: VOL.v, shuffle: !!S.shuffle, loop: S.loop,
    ctx: P.ctx || 'all', label: P.label || '', left: up.length, next: up.slice(0, 5).map(id => { const x = track(id); return x ? { id, title: x.title, dur: x.dur || 0 } : null; }).filter(Boolean) };
}
function rtState(force) {
  if (!RT.joined || !RT.active) return;
  const s = rtStateObj(); if (!s) return;
  const sig = JSON.stringify([s.id, s.playing, s.vol, s.shuffle, s.loop, s.left, s.next.map(x => x.id).join()]);
  if (!force && sig === RT.sentSig) return;
  RT.sentSig = sig; rtCast('state', s);
}
function rtSoon(force) { if (!RT.joined) return; clearTimeout(RT.soonT); RT.soonT = setTimeout(() => rtState(force), 150); }
/* this device started playing on its own: it is the one playing now, the others stop */
function rtLocalPlay() {
  if (!RT.joined || !track(P.cur)) return;
  const was = RT.active; RT.active = true; rtRemote(null);
  if (!was || RT.local !== 'take') rtCast('took', { state: rtStateObj() }); else rtState(true);
}
/* commands from another device, to this one (the one playing) */
function rtCommand(d) {
  const t = track(P.cur); RT.local = true;
  try {
    switch (d.do) {
      case 'toggle': if (audio.paused) { togglePlay(); rtExpectPlay(d.from); } else audio.pause(); break;
      case 'next': next(false); rtExpectPlay(d.from); break;
      case 'prev': prev(); break;
      case 'seek': if (t) seekAbs(t, Math.max(0, Math.min(+d.abs || 0, (t.dur || 0) - 0.2))); break;
      case 'vol': setVolume(Math.max(0, Math.min(1, +d.v || 0)), true); break;
      case 'shuffle': ACT.shuffle(); break;
      case 'loop': ACT.loop(); break;
      case 'jump': ACT['q-jump']({ id: String(d.id || '') }); rtExpectPlay(d.from); break;
      case 'queue': {
        const ids = (Array.isArray(d.ids) ? d.ids : []).filter(id => typeof id === 'string' && track(id)); if (!ids.length) break;
        if (typeof d.ctx === 'string') P.ctx = d.ctx;
        startQueue(ids, String(d.label || 'Uploads').slice(0, 80), track(d.startId) ? d.startId : null); rtExpectPlay(d.from); break;
      }
      case 'take': {                                           // "play here": start the same upload at the same spot
        const id = String(d.id || ''); if (!track(id)) { rtCast('missing', { to: d.from, id }); break; }
        rtTake(d); rtExpectPlay(d.from); break;
      }
    }
  } finally { RT.local = false; }
  rtSoon(true);
}
function rtTake(d) {
  const id = String(d.id), ids = (Array.isArray(d.ids) ? d.ids : []).filter(x => typeof x === 'string' && track(x));
  if (ids.indexOf(id) < 0) ids.unshift(id);
  RT.local = 'take'; rtRemote(null);
  P.ctx = typeof d.ctx === 'string' ? d.ctx : 'all'; P.queue = ids; P.label = String(d.label || 'Uploads').slice(0, 80);
  if (typeof d.shuffle === 'boolean' && d.shuffle !== S.shuffle) { S.shuffle = d.shuffle; savePrefs(); }
  P.order = ids.slice(); P.pos = ids.indexOf(id);
  playAt(track(id), Math.max(0, +d.abs || 0));
  RT.active = true;
}
/* a device asked to play may not be allowed to start sound yet (a computer that has not been clicked): say so */
function rtExpectPlay(from) { setTimeout(() => { if (audio.paused && RT.joined && track(P.cur)) rtCast('blocked', { to: from }); }, 1500); }
/* this device is showing another one that plays: send it what was tapped here */
function rtRoute(what, data) {
  if (!RT || RT.local || !RT.remote || !RT.joined || !RT.devices.has(RT.remote.from)) return false;
  rtCast('cmd', Object.assign({ to: RT.remote.from, do: what }, data || {}));
  if (what === 'toggle') { RT.remote.playing = !RT.remote.playing; RT.remote.abs = rtPos(); RT.remote.recv = Date.now(); rtDraw(); }
  return true;
}
function rtPos() { const r = RT.remote; if (!r) return 0; const p = (+r.abs || 0) + (r.playing ? (Date.now() - r.recv) / 1000 : 0); return Math.max(0, r.dur ? Math.min(r.dur, p) : p); }
function rtRemote(s, from) {
  if (!s) { if (RT.remote) { RT.remote = null; rtDraw(); } return; }
  const keepVol = RT.remote && RT.volT && Date.now() - RT.volT < 1200 ? RT.remote.vol : null;
  RT.remote = Object.assign({}, s, { from: from || s.from, recv: Date.now() }); if (keepVol != null) RT.remote.vol = keepVol;
  rtDraw();
}
/* move playing to another device (or here), at the same spot */
function rtTransfer(id) {
  closeSheet();
  if (id === deviceId()) return rtHere();
  if (!RT.devices.has(id)) return toast('That device is not online right now.');
  if (RT.remote && RT.remote.from === id) return;            // it is already the one playing
  const t = track(RT.remote ? RT.remote.id : P.cur); if (!t) return toast('Play something first, then move it.');
  const src = RT.remote ? { id: RT.remote.id, abs: rtPos(), ctx: RT.remote.ctx, label: RT.remote.label, ids: [RT.remote.id].concat((RT.remote.next || []).map(x => x.id)), shuffle: RT.remote.shuffle }
    : { id: P.cur, abs: curAbs(), ctx: P.ctx, label: P.label, ids: P.order.slice(Math.max(0, P.pos - 50), P.pos + 300), shuffle: S.shuffle };
  rtCast('cmd', Object.assign({ to: id, do: 'take' }, src));
  toast('Playing on ' + rtDev(id).name + '.');
}
function rtHere() {
  const r = RT.remote; if (!r) return;
  if (!track(r.id)) return toast('That upload is not on this device yet. It will be once it syncs.');
  const l = typeof listFor === 'function' ? listFor(r.ctx) : null;
  rtTake({ id: r.id, abs: rtPos(), ctx: r.ctx, label: r.label, shuffle: r.shuffle, ids: l && l.ids && l.ids.indexOf(r.id) >= 0 ? l.ids : [r.id].concat((r.next || []).map(x => x.id)) });
  RT.local = false;
}
/* ----- the remote bar (phone) and panel (computer), and its sheet ----- */
function rtCoverOf(id) { const t = track(id); return t ? trackCover(t) : '<span class="cover rt-nocov"></span>'; }
const rtDevBtn = () => '<button class="icon-btn sm rt-devbtn" data-act="rt-devices" aria-label="Play on another device">' + RT_IC.dev + '</button>';
function rtBar() {
  const r = RT.remote, d = rtDev(r.from);
  return '<div class="rt-in"><button class="rt-open" data-act="rt-open" aria-label="Controls for ' + esc(d.name) + '">' + rtCoverOf(r.id) +
    '<span class="rt-t"><span class="title" id="rtTitle">' + esc(r.title || 'Playing') + '</span><span class="rt-on">' + RT_IC.dev + '<span>Playing on ' + esc(d.name) + '</span></span></span></button>' +
    '<button class="rnd sm" id="rtToggle" data-act="rt-toggle" aria-label="' + (r.playing ? 'Pause' : 'Play') + ' on ' + esc(d.name) + '">' + (r.playing ? RT_IC.pause : RT_IC.play) + '</button>' +
    '<button class="rnd sm" id="rtNext" data-act="rt-next" aria-label="Next on ' + esc(d.name) + '">' + RT_IC.next + '</button>' +
    '<span class="mini-prog"><i id="rtLine"></i></span></div>';
}
function rtFull(panel) {
  const r = RT.remote, d = rtDev(r.from), on = !!r.playing;
  return '<div class="rt-full" id="rtFull">' +
    (panel ? '<div class="np-head"><span>Playing on ' + esc(d.name) + '</span>' + rtDevBtn() + '</div>' : '<div class="rt-head">' + RT_IC.dev + '<span>Playing on <b>' + esc(d.name) + '</b></span></div>') +
    '<div class="rt-cover">' + rtCoverOf(r.id) + '</div>' +
    '<div class="rt-name"><div class="title" id="rtFullTitle">' + esc(r.title || '') + '</div><div class="meta">' + esc(r.label || '') + '</div></div>' +
    '<input type="range" class="rt-seek" id="rtSeek" min="0" max="' + Math.max(1, Math.round((r.dur || 1) * 10)) + '" step="1" value="' + Math.round(rtPos() * 10) + '" aria-label="Position on ' + esc(d.name) + '" data-rt="seek">' +
    '<div class="times"><span id="rtCur">' + fmt(rtPos()) + '</span><span>' + fmt(r.dur || 0) + '</span></div>' +
    '<div class="ctl"><button class="tog" id="rtShuf" data-act="rt-shuffle" aria-pressed="' + !!r.shuffle + '" aria-label="Shuffle">' + IC.shuffle + '</button>' +
      '<button class="rnd" data-act="rt-prev" aria-label="Previous on ' + esc(d.name) + '">' + RT_IC.prev + '</button>' +
      '<button class="rnd big" id="rtFullToggle" data-act="rt-toggle" aria-label="' + (on ? 'Pause' : 'Play') + ' on ' + esc(d.name) + '">' + (on ? RT_IC.pause : RT_IC.play) + '</button>' +
      '<button class="rnd" data-act="rt-next" aria-label="Next on ' + esc(d.name) + '">' + RT_IC.next + '</button>' +
      '<button class="tog" id="rtLoop" data-act="rt-loop" aria-pressed="' + (r.loop !== 'off') + '" aria-label="Loop">' + RT_IC.loop + '</button></div>' +
    '<div class="vol"><span class="vol-ic">' + IC.vol + '</span><input type="range" id="rtVol" min="0" max="100" step="1" value="' + Math.round((r.vol == null ? 1 : r.vol) * 100) + '" data-rt="vol" aria-label="Volume on ' + esc(d.name) + '"></div>' +
    '<div class="pair"><button class="btn primary" id="rtHere" data-act="rt-here">Play here</button><button class="btn" id="rtDevs" data-act="rt-devices">Devices</button></div>' +
    (r.next && r.next.length ? '<div class="sec-h"><h3>Up next</h3><span class="f-note">' + (r.left || r.next.length) + ' to go</span></div><div class="rt-q">' +
      r.next.map(x => '<button class="rt-qrow" data-act="rt-jump" data-id="' + esc(x.id) + '">' + rtCoverOf(x.id) + '<span class="tt"><span class="title">' + esc(x.title) + '</span><span class="meta">' + fmt(x.dur || 0) + '</span></span></button>').join('') + '</div>' : '') +
    '</div>';
}
function rtDraw() {
  const on = !!RT.remote, b = document.body;
  b.classList.toggle('rt-remote', on); b.classList.toggle('rt-devs', RT.joined && RT.devices.size > 0);
  const el = $('#remote'); if (!el) return;
  el.hidden = !on;
  if (!on) { clearInterval(RT.tick); RT.tick = 0; if (sheetCtx && sheetCtx.kind === 'remote') closeSheet(); rtAcct(); return; }
  const busy = document.activeElement && document.activeElement.closest && document.activeElement.closest('#remote [data-rt]');
  if (!busy) paint(el, isPC() ? rtFull(true) : rtBar());
  const sp = $('#sheetPanel .rt-wrap'); if (sp && !(document.activeElement && document.activeElement.closest && document.activeElement.closest('.rt-wrap [data-rt]'))) paint(sp, rtFull(false));
  if (!RT.tick) RT.tick = setInterval(rtProgress, 500);
  rtProgress(); rtAcct();
}
function rtProgress() {
  const r = RT.remote; if (!r) return;
  const p = rtPos(), pct = r.dur ? Math.min(100, p / r.dur * 100) : 0;
  all('#rtLine', i => { i.style.width = pct + '%'; });
  all('#rtCur', c => { c.textContent = fmt(p); });
  all('#rtSeek', s => { if (document.activeElement !== s) s.value = Math.round(p * 10); });
}
function rtSheet() { if (!RT.remote) return; sheet('<div class="rt-wrap">' + rtFull(false) + '</div><button class="btn" data-act="sheet-close">Close</button>', { kind: 'remote' }); }
function devicesSheet() {
  const r = RT.remote, here = !r && !!track(P.cur);
  const row = (id, name, kind, on, sub) => '<button class="dev-row' + (on ? ' on' : '') + '" data-act="rt-pick" data-id="' + esc(id) + '"><span class="dev-ic">' + (kind === 'computer' ? RT_IC.computer : RT_IC.phone) + '</span>' +
    '<span><span class="dev-n">' + esc(name) + '</span><br><span class="dev-s">' + sub + '</span></span><span class="tick">' + (on ? IC.tick : '') + '</span></button>';
  const mine = row(deviceId(), 'This ' + (devKind() === 'computer' ? 'computer' : 'phone') + ' (' + devName() + ')', devKind(), here, here ? (audio.paused ? 'Paused here' : 'Playing here') : 'Tap to play here');
  const others = [...RT.devices.values()].map(d => row(d.id, d.name, d.kind, !!(r && r.from === d.id), r && r.from === d.id ? (r.playing ? 'Playing' : 'Paused') : 'Tap to play there'));
  sheet('<h2>Play on</h2><div class="dev-list">' + mine + others.join('') + '</div>' +
    '<p class="sub">Your devices signed in to this account show here while EarWorm is open on them. Only one plays at a time.</p><button class="btn" data-act="sheet-close">Close</button>', { kind: 'devices' });
}
/* ----- Settings, Account ----- */
function rtStatusText() {
  const on = S.opt.anywhere !== false, others = [...RT.devices.values()].map(d => d.name);
  if (!on) return 'Off. Each device plays on its own.';
  if (!RT.joined) return RT.lastErr ? 'Can\'t connect right now. It keeps trying.' : 'Connecting...';
  return others.length ? 'Online now: ' + others.join(', ') + '.' : 'No other devices online right now. Open EarWorm on another device signed in to this account.';
}
function rtGroup() {
  return group('Play anywhere',
    setRow('Play anywhere', 'Your signed-in devices play as one. Only one plays at a time, and any of them can control it: play and pause, skip, volume and what plays.', swBtn('anywhere', 'Play anywhere')) +
    '<div class="set"><div class="grow"><div class="set-t">This device</div><p class="sub" id="rtStatus">' + esc(devName()) + '. ' + esc(rtStatusText()) + '</p></div><button class="btn sm" id="rtNameBtn" data-act="rt-name">Rename</button></div>');
}
function rtAcct() { const s = $('#rtStatus'); if (s) s.textContent = devName() + '. ' + rtStatusText(); }
function rtNameSheet() {
  sheet('<h2>Name this device</h2><p class="sub">Your other devices see this name in Play on.</p><form data-form="rtname"><input type="text" id="rtNameIn" name="dname" maxlength="30" value="' + esc(devName()) + '" data-focus autocomplete="off">' +
    '<div class="pair"><button type="button" class="btn" data-act="sheet-close">Cancel</button><button type="submit" class="btn primary" id="rtNameSave">Save</button></div></form>', { kind: 'rtname' });
}
/* the range sliders in the remote controls */
document.addEventListener('input', e => {
  const el = e.target && e.target.closest ? e.target.closest('[data-rt]') : null; if (!el || !RT.remote) return;
  if (el.dataset.rt === 'vol') { RT.volT = Date.now(); RT.remote.vol = (+el.value || 0) / 100; clearTimeout(RT.volSend); RT.volSend = setTimeout(() => rtRoute('vol', { v: RT.remote ? RT.remote.vol : 0 }), 120); }
  if (el.dataset.rt === 'seek') { const p = (+el.value || 0) / 10; all('#rtCur', c => { c.textContent = fmt(p); }); }
});
document.addEventListener('change', e => {
  const el = e.target && e.target.closest ? e.target.closest('[data-rt="seek"]') : null; if (!el || !RT.remote) return;
  const abs = (+el.value || 0) / 10; rtRoute('seek', { abs }); RT.remote.abs = abs; RT.remote.recv = Date.now(); el.blur(); rtProgress();
});
on('play', rtLocalPlay);
on('pause', () => rtSoon(true));
on('seeked', () => rtSoon(true));
document.addEventListener('visibilitychange', () => { if (document.visibilityState !== 'visible') return; rtSync(); if (RT.joined) { rtCast('hello'); rtSend('presence', { type: 'presence', event: 'track', payload: rtMe() }); } });
let rtResize = 0; window.addEventListener('resize', () => { clearTimeout(rtResize); rtResize = setTimeout(rtDraw, 200); });
/* a watchdog: start or stop with sign-in and the switch, and reconnect a connection that went quiet (a phone waking up) */
setInterval(() => { rtSync(); if (RT.ws && Date.now() - RT.lastMsg > 70000) { RT.retry = 0; rtDrop(); } }, 5000);
'''

ACTS = r'''  'rt-devices'() { devicesSheet(); },
  'rt-pick'(d) { rtTransfer(d.id); },
  'rt-open'() { rtSheet(); },
  'rt-toggle'() { rtRoute('toggle'); },
  'rt-next'() { rtRoute('next'); },
  'rt-prev'() { rtRoute('prev'); },
  'rt-shuffle'() { if (RT.remote) { RT.remote.shuffle = !RT.remote.shuffle; rtDraw(); } rtRoute('shuffle'); },
  'rt-loop'() { rtRoute('loop'); },
  'rt-jump'(d) { rtRoute('jump', { id: d.id }); },
  'rt-here'() { closeSheet(); rtHere(); },
  'rt-name'() { rtNameSheet(); },
'''

def apply(d):
    d.before('</style>', CSS)
    d.before('<section class="player', '<section class="rt-bar" id="remote" hidden aria-label="Playing on another device"></section>\n')
    # the Devices button: in the big player's top bar, and in the computer's Now playing panel
    d.rep('<button class="icon-btn" data-act="full-menu" aria-label="Options for this upload">',
          '<button class="icon-btn rt-devbtn" data-act="rt-devices" aria-label="Play on another device"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="2" y="4" width="13" height="10" rx="2"/><path d="M6 18h5M8.5 14v4"/><rect x="17" y="7" width="5" height="12" rx="1.5"/></svg></button><button class="icon-btn" data-act="full-menu" aria-label="Options for this upload">')
    d.rep('<div class="np-head"><span>Now playing</span><button class="icon-btn sm" data-act="full-open"',
          '<div class="np-head"><span>Now playing</span><span class="np-btns"><button class="icon-btn sm rt-devbtn" data-act="rt-devices" aria-label="Play on another device"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="2" y="4" width="13" height="10" rx="2"/><path d="M6 18h5M8.5 14v4"/><rect x="17" y="7" width="5" height="12" rx="1.5"/></svg></button><button class="icon-btn sm" data-act="full-open"')
    d.rep('aria-label="Open the full-screen player"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M14 4h6v6M10 20H4v-6M20 4l-7 7M4 20l7-7"/></svg></button></div>',
          'aria-label="Open the full-screen player"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M14 4h6v6M10 20H4v-6M20 4l-7 7M4 20l7-7"/></svg></button></span></div>')
    d.before('/* ---------- loudness, for volume leveling ---------- */', ICONS + RT_JS)
    d.after("const ACT = {\n", ACTS)
    # the Play anywhere switch
    d.rep("glass: true, nameIt: true, improve: true, nav: 'scroll' };", "glass: true, nameIt: true, improve: true, nav: 'scroll', anywhere: true };")
    d.rep("'syncVideo', 'glass', 'nameIt', 'improve'].forEach(k =>", "'syncVideo', 'glass', 'nameIt', 'improve', 'anywhere'].forEach(k =>")
    d.rep("  if (k === 'nav') {", "  if (k === 'anywhere') rtSync();\n  if (k === 'nav') {")
    d.rep("      setRow('Sync videos', 'Kept videos go to your other devices too. Uses a lot more cloud space. Videos over 50 MB stay on the device they were added on.', swBtn('syncVideo', 'Sync videos'))) +",
          "      setRow('Sync videos', 'Kept videos go to your other devices too. Uses a lot more cloud space. Videos over 50 MB stay on the device they were added on.', swBtn('syncVideo', 'Sync videos'))) +\n    rtGroup() +")
    d.rep("'Glass effects': 'glass blur frosted transparent liquid see through',", "'Glass effects': 'glass blur frosted transparent liquid see through', 'Play anywhere': 'devices connect cast remote control other phone computer speaker swap transfer', 'This device': 'device name rename play anywhere',")
    d.rep("  rename(f) {", "  rtname(f) { const v = String(f.elements.dname.value || '').trim().slice(0, 30); try { if (v) localStorage.setItem('hp.devName', v); else localStorage.removeItem('hp.devName'); } catch (e) { /* not kept */ } closeSheet(); if (RT.joined) rtSend('presence', { type: 'presence', event: 'track', payload: rtMe() }); rtAcct(); render(); toast('This device is ' + devName() + '.'); },\n  rename(f) {")
    # what plays: on a device showing another one that plays, taps go to the one playing
    d.rep("function startQueue(ids, label, startId) {\n  if (!ids.length) return;",
          "function startQueue(ids, label, startId) {\n  if (!ids.length) return;\n  if (rtRoute('queue', { ids: ids.slice(0, 500), label, startId: startId || null, ctx: P.ctx })) return;")
    d.rep("function togglePlay() {\n  if (!P.cur) return;", "function togglePlay() {\n  if (rtRoute('toggle')) return;\n  if (!P.cur) return;")
    # changes on the playing device go out to the others
    d.rep("  try { localStorage.setItem('gymtapes.vol', String(VOL.v)); } catch (e) { /* not kept */ }\n  if (commit) volCommit();",
          "  try { localStorage.setItem('gymtapes.vol', String(VOL.v)); } catch (e) { /* not kept */ }\n  if (commit) volCommit();\n  if (RT && RT.active) rtSoon();")
    d.rep("  document.body.classList.toggle('no-glass', S.opt.glass === false);\n  navRest();", "  document.body.classList.toggle('no-glass', S.opt.glass === false);\n  navRest();\n  if (RT && RT.active) rtSoon();")
    d.rep("    SYNC.busy = false; SYNC.phase = ''; SYNC.upLeft = SYNC.downLeft = 0; syncShow(); if (SYNC.okAt && !SYNC.err) guideAfterSync();",
          "    SYNC.busy = false; SYNC.phase = ''; SYNC.upLeft = SYNC.downLeft = 0; syncShow(); if (SYNC.okAt && !SYNC.err) guideAfterSync(); rtSync();")
    d.rep("function syncStop() { SYNC.on = false;", "function syncStop() { SYNC.on = false; setTimeout(rtSync, 0);")
    d.rep("const VERSION = 'V14.2', NEWS = 'V14';", "const VERSION = 'V15', NEWS = 'V15';")
    d.rep("const WHATS_NEW = [\n", "const WHATS_NEW = [\n  ['Play anywhere', 'Signed in on your phone and your computer? They play as one now. Start on one and the other stops. Control the one playing from the other: play and pause, skip, volume, what plays. Tap the devices button to move it, same spot.'],\n")
    d.rep("window.__gymTapes = { isPC: () => isPC(),", "window.__gymTapes = { isPC: () => isPC(), RT, devName, rtSync,")
