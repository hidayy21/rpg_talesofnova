# The Character page of Nova Tools (/chargen): the HTTP side of chargen.py.
#   GET  /api/chargen/setup                     parts, colour boxes, gradient rows, sheets, saved characters
#   GET  /api/chargen/thumb?sex=&group=&v=      a part's 64x64 thumbnail
#   GET  /api/chargen/sheet?kind=&name=         a sheet from img/faces, img/characters or img/sv_actors
#   GET  /api/chargen/recipe?name=              a saved character
#   POST /api/chargen/render  {char, base?}     Face/TV/SV/TVD pictures (base: {sheet, i, old} edits a finished face)
#   POST /api/chargen/fit     {sheet, i, sex}   read a finished face back into a recipe
#   POST /api/chargen/save    {char, name, targets, base?}
# Saved characters are Project Nova_tools/characters/<name>.json; sheets are backed up to
# <project>_backups/chargen/<time>/ before they are written.
import base64, io, json, os, re, shutil, time
from urllib.parse import parse_qs
from PIL import Image
import chargen as G

RECIPES = os.path.join(G.HERE, 'characters')
_thumbs = {}


def _png(img):
    buf = io.BytesIO()
    img.save(buf, 'PNG')
    return buf.getvalue()


def _data_url(img):
    return 'data:image/png;base64,' + base64.b64encode(_png(img)).decode('ascii')


def _safe(name):
    return re.sub(r'[^A-Za-z0-9_\- ]+', '', name or '').strip()


def default_char(sex):
    parts = {}
    for g in ('face', 'ears', 'eyes', 'eyebrows', 'nose', 'mouth', 'body', 'frontHair', 'rearHair', 'cloth'):
        vs = G.variations(sex, g)
        if vs: parts[g] = vs[0]
    return {'sex': sex, 'parts': parts, 'colors': {}}


def sheets():
    out = {}
    for kind, (folder, _, _) in G.SHEET.items():
        d = os.path.join(G.PROJ, folder)
        names = sorted(f[:-4] for f in os.listdir(d) if f.endswith('.png')) if os.path.isdir(d) else []
        if kind == 'TVD': names = [n for n in names if re.search(r'damage', n, re.I)]
        if kind == 'TV': names = [n for n in names if not n.startswith(('!', '$')) and not re.search(r'damage', n, re.I)]
        out[kind] = names
    return out


def setup():
    G.index(refresh=True)
    _thumbs.clear()
    grad = G.gradients()
    rows = [['#%02x%02x%02x' % tuple(grad[r][x]) for x in (0, 48, 96, 144, 192, 240)] for r in range(len(grad))]
    recipes = sorted(f[:-5] for f in os.listdir(RECIPES) if f.endswith('.json')) if os.path.isdir(RECIPES) else []
    face_groups = {g for _, g in G.LAYERS['Face']}
    packs = sorted({v.rsplit('/', 1)[0] for s in G.SEXES for g, *_ in G.GROUPS for v in G.variations(s, g)
                    if '/' in v and not (s == 'Kid' and v.split('/')[0] in G.BORROW)})   # not the adults' hair
    return {
        'ok': bool(G.GEN), 'generator': G.GEN, 'packs': packs, 'skipped': G.skipped,
        'extra': [{'row': 70 + i, 'name': n, 'skin': 70 + i in G.EXTRA_SKIN} for i, (n, _) in enumerate(G.EXTRA)],
        'groups': [{'id': g, 'label': label, 'blank': blank, 'face': g in face_groups} for g, label, blank, _ in G.GROUPS],
        'colors': [{'mask': m, 'label': label, 'groups': list(groups), 'rows': list(rows_)} for m, label, groups, rows_ in G.COLORS],
        'gradients': rows,
        'variations': {s: {g: G.variations(s, g) for g, *_ in G.GROUPS + [('body',)]} for s in G.SEXES},
        'defaults': {s: default_char(s) for s in G.SEXES},
        'sheets': sheets(), 'recipes': recipes}


def thumb(sex, group, v):
    key = (sex, group, v)
    if key not in _thumbs:
        img = G.icon(sex, group, v)
        if img is None:              # no icon in the pack: the part on a plain character
            char = default_char(sex)
            char['parts'][group] = v
            if group in {g for _, g in G.LAYERS['Face']}:
                img = G.compose(char, 'Face').crop((24, 8, 120, 104)).resize((64, 64), Image.LANCZOS)
            else:
                img = G.compose(char, 'SV').crop((0, 0, 64, 64))
        _thumbs[key] = _png(img)
    return _thumbs[key]


def sheet_png(kind, name):
    folder = G.SHEET[kind][0]
    path = os.path.join(G.PROJ, folder, os.path.basename(name) + '.png')
    return open(path, 'rb').read() if os.path.isfile(path) else None


def render(char, base=None):
    out = {}
    for kind in G.KINDS:
        if kind == 'Face' and base:
            img, kept = G.swap(G.read_cell('Face', base['sheet'], int(base['i'])), base['old'], char)
            out['kept'] = kept
        else:
            img = G.compose(char, kind)
        out[kind] = _data_url(img)
    return out


def fit(sheet, i, sex):
    char, off = G.fit(G.read_cell('Face', sheet, int(i)), sex)
    return {'char': char, 'off': off}


def save(char, name, targets, base=None):
    """targets: {'Face': {'sheet', 'i'}, 'TV': {...}, 'TVD': {...}, 'SV': {'sheet'}} (missing or null = not written)."""
    name = _safe(name)
    if not name: raise ValueError('Beri nama karakter dulu.')
    proj = os.path.abspath(G.PROJ)
    backup = os.path.join(os.path.dirname(proj), os.path.basename(proj) + '_backups', 'chargen', time.strftime('%Y%m%d_%H%M%S'))
    written = []
    for kind in G.KINDS:
        t = (targets or {}).get(kind)
        if not t or not _safe(t.get('sheet')): continue
        sheet = _safe(t['sheet'])
        i = 0 if kind == 'SV' else int(t.get('i', 0))
        if not 0 <= i < (1 if kind == 'SV' else 8 if kind != 'TVD' else 32): raise ValueError('Slot %s tidak valid.' % kind)
        folder = G.SHEET[kind][0]
        path = os.path.join(G.PROJ, folder, sheet + '.png')
        if os.path.isfile(path):
            os.makedirs(os.path.join(backup, folder), exist_ok=True)
            shutil.copy2(path, os.path.join(backup, folder))
        if kind == 'Face' and base:
            img, _ = G.swap(G.read_cell('Face', base['sheet'], int(base['i'])), base['old'], char)
        else:
            img = G.compose(char, kind)
        G.write_cell(kind, sheet, i, img)
        written.append('%s/%s.png%s' % (folder, sheet, '' if kind == 'SV' else ' #%d' % i))
    os.makedirs(RECIPES, exist_ok=True)
    with open(os.path.join(RECIPES, name + '.json'), 'w', encoding='utf8') as f:
        json.dump({'name': name, **char, 'targets': targets}, f, ensure_ascii=False, indent=1)
    return {'written': written, 'recipe': 'Project Nova_tools/characters/%s.json' % name,
            'backup': backup if os.path.isdir(backup) else None}


def recipe(name):
    path = os.path.join(RECIPES, _safe(name) + '.json')
    return json.load(open(path, encoding='utf8')) if os.path.isfile(path) else None


def handle_get(path, query):
    """(code, body, content type) for the Character page's GET requests, None when the path is not one of them."""
    if not path.startswith('/api/chargen/'): return None
    q = {k: v[0] for k, v in parse_qs(query).items()}
    if not G.GEN: return 500, {'error': 'Folder Generator RPG Maker MV tidak ditemukan (atur NOVA_GENERATOR).'}, None
    if path == '/api/chargen/setup': return 200, setup(), None
    if path == '/api/chargen/thumb':
        return 200, thumb(q.get('sex', 'Female'), q.get('group', ''), q.get('v', '')), 'image/png'
    if path == '/api/chargen/sheet':
        data = q.get('kind') in G.SHEET and sheet_png(q['kind'], q.get('name', ''))
        return (200, data, 'image/png') if data else (404, {'error': 'not found'}, None)
    if path == '/api/chargen/recipe':
        r = recipe(q.get('name', ''))
        return (200, r, None) if r else (404, {'error': 'not found'}, None)
    return 404, {'error': 'not found'}, None


def handle_post(path, body):
    if not path.startswith('/api/chargen/'): return None
    try:
        if path == '/api/chargen/render': return 200, render(body['char'], body.get('base')), None
        if path == '/api/chargen/fit': return 200, fit(body['sheet'], body['i'], body['sex']), None
        if path == '/api/chargen/save':
            return 200, save(body['char'], body.get('name'), body.get('targets'), body.get('base')), None
    except (ValueError, KeyError, OSError) as e:
        return 400, {'error': str(e)}, None
    return 404, {'error': 'not found'}, None
