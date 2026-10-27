# Builds a combined tileset for maps painted in the RPG Maker editor: floors/walls (A1-A4) from one tileset, and
# B-E / A5 sheets that are whole sheets or hand-picked tiles from ANY sheet (Inside furniture in an Outside
# tileset, dungeon props in a town ...). Passability etc. is copied from the tileset each tile comes from.
#
#   python compose_tileset.py recipe.json            writes img/tilesets/<Name>_<slot>_mix.png + Tilesets.json
#   python compose_tileset.py recipe.json --remap    same, and fixes the maps that already use this tileset
#   python compose_tileset.py recipe.json --check    only reports what --remap would change
#   python compose_tileset.py recipe.json --preview  writes the sheets and Tilesets.json to _work/compose/
#
# Recipe (JSON):
#   {"name": "Town Plus",            tileset name in the database (updated if it exists, else added)
#    "base": 2,                      tileset id that gives A1-A4, the mode and (unless set below) A5/B-E
#    "A5": "Inside_A5",              a whole sheet, or a list of picks (max 128)
#    "B":  "Outside_B",
#    "C":  [["Inside_C", 39], ["Inside_B", "49:1x2", "81:2x2"], ["Dungeon_C", 5, 6, 7]],
#    "D":  "Nova_Market_D",
#    "E":  [["SF_Inside_B", 16, 17, 18]],
#    "note": "optional"}
#
# Picks: a sheet name, then tile numbers, or blocks "first:WxH" (W columns, H rows starting at tile `first`) for
# furniture made of several tiles - a block keeps its shape on the new sheet, so it is painted the same way.
# Tile numbers are RPG Maker's numbering on the sheet (left half top-to-bottom, then right half); atlas.py's
# sheet_grid() draws a numbered grid of any sheet to pick from. Picks fill the new sheet from the top left
# (tile 0 stays empty, like every B sheet). Close the RPG Maker editor first: it overwrites Tilesets.json on save.
#
# Remap: maps store tile *positions*, so changing a slot that maps already use would show other pictures there.
# With remap every A5/B-E tile of those maps is moved to wherever the same picture sits in the new tileset;
# pictures that are no longer in it become NovaTilesetEx extra tiles (shown in the game, empty in the editor).
# A sheet that no tileset holds any more is kept in a "Nova Archive" tileset so its passability stays known.
# Tilesets.json, plugins.js and every changed map are copied to <project>_backups/tileset_<time>/ first.
import json, os, re, shutil, sys, time
from PIL import Image

_HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.environ.get('NOVA_PROJ') or next(p for p in [os.path.join(_HERE, '..')] + [os.path.join(_HERE, '..', n) for n in ('rpg_talesofnova', 'Project Nova')]
                                            if os.path.isfile(os.path.join(p, 'Game.rpgproject'))).replace('\\', '/') + '/'
A5_ID = 1536
SLOTS = {'A5': 4, 'B': 5, 'C': 6, 'D': 7, 'E': 8}
EXT_BASE, EXT_SPAN = 20000, 1000                    # NovaTilesetEx ids
PROVENANCE = os.environ.get('NOVA_PROVENANCE') or os.path.join(_HERE, 'tileset_recipes', '_provenance.json')   # composed sheet -> where each tile came from


def _xy(n):
    return ((n // 128) % 2 * 8 + n % 8) * 48, ((n % 256) // 8 % 16) * 48


def _cell(n):                                       # tile number -> (half, column, row)
    return n // 128, n % 8, (n % 128) // 8


def _num(half, col, row):
    return half * 128 + row * 8 + col


def _blocks(spec):
    """[(sheet, first, w, h)] from [["Sheet", 5, "49:2x2", ...], ...]."""
    out = []
    for pick in spec:
        for item in pick[1:]:
            m = re.match(r'^(\d+)(?::(\d+)x(\d+))?$', str(item))
            if not m: raise ValueError('bad pick %r (use 49 or "49:2x2")' % (item,))
            first, w, h = int(m.group(1)), int(m.group(2) or 1), int(m.group(3) or 1)
            if _cell(first)[1] + w > 8 or _cell(first)[2] + h > 16:
                raise ValueError('%s %s runs off the sheet half (8 columns x 16 rows)' % (pick[0], item))
            out.append((pick[0], first, w, h))
    return out


def _place(used, halves, w, h):
    """First free spot for a w x h block; marks it used. Returns (half, col, row) or None."""
    for half in range(halves):
        for row in range(16 - h + 1):
            for col in range(8 - w + 1):
                if all(not used[half][row + j][col + i] for j in range(h) for i in range(w)):
                    for j in range(h):
                        for i in range(w): used[half][row + j][col + i] = True
                    return half, col, row
    return None


def _first_id(slot):
    return A5_ID if slot == 4 else (slot - 5) * 256


def _sheet_slot(ts, sheet):
    return next((s for s in range(4, 9) if ts['tilesetNames'][s] == sheet), None)


def _flag_source(tilesets, sheet):
    """(flags, first id, slot) of the first tileset that has this sheet in A5 or B-E."""
    for ts in tilesets:
        if not ts: continue
        s = _sheet_slot(ts, sheet)
        if s is not None: return ts['flags'], _first_id(s), s
    raise KeyError('no tileset in the database uses sheet "%s" - flags unknown' % sheet)


def _read(path, default=None):
    return json.load(open(path, encoding='utf8')) if os.path.exists(path) else default


def _tilesets_text(tilesets):
    return '[\n' + ',\n'.join(json.dumps(t, ensure_ascii=False, separators=(',', ':')) for t in tilesets) + '\n]'


def _map_text(m):
    """The layout the RPG Maker editor writes: settings on one line, then data, then one event per line."""
    head = {k: v for k, v in m.items() if k not in ('data', 'events')}
    return ('{\n' + json.dumps(head, ensure_ascii=False, separators=(',', ':'))[1:-1] +
            ',\n"data":' + json.dumps(m['data'], separators=(',', ':')) +
            ',\n"events":[\n' + ',\n'.join(json.dumps(e, ensure_ascii=False, separators=(',', ':')) for e in m['events']) + '\n]\n}')


# ---------------------------------------------------------------- NovaTilesetEx registry in js/plugins.js
def _plugins():
    text = open(PROJ + 'js/plugins.js', encoding='utf8').read()
    m = re.search(r'^(\{"name":"NovaTilesetEx".*\}),?$', text, re.M)
    if not m: return text, None, None, {}
    entry = json.loads(m.group(1))
    slots = {}
    for line in json.loads(entry['parameters']['Extra Sheets']).splitlines():
        mm = re.match(r'\s*(\d+)\s*:\s*([^@]+?)\s*(?:@\s*(\d+))?\s*$', line)
        if mm: slots[mm.group(2)] = int(mm.group(1))
    return text, m.group(1), entry, slots


def _plugins_with(text, line, entry, new_sheets):
    """plugins.js text with sheets appended to NovaTilesetEx's "Extra Sheets"."""
    lines = json.loads(entry['parameters']['Extra Sheets']).rstrip('\n')
    for sheet, slot in new_sheets: lines += '\n%d: %s' % (slot, sheet)
    entry = dict(entry, parameters=dict(entry['parameters'], **{'Extra Sheets': json.dumps(lines, ensure_ascii=False)}))
    return text.replace(line, json.dumps(entry, ensure_ascii=False, separators=(',', ':')))


# ---------------------------------------------------------------- building the tileset
def _build(recipe, tilesets, old_prov):
    """New tilesetNames/flags, sheet images to write, and where each composed tile came from."""
    base = tilesets[recipe['base']]
    names, flags = list(base['tilesetNames']), list(base['flags'])
    ids, images, prov = {}, {}, {}                  # ids: (sheet, n) -> tile id in the new tileset
    safe = re.sub(r'[^A-Za-z0-9]+', '_', recipe['name']).strip('_')
    for key, slot in SLOTS.items():
        spec = recipe.get(key)
        if spec is None: continue
        first, size = _first_id(slot), (128 if slot == 4 else 256)
        if isinstance(spec, str):                   # a whole sheet
            names[slot] = spec
            if spec:
                src_flags, src_first, _ = _flag_source(tilesets, spec)
                flags[first:first + size] = src_flags[src_first:src_first + size]
                for n in range(size): ids[(spec, n)] = first + n
            continue
        halves = 1 if slot == 4 else 2
        used = [[[False] * 8 for _ in range(16)] for _ in range(halves)]
        used[0][0][0] = True                        # tile 0 stays empty
        sheet = Image.new('RGBA', (384 if slot == 4 else 768, 768), (0, 0, 0, 0))
        for f in range(first, first + size): flags[f] = 0x10 if slot != 4 and f == first else 0
        # never overwrite a sheet the composer did not make (a tileset called "Outside" must not replace Outside_C)
        name, k = '%s_%s_mix' % (safe, key), 2
        while os.path.exists(PROJ + 'img/tilesets/%s.png' % name) and name not in old_prov:
            name, k = '%s_%s_mix%d' % (safe, key, k), k + 1
        prov[name] = {}
        for src, n0, w, h in _blocks(spec):
            spot = _place(used, halves, w, h)
            if spot is None: raise ValueError('%s: no room left for %s %d (%dx%d)' % (key, src, n0, w, h))
            img = Image.open(PROJ + 'img/tilesets/%s.png' % src).convert('RGBA')
            src_flags, src_first, _ = _flag_source(tilesets, src)
            sh, sc, sr = _cell(n0)
            for j in range(h):
                for i in range(w):
                    n, m = _num(sh, sc + i, sr + j), _num(spot[0], spot[1] + i, spot[2] + j)
                    sx, sy = _xy(n)
                    sheet.paste(img.crop((sx, sy, sx + 48, sy + 48)), _xy(m))
                    flags[first + m] = src_flags[src_first + n]
                    ids[(src, n)] = first + m
                    prov[name][str(m)] = [src, n]
        names[slot] = name
        images[name] = sheet
    return names, flags, images, prov, ids


# ---------------------------------------------------------------- remap
def _identity(names, prov):
    """tile id -> (original sheet, tile number) for the A5 and B-E slots of a tileset."""
    out = {}
    for s in range(4, 9):
        sheet = names[s]
        if not sheet: continue
        first, size, p = _first_id(s), (128 if s == 4 else 256), prov.get(sheet)
        for n in range(size):
            if p is None: out[first + n] = (sheet, n)
            elif str(n) in p: out[first + n] = tuple(p[str(n)])
    return out


def _maps_using(tileset_id):
    for info in _read(PROJ + 'data/MapInfos.json', []):
        if not info: continue
        path = PROJ + 'data/Map%03d.json' % info['id']
        m = _read(path)
        if m and m['tilesetId'] == tileset_id: yield info['name'], path, m


def _plan_remap(target, new_names, old_prov, new_prov, ext_slots, ext_enabled):
    old_id = _identity(target['tilesetNames'], old_prov)   # a re-composed sheet keeps its name, so old and new differ
    new_rev = {}
    for tid, ident in sorted(_identity(new_names, new_prov).items()):
        new_rev.setdefault(ident, tid)
    report = {'maps': [], 'moved': 0, 'extra': 0, 'lost': 0, 'newExtraSheets': [], 'archived': []}
    new_ext, changed = [], []
    next_slot = max(ext_slots.values(), default=-1) + 1

    def remap(v):
        nonlocal next_slot
        if not (0 < v < 1024 or A5_ID <= v < A5_ID + 128): return v
        ident = old_id.get(v)
        if ident is None: return v
        nv = new_rev.get(ident)
        if nv is not None:
            if nv != v: report['moved'] += 1
            return nv
        if not ext_enabled:
            report['lost'] += 1
            return v
        sheet, n = ident
        if sheet not in ext_slots:
            ext_slots[sheet] = next_slot
            new_ext.append((sheet, next_slot))
            next_slot += 1
        report['extra'] += 1
        return EXT_BASE + ext_slots[sheet] * EXT_SPAN + n

    for name, path, m in _maps_using(target['id']):
        layers = 4 * m['width'] * m['height']
        data = m['data']
        before = (report['moved'], report['extra'], report['lost'])
        for i in range(layers):
            if data[i]: data[i] = remap(data[i])
        for e in m['events']:
            if e:
                for p in e['pages']:
                    if p['image']['tileId']: p['image']['tileId'] = remap(p['image']['tileId'])
        if (report['moved'], report['extra'], report['lost']) != before:
            report['maps'].append(name)
            changed.append((path, m))
    report['newExtraSheets'] = [s for s, _ in new_ext]
    return report, changed, new_ext


def _archive(tilesets, sheets_needed, old_tilesets):
    """Keep sheets that no tileset holds any more in 'Nova Archive N' tilesets, so their flags stay known."""
    archived = []
    for sheet in sheets_needed:
        if any(t and _sheet_slot(t, sheet) is not None for t in tilesets): continue
        flags, first, kind_slot = _flag_source(old_tilesets, sheet)
        want = [4] if kind_slot == 4 else [5, 6, 7, 8]
        home, slot = None, None
        for t in tilesets:
            if t and t['name'].startswith('Nova Archive'):
                slot = next((s for s in want if not t['tilesetNames'][s]), None)
                if slot is not None: home = t; break
        if home is None:
            n = 1 + sum(1 for t in tilesets if t and t['name'].startswith('Nova Archive'))
            home = {'id': len(tilesets), 'flags': [0] * 8192, 'mode': 1, 'name': 'Nova Archive %d' % n,
                    'note': 'Holds sheets that maps still use as NovaTilesetEx extra tiles, so their passability '
                            'stays known. Not meant for painting maps.', 'tilesetNames': [''] * 9}
            tilesets.append(home)
            slot = want[0]
        home['tilesetNames'][slot] = sheet
        size, dst = (128 if slot == 4 else 256), _first_id(slot)
        home['flags'][dst:dst + size] = flags[first:first + size]
        archived.append('%s -> %s' % (sheet, home['name']))
    return archived


# ---------------------------------------------------------------- main entry
def compose(recipe, preview=False, remap=False, check=False):
    """Returns {'id', 'ids', 'report'}; report says what remap changes (None without remap)."""
    tilesets = _read(PROJ + 'data/Tilesets.json')
    old_tilesets = json.loads(json.dumps(tilesets))
    prov = _read(PROVENANCE, {})
    names, flags, images, new_prov, ids = _build(recipe, tilesets, prov)
    all_prov = dict(prov, **new_prov)
    target = next((t for t in tilesets if t and t['name'] == recipe['name']), None)

    report, changed, new_ext = None, [], []
    plugins_text, plugins_line, ext_entry, ext_slots = _plugins()
    if (remap or check) and target is not None:
        report, changed, new_ext = _plan_remap(target, names, prov, all_prov, dict(ext_slots),
                                               ext_entry is not None and ext_entry.get('status', True))
        report['baseChanged'] = target['tilesetNames'][:4] != names[:4]

    if target is None:
        target = {'id': len(tilesets), 'name': recipe['name']}
        tilesets.append(target)
    target.update({'flags': flags, 'mode': tilesets[recipe['base']]['mode'], 'note': recipe.get('note', ''), 'tilesetNames': names})
    if report is not None:
        # Sheets this tileset gave up that maps may reference as extra tiles (remapped here, or painted with
        # NovaMapPainter): keep a flag source for them if no other tileset holds them.
        registered = set(ext_slots) | {s for s, _ in new_ext}
        old_sheets = {old_tilesets[target['id']]['tilesetNames'][s] for s in range(4, 9)} if target['id'] < len(old_tilesets) else set()
        report['archived'] = _archive(tilesets, sorted((old_sheets & registered) - {''}), old_tilesets)
    result = {'id': target['id'], 'ids': ids, 'report': report}
    if check: return result

    if preview:
        out = PROJ + 'Project Nova_tools/_work/compose/'
        os.makedirs(out, exist_ok=True)
        for name, img in images.items(): img.save(out + name + '.png')
        with open(out + 'Tilesets.json', 'w', encoding='utf8', newline='') as f: f.write(_tilesets_text(tilesets))
        return result

    # backups first
    stamp = time.strftime('%Y%m%d_%H%M%S')
    proj = PROJ.rstrip('/')
    backup = os.path.join(os.path.dirname(proj), os.path.basename(proj) + '_backups', 'tileset_' + stamp)
    os.makedirs(backup, exist_ok=True)
    shutil.copy2(PROJ + 'data/Tilesets.json', backup)
    shutil.copy2(PROJ + 'js/plugins.js', backup)
    for path, _ in changed: shutil.copy2(path, backup)

    for name, img in images.items(): img.save(PROJ + 'img/tilesets/' + name + '.png')
    os.makedirs(os.path.dirname(PROVENANCE), exist_ok=True)
    with open(PROVENANCE, 'w', encoding='utf8') as f: json.dump(all_prov, f, ensure_ascii=False, indent=1)
    with open(PROJ + 'data/Tilesets.json', 'w', encoding='utf8', newline='') as f: f.write(_tilesets_text(tilesets))
    if new_ext:
        with open(PROJ + 'js/plugins.js', 'w', encoding='utf8', newline='') as f:
            f.write(_plugins_with(plugins_text, plugins_line, ext_entry, new_ext))
    for path, m in changed:
        with open(path, 'w', encoding='utf8', newline='') as f: f.write(_map_text(m))
    if report is not None: report['backup'] = backup
    return result


def describe(report):
    if report is None: return 'tileset belum dipakai map - tidak ada yang perlu disesuaikan'
    if not report['maps']: return 'tidak ada tile di map yang terpengaruh'
    parts = ['%d map disesuaikan (%s)' % (len(report['maps']), ', '.join(report['maps']))]
    if report['moved']: parts.append('%d tile dipindah ke posisi barunya' % report['moved'])
    if report['extra']: parts.append('%d tile menjadi tile tambahan NovaTilesetEx (tampil di game, kosong di editor)' % report['extra'])
    if report['lost']: parts.append('%d tile TIDAK bisa dipertahankan (NovaTilesetEx tidak aktif)' % report['lost'])
    if report['newExtraSheets']: parts.append('sheet didaftarkan ke NovaTilesetEx: ' + ', '.join(report['newExtraSheets']))
    if report['archived']: parts.append('disimpan di arsip: ' + ', '.join(report['archived']))
    if report.get('baseChanged'): parts.append('PERINGATAN: lantai/dinding (A1-A4) ikut berubah - tidak disesuaikan')
    return '; '.join(parts)


if __name__ == '__main__':
    recipe = json.load(open(sys.argv[1], encoding='utf8'))
    preview, remap, check = '--preview' in sys.argv, '--remap' in sys.argv, '--check' in sys.argv
    res = compose(recipe, preview=preview, remap=remap, check=check)
    where = 'Project Nova_tools/_work/compose/' if preview else ('(cek saja)' if check else 'data/Tilesets.json')
    print('tileset %d "%s" -> %s (%d tiles mapped)' % (res['id'], recipe['name'], where, len(res['ids'])))
    if remap or check: print(describe(res['report']))
