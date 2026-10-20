# V10: keep the original video of video uploads, to watch full screen or save, with its own end clip switch,
# and backups that can take the videos along.
CSS = r'''
/* the original video */
.vview{position:fixed;inset:0;z-index:38;background:#000;color:#fff;display:flex;flex-direction:column;gap:8px;padding:calc(10px + env(safe-area-inset-top,0px)) 0 calc(12px + env(safe-area-inset-bottom,0px))}
.v-top{display:flex;align-items:center;gap:10px;padding:0 12px}
.vview .icon-btn{background:rgba(255,255,255,.16);color:#fff}
.v-title{flex:1;min-width:0;font-weight:700;font-size:15px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;text-align:center}
.v-save{display:inline-flex;align-items:center;gap:6px;min-height:40px;padding:0 15px;border-radius:999px;background:#fff;color:#000;font-weight:700;font-size:14px;flex:none}
.v-stage{flex:1;min-height:0;position:relative;display:flex;align-items:center;justify-content:center}
.v-stage video{width:100%;height:100%;object-fit:contain;background:#000}
.v-msg{position:absolute;left:0;right:0;top:50%;transform:translateY(-50%);margin:0;padding:0 24px;text-align:center;font-size:15px;opacity:.75}
.v-note{margin:0;padding:0 24px;min-height:18px;text-align:center;font-size:13px;opacity:.65}
body.v-on{overflow:hidden}
.f-watch{align-self:center;display:inline-flex;align-items:center;gap:7px;min-height:38px;padding:0 16px;border-radius:999px;background:var(--raise);font-weight:600;font-size:14px;margin-top:-4px}
'''

ICON_WATCH = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="3" y="5" width="18" height="14" rx="3"/><path d="M10 9.3v5.4l4.6-2.7z" fill="currentColor"/></svg>'
ICON_CLOSE = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" aria-hidden="true"><path d="M6 6l12 12M18 6L6 18"/></svg>'
ICON_SAVE = '<svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 4v11M7 10.5l5 5 5-5M5 20h14"/></svg>'

VIEWER = '''<section class="vview" id="vview" role="dialog" aria-label="Original video" hidden>
  <div class="v-top">
    <button class="icon-btn" data-act="v-close" aria-label="Close the video">''' + ICON_CLOSE + '''</button>
    <div class="v-title" id="vTitle"></div>
    <button class="v-save" id="vSave" data-act="v-save">''' + ICON_SAVE + '''Save video</button>
  </div>
  <div class="v-stage"><video id="vVideo" playsinline controls preload="auto" hidden></video><p class="v-msg" id="vMsg"></p></div>
  <p class="v-note" id="vNote" aria-live="polite"></p>
</section>

'''

VIDEO = r'''/* ---------- original videos: kept next to the sound, to watch or save ---------- */
/* Cuts the end off a video without re-encoding anything. Only the file's index changes: the frames and sound after the cut
   are left out of it, and everything that is kept is the exact same bytes as before, so nothing loses quality. */
const VCUT = (() => {
  const cc = (u8, o) => String.fromCharCode(u8[o], u8[o + 1], u8[o + 2], u8[o + 3]);
  function* kids(u8, start, end) {
    let o = start;
    while (o + 8 <= end) {
      const dv = new DataView(u8.buffer, u8.byteOffset + o, Math.min(16, end - o));
      let size = dv.getUint32(0), hdr = 8;
      if (size === 1) { if (o + 16 > end) return; size = dv.getUint32(8) * 4294967296 + dv.getUint32(12); hdr = 16; }
      else if (size === 0) size = end - o;
      if (size < hdr || o + size > end) return;
      yield { type: cc(u8, o + 4), start: o, body: o + hdr, end: o + size };
      o += size;
    }
  }
  const find = (u8, b, type) => { for (const k of kids(u8, b.body, b.end)) if (k.type === type) return k; return null; };
  const cat = parts => { let L = 0; for (const x of parts) L += x.length; const o = new Uint8Array(L); let p = 0; for (const x of parts) { o.set(x, p); p += x.length; } return o; };
  const box = (type, body) => { const o = new Uint8Array(8 + body.length); new DataView(o.buffer).setUint32(0, o.length); for (let i = 0; i < 4; i++) o[4 + i] = type.charCodeAt(i); o.set(body, 8); return o; };
  const u32s = arr => { const o = new Uint8Array(arr.length * 4), dv = new DataView(o.buffer); arr.forEach((v, i) => dv.setUint32(i * 4, v >>> 0)); return o; };
  const view = u8 => new DataView(u8.buffer, u8.byteOffset, u8.length);
  const get64 = (dv, o) => dv.getUint32(o) * 4294967296 + dv.getUint32(o + 4);
  const set64 = (dv, o, v) => { const hi = Math.floor(v / 4294967296); dv.setUint32(o, hi); dv.setUint32(o + 4, v - hi * 4294967296); };
  const raw = (u8, k) => u8.slice(k.start, k.end);
  const runs = (arr, n) => { const r = []; for (let i = 0; i < n; i++) { const v = arr[i]; if (r.length && r[r.length - 1] === v) r[r.length - 2]++; else r.push(1, v); } return r; };
  /* mvhd, mdhd and tkhd keep their time scale and length at different spots, depending on their version */
  const scaleOf = b => view(b).getUint32(b[0] === 1 ? 20 : 12);
  const lenAt = (kind, v1) => (kind === 'tkhd' ? (v1 ? 28 : 20) : (v1 ? 24 : 16));
  const getLen = (b, kind) => { const v1 = b[0] === 1; return v1 ? get64(view(b), lenAt(kind, v1)) : view(b).getUint32(lenAt(kind, v1)); };
  const setLen = (b, kind, v) => { const v1 = b[0] === 1; if (v1) set64(view(b), lenAt(kind, v1), v); else view(b).setUint32(lenAt(kind, v1), Math.min(v, 0xFFFFFFFF)); };
  const ORDER = ['stsd', 'stts', 'ctts', 'cslg', 'stss', 'stps', 'sdtp', 'stsc', 'stsz', 'stco', 'co64', 'sgpd', 'sbgp'];

  function cutTrak(m, trak, T, movieTs, shift) {
    const mdia = find(m, trak, 'mdia'), hdlr = mdia && find(m, mdia, 'hdlr'), kind = hdlr ? cc(m, hdlr.body + 8) : '';
    if (kind !== 'vide' && kind !== 'soun') return null;          // timecode, metadata and other side tracks are left out
    const tkhd = find(m, trak, 'tkhd'), mdhd = find(m, mdia, 'mdhd'), minf = find(m, mdia, 'minf'), stbl = minf && find(m, minf, 'stbl');
    if (!tkhd || !mdhd || !stbl) throw err('bad_file');
    const dv = view(m), ts = scaleOf(m.subarray(mdhd.body, mdhd.end)), tb = {};
    for (const k of kids(m, stbl.body, stbl.end)) tb[k.type] = k;
    const stsz = tb.stsz, stts = tb.stts, stsc = tb.stsc, co = tb.stco || tb.co64;
    if (!stsz || !stts || !stsc || !co || !ts) throw err('unsupported');
    const uniform = dv.getUint32(stsz.body + 4), n = dv.getUint32(stsz.body + 8);
    if (!n) throw err('unsupported');
    const durs = new Uint32Array(n), offs = new Int32Array(n);
    { let s = 0, last = 0; const c = dv.getUint32(stts.body + 4); for (let e = 0; e < c && s < n; e++) { const cnt = dv.getUint32(stts.body + 8 + 8 * e); last = dv.getUint32(stts.body + 12 + 8 * e); for (let k = 0; k < cnt && s < n; k++) durs[s++] = last; } while (s < n) durs[s++] = last; }
    if (tb.ctts) { let s = 0; const c = dv.getUint32(tb.ctts.body + 4); for (let e = 0; e < c && s < n; e++) { const cnt = dv.getUint32(tb.ctts.body + 8 + 8 * e), o = dv.getInt32(tb.ctts.body + 12 + 8 * e); for (let k = 0; k < cnt && s < n; k++) offs[s++] = o; } }
    /* the edit list says where showing starts inside the track, after any empty lead-in */
    const edts = find(m, trak, 'edts'), elst = edts && find(m, edts, 'elst');
    let mediaTime = 0, lead = 0;
    if (elst) {
      const v1 = m[elst.body] === 1, c = dv.getUint32(elst.body + 4);
      for (let e = 0; e < c; e++) {
        const b = elst.body + 8 + e * (v1 ? 20 : 12), sd = v1 ? get64(dv, b) : dv.getUint32(b), mt = v1 ? dv.getInt32(b + 8) * 4294967296 + dv.getUint32(b + 12) : dv.getInt32(b + 4);
        if (mt < 0) { lead += sd; continue; }
        mediaTime = mt; break;
      }
    }
    /* keep the samples, in the order they are stored, up to the first one that would show at or after the cut */
    const limit = T * ts, leadIn = lead / movieTs * ts;
    let N = 0, dts = 0, endPts = 0;
    while (N < n) { const pts = dts + offs[N] - mediaTime + leadIn; if (pts >= limit) break; endPts = Math.max(endPts, pts + durs[N]); dts += durs[N]; N++; }
    if (N < 1) throw err('bad_file');
    const whole = N === n, out = {}, put = (type, b) => { (out[type] = out[type] || []).push(b); };
    const full = (type, k, body) => box(type, cat([m.slice(k.body, k.body + 4), body]));        // keeps the version and flags
    for (const k of kids(m, stbl.body, stbl.end)) {
      switch (k.type) {
        case 'stsd': case 'sgpd': case 'cslg': put(k.type, raw(m, k)); break;
        case 'stts': { const r = runs(durs, N); put('stts', full('stts', k, u32s([r.length / 2].concat(r)))); break; }
        case 'ctts': {
          const r = runs(offs, N), b = new Uint8Array(4 + 4 * r.length), bd = view(b); bd.setUint32(0, r.length / 2);
          for (let i = 0; i < r.length; i += 2) { bd.setUint32(4 + 4 * i, r[i]); bd.setInt32(8 + 4 * i, r[i + 1]); }
          put('ctts', full('ctts', k, b)); break;
        }
        case 'stss': case 'stps': { const c = dv.getUint32(k.body + 4), keep = []; for (let e = 0; e < c; e++) { const s = dv.getUint32(k.body + 8 + 4 * e); if (s <= N) keep.push(s); } put(k.type, full(k.type, k, u32s([keep.length].concat(keep)))); break; }
        case 'stsz': put('stsz', full('stsz', k, uniform ? u32s([uniform, N]) : cat([u32s([0, N]), m.slice(k.body + 12, k.body + 12 + 4 * N)]))); break;
        case 'sdtp': put('sdtp', box('sdtp', m.slice(k.body, Math.min(k.end, k.body + 4 + N)))); break;
        case 'sbgp': {
          const h = m[k.body] === 1 ? 12 : 8, c = dv.getUint32(k.body + h), keep = []; let acc = 0;
          for (let e = 0; e < c && acc < N; e++) { const cnt = dv.getUint32(k.body + h + 4 + 8 * e), take = Math.min(cnt, N - acc); keep.push(take, dv.getUint32(k.body + h + 8 + 8 * e)); acc += take; }
          put('sbgp', box('sbgp', cat([m.slice(k.body, k.body + h), u32s([keep.length / 2].concat(keep))]))); break;
        }
        default: break;          // the chunk tables are rebuilt below; other per-sample tables are left out
      }
    }
    /* chunks: keep the ones that hold those samples, the last one possibly shorter */
    const nc = dv.getUint32(co.body + 4), is64 = co.type === 'co64', sc = dv.getUint32(stsc.body + 4), per = [], desc = [];
    const chunkAt = j => (is64 ? get64(dv, co.body + 8 + 8 * j) : dv.getUint32(co.body + 8 + 4 * j));
    let s = 0;
    for (let e = 0; e < sc && s < N; e++) {
      const b = stsc.body + 8 + 12 * e, first = dv.getUint32(b), spc = dv.getUint32(b + 4), sdi = dv.getUint32(b + 8), stop = e + 1 < sc ? dv.getUint32(b + 12) : nc + 1;
      for (let c = first; c < stop && c <= nc && s < N; c++) { const take = Math.min(spc, N - s); per.push(take); desc.push(sdi); s += take; }
    }
    if (s < N) throw err('bad_file');
    const rows = [];
    for (let c = 0; c < per.length; c++) if (!rows.length || rows[rows.length - 2] !== per[c] || rows[rows.length - 1] !== desc[c]) rows.push(c + 1, per[c], desc[c]);
    put('stsc', full('stsc', stsc, u32s([rows.length / 3].concat(rows))));
    const at = per.map((x, j) => shift(chunkAt(j)));
    if (at.some(o => o > 0xFFFFFFFF)) { const b = new Uint8Array(4 + 8 * at.length), bd = view(b); bd.setUint32(0, at.length); at.forEach((o, i) => set64(bd, 4 + 8 * i, o)); put('co64', full('co64', co, b)); }
    else put('stco', full('stco', co, u32s([at.length].concat(at))));
    const stblNew = box('stbl', cat([].concat(...ORDER.map(t => out[t] || []))));
    const swap = (k, to) => { const parts = []; for (const x of kids(m, k.body, k.end)) { const r = to(x); if (r) parts.push(r); } return box(k.type, cat(parts)); };
    const minfNew = swap(minf, x => (x.type === 'stbl' ? stblNew : raw(m, x)));
    const mdhdB = m.slice(mdhd.body, mdhd.end), tkhdB = m.slice(tkhd.body, tkhd.end);
    let len, edtsNew = edts ? raw(m, edts) : null;
    if (whole) len = getLen(tkhdB, 'tkhd');           // this track already ends before the cut
    else {
      let md = 0; for (let i = 0; i < N; i++) md += durs[i];
      setLen(mdhdB, 'mdhd', md);
      len = Math.max(0, Math.round(Math.min(endPts, limit) / ts * movieTs));      // how long it now shows for, in the movie's time units
      setLen(tkhdB, 'tkhd', len);
      if (elst) {
        const v1 = m[elst.body] === 1, w = v1 ? 20 : 12, c = dv.getUint32(elst.body + 4), ents = []; let acc = 0;
        for (let e = 0; e < c && acc < len; e++) {
          const ent = m.slice(elst.body + 8 + e * w, elst.body + 8 + (e + 1) * w), ed = view(ent), sd = Math.min(v1 ? get64(ed, 0) : ed.getUint32(0), len - acc);
          if (v1) set64(ed, 0, sd); else ed.setUint32(0, sd);
          acc += sd; ents.push(ent);
        }
        edtsNew = box('edts', box('elst', cat([m.slice(elst.body, elst.body + 4), u32s([ents.length])].concat(ents))));
      }
    }
    const mdiaNew = swap(mdia, x => (x.type === 'minf' ? minfNew : x.type === 'mdhd' ? box('mdhd', mdhdB) : raw(m, x)));
    const trakNew = swap(trak, x => (x.type === 'tkhd' ? box('tkhd', tkhdB) : x.type === 'mdia' ? mdiaNew : x.type === 'edts' ? edtsNew : x.type === 'tref' ? null : raw(m, x)));
    return { bytes: trakNew, len };
  }
  function rebuild(m, hdr, T, shift) {
    const top = { body: hdr, end: m.length };
    if (find(m, top, 'mvex')) throw err('unsupported');      // a file in fragments: not every sample is listed up front
    const mvhd = find(m, top, 'mvhd'); if (!mvhd) throw err('bad_file');
    const mv = m.slice(mvhd.body, mvhd.end), movieTs = scaleOf(mv), parts = []; let len = 0, kept = 0;
    if (!movieTs) throw err('bad_file');
    for (const k of kids(m, top.body, top.end)) {
      if (k.type === 'mvhd') continue;
      if (k.type !== 'trak') { parts.push(raw(m, k)); continue; }
      const r = cutTrak(m, k, T, movieTs, shift); if (!r) continue;
      parts.push(r.bytes); len = Math.max(len, r.len); kept++;
    }
    if (!kept) throw err('unsupported');
    setLen(mv, 'mvhd', len);
    return box('moov', cat([box('mvhd', mv)].concat(parts)));
  }
  /* the top level of the file, read a few bytes at a time */
  async function tops(blob) {
    const list = []; let o = 0;
    while (o + 8 <= blob.size) {
      if (list.length > 10000) throw err('bad_file');
      const h = new Uint8Array(await blob.slice(o, Math.min(blob.size, o + 16)).arrayBuffer()), dv = view(h);
      let size = dv.getUint32(0), hdr = 8, zero = false; const type = cc(h, 4);
      if (size === 1) { if (h.length < 16) throw err('bad_file'); size = get64(dv, 8); hdr = 16; }
      else if (size === 0) { size = blob.size - o; zero = true; }
      if (size < hdr || o + size > blob.size || !/^[\x20-\x7e]{4}$/.test(type)) throw err('bad_file');
      list.push({ type, start: o, end: o + size, hdr, zero }); o += size;
    }
    return list;
  }
  /* blob: the whole video, T: seconds to keep. Only the index is read into memory; the rest stays where it is. */
  async function cut(blob, T) {
    if (!(T > 0.5)) throw err('bad_file');
    const list = await tops(blob), mv = list.find(b => b.type === 'moov');
    if (!mv || list.some(b => b.type === 'moof')) throw err('unsupported');
    if (mv.end - mv.start > 96 * 1048576) throw err('bad_file');
    const m = new Uint8Array(await blob.slice(mv.start, mv.end).arrayBuffer()), size = mv.end - mv.start;
    const moov = rebuild(m, mv.hdr, T, o => (o >= mv.end ? o - size : o));      // the index moves to the end, so anything after its old spot moves up
    const parts = [];
    for (const b of list) {
      if (b === mv) continue;
      if (b.zero) {          // a box that ran "to the end of the file" gets its real size, since the index now comes after it
        const len = b.end - b.start; if (len > 0xFFFFFFFF) throw err('too_large');
        const h = new Uint8Array(8); view(h).setUint32(0, len); for (let i = 0; i < 4; i++) h[4 + i] = b.type.charCodeAt(i);
        parts.push(h, blob.slice(b.start + 8, b.end));
      } else parts.push(blob.slice(b.start, b.end));
    }
    parts.push(moov);
    return new Blob(parts, { type: 'video/mp4' });
  }
  return { cut };
})();

const VID = { open: null, cache: new Map(), missed: 0, full: false };
function hasVideo(t) { return !!(t && t.video && Array.isArray(t.video.parts) && t.video.parts.length); }
/* where the end clip starts in the video: the spot the sound gets cut at, counted from where showing starts */
function endTime(src, keep) { let a = 0; for (let i = 0; i < keep; i++) a += src.durs[i]; return Math.max(0, Math.round((a - (src.prime || 0)) / src.timescale * 1000) / 1000); }
/* the saved library takes files of up to 20 MB, so a bigger video goes in as pieces; on this device it is kept whole */
async function videoPieces(file) {
  const whole = file.type === 'video/mp4' ? file : new Blob([file], { type: 'video/mp4' });
  if (store.kind === 'local') return [whole];
  const MAX = 19 * 1048576, out = []; let a = 0;
  while (a < whole.size) {
    let b = Math.min(whole.size, a + MAX);
    /* the library turns away a file that starts like a web page, so no piece may start with "<" after blank space */
    while (b < whole.size && b > a + 64) {
      const h = new Uint8Array(await whole.slice(b, Math.min(whole.size, b + 64)).arrayBuffer()); let k = 0;
      while (k < h.length && (h[k] === 32 || (h[k] >= 9 && h[k] <= 13))) k++;
      if (k < h.length && h[k] !== 60) break;
      b -= k < h.length ? 1 : 64;
    }
    out.push(whole.slice(a, b, 'video/mp4')); a = b;
  }
  return out;
}
async function keepVideo(file, end, retry) {
  const pieces = await videoPieces(file), ids = [];
  try { for (const p of pieces) ids.push(await (retry ? retry(() => store.putBlob(p, 'video/mp4', true)) : store.putBlob(p, 'video/mp4', true))); }
  catch (e) { ids.forEach(id => store.delBlob(id)); throw e; }
  return { parts: ids, bytes: file.size, name: String(file.name || '').slice(0, 120), end: end > 0 ? end : null };
}
async function videoBlob(t) {
  if (!hasVideo(t)) throw err('missing');
  const parts = []; for (const id of t.video.parts) parts.push(await store.blob(id));
  return parts.length === 1 && parts[0].type === 'video/mp4' ? parts[0] : new Blob(parts, { type: 'video/mp4' });
}
const vidCut = t => (S.opt.videoEnd && hasVideo(t) && +t.video.end > 0.5 ? +t.video.end : 0);
const vidKey = t => t.id + '|' + t.video.parts.join(',') + '|' + vidCut(t);
/* the video as it will be watched or saved: with the end clip cut off when that is switched on. The last two are kept ready. */
function prepVideo(t) {
  const k = vidKey(t); let p = VID.cache.get(k);
  if (p) { VID.cache.delete(k); VID.cache.set(k, p); return p; }
  p = (async () => {
    const whole = await videoBlob(t), T = vidCut(t);
    if (!T) return { blob: whole, cut: false, failed: false, T: 0 };
    try { return { blob: await VCUT.cut(whole, T), cut: true, failed: false, T }; } catch (e) { return { blob: whole, cut: false, failed: true, T }; }
  })();
  p.then(r => { p.done = r; }, () => { if (VID.cache.get(k) === p) VID.cache.delete(k); });
  VID.cache.set(k, p);
  while (VID.cache.size > (store.kind === 'local' ? 2 : 1)) VID.cache.delete(VID.cache.keys().next().value);      // a fetched video sits in memory, so the saved library keeps just one
  return p;
}
function openVideo(id) {
  const t = track(id); if (!hasVideo(t)) return;
  closeSheet(); closeVideo();
  if (!audio.paused) audio.pause();          // one sound at a time
  const v = $('#vVideo'), msg = $('#vMsg'), o = { id, url: null, T: 0, failed: false };
  try { const pr = v.play(); if (pr && pr.catch) pr.catch(() => {}); } catch (e) { /* fine */ }      // asked inside the tap, so an iPhone lets it start by itself once it has loaded
  VID.open = o;
  $('#vTitle').textContent = t.title; $('#vNote').textContent = ''; msg.textContent = 'Getting the video ready'; msg.hidden = false; v.hidden = true;
  $('#vSave').hidden = !(DL || store.kind === 'local');
  $('#vview').hidden = false; document.body.classList.add('v-on');
  prepVideo(t).then(r => {
    if (VID.open !== o) return;
    o.url = URL.createObjectURL(r.blob); o.T = r.T; o.failed = r.failed;
    v.src = o.url; v.hidden = false; msg.hidden = true;
    $('#vNote').textContent = r.cut ? 'End clip cut off. You can change that in Settings.' : r.failed ? 'The end clip could not be cut out of this file, so it stops where the end clip starts.' : '';
    const pr = v.play(); if (pr && pr.catch) pr.catch(() => {});
  }).catch(() => { if (VID.open === o) msg.textContent = 'This video could not be loaded. Check your connection and try again.'; });
}
function closeVideo() {
  const o = VID.open; if (!o) return; VID.open = null;
  const v = $('#vVideo'); v.pause(); v.removeAttribute('src'); try { v.load(); } catch (e) { /* fine */ }
  if (o.url) URL.revokeObjectURL(o.url);
  $('#vview').hidden = true; document.body.classList.remove('v-on');
}
/* where the end clip could not be cut out of the file, playback stops where it starts instead */
$('#vVideo').addEventListener('timeupdate', () => { const o = VID.open, v = $('#vVideo'); if (o && o.failed && o.T && v.currentTime >= o.T) { v.pause(); v.currentTime = o.T; } });
const fileNameOf = t => String(t.title || 'upload').replace(/[\\/:*?"<>|\u0000-\u001f]+/g, ' ').trim().slice(0, 80) || 'upload';
function shareVideo(r, name) {
  const f = new File([r.blob], name, { type: 'video/mp4' });
  if (canShareFile(f)) navigator.share({ files: [f], title: name }).catch(e => { if (!e || e.name !== 'AbortError') downloadBlob(r.blob, name, 300000); });
  else downloadBlob(r.blob, name, 300000);
  if (r.failed) toast('This is the whole video. The end clip could not be cut out of this file.');
}
async function saveVideo(id) {
  const t = track(id); if (!hasVideo(t)) return;
  const name = fileNameOf(t) + '.mp4';
  if (DL) {          // the saved library: the app asks before saving, so the file can be got ready first
    toast('Getting the video ready');
    let r; try { r = await prepVideo(t); } catch (e) { return toast('This video could not be loaded. Check your connection and try again.'); }
    try { await DL.save({ filename: name, data: r.blob }); if (r.failed) toast('Saved the whole video. The end clip could not be cut out of this file.'); }
    catch (e) { const c = e && e.code; if (c !== 'declined') toast(c === 'rate_limited' ? 'Finish the save that is already open first.' : c === 'too_large' ? 'This video is too big to save here.' : 'Saving files is not available here.'); }
    return;
  }
  if (store.kind !== 'local') return;
  /* a phone only opens the share sheet straight from a tap, so the video has to be ready before the tap */
  const p = VID.cache.get(vidKey(t));
  if (p && p.done) return shareVideo(p.done, name);
  toast('Getting the video ready');
  let r; try { r = await prepVideo(t); } catch (e) { return toast('This video could not be loaded.'); }
  if (canShareFile(new File([r.blob], name, { type: 'video/mp4' }))) toast('Video ready.', { action: 'Save', ms: 20000, fn: () => shareVideo(r, name) });
  else shareVideo(r, name);
}
function backupChoice() {
  const vt = S.tracks.filter(hasVideo), aud = S.tracks.reduce((a, t) => a + (t.bytes || 0), 0), vid = vt.reduce((a, t) => a + (+t.video.bytes || 0), 0);
  sheet('<h2>Back up library</h2><p class="sub">' + (vt.length === 1 ? '1 upload has its' : vt.length + ' uploads have their') + ' original video. Videos make the backup a lot bigger.</p><div class="opts">' +
    opt('bk-video', 'With videos', { post: '<span class="tick">about ' + fmtBytes(aud + vid) + '</span>' }) +
    opt('bk-audio', 'Audio only', { post: '<span class="tick">about ' + fmtBytes(aud) + '</span>' }) +
    '</div><button class="btn" data-act="sheet-close">Cancel</button>', { kind: 'backup' });
}

'''

BACKUP = r'''async function crcBlob(b) { let c = 0xFFFFFFFF; for (let o = 0; o < b.size; o += 4194304) c = crc32.step(c, new Uint8Array(await b.slice(o, o + 4194304).arrayBuffer())); return (c ^ 0xFFFFFFFF) >>> 0; }
async function backupLibrary(withVideo) {
  if (BK.busy || !S.tracks.length) return; bkBusy(true);
  try {
    const files = [], seen = new Set(), tracks = S.tracks.slice().reverse(), kept = []; let missed = 0, vids = 0, vmissed = 0, i = 0;
    /* each file is read a few MB at a time to checksum it, then only the handle is kept, so a big library does not have to sit in memory */
    const entry = async (name, b) => ({ name, data: b, size: b.size, crc: await crcBlob(b) });
    const addImg = async id => { if (!id || seen.has(id)) return; seen.add(id); try { files.push(await entry('img/' + id + '.jpg', await store.blob(id))); } catch (e) { /* the picture is gone; the rest still counts */ } };
    for (const t of tracks) {
      bkSay('Packing ' + (++i) + ' of ' + tracks.length);
      try { files.push(await entry('audio/' + t.asset + '.mp4', await store.blob(t.asset))); } catch (e) { missed++; continue; }
      kept.push(t); await addImg(t.cover);
      if (withVideo && hasVideo(t)) { try { files.push(await entry('video/' + t.id + '.mp4', await videoBlob(t))); vids++; } catch (e) { vmissed++; } }
    }
    for (const p of S.playlists) await addImg(p.cover);
    const bg = curBg(); if (bg.kind === 'wall') await addImg(bg.asset);
    const lib = { app: 'HighestPeak', v: 1, made: new Date().toISOString(), tracks: kept, playlists: S.playlists, settings: { bg, opts: S.opt, recent: S.recent, plays: S.plays, presets: S.presets, stats: { total: Math.round(ST.total), best: ST.best, days: ST.days } } };
    files.unshift({ name: 'library.json', data: new TextEncoder().encode(JSON.stringify(lib)) });
    const blob = zipBlob(files), d = new Date(), name = 'HighestPeak-backup-' + d.getFullYear() + '-' + String(d.getMonth() + 1).padStart(2, '0') + '-' + String(d.getDate()).padStart(2, '0') + '.zip';
    const what = countText(kept.length) + (vids ? ', ' + vids + (vids === 1 ? ' video' : ' videos') : '') + ', ' + fmtBytes(blob.size);
    const left = (missed ? ' ' + missed + ' could not be read and ' + (missed === 1 ? 'was' : 'were') + ' left out.' : '') + (vmissed ? ' ' + vmissed + (vmissed === 1 ? ' video' : ' videos') + ' could not be read and ' + (vmissed === 1 ? 'was' : 'were') + ' left out.' : '');
    bkSay('Saving ' + fmtBytes(blob.size));
    if (DL) await DL.save({ filename: name, data: blob });
    else {
      const file = new File([blob], name, { type: 'application/zip' });
      if (canShareFile(file)) { BK.file = file; bkSay('Backup ready: ' + what + '. Tap Save backup file.' + left); return; }
      downloadBlob(blob, name, 300000);
    }
    bkSay('Backup saved: ' + what + '.' + left);
  } catch (e) {
    const c = e && e.code;
    bkSay(c === 'declined' ? 'Backup not saved.' : c === 'rate_limited' ? 'Finish the save that is already open first.' : c === 'too_large' ? 'The library is too big to save as one file here.' + (withVideo ? ' Try Audio only.' : '')
      : c === 'extension_not_enabled' || c === 'rejected_extension' || c === 'unavailable' ? 'Saving a backup file is not available in this view of the app.' : 'The backup could not be made. Check your connection and try again.');
  } finally { bkBusy(false); }
}
'''

def apply(d):
    d.before('</style>', CSS)
    # on this device a save that fails (storage full) can be told apart, for videos, which are big enough for that to happen
    d.rep("    async putBlob(blob) { const id = newId(); blobs.set(id, blob); await run('blobs', 'readwrite', s => s.put(blob, id)).catch(() => {}); return id; },",
          "    async putBlob(blob, type, strict) { const id = newId(); blobs.set(id, blob); try { await run('blobs', 'readwrite', s => s.put(blob, id)); } catch (e) { if (strict) { blobs.delete(id); throw err('quota_exceeded'); } } return id; },")
    d.before('<section class="editor" id="editor"', VIEWER)
    d.after('<div class="f-cover" id="fCover"></div>\n',
            '    <button class="f-watch" id="fWatch" data-act="watch-cur" hidden>' + ICON_WATCH + 'Watch original</button>\n')
    # the file parser notes whether there is a picture as well as sound
    d.rep("    const extras = [];\n    for (const k of kids(moov, minf.body, minf.end))",
          "    let hasVideo = false;\n"
          "    for (const t of kids(moov, top.body, top.end)) { if (t.type !== 'trak') continue; const m = find(moov, t, 'mdia'), h = m && find(moov, m, 'hdlr'); if (h && cc(moov, h.body + 8) === 'vide') hasVideo = true; }\n"
          "    const extras = [];\n    for (const k of kids(moov, minf.body, minf.end))")
    d.rep("      n, timescale, lang, codec, prime, sizes, durs, offsets,\n", "      n, timescale, lang, codec, prime, sizes, durs, offsets, video: hasVideo,\n")
    # options
    d.rep("hPlaylists: true, hNewest: true };", "hPlaylists: true, hNewest: true, keepVideo: true, videoEnd: true };")
    d.rep("'hPlaylists', 'hNewest'].forEach(k =>", "'hPlaylists', 'hNewest', 'keepVideo', 'videoEnd'].forEach(k =>")
    d.before("/* ---------- adding videos ---------- */", VIDEO)
    # adding: a video file keeps its video, and the end clip is found for it even when the sound keeps its own end
    d.rep("  let full, payload;\n  try { const reader = MP4.fileReader(job.file), raw = await MP4.parse(reader); payload = await MP4.readAll(reader, raw); full = MP4.packed(raw); }",
          "  let full, payload, isVideo = false;\n  try { const reader = MP4.fileReader(job.file), raw = await MP4.parse(reader); payload = await MP4.readAll(reader, raw); full = MP4.packed(raw); isVideo = !!raw.video; }")
    d.rep("  let seq = range(full.n), cut = null;\n  if (S.opt.autoTrim) { jobStep(job, 'Checking the ending'); cut = await findEnding(payload, full); if (cut) seq = range(cut.keep); }",
          "  const keepVid = isVideo && S.opt.keepVideo && store.canWrite;\n"
          "  let seq = range(full.n), cut = null, vEnd = null;\n"
          "  if (S.opt.autoTrim || keepVid) {\n"
          "    jobStep(job, 'Checking the ending');\n"
          "    const hit = await findEnding(payload, full);\n"
          "    if (hit) { vEnd = endTime(full, hit.keep); if (S.opt.autoTrim) { cut = hit; seq = range(hit.keep); } }\n"
          "  }")
    d.rep("  if (typeof fp2.gain === 'number') doc.gain = fp2.gain;\n  await store.set('tracks', id, doc);",
          "  if (typeof fp2.gain === 'number') doc.gain = fp2.gain;\n"
          "  if (keepVid) {           // the sound is what matters: if the video cannot be kept, the upload still goes in without it\n"
          "    jobStep(job, 'Saving the video');\n"
          "    try { doc.video = await keepVideo(job.file, vEnd); } catch (e) { VID.missed++; if (e && (e.code === 'quota_exceeded' || e.code === 'quota_or_state')) VID.full = true; }\n"
          "  }\n"
          "  try { await store.set('tracks', id, doc); } catch (e) { if (doc.video) doc.video.parts.forEach(p => store.delBlob(p)); throw e; }")
    d.rep("  let added = 0, trimmedCount = 0, asked = 0;\n", "  let added = 0, trimmedCount = 0, asked = 0; VID.missed = 0; VID.full = false;\n")
    d.rep("  if (added) toast((added === 1 ? 'Upload added.' : added + ' uploads added.') + note);",
          "  const vnote = VID.missed ? ' ' + (VID.missed === 1 ? (added === 1 ? 'Its video' : '1 video') : VID.missed + ' videos') + ' could not be kept' + (VID.full ? ', storage is full.' : '.') : '';\n"
          "  if (added) toast((added === 1 ? 'Upload added.' : added + ' uploads added.') + note + vnote);")
    # deleting an upload deletes its video too
    d.rep("  await store.delBlob(t.asset); if (t.cover) store.delBlob(t.cover);",
          "  await store.delBlob(t.asset); if (t.cover) store.delBlob(t.cover);\n  if (hasVideo(t)) t.video.parts.forEach(p => store.delBlob(p));")
    # the options of an upload
    d.rep("'</h2><p class=\"sub\">' + fmt(t.dur) + ', ' + fmtBytes(t.bytes) + (n ?",
          "'</h2><p class=\"sub\">' + fmt(t.dur) + ', ' + fmtBytes(t.bytes) + (hasVideo(t) ? ', video ' + fmtBytes(t.video.bytes) : '') + (n ?")
    d.rep("  h += opt('m-next', 'Play next');\n  if (store.canWrite) {",
          "  h += opt('m-next', 'Play next');\n"
          "  if (hasVideo(t)) {\n"
          "    h += opt('m-watch', 'Watch original') + (DL || store.kind === 'local' ? opt('m-savevid', 'Save video') : '');\n"
          "    if (store.kind === 'local') prepVideo(t).catch(() => {});      // get it ready now, so Save video can open the share sheet straight from the tap\n"
          "  }\n"
          "  if (store.canWrite) {")
    # the big player
    d.rep("  const t = track(P.cur), el = $('#player');\n  el.hidden = !t;\n", "  const t = track(P.cur), el = $('#player');\n  el.hidden = !t; $('#fWatch').hidden = !hasVideo(t);\n")
    # settings and the Upload screen
    d.rep("const END_CLIP_SUB = ",
          "const KEEP_VID_SUB = 'Video files keep their video next to the sound, to watch or save later. Uses more space. Only for new uploads.';\n"
          "const END_VID_SUB = 'Watching or saving a kept video stops before the app logo and chime at the end. Off gives you the whole video.';\n"
          "const END_CLIP_SUB = ")
    d.rep("      setRow('Remove end clips', END_CLIP_SUB, swBtn('autoTrim', 'Remove end clips', 'autoTrimSwitch')) +\n",
          "      setRow('Remove end clips', END_CLIP_SUB, swBtn('autoTrim', 'Remove end clips', 'autoTrimSwitch')) +\n"
          "      setRow('Keep original videos', KEEP_VID_SUB, swBtn('keepVideo', 'Keep original videos')) +\n"
          "      setRow('Cut end clips from videos', END_VID_SUB, swBtn('videoEnd', 'Cut end clips from videos')) +\n")
    d.rep("    group('', setRow('Remove end clips', END_CLIP_SUB, swBtn('autoTrim', 'Remove end clips', 'upTrimSwitch')));",
          "    group('', setRow('Remove end clips', END_CLIP_SUB, swBtn('autoTrim', 'Remove end clips', 'upTrimSwitch')) + setRow('Keep original videos', KEEP_VID_SUB, swBtn('keepVideo', 'Keep original videos', 'upVideoSwitch')));")
    d.rep("'<h2>Add videos or audio</h2><p>Only the sound is kept. Pick as many as you want.</p>' +",
          "'<h2>Add videos or audio</h2><p>' + (S.opt.keepVideo ? 'The sound becomes an upload, and videos are kept to watch later.' : 'Only the sound is kept.') + ' Pick as many as you want.</p>' +")
    d.rep("<p class=\"sub\">Saves one file with every upload, cover, playlist, like and setting. Keep it somewhere safe, like Files or iCloud Drive.</p>",
          "<p class=\"sub\">Saves one file with every upload, cover, playlist, like and setting' + (S.tracks.some(hasVideo) ? ', and the videos if you want them' : '') + '. Keep it somewhere safe, like Files or iCloud Drive.</p>")
    # backups: checksums a piece at a time, and the videos when asked for
    d.rep("  return u8 => { let c = 0xFFFFFFFF; for (let i = 0; i < u8.length; i++) c = tb[(c ^ u8[i]) & 255] ^ (c >>> 8); return (c ^ 0xFFFFFFFF) >>> 0; };",
          "  const step = (c, u8) => { for (let i = 0; i < u8.length; i++) c = tb[(c ^ u8[i]) & 255] ^ (c >>> 8); return c; };\n"
          "  const f = u8 => (step(0xFFFFFFFF, u8) ^ 0xFFFFFFFF) >>> 0; f.step = step; return f;")
    d.cut("async function backupLibrary() {", "async function restoreLibrary(file) {", BACKUP)
    d.rep("    names: () => Array.from(map.keys()), has: n => map.has(n),\n",
          "    names: () => Array.from(map.keys()), has: n => map.has(n),\n"
          "    /* a stored entry comes back as a piece of the file itself, so a big video is never read into memory */\n"
          "    async blob(n, type) {\n"
          "      const f = map.get(n); if (!f) throw err('missing');\n"
          "      if (f.method !== 0) return new Blob([await this.bytes(n)], { type: type || '' });\n"
          "      const lh = new DataView(await file.slice(f.at, f.at + 30).arrayBuffer()); if (lh.byteLength < 30 || lh.getUint32(0, true) !== 0x04034b50) throw err('bad_file');\n"
          "      const from = f.at + 30 + lh.getUint16(26, true) + lh.getUint16(28, true); return file.slice(from, from + f.csz, type || '');\n"
          "    },\n")
    d.rep("const idMap = new Map(), plMap = new Map(), fresh = new Set(); let added = 0, skipped = 0, failed = 0, pls = 0, n = 0, full = false;",
          "const idMap = new Map(), plMap = new Map(), fresh = new Set(); let added = 0, skipped = 0, failed = 0, pls = 0, n = 0, full = false, vids = 0, vfail = 0, vfull = false;")
    d.rep("        const cover = await img(bt.cover); if (cover) doc.cover = cover;\n        S.gone.delete(bt.id);",
          "        const cover = await img(bt.cover); if (cover) doc.cover = cover;\n"
          "        const vn = pre + 'video/' + bt.id + '.mp4';\n"
          "        if (bt.video && z.has(vn) && !vfull) {\n"
          "          try { doc.video = await keepVideo(await z.blob(vn, 'video/mp4'), +bt.video.end || 0, again); doc.video.name = String(bt.video.name || '').slice(0, 120); vids++; }\n"
          "          catch (e) { vfail++; if (e && (e.code === 'quota_exceeded' || e.code === 'quota_or_state')) vfull = true; }\n"
          "        }\n"
          "        S.gone.delete(bt.id);")
    d.rep("    if (failed) bits.push(failed + ' could not be restored' + (full ? ' because storage is full.' : '.'));\n",
          "    if (failed) bits.push(failed + ' could not be restored' + (full ? ' because storage is full.' : '.'));\n"
          "    if (vids) bits.push(vids === 1 ? '1 video put back too.' : vids + ' videos put back too.');\n"
          "    if (vfail) bits.push(vfail + (vfail === 1 ? ' video' : ' videos') + ' could not be put back' + (vfull ? ' because storage is full.' : '.'));\n")
    # actions
    d.rep("  backup() { backupLibrary(); },", "  backup() { if (S.tracks.some(hasVideo)) backupChoice(); else backupLibrary(false); },")
    d.after("const ACT = {\n",
            "  'm-watch'() { const c = sheetCtx; closeSheet(); if (c) openVideo(c.id); },\n"
            "  'm-savevid'() { const c = sheetCtx; closeSheet(); if (c) saveVideo(c.id); },\n"
            "  'watch-cur'() { if (P.cur) openVideo(P.cur); },\n"
            "  'v-close'() { closeVideo(); },\n"
            "  'v-save'() { if (VID.open) saveVideo(VID.open.id); },\n"
            "  'bk-video'() { closeSheet(); backupLibrary(true); },\n"
            "  'bk-audio'() { closeSheet(); backupLibrary(false); },\n")
    d.rep("document.addEventListener('keydown', e => { if (e.key !== 'Escape') return; if (sheetOpen()) closeSheet(); else if (S.full) closeFull(); });",
          "document.addEventListener('keydown', e => { if (e.key !== 'Escape') return; if (VID.open) closeVideo(); else if (sheetOpen()) closeSheet(); else if (S.full) closeFull(); });")
    d.rep("window.__gymTapes = { MP4, S,", "window.__gymTapes = { MP4, VCUT, VID, prepVideo, videoBlob, S,")
