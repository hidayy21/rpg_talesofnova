"""Outdoor maps on an rm-map-forge layout (forge_outdoor.js): noise ground, raised ground with cliffs, roads routed
through given points and trees packed everywhere else. The script of a map gives the road, the cells to keep open
(clearings, event spots, exits) and its trees; this module runs the generator and hands back a MapBuilder whose
put/cell/events are laid over the forged tiles, plus a flood fill to check what the player can reach.

    fm = forge(K.SOME_MAP, w, h, seed='...', ground=A2(9), road=A2(10), hill=A4(33), paths=[...], keep=[...],
               trees=[Tree(tiles, density, band)])
    fm.walkable(x, y); fm.reach([(x, y)]) -> set of cells
Auto kinds use the map's own sheets: A2(k) = Outside_A2 kind k, A4(k) = Outside_A4 kind k."""
import os, json, subprocess, tempfile
import nova_maplib as L
import validate_maps as V
import town_kit as T

HERE = os.path.dirname(os.path.abspath(__file__))
A1 = lambda k: k
A2 = lambda k: 16 + k
A4 = lambda k: 80 + k
BLOCKER = 767                      # Nova_Market_D's last cell: blank, impassable on the Outside tileset


class Tree:
    def __init__(self, rows, density, band=None, sheet=None):
        """rows: tile numbers top row first (the last row stands on the ground); sheet: an L.ext sheet name, or None
        for the tileset's own B/C ids."""
        f = (lambda n: L.ext(sheet, n)) if sheet else (lambda n: n)
        self.tiles = [[f(n) if n is not None else 0 for n in row] for row in rows]
        self.density, self.band = density, band


class ForgeOutdoor(T.Town):
    """A Town (sign, npc, door, exit, lamp... and edge exits widened on save) over the forged tiles."""

    def __init__(self, level, tileset, name, display):
        L.MapBuilder.__init__(self, level['width'], level['height'], tileset, name, display)
        self.note = '<outdoor>'
        self.base = level['data']
        self.road = level['road']
        self.face = level['face'] or [0] * (self.w * self.h)
        self.level = level['level'] or [0] * (self.w * self.h)
        self.own = level['own']

    def i(self, x, y): return y * self.w + x
    def is_road(self, x, y): return self.inb(x, y) and bool(self.road[self.i(x, y)])
    def is_face(self, x, y): return self.inb(x, y) and bool(self.face[self.i(x, y)])
    def has_object(self, x, y): return self.inb(x, y) and bool(self.own[self.i(x, y)])
    def lvl(self, x, y): return self.level[self.i(x, y)]

    def clear(self, x, y):
        """Take the forged object tiles off a cell (both layers) - for a spot an event or prop needs."""
        N = self.w * self.h
        for z in (2, 3): self.base[z * N + self.i(x, y)] = 0
        self.own[self.i(x, y)] = 0

    def tile_data(self):
        w, h, N = self.w, self.h, self.w * self.h
        out = list(self.base)
        mine = super().tile_data()
        for z in range(4):
            for k in range(N):
                if z < 2:
                    if self.auto[z][k // w][k % w] is not None: out[z * N + k] = mine[z * N + k]
                elif self.top[z - 2][k // w][k % w]:
                    out[z * N + k] = mine[z * N + k]
        return out

    # ------------------------------------------------------------ reachability
    def walkable(self, x, y, data=None, flags=None):
        """Passable on every layer (the tile flags of the map's tileset) and no blocking event."""
        data = data or self.tile_data()
        flags = flags or V.flags_for(self.tileset_id)
        N = self.w * self.h
        k = self.i(x, y)
        for z in (3, 2, 1, 0):
            t = data[z * N + k]
            if not t: continue
            f = flags[t] if t < len(flags) else 0
            if f & 0x10: continue                 # drawn above: decides nothing
            return (f & 0x0f) != 0x0f
        return False

    def reach(self, starts):
        data, flags = self.tile_data(), V.flags_for(self.tileset_id)
        solid = {(e['x'], e['y']) for e in self.events[1:] if e and e['pages'][0].get('priorityType', 1) == 1
                 and not e['pages'][0].get('through')}
        seen, stack = set(), list(starts)
        while stack:
            x, y = stack.pop()
            if (x, y) in seen or not self.inb(x, y) or (x, y) in solid and (x, y) not in starts: continue
            if not self.walkable(x, y, data, flags): continue
            seen.add((x, y))
            stack += [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
        return seen


def forge(map_id_names, w, h, seed, ground, road, paths, trees, keep=(), hill=None, stairs=None, patch=None,
          overlay=None, water=0, water_auto=0, params=None, tileset=2, zones=()):
    """zones: [(auto, y0, y1)] - another ground over those rows (ragged edge)."""
    """map_id_names: (editor name, display name). paths: [(points, width)]. patch/overlay: (auto, threshold, scale)."""
    cfg = {'seed': seed, 'width': w, 'height': h, 'params': params or {}, 'ground': ground, 'road': road,
           'hill': hill, 'stairs': stairs, 'water': water, 'waterAuto': water_auto,
           'patch': dict(zip(('auto', 'threshold', 'scale'), patch)) if patch else None,
           'overlay': dict(zip(('auto', 'threshold', 'scale'), overlay)) if overlay else None,
           'paths': [{'points': [list(p) for p in pts], 'width': wd} for pts, wd in paths],
           'keep': [list(c) for c in keep],
           'zones': [{'auto': a, 'y0': y0, 'y1': y1} for a, y0, y1 in zones],
           'objects': [{'tiles': t.tiles, 'density': t.density, 'band': t.band} for t in trees]}
    with tempfile.TemporaryDirectory() as tmp:
        cin, cout = os.path.join(tmp, 'cfg.json'), os.path.join(tmp, 'out.json')
        json.dump(cfg, open(cin, 'w'))
        subprocess.run(['node', os.path.join(HERE, 'forge_outdoor.js'), cin, cout], check=True)
        level = json.load(open(cout))
    return ForgeOutdoor(level, tileset, *map_id_names)
