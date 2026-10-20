# V12: a real computer layout, Settings in sections, the sync invite, usernames, two-step sign-in,
# deleting the account, and clearing the library on one device.
LOGO = lambda gid: ('<svg class="logo" viewBox="0 0 34 30" aria-hidden="true"><defs><linearGradient id="' + gid + '" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="var(--brand-a)"/><stop offset="1" stop-color="var(--brand-b)"/></linearGradient></defs>'
  '<g fill="currentColor"><rect x="0" y="20.5" width="3.4" height="8.5" rx="1.7" opacity=".34"/><rect x="5.1" y="15.2" width="3.4" height="13.8" rx="1.7" opacity=".58"/><rect x="10.2" y="9.1" width="3.4" height="19.9" rx="1.7" opacity=".86"/>'
  '<rect x="20.4" y="10.9" width="3.4" height="18.1" rx="1.7" opacity=".86"/><rect x="25.5" y="16.7" width="3.4" height="12.3" rx="1.7" opacity=".58"/><rect x="30.6" y="21.3" width="3.4" height="7.7" rx="1.7" opacity=".34"/></g>'
  '<rect x="15.3" y="1" width="3.4" height="28" rx="1.7" fill="url(#' + gid + ')"/></svg>')

CSS = r'''
/* settings in sections */
.set-list{margin-top:16px;padding:2px 14px}
.set-go{display:flex;align-items:center;gap:14px;width:100%;min-height:62px;padding:10px 0;border-bottom:1px solid var(--line);text-align:left}
.set-go:last-child{border-bottom:0}
.set-go .grow{display:flex;flex-direction:column;gap:2px;min-width:0}
.set-go .sub{margin:0;color:var(--muted);font-size:13px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.set-go > svg{flex:none;color:var(--muted)}
.set-ic{flex:none;width:36px;height:36px;border-radius:11px;display:grid;place-items:center;background:var(--raise);color:var(--ink)}
.set-pt{margin-top:2px}
.sec-t{font:800 26px/1.1 var(--font);letter-spacing:-.03em;margin:0}
.switch[disabled]{opacity:.4;cursor:default}
.btn.danger{background:var(--danger);color:#fff}
a.btn{text-decoration:none;color:inherit}
/* the sync invite, usernames, two-step sign-in */
.ask-head{display:flex;flex-direction:column;align-items:center;gap:10px;text-align:center;padding:10px 6px 4px}
.ask-head .logo{width:58px;height:52px;margin-bottom:4px}
.ask-head .sub{max-width:36ch}
.uname-in{display:flex;align-items:center;gap:2px;min-height:50px;padding:0 14px;border-radius:14px;background:var(--raise)}
.uname-in span{color:var(--muted);font-weight:700}
.uname-in input[type="text"]{flex:1;min-width:0;min-height:48px;padding:0;border:0;background:none;outline:0}
.mfa-steps{margin:0;padding-left:20px;color:var(--muted);font-size:14px;display:flex;flex-direction:column;gap:6px}
.mfa-steps b{color:var(--ink)}
.mfa-qr{align-self:center;background:#fff;padding:12px;border-radius:18px;box-shadow:0 1px 4px var(--shadow)}
.mfa-qr img{display:block;width:176px;height:176px}
.mfa-key{display:flex;flex-direction:column;align-items:center;gap:4px;font-size:13px;font-weight:600;color:var(--muted)}
.mfa-key code{font:700 16px/1.3 ui-monospace,SFMono-Regular,Menlo,monospace;color:var(--ink);letter-spacing:.04em;text-align:center;overflow-wrap:anywhere;-webkit-user-select:all;user-select:all}
#mfaCode{font-size:22px;letter-spacing:.3em;text-align:center;font-variant-numeric:tabular-nums}
.nav-logo{display:none}
.f-body,.f-main,.f-side{display:contents}

/* ---------- computers: a sidebar, the whole width, a player bar along the bottom, everything bigger ---------- */
@media (min-width: 900px){
  :root{--side-w:248px}
  body{font-size:17px}
  .nav{top:0;right:auto;bottom:var(--player-h,0px);width:var(--side-w);padding:22px 14px;border-top:0;border-right:1px solid var(--line);overflow-y:auto}
  .nav-in{max-width:none;display:flex;flex-direction:column;align-items:stretch;gap:4px}
  .nav-logo{display:flex;align-items:center;gap:10px;padding:4px 12px 24px;font:500 23px/1.1 var(--font);letter-spacing:-.04em;color:var(--ink)}
  .nav-logo b{font-weight:800}
  .nav-logo .logo{width:30px;height:26px}
  .nav button{flex-direction:row;justify-content:flex-start;gap:14px;min-height:48px;padding:0 12px;border-radius:12px;font:600 16px/1 var(--font)}
  .nav button[aria-selected="true"]{background:var(--raise);color:var(--ink)}
  .nav .plus{width:24px;height:24px;border-radius:8px}
  .nav .plus svg{width:16px;height:16px}
  .nav .dot{top:9px;left:31px;right:auto}
  .app{max-width:none;margin:0 0 0 var(--side-w);padding:30px 48px calc(44px + var(--player-h,0px))}
  #view,.notice{max-width:1600px}
  .top{display:none}
  .page-t{font-size:40px;margin-top:4px}
  .sec-h{margin:36px 0 12px}
  .sec-h h3{font-size:24px}
  .link{font-size:15px}
  .btn{min-height:50px;padding:0 22px;font-size:16px}
  .btn.sm{min-height:44px;padding:0 18px;font-size:15px}
  .btn.xs{min-height:38px;padding:0 14px;font-size:14px}
  .icon-btn{width:50px;height:50px}
  .icon-btn.sm{width:44px;height:44px}
  .strip{margin-inline:-48px;padding-inline:48px;gap:18px}
  .tile{width:180px}
  .tile .cover{width:180px;height:180px;border-radius:26px}
  .tile .cover b{font-size:72px}
  .tile .title{font-size:16px}
  .tile .meta{font-size:14px}
  .row-hit{grid-template-columns:60px minmax(0,1fr);gap:16px;min-height:80px}
  .row .cover{width:60px;height:60px;border-radius:15px}
  .tt .title{font-size:17px}
  .tt .meta{font-size:14px}
  .more,.check{width:50px;height:50px}
  .acts{margin-left:76px}
  .grid{grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:30px 24px}
  .pl-row .tt .title{font-size:17px}
  .rot-grid{grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:12px}
  .rot{grid-template-columns:56px minmax(0,1fr);min-height:72px}
  .rot .cover{width:56px;height:56px;border-radius:13px}
  .rot .title{font-size:16px}
  .rot .meta{font-size:13px}
  .preset{width:330px}
  .preset .title{font-size:16px}
  .stat-chip{min-height:38px;padding:0 14px;font-size:14px}
  .tabs{max-width:460px}
  .tab{min-height:42px;font-size:16px}
  .search{max-width:680px;height:54px}
  .search input{font-size:17px}
  .bar .btn.wide{flex:0 0 auto;min-width:170px}
  .pl-head{flex-direction:row;align-items:flex-end;gap:28px}
  .pl-head .cover{width:200px;height:200px;border-radius:36px}
  .pl-head .cover b{font-size:90px}
  .pl-head h2{font-size:44px}
  .pl-head .meta{font-size:15px}
  .drop{max-width:900px;padding:48px 28px}
  .drop h2{font-size:26px}
  .drop p{font-size:16px;max-width:46ch}
  .empty h2{font-size:24px}
  .empty p{font-size:16px}
  .hint-card{max-width:620px}
  .imp{font-size:15px}
  .count{font-size:14px}
  .group h3{font-size:14px}
  .card{padding:4px 22px;border-radius:22px}
  .card .set{padding:16px 0}
  .set-t{font-size:17px}
  .set .sub{font-size:15px}
  .set-wrap{display:grid;grid-template-columns:230px minmax(0,1fr);gap:44px;align-items:start;margin-top:22px}
  .set-side{position:sticky;top:24px;display:flex;flex-direction:column;gap:2px}
  .set-side button{display:flex;align-items:center;gap:12px;min-height:46px;padding:0 12px;border-radius:12px;font-weight:600;font-size:15px;color:var(--muted)}
  .set-side button[aria-current="true"]{background:var(--raise);color:var(--ink)}
  .set-main{max-width:780px;min-width:0}
  .set-main .group:first-of-type{margin-top:14px}
  /* the player bar */
  .player{left:0;right:0;bottom:0;padding:0;z-index:13}
  .player-in{max-width:none;border-radius:0;border:0;border-top:1px solid var(--line);box-shadow:none;background:var(--sheet);-webkit-backdrop-filter:none;backdrop-filter:none;padding:12px 24px;display:grid;
    grid-template-columns:minmax(240px,1fr) auto minmax(280px,620px) auto minmax(240px,1fr);grid-template-rows:auto auto;column-gap:14px;row-gap:2px;align-items:center}
  .player .now{grid-column:1;grid-row:1/3;padding-right:12px}
  .player .now-open{grid-template-columns:56px minmax(0,1fr);gap:12px}
  .player .now .cover{width:56px;height:56px;border-radius:13px}
  .player .now .title{font-size:16px}
  .player .ctl{grid-column:2/5;grid-row:1;justify-content:center;gap:10px}
  .player .ctl .rnd{width:44px;height:44px}
  .player .ctl .big{width:50px;height:50px}
  .player .tog{width:62px;height:46px}
  .player .times{display:contents}
  .player #tCur{grid-column:2;grid-row:2;min-width:40px;text-align:right}
  .player .wave{grid-column:3;grid-row:2;height:30px;margin:0}
  .player #tDur{grid-column:4;grid-row:2;min-width:40px}
  .player .chips{grid-column:5;grid-row:1;justify-content:flex-end}
  .player .vol{grid-column:5;grid-row:2;justify-self:end;width:min(190px,100%)}
  #sizeBtn,.player .mini-only{display:none!important}
  .toast{left:calc(var(--side-w) + (100vw - var(--side-w)) / 2)}
  /* the big player: picture and controls on the left, what is up next on the right */
  .full{padding-block:24px 32px}
  .full-in{max-width:1180px;padding-inline:48px}
  .f-body{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:56px;align-items:start;margin-top:6px}
  .f-main,.f-side{display:flex;flex-direction:column;gap:14px;min-width:0}
  .f-side{position:sticky;top:0;max-height:calc(100vh - 120px);overflow-y:auto;padding-right:4px}
  .full .f-side .sec-h{margin:0}
  .f-cover{width:min(100%,420px,48vh)}
  .f-title{font-size:30px}
  /* sheets become centred windows */
  .sheet{align-items:center;padding:24px}
  .sheet-panel{max-width:520px;max-height:min(88vh,920px);border-radius:26px;padding:24px 26px;animation:popIn .2s cubic-bezier(.2,.8,.2,1)}
  .sheet-panel::before{display:none}
  .sheet.out .sheet-panel{animation:popOut .16s ease-in forwards}
  .ed-in{max-width:940px}
  .ed-track{height:200px}
  .ed-grid{grid-template-columns:repeat(4,minmax(0,1fr))}
}
@keyframes popIn{from{opacity:0;transform:scale(.96) translateY(8px)}to{opacity:1;transform:none}}
@keyframes popOut{to{opacity:0;transform:scale(.97)}}
@media (min-width: 900px) and (hover: hover){
  .nav button:hover,.set-side button:hover{color:var(--ink);background:color-mix(in srgb,var(--ink) 6%,transparent)}
  .nav button[aria-selected="true"]:hover,.set-side button[aria-current="true"]:hover{background:var(--raise)}
  .list > .row{border-radius:14px;padding-inline:10px;margin-inline:-10px}
  .list > .row:hover{background:color-mix(in srgb,var(--ink) 5%,transparent)}
  .set-go:hover .set-t{text-decoration:underline}
}
@media (prefers-reduced-motion: reduce){.sheet-panel,.sheet.out .sheet-panel{animation:none!important}}
'''

NAV_LOGO = '<div class="nav-logo">' + LOGO('peakGradS') + '<span>Highest<b>Peak</b></span></div>\n  '

# Settings in sections. The text of every setting is the same as V11; it is only split into pages.
SETTINGS = r'''const svgIc = p => '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">' + p + '</svg>';
const SET_IC = {
  account: '<circle cx="12" cy="8.5" r="3.6"/><path d="M5 20c.8-3.6 3.6-5.6 7-5.6s6.2 2 7 5.6"/>',
  playback: '<circle cx="12" cy="12" r="8.5"/><path d="M10.2 8.8v6.4l5-3.2z" fill="currentColor"/>',
  sound: '<path d="M4 9.5h3.5L12 6v12l-4.5-3.5H4z"/><path d="M15.5 9a4 4 0 0 1 0 6M18 6.5a7.5 7.5 0 0 1 0 11"/>',
  uploads: '<path d="M12 15V5M8 9l4-4 4 4"/><path d="M5 14v3.5A1.5 1.5 0 0 0 6.5 19h11a1.5 1.5 0 0 0 1.5-1.5V14"/>',
  look: '<path d="M12 4a8 8 0 1 0 0 16c1.1 0 1.6-.7 1.6-1.5 0-1.2-1-1.5-1-2.6 0-.9.7-1.4 1.6-1.4h1.9A3.9 3.9 0 0 0 20 10.6C20 7 16.4 4 12 4z"/><circle cx="8" cy="11" r="1.1" fill="currentColor"/><circle cx="10.5" cy="7.6" r="1.1" fill="currentColor"/><circle cx="14.5" cy="7.6" r="1.1" fill="currentColor"/>',
  home: '<path d="M4 11l8-7 8 7v8a1.5 1.5 0 0 1-1.5 1.5H14v-6h-4v6H5.5A1.5 1.5 0 0 1 4 19z"/>',
  library: '<path d="M5 4v16M10 4v16M15 5l4 14.5"/>',
  backup: '<rect x="4" y="5" width="16" height="4" rx="1.5"/><path d="M5.5 9v8.5A1.5 1.5 0 0 0 7 19h10a1.5 1.5 0 0 0 1.5-1.5V9M10 13h4"/>'
};
const SET_SECS = [
  { k: 'account', name: 'Account', on: () => SYNC.avail, sub: () => SYNC.sess ? (SYNC.username ? '@' + SYNC.username + ', ' : '') + (SYNC.sess.email || 'Signed in') : 'Sync your library across your devices' },
  { k: 'playback', name: 'Playback', sub: () => 'Speed, start delay, stop timer' },
  { k: 'sound', name: 'Sound', sub: () => 'Volume leveling, loop fade' },
  { k: 'uploads', name: 'Uploads and videos', sub: () => 'End clips, kept videos, join' },
  { k: 'look', name: 'Look', sub: () => 'Background' },
  { k: 'home', name: 'Home', sub: () => 'What shows on Home' },
  { k: 'library', name: 'Library and storage', sub: () => 'Space used, recently deleted, clear library' },
  { k: 'backup', name: 'Backup', sub: () => 'Back up or restore your library' }
];
const setSecs = () => SET_SECS.filter(s => !s.on || s.on());
/* one section's settings; with all, each group keeps its heading (every section on one page) */
function secBody(k, all) {
  const o = S.opt, t = name => (all ? name : '');
  const seg = (k, cur, opts) => '<div class="seg" role="radiogroup">' + opts.map(x => '<button role="radio" aria-checked="' + (String(x[0]) === String(cur)) + '" data-act="opt" data-k="' + k + '" data-v="' + x[0] + '">' + x[1] + '</button>').join('') + '</div>';
  const left = T.at ? Math.max(1, Math.ceil((T.at - Date.now()) / 60000)) : 0;
  if (k === 'account') return accountSec(all);
  if (k === 'playback') return group(t('Playback'),
      setCol('Speed', o.speed === 1 ? 'Normal speed.' : (o.speed < 1 ? 'Slowed to ' : 'Sped up to ') + o.speed + ' times normal.', seg('speed', o.speed, [[0.75, '0.75×'], [0.85, '0.85×'], [1, '1×'], [1.15, '1.15×'], [1.25, '1.25×']])) +
      setRow('Keep the original pitch', 'Off gives the slowed or sped-up sound, where the pitch moves with the speed.', swBtn('keepPitch', 'Keep the original pitch')) +
      setCol('Start delay', o.delay ? 'Counts down ' + o.delay + ' seconds with a beep each second, then plays. Only when you tap play.' : 'Plays the moment you tap play.', seg('delay', o.delay, [[0, 'Off'], [3, '3 s'], [5, '5 s'], [10, '10 s']])) +
      setCol('Stop timer', left ? 'Playback stops in about ' + left + ' min.' : 'Stop playing after a set time.', seg('timer', T.at ? T.mins : 0, [[0, 'Off'], [15, '15'], [30, '30'], [45, '45'], [60, '60 min']])) +
      setRow('Stop after loops', T.loops ? 'Stops after ' + T.loops + ' more ' + (T.loops === 1 ? 'play' : 'plays') + '.' : 'Count the times an upload finishes, then stop.',
        '<div class="stepper"><button data-act="loops" data-d="-1" aria-label="One loop fewer">&minus;</button><output id="loopsOut">' + (T.loops || 'Off') + '</output><button data-act="loops" data-d="1" aria-label="One loop more">+</button></div>') +
      setRow('Play saved sections', 'A section is one part of an upload that you mark in Trim or cut. Only that part plays, and nothing is deleted.', swBtn('sections', 'Play saved sections')));
  if (k === 'sound') return group(t('Sound'),
      setRow('Volume leveling', 'Plays everything at a similar loudness.', swBtn('level', 'Volume leveling')) +
      setCol('Loop fade', 'A quick fade out and back in where an upload loops or ends, so it does not click.', seg('fade', o.fade, [[0, 'Off'], [40, 'Short'], [120, 'Medium'], [300, 'Long']])) +
      '<p class="sub note">These two send the sound through extra processing, and so does the volume bar on iPhone when it is below full. If playback stops when your phone locks, turn these off or slide the volume back to full.</p>');
  if (k === 'uploads') return group(t('Uploads'),
      setRow('Remove end clips', END_CLIP_SUB, swBtn('autoTrim', 'Remove end clips', 'autoTrimSwitch')) +
      setRow('Keep original videos', KEEP_VID_SUB, swBtn('keepVideo', 'Keep original videos')) +
      setRow('Cut end clips from videos', END_VID_SUB, swBtn('videoEnd', 'Cut end clips from videos')) +
      '<div class="set col"><button class="btn sm" data-act="trim-all">Check every upload for an end clip</button><p class="sub" id="trimAllStatus" aria-live="polite">' + esc(trimAllMsg) + '</p></div>' +
      setRow('Join uploads', 'Adds Join to the options of each upload, to stitch two or more into one that loops as a whole.', swBtn('join', 'Join uploads')));
  if (k === 'look') return group(t('Look'), setCol('Background', 'Pick a color, or tap the last circle to use a photo of your own.', bgSwatches()));
  if (k === 'home') return group(t('Home'),
      setRow('Stats', 'Your streak and time listened, under the greeting.', swBtn('hStats', 'Show stats on Home')) +
      setRow('Presets', '', swBtn('hPresets', 'Show presets on Home')) +
      setRow('Your rotation', 'What you played last and what you play most, in one small grid.', swBtn('hRotation', 'Show Your rotation on Home')) +
      setRow('Playlists', '', swBtn('hPlaylists', 'Show playlists on Home')) +
      setRow('Newest uploads', '', swBtn('hNewest', 'Show newest uploads on Home')));
  if (k === 'library') return group(t('Library'), '<div class="set"><div class="grow"><div class="set-t">' + countText(S.tracks.length) + ', ' + S.playlists.length + (S.playlists.length === 1 ? ' playlist' : ' playlists') + '</div><p class="sub" id="setStorage">' + esc(storageText()) + '</p></div></div>' + binRow()) +
      (store && store.kind === 'local' ? group('', '<div class="set"><div class="grow"><div class="set-t">Clear library on this device</div><p class="sub">' +
        (SYNC.sess ? 'Deletes everything here and signs this device out. Your cloud copy and your other devices keep it all.' : 'Deletes every upload, video, playlist, like and stat on this device for good.') +
        '</p></div><button class="btn sm warn" id="clearBtn" data-act="clear-lib">Clear</button></div>') : '');
  if (k === 'backup') return group(t('Backup'),
      '<div class="set col"><div><div class="set-t">Back up library</div><p class="sub">Saves one file with every upload, cover, playlist, like and setting' + (S.tracks.some(hasVideo) ? ', and the videos if you want them' : '') + '. Keep it somewhere safe, like Files or iCloud Drive.</p></div><button class="btn sm" id="backupBtn" data-act="backup"' + (S.tracks.length && !BK.busy ? '' : ' disabled') + '>Back up library</button>' + (BK.file ? '<button class="btn sm primary" id="backupSave" data-act="backup-save">Save backup file</button>' : '') + '</div>' +
      '<div class="set col"><div><div class="set-t">Restore from backup</div><p class="sub">Pick a backup file and everything in it is put back. Anything already here is skipped.</p></div><button class="btn sm" id="restoreBtn" data-act="restore"' + (store && store.canWrite && !BK.busy ? '' : ' disabled') + '>Restore from backup</button>' +
      '<p class="sub" id="backupStatus" aria-live="polite">' + esc(BK.msg) + '</p></div>');
  return '';
}
/* on a phone: a list of sections, each opening its own page with a back arrow; on a computer: the sections down the side */
function settingsView() {
  const secs = setSecs();
  if (window.__HP_SETTINGS_ALL) return pageTitle('Settings') + secs.map(s => secBody(s.k, true)).join('');
  let cur = secs.find(s => s.k === S.setSec);
  if (isPC()) {
    cur = cur || secs[0];
    return pageTitle('Settings') + '<div class="set-wrap"><nav class="set-side" aria-label="Settings sections">' +
      secs.map(s => '<button id="side-' + s.k + '" data-act="set-sec" data-sec="' + s.k + '" aria-current="' + (s === cur) + '">' + svgIc(SET_IC[s.k]) + '<span>' + s.name + '</span></button>').join('') +
      '</nav><div class="set-main" id="setMain"><h2 class="sec-t">' + cur.name + '</h2>' + secBody(cur.k, false) + '</div></div>';
  }
  if (!cur) return pageTitle('Settings') + '<div class="card set-list" id="setList">' + secs.map(s => '<button class="set-go" id="set-' + s.k + '" data-act="set-sec" data-sec="' + s.k + '"><span class="set-ic">' + svgIc(SET_IC[s.k]) + '</span><span class="grow"><span class="set-t">' + s.name + '</span><span class="sub">' + esc(s.sub()) + '</span></span>' + IC.chev + '</button>').join('') + '</div>';
  return '<button class="back" id="setBack" data-act="set-back">' + IC.back + 'Settings</button><h2 class="page-t set-pt">' + cur.name + '</h2>' + secBody(cur.k, false);
}
'''

ACCOUNT = r'''/* ----- V12: the Account section, usernames, two-step sign-in, deleting the account, clearing a device ----- */
const nap = ms => new Promise(r => setTimeout(r, ms));
const UNAME_RE = /^[a-z0-9._]{3,20}$/, digits6 = v => String(v || '').replace(/\D/g, '').slice(0, 6);
const verifiedTotp = u => ((u && u.factors) || []).filter(f => f && f.status === 'verified' && (f.factor_type || f.type || 'totp') === 'totp');
const NEED_CODE = 'Two-step sign-in is on for this account. Tap Enter code to keep syncing.';
/* the sign-in level in the access token: aal2 once the two-step code was given */
function jwtAal(at) { try { const p = String(at || '').split('.')[1].replace(/-/g, '+').replace(/_/g, '/'); return JSON.parse(atob(p + '==='.slice((p.length + 3) % 4))).aal || ''; } catch (e) { return ''; } }
function acctReset() { SYNC.username = null; SYNC.mfa = null; SYNC.needCode = false; SYNC.checked = false; SYNC.pending = null; SYNC.askedName = false; }
function acctCache() { try { const c = JSON.parse(localStorage.getItem('hp.user.' + SYNC.sess.uid) || 'null'); if (c && typeof c.u === 'string') SYNC.username = c.u; } catch (e) { /* unknown until checked */ } }
function setUsername(v) { SYNC.username = v; try { if (SYNC.sess) localStorage.setItem('hp.user.' + SYNC.sess.uid, JSON.stringify({ u: v })); } catch (e) { /* not kept */ } }
function keepSess(j) { const s = SYNC.sess || {}, n = sessFrom(j); n.uid = n.uid || s.uid; n.email = n.email || s.email; saveSess(n); return n; }
/* once per app start (and after the cloud turns this device away): is a two-step code owed, and what is the username */
async function acctCheck() {
  let u; try { u = await sbFetch('/auth/v1/user', { auth: true }); }
  catch (e) { if (e && (e.status === 401 || e.status === 403)) { signedOut('Your sign-in ended. Sign in again to keep syncing.'); return false; } throw e; }      // e.g. two-step sign-in was turned on from another device
  SYNC.mfa = verifiedTotp(u);
  if (SYNC.mfa.length && jwtAal(SYNC.sess.at) !== 'aal2') {
    SYNC.needCode = true; SYNC.err = NEED_CODE;
    if (!sheetOpen()) codeSheet(false);
    if (S.tab === 'settings') render();
    return false;
  }
  SYNC.needCode = false;
  try { const p = await sbFetch('/rest/v1/profiles?select=username&user_id=eq.' + SYNC.sess.uid, { auth: true }) || []; setUsername(p[0] && p[0].username ? p[0].username : ''); }
  catch (e) { if (e && e.status === 404) SYNC.username = null; else throw e; }      // no usernames table: carry on without them
  SYNC.checked = true; SYNC.checkedAt = Date.now();
  if (SYNC.username === '' && !SYNC.askedName) { SYNC.askedName = true; setTimeout(() => { if (SYNC.on && SYNC.username === '' && !sheetOpen()) userSheet(true); }, 300); }
  if (S.tab === 'settings') render();
  return true;
}
function mfaText() {
  if (!SYNC.mfa) return 'Checking your account. Needs a connection.';
  return SYNC.mfa.length ? 'On. Signing in asks for a 6-digit code from your authenticator app.' : 'Ask for a 6-digit code from an authenticator app, like Keeper or iPhone Passwords, each time you sign in.';
}
function accountSec(all) {
  if (!SYNC.sess) return group(all ? 'Account' : '', '<div class="set col"><div><div class="set-t">Sync your library</div><p class="sub">Sign in to keep your uploads, playlists and likes the same on your phone and your computer. Without an account everything stays on this device, like now.</p></div>' +
    '<div class="pair"><button class="btn sm" id="acctIn" data-act="acct-in">Sign in</button><button class="btn sm primary" id="acctNew" data-act="acct-new">Create account</button></div></div>');
  const n = SYNC.username, on = !!(SYNC.mfa && SYNC.mfa.length);
  return group(all ? 'Account' : '',
      '<div class="set"><div class="grow"><div class="set-t" id="acctUser">' + (n ? '@' + esc(n) : n === '' ? 'No username yet' : 'Signed in') + '</div><p class="sub" id="acctEmail">' + esc(SYNC.sess.email || '') + '</p></div>' +
        (n != null ? '<button class="btn sm' + (n ? '' : ' primary') + '" id="unameBtn" data-act="uname">' + (n ? 'Change' : 'Pick one') + '</button>' : '') + '</div>' +
      '<div class="set col"><div><div class="set-t">Sync</div><p class="sub" id="syncStatus" aria-live="polite">' + esc(syncText()) + '</p><p class="sub" id="syncStorage">' + esc(cloudText()) + '</p></div>' +
        (SYNC.needCode ? '<button class="btn sm primary" id="mfaEnter" data-act="mfa-enter">Enter code</button>' : '') +
        '<div class="pair"><button class="btn sm" id="syncNowBtn" data-act="sync-now"' + (SYNC.busy || SYNC.needCode ? ' disabled' : '') + '>Sync now</button><button class="btn sm" id="acctOut" data-act="acct-out">Sign out</button></div></div>' +
      setRow('Sync videos', 'Kept videos go to your other devices too. Uses a lot more cloud space. Videos over 50 MB stay on the device they were added on.', swBtn('syncVideo', 'Sync videos'))) +
    group('Security',
      setRow('Two-step sign-in', mfaText(), '<button class="switch" id="mfaSwitch" role="switch" aria-checked="' + on + '" data-act="mfa-toggle" aria-label="Two-step sign-in"' + (SYNC.mfa && !SYNC.needCode ? '' : ' disabled') + '></button>') +
      '<div class="set"><div class="grow"><div class="set-t">Password</div><p class="sub">Change the password you sign in with.</p></div><button class="btn sm" id="pwBtn" data-act="acct-pw">Change</button></div>') +
    group('', '<div class="set"><div class="grow"><div class="set-t">Delete account</div><p class="sub">Deletes your account, your username and the cloud copy of your library. The library on this device stays.</p></div><button class="btn sm warn" id="delAcctBtn" data-act="acct-del">Delete</button></div>');
}
/* the invite, once per device, for someone who has not signed in */
function askSync() {
  let seen = true; try { seen = localStorage.getItem('hp.syncAsked') === '1'; } catch (e) { seen = true; }
  if (seen) return;
  setTimeout(() => {
    if (SYNC.sess || sheetOpen() || !$('#editor').hidden || VID.open || S.full) return;
    try { localStorage.setItem('hp.syncAsked', '1'); } catch (e) { /* asked anyway */ }
    sheet('<div class="ask-head">ASK_LOGO<h2>Sync your library across your devices</h2><p class="sub">Make a free account and your uploads, playlists and likes show up on your phone and your computer. Or keep using HighestPeak on this device only.</p></div>' +
      '<button class="btn primary" id="askNew" data-act="acct-new">Create account</button><button class="btn" id="askIn" data-act="acct-in">Sign in</button><button class="link-btn" id="askLater" data-act="sheet-close">Not now</button>', { kind: 'ask' });
  }, 900);
}
/* usernames: picked after making an account, changed any time in Account */
function unameProblem(v) {
  if (!v) return 'Type a username.';
  if (/[^a-z0-9._]/.test(v)) return 'Only letters, numbers, dots and underscores.';
  if (v.length < 3) return 'At least 3 characters.';
  if (v.length > 20) return 'No more than 20 characters.';
  return '';
}
function userSheet(first) {
  sheet('<h2>' + (first ? 'Pick a username' : 'Change your username') + '</h2><p class="sub">3 to 20 characters: letters, numbers, dots and underscores.' + (first ? ' You can change it later in Settings, under Account.' : '') + '</p>' +
    '<form class="auth" data-form="uname"><label class="uname-in"><span>@</span><input type="text" id="unameIn" name="uname" autocomplete="username" autocapitalize="none" autocorrect="off" spellcheck="false" maxlength="20" placeholder="username" aria-label="Username" required data-focus value="' + esc(SYNC.username || '') + '"></label>' +
    '<p class="sub auth-msg" id="authMsg" aria-live="polite"></p><button type="submit" class="btn primary" id="authGo">Save</button></form>' +
    '<button class="btn" data-act="sheet-close">' + (first ? 'Later' : 'Cancel') + '</button>', { kind: 'uname' });
}
let unameSeq = 0, unameTimer = 0;
function unameTyped(el) {
  const low = el.value.toLowerCase(); if (low !== el.value) { const p = el.selectionStart; el.value = low; try { el.setSelectionRange(p, p); } catch (e) { /* fine */ } }
  const v = low.trim(), bad = unameProblem(v), seq = ++unameSeq; clearTimeout(unameTimer);
  if (bad) return authSay(v.length >= 3 || /[^a-z0-9._]/.test(v) ? bad : '', true);
  if (v === SYNC.username) return authSay('That is your username now.');
  authSay('Checking @' + v);
  unameTimer = setTimeout(async () => {
    try { const taken = await sbFetch('/rest/v1/rpc/username_taken', { method: 'POST', json: { name: v }, auth: true }); if (seq === unameSeq) authSay(taken ? '@' + v + ' is taken.' : '@' + v + ' is available.', !!taken); }
    catch (e) { if (seq === unameSeq) authSay(''); }
  }, 350);
}
/* two-step sign-in with an authenticator app (Keeper, iPhone Passwords and the like) */
function qrSrc(q) {
  q = String(q || ''); const i = q.indexOf(',');
  if (i > 0 && /^data:image\/svg\+xml/.test(q) && !/;base64$/.test(q.slice(0, i))) { let svg = q.slice(i + 1); try { if (/^%3C/i.test(svg)) svg = decodeURIComponent(svg); } catch (e) { /* as it is */ } return 'data:image/svg+xml;charset=utf-8,' + encodeURIComponent(svg); }
  return q;
}
async function mfaStart() {
  sheet('<h2>Turn on two-step sign-in</h2><p class="sub">Getting your setup code</p><button class="btn" data-act="sheet-close">Cancel</button>', { kind: 'mfa' });
  try {
    const u = await sbFetch('/auth/v1/user', { auth: true });
    for (const f of (u && u.factors) || []) if (f.status !== 'verified') await sbFetch('/auth/v1/factors/' + f.id, { method: 'DELETE', auth: true }).catch(() => {});      // an earlier setup that was not finished
    const j = await sbFetch('/auth/v1/factors', { method: 'POST', auth: true, json: { factor_type: 'totp', issuer: 'HighestPeak', friendly_name: 'HighestPeak ' + Math.random().toString(36).slice(2, 8) } });
    if (!sheetCtx || sheetCtx.kind !== 'mfa') { sbFetch('/auth/v1/factors/' + j.id, { method: 'DELETE', auth: true }).catch(() => {}); return; }
    mfaSetupSheet({ id: j.id, qr: j.totp && j.totp.qr_code, secret: j.totp && j.totp.secret, uri: j.totp && j.totp.uri });
  } catch (e) { if (sheetCtx && sheetCtx.kind === 'mfa') closeSheet(); toast(authText(e)); }
}
function mfaSetupSheet(f) {
  const key = String(f.secret || '').replace(/(.{4})/g, '$1 ').trim();
  sheet('<h2>Turn on two-step sign-in</h2><p class="sub">From now on, signing in also asks for a 6-digit code from an authenticator app, like Keeper or the Passwords app on iPhone.</p>' +
    '<ol class="mfa-steps"><li>Add HighestPeak to the app: scan this code with your phone, or on iPhone tap <b>Open in authenticator</b>. You can also copy the setup key into Keeper.</li><li>Type the 6-digit code the app shows for HighestPeak.</li></ol>' +
    (f.qr ? '<div class="mfa-qr"><img id="mfaQr" alt="Setup code to scan with your authenticator app" src="' + esc(qrSrc(f.qr)) + '"></div>' : '') +
    '<div class="mfa-key"><span>Setup key</span><code id="mfaKey">' + esc(key) + '</code></div>' +
    '<div class="pair">' + (f.uri ? '<a class="btn sm" id="mfaOpen" href="' + esc(f.uri) + '">Open in authenticator</a>' : '') + '<button type="button" class="btn sm" id="mfaCopy" data-act="mfa-copy">Copy setup key</button></div>' +
    '<form class="auth" data-form="mfaon"><input type="text" id="mfaCode" name="code" inputmode="numeric" autocomplete="one-time-code" placeholder="6-digit code" aria-label="6-digit code from the app" required><p class="sub auth-msg" id="authMsg" aria-live="polite"></p><button type="submit" class="btn primary" id="authGo">Turn on</button></form>' +
    '<button class="btn" data-act="mfa-cancel">Cancel</button>', { kind: 'mfa', factor: f.id, secret: f.secret });
}
function codeSheet(signin) {
  sheet('<h2>Enter your code</h2><p class="sub">' + (signin ? 'Two-step sign-in is on. ' : 'Two-step sign-in is on for your account. ') + 'Open your authenticator app and type the 6-digit code for HighestPeak.</p>' +
    '<form class="auth" data-form="mfacode"><input type="text" id="mfaCode" name="code" inputmode="numeric" autocomplete="one-time-code" placeholder="6-digit code" aria-label="6-digit code" required data-focus><p class="sub auth-msg" id="authMsg" aria-live="polite"></p><button type="submit" class="btn primary" id="authGo">' + (signin ? 'Sign in' : 'Continue') + '</button></form>' +
    '<button class="btn" data-act="mfa-code-cancel">Cancel</button>', { kind: 'mfacode' });
}
/* a fresh challenge for each try, then the code: the answer is a sign-in at the two-step level */
async function mfaVerify(factor, code, bearer) {
  const h = bearer ? { headers: { Authorization: 'Bearer ' + bearer } } : { auth: true };
  const ch = await sbFetch('/auth/v1/factors/' + factor + '/challenge', Object.assign({ method: 'POST', json: {} }, h));
  return sbFetch('/auth/v1/factors/' + factor + '/verify', Object.assign({ method: 'POST', json: { challenge_id: ch.id, code } }, h));
}
/* type a word to confirm the two that cannot be undone */
function wordSheet(title, body, word, label, form, id) {
  sheet('<h2>' + title + '</h2><p class="sub">' + esc(body) + '</p><form class="auth" data-form="' + form + '"><input type="text" id="' + id + '" name="word" autocomplete="off" autocapitalize="characters" autocorrect="off" spellcheck="false" placeholder="Type ' + word + '" aria-label="Type ' + word + ' to confirm" data-focus>' +
    '<p class="sub auth-msg" id="authMsg" aria-live="polite"></p><button type="submit" class="btn danger" id="authGo" disabled>' + label + '</button></form><button class="btn" data-act="sheet-close">Cancel</button>', { kind: form });
}
function delAcctSheet() {
  wordSheet('Delete account', 'This deletes your HighestPeak account for good: your username, your sign-in, and the copy of your library in the cloud. The library on this device stays here, and your other devices keep their copies, but nothing syncs any more. Type DELETE to confirm.', 'DELETE', 'Delete account', 'delacct', 'delConfirm');
}
function unsynced() {
  if (!SYNC.on || !SYNC.st) return 0;
  return Object.keys(SYNC.st.out).length + Array.from(allRefs(false)).filter(id => !SYNC.st.up.has(id) && store.has(id) && store.blobSize(id) <= SYNC_MAX).length;
}
function clearSheet() {
  let body;
  if (SYNC.sess) {
    const n = unsynced(), vids = !S.opt.syncVideo && S.tracks.some(hasVideo);
    body = 'Everything on this device is deleted: uploads, videos, playlists, likes and stats. This device also signs out. Your cloud copy and your other devices keep everything, so signing in again brings it back.' +
      (n ? ' ' + n + (n === 1 ? ' change has' : ' changes have') + ' not synced yet and will be lost.' : '') + (vids ? ' Kept videos are not synced, so the ones here are deleted for good.' : '');
  } else body = 'Everything on this device is deleted for good: uploads, videos, playlists, likes and stats. Back up your library first if you want to keep any of it.';
  wordSheet('Clear library on this device', body + ' Type CLEAR to confirm.', 'CLEAR', 'Clear library', 'clearlib', 'clearConfirm');
}
/* Deleting the account: its files first (an account that still owns files cannot be deleted), then the account itself.
   The library on this device is not touched. */
async function deleteAccount(say) {
  const s = SYNC.sess; if (!s) throw err('sb_signed_out');
  const was = SYNC.on; let gone = false; syncStop();
  for (let i = 0; i < 300 && SYNC.busy; i++) await nap(100);
  try {
    say('Deleting your cloud files');
    for (let round = 0; round < 40; round++) {
      const list = await sbFetch('/storage/v1/object/list/media', { method: 'POST', json: { prefix: s.uid, limit: 1000, offset: 0, sortBy: { column: 'name', order: 'asc' } }, auth: true }) || [];
      const names = list.filter(x => x && x.name && x.id).map(x => s.uid + '/' + x.name); if (!names.length) break;
      for (let i = 0; i < names.length; i += 500) { await sbFetch('/storage/v1/object/media', { method: 'DELETE', json: { prefixes: names.slice(i, i + 500) }, auth: true }); gone = true; }
    }
    say('Deleting your account');
    await sbFetch('/rest/v1/rpc/delete_my_account', { method: 'POST', json: {}, auth: true });
  } catch (e) {
    if (SYNC.sess && was) { if (gone && SYNC.st) { SYNC.st.up = new Set(); saveSt(); } syncStart(); }       // some files may have left the cloud already: they go up again
    throw e;
  }
  try { localStorage.removeItem('hp.sync.' + s.uid); localStorage.removeItem('hp.user.' + s.uid); } catch (e) { /* fine */ }
  SYNC.st = null; saveSess(null); acctReset();
}
/* Clearing this device: everything in its library goes, it signs out, and the page starts over. The cloud is not touched. */
async function clearLibrary() {
  if (!store || store.kind !== 'local') return;
  stopPlayer();
  const s = SYNC.sess;
  if (s) {
    syncStop(); for (let i = 0; i < 300 && SYNC.busy; i++) await nap(100);
    try { localStorage.removeItem('hp.sync.' + s.uid); } catch (e) { /* fine */ }
    await Promise.race([sbFetch('/auth/v1/logout', { method: 'POST', headers: { Authorization: 'Bearer ' + s.at } }).catch(() => {}), nap(1500)]);
    saveSess(null); acctReset();
  }
  const keep = new Set(['settings/opts']), ui = store.docs.settings.get('ui');
  if (ui && !(ui.bg && ui.bg.kind === 'wall')) keep.add('settings/ui');
  await store.clearAll(keep);
  try { localStorage.removeItem('gymtapes.session'); const b = JSON.parse(localStorage.getItem('gymtapes.bg') || 'null'); if (b && b.kind === 'wall') localStorage.removeItem('gymtapes.bg'); sessionStorage.setItem('hp.cleared', '1'); } catch (e) { /* fine */ }
  location.reload();
}
try { if (sessionStorage.getItem('hp.cleared')) { sessionStorage.removeItem('hp.cleared'); setTimeout(() => toast('Library cleared on this device.'), 700); } } catch (e) { /* fine */ }
document.addEventListener('input', e => {
  const el = e.target; if (!el || !el.id) return;
  if (el.id === 'unameIn') unameTyped(el);
  else if (el.id === 'mfaCode') { const v = digits6(el.value); if (v !== el.value) el.value = v; }
  else if (el.id === 'delConfirm' || el.id === 'clearConfirm') { const go = document.getElementById('authGo'); if (go) go.disabled = el.value.trim().toUpperCase() !== (el.id === 'delConfirm' ? 'DELETE' : 'CLEAR'); }
});
/* the space bar plays and pauses on a computer */
document.addEventListener('keydown', e => {
  if (e.key !== ' ' || e.repeat || e.ctrlKey || e.metaKey || e.altKey) return;
  const t = e.target; if (t && t.closest && t.closest('input,textarea,select,button,a,[contenteditable],[role="slider"]')) return;
  if (!track(P.cur) || sheetOpen() || VID.open || !$('#editor').hidden) return;
  e.preventDefault(); togglePlay();
});

'''.replace('ASK_LOGO', LOGO('peakGradA').replace("'", "\\'"))

ACTS = r'''  'set-sec'(d) { S.setSec = d.sec; render(); if (!isPC()) window.scrollTo(0, 0); },
  'set-back'() { S.setSec = null; render(); window.scrollTo(0, 0); },
  uname() { userSheet(!SYNC.username); },
  'acct-pw'() { newPwSheet(); },
  'acct-del'() { delAcctSheet(); },
  'clear-lib'() { clearSheet(); },
  'mfa-toggle'() { if (!SYNC.mfa || SYNC.needCode) return; if (SYNC.mfa.length) confirmSheet('Turn off two-step sign-in', 'Signing in will only need your email and password again.', 'Turn off', 'mfa-off-go', {}); else mfaStart(); },
  'mfa-off-go'() {
    closeSheet(); const list = (SYNC.mfa || []).slice();
    (async () => { try { for (const f of list) await sbFetch('/auth/v1/factors/' + f.id, { method: 'DELETE', auth: true }); SYNC.mfa = []; render(); toast('Two-step sign-in is off.'); } catch (e) { toast(authText(e)); } })();
  },
  'mfa-copy'() {
    const c = sheetCtx; if (!c || !c.secret) return;
    const pick = () => { const k = document.getElementById('mfaKey'); if (k && window.getSelection) { const r = document.createRange(); r.selectNodeContents(k); const s = getSelection(); s.removeAllRanges(); s.addRange(r); } toast('Select the key and copy it.'); };
    try { navigator.clipboard.writeText(c.secret).then(() => toast('Setup key copied.'), pick); } catch (e) { pick(); }
  },
  'mfa-cancel'() { const c = sheetCtx; closeSheet(); if (c && c.factor) sbFetch('/auth/v1/factors/' + c.factor, { method: 'DELETE', auth: true }).catch(() => {}); },
  'mfa-enter'() { codeSheet(false); },
  'mfa-code-cancel'() { const p = SYNC.pending; SYNC.pending = null; closeSheet(); if (p) sbFetch('/auth/v1/logout', { method: 'POST', headers: { Authorization: 'Bearer ' + p.sess.at } }).catch(() => {}); },
'''

FORMS = r'''  uname(f) {
    const v = f.elements.uname.value.trim().toLowerCase(), bad = unameProblem(v); if (bad) return authSay(bad, true);
    if (v === SYNC.username) return closeSheet();
    clearTimeout(unameTimer); unameSeq++;
    authRun(f, async () => {
      await sbFetch('/rest/v1/profiles?on_conflict=user_id', { method: 'POST', json: { user_id: SYNC.sess.uid, username: v }, auth: true, headers: { Prefer: 'resolution=merge-duplicates,return=minimal' } });
      setUsername(v); closeSheet(); render(); toast('Username saved: @' + v + '.');
    });
  },
  mfaon(f) {
    const c = sheetCtx, code = digits6(f.elements.code.value); if (!c || !c.factor) return;
    if (code.length !== 6) return authSay('Type the 6 digits from the app.', true);
    authRun(f, async () => { keepSess(await mfaVerify(c.factor, code)); SYNC.mfa = [{ id: c.factor, status: 'verified', factor_type: 'totp' }]; SYNC.needCode = false; closeSheet(); render(); toast('Two-step sign-in is on.'); });
  },
  mfacode(f) {
    const code = digits6(f.elements.code.value), p = SYNC.pending;
    if (code.length !== 6) return authSay('Type the 6 digits from the app.', true);
    authRun(f, async () => {
      if (p) { const n = sessFrom(await mfaVerify(p.factor, code, p.sess.at)); n.uid = n.uid || p.sess.uid; n.email = n.email || p.sess.email; SYNC.pending = null; saveSess(n); closeSheet(); syncStart(); render(); toast('Signed in. Syncing your library.'); }
      else if (SYNC.sess && SYNC.mfa && SYNC.mfa.length) {
        try { keepSess(await mfaVerify(SYNC.mfa[0].id, code)); } catch (e) { if (e && (e.status === 401 || e.status === 403) && !/insufficient/.test(e.code || '')) { closeSheet(); signedOut('Your sign-in ended. Sign in again with your code.'); return; } throw e; } SYNC.needCode = false; SYNC.checked = false; SYNC.err = ''; closeSheet(); render(); soon(100); toast('Code accepted. Syncing again.'); }
      else closeSheet();
    });
  },
  delacct(f) {
    if (f.elements.word.value.trim().toUpperCase() !== 'DELETE') return authSay('Type DELETE to confirm.', true);
    authRun(f, async () => { await deleteAccount(m => authSay(m)); closeSheet(); render(); toast('Account deleted. Your library is still on this device.'); });
  },
  clearlib(f) {
    if (f.elements.word.value.trim().toUpperCase() !== 'CLEAR') return authSay('Type CLEAR to confirm.', true);
    authRun(f, async () => { authSay('Clearing this device'); await clearLibrary(); });
  },
'''

AUTH_TEXT = r"""  if (c === 'mfa_verification_failed' || /invalid totp/i.test(m)) return 'That code did not work. Type the newest code from the app.';
  if (c === 'mfa_challenge_expired') return 'That took too long. Type the newest code and try again.';
  if (c === 'insufficient_aal' || /aal2/i.test(m)) return 'Sign out, sign in again with your code, then try once more.';
  if (c === 'mfa_totp_enroll_not_enabled' || c === 'mfa_totp_verify_not_enabled') return 'Two-step sign-in is turned off for this app in Supabase.';
  if (c === 'mfa_factor_name_conflict') return 'Try again in a moment.';
  if (c === '23505' || /duplicate key/i.test(m)) return 'That username is taken. Try another.';
  if (c === '23514') return 'Only letters, numbers, dots and underscores, 3 to 20 of them.';
  if (c === 'P0001' && /two-step/i.test(m)) return 'Enter your two-step code first: sign out, then sign in again with it.';
  if (c === 'user_not_found') return 'This account no longer exists.';
  if (c === 'session_not_found') return 'Your sign-in ended. Sign out, then sign in again.';
"""

CLEAR_ALL = r'''
    async clearAll(keep) {
      const kept = [];
      for (const c in docs) docs[c].forEach((d, id) => { if (keep.has(c + '/' + id)) kept.push([c + '/' + id, d]); });
      for (const c in docs) docs[c].clear();
      kept.forEach(([k, d]) => { const i = k.indexOf('/'); docs[k.slice(0, i)].set(k.slice(i + 1), d); });
      urls.forEach(u => URL.revokeObjectURL(u)); urls.clear(); blobs.clear();
      await run('docs', 'readwrite', s => { s.clear(); kept.forEach(([k, d]) => s.put(d, k)); });
      await run('blobs', 'readwrite', s => s.clear());
    },'''


def apply(d):
    d.before('</style>', CSS)
    # markup: the logo at the top of the sidebar; the big player split into two columns on a computer
    d.after('<nav class="nav" id="nav" aria-label="Main"><div class="nav-in" role="tablist">\n  ', NAV_LOGO)
    d.before('    <div class="f-cover" id="fCover"></div>', '    <div class="f-body"><div class="f-main">\n')
    d.before('    <div class="sec-h"><h3>Up next</h3>', '    </div><div class="f-side">\n')
    d.after('    <div class="list" id="fQueue" data-sortlist="queue"></div>\n', '    </div></div>\n')
    # computer or phone
    d.after("const calm = !!(window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches);\n",
            "const PCQ = window.matchMedia ? window.matchMedia('(min-width: 900px)') : null, isPC = () => !!(PCQ && PCQ.matches);\n")
    d.rep("  el.classList.toggle('mini', !!S.mini);", "  el.classList.toggle('mini', !!S.mini && !isPC());")
    d.rep("  document.documentElement.style.setProperty('--nav-h', $('#nav').offsetHeight + 'px');", "  document.documentElement.style.setProperty('--nav-h', (isPC() ? 0 : $('#nav').offsetHeight) + 'px');")
    d.rep("window.addEventListener('resize', () => { if (!$('#editor').hidden) { ED.bins = null; drawEd(); } updatePlayer(); });",
          "window.addEventListener('resize', () => { if (!$('#editor').hidden) { ED.bins = null; drawEd(); } updatePlayer(); });\n"
          "if (PCQ) { const flip = () => { viewKey = ''; render(); updatePlayer(); }; if (PCQ.addEventListener) PCQ.addEventListener('change', flip); else if (PCQ.addListener) PCQ.addListener(flip); }")
    # settings in sections
    d.cut('function settingsView() {', 'let viewKey = ', SETTINGS)
    d.rep("  const key = S.tab + (S.tab === 'library' ? '|' + S.lib + '|' + (S.pl || '') : ''), v = $('#view');",
          "  const key = S.tab + (S.tab === 'library' ? '|' + S.lib + '|' + (S.pl || '') : '') + (S.tab === 'settings' ? '|' + (S.setSec || '') + (isPC() ? '|pc' : '') : ''), v = $('#view');")
    d.rep("function go(tab, extra) { closeFull(); S.tab = tab; S.pl = null; S.sel = null;", "function go(tab, extra) { closeFull(); S.tab = tab; S.pl = null; S.sel = null; S.setSec = null;")
    d.rep("home: { recent: [], top: [], rot: [], rotFirst: null }, full: false };", "home: { recent: [], top: [], rot: [], rotFirst: null }, full: false, setSec: null };")
    # accounts
    d.rep("refreshing: null, recovery: null };", "refreshing: null, recovery: null,\n  username: null, mfa: null, needCode: false, checked: false, checkedAt: 0, pending: null, askedName: false };")
    d.rep("async function signIn(email, pw) { saveSess(sessFrom(await sbFetch('/auth/v1/token?grant_type=password', { method: 'POST', json: { email, password: pw } }))); }",
          "async function signIn(email, pw) { return sessFrom(await sbFetch('/auth/v1/token?grant_type=password', { method: 'POST', json: { email, password: pw } })); }")
    d.rep("  if (/rate.?limit|too many/i.test(c + ' ' + m)) return 'Too many tries. Wait a bit, then try again.';",
          AUTH_TEXT + "  if (/rate.?limit|too many/i.test(c + ' ' + m)) return 'Too many tries. Wait a bit, then try again.';")
    d.rep("function signedOut(msg) {\n  syncStop(); saveSess(null); render();", "function signedOut(msg) {\n  syncStop(); saveSess(null); acctReset(); render();")
    d.rep("  try {\n    if (!SYNC.st.merged) await firstMerge();",
          "  try {\n    if (SYNC.needCode) { SYNC.err = NEED_CODE; return; }                    // waiting for the two-step code\n"
          "    if ((!SYNC.checked || (Date.now() - SYNC.checkedAt > 600000 && jwtAal(SYNC.sess.at) !== 'aal2')) && !(await acctCheck())) return;\n    if (!SYNC.st.merged) await firstMerge();")
    d.rep("  } catch (e) { if (SYNC.on) SYNC.err = syncErrText(e); }\n  finally {\n    SYNC.busy = false;",
          "  } catch (e) { if (SYNC.on) { SYNC.err = syncErrText(e); if (e && (e.status === 401 || e.status === 403 || /Unauthorized/.test(e.code || ''))) SYNC.checked = false; } }\n  finally {\n    SYNC.busy = false;")
    d.rep("  SYNC.on = true; loadSt();", "  SYNC.on = true; loadSt(); SYNC.checked = false; SYNC.needCode = false; acctCache();")
    d.rep("  const c = document.getElementById('syncNowBtn'); if (c) c.disabled = SYNC.busy;", "  const c = document.getElementById('syncNowBtn'); if (c) c.disabled = SYNC.busy || SYNC.needCode;")
    d.rep("  if (SYNC.sess) syncStart();\n  render();\n}\n/* ----- what Settings shows ----- */", "  if (SYNC.sess) syncStart(); else askSync();\n  render();\n}\n/* ----- what Settings shows ----- */")
    d.cut('function accountGroup() {', 'const AUTHF = ', ACCOUNT)
    d.rep("  signin(f) { const email = f.elements.email.value.trim(), pw = f.elements.pw.value; AUTHF.email = email; authRun(f, async () => { await signIn(email, pw); closeSheet(); syncStart(); render(); toast('Signed in. Syncing your library.'); }); },",
          "  signin(f) {\n    const email = f.elements.email.value.trim(), pw = f.elements.pw.value; AUTHF.email = email;\n"
          "    authRun(f, async () => {\n      const s = await signIn(email, pw), fs = verifiedTotp(await sbFetch('/auth/v1/user', { headers: { Authorization: 'Bearer ' + s.at } }));\n"
          "      if (fs.length) { SYNC.pending = { sess: s, factor: fs[0].id }; codeSheet(true); return; }       // two-step sign-in: the code first, then the library\n"
          "      saveSess(s); closeSheet(); syncStart(); render(); toast('Signed in. Syncing your library.');\n    });\n  },")
    d.after("const ACT = {\n", ACTS)
    d.after("const FORM = {\n", FORMS)
    d.after("    emit() { emit(); }, docs, hook: null, hidden: null,", CLEAR_ALL)
    # a message already showing moves to the top when a sheet opens, so it never covers the sheet's buttons
    d.rep("  $('#sheetPanel').innerHTML = html; s.hidden = false;", "  $('#sheetPanel').innerHTML = html; s.hidden = false;\n  const tt = $('#toast'); if (!tt.hidden) tt.classList.add('up');")
    d.rep("window.__gymTapes = { MP4, VCUT, VID, SYNC,", "window.__gymTapes = { isPC: () => isPC(), MP4, VCUT, VID, SYNC,")
