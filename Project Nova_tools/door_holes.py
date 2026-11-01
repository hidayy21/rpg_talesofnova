# The dark doorway (Outside_B 69, or 71 for the round-topped doors) under every !Door1 event on the outdoor maps, so
# an opening door shows a hole into the house instead of the wall behind it. town_kit's door()/locked_door() put it
# on generated maps; this fixes the maps as they are now (editor edits included).
#   python door_holes.py          -> list what would change
#   python door_holes.py --save   -> write it (RPG Maker MV must be closed)
import sys, json
import nova_maplib as L
from town_kit import door_hole, DOOR_HOLE, DOOR_HOLE_ARCH

OUTSIDE = 2         # tileset id


def patch(mp):
    w, h, changed = mp['width'], mp['height'], []
    for e in mp['events']:
        if not e or not e['pages']: continue
        img = e['pages'][0]['image']
        if img['characterName'] != '!Door1': continue
        x, y, want = e['x'], e['y'], door_hole(img['characterIndex'])
        upper, top = (2 * h + y) * w + x, (3 * h + y) * w + x
        if mp['data'][upper] == want or mp['data'][top] in (DOOR_HOLE, DOOR_HOLE_ARCH): continue
        changed.append((e['name'], x, y, mp['data'][upper], want))
        mp['data'][upper] = want
    return changed


if __name__ == '__main__':
    infos = json.load(open(L.DATA + 'MapInfos.json', encoding='utf8'))
    for i in range(1, len(infos)):
        if not infos[i]: continue
        mp = json.load(open(L.DATA + 'Map%03d.json' % i, encoding='utf8'))
        if mp['tilesetId'] != OUTSIDE: continue
        changed = patch(mp)
        for name, x, y, old, new in changed:
            print('Map%03d %-28s (%d,%d) %d -> %d' % (i, name, x, y, old, new))
        if changed and '--save' in sys.argv: L.write_map(i, mp)
