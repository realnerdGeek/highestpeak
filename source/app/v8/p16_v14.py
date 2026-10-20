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
    apply_b(d)


# ---------------------------------------------------------------------------------------------------------------------
# V14 chunk B: the EarWorm name, the first-open guide with a sample beat, the Name it box after an upload, and not losing
# uploads (cloud space sitting in Recently deleted, whether this device protects the library, a monthly backup nudge).

CSS_B = r"""
/* the first-open guide */
.guide{position:fixed;inset:0;z-index:45;background:var(--bg);color:var(--ink);overflow:auto;display:flex;justify-content:center;padding:calc(18px + env(safe-area-inset-top,0px)) 20px calc(26px + env(safe-area-inset-bottom,0px));animation:viewIn .25s ease-out}
.guide::before{content:"";position:fixed;left:0;right:0;top:0;height:60vh;background:radial-gradient(90% 70% at 50% 35%,color-mix(in srgb,var(--accent) 16%,transparent),transparent 70%);pointer-events:none}
.g-in{position:relative;width:100%;max-width:440px;display:flex;flex-direction:column;gap:14px;min-height:100%}
.g-top{display:flex;align-items:center;justify-content:space-between}
.g-dots{display:flex;gap:6px}.g-dots i{width:6px;height:6px;border-radius:3px;background:color-mix(in srgb,var(--ink) 25%,transparent)}.g-dots i.on{width:26px;background:var(--accent)}
.g-phone{position:relative;align-self:center;width:220px;height:322px;border-radius:34px;border:2px solid color-mix(in srgb,var(--ink) 22%,transparent);background:var(--surface);overflow:hidden;box-shadow:0 30px 60px var(--shadow);margin-top:6px;flex:none}
.g-vid{position:absolute;left:10px;right:10px;top:10px;height:196px;border-radius:24px;background:radial-gradient(circle at 65% 30%,#F0446A 0,transparent 55%),linear-gradient(160deg,#2B1055,#120A22)}
.g-share{position:absolute;right:18px;top:116px;width:34px;height:34px;border-radius:17px;background:rgba(255,255,255,.2);display:grid;place-items:center;color:#fff}
.g-sheet{position:absolute;left:0;right:0;bottom:0;height:168px;border-radius:22px 22px 0 0;background:var(--raise);padding:10px 12px;box-sizing:border-box;display:flex;flex-direction:column;gap:6px;animation:gSheet 4s ease-in-out infinite}
.g-sheet .gh{align-self:center;width:30px;height:4px;border-radius:2px;background:color-mix(in srgb,var(--ink) 30%,transparent)}
.g-row{position:relative;height:38px;border-radius:10px;background:color-mix(in srgb,var(--ink) 6%,transparent);display:flex;align-items:center;gap:9px;padding:0 10px;font-size:13px;font-weight:600}
.g-row.hit{font-weight:700;animation:gRow 4s ease-in-out infinite}
.g-tap{position:absolute;width:30px;height:30px;border-radius:15px;border:3px solid var(--accent);animation:gTap 4s ease-out infinite}
.g-up{position:absolute;left:14px;right:14px;top:56px;height:150px;border-radius:20px;border:2px dashed color-mix(in srgb,var(--ink) 25%,transparent);display:grid;place-items:center}
.g-plus{width:58px;height:42px;border-radius:21px;background:var(--accent);color:var(--on-accent);display:grid;place-items:center}
.g-h{position:absolute;left:16px;top:18px;font:800 20px/1 var(--round)}
.g-thumbs{position:absolute;left:14px;right:14px;bottom:18px;display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:6px;animation:gThumbs 4s ease-in-out infinite}
.g-thumbs i{height:62px;border-radius:10px;background:linear-gradient(160deg,#2B1055,#F0446A)}.g-thumbs i:nth-child(2){background:linear-gradient(160deg,#0F3B2E,#C8F135)}.g-thumbs i:nth-child(3){background:linear-gradient(160deg,#0B1A3A,#4AA8FF)}
.g-mini{position:absolute;left:10px;right:10px;bottom:16px;height:56px;border-radius:18px;background:var(--raise);display:flex;align-items:center;gap:9px;padding:0 10px}
.g-mini b{width:38px;height:38px;border-radius:10px;background:radial-gradient(circle at 65% 30%,#F0446A 0,transparent 55%),linear-gradient(160deg,#2B1055,#120A22);flex:none}
.g-mini span{flex:1;font-size:13px;font-weight:700}
.g-loop{color:var(--accent-ink);animation:gSpin 2.4s linear infinite}
.g-wave{position:absolute;left:18px;right:18px;top:70px;height:120px;display:flex;align-items:center;gap:4px}
.g-wave i{flex:1;border-radius:3px;background:var(--accent);animation:eq .9s ease-in-out infinite alternate}
.g-wave i:nth-child(2n){animation-delay:.2s}.g-wave i:nth-child(3n){animation-delay:.45s}.g-wave i:nth-child(5n){animation-delay:.1s}
.g-t{margin:8px 0 0;font:800 28px/1.15 var(--round);letter-spacing:-.02em}
.g-p{margin:0;font-size:15px;line-height:1.45;color:var(--muted)}.g-p b{color:var(--ink)}
.g-works{display:flex;flex-wrap:wrap;gap:8px}.g-works span{display:inline-flex;align-items:center;gap:6px;height:30px;padding:0 11px;border-radius:15px;background:color-mix(in srgb,var(--ink) 7%,transparent);font-size:12px;font-weight:600}
.g-acts{margin-top:auto;display:flex;flex-direction:column;gap:10px;padding-top:12px}
.g-acts .btn{width:100%;min-height:54px;font-size:17px}
.g-acts .link-btn{align-self:center;padding:8px;font-size:14px;font-weight:600;color:var(--muted)}
@keyframes gSheet{0%,12%{transform:translateY(105%)}30%,82%{transform:translateY(0)}100%{transform:translateY(105%)}}
@keyframes gTap{0%,44%{transform:scale(.4);opacity:0}52%{opacity:.95}72%{transform:scale(1.5);opacity:0}100%{opacity:0}}
@keyframes gRow{0%,48%{background:color-mix(in srgb,var(--ink) 6%,transparent)}56%,78%{background:color-mix(in srgb,var(--accent) 24%,transparent)}100%{background:color-mix(in srgb,var(--ink) 6%,transparent)}}
@keyframes gThumbs{0%,15%{transform:translateY(130%)}35%,85%{transform:translateY(0)}100%{transform:translateY(130%)}}
@keyframes gSpin{to{transform:rotate(360deg)}}
@media (prefers-reduced-motion: reduce){.g-sheet,.g-tap,.g-row.hit,.g-thumbs,.g-loop,.g-wave i{animation:none}}
/* Name it, after an upload */
.nameit-head{display:flex;align-items:center;gap:14px}
.nameit-head .cover{width:64px;height:64px;border-radius:14px;flex:none}
.nameit-t{display:block;font:800 21px/1.2 var(--round)}
.nameit-ok{display:inline-flex;align-items:center;gap:5px;color:var(--accent-ink);font-weight:600}
.nameit-ok svg{width:14px;height:14px}
.nameit-l{display:block;margin:4px 0 6px;font-size:13px;font-weight:700;color:var(--muted)}
/* the backup nudge */
.nudge{margin-top:14px;border-radius:18px;padding:14px;background:color-mix(in srgb,var(--accent) 9%,transparent);border:1px solid color-mix(in srgb,var(--accent) 34%,transparent);display:flex;flex-direction:column;gap:10px}
.nudge-t{font-weight:700;font-size:15px}
.nudge .sub{margin:3px 0 0}
.nudge-b{display:flex;gap:8px}
.ok-line{color:var(--accent-ink)}
"""

GUIDE_JS = r"""/* ----- V14: the first-open guide, with a sample beat to play with ----- */
const GUIDE = { open: false, step: 0 };
const gIc = (d, fill) => '<svg width="16" height="16" viewBox="0 0 24 24" fill="' + (fill ? 'currentColor' : 'none') + '" stroke="' + (fill ? 'none' : 'currentColor') + '" stroke-width="2.3" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">' + d + '</svg>';
const G_STEPS = [
  { t: 'Save the video to your phone', p: 'In the app you are watching, tap <b>Share</b>, then <b>Save video</b> or <b>Download</b>. Screen recordings and clips already in your camera roll work too.',
    art: '<div class="g-phone" aria-hidden="true"><div class="g-vid"></div><span class="g-share">' + gIc('<path d="M12 3v12M7 8l5-5 5 5M5 14v5a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2v-5"/>') + '</span><div class="g-sheet"><span class="gh"></span>' +
      '<div class="g-row hit">' + gIc('<path d="M12 4v11M7 10l5 5 5-5M5 20h14"/>') + 'Save video<span class="g-tap" style="right:18px;top:4px"></span></div><div class="g-row">' + gIc('<rect x="8" y="8" width="12" height="12" rx="2"/><path d="M4 16V6a2 2 0 0 1 2-2h10"/>') + 'Copy link</div><div class="g-row">More</div></div></div>' },
  { t: 'Upload it to EarWorm', p: 'Tap <b>Upload</b> and pick the video from Photos or Files. EarWorm keeps the sound and cuts off the app logo and chime at the end.',
    art: '<div class="g-phone" aria-hidden="true"><span class="g-h">Upload</span><div class="g-up"><span class="g-plus">' + gIc('<path d="M12 5v14M5 12h14"/>') + '</span><span class="g-tap" style="left:calc(50% - 15px);top:calc(50% - 15px)"></span></div><div class="g-thumbs"><i></i><i></i><i></i></div></div>' },
  { t: 'Loop it your way', p: 'Play it on repeat, keep just the part you want, and make a playlist for each workout. Try it with a beat made for you.',
    art: '<div class="g-phone" aria-hidden="true"><span class="g-h">Now playing</span><div class="g-wave">' + '<i style="height:40%"></i><i style="height:70%"></i><i style="height:55%"></i><i style="height:90%"></i><i style="height:60%"></i><i style="height:80%"></i><i style="height:45%"></i><i style="height:75%"></i><i style="height:50%"></i><i style="height:85%"></i>' + '</div>' +
      '<div class="g-mini"><b></b><span>Sample beat</span><span class="g-loop">' + gIc('<path d="M17 2l3 3-3 3M4 11V9a4 4 0 0 1 4-4h12M7 22l-3-3 3-3M20 13v2a4 4 0 0 1-4 4H4"/>') + '</span></div></div>' }
];
const G_WORKS = '<div class="g-works"><span>' + gIc('<rect x="3" y="6" width="13" height="12" rx="2"/><path d="m16 10 5-3v10l-5-3z"/>') + 'Saved videos</span><span>' + gIc('<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="4"/>') + 'Screen recordings</span>' +
  '<span>' + gIc('<rect x="9" y="3" width="6" height="11" rx="3"/><path d="M5 11a7 7 0 0 0 14 0M12 18v3"/>') + 'Voice memos</span><span>' + gIc('<path d="M9 18V5l11-2v13"/><circle cx="6" cy="18" r="3"/><circle cx="17" cy="16" r="3"/>') + 'MP3, WAV, M4A</span></div>';
const guided = () => { try { return localStorage.getItem('hp.guided') === '1'; } catch (e) { return true; } };
function maybeGuide() {
  if (GUIDE.open || window.__HP_QUIET || !S.ready || S.tracks.length || guided() || !store || !store.canWrite || SYNC.sess || sheetOpen() || S.full || VID.open) return;
  let asked = true; try { asked = localStorage.getItem('hp.syncAsked') === '1'; } catch (e) { /* asked */ }
  if (asked) openGuide();
}
function openGuide() { GUIDE.open = true; GUIDE.step = 0; drawGuide(); }
function drawGuide() {
  let g = $('#guide');
  if (!g) { g = document.createElement('section'); g.id = 'guide'; g.className = 'guide'; g.setAttribute('role', 'dialog'); g.setAttribute('aria-label', 'Getting started'); document.body.appendChild(g); }
  const n = GUIDE.step, st = G_STEPS[n], last = n === G_STEPS.length - 1;
  g.innerHTML = '<div class="g-in"><div class="g-top"><div class="g-dots" aria-label="Step ' + (n + 1) + ' of ' + G_STEPS.length + '">' + G_STEPS.map((x, i) => '<i class="' + (i === n ? 'on' : '') + '"></i>').join('') + '</div>' +
    '<button class="btn sm" id="guideSkip" data-act="guide-skip">Skip</button></div>' + st.art + '<h2 class="g-t" id="guideTitle">' + st.t + '</h2><p class="g-p">' + st.p + '</p>' + (n === 0 ? G_WORKS : '') +
    '<div class="g-acts">' + (last ? '<button class="btn primary" id="guideSample" data-act="guide-sample">Try the sample beat</button><button class="link-btn" id="guideUpload" data-act="guide-upload">Upload a video</button>'
      : '<button class="btn primary" id="guideNext" data-act="guide-next">Next</button>' + (n === 0 ? '<button class="link-btn" id="guideHave" data-act="guide-upload">I already have videos, take me to Upload</button>' : '')) + '</div></div>';
  g.hidden = false;
}
function closeGuide() { GUIDE.open = false; try { localStorage.setItem('hp.guided', '1'); } catch (e) { /* fine */ } const g = $('#guide'); if (g) g.remove(); }
/* a short beat made right here, so a first upload is one tap away (and nobody else's sound) */
async function sampleBeat() {
  const OAC = window.OfflineAudioContext || window.webkitOfflineAudioContext, sr = 44100, bpm = 140, beats = 16, spb = 60 / bpm, len = Math.ceil(sr * beats * spb);
  const ctx = new OAC(2, len, sr), out = ctx.destination;
  const noise = ctx.createBuffer(1, sr, sr), nd = noise.getChannelData(0); for (let i = 0; i < nd.length; i++) nd[i] = Math.random() * 2 - 1;
  const env = (g, t, a, peak, d) => { g.gain.setValueAtTime(0.0001, t); g.gain.exponentialRampToValueAtTime(peak, t + a); g.gain.exponentialRampToValueAtTime(0.0001, t + d); };
  const hit = (t, type, f, q, peak, d) => { const s = ctx.createBufferSource(), fl = ctx.createBiquadFilter(), g = ctx.createGain(); s.buffer = noise; fl.type = type; fl.frequency.value = f; if (q) fl.Q.value = q; env(g, t, 0.002, peak, d); s.connect(fl); fl.connect(g); g.connect(out); s.start(t); s.stop(t + d + 0.02); };
  const bass = [55, 55, 65.41, 49];
  for (let b = 0; b < beats; b++) {
    const t = b * spb;
    const o = ctx.createOscillator(), g = ctx.createGain(); o.frequency.setValueAtTime(150, t); o.frequency.exponentialRampToValueAtTime(42, t + 0.16); env(g, t, 0.004, 0.9, 0.34); o.connect(g); g.connect(out); o.start(t); o.stop(t + 0.36);
    hit(t + spb / 2, 'highpass', 7000, 0, 0.22, 0.05);
    if (b % 4 === 1 || b % 4 === 3) hit(t, 'bandpass', 1800, 0.8, 0.45, 0.16);
    if (b % 2 === 0) { const bo = ctx.createOscillator(), lp = ctx.createBiquadFilter(), bg = ctx.createGain(); bo.type = 'sawtooth'; bo.frequency.value = bass[(b / 2) % 4]; lp.type = 'lowpass'; lp.frequency.value = 420; env(bg, t, 0.02, 0.3, spb * 1.8); bo.connect(lp); lp.connect(bg); bg.connect(out); bo.start(t); bo.stop(t + spb * 2); }
  }
  const buf = await ctx.startRendering(), ch = buf.numberOfChannels, n = buf.length, v = new DataView(new ArrayBuffer(44 + n * ch * 2));
  const w = (o, str) => { for (let i = 0; i < str.length; i++) v.setUint8(o + i, str.charCodeAt(i)); };
  w(0, 'RIFF'); v.setUint32(4, 36 + n * ch * 2, true); w(8, 'WAVE'); w(12, 'fmt '); v.setUint32(16, 16, true); v.setUint16(20, 1, true); v.setUint16(22, ch, true); v.setUint32(24, sr, true);
  v.setUint32(28, sr * ch * 2, true); v.setUint16(32, ch * 2, true); v.setUint16(34, 16, true); w(36, 'data'); v.setUint32(40, n * ch * 2, true);
  const d = []; for (let c = 0; c < ch; c++) d.push(buf.getChannelData(c));
  let o = 44; for (let i = 0; i < n; i++) for (let c = 0; c < ch; c++) { const x = Math.max(-1, Math.min(1, d[c][i] * 0.8)); v.setInt16(o, x < 0 ? x * 0x8000 : x * 0x7fff, true); o += 2; }
  return new File([v.buffer], 'Sample beat.wav', { type: 'audio/wav' });
}
async function addSample() {
  try { V14.sample = true; queueFiles([await sampleBeat()]); }
  catch (e) { V14.sample = false; toast('The sample beat could not be made here. Upload a video instead.'); go('upload'); }
}
/* ----- V14: Name it, right after an upload ----- */
function nameItSheet(id, cut) {
  const t = track(id); if (!t || sheetOpen() || GUIDE.open) return;
  const keep = /^Upload \d+$/.test(t.title) ? '' : t.title;
  sheet('<div class="nameit-head">' + trackCover(t) + '<span class="grow"><span class="nameit-t">Upload added</span><span class="sub nameit-ok">' + IC.tick + fmt(t.dur) + (cut ? ', end clip removed' : '') + '</span></span></div>' +
    '<form data-form="rename"><label class="nameit-l" for="renameInput">Name it</label><input type="text" id="renameInput" name="tname" maxlength="80" value="' + esc(keep) + '" placeholder="Like Phonk leg day" data-focus autocomplete="off">' +
    '<p class="sub">Skip and it stays ' + esc(t.title) + '. You can rename it any time.</p>' +
    '<div class="pair"><button type="button" class="btn" id="nameSkip" data-act="sheet-close">Skip</button><button type="submit" class="btn primary" id="nameSave">Save</button></div></form>', { id, kind: 'nameit' });
}
function afterImports(added, newId, cut) {
  if (V14.sample) { V14.sample = false; if (added === 1 && newId) { go('home'); ACT.play({ id: newId, ctx: 'all' }); } return; }
  if (added === 1 && newId && S.opt.nameIt && !window.__HP_QUIET) setTimeout(() => nameItSheet(newId, cut), 260);
}
/* ----- V14: not losing uploads ----- */
function trashCloudBytes() {
  if (!SYNC.st || !S.trash.length) return 0;
  const ids = new Set(); S.trash.forEach(t => blobRefs('tracks', t, true).forEach(x => ids.add(x)));
  let b = 0; SYNC.st.up.forEach(x => { if (ids.has(x)) b += store.blobSize(x); }); return b;
}
function binFree() { const b = SYNC.on ? trashCloudBytes() : 0; return b ? '<p class="sub" id="binFree">Emptying it frees about ' + fmtBytes(b) + ' of cloud space.</p>' : ''; }
V14.persisted = null;
function checkPersist() {
  try { if (!navigator.storage || !navigator.storage.persisted) return; navigator.storage.persisted().then(v => { const was = V14.persisted; V14.persisted = !!v; if (was !== V14.persisted && S.tab === 'settings') render(); }).catch(() => {}); } catch (e) { /* unknown */ }
}
function protectRow() {
  if (V14.persisted == null) return '';
  return '<div class="set"><div class="grow"><div class="set-t">' + (V14.persisted ? 'Protected on this device' : 'Not protected yet') + '</div><p class="sub' + (V14.persisted ? ' ok-line' : '') + '" id="protectSub">' +
    (V14.persisted ? 'This device keeps your library even when space runs low.' : 'When space runs low, this device could clear the library. Back up, or sign in to keep a copy in the cloud.') + '</p></div>' +
    (V14.persisted ? '' : '<button class="btn sm" id="protectBtn" data-act="persist-ask">Protect</button>') + '</div>';
}
const lsNum = k => { try { return +localStorage.getItem(k) || 0; } catch (e) { return 0; } };
const lsSet = (k, v) => { try { localStorage.setItem(k, String(v)); } catch (e) { /* not kept */ } };
function markBackup() { lsSet('hp.lastBackup', Date.now()); }
function backupNudge() {
  if (SYNC.sess || !store || !store.canWrite || !S.tracks.length) return '';
  const now = Date.now(), last = lsNum('hp.lastBackup'), since = lsNum('hp.since') || now, base = Math.max(last, since);
  if (now - base < 30 * 86400000 || now < lsNum('hp.nudgeLater')) return '';
  const days = Math.floor((now - (last || since)) / 86400000);
  return '<div class="nudge" id="nudge"><div><div class="nudge-t">Back up your library?</div><p class="sub">' + (last ? 'Your last backup was ' + days + ' days ago.' : 'You have not made a backup yet.') +
    ' You are not signed in, so this device has the only copy.</p></div><div class="nudge-b"><button class="btn sm primary" id="nudgeGo" data-act="nudge-backup">Back up now</button><button class="btn sm" id="nudgeLater" data-act="nudge-later">Not now</button></div></div>';
}

"""

ACTS_B = r"""  'guide-next'() { GUIDE.step = Math.min(G_STEPS.length - 1, GUIDE.step + 1); drawGuide(); },
  'guide-skip'() { closeGuide(); },
  'guide-upload'() { closeGuide(); go('upload'); },
  'guide-sample'() { closeGuide(); addSample(); },
  'guide-show'() { openGuide(); },
  'nudge-backup'() { ACT.backup(); },
  'nudge-later'() { lsSet('hp.nudgeLater', Date.now() + 14 * 86400000); render(); },
  'persist-ask'() { try { navigator.storage.persist().then(v => { V14.persisted = !!v; render(); if (!v) toast('This device did not agree yet. Adding EarWorm to your home screen helps.'); }).catch(() => {}); } catch (e) { /* no */ } },
"""


def apply_b(d):
    d.before('</style>', CSS_B)
    # the name: EarWorm, one word, two colors kept
    d.rep('Ear Worm', 'EarWorm', 13)
    d.rep('Ear <b>Worm</b>', 'Ear<b>Worm</b>', 2)
    d.rep('If you set it up before the name changed, it is listed as HighestPeak.', 'If you set it up before the name changed, it may be listed as HighestPeak or Ear Worm.')
    # options: Name new uploads
    d.rep("syncVideo: false, glass: true };", "syncVideo: false, glass: true, nameIt: true };")
    d.rep("'syncVideo', 'glass'].forEach(k =>", "'syncVideo', 'glass', 'nameIt'].forEach(k =>")
    d.rep("      setRow('Join uploads', 'Adds Join to the options of each upload, to stitch two or more into one that loops as a whole.', swBtn('join', 'Join uploads')));",
          "      setRow('Join uploads', 'Adds Join to the options of each upload, to stitch two or more into one that loops as a whole.', swBtn('join', 'Join uploads')) +\n"
          "      setRow('Name new uploads', 'Right after an upload, ask what to call it.', swBtn('nameIt', 'Name new uploads')) +\n"
          "      setRow('First-open guide', 'How to get videos into EarWorm, step by step.', '<button class=\"btn sm\" id=\"guideShow\" data-act=\"guide-show\">Show</button>'));")
    d.rep("'Join uploads': 'merge combine stitch',", "'Join uploads': 'merge combine stitch', 'Name new uploads': 'rename title name ask', 'First-open guide': 'help tutorial how start guide intro',")
    d.rep("setRow('Your rotation', 'What you played last and what you play most, in one small grid.'", "setRow('Your rotation', 'Quick picks of what you played last and play most, and Recently played with big covers.'")
    # Name it: remember the new upload, then ask once the import is done
    d.rep("  const id = store.id(), title = autoName(job.file.name);", "  const id = store.id(), title = autoName(job.file.name); job.newId = id;")
    d.rep("  let added = 0, trimmedCount = 0, asked = 0; VID.missed = 0; VID.full = false;", "  let added = 0, trimmedCount = 0, asked = 0, lastNew = null; VID.missed = 0; VID.full = false;")
    d.rep("else { added++; if (r === 'trimmed') trimmedCount++; } }", "else { added++; lastNew = job.newId || null; if (r === 'trimmed') trimmedCount++; } }")
    d.rep("  if (added) toast((added === 1 ? 'Upload added.' : added + ' uploads added.') + note + vnote);",
          "  if (added) { toast((added === 1 ? 'Upload added.' : added + ' uploads added.') + note + vnote); afterImports(added, lastNew, trimmedCount > 0); }")
    # the guide comes after the sync invite, on an empty library
    d.rep("function render() {\n", "function render() {\n  if (!GUIDE.open && !S.tracks.length) setTimeout(maybeGuide, 0);\n")
    d.rep("function closeSheet() {\n", "function closeSheet() {\n  setTimeout(maybeGuide, 400);\n")
    # cloud space sitting in Recently deleted
    d.rep("function cloudText() { if (!SYNC.st) return ''; let b = 0; SYNC.st.up.forEach(id => { b += store.blobSize(id); }); return 'About ' + fmtBytes(b) + ' of 1 GB cloud space used'; }",
          "function cloudText() { if (!SYNC.st) return ''; let b = 0; SYNC.st.up.forEach(id => { b += store.blobSize(id); }); const tb = trashCloudBytes(); return 'About ' + fmtBytes(b) + ' of 1 GB cloud space used' + (tb ? ', ' + fmtBytes(tb) + ' of it in Recently deleted' : ''); }")
    d.rep("(SYNC.on ? ' on every device' : '') + '.</p>' +\n    (list.length ?", "(SYNC.on ? ' on every device' : '') + '.</p>' + binFree() +\n    (list.length ?")
    # whether this device protects the library
    d.rep("'</p></div></div>' + binRow()) +", "'</p></div></div>' + protectRow() + binRow()) +")
    d.rep("{ k: 'library', name: 'Library and storage', sub: () => 'Space used, recently deleted, clear library' }",
          "{ k: 'library', name: 'Library and storage', sub: () => (V14.persisted === true ? 'Protected on this device, space used' : V14.persisted === false ? 'Not protected yet, space used' : 'Space used') + ', recently deleted, clear library' }")
    # the backup nudge (people who are not signed in), and remembering when a backup was made
    d.rep("bkSay('Backup saved: ' + what + '.' + left);", "markBackup(); bkSay('Backup saved: ' + what + '.' + left);")
    d.rep("if (canShareFile(file)) { BK.file = file; bkSay(", "if (canShareFile(file)) { markBackup(); BK.file = file; bkSay(")
    d.rep("return '<h2 class=\"sec-t\">' + cur.name + '</h2>'", "return (cur.k === 'quick' ? backupNudge() : '') + '<h2 class=\"sec-t\">' + cur.name + '</h2>'")
    d.rep("  return group('Quick settings', quickBody()) +", "  return backupNudge() + group('Quick settings', quickBody()) +")
    d.after("  const first = !S.ready; S.ready = true;", "\n  checkPersist(); if (S.tracks.length && !lsNum('hp.since')) lsSet('hp.since', Date.now());")
    d.before('/* ---------- loudness, for volume leveling ---------- */', GUIDE_JS)
    d.after("const ACT = {\n", ACTS_B)
    d.rep("window.__gymTapes = { isPC: () => isPC(),", "window.__gymTapes = { isPC: () => isPC(), cloudText, trashCloudBytes, toggleLike: id => toggleLike(id),")
