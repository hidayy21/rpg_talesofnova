# The Royal Magic Academy of Nova, inside (MAP032-038). Laid out like an old college around its quadrangle: the
# front door opens into the Entrance Hall with the grand staircase, the Great Hall (dining hall: four long tables,
# the faculty's high table on a dais) through the doors on one side and the Registry on the other; behind it the Cloister Court, the open quad with the Star
# Tower on its north range, the Lecture Wing west and the Library and Infirmary east; the Undercroft (alchemy
# laboratory, kitchens, stores) below; dormitories, the students' common room, the professors' rooms and the
# Archmage's study on the upper floor with the Enchanting Workshop, the Hall of Familiars and the faculty's offices.
# The students (some two hundred and forty) live in two dormitory towers, Dawnward and Duskward; their doors open
# off the common room, but only students go in.
#   MAP032 Entrance Hall & Registry   041 Great Hall   033 Cloister Court   034 Lecture Wing
#   035 Library & Infirmary   036 Undercroft   037 Upper Floor   038 Star Tower
#   python map_academy_castle.py preview.png [--grid]   -> preview_<id>.png for every map
#   python map_academy_castle.py --save                 -> write them all (editor must be closed)
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from academy_kit import *
import nova_maplib as L
from nova_maplib import page, cmd, text, char
import kingdom as K
import town_kit as T

A = K.ARRIVE
MAPS = {}


def reg(mid, parent):
    def deco(fn):
        MAPS[mid] = (fn, parent)
        return fn
    return deco


def at(key): return A[key][1:3]
def dest(key): return A[key]


def long_table(m, x, y0, y1):
    """A long table (a column of clothed tables) with chairs on both sides, laid with empty plates and cups."""
    for i, y in enumerate(range(y0, y1 + 1)):
        m.put(x, y, TABLE_CLOTH); m.put(x, y, (PLATE, CUP_TEA)[i % 2], 3)
        m.put(x - 1, y, CHAIR); m.put(x + 1, y, CHAIR)


# students: (sheet, index) for variety, and things students say
STUDENT_LOOKS = [('Actor2', 4), ('Actor2', 5), ('Actor2', 7), ('Actor3', 7), ('People1', 0), ('People1', 5), ('People2', 0),
                 ('People2', 1), ('People2', 3), ('People2', 4), ('People3', 0), ('People4', 0), ('People1', 4), ('People3', 1)]
STUDENT_LINES = [
    'Dawnward is two merits ahead. Two!', 'Duskward will win the merit orb this year. We always do.',
    'I\'m not hungry. I have Wards in an hour.', 'Has anyone seen my familiar? He\'s a toad. He answers to Bartholomew.',
    'Professor Wyndmere\'s lectures were the only ones nobody skipped. I miss them.', 'The Great Hall only fills up for feasts. Next one\'s at the solstice!',
    'If the staircase moves again, I\'m sleeping in the library.', 'Third years get to use the Practice Hall after dark. Lucky.',
    'My essay on ley lines is due tomorrow. I haven\'t started. I haven\'t even found the library.',
    'They say the black door in the Undercroft opens once a century.', 'I want to be a Class 4 when I graduate. Class 3, if I\'m brave.',
    'The Star Tower professor says the stars are "restless". What does that even mean?',
    'Dawnward Tower has seven hundred steps. I counted. Twice.', 'Duskward Tower creaks at night. The prefects say it\'s "character".',
    'Don\'t sit there, that\'s where the Archmage\'s cat sleeps.', 'I enchanted my quill to write by itself. Now it writes poetry. Bad poetry.',
]


def crowd(m, spots, seed=0):
    """Students at the given spots: (x, y, direction[, move]). Looks and lines go round the lists from `seed`."""
    for i, spot in enumerate(spots):
        x, y, d = spot[:3]
        move = spot[3] if len(spot) > 3 else 0
        sheet, idx = STUDENT_LOOKS[(seed + i) % len(STUDENT_LOOKS)]
        m.npc('Student', x, y, sheet, idx, ('Student:', STUDENT_LINES[(seed * 3 + i) % len(STUDENT_LINES)]), direction=d,
              move=move, freq=3 if move else 3)


# =========================================================================== MAP032 Entrance Hall & Registry
@reg(K.ACADEMY_HALL, K.ACADEMY)
def entrance_hall():
    W, H = 30, 22
    m = AcademyMap(W, H, *K.NAMES[K.ACADEMY_HALL])
    m.bgm = {'name': 'Castle2', 'pan': 0, 'pitch': 100, 'volume': 70}
    SX = 9                                                       # the grand staircase's middle column
    m.room(1, 1, 18, H - 2, STONE, 'rune')                       # the Entrance Hall
    m.room(20, 1, 28, H - 2, OAK, 'oak')                         # the Registry
    m.opening(19, 14, 19, 15, STONE)
    m.opening(SX, H - 1, SX, H - 1, FLEUR_CYAN)                  # the front door
    gy = at('hall_from_dining')[1]
    m.opening(0, gy, 0, gy + 1, STONE)                           # the doors to the Great Hall
    assert at('hall_from_academy') == (SX, H - 2) and at('hall_from_upper') == (SX, 7) and at('hall_from_dining')[0] == 1
    # the grand staircase up into the back wall, the court doors either side, the carpet down to the front door
    m.rect(SX - 1, 7, SX + 1, H - 2, FLEUR_CYAN); m.rect(1, gy - 1, SX - 2, gy + 2, FLEUR_CYAN)
    for r, row in enumerate(WC['staircase']):
        for c, n in enumerate(row): m.put(SX - 1 + c, 1 + r, n)
    for x in (SX - 1, SX, SX + 1): m.go('Grand Staircase', x, 1, *dest('upper_from_hall'))
    m.go('Court Door', at('hall_from_court_w')[0], 3, *dest('court_from_hall_w'), door=2)
    m.go('Court Door', at('hall_from_court_e')[0], 3, *dest('court_from_hall_e'), door=2)
    m.put(1, 19, STAIRS_DOWN[0]); m.go('Stairs Down', 1, 19, *dest('under_from_hall'))
    for y in (gy, gy + 1): m.go('Great Hall', 0, y, *dest('dining_from_hall'))
    m.go('Front Door', SX, H - 1, *dest('academy_from_hall'))
    m.obj('candelabra', SX - 2, 5); m.obj('candelabra', SX + 2, 5)
    m.obj('clock', 1, 4); m.obj('clock2', 18, 4); m.obj('sigil', 15, 1); m.obj('window2', 2, 2)
    for x, y in ((SX, 10), (SX, 16), (4, 15), (15, 9)): m.put(x, y, 21, 3)
    for x in (SX - 2, SX + 2):                                   # angel statues either side of the front door
        m.two(x, H - 3, ANGEL_STATUE)
    m.obj('armchair', 14, 11); m.obj('armchair', 16, 11); m.obj('armchair', 14, 17)
    m.put(17, 11, TABLE_ROUND); m.put(17, 11, BOOK_OPEN, 3)
    m.obj('chairs2', 3, 9); m.obj('chairs2', 12, 15)
    m.put(18, H - 2, PLANT_B)
    m.look('Great Hall Doors', 1, gy - 1, ['The great oak doors of the Great Hall stand open.', 'Voices, cutlery and laughter spill out.'])
    # the Registry: the registrar's desk, the dormitories' merit orbs, notices and portraits
    m.obj('counter_wide', 22, 5)
    m.put(21, 2, NOTICE); m.put(24, 2, PORTRAIT_A); m.put(25, 2, PORTRAIT_B)
    m.obj('seal_blue', 26, 2); m.obj('seal_violet', 28, 2)
    m.obj('orb_pedestal', 26, 9); m.obj('orb_pedestal', 28, 9)
    m.obj('glass_cabinet', 21, 9); m.obj('chairs2', 22, 15); m.obj('chairs2', 26, 15)
    m.obj('plant', 28, H - 2); m.obj('plant', 20, H - 2); m.put(25, 12, 22, 3)
    # people
    m.npc('Prefect', SX + 2, 7, 'People2', 4, ('Prefect:', 'Great Hall to the west, lessons through the court,',
          'the laboratory below, and the upper floor up the stairs.', 'No running on the staircase. It moves when it\'s cross.'), direction=2)
    m.npc('Registrar Fenwick', 23, 5, 'People1', 6, ('Registrar Fenwick:', 'The Registry. Admissions, exams, merit counts.',
          'Licenses and missions are the Guild\'s business in the capital -', 'exams are ours.'), direction=2)
    m.look('Dawnward Orb', 26, 10, ['\\C[6]Dawnward\\C[0]: the orb glows a steady blue.', '"412 merits"'])
    m.look('Duskward Orb', 28, 10, ['\\C[6]Duskward\\C[0]: the orb glows a restless violet.', '"409 merits"'])
    m.look('Notice', 21, 3, ['\\C[6]NOTICE\\C[0]', '"Third-year Wards exam: Thursday, Lecture Wing."',
                             '"The Undercroft\'s black door is NOT a dare."'])
    crowd(m, [(4, 12, 6), (12, 8, 2, 1), (6, 17, 8), (16, 14, 4), (12, 19, 8, 1), (24, 12, 8), (27, 17, 4), (3, 6, 2)], seed=1)
    return m


# =========================================================================== MAP041 Great Hall
@reg(K.ACADEMY_DINING, K.ACADEMY_HALL)
def great_hall():
    W, H = 34, 29
    m = AcademyMap(W, H, *K.NAMES[K.ACADEMY_DINING])
    m.bgm = {'name': 'Castle2', 'pan': 0, 'pitch': 105, 'volume': 70}
    # the hall is laid but empty most days: it fills for feasts, ceremonies and story events, which add their
    # own people; the faculty are in their classrooms and offices
    m.room(1, 1, W - 2, H - 2, FLEUR_GREY, 'stone')
    ey = at('dining_from_hall')[1]
    assert at('dining_from_hall')[0] == W - 2
    m.opening(W - 1, ey, W - 1, ey + 1, FLEUR_GREY)
    for y in (ey, ey + 1): m.go('To the Entrance Hall', W - 1, y, *dest('hall_from_dining'))
    # the dais: a red carpet, the high table, the Archmage's chair under the Academy's crest
    m.rect(5, 4, W - 6, 7, FLEUR_RED)
    m.obj('sigil', 15, 1); m.wide(15, 3, THRONE)
    for x in (2, 6, 25, 29): m.obj('window2', x, 2)
    m.obj('seal_blue', 11, 2); m.obj('seal_violet', 21, 2)
    for x in range(6, W - 6):
        m.put(x, 6, TABLE_MARBLE)
        if not 15 <= x <= 17: m.put(x, 5, CHAIR)
    for x in range(6, W - 6):
        if not 15 <= x <= 17: m.put(x, 6, PLATE if x % 2 else CUP_TEA, 3)
    m.obj('candelabra', 4, 5); m.obj('candelabra', W - 5, 5)
    # four long tables, two for each dormitory, with an aisle down the middle
    for x in (5, 11, 21, 27): long_table(m, x, 10, H - 4)
    m.rect(15, 8, 17, H - 2, FLEUR_CYAN)
    for x in (5, 11, 21, 27):
        for y in (12, 18, 23): m.put(x, y, 20, 3)
    m.obj('seal_blue2', 8, 8); m.obj('seal_violet2', 24, 8)
    for x in (1, W - 2): m.put(x, H - 2, PLANT_A)
    # a steward laying the tables, and a few students passing through
    m.npc('Hall Steward', 13, 9, 'People3', 2, ('Hall Steward:', 'Plates, cups, plates, cups. Two hundred and forty of each.',
          'The hall fills at feast days and ceremonies.', 'The rest of the time, it\'s just me and the echo.'), direction=2)
    seats = [(16, 14, 2, 1), (8, 20, 6), (24, 25, 8, 1)]
    crowd(m, seats, seed=4)
    return m


# =========================================================================== MAP033 Cloister Court (outdoors)
@reg(K.ACADEMY_COURT, K.ACADEMY)
def cloister_court():
    W, H = 36, 28
    m = T.Town(W, H, *K.NAMES[K.ACADEMY_COURT], ground=T.COBBLE)
    m.bgm = {'name': 'Castle2', 'pan': 0, 'pitch': 100, 'volume': 65}
    PASS_W, PASS_E, PASS_S = 16, 16, (13, 23)
    assert at('court_from_classes') == (1, PASS_W) and at('court_from_library') == (W - 2, PASS_E)
    assert at('court_from_hall_w') == (PASS_S[0], H - 2) and at('court_from_hall_e') == (PASS_S[1], H - 2)
    TX = 18                                                      # the Star Tower's door
    assert at('court_from_tower') == (TX, 8)
    # the north range with the Star Tower in the middle, the other three ranges seen from above
    m.rect(0, 0, W - 1, 2, T.CASTLE_TOP)
    m.rect(0, 3, W - 1, 7, T.CASTLE_WALL)
    m.rect(0, 8, 2, H - 1, T.CASTLE_TOP); m.rect(W - 3, 8, W - 1, H - 1, T.CASTLE_TOP)
    m.rect(0, H - 3, W - 1, H - 1, T.CASTLE_TOP)
    for i, (a, b) in enumerate([(194, 195), (202, 203), (176, 177), (184, 185), (192, 193), (200, 201), (192, 193), (208, 209)]):
        m.put(TX - 1, i, T.C_ + a, 3 if i < 7 else 2); m.put(TX, i, T.C_ + b, 3 if i < 7 else 2)
    for x in (5, 11, 25, 31): m.tall(x, 4, T.BANNER_BLUE)
    for x in (8, 14, 22, 28): m.put(x, 5, T.STAINED)
    m.put(TX, 3, T.SIGN['magic'])
    for y in (PASS_W,): m.rect(0, y, 2, y, T.COBBLE_B)
    m.rect(W - 3, PASS_E, W - 1, PASS_E, T.COBBLE_B)
    for x in PASS_S: m.rect(x, H - 3, x, H - 1, T.COBBLE_B)
    # the cloister walk round the lawn, its columns along the lawn's edge
    LX0, LY0, LX1, LY1 = 6, 11, 29, 22
    m.rect(LX0, LY0, LX1, LY1, T.GRASS)
    m.rect(17, LY0, 18, LY1, T.COBBLE_B); m.rect(LX0, 16, LX1, 17, T.COBBLE_B)
    m.rect(15, 14, 20, 19, T.COBBLE_B)
    for x in range(LX0, LX1 + 1, 3):
        for y0 in (LY0 - 3, LY1 + 1):
            if x in (17, 18): continue
            m.put(x, y0, L.ext('Inside_C', 188), 3); m.put(x, y0 + 1, L.ext('Inside_C', 196), 3); m.put(x, y0 + 2, L.ext('Inside_C', 204))
    # the fountain in the middle, with the Founder's statue
    m.rect(16, 15, 19, 18, T.WATER)
    m.put(17, 15, L.ext('Inside_C', 171), 3); m.put(17, 16, L.ext('Inside_C', 179))
    m.put(18, 15, L.ext('Inside_C', 171), 3); m.put(18, 16, L.ext('Inside_C', 179))
    # the lawn: blossom trees in the corners, flower beds, benches, a sundial
    for x, y in ((LX0, LY0), (LX1 - 1, LY0), (LX0, LY1 - 1), (LX1 - 1, LY1 - 1)):
        m.put(x, y, L.ext('PM_Nature1', 118), 3); m.put(x + 1, y, L.ext('PM_Nature1', 119), 3)
        m.put(x, y + 1, L.ext('PM_Nature1', 126)); m.put(x + 1, y + 1, L.ext('PM_Nature1', 127))
    for x in range(LX0 + 3, LX1 - 2):
        if x in (15, 16, 17, 18, 19, 20): continue
        m.put(x, LY0, T.FLOWERS[x % 4]); m.put(x, LY1, T.FLOWERS[(x + 1) % 4])
    for x, y in ((9, 14), (24, 14), (9, 19), (24, 19)):
        m.put(x, y, L.ext('Avy_Town_B', 102), 3); m.put(x + 1, y, L.ext('Avy_Town_B', 103), 3)
        m.put(x, y + 1, L.ext('Avy_Town_B', 110)); m.put(x + 1, y + 1, L.ext('Avy_Town_B', 111))
    m.put(13, 20, L.ext('Avy_Town_B', 68), 3); m.put(13, 21, L.ext('Avy_Town_B', 76))
    for x, y in ((4, 9), (W - 5, 9), (4, H - 5), (W - 5, H - 5)): m.lamp(x, y)
    for x, y in ((3, 12), (W - 4, 21), (8, 23), (27, 9)): m.put(x, y, L.ext('Avy_Town_B', 59))
    # events
    m.add_event('Star Tower', TX, 7, [L.door_page(*dest('tower_from_court')[:3], 8, '!Door1', 2)])
    m.exit('To the Lecture Wing', [(0, PASS_W)], *dest('classes_from_court'))
    m.exit('To the Library', [(W - 1, PASS_E)], *dest('library_from_court'))
    m.exit('To the Great Hall', [(PASS_S[0], H - 1)], *dest('hall_from_court_w'))
    m.exit('To the Great Hall ', [(PASS_S[1], H - 1)], *dest('hall_from_court_e'))
    m.sign('Founder\'s Statue', 17, 19, ['\\C[6]Aldric Vane, First Archmage\\C[0]', '"Every spell begins as a question."'])
    m.sign('Sundial', 13, 21, ['The sundial\'s shadow points at a rune', 'that means "lunch".'])
    m.npc('Professor of Herbs', 26, 12, 'People1', 7, ('Professor Moss:', 'These blossom trees were grafted by the founders.',
          'They flower all year. Nobody remembers the spell.'), direction=2)
    m.npc('Student', 10, 16, 'Actor2', 7, ('Student:', 'I study out here. The library ghost', 'keeps correcting my handwriting.'), direction=2)
    m.npc('Student', 25, 21, 'People2', 3, ('Student:', 'The Star Tower is open after dark.', 'Professor Lyra says the stars are "restless" this year.'), direction=8)
    m.npc('Student', 20, 23, 'Actor3', 7, ('Student:', 'Duskward dares say if you circle the fountain', 'thirteen times, the statue winks.', 'I\'m on lap nine.'),
          route=T.wander_route('RRRWLLLW'), speed=3)
    m.critter('Owl', 30, 14, 'Owls', 1, None, 'The owl regards you with the patience of a professor.', move=0)
    crowd(m, [(8, 13, 2), (12, 19, 8), (22, 12, 6), (27, 18, 4), (5, 10, 2, 1), (30, 23, 8, 1), (14, 9, 6, 1), (21, 22, 2)], seed=9)
    m.critter('Cat', 7, 20, 'Nature', 1, 'Cat', 'The Academy cat. It has a scarf in Duskward colours.', move=1)
    return m


# =========================================================================== MAP034 Lecture Wing
@reg(K.ACADEMY_CLASSES, K.ACADEMY_COURT)
def lecture_wing():
    W, H = 40, 25
    m = AcademyMap(W, H, *K.NAMES[K.ACADEMY_CLASSES])
    m.bgm = {'name': 'Castle2', 'pan': 0, 'pitch': 95, 'volume': 60}
    rooms = [((1, 8), FLEUR_VIOLET, 'stone', 'Elemental Theory'), ((10, 17), CHECK_CYAN, 'rune', 'Wards & Runes'),
             ((19, 28), FLEUR_GREY, 'stone2', 'Practice Hall'), ((30, 37), PLUM_WOOD, 'wood', 'Arcane History')]
    for (x0, x1), floor, wall, _ in rooms:
        m.room(x0, 1, x1, 16, floor, wall)
    m.room(1, 18, W - 2, H - 2, WOOD, 'oak', face=2)               # the corridor
    for (x0, x1), floor, _, _ in rooms:
        dx = (x0 + x1) // 2
        m.opening(dx, 17, dx + 1, 19, floor)                       # each classroom opens on the corridor
    ey = at('classes_from_court')[1]
    assert at('classes_from_court')[0] == W - 2
    m.opening(W - 1, ey, W - 1, ey, WOOD)
    m.go('To the Cloister Court', W - 1, ey, *dest('court_from_classes'))
    # Elemental Theory: desks facing the lectern, the four elements' seals on the wall
    m.put(4, 2, WORLD_MAP[0]); m.put(5, 2, WORLD_MAP[1])
    m.obj('seal_blue', 2, 2); m.obj('seal_violet', 7, 2); m.obj('lectern', 4, 5); m.obj('crystal_ball', 5, 5)
    for y in (8, 11, 14): m.obj('class_desks', 1, y - 1); m.obj('class_desks', 5, y - 1)
    # Wards & Runes: rune circles, an arcane device, a glowing orb
    m.obj('sigil', 12, 1); m.obj('arcane_device', 11, 5); m.obj('orb_pedestal', 16, 4); m.obj('lectern', 13, 5)
    for y in (8, 12): m.obj('class_desks', 10, y); m.obj('class_desks', 14, y)
    m.obj('cobweb3', 16, 14)
    # Practice Hall: open floor for duelling, targets (shields) on the wall, mats at both ends
    m.rect(20, 7, 27, 13, CHECK_CYAN)
    for x in (20, 23, 26): m.put(x, 2, WALL_SHIELD)
    m.put(21, 2, WALL_SWORDS_X); m.put(25, 2, WALL_SWORDS_X)
    for x in range(21, 27): m.obj('mat_red', x, 6); m.obj('mat_grey', x, 14)
    m.obj('orb_pedestal', 19, 4); m.obj('orb_pedestal', 28, 4)
    # Arcane History: bookshelves, globes, a tapestry
    m.two(30, 3, BOOKSHELF_A); m.two(31, 3, BOOKSHELF_B); m.two(36, 3, BOOKSHELF_A); m.two(37, 3, BOOKSHELF_B)
    m.wide(33, 2, [(TAPESTRY[0],), (TAPESTRY[1],)])
    m.obj('globe_desk', 34, 5); m.obj('lectern', 33, 5)
    for y in (8, 12): m.obj('study_desk', 31, y - 1); m.obj('study_desk', 35, y - 1)
    # the corridor: windows and candelabra between the doors, benches
    for x in (3, 7, 12, 16, 22, 26, 32, 36): m.obj('window', x, 18)
    for x in (9, 18, 29): m.obj('candelabra', x, 19)
    m.obj('chairs2', 6, 22); m.obj('chairs2', 33, 22); m.obj('plant', 1, 23); m.obj('plant', 38, 21)
    m.put(24, 22, NOTICE)
    # people
    m.npc('Professor Elspeth Rook', 4, 4, 'Actor2', 4, ('Professor Rook:', 'Fire wants to spread, water to settle,',
          'earth to hold and wind to leave. Your job is to argue with them.'), direction=2)
    m.npc('Professor Halden', 14, 4, 'People4', 3, ('Professor Halden:', 'A ward is a promise you make to a place.',
          'Break it, and the place remembers.'), direction=2)
    m.npc('Duelling Master Kestrel', 24, 6, 'People3', 6, ('Duelling Master Kestrel:', 'Bow. Draw. Cast. Bow again.',
          'If you skip the second bow, I fail you, even if you win.'), direction=2)
    m.npc('Professor Aubert', 33, 4, 'People2', 2, ('Professor Aubert:', 'History is the record of spells that went wrong.',
          'The ones that went right, we call "tradition".'), direction=2)
    m.npc('Student', 22, 10, 'Actor2', 7, ('Student:', 'Ready? On three. One... two...'), direction=6)
    m.npc('Student', 25, 10, 'People2', 1, ('Student:', '...I said on THREE!'), direction=4)
    for x, y, sheet, idx, line in ((2, 9, 'People1', 0, 'Fire, water, earth, wind... and what\'s the fifth? Lunch?'),
                                   (15, 9, 'Actor3', 7, 'My ward fizzled. Professor Halden says it "lacked conviction".'),
                                   (31, 9, 'People2', 3, 'Did you know the Academy is older than the capital\'s walls?'),
                                   (20, 21, 'Actor2', 5, 'Late! Late! Wards started five minutes ago!')):
        m.npc('Student', x, y, sheet, idx, ('Student:', line), direction=8 if y < 18 else 4,
              move=0 if y < 18 else 1, freq=4)
    crowd(m, [(5, 21, 2, 1), (11, 22, 8), (14, 21, 2), (27, 22, 8, 1), (35, 21, 2), (3, 12, 8), (12, 15, 8), (36, 10, 8)], seed=2)
    for (x0, x1), _, _, title in rooms:
        m.look(title, (x0 + x1) // 2 + 2, 17, ['\\C[6]%s\\C[0]' % title])
    return m


# =========================================================================== MAP035 Library & Infirmary
@reg(K.ACADEMY_LIBRARY, K.ACADEMY_COURT)
def library():
    W, H = 36, 25
    m = AcademyMap(W, H, *K.NAMES[K.ACADEMY_LIBRARY])
    m.bgm = {'name': 'Castle2', 'pan': 0, 'pitch': 90, 'volume': 55}
    m.room(1, 1, 24, H - 2, PLUM_WOOD, 'wood')
    m.room(26, 1, 34, H - 2, WOOD, 'stone2')
    m.opening(25, 12, 25, 13, PLUM_WOOD)
    ey = at('library_from_court')[1]
    m.opening(0, ey, 0, ey, PLUM_WOOD)
    m.go('To the Cloister Court', 0, ey, *dest('court_from_library'))
    # the Library: shelves along the back wall and in rows, reading tables down the middle, the librarian's desk
    for x in (1, 7, 14, 20): m.obj('shelf_tall', x, 1, ground=2)
    for x, y in ((2, 6), (2, 15), (18, 6), (18, 15)): m.obj('shelf_tall', x, y, ground=2)
    m.rect(9, 6, 15, 18, FLEUR_VIOLET)
    for y in (7, 11, 15): m.obj('study_desk', 10, y); m.obj('study_desk2', 13, y)
    m.obj('long_desk', 9, 20)
    for x, y in ((12, 9), (12, 16), (4, 12), (20, 12)): m.put(x, y, 21, 3)
    m.obj('globe_desk', 7, 12); m.obj('desk_lamp', 16, 12); m.put(1, 22, PLANT_B)
    # the Restricted Stacks: behind a rope of cobwebs in the south-east corner
    for x, y in ((20, 19), (22, 19)): m.obj('shelf3', x, y, ground=2)
    m.obj('cobweb', 23, 19); m.obj('skull_shelf', 19, 21); m.obj('chest', 21, 22)
    # the Infirmary: beds along the back wall and in a row, the healer's cabinet
    for x in (27, 29, 31, 33): m.two(x, 3, BED)
    for x in (27, 29, 31): m.two(x, 15, BED)
    m.two(33, 15, MEDICINE_SHELF); m.put(34, 20, BASIN); m.put(26, H - 2, PLANT_A); m.obj('apothecary', 30, 19, ground=1)
    m.put(28, 10, MEDICINES); m.put(32, 10, POTION_RED)
    # people
    m.npc('Librarian Ottoline', 11, 20, 'People4', 6, ('Librarian Ottoline:', 'Speak softly. The Founding Grimoires are in the',
          'Restricted Stacks.', 'No, you may not. Nobody may. That is rather the point.'), direction=2)
    m.npc('Library Ghost', 6, 18, 'Monster', 6, ('Library Ghost:', 'Shhh!', 'I have been shushing in this library for two hundred years.',
          'It is the only spell I ever mastered.'), move=1, freq=2)
    for x, y, sheet, idx, line in ((10, 8, 'Actor2', 7, 'Page four hundred. Four hundred! And it\'s still the introduction.'),
                                   (14, 12, 'People2', 3, 'Mira Moonvale used to sit right here. She read the whole east wall.'),
                                   (4, 10, 'Actor3', 7, 'I\'m looking for "Wards for the Desperate". Someone checked it out. Everyone did.')):
        m.npc('Student', x, y, sheet, idx, ('Student:', line), direction=8 if y > 9 else 2)
    m.npc('Professor Wren-Hollis', 7, 15, 'People2', 2, ('Professor Wren-Hollis:', 'Enchantment Theory, third floor of the stacks.',
          'I come down here for the quiet. And the tea I\'m not supposed to drink here.'), direction=2)
    crowd(m, [(13, 9, 8), (10, 13, 8), (14, 16, 8), (7, 9, 4, 1), (17, 13, 6, 1), (21, 5, 2), (5, 20, 6)], seed=5)
    m.look('Restricted Stacks', 22, 18, ['\\C[6]RESTRICTED\\C[0]', 'The cobwebs here are thick, and very carefully', 'not disturbed.'])
    heal = [cmd(250, [{'name': 'Recovery', 'volume': 80, 'pitch': 100, 'pan': 0}]), cmd(224, [[200, 255, 220, 120], 30, True]),
            cmd(314, [0, 0])] + text('\\C[6]HP and MP fully restored.\\C[0]')
    m.npc('Healer Agnes', 30, 9, 'People1', 7, ('Healer Agnes:', 'Singed? Frozen? Turned briefly into a newt?',
          'Sit. Drink this. Don\'t ask what\'s in it.'), direction=2, extra=heal)
    m.npc('Patient', 29, 6, 'People2', 0, ('Patient:', 'I tried to cast Fire with a cold.', 'I sneezed. The curtains are gone.'), direction=2)
    return m


# =========================================================================== MAP036 Undercroft
@reg(K.ACADEMY_UNDERCROFT, K.ACADEMY_HALL)
def undercroft():
    W, H = 34, 24
    m = AcademyMap(W, H, *K.NAMES[K.ACADEMY_UNDERCROFT], ambient='#b8b4c8')
    m.bgm = {'name': 'Dungeon1', 'pan': 0, 'pitch': 90, 'volume': 50}
    m.room(1, 1, 6, H - 2, STONE, 'stone')                      # the stair passage
    m.room(8, 1, 20, H - 2, CHECK_CYAN, 'rune')                 # the Alchemy Laboratory
    m.room(22, 1, 32, 11, OAK, 'oak')                           # the kitchens
    m.room(22, 13, 32, H - 2, STONE, 'stone3')                  # the stores
    m.opening(7, 11, 7, 12, STONE); m.opening(21, 6, 21, 7, CHECK_CYAN); m.opening(21, 18, 21, 19, CHECK_CYAN)
    assert at('under_from_hall') == (3, 5)
    m.put(3, 4, STAIRS_UP[0]); m.go('Stairs Up', 3, 4, *dest('hall_from_under'))
    m.obj('lantern2', 2, 8); m.obj('cobweb2', 5, 4); m.put(1, H - 2, BARREL); m.put(6, H - 2, CRATES[1]); m.put(6, H - 3, CRATES[0], 3)
    # the laboratory: rows of cauldrons, shelves of ingredients
    m.obj('apothecary', 9, 1); m.obj('apothecary', 17, 1); m.obj('glass_cabinet', 13, 2); m.obj('sign_cauldrons', 13, 1)
    for x, y, kind in ((10, 7, 'cauldron_green'), (14, 7, 'cauldron_blue'), (18, 7, 'cauldron_green'),
                       (10, 12, 'cauldron_blue'), (14, 12, 'cauldron_green'), (18, 12, 'cauldron_blue')):
        m.obj(kind, x, y)
    m.obj('long_desk', 10, 17); m.obj('skull_shelf', 20, 16); m.obj('crate', 8, 20); m.put(20, 20, SACKS)
    for x, y in ((10, 6), (14, 6), (18, 6)): m.put(x, y - 1, 22, 3)
    # the kitchens
    for x in (23, 24): m.put(x, 3, OVEN)
    m.put(25, 3, SINK); m.put(26, 3, SHELF_JARS); m.put(27, 3, SHELF_BOTTLES)
    for x in range(24, 31): m.put(x, 7, TABLE_CLOTH)
    for x, t in zip(range(24, 31), (BREAD, ROAST, PIE, BOWL, CAKE, FRUIT_BOWL, PLATE)): m.put(x, 7, t, 3)
    m.put(32, 4, BARREL); m.put(32, 5, BARREL); m.put(22, 10, SACKS); m.put(32, 10, CRATES[1]); m.put(32, 9, CRATES[0], 3)
    # the stores, and the black door nobody opens
    for x, y in ((23, 16), (25, 16), (23, 19)): m.obj('chest_stack', x, y)
    for x in (29, 30, 31, 32): m.put(x, 21, BARREL)
    m.obj('cobweb3', 31, 16); m.obj('cobweb', 22, 20)
    # people
    m.npc('Professor Brisk', 14, 16, 'People4', 7, ('Professor Brisk:', 'Green cauldrons: healing draughts, second-years.',
          'Blue cauldrons: do not touch the blue cauldrons.', 'Last term a student did. He is upstairs. In a jar. He\'s fine.'), direction=2)
    for x, y, d, line in ((11, 9, 8, 'Stir clockwise... or was it widdershins? Professor? PROFESSOR?'),
                          (19, 14, 8, 'If I mix this right, it turns gold. If I mix it wrong, I turn gold.')):
        m.npc('Student', x, y, 'Actor2' if x < 15 else 'People2', 5 if x < 15 else 1, ('Student:', line), direction=d)
    m.npc('Cook', 27, 5, 'People1', 3, ('Cook:', 'Eight hundred eggs a week. Nine a day for Professor Halden alone.',
          'I don\'t ask. I just crack.'), direction=2)
    m.add_event('Black Door', 28, 15, [page(char('!Door1', 6), walk_anim=False, commands=text(
        'A door of black iron with no handle and no keyhole.', 'It is cold to the touch, and very faintly, it hums.'))])
    m.look('Blue Cauldron', 14, 8, ['The blue brew hums quietly.', 'You decide not to touch it.'])
    return m


# =========================================================================== MAP037 Upper Floor
@reg(K.ACADEMY_UPPER, K.ACADEMY_HALL)
def upper_floor():
    W, H = 48, 28
    m = AcademyMap(W, H, *K.NAMES[K.ACADEMY_UPPER])
    m.bgm = {'name': '03_The_Calm', 'pan': 0, 'pitch': 100, 'volume': 55}
    m.room(1, 1, 13, 12, OAK, 'oak')                            # the Enchanting Workshop
    m.room(15, 1, 32, 12, FLEUR_GREY, 'stone')                  # the students' common room, the dormitory doors
    m.room(34, 1, 46, 12, CHECK_CYAN, 'rune')                   # the Hall of Familiars
    m.room(1, 23, 25, H - 2, WOOD, 'wood', face=2)              # the faculty corridor ...
    OFFICES = [(1, 3), (5, 7), (9, 11), (13, 15), (17, 19), (21, 23)]
    for x0, x1 in OFFICES: m.room(x0, 14, x1, 21, PLUM_WOOD, 'wood')   # ... and its six offices
    m.room(27, 14, 33, H - 2, STONE, 'rune')                    # the landing
    m.room(35, 14, 46, H - 2, FLEUR_RED, 'rune')                # the Archmage's study
    for x0, y0, x1, y1, f in ((14, 8, 14, 9, OAK), (33, 8, 33, 9, CHECK_CYAN), (29, 13, 31, 16, STONE),
                              (26, 25, 26, 26, WOOD), (34, 20, 34, 21, FLEUR_RED)):
        m.opening(x0, y0, x1, y1, f)
    for x0, x1 in OFFICES: m.opening(x0 + 1, 22, x0 + 1, 24, PLUM_WOOD)
    assert at('upper_from_hall') == (30, H - 3)
    for x in (29, 30, 31): m.put(x, H - 2, STAIRS_DOWN[0]); m.go('Stairs Down', x, H - 2, *dest('hall_from_upper'))
    m.rect(29, 17, 31, H - 3, FLEUR_CYAN)
    # the common room: a great fireplace, armchairs round it, a piano, and the two dormitory gates in the back wall
    m.wide(22, 2, ib(I.FIREPLACE_L))
    m.obj('armchair', 21, 6); m.obj('armchair', 25, 6)
    m.put(23, 8, TABLE_ROUND); m.put(23, 8, BOOK_OPEN, 3); m.put(24, 8, TABLE_ROUND); m.put(24, 8, TEAPOT, 3)
    m.wide(19, 3, PIANO); m.two(27, 3, BOOKSHELF_A); m.two(28, 3, BOOKSHELF_B)
    m.put(15, 12, PLANT_A); m.put(32, 12, PLANT_B); m.put(22, 10, 21, 3)
    # each gate: double doors under the house seal and crest, the house banners either side, a carpet in its
    # colours running out into the room, and the prefect on guard. Duskward (west) violet and red, as its tower's
    # banners; Dawnward (east) blue and gold.
    for x, name, seals, banner, carpet, prefect in (
            (16, 'Duskward Tower', ('seal_violet', 'seal_violet2'), (32, 40), FLEUR_RED,
             (18, 'Actor2', 5, ('Duskward Prefect:', 'Duskward Tower. Students only.',
                                'We\'d let you in, but then we\'d have to let Dawnward in.'))),
            (30, 'Dawnward Tower', ('seal_blue', 'seal_blue2'), (38, 46), FLEUR_CYAN,
             (29, 'People2', 4, ('Dawnward Prefect:', 'Dawnward Tower. Students only, I\'m afraid -',
                                 'graduates included. Seven floors of beds and bad singing up there.')))):
        m.obj(seals[0], x, 1); m.obj(seals[1], x + 1, 1)
        for dx in (0, 1): m.put(x + dx, 2, L.ext('Outside_B', 14))           # the crest over the gate
        for bx in (x - 1, x + 2):
            m.put(bx, 2, L.ext('Outside_C', banner[0])); m.put(bx, 3, L.ext('Outside_C', banner[1]))
        m.rect(x, 4, x + 1, 8, carpet)
        for dx in (0, 1):
            m.add_event(name, x + dx, 3, [page(char('!Door1', 2), walk_anim=False, commands=text(
                '\\C[6]%s\\C[0]' % name, 'The great doors are locked. A brass plate reads:', '"Students of %s only."' % name.split()[0]))])
        px_, sheet, idx, lines = prefect
        m.npc(lines[0][:-1], px_, 5, sheet, idx, lines, direction=2)
    # the Enchanting Workshop: workbenches, glowing devices, staves waiting for their runes
    m.obj('sign_wands', 2, 2); m.obj('sign_brooms', 4, 2); m.obj('glass_cabinet', 9, 2)
    for x, y in ((2, 6), (2, 9)): m.obj('study_desk2', x, y - 1)
    m.obj('arcane_device', 6, 6); m.obj('orb_pedestal', 8, 6); m.obj('crystal_ball', 10, 8); m.obj('desk_potions', 11, 8)
    m.obj('broom', 6, 10); m.obj('crate', 11, 11); m.obj('chest', 1, 11)
    m.npc('Master Enchanter Thibault', 7, 9, 'People3', 1, ('Master Enchanter Thibault:', 'Enchanting is patience, not power.',
          'A staff takes a year to wake. A sword, three. A student, five.'), direction=2)
    # the Hall of Familiars: owls, cats and stranger things, and the keeper who feeds them
    m.obj('orb_window', 36, 2); m.obj('orb_window', 44, 2); m.obj('seal_violet2', 40, 2)
    m.obj('orb_pedestal', 37, 8); m.obj('orb_pedestal', 43, 8); m.put(40, 11, BASIN)
    for x, y, sheet, idx, line in ((36, 6, 'Owls', 1, 'An owl with a Dawnward ribbon. It hoots twice, smugly.'),
                                   (41, 5, 'Owls', 1, 'This owl is asleep. It is always asleep.'),
                                   (39, 9, 'Nature', 1, 'A black cat with violet eyes. It is definitely judging you.'),
                                   (44, 10, 'Pet_Animals', 0, 'A small red fox curls round a student\'s scarf.'),
                                   (35, 11, 'Pet_Animals', 6, 'A tortoise. Its shell is carved with tiny runes.')):
        m.critter('Familiar', x, y, sheet, idx, None, line, move=1 if sheet != 'Owls' else 0, area=(35, 4, 45, 11))
    m.npc('Familiar Keeper Pim', 42, 7, 'People1', 5, ('Familiar Keeper Pim:', 'Every student gets a familiar in second year.',
          'Most pick owls. One boy picked a toad. We are all still looking for it.'), direction=2)
    # the faculty offices: each one dressed for its professor
    for (x0, x1), (who, things) in zip(OFFICES, (
            ('Professor Rook - Elemental Theory', ('candelabra', 'desk_lamp')),
            ('Professor Halden - Wards & Runes', ('orb_pedestal', 'arcane_device')),
            ('Duelling Master Kestrel', ('chest', 'broom_stand')),
            ('Professor Aubert - Arcane History', ('globe_desk', 'books')),
            ('Professor Lyra Venn - Astronomy', ('crystal_ball', 'desk_globe')),
            ('Professor Moss - Herbalism', ('plant', 'vase_flowers')))):
        m.two(x0, 17, BOOKSHELF_A if x0 % 2 else BOOKSHELF_B)
        m.obj(things[0], x1, 17 if things[0] in ('candelabra', 'orb_pedestal') else 18)
        m.obj(things[1], x0 + 1, 18)
        m.put(x0, 20, CHAIR)
        m.look('Office', x0 + 1, 22, ['\\C[6]%s\\C[0]' % who])
    m.put(4, 23, WIN_LARGE[1]); m.put(12, 23, WIN_LARGE[1]); m.put(20, 23, WIN_LARGE[1])
    # the landing, and the Archmage's study
    m.obj('clock', 27, 17); m.obj('candelabra', 33, 17); m.put(28, 22, VASE)
    m.obj('sigil', 39, 14); m.obj('long_desk', 38, 18); m.obj('orb_pedestal', 45, 17); m.obj('globe_desk', 36, 18)
    m.two(45, 20, BOOKSHELF_A); m.two(46, 20, BOOKSHELF_B); m.obj('glass_cabinet', 35, 23); m.obj('chandelier_black', 40, 22, ground=0)
    m.obj('crystal_ball', 42, 18); m.put(46, H - 2, PLANT_B)
    m.npc('Archmage Corvin Vale', 40, 17, 'People4', 6, ('Archmage Corvin Vale:', 'Ah. Few visitors find their way up here.',
          'The orb on that pedestal has dimmed twice this month.', 'When it dims a third time, I will need to ask for help.'), direction=2)
    crowd(m, [(20, 9, 8), (26, 10, 8), (17, 7, 2, 1), (29, 9, 4), (9, 26, 4, 1), (22, 25, 6, 1), (30, 20, 2, 1), (5, 8, 6)], seed=7)
    return m


# =========================================================================== MAP038 Star Tower
@reg(K.ACADEMY_TOWER, K.ACADEMY_COURT)
def star_tower():
    W, H = 17, 17
    m = AcademyMap(W, H, *K.NAMES[K.ACADEMY_TOWER], ambient='#a8a8d8')
    m.bgm = {'name': '03_The_Calm', 'pan': 0, 'pitch': 85, 'volume': 55}
    m.room(1, 1, W - 2, H - 2, FLEUR_VIOLET, 'rune')
    m.opening(8, H - 1, 8, H - 1, FLEUR_VIOLET)
    assert at('tower_from_court') == (8, H - 2)
    m.go('To the Cloister Court', 8, H - 1, *dest('court_from_tower'))
    m.rect(5, 6, 11, 11, CHECK_CYAN)
    for x in (2, 5, 11, 14): m.obj('orb_window', x, 2)
    m.obj('sigil', 7, 1)
    m.obj('arcane_device', 8, 8); m.obj('orb_pedestal', 3, 5); m.obj('orb_pedestal', 13, 5)
    m.put(12, 13, STAIRS_UP[2]); m.obj('globe_desk', 2, 11)
    m.put(4, 13, TABLE_ROUND); m.put(4, 13, MAP_C, 3); m.put(3, 13, CHAIR); m.put(5, 13, CHAIR)
    m.obj('chandelier_black', 7, 9, ground=0)
    m.npc('Professor Lyra Venn', 8, 5, 'Actor3', 7, ('Professor Lyra Venn:', 'The Star Tower. Astronomy, astromancy,',
          'and the occasional proposal of marriage.', 'The stars have been restless this year. I log everything.'), direction=2)
    m.look('Star Engine', 8, 8, ['A brass engine of rings and lenses, turning slowly', 'with the sky. One ring is turning the wrong way.'])
    m.look('Roof Hatch', 12, 13, ['The roof hatch is bolted.', '"Stargazing after dark only. - L.V."'])
    return m


def build_all():
    from academy_sprites import recast
    out = {}
    for mid, (fn, parent) in MAPS.items():
        m = fn()
        recast(m.events, seed=mid)                  # students in uniform, the staff in their robes and hats
        out[mid] = (m, parent)
    return out


if __name__ == '__main__':
    out = next((a for a in sys.argv[1:] if not a.startswith('--')), None)
    maps = build_all()
    if out:
        for mid, (m, _) in maps.items(): m.render(out.replace('.png', '_%d.png' % mid), scale=0.5, grid='--grid' in sys.argv)
    if '--save' in sys.argv:
        # the Cloister Court (a Town) widens its edge exits by reading the maps they lead to: save it last
        for mid, (m, parent) in sorted(maps.items(), key=lambda kv: isinstance(kv[1][0], T.Town)):
            m.save(mid, parent_id=parent, order=mid)
            print('saved Map%03d' % mid)
