# Villa Bloodrose (Map048): the road off the bottom edge now leads back into Mistveil (MAP067), the misty wood the
# party comes through from Lilydale. Adds the edge exits only (Map048 has hand edits; nothing else is touched).
#   python3 patch_villa_south_exit.py          -> report
#   python3 patch_villa_south_exit.py --save   -> write Map048 (editor must be closed)
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import nova_maplib as L
import kingdom as K

m = json.load(open(L.DATA + 'Map%03d.json' % K.VILLA_BLOODROSE, encoding='utf8'))
H = m['height']
events = m['events']
have = {(e['x'], e['y']) for e in events if e}
tx, ty = K.ARRIVE['mistveil_from_bloodrose'][1:3]
added = 0
for x in (20, 21, 22):                                   # the road off the bottom edge
    if (x, H - 1) in have: continue
    events.append({'id': len(events), 'name': 'To Mistveil %d' % x, 'note': '<minimap: exit>',
                   'pages': [L.exit_page(K.MISTVEIL, tx + x - 21, ty, 2)], 'x': x, 'y': H - 1})
    added += 1
print('exits added:', added)
if '--save' in sys.argv and added:
    L.write_map(K.VILLA_BLOODROSE, m)
    print('saved Map%03d' % K.VILLA_BLOODROSE)
