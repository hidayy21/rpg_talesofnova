# "additional asset 2 by avy" (credit: Avery) -> three packs in img/tilesets/import/, ready for the Tileset Wizard's
# "Import aset" (one tileset each):
#   Avy_Town    A3 house walls/roofs; B Avy B (roofs, columns, windows), B2 ship parts, B3-B4 packed town objects
#               (gothic windows, church spire, wells, palms, doors, crates, benches, roses, cart, world-map towns)
#   Avy_Castle  A4 both castle sets in one sheet (band 1 "Avy Castle": grey and sandstone; band 2 "castle3": grey
#               with arches, a wooden gate, battlements); B Avy Castle2, B2-B4 stone stairs and balustrades,
#               round towers, drawbridges
#   Avy_Nature  A2 Outside_A2 with the green and the snowy tree canopy in place of the yellow (12) and snowy (28)
#               bushes; B Water Cave, B2-B4 lighthouses (4 colours, railings), big trees, giant tree, rock plateau,
#               palms, tree trunks (they go under the canopies)
#   Avy_Palm    A2 Outside_A2 with the 9 palm forest canopies (dark, grass, sand ground; 3 shapes) in the right half
#               kinds the towns do not use (12, 13, 15, 20, 21, 28-31)
#   Avy_Landmarks  the two round towers (14x23: top 16 rows and the bottom 7 apart) and the premade castle (33x32,
#               in 15x16 parts): bigger than a sheet, so paint them part by part (left/right halves, then the rows below)
#   Avy_Ship    A2 Outside_A2 with the deck planks and the hatch grating in place of two snow kinds (24, 25); B the
#               hull, stairs, railings, crow's nest, wheel ("avy ship2"), B2 the masts, sails and flags ("Avy Ship")
# Characters: $Monster is a normal 8-character sheet (the "$" is wrong) -> img/characters/Avy_Monsters.png;
# Cerberus and Lion Battler -> img/sv_enemies/Avy_Cerberus.png, Avy_Lion.png.
#   python pack_avy.py [Avy_Ship]   (writes img/tilesets/import/Avy_* and the characters, or that one pack; rerun after changes)
import json, os, shutil, sys
from PIL import Image
import compose_tileset as C
import pack_sheets as P

SRC = C.PROJ + 'additional asset 2 by avy/'
OUT = C.PROJ + 'img/tilesets/import/'
s = lambda f, crop=None: (SRC + f, crop)


def copy(f, pack, name):
    os.makedirs(OUT + pack, exist_ok=True)
    shutil.copy2(SRC + f, OUT + pack + '/' + name)


def castle_a4():
    a4 = Image.new('RGBA', (768, 720), (0, 0, 0, 0))
    a4.paste(Image.open(SRC + 'Avy Castle.png').convert('RGBA').crop((0, 0, 768, 240)), (0, 0))
    a4.paste(Image.open(SRC + 'castle3.png').convert('RGBA').crop((0, 0, 768, 240)), (0, 240))
    os.makedirs(OUT + 'Avy_Castle', exist_ok=True)
    a4.save(OUT + 'Avy_Castle/A4.png')


A2_KIND = lambda k: ((k % 8) * 96, (k // 8) * 144)
CANOPIES = {12: 0, 28: 1}                                # Outside_A2 kind <- "Avy tree autotile" kind (green, snowy)
PALMS = [12, 13, 15, 20, 21, 28, 29, 30, 31]             # <- "Avy Palm Forest" kinds, row by row


def a2(pack, src, kinds, cols):
    sheet = Image.open(C.PROJ + 'img/tilesets/Outside_A2.png').convert('RGBA')
    art = Image.open(SRC + src).convert('RGBA')
    for k, i in kinds:
        x, y = A2_KIND(k)
        sheet.paste(Image.new('RGBA', (96, 144), (0, 0, 0, 0)), (x, y))
        sheet.paste(art.crop(((i % cols) * 96, (i // cols) * 144, (i % cols) * 96 + 96, (i // cols) * 144 + 144)), (x, y))
    os.makedirs(OUT + pack, exist_ok=True)
    sheet.save(OUT + pack + '/A2.png')


def characters():
    shutil.copy2(SRC + '$Monster.png', C.PROJ + 'img/characters/Avy_Monsters.png')
    shutil.copy2(SRC + 'Cerberus.png', C.PROJ + 'img/sv_enemies/Avy_Cerberus.png')
    shutil.copy2(SRC + 'Lion Battler.png', C.PROJ + 'img/sv_enemies/Avy_Lion.png')


DECK = [(24, 0), (25, 8)]        # Outside_A2 snow kinds <- "avy ship tile" deck planks, hatch grating


def ship():
    """Avy_Ship: a ship at sea - Outside A1 water, the deck and hatch in A2, the hull, then the masts and sails."""
    a2('Avy_Ship', 'avy ship tile.png', DECK, 8)
    with open(OUT + 'Avy_Ship/passage.json', 'w', encoding='utf8') as f: json.dump({'A2': {str(k): 'o' for k, _ in DECK}}, f)
    copy('avy ship2.png', 'Avy_Ship', 'B.png'); copy('Avy Ship.png', 'Avy_Ship', 'B2.png')
    return [], []


def build(only=None):
    if only: return {only: {'Avy_Ship': ship}[only]()}
    for pack in ('Avy_Town', 'Avy_Castle', 'Avy_Nature', 'Avy_Palm', 'Avy_Landmarks', 'Avy_Ship'):
        if os.path.isdir(OUT + pack): shutil.rmtree(OUT + pack)
    copy('Avy A3.png', 'Avy_Town', 'A3.png'); copy('Avy B.png', 'Avy_Town', 'B.png'); copy('Avy Ship.png', 'Avy_Town', 'B2.png')
    town = P.pack([s('Avy Window.png'), s('objec2.png'), s('object1.png'), s('object3.png'), s('church.png'),
                   s('Avy Rose.png'), s('cart.png'), s('world map1.png')], OUT + 'Avy_Town', first=3)
    castle_a4(); copy('Avy Castle2.png', 'Avy_Castle', 'B.png')
    castle = P.pack([s('tower.png'), s('gate.png', (0, 0, 9, 11)), s('gate.png', (0, 12, 9, 16)), s('gate.png', (0, 18, 9, 22)),
                     s('start.png')], OUT + 'Avy_Castle', first=2)
    a2('Avy_Nature', 'Avy tree autotile.png', sorted(CANOPIES.items()), 2)
    a2('Avy_Palm', 'Avy Palm Forest.png', list(zip(PALMS, range(9))), 3)
    for pack, kinds in (('Avy_Nature', CANOPIES), ('Avy_Palm', PALMS)):         # tree crowns block
        with open(OUT + pack + '/passage.json', 'w', encoding='utf8') as f: json.dump({'A2': {str(k): 'x' for k in kinds}}, f)
    copy('Water Cave.png', 'Avy_Nature', 'B.png')
    nature = P.pack([s('Avy Tree.png'), s('Avy Giant Tree.png', (0, 0, 7, 8)), s('Avy Giant Tree.png', (7, 0, 10, 3)),
                     s('Avy Palm Forest.png', (6, 0, 8, 9)), s('Avy tree autotile.png', (0, 3, 4, 5)), s('avy tree autotile2.png'),
                     *[s('Avy Lighthouse.png', (x, 0, x + 5, 13)) for x in (0, 5, 10, 15)], s('Avy Lighthouse.png', (0, 13, 8, 16))],
                    OUT + 'Avy_Nature', first=2)
    # parts of at most 15x16 (so each can clear tile 0 of its sheet), kept at full size so they line up again
    part = lambda f, x0, y0, x1, y1: (SRC + f, (x0, y0, x1, y1), True)
    big = [part(f, 0, y, 15, min(y + 16, 23)) for f in ('Avy Tower.png', 'Avy Tower2.png') for y in (0, 16)]
    big += [part('Avy premade.png', x, y, min(x + 15, 33), y + 16) for y in (0, 16) for x in (0, 15, 30)]
    landmarks = P.pack(big, OUT + 'Avy_Landmarks')
    characters()
    return {'Avy_Town': town, 'Avy_Castle': castle, 'Avy_Nature': nature, 'Avy_Landmarks': landmarks, 'Avy_Ship': ship()}


if __name__ == '__main__':
    for pack, (sheets, skipped) in build(sys.argv[1] if len(sys.argv) > 1 else None).items():
        for f, placed in sheets:
            print('%-10s %-7s %s' % (pack, f, ', '.join('%s %dx%d' % (n.split('.')[0], w, h) for n, x, y, w, h in placed)))
        for n, w, h in skipped: print('%-10s skipped %s (%dx%d tiles)' % (pack, n, w, h))
