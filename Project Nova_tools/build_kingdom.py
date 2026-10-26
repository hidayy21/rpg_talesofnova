# Builds every Royal Kingdom of Nova map, validates the whole set, and (with --apply) writes it to the project.
#   python build_kingdom.py            -> validate only
#   python build_kingdom.py --apply    -> back up data/, write database additions + maps (editor must be closed)
import sys, json, copy, shutil, datetime, subprocess, importlib
sys.path.insert(0, 'D:/RPG Maker MV/Project Nova_tools')
import nova_maplib as L
import kingdom as K
import validate_maps as V

EXTERIORS = [('map_plaza', K.PLAZA, 0), ('map_market', K.MARKET, K.PLAZA), ('map_residential', K.RESIDENTIAL, K.PLAZA),
             ('map_harbor', K.HARBOR, K.PLAZA), ('map_castle_approach', K.CASTLE_APPROACH, K.PLAZA)]


def as_dict(builder):
    return {'width': builder.w, 'height': builder.h, 'tilesetId': builder.tileset_id, 'data': builder.tile_data(),
            'events': builder.events}


def collect():
    built = {}
    for mod, mid, parent in EXTERIORS:
        built[mid] = (importlib.import_module(mod).m, parent)
    import map_interiors
    for mid, (room, parent) in map_interiors.build_all().items():
        built[mid] = (room, parent)
    return built


def bakers_lane_preview():
    """Baker's Lane as kingdom_data.patch_bakers_lane() will leave it (in memory)."""
    m = json.load(open(L.DATA + 'Map002.json', encoding='utf8'))
    m = copy.deepcopy(m)
    ev = {e['name']: e for e in m['events'] if e}
    for nm, tgt, tx, ty in (('Bakery Door', K.BAKERY, 7, 10), ('Tavern Door', K.TAVERN, 10, 13), ('Inn Door', K.INN, 5, 13)):
        e = ev[nm]; e['pages'] = [L.door_page(tgt, tx, ty, 8, '!Door1', e['pages'][0]['image']['characterIndex'])]
    m['events'] = [e for e in m['events'] if e is None or not e['name'].startswith('Edge:')]
    W = m['width']
    for label, cells, tgt, tx, ty, d in (('Plaza 1', [(W - 1, y) for y in range(7, 11)], K.PLAZA, 1, 1, 2),
                                         ('Plaza 2', [(W - 1, y) for y in range(17, 21)], K.PLAZA, 1, 1, 2),
                                         ('Res 1', [(0, y) for y in range(7, 11)], K.RESIDENTIAL, 38, 1, 2),
                                         ('Res 2', [(0, y) for y in range(17, 21)], K.RESIDENTIAL, 38, 1, 2)):
        for i, (x, y) in enumerate(cells):
            m['events'].append({'id': len(m['events']), 'name': 'Edge: %s %d' % (label, i), 'note': '',
                                'pages': [L.exit_page(tgt, tx, ty, d)], 'x': x, 'y': y})
    return m


def editor_running():
    out = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq RPGMV.exe'], capture_output=True, text=True).stdout
    return 'RPGMV.exe' in out


if __name__ == '__main__':
    built = collect()
    maps = {mid: as_dict(b) for mid, (b, _) in built.items()}
    maps[K.BAKERS_LANE] = bakers_lane_preview()
    problems = V.check(maps)
    print('%d maps, %d events' % (len(maps), sum(len([e for e in m['events'] if e]) for m in maps.values())))
    print('\n'.join(problems) if problems else 'validation: OK')
    if '--apply' in sys.argv:
        if problems: sys.exit('not applying: fix the problems above first')
        if editor_running(): sys.exit('not applying: RPG Maker MV is open - save and close it first')
        stamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        bk = 'D:/RPG Maker MV/Project Nova_backups/data_' + stamp
        shutil.copytree(L.DATA, bk)
        print('backup:', bk)
        import kingdom_data
        kingdom_data.main()
        for mid, (b, parent) in sorted(built.items()):
            b.save(mid, parent_id=parent, order=mid, expanded=(mid == K.PLAZA))
        kingdom_data.patch_bakers_lane()
        print('applied')
