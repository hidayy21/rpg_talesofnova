# Playtest straight into any map: starts MV's own playtest runtime (as Playtest.command / Playtest.bat do) with
# "start=map,x,y,dir" on its command line; NovaSceneSelect then skips the title and begins a new game on that tile.
# Works on maps nothing links to yet. The Map Editor's "Main" button calls this through /api/playtest.
#   python playtest.py 31              -> new game on Map031, on the open tile nearest its middle
#   python playtest.py 31 27 19        -> on (27, 19), or the nearest open tile
#   python playtest.py 31 27 19 21:00  -> and with the clock at 21:00 (NovaDayNight), to see the night
import json, os, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import nova_maplib as L

_STEAM_MAC = os.path.expanduser('~/Library/Application Support/Steam/steamapps/common/RPG Maker MV/RPG Maker MV.app')
RUNTIMES = [
    _STEAM_MAC + '/Contents/MacOS/nwjs-osx-test/Game.app/Contents/MacOS/nwjs',
    '/Applications/RPG Maker MV.app/Contents/MacOS/nwjs-osx-test/Game.app/Contents/MacOS/nwjs',
] + [os.path.join(os.environ.get(v, ''), sub, 'nwjs-win-test', 'Game.exe')
     for v in ('ProgramFiles(x86)', 'ProgramFiles')
     for sub in (r'Steam\steamapps\common\RPG Maker MV', r'KADOKAWA\RPGMV') if os.environ.get(v)]


def runtime():
    return next((p for p in RUNTIMES if os.path.isfile(p)), None)


def passable(mp, flags, x, y):
    """MV's own rule (Game_Map.checkPassage): the topmost tile that is not a ☆ tile decides."""
    w, h, d = mp['width'], mp['height'], mp['data']
    for l in (3, 2, 1, 0):
        f = flags[d[(l * h + y) * w + x]] if d[(l * h + y) * w + x] < len(flags) else 0
        if f & 0x10: continue
        return (f & 0x0f) != 0x0f
    return False


def start_spot(map_id, x=None, y=None):
    """(x, y) itself when a party can stand there, else the nearest such tile (from the middle when none is given)."""
    mp = json.load(open(L.DATA + 'Map%03d.json' % map_id, encoding='utf8'))
    w, h = mp['width'], mp['height']
    flags = L.tileset_flags(mp['tilesetId'])
    taken = {(e['x'], e['y']) for e in mp['events'] if e}
    x = w // 2 if x is None else max(0, min(w - 1, x))
    y = h // 2 if y is None else max(0, min(h - 1, y))
    cells = sorted(((cx, cy) for cy in range(h) for cx in range(w)), key=lambda c: (c[0] - x) ** 2 + (c[1] - y) ** 2)
    return next(((cx, cy) for cx, cy in cells if (cx, cy) not in taken and passable(mp, flags, cx, cy)), (x, y))


def launch(map_id, x=None, y=None, clock=None, direction=2):
    nw = runtime()
    if not nw:
        return None, 'Runtime playtest RPG Maker MV tidak ditemukan. Dicari di:\n' + '\n'.join(RUNTIMES)
    x, y = start_spot(map_id, x, y)
    arg = 'test&start=%d,%d,%d,%d' % (map_id, x, y, direction) + ('&clock=' + clock if clock else '')
    kw = {'stdout': subprocess.DEVNULL, 'stderr': subprocess.DEVNULL, 'cwd': L.PROJ}
    if os.name == 'nt': kw['creationflags'] = 0x00000008          # DETACHED_PROCESS: keeps running on its own
    else: kw['start_new_session'] = True
    subprocess.Popen([nw, L.PROJ.rstrip('/'), arg], **kw)
    return (x, y), None


if __name__ == '__main__':
    a = sys.argv[1:]
    spot, err = launch(int(a[0]), int(a[1]) if len(a) > 2 else None, int(a[2]) if len(a) > 2 else None,
                       a[3] if len(a) > 3 else None)
    print(err or 'Map%03d dari (%d, %d)' % ((int(a[0]),) + spot))
