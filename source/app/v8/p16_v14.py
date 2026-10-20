# V14: the redesign. EarWorm lime for the main buttons, rounded headings, frosted glass on the controls (with a switch to
# turn it off), a floating tab bar on phones that shrinks while scrolling, a Now playing panel on the right on computers,
# quick picks and big covers on Home, gym mode and double-tap to like in the big player, swipes and drags, and motion.

EXPAND = ('<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" '
          'stroke-linejoin="round" aria-hidden="true"><path d="M14 4h6v6M10 20H4v-6M20 4l-7 7M4 20l7-7"/></svg>')

CSS = r'''
/* ===================== V14: the redesign ===================== */
:root{--accent:#C8F135;--accent-ink:#4A6A00;--on-accent:#0A0A0D;--round:ui-rounded,"SF Pro Rounded","Nunito",system-ui,-apple-system,sans-serif;
  --g-bg:rgba(255,255,255,.68);--g-line:rgba(10,10,20,.08);--g-hi:rgba(255,255,255,.8);--g-sh:0 10px 30px rgba(16,16,32,.14);--g-solid:#FFFFFF;--g-over:rgba(255,255,255,.55)}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){--accent-ink:#C8F135;--g-bg:rgba(34,34,42,.52);--g-line:rgba(255,255,255,.13);--g-hi:rgba(255,255,255,.18);--g-sh:0 12px 32px rgba(0,0,0,.55);--g-solid:#1C1C23;--g-over:rgba(255,255,255,.1)}}
:root[data-theme="dark"],:root[data-skin="dark"]{--accent-ink:#C8F135;--g-bg:rgba(34,34,42,.52);--g-line:rgba(255,255,255,.13);--g-hi:rgba(255,255,255,.18);--g-sh:0 12px 32px rgba(0,0,0,.55);--g-solid:#1C1C23;--g-over:rgba(255,255,255,.1)}
:root[data-skin="light"]{--accent-ink:#4A6A00;--g-bg:rgba(255,255,255,.62);--g-line:rgba(10,10,20,.1);--g-hi:rgba(255,255,255,.8);--g-sh:0 10px 30px rgba(16,16,32,.16);--g-solid:#FFFFFF;--g-over:rgba(255,255,255,.55)}
/* rounded headings, lime for the main buttons and anything switched on */
.page-t,.sec-h h3,.f-title,.empty h2,.sheet-panel h2,.np-head span{font-family:var(--round);font-weight:800}
.sec-h h3{font-size:21px;letter-spacing:-.02em}
.btn.primary{background:var(--accent);color:var(--on-accent)}
.switch[aria-checked="true"]{background:var(--accent)}
.switch[aria-checked="true"]::after{background:#FFFFFF}
.tog[aria-pressed="true"],.tile.cur .title,.rot.cur .title,.row.cur .title{color:var(--accent-ink)}
.stat-chip svg:first-child{color:var(--accent-ink)}
/* frosted glass on the controls: the tab bar, the player, the buttons over covers */
.nav,.player-in,.np-head .icon-btn{background:var(--g-bg);-webkit-backdrop-filter:blur(22px) saturate(180%);backdrop-filter:blur(22px) saturate(180%);border:1px solid var(--g-line);box-shadow:inset 0 1px 0 var(--g-hi),var(--g-sh)}
.f-top .icon-btn,.f-watch,.full .chips .chip{background:var(--g-over);-webkit-backdrop-filter:blur(20px) saturate(170%);backdrop-filter:blur(20px) saturate(170%);border:1px solid var(--g-line);box-shadow:inset 0 1px 0 var(--g-hi)}
body.no-glass .nav,body.no-glass .player-in,body.no-glass .np-head .icon-btn{background:var(--g-solid);-webkit-backdrop-filter:none;backdrop-filter:none}
body.no-glass .f-top .icon-btn,body.no-glass .f-watch,body.no-glass .full .chips .chip{background:var(--raise);-webkit-backdrop-filter:none;backdrop-filter:none}
/* Home: quick picks with the cover flush left, bigger covers in the rows that scroll sideways */
.rot{grid-template-columns:56px minmax(0,1fr);gap:10px;min-height:56px;padding:0 10px 0 0;border-radius:10px;overflow:hidden;box-shadow:none;background:var(--surface)}
.rot .cover{width:56px;height:56px;border-radius:0}
.rot .meta{font-size:12px}
.tile{width:140px}
.tile .cover{width:140px;height:140px;border-radius:14px;box-shadow:0 10px 24px var(--shadow)}
.row .cover{border-radius:10px}
.stat-chips{margin-top:12px}
/* Now playing panel bits: only on computers */
.np-head,.np-q{display:none}
.mini-prog{display:none}
/* the big player: colors from the cover, a big cover, a white play button */
.full{background:radial-gradient(120% 60% at 50% 0%,hsl(var(--hue,235) var(--ft-s) calc(var(--ft-l) + 8%) / .62),transparent 72%),linear-gradient(hsl(var(--hue,235) var(--ft-s) var(--ft-l) / var(--ft-a)),transparent 640px),var(--bg)}
.f-cover{position:relative;width:min(100%,342px,44vh)}
.f-cover .cover{border-radius:22px;box-shadow:0 30px 60px var(--shadow)}
.f-title{font-size:27px;letter-spacing:-.025em}
.full .ctl .big{width:76px;height:76px;box-shadow:0 14px 34px var(--shadow)}
.full .tog span{display:none}
.full .tog{width:48px}
.full .chips .chip{padding:9px 13px;font-size:12.5px}
/* gym mode: tap the cover and only the cover, the name and a thin line stay */
.gym-prog,.gym-hint{display:none}
.full.gym .f-top,.full.gym .f-head .heart,.full.gym .wave,.full.gym .ctl,.full.gym .vol,.full.gym .chips,.full.gym .f-side,.full.gym .f-watch{display:none!important}
.full.gym .full-in{min-height:calc(100vh - 60px);justify-content:center}
.full.gym .f-cover{width:min(100%,58vh,520px)}
.full.gym .gym-prog{display:block;height:3px;border-radius:2px;background:color-mix(in srgb,var(--ink) 18%,transparent);overflow:hidden}
.full.gym .gym-prog i{display:block;height:100%;width:0;background:var(--accent);border-radius:2px}
.full.gym .gym-hint{display:block;margin:6px 0 0;text-align:center;font-size:13px;font-weight:600;color:var(--muted);animation:hint 3s ease-in-out infinite}
@keyframes hint{0%,100%{opacity:.35}50%{opacity:.85}}
/* double-tap the cover to like */
.burst{position:absolute;left:50%;top:50%;width:120px;height:120px;margin:-60px 0 0 -60px;color:var(--like);pointer-events:none;animation:burst .8s cubic-bezier(.2,1.4,.4,1) forwards;filter:drop-shadow(0 10px 24px rgba(0,0,0,.4))}
.burst svg{width:120px;height:120px;fill:currentColor;stroke:none}
@keyframes burst{0%{transform:scale(.2);opacity:0}25%{transform:scale(1.1);opacity:1}60%{transform:scale(1);opacity:1}100%{transform:scale(1.25);opacity:0}}
/* motion: springy sheets, a heart that pops, lists that slide in */
.sheet-panel{animation-duration:.38s;animation-timing-function:cubic-bezier(.2,1.18,.35,1)}
.heart[aria-pressed="true"] svg{animation:heartPop .38s cubic-bezier(.2,1.7,.4,1)}
@keyframes heartPop{0%{transform:scale(1)}40%{transform:scale(1.35)}100%{transform:scale(1)}}
#view.enter .list > .row,#view.enter .tile,#view.enter .rot{animation:rowIn .42s cubic-bezier(.2,.9,.3,1) both}
#view.enter .list > .row:nth-child(2),#view.enter .tile:nth-child(2),#view.enter .rot:nth-child(2){animation-delay:.03s}
#view.enter .list > .row:nth-child(3),#view.enter .tile:nth-child(3),#view.enter .rot:nth-child(3){animation-delay:.06s}
#view.enter .list > .row:nth-child(4),#view.enter .tile:nth-child(4),#view.enter .rot:nth-child(4){animation-delay:.09s}
#view.enter .list > .row:nth-child(n+5),#view.enter .tile:nth-child(n+5),#view.enter .rot:nth-child(n+5){animation-delay:.12s}
@keyframes rowIn{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:none}}
::view-transition-group(np-cover){animation-duration:.42s;animation-timing-function:cubic-bezier(.2,.9,.25,1)}
.vt-on .full{animation:none}
@media (prefers-reduced-motion: reduce){
  #view.enter .list > .row,#view.enter .tile,#view.enter .rot,.heart[aria-pressed="true"] svg,.burst,.full.gym .gym-hint{animation:none}
  .nav,.player{transition:none!important}
}
/* ---------- phones: a floating tab bar and mini player ---------- */
@media (max-width: 899.98px){
  .page-t{font-size:32px;letter-spacing:-.025em}
  .app{padding-bottom:calc(60px + var(--player-h,0px) + var(--nav-h,66px) + env(safe-area-inset-bottom,0px))}
  .nav{left:50%;right:auto;bottom:calc(12px + env(safe-area-inset-bottom,0px));transform:translateX(-50%);width:min(520px,calc(100% - 24px));box-sizing:border-box;padding:6px;border-radius:34px;
    transition:left .34s cubic-bezier(.2,.9,.25,1.1),width .34s cubic-bezier(.2,.9,.25,1.1),transform .34s cubic-bezier(.2,.9,.25,1.1),padding .34s}
  .nav-in{max-width:none}
  .nav button{min-height:54px;border-radius:27px;font-size:10.5px;transition:background .2s,color .2s}
  .nav button[aria-selected="true"]{background:color-mix(in srgb,var(--ink) 11%,transparent);color:var(--accent-ink)}
  .nav .plus{width:36px;height:26px;border-radius:13px;background:var(--accent);color:var(--on-accent)}
  .player{left:50%;right:auto;transform:translateX(-50%);width:min(520px,calc(100% - 24px));padding:0;bottom:calc(var(--nav-h,66px) + 20px + env(safe-area-inset-bottom,0px));
    transition:left .34s cubic-bezier(.2,.9,.25,1.1),width .34s cubic-bezier(.2,.9,.25,1.1),transform .34s cubic-bezier(.2,.9,.25,1.1),bottom .34s cubic-bezier(.2,.9,.25,1.1)}
  .player-in{position:relative;max-width:none;border-radius:24px}
  .player.mini .player-in{border-radius:20px;padding:8px 8px 8px 8px;overflow:hidden}
  .player.mini .now .cover{width:46px;height:46px;border-radius:11px}
  .player.mini .now-open{grid-template-columns:46px minmax(0,1fr);gap:11px}
  .player.mini .mini-prog{display:block;position:absolute;left:16px;right:16px;bottom:0;height:3px;border-radius:2px;background:color-mix(in srgb,var(--ink) 14%,transparent);overflow:hidden}
  .mini-prog i{display:block;height:100%;width:0;background:var(--accent);border-radius:2px}
  .toast{bottom:calc(var(--player-h,0px) + var(--nav-h,66px) + 30px + env(safe-area-inset-bottom,0px))}
  /* scrolling down: the tab bar shrinks to one round button and the mini player slides in next to it */
  body.nav-min .nav{left:12px;transform:none;width:62px;padding:3px}
  body.nav-min .nav-in{grid-template-columns:minmax(0,1fr)}
  body.nav-min .nav button:not([aria-selected="true"]),body.nav-min .nav .dot{display:none}
  body.nav-min .nav button{font-size:0;gap:0;min-height:54px}
  body.nav-min .player{left:84px;transform:none;width:calc(100% - 96px);bottom:calc(12px + env(safe-area-inset-bottom,0px))}
  body.nav-min .player.mini .player-in{border-radius:31px}
  body.nav-min .player.mini .now .cover{border-radius:50%}
}
/* ---------- computers: a Now playing panel on the right ---------- */
@media (min-width: 900px){
  .page-t{letter-spacing:-.03em}
  .sec-h h3{font-size:24px}
  body.has-np{--np-w:340px}
  body.has-np .app{margin-right:var(--np-w)}
  .rot-grid{grid-template-columns:repeat(auto-fill,minmax(230px,1fr));gap:10px}
  .rot{min-height:64px;grid-template-columns:64px minmax(0,1fr)}
  .rot .cover{width:64px;height:64px}
  .tile{width:180px}
  .tile .cover{width:180px;height:180px;border-radius:16px}
  .player{left:auto;top:0;right:0;bottom:0;width:var(--np-w,340px)}
  .player-in{height:100%;box-sizing:border-box;display:flex;flex-direction:column;align-items:stretch;gap:12px;padding:22px 20px 24px;border-radius:0;border:0;border-left:1px solid var(--line);
    background:var(--sheet);box-shadow:none;-webkit-backdrop-filter:none;backdrop-filter:none;overflow-y:auto}
  .np-head{display:flex;align-items:center;justify-content:space-between}
  .np-head span{font-size:16px}
  .player .now{position:relative;padding:0}
  .player .now-open{display:flex;flex-direction:column;align-items:stretch;gap:14px;width:100%;text-align:left}
  .player #pCover{display:block;width:100%}
  .player #pCover .cover{width:100%;height:auto;aspect-ratio:1;border-radius:18px;box-shadow:0 24px 50px var(--shadow)}
  .player .now .title{font:800 22px/1.2 var(--round);letter-spacing:-.02em;padding-right:48px}
  .player .now .meta{padding-right:48px}
  .player .now-btns{position:absolute;right:0;bottom:4px}
  .player .chips{justify-content:flex-start}
  .player .wave{height:34px;margin:0}
  .player .times{display:flex;justify-content:space-between;margin-top:-6px}
  .player .ctl{justify-content:space-between;gap:4px}
  .player .ctl .big{width:58px;height:58px}
  .player .tog{width:44px}
  .player .tog span{display:none}
  .player .vol{width:100%}
  .np-q{display:block}
  .np-q .sec-h{margin:10px 0 2px}
  .np-q .sec-h h3{font-size:17px}
  .np-q .row-hit{min-height:56px;grid-template-columns:42px minmax(0,1fr);gap:11px}
  .np-q .row .cover{width:42px;height:42px;border-radius:8px}
  .np-q .tt .title{font-size:15px}
  .toast{left:calc(var(--side-w) + (100vw - var(--side-w) - var(--np-w,0px)) / 2)}
  /* the full-screen player: blurred cover colors behind, Up next in a glass panel */
  .full{background:radial-gradient(60% 70% at 25% 35%,hsl(var(--hue,235) var(--ft-s) calc(var(--ft-l) + 10%) / .55),transparent 70%),radial-gradient(50% 60% at 80% 75%,hsl(var(--hue,235) var(--ft-s) var(--ft-l) / .6),transparent 70%),var(--bg)}
  .f-cover{width:min(100%,520px,58vh)}
  .f-cover .cover{border-radius:26px}
  .f-title{font-size:40px}
  .full .f-side{overflow-x:hidden;padding:14px 16px;border-radius:20px;background:var(--g-over);-webkit-backdrop-filter:blur(24px) saturate(180%);backdrop-filter:blur(24px) saturate(180%);border:1px solid var(--g-line);box-shadow:inset 0 1px 0 var(--g-hi)}
  body.no-glass .full .f-side{background:var(--raise);-webkit-backdrop-filter:none;backdrop-filter:none}
  .full .f-side .list > .row{margin-inline:0}
  /* thin scrollbars that only show while scrolling */
  *{scrollbar-width:thin;scrollbar-color:color-mix(in srgb,var(--ink) 22%,transparent) transparent}
  ::-webkit-scrollbar{width:10px;height:10px}
  ::-webkit-scrollbar-track{background:transparent}
  ::-webkit-scrollbar-thumb{background-color:color-mix(in srgb,var(--ink) 22%,transparent);border-radius:10px;border:3px solid transparent;background-clip:padding-box}
  html:not(.scrolling) ::-webkit-scrollbar-thumb{background-color:transparent}
  html:not(.scrolling) .f-side:hover::-webkit-scrollbar-thumb,html:not(.scrolling) .player-in:hover::-webkit-scrollbar-thumb{background-color:color-mix(in srgb,var(--ink) 22%,transparent)}
}
'''

NP_HEAD = '<div class="np-head"><span>Now playing</span><button class="icon-btn sm" data-act="full-open" aria-label="Open the full-screen player">' + EXPAND + '</button></div>'
NP_TAIL = ('<div class="np-q"><div class="sec-h"><h3>Up next</h3><span class="f-note" id="pNextNote"></span></div><div class="list" id="pQueue" data-sortlist="queue"></div></div>'
           '<span class="mini-prog" aria-hidden="true"><i id="pProg"></i></span>')
GYM = '<div class="gym-prog" aria-hidden="true"><i id="gymProg"></i></div><p class="gym-hint" aria-hidden="true">Tap anywhere to show controls</p>\n    '

EXTRA = r'''/* ----- V14: the redesign's motion and gestures ----- */
const V14 = { touching: false, lastTouch: 0, y: 0, skip: 0 };
function v14Player(t) {
  document.body.classList.toggle('has-np', !!t && isPC());
  document.body.classList.toggle('no-glass', S.opt.glass === false);
}
/* on a computer, the Settings side list shows no section as open while searching */
function sideCur() {
  const q = !!(S.setQ && S.setQ.trim()), cur = S.setSec || 'quick';
  all('.set-side button[data-sec]', b => b.setAttribute('aria-current', String(!q && b.dataset.sec === cur)));
}
/* a tiny tap felt in the hand on swipes and likes (vibration where it exists, the iPhone switch tap where it does not) */
const buzz = (() => {
  let lab = null;
  return () => {
    try {
      if (navigator.vibrate) { navigator.vibrate(10); return; }
      if (!/iP(hone|ad|od)/.test(navigator.userAgent)) return;
      if (!lab) { lab = document.createElement('label'); lab.setAttribute('aria-hidden', 'true'); lab.style.cssText = 'position:fixed;left:-99px;top:0;width:1px;height:1px;overflow:hidden;opacity:0';
        const i = document.createElement('input'); i.type = 'checkbox'; i.setAttribute('switch', ''); i.tabIndex = -1; lab.appendChild(i); document.body.appendChild(lab); }
      lab.click();
    } catch (e) { /* no buzz */ }
  };
})();
/* opening and closing the big player: the mini player's cover grows into the big one */
const vtOK = () => !!document.startViewTransition && !calm && !isPC();
function vtSwap(update, open) {
  if (!vtOK()) return update();
  const big = () => $('#fCover .cover'), mini = () => $('#pCover .cover'), a = open ? mini() : big();
  if (a) a.style.viewTransitionName = 'np-cover';
  document.documentElement.classList.add('vt-on');
  let tr;
  try { tr = document.startViewTransition(() => { if (a) a.style.viewTransitionName = ''; update(); const b = open ? big() : mini(); if (b) b.style.viewTransitionName = 'np-cover'; }); }
  catch (e) { if (a) a.style.viewTransitionName = ''; document.documentElement.classList.remove('vt-on'); return update(); }
  tr.finished.catch(() => {}).then(() => { all('#pCover .cover, #fCover .cover', c => { c.style.viewTransitionName = ''; }); document.documentElement.classList.remove('vt-on'); });
}
/* phones: scrolling down with a finger shrinks the tab bar, scrolling up or reaching the top brings it back */
document.addEventListener('touchstart', () => { V14.touching = true; }, { passive: true });
document.addEventListener('touchend', () => { V14.touching = false; V14.lastTouch = Date.now(); }, { passive: true });
window.addEventListener('scroll', () => {
  const y = window.scrollY, dy = y - V14.y; V14.y = y;
  if (isPC() || S.full) return;
  if (y < 80) { document.body.classList.remove('nav-min'); return; }
  if (!(V14.touching || Date.now() - V14.lastTouch < 1200)) return;
  if (dy > 6) document.body.classList.add('nav-min'); else if (dy < -6) document.body.classList.remove('nav-min');
}, { passive: true });
document.addEventListener('click', e => { if (e.target.closest && e.target.closest('#nav')) document.body.classList.remove('nav-min'); }, true);
/* computers: scrollbars show while scrolling, then fade */
let scrollFade = 0;
document.addEventListener('scroll', () => { if (!isPC()) return; document.documentElement.classList.add('scrolling'); clearTimeout(scrollFade); scrollFade = setTimeout(() => document.documentElement.classList.remove('scrolling'), 900); }, { passive: true, capture: true });
/* the tap that ends a swipe or a drag is not also a tap */
document.addEventListener('click', e => { if (V14.skip && Date.now() - V14.skip < 400) { V14.skip = 0; e.preventDefault(); e.stopImmediatePropagation(); } }, true);
/* phones: swipe the mini player left for the next upload, right for the one before, up for the big player */
(() => {
  const g = { on: false, moved: false, dir: '', x: 0, y: 0, el: null };
  document.addEventListener('touchstart', e => {
    const hit = e.target.closest && e.target.closest('#player .now-open'); if (!hit || isPC() || e.touches.length > 1) return;
    g.on = true; g.moved = false; g.dir = ''; g.x = e.touches[0].clientX; g.y = e.touches[0].clientY; g.el = $('#player .player-in');
  }, { passive: true });
  document.addEventListener('touchmove', e => {
    if (!g.on) return; const dx = e.touches[0].clientX - g.x, dy = e.touches[0].clientY - g.y;
    if (!g.moved) { if (Math.abs(dx) < 8 && Math.abs(dy) < 8) return; g.dir = Math.abs(dx) > Math.abs(dy) ? 'x' : 'y'; g.moved = true; }
    g.el.style.transition = 'none';
    if (g.dir === 'x') { g.el.style.transform = 'translateX(' + Math.round(dx * 0.6) + 'px)'; g.el.style.opacity = String(1 - Math.min(0.5, Math.abs(dx) / 400)); }
    else if (dy < 0) g.el.style.transform = 'translateY(' + Math.round(Math.max(-40, dy * 0.4)) + 'px)';
  }, { passive: true });
  document.addEventListener('touchend', e => {
    if (!g.on) return; g.on = false; if (!g.moved) return;
    const t = e.changedTouches[0], dx = t.clientX - g.x, dy = t.clientY - g.y, el = g.el;
    V14.skip = Date.now();
    el.style.transition = 'transform .32s cubic-bezier(.2,.9,.25,1.2), opacity .32s'; el.style.transform = ''; el.style.opacity = '';
    setTimeout(() => { el.style.transition = ''; }, 340);
    if (g.dir === 'x' && Math.abs(dx) > 70) { buzz(); if (dx < 0) next(false); else prev(); }
    else if (g.dir === 'y' && dy < -50) openFull();
  }, { passive: true });
})();
/* the big player's cover: one tap for gym mode, two taps to like; in gym mode any tap brings the controls back */
function likeBurst() {
  const t = track(P.cur); if (!t || !store || !store.canWrite) return;
  if (!isLiked(t)) toggleLike(t.id);
  const c = $('#fCover'), h = document.createElement('span'); h.className = 'burst'; h.setAttribute('aria-hidden', 'true'); h.innerHTML = IC.heart;
  c.appendChild(h); setTimeout(() => h.remove(), 850); buzz();
}
(() => {
  let wait = 0, last = 0;
  document.addEventListener('click', e => {
    if (!S.full) return; const f = $('#full');
    if (f.classList.contains('gym')) { if (f.contains(e.target)) { e.preventDefault(); e.stopImmediatePropagation(); f.classList.remove('gym'); } return; }
    if (!(e.target.closest && e.target.closest('#fCover'))) return;
    const now = Date.now();
    if (now - last < 320) { clearTimeout(wait); last = 0; likeBurst(); return; }
    last = now; clearTimeout(wait); wait = setTimeout(() => { if (S.full) { f.classList.add('gym'); f.scrollTop = 0; } }, 320);
  }, true);
})();

'''


def apply(d):
    d.before('</style>', CSS)
    # the Now playing panel (computers), the mini player's progress line (phones), gym mode's line and hint
    d.after('<div class="player-in">', '\n    ' + NP_HEAD)
    d.rep('value="100" aria-label="Volume"></div>\n  </div>\n</section>\n\n<section class="full"',
          'value="100" aria-label="Volume"></div>\n    ' + NP_TAIL + '\n  </div>\n</section>\n\n<section class="full"')
    d.before('<div class="wave big" id="fWave"', GYM)
    # the Glass effects switch
    d.rep("hNewest: true, keepVideo: true, videoEnd: true, syncVideo: false };", "hNewest: true, keepVideo: true, videoEnd: true, syncVideo: false, glass: true };")
    d.rep("'hNewest', 'keepVideo', 'videoEnd', 'syncVideo'].forEach(k =>", "'hNewest', 'keepVideo', 'videoEnd', 'syncVideo', 'glass'].forEach(k =>")
    d.rep("{ k: 'look', name: 'Look', sub: () => 'Background' }", "{ k: 'look', name: 'Look', sub: () => 'Background, glass effects' }")
    d.rep("'Pick a color, or tap the last circle to use a photo of your own.', bgSwatches()));",
          "'Pick a color, or tap the last circle to use a photo of your own.', bgSwatches()) +\n"
          "    setRow('Glass effects', 'Frosted glass on the tab bar, the player and the buttons over covers. Turn it off if it feels slow or hard to read.', swBtn('glass', 'Glass effects')));")
    d.rep("'Join uploads': 'merge combine stitch',", "'Join uploads': 'merge combine stitch', 'Glass effects': 'glass blur frosted transparent liquid see through',")
    # the mini player is the phone's default once (people can still make it bigger); older tests keep the V13 default
    d.after("if (p.mini) S.mini = true; if (p.autoTrim === false) S.opt.autoTrim = false; } catch (e) { /* defaults */ }",
            "\ntry { if (!localStorage.getItem('hp.v14')) { localStorage.setItem('hp.v14', '1'); if (!S.mini) { S.mini = true; savePrefs(); } } } catch (e) { /* fine */ }")
    # Home: quick picks up top (Your rotation), big covers for what was played lately
    d.rep("const rot = S.home.rot.map(track).filter(Boolean), newest",
          "const rot = S.home.rot.map(track).filter(Boolean), lately = S.home.recent.map(track).filter(Boolean).slice(0, 10), newest")
    d.before("  const plTile = p => '<button class=\"tile\"",
             "  const recentTile = t => '<button class=\"tile' + (P.cur === t.id ? ' cur' : '') + '\" data-key=\"' + esc(t.id) + '\" style=\"--h:' + hueOf(t.id) + '\" data-act=\"play\" data-id=\"' + esc(t.id) + '\" data-ctx=\"recent\">' + trackCover(t, P.cur === t.id) +\n"
             "    '<span class=\"title\">' + esc(t.title) + '</span><span class=\"meta\">' + (S.plays[t.id] ? playsText(S.plays[t.id]) : fmt(playDur(t))) + '</span></button>';\n")
    d.rep("    (o.hPresets ? presetsHome() : '') +\n"
          "    (o.hRotation && rot.length ? secHead('Your rotation') + '<div class=\"rot-grid\" id=\"rotGrid\">' + rot.map(card).join('') + '</div>' : '') +",
          "    (o.hRotation && rot.length ? '<div class=\"rot-grid\" id=\"rotGrid\" role=\"group\" aria-label=\"Your rotation\">' + rot.map(card).join('') + '</div>' : '') +\n"
          "    (o.hPresets ? presetsHome() : '') +\n"
          "    (o.hRotation && lately.length > 2 ? secHead('Recently played') + '<div class=\"strip\" id=\"recentStrip\">' + lately.map(recentTile).join('') + '</div>' : '') +")
    # the player: the panel on computers, the mini player's line, the glass switch
    d.rep("  document.documentElement.style.setProperty('--player-h', t ? el.offsetHeight + 'px' : '0px');",
          "  document.documentElement.style.setProperty('--player-h', t && !isPC() ? el.offsetHeight + 'px' : '0px');")
    d.rep("  chips();\n  document.documentElement.style.setProperty('--nav-h'", "  chips(); v14Player(t);\n  document.documentElement.style.setProperty('--nav-h'")
    d.rep("  if (S.full && t) drawQueue();", "  if (t && (S.full || isPC())) drawQueue();")
    d.after("'Nothing else lined up.') + '</p>');",
            "\n  if (isPC()) { $('#pNextNote').textContent = $('#fNextNote').textContent; paint($('#pQueue'), $('#fQueue').innerHTML); }")
    d.rep("  $('#tCur').textContent = a; $('#tDur').textContent = b; $('#fCur').textContent = a; $('#fDur').textContent = b;",
          "  $('#tCur').textContent = a; $('#tDur').textContent = b; $('#fCur').textContent = a; $('#fDur').textContent = b;\n"
          "  const pp = $('#pProg'), gp = $('#gymProg'); if (pp) pp.style.width = (f * 100) + '%'; if (gp && S.full) gp.style.width = (f * 100) + '%';")
    # opening and closing the big player
    d.rep("  S.full = true; f.hidden = false; f.scrollTop = 0; updatePlayer();",
          "  S.full = true; vtSwap(() => { f.hidden = false; f.scrollTop = 0; f.classList.remove('gym'); updatePlayer(); }, true);")
    d.rep("  const f = $('#full'), done = () => { f.hidden = true; f.classList.remove('out'); };",
          "  const f = $('#full'), done = () => { f.hidden = true; f.classList.remove('out', 'gym'); };")
    d.rep("  if (now === true || calm) return done();\n  f.classList.add('out');",
          "  if (now === true || calm) return done();\n  if (vtOK()) return vtSwap(done, false);\n  f.classList.add('out');")
    # Settings search on a computer: no section stays highlighted
    d.rep("if (out) paint(out, setFindBody());", "if (out) paint(out, setFindBody()); sideCur();")
    d.before('/* ---------- loudness, for volume leveling ---------- */', EXTRA)
