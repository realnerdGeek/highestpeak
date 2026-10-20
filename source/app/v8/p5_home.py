# V8 part 1: Your rotation, Home layout switches, playlist covers from their uploads, stats
CSS = r'''
/* Your rotation: last played and the most played, in one small grid */
.rot-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:8px}
.rot{--h:235;display:grid;grid-template-columns:46px minmax(0,1fr);gap:10px;align-items:center;min-width:0;min-height:58px;padding:6px 10px 6px 6px;border-radius:16px;background:var(--surface);box-shadow:0 1px 4px var(--shadow);transition:transform .12s ease}
.rot:active{transform:scale(.97)}
.rot .cover{width:46px;height:46px;border-radius:11px}
.rot .tt{min-width:0}
.rot .title{font-weight:650;font-size:14px;letter-spacing:-.01em;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.rot .meta{font-size:12px;color:var(--muted);overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.rot.cur .title{color:hsl(var(--h) var(--tint-s) var(--tint-l))}
/* a playlist without a picture shows the covers of its first four uploads */
.cover.mosaic{display:grid;grid-template-columns:1fr 1fr;grid-template-rows:1fr 1fr;gap:0;background:var(--raise)}
.cover.mosaic > .cover{width:100%;height:100%;min-width:0;min-height:0;border-radius:0;margin:0;box-shadow:none}
/* stats */
.stat-chips{display:flex;flex-wrap:wrap;gap:6px;margin-top:10px}
.stat-chip{display:inline-flex;align-items:center;gap:6px;min-height:32px;padding:0 12px;border-radius:999px;background:var(--raise);font-weight:600;font-size:13px;font-variant-numeric:tabular-nums;transition:transform .12s ease}
.stat-chip:active{transform:scale(.96)}
.stat-chip svg{flex:none;color:var(--muted)}
.stats-big{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:8px}
.stats-big > div{background:var(--raise);border-radius:16px;padding:12px 10px;min-width:0}
.stats-big b{display:block;font:800 20px/1.15 var(--font);letter-spacing:-.02em;font-variant-numeric:tabular-nums}
.stats-big span{display:block;margin-top:4px;font-size:12px;line-height:1.3;color:var(--muted);font-weight:600}
.week{display:grid;grid-template-columns:repeat(7,minmax(0,1fr));align-items:end;height:128px;padding-top:20px;border-bottom:1px solid var(--line)}
.week button{height:100%;display:flex;flex-direction:column;justify-content:flex-end;align-items:center;gap:4px;min-width:0}
.week i{display:block;width:min(24px,64%);border-radius:4px 4px 0 0;background:var(--ink);opacity:.28}
.week button.today i{opacity:1}
.week button[aria-pressed="true"]:not(.today) i{opacity:.55}
.week .v{font-size:11px;font-weight:700;color:var(--ink);font-variant-numeric:tabular-nums;line-height:1}
.week-days{display:grid;grid-template-columns:repeat(7,minmax(0,1fr));margin-top:6px;font-size:11px;font-weight:600;color:var(--muted);text-align:center}
.week-read{margin:8px 0 0;font-size:13px;color:var(--muted);min-height:1.3em;font-variant-numeric:tabular-nums}
.sheet-panel .opt.static{cursor:default}
'''

ICONS = r'''  flame: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 21c-3.9 0-6.5-2.6-6.5-6.1 0-3.3 2.3-5.4 3.6-7.8.4 1.6 1.2 2.7 2.4 3.4.3-2.8 1.6-5.2 3.6-7 .2 3.3 3.4 5.6 3.4 10.2 0 4.200-2.700 7.300-6.500 7.300z"/></svg>',
  clock: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><circle cx="12" cy="12" r="8.5"/><path d="M12 7.5V12l3 2"/></svg>',
'''

STATS = r'''/* ---------- stats: time listened, plays per day, the streak ---------- */
const ST = { total: 0, best: 0, days: {}, last: 0, sent: '', at: 0, timer: 0 };
const dayKey = d => { const x = d || new Date(); return x.getFullYear() + '-' + String(x.getMonth() + 1).padStart(2, '0') + '-' + String(x.getDate()).padStart(2, '0'); };
const dayAgo = n => { const d = new Date(); d.setHours(12, 0, 0, 0); d.setDate(d.getDate() - n); return d; };
const statDay = k => ST.days[k] || (ST.days[k] = { s: 0, p: {} });
const DAY_NAMES = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
function fmtLong(sec) { const m = Math.floor((sec || 0) / 60), h = Math.floor(m / 60); return m < 1 ? '0 min' : h ? h + ' h' + (m % 60 ? ' ' + (m % 60) + ' min' : '') : m + ' min'; }
function addListen(sec) { if (!(sec > 0)) return; ST.total += sec; statDay(dayKey()).s += sec; saveStats(false); }
/* days in a row with at least a minute listened; today only counts once it has that minute, and missing it does not break the streak until the day is over */
function streak() {
  const ok = i => { const d = ST.days[dayKey(dayAgo(i))]; return !!d && d.s >= 60; };
  let n = 0; for (let i = ok(0) ? 0 : 1; i < 400 && ok(i); i++) n++;
  return n;
}
function weekStats() {
  const days = [], plays = {}; let secs = 0;
  for (let i = 6; i >= 0; i--) { const d = dayAgo(i), x = ST.days[dayKey(d)]; days.push({ d, s: x ? x.s : 0 }); if (x) { secs += x.s; for (const id in x.p) plays[id] = (plays[id] || 0) + x.p[id]; } }
  return { days, secs, top: Object.keys(plays).filter(id => track(id)).sort((a, b) => plays[b] - plays[a]).slice(0, 5).map(id => ({ t: track(id), n: plays[id] })) };
}
function saveStats(now) {
  if (!S.ready || !store || !store.canWrite || store.settingsOk === false) return;      // never before the saved stats have been read in
  clearTimeout(ST.timer);
  const wait = 60000 - (Date.now() - ST.at);
  if (!now && wait > 0) { ST.timer = setTimeout(() => saveStats(true), wait); return; }      // saved about once a minute, and when playback stops
  /* about a year of days is kept for the streak; which uploads were played is only kept for the last few weeks */
  const keys = Object.keys(ST.days).sort(), days = {}, old = dayKey(dayAgo(21));
  keys.slice(0, Math.max(0, keys.length - 400)).forEach(k => { delete ST.days[k]; });
  keys.slice(-400).forEach(k => { const d = ST.days[k]; if (k < old) d.p = {}; days[k] = { s: Math.round(d.s), p: d.p }; });
  ST.best = Math.max(ST.best, streak());
  const doc = { total: Math.round(ST.total), best: ST.best, days }, sig = JSON.stringify(doc); if (sig === ST.sent) return; ST.sent = sig; ST.at = Date.now();
  Promise.resolve(store.set('settings', 'stats', doc)).catch(() => { ST.sent = ''; });
}
/* an older copy never takes away what was counted here: the higher number wins */
function mergeStats(doc, map) {
  if (!doc || typeof doc !== 'object') return;
  ST.total = Math.max(ST.total, +doc.total || 0); ST.best = Math.max(ST.best, Math.round(+doc.best || 0));
  const days = doc.days && typeof doc.days === 'object' ? doc.days : {};
  for (const k in days) {
    if (!/^\d{4}-\d\d-\d\d$/.test(k)) continue;
    const r = days[k] || {}, d = statDay(k), p = r.p && typeof r.p === 'object' ? r.p : {};
    d.s = Math.max(d.s, +r.s || 0);
    for (const id in p) { const to = map ? map.get(id) : id; if (to) d.p[to] = Math.max(d.p[to] || 0, Math.round(+p[id] || 0)); }
  }
}
function statsChips() {
  if (!S.opt.hStats || ST.total < 60) return '';
  const s = streak();
  return '<div class="stat-chips"><button class="stat-chip" data-act="stats">' + IC.flame + (s ? s + ' day streak' : 'No streak yet') + '</button>' +
    '<button class="stat-chip" data-act="stats">' + IC.clock + fmtLong(ST.total) + ' listened</button></div>';
}
function statsSheet(pick) {
  const w = weekStats(), s = streak(), today = 6, sel = pick == null ? today : pick, max = Math.max(60, ...w.days.map(d => d.s));
  const read = i => { const d = w.days[i]; return (i === today ? 'Today' : DAY_NAMES[d.d.getDay()]) + ': ' + fmtLong(d.s); };
  const bars = w.days.map((d, i) => {
    const h = d.s >= 1 ? Math.max(3, Math.round(d.s / max * 100)) : 0;
    return '<button class="' + (i === today ? 'today' : '') + '" data-act="stats-day" data-i="' + i + '" aria-pressed="' + (i === sel) + '" aria-label="' + read(i) + '">' +
      (i === today ? '<span class="v">' + Math.round(d.s / 60) + '</span>' : '') + '<i style="height:' + h + '%"></i></button>';
  }).join('');
  sheet('<h2>Your stats</h2><p class="sub">Counted from version 8 on, for this library.</p>' +
    '<div class="stats-big"><div><b>' + fmtLong(ST.total) + '</b><span>Listened in total</span></div><div><b>' + fmtLong(w.secs) + '</b><span>The last 7 days</span></div>' +
    '<div><b>' + s + (s === 1 ? ' day' : ' days') + '</b><span>Streak, best ' + Math.max(ST.best, s) + '</span></div></div>' +
    '<div><span class="fld-l">Minutes each day</span><div class="week" id="weekChart">' + bars + '</div>' +
    '<div class="week-days" aria-hidden="true">' + w.days.map(d => '<span>' + DAY_NAMES[d.d.getDay()].charAt(0) + '</span>').join('') + '</div>' +
    '<p class="week-read" id="weekRead">' + read(sel) + '</p></div>' +
    '<div><span class="fld-l">Most played this week</span>' + (w.top.length ? '<div class="opts">' + w.top.map(x => '<div class="opt static">' + trackCover(x.t) + '<span class="grow">' + esc(x.t.title) + '</span><span class="tick">' + playsText(x.n) + '</span></div>').join('') + '</div>'
      : '<p class="sub">Nothing played yet this week.</p>') + '</div>' +
    '<button class="btn" data-act="sheet-close">Close</button>', { kind: 'stats' });
}

'''

HOME = r'''function homeView() {
  if (!S.tracks.length) {
    return '<div class="empty">' + '<span class="cover" style="--h:338;--hb:24;--hc:312" aria-hidden="true">' + coverBars(null).map(x => '<i style="height:' + x + '%"></i>').join('') + '</span>' +
      '<h2>Nothing here yet</h2><p>Upload a video and its sound becomes something you can loop, shuffle and trim.</p>' +
      '<button class="btn primary" data-act="tab" data-tab="upload">' + IC.plus + 'Upload your first one</button></div>';
  }
  const o = S.opt, hr = new Date().getHours(), hello = hr < 5 ? 'Up late' : hr < 12 ? 'Good morning' : hr < 18 ? 'Good afternoon' : 'Good evening';
  const rot = S.home.rot.map(track).filter(Boolean), newest = S.tracks.slice(0, 5), liked = likedTracks();
  const card = (t, i) => {
    const n = S.plays[t.id] || 0, meta = i === 0 && t.id === S.home.rotFirst ? 'Last played' : n ? playsText(n) : fmt(playDur(t));
    return '<button class="rot' + (P.cur === t.id ? ' cur' : '') + '" data-key="' + esc(t.id) + '" style="--h:' + hueOf(t.id) + '" data-act="play" data-id="' + esc(t.id) + '" data-ctx="rot">' + trackCover(t, P.cur === t.id) +
      '<span class="tt"><span class="title">' + esc(t.title) + '</span><span class="meta">' + meta + '</span></span></button>';
  };
  const plTile = p => '<button class="tile" data-key="' + esc(p.id) + '" data-act="pl-open" data-id="' + esc(p.id) + '">' + plCover(p) + '<span class="title">' + esc(p.name) + '</span><span class="meta">' + countText(plTracks(p).length) + '</span></button>';
  const likedTile = liked.length ? '<button class="tile" data-key="liked" data-act="pl-open" data-id="' + LIKED + '">' + likedCover() + '<span class="title">Liked</span><span class="meta">' + countText(liked.length) + '</span></button>' : '';
  return '<div class="hello"><h2 class="page-t">' + hello + '</h2><p class="count">' + countText(S.tracks.length) + ', ' + fmt(sumDur(S.tracks)) + ' of audio</p>' + statsChips() + '</div>' +
    '<div class="bar"><button class="btn primary wide big" data-act="shuffle-all">' + IC.shuffle + 'Shuffle everything</button><button class="btn wide" data-act="play-all">' + IC.play + 'Play all</button></div>' +
    (o.hPresets ? presetsHome() : '') +
    (o.hRotation && rot.length ? secHead('Your rotation') + '<div class="rot-grid" id="rotGrid">' + rot.map(card).join('') + '</div>' : '') +
    (o.hPlaylists ? secHead('Playlists', S.playlists.length ? '<button class="link" data-act="tab" data-tab="library" data-lib="playlists">See all</button>' : '') +
      (S.playlists.length || likedTile ? '<div class="strip" id="plStrip">' + likedTile + S.playlists.map(plTile).join('') + '</div>'
        : '<div class="hint-card"><p>Group uploads into sets, one for each kind of workout.</p><button class="btn sm" data-act="pl-new">' + IC.plus + 'New playlist</button></div>') : '') +
    (o.hNewest ? secHead('Newest uploads', '<button class="link" data-act="tab" data-tab="library" data-lib="uploads">See all</button>') +
      '<div class="list">' + newest.map((t, i) => trackRow(t, i, 'all')).join('') + '</div>' : '');
}

'''

def apply(d):
    d.rep("function saveRecent(now) {\n  S.recentSig = JSON.stringify(S.recent);\n  if (!store || !store.canWrite || store.settingsOk === false) return;",
          "function saveRecent(now) {\n  S.recentSig = JSON.stringify(S.recent);\n  if (!S.ready || !store || !store.canWrite || store.settingsOk === false) return;      // never before the saved counts have been read in")
    d.before('</style>', '[hidden]{display:none!important}\n')
    d.before('</style>', CSS)
    # ----- options -----
    d.rep("const OPT_DEFAULTS = { autoTrim: true, speed: 1, keepPitch: false, level: false, fade: 0, sections: true, sort: 'new' };",
          "const OPT_DEFAULTS = { autoTrim: true, speed: 1, keepPitch: false, level: false, fade: 0, sections: true, sort: 'new', delay: 0, join: false, hStats: true, hPresets: true, hRotation: true, hPlaylists: true, hNewest: true };")
    d.rep("  ['autoTrim', 'keepPitch', 'level', 'sections'].forEach(k => { if (typeof o[k] === 'boolean') d[k] = o[k]; });",
          "  ['autoTrim', 'keepPitch', 'level', 'sections', 'join', 'hStats', 'hPresets', 'hRotation', 'hPlaylists', 'hNewest'].forEach(k => { if (typeof o[k] === 'boolean') d[k] = o[k]; });\n"
          "  if ([0, 3, 5, 10].indexOf(+o.delay) >= 0) d.delay = +o.delay;")
    d.rep("    setOpt(d.k, d.k === 'speed' || d.k === 'fade' ? +d.v : d.v); render();", "    setOpt(d.k, d.k === 'speed' || d.k === 'fade' || d.k === 'delay' ? +d.v : d.v); render();")
    d.rep("plays: {}, gone: new Set(), raw: null, presets: [], presetSig: '[]', home: { recent: [], top: [] }, full: false };",
          "plays: {}, gone: new Set(), raw: null, presets: [], presetSig: '[]', home: { recent: [], top: [], rot: [], rotFirst: null }, full: false };")
    # ----- icons -----
    d.rep("  tick: '<svg width=\"14\" height=\"14\"", ICONS + "  tick: '<svg width=\"14\" height=\"14\"")
    # ----- Your rotation -----
    d.rep("function freezeHome() { S.home.recent = (S.recent || []).slice(0, 10); S.home.top = topIds().slice(0, 10); }",
          """/* last played first, then the most played, then the rest of what was played lately; six at most */
function rotationIds() {
  const out = [], add = id => { if (id && track(id) && out.indexOf(id) < 0) out.push(id); };
  add((S.recent || [])[0]); topIds().forEach(add); (S.recent || []).forEach(add);
  return out.slice(0, 6);
}
function freezeHome() { S.home.recent = (S.recent || []).slice(0, 10); S.home.top = topIds().slice(0, 10); S.home.rot = rotationIds(); S.home.rotFirst = (S.recent || [])[0] || null; }""")
    d.rep("  if (ctx === 'top') return { ids: S.home.top.filter(track), label: 'Most played' };",
          "  if (ctx === 'top') return { ids: S.home.top.filter(track), label: 'Most played' };\n  if (ctx === 'rot') return { ids: S.home.rot.filter(track), label: 'Your rotation' };")
    # ----- playlist covers -----
    d.rep("""function plCover(p) {
  if (p.cover) return '<span class="cover img" aria-hidden="true">' + imgTag(p.cover) + '</span>';
  return colorCover(p.color || 'blue', plLetter(p));
}""", """function plCover(p) {
  if (p.cover) return '<span class="cover img" aria-hidden="true">' + imgTag(p.cover) + '</span>';
  const ts = plTracks(p);       // no picture picked: four uploads make a collage, fewer show the first one
  if (ts.length >= 4) return '<span class="cover mosaic" aria-hidden="true">' + ts.slice(0, 4).map(t => '<span class="cover' + (t.cover ? ' img' : '') + '" style="' + auraStyle(t.id) + '">' + (t.cover ? imgTag(t.cover) : '') + '</span>').join('') + '</span>';
  if (ts.length) return trackCover(ts[0]);
  return colorCover(p.color || 'blue', plLetter(p));
}""")
    # ----- Home -----
    d.cut("function homeView() {", "/* ----- Library ----- */", HOME)
    # ----- Settings: Home group -----
    d.rep("    group('Look', setCol('Background', 'Pick a color, or tap the last circle to use a photo of your own.', bgSwatches())) +\n",
          "    group('Look', setCol('Background', 'Pick a color, or tap the last circle to use a photo of your own.', bgSwatches())) +\n"
          "    group('Home',\n"
          "      setRow('Stats', 'Your streak and time listened, under the greeting.', swBtn('hStats', 'Show stats on Home')) +\n"
          "      setRow('Presets', '', swBtn('hPresets', 'Show presets on Home')) +\n"
          "      setRow('Your rotation', 'What you played last and what you play most, in one small grid.', swBtn('hRotation', 'Show Your rotation on Home')) +\n"
          "      setRow('Playlists', '', swBtn('hPlaylists', 'Show playlists on Home')) +\n"
          "      setRow('Newest uploads', '', swBtn('hNewest', 'Show newest uploads on Home'))) +\n")
    # ----- stats: counting, saving, reading back -----
    d.before("/* ---------- options ---------- */", STATS)
    d.rep("function notePlay(id) { S.plays[id] = (S.plays[id] || 0) + 1; saveRecent(false); }",
          "function notePlay(id) { S.plays[id] = (S.plays[id] || 0) + 1; saveRecent(false); const d = statDay(dayKey()); d.p[id] = (d.p[id] || 0) + 1; saveStats(false); }")
    d.rep("  if (psig !== S.presetSig) { S.presets = plist; S.presetSig = psig; }\n",
          "  if (psig !== S.presetSig) { S.presets = plist; S.presetSig = psig; }\n  mergeStats(sets.find(x => x.id === 'stats'));\n")
    d.rep("window.addEventListener('pagehide', () => { flushDelete(); saveRecent(true); });\ndocument.addEventListener('visibilitychange', () => { if (document.visibilityState === 'hidden') { flushDelete(); saveRecent(true); } });",
          "window.addEventListener('pagehide', () => { flushDelete(); saveRecent(true); saveStats(true); });\ndocument.addEventListener('visibilitychange', () => { if (document.visibilityState === 'hidden') { flushDelete(); saveRecent(true); saveStats(true); } });")
    d.after("const ACT = {\n", "  stats() { statsSheet(null); },\n  'stats-day'(d) { if (sheetCtx && sheetCtx.kind === 'stats') statsSheet(+d.i); },\n")
    # ----- backup and restore carry the stats -----
    d.rep("settings: { bg, opts: S.opt, recent: S.recent, plays: S.plays, presets: S.presets } };",
          "settings: { bg, opts: S.opt, recent: S.recent, plays: S.plays, presets: S.presets, stats: { total: Math.round(ST.total), best: ST.best, days: ST.days } } };")
    d.rep("      saveRecent(true); freezeHome();", "      if (st.stats) { mergeStats(st.stats, idMap); saveStats(true); }\n      saveRecent(true); freezeHome();")
