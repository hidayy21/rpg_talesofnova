"""Villa Bloodrose - full plan: every map of the villa (outside, both floors and the three levels below) drawn from
the saved MapXXX.json files, with the doors, stairs and ladders between them.
    python3 villa_full_plan.py [out.png]      (default: _work/samples/villa_bloodrose_full.png)
Run it again after changing a villa map to refresh the plan."""
import json, sys, os
from PIL import Image, ImageDraw, ImageFont
from nova_maplib import render_map

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, '..', 'data')
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, '_work', 'samples', 'villa_bloodrose_full.png')
S = 0.3                      # 48 px tile -> 14.4 px
T = 48 * S
W, H = 1960, 3420

BG, PANEL, EDGE = (32, 29, 42), (38, 35, 50), (80, 76, 100)
TXT, SEC = (240, 226, 190), (200, 180, 230)
RED, PINK, GOLD = (230, 60, 70), (255, 140, 200), (250, 170, 60)


def font(size, bold=False):
    for p in (['/System/Library/Fonts/Supplemental/Arial Bold.ttf', 'C:/Windows/Fonts/arialbd.ttf'] if bold else
              ['/System/Library/Fonts/Supplemental/Arial.ttf', 'C:/Windows/Fonts/arial.ttf']):
        if os.path.exists(p): return ImageFont.truetype(p, size)
    return ImageFont.load_default()


F_TITLE, F_SEC, F_LBL, F_BADGE = font(30, True), font(26, True), font(15), font(15, True)

# sections: (title, y0, y1)
SECTIONS = [('LANTAI 2', 70, 1010), ('LANTAI 1', 1025, 1820), ('LUAR', 1835, 2640),
            ('BAWAH TANAH  (dungeon: B1 Cellars, B2 Old Foundations, B3 Rose Way)', 2655, 3400)]
CX = 760
# map id -> top-left on the plan
POS = {
    52: (CX - 108, 140), 51: (CX - 195, 360),
    58: (150, 500), 57: (1000, 520), 59: (1190, 520), 60: (1365, 520),
    55: (40, 800), 50: (CX - 223, 760), 56: (1110, 800),
    61: (CX - 223, 1085),
    53: (150, 1505), 49: (CX - 223, 1490), 54: (1110, 1505),
    48: (CX - 317, 1895),
    62: (40, 2745), 63: (740, 2745), 64: (1480, 2745),
}
# links drawn as lettered badges at both ends instead of a long line across other maps
BADGES = {(61, 62): 'A', (48, 64): 'B', (64, 48): 'B', (62, 63): 'C', (63, 62): 'C', (63, 64): 'D', (64, 63): 'D'}
NOTES = {'A': 'A  Ballroom trapdoor  ->  B1 Cellars (switch 13, sekali jalan)',
         'B': 'B  Rose slab di taman  <->  B3 Rose Way (switch 15)',
         'C': 'C  Tangga B1 Cellars  <->  B2 Old Foundations',
         'D': 'D  Sealed Gate B2  <->  B3 Rose Way (setelah gerbang terbuka)'}

infos = json.load(open(os.path.join(DATA, 'MapInfos.json'), encoding='utf8'))
maps = {i: json.load(open(os.path.join(DATA, 'Map%03d.json' % i), encoding='utf8')) for i in POS}

img = Image.new('RGB', (W, H), BG)
d = ImageDraw.Draw(img, 'RGBA')
d.text((30, 18), 'Villa Bloodrose  -  denah lengkap', font=F_TITLE, fill=(255, 255, 255))
for title, y0, y1 in SECTIONS:
    d.rectangle([20, y0, W - 20, y1], fill=PANEL, outline=EDGE, width=2)
    d.text((34, y0 + 8), title, font=F_SEC, fill=SEC)

for i, (x, y) in POS.items():
    m = maps[i]
    im = render_map(m['tilesetId'], m['width'], m['height'], m['data'], m['events']).convert('RGB')
    im = im.resize((round(m['width'] * T), round(m['height'] * T)), Image.LANCZOS)
    d.rectangle([x - 4, y - 4, x + im.width + 3, y + im.height + 3], fill=(10, 10, 14), outline=(150, 150, 170))
    img.paste(im, (x, y))
    name = infos[i]['name'].replace('Villa Bloodrose - ', '')
    d.text((x, y - 24), 'Map%03d  %s' % (i, name), font=F_LBL, fill=TXT)


def at(i, tx, ty):
    x, y = POS[i]
    return x + (tx + 0.5) * T, y + (ty + 0.5) * T


# collect links: one per source event and destination (wide exits are several events -> keep the first)
links, seen = [], set()
for i, m in maps.items():
    for e in m['events']:
        if not e: continue
        for p in e['pages']:
            for c in p['list']:
                if c['code'] != 201 or c['parameters'][0] != 0: continue
                dst, dx, dy = c['parameters'][1:4]
                if dst not in POS: continue
                key = (i, dst, dx, dy)
                if key in seen: continue
                seen.add(key)
                sw = p['conditions']['switch1Id'] if p['conditions']['switch1Valid'] else 0
                links.append((i, e['x'], e['y'], dst, dx, dy, sw))

drawn = set()
for i, sx, sy, dst, dx, dy, sw in links:
    a, b = at(i, sx, sy), at(dst, dx, dy)
    if (i, dst) in BADGES:
        # a badge on the door itself; on the arrival point too only when there is no way back
        if (i, dst) in drawn: continue
        drawn.add((i, dst))
        pts = (a,) if any(l[0] == dst and l[3] == i for l in links) else (a, b)
        for pt in pts:
            r = 13
            d.ellipse([pt[0] - r, pt[1] - r, pt[0] + r, pt[1] + r], fill=GOLD, outline=(40, 20, 0), width=2)
            d.text(pt, BADGES[(i, dst)], font=F_BADGE, fill=(40, 20, 0), anchor='mm')
        continue
    col = PINK if sw else RED
    d.line([a, b], fill=col + (220,), width=3)
    for pt in (a, b):
        d.ellipse([pt[0] - 5, pt[1] - 5, pt[0] + 5, pt[1] + 5], fill=col)

# legend
lx, ly = W - 560, 90
d.rectangle([lx, ly, W - 40, ly + 210], fill=(26, 24, 34), outline=EDGE)
d.line([lx + 16, ly + 22, lx + 56, ly + 22], fill=RED, width=3)
d.text((lx + 66, ly + 13), 'pintu / celah / tangga', font=F_LBL, fill=TXT)
d.line([lx + 16, ly + 48, lx + 56, ly + 48], fill=PINK, width=3)
d.text((lx + 66, ly + 39), 'terbuka setelah switch (12 = pintu ballroom)', font=F_LBL, fill=TXT)
for k, (letter, note) in enumerate(sorted(NOTES.items())):
    cy = ly + 76 + k * 30
    d.ellipse([lx + 24, cy - 11, lx + 46, cy + 11], fill=GOLD)
    d.text((lx + 35, cy), letter, font=F_BADGE, fill=(40, 20, 0), anchor='mm')
    d.text((lx + 66, cy - 9), note[3:], font=F_LBL, fill=TXT)

os.makedirs(os.path.dirname(OUT), exist_ok=True)
img.save(OUT)
print('saved', OUT, img.size)
