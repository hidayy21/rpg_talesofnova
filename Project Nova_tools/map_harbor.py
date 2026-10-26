# MAP006 - Saltwind Harbor: quay, fish market, piers with moored ships, a lighthouse on the breakwater.
import sys
sys.path.insert(0, 'D:/RPG Maker MV/Project Nova_tools')
from town_kit import *
from nova_maplib import cmd, text, say, page, char, common_event
import kingdom as K
import data_ids as DI

W, H = 46, 30
m = Town(W, H, K.NAMES[K.HARBOR][0], K.NAMES[K.HARBOR][1], ground=COBBLE)
m.bgm = {'name': 'Town1', 'pan': 0, 'pitch': 95, 'volume': 70}
m.bgs = {'name': 'Sea', 'pan': 0, 'pitch': 100, 'volume': 60}
P = PROP
QUAY_Y = 17

# ---------------------------------------------------------------- sea, quay wall, breakwater
m.rect(0, QUAY_Y + 1, W - 1, H - 1, PORT_WATER)
for x in range(W):
    m.cell(x, QUAY_Y, A5(QUAY[1]))
# stone breakwater running out to the lighthouse (east)
m.rect(39, QUAY_Y, 45, 26, COBBLE)
for x in range(39, 46): m.cell(x, 27, A5(QUAY[1]))
m.rect(39, 28, 45, H - 1, PORT_WATER)
for y in range(QUAY_Y, 27): m.cell(38, y, A5(QUAY[1]))
m.cell(38, QUAY_Y, COBBLE)

# wooden piers over the water (bridge tiles keep the water continuous underneath)
for x0, length in ((5, 9), (19, 10), (29, 8)):
    for x in range(x0, x0 + 3):
        m.cell(x, QUAY_Y, COBBLE)
        for y in range(QUAY_Y + 1, QUAY_Y + 1 + length):
            m.put(x, y, BRIDGE_V)
    m.put(x0, QUAY_Y + length, BOLLARD_ROPE, 3); m.put(x0 + 2, QUAY_Y + length, BOLLARD, 3)

# ---------------------------------------------------------------- the lighthouse (stone tower + beacon)
tower = [(176, 177), (184, 185), (192, 193), (200, 201), (192, 193), (208, 209)]
for i, (a, b) in enumerate(tower):
    y = 19 + i
    layer = 3 if i < len(tower) - 1 else 2
    m.put(42, y, C_ + a, layer); m.put(43, y, C_ + b, layer)
m.put(40, 25, BARREL); m.put(44, 25, CRATE)

# ---------------------------------------------------------------- north buildings (roofs off the top)
# Harbormaster's Office
m.building(1, 9, 0, 3, 6, 'blue', 'stone', windows=False)
for x in (2, 4, 6, 8): m.put(x, 5, WIN)
m.put(5, 7, SIGN['crest']); m.put(3, 7, WIN); m.put(7, 7, WIN)
m.tall(1, 6, BANNER_BLUE); m.tall(9, 6, BANNER_BLUE)
# Sailors' Rest (rooms above, galley below)
m.building(10, 17, 0, 3, 6, 'red', 'planks', win_tiles=(WIN, WIN_SHUT))
m.put(14, 7, SIGN['eatery']); m.put(12, 1, CHIMNEY_B)
# Saltwind Warehouse (big doors, crates)
m.building(25, 33, 0, 2, 7, 'metal', 'boards', windows=False)
m.put(27, 5, WIN); m.put(31, 5, WIN)
m.put(28, 7, ARCH_TOP); m.put(28, 8, ARCH_BOT); m.put(30, 7, ARCH_TOP); m.put(30, 8, ARCH_BOT)
for x, y, t in ((25, 9, CRATE_L_T), (25, 10, CRATE_L_B), (26, 10, CRATE), (32, 10, CRATE), (33, 10, BARREL),
                (33, 9, BARREL)):
    m.put(x, y, t, 3 if t == CRATE_L_T else 2)
# Fisherman's cottages (east)
m.building(38, 45, 0, 3, 5, 'thatch', 'wood', win_tiles=(WIN, WIN_FLOWER_G))
m.put(41, 1, CHIMNEY_A)

# ---------------------------------------------------------------- fish market on the quay (y11..16)
m.rect(0, 11, 37, 16, COB_E)
fish_stalls = [(2, 11, ('fish_platter', 'fish_tub', 'fish_meal')),
               (11, 11, ('fish_tub', 'fish_platter', 'basket_empty')),
               (25, 11, ('fish_meal', 'fish_tub', 'fish_platter'))]
for x, y, wares in fish_stalls:
    m.tent(x, y)
    m.put(x, y + 3, P[wares[0]]); m.put(x + 2, y + 3, P[wares[2]]); m.put(x + 3, y + 3, P[wares[1]])
# quayside clutter: barrels, crates, rope, bollards
for x, y, t in ((0, 16, BARREL), (1, 16, BARREL), (9, 16, CRATE), (15, 15, P['rope']), (17, 16, BOLLARD_ROPE),
                (24, 16, BOLLARD), (27, 16, CRATE_GRAIN), (34, 16, BOLLARD_ROPE), (36, 15, BARREL),
                (37, 15, P['big_sacks']), (13, 16, P['tub_a'])):
    m.put(x, y, t)
for x in (8, 18, 23, 33): m.lamp(x, 10)

# ---------------------------------------------------------------- vessels
m.obj('The Morning Gull', 23, 21, 'Vehicle', 1, ['The Morning Gull, a merchant ship bound for the Eastern Continent.'], step=False, direction=4)
m.obj('Fishing Boat', 4, 21, 'Vehicle', 0, ['A fishing boat, still smelling of this morning\'s catch.'], step=False, direction=6)
m.obj('Fishing Boat', 9, 24, 'Vehicle', 0, ['Nets hang over the side to dry.'], step=False, direction=4)
m.obj('Royal Galleon', 34, 22, 'Vehicle', 7, ['A galleon of the Royal Navy, flying the lion of Nova.'], step=False, direction=6)
m.obj('Lighthouse Beacon', 42, 18, '!Flame', 3, None, step=True, through=True, priority=2)
m.obj('Lighthouse Beacon', 43, 18, '!Flame', 3, None, step=True, through=True, priority=2)

# ---------------------------------------------------------------- doors and exits
m.locked_door("Harbormaster's Office", 5, 8, ['The Harbormaster is out on the piers.'], style=1)
m.locked_door("Sailors' Rest", 14, 8, ['"Rooms for sailors only."'])
m.locked_door('Saltwind Warehouse', 29, 8, ['The warehouse doors are barred from inside.'], style=1)
m.locked_door("Fisherman's Cottage", 41, 7, ['Someone is snoring inside.'])
m.exit('To Plaza', [(x, 0) for x in range(19, 25)], K.PLAZA, 19, 30, 8)
m.exit('To Market', [(x, 0) for x in range(34, 38)], K.MARKET, 20, 30, 8)
m.rect(19, 0, 24, 10, COBBLE); m.rect(34, 0, 37, 10, COBBLE)

# ---------------------------------------------------------------- people
m.add_event('Fishmonger', 3, 13, [page(char('People2', 4, 2), commands=say('Fishmonger:',
            'Trout, eel, mackerel - caught before sunrise!', 'Grill it on the spot for you, if you like.') + common_event(DI.CE_FISH))])
m.add_event('Fishmonger', 12, 13, [page(char('People4', 2, 2), commands=say('Fishwife:',
            'Chowder! Hot chowder for cold sailors!') + common_event(DI.CE_FISH))])
m.npc('Oyster Seller', 26, 13, 'People1', 7, ('Oyster Seller:', 'Pearls? No, no. Only oysters today.', 'The pearls are on the Royal Galleon.'))
m.npc('Captain Mara', 21, 20, 'People2', 3, ('Captain Mara:', 'The Morning Gull sails east when the winds turn.',
      'A swordswoman from the East asked about passage...', 'Friend of yours?'), direction=6)
m.npc('Naval Officer', 31, 20, 'People3', 7, ('Naval Officer:', 'The galleon is under royal guard.', 'No visitors without a writ from the castle.'), direction=4)
m.npc('Old Fisherman', 7, 25, 'People4', 6, ('Old Fisherman:', 'Fifty years on this pier.', 'The sea gives, and the sea remembers.'), direction=2)
m.npc('Dockhand', 30, 12, 'People4', 4, ('Dockhand:', 'Heave! These crates are for the castle kitchens.'), move=1, freq=4)
m.npc('Dockhand', 16, 14, 'People1', 0, ('Dockhand:', 'Watch your step on the wet stones.'), move=1)
m.npc('Lighthouse Keeper', 41, 23, 'People2', 2, ('Lighthouse Keeper:', 'The beacon has not gone dark in two hundred years.',
      'On a clear night you can see it from the castle tower.'), direction=4)
m.npc('Child', 20, 26, 'People4', 3, ('Child:', 'I\'m going to be a pirate! ...A royal pirate.'), direction=2)
m.critter('Harbor Cat', 6, 15, 'Nature', 1, 'Cat', 'The cat stares at the fish, then at you.', move=0)
m.critter('Harbor Cat', 27, 15, 'Nature', 1, 'Cat', 'Mrrow.', move=1)

if __name__ == '__main__':
    out = sys.argv[1] if len(sys.argv) > 1 else None
    if out: m.render(out, scale=0.5, grid='--grid' in sys.argv)
    if '--save' in sys.argv: m.save(K.HARBOR, parent_id=K.PLAZA, order=6)
