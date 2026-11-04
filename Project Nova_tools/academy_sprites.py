# The Royal Magic Academy's people, put together with sprite_gen.py (RPG Maker MV's Character Generator parts):
#   Nova_Students1-3  24 students in uniform: blazer, white shirt and tie in their dormitory's colours, and a cape of
#                     the same colour in one of the generator's three cuts (Dawnward navy and gold, Duskward maroon
#                     and violet)
#   Nova_Faculty1-2   the staff in robes; several professors wear witch hats (never violet or pink: that is Mira's)
# CAST maps the NPC names used by the Academy's map scripts to their (sheet, index); STUDENTS lists the student looks.
#   python3 academy_sprites.py           -> preview _work/academy_sprites.png
#   python3 academy_sprites.py --apply   -> write the sheets to img/characters/
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sprite_gen as G

hair = lambda f, r=None: {'FrontHair': f, 'RearHair': r or f}
DAWN = {'c1': 20, 'c2': 23, 'c4': 55, 'cloak': 20, 'cloak_lining': 55}        # navy, white shirt, gold tie
DUSK = {'c1': 46, 'c2': 23, 'c4': 16, 'cloak': 46, 'cloak_lining': 16}        # maroon, white shirt, violet tie
SKINS = (36, 37, 38, 41, 40, 36, 44, 37)
HAIRS_M = ((3, 44), (5, 22), (7, 0), (11, 2), (2, 41), (13, 18), (16, 43), (4, 17))      # (style, gradient row)
HAIRS_F = ((5, 0), (12, 4), (9, 17), (2, 42), (14, 31), (6, 22), (11, 1), (3, 44))


def student(house, sex, n):
    cols = dict(DAWN if house == 'dawn' else DUSK)
    style, colour = (HAIRS_M if sex == 'Male' else HAIRS_F)[n % 8]
    cols.update({'skin': SKINS[(n * 3 + (house == 'dusk')) % len(SKINS)], 'hair': colour})
    parts = {'Body': 1, ('Clothing2' if sex == 'Male' else 'Clothing1'): 12 if sex == 'Male' else 13, **hair(style),
             'Cloak': 1 + (n + (house == 'dusk')) % 3}                       # the three cuts of cape, in turn
    return {'sex': sex, 'parts': parts, 'colors': cols}


def staff(sex, parts, colors):
    return {'sex': sex, 'parts': {'Body': 1, **parts}, 'colors': colors}


M, F = 'Male', 'Female'
STUDENT_SHEETS = {
    'Nova_Students1': [student('dawn', M if i % 2 == 0 else F, i) for i in range(8)],
    'Nova_Students2': [student('dusk', M if i % 2 == 0 else F, i + 1) for i in range(8)],
    'Nova_Students3': [student('dawn' if i < 4 else 'dusk', M if i % 2 else F, i + 4) for i in range(8)],
}
FACULTY = [   # (name in the maps, character)
    ('Archmage Corvin Vale', staff(M, {'Clothing2': 19, 'Beard': 6, 'Cloak': 2, **hair(11)},
                                   {'skin': 40, 'hair': 5, 'beard': 5, 'c1': 27, 'c2': 64, 'cloak': 64, 'cloak_lining': 27})),
    ('Professor Elspeth Rook', staff(F, {'Clothing1': 10, 'Hat': 1, **hair(1)},                     # Elemental Theory: fire
                                     {'skin': 37, 'hair': 22, 'c1': 46, 'c2': 15, 'c3': 55, 'c4': 55, 'hat': 53, 'hat_band': 55})),
    ('Professor Halden', staff(M, {'Clothing2': 19, 'Beard': 3, 'Glasses': 2, **hair(9)},          # Wards & Runes
                               {'skin': 41, 'hair': 52, 'beard': 52, 'c1': 24, 'c2': 5})),
    ('Duelling Master Kestrel', staff(M, {'Clothing2': 23, 'Cloak': 1, **hair(16)},
                                      {'skin': 36, 'hair': 22, 'c1': 22, 'c2': 46, 'c3': 22, 'c4': 18, 'cloak': 46, 'cloak_lining': 22})),
    ('Professor Aubert', staff(M, {'Clothing2': 19, 'Beard': 9, 'Glasses': 1, 'Hat': 1, **hair(1)},  # Arcane History
                               {'skin': 40, 'hair': 18, 'beard': 18, 'c1': 2, 'c2': 66, 'hat': 2, 'hat_band': 41})),
    ('Professor Brisk', staff(M, {'Clothing2': 19, 'Glasses': 1, **hair(13)},                     # Alchemy
                              {'skin': 36, 'hair': 35, 'c1': 3, 'c2': 55})),
    ('Professor of Herbs', staff(F, {'Clothing1': 8, 'Hat': 1, **hair(3)},                        # Professor Moss
                                 {'skin': 38, 'hair': 17, 'c1': 19, 'c2': 49, 'c3': 49, 'c4': 21, 'hat': 49, 'hat_band': 41})),
    ('Professor Lyra Venn', staff(F, {'Clothing1': 10, 'Hat': 1, **hair(6)},                      # Astronomy
                                  {'skin': 37, 'hair': 1, 'c1': 20, 'c2': 55, 'c3': 23, 'c4': 45, 'hat': 20, 'hat_band': 55})),
    ('Professor Wren-Hollis', staff(F, {'Clothing1': 10, 'Cloak': 2, 'Hat': 1, **hair(4)},        # Enchantment Theory
                                    {'skin': 36, 'hair': 5, 'c1': 22, 'c2': 5, 'c3': 5, 'c4': 5, 'cloak': 22, 'cloak_lining': 18,
                                     'hat': 52, 'hat_band': 5})),
    ('Librarian Ottoline', staff(F, {'Clothing1': 8, 'Glasses': 1, **hair(15)},
                                 {'skin': 40, 'hair': 18, 'c1': 60, 'c2': 41, 'c3': 2, 'c4': 2})),
    ('Healer Agnes', staff(F, {'Clothing1': 8, **hair(7)}, {'skin': 41, 'hair': 42, 'c1': 23, 'c2': 63, 'c3': 7, 'c4': 7})),
    ('Master Enchanter Thibault', staff(M, {'Clothing2': 19, 'Beard': 5, 'Cloak': 3, **hair(14)},
                                        {'skin': 36, 'hair': 17, 'beard': 17, 'c1': 17, 'c2': 55, 'cloak': 41, 'cloak_lining': 55})),
    ('Familiar Keeper Pim', staff(F, {'Clothing1': 14, **hair(10)}, {'skin': 38, 'hair': 0, 'c1': 49, 'c2': 23, 'c4': 55})),
    ('Registrar Fenwick', staff(M, {'Clothing2': 13, 'Glasses': 1, **hair(8)}, {'skin': 40, 'hair': 52, 'c1': 22, 'c2': 23, 'c4': 2})),
    ('Hall Steward', staff(M, {'Clothing2': 13, **hair(15)}, {'skin': 41, 'hair': 43, 'c1': 2, 'c2': 23, 'c4': 2})),
    ('Academy Sentinel', staff(M, {'Clothing2': 23, 'Cloak': 2, **hair(16)},
                               {'skin': 36, 'hair': 22, 'c1': 20, 'c2': 55, 'c3': 20, 'c4': 55, 'cloak': 20, 'cloak_lining': 55})),
]
FACULTY_SHEETS = {'Nova_Faculty1': [c for _, c in FACULTY[:8]], 'Nova_Faculty2': [c for _, c in FACULTY[8:16]]}


# the heroes in uniform (img/characters/Nova_Heroes_Uniform.png): Kael and Selene keep their own heads (sprite_gen.head_swap
# on a generator body in uniform); Mira, whose hair is all under her hat on her own sprite, is rebuilt with the
# generator's hair in her pink (style 14 facing the camera, style 4 from the side and behind), without the hat
def hero_body(sex, house, cloak, skin=36, extra=None):
    cols = dict(DAWN if house == 'dawn' else DUSK); cols['skin'] = skin
    parts = {'Body': 1, ('Clothing2' if sex == 'Male' else 'Clothing1'): 12 if sex == 'Male' else 13, 'Cloak': cloak}
    parts.update((extra or {}).get('parts', {})); cols.update((extra or {}).get('colors', {}))
    return {'sex': sex, 'parts': parts, 'colors': cols}


HEROES = [   # (name, how it is made)
    ('Kael (Dawnward)', lambda: G.head_swap(G.compose(hero_body('Male', 'dawn', 2)), 'Actor4', 0)),
    ('Mira (Dawnward)', lambda: G.by_direction(                 # facing the camera: hair 14; from the side and behind: hair 4
        G.compose(hero_body('Female', 'dawn', 2, skin=37, extra={'parts': hair(14), 'colors': {'hair': 13, 'eyes': 48}})),
        G.compose(hero_body('Female', 'dawn', 2, skin=37, extra={'parts': hair(4), 'colors': {'hair': 13, 'eyes': 48}})))),
    ('Selene (Duskward)', lambda: G.head_swap(G.compose(hero_body('Female', 'dusk', 2)), 'family1', 0, long_hair=True)),
]
HERO_SHEET = 'Nova_Heroes_Uniform'
# Selene is a generator character all through (family1: FrontHair 6, RearHair 2 in hair colour 22, eyes 28, the white
# Clothing 13), so her battler and damage strip in uniform are built straight from the parts:
#   img/sv_actors/Nova_Heroes_Uniform_3.png   (the generator's own naming: sheet name + index + 1)
#   img/characters/Nova_Damage_Uniform.png    Selene at index 2, the first (facing down) row
SELENE = {'sex': 'Female', 'parts': {'Body': 1, 'Clothing1': 13, 'Cloak': 2, 'FrontHair': 6, 'RearHair': 2},
          'colors': {**DUSK, 'eyes': 28, 'hair': 22}}
HERO_SV = {'Nova_Heroes_Uniform_3': SELENE}
DAMAGE_SHEET, DAMAGE = 'Nova_Damage_Uniform', {2: SELENE}


def damage_sheet():
    out = G.Image.new('RGBA', (576, 384), (0, 0, 0, 0))
    for i, c in DAMAGE.items():
        out.alpha_composite(G.compose(c, 'TVD'), ((i % 4) * 144, (i // 4) * 192))
    return out


def hero_sheet():
    out = G.Image.new('RGBA', (576, 384), (0, 0, 0, 0))
    for i, (_, make) in enumerate(HEROES):
        out.alpha_composite(make(), ((i % 4) * 144, (i // 4) * 192))
    return out

CAST = {name: ('Nova_Faculty%d' % (1 + i // 8), i % 8) for i, (name, _) in enumerate(FACULTY)}
CAST['Professor Moss'] = CAST['Professor of Herbs']
CAST['Professor Rook'] = CAST['Professor Elspeth Rook']
STUDENTS = [(sheet, i) for sheet in STUDENT_SHEETS for i in range(8)]
CAST['Dawnward Prefect'] = ('Nova_Students1', 0)
CAST['Duskward Prefect'] = ('Nova_Students2', 2)
CAST['Prefect'] = ('Nova_Students3', 1)


def recast(events, seed=0):
    """Give the Academy's people their sprites: named staff from CAST, every 'Student' a student look in turn."""
    k = seed
    for e in events:
        if not e: continue
        look = CAST.get(e['name'])
        if look is None and e['name'] == 'Student':
            look = STUDENTS[k % len(STUDENTS)]; k += 5          # step through the looks so neighbours differ
        if look is None: continue
        for pg in e['pages']:
            if pg['image'].get('characterName'):
                pg['image']['characterName'], pg['image']['characterIndex'] = look


if __name__ == '__main__':
    from PIL import Image, ImageDraw
    sheets = {**STUDENT_SHEETS, **FACULTY_SHEETS}
    if '--apply' in sys.argv:
        for name, chars in sheets.items():
            G.sheet(chars).save(os.path.join(G.HERE, '..', 'img', 'characters', name + '.png'))
            print('wrote img/characters/%s.png' % name)
        hero_sheet().save(os.path.join(G.HERE, '..', 'img', 'characters', HERO_SHEET + '.png'))
        print('wrote img/characters/%s.png' % HERO_SHEET)
        for name, c in HERO_SV.items():
            G.compose(c, 'SV').save(os.path.join(G.HERE, '..', 'img', 'sv_actors', name + '.png'))
            print('wrote img/sv_actors/%s.png' % name)
        damage_sheet().save(os.path.join(G.HERE, '..', 'img', 'characters', DAMAGE_SHEET + '.png'))
        print('wrote img/characters/%s.png' % DAMAGE_SHEET)
    S = 2
    out = Image.new('RGBA', (8 * 48 * S + 150, len(sheets) * 48 * S + 10), (70, 75, 90, 255)); d = ImageDraw.Draw(out)
    names = {**{s: ['%s %d' % (s[5:], i) for i in range(8)] for s in STUDENT_SHEETS},
             'Nova_Faculty1': [n for n, _ in FACULTY[:8]], 'Nova_Faculty2': [n for n, _ in FACULTY[8:16]]}
    for r, (name, chars) in enumerate(sheets.items()):
        d.text((4, r * 48 * S + 40), name, fill=(255, 255, 160))
        for i, c in enumerate(chars):
            out.alpha_composite(G.compose(c).crop((48, 0, 96, 48)).resize((48 * S, 48 * S), Image.NEAREST), (150 + i * 48 * S, r * 48 * S + 4))
    out.save(os.path.join(G.HERE, '_work', 'academy_sprites.png'))
