# Villa Bloodrose (Map048) - the hereditary seat of the Bloodrose family (chapters 7 and 11), seen from its grounds by
# night. A gothic manor of dark stone and slate stands on a crag: the only way in is a long stone bridge over a
# misty chasm, then a gate in the curtain wall, a courtyard with a demon fountain, the family's rose garden (a
# crimson-violet "bloodrose" tree at its heart), and the family graveyard with its crypt. Purple thorn towers and
# thorned walls mark it as Bloodrose ground.
# Mood: the user asked for "lebih gelap" (darker) than the Valemont sample it grew from, and named a dark fairy-tale
# beast's castle as the feel to aim for: one lonely castle, a bridge over an abyss, cold blue night, warm windows, roses.
# The layout is our own.
# Outside tileset (2) + PM_Forest (gnarled bare trees, the violet tree), PM_Rome_B (arched doorway), Avy_Castle_B3
# (grey round towers, without their orange cones), Outside_C purple thorn towers, through L.ext.
#   python map_villa_bloodrose.py preview.png [--grid]   -> preview image
#   python map_villa_bloodrose.py --save                 -> write Map048 (editor must be closed)
import sys, os, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from town_kit import *
import nova_maplib as L
from nova_maplib import page, char, text, say, cmd
import kingdom as K

W, H = 44, 50
PF = lambda n: L.ext('PM_Forest', n)
ROME = lambda n: L.ext('PM_Rome_B', n)
AC3 = lambda n: L.ext('Avy_Castle_B3', n)
OC = lambda n: C_ + n                                    # Outside_C is this tileset's own C sheet

# ---------------------------------------------------------------- named tiles (checked on 2x crops of the sheets)
SLATE = ('A3', ROOF['indigo'])                           # dark blue slate roofs
DARK_STONE_TOP, DARK_STONE = ('A4', 0), ('A4', 8)        # dark grey ashlar
THORN_TOP, THORN_WALL = ('A4', 39), ('A4', 47)           # violet brick overgrown with thorns
WITHERED, DARK_GRASS = ('A2', 20), ('A2', 4)
VOID, CLIFF_A, CLIFF_B = ('A5', 0), ('A5', 112), ('A5', 120)
SLAB = ('A5', 68)                                        # bridge deck
ARCH_DOORWAY = ((133, 134, 135), (141, 142, 143), (149, 150, 151))          # PM_Rome_B, 3x3, dark inside
BIG_TOWER = [(3, 4, 5, 6), (11, 12, 13, 14), (19, 20, 21, 22)] + [(27, 28, 29, 30), (35, 36, 37, 38)] * 5 + [(43, 44, 45, 46)]
SMALL_TOWER = [(1, 2), (9, 10), (17, 18), (25, 26), (33, 34)]                # Avy_Castle_B3, open crenellated tops
THORN_TOWER = [(204, 205), (212, 213), (220, 221), (228, 229), (236, 237), (244, 245)]   # Outside_C
BARE_TREE_A = [(176, 177, 178), (184, 185, 186), (192, 193, 194)]           # PM_Forest gnarled trees
BARE_TREE_B = [(179, 180), (187, 188), (195, 196)]
BARE_TREE_C = [(181, 182, 183), (189, 190, 191), (197, 198, 199)]
MOSS_TREE = [(136, 137, 138), (144, 145, 146), (152, 153, 154)]
BARE_SMALL = [(163,), (171,)]
BARE_PAIR = [(164, 165), (172, 173)]
VIOLET_TREE = [(200, 201, 202, 203, 204), (208, 209, 210, 211, 212), (216, 217, 218, 219, 220),
               (224, 225, 226, 227, 228), (232, 233, 234, 235, 236), (240, 241, 242, 243, 244),
               (248, 249, 250, 251, 252)]
DEMON = (OC(83), OC(91))
DRAGON = ((OC(85), OC(86)), (OC(93), OC(94)))
MONUMENT_A, MONUMENT_B = (OC(48), OC(56)), (OC(49), OC(57))
BANNER = BANNER_RED
GRAVES = (78, 79)
STAINED_ARCH, DARK_ARCH = 51, 53                       # Outside_B gothic windows
ROSE_WINDOW = STAINED
TALL_WINDOW = (ROME(128), ROME(136))                    # PM_Rome_B framed window, 1x2
DEAD_GRASS = (175, 183)
DEAD_TREE_S, DEAD_SHRUB = 168, 177
NN = lambda n: L.ext('Nova_Nature', n)
ROSE_BUSH, ROSE_CLUMP = FLOWER_BUSH, NN(5)               # pink in daylight, deep rose under this night
THORNS = (NN(12), NN(13))                               # dry thorny shrubs

m = Town(W, H, K.NAMES[K.VILLA_BLOODROSE][0], K.NAMES[K.VILLA_BLOODROSE][1], ground=DARK_GRASS)
m.note = '<outdoor>\n<night ambient: #5c5878>\n<glow: 0.4>'               # always night here; lamps and windows carry the light
m.bgm = {'name': '03_Ancient_Castle', 'pan': 0, 'pitch': 95, 'volume': 70}
m.bgs = {'name': 'Wind', 'pan': 0, 'pitch': 80, 'volume': 45}
rnd = random.Random(48)
taken = set()


def claim(x0, y0, x1, y1):
    taken.update((x, y) for x in range(x0, x1 + 1) for y in range(y0, y1 + 1))


def stamp(x0, y0, rows, f, base_layer=2):
    """Multi-tile object: every row above the last on the upper layer."""
    last = len(rows) - 1
    for r, row in enumerate(rows):
        for c, n in enumerate(row):
            if n is not None: m.put(x0 + c, y0 + r, f(n), base_layer if r == last else 3)
    claim(x0, y0, x0 + len(rows[0]) - 1, y0 + last)


def blocker(x, y):
    """Avy tiles are all passable - an empty event keeps the player off a tower drawn over walkable ground."""
    m.add_event('Block', x, y, [page(None, priority=1)])


def light(x, y, radius, color, flicker=True, oy=0):
    note = '<light: %d, %s%s%s>' % (radius, color, ', flicker' if flicker else '', ', %d' % oy if oy else '')
    m.add_event('Light', x, y, [page(None, priority=0, through=True)], note)


def tall(x, y, pair):
    m.put(x, y, pair[0], 3); m.put(x, y + 1, pair[1]); claim(x, y, x, y + 1)


# ================================================================ the manor (north)
m.rect(0, 0, W - 1, 4, VOID)                              # night sky above the wings
m.rect(13, 0, 29, 6, SLATE)                               # the hall roof
m.rect(0, 5, 12, 8, SLATE); m.rect(30, 5, W - 1, 8, SLATE)   # the wing roofs
# central hall: roof y0..6, a tall dark face y7..15
m.rect(13, 7, 29, 15, DARK_STONE)
# wings: lower roofs, faces y9..15
m.rect(0, 9, 12, 15, DARK_STONE); m.rect(30, 9, W - 1, 15, DARK_STONE)
# the hall front: stained arches up high, dark arches below, a rose window over the doors
for x in (15, 17, 19, 23, 25, 27): m.put(x, 8, STAINED_ARCH)
m.put(21, 8, ROSE_WINDOW)
for x in (15, 17, 25, 27): m.put(x, 10, TALL_WINDOW[0]); m.put(x, 11, TALL_WINDOW[1])
for x in (15, 19, 23, 27): light(x, 8, 70, '#ffc070', oy=8)   # candlelight behind the stained glass
light(21, 8, 90, '#ff6a80', flicker=False, oy=8)                 # the rose window glows red
for x in (5, 11, 34, 40): light(x, 12, 60, '#ffc070', oy=8)
for x0 in (13, 28): stamp(x0, 2, SMALL_TOWER, AC3)          # turrets on the corners of the hall roof
stamp(20, 13, ARCH_DOORWAY, ROME, base_layer=2)
for x in (18, 24): tall(x, 11, BANNER)
for x in (19, 23): tall(x, 13, BANNER)
# wing fronts: two storeys of arched windows, thorned vines climbing the stone
for x in list(range(3, 12, 2)) + list(range(32, 42, 2)):
    if x in (3, 41): continue
    m.put(x, 11, STAINED_ARCH if x % 4 == 1 else DARK_ARCH)
    m.put(x, 13, DARK_ARCH if x % 4 == 1 else STAINED_ARCH)
for x in (4, 10, 33, 39): m.put(x, 10, VINES[0]); m.put(x, 11, VINES[1])
# great grey towers at the corners of the hall (the cones left off: they are orange on that sheet)
for x0 in (9, 30):
    stamp(x0, 2, BIG_TOWER, AC3)
    for x in range(x0, x0 + 4): blocker(x, 15)
# thorn towers at the ends of the wings
for x0 in (0, W - 2):
    stamp(x0, 10, THORN_TOWER, OC)
claim(0, 0, W - 1, 15)

# ================================================================ the courtyard
m.rect(0, 16, W - 1, 17, ROAD)                            # terrace along the front
m.rect(19, 16, 23, 36, COBBLE)                            # the avenue, door to gate
m.rect(16, 21, 26, 28, COBBLE)                            # the fountain square
m.rect(18, 22, 24, 27, WATER)
tall(21, 24, DEMON)
light(21, 25, 120, '#7a8cff', flicker=False)              # the fountain's cold glow
for x0 in (14, 26):                                       # dragon statues at the foot of the steps
    stamp(x0, 16, DRAGON, lambda n: n)
for x in (17, 25):                                        # lamps along the avenue
    for base in (20, 31):
        m.lamp(x, base); claim(x, base - 2, x, base)        # the lamp tile is lit by NovaLighting's Tile Lights
claim(16, 16, 26, 32)
for y in range(18, 33): m.cell(0, y, METAL_FENCE, 1); m.cell(W - 1, y, METAL_FENCE, 1)

# ---------------------------------------------------------------- west: the rose garden and the bloodrose tree
for x0, y0, x1, y1 in ((2, 19, 14, 20), (2, 30, 14, 31), (2, 21, 3, 29), (13, 21, 14, 23), (13, 27, 14, 29)):
    m.rect(x0, y0, x1, y1, DARK_GRASS)
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            if (x + y) % 2 == 0: m.put(x, y, ROSE_BUSH if (x + y) % 4 == 0 else ROSE_CLUMP)
claim(1, 18, 15, 32)
m.rect(4, 21, 12, 29, ROAD)                               # the path round the tree
stamp(6, 21, VIOLET_TREE, PF)
m.rect(13, 24, 15, 26, ROAD)                              # garden gate from the fountain square
m.cell(15, 24, ROAD); m.cell(15, 25, ROAD); m.cell(15, 26, ROAD)
for x, y in ((4, 22), (12, 22), (4, 28), (12, 28)):
    m.put(x, y, POT)

# ---------------------------------------------------------------- east: the family graveyard and crypt
m.rect(29, 19, W - 2, 31, WITHERED)                       # the graveyard grass has died
for x in range(28, W - 1): m.cell(x, 18, METAL_FENCE, 1); m.cell(x, 32, METAL_FENCE, 1)
for y in range(18, 33): m.cell(28, y, METAL_FENCE, 1)
for y in (24, 25, 26): m.cell(28, y, None, 1)
m.rect(27, 24, 28, 26, ROAD)
m.building(36, 41, 19, 2, 3, 'indigo', 'stone', windows=False)
stamp(37, 21, ARCH_DOORWAY, ROME)
tall(36, 22, MONUMENT_A); tall(41, 22, MONUMENT_A)
claim(35, 18, 42, 24)
for gx, gy in ((30, 21), (32, 21), (30, 28), (32, 28), (34, 28), (36, 28), (38, 28), (34, 25), (36, 25), (38, 25)):
    m.put(gx, gy, GRAVES[(gx + gy) % 2]); claim(gx, gy, gx, gy)
tall(30, 25, MONUMENT_B)
stamp(39, 25, MOSS_TREE, PF)
stamp(29, 29, BARE_PAIR, PF)

# ================================================================ curtain wall and gate (south of the courtyard)
m.rect(0, 33, W - 1, 34, CASTLE_TOP); m.rect(0, 35, W - 1, 36, CASTLE_WALL)
m.rect(20, 33, 22, 36, COBBLE)
for x in (19, 23): m.rect(x, 33, x, 34, CASTLE_WALL)     # passage sides: no stepping onto the wall walk
for x in range(0, W):
    if not 19 <= x <= 23 and m.get(x, 32, 1) != METAL_FENCE: m.cell(x, 32, METAL_FENCE, 1)
for x in (19, 23): m.cell(x, 32, METAL_FENCE, 1)
for x0 in (17, 24):
    stamp(x0, 32, SMALL_TOWER, AC3)
    for y in range(32, 37):
        for x in (x0, x0 + 1): blocker(x, y)
for x in (5, 11, 31, 37): tall(x, 35, BANNER)
for e in m.events[1:]:                                    # torches on the gate towers (on their blockers)
    if e['name'] == 'Block' and (e['x'], e['y']) in ((18, 33), (25, 33)): e['note'] = '<light: 110, #ff8a40, flicker, -10>'
claim(0, 32, W - 1, 36)

# ================================================================ the chasm and the bridge
m.rect(0, 37, W - 1, 38, CLIFF_A); m.rect(0, 38, W - 1, 38, CLIFF_B)
m.rect(0, 39, W - 1, 44, VOID)
m.rect(20, 37, 22, 44, SLAB)
for y in range(37, 45): m.cell(19, y, STONE_FENCE, 1); m.cell(23, y, STONE_FENCE, 1)
claim(0, 37, W - 1, 44)

# ================================================================ the south bank: the road in through dead woods
m.rect(0, 45, W - 1, H - 1, WITHERED)
m.rect(20, 45, 22, H - 1, ROAD)
for x in (18, 24):
    m.lamp(x, 47); claim(x, 45, x, 47)                     # lit by Tile Lights, no extra light event
m.put(17, 47, SIGNPOST); claim(17, 47, 17, 47)
for x0, y0, tree in ((1, 45, BARE_TREE_A), (6, 46, BARE_TREE_B), (10, 45, BARE_TREE_C), (27, 45, BARE_TREE_C),
                     (32, 46, BARE_TREE_A), (37, 45, BARE_TREE_B), (40, 46, BARE_TREE_A), (14, 46, BARE_PAIR)):
    stamp(x0, y0, tree, PF)
claim(17, 45, 25, H - 1)

# ================================================================ ground dressing
for i in range(120):
    x, y = rnd.randrange(0, W), rnd.randrange(16, H)
    if (x, y) in taken or m.top[0][y][x] or m.get(x, y) not in (WITHERED, DARK_GRASS): continue
    m.put(x, y, rnd.choice(DEAD_GRASS + DEAD_GRASS + (DEAD_SHRUB,) + THORNS))

# ================================================================ events
door_lines = ('The doors are black oak bound in iron, taller than three men.',
              'A rose is carved over the lock - its thorns worn smooth by many hands.')
m.add_event('Great Doors', 21, 15, [page(char('!$Gate1', 0), commands=text(*door_lines), walk_anim=False)])
m.add_event('Crypt Door', 38, 23, [page(None, priority=1, commands=text(
    'The Bloodrose crypt. The names on the lintel go back further than the kingdom does.',
    'The door is sealed - not with a lock, but with something colder.'))])
m.add_event('Bloodrose Tree', 8, 27, [page(None, priority=1, commands=text(
    'Its leaves are the colour of wine held up to a candle.', 'Petals drift down, though there is no wind.'))])
m.add_event('Fountain', 21, 22, [page(None, priority=1, commands=text(
    'A horned figure pours black water into the basin.', 'The water is ice-cold and perfectly still.'))])
m.add_event('Signpost', 17, 47, [page(None, priority=1, commands=text(
    '"VILLA BLOODROSE."', 'Below, newer letters: "The house receives no one."'))])
for gx, gy, lines in ((32, 21, ('"Here sleeps Aurelie Bloodrose, who loved the garden more than the house."',)),
                      (36, 25, ('The name has been scratched out. Fresh roses lie on it anyway.',)),
                      (30, 26, ('"To the first David, who swore the oath and kept it."',))):
    m.add_event('Grave', gx, gy, [page(None, priority=1, commands=text(*lines))])

ITEMS = {1: 'Potion', 2: 'Magic Water', 5: 'Hi-Potion'}


def loot(name, x, y, item, n, where):
    found = [cmd(250, [{'name': 'Item3', 'volume': 80, 'pitch': 100, 'pan': 0}]), cmd(126, [item, 0, 0, n]),
             *text('Found %d \\C[6]%s\\C[0] %s!' % (n, ITEMS[item], where)), cmd(123, ['A', 0])]
    m.add_event(name, x, y, [page(None, commands=found, priority=1),
                             page(None, commands=text('Nothing else here.'), priority=1,
                                  cond={'selfSwitchValid': True, 'selfSwitchCh': 'A'})])


loot('Loot: Urn', 4, 22, 5, 1, 'in the stone urn')
loot('Loot: Offering', 34, 28, 2, 1, 'among the grave offerings')

m.npc('Lysandre', 12, 26, '$Succubus', 0, ('Lysandre:', 'You crossed the bridge without an invitation.',
      'Bold. Or foolish. Father will decide which.'), direction=4)
m.npc('Steward', 21, 18, 'Evil', 1, ('Steward:', 'The master is not receiving.',
      'Whatever you came for, the house has not lost it.'))
m.npc('Maid', 25, 29, 'Evil', 5, ('Maid:', 'Don\'t touch the roses. They prick back.'), move=1, freq=2)
m.npc('Gardener', 4, 25, 'Evil', 4, ('Gardener:', 'Black soil, red roses.', 'They drink deeper than you would think.'),
      direction=6)
for x in (19, 23):
    m.npc('Bone Sentinel', x, 31, '$Skull_Knight1', 0, ('Bone Sentinel:', '...', '(It watches you without eyes.)'))
m.critter('Ghost', 33, 23, 'Monster', 6, 'Monster1', 'A cold breath brushes past your neck.', move=1, freq=2,
          area=(29, 19, 42, 31))
for x, y in ((8, 18), (34, 17), (12, 46)):
    m.critter('Bat', x, y, 'Monster', 0, 'Monster2', 'Squeak!', move=1, speed=4, freq=4)
m.critter('Black Cat', 27, 17, 'Nature', 1, 'Cat', 'The cat stares at you, then at the doors, then at you.', move=1, freq=2)

if __name__ == '__main__':
    out = next((a for a in sys.argv[1:] if not a.startswith('--')), None)
    if out: m.render(out, scale=0.5, grid='--grid' in sys.argv)
    if '--save' in sys.argv:
        m.save(K.VILLA_BLOODROSE, parent_id=K.WORLD)
        print('saved Map%03d' % K.VILLA_BLOODROSE)
