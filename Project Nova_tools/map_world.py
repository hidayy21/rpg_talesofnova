# MAP001 - World Map: the Western Continent, with the Royal Kingdom of Nova at the head of a bay on its east coast
# (Saltwind Harbor's pier runs out into it), and a small island alone off the south coast (kept free for a secret).
#   python map_world.py preview.png [--grid]   -> preview image
#   python map_world.py --save                 -> write Map001 + the city gates on Map004/Map005 (editor must be closed)
# Terrain is generated from fixed-seed noise plus hand-placed features (ridge, passes, lake, roads), so every run
# draws the same map. Encounters are per region: 1 Nova plains, 2 wilds, 3 wastes, 4 highlands, 5 snow, 6 shore.
import sys, math, json
import nova_maplib as L
from nova_maplib import page, cmd, text, char
import kingdom as K

W, H = 84, 84
OVERWORLD = 1

# ---------------------------------------------------------------- Overworld tileset (field type)
SEA, DEEP_SEA = ('A1', 0), ('A1', 1)
GRASS, WASTE, DESERT, SNOW = ('A2', 0), ('A2', 8), ('A2', 16), ('A2', 24)
FOREST, CONIFER, PALMS, SNOW_FOREST, DEAD_FOREST = ('A2', 4), ('A2', 5), ('A2', 20), ('A2', 28), ('A2', 12)
HILL, DIRT_HILL, SAND_HILL, SNOW_HILL = ('A2', 6), ('A2', 14), ('A2', 22), ('A2', 25)
MOUNTAIN, ROCK_MOUNTAIN, SAND_MOUNTAIN, SNOW_MOUNTAIN = ('A2', 7), ('A2', 15), ('A2', 23), ('A2', 31)
ROAD = ('A2', 13)
SIGNPOST, PIER, LIGHTHOUSE = 1, 2, 112                        # World_B
VILLAGE, VILLAGE_MIRROR, CASTLE = ((56, 57), (64, 65)), ((57, 56), (65, 64)), ((128, 129), (136, 137))

# The capital: a 6x2 footprint (west quarter, castle, east quarter), a strip of shore east of it, then the bay.
NX, NY = 60, 35
WEST_GATE, EAST_GATE = K.ARRIVE['residential_from_world'], K.ARRIVE['market_from_world']
assert K.ARRIVE['world_from_west_gate'][1:3] == (NX - 1, NY + 1) and K.ARRIVE['world_from_east_gate'][1:3] == (NX + 6, NY + 1)
NOVA_C = (NX + 2.5, NY + 0.5)

RIDGE = [(8, 22), (17, 18), (26, 21), (35, 17), (44, 20), (53, 16), (60, 20)]   # the mountain range across the north
PASSES = [(26, 21), (44, 20)]
LAKE = (19, 31, 3.4, 2.3)
SECRET_ISLE = (58, 77, 2.6)                       # x, y, radius - no encounters, nothing on it yet
ROADS = [[(NX - 1, NY + 1), (52, 37), (42, 41), (33, 44), (29, 45)],                          # west gate -> crossroads
         [(29, 45), (27, 38), (27, 30), (26, 22), (26, 12)],                                    # -> the north pass
         [(29, 45), (22, 47), (15, 50)],                                                        # -> the wastes
         [(NX + 6, NY + 1), (NX + 6, NY - 3), (65, 26), (62, 16)]]                              # east gate -> up the coast
SIGN_AT = (30, 44)

ENCOUNTERS = {1: [(2, 10), (5, 8), (6, 8), (1, 6), (7, 6), (8, 5), (9, 5)],
              2: [(7, 5), (8, 5), (9, 5), (10, 4), (11, 5), (12, 5), (13, 4), (18, 3)],
              3: [(19, 6), (17, 5), (18, 4), (3, 4), (23, 3), (26, 3)],
              4: [(22, 4), (23, 4), (24, 4), (28, 3), (29, 3), (30, 3), (32, 3)],
              5: [(33, 4), (34, 4), (35, 4), (30, 3), (31, 3), (37, 2)],
              6: [(15, 6), (16, 5), (2, 3)]}


# ---------------------------------------------------------------- noise
def _rand(seed, ix, iy):
    h = (ix * 73856093) ^ (iy * 19349663) ^ (seed * 83492791)
    h = (h ^ (h >> 13)) * 1274126177 & 0xffffffff
    return ((h ^ (h >> 16)) & 0xffff) / 65535.0


def _value(seed, x, y, cell):
    ang = seed * 2.399                       # each layer on its own rotated grid, so no straight grid-aligned edges
    x, y = x * math.cos(ang) - y * math.sin(ang), x * math.sin(ang) + y * math.cos(ang)
    gx, gy = x / cell, y / cell
    ix, iy = math.floor(gx), math.floor(gy)
    fx, fy = gx - ix, gy - iy
    fx, fy = fx * fx * (3 - 2 * fx), fy * fy * (3 - 2 * fy)
    a = _rand(seed, ix, iy) + (_rand(seed, ix + 1, iy) - _rand(seed, ix, iy)) * fx
    b = _rand(seed, ix, iy + 1) + (_rand(seed, ix + 1, iy + 1) - _rand(seed, ix, iy + 1)) * fx
    return a + (b - a) * fy


def fbm(x, y, seed):
    return 0.55 * _value(seed, x, y, 14) + 0.3 * _value(seed + 101, x, y, 7) + 0.15 * _value(seed + 202, x, y, 3.5)


def fine(x, y, seed):
    """Smaller-grained noise for woods and hills, so they come in patches rather than one big blob."""
    return 0.5 * _value(seed, x, y, 7) + 0.3 * _value(seed + 101, x, y, 3.5) + 0.2 * _value(seed + 202, x, y, 2)


def seg_dist(p, a, b):
    (px, py), (ax, ay), (bx, by) = p, a, b
    dx, dy = bx - ax, by - ay
    t = max(0, min(1, ((px - ax) * dx + (py - ay) * dy) / float(dx * dx + dy * dy)))
    return math.hypot(px - ax - t * dx, py - ay - t * dy)


def line_dist(p, pts): return min(seg_dist(p, pts[i], pts[i + 1]) for i in range(len(pts) - 1))


def cells_of(pts):
    """4-connected cells along a polyline (roads must be walkable step by step)."""
    out = []
    for (ax, ay), (bx, by) in zip(pts, pts[1:]):
        n = int(max(abs(bx - ax), abs(by - ay)) * 4) + 1
        for i in range(n + 1):
            c = (int(round(ax + (bx - ax) * i / n)), int(round(ay + (by - ay) * i / n)))
            if out and c != out[-1] and c[0] != out[-1][0] and c[1] != out[-1][1]:
                out.append((c[0], out[-1][1]))
            if not out or c != out[-1]: out.append(c)
    return out


# ---------------------------------------------------------------- land and sea
def raw_land(x, y):
    if x < 2 or y < 2 or y > H - 3: return 'sea'
    rough = (fbm(x, y, 1) - 0.5) * 1.3 + (_value(9, x, y, 2.5) - 0.5) * 0.3
    if ((x - 36) / 32.0) ** 2 + ((y - 36) / 31.0) ** 2 + rough < 0.92: return 'west'
    return 'sea'


def secret_isle(x, y):
    """'isle' on the island, 'sea' in a channel round it (so it never joins the mainland), else None."""
    d = math.hypot(x - SECRET_ISLE[0], (y - SECRET_ISLE[1]) * 1.2) + (fine(x, y, 4) - 0.5) * 1.5
    return 'isle' if d < SECRET_ISLE[2] else 'sea' if d < SECRET_ISLE[2] + 4 else None


BAY_C = (NX + 14, NY + 0.5)


def bay(x, y):
    """The bay east of the capital: sea from the second column past it, opening to the ocean in the east."""
    return math.hypot((x - BAY_C[0]) / 6.5, (y - BAY_C[1]) / 4.5) < 1 or (x >= BAY_C[0] and abs(y - BAY_C[1]) < 3 + (x - BAY_C[0]) * 0.5)


def headlands(x, y):
    """Land wrapping round the bay to the north and south."""
    return math.hypot((x - NX - 8) / 9.0, (y - BAY_C[1]) / 11.0) < 1


land = [[raw_land(x, y) for x in range(W)] for y in range(H)]
for y in range(H):
    for x in range(W):
        if (NX - 6 <= x <= NX + 7 and NY - 6 <= y <= NY + 7) or headlands(x, y): land[y][x] = 'west'
        if bay(x, y): land[y][x] = 'sea'
        land[y][x] = secret_isle(x, y) or land[y][x]
        if math.hypot((x - LAKE[0]) / LAKE[2], (y - LAKE[1]) / LAKE[3]) < 1: land[y][x] = 'lake'
road_cells = set(c for r in ROADS for c in cells_of(r))
for x, y in road_cells:                                  # roads always run on land, with a verge either side
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if land[y + dy][x + dx] == 'sea': land[y + dy][x + dx] = 'west'


def components(match):
    seen, comps = set(), []
    for y in range(H):
        for x in range(W):
            if (x, y) in seen or not match(land[y][x]): continue
            stack, comp = [(x, y)], []
            seen.add((x, y))
            while stack:
                cx, cy = stack.pop(); comp.append((cx, cy))
                for nx, ny in ((cx + 1, cy), (cx - 1, cy), (cx, cy + 1), (cx, cy - 1)):
                    if 0 <= nx < W and 0 <= ny < H and (nx, ny) not in seen and match(land[ny][nx]):
                        seen.add((nx, ny)); stack.append((nx, ny))
            comps.append(comp)
    return comps


for comp in components(lambda v: v != 'sea'):          # specks of land -> sea
    if len(comp) < 8:
        for x, y in comp: land[y][x] = 'sea'
for comp in components(lambda v: v == 'sea'):          # puddles cut off from the ocean -> land
    if len(comp) < 40:
        for x, y in comp: land[y][x] = 'west'

is_water = lambda x, y: not (0 <= x < W and 0 <= y < H) or land[y][x] in ('sea', 'lake')
shore_dist = {}                                        # sea cells: distance to the nearest land
frontier = [(x, y) for y in range(H) for x in range(W) if not is_water(x, y)]
for c in frontier: shore_dist[c] = 0
while frontier:
    nxt = []
    for cx, cy in frontier:
        for nx, ny in ((cx + 1, cy), (cx - 1, cy), (cx, cy + 1), (cx, cy - 1)):
            if 0 <= nx < W and 0 <= ny < H and (nx, ny) not in shore_dist:
                shore_dist[(nx, ny)] = shore_dist[(cx, cy)] + 1; nxt.append((nx, ny))
    frontier = nxt
coastal = lambda x, y: any(is_water(x + dx, y + dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1))

# ---------------------------------------------------------------- biomes
town_cells = set((x, y) for x in range(NX, NX + 6) for y in (NY, NY + 1))
m = L.MapBuilder(W, H, OVERWORLD, K.NAMES[K.WORLD][0], K.NAMES[K.WORLD][1])
m.note = '<outdoor>'
m.bgm = {'name': 'Field1', 'pan': 0, 'pitch': 100, 'volume': 80}
region = [[0] * W for _ in range(H)]

for y in range(H):
    for x in range(W):
        kind = land[y][x]
        if kind in ('sea', 'lake'):
            m.cell(x, y, DEEP_SEA if kind == 'sea' and shore_dist[(x, y)] >= 4 else SEA)
            continue
        snow = y < 15 + (fbm(x, y, 11) - 0.5) * 9
        dry = math.hypot((x - 11) / 12.0, (y - 55) / 11.0) + (fbm(x, y, 12) - 0.5) * 0.7
        desert, waste = dry < 1, 1 <= dry < 1.2
        if kind != 'west': snow = desert = waste = False
        m.cell(x, y, SNOW if snow else DESERT if desert else WASTE if waste else GRASS)

        f, f2 = fine(x, y, 7), fine(x, y, 8)
        ridge = line_dist((x, y), RIDGE) if kind == 'west' else 99
        width = 1.3 + 1.5 * fbm(x, y, 5)
        in_pass = any(math.hypot(x - px, y - py) < 2.2 for px, py in PASSES)
        near_nova = math.hypot(x - NOVA_C[0], (y - NOVA_C[1]) * 1.4) < 6.5
        deco = None
        if ridge < width and not in_pass:
            deco = SNOW_MOUNTAIN if snow else ROCK_MOUNTAIN if f2 > 0.5 else MOUNTAIN
        elif ridge < width + 1.8:
            deco = SNOW_HILL if snow else DIRT_HILL if waste or desert else HILL
        elif snow:
            deco = SNOW_MOUNTAIN if y < 6 and f2 > 0.45 else SNOW_FOREST if f > 0.56 else SNOW_HILL if f < 0.2 else None
        elif desert:
            deco = PALMS if coastal(x, y) and f2 > 0.5 else SAND_HILL if f > 0.68 else SAND_MOUNTAIN if f < 0.16 else None
        elif waste:
            deco = DIRT_HILL if f > 0.66 else DEAD_FOREST if f < 0.3 else None
        elif kind == 'isle':
            deco = PALMS if f > 0.55 else None
        else:
            deco = (CONIFER if x > 50 and y < 26 else FOREST) if f > 0.56 else HILL if f < 0.2 else None
        if near_nova or (x, y) in road_cells: deco = None
        if deco: m.cell(x, y, deco, layer=1)

        if kind != 'west' or near_nova and math.hypot(x - NOVA_C[0], y - NOVA_C[1]) < 4: r = 0
        elif snow: r = 5
        elif desert or waste: r = 3
        elif ridge < width + 4 or (x > 50 and y < 26): r = 4
        elif coastal(x, y): r = 6
        elif math.hypot(x - NOVA_C[0], y - NOVA_C[1]) < 18: r = 1
        else: r = 2
        region[y][x] = r

for x, y in road_cells:
    assert not is_water(x, y), 'road runs into water at %d,%d' % (x, y)
    if (x, y) not in town_cells: m.cell(x, y, ROAD, layer=1)

# ---------------------------------------------------------------- the Royal Capital of Nova
for blk, bx in ((VILLAGE, NX), (CASTLE, NX + 2), (VILLAGE_MIRROR, NX + 4)):
    for dy, row in enumerate(blk):
        for dx, t in enumerate(row): m.put(bx + dx, NY + dy, t)
for x in range(NX + 8, NX + 10): m.put(x, NY + 1, PIER)     # Saltwind Harbor's pier
m.put(NX + 8, NY - 2, LIGHTHOUSE)                            # and its lighthouse on the north point
assert all(is_water(x, NY + 1) for x in range(NX + 8, NX + 11)) and not is_water(NX + 8, NY - 2)
m.put(*SIGN_AT, SIGNPOST)

for x, y in sorted(town_cells):
    if (x, y) in ((NX + 2, NY), (NX + 3, NY)): continue     # castle towers: not walkable
    gate, label = (WEST_GATE, 'West Gate') if x < NX + 3 else (EAST_GATE, 'East Gate')
    m.add_event('Royal Capital Nova - %s' % label, x, y, [L.exit_page(*gate)], note='<minimap: exit>')

m.add_event('Harbor Ship', NX + 10, NY + 1, [page(char('Vehicle', 1, 4), step_anim=True, walk_anim=False)],
            note='<minimap: hide>')
m.add_event('Crossroads Sign', SIGN_AT[0], SIGN_AT[1], [page(None, commands=text(
    'North: the mountain pass.', 'South-west: the wastes.', 'East: the Royal Capital of Nova.'))],
    note='<minimap: hide>')

# dev testers from the old test map, parked by the West Gate
_old = {e['name']: e for e in json.load(open(L.DATA + 'Map001.json', encoding='utf8'))['events'] if e}
for name, (x, y) in (('EV001', (NX - 4, NY - 1)), ('Pet Tester', (NX - 2, NY - 1))):
    if name in _old: m.add_event(name, x, y, _old[name]['pages'], note=_old[name]['note'])

ENCOUNTER_LIST = [{'troopId': t, 'weight': w, 'regionSet': [r]} for r, lst in sorted(ENCOUNTERS.items()) for t, w in lst]
_tile_data = m.tile_data
m.tile_data = lambda: _tile_data()[:5 * W * H] + [region[y][x] for y in range(H) for x in range(W)]


# ---------------------------------------------------------------- city gates on the Nova side
def gate_events():
    """{map id: [(name, cells, arrival)]} - the exits from the capital out to this map."""
    return {K.MARKET: [('To World Map (East Gate)', [(45, y) for y in range(14, 18)], K.ARRIVE['world_from_east_gate'])],
            K.RESIDENTIAL: [('To World Map (West Gate)', [(0, y) for y in range(15, 19)], K.ARRIVE['world_from_west_gate'])]}


def patch_gates():
    for mid, exits in gate_events().items():
        mp = json.load(open(L.DATA + 'Map%03d.json' % mid, encoding='utf8'))
        names = [n for n, _, _ in exits]
        mp['events'] = [None if e and any(e['name'].startswith(n) for n in names) else e for e in mp['events']]
        while len(mp['events']) > 1 and mp['events'][-1] is None: mp['events'].pop()
        for name, cells, arrive in exits:
            for i, (x, y) in enumerate(cells):
                slot = next((k for k in range(1, len(mp['events'])) if mp['events'][k] is None), len(mp['events']))
                ev = {'id': slot, 'name': '%s %d' % (name, i + 1), 'note': '', 'pages': [L.exit_page(*arrive)], 'x': x, 'y': y}
                if slot == len(mp['events']): mp['events'].append(ev)
                else: mp['events'][slot] = ev
        L.write_map(mid, mp)


if __name__ == '__main__':
    out = next((a for a in sys.argv[1:] if not a.startswith('--')), None)
    if out: m.render(out, scale=0.25, grid='--grid' in sys.argv)
    if '--save' in sys.argv:
        m.save(K.WORLD, parent_id=0, order=1, encounter=ENCOUNTER_LIST)
        patch_gates()
        print('saved Map%03d + gates' % K.WORLD)
