# MAP031 - Quillhaven and the Royal Magic Academy's gate: the Academy's castle front north of the capital, up the
# coast road, and the village of Quillhaven that grew up facing it (lodgings, an inn, an apothecary and a bookshop
# for students, scholars and visiting families). The castle front fills the top of the map, its walled forecourt opens
# through an iron fence onto the road; the village lies south of the road around a dirt square with a well, its
# cottages, gardens and the chicken run scattered among the trees, the whole of it hemmed in by woodland.
# Laid out after the usual village plan (green and well at the centre, inn on the square with its yard and pens,
# cottages with kitchen gardens, paths that wind the way people walk) and RPG Maker's own town-mapping advice
# (no grid, mixed trees, details everywhere).
# The road comes in from the east (the coast road on the World Map), the village path from the south.
#   python map_academy.py preview.png [--grid]   -> preview image
#   python map_academy.py --save                 -> write Map031 (editor must be closed)
import sys, os, math, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from town_kit import *
from nova_maplib import page, char, text
import nova_maplib as L
import kingdom as K
from town_kit import wander_route

W, H = 56, 50
m = Town(W, H, K.NAMES[K.ACADEMY][0], K.NAMES[K.ACADEMY][1], ground=GRASS)
m.bgm = {'name': 'Town5', 'pan': 0, 'pitch': 100, 'volume': 75}
P = PROP
rnd = random.Random(31)
GX = 27                                         # the Academy gate
CX0, CX1 = 8, 47                                # the castle front
ROAD_Y = (18, 20)
SOUTH = (25, 29)                                # the path out to the south
SQUARE = (27, 31)                               # the well in the middle of the village square
BLOCKER = 767                                   # Nova_Market_D's last cell: empty and impassable (see Briarwood)
assert K.ARRIVE['academy_from_world_east'][1:3] == (W - 2, 19) and K.ARRIVE['academy_from_world_south'][1:3] == (GX, H - 2)
assert K.ARRIVE['academy_from_hall'][1:3] == (GX, 11)
TOWER = [(176, 177), (184, 185), (192, 193), (200, 201), (192, 193), (208, 209)]
# objects from the NovaTilesetEx extra sheets: (sheet, rows of tile numbers, rows on the ground layer at the bottom)
X = {
    'magic_tree': ('PM_Forest', [(200, 201, 202, 203, 204), (208, 209, 210, 211, 212), (216, 217, 218, 219, 220),
                                 (224, 225, 226, 227, 228), (232, 233, 234, 235, 236), (240, 241, 242, 243, 244),
                                 (248, 249, 250, 251, 252)], 2),          # violet-leaved, 5x7, trunk and shadow below
    'leafy_tree': ('PM_Nature1', [(128, 129), (136, 137), (144, 145)], 1),
    'leafy_tree2': ('PM_Nature1', [(130, 131), (138, 139), (146, 147)], 1),
    'round_tree': ('PM_Nature1', [(134, 135), (142, 143), (150, 151)], 1),
    'park_tree': ('Avy_Town_B', [(104, 105), (112, 113), (120, 121)], 1),
    'big_oak': ('PM_Forest', [(16, 17, 18), (24, 25, 26), (32, 33, 34)], 1),
    'swing': ('PM_Nature1', [(246, 247), (254, 255)], 1),
    'bush': ('PM_Forest', [(64,)], 1), 'bush2': ('PM_Forest', [(65,)], 1),
    'fern': ('PM_Forest', [(80,), (88,)], 1),
    'stump_big': ('PM_Nature1', [(216, 217, 218), (224, 225, 226)], 1),
    'axe_stump': ('PM_Nature1', [(219,)], 1),
    'log_pile': ('PM_Nature1', [(222, 223), (230, 231)], 1),
    'garden_bench': ('Avy_Town_B', [(102, 103), (110, 111)], 1),        # white park bench
    'birdbath': ('Avy_Town_B', [(68,), (76,)], 1),
    'planter': ('Avy_Town_B', [(58,)], 1), 'planter_green': ('Avy_Town_B', [(59,)], 1),
    'roofed_well': ('Avy_Town_B3', [(5, 6), (13, 14)], 1),
    'wood_bench': ('Avy_Town_B3', [(220, 221), (228, 229)], 1),
    'flower_box': ('Avy_Town_B3', [(113, 114), (121, 122)], 1),
    'mushrooms': ('Nova_Nature', [(128, 129)], 1),
    'pink_flowers': ('Nova_Nature', [(24, 25), (32, 33)], 2),
    'rock': ('Nova_Nature', [(1,)], 1), 'pebbles': ('Nova_Nature', [(3,)], 1),
    'carrots': ('Nova_Farm', [(25,)], 1), 'cabbages': ('Nova_Farm', [(26,)], 1), 'mandrakes': ('Nova_Farm', [(27,)], 1),
    'wheat': ('Nova_Farm', [(24,)], 1), 'sprouts': ('Nova_Farm', [(17,)], 1),
    'nest': ('Nova_Farm', [(170,)], 1), 'nest_full': ('Nova_Farm', [(178,)], 1), 'hen_on_nest': ('Nova_Farm', [(185,)], 1),
    'scales': ('PM_Market', [(122,)], 1), 'potions': ('PM_Market', [(123,)], 1), 'grain_sack': ('PM_Market', [(127,)], 1),
    'hay': ('PM_Village2', [(219, 220), (227, 228)], 1),
    'baskets': ('Avy_Town_B4', [(1,)], 1), 'jars': ('Avy_Town_B4', [(30,)], 1),
}
# 2x2 trees for the woods around the village, picked at random for a mixed wood: (crown row, trunk row)
pair = lambda sheet, a, b: ((L.ext(sheet, a), L.ext(sheet, a + 1)), (L.ext(sheet, b), L.ext(sheet, b + 1)))
WOOD_TREES = [BIG_TREE, BIG_TREE2, pair('PM_Nature1', 114, 122), pair('PM_Nature1', 116, 124),
              pair('PM_Forest', 112, 120), pair('PM_Forest', 116, 124)]
WOOD_WEIGHTS = [5, 3, 2, 2, 2, 1]
taken, paths, keep = set(), set(), set()       # cells with an object / a path / never wooded


def tower(x0, top=4):
    for i, (a, b) in enumerate(TOWER):
        m.put(x0, top + i, C_ + a, 3 if i < 5 else 2); m.put(x0 + 1, top + i, C_ + b, 3 if i < 5 else 2)


def ext_obj(name, x, y):
    """An object from X at (x, y) = its top-left tile; the upper rows above the characters, the ground rows below."""
    sheet, rows, ground = X[name]
    for r, row in enumerate(rows):
        for c, n in enumerate(row):
            m.put(x + c, y + r, L.ext(sheet, n), 2 if r >= len(rows) - ground else 3)
            taken.add((x + c, y + r))


def keep_rect(x0, y0, x1, y1):
    keep.update((x, y) for x in range(x0, x1 + 1) for y in range(y0, y1 + 1))


def seg_dist(p, a, b):
    (px, py), (ax, ay), (bx, by) = p, a, b
    dx, dy = bx - ax, by - ay
    t = max(0, min(1, ((px - ax) * dx + (py - ay) * dy) / float(dx * dx + dy * dy or 1)))
    return math.hypot(px - ax - t * dx, py - ay - t * dy)


def path(points, width=1.0):
    """A worn dirt path along a polyline (width = half-width in tiles)."""
    for y in range(H):
        for x in range(W):
            if min(seg_dist((x, y), points[i], points[i + 1]) for i in range(len(points) - 1)) < width:
                m.cell(x, y, DIRT); paths.add((x, y))


def fence_box(x0, y0, x1, y1, gates=()):
    m.rect(x0, y0, x1, y0, FENCE, layer=1); m.rect(x0, y1, x1, y1, FENCE, layer=1)
    m.rect(x0, y0, x0, y1, FENCE, layer=1); m.rect(x1, y0, x1, y1, FENCE, layer=1)
    for g in gates: m.cell(g[0], g[1], None, layer=1)
    keep_rect(x0, y0, x1, y1)


def house(x0, x1, top, roof_rows, wall_rows, roof, wall, door, **kw):
    b = m.building(x0, x1, top, roof_rows, wall_rows, roof, wall, door=door, **kw)
    keep_rect(x0 - 1, top, x1 + 1, b + 1)
    taken.update((x, y) for x in range(x0, x1 + 1) for y in range(top, b + 1))
    return b


# ---------------------------------------------------------------- the Academy: castle front, slate roof and spires
m.rect(CX0, 0, CX1, 4, CASTLE_TOP)
m.rect(CX0, 5, CX1, 10, CASTLE_WALL)
m.rect(CX0 + 4, 0, CX1 - 4, 1, ('A3', ROOF['indigo']))
for x0 in (14, GX - 1, 39):
    for i, (a, b) in enumerate([(194, 195), (202, 203)]):
        m.put(x0, i, C_ + a, 3); m.put(x0 + 1, i, C_ + b, 3)
for x0 in (GX - 4, GX + 3): tower(x0)
# the dormitory towers at the ends of the front, taller and twice as broad as the others: Duskward (west, its banners
# dusk-red) and Dawnward (east, gold); some two hundred and forty students live in them
DORM_TOWER = [(176, 177), (184, 185), (192, 193), (200, 201), (192, 193), (200, 201), (192, 193), (200, 201), (192, 193), (208, 209)]
for x0, banner in ((CX0, BANNER_RED), (CX1 - 3, BANNER_TAN)):
    for dx in (0, 2):
        for i, (a, b) in enumerate(DORM_TOWER):
            m.put(x0 + dx, i, C_ + a, 3 if i < len(DORM_TOWER) - 1 else 2); m.put(x0 + dx + 1, i, C_ + b, 3 if i < len(DORM_TOWER) - 1 else 2)
    m.tall(x0 + 4 if x0 == CX0 else x0 - 1, 6, banner)
for x in (16, 20, 34, 38): m.tall(x, 6, BANNER_BLUE)
for x in (14, 18, 36, 40): m.put(x, 8, STAINED)
m.put(GX, 6, SIGN['magic'])
m.put(GX - 1, 8, LG_TOP); m.put(GX + 1, 8, LG_TOP)
keep_rect(CX0, 0, CX1, 17)

# ---------------------------------------------------------------- the forecourt: gardens either side of the walk
m.rect(CX0, 11, CX1, 16, COBBLE)
m.rect(GX - 1, 11, GX + 1, 17, COBBLE_B)
m.relief(GX - 3, 13, GX + 3, 14, RELIEF_B)
for x0, x1 in ((CX0 + 1, GX - 5), (GX + 5, CX1 - 1)):
    m.rect(x0, 12, x1, 15, GRASS)
    m.rect(x0, 12, x1, 12, HEDGE_TOP)
    for x in range(x0 + 1, x1, 3): m.put(x, 13, FLOWERS[x % 4])
    for x in range(x0 + 2, x1, 3): m.put(x, 15, FLOWERS[(x + 2) % 4])
    m.put(x0, 14, TREE_S1, 3); m.put(x0, 15, TREE_S3)
    m.put(x1, 14, TREE_S1, 3); m.put(x1, 15, TREE_S3)
m.tall(GX - 3, 11, ANGEL_A); m.tall(GX + 3, 11, ANGEL_B)
for x in (GX - 2, GX + 2): m.lamp(x, 16)
ext_obj('magic_tree', 37, 10)                   # the old violet tree in the east garden
ext_obj('garden_bench', 12, 13); ext_obj('garden_bench', 15, 13); ext_obj('birdbath', 19, 13)
for x in (GX - 5, GX + 5): ext_obj('planter', x, 11)
ext_obj('planter_green', CX0 + 1, 11); ext_obj('planter_green', CX1 - 1, 11)
m.rect(CX0, 17, GX - 3, 17, METAL_FENCE, layer=1)
m.rect(GX + 3, 17, CX1, 17, METAL_FENCE, layer=1)
m.rect(CX0, 11, CX0, 17, METAL_FENCE, layer=1)
m.rect(CX1, 11, CX1, 17, METAL_FENCE, layer=1)

# ---------------------------------------------------------------- the road, from the coast road (east)
m.rect(CX0, ROAD_Y[0], W - 1, ROAD_Y[1], ROAD)
keep_rect(CX0, ROAD_Y[0], W - 1, ROAD_Y[1])
m.put(GX + 4, 21, SIGNPOST); taken.add((GX + 4, 21))

# ---------------------------------------------------------------- Quillhaven: paths first (they wind between the houses)
path([(GX, 21), (GX, 25), SQUARE], 1.6)                                      # from the gate down to the square
path([SQUARE, (26.5, 40), (27, H)], 1.5)                                     # out to the south
path([SQUARE, (18, 29.5), (10, 28.5)], 1.1)                                  # west to the inn
path([SQUARE, (34, 29.5), (40, 28.5)], 1.1)                                  # east to the apothecary
path([(40, 28.5), (44, 31), (44, 37)], 0.9)                                  # ... on to the bookshop
path([(10, 28.5), (11.5, 31), (11.5, 45.5), (6, 45.5)], 0.8)                 # down past the chicken run to the west cottages
path([(11.5, 40.5), (16, 40.5)], 0.8)
path([(18, 46.5), (26, 46.5)], 0.8)
path([(26.5, 38), (33, 38.5), (33, 43)], 0.8)                                # east cottages
path([(44, 37), (46, 40), (46, 44)], 0.8)
for y in range(H):                                                           # the square: an oval of trodden earth
    for x in range(W):
        if ((x - SQUARE[0]) / 6.2) ** 2 + ((y - SQUARE[1]) / 3.6) ** 2 < 1: m.cell(x, y, DIRT); paths.add((x, y))
m.rect(SQUARE[0] - 1, SQUARE[1] - 1, SQUARE[0] + 2, SQUARE[1] + 1, GRASS)      # a patch of green round the well
paths -= {(x, y) for x in range(SQUARE[0] - 1, SQUARE[0] + 3) for y in range(SQUARE[1] - 1, SQUARE[1] + 2)}
keep_rect(SQUARE[0] - 7, SQUARE[1] - 4, SQUARE[0] + 7, SQUARE[1] + 4)

# ---------------------------------------------------------------- the square: well, a pedlar's tent, notice board
ext_obj('roofed_well', SQUARE[0], SQUARE[1] - 1)
m.tent(31, 27); taken.update((x, y) for x in range(31, 34) for y in range(27, 30))
for x, y, t in ((30, 29, CRATE), (34, 29, BARREL), (34, 28, CRATE_APPLE)): m.put(x, y, t); taken.add((x, y))
ext_obj('baskets', 30, 30); ext_obj('jars', 34, 30)
m.put(22, 30, NOTICE_BOARD); taken.add((22, 30))
ext_obj('wood_bench', 23, 33); ext_obj('wood_bench', 30, 33)
for x, y in ((21, 27), (33, 25), (21, 34), (34, 34)): m.lamp(x, y); taken.update({(x, y - 2), (x, y - 1), (x, y)})

# ---------------------------------------------------------------- the Inkpot Inn (west of the square) and its yard
inn = house(5, 15, 22, 3, 3, 'red', 'tudor', 10, win_tiles=(WIN, WIN_FLOWER_P))
m.put(7, 23, CHIMNEY_A); m.put(13, 23, CHIMNEY_A)
m.put(12, inn - 1, SIGN['inn'])
ext_obj('flower_box', 6, inn - 1)
for x, y, t in ((14, inn + 1, BARREL), (15, inn + 1, BARREL), (5, inn + 1, CRATE)): m.put(x, y, t); taken.add((x, y))
# the chicken run south of the inn: a fenced pen with the coop in one corner
PEN = (3, 31, 10, 37)
fence_box(*PEN, gates=[(PEN[2], 34)])
m.rect(PEN[0] + 1, PEN[1] + 1, PEN[2] - 1, PEN[3] - 1, DIRT)
coop = m.building(4, 6, 32, 1, 2, 'wood', 'planks', windows=False)
m.put(5, coop, DOOR_HOLE)
for name, x, y in (('nest_full', 7, 32), ('nest', 8, 32), ('hen_on_nest', 9, 32), ('hay', 8, 35), ('grain_sack', 4, 35)):
    ext_obj(name, x, y)

# ---------------------------------------------------------------- Moonwell Apothecary (east of the square), herb beds
apo = house(37, 44, 23, 2, 3, 'green', 'white', 40, win_tiles=(WIN_FLOWER_G,))
m.put(38, 24, CHIMNEY_A); m.put(42, apo - 2, SIGN['item'])
ext_obj('potions', 38, apo + 1); ext_obj('scales', 43, apo + 1)
fence_box(46, 23, 51, 28, gates=[(46, 26)])
for y, crop in zip((24, 26), ('mandrakes', 'sprouts')):
    for x in range(47, 51): ext_obj(crop, x, y)

# ---------------------------------------------------------------- Quill & Candle, the bookshop
books = house(41, 47, 32, 2, 3, 'indigo', 'plaster', 44, win_tiles=(WIN_FLOWER_P, WIN))
m.put(42, 33, CHIMNEY_A); m.put(46, books - 2, SIGN['magic'])
ext_obj('baskets', 47, books + 1)

# ---------------------------------------------------------------- cottages, each with its garden
c1 = house(13, 18, 35, 2, 3, 'thatch', 'log', 16, win_tiles=(WIN_SHUT, WIN))
fence_box(19, 36, 23, 40, gates=[(21, 40)])
for y, crop in zip((37, 39), ('carrots', 'cabbages')):
    for x in range(20, 23): ext_obj(crop, x, y)
c2 = house(30, 36, 37, 2, 3, 'orange', 'plaster', 33, win_tiles=(WIN, WIN_FLOWER_G))
m.put(31, 38, CHIMNEY_A)
for x, t in ((35, P['mens_clothes']), (36, P['robe_b'])): m.put(x, c2 + 1, t); taken.add((x, c2 + 1))
c3 = house(3, 9, 40, 2, 3, 'red', 'brick', 6, win_tiles=(WIN, WIN_FLOWER_P))
m.put(4, 41, CHIMNEY_A)
c4 = house(42, 48, 39, 2, 3, 'green', 'tudor', 46, win_tiles=(WIN_FLOWER_G, WIN))
m.put(47, 40, CHIMNEY_A)
c5 = house(16, 21, 42, 2, 2, 'thatch', 'wood', 18, win_tiles=(WIN,))
m.put(17, 43, CHIMNEY_A)
ext_obj('log_pile', 13, c3 - 1); ext_obj('axe_stump', 22, c5)
for x, y in ((14, c1 + 1), (29, c2 + 1)): m.put(x, y, FIREWOOD); taken.add((x, y))
# the pond between the east cottages
m.rect(37, 42, 40, 44, WATER)
keep_rect(36, 41, 41, 45); taken.update((x, y) for x in range(37, 41) for y in range(42, 45))
ext_obj('fern', 36, 43); ext_obj('rock', 41, 44)
# the children's swing under a big oak by the south path
ext_obj('big_oak', 30, 43); ext_obj('swing', 33, 44)
keep_rect(29, 42, 35, 47)

# ---------------------------------------------------------------- lone trees in the open
for name, x, y in (('leafy_tree', 17, 22), ('round_tree', 34, 22), ('park_tree', 50, 31), ('leafy_tree2', 1, 27),
                   ('park_tree', 22, 23), ('leafy_tree', 37, 31)):
    ext_obj(name, x, y); keep_rect(x, y, x + 1, y + 2)


# ---------------------------------------------------------------- the woods: everything outside the village's clearing
def edge_l(y): return 1 + int(1.6 * (1 + math.sin(y * 0.55)))
def edge_r(y): return W - 3 - int(1.6 * (1 + math.sin(y * 0.45 + 2)))
def edge_b(x): return H - 3 - int(1.3 * (1 + math.sin(x * 0.5)))


def wooded(x, y):
    if (x, y) in keep: return False
    if y <= 17: return x < CX0 or x > CX1
    if y <= ROAD_Y[1]: return x < CX0
    if SOUTH[0] <= x <= SOUTH[1] and y >= 40: return False
    return x < edge_l(y) or x > edge_r(y) or y > edge_b(x)


trunks, crowns = set(), set()
inside = lambda x, y: 0 <= x < W and 0 <= y < H


def fits(x, y):
    for dx in (0, 1):
        tx, ty = x + dx, y + 1
        if inside(tx, ty) and (not wooded(tx, ty) or (tx, ty) in trunks or (tx, ty) in taken): return False
        if inside(tx, y) and ((tx, y) in crowns or (tx, y) in taken or (tx, y) in paths): return False
    return any(inside(x + dx, y + dy) for dx in (0, 1) for dy in (0, 1))


def plant(x, y):
    (a, b), (c, d) = rnd.choices(WOOD_TREES, WOOD_WEIGHTS)[0]
    for dx, top, bottom in ((0, a, c), (1, b, d)):
        if inside(x + dx, y): m.put(x + dx, y, top, 3); crowns.add((x + dx, y))
        if inside(x + dx, y + 1): m.put(x + dx, y + 1, bottom, 2); trunks.add((x + dx, y + 1))


for y in range(-1, H, 2):
    for x in range(((y + 1) // 2) % 2 - 1, W, 2):
        if fits(x, y): plant(x, y)
for y in range(H):
    for x in range(W):
        if wooded(x, y) and (x, y) not in trunks and (x, y) not in crowns:
            for tx, ty in ((x - 1, y - 1), (x, y - 1), (x - 1, y), (x, y)):
                if fits(tx, ty): plant(tx, ty); break
for y in range(H):
    for x in range(W):
        if wooded(x, y) and (x, y) not in trunks and (x, y) not in taken:
            m.put(x, y, BLOCKER)                                    # under the crowns: no walking through the wood

# ---------------------------------------------------------------- undergrowth and small things in the open grass
for y in range(21, H):
    for x in range(W):
        if wooded(x, y) or (x, y) in paths or (x, y) in taken or (x, y) in crowns or m.get(x, y) != GRASS: continue
        near_wood = any(inside(x + dx, y + dy) and wooded(x + dx, y + dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1))
        r = rnd.random()
        if near_wood and r < 0.16: ext_obj(rnd.choice(('bush', 'bush2', 'rock', 'pebbles')), x, y)
        elif r < 0.07: m.put(x, y, rnd.choice(GRASS_TUFTS)); taken.add((x, y))
        elif r < 0.10: m.put(x, y, rnd.choice(FLOWERS)); taken.add((x, y))
for name, x, y in (('pink_flowers', 2, 34), ('mushrooms', 48, 45), ('stump_big', 50, 21), ('fern', 3, 45),
                   ('pink_flowers', 34, 45)):
    ext_obj(name, x, y)

# ---------------------------------------------------------------- events
m.door('Royal Magic Academy', GX, 10, *K.ARRIVE['hall_from_academy'][:3], style=2)
m.door('The Inkpot Inn', 10, inn, *K.ARRIVE['inn_from_village'][:3])
m.door('Moonwell Apothecary', 40, apo, *K.ARRIVE['apothecary_from_village'][:3], style=1)
m.exit('To the coast road', [(W - 1, y) for y in range(ROAD_Y[0], ROAD_Y[1] + 1)], *K.ARRIVE['world_from_academy_east'])
m.exit('To the plains', [(x, H - 1) for x in range(SOUTH[0], SOUTH[1] + 1) if not wooded(x, H - 1)],
       *K.ARRIVE['world_from_academy_south'])
for x in (GX - 2, GX + 2): m.obj('Brazier', x, 11, '!Other2', 7, None, step=True)
m.sign('Signpost', GX + 4, 21, ['\\C[6]Quillhaven\\C[0] - Royal Magic Academy of Nova', 'East: the coast road, south to the Royal Capital.'])
m.sign('Notice Board', 22, 30, ['\\C[6]Notice Board\\C[0]', '"Rooms for students\' families - ask at the Inkpot."',
       '"LOST: one familiar (toad). Answers to Bartholomew."', '"Fresh eggs daily - knock at the coop, not the hens."'])
m.locked_door('Quill & Candle', 44, books, ['\\C[6]QUILL & CANDLE - Books, ink and spell paper\\C[0]',
              '"Closed for stocktaking. Back tomorrow."'], style=1)
m.locked_door('Cottage', 16, c1, ['A student\'s mother answers through the door:', '"If you\'re selling charms, we have plenty!"'])
m.locked_door('Cottage', 33, c2, ['The door is locked. Someone inside is practising', 'a spell... badly. Something just popped.'], style=1)
m.locked_door('Cottage', 6, c3, ['The door is locked. It smells of fresh bread.'])
m.locked_door('Cottage', 46, c4, ['An old voice: "The door\'s stuck again. Come back later."'], style=1)
m.locked_door('Cottage', 18, c5, ['A note on the door: "Gone to the Academy to lecture. Feed the cat."'])
m.sign('Chicken Coop', 5, coop, ['The coop smells of straw and indignation.'])

m.npc('Academy Sentinel', GX + 1, 12, 'People2', 2, ('Academy Sentinel:', 'The Royal Magic Academy of Nova.',
      'Visitors may see the Great Hall and the Cloister Court.', 'The dormitories are for students only.'), direction=2)
m.npc('Student', 22, 16, 'Actor2', 5, ('Student:', 'Third-year exams start next week.', 'If I fail Wards again, my mother will turn me into a toad.',
      '...She can, you know. She graduated top of her year.'), direction=2)
m.npc('Student', 33, 14, 'Actor3', 7, ('Student:', 'I keep counting the windows on the east wing.', 'Thirteen from outside. Twelve from inside.',
      'Nobody will tell me why.'), direction=8)
m.npc('Student', 16, 19, 'Actor2', 4, ('Student:', 'Graduates leave as Class 5, or Class 4 if the', 'examiners like you. Then it\'s missions and more exams.'),
      route=wander_route('RRRRWLLLLW'), speed=3)
m.npc('Old Scholar', SQUARE[0] - 2, SQUARE[1], 'People4', 6, ('Old Scholar:', 'Forty years I taught Runes up there.',
      'Now I sit by this well and correct the children\'s spelling.', 'The runes, I mean. Their spelling is hopeless too.'), direction=6)
m.npc('Pedlar', 32, 30, 'People3', 5, ('Pedlar:', 'Quills, candle-ends, lucky beetles!', 'The students buy anything before an exam.'), direction=2)
m.npc('Hen-wife Bess', 12, 33, 'People1', 7, ('Hen-wife Bess:', 'The Academy kitchens take every egg I have.',
      'Something about a professor who eats nine a day.', 'Nine! I don\'t ask.'), direction=4)
m.npc('Farmer', 49, 29, 'People3', 4, ('Farmer:', 'The apothecary buys my mandrakes. Ten silver a root.', 'Earplugs are extra.'), direction=8)
m.npc('Child', 33, 46, 'People1', 0, ('Child:', 'When I grow up I\'ll go to the Academy', 'and make the carrots dance!'), move=1, freq=5, speed=4)
m.npc('Child', 29, 37, 'People2', 0, ('Child:', 'Tag! You\'re it!'), move=1, freq=5, speed=4)
m.npc('Washerwoman', 34, c2 + 1, 'People1', 4, ('Washerwoman:', 'Robes, robes and more robes.', 'Do you know how hard it is to get scorch marks out of velvet?'), direction=2)
for i, (x, y) in enumerate(((5, 35), (7, 36), (9, 34))):
    m.critter('Hen', x, y, 'Nature', 2, None, ('The hen eyes you suspiciously.', 'Cluck.', 'The hen pecks at your boot.')[i],
              move=1, freq=4, area=(PEN[0] + 1, PEN[1] + 3, PEN[2] - 1, PEN[3] - 1))
m.critter('Stray Cat', 36, 45, 'Nature', 1, 'Cat', 'The cat is watching the pond. Possibly for Bartholomew.', move=1)

from academy_sprites import recast
recast(m.events)                                # the Academy's students and sentinel in uniform

if __name__ == '__main__':
    out = next((a for a in sys.argv[1:] if not a.startswith('--')), None)
    if out: m.render(out, scale=0.5, grid='--grid' in sys.argv)
    if '--save' in sys.argv:
        m.save(K.ACADEMY, parent_id=K.WORLD, order=K.ACADEMY)
        print('saved Map%03d' % K.ACADEMY)
