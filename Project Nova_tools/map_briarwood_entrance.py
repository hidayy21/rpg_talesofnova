# MAP030 - Briarwood - Entrance: the forest edge between the World Map and Briarwood (MAP029). A winding dirt track
# under broad-leaf canopies: in at the bottom, out at the top into Briarwood; a side path climbs stone steps to a
# ledge on the right with a chest, and a healing crystal waits by the track just before Briarwood.
#   python map_briarwood_entrance.py preview.png   -> preview image
#   python map_briarwood_entrance.py --save        -> write MAP030 (RPG Maker MV must be closed); prologue.py --save
#                                                     also runs it, and links the World Map and Briarwood to it
import sys, math, random, json
import nova_maplib as L
from nova_maplib import page, cmd, text, char
import town_kit as T
import kingdom as K

import prologue as P
ENTRANCE, START, TOP_OUT = P.ENTRANCE, P.ENTRANCE_START, P.ENTRANCE_TOP   # in from the World Map / back out of Briarwood
W, H = 26, 30
CRYSTAL, CHEST = (19, 5), (22, 10)
SIGN = (14, 25)                     # by the track, read from the right
BLOCKER = 767                                           # Nova_Market_D's last cell: empty, made impassable below
LEDGE, CLIFF, STEPS = ('A4', 32), ('A4', 40), ('A5', 27)  # Ledge A (meadow), Cliff A, Stairs (meadow)
CHEST_ITEMS = ((5, 2), (2, 2))                          # 2 Hi-Potion, 2 Magic Water

# the track: entrance (bottom) -> lower clearing -> middle clearing -> crystal clearing -> Briarwood (top)
TRACK = [(16, 30), (15.5, 25), (12.5, 21), (11.5, 16), (13, 11.5), (16, 7.5), (17, 3.5), (17, -1)]
WEST = [(12, 21), (8, 19), (5.5, 15.5)]                 # a dead-end glade to the west
EAST = [(13, 20.5), (18, 19.5), (21, 18), (21, 13)]     # to the steps and the ledge
CLEARINGS = [((12.5, 21.5), 4.3, 2.4), ((12.5, 13.5), 3.6, 2.4), ((17.5, 5.5), 3.2, 2.2), ((5.5, 15), 2.8, 2.3)]
PLATEAU = (18, 8, W - 1, 14)        # x0, y0, x1, y1 of the ledge top; its cliff face is the two rows below
LEDGE_CLEARING = ((21.5, 11.5), 2.6, 2.4)


def seg_dist(p, a, b):
    (px, py), (ax, ay), (bx, by) = p, a, b
    dx, dy = bx - ax, by - ay
    t = max(0, min(1, ((px - ax) * dx + (py - ay) * dy) / (dx * dx + dy * dy)))
    return math.hypot(px - ax - t * dx, py - ay - t * dy)


def line_dist(p, pts): return min(seg_dist(p, pts[i], pts[i + 1]) for i in range(len(pts) - 1))
def in_ellipse(x, y, e): (cx, cy), rx, ry = e; return ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 < 1


def on_plateau(x, y): return PLATEAU[0] <= x <= PLATEAU[2] and PLATEAU[1] <= y <= PLATEAU[3]
def cliff_face(x, y): return PLATEAU[0] <= x <= PLATEAU[2] and PLATEAU[3] < y <= PLATEAU[3] + 2


def walkable(x, y):
    p = (x, y)
    if cliff_face(x, y): return x == EAST[-1][0]                       # only the steps
    if on_plateau(x, y): return in_ellipse(x, y, LEDGE_CLEARING) or (x == EAST[-1][0] and y >= 12)
    wobble = 0.35 * math.sin(y * 0.9 + x * 0.4)
    return (line_dist(p, TRACK) < 1.7 + wobble or line_dist(p, WEST) < 1.3 + wobble or line_dist(p, EAST) < 1.2
            or any(in_ellipse(x, y, e) for e in CLEARINGS))


LONE_TREES = ((15, 13), (4, 14), (23, 12))      # top-left of a 2x2 tree standing in the open


def plant_forest(m, walk, rnd):
    """Whole broad-leaf trees (2x2: crown row on layer 3, trunk row on layer 2) on plain grass, in rows two apart
    and shifted by one every other row, so each crown shows round and complete. A tree only needs its trunk row on
    the forest floor: its crown may hang over the open ground above, which rounds off the forest's stepped edge.
    A second pass fills the gaps the grid leaves along the edges."""
    inside = lambda x, y: 0 <= x < W and 0 <= y < H
    forest = lambda x, y: inside(x, y) and (x, y) not in walk and not cliff_face(x, y)
    clear = {CRYSTAL, CHEST, SIGN, START, TOP_OUT} | {(x + dx, y + dy) for x, y in LONE_TREES for dx in (0, 1) for dy in (0, 1)}
    trunks, crowns = set(), set()
    (a, b), (c, d) = T.BIG_TREE

    def fits(x, y):
        for dx in (0, 1):
            tx, ty = x + dx, y + 1
            if 0 <= tx < W and ty < H and (not forest(tx, ty) or (tx, ty) in trunks): return False
            cx, cy = x + dx, y
            if inside(cx, cy) and ((cx, cy) in crowns or (cx, cy) in clear or cliff_face(cx, cy)): return False
        return any(inside(x + dx, y + dy) for dx in (0, 1) for dy in (0, 1))

    def plant(x, y):
        for dx, top, bottom in ((0, a, c), (1, b, d)):
            if inside(x + dx, y): m.put(x + dx, y, top, 3); crowns.add((x + dx, y))
            if inside(x + dx, y + 1): m.put(x + dx, y + 1, bottom, 2); trunks.add((x + dx, y + 1))

    for y in range(-1, H, 2):
        for x in range(((y + 1) // 2) % 2 - 1, W, 2):
            if fits(x, y): plant(x, y)
    for y in range(H):
        for x in range(W):
            if forest(x, y) and (x, y) not in trunks and (x, y) not in crowns:
                for tx, ty in ((x - 1, y - 1), (x, y - 1), (x - 1, y), (x, y)):
                    if fits(tx, ty):
                        plant(tx, ty)
                        break
    # edge cells no whole tree fits on (one-tile strips, notches) stay open ground
    bare = [(x, y) for y in range(H) for x in range(W) if forest(x, y) and (x, y) not in trunks and (x, y) not in crowns
            and any((x + dx, y + dy) in walk for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))]
    for x, y in bare:
        if on_plateau(x, y): m.cell(x, y, LEDGE)
        walk.add((x, y))
    # the ground under the trees is the same grass as the open ground (no tile-shaped patches between the crowns);
    # an invisible blocker on layer 2 keeps the player out wherever no trunk does already (the crown rows)
    for y in range(H):
        for x in range(W):
            if forest(x, y) and (x, y) not in trunks: m.put(x, y, BLOCKER)


def build():
    m = T.Town(W, H, 'Briarwood - Entrance', 'Briarwood', ground=T.GRASS)
    m.note = '<outdoor>'
    m.bgm = {'name': 'Field2', 'pan': 0, 'pitch': 100, 'volume': 70}
    m.bgs = {'name': 'Wind', 'pan': 0, 'pitch': 100, 'volume': 25}
    walk = {(x, y) for y in range(H) for x in range(W) if walkable(x, y)}
    rnd = random.Random(30)
    for y in range(H):
        for x in range(W):
            if cliff_face(x, y):
                m.cell(x, y, STEPS if (x, y) in walk else CLIFF)
            elif (x, y) in walk:
                if on_plateau(x, y): m.cell(x, y, LEDGE)
                elif line_dist((x, y), TRACK) < 0.95 or any(in_ellipse(x, y, ((cx, cy), rx * 0.5, ry * 0.45))
                                                             for (cx, cy), rx, ry in CLEARINGS[:3]):
                    m.cell(x, y, T.DIRT)            # one worn track, widening in the clearings (no stray patches)
                else: m.cell(x, y, T.GRASS)
            else:
                m.cell(x, y, T.GRASS)
    plant_forest(m, walk, rnd)

    # lone broad-leaf trees in the open, undergrowth along the edges (never on the track)
    for x, y in LONE_TREES:
        m.big_tree(x, y, T.BIG_TREE)
    keep = {START, TOP_OUT, CRYSTAL, CHEST, SIGN, (CRYSTAL[0], CRYSTAL[1] + 1), (CHEST[0], CHEST[1] + 1)}
    trees = {(x + dx, y + dy) for x, y in LONE_TREES for dx in (0, 1) for dy in (0, 1)}
    for (x, y) in sorted(walk):
        if (x, y) in keep or (x, y) in trees or line_dist((x, y), TRACK) < 1.2 or line_dist((x, y), EAST) < 0.8 \
                or line_dist((x, y), WEST) < 0.8 or cliff_face(x, y) or y in (0, H - 1):
            continue
        r = rnd.random()
        if r < 0.10: m.put(x, y, rnd.choice(T.GRASS_TUFTS))
        elif r < 0.16: m.put(x, y, rnd.choice(T.FLOWERS))
        elif r < 0.19: m.put(x, y, rnd.choice((T.FERN, T.BUSH_S, T.STUMP, T.ROCKS)))
    for (x, y), tile in (((6, 16), T.FLOWER_BUSH), ((4, 17), T.FLOWERS[2]), ((7, 14), T.FLOWERS[0]), ((11, 23), T.LOG),
                         ((20, 9), T.BOULDER), ((24, 10), T.FERN), ((10, 12), T.STUMP)):
        m.put(x, y, tile)

    # exits: down to the World Map, up into Briarwood (only on the open track cells of the edge rows)

    for x in (x for x in range(W) if (x, H - 1) in walk):
        m.add_event('To World Map %d' % x, x, H - 1, [L.exit_page(K.WORLD, P.WORLD_WOOD_OUT[0], P.WORLD_WOOD_OUT[1], 2)],
                    note='<minimap: exit>')
    for x in (x for x in range(W) if (x, 0) in walk):
        m.add_event('To Briarwood %d' % x, x, 0, [L.exit_page(P.BRIARWOOD, P.WOOD_START[0], P.WOOD_START[1], 8)],
                    note='<minimap: exit>')

    m.put(*SIGN, T.SIGNPOST)
    m.sign('Signpost', *SIGN, ['\\C[6]Briarwood\\C[0]', 'The old cart road, west of the capital.',
                               'Travellers: keep to the road after dark.'])
    # the crystal: full HP and MP for the whole party, as often as you like
    m.add_event('Healing Crystal', CRYSTAL[0], CRYSTAL[1], [page(char('!Crystal', 2), step_anim=True, walk_anim=False, commands=[
        cmd(250, [{'name': 'Recovery', 'volume': 80, 'pitch': 100, 'pan': 0}]), cmd(212, [-1, 43, False]),
        cmd(224, [[180, 255, 200, 120], 30, True]), cmd(314, [0, 0]),
        *text('The crystal hums softly, and its green light', 'washes over the party.', '\\C[6]HP and MP fully restored.\\C[0]')])])
    # the chest on the ledge
    open_lid = [L.rt(L.R_TURN_LEFT), L.rt(L.R_WAIT, 3), L.rt(L.R_TURN_RIGHT), L.rt(L.R_WAIT, 3), L.rt(L.R_TURN_UP),
                {'code': 0, 'parameters': []}]
    names = {5: 'Hi-Potion', 2: 'Magic Water'}
    loot = [cmd(126, [i, 0, 0, n]) for i, n in CHEST_ITEMS]
    found = ' and '.join('%d \\C[6]%s\\C[0]' % (n, names[i]) for i, n in CHEST_ITEMS)
    m.add_event('Chest', CHEST[0], CHEST[1], [
        page(char('!Chest', 4), walk_anim=False, commands=[
            cmd(250, [{'name': 'Chest1', 'volume': 80, 'pitch': 100, 'pan': 0}]),
            cmd(205, [0, {'list': open_lid, 'repeat': False, 'skippable': False, 'wait': True}]),
            *loot, *text('Found %s!' % found), cmd(123, ['A', 0])]),
        page(char('!Chest', 4, direction=8), walk_anim=False, cond={'selfSwitchValid': True, 'selfSwitchCh': 'A'})])
    return m


def blocker_flags():
    """The invisible blocker (an empty cell of the D sheet) is impassable. An older version of this map used the
    Bush autotile (Outside_A2) as an impassable forest floor: its flags go back to the default walk-through bush."""
    path = L.DATA + 'Tilesets.json'
    sets = json.load(open(path, encoding='utf8'))
    flags = sets[T.OUTSIDE]['flags']
    flags[BLOCKER] = 0x60F
    bush = L.A2 + 4 * 48
    for t in range(bush, bush + 48): flags[t] &= ~0x0F
    with open(path, 'w', encoding='utf8', newline='') as f:
        f.write('[\n' + ',\n'.join(json.dumps(s, ensure_ascii=False, separators=(',', ':')) for s in sets) + '\n]')


def save():
    blocker_flags()
    build().save(ENTRANCE, parent_id=K.WORLD, order=ENTRANCE)


if __name__ == '__main__':
    out = next((a for a in sys.argv[1:] if not a.startswith('--')), None)
    if out: build().render(out, scale=0.5, grid=True)
    if '--save' in sys.argv:
        save()
        print('Briarwood - Entrance saved')
