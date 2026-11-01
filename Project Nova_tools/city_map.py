# Wayfinding in the Royal Capital: the city map picture shown by the map board in the Grand Plaza, and the signboard in
# front of the Ashveil house on Ember Lane.
#   python city_map.py            -> img/pictures/Nova_CityMap.png only (safe while RPG Maker MV is open)
#   python city_map.py --save     -> also the two boards on Map003 / Map005 (RPG Maker MV must be closed)
# Rerun after changing a district map: the picture is rendered from the maps themselves.
import sys, json
import nova_maplib as L
from nova_maplib import page, cmd, text
from PIL import Image, ImageDraw, ImageFilter
import kingdom as K
import kingdom_overview as O
import prologue as P

OUT = L.PROJ + 'img/pictures/Nova_CityMap.png'
PICTURE, PIC_ID = 'Nova_CityMap', 50
SIZE = (1280, 720)
BOARD = (18, 25)                    # Grand Plaza: west side of the road in from the Main Gate
HOME_SIGN = (13, 44)                # Ember Lane, in front of the Ashveil house (door 11,43)
SIGNPOST, NOTICE_BOARD = 73, 74     # Outside_B
TAG = '<citymap>'
INK, GOLD, TEXT, DIM, STEEL = (11, 17, 32), (232, 207, 143), (234, 240, 248), (159, 177, 201), (156, 192, 236)
# streets worth naming on the map: (district, x, y, name)
STREETS = [(K.RESIDENTIAL, 26, 45.5, 'Ember Lane')]


def diamond(d, cx, cy, r, fill):
    d.polygon([(cx, cy - r), (cx + r, cy), (cx, cy + r), (cx - r, cy)], fill=fill)


def render():
    img = Image.new('RGBA', SIZE, INK + (255,))
    d = ImageDraw.Draw(img)
    for y in range(SIZE[1]):                     # night-blue backdrop, as in the menus
        t = y / SIZE[1]
        d.line([(0, y), (SIZE[0], y)], fill=(int(14 + 10 * (1 - abs(t - 0.5) * 2)), int(20 + 14 * (1 - abs(t - 0.5) * 2)),
                                              int(38 + 22 * (1 - abs(t - 0.5) * 2)), 255))
    # header: title in Cinzel over a rule with a diamond
    d.text((32, 16), 'ROYAL CAPITAL OF NOVA', font=O.font(34, True), fill=TEXT)
    d.text((34, 58), 'Map of the city', font=O.font(19), fill=DIM)
    d.line([(32, 86), (620, 86)], fill=STEEL, width=1)
    diamond(d, 32, 86, 5, STEEL)

    # the districts, scaled to fit the map area, at their place in the city (kingdom_overview.LAYOUT)
    area = (28, 104, 930, 580)
    x0 = min(x for x, y in O.LAYOUT.values()); y0 = min(y for x, y in O.LAYOUT.values())
    x1 = max(x + O.maps[i]['width'] for i, (x, y) in O.LAYOUT.items())
    y1 = max(y + O.maps[i]['height'] for i, (x, y) in O.LAYOUT.items())
    s = min(area[2] / (x1 - x0), area[3] / (y1 - y0))
    ox = area[0] + (area[2] - (x1 - x0) * s) / 2; oy = area[1] + (area[3] - (y1 - y0) * s) / 2
    px = lambda i, x, y: (ox + (O.LAYOUT[i][0] - x0 + x + 0.5) * s, oy + (O.LAYOUT[i][1] - y0 + y + 0.5) * s)

    # roads between districts first, so the districts sit on top of their ends
    links, gates, doors = set(), [], []
    for i in O.LAYOUT:
        by_target = {}
        for (x, y, t, tx, ty) in O.transfers(O.maps[i]):
            if t in O.LAYOUT: by_target.setdefault(t, []).append((x, y, tx, ty))
            elif t == O.WORLD: gates.append((i, x, y))
            else: doors.append((i, x, y, t))
        for t, pts in by_target.items():
            for g in O.groups(pts):
                a = px(i, sum(p[0] for p in g) / len(g), sum(p[1] for p in g) / len(g))
                b = px(t, sum(p[2] for p in g) / len(g), sum(p[3] for p in g) / len(g))
                key = tuple(sorted([(round(a[0] / 8), round(a[1] / 8)), (round(b[0] / 8), round(b[1] / 8))]))
                if key in links: continue
                links.add(key)
                d.line([a, b], fill=(120, 104, 78, 255), width=9)
                d.line([a, b], fill=(206, 186, 140, 255), width=5)
    for i, (x, y) in O.LAYOUT.items():
        m = O.maps[i]
        pic = L.render_map(m['tilesetId'], m['width'], m['height'], m['data'])
        w, h = max(1, round(m['width'] * s)), max(1, round(m['height'] * s))
        pic = pic.resize((w, h), Image.LANCZOS)
        bx, by = px(i, -0.5, -0.5)
        shadow = Image.new('RGBA', (w + 24, h + 24), (0, 0, 0, 0))
        ImageDraw.Draw(shadow).rectangle([12, 12, w + 12, h + 12], fill=(0, 0, 0, 150))
        img.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(6)), (int(bx) - 8, int(by) - 6))
        img.alpha_composite(pic, (int(bx), int(by)))
        d.rectangle([int(bx) - 1, int(by) - 1, int(bx) + w, int(by) + h], outline=O.COLORS[i] + (255,), width=2)

    # gates to the World Map
    for g in O.groups([(x, y, i) for (i, x, y) in gates]):
        i = g[0][2]
        sx = sum(p[0] for p in g) / len(g); sy = sum(p[1] for p in g) / len(g)
        p = px(i, sx, sy)
        end = (p[0], p[1] + 34)
        d.line([p, end], fill=(120, 230, 140, 255), width=5)
        d.polygon([(end[0], end[1] + 12), (end[0] - 9, end[1]), (end[0] + 9, end[1])], fill=(120, 230, 140, 255))
        d.text((end[0] + 14, end[1] - 8), 'To the World Map', font=O.font(17, True), fill=(150, 240, 160))

    # district names: inside the top-left corner, or another corner (or just outside) clear of the door badges,
    # the other districts and the labels already placed
    badges = [px(i, x, y) for (i, x, y, t) in doors]
    blocks = {i: (px(i, -0.5, -0.5), px(i, O.maps[i]['width'] - 0.5, O.maps[i]['height'] - 0.5)) for i in O.LAYOUT}
    placed = []
    def clear(r, own):
        if any(r[0] - 14 < bx < r[2] + 14 and r[1] - 16 < by < r[3] + 16 for bx, by in badges): return False
        if any(j != own and r[0] < b[1][0] and r[2] > b[0][0] and r[1] < b[1][1] and r[3] > b[0][1] for j, b in blocks.items()):
            return False
        return not any(r[0] < q[2] and r[2] > q[0] and r[1] < q[3] and r[3] > q[1] for q in placed)
    for i in O.LAYOUT:
        name = O.short(i).replace('Residential Quarter', 'Lantern Row')
        f = O.font(15, True)
        (l, t), (r, b) = blocks[i]
        tw = d.textlength(name, font=f) + 12
        spots = [(l + 3, t + 3), (r - tw - 3, t + 3), (l + 3, b - 25), (r - tw - 3, b - 25), (l, t - 26), (l, b + 4)]
        rect = next((q for q in ((x, y, x + tw, y + 22) for x, y in spots) if clear(q, i)), (l + 3, t + 3, l + 3 + tw, t + 25))
        placed.append(rect)
        d.rectangle(rect, fill=INK + (225,), outline=O.COLORS[i] + (255,))
        d.text((rect[0] + 6, rect[1] + 2), name, font=f, fill=O.COLORS[i])
    for i, x, y, name in STREETS:
        f = O.font(14)
        cx, cy = px(i, x, y)
        tw = d.textlength(name, font=f)
        d.rounded_rectangle([cx - tw / 2 - 6, cy - 10, cx + tw / 2 + 6, cy + 10], 6, fill=(250, 240, 210, 230))
        d.text((cx - tw / 2, cy - 9), name, font=f, fill=INK)

    # buildings: numbered badges, listed on the right
    entries, seen = [], {}
    for (i, x, y, t) in doors:
        if t in seen: continue
        seen[t] = len(entries) + 1
        entries.append((seen[t], i, t))
        cx, cy = px(i, x, y)
        d.ellipse([cx - 10, cy - 10, cx + 10, cy + 10], fill=(250, 246, 236, 255), outline=INK, width=2)
        n, f = str(seen[t]), O.font(13, True)
        d.text((cx - d.textlength(n, font=f) / 2, cy - 9), n, font=f, fill=INK)

    # you are here: the board in the Grand Plaza
    hx, hy = px(K.PLAZA, *BOARD)
    d.ellipse([hx - 9, hy - 9, hx + 9, hy + 9], fill=(230, 70, 70, 255), outline=(255, 255, 255, 255), width=3)
    f = O.font(15, True)
    tw = d.textlength('You are here', font=f)
    d.rectangle([hx + 13, hy - 11, hx + tw + 25, hy + 11], fill=INK + (235,), outline=(230, 70, 70, 255))
    d.text((hx + 19, hy - 9), 'You are here', font=f, fill=(255, 170, 160))

    # legend
    lx, ly = 980, 104
    d.text((lx, ly), 'PLACES', font=O.font(20, True), fill=GOLD)
    d.line([(lx, ly + 32), (SIZE[0] - 30, ly + 32)], fill=STEEL, width=1)
    ly += 44
    step = min(36, (SIZE[1] - 70 - ly) // max(1, len(entries)))
    for n, i, t in entries:
        d.ellipse([lx, ly + 2, lx + 20, ly + 22], fill=(250, 246, 236), outline=INK, width=2)
        f = O.font(13, True)
        d.text((lx + 10 - d.textlength(str(n), font=f) / 2, ly + 3), str(n), font=f, fill=INK)
        name = O.maps[t]['displayName'] or O.short(t)
        name = name.split(' - ')[0] + (' (Guild)' if t == K.TAVERN else '')
        d.text((lx + 30, ly), name, font=O.font(17), fill=TEXT)
        d.text((lx + 30, ly + 18), O.short(i).replace('Residential Quarter', 'Lantern Row'), font=O.font(12), fill=DIM)
        ly += step
    d.text((32, SIZE[1] - 36), 'Press any key to close', font=O.font(16), fill=DIM)
    img.convert('RGB').save(OUT)
    return OUT


# ====================================================================== the boards
def show_map():
    """Show the city map over the screen until a key or a click; the minimap and clock HUD step aside meanwhile
    (put back as the player had them)."""
    wait_key = "Input.isTriggered('ok') || Input.isTriggered('cancel') || TouchInput.isTriggered() || TouchInput.isCancelled()"
    return [
        *P.se('Book1'),
        cmd(355, ['this._novaHud = [$gameSystem._novaMinimapHidden, !!($gameSystem._novaClock && $gameSystem._novaClock.hudHidden)];']),
        cmd(655, ['$gameSystem._novaMinimapHidden = true; if ($gameSystem._novaClock) $gameSystem._novaClock.hudHidden = true;']),
        cmd(231, [PIC_ID, PICTURE, 0, 0, 0, 0, 100, 100, 0, 0]),
        cmd(232, [PIC_ID, None, 0, 0, 0, 0, 100, 100, 255, 0, 20, True]),
        cmd(112, []),
        cmd(111, [12, wait_key], 1), cmd(113, [], 2), cmd(0, [], 2), cmd(412, [], 1),
        cmd(230, [1], 1), cmd(0, [], 1), cmd(413, [], 0),
        *P.se('Book1', 60),
        cmd(232, [PIC_ID, None, 0, 0, 0, 0, 100, 100, 0, 0, 15, True]),
        cmd(235, [PIC_ID]),
        cmd(355, ['var h = this._novaHud || [false, false]; $gameSystem._novaMinimapHidden = h[0];']),
        cmd(655, ['if ($gameSystem._novaClock) $gameSystem._novaClock.hudHidden = h[1];'])]


def plaza_events(add, mp):
    put_tile(mp, BOARD, NOTICE_BOARD)
    add('City Map Board', BOARD[0], BOARD[1], [page(None, priority=1, commands=text(
        '\\C[6]Royal Capital of Nova\\C[0]', 'A painted map of the city, weathered by rain and', 'covered in travellers\' fingerprints.')
        + show_map())])


def residential_events(add, mp):
    put_tile(mp, HOME_SIGN, SIGNPOST)
    add('Ashveil House Sign', HOME_SIGN[0], HOME_SIGN[1], [page(None, priority=1, commands=text(
        '\\C[6]Ashveil Residence\\C[0]', 'Ember Lane, Lantern Row', '(Kael\'s home)'))])


def put_tile(mp, at, tile):
    w, h = mp['width'], mp['height']
    mp['data'][(2 * h + at[1]) * w + at[0]] = tile


if __name__ == '__main__':
    print('wrote', render())
    if '--save' in sys.argv:
        L.write_map(K.PLAZA, P.patch_events(K.PLAZA, plaza_events, tag=TAG))
        L.write_map(K.RESIDENTIAL, P.patch_events(K.RESIDENTIAL, residential_events, tag=TAG))
        print('boards saved')
