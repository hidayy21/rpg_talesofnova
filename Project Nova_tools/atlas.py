# Renders sample blocks of every autotile kind of a tileset sheet, for picking tiles by eye.
import sys
sys.path.insert(0, '.')
import nova_maplib as L
from PIL import Image, ImageDraw

def atlas(tileset, sheet, kinds, path, cols=8):
    cells = []
    for k in kinds:
        m = L.MapBuilder(4, 3, tileset, 'x')
        if L.is_wall_kind(sheet, k):
            m.rect(0, 0, 3, 2, (sheet, k))
        else:
            m.rect(1, 0, 2, 2, (sheet, k)); m.rect(0, 1, 3, 1, (sheet, k))
        cells.append((k, L.render_map(tileset, 4, 3, m.tile_data(), None)))
    rows = (len(cells) + cols - 1) // cols
    out = Image.new('RGBA', (cols * 200, rows * 160), (90, 90, 90, 255)); d = ImageDraw.Draw(out)
    for i, (k, img) in enumerate(cells):
        x, y = (i % cols) * 200, (i // cols) * 160
        out.alpha_composite(img, (x, y)); d.text((x + 2, y + 146), '%s %d' % (sheet, k), fill=(255, 255, 0))
    out.save(path)

def sheet_grid(path_in, path_out, first_id, cols=16, scale=1):
    im = Image.open(path_in).convert('RGBA')
    n_cols, n_rows = im.width // 48, im.height // 48
    out = Image.new('RGBA', (n_cols * 58, n_rows * 62), (150, 150, 150, 255)); d = ImageDraw.Draw(out)
    for r in range(n_rows):
        for c in range(n_cols):
            t = im.crop((c * 48, r * 48, c * 48 + 48, r * 48 + 48))
            out.alpha_composite(t, (c * 58 + 5, r * 62))
            if first_id == 'A5': tid = r * 8 + c
            else: tid = (c // 8) * 128 + r * 8 + c % 8
            d.text((c * 58 + 6, r * 62 + 48), str(tid), fill=(0, 0, 0))
    if scale != 1: out = out.resize((int(out.width * scale), int(out.height * scale)), Image.LANCZOS)
    out.save(path_out)
