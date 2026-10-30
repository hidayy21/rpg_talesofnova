# Widens every edge exit to the whole open crossing: map edge cells next to an exit become exits too while they
# can be walked on (and hold no other event) AND the same lane is open on the other side, so a road never leaves
# a strip along the edge that leads nowhere, and a lane never lands on a wall. Town.save() runs this after
# writing a map; for maps edited in the editor:
#   python edge_exits.py            -> report only
#   python edge_exits.py --apply    -> widen the exits of every Royal Capital map (editor must be closed)
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import nova_maplib as L


def _load(mid): return json.load(open(L.DATA + 'Map%03d.json' % mid, encoding='utf8'))


def _transfer(e):
    for pg in e['pages']:
        for c in pg['list']:
            if c['code'] == 201 and c['parameters'][0] == 0: return c['parameters']
    return None


def _open(m, x, y, flags):
    """Walkable ground: passable, and not the top of a wall or a roof (A3/A4 tops count as passable in the tileset)."""
    import validate_maps as V
    w, h = m['width'], m['height']
    if not (0 <= x < w and 0 <= y < h): return False
    ground = m['data'][y * w + x]
    return V.passable(m, x, y, flags) and not (L.A3 <= ground < 8192)


def _side(m, x, y):
    w, h = m['width'], m['height']
    if x == 0: return 'w'
    if x == w - 1: return 'e'
    if y == 0: return 'n'
    if y == h - 1: return 's'
    return None


def widen(m, load=_load):
    """Adds exits to map dict m in place; returns the cells added."""
    import validate_maps as V
    flags = V.flags_for(m['tilesetId'])
    taken = {(e['x'], e['y']) for e in m['events'] if e}
    exits = {}
    for e in m['events']:
        if not e or e['pages'][0]['trigger'] != 1: continue
        t = _transfer(e)
        side = _side(m, e['x'], e['y'])
        if t and side: exits.setdefault((side, t[1]), []).append(e)
    added = []
    targets = {}
    for (side, tmap), evs in exits.items():
        along = (lambda e: e['y']) if side in 'we' else (lambda e: e['x'])
        fixed = evs[0]['x'] if side in 'we' else evs[0]['y']
        cell = (lambda k: (fixed, k)) if side in 'we' else (lambda k: (k, fixed))
        have = {along(e): e for e in evs}
        if tmap not in targets: targets[tmap] = load(tmap)
        tm = targets[tmap]
        tflags = V.flags_for(tm['tilesetId'])
        for k0 in sorted(have):
            for step in (-1, 1):
                k = k0 + step
                while k not in have:
                    x, y = cell(k)
                    if (x, y) in taken or not _open(m, x, y, flags): break
                    near = have[min(have, key=lambda j: abs(j - k))]
                    p = _transfer(near)
                    delta = k - along(near)
                    tx, ty = (p[2], p[3] + delta) if side in 'we' else (p[2] + delta, p[3])
                    if not _open(tm, tx, ty, tflags) or any(
                            o and o['x'] == tx and o['y'] == ty and o['pages'][0]['priorityType'] == 1 for o in tm['events']):
                        break                                   # the lane is closed on the other side
                    page = json.loads(json.dumps(near['pages'][0]))
                    for c in page['list']:
                        if c['code'] == 201: c['parameters'][2], c['parameters'][3] = tx, ty
                    base = near['name'].rstrip('0123456789').rstrip()
                    slot = next((i for i in range(1, len(m['events'])) if m['events'][i] is None), len(m['events']))
                    ev = {'id': slot, 'name': '%s %d' % (base, len([1 for v in have.values()]) + 1), 'note': near['note'],
                          'pages': [page] + near['pages'][1:], 'x': x, 'y': y}
                    if slot == len(m['events']): m['events'].append(ev)
                    else: m['events'][slot] = ev
                    have[k] = ev; taken.add((x, y)); added.append((x, y, tmap))
                    k += step
    return added


if __name__ == '__main__':
    import kingdom as K
    import validate_maps as V
    from build_kingdom import editor_running
    city = [K.BAKERS_LANE, K.PLAZA, K.MARKET, K.RESIDENTIAL, K.HARBOR, K.CASTLE_APPROACH, K.CITY_GATE,
            K.HOLLOW_FARM, K.ROYAL_QUARTER, K.TERRACES]
    maps = {mid: _load(mid) for mid in range(1, K.TERRACES + 1)}
    for mid in city:
        added = widen(maps[mid], lambda t: maps[t])
        for x, y, t in added: print('map %d: exit to map %d added at (%d,%d)' % (mid, t, x, y))
    problems = V.check(maps)
    print('\n'.join(problems) if problems else 'validation: OK')
    if '--apply' in sys.argv:
        if problems: sys.exit('not applying: fix the problems above first')
        if editor_running(): sys.exit('not applying: RPG Maker MV is open - save and close it first')
        for mid in city: L.write_map(mid, maps[mid])
        print('applied')
