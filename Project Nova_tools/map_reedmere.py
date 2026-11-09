# Reedmere - a fishing village on the west shore of a lake (sample map; not linked into the world yet).
# Inspired by the lakeside villages in Referensi Map (wooden houses along the shore, a store standing out on the
# water at the end of a boardwalk); the layout is our own.
# Thatch-and-log houses round a well green, the Reed & Ripple general store on stilts in the lake, a fishing jetty
# with a moored boat, forest framing the north and west, the road leaving south through a fence gate.
#   python map_reedmere.py preview.png [--grid]   -> preview image
#   python map_reedmere.py --save                 -> write the map (editor must be closed; id set below)
import sys, os, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from town_kit import *
import nova_maplib as L

MAP_ID = None                       # assigned when the map is placed in the world
W, H = 40, 30
m = Town(W, H, 'Reedmere', 'Reedmere', ground=GRASS)
m.bgm = {'name': '03_Valley_Village', 'pan': 0, 'pitch': 100, 'volume': 70}
m.bgs = {'name': 'River', 'pan': 0, 'pitch': 100, 'volume': 35}
m.note += '\n<bloom: 0.2>'
rnd = random.Random(42)
NN = lambda n: L.ext('Nova_Nature', n)
CYPRESS = ((NN(23), NN(31), NN(39)), (NN(30), NN(38)))   # trunk column (tip, body, base), left column (foliage, flowers)
FLOWER_BED = ((NN(24), NN(25)), (NN(32), NN(33)))
taken = set()                       # cells that must stay free of random dressing

def claim(x0, y0, x1, y1):
    taken.update((x, y) for x in range(x0, x1 + 1) for y in range(y0, y1 + 1))

# ---------------------------------------------------------------- the lake (east) - shoreline per row
SHORE = [31, 30, 29, 28, 27, 27, 26, 26, 25, 25, 24, 24, 24, 24, 24, 24, 25, 25, 25, 26,
         26, 26, 27, 27, 28, 29, 30, 31, 32, 33]
for y, sx in enumerate(SHORE):
    m.rect(sx, y, W - 1, y, WATER)
    claim(sx - 1, y, W - 1, y)

# ---------------------------------------------------------------- roads
road = set()
def dirt(x0, y0, x1, y1):
    m.rect(x0, y0, x1, y1, DIRT)
    road.update((x, y) for x in range(x0, x1 + 1) for y in range(y0, y1 + 1))
dirt(10, 21, 12, H - 1)             # the south road
dirt(4, 13, 22, 17)                 # the green's lane in front of the houses
dirt(6, 11, 8, 12); dirt(15, 10, 17, 12)   # doorsteps of the inn and the elder's house
dirt(10, 18, 12, 20)
dirt(22, 13, 23, 14)                # to the boardwalk
dirt(19, 17, 21, 22); dirt(21, 22, 26, 23)  # down to the fishing jetty
dirt(4, 18, 5, 21)                  # to the west cottage
claim(0, 0, -1, -1); taken |= road

# ---------------------------------------------------------------- the store on stilts and its boardwalk
# deck (horizontal plank bridge tiles: top / centre / bottom rows), walkway in from the shore
m.rect(29, 13, 38, 13, A5(PIER_H[0])); m.rect(29, 14, 38, 14, A5(PIER_H[2]))
m.rect(24, 13, 28, 13, A5(PIER_H[0])); m.rect(24, 14, 28, 14, A5(PIER_H[2]))
st = m.building(30, 37, 9, 2, 2, 'thatch', 'boards', windows=False)
m.put(32, st - 1, WIN_FLOWER_G); m.put(36, st - 1, WIN_FLOWER_G); m.put(31, st - 1, WIN)
m.put(35, st, SIGN['item']); m.put(31, st, SIGN['eatery'])
m.put(37, 13, BOLLARD); m.put(38, 14, BOLLARD_ROPE)
for x, t in ((30, CRATE_APPLE), (36, CRATE_CARROT), (37, BARREL)): m.put(x, 14, t)

# fishing jetty (south-east) with the boat tied at its end
m.rect(27, 22, 34, 22, A5(PIER_H[0])); m.rect(27, 23, 34, 23, A5(PIER_H[2]))
m.put(34, 22, BOLLARD); m.put(30, 23, BUCKET); m.put(31, 23, CRATE_GRAIN)
claim(26, 21, 35, 24)

# ---------------------------------------------------------------- houses
# the Willow Rest inn (north-west), the elder's long house (north), two cottages (south-west and south)
inn = m.building(2, 10, 6, 2, 3, 'thatch', 'log', windows=False)
for x in (3, 5, 9): m.put(x, inn - 1, WIN_FLOWER_P)
m.put(4, inn - 2, WIN); m.put(8, inn - 2, WIN)
m.put(8, inn, SIGN['inn']); m.put(4, 7, CHIMNEY_A)
claim(1, 5, 11, inn + 1)

eld = m.building(13, 20, 5, 3, 2, 'wood', 'planks', windows=False)
for x in (14, 18, 19): m.put(x, eld - 1, WIN_SHUT if x == 19 else WIN)
m.put(14, eld, BARREL); m.put(19, eld, FIREWOOD); m.put(18, 6, CHIMNEY_A)
claim(12, 4, 21, eld + 1)

c1 = m.building(1, 6, 18, 2, 2, 'green', 'wood', windows=False)
m.put(2, c1 - 1, WIN_FLOWER_G); m.put(5, c1 - 1, WIN)
claim(0, 17, 7, c1 + 1)

c2 = m.building(14, 18, 20, 2, 2, 'orange', 'log', windows=False)
m.put(15, c2 - 1, WIN); m.put(17, c2 - 1, WIN_FLOWER_G)
claim(13, 19, 19, c2 + 1)
m.rect(14, c2 + 2, 18, c2 + 3, DIRT)        # vegetable patch behind the gate of cottage 2
for x in range(14, 19): m.put(x, c2 + 3, CROPS[x % 4])
m.rect(13, c2 + 4, 19, c2 + 4, FENCE, layer=1)
claim(13, c2 + 2, 19, c2 + 4)

# ---------------------------------------------------------------- the well green
m.put(13, 15, WELL); m.put(11, 13, NOTICE_BOARD)
m.put(20, 13, LAMP[2]); m.put(20, 12, LAMP[1], 3); m.put(20, 11, LAMP[0], 3)
for x, y in ((9, 13), (9, 14)): m.put(x, y, (BARREL, CRATE)[y % 2])
for (x, y) in ((22, 12), (2, 15)):
    m.put(x, y, FLOWER_BED[0][0]); m.put(x + 1, y, FLOWER_BED[0][1])
    m.put(x, y + 1, FLOWER_BED[1][0]); m.put(x + 1, y + 1, FLOWER_BED[1][1])
    claim(x, y, x + 1, y + 1)
claim(8, 12, 23, 17)

# ---------------------------------------------------------------- south fence and gate
m.rect(0, 26, 8, 26, FENCE, layer=1); m.rect(14, 26, 22, 26, FENCE, layer=1)
m.put(9, 25, SIGNPOST)
m.lamp(13, 26)
claim(0, 25, 23, 27)

# ---------------------------------------------------------------- forest frame (north and west), reeds, lilies
def big(x, y):                      # round tree, 2x2 (Outside_B 112/113 over 120/121)
    (a, b), (c, d) = BIG_TREE
    m.put(x, y, a, 3); m.put(x + 1, y, b, 3); m.put(x, y + 1, c); m.put(x + 1, y + 1, d)
    claim(x, y, x + 1, y + 1)

def small(x, y):                    # slim tree, 1x2 (Outside_B 93 over 101)
    m.put(x, y, TREE_S1, 3); m.put(x, y + 1, TREE_S3)
    claim(x, y, x, y + 1)

def cypress(x, y):                  # tall cypress, trunk column x, its left foliage and flowers in column x-1
    (tip, body, base), (side, flowers) = CYPRESS
    m.put(x, y, tip, 3); m.put(x, y + 1, body, 3); m.put(x, y + 2, base)
    m.put(x - 1, y + 1, side, 3); m.put(x - 1, y + 2, flowers)
    claim(x - 1, y, x, y + 2)

for x in range(0, 30, 2): big(x, 0)                       # the forest along the north edge
cypress(2, 2); small(5, 2); big(7, 2); small(11, 2); big(21, 2); cypress(24, 2); small(26, 2)
big(0, 10); small(0, 12); big(0, 14)                     # the west edge
big(1, 23); cypress(1, 27); big(3, 27); cypress(7, 27); small(9, 28)   # south, outside the fence
big(17, 27); small(20, 27); big(23, 25); small(25, 26); big(23, 28)

for y, sx in enumerate(SHORE):          # reeds along the waterline, lily pads just off it
    if (sx - 1, y) not in road and m.get(sx - 1, y) == GRASS and m.top[0][y][sx - 1] == 0 and rnd.random() < 0.55:
        m.put(sx - 1, y, rnd.choice((187, 187, FERN)))
    lx = sx + rnd.randrange(1, 4)
    if rnd.random() < 0.45 and m.get(lx, y) == WATER and m.top[0][y][lx] == 0:
        m.put(lx, y, rnd.choice((189, 190, 191)))

# deep water (overlay) away from the shore, the decks and the store
for y, sx in enumerate(SHORE):
    for x in range(sx + 4, W):
        if all(m.get(x + dx, y + dy) in (WATER, 'edge') for dx in (-1, 0, 1) for dy in (-1, 0, 1)):
            m.cell(x, y, DEEP, 1)

# grass dressing
for i in range(70):
    x, y = rnd.randrange(0, W), rnd.randrange(0, H)
    if (x, y) in taken or m.get(x, y) != GRASS or m.top[0][y][x]: continue
    m.put(x, y, rnd.choice(GRASS_TUFTS + GRASS_TUFTS + FLOWERS + (STUMP, BUSH_S, NN(5), NN(3))))
    taken.add((x, y))

# ---------------------------------------------------------------- events
m.locked_door('Willow Rest Inn', 6, inn, ['The innkeeper is airing out the rooms.', '"Come back at sundown, love!"'])
m.locked_door('Elder\'s House', 16, eld, ['You hear an old man humming behind the door.'])
m.locked_door('West Cottage', 4, c1, ['Fishing nets hang drying on the door.'])
m.locked_door('South Cottage', 16, c2, ['Nobody is home. The garden is very well kept.'])
m.locked_door('Reed & Ripple', 33, st, ['"Fresh catch, bait and rope! Open after the morning haul!"'])
m.sign('Notice Board', 11, 13, ['"Lost: one rowing boat, green, answers to Pip."', '"Found: one rowing boat, green. It was at the jetty."'])
m.sign('Signpost', 9, 25, ['North: Reedmere', 'South: the high road'])

m.npc('Elder Maren', 16, 15, 'People1', 7, ('Elder Maren:', 'Welcome to Reedmere, travellers.',
      'The lake gives us fish, reeds and quiet. Mind you, the quiet is the best of the three.'))
m.npc('Fisher Tobin', 33, 22, 'People4', 2, ('Fisher Tobin:', 'Shh... the perch are biting.',
      'Every morning, same spot, same bucket. Never caught the big one. Yet.'), direction=6)
m.npc('Store Girl Nell', 34, 14, 'People2', 5, ('Nell:', 'Mind the planks - the third one squeaks.',
      'We\'re stocking up before the lake freezes over.'), direction=2)
m.npc('Washerwoman', 23, 17, 'People4', 1, ('Washerwoman:', 'The water\'s so clear here you can count the pebbles.'),
      move=1, freq=2)
m.npc('Boy', 11, 18, 'People1', 0, ('Boy:', 'I\'m going to row out to the middle one day!', 'Mum says not till I can swim.'),
      move=1, freq=4)
m.obj('Boat', 35, 23, 'Vehicle', 0, ['A little green rowing boat. Someone painted "PIP" on the side.'], step=False, direction=4)
m.critter('Cat', 21, 10, 'Nature', 1, 'Cat', 'The cat ignores you magnificently.', move=1, freq=2)
m.critter('Hen', 24, 19, 'Nature', 2, None, 'Bawk! The hen eyes your boots for worms.', move=1, freq=4)

if __name__ == '__main__':
    out = next((a for a in sys.argv[1:] if not a.startswith('--')), None)
    if out: m.render(out, scale=0.5, grid='--grid' in sys.argv)
    if '--save' in sys.argv:
        assert MAP_ID, 'set MAP_ID first'
        m.save(MAP_ID)
        print('saved Map%03d' % MAP_ID)
