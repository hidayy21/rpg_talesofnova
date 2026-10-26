# Checks the Royal Kingdom of Nova maps before/after saving: transfers land on walkable tiles, doors have a
# walkable doorstep, no two events share a tile, every map's exits point to maps that exist.
import sys, json
sys.path.insert(0, 'D:/RPG Maker MV/Project Nova_tools')
import nova_maplib as L
from make_town_tiles import build as build_props

TILESETS = json.load(open(L.DATA + 'Tilesets.json', encoding='utf8'))
_, D_FLAGS = build_props(write=False)


def flags_for(ts_id):
    f = list(TILESETS[ts_id]['flags'])
    if ts_id == 2:
        for tid, fl in D_FLAGS.items(): f[tid] = fl
    return f


def passable(mapd, x, y, flags):
    w, h = mapd['width'], mapd['height']
    if not (0 <= x < w and 0 <= y < h): return False
    for L_ in (3, 2, 1, 0):
        tid = mapd['data'][(L_ * h + y) * w + x]
        if tid == 0: continue
        fl = flags[tid]
        if fl & 0x10: continue
        return (fl & 0x0f) != 0x0f
    return False


def check(maps):
    """maps: {map_id: map_dict}. Returns list of problems."""
    problems = []
    for mid, m in maps.items():
        flags = flags_for(m['tilesetId'])
        seen = {}
        for e in m['events'][1:]:
            if not e: continue
            key = (e['x'], e['y'])
            if key in seen: problems.append('map %d: events "%s" and "%s" share tile %s' % (mid, seen[key], e['name'], key))
            seen[key] = e['name']
            for pg in e['pages']:
                for c in pg['list']:
                    if c['code'] == 201:
                        _, tmap, tx, ty, _, _ = c['parameters']
                        if tmap not in maps:
                            problems.append('map %d "%s": transfer to map %d not in set' % (mid, e['name'], tmap)); continue
                        t = maps[tmap]
                        if not passable(t, tx, ty, flags_for(t['tilesetId'])):
                            problems.append('map %d "%s": lands on blocked tile (%d,%d) of map %d' % (mid, e['name'], tx, ty, tmap))
                        blocker = [x for x in t['events'][1:] if x and x['x'] == tx and x['y'] == ty and x['pages'][0]['priorityType'] == 1
                                   and x['pages'][0]['trigger'] != 1]
                        if blocker:
                            problems.append('map %d "%s": lands on event "%s" in map %d' % (mid, e['name'], blocker[0]['name'], tmap))
                img = pg['image']
                if img.get('characterName', '').startswith('!Door') and img['characterName'] != '!Door2':
                    if not passable(m, e['x'], e['y'] + 1, flags):
                        problems.append('map %d door "%s" at (%d,%d): doorstep blocked' % (mid, e['name'], e['x'], e['y']))
    return problems
