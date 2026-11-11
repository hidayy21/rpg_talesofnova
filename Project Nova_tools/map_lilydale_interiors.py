# Lilydale's rooms (doors on Map065, chapter 7):
#   MAP068 - Lantern & Lily, the tavern: the bar, the hearth, round tables, stairs up to the rooms. The innkeeper
#            sells a bed (the shared inn common event) and food and drink (the tavern shop).
#   MAP069 - Lantern & Lily, upstairs: a corridor with three guest rooms off it, like a village inn - the party's room
#            open, the other two taken.
#   MAP070 - Lilydale Chapel: pews, the altar, stained glass; a plaque for the lady of the villa, who was born here.
#   MAP071 - Thistle & Wick General Goods: the item shop (no weapons or armor in Lilydale).
#   MAP072-074 - the elders' houses: Henrik (by his fire), Marta (her granddaughter at home), Bram (his wife).
# Pots, barrels and crates marked as loot can be searched once each.
#   python map_lilydale_interiors.py preview.png [--grid]   -> preview images (preview_68.png, ...)
#   python map_lilydale_interiors.py --save                 -> write Map068-074 (editor must be closed)
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from interior_kit import *
import nova_maplib as L
import kingdom as K
import data_ids as DI
import compose_tileset as C
from map_moods import MOODS, set_tag
from map_frosthollow_interiors import (place, column, loot, NP, NB, PR, TAVERN_TABLE, SINGLE_BED, DOUBLE_BED,
                                       GOODS_SHELF, KITCHEN, POTION, HI_POTION, MAGIC_WATER)

AV3 = lambda n: L.ext('Avy_Town_B3', n)
PEW = ((244, 245), (252, 253))                                   # Avy_Town_B3: a bench seen from behind
GLASS = (192, 200)                                               # Avy_Town_B3: a stained-glass window, two tiles tall
ROOMS = {}


def reg(mid):
    def deco(fn):
        ROOMS[mid] = fn
        return fn
    return deco


def arrive(key):
    a = K.ARRIVE[key]
    return a[0], a[1], a[2], a[3]


# =========================================================================== the tavern (ground floor)
@reg(K.LILY_TAVERN)
def tavern():
    W, H = 19, 13
    r = Room(W, H, *K.NAMES[K.LILY_TAVERN], floor=WOOD_B, walls='wood', ambient='#f2dcc0')
    assert K.ARRIVE['lily_tavern_from_town'][1:3] == (9, H - 2)
    r.bgs = {'name': 'Fire1', 'pan': 0, 'pitch': 90, 'volume': 15}
    # --- behind the bar: wine, bottles, crockery, two casks
    r.two(1, 2, WINE_RACK); r.two(2, 2, BOTTLES_A); r.two(3, 2, BOTTLES_B); r.two(5, 2, DISH_CABINET)
    r.put(4, 1, WIN_SMALL[1]); r.put(7, 3, BARREL); r.put(8, 3, BARREL); r.put(6, 3, SACK_A)
    r.counter(1, 5, 8, 5, TABLE_A); r.counter(9, 3, 9, 5, TABLE_A)
    for x, t in ((2, MUG_ALE), (4, MUG_ALE), (6, BOTTLE), (8, CUPS)): r.put(x, 5, t, 3)
    r.put(9, 4, MUG, 3)
    for x in (2, 4, 6, 8): r.put(x, 6, STOOL_A)
    # --- the hearth, the notice board, a window; the stairs up in the corner
    r.wide(11, 1, FIREPLACE_L)
    r.put(10, 1, NOTICE); r.put(14, 1, WIN_MID[1])
    r.wide(16, 1, [(STAIRS_UP[3],), (STAIRS_UP[3],)])
    r.add_event('Stairs Up', 16, 2, [L.exit_page(*arrive('lily_inn_from_tavern'))])
    # --- round tables
    place(r, PR, 2, 8, TAVERN_TABLE); place(r, PR, 6, 9, TAVERN_TABLE); place(r, PR, 12, 5, TAVERN_TABLE)
    place(r, PR, 13, 9, TAVERN_TABLE)
    r.rect(8, 10, 10, 11, RUG_B)
    r.put(1, 11, PLANT_A); r.put(17, 11, PLANT_B); r.put(17, 5, BARREL)
    r.exit_door(9, *K.ARRIVE['lilydale_from_tavern'])
    loot(r, 'Cask', 17, 6, BARREL, POTION, 2, 'cask')
    r.look('Notice', 10, 3, ['\\C[6]ROOMS\\C[0] - ask at the bar.', 'Under it, in chalk: "No credit. Not even you, Bram."'])
    # --- people
    r.keeper('Innkeeper', 5, 4, 'People4', 3, ('Innkeeper Wynn:', 'Welcome to the Lantern & Lily. Rooms upstairs, ale down here,',
             'and both cheaper than they ought to be - nobody\'s travelling.'),
             choice_shop('Innkeeper Wynn', 'What\'ll it be?', [('A room for the night', DI.CE_INN), ('Food & drink', DI.CE_TAVERN)]))
    r.npc('Barmaid', 10, 8, 'People2', 5, ('Barmaid:', 'Stew\'s mostly turnip this week.',
          'The villa\'s cart used to bring the good flour, and a ham at harvest.'), move=1, freq=3)
    r.npc('Woodcutter', 5, 8, 'People4', 0, ('Woodcutter:', 'I cut on the edge of Hollow Wood. I don\'t go past the old oak now.',
          'The mist comes down to meet you there. Like it\'s been waiting.'), direction=4)
    r.npc('Bard', 15, 6, 'People1', 4, ('Bard:', 'I wrote a song about the lady of the villa once.',
          'The elders asked me not to sing it. Not because it was bad.', 'Because it was true.'), direction=4)
    r.npc('Old Soldier', 12, 9, 'People3', 6, ('Old Soldier:', 'Sixteen years since the war, and the lady died in it.',
          'They say the master of the villa never forgave the world.', 'I never forgave it either. I just had to keep living in it.'),
          direction=6)
    return r


# =========================================================================== upstairs: the inn's corridor and rooms
@reg(K.LILY_INN)
def inn_up():
    W, H = 19, 12
    r = Room(W, H, *K.NAMES[K.LILY_INN], floor=WOOD, walls='wood', ambient='#efdcc4')
    assert K.ARRIVE['lily_inn_from_tavern'][1:3] == (17, 8)
    # three rooms along the back (floor y 3-4), their front wall facing the corridor (top y 5, face y 6-7)
    for x in (6, 12): r.rect(x, 1, x, 4, r.WT)
    r.rect(16, 1, 17, 4, r.WT)
    r.rect(1, 5, 17, 5, r.WT); r.rect(1, 6, 17, 7, r.WF)
    # the party's room (west): two beds, a window, a chest of drawers
    column(r, NB, 1, 2, SINGLE_BED); column(r, NB, 4, 2, SINGLE_BED)
    r.put(2, 1, WIN_SMALL[1]); r.put(5, 3, DRESSER); r.put(2, 3, MINI_TABLE); r.put(2, 3, BOOK, 3)
    # the two taken rooms
    column(r, NB, 7, 2, SINGLE_BED); r.put(9, 1, WIN_SMALL[1]); r.put(10, 3, CRATE_B); r.put(11, 4, SACK_A)
    column(r, NB, 13, 2, SINGLE_BED); r.put(14, 1, WIN_SMALL[1]); r.put(15, 3, DRESSER)
    # doors from the corridor; the party's room opens, the others are taken
    r.door('Your Room', 3, 7, K.LILY_INN, 3, 4, d=8)
    r.cell(3, 5, WOOD)                                               # the doorway, seen from inside
    r.add_event('Doorway', 3, 5, [L.exit_page(K.LILY_INN, 3, 8, 2)])
    r.locked_door('Room 2', 9, 7, ['A snore comes through the door, deep as a cellar.'])
    r.locked_door('Room 3', 14, 7, ['A card on the door: "Do not disturb - Brother Aldo, pilgrim."',
                                    'Under it, in another hand: "He\'s been here eleven days."'])
    # the stairs down at the end of the corridor
    r.put(17, 6, STAIRS_DOWN[3]); r.put(17, 7, STAIRS_DOWN[3])
    r.add_event('Stairs Down', 17, 7, [L.exit_page(*arrive('lily_tavern_from_inn'))])
    # the corridor: a runner, flowers, a lamp table
    r.rect(1, 9, 15, 9, RUG_B)
    r.put(6, 10, FLOWER_TABLE); r.put(12, 10, MINI_TABLE); r.put(12, 10, VASE, 3); r.put(1, 10, PLANT_A)
    r.look('Bed', 1, 4, ['Your room for the night. The sheets smell of lavender and woodsmoke.'])
    r.npc('Maid', 9, 9, 'People2', 5, ('Maid:', 'Your room\'s the first on the left. Fresh sheets.',
          'The pilgrim in the end room hasn\'t come out in days. I leave his tray by the door.'), move=1, freq=2)
    return r


# =========================================================================== the chapel
@reg(K.LILY_CHAPEL)
def chapel():
    W, H = 15, 15
    r = Room(W, H, *K.NAMES[K.LILY_CHAPEL], floor=STONE, walls='temple', ambient='#e6e2ee')
    assert K.ARRIVE['lily_chapel_from_town'][1:3] == (7, H - 2)
    r.bgm = {'name': 'Theme4', 'pan': 0, 'pitch': 90, 'volume': 45}
    # stained glass along the back wall, the altar, candle pillars
    for x in (2, 5, 9, 12): r.put(x, 1, AV3(GLASS[0])); r.put(x, 2, AV3(GLASS[1]))
    r.counter(6, 4, 8, 4, TABLE_D)
    r.put(6, 4, VASE, 3); r.put(7, 4, OLD_BOOK_OPEN, 3); r.put(8, 4, VASE, 3)
    for x in (4, 10): r.two(x, 3, PILLAR)
    # the plaque for the lady of the villa, fresh roses under it
    r.put(1, 2, NOTICE); r.put(1, 3, FLOWER_TABLE)
    # pews, an aisle down the middle
    for y in (6, 8, 10):
        for x in (2, 4, 9, 11):
            for c in range(2):
                r.put(x + c, y, AV3(PEW[0][c]), 3); r.put(x + c, y + 1, AV3(PEW[1][c]))
    r.rect(6, 5, 8, 12, RUG_E)
    r.put(1, 12, PLANT_B); r.put(13, 12, PLANT_B)
    r.exit_door(7, *K.ARRIVE['lilydale_from_chapel'])
    r.look('Plaque', 1, 3, ['A small brass plaque, polished bright:',
                           '"For our daughter, who married the quiet gentleman of the hill.',
                           'Lilydale remembers. Every spring, the bell."',
                           'Under it, roses - fresh, and so dark a red they are nearly black.',
                           'Nobody in the village grows roses like these.'])
    r.look('Altar', 7, 4, ['The book on the altar is open at the prayer for those who are far away.'])
    r.look('Bell Rope', 13, 3, ['A rope hangs down from the tower.', 'You decide not to pull it.'])
    loot(r, 'Pot', 13, 11, POT_A, MAGIC_WATER, 1, 'pot')
    r.npc('Priestess', 7, 3, 'People2', 2, ('Priestess:', 'We still ring the bell for the lady of the villa, every spring.',
          'Someone from the house always came to hear it.', 'This spring, nobody came. But the roses were left all the same.'))
    r.npc('Old Widow', 7, 9, 'People1', 7, ('Old Widow:', '...', 'I\'m praying for the villa folk. Somebody ought to.'),
          direction=8)
    return r


# =========================================================================== the item shop
@reg(K.LILY_STORE)
def store():
    W, H = 16, 12
    r = Room(W, H, *K.NAMES[K.LILY_STORE], floor=WOOD, walls='wood', ambient='#efe6da')
    assert K.ARRIVE['lily_store_from_town'][1:3] == (8, H - 2)
    place(r, NP, 1, 1, GOODS_SHELF)
    r.two(4, 2, MEDICINE_SHELF); r.two(5, 2, SUNDRIES_A); r.two(6, 2, SUNDRIES_A2)
    r.put(8, 1, WIN_MID[1])
    r.two(10, 2, SUNDRIES_B); r.two(11, 2, MEDICINE_SHELF); r.two(13, 2, CLOSET)
    r.counter(4, 5, 10, 5, TABLE_D)
    for x, t in ((4, POTION_RED), (5, MEDICINES), (7, BASKET), (9, POTION_BLUE), (10, MEDICINE)): r.put(x, 5, t, 3)
    r.rect(6, 7, 10, 9, RUG_C)
    r.put(13, 7, SACKS); r.put(14, 7, CRATE_GRAIN); r.put(13, 8, BASKET_APPLE); r.put(1, 6, BARREL); r.put(1, 7, SACK_A)
    r.put(14, 10, PLANT_A); r.put(1, 10, PLANT_B)
    r.exit_door(8, *K.ARRIVE['lilydale_from_store'])
    loot(r, 'Crate', 14, 8, CRATE_C, POTION, 2, 'crate')
    r.keeper('Shopkeeper', 7, 4, 'People1', 4, ('Shopkeeper Tilda:', 'Thistle & Wick - herbs, tonics, candles...',
             'Well. No candles. No lamp oil, no wicks. Half the name\'s a lie this month.'),
             choice_shop('Shopkeeper Tilda', 'What do you need?', [('Potions & remedies', DI.CE_ITEMS_BASIC),
                                                                   ('Rare goods', DI.CE_ITEMS_ADV)]))
    r.npc('Customer', 12, 9, 'People2', 3, ('Customer:', 'I came for lamp oil. Tilda says the villa\'s chandler',
          'used to bring it down. Now we sit in the dark by nine.'), direction=4)
    return r


# =========================================================================== the elders' houses
def home(mid, walls, floor, back_key, bed, people, keepsake):
    W, H = 13, 10
    r = Room(W, H, *K.NAMES[mid], floor=floor, walls=walls, ambient='#f0e2cc')
    r.wide(1, 1, FIREPLACE_L)
    r.put(5, 1, WIN_SMALL[1]); r.two(7, 2, CABINET); r.two(8, 2, BOOKSHELF_A)
    if bed == 'double': place(r, NB, 10, 1, DOUBLE_BED)
    else: column(r, NB, 11, 2, SINGLE_BED); r.put(10, 3, DRESSER)
    r.rect(2, 5, 5, 6, RUG_A)
    r.put(3, 5, TABLE_ROUND); r.put(4, 5, TABLE_ROUND); r.put(3, 5, TEAPOT, 3); r.put(4, 5, CUP_TEA, 3)
    r.two(2, 4, CHAIR_A); r.put(5, 5, STOOL_A)
    r.put(1, 7, BARREL); r.put(11, 7, PLANT_A); r.put(11, 6, POT_B)
    r.exit_door(6, *K.ARRIVE[back_key])
    kx, ky, lines = keepsake
    if mid == K.LILY_MARTA: r.put(kx, ky, BASKET)
    r.look('Keepsake', kx, ky, lines)
    for p in people: r.npc(*p)
    return r


@reg(K.LILY_HENRIK)
def henrik():
    return home(K.LILY_HENRIK, 'int_wood', WOOD, 'lilydale_from_henrik', 'single', [
        ('Old Henrik', 3, 3, 'People4', 6, ('Old Henrik:', 'The Bloodroses? Good neighbours, once.',
         'Then the war took the lady, and the master shut his doors.', 'Sixteen years. He never came down again.'), 2)],
        (2, 1, ['On the mantel, a little wooden horse, worn smooth.',
                'Henrik: "A boy from the villa carved that for me. Sixty years ago, near enough.',
                'Still the best carving in the house. Don\'t tell my son-in-law."']))


@reg(K.LILY_MARTA)
def marta():
    return home(K.LILY_MARTA, 'plaster_e', WOOD_B, 'lilydale_from_marta', 'double', [
        ('Granddaughter', 4, 7, 'People1', 3, ('Marta\'s Granddaughter:', 'Gran\'s out by the well again, watching the north road.',
         'She says Hanna from the villa always came that way, with her basket.'), 8)],
        (5, 4, ['A wicker basket, a blue cloth folded inside.',
                '"HANNA" is stitched on the cloth.', 'She left it here on the last market day, meaning to come back for it.']))


@reg(K.LILY_BRAM)
def bram():
    return home(K.LILY_BRAM, 'log', WOOD, 'lilydale_from_bram', 'double', [
        ('Bram\'s Wife', 9, 6, 'People2', 7, ('Bram\'s Wife:', 'He\'s at the rose tree again, isn\'t he.',
         'Sixty years he\'s been sitting under it. Waiting for a boy who stopped coming.'), 4)],
        (6, 2, ['Notches cut into the doorframe, each with a name: the heights of children, long grown.',
                'The lowest notch has no name. Just a small carved rose.']))


if __name__ == '__main__':
    out = next((a for a in sys.argv[1:] if not a.startswith('--')), None)
    rooms = {mid: fn() for mid, fn in ROOMS.items()}
    if out:
        for mid, r in rooms.items(): r.render(out.replace('.png', '_%d.png' % mid), scale=1, grid='--grid' in sys.argv)
    if '--save' in sys.argv:
        for mid, r in rooms.items():
            r.save(mid, parent_id=K.LILYDALE, order=mid)
            path = L.DATA + 'Map%03d.json' % mid                 # the mood tags (map_moods.py) go back on
            m = C._read(path)
            for tag, value in MOODS.get(mid, {}).items(): m['note'] = set_tag(m['note'], tag, value)
            open(path, 'w', encoding='utf8', newline='').write(C._map_text(m))
            print('saved Map%03d' % mid)
