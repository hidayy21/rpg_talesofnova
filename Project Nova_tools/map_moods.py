# Mood of every map, as NovaAtmosphere map-note tags: colour grade preset, fog, window light (indoor sunbeams)
# and particles. Tags not listed here are left as they are; None removes a tag.
#   python3 map_moods.py           -> report
#   python3 map_moods.py --apply   -> write the maps (RPG Maker editor must be closed)
import os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import nova_maplib as L
import compose_tileset as C
import kingdom as K

ROOM = {'grade': 'interior', 'sunbeams': 0.45, 'particles': 'dust'}      # a room with windows, lit by day
DIM = {'grade': 'interior'}
MOODS = {
    K.BAKERS_LANE: {'grade': 'warm'}, K.PLAZA: {'grade': 'warm'}, K.MARKET: {'grade': 'warm'},
    K.RESIDENTIAL: {'grade': 'warm'}, K.TERRACES: {'grade': 'warm'}, K.CITY_GATE: {'grade': 'warm'},
    K.HOLLOW_FARM: {'grade': 'warm'}, K.HARBOR: {'grade': 'coast'},
    K.CASTLE_APPROACH: {'grade': 'noble'}, K.ROYAL_QUARTER: {'grade': 'noble'},
    K.WEAPON_SHOP: ROOM, K.ARMOR_SHOP: ROOM, K.PET_SHOP: ROOM, K.BAKERY: ROOM, K.INN: ROOM,
    K.MAGIC_SHOP: {'grade': 'arcane', 'sunbeams': 0.35, 'particles': 'dust'},
    K.TAVERN: {'grade': 'interior', 'sunbeams': 0.3, 'particles': 'dust'},
    K.BARRACKS: DIM, K.TOWNHOUSE_1F: ROOM, K.TOWNHOUSE_2F: ROOM,
    K.ASHVEIL_1F: ROOM, K.ASHVEIL_2F: ROOM, K.ASHVEIL_3F: ROOM,
    K.PRISON_1F: {'grade': 'gloom'}, K.PRISON_CELLS: {'grade': 'gloom', 'particles': 'dust'},
    27: {'grade': 'arcane'},                                    # Prologue - Sealed Vault
    28: {'grade': 'warm'},                                      # Skyreach Hill
    29: {'grade': 'mystic', 'fog': 0.5, 'fog color': '#8fa3a2', 'sunbeams': 0.3, 'vignette': 0.45},                        # Briarwood: deep, misty, a little uncanny
    30: {'grade': 'forest', 'fog': 0.25, 'fog color': '#b4c4bc'},                        # Briarwood - Entrance: the mist starts here
    K.ACADEMY: {'grade': 'warm', 'bloom': 0.3, 'sunbeams': 0.6, 'vignette': 0.3, 'fog': 0.12,   # a village under a
                'fog color': '#e6dcf2'},                                         # mage school: soft glow, faint violet haze
    K.ACADEMY_HALL: {'grade': 'arcane', 'sunbeams': 0.3, 'particles': 'dust'},
    K.ACADEMY_COURT: {'grade': 'noble', 'bloom': 0.3, 'sunbeams': 0.6, 'vignette': 0.25, 'fog': 0.1,     # the court
                      'fog color': '#e6dcf2'},                                         # shares the village's violet haze
    K.ACADEMY_CLASSES: ROOM, K.ACADEMY_UPPER: ROOM,
    K.ACADEMY_LIBRARY: {'grade': 'arcane', 'sunbeams': 0.25, 'particles': 'dust'},
    K.ACADEMY_UNDERCROFT: {'grade': 'gloom', 'particles': 'dust'}, K.ACADEMY_TOWER: {'grade': 'arcane', 'bloom': 0.5, 'vignette': 0.4,
                                                                                         'particles': 'fireflies'},   # motes like stars
    K.ACADEMY_DINING: {'grade': 'interior', 'sunbeams': 0.4, 'particles': 'dust'},
    K.FROSTHOLLOW: {'grade': 'noble', 'particles': 'snow', 'fog': 0.15, 'fog color': '#dfe8f5'},   # falling snow, a pale haze
    K.FROST_INN: {'grade': 'interior', 'sunbeams': 0.35, 'particles': 'dust'}, K.FROST_STORE: ROOM,
    K.FROST_SMITHY: {'grade': 'interior', 'particles': 'embers'},                 # sparks from the forge
    K.VILLA_BLOODROSE: {'grade': 'noble', 'fog': 0.45, 'fog color': '#eef2f4', 'vignette': 0.3,   # day by default, soft white mist;
                        'particles': 'auto',                                      # the clock brings the night (ch. 7, 11)
                        'fog bank': '0,45,19,49,0.8; 23,45,43,49,0.8', 'bloom': 0.2,   # thick grey mist in the dead wood
                        'fog mystery': 1},                                        # either side of the road
    K.VILLA_HALL: {'grade': 'interior', 'vignette': 0.35, 'particles': 'dust'},    # candlelight and moonlit windows
    K.VILLA_UPPER: {'grade': 'interior', 'vignette': 0.35, 'particles': 'dust'},
    K.VILLA_LIBRARY: {'grade': 'interior', 'vignette': 0.4, 'particles': 'dust'},
    K.VILLA_ARCHIVE: {'grade': 'arcane', 'vignette': 0.5, 'particles': 'dust'},   # shut away for centuries
    **{mid: {'grade': 'interior', 'vignette': 0.35, 'particles': 'dust'} for mid in (
        K.VILLA_BALLROOM, K.VILLA_DINING, K.VILLA_MUSIC, K.VILLA_WEST, K.VILLA_EAST, K.VILLA_LYSANDRE, K.VILLA_STUDY, K.VILLA_GUEST, K.VILLA_GUEST2)},
    K.QUILL_INN: ROOM, K.QUILL_APOTHECARY: {'grade': 'interior', 'sunbeams': 0.35, 'particles': 'dust'},
}


def set_tag(note, tag, value):
    note = re.sub(r'\n?<%s:[^>]*>' % re.escape(tag), '', note)
    if value is None: return note
    return (note + '\n' if note and not note.endswith('\n') else note) + '<%s: %s>' % (tag, value)


if __name__ == '__main__':
    apply = '--apply' in sys.argv
    for mid, tags in sorted(MOODS.items()):
        path = L.DATA + 'Map%03d.json' % mid
        m = C._read(path)
        note = m['note']
        for tag, value in tags.items(): note = set_tag(note, tag, value)
        if note == m['note']: continue
        print('Map%03d %-32s %s' % (mid, m['displayName'], note.replace('\n', ' ')))
        m['note'] = note
        if apply:
            with open(path, 'w', encoding='utf8', newline='') as f: f.write(C._map_text(m))
