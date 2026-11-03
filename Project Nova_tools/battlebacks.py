# Battle backgrounds for every map (instead of RPG Maker's blurred snapshot of the map): (floor, backdrop) from
# img/battlebacks1 and img/battlebacks2. The World Map keeps the editor's automatic choice by terrain.
#   python3 battlebacks.py           -> report
#   python3 battlebacks.py --apply   -> write the maps (RPG Maker editor must be closed)
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import nova_maplib as L
import compose_tileset as C
import kingdom as K

ROOM, SHOP, NOBLE = ('Wood1', 'Room1'), ('Wood2', 'Room3'), ('Wood1', 'Room2')
BB = {
    K.BAKERS_LANE: ('Cobblestones2', 'Town2'), K.PLAZA: ('Cobblestones1', 'Town2'),
    K.MARKET: ('Cobblestones1', 'Town3'), K.RESIDENTIAL: ('Cobblestones2', 'Town1'),
    K.HARBOR: ('Road1', 'Port'), K.CASTLE_APPROACH: ('Castle1', 'Brick'), K.ROYAL_QUARTER: ('Cobblestones4', 'Town5'),
    K.TERRACES: ('Cobblestones2', 'Town4'), K.CITY_GATE: ('Road1', 'Castle1'), K.HOLLOW_FARM: ('Meadow', 'Grassland'),
    K.WEAPON_SHOP: SHOP, K.ARMOR_SHOP: SHOP, K.MAGIC_SHOP: ROOM, K.PET_SHOP: SHOP, K.TAVERN: ('Wood2', 'Town4'),
    K.INN: NOBLE, K.BARRACKS: ('Cobblestones3', 'Fort1'), K.BAKERY: SHOP,
    K.TOWNHOUSE_1F: ROOM, K.TOWNHOUSE_2F: ROOM, K.ASHVEIL_1F: NOBLE, K.ASHVEIL_2F: NOBLE, K.ASHVEIL_3F: NOBLE,
    K.PRISON_1F: ('Cobblestones3', 'Stone1'), K.PRISON_CELLS: ('RockCave', 'Stone1'),
    27: ('Ruins1', 'Temple'),            # Prologue - Sealed Vault
    28: ('Grassland', 'Grassland'),      # Skyreach Hill
    29: ('GrassMaze', 'GrassMaze'),      # Briarwood
    30: ('Grassland', 'Forest'),         # Briarwood - Entrance
}

if __name__ == '__main__':
    apply = '--apply' in sys.argv
    for mid, (b1, b2) in sorted(BB.items()):
        for folder, name in (('battlebacks1', b1), ('battlebacks2', b2)):
            assert os.path.isfile(L.PROJ + 'img/%s/%s.png' % (folder, name)), (folder, name)
        path = L.DATA + 'Map%03d.json' % mid
        m = C._read(path)
        if (m['specifyBattleback'], m['battleback1Name'], m['battleback2Name']) == (True, b1, b2): continue
        print('Map%03d %-32s %s + %s' % (mid, m['displayName'], b1, b2))
        m.update({'specifyBattleback': True, 'battleback1Name': b1, 'battleback2Name': b2})
        if apply:
            with open(path, 'w', encoding='utf8', newline='') as f: f.write(C._map_text(m))
