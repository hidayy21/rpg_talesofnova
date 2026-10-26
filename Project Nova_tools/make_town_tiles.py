# Builds img/tilesets/Nova_Market_D.png: market / harbour props for the Outside tileset, copied from the
# Inside_B / Inside_C sheets (fish, baskets, goods, weapons, armour ...). Also returns the D-slot id of each prop
# and the passability flags copied from the Inside tileset, so the Outside tileset can use them.
import json, os
from PIL import Image

# the game folder sits next to this tools folder ('rpg_talesofnova' on the Mac, 'Project Nova' on Windows)
_HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.environ.get('NOVA_PROJ') or next(p for p in (os.path.join(_HERE, '..', n) for n in ('rpg_talesofnova', 'Project Nova'))
                                            if os.path.isdir(p)).replace('\\', '/') + '/'
TS = PROJ + 'img/tilesets/'
OUT_NAME = 'Nova_Market_D'

# (name, source sheet, local index) - local index uses the same numbering as RPG Maker (B/C local id).
PROPS = [
    # food / fish market
    ('fish_platter', 'C', 39), ('fish_meal', 'C', 32), ('roast', 'C', 33), ('fruit_bowl', 'C', 35),
    ('pie', 'C', 44), ('cake', 'C', 37), ('side_dish', 'C', 34), ('roast_pig', 'C', 36),
    ('basket_empty', 'C', 104), ('basket_grain', 'C', 105), ('basket_apples', 'C', 106), ('basket_bread', 'C', 107),
    ('sack_a', 'C', 96), ('sacks_b', 'C', 97), ('sacks_c', 'C', 98), ('fish_tub', 'B', 218),
    ('crate_grain', 'B', 232), ('crate_apples', 'B', 233), ('crate_oranges', 'B', 240), ('crate_greens', 'B', 241),
    ('big_sack_a', 'B', 248), ('big_sack_b', 'B', 249), ('big_sacks', 'B', 250), ('tub_a', 'B', 217),
    # magic / books
    ('potion_red', 'C', 103), ('potion_blue', 'C', 102), ('medicine_a', 'C', 99), ('medicine_b', 'C', 100),
    ('medicine_c', 'C', 101), ('scrolls_a', 'C', 82), ('scrolls_b', 'C', 83), ('crystal_table', 'B', 107),
    ('book_closed', 'C', 56), ('book_open', 'C', 60), ('old_book', 'C', 64), ('old_book_open', 'C', 68),
    ('map_a', 'C', 76), ('lab_equipment', 'C', 111), ('jewel_case_a', 'C', 125), ('jewel_case_b', 'C', 127),
    ('pendant', 'C', 124), ('necklace', 'C', 126), ('dry_flowers', 'C', 137), ('potted_a', 'C', 85),
    # weapons / armour
    ('sword', 'C', 128), ('swords', 'C', 129), ('swords_x', 'C', 130), ('axes', 'C', 131),
    ('spears', 'C', 132), ('whip', 'C', 134), ('knives', 'C', 135), ('bows', 'C', 147),
    ('shield_a', 'C', 138), ('shield_b', 'C', 139), ('helmet_a', 'C', 152), ('helmet_b', 'C', 153),
    ('helmet_gold', 'C', 154), ('hat_stand', 'C', 155), ('sword_rack_a', 'C', 144), ('sword_rack_b', 'C', 145),
    ('armor_stand_a', 'C', 160), ('armor_stand_b', 'C', 161), ('armor_stand_c', 'C', 162), ('armor_stand_d', 'C', 163),
    ('robe_a', 'C', 166), ('robe_b', 'C', 167), ('cape_stand', 'C', 165), ('mens_clothes', 'C', 164),
    ('hammers', 'C', 146), ('anvil_table_a', 'C', 148), ('anvil_table_b', 'C', 149), ('scrap_metal', 'C', 151),
    # pets / misc
    ('doll_bear', 'C', 112), ('doll_blue', 'C', 113), ('bowl', 'C', 53), ('rope', 'C', 122),
    ('gifts', 'C', 118), ('stacked_crates_a', 'B', 226), ('stacked_crates_b', 'B', 227), ('crate_small', 'B', 224),
]


def _src_xy(local):
    return ((local // 128) * 8 + local % 8) * 48, ((local % 128) // 8) * 48


def build(write=True):
    srcs = {'B': Image.open(TS + 'Inside_B.png').convert('RGBA'), 'C': Image.open(TS + 'Inside_C.png').convert('RGBA')}
    inside_flags = json.load(open(PROJ + 'data/Tilesets.json', encoding='utf8'))[3]['flags']
    sheet = Image.new('RGBA', (768, 768), (0, 0, 0, 0))
    ids, flags = {}, {}
    for n, (name, s, local) in enumerate(PROPS, start=1):    # local 0 stays empty, like every B-E sheet
        sx, sy = _src_xy(local)
        dx, dy = _src_xy(n)
        sheet.paste(srcs[s].crop((sx, sy, sx + 48, sy + 48)), (dx, dy))
        ids[name] = 512 + n
        flags[512 + n] = inside_flags[(0 if s == 'B' else 256) + local]
    if write:
        sheet.save(TS + OUT_NAME + '.png')
    return ids, flags


if __name__ == '__main__':
    ids, flags = build()
    print(len(ids), 'props ->', OUT_NAME + '.png')
