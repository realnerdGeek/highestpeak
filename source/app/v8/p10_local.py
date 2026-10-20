# V9.1: on-device mode polish, used by the home screen app (and harmless in the Claude version):
# storage shown from the phone, saving files through the share sheet, no "not connected" notice in the home screen app.
def apply(d):
    d.rep("    async usage() { return null; }",
          "    async usage() { try { const e = navigator.storage && navigator.storage.estimate ? await navigator.storage.estimate() : null; return e && e.quota ? { bytes: e.usage || 0, maxBytes: e.quota } : null; } catch (e) { return null; } }")
    # a file goes out through the share sheet where there is one (Save to Files on iPhone), a download otherwise
    d.before("async function exportTrack(id) {",
             "const canShareFile = f => { try { return !!(navigator.share && navigator.canShare && navigator.canShare({ files: [f] })); } catch (e) { return false; } };\n"
             "function downloadBlob(blob, name, keep) { const a = document.createElement('a'); a.href = URL.createObjectURL(blob); a.download = name; document.body.appendChild(a); a.click(); a.remove(); setTimeout(() => URL.revokeObjectURL(a.href), keep || 5000); }\n")
    d.rep("    else { const a = document.createElement('a'); a.href = URL.createObjectURL(blob); a.download = name + '.m4a'; document.body.appendChild(a); a.click(); a.remove(); setTimeout(() => URL.revokeObjectURL(a.href), 5000); }",
          "    else {\n"
          "      const file = new File([blob], name + '.m4a', { type: 'audio/mp4' });\n"
          "      if (canShareFile(file)) { try { await navigator.share({ files: [file], title: name }); return; } catch (x) { if (x && x.name === 'AbortError') return; } }\n"
          "      downloadBlob(blob, name + '.m4a');\n"
          "    }")
    # a backup takes a few seconds to pack, longer than an iPhone keeps a tap valid for the share sheet, so it is a second tap
    d.rep("    else { const a = document.createElement('a'); a.href = URL.createObjectURL(blob); a.download = name; document.body.appendChild(a); a.click(); a.remove(); setTimeout(() => URL.revokeObjectURL(a.href), 300000); }",
          "    else {\n"
          "      const file = new File([blob], name, { type: 'application/zip' });\n"
          "      if (canShareFile(file)) { BK.file = file; bkSay('Backup ready: ' + countText(kept.length) + ', ' + fmtBytes(blob.size) + '. Tap Save backup file.'); return; }\n"
          "      downloadBlob(blob, name, 300000);\n"
          "    }")
    d.rep("data-act=\"backup\"' + (S.tracks.length && !BK.busy ? '' : ' disabled') + '>Back up library</button></div>' +",
          "data-act=\"backup\"' + (S.tracks.length && !BK.busy ? '' : ' disabled') + '>Back up library</button>' + (BK.file ? '<button class=\"btn sm primary\" id=\"backupSave\" data-act=\"backup-save\">Save backup file</button>' : '') + '</div>' +")
    d.after("const ACT = {\n",
            "  'backup-save'() {\n"
            "    const f = BK.file; if (!f) return;\n"
            "    const done = () => { BK.file = null; bkSay('Backup saved: ' + fmtBytes(f.size) + '.'); render(); };\n"
            "    if (canShareFile(f)) navigator.share({ files: [f], title: f.name }).then(done).catch(e => { if (!e || e.name !== 'AbortError') { downloadBlob(f, f.name, 300000); done(); } });\n"
            "    else { downloadBlob(f, f.name, 300000); done(); }\n"
            "  },\n")
    # the home screen app keeps its library on the phone on purpose, so there is nothing to warn about
    d.rep("    note(store.persistent ? 'Not connected to your saved library right now. What you upload here stays on this device only.' : 'This browser is not letting the page save anything. What you upload will be gone when you close it.');",
          "    if (window.HP_STANDALONE) {\n"
          "      if (!store.persistent) note('This phone is not letting the app save anything right now. What you upload will be gone when you close it.');\n"
          "      try { if (navigator.storage && navigator.storage.persist) navigator.storage.persist().catch(() => {}); } catch (e) { /* fine */ }      // ask the phone to keep the library even when space runs low\n"
          "    } else note(store.persistent ? 'Not connected to your saved library right now. What you upload here stays on this device only.' : 'This browser is not letting the page save anything. What you upload will be gone when you close it.');")
