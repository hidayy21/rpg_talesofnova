# Database for the NovaPets plugin: the Companion class, pet skills, pet actors, the adoption talk at Whisker & Paw
# (common event CE_PETS) and the plugin's entry in js/plugins.js. Idempotent: re-running rewrites the same ids.
# The old companion accessories (armors PET_*) stay: each pet hands its armor's params/traits to the whole party;
# the pets made from the side-view battlers (pet_sprites.py) get theirs here (armors 71-79).
#
#   python pet_data.py            close the RPG Maker editor first: it overwrites the database when it saves
import json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import data_ids as DI
import nova_maplib as L

DATA = L.DATA
CLASS_COMPANION = 7
ACTOR_HOUND, ACTOR_CAT, ACTOR_CHICK, ACTOR_OWL = 7, 8, 9, 10
ACTOR_WOLF, ACTOR_FOX, ACTOR_BAT, ACTOR_SLIME, ACTOR_FAIRY, ACTOR_GHOST, ACTOR_HORNET, ACTOR_VIPER, ACTOR_GOLEM = range(12, 21)
SK_BITE, SK_HOWL, SK_SCRATCH, SK_POUNCE, SK_PECK, SK_CHEER, SK_TALON, SK_HOOT = range(141, 149)
(SK_FANG_RUSH, SK_HUNTING_CALL, SK_FOXFIRE, SK_FOX_DANCE, SK_LEECH, SK_SCREECH, SK_BODY_SLAM, SK_GEL_MEND,
 SK_FAIRY_DUST, SK_POLLEN, SK_SPECTRAL, SK_WAIL, SK_STING, SK_SWARM, SK_VENOM, SK_CONSTRICT, SK_IRON_FIST,
 SK_BULWARK) = range(170, 188)
(PET_WOLF, PET_FOX, PET_BAT, PET_SLIME, PET_FAIRY, PET_GHOST, PET_HORNET, PET_VIPER, PET_GOLEM) = range(71, 80)
# (actor, name, price, sound) offered by Wren. The other pets are found on the road: NovaPet add <id>.
ADOPT = [(ACTOR_HOUND, 'Loyal Hound', 3000, 'Dog'), (ACTOR_CAT, 'Alley Cat', 3000, 'Cat'), (ACTOR_CHICK, 'Lucky Chick', 4000, 'Item3'),
         (ACTOR_OWL, 'Barn Owl', 3500, 'Crow')]


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

FIRE, DARK = 2, 9
POISON, BLIND, SLEEP, PARALYSIS = 4, 5, 10, 22
add_state = lambda state, chance: {'code': 21, 'dataId': state, 'value1': chance, 'value2': 0}
buff = lambda param: {'code': 31, 'dataId': param, 'value1': 3, 'value2': 0}
debuff = lambda param: {'code': 32, 'dataId': param, 'value1': 3, 'value2': 0}
MAGIC = 2
SKILLS += [
    skill(SK_FANG_RUSH, 'Fang Rush', 76, 'Rushes one enemy, fangs bared.', ' rushes in, fangs bared!', 1, 16, 1, 'a.atk * 4 + a.agi - b.def * 2', 1, True, PHYS),
    skill(SK_HUNTING_CALL, 'Hunting Call', 82, 'Raises AGI of all allies for 3 turns.', ' howls the hunting call!', 8, 37, effects=[buff(6)]),
    skill(SK_FOXFIRE, 'Foxfire', 64, 'Fire damage to one enemy.', ' conjures a flickering foxfire!', 1, 66, 1, 'a.mat * 3 - b.mdf * 1.5', MAGIC, False, FIRE),
    skill(SK_FOX_DANCE, 'Lantern Dance', 64, 'Fire damage to all enemies.', ' dances, scattering foxfire everywhere!', 2, 68, 1, 'a.mat * 2 - b.mdf', MAGIC, False, FIRE),
    skill(SK_LEECH, 'Leech Bite', 76, 'Drains HP from one enemy.', ' sinks its fangs in!', 1, 58, 5, 'a.atk * 3 - b.def * 1.5', 1, False, PHYS),
    skill(SK_SCREECH, 'Sonic Screech', 74, 'May Blind all enemies.', ' lets out an ear-splitting screech!', 2, 34, effects=[add_state(BLIND, 0.4)]),
    skill(SK_BODY_SLAM, 'Body Slam', 78, 'Bounces into one enemy.', ' bounces into the enemy!', 1, 39, 1, 'a.atk * 3 + a.def - b.def * 2', 1, True, PHYS),
    skill(SK_GEL_MEND, 'Gel Mend', 72, 'Restores a little HP to all allies.', ' splits off soothing gel!', 8, 43, 3, 'a.mat + 60'),
    skill(SK_FAIRY_DUST, 'Fairy Dust', 72, 'Restores HP to one ally.', ' sprinkles glittering fairy dust!', 7, 41, 3, 'a.mat * 2 + 60'),
    skill(SK_POLLEN, 'Drowsy Pollen', 74, 'May put all enemies to Sleep.', ' scatters drowsy pollen!', 2, 33, effects=[add_state(SLEEP, 0.35)]),
    skill(SK_SPECTRAL, 'Spectral Touch', 71, 'Darkness damage to one enemy.', ' reaches through with an icy hand!', 1, 101, 1, 'a.mat * 3 - b.mdf * 1.5', MAGIC, False, DARK),
    skill(SK_WAIL, 'Dread Wail', 74, 'Lowers ATK of all enemies for 3 turns.', ' lets out a dreadful wail!', 2, 55, effects=[debuff(2)]),
    skill(SK_STING, 'Sting', 76, 'Stings one enemy. May Poison.', ' darts in and stings!', 1, 11, 1, 'a.atk * 3 + a.agi - b.def * 2', 1, True, PHYS,
          effects=[add_state(POISON, 0.5)]),
    skill(SK_SWARM, 'Swarm Strike', 77, 'Strikes 3 random enemies.', ' strikes again and again!', 5, 12, 1, 'a.atk * 2 + a.agi - b.def * 1.5', 1, True, PHYS),
    skill(SK_VENOM, 'Venom Fang', 76, 'Bites one enemy. Often Poisons.', ' strikes with venomous fangs!', 1, 59, 1, 'a.atk * 3 - b.def * 1.5', 1, True, PHYS,
          effects=[add_state(POISON, 0.8)]),
    skill(SK_CONSTRICT, 'Constrict', 78, 'Crushes one enemy. May Paralyze.', ' coils tight around the enemy!', 1, 57, 1, 'a.atk * 4 - b.def * 2', 1, False, PHYS,
          effects=[add_state(PARALYSIS, 0.3)]),
    skill(SK_IRON_FIST, 'Iron Fist', 78, 'A crushing blow to one enemy.', ' brings down an iron fist!', 1, 21, 1, 'a.atk * 5 - b.def * 2', 1, True, PHYS),
    skill(SK_BULWARK, 'Bulwark', 81, 'Raises DEF of all allies for 3 turns.', ' raises its great arm over the party!', 8, 51, effects=[buff(3)]),
]


# ---------------------------------------------------------------- pets (actors that never join the party)
def pet(i, name, nick, char, idx, skills_note, assist, passive, profile, sound=None, battler='', side=False):
    note = '<pet>\n<pet skills: %s>\n<pet assist: %d>\n<pet passive: %d>' % (skills_note, assist, passive)
    if sound: note += '\n<pet sound: %s>' % sound
    if side: note += '\n<pet side view>'
    return {'id': i, 'battlerName': battler, 'characterIndex': idx, 'characterName': char, 'classId': CLASS_COMPANION,
            'equips': [0, 0, 0, 0, 0], 'faceIndex': 0, 'faceName': '', 'traits': [], 'initialLevel': 1, 'maxLevel': 99,
            'name': name, 'nickname': nick, 'note': note, 'profile': profile}


def two(a, b): return '%d, %d@12' % (a, b)


PETS = [
    pet(ACTOR_HOUND, 'Loyal Hound', 'Bred for the royal hunt', 'Nature', 0, two(SK_BITE, SK_HOWL), 35, DI.PET_HOUND,
        'A brave hound from the Old Breeder\'s line. Never lets go\nof a bite, and never lets go of a friend.', 'Dog'),
    pet(ACTOR_CAT, 'Alley Cat', 'Queen of the back streets', 'Nature', 1, two(SK_SCRATCH, SK_POUNCE), 35, DI.PET_CAT,
        'A clever street cat that hears trouble long before you do.\nAccepts you. Mostly.', 'Cat', 'Pet_Cat'),
    pet(ACTOR_CHICK, 'Lucky Chick', 'Finder of shiny things', 'Nature', 2, two(SK_PECK, SK_CHEER), 30, DI.PET_CHICK,
        'A chick with very big ambitions and a talent for\nturning up coins, gems and the odd lost ring.', None, 'Pet_Chicken'),
    pet(ACTOR_OWL, 'Barn Owl', 'Keeper of forgotten words', '$Pet_BarnOwl', 0, two(SK_TALON, SK_HOOT), 30, DI.PET_OWL,
        'A wise owl that whispers forgotten words to anyone\npatient enough to listen at night.', 'Crow', 'Pet_Owl', True),
    pet(ACTOR_WOLF, 'Grey Wolf', 'Lone runner of the north woods', 'Pet_Animals', 1, two(SK_FANG_RUSH, SK_HUNTING_CALL), 35, PET_WOLF,
        'A grey wolf that left its pack to run with yours.\nQuick to strike, quicker to guard your back.', 'Wolf', 'Pet_Wolf'),
    pet(ACTOR_FOX, 'Ember Fox', 'Trickster with fire in its tail', '$Pet_Fox', 0, two(SK_FOXFIRE, SK_FOX_DANCE), 30, PET_FOX,
        'A red fox whose tail glows like a coal at night.\nIt plays tricks on enemies and, now and then, on you.', 'Growl', 'Pet_Fox', True),
    pet(ACTOR_BAT, 'Cave Bat', 'Night flier with a taste for red', 'Monster', 0, two(SK_LEECH, SK_SCREECH), 30, PET_BAT,
        'A bat from the deep caves. Sleeps all day upside down\nin your pack and squeaks at every shadow.', 'Monster3', 'Pet_Bat'),
    pet(ACTOR_SLIME, 'Blue Slime', 'Squishy, sticky and devoted', 'Monster', 1, two(SK_BODY_SLAM, SK_GEL_MEND), 30, PET_SLIME,
        'A friendly slime that wobbles after you everywhere.\nSoaks up blows, and leaves a damp trail.', 'Water1', 'Pet_Slime'),
    pet(ACTOR_FAIRY, 'Leaf Fairy', 'Small, bright and a little bossy', 'Nature', 4, two(SK_FAIRY_DUST, SK_POLLEN), 30, PET_FAIRY,
        'A forest fairy who decided you need looking after.\nShe is probably right.', 'Saint1', 'Pet_Fairy'),
    pet(ACTOR_GHOST, 'Little Ghost', 'Bound to you by an old promise', 'Monster', 6, two(SK_SPECTRAL, SK_WAIL), 30, PET_GHOST,
        'A lost spirit that cannot remember its name, only that\nit once promised to protect someone.', 'Darkness1', 'Pet_Ghost'),
    pet(ACTOR_HORNET, 'War Hornet', 'Tiny, loud and fearless', '$Pet_Hornet', 0, two(SK_STING, SK_SWARM), 35, PET_HORNET,
        'A hornet the size of a fist with the temper of a bear.\nIt buzzes at anything bigger than itself.', 'Wind1', 'Pet_Hornet', True),
    pet(ACTOR_VIPER, 'Violet Viper', 'Coiled, patient and loyal', '$Pet_Snake', 0, two(SK_VENOM, SK_CONSTRICT), 30, PET_VIPER,
        'A violet snake from the marshes. Rests coiled around\nyour shoulders and strikes before the enemy blinks.', 'Monster1', 'Pet_Snake', True),
    pet(ACTOR_GOLEM, 'Iron Golem', 'Ancient guardian, newly awakened', '$Pet_IronGolem', 0, two(SK_IRON_FIST, SK_BULWARK), 25, PET_GOLEM,
        'A guardian of a forgotten kingdom, woken after a\nthousand years. It follows you without a word.', 'Hammer', 'Pet_IronGolem', True),
]


# ---------------------------------------------------------------- party bonus of the new pets (armors, as in kingdom_data.py)
def companion_armors(armors):
    template = armors[4]
    xp = lambda i, v: {'code': 22, 'dataId': i, 'value': v}

    def companion(idx, name, icon, price, desc, params, traits=()):
        a = json.loads(json.dumps(template))
        p = [0] * 8
        for k, v in params.items(): p[['mhp', 'mmp', 'atk', 'def', 'mat', 'mdf', 'agi', 'luk'].index(k)] = v
        a.update({'id': idx, 'name': name, 'iconIndex': icon, 'price': price, 'description': desc, 'params': p,
                  'atypeId': 1, 'etypeId': 5, 'traits': [{'code': 22, 'dataId': 1, 'value': 0}] + list(traits),
                  'note': '<companion>\n<book:no>'})
        put(armors, idx, a)
    companion(PET_WOLF, 'Companion: Grey Wolf', 140, 3500, 'A grey wolf that runs at your side.\nATK +8, AGI +8.', {'atk': 8, 'agi': 8})
    companion(PET_FOX, 'Companion: Ember Fox', 140, 3500, 'A fox with fire in its tail.\nM.Attack +10, Fire damage -15%.', {'mat': 10},
              [{'code': 11, 'dataId': FIRE, 'value': 0.85}])
    companion(PET_BAT, 'Companion: Cave Bat', 149, 3500, 'A bat that sees in the dark.\nAGI +10, Hit +5%.', {'agi': 10}, [xp(0, 0.05)])
    companion(PET_SLIME, 'Companion: Blue Slime', 135, 3500, 'A slime that soaks up blows.\nMax HP +80, DEF +8.', {'mhp': 80, 'def': 8})
    companion(PET_FAIRY, 'Companion: Leaf Fairy', 135, 3500, 'A fairy who looks after you.\nMax MP +30, M.Defense +10.', {'mmp': 30, 'mdf': 10})
    companion(PET_GHOST, 'Companion: Little Ghost', 149, 3500, 'A spirit that keeps an old promise.\nM.Defense +8, Magic Evasion +5%.', {'mdf': 8},
              [xp(4, 0.05)])
    companion(PET_HORNET, 'Companion: War Hornet', 140, 3500, 'A hornet with the temper of a bear.\nATK +6, Critical +5%.', {'atk': 6}, [xp(2, 0.05)])
    companion(PET_VIPER, 'Companion: Violet Viper', 140, 3500, 'A snake that shares its resistance.\nDEF +8, immune to Poison.', {'def': 8},
              [{'code': 14, 'dataId': POISON, 'value': 0}])
    companion(PET_GOLEM, 'Companion: Iron Golem', 135, 3500, 'An ancient guardian at your back.\nDEF +15, Max HP +60.', {'def': 15, 'mhp': 60})


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
    Classes, Skills, Actors, Armors, CE = load('Classes'), load('Skills'), load('Actors'), load('Armors'), load('CommonEvents')
    put(Classes, CLASS_COMPANION, companion_class())
    for s in SKILLS: put(Skills, s['id'], s)
    for p in PETS: put(Actors, p['id'], p)
    companion_armors(Armors)
    put(CE, DI.CE_PETS, {'id': DI.CE_PETS, 'list': adoption_event() + [cmd(0, [])], 'name': 'Shop: Companions (Whisker & Paw)',
                         'switchId': 1, 'trigger': 0})
    save('Classes', Classes); save('Skills', Skills); save('Actors', Actors); save('Armors', Armors); save('CommonEvents', CE)
    register_plugin()
    print('pets', len(PETS), 'pet skills', len(SKILLS))


if __name__ == '__main__':
    import tileset_wizard as W
    if W.editor_running() and '--force' not in sys.argv:
        sys.exit('Editor RPG Maker masih terbuka: tutup dulu (simpan pekerjaanmu), lalu jalankan lagi.')
    main()
