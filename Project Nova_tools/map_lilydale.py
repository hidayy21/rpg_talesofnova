# MAP065 - Lilydale (chapter 7): the village in the woods, the last place before Hollow Wood and the misty wood that
# hides Villa Bloodrose. The party arrives here first. The village knew the Bloodroses well once: David came to play
# here as a boy (the elders were those children), and his wife was one of the village's own. Since she died in the war
# sixteen years ago only the villa's servants come, on market days, for flour and lamp oil - and for three weeks not
# even they have come.
# Built from the user's four reference pictures - a village on terraces held up by stone walls, iron railings along
# the top and stairs flanked by pillars with plants; half-timbered houses with steep gables, stone ground floors,
# flower boxes and hanging signs; a big tree in a raised bed on the square; iron street lamps; a smithy with its forge -
# and the village maps in Referensi Map (Trials of Mana Wendel: a village on terraces with the temple at the top; FF4
# Mist: a clearing walled in by forest; Golden Sun Vale: houses on several levels of a slope). The layout is our own:
#   upper terrace - the north road from Hollow Wood, the church with its spire and the memorial garden, Old Henrik's
#                   house and the shepherd's cottage; the grand stair down to the square
#   the village   - Rose Square: the old rose-coloured tree in its raised bed (a cutting of the Bloodrose tree - "the
#                   boy who always waited under the rose tree"), the roofed well, the market stalls - one empty: it was
#                   the villa's flour stall. Round it the Lantern & Lily, the tailor, Thistle & Wick, the smithy and
#                   its forge yard, the bakery (no flour), Old Marta's house, the weaver; vegetable plots, the orchard
#                   and the hens down by the south road
#   lower garden  - the lily pond the village is named for, its jetty and swans, Old Bram's cottage
#   doors that open (map_lilydale_interiors.py): the Lantern & Lily (tavern below, inn rooms upstairs), the church,
#   Thistle & Wick (items only), and the three elders' houses. Every other door is latched, each with its own line.
#   road north (top) into Hollow Wood; road south (bottom) out of the valley (no World Map link yet)
# Tileset 21 "Medieval Town" (make_medieval_tileset.py) plus pieces of Avy_Town_B/B3, PM_Market, PM_Forest, PM_Nature1,
# PM_Village2, Nova_Nature, Nova_Farm and Outside_C; the smithy's forge is the !$PM_Blacksmith sheet. The woods round
# the edge come from rm-map-forge (forge_outdoor.js, trees only).
#   python3 map_lilydale.py preview.png [--grid] [--full]   -> preview image
#   python3 map_lilydale.py --save                          -> write Map065 (editor must be closed)
import sys, os, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import nova_maplib as L
from nova_maplib import page, cmd, text, char
from town_kit import *
import kingdom as K
from forge_outdoor import forge, Tree, BLOCKER
from forge_outdoor import A2 as FA2
from make_medieval_tileset import MED_GROUND, MED_ROOF, MED_WALL

W, H = 52, 50
TILESET = 21
X = L.ext
MV = lambda n: 768 + n                                           # MedievalVillage_B, slot E of tileset 21
OC = lambda n: 256 + n                                           # Outside_C, slot C
AV = lambda n: X('Avy_Town_B', n)
AV3 = lambda n: X('Avy_Town_B3', n)
AV4 = lambda n: X('Avy_Town_B4', n)
PF = lambda n: X('PM_Forest', n)
PM = lambda n: X('PM_Market', n)
PN = lambda n: X('PM_Nature1', n)
PV2 = lambda n: X('PM_Village2', n)
NN = lambda n: X('Nova_Nature', n)

# ---------------------------------------------------------------- ground, walls, railings
LANE = ('A2', 10)                                                # grey cobbles: lanes, the roads, the forecourts
PLAZA = ('A2', 19)                                               # warm cobbles in a pale frame: Rose Square
SOFT_GRASS = ('A2', MED_GROUND['grass'])                         # gardens, beds
FOOTPATH = ('A2', 1)                                             # trodden earth: paths across the yards
TILLED = ('A2', 8)                                               # the vegetable plots
RETAIN = ('A4', 8)                                               # grey stone retaining wall (face)
BED_WALL = ('A4', 12)                                            # rubble stone: the raised bed of the rose tree
RAILING = ('A2', 14)                                             # black iron railing (layer 1)
PICKET = ('A2', 6)                                               # wooden fence (layer 1)
STAIR = (56, 57, 58)                                             # Outside_A5 stone steps: left, middle, right
JETTY = (5, 13)                                                  # Outside_A5 planks, horizontal: top row, bottom row
POND_WATER, LILY_PADS = ('A1', 0), ('A1', 2)                     # water with a grass bank / floating lily pads (layer 1)

# ---------------------------------------------------------------- objects, by sheet
PILLAR = (OC(0), OC(8))                                          # Outside_C: a short stone pillar, top and base
POTS = (AV(59), AV(58), AV(63), AV(71))                          # Avy_Town_B: plants and flowers in white pots
ANGEL = (OC(81), OC(89))                                         # Outside_C: an angel on a plinth
BENCH = (AV3(228), AV3(229))                                     # Avy_Town_B3: a wooden bench, front view, 2x1
WELL_ROOFED = ((AV3(5), AV3(6)), (AV3(13), AV3(14)))             # Avy_Town_B3: well with its winch frame, 2x2
SPIRE = [(128, 129, 130), (136, 137, 138), (144, 145, 146), (152, 153, 154), (160, 161, 162),
         (168, 169, 170), (176, 177, 178)]                       # Avy_Town_B3, 3x7
BELFRY = (AV3(66), AV3(74))                                      # Avy_Town_B3: a pointed opening, two tiles tall
ROSE_WINDOW = (AV3(84), AV3(92))                                 # Avy_Town_B3: round-headed tracery window
LATTICE = (AV3(71), AV3(79))                                     # Avy_Town_B3: pointed leaded window
STAINED_GLASS = [(AV3(192), AV3(200)), (AV3(193), AV3(201)), (AV3(194), AV3(202)), (AV3(195), AV3(203))]
SMOKE = (AV3(24), AV3(32))                                       # Avy_Town_B3: a wisp of chimney smoke
ROSE_BUSH = ((AV3(113), AV3(114)), (AV3(121), AV3(122)))         # Avy_Town_B3: a rose bush, 2x2
HANGING_SIGN = (PM(167), PM(175))                                # PM_Market: a board / a bowl hung from a bracket
ROSE_TREE = [(200, 201, 202, 203, 204), (208, 209, 210, 211, 212), (216, 217, 218, 219, 220),
             (224, 225, 226, 227, 228), (232, 233, 234, 235, 236), (240, 241, 242, 243, 244),
             (248, 249, 250, 251, 252)]                          # PM_Forest, 5x7 (the villa garden has its parent)
ROUND_TREE = [tuple(PF(n) for n in r) for r in ((16, 17, 18), (24, 25, 26), (32, 33, 34))]   # PM_Forest
SMALL_ROUND = [tuple(PF(n) for n in r) for r in ((40, 41, 42), (48, 49, 50))]               # PM_Forest
FRUIT_TREE = [tuple(PN(n) for n in r) for r in ((128, 129), (136, 137), (144, 145))]         # PM_Nature1, 2x3
FRUIT_TREE2 = [tuple(PN(n) for n in r) for r in ((130, 131), (138, 139), (146, 147))]
LILIES = (PF(9), PF(10))                                         # white lilies standing in water
FLOWER_BED = ((NN(24), NN(25)), (NN(32), NN(33)))                # Nova_Nature: pink and white flowers, 2x2
CONIFER = (NN(30), NN(38))                                       # Nova_Nature: a small fir with flowers at its foot
STALL = {'red': ((42, 43, 44), (50, 51, 52), (58, 59, 60), (66, 67, 68)),       # PM_Market: awning, shade, counter
         'green': ((45, 46, 47), (53, 54, 55), (61, 62, 63), (69, 70, 71))}
FLOWER_CART = ((56, 57), (64, 65))
PRODUCE = (16, 17, 24, 25, 32, 33, 124, 125)                     # PM_Market: crates and baskets of fruit and greens
HAYSTACK = (PV2(227), PV2(228))
WOODPILE = ((PN(222), PN(223)), (PN(230), PN(231)))              # PM_Nature1: split logs stacked, 2x2

# MedievalVillage_B pieces
GABLE = {'shingle': [(None, None, 130, None, None), (None, 137, 138, 139, None), (144, 145, 146, 147, 148),
                     (152, 153, 154, 155, 156), (160, 161, 162, 163, 164)],
         'slate': [(None, None, 170, None, None), (None, 177, 178, 179, None), (184, 185, 186, 187, 188),
                   (192, 193, 194, 195, 196), (200, 201, 202, 203, 204)]}
DORMER = {'shingle': 133, 'slate': 141}
M_CHIMNEY = {'brick': (149, 157), 'stone': (181, 189)}
M_WIN = {'small': (9, 17), 'wide': (10, 18), 'tall': (11, 19), 'flowers': (12, 20), 'arched': (13, 21)}
M_DOOR = {'wood': (14, 22), 'arched': (15, 23)}
M_BARREL, M_CRATE, M_BARREL2 = 1, 2, 39
STONE_WALLS = {'rubble', 'stone', 'ashlar', 'brick', 'brickstone', 'timber_brick', 'rockwall', 'sandstone', 'log'}

NORTH_X, SOUTH_X = (25, 26), (25, 26)                            # the road lanes at the top and bottom edges


# ================================================================ levels
# upper terrace (2) / its retaining wall (F2) / the village (1) / the lily-pond garden's wall (F1) / the garden (0)
def e2(x):
    """Last row of the upper terrace in column x (the railing row); the wall below it is two rows high."""
    return 16 if x <= 21 else 17 if x <= 29 else 19


LOW_X = (3, 20)                                                  # columns of the lily-pond garden
E1 = 30                                                          # its railing row; wall 31-32, garden from 33


def level(x, y):
    if y <= e2(x): return 2
    if y <= e2(x) + 2: return 'F2'
    if LOW_X[0] <= x <= LOW_X[1] and y > E1:
        return 'F1' if y <= E1 + 2 else 0
    return 1


def in_village(x, y):
    """Inside the clearing; outside is the wood. Ragged corners, the two roads out, room for the spire."""
    if x in NORTH_X and y <= 3 or x in SOUTH_X and y >= H - 4: return True
    if 34 <= x <= 40 and y == 2: return True
    if not (3 <= x <= 48 and 3 <= y <= 46): return False
    cx, cy = min(x - 3, 48 - x), min(y - 3, 46 - y)
    return cx + cy >= 2 or ((x * 7 + y * 3) % 5 == 0 and cx + cy >= 1)


GREEN = [Tree([(16, 17, 18), (24, 25, 26), (32, 33, 34)], 0.30, None, 'PM_Forest'),
         Tree([(40, 41, 42), (48, 49, 50), (56, 57, 58)], 0.25, None, 'PM_Forest'),
         Tree([(112, 113), (120, 121)], 0.25, None, 'PM_Forest'),
         Tree([(114, 115), (122, 123)], 0.22, None, 'PM_Forest'),
         Tree(BIG_TREE, 0.15),
         Tree([(BUSH_S,)], 0.05)]
KEEP = [(x, y) for y in range(H) for x in range(W) if in_village(x, y)]
KEEP_SET = set(KEEP)
m = forge(K.NAMES[K.LILYDALE], W, H, seed='lilydale-4', ground=FA2(0), road=FA2(1), paths=[], keep=KEEP, trees=GREEN,
          params={'hills': 0, 'scale': 16}, tileset=TILESET)
m.note = '<outdoor>'
m.bgm = {'name': 'Town2', 'pan': 0, 'pitch': 95, 'volume': 70}
m.bgs = {'name': 'Wind', 'pan': 0, 'pitch': 100, 'volume': 15}
rnd = random.Random(65)
taken = set()


def claim(x0, y0, x1, y1): taken.update((x, y) for x in range(x0, x1 + 1) for y in range(y0, y1 + 1))


def free(x, y):
    return (x, y) not in taken and (x, y) in KEEP_SET and level(x, y) in (0, 1, 2) and not m.has_object(x, y)


m.rect(0, 0, W - 1, H - 1, GRASS)                                # the wood's floor and the village's grass
for (x, y) in KEEP:
    if level(x, y) in ('F1', 'F2'): m.cell(x, y, RETAIN); claim(x, y, x, y)
# gaps in the wood that no whole tree fitted into stay closed
for y in range(H):
    for x in range(W):
        if (x, y) not in KEEP_SET and not m.has_object(x, y):
            m.put(x, y, BLOCKER)
            if rnd.random() < 0.5: m.put(x, y, rnd.choice((BUSH_S, FERN, TREE_S1)), 3)


# ================================================================ streets, stairs, railings
def pave(x0, y0, x1, y1, val=LANE):
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            if (x, y) in KEEP_SET and level(x, y) in (0, 1, 2): m.cell(x, y, val)


STAIR_CELLS = set()


def stair(x0, x1, face):
    """Stone steps through every wall row of columns x0..x1 (face 'F1' or 'F2')."""
    for x in range(x0, x1 + 1):
        for y in range(H):
            if level(x, y) == face:
                m.cell(x, y, ('A5', STAIR[0] if x == x0 else STAIR[2] if x == x1 else STAIR[1]))
                STAIR_CELLS.add((x, y))


m.rect(NORTH_X[0], 0, NORTH_X[1], 3, DIRT)                       # the road from Hollow Wood...
pave(24, 4, 27, 13)                                              # ...cobbled once it is in the village
pave(21, 14, 30, 17)                                             # the landing at the head of the grand stair
pave(4, 14, 20, 15)                                              # upper lane: Henrik's, the shepherd's
pave(31, 17, 47, 18)                                             # the church forecourt
stair(24, 27, 'F2')                                              # the grand stair down to Rose Square
pave(21, 19, 35, 34, PLAZA)                                      # Rose Square
pave(3, 28, 22, 29)                                              # lane in front of the Lantern & Lily
pave(36, 22, 36, 40)                                             # alley: the square, the shop lane, the south lane
pave(37, 29, 48, 30)                                             # lane in front of the shop and the smithy
pave(24, 35, 27, 44)                                             # the south road...
m.rect(SOUTH_X[0], 45, SOUTH_X[1], H - 1, DIRT)                  # ...out of the valley
pave(28, 39, 47, 40)                                             # south lane: the bakery, Marta's, the weaver's
pave(22, 30, 23, 44)                                             # walk beside the south road
stair(11, 12, 'F1')                                              # down to the lily pond
for (x, y) in KEEP:                                              # the gardens' softer grass
    if level(x, y) == 0 or 44 <= x <= 48 and 7 <= y <= 16 or 28 <= x <= 47 and 42 <= y <= 46: m.cell(x, y, SOFT_GRASS)
claim(0, 0, W - 1, 0)

RAIL_CELLS = set()


def rail(x, y):
    if (x, y) in STAIR_CELLS: return
    m.cell(x, y, RAILING, 1); RAIL_CELLS.add((x, y)); claim(x, y, x, y)


for x in range(3, 49):                                           # along the top of every retaining wall
    if (x, e2(x)) in KEEP_SET and not 24 <= x <= 27: rail(x, e2(x))
rail(22, 16); rail(30, 18)                                       # round the steps in the wall
for x in range(LOW_X[0], LOW_X[1] + 1):
    if x not in (11, 12): rail(x, E1)
for y in range(E1, 47): rail(21, y)                              # the garden's east side, above the drop


def pillar(x, y, pot=None):
    """A stone pillar on the railing row with a potted plant on top (the reference's stair heads)."""
    m.put(x, y, PILLAR[1]); m.put(x, y - 1, PILLAR[0], 3)
    m.put(x, y - 2, pot or POTS[(x + y) % len(POTS)], 3)
    claim(x, y - 2, x, y)


for x in (23, 28): pillar(x, 17)
for x in (10, 13): pillar(x, E1)
pillar(21, E1)


def on_wall(x, y, tile):
    """A window or vine on a wall. Avy tiles are passable, so a blank blocker goes over them on layer 3."""
    m.put(x, y, tile)
    if (_flag(tile) & 0x0f) != 0x0f and not (_flag(tile) & 0x10): m.put(x, y, BLOCKER, 3)


def _flag(tile):
    import validate_maps as V
    global _FL
    try: _FL
    except NameError: _FL = V.flags_for(TILESET)
    return _FL[tile] if tile < len(_FL) else 0


# ================================================================ buildings
SMOKES = []                                                      # chimney smoke, laid once everything else is down


def house(h):
    """Roof rows, then wall storeys top to bottom; gables, dormers, chimney, windows by storey, the door, signs.
    Returns the bottom (street level) row."""
    x0, x1, top, roof_rows, roof = h['x0'], h['x1'], h['top'], h['roof_rows'], h['roof']
    rt_y = top + roof_rows - 1
    m.rect(x0, top, x1, rt_y, ('A3', MED_ROOF[roof]))
    y, storeys = rt_y + 1, []
    for wall, n in h['walls']:
        m.rect(x0, y, x1, y + n - 1, ('A3', MED_WALL[wall])); storeys.append((wall, y, y + n - 1)); y += n
    bottom = h['bottom'] = y - 1
    claim(x0, top, x1, bottom)
    covered = set()
    for gx in h.get('gables', ()):
        for r, row in enumerate(GABLE['slate' if roof == 'slate' else 'shingle']):
            for c, n in enumerate(row):
                if n is not None and rt_y - 4 + r >= 0:
                    m.put(gx + c, rt_y - 4 + r, MV(n), 3); covered.add((gx + c, rt_y - 4 + r))
    for dx in h.get('dormers', ()):
        if (dx, top + roof_rows // 2) not in covered:
            m.put(dx, top + roof_rows // 2, MV(DORMER['slate' if roof == 'slate' else 'shingle']))
    if h.get('chimney'):
        cx, kind = h['chimney']
        if (cx, top) not in covered and (cx, top - 1) not in covered:
            m.put(cx, top - 1, MV(M_CHIMNEY[kind][0]), 3); m.put(cx, top, MV(M_CHIMNEY[kind][1]))
            if h.get('smoke'): SMOKES.append((cx, top - 3))
    door = h.get('door')
    for i, (wall, sy0, sy1) in enumerate(storeys):              # windows: two rows tall, every other column
        ground = i == len(storeys) - 1
        kinds = h.get('wins', {}).get(i) or (('arched', 'small') if wall in STONE_WALLS else ('flowers', 'wide', 'tall'))
        if sy1 - sy0 + 1 < 2: continue
        wy = sy1 - 1
        for k, x in enumerate(range(x0 + 1, x1, 2)):
            if ground and door is not None and abs(x - door) <= 1: continue
            a, b = M_WIN[kinds[k % len(kinds)]]
            m.put(x, wy, MV(a)); m.put(x, wy + 1, MV(b))
    if door is not None and not h.get('enter'):
        a, b = M_DOOR[h.get('door_look', 'wood')]
        m.put(door, bottom - 1, MV(a)); m.put(door, bottom, MV(b))
    for k, s in enumerate(h.get('signs', ())):
        m.put(door + (1, -1)[k], bottom - 2 if bottom - 2 > rt_y else bottom - 1, SIGN[s])
    if h.get('hang') is not None:                                # a sign hung out over the street
        hx, which = h['hang']
        m.put(hx, bottom - 1, HANGING_SIGN[which], 3)
    return bottom


# name: x0, x1, top, roof rows, walls [(kind, rows) top to bottom], roof, door x, + extras. `enter`: the ARRIVE key
# of the room behind the door, `lines`: what a latched door says.
HOUSES = [
    # ---- upper terrace
    dict(name='Old Henrik\'s House', x0=13, x1=19, top=7, roof_rows=3, walls=[('tudor', 2), ('rubble', 2)],
         roof='red', door=16, gables=(14,), chimney=(19, 'brick'), smoke=True, enter='lily_henrik_from_town'),
    dict(name='Shepherd\'s Cottage', x0=4, x1=9, top=5, roof_rows=3, walls=[('daub', 3)], roof='thatch', door=7,
         chimney=(4, 'stone'), wins={0: ('small', 'flowers')},
         lines=['Nobody home. A crook leans by the door, and there is wool caught in the latch.']),
    # ---- round Rose Square
    dict(name='Lantern & Lily', x0=8, x1=20, top=19, roof_rows=4, walls=[('plaster', 3), ('brick', 2)],
         roof='shingle', door=14, gables=(9, 15), signs=('inn', 'pub'), chimney=(8, 'brick'), smoke=True,
         hang=(17, 0), enter='lily_tavern_from_town'),
    dict(name='Tailor', x0=3, x1=7, top=19, roof_rows=3, walls=[('timber', 3)], roof='orange', door=4,
         signs=('armor',), lines=['Pinned to the door: "Mending only. No cloth till the cart comes."']),
    dict(name='Thistle & Wick', x0=37, x1=43, top=22, roof_rows=3, walls=[('timber', 2), ('timber_brick', 2)],
         roof='umber', door=40, signs=('item',), chimney=(42, 'brick'), hang=(38, 1), enter='lily_store_from_town'),
    dict(name='Smithy', x0=44, x1=48, top=22, roof_rows=3, walls=[('rubble', 4)], roof='slate', door=47,
         signs=('hammer',), chimney=(44, 'stone'), smoke=True, door_look='arched',
         lines=['The smith\'s house. The door is shut; the noise is all out in the yard.']),
    dict(name='Bakery', x0=29, x1=35, top=34, roof_rows=3, walls=[('brick', 3)], roof='red', door=32,
         signs=('eatery',), chimney=(30, 'brick'),
         lines=['The ovens are cold.', 'A slate on the door: "NO FLOUR. Ask at the villa."',
                'Someone has rubbed out "Ask at the villa" with a thumb.']),
    dict(name='Old Marta\'s House', x0=37, x1=42, top=32, roof_rows=3, walls=[('timber', 2), ('timber_brick', 2)],
         roof='shingle', door=41, gables=(37,), enter='lily_marta_from_town'),
    dict(name='Weaver\'s House', x0=44, x1=48, top=33, roof_rows=3, walls=[('daub', 3)], roof='moss', door=45,
         dormers=(47,), lines=['A loom clacks inside, then stops.', 'Nobody comes to the door.']),
    # ---- the lily-pond garden
    dict(name='Old Bram\'s House', x0=15, x1=20, top=33, roof_rows=3, walls=[('log', 3)], roof='thatch', door=18,
         chimney=(16, 'stone'), smoke=True, wins={0: ('small',)}, enter='lily_bram_from_town'),
]
for h in HOUSES: house(h)
DOORS = {h['name']: (h['door'], h['bottom']) for h in HOUSES if h.get('door') is not None}

# ---------------------------------------------------------------- the church
CH_X0, CH_X1, TOWER_X = 32, 42, 37                               # nave columns; the tower is TOWER_X-1..TOWER_X+1
CH_ROOF, CH_WALL, CH_BOTTOM = 9, 13, 16                          # nave roof from row 9, walls from 13, door row 16
m.rect(CH_X0, CH_ROOF, CH_X1, CH_WALL - 1, ('A3', MED_ROOF['slate']))
m.rect(CH_X0, CH_WALL, CH_X1, CH_BOTTOM, ('A3', MED_WALL['ashlar']))
m.rect(TOWER_X - 1, CH_ROOF, TOWER_X + 1, CH_BOTTOM, ('A3', MED_WALL['stone']))
for r, row in enumerate(SPIRE):                                  # the spire stands on the tower, over the ground
    for c, t in enumerate(row): m.put(TOWER_X - 1 + c, CH_ROOF - 7 + r, AV3(t), 3)   # behind the church
on_wall(TOWER_X, CH_ROOF, BELFRY[0]); on_wall(TOWER_X, CH_ROOF + 1, BELFRY[1])
on_wall(TOWER_X, CH_WALL - 1, ROSE_WINDOW[0]); on_wall(TOWER_X, CH_WALL, ROSE_WINDOW[1])
for k, x in enumerate((CH_X0 + 1, CH_X0 + 3, CH_X1 - 3, CH_X1 - 1)):
    a, b = STAINED_GLASS[k]
    on_wall(x, CH_WALL, a); on_wall(x, CH_WALL + 1, b)
    on_wall(x, CH_BOTTOM - 1, LATTICE[0]); on_wall(x, CH_BOTTOM, LATTICE[1])
claim(TOWER_X - 1, CH_ROOF - 7, TOWER_X + 1, CH_ROOF - 1); claim(CH_X0, CH_ROOF, CH_X1, CH_BOTTOM)
DOORS['Church'] = (TOWER_X, CH_BOTTOM)
for x in (CH_X0 + 2, CH_X1 - 2):                                 # rose bushes against the church wall
    m.put(x, CH_BOTTOM + 1, FLOWER_BUSH); claim(x, CH_BOTTOM + 1, x, CH_BOTTOM + 1)

STEPS = set(DOORS.values())
taken.update((x, y + 1) for x, y in STEPS)                       # nothing goes on a doorstep
taken.update((x, y) for x, y in STEPS)

# ---------------------------------------------------------------- the memorial garden by the church
GX0, GY0, GX1, GY1 = 44, 7, 48, 16
m.rect(GX0, GY0, GX1, GY1, SOFT_GRASS)
for x in range(GX0, GX1 + 1):
    for y in (GY0, GY1):
        if not (y == GY1 and x == 46): m.cell(x, y, RAILING, 1); RAIL_CELLS.add((x, y))
for y in range(GY0, GY1 + 1):
    m.cell(GX0, y, RAILING, 1); RAIL_CELLS.add((GX0, y))
claim(GX0, GY0, GX1, GY1)
ANGEL_AT = (46, 10)
m.put(ANGEL_AT[0], ANGEL_AT[1] - 1, ANGEL[0], 3); m.put(*ANGEL_AT, ANGEL[1])
for x, y in ((45, 11), (47, 11)): m.put(x, y, FLOWERS[x % 4])
m.put(45, 9, FLOWER_BUSH); m.put(47, 9, FLOWER_BUSH)
for c in range(2): m.put(45 + c, 13, BENCH[c])                  # a bench facing the angel
for x, y in ((48, 13), (48, 14)): m.put(x, y, FLOWERS[(x + y) % 4])

# ---------------------------------------------------------------- Rose Square
RX, RY = 24, 29                                                  # the rose tree's trunk row starts at (RX, RY)
m.rect(RX - 1, RY - 2, RX + 5, RY, SOFT_GRASS)                   # its raised bed
m.rect(RX - 1, RY + 1, RX + 5, RY + 1, BED_WALL)
for r, row in enumerate(ROSE_TREE):
    for c, t in enumerate(row):
        m.put(RX + c, RY - 6 + r, PF(t), 2 if r == 6 else 3)
claim(RX - 1, RY - 6, RX + 5, RY + 1)
for x in (RX - 1, RX + 5):
    m.put(x, RY - 1, FLOWER_BUSH); m.put(x, RY, FLOWERS[x % 4])
WELL_AT = (31, 23)                                               # the well and its winch frame (base row WELL_AT[1] + 1)
for c in range(2):
    m.put(WELL_AT[0] + c, WELL_AT[1], WELL_ROOFED[0][c], 3); m.put(WELL_AT[0] + c, WELL_AT[1] + 1, WELL_ROOFED[1][c])
    m.put(WELL_AT[0] + c, WELL_AT[1] + 1, BLOCKER, 3)
claim(WELL_AT[0], WELL_AT[1], WELL_AT[0] + 1, WELL_AT[1] + 1)
m.put(33, 24, BUCKET); claim(33, 24, 33, 24)


def stall(x, y, colour, goods):
    for r, row in enumerate(STALL[colour]):
        for c, t in enumerate(row): m.put(x + c, y + r, PM(t), 3 if r < 2 else 2)
    for c, g in enumerate(goods):
        if g is not None: m.put(x + c, y + 2, PM(g), 3)
    claim(x, y, x + 2, y + 3)


stall(33, 26, 'red', (16, 24, 32))                               # the greengrocer's, still trading
stall(33, 30, 'green', (None, None, None))                       # empty: it was the villa's flour stall
m.put(35, 34, PM(PRODUCE[6])); m.put(34, 34, MV(M_CRATE)); claim(34, 34, 35, 34)
for r in range(2):                                               # the flower seller's cart by the tavern corner
    for c in range(2): m.put(21 + c, 25 + r, PM(FLOWER_CART[r][c]), 3 if r == 0 else 2)
claim(21, 25, 22, 26)
for c in range(2): m.put(25 + c, 33, BENCH[c])                  # a bench facing the rose tree
claim(25, 33, 26, 33)
NOTICE_AT = (21, 21)
m.put(*NOTICE_AT, NOTICE_BOARD); claim(*NOTICE_AT, *NOTICE_AT)
for x, y in ((22, 19), (22, 23), (34, 22), (35, 23)):            # pots round the square
    if free(x, y): m.put(x, y, POTS[(x * 3 + y) % len(POTS)]); claim(x, y, x, y)

# ---------------------------------------------------------------- the smithy's yard
SMITH = '!$PM_Blacksmith'
m.rect(44, 31, 48, 32, ('A2', 8))                                # beaten earth and cinders
claim(44, 31, 48, 32)



def place(x, y, tile, layer=2, need_free=True):
    """Put an object where nothing else is; says so when the spot is already used (so a layout change shows)."""
    if need_free and not free(x, y):
        print('  skipped', x, y, tile); return False
    m.put(x, y, tile, layer); claim(x, y, x, y)
    return True


def block(x0, y0, rows, layers=None):
    """A multi-tile object: rows top to bottom; the last row stands on the ground (layer 2), the rest go above (3)."""
    for r, row in enumerate(rows):
        for c, t in enumerate(row):
            if t: m.put(x0 + c, y0 + r, t, (layers[r] if layers else (2 if r == len(rows) - 1 else 3)))
    claim(x0, y0, x0 + len(rows[0]) - 1, y0 + len(rows) - 1)


def fence(x0, y0, x1, y1, gates=(), kind=PICKET):
    for x in range(x0, x1 + 1):
        for y in range(y0, y1 + 1):
            if (x in (x0, x1) or y in (y0, y1)) and (x, y) not in gates:
                m.cell(x, y, kind, 1); claim(x, y, x, y)


def plot(x0, y0, x1, y1, crops):
    """Tilled rows with a crop in each, a different one per row."""
    m.rect(x0, y0, x1, y1, TILLED)
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1): m.put(x, y, crops[(y - y0) % len(crops)])
    claim(x0, y0, x1, y1)


# ---------------------------------------------------------------- the smithy's yard (events below)
FORGE_HOOD, FORGE_AT, ANVIL_AT, QUENCH_AT, SMITH_AT = (48, 31), (47, 32), (45, 31), (44, 32), (46, 31)

# ---------------------------------------------------------------- the upper terrace: yards and gardens
m.rect(7, 11, 7, 13, FOOTPATH)                                   # the shepherd's path to the lane
plot(4, 11, 6, 12, CROPS[:2])
block(8, 11, WOODPILE)
place(10, 10, BASIN)
block(10, 8, FRUIT_TREE)
block(20, 4, ROUND_TREE)
block(21, 9, FLOWER_BED)
block(28, 4, ROUND_TREE)
block(30, 9, [(CONIFER[0],), (CONIFER[1],)])
block(32, 4, ROUND_TREE); block(40, 3, ROUND_TREE); block(43, 4, SMALL_ROUND)
for x, y in ((35, 6), (39, 7), (34, 3)): place(x, y, FLOWERS[(x + y) % 4])
for x, ivy in ((5, 2), (19, 3), (31, 2), (40, 3), (47, 2), (16, 2), (6, 3)):   # ivy down the retaining walls
    y = e2(x) + 1 if level(x, e2(x) + 1) == 'F2' else None
    if x in (16, 6): y = E1 + 1
    if y is not None and (x, y) not in STAIR_CELLS:
        on_wall(x, y, (192, 193, 194, 195)[ivy]); on_wall(x, y + 1, (200, 201, 202, 203)[ivy])
place(29, 11, FLOWER_BUSH); place(30, 12, FLOWERS[1]); place(29, 15, FLOWERS[3])
for r in range(2):                                               # a rose climbing Henrik's wall
    for c in range(2): on_wall(18 + c, 12 + r, ROSE_BUSH[r][c])

# ---------------------------------------------------------------- round the square and the lanes
for x, y, t in ((8, 28, MV(M_BARREL)), (9, 28, MV(M_BARREL2)), (7, 26, MV(M_BARREL)), (7, 25, FLOWER_BUSH),
                (20, 28, MV(M_CRATE)), (43, 29, MV(M_CRATE)), (48, 29, MV(M_BARREL)),
                (28, 41, MV(M_BARREL)), (43, 38, FLOWER_BUSH)):
    place(x, y, t)
for x in (5, 6):                                                 # the tailor's yard
    place(x, 26, FLOWERS[x % 4])
m.rect(4, 25, 4, 27, FOOTPATH)

# ---------------------------------------------------------------- the lily-pond garden
POND = [(x, y) for y in range(36, 45) for x in range(4, 13)
        if (x, y) not in ((4, 36), (5, 36), (12, 36), (4, 37), (4, 44), (11, 44), (12, 44))]
for x, y in POND: m.cell(x, y, POND_WATER)
for x, y in ((6, 38), (7, 38), (10, 37), (5, 41), (6, 42), (9, 43), (10, 42)): m.cell(x, y, LILY_PADS, 1)
for x, y in ((8, 37), (5, 39), (11, 38), (7, 43)): m.put(x, y, LILIES[(x + y) % 2])
for x in range(9, 13):                                           # the jetty from the east bank
    m.cell(x, 40, ('A5', JETTY[0])); m.cell(x, 41, ('A5', JETTY[1]))
claim(4, 36, 12, 44)
m.rect(11, 33, 12, 34, FOOTPATH); m.rect(13, 34, 14, 34, FOOTPATH)    # from the steps to Bram's door and the jetty
m.rect(14, 35, 14, 41, FOOTPATH); m.rect(15, 39, 18, 39, FOOTPATH); m.rect(13, 40, 13, 41, FOOTPATH)
block(4, 33, FLOWER_BED); block(8, 33, FLOWER_BED)
for c in range(2): m.put(6 + c, 34, BENCH[c])                   # a bench looking over the pond
claim(6, 34, 7, 34)
for x, y in ((3, 38), (3, 41), (13, 44), (4, 45), (8, 45), (12, 45)):
    place(x, y, FERN if (x + y) % 2 else FLOWER_BUSH)
for x, y in ((5, 45), (10, 45), (3, 44)): place(x, y, FLOWERS[(x + y) % 4])
plot(16, 42, 19, 44, (CROPS[2], CROPS[3]))                       # Bram's vegetables
fence(15, 41, 20, 45, gates={(15, 43)})
block(19, 40, WOODPILE)

# ---------------------------------------------------------------- the gardens by the south road
plot(30, 42, 34, 45, CROPS)
fence(29, 41, 35, 46, gates={(32, 41)})
place(32, 43, SCARECROW, need_free=False)
for x, y in ((37, 42), (40, 42), (38, 45)):                      # the orchard
    block(x, y - 1 if y == 42 else y - 2, FRUIT_TREE if x != 40 else FRUIT_TREE2)
place(42, 44, AV4(2)); place(36, 44, AV4(1))
fence(43, 41, 48, 46, gates={(45, 41)})                          # the hens' run
block(46, 45, [HAYSTACK])
place(47, 42, HAY)

# ---------------------------------------------------------------- lamp posts
LAMPS = [(23, 13), (28, 13), (31, 16), (43, 18), (11, 13), (3, 27), (21, 24), (30, 33), (23, 38), (28, 38),
         (22, 44), (28, 44), (13, 39), (36, 41), (36, 27)]
for x, y in LAMPS:
    if all(free(x, y - d) for d in range(3)): m.lamp(x, y); claim(x, y - 2, x, y)
    else: print('  lamp skipped', x, y)


import validate_maps as _V
_FLAGS = _V.flags_for(TILESET)


def blocked_now(x, y):
    """The cell blocks the player as the map stands (before the smoke goes on)."""
    return not m.walkable(x, y, _DATA, _FLAGS)


_DATA = m.tile_data()
for cx, cy in SMOKES:                                            # smoke (Avy tiles are passable) only over cells that
    cells = [(cx, cy), (cx, cy + 1)]                             # are open ground anyway or can never be reached
    if all(not blocked_now(x, y) and (m.get(x, y) or ('',))[0] in ('A2', 'A5') for x, y in cells):
        m.put(cx, cy, SMOKE[0], 3); m.put(cx, cy + 1, SMOKE[1], 3)
    else:
        print('  smoke skipped', cx, cy)


# ================================================================ events
def look(name, x, y, lines, note=''):
    return m.add_event(name, x, y, [page(None, priority=1, commands=text(*lines))], note)


def thing(name, x, y, sheet, idx, direction=2, pattern=1, lines=None, note='', priority=1, through=False):
    """A still object drawn from a character sheet (the smithy's forge, anvil...)."""
    return m.add_event(name, x, y, [page(char(sheet, idx, direction, pattern), priority=priority, through=through,
                                         commands=text(*lines) if lines else None, walk_anim=False)], note)


# ---- doors
for h in HOUSES:
    if h.get('door') is None: continue
    x, y = h['door'], h['bottom']
    if h.get('enter'):
        a = K.ARRIVE[h['enter']]
        m.door(h['name'], x, y, a[0], a[1], a[2], style=h.get('door_style', 0))
    else:
        m.add_event(h['name'], x, y, [page(None, priority=1, commands=text(*h['lines']))])
a = K.ARRIVE['lily_chapel_from_town']
m.door('Church', TOWER_X, CH_BOTTOM, a[0], a[1], a[2], style=2)

# ---- the smithy's forge (!$PM_Blacksmith: row = direction 2/4/6/8, column = pattern)
thing('Forge Hood', FORGE_HOOD[0], FORGE_HOOD[1], SMITH, 0, 4, 0, through=False)
thing('Forge', FORGE_AT[0], FORGE_AT[1], SMITH, 0, 8, 0, ['The coals are banked, still red under the ash.'],
      note='<light: 120, #ff8a3a, flicker>')
thing('Anvil', ANVIL_AT[0], ANVIL_AT[1], SMITH, 0, 6, 1, ['A horseshoe, half hammered, cooling on the anvil.'])
thing('Quench Bucket', QUENCH_AT[0], QUENCH_AT[1], SMITH, 0, 8, 2, ['Black water, and a skin of scale on top.'])

# ---- signs and things to look at
look('Signpost North', 27, 3, ['North: Hollow Wood, then Mistveil.', 'Carved under it, very old: a small rose.'])
m.put(27, 3, SIGNPOST)
look('Signpost South', 27, 46, ['\\C[6]Lilydale\\C[0]', 'South: down the valley.'])
m.put(27, 46, SIGNPOST)
look('Notice Board', *NOTICE_AT, ['MARKET DAY - every seventh day, in Rose Square.',
                                  'Pinned below, newer: "Has anyone seen Hanna from the villa?"'])
look('Old Well', WELL_AT[0] + 1, WELL_AT[1] + 1, ['The stones are worn smooth where a hundred years of hands have rested.'])
look('Empty Stall', 34, 33, ['Flour dust in the cracks of the counter, and nothing else.',
                             'This was where the villa\'s cart unloaded.'])
look('Rose Tree', RX + 2, RY + 1, ['An old tree with leaves the colour of wine.',
                                   'Children have carved their names into the bark, low down.',
                                   'One name is carved higher than the others, as if by someone who never grew any taller.'])
look('Lily Pond', 13, 36, ['White lilies. The village was named for them, or they for the village -',
                           'nobody remembers which came first.'])
place(13, 36, SIGNPOST)
look('Memorial Angel', *ANGEL_AT, ['On the plinth, the names of those the war took, sixteen years ago.',
                                   'Under one of them someone has left white lilies. They are fresh.'])

# ---- people (chapter 7, before the party sets out)
m.npc('Old Bram', RX, RY + 2, 'People1', 6, ('Old Bram:', 'We used to play under this tree, the lot of us.',
      'Funny. I can\'t remember my own wedding, but I remember that.'), direction=8)
m.npc('Old Marta', 29, 22, 'People1', 7, ('Old Marta:', 'The villa folk always came on market day, down that stair.',
      'Three weeks now. Not even Hanna with her basket.'), direction=8)
m.npc('Shepherd', 9, 15, 'People1', 2, ('Shepherd:', 'Two ewes dead in the north pasture. Not a mark on the wool.',
      'Folk say it\'s the villa. I say it\'s something out of that wood.'), move=1, freq=2)
m.npc('Young Mother', 23, 36, 'People1', 3, ('Young Mother:', 'The priest from the road says the house in the mist is cursed.',
      'My gran says it was the kindest house in the valley.'), move=1, freq=2)
m.npc('Tavern Regular', 12, 29, 'People4', 5, ('Tavern Regular:', 'Ale\'s gone thin since the villa stopped buying.',
      'Funny how a house nobody visits keeps a whole village fed.'), direction=8)
m.npc('Greengrocer', 32, 28, 'People2', 4, ('Greengrocer:', 'Apples, greens, the last of the oranges.',
      'Buy something, would you? Half the square\'s gone quiet.'), direction=6)
m.npc('Bell-Ringer', 35, 18, 'People4', 1, ('Bell-Ringer:', 'Every spring we ring the bell for the lady of the villa.',
      'She was born two lanes from here, you know. Married the quiet gentleman from the hill.'), direction=2)
m.add_event('Smith', SMITH_AT[0], SMITH_AT[1], [page(char(SMITH, 0, 2, 1), dir_fix=True, walk_anim=False, commands=L.say(
    'Smith:', 'Ploughshares, hinges, horseshoes. Never had call for swords here.',
    'Had two men from the road ask for one this week, mind. Paid in silver. Didn\'t like their eyes.'))])
m.npc('Boy', 27, 21, 'People1', 0, ('Boy:', 'Grandpa says a vampire used to give him sweets!', 'I think he\'s making it up.'),
      move=1, speed=4, freq=4)
m.npc('Girl', 6, 28, 'People2', 0, ('Girl:', 'Don\'t go in the wood. The mist eats sound.', 'Mama says so.'),
      move=1, speed=4, freq=4)
m.npc('Gardener', 14, 43, 'People4', 2, ('Gardener:', 'Lilies don\'t care who comes to market.',
      'Wish I could say the same for the rest of us.'), direction=6)
m.critter('Cat', 30, 30, 'Nature', 1, 'Cat', 'The cat stretches on the warm stones.', move=1, freq=2)
m.critter('Dog', 5, 13, 'Nature', 0, 'Dog', 'The shepherd\'s dog wags, then goes back to watching the north road.',
          move=1, freq=2, area=(4, 11, 10, 15))
m.critter('Carthorse', 48, 30, 'Nature', 3, 'Horse', 'The carthorse waits for its new shoes, one hoof lifted.', move=0)
for i, (x, y) in enumerate(((45, 44), (46, 43))):
    m.critter('Hen %d' % (i + 1), x, y, 'Nature', 2, 'Chicken', 'Cluck.', move=1, freq=3, area=(44, 42, 47, 45))
m.critter('Rooster', 44, 44, 'Animals2', 7, 'Chicken', 'The rooster eyes you as if you owe it money.', move=1, freq=3,
          area=(44, 42, 47, 45))
for i, (x, y) in enumerate(((6, 40), (10, 38))):
    m.add_event('Swan %d' % (i + 1), x, y, [page(char('Animals2', 3, 4 if i else 6), move_type=1, priority=0,
                                                  through=True, freq=2, speed=2, step_anim=False)],
                note='<pen: 5,37,11,43>')

# ---- exits
for x in NORTH_X:
    a = K.ARRIVE['hollow_from_lilydale']
    m.add_event('To Hollow Wood %d' % x, x, 0, [L.exit_page(K.HOLLOW_WOOD, a[1] + x - NORTH_X[0], a[2], 8)],
                note='<minimap: exit>')

ARRIVALS = [K.ARRIVE['lilydale_from_hollow'][1:3], (SOUTH_X[0], H - 2)]


def leaks(data=None):
    """Walkable cells on two different levels side by side (other than up and down the stairs)."""
    data = data or m.tile_data()
    import validate_maps as V
    flags = V.flags_for(TILESET)
    out = []
    for y in range(H):
        for x in range(W):
            if not m.walkable(x, y, data, flags): continue
            for dx, dy in ((1, 0), (0, 1)):
                nx, ny = x + dx, y + dy
                if not m.inb(nx, ny) or not m.walkable(nx, ny, data, flags): continue
                a, b = level(x, y), level(nx, ny)
                if (x, y) in STAIR_CELLS or (nx, ny) in STAIR_CELLS: continue
                if a != b and (x, y) in KEEP_SET and (nx, ny) in KEEP_SET: out.append(((x, y), a, (nx, ny), b))
    return out


if __name__ == '__main__':
    out = next((a for a in sys.argv[1:] if not a.startswith('--')), None)
    reach = m.reach([tuple(a) for a in ARRIVALS])
    bad = [n for n, (x, y) in DOORS.items() if (x, y + 1) not in reach]
    print('%d doors' % len(DOORS), 'unreachable doors:', [(b, DOORS[b]) for b in bad] or 'none')
    for h in HOUSES + [dict(name='Church', door=TOWER_X, bottom=CH_BOTTOM, enter='lily_chapel_from_town')]:
        if h.get('enter'):
            back = [k for k, v in K.ARRIVE.items() if k.startswith('lilydale_from_') and v[1:3] == (h['door'], h['bottom'] + 1)]
            print('%-22s door (%d,%d)' % (h['name'], h['door'], h['bottom']), 'arrival key:', back or 'MISSING')
    for e in m.events[1:]:
        if e['name'] in DOORS or e['name'].startswith('To ') or e['pages'][0].get('through'): continue
        if not any((e['x'] + dx, e['y'] + dy) in reach for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
            print('unreachable', e['name'], e['x'], e['y'])
    pos = {}
    for e in m.events[1:]: pos.setdefault((e['x'], e['y']), []).append(e['name'])
    print('stacked events:', [v for v in pos.values() if len(v) > 1] or 'none')
    print('level leaks:', leaks() or 'none')
    solid = [(x, y) for x, y in reach if (m.get(x, y) or ('',))[0] in ('A3', 'A4', 'A1') or (x, y) in RAIL_CELLS]
    print('walls/roofs/water/railings reachable:', solid or 'none')
    if out: m.render(out, scale=0.5 if '--full' not in sys.argv else 1, grid='--grid' in sys.argv)
    if '--save' in sys.argv:
        import tileset_wizard
        if tileset_wizard.editor_running(): sys.exit('close RPG Maker MV first')
        m.save(K.LILYDALE, parent_id=K.WORLD)
        import compose_tileset as C                              # the mood tags and the battle background go back on
        from map_moods import MOODS, set_tag
        from battlebacks import BB
        path = L.DATA + 'Map%03d.json' % K.LILYDALE
        j = C._read(path)
        for tag, value in MOODS.get(K.LILYDALE, {}).items(): j['note'] = set_tag(j['note'], tag, value)
        b1, b2 = BB[K.LILYDALE]
        j.update({'specifyBattleback': True, 'battleback1Name': b1, 'battleback2Name': b2})
        with open(path, 'w', encoding='utf8', newline='') as f: f.write(C._map_text(j))
        print('saved Map%03d' % K.LILYDALE)
