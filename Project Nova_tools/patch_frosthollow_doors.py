# Frosthollow (Map042) has hand edits since map_frosthollow.py ran, so this edits its events in place:
#   - the Hearthfire Inn, General Store and Smithy doors open onto their interiors (Map043-045)
#   - a few of the snowy crates, barrels and pots already on the map can be searched once each for potions
#     (invisible events on the prop's own tile; self switch A empties them)
# Running it again changes nothing.
#   python patch_frosthollow_doors.py            -> report
#   python patch_frosthollow_doors.py --apply    -> write Map042 (editor must be closed)
import json, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import nova_maplib as L
from nova_maplib import page, cmd, text
import kingdom as K

DOORS = {'Hearthfire Inn': 'frost_inn_from_town', 'General Store': 'frost_store_from_town', 'Smithy': 'frost_smithy_from_town'}
POTION, HI_POTION = 1, 5
NAMES = {POTION: 'Potion', HI_POTION: 'Hi-Potion'}
LOOT = [('Crate', 16, 9, POTION, 1, 'crate'),           # stacked by the supply depot
        ('Barrel', 2, 30, POTION, 1, 'barrel'),         # beside the west cottage
        ('Pot', 4, 34, HI_POTION, 1, 'pot'),            # at the foot of the west cliff
        ('Crate', 54, 36, POTION, 2, 'crate')]          # by the lower house on the east side


def loot_pages(item, n, where):
    found = [cmd(250, [{'name': 'Item3', 'volume': 80, 'pitch': 100, 'pan': 0}]), cmd(126, [item, 0, 0, n]),
             *text('Found %d \\C[6]%s\\C[0] in the %s!' % (n, NAMES[item], where)), cmd(123, ['A', 0])]
    return [page(None, commands=found, priority=1),
            page(None, commands=text('The %s is empty.' % where), priority=1,
                 cond={'selfSwitchValid': True, 'selfSwitchCh': 'A'})]


def patch(m):
    ev = m['events']
    for e in ev:
        if e and e['name'] in DOORS:
            style = e['pages'][0]['image'].get('characterIndex', 0)
            style = style if isinstance(style, int) else 0     # all three are plain wooden doors (style 0)
            target, x, y, d = K.ARRIVE[DOORS[e['name']]]
            e['pages'] = [L.door_page(target, x, y, d, '!Door1', style)]
            e['note'] = ''
    at = {(e['x'], e['y']): e for e in ev if e}
    for name, x, y, item, n, where in LOOT:
        full = 'Loot: %s' % name
        e = at.get((x, y))
        if e and e['name'] != full: raise SystemExit('(%d,%d) already has event "%s"' % (x, y, e['name']))
        if e: e['pages'] = loot_pages(item, n, where)
        else: ev.append({'id': len(ev), 'name': full, 'note': '', 'x': x, 'y': y, 'pages': loot_pages(item, n, where)})
    return m


if __name__ == '__main__':
    path = L.DATA + 'Map%03d.json' % K.FROSTHOLLOW
    m = patch(json.load(open(path, encoding='utf8')))
    for e in m['events']:
        if e and (e['name'] in DOORS or e['name'].startswith('Loot:')):
            print('%-16s (%2d,%2d) -> %s' % (e['name'], e['x'], e['y'], [c['parameters'] for c in e['pages'][0]['list'] if c['code'] in (201, 126)]))
    if '--apply' in sys.argv:
        L.write_map(K.FROSTHOLLOW, m)
        print('saved Map%03d' % K.FROSTHOLLOW)
