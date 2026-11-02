# The playable Prologue (Story/Prolog_Scenario.md): database entries, three new maps and the story events on
# existing maps.
#   python prologue.py preview_dir      -> preview images of the new maps
#   python prologue.py --save           -> write everything (RPG Maker MV must be closed)
#
# Story flags: variable 1 "Prologue" (stage), switch 11 "Mana Sight".
#   0 opening (Sealed Vault)        1 Briarwood: looking for Tobin  2 the rescue (slime + hornet)
#   3 the wolf                      4 wolf beaten: home to the gate 5 the Guild
#   6 night walk on Skyreach Hill   8 the Order at the crack        9 five months later (license)   10 prologue over
# Kael can't leave Briarwood before stage 5; from the wolf on, the story walks him to the Guild by itself.
# --save is safe to run again: it replaces its own records/events (matched by id/name) and leaves the rest alone.
import sys, os, json, math, copy
import nova_maplib as L
from nova_maplib import page, cmd, text, say, char, rt
import town_kit as T
import kingdom as K

V_STAGE, V_PESTS, S_MANA_SIGHT = 1, 2, 11       # V_PESTS: no longer used (the old Hollow Farm pest count)
V_CHAPTER1 = 3                             # chapter1.py's story variable: the prologue's last scene sets it to 1
VAULT, SKYREACH, BRIARWOOD = 27, 28, 29
FARM, GUILD = 24, K.TAVERN
KAEL, ISOLDE = ('Actor4', 0), ('family1', 5)
ISOLDE_SPRITE, ORDER_SPRITE, WOLF_SPRITE = ('family1', 5), ('People2', 2), ('Animals2', 1)
TOBIN_SPRITE = ('People1', 4)              # Tobin the carter, from the capital
ITEM_SHARD, STATE_VEIL, STATE_TUTORIAL, ENEMY_WOLF, CE_PESTS = 51, 36, 37, 38, 25
TROOP_SLIME, TROOP_HORNET, TROOP_WOLF = 41, 42, 43
WORLD_HILL = (58, 30)                      # Skyreach Hill on the World Map; you come back out one tile below
WORLD_WOOD = (54, 38)                      # Briarwood on the World Map: the forest corner by the road, south-west of
WORLD_WOOD_OUT = (55, 38)                  # the capital; you come back out next to it
ENTRANCE, ENTRANCE_START, ENTRANCE_TOP = 30, (16, 28), (17, 1)   # Briarwood - Entrance (map_briarwood_entrance.py):
                                                                # in from the World Map / back out of Briarwood


# ====================================================================== event-command helpers
def kael(*lines, i=0): return say('Kael', *lines, face=KAEL, indent=i)
def isolde(*lines, i=0): return say('Isolde', *lines, face=ISOLDE, indent=i)
def npc(name, *lines, i=0): return say(name, *lines, indent=i)
def tutorial(*lines, i=0): return text('\\C[3]Tutorial\\C[0]', *lines, indent=i)
def plain(*lines, i=0): return text(*lines, indent=i)
def var(v, value, op=0, i=0): return [cmd(122, [v, v, op, 0, value], i)]
def switch(s, on, i=0): return [cmd(121, [s, s, 0 if on else 1], i)]
def self_sw(ch='A', i=0): return [cmd(123, [ch, 0], i)]
def plugin(s, i=0): return [cmd(356, [s], i)]
def chapter_card(head, title, i=0):     # NovaChapterCard: animated title card in the middle of the screen, waits for it
    return plugin('ChapterCard %s | %s' % (head, title), i)
def wait(n, i=0): return [cmd(230, [n], i)]
def se(name, vol=80, pitch=100, i=0): return [cmd(250, [{'name': name, 'volume': vol, 'pitch': pitch, 'pan': 0}], i)]
def bgm(name, vol=80, i=0): return [cmd(241, [{'name': name, 'volume': vol, 'pitch': 100, 'pan': 0}], i)]
def fade_bgm(sec, i=0): return [cmd(242, [sec], i)]
def fadeout(i=0): return [cmd(221, [], i)]
def fadein(i=0): return [cmd(222, [], i)]
def tint(tone, frames=30, w=True, i=0): return [cmd(223, [tone, frames, w], i)]
def flash(color, frames=30, w=True, i=0): return [cmd(224, [color, frames, w], i)]
def shake(power=5, speed=5, frames=20, w=False, i=0): return [cmd(225, [power, speed, frames, w], i)]
def anim(who, anim_id, w=True, i=0): return [cmd(212, [who, anim_id, w], i)]
def balloon(who, bid, w=True, i=0): return [cmd(213, [who, bid, w], i)]
def transparent(on, i=0): return [cmd(211, [0 if on else 1], i)]
def goto(map_id, x, y, d=2, fade=2, i=0): return [cmd(201, [0, map_id, x, y, d, fade], i)]
def place(ev, x, y, d=0, i=0): return [cmd(203, [ev, 0, x, y, d], i)]
def erase(i=0): return [cmd(214, [], i)]
def scroll(*lines, i=0): return [cmd(105, [2, False], i)] + [cmd(405, [l], i) for l in lines]
def gold(n, i=0): return [cmd(125, [0, 0, n], i)]
def item(item_id, n=1, i=0): return [cmd(126, [item_id, 0, 0, n], i)]
def battle(troop, i=0): return [cmd(301, [0, troop, False, False], i)]
def common(ce, i=0): return [cmd(117, [ce], i)]
def heal(i=0):      # prologue battles are tutorials: back to full HP/MP after every win
    return [cmd(314, [0, 0], i)] + se('Recovery', 70, i=i) + plain('\\C[3]HP and MP fully restored.\\C[0]', i=i)


def move(who, *steps, w=True, skip=False, i=0):
    """steps: route codes or (code, *params). who: -1 player, 0 this event, n event id."""
    lst = [rt(*s) if isinstance(s, tuple) else rt(s) for s in steps] + [{'code': 0, 'parameters': []}]
    return [cmd(205, [who, {'list': lst, 'repeat': False, 'skippable': skip, 'wait': w}], i)]


UP, DOWN, LEFT, RIGHT = L.R_UP, L.R_DOWN, L.R_LEFT, L.R_RIGHT
T_UP, T_DOWN, T_LEFT, T_RIGHT = L.R_TURN_UP, L.R_TURN_DOWN, L.R_TURN_LEFT, L.R_TURN_RIGHT


def if_stage_at_least(value, body_fn, i=0):
    return [cmd(111, [1, V_STAGE, 0, value, 1], i)] + body_fn(i + 1) + [cmd(0, [], i + 1), cmd(412, [], i)]


def cond(stage=None, self_a=False, sw=None, var=V_STAGE):
    c = {}
    if stage is not None: c.update({'variableValid': True, 'variableId': var, 'variableValue': stage})
    if self_a: c.update({'selfSwitchValid': True, 'selfSwitchCh': 'A'})
    if sw: c.update({'switch1Valid': True, 'switch1Id': sw})
    return c


# "not here": no picture and Through, because MV won't let an event step onto a tile holding any other event that
# isn't Through, picture or not (Game_Event.isCollidedWithEvents) - a spent prologue hornet would block a later scene
BLANK = lambda **c: page(None, priority=0, through=True, cond=c or None)


def director(commands, stage, var=V_STAGE):
    """Autorun that plays once from the given stage on: [nothing, autorun (stage), done (self switch A)].
    It only plays when the story is exactly at its stage; one that was skipped (Scene Select, F9) just marks itself
    done, so a later stage never replays an old cutscene on the same map. var: the story variable (chapter)."""
    body = [cmd(111, [1, var, 0, stage, 0], 0)] + [dict(c, indent=c['indent'] + 1) for c in commands] \
        + [cmd(0, [], 1), cmd(412, [], 0)]
    return [BLANK(), page(None, trigger=3, priority=0, commands=body + self_sw(), cond=cond(stage, var=var)),
            page(None, priority=0, cond=cond(self_a=True))]


def staged(img, from_stage, until_stage, **kw):
    """A character that only stands there from one stage until another."""
    return [BLANK(), page(img, cond=cond(from_stage), **kw), BLANK(**cond(until_stage))]


# ====================================================================== database
def db_load(name): return json.load(open(L.DATA + name + '.json', encoding='utf8'))


def db_save(name, rows):
    with open(L.DATA + name + '.json', 'w', encoding='utf8', newline='') as f:
        f.write('[\n' + ',\n'.join(json.dumps(r, ensure_ascii=False, separators=(',', ':')) for r in rows) + '\n]')


def db_put(rows, rec):
    while len(rows) <= rec['id']: rows.append(None)
    rows[rec['id']] = rec


def troop_page(commands, turn0=False, enemy_hp=None):
    c = {'actorHp': 50, 'actorId': 1, 'actorValid': False, 'enemyHp': 50, 'enemyIndex': 0, 'enemyValid': False,
         'switchId': 1, 'switchValid': False, 'turnA': 0, 'turnB': 0, 'turnEnding': False, 'turnValid': False}
    if turn0: c['turnValid'] = True
    if enemy_hp is not None: c.update({'enemyValid': True, 'enemyHp': enemy_hp})
    return {'conditions': c, 'list': commands + [cmd(0, [])], 'span': 0}


def build_database():
    enemies, troops, states, items = db_load('Enemies'), db_load('Troops'), db_load('States'), db_load('Items')
    ces, system = db_load('CommonEvents'), db_load('System')
    eid = {e['name']: e['id'] for e in enemies if e}
    tid = {t['name']: t for t in troops if t}

    veil = copy.deepcopy(states[35])
    veil.update({'id': STATE_VEIL, 'name': 'Corrupted Veil', 'iconIndex': 161, 'restriction': 0, 'priority': 60,
                 'motion': 0, 'overlay': 0, 'autoRemovalTiming': 0, 'removeAtBattleEnd': True, 'removeByDamage': False,
                 'removeByRestriction': False, 'removeByWalking': False, 'message1': '', 'message2': '', 'message3': '',
                 'message4': '', 'traits': [{'code': 11, 'dataId': 2, 'value': 0.5}],
                 'note': '<veil weakness>\nCorruption swallows the weaknesses (NovaBreak). Fire 50%.'})
    db_put(states, veil)

    wolf = copy.deepcopy(enemies[eid['Werewolf']])
    wolf.update({'id': ENEMY_WOLF, 'name': 'Corrupted Wolf', 'battlerHue': 250, 'params': [560, 0, 26, 18, 20, 20, 24, 10],
                 'exp': 45, 'gold': 0, 'dropItems': [{'dataId': 1, 'denominator': 1, 'kind': 0}] * 3,
                 'actions': [{'conditionParam1': 0, 'conditionParam2': 0, 'conditionType': 0, 'rating': 5, 'skillId': 188},
                             {'conditionParam1': 0, 'conditionParam2': 0, 'conditionType': 0, 'rating': 4, 'skillId': 194}],
                 'note': '<guard: 2>\n<weak: Fire>\n<desc1:A grey wolf twisted by something in the mana.>\n'
                         '<desc2:Fire sinks into it... until the corruption cracks.>'})
    db_put(enemies, wolf)

    def troop(troop_id, name, like, enemy, pages):
        members = [dict(m, enemyId=enemy) for m in tid[like]['members']]
        db_put(troops, {'id': troop_id, 'members': members, 'name': name, 'pages': pages})

    # tutorial enemies hit softer: an icon-less state (NovaBreak only shows states with an icon), gone after the battle
    restraint = copy.deepcopy(veil)
    restraint.update({'id': STATE_TUTORIAL, 'name': 'Tutorial', 'iconIndex': 0, 'priority': 0,
                      'traits': [{'code': 21, 'dataId': 2, 'value': 0.75}], 'note': 'Prologue tutorial enemies: ATK 75%.'})
    db_put(states, restraint)
    soften = [cmd(333, [-1, 0, STATE_TUTORIAL])]

    # Briarwood: first the hornet (basics and weaknesses), then the slime (Guard and Break); both weak to Fire
    troop(TROOP_HORNET, 'Prologue: Field Hornet', 'Minotaur', eid['Field Hornet'], [troop_page(soften + plain(
        '\\C[3]Battle Tutorial\\C[0]', 'Time flows in battle. When Kael\'s gauge on the timeline',
        'fills, it is his turn: Attack, use a Skill or an Item.') + plain(
        '\\C[3]Weaknesses\\C[0]', 'Every enemy has weaknesses. The plate under the enemy',
        'shows them, as \\C[6]?\\C[0] until you have hit them once.') + plain(
        'Field Hornets are weak to \\C[2]Fire\\C[0]. Try \\C[6]Fire\\C[0] from Kael\'s Magic.',
        'Spells cost MP.') + plain(
        'A hit on a weakness is always a \\C[6]CRITICAL\\C[0] hit.', 'Find the weakness, and battles end fast.'), turn0=True)])
    troop(TROOP_SLIME, 'Prologue: Slime', 'Minotaur', eid['Slime'], [troop_page(soften + plain(
        'Slimes are weak to \\C[2]Fire\\C[0] too.') + plain(
        '\\C[3]Guard and Break\\C[0]', 'Every hit on a weakness also wears down the enemy\'s',
        '\\C[6]Guard\\C[0], shown on its plate.') + plain(
        'When the Guard runs out the enemy is \\C[2]Broken\\C[0]:', 'it loses its next turn and takes 50% more damage.')
        + plain('Battle too slow? Press \\C[6]Shift\\C[0] or click \\C[6]SPEED\\C[0] at the top right',
                'to switch between x1, x1.5 and x2. It stays as you leave it.'), turn0=True)])
    for t in range(TROOP_WOLF + 1, len(troops)):          # troops left over from an older version of this script
        if troops[t] and troops[t]['name'].startswith('Prologue:'): troops[t] = None
    while troops[-1] is None: troops.pop()
    troop(TROOP_WOLF, 'Prologue: Corrupted Wolf', 'Minotaur', ENEMY_WOLF, [
        troop_page([cmd(333, [0, 0, STATE_VEIL])] + plain('Black-violet veins pulse under the wolf\'s fur.',
                                                         'Its mana moves like water flowing uphill...')
                   + tutorial('A \\C[2]corrupted\\C[0] enemy hides its weaknesses: hitting one is',
                              'no critical and leaves its \\C[6]Guard\\C[0] alone. Wear it down,',
                              'and the corruption may crack.'), turn0=True),
        troop_page([cmd(333, [0, 1, STATE_VEIL]), cmd(337, [0, 101, False])] + se('Break', 90)
                   + plain('The corruption \\C[2]cracks\\C[0]!', 'Its weakness to \\C[2]Fire\\C[0] shows through.'), enemy_hp=50)])

    shard = copy.deepcopy(items[1])
    shard.update({'id': ITEM_SHARD, 'name': 'Tainted Shard', 'iconIndex': 161, 'itypeId': 2, 'consumable': False,
                  'occasion': 3, 'scope': 0, 'price': 0, 'effects': [], 'animationId': 0, 'speed': 0, 'successRate': 100,
                  'damage': {'critical': False, 'elementId': 0, 'formula': '0', 'type': 0, 'variance': 20},
                  'description': 'A cold black crystal. Its mana flows the wrong way,\nas if something is pulling it.',
                  'note': ''})
    db_put(items, shard)

    # the Hollow Farm pest counter is gone with the farm mission: clear its common event and variable name
    db_put(ces, {'id': CE_PESTS, 'name': '', 'switchId': 1, 'trigger': 0, 'list': [cmd(0, [])]})

    for i_, n in ((V_STAGE, 'Prologue'), (V_PESTS, '')): system['variables'][i_] = n
    system['switches'][S_MANA_SIGHT] = 'Mana Sight'
    system['partyMembers'] = [1]
    system.update({'startMapId': VAULT, 'startX': 8, 'startY': 11})

    db_save('Enemies', enemies); db_save('Troops', troops); db_save('States', states); db_save('Items', items)
    db_save('CommonEvents', ces)
    with open(L.DATA + 'System.json', 'w', encoding='utf8', newline='') as f:
        json.dump(system, f, ensure_ascii=False, separators=(',', ':'))


# ====================================================================== MAP027 - the Sealed Vault (opening)
D_TOP, D_FACE, D_FLOOR = ('A4', 16), ('A4', 24), ('A5', 32)


def build_vault():
    W, H = 17, 13
    m = L.MapBuilder(W, H, 4, 'Prologue - Sealed Vault', '')
    m.note = '<ambient: #3a3048>\n<minimap: off>'
    for y in range(H):
        for x in range(W):
            edge = x in (0, W - 1) or y in (0, H - 1)
            m.cell(x, y, D_TOP if edge else D_FACE if y in (1, 2) else D_FLOOR)
    seal = m.add_event('The Seal', 8, 5, [page(char('!Other1', 3), step_anim=True, walk_anim=False)])['id']
    for x in (5, 11):
        m.add_event('Torch', x, 2, [page(char('!Flame', 0), step_anim=True, walk_anim=False)], note='<light: 4, #a070ff>')
    for x in (6, 10):
        m.add_event('Wisp', x, 6, [page(char('!Flame', 5), step_anim=True, walk_anim=False, priority=2)])
    m.add_event('???', 8, 8, [page(char(*ORDER_SPRITE, direction=8), walk_anim=False)])['id']
    m.add_event('Opening', 1, 11, director([
        *transparent(True), *plugin('Clock hud hide'), *plugin('Minimap hide'), *plugin('Clock stop'),
        *fadeout(), *bgm('Theme2', 70),
        *scroll('Long ago, when the world was young and wild,', 'seven heroes rose against an evil force',
                'that threatened the planet.', '',
                'They were called the Elemental Champions.', '',
                'Together they sealed the evil away,', 'and the world forgot it had ever been afraid.', '',
                'But seals, like heroes, do not last forever.'),
        *fade_bgm(3), *tint([-68, -85, -17, 85], 0), *wait(60), *bgm('Dungeon3', 60), *fadein(), *wait(40),
        *se('Darkness1', 70), *anim(seal, 101), *wait(20),
        *npc('???', 'Can you hear it? The seal is breathing.'),
        *npc('???', 'The Age of Heroes ended in silence.', 'The kings forgot. The people forgot.'),
        *npc('???', 'I have not.'),
        *se('Earth3', 80), *shake(6, 6, 40), *flash([170, 120, 255, 170], 30), *anim(seal, 105),
        *npc('???', 'I will bring it back.'),
        *wait(30), *npc('???', 'The Champion of Light will rise again.'),
        *fade_bgm(2), *fadeout(), *wait(60), *tint([0, 0, 0, 0], 0, False),
        *var(V_STAGE, 1), *plugin('Clock set 10:00'), *plugin('Clock start'), *plugin('Clock hud show'),
        *plugin('Minimap show'), *transparent(False),
        *goto(BRIARWOOD, WOOD_START[0], WOOD_START[1], 8)], 0))
    return m


# ====================================================================== MAP028 - Skyreach Hill
SKY_W, SKY_H = 34, 44
MEADOW = ('A4', 32)
PATH = [(16.5, 44), (15.5, 38), (18, 32), (17, 26), (15.5, 20), (17, 13)]
LOOKOUT = (17, 12)
CRACK = (22, 11)
FLOW = [(17, 11), (18, 11), (19, 12), (20, 12), (21, 12), (21, 11)]


def sky_top(x): return 8 + ((x - 17) / 4.6) ** 2


def seg_dist(p, a, b):
    (px, py), (ax, ay), (bx, by) = p, a, b
    dx, dy = bx - ax, by - ay
    t = max(0, min(1, ((px - ax) * dx + (py - ay) * dy) / float(dx * dx + dy * dy)))
    return math.hypot(px - ax - t * dx, py - ay - t * dy)


def on_path(x, y): return min(seg_dist((x, y), PATH[i], PATH[i + 1]) for i in range(len(PATH) - 1)) < 1.15


def build_skyreach():
    W, H = SKY_W, SKY_H
    m = L.MapBuilder(W, H, T.OUTSIDE, 'Skyreach Hill', 'Skyreach Hill')
    m.note = '<outdoor>\n<night ambient: #7078b0>\n<player light: 110,#8c8070>'   # moonlit: only a faint lantern
    m.bgm = {'name': 'Field2', 'pan': 0, 'pitch': 100, 'volume': 70}
    m.parallax = 'BlueSky'
    land = lambda x, y: 0 <= x < W and 0 <= y < H and y >= sky_top(x)
    clearing = lambda x, y: math.hypot(x - LOOKOUT[0], (y - LOOKOUT[1]) * 1.3) < 6.5
    for y in range(H):
        for x in range(W):
            if land(x, y): m.cell(x, y, MEADOW)
    path = set((x, y) for y in range(H) for x in range(W) if land(x, y) and on_path(x, y))
    for x, y in path: m.cell(x, y, T.DIRT, layer=1)

    # forest walls down both sides and along the bottom: pines packed one per tile, each crown over the tile above
    def wood(x, y):
        if not land(x, y) or (x, y) in path or y < 19: return False
        left = 3 + 2.5 * math.sin(y * 0.45) + max(0, y - 30) * 0.25
        right = W - 4 - 2.5 * math.sin(y * 0.38 + 1.5) - max(0, y - 30) * 0.25
        return x < left or x > right or y >= H - 3
    canopy = set((x, y) for y in range(H) for x in range(W) if wood(x, y))
    for x, y in canopy:
        m.put(x, y, T.TREE_S3)
        if land(x, y - 1): m.put(x, y - 1, T.TREE_S1, 3)

    # single pines, a fallen log and some flowers
    taken = set(path) | set(canopy) | {(x, y - 1) for x, y in canopy}
    pines = [(9, 16), (11, 19), (8, 21), (12, 24), (10, 28), (13, 31), (9, 34), (12, 37), (24, 15), (26, 18),
             (22, 21), (25, 24), (21, 27), (24, 30), (20, 35), (23, 38), (13, 15), (27, 22), (7, 25), (11, 40),
             (20, 40), (14, 27), (19, 30)]
    for x, y in pines:
        near = any((x + dx, y + dy) in path for dx in (-1, 0, 1) for dy in (-1, 0, 1))
        if not land(x, y - 1) or near or clearing(x, y) or (x, y) in taken or (x, y - 1) in taken: continue
        m.put(x, y - 1, T.TREE_S1, 3); m.put(x, y, T.TREE_S3); taken |= {(x, y), (x, y - 1)}
    m.put(14, 11, T.LOG); m.put(12, 13, T.BOULDER); m.put(20, 14, T.STUMP)
    for i, (x, y) in enumerate([(15, 9), (19, 10), (13, 12), (21, 13), (16, 14), (11, 14), (23, 13)]):
        m.put(x, y, T.FLOWERS[i % 4] if i % 2 else T.GRASS_TUFTS[i % 4])

    # parallax by the clock: stars at night, sunset in the evening, blue sky by day
    m.add_event('Sky', 0, H - 1, [page(None, trigger=4, priority=0, commands=[
        cmd(355, ["var h = window.NovaDayNight ? NovaDayNight.hour() : 12;"]),
        cmd(655, ["$gameMap.changeParallax(h >= 19 || h < 5 ? 'StarlitSky' : h >= 16 ? 'Sunset' : 'BlueSky', true, false, 1, 0);"]),
        *erase()])])
    for i, x in enumerate(sorted(x for x, y in path if y == H - 1)):
        out = L.exit_page(K.WORLD, WORLD_HILL[0], WORLD_HILL[1] + 1, 2)
        stay = page(None, trigger=1, priority=0, cond=cond(6), commands=kael("The Professor's waiting up top.") + move(-1, UP))
        m.add_event('To World Map %d' % (i + 1), x, H - 1, [out, stay, dict(copy.deepcopy(out), conditions=page(None, cond=cond(9))['conditions'])])

    # ---- the prologue night: walk up, the shard, Mana Sight, the crack, the Order
    isolde_ev = m.add_event('Isolde', 17, 41, staged(char(*ISOLDE_SPRITE, direction=8), 6, 8))['id']
    for x, y in FLOW:
        m.add_event('Mana Flow', x, y, [BLANK(), page(char('!Flame', 7), priority=0, through=True, step_anim=True,
                                                      walk_anim=False, cond=cond(sw=S_MANA_SIGHT)), BLANK(**cond(9))],
                    note='<minimap: hide>')
    order = [m.add_event('Robed Figure', x, 16, staged(char(*ORDER_SPRITE, direction=8), 8, 9), note='<minimap: hide>')['id']
             for x in (21, 23)]

    burden = [
        *fadeout(), *goto(SKYREACH, CRACK[0], CRACK[1] + 1, 8), *place(isolde_ev, CRACK[0] + 1, CRACK[1] + 1, 4), *fadein(),
        *kael("It's... draining. The flow goes in,", 'and something else comes *out*.'),
        *isolde('Yes.'),
        *kael("That's not natural. Leylines don't just *leak*."),
        *isolde("No. They don't."),
        *fade_bgm(3), *wait(40),
        *isolde('Two years ago, I felt the first one. Far to the north.', 'I thought I was imagining it.'),
        *isolde('Then another. And another.', 'Each a little closer. Each a little larger.'),
        *kael("That's why you retired."),
        *isolde('The Academy teaches what is known, Kaelen.', 'This is not known. So I left to learn it.'),
        *kael('Did you tell the Council? The Royal Mages could—'),
        *wait(30), *isolde('The Council is... aware that mages talk', 'about strange things.'),
        *kael("That's not a no."),
        *isolde("It isn't a yes, either."),
        *move(isolde_ev, T_LEFT), *se('Magic3', 70), *anim(-1, 96),
        *plain('Isolde touches the crack with the tip of her staff.', 'It shrinks... but does not close.'),
        *isolde('Magic flow is the blood of this world.', 'Something is poisoning it. Through cracks like this one.'),
        *kael('Something? Or some*one*?'),
        *wait(40), *isolde("...I'm beginning to believe there are people who would", 'welcome this. Who might even be helping it along.'),
        *kael("Then let's find them. Tomorrow.", "I'll drop the Guild, I'll—"),
        *isolde('And your exam?'),
        *kael('...My exam.'),
        *isolde('You set yourself one year. You are seven months in.', 'Finish it.'),
        *kael('But this is more important than a license!'),
        *isolde('The world will still be broken in five months, Kaelen.', 'I promise you that much.'),
        *isolde('Become stronger first. Then...'),
        *move(isolde_ev, T_UP), *wait(30), *bgm('Theme2', 60),
        *isolde('\\C[6]Go. See the world.\\C[0]', "\\C[6]You'll find that we are small.\\C[0]"),
        *kael('...Small?'),
        *move(isolde_ev, T_LEFT),
        *isolde('You want to be the number one mage. I know.', 'You told the entire Academy. Twice. At graduation.'),
        *kael('It was *one* time. It just echoed.'),
        *isolde('Number one of *what*, Kaelen? Of Nova?', 'The world is far larger than this kingdom,', 'and far larger than any of us.'),
        *isolde('Go and see how large.', "Then decide what 'number one' means."),
        *wait(30), *kael("...I'll finish the exam. And then I'll go."),
        *isolde("Good. Keep the shard. Don't show it to anyone", "you can't trust."),
        *kael('Do *you* count?'),
        *isolde('Never trust a teacher who answers that question.'),
        *fade_bgm(3), *fadeout(), *switch(S_MANA_SIGHT, False), *tint([0, 0, 0, 0], 0, False), *wait(60),
        # ---- later that night: the Order of Caelum
        *var(V_STAGE, 8), *transparent(True), *plugin('Clock set 23:40'), *wait(30), *bgm('Dungeon3', 55), *fadein(),
        # through + skippable: a cutscene walk must never hang on something in the way
        *move(order[0], 37, UP, UP, UP, 38, T_UP, w=False, skip=True), *move(order[1], 37, UP, UP, UP, 38, T_UP, skip=True), *wait(20),
        *npc('Robed Figure', 'Someone was here. Recently.', "The crack's been... *soothed*."),
        *npc('Robed Figure', 'A mage of the capital, then. It does not matter.'),
        *anim(order[1], 58), *se('Absorb1', 70),
        *plain('The second figure draws the violet smoke into a glass vial.'),
        *npc('Robed Figure', 'Every crack brings us closer.', 'The Age of Heroes will return,', 'and this time, it will be *ours*.'),
        *npc('Robed Figure', 'For Caelum.'), *npc('Robed Figure', 'For Caelum.'),
        *se('Saint3', 60), *flash([255, 255, 220, 200], 40), *fade_bgm(3), *fadeout(), *wait(90),
        # ---- five months later
        *var(V_STAGE, 9), *transparent(False),
        *scroll('', '', 'Five months later.'),
        *plugin('Clock set 09:00'), *goto(GUILD, 26, 7, 8)]
    crack = m.add_event('The Crack', CRACK[0], CRACK[1], [
        BLANK(), page(char('!Other2', 5), commands=burden, step_anim=True, walk_anim=False, cond=cond(sw=S_MANA_SIGHT)),
        BLANK(**cond(9))], note='<minimap: hide>')

    walk = [
        *fadein(), *move(isolde_ev, UP, UP, UP, w=False), *move(-1, UP, UP, UP),
        *kael('Everyone thinks you vanished, you know.', 'Rumor says you live in a tower and talk to owls.'),
        *isolde('Only one owl. And he rarely answers.'),
        *kael('Why did you retire, Professor? You were the best', 'teacher at the Academy. Everyone says so.'),
        *isolde('Everyone says a great many things.'), *wait(30),
        *isolde("I needed to listen to something", "the Academy couldn't hear."),
        *kael("...That's a very teacher way of not answering."),
        *isolde('Thank you. I practiced it for years.'),
        *fadeout(), *goto(SKYREACH, LOOKOUT[0] - 1, LOOKOUT[1], 8), *place(isolde_ev, LOOKOUT[0], LOOKOUT[1] - 2, 8), *fadein(),
        *wait(60), *kael('Whoa...'),
        *isolde('Skyreach Hill. On a clear night you can see', 'halfway to the sea.'),
        *kael('Actually... I found something today. On my mission.'),
        *move(isolde_ev, T_DOWN), *se('Item1'),
        *plain('Kael holds out the \\C[6]Tainted Shard\\C[0].'),
        *balloon(isolde_ev, 1), *isolde('Where?'),
        *kael('In Briarwood, on the old cart road.', 'A wolf whose mana flowed backwards.', 'Fire sank into it like water.'),
        *kael('When it died, it melted, and left *this*.'),
        *isolde('...Already so close to the capital.'),
        *kael('Professor?'),
        *isolde('Tell me, Kaelen. Can you read the flow?'),
        *kael("Mana flow? That's third-year theory. Of course I can."),
        *isolde('Theory, yes. Show me.'),
        *se('Magic1', 80), *anim(-1, 119), *tint([-51, -17, 68, 34], 45), *switch(S_MANA_SIGHT, True),
        *tutorial('\\C[6]Mana Sight\\C[0]: threads of mana glimmer in the dark,', 'all flowing the same way.',
                  'Follow them, and examine the place where they go wrong.')]
    m.add_event('Prologue: Night Walk', 0, H - 2, director(walk, 6))
    return m


# ====================================================================== MAP029 - Briarwood (the rescue)
WOOD_W, WOOD_H = 30, 36
WOOD_PATH = [(15.5, 36), (13.5, 30), (16, 24), (15, 19), (15.5, 13)]
WOOD_CLEARING, WOOD_RX, WOOD_RY = (15.5, 9.5), 7, 5
WOOD_START = (15, WOOD_H - 2)              # where the opening drops Kael, and where the World Map lets you in
STRIP_Y = 17                               # stepping on this row (stage 1) starts the rescue
TOBIN, KAEL_STOP = (15, 7), (15, 8)        # Kael ends up right in front of Tobin, between him and the monsters
HORNET = (16, 11)
# the slime and the wolf wait inside the tree line, hidden under the crowns, and come out when it is their turn
SLIME_FROM, WOLF_FROM = (23, 9), (8, 10)


def build_briarwood():
    W, H = WOOD_W, WOOD_H
    m = L.MapBuilder(W, H, T.OUTSIDE, 'Briarwood', 'Briarwood')
    m.note = '<outdoor>'
    m.bgm = {'name': 'Field2', 'pan': 0, 'pitch': 100, 'volume': 70}
    road = lambda x, y: min(seg_dist((x, y), WOOD_PATH[i], WOOD_PATH[i + 1]) for i in range(len(WOOD_PATH) - 1))
    path = lambda x, y: road(x, y) < 1.15
    clearing = lambda x, y: ((x - WOOD_CLEARING[0]) / WOOD_RX) ** 2 + ((y - WOOD_CLEARING[1]) / WOOD_RY) ** 2 < 1
    verge = lambda x, y: road(x, y) < 2.3 + 0.9 * math.sin(y * 0.8 + x * 0.5)     # a ragged grass edge along the road
    wood = lambda x, y: not clearing(x, y) and not verge(x, y)
    for y in range(H):
        for x in range(W):
            m.cell(x, y, T.DIRT if path(x, y) and not clearing(x, y) else T.GRASS)
    # pines packed one per tile, each crown over the tile above: the forest is a wall around the road and the clearing
    for y in range(H):
        for x in range(W):
            if wood(x, y):
                m.put(x, y, T.TREE_S3)
                if y > 0: m.put(x, y - 1, T.TREE_S1, 3)
    # undergrowth on the verge, kept off the road itself and off the row that starts the rescue
    rnd = __import__('random').Random(29)
    for y in range(STRIP_Y + 1, H - 1):
        for x in range(W):
            if not wood(x, y) and not path(x, y) and rnd.random() < 0.45:
                m.put(x, y, rnd.choice([T.FERN, T.BUSH_S, T.STUMP, *T.GRASS_TUFTS, *T.GRASS_TUFTS, *T.FLOWERS]))
    # Tobin's wrecked cart: spilled crates, a barrel and firewood; ferns where he hides, rocks and a log
    for (x, y), tile in (((19, 6), T.CRATE), ((20, 6), T.BARREL), ((20, 8), T.CRATE_APPLE), ((21, 7), T.FIREWOOD),
                         ((12, 7), T.BOULDER), ((19, 12), T.STUMP), ((11, 12), T.LOG), ((14, 6), T.FERN), ((16, 6), T.FERN),
                         ((22, 10), T.ROCKS)):
        m.put(x, y, tile)
    for i, (x, y) in enumerate([(13, 13), (18, 13), (11, 9), (20, 11), (17, 6), (13, 5), (21, 9)]):
        m.put(x, y, T.FLOWERS[i % 4] if i % 2 else T.GRASS_TUFTS[i % 4])

    # out to the forest edge (Briarwood - Entrance, then the World Map): not before Tobin is found
    for x in (x for x in range(W) if not wood(x, H - 1)):
        out = L.exit_page(ENTRANCE, ENTRANCE_TOP[0], ENTRANCE_TOP[1], 2)
        stay = page(None, trigger=1, priority=0, cond=cond(1), commands=kael("Not yet. I came here to find Tobin.") + move(-1, UP))
        m.add_event('To World Map %d' % x, x, H - 1, [out, stay, dict(copy.deepcopy(out), conditions=page(None, cond=cond(5))['conditions'])])

    tobin = m.add_event('Tobin', TOBIN[0], TOBIN[1], staged(char(*TOBIN_SPRITE, direction=2), 1, 4))['id']
    slime = m.add_event('Slime', SLIME_FROM[0], SLIME_FROM[1], staged(char('Monster', 1, direction=4), 1, 3, step_anim=True),
                        note='<minimap: hide>')['id']
    hornet = m.add_event('Field Hornet', HORNET[0], HORNET[1], staged(char('$Pet_Hornet', 0, direction=8), 1, 3, step_anim=True),
                         note='<minimap: hide>')['id']
    wolf = m.add_event('Grey Wolf', WOLF_FROM[0], WOLF_FROM[1], staged(char(*WOLF_SPRITE, direction=6), 3, 4, step_anim=True),
                       note='<minimap: hide>')['id']
    for x in (x for x in range(W) if not wood(x, STRIP_Y)):
        m.add_event('Prologue: Clearing %d' % x, x, STRIP_Y,
                    [BLANK(), page(None, trigger=1, priority=0, cond=cond(1), commands=var(V_STAGE, 2)), BLANK(**cond(2))])

    m.add_event('Prologue: Briarwood', 0, H - 1, director([
        *fadein(),
        *kael("Tobin's cart never made it home last night,", 'and the Guild says he took the Briarwood road.'),
        *kael('The clerk even made me take supplies.', "Hang on, Tobin. I'm coming."),
        *se('Item1'), *item(1, 3), *plain('Kael has 3 \\C[6]Potions\\C[0].'),
        *tutorial('Move with the arrow keys or a click. Hold \\C[6]Shift\\C[0] to dash.',
                  'Talk and examine with \\C[6]Enter\\C[0] / \\C[6]Z\\C[0].')], 1))

    gone = lambda ev, w=True: move(ev, 39, 37, w=w)          # transparent + through: off the stage
    rescue = [
        *goto(BRIARWOOD, KAEL_STOP[0], STRIP_Y, 8, fade=2),     # same spot whichever tile of the row was stepped on
        *npc('Tobin', 'S-stay back! Shoo! Go bother a squirrel!'), *balloon(tobin, 6),
        *move(hornet, UP), *wait(20),
        *npc('Tobin', 'Somebody... help!'),
        *move(hornet, UP, w=False),
        # through + skippable: a cutscene walk must never hang on something in the way
        *move(-1, 37, (29, 5), *[UP] * (STRIP_Y - KAEL_STOP[1]), (29, 4), 38, T_DOWN, skip=True),
        *kael('Hold it right there!'),
        *balloon(tobin, 1), *npc('Tobin', 'Kael!'),
        *move(-1, T_UP),
        *kael("Are you alright? I took the Guild's mission to find you.", "Nobody's heard from you since last night."),
        *npc('Tobin', 'Right... my cart was attacked by monsters,', 'and I twisted my ankle.'),
        *move(-1, T_DOWN),
        *kael('Alright. Leave this to me.'),
        *battle(TROOP_HORNET), *gone(hornet), *heal(),
        *move(-1, T_UP),
        *kael('Phew. Are you hurt anywhere else?'),
        *npc('Tobin', 'Just my ankle, and my pride—'),
        *balloon(tobin, 1), *npc('Tobin', "Kael, look out! There's another one!"),
        *move(slime, 37, *[LEFT] * (SLIME_FROM[0] - 17), 38, skip=True), *move(-1, T_RIGHT),
        *kael('A slime too? Fine. One more!'),
        *battle(TROOP_SLIME), *gone(slime), *heal(),
        *move(-1, T_UP),
        *kael("That's the last of them. Can you stand?"),
        *npc('Tobin', 'With a hand, maybe. Gods, lad,', 'you came all this way for me?'),
        *kael('Your wife marched into the Guild at dawn.', 'Half the request board was in her handwriting.'),
        *npc('Tobin', '...That sounds like her.'),
        *kael("Come on. Let's get you home before—"),
        *se('Wolf', 90), *shake(3, 6, 20), *balloon(-1, 1, w=False), *balloon(tobin, 1),
        *npc('Tobin', 'W-what was that?!'),
        *var(V_STAGE, 3), *move(-1, T_LEFT, w=False), *move(wolf, 37, RIGHT, RIGHT, RIGHT, RIGHT, 38, skip=True),
        *kael('A grey wolf? No... its mana is all *wrong*.', "It's like looking at a river flowing uphill."),
        *se('Growl', 90), *flash([120, 60, 200, 160], 30), *anim(wolf, 103),
        *kael("It's... changing!"),
        *npc('Tobin', 'Kael...!'),
        *kael('Stay behind me, Tobin!'),
        *battle(TROOP_WOLF), *heal(),
        *anim(wolf, 104), *se('Darkness3', 80), *gone(wolf),
        *plain('The wolf dissolves into violet smoke.', 'Only a small black crystal is left in the grass.'),
        *kael('It just... dissolved? Wolves don\'t do that.'),
        *se('Item3'), *item(ITEM_SHARD),
        *plain('Got the \\C[6]Tainted Shard\\C[0]!'),
        *kael('Cold. And the mana inside is moving the wrong way.', "Like it's being *pulled* somewhere."),
        *flash([255, 240, 170, 120], 20), *se('Saint1', 50),
        *kael("...Must've been my fire reflecting. Right."),
        *move(-1, T_UP),
        *npc('Tobin', "Kael... what in the gods' name was that thing?"),
        *kael("I don't know. I've never seen anything like it.", 'Not in the Academy books, not anywhere.'),
        *npc('Tobin', "Twenty years I've driven this road.", 'Slimes, hornets, the odd boar... never *that*.'),
        *kael('Is that what wrecked your cart?'),
        *npc('Tobin', "I didn't get a good look. Something big,", 'out of the dark. Then I ran.'),
        *kael("...Let's get you home. The Guild needs to hear about this."),
        *tutorial('Open the \\C[6]Menu\\C[0] with \\C[6]Esc\\C[0] / \\C[6]X\\C[0] or a right click:',
                  'Items (the shard is under Key Items), Skills, Equip and Status.',
                  'Press \\C[6]M\\C[0] to show or hide the minimap.'),
        *tutorial('\\C[6]Quests\\C[0], at the top of the Menu, keep track of your',
                  'current objective and the story so far.'),
        *fade_bgm(2), *fadeout(), *var(V_STAGE, 4), *plugin('Clock set 17:00'),
        *goto(K.CITY_GATE, GATE_ROAD[0], GATE_ROAD[1], 8)]
    m.add_event('Prologue: The Rescue', 1, H - 1, director(rescue, 2))
    return m


# ====================================================================== existing maps
def patch_events(map_id, build, tag='<prologue>'):
    """Drop this script's events (note tag, '<prologue>') from the map, then add new ones; build(add) returns nothing."""
    mp = json.load(open(L.DATA + 'Map%03d.json' % map_id, encoding='utf8'))
    mp['events'] = [None if e and tag in e.get('note', '') else e for e in mp['events']]
    while len(mp['events']) > 1 and mp['events'][-1] is None: mp['events'].pop()

    def add(name, x, y, pages, note=''):
        slot = next((k for k in range(1, len(mp['events'])) if mp['events'][k] is None), len(mp['events']))
        ev = {'id': slot, 'name': name, 'note': (note + '\n' + tag).strip(), 'pages': pages, 'x': x, 'y': y}
        if slot == len(mp['events']): mp['events'].append(ev)
        else: mp['events'][slot] = ev
        return slot
    build(add, mp)
    return mp


def restore_pages(mp, prefix):
    """Existing events named prefix* back to their own first page (an older version of this script staged them)."""
    for e in mp['events']:
        if e and e['name'].startswith(prefix): e['pages'] = e['pages'][:1]


def farm_events(add, mp):
    """The prologue no longer happens on Hollow Farm: its old events go (patch_events) and the exits are plain again."""
    restore_pages(mp, 'To Main Gate')


GUILD_DOOR = (10, 13)                      # where the Tavern Door in Baker's Lane lets you in
GUILD_SILL = (10, 14)                      # the doorway itself: in the prologue Kael walks in from here
GATE_ROAD = (20, 32)                       # Main Gate: bottom of the road, where Kael comes home with Tobin
# Isolde sits on the stool right of the west table (3,10); the crowd stands around her (name, sheet, index, x, y, facing)
ISOLDE_SEAT = (4, 10)
CROWD = [('Young Mage', 'People4', 3, 3, 9, 2), ('Scholar', 'People2', 1, 4, 9, 2), ('Mage', 'People2', 6, 2, 9, 2),
         ('Mercenary', 'People3', 4, 5, 9, 4), ('Sellsword', 'People3', 0, 5, 10, 4), ('Battle Mage', 'People4', 5, 5, 11, 4),
         ('Apprentice', 'People1', 3, 4, 11, 8)]


def gate_events(add, mp):
    """Main Gate at dusk: Kael walks Tobin home from Briarwood, the gate guard takes over, then on to the Guild."""
    guard = next(e['id'] for e in mp['events'] if e and e['name'] == 'Gate Guard' and e['x'] > 20)
    tobin = add('Tobin', GATE_ROAD[0] - 1, GATE_ROAD[1], staged(char(*TOBIN_SPRITE, direction=8), 4, 5))
    steps = GATE_ROAD[1] - 18                  # up the road to just below the gate guards (y15)
    add('Prologue: Home Again', 0, 0, director([
        *fadein(),       # the Briarwood scene ended on a Fadeout, and a transfer does not undo that
        *move(tobin, 37, *[UP] * steps, 38, w=False, skip=True), *move(-1, 37, *[UP] * steps, 38, skip=True),
        *move(guard, 37, LEFT, LEFT, DOWN, DOWN, DOWN, 38, T_LEFT, skip=True), *move(-1, T_RIGHT),
        *npc('Gate Guard', 'Ashveil! You found him!'),
        *npc('Gate Guard', 'We were about to send a patrol into Briarwood.', "His wife's been at this gate since dawn."),
        *npc('Tobin', 'Found me? The lad saved my hide.', 'Slimes, hornets, and a wolf that... *melted*.'),
        *npc('Gate Guard', 'A wolf that what?'),
        *kael("It's a long story. I'll put it in my report."),
        *npc('Gate Guard', "Then go and report. I'll walk Tobin to the healer.", 'Good work, Kael.'),
        *move(-1, T_LEFT, w=False), *move(tobin, T_RIGHT),
        *npc('Tobin', 'Thank you, Kael. The next round at', "the Lion's Rest is on me."),
        *kael("I'll hold you to that."),
        *fadeout(), *var(V_STAGE, 5), *plugin('Clock set 17:30'),
        *goto(GUILD, GUILD_SILL[0], GUILD_SILL[1], 8)], 4))


def guild_events(add, mp):
    crowd = {}
    for name, sheet, idx, x, y, d in CROWD:
        crowd[name] = add(name, x, y, staged(char(sheet, idx, direction=d), 5, 6))
    isolde_ev = add('Isolde', ISOLDE_SEAT[0], ISOLDE_SEAT[1], staged(char(*ISOLDE_SPRITE, direction=4), 5, 6))
    clerk = next(e['id'] for e in mp['events'] if e and e['name'] == 'Guild Clerk')
    # Kael walks in from the doorway (10,14) to (10,12), squeezes through the crowd and ends up at Isolde's table, on (5,10)
    add('Prologue: The Crowd', 0, 0, director([
        *fadein(), *move(-1, UP, UP), *wait(30),
        *npc('Young Mage', 'Is it really her? I thought she retired!'),
        *npc('Mercenary', 'Hah, every mage in the capital is here.', "Look at 'em. Like moths to a lamp."),
        *balloon(-1, 1), *kael("Whoa. What's everyone crowding around?"),
        # through: the Barmaid wanders around here and must never hold the scene up
        *move(-1, 37, LEFT, LEFT, LEFT, LEFT, 38, skip=True),
        *kael('Excuse me... pardon me...'),
        *move(crowd['Sellsword'], 37, RIGHT, UP, T_LEFT, 38, skip=True),
        *move(-1, 37, UP, UP, LEFT, 38, skip=True),
        *balloon(-1, 1), *kael('White hair... no way.'),
        *shake(4, 8, 15), *kael('\\{PROFESSOR WYNDMERE!\\}'),
        *[c for k in crowd.values() for c in balloon(k, 1, w=False)], *wait(40),
        *move(isolde_ev, T_RIGHT),
        *isolde('Still the loudest student I ever had, Kaelen.'),
        *npc('Apprentice', '(He *knows* her?!)'),
        *isolde('Forgive me, everyone. I have an old student to scold.'),
        *isolde('Seven months as a licensed mage.', 'Your letters stopped after the second month.'),
        *kael("I've been busy! I'm taking the Class 3 exam", 'within the year.'),
        *isolde('Within the year.'), *wait(20), *isolde('Of course you are.'),
        *isolde('Walk with me tonight, Kaelen. Outside the walls.', "There is something I'd like you to see."),
        *kael("Now? It's getting dark."),
        *isolde("That's rather the point."),
        *fade_bgm(2), *fadeout(), *var(V_STAGE, 6), *plugin('Clock set 21:00'),
        *goto(SKYREACH, 16, 41, 8)], 5))
    add('Prologue: Five Months Later', 0, 1, director([
        *fadein(), *move(clerk, T_DOWN),
        *npc('Guild Clerk', 'Well, well. Kaelen Ashveil.', 'The Examination Board sent this over this morning.'),
        *se('Item3'), *plain('Kael receives his new license: \\C[6]Mage Class 3\\C[0].'),
        *npc('Guild Clerk', 'One year, on the dot. Show-off.'),
        *kael('One year. Exactly as promised.'), *wait(30),
        *kael('...Both promises.'),
        *npc('Guild Clerk', 'So? The board has three new requests for a Class 3.'),
        *kael("Not this time. I'm stepping away from missions", "for a while. I'm going to see the world."),
        *npc('Guild Clerk', "Oh? Whatever it is, good luck."),
        # the title cards (NovaChapterCard) draw their own black backdrop over the faded-out map
        cmd(243, []), *fade_bgm(3), *fadeout(), *var(V_STAGE, 10), *wait(30),
        *se('Saint1', 60), *chapter_card('', 'Prologue Ends'), *wait(40),
        *se('Saint3', 70), *chapter_card('Chapter 1', 'The Adventure Begins'),
        *var(V_CHAPTER1, 1), cmd(244, []), *fadein(),
        *kael('Time to get going.')], 9))


def world_entry(mp):
    """Skyreach Hill on the World Map (a wooded knoll north-west of the capital) and the way into Briarwood."""
    W, H = mp['width'], mp['height']
    hx, hy = WORLD_HILL
    knoll = {(hx + dx, hy + dy) for dx in (-1, 0, 1) for dy in (-1, 0)}
    same = lambda x, y: (x, y) in knoll
    for x, y in knoll:   # hills (A2 kind 6) on layer 1
        shape = L._shape(lambda xx, yy: same(xx, yy), x, y, True)
        mp['data'][(1 * H + y) * W + x] = L.A2 + 6 * 48 + shape
    mp['data'][(2 * H + hy - 1) * W + hx] = 11            # World_B: a big tree on top
    # Briarwood needs no new tiles: its entrance sits on the corner of the forest south-west of the capital
    entries = {'Skyreach Hill': (hx, hy, L.exit_page(SKYREACH, 16, SKY_H - 2, 8)),
               'Briarwood': (WORLD_WOOD[0], WORLD_WOOD[1], L.exit_page(ENTRANCE, ENTRANCE_START[0], ENTRANCE_START[1], 8))}
    mp['events'] = [None if e and e['name'] in entries else e for e in mp['events']]
    while len(mp['events']) > 1 and mp['events'][-1] is None: mp['events'].pop()
    for name, (x, y, pg) in entries.items():
        slot = next((k for k in range(1, len(mp['events'])) if mp['events'][k] is None), len(mp['events']))
        ev = {'id': slot, 'name': name, 'note': '<minimap: exit>', 'x': x, 'y': y, 'pages': [pg]}
        if slot == len(mp['events']): mp['events'].append(ev)
        else: mp['events'][slot] = ev


# ====================================================================== playtest: Scene Select (scene_select.py)
def scenes():
    """The prologue's checkpoints for the Scene Select on the title screen (playtest only), from this script's own
    coordinates: (label, (map, x, y, direction), settings). 'done' marks cutscenes that already happened."""
    shard, gate = 'item=%d' % ITEM_SHARD, K.CITY_GATE
    return [
        ('Prologue 0: Opening', (VAULT, 8, 11, 2), []),
        ('Prologue 1: Briarwood, looking for Tobin', (BRIARWOOD, WOOD_START[0], WOOD_START[1], 8), ['v1=1', 'cmd=Clock set 10:00']),
        ('Prologue 2: Briarwood, the rescue', (BRIARWOOD, KAEL_STOP[0], STRIP_Y, 8),
         ['v1=2', 'item=1x3', 'done=Prologue: Briarwood', 'cmd=Clock set 10:30']),
        ('Prologue 4: Main Gate, home with Tobin', (gate, GATE_ROAD[0], GATE_ROAD[1], 8), ['v1=4', shard, 'cmd=Clock set 17:00']),
        ('Prologue 5: Guild, Professor Wyndmere', (GUILD, GUILD_SILL[0], GUILD_SILL[1], 8), ['v1=5', shard, 'cmd=Clock set 17:30']),
        ('Prologue 6: Skyreach Hill, night walk', (SKYREACH, 16, 41, 8), ['v1=6', shard, 'cmd=Clock set 21:00']),
        ('Prologue 6: Skyreach Hill, Mana Sight', (SKYREACH, LOOKOUT[0] - 1, LOOKOUT[1], 8),
         ['v1=6', 's%d=on' % S_MANA_SIGHT, shard, 'done=Prologue: Night Walk', 'tint=-51,-17,68,34', 'cmd=Clock set 21:30']),
        ('Prologue 9: Five months later', (GUILD, 26, 7, 8), ['v1=9', shard, 'cmd=Clock set 09:00'])]


# ====================================================================== the quest log (quests.py, NovaQuests)
def quest():
    """The prologue in the quest log: it follows the story variable, one step per stage. Kael's side of the story only
    (the Order at the crack, stage 8, stays a secret)."""
    from quests import quest, step
    return quest('prologue', 'main', 'Prologue - Flowing Uphill', [
        step(1, 'Briarwood', 'Find Tobin on the old cart road in Briarwood.',
             "Tobin, a carter from the capital, never came home last night. Kael takes the Guild's request and sets out "
             "along the old cart road through Briarwood to find him."),
        step(2, 'Briarwood', 'Protect Tobin.',
             'Deep in the woods, Kael finds Tobin beside his wrecked cart, cornered by a Field Hornet and a Slime.'),
        step(3, 'Briarwood', 'Defeat the strange wolf.',
             'Then a grey wolf steps out of the trees, its mana flowing the wrong way, like a river running uphill. '
             "Before Kael's eyes it changes into something far larger."),
        step(4, 'Main Gate', 'Report to the Guild.',
             'When it falls, the wolf dissolves into purple smoke and leaves behind a cold black crystal: the Tainted '
             'Shard. Kael brings a shaken Tobin home to the capital, where the gate guard has been waiting since dawn.'),
        step(5, "The Lion's Rest", 'Walk with Professor Wyndmere.',
             'The Guild is packed. At its centre sits a face Kael never expected to see again: Professor Isolde '
             'Wyndmere, his old teacher from the Royal Magic Academy. She asks him to walk with her outside the walls '
             'tonight.'),
        step(6, 'Skyreach Hill', 'Follow the flow of mana.',
             "On Skyreach Hill, Kael shows Isolde the shard. With Mana Sight he follows the flow of mana to a crack in "
             "the ground, where the world's mana drains away and the same purple smoke seeps out. Isolde has been "
             'tracking these cracks for two years, each one closer to the capital than the last.'),
        step(9, "The Lion's Rest", 'Collect the Class 3 license.',
             '"Go. See the world. You\'ll find that we are small." Isolde sends Kael back to finish his exam first. '
             'Five months later, exactly one year after graduation, Kael earns his Mage Class 3 license.'),
        step(10, '', '',
             'The shard is still in his pocket. Kael tells the Guild he is stepping away from missions for a while. '
             'It is time to see the world.')], var=V_STAGE, done=10)


if __name__ == '__main__':
    vault, sky, wood = build_vault(), build_skyreach(), build_briarwood()
    out = next((a for a in sys.argv[1:] if not a.startswith('--')), None)
    if out:
        vault.render(os.path.join(out, 'vault.png'), scale=0.5)
        sky.render(os.path.join(out, 'skyreach.png'), scale=0.5, grid=True)
        wood.render(os.path.join(out, 'briarwood.png'), scale=0.5, grid=True)
    if '--save' in sys.argv:
        build_database()
        vault.save(VAULT, parent_id=0, order=VAULT)
        sky.save(SKYREACH, parent_id=K.WORLD, order=SKYREACH)
        wood.save(BRIARWOOD, parent_id=K.WORLD, order=BRIARWOOD)
        import map_briarwood_entrance; map_briarwood_entrance.save()
        for mid, fn in ((FARM, farm_events), (K.CITY_GATE, gate_events), (GUILD, guild_events)):
            L.write_map(mid, patch_events(mid, fn))
        world = json.load(open(L.DATA + 'Map001.json', encoding='utf8'))
        world_entry(world); L.write_map(K.WORLD, world)
        import scene_select; scene_select.register()
        import quests; quests.register()
        print('prologue saved')
