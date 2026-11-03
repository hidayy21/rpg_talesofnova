# Nova at night: the townsfolk who stroll about (random walkers, route walkers, children) go home when the Night
# switch turns on, and about half of them are replaced by the Night Watch patrolling from the same spot. Sellers,
# people standing at their place, guards and animals stay. Done with a second event page on the Night switch (NovaDayNight
# turns it on and off with the clock), so the editor shows it and nothing else needs a plugin.
# Events with more than one page (story NPCs) are left alone. Running it again changes nothing.
#   python3 night_watch.py           -> report
#   python3 night_watch.py --apply   -> write the maps (RPG Maker editor must be closed)
import json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import nova_maplib as L
from nova_maplib import page, char, say
import compose_tileset as C
import kingdom as K

NIGHT = 10                                          # NovaLighting's Night Switch ("Night (lighting)")
MAPS = [K.BAKERS_LANE, K.PLAZA, K.MARKET, K.RESIDENTIAL, K.HARBOR, K.CASTLE_APPROACH, K.CITY_GATE,
        K.ROYAL_QUARTER, K.TERRACES]
GUARD_SHEETS = {('People3', 6), ('People3', 7)}
GUARD_NAME = re.compile(r'guard|soldier|patrol|watch|knight|officer|captain|sergeant|archer', re.I)
CHILD_NAME = re.compile(r'^(child|children|boy|urchin)$', re.I)   # not 'Flower Girl', 'Stable Boy'
MAX_WATCH = 3
LINES = [
    ('Streets are quiet after dark.', 'Let\'s keep it that way.'),
    ('The lanterns stay lit till dawn.', 'So do we.'),
    ('Out this late? Mind the alleys -', 'the market thief works nights too.'),
    ('No curfew in Nova, but the Captain', 'likes honest folk indoors by midnight.'),
    ('Move along, friend.', 'Nothing out here but cobblestones and cats.'),
]


def is_night_page(p):
    c = p['conditions']
    return c['switch1Valid'] and c['switch1Id'] == NIGHT


def strollers(m):
    """Single-page townsfolk who walk about (or children anywhere), in event order."""
    out = []
    for e in m['events'][1:]:
        if not e or not e['pages']: continue
        p, im = e['pages'][0], e['pages'][0]['image']
        sheet = im['characterName']
        if not sheet.startswith('People'): continue                      # animals, vehicles, doors
        if (sheet, im['characterIndex']) in GUARD_SHEETS or GUARD_NAME.search(e['name']): continue
        if len(e['pages']) > 1 and not any(is_night_page(q) for q in e['pages'][1:]): continue   # story NPC
        codes = {c['code'] for c in p['list']}
        if 117 in codes or 302 in codes: continue                         # sells something
        if p['moveType'] in (1, 3) or CHILD_NAME.search(e['name']): out.append(e)
    return out


def night_pages(m):
    """{event id: night page} - every other stroller (the first one included, at most MAX_WATCH) turns into the Night Watch."""
    pages, n = {}, 0
    for i, e in enumerate(strollers(m)):
        if i % 2 == 0 and n < MAX_WATCH:
            line = LINES[(m['tilesetId'] + e['id'] + n) % len(LINES)]
            pages[e['id']] = page(char('People3', 6 + n % 2, e['pages'][0]['image']['direction']), move_type=1,
                                  freq=2, speed=3, commands=say('Night Watch:', *line), cond={'switch1Valid': True, 'switch1Id': NIGHT})
            n += 1
        else:
            pages[e['id']] = page(None, priority=0, through=True, cond={'switch1Valid': True, 'switch1Id': NIGHT})
    return pages


if __name__ == '__main__':
    apply = '--apply' in sys.argv
    for mid in MAPS:
        path = L.DATA + 'Map%03d.json' % mid
        m = C._read(path)
        new = night_pages(m)
        changed = False
        for e in m['events']:
            if not e or e['id'] not in new: continue
            pages = [p for p in e['pages'] if not is_night_page(p)] + [new[e['id']]]
            if pages != e['pages']:
                e['pages'], changed = pages, True
        watch = [m['events'][i]['name'] for i, p in new.items() if p['image']['characterName']]
        home = [m['events'][i]['name'] for i, p in new.items() if not p['image']['characterName']]
        print('Map%03d %-34s watch: %s | home: %s' % (mid, m['displayName'], ', '.join(watch) or '-', ', '.join(home) or '-'))
        if apply and changed:
            with open(path, 'w', encoding='utf8', newline='') as f: f.write(C._map_text(m))
