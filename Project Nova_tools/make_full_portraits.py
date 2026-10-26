# Full-body character art (white background) -> menu card portraits + transparent full-body pictures.
#   Input : D:/RPG Maker MV/Project Nova_full portrait/<Name>.(jpg|png)
#   Output: img/pictures/Portrait_<Actor>.png        480x640 card (head-to-waist, themed background)
#           img/pictures/Portrait_<Actor>_Bust.png   same crop, transparent
#           img/pictures/Full_<Actor>.png            full body, transparent, 1200 px tall
import sys, os
from collections import deque
import numpy as np
from PIL import Image, ImageFilter

sys.path.insert(0, 'D:/RPG Maker MV/Project Nova_tools')
import import_portraits as IP

SRC = 'D:/RPG Maker MV/Project Nova_full portrait/'
OUT = 'D:/RPG Maker MV/Project Nova/img/pictures/'
# Small background gaps the automatic rule can't tell from white clothing (e.g. Roland's white collar):
# seed points (x, y in the source image) whose connected near-white area is made transparent.
MANUAL_POCKETS = {
    'Mira': [(437, 333), (562, 587)],                 # left of the chin, between sleeve and dress
    'Diana': [(845, 388)],                            # between hair and cheek
    'Barion': [(681, 456), (887, 408), (928, 419), (998, 473)],   # under the chin, right of the neck
    'Kael': [(397, 1454)],                            # between hand and strap
}
# Thin white slivers (between hair strands, hair and cheek): boxes (x0, y0, x1, y1) in the source image
# where every paper-white pixel becomes transparent. Skin, eyes and cloth inside are not white, so they stay.
MANUAL_REGIONS = {
    'Yuki': [(760, 360, 822, 452)],                   # left of the chin, between hair and scarf
    'Diana': [(812, 292, 876, 425)],                  # between hair and cheek
}
ALIASES = {}                       # file name -> actor name, if they differ
# NovaMenu's portrait area at 1280x720 (4 cards). The card is rendered at 2x and reduced here with a good
# filter, so the game draws it 1:1 - the runtime canvas downscale in MV's Chromium is what made it soft.
CARD = (231, 294)
IP.W, IP.H = CARD[0] * 2, CARD[1] * 2
CARD_ASPECT = IP.W / IP.H


def cutout(img, seeds=(), regions=()):
    """White background -> transparent: flood fill from the border plus large enclosed white pockets."""
    a = np.array(img.convert('RGB')).astype(np.int16)
    h, w = a.shape[:2]
    # the backgrounds are flat paper white (>= 250); white hair/cloth is shaded, so keep the key tight
    white = (a.min(axis=2) >= 247) & ((a.max(axis=2) - a.min(axis=2)) <= 6)
    bg = np.zeros((h, w), bool)
    q = deque()
    for x in range(w):
        for y in (0, h - 1):
            if white[y, x] and not bg[y, x]: bg[y, x] = True; q.append((y, x))
    for y in range(h):
        for x in (0, w - 1):
            if white[y, x] and not bg[y, x]: bg[y, x] = True; q.append((y, x))
    while q:
        y, x = q.popleft()
        for ny, nx in ((y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1)):
            if 0 <= ny < h and 0 <= nx < w and white[ny, nx] and not bg[ny, nx]:
                bg[ny, nx] = True; q.append((ny, nx))
    # enclosed pockets (between arm and body, hair and neck...). A pocket is background when it is mostly
    # paper white AND its rim touches dark line art; highlights on hair/armour are rimmed by light colours.
    lum = a[..., 0] * 0.299 + a[..., 1] * 0.587 + a[..., 2] * 0.114
    nearwhite = (a.min(axis=2) >= 238) & ((a.max(axis=2) - a.min(axis=2)) <= 12)
    seen = bg.copy()
    min_px = int(w * h * 0.001)       # background pockets are big; armour/hair highlights are small
    removed = []
    for y in range(0, h, 2):
        for x in np.nonzero(nearwhite[y] & ~seen[y])[0]:
            if seen[y, x]: continue
            q = deque([(y, x)]); seen[y, x] = True; pts = []
            while q:
                yy, xx = q.popleft(); pts.append((yy, xx))
                for ny, nx in ((yy - 1, xx), (yy + 1, xx), (yy, xx - 1), (yy, xx + 1)):
                    if 0 <= ny < h and 0 <= nx < w and nearwhite[ny, nx] and not seen[ny, nx]:
                        seen[ny, nx] = True; q.append((ny, nx))
            if len(pts) < min_px: continue
            ys, xs = np.array(pts).T
            vals = a[ys, xs].min(axis=1)
            if (vals >= 250).mean() < 0.9: continue
            m = np.zeros((h, w), np.uint8); m[ys, xs] = 255
            ring = (np.array(Image.fromarray(m).filter(ImageFilter.MaxFilter(9))) > 0) & (m == 0)
            if np.percentile(lum[ring], 15) > 140: continue          # rimmed by light colour = highlight
            bg[ys, xs] = True; removed.append(len(pts))
    for x0, y0, x1, y1 in regions:
        box = np.zeros((h, w), bool); box[y0:y1, x0:x1] = True
        bg |= box & (a.min(axis=2) >= 232) & ((a.max(axis=2) - a.min(axis=2)) <= 20)
    for sx, sy in seeds:
        if not nearwhite[sy, sx]:                     # snap to the nearest near-white pixel
            win = nearwhite[max(0, sy - 12):sy + 13, max(0, sx - 12):sx + 13]
            ys, xs = np.nonzero(win)
            if not len(ys): continue
            k = np.argmin((ys - min(12, sy)) ** 2 + (xs - min(12, sx)) ** 2)
            sy, sx = max(0, sy - 12) + ys[k], max(0, sx - 12) + xs[k]
        q = deque([(sy, sx)]); fill = np.zeros((h, w), bool); fill[sy, sx] = True
        while q:
            yy, xx = q.popleft()
            for ny, nx in ((yy - 1, xx), (yy + 1, xx), (yy, xx - 1), (yy, xx + 1)):
                if 0 <= ny < h and 0 <= nx < w and nearwhite[ny, nx] and not fill[ny, nx]:
                    fill[ny, nx] = True; q.append((ny, nx))
        bg |= fill; removed.append(int(fill.sum()))
    cutout.last_removed = removed
    alpha = Image.fromarray(np.where(bg, 0, 255).astype(np.uint8))
    alpha = alpha.filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(0.9))
    out = img.convert('RGBA'); out.putalpha(alpha)
    return out


def head_center_x(cut, top, bot):
    a = np.array(cut.split()[3])
    band = a[top: top + max(8, (bot - top) // 10)]
    xs = np.nonzero(band.max(axis=0) > 128)[0]
    return int((xs.min() + xs.max()) / 2) if len(xs) else cut.width // 2


def bust_crop(cut):
    l, t, r, b = cut.getbbox()
    body_h = b - t
    ch = int(body_h * 0.46)                       # head to waist
    cw = int(ch * CARD_ASPECT)
    cx = head_center_x(cut, t, b)
    top = max(0, t - int(body_h * 0.025))
    box = (cx - cw // 2, top, cx - cw // 2 + cw, top + ch)
    canvas = Image.new('RGBA', (cw, ch), (0, 0, 0, 0))
    canvas.alpha_composite(cut.crop((max(0, box[0]), box[1], min(cut.width, box[2]), box[3])), (max(0, -box[0]), 0))
    return canvas


def card(name, bust):
    big = bust.resize((IP.W, IP.H), Image.LANCZOS)
    # fade the bottom edge so the waist cut isn't hard
    a = np.array(big)
    ramp = np.ones(IP.H, np.float32)
    s = int(IP.H * 0.80)
    ramp[s:] = np.linspace(1, 0, IP.H - s) ** 1.3
    a[..., 3] = (a[..., 3].astype(np.float32) * ramp[:, None]).astype(np.uint8)
    b = Image.fromarray(a, 'RGBA')
    theme = IP.THEMES.get(name, IP.DEFAULT_THEME)
    seed = {'Kael': 1, 'Yuki': 2, 'Mira': 3, 'Diana': 4, 'Roland': 5, 'Barion': 6}.get(name, 7) * 97
    c = Image.alpha_composite(IP.background(theme, seed), IP.rim(b, theme[3]))
    return IP.vignette(Image.alpha_composite(c, b)), b


if __name__ == '__main__':
    preview = []
    for f in sorted(os.listdir(SRC)):
        stem, ext = os.path.splitext(f)
        if ext.lower() not in ('.png', '.jpg', '.jpeg', '.webp'): continue
        name = ALIASES.get(stem, stem)
        cut = cutout(Image.open(SRC + f), MANUAL_POCKETS.get(stem, ()), MANUAL_REGIONS.get(stem, ()))
        full = cut.crop(cut.getbbox())
        full = full.resize((int(full.width * 1200 / full.height), 1200), Image.LANCZOS)
        full.save(OUT + 'Full_%s.png' % name)
        c, b = card(name, bust_crop(cut))
        sharpen = lambda im: im.resize(CARD, Image.LANCZOS).filter(ImageFilter.UnsharpMask(radius=0.7, percent=55, threshold=2))
        c = sharpen(c)
        bs = b.resize(CARD, Image.LANCZOS)
        bs_rgb = bs.convert('RGB').filter(ImageFilter.UnsharpMask(radius=0.7, percent=55, threshold=2)).convert('RGBA'); bs_rgb.putalpha(bs.split()[3])
        c.save(OUT + 'Portrait_%s.png' % name)
        bs_rgb.save(OUT + 'Portrait_%s_Bust.png' % name)
        preview.append((name, c, full))
        print('wrote', name)
    if len(sys.argv) > 1:
        sheet = Image.new('RGBA', (len(preview) * 250, 330 + 420), (40, 40, 40, 255))
        for i, (n, c, full) in enumerate(preview):
            sheet.alpha_composite(c.resize((240, 320), Image.LANCZOS), (i * 250, 0))
            fb = Image.new('RGBA', full.size, (255, 0, 255, 255)); fb.alpha_composite(full); fb.thumbnail((240, 410))
            sheet.alpha_composite(fb, (i * 250, 335))
        sheet.save(sys.argv[1])
