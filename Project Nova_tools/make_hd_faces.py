# Turns an HD face-sheet image (any format, white background, same 4x2 layout as the game sheet)
# into a transparent PNG in Project Nova_hd_faces/<Name>_HD.png (the game itself uses the 144px sheet).
#
#   python make_hd_faces.py [Actor4] [path/to/Actor4_HD.jpg]
#
# Silhouette: for faces that line up with the normal sheet (img/faces/<Name>.png) its alpha is used as the
# matte - this keeps near-white parts (white hair, light scarves) that a colour key would eat. Faces that
# were redrawn (they don't line up) get a white-background flood fill instead.
import os, sys
from collections import deque
import numpy as np
from PIL import Image, ImageFilter

PROJ = 'D:/RPG Maker MV/Project Nova/'
name = sys.argv[1] if len(sys.argv) > 1 else 'Actor4'
HD_DIR = 'D:/RPG Maker MV/Project Nova_hd_faces/'   # HD masters live outside the project
src_path = sys.argv[2] if len(sys.argv) > 2 else HD_DIR + '%s_HD.jpg' % name
out_path = HD_DIR + '%s_HD.png' % name

hd = Image.open(src_path).convert('RGB')
lo = Image.open(PROJ + 'img/faces/%s.png' % name).convert('RGBA')
cw, ch = hd.width // 4, hd.height // 2
out = Image.new('RGBA', (cw * 4, ch * 2), (0, 0, 0, 0))


def flood_white(cell, tol=14):
    a = np.array(cell).astype(np.int16)
    h, w = a.shape[:2]
    close = (255 - a.min(axis=2)) <= tol
    mask = np.zeros((h, w), bool)
    q = deque()
    for x in range(w):
        for y in (0, h - 1):
            if close[y, x] and not mask[y, x]: mask[y, x] = True; q.append((y, x))
    for y in range(h):
        for x in (0, w - 1):
            if close[y, x] and not mask[y, x]: mask[y, x] = True; q.append((y, x))
    while q:
        y, x = q.popleft()
        for ny, nx in ((y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1)):
            if 0 <= ny < h and 0 <= nx < w and close[ny, nx] and not mask[ny, nx]:
                mask[ny, nx] = True; q.append((ny, nx))
    return mask


def enclosed_white(a_cell, bg, min_px):
    """Pure-white regions not connected to the background, larger than min_px, grown into their light edge."""
    white = (a_cell.min(axis=2) >= 238) & ((a_cell.max(axis=2) - a_cell.min(axis=2)) <= 14) & ~bg
    h, w = white.shape
    seen = np.zeros((h, w), bool)
    out = np.zeros((h, w), bool)
    for y in range(h):
        for x in range(w):
            if not white[y, x] or seen[y, x]: continue
            q = deque([(y, x)]); seen[y, x] = True; pts = []
            while q:
                yy, xx = q.popleft(); pts.append((yy, xx))
                for ny, nx in ((yy - 1, xx), (yy + 1, xx), (yy, xx - 1), (yy, xx + 1)):
                    if 0 <= ny < h and 0 <= nx < w and white[ny, nx] and not seen[ny, nx]:
                        seen[ny, nx] = True; q.append((ny, nx))
            if len(pts) >= min_px:
                ys, xs = zip(*pts); out[list(ys), list(xs)] = True
    light = (a_cell.min(axis=2) >= 215) & ((a_cell.max(axis=2) - a_cell.min(axis=2)) <= 26)
    for _ in range(4):   # include the anti-aliased light rim around each pocket
        grown = np.array(Image.fromarray((out * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(3))) > 0
        out |= grown & light
    return out


for i in range(8):
    cx, cy = (i % 4) * cw, (i // 4) * ch
    cell = hd.crop((cx, cy, cx + cw, cy + ch))
    lcell = lo.crop(((i % 4) * 144, (i // 4) * 144, (i % 4) * 144 + 144, (i // 4) * 144 + 144))
    la = np.array(lcell)
    if (la[..., 3] > 0).sum() < 50 and (255 - np.array(cell).min(axis=2) > 20).sum() < 500:
        continue  # empty slot

    # does this HD face line up with the game sheet? (small search over offsets)
    l = la.astype(np.float32); m = l[..., 3] > 250
    best = (1e9, 0, 0)
    if m.sum() > 200:
        for dx in range(-10, 11, 2):
            for dy in range(-10, 11, 2):
                s = np.array(cell.crop((dx, dy, dx + cw, dy + ch)).resize((144, 144), Image.LANCZOS)).astype(np.float32)
                d = np.abs(s - l[..., :3])[m].mean()
                if d < best[0]: best = (d, dx, dy)
    a_cell = np.array(cell).astype(np.float32)
    whiteness = np.clip((a_cell.min(axis=2) - 235) / 20.0, 0, 1)   # 1 = pure white
    if best[0] < 20:
        # matte from the game sheet, upscaled and shifted onto the HD cell
        up = lcell.split()[3].resize((cw, ch), Image.LANCZOS)
        matte = Image.new('L', (cw, ch), 0); matte.paste(up, (-best[1], -best[2]))
        alpha = np.array(matte).astype(np.float32) / 255
        alpha = np.where(alpha < 0.97, alpha * (1 - whiteness), alpha)   # trim white fringe on the soft edge
        how = 'matte from %s.png (offset %d,%d)' % (name, best[1], best[2])
    else:
        bg = flood_white(cell)
        # White background trapped between hair and neck/collar is not reached by the flood fill:
        # remove large enclosed pure-white areas too (eye whites and collar lace are far smaller).
        pockets = enclosed_white(a_cell, bg, min_px=int(cw * ch * 0.008))
        bg |= pockets
        alpha = (~bg).astype(np.float32)
        alpha = np.array(Image.fromarray((alpha * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.8))).astype(np.float32) / 255
        how = 'white-background key (redrawn face), %d enclosed white px removed' % int(pockets.sum())
    # leftover white fringe: near-white, mostly transparent pixels on the silhouette edge
    alpha = np.where((alpha < 0.5) & (whiteness > 0.5), 0, alpha)
    rgba = np.dstack([a_cell, alpha * 255]).clip(0, 255).astype(np.uint8)
    out.paste(Image.fromarray(rgba, 'RGBA'), (cx, cy))
    print('face %d: %s' % (i, how))

out.save(out_path)
print('wrote', out_path, out.size)
