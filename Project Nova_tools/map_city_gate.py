# MAP023 - Main Gate: the only way into the Royal Capital from the World Map. The city wall with its gatehouse
# across the top, the moat and the stone bridge, then a dirt road down through the meadow that forks to a small
# farmstead (west) and a travelling merchants' camp (east) before it leaves for the World Map at the bottom.
#   python map_city_gate.py preview.png [--grid]   -> preview image
#   python map_city_gate.py --save                 -> write Map023 (editor must be closed)
import sys, os, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from town_kit import *
from nova_maplib import page, char, text
import nova_maplib as L
import kingdom as K
from town_kit import wander_route

W, H = 40, 34
GX = 20                                    # gate centre column
m = Town(W, H, K.NAMES[K.CITY_GATE][0], K.NAMES[K.CITY_GATE][1], ground=GRASS)
m.bgm = {'name': 'Town1', 'pan': 0, 'pitch': 100, 'volume': 80}
m.note += '\n<bloom: 0.2>'                    # NovaAtmosphere: the pale dirt road glares at full bloom
rnd = random.Random(23)                    # fixed seed: every run draws the same map
P = PROP
assert K.ARRIVE['gate_from_plaza'][1:3] == (GX, 11) and K.ARRIVE['gate_from_world'][1:3] == (GX, H - 2)

# ---------------------------------------------------------------- the city wall and its gatehouse
m.rect(0, 0, W - 1, 4, CASTLE_TOP)
m.rect(0, 5, W - 1, 10, CASTLE_WALL)
# rooftops of the city peeking over the wall
for x0, x1, roof in ((0, 6, 'red'), (7, 12, 'indigo'), (13, 17, 'orange'), (23, 27, 'green'), (28, 33, 'red'), (34, 39, 'blue')):
    m.rect(x0, 0, x1, 1, ('A3', ROOF[roof]))
# gatehouse towers flanking the gate, and a pair of corner towers further out
for x0 in (GX - 4, GX + 3, 4, W - 6):
    for i, (a, b) in enumerate([(176, 177), (184, 185), (192, 193), (200, 201), (192, 193), (208, 209)]):
        y = 4 + i
        m.put(x0, y, C_ + a, 3 if i < 5 else 2); m.put(x0 + 1, y, C_ + b, 3 if i < 5 else 2)
for x in (2, 9, 13, 26, 30, 37):
    m.tall(x, 6, BANNER_RED)
m.put(GX, 6, SIGN['crest'])

# ---------------------------------------------------------------- moat and the stone bridge
m.rect(0, 11, W - 1, 14, WATER)
for y in range(11, 15):
    for x in range(GX - 2, GX + 3):
        m.put(x, y, STONE_BRIDGE_V)

# ---------------------------------------------------------------- the road (dirt, gently wandering)
road = set()
def lay(x, y):
    if 15 <= y < H and 0 <= x < W:
        m.cell(x, y, DIRT); road.add((x, y))

l, r = GX - 2, GX + 2
for y in range(15, H):
    if y > 17 and rnd.random() < 0.35: l += rnd.choice((-1, 1)) if GX - 3 <= l <= GX - 1 else (1 if l < GX - 2 else -1)
    if y > 17 and rnd.random() < 0.35: r += rnd.choice((-1, 1)) if GX + 1 <= r <= GX + 3 else (1 if r < GX + 2 else -1)
    for x in range(l, r + 1): lay(x, y)
for x in range(GX - 2, GX + 3): lay(x, H - 1)          # the bottom stays 5 wide for the exits

# west fork: past the farmstead to Hollow Farm (off the west edge)
y0 = K.ARRIVE['gate_from_farm'][2]
for x in range(0, GX - 1):
    top = y0 + (1 if 9 <= x < 14 and rnd.random() < 0.4 else 0)
    for y in range(top, y0 + 3): lay(x, y)
for y in range(y0, 25):
    for x in range(4, 8): lay(x, y)
# east fork: to the merchants' camp
for x in range(GX + 2, 33):
    for y in range(y0, y0 + 3): lay(x, y)
m.rect(28, 22, 37, 28, DIRT)
for x in range(28, 38):
    for y in range(22, 29): road.add((x, y))
for y in range(y0, 22):
    for x in range(30, 34): lay(x, y)

# ---------------------------------------------------------------- farmstead (west)
fb = m.building(2, 7, 25, 2, 2, 'thatch', 'log', windows=False)
m.put(3, fb, WIN); m.put(6, fb, WIN)
fb2 = m.building(10, 14, 25, 2, 2, 'wood', 'boards', windows=False)
m.put(12, fb2 - 1, WIN_SHUT)
for x in range(4, 8): lay(x, fb + 1)
m.rect(9, 29, 15, 32, ('A2', 8))                      # vegetable patch
for x in range(10, 15):
    for y in range(30, 32): m.put(x, y, CROPS[(x + y) % 4])
m.rect(9, 28, 15, 28, FENCE, layer=1); m.rect(9, 33, 15, 33, FENCE, layer=1)
m.rect(9, 28, 9, 33, FENCE, layer=1); m.rect(15, 28, 15, 31, FENCE, layer=1)
for x in range(9, 16):
    for y in range(28, 34): road.add((x, y))
m.put(8, fb + 1, WELL); m.put(2, fb + 2, HAY); m.put(3, fb + 2, HAY); m.put(1, 31, FIREWOOD); m.put(16, fb2 + 1, BARREL)
m.put(5, 32, SCARECROW)

# ---------------------------------------------------------------- merchants' camp (east)
m.tent(28, 22); m.tent(34, 22)
m.put(31, 27, FIRE_PIT)
for x, y, t in ((29, 26, CRATE), (30, 26, CRATE_APPLE), (35, 26, BARREL), (36, 26, CRATE_GRAIN), (37, 27, BARREL),
                (28, 28, LOG)):
    m.put(x, y, t)

# ---------------------------------------------------------------- dressing: lamps, sign, trees, rocks, flowers
m.lamp(GX - 4, 17); m.lamp(GX + 4, 17)
m.put(GX + 4, 23, SIGNPOST)
taken = set(road) | {(x, y) for x in (GX - 4, GX - 3, GX + 3, GX + 4) for y in range(15, 18)} | {(GX + 4, 23)}
taken |= {(x, y) for x in range(1, 17) for y in range(23, 34)} | {(x, y) for x in range(27, 39) for y in range(21, 30)}

def free(x, y, w=1, h=1, pad=1):
    return all(0 <= xx < W and 15 <= yy < H and (xx, yy) not in taken
               for xx in range(x - pad, x + w + pad) for yy in range(y - pad, y + h + pad))

def claim(x, y, w=1, h=1):
    for xx in range(x, x + w):
        for yy in range(y, y + h): taken.add((xx, yy))

# woods along both sides of the meadow, thinning toward the road
for _ in range(900):
    x, y = rnd.randrange(0, W), rnd.randrange(16, H)
    edge = min(x, W - 1 - x)
    if edge > 9 and rnd.random() < 0.85: continue
    if free(x, y - 1, 1, 2, 0):
        m.put(x, y - 1, TREE_S1, 3); m.put(x, y, TREE_S3); claim(x, y - 1, 1, 2)
for t, n in ((BOULDER, 4), (BOULDER_B, 3), (STUMP, 3), (FLOWER_BUSH, 5)):
    placed = 0
    for _ in range(n * 20):
        x, y = rnd.randrange(1, W - 1), rnd.randrange(16, H - 1)
        if placed < n and free(x, y, 1, 1, 1):
            m.put(x, y, t); claim(x, y); placed += 1
for i in range(40):
    x, y = rnd.randrange(0, W), rnd.randrange(15, H)
    if (x, y) not in taken:
        m.put(x, y, rnd.choice(GRASS_TUFTS + FLOWERS)); claim(x, y)

# ---------------------------------------------------------------- events
m.add_event('Main Gate', GX, 10, [L.door_page(K.PLAZA, *K.ARRIVE['plaza_from_gate'][1:], sheet='!$Gate1', index=0)],
            note='<minimap: exit>')
for x in (GX - 2, GX + 2):
    m.obj('Brazier', x, 10, '!Other2', 7, None, step=True)
m.exit('To Hollow Farm', [(0, y) for y in range(y0, y0 + 3)], *K.ARRIVE['farm_from_gate'])
for i, x in enumerate(range(GX - 2, GX + 3)):          # one landing spot: the World Map shows the capital as one tile
    m.add_event('To World Map %d' % (i + 1), x, H - 1, [L.exit_page(*K.ARRIVE['world_from_gate'])])
m.npc('Gate Guard', GX - 3, 15, 'People3', 6, ('Gate Guard:', 'Welcome to the Royal Capital of Nova.',
      'Keep your blades sheathed inside the walls.'), direction=2)
m.npc('Gate Guard', GX + 3, 15, 'People3', 7, ('Gate Guard:', 'The Grand Plaza is straight through the gate.',
      'Shops are in the Market District, east of the plaza.'), direction=2)
m.sign('Road Sign', GX + 4, 23, ['\\C[6]North:\\C[0] the Royal Capital of Nova', '\\C[6]West:\\C[0] Hollow Farm',
       "\\C[6]East:\\C[0] the merchants' camp", '\\C[6]South:\\C[0] the open road'])
m.npc('Farmer', 6, fb + 2, 'People1', 0, ('Farmer:', 'Best turnips this side of the mountains.',
      'The castle kitchens buy every last one.'), move=1, freq=2)
m.critter('Farm Cat', 9, 27, 'Nature', 1, 'Cat', 'The farm cat yawns at you.', move=1)
m.npc('Travelling Merchant', 31, 25, 'People2', 2, ('Travelling Merchant:', 'Fresh in from the coast road!',
      'Come back when my wagon arrives - I will have rare goods.'), direction=2)
m.npc('Mercenary', 33, 28, 'People4', 5, ('Mercenary:', 'Waiting for a caravan to guard.',
      'Pays better than fighting slimes, I tell you.'), direction=8)
m.npc('Traveller', GX + 1, 26, 'People1', 3, ('Traveller:', 'Three days on the road, and the gate at last!',
      'I hear the bread on Baker\'s Lane is worth the walk.'), route=wander_route('UUUWDDDW'), speed=3)

if __name__ == '__main__':
    out = next((a for a in sys.argv[1:] if not a.startswith('--')), None)
    if out: m.render(out, scale=0.5, grid='--grid' in sys.argv)
    if '--save' in sys.argv:
        m.save(K.CITY_GATE, parent_id=K.PLAZA, order=K.CITY_GATE)
        print('saved Map%03d' % K.CITY_GATE)
