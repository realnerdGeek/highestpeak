# V8 part 4: join uploads (behind a Settings switch), and the encoder shared with MP3/WAV conversion
ENCODE = r'''/* encode decoded audio (one or more buffers, played back to back) into the format every upload uses */
async function encodeBuffers(bufs, pick, onPct) {
  const rate = bufs[0].sampleRate, ch = Math.min(2, Math.max.apply(null, bufs.map(b => b.numberOfChannels))), n = bufs.reduce((a, b) => a + b.length, 0);
  if (!n || !ch) throw err('no_audio');
  const frames = [], step = pick.kind === 'aac' ? 1024 : 960; let failed = null, prime = pick.prime;
  const enc = new AudioEncoder({
    output: (c, meta) => {
      const b = new Uint8Array(c.byteLength); c.copyTo(b);
      const d = c.duration ? Math.round(c.duration * rate / 1e6) : 0;
      frames.push({ b: pick.kind === 'aac' ? stripAdts(b) : b, dur: d > 0 ? d : step });
      const desc = pick.kind === 'opus' && meta && meta.decoderConfig && meta.decoderConfig.description;
      if (desc) { try { const v = desc.buffer ? new Uint8Array(desc.buffer, desc.byteOffset, desc.byteLength) : new Uint8Array(desc); if (v.length >= 12) prime = v[10] | (v[11] << 8); } catch (e) { /* keep the default */ } }
    },
    error: e => { failed = e || new Error('encode'); }
  });
  const bitrate = pick.kind === 'aac' && n / rate > 720 ? 128000 : pick.bitrate;
  enc.configure({ codec: pick.codec, sampleRate: rate, numberOfChannels: ch, bitrate });
  const BLOCK = Math.round(rate / 2); let done = 0, k = 0;
  for (const ab of bufs) {
    for (let off = 0; off < ab.length && !failed; off += BLOCK, k++) {
      const len = Math.min(BLOCK, ab.length - off), data = new Float32Array(len * ch);
      for (let c = 0; c < ch; c++) data.set(ab.getChannelData(Math.min(c, ab.numberOfChannels - 1)).subarray(off, off + len), c * len);      // a mono part is played on both sides
      const ad = new AudioData({ format: 'f32-planar', sampleRate: rate, numberOfFrames: len, numberOfChannels: ch, timestamp: Math.round((done + off) / rate * 1e6), data });
      enc.encode(ad); ad.close();
      if (k % 8 === 7 || enc.encodeQueueSize > 6) {     // let the page breathe, and never pile up more than the encoder can take
        if (onPct) onPct(Math.round((done + off) / n * 100));
        await new Promise(r => setTimeout(r, 0));
        while (enc.encodeQueueSize > 6 && !failed) await new Promise(r => setTimeout(r, 15));
      }
    }
    done += ab.length;
  }
  if (!failed) { try { await enc.flush(); } catch (e) { failed = e; } }
  try { enc.close(); } catch (e) { /* already closed */ }
  if (failed || !frames.length) throw err('no_convert');
  return MP4.audioSrc(pick.kind, rate, ch, frames, prime, bitrate);
}
async function convertAudio(file, onPct) {
  if (file.size > 150 * 1024 * 1024) throw err('convert_big');
  const pick = await pickEncoder(); if (!pick) throw err('no_convert');
  let ab; try { ab = await decodeAudio(await file.arrayBuffer(), pick.rate, 90000); } catch (e) { throw err('not_audio'); }
  if (!ab.length || !ab.numberOfChannels) throw err('no_audio');
  return encodeBuffers([ab], pick, onPct);
}
'''

JOIN = r'''/* ---------- join uploads: several uploads become one that loops as a single piece ---------- */
/* what has to match for the audio to be stitched together as it is, with nothing re-encoded */
function joinKey(src) {
  const s = src.stsd; if (!s || s.length < 52) return null;
  const dv = new DataView(s.buffer, s.byteOffset, s.byteLength), parts = [src.codec, src.timescale, dv.getUint16(40)];
  const box = type => { for (let i = 52; i + 8 <= s.length; i++) if (s[i + 4] === type.charCodeAt(0) && s[i + 5] === type.charCodeAt(1) && s[i + 6] === type.charCodeAt(2) && s[i + 7] === type.charCodeAt(3)) return i; return -1; };
  if (src.codec === 'mp4a') {
    let p = box('esds'); if (p < 0) return null; p += 12;
    const desc = () => { const tag = s[p++]; let len = 0; for (let k = 0; k < 4; k++) { const b = s[p++]; len = (len << 7) | (b & 0x7f); if (!(b & 0x80)) break; } return { tag, len }; };
    let x = desc(); if (x.tag !== 3) return null;
    const fl = s[p + 2]; p += 3; if (fl & 0x80) p += 2; if (fl & 0x40) p += 1 + s[p]; if (fl & 0x20) p += 2;
    x = desc(); if (x.tag !== 4) return null; p += 13; x = desc(); if (x.tag !== 5 || p + x.len > s.length) return null;
    parts.push(Array.from(s.subarray(p, p + x.len)).join('.'));
  } else if (src.codec === 'Opus') {
    const p = box('dOps'); if (p < 0 || p + 19 > s.length) return null;
    const b = s.subarray(p + 8); parts.push(b[0], b[1], Array.from(b.subarray(8)).join('.'));
  } else return null;
  return parts.join('|');
}
const JOIN_MAX = 5;
function joinSheet(id, picks) {
  const t = track(id); if (!t) return;
  picks = (picks || []).filter(x => x !== id && track(x));
  const others = S.tracks.filter(x => x.id !== id);
  let h = '<h2>Join uploads</h2><p class="sub">Pick what plays after ' + esc(t.title) + ', in order. Up to ' + (JOIN_MAX - 1) + '. The originals stay as they are.</p><div class="opts">';
  h += others.length ? others.map(x => { const k = picks.indexOf(x.id); return opt('join-pick', esc(x.title), { id: x.id, pre: trackCover(x), post: '<span class="tick">' + (k >= 0 ? k + 2 : '') + '</span>' }); }).join('') : '<p class="sub">Add another upload first.</p>';
  h += '</div><div class="pair"><button class="btn" data-act="sheet-close">Cancel</button><button class="btn primary" data-act="join-go"' + (picks.length ? '' : ' disabled') + '>' + (picks.length ? 'Join ' + (picks.length + 1) : 'Join') + '</button></div>';
  sheet(h, { kind: 'join', id, picks });
}
let joinBusy = false;
async function joinUploads(ids) {
  const ts = ids.map(track).filter(Boolean); if (ts.length < 2 || joinBusy || !store.canWrite) return;
  if (ts.reduce((a, t) => a + (t.bytes || 0), 0) > store.cap * 1.02) return toast(errText(err('too_large')));       // would be too big to save, so do not even start
  joinBusy = true; toast('Joining ' + ts.length + ' uploads');
  try {
    const parts = [];
    for (const t of ts) { const u8 = await store.bytes(t.asset); parts.push({ t, u8, src: await MP4.parse(MP4.bufReader(u8)) }); }
    const key = joinKey(parts[0].src); let out, src;
    if (key && parts.every(p => joinKey(p.src) === key)) {
      /* same format throughout: the audio frames are put one after another as they are. The short start-up padding
         at the front of every later part is left out so there is no gap at the joins. */
      const sizes = [], durs = [], chunks = [];
      parts.forEach((p, i) => {
        const s = p.src, skip = i === 0 ? 0 : Math.min(s.n - 1, Math.floor((s.prime || 0) / (s.durs[0] || 1)));
        const seq = new Uint32Array(s.n - skip); for (let k = 0; k < seq.length; k++) seq[k] = skip + k;
        chunks.push(MP4.gather(p.u8, s, seq)); for (let k = 0; k < seq.length; k++) { sizes.push(s.sizes[seq[k]]); durs.push(s.durs[seq[k]]); }
      });
      let total = 0; chunks.forEach(c => { total += c.length; });
      const payload = new Uint8Array(total); let o = 0; chunks.forEach(c => { payload.set(c, o); o += c.length; });
      src = MP4.packed(Object.assign({}, parts[0].src, { n: sizes.length, sizes: Uint32Array.from(sizes), durs: Uint32Array.from(durs) }));
      out = MP4.mux(src, range(src.n), payload);
    } else {
      /* different formats: decode everything and encode it again as one. That needs the whole sound in memory, so it is kept short. */
      const secs = ts.reduce((a, t) => a + (t.dur || 0), 0); if (secs > 360) throw err('join_long');
      const pick = await pickEncoder(); if (!pick) throw err('no_convert');
      const bufs = [];
      for (const p of parts) bufs.push(await decodeAudio(p.u8.buffer.slice(p.u8.byteOffset, p.u8.byteOffset + p.u8.length), pick.rate, 90000));
      const r = await encodeBuffers(bufs, pick);
      src = r.full; out = MP4.mux(r.full, range(r.full.n), r.payload);
    }
    if (out.blob.size > store.cap) throw err('too_large');
    const fp = await framePeaks(new Uint8Array(await out.blob.arrayBuffer()), src);
    const asset = await store.putBlob(out.blob);
    const doc = { title: ts.map(t => t.title).join(' + ').slice(0, 80), asset, dur: Math.round(out.dur * 100) / 100, bytes: out.blob.size, created: Date.now(), peaks: storedPeaks(fp, range(src.n)) };
    if (typeof fp.gain === 'number') doc.gain = fp.gain;
    const withCover = ts.find(t => t.cover);
    if (withCover) { try { doc.cover = await store.putBlob(await store.blob(withCover.cover), 'image/jpeg'); } catch (e) { /* no cover then */ } }   // its own copy, so deleting one never takes the other's picture
    await store.set('tracks', store.id(), doc);
    toast('Joined into a new upload: ' + doc.title + '.'); refreshUsage();
  } catch (e) { toast(e && e.code === 'join_long' ? 'These are in different formats, and together too long to join on a phone. Try up to 6 minutes.' : errText(e)); }
  finally { joinBusy = false; }
}

'''

def apply(d):
    d.rep("window.__gymTapes = { MP4, S, P, ED, Ending, T, FX, SEC, PRE, UP, stripAdts, pickEncoder, zipBlob, zipRead, get audio() { return audio; } };",
          "window.__gymTapes = { MP4, S, P, ED, Ending, T, FX, SEC, PRE, UP, ST, VOL, stripAdts, pickEncoder, zipBlob, zipRead, joinKey, addListen: s => addListen(s), saveStats: () => saveStats(true), get audio() { return audio; } };")
    d.cut("async function convertAudio(file, onPct) {", "/* ---------- adding videos ---------- */", ENCODE + "\n")
    d.before("/* ---------- actions ---------- */", JOIN)
    # ----- the switch, and the menu entry it controls -----
    d.rep("      '<div class=\"set col\"><button class=\"btn sm\" data-act=\"trim-all\">Check every upload for an end clip</button><p class=\"sub\" id=\"trimAllStatus\" aria-live=\"polite\">' + esc(trimAllMsg) + '</p></div>') +",
          "      '<div class=\"set col\"><button class=\"btn sm\" data-act=\"trim-all\">Check every upload for an end clip</button><p class=\"sub\" id=\"trimAllStatus\" aria-live=\"polite\">' + esc(trimAllMsg) + '</p></div>' +\n"
          "      setRow('Join uploads', 'Adds Join to the options of each upload, to stitch two or more into one that loops as a whole.', swBtn('join', 'Join uploads'))) +")
    d.rep("opt('m-edit', 'Trim, cut or section') + opt('m-trimend', 'Remove end clip')", "opt('m-edit', 'Trim, cut or section') + (S.opt.join ? opt('m-join', 'Join with other uploads') : '') + opt('m-trimend', 'Remove end clip')")
    d.after("const ACT = {\n", "  'm-join'() { const c = sheetCtx; if (c) joinSheet(c.id, []); },\n"
            "  'join-pick'(d) { const c = sheetCtx; if (!c || c.kind !== 'join') return; const p = c.picks.slice(), k = p.indexOf(d.id); if (k >= 0) p.splice(k, 1); else if (p.length < JOIN_MAX - 1) p.push(d.id); else return toast('That is as many as one join takes.'); joinSheet(c.id, p); },\n"
            "  'join-go'() { const c = sheetCtx; if (!c || c.kind !== 'join' || !c.picks.length) return; closeSheet(); joinUploads([c.id].concat(c.picks)); },\n")
