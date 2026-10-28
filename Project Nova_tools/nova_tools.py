# Nova Tools: the Map Editor and the Tileset Wizard in one window of their own.
#
#   python nova_tools.py              Windows: Nova Tools.bat   Mac: Nova Tools.command   (Ctrl+C to stop)
#
# Map Editor: paints every tile layer of a map - floors, walls and water as joined autotiles (A1-A4), A5, objects
# from the map's own B-E sheets and from every NovaTilesetEx sheet, wall shadows and regions. Events can be placed,
# moved, copied and set up (image, trigger, priority, page conditions, quick NPC/door/chest templates); their
# command lists are shown but edited in the RPG Maker editor. Saving writes the map file in the editor's layout and keeps the old file in
# <project>_backups/map_editor/. Only this computer can reach the server (127.0.0.1). Needs Python 3 with Pillow.
import json, os, re, shutil, sys, time
from urllib.parse import unquote
from http.server import ThreadingHTTPServer

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import tileset_wizard as W
import compose_tileset as C
import nova_maplib as L

PROJ = C.PROJ
MAP_PAGE = os.path.join(HERE, 'mapeditor', 'index.html')
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


class Handler(W.Handler):
    def do_GET(self):
        path, _, query = self.path.partition('?')
        q = dict(p.split('=', 1) for p in query.split('&') if '=' in p)
        if path in ('/', '/map'):
            return self._send(200, open(MAP_PAGE, 'rb').read(), 'text/html; charset=utf-8')
        if path == '/wizard':
            return self._send(200, open(W.PAGE, 'rb').read(), 'text/html; charset=utf-8')
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
        return W.Handler.do_POST(self)


def main(page='/'):
    server = ThreadingHTTPServer(('127.0.0.1', PORT), Handler)
    url = 'http://localhost:%d%s' % (PORT, page)
    print('Nova Tools: %s   (Ctrl+C untuk berhenti)' % url)
    if '--no-browser' not in sys.argv: W.open_window(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    main('/wizard' if '--wizard' in sys.argv else '/')
