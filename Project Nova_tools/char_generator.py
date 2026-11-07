# Character Generator for Project Nova: builds a character from RPG Maker MV's own Generator parts (the ones the
# editor's Tools > Character Generator uses), without opening the editor. One recipe gives every sheet:
#
#   img/characters/$<Name>.png         walk sprite (one character, 3x4 frames)
#   img/characters/$<Name>_Down.png    knocked-down sprite (the generator's damage frames, same in every facing)
#   img/sv_actors/<Name>.png           side-view battler (usable as an animated enemy too)
#   img/faces/<Name>.png               face, index 0
#
#   python char_generator.py Homura            -> writes the sheets above
#   python char_generator.py Homura --preview  -> only a preview in Project Nova_previews/
#
# Colours: every part comes with a colour mask (*_c.png) whose key colours say which colour slot a pixel belongs
# to (hair, skin, eyes, the four clothing colours...). A slot is recoloured by mapping each pixel's lightness onto
# one row of Generator/gradients.png - the same rows the editor's colour picker shows (row 0 = the default blonde).
# Face parts come pre-split per slot (FG_<part>_pNN_c<n>_m<slot>.png).
import os, re, sys
import numpy as np
from PIL import Image, ImageFilter

PROJ = 'D:/RPG Maker MV/Project Nova/'
PREVIEWS = 'D:/RPG Maker MV/Project Nova_previews/'
GEN = next((p for p in (
    'C:/Program Files (x86)/Steam/steamapps/common/RPG Maker MV/Generator/',
    'C:/Program Files/Steam/steamapps/common/RPG Maker MV/Generator/',
    'C:/Program Files (x86)/KADOKAWA/RPGMV/Generator/',
    'C:/Program Files/KADOKAWA/RPGMV/Generator/') if os.path.isdir(p)), None)

# Colour slots: mask key colour <-> the m-number on face parts.
SLOTS = {'skin': 'F9C19D', 'eyes': '2C80CB', 'hair': 'FCCB0A', 'hair2': 'B892C5', 'mark': '009296',
         'kemono': 'D3CEC7', 'cloth1': 'FE9D1E', 'cloth2': '1C76D0', 'cloth3': 'D9A404', 'cloth4': 'AE8682',
         'cloak1': 'D8AC00', 'cloak2': 'A30708', 'accA1': 'D3CEC2', 'accA2': 'DA346E', 'accA3': 'A4C911',
         'accB1': 'C78407', 'accB2': '4155B6', 'accB3': 'C0D3D2', 'accB4': 'BA3B45', 'glasses1': '999999',
         'glasses2': 'CCBAD2', 'glasses3': '607E4B', 'body3': '4F413C', 'tail': 'E6D6BD', 'wing': 'A7D6D6'}
M_SLOT = ['skin', 'eyes', 'hair', 'hair2', 'mark', 'kemono', 'cloth1', 'cloth2', 'cloth3', 'cloth4', 'cloak1',
          'cloak2', 'accA1', 'accA2', 'accA3', 'accB1', 'accB2', 'accB3', 'accB4', 'glasses1', 'glasses2', 'glasses3']
# Back to front, per sheet. A part name matches files named <prefix>_<part>_pNN (TV/SV/TVD) or FG_<part>_pNN.
# On walk sprites the 1/2 halves split a part by facing (e.g. RearHair1 = back row, RearHair2 = the other rows), so
# both sit above the body - except Clothing1 next to a Clothing2, which holds cape flaps behind the body.
ORDER = {
    'TV': ['Wing1', 'Wing2', 'Tail1', 'Tail2', 'Clothing1:back', 'Body', 'Ears', 'FacialMark', 'Beard1', 'Beard2',
           'Clothing2', 'Clothing1', 'Cloak1', 'Cloak2', 'RearHair1', 'RearHair2', 'BeastEars', 'FrontHair1',
           'FrontHair2', 'Glasses', 'AccA', 'AccB'],
    'TVD': ['Wing', 'Tail', 'Body', 'Ears', 'FacialMark', 'Beard', 'Clothing', 'Cloak', 'RearHair', 'BeastEars',
            'FrontHair', 'Glasses', 'AccA', 'AccB'],
    'SV': ['Wing', 'Tail', 'Cloak2', 'Clothing1', 'body', 'Ears', 'FacialMark', 'Beard', 'Clothing2', 'Cloak1',
           'RearHair1', 'BeastEars', 'FrontHair', 'Glasses', 'AccA', 'AccB'],
    'Face': ['RearHair1', 'Cloak2', 'Body', 'Face', 'Ears', 'Eyes', 'Eyebrows', 'Nose', 'Mouth', 'FacialMark',
             'Beard', 'Clothing1', 'Clothing2', 'Cloak1', 'RearHair2', 'BeastEars', 'FrontHair', 'Glasses', 'AccA',
             'AccB'],
}
# Which recipe key picks the pattern number of each part.
PART_KEY = {'Body': 'body', 'body': 'body', 'Face': 'face', 'Ears': 'ears', 'Eyes': 'eyes', 'Eyebrows': 'eyebrows',
            'Nose': 'nose', 'Mouth': 'mouth', 'FacialMark': 'mark', 'Beard': 'beard', 'Beard1': 'beard',
            'Beard2': 'beard', 'Clothing': 'cloth', 'Clothing1': 'cloth', 'Clothing2': 'cloth', 'Cloak': 'cloak',
            'Cloak1': 'cloak', 'Cloak2': 'cloak', 'RearHair': 'rearHair', 'RearHair1': 'rearHair',
            'RearHair2': 'rearHair', 'FrontHair': 'frontHair', 'FrontHair1': 'frontHair', 'FrontHair2': 'frontHair',
            'BeastEars': 'kemono', 'Glasses': 'glasses', 'AccA': 'accA', 'AccB': 'accB', 'Wing': 'wing',
            'Wing1': 'wing', 'Wing2': 'wing', 'Tail': 'tail', 'Tail1': 'tail', 'Tail2': 'tail'}

# Recipes: pattern numbers as in the editor's Character Generator (p01 = 1), colours as gradient rows.
RECIPES = {
    # Ryuzetsu Homura, Yuki's older brother (Story Bible: Masa Lalu Yuki). Yuki's blonde (the default row) and gold
    # eyes, side-swept bangs like hers, a samurai topknot, black brows; a dark high-collared jacket and a flame-red
    # scarf (the scarf cloak). faces = the 8 slots of img/faces/Homura.png.
    'Homura': {'sex': 'Male', 'body': 1, 'face': 1, 'ears': 1, 'eyes': 2, 'eyebrows': 5, 'nose': 1, 'mouth': 3,
               'frontHair': 6, 'rearHair': 14, 'cloth': 16, 'cloak': 4,
               'colors': {'eyes': 55, 'brows': 69, 'cloth1': 18, 'cloth2': 69, 'cloth3': 11, 'cloth4': 69,
                          'cloak1': 28, 'cloak2': 28},
               'faces': [{},                                              # 0 calm
                         {'mouth': 4},                                    # 1 smirk
                         {'eyes': 17, 'mouth': 10},                       # 2 cold
                         {'eyes': 15, 'eyebrows': 8, 'mouth': 15},        # 3 angry
                         {'eyes': 15, 'eyebrows': 8, 'mouth': 11},        # 4 shouting
                         {'eyes': 19, 'mouth': 9},                        # 5 Mumeito's grin
                         {'eyes': 13, 'eyebrows': 17, 'mouth': 15},       # 6 hurt
                         {'hood': {'color': 69, 'rearHair': 12}}]},                     # 7 hooded, before the reveal
}
# Homura before the reveal: the hood up, the topknot under it.
RECIPES['Homura_Hood'] = dict(RECIPES['Homura'], hood={'color': 69, 'rearHair': 12}, sheets=('TV', 'SV'))


def _gradients():
    a = np.array(Image.open(GEN + 'gradients.png').convert('RGB')).astype(np.float32)
    return a[1::4]                                  # 70 rows of 256 colours, 4px each


def _lightness(rgb):
    return (rgb.max(-1) + rgb.min(-1)) / 2.0


def recolor(rgba, sel, row):
    """Recolours the pixels in sel onto one gradient row by lightness (white -> left end, black -> right end)."""
    rgb = rgba[..., :3].astype(np.float32)
    x = np.clip(0.85 * (255 - _lightness(rgb)) + 15, 0, 255).astype(int)
    out = rgba.copy()
    out[..., :3][sel] = row[x[sel]].astype(np.uint8)
    return out


def _files(folder, prefix, part, num):
    d = GEN + folder + '/'
    pat = re.compile(r'^%s_%s_p%02d(_c\d(_m\d+)?)?\.png$' % (prefix, part, num))
    return sorted(f for f in os.listdir(d) if pat.match(f) and not f.endswith('_c.png'))


_SV_SLOTS = {}


def _sv_slot_colors(sex, part, num):
    """Mean default colour of every slot of the matching battler part (Clothing2 p05 -> SV_Clothing*_p05)."""
    k = (sex, re.sub(r'\d$', '', part), num)
    if k not in _SV_SLOTS:
        d, acc = GEN + 'SV/' + sex + '/', {}
        for f in os.listdir(d):
            if not re.match(r'^SV_%s\d?_p%02d\.png$' % (k[1], num), f, re.I): continue
            img = np.array(Image.open(d + f).convert('RGBA')).astype(np.float32)
            mask = np.array(Image.open(d + f[:-4] + '_c.png').convert('RGB'))
            for slot, hexkey in SLOTS.items():
                key = np.array([int(hexkey[i:i + 2], 16) for i in (0, 2, 4)])
                sel = (mask == key).all(-1) & (img[..., 3] > 0) & (img[..., :3].max(-1) > 40)  # skip outlines
                if sel.any(): acc.setdefault(slot, []).append(img[..., :3][sel])
        _SV_SLOTS[k] = {s: np.concatenate(v).mean(0) for s, v in acc.items()}
    return _SV_SLOTS[k]


def _face_slot(img, m, sex, part, num):
    """Face parts name their slot with an m-number, but clothing and accessories number theirs per pattern, so
    those are matched to the battler part's slot with the closest default colour."""
    slot = M_SLOT[m - 1] if m <= len(M_SLOT) else None
    if not re.match(r'Clothing|AccA|AccB|Cloak', part): return slot
    cand = _sv_slot_colors(sex, part, num)
    px = img[..., :3][(img[..., 3] > 0) & (img[..., :3].max(-1) > 40)].astype(np.float32)
    if not cand or not len(px): return slot
    mean = px.mean(0)
    return min(cand, key=lambda s: ((cand[s] - mean) ** 2).sum())


def layer(kind, sex, part, num, colors, grads):
    """One part as an RGBA array, recoloured. kind: TV, TVD, SV or Face."""
    folder, prefix = (('Face/' + sex, 'FG') if kind == 'Face' else (kind + '/' + sex, kind))
    out = None
    files = _files(folder, prefix, part, num)
    if kind == 'Face':
        files.sort(key=lambda f: -int(re.search(r'_c(\d)', f).group(1)) if '_c' in f else 0)  # c1 on top
    for f in files:
        img = np.array(Image.open(GEN + folder + '/' + f).convert('RGBA'))
        if kind == 'Face':
            m = re.search(r'_m(\d+)', f)
            slot = _face_slot(img, int(m.group(1)), sex, part, num) if m else None
            if part == 'Eyebrows' and slot == 'hair' and 'brows' in colors:
                slot = 'brows'                     # brows can be their own colour instead of the hair's
            if slot in colors:
                img = recolor(img, img[..., 3] > 0, grads[colors[slot]])
        else:
            mask = np.array(Image.open(GEN + folder + '/' + f[:-4] + '_c.png').convert('RGB'))
            for slot, row in colors.items():
                if slot not in SLOTS: continue
                key = np.array([int(SLOTS[slot][i:i + 2], 16) for i in (0, 2, 4)])
                sel = (mask == key).all(-1) & (img[..., 3] > 0)
                if sel.any(): img = recolor(img, sel, grads[row])
        if out is None:
            out = img
        else:
            o = Image.fromarray(out); o.alpha_composite(Image.fromarray(img)); out = np.array(o)
    return out


def build(recipe, kind):
    grads, sex, colors = _gradients(), recipe['sex'], recipe.get('colors', {})
    if recipe.get('hood'):
        h = recipe['hood']
        bare = build(dict(recipe, hood=None, rearHair=None, frontHair=None), kind)
        shape = build({'sex': sex, 'rearHair': h.get('rearHair', 1), 'frontHair': recipe.get('frontHair')}, kind)
        return hood(bare, shape, kind, grads[h['color']])
    canvas = None
    for part in ORDER[kind]:
        part, back = part.split(':')[0], part.endswith(':back')
        num = recipe.get(PART_KEY[part])
        if not num: continue
        if kind == 'TV' and part == 'Clothing1' and back != bool(_files('TV/' + sex, 'TV', 'Clothing2', num)): continue
        img = layer(kind, sex, part, num, colors, grads)
        if img is None: continue
        if canvas is None: canvas = Image.new('RGBA', (img.shape[1], img.shape[0]))
        canvas.alpha_composite(Image.fromarray(img))
    return canvas


def hood(bare, shape, kind, row):
    """Pulls a cloth hood over the head: the hair's silhouette, rounded and a little bigger, shaded with one gradient
    row and outlined, plus a shadow under its rim that hides the eyes."""
    face = kind == 'Face'
    grow, soft, shade = (9, 3.0, 12) if face else (3, 0.7, 2)
    a = shape.split()[3].point(lambda v: 255 if v else 0)
    a = a.filter(ImageFilter.MaxFilter(grow)).filter(ImageFilter.MinFilter(grow))       # close gaps between spikes
    a = a.filter(ImageFilter.MaxFilter(grow if face else 3))                              # a little thicker than hair
    a = a.filter(ImageFilter.GaussianBlur(soft)).point(lambda v: 255 if v > 110 else 0)  # round the spikes off
    mask = np.array(a) > 0
    # Cloth shading: light grows with the distance from the hood's edge (a rounded, padded look) and from above.
    depth, m, steps = np.zeros(mask.shape, np.float32), a, (14 if face else 3)
    for _ in range(steps):
        m = m.filter(ImageFilter.MinFilter(3)); depth += np.array(m) > 0
    yy = np.arange(mask.shape[0], dtype=np.float32)[:, None] % (144 if face else 48 if kind == 'TV' else 64)
    t = 0.75 * depth / steps + 0.25 * (1 - yy / yy.max())
    if not face: t = np.round(t * 3) / 3                                                  # few flat tones, pixel-art
    x = np.clip(215 - t * 150, 0, 255).astype(int)
    edge = mask & ~(np.array(a.filter(ImageFilter.MinFilter(3))) > 0)
    x[edge] = 250
    out = np.array(bare).copy()
    # The folded rim of the opening: hood pixels right above the uncovered face get a lighter seam.
    lip, below = np.zeros_like(mask), ~mask & (out[..., 3] > 0)
    for dy in range(1, 5 if face else 2): lip[:-dy] |= below[dy:]
    lip &= mask & ~edge
    x[lip] = 95
    under = np.zeros_like(mask)
    for dy in range(1, shade + 1): under[dy:] |= mask[:-dy]
    under &= ~mask & (out[..., 3] > 0)
    out[..., :3][under] = (out[..., :3][under] * 0.42).astype(np.uint8)
    out[..., :3][mask] = row[x[mask]].astype(np.uint8)
    out[..., 3][mask] = 255
    return Image.fromarray(out)


def sheets(recipe):
    s = {k: build(recipe, k) for k in recipe.get('sheets', ('TV', 'TVD', 'SV'))}
    s['Faces'] = [build(dict(recipe, **f), 'Face') for f in recipe.get('faces', [{}])] if 'TVD' in s else []
    return s


def save(name, s):
    out = {PROJ + 'img/characters/$%s.png' % name: s['TV'], PROJ + 'img/sv_actors/%s.png' % name: s['SV']}
    if 'TVD' in s:
        down = Image.new('RGBA', (144, 192))           # the one damage row, repeated for every facing
        for y in range(4): down.paste(s['TVD'], (0, y * 48))
        out[PROJ + 'img/characters/$%s_Down.png' % name] = down
    if s['Faces']:
        face = Image.new('RGBA', (576, 288))
        for i, f in enumerate(s['Faces']): face.paste(f, (i % 4 * 144, i // 4 * 144))
        out[PROJ + 'img/faces/%s.png' % name] = face
    for path, img in out.items():
        img.save(path); print('wrote', path.replace(PROJ, ''))


def preview(name, s, scale=2):
    tv, tvd, sv, fgs = s['TV'], s.get('TVD'), s['SV'], s['Faces']
    W = max(tv.width * scale + 4 * 148 + 24, sv.width) + 16
    H = max(tv.height * scale, 2 * 148) + 16 + (tvd.height * scale + 16 if tvd else 0) + sv.height + 16
    c = Image.new('RGBA', (W, H), (236, 236, 240, 255))
    c.alpha_composite(tv.resize((tv.width * scale, tv.height * scale), Image.NEAREST), (8, 8))
    for i, f in enumerate(fgs): c.alpha_composite(f, (tv.width * scale + 24 + i % 4 * 148, 8 + i // 4 * 148))
    y = max(tv.height * scale, 2 * 148) + 24
    if tvd:
        c.alpha_composite(tvd.resize((tvd.width * scale, tvd.height * scale), Image.NEAREST), (8, y))
        y += tvd.height * scale + 16
    c.alpha_composite(sv, (8, y))
    os.makedirs(PREVIEWS, exist_ok=True)
    path = PREVIEWS + 'char_%s.png' % name
    c.save(path); print('preview', path)
    return path


if __name__ == '__main__':
    args = sys.argv[1:]
    if not GEN: sys.exit('RPG Maker MV Generator folder not found.')
    for name in [a for a in args if not a.startswith('--')] or list(RECIPES):
        s = sheets(RECIPES[name])
        preview(name, s)
        if '--preview' not in args: save(name, s)
