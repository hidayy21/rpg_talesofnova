# Character Generator without RPG Maker: faces, walking sprites, side-view battlers and damage strips from the
# Generator's parts, built the way the editor builds them (layer order, mask table and palette groups as in RPG Maker
# MV's own generator code), plus extra part packs and editing finished faces.
#
# Parts come from RPG Maker MV's Generator folder and from everything in Project Nova_tools/generator_parts/ -
# folders, .zip and .rar (a .rar is unpacked next to itself once, with the system's tar), in any of these layouts:
#   <Pack>/Face|TV|SV|TVD|Variation/Male|Female|Kid/<generator file names>     (the editor's own layout)
#   <Pack>/Face|TV|SV|TVD|Variation/<files>    <Pack>/<files>    <Collection>/<Pack>/<files>
# A pack is the folder the files are in, less the Face/TV/.../Male/Female parts of the path; its variations are
# "<Pack>/p20" (the editor's own are "p06"), so two packs that both number a part 20 do not clash. Without a
# Male/Female/Kid folder, a pack is for the sex its name says, or for both Male and Female.
#
# A character (recipe) = {'sex': 'Male'|'Female'|'Kid', 'parts': {group: variation or None}, 'colors': {mask: row}}
#   groups: face frontHair rearHair beard ears eyes eyebrows nose mouth tattoo kemono tail wing cloth cloak
#           accessoryA accessoryB glasses body;  mask: the generator's mask colour ('F9C19D' skin ...);
#   row: a gradients.png row (0-69), one of Nova's extra gradients (70 on, EXTRA), or '#rrggbb' for a gradient made
#   from any colour; -1 (or missing) = the part's own colours.
#
#   python chargen.py parts Female           -> the parts found
#   python chargen.py fit family1 0 Female   -> the recipe of a generator face (and how close it comes)
import io, json, os, re, shutil, sys, zipfile
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.join(HERE, '..')
GEN = os.environ.get('NOVA_GENERATOR') or next((p for p in (
    os.path.expanduser('~/Library/Application Support/Steam/steamapps/common/RPG Maker MV/RPG Maker MV.app/Contents/MacOS/Generator'),
    'C:/Program Files (x86)/Steam/steamapps/common/RPG Maker MV/Generator',
    'C:/Program Files/Steam/steamapps/common/RPG Maker MV/Generator') if os.path.isdir(p)), None)
PACKS = os.path.join(HERE, 'generator_parts')
SEXES = ('Male', 'Female', 'Kid')
KINDS = ('Face', 'TV', 'SV', 'TVD')
SIZE = {'Face': (144, 144), 'TV': (144, 192), 'SV': (576, 384), 'TVD': (144, 48)}

# ---------------------------------------------------------------- the editor's own tables (CharacterGeneratorData)
# layers back to front: (layer, group). Male and Female are the same; Kid swaps ears/kemono on TV, TVD and SV.
_FACE = [('rearhair2', 'rearHair'), ('cloak2', 'cloak'), ('body', 'body'), ('cloth2', 'cloth'), ('face', 'face'),
         ('mouth', 'mouth'), ('nose', 'nose'), ('tattoo', 'tattoo'), ('eyes', 'eyes'), ('eyebrows', 'eyebrows'),
         ('rearhair1', 'rearHair'), ('ears', 'ears'), ('cloth1', 'cloth'), ('beard', 'beard'), ('kemono', 'kemono'),
         ('acca', 'accessoryA'), ('cloak1', 'cloak'), ('fronthair', 'frontHair'), ('glasses', 'glasses'),
         ('accb', 'accessoryB')]
_TV = [('wing2', 'wing'), ('cloak2', 'cloak'), ('tail2', 'tail'), ('fronthair2', 'frontHair'), ('beard2', 'beard'),
       ('body', 'body'), ('tattoo', 'tattoo'), ('rearhair2', 'rearHair'), ('cloth2', 'cloth'), ('beard1', 'beard'),
       ('cloth1', 'cloth'), ('tail1', 'tail'), ('cloak1', 'cloak'), ('kemono', 'kemono'), ('ears', 'ears'),
       ('glasses', 'glasses'), ('rearhair1', 'rearHair'), ('acca', 'accessoryA'), ('fronthair1', 'frontHair'),
       ('accb', 'accessoryB'), ('wing1', 'wing')]
_TVD = [('body', 'body'), ('tattoo', 'tattoo'), ('cloth', 'cloth'), ('beard', 'beard'), ('tail', 'tail'),
        ('cloak', 'cloak'), ('glasses', 'glasses'), ('wing', 'wing'), ('rearhair', 'rearHair'), ('kemono', 'kemono'),
        ('ears', 'ears'), ('acca', 'accessoryA'), ('fronthair', 'frontHair'), ('accb', 'accessoryB')]
_SV = [('wing', 'wing'), ('cloak2', 'cloak'), ('tail', 'tail'), ('body', 'body'), ('tattoo', 'tattoo'),
       ('rearhair1', 'rearHair'), ('cloth2', 'cloth'), ('beard', 'beard'), ('cloth1', 'cloth'), ('cloak1', 'cloak'),
       ('kemono', 'kemono'), ('ears', 'ears'), ('glasses', 'glasses'), ('acca', 'accessoryA'),
       ('fronthair', 'frontHair'), ('accb', 'accessoryB')]


def _kid(order):
    out = list(order)
    i, j = out.index(('kemono', 'kemono')), out.index(('ears', 'ears'))
    out[i], out[j] = out[j], out[i]
    return out


LAYERS = {'Face': _FACE, 'TV': _TV, 'SV': _SV, 'TVD': _TVD}
LAYERS_KID = {'Face': _FACE, 'TV': _kid(_TV), 'SV': _kid(_SV), 'TVD': _kid(_TVD)}
# the groups as the editor lists them: (group, label, may be left out, picture for its thumbnails)
GROUPS = [('face', 'Face', False, 'Face'), ('frontHair', 'Front Hair', True, 'SV'), ('rearHair', 'Rear Hair', True, 'SV'),
          ('beard', 'Beard', True, 'SV'), ('ears', 'Ears', False, 'SV'), ('eyes', 'Eyes', False, 'Face'),
          ('eyebrows', 'Eyebrows', False, 'Face'), ('nose', 'Nose', False, 'Face'), ('mouth', 'Mouth', False, 'Face'),
          ('tattoo', 'Facial Mark', True, 'SV'), ('kemono', 'Beast Ears', True, 'SV'), ('tail', 'Tail', True, 'SV'),
          ('wing', 'Wing', True, 'SV'), ('cloth', 'Clothing', True, 'SV'), ('cloak', 'Cloak', True, 'SV'),
          ('accessoryA', 'Accessory A', True, 'SV'), ('accessoryB', 'Accessory B', True, 'SV'),
          ('glasses', 'Glasses', True, 'SV')]
MASKS = {'m001': 'F9C19D', 'm002': '2C80CB', 'm003': 'FCCB0A', 'm004': 'B892C5', 'm005': '009296', 'm006': 'D3CEC7',
         'm007': 'AE8682', 'm008': 'FE9D1E', 'm009': '1C76D0', 'm010': 'D9A404', 'm011': 'D8AC00', 'm012': 'A30708',
         'm013': 'D3CEC2', 'm014': 'DA346E', 'm015': 'A4C911', 'm016': 'C78407', 'm017': 'C0D3D2', 'm018': '4155B6',
         'm019': 'BA3B45', 'm020': '999999', 'm021': 'CCBAD2', 'm022': '607E4B'}
# the colour boxes: (mask, label, groups that show it, gradient rows offered). Rows: hair 0-22, eyes 24-35,
# skin 36-44 (the editor's palette offsets 0, 1, 2); clothing and the rest may use any row.
HAIR, EYES, SKIN, ALL = range(0, 23), range(24, 36), range(36, 45), range(0, 70)
COLORS = [('F9C19D', 'Skin', ('face', 'ears', 'nose', 'mouth', 'body'), SKIN),
          ('FCCB0A', 'Hair', ('frontHair', 'rearHair', 'eyebrows', 'beard'), HAIR),
          ('B892C5', 'Hair (sub)', ('rearHair',), HAIR),
          ('2C80CB', 'Eyes', ('eyes',), EYES),
          ('009296', 'Facial Mark', ('tattoo',), ALL), ('D3CEC7', 'Beast Ears', ('kemono',), HAIR),
          ('E6D6BD', 'Tail', ('tail',), HAIR), ('A7D6D6', 'Wing', ('wing',), ALL),
          ('AE8682', 'Clothing', ('cloth',), ALL), ('FE9D1E', 'Clothing 2', ('cloth',), ALL),
          ('1C76D0', 'Clothing 3', ('cloth',), ALL), ('D9A404', 'Clothing 4', ('cloth',), ALL),
          ('D8AC00', 'Cloak', ('cloak',), ALL), ('A30708', 'Cloak lining', ('cloak',), ALL),
          ('D3CEC2', 'Accessory A', ('accessoryA',), ALL), ('DA346E', 'Accessory A 2', ('accessoryA',), ALL),
          ('A4C911', 'Accessory A 3', ('accessoryA',), ALL),
          ('C78407', 'Accessory B', ('accessoryB',), ALL), ('C0D3D2', 'Accessory B 2', ('accessoryB',), ALL),
          ('4155B6', 'Accessory B 3', ('accessoryB',), ALL), ('BA3B45', 'Accessory B 4', ('accessoryB',), ALL),
          ('999999', 'Glasses', ('glasses',), ALL), ('CCBAD2', 'Glasses 2', ('glasses',), ALL),
          ('607E4B', 'Glasses 3', ('glasses',), ALL)]
_RENAME = {'facialmark': 'tattoo', 'beastears': 'kemono', 'clothing': 'cloth'}


def layer_name(file_name):
    """'FG_Clothing2_p05_c1_m008' -> 'cloth2' (the editor's scanDirectory)."""
    m = re.match(r'^[^_]+_([^_]+)_', file_name)
    if not m: return None
    name = m.group(1).lower()
    base, num = re.match(r'^(\D+)(\d*)', name).groups()
    return _RENAME.get(base, base) + num


# ---------------------------------------------------------------- finding the parts (editor folder + packs)
class Source:
    """Reads files from a folder or a zip."""
    def __init__(self, root, pack=None, zip_path=None):
        self.root, self.pack, self.zip = root, pack, zipfile.ZipFile(zip_path) if zip_path else None

    def files(self):
        if self.zip: return [n for n in self.zip.namelist() if n.lower().endswith('.png')]
        out = []
        for d, _, fs in os.walk(self.root):
            out += [os.path.relpath(os.path.join(d, f), self.root).replace('\\', '/') for f in fs if f.lower().endswith('.png')]
        return out

    def open(self, rel):
        if self.zip: return Image.open(io.BytesIO(self.zip.read(rel)))
        return Image.open(os.path.join(self.root, rel))


def _unrar(path):
    """A .rar unpacked once into the folder next to it (Windows 10+ and macOS tar read RAR); the folder, or None."""
    out = path[:-4]
    if not os.path.isdir(out):
        import subprocess
        tar = os.path.join(os.environ.get('SystemRoot', 'C:/Windows'), 'System32', 'tar.exe') if os.name == 'nt' else 'tar'
        os.makedirs(out, exist_ok=True)
        try:
            subprocess.run([tar, '-xf', path, '-C', out], check=True, capture_output=True)
        except (OSError, subprocess.CalledProcessError):
            shutil.rmtree(out, ignore_errors=True)
            return None
        # a rar holding one folder of the same name: lift its contents up a level
        inner = os.path.join(out, os.path.basename(out))
        if os.path.isdir(inner) and os.listdir(out) == [os.path.basename(out)]:
            for e in os.listdir(inner): shutil.move(os.path.join(inner, e), out)
            os.rmdir(inner)
    return out


def sources():
    out = [Source(GEN)] if GEN else []
    if os.path.isdir(PACKS):
        names = sorted(os.listdir(PACKS))
        for e in names:
            full = os.path.join(PACKS, e)
            if e.lower().endswith('.rar') and e[:-4] not in names:
                full = _unrar(full)
                if full: out.append(Source(full, e[:-4]))
            elif os.path.isdir(full): out.append(Source(full, e))
            elif e.lower().endswith('.zip'): out.append(Source(None, e[:-4], full))
    return out


_index = None
skipped = []                    # pack files whose names are not the generator's (they are left out)


def index(refresh=False):
    """{sex: {kind: {layer: {variation: [(source, rel, mask or None)]}}}, plus 'icons': {sex: {group: {var: (src, rel)}}}}"""
    global _index
    if _index is not None and not refresh: return _index
    idx = {s: {k: {} for k in KINDS + ('Variation',)} for s in SEXES}
    del skipped[:]
    for src in sources():
        for rel in src.files():
            bits = rel.split('/')
            folders = bits[:-1]
            kind = next((b for b in folders if b in KINDS + ('Variation',)), None)
            stem = bits[-1][:-4]
            if not kind:            # a loose pack: the kind from the file name (FG_ / TV_ / SV_ / TVD_ / icon_)
                kind = {'FG': 'Face', 'TV': 'TV', 'SV': 'SV', 'TVD': 'TVD', 'icon': 'Variation'}.get(stem.split('_')[0])
            var = re.search(r'_([pq]\d+)', stem)
            name = layer_name(stem)
            if not (kind and var and name):
                if src.pack: skipped.append('%s/%s' % (src.pack, rel))
                continue
            pack = src.pack and '/'.join([src.pack] + [b for b in folders if b not in KINDS + ('Variation',) + SEXES])
            sex = next((b for b in folders if b in SEXES), None)
            if not sex and pack:
                hint = re.search(r'\b(female|male|kid)\b', pack, re.I)
                sex = hint and hint.group(1).capitalize()
            v = var.group(1) if not pack else '%s/%s' % (pack, var.group(1))
            for sex in ([sex] if sex else ['Male', 'Female']):
                _add(idx, sex, kind, name, v, src, rel, stem)
    # a pack's variation without an icon, numbered like one of the editor's own, is a fix for that one (Hiddenone's
    # damage sprite for the male rear hair 18) and replaces those pictures; with an icon it is a part of its own
    for sex in SEXES:
        icons = idx[sex]['Variation']
        for kind in KINDS:
            for layer, group in (LAYERS_KID if sex == 'Kid' else LAYERS)[kind]:
                found = idx[sex][kind].get(layer, {})
                own = {v for v in _vars(idx, sex, group) if '/' not in v}
                for v in [v for v in found if '/' in v]:
                    base = v.rsplit('/', 1)[1]
                    if base in own and v not in icons.get(group, {}):
                        found[base] = found.pop(v)
    _index = idx
    return idx


def _add(idx, sex, kind, name, v, src, rel, stem):
    if kind == 'Variation':
        base = re.sub(r'\d+$', '', name)
        group = {'acca': 'accessoryA', 'accb': 'accessoryB'}.get(base) or \
            next((g for g, *_ in GROUPS if g.lower() == base), None)
        if group: idx[sex]['Variation'].setdefault(group, {})[v] = (src, rel)
    elif kind != 'Face' and stem.endswith('_c'):
        idx[sex][kind].setdefault(name, {}).setdefault(v, {})['mask'] = (src, rel)
    elif kind == 'Face':
        m = re.search(r'(m\d{3})$', stem)
        idx[sex][kind].setdefault(name, {}).setdefault(v, []).append((src, rel, MASKS.get(m.group(1)) if m else None))
    else:
        idx[sex][kind].setdefault(name, {}).setdefault(v, {})['image'] = (src, rel)


def _vars(idx, sex, group):
    out = set()
    for kind in KINDS:
        for layer, g in (LAYERS_KID if sex == 'Kid' else LAYERS)[kind]:
            if g == group: out |= set(idx[sex][kind].get(layer, {}))
    return out


def variations(sex, group):
    """Every variation of a group, in the editor's order (its own first, then the packs)."""
    found = _vars(index(), sex, group)
    key = lambda v: (('/' in v), v.rsplit('/', 1)[0] if '/' in v else '', int(re.sub(r'\D', '', v.split('/')[-1])))
    return sorted(found, key=key)


# ---------------------------------------------------------------- drawing
_grad = None
_cache = {}


# Nova's extra gradients (rows 70 on), made from one colour each like RPG Maker's own rows: near white on the left,
# the colour a little left of the middle, black on the right. (name, colour)
EXTRA = [('Crimson', 'c8102e'), ('Scarlet', 'e03c31'), ('Coral', 'ff7f50'), ('Orange', 'f28c28'), ('Amber', 'ffbf00'),
         ('Gold', 'd4af37'), ('Lemon', 'f5e050'), ('Lime', '9acd32'), ('Emerald', '2e8b57'), ('Mint', '3eb489'),
         ('Teal', '008080'), ('Turquoise', '30d5c8'), ('Cyan', '00b7eb'), ('Sky', '4fa3e0'), ('Azure', '1e6fd9'),
         ('Navy', '1f2f6b'), ('Indigo', '4b2a8c'), ('Violet', '8f5bd6'), ('Purple', '6a0dad'), ('Magenta', 'c2185b'),
         ('Pink', 'ff69b4'), ('Rose', 'e8a0b4'), ('Lavender', 'b8a1e3'), ('Peach', 'ffcba4'), ('Sand', 'd8c39a'),
         ('Tan', 'c19a6b'), ('Brown', '7b4a2a'), ('Chocolate', '4e2a1e'), ('Olive', '708238'), ('Moss', '5a6b3a'),
         ('Forest', '2f4f2f'), ('Slate', '5f6f7f'), ('Steel', '7a8ea6'), ('Silver', 'c0c0c8'), ('Ash', '8a8a8a'),
         ('Charcoal', '3a3a40'), ('Midnight', '1b2233'), ('Wine', '722f37'), ('Rust', 'b7410e'), ('Plum', '7d3c6b'),
         ('Snow', 'eef0f6'), ('Platinum', 'e8dcc0'), ('Ginger', 'c25a2c'), ('Auburn', '8b3a2b'), ('Ice', 'bfe3f2'),
         ('Sea', '2e9e8f'), ('Blood', '8a0303'), ('Neon green', '39ff14'), ('Electric blue', '2f6bff'),
         ('Hot pink', 'ff1493'),
         # skins
         ('Porcelain', 'f6dccb'), ('Pale', 'f1c9b0'), ('Warm', 'e0ac8a'), ('Golden', 'c68863'), ('Olive skin', 'b88a62'),
         ('Brown skin', '8d5a3b'), ('Deep', '5c3a28'), ('Orc', '7d9a6a'), ('Fae blue', '8fb7e0'), ('Ghost', 'd8dde6'),
         ('Demon', 'b03a48')]
EXTRA_SKIN = range(70 + 50, 70 + len(EXTRA))


def make_gradient(hexc):
    """A 256-colour gradient row from one colour, shaped like the generator's rows."""
    c = np.array([int(hexc.lstrip('#')[i:i + 2], 16) for i in (0, 2, 4)], np.float64)
    white, black = np.array([255.0] * 3), np.zeros(3)
    stops = [(0, white * 0.94 + c * 0.06), (56, white * 0.45 + c * 0.55), (112, c), (176, c * 0.48),
             (228, c * 0.14), (255, black)]
    row = np.zeros((256, 3))
    for (x0, a), (x1, b) in zip(stops, stops[1:]):
        t = (np.arange(x0, x1 + 1) - x0) / (x1 - x0)
        row[x0:x1 + 1] = a + (b - a) * t[:, None]
    return np.clip(np.round(row), 0, 255).astype(np.uint8)


def gradients():
    global _grad
    if _grad is None:
        g = np.asarray(Image.open(os.path.join(GEN, 'gradients.png')).convert('RGB'), dtype=np.uint8)
        _grad = np.concatenate([g[0::4][:70], np.stack([make_gradient(h) for _, h in EXTRA])])
    return _grad                     # (70 + extra, 256, 3); RPG Maker's rows: the top line of every 4 px row


_custom = {}


def grad_row(row):
    """A row number, or '#rrggbb' for a gradient made from that colour."""
    if isinstance(row, str):
        if row not in _custom: _custom[row] = make_gradient(row)
        return _custom[row]
    return gradients()[row]


def recolors(row):
    return row is not None and row != -1 and row != ''


def _load(src, rel):
    key = (id(src), rel)
    if key not in _cache: _cache[key] = np.asarray(src.open(rel).convert('RGBA'), dtype=np.uint8)
    return _cache[key]


def _recolor(arr, row, where=None):
    """The editor's colouring: a pixel's brightness picks the colour from a gradient row (dark parts -> the right).
    Brightness and gradient line as RPG Maker computes them (checked pixel for pixel against its faces)."""
    out = arr.copy()
    rgb = arr[..., :3].astype(np.int32)
    lum = (rgb[..., 0] * 306 + rgb[..., 1] * 601 + rgb[..., 2] * 116) >> 10
    i = np.clip(255 - lum, 0, 255)
    sel = arr[..., 3] > 0 if where is None else where & (arr[..., 3] > 0)
    out[..., :3][sel] = grad_row(row)[i[sel]]
    return out


def _piece(src, rel, row):
    key = (id(src), rel, row)
    if key not in _cache: _cache[key] = _recolor(_load(src, rel), row)
    return _cache[key]


def _masked(img, mask, colors):
    key = (id(img[0]), img[1], id(mask[0]) if mask else None, mask and mask[1], tuple(sorted(colors.items())))
    if key in _cache: return _cache[key]
    arr = _load(*img)
    if not mask: return arr
    m = _load(*mask)
    out = arr
    for hexc, row in colors.items():
        if not recolors(row): continue
        rgb = tuple(int(hexc[i:i + 2], 16) for i in (0, 2, 4))
        where = (m[..., 3] > 0) & (m[..., 0] == rgb[0]) & (m[..., 1] == rgb[1]) & (m[..., 2] == rgb[2])
        if where.any(): out = _recolor(out, row, where)
    _cache[key] = out
    return out


def layers(char, kind):
    """The pictures of one character, back to front, as RGBA arrays."""
    sex, parts, colors = char['sex'], char.get('parts', {}), char.get('colors', {})
    idx, out = index()[sex][kind], []
    for layer, group in (LAYERS_KID if sex == 'Kid' else LAYERS)[kind]:
        v = parts.get(group)
        if not v or v not in idx.get(layer, {}): continue
        entry = idx[layer][v]
        if kind == 'Face':
            # the editor sorts a variation's pieces by name and draws them last first: _c1 ends up on top
            for src, rel, mask in sorted(entry, key=lambda e: e[1].split('/')[-1], reverse=True):
                row = colors.get(mask, -1) if mask else -1
                out.append(_piece(src, rel, row) if recolors(row) else _load(src, rel))
        elif 'image' in entry:
            out.append(_masked(entry['image'], entry.get('mask'), colors))
    return out


def _bmul(x, a):
    t = x * a
    return (t + (t >> 8) + 0x80) >> 8


_pre = {}


def _premul(arr, w, h):
    """A layer as Qt holds it: premultiplied colour and 255 - alpha (cached, the fit draws the same layers a lot)."""
    key = (id(arr), w, h)
    if key not in _pre:
        if arr.shape[:2] != (h, w):
            pad = np.zeros((h, w, 4), np.uint8)
            pad[:min(h, arr.shape[0]), :min(w, arr.shape[1])] = arr[:h, :w]
            arr = pad
        ys, xs = np.nonzero(arr[..., 3])
        if not len(ys): _pre[key] = None; return None
        box = (slice(ys.min(), ys.max() + 1), slice(xs.min(), xs.max() + 1))     # transparent pixels change nothing
        arr = arr[box]
        a = arr[..., 3:4].astype(np.int32)
        _pre[key] = (box, np.concatenate([_bmul(arr[..., :3].astype(np.int32), a), a], axis=2), 255 - a)
    return _pre[key]


def stack(arrays, size):
    """Layers drawn over each other the way Qt does it in the editor: 8-bit premultiplied colour, so the soft edges
    come out exactly like RPG Maker's own pictures."""
    w, h = size
    dst = np.zeros((h, w, 4), np.int32)
    for arr in arrays:
        p = _premul(arr, w, h)
        if p is None: continue
        box, src, rest = p
        dst[box] = src + _bmul(dst[box], rest)
    a = dst[..., 3:4]
    inv = 0x00ff00ff // np.maximum(a, 1)
    rgb = np.where(a == 255, dst[..., :3], np.where(a == 0, 0, (dst[..., :3] * inv + 0x8000) >> 16))
    return np.concatenate([rgb, a], axis=2).astype(np.uint8)


def compose(char, kind='Face'):
    return Image.fromarray(stack(layers(char, kind), SIZE[kind]), 'RGBA')


def icon(sex, group, v):
    """The editor's 64x64 thumbnail when the part has one, else None."""
    e = index()[sex]['Variation'].get(group, {}).get(v)
    return e and e[0].open(e[1]).convert('RGBA')


# ---------------------------------------------------------------- sheets in the project
SHEET = {'Face': ('img/faces', 4, (144, 144)), 'TV': ('img/characters', 4, (144, 192)),
         'TVD': ('img/characters', 4, (144, 48)), 'SV': ('img/sv_actors', 1, (576, 384))}


def read_cell(kind, name, i):
    folder, cols, (w, h) = SHEET[kind]
    im = Image.open(os.path.join(PROJ, folder, name + '.png')).convert('RGBA')
    return im.crop(((i % cols) * w, (i // cols) * h, (i % cols) * w + w, (i // cols) * h + h))


def write_cell(kind, name, i, img):
    """Puts img in cell i of a sheet (a new sheet is made at the editor's size); returns the path."""
    folder, cols, (w, h) = SHEET[kind]
    path = os.path.join(PROJ, folder, name + '.png')
    full = {'Face': (576, 288), 'TV': (576, 384), 'TVD': (576, 384), 'SV': (576, 384)}[kind]
    sheet = Image.open(path).convert('RGBA') if os.path.isfile(path) else Image.new('RGBA', full, (0, 0, 0, 0))
    x, y = (i % cols) * w, (i // cols) * h
    sheet.paste(Image.new('RGBA', (w, h), (0, 0, 0, 0)), (x, y))
    sheet.paste(img, (x, y))
    sheet.save(path)
    return path


# ---------------------------------------------------------------- reading a finished face back into a recipe
def _diff(a, b):
    """How far apart two RGBA pictures look: colour where either is drawn, weighted by coverage."""
    a, b = a.astype(np.int32), b.astype(np.int32)
    return int(np.abs(a[..., :3] * a[..., 3:] // 255 - b[..., :3] * b[..., 3:] // 255).sum() + np.abs(a[..., 3] - b[..., 3]).sum())


def _render(char):
    return np.asarray(compose(char, 'Face'), dtype=np.uint8)


def fit(target, sex, start=None, rounds=4, log=None):
    """The recipe whose face comes closest to target (a 144x144 RGBA image), by trying every part and colour in turn.
    Returns (recipe, pixels that differ)."""
    tgt = np.asarray(target.convert('RGBA'), dtype=np.uint8)
    char = start or {'sex': sex, 'parts': {}, 'colors': {}}
    char = {'sex': sex, 'parts': dict(char['parts']), 'colors': dict(char['colors'])}
    face_groups = [g for _, g in LAYERS['Face']]
    for g, _, blank, _ in GROUPS:
        if g in face_groups and not blank and not char['parts'].get(g):
            vs = variations(sex, g)
            if vs: char['parts'][g] = vs[0]
    if not char['parts'].get('body'): char['parts']['body'] = (variations(sex, 'body') or [None])[0]
    best = _diff(_render(char), tgt)
    for r in range(rounds):
        before = best
        for g in dict.fromkeys(face_groups):
            blank = next((b for gg, _, b, _ in GROUPS if gg == g), True)
            for v in ([None] if blank else []) + variations(sex, g):
                if v == char['parts'].get(g): continue
                trial = {**char, 'parts': {**char['parts'], g: v}}
                d = _diff(_render(trial), tgt)
                if d < best: best, char = d, trial
        used = set(_used_masks(char))
        for hexc, _, _, rows in COLORS:
            if hexc not in used: continue
            for row in [-1] + list(ALL):
                if row == char['colors'].get(hexc, -1): continue
                trial = {**char, 'colors': {**char['colors'], hexc: row}}
                d = _diff(_render(trial), tgt)
                if d < best: best, char = d, trial
        if log: log('round %d: %d' % (r + 1, best))
        if best == before or best == 0: break
    used = set(_used_masks(char))
    char['parts'] = {g: v for g, v in char['parts'].items() if v}
    char['colors'] = {m: row for m, row in char['colors'].items() if m in used and recolors(row)}
    out = _render(char)
    return char, int((np.abs(out.astype(int) - tgt.astype(int)).sum(axis=2) > 0).sum())


def _used_masks(char):
    idx = index()[char['sex']]['Face']
    for layer, group in LAYERS['Face']:
        v = char['parts'].get(group)
        for src, rel, mask in idx.get(layer, {}).get(v, []) if v else []:
            if mask: yield mask


def swap(original, old, new):
    """A finished face with some parts changed: where the original is exactly what the old recipe draws, the new
    recipe's pixels; anything else (touch-ups by hand, parts the fit missed) stays as it was."""
    o = np.asarray(original.convert('RGBA'), dtype=np.uint8)
    a, b = _render(old), _render(new)
    same = (o == a).all(axis=2)
    out = o.copy()
    out[same] = b[same]
    return Image.fromarray(out, 'RGBA'), int((~same).sum())


if __name__ == '__main__':
    assert GEN, 'RPG Maker MV Generator folder not found (set NOVA_GENERATOR)'
    if hasattr(sys.stdout, 'reconfigure'): sys.stdout.reconfigure(errors='replace')
    args = sys.argv[1:]
    if args[:1] == ['parts']:
        sex = args[1] if len(args) > 1 else 'Female'
        for g, label, *_ in GROUPS: print('%-12s %s' % (label, ' '.join(variations(sex, g))))
    elif args[:1] == ['fit']:
        name, i, sex = args[1], int(args[2]), args[3] if len(args) > 3 else 'Female'
        char, off = fit(read_cell('Face', name, i), sex, log=print)
        print(json.dumps(char))
        print('%d pixels differ' % off)
