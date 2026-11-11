# MAP066 - Hollow Wood (chapter 7): the first of the two woods between Lilydale and Villa Bloodrose. The road leaves
# the village at the bottom still among green broad-leaf trees and pines; going north the trees thin, lose their
# leaves and twist, the grass dries out and a thin mist starts. Corrupted beasts walk here (the black crystal under the
# villa seeps this far). Halfway, a clearing with a fallen log where the elders stop to rest and talk about the boy
# who waited under the rose tree. Out at the top into Mistveil (MAP067).
# Layout from rm-map-forge (forge_outdoor.js: ground, a ledge of raised ground with stairs, the road through given
# points, trees everywhere else), dressed and linked here. Same seed -> same map.
#   python3 map_hollow_wood.py preview.png [--grid]   -> preview image
#   python3 map_hollow_wood.py --save                 -> write Map066 (editor must be closed)
import sys, os, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import nova_maplib as L
from nova_maplib import page, cmd, text, char
import town_kit as T
import kingdom as K
from forge_outdoor import forge, Tree, A2, A4, BLOCKER

W, H = 40, 50
PF = 'PM_Forest'
# trees: green below, withering above (bands are the rows of the trunk); PM_Forest groupings checked on a render
GREEN = [Tree([(16, 17, 18), (24, 25, 26), (32, 33, 34)], 0.30, (24, H), PF),
         Tree([(40, 41, 42), (48, 49, 50)], 0.25, (22, H), PF),
         Tree([(112, 113), (120, 121)], 0.25, (18, H), PF),                 # pines
         Tree([(114, 115), (122, 123)], 0.22, (18, H), PF),
         Tree(T.BIG_TREE, 0.08, (26, H))]
WITHER = [Tree([(136, 137, 138), (144, 145, 146), (152, 153, 154)], 0.28, (8, 34), PF),   # mossy, half dead
          Tree([(139, 140), (147, 148), (155, 156)], 0.28, (8, 34), PF),
          Tree([(141, 142, 143), (149, 150, 151), (157, 158, 159)], 0.25, (8, 34), PF)]
DEAD = [Tree([(176, 177, 178), (184, 185, 186), (192, 193, 194)], 0.30, (0, 20), PF),
        Tree([(179, 180), (187, 188), (195, 196)], 0.30, (0, 20), PF),
        Tree([(181, 182, 183), (189, 190, 191), (197, 198, 199)], 0.28, (0, 20), PF),
        Tree([(160, 161, 162), (168, 169, 170)], 0.20, (0, 26), PF)]
SMALL = [Tree([(T.TREE_S1,)], 0.05, (20, H)), Tree([(T.BUSH_S,)], 0.04, (16, H)), Tree([(T.STUMP,)], 0.03)]

# the road: in from Lilydale at the bottom, out to Mistveil at the top
ROAD = [(20, 49), (20, 44), (16, 38), (19, 31), (23, 26), (22, 20), (15, 14), (17, 7), (21, 2), (21, 0)]
SIDE = [(19, 31), (28, 34), (33, 37)]                    # a side track east to a hunter's cache
REST = (23, 26)                                          # the clearing where the elders rest
CACHE = (34, 37)
LOG = (25, 24)
SIGN = (22, 46)


def disc(c, r):
    return [(c[0] + dx, c[1] + dy) for dx in range(-r, r + 1) for dy in range(-r, r + 1) if dx * dx + dy * dy <= r * r + 1]


KEEP = disc(REST, 3) + disc(CACHE, 2) + [SIGN, (SIGN[0], SIGN[1] + 1)] + [(x, H - 1) for x in (19, 20, 21)] + \
       [(x, 0) for x in (20, 21, 22)]

m = forge(K.NAMES[K.HOLLOW_WOOD], W, H, seed='hollow-wood-2', ground=A2(0), road=A2(1), hill=A4(32),
          stairs=L.A5 + 27, patch=(A2(9), 0.75, 9), zones=[(A2(20), -10, 18)],
          params={'hills': 0.12, 'hillLevels': 1, 'hillScale': 22, 'cliffHeight': 2, 'scale': 18, 'shadow': True},
          paths=[(ROAD, 2), (SIDE, 1)], keep=KEEP, trees=GREEN + WITHER + DEAD + SMALL)
m.note = '<outdoor>'
m.bgm = {'name': 'Field2', 'pan': 0, 'pitch': 85, 'volume': 65}
m.bgs = {'name': 'Wind', 'pan': 0, 'pitch': 90, 'volume': 30}
rnd = random.Random(66)

# ---------------------------------------------------------------- edges: no way out but the road
for x in range(W):
    for y in (0, H - 1):
        if not m.is_road(x, y) and not m.has_object(x, y): m.put(x, y, BLOCKER)
for y in range(H):
    for x in (0, W - 1):
        if not m.is_road(x, y) and not m.has_object(x, y): m.put(x, y, BLOCKER)

# ---------------------------------------------------------------- dressing on the open ground
DRY = (T.GRASS_TUFTS[0], T.GRASS_TUFTS[1], 175, 183)     # green tufts low down, dry grass (Outside_B) higher up
for y in range(1, H - 1):
    for x in range(1, W - 1):
        if m.is_road(x, y) or m.has_object(x, y) or m.is_face(x, y) or (x, y) in KEEP[:len(disc(REST, 3))]: continue
        r = rnd.random()
        if r < 0.10: m.put(x, y, rnd.choice(DRY[:2] if y > 30 else DRY))
        elif r < 0.14 and y > 28: m.put(x, y, rnd.choice(T.FLOWERS))
        elif r < 0.16: m.put(x, y, rnd.choice((T.FERN, T.ROCKS, 177)))   # 177: a dead shrub
m.put(*LOG, T.LOG); m.put(LOG[0] + 2, LOG[1] + 1, T.STUMP)
m.put(*SIGN, T.SIGNPOST)

# ---------------------------------------------------------------- events
m.sign('Signpost', *SIGN, ['North: \\C[6]Mistveil\\C[0], then the Bloodrose house.',
                           'Someone has added in chalk: "Don\'t."'])
m.add_event('Fallen Log', *LOG, [page(None, priority=1, commands=text(
    'A fallen trunk worn smooth on top, as if people have sat here', 'for a very long time.'))])
loot = [cmd(250, [{'name': 'Item3', 'volume': 80, 'pitch': 100, 'pan': 0}]), cmd(126, [1, 0, 0, 3]),
        *text('Found 3 \\C[6]Potion\\C[0] in an old hunter\'s cache!'), cmd(123, ['A', 0])]
m.add_event('Hunter\'s Cache', *CACHE, [
    page(char('!Chest', 0), commands=loot, priority=1, walk_anim=False),
    page(char('!Chest', 0, 8), commands=text('Empty.'), priority=1, walk_anim=False,
         cond={'selfSwitchValid': True, 'selfSwitchCh': 'A'})])
for x in (x for x in range(W) if m.is_road(x, H - 1)):
    m.add_event('To Lilydale %d' % x, x, H - 1, [L.exit_page(K.LILYDALE, K.ARRIVE['lilydale_from_hollow'][1] + x - 20,
                                                             K.ARRIVE['lilydale_from_hollow'][2], 2)],
                note='<minimap: exit>')
for x in (x for x in range(W) if m.is_road(x, 0)):
    m.add_event('To Mistveil %d' % x, x, 0, [L.exit_page(K.MISTVEIL, K.ARRIVE['mistveil_from_hollow'][1] + x - 21,
                                                         K.ARRIVE['mistveil_from_hollow'][2], 8)],
                note='<minimap: exit>')

ARRIVALS = [K.ARRIVE['hollow_from_lilydale'][1:3], K.ARRIVE['hollow_from_mistveil'][1:3]]

if __name__ == '__main__':
    out = next((a for a in sys.argv[1:] if not a.startswith('--')), None)
    reach = m.reach([tuple(a) for a in ARRIVALS])
    for name, p in (('rest', REST), ('cache', (CACHE[0], CACHE[1] + 1)), ('top', ARRIVALS[1]), ('sign', (SIGN[0] - 1, SIGN[1]))):
        print(name, p, 'reachable' if p in reach else 'NOT REACHABLE')
    if out: m.render(out, scale=0.5, grid='--grid' in sys.argv)
    if '--save' in sys.argv:
        m.save(K.HOLLOW_WOOD, parent_id=K.WORLD)
        print('saved Map%03d' % K.HOLLOW_WOOD)
