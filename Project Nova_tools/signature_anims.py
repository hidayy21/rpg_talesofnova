# Signature battle animations for the heroes' big skills, built from the RTP animations already in the project:
# a recolour (new hue on one or both sheets) or two one-sheet animations played together (the second on sheet 2,
# starting a few frames later). They are added as "Nova: ..." after the RTP ones and the skills point to them.
# Running it again updates the same entries.
#   python3 signature_anims.py           -> report
#   python3 signature_anims.py --apply   -> write Animations.json and Skills.json (RPG Maker editor must be closed)
import copy, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import nova_maplib as L

MAX_CELLS = 16              # Sprite_Animation draws at most 16 cells per frame


def recolor(src, hue1, hue2=None, flash=None):
    return ('recolor', src, hue1, hue2, flash)


def overlay(a, b, offset, hue_a=0, hue_b=0, flash=None):
    return ('overlay', a, b, offset, hue_a, hue_b, flash)


# name: (recipe, [skills that use it])
SIGNATURES = {
    # Kael - shadow and the Ashveil flame
    'Shadowflame Eclipse': (overlay(104, 69, 8, 0, 0, [255, 90, 40, 160]), ['Shadowflame Eclipse']),
    'Ashveil Apocalypse': (recolor(105, 0, 330, [255, 40, 60, 200]), ['Ashveil Apocalypse']),
    'Gravity Well': (recolor(105, 0, 240), ['Gravity Well']),
    'Black Flame': (recolor(67, 260), ['Black Flame']),
    'Abyssal Pact': (recolor(53, 270), ['Abyssal Pact']),
    'Singularity': (recolor(110, 200, 200), ['Singularity']),
    'Twilight Eclipse': (recolor(105, 0, 200), ['Twilight Eclipse']),
    # Mira - arcane, stars and the void
    'Void Rift': (recolor(105, 180, 160), ['Void Rift']),
    'Abyssal Bloom': (recolor(104, 300), ['Abyssal Bloom']),
    'Oblivion': (recolor(105, 180, 180, [220, 240, 255, 200]), ['Oblivion']),
    'Void Collapse': (recolor(110, 260, 260), ['Void Collapse']),
    'Elemental Convergence': (recolor(110, 90, 0), ['Elemental Convergence']),
    # Yuki - ice and the single stroke
    'Hyoryu Tensho': (overlay(25, 74, 10, 180, 0, [200, 240, 255, 200]), ['Ryūzetsu Hiden: Hyōryū Tenshō']),
    'Issen': (recolor(25, 180), ['Ittōryū Ōgi: Issen']),
    'Yukihime': (recolor(53, 160), ['Yukihime Awakening']),
    # Diana - arrows on the wind
    'Thousandfold Hawk': (overlay(113, 74, 4, 0, 90), ['Thousandfold Hawk']),
    # Roland - the lion's gold
    'Lionheart Aegis': (recolor(53, 40), ['Lionheart Aegis', 'Rally']),
    # Barion - dragon fire
    'Twilight of Wyrms': (overlay(25, 69, 10, 15, 0, [255, 120, 40, 180]), ['Twilight of Wyrms']),
    'Dragonfall': (recolor(25, 330), ['Dragonfall']),
    'Dragon Blood': (recolor(53, 330), ['Dragon Blood', 'Beast Unleashed']),
    # Lysandre - blood and roses
    'Bloodrose Requiem': (recolor(105, 300, 320, [255, 60, 120, 180]), ['Bloodrose Requiem']),
    'Chains of Lilith': (recolor(104, 320), ['Chains of Lilith']),
    'Undying Hunger': (recolor(53, 300), ['Undying Hunger']),
}


def one_sheet(a):
    return not a['animation2Name'] and all(c[0] < 100 for f in a['frames'] for c in f)


def build(anims, recipe):
    kind = recipe[0]
    if kind == 'recolor':
        _, src, hue1, hue2, flash = recipe
        a = copy.deepcopy(anims[src])
        a['animation1Hue'] = hue1
        if hue2 is not None and a['animation2Name']: a['animation2Hue'] = hue2
    else:
        _, ia, ib, offset, hue_a, hue_b, flash = recipe
        A, B = anims[ia], anims[ib]
        assert one_sheet(A) and one_sheet(B), 'overlay needs two one-sheet animations (%d, %d)' % (ia, ib)
        assert A['position'] == B['position'], 'overlay needs the same position (%d, %d)' % (ia, ib)
        a = copy.deepcopy(A)
        a.update({'animation1Hue': hue_a, 'animation2Name': B['animation1Name'], 'animation2Hue': hue_b})
        n = max(len(A['frames']), offset + len(B['frames']))
        frames = []
        for i in range(n):
            cells = copy.deepcopy(A['frames'][i]) if i < len(A['frames']) else []
            j = i - offset
            if 0 <= j < len(B['frames']):
                for c in B['frames'][j]:
                    if len(cells) >= MAX_CELLS: break
                    cells.append([c[0] + 100] + c[1:])
            frames.append(cells)
        a['frames'] = frames
        a['timings'] = sorted(copy.deepcopy(A['timings']) + [dict(t, frame=t['frame'] + offset) for t in copy.deepcopy(B['timings'])],
                              key=lambda t: t['frame'])
    if flash:                                                   # a screen flash at the peak (middle of the animation)
        a['timings'].append({'flashColor': flash, 'flashDuration': 8, 'flashScope': 2, 'frame': len(a['frames']) // 2, 'se': None})
        a['timings'].sort(key=lambda t: t['frame'])
    return a


if __name__ == '__main__':
    apply = '--apply' in sys.argv
    anims = json.load(open(L.DATA + 'Animations.json', encoding='utf8'))
    skills = json.load(open(L.DATA + 'Skills.json', encoding='utf8'))
    rtp_count = len(anims)
    for name, (recipe, users) in SIGNATURES.items():
        full = 'Nova: ' + name
        aid = next((a['id'] for a in anims if a and a['name'] == full), None)
        if aid is None:
            aid = len(anims)
            anims.append(None)
        a = build(anims, recipe)
        a.update({'id': aid, 'name': full})
        anims[aid] = a
        hit = [s for s in skills if s and s['name'] in users]
        missing = set(users) - {s['name'] for s in hit}
        assert not missing, 'no skill named %s' % missing
        for s in hit: s['animationId'] = aid
        print('%3d %-24s -> %s' % (aid, full, ', '.join(users)))
    if apply:
        dump = lambda xs: '[\n' + ',\n'.join(json.dumps(x, ensure_ascii=False, separators=(',', ':')) for x in xs) + '\n]'
        with open(L.DATA + 'Animations.json', 'w', encoding='utf8', newline='') as f: f.write(dump(anims))
        with open(L.DATA + 'Skills.json', 'w', encoding='utf8', newline='') as f: f.write(dump(skills))
    print('%d animations (%s)' % (len(SIGNATURES), 'written' if apply else 'report only, --apply to write'))
