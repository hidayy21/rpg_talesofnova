# MAP067 - Mistveil (chapter 7): the dying heart of the wood before Villa Bloodrose. Most trees are bare and twisted,
# packed close; a few pines and oaks still hold on, fewer the nearer the villa. Withered grass, a thick mist that breathes (NovaAtmosphere <fog mystery>). The road
# winds and forks; the side ways end in nothing, or in something worse:
#   - west: a dead end with a traveller's pack (Magic Water);
#   - east: a shard of black crystal half sunk in the earth, the dead ground spreading from it (the corruption under
#     the villa reaches this far - Diana and Mira know it from chapter 6);
#   - north-west: a loop of trees that all look the same, and a torn dark cloak caught on the thorns (the Order came
#     this way);
#   - north-east: an old way-shrine with a healing crystal, the last rest before the villa.
# Out at the top onto the road to the villa bridge (Map048), in at the bottom from Hollow Wood (MAP066).
# Layout from rm-map-forge (forge_outdoor.js), dressed and linked here. Same seed -> same map.
#   python3 map_mistveil.py preview.png [--grid]   -> preview image
#   python3 map_mistveil.py --save                 -> write Map067 (editor must be closed)
import sys, os, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import nova_maplib as L
from nova_maplib import page, cmd, text, char
import town_kit as T
import kingdom as K
from forge_outdoor import forge, Tree, A2, BLOCKER

W, H = 44, 50
PF = 'PM_Forest'
NN = lambda n: L.ext('Nova_Nature', n)
DEAD = [Tree([(176, 177, 178), (184, 185, 186), (192, 193, 194)], 0.30, None, PF),
        Tree([(179, 180), (187, 188), (195, 196)], 0.30, None, PF),
        Tree([(181, 182, 183), (189, 190, 191), (197, 198, 199)], 0.28, None, PF),
        Tree([(160, 161, 162), (168, 169, 170)], 0.20, None, PF),
        Tree([(136, 137, 138), (144, 145, 146), (152, 153, 154)], 0.15, (36, H), PF),   # a few still mossy near the
        Tree([(139, 140), (147, 148), (155, 156)], 0.15, (36, H), PF),                  # way in from Hollow Wood
        Tree([(163,), (171,)], 0.10, None, PF)]
# the living ones (a quarter or so of the trees): pines, an oak here and there; none in the last stretch to the villa
LIVING = [Tree([(112, 113), (120, 121)], 0.16, (10, H), PF),                         # dark pine
          Tree([(114, 115), (122, 123)], 0.10, (14, H), PF),                         # green pine
          Tree([(16, 17, 18), (24, 25, 26), (32, 33, 34)], 0.07, (24, H), PF)]       # oak
TREES = DEAD[:3] + LIVING[:1] + DEAD[3:5] + LIVING[1:] + DEAD[5:]   # tried in this order at every cell
FILL = (177, 177, T.BOULDER, T.BOULDER_B, NN(12), NN(13), T.STUMP)   # blocking: closes the gaps between the trees

ROAD = [(21, 49), (21, 44), (13, 40), (10, 33), (18, 29), (27, 31), (33, 25), (30, 18), (22, 15), (16, 10), (21, 6)]
TOP = [(20, 6), (20, 0)]                                # the last stretch as wide as the villa road (x 20-22)
WEST = [(10, 33), (4, 30), (4, 24)]                     # dead end: the pack
EAST = [(27, 31), (36, 35), (38, 41)]                   # the black crystal
LOOP = [(22, 15), (9, 15), (6, 9)]                      # the cloak
SHRINE_WAY = [(30, 18), (37, 13), (39, 7)]              # the way-shrine
PACK, SHARD, CLOAK, CRYSTAL = (4, 23), (38, 42), (6, 8), (39, 6)
SIGN = (19, 45)


def disc(c, r):
    return [(c[0] + dx, c[1] + dy) for dx in range(-r, r + 1) for dy in range(-r, r + 1) if dx * dx + dy * dy <= r * r + 1]


GLADES = disc(PACK, 1) + disc(SHARD, 2) + disc(CLOAK, 1) + disc(CRYSTAL, 2)
KEEP = GLADES + [SIGN, (SIGN[0], SIGN[1] + 1)] + [(x, 0) for x in (20, 21, 22)] + [(x, H - 1) for x in (20, 21, 22)]

m = forge(K.NAMES[K.MISTVEIL], W, H, seed='mistveil-4', ground=A2(20), road=A2(1), overlay=(A2(12), 0.74, 6),
          params={'hills': 0, 'scale': 16, 'shadow': True},
          paths=[(ROAD, 2), (TOP, 3), (WEST, 1), (EAST, 1), (LOOP, 1), (SHRINE_WAY, 1)], keep=KEEP, trees=TREES)
m.note = '<outdoor>'
m.bgm = {'name': 'Dungeon2', 'pan': 0, 'pitch': 80, 'volume': 55}
m.bgs = {'name': 'Wind', 'pan': 0, 'pitch': 70, 'volume': 45}
rnd = random.Random(67)

# ---------------------------------------------------------------- close every gap between the trees: the way is the
# road (a labyrinth, not a field); the glades at the ends stay open. Edge cells are closed the same way.
glade = set(GLADES) | {SIGN, (SIGN[0], SIGN[1] + 1)}
for y in range(H):
    for x in range(W):
        if m.is_road(x, y) or m.has_object(x, y) or (x, y) in glade: continue
        near_road = any(m.is_road(x + dx, y + dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1))
        m.put(x, y, rnd.choice(FILL) if near_road or rnd.random() < 0.35 else BLOCKER)
        if not near_road and rnd.random() < 0.5: m.put(x, y, rnd.choice((175, 183)), 3)   # dry grass over the blocker
# withered dressing on the road verges and in the glades
for x, y in glade:
    if m.inb(x, y) and not m.is_road(x, y) and rnd.random() < 0.3: m.put(x, y, rnd.choice((175, 183)))
m.put(*SIGN, T.SIGNPOST)

# ---------------------------------------------------------------- events
m.sign('Signpost', *SIGN, ['The letters are almost gone.', '"...BLOODROSE... KEEP TO THE R..."'])
loot = [cmd(250, [{'name': 'Item3', 'volume': 80, 'pitch': 100, 'pan': 0}]), cmd(126, [2, 0, 0, 2]),
        *text('A traveller\'s pack, long abandoned.', 'Found 2 \\C[6]Magic Water\\C[0]!'), cmd(123, ['A', 0])]
m.add_event('Abandoned Pack', *PACK, [
    page(None, commands=loot, priority=1),
    page(None, commands=text('The pack is empty now.'), priority=1, cond={'selfSwitchValid': True, 'selfSwitchCh': 'A'})])
m.put(*PACK, T.CRATE_GRAIN)
m.add_event('Black Crystal', *SHARD, [page(char('!Crystal', 0, 6), priority=1, step_anim=True, walk_anim=False, commands=text(
    'A shard of black crystal, half sunk in the earth.', 'The grass around it is not withered. It is dead - every blade, in a ring.',
    'It is the same dark crystal as the ones from the shrine in the wood.'))],
    note='<light: 90, #6a4a8a>')
m.add_event('Torn Cloak', *CLOAK, [page(None, priority=0, commands=text(
    'A strip of dark cloth caught on the thorns. Good cloth - not a woodsman\'s.',
    'Someone came this way, and did not want to be seen doing it.'))])
m.put(*CLOAK, 177)
m.add_event('Healing Crystal', *CRYSTAL, [page(char('!Crystal', 2), step_anim=True, walk_anim=False, commands=[
    cmd(250, [{'name': 'Recovery', 'volume': 80, 'pitch': 100, 'pan': 0}]), cmd(212, [-1, 43, False]),
    cmd(224, [[180, 255, 200, 120], 30, True]), cmd(314, [0, 0]),
    *text('An old way-shrine. The crystal in it still glows, faintly,', 'as if it has been waiting.',
          '\\C[6]HP and MP fully restored.\\C[0]')])])
for x in (x for x in range(W) if m.is_road(x, H - 1)):
    m.add_event('To Hollow Wood %d' % x, x, H - 1, [L.exit_page(K.HOLLOW_WOOD, K.ARRIVE['hollow_from_mistveil'][1] + x - 21,
                                                                K.ARRIVE['hollow_from_mistveil'][2], 2)],
                note='<minimap: exit>')
for x in (x for x in range(W) if m.is_road(x, 0)):
    m.add_event('To Villa Bloodrose %d' % x, x, 0, [L.exit_page(K.VILLA_BLOODROSE, K.ARRIVE['bloodrose_from_world'][1] + x - 21,
                                                               K.ARRIVE['bloodrose_from_world'][2], 8)],
                note='<minimap: exit>')

ARRIVALS = [K.ARRIVE['mistveil_from_hollow'][1:3], K.ARRIVE['mistveil_from_bloodrose'][1:3]]

if __name__ == '__main__':
    out = next((a for a in sys.argv[1:] if not a.startswith('--')), None)
    reach = m.reach([tuple(a) for a in ARRIVALS])
    for name, p in (('pack', (PACK[0], PACK[1] + 1)), ('shard', (SHARD[0], SHARD[1] - 1)), ('cloak', (CLOAK[0], CLOAK[1] + 1)),
                    ('crystal', (CRYSTAL[0], CRYSTAL[1] + 1)), ('top', ARRIVALS[1]), ('bottom', ARRIVALS[0])):
        print(name, p, 'reachable' if p in reach else 'NOT REACHABLE')
    print('top exits', [x for x in range(W) if m.is_road(x, 0)], 'bottom exits', [x for x in range(W) if m.is_road(x, H - 1)])
    if out: m.render(out, scale=0.5, grid='--grid' in sys.argv)
    if '--save' in sys.argv:
        m.save(K.MISTVEIL, parent_id=K.WORLD)
        print('saved Map%03d' % K.MISTVEIL)
