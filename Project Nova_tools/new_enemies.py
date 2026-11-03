# Enemies from the Dark Fantasy Character Pack (RPG Maker MV DLC), drawn with its side-view sheets (NovaSvEnemy):
# the Order of Caelum (Light mages and knights - weak to Darkness), remnants of the Arulustus war, and what the
# taint from the weakening seal makes of the living and the dead. Their action patterns are in enemy_ai.py.
# Copies the sheets into img/sv_actors, draws a still for the Bestiary (img/enemies and img/sv_enemies), and adds
# troops. Running it again updates the same entries (matched by name).
#   python3 new_enemies.py           -> report
#   python3 new_enemies.py --apply   -> write (RPG Maker editor must be closed)
import json, os, shutil, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import nova_maplib as L
from PIL import Image

DLC = os.path.expanduser('~/Library/Application Support/Steam/steamapps/common/RPG Maker MV/dlc/DarkFantasyCharacterPack/img/sv_actors')
LIGHT, DARK = 8, 9                                   # element ids (System > Types)
BASE_TRAITS = [{'code': 22, 'dataId': 0, 'value': 0.95}, {'code': 22, 'dataId': 1, 'value': 0.05},
               {'code': 31, 'dataId': 1, 'value': 0}]


def rate(element, value): return {'code': 11, 'dataId': element, 'value': value}


# name: (sheet, params [mhp, mmp, atk, def, mat, mdf, agi, luk], exp, gold, guard, weak, extra traits, drops, desc1, desc2)
ENEMIES = [
    ('Arulustus Remnant', '2_DF_Actor1', [1600, 40, 70, 75, 30, 45, 40, 30], 380, 160, 5, 'Thunder, Axe', [],
     [(1, 5, 2), (1, 33, 6)], 'A knight of the Arulustus Empire who never laid down his sword.',
     'Sixteen years after the war, he is still fighting it.'),
    ('Caelum Templar', '2_DF_Actor2', [2200, 120, 78, 70, 50, 60, 45, 30], 520, 200, 5, 'Darkness, Spear', [rate(LIGHT, 0.5)],
     [(1, 5, 2), (1, 28, 4)], 'Sworn blade of the Order of Caelum, gilded in its colours.',
     'Light barely scratches it. Shadow does.'),
    ('Plague Doctor', '2_DF_Actor3', [1300, 200, 45, 45, 80, 70, 55, 40], 400, 180, 3, 'Fire, Wind', [],
     [(1, 29, 4), (1, 26, 3)], 'Walks where the sickness is, studying it more than curing it.',
     'Burn the mask and the miasma goes with it.'),
    ('Caelum Acolyte', '2_DF_Actor4', [1100, 260, 40, 50, 85, 90, 60, 40], 420, 190, 3, 'Darkness, Bow', [rate(LIGHT, 0.5)],
     [(1, 2, 2), (1, 28, 4)], 'A healer of the Order. Keeps the Templars standing.',
     'Silence her first, or the fight never ends.'),
    ('Tainted Revenant', '2_DF_Actor5', [1500, 120, 65, 55, 70, 60, 50, 20], 430, 100, 4, 'Light, Fire', [rate(DARK, 0.5)],
     [(1, 28, 3), (1, 17, 3)], 'A corpse that the black crystals\' taint has stood back up.',
     'It hungers for mana, not flesh.'),
    ('Riftborn Fiend', '2_DF_Actor6', [1700, 200, 70, 50, 85, 60, 70, 40], 480, 150, 4, 'Light, Ice', [rate(DARK, 0.5)],
     [(1, 2, 3), (1, 24, 4)], 'Crawled out of a crack in the magic flow.',
     'Sweet words, sharp claws. Do not listen to it.'),
    ('Hollow Monarch', '2_DF_Actor7', [6500, 400, 85, 75, 100, 85, 55, 50], 1500, 800, 7, 'Light, Spear', [rate(DARK, 0)],
     [(1, 8, 2), (1, 14, 3)], 'A dead king\'s crown, worn by something from under the seal.',
     'It speaks with more than one voice.'),
    ('Caelum Inquisitor', '2_DF_Actor8', [5200, 500, 50, 65, 110, 100, 65, 50], 1400, 900, 6, 'Darkness, Bow', [rate(LIGHT, 0)],
     [(1, 8, 2), (1, 13, 3)], 'Judges heresy for the Order of Caelum. Has never found anyone innocent.',
     'Pure Light, and no mercy in it.'),
]

# troop name: members (enemy names), placed left to right
TROOPS = [
    ('Arulustus Remnant*2', ['Arulustus Remnant', 'Arulustus Remnant']),
    ('Caelum Templar, Acolyte', ['Caelum Templar', 'Caelum Acolyte']),
    ('Caelum Templar*2, Acolyte', ['Caelum Templar', 'Caelum Acolyte', 'Caelum Templar']),
    ('Plague Doctor, Revenant*2', ['Tainted Revenant', 'Plague Doctor', 'Tainted Revenant']),
    ('Tainted Revenant*3', ['Tainted Revenant', 'Tainted Revenant', 'Tainted Revenant']),
    ('Riftborn Fiend*2', ['Riftborn Fiend', 'Riftborn Fiend']),
    ('Hollow Monarch', ['Tainted Revenant', 'Hollow Monarch', 'Tainted Revenant']),
    ('Caelum Inquisitor', ['Caelum Templar', 'Caelum Inquisitor', 'Caelum Templar']),
]
SPOTS = {1: [(410, 420)], 2: [(520, 400), (300, 430)], 3: [(560, 380), (410, 450), (250, 400)]}
ELITE_SPOTS = [(560, 450), (330, 380), (250, 470)]     # the leader in the middle stands back, its escort in front


def still(sheet, out_name):
    """The first idle frame, 3x larger, for the Bestiary and the editor."""
    im = Image.open(os.path.join(DLC, sheet + '.png')).convert('RGBA')
    fw, fh = im.width // 9, im.height // 6
    frame = im.crop((0, 0, fw, fh)).transpose(Image.FLIP_LEFT_RIGHT)          # faces the party, like in battle
    frame = frame.resize((fw * 3, fh * 3), Image.NEAREST)
    for folder in ('enemies', 'sv_enemies'):
        frame.save(L.PROJ + 'img/%s/%s.png' % (folder, out_name))


if __name__ == '__main__':
    apply = '--apply' in sys.argv
    enemies = json.load(open(L.DATA + 'Enemies.json', encoding='utf8'))
    troops = json.load(open(L.DATA + 'Troops.json', encoding='utf8'))
    ids = {}
    for name, sheet, params, exp, gold, guard, weak, traits, drops, d1, d2 in ENEMIES:
        eid = next((e['id'] for e in enemies if e and e['name'] == name), None) or len(enemies)
        if eid == len(enemies): enemies.append(None)
        old = enemies[eid] or {}
        battler = 'DF_' + name.replace(' ', '')
        note = '<sv actor: %s>\n<guard: %d>\n<weak: %s>\n<desc1:%s>\n<desc2:%s>' % (sheet, guard, weak, d1, d2)
        if params[0] >= 5000: note = note.replace('\n', '\n<sv scale: 1.5>\n', 1)     # elites stand taller
        keep = [l for l in old.get('note', '').split('\n') if l.startswith('<charge')]   # set by enemy_ai.py
        enemies[eid] = {'id': eid, 'actions': old.get('actions', [{'conditionParam1': 0, 'conditionParam2': 0,
                        'conditionType': 0, 'rating': 5, 'skillId': 1}]), 'battlerHue': 0, 'battlerName': battler,
                        'dropItems': [{'kind': k, 'dataId': i, 'denominator': d} for k, i, d in drops] +
                                     [{'kind': 0, 'dataId': 1, 'denominator': 1}] * (3 - len(drops)),
                        'exp': exp, 'gold': gold, 'name': name, 'note': '\n'.join([note] + keep),
                        'params': params, 'traits': BASE_TRAITS + traits}
        ids[name] = eid
        print('enemy %2d %-18s %s' % (eid, name, sheet))
        if apply:
            shutil.copy2(os.path.join(DLC, sheet + '.png'), L.PROJ + 'img/sv_actors/%s.png' % sheet)
            still(sheet, battler)
    for tname, members in TROOPS:
        tid = next((t['id'] for t in troops if t and t['name'] == tname), None) or len(troops)
        if tid == len(troops): troops.append(None)
        page = {'conditions': {'actorHp': 50, 'actorId': 1, 'actorValid': False, 'enemyHp': 50, 'enemyIndex': 0,
                               'enemyValid': False, 'switchId': 1, 'switchValid': False, 'turnA': 0, 'turnB': 0,
                               'turnEnding': False, 'turnValid': False},
                'list': [{'code': 0, 'indent': 0, 'parameters': []}], 'span': 0}
        old = troops[tid] or {}
        troops[tid] = {'id': tid, 'members': [{'enemyId': ids[n], 'x': x, 'y': y, 'hidden': False}
                                              for n, (x, y) in zip(members, ELITE_SPOTS if tname in ('Hollow Monarch', 'Caelum Inquisitor')
                                                                   else SPOTS[len(members)])],
                       'name': tname, 'pages': old.get('pages', [page])}
        print('troop %2d %s' % (tid, tname))
    if apply:
        dump = lambda xs: '[\n' + ',\n'.join(json.dumps(x, ensure_ascii=False, separators=(',', ':')) for x in xs) + '\n]'
        with open(L.DATA + 'Enemies.json', 'w', encoding='utf8', newline='') as f: f.write(dump(enemies))
        with open(L.DATA + 'Troops.json', 'w', encoding='utf8', newline='') as f: f.write(dump(troops))
