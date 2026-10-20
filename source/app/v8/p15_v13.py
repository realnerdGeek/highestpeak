# V13: the app becomes Ear Worm (new name and sound wave logo), the greeting says your username, selecting several uploads
# is out in the open (Home and Library, long-press, Select all), and shortcuts: quick settings, a settings search, and
# quick actions on the computer app's icon.
from p14_v12 import LOGO, NAV_LOGO

WAVE = ('<path d="M16 62 C24 36 36 36 42 54 S60 74 70 44" fill="none" stroke="#C8F135" stroke-width="13" stroke-linecap="round"/>')
BANDS = ('<path d="M16 62 C24 36 36 36 42 54 S60 74 70 44" fill="none" stroke="#A6CF17" stroke-width="13" stroke-dasharray="1.5 6.5" stroke-dashoffset="-4"/>')
HEAD = ('<circle cx="70" cy="44" r="11" fill="#C8F135"/><circle cx="73" cy="40.8" r="4.3" fill="#FFFFFF"/><circle cx="74" cy="40.2" r="2.2" fill="#17121F"/>')
def icon(bands):
    return ('<svg viewBox="0 0 100 100" aria-hidden="true"><rect width="100" height="100" fill="#17121F"/><g transform="translate(5 0)">'
            + WAVE + (BANDS if bands else '') + HEAD + '</g></svg>')
# the full icon, as the home screen and computer app icons are drawn from it
ICON_FULL = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" width="1024" height="1024"><rect width="100" height="100" fill="#17121F"/><g transform="translate(5 0)">'
             + WAVE + BANDS + HEAD + '</g></svg>')
BRAND = '<span class="brand-ic">' + icon(False) + '</span><span class="brand-t">Ear <b>Worm</b></span>'

CSS = r'''
/* Ear Worm: the icon is its own dark square; "Worm" is lime on dark looks, the same ink as "Ear" on light ones */
:root{--worm-text:var(--ink)}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){--worm-text:#C8F135}}
:root[data-theme="dark"]{--worm-text:#C8F135}
:root[data-skin="dark"]{--worm-text:#C8F135}
:root[data-skin="light"]{--worm-text:var(--ink)}
.brand-ic{flex:none;display:block;width:30px;height:30px;border-radius:7px;overflow:hidden;box-shadow:0 0 0 1px color-mix(in srgb,var(--ink) 10%,transparent)}
.brand-ic svg{display:block;width:100%;height:100%}
.brand-t{font-family:ui-rounded,"SF Pro Rounded",system-ui,-apple-system,sans-serif;font-weight:700;letter-spacing:-.02em}
.brand-t b{font-weight:700;color:var(--worm-text)}
h1 .brand-t{font-size:25px}
.ask-head .brand-ic{width:64px;height:64px;border-radius:15px;margin-bottom:4px}
/* the greeting row, with Select */
.hello-row{display:flex;align-items:baseline;justify-content:space-between;gap:12px}
.hello-row .btn{flex:none}
/* selecting several uploads */
.sel-top{position:sticky;top:0;z-index:6;margin:10px -18px 4px;padding:10px 18px 12px;background:var(--bg);display:flex;flex-direction:column;gap:10px;border-bottom:1px solid var(--line)}
.sel-line{display:flex;align-items:center;gap:8px}
.sel-line .count{margin:0;flex:1;min-width:0}
.sel-line .btn.wide{flex:1 1 0;min-width:0}
.row-hit{-webkit-touch-callout:none;-webkit-user-select:none;user-select:none}
/* settings shortcuts */
.set-q{margin-top:14px}
.group .set-list{margin-top:0}
.set.found{animation:setFound 1.8s ease-out}
@keyframes setFound{0%,35%{background:color-mix(in srgb,var(--ink) 9%,transparent);box-shadow:0 0 0 10px color-mix(in srgb,var(--ink) 9%,transparent)}100%{background:transparent;box-shadow:0 0 0 10px transparent}}
@media (prefers-reduced-motion: reduce){.set.found{animation:none;outline:2px solid var(--ink);outline-offset:6px}}
@media (min-width: 900px){
  .nav-logo .brand-ic{width:30px;height:30px}
  .sel-top{margin-inline:-48px;padding-inline:48px}
  .sel-line .btn.wide{flex:0 0 auto;min-width:170px}
  .set-side .set-q{margin:0 0 12px;height:46px}
  .set-side .set-q input{font-size:15px}
}
'''

HOME_SEL = r'''/* Home while selecting: every upload, ready to tick */
function selTop() {
  const ids = visibleTracks().map(t => t.id), n = S.sel ? S.sel.size : 0, allOn = ids.length > 0 && ids.every(id => S.sel.has(id));
  return '<div class="sel-top"><div class="sel-line"><p class="count pick" id="selCount">' + n + ' selected</p><button class="btn sm" id="selAll" data-act="sel-all">' + (allOn ? 'Select none' : 'Select all') + '</button><button class="btn sm primary" data-act="sel-done">Done</button></div>' +
    '<div class="sel-line"><button class="btn sm wide" data-act="sel-add">Add to playlist</button><button class="btn sm wide warn" id="selDel" data-act="sel-del">Delete' + (n ? ' ' + n : '') + '</button></div></div>';
}
function homeSelView() {
  return pageTitle('Select uploads') + selTop() + '<div class="list" id="homeSel">' + visibleTracks().map((t, i) => trackRow(t, i, 'all')).join('') + '</div>';
}
'''

SETTINGS = r'''const QUICK = { k: 'quick', name: 'Quick settings' };
SET_IC.quick = '<path d="M13 3L5 14h6l-1 7 8-11h-6z"/>';
const segCtl = (k, cur, opts) => '<div class="seg" role="radiogroup">' + opts.map(x => '<button role="radio" aria-checked="' + (String(x[0]) === String(cur)) + '" data-act="opt" data-k="' + k + '" data-v="' + x[0] + '">' + x[1] + '</button>').join('') + '</div>';
/* the three settings changed most, at the top of Settings */
function quickBody() {
  const o = S.opt, left = T.at ? Math.max(1, Math.ceil((T.at - Date.now()) / 60000)) : 0;
  return setCol('Speed', o.speed === 1 ? 'Normal speed.' : (o.speed < 1 ? 'Slowed to ' : 'Sped up to ') + o.speed + ' times normal.', segCtl('speed', o.speed, [[0.75, '0.75×'], [0.85, '0.85×'], [1, '1×'], [1.15, '1.15×'], [1.25, '1.25×']])) +
    setCol('Start delay', o.delay ? 'Counts down ' + o.delay + ' seconds, then plays.' : 'Plays the moment you tap play.', segCtl('delay', o.delay, [[0, 'Off'], [3, '3 s'], [5, '5 s'], [10, '10 s']])) +
    setCol('Stop timer', left ? 'Playback stops in about ' + left + ' min.' : 'Stop playing after a set time.', segCtl('timer', T.at ? T.mins : 0, [[0, 'Off'], [15, '15'], [30, '30'], [45, '45'], [60, '60 min']]));
}
const setSearchBox = () => '<label class="search set-q">' + IC.search + '<input type="search" id="setQ" placeholder="Search settings" value="' + esc(S.setQ || '') + '" autocomplete="off" autocapitalize="off" spellcheck="false" enterkeyhint="search" aria-label="Search settings"></label>';
/* other words people use for each setting */
const SET_WORDS = {
  'Speed': 'tempo fast faster slow slower slowed sped nightcore', 'Keep the original pitch': 'pitch chipmunk deep', 'Start delay': 'countdown wait beep before',
  'Stop timer': 'sleep timer minutes', 'Stop after loops': 'repeat count plays times loop', 'Play saved sections': 'section part trim',
  'Volume leveling': 'loudness normalize loud quiet volume', 'Loop fade': 'fade crossfade click pop', 'Remove end clips': 'tiktok logo outro ending chime watermark',
  'Keep original videos': 'video save space', 'Cut end clips from videos': 'video ending outro tiktok', 'Check every upload for an end clip': 'scan fix old end clip tiktok',
  'Join uploads': 'merge combine stitch', 'Background': 'theme color colour wallpaper dark light mode photo look', 'Stats': 'streak time listened',
  'Your rotation': 'recent most played', 'Newest uploads': 'recent', 'Recently deleted': 'trash bin restore undo deleted', 'Clear library on this device': 'wipe reset erase delete everything',
  'Back up library': 'backup export save zip', 'Restore from backup': 'import restore backup', 'Sync your library': 'account sign in log in login create account sync',
  'Sync': 'sign out log out logout sync now cloud', 'Sync videos': 'video cloud', 'Two-step sign-in': '2fa two factor authenticator code mfa security keeper',
  'Password': 'change password reset', 'Delete account': 'remove account close'
};
/* every setting on every page, read from the pages themselves so the search never goes stale */
function setIndex() {
  const out = [], tpl = document.createElement('template');
  setSecs().forEach(s => {
    tpl.innerHTML = secBody(s.k, false);
    tpl.content.querySelectorAll('.set').forEach(el => {
      const st = el.querySelector('.set-t'), b = el.querySelector('button'), sub = (el.querySelector('.sub') || {}).textContent || '';
      let label = (st ? st.textContent : b ? b.textContent : '').trim(), find = 't:' + label, extra = SET_WORDS[label] || '';
      if (el.querySelector('#acctUser')) { label = 'Username'; find = 'id:acctUser'; extra = 'username name email account change'; }
      else if (el.querySelector('#setStorage')) { label = 'Storage'; find = 'id:setStorage'; extra = 'space storage used uploads playlists'; }
      if (!label) return;
      out.push({ sec: s.k, secName: s.name, label, find, hay: (label + ' ' + sub + ' ' + s.name + ' ' + extra).toLowerCase() });
    });
  });
  return out;
}
function findResults() {
  const q = String(S.setQ || '').toLowerCase().trim(), words = q.split(/\s+/).filter(Boolean);
  const hits = setIndex().filter(h => words.every(w => h.hay.indexOf(w) >= 0))
    .map(h => ({ h, r: h.label.toLowerCase().indexOf(q) === 0 ? 0 : h.label.toLowerCase().indexOf(q) > 0 ? 1 : 2 })).sort((a, b) => a.r - b.r).slice(0, 30).map(x => x.h);
  if (!hits.length) return '<div class="empty" id="setNone"><p>No settings match that. Try speed, timer, video or password.</p></div>';
  return '<div class="card set-list" id="setHits">' + hits.map(h => '<button class="set-go" data-act="set-find" data-sec="' + h.sec + '" data-find="' + esc(h.find) + '"><span class="grow"><span class="set-t">' + esc(h.label) + '</span><span class="sub">' + esc(h.secName) + '</span></span>' + IC.chev + '</button>').join('') + '</div>';
}
/* what sits under the search box: search results, or (phone) quick settings and the list of pages, or (computer) the open page */
function setFindBody() {
  if (S.setQ && S.setQ.trim()) return findResults();
  const secs = setSecs();
  if (isPC()) { const all = [QUICK].concat(secs), cur = all.find(s => s.k === S.setSec) || all[0]; return '<h2 class="sec-t">' + cur.name + '</h2>' + (cur.k === 'quick' ? group('', quickBody()) : secBody(cur.k, false)); }
  return group('Quick settings', quickBody()) +
    '<section class="group"><h3>All settings</h3><div class="card set-list" id="setList">' + secs.map(s => '<button class="set-go" id="set-' + s.k + '" data-act="set-sec" data-sec="' + s.k + '"><span class="set-ic">' + svgIc(SET_IC[s.k]) + '</span><span class="grow"><span class="set-t">' + s.name + '</span><span class="sub">' + esc(s.sub()) + '</span></span>' + IC.chev + '</button>').join('') + '</div></section>';
}
/* on a phone: search, quick settings and a list of pages, each opening with a back arrow; on a computer: the pages down the side */
function settingsView() {
  const secs = setSecs();
  if (window.__HP_SETTINGS_ALL) return pageTitle('Settings') + secs.map(s => secBody(s.k, true)).join('');
  if (isPC()) {
    const all = [QUICK].concat(secs), cur = all.find(s => s.k === S.setSec) || all[0], q = !!(S.setQ && S.setQ.trim());
    return pageTitle('Settings') + '<div class="set-wrap"><nav class="set-side" aria-label="Settings sections">' + setSearchBox() +
      all.map(s => '<button id="side-' + s.k + '" data-act="set-sec" data-sec="' + s.k + '" aria-current="' + (!q && s === cur) + '">' + svgIc(SET_IC[s.k]) + '<span>' + s.name + '</span></button>').join('') +
      '</nav><div class="set-main" id="setMain">' + setFindBody() + '</div></div>';
  }
  const cur = secs.find(s => s.k === S.setSec);
  if (!cur) return pageTitle('Settings') + setSearchBox() + '<div id="setFindOut">' + setFindBody() + '</div>';
  return '<button class="back" id="setBack" data-act="set-back">' + IC.back + 'Settings</button><h2 class="page-t set-pt">' + cur.name + '</h2>' + secBody(cur.k, false);
}
/* a search result opens its page and points at the setting */
function flashSetting(find) {
  let el = null;
  if (find.indexOf('id:') === 0) { const x = document.getElementById(find.slice(3)); el = x && x.closest('.set'); }
  else { const t = find.slice(2); el = Array.from(document.querySelectorAll('#view .set')).find(s => { const st = s.querySelector('.set-t'), b = s.querySelector('button'); return (st ? st.textContent : b ? b.textContent : '').trim() === t; }) || null; }
  if (!el) return;
  try { el.scrollIntoView({ block: 'center', behavior: calm ? 'auto' : 'smooth' }); } catch (e) { el.scrollIntoView(); }
  el.classList.remove('found'); void el.offsetWidth; el.classList.add('found'); setTimeout(() => el.classList.remove('found'), 1900);
}
'''

EXTRA = r'''/* ----- V13: long-press an upload to start selecting (Home and Library), and the computer app's icon shortcuts ----- */
function startSelect(id) {
  if (!(S.tab === 'home' || (S.tab === 'library' && S.lib === 'uploads' && !S.pl)) || !store || !store.canWrite) return;
  if (!S.sel) S.sel = new Set();
  S.sel.add(id);
  try { if (navigator.vibrate) navigator.vibrate(12); } catch (e) { /* no buzz */ }
  render();
}
const LP = { t: 0, x: 0, y: 0, el: null, fired: 0 };
const lpCancel = () => { clearTimeout(LP.t); LP.t = 0; LP.el = null; };
document.addEventListener('pointerdown', e => {
  LP.fired = 0;                                   // a new touch: only the click of the long-press itself is held back
  if (e.button > 0) return;
  const hit = e.target && e.target.closest ? e.target.closest('.row-hit[data-act="play"][data-ctx="all"]') : null; if (!hit) return;
  lpCancel(); LP.x = e.clientX; LP.y = e.clientY; LP.el = hit;
  LP.t = setTimeout(() => { const el = LP.el; LP.t = 0; LP.el = null; if (el && el.isConnected) { LP.fired = Date.now(); startSelect(el.dataset.id); } }, 480);
}, { passive: true });
document.addEventListener('pointermove', e => { if (LP.t && (Math.abs(e.clientX - LP.x) > 10 || Math.abs(e.clientY - LP.y) > 10)) lpCancel(); }, { passive: true });
document.addEventListener('pointerup', () => { if (LP.t) lpCancel(); }, { passive: true });
document.addEventListener('pointercancel', lpCancel, { passive: true });
window.addEventListener('scroll', lpCancel, { passive: true });
/* the tap that ends a long-press is not also a tap on the upload (the next touch is a tap again) */
document.addEventListener('click', e => { if (LP.fired && Date.now() - LP.fired < 2000) { LP.fired = 0; e.preventDefault(); e.stopImmediatePropagation(); } }, true);
document.addEventListener('contextmenu', e => { if (LP.t || Date.now() - LP.fired < 900) e.preventDefault(); });
document.addEventListener('keydown', e => { if (e.key === 'Escape' && S.sel && !sheetOpen() && !S.full && !VID.open) { S.sel = null; render(); } });
document.addEventListener('input', e => {
  const el = e.target; if (!el || el.id !== 'setQ') return;
  S.setQ = el.value; const out = document.getElementById('setFindOut') || document.getElementById('setMain'); if (out) paint(out, setFindBody());
});
/* Quick actions on the computer app's icon open the app with ?go=… */
const GO = (() => { try { const g = new URLSearchParams(location.search).get('go'); if (g) history.replaceState(null, '', location.pathname + location.hash); return g; } catch (e) { return null; } })();
if (GO) {
  const run = n => {
    if (!S.ready) return n < 200 && setTimeout(() => run(n + 1), 100);
    if (GO === 'upload') go('upload');
    else if (GO === 'library') go('library', { lib: 'uploads' });
    else if (GO === 'search') { go('search'); setTimeout(() => { const q = document.getElementById('q'); if (q) q.focus(); }, 60); }
    else if (GO === 'shuffle' && S.tracks.length) ACT['shuffle-all']();
  };
  setTimeout(() => run(0), 0);
}

'''

ACTS = r'''  'sel-all'() { if (!S.sel) return; const ids = visibleTracks().map(t => t.id), allOn = ids.length > 0 && ids.every(id => S.sel.has(id)); S.sel = allOn ? new Set() : new Set(ids); render(); },
  'set-find'(d) { S.setQ = ''; S.setSec = d.sec; const qi = document.getElementById('setQ'); if (qi) qi.value = ''; viewKey = ''; render(); window.scrollTo(0, 0); setTimeout(() => flashSetting(d.find || ''), 80); },
'''


def apply(d):
    d.rep('<title>HighestPeak</title>', '<title>Ear Worm</title>')
    d.before('</style>', CSS)
    # the name and logo: header, the computer sidebar, the sync invite
    d.rep('<h1><svg class="logo" viewBox="0 0 34 30" aria-hidden="true"><defs><linearGradient id="peakGrad" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="var(--brand-a)"/><stop offset="1" stop-color="var(--brand-b)"/></linearGradient></defs><g fill="currentColor"><rect x="0" y="20.5" width="3.4" height="8.5" rx="1.7" opacity=".34"/><rect x="5.1" y="15.2" width="3.4" height="13.8" rx="1.7" opacity=".58"/><rect x="10.2" y="9.1" width="3.4" height="19.9" rx="1.7" opacity=".86"/><rect x="20.4" y="10.9" width="3.4" height="18.1" rx="1.7" opacity=".86"/><rect x="25.5" y="16.7" width="3.4" height="12.3" rx="1.7" opacity=".58"/><rect x="30.6" y="21.3" width="3.4" height="7.7" rx="1.7" opacity=".34"/></g><rect x="15.3" y="1" width="3.4" height="28" rx="1.7" fill="url(#peakGrad)"/></svg><span>Highest<b>Peak</b></span></h1>',
          '<h1>' + BRAND + '</h1>')
    d.rep(NAV_LOGO, '<div class="nav-logo">' + BRAND + '</div>\n  ')
    d.rep(LOGO('peakGradA').replace("'", "\\'"), ('<span class="brand-ic">' + icon(True) + '</span>').replace("'", "\\'"))
    # the name in what the app says
    for a, b in [
        ("return 'That file is not a HighestPeak backup.';", "return 'That file is not an Ear Worm backup.';"),
        ("artist: 'HighestPeak',", "artist: 'Ear Worm',"),
        ("toast('Email confirmed. Now sign in in the HighestPeak app.')", "toast('Email confirmed. Now sign in in the Ear Worm app.')"),
        ("'Password changed. Sign in with it in the HighestPeak app.'", "'Password changed. Sign in with it in the Ear Worm app.'"),
        ("Or keep using HighestPeak on this device only.", "Or keep using Ear Worm on this device only."),
        ("issuer: 'HighestPeak', friendly_name: 'HighestPeak ' +", "issuer: 'Ear Worm', friendly_name: 'Ear Worm ' +"),
        ("<li>Add HighestPeak to the app:", "<li>Add Ear Worm to the app:"),
        ("Type the 6-digit code the app shows for HighestPeak.", "Type the 6-digit code the app shows for Ear Worm."),
        ("type the 6-digit code for HighestPeak.</p>", "type the 6-digit code for Ear Worm. If you set it up before the name changed, it is listed as HighestPeak.</p>"),
        ("This deletes your HighestPeak account for good:", "This deletes your Ear Worm account for good:"),
        ("name = 'HighestPeak-backup-' +", "name = 'EarWorm-backup-' +"),
    ]:
        d.rep(a, b)
    # the greeting says the username, and Home has Select (and a select view of its own)
    d.rep("  const o = S.opt, hr = new Date().getHours(), hello = hr < 5 ? 'Up late' : hr < 12 ? 'Good morning' : hr < 18 ? 'Good afternoon' : 'Good evening';",
          "  if (S.sel) return homeSelView();\n"
          "  const o = S.opt, hr = new Date().getHours(), hello = (hr < 5 ? 'Up late' : hr < 12 ? 'Good morning' : hr < 18 ? 'Good afternoon' : 'Good evening') + (SYNC.sess && SYNC.username ? ', ' + esc(SYNC.username) : '');")
    d.rep("  return '<div class=\"hello\"><h2 class=\"page-t\">' + hello + '</h2><p class=\"count\">'",
          "  return '<div class=\"hello\"><div class=\"hello-row\"><h2 class=\"page-t\" id=\"hello\">' + hello + '</h2>' + (store && store.canWrite && S.tracks.length > 1 ? '<button class=\"btn sm\" id=\"homeSelect\" data-act=\"sel-start\">Select</button>' : '') + '</div><p class=\"count\">'")
    d.before('/* ----- Library ----- */', HOME_SEL)
    d.rep("""        ? '<div class="bar"><button class="btn sm wide" data-act="sel-add">Add to playlist</button><button class="btn sm warn" data-act="sel-del">Delete</button><button class="btn sm primary" data-act="sel-done">Done</button></div><p class="count pick" id="selCount">' + S.sel.size + ' selected</p>'""",
          """        ? selTop()""")
    d.rep("""<button class="icon-btn" data-act="sel-start" aria-label="Select several uploads">' + IC.multi + '</button></div>') +""",
          """<button class="btn sm" id="libSelect" data-act="sel-start">Select</button></div>') +""")
    # the username arrives after the first check: show it on Home too
    d.rep("    if (!sheetOpen()) codeSheet(false);\n    if (S.tab === 'settings') render();\n    return false;", "    if (!sheetOpen()) codeSheet(false);\n    render();\n    return false;")
    d.rep("userSheet(true); }, 300); }\n  if (S.tab === 'settings') render();\n  return true;", "userSheet(true); }, 300); }\n  render();\n  return true;")
    # settings: search and quick settings
    d.cut('function settingsView() {', 'let viewKey = ', SETTINGS)
    d.rep("home: { recent: [], top: [], rot: [], rotFirst: null }, full: false, setSec: null };", "home: { recent: [], top: [], rot: [], rotFirst: null }, full: false, setSec: null, setQ: '' };")
    d.before('/* ---------- loudness, for volume leveling ---------- */', EXTRA)
    d.after("const ACT = {\n", ACTS)
    d.rep("S.pl = null; S.sel = null; S.setSec = null;", "S.pl = null; S.sel = null; S.setSec = null; S.setQ = '';")
    d.rep("  'set-sec'(d) { S.setSec = d.sec; render();", "  'set-sec'(d) { S.setSec = d.sec; S.setQ = ''; const qi = document.getElementById('setQ'); if (qi) qi.value = ''; render();")
