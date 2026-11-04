# Puts the Royal Magic Academy (Map031) on the World Map, north of the capital beside the coast road: the castle icon,
# Quillhaven's village icon facing it, and a short spur road between the two off the coast road. The World Map has
# hand edits since map_world.py last ran, so this edits Map001 in place; running it again changes nothing.
#   python patch_academy_world.py            -> report
#   python patch_academy_world.py --apply    -> write Map001 (editor must be closed)
import json, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import nova_maplib as L
import kingdom as K
from map_world import CASTLE, VILLAGE, ROAD

ICON_X, CASTLE_Y, VILLAGE_Y = 60, 24, 27
SPUR = [(x, 26) for x in range(ICON_X, 65)]     # meets the coast road at (65, 26)
A2_BASE = 2816


def kind(v):
    return ('A2', (v - A2_BASE) // 48) if A2_BASE <= v < 4352 else None


def patch(m):
    w, h = m['width'], m['height']
    d = m['data']
    at = lambda layer, x, y: (layer * h + y) * w + x
    # the spur: rebuild the road layer's autotile shapes around it with the map builder
    b = L.MapBuilder(w, h, 1, '')
    for y in range(h):
        for x in range(w):
            b.auto[1][y][x] = kind(d[at(1, x, y)])
    for x, y in SPUR: b.auto[1][y][x] = ROAD
    new = b.tile_data()
    for y in range(h):
        for x in range(w):
            if b.auto[1][y][x] == ROAD: d[at(1, x, y)] = new[at(1, x, y)]
    # the icons, on the same layer as the capital's
    for blk, y0 in ((CASTLE, CASTLE_Y), (VILLAGE[:1], VILLAGE_Y)):        # a small village: one row of the icon
        for dy, row in enumerate(blk):
            for dx, t in enumerate(row): d[at(2, ICON_X + dx, y0 + dy)] = t
    # entering: the castle's gate row leads to the road in front of the Academy, the village to its south lane
    ev = [e for e in m['events'] if not (e and e['name'].startswith('Royal Magic Academy'))]
    cells = [((ICON_X + dx, CASTLE_Y + 1), 'academy_from_world_east') for dx in (0, 1)] + \
            [((ICON_X + dx, VILLAGE_Y), 'academy_from_world_south') for dx in (0, 1)]
    for (x, y), arrive in cells:
        ev.append({'id': len(ev), 'name': 'Royal Magic Academy - Quillhaven', 'note': '<minimap: exit>', 'x': x, 'y': y,
                   'pages': [L.exit_page(*K.ARRIVE[arrive])]})
    for i, e in enumerate(ev):
        if e: e['id'] = i
    m['events'] = ev
    return m


if __name__ == '__main__':
    path = L.DATA + 'Map001.json'
    m = patch(json.load(open(path, encoding='utf8')))
    print('spur %s, icons at x%d, %d entry events' % (SPUR, ICON_X, sum(1 for e in m['events'] if e and e['name'].startswith('Royal Magic'))))
    if '--apply' in sys.argv:
        L.write_map(K.WORLD, m)
        print('saved Map001')
