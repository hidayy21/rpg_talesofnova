# Moves Saltwind Harbor east of the Market District, facing the bay east of the capital on the World Map. The
# harbor is rebuilt from map_harbor.py (its own layout changes completely); the Market is edited in place: its
# east road (the old East Gate) opens to the harbor, its south road is barricaded. Run after patch_city_expansion.py.
#   python patch_harbor_east.py            -> validate only
#   python patch_harbor_east.py --apply    -> save Map006 and patch Map004 (editor must be closed)
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import nova_maplib as L
import kingdom as K
import validate_maps as V
from town_kit import BARRICADE_H, BARRICADE_V
from build_kingdom import editor_running, as_dict
from patch_city_links import load, drop, barricade
from patch_city_expansion import unbarricade, add_exit


def patch():
    market = load(K.MARKET)
    barricade(market, drop(market, 'To Harbor'), BARRICADE_H)
    cells = [(market['width'] - 1, y) for y in range(14, 18)]
    unbarricade(market, cells, BARRICADE_V)
    add_exit(market, 'To Harbor', cells, *K.ARRIVE['harbor_from_market'])
    while len(market['events']) > 1 and market['events'][-1] is None: market['events'].pop()
    return market


if __name__ == '__main__':
    import map_harbor
    market = patch()
    allmaps = {mid: load(mid) for mid in range(1, K.TERRACES + 1)}
    allmaps[K.MARKET] = market
    allmaps[K.HARBOR] = as_dict(map_harbor.m)
    problems = V.check(allmaps)
    print('\n'.join(problems) if problems else 'validation: OK')
    if '--apply' in sys.argv:
        if problems: sys.exit('not applying: fix the problems above first')
        if editor_running(): sys.exit('not applying: RPG Maker MV is open - save and close it first')
        map_harbor.m.save(K.HARBOR, parent_id=K.PLAZA, order=6)
        L.write_map(K.MARKET, market)
        print('applied')
