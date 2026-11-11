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
# (46 Wild Forest 1 and 47 Ice Cave are the user's own maps)
# chapters 7 and 11: the Bloodrose family seat (where it sits on the World Map is still open in Story_Plan.md)
VILLA_BLOODROSE = 48
VILLA_HALL, VILLA_UPPER, VILLA_LIBRARY, VILLA_ARCHIVE = 49, 50, 51, 52   # inside the villa
VILLA_DINING, VILLA_MUSIC, VILLA_WEST, VILLA_EAST = 53, 54, 55, 56        # either side of the hall and the gallery
VILLA_LYSANDRE, VILLA_STUDY, VILLA_GUEST, VILLA_GUEST2 = 57, 58, 59, 60   # rooms off the wings
VILLA_BALLROOM = 61                                                        # behind the hall; shut until the story opens it
SW_VILLA_BALLROOM = 12                                                     # switch: the ballroom doors open
VILLA_CELLARS, VILLA_DEPTHS = 62, 63                                       # beneath the villa (rm-map-forge layouts)
VILLA_ROSE_WAY = 64                                                        # the old way up, out under the Bloodrose tree
SW_VILLA_TRAPDOOR = 13                                                     # switch: the ballroom floor gives way (set it after the fight)
SW_VILLA_GRATE = 14                                                       # switch: the cellar grate is raised (lever)
SW_VILLA_ROSE_WAY = 15                                                     # switch: the slab under the tree is open both ways
VAR_VILLA_BRAZIERS = 10                                                    # variable: braziers lit in order (4 = seal awake, 5 = open)
LILYDALE = 65                                                              # chapter 7: the village the party reaches first
HOLLOW_WOOD, MISTVEIL = 66, 67                                             # the misty wood between Lilydale and the villa

NAMES = {
    WORLD: ('World Map', 'Western Continent'),
    FROSTHOLLOW: ('Frosthollow', 'Frosthollow'),
    FROST_INN: ('Frosthollow - Hearthfire Inn', 'Hearthfire Inn'),
    FROST_STORE: ('Frosthollow - General Store', 'Frosthollow General Store'),
    FROST_SMITHY: ('Frosthollow - Smithy', "Hilda's Forge"),
    VILLA_BLOODROSE: ('Villa Bloodrose', 'Villa Bloodrose'),
    VILLA_HALL: ('Villa Bloodrose - Grand Hall', 'Villa Bloodrose - Grand Hall'),
    VILLA_UPPER: ('Villa Bloodrose - Upper Floor', 'Villa Bloodrose - Gallery'),
    VILLA_LIBRARY: ('Villa Bloodrose - Library', 'The Bloodrose Library'),
    VILLA_ARCHIVE: ('Villa Bloodrose - Sealed Archive', 'The Sealed Archive'),
    VILLA_DINING: ('Villa Bloodrose - Dining Room', 'Villa Bloodrose - Dining Room'),
    VILLA_MUSIC: ('Villa Bloodrose - Music Room', 'Villa Bloodrose - Music Room'),
    VILLA_WEST: ('Villa Bloodrose - West Wing', 'Villa Bloodrose - West Wing'),
    VILLA_EAST: ('Villa Bloodrose - East Wing', 'Villa Bloodrose - East Wing'),
    VILLA_LYSANDRE: ("Villa Bloodrose - Lysandre's Room", "Lysandre's Room"),
    VILLA_STUDY: ("Villa Bloodrose - David's Study", "The Master's Study"),
    VILLA_GUEST: ('Villa Bloodrose - Guest Room', 'Guest Room'),
    VILLA_GUEST2: ('Villa Bloodrose - Blue Guest Room', 'Blue Guest Room'),
    VILLA_BALLROOM: ('Villa Bloodrose - Ballroom', 'Villa Bloodrose - Ballroom'),
    VILLA_CELLARS: ('Villa Bloodrose - Cellars', 'Bloodrose Cellars'),
    VILLA_DEPTHS: ('Villa Bloodrose - Old Foundations', 'The Old Foundations'),
    VILLA_ROSE_WAY: ('Villa Bloodrose - Rose Way', 'The Rose Way'),
    LILYDALE: ('Lilydale', 'Lilydale'),
    HOLLOW_WOOD: ('Hollow Wood', 'Hollow Wood'),
    MISTVEIL: ('Mistveil', 'Mistveil'),
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
    # Villa Bloodrose: arrive at the foot of the south road, out of Mistveil
    'bloodrose_from_world': (VILLA_BLOODROSE, 21, 48, 8),
    # Chapter 7: Lilydale -> Hollow Wood -> Mistveil -> the villa, each road leaving by the top edge (no World Map link
    # until the region is decided)
    'hollow_from_lilydale': (HOLLOW_WOOD, 20, 48, 8), 'lilydale_from_hollow': (LILYDALE, 25, 1, 2),
    'mistveil_from_hollow': (MISTVEIL, 21, 48, 8), 'hollow_from_mistveil': (HOLLOW_WOOD, 21, 1, 2),
    'mistveil_from_bloodrose': (MISTVEIL, 21, 1, 2),
    # ... and inside (map_villa_bloodrose_interiors.py)
    'hall_from_bloodrose': (VILLA_HALL, 15, 18, 8), 'bloodrose_from_hall': (VILLA_BLOODROSE, 21, 16, 2),
    'villa_hall_from_dining': (VILLA_HALL, 1, 13, 6), 'villa_dining_from_hall': (VILLA_DINING, 15, 12, 4),
    'villa_hall_from_music': (VILLA_HALL, 29, 13, 4), 'villa_music_from_hall': (VILLA_MUSIC, 1, 12, 6),
    'upper_from_hall_w': (VILLA_UPPER, 9, 13, 2), 'upper_from_hall_e': (VILLA_UPPER, 21, 13, 2),
    'hall_from_upper_w': (VILLA_HALL, 9, 4, 2), 'hall_from_upper_e': (VILLA_HALL, 21, 4, 2),
    'west_from_upper': (VILLA_WEST, 24, 5, 4), 'upper_from_west': (VILLA_UPPER, 1, 6, 6),
    'east_from_upper': (VILLA_EAST, 1, 5, 6), 'upper_from_east': (VILLA_UPPER, 29, 6, 4),
    'library_from_upper': (VILLA_LIBRARY, 13, 22, 8), 'upper_from_library': (VILLA_UPPER, 15, 4, 2),
    'archive_from_library': (VILLA_ARCHIVE, 7, 10, 8), 'library_from_archive': (VILLA_LIBRARY, 23, 5, 2),
    'lysandre_from_east': (VILLA_LYSANDRE, 6, 8, 8), 'east_from_lysandre': (VILLA_EAST, 5, 4, 2),
    'study_from_west': (VILLA_STUDY, 6, 8, 8), 'west_from_study': (VILLA_WEST, 10, 4, 2),
    'guest_from_east': (VILLA_GUEST, 5, 7, 8), 'east_from_guest': (VILLA_EAST, 11, 4, 2),
    'guest2_from_east': (VILLA_GUEST2, 5, 7, 8), 'east_from_guest2': (VILLA_EAST, 17, 4, 2),
    'ballroom_from_hall': (VILLA_BALLROOM, 15, 22, 8), 'hall_from_ballroom': (VILLA_HALL, 15, 4, 2),
    # beneath the villa (map_villa_bloodrose_depths.py): the ballroom trapdoor drops the party into the cellars; the
    # way out climbs the Rose Way to a slab under the Bloodrose tree in the garden
    'villa_cellars_from_ballroom': (VILLA_CELLARS, 39, 26, 2),
    'villa_roseway_from_depths': (VILLA_ROSE_WAY, 17, 40, 8), 'villa_depths_from_roseway': (VILLA_DEPTHS, 24, 14, 2),
    'villa_roseway_from_bloodrose': (VILLA_ROSE_WAY, 8, 4, 2), 'villa_bloodrose_from_roseway': (VILLA_BLOODROSE, 8, 29, 2),
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
