# Background music (and ambience) of every map. Interiors without BGM keep the street's music playing, as RPG Maker
# does when a map has no autoplay BGM. Story events that play or fade music (prologue, Skyreach Hill) still win.
# Change a name here and run again to try another track (the DLC has many more: RPG Maker MV/dlc/BaseResource_Compressed).
#   python3 map_music.py           -> report
#   python3 map_music.py --apply   -> write the maps (RPG Maker editor must be closed)
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import nova_maplib as L
import compose_tileset as C
import kingdom as K

# map: (bgm, volume) ; BGS only where it changes: map: (bgs, volume)
BGM = {
    K.BAKERS_LANE: ('03_Valley_Village', 75), K.PLAZA: ('Town2', 80), K.MARKET: ('03_Chasing_Fortune', 75),
    K.RESIDENTIAL: ('Town3', 75), K.HARBOR: ('Ship1', 70), K.CASTLE_APPROACH: ('03_Ancient_Castle', 75),
    K.ROYAL_QUARTER: ('03_Party_at_the_Royal_Palace', 70), K.TERRACES: ('Town5', 75),
    K.CITY_GATE: ('Town1', 80), K.HOLLOW_FARM: ('03_A_Gentle_Breeze', 70),
    K.TAVERN: ('03_Adventurers', 70), K.INN: ('03_The_Calm', 65),
    K.ASHVEIL_1F: ('03_Childhood_Memories', 65), K.ASHVEIL_2F: ('03_Childhood_Memories', 65),
    K.ASHVEIL_3F: ('03_Childhood_Memories', 65), K.PRISON_1F: ('03_Suspense', 65),
    29: ('03_Fantasy_Forest', 65),        # Briarwood
    30: ('03_Fantasy_Forest', 65),        # Briarwood - Entrance
    K.ACADEMY: ('Town5', 75), K.ACADEMY_HALL: ('Castle2', 70),
    K.ACADEMY_COURT: ('Castle2', 65), K.ACADEMY_CLASSES: ('Castle2', 60), K.ACADEMY_LIBRARY: ('Castle2', 55),
    K.ACADEMY_UNDERCROFT: ('Dungeon1', 50), K.ACADEMY_UPPER: ('03_The_Calm', 55), K.ACADEMY_TOWER: ('03_The_Calm', 55),
    K.ACADEMY_DINING: ('Castle2', 70),
    K.QUILL_INN: ('03_The_Calm', 65),
}
BGS = {29: ('Night', 60), 30: ('Wind1', 30)}       # Briarwood keeps its night insects

if __name__ == '__main__':
    apply = '--apply' in sys.argv
    for mid in sorted(set(BGM) | set(BGS)):
        path = L.DATA + 'Map%03d.json' % mid
        m = C._read(path)
        new = dict(m)
        for key, table in (('bgm', BGM), ('bgs', BGS)):
            if mid not in table: continue
            name, vol = table[mid]
            assert os.path.isfile(L.PROJ + 'audio/%s/%s.ogg' % (key, name)), name
            new[key] = {'name': name, 'pan': 0, 'pitch': 100, 'volume': vol}
            new['autoplayBgm' if key == 'bgm' else 'autoplayBgs'] = True
        if new == m: continue
        print('Map%03d %-34s %s%s' % (mid, m['displayName'], new['bgm']['name'] if new['autoplayBgm'] else '-',
                                       ('  + ' + new['bgs']['name']) if new['autoplayBgs'] else ''))
        if apply:
            with open(path, 'w', encoding='utf8', newline='') as f: f.write(C._map_text(new))
