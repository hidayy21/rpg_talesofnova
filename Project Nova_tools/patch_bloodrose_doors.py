# Villa Bloodrose (Map048) belongs to the user's hand edits now, so this edits two of its events in place:
#   - the Great Doors open (the !$Gate1 doors swing) onto the Grand Hall (Map049)
#   - 'Loot: Offering' gives the Magic Water its text promises (it gave item 7, an Elixir, by mistake)
# Running it again changes nothing.
#   python patch_bloodrose_doors.py            -> report
#   python patch_bloodrose_doors.py --apply    -> write Map048 (editor must be closed)
import json, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import nova_maplib as L
import kingdom as K

MAGIC_WATER = 2


def patch(m):
    for e in m['events']:
        if not e: continue
        if e['name'] == 'Great Doors':
            target, x, y, d = K.ARRIVE['hall_from_bloodrose']
            e['pages'] = [L.door_page(target, x, y, d, '!$Gate1', 0)]
        if e['name'] == 'Loot: Offering':
            for c in e['pages'][0]['list']:
                if c['code'] == 126: c['parameters'][0] = MAGIC_WATER
    return m


if __name__ == '__main__':
    m = patch(json.load(open(L.DATA + 'Map%03d.json' % K.VILLA_BLOODROSE, encoding='utf8')))
    for e in m['events']:
        if e and e['name'] in ('Great Doors', 'Loot: Offering'):
            print('%-15s (%2d,%2d) -> %s' % (e['name'], e['x'], e['y'],
                  [c['parameters'] for c in e['pages'][0]['list'] if c['code'] in (201, 126)]))
    if '--apply' in sys.argv:
        L.write_map(K.VILLA_BLOODROSE, m)
        print('saved Map%03d' % K.VILLA_BLOODROSE)
