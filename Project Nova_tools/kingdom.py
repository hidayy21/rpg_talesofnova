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
# outside the capital, north up the coast road (27-30 are the prologue's Sealed Vault, Skyreach Hill and Briarwood)
ACADEMY, ACADEMY_HALL = 31, 32
ACADEMY_COURT, ACADEMY_CLASSES, ACADEMY_LIBRARY, ACADEMY_UNDERCROFT, ACADEMY_UPPER, ACADEMY_TOWER = 33, 34, 35, 36, 37, 38
QUILL_INN, QUILL_APOTHECARY = 39, 40
ACADEMY_DINING = 41
# chapter 5: the walled border town at the end of the north road, before the pass to Arulustus
FROSTHOLLOW = 42
FROST_INN, FROST_STORE, FROST_SMITHY = 43, 44, 45      # its interiors

NAMES = {
    WORLD: ('World Map', 'Western Continent'),
    FROSTHOLLOW: ('Frosthollow', 'Frosthollow'),
    FROST_INN: ('Frosthollow - Hearthfire Inn', 'Hearthfire Inn'),
    FROST_STORE: ('Frosthollow - General Store', 'Frosthollow General Store'),
    FROST_SMITHY: ('Frosthollow - Smithy', "Hilda's Forge"),
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
    ACADEMY: ('Royal Magic Academy & Quillhaven', 'Quillhaven - Royal Magic Academy'),
    ACADEMY_HALL: ('Royal Magic Academy - Entrance Hall', 'Royal Magic Academy - Entrance Hall'),
    ACADEMY_DINING: ('Royal Magic Academy - Great Hall', 'Royal Magic Academy - Great Hall'),
    ACADEMY_COURT: ('Royal Magic Academy - Cloister Court', 'Royal Magic Academy - Cloister Court'),
    ACADEMY_CLASSES: ('Royal Magic Academy - Lecture Wing', 'Royal Magic Academy - Lecture Wing'),
    ACADEMY_LIBRARY: ('Royal Magic Academy - Library', 'Royal Magic Academy - Library & Infirmary'),
    ACADEMY_UNDERCROFT: ('Royal Magic Academy - Undercroft', 'Royal Magic Academy - Undercroft'),
    ACADEMY_UPPER: ('Royal Magic Academy - Upper Floor', 'Royal Magic Academy - Upper Floor'),
    ACADEMY_TOWER: ('Royal Magic Academy - Star Tower', 'Royal Magic Academy - Star Tower'),
    QUILL_INN: ('Quillhaven - Inkpot Inn', 'The Inkpot Inn'),
    QUILL_APOTHECARY: ('Quillhaven - Apothecary', 'Moonwell Apothecary'),
}

# Arrival points, filled in by the map scripts' layouts (kept here so both sides of a link use one source).
ARRIVE = {
    # Frosthollow <-> the World Map (the north road ends at the town icon, 26-27,11-12)
    'frosthollow_from_world': (FROSTHOLLOW, 27, 49, 8),
    'world_from_frosthollow': (WORLD, 26, 13, 2),
    # Frosthollow's interiors (doors on Map042) and back out onto their doorsteps
    'frost_inn_from_town': (FROST_INN, 11, 13, 8), 'town_from_frost_inn': (FROSTHOLLOW, 19, 23, 2),
    'frost_store_from_town': (FROST_STORE, 7, 11, 8), 'town_from_frost_store': (FROSTHOLLOW, 51, 22, 2),
    'frost_smithy_from_town': (FROST_SMITHY, 8, 11, 8), 'town_from_frost_smithy': (FROSTHOLLOW, 42, 26, 2),
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
    # Royal Magic Academy, north of the capital on the World Map, with the village of Quillhaven facing its gate
    # across the road: the road comes in from the east (the coast road) and the village lane from the south
    'academy_from_world_east': (ACADEMY, 54, 19, 4),
    'academy_from_world_south': (ACADEMY, 27, 48, 8),
    'world_from_academy_east': (WORLD, 63, 26, 6),       # on the spur road between the two icons, off the coast road
    'world_from_academy_south': (WORLD, 60, 28, 2),      # below Quillhaven's icon
    'hall_from_academy': (ACADEMY_HALL, 9, 20, 8),
    # inside the Academy (map_academy_castle.py)
    'upper_from_hall': (ACADEMY_UPPER, 30, 25, 8), 'hall_from_upper': (ACADEMY_HALL, 9, 7, 2),
    'court_from_hall_w': (ACADEMY_COURT, 13, 26, 8), 'court_from_hall_e': (ACADEMY_COURT, 23, 26, 8),
    'hall_from_court_w': (ACADEMY_HALL, 5, 4, 2), 'hall_from_court_e': (ACADEMY_HALL, 13, 4, 2),
    'under_from_hall': (ACADEMY_UNDERCROFT, 3, 5, 2), 'hall_from_under': (ACADEMY_HALL, 2, 19, 6),
    'dining_from_hall': (ACADEMY_DINING, 32, 14, 4), 'hall_from_dining': (ACADEMY_HALL, 1, 12, 6),
    'classes_from_court': (ACADEMY_CLASSES, 38, 22, 4), 'court_from_classes': (ACADEMY_COURT, 1, 16, 6),
    'library_from_court': (ACADEMY_LIBRARY, 1, 12, 6), 'court_from_library': (ACADEMY_COURT, 34, 16, 4),
    'tower_from_court': (ACADEMY_TOWER, 8, 15, 8), 'court_from_tower': (ACADEMY_COURT, 18, 8, 2),
    'academy_from_hall': (ACADEMY, 27, 11, 2),
    # Quillhaven's inn and apothecary (doors on Map031)
    'inn_from_village': (QUILL_INN, 5, 13, 8),
    'village_from_inn': (ACADEMY, 10, 28, 2),
    'apothecary_from_village': (QUILL_APOTHECARY, 7, 11, 8),
    'village_from_apothecary': (ACADEMY, 40, 28, 2),
}
# City layout (every edge exit lands on the facing edge of its neighbour):
#                  Hearthstone Terraces - Castle Approach - Royal Quarter
#   Baker's Lane - Lantern Row ---------- Grand Plaza ----- Market District - Saltwind Harbor ~ the bay
#                  Hollow Farm ---------- Main Gate
#   (Hollow Farm and the Main Gate lie outside the city wall)
