# MAP007 - Castle Approach: the castle's outer wall and gate (guarded), the moat, the Royal Prison yard (far west),
# the Royal Barracks with its training yard (west) and the knights' stables (east).
import sys
sys.path.insert(0, 'D:/RPG Maker MV/Project Nova_tools')
from town_kit import *
from nova_maplib import cmd, text, say, page, char
import kingdom as K
from town_kit import wander_route

OX = 14                                    # the prison yard takes the 14 columns west of the old map edge
W, H = 40 + OX, 34
m = Town(W, H, K.NAMES[K.CASTLE_APPROACH][0], K.NAMES[K.CASTLE_APPROACH][1], ground=COBBLE)
m.bgm = {'name': 'Castle1', 'pan': 0, 'pitch': 100, 'volume': 75}
P = PROP
GX = 20 + OX                               # gate centre column
BARRED_WIN, CELLAR_GRATE, SIGNBOARD = 41, 61, 72

# ---------------------------------------------------------------- castle wall (top surface + face), spires behind
m.rect(0, 0, W - 1, 4, CASTLE_TOP)
m.rect(0, 5, W - 1, 10, CASTLE_WALL)
# the keep behind the wall: its slate roof and three spires
m.rect(4 + OX, 0, 35 + OX, 1, ('A3', ROOF['indigo']))
for x0 in (6 + OX, 19 + OX, 32 + OX):
    for i, (a, b) in enumerate([(194, 195), (202, 203)]):
        m.put(x0, i, C_ + a, 3); m.put(x0 + 1, i, C_ + b, 3)
# gatehouse towers flanking the gate
for x0 in (GX - 4, GX + 3):
    for i, (a, b) in enumerate([(176, 177), (184, 185), (192, 193), (200, 201), (192, 193), (208, 209)]):
        y = 4 + i
        m.put(x0, y, C_ + a, 3 if i < 5 else 2); m.put(x0 + 1, y, C_ + b, 3 if i < 5 else 2)
# banners on the wall (same 4-column rhythm over the prison yard) and a lion crest over the gate
for x in (1, 5, 9, 13, 3 + OX, 7 + OX, 11 + OX, 28 + OX, 32 + OX, 36 + OX):
    m.tall(x, 6, BANNER_RED)
m.put(GX, 6, SIGN['crest'])
for x in (13 + OX, 26 + OX): m.put(x, 8, STAINED)

# ---------------------------------------------------------------- moat and the gate bridge
m.rect(0, 11, W - 1, 13, WATER)
for y in range(11, 14):
    for x in range(GX - 2, GX + 3):
        m.put(x, y, STONE_BRIDGE_V)
m.rect(GX - 2, 14, GX + 2, H - 1, COBBLE)

# ---------------------------------------------------------------- Royal Prison (far west)
m.rect(0, 15, OX - 1, 15, FORT_TOP)            # yard wall along the walkway ...
m.rect(0, 15, 0, H - 1, FORT_TOP)
m.rect(12, 15, 13, 15, COBBLE)                 # ... with a gate in its east end
pb = m.building(3, 11, 16, 2, 4, 'khaki', 'rockwall', windows=False)
for x in (4, 10): m.put(x, pb - 2, BARRED_WIN)
for x in (5, 9): m.put(x, pb, CELLAR_GRATE)    # the cells below get their air from these
m.tall(7, pb - 2, BANNER_RED)
m.put(4, pb + 2, SIGNBOARD)
for x, y in ((13, 24), (13, 25), (12, 25)): m.put(x, y, BARREL)
for y in (22, 23): m.put(1, y, HAY)
for x, y in ((1, 32), (13, 32), (1, 26), (13, 28)):
    m.put(x, y - 1, TREE_S1, 3); m.put(x, y, TREE_S3)

# ---------------------------------------------------------------- Royal Barracks (west)
m.rect(OX, 15, 15 + OX, H - 1, DIRT)           # packed earth of the yard
m.rect(OX, 15, 15 + OX, 15, FORT_TOP)
m.rect(OX, 15, OX, H - 1, FORT_TOP)
bb = m.building(2 + OX, 13 + OX, 16, 2, 4, 'metal', 'stone', windows=False)
for x in (3, 5, 10, 12): m.put(x + OX, bb - 1, WIN_SHUT)
m.put(7 + OX, bb - 1, SIGN['crest']); m.put(8 + OX, bb - 1, SIGN['sword'])
m.tall(2 + OX, bb - 2, BANNER_RED); m.tall(13 + OX, bb - 2, BANNER_RED)
# training yard: dummies, hay, weapon racks, a fire pit
for x, y in ((3, 25), (6, 25), (9, 25), (3, 29), (6, 29)):
    m.put(x + OX, y, SCARECROW)
for x, y in ((12, 24), (13, 24), (12, 30)): m.put(x + OX, y, HAY)
m.put(1 + OX, 23, P['sword_rack_a']); m.put(2 + OX, 23, P['spears']); m.put(1 + OX, 31, P['sword_rack_b'])
m.put(14 + OX, 27, P['axes']); m.put(9 + OX, 31, FIRE_PIT); m.put(14 + OX, 32, BARREL)
# fence to the avenue, with a gate in front of the barracks door
m.rect(15 + OX, 16, 15 + OX, bb, STONE_FENCE, layer=1)
m.rect(15 + OX, bb + 3, 15 + OX, H - 1, STONE_FENCE, layer=1)

# ---------------------------------------------------------------- Knights' Stables (east)
m.rect(24 + OX, 15, W - 1, H - 1, GRASS)
sb = m.building(26 + OX, 37 + OX, 16, 2, 3, 'wood', 'log', windows=False)
for x in (28, 31, 34): m.put(x + OX, sb, ARCH_BOT); m.put(x + OX, sb - 1, ARCH_TOP)
m.put(36 + OX, sb - 1, SIGN['blank'])
m.rect(25 + OX, 23, 38 + OX, 32, DIRT)         # paddock
m.rect(24 + OX, 22, W - 1, 22, FENCE, layer=1); m.rect(24 + OX, 22, 24 + OX, 33, FENCE, layer=1); m.rect(W - 1, 22, W - 1, 33, FENCE, layer=1)
for x, y in ((26, 24), (27, 24), (37, 31), (36, 31)): m.put(x + OX, y, HAY)
m.put(31 + OX, 31, P['tub_a']); m.put(32 + OX, 31, BUCKET)
m.big_tree(37 + OX, 25, BIG_TREE2)

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
m.door('Royal Barracks', 7 + OX, bb, K.BARRACKS, 8, 13)
m.locked_door("Knights' Stables", 31 + OX, sb, ['The stable boy waves: "Mind the dung!"'], style=1)
m.exit('To Plaza', [(x + OX, H - 1) for x in range(17, 23)], K.PLAZA, 19, 1, 2)
m.rect(17 + OX, 14, 23 + OX, H - 1, COBBLE)

# drilling soldiers: march back and forth
m.npc('Soldier', 4 + OX, 27, 'People3', 6, ('Soldier:', 'One-two! One-two! ...Sorry, can\'t talk. Drill.'),
      route=wander_route('RRRWLLLW'), speed=3)
m.npc('Soldier', 7 + OX, 27, 'People3', 7, ('Soldier:', 'The Drill Sergeant can hear a yawn from fifty paces.'),
      route=wander_route('RRRWLLLW'), speed=3)
m.npc('Drill Sergeant', 5 + OX, 23, 'People4', 4, ('Drill Sergeant:', 'Shields UP! Swords DOWN! Feet APART!',
      'You there - fancy a round in the yard? Come back when you\'re stronger.'), direction=2)
m.npc('Archer', 11 + OX, 28, 'People4', 5, ('Barracks Archer:', 'Diana of the Silent Hawk trained here once.', 'Never missed. Not once.'), direction=4)
m.npc('Quartermaster', 9 + OX, bb + 1, 'People2', 7, ('Quartermaster:', 'Rations, blankets and boots for three hundred men.',
      'And nobody ever says thank you.'), direction=2)
m.critter('Warhorse', 30 + OX, 26, 'Nature', 3, 'Horse', 'The warhorse tosses its mane proudly.', move=1)
m.critter('Warhorse', 34 + OX, 28, 'Nature', 3, 'Horse', 'A grey mare nibbles at the hay.', move=1)
# outside the paddock: the horses wander, so the paddock has no gate
m.npc('Stable Boy', 35 + OX, sb + 1, 'People4', 0, ('Stable Boy:', 'Sir Roland\'s horse is the biggest one.', 'He calls it "Small".'))
m.npc('Knight', 33 + OX, sb + 1, 'People3', 7, ('Knight:', 'We ride to the northern border at dawn.'), direction=2)

# the prison yard
m.door('Royal Prison', 7, pb, K.PRISON_1F, 9, 12, style=6)
for x in (5, 9):
    m.obj('Brazier', x, pb + 1, '!Other2', 7, None, step=True)
m.npc('Prison Guard', 6, pb + 1, 'People3', 6, ('Prison Guard:', 'The Royal Prison. Visitors keep their hands',
      'to themselves and their questions short.'))
m.npc('Prison Guard', 8, pb + 1, 'People3', 7, ('Prison Guard:', 'Every rogue in Nova ends up behind this door',
      'sooner or later. Some of them twice.'))
m.sign('Prison Sign', 4, pb + 2, ['\\C[6]ROYAL PRISON OF NOVA\\C[0]', 'By order of the Crown. Visitors must report',
       'to the Warden on entering.'])
m.npc('Patrol', 9, 28, 'People3', 6, ('Soldier:', 'Prison yard patrol. Twelve laps a watch.',
      'Nobody has ever escaped. ...Nobody has ever tried.'), move=1, freq=2)

if __name__ == '__main__':
    out = sys.argv[1] if len(sys.argv) > 1 else None
    if out: m.render(out, scale=0.5, grid='--grid' in sys.argv)
    if '--save' in sys.argv: m.save(K.CASTLE_APPROACH, parent_id=K.PLAZA, order=7)
