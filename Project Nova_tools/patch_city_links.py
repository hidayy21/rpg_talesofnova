# Re-links the Royal Capital's districts around the new Main Gate, editing the saved maps in place (events and the
# barricades that close old roads) so hand edits made in the editor survive. Layout after the patch:
#                      Castle Approach
#   Baker's Lane - Lantern Row - Grand Plaza - Market District
#                                Main Gate     Saltwind Harbor
# The Main Gate is the only way in from the World Map.
#   python patch_city_links.py            -> validate only (Main Gate built in memory)
#   python patch_city_links.py --apply    -> save Map023 and patch Map001-006 (editor must be closed)
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import nova_maplib as L
import kingdom as K
import validate_maps as V
from town_kit import BARRICADE_H, BARRICADE_V
from build_kingdom import editor_running, as_dict


def load(mid): return json.load(open(L.DATA + 'Map%03d.json' % mid, encoding='utf8'))


def drop(m, prefix):
    """Remove every event whose name starts with prefix; returns their (x, y)."""
    cells = []
    for i, e in enumerate(m['events']):
        if e and e['name'].startswith(prefix):
            cells.append((e['x'], e['y'])); m['events'][i] = None
    assert cells, 'no events named %r' % prefix
    return cells


def relink(m, prefix, name, arrive):
    """Point the exits named prefix* somewhere else; arrive(x, y) -> (map, x, y, dir)."""
    hit = 0
    for e in m['events']:
        if e and e['name'].startswith(prefix):
            hit += 1
            e['name'] = '%s %d' % (name, hit)
            e['pages'] = [L.exit_page(*arrive(e['x'], e['y']))]
    assert hit, 'no events named %r' % prefix


def barricade(m, cells, tile):
    """Close a road where it meets the map edge: a wooden barricade on the first free upper layer."""
    w, h = m['width'], m['height']
    for x, y in cells:
        for layer in (2, 3):
            i = (layer * h + y) * w + x
            if m['data'][i] == 0:
                m['data'][i] = tile; break
        else:
            raise AssertionError('no free layer for a barricade at %d,%d' % (x, y))


def patch():
    maps = {mid: load(mid) for mid in (K.WORLD, K.BAKERS_LANE, K.PLAZA, K.MARKET, K.RESIDENTIAL, K.HARBOR)}
    world, bakers, plaza, market, res, harbor = (maps[k] for k in (K.WORLD, K.BAKERS_LANE, K.PLAZA, K.MARKET,
                                                                     K.RESIDENTIAL, K.HARBOR))
    gate = K.ARRIVE['gate_from_plaza']

    # World Map: every tile of the capital leads to the Main Gate
    relink(world, 'Royal Capital Nova - ', 'Royal Capital Nova - Main Gate', lambda x, y: K.ARRIVE['gate_from_world'])

    # Grand Plaza: the south road goes out through the Main Gate (lane kept on the 5-wide bridge);
    # the north-west alley to Baker's Lane is closed
    relink(plaza, 'To Harbor', 'To Main Gate', lambda x, y: (gate[0], min(max(x - 1, gate[1] - 2), gate[1] + 2), gate[2], 2))
    barricade(plaza, drop(plaza, "To Baker's Lane"), BARRICADE_H)

    # Saltwind Harbor: reached from the Market only
    barricade(harbor, drop(harbor, 'To Plaza'), BARRICADE_H)

    # Market District: no more alley to Lantern Row, no East Gate
    barricade(market, drop(market, 'To Residential (alley)'), BARRICADE_H)
    barricade(market, drop(market, 'To World Map (East Gate)'), BARRICADE_V)

    # Lantern Row: Baker's Lane lies to the west; north and south roads closed
    barricade(res, drop(res, "To Baker's Lane"), BARRICADE_H)
    barricade(res, drop(res, 'To Market'), BARRICADE_H)
    a1, a2 = K.ARRIVE['bakers_from_residential_1'], K.ARRIVE['bakers_from_residential_2']
    for e in res['events']:
        if e and e['name'].startswith('To World Map (West Gate)'):
            if 15 <= e['y'] <= 18: e['name'] = 'To Baker\'s Lane (north road)'; e['pages'] = [L.exit_page(a1[0], a1[1], a1[2] + e['y'] - 15, 4)]
            elif 44 <= e['y'] <= 47: e['name'] = 'To Baker\'s Lane (south road)'; e['pages'] = [L.exit_page(a2[0], a2[1], a2[2] + e['y'] - 44, 4)]
    barricade(res, drop(res, 'To World Map (West Gate)'), BARRICADE_V)       # the farm lanes (y25, y30-31)

    # Baker's Lane: its east ends now meet Lantern Row's west roads; the west ends are closed
    r1, r2 = K.ARRIVE['residential_from_bakers_1'], K.ARRIVE['residential_from_bakers_2']
    relink(bakers, 'Edge: Plaza (street 1)', 'Edge: Lantern Row (street 1)', lambda x, y: (r1[0], r1[1], r1[2] + y - 7, 6))
    relink(bakers, 'Edge: Plaza (street 2)', 'Edge: Lantern Row (street 2)', lambda x, y: (r2[0], r2[1], r2[2] + y - 17, 6))
    barricade(bakers, drop(bakers, 'Edge: Residential'), BARRICADE_V)

    for m in maps.values():                          # trailing empty slots are not needed
        while len(m['events']) > 1 and m['events'][-1] is None: m['events'].pop()
    return maps


if __name__ == '__main__':
    import map_city_gate
    maps = patch()
    maps[K.CITY_GATE] = as_dict(map_city_gate.m)
    others = {mid: load(mid) for mid in range(7, K.CITY_GATE)}
    problems = V.check({**others, **maps})
    print('\n'.join(problems) if problems else 'validation: OK')
    if '--apply' in sys.argv:
        if problems: sys.exit('not applying: fix the problems above first')
        if editor_running(): sys.exit('not applying: RPG Maker MV is open - save and close it first')
        map_city_gate.m.save(K.CITY_GATE, parent_id=K.PLAZA, order=K.CITY_GATE)
        for mid, m in maps.items():
            if mid != K.CITY_GATE: L.write_map(mid, m)
        print('applied')
