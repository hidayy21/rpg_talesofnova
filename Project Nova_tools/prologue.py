# The playable Prologue (Story/Prolog_Scenario.md): database entries, two new maps and the story events on
# existing maps.
#   python prologue.py preview_dir      -> preview images of the new maps
#   python prologue.py --save           -> write everything (RPG Maker MV must be closed)
#
# Story flags: variable 1 "Prologue" (stage), variable 2 "Pests Cleared", switch 11 "Mana Sight".
#   0 opening (Sealed Vault)        1 Hollow Farm: talk to Bram     3 pests cleared, wolf at the pond
#   4 wolf beaten (shard)           5 go back to the Guild          6 night walk on Skyreach Hill
#   8 the Order at the crack        9 five months later (license)   10 prologue over
# Kael can't leave Hollow Farm before stage 5; at stage 5 the World Map exits of the Main Gate turn him back and the
# gate itself leads straight into the Guild.
# --save is safe to run again: it replaces its own records/events (matched by id/name) and leaves the rest alone.
import sys, os, json, math, copy
import nova_maplib as L
from nova_maplib import page, cmd, text, say, char, rt
import town_kit as T
import kingdom as K

V_STAGE, V_PESTS, S_MANA_SIGHT = 1, 2, 11
VAULT, SKYREACH = 27, 28
FARM, GUILD = 24, K.TAVERN
KAEL, ISOLDE = ('Actor4', 0), ('family1', 5)
ISOLDE_SPRITE, ORDER_SPRITE, WOLF_SPRITE = ('family1', 5), ('People2', 2), ('Animals2', 1)
ITEM_SHARD, STATE_VEIL, ENEMY_WOLF, CE_PESTS = 51, 36, 38, 25
TROOP_SLIME, TROOP_HORNET, TROOP_WOLF = 41, 42, 43
WORLD_HILL = (58, 30)                      # Skyreach Hill on the World Map; you come back out one tile below


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


def cond(stage=None, self_a=False, sw=None):
    c = {}
    if stage is not None: c.update({'variableValid': True, 'variableId': V_STAGE, 'variableValue': stage})
    if self_a: c.update({'selfSwitchValid': True, 'selfSwitchCh': 'A'})
    if sw: c.update({'switch1Valid': True, 'switch1Id': sw})
    return c


BLANK = lambda **c: page(None, priority=0, cond=c or None)


def director(commands, stage):
    """Autorun that plays once from the given stage on: [nothing, autorun (stage), done (self switch A)]."""
    return [BLANK(), page(None, trigger=3, priority=0, commands=commands + self_sw(), cond=cond(stage)),
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

    # one enemy each, both weak to Fire; whichever is fought first also explains the basics
    def basics():
        return [cmd(111, [1, V_PESTS, 0, 0, 0], 0)] + plain(
            '\\C[3]Battle Tutorial\\C[0]', 'Time flows in battle. When Kael\'s gauge on the timeline',
            'fills, it is his turn: Attack, use a Skill or an Item.', i=1) + plain(
            'Try \\C[6]Fire\\C[0] from Kael\'s Magic. Spells cost MP.', i=1) + [cmd(0, [], 1), cmd(412, [], 0)]
    troop(TROOP_SLIME, 'Prologue: Slime', 'Minotaur', eid['Slime'], [troop_page(basics() + plain(
        'Slimes are weak to \\C[2]Fire\\C[0]. A hit on a weakness is always', 'a \\C[6]CRITICAL\\C[0] hit and wears down the enemy\'s \\C[6]Guard\\C[0].',
        'The plate under the enemy shows its Guard and weaknesses.')
        + plain('When the Guard runs out the enemy is \\C[2]Broken\\C[0]:', 'it loses its next turn and takes 50% more damage.'), turn0=True)])
    troop(TROOP_HORNET, 'Prologue: Field Hornet', 'Minotaur', eid['Field Hornet'], [troop_page(basics() + plain(
        'Hornets are weak to \\C[2]Fire\\C[0] too. Burn it before it stings!')
        + plain('Battle too slow? Press \\C[6]Shift\\C[0] or click \\C[6]SPEED\\C[0] at the top right',
                'to switch between x1, x1.5 and x2. It stays as you leave it.'), turn0=True)])
    for t in range(TROOP_WOLF + 1, len(troops)):          # troops left over from an older version of this script
        if troops[t] and troops[t]['name'].startswith('Prologue:'): troops[t] = None
    while troops[-1] is None: troops.pop()
    troop(TROOP_WOLF, 'Prologue: Corrupted Wolf', 'Minotaur', ENEMY_WOLF, [
        troop_page([cmd(333, [0, 0, STATE_VEIL])] + plain('Black-violet veins pulse under the wolf\'s fur.',
                                                         'Its mana moves like water flowing uphill...'), turn0=True),
        troop_page([cmd(333, [0, 1, STATE_VEIL]), cmd(337, [0, 101, False])] + se('Break', 90)
                   + plain('The corruption \\C[2]cracks\\C[0]!', 'Its weakness to \\C[2]Fire\\C[0] shows through.'), enemy_hp=50)])

    shard = copy.deepcopy(items[1])
    shard.update({'id': ITEM_SHARD, 'name': 'Tainted Shard', 'iconIndex': 161, 'itypeId': 2, 'consumable': False,
                  'occasion': 3, 'scope': 0, 'price': 0, 'effects': [], 'animationId': 0, 'speed': 0, 'successRate': 100,
                  'damage': {'critical': False, 'elementId': 0, 'formula': '0', 'type': 0, 'variance': 20},
                  'description': 'A cold black crystal left by a corrupted wolf.\nIts mana flows the wrong way.',
                  'note': ''})
    db_put(items, shard)

    db_put(ces, {'id': CE_PESTS, 'name': 'Prologue: Pest Cleared', 'switchId': 1, 'trigger': 0, 'list': var(V_PESTS, 1, op=1) + [
        cmd(111, [1, V_PESTS, 0, 2, 1], 0),
        *kael("That's the last of them. ...Huh.", "Slimes don't usually crawl *toward* a farm.", i=1),
        *se('Dog', 90, i=1), *balloon(9, 1, i=1), *balloon(-1, 1, i=1),
        *npc('Farm Dog', 'Grrrr... Woof! Woof!', i=1),
        *npc('Rancher Bram', 'Done already? ...Then what has the animals so spooked?', i=1),
        *kael('Something is out by the pond, west side.', 'Stay here, Mister Bram.', i=1),
        *var(V_STAGE, 3, i=1), cmd(0, [], 1), cmd(412, [], 0), cmd(0, [])]})

    for i_, n in ((V_STAGE, 'Prologue'), (V_PESTS, 'Pests Cleared')): system['variables'][i_] = n
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
        *var(V_STAGE, 1), *plugin('Clock set 12:00'), *plugin('Clock start'), *plugin('Clock hud show'),
        *plugin('Minimap show'), *transparent(False),
        *goto(FARM, 15, 20, 8)], 0))
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
        *kael('Hollow Farm, by the pond. A wolf whose mana', 'flowed backwards. Fire sank into it like water.', 'When it died, it melted, and left *this*.'),
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


# ====================================================================== existing maps
def patch_events(map_id, build):
    """Drop this script's events (note '<prologue>') from the map, then add new ones; build(add) returns nothing."""
    mp = json.load(open(L.DATA + 'Map%03d.json' % map_id, encoding='utf8'))
    mp['events'] = [None if e and '<prologue>' in e.get('note', '') else e for e in mp['events']]
    while len(mp['events']) > 1 and mp['events'][-1] is None: mp['events'].pop()

    def add(name, x, y, pages, note=''):
        slot = next((k for k in range(1, len(mp['events'])) if mp['events'][k] is None), len(mp['events']))
        ev = {'id': slot, 'name': name, 'note': (note + '\n<prologue>').strip(), 'pages': pages, 'x': x, 'y': y}
        if slot == len(mp['events']): mp['events'].append(ev)
        else: mp['events'][slot] = ev
        return slot
    build(add, mp)
    return mp


def staged_pages(mp, prefix, from_stage, until_stage, make):
    """Existing events named prefix*: their own first page, then make(first page) from one stage until another."""
    for e in mp['events']:
        if e and e['name'].startswith(prefix):
            base = e['pages'][0]
            e['pages'] = [base, dict(make(base), conditions=page(None, cond=cond(from_stage))['conditions']),
                          dict(copy.deepcopy(base), conditions=page(None, cond=cond(until_stage))['conditions'])]


def hold_exits(mp, prefix, lines, step, from_stage, until_stage):
    """Map exits that turn Kael back (he talks to himself) from one stage until another."""
    staged_pages(mp, prefix, from_stage, until_stage,
                 lambda base: page(None, trigger=1, priority=0, commands=kael(*lines) + move(-1, step)))


def farm_events(add, mp):
    ev = {e['name']: e['id'] for e in mp['events'] if e}
    bram = ev['Rancher Bram']
    hold_exits(mp, 'To Main Gate', ("Not yet. There's still something", 'I need to finish here.'), LEFT, 1, 5)
    add('Prologue: The Job', 1, 15, director([
        *fadein(), *move(bram, T_DOWN),
        *kael("Request from the Guild: 'Pests in the south field.", "Please hurry.' That's me."),
        *kael('Kaelen Ashveil, Mage Class 4, at your service.'),
        *npc('Rancher Bram', 'Class 4? Bit much for some field vermin, isn\'t it?'),
        *kael("Every mission counts. I'm making Class 3", 'within the year.'),
        *npc('Rancher Bram', 'Hah! Then go count some vermin for me, lad.', 'The crop field, south-east. A slime and a hornet.'),
        *npc('Rancher Bram', 'And take these. My wife insists.'), *se('Item1'), *item(1, 3), *plain('Received 3 \\C[6]Potions\\C[0].'),
        *tutorial('Move with the arrow keys or a click. Hold \\C[6]Shift\\C[0] to dash.',
                  'Talk and examine with \\C[6]Enter\\C[0] / \\C[6]Z\\C[0]. Touch a monster to fight it.')], 1))
    for name, (x, y), img, troop in (('Pest: Slime', (34, 27), char('Monster', 1), TROOP_SLIME),
                                     ('Pest: Hornet', (30, 28), char('$Pet_Hornet', 0), TROOP_HORNET)):
        add(name, x, y, [BLANK(), page(img, trigger=2, move_type=1, freq=2, speed=2, step_anim=True, cond=cond(1),
                                       commands=battle(troop) + heal() + self_sw() + common(CE_PESTS)),
                         page(None, priority=0, cond=cond(self_a=True))],
            note='<minimap: npc>')
    wolf_scene = [
        *se('Wolf', 80), *balloon(-1, 1), *move(0, T_RIGHT),
        *kael('A grey wolf? No... its mana is all *wrong*.', "It's like looking at a river flowing uphill."),
        *se('Growl', 90), *flash([120, 60, 200, 160], 30), *anim(0, 103),
        *kael("It's... changing!"),
        *battle(TROOP_WOLF), *heal(),
        *anim(0, 104), *se('Darkness3', 80), *self_sw(),
        *plain('The wolf dissolves into violet smoke.', 'Only a small black crystal is left in the grass.'),
        *kael('It just... dissolved? Wolves don\'t do that.'),
        *se('Item3'), *item(ITEM_SHARD),
        *plain('Got the \\C[6]Tainted Shard\\C[0]!'),
        *kael('Cold. And the mana inside is moving the wrong way.', "Like it's being *pulled* somewhere."),
        *flash([255, 240, 170, 120], 20), *se('Saint1', 50),
        *kael("...Must've been my fire reflecting. Right."),
        *fadeout(), *goto(FARM, 15, 20, 8), *move(bram, T_DOWN), *fadein(),
        *npc('Rancher Bram', 'You look like you\'ve seen a ghost, lad. What was it?'),
        *kael('A wolf. A very rude wolf.'),
        *npc('Rancher Bram', "Wolves *and* vermin. I'm paying you", 'for the vermin only, mind.'),
        *kael('...Fair.'), *se('Coin'), *gold(120), *plain('Received 120 Z.'),
        *var(V_STAGE, 5),
        *tutorial('Open the \\C[6]Menu\\C[0] with \\C[6]Esc\\C[0] / \\C[6]X\\C[0] or a right click:',
                  'Items (the shard is under Key Items), Skills, Equip and Status.',
                  'Press \\C[6]M\\C[0] to show or hide the minimap.'),
        *tutorial('Report back to the Guild: \\C[6]The Lion\'s Rest\\C[0].',
                  'Head east to the Main Gate and go through it.')]
    add('Corrupted Wolf', 1, 24, [BLANK(), page(char(*WOLF_SPRITE, direction=6), trigger=1, commands=wolf_scene,
                                                step_anim=True, cond=cond(3)),
                                  page(None, priority=0, cond=cond(self_a=True))])


GUILD_DOOR = (10, 13)                      # where the Tavern Door in Baker's Lane lets you in
# Isolde sits on the stool right of the west table (3,10); the crowd stands around her (name, sheet, index, x, y, facing)
ISOLDE_SEAT = (4, 10)
CROWD = [('Young Mage', 'People4', 3, 3, 9, 2), ('Scholar', 'People2', 1, 4, 9, 2), ('Mage', 'People2', 6, 2, 9, 2),
         ('Mercenary', 'People3', 4, 5, 9, 4), ('Sellsword', 'People3', 0, 5, 10, 4), ('Battle Mage', 'People4', 5, 5, 11, 4),
         ('Apprentice', 'People1', 3, 4, 11, 8)]


def gate_events(add, mp):
    """Main Gate during the walk back to the Guild: no way out into the world, and the gate leads straight to the Guild."""
    hold_exits(mp, 'To World Map', ('Not yet. I still have something to finish:', 'my report to the Guild.'), UP, 1, 9)

    def to_guild(base):
        p = copy.deepcopy(base)
        for c in p['list']:
            if c['code'] == 201: c['parameters'] = [0, GUILD, GUILD_DOOR[0], GUILD_DOOR[1], 8, 0]
        return p
    staged_pages(mp, 'Main Gate', 5, 6, to_guild)


def guild_events(add, mp):
    crowd = {}
    for name, sheet, idx, x, y, d in CROWD:
        crowd[name] = add(name, x, y, staged(char(sheet, idx, direction=d), 5, 6))
    isolde_ev = add('Isolde', ISOLDE_SEAT[0], ISOLDE_SEAT[1], staged(char(*ISOLDE_SPRITE, direction=4), 5, 6))
    clerk = next(e['id'] for e in mp['events'] if e and e['name'] == 'Guild Clerk')
    # Kael comes in at the door (10,13), squeezes through the crowd and ends up at Isolde's table, on (5,10)
    add('Prologue: The Crowd', 0, 0, director([
        *npc('Young Mage', 'Is it really her? I thought she retired!'),
        *npc('Mercenary', 'Hah, every mage in the capital is here.', "Look at 'em. Like moths to a lamp."),
        *balloon(-1, 1), *kael("Whoa. What's everyone crowding around?"),
        # through: the Barmaid wanders around here and must never hold the scene up
        *move(-1, 37, LEFT, LEFT, LEFT, LEFT, UP, 38, skip=True),
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
        *kael("Not this time. I'm done taking missions here.", "I'm going to see the world."),
        *var(V_STAGE, 10),
        *plain('\\C[6]Prologue - End\\C[0]', 'Chapter 1: The Day of the Class Exam')], 9))


def world_entry(mp):
    """Skyreach Hill on the World Map: a wooded knoll north-west of the capital."""
    W, H = mp['width'], mp['height']
    hx, hy = WORLD_HILL
    knoll = {(hx + dx, hy + dy) for dx in (-1, 0, 1) for dy in (-1, 0)}
    same = lambda x, y: (x, y) in knoll
    for x, y in knoll:   # hills (A2 kind 6) on layer 1
        shape = L._shape(lambda xx, yy: same(xx, yy), x, y, True)
        mp['data'][(1 * H + y) * W + x] = L.A2 + 6 * 48 + shape
    mp['data'][(2 * H + hy - 1) * W + hx] = 11            # World_B: a big tree on top
    mp['events'] = [None if e and e['name'] == 'Skyreach Hill' else e for e in mp['events']]
    while len(mp['events']) > 1 and mp['events'][-1] is None: mp['events'].pop()
    slot = next((k for k in range(1, len(mp['events'])) if mp['events'][k] is None), len(mp['events']))
    ev = {'id': slot, 'name': 'Skyreach Hill', 'note': '<minimap: exit>', 'x': hx, 'y': hy,
          'pages': [L.exit_page(SKYREACH, 16, SKY_H - 2, 8)]}
    if slot == len(mp['events']): mp['events'].append(ev)
    else: mp['events'][slot] = ev


if __name__ == '__main__':
    vault, sky = build_vault(), build_skyreach()
    out = next((a for a in sys.argv[1:] if not a.startswith('--')), None)
    if out:
        vault.render(os.path.join(out, 'vault.png'), scale=0.5)
        sky.render(os.path.join(out, 'skyreach.png'), scale=0.5, grid=True)
    if '--save' in sys.argv:
        build_database()
        vault.save(VAULT, parent_id=0, order=VAULT)
        sky.save(SKYREACH, parent_id=K.WORLD, order=SKYREACH)
        for mid, fn in ((FARM, farm_events), (K.CITY_GATE, gate_events), (GUILD, guild_events)):
            L.write_map(mid, patch_events(mid, fn))
        world = json.load(open(L.DATA + 'Map001.json', encoding='utf8'))
        world_entry(world); L.write_map(K.WORLD, world)
        print('prologue saved')
