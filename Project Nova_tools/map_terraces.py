# MAP026 - Hearthstone Terraces: the commoners' housing north of Lantern Row, packed against the castle wall and moat
# (they carry on from Castle Approach to the east, and so does the moat walk); the canal leaves the moat here and
# runs down into Lantern Row's canal.
# (inside the walls land was scarce, so ordinary houses stood close together). Rows of terrace houses on two
# streets, a shared courtyard with the well and the washing lines, a carpenter's and a tailor's workshop, and
# the Royal Prison yard's wall along the east side (Castle Approach lies beyond it).
# Lantern Row's north lane (x37..40) comes in at the bottom.
#   python map_terraces.py preview.png [--grid]   -> preview image
#   python map_terraces.py --save                 -> write Map026 (editor must be closed)
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from town_kit import *
from nova_maplib import page, char, text
import nova_maplib as L
import kingdom as K
from town_kit import wander_route

W, H = 44, 38
m = Town(W, H, K.NAMES[K.TERRACES][0], K.NAMES[K.TERRACES][1], ground=COBBLE)
m.bgm = {'name': 'Town2', 'pan': 0, 'pitch': 100, 'volume': 70}
P = PROP
LX = (37, 40)                                   # the lane down to Lantern Row
WALK = 14                                       # the moat walk, in line with Castle Approach's
OY = 6                                          # everything below the moat walk starts 6 rows lower than Wall Street did
CX = (21, 22)                                   # the canal: out of the moat, down into Lantern Row's canal (same columns)
assert K.ARRIVE['terraces_from_residential'][1:3] == (LX[0], H - 2) and K.ARRIVE['residential_from_terraces'][1] == LX[0]
assert K.ARRIVE['terraces_from_castle'][2] == WALK

# ---------------------------------------------------------------- the castle wall and moat (carrying on from Castle Approach)
m.rect(0, 0, W - 1, 4, CASTLE_TOP)
m.rect(0, 5, W - 1, 10, CASTLE_WALL)
m.rect(14, 0, W - 1, 1, ('A3', ROOF['indigo']))  # the keep's slate roof, as on Castle Approach
m.put(36, 0, C_ + 194, 3); m.put(37, 0, C_ + 195, 3); m.put(36, 1, C_ + 202, 3); m.put(37, 1, C_ + 203, 3)
for x0 in (8, 26):                              # wall towers
    for i, (a, b) in enumerate([(176, 177), (184, 185), (192, 193), (200, 201), (192, 193), (208, 209)]):
        m.put(x0, 4 + i, C_ + a, 3 if i < 5 else 2); m.put(x0 + 1, 4 + i, C_ + b, 3 if i < 5 else 2)
for x in (3, 14, 20, 32, 40): m.tall(x, 6, BANNER_RED)
m.rect(0, 11, W - 1, 13, WATER)
# the moat walk (y14) runs on east into Castle Approach; below it the Royal Prison yard wall closes the east side
m.rect(W - 2, WALK + 1, W - 1, H - 1, FORT_TOP)

# ---------------------------------------------------------------- the canal, with stone bridges where the streets cross it
m.rect(CX[0], WALK, CX[1], H - 1, CANAL)
def bridge(y0, y1):
    for y in range(y0, y1 + 1):
        for x in range(CX[0] - 1, CX[1] + 2): m.put(x, y, STONE_BRIDGE_H)
bridge(WALK, WALK + 1)                          # the moat walk
bridge(22, 24)                                  # Hearth Street
bridge(27 + OY, 27 + OY)                        # the back lane
for y in (18, 30): m.lamp(CX[0] - 1, y); m.lamp(CX[1] + 1, y)

# ---------------------------------------------------------------- north terrace: houses in a row along the moat walk, split by the canal
houses = []
for x0, x1, roof, wall, wins in ((0, 5, 'red', 'plaster', (WIN_FLOWER_P, WIN)), (6, 12, 'green', 'tudor', (WIN,)),
                                 (13, 19, 'orange', 'brick', (WIN_FLOWER_G,)), (24, 29, 'indigo', 'plaster', (WIN, WIN_FLOWER_P)),
                                 (30, 34, 'blue', 'white', (MID_WIN,))):
    door = (x0 + x1 + 1) // 2
    b = m.building(x0, x1, 10 + OY, 2, 4, roof, wall, win_tiles=wins, door=door)
    houses.append((door, b))
    m.put(x0 + 1, 11 + OY, CHIMNEY_A)
# workshops east of the terrace, up to the lane: carpenter
cw = m.building(35, 41, 10 + OY, 2, 4, 'wood', 'boards', windows=False)
m.put(36, cw - 1, WIN_SHUT); m.put(40, cw - 1, WIN_SHUT); m.put(38, cw - 2, SIGN['hammer'])
for x_, t in ((35, LOG), (36, FIREWOOD), (41, P['hammers'])): m.put(x_, cw + 1, t)

# ---------------------------------------------------------------- Hearth Street
for x_ in (4, 16, 28): m.lamp(x_, 18 + OY)

# ---------------------------------------------------------------- south block: courtyard in the middle, houses either side
s0 = m.building(0, 9, 19 + OY, 2, 4, 'orange', 'plaster', win_tiles=(WIN, WIN_FLOWER_G), door=4)
s1 = m.building(26, 34, 19 + OY, 2, 4, 'red', 'tudor', windows=False)      # tailor
for x_ in (27, 29, 33): m.put(x_, s1 - 1, WIN_FLOWER_P)
m.put(30, s1 - 2, P['cape_stand'])
# the courtyard (west bank of the canal)
m.rect(11, 19 + OY, 19, 25 + OY, GRASS)
m.rect(11, 22 + OY, 19, 22 + OY, ROAD); m.rect(15, 19 + OY, 16, 25 + OY, ROAD)
m.put(16, 23 + OY, WELL)
m.put(12, 20 + OY, P['mens_clothes']); m.put(13, 20 + OY, P['robe_b']); m.put(14, 20 + OY, P['cape_stand'])
m.put(18, 24 + OY, P['mens_clothes']); m.put(19, 24 + OY, P['robe_b'])
m.put(12, 24 + OY, BUCKET); m.put(13, 24 + OY, P['basket_empty']); m.put(18, 20 + OY, BASIN)
m.put(19, 19 + OY, TREE_S1, 3); m.put(19, 20 + OY, TREE_S3); m.put(11, 24 + OY, FLOWER_BUSH)
m.rect(11, 25 + OY, 19, 25 + OY, HEDGE_TOP); m.rect(15, 25 + OY, 16, 25 + OY, ROAD)
# east bank: a little garden between the canal and the tailor's
m.rect(24, 19 + OY, 25, 25 + OY, GRASS)
m.put(24, 20 + OY, FLOWERS[0]); m.put(25, 23 + OY, FLOWER_BUSH); m.put(24, 25 + OY, FLOWERS[2])

# ---------------------------------------------------------------- the bottom: back gardens and the roofs of Lantern Row's houses
m.rect(0, 27 + OY, 35, 27 + OY, COBBLE)
m.building(0, 9, 28 + OY, 4, 0, 'indigo', 'plaster', windows=False)
m.building(10, 19, 28 + OY, 4, 0, 'green', 'plaster', windows=False)
m.building(24, 35, 28 + OY, 4, 0, 'orange', 'plaster', windows=False)
m.building(41, 41, 28 + OY, 4, 0, 'blue', 'plaster', windows=False)
for x_ in (4, 16, 30): m.put(x_, 29 + OY, CHIMNEY_A)
for x_, y_ in ((10, 26), (25, 26), (35, 26)): m.put(x_, y_ + OY, POT)

# ---------------------------------------------------------------- events
m.exit('To Lantern Row', [(x_, H - 1) for x_ in range(LX[0], LX[1] + 1)], *K.ARRIVE['residential_from_terraces'])
m.exit('To Castle Approach', [(W - 1, WALK)], *K.ARRIVE['castle_from_terraces'])
lines = [['A baby is crying inside. The door stays shut.'], ['"Not today, thank you!"'],
         ['The door is locked. Someone is frying onions.'], ['A note: "At the market - back by noon."'],
         ['The door is locked.'], ['An old man shouts: "If it\'s about the rent, I paid!"']]
for (dx, by), ln in zip(houses, lines):
    m.locked_door('Terrace House', dx, by, ln, style=(dx % 2))
m.locked_door('House', 4, s0, ['The door is locked. Children giggle behind it.'])
m.locked_door("Carpenter's Workshop", 38, cw, ['The carpenter is out buying timber.'], style=1)
m.locked_door("Tailor's Shop", 31, s1, ['"Closed - fitting at the Royal Chancery."'])
m.npc('Washerwoman', 13, 21 + OY, 'People1', 4, ('Washerwoman:', 'Half the city\'s shirts hang in this yard.',
      'The other half should.'), direction=8)
m.npc('Old Tomas', 17, 23 + OY, 'People4', 3, ('Old Tomas:', 'Forty years by this well. I\'ve heard every rumour in Nova.',
      'Lately they\'re all about the castle.'), direction=4)
m.npc('Child', 15, 17 + OY, 'People2', 0, ('Child:', 'Tag! You\'re it!'), move=1, freq=5, speed=4)
m.npc('Child', 22, 17 + OY, 'People1', 5, ('Child:', 'You can\'t catch me!'), move=1, freq=5, speed=4)
m.npc('Carpenter\'s Apprentice', 36, cw + 2, 'People4', 0, ('Apprentice:', 'The master says the Royal Archives want new shelves.',
      'Scrolls are heavier than you\'d think.'), direction=2)
m.npc('Watchman', LX[0] + 1, 24 + OY, 'People3', 6, ('Watchman:', 'Hearthstone Terraces. Quiet folk, mostly.',
      'The castle wall up there keeps the north wind out.'), route=wander_route('UUUUWDDDDW'), speed=2)
m.npc('Canal Fisher', CX[0] - 1, 20, 'People4', 6, ('Canal Fisher:', 'The canal runs from the castle moat, right through',
      'Lantern Row and out under the wall to Hollow Farm.', 'Not a single fish in it, mind. I keep trying.'), direction=6)
m.critter('Stray Cat', 26, 26 + OY, 'Nature', 1, 'Cat', 'The cat ignores you completely.', move=1)

if __name__ == '__main__':
    out = next((a for a in sys.argv[1:] if not a.startswith('--')), None)
    if out: m.render(out, scale=0.5, grid='--grid' in sys.argv)
    if '--save' in sys.argv:
        m.save(K.TERRACES, parent_id=K.PLAZA, order=K.TERRACES)
        print('saved Map%03d' % K.TERRACES)
