# Pack loose object pictures (any size on the 48 px grid) into RPG Maker B-E sheets (768x768), ready for the
# Tileset Wizard's "Import aset" (img/tilesets/import/<Pack>/B.png, B2.png ...).
#
# RPG Maker (and Nova Tools) select tiles within one 8-column half of a sheet, so an object up to 8 tiles wide
# goes inside one half; a wider one (up to 16) is cut at the column where the fewest opaque pixels cross and laid
# across the middle of the sheet, its left part ending at column 8 and its right part starting there - in a wide
# palette it still looks whole. Objects taller than 16 or wider than 16 tiles do not fit a sheet: they are
# returned as skipped (crop them into parts first). First-fit, biggest first; tile 0 stays empty.
#   pack([(png path, crop box in tiles or None[, True]), ...], out_dir, first=1) -> (sheets, skipped)
# A third item True keeps the crop's full size: parts of one big object then still line up when painted.
import os
from PIL import Image

T, SIDE, HALF = 48, 16, 8
RESERVED = 'tile 0'


def _load(path, crop=None, trim=True):
    im = Image.open(path).convert('RGBA')
    if crop: im = im.crop(tuple(v * T for v in crop))
    out = Image.new('RGBA', (-(-im.width // T) * T, -(-im.height // T) * T), (0, 0, 0, 0))
    out.paste(im, (0, 0))
    box = out.getchannel('A').point(lambda v: 255 if v > 8 else 0).getbbox()      # drop empty tile rows/columns
    if not box: return None
    if not trim: return out
    return out.crop((box[0] // T * T, box[1] // T * T, -(-box[2] // T) * T, -(-box[3] // T) * T))


def _crossing(im, c):
    a = im.getchannel('A').load()
    return sum(1 for y in range(im.height) if a[c * T - 1, y] > 24 and a[c * T, y] > 24)


def _spots(w, cuts):
    """Columns (on the 16-wide sheet) where an object may start."""
    if cuts != [0]: return [HALF - c for c in cuts]
    return [x for x in range(SIDE - w + 1) if x + w <= HALF or x >= HALF]


def pack(sources, out_dir, first=1, prefix='B'):
    objects, skipped = [], []
    for path, crop, *whole in sources:
        im = _load(path, crop, trim=not whole)
        if im is None: continue
        w, h = im.width // T, im.height // T
        name = os.path.basename(path) + ('' if not crop else ' %s' % (crop,))
        if w > SIDE or h > SIDE: skipped.append((name, w, h)); continue
        # cuts that split the fewest pixels first; another one when the best would cover tile 0
        cut = sorted(range(w - HALF, HALF + 1), key=lambda c: (_crossing(im, c), -c)) if w > HALF else [0]
        a = im.getchannel('A')
        empty = {(x, y) for y in range(h) for x in range(w) if not a.crop((x * T, y * T, x * T + T, y * T + T)).point(lambda v: 255 if v > 8 else 0).getbbox()}
        objects.append((name, im, w, h, cut, empty))
    objects.sort(key=lambda o: (-o[3], -o[2]))
    sheets = []                                           # [image, used grid, placed]
    for name, im, w, h, cut, empty in objects:
        spot = next((s for s in ((sh, _fit(sh[1], w, h, cut, empty)) for sh in sheets) if s[1]), None)
        if not spot:
            used = [[False] * SIDE for _ in range(SIDE)]
            used[0][0] = RESERVED                         # tile 0: empty, like every B sheet
            if not _fit(used, w, h, cut, empty): skipped.append((name, w, h)); continue   # 16x16 over tile 0
            sheets.append([Image.new('RGBA', (768, 768), (0, 0, 0, 0)), used, []])
            spot = (sheets[-1], _fit(used, w, h, cut, empty))
        sheet, (x, y) = spot
        for yy in range(y, y + h):
            for xx in range(x, x + w): sheet[1][yy][xx] = True
        sheet[0].paste(im, (x * T, y * T))
        sheet[2].append((name, x, y, w, h))
    os.makedirs(out_dir, exist_ok=True)
    out = []
    for i, (im, _, placed) in enumerate(sheets):
        n = first + i
        fname = '%s%s.png' % (prefix, n if n > 1 else '')
        im.save(os.path.join(out_dir, fname))
        out.append((fname, placed))
    return out, skipped


def _fit(used, w, h, cut, empty=()):
    # tile 0 may fall inside an object where the object itself has no pixels
    free = lambda xx, yy: not used[yy][xx] or (used[yy][xx] is RESERVED and (xx - x, yy - y) in empty)
    for y in range(SIDE - h + 1):
        for x in _spots(w, cut):
            if all(free(xx, yy) for yy in range(y, y + h) for xx in range(x, x + w)):
                return x, y
    return None
