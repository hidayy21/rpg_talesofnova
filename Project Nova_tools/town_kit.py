# Building blocks for Royal Kingdom of Nova town maps (Outside tileset = 2, with Nova_Market_D in slot D).
import nova_maplib as L
from nova_maplib import page, cmd, text, say, transfer, char, rt
from make_town_tiles import build as _build_props

PROP, _ = _build_props(write=False)       # name -> D tile id

OUTSIDE = 2
# ---------------------------------------------------------------- ground (A2 / A5)
GRASS, DIRT, ROAD, COBBLE, BUSH, EDGING = ('A2', 0), ('A2', 8), ('A2', 2), ('A2', 3), ('A2', 4), ('A2', 5)
COBBLE_B, SAND, MOSS, CARPET, FENCE, STONE_FENCE, METAL_FENCE = ('A2', 19), ('A2', 16), ('A2', 23), ('A2', 27), ('A2', 6), ('A2', 22), ('A2', 14)
WATER, DEEP, PORT_WATER, CANAL = ('A1', 0), ('A1', 1), ('A1', 12), ('A1', 6)
STONE_WALL_TOP, STONE_WALL = ('A4', 0), ('A4', 8)
CASTLE_TOP, CASTLE_WALL = ('A4', 20), ('A4', 28)
FORT_TOP, FORT_WALL = ('A4', 22), ('A4', 30)
URBAN_TOP, URBAN_WALL = ('A4', 16), ('A4', 24)
HEDGE_TOP, HEDGE = ('A4', 6), ('A4', 14)
PAVED_LEDGE_TOP, PAVED_LEDGE = ('A4', 36), ('A4', 44)
def A5(i): return ('A5', i)
COB_E, COB_F, COB_G, COB_H, COB_I = A5(48), A5(49), A5(50), A5(68), A5(69)
RELIEF_A = (76, 77, 84, 85)       # 2x2 large relief floor tile
RELIEF_B = (78, 79, 86, 87)
QUAY = (64, 65, 66, 67)           # port ledge: left, centre, right, single
PIER_V = (2, 3, 4)                # large wooden bridge, vertical: left, centre, right
PIER_H = (5, 6, 13)               # horizontal: top, centre, bottom
STAIRS_PAVED = (56, 57, 58, 59)

# ---------------------------------------------------------------- roofs / walls (A3)
ROOF = {'red': 0, 'orange': 1, 'indigo': 2, 'green': 3, 'blue': 4, 'dressed': 5, 'khaki': 6, 'metal': 7,
        'wood': 16, 'wood2': 17, 'log': 18, 'thatch': 19, 'stone': 20, 'tent': 21}
WALL = {'plaster': 8, 'brickstone': 9, 'brick': 10, 'stone': 11, 'tudor': 12, 'white': 13, 'mud': 14, 'wood': 15,
        'planks': 24, 'wood2': 25, 'log': 26, 'boards': 27, 'rockwall': 28, 'tent': 29}

# ---------------------------------------------------------------- B tiles (Outside_B)
SIGN = {'sword': 1, 'armor_shield': 2, 'armor': 3, 'item': 4, 'tea': 5, 'inn': 6, 'pub': 7, 'eatery': 8,
        'magic': 9, 'staff': 10, 'coin': 11, 'jewel': 12, 'hammer': 13, 'crest': 14, 'blank': 15}
WIN, WIN_FLOWER_G, WIN_FLOWER_P, WIN_SHUT, MID_WIN = 32, 33, 34, 35, 36
STAINED = 43
LG_TOP, LG_BOT = 48, 56
ARCH_TOP, ARCH_BOT = 50, 58          # double wooden door window/arch
CHIMNEY_A, CHIMNEY_B = 64, 72
BOLLARD, BOLLARD_ROPE = 65, 66
SIGNPOST, NOTICE_BOARD, WELL, STEPPING = 73, 74, 75, 76
BARREL, POT, BUCKET, BASIN = 77, 80, 81, 82
FIRE_PIT = 83
BARRICADE_H, BARRICADE_V = 85, 86
GRASS_TUFTS = (88, 89, 90, 91)
STUMP, TREE_S1, TREE_S2, BOULDER = 92, 93, 94, 95
FLOWERS = (96, 97, 98, 99)
LOG, TREE_S3, BUSH_S, BOULDER_B = 100, 101, 102, 103
SCARECROW, HAY = 104, 184
FIREWOOD, ROCKS = 106, 107
CROPS = (108, 109, 110, 111)
CRATE_L_T, CRATE_L_B = 116, 124
CRATE, CRATE_GRAIN, CRATE_APPLE, CRATE_CARROT, CRATE_ORANGE = 117, 118, 119, 126, 127
FLOWER_BUSH, FERN = 181, 182
VINES = (192, 200)
TENT = ((208, 209, 210), (216, 217, 218), (224, 225, 226))
LAMP = (211, 219, 227)
BIG_TREE = ((112, 113), (120, 121))
BIG_TREE2 = ((114, 115), (122, 123))
BRIDGE_V, BRIDGE_H, STONE_BRIDGE_V, STONE_BRIDGE_H = 18, 19, 20, 21
# Outside_C
C_ = 256
BANNER_RED, BANNER_BLUE, BANNER_GREEN, BANNER_TAN = (C_ + 32, C_ + 40), (C_ + 34, C_ + 42), (C_ + 36, C_ + 44), (C_ + 38, C_ + 46)
STATUE_A = (C_ + 80, C_ + 88)
ANGEL_A, ANGEL_B = (C_ + 81, C_ + 89), (C_ + 82, C_ + 90)
DRAGON_STATUE = ((C_ + 85, C_ + 86), (C_ + 93, C_ + 94))
MONUMENT = (C_ + 48, C_ + 56)
PILLAR = (C_ + 0, C_ + 8)
TOWER = None  # see castle map


class Town(L.MapBuilder):
    def __init__(self, w, h, name, display, ground=COBBLE):
        super().__init__(w, h, OUTSIDE, name, display)
        self.rect(0, 0, w - 1, h - 1, ground)
        self.note = '<outdoor>'          # NovaLighting: follows the night switch

    def save(self, map_id, *args, **kw):
        """Saves, then widens the edge exits to the whole open crossing (see edge_exits.py)."""
        super().save(map_id, *args, **kw)
        import json, edge_exits
        m = json.load(open(L.DATA + 'Map%03d.json' % map_id, encoding='utf8'))
        if edge_exits.widen(m): L.write_map(map_id, m)

    # ------------------------------------------------------------ buildings
    def building(self, x0, x1, top, roof_rows, wall_rows, roof, wall, storeys=None, windows=True,
                 door=None, win_tiles=(WIN,), chimney=None):
        """Front-facing building: roof rows, then wall rows (bottom row = street level).
        Returns the y of the street-level wall row. Windows are placed on every other wall row from the bottom-1."""
        rt_y = top + roof_rows - 1
        self.rect(x0, top, x1, rt_y, ('A3', ROOF[roof]))
        bottom = rt_y + wall_rows
        self.rect(x0, rt_y + 1, x1, bottom, ('A3', WALL[wall]))
        if windows:
            rows = [y for y in range(bottom - 1, rt_y, -2)] if wall_rows >= 2 else []
            for i, y in enumerate(rows):
                for k, x in enumerate(range(x0 + 1, x1, 2)):
                    if door is not None and abs(x - door) < 1 and y >= bottom - 1: continue
                    self.put(x, y, win_tiles[(i + k) % len(win_tiles)])
        if chimney:
            self.put(chimney, top + 1, CHIMNEY_A)
        return bottom

    def tower_roof_note(self): pass

    # ------------------------------------------------------------ props
    def lamp(self, x, base_y):
        self.put(x, base_y - 2, LAMP[0], 3); self.put(x, base_y - 1, LAMP[1], 3); self.put(x, base_y, LAMP[2])

    def big_tree(self, x, y, kind=BIG_TREE):
        (a, b), (c, d) = kind
        self.put(x, y, a, 3); self.put(x + 1, y, b, 3); self.put(x, y + 1, c); self.put(x + 1, y + 1, d)

    def tent(self, x, y):
        for r in range(3):
            for c in range(3):
                self.put(x + c, y + r, TENT[r][c], 3 if r == 0 else 2)

    def tall(self, x, y, pair, layer_top=3):
        self.put(x, y, pair[0], layer_top); self.put(x, y + 1, pair[1])

    def relief(self, x0, y0, x1, y1, tiles=RELIEF_A):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                self.cell(x, y, A5(tiles[((y - y0) % 2) * 2 + (x - x0) % 2]))

    # ------------------------------------------------------------ events
    def door(self, name, x, y, target, tx, ty, style=0, note=''):
        return self.add_event(name, x, y, [L.door_page(target, tx, ty, 8, '!Door1', style)], note)

    def locked_door(self, name, x, y, lines, style=0):
        return self.add_event(name, x, y, [page(char('!Door1', style), commands=text(*lines))])

    def exit(self, name, cells, target, tx, ty, d):
        for i, (x, y) in enumerate(cells):
            # keep the player's offset along the exit so walking off a 4-wide road lands on the same lane
            ox = (x - cells[0][0]) if d in (2, 8) else 0
            oy = (y - cells[0][1]) if d in (4, 6) else 0
            self.add_event('%s %d' % (name, i + 1), x, y, [L.exit_page(target, tx + ox, ty + oy, d)])

    def npc(self, name, x, y, sheet, idx, lines, direction=2, move=0, speed=3, freq=3, route=None, face=('', 0), extra=None):
        speaker, *rest = lines
        cmds = say(speaker, *rest, face=face)
        if extra: cmds = cmds + extra
        return self.add_event(name, x, y, [page(char(sheet, idx, direction), move_type=move, commands=cmds,
                                                 speed=speed, freq=freq, route=route)])

    def critter(self, name, x, y, sheet, idx, se, line, move=1, speed=3, freq=3, pen=None, area=None):
        """area (x1, y1, x2, y2): wanders only inside it (NovaPens), e.g. a paddock with an open gate."""
        cmds = [cmd(250, [{'name': se, 'volume': 70, 'pitch': 100, 'pan': 0}])] + text(line) if se else text(line)
        return self.add_event(name, x, y, [page(char(sheet, idx), move_type=move, commands=cmds, speed=speed, freq=freq,
                                                 route=pen_route(pen) if pen else None, step_anim=bool(pen))],
                              note='<pen: %d,%d,%d,%d>' % area if area else '')

    def obj(self, name, x, y, sheet, idx, lines=None, step=True, through=False, priority=1, direction=2, pattern=1):
        img = char(sheet, idx, direction, pattern)
        return self.add_event(name, x, y, [page(img, commands=text(*lines) if lines else None, step_anim=step,
                                                 walk_anim=step, through=through, priority=priority)])

    def sign(self, name, x, y, lines):
        return self.add_event(name, x, y, [page(None, commands=text(*lines), priority=1)])


def pen_route(step):
    """Animal in an enclosure: one step to `step` ('L'/'R'/'U'/'D') and back, looking around in between."""
    back = {'L': 'R', 'R': 'L', 'U': 'D', 'D': 'U'}[step]
    m = {'L': L.R_LEFT, 'R': L.R_RIGHT, 'U': L.R_UP, 'D': L.R_DOWN}
    return [rt(L.R_WAIT, 90), rt(m[step]), rt(L.R_WAIT, 60), rt(L.R_TURN_RANDOM), rt(L.R_WAIT, 90),
            rt(m[back]), rt(L.R_WAIT, 60), rt(L.R_TURN_DOWN)]


def wander_route(steps):
    """steps: list of 'L','R','U','D','W' (wait 60f). Repeating route for 'patrol' NPCs."""
    m = {'L': rt(L.R_LEFT), 'R': rt(L.R_RIGHT), 'U': rt(L.R_UP), 'D': rt(L.R_DOWN), 'W': rt(L.R_WAIT, 60)}
    return [m[s] for s in steps]
