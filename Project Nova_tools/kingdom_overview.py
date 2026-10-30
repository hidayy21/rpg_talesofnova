# Kingdom overview: every outdoor district of the Royal Capital rendered and laid out as one
# navigation map, with the walk-through connections between districts, the doors into
# buildings (numbered, listed on the right) and the gates to the world map.
#   python kingdom_overview.py            -> _work/kingdom_map.png
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import nova_maplib as L
from PIL import Image, ImageDraw, ImageFont

TILE = 20                       # pixels per map tile on the overview (maps render at 48)
GAP = 7                         # tiles between districts
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '_work', 'kingdom_map.png')

# top-left corner of each district, in tiles, roughly where it lies in the city
LAYOUT = {
    26: (47, 0),                # Hearthstone Terraces (north of Lantern Row)
    7: (98, 0),                 # Castle Approach (north of the plaza)
    25: (159, 0),               # Royal Quarter (east of Castle Approach, north of the Market)
    2: (8, 49),                 # Baker's Lane (west of Lantern Row)
    5: (47, 39),                # Lantern Row / Residential Quarter (west)
    3: (98, 41),                # Grand Plaza (centre)
    4: (149, 41),               # Market District (east)
    24: (54, 102),              # Hollow Farm (outside the wall, west of the Main Gate)
    23: (100, 80),              # Main Gate (south of the plaza, outside the walls)
    6: (201, 41),               # Saltwind Harbor (east of the market, on the bay)
}
WORLD = 1
COLORS = {26: (230, 180, 200), 25: (170, 150, 230), 24: (200, 210, 110), 23: (190, 225, 140), 7: (214, 170, 90), 2: (226, 150, 110), 5: (150, 190, 120), 3: (240, 220, 150), 4: (120, 170, 230), 6: (110, 200, 210)}

infos = json.load(open(L.DATA + 'MapInfos.json', encoding='utf8'))
maps = {i: json.load(open(L.DATA + 'Map%03d.json' % i, encoding='utf8')) for i in range(1, len(infos)) if infos[i]}


def short(i):
    name = maps[i]['displayName'] or infos[i]['name']
    return name.replace('Royal Capital - ', '').replace('Nova - ', '')


def transfers(m):
    """(x, y, target map, tx, ty) for every event whose pages transfer the player."""
    out = []
    for ev in m['events']:
        if not ev: continue
        for pg in ev['pages']:
            for c in pg['list']:
                if c['code'] == 201 and c['parameters'][0] == 0:
                    out.append((ev['x'], ev['y'], c['parameters'][1], c['parameters'][2], c['parameters'][3]))
                    break
            else: continue
            break
    return out


def groups(points):
    """Split neighbouring exit tiles into separate openings."""
    left, out = list(points), []
    while left:
        g = [left.pop()]
        grown = True
        while grown:
            grown = False
            for p in left[:]:
                if any(abs(p[0] - q[0]) <= 1 and abs(p[1] - q[1]) <= 1 for q in g):
                    g.append(p); left.remove(p); grown = True
        out.append(g)
    return out


def font(size, title=False):
    path = L.PROJ + 'fonts/' + ('Cinzel.ttf' if title else 'AlegreyaSans-Regular.ttf')
    try: return ImageFont.truetype(path, size)
    except OSError: return ImageFont.load_default()


def main():
    W = max(x + maps[i]['width'] for i, (x, y) in LAYOUT.items()) + 14
    H = max(y + maps[i]['height'] for i, (x, y) in LAYOUT.items()) + 9
    LEGEND = 520
    img = Image.new('RGBA', (W * TILE + LEGEND, H * TILE + 90), (18, 24, 38, 255))
    d = ImageDraw.Draw(img)
    TOP = 90
    px = lambda i, x, y: (int((LAYOUT[i][0] + x + 0.5) * TILE), int((LAYOUT[i][1] + y + 0.5) * TILE) + TOP)

    # districts
    for i, (x, y) in LAYOUT.items():
        m = maps[i]
        pic = L.render_map(m['tilesetId'], m['width'], m['height'], m['data'], m['events'])
        pic = pic.resize((m['width'] * TILE, m['height'] * TILE), Image.LANCZOS)
        ox, oy = x * TILE, y * TILE + TOP
        img.alpha_composite(pic, (ox, oy))
        d.rectangle([ox - 2, oy - 2, ox + pic.width + 1, oy + pic.height + 1], outline=COLORS[i], width=4)

    # walk-through connections between districts, one line per opening pair
    gates, doors = [], []
    for i in LAYOUT:
        by_target = {}
        for (x, y, t, tx, ty) in transfers(maps[i]):
            if t in LAYOUT: by_target.setdefault(t, []).append((x, y, tx, ty))
            elif t == WORLD: gates.append((i, x, y))
            else: doors.append((i, x, y, t))
        for t, pts in by_target.items():
            for g in groups(pts):
                sx = sum(p[0] for p in g) / len(g); sy = sum(p[1] for p in g) / len(g)
                tx = sum(p[2] for p in g) / len(g); ty = sum(p[3] for p in g) / len(g)
                a, b = px(i, sx, sy), px(t, tx, ty)
                d.line([a, b], fill=(255, 255, 255, 230), width=5)
                d.line([a, b], fill=(240, 90, 80, 255) if ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5 > 40 * TILE else (255, 214, 90, 255), width=3)
                for p in (a, b):
                    d.ellipse([p[0] - 7, p[1] - 7, p[0] + 7, p[1] + 7], fill=(255, 214, 90, 255), outline=(20, 20, 20, 255), width=2)

    # gates to the world map: an arrow out of the map edge they sit on
    for g in groups([(x, y, i) for (i, x, y) in gates]):
        i = g[0][2]
        sx = sum(p[0] for p in g) / len(g); sy = sum(p[1] for p in g) / len(g)
        p = px(i, sx, sy)
        w, h = maps[i]['width'], maps[i]['height']
        if sy >= h - 1: dx, dy = 0, 1
        elif sy <= 0: dx, dy = 0, -1
        elif sx <= 0: dx, dy = -1, 0
        else: dx, dy = 1, 0
        end = (p[0] + dx * 70, p[1] + dy * 70)
        d.line([p, end], fill=(120, 230, 140, 255), width=6)
        nx, ny = -dy, dx
        tip = [(end[0] + dx * 16, end[1] + dy * 16), (end[0] + nx * 12, end[1] + ny * 12), (end[0] - nx * 12, end[1] - ny * 12)]
        d.polygon(tip, fill=(120, 230, 140, 255))
        d.text((end[0] + 24 if dy else end[0] - 60, end[1] - 6 if dy else end[1] + 18), 'World Map', font=font(22, True), fill=(150, 240, 160))

    # doors into buildings: numbered badges
    entries, seen = [], {}
    for (i, x, y, t) in doors:
        if t in seen: continue
        seen[t] = len(entries) + 1
        entries.append((seen[t], i, t))
        p = px(i, x, y)
        d.ellipse([p[0] - 14, p[1] - 14, p[0] + 14, p[1] + 14], fill=(255, 255, 255, 255), outline=(20, 20, 20, 255), width=3)
        n = str(seen[t])
        f = font(19, True)
        w = d.textlength(n, font=f)
        d.text((p[0] - w / 2, p[1] - 12), n, font=f, fill=(20, 20, 20))

    # every transfer tile, outlined (magenta: to another district or the World Map, cyan: a door into a building),
    # and each opening labelled with where it goes and its tile coordinates, to check against the editor
    lab = font(17)
    for i in LAYOUT:
        mw, mh = maps[i]['width'], maps[i]['height']
        by_target = {}
        for (x, y, t, tx, ty) in transfers(maps[i]):
            by_target.setdefault(t, []).append((x, y))
        for t, pts in by_target.items():
            door = t not in LAYOUT and t != WORLD
            col = (90, 220, 255) if door else (255, 80, 220)
            for (x, y) in pts:
                ox, oy = (LAYOUT[i][0] + x) * TILE, (LAYOUT[i][1] + y) * TILE + TOP
                d.rectangle([ox, oy, ox + TILE - 1, oy + TILE - 1], fill=col + (70,), outline=col + (255,), width=2)
            if door: continue
            for g in groups(pts):
                xs, ys = sorted({p[0] for p in g}), sorted({p[1] for p in g})
                span = lambda v: str(v[0]) if len(v) == 1 else '%d-%d' % (v[0], v[-1])
                text = '> %s  (x %s, y %s)' % ('World Map' if t == WORLD else short(t), span(xs), span(ys))
                tw = d.textlength(text, font=lab)
                gx0, gy0 = (LAYOUT[i][0] + xs[0]) * TILE, (LAYOUT[i][1] + ys[0]) * TILE + TOP
                gx1, gy1 = (LAYOUT[i][0] + xs[-1] + 1) * TILE, (LAYOUT[i][1] + ys[-1] + 1) * TILE + TOP
                if xs[0] == 0 and len(xs) == 1: lx_, ly_ = gx1 + 4, (gy0 + gy1) / 2 - 11
                elif xs[-1] == mw - 1 and len(xs) == 1: lx_, ly_ = gx0 - tw - 12, (gy0 + gy1) / 2 - 11
                elif ys[0] == 0: lx_, ly_ = (gx0 + gx1) / 2 - tw / 2, gy1 + 4
                elif ys[-1] == mh - 1: lx_, ly_ = (gx0 + gx1) / 2 - tw / 2, gy0 - 28
                else: lx_, ly_ = gx1 + 4, (gy0 + gy1) / 2 - 11
                d.rectangle([lx_ - 4, ly_, lx_ + tw + 4, ly_ + 22], fill=(12, 16, 28, 225), outline=(255, 80, 220, 255), width=1)
                d.text((lx_, ly_), text, font=lab, fill=(255, 210, 245))

    # district names
    for i, (x, y) in LAYOUT.items():
        f = font(30, True)
        t = short(i)
        tw = d.textlength(t, font=f)
        bx, by = x * TILE + 10, y * TILE + TOP + 10
        d.rectangle([bx - 6, by - 4, bx + tw + 10, by + 40], fill=(12, 16, 28, 220), outline=COLORS[i], width=2)
        d.text((bx + 2, by), t, font=f, fill=COLORS[i])

    # title and legend
    d.text((24, 20), 'Royal Capital of Nova', font=font(44, True), fill=(240, 226, 180))
    lx = W * TILE + 30
    d.text((lx, TOP), 'Buildings', font=font(30, True), fill=(240, 226, 180))
    y = TOP + 50
    for n, i, t in entries:
        sub = [j for j in range(1, len(infos)) if infos[j] and infos[j]['parentId'] == t]
        d.ellipse([lx, y + 2, lx + 26, y + 28], fill=(255, 255, 255), outline=(20, 20, 20), width=2)
        f = font(17, True); w = d.textlength(str(n), font=f)
        d.text((lx + 13 - w / 2, y + 3), str(n), font=f, fill=(20, 20, 20))
        d.text((lx + 38, y), short(t), font=font(22), fill=(234, 240, 248))
        d.text((lx + 38, y + 26), 'in ' + short(i) + (' - also ' + ', '.join(short(j).split(' - ')[-1] for j in sub) if sub else ''),
               font=font(17), fill=(150, 165, 190))
        y += 62
    y += 20
    d.text((lx, y), 'Lines', font=font(30, True), fill=(240, 226, 180)); y += 48
    for col, text in [((255, 80, 220), 'transfer tile (label: target, x/y)'), ((90, 220, 255), 'door tile (into a building)'),
                      ((255, 214, 90), 'walk-through between districts'), ((240, 90, 80), 'long jump: the two ends do not\n  sit next to each other'),
                      ((120, 230, 140), 'gate to the world map')]:
        d.line([(lx, y + 14), (lx + 40, y + 14)], fill=col, width=5)
        d.multiline_text((lx + 52, y), text, font=font(20), fill=(234, 240, 248))
        y += 58

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    img.convert('RGB').save(OUT)
    print('saved', OUT, img.size)


if __name__ == '__main__':
    main()
