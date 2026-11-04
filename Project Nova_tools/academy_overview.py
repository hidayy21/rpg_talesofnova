# Royal Magic Academy overview: Quillhaven, the Academy's ground floor laid out roughly as the rooms lie in the
# castle (the Great Hall west of the Entrance Hall, the Cloister Court behind it with the Lecture Wing, the Library
# and the Star Tower round it), the other floors (Upper Floor, Undercroft) in a column on the right, and the village's
# inn and apothecary beside it. Lines join every transfer to where it lands: gold for doors and archways on the same
# floor, violet for stairs between floors; green arrows lead out to the World Map.
#   python academy_overview.py            -> _work/academy_map.png
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import nova_maplib as L
import kingdom as K
from PIL import Image, ImageDraw
from kingdom_overview import maps, transfers, groups, font

TILE = 16
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '_work', 'academy_map.png')
# top-left corner of each map, in tiles
LAYOUT = {
    K.ACADEMY_TOWER: (55, 3), K.ACADEMY_CLASSES: (0, 23), K.ACADEMY_COURT: (46, 23), K.ACADEMY_LIBRARY: (88, 23),
    K.ACADEMY_DINING: (9, 57), K.ACADEMY_HALL: (49, 57),
    K.ACADEMY: (36, 88), K.QUILL_INN: (14, 95), K.QUILL_APOTHECARY: (100, 116),
    K.ACADEMY_UPPER: (132, 23), K.ACADEMY_UNDERCROFT: (132, 62),
}
OTHER_FLOORS = {K.ACADEMY_UPPER, K.ACADEMY_UNDERCROFT}
COLORS = {K.ACADEMY: (150, 200, 120), K.QUILL_INN: (226, 150, 110), K.QUILL_APOTHECARY: (120, 210, 170),
          K.ACADEMY_HALL: (240, 220, 150), K.ACADEMY_DINING: (230, 180, 120), K.ACADEMY_COURT: (190, 225, 140),
          K.ACADEMY_CLASSES: (170, 150, 230), K.ACADEMY_LIBRARY: (200, 140, 190), K.ACADEMY_TOWER: (140, 170, 240),
          K.ACADEMY_UPPER: (110, 200, 210), K.ACADEMY_UNDERCROFT: (160, 160, 170)}
SECTIONS = [((0, 0), 'Lantai Dasar - Ground Floor'), ((132, 20), 'Lantai Lain - Other Floors'), ((14, 93), 'Desa Quillhaven')]


def title(i):
    return (maps[i]['displayName'] or '').replace('Royal Magic Academy - ', '').replace('Quillhaven - ', '')


def main():
    W = max(x + maps[i]['width'] for i, (x, y) in LAYOUT.items()) + 4
    H = max(y + maps[i]['height'] for i, (x, y) in LAYOUT.items()) + 6
    TOP = 170
    img = Image.new('RGBA', (W * TILE, H * TILE + TOP), (18, 24, 38, 255))
    d = ImageDraw.Draw(img)
    px = lambda i, x, y: (int((LAYOUT[i][0] + x + 0.5) * TILE), int((LAYOUT[i][1] + y + 0.5) * TILE) + TOP)

    for i, (x, y) in LAYOUT.items():
        m = maps[i]
        pic = L.render_map(m['tilesetId'], m['width'], m['height'], m['data'], m['events'])
        pic = pic.resize((m['width'] * TILE, m['height'] * TILE), Image.LANCZOS)
        ox, oy = x * TILE, y * TILE + TOP
        img.alpha_composite(pic, (ox, oy))
        d.rectangle([ox - 3, oy - 3, ox + pic.width + 2, oy + pic.height + 2], outline=COLORS[i], width=5)

    # connections: one line per opening, drawn once for each pair of maps
    done = set()
    for i in LAYOUT:
        by_target = {}
        for (x, y, t, tx, ty) in transfers(maps[i]):
            by_target.setdefault(t, []).append((x, y, tx, ty))
        for t, pts in by_target.items():
            if t == K.WORLD:
                for g in groups([(p[0], p[1]) for p in pts]):
                    sx = sum(p[0] for p in g) / len(g); sy = sum(p[1] for p in g) / len(g)
                    w, h = maps[i]['width'], maps[i]['height']
                    dx, dy = (0, 1) if sy >= h - 1 else (0, -1) if sy <= 0 else (-1, 0) if sx <= 0 else (1, 0)
                    a = px(i, sx, sy); e = (a[0] + dx * 60, a[1] + dy * 60)
                    d.line([a, e], fill=(120, 230, 140, 255), width=6)
                    nx, ny = -dy, dx
                    d.polygon([(e[0] + dx * 16, e[1] + dy * 16), (e[0] + nx * 12, e[1] + ny * 12), (e[0] - nx * 12, e[1] - ny * 12)],
                              fill=(120, 230, 140, 255))
                    d.text((e[0] - 40 if dy else e[0] - 50 if dx < 0 else e[0] + 22, e[1] + 22 if dy > 0 else e[1] + 14),
                           'World Map', font=font(20, True), fill=(150, 240, 160))
                continue
            if t not in LAYOUT or (t, i) in done: continue
            done.add((i, t))
            stairs = i in OTHER_FLOORS or t in OTHER_FLOORS
            col = (190, 130, 255, 255) if stairs else (255, 214, 90, 255)
            for g in groups(pts):
                sx = sum(p[0] for p in g) / len(g); sy = sum(p[1] for p in g) / len(g)
                tx = sum(p[2] for p in g) / len(g); ty = sum(p[3] for p in g) / len(g)
                a, b = px(i, sx, sy), px(t, tx, ty)
                d.line([a, b], fill=(255, 255, 255, 200), width=6)
                d.line([a, b], fill=col, width=3)
                for p in (a, b):
                    d.ellipse([p[0] - 7, p[1] - 7, p[0] + 7, p[1] + 7], fill=col, outline=(20, 20, 20, 255), width=2)

    # map names
    for i, (x, y) in LAYOUT.items():
        f = font(24, True); t = '%d  %s' % (i, title(i))
        tw = d.textlength(t, font=f)
        bx, by = x * TILE + 8, y * TILE + TOP + 8
        d.rectangle([bx - 6, by - 4, bx + tw + 10, by + 32], fill=(12, 16, 28, 225), outline=COLORS[i], width=2)
        d.text((bx + 2, by), t, font=f, fill=COLORS[i])
    for (x, y), t in SECTIONS:
        d.text((x * TILE + 4, y * TILE + TOP - 44), t, font=font(30, True), fill=(240, 226, 180))

    d.text((24, 18), 'Royal Magic Academy of Nova & Quillhaven', font=font(44, True), fill=(240, 226, 180))
    lx, ly = 1250, 34
    for col, text in (((255, 214, 90), 'pintu / lorong (satu lantai)'), ((190, 130, 255), 'tangga (pindah lantai)'),
                      ((120, 230, 140), 'keluar ke World Map')):
        d.line([(lx, ly + 12), (lx + 40, ly + 12)], fill=col, width=5)
        d.text((lx + 50, ly), text, font=font(20), fill=(234, 240, 248))
        lx += 360
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    img.convert('RGB').save(OUT)
    print('saved', OUT, img.size)


if __name__ == '__main__':
    main()
