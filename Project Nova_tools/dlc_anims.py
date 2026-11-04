# Battle animations from two DLCs, added after the RTP and "Nova:" signature ones, and the skills that use them.
#  - Animations Collection III: Thaumaturgy (Andy Chen): the 30 FPS sheets and the Demo Project's database entries,
#    as "Thaum: ..." with the [30fps] tag (and [fit] for full-screen ones) read by the NovaAnimFx plugin. The demo has
#    no sounds, so each gets the sound timings of the RTP animation it replaces, stretched to its length.
#    The six magic circles (Cast 01-06, long "a" / short "b") play under the caster: <cast animation: N> in the note.
#  - Pixel Animations (finalbossblues): the MV sheets, copied as img/animations/Px_*.png (drawn sharp by NovaAnimFx).
#    The sheets hold several small effects each; PX_CELLS says which cells make each one. "Px: ..." entries.
# Running it again updates the same entries (matched by name) and rewrites the skills' animation and cast tags.
#   python3 dlc_anims.py           -> report
#   python3 dlc_anims.py --apply   -> copy sheets, write Animations.json and Skills.json (RPG Maker editor closed)
import copy, json, os, re, shutil, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import nova_maplib as L

DLC = os.environ.get('NOVA_DLC') or next((p for p in (
    os.path.expanduser('~/Library/Application Support/Steam/steamapps/common/RPG Maker MV/dlc'),
    'C:/Program Files (x86)/Steam/steamapps/common/RPG Maker MV/dlc',
    'C:/Program Files/Steam/steamapps/common/RPG Maker MV/dlc') if os.path.isdir(p)), None)
THAUM = '/Animations Collection III - Thaumaturgy/'
PIXEL = '/Pixel Animations/anim_sheets/MV/'
ANIM_DIR = L.PROJ + 'img/animations/'
MAX_CELLS = 16

# ---------------------------------------------------------------- Thaumaturgy
# short name -> RTP animation whose sounds it takes (None = sounds given in THAUM_SE)
THAUM_SOUND_FROM = {
    'Blind': 60, 'Confuse': 63, 'Seal': 61, 'Benediction': 44, 'Resurrection': 50,
    'Tempest': 95, 'Torrent': 85, 'Inferno': 70, 'Upheaval': 90, 'Discharge': 80, 'Cocytus': 75,
    'Collapse': 105, 'Luminescence': 100, 'Nova': 110,
}
CAST_SE = {'01': ('Ice1', 120), '02': ('Darkness2', 120), '03': ('Heal1', 110),
           '04': ('Fire1', 120), '05': ('Magic1', 110), '06': ('Saint3', 120)}
CAST_SCALE = 70                     # the circles are drawn for front-view enemies; side-view heroes are smaller

# name: (short, hue, extra flash [r,g,b,a] at the climax or None)
THAUM_VARIANTS = {
    'Inferno (Pandemonium)': ('Inferno', 300, [255, 40, 160, 200]),
    'Luminescence (Judgment)': ('Luminescence', 200, [255, 220, 120, 200]),
    'Upheaval (Ragnarok)': ('Upheaval', 330, [255, 60, 30, 200]),
    'Collapse (Crimson)': ('Collapse', 60, [255, 30, 60, 200]),
    'Collapse (Endless Night)': ('Collapse', 300, [60, 60, 255, 200]),
    'Benediction (Aurora)': ('Benediction', 300, None),
    'Benediction (Regulus)': ('Benediction', 225, [255, 220, 120, 160]),
    'Resurrection (Gold)': ('Resurrection', 225, None),
}

# ---------------------------------------------------------------- Pixel Animations
# effect: (sheet, first cell, last cell)  - from the pack's individual frames, matched pixel for pixel to the sheets
PX_CELLS = {
    'arrow1': ('arrow', 0, 10), 'arrow2': ('arrow', 12, 18),
    'bite1': ('claw_bite', 0, 7), 'bite2': ('claw_bite', 8, 15), 'claw': ('claw_bite', 16, 21),
    'darkness1': ('darkness', 0, 2), 'darkness2': ('darkness', 3, 12), 'darkness3': ('darkness', 13, 22),
    'earth1': ('earth1', 0, 11), 'earth2': ('earth1', 12, 26),
    'earth3': ('earth2', 0, 7), 'earth4': ('earth2', 8, 13), 'earth5': ('earth2', 14, 19),
    'explosion1': ('explosion', 0, 9), 'explosion2': ('explosion', 10, 17),
    'fire1': ('fire', 0, 3), 'fire2': ('fire', 4, 9), 'fire3': ('fire', 10, 15), 'fire4': ('fire', 16, 26),
    'heal1': ('heal', 0, 8), 'heal2': ('heal', 9, 21), 'heal3': ('heal', 22, 33), 'heal4': ('heal', 34, 38),
    'heal5': ('heal', 40, 49),
    'holy1': ('holy', 0, 8), 'holy2': ('holy', 9, 14), 'holy3': ('holy', 15, 22),
    'ice1': ('ice', 0, 10), 'ice2': ('ice', 11, 23), 'ice3': ('ice', 24, 28), 'ice4': ('ice', 29, 36),
    'impact1': ('impact1', 0, 5), 'impact2': ('impact1', 6, 10), 'impact3': ('impact1', 11, 16),
    'impact4': ('impact1', 17, 21), 'impact5': ('impact1', 22, 27), 'impact6': ('impact2', 0, 3),
    'impact7': ('impact2', 4, 11),
    'lightning1': ('lightning', 0, 5), 'lightning2': ('lightning', 6, 11), 'lightning3': ('lightning', 12, 19),
    'lightning4': ('lightning', 20, 27),
    'smoke1': ('smoke', 0, 5), 'smoke2': ('smoke', 6, 9), 'smoke3': ('smoke', 10, 15),
    'poison': ('status_1', 0, 7), 'anger': ('status_1', 20, 23), 'daze': ('status_1', 24, 29),
    'hearts': ('status_2', 0, 7), 'sleep': ('status_2', 8, 15), 'shock': ('status_2', 16, 20),
    'skulls': ('status_2', 21, 28),
    'sword1': ('weapons_1', 0, 5), 'sword2': ('weapons_1', 6, 11), 'sword3': ('weapons_1', 12, 17),
    'sword4': ('weapons_1', 18, 23), 'sword5': ('weapons_1', 24, 31),
    'sparkle': ('weapons_2', 12, 15), 'crosshair': ('weapons_3', 11, 12),
    'water1': ('water', 0, 10), 'water3': ('water', 22, 33), 'water5': ('water', 42, 48),
    'wind1': ('wind', 0, 3), 'wind2': ('wind', 4, 9), 'wind3': ('wind', 10, 18), 'wind4': ('wind', 19, 24),
}
PX_SCALE = 200                      # the MV sheets are 3x pixels; 200% = 6x, still sharp (no smoothing)


def px(*layers, pos=1, se=(), scale=PX_SCALE, hue=0, hue2=0, loop=1):
    """layers: effect names, or (effect, start frame); at most two sheets. se: (frame, name, pitch[, volume])."""
    return dict(layers=[(l, 0) if isinstance(l, str) else l for l in layers], pos=pos, se=se, scale=scale,
                hue=hue, hue2=hue2, loop=loop)


PX_ANIMS = {
    'Bite': px('bite1', se=[(0, 'Attack2', 150), (3, 'Slash2', 80)]),
    'Venom Fang': px('bite2', ('poison', 5), hue=240, se=[(0, 'Attack2', 150), (3, 'Slash2', 80), (6, 'Poison', 100)]),
    'Claw': px('claw', se=[(0, 'Attack2', 200), (1, 'Slash2', 100)]),
    'Blood Claw': px('claw', hue=160, se=[(0, 'Attack2', 180), (1, 'Slash5', 110), (2, 'Absorb1', 150, 60)]),
    'Charm': px('hearts', pos=0, se=[(0, 'Absorb2', 150), (3, 'Up1', 150, 70)]),
    'Sleep': px('sleep', pos=0, se=[(0, 'Sleep', 100)]),
    'Dread': px('skulls', pos=0, se=[(0, 'Darkness3', 70), (2, 'Devil1', 120, 60)]),
    'Fury': px('anger', pos=0, loop=3, se=[(0, 'Monster1', 130, 70)]),
    'Daze': px('daze', pos=0, se=[(0, 'Absorb2', 70), (2, 'Raise2', 120, 70)]),
    'Shock': px('lightning4', ('shock', 4), se=[(0, 'Paralyze1', 120), (4, 'Thunder1', 150, 60)]),
    'Arrow': px('arrow2', se=[(0, 'Crossbow', 120), (4, 'Sword5', 120)]),
    'Arrow Rain': px('arrow1', se=[(0, 'Wind1', 150, 60), (6, 'Crossbow', 110), (8, 'Sword5', 120, 70)]),
    'Venom Arrow': px('arrow2', ('poison', 5), se=[(0, 'Crossbow', 120), (4, 'Sword5', 120), (6, 'Poison', 100)]),
    'Nerve Shot': px('arrow2', ('shock', 5), se=[(0, 'Crossbow', 120), (4, 'Sword5', 120), (6, 'Paralyze1', 120)]),
    'Gale Arrow': px('arrow2', ('wind3', 4), se=[(0, 'Crossbow', 120), (4, 'Wind4', 110), (8, 'Wind2', 120)]),
    'Hawk Eye': px('crosshair', ('sparkle', 8), pos=1, loop=4, se=[(0, 'Switch2', 150), (8, 'Powerup', 130)]),
    'Holy Cross': px('holy2', ('impact2', 2), se=[(0, 'Saint1', 120), (2, 'Blow3', 110)]),
    'Holy Pillar': px('holy1', se=[(0, 'Saint2', 110), (3, 'Flash1', 120, 70)]),
    'Angel Wings': px('holy3', ('heal2', 2), se=[(0, 'Saint4', 120), (2, 'Heal3', 100)]),
    'Mend': px('heal2', se=[(0, 'Heal3', 110), (4, 'Ice4', 150, 60)]),
    'Second Wind': px('heal3', pos=2, se=[(0, 'Heal1', 100), (4, 'Up1', 120, 70)]),
    'Still Mind': px('heal3', pos=2, hue=180, se=[(0, 'Heal1', 80), (4, 'Ice4', 120, 60)]),
    'Cheer': px('heal1', pos=2, se=[(0, 'Heal2', 130), (4, 'Up1', 140, 60)]),
    'Moonlight': px('heal5', hue=180, se=[(0, 'Starlight', 110), (3, 'Heal3', 120, 70)]),
    'Bubble': px('water5', se=[(0, 'Water1', 130), (4, 'Heal1', 120, 70)]),
    'Herbal': px('earth3', ('heal2', 4), pos=2, se=[(0, 'Pollen', 120, 70), (4, 'Heal3', 110)]),
    'Forest Blessing': px('earth3', ('heal1', 3), pos=2, se=[(0, 'Pollen', 120, 70), (3, 'Heal2', 110)]),
    'Thorns': px('earth5', pos=2, se=[(0, 'Twine', 120), (1, 'Slash3', 120, 70)]),
    'Stone Pillar': px('earth2', pos=2, se=[(0, 'Earth2', 120), (8, 'Crash', 130, 60)]),
    'Gust': px('wind1', ('wind1', 3), se=[(0, 'Wind1', 130), (3, 'Wind2', 150, 60)]),
    'Tailwind': px('wind2', pos=2, se=[(0, 'Wind4', 130, 70), (3, 'Up1', 130, 60)]),
    'Splash': px('water1', se=[(0, 'Water1', 110), (4, 'Water2', 120, 70)]),
    'Frost': px('ice1', se=[(0, 'Ice1', 110), (5, 'Ice4', 120)]),
    'Frost Fang': px('ice2', se=[(0, 'Sword5', 140), (2, 'Ice2', 110), (6, 'Ice5', 120)]),
    'Twin Snowfall': px('sword3', ('ice4', 3), se=[(0, 'Slash1', 140), (3, 'Ice4', 130)]),
    'Sasameyuki': px('sword1', ('ice3', 3), se=[(0, 'Slash1', 150), (3, 'Ice4', 150, 70)]),
    'Spark': px('lightning1', se=[(0, 'Thunder3', 120), (2, 'Thunder1', 150, 60)]),
    'Spectre': px('darkness1', ('darkness3', 2), se=[(0, 'Darkness1', 110), (2, 'Darkness3', 120, 70)]),
    'Hex': px('darkness3', ('skulls', 2), se=[(0, 'Darkness2', 110), (2, 'Down1', 100)]),
    'Smoke': px('smoke1', ('smoke3', 2), pos=2, se=[(0, 'Evasion2', 100), (1, 'Sand', 120, 70)]),
    'Fireball': px('fire2', ('explosion1', 5), se=[(0, 'Fire1', 130), (5, 'Explosion1', 130, 80)]),
    'Hellfire Bolt': px('fire2', ('explosion1', 5), hue=300, hue2=300, se=[(0, 'Fire1', 110), (5, 'Fire3', 110)]),
    'Flame Pillar': px('fire4', pos=2, se=[(0, 'Fire2', 120), (3, 'Fire1', 100, 70)]),
    'Kesagiri': px('sword1', ('impact1', 3), se=[(0, 'Slash1', 130), (3, 'Sword4', 120, 70)]),
    'Tsubame Gaeshi': px('sword5', se=[(0, 'Slash1', 140), (4, 'Slash1', 110)]),
    'Kiri-otoshi': px('sword2', ('impact4', 3), se=[(0, 'Sword5', 120), (3, 'Blow3', 110)]),
    'Blade': px('sword3', se=[(0, 'Slash1', 130)]),
    'Shield Bash': px('impact7', ('impact6', 1), se=[(0, 'Blow3', 100), (1, 'Shot1', 120, 70)]),
    'Strike': px('impact1', se=[(0, 'Blow1', 110)]),
    'Pound': px('impact5', ('impact3', 1), se=[(0, 'Blow3', 100), (1, 'Blow1', 80)]),
    'Crash': px('explosion2', se=[(0, 'Blow3', 90), (1, 'Earth1', 140, 70)]),
}

# ---------------------------------------------------------------- skills
# animation name (as in the database, without tags) -> skill ids that use it
SKILL_ANIMS = {
    # big full-screen spells: high tier and the legendary weapons' skills
    'Thaum: Inferno': [61],                         # Ember Requiem (Kael)
    'Thaum: Inferno (Pandemonium)': [163],          # Pandemonium Flame (Lysandre)
    'Thaum: Torrent': [88],                         # Maelstrom (Mira)
    'Thaum: Tempest': [102],                        # Requiem of the Last Gale (Zephyr's Requiem)
    'Thaum: Discharge': [100],                      # Thunderhead Arrow (Diana)
    'Thaum: Upheaval': [115],                       # Cataclysm Swing (Barion)
    'Thaum: Upheaval (Ragnarok)': [117],            # Ragnarök Cleave (Ragnafell)
    'Thaum: Cocytus': [135],                        # Ryūzetsu Hiden: Ginsetsu Ranbu (Yuki's story skill)
    'Thaum: Luminescence': [72],                    # Setsutei Kagura (Setsutei no Mikoto)
    'Thaum: Luminescence (Judgment)': [50],         # Sacred Judgment (Roland)
    'Thaum: Collapse': [92],                        # Void Collapse (Mira)
    'Thaum: Collapse (Endless Night)': [65],        # Regalia of Endless Night (Noctis Regalia)
    'Thaum: Collapse (Crimson)': [166],             # Crimson Sovereignty (Bloodrose Sovereign)
    'Thaum: Nova': [19],                            # Arcane Nova (Mira)
    'Thaum: Benediction': [123],                    # Grand Benediction (Mira)
    'Thaum: Benediction (Aurora)': [95],            # Aurora Benediction (Dawnbringer)
    'Thaum: Benediction (Regulus)': [110],          # Heart of Regulus (Regulus)
    'Thaum: Resurrection': [122],                   # Rebirth (Mira)
    'Thaum: Resurrection (Gold)': [108],            # Divine Intercession (Roland)
    'Thaum: Blind': [39],                           # Blinding Shot
    'Thaum: Confuse': [212],                        # Bewitch
    'Thaum: Seal': [62, 208],                       # Shadowbind, Curse
    # small effects: early skills, pets and enemies that shared a handful of RTP animations
    'Px: Bite': [141, 188, 170],                    # Bite (pet), Bite (enemy), Fang Rush
    'Px: Venom Fang': [184, 197],                   # Venom Fang, Poison Fang
    'Px: Claw': [143, 194, 147],                    # Scratch, Rending Claws (enemy), Talon Dive
    'Px: Blood Claw': [149, 164],                   # Rending Claws, Crimson Waltz (Lysandre)
    'Px: Charm': [150],                             # Allure
    'Px: Sleep': [179],                             # Drowsy Pollen
    'Px: Dread': [181],                             # Dread Wail
    'Px: Fury': [43, 52, 203],                      # Provoke, War Cry, Battle Roar
    'Px: Daze': [209],                              # Baleful Gaze
    'Px: Shock': [207],                             # Numbing Touch
    'Px: Arrow': [35],                              # Aimed Shot
    'Px: Arrow Rain': [37],                         # Arrow Rain
    'Px: Venom Arrow': [36],                        # Venom Arrow
    'Px: Nerve Shot': [97],                         # Nerve Shot
    'Px: Gale Arrow': [41],                         # Gale Arrow
    'Px: Hawk Eye': [38],                           # Hawk Eye
    'Px: Holy Cross': [46],                         # Holy Strike
    'Px: Holy Pillar': [76, 136],                   # Lumen, Radiant Ember
    'Px: Angel Wings': [124],                       # Lay on Hands
    'Px: Mend': [45, 178],                          # First Aid, Fairy Dust
    'Px: Second Wind': [128],                       # Second Wind
    'Px: Still Mind': [133],                        # Mokusō
    'Px: Cheer': [146],                             # Cheep Cheer
    'Px: Moonlight': [148],                         # Moonlit Hoot
    'Px: Bubble': [177],                            # Gel Mend
    'Px: Herbal': [126],                            # Herbal Remedy
    'Px: Forest Blessing': [127],                   # Forest Blessing
    'Px: Thorns': [200],                            # Vine Lash
    'Px: Stone Pillar': [210],                      # Stone Gaze
    'Px: Gust': [74],                               # Gust
    'Px: Tailwind': [96],                           # Tailwind
    'Px: Splash': [75],                             # Aqua
    'Px: Frost': [11],                              # Frost
    'Px: Frost Fang': [67],                         # Shimo no Kiba
    'Px: Twin Snowfall': [28],                      # Twin Snowfall
    'Px: Sasameyuki': [66],                         # Sasameyuki
    'Px: Spark': [10],                              # Spark
    'Px: Spectre': [180],                           # Spectral Touch
    'Px: Hex': [24],                                # Hex of Dusk
    'Px: Smoke': [202, 99],                         # Slip Away, Camouflage
    'Px: Fireball': [172],                          # Foxfire
    'Px: Hellfire Bolt': [153],                     # Hellfire
    'Px: Flame Pillar': [173],                      # Lantern Dance
    'Px: Kesagiri': [129],                          # Ittōryū: Kesagiri
    'Px: Tsubame Gaeshi': [130],                    # Ittōryū: Tsubame Gaeshi
    'Px: Kiri-otoshi': [131],                       # Ittōryū: Kiri-otoshi
    'Px: Blade': [190],                             # Slash (enemy)
    'Px: Shield Bash': [44],                        # Shield Bash
    'Px: Strike': [189],                            # Tackle
    'Px: Pound': [186],                             # Iron Fist
    'Px: Crash': [176, 214],                        # Body Slam, Horn Charge
}

# magic circle under the caster: circle -> {'a': long (ultimates), 'b': short}
CASTS = {
    '01': {'a': [34, 69, 71, 135, 72], 'b': [33, 68, 85]},                         # frost: Yuki, Diamond Dust
    '02': {'a': [26, 140, 64, 65, 92, 94], 'b': [25, 59, 138, 60, 139, 62, 63, 81, 82, 90, 169]},  # shadow, void
    '03': {'a': [122, 123, 95, 102], 'b': [17, 18, 83, 120, 121, 127]},            # healing, nature
    '04': {'a': [61, 163, 165, 166], 'b': [84, 158, 159, 160, 162]},              # fire, blood
    '05': {'a': [88, 19, 93], 'b': [86, 87, 91]},                                  # arcane, storm, water
    '06': {'a': [50, 108, 109, 110], 'b': [80, 89, 104, 106, 107, 125]},           # light, holy
}


# ---------------------------------------------------------------- building
def load_demo():
    demo = json.load(open(DLC + THAUM + 'Demo Project/data/Animations.json', encoding='utf8'))
    out = {}
    for a in demo:                                  # the demo's names are not reliable; the sheet name is
        if a and a['animation1Name'].startswith('30FPS_AC3T'):
            out[a['animation1Name'].split('_', 2)[2]] = a
    return out


def stretch_sounds(rtp, length, climax):
    """The RTP animation's sounds, spread so its last sound lands on the climax (or over the whole length)."""
    timings = [t for t in rtp['timings'] if t['se']]
    last = max([t['frame'] for t in timings] + [1])
    span = climax if climax else length - 1
    return [dict(copy.deepcopy(t), frame=min(length - 1, round(t['frame'] * span / last)), flashScope=0,
                 flashDuration=5, flashColor=[255, 255, 255, 255]) for t in timings]


def se(frame, name, pitch, volume=90):
    return {'flashColor': [255, 255, 255, 255], 'flashDuration': 5, 'flashScope': 0, 'frame': frame,
            'se': {'name': name, 'pan': 0, 'pitch': pitch, 'volume': volume}}


def thaum_anim(demo, short, anims):
    a = copy.deepcopy(demo[short])
    m =re.match(r'Cast(\d\d)([ab])', short)
    if m:
        name, pitch = CAST_SE[m.group(1)]
        a['timings'] = [se(0, name, pitch, 70)]
        for f in a['frames']:
            for c in f:
                c[1], c[2], c[3] = round(c[1] * CAST_SCALE / 100), round(c[2] * CAST_SCALE / 100), round(c[3] * CAST_SCALE / 100)
        return a, 'Thaum: Cast %s%s [30fps]' % m.groups()
    flashes = [t['frame'] for t in a['timings'] if t['flashScope']]
    a['timings'] = sorted(a['timings'] + stretch_sounds(anims[THAUM_SOUND_FROM[short]], len(a['frames']),
                                                        flashes[0] if flashes else None), key=lambda t: t['frame'])
    return a, 'Thaum: %s [30fps%s]' % (short, ' fit' if a['position'] == 3 else '')


def px_anim(recipe):
    sheets, frames = [], []
    for effect, start in recipe['layers']:
        sheet, first, last = PX_CELLS[effect]
        if sheet not in sheets: sheets.append(sheet)
        assert len(sheets) <= 2, 'at most two sheets per animation'
        base = 100 * sheets.index(sheet)
        cells = list(range(first, last + 1)) * recipe['loop']
        for i, cell in enumerate(cells):
            while len(frames) <= start + i: frames.append([])
            if len(frames[start + i]) < MAX_CELLS:
                frames[start + i].append([base + cell, 0, 0, recipe['scale'], 0, 0, 255, 0])
    return {'animation1Name': 'Px_' + sheets[0], 'animation1Hue': recipe['hue'],
            'animation2Name': 'Px_' + sheets[1] if len(sheets) > 1 else '', 'animation2Hue': recipe['hue2'],
            'position': recipe['pos'], 'frames': frames,
            'timings': [se(*t) for t in sorted(recipe['se'])]}


def base_name(name):
    return re.sub(r'\s*\[[^\]]*\]$', '', name)


def put(anims, name, a):
    aid = next((x['id'] for x in anims if x and base_name(x['name']) == base_name(name)), None)
    if aid is None:
        aid = len(anims)
        anims.append(None)
    a.update({'id': aid, 'name': name})
    anims[aid] = a
    return aid


def copy_sheets(names):
    for src, dst in names:
        if not os.path.isfile(ANIM_DIR + dst + '.png') or os.path.getsize(src) != os.path.getsize(ANIM_DIR + dst + '.png'):
            shutil.copyfile(src, ANIM_DIR + dst + '.png')


if __name__ == '__main__':
    apply = '--apply' in sys.argv
    assert DLC, 'RPG Maker MV dlc folder not found (set NOVA_DLC)'
    anims = json.load(open(L.DATA + 'Animations.json', encoding='utf8'))
    skills = json.load(open(L.DATA + 'Skills.json', encoding='utf8'))
    demo = load_demo()
    ids, sheets = {}, []

    for short in demo:
        a, name = thaum_anim(demo, short, anims)
        ids[base_name(name)] = put(anims, name, a)
        sheets.append((DLC + THAUM + '30FPS Animation Sheets/' + a['animation1Name'] + '.png', a['animation1Name']))
    for name, (short, hue, flash) in THAUM_VARIANTS.items():
        src = anims[ids['Thaum: ' + short]]
        a = copy.deepcopy(src)
        a['animation1Hue'] = hue
        if flash:
            climax = min([t['frame'] for t in a['timings'] if t['flashScope']] or [len(a['frames']) // 2])
            a['timings'] = sorted(a['timings'] + [{'flashColor': flash, 'flashDuration': 10, 'flashScope': 2,
                                                   'frame': max(0, climax - 6), 'se': None}], key=lambda t: t['frame'])
        tag = re.search(r'\[[^\]]*\]$', src['name']).group(0)
        ids['Thaum: ' + name] = put(anims, 'Thaum: %s %s' % (name, tag), a)
    for name, recipe in PX_ANIMS.items():
        a = px_anim(recipe)
        ids['Px: ' + name] = put(anims, 'Px: ' + name, a)
    for f in sorted(os.listdir(DLC + PIXEL)):
        sheets.append((DLC + PIXEL + f, 'Px_' + f[:-4]))

    by_id = {s['id']: s for s in skills if s}
    for name, users in SKILL_ANIMS.items():
        for sid in users: by_id[sid]['animationId'] = ids[name]
    cast_of = {}
    for circle, kinds in CASTS.items():
        for kind, users in kinds.items():
            for sid in users:
                assert sid not in cast_of, 'skill %d has two casts' % sid
                cast_of[sid] = ids['Thaum: Cast %s%s' % (circle, kind)]
    for s in skills:
        if not s: continue
        note = re.sub(r'\n?<cast (animation|wait):[^>]*>', '', s['note'])
        if s['id'] in cast_of: note = (note + '\n' if note else '') + '<cast animation: %d>' % cast_of[s['id']]
        s['note'] = note

    for name in list(SKILL_ANIMS) + ['Thaum: Cast %s%s' % (c, k) for c in sorted(CASTS) for k in 'ab']:
        aid = ids[name]
        users = [by_id[s]['name'] for s in SKILL_ANIMS.get(name, [])] or \
                [by_id[s]['name'] for s, c in cast_of.items() if c == aid]
        print('%3d %-34s -> %s' % (aid, anims[aid]['name'], ', '.join(users)))
    unused = [a['name'] for a in anims[1:] if a and (a['name'].startswith('Thaum:') or a['name'].startswith('Px:'))
              and not any(s and (s['animationId'] == a['id'] or '<cast animation: %d>' % a['id'] in s['note']) for s in skills)]
    print('not used by a skill yet:', ', '.join(unused) or '-')
    if apply:
        copy_sheets(sheets)
        dump = lambda xs: '[\n' + ',\n'.join(json.dumps(x, ensure_ascii=False, separators=(',', ':')) for x in xs) + '\n]'
        with open(L.DATA + 'Animations.json', 'w', encoding='utf8', newline='') as f: f.write(dump(anims))
        with open(L.DATA + 'Skills.json', 'w', encoding='utf8', newline='') as f: f.write(dump(skills))
    print('%d animations, %d skills with a cast circle (%s)' % (len(anims) - 1, len(cast_of),
                                                                'written' if apply else 'report only, --apply to write'))
