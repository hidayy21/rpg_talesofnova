# Avy's ship, assembled: the bow (left half of Avy_Ship_B) and the stern (its right half from column 9, one row up)
# meet at the two staircases. The open deck inside the rails gets Avy's deck planks pixel by pixel, so no water
# shows through. The whole ship (15x13 tiles) becomes Avy_Ship_B3 - slot D of the "Avy Ship" tileset and an extra
# sheet for every map - and is moored at the end of the Harbor pier as The Morning Gull (bow at x 32; the stern runs
# past the east edge of the map, like the lighthouse; the pier boards under the hull are taken out).
#   python harbor_ship.py          -> preview in _work/
#   python harbor_ship.py --save   -> write the sheet, the tileset and Map006 (RPG Maker MV must be closed)
import json, os, sys
import numpy as np
from PIL import Image, ImageDraw
import compose_tileset as C
import nova_maplib as L

T = 48
HULL = C.PROJ + 'img/tilesets/Avy_Ship_B.png'
DECK = C.PROJ + 'additional asset 2 by avy/avy ship tile.png'
SHEET = 'Avy_Ship_B3'
TILESET = 'Avy Ship'
W, H = 15, 13                       # ship size in tiles
HARBOR, AT = 6, (32, 8)             # map, where the ship's top-left tile goes
DECKS = [[(0, 92), (95, 62), (278, 62), (278, 350), (95, 352), (0, 306)],     # bow, inside the rail (pixels)
         [(532, 40), (576, 40), (576, 300), (532, 300)]]                          # stern, beside the stern cabin
PIER = 19                           # Outside_B horizontal boards
LOOSE = {7, 130, 88, 89}            # spare pieces sharing those rows (two windows, a round railing), not the ship


def _tile(src, n):
    x, y = (n % 8 + (n // 128) * 8) * T, (n % 128 // 8) * T
    return src.crop((x, y, x + T, y + T))


def assemble():
    """The ship picture (W x H tiles) with its deck filled in."""
    src = Image.open(HULL).convert('RGBA')
    ship = Image.new('RGBA', (W * T, H * T), (0, 0, 0, 0))
    for r in range(12):                                   # bow: left half, rows 0-11, one row down
        for c in range(8):
            if r * 8 + c not in LOOSE: ship.alpha_composite(_tile(src, r * 8 + c), (c * T, (r + 1) * T))
    for r in range(13):                                   # stern: right half columns 9-15, rows 0-12
        for c in range(1, 8):
            if 128 + r * 8 + c not in LOOSE: ship.alpha_composite(_tile(src, 128 + r * 8 + c), ((7 + c) * T, r * T))
    # the deck: transparent pixels the sea cannot reach (gaps in the rails closed first) - between the stairs - plus
    # the bow and the stern deck, which the sheet leaves open (it expects a deck floor painted underneath)
    solid = np.array(ship.getchannel('A')) > 24
    closed = solid.copy()
    for dy in range(-3, 4):
        for dx in range(-3, 4): closed |= np.roll(np.roll(solid, dy, 0), dx, 1)
    sea = Image.fromarray(np.where(closed, 0, 255).astype('uint8'))
    sea = Image.fromarray(np.pad(np.array(sea), 1, constant_values=255)).copy()   # a copy: fromarray images are read-only
    ImageDraw.floodfill(sea, (0, 0), 128)
    outside = np.array(sea)[1:-1, 1:-1] == 128
    near = outside.copy()                                 # undo the closing: the sea reaches right up to the rails
    for dy in range(-3, 4):
        for dx in range(-3, 4): near |= np.roll(np.roll(outside, dy, 0), dx, 1)
    open_decks = Image.new('L', ship.size, 0)
    for poly in DECKS: ImageDraw.Draw(open_decks).polygon(poly, fill=255)
    middle = np.zeros(solid.shape, bool); middle[200:500, 280:536] = True            # the main deck, between the stairs
    deck_px = ~solid & ((~near & middle) | (np.array(open_decks) > 0))
    planks = Image.open(DECK).convert('RGBA').crop((0, 48, 96, 144))
    floor = Image.new('RGBA', ship.size)
    for y in range(0, ship.height, 96):
        for x in range(0, ship.width, 96): floor.paste(planks, (x, y))
    floor.putalpha(Image.fromarray((deck_px * 255).astype('uint8')))
    out = Image.new('RGBA', ship.size, (0, 0, 0, 0))
    out.alpha_composite(floor); out.alpha_composite(ship)
    return out


def to_n(x, y):
    """Ship tile (x, y), placed at the sheet's top left -> tile number on the sheet."""
    return (x // 8) * 128 + y * 8 + x % 8


def save():
    ship = assemble()
    sheet = Image.new('RGBA', (768, 768), (0, 0, 0, 0))
    sheet.paste(ship, (0, 0))
    assert not sheet.crop((0, 0, T, T)).getchannel('A').getbbox(), 'tile 0 must stay empty'
    sheet.save(C.PROJ + 'img/tilesets/%s.png' % SHEET)

    # the tileset (slot D) and NovaTilesetEx. Scenery for now: every tile blocks (open the deck with the Passage
    # tool once the story boards a ship - the rail posts between the decks would need to stay blocked)
    tilesets = C._read(C.PROJ + 'data/Tilesets.json')
    ts = next(t for t in tilesets if t and t['name'] == TILESET)
    ts['tilesetNames'][7] = SHEET
    first = C._first_id(7)
    ts['flags'][first:first + 256] = [0x10] + [0x0F] * 255
    with open(C.PROJ + 'data/Tilesets.json', 'w', encoding='utf8', newline='') as f: f.write(C._tilesets_text(tilesets))
    text, line, entry, slots = C._plugins()
    if SHEET not in slots:
        with open(C.PROJ + 'js/plugins.js', 'w', encoding='utf8', newline='') as f:
            f.write(C._plugins_with(text, line, entry, [('%s @ %d' % (SHEET, ts['id']), max(slots.values()) + 1)]))
        text, line, entry, slots = C._plugins()
    slot = slots[SHEET]

    # the Harbor: old ship tiles and the pier under the hull out, the assembled ship in (layer 2)
    mp = json.load(open(L.DATA + 'Map%03d.json' % HARBOR, encoding='utf8'))
    w, h, data = mp['width'], mp['height'], mp['data']
    ship_slots = {s for name, s in slots.items() if name.startswith('Avy_Ship_')}
    for y in range(h):
        for x in range(w):
            for z in (2, 3):
                t = data[(z * h + y) * w + x]
                if t >= L.EXT_BASE and (t - L.EXT_BASE) // L.EXT_SPAN in ship_slots: data[(z * h + y) * w + x] = 0
    for y in range(H):
        for x in range(W):
            mx, my = AT[0] + x, AT[1] + y
            if mx >= w: continue
            if data[(2 * h + my) * w + mx] == PIER: data[(2 * h + my) * w + mx] = 0
            if ship.crop((x * T, y * T, x * T + T, y * T + T)).getchannel('A').getbbox():
                data[(2 * h + my) * w + mx] = L.EXT_BASE + slot * L.EXT_SPAN + to_n(x, y)
    L.write_map(HARBOR, mp)
    print('%s saved, Harbor ship at %s (%d of %d columns on the map)' % (SHEET, AT, min(W, w - AT[0]), W))


if __name__ == '__main__':
    if '--save' in sys.argv:
        save()
    else:
        ship = assemble()
        os.makedirs(C.PROJ + 'Project Nova_tools/_work', exist_ok=True)
        bg = Image.new('RGBA', ship.size, (40, 110, 170, 255)); bg.alpha_composite(ship)
        bg.save(C.PROJ + 'Project Nova_tools/_work/avy_ship.png')
        print('preview: Project Nova_tools/_work/avy_ship.png')
