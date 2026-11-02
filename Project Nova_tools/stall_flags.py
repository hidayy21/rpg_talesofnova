# PandaMaru market stalls (PM_Market): the keeper stands in the row whose overlay tile holds the counter board, so that
# overlay must be drawn above characters (star) or the keeper seems to stand on the table. The counter fronts below
# get the Counter flag, so the player talks to the keeper across them. Passability stays as it is (the shelves under
# the overlays block). Run again after the Tileset Wizard rewrites the flags.
#   python stall_flags.py          -> list what would change
#   python stall_flags.py --save   -> write it (RPG Maker MV must be closed)
import sys
import compose_tileset as C

SHEET = 'PM_Market'
STAR = [*range(10, 16), *range(58, 64), *range(85, 88)]        # counter tops / fringe with the board at the bottom
COUNTER = [*range(18, 24), *range(66, 72), *range(96, 104), *range(112, 120)]    # counter fronts


def patch(tilesets):
    flags, first, _ = C._flag_source(tilesets, SHEET)
    changed = []
    for ns, bit in ((STAR, 0x10), (COUNTER, 0x80)):
        for n in ns:
            if not flags[first + n] & bit:
                flags[first + n] |= bit
                changed.append((n, bit))
    return changed


if __name__ == '__main__':
    path = C.PROJ + 'data/Tilesets.json'
    tilesets = C._read(path)
    changed = patch(tilesets)
    print('%s: %d tiles' % (SHEET, len(changed)), ' '.join('%d%s' % (n, '*' if b == 0x10 else 'C') for n, b in changed))
    if changed and '--save' in sys.argv:
        with open(path, 'w', encoding='utf8', newline='') as f: f.write(C._tilesets_text(tilesets))
        print('saved')
