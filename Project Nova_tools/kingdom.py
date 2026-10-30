# Map ids and connection points for the Royal Kingdom of Nova. Every map script imports this so exits and doors
# always agree. (x, y, direction) = where the player arrives.
WORLD = 1
BAKERS_LANE = 2
PLAZA, MARKET, RESIDENTIAL, HARBOR, CASTLE_APPROACH = 3, 4, 5, 6, 7
WEAPON_SHOP, ARMOR_SHOP, MAGIC_SHOP, PET_SHOP = 8, 9, 10, 11
TAVERN, INN, BARRACKS, BAKERY, TOWNHOUSE_1F, TOWNHOUSE_2F = 12, 13, 14, 15, 16, 17
ASHVEIL_1F, ASHVEIL_2F, ASHVEIL_3F = 18, 19, 20
PRISON_1F, PRISON_CELLS = 21, 22
CITY_GATE = 23
HOLLOW_FARM, ROYAL_QUARTER, TERRACES = 24, 25, 26

NAMES = {
    WORLD: ('World Map', 'Western Continent'),
    PLAZA: ('Royal Kingdom of Nova', 'Royal Capital - Grand Plaza'),
    MARKET: ('Nova - Market District', 'Royal Capital - Market District'),
    RESIDENTIAL: ('Nova - Residential Quarter', 'Royal Capital - Lantern Row'),
    HARBOR: ('Nova - Harbor', 'Royal Capital - Saltwind Harbor'),
    CASTLE_APPROACH: ('Nova - Castle Approach', 'Royal Capital - Castle Approach'),
    WEAPON_SHOP: ('Nova - Weapon Shop', 'Ironhart Arms'),
    ARMOR_SHOP: ('Nova - Armor Shop', 'Bulwark & Thread'),
    MAGIC_SHOP: ('Nova - Magic Shop', "The Starlit Grimoire"),
    PET_SHOP: ('Nova - Pet Shop', 'Whisker & Paw'),
    TAVERN: ('Nova - Tavern & Guild', "The Lion's Rest - Tavern & Guild"),
    INN: ('Nova - Inn', 'The Silver Swan'),
    BARRACKS: ('Nova - Barracks', 'Royal Barracks'),
    BAKERY: ('Nova - Bakery', 'Golden Crust Bakery'),
    TOWNHOUSE_1F: ('Nova - Townhouse 1F', 'Lantern Row Townhouse'),
    TOWNHOUSE_2F: ('Nova - Townhouse 2F', 'Lantern Row Townhouse - 2F'),
    ASHVEIL_1F: ('Nova - Ashveil House 1F', 'Ashveil Residence'),
    ASHVEIL_2F: ('Nova - Ashveil House 2F', 'Ashveil Residence - 2F'),
    ASHVEIL_3F: ('Nova - Ashveil House 3F', 'Ashveil Residence - 3F'),
    PRISON_1F: ('Nova - Royal Prison 1F', 'Royal Prison'),
    PRISON_CELLS: ('Nova - Royal Prison Cells', 'Royal Prison - Cells'),
    CITY_GATE: ('Nova - Main Gate', 'Royal Capital - Main Gate'),
    HOLLOW_FARM: ('Nova - Hollow Farm', 'Hollow Farm'),
    ROYAL_QUARTER: ('Nova - Royal Quarter', 'Royal Capital - Royal Quarter'),
    TERRACES: ('Nova - Hearthstone Terraces', 'Royal Capital - Hearthstone Terraces'),
}

# Arrival points, filled in by the map scripts' layouts (kept here so both sides of a link use one source).
ARRIVE = {
    # Grand Plaza
    'plaza_from_residential': (PLAZA, 1, 16, 6),  # west road
    'plaza_from_market': (PLAZA, 42, 16, 4),      # east road
    'plaza_from_gate': (PLAZA, 21, 30, 8),        # south road, through the Main Gate
    'plaza_from_castle': (PLAZA, 19, 1, 2),       # north road
    # Baker's Lane lies west of Lantern Row (existing map: street 1 = y7..10, street 2 = y17..20), its east ends
    # meeting Lantern Row's west road (y15..18) and south-west road (y44..47)
    'bakers_from_residential_1': (BAKERS_LANE, 30, 7, 4),
    'bakers_from_residential_2': (BAKERS_LANE, 30, 17, 4),
    'residential_from_bakers_1': (RESIDENTIAL, 1, 15, 6),
    'residential_from_bakers_2': (RESIDENTIAL, 1, 44, 6),
    # The Main Gate: the only way in from the World Map (map_city_gate.py)
    'gate_from_plaza': (CITY_GATE, 20, 11, 2),           # on the bridge, just outside the gate
    'gate_from_world': (CITY_GATE, 20, 32, 8),           # bottom of the road
    'world_from_gate': (WORLD, 65, 37, 2),               # in front of the capital on the World Map
    # Hollow Farm, outside the walls west of the Main Gate: the gate road's west fork (y19..21)
    'farm_from_gate': (HOLLOW_FARM, 38, 19, 4),
    'gate_from_farm': (CITY_GATE, 1, 19, 6),
    # Royal Quarter, north-east, beside the castle: the moat walk (y14) and the Market's north alley (x20..22)
    'royal_from_castle': (ROYAL_QUARTER, 1, 14, 6),
    'castle_from_royal': (CASTLE_APPROACH, 52, 14, 4),
    'royal_from_market': (ROYAL_QUARTER, 20, 38, 8),
    'market_from_royal': (MARKET, 20, 1, 2),
    # Saltwind Harbor, east of the Market (the bay lies east of the capital on the World Map): the Market's
    # old East Gate road (y14..17)
    'harbor_from_market': (HARBOR, 1, 14, 6),
    'market_from_harbor': (MARKET, 44, 14, 4),
    # Hearthstone Terraces, north of Lantern Row: Lantern Row's north lane (x37..40)
    'terraces_from_residential': (TERRACES, 37, 36, 8),
    'residential_from_terraces': (RESIDENTIAL, 37, 1, 2),
    # ... and Castle Approach's moat walk (y14) runs on west into it, as it does east into the Royal Quarter
    'terraces_from_castle': (TERRACES, 42, 14, 4),
    'castle_from_terraces': (CASTLE_APPROACH, 1, 14, 6),
}
# City layout (every edge exit lands on the facing edge of its neighbour):
#                  Hearthstone Terraces - Castle Approach - Royal Quarter
#   Baker's Lane - Lantern Row ---------- Grand Plaza ----- Market District - Saltwind Harbor ~ the bay
#                  Hollow Farm ---------- Main Gate
#   (Hollow Farm and the Main Gate lie outside the city wall)
