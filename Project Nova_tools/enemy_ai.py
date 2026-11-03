# Action patterns for every enemy (Database > Enemies > Action Patterns) and the skills they charge (NovaCharge).
# RPG Maker picks among the actions whose conditions hold, only from those rated within 2 of the best one, so a
# conditional action rated 8 takes over when it applies (an opener on turn 1, a charge every 3 turns, a heal
# below half HP) and the rest of the time the enemy uses its ordinary moves.
#   python3 enemy_ai.py           -> report what would change
#   python3 enemy_ai.py --apply   -> write data/Enemies.json (RPG Maker editor must be closed)
import json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import nova_maplib as L

A = (0, 0, 0)                                # always
def T(a, b=0): return (1, a, b)              # turn a + b*X (b = 0: only turn a)
def HP(lo, hi): return (2, lo, hi)           # HP between lo and hi (0-1)

# enemy id: ([(skill name, condition, rating), ...], [charged skill names], charge time % or None)
AI = {
    1: ([('Bite', A, 5), ('Blood Suck', A, 3), ('Blood Suck', HP(0, 0.5), 7)], [], None),
    2: ([('Tackle', A, 5), ('Acid Spit', T(2, 3), 7)], [], None),
    3: ([('Slash', A, 5), ('Battle Roar', T(1), 8), ('Smash', T(3, 3), 8), ('Smash', HP(0, 0.35), 6)], ['Smash'], None),
    4: ([('Smash', A, 5), ('Horn Charge', T(2, 3), 8), ('Battle Roar', HP(0, 0.5), 6)], ['Horn Charge'], None),
    5: ([('Bite', A, 6), ('Poison Fang', A, 3), ('Slip Away', HP(0, 0.25), 7)], [], None),
    6: ([('Stab', A, 5), ('Venom Sting', T(1, 2), 6)], [], None),
    7: ([('Poison Fang', A, 5), ('Constrict', T(2, 2), 7)], [], None),
    8: ([('Vine Lash', A, 5), ('Spore Cloud', T(1), 8), ('Spore Cloud', T(4, 4), 7)], [], None),
    9: ([('Stab', A, 5), ('Cheap Shot', A, 3), ('Slip Away', HP(0, 0.3), 8), ('Slip Away', T(5), 8)], [], None),
    10: ([('Mana Bolt', A, 5), ('Fire', T(2, 2), 7)], [], None),
    11: ([('Slash', A, 5), ('Cheap Shot', A, 2), ('Cheap Shot', T(1), 7)], [], None),
    12: ([('Stab', A, 5), ('Aqua', T(2, 2), 7)], [], None),
    13: ([('Aqua', A, 5), ('Numbing Touch', T(2, 3), 7)], [], None),
    14: ([('Poison Fang', A, 5), ('Web Shot', T(1), 8), ('Web Shot', T(4, 4), 7)], [], None),
    15: ([('Stab', A, 5), ('Venom Sting', A, 4), ('Harden', HP(0, 0.5), 6)], [], None),
    16: ([('Slash', A, 5), ('Harden', T(1), 7)], [], None),
    17: ([('Bite', A, 5), ('Poison Fang', T(2, 2), 6)], [], None),
    18: ([('Fire', A, 5), ('Stab', A, 3), ('Umbra', T(3, 3), 7)], [], None),
    19: ([('Bite', A, 5), ('Rending Claws', T(3, 3), 8), ('Battle Roar', HP(0, 0.5), 6)], ['Rending Claws'], None),
    20: ([('Stab', A, 5), ('Umbra', A, 4), ('Curse', T(1), 8)], [], None),
    21: ([('Fire', A, 5), ('Frost', A, 5), ('Spark', T(3, 3), 8), ('Heal', HP(0, 0.5), 6)], ['Spark'], None),
    22: ([('Umbra', A, 5), ('Baleful Gaze', T(2, 3), 7)], [], None),
    23: ([('Smash', A, 5), ('Ground Pound', T(3, 3), 8), ('Ground Pound', HP(0, 0.3), 6)], ['Ground Pound'], None),
    24: ([('Slash', A, 5), ('Harden', T(1), 8), ('Stone Gaze', T(4, 4), 8)], ['Stone Gaze'], None),
    25: ([('Constrict', A, 5), ('Aqua', A, 4), ('Bewitch', T(2, 3), 7)], [], None),
    26: ([('Stab', A, 5), ('Stone Gaze', T(3, 3), 8)], ['Stone Gaze'], None),
    27: ([('Life Drain', A, 5), ('Curse', T(1), 8), ('Life Drain', HP(0, 0.5), 7)], [], None),
    28: ([('Fire', A, 5), ('Flame Burst', T(3, 3), 8), ('Flame Burst', HP(0, 0.3), 6)], ['Flame Burst'], None),
    29: ([('Aqua', A, 5), ('Tidal Wave', T(3, 3), 8), ('Heal', HP(0, 0.5), 6)], ['Tidal Wave'], None),
    30: ([('Smash', A, 5), ('Harden', T(1), 8), ('Ground Pound', T(3, 3), 8)], ['Ground Pound'], None),
    31: ([('Gust', A, 5), ('Aero Storm', T(3, 3), 8)], ['Aero Storm'], None),
    32: ([('Bite', A, 5), ('Smash', T(2, 3), 8)], ['Smash'], None),
    33: ([('Umbra', A, 5), ('Mana Rupture', T(2, 3), 7), ('Dark Nebula', T(4, 4), 8), ('Heal', HP(0, 0.5), 6)],
         ['Dark Nebula'], None),
    34: ([('Slash', A, 5), ('Battle Roar', T(1), 8), ('Sweep', T(3, 3), 8), ('Battle Roar', HP(0, 0.4), 6)], ['Sweep'], None),
    35: ([('Bite', A, 5), ('Venom Breath', T(2, 3), 7), ('Fire Breath', T(3, 3), 8), ('Fire Breath', HP(0, 0.3), 6)],
         ['Fire Breath'], 65),
    36: ([('Blood Suck', A, 5), ('Bewitch', T(2, 4), 7), ('Life Drain', HP(0, 0.5), 7), ('Dark Nebula', T(4, 4), 8)],
         ['Dark Nebula'], 65),
    37: ([('Bite', A, 5), ('Tail Sweep', A, 4), ('Battle Roar', T(1), 8), ('Wyrmfire', T(4, 4), 9),
          ('Wyrmfire', HP(0, 0.3), 7)], ['Wyrmfire'], 70),
    38: ([('Bite', A, 5), ('Rending Claws', T(2, 2), 6)], [], None),
    39: ([('Attack', A, 5), ('Frost Iai', A, 4), ('Ittōryū: Kesagiri', T(3, 3), 8)], ['Ittōryū: Kesagiri'], None),
    40: ([('Slash', A, 5), ('Cheap Shot', A, 3), ('Slip Away', HP(0, 0.2), 7)], [], None),
    41: ([('Slash', A, 5), ('Battle Roar', T(1), 8), ('Sweep', T(3, 3), 8)], ['Sweep'], None),
    # Dark Fantasy pack enemies (new_enemies.py)
    42: ([('Slash', A, 5), ('Shield Bash', A, 3), ('Battle Roar', T(1), 8), ('Sweep', T(3, 3), 8)], ['Sweep'], None),
    43: ([('Slash', A, 5), ('Holy Strike', A, 4), ('Iron Wall', T(1), 7), ('Radiant Cleave', T(3, 3), 8)],
         ['Radiant Cleave'], None),
    44: ([('Venom Breath', A, 5), ('Acid Spit', A, 4), ('Spore Cloud', T(2, 3), 7), ('Heal', HP(0, 0.5), 6)], [], None),
    45: ([('Lumen', A, 5), ('Greater Heal', A, 3), ('Greater Heal', HP(0, 0.6), 7), ('Purify', T(4, 4), 6),
          ('Holy Radiance', T(3, 3), 8)], ['Holy Radiance'], None),
    46: ([('Life Drain', A, 5), ('Umbra', A, 4), ('Curse', T(1), 8), ('Mana Rupture', T(3, 3), 8)], ['Mana Rupture'], None),
    47: ([('Rending Claws', A, 5), ('Umbra', A, 4), ('Bewitch', T(2, 3), 7), ('Dark Nebula', T(3, 3), 8)],
         ['Dark Nebula'], None),
    48: ([('Umbra', A, 5), ('Shadowbind', A, 3), ('Phantom Legion', T(2, 3), 7), ('Mana Rupture', T(4, 4), 8),
          ('Dark Nebula', HP(0, 0.4), 6)], ['Mana Rupture', 'Phantom Legion'], 65),
    49: ([('Lumen', A, 5), ('Holy Radiance', A, 3), ('Hex of Dusk', T(2, 3), 7), ('Greater Heal', HP(0, 0.5), 6),
          ('Seraphic Ray', T(3, 3), 8)], ['Seraphic Ray'], 65),
}


def set_tag(note, tag, value):
    """<tag: value> in the note: replaced, added, or removed when value is None."""
    note = re.sub(r'\n?<%s:[^>]*>' % re.escape(tag), '', note)
    if value is None: return note
    return (note + '\n' if note and not note.endswith('\n') else note) + '<%s: %s>' % (tag, value)


def main(apply):
    skills = json.load(open(L.DATA + 'Skills.json', encoding='utf8'))
    by_name = {s['name']: s['id'] for s in skills[::-1] if s}       # lowest id wins for duplicate names
    enemies = json.load(open(L.DATA + 'Enemies.json', encoding='utf8'))
    changed = 0
    for eid, (actions, charged, ctime) in sorted(AI.items()):
        e = enemies[eid]
        new = [{'conditionParam1': c[1], 'conditionParam2': c[2], 'conditionType': c[0], 'rating': r,
                'skillId': by_name[name]} for name, c, r in actions]
        note = set_tag(e['note'], 'charge', ', '.join(charged) if charged else None)
        note = set_tag(note, 'charge time', ctime)
        if new != e['actions'] or note != e['note']:
            changed += 1
            print('%2d %-15s %s%s' % (eid, e['name'], ', '.join(a[0] for a in actions),
                                      ('   charges: ' + ', '.join(charged)) if charged else ''))
        e['actions'], e['note'] = new, note
    if apply:
        with open(L.DATA + 'Enemies.json', 'w', encoding='utf8', newline='') as f:
            f.write('[\n' + ',\n'.join(json.dumps(x, ensure_ascii=False, separators=(',', ':')) for x in enemies) + '\n]')
    print('%d enemies %s' % (changed, 'updated' if apply else 'would change (--apply to write)'))


if __name__ == '__main__':
    main('--apply' in sys.argv)
