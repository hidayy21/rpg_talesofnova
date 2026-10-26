# Database for the NovaPets plugin: the Companion class, pet skills, pet actors, the adoption talk at Whisker & Paw
# (common event CE_PETS) and the plugin's entry in js/plugins.js. Idempotent: re-running rewrites the same ids.
# The old companion accessories (armors PET_*) stay: each pet hands its armor's params/traits to the whole party.
import json, re, sys
sys.path.insert(0, 'D:/RPG Maker MV/Project Nova_tools')
import data_ids as DI
import nova_maplib as L

DATA = L.DATA
CLASS_COMPANION = 7
ACTOR_HOUND, ACTOR_CAT, ACTOR_CHICK, ACTOR_OWL = 7, 8, 9, 10
SK_BITE, SK_HOWL, SK_SCRATCH, SK_POUNCE, SK_PECK, SK_CHEER, SK_TALON, SK_HOOT = range(141, 149)
# (actor, name, price, sound) offered by Wren. The Barn Owl waits for its sprite ($Pet_BarnOwl).
ADOPT = [(ACTOR_HOUND, 'Loyal Hound', 3000, 'Dog'), (ACTOR_CAT, 'Alley Cat', 3000, 'Cat'), (ACTOR_CHICK, 'Lucky Chick', 4000, 'Item3')]


def load(n): return json.load(open(DATA + n + '.json', encoding='utf8'))


def save(n, arr):
    with open(DATA + n + '.json', 'w', encoding='utf8', newline='') as f:
        f.write('[\n' + ',\n'.join(json.dumps(x, ensure_ascii=False, separators=(',', ':')) for x in arr) + '\n]')


def put(arr, idx, obj):
    while len(arr) <= idx: arr.append(None)
    arr[idx] = obj


def cmd(code, params, indent=0): return {'code': code, 'indent': indent, 'parameters': params}


# ---------------------------------------------------------------- Companion class: ~70% of a front-line hero
def companion_class():
    curve = {0: (300, 1900, 3300), 1: (20, 100, 200), 2: (15, 180, 330), 3: (10, 110, 200),
             4: (14, 170, 320), 5: (10, 120, 220), 6: (18, 210, 380), 7: (15, 180, 320)}

    def at(v1, v50, v99, lv):
        if lv <= 50: return round(v1 + (v50 - v1) * (lv - 1) / 49)
        return round(v50 + (v99 - v50) * (lv - 50) / 49)
    params = [[at(*curve[p], max(1, lv)) for lv in range(100)] for p in range(8)]
    return {'id': CLASS_COMPANION, 'expParams': [30, 20, 30, 30],
            'traits': [{'code': 22, 'dataId': 0, 'value': 0.95}, {'code': 22, 'dataId': 1, 'value': 0.05},
                       {'code': 22, 'dataId': 2, 'value': 0.04}],
            'learnings': [], 'name': 'Companion', 'note': 'Stats for NovaPets pets.', 'params': params}


# ---------------------------------------------------------------- pet skills (battle only, free)
def skill(i, name, icon, desc, msg, scope, anim, dmg_type=0, formula='0', hit=0, crit=False, element=0, repeats=1, effects=None):
    return {'id': i, 'animationId': anim,
            'damage': {'critical': crit, 'elementId': element, 'formula': formula, 'type': dmg_type, 'variance': 15},
            'description': desc, 'effects': effects or [], 'hitType': hit, 'iconIndex': icon,
            'message1': msg, 'message2': '', 'mpCost': 0, 'name': name, 'note': 'Pet skill (NovaPets).', 'occasion': 1,
            'repeats': repeats, 'requiredWtypeId1': 0, 'requiredWtypeId2': 0, 'scope': scope, 'speed': 0,
            'stypeId': 0, 'successRate': 100, 'tpCost': 0, 'tpGain': 0}


PHYS = 1
SKILLS = [
    skill(SK_BITE, 'Bite', 76, 'Bites one enemy.', ' leaps in and bites!', 1, 16, 1, 'a.atk * 4 - b.def * 2', 1, True, PHYS),
    skill(SK_HOWL, 'Howl', 73, 'Raises ATK of all allies for 3 turns.', ' lets out a rallying howl!', 8, 37,
          effects=[{'code': 31, 'dataId': 2, 'value1': 3, 'value2': 0}]),
    skill(SK_SCRATCH, 'Scratch', 76, 'Scratches one enemy twice.', ' scratches wildly!', 1, 16, 1, 'a.atk * 2.5 - b.def * 1.5', 1, True, PHYS, 2),
    skill(SK_POUNCE, 'Pounce', 76, 'A heavy pounce on one enemy.', ' pounces with all its might!', 1, 28, 1, 'a.atk * 5 + a.agi - b.def * 2', 1, True, PHYS),
    skill(SK_PECK, 'Peck', 76, 'Pecks one enemy.', ' pecks furiously!', 1, 11, 1, 'a.atk * 3 + a.agi - b.def * 2', 1, True, PHYS),
    skill(SK_CHEER, 'Cheep Cheer', 72, 'Restores a little HP to all allies.', ' cheeps a happy little song!', 8, 43, 3, 'a.mat + 40'),
    skill(SK_TALON, 'Talon Dive', 76, 'Dives at one enemy, talons first.', ' dives from above!', 1, 16, 1, 'a.atk * 4 + a.agi - b.def * 2', 1, True, PHYS),
    skill(SK_HOOT, 'Moonlit Hoot', 72, 'Restores HP to all allies.', ' hoots softly under its breath!', 8, 43, 3, 'a.mat * 1.5 + 50'),
]


# ---------------------------------------------------------------- pets (actors that never join the party)
def pet(i, name, nick, char, idx, skills_note, assist, passive, profile, sound=None):
    note = '<pet>\n<pet skills: %s>\n<pet assist: %d>\n<pet passive: %d>' % (skills_note, assist, passive)
    if sound: note += '\n<pet sound: %s>' % sound
    return {'id': i, 'battlerName': '', 'characterIndex': idx, 'characterName': char, 'classId': CLASS_COMPANION,
            'equips': [0, 0, 0, 0, 0], 'faceIndex': 0, 'faceName': '', 'traits': [], 'initialLevel': 1, 'maxLevel': 99,
            'name': name, 'nickname': nick, 'note': note, 'profile': profile}


PETS = [
    pet(ACTOR_HOUND, 'Loyal Hound', 'Bred for the royal hunt', 'Nature', 0, '%d, %d@12' % (SK_BITE, SK_HOWL), 35, DI.PET_HOUND,
        'A brave hound from the Old Breeder\'s line. Never lets go\nof a bite, and never lets go of a friend.', 'Dog'),
    pet(ACTOR_CAT, 'Alley Cat', 'Queen of the back streets', 'Nature', 1, '%d, %d@12' % (SK_SCRATCH, SK_POUNCE), 35, DI.PET_CAT,
        'A clever street cat that hears trouble long before you do.\nAccepts you. Mostly.', 'Cat'),
    pet(ACTOR_CHICK, 'Lucky Chick', 'Finder of shiny things', 'Nature', 2, '%d, %d@12' % (SK_PECK, SK_CHEER), 30, DI.PET_CHICK,
        'A chick with very big ambitions and a talent for\nturning up coins, gems and the odd lost ring.'),
    pet(ACTOR_OWL, 'Barn Owl', 'Keeper of forgotten words', '$Pet_BarnOwl', 0, '%d, %d@12' % (SK_TALON, SK_HOOT), 30, DI.PET_OWL,
        'A wise owl that whispers forgotten words to anyone\npatient enough to listen at night.'),
]


# ---------------------------------------------------------------- Wren's adoption talk (common event body)
def adoption_event():
    def msg(indent, *lines, speaker='Wren'):
        out = [cmd(101, ['', 0, 0, 2], indent)]
        if speaker: out.append(cmd(401, ['\\C[6]%s:\\C[0]' % speaker], indent))
        return out + [cmd(401, [l], indent) for l in lines]
    lst = msg(0, 'Who catches your eye? They\'ll walk with you,', 'and help out when a fight breaks out.')
    choices = ['%s - %d Z' % (n, p) for (_, n, p, _) in ADOPT] + ['Not today']
    lst.append(cmd(102, [choices, len(ADOPT), 0, 2, 0]))
    for k, (aid, name, price, sound) in enumerate(ADOPT):
        lst.append(cmd(402, [k, choices[k]]))
        lst.append(cmd(111, [12, '$gameParty.hasNovaPet(%d)' % aid], 1))
        lst += msg(2, 'The %s already adores you!' % name, 'Every pet needs only one hero.')
        lst.append(cmd(0, [], 2))
        lst.append(cmd(411, [], 1))
        lst.append(cmd(111, [7, price, 0], 2))
        lst.append(cmd(125, [1, 0, price], 3))
        lst.append(cmd(250, [{'name': sound, 'volume': 80, 'pitch': 100, 'pan': 0}], 3))
        lst.append(cmd(356, ['NovaPet add %d' % aid], 3))
        lst.append(cmd(356, ['NovaPet active %d' % aid], 3))
        lst += msg(3, '\\C[14]%s\\C[0] joined you!' % name, speaker=None)
        lst += msg(3, 'Look after each other out there. You can send', 'a pet home and swap any time from the Pets menu.')
        lst.append(cmd(0, [], 3))
        lst.append(cmd(411, [], 2))
        lst += msg(3, 'Ah... that\'s a little more than you have.', 'Come back soon - they\'ll wait for you.')
        lst.append(cmd(0, [], 3))
        lst.append(cmd(412, [], 2))
        lst.append(cmd(0, [], 2))
        lst.append(cmd(412, [], 1))
        lst.append(cmd(0, [], 1))
    lst.append(cmd(402, [len(ADOPT), choices[-1]]))
    lst += msg(1, 'No rush. A companion should choose you as much', 'as you choose them.')
    lst.append(cmd(0, [], 1))
    lst.append(cmd(404, []))
    return lst


PLUGIN_ENTRY = ('{"name":"NovaPets","status":true,"description":"Pet companions: one active pet follows the party '
                'on the map, jumps into battle to help, and has its own screen in the main menu.",'
                '"parameters":{"Menu Command":"Pets","Assist Message":"%1 jumps in!"}}')


def register_plugin():
    path = L.PROJ + 'js/plugins.js'
    src = open(path, encoding='utf8').read()
    if '"name":"NovaPets"' in src: return
    src = re.sub(r'\}\n\];\s*$', '},\n' + PLUGIN_ENTRY + '\n];\n', src)
    with open(path, 'w', encoding='utf8', newline='') as f: f.write(src)


def main():
    Classes, Skills, Actors = load('Classes'), load('Skills'), load('Actors')
    put(Classes, CLASS_COMPANION, companion_class())
    for s in SKILLS: put(Skills, s['id'], s)
    for p in PETS: put(Actors, p['id'], p)
    save('Classes', Classes); save('Skills', Skills); save('Actors', Actors)
    register_plugin()
    print('pets', len(PETS), 'pet skills', len(SKILLS))


if __name__ == '__main__':
    main()
