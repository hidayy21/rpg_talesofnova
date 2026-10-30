# MAP006 - Saltwind Harbor: east of the Market District, facing the bay that lies east of the capital on the World
# Map. Harbor Street comes in from the Market (west) and runs down to the quay; the sea fills the east side, with
# three piers and the moored ships, and the breakwater runs out along the north to the lighthouse (the World Map
# shows the lighthouse on the bay's north point). Fish market south of the street, warehouse and cottages below.
#   python map_harbor.py preview.png [--grid]   -> preview image
#   python map_harbor.py --save                 -> write Map006 (editor must be closed)
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from town_kit import *
from nova_maplib import say, page, char, common_event
import kingdom as K
import data_ids as DI

W, H = 44, 32
m = Town(W, H, K.NAMES[K.HARBOR][0], K.NAMES[K.HARBOR][1], ground=COBBLE)
m.bgm = {'name': 'Town1', 'pan': 0, 'pitch': 95, 'volume': 70}
m.bgs = {'name': 'Sea', 'pan': 0, 'pitch': 100, 'volume': 60}
P = PROP
QX = 27                                         # the quay edge column; the sea is east of it
ST = K.ARRIVE['harbor_from_market'][2]          # Harbor Street y14..17, in line with the Market's east road
assert ST == 14

# ---------------------------------------------------------------- the sea, the quay and the breakwater
m.rect(QX + 1, 0, W - 1, H - 1, PORT_WATER)
for y in range(H): m.cell(QX, y, A5(QUAY[1]))
m.rect(QX, 2, W - 1, 7, COBBLE)                 # breakwater along the north, out to the lighthouse
for x in range(QX + 1, W): m.cell(x, 8, A5(QUAY[1]))
tower = [(176, 177), (184, 185), (192, 193), (200, 201), (192, 193), (208, 209)]
for i, (a, b) in enumerate(tower):
    m.put(40, 2 + i, C_ + a, 3 if i < len(tower) - 1 else 2); m.put(41, 2 + i, C_ + b, 3 if i < len(tower) - 1 else 2)
for x, y, t in ((38, 6, BARREL), (43, 6, CRATE), (33, 7, BOLLARD_ROPE), (30, 7, BOLLARD)): m.put(x, y, t)

# wooden piers running east over the water (bridge tiles keep the water continuous underneath)
for y0, length in ((ST, 12), (21, 9), (27, 7)):
    for y in range(y0, y0 + 3):
        m.cell(QX, y, COBBLE)
        for x in range(QX + 1, QX + 1 + length):
            m.put(x, y, BRIDGE_H)
    m.put(QX + length, y0, BOLLARD_ROPE, 3); m.put(QX + length, y0 + 2, BOLLARD, 3)

# ---------------------------------------------------------------- the city wall (low harbour wall) top and bottom
m.rect(0, 0, QX - 1, 0, FORT_TOP); m.rect(0, 1, QX - 1, 1, FORT_WALL)
m.rect(0, H - 1, QX - 1, H - 1, FORT_TOP)

# ---------------------------------------------------------------- north of Harbor Street
ho = m.building(1, 9, 3, 3, 5, 'blue', 'stone', windows=False)            # Harbormaster's Office
for x in (2, 4, 6, 8): m.put(x, ho - 3, WIN)
m.put(5, ho - 1, SIGN['crest']); m.put(3, ho - 1, WIN); m.put(7, ho - 1, WIN)
m.tall(1, ho - 2, BANNER_BLUE); m.tall(9, ho - 2, BANNER_BLUE)
sr = m.building(11, 18, 3, 3, 5, 'red', 'planks', win_tiles=(WIN, WIN_SHUT), door=14)  # Sailors' Rest
m.put(15, sr - 1, SIGN['eatery']); m.put(13, 4, CHIMNEY_B)
fc = m.building(20, 25, 5, 2, 4, 'thatch', 'wood', win_tiles=(WIN, WIN_FLOWER_G), door=23)  # Fisherman's Cottage
m.put(21, 6, CHIMNEY_A)
for x in (1, 10, 19, 26): m.put(x, ST - 2, BARREL)
for x in (6, 16, 24): m.lamp(x, ST - 1)

# ---------------------------------------------------------------- fish market south of the street (y18..22)
m.rect(0, 18, QX - 1, 23, COB_E)
fish_stalls = [(2, 18, ('fish_platter', 'fish_tub', 'fish_meal')),
               (9, 18, ('fish_tub', 'fish_platter', 'basket_empty')),
               (16, 18, ('fish_meal', 'fish_tub', 'fish_platter'))]
for x, y, wares in fish_stalls:
    m.tent(x, y)
    m.put(x, y + 3, P[wares[0]]); m.put(x + 2, y + 3, P[wares[2]]); m.put(x + 3, y + 3, P[wares[1]])
for x, y, t in ((22, 19, P['rope']), (24, 18, CRATE_GRAIN), (25, 18, CRATE), (26, 20, BOLLARD_ROPE),
                (22, 22, P['big_sacks']), (14, 22, P['tub_a']), (0, 22, BARREL), (26, 23, BOLLARD)):
    m.put(x, y, t)

# ---------------------------------------------------------------- south: Saltwind Warehouse and a cottage on Net Lane (y30)
wh = m.building(1, 11, 24, 2, 4, 'metal', 'boards', windows=False)        # Saltwind Warehouse
m.put(3, wh - 2, WIN); m.put(9, wh - 2, WIN)
m.put(5, wh - 1, ARCH_TOP); m.put(5, wh, ARCH_BOT); m.put(7, wh - 1, ARCH_TOP); m.put(7, wh, ARCH_BOT)
c2 = m.building(14, 20, 25, 2, 3, 'orange', 'mud', win_tiles=(WIN_FLOWER_P,), door=17)
m.put(15, 26, CHIMNEY_A)
for x, y, t in ((12, 29, CRATE_L_T), (12, 30, CRATE_L_B), (13, 30, CRATE), (22, 29, BARREL), (23, 29, BARREL),
                (25, 26, P['rope']), (24, 30, CRATE)):
    m.put(x, y, t, 3 if t == CRATE_L_T else 2)
m.lamp(22, 26)

# ---------------------------------------------------------------- vessels
m.obj('The Morning Gull', 36, 11, '$Boat', 0, ['The Morning Gull, a merchant ship bound for the Eastern Continent.'], step=False, direction=4)
m.obj('Royal Galleon', 38, 19, 'Vehicle', 7, ['A galleon of the Royal Navy, flying the lion of Nova.'], step=False, direction=6)
m.obj('Fishing Boat', 34, 25, 'Vehicle', 0, ['A fishing boat, still smelling of this morning\'s catch.'], step=False, direction=6)
m.obj('Fishing Boat', 38, 30, 'Vehicle', 0, ['Nets hang over the side to dry.'], step=False, direction=4)
m.obj('Lighthouse Beacon', 40, 1, '!Flame', 3, None, step=True, through=True, priority=2)
m.obj('Lighthouse Beacon', 41, 1, '!Flame', 3, None, step=True, through=True, priority=2)

# ---------------------------------------------------------------- doors and exits
m.locked_door("Harbormaster's Office", 5, ho, ['The Harbormaster is out on the piers.'], style=1)
m.locked_door("Sailors' Rest", 14, sr, ['"Rooms for sailors only."'])
m.locked_door('Saltwind Warehouse', 6, wh, ['The warehouse doors are barred from inside.'], style=1)
m.locked_door("Fisherman's Cottage", 23, fc, ['Someone is snoring inside.'])
m.locked_door("Netmaker's House", 17, c2, ['Nets everywhere - the door won\'t even open fully.'])
m.exit('To Market', [(0, y) for y in range(ST, ST + 4)], *K.ARRIVE['market_from_harbor'])

# ---------------------------------------------------------------- people
m.add_event('Fishmonger', 3, 21, [page(char('People2', 4, 2), commands=say('Fishmonger:',
            'Trout, eel, mackerel - caught before sunrise!', 'Grill it on the spot for you, if you like.') + common_event(DI.CE_FISH))])
m.add_event('Fishmonger', 10, 21, [page(char('People4', 2, 2), commands=say('Fishwife:',
            'Chowder! Hot chowder for cold sailors!') + common_event(DI.CE_FISH))])
m.npc('Oyster Seller', 17, 21, 'People1', 7, ('Oyster Seller:', 'Pearls? No, no. Only oysters today.', 'The pearls are on the Royal Galleon.'))
m.npc('Captain Mara', 33, ST + 1, 'People2', 3, ('Captain Mara:', 'The Morning Gull sails east when the winds turn.',
      'A swordswoman from the East asked about passage...', 'Friend of yours?'), direction=8)
m.npc('Naval Officer', 34, 22, 'People3', 7, ('Naval Officer:', 'The galleon is under royal guard.', 'No visitors without a writ from the castle.'), direction=6)
m.npc('Old Fisherman', 33, 28, 'People4', 6, ('Old Fisherman:', 'Fifty years on this pier.', 'The sea gives, and the sea remembers.'), direction=6)
m.npc('Dockhand', 24, 16, 'People4', 4, ('Dockhand:', 'Heave! These crates are for the castle kitchens.'), move=1, freq=4)
m.npc('Dockhand', 12, 15, 'People1', 0, ('Dockhand:', 'Watch your step on the wet stones.'), move=1)
m.npc('Lighthouse Keeper', 39, 7, 'People2', 2, ('Lighthouse Keeper:', 'The beacon has not gone dark in two hundred years.',
      'On a clear night you can see it from the castle tower.'), direction=2)
m.npc('Child', 31, 4, 'People4', 3, ('Child:', 'I\'m going to be a pirate! ...A royal pirate.'), direction=2)
m.critter('Harbor Cat', 6, 22, 'Nature', 1, 'Cat', 'The cat stares at the fish, then at you.', move=0)
m.critter('Harbor Cat', 20, 16, 'Nature', 1, 'Cat', 'Mrrow.', move=1)

if __name__ == '__main__':
    out = next((a for a in sys.argv[1:] if not a.startswith('--')), None)
    if out: m.render(out, scale=0.5, grid='--grid' in sys.argv)
    if '--save' in sys.argv: m.save(K.HARBOR, parent_id=K.PLAZA, order=6)
