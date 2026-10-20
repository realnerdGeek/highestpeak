# V17: sound. Presets (Slowed + reverb, Sped up, Bass boost, 8D), EQ, reverb and 8D you can mix yourself, a fade between
# uploads, the BPM of every upload (shown on each row, sort by it, a 140+ filter, section edges that snap to the beat in
# the editor), and silence cut from the start and end of new uploads.

CSS = r'''
/* ===================== V17: sound ===================== */
.snd-tiles{display:grid;grid-template-columns:repeat(auto-fill,minmax(130px,1fr));gap:8px;margin:4px 0 14px}
.snd-tile{display:flex;flex-direction:column;align-items:flex-start;gap:4px;min-height:74px;padding:12px;border-radius:16px;background:var(--raise);text-align:left;border:1px solid transparent}
.snd-tile b{font-size:15px}
.snd-tile span{font-size:12px;color:var(--muted)}
.snd-tile[aria-pressed="true"]{border-color:var(--accent);background:color-mix(in srgb,var(--accent) 14%,var(--raise))}
.snd-tile[aria-pressed="true"] b{color:var(--accent-ink)}
.lib-filter{display:flex;gap:8px;margin:2px 0 10px}
.gym-chip.snd-on{background:color-mix(in srgb,var(--accent) 22%,var(--g-over));border-color:color-mix(in srgb,var(--accent) 50%,transparent)}
'''

JS = r'''
/* ===================== V17: sound =====================
   The sound goes through an EQ (low, mid, high), a reverb (made right here, no files) and a slow left-right sweep for 8D.
   It only runs when one of them is on; otherwise the plain player is used (the one that keeps playing with the phone
   locked on iPhones). */
const SND_PRESETS = {
  normal: { name: 'Normal', sub: 'As it was saved', speed: 1, keepPitch: false, eq: 'flat', verb: 'off', d8: false },
  slowed: { name: 'Slowed + reverb', sub: 'Lower, slower, roomy', speed: 0.85, keepPitch: false, eq: 'flat', verb: 'hall', d8: false },
  sped: { name: 'Sped up', sub: 'Faster and higher', speed: 1.25, keepPitch: false, eq: 'flat', verb: 'off', d8: false },
  bass: { name: 'Bass boost', sub: 'Heavier low end', speed: 1, keepPitch: false, eq: 'bass', verb: 'off', d8: false },
  d8: { name: '8D', sub: 'Moves around your head', speed: 1, keepPitch: false, eq: 'flat', verb: 'room', d8: true }
};
const EQ_DB = { flat: [0, 0, 0], bass: [8, -1, 0], treble: [-1, 0, 6], vocal: [-2, 4, 1] };
const sndOn = () => !!(S.opt.eq && S.opt.eq !== 'flat') || !!(S.opt.verb && S.opt.verb !== 'off') || !!S.opt.d8 || +S.opt.xfade > 0;
function sndPreset() { const o = S.opt; for (const k in SND_PRESETS) { const p = SND_PRESETS[k]; if ((+o.speed || 1) === p.speed && !!o.keepPitch === p.keepPitch && (o.eq || 'flat') === p.eq && (o.verb || 'off') === p.verb && !!o.d8 === p.d8) return k; } return ''; }
function makeIR(c, sec) {
  const n = Math.round(c.sampleRate * sec), b = c.createBuffer(2, n, c.sampleRate);
  for (let ch = 0; ch < 2; ch++) { const d = b.getChannelData(ch); let lp = 0; for (let i = 0; i < n; i++) { lp = lp * 0.6 + (Math.random() * 2 - 1) * 0.4; d[i] = lp * Math.pow(1 - i / n, 3.2); } }
  return b;
}
function sndBuild() {
  const c = FX.ctx, N = FX.n = {};
  N.low = c.createBiquadFilter(); N.low.type = 'lowshelf'; N.low.frequency.value = 110;
  N.mid = c.createBiquadFilter(); N.mid.type = 'peaking'; N.mid.frequency.value = 1800; N.mid.Q.value = 0.9;
  N.high = c.createBiquadFilter(); N.high.type = 'highshelf'; N.high.frequency.value = 6500;
  N.dry = c.createGain(); N.wet = c.createGain(); N.wet.gain.value = 0; N.verb = c.createConvolver();
  N.pan = c.createStereoPanner ? c.createStereoPanner() : null;
  FX.src.connect(N.low); N.low.connect(N.mid); N.mid.connect(N.high); N.high.connect(N.dry); N.high.connect(N.verb); N.verb.connect(N.wet);
  const out = N.pan || FX.gain; N.dry.connect(out); N.wet.connect(out);
  if (N.pan) { N.pan.connect(FX.gain); N.lfo = c.createOscillator(); N.lfo.frequency.value = 0.11; N.depth = c.createGain(); N.depth.gain.value = 0; N.lfo.connect(N.depth); N.depth.connect(N.pan.pan); N.lfo.start(); }
  N.irs = {};
  sndApply();
}
function sndApply() {
  const N = FX.n; if (!N || !FX.ctx) return;
  const c = FX.ctx, ct = c.currentTime, db = EQ_DB[S.opt.eq] || EQ_DB.flat, v = S.opt.verb || 'off';
  N.low.gain.setTargetAtTime(db[0], ct, 0.05); N.mid.gain.setTargetAtTime(db[1], ct, 0.05); N.high.gain.setTargetAtTime(db[2], ct, 0.05);
  if (v !== 'off' && !N.irs[v]) { N.irs[v] = makeIR(c, v === 'hall' ? 3.2 : 1.2); }
  if (v !== 'off' && N.verb.buffer !== N.irs[v]) { try { N.verb.buffer = N.irs[v]; } catch (e) { /* fine */ } }
  N.wet.gain.setTargetAtTime(v === 'hall' ? 0.42 : v === 'room' ? 0.22 : 0, ct, 0.08);
  N.dry.gain.setTargetAtTime(v === 'hall' ? 0.82 : 1, ct, 0.08);
  if (N.depth) N.depth.gain.setTargetAtTime(S.opt.d8 ? 0.85 : 0, ct, 0.2);
}
/* switching to (or off) the processing while something plays: the player changes inside the tap */
function sndSwitch() {
  const t = track(P.cur); if (FX.n) sndApply();
  if (!t || audio.paused || engineFor() === audio) return;
  const c = P.counted; playAt(t, curAbs()); P.counted = c;
}
function sndPick(k) {
  const p = SND_PRESETS[k]; if (!p) return;
  S.opt.speed = p.speed; S.opt.keepPitch = p.keepPitch; S.opt.eq = p.eq; S.opt.verb = p.verb; setOpt('d8', p.d8);
  applyRate(); sndSwitch();
}
function sndSheet() {
  const cur = sndPreset(), o = S.opt;
  const tile = k => '<button class="snd-tile" data-act="snd-pick" data-k="' + k + '" aria-pressed="' + (cur === k) + '"><b>' + SND_PRESETS[k].name + '</b><span>' + SND_PRESETS[k].sub + '</span></button>';
  sheet('<h2>Sound</h2><div class="snd-tiles">' + Object.keys(SND_PRESETS).map(tile).join('') + '</div>' +
    '<div class="card">' +
    setCol('EQ', 'Shapes the sound: more low end, more top, or the voice up front.', segCtl('eq', o.eq || 'flat', [['flat', 'Flat'], ['bass', 'Bass'], ['treble', 'Treble'], ['vocal', 'Vocal']])) +
    setCol('Reverb', 'A room around the sound. Hall is the slowed + reverb one.', segCtl('verb', o.verb || 'off', [['off', 'Off'], ['room', 'Room'], ['hall', 'Hall']])) +
    setRow('8D', 'The sound slowly moves from ear to ear. Best with headphones.', swBtn('d8', '8D')) +
    setCol('Speed', (+o.speed || 1) === 1 ? 'Normal speed.' : ((+o.speed < 1 ? 'Slowed to ' : 'Sped up to ') + o.speed + ' times.'), segCtl('speed', o.speed, [[0.75, '0.75×'], [0.85, '0.85×'], [1, '1×'], [1.15, '1.15×'], [1.25, '1.25×']])) +
    setCol('Fade between uploads', 'The end fades out and the next one fades in.', segCtl('xfade', +o.xfade || 0, [[0, 'Off'], [3, '3 s'], [6, '6 s']])) +
    '</div><button class="btn" data-act="sheet-close">Close</button>', { kind: 'sound' });
}
/* the fade between uploads (out at the end, in at the start), on the processing's volume */
var XF = { out: '', in: '' };
function xfTick() {
  const s = +S.opt.xfade || 0, t = track(P.cur);
  if (!s || !t || audio !== A1 || !FX.gain || audio.paused || P.countIn) return;
  const pos = audio.currentTime || 0, len = isFinite(audio.duration) ? audio.duration : t.dur || 0, last = S.loop === 'off' && P.pos >= P.order.length - 1;
  if (S.loop === 'one' || last || len < s * 3) return;
  const key = t.id + ':' + P.lid;
  if (len - pos <= s && XF.out !== key) { XF.out = key; const ct = FX.ctx.currentTime; try { FX.gain.gain.cancelScheduledValues(ct); FX.gain.gain.setValueAtTime(FX.base || 1, ct); FX.gain.gain.linearRampToValueAtTime(0.0001, ct + Math.max(0.2, len - pos)); } catch (e) { /* fine */ } }
}
on('timeupdate', xfTick);
/* the fade in starts once the next one is really playing (after the volume is set for it) */
function xfIn() {
  const s = +S.opt.xfade || 0, t = track(P.cur);
  if (!s || !t || audio !== A1 || !FX.gain || P.countIn || (audio.currentTime || 0) > 0.6) return;
  const key = t.id + ':' + P.lid; if (XF.in === key) return; XF.in = key;
  const ct = FX.ctx.currentTime; try { FX.gain.gain.cancelScheduledValues(ct); FX.gain.gain.setValueAtTime(0.0001, ct); FX.gain.gain.linearRampToValueAtTime(FX.base || 1, ct + s); } catch (e) { /* fine */ }
}
on('playing', () => setTimeout(xfIn, 0));

/* ===================== V17: BPM =====================
   Worked out on this device from the sound: how loud it gets every 10 ms, where it jumps, and how often those jumps
   repeat. Saved with the upload, so it is done once. */
function bpmFrom(buf) {
  const sr = buf.sampleRate, hop = Math.max(1, Math.round(sr / 100)), chs = [];
  for (let c = 0; c < buf.numberOfChannels; c++) chs.push(buf.getChannelData(c));
  const n = Math.floor(buf.length / hop); if (n < 400) return null;          // under 4 seconds: not enough to tell
  const env = new Float32Array(n); let prev = 0;
  for (let i = 0; i < n; i++) { let e = 0; for (let j = i * hop, k = j + hop; j < k; j++) { let x = 0; for (const ch of chs) x += ch[j]; e += x * x; } e = Math.sqrt(e / hop); const d = e - prev; env[i] = d > 0 ? d : 0; prev = e; }
  let mean = 0; for (let i = 0; i < n; i++) mean += env[i]; mean /= n; for (let i = 0; i < n; i++) env[i] = Math.max(0, env[i] - mean);
  const minL = 30, maxL = 100;                                   // 200 down to 60 BPM, in 10 ms steps
  const ac = new Float32Array(maxL + 2);
  for (let L = minL - 1; L <= maxL + 1; L++) { let s = 0; for (let i = L; i < n; i++) s += env[i] * env[i - L]; ac[L] = s / (n - L); }
  let best = minL; for (let L = minL; L <= maxL; L++) if (ac[L] > ac[best]) best = L;
  if (!(ac[best] > 0)) return null;
  const a = ac[best - 1], b = ac[best], c = ac[best + 1], den = a - 2 * b + c, lag = best + (den ? 0.5 * (a - c) / den : 0);
  let bpm = 6000 / lag; while (bpm < 80) bpm *= 2; while (bpm > 180) bpm /= 2;
  // where the beats fall: the start that lines up with the most jumps
  const L = 6000 / bpm; let off = 0, top = -1;
  for (let o = 0; o < L; o++) { let s = 0; for (let x = o; x < n; x += L) s += env[Math.round(x)] || 0; if (s > top) { top = s; off = o; } }
  return { bpm: Math.round(bpm), off: Math.round(off) / 100 };
}
async function bpmOfBlob(blob) { const buf = await decodeAudio(await blob.arrayBuffer(), 22050, 20000); return bpmFrom(buf); }
/* uploads from before V17 get theirs in the background, one at a time */
var BPMQ = { busy: false, tried: new Set() };
async function bpmFill() {
  if (BPMQ.busy || !S.ready || !store || !store.canWrite || document.visibilityState !== 'visible') return;
  const t = S.tracks.find(x => typeof x.bpm !== 'number' && !BPMQ.tried.has(x.id) && x.asset && (!store.has || store.has(x.asset))); if (!t) return;
  BPMQ.busy = true; BPMQ.tried.add(t.id);
  try { const blob = await store.blob(t.asset); const r = blob ? await bpmOfBlob(blob) : null; await store.update('tracks', t.id, r ? { bpm: r.bpm, beat: r.off } : { bpm: 0 }); }
  catch (e) { /* can't read this one here: leave it */ }
  finally { BPMQ.busy = false; }
}
setInterval(bpmFill, 2500);
const bpmText = t => (t && t.bpm > 0 ? t.bpm + ' BPM' : '');
/* in the editor, section edges land on the beat when they are close to one */
function beatSnap(t, x) {
  if (S.opt.snapBeat === false || !t || !(t.bpm > 0) || ED.undo.length) return x;
  const L = 60 / t.bpm, off = +t.beat || 0, k = Math.round((x - off) / L), y = off + k * L;
  return Math.abs(y - x) < L * 0.35 && y >= 0 && y <= ED.dur ? Math.round(y * 100) / 100 : x;
}
/* silence at the very start and end of a new upload: how many frames to drop each side (a little is left so nothing clips) */
function silenceEdges(fp, frameSec) {
  const n = fp.length; if (n < 20) return null;
  let max = 0; for (let i = 0; i < n; i++) if (fp[i] > max) max = fp[i];
  const thr = max * 0.03; let a = 0, b = n - 1;
  while (a < n && fp[a] <= thr) a++; while (b > a && fp[b] <= thr) b--;
  const keep = Math.ceil(0.05 / frameSec), lead = Math.max(0, a - keep), tail = Math.max(0, n - 1 - b - keep);
  if ((lead + tail) * frameSec < 0.4 || b - a < 20) return null;
  return { lead: lead * frameSec >= 0.3 ? lead : 0, tail: tail * frameSec >= 0.3 ? tail : 0 };
}
'''

ACTS = r'''  sound() { sndSheet(); },
  'snd-pick'(d) { sndPick(d.k); sndSheet(); gymDraw(); },
  'bpm-filter'() { S.bpmF = S.bpmF ? '' : 'fast'; render(); },
'''

WHATS_NEW = r"""const WHATS_NEW = [
  ['Sound presets', 'Slowed + reverb, Sped up, Bass boost and 8D, one tap each. Tap Sound in the big player.'],
  ['Mix it yourself', 'EQ (bass, treble, vocal), reverb (room or hall), 8D and speed, in the same place.'],
  ['Fade between uploads', 'The end fades out and the next fades in. Off, 3 or 6 seconds.'],
  ['BPM on every upload', 'Shown on each row. Sort by it, or tap 140+ BPM in Library for the fast ones. Older uploads get theirs in the background.'],
  ['Cleaner starts', 'Silence at the start and end of new uploads is cut off. Section edges in the editor snap to the beat.']
];"""

def apply(d):
    d.before('</style>', CSS)
    d.before('/* ---------- loudness, for volume leveling ---------- */', JS)
    d.after("const ACT = {\n", ACTS)
    # the processing: built with its EQ, reverb and 8D, used when any of them (or the fade) is on
    d.rep("      FX.ctx.createMediaElementSource(A1).connect(FX.gain); FX.gain.connect(FX.ctx.destination);",
          "      FX.src = FX.ctx.createMediaElementSource(A1); FX.gain.connect(FX.ctx.destination); sndBuild();")
    d.rep("const fxWanted = () => !!(S.opt.level || S.opt.fade > 0 || VOL.useFx);", "const fxWanted = () => !!(S.opt.level || S.opt.fade > 0 || VOL.useFx || sndOn());")
    # settings for it
    d.rep("glass: true, nameIt: true, improve: true, nav: 'scroll', anywhere: true };",
          "glass: true, nameIt: true, improve: true, nav: 'scroll', anywhere: true, eq: 'flat', verb: 'off', d8: false, xfade: 0, trimSilence: true, snapBeat: true };")
    d.rep("'syncVideo', 'glass', 'nameIt', 'improve', 'anywhere'].forEach(k =>", "'syncVideo', 'glass', 'nameIt', 'improve', 'anywhere', 'd8', 'trimSilence', 'snapBeat'].forEach(k =>")
    d.rep("  if (['full', 'scroll', 'small'].indexOf(o.nav) >= 0) d.nav = o.nav;",
          "  if (['full', 'scroll', 'small'].indexOf(o.nav) >= 0) d.nav = o.nav;\n  if (EQ_DB[o.eq]) d.eq = o.eq;\n  if (['off', 'room', 'hall'].indexOf(o.verb) >= 0) d.verb = o.verb;\n  if ([0, 3, 6].indexOf(+o.xfade) >= 0) d.xfade = +o.xfade;")
    d.rep("  setOpt(d.k, d.k === 'speed' || d.k === 'fade' || d.k === 'delay' ? +d.v : d.v); render();",
          "  setOpt(d.k, d.k === 'speed' || d.k === 'fade' || d.k === 'delay' || d.k === 'xfade' ? +d.v : d.v); render(); if (sheetCtx && sheetCtx.kind === 'sound') sndSheet();")
    d.rep("  if (k === 'anywhere') rtSync();", "  if (k === 'anywhere') rtSync();\n  if (k === 'eq' || k === 'verb' || k === 'd8' || k === 'xfade' || k === 'speed' || k === 'keepPitch') { sndSwitch(); if (typeof gymDraw === 'function') gymDraw(); }")
    d.rep("'Glass effects': 'glass blur frosted transparent liquid see through',",
          "'Glass effects': 'glass blur frosted transparent liquid see through', 'Trim silence': 'silence quiet start end cut gap', 'Snap to the beat': 'bpm beat tempo editor section snap',")
    d.rep("      setRow('Name new uploads', 'Right after an upload, ask what to call it.', swBtn('nameIt', 'Name new uploads')) +",
          "      setRow('Name new uploads', 'Right after an upload, ask what to call it.', swBtn('nameIt', 'Name new uploads')) +\n"
          "      setRow('Trim silence', 'Cuts the silence at the very start and end of new uploads.', swBtn('trimSilence', 'Trim silence')) +\n"
          "      setRow('Snap to the beat', 'In the editor, section edges land on the beat when they are close to one.', swBtn('snapBeat', 'Snap to the beat')) +")
    # the Sound button in the tools row (lit when something is on)
    d.rep("    '<button class=\"gym-chip icon\" data-act=\"gym-opts\" aria-label=\"Gym options\">' + GYM_IC.gear + '</button>';",
          "    '<button class=\"gym-chip' + (sndPreset() === 'normal' ? '' : ' snd-on') + '\" data-act=\"sound\">' + SND_IC + (sndPreset() && sndPreset() !== 'normal' ? SND_PRESETS[sndPreset()].name : sndPreset() === 'normal' ? 'Sound' : 'Custom sound') + '</button>' +\n"
          "    '<button class=\"gym-chip icon\" data-act=\"gym-opts\" aria-label=\"Gym options\">' + GYM_IC.gear + '</button>';")
    d.before("function gymRow() {", "const SND_IC = '<svg width=\"16\" height=\"16\" viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2.2\" stroke-linecap=\"round\" aria-hidden=\"true\"><path d=\"M4 10v4M8 7v10M12 4v16M16 8v8M20 11v2\"/></svg>';\n")
    # BPM: worked out for new uploads, shown on rows, sort and filter
    d.rep("  const doc = { title, asset, dur, bytes: out.blob.size, created: Date.now(), peaks: storedPeaks(fp2, seq) };",
          "  const doc = { title, asset, dur, bytes: out.blob.size, created: Date.now(), peaks: storedPeaks(fp2, seq) };\n"
          "  try { const r = await bpmOfBlob(out.blob); doc.bpm = r ? r.bpm : 0; if (r) doc.beat = r.off; } catch (e) { /* worked out later */ }")
    d.rep("  const meta = secWanted(t) ? fmt(t.sec.b - t.sec.a) + ', section of ' + fmt(t.dur) : fmt(t.dur), id = esc(t.id), name = esc(t.title);",
          "  const meta = (secWanted(t) ? fmt(t.sec.b - t.sec.a) + ', section of ' + fmt(t.dur) : fmt(t.dur)) + (t.bpm > 0 ? ' · ' + t.bpm + ' BPM' : ''), id = esc(t.id), name = esc(t.title);")
    d.rep("const SORTS = { new: 'Newest first', old: 'Oldest first', az: 'A to Z', long: 'Longest first', short: 'Shortest first', liked: 'Liked first', top: 'Most played first' };",
          "const SORTS = { new: 'Newest first', old: 'Oldest first', az: 'A to Z', long: 'Longest first', short: 'Shortest first', liked: 'Liked first', top: 'Most played first', bpm: 'Fastest BPM first' };")
    d.rep("  if (['new', 'old', 'az', 'long', 'short', 'liked', 'top'].indexOf(o.sort) >= 0) d.sort = o.sort;", "  if (['new', 'old', 'az', 'long', 'short', 'liked', 'top', 'bpm'].indexOf(o.sort) >= 0) d.sort = o.sort;")
    d.rep("  const k = S.opt.sort, list = S.tracks.slice();   // S.tracks is already newest first",
          "  const k = S.opt.sort, list = S.bpmF === 'fast' ? S.tracks.filter(t => t.bpm >= 140) : S.tracks.slice();   // S.tracks is already newest first; the 140+ BPM filter in Library")
    d.rep("  else if (k === 'top') list.sort((a, b) => (S.plays[b.id] || 0) - (S.plays[a.id] || 0));",
          "  else if (k === 'top') list.sort((a, b) => (S.plays[b.id] || 0) - (S.plays[a.id] || 0));\n  else if (k === 'bpm') list.sort((a, b) => (b.bpm || 0) - (a.bpm || 0));")
    d.rep("          '<button class=\"icon-btn\" data-act=\"sort\" aria-label=\"Sort uploads\">' + IC.sort + '</button><button class=\"btn sm\" id=\"libSelect\" data-act=\"sel-start\">Select</button></div>') +",
          "          '<button class=\"icon-btn\" data-act=\"sort\" aria-label=\"Sort uploads\">' + IC.sort + '</button><button class=\"btn sm\" id=\"libSelect\" data-act=\"sel-start\">Select</button></div>' +\n"
          "          (S.tracks.some(t => t.bpm > 0) ? '<div class=\"lib-filter\"><button class=\"gym-chip\" id=\"bpmFilter\" data-act=\"bpm-filter\" aria-pressed=\"' + (S.bpmF === 'fast') + '\">140+ BPM</button></div>' : '')) +")
    # the editor: edges snap to the beat
    d.rep("  if (which === 'a') ED.a = Math.max(0, Math.min(t, ED.b - gap)); else ED.b = Math.min(ED.dur, Math.max(t, ED.a + gap));",
          "  t = beatSnap(track(ED.id), t);\n  if (which === 'a') ED.a = Math.max(0, Math.min(t, ED.b - gap)); else ED.b = Math.min(ED.dur, Math.max(t, ED.a + gap));")
    # silence at the start and end of new uploads
    d.rep("  const src = Object.assign({}, full, { n: seq.length });\n  const out = MP4.mux(full, seq, cut ? MP4.gather(payload, full, seq) : payload);",
          "  let src = Object.assign({}, full, { n: seq.length });\n  let out = MP4.mux(full, seq, cut ? MP4.gather(payload, full, seq) : payload);\n"
          "  if (S.opt.trimSilence !== false && !window.__HP_KEEP_SILENCE && out.dur > 3) {      // (older tests keep their files exactly as they were)\n"
          "    try {\n"
          "      const fp0 = await framePeaks(new Uint8Array(await out.blob.arrayBuffer()), src), edge = silenceEdges(fp0, out.dur / seq.length);\n"
          "      if (edge && (edge.lead || edge.tail)) { seq = seq.slice(edge.lead, seq.length - edge.tail); src = Object.assign({}, full, { n: seq.length }); out = MP4.mux(full, seq, MP4.gather(payload, full, seq)); job.silence = true; }\n"
          "    } catch (e) { /* keep it as it is */ }\n"
          "  }")
    d.rep("const VERSION = 'V16', NEWS = 'V16';", "const VERSION = 'V17', NEWS = 'V17';")
    i = d.s.index('const WHATS_NEW = [\n'); j = d.s.index('\n];', i) + 3
    d.s = d.s[:i] + WHATS_NEW + d.s[j:]
    d.rep("window.__gymTapes = { isPC: () => isPC(),", "window.__gymTapes = { isPC: () => isPC(), FX, bpmFrom, bpmOfBlob, sndPreset, silenceEdges, beatSnap, BPMQ,")
