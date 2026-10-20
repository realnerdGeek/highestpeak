// A stand-in for Supabase Realtime (protocol 1.0.0), through Playwright's WebSocket routing: private channels with the
// same rule as sql/v15.sql (mock.rtAuth), presence (join, track, leave) and broadcast to the others on the topic.
module.exports = function makeRealtime(mock) {
  const clients = new Set(), log = [];
  const send = (c, m) => { try { c.ws.send(JSON.stringify(m)); } catch (e) { /* closed */ } };
  const metaOf = c => Object.assign({ phx_ref: c.ref }, c.meta);
  const state = topic => { const out = {}; for (const c of clients) if (c.topic === topic && c.meta) out[c.key] = { metas: [metaOf(c)] }; return out; };
  function leave(c, gone) {
    if (c.topic && c.meta) { const diff = { joins: {}, leaves: { [c.key]: { metas: [metaOf(c)] } } }; for (const o of clients) if (o !== c && o.topic === c.topic) send(o, { topic: c.topic, event: 'presence_diff', payload: diff, ref: null, join_ref: o.jref }); }
    c.topic = null; c.meta = null; if (gone) clients.delete(c);
  }
  function attach(ctx) {
    return ctx.routeWebSocket(/\/realtime\/v1\/websocket/, ws => {
      const c = { ws, topic: null, key: null, meta: null, jref: null, ref: 'r' + Math.random().toString(36).slice(2, 10) };
      clients.add(c);
      ws.onMessage(raw => {
        let m; try { m = JSON.parse(String(raw)); } catch (e) { return; }
        log.push({ ev: m.event, topic: m.topic, sub: m.payload && m.payload.event, from: m.payload && m.payload.payload && m.payload.payload.from });
        if (m.topic === 'phoenix' && m.event === 'heartbeat') return send(c, { topic: 'phoenix', event: 'phx_reply', payload: { status: 'ok', response: {} }, ref: m.ref, join_ref: null });
        if (m.event === 'phx_join') {
          const topic = String(m.topic || '').replace(/^realtime:/, ''), cfg = (m.payload && m.payload.config) || {};
          const a = cfg.private ? mock.rtAuth(m.payload.access_token, topic) : { ok: false, reason: 'Unauthorized: public channels are off' };
          if (!a.ok) return send(c, { topic: m.topic, event: 'phx_reply', payload: { status: 'error', response: { reason: a.reason } }, ref: m.ref, join_ref: m.join_ref });
          c.topic = m.topic; c.jref = m.join_ref; c.key = (cfg.presence && cfg.presence.key) || c.ref; c.uid = a.uid;
          send(c, { topic: m.topic, event: 'phx_reply', payload: { status: 'ok', response: { postgres_changes: [] } }, ref: m.ref, join_ref: m.join_ref });
          send(c, { topic: m.topic, event: 'presence_state', payload: state(m.topic), ref: null, join_ref: m.join_ref });
          return;
        }
        if (!c.topic || m.topic !== c.topic) return;
        if (m.event === 'presence' && m.payload && m.payload.event === 'track') {
          c.meta = m.payload.payload || {};
          const diff = { joins: { [c.key]: { metas: [metaOf(c)] } }, leaves: {} };
          for (const o of clients) if (o.topic === c.topic) send(o, { topic: c.topic, event: 'presence_diff', payload: diff, ref: null, join_ref: o.jref });
          return send(c, { topic: m.topic, event: 'phx_reply', payload: { status: 'ok', response: {} }, ref: m.ref, join_ref: m.join_ref });
        }
        if (m.event === 'broadcast') { for (const o of clients) if (o !== c && o.topic === c.topic) send(o, { topic: c.topic, event: 'broadcast', payload: m.payload, ref: null, join_ref: o.jref }); return; }
        if (m.event === 'access_token') {
          const a = mock.rtAuth(m.payload && m.payload.access_token, c.topic.replace(/^realtime:/, ''));
          if (!a.ok) { const tp = c.topic; send(c, { topic: tp, event: 'system', payload: { status: 'error', message: 'Token has expired', extension: 'system' } }); send(c, { topic: tp, event: 'phx_close', payload: {} }); leave(c); }
          return;
        }
        if (m.event === 'phx_leave') leave(c);
      });
      ws.onClose(() => leave(c, true));
    });
  }
  return { attach, clients, log, online: topic => [...clients].filter(c => c.topic === topic && c.meta).map(c => c.meta.name) };
};
