# V8 part 2: pick up where you left off, start delay (count-in), volume bar on computers
CSS = r'''
/* volume, on computers only */
.vol{display:flex;align-items:center;gap:8px;padding:0 2px}
.vol-ic{flex:none;width:36px;height:36px;display:grid;place-items:center;border-radius:50%;color:var(--muted)}
.vol input{flex:1;min-width:0;height:28px;margin:0;accent-color:var(--tint);cursor:pointer}
.player.mini .vol{display:none}
/* start delay */
.countdown{position:fixed;inset:0;z-index:35;display:grid;place-items:center;pointer-events:none}
.cd-in{width:184px;height:184px;border-radius:50%;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:4px;padding:0 20px;text-align:center;background:var(--glass);-webkit-backdrop-filter:saturate(180%) blur(24px);backdrop-filter:saturate(180%) blur(24px);border:1px solid var(--line);box-shadow:0 18px 50px var(--shadow)}
.cd-in b{font:800 80px/1 var(--font);letter-spacing:-.04em;font-variant-numeric:tabular-nums}
.cd-in span{max-width:140px;font-size:13px;font-weight:600;color:var(--muted);overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.cd-in b.pop{animation:cdPop .35s ease-out}
@keyframes cdPop{from{transform:scale(1.35);opacity:.35}to{transform:none;opacity:1}}
@media (prefers-reduced-motion: reduce){.cd-in b.pop{animation:none}}
'''

VOL_ROW = '<div class="vol" hidden><button class="vol-ic js-vol-ic" data-act="mute" aria-label="Mute"></button><input type="range" class="js-vol" min="0" max="100" step="1" value="100" aria-label="Volume"></div>'

PLAY = r'''/* ---------- start delay: a short count-in with beeps, then the upload ---------- */
const COUNTS = {};
let tapAt = 0, tapPlaying = false, swipeBlock = 0, swipeRow = null;
/* only a tap that starts sound from silence gets the count-in; the lock screen and the next upload in line never do */
const wantsCountIn = () => (+S.opt.delay || 0) > 0 && Date.now() - tapAt < 1500 && !tapPlaying;
/* the count-in is a real sound file (a beep each second, louder for the last three), so it keeps going with the phone locked */
function countInUrl(sec) {
  if (COUNTS[sec]) return COUNTS[sec];
  const rate = 22050, n = rate * sec, buf = new ArrayBuffer(44 + n * 2), v = new DataView(buf), w = (o, s) => { for (let i = 0; i < s.length; i++) v.setUint8(o + i, s.charCodeAt(i)); };
  w(0, 'RIFF'); v.setUint32(4, 36 + n * 2, true); w(8, 'WAVE'); w(12, 'fmt '); v.setUint32(16, 16, true); v.setUint16(20, 1, true); v.setUint16(22, 1, true);
  v.setUint32(24, rate, true); v.setUint32(28, rate * 2, true); v.setUint16(32, 2, true); v.setUint16(34, 16, true); w(36, 'data'); v.setUint32(40, n * 2, true);
  for (let k = 0; k < sec; k++) {
    const lastOne = k === sec - 1, f = lastOne ? 1320 : 880, len = Math.floor(rate * (lastOne ? 0.24 : 0.12)), amp = k >= sec - 3 ? 0.42 : 0.16;
    for (let i = 0; i < len; i++) { const env = Math.min(1, i / 110, (len - i) / 380); v.setInt16(44 + (k * rate + i) * 2, Math.round(Math.sin(2 * Math.PI * f * i / rate) * amp * env * 32767), true); }
  }
  return (COUNTS[sec] = URL.createObjectURL(new Blob([buf], { type: 'audio/wav' })));
}
function countLeft() { const c = P.countIn; if (!c) return 0; const d = isFinite(audio.duration) && audio.duration > 0 ? audio.duration : c.sec; return Math.max(1, Math.ceil(d - audio.currentTime - 0.05)); }
function hideCount() { const b = document.getElementById('countdown'); if (b) b.hidden = true; }
function updateCount() {
  const box = $('#countdown'), c = P.countIn;
  if (!c || audio.paused) return hideCount();
  const n = countLeft(), b = $('#cdNum'), t = track(c.id);
  if (box.hidden || b.textContent !== String(n)) { b.textContent = n; b.classList.remove('pop'); void b.offsetWidth; b.classList.add('pop'); }
  $('#cdTitle').textContent = t ? t.title : ''; box.hidden = false;
  $('#pMeta').textContent = 'Starting in ' + n;
}
function startCountIn(t, abs) {
  const sec = +S.opt.delay || 0; if (!sec) return playAt(t, abs);
  P.lid++;          // anything still waiting for the upload to load must not act on the count-in instead
  if (audio === A1) fxSetup();
  P.countIn = { id: t.id, abs: Math.max(0, abs || 0), sec, counted: P.cur === t.id && P.counted };
  audio.loop = false; audio.src = countInUrl(sec);
  try { audio.defaultPlaybackRate = 1; audio.playbackRate = 1; } catch (e) { /* fine */ }
  audio.play().catch(() => {});
  updateCount(); updatePlayer();
}
function finishCountIn() {
  const c = P.countIn; if (!c) return; hideCount();
  const t = track(c.id); P.countIn = null;
  if (!t) return updatePlayer();
  playAt(t, c.abs); if (c.abs > 0.05) P.counted = c.counted;
}
/* where to put the playhead for a spot given in seconds into the whole upload, with or without a saved section */
function seekAbs(t, abs, el) {
  el = el || audio;
  let p = P.sec && t.sec ? abs - t.sec.a : abs; if (P.pendingSec && t.sec) p = Math.max(t.sec.a, Math.min(abs, t.sec.b - 0.1));
  P.seekAt = Date.now();
  try { el.currentTime = Math.max(0, Math.min(p, (isFinite(el.duration) ? el.duration : p + 1) - 0.05)); } catch (e) { /* fine */ }
}
function playAt(t, abs) {
  setTrack(t, true, true);
  if (abs > 0.05) { const el = audio, lid = P.lid; el.addEventListener('loadedmetadata', () => { if (audio === el && P.cur === t.id && P.lid === lid) seekAbs(t, abs, el); }, { once: true }); }
}

/* ---------- pick up where you left off: the last queue and spot, kept on this device ---------- */
let sessionAt = 0;
function curAbs() {
  const t = track(P.cur); if (P.countIn) return P.countIn.abs;
  if (!audio.readyState && P.restoreAt != null) return P.restoreAt;
  if (audio.ended) return 0;
  return (audio.currentTime || 0) + (P.sec && t && t.sec ? t.sec.a : 0);
}
function saveSession(force) {
  if (!S.ready) return;              // before the library is in, there is nothing to save and the saved one must stay
  if (!force && Date.now() - sessionAt < 5000) return; sessionAt = Date.now();
  try {
    if (!track(P.cur) || !P.order.length) return localStorage.removeItem('gymtapes.session');
    localStorage.setItem('gymtapes.session', JSON.stringify({ cur: P.cur, queue: P.queue, order: P.order, pos: P.pos, label: P.label, ctx: P.ctx, abs: Math.round(curAbs() * 10) / 10, counted: !!(P.countIn ? P.countIn.counted : P.counted), at: Date.now() }));
  } catch (e) { /* not kept */ }
}
function restoreSession() {
  let s = null; try { s = JSON.parse(localStorage.getItem('gymtapes.session') || 'null'); } catch (e) { s = null; }
  if (!s || P.cur || typeof s.cur !== 'string' || !track(s.cur)) return;
  const have = id => typeof id === 'string' && !!track(id), uniq = a => a.filter((id, i) => have(id) && a.indexOf(id) === i);
  let order = uniq(Array.isArray(s.order) ? s.order : []); if (order.indexOf(s.cur) < 0) order = [s.cur].concat(order);
  const queue = uniq(Array.isArray(s.queue) ? s.queue : []);
  P.order = order; P.queue = queue.length ? queue.concat(order.filter(id => queue.indexOf(id) < 0)) : order.slice(); P.pos = order.indexOf(s.cur);
  P.label = typeof s.label === 'string' ? s.label : 'All uploads'; P.ctx = typeof s.ctx === 'string' ? s.ctx : 'all';
  const t = track(s.cur), abs = Math.max(0, +s.abs || 0);
  setTrack(t, false);
  P.restoreAt = abs > 0.5 && abs < (t.dur || 0) - 0.5 ? abs : null;      // shown in the player right away, applied once the audio is ready
  if (P.restoreAt != null) {
    if (s.counted) P.counted = true;           // this listen was already counted before the app closed
    const el = audio, lid = P.lid;
    el.addEventListener('loadedmetadata', () => { if (audio === el && P.cur === t.id && P.lid === lid && P.restoreAt != null) { seekAbs(t, P.restoreAt, el); P.restoreAt = null; progress(); } }, { once: true });
  }
  progress();
}

'''

VOLUME = r'''/* ---------- volume: only where the browser lets a page set it (computers). Phones keep using their own buttons. ---------- */
const canVolume = (() => { try { const a = document.createElement('audio'); a.volume = 0.5; return Math.abs(a.volume - 0.5) < 0.01; } catch (e) { return false; } })();
const VOL = { v: 1, last: 1 };
try { const v = parseFloat(localStorage.getItem('gymtapes.vol')); if (v >= 0 && v <= 1) VOL.v = v; } catch (e) { /* default */ }
function setVolume(v) {
  VOL.v = Math.max(0, Math.min(1, Math.round(v * 100) / 100)); if (VOL.v > 0) VOL.last = VOL.v;
  [A0, A1].forEach(el => { try { el.volume = VOL.v; } catch (e) { /* fine */ } });
  all('.js-vol', r => { if (document.activeElement !== r) r.value = Math.round(VOL.v * 100); r.setAttribute('aria-valuetext', Math.round(VOL.v * 100) + ' percent'); });
  all('.js-vol-ic', b => { b.innerHTML = VOL.v === 0 ? IC.volOff : VOL.v < 0.5 ? IC.volLow : IC.vol; b.setAttribute('aria-label', VOL.v === 0 ? 'Unmute' : 'Mute'); });
  try { localStorage.setItem('gymtapes.vol', String(VOL.v)); } catch (e) { /* not kept */ }
}
if (canVolume) { all('.vol', el => { el.hidden = false; }); setVolume(VOL.v); }
document.addEventListener('input', e => { if (canVolume && e.target && e.target.classList && e.target.classList.contains('js-vol')) setVolume(e.target.value / 100); });
'''

VOL_ICONS = r'''  vol: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M4 9.5h3.5L12 5.5v13l-4.5-4H4z"/><path d="M15.5 9a4 4 0 0 1 0 6M18.300 6.500a7.500 7.500 0 0 1 0 11"/></svg>',
  volLow: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M4 9.5h3.5L12 5.5v13l-4.5-4H4z"/><path d="M15.5 9a4 4 0 0 1 0 6"/></svg>',
  volOff: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M4 9.5h3.5L12 5.5v13l-4.5-4H4z"/><path d="M16 9.500l5 5M21 9.500l-5 5"/></svg>',
'''

def apply(d):
    d.rep("seekAt: 0, counted: false };", "seekAt: 0, counted: false, lid: 0 };")
    d.before('</style>', CSS)
    # ----- markup -----
    d.rep('<span id="loopLab" class="js-loop-lab">Loop off</span>\n      </button>\n    </div>\n', '<span id="loopLab" class="js-loop-lab">Loop off</span>\n      </button>\n    </div>\n    ' + VOL_ROW + '\n')
    d.rep('<span class="js-loop-lab">Loop off</span>\n      </button>\n    </div>\n', '<span class="js-loop-lab">Loop off</span>\n      </button>\n    </div>\n    ' + VOL_ROW + '\n')
    d.after('<div class="toast" id="toast" role="status" aria-live="polite" hidden></div>\n', '<div class="countdown" id="countdown" hidden aria-live="assertive"><div class="cd-in"><b id="cdNum">3</b><span id="cdTitle"></span></div></div>\n')
    d.rep("  tick: '<svg width=\"14\" height=\"14\"", VOL_ICONS + "  tick: '<svg width=\"14\" height=\"14\"")
    # ----- settings -----
    d.rep("      setRow('Keep the original pitch', 'Off gives the slowed or sped-up sound, where the pitch moves with the speed.', swBtn('keepPitch', 'Keep the original pitch')) +\n",
          "      setRow('Keep the original pitch', 'Off gives the slowed or sped-up sound, where the pitch moves with the speed.', swBtn('keepPitch', 'Keep the original pitch')) +\n"
          "      setCol('Start delay', o.delay ? 'Counts down ' + o.delay + ' seconds with a beep each second, then plays. Only when you tap play.' : 'Plays the moment you tap play.', seg('delay', o.delay, [[0, 'Off'], [3, '3 s'], [5, '5 s'], [10, '10 s']])) +\n")
    # ----- the player -----
    d.before("/* P.queue is the list as it was started, P.order is the same uploads in the order they will play */", PLAY)
    d.rep("function setTrack(t, autoplay) {\n  P.cur = t.id;", "function setTrack(t, autoplay, noCount) {\n  P.countIn = null; P.restoreAt = null; hideCount(); P.lid++;\n  P.cur = t.id;")
    d.rep("    const el = audio; el.addEventListener('loadedmetadata', () => { if (audio === el && P.cur === t.id && P.pendingSec) {", "    const el = audio, lid = P.lid; el.addEventListener('loadedmetadata', () => { if (audio === el && P.cur === t.id && P.lid === lid && P.pendingSec) {")
    d.rep("  if (autoplay) audio.play().catch(() => {});\n  if (S.opt.level) ensureGain(t);", "  if (autoplay) { if (!noCount && wantsCountIn()) startCountIn(t, 0); else audio.play().catch(() => {}); }\n  if (S.opt.level) ensureGain(t);")
    d.rep("  const r = +S.opt.speed || 1, keep = !!S.opt.keepPitch;", "  const r = P.countIn ? 1 : +S.opt.speed || 1, keep = !!S.opt.keepPitch;")
    d.rep("  setTrack(t, autoplay); if (autoplay) noteRecent(t.id);\n  render();\n}", "  setTrack(t, autoplay); if (autoplay) noteRecent(t.id);\n  render(); saveSession(true);\n}")
    d.rep("function reloadKeep() {\n  const t = track(P.cur); if (!t) return;", "function reloadKeep() {\n  const t = track(P.cur); if (!t || P.countIn) return;")
    d.rep("abs = audio.currentTime + (P.sec && t.sec ? t.sec.a : 0), counted = P.counted;\n  setTrack(t, false); P.counted = counted;\n  const el = audio;\n  el.addEventListener('loadedmetadata', () => {\n    if (audio !== el || P.cur !== t.id) return;",
          "abs = curAbs(), counted = P.counted;\n  setTrack(t, false); P.counted = counted;\n  const el = audio, lid = P.lid;\n  el.addEventListener('loadedmetadata', () => {\n    if (audio !== el || P.cur !== t.id || P.lid !== lid) return;")
    d.rep("audio.loop = S.loop === 'one' && T.loops !== 1; render(); updatePlayer(); },", "if (!P.countIn) audio.loop = S.loop === 'one' && T.loops !== 1; render(); updatePlayer(); },")
    d.rep("S.loop = S.loop === 'off' ? 'all' : S.loop === 'all' ? 'one' : 'off'; audio.loop = S.loop === 'one' && T.loops !== 1; savePrefs(); queueChanged(); },", "S.loop = S.loop === 'off' ? 'all' : S.loop === 'all' ? 'one' : 'off'; if (!P.countIn) audio.loop = S.loop === 'one' && T.loops !== 1; savePrefs(); queueChanged(); },")
    d.rep("  set('play', () => audio.play().catch(() => {}));", "  set('play', () => { if (audio === A1) fxSetup(); audio.play().catch(() => {}); });")
    d.rep("  if (audio.currentTime - startPos() > 3 || P.order.length === 1) { seekTo(startPos()); if (audio.paused) audio.play().catch(() => {}); return; }",
          "  if (audio.currentTime - startPos() > 3 || P.order.length === 1) {\n    const t = track(P.cur); if (audio.paused && t && wantsCountIn()) return startCountIn(t, secWanted(t) ? t.sec.a : 0);\n    seekTo(startPos()); if (audio.paused) audio.play().catch(() => {}); return;\n  }")
    d.rep("function prev() {\n  if (!P.order.length) return;\n", "function prev() {\n  if (!P.order.length) return;\n  if (P.countIn) { const t = track(P.countIn.id); if (t) startCountIn(t, 0); return; }      // back during the count-in starts it over\n")
    d.rep("""function togglePlay() {
  if (!P.cur) return;
  if (audio.paused) { audio.loop = S.loop === 'one' && T.loops !== 1; audio.play().catch(() => {}); } else audio.pause();
}""", """function togglePlay() {
  if (!P.cur) return;
  if (P.countIn) { if (audio.paused) audio.play().catch(() => {}); else audio.pause(); return; }
  if (audio.paused) {
    if (wantsCountIn()) { const t = track(P.cur); if (t) return startCountIn(t, curAbs()); }
    if (audio === A1) fxSetup();      // wake the sound processing inside the tap, or an iPhone may keep it silent
    audio.loop = S.loop === 'one' && T.loops !== 1; audio.play().catch(() => {});
  } else audio.pause();
}""")
    d.rep("P.sec = P.pendingSec = false; updatePlayer(); render(); }", "P.sec = P.pendingSec = false; P.countIn = null; P.restoreAt = null; hideCount(); updatePlayer(); render(); saveSession(true); }")
    d.rep("""  const d = isFinite(audio.duration) && audio.duration > 0 ? audio.duration : (track(P.cur) || {}).dur || 0;
  const f = d ? Math.min(1, audio.currentTime / d) : 0, a = fmt(audio.currentTime), b = fmt(d), pct = Math.round(f * 100);""",
          """  const t = track(P.cur), held = P.countIn ? P.countIn.abs : !audio.readyState && P.restoreAt != null ? P.restoreAt : null;     // during the count-in, or before a restored upload has loaded, show the spot it will start from
  let d, cur;
  if (held != null && t) { const s = P.sec && t.sec ? t.sec : null; d = s ? s.b - s.a : t.dur || 0; cur = s ? Math.max(0, held - s.a) : held; }
  else { d = isFinite(audio.duration) && audio.duration > 0 ? audio.duration : (t || {}).dur || 0; cur = audio.currentTime; }
  const f = d ? Math.min(1, cur / d) : 0, a = fmt(cur), b = fmt(d), pct = Math.round(f * 100);""")
    d.rep("    $('#pMeta').textContent = P.label + ', ' + where;", "    $('#pMeta').textContent = P.countIn ? (audio.paused ? 'Paused before the start' : 'Starting in ' + countLeft()) : P.label + ', ' + where;")
    d.rep("function queueChanged() { updatePlayer(); preloadNext(); }", "function queueChanged() { updatePlayer(); preloadNext(); saveSession(true); }")
    d.rep("function tick() {\n  const t = track(P.cur), cur = audio.currentTime, d = audio.duration;\n",
          "function tick() {\n  const t = track(P.cur), cur = audio.currentTime, d = audio.duration;\n"
          "  if (P.countIn) { updateCount(); return progress(); }\n"
          "  if (t && !audio.paused) { const now = Date.now(), dt = now - (ST.last || now); if (dt > 0 && dt < 3000) addListen(dt / 1000); ST.last = now; saveSession(false); }     // time listened, and the spot to come back to\n")
    d.rep("on('ended', () => {\n", "on('ended', () => {\n  if (P.countIn) return finishCountIn();\n")
    d.rep("on('play', () => { if (T.at && Date.now() >= T.at) T.at = 0;", "on('play', () => { ST.last = Date.now(); updateCount(); if (T.at && Date.now() >= T.at) T.at = 0;")
    d.rep("on('pause', () => { updatePlayer(); saveRecent(true); });", "on('pause', () => { updatePlayer(); updateCount(); saveRecent(true); saveStats(true); saveSession(true); ST.last = 0; });")
    d.rep("on('error', async () => {\n", "on('error', async () => {\n  if (P.countIn) return finishCountIn();          // if the count-in cannot play, just start\n")
    d.rep("  const seek = e => { const r = w.getBoundingClientRect(), d = audio.duration; if (!isFinite(d) || !d) return;", "  const seek = e => { const r = w.getBoundingClientRect(), d = audio.duration; if (P.countIn || !isFinite(d) || !d) return;")
    d.rep("const now = track(P.cur); if (now && now.id === t.id && P.pendingSec && secKey(now) === key) reloadKeep();", "const now = track(P.cur); if (now && now.id === t.id && P.pendingSec && secKey(now) === key && !P.countIn) reloadKeep();")
    d.before("/* ---------- loudness, for volume leveling ---------- */", VOLUME + "\n")
    # ----- data in, taps, leaving the page -----
    d.rep("  const now = track(P.cur);\n  if (now) {\n    if (now.asset !== P.asset)", "  const now = track(P.cur);\n  if (now && !P.countIn) {\n    if (now.asset !== P.asset)")
    d.rep("  if (first) freezeHome();", "  if (first) { freezeHome(); restoreSession(); }")
    d.rep("""document.addEventListener('click', e => {
  if (e.target === $('#sheet')) return closeSheet();
  const el = e.target.closest('[data-act]'); if (!el || el.disabled) return;
""", """document.addEventListener('click', e => {
  if (Date.now() < swipeBlock && swipeRow && swipeRow.contains(e.target)) { e.preventDefault(); return; }       // the tap that ends a swipe on a row is not a tap on it
  if (e.target === $('#sheet')) return closeSheet();
  const el = e.target.closest('[data-act]'); if (!el || el.disabled) return;
  tapAt = Date.now(); tapPlaying = !!track(P.cur) && !audio.paused && !P.countIn;
""")
    d.rep("window.addEventListener('pagehide', () => { flushDelete(); saveRecent(true); saveStats(true); });\ndocument.addEventListener('visibilitychange', () => { if (document.visibilityState === 'hidden') { flushDelete(); saveRecent(true); saveStats(true); } });",
          "window.addEventListener('pagehide', () => { flushDelete(); saveRecent(true); saveStats(true); saveSession(true); });\ndocument.addEventListener('visibilitychange', () => { if (document.visibilityState === 'hidden') { flushDelete(); saveRecent(true); saveStats(true); saveSession(true); } });")
    d.after("const ACT = {\n", "  mute() { setVolume(VOL.v > 0 ? 0 : VOL.last || 1); },\n")
