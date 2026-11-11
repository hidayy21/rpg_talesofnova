# Beneath Villa Bloodrose - the dungeon the party falls into from the ballroom and has to climb out of. Layouts come
# from rm-map-forge (forge_bloodrose_depths.js runs rm-map-forge/core.js with fixed seeds); dressed and linked here.
#
#   The fight with David in the ballroom (Map061) ends with switch 13 on: the floor under the party gives way.
#   MAP062 - Bloodrose Cellars (B1): they land in a pit room where others fell before them (bones, the skeletons that
#            walk here). The steps up to the hall are barred from above. The way down is behind an iron grate - the
#            lever that raises it is in a far room (switch 14).
#   MAP063 - The Old Foundations (B2): stonework older than the house. The sealed gate in the central hall wakes when
#            four braziers are lit in the order the oath was kept - KNEEL, SWEAR, PLANT, KINDLE (variable 10; a wrong
#            brazier puts them all out). The steles in the first hall tell the story; the gate names the words.
#   MAP064 - The Rose Way: a passage of earth climbing to the garden. Its roots are the Bloodrose tree's. At the top a
#            slab opens under the tree (switch 15) - from then on the way is open both ways (Map048, patch_villa_rose_way.py).
#
# Same seeds -> same maps. Dungeon tileset (4); props from Dungeon_B/C plus Inside_B through L.ext.
#   python map_villa_bloodrose_depths.py preview.png [--grid]   -> preview_62.png ... preview_64.png
#   python map_villa_bloodrose_depths.py --save                 -> write Map062-064 (editor must be closed)
import sys, os, json, subprocess, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import nova_maplib as L
from nova_maplib import page, cmd, text, char, tile_image
import kingdom as K

HERE = os.path.dirname(os.path.abspath(__file__))
DUNGEON = 4
IB = lambda n: L.ext('Inside_B', n)
DC = lambda n: 256 + n                                       # Dungeon_C is this tileset's own C sheet
INVISIBLE_WALL = L.ext('Avy_Ship_B3', 1)

# ---------------------------------------------------------------- tiles (checked on 1.3-1.6x crops)
STAIRS_UP = ((2, 3), (10, 11))                               # stone steps up into a dark doorway, 2x2
LADDER_DOWN = 29                                             # wooden ladder into a dark hole (floor)
LADDER_UP = (5, 13)                                          # wooden ladder up the wall, 1x2
CRATES = (220, 221, 228, 229, 236, 237)
JAR, POT, BARREL, BARREL_OPEN, BROKEN_CRATE = 230, 231, 238, 239, 222
PILLAR_ROUND, PILLAR_SQUARE, PILLAR_FLUTED = (81, 89), (80, 88), (82, 90)
BROKEN_PILLARS = (96, 97, 98, 102, 103)                      # (99 is mossy, 100 icy)
RUBBLE = (104, 108)                                          # grey and brown (105/106 are mossy and icy)
PEBBLES, ROCK, ROCK_GREY, PETALS = (48, 49), 56, 57, 54
STELE = (168, 176)
STATUE_ANGEL, STATUE_GODDESS = (184, 192), (186, 194)
GATE_DARK = ((170, 171, 172), (178, 179, 180))               # the sealed gate asleep
GATE_LIT = ((173, 174, 175), (181, 182, 183))                # ... and awake
DARK, DARK_ARCH = 147, 151                                   # black opening / its round top
CIRCLE_BLUE = ((83, 84, 85), (91, 92, 93), (99, 100, 101))   # Dungeon_C, on the floor
PLAQUE = 145                                                 # carved stone tablet, on a wall face
GRATE = (252, 253)                                           # iron bars
BONES, BONES_B, SKELETON = 248, 249, 250
ROOTS, VINES = (153, 161), (152, 160)                        # hanging from a wall face, 1x2
WINE_RACK, BOTTLES = (53, 61), (54, 62)                      # Inside_B, 1x2
SACKS = 250                                                  # Inside_B
COBWEB = 144                                                 # Dungeon_B
BRAZIER = '!Other2'                                          # index 7: 2 = yellow flame, 4 = blue, 8 = cold
LEVER = '!Switch1'                                           # index 0: 2 = up, 6 = pulled
ITEM_NAMES = {1: 'Potion', 2: 'Magic Water', 5: 'Hi-Potion', 6: 'Mega Potion', 7: 'Elixir'}
BLUE_LIGHT = '<light: 130, #7fa8ff, flicker>'


def se(name, volume=80, pitch=100, indent=0):
    return cmd(250, [{'name': name, 'volume': volume, 'pitch': pitch, 'pan': 0}], indent)


def shift(cmds, k):
    return [dict(c, indent=c['indent'] + k) for c in cmds]


def if_var(var, value, then, else_=(), op=0, indent=0):
    """Conditional branch on a variable (op 0 '=', 1 '>='), with an else part."""
    out = [cmd(111, [1, var, 0, value, op], indent)] + shift(list(then), indent + 1) + [cmd(0, [], indent + 1)]
    out += [cmd(411, [], indent)] + shift(list(else_), indent + 1) + [cmd(0, [], indent + 1)]
    return out + [cmd(412, [], indent)]


def choice(labels, branches, indent=0):
    out = [cmd(102, [labels, len(labels) - 1, 0, 2, 0], indent)]
    for i, (label, body) in enumerate(zip(labels, branches)):
        out += [cmd(402, [i, label], indent)] + shift(list(body), indent + 1) + [cmd(0, [], indent + 1)]
    return out + [cmd(404, [], indent)]


def comment(s): return cmd(108, [s])


def forge():
    """Run the rm-map-forge generator (Node) and return the levels: width, height, data (6 layers) and cls
    (0 floor, 1 wall face, 2 wall top) per cell."""
    with tempfile.TemporaryDirectory() as tmp:
        out = os.path.join(tmp, 'levels.json')
        subprocess.run(['node', os.path.join(HERE, 'forge_bloodrose_depths.js'), out], check=True,
                       stdout=subprocess.DEVNULL)
        return json.load(open(out, encoding='utf8'))


class ForgeMap(L.MapBuilder):
    """A map whose tiles come from rm-map-forge; put/cell/events work as on any MapBuilder and are laid over it."""

    def __init__(self, level, mid):
        super().__init__(level['width'], level['height'], DUNGEON, *K.NAMES[mid])
        self.base, self.cls = level['data'], level['cls']
        self.taken = set()

    def c(self, x, y):
        return self.cls[y * self.w + x] if 0 <= x < self.w and 0 <= y < self.h else 2

    def tile_data(self):
        w, h, N = self.w, self.h, self.w * self.h
        out = list(self.base)
        for z in (0, 1):
            for y in range(h):
                for x in range(w):
                    v = self.auto[z][y][x]
                    if v: out[z * N + y * w + x] = (L.A5 + v[1]) if v[0] == 'A5' else v[1]
                    if self.top[z][y][x]: out[(2 + z) * N + y * w + x] = self.top[z][y][x]
        return out

    # -- rooms: the generator's rectangles, found again as blocks of floor at least 3x3
    def rooms(self):
        w, h = self.w, self.h
        core = {(x, y) for y in range(1, h - 1) for x in range(1, w - 1)
                if all(self.c(x + dx, y + dy) == 0 for dx in (-1, 0, 1) for dy in (-1, 0, 1))}
        out, seen = [], set()
        for s in sorted(core, key=lambda p: (p[1], p[0])):
            if s in seen: continue
            comp, stack = [], [s]
            seen.add(s)
            while stack:
                x, y = stack.pop(); comp.append((x, y))
                for n in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                    if n in core and n not in seen: seen.add(n); stack.append(n)
            xs, ys = [p[0] for p in comp], [p[1] for p in comp]
            r = Room(min(xs) - 1, min(ys) - 1, max(xs) + 1, max(ys) + 1)
            if r.w >= 4 and r.h >= 3: out.append(r)
        return out

    def mouths(self, r):
        """Floor cells in the ring just outside the room: the corridor mouths, grouped into openings."""
        ring = {(x, y) for x in range(r.x0 - 1, r.x1 + 2) for y in range(r.y0 - 1, r.y1 + 2)
                if not (r.x0 <= x <= r.x1 and r.y0 <= y <= r.y1) and self.c(x, y) == 0}
        groups, seen = [], set()
        for p in sorted(ring):
            if p in seen: continue
            g, stack = [], [p]; seen.add(p)
            while stack:
                x, y = stack.pop(); g.append((x, y))
                for n in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                    if n in ring and n not in seen: seen.add(n); stack.append(n)
            groups.append(sorted(g))
        return groups

    def openings(self, r):
        """The corridor mouths and their neighbours: keep them clear of props."""
        keep = set()
        for g in self.mouths(r):
            for x, y in g:
                for dx in (-1, 0, 1):
                    for dy in (-1, 0, 1): keep.add((x + dx, y + dy))
        return keep

    def wall_slot(self, r, width):
        """Left x of `width` columns of the room's back wall that are whole face (two rows) - no corridor mouth -
        nearest the middle of the room, or None."""
        xs = [x for x in range(r.x0, r.x1 - width + 2)
              if all(self.c(x + k, r.y0 - 1) == 1 and self.c(x + k, r.y0 - 2) == 1 for k in range(width))]
        return min(xs, key=lambda x: abs(x + (width - 1) / 2 - (r.x0 + r.x1) / 2)) if xs else None

    def distances(self, start):
        dist, q = {start: 0}, [start]
        for p in q:
            x, y = p
            for n in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                if n not in dist and self.c(*n) == 0: dist[n] = dist[p] + 1; q.append(n)
        return dist

    # -- placing
    def free(self, x, y, keep=()):
        return self.c(x, y) == 0 and (x, y) not in self.taken and (x, y) not in keep

    def prop(self, x, y, tile, keep=(), layer=2):
        if not self.free(x, y, keep): return False
        self.put(x, y, tile, layer); self.taken.add((x, y)); return True

    def tall(self, x, y, pair, keep=()):
        """1x2 object standing on (x, y): its top on the upper layer one row up (over floor or wall face)."""
        if not self.free(x, y, keep): return False
        self.put(x, y - 1, pair[0], 3); self.put(x, y, pair[1]); self.taken.update({(x, y), (x, y - 1)}); return True

    def on_wall(self, x, y, pair):
        """1x2 thing on the wall face rows above a room's top floor row y."""
        self.put(x, y - 2, pair[0]); self.put(x, y - 1, pair[1])

    def brazier(self, x, y, colour=2, keep=()):
        if not self.free(x, y, keep): return False
        # NovaLighting lights every !Other2 index 7 orange on its own; a blue flame needs its own light
        self.add_event('Brazier', x, y, [page(char(BRAZIER, 7, colour), step_anim=True, walk_anim=False, dir_fix=True)],
                       BLUE_LIGHT if colour == 4 else '')
        self.taken.add((x, y)); return True

    def chest(self, x, y, items, keep=()):
        if not self.free(x, y, keep): return False
        lid = [L.rt(L.R_TURN_LEFT), L.rt(L.R_WAIT, 3), L.rt(L.R_TURN_RIGHT), L.rt(L.R_WAIT, 3), L.rt(L.R_TURN_UP),
               {'code': 0, 'parameters': []}]
        found = ' and '.join('%d \\C[6]%s\\C[0]' % (n, ITEM_NAMES[i]) for i, n in items)
        self.add_event('Chest', x, y, [
            page(char('!Chest', 4), walk_anim=False, commands=[
                se('Chest1'),
                cmd(205, [0, {'list': lid, 'repeat': False, 'skippable': False, 'wait': True}]),
                *[cmd(126, [i, 0, 0, n]) for i, n in items], *text('Found %s!' % found), cmd(123, ['A', 0])]),
            page(char('!Chest', 4, direction=8), walk_anim=False, cond={'selfSwitchValid': True, 'selfSwitchCh': 'A'})])
        self.taken.add((x, y)); return True

    def look(self, name, x, y, lines):
        self.add_event(name, x, y, [page(None, commands=text(*lines), priority=1)])

    def go(self, name, x, y, target, tx, ty, d):
        self.add_event(name, x, y, [L.exit_page(target, tx, ty, d)])

    def light(self, x, y, radius, color):
        self.add_event('Light', x, y, [page(None, priority=0, through=True)], '<light: %d, %s>' % (radius, color))

    def scatter(self, cells, tiles, every, keep=()):
        """Deterministic sprinkle: every `every`-th free cell (by a hash of its position) gets the next tile."""
        k = 0
        for x, y in cells:
            if (x * 7 + y * 13) % every == 0 and self.prop(x, y, tiles[k % len(tiles)], keep): k += 1

    def walkable(self, blockers=()):
        import validate_maps as V
        f = V.flags_for(DUNGEON)
        d = {'width': self.w, 'height': self.h, 'tilesetId': DUNGEON, 'data': self.tile_data(), 'events': self.events}
        ev = {(e['x'], e['y']) for e in self.events[1:]
              if e['pages'][0]['priorityType'] == 1 and not e['pages'][0]['through']} | set(blockers)
        seen, q = {self.arrival}, [self.arrival]
        for x, y in q:
            for n in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                if n not in seen and n not in ev and V.passable(d, *n, f): seen.add(n); q.append(n)
        return seen, ev

    def free_trapped(self, opened=()):
        """Props along the walls can close off a corner: lift the props round any floor cell nobody can reach.
        `opened` = blocking events that open later (grates, gates): treated as open here."""
        for _ in range(10):
            seen, ev = self._walk_open(opened)
            floor = {(i % self.w, i // self.w) for i, c in enumerate(self.cls) if c == 0}
            trapped = [p for p in floor - seen - self.taken - ev]
            if not trapped: return
            for x, y in trapped:
                for n in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                    if n in self.taken and n not in ev:
                        self.put(n[0], n[1], 0); self.put(n[0], n[1] - 1, 0, 3); self.taken.discard(n)

    def _walk_open(self, opened):
        saved = self.events
        self.events = [e for e in saved if not e or (e['x'], e['y']) not in set(opened)]
        try: return self.walkable()
        finally: self.events = saved

    def seal_wall_tops(self):
        for i, c in enumerate(self.cls):
            x, y = i % self.w, i // self.w
            if c == 2 and not self.top[1][y][x]: self.put(x, y, INVISIBLE_WALL, 3)


class Room:
    def __init__(self, x0, y0, x1, y1):
        self.x0, self.y0, self.x1, self.y1 = x0, y0, x1, y1
        self.w, self.h = x1 - x0 + 1, y1 - y0 + 1
        self.cx, self.cy = (x0 + x1) // 2, (y0 + y1) // 2

    def back(self):                    # the top floor row, against the back wall
        return [(x, self.y0) for x in range(self.x0, self.x1 + 1)]

    def sides(self):
        return [(x, y) for y in range(self.y0 + 1, self.y1 + 1) for x in (self.x0, self.x1)]

    def front(self):
        return [(x, self.y1) for x in range(self.x0 + 1, self.x1)]

    def corners(self):
        return [(self.x0, self.y1), (self.x1, self.y1), (self.x1, self.y0), (self.x0, self.y0)]


def place_first(m, r, fn):
    keep = m.openings(r)
    for x, y in r.sides() + r.front():
        if fn(x, y, keep): return True
    return False


# =========================================================================== B1: the cellars
def cellars(level, depths_arrival):
    m = ForgeMap(level, K.VILLA_CELLARS)
    m.note = '<ambient: #5a5266>'
    m.bgm = {'name': 'Dungeon1', 'pan': 0, 'pitch': 90, 'volume': 65}
    m.bgs = {'name': 'Drips', 'pan': 0, 'pitch': 100, 'volume': 40}
    m.encounters = [(1, 5), (20, 4), (5, 3), (18, 2)]            # bats, skeletons, sewer rats, spiders and bats
    rooms = m.rooms()
    # the stairs to the hall: the topmost room with whole back wall. Landing pit: the dead end nearest them (the
    # party finds the way up barred first). Ladder down: the dead end farthest from the pit, behind the grate.
    # Lever: the dead end farthest from the pit after that.
    stairs = min((r for r in rooms if m.wall_slot(r, 2) is not None), key=lambda r: (r.y0, r.x0))
    dead = [r for r in rooms if r is not stairs and len(m.mouths(r)) == 1]
    to_stairs = m.distances((stairs.cx, stairs.cy))
    landing = min(dead, key=lambda r: to_stairs[(r.cx, r.cy)])
    from_pit = m.distances((landing.cx, landing.cy))
    far = max((r for r in dead if r is not landing and m.wall_slot(r, 1) is not None), key=lambda r: from_pit[(r.cx, r.cy)])
    lever_room = max((r for r in dead if r not in (landing, far)), key=lambda r: from_pit[(r.cx, r.cy)])
    others = [r for r in rooms if r not in (stairs, landing, far, lever_room)]

    # -- the landing pit, under the trapdoor
    m.arrival = (landing.cx, landing.cy)
    assert (K.VILLA_CELLARS,) + m.arrival == K.ARRIVE['villa_cellars_from_ballroom'][:3], m.arrival
    ax, ay = m.arrival
    clear = {(ax + dx, ay + dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)}
    keep = m.openings(landing) | clear
    m.prop(landing.x0, landing.y1, SKELETON, keep); m.prop(landing.x0 + 1, landing.y1, BONES, keep)
    m.prop(landing.x1, landing.y0, BONES_B, keep)
    m.look('Remains', landing.x0, landing.y1, ['Bones, long dry, still in the clothes of a guest.',
                                               'You are not the first the ballroom has let go of.'])
    m.scatter([p for p in landing.back() + landing.sides() + landing.front()], RUBBLE + (BROKEN_CRATE,), 2, keep)
    m.light(ax, ay - 1, 110, '#c8c0e0')                           # the thread of light from the seam above
    land = [cmd(230, [20]), se('Blow3', 90, 80), cmd(225, [6, 9, 20, True]), cmd(222, []), cmd(230, [30]),
            *text('The floor of the ballroom gave way - and the dark took the rest.',
                  'Far above, the seam of light narrows to a thread, and is gone.'),
            cmd(123, ['A', 0])]
    lx0, ly0 = next(p for p in landing.corners()[::-1] if m.free(*p, keep=clear))
    m.add_event('Landing', lx0, ly0, [
        page(None, trigger=3, priority=0, commands=land, cond={'switch1Valid': True, 'switch1Id': K.SW_VILLA_TRAPDOOR}),
        page(None, priority=0, cond={'selfSwitchValid': True, 'selfSwitchCh': 'A'})])
    m.taken.add((lx0, ly0))

    # -- the steps up to the hall: barred from above
    sx = m.wall_slot(stairs, 2)
    for c, (top, bot) in enumerate(zip(*STAIRS_UP)):
        m.put(sx + c, stairs.y0 - 2, top); m.put(sx + c, stairs.y0 - 1, bot)
        m.look('Stairs Up', sx + c, stairs.y0 - 1, ['The steps climb to a cellar door.',
                                                    'It is barred from the other side - an old bar, and a heavy one.'])

    # -- the way down: a ladder in the far room, an iron grate across the passage in
    lx, ly = far.cx, far.cy
    m.put(lx, ly, LADDER_DOWN); m.taken.add((lx, ly))
    m.go('Ladder Down', lx, ly, *depths_arrival)
    m.ladder = (lx, ly)
    m.look('Old Masonry', far.x0, far.y0, ['The brick gives way to older stone here, grey and close-fitted.',
                                            'Whoever built the cellars dug down onto something already standing.'])
    m.taken.add((far.x0, far.y0))
    (mouth,) = m.mouths(far)
    m.grate = []
    for i, (x, y) in enumerate(mouth):
        m.add_event('Iron Grate', x, y, [
            page(tile_image(GRATE[i % 2]), commands=text(
                'An iron grate, set in grooves cut into the stone. It will not lift by hand.',
                'Its chain runs up into the wall - and away along the passage, somewhere you have not been.')),
            page(None, priority=0, through=True, cond={'switch1Valid': True, 'switch1Id': K.SW_VILLA_GRATE})])
        m.grate.append((x, y))

    # -- the lever that raises it, against the back wall of the farthest other dead end
    vx = m.wall_slot(lever_room, 1)
    pulled = [se('Switch2'), cmd(121, [K.SW_VILLA_GRATE, K.SW_VILLA_GRATE, 0]), cmd(230, [20]),
              se('Earth3', 70, 80), cmd(225, [3, 6, 30, True]),
              *text('Somewhere far off, chain rattles through stone and iron grinds upward.')]
    m.add_event('Lever', vx, lever_room.y0, [
        page(char(LEVER, 0, 2), walk_anim=False, dir_fix=True, commands=text(
            'An old lever, its chain running into the wall.') + choice(['Pull it', 'Leave it'], [pulled, []])),
        page(char(LEVER, 0, 6), walk_anim=False, dir_fix=True, commands=text('The lever is down. The grate stands open.'),
             cond={'switch1Valid': True, 'switch1Id': K.SW_VILLA_GRATE})])
    m.taken.add((vx, lever_room.y0))

    # -- the working cellars
    for k, r in enumerate([stairs] + others + [lever_room]):
        keep = m.openings(r) | {(sx, stairs.y0), (sx + 1, stairs.y0), (vx, lever_room.y0 + 1)}
        dress_cellar(m, r, ('wine', 'store', 'larder')[k % 3], keep)
    keep = m.openings(far) | {(lx, ly + 1), (lx, ly - 1), (lx - 1, ly), (lx + 1, ly)}
    dress_cellar(m, far, 'far', keep)
    # light: a brazier in each room (none in the pit - only the light from above)
    for r in [stairs] + others + [far, lever_room]:
        keep = m.openings(r)
        for x, y in [(r.x0, r.y1), (r.x1, r.y1), (r.x1, r.y0), (r.x0, r.y0 + 1)]:
            if m.brazier(x, y, 2, keep): break
    stores = sorted(others, key=lambda r: -r.w * r.h)
    if stores: place_first(m, stores[0], lambda x, y, keep: m.chest(x, y, [(2, 2)], keep))
    if len(stores) > 1: place_first(m, stores[1], lambda x, y, keep: m.chest(x, y, [(1, 3)], keep))
    m.seal_wall_tops(); m.free_trapped(opened=m.grate)
    return m


def dress_cellar(m, r, role, keep):
    if role == 'wine':                       # racks along the back wall, barrels at the sides
        for i, (x, y) in enumerate(r.back()):
            if m.c(x, y - 1) == 1: m.tall(x, y, tuple(IB(n) for n in (WINE_RACK, BOTTLES)[i % 2]), keep)
        for j, (x, y) in enumerate(r.sides()):
            if j % 2 == 0: m.prop(x, y, (BARREL, BARREL_OPEN)[j % 4 // 2], keep)
    elif role == 'store':                    # crates and sacks
        for i, (x, y) in enumerate(r.back()):
            if i % 3 != 1: m.prop(x, y, CRATES[i % len(CRATES)], keep)
        for j, (x, y) in enumerate(r.sides()):
            if j % 3 == 0: m.prop(x, y, IB(SACKS), keep)
    elif role == 'larder':                   # jars, pots, barrels
        for i, (x, y) in enumerate(r.back()):
            if i % 2 == 0: m.prop(x, y, (JAR, POT)[i // 2 % 2], keep)
        for j, (x, y) in enumerate(r.sides()):
            if j % 4 == 1: m.prop(x, y, BARREL, keep)
    else:                                    # the far room: older, disused
        for i, (x, y) in enumerate(r.back()):
            if i % 3 == 2: m.prop(x, y, (BROKEN_CRATE, RUBBLE[0])[i % 2], keep)
        if m.c(r.x1, r.y0 - 1) == 1: m.put(r.x1, r.y0 - 1, COBWEB)


# =========================================================================== B2: the old foundations
CARVINGS = [   # in the order the seal wants them
    ('KNEEL', 'a knight on one knee, his sword laid down before him'),
    ('SWEAR', 'a bare hand pressed flat to a stone, light running out between the fingers'),
    ('PLANT', 'a rose, its roots gripping the stones of a doorway'),
    ('KINDLE', 'a fire in a cupped pair of hands, rayed like a small sun'),
]


def foundations(level, cellars_ladder):
    m = ForgeMap(level, K.VILLA_DEPTHS)
    m.note = '<ambient: #4a4868>'
    m.bgm = {'name': '03_Creeping_Darkness', 'pan': 0, 'pitch': 90, 'volume': 60}
    m.bgs = {'name': 'Darkness', 'pan': 0, 'pitch': 100, 'volume': 35}
    m.encounters = [(20, 5), (11, 4), (21, 3), (30, 2)]          # skeletons, bats, the dead risen, gargoyles
    V = K.VAR_VILLA_BRAZIERS
    rooms = m.rooms()
    entrance = min((r for r in rooms if m.wall_slot(r, 1) is not None), key=lambda r: (r.y0, r.x0))
    gate_room = max((r for r in rooms if r is not entrance and m.wall_slot(r, 3) is not None),
                    key=lambda r: (len(m.mouths(r)), r.w * r.h))
    rest = [r for r in rooms if r not in (entrance, gate_room)]
    # the four braziers go in the rooms round the gate; the order the seal wants is not the order you walk them
    to_gate = m.distances((gate_room.cx, gate_room.cy))
    by_dist = sorted(rest, key=lambda r: to_gate[(r.cx, r.cy)])
    assert len(by_dist) == 4, len(by_dist)
    order = [by_dist[1], by_dist[3], by_dist[0], by_dist[2]]

    # -- the ladder up to the cellars
    ux = m.wall_slot(entrance, 1)
    m.on_wall(ux, entrance.y0, LADDER_UP)
    m.go('Ladder Up', ux, entrance.y0 - 1, K.VILLA_CELLARS, cellars_ladder[0], cellars_ladder[1] + 1, 2)
    m.arrival = (ux, entrance.y0)

    # -- the sealed gate in the back wall of the central hall: six tile events (asleep / awake / open)
    gx = m.wall_slot(gate_room, 3)
    gy = gate_room.y0
    assert (K.VILLA_DEPTHS, gx + 1, gy) == K.ARRIVE['villa_depths_from_roseway'][:3], (gx + 1, gy)
    words = '. '.join(w for w, _ in CARVINGS) + '.'
    for row in (0, 1):
        for c in range(3):
            x, y = gx + c, gy - 2 + row
            asleep = page(tile_image(GATE_DARK[row][c]), walk_anim=False)
            awake = page(tile_image(GATE_LIT[row][c]), walk_anim=False, cond={'variableValid': True, 'variableId': V, 'variableValue': 4})
            pages = [asleep, awake]
            if c == 1 and row == 1:
                asleep['list'][:0] = text('A gate older than the house above it. Cut deep into the stone: a rose, growing round a sun.',
                                          'Four words ring the seal, cut in order: %s' % words, 'The seal is cold and dark.')
                awake['list'][:0] = [comment(BLUE_LIGHT),
                                     *text('The rose round the sun burns blue. The seal hums - not unkindly.',
                                           'As if it remembers a hand like yours.'),
                                     se('Saint3'), cmd(224, [[150, 190, 255, 170], 30, True]), se('Earth4', 80, 70),
                                     cmd(225, [4, 6, 30, True]), *text('The stone sighs, and parts.'),
                                     cmd(122, [V, V, 0, 0, 5])]
                opened = L.exit_page(*K.ARRIVE['villa_roseway_from_depths'])
                opened.update(priorityType=1, image=dict(opened['image'], **tile_image(DARK)))
                opened['conditions'].update(variableValid=True, variableId=V, variableValue=5)
                opened['list'][:0] = [comment(BLUE_LIGHT)]
                pages.append(opened)
            elif c == 1 and row == 0:
                pages.append(page(tile_image(DARK_ARCH), walk_anim=False,
                                  cond={'variableValid': True, 'variableId': V, 'variableValue': 5}))
            m.add_event('Sealed Gate', x, y, pages)
    for i, row in enumerate(CIRCLE_BLUE):
        for c, n in enumerate(row):
            if gy + 1 + i <= gate_room.y1: m.put(gx + c, gy + 1 + i, DC(n))
    for c in range(3): m.taken.update({(gx + c, gy + i) for i in range(4)})
    for x in (gx - 1, gx + 3):
        m.tall(x, gy + 1, STATUE_GODDESS if x < gx else STATUE_ANGEL)

    # -- the first hall: the steles that tell the story, a colonnade, two braziers burning
    stelae = [['The carving shows knights kneeling before a figure made only of light.',
               'Below it a single word, worn almost away: "...until."'],
              ['"First the knight knelt. Then he swore upon the stone.',
               'Then the rose was planted at the door, and the fire kindled to keep it -',
               'until the light comes home."'],
              ['"Whoever keeps this door keeps the oath.',
               'Whoever keeps the oath keeps the light."']]
    keep = m.openings(entrance) | {(ux, entrance.y0), (ux, entrance.y0 + 1)}
    # stelae against the hall's back walls (it is L-shaped: the top and the lower west arm), two apart
    spots = []
    for x, y in sorted(((x, y) for x in range(entrance.x0, entrance.x1 + 1) for y in range(entrance.y0, entrance.y1)
                        if m.c(x, y) == 0 and m.c(x, y - 1) == 1 and m.c(x, y - 2) == 1 and abs(x - ux) >= 2
                        and (x, y + 1) not in keep and m.c(x, y + 2) == 0), key=lambda p: (p[1], p[0])):
        if all(abs(x - a) >= 2 or y != b for a, b in spots): spots.append((x, y))
    for (x, y), lines in zip(spots, stelae):
        if m.tall(x, y + 1, STELE, keep):
            m.look('Stele', x, y + 1, lines); keep.add((x, y + 2))          # read from the front
    for x in range(entrance.x0 + 1, entrance.x1, 3):
        for y in range(entrance.y0 + 5, entrance.y1 - 1, 4):
            m.tall(x, y, PILLAR_ROUND, keep) if x in (entrance.x0 + 1, entrance.x1 - 1) else None
    lit = 0
    for x, y in [(ux - 2, entrance.y0), (ux + 2, entrance.y0)] + entrance.corners() + entrance.sides():
        if lit < 2 and m.brazier(x, y, 4, keep): lit += 1

    # -- the four cold braziers, each under a carved tablet
    for i, (r, (word, carving)) in enumerate(zip(order, CARVINGS), start=1):
        bx = m.wall_slot(r, 1)
        by = r.y0
        m.put(bx, by - 1, PLAQUE)
        light_it = if_var(V, i - 1, then=[
            se('Fire1'), cmd(122, [V, V, 0, 0, i]), *text('The flame takes, and burns blue.')] + ([
            cmd(230, [30]), se('Saint3'), cmd(224, [[150, 190, 255, 170], 40, True]), cmd(225, [3, 5, 30, True]),
            *text('Somewhere in the foundations a deep note sounds, like a bell heard under water.')] if i == 4 else []),
            else_=[se('Fire1'), cmd(230, [10]), se('Blow1', 70, 60), cmd(224, [[20, 20, 40, 200], 20, True]),
                   cmd(122, [V, V, 0, 0, 0]),
                   *text('The flame flares - and gutters out. Every brazier you lit has gone dark with it.')])
        m.add_event('Brazier: ' + word.title(), bx, by, [
            page(char(BRAZIER, 7, 8), walk_anim=False, dir_fix=True,
                 commands=[comment('<light: 0, #000000>')] + text('A cold brazier. On the tablet above it: %s.' % carving)
                 + choice(['Light it', 'Leave it'], [light_it, []])),
            page(char(BRAZIER, 7, 4), step_anim=True, walk_anim=False, dir_fix=True,
                 commands=[comment(BLUE_LIGHT), *text('The flame burns blue and steady under the carving of %s.' % carving)],
                 cond={'variableValid': True, 'variableId': V, 'variableValue': i})])
        m.taken.update({(bx, by), (bx, by + 1)})
        keep = m.openings(r) | {(bx, by + 1), (bx - 1, by + 1), (bx + 1, by + 1)}
        if r.h >= 6 and r.w >= 7:            # a colonnade
            for x in (r.x0 + 1, r.x1 - 1):
                for y in range(r.y0 + 2, r.y1, 3): m.tall(x, y, PILLAR_ROUND, keep)
        else:                                # fallen masonry
            for j, (x, y) in enumerate(r.sides() + r.front()):
                if j % 3 == 0: m.prop(x, y, (BROKEN_PILLARS + RUBBLE)[j % 9], keep)
    far = max(rest, key=lambda r: to_gate[(r.cx, r.cy)])
    near = min(rest, key=lambda r: to_gate[(r.cx, r.cy)])
    place_first(m, far, lambda x, y, keep: m.chest(x, y, [(7, 1)], keep))
    place_first(m, near, lambda x, y, keep: m.chest(x, y, [(5, 2)], keep))
    m.seal_wall_tops(); m.free_trapped()
    return m


# =========================================================================== the Rose Way: up to the garden
def rose_way(level):
    m = ForgeMap(level, K.VILLA_ROSE_WAY)
    m.note = '<ambient: #57504a>'
    m.bgm = {'name': 'Dungeon2', 'pan': 0, 'pitch': 90, 'volume': 60}
    m.bgs = {'name': 'Drips', 'pan': 0, 'pitch': 80, 'volume': 30}
    m.encounters = [(1, 5), (11, 3), (17, 3), (18, 2)]           # bats, more bats, cave spiders
    floor = [(i % m.w, i // m.w) for i, c in enumerate(m.cls) if c == 0]
    # the bottom: the passage from the gate comes in at the lowest floor cells
    low = max(y for _, y in floor)
    bottom = sorted(x for x, y in floor if y == low)
    m.arrival = (bottom[0], low - 1)
    assert (K.VILLA_ROSE_WAY,) + m.arrival == K.ARRIVE['villa_roseway_from_depths'][:3], m.arrival
    for x in bottom:
        m.put(x, low, DARK)
        m.go('Way Down', x, low, *K.ARRIVE['villa_depths_from_roseway'])
        m.taken.add((x, low))
    # the top: steps up to the slab, in the back wall of the highest chamber
    top = min((r for r in m.rooms() if m.wall_slot(r, 2) is not None), key=lambda r: r.y0)
    sx = m.wall_slot(top, 2)
    assert (K.VILLA_ROSE_WAY, sx, top.y0) == K.ARRIVE['villa_roseway_from_bloodrose'][:3], (sx, top.y0)
    out = K.ARRIVE['villa_bloodrose_from_roseway']
    first = [*text('The steps end under a slab of stone. Daylight shows round its edges -',
                   'and the smell of roses.'),
             se('Push', 90, 80), cmd(225, [5, 6, 30, True]), se('Earth3', 90, 90),
             *text('You set your shoulders to it. The slab grinds aside.'),
             cmd(121, [K.SW_VILLA_ROSE_WAY, K.SW_VILLA_ROSE_WAY, 0]), *L.transfer(*out)]
    for c, (t, b) in enumerate(zip(*STAIRS_UP)):
        m.put(sx + c, top.y0 - 2, t); m.put(sx + c, top.y0 - 1, b)
        again = L.exit_page(*out)
        again['conditions'].update(switch1Valid=True, switch1Id=K.SW_VILLA_ROSE_WAY)
        m.add_event('Slab', sx + c, top.y0 - 1, [page(None, trigger=1, commands=first), again])
    m.light(sx, top.y0, 140, '#ffe4b8')
    keep_top = {(sx + dx, top.y0 + dy) for dx in (-1, 0, 1, 2) for dy in (0, 1)}
    for x, y in ((sx - 1, top.y0 + 1), (sx + 2, top.y0), (sx + 1, top.y0 + 2)):
        if m.c(x, y) == 0: m.put(x, y, PETALS)        # petals fallen through the cracks round the slab
    # roots of the Bloodrose tree through the walls - thicker the higher you climb
    faces = [(x, y) for x, y in floor if m.c(x, y - 1) == 1 and m.c(x, y - 2) == 1]
    for x, y in faces:
        if (x * 5 + y * 3) % (3 if y < 16 else 7) == 0 and (x, y) not in keep_top:
            m.on_wall(x, y, ROOTS if (x + y) % 2 else VINES)
    rx, ry = next((x, y) for x, y in sorted(faces, key=lambda p: p[1]) if (x * 5 + y * 3) % 3 == 0 and (x, y) not in keep_top)
    m.look('Roots', rx, ry - 1, ['Roots as thick as an arm push out of the earth, veined dark red',
                                 'like the leaves of the tree in the garden.'])
    # stones along the walls; a chest in the side chamber
    keep = keep_top | {(x, low - 1) for x in bottom} | {(x, low - 2) for x in bottom}
    edge = [(x, y) for x, y in floor if any(m.c(x + dx, y + dy) != 0 for dx, dy in ((1, 0), (-1, 0), (0, 1)))]
    m.scatter(edge, (PEBBLES[0], ROCK, PEBBLES[1], ROCK_GREY), 5, keep)
    side = max((r for r in m.rooms() if r is not top), key=lambda r: (r.w * r.h))
    place_first(m, side, lambda x, y, k: m.chest(x, y, [(6, 1)], k | keep))
    m.seal_wall_tops(); m.free_trapped()
    return m


def build():
    lv = forge()
    # the levels refer to each other's ladders, so lay out B2's entrance first
    probe = ForgeMap(lv['foundations'], K.VILLA_DEPTHS)
    e2 = min((r for r in probe.rooms() if probe.wall_slot(r, 1) is not None), key=lambda r: (r.y0, r.x0))
    depths_arrival = (K.VILLA_DEPTHS, probe.wall_slot(e2, 1), e2.y0, 2)
    b1 = cellars(lv['cellars'], depths_arrival)
    b2 = foundations(lv['foundations'], b1.ladder)
    rw = rose_way(lv['roseway'])
    return {K.VILLA_CELLARS: b1, K.VILLA_DEPTHS: b2, K.VILLA_ROSE_WAY: rw}


def save(mid, m):
    """Write the map, then put back its mood tags (map_moods.py) and battle background (battlebacks.py) - a plain save
    would drop them, and running those tables with --apply also rewrites hand-tuned maps such as Map048."""
    import map_moods, battlebacks
    m.save(mid, parent_id=K.VILLA_HALL, order=mid,
           encounter=[{'regionSet': [], 'troopId': t, 'weight': w} for t, w in m.encounters])
    C = map_moods.C
    path = L.DATA + 'Map%03d.json' % mid
    d = C._read(path)
    for tag, value in map_moods.MOODS.get(mid, {}).items(): d['note'] = map_moods.set_tag(d['note'], tag, value)
    if mid in battlebacks.BB:
        b1, b2 = battlebacks.BB[mid]
        d.update({'specifyBattleback': True, 'battleback1Name': b1, 'battleback2Name': b2})
    with open(path, 'w', encoding='utf8', newline='') as f: f.write(C._map_text(d))


def reach_report(mid, m):
    """Flood-fill from the arrival: with the grate / gate shut (what the player can do first) and open."""
    opened = getattr(m, 'grate', [])
    shut, ev = m.walkable()
    full, _ = m._walk_open(opened) if opened else (shut, ev)
    floor = {(i % m.w, i // m.w) for i, c in enumerate(m.cls) if c == 0}
    cut = sorted(floor - full - m.taken - ev)
    far = [e['name'] for e in m.events[1:] if e['name'] not in ('Light', 'Brazier', 'Landing') and
           not any((e['x'] + dx, e['y'] + dy) in full for dx, dy in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)))]
    print('  reach Map%03d: %d cells shut / %d open, cut off %s, unreachable events %s' % (mid, len(shut), len(full), cut[:8], far))
    if opened:
        lever = next(e for e in m.events[1:] if e['name'] == 'Lever')
        print('  lever reachable with the grate shut:', any((lever['x'] + dx, lever['y'] + dy) in shut for dx, dy in ((0, 1), (1, 0), (-1, 0))))


if __name__ == '__main__':
    maps = build()
    for mid, m in maps.items():
        print('Map%03d %s: arrival %s' % (mid, m.display, m.arrival))
        reach_report(mid, m)
    out = next((a for a in sys.argv[1:] if not a.startswith('--')), None)
    if out:
        for mid, m in maps.items(): m.render(out.replace('.png', '_%d.png' % mid), scale=0.5, grid='--grid' in sys.argv)
    if '--save' in sys.argv:
        for mid, m in maps.items():
            save(mid, m); print('saved Map%03d' % mid)
