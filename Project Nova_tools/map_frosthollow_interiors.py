# Frosthollow's working interiors (doors on Map042; chapter 5, the border town):
#   MAP043 - Hearthfire Inn: a log hall round a festival hearth hung with stockings, the innkeeper's counter and
#            kitchen, tavern tables, and the guest room behind a partition. Rest = the shared inn common event.
#   MAP044 - Frosthollow General Store: goods shelves, furs and cloth for the cold, potions on the counter.
#            Shop = the basic and advanced item shops.
#   MAP045 - Hilda's Forge: the forge and anvils, a weapons counter and an armor counter. What they sell is decided
#            later: set WEAPON_SHOPS / ARMOR_SHOPS below to the shop common events and rebuild.
# Pots, barrels and crates marked as loot can be searched once each (self switch A) for potions.
#   python map_frosthollow_interiors.py preview.png [--grid]   -> preview images (preview_43.png, ...)
#   python map_frosthollow_interiors.py --save                 -> write Map043-045 (editor must be closed)
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from interior_kit import *
import nova_maplib as L
import kingdom as K
import data_ids as DI

WEAPON_SHOPS = []        # e.g. [('Swords & spears', DI.CE_WEAPONS[1])] - goods still to be decided
ARMOR_SHOPS = []         # e.g. [('Armor & shields', DI.CE_ARMOR[1])]

X = lambda n: L.ext('PM_XmasDecoration', n)
NP = lambda n: L.ext('Nova_InsideProps', n)
NB = lambda n: L.ext('Nova_Beds', n)
PR = lambda n: L.ext('PM_Rooms', n)
NI = lambda n: L.ext('PM_NobleInterior', n)
XMAS_HEARTH = ((130, 131, 132), (138, 139, 140), (146, 147, 148))      # 3x3: mantel with garland, fire, hearth
XMAS_WINDOW = ((154, 155), (162, 163))                                  # 2x2 window with red curtains
GARLAND_WINDOW = ((156, 157), (164, 165))                               # the same with a garland and a teddy
POTTED_TREE = (112, 120)                                                # little decorated tree in a pot
SINGLE_BED, DOUBLE_BED = (8, 16, 24), ((9, 10), (17, 18), (25, 26))     # Nova_Beds, headboard on the wall row
GOODS_SHELF = ((130, 131), (138, 139), (146, 147))                      # Nova_InsideProps: 2x3 shelf of wares
KITCHEN = ((40, 48), (41, 49), (42, 50))                                # stove, sink, worktop (top, front)
TAVERN_TABLE = ((217, 218, 219), (225, 226, 227))                       # PM_Rooms: round table with stools
KNIGHT, BANNER = (246, 254), (247, 255)                                 # PM_NobleInterior: armor stand, banner
SMITH = '!$PM_Blacksmith'                                               # object sheet: (direction, pattern)
SMITH_HOOD_T, SMITH_HOOD_B, SMITH_FIRE, SMITH_FIRE2 = (4, 0), (6, 0), (8, 0), (8, 1)
SMITH_ANVIL, SMITH_ANVIL2, SMITH_HAMMERS, SMITH_BUCKET = (4, 1), (6, 2), (4, 2), (8, 2)
POTION, HI_POTION, MAGIC_WATER = 1, 5, 2
ITEM_NAMES = {POTION: 'Potion', HI_POTION: 'Hi-Potion', MAGIC_WATER: 'Magic Water'}


def place(r, f, x, y, rows, floor_row=None):
    """Multi-tile object; the bottom row is on the ground layer (2), the rows above on the upper layer (3)."""
    for i, row in enumerate(rows):
        for c, n in enumerate(row):
            r.put(x + c, y + i, f(n), 2 if i == len(rows) - 1 else 3)


def column(r, f, x, y, ids):
    place(r, f, x, y, [(n,) for n in ids])


def smith_obj(r, name, x, y, frame, lines=None):
    d, p = frame
    return r.add_event(name, x, y, [page(char(SMITH, 0, d, p), commands=text(*lines) if lines else None,
                                         walk_anim=False, dir_fix=True, priority=1)])


def loot(r, name, x, y, tile, item, n, where):
    """A pot / barrel / crate to search once: the item goes to the party, then it is empty (self switch A)."""
    found = [cmd(250, [{'name': 'Item3', 'volume': 80, 'pitch': 100, 'pan': 0}]), cmd(126, [item, 0, 0, n]),
             *text('Found %d \\C[6]%s\\C[0] in the %s!' % (n, ITEM_NAMES[item], where)), cmd(123, ['A', 0])]
    return r.add_event(name, x, y, [page(L.tile_image(tile), commands=found, priority=1),
                                     page(L.tile_image(tile), commands=text('The %s is empty.' % where), priority=1,
                                          cond={'selfSwitchValid': True, 'selfSwitchCh': 'A'})])


def shop_or_wait(speaker, prompt, shops, wait_line):
    return choice_shop(speaker, prompt, shops) if shops else say(speaker, wait_line)


# =========================================================================== Hearthfire Inn
def inn():
    W, H = 24, 15
    r = Room(W, H, *K.NAMES[K.FROST_INN], floor=WOOD_B, walls='log', ambient='#f2e2cc')
    tx, ty = K.ARRIVE['frost_inn_from_town'][1:3]
    assert ty == H - 2
    r.bgs = {'name': 'Fire1', 'pan': 0, 'pitch': 90, 'volume': 20}
    # --- the back wall of the hall: clock, window, kitchen, the festival hearth, a garland window, wine
    r.two(1, 2, CLOCK)
    place(r, X, 2, 1, XMAS_WINDOW)
    for i, (top, front) in enumerate(KITCHEN):
        r.put(4 + i, 2, NP(top), 2); r.put(4 + i, 3, NP(front), 2)
    place(r, X, 9, 1, XMAS_HEARTH)
    place(r, X, 13, 1, GARLAND_WINDOW)
    r.two(16, 2, WINE_RACK); r.put(15, 1, X(59))                       # wreath beside the window
    r.put(7, 1, X(59)); r.put(12, 1, X(59))
    # --- the innkeeper's counter (L-shaped, so the kitchen stays behind it)
    r.counter(1, 5, 6, 5, TABLE_C); r.counter(7, 3, 7, 5, TABLE_C)
    r.put(2, 5, BOOK_OPEN, 3); r.put(5, 5, CUP_TEA, 3); r.put(7, 4, VASE, 3); r.put(6, 5, MUG_ALE, 3)
    # --- by the hearth: rug, two chairs, the inn's cat asleep on the warm stones
    r.rect(8, 4, 12, 6, RUG_D)
    r.two(8, 4, CHAIR_A); r.two(12, 4, CHAIR_A)                       # whole chairs: backrest over the seat
    r.put(10, 4, L.ext('PM_Extras', 152))
    # --- tavern tables, a long supper table
    place(r, PR, 8, 8, TAVERN_TABLE); place(r, PR, 13, 8, TAVERN_TABLE)
    r.counter(2, 10, 5, 10, TABLE_A)
    for x in range(2, 6): r.two(x, 8, CHAIR_A); r.put(x, 11, STOOL_A)   # chairs behind the table, stools in front
    for x, t in zip(range(2, 6), (MEAL_MEAT, BOWL, PIE, MUG_ALE)): r.put(x, 10, t, 3)
    column(r, X, 15, 11, POTTED_TREE); r.put(9, 13, PLANT_A); r.put(13, 13, PLANT_B); r.put(1, 13, POT_B)
    # --- the guest room behind the partition (doorway at y 7-8)
    r.rect(17, 1, 17, H - 2, r.WT); r.rect(17, 7, 17, 8, WOOD_B)
    for x in (18, 20, 22): column(r, NB, x, 2, SINGLE_BED)
    r.two(19, 2, DRAWERS); r.two(21, 2, CABINET)
    r.rect(18, 8, 22, 10, RUG_B)
    r.put(20, 9, MINI_TABLE); r.put(20, 9, BOOK, 3)
    column(r, X, 22, 6, POTTED_TREE)
    r.exit_door(tx, *K.ARRIVE['town_from_frost_inn'])
    # --- loot
    loot(r, 'Barrel', 16, 12, BARREL, POTION, 2, 'barrel')
    loot(r, 'Crate', 18, 12, CRATE_B, POTION, 1, 'crate')
    loot(r, 'Pot', 22, 12, POT_A, HI_POTION, 1, 'pot')
    # --- people
    r.keeper('Innkeeper', 3, 4, 'People4', 1, ('Innkeeper Astrid:', 'Welcome to the Hearthfire! Shake the snow off,',
             'there\'s a bed and a bowl of stew for every traveller tonight.'), common_event(DI.CE_INN))
    r.npc('Barmaid', 11, 10, 'People2', 5, ('Barmaid:', 'Spiced cider, two coppers. Stew, three.',
          'Festival songs are free - whether you want them or not.'), move=1, freq=3)
    r.npc('Off-duty Soldier', 7, 9, 'People3', 6, ('Off-duty Soldier:', 'Three weeks on the north wall and not one raider.',
          'Then I take one night off and they say the pass is crawling with them.'), direction=6)
    r.npc('Traveling Merchant', 15, 9, 'People1', 4, ('Traveling Merchant:', 'The pass is closed, so here I sit, selling nothing.',
          'Still - this is the best stew between here and the capital.'), direction=4)
    r.npc('Old Trapper', 4, 9, 'People4', 6, ('Old Trapper:', 'Wolves came down off the ridge early this year.',
          'Something up north is scaring them. And it takes a lot to scare a wolf.'), direction=2)
    return r


# =========================================================================== Frosthollow General Store
def store():
    W, H = 16, 13
    r = Room(W, H, *K.NAMES[K.FROST_STORE], floor=WOOD, walls='wood', ambient='#efe6da')
    tx, ty = K.ARRIVE['frost_store_from_town'][1:3]
    assert ty == H - 2
    # --- shelves along the back wall: wares, medicine, sundries, bread, a window, coats and crockery
    place(r, NP, 1, 1, GOODS_SHELF)
    r.two(4, 2, MEDICINE_SHELF); r.two(5, 2, SUNDRIES_A); r.two(6, 2, BREAD_SHELF)
    place(r, X, 8, 1, XMAS_WINDOW)
    r.two(10, 2, SUNDRIES_B); r.two(11, 2, SUNDRIES_A2)
    r.two(13, 2, CLOSET); r.two(14, 2, DISH_CABINET)
    r.put(3, 1, X(59))
    # --- the counter
    r.counter(4, 5, 10, 5, TABLE_D)
    for x, t in ((4, POTION_RED), (5, MEDICINES), (6, BASKET_BREAD), (9, POTION_BLUE), (10, MEDICINE)): r.put(x, 5, t, 3)
    # --- winter goods on the floor
    r.rect(5, 8, 10, 10, RUG_C)
    r.put(13, 8, SACKS); r.put(14, 8, NP(57)); r.put(13, 9, BASKET_APPLE); r.put(14, 9, CRATE_GRAIN)
    r.put(1, 7, BARREL); r.put(2, 7, BARREL); r.put(1, 8, SACK_A)
    column(r, X, 1, 9, POTTED_TREE); r.put(12, 11, PLANT_A)
    r.exit_door(tx, *K.ARRIVE['town_from_frost_store'])
    # --- loot
    loot(r, 'Crate', 1, 11, CRATE_C, POTION, 2, 'crate')
    loot(r, 'Pot', 14, 11, POT_B, MAGIC_WATER, 1, 'pot')
    # --- people
    r.keeper('Shopkeeper', 7, 4, 'People1', 4, ('Shopkeeper Olaf:', 'Frosthollow General! Potions, rope, lamp oil,',
             'and enough wool socks to bury a mule.'), choice_shop('Shopkeeper Olaf', 'What can I get you for the cold?',
                                                                   [('Potions & remedies', DI.CE_ITEMS_BASIC), ('Rare goods', DI.CE_ITEMS_ADV)]))
    r.npc('Hunter', 12, 7, 'People4', 0, ('Hunter:', 'Fur prices doubled since the pass closed.',
          'Olaf says it\'s the war. I say it\'s Olaf.'), direction=4)
    r.npc('Child', 9, 9, 'People1', 0, ('Child:', 'Mama sent me for candles.', 'I\'m buying sweets. She doesn\'t need to know.'),
          move=1, freq=3)
    return r


# =========================================================================== Hilda's Forge
def smithy():
    W, H = 18, 13
    r = Room(W, H, *K.NAMES[K.FROST_SMITHY], floor=COBBLE_O, walls='stone', ambient='#f0d8c0')
    tx, ty = K.ARRIVE['frost_smithy_from_town'][1:3]
    assert ty == H - 2
    r.bgs = {'name': 'Fire2', 'pan': 0, 'pitch': 100, 'volume': 25}
    # --- the forge in the back-left corner: hood over the fire, two fire pits, anvils, the quench bucket
    smith_obj(r, 'Forge Hood', 2, 2, SMITH_HOOD_T); smith_obj(r, 'Forge Hood', 2, 3, SMITH_HOOD_B)
    smith_obj(r, 'Forge', 1, 3, SMITH_FIRE, ['The forge glows orange-white.', 'Even from here it warms your face.'])
    smith_obj(r, 'Forge', 3, 3, SMITH_FIRE2, ['The coals tick and settle.'])
    smith_obj(r, 'Anvil', 2, 6, SMITH_ANVIL, ['A heavy anvil, its face polished by a thousand blows.'])
    smith_obj(r, 'Anvil', 4, 8, SMITH_ANVIL2, ['A second anvil, for the apprentice.'])
    smith_obj(r, 'Hammers', 1, 8, SMITH_HAMMERS); smith_obj(r, 'Quench Bucket', 1, 6, SMITH_BUCKET)
    r.put(3, 9, SCRAP); r.put(1, 10, BASIN_L); r.put(4, 10, HAMMERS, 3); r.put(4, 10, MINI_TABLE)
    # --- the weapons side: swords and spears racked on the wall, the counter in front
    r.two(5, 2, REPO_SWORDS); r.two(6, 2, REPO_SPEARS); r.two(8, 2, REPO_SWORDS)
    r.put(7, 1, WALL_SWORDS_X); r.put(5, 1, WALL_SWORDS); r.put(8, 1, WALL_SWORDS)
    r.counter(5, 6, 8, 6, TABLE_B)
    r.put(5, 6, SWORD, 3); r.put(8, 6, KNIVES, 3)
    r.put(9, 3, SWORD_RACK_A); r.put(9, 4, BOWS)
    # --- the armor side: armor stands, shields and helmets, a knight's harness and the house banner
    place(r, NI, 11, 1, [(BANNER[0],), (BANNER[1],)])
    for x, t in zip((12, 13, 14), ARMOR_STANDS): r.put(x, 3, t)
    r.put(12, 1, WALL_SHIELD); r.put(14, 1, WALL_SHIELD); r.put(13, 2, SHIELD_A); r.put(15, 2, SHIELD_B)
    column(r, NI, 16, 2, KNIGHT)
    r.counter(11, 6, 14, 6, TABLE_B)
    for x, t in zip((11, 12, 14), HELMETS): r.put(x, 6, t, 3)
    r.rect(6, 8, 12, 10, RUG_A)
    for dx, (top, bottom) in enumerate(((226, 234), (227, 235))):      # Inside_B crate stack, 2x2
        r.put(15 + dx, 5, top, 3); r.put(15 + dx, 6, bottom)
    r.exit_door(tx, *K.ARRIVE['town_from_frost_smithy'])
    # --- loot
    loot(r, 'Barrel', 16, 11, BARREL, POTION, 1, 'barrel')
    loot(r, 'Crate', 13, 11, CRATE_B, POTION, 2, 'crate')
    # --- people (the goods are decided later: see WEAPON_SHOPS / ARMOR_SHOPS at the top)
    r.keeper('Weaponsmith', 7, 5, 'People4', 6, ('Smith Bjorn:', 'Hilda\'s forge. She\'s out at the festival,',
             'so you get her brother. I bend steel just as well.'),
             shop_or_wait('Smith Bjorn', 'Blades or spears?', WEAPON_SHOPS,
                          'The new batch is still cooling. Come back when the pass opens - I\'ll have steel for you then.'))
    r.keeper('Armorer', 13, 5, 'People4', 5, ('Armorer Sigrun:', 'Mail, plate, shields. Everything a border needs.'),
             shop_or_wait('Armorer Sigrun', 'What do you need covered?', ARMOR_SHOPS,
                          'The garrison bought out my stock this morning. I\'m fitting new pieces - check back soon.'))
    r.npc('Apprentice', 3, 7, 'People4', 0, ('Apprentice:', 'Pump the bellows, fetch the coal, sweep the scale...',
          'One day I\'ll get to hit something.'), direction=4)
    return r


ROOMS = {K.FROST_INN: inn, K.FROST_STORE: store, K.FROST_SMITHY: smithy}

if __name__ == '__main__':
    out = next((a for a in sys.argv[1:] if not a.startswith('--')), None)
    rooms = {mid: fn() for mid, fn in ROOMS.items()}
    if out:
        for mid, r in rooms.items(): r.render(out.replace('.png', '_%d.png' % mid), scale=1, grid='--grid' in sys.argv)
    if '--save' in sys.argv:
        for mid, r in rooms.items():
            r.save(mid, parent_id=K.FROSTHOLLOW, order=mid)
            print('saved Map%03d' % mid)
