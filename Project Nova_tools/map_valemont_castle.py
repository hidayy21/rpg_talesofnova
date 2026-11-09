# Valemont Castle - the courtyard before a castle keep (sample map; not linked into the world yet).
# Inspired by the castle maps in Referensi Map (a keep with flanking round towers across the north, a formal
# courtyard with a fountain on the axis, barracks and stables against the side walls, a towered gate in the south);
# the layout is our own.
# Uses the Avy Castle tileset (14): Avy_Castle_A4 walls, Avy_Castle_B3 towers, Avy_Castle_B doors, PM_Rome_B
# windows, Outside_B/C props through L.ext (the B-E slots of this tileset are the Avy sheets).
#   python map_valemont_castle.py preview.png [--grid]   -> preview image
#   python map_valemont_castle.py --save                 -> write the map (editor must be closed; id set below)
import sys, os, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from town_kit import *
import nova_maplib as L
from nova_maplib import page, char, text

MAP_ID = None                       # assigned when the map is placed in the world
AVY_CASTLE = 14
W, H = 40, 34
OB = lambda n: L.ext('Outside_B', n)
OC = lambda n: L.ext('Outside_C', n - C_ if n >= C_ else n)
AC = lambda n: L.ext('Avy_Castle_B', n)
AC3 = lambda n: L.ext('Avy_Castle_B3', n)
ROME = lambda n: L.ext('PM_Rome_B', n)
NN = lambda n: L.ext('Nova_Nature', n)
KEEP_TOP, KEEP_WALL = ('A4', 0), ('A4', 8)          # Avy_Castle_A4 pale stone
IRON_FENCE = ('A2', 14)
BIG_TOWER = [(None, 68, 69, None), (75, 76, 77, 78), (83, 84, 85, 86), (91, 92, 93, 94),
             (27, 28, 29, 30), (35, 36, 37, 38), (27, 28, 29, 30), (35, 36, 37, 38), (27, 28, 29, 30),
             (35, 36, 37, 38), (43, 44, 45, 46)]
SMALL_TOWER = [(41, 42), (49, 50), (57, 58), (17, 18), (25, 26), (33, 34)]
GREAT_DOOR = ((20, 21), (28, 29))
TALL_WINDOW = (ROME(128), ROME(136))
FLOWERS_PINK = NN(5)                                  # single-tile flower clump

m = Town(W, H, 'Valemont Castle', 'Valemont Castle', ground=GRASS)
m.tileset_id = AVY_CASTLE
m.bgm = {'name': 'Castle1', 'pan': 0, 'pitch': 100, 'volume': 70}
m.note += '\n<bloom: 0.25>'
rnd = random.Random(14)
taken = set()

def claim(x0, y0, x1, y1):
    taken.update((x, y) for x in range(x0, x1 + 1) for y in range(y0, y1 + 1))

def blocker(x, y):
    """Avy tiles are all passable - an empty event stands on tower bases the player could otherwise walk into."""
    m.add_event('Block', x, y, [page(None, priority=1)])

def stamp(x0, y0, rows, f, base_layer=2):
    last = len(rows) - 1
    for r, row in enumerate(rows):
        for c, n in enumerate(row):
            if n is not None: m.put(x0 + c, y0 + r, f(n), base_layer if r == last else 3)

# ---------------------------------------------------------------- the keep (north) with its two great towers
m.rect(0, 0, W - 1, 4, KEEP_TOP)
m.rect(0, 5, W - 1, 10, KEEP_WALL)
for x in (6, 33): m.rect(x, 5, x, 10, ('A4', 26))     # pilaster strips
stamp(19, 9, GREAT_DOOR, AC)
for x in (9, 13, 25, 29):                              # tall windows, two storeys
    m.put(x, 6, TALL_WINDOW[0]); m.put(x, 7, TALL_WINDOW[1])
for x in (2, 36):
    m.put(x, 7, TALL_WINDOW[0]); m.put(x, 8, TALL_WINDOW[1])
for x in (11, 18, 21, 28): m.put(x, 8, OC(BANNER_RED[0])); m.put(x, 9, OC(BANNER_RED[1]))
for x0 in (14, 22):
    stamp(x0, 0, BIG_TOWER, AC3)
    for x in range(x0, x0 + 4): blocker(x, 10)
claim(0, 0, W - 1, 10)

# ---------------------------------------------------------------- the courtyard
m.rect(0, 11, W - 1, 27, GRASS)
m.rect(13, 14, 26, 21, COBBLE)                        # fountain square
m.rect(12, 13, 27, 13, COBBLE); m.rect(16, 22, 23, 22, COBBLE)
m.relief(18, 11, 21, 27)                              # the royal avenue
m.rect(17, 16, 22, 19, WATER)                         # the fountain pool with its angels
m.put(19, 17, OC(ANGEL_A[0]), 3); m.put(19, 18, OC(ANGEL_A[1]))
m.put(20, 17, OC(ANGEL_B[0]), 3); m.put(20, 18, OC(ANGEL_B[1]))
claim(13, 11, 26, 27)
m.rect(0, 11, 17, 12, COBBLE); m.rect(22, 11, 39, 12, COBBLE)   # walk along the keep front
for x in (12, 27): m.rect(x, 13, x, 21, COBBLE)
for x in (16, 23): m.put(x, 14, OB(LAMP[0]), 3); m.put(x, 15, OB(LAMP[1]), 3); m.put(x, 16, OB(LAMP[2]))
for x in (14, 25):
    for y in (15, 20): m.put(x, y, FLOWERS_PINK)
m.put(13, 14, OC(STATUE_A[0]), 3); m.put(13, 15, OC(STATUE_A[1]))
m.put(26, 14, OC(STATUE_A[0]), 3); m.put(26, 15, OC(STATUE_A[1]))

# formal garden beds either side of the avenue, below the square
for x0 in (13, 22):
    m.rect(x0, 23, x0 + 4, 26, BUSH)
    for x in range(x0 + 1, x0 + 4): m.put(x, 24, OB(FLOWERS[(x + x0) % 4])); m.put(x, 25, OB(FLOWERS[(x + 1) % 4]))
    m.rect(x0 + 1, 24, x0 + 3, 25, GRASS)
claim(13, 22, 26, 27)

# ---------------------------------------------------------------- barracks and training yard (west)
br = m.building(1, 9, 14, 2, 3, 'blue', 'stone', windows=False)
for x in (2, 4, 8): m.put(x, br - 1, OB(WIN_SHUT if x == 8 else WIN))
m.put(3, br - 2, OB(WIN)); m.put(7, br - 2, OB(WIN))
m.put(7, br, OB(SIGN['sword'])); m.put(2, br, OB(BARREL)); m.put(9, br, OB(BARREL))
m.put(4, 15, OB(CHIMNEY_A))
claim(0, 13, 10, br + 1)
m.rect(1, 20, 10, 26, DIRT)
m.rect(0, 19, 11, 19, FENCE, layer=1); m.rect(0, 27, 11, 27, FENCE, layer=1)
m.rect(11, 19, 11, 27, FENCE, layer=1); m.cell(11, 22, None, 1); m.cell(11, 23, None, 1)
for x in (4, 5, 6): m.cell(x, 19, None, 1)            # yard gate below the barracks door
for x, y in ((3, 22), (6, 22), (3, 25), (6, 25)): m.put(x, y, OB(SCARECROW))
m.put(9, 21, OB(BARREL)); m.put(9, 26, OB(CRATE)); m.put(1, 26, OB(CRATE_L_B)); m.put(1, 25, OB(CRATE_L_T), 3)
claim(0, 19, 11, 27)

# ---------------------------------------------------------------- stables and paddock (east)
sb = m.building(30, 38, 14, 2, 3, 'wood', 'boards', windows=False)
m.put(34, sb, OB(ARCH_BOT)); m.put(34, sb - 1, OB(ARCH_TOP))
for x in (31, 37): m.put(x, sb - 1, OB(WIN_SHUT))
for x in (31, 32, 36, 38): m.put(x, sb + 1, OB(HAY))
claim(29, 13, 39, sb + 1)
m.rect(29, 20, 38, 26, DIRT)
m.rect(28, 19, 39, 19, FENCE, layer=1); m.rect(28, 27, 39, 27, FENCE, layer=1)
m.rect(28, 19, 28, 27, FENCE, layer=1); m.cell(28, 22, None, 1); m.cell(28, 23, None, 1)
for x in (33, 34, 35): m.cell(x, 19, None, 1)         # paddock gate below the stable doors
m.put(37, 21, OB(BASIN)); m.put(37, 25, OB(HAY)); m.put(30, 26, OB(BUCKET))
claim(28, 19, 39, 27)

# ---------------------------------------------------------------- the outer wall and gatehouse (south)
m.rect(0, 28, W - 1, 29, KEEP_TOP); m.rect(0, 30, W - 1, H - 1, KEEP_WALL)
m.rect(18, 28, 21, H - 1, COBBLE)
m.relief(18, 28, 21, H - 1)
for x in (17, 22): m.rect(x, 28, x, 29, KEEP_WALL)    # gate passage sides: no stepping onto the wall walk
for x0 in (15, 23):
    stamp(x0, 28, SMALL_TOWER, AC3)
for x in range(12, 28):                               # iron parapet: the wall walk is not reachable from below
    if not 18 <= x <= 21: m.cell(x, 27, IRON_FENCE, 1)
for x in (3, 8, 31, 36): m.put(x, 31, OC(BANNER_RED[0])); m.put(x, 32, OC(BANNER_RED[1]))
claim(0, 27, W - 1, H - 1)

# ---------------------------------------------------------------- trees and lawn dressing
for x, y in ((12, 23), (27, 23), (12, 25), (27, 25)):
    m.put(x, y, OB(TREE_S1), 3); m.put(x, y + 1, OB(TREE_S3))     # slim tree, 1x2
for i in range(40):
    x, y = rnd.randrange(0, W), rnd.randrange(11, 27)
    if (x, y) in taken or m.get(x, y) != GRASS or m.top[0][y][x]: continue
    m.put(x, y, OB(rnd.choice(GRASS_TUFTS + FLOWERS)))

# ---------------------------------------------------------------- events
door_lines = ['The great doors of Valemont Keep.', 'A herald\'s notice: "The Duke receives no visitors until the bells of noon."']
for x in (19, 20): m.add_event('Great Doors', x, 10, [page(None, priority=1, commands=text(*door_lines))])
m.put(5, br, OB(DOOR_HOLE))
m.add_event('Barracks', 5, br, [page(char('!Door1', 0), commands=text('Snoring. Many, many soldiers snoring.'))])
m.add_event('Stables', 34, sb, [page(None, priority=1, commands=text('Warm straw and the smell of horses. The stable boy waves from inside.'))])

m.npc('Royal Guard', 18, 12, 'People3', 7, ('Royal Guard:', 'Halt. State your business with the Duke.', '...Ah, the travellers from the south. Wait here.'))
m.npc('Royal Guard', 21, 12, 'People3', 7, ('Royal Guard:', 'The fountain? Seven generations old. Don\'t throw coins - the gardener fishes them out.'))
m.npc('Gate Guard', 18, 29, 'People3', 6, ('Gate Guard:', 'Welcome to Valemont.'), direction=2)
m.npc('Drill Sergeant', 8, 21, 'People4', 6, ('Drill Sergeant:', 'Again! A straw man has never once dodged, and still you miss!'), direction=2)
m.npc('Recruit', 4, 23, 'People4', 4, ('Recruit:', 'Hah! Hyah! ...Is it lunch yet?'), direction=8)
m.npc('Lady Isolde', 24, 18, 'People2', 7, ('Lady Isolde:', 'Every morning I count the carp in the fountain.', 'There were twelve. Now there are eleven. I suspect the cat.'),
      move=1, freq=2)
m.npc('Gardener', 15, 24, 'People4', 2, ('Gardener:', 'Roses, lilies, and not a single weed. Not one!'), direction=2)
m.npc('Stable Boy', 32, 21, 'People1', 0, ('Stable Boy:', 'Captain\'s horse bit me again. Twice. He likes me really.'), move=1, freq=3)
for x, y in ((31, 22), (35, 24), (33, 25)):
    m.critter('Horse', x, y, 'Horses', rnd.randrange(4), 'Horse', 'The horse flicks an ear at you.', move=1, freq=2, area=(29, 20, 38, 26))
m.critter('Cat', 23, 21, 'Nature', 1, 'Cat', 'The cat is very interested in the fountain.', move=1, freq=2)

if __name__ == '__main__':
    out = next((a for a in sys.argv[1:] if not a.startswith('--')), None)
    if out: m.render(out, scale=0.5, grid='--grid' in sys.argv)
    if '--save' in sys.argv:
        assert MAP_ID, 'set MAP_ID first'
        m.save(MAP_ID)
        print('saved Map%03d' % MAP_ID)
