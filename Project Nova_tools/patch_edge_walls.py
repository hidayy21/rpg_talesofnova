# Gives wall autotiles (A3 roofs/walls, A4 wall sides) their border line along the map edge, as RPG Maker's editor
# draws them: walls do not continue past the edge, floors and water do. Maps built by script (or by Nova Tools before
# 2026-11-09) treated the edge as "same" there. Only the edge bits of the shape change (wall shape = border bitmask:
# 1 left, 2 top, 4 right, 8 bottom), so hand-picked seams and everything else stay as they are; only the "data" line
# of each map file is rewritten.
#   python patch_edge_walls.py                 -> report
#   python patch_edge_walls.py --apply         -> write the maps (RPG Maker editor must be closed)
#   python patch_edge_walls.py --before DIR    -> also render every changed map before/after into DIR
import json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import nova_maplib as L

A1 = L.A1


def is_wall(t):
    if not (L.A3 <= t < 8192): return False
    k = (t - A1) // 48
    return k < 80 or (k - 80) % 16 >= 8          # every A3 kind; A4 rows of wall sides


def patch_data(m):
    w, h, d = m['width'], m['height'], list(m['data'])
    changed = []
    for z in (0, 1):
        for y in range(h):
            for x in range(w):
                i = (z * h + y) * w + x
                t = d[i]
                if not is_wall(t): continue
                bits = (1 if x == 0 else 0) | (2 if y == 0 else 0) | (4 if x == w - 1 else 0) | (8 if y == h - 1 else 0)
                if not bits: continue
                shape = (t - A1) % 48
                new = shape | bits
                if new != shape:
                    d[i] = t - shape + new
                    changed.append((z, x, y))
    return d, changed


def rewrite_data_line(path, data):
    text = open(path, encoding='utf8').read()
    line = '"data":' + json.dumps(data, separators=(',', ':'))
    new, n = re.subn(r'^"data":\[[^\n]*\],?$', lambda mo: line + (',' if mo.group(0).endswith(',') else ''), text, count=1, flags=re.M)
    assert n == 1, 'no data line in ' + path
    with open(path, 'w', encoding='utf8', newline='') as f: f.write(new)


if __name__ == '__main__':
    out_dir = sys.argv[sys.argv.index('--before') + 1] if '--before' in sys.argv else None
    infos = json.load(open(L.DATA + 'MapInfos.json', encoding='utf8'))
    total = 0
    for mid, mi in enumerate(infos):
        if not mi: continue
        path = L.DATA + 'Map%03d.json' % mid
        m = json.load(open(path, encoding='utf8'))
        data, changed = patch_data(m)
        if not changed: continue
        total += len(changed)
        print('Map%03d %-34s %4d edge wall cells' % (mid, mi['name'], len(changed)))
        if out_dir:
            os.makedirs(out_dir, exist_ok=True)
            for tag, dd in (('before', m['data']), ('after', data)):
                L.render_map(m['tilesetId'], m['width'], m['height'], dd, m['events']).save(
                    os.path.join(out_dir, 'Map%03d_%s.png' % (mid, tag)))
        if '--apply' in sys.argv:
            rewrite_data_line(path, data)
    print('%d cells%s' % (total, ' written' if '--apply' in sys.argv else ' (report only)'))
