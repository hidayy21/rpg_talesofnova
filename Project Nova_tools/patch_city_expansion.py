# Adds the three districts that round off the Royal Capital and links them in, editing the saved district maps in
# place (hand edits made in the editor survive). Run after patch_city_links.py. Layout after the patch:
#                  Hearthstone Terraces   Castle Approach - Royal Quarter
#   Baker's Lane - Lantern Row ---------- Grand Plaza ----- Market District
#                  Hollow Farm ---------- Main Gate         Saltwind Harbor
#   python patch_city_expansion.py            -> validate only (new maps built in memory)
#   python patch_city_expansion.py --apply    -> save Map023-026 and patch Map004, Map005, Map007 (editor closed)
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import nova_maplib as L
import kingdom as K
import validate_maps as V
from town_kit import BARRICADE_H, BARRICADE_V
from build_kingdom import editor_running, as_dict
from patch_city_links import load


def unbarricade(m, cells, tile=BARRICADE_H):
    """Take the barricade off a road that opens again."""
    w, h = m['width'], m['height']
    for x, y in cells:
        hit = False
        for layer in (3, 2):
            i = (layer * h + y) * w + x
            if m['data'][i] == tile: m['data'][i] = 0; hit = True; break
        assert hit, 'no barricade at %d,%d' % (x, y)


def add_exit(m, name, cells, target, tx, ty, d):
    """Edge exits, keeping the player's lane like Town.exit; reuses empty event slots."""
    for i, (x, y) in enumerate(cells):
        assert not any(e and e['x'] == x and e['y'] == y for e in m['events']), 'event already at %d,%d' % (x, y)
        ox = (x - cells[0][0]) if d in (2, 8) else 0
        oy = (y - cells[0][1]) if d in (4, 6) else 0
        slot = next((k for k in range(1, len(m['events'])) if m['events'][k] is None), len(m['events']))
        ev = {'id': slot, 'name': '%s %d' % (name, i + 1), 'note': '', 'x': x, 'y': y,
              'pages': [L.exit_page(target, tx + ox, ty + oy, d)]}
        if slot == len(m['events']): m['events'].append(ev)
        else: m['events'][slot] = ev


def patch():
    market, res, castle = load(K.MARKET), load(K.RESIDENTIAL), load(K.CASTLE_APPROACH)
    # Castle Approach: the moat walk (y14) runs on east into the Royal Quarter
    add_exit(castle, 'To Royal Quarter', [(castle['width'] - 1, 14)], *K.ARRIVE['royal_from_castle'])
    # Market District: the north alley opens again, now to the Royal Quarter
    cells = [(x, 0) for x in range(20, 23)]
    unbarricade(market, cells)
    add_exit(market, 'To Royal Quarter', cells, *K.ARRIVE['royal_from_market'])
    # Lantern Row: the north lane opens again, now to Hearthstone Terraces
    cells = [(x, 0) for x in range(37, 41)]
    unbarricade(res, cells)
    add_exit(res, 'To Hearthstone Terraces', cells, *K.ARRIVE['terraces_from_residential'])
    return {K.MARKET: market, K.RESIDENTIAL: res, K.CASTLE_APPROACH: castle}


if __name__ == '__main__':
    import map_city_gate, map_hollow_farm, map_royal_quarter, map_terraces
    new = {K.CITY_GATE: map_city_gate.m, K.HOLLOW_FARM: map_hollow_farm.m, K.ROYAL_QUARTER: map_royal_quarter.m,
           K.TERRACES: map_terraces.m}
    maps = patch()
    allmaps = {mid: load(mid) for mid in range(1, K.CITY_GATE)}
    allmaps.update(maps)
    allmaps.update({mid: as_dict(b) for mid, b in new.items()})
    problems = V.check(allmaps)
    print('\n'.join(problems) if problems else 'validation: OK')
    if '--apply' in sys.argv:
        if problems: sys.exit('not applying: fix the problems above first')
        if editor_running(): sys.exit('not applying: RPG Maker MV is open - save and close it first')
        for mid, b in new.items():
            b.save(mid, parent_id=K.PLAZA, order=mid)
        for mid, m in maps.items():
            L.write_map(mid, m)
        print('applied')
