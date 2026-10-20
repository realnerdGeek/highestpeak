# V9: the volume bar works on iPhone, through the sound processing (iPhones ignore a page's own volume)
VOLUME = r'''/* ---------- volume ---------- */
/* On a computer the bar sets the player's own volume. iPhones ignore that (some views even pretend to accept it),
   so there the bar turns the sound processing up or down instead. */
const IOS = /iPad|iPhone|iPod/.test(navigator.userAgent) || (/Macintosh/.test(navigator.userAgent) && navigator.maxTouchPoints > 1);
const elVolume = !IOS && (() => { try { const a = document.createElement('audio'); a.volume = 0.5; return Math.abs(a.volume - 0.5) < 0.01; } catch (e) { return false; } })();
const gainVolume = !elVolume && !!(window.AudioContext || window.webkitAudioContext);
const canVolume = elVolume || gainVolume;
const VOL = { v: 1, last: 1, useFx: false, told: false };
try { const v = parseFloat(localStorage.getItem('gymtapes.vol')); if (v >= 0 && v <= 1) VOL.v = v; VOL.told = localStorage.getItem('gymtapes.voltold') === '1'; } catch (e) { /* default */ }
const volLow = () => gainVolume && VOL.v < 0.995;
function setVolume(v, commit) {
  VOL.v = Math.max(0, Math.min(1, Math.round(v * 100) / 100)); if (VOL.v > 0) VOL.last = VOL.v;
  if (elVolume) [A0, A1].forEach(el => { try { el.volume = VOL.v; } catch (e) { /* fine */ } });
  else if (gainVolume && audio === A1) applyGain();          // already going through the processing: follow the finger
  all('.js-vol', r => { if (document.activeElement !== r) r.value = Math.round(VOL.v * 100); r.setAttribute('aria-valuetext', Math.round(VOL.v * 100) + ' percent'); });
  all('.js-vol-ic', b => { b.innerHTML = VOL.v === 0 ? IC.volOff : VOL.v < 0.5 ? IC.volLow : IC.vol; b.setAttribute('aria-label', VOL.v === 0 ? 'Unmute' : 'Mute'); });
  try { localStorage.setItem('gymtapes.vol', String(VOL.v)); } catch (e) { /* not kept */ }
  if (commit) volCommit();
}
/* Moving the sound over to the processing happens when the finger lets go of the bar: that counts as a tap,
   and an iPhone only lets the other player start during a tap. Going back to the plain player waits for the next tap on play. */
function volCommit() {
  if (!gainVolume) return;
  if (volLow() && !VOL.useFx) {
    VOL.useFx = true;
    const t = track(P.cur);
    if (t && !P.countIn && !audio.paused && engineFor() !== audio) { const c = P.counted; playAt(t, curAbs()); P.counted = c; }
    if (!VOL.told) { VOL.told = true; try { localStorage.setItem('gymtapes.voltold', '1'); } catch (e) { /* fine */ } toast('On iPhone, a lower app volume uses extra sound processing. If it stops when you lock the phone, slide it back to full.'); }
  }
  if (audio === A1) { fxSetup(); applyGain(); }
}
if (canVolume) { all('.vol', el => { el.hidden = false; }); setVolume(VOL.v); }
document.addEventListener('input', e => { if (canVolume && e.target && e.target.classList && e.target.classList.contains('js-vol')) setVolume(e.target.value / 100); });
document.addEventListener('change', e => { if (canVolume && e.target && e.target.classList && e.target.classList.contains('js-vol')) setVolume(e.target.value / 100, true); });
document.addEventListener('touchend', e => { if (gainVolume && e.target && e.target.classList && e.target.classList.contains('js-vol')) volCommit(); });

'''

def apply(d):
    d.cut("/* ---------- volume: only where the browser lets a page set it (computers).", "/* ---------- swipes ---------- */", VOLUME)
    d.rep("const fxWanted = () => !!(S.opt.level || S.opt.fade > 0);", "const fxWanted = () => !!(S.opt.level || S.opt.fade > 0 || VOL.useFx);")
    d.rep("  const t = track(P.cur), g = S.opt.level && t && typeof t.gain === 'number' ? Math.pow(10, t.gain / 20) : 1, ct = FX.ctx.currentTime;",
          "  const t = track(P.cur), g = (S.opt.level && t && typeof t.gain === 'number' ? Math.pow(10, t.gain / 20) : 1) * (gainVolume ? VOL.v : 1), ct = FX.ctx.currentTime;")
    d.rep("  P.countIn = null; P.restoreAt = null; hideCount(); P.lid++;\n  P.cur = t.id;",
          "  P.countIn = null; P.restoreAt = null; hideCount(); P.lid++;\n"
          "  if (gainVolume) { if (volLow()) VOL.useFx = true; else if (Date.now() - tapAt < 1500) VOL.useFx = false; }      // back to the plain player only on a tap\n"
          "  P.cur = t.id;")
    d.rep("""    if (wantsCountIn()) { const t = track(P.cur); if (t) return startCountIn(t, curAbs()); }
    if (audio === A1) fxSetup();      // wake the sound processing inside the tap, or an iPhone may keep it silent""",
          """    if (wantsCountIn()) { const t = track(P.cur); if (t) return startCountIn(t, curAbs()); }
    if (gainVolume) VOL.useFx = volLow();
    if (engineFor() !== audio) { const t = track(P.cur); if (t) { const c = P.counted; playAt(t, curAbs()); P.counted = c; return; } }      // switch players inside the tap
    if (audio === A1) fxSetup();      // wake the sound processing inside the tap, or an iPhone may keep it silent""")
    d.rep("  P.lid++;          // anything still waiting for the upload to load must not act on the count-in instead\n  if (audio === A1) fxSetup();",
          "  P.lid++;          // anything still waiting for the upload to load must not act on the count-in instead\n"
          "  if (gainVolume) VOL.useFx = volLow();\n"
          "  const want = engineFor(); if (want !== audio) { audio.pause(); audio.removeAttribute('src'); try { audio.load(); } catch (e) { /* fine */ } audio = want; }      // the count-in plays on the player the upload will use\n"
          "  if (audio === A1) fxSetup();")
    d.rep("  mute() { setVolume(VOL.v > 0 ? 0 : VOL.last || 1); },", "  mute() { setVolume(VOL.v > 0 ? 0 : VOL.last || 1, true); },")
    d.rep("'<p class=\"sub note\">These two send the sound through extra processing. If playback stops when your phone locks while one is on, turn it off.</p>'",
          "'<p class=\"sub note\">These two send the sound through extra processing, and so does the volume bar on iPhone when it is below full. If playback stops when your phone locks, turn these off or slide the volume back to full.</p>'")
