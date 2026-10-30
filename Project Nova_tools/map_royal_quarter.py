# MAP025 - Royal Quarter: beside the castle, east of Castle Approach - the offices of the royal clan and the
# houses of the court (in medieval towns the nobility lived close to the castle). The castle wall and moat carry
# on along the top; the moat walk comes in from Castle Approach (west), Crown Avenue runs down to the Market's
# north alley (south). North row: Royal Chancery, Royal Treasury, Royal Archives. South: a noble manor with its
# garden, the Queen's Garden with the founder's statue, and the Royal Chapel.
#   python map_royal_quarter.py preview.png [--grid]   -> preview image
#   python map_royal_quarter.py --save                 -> write Map025 (editor must be closed)
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from town_kit import *
from nova_maplib import page, char, text
import nova_maplib as L
import kingdom as K
from town_kit import wander_route

W, H = 46, 40
m = Town(W, H, K.NAMES[K.ROYAL_QUARTER][0], K.NAMES[K.ROYAL_QUARTER][1], ground=COBBLE)
m.bgm = {'name': 'Castle1', 'pan': 0, 'pitch': 100, 'volume': 70}
P = PROP
AX = (20, 22)                                   # Crown Avenue columns, in line with the Market's north alley
WALK = K.ARRIVE['royal_from_castle'][2]         # the moat walk row from Castle Approach (14)
assert K.ARRIVE['royal_from_market'][1] == AX[0] and WALK == 14

# ---------------------------------------------------------------- castle wall (the keep behind it) and the moat
m.rect(0, 0, W - 1, 4, CASTLE_TOP)
m.rect(0, 5, W - 1, 10, CASTLE_WALL)
m.rect(0, 0, 30, 1, ('A3', ROOF['indigo']))     # the keep's slate roof carries on from Castle Approach
for x0 in (6, 22):
    for i, (a, b) in enumerate([(194, 195), (202, 203)]):
        m.put(x0, i, C_ + a, 3); m.put(x0 + 1, i, C_ + b, 3)
for x0 in (14, 34):                             # wall towers
    for i, (a, b) in enumerate([(176, 177), (184, 185), (192, 193), (200, 201), (192, 193), (208, 209)]):
        m.put(x0, 4 + i, C_ + a, 3 if i < 5 else 2); m.put(x0 + 1, 4 + i, C_ + b, 3 if i < 5 else 2)
for x in (3, 10, 19, 26, 30, 39, 43): m.tall(x, 6, BANNER_BLUE)
for x in (8, 24): m.put(x, 8, STAINED)
m.rect(0, 11, W - 1, 13, WATER)

# ---------------------------------------------------------------- streets
# (the cobbled ground is the streets: the moat walk widening into Court Row y14..16, Crown Avenue down the
#  middle, Chancery Street y25..28 - same grey cobbles as Castle Approach's moat walk)

# ---------------------------------------------------------------- north row: the offices of the crown
ch = m.building(1, 17, 17, 3, 5, 'blue', 'white', windows=False)            # Royal Chancery (offices)
for x in (2, 4, 6, 12, 14, 16):
    m.put(x, ch - 1, MID_WIN); m.put(x, ch - 3, MID_WIN)
m.put(9, ch - 1, ARCH_BOT); m.put(9, ch - 2, ARCH_TOP)
m.tall(8, ch - 4, BANNER_BLUE); m.tall(10, ch - 4, BANNER_BLUE)
m.put(9, ch - 4, SIGN['crest'])
tr = m.building(25, 33, 17, 3, 5, 'metal', 'stone', windows=False)          # Royal Treasury
for x in (26, 32): m.put(x, tr - 2, 41)                                     # barred windows
m.put(29, tr - 3, SIGN['coin'])
ar = m.building(35, 44, 17, 3, 5, 'indigo', 'brickstone', windows=False)    # Royal Archives
for x in (36, 38, 42, 44):
    m.put(x, ar - 1, WIN); m.put(x, ar - 3, WIN)
m.put(40, ar - 3, SIGN['magic'])
for x in (1, 17, 25, 33, 35, 44): m.put(x, 24, POT)
for x in (3, 15, 27, 37): m.lamp(x, 28)

# ---------------------------------------------------------------- south-west: a noble manor and its garden
mn = m.building(1, 14, 29, 3, 4, 'red', 'tudor', windows=False)
for x in (2, 4, 10, 12):
    m.put(x, mn - 1, WIN_FLOWER_P); m.put(x, mn - 3, WIN)
m.put(7, mn - 1, LG_TOP)
m.put(4, 30, CHIMNEY_B); m.put(11, 30, CHIMNEY_B)
m.rect(0, mn + 1, 17, H - 1, GRASS)
m.rect(6, mn + 1, 8, H - 1, ROAD)                # garden path
m.rect(0, H - 1, 17, H - 1, HEDGE_TOP)
m.rect(17, mn + 1, 17, H - 1, HEDGE_TOP)
for x, y, t in ((2, 36, FLOWER_BUSH), (4, 37, FLOWERS[0]), (11, 36, FLOWER_BUSH), (13, 37, FLOWERS[2]),
                (15, 35, FLOWERS[3]), (1, 38, FERN), (10, 38, FLOWERS[1])):
    m.put(x, y, t)
m.put(3, 34, TREE_S1, 3); m.put(3, 35, TREE_S3); m.put(14, 37, TREE_S1, 3); m.put(14, 38, TREE_S3)
m.cell(6, H - 1, ROAD); m.cell(7, H - 1, ROAD); m.cell(8, H - 1, ROAD)
m.cell(17, mn + 1, COBBLE)                    # gap in the hedge onto Crown Avenue
m.rect(9, mn + 1, 16, mn + 1, ROAD)

# ---------------------------------------------------------------- south-east: the Queen's Garden and the Royal Chapel
m.rect(24, 29, W - 1, H - 1, GRASS)
cp = m.building(33, 44, 29, 4, 5, 'dressed', 'white', windows=False)        # Royal Chapel
for x in (34, 36, 41, 43): m.put(x, cp - 2, STAINED)
m.put(38, cp, ARCH_BOT); m.put(38, cp - 1, ARCH_TOP); m.put(39, cp, ARCH_BOT); m.put(39, cp - 1, ARCH_TOP)
m.rect(38, cp + 1, 39, H - 1, ROAD)
# the garden: hedged beds round the founder's statue
m.relief(26, 31, 30, 35)
m.tall(28, 32, STATUE_A)
for x, y in ((26, 31), (30, 31), (26, 35), (30, 35)): m.put(x, y, FLOWER_BUSH)
m.rect(24, 30, 24, H - 2, HEDGE_TOP)
m.rect(24, 38, 32, 38, HEDGE_TOP)
m.cell(24, 33, ROAD); m.rect(25, 33, 25, 33, ROAD)
for x, y in ((32, 30), (25, 37)): m.put(x, y, TREE_S1, 3); m.put(x, y + 1, TREE_S3)
for x, y, t in ((27, 37, FLOWERS[0]), (29, 37, FLOWERS[3]), (31, 33, FLOWERS[1]), (36, 38, FLOWERS[2]), (42, 38, FERN)):
    m.put(x, y, t)
for y in (31, 36): m.lamp(AX[0] - 1, y); m.lamp(AX[1] + 1, y)

# ---------------------------------------------------------------- events
m.exit('To Castle Approach', [(0, WALK)], *K.ARRIVE['castle_from_royal'])
for y in (WALK + 1, WALK + 2): m.put(0, y, BARRICADE_V)          # Castle Approach only has the one-tile walk
m.exit('To Market', [(x, H - 1) for x in range(AX[0], AX[1] + 1)], *K.ARRIVE['market_from_royal'])
m.locked_door('Royal Chancery', 9, ch, ['\\C[6]ROYAL CHANCERY\\C[0]', 'Offices of the royal clan: decrees, seals, petitions.',
              'A clerk calls through the door: "Petitions on Tuesdays!"'], style=1)
m.locked_door('Royal Treasury', 29, tr, ['The Treasury door is iron, three times locked.', 'Two guards watch you read this.'], style=1)
m.locked_door('Royal Archives', 40, ar, ['\\C[6]ROYAL ARCHIVES\\C[0]', 'Every law, census and royal birth since the founding.',
              'Scholars by appointment only.'])
m.locked_door('Valemont Manor', 7, mn, ['A brass plate: \\C[6]House Valemont\\C[0], Keepers of the Royal Seal.',
              'A butler opens the door a crack... and shuts it again.'], style=1)
m.locked_door('Royal Chapel', 38, cp, ['Organ music and the smell of incense.', 'A service is in progress - best not to interrupt.'], style=1)
m.sign('Founder Statue', 28, 34, ['\\C[6]Queen Seraphine the Wise\\C[0]', '"Rule with a ledger in one hand and mercy in the other."'])
m.npc('Royal Guard', AX[0] - 1, WALK + 1, 'People3', 6, ('Royal Guard:', 'The Royal Quarter. Mind your manners -',
      'half the people here outrank the other half.'), direction=2)
m.npc('Treasury Guard', 28, tr + 1, 'People3', 7, ('Treasury Guard:', 'Move along.'), direction=2)
m.npc('Treasury Guard', 30, tr + 1, 'People3', 6, ('Treasury Guard:', '...I said, move along.'), direction=2)
m.npc('Royal Clerk', 12, 26, 'People2', 6, ('Royal Clerk:', 'Seventeen decrees to copy before supper.',
      'The royal clan writes more letters than the whole city.'), route=wander_route('LLLLWRRRRW'), speed=3)
m.npc('Archivist', 41, ar + 1, 'People4', 2, ('Archivist:', 'The Ashveil files? Sealed by order of the Chancellor.',
      'Why do you ask?'), direction=2)
m.npc('Lady Valemont', 10, 36, 'People2', 3, ('Lady Valemont:', 'The roses are late this year.',
      'Everything at court is late this year.'), direction=4)
m.npc('Court Noble', 34, 27, 'People4', 6, ('Court Noble:', 'The King has not held court in weeks.',
      'The Chancellor signs everything now. Curious, isn\'t it?'), move=1, freq=2)
m.npc('Chapel Sister', 39, cp + 2, 'People1', 7, ('Sister Maren:', 'The chapel bells ring for the royal clan only.',
      'But the gods, I think, listen to everyone.'), direction=2)

if __name__ == '__main__':
    out = next((a for a in sys.argv[1:] if not a.startswith('--')), None)
    if out: m.render(out, scale=0.5, grid='--grid' in sys.argv)
    if '--save' in sys.argv:
        m.save(K.ROYAL_QUARTER, parent_id=K.PLAZA, order=K.ROYAL_QUARTER)
        print('saved Map%03d' % K.ROYAL_QUARTER)
