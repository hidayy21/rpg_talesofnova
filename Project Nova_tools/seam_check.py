# Finds cut-off objects on a map: a B-E / extra-sheet tile whose picture runs off one of its edges (trees, houses,
# beds...) must have, in the cell on that side, the tile that sits next to it on the sheet. Anything else means the
# object was cut (a missing crown row, a neighbour's crown drawn over it, the wrong half of a pair).
#   python seam_check.py 31            -> list of cuts on Map031
#   python seam_check.py 31 out.png    -> also an image with the cuts marked in red
#   python seam_check.py PM_Forest 37  -> every tile of the object that tile belongs to (crown, trunk, shadow), by row
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import nova_maplib as L

EDGE_MIN = 8            # pixels along an edge that count as "the picture goes on"
ALPHA_MIN = 40          # low enough for the half-transparent shadows under trees
SIDES = {'up': (0, -1), 'down': (0, 1), 'left': (-1, 0), 'right': (1, 0)}
_EDGES = {}


def sheet_of(tid, sets):
    """(image, base id, n) for an object tile, None for autotiles / empty."""
    if tid >= L.EXT_BASE:
        slot, n = divmod(tid - L.EXT_BASE, L.EXT_SPAN)
        s = L.ext_sheets().get(slot)
        return (L._img(L.PROJ + 'img/tilesets/%s.png' % s[0]), tid - n, n) if s else None
    if 0 < tid < L.A5:
        return sets[5 + tid // 256], tid - tid % 256, tid % 256
    return None


def edges(tid, sets):
    """Which sides of the tile's picture reach the tile border."""
    if tid not in _EDGES:
        sh = sheet_of(tid, sets)
        out = set()
        if sh and sh[0] is not None:
            img, _, n = sh
            sx, sy = ((n // 128) * 8 + n % 8) * 48, ((n % 128) // 8) * 48
            a = img.crop((sx, sy, sx + 48, sy + 48)).getchannel('A')
            px = a.load()
            on = lambda x, y: px[x, y] > ALPHA_MIN
            cnt = {'up': sum(on(i, 0) for i in range(48)), 'down': sum(on(i, 47) for i in range(48)),
                   'left': sum(on(0, i) for i in range(48)), 'right': sum(on(47, i) for i in range(48))}
            out = {k for k, v in cnt.items() if v >= EDGE_MIN}
        _EDGES[tid] = out
    return _EDGES[tid]


def partner(tid, side):
    """The tile next to tid on its sheet in that direction (None off the sheet)."""
    n = tid % L.EXT_SPAN if tid >= L.EXT_BASE else tid % 256
    base = tid - n
    col, row = (n // 128) * 8 + n % 8, (n % 128) // 8
    dx, dy = SIDES[side]
    col, row = col + dx, row + dy
    if not (0 <= col < 16 and 0 <= row < 16): return None
    return base + (col // 8) * 128 + row * 8 + col % 8


def check(mp):
    w, h, data = mp['width'], mp['height'], mp['data']
    sets = L.tileset_images(mp['tilesetId'])
    at = lambda x, y: {data[(l * h + y) * w + x] for l in (2, 3)} if 0 <= x < w and 0 <= y < h else None
    cuts = []
    for l in (2, 3):
        for y in range(h):
            for x in range(w):
                tid = data[(l * h + y) * w + x]
                for side in edges(tid, sets):
                    dx, dy = SIDES[side]
                    there = at(x + dx, y + dy)
                    if there is None: continue                      # runs off the map: fine
                    want = partner(tid, side)
                    if want is None or want in there: continue      # nothing on the sheet beyond that edge
                    cuts.append((x, y, l, tid, side, want))
    return cuts


def group(sheet, n, tileset_id=2):
    """Every tile of the object tile n of an extra sheet belongs to: follows the picture across tile borders.
    Returns rows of tile numbers (None where the object has no tile), ready for an object dict."""
    base, sets = L.ext(sheet, 0), L.tileset_images(tileset_id)
    seen, todo = {n}, [n]
    while todo:
        t = todo.pop()
        for side in edges(base + t, sets):
            p = partner(base + t, side)
            if p is not None and p - base not in seen:
                seen.add(p - base); todo.append(p - base)
        for side in SIDES:                                  # the far side of a border the neighbour runs across
            p = partner(base + t, side)
            opp = {'up': 'down', 'down': 'up', 'left': 'right', 'right': 'left'}[side]
            if p is not None and p - base not in seen and opp in edges(p, sets):
                seen.add(p - base); todo.append(p - base)
    pos = {t: ((t // 128) * 8 + t % 8, (t % 128) // 8) for t in seen}
    c0, c1 = min(c for c, _ in pos.values()), max(c for c, _ in pos.values())
    r0, r1 = min(r for _, r in pos.values()), max(r for _, r in pos.values())
    at = {p: t for t, p in pos.items()}
    return [tuple(at.get((c, r)) for c in range(c0, c1 + 1)) for r in range(r0, r1 + 1)]


def name(tid):
    if tid >= L.EXT_BASE:
        slot, n = divmod(tid - L.EXT_BASE, L.EXT_SPAN)
        return '%s:%d' % (L.ext_sheets()[slot][0], n)
    return '%s:%d' % ('BCDE'[tid // 256], tid % 256)


if __name__ == '__main__':
    if not sys.argv[1].isdigit():
        for row in group(sys.argv[1], int(sys.argv[2])): print(row)
        sys.exit()
    mid = int(sys.argv[1])
    mp = json.load(open(L.DATA + 'Map%03d.json' % mid, encoding='utf8'))
    cuts = check(mp)
    from collections import Counter
    print(len(cuts), 'cut edges')
    for (t, s), c in sorted(Counter((name(c[3]), c[4]) for c in cuts).items(), key=lambda kv: -kv[1]):
        print('  %-22s %-5s x%d' % (t, s, c))
    if len(sys.argv) > 2:
        from PIL import ImageDraw
        img = L.render_map(mp['tilesetId'], mp['width'], mp['height'], mp['data'], mp['events'])
        d = ImageDraw.Draw(img)
        for x, y, l, tid, side, _ in cuts:
            x0, y0 = x * 48, y * 48
            seg = {'up': (x0, y0, x0 + 47, y0), 'down': (x0, y0 + 47, x0 + 47, y0 + 47),
                   'left': (x0, y0, x0, y0 + 47), 'right': (x0 + 47, y0, x0 + 47, y0 + 47)}[side]
            d.line(seg, fill=(255, 0, 0, 255), width=4)
        img.save(sys.argv[2])
