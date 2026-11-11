# Villa Bloodrose garden (Map048, hand-edited in Nova Tools - patch, never regenerate): the slab under the Bloodrose
# tree where the Rose Way comes out (map_villa_bloodrose_depths.py). Until the party pushes it up from below
# (switch 15) it is only a paving stone that rings hollow; afterwards it is a stair down into the dungeon.
# Adds one event, touches no tile.   python patch_villa_rose_way.py [--save]
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import nova_maplib as L
from nova_maplib import page, text
import kingdom as K

X, Y = 8, 28                      # on the paving just below the tree's trunk
STAIRS_DOWN = 220                 # Outside_B (the garden's own tileset): stone steps down into the dark

m = json.load(open(L.DATA + 'Map%03d.json' % K.VILLA_BLOODROSE, encoding='utf8'))
assert not any(e and (e['x'], e['y']) == (X, Y) for e in m['events'])
assert not any(e and e['name'] == 'Rose Slab' for e in m['events']), 'already patched'
opened = L.exit_page(*K.ARRIVE['villa_roseway_from_bloodrose'])
opened['image'] = L.tile_image(STAIRS_DOWN)
opened['conditions'].update(switch1Valid=True, switch1Id=K.SW_VILLA_ROSE_WAY)
ev = {'id': len(m['events']), 'name': 'Rose Slab', 'note': '', 'x': X, 'y': Y, 'pages': [
    page(None, priority=0, commands=text('One paving stone under the tree sits a little proud of the rest.',
                                         'It rings hollow underfoot - and will not shift from up here.')),
    opened]}
m['events'].append(ev)
print('Rose Slab -> event %d at (%d, %d)' % (ev['id'], X, Y))
if '--save' in sys.argv:
    L.write_map(K.VILLA_BLOODROSE, m); print('saved Map048')
