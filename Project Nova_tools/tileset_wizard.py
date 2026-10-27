# Tileset Wizard: a page in your browser to build combined tilesets by clicking tiles from every sheet
# (Inside furniture in a town tileset, dungeon props indoors ...). It writes the tileset into the database
# with compose_tileset.py, so the RPG Maker editor shows it like any other tileset.
#
#   python tileset_wizard.py          opens it in its own window (Ctrl+C to stop); Windows: Tileset Wizard.bat,
#                                     Mac: Tileset Wizard.command (or python3 tileset_wizard.py)
#
# Only this computer can reach it (127.0.0.1); nothing is sent anywhere. Needs Python 3 with Pillow.
#
# Close the RPG Maker editor before pressing "Buat Tileset": the editor overwrites Tilesets.json when it saves.
import json, os, re, subprocess, sys, webbrowser
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import compose_tileset as C

PROJ = C.PROJ
PAGE = os.path.join(HERE, 'wizard', 'index.html')
RECIPES = os.path.join(HERE, 'tileset_recipes')
PORT = 8765
SLOT_KEYS = {4: 'A5', 5: 'B', 6: 'C', 7: 'D', 8: 'E'}


def _load(name):
    return json.load(open(PROJ + 'data/' + name, encoding='utf8'))


def map_usage():
    """{tileset id: {'maps': [map names], 'slots': {'C', 'A5', ...} that maps really use}}"""
    usage = {}
    for info in _load('MapInfos.json'):
        if not info: continue
        path = PROJ + 'data/Map%03d.json' % info['id']
        if not os.path.exists(path): continue
        m = json.load(open(path, encoding='utf8'))
        u = usage.setdefault(m['tilesetId'], {'maps': [], 'slots': set()})
        u['maps'].append(info['name'])
        ids = set(m['data'])
        ids.update(p['image']['tileId'] for e in m['events'] if e for p in e['pages'])
        for t in ids:
            if 0 < t < 1024: u['slots'].add('BCDE'[t // 256])
            elif 1536 <= t < 2048: u['slots'].add('A5')
    return usage


def state():
    tilesets, usage = _load('Tilesets.json'), map_usage()
    out_ts, sheets = [], {}
    for t in tilesets:
        if not t: continue
        u = usage.get(t['id'], {'maps': [], 'slots': set()})
        out_ts.append({'id': t['id'], 'name': t['name'], 'mode': t['mode'], 'names': t['tilesetNames'],
                       'flags': t['flags'][:2048], 'maps': u['maps'], 'usedSlots': sorted(u['slots'])})
        for s in range(4, 9):
            n = t['tilesetNames'][s]
            if n and n not in sheets:
                sheets[n] = {'name': n, 'kind': 'A5' if s == 4 else 'BE', 'tilesetId': t['id'],
                             'tileset': t['name'], 'first': C._first_id(s)}
    recipes = {}
    if os.path.isdir(RECIPES):
        for f in sorted(os.listdir(RECIPES)):
            if f.endswith('.json'):
                try:
                    r = json.load(open(os.path.join(RECIPES, f), encoding='utf8'))
                    recipes[r['name']] = r
                except (ValueError, KeyError):
                    pass
    return {'tilesets': out_ts, 'sheets': list(sheets.values()), 'recipes': recipes}


def editor_running():
    try:
        if os.name == 'nt':
            out = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq RPGMV.exe', '/NH'], capture_output=True, text=True).stdout
            return 'RPGMV.exe' in out
        if sys.platform == 'darwin':
            return subprocess.run(['pgrep', '-f', 'RPG Maker MV.app'], capture_output=True).returncode == 0
    except OSError:
        pass
    return False


def open_window(url):
    """Its own window, without tabs or address bar (Edge/Chrome app mode); the normal browser otherwise."""
    if os.name == 'nt':
        roots = [os.environ.get(k, '') for k in ('ProgramFiles(x86)', 'ProgramFiles', 'LOCALAPPDATA')]
        apps = [os.path.join(r, 'Microsoft', 'Edge', 'Application', 'msedge.exe') for r in roots if r] +                [os.path.join(r, 'Google', 'Chrome', 'Application', 'chrome.exe') for r in roots if r]
    elif sys.platform == 'darwin':
        apps = ['/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
                '/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge']
    else:
        apps = []
    for exe in apps:
        if os.path.isfile(exe):
            subprocess.Popen([exe, '--app=' + url, '--window-size=1500,950'])
            return
    webbrowser.open(url)


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args): pass

    def _send(self, code, body, ctype='application/json; charset=utf-8'):
        data = body if isinstance(body, bytes) else json.dumps(body, ensure_ascii=False).encode('utf8')
        self.send_response(code)
        self.send_header('Content-Type', ctype)
        self.send_header('Cache-Control', 'no-store')
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        path = self.path.split('?')[0]
        if path == '/':
            return self._send(200, open(PAGE, 'rb').read(), 'text/html; charset=utf-8')
        if path == '/api/state':
            return self._send(200, state())
        m = re.match(r'^/tileset/([\w\-. ()]+)\.png$', path)
        if m:
            f = PROJ + 'img/tilesets/%s.png' % m.group(1).replace('%20', ' ')
            if os.path.isfile(f): return self._send(200, open(f, 'rb').read(), 'image/png')
        self._send(404, {'error': 'not found'})

    def do_POST(self):
        if self.path != '/api/compose':
            return self._send(404, {'error': 'not found'})
        body = json.loads(self.rfile.read(int(self.headers.get('Content-Length', 0))).decode('utf8'))
        recipe, remap, check = body['recipe'], bool(body.get('remap')), bool(body.get('check'))
        if not check and editor_running():
            return self._send(409, {'error': 'Editor RPG Maker masih terbuka. Tutup dulu (simpan pekerjaanmu), '
                                             'lalu tekan Buat Tileset lagi.'})
        try:
            res = C.compose(recipe, remap=remap, check=check)
        except (ValueError, KeyError, OSError) as e:
            return self._send(400, {'error': str(e)})
        if not check:
            os.makedirs(RECIPES, exist_ok=True)
            safe = re.sub(r'[^A-Za-z0-9]+', '_', recipe['name']).strip('_')
            with open(os.path.join(RECIPES, safe + '.json'), 'w', encoding='utf8') as f:
                json.dump(recipe, f, ensure_ascii=False, indent=2)
        report = res['report']
        self._send(200, {'id': res['id'], 'tiles': len(res['ids']), 'report': report,
                         'text': C.describe(report) if (remap or check) else ''})


if __name__ == '__main__':
    server = ThreadingHTTPServer(('127.0.0.1', PORT), Handler)
    url = 'http://localhost:%d/' % PORT
    print('Tileset Wizard: %s   (Ctrl+C untuk berhenti)' % url)
    if '--no-browser' not in sys.argv: open_window(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
