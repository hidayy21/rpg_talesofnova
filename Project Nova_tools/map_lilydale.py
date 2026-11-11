# MAP065 - Lilydale (chapter 7): a mid-sized village in a clearing of the woods, the last place before Hollow Wood and
# the misty wood that hides Villa Bloodrose. The party arrives here first. The village knew the Bloodroses well once:
# David came to play here as a boy (the elders were those children), and his wife was loved here. Since she died in
# the war sixteen years ago only the villa's servants come, on market days, for flour and lamp oil - and for three
# weeks not even they have come.
#   - the square: an old well and an old rose-coloured tree (a cutting of the Bloodrose tree, planted long ago -
#     "the boy who always waited under the rose tree")
#   - the Lantern & Lily inn, the general store, a small stone chapel, the elders' houses, a farm and a lily pond
#   - road north (top) into Hollow Wood; road south (bottom) out of the valley (no World Map link yet)
# The woods round the clearing come from rm-map-forge (forge_outdoor.js, trees only); the village is laid by hand.
# Interiors are not built yet: their doors are latched for now.
#   python3 map_lilydale.py preview.png [--grid]   -> preview image
#   python3 map_lilydale.py --save                 -> write Map065 (editor must be closed)
import sys, os, math, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import nova_maplib as L
from nova_maplib import page, cmd, text, char
from town_kit import *
import kingdom as K
from forge_outdoor import forge, Tree, A2, BLOCKER

W, H = 50, 45
PF = lambda n: L.ext('PM_Forest', n)
NN = lambda n: L.ext('Nova_Nature', n)
ROSE_TREE = [(200, 201, 202, 203, 204), (208, 209, 210, 211, 212), (216, 217, 218, 219, 220),
             (224, 225, 226, 227, 228), (232, 233, 234, 235, 236), (240, 241, 242, 243, 244),
             (248, 249, 250, 251, 252)]                          # PM_Forest, 5x7 (the villa garden has its parent)
LILIES = (PF(9), PF(10))                                         # white lilies standing in water
ROSE_BUSH = FLOWER_BUSH

NORTH_X, SOUTH_X = (25, 26), (24, 25)                            # road lanes at the top and bottom edges


def in_clearing(x, y):
    """The village clearing: a wide oval with a ragged rim, plus the two roads out."""
    if x in NORTH_X and y <= 6 or x in SOUTH_X and y >= 38: return True
    wob = 1.3 * math.sin(x * 0.7) + 1.0 * math.cos(y * 0.9 + x * 0.3)
    return ((x - 24.5) / (21.5 + wob)) ** 2 + ((y - 22.5) / (18.5 + wob * 0.6)) ** 2 < 1


GREEN = [Tree([(16, 17, 18), (24, 25, 26), (32, 33, 34)], 0.30, None, 'PM_Forest'),
         Tree([(40, 41, 42), (48, 49, 50)], 0.25, None, 'PM_Forest'),
         Tree([(112, 113), (120, 121)], 0.25, None, 'PM_Forest'),
         Tree([(114, 115), (122, 123)], 0.22, None, 'PM_Forest'),
         Tree(BIG_TREE, 0.15),
         Tree([(BUSH_S,)], 0.05)]
# everything the village builds stays clear of the forest trees (with a margin)
VILLAGE = [(10, 5, 19, 10), (32, 3, 40, 9), (38, 12, 45, 16), (4, 15, 10, 19), (5, 25, 11, 29), (13, 25, 19, 29),
           (29, 25, 35, 29), (37, 25, 43, 29), (4, 33, 18, 39), (32, 32, 43, 39)]
KEEP = [(x, y) for y in range(H) for x in range(W) if in_clearing(x, y) or
        any(x0 - 1 <= x <= x1 + 1 and y0 - 2 <= y <= y1 + 1 for x0, y0, x1, y1 in VILLAGE)]
m = forge(K.NAMES[K.LILYDALE], W, H, seed='lilydale-1', ground=A2(0), road=A2(1), paths=[], keep=KEEP, trees=GREEN,
          params={'hills': 0, 'scale': 16})
m.note = '<outdoor>'
m.bgm = {'name': 'Town2', 'pan': 0, 'pitch': 95, 'volume': 70}
m.bgs = {'name': 'Wind', 'pan': 0, 'pitch': 100, 'volume': 15}
rnd = random.Random(65)
m.rect(0, 0, W - 1, H - 1, GRASS)                                # our own ground everywhere (the forge gave the trees)
KEEP_SET = set(KEEP)
taken = set()


def claim(x0, y0, x1, y1): taken.update((x, y) for x in range(x0, x1 + 1) for y in range(y0, y1 + 1))


def dirt(x0, y0, x1, y1):
    m.rect(x0, y0, x1, y1, DIRT); claim(x0, y0, x1, y1)


# gaps in the forest ring that no whole tree fitted into stay closed (the edge of the clearing is the forest)
for y in range(H):
    for x in range(W):
        if (x, y) not in KEEP_SET and not m.has_object(x, y):
            m.put(x, y, BLOCKER)
            if rnd.random() < 0.5: m.put(x, y, rnd.choice((BUSH_S, FERN, TREE_S1)), 3)

# ---------------------------------------------------------------- roads, the square, lanes
dirt(NORTH_X[0], 0, NORTH_X[1], 16)                              # north road, into Hollow Wood
dirt(SOUTH_X[0], 27, SOUTH_X[1], H - 1)                          # south road, out of the valley
m.rect(18, 17, 33, 26, COBBLE); claim(18, 17, 33, 26)            # the square
dirt(4, 21, 17, 22)                                              # west lane
dirt(34, 21, 45, 22)                                             # east lane, to the pond
dirt(5, 30, 23, 31); dirt(26, 30, 44, 31)                        # south lanes

# ---------------------------------------------------------------- buildings (door x, street row)
DOORS = {}


def house(name, x0, x1, top, roof_rows, wall_rows, roof, wall, door, chimney=None, sign=None, flowers=True,
          style=0, wins=(WIN, WIN_FLOWER_P)):
    bottom = m.building(x0, x1, top, roof_rows, wall_rows, roof, wall, door=door, win_tiles=wins, chimney=chimney)
    claim(x0, top, x1, bottom)
    DOORS[name] = (door, bottom, style)
    if sign: m.put(door + 2 if door + 2 < x1 else door - 2, bottom - 1, SIGN[sign])
    if flowers:
        for x in (x0, x1):
            if (x, bottom + 1) not in taken: m.put(x, bottom + 1, ROSE_BUSH)
    return bottom


inn = house('Lantern & Lily Inn', 10, 19, 5, 3, 3, 'red', 'tudor', 15, chimney=12, sign='inn')
dirt(15, inn + 1, 15, 20)
chapel = house('Chapel', 32, 40, 3, 3, 4, 'indigo', 'stone', 36, flowers=False, style=2, wins=(STAINED,))
dirt(36, chapel + 1, 36, 20)
store = house('General Store', 38, 45, 12, 2, 3, 'green', 'brickstone', 41, sign='item')
dirt(41, store + 1, 41, 20)
house('Old Henrik\'s House', 4, 10, 15, 2, 3, 'orange', 'plaster', 7, chimney=5)
dirt(7, 20, 7, 20)
house('Old Bram\'s House', 5, 11, 25, 2, 3, 'thatch', 'log', 8, chimney=10)
house('Old Marta\'s House', 13, 19, 25, 2, 3, 'khaki', 'plaster', 16)
house('Cottage', 29, 35, 25, 2, 3, 'blue', 'wood', 32, chimney=34)
house('Farmhouse', 37, 43, 25, 2, 3, 'thatch', 'boards', 40)

# ---------------------------------------------------------------- the square: the rose tree and the well
RX, RY = 18, 18                                                  # top-left of the rose tree's trunk row is (RX.., RY)
for r, row in enumerate(ROSE_TREE):
    for c, n in enumerate(row):
        m.put(RX + c, RY - 6 + r, PF(n), 2 if r == 6 else 3)
claim(RX, RY - 6, RX + 4, RY)
for x in (RX, RX + 4): m.put(x, RY + 1, ROSE_BUSH)
m.put(RX + 1, RY + 1, FLOWERS[0]); m.put(RX + 3, RY + 1, FLOWERS[2])
WELL_AT = (29, 22)
m.put(*WELL_AT, WELL); m.put(30, 23, BUCKET)
m.put(31, 18, NOTICE_BOARD)
for x, y in ((18, 26), (33, 26), (33, 17)): m.put(x, y, POT)

# ---------------------------------------------------------------- lamps along the roads
for x, y in ((24, 14), (27, 14), (23, 29), (26, 29), (17, 23), (34, 23)):
    if (x, y) not in taken: m.lamp(x, y); claim(x, y - 2, x, y)

# ---------------------------------------------------------------- the farm (south-west) and the lily pond (south-east)
m.rect(5, 34, 15, 38, DIRT); claim(4, 33, 16, 39)               # tilled soil
for y in (34, 36, 38):
    for x in range(5, 16): m.put(x, y, CROPS[(y // 2) % 4])
for x in range(4, 17): m.cell(x, 33, FENCE, 1); m.cell(x, 39, FENCE, 1)
for y in range(33, 40): m.cell(4, y, FENCE, 1); m.cell(16, y, FENCE, 1)
m.cell(10, 33, None, 1)                                          # the gate into the field
m.put(18, 35, SCARECROW); m.put(18, 37, HAY); m.put(17, 34, BARREL)
m.rect(33, 33, 42, 38, WATER); claim(32, 32, 43, 39)
for x, y in ((34, 34), (36, 35), (39, 34), (41, 36), (35, 37), (38, 37)): m.put(x, y, LILIES[(x + y) % 2])
for x, y in ((32, 33), (43, 34), (32, 37), (43, 38), (37, 39)): m.put(x, y, rnd.choice(FLOWERS))
m.put(33, 39, LOG)

# props by the doors
m.put(12, inn + 1, BARREL); m.put(13, inn + 1, BARREL); m.put(18, inn + 1, CRATE)
m.put(39, store + 1, CRATE_APPLE); m.put(43, store + 1, CRATE_CARROT); m.put(44, store + 1, BARREL)
m.put(44, 29, HAY); m.put(36, 29, FIREWOOD)

# ---------------------------------------------------------------- flowers and grass in the open
for y in range(1, H - 1):
    for x in range(1, W - 1):
        if (x, y) in taken or (x, y) not in KEEP_SET or m.top[0][y][x] or m.top[1][y][x]: continue
        r = rnd.random()
        if r < 0.07: m.put(x, y, rnd.choice(GRASS_TUFTS))
        elif r < 0.11: m.put(x, y, rnd.choice(FLOWERS))

# ---------------------------------------------------------------- doors (latched until the interiors are built)
LATCHED = {'Lantern & Lily Inn': ('The door is latched from inside.', '(The inn is not open yet.)'),
           'General Store': ('"Back soon," says a slate on the door.',),
           'Chapel': ('The chapel is quiet. The door is shut.',),
           'Old Henrik\'s House': ('Nobody answers.',), 'Old Bram\'s House': ('Nobody answers.',),
           'Old Marta\'s House': ('Nobody answers.',), 'Cottage': ('The door is locked.',),
           'Farmhouse': ('The door is locked.',)}
for name, (x, y, style) in DOORS.items():
    m.locked_door(name, x, y, LATCHED[name], style=style)

# ---------------------------------------------------------------- signs and the square
m.put(23, 40, SIGNPOST); m.sign('Signpost', 23, 40, ['\\C[6]Lilydale\\C[0]', 'North: Hollow Wood.'])
m.put(27, 3, SIGNPOST); m.sign('Signpost', 27, 3, ['North: Hollow Wood, then Mistveil.',
                                                  'Carved under it, very old: a small rose.'])
m.sign('Notice Board', 31, 18, ['MARKET DAY - every seventh day, in the square.',
                                 'Pinned below, newer: "Has anyone seen Hanna from the villa?"'])
m.sign('Old Well', *WELL_AT, ['The stones are worn smooth where a hundred years of hands have rested.'])
m.add_event('Rose Tree', RX + 2, RY, [page(None, priority=1, commands=text(
    'An old tree with leaves the colour of wine.', 'Children have carved their names into the bark, low down.',
    'One name is carved higher than the others, as if by someone who never grew any taller.'))])

# ---------------------------------------------------------------- people (chapter 7, before the party sets out)
m.npc('Old Bram', 22, 20, 'People1', 6, ('Old Bram:', 'We used to play under this tree, the lot of us.',
      'Funny. I can\'t remember my own wedding, but I remember that.'), direction=8)
m.npc('Old Marta', 28, 22, 'People1', 7, ('Old Marta:', 'The villa folk always came on market day.',
      'Three weeks now. Not even Hanna with her basket.'), direction=6)
m.npc('Old Henrik', 34, 12, 'People4', 6, ('Old Henrik:', 'The Bloodroses? Good neighbours, once.',
      'Then the war took the lady, and the master shut his doors.', 'Sixteen years. He never came down again.'))
m.npc('Shepherd', 27, 9, 'People1', 2, ('Shepherd:', 'Two ewes dead in the north pasture. Not a mark on the wool.',
      'Folk say it\'s the villa. I say it\'s something out of that wood.'), move=1, freq=2)
m.npc('Young Mother', 20, 28, 'People1', 3, ('Young Mother:', 'The priest from the road says the house in the mist is cursed.',
      'My gran says it was the kindest house in the valley.'), move=1, freq=2)
m.npc('Priestess', 37, 11, 'People2', 2, ('Priestess:', 'We still ring the bell for the lady of the villa, every spring.',
      'Someone from the house always used to come to hear it.'))
m.npc('Innkeeper', 17, 12, 'People4', 4, ('Innkeeper:', 'Sorry, travellers - we\'re short of lamp oil and flour both.',
      'The villa\'s cart always brought the good flour. Hasn\'t come.'))
m.npc('Boy', 30, 19, 'People1', 0, ('Boy:', 'Grandpa says a vampire used to give him sweets!', 'I think he\'s making it up.'),
      move=1, speed=4, freq=4)
m.npc('Girl', 12, 23, 'People2', 0, ('Girl:', 'Don\'t go in the wood. The mist eats sound.', 'Mama says so.'),
      move=1, speed=4, freq=4)
m.npc('Farmer', 8, 37, 'People4', 2, ('Farmer:', 'Good soil, this. Too good to leave for the city.'), move=1, freq=2)
m.critter('Cat', 14, 24, 'Nature', 1, 'Cat', 'The cat stretches on the warm stones.', move=1, freq=2)

# ---------------------------------------------------------------- exits
for x in NORTH_X:
    m.add_event('To Hollow Wood %d' % x, x, 0, [L.exit_page(K.HOLLOW_WOOD, K.ARRIVE['hollow_from_lilydale'][1] + x - NORTH_X[0],
                                                             K.ARRIVE['hollow_from_lilydale'][2], 8)], note='<minimap: exit>')

ARRIVALS = [K.ARRIVE['lilydale_from_hollow'][1:3], (SOUTH_X[0], H - 2)]

if __name__ == '__main__':
    out = next((a for a in sys.argv[1:] if not a.startswith('--')), None)
    reach = m.reach([tuple(a) for a in ARRIVALS])
    for name, (x, y, _) in DOORS.items():
        print('%-22s door step' % name, 'ok' if (x, y + 1) in reach else 'NOT REACHABLE')
    for e in m.events[1:]:
        if e['name'].startswith(('Old', 'Shepherd', 'Young', 'Priestess', 'Innkeeper', 'Boy', 'Girl', 'Farmer')):
            if not any((e['x'] + dx, e['y'] + dy) in reach for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                print('npc unreachable', e['name'])
    if out: m.render(out, scale=0.5, grid='--grid' in sys.argv)
    if '--save' in sys.argv:
        m.save(K.LILYDALE, parent_id=K.WORLD)
        print('saved Map%03d' % K.LILYDALE)
