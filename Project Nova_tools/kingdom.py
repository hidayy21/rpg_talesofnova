# Map ids and connection points for the Royal Kingdom of Nova. Every map script imports this so exits and doors
# always agree. (x, y, direction) = where the player arrives.
BAKERS_LANE = 2
PLAZA, MARKET, RESIDENTIAL, HARBOR, CASTLE_APPROACH = 3, 4, 5, 6, 7
WEAPON_SHOP, ARMOR_SHOP, MAGIC_SHOP, PET_SHOP = 8, 9, 10, 11
TAVERN, INN, BARRACKS, BAKERY, TOWNHOUSE_1F, TOWNHOUSE_2F = 12, 13, 14, 15, 16, 17
ASHVEIL_1F, ASHVEIL_2F, ASHVEIL_3F = 18, 19, 20
PRISON_1F, PRISON_CELLS = 21, 22

NAMES = {
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
}

# Arrival points, filled in by the map scripts' layouts (kept here so both sides of a link use one source).
ARRIVE = {
    # Grand Plaza
    'plaza_from_bakers': (PLAZA, 0, 2, 2),        # NW alley, top-left
    'plaza_from_residential': (PLAZA, 1, 16, 6),  # west road
    'plaza_from_market': (PLAZA, 42, 16, 4),      # east road
    'plaza_from_harbor': (PLAZA, 19, 32, 8),      # south road
    'plaza_from_castle': (PLAZA, 19, 1, 2),       # north road
    # Baker's Lane (existing map: street 1 = y7..10, street 2 = y17..20)
    'bakers_from_plaza': (BAKERS_LANE, 30, 7, 4),
    'bakers_from_residential': (BAKERS_LANE, 1, 17, 6),
    # Residential Quarter (south end of the market alley)
    'residential_from_market': (RESIDENTIAL, 33, 54, 8),
}
