# Building blocks for the Royal Magic Academy's interiors (Wizard Castle tileset = 20: WizardCastle_A2/A4/B, with
# Inside_B as its C sheet and Inside_C as its D sheet). A map holds several rooms: the whole map starts as wall top
# (the black ceiling), each room gets its back-wall face rows and its floor, and doorways are carved between them.
import nova_maplib as L
from nova_maplib import page, cmd, text, say, char
import interior_kit as I

WIZARD = 20
# ---------------------------------------------------------------- floors (A2) and walls (A4 top, face)
WOOD, STONE, FLEUR_CYAN, FLEUR_GREY, CHECK_CYAN = (('A2', k) for k in (1, 2, 3, 4, 5))
PLUM_WOOD, FLEUR_RED, OAK, FLEUR_VIOLET = (('A2', k) for k in (8, 9, 10, 11))
WALLS = {'stone': (0, 8), 'wood': (1, 9), 'stone2': (2, 10), 'rune': (3, 11), 'oak': (4, 12), 'stone3': (5, 13)}


# ---------------------------------------------------------------- Inside_B / Inside_C ids, moved to the C / D slots
def ib(n): return 256 + n if isinstance(n, int) else tuple(ib(v) for v in n)
def ic(n): return 256 + n if isinstance(n, int) else tuple(ic(v) for v in n)     # interior_kit's C_ ids are 256 + i


BED, CHEAP_BED, CLOSET, DRESSER, CABINET = ib(I.BED), ib(I.CHEAP_BED), ib(I.CLOSET), ib(I.DRESSER), ib(I.CABINET)
BOOKSHELF_A, BOOKSHELF_B, DRAWERS = ib(I.BOOKSHELF_A), ib(I.BOOKSHELF_B), ib(I.DRAWERS)
TABLE_ROUND, TABLE_MARBLE, TABLE_CLOTH, MINI_TABLE, CHAIR, STOOL = (ib(v) for v in (I.TABLE_ROUND, I.TABLE_MARBLE,
                                                                                    I.TABLE_CLOTH, I.MINI_TABLE, I.CHAIR, I.STOOL_A))
FIREPLACE_STONE, CLOCK, PILLAR, TAPESTRY, CURTAINS = ib(I.FIREPLACE_STONE), ib(I.CLOCK), ib(I.PILLAR), ib(I.TAPESTRY), ib(I.CURTAINS_RED)
THRONE, PIANO, MIRROR, WORLD_MAP = ib(I.THRONE), ib(I.PIANO), ib(I.MIRROR), ib(I.WORLD_MAP)
PORTRAIT_A, PORTRAIT_B, PAINTING_A, NOTICE = ib(I.PORTRAIT_A), ib(I.PORTRAIT_B), ib(I.PAINTING_A), ib(I.NOTICE)
STAIRS_UP, STAIRS_DOWN = ib(I.STAIRS_UP), ib(I.STAIRS_DOWN)
WIN_LARGE, STAINED = ib(I.WIN_LARGE), ib(I.STAINED)
POT_A, POT_B, BARREL, CRATES, SACKS, OVEN, SINK, SHELF_JARS, SHELF_BOTTLES = (ib(v) for v in (
    I.POT_A, I.POT_B, I.BARREL, I.CRATES_STACK, I.SACKS, I.OVEN, I.SINK, I.SHELF_JARS, I.SHELF_BOTTLES))
MEDICINE_SHELF, WALL_SWORDS_X, WALL_SHIELD, BASIN, TUB = ib(I.MEDICINE_SHELF), ib(I.WALL_SWORDS_X), ib(I.WALL_SHIELD), ib(I.BASIN), ib(I.TUB_A)
# Inside_C (table-top things and small props)
BOOK, BOOK_OPEN, OLD_BOOK, OLD_BOOK_OPEN, NOTES, SCROLLS, MAP_C = (ic(v) for v in (
    I.BOOK, I.BOOK_OPEN, I.OLD_BOOK, I.OLD_BOOK_OPEN, I.NOTES, I.SCROLLS, I.MAP_C))
CUP_TEA, TEAPOT, MUG, PLATE, BOWL, PIE, CAKE, ROAST, FRUIT_BOWL, BREAD = (ic(v) for v in (
    I.CUP_TEA, I.TEAPOT, I.MUG, I.PLATE, I.BOWL, I.PIE, I.CAKE, I.ROAST_PIG, I.FRUIT_BOWL, I.BASKET_BREAD))
VASE, PLANT_A, PLANT_B, PLANTER, POTION_BLUE, POTION_RED, MEDICINES, LAB = (ic(v) for v in (
    I.VASE, I.PLANT_A, I.PLANT_B, I.PLANTER, I.POTION_BLUE, I.POTION_RED, I.MEDICINES, I.LAB))
DOLL_BEAR, GIFTS, HATS, ROBES, DRY_FLOWERS, UTENSILS = ic(I.DOLL_BEAR), ic(I.GIFTS), ic(I.HATS), ic(I.ROBES), ic(I.DRY_FLOWERS), ic(I.UTENSILS)
ANGEL_STATUE = (ic(I.C_ + 169), ic(I.C_ + 177))           # Inside_C's angel statue, top and base

# ---------------------------------------------------------------- WizardCastle_B: (rows of tile numbers), top-left first
WC = {
    'window': [(1,), (9,)], 'window2': [(2, 3), (10, 11)], 'window_r': [(4,), (12,)], 'orb_window': [(5,), (13,)],
    'seal_blue': [(6,)], 'seal_violet': [(7,)], 'seal_blue2': [(14,)], 'seal_violet2': [(15,)],
    'painting': [(8,)], 'sigil': [(16, 17, 18), (24, 25, 26)],
    'candelabra': [(19,), (27,)], 'chandelier': [(20,)], 'chandelier2': [(21,)], 'chandelier3': [(22,)],
    'clock': [(23,), (31,)], 'clock2': [(247,), (255,)], 'frame': [(28,)], 'lantern': [(29,)], 'lantern2': [(30,)],
    'sign_brooms': [(32,)], 'sign_wands': [(33,)], 'sign_cauldrons': [(34, 35)],
    'hat_blue': [(36,)], 'hat_star': [(37,)], 'hat_cat': [(38,)], 'crystal_ball': [(39,)],
    'broom': [(40, 41, 42)], 'books': [(43,)], 'books2': [(44,)], 'books3': [(45,)],
    'chest_stack': [(46, 47), (54, 55)], 'chest': [(52, 53)],
    'cauldron_green': [(48, 49), (56, 57)], 'cauldron_blue': [(50, 51), (58, 59)], 'crate': [(60, 61)], 'cat': [(63,)],
    'staircase': [(64, 65, 66), (72, 73, 74), (80, 81, 82), (88, 89, 90), (96, 97, 98), (104, 105, 106)],
    'chairs2': [(67, 68)], 'chair_back': [(69,)], 'chair_l': [(75,)], 'chair_r': [(76,)], 'chair': [(77,)], 'stool': [(78,)],
    'side_table': [(71,)], 'lectern': [(79,)],
    'armchair': [(86, 87), (94, 95)], 'desk_books': [(91, 92, 93)],
    'cobweb': [(102, 103), (110, 111)], 'cobweb2': [(107, 108), (115, 116)], 'cobweb3': [(118, 119), (126, 127)],
    'mat_wood': [(112,)], 'mat_red': [(113,)], 'mat_grey': [(114,)],
    'shelf_tall': [(128, 129, 130, 131, 132), (136, 137, 138, 139, 140), (144, 145, 146, 147, 148)],
    'shelf3': [(128, 129, 130), (136, 137, 138), (144, 145, 146)],
    'cabinet': [(133, 134, 135), (141, 142, 143)], 'glass_cabinet': [(149, 150, 151), (157, 158, 159)],
    'long_desk': [(152, 153, 154, 155, 156), (160, 161, 162, 163, 164)],
    'desk_set': [(165, 166, 167), (173, 174, 175)],
    'study_desk': [(168, 169), (176, 177), (184, 185)], 'study_desk2': [(170, 171), (178, 179), (186, 187)],
    'class_desks': [(180, 181, 182, 183), (188, 189, 190, 191)],
    'vase_flowers': [(194,)], 'orb_pedestal': [(195,), (203,)], 'orb_light': [(202,)],
    'counter': [(196, 197), (204, 205)], 'counter_wide': [(196, 197, 198, 199), (204, 205, 206, 207)],
    'table_long': [(200, 201)], 'table_long2': [(208, 209)],
    'desk_lamp': [(210,)], 'desk_globe': [(211,)], 'desk_potions': [(218,)], 'desk_sack': [(219,)],
    'drawers': [(216, 217), (224, 225)], 'drawers2': [(232, 233), (240, 241)],
    'apothecary': [(220, 221, 222), (228, 229, 230), (236, 237, 238)],
    'skull_shelf': [(223,), (231,)], 'plant': [(239,)], 'witch_desk': [(226,)], 'globe_desk': [(227,)],
    'chandelier_black': [(234, 235), (242, 243)], 'arcane_device': [(244,)], 'doll': [(245, 246), (253, 254)],
    'broom_stand': [(252,)],
}


class AcademyMap(L.MapBuilder):
    """Several rooms on one map. Everything starts as wall top; room() opens a room with its back wall."""

    def __init__(self, w, h, name, display, ambient='#e8e4f0'):
        super().__init__(w, h, WIZARD, name, display)
        self.note = '<ambient: %s>' % ambient if ambient else ''
        self.default_top = ('A4', WALLS['rune'][0])
        self.rect(0, 0, w - 1, h - 1, self.default_top)

    def room(self, x0, y0, x1, y1, floor, wall='rune', face=3):
        """Room whose walls are x0-1 / x1+1 / y0-1 (wall top). Rows y0..y0+face-1 are the back wall's face."""
        top, side = WALLS[wall]
        self.rect(x0, y0, x1, y0 + face - 1, ('A4', side))
        self.rect(x0, y0 + face, x1, y1, floor)
        return (x0, y0 + face, x1, y1)              # the floor

    def opening(self, x0, y0, x1, y1, floor):
        """A doorway or archway: floor carved through walls."""
        self.rect(x0, y0, x1, y1, floor)

    def obj(self, name, x, y, ground=1):
        rows = WC[name]
        for r, row in enumerate(rows):
            for c, n in enumerate(row):
                self.put(x + c, y + r, n, 2 if r >= len(rows) - ground else 3)

    def two(self, x, y_top, pair):
        self.put(x, y_top, pair[0], 3); self.put(x, y_top + 1, pair[1], 2)

    def wide(self, x, y, rows):
        for r, row in enumerate(rows):
            for c, t in enumerate(row):
                self.put(x + c, y + r, t, 3 if r < len(rows) - 1 else 2)

    def counter(self, x0, y0, x1, y1, kind=I.TABLE_A):
        self.rect(x0, y0, x1, y1, kind, layer=1)

    # ------------------------------------------------------------ events
    def go(self, name, x, y, target, tx, ty, d=2, door=None):
        """A transfer: a touch tile (stairs, archway), or a door that opens (door = !Door1 style)."""
        if door is None:
            return self.add_event(name, x, y, [L.exit_page(target, tx, ty, d)])
        return self.add_event(name, x, y, [L.door_page(target, tx, ty, d, '!Door1', door)])

    def npc(self, name, x, y, sheet, idx, lines, direction=2, move=0, speed=3, freq=3, route=None, extra=None):
        speaker, *rest = lines
        cmds = say(speaker, *rest) + (extra or [])
        return self.add_event(name, x, y, [page(char(sheet, idx, direction), move_type=move, commands=cmds,
                                                 speed=speed, freq=freq, route=route)])

    def critter(self, name, x, y, sheet, idx, se, line, move=1, freq=3, area=None):
        """An animal; area (x1, y1, x2, y2) keeps it inside (NovaPens)."""
        cmds = ([cmd(250, [{'name': se, 'volume': 70, 'pitch': 100, 'pan': 0}])] if se else []) + text(line)
        return self.add_event(name, x, y, [page(char(sheet, idx), move_type=move, commands=cmds, freq=freq)],
                              note='<pen: %d,%d,%d,%d>' % area if area else '')

    def look(self, name, x, y, lines):
        return self.add_event(name, x, y, [page(None, commands=text(*lines), priority=1)])

    def flame(self, x, y, idx=0):
        return self.add_event('Candle', x, y, [page(char('!Flame', idx), step_anim=True, walk_anim=False, through=True, priority=2)])
