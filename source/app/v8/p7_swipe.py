# V8 part 3: swipes. Down closes the big player; a row swiped right plays next, swiped left deletes (or removes, in a playlist or Up next).
CSS = r'''
/* swipes */
.list{position:relative}
.list > .row{touch-action:pan-y}
.row.swiping{position:relative;z-index:2;background:var(--bg);border-radius:16px}
.swipe-under{position:absolute;left:0;right:0;z-index:1;display:flex;align-items:center;gap:8px;padding:0 20px;border-radius:16px;font-weight:700;font-size:15px;color:#fff;pointer-events:none;opacity:0}
.swipe-under.next{justify-content:flex-start;background:hsl(152 58% 36%)}
.swipe-under.del{justify-content:flex-end;background:var(--danger)}
'''

SWIPE = r'''/* ---------- swipes ---------- */
function removeFromPlaylist(plId, id) {
  const p = playlist(plId); if (!p) return;
  const old = (p.tracks || []).slice(), k = old.indexOf(id); if (k < 0) return;
  const before = k > 0 ? old[k - 1] : null, after = old[k + 1] || null;
  p.tracks = old.filter(x => x !== id); render();
  /* Undo puts back just this one, next to its old neighbours, so anything else changed meanwhile is kept */
  const undo = () => {
    const now = playlist(plId); if (!now) return;
    const list = (now.tracks || []).slice(); if (list.indexOf(id) >= 0) return;
    const b = before ? list.indexOf(before) : -1, a = after ? list.indexOf(after) : -1;
    list.splice(b >= 0 ? b + 1 : a >= 0 ? a : before ? list.length : 0, 0, id);
    now.tracks = list; render(); guard(() => setPlaylistTracks(plId, list));
  };
  guard(async () => { await setPlaylistTracks(p.id, p.tracks); toast('Removed from ' + p.name + '.', { action: 'Undo', ms: 6000, fn: undo }); });
}
(() => {
  let s = null;
  const rowOf = e => {
    const r = e.target.closest && e.target.closest('.list > .row'); if (!r || e.target.closest('[data-grip], .heart, .more, .check, input, a')) return null;
    const hit = r.querySelector('.row-hit'); return hit && (hit.dataset.act === 'play' || hit.dataset.act === 'q-jump') ? r : null;
  };
  const cleanup = x => {
    if (x.under) x.under.remove();
    x.r.classList.remove('swiping'); x.r.style.transition = ''; x.r.style.transform = '';
    dragOn = false; if (renderDue) { renderDue = false; render(); updatePlayer(); }
  };
  document.addEventListener('touchstart', e => {
    if (s) { const old = s; s = null; if (old.axis === 'x') cleanup(old); }      // a gesture whose end never arrived is dropped, never reused
    if (dragOn || e.touches.length !== 1) return;
    const r = rowOf(e); if (!r) return;
    const hit = r.querySelector('.row-hit'), t = e.touches[0], q = !!r.closest('#fQueue'), ctx = hit.dataset.ctx || '';
    s = { r, q, ctx, id: hit.dataset.id, tid: t.identifier, x0: t.clientX, y0: t.clientY, dx: 0, axis: null, w: r.offsetWidth || 300, under: null,
      right: !q, left: q || !!(store && store.canWrite) };
  }, { passive: true });
  document.addEventListener('touchmove', e => {
    if (!s) return;
    if (!s.r.isConnected) { const old = s; s = null; if (old.axis === 'x') cleanup(old); return; }       // the row was redrawn away under the finger
    const t = Array.from(e.touches).find(x => x.identifier === s.tid); if (!t) return;
    const dx = t.clientX - s.x0, dy = t.clientY - s.y0;
    if (!s.axis) {
      if (Math.abs(dx) < 10 && Math.abs(dy) < 10) return;
      if (Math.abs(dx) <= Math.abs(dy) * 1.3) { s = null; return; }        // up and down is scrolling; leave it alone
      s.axis = 'x'; dragOn = true; s.r.classList.add('swiping');
      const u = document.createElement('div'); u.className = 'swipe-under'; u.style.top = s.r.offsetTop + 'px'; u.style.height = s.r.offsetHeight + 'px';
      s.r.parentElement.insertBefore(u, s.r); s.under = u;
    }
    e.preventDefault();
    let x = dx; if (x > 0 && !s.right) x = 0; if (x < 0 && !s.left) x = 0;
    if (Math.abs(x) > s.w * 0.6) x = Math.sign(x) * (s.w * 0.6 + (Math.abs(x) - s.w * 0.6) * 0.25);
    s.dx = x; s.r.style.transform = 'translateX(' + x + 'px)';
    const del = x < 0, label = del ? (s.q || s.ctx.indexOf('pl:') === 0 ? 'Remove' : 'Delete') : 'Play next';
    s.under.className = 'swipe-under ' + (del ? 'del' : 'next'); if (s.under.textContent !== label) s.under.textContent = label;
    s.under.style.opacity = Math.min(1, Math.abs(x) / 70);
  }, { passive: false });
  const end = cancelled => {
    if (!s) return; const x = s; s = null;
    if (x.axis !== 'x') return;
    swipeBlock = Date.now() + 450; swipeRow = x.r;
    const go = !cancelled && Math.abs(x.dx) > Math.min(110, x.w * 0.3);
    if (go && x.dx < 0) {
      x.r.style.transition = 'transform .18s ease-in'; x.r.style.transform = 'translateX(-105%)';
      setTimeout(() => {
        cleanup(x);
        if (x.q) { const k = P.order.indexOf(x.id, P.pos + 1); if (k >= 0) { P.order.splice(k, 1); const j = P.queue.indexOf(x.id); if (j >= 0) P.queue.splice(j, 1); queueChanged(); } }
        else if (x.ctx.indexOf('pl:') === 0) removeFromPlaylist(x.ctx.slice(3), x.id);
        else if (track(x.id)) removeUploads([x.id]);
      }, 180);
      return;
    }
    x.r.style.transition = 'transform .2s ease'; x.r.style.transform = '';
    setTimeout(() => cleanup(x), 210);
    if (go && x.dx > 0) { tapAt = Date.now(); tapPlaying = !!track(P.cur) && !audio.paused && !P.countIn; playNext(x.id); }
  };
  document.addEventListener('touchend', () => end(false));
  document.addEventListener('touchcancel', () => end(true));
})();
/* the big player: pull it down from the top to close it */
(() => {
  const f = $('#full'); let s = null;
  f.addEventListener('touchstart', e => {
    s = null;
    if (e.touches.length !== 1 || f.scrollTop > 0 || e.target.closest('.wave, [data-grip], input, .row, .vol')) return;
    s = { y0: e.touches[0].clientY, t0: Date.now(), dy: 0, on: false };
  }, { passive: true });
  f.addEventListener('touchmove', e => {
    if (!s) return;
    const dy = e.touches[0].clientY - s.y0;
    if (dy > 0 && f.scrollTop <= 0) e.preventDefault();          // stop the page bounce from taking over before the pull starts
    if (!s.on) { if (dy < -8 || f.scrollTop > 0) { s = null; return; } if (dy < 8) return; s.on = true; }
    e.preventDefault();
    s.dy = Math.max(0, dy); f.style.transition = 'none'; f.style.transform = 'translateY(' + s.dy + 'px)';
  }, { passive: false });
  const end = () => {
    if (!s) return; const x = s; s = null; if (!x.on) return;
    const v = x.dy / Math.max(1, Date.now() - x.t0);
    f.style.transition = '';
    if (x.dy > 140 || (x.dy > 50 && v > 0.6)) { closeFull(); setTimeout(() => { f.style.transform = ''; }, 230); }
    else { f.style.transition = 'transform .2s ease'; f.style.transform = ''; setTimeout(() => { f.style.transition = ''; }, 220); }
  };
  f.addEventListener('touchend', end); f.addEventListener('touchcancel', end);
})();

'''

def apply(d):
    d.before('</style>', CSS)
    d.before("/* ---------- loudness, for volume leveling ---------- */", SWIPE)
