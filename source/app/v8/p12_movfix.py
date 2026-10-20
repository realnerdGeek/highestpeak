# V10.1: end clips on .mov videos (photo posts turned into video on the phone).
# Their AAC sound is described the old QuickTime way, which the decoder used for finding end clips (and drawing waveforms)
# cannot read on iPhone. The sound gets rewritten the standard MP4 way when the file is read; the sound itself is the same bytes.
ISO = r'''  /* Videos made on a phone (QuickTime .mov files) describe their AAC sound the old QuickTime way. Phones play that fine, but the
     decoder used to find end clips and draw waveforms cannot read it, so the description is rewritten the standard MP4 way.
     Only the description changes: the sound itself is the same bytes. */
  const stdHdlr = () => box('hdlr', [[0, 0, 0, 0, 0, 0, 0, 0, 0x73, 0x6f, 0x75, 0x6e, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0x53, 0x6f, 0x75, 0x6e, 0x64, 0]]);
  const stdMinf = () => cat([box('smhd', [[0, 0, 0, 0, 0, 0, 0, 0]]), box('dinf', [box('dref', [[0, 0, 0, 0, 0, 0, 0, 1], box('url ', [[0, 0, 0, 1]])])])]);
  function findIn(u8, start, end, type) {
    for (const k of kids(u8, start, end)) { if (k.type === type) return u8.slice(k.start, k.end); if (k.type === 'wave') { const r = findIn(u8, k.body, k.end, type); if (r) return r; } }
    return null;
  }
  function isoAudio(src) {
    const s = src.stsd; if (src.codec !== 'mp4a' || s.length < 16 + 36) return src;
    const e = s.subarray(16), dv = new DataView(e.buffer, e.byteOffset, e.length), ver = dv.getUint16(16), size = Math.min(dv.getUint32(0), e.length);
    if (ver === 0 && !src.ftyp) return src;              // already the standard way
    let stsd = s;
    if (ver === 1 || ver === 2) {
      const esds = findIn(e, ver === 1 ? 52 : 72, size, 'esds'); if (!esds) return src;
      const ch = ver === 2 ? dv.getUint32(48) : dv.getUint16(24), head = new Uint8Array(28), hv = new DataView(head.buffer);
      hv.setUint16(6, 1); hv.setUint16(16, ch || 2); hv.setUint16(18, 16); hv.setUint32(24, Math.min(src.timescale, 65535) * 65536);
      stsd = box('stsd', [[0, 0, 0, 0, 0, 0, 0, 1], box('mp4a', [head, esds])]);
    } else if (ver !== 0) return src;
    return Object.assign({}, src, { stsd, hdlr: stdHdlr(), minfHead: stdMinf(), ftyp: null, fixed: true });
  }

'''

TRIM = r'''/* the end clip of a kept video, found from the video's own sound, so it lines up even when the upload's sound was edited */
async function videoEndOf(t) {
  const blob = await videoBlob(t), reader = MP4.fileReader(blob), raw = await MP4.parse(reader), payload = await MP4.readAll(reader, raw), full = MP4.packed(raw);
  const hit = await findEnding(payload, full); return hit ? endTime(full, hit.keep) : null;
}
async function trimEndingCore(t) {
  const u8 = await store.bytes(t.asset), src = await MP4.parse(MP4.bufReader(u8));
  const hit = await findEnding(u8, src); let did = false;
  if (hit) {
    const seq = range(hit.keep), out = MP4.mux(src, seq, MP4.gather(u8, src, seq));
    const peaks = storedPeaks(await framePeaks(await readable(u8, src), src), seq), old = t.asset, dur = Math.round(out.dur * 100) / 100;
    const asset = await store.putBlob(out.blob), patch = { asset, dur, bytes: out.blob.size, peaks };
    if (t.sec && t.sec.b > dur) patch.sec = null;
    await store.update('tracks', t.id, patch);
    store.delBlob(old); did = true;
  }
  /* a kept video whose end clip was missed when it was added gets it now, so Watch original and Save video cut it too */
  if (hasVideo(t) && !(+t.video.end > 0)) {
    let e = null; try { e = await videoEndOf(t); } catch (x) { e = null; }
    if (e) { const now = track(t.id) || t; await store.update('tracks', t.id, { video: Object.assign({}, now.video || t.video, { end: e }) }); did = true; }
  }
  return did;
}
'''

def apply(d):
    d.before("  async function parse(reader) {", ISO)
    d.rep("""    return {
      n, timescale, lang, codec, prime, sizes, durs, offsets, video: hasVideo,
      ftyp: ftyp && cc(ftyp, 8) === 'qt  ' ? ftyp : null,
      hdlr: moov.slice(hdlr.start, hdlr.end),
      minfHead: cat(extras),
      stsd: moov.slice(stsd.start, stsd.end)
    };""", """    return isoAudio({
      n, timescale, lang, codec, prime, sizes, durs, offsets, video: hasVideo,
      ftyp: ftyp && cc(ftyp, 8) === 'qt  ' ? ftyp : null,
      hdlr: moov.slice(hdlr.start, hdlr.end),
      minfHead: cat(extras),
      stsd: moov.slice(stsd.start, stsd.end)
    });""")
    d.cut("async function trimEndingCore(t) {", "async function trimEnding(id) {", TRIM)
    d.before("async function framePeaks(u8, src) {",
             "/* the file the way any decoder can read it: an upload stored before V10.1 from a .mov may still have its sound described the old way */\n"
             "async function readable(u8, src) { if (!src || !src.fixed) return u8; return new Uint8Array(await MP4.mux(src, range(src.n), MP4.gather(u8, src, range(src.n))).blob.arrayBuffer()); }\n")
    d.rep("  try { const u8 = await store.bytes(t.asset), ab = await decodeAudio(u8.buffer.slice(u8.byteOffset, u8.byteOffset + u8.length));",
          "  try { let u8 = await store.bytes(t.asset); try { u8 = await readable(u8, await MP4.parse(MP4.bufReader(u8))); } catch (e) { /* decode it as it is */ } const ab = await decodeAudio(u8.buffer.slice(u8.byteOffset, u8.byteOffset + u8.length));")
    d.rep("    ED.fp = await framePeaks(ED.u8, ED.src);", "    ED.fp = await framePeaks(await readable(ED.u8, ED.src), ED.src);")
    d.rep("      for (const p of parts) bufs.push(await decodeAudio(p.u8.buffer.slice(p.u8.byteOffset, p.u8.byteOffset + p.u8.length), pick.rate, 90000));",
          "      for (const p of parts) { const r8 = await readable(p.u8, p.src); bufs.push(await decodeAudio(r8.buffer.slice(r8.byteOffset, r8.byteOffset + r8.length), pick.rate, 90000)); }")
    d.rep("saveStats: () => saveStats(true), get audio() { return audio; } };", "saveStats: () => saveStats(true), get audio() { return audio; }, get store() { return store; } };")
