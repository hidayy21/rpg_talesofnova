# Street life on Lantern Row's main road (y10..18): a bread & fruit stall by the canal, a notice board, a flower
# cart, barrels and crates by the doors, and the people of the street. Used by map_residential.py when the map is
# built from script, and applied in place to the saved Map005 (hand edits survive):
#   python lantern_street_life.py            -> check only
#   python lantern_street_life.py --apply    -> patch Map005 (editor must be closed)
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from town_kit import *
from town_kit import wander_route
import nova_maplib as L
import kingdom as K

# (x, y, tile, layer)
PROPS = [
    # bread & fruit stall on the east bank of the canal (tent + wares in front)
    *[(33 + c, 11 + r, TENT[r][c], 3 if r == 0 else 2) for r in range(3) for c in range(3)],
    (32, 13, PROP['basket_bread'], 2), (36, 13, PROP['crate_apples'], 2), (34, 14, PROP['basket_apples'], 2),
    # notice board and a signpost by the west bridgehead
    (18, 11, NOTICE_BOARD, 2), (19, 14, SIGNPOST, 2),
    # flower cart (crates of greens and dried flowers) in front of the townhouses
    (8, 12, PROP['crate_greens'], 2), (9, 12, PROP['dry_flowers'], 2), (10, 12, PROP['potted_a'], 2),
    # barrels and crates by the doors
    (1, 11, BARREL, 2), (2, 11, BARREL, 2), (12, 11, CRATE, 2), (27, 11, PROP['sack_a'], 2),
    (40, 11, CRATE, 2), (41, 11, PROP['stacked_crates_a'], 2),
]


def people(m):
    """Adds the street's people to a Town builder (or a scratch one whose events get copied)."""
    m.npc('Baker\'s Daughter', 34, 14, 'People2', 1, ('Baker\'s Daughter:', 'Fresh rolls from Golden Crust Bakery!',
          'Papa bakes them on Baker\'s Lane - just west of here.'), direction=2)
    m.npc('Flower Seller', 9, 13, 'People1', 3, ('Flower Seller:', 'Lavender for luck, marigolds for courage.',
          'And roses... for whoever you are thinking of right now.'), direction=2)
    m.npc('Street Bard', 27, 15, 'People4', 7, ('Street Bard:', '~ Oh the lamps of Lantern Row, they glow so bright... ~',
          'A copper for the song? No? Then a smile will do.'), direction=4)
    m.npc('Child', 12, 16, 'People1', 5, ('Child:', 'We\'re playing knights! I\'m the king!'), move=1, freq=5, speed=4)
    m.npc('Child', 14, 17, 'People2', 0, ('Child:', 'No fair, you were king yesterday!'), move=1, freq=5, speed=4)
    m.npc('Grandmother', 38, 16, 'People1', 6, ('Grandmother:', 'Sixty years on Lantern Row.',
          'The lamps were oil back then. Now the lamplighter just waves his staff.'), route=wander_route('LLLLWRRRRW'), speed=2)
    m.npc('Newcomer', 17, 12, 'People4', 1, ('Newcomer:', 'The notice board says the Royal Archives need copyists.',
          'Good pay, they say. Long hours, they don\'t say.'), direction=8)
    m.critter('Street Cat', 3, 12, 'Nature', 1, 'Cat', 'The cat is asleep on a warm barrel.', move=0)
    m.sign('Notice Board', 18, 11, ['\\C[6]Lantern Row Notices\\C[0]', 'COPYISTS WANTED - Royal Archives, Royal Quarter.',
           'Farm hands wanted at Hollow Farm, outside the Main Gate.'])
    m.sign('Signpost', 19, 14, ['\\C[6]East:\\C[0] Grand Plaza   \\C[6]West:\\C[0] Baker\'s Lane',
           '\\C[6]North lane:\\C[0] Hearthstone Terraces'])


def apply_builder(m):
    for x, y, t, layer in PROPS: m.put(x, y, t, layer)
    people(m)


def apply_json(mp):
    """Patch a saved map dict: props on empty upper-layer cells, events appended (fails on any clash)."""
    w, h = mp['width'], mp['height']
    for x, y, t, layer in PROPS:
        i = (layer * h + y) * w + x
        assert mp['data'][i] in (0, t), 'tile already at %d,%d layer %d' % (x, y, layer)
        mp['data'][i] = t
    scratch = Town(w, h, 'scratch', '')
    people(scratch)
    taken = {(e['x'], e['y']) for e in mp['events'] if e}
    for ev in scratch.events[1:]:
        assert (ev['x'], ev['y']) not in taken, 'event already at %d,%d' % (ev['x'], ev['y'])
        assert not any(e and e['name'] == ev['name'] and (e['x'], e['y']) == (ev['x'], ev['y']) for e in mp['events'])
        ev = dict(ev, id=len(mp['events']))
        mp['events'].append(ev)
    return mp


if __name__ == '__main__':
    import validate_maps as V
    from patch_city_links import load
    from build_kingdom import editor_running
    mp = apply_json(load(K.RESIDENTIAL))
    maps = {mid: load(mid) for mid in range(1, K.TERRACES + 1)}
    maps[K.RESIDENTIAL] = mp
    problems = V.check(maps)
    print('\n'.join(problems) if problems else 'validation: OK')
    if '--apply' in sys.argv:
        if problems: sys.exit('not applying: fix the problems above first')
        if editor_running(): sys.exit('not applying: RPG Maker MV is open - save and close it first')
        L.write_map(K.RESIDENTIAL, mp)
        print('applied')
