# Draws a sheet with each tile's number under it (RPG Maker numbering), for picking tiles for
# L.ext('Sheet', n) in map scripts or for compose_tileset.py recipes.
#
#   python tile_numbers.py Inside_B            -> _work/tiles_Inside_B.png
#   python tile_numbers.py Inside_A5 Dungeon_C -> one image per sheet
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import nova_maplib as L
from atlas import sheet_grid

if __name__ == '__main__':
    out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '_work')
    os.makedirs(out_dir, exist_ok=True)
    for name in sys.argv[1:]:
        out = os.path.join(out_dir, 'tiles_%s.png' % name)
        sheet_grid(L.PROJ + 'img/tilesets/%s.png' % name, out, 'A5' if name.endswith('_A5') else 0)
        print(out)
