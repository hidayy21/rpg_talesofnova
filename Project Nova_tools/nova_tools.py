# Nova Tools: the Map Editor and the Tileset Wizard in one window of their own.
#
#   python nova_tools.py              Windows: Nova Tools.bat   Mac: Nova Tools.command   (Ctrl+C to stop)
#   python nova_tools.py --chargen    straight to the Character page: Nova Character.bat / Nova Character.command
#
# Map Editor: paints every tile layer of a map - floors, walls and water as joined autotiles (A1-A4), A5, objects
# from the map's own B-E sheets and from every NovaTilesetEx sheet, wall shadows and regions. Events can be placed,
# moved, copied and set up (image, trigger, priority, page conditions, quick NPC/door/chest templates); their
# command lists are shown but edited in the RPG Maker editor. The Passage tool edits tile flags (passage, 4 directions,
# ladder, bush, counter, damage, terrain tag) into Tilesets.json, like the editor's Tileset tab. Saving writes the map file in the editor's layout and keeps the old file in
# <project>_backups/map_editor/. Only this computer can reach the server (127.0.0.1). Needs Python 3 with Pillow.
# Character (/chargen): RPG Maker's Character Generator without the editor (chargen.py, chargen_api.py) - new
# characters from its parts and the packs in generator_parts/, and finished faces with eyes or mouth swapped.
import json, os, re, shutil, sys, time
from urllib.parse import unquote
from http.server import ThreadingHTTPServer

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import tileset_wizard as W
import compose_tileset as C
import nova_maplib as L
import chargen_api as CG

PROJ = C.PROJ
MAP_PAGE = os.path.join(HERE, 'mapeditor', 'index.html')
CHAR_PAGE = os.path.join(HERE, 'chargen', 'index.html')
PORT = 8765


def map_path(map_id):
    return PROJ + 'data/Map%03d.json' % map_id


def maps():
    out = []
    for info in W._load('MapInfos.json'):
        if not info: continue
        m = C._read(map_path(info['id']))
        if not m: continue
        out.append({'id': info['id'], 'name': info['name'], 'parentId': info['parentId'], 'order': info['order'],
                    'expanded': info.get('expanded', False), 'tilesetId': m['tilesetId'],
                    'width': m['width'], 'height': m['height']})
    return out


def ext_sheets():
    """NovaTilesetEx sheets with their passability flags (same lookup as the plugin)."""
    _, _, entry, _ = C._plugins()
    if not entry or not entry.get('status', True): return []
    tilesets, out = W._load('Tilesets.json'), []
    for line in json.loads(entry['parameters']['Extra Sheets']).splitlines():
        m = re.match(r'\s*(\d+)\s*:\s*([^@]+?)\s*(?:@\s*(\d+))?\s*$', line)
        if not m: continue
        slot, name, src = int(m.group(1)), m.group(2), int(m.group(3) or 0)
        flags, a5 = [0] * 256, name.endswith('_A5')
        for ts in ([tilesets[src]] if src else tilesets):
            s = ts and C._sheet_slot(ts, name)
            if s:
                first, size = C._first_id(s), (128 if s == 4 else 256)
                flags, a5 = ts['flags'][first:first + size], s == 4
                break
        out.append({'slot': slot, 'name': name, 'a5': a5, 'flags': flags})
    return out


def database():
    """Names the event panel shows: switches, variables, items, actors ... (index = id)."""
    system = W._load('System.json')
    named = lambda f: [(e or {}).get('name', '') for e in W._load(f)]
    with_icon = lambda f: [[e['name'], e['iconIndex']] if e else ['', 0] for e in W._load(f)]
    return {'switches': system['switches'], 'variables': system['variables'], 'actors': named('Actors.json'),
            'items': with_icon('Items.json'), 'weapons': with_icon('Weapons.json'), 'armors': with_icon('Armors.json'),
            'commonEvents': named('CommonEvents.json'), 'troops': named('Troops.json')}


def files(folder, ext):
    path = PROJ + folder
    return sorted(f[:-len(ext)] for f in os.listdir(path) if f.endswith(ext)) if os.path.isdir(path) else []


def save_map(map_id, data, events, mtime, force):
    path = map_path(map_id)
    if not force and W.editor_running():
        return 409, {'error': 'editor', 'message': 'Editor RPG Maker sedang terbuka. Kalau kamu simpan sekarang, '
                     'buka ulang project di editor sebelum menyimpan map ini dari sana, atau editor menimpanya lagi.'}
    if abs(os.path.getmtime(path) - mtime) > 0.01:
        return 409, {'error': 'changed', 'message': 'File map ini berubah di luar Nova Tools (disimpan dari editor?). '
                     'Muat ulang map dulu supaya tidak menimpa perubahan itu.'}
    m = C._read(path)
    if len(data) != len(m['data']):
        return 400, {'error': 'size', 'message': 'Ukuran map di file berbeda. Muat ulang map.'}
    proj = os.path.abspath(PROJ)          # PROJ ends in "Project Nova_tools/../"
    backups = os.path.join(os.path.dirname(proj), os.path.basename(proj) + '_backups', 'map_editor')
    os.makedirs(backups, exist_ok=True)
    shutil.copy2(path, os.path.join(backups, 'Map%03d_%s.json' % (map_id, time.strftime('%Y%m%d_%H%M%S'))))
    m['data'] = data
    if events is not None:
        if not isinstance(events, list) or any(e is not None and e.get('id') != i for i, e in enumerate(events)):
            return 400, {'error': 'events', 'message': 'Daftar event tidak valid; map tidak disimpan.'}
        m['events'] = events
    with open(path, 'w', encoding='utf8', newline='') as f: f.write(C._map_text(m))
    return 200, {'mtime': os.path.getmtime(path)}


FLAG_MASK = 0xF1FF      # what the Passage tool edits: 4 directions, star, ladder, bush, counter, damage, terrain tag


def save_flags(edits, force):
    """Passage edits: {'tileset', 'kind', 'v'} sets all 48 shapes of an A1-A4 autotile in that tileset;
    {'sheet', 'n', 'v'} sets tile n of a B-E/A5 sheet in every tileset that has the sheet (so NovaTilesetEx and
    the other tilesets keep the same passability). Boat/ship/airship bits are kept."""
    path = PROJ + 'data/Tilesets.json'
    if not force and W.editor_running():
        return 409, {'error': 'editor', 'message': 'Editor RPG Maker sedang terbuka. Editor menyimpan seluruh database '
                     '(termasuk Tilesets.json) setiap kali kamu menyimpan di sana - tutup editor dulu, atau buka ulang '
                     'project di editor sesudah ini supaya passage yang baru tidak tertimpa.'}
    tilesets, missing = C._read(path), []
    merge = lambda old, v: (old & ~FLAG_MASK) | (int(v) & FLAG_MASK)
    for e in edits:
        if 'kind' in e:
            ts, kind = tilesets[int(e['tileset'])], int(e['kind'])
            if not ts or not 0 <= kind < 128: return 400, {'error': 'flags', 'message': 'Autotile tidak valid.'}
            for k in range(48):
                i = 2048 + kind * 48 + k
                ts['flags'][i] = merge(ts['flags'][i], e['v'])
            continue
        n, hit = int(e['n']), False
        for ts in tilesets:
            s = ts and C._sheet_slot(ts, e['sheet'])
            if s and n < (128 if s == 4 else 256):
                i = C._first_id(s) + n
                ts['flags'][i] = merge(ts['flags'][i], e['v'])
                hit = True
        if not hit: missing.append(e['sheet'])
    proj = os.path.abspath(PROJ)
    backups = os.path.join(os.path.dirname(proj), os.path.basename(proj) + '_backups', 'map_editor')
    os.makedirs(backups, exist_ok=True)
    shutil.copy2(path, os.path.join(backups, 'Tilesets_%s.json' % time.strftime('%Y%m%d_%H%M%S')))
    with open(path, 'w', encoding='utf8', newline='') as f: f.write(C._tilesets_text(tilesets))
    return 200, {'missing': sorted(set(missing))}


class Handler(W.Handler):
    def do_GET(self):
        path, _, query = self.path.partition('?')
        q = dict(p.split('=', 1) for p in query.split('&') if '=' in p)
        if path in ('/', '/map'):
            return self._send(200, open(MAP_PAGE, 'rb').read(), 'text/html; charset=utf-8')
        if path == '/wizard':
            return self._send(200, open(W.PAGE, 'rb').read(), 'text/html; charset=utf-8')
        if path == '/chargen':
            return self._send(200, open(CHAR_PAGE, 'rb').read(), 'text/html; charset=utf-8')
        res = CG.handle_get(path, query)
        if res:
            code, body, ctype = res
            return self._send(code, body, ctype) if ctype else self._send(code, body)
        if path == '/api/maps':
            return self._send(200, {'maps': maps(), 'editorOpen': W.editor_running()})
        if path == '/api/map':
            map_id = int(q.get('id', 0))
            m = C._read(map_path(map_id))
            if not m: return self._send(404, {'error': 'no such map'})
            ts = W._load('Tilesets.json')[m['tilesetId']]
            return self._send(200, {'map': m, 'mtime': os.path.getmtime(map_path(map_id)), 'tileset': ts})
        if path == '/api/setup':
            return self._send(200, {'floor': L.FLOOR, 'wall': L.WALL, 'waterfall': L.WATERFALL,
                                    'ext': ext_sheets(), 'extBase': L.EXT_BASE, 'extSpan': L.EXT_SPAN,
                                    'db': database(), 'characters': files('img/characters', '.png'),
                                    'se': files('audio/se', '.ogg') or files('audio/se', '.m4a')})
        m = re.match(r'^/character/([^/]+)\.png$', path)
        if m:
            name = unquote(m.group(1))
            f = PROJ + 'img/characters/%s.png' % name
            if os.path.basename(name) == name and '..' not in name and os.path.isfile(f):
                return self._send(200, open(f, 'rb').read(), 'image/png')
            return self._send(404, {'error': 'not found'})
        return W.Handler.do_GET(self)

    def do_POST(self):
        if self.path == '/api/map/save':
            body = json.loads(self.rfile.read(int(self.headers.get('Content-Length', 0))).decode('utf8'))
            code, out = save_map(int(body['id']), body['data'], body.get('events'), float(body['mtime']),
                                 bool(body.get('force')))
            return self._send(code, out)
        if self.path == '/api/tileset/flags':
            body = json.loads(self.rfile.read(int(self.headers.get('Content-Length', 0))).decode('utf8'))
            return self._send(*save_flags(body['edits'], bool(body.get('force'))))
        if self.path.startswith('/api/chargen/'):
            body = json.loads(self.rfile.read(int(self.headers.get('Content-Length', 0))).decode('utf8'))
            code, out, _ = CG.handle_post(self.path, body)
            return self._send(code, out)
        return W.Handler.do_POST(self)


class Server(ThreadingHTTPServer):
    # on Windows SO_REUSEADDR lets a second Nova Tools listen on the same port, and the two then take turns answering
    # (an old copy with old code, saves going to either) - so there the bind must fail instead
    allow_reuse_address = os.name != 'nt'


def main(page='/'):
    url = 'http://localhost:%d%s' % (PORT, page)
    try:
        server = Server(('127.0.0.1', PORT), Handler)
    except OSError:
        print('Nova Tools sudah berjalan di port %d - membuka jendelanya saja.' % PORT)
        print('(Kalau baru mengubah kode Nova Tools, tutup dulu yang lama: Ctrl+C di jendela konsolnya.)')
        if '--no-browser' not in sys.argv: W.open_window(url)
        return
    print('Nova Tools: %s   (Ctrl+C untuk berhenti)' % url)
    if '--no-browser' not in sys.argv: W.open_window(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    main('/wizard' if '--wizard' in sys.argv else '/chargen' if '--chargen' in sys.argv else '/')
