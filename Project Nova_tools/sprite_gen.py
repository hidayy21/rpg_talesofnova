# Walking sprites (img/characters) put together from RPG Maker MV's Character Generator parts, without the editor:
# every TV_<Part>_pNN.png layer is recoloured through its _c mask (each mask colour marks one colour slot: skin, hair,
# robe, trim...) with a row of the generator's gradients.png, then the layers are stacked back to front.
# A character = {'sex': 'Male'|'Female', 'parts': {part: number}, 'colors': {slot: gradient row}}.
#   slots: skin, eyes, hair, beard, c1-c4 (clothing colour boxes), cloak, cloak_lining, hat, hat_band
#   parts: the generator's part names (Clothing1, FrontHair...: number), plus 'Hat': 1 for a witch hat
#   python3 sprite_gen.py   -> _work/sprite_samples.png (a few samples, enlarged)
import os, sys, glob
from PIL import Image

GEN = os.environ.get('NOVA_GENERATOR') or next((p for p in (
    os.path.expanduser('~/Library/Application Support/Steam/steamapps/common/RPG Maker MV/RPG Maker MV.app/Contents/MacOS/Generator'),
    'C:/Program Files (x86)/Steam/steamapps/common/RPG Maker MV/Generator') if os.path.isdir(p)), None)
HERE = os.path.dirname(os.path.abspath(__file__))
# back to front, as the generator stacks them for the walking sprite (RearHair2 is the back of the head: over the body)
ORDER = ['Cloak2', 'Wing2', 'Tail2', 'Body', 'RearHair2', 'FacialMark', 'Beard2', 'Clothing2', 'Clothing1',
         'Beard1', 'RearHair1', 'Cloak1', 'FrontHair2', 'FrontHair1', 'BeastEars', 'Glasses', 'AccB', 'AccA', 'Wing1', 'Tail1']
# the same character as a side-view battler (img/sv_actors, 576x384) and as the damage strip (img/characters Damage
# sheets, 144x48: three frames of lying down). These sheets have one layer per part: (file part, recipe keys)
ORDERS = {
    # (checked: Selene's own battler, family1_1, comes out pixel for pixel)
    'SV': [('Wing', ('Wing',)), ('Tail', ('Tail',)), ('Cloak2', ('Cloak',)), ('body', ('Body',)),
           ('RearHair1', ('RearHair',)), ('FacialMark', ('FacialMark',)), ('Ears', ('Ears',)), ('Beard', ('Beard',)),
           ('Clothing1', ('Clothing1', 'Clothing2')), ('Cloak1', ('Cloak',)), ('FrontHair', ('FrontHair',)),
           ('BeastEars', ('BeastEars',)), ('Glasses', ('Glasses',)), ('AccB', ('AccB',)), ('AccA', ('AccA',))],
    'TVD': [('Wing', ('Wing',)), ('Tail', ('Tail',)), ('Body', ('Body',)), ('RearHair', ('RearHair',)),
            ('FacialMark', ('FacialMark',)), ('Ears', ('Ears',)), ('Beard', ('Beard',)),
            ('Clothing', ('Clothing1', 'Clothing2')), ('Cloak', ('Cloak',)), ('FrontHair', ('FrontHair',)),
            ('BeastEars', ('BeastEars',)), ('Glasses', ('Glasses',)), ('AccB', ('AccB',)), ('AccA', ('AccA',))],
}
SIZE = {'TV': (144, 192), 'SV': (576, 384), 'TVD': (144, 48)}
# mask colour -> slot, per part family
MASK = {
    'Body': {(249, 193, 157): 'skin', (44, 128, 203): 'eyes', (79, 65, 60): 'eyes_dark'},
    'Hair': {(252, 203, 10): 'hair', (184, 146, 197): 'hair'},
    'Beard': {(252, 203, 10): 'beard'},
    # clothing has up to four colour slots, numbered like the generator's own colour boxes
    'Clothing': {(174, 134, 130): 'c1', (254, 157, 30): 'c2', (217, 164, 4): 'c3', (28, 118, 208): 'c4'},
    'Acc': {(174, 134, 130): 'c1', (254, 157, 30): 'c2', (217, 164, 4): 'c3', (28, 118, 208): 'c4'},
    'Cloak': {(216, 172, 0): 'cloak', (163, 7, 8): 'cloak_lining'},
}
_grad = None


def gradients():
    global _grad
    if _grad is None:
        g = Image.open(os.path.join(GEN, 'gradients.png')).convert('RGB')
        _grad = [[g.getpixel((x, r * 4 + 2)) for x in range(256)] for r in range(g.height // 4)]
    return _grad


def family(part):
    for f in ('Hair', 'Beard', 'Clothing', 'Cloak', 'Acc', 'Body'):
        if f.lower() in part.lower(): return f
    return None


def layer(sex, part, n, colors, kind='TV'):
    path = os.path.join(GEN, kind, sex, '%s_%s_p%02d.png' % (kind, part, n))
    if not os.path.isfile(path): return None
    base = Image.open(path).convert('RGBA')
    mpath = path[:-4] + '_c.png'
    if not os.path.isfile(mpath): return base
    mask = Image.open(mpath).convert('RGBA')
    slots = MASK.get(family(part), {})
    rows = gradients()
    out = base.copy()
    bp, mp, op = base.load(), mask.load(), out.load()
    for y in range(base.height):
        for x in range(base.width):
            r, g, b, a = bp[x, y]
            if not a: continue
            m = mp[x, y]
            if not m[3]: continue
            slot = slots.get(m[:3])
            if slot is None or colors.get(slot) is None: continue
            lum = 0.299 * r + 0.587 * g + 0.114 * b
            op[x, y] = rows[colors[slot]][max(0, min(255, int(255 - lum)))] + (a,)
    return out


# ---------------------------------------------------------------- the witch hat (the generator has none)
# Lifted from the green witch in img/characters/Actor3.png (index 7): the crown and brim are the teal pixels, the band
# the gold ones, plus the black outline round them. Recoloured like a generator part: 'hat' and 'hat_band' slots.
HAT_SOURCE = ('Actor3', 7)
HAT_SHIFT = (0, -1)                     # where the hat sits on a generator head, relative to the source sprite
_hat = None


def _hat_pixels():
    """{(x, y): (kind, (r, g, b, a))} for the whole 144x192 sheet; kind 'hat' or 'band' (outline counts as hat)."""
    global _hat
    if _hat is not None: return _hat
    import colorsys
    src = Image.open(os.path.join(HERE, '..', 'img', 'characters', HAT_SOURCE[0] + '.png')).convert('RGBA')
    i = HAT_SOURCE[1]
    src = src.crop(((i % 4) * 144, (i // 4) * 192, (i % 4) * 144 + 144, (i // 4) * 192 + 192))
    px = src.load()
    kind = {}
    for y in range(192):
        if y % 48 > 26: continue                                   # the hat is in the top half of every frame
        for x in range(144):
            r, g, b, a = px[x, y]
            if not a: continue
            h, sat, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
            if 0.44 <= h <= 0.6 and sat > 0.2: kind[(x, y)] = 'hat'
            elif 0.09 <= h <= 0.15 and sat > 0.5 and y % 48 < 18: kind[(x, y)] = 'band'
    # the dark outline that touches the hat
    for y in range(192):
        if y % 48 > 26: continue
        for x in range(144):
            r, g, b, a = px[x, y]
            if a and (x, y) not in kind and r + g + b < 120 and \
                    any(kind.get((x + dx, y + dy)) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                kind[(x, y)] = 'line'
    _hat = {k: (v, px[k]) for k, v in kind.items()}
    return _hat


def hat_layer(colors):
    rows = gradients()
    out = Image.new('RGBA', (144, 192), (0, 0, 0, 0))
    op = out.load()
    dx, dy = HAT_SHIFT
    for (x, y), (kind, (r, g, b, a)) in _hat_pixels().items():
        slot = {'hat': 'hat', 'band': 'hat_band', 'line': None}[kind]
        if slot and colors.get(slot) is not None:
            lum = 0.299 * r + 0.587 * g + 0.114 * b
            col = rows[colors[slot]][max(0, min(255, int(255 - lum * (1.6 if slot == 'hat' else 1))))] + (a,)
        else:
            col = (r, g, b, a)
        if 0 <= x + dx < 144 and 0 <= y + dy < 192: op[x + dx, y + dy] = col
    return out


def compose(char, kind='TV'):
    """One character: kind 'TV' the walking sprite, 144x192 (3 frames x 4 directions); 'SV' the side-view battler;
    'TVD' the damage strip. The witch hat is on the walking sprite only."""
    sex, parts, colors = char['sex'], char['parts'], char['colors']
    img = Image.new('RGBA', SIZE[kind], (0, 0, 0, 0))
    if kind != 'TV':
        for part, keys in ORDERS[kind]:
            n = next((parts[k] for k in keys if parts.get(k)), None)
            lay = n and layer(sex, part, n, colors, kind)
            if lay: img.alpha_composite(lay)
        return img
    for part in ORDER:
        for key in (part, part.rstrip('12')):
            if key in parts and parts[key]:
                lay = layer(sex, part, parts[key], colors)
                if lay: img.alpha_composite(lay)
                break
    if parts.get('Hat'): img.alpha_composite(hat_layer(colors))
    return img


def by_direction(down, rest):
    """A sprite made of two: the 'down' row (facing the camera) from one, the left/right/up rows from the other."""
    out = rest.copy()
    out.paste(down.crop((0, 0, 144, 48)), (0, 0))
    return out


def head_swap(body, src_sheet, index, neck=30, long_hair=False):
    """An existing character's head on a generator body (made without hair): above the neck row of each 48x48 frame
    the picture is the original's alone; below it the body, with long_hair the original's hair over it (pixels of
    the colours on top of the head, seen from behind)."""
    src = Image.open(os.path.join(HERE, '..', 'img', 'characters', src_sheet + '.png')).convert('RGBA')
    src = src.crop(((index % 4) * 144, (index // 4) * 192, (index % 4) * 144 + 144, (index // 4) * 192 + 192))
    out = body.copy()
    sp, op = src.load(), out.load()
    hair = {sp[x, y][:3] for y in range(144, 158) for x in range(144) if sp[x, y][3]} if long_hair else set()
    for y in range(192):
        for x in range(144):
            px = sp[x, y]
            if y % 48 < neck: op[x, y] = px
            elif px[3] and px[:3] in hair: op[x, y] = px
    return out


def sheet(chars):
    """Up to eight characters on one 576x384 sheet (RPG Maker's 4x2 layout)."""
    out = Image.new('RGBA', (576, 384), (0, 0, 0, 0))
    for i, c in enumerate(chars[:8]):
        out.alpha_composite(compose(c), ((i % 4) * 144, (i // 4) * 192))
    return out


def parts_of(sex):
    names = {}
    for f in glob.glob(os.path.join(GEN, 'TV', sex, 'TV_*_p*.png')):
        b = os.path.basename(f)
        if b.endswith('_c.png'): continue
        part, n = b[3:-4].rsplit('_p', 1)
        names.setdefault(part, []).append(int(n))
    return {k: sorted(v) for k, v in names.items()}


if __name__ == '__main__':
    assert GEN, 'RPG Maker MV Generator folder not found (set NOVA_GENERATOR)'
    import json
    print(json.dumps(parts_of('Male')))
