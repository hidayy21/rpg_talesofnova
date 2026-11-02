# Chapter 1 - The Adventure Begins (Story/Chapter1_Scenario.md): the story events after the prologue.
#   python chapter1.py --save           -> write everything (RPG Maker MV must be closed; run prologue.py first)
#
# Story variable 3 "Chapter 1" (the prologue's last scene sets it to 1):
#   1 Class 3 license, free in the Guild     2 leaving the Guild: Yuki lands at the harbor
#   3 back to Kael in Baker's Lane           4 Mom's errand: 2 Honey Bread + 3 Sweet Buns from the market
#   5 errand handed over: Selene comes down       6 Selene's errand: a Silk Ribbon from the Tailor
#   7 ribbon bought: the brawl with Yuki           8 the prison cells (Sera)
#   9 night, outside the prison: Yuki joins        10 to Tobin's house (the bandit story comes next)
# Kael can't leave the capital (Main Gate -> World Map) during the chapter's errands.
# --save is safe to run again: it replaces its own events (note '<chapter1>') and rebuilds the pages it adds.
import sys, json, copy
import nova_maplib as L
from nova_maplib import page, cmd, say, char
import kingdom as K
import prologue as P
from prologue import (kael, npc, plain, tutorial, var, se, gold, item, balloon, wait, fadein, fadeout, transparent, goto, plugin,
                      move, director, cond, shake, flash, BLANK, UP, DOWN, LEFT, RIGHT, T_UP, T_DOWN, T_LEFT, T_RIGHT)

V_CH1 = P.V_CHAPTER1
TAG = '<chapter1>'
YUKI_SPRITE, YUKI_FACE = ('Actor4', 1), ('Actor4', 1)
MOM_FACE = ('family1', 3)
ITEM_BUN, ITEM_HONEY_BREAD = 49, 50
LIST = ((ITEM_HONEY_BREAD, 2), (ITEM_BUN, 3))   # Mom's list: 2 x 150 + 3 x 40 = 420 Z
ERRAND_GOLD = 450
SELENE, SERA = ('family1', 0), ('family1', 1)          # sprite and face share the index
SOLDIER, CAPTAIN = ('People3', 7), ('People3', 6)        # round helmet, plumed helmet
ITEM_RIBBON, RIBBON_PRICE = 52, 120                     # Selene's errand; she pays exactly the price
ENEMY_YUKI, TROOP_YUKI = 39, 44
CLASS_RONIN, ACTOR_YUKI = 2, 2
STOP_HP = 47                                             # the duel stops once either side is under 48% HP

# Saltwind Harbor: Yuki comes off the Morning Gull at the end of the first pier and walks in past Captain Mara (33,15)
YUKI_FROM, HARBOR_VIEW = (39, 15), (33, 13)     # the camera (an invisible Kael) hangs over the pier
TAVERN_STEP = (30, 7)                           # Baker's Lane, just outside the Lion's Rest
MOM_SPOT = (3, 6)                               # Ashveil Residence 1F, in front of Mom (3,4)


def yuki(*lines, name='???'): return say(name, *lines, face=YUKI_FACE)
# a slow fade (frames) for the cuts between Kael and Yuki; the transfer between them uses no fade of its own
def fade_out_slow(frames=60): return [cmd(355, ['$gameScreen.startFadeOut(%d);' % frames])] + wait(frames)
def fade_in_slow(frames=120): return [cmd(355, ['$gameScreen.startFadeIn(%d);' % frames])] + wait(frames)
def fade_bgs(sec): return [cmd(246, [sec])]
# Yuki's scene plays without the minimap and the clock HUD (NovaMinimap, NovaDayNight)
def hud(show): return plugin('Minimap %s' % ('show' if show else 'hide')) + plugin('Clock hud %s' % ('show' if show else 'hide'))
def mom(*lines): return say('Mother', *lines, face=MOM_FACE)
def at(stage): return page(None, cond=cond(stage, var=V_CH1))['conditions']
def selene(*lines): return say('Selene', *lines, face=SELENE)
def sera(*lines, name='Sera'): return say(name, *lines, face=SERA)
def script(js, i=0): return [cmd(355, [js], i)]
def self_on(map_id, ev): return script("$gameSelfSwitches.setValue([%d, %d, 'A'], true);" % (map_id, ev))
# wait for an event's move route that was started without waiting (the scene goes on while it walks)
def wait_route(ev): return script('this._character = $gameMap.event(%d); this.setWaitMode("route");' % ev)
def quest_cmd(s, i=0): return plugin('Quest ' + s, i)
THROUGH_ON, THROUGH_OFF, DIR_FIX_OFF, SPEED = 37, 38, 36, 29


def staged(img, from_stage, until_stage, **kw):
    """A character that only stands there from one chapter stage until another."""
    return [BLANK(), page(img, cond=cond(from_stage, var=V_CH1), **kw), BLANK(**cond(until_stage, var=V_CH1))]


def on_cue(img, from_stage, until_stage, **kw):
    """Like staged(), but hidden until a scene turns its self switch A on (self_on)."""
    return [BLANK(), page(img, cond=cond(from_stage, self_a=True, var=V_CH1), **kw), BLANK(**cond(until_stage, var=V_CH1))]


def staged_pages(mp, pred, from_stage, until_stage, make):
    """Existing events (pred(event)): their own first page, then make(first page) from one chapter stage until another."""
    for e in mp['events']:
        if e and pred(e):
            base = e['pages'][0]
            e['pages'] = [base, dict(make(base), conditions=at(from_stage)), dict(copy.deepcopy(base), conditions=at(until_stage))]


# ====================================================================== database
def build_database():
    system = P.db_load('System')
    system['variables'][V_CH1] = 'Chapter 1'
    with open(L.DATA + 'System.json', 'w', encoding='utf8', newline='') as f:
        json.dump(system, f, ensure_ascii=False, separators=(',', ':'))

    items, enemies, troops = P.db_load('Items'), P.db_load('Enemies'), P.db_load('Troops')
    ribbon = copy.deepcopy(items[P.ITEM_SHARD])
    ribbon.update({'id': ITEM_RIBBON, 'name': 'Silk Ribbon', 'iconIndex': 149, 'price': RIBBON_PRICE,
                   'description': "A midnight-blue silk ribbon from the Tailor's stall.\nFor Selene. Not navy. Midnight.",
                   'note': ''})
    P.db_put(items, ribbon)

    # the street duel: Yuki fights as herself (NovaSvEnemy: her side-view sheet, mirrored), at Kael's level
    yuki_foe = copy.deepcopy(enemies[P.ENEMY_WOLF])
    yuki_foe.update({'id': ENEMY_YUKI, 'name': '???', 'battlerName': 'Swordsman', 'battlerHue': 0, 'exp': 0, 'gold': 0,
                     'dropItems': [{'dataId': 1, 'denominator': 1, 'kind': 0}] * 3,
                     'actions': [{'conditionParam1': 0, 'conditionParam2': 0, 'conditionType': 0, 'rating': 5, 'skillId': 1},
                                 {'conditionParam1': 0, 'conditionParam2': 0, 'conditionType': 0, 'rating': 4, 'skillId': 27},
                                 {'conditionParam1': 0, 'conditionParam2': 0, 'conditionType': 0, 'rating': 4, 'skillId': 129}],
                     'note': '<sv actor: Actor4_2>\n<as class: %d>\n<match level: 1>\n<book:no>\n'
                             'The swordswoman from Hōrai (chapter1.py): the market brawl, never fought to the end.' % CLASS_RONIN})
    P.db_put(enemies, yuki_foe)

    # either side under 48% HP: the screen fades out slowly and the battle stops (no winner, no game over)
    def stop(**c):
        conds = {'actorHp': 50, 'actorId': 1, 'actorValid': False, 'enemyHp': 50, 'enemyIndex': 0, 'enemyValid': False,
                 'switchId': 1, 'switchValid': False, 'turnA': 0, 'turnB': 0, 'turnEnding': False, 'turnValid': False}
        conds.update(c)
        return {'conditions': conds, 'span': 0,
                'list': [*script('$gameScreen.startFadeOut(60);'), *wait(70), cmd(340, []), cmd(0, [])]}
    like = troops[P.TROOP_WOLF]                                 # one enemy, placed like the wolf
    P.db_put(troops, {'id': TROOP_YUKI, 'name': 'Chapter 1: Yuki (market brawl)',
                      'members': [dict(m, enemyId=ENEMY_YUKI) for m in like['members']],
                      'pages': [stop(enemyValid=True, enemyHp=STOP_HP), stop(actorValid=True, actorHp=STOP_HP)]})
    P.db_save('Items', items); P.db_save('Enemies', enemies); P.db_save('Troops', troops)


# ====================================================================== the Guild: out the door, and the story cuts away
def guild_events(add, mp):
    def to_harbor(base):
        return page(None, trigger=1, priority=0, commands=[
            *se('Move1', 70), *fade_out_slow(), *hud(False), *wait(20), *transparent(True), *var(V_CH1, 2),
            *goto(K.HARBOR, HARBOR_VIEW[0], HARBOR_VIEW[1], 2, fade=2)])
    staged_pages(mp, lambda e: e['name'] == 'Exit', 1, 2, to_harbor)


# ====================================================================== Saltwind Harbor: Yuki arrives
def harbor_events(add, mp):
    mara = next(e['id'] for e in mp['events'] if e and e['name'] == 'Captain Mara')
    yuki_ev = add('???', YUKI_FROM[0], YUKI_FROM[1], [BLANK(), page(char(*YUKI_SPRITE, direction=4), cond=None),
                                                      BLANK()], note='<minimap: hide>')
    ev = mp['events'][yuki_ev]
    ev['pages'][1]['conditions'], ev['pages'][2]['conditions'] = at(2), at(3)
    walk_in = len(range(YUKI_FROM[0] - 1, 34, -1))              # down the pier to just short of Captain Mara
    add('Chapter 1: Yuki Arrives', 0, 0, director([
        *transparent(True), *fade_out_slow(1), *hud(False), *fade_in_slow(), *wait(20),   # already black, unless from Scene Select
        *move(yuki_ev, *[LEFT] * walk_in), *move(mara, T_RIGHT), *wait(20),
        *npc('Captain Mara', 'And there she is. Saltwind Harbor,', 'the Royal Capital of Nova.'),
        *yuki('So this is the Western Continent...'),
        *npc('Captain Mara', "Six weeks at sea, and that's all you have to say?"),
        *yuki('The air smells of fresh bread.', 'After six weeks of ship biscuits, that is a lot to say.'),
        *npc('Captain Mara', 'Ha! Fair enough.'),
        *npc('Captain Mara', 'So what brings a swordswoman from Hōrai', 'this far west?'),
        *wait(30), *yuki("...I'm looking for someone."),
        *npc('Captain Mara', 'In a city this size? Try the market.', 'Every rumor in Nova passes through it sooner or later.'),
        *yuki('The market, then.'), *balloon(yuki_ev, 9), *yuki('...And some of that bread.'),
        *npc('Captain Mara', 'Good luck, miss. And mind your purse in the crowds.'),
        # through: the dockhands and cats on the pier must never hold the scene up
        *move(yuki_ev, 37, UP, LEFT, LEFT, LEFT, LEFT, 38, skip=True), *wait(30),
        *yuki('Somewhere on this side of the sea... you are hiding.', 'I will find you.'),
        # the screen fades while she walks on, so she leaves the picture instead of vanishing; the harbor's waves go too
        *move(yuki_ev, 37, LEFT, LEFT, LEFT, LEFT, LEFT, LEFT, 38, w=False, skip=True), *wait(20),
        *fade_bgs(2), *fade_out_slow(100), *wait(20), *transparent(False), *var(V_CH1, 3),
        *goto(K.BAKERS_LANE, TAVERN_STEP[0], TAVERN_STEP[1], 2, fade=2)], 2, var=V_CH1),
        note='<minimap: hide>')


# ====================================================================== Baker's Lane: Mom's list
def bakers_lane_events(add, mp):
    rows = ['\\C[6]Mom\'s list\\C[0]'] + ['- %d %s' % (n, 'Honey Bread' if i == ITEM_HONEY_BREAD else 'Sweet Buns') for i, n in LIST]
    add('Chapter 1: Mom\'s List', 0, 0, director([
        *fade_out_slow(1), *hud(True), *fade_in_slow(), *wait(20),
        *kael("Class 3. Five months of studying, and it's finally done."),
        *kael('Now, before I go anywhere...'),
        *balloon(-1, 1), *kael("Right. Mom's list. She made me promise this morning."),
        *se('Book1'), *plain(*rows, "(the Baker's Stall in the Market District)"),
        *se('Coin'), *gold(ERRAND_GOLD), *plain('Received %d Z from Mom for the shopping.' % ERRAND_GOLD),
        *kael("'And not one coin on spellbooks, Kaelen.'", '...She knows me too well.'),
        *plain('\\C[3]Errand\\C[0]', 'Buy \\C[6]2 Honey Bread\\C[0] and \\C[6]3 Sweet Buns\\C[0] in the Market District,',
               'then bring them home to Mom: the Ashveil house',
               'on \\C[6]Ember Lane\\C[0], in Lantern Row.'),
        *var(V_CH1, 4),
        *tutorial('\\C[6]Save\\C[0] your progress any time from the \\C[6]Menu\\C[0]',
                  '(\\C[6]Esc\\C[0] / \\C[6]X\\C[0] or a right click) and choose \\C[6]Save\\C[0].',
                  'A good habit before a long errand... or a long journey.'),
        *tutorial('\\C[6]Quests\\C[0] in the \\C[6]Menu\\C[0] show your current objective',
                  'and the story so far.',
                  'Lost? The map board in the \\C[6]Grand Plaza\\C[0] shows the whole capital.')], 3, var=V_CH1),
        note='<minimap: hide>')


# ====================================================================== Main Gate: not during the chapter's errands
def gate_events(add, mp):
    def stay(base):
        # stage <= 4: Mom's list; 6-7: Selene's ribbon; later: Tobin (stages 5, 8 and 9 are cutscenes elsewhere)
        lines = [cmd(111, [1, V_CH1, 0, 4, 2], 0), *kael("Not yet. Mom's errand comes first.", i=1), cmd(0, [], 1),
                 cmd(411, [], 0), cmd(111, [1, V_CH1, 0, 7, 2], 1), *kael('Not yet. I promised Selene her ribbon.', i=2),
                 cmd(0, [], 2), cmd(411, [], 1), *kael('Not yet. We should go and see Tobin first.', i=2), cmd(0, [], 2),
                 cmd(412, [], 1), cmd(0, [], 1), cmd(412, [], 0)]
        return page(None, trigger=1, priority=0, commands=lines + move(-1, UP))
    staged_pages(mp, lambda e: e['name'].startswith('To World Map'), 1, 11, stay)


# ====================================================================== Ashveil Residence: home to Mom, then Selene
SELENE_STAIRS, SELENE_SPOT = (14, 3), (2, 6)      # she runs down from 2F to Kael's left (Kael stands at MOM_SPOT)


def home_events(add, mp):
    has_all = ' && '.join('$gameParty.numItems($dataItems[%d]) >= %d' % (i, n) for i, n in LIST)
    sis = add('Selene', SELENE_SPOT[0], SELENE_SPOT[1], staged(char(*SELENE, direction=6), 5, 11, commands=selene(
        'Midnight blue, Brother! From the Tailor in the market.', 'Not navy. Not sky blue. Midnight.')))
    # through the living room and round the kitchen table: down, left, down to the doorway row, left, up, right
    run = [(SPEED, 5), THROUGH_ON, DOWN, LEFT, *[DOWN] * 6, *[LEFT] * 12, *[UP] * 4, RIGHT, THROUGH_OFF, (SPEED, 3)]

    def errand(base):
        give = [cmd(126, [i, 1, 0, n], 1) for i, n in LIST]
        return page(char('family1', 3), commands=[
            cmd(111, [12, has_all], 0),
            *[dict(c, indent=c['indent'] + 1) for c in [
                *mom('Two Honey Bread, three Sweet Buns...', 'and not a single bite missing?'),
                *kael('I was tempted. Very tempted.'),
                *mom('Thank you, dear.')]],
            *give, *se('Item1', i=1),
            *[dict(c, indent=c['indent'] + 1) for c in [
                *mom('So... Class 3. You have that look on your face,', 'the one your father gets before he leaves.'),
                *kael('...Not today. But soon.'),
                *mom("Then promise me you'll say goodbye properly", 'before you go.'),
                *kael('I promise.'),
                *plain('\\C[3]Errand complete.\\C[0]'),
                # Selene has been waiting upstairs for exactly this moment
                *P.place(sis, SELENE_STAIRS[0], SELENE_STAIRS[1], 2), *var(V_CH1, 5),
                *selene('Brotheeer!'), *move(-1, T_RIGHT), *balloon(-1, 1),
                *move(sis, *run), *move(-1, T_LEFT),
                *selene("You're going back to the market, right? Right?"),
                *kael('I just came back from the market.'),
                *selene("The Tailor has a silk ribbon. Midnight blue.", "I've wanted it for weeks!"),
                *kael('Ask me tomorrow, Selene. Today I have plans.'),
                *selene("Oh? The great Class 3 mage is off to see the world...", "and he can't even handle one little errand?"),
                *selene("If you can't manage a small mission like this,", 'how are you going to manage the big ones?'),
                *balloon(-1, 6), *kael("...That's not fair."),
                *kael('Fine. One ribbon.'),
                *balloon(sis, 3), *selene("Yay! Here, I saved up for it."),
                *se('Coin'), *gold(RIBBON_PRICE), *plain('Received %d Z from Selene.' % RIBBON_PRICE),
                *selene('Midnight blue! Not navy, not sky blue. Midnight!'),
                *var(V_CH1, 6), *quest_cmd('start selene_ribbon'), *se('Book1'),
                *plain('\\C[3]New Quest: A Ribbon for Selene\\C[0]',
                       "Buy the \\C[6]Silk Ribbon\\C[0] at the \\C[6]Tailor's stall\\C[0] in the Market District,",
                       'then bring it home to Selene.')]],
            cmd(0, [], 1), cmd(411, [], 0),
            *[dict(c, indent=c['indent'] + 1) for c in
              mom('Did you get everything on my list?', 'Two Honey Bread and three Sweet Buns.',
                  "The Baker's Stall in the market has them.")],
            cmd(0, [], 1), cmd(412, [], 0)])
    staged_pages(mp, lambda e: e['name'] == 'Mother', 4, 5, errand)


def upstairs_events(add, mp):
    """Ashveil 2F: Selene is downstairs, waiting for her ribbon (she comes back up once it is handed over)."""
    staged_pages(mp, lambda e: e['name'] == 'Little Sister', 5, 11, lambda base: BLANK())


# ====================================================================== Market District: the ribbon, and the brawl
SCENE_YUKI, SCENE_KAEL, SCENE_TOBIN = (16, 15), (18, 15), (19, 15)     # Kael ends up between them
KAEL_FROM = (18, 19)                                                    # and walks up to them from here
CROWD = [('People1', 1, 17, 12, 2), ('People2', 4, 19, 12, 2), ('People4', 5, 21, 13, 4), ('People1', 6, 22, 15, 4),
         ('People3', 2, 21, 17, 8), ('People2', 0, 14, 14, 6), ('People4', 3, 13, 16, 6), ('People3', 5, 15, 17, 8)]
SOLDIERS = [(16, 14, 2), (16, 16, 8), (18, 14, 2), (18, 16, 8)]
CAPTAIN_SPOT = (17, 17)
TAILOR_STEP = (34, 23)


def market_events(add, mp):
    tailor = next(e for e in mp['events'] if e and e['name'] == 'Tailor')

    def sells_ribbon(base):
        bought = '$gameParty.numItems($dataItems[%d]) > 0' % ITEM_RIBBON
        return dict(copy.deepcopy(base), list=[
            *npc('Tailor', 'A ribbon for your sister? Midnight blue?', 'Ha! She was here last week, eyeing that one.'),
            cmd(302, [0, ITEM_RIBBON, 0, 0, True]),
            cmd(111, [12, bought], 0),
            *npc('Tailor', 'There you are. She has good taste, your sister.', i=1),
            *var(V_CH1, 7, i=1), *quest_cmd('step selene_ribbon 2', i=1),
            cmd(0, [], 1), cmd(412, [], 0), cmd(0, [], 0)])
    staged_pages(mp, lambda e: e is tailor, 6, 7, sells_ribbon)

    add('???', SCENE_YUKI[0], SCENE_YUKI[1], staged(char(*YUKI_SPRITE, direction=6), 7, 8))
    tobin = add('Tobin', SCENE_TOBIN[0], SCENE_TOBIN[1], staged(char(*P.TOBIN_SPRITE, direction=4), 7, 8))
    for k, (sheet, idx, x, y, d) in enumerate(CROWD):
        add('Onlooker %d' % (k + 1), x, y, staged(char(sheet, idx, direction=d), 7, 8))
    guards = [add('Soldier %d' % (k + 1), x, y, on_cue(char(*SOLDIER, direction=d), 7, 8)) for k, (x, y, d) in enumerate(SOLDIERS)]
    captain = add('Captain', CAPTAIN_SPOT[0], CAPTAIN_SPOT[1], on_cue(char(*CAPTAIN, direction=8), 7, 8))
    shopper = next(e['id'] for e in mp['events'] if e and e['name'] == 'Shopper' and e['x'] == 24)

    add('Chapter 1: The Brawl', 0, 0, director([
        *wait(20), *se('Blow3', 90), *shake(6, 6, 20),
        *npc('Townsfolk', "Somebody call the guard! There's a fight by the shops!"),
        *balloon(-1, 1), *kael('A fight? Here?'),
        *se('Run'), *fade_out_slow(40),
        *P.place(shopper, 27, 12, 2), *goto(K.MARKET, KAEL_FROM[0], KAEL_FROM[1], 8, fade=2), *wait(10), *fade_in_slow(60),
        *move(-1, UP, UP, UP, UP), *move(-1, T_RIGHT), *balloon(-1, 1),
        *kael('Tobin?!'), *balloon(tobin, 6), *npc('Tobin', 'K-Kael...'),
        *move(-1, T_LEFT),
        *kael('Hey, you in the strange clothes!', 'What do you think you are doing?'),
        *yuki('Step aside. I saw that man stealing.'),
        *npc('Tobin', "NO! I-I didn't steal anything..."),
        *kael('Listen, miss. This man is someone I know.', "There's no way he stole from you."),
        *yuki('Hmph. Thieves always cover for each other.'),
        *se('Sword4', 90), *flash([255, 255, 255, 170], 12), *yuki('Bring it on.'),
        *kael("Tch. Guess I've got no choice."),
        # Kael can't lose: the battle stops itself under 48% HP (troop), and a loss is no game over anyway
        cmd(314, [0, 0]),                         # full HP first, or a hurt Kael would stop the duel at once
        cmd(301, [0, TROOP_YUKI, False, True]),
        *script('if ($gameScreen.brightness() > 0) $gameScreen.startFadeOut(30);'), *wait(30),
        cmd(314, [0, 0]),
        *[c for g in guards + [captain] for c in self_on(K.MARKET, g)], *wait(30), *fade_in_slow(60),
        *shake(4, 6, 15), *npc('Soldier', 'HEY, YOU TWO!', 'No brawling inside the city walls!'),
        *kael('But she—'),
        *npc('Captain', 'Take them to the prison!'),
        *kael('Hey, wait—'),
        *fade_out_slow(100), *var(V_CH1, 8), *goto(K.PRISON_CELLS, CELL_KAEL[0], CELL_KAEL[1], 6, fade=2)], 7, var=V_CH1),
        note='<minimap: hide>')


# ====================================================================== Royal Prison: one cell, two prisoners
# the top-right cell (above the message box); its door is the Cell Door at (22,7). Old Pell, its usual prisoner,
# spends the scene in the empty bottom-right cell instead.
CELL_KAEL, CELL_YUKI, CELL_DOOR = (22, 5), (23, 5), (22, 7)
PELL_SPOT = (23, 14)
GUARD_FROM, GUARD_AT = (3, 8), (22, 8)         # the guard walks the upper corridor to the cell
SERA_AT, KAEL_OUT = (20, 8), (22, 8)


def prison_events(add, mp):
    door = next(e['id'] for e in mp['events'] if e and e['name'] == 'Cell Door' and (e['x'], e['y']) == CELL_DOOR)
    pell = next(e for e in mp['events'] if e and e['name'] == 'Old Pell')
    add('Old Pell', PELL_SPOT[0], PELL_SPOT[1], staged(pell['pages'][0]['image'], 8, 9, commands=pell['pages'][0]['list'][:-1]))
    staged_pages(mp, lambda e: e is pell, 8, 9, lambda base: BLANK())
    yuki_ev = add('Yuki', CELL_YUKI[0], CELL_YUKI[1], staged(char(*YUKI_SPRITE, direction=8), 8, 9))
    guard = add('Prison Guard', GUARD_FROM[0], GUARD_FROM[1], staged(char(*SOLDIER, direction=6), 8, 9))
    sis = add('Seraphine', SERA_AT[0], SERA_AT[1], on_cue(char(*SERA, direction=6), 8, 9))
    add('Chapter 1: The Cell', 0, 0, director([
        *fade_out_slow(1), *wait(30), *fade_in_slow(), *wait(30),
        *kael("Hey. Listen... I'm sorry.", "But I'm not a thief. And neither is the man from before."),
        *yuki('......'),
        *move(guard, THROUGH_ON, *[RIGHT] * (GUARD_AT[0] - GUARD_FROM[0]), T_UP, THROUGH_OFF, w=False),
        *kael("My name's Kael. Class 3 Mage. Nice to meet you."),
        *kael("I've never seen clothes like yours before."),
        *yuki('......'), *wait(30), *move(yuki_ev, T_LEFT),
        *yuki('Yuki.', 'I come from Hōrai.', name='Yuki'),
        *kael('Hōrai? Hmm...', "Isn't that on the Eastern Continent?"),
        *wait_route(guard), *se('Key'),
        *npc('Prison Guard', 'Ashveil! Out you come.'),
        *se('Open1'), *move(door, DIR_FIX_OFF, T_DOWN, (L.R_WAIT, 3), T_LEFT, (L.R_WAIT, 3), T_RIGHT, (L.R_WAIT, 3), T_UP,
                            THROUGH_ON),
        *move(guard, RIGHT, T_LEFT),
        *move(-1, T_DOWN, DOWN, THROUGH_ON, DOWN, THROUGH_OFF),
        *fade_out_slow(30), *goto(K.PRISON_CELLS, KAEL_OUT[0], KAEL_OUT[1], 4, fade=2), *self_on(K.PRISON_CELLS, sis),
        *wait(10), *fade_in_slow(40),
        *sera('You really are something...', name='???'),
        *balloon(-1, 1), *kael('Sister!', 'Er... I mean... Sera!'),
        *sera('Plenty of witnesses have given their statements.', "That's the only reason you're walking out.",
              'I just happened to be here on an inspection.'),
        *kael('......'),
        *move(-1, T_RIGHT),
        *kael("Can't you let that woman out too?", 'I think this is all a misunderstanding.'),
        *npc('Prison Guard', 'Not a chance. If it weren\'t for Sir Seraphine,', "you'd still be rotting in—\\^"),
        *shake(3, 8, 10), *sera('Soldier!'),
        *move(-1, T_LEFT),
        *sera('Haah... Always doing whatever you please.'),
        *kael('She only attacked because she saw him acting like a thief.', "She's not a bad person.",
              "Besides, she's from the East. She must still be finding her feet here."),
        *sera('......'),
        *sera('Listen. If she walks free,', 'she apologizes to the man she accused.'),
        *kael("Fine. I'll make sure of it.", 'So... can she go?'),
        *balloon(sis, 5),
        *sera("I'll speak to the head jailer."),
        *kael('Thanks, Sera!'),
        *fade_out_slow(100), *var(V_CH1, 9), *plugin('Clock set 20:30'),
        *goto(K.CASTLE_APPROACH, NIGHT_KAEL[0], NIGHT_KAEL[1], 6, fade=2)], 8, var=V_CH1),
        note='<minimap: hide>')


# ====================================================================== Castle Approach: night, outside the prison
NIGHT_KAEL, NIGHT_YUKI = (7, 23), (8, 23)      # in front of the Royal Prison door (7,21), between its guards


def castle_events(add, mp):
    yuki_ev = add('Yuki', NIGHT_YUKI[0], NIGHT_YUKI[1], staged(char(*YUKI_SPRITE, direction=4), 9, 10))
    add('Chapter 1: Night Outside the Prison', 0, 0, director([
        *fade_out_slow(1), *wait(30), *fade_in_slow(), *wait(20),
        *yuki('Thank you for getting me out.', name='Yuki'),
        *kael("It's Yuki, right? Listen. I know you're not a bad person.",
              'But in this country, attacking a man just because',
              "you think he's a thief isn't okay."),
        *yuki("I'm sorry...", 'But I saw him take coins from people\'s pockets.',
              "Honestly, I'm surprised nobody noticed.", name='Yuki'),
        *kael('Hmm....'),
        *kael("Tell you what. Let's go to his house,", 'so you can see the truth for yourself and be at ease.'),
        *yuki("Very well. I don't know where else to go right now anyway.", name='Yuki'),
        *kael('Okay, follow me.'),
        *script('$gameActors.actor(%d).changeLevel($gameActors.actor(1).level, false);' % ACTOR_YUKI),
        cmd(129, [ACTOR_YUKI, 0, False]), cmd(314, [0, 0]), *var(V_CH1, 10),
        *se('Item3'), *plain('\\C[3]Yuki joined the party!\\C[0]'),
        *se('Book1'), *plain('\\C[3]New Quest\\C[0]', 'Take Yuki to \\C[6]Tobin\'s house\\C[0]',
                             'and find out what really happened in the market.')], 9, var=V_CH1),
        note='<minimap: hide>')


# ====================================================================== playtest: Scene Select
def scenes():
    base = ['v1=10', 'item=%d' % P.ITEM_SHARD]
    goods = ['item=%dx%d' % (i, n) for i, n in LIST]
    return [
        ('Chapter 1: the Guild, after the license', (P.GUILD, 26, 7, 8), base + ['v3=1', 'cmd=Clock set 09:10']),
        ('Chapter 1: Yuki arrives at the harbor', (K.HARBOR, HARBOR_VIEW[0], HARBOR_VIEW[1], 2), base + ['v3=2', 'cmd=Clock set 09:15']),
        ("Chapter 1: Mom's list", (K.BAKERS_LANE, TAVERN_STEP[0], TAVERN_STEP[1], 2), base + ['v3=3', 'cmd=Clock set 09:20']),
        ('Chapter 1: home to Mom with the shopping', (K.ASHVEIL_1F, MOM_SPOT[0], MOM_SPOT[1], 8),
         base + ['v3=4'] + goods + ['cmd=Clock set 10:30']),
        ("Chapter 1: Selene's ribbon, at the Tailor", (K.MARKET, TAILOR_STEP[0], TAILOR_STEP[1], 8),
         base + ['v3=6', 'gold=%d' % RIBBON_PRICE, 'cmd=Quest start selene_ribbon', 'cmd=Clock set 11:00']),
        ('Chapter 1: the prison cell with Yuki', (K.PRISON_CELLS, CELL_KAEL[0], CELL_KAEL[1], 6),
         base + ['v3=8', 'item=%d' % ITEM_RIBBON, 'cmd=Quest step selene_ribbon 2', 'cmd=Clock set 15:00']),
        ('Chapter 1: night outside the prison (Yuki joins)', (K.CASTLE_APPROACH, NIGHT_KAEL[0], NIGHT_KAEL[1], 6),
         base + ['v3=9', 'item=%d' % ITEM_RIBBON, 'cmd=Quest step selene_ribbon 2', 'cmd=Clock set 20:30'])]


# ====================================================================== the quest log (quests.py, NovaQuests)
def quest():
    """Chapter 1 in the quest log: it follows the chapter's story variable (not completed yet: the chapter goes on)."""
    from quests import quest, step
    return quest('chapter1', 'main', 'Chapter 1 - The Adventure Begins', [
        step(1, "The Lion's Rest", 'Leave the Guild.',
             "License in hand, Kael is free at last. The world is waiting just outside the Guild's door."),
        step(2, 'Saltwind Harbor', '',
             'Meanwhile, the Morning Gull docks at Saltwind Harbor. A swordswoman from Hōrai steps ashore, six weeks '
             'from home, looking for someone.'),
        step(4, 'Market District', "Buy 2 Honey Bread and 3 Sweet Buns at the Baker's Stall, then take them home to "
             'Mom on Ember Lane (Lantern Row).',
             "Before he goes anywhere, Kael has a promise to keep: Mom's shopping list. Two Honey Bread and three Sweet "
             "Buns from the Baker's Stall in the Market District, and not one coin on spellbooks. Then home with them, "
             'to the Ashveil house on Ember Lane, in the south of Lantern Row.'),
        step(5, 'Ember Lane, Lantern Row', '',
             'Mom gets her bread, and Kael promises to say goodbye properly before he leaves.'),
        step(6, 'Market District', "Buy the Silk Ribbon at the Tailor's stall for Selene.",
             'Then Selene comes running downstairs: a midnight-blue silk ribbon from the Tailor, please. Kael says no. '
             "Selene asks how a Class 3 mage plans to manage big missions if he can't manage a small one. Kael says yes."),
        step(7, 'Market District', '',
             'Ribbon in hand, Kael hears a commotion by the shops. A swordswoman in strange clothes has knocked Tobin '
             'the carter to the ground, swearing he is a thief. Kael stands between them, and the stranger draws her sword.'),
        step(8, 'Royal Prison', '',
             'The city guard breaks up the fight and throws them both in the same cell. The swordswoman is Yuki, from '
             'Hōrai. Sera, on an inspection, gets Kael out, and on his word has Yuki released too, on one condition: '
             'Yuki apologizes to the man she accused.'),
        step(10, "Tobin's house", "Take Yuki to Tobin's house.",
             'Outside the prison at night, Yuki insists she saw Tobin picking pockets. To settle it, Kael offers to take '
             "her to Tobin's house. With nowhere else to go, Yuki joins him.")], var=V_CH1)


def sub_quests():
    """Selene's errand: started by her (Ashveil 1F), step 2 once the ribbon is bought. Handing it over comes later."""
    from quests import quest, step
    return [quest('selene_ribbon', 'sub', 'A Ribbon for Selene', [
        step(1, 'Market District', "Buy the Silk Ribbon at the Tailor's stall.",
             "Selene wants the midnight-blue silk ribbon from the Tailor's stall, and she paid the %d Z herself. "
             'Not navy. Not sky blue. Midnight.' % RIBBON_PRICE),
        step(2, 'Ember Lane, Lantern Row', 'Bring the ribbon home to Selene.',
             'The ribbon is bought. Now it only has to make it home.')], done=3)]


if __name__ == '__main__':
    if '--save' in sys.argv:
        build_database()
        for mid, fn in ((P.GUILD, guild_events), (K.HARBOR, harbor_events), (K.BAKERS_LANE, bakers_lane_events),
                        (K.CITY_GATE, gate_events), (K.ASHVEIL_1F, home_events), (K.ASHVEIL_2F, upstairs_events),
                        (K.MARKET, market_events), (K.PRISON_CELLS, prison_events), (K.CASTLE_APPROACH, castle_events)):
            L.write_map(mid, P.patch_events(mid, fn, tag=TAG))
        import scene_select
        scene_select.register_plugin('NovaChapterCard', 'Chapter title cards: an animated title in the middle of the '
                                     'screen on black ("Prologue Ends", "Chapter 1 / The Adventure Begins").',
                                     {'Duration': '300', 'Head Color': '#e8cf8a'})
        scene_select.register_plugin('NovaSvEnemy', 'Enemies drawn with a side-view actor sheet (animated, mirrored '
                                     'to face the party), and enemies whose stats follow an actor\'s level.')
        scene_select.register()
        import quests; quests.register()
        print('chapter 1 saved')
