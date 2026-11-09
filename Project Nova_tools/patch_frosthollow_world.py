# Puts Frosthollow (Map042, the chapter 5 border town) on the World Map: the snowy walled-town icon where the north road ends in
# the snowfield (26-27, 11-12), entered from the icon's lower row. The World Map has hand edits since map_world.py
# last ran, so this edits Map001 in place; running it again changes nothing.
#   python patch_frosthollow_world.py            -> report
#   python patch_frosthollow_world.py --apply    -> write Map001 (editor must be closed)
import json, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import nova_maplib as L
import kingdom as K
SNOW_TOWN = ((90, 91), (98, 99))            # World_B: walled town under snow, 2x2

ICON_X, ICON_Y = 26, 11
NAME = 'Frosthollow'


def patch(m):
    w, h = m['width'], m['height']
    d = m['data']
    at = lambda layer, x, y: (layer * h + y) * w + x
    for dy, row in enumerate(SNOW_TOWN):
        for dx, t in enumerate(row): d[at(2, ICON_X + dx, ICON_Y + dy)] = t
    ev = [e for e in m['events'] if not (e and e['name'].startswith(NAME))]
    for dx in (0, 1):
        ev.append({'id': len(ev), 'name': NAME, 'note': '<minimap: exit>', 'x': ICON_X + dx, 'y': ICON_Y + 1,
                   'pages': [L.exit_page(*K.ARRIVE['frosthollow_from_world'])]})
    for i, e in enumerate(ev):
        if e: e['id'] = i
    m['events'] = ev
    return m


if __name__ == '__main__':
    path = L.DATA + 'Map001.json'
    m = patch(json.load(open(path, encoding='utf8')))
    print('icon at (%d,%d), %d entry events' % (ICON_X, ICON_Y, sum(1 for e in m['events'] if e and e['name'] == NAME)))
    if '--apply' in sys.argv:
        L.write_map(K.WORLD, m)
        print('saved Map001')
