# MAP003 - Royal Kingdom of Nova: Grand Plaza (hub of the capital).
import sys
sys.path.insert(0, 'D:/RPG Maker MV/Project Nova_tools')
from town_kit import *
from nova_maplib import cmd, text, say, page, char, transfer
import kingdom as K

W, H = 44, 32
m = Town(W, H, K.NAMES[K.PLAZA][0], K.NAMES[K.PLAZA][1], ground=COBBLE)
m.bgm = {'name': 'Town2', 'pan': 0, 'pitch': 100, 'volume': 80}
m.bgs = {'name': 'City', 'pan': 0, 'pitch': 100, 'volume': 45}

# ---------------------------------------------------------------- square
m.rect(12, 11, 31, 22, COB_G)                  # stone slabs
m.relief(16, 12, 27, 21)                       # carved relief ring around the fountain
m.rect(19, 14, 24, 19, PORT_WATER)             # fountain basin (port water has its own stone rim)

# ---------------------------------------------------------------- north row (tall buildings, roofs run off the top)
# NW: Royal Gazette (3 storeys) | Adventurers' Guild (2 storeys, wide)
gz = m.building(2, 8, 0, 2, 7, 'indigo', 'white', win_tiles=(WIN, WIN_FLOWER_P))
m.put(5, gz - 1, SIGN['blank'])
y = m.building(9, 17, 0, 3, 6, 'red', 'brickstone', win_tiles=(LG_TOP,), windows=False)
for x in (10, 12, 14, 16): m.put(x, 5, WIN_FLOWER_G); m.put(x, 7, LG_TOP); m.put(x, 8, LG_BOT)
m.put(13, 7, SIGN['crest']); m.put(11, 4, CHIMNEY_B)
m.tall(9, 5, BANNER_GREEN); m.tall(17, 5, BANNER_GREEN)
# NE: Royal Bank of Nova (white, banners) | Clocktower apartments (3 storeys)
y = m.building(26, 33, 0, 2, 7, 'blue', 'white', windows=False)
for x in (27, 29, 30, 32): m.put(x, 4, MID_WIN)
for x in (27, 32): m.tall(x, 6, BANNER_RED)
m.put(29, 7, SIGN['coin']); m.put(30, 7, SIGN['coin'])
m.put(28, 7, LG_TOP); m.put(28, 8, LG_BOT); m.put(31, 7, LG_TOP); m.put(31, 8, LG_BOT)
y = m.building(34, 41, 0, 2, 7, 'khaki', 'tudor', win_tiles=(WIN, WIN_FLOWER_P, WIN_FLOWER_G))
m.put(36, 1, CHIMNEY_A); m.put(40, 1, CHIMNEY_B)
m.building(42, 43, 0, 3, 6, 'green', 'stone', windows=False)

# ---------------------------------------------------------------- west: garden (north) and founder's memorial (south)
m.rect(2, 11, 11, 13, GRASS)
m.big_tree(3, 11); m.big_tree(8, 11)
for x in (2, 6, 11): m.put(x, 13, FLOWERS[x % 4])
m.rect(2, 20, 11, 25, GRASS)
m.rect(5, 21, 8, 24, COBBLE)
m.tall(6, 21, STATUE_A); m.put(5, 22, FLOWER_BUSH); m.put(7, 22, FLOWER_BUSH)
m.put(5, 24, FLOWERS[1]); m.put(8, 24, FLOWERS[2])
m.big_tree(2, 20, BIG_TREE2); m.big_tree(10, 20, BIG_TREE2)
for x in (3, 10): m.put(x, 25, BUSH_S)

# ---------------------------------------------------------------- east: notice board & flower sellers
m.rect(33, 11, 42, 13, GRASS)
m.big_tree(34, 11); m.big_tree(40, 11)
m.put(37, 13, NOTICE_BOARD)
m.tent(34, 20); m.tent(38, 20)
for x, t in ((34, FLOWERS[0]), (35, FLOWERS[2]), (36, FLOWERS[3]), (38, FLOWERS[1]), (39, FLOWER_BUSH), (40, FLOWERS[0])):
    m.put(x, 23, t)
m.put(42, 22, BUCKET); m.put(33, 23, POT)

# ---------------------------------------------------------------- south blocks: roofs facing the plaza, facades on the lower street
m.building(0, 8, 23, 3, 4, 'orange', 'plaster', win_tiles=(WIN, WIN_FLOWER_P))
m.building(9, 17, 23, 3, 4, 'dressed', 'brick', win_tiles=(WIN,))
m.building(26, 34, 23, 3, 4, 'red', 'tudor', win_tiles=(WIN_FLOWER_G, WIN))
m.building(35, 43, 23, 3, 4, 'indigo', 'brickstone', win_tiles=(WIN,))
for x in (4, 13, 30, 39): m.put(x, 24, CHIMNEY_A)
m.put(13, 29, SIGN['eatery']); m.put(39, 29, SIGN['tea'])
# lower street y30..31 is the cobble ground

# ---------------------------------------------------------------- lamps around the square
for x, yy in ((13, 12), (30, 12), (13, 21), (30, 21), (18, 10), (25, 10), (18, 22), (25, 22)):
    m.lamp(x, yy)


# ---------------------------------------------------------------- avenue dressing
for yy in (2, 5, 8):
    m.put(18, yy, POT); m.put(25, yy, POT)
m.put(42, 14, BARREL); m.put(43, 14, CRATE); m.put(0, 19, BARREL)
m.put(30, 31, CRATE_APPLE); m.put(15, 31, BARREL)

# ---------------------------------------------------------------- events
# fountain jets (animated)
for x in (21, 22):
    m.obj('Fountain', x, 16, '!Other2', 2, ['The fountain of King Aurelian.', 'Coins glitter at the bottom of the basin.'])
# doors
m.locked_door('Royal Gazette', 5, gz, ['A notice on the door:', '"The Royal Gazette - next issue at dawn."'])
m.locked_door("Adventurers' Guild", 13, 8, ['The old Guild Hall. A notice on the door:',
              '"The Adventurers\' Guild now takes missions at', 'the Lion\'s Rest, Baker\'s Lane."'], style=1)
m.locked_door('Royal Bank', 29, 8, ['The Royal Bank of Nova.', 'Two guards eye you from behind the window.'], style=1)
m.locked_door('Clocktower Apartments', 37, 8, ['The door is locked.'])
m.locked_door('Gull & Kettle Eatery', 13, 29, ['The Gull & Kettle.', 'Smells of fish stew. Closed until dinner.'])
m.locked_door('Teahouse', 39, 29, ['A small teahouse. The shutters are drawn.'])
m.sign('Notice Board', 37, 13, ['\\C[6]Notice Board\\C[0]',
       'WANTED: escorts for the Saltwind Harbor caravans.',
       'LOST: grey tabby, answers to "Biscuit". - Whisker & Paw'])
m.sign("Founder's Statue", 6, 22, ['\\C[6]Aurelian I, Founder of Nova\\C[0]',
       '"Let every street lead home, and every home to the crown."'])
# exits
for x in (0, 1): m.put(x, 0, BARRICADE_H)      # the NW alley is closed (Baker's Lane lies west of Lantern Row)
m.exit('To Residential', [(0, y) for y in range(15, 19)], K.RESIDENTIAL, 42, 15, 4)
m.exit('To Market', [(W - 1, y) for y in range(15, 19)], K.MARKET, 1, 15, 6)
for i, x in enumerate(range(19, 25)):          # the south road leaves the city through the Main Gate (5-wide bridge)
    g = K.ARRIVE['gate_from_plaza']
    m.add_event('To Main Gate %d' % (i + 1), x, H - 1, [L.exit_page(g[0], min(max(x - 1, g[1] - 2), g[1] + 2), g[2], 2)])
m.exit('To Castle', [(x, 0) for x in range(19, 25)], K.CASTLE_APPROACH, 31, 32, 8)
# people
m.obj('Carriage', 18, 7, 'Vehicle', 5, ["A noble's carriage, waiting for its owner."], step=False, direction=4)
m.obj('Carriage Horse', 19, 7, 'Nature', 3, ['The horse snorts and stamps a hoof.'], step=False, direction=2)
m.npc('Avenue Guard', 19, 4, 'People3', 6, ('Royal Guard:', 'The Royal Avenue leads to the castle gate.'), direction=6)
m.npc('Avenue Guard', 24, 4, 'People3', 7, ('Royal Guard:', "Sheathe your weapons in the King's presence."), direction=4)
m.npc('Coachman', 25, 7, 'People1', 6, ('Coachman:', 'Lady Evelyn is at the bank again.', 'I could wait here all day, and often do.'), direction=4)
m.npc('Plaza Guard', 18, 12, 'People3', 6, ('Royal Guard:', 'The castle lies north along the Royal Avenue.',
      'The market is east, the harbor south.'), direction=2)
m.npc('Plaza Guard', 25, 12, 'People3', 7, ('Royal Guard:', 'Keep the peace in the King\'s square.'), direction=2)
m.npc('Bard', 16, 19, 'People2', 6, ('Bard:', '♪ Oh the Snowblade came from the East... ♪', 'Spare a coin for a song?'), direction=6)
m.npc('Flower Girl', 36, 22, 'People1', 3, ('Flower Girl:', 'Fresh lilies from the valley!', 'They say the Queen loves white roses.'), direction=8)
m.npc('Flower Seller', 39, 22, 'People4', 1, ('Flower Seller:', 'Every bloom here was cut this morning.'), direction=8)
m.npc('Old Scholar', 8, 22, 'People2', 2, ('Old Scholar:', 'Aurelian founded Nova on a fishing village.',
      'The harbor is older than the crown itself.'), direction=8)
m.npc('Townsman', 27, 17, 'People1', 0, ('Townsman:', 'Have you tried the Golden Crust bakery?', 'Through the alley at the north-west corner.'), move=1)
m.npc('Child', 17, 14, 'People4', 3, ('Child:', 'I threw a coin in the fountain and wished for a dragon!'), move=1, speed=4)
m.npc('Merchant', 34, 16, 'People2', 3, ('Traveling Merchant:', 'The Market District is just east of here.', 'Best prices in the kingdom - or so they say.'), move=1, freq=2)
m.critter('Stray Cat', 4, 17, 'Nature', 1, 'Cat', 'Meow?', move=1)
m.npc('Lady', 21, 20, 'People3', 3, ('Noble Lady:', 'The square is lovely at dusk, when the lamps are lit.'), direction=8)

# ---------------------------------------------------------------- touch-ups made by hand in the editor (Oct 2026)
m.put(27, 4, 0, 2); m.put(27, 4, 32, 3); m.put(29, 4, 0, 2); m.put(29, 4, 32, 3); m.put(30, 4, 0, 2); m.put(30, 4, 32, 3); m.put(32, 4, 0, 2); m.put(32, 4, 32, 3)
m.put(2, 19, 112, 3); m.put(3, 19, 113, 3); m.put(10, 19, 112, 3); m.put(11, 19, 113, 3)
m.put(1, 20, 112, 3); m.put(4, 20, 113, 3); m.put(9, 20, 112, 3); m.put(12, 20, 113, 3)
m.put(1, 21, 120, 3); m.put(4, 21, 121, 3); m.put(9, 21, 120, 3); m.put(12, 21, 121, 3)
m.put(2, 22, 120, 3); m.put(3, 22, 121, 3); m.put(10, 22, 120, 3); m.put(11, 22, 121, 3)
m.put(4, 29, 71, 3)
ev049 = page(char('!Door1', 2))                   # door placed in the editor, not wired up yet
ev049['moveRoute']['skippable'] = False
m.add_event('EV049', 4, 29, [ev049])

if __name__ == '__main__':
    out = sys.argv[1] if len(sys.argv) > 1 else None
    if out: m.render(out, scale=0.5, grid='--grid' in sys.argv)
    if '--save' in sys.argv: m.save(K.PLAZA, parent_id=0, order=3, expanded=True)
