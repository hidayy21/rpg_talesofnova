# Sprites for the NovaPets pets, built from the side-view battlers in "additional asset/battler":
#   img/sv_actors/Pet_*.png       the battler (9 x 6 motions, as the RPG Maker editor expects)
#   img/characters/$Pet_*.png     a walking sheet for pets the RTP has no map sprite for (side view: the battler's
#                                 walk motion facing left and mirrored; the NovaPets <pet side view> tag keeps them
#                                 from turning up or down)
#   img/characters/Pet_Animals.png  the eight-animal walking sheet (red panda, wolves, swan, kitten ...)
# Pets with an RTP map sprite use Monster.png / Nature.png as they are. Re-running rewrites the same files.
import os, sys
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import compose_tileset as C

PROJ = C.PROJ
SRC = PROJ + 'additional asset/battler/'
SV_DIR, CHAR_DIR = PROJ + 'img/sv_actors/', PROJ + 'img/characters/'

# battler file -> img/sv_actors name (and the size of one motion frame in the game)
BATTLERS = {'bat': 'Pet_Bat', 'cat': 'Pet_Cat', 'chicken': 'Pet_Chicken', 'fairy': 'Pet_Fairy', 'fox': 'Pet_Fox',
            'ghost': 'Pet_Ghost', 'hornet': 'Pet_Hornet', 'owl': 'Pet_Owl', 'Slime': 'Pet_Slime', 'snake': 'Pet_Snake',
            'wolf': 'Pet_Wolf', 'IronGolem': 'Pet_IronGolem'}
FRAME = {'IronGolem': 96}           # drawn at 384 px a frame; 96 keeps it a head taller than the heroes
# walking sheets made from a battler: battler file -> (sheet name, frame size, front-facing sheet or None)
SIDE_SHEETS = {'fox': ('$Pet_Fox', 64, None), 'owl': ('$Pet_BarnOwl', 64, None), 'hornet': ('$Pet_Hornet', 64, None),
               'snake': ('$Pet_Snake', 64, None), 'IronGolem': ('$Pet_IronGolem', 96, 'IronGiantTV')}


def battler(name):
    im = Image.open(SRC + name + '.png').convert('RGBA')
    size = FRAME.get(name, 64)
    if im.size != (size * 9, size * 6):
        im = im.resize((size * 9, size * 6), Image.LANCZOS)
    return im


def walk_frames(sv, size):
    """The three frames of the battler's walk motion (top-left block), scaled to size x size."""
    f = sv.width // 9
    return [sv.crop((k * f, 0, k * f + f, f)).resize((size, size), Image.LANCZOS) if f != size
            else sv.crop((k * f, 0, k * f + f, f)) for k in range(3)]


def side_sheet(sv, size, front=None):
    """$ sheet, rows down/left/right/up: left = walk frames, right = mirrored; down = the front sheet or left."""
    left = walk_frames(sv, size)
    right = [f.transpose(Image.FLIP_LEFT_RIGHT) for f in left]
    down = left
    if front:
        tv = Image.open(SRC + front + '.png').convert('RGBA')
        fw = tv.width // 3
        down = [tv.crop((k * fw, 0, k * fw + fw, fw)).resize((size, size), Image.LANCZOS) for k in range(3)]
    sheet = Image.new('RGBA', (size * 3, size * 4))
    for row, frames in enumerate([down, left, right, right]):
        for k, f in enumerate(frames):
            sheet.alpha_composite(f, (k * size, row * size))
    return sheet


def main():
    for src, name in BATTLERS.items():
        sv = battler(src)
        sv.save(SV_DIR + name + '.png')
        if src in SIDE_SHEETS:
            sheet, size, front = SIDE_SHEETS[src]
            side_sheet(sv, size, front).save(CHAR_DIR + sheet + '.png')
    Image.open(SRC + 'animal.png').convert('RGBA').save(CHAR_DIR + 'Pet_Animals.png')
    print('battlers', len(BATTLERS), 'walking sheets', len(SIDE_SHEETS) + 1)


if __name__ == '__main__':
    main()
