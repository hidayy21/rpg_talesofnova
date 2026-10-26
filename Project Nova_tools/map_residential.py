# MAP005 - Residential Quarter "Lantern Row": tall townhouses, a canal with stone bridges, cottages with gardens,
# and to the south Ember Lane with the Ashveil family house (3 storeys).
import sys
sys.path.insert(0, 'D:/RPG Maker MV/Project Nova_tools')
from town_kit import *
from nova_maplib import cmd, text, say, page, char
import kingdom as K

W, H = 44, 56
m = Town(W, H, K.NAMES[K.RESIDENTIAL][0], K.NAMES[K.RESIDENTIAL][1], ground=COBBLE)
m.bgm = {'name': 'Town2', 'pan': 0, 'pitch': 95, 'volume': 70}
m.bgs = {'name': 'River', 'pan': 0, 'pitch': 100, 'volume': 30}
P = PROP
CX = (21, 22)       # canal columns

# ---------------------------------------------------------------- canal with stone bridges
m.rect(CX[0], 0, CX[1], H - 1, CANAL)
def bridge(y0, y1):
    for y in range(y0, y1 + 1):
        for x in range(CX[0] - 1, CX[1] + 2):
            m.put(x, y, STONE_BRIDGE_H)
bridge(15, 18)
bridge(30, 31)
bridge(44, 47)

# ---------------------------------------------------------------- north row: tall townhouses (roofs off the top)
b0 = m.building(0, 6, 0, 2, 8, 'indigo', 'plaster', win_tiles=(WIN_FLOWER_P, WIN))
b1 = m.building(7, 13, 0, 2, 9, 'red', 'tudor', windows=False)          # the visitable townhouse, 3 storeys
for y in (b1 - 7, b1 - 4, b1 - 1):
    for x in (8, 10, 12): m.put(x, y, WIN_FLOWER_G if y == b1 - 4 else WIN)
m.put(10, b1 - 1, LG_TOP)
b2 = m.building(14, 19, 0, 3, 7, 'dressed', 'white', win_tiles=(MID_WIN,))
b3 = m.building(25, 31, 0, 2, 8, 'orange', 'brick', win_tiles=(WIN, WIN_FLOWER_P))
b4 = m.building(32, 36, 0, 3, 7, 'khaki', 'tudor', win_tiles=(WIN_FLOWER_G,))
# lane north to Baker's Lane (x37..40), then a narrow house
b5 = m.building(41, 43, 0, 3, 6, 'blue', 'plaster', win_tiles=(WIN,))
for x in (3, 16, 28, 34): m.put(x, 1, CHIMNEY_A)
for x in (9, 12): m.put(x, 0, CHIMNEY_B)
# window boxes, a bench-pot, lanterns along the canal
for x, y in ((6, 11), (14, 11), (25, 11), (31, 11)): m.put(x, y, POT)
# keep doorsteps clear: nothing on the row right below a door
for y in (3, 7, 11): m.lamp(CX[0] - 1, y); m.lamp(CX[1] + 1, y)

# ---------------------------------------------------------------- the main road y15..18 (from the plaza)
for x in (4, 16, 28, 38): m.lamp(x, 14)

# ---------------------------------------------------------------- west middle: cottages with gardens
m.rect(0, 19, CX[0] - 2, 29, GRASS)
m.rect(0, 25, CX[0] - 2, 25, ROAD)                         # garden path
c0 = m.building(1, 6, 19, 2, 3, 'thatch', 'wood', win_tiles=(WIN_FLOWER_G,))
c1 = m.building(10, 16, 19, 2, 3, 'green', 'plaster', win_tiles=(WIN_FLOWER_P, WIN))
# vegetable patch and fence
m.rect(1, 26, 7, 29, DIRT)
for x in range(1, 8):
    m.put(x, 27, CROPS[x % 4]); m.put(x, 28, CROPS[(x + 1) % 4])
m.rect(0, 26, 0, 29, FENCE, layer=1); m.rect(8, 26, 8, 29, FENCE, layer=1)
m.put(4, 29, SCARECROW)
# laundry line: clothes on stands between two posts
m.put(11, 26, P['mens_clothes']); m.put(12, 26, P['robe_b']); m.put(13, 26, P['cape_stand'])
m.put(15, 27, BUCKET); m.put(16, 27, P['basket_empty'])
m.big_tree(17, 21, BIG_TREE2); m.big_tree(17, 27)
m.put(9, 21, FLOWER_BUSH); m.put(9, 23, FLOWERS[1]); m.put(7, 23, WELL)

# ---------------------------------------------------------------- east middle: lantern park with a pond
m.rect(CX[1] + 2, 19, 43, 29, GRASS)
m.rect(28, 21, 34, 25, WATER)
m.rect(25, 26, 43, 26, ROAD)
for x, y in ((26, 20), (36, 20), (26, 24), (36, 24), (31, 27), (40, 27)): m.lamp(x, y)
m.big_tree(38, 20); m.big_tree(41, 22, BIG_TREE2); m.big_tree(24, 22, BIG_TREE2)
for x, t in ((27, FLOWERS[0]), (35, FLOWERS[2]), (29, FLOWERS[3]), (33, FLOWERS[1])): m.put(x, 20 if x < 31 else 26 if x > 40 else 20, t)
m.put(31, 23, BOULDER)                                     # stepping rock in the pond
m.put(38, 24, STEPPING); m.put(39, 24, STEPPING)
m.put(42, 28, FERN); m.put(25, 28, FLOWER_BUSH)

# ---------------------------------------------------------------- lower lane y30..31
m.rect(0, 30, W - 1, 31, COBBLE)

# ---------------------------------------------------------------- Ember Lane: houses y32..43 facing the street y44..47
# back gardens behind the lower houses (seen from the lane above)
m.rect(0, 32, 5, 34, GRASS); m.rect(24, 32, 31, 34, GRASS); m.rect(37, 32, 43, 34, GRASS)
m.put(1, 33, FLOWER_BUSH); m.put(4, 33, TREE_S1); m.put(25, 33, TREE_S2); m.put(28, 33, FLOWERS[2]); m.put(30, 33, BUSH_S); m.put(39, 33, TREE_S1); m.put(42, 33, FLOWERS[0])
h0 = m.building(0, 5, 35, 3, 6, 'green', 'plaster', win_tiles=(WIN_FLOWER_G, WIN))
# the Ashveil house: 3 storeys, a window row per storey, ash-grey roof
ash = m.building(7, 15, 32, 3, 9, 'metal', 'brickstone', windows=False)
for y in (ash - 7, ash - 4, ash - 1):
    for x in (8, 10, 12, 14):
        if (x, y) != (12, ash - 1): m.put(x, y, WIN_FLOWER_P if y == ash - 4 else WIN)
m.put(11, ash - 1, LG_TOP)
for x in (9, 13): m.put(x, 33, CHIMNEY_B)
m.rect(16, 32, 19, 43, COBBLE)                              # alley from the lane down to Ember Lane
h1 = m.building(24, 31, 35, 3, 6, 'orange', 'brick', win_tiles=(WIN, WIN_FLOWER_P))
h2 = m.building(37, 43, 35, 3, 6, 'blue', 'white', win_tiles=(MID_WIN,))
for x in (2, 27, 40): m.put(x, 36, CHIMNEY_A)
m.rect(33, 32, 35, H - 1, COBBLE)                          # passage south to the market
m.rect(0, 44, W - 1, 47, COBBLE)                           # Ember Lane
m.put(6, 43, POT); m.put(16, 43, POT); m.put(32, 43, BARREL); m.put(36, 43, POT)

# ---------------------------------------------------------------- south of Ember Lane: front gardens, then the next street's roofs
m.rect(0, 48, 19, 51, GRASS); m.rect(24, 48, 32, 51, GRASS); m.rect(36, 48, W - 1, 51, GRASS)
for x in (4, 12, 28, 40): m.lamp(x, 48)
m.rect(0, 51, 19, 51, HEDGE_TOP); m.rect(24, 51, 32, 51, HEDGE_TOP); m.rect(36, 51, W - 1, 51, HEDGE_TOP)
for x, t in ((2, FLOWERS[0]), (7, FLOWERS[3]), (9, FLOWER_BUSH), (15, FLOWERS[1]), (26, FLOWERS[2]), (31, FERN), (38, FLOWERS[0]), (42, FLOWER_BUSH)):
    m.put(x, 49, t)
m.big_tree(17, 48, BIG_TREE2); m.big_tree(25, 49)
m.building(0, 9, 52, 4, 0, 'orange', 'plaster', windows=False)
m.building(10, 19, 52, 4, 0, 'red', 'plaster', windows=False)
m.building(24, 32, 52, 4, 0, 'indigo', 'plaster', windows=False)
m.building(36, 43, 52, 4, 0, 'green', 'plaster', windows=False)
for x in (5, 14, 28, 40): m.put(x, 53, CHIMNEY_A)

# ---------------------------------------------------------------- doors & exits
m.door('Lantern Row Townhouse', 10, b1, K.TOWNHOUSE_1F, 6, 11)
m.locked_door('Townhouse', 3, b0, ['A child\'s voice: "Mama says don\'t open the door!"'])
m.locked_door('Townhouse', 16, b2, ['The door is locked. Piano music drifts out.'], style=1)
m.locked_door('Townhouse', 28, b3, ['The door is locked.'])
m.locked_door('Townhouse', 34, b4, ['A note: "Gone to the harbor - back at sundown."'])
m.locked_door('Narrow House', 42, b5, ['The door is locked.'])
m.locked_door('Cottage', 3, c0, ['An old woman calls: "Wipe your boots first!"', '...The door stays shut.'])
m.locked_door('Cottage', 13, c1, ['The door is locked. A cat watches from the window.'])
m.door('Ashveil House', 11, ash, K.ASHVEIL_1F, 11, 13)
m.sign('Ashveil Nameplate', 10, ash, ['A brass nameplate by the door:', '\\C[6]ASHVEIL\\C[0]'])
m.locked_door('House', 3, h0, ['The door is locked. Someone is practising the lute, badly.'])
m.locked_door('House', 28, h1, ['The door is locked.'])
m.locked_door('House', 40, h2, ['A note: "Away at the Harvest Fair."'], style=1)
m.exit('To Plaza', [(W - 1, y) for y in range(15, 19)], K.PLAZA, 1, 15, 6)
m.exit("To Baker's Lane", [(x, 0) for x in range(37, 41)], *K.ARRIVE['bakers_from_residential'])
m.exit('To Market', [(x, H - 1) for x in range(33, 36)], K.MARKET, 20, 1, 2)
m.rect(37, 0, 40, 13, COBBLE)

# ---------------------------------------------------------------- people & animals
NIGHT = 10   # NovaLighting "Night Switch"
_ll = say('Lamplighter', 'Sixty-two lanterns on Lantern Row.', 'Shall I light them? Or put them out for the day?')
_ll.append(cmd(102, [['Light the lamps (night)', 'Put them out (day)', 'Leave them'], 2, 0, 2, 0]))
_ll += [cmd(402, [0, 'Light the lamps (night)']), cmd(121, [NIGHT, NIGHT, 0], 1), cmd(0, [], 1),
        cmd(402, [1, 'Put them out (day)']), cmd(121, [NIGHT, NIGHT, 1], 1), cmd(0, [], 1),
        cmd(402, [2, 'Leave them']), cmd(0, [], 1), cmd(404, [])]
m.add_event('Lamplighter', 20, 13, [page(char('People4', 6, 2), commands=_ll)])
m.npc('Gardener', 4, 26, 'People4', 2, ('Gardener:', 'Turnips for the inn, cabbages for the tavern.', 'And pumpkins for the Harvest Festival!'), direction=2)
m.npc('Housewife', 12, 27, 'People1', 3, ('Housewife:', 'Laundry day. If it rains, I\'m blaming the wizards.'), direction=8)
m.npc('Children', 30, 27, 'People4', 3, ('Child:', 'Tag! You\'re it!'), move=1, speed=4, freq=5)
m.npc('Children', 37, 23, 'People4', 0, ('Child:', 'The Snowblade lady can cut a falling leaf in half!'), move=1, speed=4, freq=5)
m.npc('Old Couple', 33, 27, 'People2', 2, ('Old Man:', 'We\'ve fed the ducks in this pond for forty years.', 'There are no ducks. We feed them anyway.'), direction=8)
m.npc('Canal Guard', 24, 17, 'People3', 6, ('City Watch:', 'This canal runs from the castle moat to the sea.'), direction=4)
m.npc('Mother', 6, 16, 'People1', 1, ('Mother:', 'The townhouse with red roof belongs to Lady Mirelle.', 'She lets rooms to travellers, they say.'), move=1)
m.npc('Painter', 38, 28, 'People2', 6, ('Painter:', 'The light on the pond at dusk... if only I could paint it.'), direction=8)
m.critter('Dog', 25, 29, 'Nature', 0, 'Dog', 'Woof! Woof!', move=1, speed=4)
m.critter('Cat', 15, 21, 'Nature', 1, 'Cat', 'The cat ignores you completely.', move=0)
m.critter('Hen', 6, 28, 'Nature', 2, None, 'Bawk! The hen pecks at the turnips.', move=1)
# Ember Lane
m.npc('Neighbour', 8, 46, 'People1', 7, ('Neighbour:', 'The Ashveils? Lovely family. Loud, mind you.', 'Something is always on fire in that house.'), direction=2)
m.npc('Old Woman', 27, 45, 'People2', 2, ('Old Woman:', 'Ember Lane, they call it. All these chimneys.', 'Never a cold night on this street.'), direction=2)
m.npc('Boy', 38, 46, 'People4', 0, ('Boy:', 'When I grow up I\'m going to be a knight', 'like the Ashveil girl!'), move=1, speed=4, freq=4)
m.critter('Cat', 30, 49, 'Nature', 1, 'Cat', 'The cat is asleep in the flowerbed.', move=0)

# ---------------------------------------------------------------- touch-ups made by hand in the editor (Oct 2026)
m.put(15, 4, 0, 2); m.put(15, 4, 32, 3); m.put(17, 4, 0, 2); m.put(17, 4, 32, 3)
m.put(15, 6, 0, 2); m.put(15, 6, 32, 3); m.put(17, 6, 0, 2); m.put(17, 6, 32, 3)
m.put(15, 8, 0, 2); m.put(15, 8, 32, 3); m.put(17, 8, 0, 2); m.put(17, 8, 32, 3)
m.put(17, 20, 112, 3); m.put(18, 20, 113, 3)
m.put(19, 21, 113, 3); m.put(24, 21, 112, 3); m.put(25, 21, 113, 3); m.put(41, 21, 112, 3); m.put(42, 21, 113, 3)
m.put(19, 22, 121, 3); m.put(23, 22, 112, 3); m.put(26, 22, 211, 2); m.put(26, 22, 113, 3); m.put(40, 22, 112, 3); m.put(43, 22, 113, 3)
m.put(17, 23, 120, 3); m.put(18, 23, 121, 3); m.put(23, 23, 120, 3); m.put(26, 23, 219, 2); m.put(26, 23, 121, 3); m.put(40, 23, 120, 3); m.put(43, 23, 121, 3)
m.put(24, 24, 120, 3); m.put(25, 24, 121, 3); m.put(41, 24, 120, 3); m.put(42, 24, 121, 3)
m.put(25, 32, 93, 3)
m.put(26, 33, 93, 3)
m.put(25, 34, 101, 3); m.put(26, 34, 101, 3)
m.put(17, 47, 112, 3); m.put(18, 47, 113, 3)
m.put(16, 48, 112, 3); m.put(19, 48, 113, 3)
m.put(16, 49, 120, 3); m.put(19, 49, 121, 3)
m.put(17, 50, 120, 3); m.put(18, 50, 121, 3)

if __name__ == '__main__':
    out = sys.argv[1] if len(sys.argv) > 1 else None
    if out: m.render(out, scale=0.5, grid='--grid' in sys.argv)
    if '--save' in sys.argv: m.save(K.RESIDENTIAL, parent_id=K.PLAZA, order=5)
