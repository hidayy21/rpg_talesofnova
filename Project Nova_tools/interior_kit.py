# Building blocks for interiors (Inside tileset = 3).
import nova_maplib as L
from nova_maplib import page, cmd, text, say, transfer, char, rt, common_event

INSIDE = 3
# ---------------------------------------------------------------- floors (A2) and tables (A2, counter flag)
WOOD, WOOD_B, COBBLE_O, STONE, COBBLE_C, COBBLE_D, COBBLE_E, COBBLE_F = (('A2', k) for k in (0, 8, 1, 9, 16, 17, 24, 25))
RUG_A, RUG_B, RUG_C, RUG_D, RUG_E, RUG_F, STRAW = ('A2', 2), ('A2', 10), ('A2', 11), ('A2', 18), ('A2', 26), ('A2', 27), ('A2', 3)
MARBLE, TILE_W = ('A2', 21), ('A2', 29)
TABLE_A, TABLE_B, TABLE_C, TABLE_D = ('A2', 7), ('A2', 15), ('A2', 23), ('A2', 31)
# ---------------------------------------------------------------- walls (A4): (top, face)
WALLS = {'stone': (0, 8), 'brick': (1, 9), 'brick2': (2, 10), 'stone2': (3, 11), 'cobble': (4, 12), 'castle': (5, 13),
         'fort': (6, 14), 'wood': (16, 24), 'log': (17, 25), 'wood2': (18, 26), 'int_wood': (19, 27),
         'int_stone': (20, 28), 'stone_l': (21, 29), 'marble': (22, 30), 'concrete': (23, 31),
         'plaster_c': (32, 40), 'brick_d': (33, 41), 'plaster_e': (34, 42), 'desert': (35, 43),
         'mansion': (36, 44), 'temple': (37, 45), 'tent': (38, 46), 'stage': (39, 47)}
# ---------------------------------------------------------------- Inside_B (ids = local)
B_ = 0
STAIRS_UP, STAIRS_DOWN = (1, 2, 3, 4), (9, 10, 11, 12)
WIN_MID = (16, 17, 18)
WIN_LARGE = (32, 33, 34)
STAINED = 35
WIN_SMALL = (37, 38, 39)
# two-tile furniture (top on the wall row / upper layer, bottom on the floor)
CABINET, CLOSET, DRAWERS, DISH_CABINET = (49, 57), (50, 58), (51, 59), (52, 60)
WINE_RACK, BOTTLES_A, BOTTLES_B = (53, 61), (54, 62), (55, 63)
BREAD_SHELF, SUNDRIES_A, SUNDRIES_A2, SUNDRIES_B, MEDICINE_SHELF = (64, 72), (65, 73), (66, 74), (67, 75), (68, 76)
BOOKSHELF_A, BOOKSHELF_B, BOOKSHELF_B2 = (69, 77), (70, 78), (71, 79)
BED, CHEAP_BED, CHEAP_BED_B, STRAW_BED = (80, 88), (83, 91), (84, 92), (85, 93)
LARGE_BED = ((81, 82), (89, 90))
TABLE_ROUND, TABLE_MARBLE, TABLE_CLOTH, FORTUNE_TABLE, MINI_TABLE = 96, 97, 98, 99, 100
STOOL_A, STOOL_B, STOOL_C, CRYSTAL_TABLE, FLOWER_TABLE = 104, 105, 106, 107, 108
PIANO = ((101, 102, 103), (109, 110, 111))
OVEN, SINK, COUNTER_A, COUNTER_B, DRESSER = 112, 113, 114, 115, 116
SHELF_A, SHELF_JARS, SHELF_BOOKS, SHELF_SACKS, SHELF_BOTTLES = 120, 121, 122, 123, 124
FIREPLACE_L = ((128, 129, 130), (136, 137, 138))
FIREPLACE_STONE, FIREPLACE_BRICK, FIREPLACE_IRON = (131, 139), (132, 140), (133, 141)
TAPESTRY = (134, 142)
CURTAINS_RED = ((145, 146), (153, 154))
CLOCK, MIRROR, NOTICE, WORLD_MAP, PAINTING = (160, 168), (161, 169), 162, (164, 165), 166
PORTRAIT_A, PORTRAIT_B, PAINTING_A, PAINTING_B = 172, 173, 174, 175
CHAIR, CHAIR_STONE = 176, 177
THRONE = ((178, 179, 180), (186, 187, 188))
WALL_SHIELD, WALL_SWORDS, WALL_SWORDS_X = 192, 193, 194
POT_A, POT_B = 200, 201
PILLAR = (204, 212)
BASIN, BARREL, TUB_A, TUB_B = 208, 209, 217, 218
CRATE_B, CRATE_C, CRATES_STACK = 224, 225, (226, 234)
CRATE_GRAIN, CRATE_APPLE, CRATE_ORANGE, CRATE_GREEN = 232, 233, 240, 241
SACK_A, SACK_B, SACKS = 248, 249, 250
JAIL = (244, 245, 246, 247)
# ---------------------------------------------------------------- Inside_C
C_ = 256
CUP_TEA, CUPS, WINE_GLASS, MUG_ALE, MUG = C_ + 0, C_ + 4, C_ + 8, C_ + 16, C_ + 20
TEAPOT, BOTTLE, ALE_BOTTLES = C_ + 24, C_ + 25, C_ + 30
MEAL_FISH, MEAL_MEAT, SIDE_DISH, FRUIT_BOWL, ROAST_PIG, CAKE, PIZZA, ROAST_FISH = (C_ + i for i in (32, 33, 34, 35, 36, 37, 38, 39))
DINNER, PIE, BREAKFAST, PLATE, BOWL, PLATES = C_ + 40, C_ + 44, C_ + 48, C_ + 52, C_ + 53, C_ + 54
BOOK, BOOK_OPEN, OLD_BOOK, OLD_BOOK_OPEN, NOTES, MAP_C, SCROLLS = C_ + 56, C_ + 60, C_ + 64, C_ + 68, C_ + 72, C_ + 76, C_ + 82
VASE, PLANT_A, PLANT_B, PLANTER = C_ + 84, C_ + 85, C_ + 86, C_ + 87
SACK_S, SACKS_S, MEDICINE, MEDICINES, POTION_BLUE, POTION_RED = C_ + 96, C_ + 97, C_ + 99, C_ + 100, C_ + 102, C_ + 103
BASKET, BASKET_GRAIN, BASKET_APPLE, BASKET_BREAD = C_ + 104, C_ + 105, C_ + 106, C_ + 107
LAB = C_ + 111
DOLL_BEAR, DOLL_BLUE, GIFTS = C_ + 112, C_ + 113, C_ + 118
ROPE_C = C_ + 122
JEWEL_A, NECKLACE, JEWEL_B = C_ + 125, C_ + 126, C_ + 127
SWORD, SWORDS, SWORDS_X, AXES, SPEARS, SPEARS_B, WHIP, KNIVES = (C_ + i for i in range(128, 136))
UTENSILS, DRY_FLOWERS, SHIELD_A, SHIELD_B = C_ + 136, C_ + 137, C_ + 138, C_ + 139
CLOTHES = (C_ + 140, C_ + 141, C_ + 142, C_ + 143)
SWORD_RACK_A, SWORD_RACK_B, HAMMERS, BOWS, ANVIL_A, ANVIL_B, BASIN_L, SCRAP = (C_ + i for i in range(144, 152))
HELMETS = (C_ + 152, C_ + 153, C_ + 154)
HATS = (C_ + 155, C_ + 156, C_ + 157)
ARMOR_STANDS = (C_ + 160, C_ + 161, C_ + 162, C_ + 163)
ROBES = (C_ + 166, C_ + 167)
CAPE = C_ + 165
REPO_SWORDS, REPO_SPEARS = (C_ + 174, C_ + 182), (C_ + 175, C_ + 183)
GOLD_BARS, SILVER_BARS = C_ + 200, C_ + 202
RAILING = C_ + 224


class Room(L.MapBuilder):
    """A single interior room: wall-top border, `face` rows of wall at the back, floor below.
    The map is sized to the room so there is no void."""

    def __init__(self, w, h, name, display, floor=WOOD, walls='int_wood', face=2, ambient='#ece6e0'):
        super().__init__(w, h, INSIDE, name, display)
        self.note = '<ambient: %s>' % ambient if ambient else ''
        top, side = WALLS[walls]
        self.WT, self.WF = ('A4', top), ('A4', side)
        self.rect(0, 0, w - 1, h - 1, self.WT)
        self.rect(1, 1, w - 2, face, self.WF)
        self.rect(1, face + 1, w - 2, h - 2, floor)
        self.floor_top = face + 1
        self.face = face

    def partition(self, x, y0, y1, face_rows=0):
        """Interior wall (top) between y0..y1 at column x, optionally with face rows below its end."""
        self.rect(x, y0, x, y1, self.WT)

    def wall_block(self, x0, y0, x1, y1, face_rows=2):
        self.rect(x0, y0, x1, y1 - face_rows, self.WT)
        self.rect(x0, y1 - face_rows + 1, x1, y1, self.WF)

    def counter(self, x0, y0, x1, y1, kind=TABLE_A):
        self.rect(x0, y0, x1, y1, kind, layer=1)

    def two(self, x, y_top, pair):
        """Two-tile furniture: top half on the upper layer at y_top, bottom half at y_top+1."""
        self.put(x, y_top, pair[0], 3); self.put(x, y_top + 1, pair[1], 2)

    def wide(self, x, y, rows):
        for r, row in enumerate(rows):
            for c, t in enumerate(row):
                self.put(x + c, y + r, t, 3 if r < len(rows) - 1 else 2)

    def exit_door(self, x, target, tx, ty, d=2):
        """Doorway in the bottom wall: carve it and put the touch exit there."""
        y = self.h - 1
        self.cell(x, y, self.auto[0][y - 1][x])
        self.add_event('Exit', x, y, [L.exit_page(target, tx, ty, d)])
        self.put(x, y - 1, 0)

    def keeper(self, name, x, y, sheet, idx, lines, commands=None, direction=2):
        speaker, *rest = lines
        cmds = say(speaker, *rest) + (commands or [])
        return self.add_event(name, x, y, [page(char(sheet, idx, direction), commands=cmds)])

    def npc(self, name, x, y, sheet, idx, lines, direction=2, move=0, speed=3, freq=3, route=None):
        speaker, *rest = lines
        return self.add_event(name, x, y, [page(char(sheet, idx, direction), move_type=move, commands=say(speaker, *rest),
                                                 speed=speed, freq=freq, route=route)])

    def obj(self, name, x, y, sheet, idx, lines=None, step=True, through=False, priority=1, direction=2):
        return self.add_event(name, x, y, [page(char(sheet, idx, direction), commands=text(*lines) if lines else None,
                                                 step_anim=step, walk_anim=step, through=through, priority=priority)])

    def look(self, name, x, y, lines):
        # same-as-characters priority so it can be read from the front (it sits on an impassable tile)
        return self.add_event(name, x, y, [page(None, commands=text(*lines), priority=1)])


def choice_shop(prompt_speaker, prompt, options):
    """Show Choices -> call a shop common event per option. options: [(label, ce_id), ...]; last choice = Leave."""
    labels = [o[0] for o in options] + ['Leave']
    out = say(prompt_speaker, prompt)
    out.append(cmd(102, [labels, len(labels) - 1, 0, 2, 0]))
    for i, (label, ce) in enumerate(options):
        out.append(cmd(402, [i, label], 0))
        out += common_event(ce, 1)
        out.append(cmd(0, [], 1))
    out.append(cmd(402, [len(options), 'Leave'], 0))
    out.append(cmd(0, [], 1))
    out.append(cmd(404, [], 0))
    return out
