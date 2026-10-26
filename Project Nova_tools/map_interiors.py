# Interiors of the Royal Kingdom of Nova (MAP008-020).
import sys
sys.path.insert(0, 'D:/RPG Maker MV/Project Nova_tools')
from interior_kit import *
import nova_maplib as L
from nova_maplib import cmd, text, say, page, char, common_event
import kingdom as K
import data_ids as DI

ROOMS = {}


def reg(map_id, parent):
    def deco(fn):
        ROOMS[map_id] = (fn, parent)
        return fn
    return deco


def name(mid): return K.NAMES[mid]


# =========================================================================== Ironhart Arms (weapons)
@reg(K.WEAPON_SHOP, K.MARKET)
def weapon_shop():
    r = Room(15, 13, *name(K.WEAPON_SHOP), floor=STONE, walls='stone', ambient='#e2dad4')
    r.bgm = {'name': '', 'pan': 0, 'pitch': 100, 'volume': 90}
    r.bgs = {'name': 'City', 'pan': 0, 'pitch': 100, 'volume': 20}
    r.counter(4, 5, 10, 5)
    for x, t in ((5, SWORDS), (9, AXES)): r.put(x, 5, t, 3)
    r.put(3, 1, WALL_SWORDS_X); r.put(7, 1, WALL_SHIELD); r.put(11, 1, WALL_SWORDS_X)
    r.put(5, 2, SWORDS_X); r.put(9, 2, SPEARS)
    r.two(1, 2, REPO_SWORDS); r.two(2, 2, REPO_SPEARS); r.two(12, 2, REPO_SWORDS); r.two(13, 2, FIREPLACE_IRON)
    r.put(1, 7, SWORD_RACK_A); r.put(1, 8, SWORD_RACK_B); r.put(13, 7, BOWS); r.put(13, 8, SPEARS_B)
    r.put(2, 10, BARREL); r.put(12, 10, CRATE_B); r.put(13, 10, BARREL)
    r.put(11, 8, ANVIL_A); r.put(12, 8, HAMMERS)
    r.exit_door(7, K.MARKET, 5, 10, 2)
    r.keeper('Ironhart', 7, 4, 'People4', 4, ('Master Ironhart:', 'Every blade here was folded in my own forge.'),
             choice_shop('Master Ironhart', 'What are you after?', [('Standard arms', DI.CE_WEAPONS[0]),
                         ('Fine arms', DI.CE_WEAPONS[1]), ('Masterwork', DI.CE_WEAPONS[2]), ('Legendary', DI.CE_WEAPONS[3])]))
    r.npc('Apprentice', 11, 9, 'People1', 0, ('Apprentice:', 'Master says a katana is "just a long knife".',
          'Don\'t tell the Snowblade I said that.'), direction=8)
    r.npc('Customer', 4, 8, 'People3', 7, ('Knight:', 'Ironhart repaired my sword in an hour.', 'The man is a wizard. Of metal.'), direction=6)
    return r


# =========================================================================== Bulwark & Thread (armor)
@reg(K.ARMOR_SHOP, K.MARKET)
def armor_shop():
    r = Room(15, 13, *name(K.ARMOR_SHOP), floor=WOOD, walls='brick')
    r.counter(4, 5, 10, 5, TABLE_B)
    r.put(5, 5, HELMETS[0], 3); r.put(9, 5, SHIELD_A, 3)
    for x in (2, 4, 10, 12): r.put(x, 1, WIN_MID[0])
    r.put(7, 1, WALL_SHIELD); r.put(3, 2, SHIELD_B); r.put(11, 2, SHIELD_A)
    for i, x in enumerate((1, 2, 12, 13)): r.put(x, 3, ARMOR_STANDS[i])
    for i, x in enumerate((1, 2, 3)): r.put(x, 8, HATS[i])
    r.put(13, 7, CLOTHES[0]); r.put(13, 8, CLOTHES[2]); r.put(12, 8, CAPE)
    r.two(6, 2, CLOSET); r.two(8, 2, DRAWERS)
    r.put(1, 10, HELMETS[1]); r.put(13, 10, HELMETS[2]); r.put(2, 10, CRATE_B)
    r.exit_door(7, K.MARKET, 15, 10, 2)
    r.keeper('Brannoc', 7, 4, 'People2', 7, ('Brannoc the Armorer:', 'Plate for the brave, leather for the quick,', 'silk for the wise.'),
             choice_shop('Brannoc', 'What do you need?', [('Basic gear', DI.CE_ARMOR[0]), ('Sturdy gear', DI.CE_ARMOR[1]),
                         ('Knight\'s gear', DI.CE_ARMOR[2]), ('Finest gear', DI.CE_ARMOR[3]), ('Accessories', DI.CE_ACCESSORIES)]))
    r.npc('Seamstress', 12, 9, 'People1', 3, ('Seamstress:', 'Brannoc does the plate, I do the thread.', 'Guess which takes longer.'), direction=4)
    return r


# =========================================================================== The Starlit Grimoire (magic)
@reg(K.MAGIC_SHOP, K.MARKET)
def magic_shop():
    r = Room(15, 13, *name(K.MAGIC_SHOP), floor=RUG_F, walls='mansion', ambient='#cfc6e4')
    r.bgs = {'name': 'Wind', 'pan': 0, 'pitch': 60, 'volume': 15}
    for x in (1, 2, 3, 11, 12, 13): r.two(x, 2, (BOOKSHELF_A, BOOKSHELF_B)[x % 2] if False else (BOOKSHELF_A if x % 2 else BOOKSHELF_B))
    r.put(7, 1, STAINED); r.put(5, 1, WIN_MID[0]); r.put(9, 1, WIN_MID[0])
    r.two(5, 2, MEDICINE_SHELF); r.two(9, 2, MEDICINE_SHELF)
    r.counter(5, 5, 9, 5, TABLE_D)
    r.put(5, 5, POTION_BLUE, 3); r.put(6, 5, OLD_BOOK_OPEN, 3); r.put(9, 5, POTION_RED, 3)
    r.put(2, 8, CRYSTAL_TABLE); r.put(12, 8, LAB); r.put(13, 8, SCROLLS); r.put(1, 10, POT_A); r.put(13, 10, PLANT_B)
    r.put(1, 8, STOOL_C)
    r.exit_door(7, K.MARKET, 27, 10, 2)
    r.obj('Magic Circle', 7, 8, '!Door2', 7, ['A circle of silver light hums beneath your feet.'], step=True, through=True, priority=0)
    r.obj('Candle', 4, 2, '!Flame', 0, None, step=True, through=True, priority=2)
    r.obj('Candle', 10, 2, '!Flame', 0, None, step=True, through=True, priority=2)
    r.obj('Sparkle', 2, 7, '!Flame', 7, None, step=True, through=True, priority=2)
    r.keeper('Madame Orsolya', 7, 4, 'People3', 3, ('Madame Orsolya:', 'Ah... a caster. I can smell starlight on you.',
             'Staves, elixirs, and charms - all yours, for a price.'), common_event(DI.CE_MAGIC))
    r.npc('Apprentice Mage', 11, 9, 'People2', 2, ('Apprentice Mage:', 'Madame says Void magic is forbidden.',
          'Which is exactly why I want to learn it.'), direction=4)
    r.look('Crystal Ball', 2, 8, ['Mist swirls inside the crystal...', 'For a moment you see a white blade in the snow.'])
    return r


# =========================================================================== Whisker & Paw (pets)
@reg(K.PET_SHOP, K.MARKET)
def pet_shop():
    r = Room(15, 13, *name(K.PET_SHOP), floor=WOOD_B, walls='wood')
    # three pens along the back wall, fronted by bars
    for x0 in (1, 5, 10):
        r.rect(x0, 3, x0 + 3, 4, STRAW)
        for x in range(x0, x0 + 4): r.put(x, 5, JAIL[0])
        r.put(x0, 3, STRAW_BED[0], 3); r.put(x0, 4, STRAW_BED[1])
    r.rect(9, 3, 9, 5, r.WT); r.rect(4, 3, 4, 5, r.WT)
    r.put(3, 1, WIN_SMALL[1]); r.put(7, 1, WIN_SMALL[1]); r.put(12, 1, WIN_SMALL[1])
    r.counter(6, 8, 8, 8, TABLE_A)
    r.put(6, 8, BOWL, 3); r.put(8, 8, BASKET, 3)
    for x, t in ((1, SACK_A), (2, SACKS), (13, BARREL), (12, BASKET_GRAIN), (1, CRATE_B)):
        r.put(x, 10 if t != CRATE_B else 9, t)
    r.put(13, 9, PLANT_A)
    r.exit_door(7, K.MARKET, 37, 10, 2)
    import nova_maplib as N
    from town_kit import pen_route
    def pet(name_, x, y, sheet, idx, se, line, step):
        # fixed little loop inside the pen (one step out and back), never a random walk through the bars
        cmds = ([cmd(250, [{'name': se, 'volume': 70, 'pitch': 100, 'pan': 0}])] if se else []) + text(line)
        r.add_event(name_, x, y, [page(char(sheet, idx), commands=cmds, route=pen_route(step), step_anim=True, freq=4)])
    pet('Puppy', 2, 3, 'Nature', 0, 'Dog', 'The puppy tries to lick you through the bars.', 'R')
    pet('Hound', 3, 4, 'Nature', 0, 'Dog', 'A loyal hound sits up straight, hoping to be chosen.', 'L')
    pet('Kitten', 6, 3, 'Nature', 1, 'Cat', 'A kitten is fighting a ball of yarn. The yarn is winning.', 'R')
    pet('Tabby', 7, 4, 'Nature', 1, 'Cat', 'A grey tabby... is this "Biscuit" from the notice board?', 'L')
    pet('Chick', 11, 3, 'Nature', 2, None, 'Peep! A tiny chick with very big ambitions.', 'R')
    pet('Hen', 12, 4, 'Nature', 2, None, 'Bawk. The hen judges you silently.', 'L')
    r.keeper('Wren', 7, 7, 'People1', 3, ('Wren of Whisker & Paw:', 'Every adventurer needs a companion!',
             'They\'re small, but they\'ll fight beside you - in their own way.'), common_event(DI.CE_PETS))
    r.npc('Old Breeder', 12, 7, 'People2', 2, ('Old Breeder:', 'I bred hounds for the royal hunt for thirty years.',
          'Now I breed them for heroes. Better company.'), direction=4)
    # ------------------------------------------------------------ touch-ups made by hand in the editor (Oct 2026)
    r.cell(4, 4, ('A4', 16))
    r.cell(9, 4, ('A4', 16))
    r.cell(4, 5, ('A4', 24))
    r.cell(9, 5, ('A4', 24))
    r.cell(3, 6, ('A2', 8))
    r.cell(4, 6, ('A4', 24))
    r.cell(5, 6, ('A2', 8))
    r.cell(8, 6, ('A2', 8))
    r.cell(9, 6, ('A4', 24))
    r.cell(10, 6, ('A2', 8))
    r.cell(3, 7, ('A2', 8))
    r.cell(4, 7, ('A2', 8))
    r.cell(5, 7, ('A2', 8))
    r.cell(8, 7, ('A2', 8))
    r.cell(9, 7, ('A2', 8))
    r.cell(10, 7, ('A2', 8))
    r.put(1, 5, 0, 2); r.put(1, 5, 244, 3); r.put(2, 5, 245, 2); r.put(2, 5, 246, 3); r.put(3, 5, 245, 2); r.put(3, 5, 247, 3); r.put(4, 5, 0, 2); r.put(5, 5, 0, 2); r.put(5, 5, 245, 3); r.put(6, 5, 0, 2); r.put(6, 5, 246, 3); r.put(7, 5, 0, 2); r.put(7, 5, 247, 3); r.put(8, 5, 0, 2); r.put(8, 5, 244, 3); r.put(10, 5, 0, 2); r.put(10, 5, 245, 3); r.put(11, 5, 0, 2); r.put(11, 5, 246, 3); r.put(12, 5, 0, 2); r.put(12, 5, 247, 3); r.put(13, 5, 0, 2); r.put(13, 5, 244, 3)
    r.put(1, 6, 252, 3); r.put(2, 6, 252, 2); r.put(2, 6, 254, 3); r.put(3, 6, 252, 2); r.put(3, 6, 255, 3); r.put(5, 6, 252, 2); r.put(5, 6, 253, 3); r.put(6, 6, 252, 2); r.put(6, 6, 254, 3); r.put(7, 6, 252, 2); r.put(7, 6, 255, 3); r.put(8, 6, 252, 3); r.put(10, 6, 252, 2); r.put(10, 6, 253, 3); r.put(11, 6, 252, 2); r.put(11, 6, 254, 3); r.put(12, 6, 252, 2); r.put(12, 6, 255, 3); r.put(13, 6, 252, 3)
    r.shadow[6][5] = 5
    r.shadow[6][10] = 5
    return r


# =========================================================================== The Lion's Rest (tavern + guild desk)
@reg(K.TAVERN, K.BAKERS_LANE)
def tavern():
    r = Room(29, 15, *name(K.TAVERN), floor=WOOD, walls='log', ambient='#e6dad0')
    r.bgm = {'name': 'Town2', 'pan': 0, 'pitch': 110, 'volume': 70}
    r.bgs = {'name': 'City', 'pan': 0, 'pitch': 90, 'volume': 35}
    # bar along the right with shelves behind
    r.counter(14, 5, 14, 10, TABLE_B); r.counter(15, 10, 18, 10, TABLE_B)
    r.two(15, 2, WINE_RACK); r.two(16, 2, BOTTLES_A); r.two(17, 2, BOTTLES_B); r.two(18, 2, WINE_RACK)
    for y, t in ((6, MUG_ALE), (8, MUG)): r.put(14, y, t, 3)
    r.put(16, 10, ALE_BOTTLES, 3); r.put(18, 10, MUG, 3)
    r.put(19, 6, BARREL); r.put(19, 7, BARREL); r.put(19, 9, BARREL)
    # fireplace, stage and the room
    r.wide(2, 1, FIREPLACE_L)
    r.put(6, 1, PAINTING_A); r.put(10, 1, WIN_LARGE[0]); r.put(12, 1, PAINTING_B)
    tables = [(3, 6), (8, 6), (3, 10), (8, 10)]
    for tx, ty in tables:
        r.put(tx, ty, TABLE_ROUND)
        r.put(tx - 1, ty, STOOL_A); r.put(tx + 1, ty, STOOL_A); r.put(tx, ty + 1, STOOL_B)
    r.put(3, 6, MEAL_MEAT, 3); r.put(8, 6, MUG_ALE, 3); r.put(3, 10, ROAST_FISH, 3); r.put(8, 10, PIZZA, 3)
    r.rect(11, 12, 13, 13, RUG_E)
    for tx, ty in ((14, 4), (19, 4)):
        r.obj('Wall Lamp', tx, ty, '!Flame', 1, None, step=True, through=True, priority=2)
    r.put(1, 13, POT_A); r.put(12, 3, PLANT_A); r.put(1, 3, BARREL)
    r.exit_door(10, K.BAKERS_LANE, 30, 7, 2)
    r.keeper('Bartender', 15, 6, 'People4', 4, ('Old Bart, the Bartender:', 'Welcome to the Lion\'s Rest!', 'Drink, food, or rumors?'),
             choice_shop('Old Bart', 'What\'ll it be?', [('Food & drink', DI.CE_TAVERN)]) + [
                 cmd(101, ['', 0, 0, 2]), cmd(401, ['\\C[6]Old Bart:\\C[0]']),
                 cmd(401, ['They say a frozen shrine lies beyond the northern pass,']),
                 cmd(401, ['and a sword sleeps there that no smith ever forged.'])], direction=4)
    r.npc('Bard', 12, 12, 'People2', 6, ('Bard:', '♪ Lion of Nova, shield of the realm,', 'never yields, never falls... ♪'), direction=2)
    r.npc('Sailor', 4, 6, 'People2', 3, ('Drunk Sailor:', 'The galleon? Carrying gold to the East, I bet.', '...Or a princess. Hic.'), direction=4)
    r.npc('Mercenary', 9, 10, 'People4', 5, ('Mercenary:', 'Heard the Dragonslayer drinks here.', 'Four dragons. FOUR. I\'ve killed four chickens.'), direction=4)
    r.npc('Merchant', 7, 6, 'People2', 1, ('Merchant:', 'Bulwark & Thread is selling knight\'s plate cheap.', 'Someone\'s preparing for a war.'), direction=6)
    r.npc('Barmaid', 6, 8, 'People2', 5, ('Barmaid:', 'Mind the floor, it\'s still wet from last night.'), move=1, freq=4)
    r.npc('Hooded Figure', 19, 12, 'Evil', 1, ('Hooded Figure:', '...', 'The Ashveil boy. You travel with him?', 'Interesting.'), direction=4)
    # guild wing (east), through an open archway south of the bar
    r.rect(20, 0, 20, 13, r.WT)
    r.rect(20, 11, 20, 13, WOOD)
    r.rect(21, 3, 27, 13, WOOD_B)
    for x in (21, 22, 23): r.put(x, 2, NOTICE)                  # mission board
    r.put(21, 1, WORLD_MAP[0]); r.put(22, 1, WORLD_MAP[1])
    r.two(27, 1, TAPESTRY); r.put(25, 1, WIN_SMALL[1])
    r.counter(24, 6, 27, 6, TABLE_C)
    r.put(24, 6, NOTES, 3); r.put(25, 6, BOOK_OPEN, 3)
    r.put(24, 3, SHELF_BOOKS); r.two(25, 2, CABINET); r.put(27, 3, SHELF_SACKS)
    r.put(23, 10, TABLE_ROUND); r.put(22, 10, STOOL_A); r.put(24, 10, STOOL_A); r.put(23, 10, MAP_C, 3)
    r.put(27, 12, SWORD_RACK_A); r.put(27, 13, SWORD_RACK_B); r.put(21, 13, CRATE_B); r.put(22, 13, BARREL)
    r.obj('Wall Lamp', 23, 4, '!Flame', 1, None, step=True, through=True, priority=2)
    r.look('Mission Board', 22, 2, ['\\C[6]Guild Mission Board\\C[0]',
           'Class 5+: Clear the rats from the Silver Swan\'s cellar.',
           'Class 4+: Escort the Saltwind Harbor caravans.',
           'Class 3+: Hunt the wolf pack on the northern road.'])
    r.keeper('Guild Clerk', 26, 5, 'People1', 3, ('Guild Clerk:', 'Welcome to the Guild desk!',
             'Missions are on the board. Show me your license', 'and I\'ll register the job to your name.'), direction=2)
    r.npc('Adventurer', 22, 9, 'People4', 5, ('Mercenary:', 'Class 5 jobs pay in copper and blisters.',
          'One day I\'ll take a Class 3 contract.'), direction=6)
    r.npc('Young Mage', 25, 11, 'People2', 2, ('Young Mage:', 'Just got my Class 5 license this spring.',
          'Mother still thinks I work in a library.'), direction=8)
    # ------------------------------------------------------------ touch-ups made by hand in the editor (Oct 2026)
    r.cell(20, 8, ('A4', 17))
    r.cell(20, 9, ('A4', 25))
    r.cell(20, 10, ('A4', 25))
    return r


# =========================================================================== The Silver Swan (inn)
@reg(K.INN, K.BAKERS_LANE)
def inn():
    r = Room(19, 15, *name(K.INN), floor=WOOD_B, walls='int_wood')
    # partition: lobby (west) and the guest room (east), with a doorway
    r.rect(10, 1, 10, 13, r.WT)
    r.rect(10, 9, 10, 9, WOOD_B)
    # lobby
    r.counter(2, 6, 6, 6, TABLE_C)
    r.put(3, 6, BOOK_OPEN, 3); r.put(5, 6, VASE, 3)
    r.two(2, 2, CLOCK); r.two(6, 2, CABINET); r.put(4, 1, PORTRAIT_A); r.put(8, 1, WIN_LARGE[1])
    r.two(8, 2, FIREPLACE_BRICK)
    r.rect(3, 9, 7, 11, RUG_B)
    r.put(4, 10, TABLE_ROUND); r.put(3, 10, CHAIR); r.put(5, 10, CHAIR); r.put(4, 10, TEAPOT, 3)
    r.put(1, 12, PLANT_B); r.put(9, 12, PLANT_A)
    # guest room
    for x in (11, 14, 17):
        r.two(x, 3, BED)
        if x < 17: r.put(x + 1, 3, DRESSER)
    r.put(12, 1, WIN_MID[1]); r.put(15, 1, WIN_MID[1])
    r.rect(11, 6, 17, 6, RUG_D)
    r.two(17, 9, CLOSET); r.put(11, 12, POT_B); r.put(17, 12, FLOWER_TABLE)
    r.exit_door(5, K.BAKERS_LANE, 3, 17, 2)
    r.keeper('Innkeeper', 4, 5, 'People1', 3, ('Marigold, the Innkeeper:', 'Welcome to the Silver Swan!'), common_event(DI.CE_INN))
    r.npc('Guest', 13, 7, 'People4', 5, ('Traveller:', 'Best beds this side of the mountains.', 'The soup is... well, the beds are good.'), direction=2)
    r.npc('Maid', 15, 10, 'People2', 5, ('Maid:', 'I change the sheets every morning.', 'The Dragonslayer\'s room I change twice.'), move=1)
    r.npc('Old Guest', 3, 11, 'People2', 2, ('Old Guest:', 'I have lived at this inn for eleven years.', 'I keep meaning to leave.'), direction=6)
    # ------------------------------------------------------------ touch-ups made by hand in the editor (Oct 2026)
    r.cell(10, 6, ('A4', 19))
    r.cell(10, 7, ('A4', 27))
    r.cell(10, 8, ('A4', 27))
    r.put(7, 1, 34, 3); r.put(8, 1, 0, 2); r.put(9, 1, 132, 3); r.put(12, 1, 0, 2); r.put(12, 1, 17, 3); r.put(15, 1, 0, 2); r.put(15, 1, 17, 3)
    r.put(4, 2, 50, 3); r.put(5, 2, 51, 3); r.put(6, 2, 65, 3); r.put(7, 2, 42, 3); r.put(8, 2, 0, 3); r.put(9, 2, 140, 3); r.put(12, 2, 25, 3); r.put(15, 2, 25, 3)
    r.put(4, 3, 58, 3); r.put(5, 3, 59, 3); r.put(6, 3, 0, 2); r.put(6, 3, 73, 3); r.put(8, 3, 0, 2)
    r.put(4, 9, 104, 3)
    r.put(3, 10, 0, 2); r.put(3, 10, 104, 3); r.put(5, 10, 0, 2); r.put(5, 10, 104, 3)
    r.put(4, 11, 104, 3)
    return r


# =========================================================================== Royal Barracks
@reg(K.BARRACKS, K.CASTLE_APPROACH)
def barracks():
    r = Room(17, 15, *name(K.BARRACKS), floor=STONE, walls='stone', ambient='#e4e4e8')
    r.bgm = {'name': 'Castle2', 'pan': 0, 'pitch': 100, 'volume': 60}
    # bunks on both sides
    for x in (1, 3, 13, 15):
        r.two(x, 3, CHEAP_BED)
    for x in (1, 3, 13, 15):
        r.put(x, 9, CHEAP_BED_B[0], 3); r.put(x, 10, CHEAP_BED_B[1])
    # long mess table
    r.counter(6, 7, 10, 8, TABLE_C)
    for x in (6, 8, 10): r.put(x, 7, BOWL, 3)
    r.put(7, 8, MUG, 3); r.put(9, 8, BREAKFAST, 3)
    for x in (6, 8, 10): r.put(x, 6, STOOL_A); r.put(x, 9, STOOL_A)
    # captain's corner, weapons, banners
    r.two(7, 2, TAPESTRY); r.two(9, 2, TAPESTRY)
    r.put(8, 1, WALL_SHIELD); r.put(5, 1, WALL_SWORDS_X); r.put(11, 1, WALL_SWORDS_X)
    r.put(8, 4, TABLE_CLOTH); r.put(8, 4, MAP_C, 3)
    for i, x in enumerate((5, 11)): r.put(x, 3, ARMOR_STANDS[i])
    r.put(1, 12, SWORD_RACK_A); r.put(15, 12, SWORD_RACK_B); r.put(2, 12, BARREL); r.put(14, 12, CRATE_B)
    r.put(5, 12, NOTICE)
    for bx in (6, 10):
        r.obj('Brazier', bx, 12, '!Other2', 7, None, step=True)
    r.exit_door(8, K.CASTLE_APPROACH, 21, 22, 2)
    r.npc('Commander Vale', 8, 3, 'People3', 7, ('Commander Vale:', 'You walk like a soldier, whoever you are.',
          'Roland of the Shield trained under me. Tell him', 'old Vale still keeps his bunk made.'), direction=2)
    r.npc('Soldier', 4, 7, 'People3', 6, ('Soldier:', 'Off duty. Don\'t tell the Sergeant.'), direction=6)
    r.npc('Soldier', 12, 8, 'People3', 7, ('Soldier:', 'The northern patrols came back with frostbite.', 'In summer. Something is wrong up there.'), direction=4)
    r.npc('Cook', 14, 5, 'People4', 4, ('Barracks Cook:', 'Stew. It\'s always stew. Don\'t ask what\'s in it.'), direction=4)
    r.look('Notice', 5, 12, ['\\C[6]Duty Roster\\C[0]', 'North gate: Squad 3   Harbor: Squad 5', 'Volunteers wanted - frozen pass, double pay.'])
    return r


# =========================================================================== Golden Crust Bakery
@reg(K.BAKERY, K.BAKERS_LANE)
def bakery():
    r = Room(15, 12, *name(K.BAKERY), floor=COBBLE_O, walls='brick2', ambient='#efe4d8')
    r.bgs = {'name': 'City', 'pan': 0, 'pitch': 100, 'volume': 15}
    r.put(2, 3, OVEN); r.put(3, 3, OVEN); r.put(4, 3, COUNTER_A); r.put(5, 3, SINK)
    r.two(7, 2, BREAD_SHELF); r.two(8, 2, BREAD_SHELF); r.two(12, 2, SUNDRIES_A); r.two(13, 2, BREAD_SHELF)
    r.put(10, 1, WIN_MID[0]); r.put(1, 1, WIN_SMALL[0])
    r.counter(5, 6, 10, 6, TABLE_A)
    r.put(5, 6, BASKET_BREAD, 3); r.put(7, 6, PIE, 3); r.put(9, 6, CAKE, 3); r.put(10, 6, BASKET_BREAD, 3)
    r.put(1, 5, SACK_A); r.put(1, 6, SACKS); r.put(1, 8, CRATE_GRAIN); r.put(13, 8, BASKET_APPLE)
    r.put(12, 9, TABLE_ROUND); r.put(11, 9, STOOL_A); r.put(13, 9, STOOL_A); r.put(12, 9, CUP_TEA, 3)
    r.exit_door(7, K.BAKERS_LANE, 15, 7, 2)
    r.keeper('Baker Hollis', 7, 5, 'People1', 5, ('Baker Hollis:', 'Fresh from the oven!', 'The royal kitchens buy my honey bread, you know.'),
             common_event(DI.CE_BAKERY))
    r.npc('Baker\'s Daughter', 3, 4, 'People1', 3, ('Baker\'s Daughter:', 'I knead the dough at four in the morning.', 'Every. Single. Morning.'), direction=8)
    r.npc('Customer', 12, 8, 'People2', 2, ('Old Customer:', 'Same bun, same table, for twenty years.'), direction=2)
    return r


# =========================================================================== Lantern Row Townhouse (2 floors)
@reg(K.TOWNHOUSE_1F, K.RESIDENTIAL)
def townhouse_1f():
    r = Room(13, 13, *name(K.TOWNHOUSE_1F), floor=WOOD, walls='plaster_e')
    r.wide(1, 1, FIREPLACE_L)
    r.put(5, 1, PAINTING); r.put(7, 1, WIN_MID[2]); r.two(9, 2, BOOKSHELF_A); r.two(10, 2, BOOKSHELF_B)
    r.wide(11, 1, [(STAIRS_UP[3],), (STAIRS_UP[3],)])
    r.rect(2, 6, 7, 9, RUG_A)
    r.put(4, 7, TABLE_ROUND); r.put(5, 7, TABLE_ROUND); r.put(3, 7, CHAIR); r.put(6, 7, CHAIR)
    r.put(4, 7, TEAPOT, 3); r.put(5, 7, FRUIT_BOWL, 3)
    r.wide(8, 8, PIANO)
    r.put(1, 10, PLANT_A); r.put(11, 10, VASE); r.put(1, 6, DRESSER)
    r.exit_door(6, K.RESIDENTIAL, 10, 11, 2)
    r.add_event('Stairs Up', 11, 2, [L.exit_page(K.TOWNHOUSE_2F, 11, 3, 2)])
    r.npc('Lady Mirelle', 4, 9, 'People3', 3, ('Lady Mirelle:', 'Visitors! How delightful.',
          'My late husband was a captain of the Royal Navy.', 'Do look around - the view from upstairs is lovely.'), direction=8)
    r.npc('Butler', 9, 6, 'People2', 7, ('Butler:', 'Tea will be served at four, as always.'), direction=2)
    # ------------------------------------------------------------ touch-ups made by hand in the editor (Oct 2026)
    r.put(6, 1, 167, 3); r.put(11, 1, 0, 3)
    r.put(7, 2, 25, 3)
    return r


@reg(K.TOWNHOUSE_2F, K.RESIDENTIAL)
def townhouse_2f():
    r = Room(13, 11, *name(K.TOWNHOUSE_2F), floor=WOOD_B, walls='plaster_e')
    r.put(11, 2, STAIRS_DOWN[3]); r.put(11, 3, STAIRS_DOWN[3])
    r.wide(2, 3, LARGE_BED); r.put(4, 3, DRESSER)
    r.put(1, 1, WIN_LARGE[0]); r.put(5, 1, MIRROR[0]); r.put(5, 2, MIRROR[1])
    r.put(7, 1, WIN_LARGE[2]); r.two(8, 2, CLOSET)
    r.rect(2, 6, 6, 8, RUG_C)
    r.put(9, 7, TABLE_CLOTH); r.put(9, 7, OLD_BOOK_OPEN, 3); r.put(8, 7, CHAIR)
    r.put(1, 9, PLANT_B); r.put(11, 9, POT_A); r.put(6, 9, DOLL_BEAR)
    r.add_event('Stairs Down', 11, 2, [L.exit_page(K.TOWNHOUSE_1F, 11, 3, 2)])
    r.look('Telescope Window', 7, 2, ['Through the window: the harbor, the lighthouse,', 'and far away, the snowy mountains of the north.'])
    r.npc('Young Mirelle', 4, 7, 'People1', 1, ('Young Mirelle:', 'Grandmother says Father\'s ship will come home.', 'I watch the harbor every evening.'), direction=8)
    r.look('Diary', 9, 7, ['"Day 312. Still no word from the Morning Star."', '"The harbormaster says the northern sea froze over."'])
    # ------------------------------------------------------------ touch-ups made by hand in the editor (Oct 2026)
    r.put(7, 1, 0, 2); r.put(7, 1, 33, 3)
    r.put(1, 2, 40, 3); r.put(7, 2, 41, 3)
    r.put(8, 7, 0, 2); r.put(8, 7, 104, 3); r.put(10, 7, 104, 3)
    return r


# =========================================================================== Ashveil Residence (3 floors)
@reg(K.ASHVEIL_1F, K.RESIDENTIAL)
def ashveil_1f():
    # kitchen & dining (west) | living room (east) | bathroom (south-east corner)
    r = Room(21, 15, *name(K.ASHVEIL_1F), floor=WOOD, walls='plaster_e', ambient='#efe2d6')
    r.rect(8, 0, 8, 13, r.WT); r.rect(8, 10, 8, 11, WOOD)               # kitchen | living room, open doorway
    r.rect(14, 7, 20, 7, r.WT); r.rect(14, 8, 14, 13, r.WT)               # bathroom walls
    r.rect(15, 8, 19, 9, r.WF); r.rect(15, 10, 19, 13, TILE_W)
    r.cell(14, 11, TILE_W)                                                 # bathroom doorway
    # kitchen
    r.put(1, 3, OVEN); r.put(2, 3, SINK); r.put(3, 3, COUNTER_A); r.put(4, 3, COUNTER_B); r.put(5, 3, SHELF_JARS)
    r.two(6, 2, DISH_CABINET); r.put(2, 2, UTENSILS); r.put(4, 1, WIN_SMALL[1]); r.put(7, 3, BARREL)
    r.put(1, 12, SACK_A); r.put(1, 13, SACKS); r.put(7, 13, BASKET_APPLE)
    # dining table
    r.counter(3, 7, 5, 8, TABLE_A)
    for y in (7, 8): r.put(2, y, STOOL_A); r.put(6, y, STOOL_A)
    r.put(3, 7, BREAKFAST, 3); r.put(5, 7, BASKET_BREAD, 3); r.put(4, 8, TEAPOT, 3)
    # living room
    r.wide(10, 1, FIREPLACE_L)
    r.two(9, 2, BOOKSHELF_A); r.put(16, 1, PORTRAIT_A); r.put(17, 1, WIN_MID[1]); r.put(19, 1, WIN_MID[1])
    r.put(14, 2, STAIRS_UP[2])
    r.rect(10, 5, 13, 8, RUG_A)
    r.put(11, 6, TABLE_ROUND); r.put(12, 6, TABLE_ROUND); r.put(10, 6, CHAIR); r.put(13, 6, CHAIR)
    r.put(11, 6, CUP_TEA, 3); r.put(12, 6, FRUIT_BOWL, 3)
    r.put(9, 13, PLANT_A); r.put(13, 13, VASE); r.put(18, 4, FLOWER_TABLE)
    # bathroom
    r.put(15, 10, DRESSER); r.two(16, 8, MIRROR); r.put(18, 10, TUB_A); r.put(19, 10, TUB_B); r.put(19, 13, PLANT_B)
    r.exit_door(11, K.RESIDENTIAL, 11, 44, 2)
    r.add_event('Stairs Up', 14, 3, [L.exit_page(K.ASHVEIL_2F, 10, 4, 2)])
    r.npc('Mother', 3, 4, 'People1', 1, ('Mother:', 'Wipe your boots, Kael.', 'And if you are going to practise fire spells,', 'do it OUTSIDE this time.'), direction=2)
    r.look('Family Portrait', 16, 1, ['A family portrait. Six Ashveils, all with the', 'same stubborn look in their eyes.'])
    r.look('Bath', 18, 10, ['A wooden tub, still warm.', 'Fire mages never have to wait for hot water.'])
    # ------------------------------------------------------------ touch-ups made by hand in the editor (Oct 2026)
    r.cell(8, 7, ('A4', 34))
    r.cell(8, 8, ('A4', 40))
    r.cell(14, 8, ('A4', 34))
    r.cell(15, 8, ('A4', 42))
    r.cell(8, 9, ('A4', 40))
    r.cell(14, 9, ('A4', 40))
    r.cell(15, 9, ('A4', 42))
    r.cell(14, 10, ('A4', 40))
    r.put(4, 1, 0, 2); r.put(4, 1, 38, 3)
    r.put(4, 2, 46, 3); r.put(14, 2, 0, 2); r.put(17, 2, 25, 3); r.put(19, 2, 25, 3)
    r.put(14, 3, 4, 3)
    r.put(4, 6, 104, 3); r.put(10, 6, 0, 2); r.put(11, 6, 0, 2); r.put(11, 6, 0, 3); r.put(12, 6, 0, 2); r.put(12, 6, 0, 3); r.put(13, 6, 0, 2)
    r.put(4, 9, 104, 3)
    r.cell(15, 8, ('ID', 7906)); r.cell(15, 9, ('ID', 7912))   # the editor's own wall-corner shapes
    return r


@reg(K.ASHVEIL_2F, K.RESIDENTIAL)
def ashveil_2f():
    # parents' room (west) | stair hall (middle) | sisters' room (east)
    r = Room(21, 13, *name(K.ASHVEIL_2F), floor=WOOD_B, walls='plaster_e', ambient='#efe2d6')
    r.rect(7, 0, 7, 11, r.WT); r.cell(7, 9, WOOD_B)
    r.rect(13, 0, 13, 11, r.WT); r.cell(13, 9, WOOD_B)
    # stair hall
    r.put(11, 2, STAIRS_UP[2])
    r.put(9, 10, STAIRS_DOWN[3])
    r.rect(9, 5, 11, 8, RUG_D); r.put(8, 11, PLANT_A); r.put(12, 11, VASE); r.two(8, 2, CLOCK)
    # parents
    r.wide(2, 3, LARGE_BED); r.put(1, 3, DRESSER); r.put(4, 3, DRESSER)
    r.put(2, 1, WIN_LARGE[1]); r.put(3, 1, WIN_LARGE[1]); r.two(5, 2, CLOSET)
    r.rect(2, 7, 5, 9, RUG_C); r.put(5, 10, TABLE_CLOTH); r.put(5, 10, BOOK, 3); r.put(4, 10, CHAIR); r.put(1, 11, PLANT_B)
    # sisters: the knight's bed (east) and the little sister's bed (west), separate
    r.two(15, 3, BED); r.two(18, 3, BED); r.put(16, 3, DRESSER)
    r.put(15, 1, WIN_MID[1]); r.put(18, 1, WIN_MID[1]); r.two(17, 1, MIRROR)
    r.put(19, 3, ARMOR_STANDS[1]); r.put(19, 7, SWORD_RACK_A); r.put(19, 8, SHIELD_A)
    r.put(14, 6, DOLL_BEAR); r.put(14, 7, DOLL_BLUE); r.put(14, 11, FLOWER_TABLE); r.rect(15, 7, 18, 9, RUG_F)
    r.add_event('Stairs Down', 10, 3, [L.exit_page(K.ASHVEIL_1F, 14, 4, 2)])
    r.add_event('Stairs Up', 12, 3, [L.exit_page(K.ASHVEIL_3F, 8, 4, 2)])
    r.npc('Little Sister', 16, 8, 'People1', 2, ('Little Sister:', 'Brother! When you go adventuring,', 'you have to bring me something from every town.', 'Promise!'), direction=2)
    r.look('Knight\'s Bed', 18, 3, ['Your older sister\'s bed, made with military', 'precision. It has not been slept in for weeks.'])
    r.look('Armor Stand', 19, 3, ['Spare armor, polished to a mirror shine.', 'She serves the Crown now.'])
    r.look('Parents\' Bed', 2, 3, ['Your parents\' bed. Father\'s side is cold.', 'He is off on another journey.'])
    # ------------------------------------------------------------ touch-ups made by hand in the editor (Oct 2026)
    r.cell(7, 6, ('A4', 34))
    r.cell(13, 6, ('A4', 34))
    r.cell(7, 7, ('A4', 40))
    r.cell(13, 7, ('A4', 40))
    r.cell(7, 8, ('A4', 40))
    r.cell(13, 8, ('A4', 40))
    r.put(2, 2, 41, 3); r.put(3, 2, 41, 3); r.put(11, 2, 0, 2); r.put(15, 2, 25, 3); r.put(16, 2, 116, 3); r.put(18, 2, 25, 3)
    r.put(10, 3, 12, 3); r.put(12, 3, 3, 3); r.put(14, 3, 80, 3); r.put(15, 3, 0, 3); r.put(16, 3, 0, 2)
    r.put(14, 4, 88, 3); r.put(15, 4, 0, 2)
    r.put(4, 10, 0, 2); r.put(4, 10, 104, 3); r.put(9, 10, 0, 2)
    r.put(15, 11, 104, 3)
    return r


@reg(K.ASHVEIL_3F, K.RESIDENTIAL)
def ashveil_3f():
    # the brothers' attic room: Kael (west), the eldest brother (east), separate beds
    r = Room(17, 11, *name(K.ASHVEIL_3F), floor=WOOD, walls='plaster_e', ambient='#e8dccf')
    r.put(8, 3, STAIRS_DOWN[3])
    # Kael
    r.two(1, 3, BED); r.two(3, 2, BOOKSHELF_A); r.two(4, 2, BOOKSHELF_B); r.put(2, 1, WIN_SMALL[1])
    r.put(5, 7, TABLE_CLOTH); r.put(5, 7, OLD_BOOK_OPEN, 3); r.put(5, 8, CHAIR)
    r.put(1, 8, CRYSTAL_TABLE); r.put(2, 9, POTION_BLUE); r.put(6, 3, SHELF_BOOKS)
    r.obj('Candle', 6, 7, '!Flame', 0, None, step=True, through=True, priority=2)
    # eldest brother
    r.two(15, 3, BED); r.put(12, 1, WORLD_MAP[0]); r.put(13, 1, WORLD_MAP[1]); r.put(14, 1, WIN_SMALL[1])
    r.put(11, 7, TABLE_CLOTH); r.put(11, 7, MAP_C, 3); r.put(11, 8, CHAIR)
    r.put(15, 8, BARREL); r.put(14, 9, ROPE_C); r.put(15, 9, CRATE_B)
    r.rect(6, 5, 10, 6, RUG_B); r.two(12, 2, DRAWERS); r.two(10, 2, CLOSET)
    r.add_event('Stairs Down', 8, 3, [L.exit_page(K.ASHVEIL_2F, 12, 4, 2)])
    r.look('Kael\'s Desk', 5, 7, ['Your notes from the Academy, covered in', 'shadow-weave diagrams and scorch marks.'])
    r.look('Crystal Ball', 1, 8, ['Your old practice crystal.', 'A thin wisp of shadow still curls inside.'])
    r.look('Sea Chart', 11, 7, ['Your elder brother\'s sea chart. He circled ports', 'you have never heard of.'])
    r.look('Brother\'s Bed', 15, 3, ['Your elder brother\'s bed. It still smells', 'faintly of salt and tar.'])
    # ------------------------------------------------------------ touch-ups made by hand in the editor (Oct 2026)
    r.put(2, 1, 0, 2); r.put(2, 1, 38, 3); r.put(14, 1, 0, 2); r.put(14, 1, 38, 3)
    r.put(2, 2, 46, 3); r.put(14, 2, 46, 3)
    r.put(5, 8, 0, 2); r.put(5, 8, 104, 3); r.put(11, 8, 0, 2); r.put(11, 8, 104, 3)
    return r


def build_all():
    return {mid: (fn(), parent) for mid, (fn, parent) in ROOMS.items()}


if __name__ == '__main__':
    from PIL import Image, ImageDraw
    out = sys.argv[1] if len(sys.argv) > 1 else None
    rooms = build_all()
    if out:
        imgs = [(mid, r.render(out.replace('.png', '_%d.png' % mid), scale=0.5)) for mid, (r, _) in rooms.items()]
        W = 3 * 520; H = ((len(imgs) + 2) // 3) * 400
        sheet = Image.new('RGBA', (W, H), (40, 40, 40, 255)); d = ImageDraw.Draw(sheet)
        for i, (mid, im) in enumerate(imgs):
            x, y = (i % 3) * 520, (i // 3) * 400
            sheet.alpha_composite(im, (x, y)); d.text((x + 4, y + im.height + 2), '%d %s' % (mid, K.NAMES[mid][1]), fill=(255, 255, 0))
        sheet.save(out)
    if '--save' in sys.argv:
        for mid, (r, parent) in rooms.items():
            r.save(mid, parent_id=parent, order=mid)
