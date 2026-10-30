# MAP004 - Market District: four specialist shops on the north side, an open-air market of tent stalls below.
import sys
sys.path.insert(0, 'D:/RPG Maker MV/Project Nova_tools')
from town_kit import *
from nova_maplib import cmd, text, say, page, char, common_event
import kingdom as K
import data_ids as DI

W, H = 46, 32
m = Town(W, H, K.NAMES[K.MARKET][0], K.NAMES[K.MARKET][1], ground=COBBLE)
m.bgm = {'name': 'Town1', 'pan': 0, 'pitch': 100, 'volume': 80}
m.bgs = {'name': 'City', 'pan': 0, 'pitch': 100, 'volume': 55}
P = PROP

# ---------------------------------------------------------------- shop row (roofs run off the top)
# Ironhart Arms - weapon shop
m.building(1, 9, 0, 3, 7, 'khaki', 'stone', windows=False)
for x in (2, 8): m.put(x, 5, WIN); m.put(x, 7, WIN)
m.put(4, 7, LG_TOP); m.put(4, 8, LG_BOT); m.put(6, 7, LG_TOP); m.put(6, 8, LG_BOT)
m.put(5, 8, SIGN['sword']); m.put(3, 1, CHIMNEY_B)
for x, t in ((2, P['sword_rack_a']), (3, P['spears']), (7, P['axes']), (8, P['sword_rack_b'])): m.put(x, 10, t)
m.put(1, 10, BARREL); m.put(9, 10, P['bows'])
# Bulwark & Thread - armor shop
m.building(11, 19, 0, 3, 7, 'red', 'brickstone', windows=False)
for x in (12, 14, 16, 18): m.put(x, 5, WIN_FLOWER_P)
m.put(13, 7, LG_TOP); m.put(13, 8, LG_BOT); m.put(17, 7, LG_TOP); m.put(17, 8, LG_BOT)
m.put(15, 7, SIGN['armor_shield'])
for x, t in ((11, P['armor_stand_a']), (12, P['armor_stand_b']), (18, P['armor_stand_c']), (19, P['armor_stand_d'])): m.put(x, 10, t)
m.put(13, 10, P['shield_a']); m.put(17, 10, P['helmet_a'])
# alley (north exit to the Residential Quarter's back street)
m.rect(20, 0, 22, 9, COBBLE)
m.put(20, 3, CRATE); m.put(22, 6, BARREL)
# The Starlit Grimoire - magic shop
m.building(23, 31, 0, 3, 7, 'dressed', 'white', windows=False)
for x in (24, 26, 28, 30): m.put(x, 5, MID_WIN)
m.put(25, 7, STAINED); m.put(29, 7, STAINED)
m.put(27, 7, SIGN['magic'])
m.tall(23, 6, BANNER_BLUE); m.tall(31, 6, BANNER_BLUE)
for x, t in ((24, P['potion_blue']), (25, P['crystal_table']), (29, P['scrolls_a']), (30, P['potion_red'])): m.put(x, 10, t)
# Whisker & Paw - pet shop
m.building(33, 41, 0, 3, 7, 'green', 'wood', windows=False)
for x in (34, 36, 38, 40): m.put(x, 5, WIN_FLOWER_G)
m.put(35, 7, LG_TOP); m.put(35, 8, LG_BOT); m.put(39, 7, LG_TOP); m.put(39, 8, LG_BOT)
m.put(37, 7, SIGN['blank'])
# animal pen with a wooden fence
m.rect(42, 0, 45, 13, GRASS)
m.rect(42, 4, 45, 4, FENCE, layer=1); m.rect(42, 4, 42, 13, FENCE, layer=1)
m.put(44, 6, HAY); m.put(45, 8, HAY); m.put(43, 12, P['bowl']); m.put(45, 11, BUCKET)

# ---------------------------------------------------------------- main street y14..17, kerb stones and lamps
for x in (5, 15, 27, 37): m.lamp(x, 13)

# ---------------------------------------------------------------- open-air market (y19..31)
m.rect(0, 19, 45, 31, COB_E)
m.rect(0, 19, 45, 19, COBBLE)
# rows of tent stalls with their wares laid out in front
stalls = [  # (x, y, wares-in-front, kind)
    (2, 20, ('crate_apples', 'crate_oranges', 'basket_apples'), 'fruit'),
    (7, 20, ('crate_greens', 'basket_grain', 'crate_grain'), 'veg'),
    (12, 20, ('basket_bread', 'pie', 'basket_bread'), 'bread'),
    (28, 20, ('jewel_case_a', 'necklace', 'jewel_case_b'), 'jewel'),
    (33, 20, ('mens_clothes', 'robe_a', 'cape_stand'), 'cloth'),
    (38, 20, ('sacks_b', 'sack_a', 'sacks_c'), 'spice'),
    (2, 26, ('medicine_a', 'medicine_b', 'medicine_c'), 'herbs'),
    (7, 26, ('doll_bear', 'gifts', 'doll_blue'), 'toys'),
    (33, 26, ('pot', 'basin', 'pot'), 'pottery'),
    (38, 26, ('roast', 'side_dish', 'roast_pig'), 'food'),
]
for x, y, wares, kind in stalls:
    m.tent(x, y)
    # wares on either side of the tent's opening; the middle stays free so the stall keeper can be reached
    for i, w in ((0, wares[0]), (2, wares[2])):
        tile = {'pot': POT, 'basin': BASIN}.get(w) or P[w]
        m.put(x + i, y + 3, tile)
    mid = {'pot': POT, 'basin': BASIN}.get(wares[1]) or P[wares[1]]
    m.put(x - 1 if x > 2 else x + 3, y + 3, mid)
# centre of the market: the old well and a ring of benches (stepping stones) under two trees
m.rect(18, 21, 26, 29, COBBLE)
m.put(22, 24, WELL)
m.big_tree(18, 22); m.big_tree(25, 22); m.big_tree(18, 27, BIG_TREE2); m.big_tree(25, 27, BIG_TREE2)
for x in (20, 24): m.put(x, 26, STEPPING)
m.put(22, 28, FLOWERS[0]); m.put(21, 21, FLOWERS[2]); m.put(23, 21, FLOWERS[3])
# crates and carts along the edges
for x, y, t in ((0, 20, CRATE_L_T), (0, 21, CRATE_L_B), (44, 20, BARREL), (45, 20, BARREL), (44, 30, CRATE),
                (13, 30, CRATE_APPLE), (31, 30, CRATE_CARROT), (45, 25, BARREL)):
    m.put(x, y, t, 3 if t == CRATE_L_T else 2)
for x in (16, 28): m.lamp(x, 24)

# ---------------------------------------------------------------- doors (interiors)
m.door('Ironhart Arms', 5, 9, K.WEAPON_SHOP, 7, 11)
m.door('Bulwark & Thread', 15, 9, K.ARMOR_SHOP, 7, 11)
m.door('The Starlit Grimoire', 27, 9, K.MAGIC_SHOP, 7, 11, style=1)
m.door('Whisker & Paw', 37, 9, K.PET_SHOP, 7, 11)

# ---------------------------------------------------------------- exits
m.exit('To Plaza', [(0, y) for y in range(14, 18)], K.PLAZA, 42, 15, 4)
for x in range(20, 24): m.put(x, H - 1, BARRICADE_H)   # the south road is closed: the harbor lies east now
m.exit('To Royal Quarter', [(x, 0) for x in range(20, 23)], *K.ARRIVE['royal_from_market'])   # the north alley
m.exit('To Harbor', [(W - 1, y) for y in range(14, 18)], *K.ARRIVE['harbor_from_market'])   # the old East Gate road

# ---------------------------------------------------------------- stall keepers (some sell, some chat)
def shop_npc(name, x, y, sheet, idx, lines, ce):
    m.add_event(name, x, y, [page(char(sheet, idx, 2), commands=say(*lines) + common_event(ce))])

shop_npc('Fruit Seller', 3, 22, 'People1', 4, ('Fruit Seller:', 'Sweetest apples in Nova, picked at dawn!'), DI.CE_ITEMS_BASIC)
m.npc('Greengrocer', 8, 22, 'People4', 2, ('Greengrocer:', 'Cabbages, leeks, turnips - the harbor cooks buy them all.'))
shop_npc('Baker\'s Stall', 13, 22, 'People4', 1, ('Baker\'s Girl:', 'Buns from the Golden Crust, still warm!'), DI.CE_BAKERY)
shop_npc('Jeweller', 29, 22, 'People3', 3, ('Jeweller:', 'Charms and rings with real enchantments.', 'Not one of them is cursed. Probably.'), DI.CE_ACCESSORIES)
m.npc('Tailor', 34, 22, 'People2', 5, ('Tailor:', 'Capes for heroes, aprons for bakers.', 'I measure twice and cut once.'))
m.npc('Spice Merchant', 39, 22, 'People2', 3, ('Spice Merchant:', 'Pepper from the Eastern Continent!', 'Your friend with the katana would know its value.'))
shop_npc('Herbalist', 3, 28, 'People4', 6, ('Herbalist:', 'Herbs for every ill - poison, sleep, paralysis.'), DI.CE_ITEMS_BASIC)
m.npc('Toymaker', 8, 28, 'People1', 7, ('Toymaker:', 'Every child in Nova owns one of my bears.'))
m.npc('Potter', 34, 28, 'People4', 4, ('Potter:', 'Careful! You break it, you buy it.'))
shop_npc('Cook', 39, 28, 'People2', 1, ('Street Cook:', 'Roast on a skewer, two coppers!'), DI.CE_BAKERY)
# shoppers, a pickpocket chase, animals
m.npc('Shopper', 10, 16, 'People1', 1, ('Shopper:', 'The magic shop sells potions that glow in the dark.'), move=1)
m.npc('Shopper', 24, 15, 'People3', 4, ('Housewife:', 'Fish is cheaper down at the harbor, mind you.'), move=1, freq=2)
m.npc('Guard', 20, 18, 'People3', 6, ('Market Guard:', 'Keep an eye on your purse.', 'A thief has been seen near the stalls.'), direction=2)
m.npc('Urchin', 30, 25, 'People4', 0, ('Urchin:', 'I didn\'t take anything! ...Want to buy a ring?'), move=1, speed=4, freq=4)
m.critter('Pen Dog', 43, 7, 'Nature', 0, 'Dog', 'Woof! The puppy wags its tail.', pen='R')
m.critter('Pen Chicken', 44, 10, 'Nature', 2, None, 'Bawk!', pen='R')
m.critter('Market Cat', 21, 27, 'Nature', 1, 'Cat', 'The cat is guarding the well. Or sleeping.', move=0)
m.npc('Pet Shop Girl', 41, 11, 'People1', 3, ('Pet Shop Girl:', 'Come inside! We have cats, hounds and an owl', 'that can read. Allegedly.'), direction=4)

# ---------------------------------------------------------------- touch-ups made by hand in the editor (Oct 2026)
m.put(20, 3, 0, 2); m.put(20, 3, 116, 3)
m.put(20, 4, 124, 3)

if __name__ == '__main__':
    out = sys.argv[1] if len(sys.argv) > 1 else None
    if out: m.render(out, scale=0.5, grid='--grid' in sys.argv)
    if '--save' in sys.argv: m.save(K.MARKET, parent_id=K.PLAZA, order=4)
