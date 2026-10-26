# MAP021-022 - the Royal Prison beside the barracks: a guardroom on the ground floor (soldiers only) and the
# cells below (Dungeon tileset), where the prisoners talk to you through the bars.
import sys
sys.path.insert(0, 'D:/RPG Maker MV/Project Nova_tools')
from interior_kit import *
import nova_maplib as L
from nova_maplib import cmd, text, say, page, char
import kingdom as K

DUNGEON = 4
SOLDIER, SOLDIER2 = ('People3', 6), ('People3', 7)


def talk(r, name, x, y, sprite, direction, *messages, move=0, freq=3):
    """NPC with one or more message boxes: messages = (speaker, line, line...), ..."""
    cmds = sum((say(*msg) for msg in messages), [])
    return r.add_event(name, x, y, [page(char(sprite[0], sprite[1], direction), move_type=move, freq=freq, commands=cmds)])


# =========================================================================== guardroom (1F)
def ground_floor():
    r = Room(19, 14, *K.NAMES[K.PRISON_1F], floor=STONE, walls='stone', ambient='#d6d2dc')
    r.bgm = {'name': 'Castle2', 'pan': 0, 'pitch': 100, 'volume': 60}
    # warden's corner: desk, cabinet, notices and a city map
    r.counter(3, 5, 6, 5)
    r.put(4, 5, NOTES, 3); r.put(5, 5, C_ + 75, 3)
    r.two(2, 2, CABINET)
    r.put(4, 1, NOTICE); r.put(6, 1, 163)
    r.put(5, 2, WORLD_MAP[0]); r.put(6, 2, WORLD_MAP[1])
    # armoury wall
    r.put(9, 1, WALL_SHIELD); r.put(8, 1, WALL_SWORDS); r.put(10, 1, WALL_SWORDS_X)
    r.put(8, 3, SWORD_RACK_A); r.put(10, 3, SWORD_RACK_B); r.put(9, 3, REPO_SWORDS[1])
    r.put(12, 3, ARMOR_STANDS[0]); r.put(13, 3, ARMOR_STANDS[1])
    # the guards' card table
    r.counter(8, 7, 10, 8)
    r.put(8, 7, C_ + 80, 3); r.put(10, 8, C_ + 17, 3)
    for x, y in ((7, 7), (7, 8), (11, 7), (11, 8), (9, 9)): r.put(x, y, STOOL_A)
    # night-shift cots, stores
    for x in (2, 4): r.two(x, 9, CHEAP_BED)
    r.put(2, 12, BASIN); r.put(3, 12, BARREL)
    r.put(16, 11, CRATE_B); r.put(17, 11, CRATE_C); r.put(17, 12, SACK_A); r.put(16, 12, SACK_B)
    # stairs down to the cells, in the corner, in plain view
    r.put(16, 3, STAIRS_DOWN[0])

    r.exit_door(9, K.CASTLE_APPROACH, 7, 22, 2)
    r.add_event('Stairs Down', 16, 3, [L.exit_page(K.PRISON_CELLS, 2, 4, 2)])
    for x in (3, 15):
        r.obj('Sconce', x, 2, '!Flame', 0, None, step=True, priority=2)
    r.obj('Brazier', 14, 10, '!Other2', 7, None, step=True)
    talk(r, 'Warden Brask', 4, 4, SOLDIER2, 2,
         ('Warden Brask:', 'Twenty cells below, and every last one holds', 'a man who swears he is innocent.'),
         ('Warden Brask:', 'You may walk the lower hall. Hand them nothing', 'through the bars - not bread, not a word of hope.'))
    talk(r, 'Soldier', 7, 8, SOLDIER, 6,
         ('Soldier:', 'Three of a kind! ...Don\'t tell the Warden we', 'play cards on watch. He thinks we\'re polishing.'))
    talk(r, 'Soldier', 11, 7, SOLDIER2, 4,
         ('Soldier:', 'I\'ve lost two weeks\' pay at this table.', 'Worst posting in Nova.'))
    talk(r, 'Armourer', 12, 4, SOLDIER, 2,
         ('Soldier:', 'Halberds polished, manacles oiled.', 'The night shift always leaves the mess for us.'))
    talk(r, 'Stair Guard', 15, 3, SOLDIER2, 2,
         ('Stair Guard:', 'The cells are below. Watch your step - and', 'your purse. Fenn has quick fingers, bars or no bars.'))
    r.look('Cot', 2, 10, ['A rumpled cot, still warm.', 'Someone\'s night shift has only just ended.'])
    r.look('Duty Roster', 4, 2, ['\\C[6]Prison Duty Roster\\C[0]', 'Day watch: Squad 2   Night watch: Squad 6',
                                 'Lower hall: two guards at all times. NO EXCEPTIONS.'])
    return r


# =========================================================================== the cells (B1)
D_TOP, D_FACE, D_FLOOR, D_CELL = ('A4', 16), ('A4', 24), ('A5', 32), ('A2', 8)   # grey brick, stone slabs, rubble
D_STAIRS_UP, D_COBWEB, D_BUCKET, D_POT = 2, 144, 239, 230
D_COT = (406, 414)
D_BARS_TOP, D_BARS = (244, 245, 246, 247), (252, 253, 254, 255)   # the bars' lower row is a counter: talk across it
D_BONES = (248, 250, 249)
D_BARREL, D_BARREL_OPEN, D_CRATE_L, D_CRATE_R = 238, 239, 236, 237


def cells():
    W, H = 26, 18
    r = L.MapBuilder(W, H, DUNGEON, *K.NAMES[K.PRISON_CELLS])
    r.note = '<ambient: #5e5a6a>\n<glow: 0.45>'
    r.bgm = {'name': 'Dungeon1', 'pan': 0, 'pitch': 100, 'volume': 60}
    r.bgs = {'name': 'Drips', 'pan': 0, 'pitch': 100, 'volume': 55}
    r.rect(0, 0, W - 1, H - 1, D_TOP)
    upper = lower = [6, 11, 16, 21]            # left column of each 4-wide cell
    # upper block: the stair alcove and four cells, back wall rows 1-2
    for x0 in [1] + upper:
        r.rect(x0, 1, x0 + 3, 2, D_FACE)
        r.rect(x0, 3, x0 + 3, 7, D_FLOOR if x0 == 1 else D_CELL)
    r.rect(1, 8, W - 2, 11, D_FLOOR)           # the hall
    r.rect(1, 12, 4, 16, D_FLOOR)              # jailer's post
    for x0 in lower:
        r.rect(x0, 12, x0 + 3, 16, D_CELL)
    up_doors = [x0 + 1 for x0 in upper]
    lo_doors = [x0 + 2 for x0 in lower]
    for x0 in upper:                           # bars stand on row 7, their tops overhang row 6
        for i in range(4):
            r.put(x0 + i, 6, D_BARS_TOP[i])
            if x0 + i not in up_doors: r.put(x0 + i, 7, D_BARS[i])
    for x0 in lower:                           # bars on row 12, tops overhang the hall
        for i in range(4):
            r.put(x0 + i, 11, D_BARS_TOP[i])
            if x0 + i not in lo_doors: r.put(x0 + i, 12, D_BARS[i])
    r.put(2, 3, D_STAIRS_UP)
    for x0 in upper:                           # a cot, a bucket and cobwebs in every cell
        r.put(x0 + 3, 3, D_COT[0], 3); r.put(x0 + 3, 4, D_COT[1])
        r.put(x0, 5, D_BUCKET); r.put(x0, 1, D_COBWEB)
    for x0 in lower:
        r.put(x0 + 3, 15, D_COT[0], 3); r.put(x0 + 3, 16, D_COT[1])
        r.put(x0, 16, D_BUCKET)
    r.put(21, 14, D_BONES[0]); r.put(22, 15, D_BONES[1]); r.put(21, 16, D_BONES[2])   # the empty cell
    r.put(3, 1, D_COBWEB)
    r.put(1, 14, D_BARREL); r.put(1, 15, D_BARREL_OPEN); r.put(1, 16, D_CRATE_L); r.put(2, 16, D_CRATE_R)
    r.put(4, 16, D_POT)

    r.add_event('Stairs Up', 2, 3, [L.exit_page(K.PRISON_1F, 16, 4, 2)])
    for x in (3, 8, 13, 18, 23):
        r.add_event('Sconce', x, 2, [page(char('!Flame', 0), step_anim=True, priority=2)])
    for x, y in ((4, 13), (24, 8)):
        r.add_event('Brazier', x, y, [page(char('!Other2', 7), step_anim=True)])
    locked = text('The cell door is locked fast.', 'The Jailer keeps the only key.')
    for x, y in [(x, 7) for x in up_doors] + [(x, 12) for x in lo_doors]:
        r.add_event('Cell Door', x, y, [page(char('!Door1', 7), commands=locked, dir_fix=True)])
    talk(r, 'Jailer Gorm', 2, 13, SOLDIER2, 6,
         ('Jailer Gorm:', 'Walk the hall if you like. Keep your fingers', 'out of the bars - Big Dunn bites.'),
         ('Jailer Gorm:', 'And don\'t listen to the hooded one in cell six.', 'Gives the lads nightmares, that one.'))
    talk(r, 'Guard', 13, 9, SOLDIER, 2,
         ('Guard:', 'Hate the lower hall. Damp, dark, and they', 'never stop TALKING.'), move=1, freq=2)
    # prisoners stand right behind the bars so they can be spoken to across them
    talk(r, 'Fenn', 8, 6, ('Evil', 1), 2,
         ('"Fingers" Fenn:', 'Psst. You\'ve got an honest face. And a heavy', 'purse. ...Just an observation, friend.'),
         ('"Fingers" Fenn:', 'They say I picked the Lord Treasurer\'s pocket.', 'Lies! I picked his wife\'s.'))
    talk(r, 'Marrow', 13, 6, ('People2', 3), 2,
         ('Captain Marrow:', 'Twelve crates of Emberleaf past the harbor', 'watch, and they nab me for the thirteenth.'),
         ('Captain Marrow:', 'Should\'ve stopped at twelve. Always stop', 'at twelve, lad. Write that down.'))
    talk(r, 'Big Dunn', 18, 6, ('People4', 2), 2,
         ('Big Dunn:', 'Man said my mum\'s stew tasted of boots.', 'So I introduced his face to a chair.'),
         ('Big Dunn:', '...Two chairs. The Lion\'s Rest wants me to', 'pay for both.'))
    talk(r, 'Old Pell', 23, 6, ('People1', 6), 2,
         ('Old Pell:', 'These coins? Real as the King\'s own crown.', 'Bite one if you don\'t believe me.'),
         ('Old Pell:', '...Actually, don\'t. They\'re mostly lead.'))
    talk(r, 'Masked Bandit', 7, 13, ('Evil', 4), 2,
         ('Masked Bandit:', 'The north road was mine. Every wagon, every', 'coin. Ask anyone between here and the pass.'),
         ('Masked Bandit:', 'Only reason they caught me? Something up there', 'scared off my whole crew. Something cold.'))
    talk(r, 'Hooded Prisoner', 12, 13, ('Evil', 3), 2,
         ('Hooded Prisoner:', '...the frost wakes... the frost wakes...'),
         ('Hooded Prisoner:', 'You feel it too, don\'t you? Summer in the north,', 'and the rivers freezing. It has already begun.'))
    talk(r, 'Poacher Tamsin', 17, 13, ('People4', 7), 2,
         ('Tamsin:', 'One deer. I took ONE deer from the King\'s wood', 'because my little brothers were starving.'),
         ('Tamsin:', 'Three months for a deer. The Lord who sold the', 'forest to the loggers got a medal.'))
    r.add_event('Tally Marks', 22, 13, [page(None, commands=text(
        'The cell is empty. Tally marks cover the wall,', 'hundreds of them. Whoever made them is long gone.'))])
    return r


def build_all():
    return {K.PRISON_1F: (ground_floor(), K.CASTLE_APPROACH), K.PRISON_CELLS: (cells(), K.CASTLE_APPROACH)}


if __name__ == '__main__':
    rooms = build_all()
    out = sys.argv[1] if len(sys.argv) > 1 else None
    for mid, (r, parent) in rooms.items():
        if out: r.render(out.replace('.png', '_%d.png' % mid), scale=0.5)
        if '--save' in sys.argv: r.save(mid, parent_id=parent, order=mid)
