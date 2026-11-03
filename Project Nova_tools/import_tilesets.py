# Import new tile sheets dropped in img/tilesets/import/: one new tileset per pack, like the PandaMaru ones.
#
# File names say what each sheet is, RPG Maker style:  <Pack>_A1.png ... <Pack>_A5.png, <Pack>_B.png, <Pack>_B2.png
# (C/D/E work like B), or a folder per pack:  import/<Pack>/A2.png, import/<Pack>/B.png ...
#
# The pack's A1-A5 replace those slots of a base tileset (Outside, Inside or Dungeon); the slots the pack lacks keep
# the base's sheets. A1-A4 start with the base's passability (RPG Maker's sheet layouts are the same), A5 and the
# object sheets start passable (tile 0 above characters) - set them with the Passage tool in the Map Editor.
# A pack folder may hold passage.json for whole autotiles: {"A2": {"12": "x", "28": "x"}} (o / x / star).
# Object sheets go four to a tileset ("<Pack>", "<Pack> 2" ...) and become NovaTilesetEx extra sheets, so every
# map's palette has them under "+ Sheet lain"; the pack's A5 too.
# The sheets move to img/tilesets/ (smaller ones padded to the full size); the originals, Tilesets.json and
# plugins.js are copied to <project>_backups/tileset_import_<time>/ first.
#
#   python import_tilesets.py                       -> list the packs found
#   python import_tilesets.py Pack [Inside] --save  -> import one (RPG Maker MV must be closed)
import json, os, re, shutil, sys, time
from PIL import Image
import compose_tileset as C

IMPORT_DIR = C.PROJ + 'img/tilesets/import/'
SIZES = {'A1': (768, 576), 'A2': (768, 576), 'A3': (768, 384), 'A4': (768, 720), 'A5': (384, 768), 'B': (768, 768)}
A_SLOT = {'A1': 0, 'A2': 1, 'A3': 2, 'A4': 3, 'A5': 4}
BASES = {'Outside': 2, 'Inside': 3, 'Dungeon': 4}
A_KIND0 = {'A1': 0, 'A2': 16, 'A3': 48, 'A4': 80}           # first autotile kind of each A sheet
PASS = {'o': 0, 'x': 0x0F, 'star': 0x10}
KIND_RE = re.compile(r'(?:^|[_\- ])(A[1-5]|[B-E])(\d*)$', re.I)
safe = lambda s: re.sub(r'[^A-Za-z0-9]+', '_', s).strip('_')


def _sheets():
    """[(pack, path, kind 'A1'..'A5'|'B', order key)] for every png in the import folder."""
    out = []
    if not os.path.isdir(IMPORT_DIR): return out
    for entry in sorted(os.listdir(IMPORT_DIR)):
        full = os.path.join(IMPORT_DIR, entry)
        files = [(entry, os.path.join(full, f)) for f in sorted(os.listdir(full))] if os.path.isdir(full) else [(None, full)]
        for folder, path in files:
            stem, ext = os.path.splitext(os.path.basename(path))
            if ext.lower() != '.png': continue
            m = KIND_RE.search(stem)
            if not m: out.append((folder or stem, path, None, '')); continue
            pack = folder or stem[:m.start()]
            letter = m.group(1).upper()
            out.append((pack, path, letter if letter[0] == 'A' else 'B', '%s%04d' % (letter, int(m.group(2) or 1))))
    return out


def scan():
    """Packs found, each {'pack', 'base', 'files': [{file, kind, dest, size, problem}], 'ok', 'tilesets'}."""
    existing = {f[:-4].lower() for f in os.listdir(C.PROJ + 'img/tilesets') if f.endswith('.png')}
    packs = {}
    for pack, path, kind, key in _sheets():
        packs.setdefault(pack, []).append((key, path, kind))
    out = []
    for pack, items in sorted(packs.items()):
        name, files, objects, seen = safe(pack), [], 0, set()
        for key, path, kind in sorted(items, key=lambda t: (t[2] is None, t[0])):
            rel = os.path.relpath(path, IMPORT_DIR).replace('\\', '/')
            f = {'file': rel, 'kind': kind, 'dest': '', 'size': None, 'problem': ''}
            files.append(f)
            if not name: f['problem'] = 'beri nama pack di depan nama file, misalnya Hutan_B.png'; continue
            if kind is None: f['problem'] = 'nama file tidak berakhiran _A1-_A5 atau _B/_C/_D/_E'; continue
            if kind == 'B':
                objects += 1
                f['dest'] = '%s_B%s' % (name, objects if objects > 1 else '')
            else:
                f['dest'] = '%s_%s' % (name, kind)
                if kind in seen: f['problem'] = 'ada dua sheet %s di pack ini' % kind
                seen.add(kind)
            try:
                with Image.open(path) as im: w, h = f['size'] = list(im.size)
            except OSError as e:
                f['problem'] = 'gambar tidak bisa dibuka: %s' % e; continue
            fw, fh = SIZES[kind]
            if w > fw or h > fh: f['problem'] = 'terlalu besar: %dx%d, maksimal %dx%d' % (w, h, fw, fh)
            elif w % 48 or h % 48: f['problem'] = 'ukuran %dx%d bukan kelipatan 48' % (w, h)
            elif (w, h) != (fw, fh): f['note'] = 'diisi transparan sampai %dx%d' % (fw, fh)
            if not f['problem'] and f['dest'].lower() in existing: f['problem'] = 'img/tilesets/%s.png sudah ada' % f['dest']
        inside = re.search(r'inside|interior|indoor|room|house_in', pack, re.I)
        out.append({'pack': pack, 'name': name, 'files': files, 'ok': bool(files) and not any(f['problem'] for f in files),
                    'base': 'Dungeon' if re.search(r'dungeon|cave', pack, re.I) else 'Inside' if inside else 'Outside',
                    'tilesets': max(1, -(-objects // 4))})
    return out


def import_pack(pack, base='Outside', title=None):
    """Writes the pack's tileset(s); returns {'ids': [...], 'sheets': [...], 'backup': dir}."""
    found = next((p for p in scan() if p['pack'] == pack), None)
    if not found: raise ValueError('Pack "%s" tidak ada di img/tilesets/import/.' % pack)
    if not found['ok']: raise ValueError('Pack "%s" belum bisa diimpor: %s' % (pack, '; '.join(
        '%s: %s' % (f['file'], f['problem']) for f in found['files'] if f['problem'])))
    if base not in BASES: raise ValueError('Dasar tileset harus Outside, Inside atau Dungeon.')
    tilesets = C._read(C.PROJ + 'data/Tilesets.json')
    plugins_text, plugins_line, entry, ext_slots = C._plugins()
    if entry is None: raise ValueError('Plugin NovaTilesetEx tidak ada di js/plugins.js.')
    title = (title or found['name'].replace('_', ' ')).strip()
    if any(t and t['name'] in (title, title + ' 2') for t in tilesets): raise ValueError('Tileset "%s" sudah ada.' % title)

    src = tilesets[BASES[base]]
    names, flags = list(src['tilesetNames']), list(src['flags'])
    a_files = [f for f in found['files'] if f['kind'] != 'B']
    objects = [f for f in found['files'] if f['kind'] == 'B']
    for f in a_files:
        names[A_SLOT[f['kind']]] = f['dest']
        if f['kind'] == 'A5': flags[C.A5_ID:C.A5_ID + 128] = [0] * 128
    # passage.json in a pack's folder sets whole autotiles: {"A2": {"12": "x"}} (o passable, x blocked, star above)
    rules = os.path.join(IMPORT_DIR, pack, 'passage.json')
    if os.path.isfile(rules):
        for sheet, kinds in json.load(open(rules, encoding='utf8')).items():
            for k, v in kinds.items():
                first = 2048 + (A_KIND0[sheet] + int(k)) * 48
                for i in range(first, first + 48): flags[i] = (flags[i] & ~0x5F) | PASS[v]   # directions, star, bush
    groups = [objects[i:i + 4] for i in range(0, len(objects), 4)] or [[]]
    new_ids, new_ext, slot = [], [], max(ext_slots.values(), default=-1) + 1
    for g, group in enumerate(groups):
        ts_names, ts_flags = list(names), list(flags)
        ts_flags[0:1024] = [0] * 1024
        for s in range(4): ts_names[5 + s] = group[s]['dest'] if s < len(group) else ''
        for s in range(len(group)): ts_flags[s * 256] = 0x10                     # tile 0 of every sheet: empty, star
        tid = len(tilesets)
        tilesets.append({'id': tid, 'flags': ts_flags, 'mode': src['mode'], 'name': title + (' %d' % (g + 1) if g else ''),
                         'note': 'Imported from img/tilesets/import/%s' % pack, 'tilesetNames': ts_names})
        new_ids.append(tid)
        for f in group + ([f for f in a_files if f['kind'] == 'A5'] if g == 0 else []):
            new_ext.append(('%s @ %d' % (f['dest'], tid), slot)); slot += 1

    stamp = time.strftime('%Y%m%d_%H%M%S')
    proj = os.path.abspath(C.PROJ)
    backup = os.path.join(os.path.dirname(proj), os.path.basename(proj) + '_backups', 'tileset_import_' + stamp)
    os.makedirs(backup, exist_ok=True)
    shutil.copy2(C.PROJ + 'data/Tilesets.json', backup)
    shutil.copy2(C.PROJ + 'js/plugins.js', backup)
    for f in found['files']:
        path = os.path.join(IMPORT_DIR, f['file'])
        with Image.open(path) as im:
            sheet = Image.new('RGBA', SIZES[f['kind']], (0, 0, 0, 0))
            sheet.paste(im.convert('RGBA'), (0, 0))
        sheet.save(C.PROJ + 'img/tilesets/%s.png' % f['dest'])
        os.makedirs(os.path.dirname(os.path.join(backup, 'import', f['file'])), exist_ok=True)
        shutil.move(path, os.path.join(backup, 'import', f['file']))
    if os.path.isfile(rules): shutil.move(rules, os.path.join(backup, 'import', pack, 'passage.json'))
    folder = os.path.join(IMPORT_DIR, pack)
    if os.path.isdir(folder) and not os.listdir(folder): os.rmdir(folder)
    with open(C.PROJ + 'data/Tilesets.json', 'w', encoding='utf8', newline='') as fh: fh.write(C._tilesets_text(tilesets))
    with open(C.PROJ + 'js/plugins.js', 'w', encoding='utf8', newline='') as fh:
        fh.write(C._plugins_with(plugins_text, plugins_line, entry, new_ext))
    return {'ids': new_ids, 'names': [tilesets[i]['name'] for i in new_ids], 'sheets': [f['dest'] for f in found['files']],
            'backup': backup}


if __name__ == '__main__':
    if hasattr(sys.stdout, 'reconfigure'): sys.stdout.reconfigure(errors='replace')
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    if args and '--save' in sys.argv:
        print(import_pack(args[0], args[1] if len(args) > 1 else 'Outside'))
    else:
        packs = scan()
        if not packs: print('Tidak ada sheet di img/tilesets/import/.')
        for p in packs:
            print('%s  (dasar %s, %d tileset)%s' % (p['pack'], p['base'], p['tilesets'], '' if p['ok'] else '  BELUM BISA'))
            for f in p['files']:
                print('   %-30s %-3s -> %-22s %s' % (f['file'], f['kind'] or '?', f['dest'], f['problem'] or f.get('note', '')))
