import sys, os, subprocess, importlib
here = os.path.dirname(os.path.abspath(__file__)); app = os.path.dirname(here); sys.path.insert(0, here)
from lib import Doc
d = Doc(open(os.path.join(app, 'v7-backup.html'), encoding='utf8').read())
for name in sys.argv[1:] or ['p5_home', 'p6_play', 'p7_swipe', 'p8_join', 'p9_ivol', 'p10_local', 'p11_video', 'p12_movfix', 'p13_sync', 'p14_v12', 'p15_v13', 'p16_v14', 'p17_v15']:
    importlib.import_module(name).apply(d); print('applied', name)
s = d.s
js = s[s.index('<script>') + 8 : s.rindex('</script>')]
open(os.path.join(app, '_check.js'), 'w', encoding='utf8').write(js)
r = subprocess.run(['node', '--check', os.path.join(app, '_check.js')], capture_output=True, text=True)
if r.returncode: print(r.stderr[:3000]); sys.exit(1)
open(os.path.join(app, 'gym-tapes.html'), 'w', encoding='utf8').write(s)
head = open(os.path.join(app, 'v6-index-head.txt'), encoding='utf8').read()
open(os.path.join(app, 'index.html'), 'w', encoding='utf8').write(head + s + '\n</body></html>')
print('ok', len(s), 'bytes,', js.count('\n'), 'script lines')
