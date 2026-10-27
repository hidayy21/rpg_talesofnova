# Turns AI-generated character art into menu portraits for Project Nova.
#
#   Input : D:/RPG Maker MV/Project Nova_portraits_src/<ActorName>.png  (any size, white or transparent background)
#   Output: <project>/img/pictures/Portrait_<ActorName>.png        480x640 card: themed background + character
#           <project>/img/pictures/Portrait_<ActorName>_Bust.png   480x640 character only (transparent)
#
# Usage:  python import_portraits.py            -> every actor that has a source image
#         python import_portraits.py Kael Yuki  -> only these
#         python import_portraits.py --out DIR  -> write somewhere else (for previews)
import json, math, os, random, sys
from collections import deque
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

PROJ = 'D:/RPG Maker MV/Project Nova/'
SRC = 'D:/RPG Maker MV/Project Nova_portraits_src/'
W, H = 480, 640

THEMES = {
    'Kael':   ((14, 8, 26), (58, 22, 74), (255, 120, 60), (170, 90, 255), 'embers'),
    'Yuki':   ((8, 18, 38), (40, 90, 150), (190, 235, 255), (120, 200, 255), 'snow'),
    'Mira':   ((16, 10, 40), (70, 45, 130), (255, 220, 150), (240, 150, 220), 'stars'),
    'Diana':  ((6, 24, 16), (30, 92, 60), (200, 255, 170), (120, 200, 110), 'leaves'),
    'Roland': ((30, 18, 6), (120, 80, 20), (255, 230, 150), (90, 140, 255), 'rays'),
    'Barion': ((30, 8, 6), (120, 40, 20), (255, 170, 90), (255, 90, 40), 'sparks'),
    'Lysandre': ((22, 6, 20), (96, 22, 60), (255, 150, 190), (210, 50, 110), 'embers'),
}
DEFAULT_THEME = ((10, 16, 30), (40, 60, 100), (200, 230, 255), (120, 180, 255), 'stars')


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def remove_background(img, tol=28):
    """Flood-fills the near-white/near-uniform background from the image border and makes it transparent."""
    img = img.convert('RGBA')
    a = np.array(img)
    if (a[..., 3] < 250).mean() > 0.05:   # already has transparency
        return img
    h, w = a.shape[:2]
    rgb = a[..., :3].astype(np.int16)
    corners = np.array([rgb[0, 0], rgb[0, -1], rgb[-1, 0], rgb[-1, -1]])
    bg = np.median(corners, axis=0)
    close = (np.abs(rgb - bg).max(axis=2) <= tol)
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
    alpha = Image.fromarray(np.where(mask, 0, 255).astype(np.uint8), 'L')
    alpha = alpha.filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(0.8))  # soften the cut edge
    img.putalpha(alpha)
    return img


def bust(src):
    """Scales the character to the card width, head near the top, and fades out the bottom edge."""
    box = src.getbbox() or (0, 0, src.width, src.height)
    char = src.crop(box)
    scale = (W * 1.02) / char.width
    if char.height * scale < H * 0.75:            # very wide art: fit by height instead
        scale = (H * 0.95) / char.height
    char = char.resize((max(1, int(char.width * scale)), max(1, int(char.height * scale))), Image.LANCZOS)
    a = np.array(char)
    ch = a.shape[0]
    visible = min(ch, H - 12)
    start = int(visible * 0.75)
    ramp = np.ones(ch, np.float32)
    ramp[start:visible] = np.linspace(1, 0, visible - start) ** 1.4
    ramp[visible:] = 0
    a[..., 3] = (a[..., 3].astype(np.float32) * ramp[:, None]).astype(np.uint8)
    canvas = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    canvas.alpha_composite(Image.fromarray(a, 'RGBA'), ((W - a.shape[1]) // 2, 12))
    return canvas


def background(theme, seed):
    dark, mid, light, accent, motif = theme
    rnd = random.Random(seed)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    t = np.clip((xx / W * 0.45 + (1 - yy / H) * 0.55), 0, 1)
    img = np.zeros((H, W, 3), np.float32)
    for c in range(3):
        img[..., c] = dark[c] + (mid[c] - dark[c]) * t
    d = np.sqrt(((xx - W * 0.52) / (W * 0.55)) ** 2 + ((yy - H * 0.36) / (H * 0.42)) ** 2)
    glow = np.clip(1 - d, 0, 1) ** 2 * 0.55
    for c in range(3):
        img[..., c] = img[..., c] * (1 - glow) + light[c] * glow
    base = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8), 'RGB').convert('RGBA')

    streaks = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(streaks)
    for _ in range(7):
        x0, wdt, al = rnd.randint(-W, W), rnd.randint(10, 40), rnd.randint(14, 34)
        sd.polygon([(x0, H), (x0 + wdt, H), (x0 + wdt + H * 0.55, 0), (x0 + H * 0.55, 0)], fill=light + (al,))
    base = Image.alpha_composite(base, streaks.filter(ImageFilter.GaussianBlur(3)))

    fx = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    fd = ImageDraw.Draw(fx)
    k = W / 288.0
    if motif in ('embers', 'snow', 'stars'):
        for _ in range(int(90 * k)):
            x, y, r = rnd.uniform(0, W), rnd.uniform(0, H), rnd.uniform(0.8, 2.6) * k
            col = {'embers': lerp(light, accent, rnd.random()), 'snow': (235, 248, 255), 'stars': (255, 245, 230)}[motif]
            fd.ellipse([x - r, y - r, x + r, y + r], fill=col + (rnd.randint(80, 220),))
    elif motif == 'leaves':
        for _ in range(int(30 * k)):
            x, y, s, ang = rnd.uniform(0, W), rnd.uniform(0, H), rnd.uniform(3, 7) * k, rnd.uniform(0, math.pi)
            pts = [(x + s * math.cos(ang), y + s * math.sin(ang)), (x + s * .4 * math.cos(ang + 1.57), y + s * .4 * math.sin(ang + 1.57)),
                   (x - s * math.cos(ang), y - s * math.sin(ang)), (x - s * .4 * math.cos(ang + 1.57), y - s * .4 * math.sin(ang + 1.57))]
            fd.polygon(pts, fill=lerp(accent, light, rnd.random()) + (rnd.randint(90, 190),))
    elif motif == 'rays':
        cx, cy = W * 0.5, -H * 0.15
        for j in range(14):
            ang = math.pi * (0.15 + 0.7 * j / 13)
            x1, y1 = cx + math.cos(ang) * H * 1.6, cy + math.sin(ang) * H * 1.6
            fd.polygon([(cx, cy), (x1 - 22, y1), (x1 + 22, y1)], fill=light + (26,))
    elif motif == 'sparks':
        for _ in range(int(45 * k)):
            x, y, l, ang = rnd.uniform(0, W), rnd.uniform(H * .15, H), rnd.uniform(4, 12) * k, rnd.uniform(-2.2, -0.9)
            fd.line([x, y, x + l * math.cos(ang), y + l * math.sin(ang)], fill=lerp(light, accent, rnd.random()) + (rnd.randint(110, 230),), width=2)
    base = Image.alpha_composite(base, fx.filter(ImageFilter.GaussianBlur(0.8)))
    return Image.alpha_composite(base, fx)


def rim(b, color):
    grown = b.split()[3].filter(ImageFilter.MaxFilter(7)).filter(ImageFilter.GaussianBlur(7))
    glow = Image.new('RGBA', (W, H), color + (0,))
    glow.putalpha(grown.point(lambda v: int(v * 0.7)))
    return glow


def vignette(img):
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    d = np.sqrt(((xx - W / 2) / (W * 0.62)) ** 2 + ((yy - H * 0.45) / (H * 0.62)) ** 2)
    shade = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    shade.putalpha(Image.fromarray((np.clip(d - 0.55, 0, 1) * 0.9 * 255).astype(np.uint8), 'L'))
    return Image.alpha_composite(img, shade)


def main():
    args = sys.argv[1:]
    out = PROJ + 'img/pictures/'
    if '--out' in args:
        i = args.index('--out'); out = args[i + 1].rstrip('/\\') + '/'; del args[i:i + 2]
    os.makedirs(out, exist_ok=True)
    actors = [a for a in json.load(open(PROJ + 'data/Actors.json', encoding='utf8')) if a]
    done = 0
    for a in actors:
        name = a['name']
        if args and name not in args: continue
        path = next((SRC + name + ext for ext in ('.png', '.jpg', '.jpeg', '.webp') if os.path.exists(SRC + name + ext)), None)
        if not path:
            print('skip %-7s (no %s<name>.png)' % (name, SRC)); continue
        theme = THEMES.get(name, DEFAULT_THEME)
        b = bust(remove_background(Image.open(path)))
        card = Image.alpha_composite(background(theme, a['id'] * 97), rim(b, theme[3]))
        card = vignette(Image.alpha_composite(card, b))
        card.save(out + 'Portrait_%s.png' % name)
        b.save(out + 'Portrait_%s_Bust.png' % name)
        print('wrote Portrait_%s.png from %s' % (name, os.path.basename(path)))
        done += 1
    print('%d portrait(s) updated.' % done)


if __name__ == '__main__':
    main()
