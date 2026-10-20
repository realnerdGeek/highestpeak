// The older tests were written before V12 split Settings into pages and added the sync invite.
// For them, every Settings section shows on one page (a flag only tests set), the invite counts as already seen, and the
// player keeps the V13 default size (V14 starts everyone on the mini player once), and there is no V14 first-open
// guide or Name it box in the way (__HP_QUIET).
const pw = require('./pw.js');
const init = () => { window.__HP_SETTINGS_ALL = true; window.__HP_QUIET = true; try { localStorage.setItem('hp.syncAsked', '1'); localStorage.setItem('hp.v14', '1'); } catch (e) { /* about:blank */ } };
const launch = pw.chromium.launch.bind(pw.chromium);
pw.chromium.launch = async (...a) => {
  const b = await launch(...a), nc = b.newContext.bind(b), np = b.newPage.bind(b);
  b.newContext = async (...o) => { const c = await nc(...o); await c.addInitScript(init); return c; };
  b.newPage = async (...o) => { const p = await np(...o); await p.addInitScript(init); return p; };
  return b;
};
