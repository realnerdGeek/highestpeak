# V16: gym + shareable. A rest timer (the music dips between sets, then beeps or jumps to your hype part), intervals
# (work and rest rounds with beeps over the music), a Hype button (jump to the hardest part of the upload and loop it),
# and a share card for your month (and your year in December). Plus the animated streak flame left over from V14.

CSS = r'''
/* ===================== V16: gym tools and the share card ===================== */
.gym-row{display:flex;flex-wrap:wrap;gap:8px;align-items:center}
.gym-row:empty{display:none}
.gym-chip{display:inline-flex;align-items:center;gap:6px;min-height:36px;padding:0 13px;border-radius:999px;background:var(--g-over);border:1px solid var(--g-line);font-weight:700;font-size:13px;color:var(--ink)}
.gym-chip svg{flex:none}
.gym-chip[aria-pressed="true"]{background:var(--accent);color:var(--on-accent);border-color:transparent}
.gym-chip.icon{width:36px;padding:0;justify-content:center}
.gym-live{flex:1;display:grid;grid-template-columns:minmax(0,1fr) auto;gap:4px 12px;align-items:center;padding:12px 14px;border-radius:18px;background:var(--g-over);border:1px solid var(--g-line);
  -webkit-backdrop-filter:blur(20px) saturate(170%);backdrop-filter:blur(20px) saturate(170%)}
body.no-glass .gym-live{background:var(--raise);-webkit-backdrop-filter:none;backdrop-filter:none}
.gym-live.work{border-color:color-mix(in srgb,var(--accent) 60%,transparent)}
.gym-l{font-size:13px;font-weight:700;color:var(--muted)}
.gym-live.work .gym-l{color:var(--accent-ink)}
.gym-t{font:800 34px/1 var(--round);letter-spacing:-.02em;font-variant-numeric:tabular-nums}
.gym-btns{grid-row:1 / span 2;grid-column:2;display:flex;gap:6px}
.gym-btns .btn{min-height:38px;padding:0 12px}
.gym-bar{grid-column:1 / -1;height:4px;border-radius:2px;background:color-mix(in srgb,var(--ink) 14%,transparent);overflow:hidden;margin-top:6px}
.gym-bar i{display:block;height:100%;width:0;background:var(--accent);border-radius:2px}
.player #pGym{display:none}
@media (min-width: 900px){
  .player #pGym{display:flex}
  .f-info{grid-template-rows:auto auto auto auto auto auto minmax(0,1fr) auto;grid-template-areas:"head head" "wave wave" "times times" "ctl vol" "chips chips" "gym gym" "side side" "keys keys"}
  .f-info>.gym-row{grid-area:gym}
  .full.gym .f-info>.gym-row{display:none}
}
@media (min-width: 900px) and (max-width: 1180px){
  .f-info{grid-template-rows:auto auto auto auto auto auto auto minmax(0,1fr) auto;grid-template-areas:"head head" "wave wave" "times times" "ctl ctl" "vol vol" "chips chips" "gym gym" "side side" "keys keys"}
}
.full.gym .gym-row{display:none}
/* the share card */
.share-prev{display:block;width:min(100%,300px);margin:4px auto 14px;border-radius:18px;box-shadow:0 20px 50px var(--shadow)}
.share-pick{display:flex;gap:8px;justify-content:center;margin-bottom:12px}
/* the streak flame flickers */
.stat-chip.lit svg:first-child{transform-origin:50% 90%;animation:flame 1.6s ease-in-out infinite}
@keyframes flame{0%,100%{transform:scale(1) rotate(0)}25%{transform:scale(1.08,.96) rotate(-4deg)}50%{transform:scale(.96,1.07) rotate(3deg)}75%{transform:scale(1.05,.97) rotate(-2deg)}}
@media (prefers-reduced-motion: reduce){.stat-chip.lit svg:first-child{animation:none}}
'''

JS = r'''
/* ===================== V16: gym tools =====================
   Rest: the music dips (or pauses, or keeps going) for the rest, three beeps count down, then it comes back up (and can
   jump to the hype part). Intervals: work and rest rounds with the same beeps; the music dips during each rest.
   Beeps are scheduled ahead on the sound clock, so they land on time even when the screen is locked. */
var GYM = { mode: null, phases: [], idx: -1, start: 0, end: 0, timer: 0, ctx: null, beeps: [], dipF: 1, paused: false, hype: null, said: '' };
const GYM_IC = {
  hype: '<svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M13 2L4 14h7l-1 8 9-12h-7z"/></svg>',
  rest: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" aria-hidden="true"><circle cx="12" cy="13" r="8"/><path d="M12 9v4l2.5 2.5M9 2h6"/></svg>',
  hiit: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M2 12h3l2-6 4 12 3-9 2 3h6"/></svg>',
  gear: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.1" stroke-linecap="round" aria-hidden="true"><path d="M4 7h10M18 7h2M4 17h4M12 17h8"/><circle cx="16" cy="7" r="2"/><circle cx="10" cy="17" r="2"/></svg>'
};
function gymOpts() {
  let o = {}; try { o = JSON.parse(localStorage.getItem('hp.gym') || '{}') || {}; } catch (e) { o = {}; }
  const pick = (v, ok, d) => ok.indexOf(v) >= 0 ? v : d;
  return { rest: pick(+o.rest, [30, 45, 60, 90, 120, 180], 60), end: pick(o.end, ['beep', 'hype'], 'beep'), music: pick(o.music, ['dip', 'keep', 'pause'], 'dip'),
    work: pick(+o.work, [20, 30, 40, 45, 60], 40), hrest: pick(+o.hrest, [10, 15, 20, 30], 20), rounds: pick(+o.rounds, [4, 6, 8, 10, 12], 8), voice: o.voice === true };
}
function gymSave(k, v) { const o = gymOpts(); o[k] = v; try { localStorage.setItem('hp.gym', JSON.stringify(o)); } catch (e) { /* not kept */ } }
const gymDipF = () => (GYM ? GYM.dipF : 1);
const fmtClock = s => { s = Math.max(0, Math.ceil(s)); return Math.floor(s / 60) + ':' + String(s % 60).padStart(2, '0'); };
/* the sound clock for beeps: the music's own when it goes through the sound processing, else one made inside the tap */
function gymCtx() {
  if (FX && FX.ctx) return FX.ctx;
  if (!GYM.ctx) { const C = window.AudioContext || window.webkitAudioContext; if (!C) return null; try { GYM.ctx = new C(); } catch (e) { return null; } }
  if (GYM.ctx.state === 'suspended') GYM.ctx.resume().catch(() => {});
  return GYM.ctx;
}
function beepAt(ms, long) {
  const c = gymCtx(); if (!c) return;
  const t = c.currentTime + Math.max(0, (ms - Date.now()) / 1000), o = c.createOscillator(), g = c.createGain(), len = long ? 0.42 : 0.13;
  o.type = 'sine'; o.frequency.value = long ? 1320 : 880;
  g.gain.setValueAtTime(0.0001, t); g.gain.exponentialRampToValueAtTime(0.4, t + 0.012); g.gain.exponentialRampToValueAtTime(0.0001, t + len);
  o.connect(g); g.connect(c.destination); o.start(t); o.stop(t + len + 0.05);
  GYM.beeps.push(o);
}
function gymBeeps() {          // 3 short beeps before every change, a long one at it
  gymClearBeeps();
  GYM.phases.forEach((p, i) => { if (i < GYM.idx || p.end < Date.now()) return; [3, 2, 1].forEach(s => { if (p.end - s * 1000 > Date.now() - 50) beepAt(p.end - s * 1000, false); }); beepAt(p.end, true); });
}
function gymClearBeeps() { GYM.beeps.forEach(o => { try { o.stop(); o.disconnect(); } catch (e) { /* done already */ } }); GYM.beeps = []; }
/* the dip: through the sound processing it is scheduled ahead (works with the screen locked); otherwise it is set as it happens */
function gymSetDip(f) {
  GYM.dipF = f;
  if (elVolume) [A0, A1].forEach(el => { try { el.volume = Math.max(0, Math.min(1, VOL.v * f)); } catch (e) { /* fine */ } });
  if (audio === A1 && FX.gain) applyGain();
}
function gymAutomate() {
  if (!GYM.mode || audio !== A1 || !FX.gain || !FX.ctx || GYM.opt.music !== 'dip') return;
  const g = FX.gain.gain, now = Date.now();
  GYM.phases.forEach((p, i) => { if (i <= GYM.idx || p.start < now) return; try { g.setTargetAtTime(FX.base0 * (p.dip ? 0.25 : 1), FX.ctx.currentTime + (p.start - now) / 1000, 0.06); } catch (e) { /* fine */ } });
  const last = GYM.phases[GYM.phases.length - 1]; if (last) { try { g.setTargetAtTime(FX.base0, FX.ctx.currentTime + Math.max(0, (last.end - now) / 1000), 0.06); } catch (e) { /* fine */ } }
}
/* the music goes through the sound processing for the session, so the dip can be scheduled (inside the tap on iPhones) */
function gymWakeFx() {
  const t = track(P.cur); if (!t || !gainVolume || audio === A1 || audio.paused) return;
  VOL.useFx = true; const c = P.counted; playAt(t, curAbs()); P.counted = c;
}
function gymStart(kind, o) {
  gymStop(true); const opt = Object.assign(gymOpts(), o || {}), now = Date.now(); GYM.opt = opt;
  if (kind === 'rest') GYM.phases = [{ kind: 'rest', start: now, end: now + opt.rest * 1000, dip: opt.music === 'dip' }];
  else {
    GYM.phases = [{ kind: 'ready', start: now, end: now + 3000, dip: false }]; let t = now + 3000;
    for (let r = 1; r <= opt.rounds; r++) {
      GYM.phases.push({ kind: 'work', round: r, start: t, end: t + opt.work * 1000, dip: false }); t += opt.work * 1000;
      if (r < opt.rounds) { GYM.phases.push({ kind: 'rest', round: r, start: t, end: t + opt.hrest * 1000, dip: opt.music !== 'keep' }); t += opt.hrest * 1000; }
    }
  }
  GYM.mode = kind; GYM.idx = -1; GYM.start = now; GYM.end = GYM.phases[GYM.phases.length - 1].end; GYM.said = '';
  gymCtx();                                         // made inside the tap, so it is allowed to sound
  if (opt.music === 'dip' || kind === 'hiit') gymWakeFx();
  if (kind === 'rest' && opt.music === 'pause' && !audio.paused) { GYM.paused = true; audio.pause(); }
  gymBeeps(); clearInterval(GYM.timer); GYM.timer = setInterval(gymTick, 200); gymTick(); gymAutomate();
  gymDraw();
}
function gymStop(quiet) {
  const was = GYM.mode; clearInterval(GYM.timer); GYM.timer = 0; gymClearBeeps();
  GYM.mode = null; GYM.phases = []; GYM.idx = -1;
  if (GYM.dipF !== 1) gymSetDip(1); else if (audio === A1 && FX.gain) applyGain();
  if (GYM.paused) { GYM.paused = false; if (!quiet && audio.paused && track(P.cur)) togglePlay(); }
  if (was && !quiet) gymDraw();
  return was;
}
function gymSay(w) { if (!GYM.opt || !GYM.opt.voice || !window.speechSynthesis || GYM.said === w) return; GYM.said = w; try { speechSynthesis.cancel(); speechSynthesis.speak(new SpeechSynthesisUtterance(w)); } catch (e) { /* fine */ } }
function gymTick() {
  if (!GYM.mode) return;
  const now = Date.now();
  if (now >= GYM.end) {                             // done
    const kind = GYM.mode, hype = kind === 'rest' && GYM.opt.end === 'hype';
    gymSay(kind === 'rest' ? 'Go' : 'Done'); gymStop(false);
    if (hype) hypeGo(false);
    toast(kind === 'rest' ? 'Rest is over. Go!' : 'Intervals done. Nice work.');
    return;
  }
  const i = GYM.phases.findIndex(p => now >= p.start && now < p.end);
  if (i !== GYM.idx && i >= 0) {
    GYM.idx = i; const p = GYM.phases[i];
    gymSetDip(p.dip ? 0.25 : 1); gymAutomate();
    if (GYM.mode === 'hiit') gymSay(p.kind === 'work' ? (p.round === GYM.opt.rounds ? 'Last round. Go' : 'Go') : p.kind === 'rest' ? 'Rest' : 'Get ready');
    gymDraw();
  }
  gymTime();
}
function gymLabel() {
  const p = GYM.phases[GYM.idx]; if (!p) return '';
  if (GYM.mode === 'rest') return 'Rest';
  if (p.kind === 'ready') return 'Get ready';
  return (p.kind === 'work' ? 'Work' : 'Rest') + ' · Round ' + p.round + ' of ' + GYM.opt.rounds;
}
function gymTime() {
  const p = GYM.phases[GYM.idx]; if (!p) return;
  const left = (p.end - Date.now()) / 1000, pct = Math.min(100, (Date.now() - p.start) / (p.end - p.start) * 100);
  all('.gym-t', e => { e.textContent = fmtClock(left); }); all('.gym-bar i', e => { e.style.width = pct + '%'; });
  const m = $('#pMeta'); if (m && !isPC()) m.textContent = gymLabel() + ' ' + fmtClock(left);
}
/* the row under the controls: Hype, Rest, Intervals and the options; while one runs, the countdown */
function gymRow() {
  if (!track(P.cur)) return '';
  if (GYM.mode) {
    const p = GYM.phases[GYM.idx] || GYM.phases[0], work = p && p.kind === 'work';
    return '<div class="gym-live' + (work ? ' work' : '') + '"><span class="gym-l">' + esc(gymLabel()) + '</span><span class="gym-btns">' +
      (GYM.mode === 'rest' ? '<button class="btn sm" data-act="gym-more">+15 s</button>' : '') +
      '<button class="btn sm" data-act="gym-skip">Skip</button><button class="btn sm" data-act="gym-stop">Stop</button></span>' +
      '<span class="gym-t">' + fmtClock(p ? (p.end - Date.now()) / 1000 : 0) + '</span><span class="gym-bar"><i></i></span></div>';
  }
  const o = gymOpts(), on = !!(GYM.hype && GYM.hype.id === P.cur);
  return '<button class="gym-chip" data-act="hype" aria-pressed="' + on + '">' + GYM_IC.hype + 'Hype</button>' +
    '<button class="gym-chip" data-act="gym-rest">' + GYM_IC.rest + 'Rest ' + fmtClock(o.rest) + '</button>' +
    '<button class="gym-chip" data-act="gym-hiit">' + GYM_IC.hiit + o.work + '/' + o.hrest + ' × ' + o.rounds + '</button>' +
    '<button class="gym-chip icon" data-act="gym-opts" aria-label="Gym options">' + GYM_IC.gear + '</button>';
}
function gymDraw() { const h = gymRow(); all('.gym-row', el => { if (el.dataset.h !== h) { el.innerHTML = h; el.dataset.h = h; } }); gymTime(); }
function gymSheet() {
  const o = gymOpts(), seg = (k, cur, opts) => '<div class="seg" role="radiogroup">' + opts.map(x => '<button role="radio" aria-checked="' + (String(x[0]) === String(cur)) + '" data-act="gym-set" data-k="' + k + '" data-v="' + x[0] + '">' + x[1] + '</button>').join('') + '</div>';
  sheet('<h2>Gym</h2>' +
    '<div class="card"><div class="set col"><div><div class="set-t">Rest between sets</div><p class="sub">The music dips while you rest, three beeps count you down, then it comes back up.</p></div>' +
      seg('rest', o.rest, [[30, '0:30'], [45, '0:45'], [60, '1:00'], [90, '1:30'], [120, '2:00'], [180, '3:00']]) + '</div>' +
    '<div class="set col"><div><div class="set-t">Music while resting</div></div>' + seg('music', o.music, [['dip', 'Quieter'], ['keep', 'Keep it'], ['pause', 'Pause']]) + '</div>' +
    '<div class="set col"><div><div class="set-t">When the rest is over</div></div>' + seg('end', o.end, [['beep', 'Just beep'], ['hype', 'Jump to the hype part']]) + '</div></div>' +
    '<div class="card"><div class="set col"><div><div class="set-t">Intervals</div><p class="sub">Work, rest, repeat, with beeps over the music. The music dips during each rest.</p></div>' +
      '<span class="fld-l">Work</span>' + seg('work', o.work, [[20, '20 s'], [30, '30 s'], [40, '40 s'], [45, '45 s'], [60, '60 s']]) +
      '<span class="fld-l">Rest</span>' + seg('hrest', o.hrest, [[10, '10 s'], [15, '15 s'], [20, '20 s'], [30, '30 s']]) +
      '<span class="fld-l">Rounds</span>' + seg('rounds', o.rounds, [[4, '4'], [6, '6'], [8, '8'], [10, '10'], [12, '12']]) + '</div>' +
    setRow('Say Go and Rest', 'Says it out loud at each change, as well as the beeps.', '<button class="switch" id="sw-gymVoice" role="switch" aria-checked="' + o.voice + '" data-act="gym-voice" aria-label="Say Go and Rest"></button>') + '</div>' +
    '<div class="pair"><button class="btn primary" id="gymGoRest" data-act="gym-rest">Start rest</button><button class="btn primary" id="gymGoHiit" data-act="gym-hiit">Start intervals</button></div>' +
    '<button class="btn" data-act="sheet-close">Close</button>', { kind: 'gym' });
}
/* ----- Hype: the hardest part of the upload, looped ----- */
function hypeWindow(t) {
  if (t.sec && t.sec.b > t.sec.a) return { a: t.sec.a, b: t.sec.b };
  const pk = Array.isArray(t.peaks) ? t.peaks : [], n = pk.length, dur = t.dur || 0;
  if (!n || dur < 4) return { a: 0, b: dur };
  const w = Math.max(1, Math.round(Math.min(15, dur * 0.4) / dur * n));
  let best = -1, at = 0, sum = 0;
  for (let i = 0; i < n; i++) { sum += +pk[i] || 0; if (i >= w) sum -= +pk[i - w] || 0; if (i >= w - 1 && sum > best) { best = sum; at = i - w + 1; } }
  const a = Math.round(at / n * dur * 10) / 10; return { a, b: Math.min(dur, Math.round((a + w / n * dur) * 10) / 10) };
}
function hypeGo(loop) {
  const t = track(P.cur); if (!t) return;
  const w = hypeWindow(t); GYM.hype = { id: t.id, a: w.a, b: w.b, loop: loop !== false };
  seekAbs(t, w.a); if (audio.paused) togglePlay();
  gymDraw();
}
function hypeTick() {
  const h = GYM && GYM.hype; if (!h) return;
  if (P.cur !== h.id) { GYM.hype = null; gymDraw(); return; }
  if (h.loop && curAbs() >= h.b - 0.05) { const t = track(h.id); if (t) seekAbs(t, h.a); }
}
on('timeupdate', hypeTick);

/* ===================== V16: the share card =====================
   Your month (any time) or your year (in December), drawn here as a picture to share or save. Nothing is uploaded. */
const MON = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];
function monthKey(d) { const x = d || new Date(); return x.getFullYear() + '-' + String(x.getMonth() + 1).padStart(2, '0'); }
function statMonth(k) { ST.months = ST.months || {}; return ST.months[k] || (ST.months[k] = { s: 0, p: {} }); }
/* listening time and plays for a month ("2026-10") or a year ("2026"): the month counters, or the days if those have more */
function periodStats(key) {
  const inP = k => k.slice(0, key.length) === key;
  let s = 0, ms = 0; const dp = {}, mp = {};
  for (const k in ST.days) if (inP(k)) { const d = ST.days[k]; s += d.s || 0; for (const id in d.p) dp[id] = (dp[id] || 0) + d.p[id]; }
  for (const k in (ST.months || {})) if (inP(k)) { const m = ST.months[k]; ms += m.s || 0; for (const id in m.p) mp[id] = (mp[id] || 0) + m.p[id]; }
  const plays = {}; new Set(Object.keys(dp).concat(Object.keys(mp))).forEach(id => { if (track(id)) plays[id] = Math.max(dp[id] || 0, mp[id] || 0); });
  const top = Object.keys(plays).sort((a, b) => plays[b] - plays[a]).slice(0, 5).map(id => ({ t: track(id), n: plays[id] }));
  let days = 0; for (const k in ST.days) if (inP(k) && ST.days[k].s >= 60) days++;
  return { s: Math.max(s, ms), plays: Object.values(plays).reduce((a, b) => a + b, 0), top, days };
}
function rr(c, x, y, w, h, r) { c.beginPath(); c.moveTo(x + r, y); c.arcTo(x + w, y, x + w, y + h, r); c.arcTo(x + w, y + h, x, y + h, r); c.arcTo(x, y + h, x, y, r); c.arcTo(x, y, x + w, y, r); c.closePath(); }
async function drawCover(c, t, x, y, s) {
  c.save(); rr(c, x, y, s, s, s * 0.18); c.clip();
  let drawn = false;
  if (t.cover) { try { const im = new Image(); im.src = store.url(t.cover); await im.decode(); const k = Math.max(s / im.width, s / im.height); c.drawImage(im, x + (s - im.width * k) / 2, y + (s - im.height * k) / 2, im.width * k, im.height * k); drawn = true; } catch (e) { drawn = false; } }
  if (!drawn) {
    const a = auraOf(t.id); c.fillStyle = 'hsl(' + a.h + ' 70% 45%)'; c.fillRect(x, y, s, s);
    [[a.hb, a.x1, a.y1], [a.hc, a.x2, a.y2]].forEach(q => { const g = c.createRadialGradient(x + s * q[1] / 100, y + s * q[2] / 100, 0, x + s * q[1] / 100, y + s * q[2] / 100, s * 0.75); g.addColorStop(0, 'hsla(' + q[0] + ',85%,62%,.95)'); g.addColorStop(1, 'hsla(' + q[0] + ',85%,62%,0)'); c.fillStyle = g; c.fillRect(x, y, s, s); });
    const bars = coverBars(t), bw = s * 0.085, gap = s * 0.05, total = bars.length * bw + (bars.length - 1) * gap;
    c.fillStyle = 'rgba(255,255,255,.95)'; bars.forEach((h, i) => { const bh = s * h / 100, bx = x + (s - total) / 2 + i * (bw + gap); rr(c, bx, y + (s - bh) / 2, bw, bh, bw / 2); c.fill(); });
  }
  c.restore();
}
function fitText(c, txt, max) { let t = String(txt || ''); if (c.measureText(t).width <= max) return t; while (t.length > 1 && c.measureText(t + '…').width > max) t = t.slice(0, -1); return t + '…'; }
async function shareCard(key) {
  const st = periodStats(key), year = key.length === 4, W = 1080, H = 1920, cv = document.createElement('canvas'); cv.width = W; cv.height = H;
  const c = cv.getContext('2d'), F = (w, s) => w + ' ' + s + 'px ui-rounded, "SF Pro Rounded", "Nunito", system-ui, -apple-system, "Segoe UI", sans-serif';
  const h = st.top[0] ? hueOf(st.top[0].t.id) : 280;
  c.fillStyle = '#0A0A0D'; c.fillRect(0, 0, W, H);
  [[h, 160, 260, 900], [(h + 60) % 360, 980, 1500, 1000]].forEach(q => { const g = c.createRadialGradient(q[1], q[2], 0, q[1], q[2], q[3]); g.addColorStop(0, 'hsla(' + q[0] + ',80%,45%,.55)'); g.addColorStop(1, 'hsla(' + q[0] + ',80%,45%,0)'); c.fillStyle = g; c.fillRect(0, 0, W, H); });
  c.textBaseline = 'alphabetic'; c.fillStyle = '#FFFFFF'; c.font = F(800, 54); c.fillText('Ear', 90, 150); const ew = c.measureText('Ear').width; c.fillStyle = '#C8F135'; c.fillText('Worm', 90 + ew, 150);
  const [yy, mm] = key.split('-'), label = year ? 'Your ' + yy : 'Your ' + MON[(+mm || 1) - 1];
  c.fillStyle = '#FFFFFF'; c.font = F(900, 118); c.fillText(fitText(c, label, W - 180), 90, 330);
  c.fillStyle = 'rgba(255,255,255,.6)'; c.font = F(700, 44); c.fillText(year ? 'on EarWorm' : yy + ' on EarWorm', 90, 400);
  c.fillStyle = '#C8F135'; c.font = F(900, 150); c.fillText(fmtLong(st.s), 90, 600);
  c.fillStyle = 'rgba(255,255,255,.75)'; c.font = F(700, 44); c.fillText('listened', 90, 668);
  const facts = [[String(st.plays), st.plays === 1 ? 'play' : 'plays'], [String(st.days), st.days === 1 ? 'day you showed up' : 'days you showed up'], [String(Math.max(ST.best, streak())), 'day best streak']];
  facts.forEach((f, i) => { const y = 790 + i * 92; c.fillStyle = '#FFFFFF'; c.font = F(900, 64); c.fillText(f[0], 90, y); const fw = c.measureText(f[0]).width; c.fillStyle = 'rgba(255,255,255,.7)'; c.font = F(700, 40); c.fillText(f[1], 90 + fw + 22, y); });
  c.fillStyle = '#FFFFFF'; c.font = F(800, 50); c.fillText(st.top.length ? 'On repeat' : 'Nothing played yet', 90, 1130);
  for (let i = 0; i < st.top.length; i++) {
    const x = st.top[i], y = 1175 + i * 128; await drawCover(c, x.t, 90, y, 104);
    c.fillStyle = '#FFFFFF'; c.font = F(800, 42); c.fillText(fitText(c, (i + 1) + '. ' + x.t.title, W - 90 - 230 - 220), 230, y + 50);
    c.fillStyle = 'rgba(255,255,255,.6)'; c.font = F(700, 34); c.fillText(x.n + (x.n === 1 ? ' play' : ' plays'), 230, y + 94);
  }
  c.fillStyle = 'rgba(255,255,255,.55)'; c.font = F(700, 34); c.fillText('Loop your edits at the gym. Made with EarWorm.', 90, H - 110);
  const blob = await new Promise(res => cv.toBlob(res, 'image/png'));
  return { blob, name: 'EarWorm-' + label.replace(/^Your /, '').replace(/\s+/g, '-') + (year ? '' : '-' + yy) + '.png', label };
}
let SHARE = { url: '', card: null };
async function shareSheet(key) {
  key = key || monthKey();
  sheet('<h2>Share card</h2><p class="sub">Making your card...</p>', { kind: 'share' });
  const card = await shareCard(key); if (SHARE.url) URL.revokeObjectURL(SHARE.url);
  SHARE = { url: URL.createObjectURL(card.blob), card, key };
  const now = new Date(), prev = new Date(now.getFullYear(), now.getMonth() - 1, 15), dec = now.getMonth() === 11 || window.__HP_YEAR_CARD;
  const pick = (k, l) => '<button class="gym-chip" data-act="share-pick" data-k="' + k + '" aria-pressed="' + (k === key) + '">' + l + '</button>';
  if (!$('#sheetPanel') || !sheetCtx || sheetCtx.kind !== 'share') return;
  sheet('<h2>' + esc(card.label) + '</h2><div class="share-pick">' + pick(monthKey(now), MON[now.getMonth()]) + pick(monthKey(prev), MON[prev.getMonth()]) + (dec ? pick(String(now.getFullYear()), 'Your year') : '') + '</div>' +
    '<img class="share-prev" id="sharePrev" src="' + SHARE.url + '" alt="Your share card">' +
    '<div class="pair"><button class="btn" id="shareSave" data-act="share-save">Save</button><button class="btn primary" id="shareGo" data-act="share-go">Share</button></div>' +
    '<button class="btn" data-act="sheet-close">Close</button>', { kind: 'share' });
}
async function shareGo() {
  const c = SHARE.card; if (!c) return;
  const f = new File([c.blob], c.name, { type: 'image/png' });
  if (navigator.canShare && navigator.share && navigator.canShare({ files: [f] })) { try { await navigator.share({ files: [f], title: c.label + ' on EarWorm' }); return; } catch (e) { if (e && e.name === 'AbortError') return; } }
  downloadBlob(c.blob, c.name); toast('Saved the card.');
}
'''

ACTS = r'''  hype() { if (GYM.hype && GYM.hype.id === P.cur) { GYM.hype = null; gymDraw(); } else hypeGo(true); },
  'gym-rest'() { closeSheet(); gymStart('rest'); },
  'gym-hiit'() { closeSheet(); gymStart('hiit'); },
  'gym-opts'() { gymSheet(); },
  'gym-set'(d) { gymSave(d.k, isNaN(+d.v) ? d.v : +d.v); gymSheet(); gymDraw(); },
  'gym-voice'() { gymSave('voice', !gymOpts().voice); gymSheet(); },
  'gym-more'() { if (GYM.mode !== 'rest') return; const p = GYM.phases[0]; p.end += 15000; GYM.end = p.end; gymBeeps(); gymAutomate(); gymTime(); },
  'gym-skip'() { if (!GYM.mode) return; const now = Date.now(), p = GYM.phases[GYM.idx]; if (!p) return; const shift = p.end - now; GYM.phases.slice(GYM.idx).forEach((q, i) => { if (i) q.start -= shift; q.end -= shift; }); p.end = now; GYM.end -= shift; gymBeeps(); gymTick(); },
  'gym-stop'() { gymStop(false); },
  share() { shareSheet(); },
  'share-pick'(d) { shareSheet(d.k); },
  'share-go'() { shareGo(); },
  'share-save'() { if (SHARE.card) { downloadBlob(SHARE.card.blob, SHARE.card.name); toast('Saved the card.'); } },
'''

WHATS_NEW = r"""const WHATS_NEW = [
  ['Rest timer', 'Tap Rest in the big player between sets. The music dips, three beeps count you down, and it comes back up. Or jumps to your hype part.'],
  ['Intervals', 'Work and rest rounds with beeps over the music, like 40 on, 20 off, 8 rounds. Set it your way with the sliders button.'],
  ['Hype', 'One tap jumps to the hardest part of what is playing and loops it.'],
  ['Share your month', 'Stats has a card of your month to share or save: time listened, your top 5, your streak. In December, your year.'],
  ['Streak flame', 'Your streak on Home has a little fire now.']
];"""

def apply(d):
    d.before('</style>', CSS)
    d.rep('    <div class="chips" id="fChips"></div>', '    <div class="chips" id="fChips"></div>\n    <div class="gym-row" id="fGym"></div>')
    d.rep('<div class="chips" id="pChips"></div>', '<div class="chips" id="pChips"></div><div class="gym-row" id="pGym"></div>')
    d.before('/* ---------- loudness, for volume leveling ---------- */', JS)
    d.after("const ACT = {\n", ACTS)
    # the dip goes into the volume, both ways it is applied
    d.rep("const t = track(P.cur), g = (S.opt.level && t && typeof t.gain === 'number' ? Math.pow(10, t.gain / 20) : 1) * (gainVolume ? VOL.v : 1), ct = FX.ctx.currentTime;\n  FX.base = g;",
          "const t = track(P.cur), g0 = (S.opt.level && t && typeof t.gain === 'number' ? Math.pow(10, t.gain / 20) : 1) * (gainVolume ? VOL.v : 1), g = g0 * gymDipF(), ct = FX.ctx.currentTime;\n  FX.base0 = g0; FX.base = g;")
    d.rep("  try { FX.gain.gain.cancelScheduledValues(ct); FX.gain.gain.setTargetAtTime(g, ct, 0.03); } catch (e) { /* fine */ }\n}",
          "  try { FX.gain.gain.cancelScheduledValues(ct); FX.gain.gain.setTargetAtTime(g, ct, 0.03); } catch (e) { /* fine */ }\n  if (GYM && GYM.mode) gymAutomate();\n}")
    d.rep("  if (elVolume) [A0, A1].forEach(el => { try { el.volume = VOL.v; } catch (e) { /* fine */ } });",
          "  if (elVolume) [A0, A1].forEach(el => { try { el.volume = Math.max(0, Math.min(1, VOL.v * gymDipF())); } catch (e) { /* fine */ } });")
    d.rep("    if (gainVolume) VOL.useFx = volLow();", "    if (gainVolume) VOL.useFx = volLow() || !!(GYM && GYM.mode);")
    # the row under the controls follows the player
    d.rep("  navRest();\n  if (RT && RT.active) rtSoon();", "  navRest();\n  if (RT && RT.active) rtSoon();\n  if (GYM) gymDraw();")
    # months counted too, so the share card has a whole month (the days keep which uploads only for three weeks)
    d.rep("function notePlay(id) { S.plays[id] = (S.plays[id] || 0) + 1; saveRecent(false); const d = statDay(dayKey()); d.p[id] = (d.p[id] || 0) + 1; saveStats(false); }",
          "function notePlay(id) { S.plays[id] = (S.plays[id] || 0) + 1; saveRecent(false); const d = statDay(dayKey()); d.p[id] = (d.p[id] || 0) + 1; const m = statMonth(monthKey()); m.p[id] = (m.p[id] || 0) + 1; saveStats(false); }")
    d.rep("function addListen(sec) { if (!(sec > 0)) return; ST.total += sec; statDay(dayKey()).s += sec; saveStats(false); }",
          "function addListen(sec) { if (!(sec > 0)) return; ST.total += sec; statDay(dayKey()).s += sec; statMonth(monthKey()).s += sec; saveStats(false); }")
    d.rep("  const doc = { total: Math.round(ST.total), best: ST.best, days }, sig",
          "  const months = {}; Object.keys(ST.months || {}).sort().slice(-24).forEach(k => { const m = ST.months[k]; months[k] = { s: Math.round(m.s), p: m.p }; });\n  const doc = { total: Math.round(ST.total), best: ST.best, days, months }, sig")
    d.rep("    for (const id in p) { const to = map ? map.get(id) : id; if (to) d.p[to] = Math.max(d.p[to] || 0, Math.round(+p[id] || 0)); }\n  }\n}",
          "    for (const id in p) { const to = map ? map.get(id) : id; if (to) d.p[to] = Math.max(d.p[to] || 0, Math.round(+p[id] || 0)); }\n  }\n"
          "  const mons = doc.months && typeof doc.months === 'object' ? doc.months : {};\n"
          "  for (const k in mons) {\n    if (!/^\\d{4}-\\d\\d$/.test(k)) continue;\n    const r = mons[k] || {}, m = statMonth(k), p = r.p && typeof r.p === 'object' ? r.p : {};\n"
          "    m.s = Math.max(m.s, +r.s || 0);\n    for (const id in p) { const to = map ? map.get(id) : id; if (to) m.p[to] = Math.max(m.p[to] || 0, Math.round(+p[id] || 0)); }\n  }\n}")
    d.rep("const ST = { total: 0, best: 0, days: {},", "const ST = { total: 0, best: 0, days: {}, months: {},")
    # the share card button in Stats
    d.rep("    '<button class=\"btn\" data-act=\"sheet-close\">Close</button>', { kind: 'stats' });",
          "    '<button class=\"btn primary\" id=\"shareBtn\" data-act=\"share\">Share my month</button>' +\n    '<button class=\"btn\" data-act=\"sheet-close\">Close</button>', { kind: 'stats' });")
    # the streak flame flickers
    d.rep("  return '<div class=\"stat-chips\"><button class=\"stat-chip\" data-act=\"stats\">' + IC.flame", "  return '<div class=\"stat-chips\"><button class=\"stat-chip' + (s ? ' lit' : '') + '\" data-act=\"stats\">' + IC.flame")
    d.rep("const VERSION = 'V15', NEWS = 'V15';", "const VERSION = 'V16', NEWS = 'V16';")
    i = d.s.index('const WHATS_NEW = [\n'); j = d.s.index('\n];', i) + 3
    d.s = d.s[:i] + WHATS_NEW + d.s[j:]
    d.rep("window.__gymTapes = { isPC: () => isPC(),", "window.__gymTapes = { isPC: () => isPC(), GYM, gymStart, gymStop, hypeWindow, periodStats, shareCard, monthKey,")
