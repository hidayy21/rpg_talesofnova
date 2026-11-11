# MAP065 - Lilydale (chapter 7): an old half-timbered town packed into a clearing of the woods, the last place before
# Hollow Wood and the misty wood that hides Villa Bloodrose. The party arrives here first. The village knew the
# Bloodroses well once: David came to play here as a boy (the elders were those children), and his wife was one of the
# village's own. Since she died in the war sixteen years ago only the villa's servants come, on market days, for flour
# and lamp oil - and for three weeks not even they have come.
# Laid out like an old town (FF6's Nikeah / Albrook, the user's sketch): stone underfoot everywhere, tall gabled houses
# shoulder to shoulder in blocks between narrow lanes, the road from the north running down into Rose Square and out
# of the south side. Little green: the rose tree's bed, a yard or two, the lily pond, the orchard, the woods round it.
#   - Rose Square: the old rose-coloured tree (a cutting of the Bloodrose tree - "the boy who always waited under the
#     rose tree"), the well, market stalls - one of them empty: it was the villa's flour stall
#   - doors that open (map_lilydale_interiors.py): the Lantern & Lily (tavern below, inn rooms upstairs), the chapel
#     under its tower, Thistle & Wick General Goods (items only), and the three elders' houses. Every other door is
#     latched, each with its own line.
#   - road north (top) into Hollow Wood; road south (bottom) out of the valley (no World Map link yet)
# Tileset 21 "Medieval Town" (make_medieval_tileset.py). The named buildings are placed by hand; `pack` fills the rest
# of each block with houses of mixed width, height, roof and wall (seeded, so the layout is fixed). The woods round
# the edge come from rm-map-forge (forge_outdoor.js, trees only).
#   python3 map_lilydale.py preview.png [--grid] [--full]   -> preview image
#   python3 map_lilydale.py --save                          -> write Map065 (editor must be closed)
import sys, os, math, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import nova_maplib as L
from nova_maplib import page, cmd, text, char
from town_kit import *
import kingdom as K
from forge_outdoor import forge, Tree, A2, BLOCKER
from make_medieval_tileset import MED_GROUND, MED_ROOF, MED_WALL

W, H = 50, 45
TILESET = 21
PF = lambda n: L.ext('PM_Forest', n)
PM = lambda n: L.ext('PM_Market', n)
MV = lambda n: 768 + n                                           # MedievalVillage_B, slot E of tileset 21
AV = lambda n: L.ext('Avy_Town_B', n)
AV3 = lambda n: L.ext('Avy_Town_B3', n)
GOTHIC = (67, 75)                                                # Avy_Town_B3: a pointed window, two tiles tall
STAINED_GLASS = [(192, 200), (193, 201), (194, 202), (195, 203)]   # Avy_Town_B3: stained glass, two tiles tall
BENCH = ((102, 103), (110, 111))                                 # Avy_Town_B: a white bench, 2x2
FLOWER_POTS = (58, 59, 63, 71, 87)                               # Avy_Town_B
ROSE_TREE = [(200, 201, 202, 203, 204), (208, 209, 210, 211, 212), (216, 217, 218, 219, 220),
             (224, 225, 226, 227, 228), (232, 233, 234, 235, 236), (240, 241, 242, 243, 244),
             (248, 249, 250, 251, 252)]                          # PM_Forest, 5x7 (the villa garden has its parent)
LILIES = (PF(9), PF(10))                                         # white lilies standing in water
SQUARE_STONE, LANE_STONE = COBBLE_B, ('A2', MED_GROUND['cobble'])

# MedievalVillage_B pieces
GABLE = {'shingle': [(None, None, 130, None, None), (None, 137, 138, 139, None), (144, 145, 146, 147, 148),
                     (152, 153, 154, 155, 156), (160, 161, 162, 163, 164)],
         'slate': [(None, None, 170, None, None), (None, 177, 178, 179, None), (184, 185, 186, 187, 188),
                   (192, 193, 194, 195, 196), (200, 201, 202, 203, 204)]}
DORMER = {'shingle': 133, 'slate': 141}
M_CHIMNEY = {'brick': (149, 157), 'stone': (181, 189)}
M_WIN = {'small': (9, 17), 'wide': (10, 18), 'tall': (11, 19), 'flowers': (12, 20), 'arched': (13, 21)}
M_DOOR = {'wood': (14, 22), 'arched': (15, 23)}
M_BARREL, M_CRATE = 1, 2
M_CART = (3, 4, 5)
M_BUNTING = (6, 7)
M_CRATES = ((28, 29), (36, 37))
STALL = {'red': ((42, 43, 44), (50, 51, 52), (58, 59, 60), (66, 67, 68)),       # PM_Market: awning, shade, counter
         'green': ((45, 46, 47), (53, 54, 55), (61, 62, 63), (69, 70, 71))}
FLOWER_CART = ((56, 57), (64, 65))

NORTH_X, SOUTH_X = (25, 26), (24, 25)                            # road lanes at the top and bottom edges
NORTH_ROAD = (24, 4, 27, 16)                                     # x0, y0, x1, y1
SQUARE = (18, 17, 33, 27)
SOUTH_ST = (23, 28, 26, 42)
LANES = [(2, 9, 11, 10), (11, 9, 11, 16), (2, 17, 47, 18), (42, 9, 47, 10), (42, 9, 42, 16),
         (2, 26, 47, 27), (2, 35, 47, 36), (2, 42, 47, 42)]
# blocks of houses: (x0, x1, bottom = the street-level wall row, highest top)
BLOCKS = {'W1': (2, 10, 8, 2), 'W2': (2, 10, 16, 11), 'E1': (43, 47, 8, 2), 'E2': (43, 47, 16, 11),
          'W3': (2, 17, 25, 19), 'E3': (34, 47, 25, 19), 'W4': (2, 22, 34, 28), 'E4': (27, 47, 34, 28),
          'W5': (11, 22, 41, 37), 'E5': (27, 39, 41, 37)}
POND = (3, 37, 9, 41)
ORCHARD = (40, 37, 47, 41)


def in_town(x, y):
    """Inside the town (stone and houses); outside is the wood. Ragged corners, the two roads out."""
    if x in NORTH_X and y <= 3 or x in SOUTH_X and y >= 43: return True
    if not (2 <= x <= 47 and 2 <= y <= 42): return False
    if 11 <= x <= 23 and y <= 6 or 34 <= x <= 41 and y <= 4: return False     # the wood behind the inn and chapel
    cx, cy = min(x - 2, 47 - x), min(y - 2, 42 - y)
    return cx + cy >= 2 or ((x * 7 + y * 3) % 5 == 0 and cx + cy >= 1)


GREEN = [Tree([(16, 17, 18), (24, 25, 26), (32, 33, 34)], 0.30, None, 'PM_Forest'),
         Tree([(40, 41, 42), (48, 49, 50), (56, 57, 58)], 0.25, None, 'PM_Forest'),
         Tree([(112, 113), (120, 121)], 0.25, None, 'PM_Forest'),
         Tree([(114, 115), (122, 123)], 0.22, None, 'PM_Forest'),
         Tree(BIG_TREE, 0.15),
         Tree([(BUSH_S,)], 0.05)]
KEEP = [(x, y) for y in range(H) for x in range(W) if in_town(x, y)]
m = forge(K.NAMES[K.LILYDALE], W, H, seed='lilydale-3', ground=A2(0), road=A2(1), paths=[], keep=KEEP, trees=GREEN,
          params={'hills': 0, 'scale': 16}, tileset=TILESET)
m.note = '<outdoor>'
m.bgm = {'name': 'Town2', 'pan': 0, 'pitch': 95, 'volume': 70}
m.bgs = {'name': 'Wind', 'pan': 0, 'pitch': 100, 'volume': 15}
rnd = random.Random(65)
KEEP_SET = set(KEEP)
m.rect(0, 0, W - 1, H - 1, GRASS)                                # the wood's floor...
for (x, y) in KEEP_SET: m.cell(x, y, LANE_STONE)                 # ...and stone everywhere in town
taken = set()


def claim(x0, y0, x1, y1): taken.update((x, y) for x in range(x0, x1 + 1) for y in range(y0, y1 + 1))


def free(x, y): return (x, y) not in taken and (x, y) in KEEP_SET and not m.has_object(x, y)


# gaps in the wood that no whole tree fitted into stay closed
for y in range(H):
    for x in range(W):
        if (x, y) not in KEEP_SET and not m.has_object(x, y):
            m.put(x, y, BLOCKER)
            if rnd.random() < 0.5: m.put(x, y, rnd.choice((BUSH_S, FERN, TREE_S1)), 3)
for x in range(W):                                               # the edge rows stay shut beside the roads
    for y, lanes in ((0, NORTH_X), (H - 1, SOUTH_X)):
        if x not in lanes and (x, y) not in KEEP_SET and not m.base[2 * W * H + y * W + x]: m.put(x, y, BLOCKER)

# ---------------------------------------------------------------- the main ways: warm cobbles; lanes: rough stone
m.rect(NORTH_X[0], 0, NORTH_X[1], 3, DIRT)
m.rect(*NORTH_ROAD, SQUARE_STONE)
m.rect(*SQUARE, SQUARE_STONE)
m.rect(*SOUTH_ST, SQUARE_STONE)
m.rect(SOUTH_X[0], 43, SOUTH_X[1], 44, DIRT)
STREETS = set()
for x0, y0, x1, y1 in [NORTH_ROAD, SQUARE, SOUTH_ST] + LANES:
    STREETS.update((x, y) for x in range(x0, x1 + 1) for y in range(y0, y1 + 1))

# ---------------------------------------------------------------- the buildings everyone knows (doors that open)
# name: x0, x1, top, roof rows, walls [(kind, rows) top to bottom], roof, door x, + extras. `enter`: the ARRIVE key
# of the room behind the door.
FIXED = [
    dict(name='Lantern & Lily', x0=12, x1=22, top=8, roof_rows=4, walls=[('timber', 3), ('timber_brick', 2)],
         roof='shingle', door=17, wins=('flowers', 'wide'), gables=(12, 18), signs=('inn', 'pub'),
         chimney=(14, 'brick'), enter='lily_tavern_from_town'),
    dict(name='Chapel', x0=29, x1=33, top=4, roof_rows=3, walls=[('rubble', 10)], roof='slate', door=31,
         wins=('arched',), high_wins=(8, 12), enter='lily_chapel_from_town', door_style=2),
    dict(name='Chapel Nave', x0=34, x1=41, top=6, roof_rows=4, walls=[('ashlar', 7)], roof='slate', door=None,
         chapel=True),
    dict(name='Thistle & Wick', block='E3', x0=35, x1=41, top=20, roof_rows=3, walls=[('timber_brick', 3)],
         roof='umber', door=38, wins=('wide', 'flowers'), signs=('item',), chimney=(40, 'brick'),
         enter='lily_store_from_town'),
    dict(name='Old Henrik\'s House', block='W1', x0=3, x1=8, top=3, roof_rows=3, walls=[('tudor', 3)], roof='red',
         door=5, wins=('small', 'flowers'), chimney=(7, 'brick'), enter='lily_henrik_from_town'),
    dict(name='Old Marta\'s House', block='W3', x0=11, x1=16, top=19, roof_rows=3, walls=[('daub', 4)],
         roof='shingle', door=13, wins=('flowers',), gables=(11,), enter='lily_marta_from_town'),
    dict(name='Old Bram\'s House', block='W4', x0=3, x1=9, top=29, roof_rows=3, walls=[('timber', 3)], roof='thatch',
         door=6, wins=('small',), chimney=(8, 'stone'), enter='lily_bram_from_town'),
]

# ---------------------------------------------------------------- houses
STYLES = [('shingle', 'timber'), ('slate', 'timber'), ('shingle', 'timber_brick'), ('slate', 'ashlar'),
          ('red', 'tudor'), ('orange', 'plaster'), ('terracotta', 'daub'), ('umber', 'timber_brick'),
          ('slate', 'daub'), ('shingle', 'daub'), ('moss', 'rubble'), ('slate', 'rubble'), ('red', 'timber'),
          ('indigo', 'timber'), ('shingle', 'plaster'), ('blue', 'tudor')]
LOWER = {'timber': 'timber_brick', 'daub': 'rubble', 'plaster': 'ashlar', 'tudor': 'brick'}
WINS = [('small', 'flowers'), ('wide',), ('tall', 'flowers'), ('wide', 'small'), ('flowers',), ('tall',)]


def pack_span(block, x0, x1, prev=None):
    """Fill x0..x1 of a block with houses of mixed widths and heights, shoulder to shoulder (now and then an alley)."""
    _, _, bottom, top_min = BLOCKS[block]
    x, out = x0, []
    while x1 - x + 1 >= 4:
        rem = x1 - x + 1
        w = min(rnd.choice((4, 5, 5, 6, 6, 7, 8, 9)), rem)
        if rem - w < 4: w = rem if rem <= 10 else rem - 5
        style = rnd.choice([s for s in STYLES if not prev or (s[0] != prev[0] and s[1] != prev[1])])
        prev = style
        room = bottom - top_min + 1
        roof_rows = rnd.choice((2, 3, 3, 4)) if room >= 6 else 2
        wall_rows = max(3, min(5, room - roof_rows - rnd.choice((0, 0, 0, 1))))   # tall: the block's full height
        while roof_rows + wall_rows > room:
            if wall_rows > 3: wall_rows -= 1
            else: roof_rows -= 1
        roof, wall = style
        walls = [(wall, wall_rows)]
        if wall_rows == 5 and wall in LOWER and rnd.random() < 0.6: walls = [(wall, 3), (LOWER[wall], 2)]
        h = dict(block=block, x0=x, x1=x + w - 1, top=bottom - roof_rows - wall_rows + 1, roof_rows=roof_rows,
                 walls=walls, roof=roof, door=x + w // 2 - (1 if rnd.random() < 0.4 and w > 5 else 0),
                 wins=rnd.choice(WINS))
        if roof in ('shingle', 'slate') and w >= 5 and roof_rows >= 3 and rnd.random() < 0.8:
            h['gables'] = (x + (w - 5) // 2,) if w < 10 else (x, x + w - 5)
        elif rnd.random() < 0.7:
            h['chimney'] = (x + rnd.choice((1, w - 2)), rnd.choice(('brick', 'stone')))
            if roof in ('shingle', 'slate') and w >= 5: h['dormers'] = (x + w // 2,)
        out.append(h)
        x += w
        if x1 - x + 1 >= 6 and rnd.random() < 0.3: x += 1     # an alley
    return out


def house(h):
    x0, x1, top, roof_rows, roof = h['x0'], h['x1'], h['top'], h['roof_rows'], h['roof']
    rt_y = top + roof_rows - 1
    m.rect(x0, top, x1, rt_y, ('A3', MED_ROOF[roof]))
    y = rt_y + 1
    for wall, n in h['walls']:
        m.rect(x0, y, x1, y + n - 1, ('A3', MED_WALL[wall])); y += n
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
        if (cx, top) not in covered and (cx, top - 1) not in covered and not m.top[1][top - 1][cx]:
            m.put(cx, top - 1, MV(M_CHIMNEY[kind][0]), 3); m.put(cx, top, MV(M_CHIMNEY[kind][1]))
    door = h['door']
    if h.get('chapel'):                                          # stained glass above, pointed windows below
        for k, x in enumerate(range(x0 + 1, x1, 2)):
            a, b = STAINED_GLASS[k % 4]
            m.put(x, rt_y + 2, AV3(a)); m.put(x, rt_y + 3, AV3(b))
            m.put(x, bottom - 1, AV3(GOTHIC[0])); m.put(x, bottom, AV3(GOTHIC[1]))
    else:
        wins = [M_WIN[w] for w in h['wins']]
        for i, wy in enumerate(range(bottom - 1, rt_y, -3)):
            for k, x in enumerate(range(x0 + 1, x1, 2)):
                if wy == bottom - 1 and abs(x - door) <= 1: continue
                a, b = wins[(i + k) % len(wins)]
                m.put(x, wy, MV(a)); m.put(x, wy + 1, MV(b))
    for wy in h.get('high_wins', ()):
        for x in (door - 1, door + 1) if wy == h['high_wins'][0] else (door,):
            m.put(x, wy, AV3(GOTHIC[0])); m.put(x, wy + 1, AV3(GOTHIC[1]))
    if door is not None and not h.get('enter'):
        d_top, d_bot = M_DOOR['wood']
        m.put(door, bottom - 1, MV(d_top)); m.put(door, bottom, MV(d_bot))
    for i, s in enumerate(h.get('signs', ())):
        m.put(door + (1, -1)[i], bottom - 2 if bottom - 2 > rt_y else bottom - 1, SIGN[s])
    return bottom


HOUSES = list(FIXED)
for b, (bx0, bx1, _, _) in BLOCKS.items():
    fixed = sorted((h for h in FIXED if h.get('block') == b), key=lambda h: h['x0'])
    x, prev = bx0, None
    for f in fixed + [None]:
        end = (f['x0'] - 1) if f else bx1
        HOUSES += pack_span(b, x, end, prev)
        if f:
            HOUSES.append(HOUSES.pop(HOUSES.index(f)))
            x = f['x1'] + 1
for h in HOUSES: house(h)
# the chapel tower's spire (Avy_Town_B3, 3x7), the cross on top, standing on the tower roof
for r, row in enumerate([(128, 129, 130), (136, 137, 138), (144, 145, 146), (152, 153, 154), (160, 161, 162),
                         (168, 169, 170), (176, 177, 178)]):
    for c, t in enumerate(row): m.put(30 + c, r, L.ext('Avy_Town_B3', t), 3)

# names and door lines for some of the houses (by block, left to right among the packed ones)
NAMED = {('E3', 1): ('Bakery', ['The ovens are cold.', 'A slate on the door: "NO FLOUR. Ask at the villa."',
                                'Someone has rubbed out "Ask at the villa" with a thumb.'], ('eatery',)),
         ('E4', 1): ('Weaver\'s House', ['A loom clacks inside, then stops.', 'Nobody comes to the door.']),
         ('W2', 0): ('Tailor', ['Pinned to the door: "Mending only. No cloth till the cart comes."'], ('armor',)),
         ('E4', 0): ('Chandler', ['"No lamp oil," says the sign. It has been underlined twice.'], ('magic',))}
DOOR_LINES = [['Nobody answers.'], ['The door is locked.'], ['A dog barks behind the door. Nobody comes.'],
              ['Someone inside says, "Not today, thank you."'], ['The door is barred.'],
              ['Through the shutters: a family at supper. Better not.'], ['Locked.'],
              ['A child peeks out of the window above, then ducks away.'],
              ['A woman\'s voice: "If you\'re selling something, we\'ve no coin."']]
by_block = {}
for h in HOUSES:
    if 'block' in h and not h.get('enter'): by_block.setdefault(h['block'], []).append(h)
for (b, i), spec in NAMED.items():
    if i < len(by_block.get(b, [])):
        h = by_block[b][i]
        h['name'], h['lines'] = spec[0], spec[1]
        for k, s in enumerate(spec[2] if len(spec) > 2 else ()):
            m.put(h['door'] + (1, -1)[k], h['bottom'] - 1, SIGN[s])
n = 0
for h in HOUSES:
    if h.get('enter') or 'block' not in h or 'name' in h: continue
    n += 1; h['name'], h['lines'] = 'House %d' % n, DOOR_LINES[n % len(DOOR_LINES)]
DOORS = {h['name']: (h['door'], h['bottom']) for h in HOUSES if h['door'] is not None}

# ---------------------------------------------------------------- the edges: the pond, the orchard, little yards
px0, py0, px1, py1 = POND
m.rect(px0 - 1, py0 - 1, px1 + 1, py1, GRASS); m.rect(px0, py0, px1, py1 - 1, WATER); claim(px0 - 1, py0 - 1, px1 + 1, py1)
for x, y in ((4, 37), (6, 38), (8, 37), (5, 39), (7, 39)): m.put(x, y, LILIES[(x + y) % 2])
for x in (px0 - 1, px1 + 1): m.put(x, py0, FLOWER_BUSH)
m.put(px0 + 1, py1, rnd.choice(FLOWERS)); m.put(px0 + 5, py1, rnd.choice(FLOWERS))
ox0, oy0, ox1, oy1 = ORCHARD
m.rect(ox0, oy0, ox1, oy1, GRASS); claim(ox0, oy0, ox1, oy1)
for x, y in ((40, 37), (44, 37), (42, 39)):
    for r, row in enumerate([(16, 17, 18), (24, 25, 26), (32, 33, 34)]):
        for c, t in enumerate(row):
            if x + c <= ox1 and y + r <= oy1: m.put(x + c, y + r, PF(t), 3 if r < 2 else 2)
covered_x = {b: set() for b in BLOCKS}
for h in HOUSES:
    if h.get('block'): covered_x[h['block']].update(range(h['x0'], h['x1'] + 1))
for b, (x0, x1, bottom, top_min) in BLOCKS.items():              # what the packer left at the end of a block: a yard
    for x in range(x0, x1 + 1):
        if x in covered_x[b]: continue
        for y in range(top_min, bottom + 1):
            if (x, y) in STREETS or (x, y) in taken: continue
            m.cell(x, y, GRASS); claim(x, y, x, y)
            r = rnd.random()
            if y == bottom: m.put(x, y, MV(M_BARREL) if r < 0.5 else FLOWER_BUSH)
            elif r < 0.35: m.put(x, y, rnd.choice(FLOWERS + (BUSH_S, FLOWER_BUSH)))

# ---------------------------------------------------------------- Rose Square
RX, RY = 19, 23                                                  # the rose tree's trunk row starts at (RX, RY)
m.rect(RX - 1, RY - 1, RX + 5, RY + 1, GRASS)
for r, row in enumerate(ROSE_TREE):
    for c, t in enumerate(row):
        m.put(RX + c, RY - 6 + r, PF(t), 2 if r == 6 else 3)
claim(RX - 1, RY - 6, RX + 5, RY + 1)
for x in (RX - 1, RX + 5): m.put(x, RY + 1, FLOWER_BUSH)
for x in (RX, RX + 1, RX + 3, RX + 4): m.put(x, RY + 1, FLOWERS[x % 4])
WELL_AT = (26, 22)
m.put(*WELL_AT, WELL); m.put(27, 23, BUCKET); claim(26, 22, 27, 23)
NOTICE_AT = (28, 18)
m.put(*NOTICE_AT, NOTICE_BOARD); claim(*NOTICE_AT, *NOTICE_AT)


def stall(x, y, colour, goods):
    for r, row in enumerate(STALL[colour]):
        for c, t in enumerate(row): m.put(x + c, y + r, PM(t), 3 if r < 2 else 2)
    for c, g in enumerate(goods):
        if g is not None: m.put(x + c, y + 2, PM(g), 3)
    claim(x, y, x + 2, y + 3)


stall(29, 19, 'red', (16, 24, 32))                               # the greengrocer's, still trading
stall(29, 23, 'green', (None, None, None))                       # empty: it was the villa's flour stall
m.put(32, 21, PM(48)); m.put(32, 22, PM(40)); m.put(28, 27, MV(M_BARREL)); claim(32, 21, 32, 22); claim(28, 27, 28, 27)
for c in range(2): m.put(20 + c, 26, AV(BENCH[0][c]))             # a bench by the rose tree
claim(20, 26, 21, 26)
for x, y in ((12, 17), (22, 17), (29, 17), (33, 17)):            # flower pots by the inn and the chapel doors
    if free(x, y): m.put(x, y, AV(FLOWER_POTS[(x + y) % 5])); claim(x, y, x, y)
m.put(18, 26, PM(FLOWER_CART[0][0]), 3); m.put(18, 27, PM(FLOWER_CART[1][0])); claim(18, 26, 18, 27)
for x in range(SQUARE[0], SQUARE[2] + 1):                        # bunting over the square's top row
    if not m.top[1][SQUARE[1]][x] and not NORTH_ROAD[0] <= x <= NORTH_ROAD[2]:
        m.put(x, SQUARE[1], MV(M_BUNTING[x % 2]), 3)
for y in (7, 11, 15):                                            # and across the north road
    for x in range(NORTH_ROAD[0], NORTH_ROAD[2] + 1): m.put(x, y, MV(M_BUNTING[x % 2]), 3)

STEPS = {(h['door'], h['bottom']) for h in HOUSES if h['door'] is not None}     # nothing goes on a doorstep
taken.update((x, y + 1) for x, y in STEPS)
# lamp posts at the corners and along the main ways
for x, y in ((23, 9), (28, 9), (23, 14), (28, 14), (33, 20), (22, 30), (27, 30), (22, 39), (27, 39),
             (2, 18), (47, 18), (10, 27), (42, 27), (10, 36), (38, 36), (2, 36)):
    if all(free(x, y - d) for d in range(3)): m.lamp(x, y); claim(x, y - 2, x, y)
# street clutter: barrels and crates against the walls, a cart
for x, y, t in ((23, 11, MV(M_BARREL)), (23, 12, MV(M_CRATE)), (28, 11, MV(M_CRATE)), (11, 15, MV(M_BARREL)),
                (43, 17, MV(M_BARREL)), (46, 26, CRATE_APPLE), (47, 26, CRATE_CARROT), (21, 35, MV(M_CRATE)),
                (13, 42, MV(M_BARREL)), (36, 42, MV(M_CRATE))):
    if free(x, y) and (x, y - 1) not in STEPS: m.put(x, y, t); claim(x, y, x, y)
if all(free(x, 36) for x in (30, 31, 32)):
    for c, t in enumerate(M_CART): m.put(30 + c, 36, MV(t))
    claim(30, 36, 32, 36)

# ---------------------------------------------------------------- doors
for h in HOUSES:
    if h['door'] is None: continue
    x, y = h['door'], h['bottom']
    if h.get('enter'):
        a = K.ARRIVE[h['enter']]
        m.door(h['name'], x, y, a[0], a[1], a[2], style=h.get('door_style', 0))
    else:
        m.add_event(h['name'], x, y, [page(None, priority=1, commands=text(*h['lines']))])

# ---------------------------------------------------------------- signs and the square
m.put(22, 41, SIGNPOST); m.sign('Signpost', 22, 41, ['\\C[6]Lilydale\\C[0]', 'North: Hollow Wood.'])
m.put(27, 3, SIGNPOST); m.sign('Signpost', 27, 3, ['North: Hollow Wood, then Mistveil.',
                                                  'Carved under it, very old: a small rose.'])
m.sign('Notice Board', *NOTICE_AT, ['MARKET DAY - every seventh day, in Rose Square.',
                                    'Pinned below, newer: "Has anyone seen Hanna from the villa?"'])
m.sign('Old Well', *WELL_AT, ['The stones are worn smooth where a hundred years of hands have rested.'])
m.sign('Empty Stall', 30, 25, ['Flour dust in the cracks of the counter, and nothing else.',
                               'This was where the villa\'s cart unloaded.'])
m.add_event('Rose Tree', RX + 2, RY, [page(None, priority=1, commands=text(
    'An old tree with leaves the colour of wine.', 'Children have carved their names into the bark, low down.',
    'One name is carved higher than the others, as if by someone who never grew any taller.'))])
m.sign('Lily Pond', 6, 41, ['White lilies. The village was named for them, or they for the village -',
                           'nobody remembers which came first.'])

# ---------------------------------------------------------------- people (chapter 7, before the party sets out)
m.npc('Old Bram', RX + 2, RY + 2, 'People1', 6, ('Old Bram:', 'We used to play under this tree, the lot of us.',
      'Funny. I can\'t remember my own wedding, but I remember that.'), direction=8)
m.npc('Old Marta', 25, 23, 'People1', 7, ('Old Marta:', 'The villa folk always came on market day.',
      'Three weeks now. Not even Hanna with her basket.'), direction=6)
m.npc('Shepherd', 26, 6, 'People1', 2, ('Shepherd:', 'Two ewes dead in the north pasture. Not a mark on the wool.',
      'Folk say it\'s the villa. I say it\'s something out of that wood.'), move=1, freq=2)
m.npc('Young Mother', 18, 35, 'People1', 3, ('Young Mother:', 'The priest from the road says the house in the mist is cursed.',
      'My gran says it was the kindest house in the valley.'), move=1, freq=2)
m.npc('Tavern Regular', 14, 17, 'People4', 5, ('Tavern Regular:', 'Ale\'s gone thin since the villa stopped buying.',
      'Funny how a house nobody visits keeps a whole village fed.'), direction=2)
m.npc('Greengrocer', 32, 20, 'People2', 4, ('Greengrocer:', 'Apples, greens, the last of the oranges.',
      'Buy something, would you? Half the square\'s gone quiet.'), direction=4)
m.npc('Bell-Ringer', 30, 17, 'People4', 1, ('Bell-Ringer:', 'Every spring we ring the bell for the lady of the villa.',
      'She was born two lanes from here, you know. Married the quiet gentleman from the hill.'), direction=2)
m.npc('Boy', 24, 26, 'People1', 0, ('Boy:', 'Grandpa says a vampire used to give him sweets!', 'I think he\'s making it up.'),
      move=1, speed=4, freq=4)
m.npc('Girl', 8, 27, 'People2', 0, ('Girl:', 'Don\'t go in the wood. The mist eats sound.', 'Mama says so.'),
      move=1, speed=4, freq=4)
m.npc('Gardener', 11, 40, 'People4', 2, ('Gardener:', 'Lilies don\'t care who comes to market.',
      'Wish I could say the same for the rest of us.'), direction=4)
m.critter('Cat', 23, 25, 'Nature', 1, 'Cat', 'The cat stretches on the warm stones.', move=1, freq=2)

# ---------------------------------------------------------------- exits
for x in NORTH_X:
    m.add_event('To Hollow Wood %d' % x, x, 0, [L.exit_page(K.HOLLOW_WOOD, K.ARRIVE['hollow_from_lilydale'][1] + x - NORTH_X[0],
                                                             K.ARRIVE['hollow_from_lilydale'][2], 8)], note='<minimap: exit>')

ARRIVALS = [K.ARRIVE['lilydale_from_hollow'][1:3], (SOUTH_X[0], H - 2)]

if __name__ == '__main__':
    out = next((a for a in sys.argv[1:] if not a.startswith('--')), None)
    reach = m.reach([tuple(a) for a in ARRIVALS])
    bad = [n for n, (x, y) in DOORS.items() if (x, y + 1) not in reach]
    print('%d doors, %d houses' % (len(DOORS), len(HOUSES)), 'unreachable doors:', [(b, DOORS[b]) for b in bad] or 'none')
    for h in FIXED:
        if h.get('enter'):
            back = [k for k, v in K.ARRIVE.items() if k.startswith('lilydale_from_') and v[1:3] == (h['door'], h['bottom'] + 1)]
            print('%-22s door (%d,%d)' % (h['name'], h['door'], h['bottom']), 'arrival key:', back or 'MISSING')
    for e in m.events[1:]:
        if e['name'] in DOORS or e['name'].startswith('To '): continue
        if not any((e['x'] + dx, e['y'] + dy) in reach for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1), (0, 0))):
            print('unreachable', e['name'], e['x'], e['y'])
    if out: m.render(out, scale=0.5 if '--full' not in sys.argv else 1, grid='--grid' in sys.argv)
    if '--save' in sys.argv:
        m.save(K.LILYDALE, parent_id=K.WORLD)
        print('saved Map%03d' % K.LILYDALE)
