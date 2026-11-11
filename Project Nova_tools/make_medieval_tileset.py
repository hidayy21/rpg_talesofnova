# Tileset 21 "Medieval Town": the Outside tileset (A1, A4, A5, Outside_B/C, Nova_Market_D - so town_kit works as
# in every town) with the MedievalVillage pack (Hypnobius, itch.io - free for commercial use, credit appreciated)
# mixed in:
#   A2  MedievalTown_A2 = Outside_A2, with the pack's grass / framed flagstones / rough cobbles in three unused kinds
#   A3  MedievalTown_A3 = roofs and walls picked from the pack, Outside_A3, PM_Town_A3 and Avy_Town_A3
#   E   MedievalVillage_B (gables, dormers, chimneys, windows, doors, barrels, crates, cart, bunting, palisade)
# Each picked kind keeps the passability of the tileset it comes from. Kind names for the map scripts: MED_GROUND,
# MED_ROOF, MED_WALL below.
#   python make_medieval_tileset.py           -> preview the sheets in _work/
#   python make_medieval_tileset.py --save    -> write img/tilesets/MedievalTown_A2/A3.png + Tilesets.json (editor closed)
import json, os, shutil, sys, time
from PIL import Image
import nova_maplib as L
import compose_tileset as C

TS_ID = 21
IMG = L.PROJ + 'img/tilesets/'
BASE = 2                                                   # Outside

# A2: (kind in the new sheet, source sheet, source kind, tileset whose flags it keeps, flag kind)
A2_PICKS = [(24, 'MedievalVillage_A2', 0, 2, 0),           # soft dark grass
            (13, 'MedievalVillage_A2', 1, 2, 2),           # flagstones in a stone frame (paved yards, the square)
            (15, 'MedievalVillage_A2', 2, 2, 2)]           # big rough cobbles (streets)
MED_GROUND = {'grass': 24, 'flagstone': 13, 'cobble': 15}

# A3: new kind -> (sheet, kind, tileset that holds that sheet's flags)
A3_PICKS = {
    # roofs, row 1
    0: ('MedievalVillage_A3', 0, 21), 1: ('MedievalVillage_A3', 1, 21), 2: ('Outside_A3', 0, 2), 3: ('Outside_A3', 1, 2),
    4: ('PM_Town_A3', 0, 9), 5: ('Outside_A3', 2, 2), 6: ('Outside_A3', 6, 2), 7: ('Avy_Town_A3', 0, 13),
    # walls, row 1
    8: ('MedievalVillage_A3', 8, 21), 9: ('MedievalVillage_A3', 9, 21), 10: ('MedievalVillage_A3', 10, 21),
    11: ('MedievalVillage_A3', 11, 21), 12: ('Outside_A3', 12, 2), 13: ('Outside_A3', 8, 2), 14: ('PM_Town_A3', 8, 9),
    15: ('Outside_A3', 11, 2),
    # roofs, row 2
    16: ('Outside_A3', 16, 2), 17: ('Outside_A3', 17, 2), 18: ('Outside_A3', 18, 2), 19: ('Outside_A3', 19, 2),
    20: ('Outside_A3', 20, 2), 21: ('Outside_A3', 4, 2), 22: ('Avy_Town_A3', 2, 13), 23: ('Outside_A3', 3, 2),
    # walls, row 2
    24: ('Outside_A3', 24, 2), 25: ('Outside_A3', 25, 2), 26: ('Outside_A3', 26, 2), 27: ('Outside_A3', 27, 2),
    28: ('Outside_A3', 28, 2), 29: ('Outside_A3', 10, 2), 30: ('Outside_A3', 9, 2), 31: ('PM_Town_A3', 11, 9),
}
MED_ROOF = {'shingle': 0, 'slate': 1, 'red': 2, 'orange': 3, 'terracotta': 4, 'indigo': 5, 'moss': 6, 'umber': 7,
            'wood': 16, 'wood2': 17, 'log': 18, 'thatch': 19, 'stone': 20, 'teal': 21, 'blue': 22, 'green': 23}
MED_WALL = {'timber_brick': 8, 'daub': 9, 'rubble': 10, 'timber': 11, 'tudor': 12, 'plaster': 13, 'ashlar': 14,
            'stone': 15, 'planks': 24, 'wood2': 25, 'log': 26, 'boards': 27, 'rockwall': 28, 'brick': 29,
            'brickstone': 30, 'sandstone': 31}

# MedievalVillage_B passability (everything else on the sheet defers to the tile below, like roofs and windows)
BLOCK = [1, 2, 3, 4, 5, 33, 34, 35, 36, 37, 38, 39]       # barrel, crate, cart, palisade foot, planters, crates, bush, barrel
A2_ID, A3_ID, E_FIRST = 2816, 4352, 768


def _sheet(name):
    im = Image.open(IMG + name + '.png').convert('RGBA')
    return im


def build():
    tilesets = json.load(open(L.DATA + 'Tilesets.json', encoding='utf8'))
    a2 = _sheet('Outside_A2').copy()
    for k, src, sk, _, _ in A2_PICKS:
        piece = _sheet(src).crop(((sk % 8) * 96, (sk // 8) * 144, (sk % 8) * 96 + 96, (sk // 8) * 144 + 144))
        a2.paste(piece, ((k % 8) * 96, (k // 8) * 144))
    a3 = Image.new('RGBA', (768, 384), (0, 0, 0, 0))
    for k, (src, sk, _) in A3_PICKS.items():
        piece = _sheet(src).crop(((sk % 8) * 96, (sk // 8) * 96, (sk % 8) * 96 + 96, (sk // 8) * 96 + 96))
        a3.paste(piece, ((k % 8) * 96, (k // 8) * 96))

    flags = list(tilesets[BASE]['flags'])
    for k, _, _, fts, fk in A2_PICKS:
        for s in range(48): flags[A2_ID + k * 48 + s] = tilesets[fts]['flags'][A2_ID + fk * 48 + s]
    for k, (_, sk, fts) in A3_PICKS.items():
        for s in range(48): flags[A3_ID + k * 48 + s] = tilesets[fts]['flags'][A3_ID + sk * 48 + s]
    for n in range(256): flags[E_FIRST + n] = 0x0F if n in BLOCK else 0x10
    flags[E_FIRST] = 0x10
    ts = dict(tilesets[TS_ID])
    ts.update(name='Medieval Town', mode=tilesets[BASE]['mode'], flags=flags,
              tilesetNames=['Outside_A1', 'MedievalTown_A2', 'MedievalTown_A3', 'Outside_A4', 'Outside_A5',
                            'Outside_B', 'Outside_C', 'Nova_Market_D', 'MedievalVillage_B'],
              note='Outside + the MedievalVillage pack (Hypnobius) - built by make_medieval_tileset.py')
    return a2, a3, tilesets, ts


if __name__ == '__main__':
    a2, a3, tilesets, ts = build()
    if '--save' not in sys.argv:
        a2.save(L.PROJ + 'Project Nova_tools/_work/MedievalTown_A2.png'); a3.save(L.PROJ + 'Project Nova_tools/_work/MedievalTown_A3.png')
        print('preview in _work/'); sys.exit()
    import tileset_wizard
    if tileset_wizard.editor_running(): sys.exit('close RPG Maker MV first')
    proj = os.path.abspath(L.PROJ)
    bak = os.path.join(os.path.dirname(proj), os.path.basename(proj) + '_backups', 'medieval_tileset_' + time.strftime('%Y%m%d_%H%M%S'))
    os.makedirs(bak, exist_ok=True)
    shutil.copy(L.DATA + 'Tilesets.json', bak)
    a2.save(IMG + 'MedievalTown_A2.png'); a3.save(IMG + 'MedievalTown_A3.png')
    tilesets[TS_ID] = ts
    with open(L.DATA + 'Tilesets.json', 'w', encoding='utf8', newline='') as f:
        f.write(C._tilesets_text(tilesets))
    print('saved tileset %d, backup in %s' % (TS_ID, bak))
