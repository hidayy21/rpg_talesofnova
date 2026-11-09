# Frosthollow - the walled border town at the end of the north road, last stop before the snow pass to Arulustus
# (Chapter 5: Ley reports to Lord Commander Roland here). Built on three terraces like the snow towns in Referensi
# Map (Imil / Prox: terraces cut by a frozen river with waterfalls and bridges; Narshe: a stair street climbing to
# the top; Elrand: houses on raised ground); the layout is our own.
#   lower terrace  - the south gate from the Nova road, stables, the winter market, the frozen pond under the falls
#   middle terrace - the festival square, Hearthfire Inn, the smithy, the general store, the Frozen Flagon tavern,
#                    and west across the river two houses (one is the fallen captain's family home)
#   upper terrace  - Roland's garrison, the sealed North Gate to the pass, the chapel and its graves, the supply depot
#   python map_frosthollow.py preview.png [--grid]   -> preview image
#   python map_frosthollow.py --save                 -> write the map (editor must be closed; id set below)
import sys, os, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from town_kit import *
import nova_maplib as L
from nova_maplib import page, char, text
import kingdom as K

MAP_ID = K.FROSTHOLLOW
W, H = 56, 52
SNOW, SNOW_COBBLE, SNOW_FENCE = ('A2', 24), ('A2', 11), ('A2', 30)
LEDGE, CLIFF = ('A4', 35), ('A4', 43)              # snow terrace top / its cliff face
WALL_TOP, WALL_FACE = ('A4', 21), ('A4', 29)       # castle wall, snow
ICE_WATER, FALLS = ('A1', 4), ('A1', 5)
SNOW_ROOF, SNOW_ROOF2 = ('A3', 22), ('A3', 23)
STAIRS = (44, 45, 46)                               # snow stairs: left, centre, right (A5)
BRIDGE_TOP, BRIDGE_BOT = 7, 15                      # snow plank bridge, horizontal (A5)
# Outside_B winter props
PINE_BIG = ((128, 129), (136, 137))
PINE = (157, 165)
SNOWMAN_B, FIREWOOD_S, ROCKS_S, LOG_S, BUSH_SN = 160, 162, 163, 164, 166
POT_S, BUCKET_S, CRATE_S, BARREL_S, WELL_S, SIGN_S, CHIMNEY_S = 133, 134, 135, 149, 147, 145, 144
GRASS_S = (152, 153, 154, 155)
STUMP_S, BOULDER_S, BOULDER_S2, HAY_S, GRAVE_A, GRAVE_B = 156, 159, 167, 185, 150, 151
SNOW_TENT = ((232, 233, 234), (240, 241, 242), (248, 249, 250))
SNOW_LAMP = (235, 243, 251)
BARRICADE_S = 141
X = lambda n: L.ext('PM_XmasDecoration', n)
XMAS_TREE = ((X(90), X(91)), (X(98), X(99)), (X(106), X(107)))
STAR_LAMP = (X(216), X(224))
SNOWMAN, PRESENTS, PRESENT_PILE, WREATH = X(236), (X(116), X(117), X(124), X(125)), X(118), X(59)
GARLAND = tuple(X(n) for n in range(65, 70))         # 5 tiles: left end, 3 middle, right end
TOWER = (C_ + 176, C_ + 177), (C_ + 184, C_ + 185), (C_ + 192, C_ + 193), (C_ + 200, C_ + 201), (C_ + 208, C_ + 209)

m = Town(W, H, *K.NAMES[K.FROSTHOLLOW], ground=SNOW)
m.bgm = {'name': '03_Childhood_Memories', 'pan': 0, 'pitch': 100, 'volume': 70}
m.bgs = {'name': 'Wind', 'pan': 0, 'pitch': 100, 'volume': 30}
m.note += '\n<bloom: 0.3>\n<particles: snow>'
rnd = random.Random(7)
taken = set()

def claim(x0, y0, x1, y1):
    taken.update((x, y) for x in range(x0, x1 + 1) for y in range(y0, y1 + 1))

# ================================================================ the terraces
# face rows of the upper cliff (b2) and the lower cliff (b1), per column band
B2 = [(0, 9, 16), (10, 23, 15), (24, 47, 17), (48, 55, 14)]
B1 = [(0, 9, 31), (10, 23, 33), (24, 47, 35), (48, 55, 33)]
FACE = 3                                            # cliff height in tiles

def band(bands, x):
    return next(b for x0, x1, b in bands if x0 <= x <= x1)

def level(x, y):
    """2 / 1 / 0 = terrace, 'F2' / 'F1' = cliff face below terrace 2 / 1."""
    b2, b1 = band(B2, x), band(B1, x)
    if y < b2: return 2
    if y < b2 + FACE: return 'F2'
    if y < b1: return 1
    if y < b1 + FACE: return 'F1'
    return 0

LV = [[level(x, y) for x in range(W)] for y in range(H)]
for y in range(H):
    for x in range(W):
        v = LV[y][x]
        m.cell(x, y, SNOW if v == 0 else (CLIFF if v in ('F1', 'F2') else LEDGE))

road = set()
def pave(x0, y0, x1, y1):
    """Cobbled street; on the terraces it lies over the ledge top (layer 1), below them it is the ground."""
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            if LV[y][x] == 0: m.cell(x, y, SNOW_COBBLE)
            else: m.cell(x, y, SNOW_COBBLE, 1)
            road.add((x, y))

stairs = set()
def stair(x0, x1, face):
    """Stairs cut through a cliff face: every face row of columns x0..x1 (face = 'F1' or 'F2')."""
    for x in range(x0, x1 + 1):
        for y in range(H):
            if LV[y][x] == face:
                m.cell(x, y, A5(STAIRS[0] if x == x0 else STAIRS[2] if x == x1 else STAIRS[1]))
                stairs.add((x, y))

# ================================================================ the frozen river and its two falls
RX = (11, 12)
for x in RX:
    for y in range(0, 36):
        v = LV[y][x]
        m.cell(x, y, FALLS if v in ('F1', 'F2') else ICE_WATER)
m.rect(6, 36, 16, 41, ICE_WATER); m.rect(8, 42, 14, 42, ICE_WATER); m.rect(7, 35, 15, 35, ICE_WATER)
claim(5, 34, 17, 43); claim(10, 0, 13, 35)

def bridge(y, x0, x1):
    m.rect(x0, y, x1, y, A5(BRIDGE_TOP)); m.rect(x0, y + 1, x1, y + 1, A5(BRIDGE_BOT))
    road.update((x, yy) for x in range(x0, x1 + 1) for yy in (y, y + 1))
bridge(9, 10, 13)                                   # upper: chapel <-> depot
bridge(24, 10, 13)                                  # middle: west houses <-> inn

# ================================================================ streets, stairs
pave(26, 38, 29, H - 1)                             # the high street, from the south gate
stair(26, 29, 'F1')                                 # ...up to the square
pave(26, 20, 37, 34)                                # the festival square
pave(33, 5, 36, 19); stair(33, 36, 'F2')            # ...up to the garrison and the North Gate
pave(14, 23, 25, 26)                                # west lane: inn, bridge
pave(2, 23, 9, 25); pave(9, 26, 9, 30); pave(3, 30, 9, 30)   # west houses
pave(38, 26, 47, 27); pave(48, 22, 52, 27)          # east lane: smithy, store, tavern
pave(38, 33, 44, 34); pave(50, 28, 51, 32)          # tavern door, down to the east stairs
stair(50, 51, 'F1'); pave(49, 36, 52, 37)           # east stairs down to the lower houses
pave(48, 38, 49, 44); pave(48, 43, 54, 44)
stair(19, 20, 'F1'); pave(17, 36, 22, 38)           # west stairs down to the market and the pond
pave(18, 36, 25, 37)
pave(4, 15, 5, 18); stair(4, 5, 'F2'); pave(2, 14, 9, 15)   # chapel stairs
pave(9, 9, 9, 12); pave(4, 12, 8, 12); pave(4, 13, 4, 13)   # chapel door to the upper bridge
pave(14, 10, 32, 11); pave(37, 12, 46, 13)          # upper lanes: depot, garrison door
pave(18, 9, 18, 9)
pave(14, 31, 25, 32)                                # guild hall front, to the square
stair(51, 52, 'F2'); pave(50, 11, 53, 13)           # east stairs to the watch post
pave(30, 40, 41, 41)                                # lower lane: stables, to the paddock gate
taken |= road | stairs

# ================================================================ walls: North (sealed gate) and South (town gate)
m.rect(16, 0, W - 1, 1, WALL_TOP); m.rect(16, 2, W - 1, 4, WALL_FACE)
for x in range(33, 37): m.cell(x, 4, WALL_FACE)
for x0 in (16, 30, 38):                              # gate towers, and one capping the wall's west end
    for i, (a, b) in enumerate(TOWER):
        m.put(x0, i, a, 3 if i < 4 else 2); m.put(x0 + 1, i, b, 3 if i < 4 else 2)
for x in (21, 26, 44, 50): m.tall(x, 2, BANNER_BLUE)
claim(16, 0, W - 1, 4)

m.rect(0, 46, W - 1, 47, WALL_TOP); m.rect(0, 48, W - 1, H - 1, WALL_FACE)
m.rect(26, 46, 29, H - 1, SNOW_COBBLE)
for x0 in (24, 30):
    for i, (a, b) in enumerate(TOWER):
        m.put(x0, 46 + i, a, 3 if i < 4 else 2); m.put(x0 + 1, 46 + i, b, 3 if i < 4 else 2)
    m.rect(x0, 46, x0 + 1, 47, WALL_FACE)               # under the towers: no stepping onto the wall walk
for x in (6, 16, 38, 48): m.tall(x, 49, BANNER_BLUE)
for x in range(W):                                   # snowy fence: the wall walk is not reachable from the town
    if not 24 <= x <= 31 and LV[45][x] == 0 and (x, 45) not in taken: m.cell(x, 45, SNOW_FENCE, 1)
for x in (25, 30):
    m.put(x, 43, SNOW_LAMP[0], 3); m.put(x, 44, SNOW_LAMP[1], 3); m.put(x, 45, SNOW_LAMP[2])
claim(0, 45, W - 1, H - 1)

# ================================================================ buildings
def house(x0, x1, top, roof_rows, wall_rows, wall, roof=SNOW_ROOF, wins=(), shut=(), chimney=None):
    b = m.building(x0, x1, top, roof_rows, wall_rows, 'stone', wall, windows=False)
    m.rect(x0, top, x1, top + roof_rows - 1, roof)
    for x in wins: m.put(x, b - 1, WIN)
    for x in shut: m.put(x, b - 1, WIN_SHUT)
    if chimney: m.put(chimney, top, CHIMNEY_S)
    claim(x0 - 1, top, x1 + 1, b + 1)              # the row in front stays clear (doorsteps)
    return b

# --- upper terrace
hq = house(39, 52, 5, 3, 4, 'stone', wins=(40, 44, 48, 51), chimney=41)     # Roland's garrison
for x in (40, 44, 48, 51): m.put(x, hq - 2, WIN)
m.tall(43, hq - 1, BANNER_BLUE); m.tall(49, hq - 1, BANNER_BLUE)
m.put(45, hq, SIGN['crest'])
for x in (38, 53): m.put(x, hq, BARREL_S)
for x, y in ((40, 14), (42, 14), (44, 14)): m.put(x, y, SCARECROW)          # practice dummies in the yard
m.put(46, 14, CRATE_S); m.put(47, 14, CRATE_S); m.put(38, 15, FIREWOOD_S)

ch = house(1, 8, 6, 3, 3, 'stone', roof=SNOW_ROOF2, wins=(2, 7))            # the chapel
m.put(4, ch - 2, STAINED); m.put(5, ch - 2, STAINED); m.put(3, ch - 1, WIN); m.put(6, ch - 1, WIN)
for x in (1, 3, 7, 8): m.put(x, 13, GRAVE_A if x % 2 else GRAVE_B)
m.put(9, 13, SNOW_LAMP[2]); m.put(9, 12, SNOW_LAMP[1], 3); m.put(9, 11, SNOW_LAMP[0], 3)

dp = house(15, 22, 5, 2, 2, 'boards', roof=SNOW_ROOF2, shut=(16, 21))        # the supply depot
m.put(18, dp, ARCH_BOT); m.put(18, dp - 1, ARCH_TOP)
for x, t in ((15, CRATE_S), (16, CRATE_S), (21, BARREL_S), (22, HAY_S)): m.put(x, dp + 1, t)

# the watch post on the east bluff
m.put(53, 9, SNOW_LAMP[0], 3); m.put(53, 10, SNOW_LAMP[1], 3); m.put(53, 11, SNOW_LAMP[2])
m.put(54, 13, BARRICADE_S); m.put(55, 13, BARRICADE_S)

# --- middle terrace
inn = house(15, 23, 18, 2, 3, 'log', wins=(16, 18, 22), chimney=17)
m.put(16, inn - 2, WIN); m.put(22, inn - 2, WIN); m.put(22, inn, SIGN['inn'])
for x, g in zip(range(17, 22), GARLAND): m.put(x, inn - 2, g)

sm = house(39, 46, 21, 2, 3, 'stone', wins=(40, 45), chimney=45)            # the smithy
m.put(40, sm - 2, WIN); m.put(44, sm, SIGN['hammer']); m.put(46, sm + 1, FIRE_PIT); m.put(38, sm, BARREL_S)
gs = house(48, 54, 17, 2, 3, 'wood', roof=SNOW_ROOF2, wins=(49, 53))        # the general store
m.put(52, gs, SIGN['item']); m.put(53, gs + 1, CRATE_APPLE); m.put(54, gs + 1, CRATE_S)
tv = house(39, 47, 28, 2, 3, 'tudor', wins=(40, 46), chimney=41)            # the Frozen Flagon
m.put(45, tv, SIGN['pub']); m.put(40, tv - 2, WIN); m.put(46, tv - 2, WIN)

cap = house(1, 7, 19, 2, 2, 'log', wins=(2, 6), chimney=6)                  # the fallen captain's family
c2 = house(1, 8, 26, 2, 2, 'wood', roof=SNOW_ROOF2, wins=(2, 7))
m.put(8, cap, FIREWOOD_S); m.put(2, c2 + 1, BARREL_S)

# --- lower terrace
st = house(33, 41, 36, 2, 2, 'boards', roof=SNOW_ROOF2, shut=(34, 40))      # stables
m.put(37, st, ARCH_BOT); m.put(37, st - 1, ARCH_TOP)
m.rect(42, 39, 47, 44, SNOW_FENCE, 1); m.rect(43, 40, 46, 43, None, 1); m.cell(42, 41, None, 1)
m.put(46, 43, HAY_S); m.put(43, 43, BUCKET_S)
lh = house(50, 55, 39, 2, 2, 'log', wins=(51, 54), chimney=54)              # lower house
claim(42, 39, 47, 44)

def tent(x, y):
    for r in range(3):
        for c in range(3): m.put(x + c, y + r, SNOW_TENT[r][c], 3 if r == 0 else 2)
    claim(x, y, x + 2, y + 2)
tent(18, 39); tent(21, 39)
pave(17, 42, 25, 43)
for x, t in ((17, CRATE_S), (24, BARREL_S), (25, POT_S)): m.put(x, 41, t)
m.put(20, 41, CRATE_APPLE)

# --- the soldiers' camp on the upper terrace, below the depot
tent(23, 12); tent(28, 12)
m.put(27, 15, FIRE_PIT); m.put(26, 15, LOG_S); m.put(27, 16, LOG_S)
m.put(32, 13, BARREL_S); m.put(22, 14, CRATE_S)
claim(22, 12, 32, 16)

# --- the Adventurers' Guild branch, below the inn
gh = house(15, 22, 27, 2, 2, 'tudor', roof=SNOW_ROOF2, wins=(16, 21))
m.put(20, gh, SIGN['sword']); m.put(23, gh, NOTICE_BOARD)

# --- the woodcutter's cabin, lower west by the pond
wc = house(0, 4, 37, 2, 2, 'log', wins=(1,), chimney=3)
pave(2, 41, 5, 42); pave(5, 43, 17, 44)
for x, y, t in ((0, 41, FIREWOOD_S), (0, 42, FIREWOOD_S), (5, 40, STUMP_S), (1, 44, LOG_S)):
    m.put(x, y, t)
claim(0, 36, 5, 44)

# ================================================================ the festival square
tx, ty = 31, 25
for r, (a, b) in enumerate(XMAS_TREE):
    m.put(tx, ty + r, a, 3 if r < 2 else 2); m.put(tx + 1, ty + r, b, 3 if r < 2 else 2)
m.put(30, 27, PRESENTS[0]); m.put(33, 27, PRESENT_PILE); m.put(30, 26, PRESENTS[2])
for x, y in ((27, 22), (36, 22), (27, 31), (36, 31)):
    m.put(x, y - 1, STAR_LAMP[0], 3); m.put(x, y, STAR_LAMP[1])
m.put(28, 29, SNOWMAN); m.put(35, 24, WELL_S); m.put(26, 24, NOTICE_BOARD)
m.put(37, 33, BARREL_S); m.put(26, 33, CRATE_S)
claim(26, 20, 37, 34)

# ================================================================ terrace edges: no walking off a terrace sideways
# where a higher terrace meets lower ground in the same row, a rock or a snowy bush stands on the lower side
def is_ground(v): return v in (0, 1, 2)
for y in range(H):
    for x in range(W):
        v = LV[y][x]
        if not is_ground(v) or (x, y) in stairs or m.top[0][y][x]: continue
        for nx in (x - 1, x + 1):
            if 0 <= nx < W and is_ground(LV[y][nx]) and LV[y][nx] > v and (nx, y) not in stairs:
                if m.get(x, y) in (ICE_WATER, FALLS) or m.get(nx, y) in (ICE_WATER, FALLS): continue
                m.put(x, y, (BOULDER_S, BUSH_SN, BOULDER_S2)[(x + y) % 3]); taken.add((x, y))
                break

# ================================================================ pines and dressing
def free_ground(cells):
    """A tree only stands on open terrace ground: no cliff face, stairs, road or other object under it."""
    return all(0 <= x < W and 0 <= y < H and LV[y][x] in (0, 1, 2) and (x, y) not in stairs and (x, y) not in road
               and not m.top[0][y][x] and not m.top[1][y][x] and m.get(x, y) in (SNOW, LEDGE) for x, y in cells)

def big(x, y):
    if not free_ground([(x, y), (x + 1, y), (x, y + 1), (x + 1, y + 1)]): return
    (a, b), (c, d) = PINE_BIG
    m.put(x, y, a, 3); m.put(x + 1, y, b, 3); m.put(x, y + 1, c); m.put(x + 1, y + 1, d)
    claim(x, y, x + 1, y + 1)
def pine(x, y):
    if not free_ground([(x, y), (x, y + 1)]): return
    m.put(x, y, PINE[0], 3); m.put(x, y + 1, PINE[1]); claim(x, y, x, y + 1)

for x in (0, 2, 4, 6, 8, 14): big(x, 0)             # forest north-west, beside the river's source
for x in (1, 3, 5, 7): big(x, 2)
big(14, 2); pine(9, 3)
for x, y in ((24, 6), (28, 6), (53, 6)): big(x, y)
for x, y in ((0, 17), (8, 17), (14, 16), (23, 21), (46, 18), (44, 33), (54, 30), (0, 34), (2, 40), (22, 44),
             (52, 42), (32, 43), (4, 44)):
    if not any((x + dx, y + dy) in taken for dx in (0, 1) for dy in (0, 1)): big(x, y)
for x, y in ((13, 19), (38, 36), (47, 37), (9, 27), (55, 21), (0, 24), (1, 42)):
    if (x, y) not in taken and (x, y + 1) not in taken: pine(x, y)

for i in range(110):
    x, y = rnd.randrange(0, W), rnd.randrange(5, 45)
    if (x, y) in taken or m.top[0][y][x] or m.get(x, y) not in (SNOW, LEDGE) or m.get(x, y, 1): continue
    m.put(x, y, rnd.choice(GRASS_S + GRASS_S + (STUMP_S, ROCKS_S, ROCKS_S, LOG_S)))
    taken.add((x, y))

# ================================================================ events
for x in range(26, 30):                              # out through the south gate: every lane lands on the road's end
    m.add_event('To World Map %d' % (x - 25), x, H - 1, [L.exit_page(*K.ARRIVE['world_from_frosthollow'])])

gate_lines = ['The North Gate is barred with iron and frozen shut.',
              'Beyond it the pass climbs into the snow toward Arulustus.']
m.add_event('North Gate', 34, 4, [page(char('!$Gate1', 0), commands=text(*gate_lines), priority=1, walk_anim=False)])
m.add_event('North Gate', 35, 4, [page(None, commands=text(*gate_lines), priority=1)])

m.locked_door('Garrison', 46, hq, ['A soldier at the door: "Lord Commander Talonheart is in council. Wait your turn."'])
m.locked_door('Chapel of the Pass', 4, ch, ['Candles burn for those who did not come back from the border.'], style=2)
m.locked_door('Supply Depot', 18, dp, ['Sacks of grain and barrels of lamp oil, stacked to the rafters.'], style=1)
m.locked_door('Hearthfire Inn', 19, inn, ['Warm laughter and the smell of spiced cider leak out under the door.'])
m.locked_door('Smithy', 42, sm, ['The ring of a hammer stops. "Closed for the festival!"'])
m.locked_door('General Store', 51, gs, ['"Back after the parade!" says a note pinned to the door.'])
m.locked_door('Frozen Flagon', 43, tv, ['Someone inside is singing very badly about a goat.'])
m.locked_door('Quiet House', 4, cap, ['An old soldier\'s helmet hangs by the door. Nobody answers.'])
m.locked_door('Cottage', 4, c2, ['Children\'s mittens are drying on the windowsill.'])
m.locked_door('Stables', 37, st, ['Warm straw, and horses stamping in the dark.'], style=1)
m.locked_door('Guild Branch', 18, gh, ['A clerk calls out: "Guild business after the festival bell!"'])
m.sign('Guild Board', 23, gh, ['FROSTHOLLOW BRANCH - open requests:', '"Wolves on the south road." "Missing goat." "Escort wanted: north pass (CANCELLED)."'])
m.locked_door("Woodcutter's Cabin", 2, wc, ['An axe is buried in the chopping block by the door. Nobody home.'])
m.locked_door('Lower House', 52, lh, ['A dog barks once behind the door, then thinks better of it.'])
m.sign('Notice Board', 26, 24, ['"By order of the garrison: no one passes the North Gate."',
                                '"Lost: one goat. Answers to nothing. Last seen at the Frozen Flagon."'])
m.sign('Graves', 3, 13, ['Simple stones, each with a name and a date. Too many share the same year.'])

m.npc('Gate Guard', 27, 44, 'People3', 7, ('Gate Guard:', 'Welcome to Frosthollow - last town before the pass.',
      'Mind the ice on the stairs. And the soldiers. Mostly the ice.'))
m.npc('Guard', 32, 6, 'People3', 6, ('Guard:', 'No one goes north. Loyalist raiders have been seen on the pass.'), direction=2)
m.npc('Guard', 37, 6, 'People3', 7, ('Guard:', 'Orders from the Lord Commander himself. The gate stays shut.'), direction=2)
m.npc('Recruit', 41, 15, 'People4', 4, ('Recruit:', 'Hyah! ...These dummies never fall over.', 'The sergeant says that\'s the point.'),
      direction=8)
m.npc('Priest', 6, 14, 'People1', 6, ('Priest:', 'Every name on these stones kept the pass for us.',
      'Light a candle if you have someone out there.'), direction=4)
m.npc('Quartermaster', 20, 12, 'People4', 6, ('Quartermaster:', 'Grain for the winter, oil for the lamps, arrows for the walls.',
      'And every crate counted twice. The Commander counts the third time.'))
m.npc('Old Ingrid', 34, 29, 'People1', 7, ('Old Ingrid:', 'Sixty winters I\'ve hung an ornament on that tree.',
      'This year mine is a little silver bell - for the boys at the border.'), move=1, freq=2)
m.npc('Boy', 29, 30, 'People1', 0, ('Boy:', 'I built the snowman! His name is Sir Frost.', 'He guards the square. Like the soldiers, but colder.'),
      move=1, freq=4)
m.npc('Smith Hilda', 43, 26, 'People2', 0, ('Hilda:', 'Even a smith needs a holiday.', 'Tomorrow I\'ll fix your blade. Today, I fix cider.'))
m.npc('Tavern Regular', 41, 33, 'People4', 2, ('Regular:', 'The goat? Oh, the goat is fine.', 'The goat is better than fine. The goat is in charge now.'),
      direction=8)
m.npc('Skater Girl', 18, 44, 'People1', 3, ('Girl:', 'The pond froze solid last night!', 'Mother says I can skate when the ice sings.'),
      move=1, freq=3)
m.npc('Fur Merchant', 20, 42, 'People1', 4, ('Fur Merchant:', 'Furs, mittens, boots! Nothing keeps you warmer!', '...except maybe the cider.'),
      direction=8)
m.npc('Little Girl', 6, 24, 'People2', 1, ('Little Girl:', 'Papa was a captain. He\'s coming home after the snow.',
      'Mama says so. Mama says it every night.'), move=1, freq=2)
m.npc('Stable Hand', 39, 40, 'People4', 0, ('Stable Hand:', 'The garrison horses eat better than I do.', 'Fair, mind. They work harder.'),
      move=1, freq=3)
for hx, hy in ((44, 41), (45, 42)):
    m.critter('Horse', hx, hy, 'Horses', rnd.randrange(4), 'Horse', 'The horse snorts a cloud of steam at you.', move=1, freq=2,
              area=(43, 40, 46, 43))
m.critter('Husky', 31, 33, 'Nature', 0, 'Dog', 'The husky shakes snow all over you.', move=1)

if __name__ == '__main__':
    out = next((a for a in sys.argv[1:] if not a.startswith('--')), None)
    if out: m.render(out, scale=0.5, grid='--grid' in sys.argv)
    if '--save' in sys.argv:
        m.save(MAP_ID, parent_id=K.WORLD, order=MAP_ID)
        print('saved Map%03d' % MAP_ID)
