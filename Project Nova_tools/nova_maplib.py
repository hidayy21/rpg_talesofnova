# Map-building library for Project Nova (RPG Maker MV).
#
#  - MapBuilder: paint terrain by autotile *kind* (A1-A4) or fixed tile (A5/B-E); autotile shapes are
#    resolved with the engine's own tables (parsed from js/rpg_core.js), so maps look as if drawn in the editor.
#  - Events: NPCs, doors with transfers, edge exits, shop counters, signs, chests.
#  - render(): a Python preview renderer (same drawing rules as Tilemap) incl. event graphics.
#  - save(): writes MapXXX.json and registers it in MapInfos.json.
import json, os, re
from PIL import Image, ImageDraw

# the game folder holds this tools folder, or sits next to it ('rpg_talesofnova' on the Mac, 'Project Nova' on Windows)
_HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.environ.get('NOVA_PROJ') or next(p for p in [os.path.join(_HERE, '..')] + [os.path.join(_HERE, '..', n) for n in ('rpg_talesofnova', 'Project Nova')]
                                            if os.path.isfile(os.path.join(p, 'Game.rpgproject'))).replace('\\', '/') + '/'
DATA = PROJ + 'data/'

A1, A2, A3, A4, A5 = 2048, 2816, 4352, 5888, 1536
B, C, D, E = 0, 256, 512, 768

# ---------------------------------------------------------------- extra sheets (NovaTilesetEx plugin)
# Any map can use object tiles from every sheet listed in the plugin: id = 20000 + slot * 1000 + n.
EXT_BASE, EXT_SPAN = 20000, 1000
_EXT = None


def ext_sheets():
    """{slot: (sheet name, flags tileset id or 0)} from NovaTilesetEx's "Extra Sheets" in js/plugins.js."""
    global _EXT
    if _EXT is None:
        plugins = json.loads(re.search(r'var \$plugins =\s*(\[.*\]);', open(PROJ + 'js/plugins.js', encoding='utf8').read(), re.S).group(1))
        entry = next((p for p in plugins if p['name'] == 'NovaTilesetEx' and p['status']), None)
        text = json.loads(entry['parameters']['Extra Sheets']) if entry else ''
        _EXT = {}
        for line in text.splitlines():
            m = re.match(r'\s*(\d+)\s*:\s*([^@]+?)\s*(?:@\s*(\d+))?\s*$', line)
            if m: _EXT[int(m.group(1))] = (m.group(2), int(m.group(3) or 0))
    return _EXT


def ext(sheet, n):
    """Tile id of tile n (RPG Maker numbering) on any registered sheet, usable on every map: ext('Inside_B', 49)."""
    for slot, (name, _) in ext_sheets().items():
        if name == sheet: return EXT_BASE + slot * EXT_SPAN + n
    raise KeyError('%s is not in NovaTilesetEx "Extra Sheets" (js/plugins.js)' % sheet)


def tileset_flags(tileset_id):
    """The tileset's flags extended with the extra sheets, indexed by tile id (same rules as the plugin)."""
    tilesets = json.load(open(DATA + 'Tilesets.json', encoding='utf8'))
    flags = list(tilesets[tileset_id]['flags'])
    sheets = ext_sheets()
    if sheets: flags += [0] * (EXT_BASE + (max(sheets) + 1) * EXT_SPAN - len(flags))
    for slot, (name, src_id) in sheets.items():
        for ts in ([tilesets[src_id]] if src_id else tilesets):
            if not ts: continue
            s = next((i for i in range(4, 9) if ts['tilesetNames'][i] == name), None)
            if s is None: continue
            first, count = (A5, 128) if s == 4 else ((s - 5) * 256, 256)
            for n in range(count): flags[EXT_BASE + slot * EXT_SPAN + n] = ts['flags'][first + n]
            break
    return flags

_core = open(PROJ + 'js/rpg_core.js', encoding='utf8').read()
def _table(name):
    return json.loads(re.search(r'Tilemap\.' + name + r' = (\[.*?\]);', _core, re.S).group(1))
FLOOR, WALL, WATERFALL = _table('FLOOR_AUTOTILE_TABLE'), _table('WALL_AUTOTILE_TABLE'), _table('WATERFALL_AUTOTILE_TABLE')

# Quarter vocabulary (TL, TR, BL, BR) for each neighbour situation.
_FQ = [{'in': [2, 4], 'corner': [2, 0], 'side': [0, 4], 'tb': [2, 2], 'out': [0, 2]},
       {'in': [1, 4], 'corner': [3, 0], 'side': [3, 4], 'tb': [1, 2], 'out': [3, 2]},
       {'in': [2, 3], 'corner': [2, 1], 'side': [0, 3], 'tb': [2, 5], 'out': [0, 5]},
       {'in': [1, 3], 'corner': [3, 1], 'side': [3, 3], 'tb': [1, 5], 'out': [3, 5]}]
_WQ = [{'in': [2, 2], 'side': [0, 2], 'tb': [2, 0], 'out': [0, 0]},
       {'in': [1, 2], 'side': [3, 2], 'tb': [1, 0], 'out': [3, 0]},
       {'in': [2, 1], 'side': [0, 1], 'tb': [2, 3], 'out': [0, 3]},
       {'in': [1, 1], 'side': [3, 1], 'tb': [1, 3], 'out': [3, 3]}]
_QN = [((0, -1), (-1, 0), (-1, -1)), ((0, -1), (1, 0), (1, -1)), ((0, 1), (-1, 0), (-1, 1)), ((0, 1), (1, 0), (1, 1))]
_ISOLATED = [[0, 0], [1, 0], [0, 1], [1, 1]]


def _shape(same, x, y, floor):
    qs = _FQ if floor else _WQ
    st = []
    for q in range(4):
        (vx, vy), (hx, hy), (dx, dy) = _QN[q]
        v, h = same(x + vx, y + vy), same(x + hx, y + hy)
        if v and h: st.append('in' if (not floor or same(x + dx, y + dy)) else 'corner')
        elif v: st.append('side')
        elif h: st.append('tb')
        else: st.append('out')
    want = _ISOLATED if (floor and st == ['out'] * 4) else [qs[q][s] for q, s in enumerate(st)]
    tab = FLOOR if floor else WALL
    return tab.index(want)


def is_wall_kind(sheet, kind):
    """A3 (roofs and walls) and A4 wall *sides* use the wall table; A1/A2/A4-tops use the floor table."""
    if sheet == 'A3': return True
    if sheet == 'A4': return (kind % 16) >= 8
    return False


BASE = {'A1': A1, 'A2': A2, 'A3': A3, 'A4': A4}


def _kind_of(v):
    """A raw ('ID', tile) autotile still counts as its kind for its neighbours' shapes."""
    if v and v[0] == 'ID' and v[1] >= A1:
        for sheet, base in (('A4', A4), ('A3', A3), ('A2', A2), ('A1', A1)):
            if v[1] >= base: return (sheet, (v[1] - base) // 48)
    return v


class MapBuilder:
    def __init__(self, w, h, tileset_id, name, display=''):
        self.w, self.h, self.tileset_id, self.name, self.display = w, h, tileset_id, name, display
        self.auto = [[[None] * w for _ in range(h)] for _ in range(2)]   # layers 0/1: ('A2', kind) | ('A5', idx)
        self.top = [[[0] * w for _ in range(h)] for _ in range(2)]       # layers 2/3: B-E tile ids
        self.shadow = [[0] * w for _ in range(h)]
        self.events = [None]
        self.bgm = {'name': '', 'pan': 0, 'pitch': 100, 'volume': 90}
        self.bgs = None
        self.note = ''
        self.parallax = ''
        self.no_auto_shadow = set()

    # ---------------------------------------------------------------- painting
    def inb(self, x, y): return 0 <= x < self.w and 0 <= y < self.h

    def rect(self, x0, y0, x1, y1, val, layer=0):
        for y in range(max(0, y0), min(self.h - 1, y1) + 1):
            for x in range(max(0, x0), min(self.w - 1, x1) + 1):
                self.auto[layer][y][x] = val

    def cell(self, x, y, val, layer=0):
        if self.inb(x, y): self.auto[layer][y][x] = val

    def put(self, x, y, tile, layer=2):
        if self.inb(x, y): self.top[layer - 2][y][x] = tile

    def get(self, x, y, layer=0):
        return self.auto[layer][y][x] if self.inb(x, y) else 'edge'

    # ---------------------------------------------------------------- resolve
    def tile_data(self):
        w, h = self.w, self.h
        out = [[0] * (w * h) for _ in range(6)]
        for L in range(2):
            grid = self.auto[L]
            for y in range(h):
                for x in range(w):
                    v = grid[y][x]
                    if v is None: continue
                    sheet, k = v
                    if sheet == 'A5':
                        out[L][y * w + x] = A5 + k; continue
                    if sheet == 'ID':
                        out[L][y * w + x] = k; continue
                    same = lambda xx, yy, v=v: (lambda g: g == 'edge' or _kind_of(g) == v)(self.get(xx, yy, L))
                    if sheet == 'A1' and k >= 5 and k % 2 == 1:   # waterfall: only left/right neighbours matter
                        shape = (0 if same(x - 1, y) else 1) + (0 if same(x + 1, y) else 2)
                    else:
                        shape = _shape(same, x, y, not is_wall_kind(sheet, k))
                    out[L][y * w + x] = BASE[sheet] + k * 48 + shape
        for L in range(2):
            for y in range(h):
                for x in range(w):
                    out[2 + L][y * w + x] = self.top[L][y][x]
        # editor-style auto shadow: ground cell whose left neighbour is a wall/roof gets a shadow on its left half
        for y in range(h):
            for x in range(1, w):
                if (x, y) in self.no_auto_shadow: continue
                here, left = self.auto[0][y][x], self.auto[0][y][x - 1]
                if here and left and here[0] in ('A1', 'A2', 'A5') and left[0] in ('A3', 'A4'):
                    up_left = self.auto[0][y - 1][x - 1] if y > 0 else None
                    self.shadow[y][x] = self.shadow[y][x] or (5 if (up_left and up_left[0] in ('A3', 'A4')) else 4)
        out[4] = [self.shadow[y][x] for y in range(h) for x in range(w)]
        return sum(out, [])

    # ---------------------------------------------------------------- events
    def add_event(self, name, x, y, pages, note=''):
        ev = {'id': len(self.events), 'name': name, 'note': note, 'pages': pages, 'x': x, 'y': y}
        self.events.append(ev)
        return ev

    def save(self, map_id, parent_id=0, order=None, expanded=False, encounter=None):
        tmpl = json.load(open(DATA + 'Map001.json', encoding='utf8'))
        m = dict(tmpl)
        m.update({'width': self.w, 'height': self.h, 'tilesetId': self.tileset_id, 'displayName': self.display,
                  'data': self.tile_data(), 'events': self.events, 'note': self.note,
                  'autoplayBgm': bool(self.bgm.get('name')), 'bgm': self.bgm,
                  'autoplayBgs': bool(self.bgs), 'bgs': self.bgs or {'name': '', 'pan': 0, 'pitch': 100, 'volume': 90},
                  'scrollType': 0, 'encounterList': encounter or [], 'encounterStep': 30, 'specifyBattleback': False,
                  'parallaxName': self.parallax, 'parallaxShow': bool(self.parallax), 'disableDashing': False})
        write_map(map_id, m)
        infos = json.load(open(DATA + 'MapInfos.json', encoding='utf8'))
        while len(infos) <= map_id: infos.append(None)
        infos[map_id] = {'id': map_id, 'expanded': expanded, 'name': self.name,
                         'order': order if order is not None else map_id, 'parentId': parent_id,
                         'scrollX': 0, 'scrollY': 0}
        with open(DATA + 'MapInfos.json', 'w', encoding='utf8', newline='') as f:
            f.write('[\n' + ',\n'.join(json.dumps(x, ensure_ascii=False, separators=(',', ':')) for x in infos) + '\n]')

    # ---------------------------------------------------------------- preview
    def render(self, path, scale=0.5, grid=False):
        img = render_map(self.tileset_id, self.w, self.h, self.tile_data(), self.events)
        if grid:
            d = ImageDraw.Draw(img)
            for x in range(0, self.w, 5):
                d.line([(x * 48, 0), (x * 48, img.height)], fill=(255, 0, 0, 90))
                d.text((x * 48 + 2, 2), str(x), fill=(255, 255, 0))
            for y in range(0, self.h, 5):
                d.line([(0, y * 48), (img.width, y * 48)], fill=(255, 0, 0, 90))
                d.text((2, y * 48 + 2), str(y), fill=(255, 255, 0))
        if scale != 1: img = img.resize((int(img.width * scale), int(img.height * scale)), Image.LANCZOS)
        img.save(path)
        return img


def write_map(map_id, m):
    """MapXXX.json in the editor's own layout (header line, data line, one event per line), so diffs stay small."""
    j = lambda v: json.dumps(v, ensure_ascii=False, separators=(',', ':'))
    head = ','.join('%s:%s' % (j(k), j(m[k])) for k in sorted(m) if k not in ('data', 'events'))
    text = '{\n' + head + ',\n"data":' + j(m['data']) + ',\n"events":[\n' + ',\n'.join(j(e) for e in m['events']) + '\n]\n}'
    with open(DATA + 'Map%03d.json' % map_id, 'w', encoding='utf8', newline='') as f:
        f.write(text)


# ====================================================================== events
def page(image=None, trigger=0, move_type=0, commands=None, priority=1, direction=2, through=False,
         walk_anim=True, step_anim=False, speed=3, freq=3, route=None, cond=None, dir_fix=False):
    img = {'tileId': 0, 'characterName': '', 'direction': direction, 'pattern': 1, 'characterIndex': 0}
    if image: img.update(image)
    conds = {'actorId': 1, 'actorValid': False, 'itemId': 1, 'itemValid': False, 'selfSwitchCh': 'A',
             'selfSwitchValid': False, 'switch1Id': 1, 'switch1Valid': False, 'switch2Id': 1,
             'switch2Valid': False, 'variableId': 1, 'variableValid': False, 'variableValue': 0}
    if cond: conds.update(cond)
    mr = {'list': (route or []) + [{'code': 0, 'parameters': []}], 'repeat': True, 'skippable': True, 'wait': False}
    return {'conditions': conds, 'directionFix': dir_fix, 'image': img,
            'list': (commands or []) + [{'code': 0, 'indent': 0, 'parameters': []}],
            'moveFrequency': freq, 'moveRoute': mr, 'moveSpeed': speed, 'moveType': 3 if route else move_type,
            'priorityType': priority, 'stepAnime': step_anim, 'through': through, 'trigger': trigger,
            'walkAnime': walk_anim}


def cmd(code, params, indent=0): return {'code': code, 'indent': indent, 'parameters': params}


def text(*lines, face=('', 0), indent=0):
    out = [cmd(101, [face[0], face[1], 0, 2], indent)]
    out += [cmd(401, [l], indent) for l in lines]
    return out


def say(speaker, *lines, face=('', 0), indent=0):
    return text('\\C[6]' + speaker + '\\C[0]', *lines, face=face, indent=indent)


def transfer(map_id, x, y, direction=0, fade=0, indent=0, se=None):
    out = []
    if se: out.append(cmd(250, [{'name': se, 'volume': 80, 'pitch': 100, 'pan': 0}], indent))
    out.append(cmd(201, [0, map_id, x, y, direction, fade], indent))
    return out


def common_event(ce_id, indent=0): return [cmd(117, [ce_id], indent)]


def rt(code, *params): return {'code': code, 'parameters': list(params), 'indent': None}
# move-route command codes
R_DOWN, R_LEFT, R_RIGHT, R_UP, R_RANDOM, R_TURN_DOWN, R_TURN_LEFT, R_TURN_RIGHT, R_TURN_UP, R_WAIT = 1, 2, 3, 4, 9, 16, 17, 18, 19, 15
R_TURN_RANDOM = 26


def char(sheet, index, direction=2, pattern=1):
    return {'characterName': sheet, 'characterIndex': index, 'direction': direction, 'pattern': pattern}


def tile_image(tile_id):
    return {'tileId': tile_id, 'characterName': '', 'characterIndex': 0, 'direction': 2, 'pattern': 0}


def door_page(target, dx, dy, ddir=8, sheet='!Door1', index=0, locked_text=None):
    """Animated door: opens, player steps through, transfer. index = door style on the sheet."""
    if locked_text:
        return page(char(sheet, index), commands=text(*locked_text))
    cmds = [cmd(250, [{'name': 'Open1', 'volume': 80, 'pitch': 100, 'pan': 0}]),
            cmd(205, [0, {'list': [rt(R_TURN_DOWN), rt(R_WAIT, 3), rt(R_TURN_LEFT), rt(R_WAIT, 3),
                                   rt(R_TURN_RIGHT), rt(R_WAIT, 3), rt(R_TURN_UP), {'code': 0, 'parameters': []}],
                          'repeat': False, 'skippable': False, 'wait': True}]),
            cmd(205, [-1, {'list': [rt(37), rt(R_UP), rt(38), {'code': 0, 'parameters': []}],
                           'repeat': False, 'skippable': False, 'wait': True}])]
    cmds += transfer(target, dx, dy, ddir)
    cmds.append(cmd(205, [0, {'list': [rt(R_TURN_DOWN), {'code': 0, 'parameters': []}],
                              'repeat': False, 'skippable': False, 'wait': False}]))
    return page(char(sheet, index), trigger=0, commands=cmds, walk_anim=False, dir_fix=False)


def exit_page(target, tx, ty, ddir):
    """Invisible touch exit (map edge / doorway)."""
    return page(None, trigger=1, priority=0, commands=transfer(target, tx, ty, ddir))


# ====================================================================== renderer
_TILESETS = None
_IMG_CACHE = {}


def _img(path):
    if path not in _IMG_CACHE:
        _IMG_CACHE[path] = Image.open(path).convert('RGBA') if os.path.exists(path) else None
    return _IMG_CACHE[path]


SHEET_OVERRIDES = {2: {7: 'Nova_Market_D'}}   # preview sheets not yet registered in Tilesets.json


def tileset_images(tileset_id):
    global _TILESETS
    if _TILESETS is None: _TILESETS = json.load(open(DATA + 'Tilesets.json', encoding='utf8'))
    names = list(_TILESETS[tileset_id]['tilesetNames'])
    for slot, n in SHEET_OVERRIDES.get(tileset_id, {}).items():
        if not names[slot]: names[slot] = n
    return [(_img(PROJ + 'img/tilesets/%s.png' % n) if n else None) for n in names]


def _draw_tile(dst, sets, tid, dx, dy):
    if tid >= EXT_BASE:
        sheet = ext_sheets().get((tid - EXT_BASE) // EXT_SPAN)
        s = sheet and _img(PROJ + 'img/tilesets/%s.png' % sheet[0])
        if not s: return
        n = (tid - EXT_BASE) % EXT_SPAN
        sx, sy = ((n // 128) % 2 * 8 + n % 8) * 48, ((n % 256) // 8 % 16) * 48
        dst.alpha_composite(s.crop((sx, sy, sx + 48, sy + 48)), (dx, dy))
        return
    if tid <= 0 or tid >= 8192: return
    if tid < A1:
        if tid >= A5: s = sets[4]
        else: s = sets[5 + tid // 256]
        if s is None: return
        sx = ((tid // 128) % 2 * 8 + tid % 8) * 48
        sy = ((tid % 256) // 8 % 16) * 48
        t = s.crop((sx, sy, sx + 48, sy + 48))
        dst.alpha_composite(t, (dx, dy))
        return
    kind, shape = (tid - A1) // 48, (tid - A1) % 48
    tx, ty = kind % 8, kind // 8
    table = FLOOR
    if tid < A2:
        s = sets[0]
        if kind == 0: bx, by = 0, 0
        elif kind == 1: bx, by = 0, 3
        elif kind == 2: bx, by = 6, 0
        elif kind == 3: bx, by = 6, 3
        else:
            bx = (tx // 4) * 8; by = ty * 6 + (tx // 2) % 2 * 3
            if kind % 2 == 1: bx += 6; table = WATERFALL
    elif tid < A3:
        s = sets[1]; bx, by = tx * 2, (ty - 2) * 3
    elif tid < A4:
        s = sets[2]; bx, by = tx * 2, (ty - 6) * 2; table = WALL
    else:
        s = sets[3]; bx = tx * 2; by = int((ty - 10) * 2.5 + (0.5 if ty % 2 == 1 else 0))
        if ty % 2 == 1: table = WALL
    if s is None: return
    q = table[shape]
    for i in range(4):
        qsx, qsy = q[i]
        sx, sy = (bx * 2 + qsx) * 24, (by * 2 + qsy) * 24
        dst.alpha_composite(s.crop((sx, sy, sx + 24, sy + 24)), (dx + (i % 2) * 24, dy + (i // 2) * 24))


def render_map(tileset_id, w, h, data, events=None):
    sets = tileset_images(tileset_id)
    img = Image.new('RGBA', (w * 48, h * 48), (0, 0, 0, 255))
    lay = lambda L, x, y: data[(L * h + y) * w + x]
    for L in range(2):
        for y in range(h):
            for x in range(w):
                _draw_tile(img, sets, lay(L, x, y), x * 48, y * 48)
    shade = Image.new('RGBA', (24, 24), (0, 0, 0, 128))
    for y in range(h):
        for x in range(w):
            bits = lay(4, x, y)
            for i in range(4):
                if bits & (1 << i): img.alpha_composite(shade, (x * 48 + (i % 2) * 24, y * 48 + (i // 2) * 24))
    for L in (2, 3):
        for y in range(h):
            for x in range(w):
                _draw_tile(img, sets, lay(L, x, y), x * 48, y * 48)
    for ev in (events or [])[1:]:
        if not ev or not ev['pages']: continue
        im = ev['pages'][0]['image']
        if im.get('tileId'):
            _draw_tile(img, sets, im['tileId'], ev['x'] * 48, ev['y'] * 48)
        elif im.get('characterName'):
            sheet = _img(PROJ + 'img/characters/%s.png' % im['characterName'])
            if sheet is None: continue
            big = '$' in im['characterName']
            cw = sheet.width // (3 if big else 12); ch = sheet.height // (4 if big else 8)
            idx = im['characterIndex']
            bx = 0 if big else (idx % 4) * 3 * cw; by = 0 if big else (idx // 4) * 4 * ch
            dirrow = {2: 0, 4: 1, 6: 2, 8: 3}[im.get('direction', 2)]
            fr = sheet.crop((bx + im.get('pattern', 1) * cw, by + dirrow * ch, bx + (im.get('pattern', 1) + 1) * cw, by + (dirrow + 1) * ch))
            img.alpha_composite(fr, (ev['x'] * 48 + 24 - cw // 2, ev['y'] * 48 + 48 - ch))
    return img
