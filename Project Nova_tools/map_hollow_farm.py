# MAP024 - Hollow Farm: the farmland outside the city wall, west of the Main Gate (fields lay outside the walls in
# medieval towns). The wall and moat carry on along the top from the Main Gate map, with the gap where Lantern
# Row's canal leaves the city and falls into the moat; below them the farmhouse,
# a red barn, the horse paddock, the chicken run, two crop fields and a duck pond.
#   python map_hollow_farm.py preview.png [--grid]   -> preview image
#   python map_hollow_farm.py --save                 -> write Map024 (editor must be closed)
import sys, os, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from town_kit import *
from nova_maplib import page, char, text
import nova_maplib as L
import kingdom as K

W, H = 40, 31
m = Town(W, H, K.NAMES[K.HOLLOW_FARM][0], K.NAMES[K.HOLLOW_FARM][1], ground=GRASS)
m.bgm = {'name': 'Field1', 'pan': 0, 'pitch': 100, 'volume': 70}
m.note += '\n<bloom: 0.2>'
rnd = random.Random(24)
P = PROP
RY = K.ARRIVE['farm_from_gate'][2]          # the road from the Main Gate, y19..21

# ---------------------------------------------------------------- the city wall and moat (as on the Main Gate map)
m.rect(0, 0, W - 1, 4, CASTLE_TOP)
m.rect(0, 5, W - 1, 10, CASTLE_WALL)
for x0, x1, roof in ((0, 5, 'green'), (6, 12, 'orange'), (13, 18, 'indigo'), (19, 25, 'red'), (26, 31, 'khaki'), (32, 39, 'blue')):
    m.rect(x0, 0, x1, 1, ('A3', ROOF[roof]))
for x0 in (8, 28):                             # wall towers
    for i, (a, b) in enumerate([(176, 177), (184, 185), (192, 193), (200, 201), (192, 193), (208, 209)]):
        m.put(x0, 4 + i, C_ + a, 3 if i < 5 else 2); m.put(x0 + 1, 4 + i, C_ + b, 3 if i < 5 else 2)
for x in (3, 15, 25, 35): m.tall(x, 6, BANNER_RED)
m.rect(0, 11, W - 1, 14, WATER)
# Lantern Row's canal comes out of the city through a gap in the wall (same columns) and falls into the moat;
# the wall walk crosses it on a bridge
CX = (21, 22)
m.rect(CX[0], 0, CX[1], 10, CANAL)
for y in (2, 3, 4):
    for x in range(CX[0] - 1, CX[1] + 2): m.put(x, y, STONE_BRIDGE_H)

# ---------------------------------------------------------------- the farm road and the yard
road = set()
def dirt(x0, y0, x1, y1):
    m.rect(x0, y0, x1, y1, DIRT)
    road.update((x, y) for x in range(x0, x1 + 1) for y in range(y0, y1 + 1))
dirt(14, RY, W - 1, RY + 2)                    # in from the Main Gate, along the foot of the moat
dirt(4, RY, 21, 24)                            # the farmyard

# farmhouse and the red barn face the road from the north
fh = m.building(13, 21, 15, 2, 2, 'thatch', 'log', windows=False)
for x in (14, 16, 20): m.put(x, fh - 1, WIN_FLOWER_G)
m.put(18, fh - 1, WIN)
m.put(15, 16, CHIMNEY_A)
bn = m.building(2, 9, 15, 2, 2, 'red', 'boards', windows=False)
m.put(5, bn, ARCH_BOT); m.put(5, bn - 1, ARCH_TOP)
m.put(3, bn - 1, WIN_SHUT); m.put(8, bn - 1, WIN_SHUT)
for x, y in ((2, bn + 1), (3, bn + 1), (10, 22), (10, 23)): m.put(x, y, HAY)
m.put(11, 20, WELL); m.put(22, fh, BARREL); m.put(23, fh, BARREL); m.put(20, 24, FIREWOOD)
m.put(8, bn + 1, P['tub_a'])

# horse paddock (south-west) and chicken run, behind the yard
m.rect(1, 26, 11, 29, DIRT)
m.rect(0, 25, 12, 25, FENCE, layer=1); m.rect(0, 30, 12, 30, FENCE, layer=1)
m.rect(0, 25, 0, 30, FENCE, layer=1); m.rect(12, 25, 12, 30, FENCE, layer=1)
for x in (5, 6, 7): m.cell(x, 25, None, 1)       # paddock gate, left open (the horses wander inside only)
m.put(2, 27, HAY); m.put(10, 29, P['tub_a'])
m.rect(15, 26, 21, 29, DIRT)
m.rect(14, 25, 22, 25, FENCE, layer=1); m.rect(14, 30, 22, 30, FENCE, layer=1)
m.rect(14, 25, 14, 30, FENCE, layer=1); m.rect(22, 25, 22, 30, FENCE, layer=1)
m.cell(18, 25, None, 1)
m.put(21, 27, HAY); m.put(15, 29, BASIN)

# crop fields east of the yard: a narrow one between the moat and the road, a big one south of it
def field(x0, x1, fy0, fy1, crop_rows, gate):
    m.rect(x0, fy0 + 1, x1, fy1 - 1, DIRT)
    for y in crop_rows:
        for x in range(x0 + 1, x1): m.put(x, y, CROPS[(x // 3 + y) % 4])
    m.rect(x0 - 1, fy0, x1 + 1, fy0, FENCE, layer=1); m.rect(x0 - 1, fy1, x1 + 1, fy1, FENCE, layer=1)
    m.rect(x0 - 1, fy0, x0 - 1, fy1, FENCE, layer=1); m.rect(x1 + 1, fy0, x1 + 1, fy1, FENCE, layer=1)
    m.cell(gate[0], gate[1], None, 1)
    road.update((x, y) for x in range(x0 - 1, x1 + 2) for y in range(fy0, fy1 + 1))
field(25, 37, 15, 18, (16, 17), (31, 18))
field(25, 37, 23, H - 1, (24, 26, 28), (31, 23))
m.put(33, 26, SCARECROW)

# duck pond (west of the yard, below the barn)
m.rect(0, 20, 2, 23, WATER)
m.put(3, 23, FERN); m.put(3, 20, FLOWERS[1])

# ---------------------------------------------------------------- grass dressing, a few trees on the east strip
taken = set(road) | {(x, y) for x in range(0, 24) for y in range(15, H)}
for x, y in ((39, 16), (38, 25), (39, 28)):
    m.put(x, y - 1, TREE_S1, 3); m.put(x, y, TREE_S3); taken |= {(x, y), (x, y - 1)}
for i in range(20):
    x, y = rnd.randrange(0, W), rnd.randrange(15, H)
    if (x, y) not in taken:
        m.put(x, y, rnd.choice(GRASS_TUFTS + FLOWERS)); taken.add((x, y))
for x, y in ((24, 16), (38, 22)):
    if (x, y) not in road: m.put(x, y, BOULDER_B)

# ---------------------------------------------------------------- events
m.exit('To Main Gate', [(W - 1, y) for y in range(RY, RY + 3)], *K.ARRIVE['gate_from_farm'])
m.locked_door('Farmhouse', 17, fh, ['Something good is baking inside.', 'Nobody answers the knock.'])
m.locked_door('Barn', 5, bn, ['The barn smells of hay and horses.', 'The doors are barred for the night... or the day.'], style=1)
m.npc('Rancher Bram', 15, 19, 'People1', 1, ('Rancher Bram:', 'Welcome to Hollow Farm! Best horses in the west.',
      'The royal stables buy from me - but don\'t tell the Knights.'), direction=2)
m.npc('Farmhand', 29, 22, 'People4', 0, ('Farmhand:', 'Turnips to the north field, beans to the south.',
      'And the crows get whatever we don\'t guard.'), move=1, freq=2)
m.npc('Farm Girl', 19, 27, 'People2', 1, ('Farm Girl:', 'This one is Duchess. She lays the biggest eggs.',
      'That one is also Duchess. They are all Duchess.'), direction=4)
m.critter('Farm Dog', 7, 23, 'Nature', 0, 'Dog', 'The dog wags its whole body.', move=1)
for x, y in ((3, 27), (7, 28), (10, 26)):
    m.critter('Horse', x, y, 'Horses', rnd.randrange(4), 'Horse', 'The horse snorts and nudges your shoulder.', move=1, freq=2,
              area=(1, 26, 11, 29))
for x, y in ((16, 27), (20, 26), (17, 28)):
    m.critter('Chicken', x, y, 'Nature', 2, None, 'Bawk! Bawk!', move=1, freq=4, area=(15, 26, 21, 29))

if __name__ == '__main__':
    out = next((a for a in sys.argv[1:] if not a.startswith('--')), None)
    if out: m.render(out, scale=0.5, grid='--grid' in sys.argv)
    if '--save' in sys.argv:
        m.save(K.HOLLOW_FARM, parent_id=K.PLAZA, order=K.HOLLOW_FARM)
        print('saved Map%03d' % K.HOLLOW_FARM)
