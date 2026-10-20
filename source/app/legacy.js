// The older tests were written before V12 split Settings into pages and added the sync invite.
// For them, every Settings section shows on one page (a flag only tests set), and the invite counts as already seen.
const pw = require('./pw.js');
const init = () => { window.__HP_SETTINGS_ALL = true; try { localStorage.setItem('hp.syncAsked', '1'); } catch (e) { /* about:blank */ } };
const launch = pw.chromium.launch.bind(pw.chromium);
pw.chromium.launch = async (...a) => {
  const b = await launch(...a), nc = b.newContext.bind(b), np = b.newPage.bind(b);
  b.newContext = async (...o) => { const c = await nc(...o); await c.addInitScript(init); return c; };
  b.newPage = async (...o) => { const p = await np(...o); await p.addInitScript(init); return p; };
  return b;
};
