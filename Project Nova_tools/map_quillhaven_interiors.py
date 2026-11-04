# Quillhaven's two working interiors (doors on Map031):
#   MAP039 - The Inkpot Inn: the lobby with the innkeeper's counter (rest for the night, the same inn event as the
#            Silver Swan), a dining room for students' families, and the guest beds.
#   MAP040 - Moonwell Apothecary: potions and remedies (the basic item shop) and rare draughts (the advanced one),
#            brewed in the back over a cauldron.
#   python map_quillhaven_interiors.py preview.png   -> preview images (preview_39.png, preview_40.png)
#   python map_quillhaven_interiors.py --save        -> write Map039 and Map040 (editor must be closed)
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from interior_kit import *
import nova_maplib as L
import kingdom as K
import data_ids as DI


def ext_obj(r, sheet, x, y, rows):
    for i, row in enumerate(rows):
        for c, n in enumerate(row):
            r.put(x + c, y + i, L.ext(sheet, n), 3 if i < len(rows) - 1 else 2)


# =========================================================================== The Inkpot Inn
def inn():
    W, H = 18, 15
    r = Room(W, H, *K.NAMES[K.QUILL_INN], floor=WOOD_B, walls='int_wood', ambient='#efe4d6')
    tx, ty = K.ARRIVE['inn_from_village'][1:3]
    assert ty == H - 2
    # the lobby (west) and the dining room (east), a wall with a doorway between them; the beds behind a second wall
    r.rect(9, 1, 9, H - 2, r.WT); r.rect(9, 8, 9, 9, WOOD_B)
    r.rect(10, 1, W - 2, 3, r.WF)
    r.counter(2, 6, 7, 6, TABLE_C)
    r.put(3, 6, BOOK_OPEN, 3); r.put(6, 6, VASE, 3); r.put(7, 6, CUP_TEA, 3)
    r.two(1, 2, CLOCK); r.two(7, 2, CABINET); r.put(4, 1, PORTRAIT_B); r.two(3, 2, FIREPLACE_BRICK)
    r.put(6, 1, WIN_MID[1]); r.put(2, 1, NOTICE)
    r.rect(2, 9, 7, 11, RUG_B)
    for x in (3, 6):
        r.put(x, 10, TABLE_ROUND); r.put(x, 10, TEAPOT if x == 3 else BREAKFAST, 3)
        r.put(x - 1, 10, CHAIR); r.put(x + 1, 10, CHAIR)
    r.put(1, H - 2, PLANT_B); r.put(8, H - 2, PLANT_A)
    # dining room: two long tables, ale and stew
    for y in (6, 10):
        r.counter(11, y, 15, y, TABLE_A)
        for x in range(11, 16):
            r.put(x, y - 1, CHAIR); r.put(x, y + 1, CHAIR)
        for x, t in zip(range(11, 16), (MUG_ALE, MEAL_MEAT, BOWL, PIE, MUG)): r.put(x, y, t, 3)
    r.put(12, 1, WIN_MID[1]); r.put(15, 1, WIN_MID[1]); r.two(16, 2, WINE_RACK)
    r.put(10, 2, BARREL); r.put(16, H - 2, BARREL); r.put(10, H - 2, POT_A)
    # guest beds along the back of the dining room's wall run
    r.two(13, 2, BED)
    r.exit_door(tx, *K.ARRIVE['village_from_inn'])
    r.keeper('Innkeeper', 4, 5, 'People1', 7, ('Innkeeper Maud:', 'Welcome to the Inkpot! Mind the ink stains,',
             'the students write on everything.'), common_event(DI.CE_INN))
    r.npc('Worried Mother', 12, 7, 'People1', 1, ('Worried Mother:', 'My son sits his Wards exam tomorrow.',
          'I brought him a lucky scarf. He says it\'s "embarrassing".'), direction=2)
    r.npc('Visiting Father', 14, 11, 'People3', 2, ('Visiting Father:', 'Thirty years ago I failed the entrance exam.',
          'Now my daughter is top of her class. I\'m not jealous. Not at all.'), direction=8)
    r.npc('Barmaid', 13, 8, 'People2', 5, ('Barmaid:', 'Stew\'s on. Ale\'s cold.', 'Don\'t let the professors tell you they don\'t drink here.'),
          move=1, freq=3)
    r.npc('Old Guest', 3, 11, 'People4', 3, ('Old Guest:', 'I came for my grandson\'s graduation.', 'That was four years ago. The beds are very comfortable.'),
          direction=6)
    return r


# =========================================================================== Moonwell Apothecary
def apothecary():
    W, H = 15, 13
    r = Room(W, H, *K.NAMES[K.QUILL_APOTHECARY], floor=COBBLE_O, walls='brick', ambient='#dfeadf')
    tx, ty = K.ARRIVE['apothecary_from_village'][1:3]
    assert ty == H - 2
    r.bgs = {'name': 'Fire1', 'pan': 0, 'pitch': 80, 'volume': 15}
    # shelves of jars and bottles along the back wall, the counter in front of them
    for x, pair in ((1, MEDICINE_SHELF), (2, SUNDRIES_B), (4, MEDICINE_SHELF), (10, MEDICINE_SHELF), (12, SUNDRIES_A), (13, MEDICINE_SHELF)):
        r.two(x, 2, pair)
    r.put(3, 2, SHELF_JARS); r.put(11, 2, SHELF_BOTTLES); r.put(7, 1, WIN_MID[1])
    r.put(5, 1, DRY_FLOWERS); r.put(9, 1, DRY_FLOWERS)
    r.counter(4, 5, 10, 5, TABLE_D)
    for x, t in ((4, POTION_RED), (5, MEDICINES), (6, OLD_BOOK_OPEN), (9, POTION_BLUE), (10, MEDICINE)): r.put(x, 5, t, 3)
    # the brewing corner: a cauldron from the Wizard Castle sheet, herbs and sacks
    ext_obj(r, 'WizardCastle_B', 11, 8, [(48, 49), (56, 57)])
    r.put(13, 8, SACKS); r.put(13, 9, SACK_A); r.put(10, 9, BASKET_GRAIN)
    r.put(1, 8, PLANTER); r.put(1, 9, PLANT_A); r.put(2, 10, CRYSTAL_TABLE); r.put(13, 11, PLANT_B); r.put(1, 11, POT_B)
    r.rect(5, 8, 9, 10, RUG_C)
    r.exit_door(tx, *K.ARRIVE['village_from_apothecary'])
    r.keeper('Apothecary', 7, 4, 'People4', 1, ('Apothecary Wren:', 'Moonwell Apothecary. Brewed on the full moon,',
             'bottled by hand. What ails you?'), choice_shop('Apothecary Wren', 'Potions for the road, or something rarer?',
                                                              [('Potions & remedies', DI.CE_ITEMS_BASIC), ('Rare draughts', DI.CE_ITEMS_ADV)]))
    r.npc('Apprentice', 12, 10, 'People2', 3, ('Apprentice:', 'Stir clockwise for healing, widdershins for poison.',
          'I wrote it on my hand. Twice.'), direction=8)
    r.look('Cauldron', 11, 9, ['A green brew bubbles quietly.', 'It smells of mint, moss and something like rain.'])
    return r


ROOMS = {K.QUILL_INN: inn, K.QUILL_APOTHECARY: apothecary}

if __name__ == '__main__':
    out = next((a for a in sys.argv[1:] if not a.startswith('--')), None)
    rooms = {mid: fn() for mid, fn in ROOMS.items()}
    if out:
        for mid, r in rooms.items(): r.render(out.replace('.png', '_%d.png' % mid), scale=0.5, grid='--grid' in sys.argv)
    if '--save' in sys.argv:
        for mid, r in rooms.items():
            r.save(mid, parent_id=K.ACADEMY, order=mid)
            print('saved Map%03d' % mid)
