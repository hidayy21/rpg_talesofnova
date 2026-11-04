# The Academy's cast sheet for the story notes: every sprite from academy_sprites.py (front and back), with its name,
# gender (M/F), role and where it sits on its sheet (img/characters/<sheet>.png, index 0-7 left to right, top to bottom).
#   python3 academy_cast.py   -> Story/Royal_Magic_Academy_cast.png
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import academy_sprites as A
import sprite_gen as G
from kingdom_overview import font
from PIL import Image, ImageDraw

OUT = os.path.join(G.HERE, '..', 'Story', 'Royal_Magic_Academy_cast.png')
ROLE = {'Archmage Corvin Vale': 'Kepala Academy', 'Professor Elspeth Rook': 'Teori Elemen', 'Professor Halden': 'Ward & Rune',
        'Duelling Master Kestrel': 'Latihan Duel', 'Professor Aubert': 'Sejarah Arkana', 'Professor Brisk': 'Alkimia',
        'Professor of Herbs': 'Herbalogi', 'Professor Lyra Venn': 'Astronomi', 'Professor Wren-Hollis': 'Enchantment Theory',
        'Librarian Ottoline': 'Pustakawan', 'Healer Agnes': 'Penyembuh', 'Master Enchanter Thibault': 'Bengkel Enchanting',
        'Familiar Keeper Pim': 'Penjaga Familiar', 'Registrar Fenwick': 'Panitera', 'Hall Steward': 'Pengurus Aula Besar',
        'Academy Sentinel': 'Penjaga Gerbang'}
SHOW = {'Professor of Herbs': 'Professor Moss'}       # the map's event name -> the name players see
BG, GOLD, TXT, SUB, ROLE_COL = (22, 28, 44, 255), (240, 226, 180), (236, 240, 248), (150, 165, 195), (255, 214, 120)
SEX_COL = {'M': (120, 180, 255), 'F': (255, 140, 190)}


def gender(c): return 'M' if c['sex'] == 'Male' else 'F'


def frames(c, scale):
    im = G.compose(c)
    out = Image.new('RGBA', (96 * scale, 48 * scale), (0, 0, 0, 0))
    for k, y in enumerate((0, 144)):                  # facing the camera, and from behind
        out.alpha_composite(im.crop((48, y, 96, y + 48)).resize((48 * scale, 48 * scale), Image.NEAREST), (48 * scale * k, 0))
    return out


def centred(d, x0, width, y, text, f, col):
    d.text((x0 + (width - d.textlength(text, font=f)) / 2, y), text, font=f, fill=col)


def main():
    COLS, CW, CH, S = 4, 330, 250, 3                    # staff cards
    SC, SCW, SCH, SS = 8, 165, 175, 2                   # student cards
    staff_rows = (len(A.FACULTY) + COLS - 1) // COLS
    img = Image.new('RGBA', (max(COLS * CW, SC * SCW) + 40, 115 + staff_rows * CH + 90 + 3 * SCH + 40), BG)
    d = ImageDraw.Draw(img)
    d.text((24, 20), 'Royal Magic Academy - Sprite & Nama', font=font(40, True), fill=GOLD)
    d.text((24, 72), 'Staf & Profesor  (img/characters/Nova_Faculty1-2.png)   M = pria, F = wanita', font=font(24, True), fill=GOLD)
    for i, (name, c) in enumerate(A.FACULTY):
        x, y, w = 20 + (i % COLS) * CW, 115 + (i // COLS) * CH, CW - 14
        d.rounded_rectangle([x, y, x + w, y + CH - 14], radius=10, fill=(32, 40, 60, 255), outline=(70, 85, 120, 255), width=2)
        img.alpha_composite(frames(c, S), (x + (w - 288) // 2, y + 6))
        g = gender(c)
        d.rounded_rectangle([x + 8, y + 8, x + 40, y + 36], radius=6, fill=SEX_COL[g])
        centred(d, x + 8, 32, y + 10, g, font(18, True), (20, 24, 36))
        sheet, idx = A.CAST[name]
        centred(d, x, w, y + 152, '%s (%s)' % (SHOW.get(name, name), g), font(19, True), TXT)
        centred(d, x, w, y + 178, ROLE[name], font(18), ROLE_COL)
        centred(d, x, w, y + 204, '%s  #%d' % (sheet, idx), font(16), SUB)
    y0 = 115 + staff_rows * CH + 20
    d.text((24, y0), 'Murid  (img/characters/Nova_Students1-3.png)   biru = Dawnward, marun = Duskward', font=font(24, True), fill=GOLD)
    prefects = {v: k for k, v in A.CAST.items() if 'Prefect' in k}
    for i, (sheet, idx) in enumerate(A.STUDENTS):
        c = A.STUDENT_SHEETS[sheet][idx]
        x, y, w = 20 + (i % SC) * SCW, y0 + 50 + (i // SC) * SCH, SCW - 10
        dawn = c['colors']['c1'] == A.DAWN['c1']
        d.rounded_rectangle([x, y, x + w, y + SCH - 12], radius=8, fill=(32, 40, 60, 255),
                            outline=(60, 100, 200, 255) if dawn else (160, 50, 70, 255), width=2)
        img.alpha_composite(frames(c, SS), (x + (w - 192) // 2, y + 4))
        g = gender(c)
        d.rounded_rectangle([x + 5, y + 5, x + 29, y + 27], radius=5, fill=SEX_COL[g])
        centred(d, x + 5, 24, y + 6, g, font(15, True), (20, 24, 36))
        centred(d, x, w, y + 102, '%s (%s)' % ('Dawnward' if dawn else 'Duskward', g), font(16, True), TXT)
        centred(d, x, w, y + 124, '%s #%d' % (sheet[5:], idx), font(14), SUB)
        role = prefects.get((sheet, idx))
        if role: centred(d, x, w, y + 146, 'Prefect (Aula Masuk)' if role == 'Prefect' else role, font(14, True), ROLE_COL)
    img.convert('RGB').save(OUT)
    print('saved', os.path.normpath(OUT), img.size)


if __name__ == '__main__':
    main()
