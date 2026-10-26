# MAP007 - Castle Approach: the castle's outer wall and gate (guarded), the moat, the Royal Barracks with its
# training yard (west) and the knights' stables (east).
import sys
sys.path.insert(0, 'D:/RPG Maker MV/Project Nova_tools')
from town_kit import *
from nova_maplib import cmd, text, say, page, char
import kingdom as K
from town_kit import wander_route

W, H = 40, 34
m = Town(W, H, K.NAMES[K.CASTLE_APPROACH][0], K.NAMES[K.CASTLE_APPROACH][1], ground=COBBLE)
m.bgm = {'name': 'Castle1', 'pan': 0, 'pitch': 100, 'volume': 75}
P = PROP
GX = 20                                    # gate centre column

# ---------------------------------------------------------------- castle wall (top surface + face), spires behind
m.rect(0, 0, W - 1, 4, CASTLE_TOP)
m.rect(0, 5, W - 1, 10, CASTLE_WALL)
# the keep behind the wall: its slate roof and three spires
m.rect(4, 0, 35, 1, ('A3', ROOF['indigo']))
for x0 in (6, 19, 32):
    for i, (a, b) in enumerate([(194, 195), (202, 203)]):
        m.put(x0, i, C_ + a, 3); m.put(x0 + 1, i, C_ + b, 3)
# gatehouse towers flanking the gate
for x0 in (GX - 4, GX + 3):
    for i, (a, b) in enumerate([(176, 177), (184, 185), (192, 193), (200, 201), (192, 193), (208, 209)]):
        y = 4 + i
        m.put(x0, y, C_ + a, 3 if i < 5 else 2); m.put(x0 + 1, y, C_ + b, 3 if i < 5 else 2)
# banners on the wall and a lion crest over the gate
for x in (3, 7, 11, 28, 32, 36):
    m.tall(x, 6, BANNER_RED)
m.put(GX, 6, SIGN['crest'])
for x in (13, 26): m.put(x, 8, STAINED)

# ---------------------------------------------------------------- moat and the gate bridge
m.rect(0, 11, W - 1, 13, WATER)
for y in range(11, 14):
    for x in range(GX - 2, GX + 3):
        m.put(x, y, STONE_BRIDGE_V)
m.rect(GX - 2, 14, GX + 2, H - 1, COBBLE)

# ---------------------------------------------------------------- Royal Barracks (west)
m.rect(0, 15, 15, H - 1, DIRT)                 # packed earth of the yard
m.rect(0, 15, 15, 15, FORT_TOP)
m.rect(0, 15, 0, H - 1, FORT_TOP)
bb = m.building(2, 13, 16, 2, 4, 'metal', 'stone', windows=False)
for x in (3, 5, 10, 12): m.put(x, bb - 1, WIN_SHUT)
m.put(7, bb - 1, SIGN['crest']); m.put(8, bb - 1, SIGN['sword'])
m.tall(2, bb - 2, BANNER_RED); m.tall(13, bb - 2, BANNER_RED)
# training yard: dummies, hay, weapon racks, a fire pit
for x, y in ((3, 25), (6, 25), (9, 25), (3, 29), (6, 29)):
    m.put(x, y, SCARECROW)
for x, y in ((12, 24), (13, 24), (12, 30)): m.put(x, y, HAY)
m.put(1, 23, P['sword_rack_a']); m.put(2, 23, P['spears']); m.put(1, 31, P['sword_rack_b'])
m.put(14, 27, P['axes']); m.put(9, 31, FIRE_PIT); m.put(14, 32, BARREL)
m.rect(15, 16, 15, H - 1, STONE_FENCE, layer=1)

# ---------------------------------------------------------------- Knights' Stables (east)
m.rect(24, 15, W - 1, H - 1, GRASS)
sb = m.building(26, 37, 16, 2, 3, 'wood', 'log', windows=False)
for x in (28, 31, 34): m.put(x, sb, ARCH_BOT); m.put(x, sb - 1, ARCH_TOP)
m.put(36, sb - 1, SIGN['blank'])
m.rect(25, 23, 38, 32, DIRT)                   # paddock
m.rect(24, 22, 39, 22, FENCE, layer=1); m.rect(24, 22, 24, 33, FENCE, layer=1); m.rect(39, 22, 39, 33, FENCE, layer=1)
for x, y in ((26, 24), (27, 24), (37, 31), (36, 31)): m.put(x, y, HAY)
m.put(31, 31, P['tub_a']); m.put(32, 31, BUCKET)
m.big_tree(37, 25, BIG_TREE2)

# ---------------------------------------------------------------- avenue dressing
for y in (16, 21, 26, 31): m.lamp(GX - 3, y); m.lamp(GX + 3, y)

# ---------------------------------------------------------------- events
m.add_event('Castle Gate', GX, 10, [page(char('!$Gate1', 0, 2, 0), commands=text(
    'The great gate of Castle Nova is shut.', 'Only those summoned by the crown may pass.'), walk_anim=False)])
m.npc('Gate Captain', GX - 2, 14, 'People3', 7, ('Gate Captain:', 'Halt! The castle is closed by royal decree.',
      'Petitions are heard at the Royal Gazette in the plaza.'), direction=2)
m.npc('Gate Guard', GX + 2, 14, 'People3', 6, ('Gate Guard:', 'The King has not held court since the Ashveil affair.',
      '...I said nothing. You heard nothing.'), direction=2)
for x in (GX - 3, GX + 3):
    m.obj('Brazier', x, 10, '!Other2', 7, None, step=True)
m.door('Royal Barracks', 7, bb, K.BARRACKS, 8, 13)
m.locked_door("Knights' Stables", 31, sb, ['The stable boy waves: "Mind the dung!"'], style=1)
m.exit('To Plaza', [(x, H - 1) for x in range(17, 23)], K.PLAZA, 19, 1, 2)
m.rect(17, 14, 23, H - 1, COBBLE)

# drilling soldiers: march back and forth
m.npc('Soldier', 4, 27, 'People3', 6, ('Soldier:', 'One-two! One-two! ...Sorry, can\'t talk. Drill.'),
      route=wander_route('RRRWLLLW'), speed=3)
m.npc('Soldier', 7, 27, 'People3', 7, ('Soldier:', 'The Drill Sergeant can hear a yawn from fifty paces.'),
      route=wander_route('RRRWLLLW'), speed=3)
m.npc('Drill Sergeant', 5, 23, 'People4', 4, ('Drill Sergeant:', 'Shields UP! Swords DOWN! Feet APART!',
      'You there - fancy a round in the yard? Come back when you\'re stronger.'), direction=2)
m.npc('Archer', 11, 28, 'People4', 5, ('Barracks Archer:', 'Diana of the Silent Hawk trained here once.', 'Never missed. Not once.'), direction=4)
m.npc('Quartermaster', 9, bb + 1, 'People2', 7, ('Quartermaster:', 'Rations, blankets and boots for three hundred men.',
      'And nobody ever says thank you.'), direction=2)
m.critter('Warhorse', 30, 26, 'Nature', 3, 'Horse', 'The warhorse tosses its mane proudly.', move=1)
m.critter('Warhorse', 34, 28, 'Nature', 3, 'Horse', 'A grey mare nibbles at the hay.', move=1)
m.npc('Stable Boy', 29, 31, 'People4', 0, ('Stable Boy:', 'Sir Roland\'s horse is the biggest one.', 'He calls it "Small".'), move=1)
m.npc('Knight', 33, sb + 1, 'People3', 7, ('Knight:', 'We ride to the northern border at dawn.'), direction=2)

if __name__ == '__main__':
    out = sys.argv[1] if len(sys.argv) > 1 else None
    if out: m.render(out, scale=0.5, grid='--grid' in sys.argv)
    if '--save' in sys.argv: m.save(K.CASTLE_APPROACH, parent_id=K.PLAZA, order=7)
