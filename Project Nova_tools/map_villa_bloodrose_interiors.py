# Inside Villa Bloodrose (front doors on Map048; chapters 7 and 11). A standard castle plan of our own:
#                                   MAP061 Ballroom (the fight with David; its doors stay shut until switch 12)
#                                        || great doors between the stairs
#   1F  MAP053 Dining Room  =open=  MAP049 Grand Hall  =open=  MAP054 Music Room
#       kitchen and servants' doors (locked)   twin stairs up, the front doors
#   2F  MAP055 West Wing  =open=  MAP050 Gallery (balcony over the hall)  =open=  MAP056 East Wing
#       doors: the master's bedchamber (locked)  doors: MAP051 Library            doors: MAP057 Lysandre's Room,
#              MAP058 David's Study                    -> MAP052 Sealed Archive         MAP059 Guest Room (Kael, ch. 11),
#              two servants' rooms (locked)            (behind a false shelf)           MAP060 Blue Guest Room, linen (locked)
# Every room is its own map, so story events can happen inside it.
# The Sealed Archive (chapter 12) cannot be reached until the story opens the false shelf: give the library's
# 'False Bookshelf' event a page with the chapter's switch and a transfer to K.ARRIVE['archive_from_library'].
# Candlelit and dim (moods in map_moods.py). Furniture from PM_NobleInterior, PM_Beds and WizardCastle_B.
#   python map_villa_bloodrose_interiors.py preview.png [--grid]   -> preview_49.png ... preview_60.png
#   python map_villa_bloodrose_interiors.py --save                 -> write Map049-061 (editor must be closed)
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from interior_kit import *
import nova_maplib as L
import kingdom as K

NI = lambda n: L.ext('PM_NobleInterior', n)
BD = lambda n: L.ext('PM_Beds', n)
WZ = lambda n: L.ext('WizardCastle_B', n)
INVISIBLE_WALL = L.ext('Avy_Ship_B3', 1)          # a blank tile that blocks: keeps the player off wall tops

# ---------------------------------------------------------------- walls and floors (Inside A2/A4)
GOTHIC = (37, 45)            # grey ashlar between columns
THORN = (7, 15)              # violet wallpaper with thorned roses - the Bloodrose rooms
PANEL = (39, 47)             # dark wood panelling
FLOOR_MARBLE, FLOOR_PLUM, FLOOR_FLAG = ('A2', 29), ('A2', 19), ('A2', 9)
CARPET_RED, CARPET_NAVY = ('A2', 26), ('A2', 27)
TABLE_DARK = ('A2', 15)
DARKNESS = ('A5', 0)

# ---------------------------------------------------------------- furniture (checked on 1.4x crops)
# PM_NobleInterior
FIREPLACE = ((67, 68, 69), (75, 76, 77), (83, 84, 85))
PIANO = ((64, 65, 66), (72, 73, 74), (80, 81, 82))
GLASS_CABINET_A, GLASS_CABINET_B = (70, 78, 86), (71, 79, 87)
CURTAINED_WINDOW = ((48, 49), (56, 57))
RED_WINDOW = (51, 59)
VANITY, VANITY_B, GILT_MIRROR = (34, 42), (35, 43), (36, 44)
BUST, FLOOR_LAMP = (38, 46), (39, 47)
WINE_CABINET = (117, 125)
BOOKCASE = ((118, 119), (126, 127))
CHAIR_FRONT, CHAIR_BACK, CHAIR_RIGHT, CHAIR_LEFT, WING_CHAIR = (128, 136), (129, 137), (130, 138), (131, 139), (132, 140)
SIDEBOARD = ((133, 134, 135), (141, 142, 143))
GRANDFATHER_CLOCK = (144, 152)
WRITING_DESK = ((149, 150, 151), (157, 158, 159))
SHELF_BOOKS = (230, 238)
DRAWERS_TALL = (90, 98, 106)
WARDROBE = ((244, 245), (252, 253))
KNIGHT, BANNER = (246, 254), (247, 255)
PILLAR_TALL = (15, 23, 31)
PALM, POTTED_TREE = (216, 224), (218, 226)
POUF_PURPLE, ROUND_TABLE = 5, 2
# PM_Beds: a canopy (2x3, upper layer) stands over its bed (2x2)
CANOPY_RED, BED_RED = ((8, 9), (16, 17), (24, 25)), ((18, 19), (26, 27))
CANOPY_PURPLE, BED_PURPLE = ((12, 13), (20, 21), (28, 29)), ((22, 23), (30, 31))
CANOPY_GREEN, BED_GREEN = ((32, 33), (40, 41), (48, 49)), ((42, 43), (50, 51))
DRAPES_RED = ((36, 37), (44, 45))
PURPLE_WINDOW, RED_CURTAIN_WINDOW = (72, 80), (55, 63)
# WizardCastle_B
GOTHIC_WINDOW = (1, 9)                     # (2-4 / 10-12 is a triple window: never use 2,3 alone)
PORTRAIT_SMALL = 8
CANDELABRA = (19, 27)
CHANDELIER = 20
LANTERN = 29
STAIR = [(64, 65, 66), (72, 73, 74), (80, 81, 82), (88, 89, 90), (96, 97, 98), (104, 105, 106)]
TALL_SHELVES = ((128, 129, 130, 131, 132), (136, 137, 138, 139, 140), (144, 145, 146, 147, 148))
JAR_SHELVES = ((133, 134, 135), (141, 142, 143))
CURIO_CABINET = ((149, 150, 151), (157, 158, 159))
LECTERN = 79
WARD_CIRCLE = 15
COBWEB = 102

ITEM_NAMES = {1: 'Potion', 2: 'Magic Water', 5: 'Hi-Potion'}
CALM = {'name': '03_The_Calm', 'pan': 0, 'pitch': 90, 'volume': 70}
ROOMS = {}


def reg(mid):
    def deco(fn):
        ROOMS[mid] = fn
        return fn
    return deco


def name(mid): return K.NAMES[mid]


def place(r, f, x, y, rows):
    """Multi-tile object; the bottom row on the ground layer (2), the rows above on the upper layer (3)."""
    for i, row in enumerate(rows):
        for c, n in enumerate(row):
            if n is not None: r.put(x + c, y + i, f(n), 2 if i == len(rows) - 1 else 3)


def column(r, f, x, y, ids):
    place(r, f, x, y, [(n,) for n in ids])


def canopy_bed(r, x, y, canopy, bed):
    """Canopy rows y..y+2 over the bed's two rows y+1..y+2."""
    for i, row in enumerate(bed):
        for c, n in enumerate(row): r.put(x + c, y + 1 + i, BD(n), 2)
    for i, row in enumerate(canopy):
        for c, n in enumerate(row): r.put(x + c, y + i, BD(n), 3)


def stair(r, x, y):
    """WizardCastle_B wooden stair, 3x6, all on the ground layer so the player walks on it, not under it."""
    for i, row in enumerate(STAIR):
        for c, n in enumerate(row): r.put(x + c, y + i, WZ(n), 2)


def light(r, x, y, radius, color, flicker=True, oy=0):
    note = '<light: %d, %s%s%s>' % (radius, color, ', flicker' if flicker else '', ', %d' % oy if oy else '')
    r.add_event('Light', x, y, [page(None, priority=0, through=True)], note)


def candelabra(r, x, base_y):
    column(r, WZ, x, base_y - 1, CANDELABRA)
    light(r, x, base_y, 110, '#ffc070', oy=-36)


def chandelier(r, x, y):
    r.put(x, y, WZ(CHANDELIER), 3)
    light(r, x, y, 230, '#ffcf80', oy=-12)


def partition(r, x, y0, y1, gaps):
    r.rect(x, y0, x, y1, r.WT)
    for y in gaps: r.cell(x, y, r.auto[0][y][x - 1])


def seal_wall_tops(r):
    """A4 wall tops are passable in the tileset: put an invisible blocking tile over every one."""
    for y in range(r.h):
        for x in range(r.w):
            v = r.auto[0][y][x]
            if v and v[0] == 'A4' and v[1] < 8 or v and v[0] == 'A4' and 16 <= v[1] < 24 or v and v[0] == 'A4' and 32 <= v[1] < 40:
                if not r.top[1][y][x]: r.put(x, y, INVISIBLE_WALL, 3)
                elif not r.top[0][y][x]: r.put(x, y, INVISIBLE_WALL, 2)


def go(r, name, x, y, key, d=None):
    target, tx, ty, td = K.ARRIVE[key]
    r.add_event(name, x, y, [L.exit_page(target, tx, ty, d or td)])


def door(r, name, x, y, key, sheet='!Door1', style=0):
    target, tx, ty, td = K.ARRIVE[key]
    r.add_event(name, x, y, [L.door_page(target, tx, ty, td, sheet, style)])


def loot(r, name, x, y, item, n, where):
    found = [cmd(250, [{'name': 'Item3', 'volume': 80, 'pitch': 100, 'pan': 0}]), cmd(126, [item, 0, 0, n]),
             *text('Found %d \\C[6]%s\\C[0] %s!' % (n, ITEM_NAMES[item], where)), cmd(123, ['A', 0])]
    r.add_event('Loot: ' + name, x, y, [page(None, commands=found, priority=1),
                                         page(None, commands=text('Nothing else here.'), priority=1,
                                              cond={'selfSwitchValid': True, 'selfSwitchCh': 'A'})])


def room(w, h, mid, floor, walls, face=3, ambient='#6a5e7a'):
    r = Room(w, h, *name(mid), floor=floor, walls='stone', face=face, ambient=ambient)
    top, side = walls
    r.WT, r.WF = ('A4', top), ('A4', side)
    r.rect(0, 0, w - 1, h - 1, r.WT); r.rect(1, 1, w - 2, face, r.WF); r.rect(1, face + 1, w - 2, h - 2, floor)
    return r


# =========================================================================== The Bloodrose Library
@reg(K.VILLA_LIBRARY)
def library():
    W, H = 27, 24
    r = room(W, H, K.VILLA_LIBRARY, FLOOR_FLAG, PANEL)
    r.bgm = {'name': '03_The_Calm', 'pan': 0, 'pitch': 85, 'volume': 60}
    r.rect(11, 4, 15, H - 2, CARPET_NAVY)
    for x0 in (1, 6, 16, 21): place(r, WZ, x0, 2, TALL_SHELVES)
    for x in (12, 14): column(r, WZ, x, 2, GOTHIC_WINDOW); light(r, x, 3, 90, '#8a9cff', flicker=False)
    r.put(13, 5, WZ(LECTERN)); candelabra(r, 11, 5); candelabra(r, 15, 5)
    for y in (8, 16):
        for x0 in (2, 5, 8, 17, 20, 23): place(r, NI, x0, y, BOOKCASE)
    r.counter(10, 12, 16, 13, TABLE_DARK)
    for x in (10, 12, 14, 16):
        column(r, NI, x, 10, CHAIR_FRONT); column(r, NI, x, 14, CHAIR_BACK)
    for x, t in zip(range(10, 17), (BOOK_OPEN, NOTES, WZ(LANTERN), OLD_BOOK_OPEN, SCROLLS, WZ(LANTERN), BOOK)):
        r.put(x, 12, t, 3)
    for x, t in zip(range(10, 17), (OLD_BOOK, BOOK, MAP_C, BOOK_OPEN, NOTES, OLD_BOOK, SCROLLS)):
        r.put(x, 13, t, 3)
    light(r, 12, 12, 130, '#ffc070', oy=-10); light(r, 15, 12, 130, '#ffc070', oy=-10)
    chandelier(r, 13, 9); chandelier(r, 13, 18)
    for x in (1, 25): column(r, NI, x, 21, POTTED_TREE)
    candelabra(r, 4, 21); candelabra(r, 22, 21)
    r.exit_door(13, *K.ARRIVE['upper_from_library'])
    r.npc('Librarian', 19, 12, 'Evil', 7, ('Librarian:', 'Every book in this room was written, copied or stolen by a Bloodrose.',
          'Please do not ask which.'), direction=4)
    r.look('Lectern', 13, 5, ['A heavy book lies open: a family register. The first names are in a script no one uses any more.'])
    r.look('Book: The Age of Heroes', 3, 4, ['"...and the Twilight was not a light nor a darkness, but the hour between,',
                                              'when both are true at once." The rest of the page is water-stained.'])
    r.look('Book: Roses', 18, 4, ['"On the Keeping of Roses in Poor Soil." A pressed red petal marks a chapter on blood meal.',
                                  'Of course it does.'])
    r.look('False Bookshelf', 23, 4, ['The spines on this shelf are painted on.', 'It does not move. Not for you - not yet.'])
    loot(r, 'Reading Table', 16, 13, 2, 1, 'under a pile of notes')
    return r


# =========================================================================== The Sealed Archive
@reg(K.VILLA_ARCHIVE)
def archive():
    W, H = 15, 12
    r = room(W, H, K.VILLA_ARCHIVE, FLOOR_FLAG, GOTHIC, face=2, ambient='#4e4a66')
    r.bgm = {'name': '03_Creeping_Darkness', 'pan': 0, 'pitch': 90, 'volume': 60}
    r.rect(5, 3, 9, 9, CARPET_NAVY)
    place(r, WZ, 1, 2, CURIO_CABINET); place(r, WZ, 11, 2, CURIO_CABINET); place(r, WZ, 6, 2, JAR_SHELVES)
    r.put(7, 6, WZ(WARD_CIRCLE)); r.put(7, 5, WZ(LECTERN))
    light(r, 7, 6, 140, '#b070ff', flicker=False)
    candelabra(r, 4, 6); candelabra(r, 10, 6)
    for x0 in (1, 4, 9, 12): place(r, NI, x0 if x0 < 12 else 12, 8, BOOKCASE)
    r.put(1, 1, WZ(COBWEB), 3); r.put(13, 1, WZ(COBWEB), 3)
    r.look('Sealed Tome', 7, 5, ['A book chained shut to its stand. The chain is warm.',
                                 '(Its pages are for the story to open.)'])
    r.exit_door(7, *K.ARRIVE['library_from_archive'])
    return r


# =========================================================================== shared pieces
def side_gap(r, side, ys, key):
    """An open doorway in the side wall (no door): walking through it changes map."""
    x = 0 if side == 'w' else r.w - 1
    inner = 1 if side == 'w' else r.w - 2
    target, tx, ty, td = K.ARRIVE[key]
    for y in ys:
        r.cell(x, y, r.auto[0][y][inner])
        r.add_event('To ' + K.NAMES[target][1], x, y, [L.exit_page(target, tx, ty, td)])


def locked(r, name, x, y, lines, style=0):
    r.add_event(name, x, y, [L.door_page(0, 0, 0, locked_text=lines, index=style)])


# =========================================================================== Grand Hall
@reg(K.VILLA_HALL)
def hall():
    W, H = 31, 20
    r = room(W, H, K.VILLA_HALL, FLOOR_MARBLE, GOTHIC)
    r.bgm = CALM
    # twin stairs to the gallery, the family hearth between them, banners and moonlit windows
    for sx in (8, 20): stair(r, sx, 1)
    go(r, 'Stairs Up', 9, 2, 'upper_from_hall_w'); go(r, 'Stairs Up', 21, 2, 'upper_from_hall_e')
    r.put(15, 1, WZ(PORTRAIT_SMALL))
    target, tx, ty, td = K.ARRIVE['ballroom_from_hall']
    shut = page(char('!$Gate1', 0), commands=text('The great doors to the ballroom.',
                                                  'They are locked - and something heavy has been set against them from inside.'),
                walk_anim=False)
    open_ = L.door_page(target, tx, ty, td, '!$Gate1', 0)
    open_['conditions'].update({'switch1Valid': True, 'switch1Id': K.SW_VILLA_BALLROOM})
    r.add_event('Ballroom Doors', 15, 3, [shut, open_])
    light(r, 13, 4, 90, '#ffc070', oy=-40); light(r, 17, 4, 90, '#ffc070', oy=-40)
    for x in (13, 17): column(r, NI, x, 2, BANNER)
    for x in (2, 5, 12, 18, 25, 28): column(r, WZ, x, 2, GOTHIC_WINDOW); light(r, x, 3, 80, '#8a9cff', flicker=False)
    # carpets: the runner from the doors, the landing between the stairs, the cross-walk to the side rooms
    r.rect(14, 5, 16, H - 2, CARPET_RED); r.rect(8, 7, 22, 8, CARPET_RED); r.rect(1, 13, W - 2, 14, CARPET_RED)
    chandelier(r, 15, 10); chandelier(r, 15, 16)
    for x in (12, 18):
        candelabra(r, x, 11); candelabra(r, x, 17)
    for x in (1, W - 2):
        column(r, NI, x, 8, KNIGHT); column(r, NI, x, 16, KNIGHT)
    for x in (5, 25): column(r, NI, x, 9, BUST)
    for x in (13, 17): column(r, NI, x, 17, PALM)
    side_gap(r, 'w', (13, 14), 'villa_dining_from_hall'); side_gap(r, 'e', (13, 14), 'villa_music_from_hall')
    r.exit_door(15, *K.ARRIVE['bloodrose_from_hall'])
    r.npc('Footman', 11, 15, 'Evil', 4, ('Footman:', 'Guests are announced. You were not announced.',
                                         'I shall announce you. Very loudly.'))
    r.npc('Maid', 22, 10, 'Evil', 5, ('Maid:', 'Mind the floor, please - I polished it for a ball nobody came to.'),
          move=1, freq=2)
    return r


# =========================================================================== Dining Room (west of the hall)
@reg(K.VILLA_DINING)
def dining():
    W, H = 17, 17
    r = room(W, H, K.VILLA_DINING, CARPET_NAVY, GOTHIC)
    r.bgm = CALM
    r.counter(4, 8, 12, 9, TABLE_DARK)
    for x in (4, 6, 8, 10, 12):
        column(r, NI, x, 6, CHAIR_FRONT); column(r, NI, x, 10, CHAIR_BACK)
    column(r, NI, 3, 8, CHAIR_RIGHT); column(r, NI, 13, 8, CHAIR_LEFT)
    for x, t in zip(range(4, 13), (PLATE, WINE_GLASS, DINNER, BOWL, FRUIT_BOWL, BOWL, DINNER, WINE_GLASS, PLATE)):
        r.put(x, 8, t, 3)
    for x, t in zip(range(4, 13), (BOWL, PLATE, WINE_GLASS, PLATE, CAKE, PLATE, WINE_GLASS, PLATE, BOWL)):
        r.put(x, 9, t, 3)
    light(r, 6, 8, 140, '#ffc070', oy=-8); light(r, 10, 9, 140, '#ffc070', oy=-8)
    place(r, NI, 2, 2, CURTAINED_WINDOW); place(r, NI, 13, 2, CURTAINED_WINDOW)
    for x in (2, 3, 13, 14): light(r, x, 3, 60, '#8a9cff', flicker=False)
    column(r, NI, 5, 3, WINE_CABINET); column(r, NI, 6, 2, GLASS_CABINET_A); column(r, NI, 7, 2, GLASS_CABINET_B)
    column(r, NI, 9, 3, GRANDFATHER_CLOCK)
    locked(r, 'Kitchen Door', 11, 3, ['Warm air and the smell of bread come round the edges of this door.',
                                      'The kitchen, by the sound of the pans. It is bolted from the other side.'])
    locked(r, "Servants' Door", 15, 3, ["A plain door, no carving: the servants' hall.", 'It is locked.'])
    r.npc('Kitchen Maid', 11, 5, 'Evil', 6, ('Kitchen Maid:', 'That door? The kitchen.',
                                             "Cook doesn't let guests in. Cook barely lets the master in."))
    place(r, NI, 2, 13, SIDEBOARD); loot(r, 'Sideboard', 3, 14, 2, 1, 'in the sideboard')
    candelabra(r, 14, 15); candelabra(r, 6, 15)
    column(r, NI, 1, 6, POTTED_TREE)
    side_gap(r, 'e', (12, 13), 'villa_hall_from_dining')
    return r


# =========================================================================== Music Room (east of the hall)
@reg(K.VILLA_MUSIC)
def music():
    W, H = 17, 17
    r = room(W, H, K.VILLA_MUSIC, FLOOR_PLUM, GOTHIC)
    r.bgm = CALM
    place(r, BD, 1, 2, DRAPES_RED); place(r, BD, 14, 2, DRAPES_RED)
    for x in (4, 8, 12): column(r, WZ, x, 2, GOTHIC_WINDOW); light(r, x, 3, 80, '#8a9cff', flicker=False)
    place(r, NI, 7, 4, PIANO)
    chandelier(r, 8, 10)
    for y in (8, 12): column(r, NI, 15, y, CHAIR_LEFT)
    column(r, NI, 1, 8, CHAIR_RIGHT)
    for x in (5, 11): column(r, NI, x, 14, CHAIR_BACK)
    candelabra(r, 2, 15); candelabra(r, 14, 15); candelabra(r, 5, 6); candelabra(r, 11, 6)
    r.look('Sheet Music', 8, 6, ["A nocturne in a lady's hand. The last page is unfinished, the ink only a week old."])
    r.npc('Maid', 9, 8, 'Evil', 7, ('Maid:', 'The young mistress plays at night, when she thinks no one listens.',
                                   'Everyone listens.'), direction=8)
    side_gap(r, 'w', (12, 13), 'villa_hall_from_music')
    return r


# =========================================================================== Gallery (upper floor, over the hall)
@reg(K.VILLA_UPPER)
def upper():
    W, H = 31, 16
    r = room(W, H, K.VILLA_UPPER, CARPET_NAVY, THORN)
    r.bgm = CALM
    # the balcony over the hall, with the stairs down at either end of it
    r.rect(10, 12, 20, 14, DARKNESS)
    for x in range(10, 21): r.put(x, 11, RAILING)
    for x in (9, 21): r.put(x, 14, STAIRS_DOWN[3])
    go(r, 'Stairs Down', 9, 14, 'hall_from_upper_w'); go(r, 'Stairs Down', 21, 14, 'hall_from_upper_e')
    # the Gallery of Ancestors along the north wall, the library doors in the middle
    door(r, 'Library Doors', 15, 3, 'library_from_upper')
    for x, t in ((2, PORTRAIT_A), (5, PAINTING_A), (8, PORTRAIT_B), (22, PAINTING_B), (25, PORTRAIT_A), (28, PORTRAIT_B)):
        r.put(x, 3, t)
    r.put(11, 3, WZ(PORTRAIT_SMALL)); r.put(19, 3, WZ(PORTRAIT_SMALL))
    r.look('Portrait', 11, 3, ['A man in silver armour, his face lost to a bright smear of paint.',
                               'Beneath, in an old hand: "To him the oath was sworn. By him it is kept."'])
    r.look('Portrait', 19, 3, ['"David Bloodrose I." He has his descendant\'s eyes, and a sword at his side.'])
    for x in (13, 17): column(r, WZ, x, 2, GOTHIC_WINDOW); light(r, x, 3, 70, '#8a9cff', flicker=False)
    for x in (4, 26): column(r, NI, x, 4, BUST)
    for x in (7, 23): candelabra(r, x, 5)
    chandelier(r, 15, 8)
    column(r, NI, 1, 13, POTTED_TREE); column(r, NI, W - 2, 13, POTTED_TREE)
    side_gap(r, 'w', (6, 7), 'west_from_upper'); side_gap(r, 'e', (6, 7), 'east_from_upper')
    return r


def wing(mid, gap_side, gap_key, doors):
    """A corridor wing: doors along its north wall, the open end into the gallery."""
    W, H = 26, 9
    r = room(W, H, mid, CARPET_NAVY, THORN)
    r.bgm = CALM
    near = {d[1] + k for d in doors for k in (-1, 0, 1)}
    for x in range(2, W - 2, 3):
        if x in near: continue
        column(r, BD, x, 2, PURPLE_WINDOW); light(r, x, 3, 60, '#8a9cff', flicker=False)
    for kind, x, label, what in doors:
        if kind == 'door':
            door(r, label, x, 3, what); r.put(x, 1, WZ(PORTRAIT_SMALL))
        else:
            locked(r, label, x, 3, what)
    side_gap(r, gap_side, (5, 6), gap_key)
    column(r, NI, 1 if gap_side == 'e' else W - 2, 5, POTTED_TREE)
    return r


@reg(K.VILLA_WEST)
def west_wing():
    r = wing(K.VILLA_WEST, 'e', 'upper_from_west', [
        ('locked', 4, "Master's Bedchamber", ['Black wood, a silver rose for a handle.',
                                                'The master\'s own chamber. You do not need to try the handle to know.']),
        ('door', 10, "Master's Study", 'study_from_west'),
        ('locked', 16, "Servants' Room", ['A narrow door. Someone has scratched a little rose into the frame.',
                                          "Locked - the maids' room."]),
        ('locked', 21, "Servants' Room", ['Snoring on the other side. Locked.'])])
    for x in (7, 13, 19): candelabra(r, x, 5)
    r.npc('Maid', 14, 6, 'Evil', 5, ('Maid:', "That first door is the master's bedchamber.",
                                    'No one goes in. Not even me, and I dust everything.'), move=1, freq=2)
    return r


@reg(K.VILLA_EAST)
def east_wing():
    r = wing(K.VILLA_EAST, 'w', 'upper_from_east', [
        ('door', 5, "Lysandre's Room", 'lysandre_from_east'),
        ('door', 11, 'Guest Room', 'guest_from_east'),
        ('door', 17, 'Blue Guest Room', 'guest2_from_east'),
        ('locked', 22, 'Linen Room', ['Lavender and starch. The linen room - locked.'])])
    for x in (8, 14, 20): candelabra(r, x, 5)
    r.npc('Maid', 9, 6, 'Evil', 6, ('Maid:', "The young mistress's room is the first door.",
                                   'Knock - she pretends not to hear.'), move=1, freq=2)
    return r


# =========================================================================== the rooms
@reg(K.VILLA_LYSANDRE)
def lysandre_room():
    W, H = 12, 10
    r = room(W, H, K.VILLA_LYSANDRE, FLOOR_PLUM, THORN)
    r.bgm = CALM
    canopy_bed(r, 1, 3, CANOPY_PURPLE, BED_PURPLE)
    column(r, NI, 4, 3, VANITY)
    r.put(5, 2, WORLD_MAP[0]); r.put(6, 2, WORLD_MAP[1])
    column(r, BD, 7, 2, PURPLE_WINDOW); light(r, 7, 3, 70, '#8a9cff', flicker=False)
    place(r, NI, 8, 3, WARDROBE)
    column(r, NI, 10, 3, SHELF_BOOKS)
    r.put(8, 7, NI(ROUND_TABLE)); r.put(8, 7, TEAPOT, 3); r.put(9, 7, NI(POUF_PURPLE))
    candelabra(r, 1, 8); candelabra(r, 10, 8)
    r.look('Pinned Map', 5, 3, ['A map of the continent, stuck full of pins - every harbour, every far city.',
                                'Not one of the pins has a thread back to this house.'])
    r.look('Travel Books', 10, 4, ['"A Sailor\'s Guide to the Southern Isles." "The Roads of Arulustus." "Snow and Silence."',
                                   'All well thumbed. None of the pages are bookmarked with tickets.'])
    r.exit_door(6, *K.ARRIVE['east_from_lysandre'])
    return r


@reg(K.VILLA_STUDY)
def study():
    W, H = 12, 10
    r = room(W, H, K.VILLA_STUDY, CARPET_RED, PANEL)
    r.bgm = CALM
    place(r, NI, 1, 3, BOOKCASE); place(r, NI, 9, 3, BOOKCASE)
    column(r, NI, 3, 3, GRANDFATHER_CLOCK)
    r.put(4, 2, WALL_SWORDS)
    column(r, NI, 6, 2, RED_WINDOW); light(r, 6, 3, 70, '#8a9cff', flicker=False)
    column(r, NI, 8, 3, BUST)
    column(r, NI, 6, 4, CHAIR_FRONT)
    place(r, NI, 5, 6, WRITING_DESK); light(r, 7, 6, 120, '#ffc070', oy=-20)
    candelabra(r, 1, 8); candelabra(r, 10, 8)
    r.look('Letters', 5, 7, ['Letters in a hand that slants like rain. Most begin "My dear Lysandre" and are never sent.'])
    r.npc('David Bloodrose', 9, 7, 'Evil', 1, ('David Bloodrose:', 'So. You are the ones who crossed my bridge.',
                                               'Sit, if you wish. I have outlived more hurried guests than you.'),
          direction=4)
    r.exit_door(6, *K.ARRIVE['west_from_study'])
    return r


@reg(K.VILLA_GUEST)
def guest_room():
    W, H = 11, 9
    r = room(W, H, K.VILLA_GUEST, CARPET_RED, THORN)
    r.bgm = CALM
    canopy_bed(r, 6, 3, CANOPY_RED, BED_RED)
    column(r, BD, 4, 2, RED_CURTAIN_WINDOW); light(r, 4, 3, 70, '#8a9cff', flicker=False)
    column(r, NI, 2, 3, VANITY_B)
    r.put(9, 4, DRESSER); loot(r, 'Dresser', 9, 4, 5, 1, 'in the dresser')
    column(r, NI, 2, 6, CHAIR_RIGHT)
    candelabra(r, 9, 7)
    r.look('Guest Bed', 6, 5, ['Fresh linen, turned down. Someone in this house always expects a guest.'])
    r.exit_door(5, *K.ARRIVE['east_from_guest'])
    return r


@reg(K.VILLA_GUEST2)
def guest_room_2():
    W, H = 11, 9
    r = room(W, H, K.VILLA_GUEST2, CARPET_NAVY, THORN)
    r.bgm = CALM
    canopy_bed(r, 2, 3, CANOPY_GREEN, BED_GREEN)
    column(r, BD, 5, 2, PURPLE_WINDOW); light(r, 5, 3, 70, '#8a9cff', flicker=False)
    column(r, NI, 7, 2, DRAWERS_TALL)
    column(r, NI, 8, 3, FLOOR_LAMP); light(r, 8, 4, 100, '#ffc070', oy=-30)
    r.put(8, 6, NI(ROUND_TABLE)); r.put(8, 6, BOOK, 3); column(r, NI, 9, 5, CHAIR_LEFT)
    candelabra(r, 1, 7)
    r.look('Writing Set', 8, 6, ['Paper, ink, a seal with a rose on it - left out for whoever sleeps here next.'])
    r.exit_door(5, *K.ARRIVE['east_from_guest2'])
    return r


# =========================================================================== Ballroom (behind the hall)
@reg(K.VILLA_BALLROOM)
def ballroom():
    """The largest room of the house and the stage for the fight with David: an open dance floor with the dais and
    the master's chair at the far end. Battle positions: David on the dais steps (15, 8), the party (15, 16)."""
    W, H = 31, 24
    r = room(W, H, K.VILLA_BALLROOM, FLOOR_PLUM, GOTHIC)
    r.bgm = {'name': '03_Ancient_Castle', 'pan': 0, 'pitch': 90, 'volume': 70}
    # the dais: the family hearth, the master's chair before it, knights and banners either side
    r.rect(9, 4, 21, 7, CARPET_RED)
    place(r, NI, 14, 2, FIREPLACE); light(r, 15, 3, 190, '#ff9040', oy=30)
    place(r, lambda n: n, 14, 5, THRONE)
    for x in (12, 18): column(r, NI, x, 2, BANNER)
    for x in (10, 20): column(r, NI, x, 5, KNIGHT)
    r.look("Master's Chair", 15, 6, ['A tall chair of black wood before the fire.',
                                     'Above the hearth an iron rose, its petals worn bright by generations of hands.'])
    # tall windows and drapes along the north wall
    for x in (3, 6, 9, 21, 24, 27): column(r, WZ, x, 2, GOTHIC_WINDOW); light(r, x, 3, 80, '#8a9cff', flicker=False)
    place(r, BD, 1, 2, DRAPES_RED); place(r, BD, 28, 2, DRAPES_RED)
    # the dance floor, with columns at its corners and three chandeliers over it
    r.rect(5, 9, 25, 19, FLOOR_MARBLE); r.rect(14, 8, 16, 8, CARPET_RED); r.rect(14, 20, 16, H - 2, CARPET_RED)
    for x in (4, 26):
        column(r, NI, x, 9, PILLAR_TALL); column(r, NI, x, 17, PILLAR_TALL)
    chandelier(r, 15, 11); chandelier(r, 9, 15); chandelier(r, 21, 15)
    for x in (2, 28):
        for base in (9, 14, 19): candelabra(r, x, base)
    for x in (1, W - 2): column(r, NI, x, 21, POTTED_TREE)
    for x in (11, 19): candelabra(r, x, 22)
    r.exit_door(15, *K.ARRIVE['hall_from_ballroom'])
    return r


def build():
    rooms = {mid: fn() for mid, fn in ROOMS.items()}
    for r in rooms.values(): seal_wall_tops(r)
    return rooms


if __name__ == '__main__':
    out = next((a for a in sys.argv[1:] if not a.startswith('--')), None)
    rooms = build()
    if out:
        for mid, r in rooms.items(): r.render(out.replace('.png', '_%d.png' % mid), scale=0.5, grid='--grid' in sys.argv)
    if '--save' in sys.argv:
        for mid, r in rooms.items():
            r.save(mid, parent_id=K.VILLA_BLOODROSE, order=mid)
            print('saved Map%03d' % mid)
