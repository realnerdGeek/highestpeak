# V18: library + computer and Android. Tags on uploads (filter and search by them, tag many at once), playlist folders,
# smart playlists that fill themselves (a tag, a BPM, Liked), an optional source link on each upload, a whole folder
# dropped in or picked on a computer, "Open with EarWorm" for the installed computer app, sharing a saved video to
# EarWorm on Android, pictures on the empty screens, and rows that lift when dragged.

CSS = r'''
/* ===================== V18: library ===================== */
.lib-filter{flex-wrap:nowrap;overflow-x:auto;scrollbar-width:none;margin-inline:-4px;padding:2px 4px 4px}
.lib-filter::-webkit-scrollbar{display:none}
.lib-filter .gym-chip{flex:none}
.tag-chips{display:flex;flex-wrap:wrap;gap:8px;margin:4px 0 14px}
.tag-chips .gym-chip{max-width:100%;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.tag-add{display:flex;flex-direction:row;gap:8px;align-items:center}
.tag-add .btn{flex:none}
.tag-add input{flex:1;min-width:0}
.sheet-panel .note{font-size:13px;color:var(--muted);margin:10px 0 0}
.pl-folder{margin-top:22px}
.fold-h{display:flex;align-items:center;gap:8px;width:100%;min-height:40px;padding:0 2px;font:800 17px/1.2 var(--round);letter-spacing:-.01em;color:var(--ink);text-align:left}
.fold-h .n{font:600 13px/1 var(--font);color:var(--muted)}
.fold-h svg{margin-left:auto;transition:transform .2s ease;color:var(--muted)}
.fold-h[aria-expanded="false"] svg{transform:rotate(-90deg)}
.pl-folder .grid{margin-top:8px}
.smart-badge{display:inline-flex;align-items:center;gap:3px;color:var(--accent-ink);font-weight:700}
.smart-badge svg{width:12px;height:12px}
.form-rows{display:grid;gap:12px;margin:12px 0 4px}
.form-row{display:grid;gap:6px}
.form-row > span{font-size:13px;font-weight:700;color:var(--muted)}
.form-row select{font:inherit;font-size:16px;width:100%;min-height:50px;padding:0 12px;border-radius:14px;border:1px solid transparent;background:var(--raise);color:var(--ink)}
.form-row.liked-row{grid-template-columns:minmax(0,1fr) auto;align-items:center;min-height:44px}
.form-row.liked-row > span{font-size:15px;color:var(--ink);font-weight:600}
.form-row.liked-row input{width:22px;height:22px;margin:0;accent-color:var(--accent)}
.smart-count{font-size:14px;color:var(--muted);margin:6px 0 12px}
.folder-pick{margin-top:10px}
.pair-btns{display:flex;gap:8px;flex-wrap:wrap;justify-content:flex-end}
.sorting .row.drag{transform-origin:50% 50%;box-shadow:0 18px 40px var(--shadow)}
.empty .cover.ic{display:grid;place-items:center;color:var(--muted);background:var(--raise)}
.empty .cover.ic svg{width:34px;height:34px}
'''

JS = r'''
/* ===================== V18: library =====================
   Tags live on each upload (t.tags, lower case). A smart playlist is a playlist with rules (p.smart) instead of a list:
   its uploads are worked out every time, so new ones join on their own. Folders are just a name on the playlist. */
const TAG_MAX = 8;
const V18_IC = {
  tag: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.1" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M3.5 12.2V4.5a1 1 0 0 1 1-1h7.7l8.3 8.3a1 1 0 0 1 0 1.4l-7.7 7.7a1 1 0 0 1-1.4 0z"/><circle cx="8" cy="8" r="1.4" fill="currentColor"/></svg>',
  bolt: '<svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M13.2 2.5 4.8 13.4h6l-1 8.1 8.4-10.9h-6z"/></svg>',
  chev: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m6 9 6 6 6-6"/></svg>',
  search: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><circle cx="11" cy="11" r="6.5"/><path d="m20 20-4.2-4.2"/></svg>',
  heart: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round" aria-hidden="true"><path d="M12 20s-7.5-4.6-7.5-10.2A4.3 4.3 0 0 1 12 7.4a4.3 4.3 0 0 1 7.5 2.4C19.5 15.4 12 20 12 20z"/></svg>',
  list: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="M4 7h11M4 12h11M4 17h7M18 14v6M15 17h6"/></svg>',
  link: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.1" stroke-linecap="round" aria-hidden="true"><path d="M10 14a4.5 4.5 0 0 0 6.4 0l3-3a4.5 4.5 0 0 0-6.4-6.4l-1 1M14 10a4.5 4.5 0 0 0-6.4 0l-3 3a4.5 4.5 0 0 0 6.4 6.4l1-1"/></svg>'
};
const cleanTag = s => String(s || '').replace(/\s+/g, ' ').trim().replace(/^#+\s*/, '').toLowerCase().slice(0, 24).trim();
const tagsOf = t => (t && Array.isArray(t.tags) ? t.tags.filter(x => typeof x === 'string' && x) : []);
function allTags() {
  const n = new Map(); S.tracks.forEach(t => tagsOf(t).forEach(g => n.set(g, (n.get(g) || 0) + 1)));
  return Array.from(n, ([tag, count]) => ({ tag, count })).sort((a, b) => b.count - a.count || a.tag.localeCompare(b.tag));
}
/* the Tags sheet works for one upload (from its menu) or many (Select, then Tag) */
function tagSheet(ids, keep) {
  ids = [].concat(ids).filter(id => track(id)); if (!ids.length) return closeSheet();
  const one = ids.length === 1 ? track(ids[0]) : null, has = g => ids.every(id => tagsOf(track(id)).indexOf(g) >= 0), tags = allTags();
  (keep || []).forEach(g => { if (!tags.some(x => x.tag === g)) tags.push({ tag: g, count: 0 }); });     // a tag just taken off stays in the list, to put back
  sheet('<h2>Tags</h2><p class="sub">' + (one ? esc(one.title) : countText(ids.length) + ' selected') + '</p>' +
    (tags.length ? '<div class="tag-chips" id="tagChips">' + tags.map(x => '<button class="gym-chip" data-act="tag-toggle" data-k="' + esc(x.tag) + '" aria-pressed="' + has(x.tag) + '">' + esc(x.tag) + '</button>').join('') + '</div>'
      : '<p class="sub">Tags group uploads any way you want: leg day, warm up, PRs, hype. Then filter by them in Library.</p>') +
    '<form data-form="tag" class="tag-add"><input type="text" id="tagInput" name="tagname" maxlength="24" placeholder="New tag, like leg day" autocomplete="off" autocapitalize="off" aria-label="New tag"' + (tags.length ? '' : ' data-focus') + '><button type="submit" class="btn primary">Add</button></form>' +
    '<button class="btn" data-act="sheet-close" style="margin-top:14px">Done</button>', { ids, kind: 'tags', shown: tags.map(x => x.tag) });
}
async function setTags(ids, tag, on) {
  const jobs = [];
  for (const id of ids) {
    const t = track(id); if (!t) continue;
    const now = tagsOf(t), has = now.indexOf(tag) >= 0;
    if (on && !has && now.length < TAG_MAX) jobs.push(store.update('tracks', id, { tags: now.concat(tag) }));
    else if (!on && has) jobs.push(store.update('tracks', id, { tags: now.filter(x => x !== tag) }));
  }
  await Promise.all(jobs);
  if (S.tagF && !allTags().some(x => x.tag === S.tagF)) S.tagF = '';
}
/* what "all uploads" is called when a Library filter is on */
function allLabel() {
  if (S.tab !== 'library' || (!S.tagF && S.bpmF !== 'fast')) return 'All uploads';
  return S.tagF ? 'Tagged ' + S.tagF + (S.bpmF === 'fast' ? ', 140+ BPM' : '') : '140+ BPM';
}
/* filter chips over the uploads in Library: the fast ones, then each tag */
function libFilters() {
  const tags = allTags(), fast = S.tracks.some(t => t.bpm > 0);
  if (!tags.length && !fast) return '';
  return '<div class="lib-filter" id="libFilter" role="group" aria-label="Filter uploads">' +
    (fast ? '<button class="gym-chip" id="bpmFilter" data-act="bpm-filter" aria-pressed="' + (S.bpmF === 'fast') + '">140+ BPM</button>' : '') +
    tags.map(x => '<button class="gym-chip" data-act="tag-filter" data-k="' + esc(x.tag) + '" aria-pressed="' + (S.tagF === x.tag) + '">' + V18_IC.tag + esc(x.tag) + '</button>').join('') + '</div>';
}

/* ----- smart playlists ----- */
const SMART_SORTS = { new: 'Newest first', top: 'Most played first', bpm: 'Fastest BPM first', az: 'A to Z' };
function cleanSmart(r) {
  r = r && typeof r === 'object' ? r : {};
  return { tag: cleanTag(r.tag), bpm: [0, 100, 120, 140, 160].indexOf(+r.bpm) >= 0 ? +r.bpm : 0, liked: !!r.liked, sort: SMART_SORTS[r.sort] ? r.sort : 'new', max: [0, 10, 25, 50].indexOf(+r.max) >= 0 ? +r.max : 0 };
}
function smartTracks(rules) {
  const r = cleanSmart(rules);
  let list = S.tracks.filter(t => (!r.tag || tagsOf(t).indexOf(r.tag) >= 0) && (!r.bpm || t.bpm >= r.bpm) && (!r.liked || isLiked(t)));
  if (r.sort === 'top') list.sort((a, b) => (S.plays[b.id] || 0) - (S.plays[a.id] || 0));
  else if (r.sort === 'bpm') list.sort((a, b) => (b.bpm || 0) - (a.bpm || 0));
  else if (r.sort === 'az') list.sort((a, b) => String(a.title).localeCompare(String(b.title), undefined, { sensitivity: 'base', numeric: true }));
  return r.max ? list.slice(0, r.max) : list;
}
const isSmart = p => !!(p && p.smart);
const handPlaylists = () => S.playlists.filter(p => !isSmart(p));          // the ones uploads can be added to by hand
function smartText(r) {
  r = cleanSmart(r); const bits = [];
  if (r.tag) bits.push('tagged ' + r.tag); if (r.bpm) bits.push(r.bpm + '+ BPM'); if (r.liked) bits.push('liked');
  return (bits.length ? bits.join(', ') : 'every upload') + (r.max ? ', top ' + r.max : '');
}
function smartForm(p) {
  const fast = S.tracks.some(t => t.bpm >= 140), r = cleanSmart(p ? p.smart : { bpm: fast ? 140 : 0 }), tags = allTags(), cur = p ? p.color || 'blue' : COLORS[S.playlists.length % COLORS.length];
  const sel = (name, label, opts, v) => '<label class="form-row"><span>' + label + '</span><select name="' + name + '" id="smart-' + name + '">' + opts.map(o => '<option value="' + esc(o[0]) + '"' + (String(o[0]) === String(v) ? ' selected' : '') + '>' + esc(o[1]) + '</option>').join('') + '</select></label>';
  sheet('<h2>' + (p ? 'Edit smart playlist' : 'New smart playlist') + '</h2><p class="sub">It fills itself with the uploads that match. New ones join on their own.</p>' +
    '<form data-form="smart"><input type="text" id="smartName" name="sname" maxlength="60" placeholder="' + (fast ? '140+ BPM' : 'Hype') + '" value="' + esc(p ? p.name : fast && !tags.length ? '140+ BPM' : '') + '" autocomplete="off" aria-label="Playlist name">' +
    '<div class="form-rows">' +
      sel('stag', 'Tag', [['', 'Any tag']].concat(tags.map(x => [x.tag, x.tag])).concat(r.tag && !tags.some(x => x.tag === r.tag) ? [[r.tag, r.tag]] : []), r.tag) +
      sel('sbpm', 'BPM', [[0, 'Any'], [100, '100 and up'], [120, '120 and up'], [140, '140 and up'], [160, '160 and up']], r.bpm) +
      '<label class="form-row liked-row"><span>Only liked uploads</span><input type="checkbox" name="sliked" id="smart-sliked"' + (r.liked ? ' checked' : '') + '></label>' +
      sel('ssort', 'Order', Object.keys(SMART_SORTS).map(k => [k, SMART_SORTS[k]]), r.sort) +
      sel('smax', 'How many', [[0, 'All that match'], [10, 'Top 10'], [25, 'Top 25'], [50, 'Top 50']], r.max) +
    '</div><p class="smart-count" id="smartCount" aria-live="polite"></p>' +
    '<div class="colors" role="radiogroup" aria-label="Cover color">' + COLORS.map(c => '<label><input type="radio" name="color" value="' + c + '"' + (c === cur ? ' checked' : '') + ' aria-label="' + c + '">' + colorCover(c, '') + '</label>').join('') + '</div>' +
    '<div class="pair"><button type="button" class="btn" data-act="sheet-close">Cancel</button><button type="submit" class="btn primary">' + (p ? 'Save' : 'Create') + '</button></div></form>', { form: 'smart', pl: p ? p.id : null });
  smartCount();
}
function smartFormRules(f) { return cleanSmart({ tag: f.elements.stag.value, bpm: +f.elements.sbpm.value, liked: f.elements.sliked.checked, sort: f.elements.ssort.value, max: +f.elements.smax.value }); }
function smartCount() {
  const f = document.querySelector('form[data-form="smart"]'), out = $('#smartCount'); if (!f || !out) return;
  const n = smartTracks(smartFormRules(f)).length; out.textContent = n ? 'Matches ' + countText(n) + ' right now.' : 'Nothing matches yet. New uploads that match will join on their own.';
}
document.addEventListener('change', e => { if (e.target.closest && e.target.closest('form[data-form="smart"]')) smartCount(); });

/* ----- folders: a name on the playlist; the Playlists page groups by it ----- */
const cleanFolder = s => String(s || '').replace(/\s+/g, ' ').trim().slice(0, 30);
const folders = () => Array.from(new Set(S.playlists.map(p => cleanFolder(p.folder)).filter(Boolean))).sort((a, b) => a.localeCompare(b, undefined, { sensitivity: 'base', numeric: true }));
const FOLDS = (() => { try { return new Set(JSON.parse(localStorage.getItem('hp.folds') || '[]')); } catch (e) { return new Set(); } })();     // the folders closed on this device
function saveFolds() { try { localStorage.setItem('hp.folds', JSON.stringify(Array.from(FOLDS))); } catch (e) { /* not kept */ } }
function plGrid(card, likedCard) {
  const loose = S.playlists.filter(p => !cleanFolder(p.folder)), fs = folders();
  let h = (likedCard || loose.length ? '<div class="grid">' + (likedCard || '') + loose.map(card).join('') + '</div>' : '');
  fs.forEach(name => {
    const in_ = S.playlists.filter(p => cleanFolder(p.folder) === name), open = !FOLDS.has(name);
    h += '<section class="pl-folder"><button class="fold-h" data-act="fold" data-k="' + esc(name) + '" aria-expanded="' + open + '">' + esc(name) + '<span class="n">' + in_.length + '</span>' + V18_IC.chev + '</button>' +
      (open ? '<div class="grid">' + in_.map(card).join('') + '</div>' : '') + '</section>';
  });
  return h;
}

/* ----- source link: where an upload came from. Only opened, never downloaded from ----- */
function cleanLink(s) {
  s = String(s || '').trim(); if (!s) return '';
  if (!/^[a-z][a-z0-9+.-]*:/i.test(s)) s = 'https://' + s;
  try { const u = new URL(s); return (u.protocol === 'https:' || u.protocol === 'http:') && u.hostname.indexOf('.') > 0 ? u.href.slice(0, 500) : null; } catch (e) { return null; }
}
const linkHost = s => { try { return new URL(s).hostname.replace(/^www\./, ''); } catch (e) { return ''; } };
function linkSheet(id) {
  const t = track(id); if (!t) return;
  sheet('<h2>Source link</h2><p class="sub">Where ' + esc(t.title) + ' came from, like the TikTok it was saved from. It opens in a new tab. EarWorm never downloads anything from it.</p>' +
    '<form data-form="link"><input type="text" inputmode="url" id="linkInput" name="lurl" maxlength="500" placeholder="https://www.tiktok.com/..." value="' + esc(t.link || '') + '" data-focus autocomplete="off" autocapitalize="off" spellcheck="false" aria-label="Link">' +
    '<div class="pair" style="margin-top:12px">' + (t.link ? '<button type="button" class="btn warn" data-act="link-remove">Remove</button>' : '<button type="button" class="btn" data-act="sheet-close">Cancel</button>') + '<button type="submit" class="btn primary">Save link</button></div></form>', { id });
}

/* ----- files from outside: a whole folder, Open with on a computer, Share on Android ----- */
const MEDIA_RE = /\.(mp4|mov|m4v|m4a|mp3|wav|aac|flac|ogg|oga|opus|webm|caf|3gp)$/i;
const isMedia = f => !!f && (/^(audio|video)\//.test(f.type || '') || MEDIA_RE.test(f.name || ''));
const FOLDER_MAX = 300;
/* everything inside dropped folders, however deep */
async function filesFromEntries(entries) {
  const out = [], walk = async en => {
    if (!en || out.length >= 2000) return;
    if (en.isFile) { const f = await new Promise(res => en.file(res, () => res(null))); if (f) out.push(f); return; }
    if (en.isDirectory) {
      const rd = en.createReader();
      for (;;) { const batch = await new Promise(res => rd.readEntries(res, () => res([]))); if (!batch.length) break; for (const x of batch) await walk(x); }
    }
  };
  for (const en of entries) await walk(en);
  return out;
}
function takeFiles(files, fromFolder) {
  const media = files.filter(isMedia), skip = files.length - media.length, take = media.slice(0, FOLDER_MAX);
  if (!take.length) return toast(files.length ? (fromFolder ? 'No videos or sound files in that folder.' : 'That isn\'t a video or sound file.') : 'That folder is empty.');
  queueFiles(take);
  if (media.length > FOLDER_MAX) toast('Adding the first ' + FOLDER_MAX + '. Drop the rest in after.');
  else if (skip && fromFolder) toast('Adding ' + countText(take.length) + '. Skipped ' + skip + (skip === 1 ? ' file that isn\'t' : ' files that aren\'t') + ' video or sound.');
}
function whenReady(fn, n) { n = n || 0; if (S.ready && store) return fn(); if (n < 300) setTimeout(() => whenReady(fn, n + 1), 100); }
/* the installed computer app: right-click a file, Open with, EarWorm */
async function launchFiles(handles) {
  const files = [];
  for (const h of handles || []) { try { files.push(h.getFile ? await h.getFile() : h); } catch (e) { /* that one can't be read */ } }
  if (files.length) whenReady(() => takeFiles(files, false));
}
if ('launchQueue' in window) { try { window.launchQueue.setConsumer(p => { if (p && p.files && p.files.length) launchFiles(p.files); }); } catch (e) { /* not this browser */ } }
/* Android: Share, EarWorm. The offline helper keeps what was shared and opens the app with ?share=1 */
const SHARE_CACHE = 'earworm-share';
async function takeShared() {
  if (!('caches' in window)) return;
  const c = await caches.open(SHARE_CACHE), base = new URL('./', location.href), m = await c.match(new URL('share/meta', base).href);
  const meta = m ? await m.json().catch(() => ({})) : {}, files = [];
  for (let i = 0; i < (+meta.n || 0); i++) {
    const r = await c.match(new URL('share/' + i, base).href); if (!r) continue;
    const b = await r.blob(); let name = 'Shared video'; try { name = decodeURIComponent(r.headers.get('x-name') || '') || name; } catch (e) { /* keep the plain name */ }
    files.push(new File([b], name, { type: b.type || r.headers.get('content-type') || '' }));
  }
  await caches.delete(SHARE_CACHE);
  if (files.some(isMedia) || (files.length && !meta.url && !meta.text)) return takeFiles(files, false);
  if (meta.url || meta.text) linkShared(cleanLink(meta.url || (String(meta.text || '').match(/https?:\/\/\S+/) || [''])[0]));
}
function linkShared(link) {
  sheet('<h2>That\'s a link</h2><p class="sub">EarWorm can\'t download from links' + (link ? ' (' + esc(linkHost(link)) + ')' : '') + '. Save the video first (in TikTok: Share, then Save video), then share the saved video from your gallery to EarWorm.</p>' +
    '<button class="btn primary" data-act="sheet-close">Got it</button>', { kind: 'shared-link' });
}
const SHARED = (() => { try { const q = new URLSearchParams(location.search); if (!q.has('share')) return false; history.replaceState(null, '', location.pathname + location.hash); return true; } catch (e) { return false; } })();
if (SHARED) setTimeout(() => whenReady(() => { takeShared().catch(() => toast('Couldn\'t read what was shared. Try again from your gallery.')); }), 0);
'''

ACTS = r'''  'm-tags'() { const c = sheetCtx; if (c) tagSheet(c.id); },
  'sel-tag'() { if (!S.sel || !S.sel.size) return toast('Tap some uploads first.'); tagSheet(visibleTracks().map(t => t.id).filter(id => S.sel.has(id))); },
  'tag-toggle'(d) {
    const c = sheetCtx; if (!c || !c.ids) return;
    const on = !c.ids.every(id => tagsOf(track(id)).indexOf(d.k) >= 0), full = on && c.ids.length === 1 && tagsOf(track(c.ids[0])).length >= TAG_MAX;
    if (full) return toast('Up to ' + TAG_MAX + ' tags on one upload.');
    guard(async () => { await setTags(c.ids, d.k, on); if (sheetCtx === c) tagSheet(c.ids, c.shown); });
  },
  'tag-filter'(d) { S.tagF = S.tagF === d.k ? '' : d.k; render(); },
  'smart-new'() { smartForm(null); },
  'smart-edit'() { const p = playlist(S.pl); if (p) smartForm(p); },
  fold(d) { if (FOLDS.has(d.k)) FOLDS.delete(d.k); else FOLDS.add(d.k); saveFolds(); render(); },
  'm-link'() { const c = sheetCtx; if (c) linkSheet(c.id); },
  'm-link-open'() { const c = sheetCtx, t = c && track(c.id); closeSheet(); if (t && cleanLink(t.link)) window.open(cleanLink(t.link), '_blank', 'noopener'); },
  'link-remove'() { const c = sheetCtx; closeSheet(); if (c) guard(async () => { await store.update('tracks', c.id, { link: null }); toast('Link removed.'); }); },
  'add-folder'() { $('#folderInput').click(); },
'''

FORMS = r'''  tag(f) {
    const c = sheetCtx, tag = cleanTag(f.elements.tagname.value); if (!c || !c.ids) return;
    if (!tag) return tagSheet(c.ids, c.shown);
    if (c.ids.length === 1 && tagsOf(track(c.ids[0])).indexOf(tag) < 0 && tagsOf(track(c.ids[0])).length >= TAG_MAX) return toast('Up to ' + TAG_MAX + ' tags on one upload.');
    guard(async () => { await setTags(c.ids, tag, true); if (sheetCtx === c) tagSheet(c.ids, c.shown); });
  },
  smart(f) {
    const c = sheetCtx || {}, rules = smartFormRules(f), name = (f.elements.sname.value.trim() || (rules.tag ? rules.tag.charAt(0).toUpperCase() + rules.tag.slice(1) : rules.bpm ? rules.bpm + '+ BPM' : 'Smart playlist')).slice(0, 60);
    const color = (f.elements.color && f.elements.color.value) || 'blue';
    closeSheet();
    guard(async () => {
      if (c.pl) { await store.update('playlists', c.pl, { name, color, smart: rules }); return; }
      const id = store.id(); await store.set('playlists', id, { name, color, tracks: [], smart: rules, created: Date.now() });
      go('library', { lib: 'playlists', pl: id });
    });
  },
  link(f) {
    const c = sheetCtx, v = cleanLink(f.elements.lurl.value); if (!c) return;
    if (v === null) return toast('That doesn\'t look like a link. Paste the whole thing, starting with https://');
    closeSheet(); guard(async () => { await store.update('tracks', c.id, { link: v || null }); if (v) toast('Link saved.'); });
  },
'''

WHATS_NEW = r"""const WHATS_NEW = [
  ['Tags', 'Tag uploads (leg day, warm up, PRs) from their menu, or many at once with Select. Filter by a tag in Library. Search finds tags too.'],
  ['Smart playlists', 'They fill themselves: pick a tag, a BPM (like 140 and up) or only liked. New uploads that match join on their own.'],
  ['Folders', 'Put playlists in folders: give them a folder when you make or edit them.'],
  ['Source link', 'Keep where an upload came from. Add source link in its menu. It opens in a new tab, nothing gets downloaded.'],
  ['Computer and Android', 'On a computer, drop in a whole folder, or right-click a file and Open with EarWorm. On Android, share a saved video to EarWorm.']
];"""

def apply(d):
    d.before('</style>', CSS)
    d.before('/* ---------- loudness, for volume leveling ---------- */', JS)
    d.after("const ACT = {\n", ACTS)
    d.after("const FORM = {\n", FORMS)
    d.rep("const plTracks = p => (p.tracks || []).map(track).filter(Boolean);",
          "const plTracks = p => (p && p.smart ? smartTracks(p.smart) : (p.tracks || []).map(track).filter(Boolean));     // a smart playlist works its uploads out every time")
    # Library: filters (BPM and tags) and search by tag
    d.rep("  const k = S.opt.sort, list = S.bpmF === 'fast' ? S.tracks.filter(t => t.bpm >= 140) : S.tracks.slice();   // S.tracks is already newest first; the 140+ BPM filter in Library",
          "  const k = S.opt.sort, lib = S.tab === 'library', list = S.tracks.filter(t => !lib || ((S.bpmF !== 'fast' || t.bpm >= 140) && (!S.tagF || tagsOf(t).indexOf(S.tagF) >= 0)));   // S.tracks is already newest first; the filters only count in Library (Home's Shuffle everything is everything)")
    d.rep("  return { ids: visibleTracks().map(t => t.id), label: 'All uploads' };", "  return { ids: visibleTracks().map(t => t.id), label: allLabel() };")
    d.rep("  'play-all'() { S.shuffle = false; savePrefs(); P.ctx = 'all'; startQueue(visibleTracks().map(t => t.id), 'All uploads', null); },", "  'play-all'() { S.shuffle = false; savePrefs(); P.ctx = 'all'; startQueue(visibleTracks().map(t => t.id), allLabel(), null); },")
    d.rep("  'shuffle-all'() { S.shuffle = true; savePrefs(); P.ctx = 'all'; startQueue(visibleTracks().map(t => t.id), 'All uploads', null); },", "  'shuffle-all'() { S.shuffle = true; savePrefs(); P.ctx = 'all'; startQueue(visibleTracks().map(t => t.id), allLabel(), null); },")
    d.rep("          (S.tracks.some(t => t.bpm > 0) ? '<div class=\"lib-filter\"><button class=\"gym-chip\" id=\"bpmFilter\" data-act=\"bpm-filter\" aria-pressed=\"' + (S.bpmF === 'fast') + '\">140+ BPM</button></div>' : '')) +",
          "          libFilters()) +")
    d.rep("  return { rows: list.map((t, i) => trackRow(t, i, 'all')).join(''), count: countText(list.length) + ', ' + fmt(sumDur(list)) + ', ' + SORTS[S.opt.sort].toLowerCase() };",
          "  return { rows: list.map((t, i) => trackRow(t, i, 'all')).join(''), count: countText(list.length) + (S.tagF ? ' tagged ' + esc(S.tagF) : '') + (S.bpmF === 'fast' ? ' at 140+ BPM' : '') + ', ' + fmt(sumDur(list)) + ', ' + SORTS[S.opt.sort].toLowerCase() };")
    d.rep("  return { q, uploads: S.tracks.filter(t => has(t.title)), playlists: S.playlists.filter(p => has(p.name)) };",
          "  return { q, uploads: S.tracks.filter(t => has(t.title) || tagsOf(t).some(has)), playlists: S.playlists.filter(p => has(p.name) || has(p.folder)) };")
    d.rep("  if (!r.q) return '<div class=\"empty\"><p>Type a name to find an upload or a playlist.</p></div>';",
          "  if (!r.q) return '<div class=\"empty\"><span class=\"cover ic\" aria-hidden=\"true\">' + V18_IC.search + '</span><p>Type a name or a tag to find an upload or a playlist.</p></div>';")
    d.rep("  if (!r.uploads.length && !r.playlists.length) return '<div class=\"empty\"><h2>Nothing matches</h2><p>Check the spelling, or try fewer letters.</p></div>';",
          "  if (!r.uploads.length && !r.playlists.length) return '<div class=\"empty\"><span class=\"cover ic\" aria-hidden=\"true\">' + V18_IC.search + '</span><h2>Nothing matches</h2><p>Check the spelling, or try fewer letters.</p></div>';")
    d.rep("label class=\"search\">' + IC.search + '<input type=\"search\" id=\"q\" placeholder=\"Uploads and playlists\"", "label class=\"search\">' + IC.search + '<input type=\"search\" id=\"q\" placeholder=\"Uploads, tags and playlists\"")
    # Select: tag many at once
    d.rep("'<div class=\"sel-line\"><button class=\"btn sm wide\" data-act=\"sel-add\">Add to playlist</button>",
          "'<div class=\"sel-line\"><button class=\"btn sm wide\" data-act=\"sel-add\">Add to playlist</button><button class=\"btn sm\" id=\"selTag\" data-act=\"sel-tag\">' + V18_IC.tag + 'Tag</button>")
    # the upload menu: Tags and the source link
    d.rep("opt('m-like', isLiked(t) ? 'Unlike' : 'Like') + opt('m-addpl', 'Add to playlist') +",
          "opt('m-like', isLiked(t) ? 'Unlike' : 'Like') + opt('m-addpl', 'Add to playlist') + opt('m-tags', 'Tags', { post: tagsOf(t).length ? '<span class=\"tick\">' + esc(tagsOf(t).join(', ')) + '</span>' : '' }) +")
    d.rep("    if (ctx && ctx.indexOf('pl:') === 0) h += opt('m-up', 'Move up') + opt('m-down', 'Move down') + opt('m-remove', 'Remove from this playlist');",
          "    h += t.link ? opt('m-link-open', 'Open source link', { post: '<span class=\"tick\">' + esc(linkHost(t.link)) + '</span>' }) + opt('m-link', 'Edit source link') : opt('m-link', 'Add source link');\n"
          "    if (ctx && ctx.indexOf('pl:') === 0 && !isSmart(playlist(ctx.slice(3)))) h += opt('m-up', 'Move up') + opt('m-down', 'Move down') + opt('m-remove', 'Remove from this playlist');")
    d.rep("    (!sel && can && ctx.indexOf('pl:') === 0 ? '<button class=\"grip\"", "    (!sel && can && ctx.indexOf('pl:') === 0 && !isSmart(playlist(ctx.slice(3))) ? '<button class=\"grip\"")
    # smart playlists can't take uploads by hand
    d.rep("  h += S.playlists.map(p => opt('toggle-in', esc(p.name),", "  h += handPlaylists().map(p => opt('toggle-in', esc(p.name),")
    d.rep("<div class=\"opts\">' + S.playlists.map(p => opt('sel-into', esc(p.name),", "<div class=\"opts\">' + handPlaylists().map(p => opt('sel-into', esc(p.name),")
    d.rep("  'pl-menu'() { const p = playlist(S.pl); if (!p) return; sheet('<h2>' + esc(p.name) + '</h2><div class=\"opts\">' + opt('pl-edit', 'Rename or change color') +",
          "  'pl-menu'() { const p = playlist(S.pl); if (!p) return; sheet('<h2>' + esc(p.name) + '</h2><div class=\"opts\">' + (isSmart(p) ? opt('smart-edit', 'Edit rules, name or color') : opt('pl-edit', 'Rename, folder or color')) +")
    d.rep("  'pl-edit'() { const p = playlist(S.pl); if (p) playlistForm(p, null); },", "  'pl-edit'() { const p = playlist(S.pl); if (p) { if (isSmart(p)) smartForm(p); else playlistForm(p, null); } },")
    # the open playlist: a smart one shows its rules and has no Add or dragging
    d.rep("      '<div class=\"pl-head\">' + (o.liked ? likedCover() : plCover(o.p)) + '<div><h2>' + esc(o.name) + '</h2><div class=\"meta\">' + countText(list.length) + ', ' + fmt(sumDur(list)) + '</div></div></div>' +",
          "      '<div class=\"pl-head\">' + (o.liked ? likedCover() : plCover(o.p)) + '<div><h2>' + esc(o.name) + '</h2><div class=\"meta\">' + (isSmart(o.p) ? '<span class=\"smart-badge\">' + V18_IC.bolt + 'Smart</span> ' + esc(smartText(o.p.smart)) + '<br>' : o.p && cleanFolder(o.p.folder) ? esc(cleanFolder(o.p.folder)) + ' · ' : '') + countText(list.length) + ', ' + fmt(sumDur(list)) + '</div></div></div>' +")
    d.rep("      (o.liked ? '' : '<button class=\"btn sm\" data-act=\"pl-add\">' + IC.plus + 'Add</button><button class=\"icon-btn sm\" data-act=\"pl-menu\" aria-label=\"Playlist options\">' + IC.more + '</button>') + '</div>' +",
          "      (o.liked ? '' : isSmart(o.p) ? '<button class=\"btn sm\" data-act=\"smart-edit\">Rules</button><button class=\"icon-btn sm\" data-act=\"pl-menu\" aria-label=\"Playlist options\">' + IC.more + '</button>'\n"
          "        : '<button class=\"btn sm\" data-act=\"pl-add\">' + IC.plus + 'Add</button><button class=\"icon-btn sm\" data-act=\"pl-menu\" aria-label=\"Playlist options\">' + IC.more + '</button>') + '</div>' +")
    d.rep("      (list.length ? '<div class=\"list\" id=\"plList\"' + (o.liked ? '' : ' data-sortlist=\"pl\"') + '>' + list.map((t, i) => trackRow(t, i, o.ctx)).join('') + '</div>'\n"
          "        : o.liked ? '<div class=\"empty\"><h2>No likes yet</h2><p>Tap the heart on an upload and it lands here.</p></div>'\n"
          "        : '<div class=\"empty\"><h2>Empty playlist</h2><p>Tap Add to pick uploads from your library.</p></div>');",
          "      (list.length ? '<div class=\"list\" id=\"plList\"' + (o.liked || isSmart(o.p) ? '' : ' data-sortlist=\"pl\"') + '>' + list.map((t, i) => trackRow(t, i, o.ctx)).join('') + '</div>'\n"
          "        : o.liked ? '<div class=\"empty\"><span class=\"cover ic\" aria-hidden=\"true\">' + V18_IC.heart + '</span><h2>No likes yet</h2><p>Tap the heart on an upload and it lands here.</p></div>'\n"
          "        : isSmart(o.p) ? '<div class=\"empty\"><span class=\"cover ic\" aria-hidden=\"true\">' + V18_IC.bolt + '</span><h2>Nothing matches yet</h2><p>Uploads that are ' + esc(smartText(o.p.smart)) + ' land here on their own.</p><button class=\"btn\" data-act=\"smart-edit\">Edit rules</button></div>'\n"
          "        : '<div class=\"empty\"><span class=\"cover ic\" aria-hidden=\"true\">' + V18_IC.list + '</span><h2>Empty playlist</h2><p>Tap Add to pick uploads from your library.</p></div>');")
    # the Playlists page: New smart playlist, folders, a Smart line on smart cards
    d.rep("    const card = (id, cover, name, n) => '<button class=\"pl-row\" data-key=\"' + esc(id) + '\" data-act=\"pl-open\" data-id=\"' + esc(id) + '\">' + cover + '<span class=\"tt\"><span class=\"title\">' + esc(name) + '</span><span class=\"meta\">' + countText(n) + '</span></span></button>';",
          "    const card = (id, cover, name, n, smart) => '<button class=\"pl-row\" data-key=\"' + esc(id) + '\" data-act=\"pl-open\" data-id=\"' + esc(id) + '\">' + cover + '<span class=\"tt\"><span class=\"title\">' + esc(name) + '</span><span class=\"meta\">' + (smart ? '<span class=\"smart-badge\">' + V18_IC.bolt + 'Smart</span> · ' : '') + countText(n) + '</span></span></button>';")
    d.rep("      '<button class=\"btn sm\" data-act=\"pl-new\">' + IC.plus + 'New playlist</button></div>' +\n"
          "      (S.playlists.length || liked ? '<div class=\"grid\">' + (S.tracks.length ? card(LIKED, likedCover(), 'Liked', liked) : '') + S.playlists.map(p => card(p.id, plCover(p), p.name, plTracks(p).length)).join('') + '</div>'",
          "      '<span class=\"pair-btns\"><button class=\"btn sm\" id=\"smartNew\" data-act=\"smart-new\">' + V18_IC.bolt + 'Smart</button><button class=\"btn sm\" data-act=\"pl-new\">' + IC.plus + 'New playlist</button></span></div>' +\n"
          "      (S.playlists.length || liked ? plGrid(p => card(p.id, plCover(p), p.name, plTracks(p).length, isSmart(p)), S.tracks.length ? card(LIKED, likedCover(), 'Liked', liked) : '')")
    d.rep("    h += '<div class=\"empty\"><h2>No uploads yet</h2><p>Everything you upload shows up here.</p>",
          "    h += '<div class=\"empty\"><span class=\"cover\" style=\"--h:338;--hb:24;--hc:312\" aria-hidden=\"true\">' + coverBars(null).map(x => '<i style=\"height:' + x + '%\"></i>').join('') + '</span><h2>No uploads yet</h2><p>Everything you upload shows up here.</p>")
    # the playlist form: a folder
    d.rep("    '<input type=\"text\" id=\"plNameInput\" name=\"pname\" maxlength=\"60\" placeholder=\"Leg day\" value=\"' + esc(p ? p.name : '') + '\" data-focus autocomplete=\"off\" aria-label=\"Playlist name\">' +",
          "    '<input type=\"text\" id=\"plNameInput\" name=\"pname\" maxlength=\"60\" placeholder=\"Leg day\" value=\"' + esc(p ? p.name : '') + '\" data-focus autocomplete=\"off\" aria-label=\"Playlist name\">' +\n"
          "    '<label class=\"form-row\" style=\"margin-top:12px\"><span>Folder (optional)</span><input type=\"text\" id=\"plFolderInput\" name=\"pfolder\" maxlength=\"30\" list=\"plFolders\" placeholder=\"Like Gym or Chill\" value=\"' + esc(p ? cleanFolder(p.folder) : '') + '\" autocomplete=\"off\" aria-label=\"Folder\"></label>' +\n"
          "    '<datalist id=\"plFolders\">' + folders().map(x => '<option value=\"' + esc(x) + '\"></option>').join('') + '</datalist>' +")
    d.rep("    const c = sheetCtx || {}, name = (f.elements.pname.value.trim() || 'Playlist ' + (S.playlists.length + 1)).slice(0, 60), color = (f.elements.color && f.elements.color.value) || 'blue';",
          "    const c = sheetCtx || {}, name = (f.elements.pname.value.trim() || 'Playlist ' + (S.playlists.length + 1)).slice(0, 60), color = (f.elements.color && f.elements.color.value) || 'blue', folder = f.elements.pfolder ? cleanFolder(f.elements.pfolder.value) : '';")
    d.rep("        const patch = { name, color }; if (coverId) patch.cover = coverId; else if (removeCover) patch.cover = null;",
          "        const patch = { name, color, folder: folder || null }; if (coverId) patch.cover = coverId; else if (removeCover) patch.cover = null;")
    d.rep("doc = { name, color, tracks: c.addTrack ? [].concat(c.addTrack) : [], created: Date.now() }; if (coverId) doc.cover = coverId;",
          "doc = { name, color, tracks: c.addTrack ? [].concat(c.addTrack) : [], created: Date.now() }; if (coverId) doc.cover = coverId; if (folder) doc.folder = folder;")
    # a restore keeps tags, links, BPM, folders and smart rules
    d.rep("        if (typeof bt.fp === 'string') doc.fp = bt.fp;",
          "        if (typeof bt.fp === 'string') doc.fp = bt.fp;\n"
          "        const tg = tagsOf(bt).map(cleanTag).filter(Boolean).slice(0, TAG_MAX); if (tg.length) doc.tags = Array.from(new Set(tg));\n"
          "        if (cleanLink(bt.link)) doc.link = cleanLink(bt.link);\n"
          "        if (typeof bt.bpm === 'number') { doc.bpm = bt.bpm; if (typeof bt.beat === 'number') doc.beat = bt.beat; }")
    d.rep("      const doc = { name, color: COLORS.indexOf(bp.color) >= 0 ? bp.color : 'blue', tracks, created: +bp.created || Date.now() };",
          "      const doc = { name, color: COLORS.indexOf(bp.color) >= 0 ? bp.color : 'blue', tracks, created: +bp.created || Date.now() };\n"
          "      if (cleanFolder(bp.folder)) doc.folder = cleanFolder(bp.folder);\n"
          "      if (bp.smart) doc.smart = cleanSmart(bp.smart);")
    # Upload: a whole folder, and what works on a computer
    d.rep("    '<button class=\"btn primary\" id=\"addBtn\" data-act=\"add\"' + (can ? '' : ' disabled') + '>' + IC.plus + 'Choose files</button>' +\n"
          "    '<p class=\"works\">Works with videos, screen recordings, voice memos, and MP3, WAV or M4A audio.</p></div>' +",
          "    '<button class=\"btn primary\" id=\"addBtn\" data-act=\"add\"' + (can ? '' : ' disabled') + '>' + IC.plus + 'Choose files</button>' +\n"
          "    (isPC() && FOLDER_PICK ? '<button class=\"btn folder-pick\" id=\"folderBtn\" data-act=\"add-folder\"' + (can ? '' : ' disabled') + '>Choose a folder</button>' : '') +\n"
          "    '<p class=\"works\">Works with videos, screen recordings, voice memos, and MP3, WAV or M4A audio.' + (isPC() ? ' You can also drop files or a whole folder anywhere on this page, or right-click a file and pick Open with, EarWorm (in the installed app).' : '') + '</p></div>' +")
    d.rep("    <input type=\"file\" id=\"fileInput\" accept=\"video/*,audio/*,.mp4,.mov,.m4v,.m4a,.mp3,.wav,.aac,.flac\" multiple hidden>",
          "    <input type=\"file\" id=\"fileInput\" accept=\"video/*,audio/*,.mp4,.mov,.m4v,.m4a,.mp3,.wav,.aac,.flac\" multiple hidden>\n"
          "    <input type=\"file\" id=\"folderInput\" webkitdirectory multiple hidden>")
    d.rep("$('#fileInput').addEventListener('change', e => { const files = Array.from(e.target.files || []); e.target.value = ''; queueFiles(files); });",
          "$('#fileInput').addEventListener('change', e => { const files = Array.from(e.target.files || []); e.target.value = ''; queueFiles(files); });\n"
          "const FOLDER_PICK = 'webkitdirectory' in document.createElement('input');\n"
          "$('#folderInput').addEventListener('change', e => { const files = Array.from(e.target.files || []); e.target.value = ''; if (files.length) takeFiles(files, true); });")
    d.rep("document.addEventListener('drop', e => { if (!e.dataTransfer || !e.dataTransfer.files || !e.dataTransfer.files.length) return; e.preventDefault(); queueFiles(Array.from(e.dataTransfer.files)); });",
          "document.addEventListener('drop', e => {\n"
          "  const dt = e.dataTransfer; if (!dt || !dt.files || !dt.files.length) return; e.preventDefault();\n"
          "  if (!store || !store.canWrite) return;\n"
          "  /* folders: their entries have to be taken now, while the drop is still going on */\n"
          "  const entries = Array.from(dt.items || []).map(i => (i.kind === 'file' && i.webkitGetAsEntry ? i.webkitGetAsEntry() : null));\n"
          "  if (entries.some(en => en && en.isDirectory)) { filesFromEntries(entries.filter(Boolean)).then(files => takeFiles(files, true)).catch(() => toast('Couldn\\'t read that folder.')); return; }\n"
          "  queueFiles(Array.from(dt.files));\n"
          "});")
    # rows lift a little while dragged (and a tiny buzz on Android)
    d.rep("    d.row.style.transform = 'translateY(' + off + 'px)';", "    d.row.style.transform = 'translateY(' + off + 'px) scale(1.02)';")
    d.rep("    row.classList.add('drag'); list.classList.add('sorting');", "    row.classList.add('drag'); list.classList.add('sorting'); row.style.transform = 'scale(1.02)'; try { if (navigator.vibrate) navigator.vibrate(8); } catch (x) { /* fine */ }")
    d.rep("const VERSION = 'V17', NEWS = 'V17';", "const VERSION = 'V18', NEWS = 'V18';")
    i = d.s.index('const WHATS_NEW = [\n'); j = d.s.index('\n];', i) + 3
    d.s = d.s[:i] + WHATS_NEW + d.s[j:]
    d.rep("window.__gymTapes = { isPC: () => isPC(),", "window.__gymTapes = { isPC: () => isPC(), allTags, smartTracks, cleanLink, filesFromEntries, takeFiles, launchFiles, takeShared, isMedia,")
