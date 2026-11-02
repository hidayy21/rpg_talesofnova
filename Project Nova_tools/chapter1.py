# Chapter 1 - The Adventure Begins (Story/Chapter1_Scenario.md): the story events after the prologue.
#   python chapter1.py --save           -> write everything (RPG Maker MV must be closed; run prologue.py first)
#
# Story variable 3 "Chapter 1" (the prologue's last scene sets it to 1):
#   1 Class 3 license, free in the Guild     2 leaving the Guild: Yuki lands at the harbor
#   3 back to Kael in Baker's Lane           4 Mom's errand: 2 Honey Bread + 3 Sweet Buns from the market
#   5 errand handed over: Selene comes down       6 Selene's errand: a Silk Ribbon from the Tailor
#   7 ribbon bought: the brawl with Yuki           8 the prison cells (Sera)
#   9 night, outside the prison: Yuki joins        10 to Tobin's house
#   11 Greta: Tobin went out, to Briarwood          12 the bandits in Briarwood
#   13 back at the Main Gate                        14 home at midnight: supper, Yuki's brother, the letter
#   15 the morning: Kael wakes on 3F, breakfast below 16 the Main Gate is open: out into the world
# Kael can't leave the capital (Main Gate -> World Map) during the chapter's errands, only to go after Tobin (11-13).
# --save is safe to run again: it replaces its own events (note '<chapter1>') and rebuilds the pages it adds.
import sys, json, copy
import nova_maplib as L
from nova_maplib import page, cmd, say, char
import kingdom as K
import prologue as P
from prologue import (kael, npc, plain, tutorial, var, se, gold, item, balloon, wait, fadein, fadeout, transparent, goto, plugin,
                      move, director, cond, shake, flash, anim, BLANK, UP, DOWN, LEFT, RIGHT, T_UP, T_DOWN, T_LEFT, T_RIGHT)

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
ENEMY_LACKEY, ENEMY_LEADER, TROOP_BANDITS = 40, 41, 45
CLASS_RONIN, ACTOR_YUKI = 2, 2
STOP_HP = 47                                             # the duel stops once either side is under 48% HP
GRETA = ('People4', 7)                                   # Tobin's wife (placeholder sprite)
# the bandits on the map (Evil sheet) and the same faces knocked out (Damage2)
BANDIT_A, BANDIT_B, BANDIT_LEADER = ('Evil', 0), ('Evil', 4), ('Evil', 1)
DOWN_A, DOWN_B, DOWN_LEADER = ('Damage2', 0), ('Damage2', 1), ('Damage2', 7)
ANIM_FIRE = 66                                           # Fire One: Kael's answer to the bandit who grabs him

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

    # Briarwood: the crew Tobin pays, sized for Kael and Yuki at about level 2-3 (two lackeys, then their leader).
    # Their skills hit for ATK x4 - DEF x2: at ATK 20 a lackey did 0 to Yuki (DEF 44 at level 3, katana + hat + cloth);
    # ATK 32/38 lands about 30-60 a hit on her and 50-80 on Kael
    def bandit(eid, name, battler, params, exp, gold, actions, note):
        foe = copy.deepcopy(enemies[11])                        # the road Bandit: traits, drops
        foe.update({'id': eid, 'name': name, 'battlerName': battler, 'battlerHue': 0, 'params': params, 'exp': exp,
                    'gold': gold, 'actions': [{'conditionParam1': 0, 'conditionParam2': 0, 'conditionType': 0,
                                               'rating': r, 'skillId': k} for k, r in actions], 'note': note})
        P.db_put(enemies, foe)
    bandit(ENEMY_LACKEY, 'Bandit Lackey', 'Rogue', [220, 0, 32, 14, 10, 12, 20, 10], 18, 25, [(190, 5), (201, 3)],
           '<guard: 2>\n<weak: Ice>\n<desc1:Hired muscle for a crew that moves crates by night.>\n'
           '<desc2:Cold steel makes them think twice.>')
    bandit(ENEMY_LEADER, 'Bandit Leader', 'Swordsman', [480, 20, 38, 18, 12, 15, 22, 12], 50, 80,
           [(190, 5), (193, 3), (203, 2)],
           '<guard: 3>\n<weak: Fire>\n<desc1:Runs a smuggling crew out of Briarwood.>\n'
           '<desc2:Asks no questions about the cargo, and answers none.>')
    like = troops[39]                                           # three enemies: one at the back, two in front
    P.db_put(troops, {'id': TROOP_BANDITS, 'name': 'Chapter 1: Bandits (Briarwood)', 'pages': [P.troop_page([])],
                      'members': [dict(m, enemyId=e) for m, e in zip(like['members'], (ENEMY_LEADER, ENEMY_LACKEY, ENEMY_LACKEY))]})
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
# from Briarwood, Kael, Yuki and Tobin walk up the road from the bottom (y32) with the bandits one row behind them,
# to just below the gate guards; Greta waits by the road (stage 11 on) and meets Tobin there
GATE_ROAD, GATE_WALK = P.GATE_ROAD, 12
GATE_WALK_TO = GATE_ROAD[1] - GATE_WALK
GRETA_AT_GATE = (18, 17)


def gate_events(add, mp):
    def stay(line):
        return page(None, trigger=1, priority=0, commands=line + move(-1, UP))
    # stage <= 4: Mom's list; 6-7: Selene's ribbon; 10: Tobin (stages 5, 8 and 9 are cutscenes elsewhere)
    errands = [cmd(111, [1, V_CH1, 0, 4, 2], 0), *kael("Not yet. Mom's errand comes first.", i=1), cmd(0, [], 1),
               cmd(411, [], 0), cmd(111, [1, V_CH1, 0, 7, 2], 1), *kael('Not yet. I promised Selene her ribbon.', i=2),
               cmd(0, [], 2), cmd(411, [], 1), *kael('Not yet. We should go and see Tobin first.', i=2), cmd(0, [], 2),
               cmd(412, [], 1), cmd(0, [], 1), cmd(412, [], 0)]
    # open from 11 (after Tobin, to Briarwood) to 13, then shut again until Selene has her ribbon
    for e in mp['events']:
        if e and e['name'].startswith('To World Map'):
            base = e['pages'][0]
            e['pages'] = [base, dict(stay(errands), conditions=at(1)), dict(copy.deepcopy(base), conditions=at(11)),
                          dict(stay(kael("Not yet. Selene's still waiting for her ribbon.")), conditions=at(14)),
                          dict(copy.deepcopy(base), conditions=at(16))]       # said goodbye: the world is open
    greta = add('Greta', *GRETA_AT_GATE, staged(char(*GRETA, direction=2), 11, 14, commands=say(
        'Greta', 'Please, Kael. Bring him home.')))
    guard = next(e['id'] for e in mp['events'] if e and e['name'] == 'Gate Guard' and e['x'] > 20)
    road = GATE_ROAD
    tobin = add('Tobin', road[0] - 1, road[1], staged(char(*P.TOBIN_SPRITE, direction=8), 13, 14))
    yuki_ev = add('Yuki', road[0] + 1, road[1], staged(char(*YUKI_SPRITE, direction=8), 13, 14))
    crew = [add('Bandit %d' % (k + 1), road[0] - 1 + k, road[1] + 1, staged(char(*img, direction=8), 13, 14))
            for k, img in enumerate((BANDIT_A, BANDIT_LEADER, BANDIT_B))]
    up = lambda ev, w=False: move(ev, 37, *[UP] * GATE_WALK, 38, w=w, skip=True)
    add('Chapter 1: Home Through the Gate', 0, 0, director([
        *fade_out_slow(1), cmd(216, [1]), *wait(20), *fade_in_slow(60),
        *up(tobin), *up(yuki_ev), *[c for b in crew for c in up(b)], *up(-1, w=True),
        *move(guard, 37, LEFT, DOWN, DOWN, DOWN, DOWN, 38, T_LEFT, skip=True),
        *npc('Gate Guard', 'Ashveil? At this hour?', 'And who are... these?'),
        *move(-1, T_RIGHT),
        *kael('Bandits. We caught them in Briarwood.', "They've been running crates through this gate", "in Tobin's cart."),
        *npc('Gate Guard', "Tobin's cart?"),
        *npc('Tobin', "It's true. Every word.", 'I carried their cargo. And when I lost it,',
             'I picked pockets in the market to pay them back.'),
        *npc('Tobin', "I'll answer for it."),
        *balloon(greta, 1), *say('Greta', 'Tobin!'),
        *move(greta, 37, DOWN, DOWN, RIGHT, 38, T_DOWN, skip=True), *move(tobin, T_UP),
        *say('Greta', 'You fool...', "Why didn't you tell me?"),
        *npc('Tobin', "I'm sorry, Greta."),
        *npc('Gate Guard', 'Picking pockets is a matter for the magistrate.',
             'But a man who walks a bandit crew to the gate himself...', 'that will count for something.'),
        *kael("I'll speak to Sera too. She'll hear the whole story."),
        *npc('Gate Guard', 'Sir Seraphine? Ha. Then he\'s in good hands.'),
        *npc('Gate Guard', "And those crates in the clearing... we'll send", 'a patrol for them at first light.'),
        *fade_out_slow(40), *[c for b in crew for c in move(b, 39)], *wait(20), *fade_in_slow(40),
        *plain('The guards lead the bandits through the gate.'),
        *move(tobin, T_RIGHT),
        *npc('Tobin', 'Kael. Miss Yuki. Thank you.'),
        *npc('Tobin', "The next round at the Lion's Rest is on me...", '...once I can afford it.'),
        *kael("I'll hold you to that. Again."),
        *yuki('Make it two rounds.', name='Yuki'),
        *fade_out_slow(100), *var(V_CH1, 14), cmd(216, [0]), *plugin('Clock set 23:30'),
        *goto(K.CITY_GATE, road[0], GATE_WALK_TO, 8, fade=2), *wait(20), *fade_in_slow(60),
        *kael('...What a day.'),
        *yuki('Is it always like this in your country?', name='Yuki'),
        *kael('No. Usually it\'s quieter. I think.'),
        *kael("Come on. Selene's still waiting for her ribbon.", 'And you need somewhere to sleep tonight.'),
        *se('Book1'), *plain('\\C[3]Quest Updated\\C[0]', 'Take the \\C[6]Silk Ribbon\\C[0] home to Selene,',
                             'on \\C[6]Ember Lane\\C[0], in Lantern Row.')], 13, var=V_CH1),
        note='<minimap: hide>')


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
    mother = next(e for e in mp['events'] if e and e['name'] == 'Mother')
    # at breakfast (stage 15) she sits at the table as her own event; back in the kitchen after the goodbye (16)
    mother['pages'] += [dict(BLANK(), conditions=at(15)), dict(copy.deepcopy(mother['pages'][0]), conditions=at(16))]
    night_events(add, mother['id'])
    breakfast_events(add)


def walk_path(map_id, start, goal, avoid=()):
    """Route steps for the shortest walk over the floor from start to goal: the map's tiles only (the walkers go
    Through other characters, but keep off `avoid`, where someone sits), and never over the top of a wall, which
    the database marks passable."""
    import validate_maps as V
    m = json.load(open(L.DATA + 'Map%03d.json' % map_id, encoding='utf8'))
    flags, w = L.tileset_flags(m['tilesetId']), m['width']
    floor = lambda x, y: V.passable(m, x, y, flags) and not (L.A3 <= m['data'][y * w + x] < 8192)
    steps = {(0, -1): UP, (0, 1): DOWN, (-1, 0): LEFT, (1, 0): RIGHT}
    came, todo = {start: None}, [start]
    while todo and goal not in came:
        x, y = todo.pop(0)
        for (dx, dy) in steps:
            n = (x + dx, y + dy)
            if n not in came and n not in avoid and (n == goal or floor(*n)):
                came[n] = (x, y)
                todo.append(n)
    route, at_ = [], goal
    while came[at_] is not None:
        prev = came[at_]
        route.append(steps[(at_[0] - prev[0], at_[1] - prev[1])])
        at_ = prev
    return route[::-1]


# the kitchen table (3..5, 7..8): stools left (2,7) (2,8), right (6,7) (6,8), at the head (4,6)
SEAT_KAEL, SEAT_YUKI, SEAT_MOM, SEAT_SELENE = (6, 7), (2, 7), (4, 6), (2, 8)
DOORWAY, STAIRS_UP = (11, 13), (14, 3)
MOM_WAITS = (11, 10)                     # up late in the living room, by the door
KAEL_BED, KAEL_WAKES = (1, 4), (2, 4)    # Ashveil 3F: Kael's bed (1,3..4), and where he gets up
BREAKFAST = [((4, 7), 256 + 34), ((3, 8), 256 + 32), ((5, 8), 256 + 35)]     # Inside_C: side dishes, a meal, fruit
LETTER = ['Professor Wyndmere,', '',
          'I found more of them. A whole crate of black crystals',
          'in Briarwood, the same as the shard from the wolf.',
          'A crew of bandits was carrying them through the Main Gate',
          'for hooded clients who never give a name.', '',
          'I kept one. Tomorrow I leave the capital,',
          'to see the world, like you told me to.', '',
          '- Kaelen']


def night_events(add, mother):
    """Stage 14: home near midnight. Mom waited up; she feeds Yuki (stew, but not the stew of Hōrai), Yuki speaks of
    her brother, Kael asks her to come along, and he writes to Isolde. Ends in his room on 3F at 07:30 (stage 15)."""
    yuki_ev = add('Yuki', DOORWAY[0] + 1, DOORWAY[1], on_cue(char(*YUKI_SPRITE, direction=8), 14, 15))
    to_bed = lambda frm, speed: [THROUGH_ON, (SPEED, speed), *walk_path(K.ASHVEIL_1F, frm, STAIRS_UP, avoid=(SEAT_KAEL,)),
                                  (39,), THROUGH_OFF]
    add('Chapter 1: Home at Midnight', 0, 0, director([
        cmd(216, [1]), *P.place(mother, MOM_WAITS[0], MOM_WAITS[1], 2), *self_on(K.ASHVEIL_1F, yuki_ev), *wait(30),
        *mom('Kaelen Ashveil.'), *balloon(-1, 1),
        *move(mother, (SPEED, 4), DOWN, (SPEED, 3)), *move(-1, UP), *move(yuki_ev, UP),
        *mom('Do you have any idea what time it is?'),
        *kael('...Late?'),
        *mom('Selene waited for you all evening.', 'She went to bed an hour ago.'),
        *balloon(-1, 6), *kael("(The ribbon... It'll have to wait until morning.)"),
        *balloon(mother, 1), *mom('And who is this?'),
        *move(-1, T_RIGHT), *move(yuki_ev, T_UP),
        *yuki('Good evening. My name is Ryuzetsu Yuki.', "I've come from Hōrai. Forgive me for calling so late.", name='Yuki'),
        *move(-1, T_UP),
        *kael("She's only just arrived in the capital, Mom.", "She's got nowhere to stay tonight."),
        *mom('Then she stays here, of course.'),
        *mom('From Hōrai... You have come a long way, Yuki.', 'Have the two of you eaten?'),
        *balloon(-1, 8), *balloon(yuki_ev, 8),
        *mom('I thought not. Sit down, both of you.', 'The stew is still warm.'),
        *fade_out_slow(40),
        *goto(K.ASHVEIL_1F, SEAT_KAEL[0], SEAT_KAEL[1], 4, fade=2),
        *P.place(yuki_ev, SEAT_YUKI[0], SEAT_YUKI[1], 6), *P.place(mother, SEAT_MOM[0], SEAT_MOM[1], 2),
        *wait(20), *fade_in_slow(60),
        # Yuki's first Western meal (Story Bible, chapter 1 point 6): Hōrai has stew too, just not this one
        *plain('Two bowls of beef stew, still steaming,', 'and the last of the Golden Crust bread.'),
        *yuki('Stew... We have stew in Hōrai as well.', name='Yuki'),
        *mom('Oh? Is it like this one?'),
        *wait(40), *balloon(yuki_ev, 1),
        *yuki('...Not at all. Ours is lighter, with miso and fish.', 'This one is rich. Heavy, in a good way.', name='Yuki'),
        *balloon(mother, 3), *mom('Then have another bowl.'),
        *kael('Wait till you try her apple pie.'),
        *mom('There is no apple pie, Kaelen.', 'Not for boys who come home at midnight.'),
        *balloon(-1, 6), *kael('...Fair.'),
        *mom('The guest room on the second floor is ready for you, Yuki.', "Goodnight, you two. Don't stay up too late."),
        *move(mother, *to_bed(SEAT_MOM, 4), w=False),
        # Yuki's brother (Story Bible: Masa Lalu Yuki), told once the business with the bandits is done
        *wait(60),
        *kael('So, Yuki. You came a long way.', 'What are you looking for out here?'),
        *yuki('......', name='Yuki'), *wait(30),
        *yuki('My brother. Homura.', name='Yuki'),
        *yuki('Half a year ago he left Hōrai in the night.', 'They say he took a ship west.', name='Yuki'),
        *kael("Your brother? Then he'll be glad to see you,", 'after all this time.'),
        *yuki("...He won't be.", name='Yuki'),
        *yuki('When I find him, I will settle what he did.', "That is all I'll say about it tonight.", name='Yuki'),
        *kael('......'),
        *kael("I'm going to see the world anyway.", "If your brother's out there, our road will cross his",
              'sooner or later.'),
        *kael('Come with me.'),
        *balloon(yuki_ev, 1),
        *yuki("You'd travel with a woman who drew her sword", 'on you this morning?', name='Yuki'),
        *kael("You'd travel with the guy who beat you?"),
        *yuki('Beat me? The guards stopped that fight.', name='Yuki'),
        *balloon(-1, 5), *wait(30),
        *yuki('Goodnight, Kael. Thank you for the stew.', name='Yuki'),
        *kael('...Goodnight.'),
        *move(yuki_ev, *to_bed(SEAT_YUKI, 3), w=False),
        # a letter to Isolde: the second shard and the hooded clients
        *wait(90), *kael('(Before I sleep...)'),
        *se('Book2'), *plain('Kael finds a pen and a sheet of paper.'),
        *P.scroll(*LETTER),
        *kael("(I'll send it with the morning post.", "Wherever she is, it'll find her.)"),
        *fade_out_slow(100), *var(V_CH1, 15), *plugin('Clock set 07:30'), *wait(60),
        *goto(K.ASHVEIL_3F, KAEL_WAKES[0], KAEL_WAKES[1], 2, fade=2)], 14, var=V_CH1),
        note='<minimap: hide>')


def breakfast_events(add):
    """Stage 15, Ashveil 1F: Kael overslept, so Yuki already sits at breakfast with Mom and Selene (and has met her).
    The ribbon, Mom's teasing goodbye (Story Bible, chapter 1 point 6), Selene's souvenirs. The food goes at 16."""
    for k, ((x, y), tile) in enumerate(BREAKFAST):
        add('Breakfast %d' % (k + 1), x, y, staged({'tileId': tile, 'characterName': ''}, 15, 16, priority=0))
    mom_ev = add('Mother at Breakfast', SEAT_MOM[0], SEAT_MOM[1], staged(char(*MOM_FACE, direction=2), 15, 16))
    sis = add('Selene', SEAT_SELENE[0], SEAT_SELENE[1], staged(char(*SELENE, direction=6), 15, 16))
    yuki_ev = add('Yuki', SEAT_YUKI[0], SEAT_YUKI[1], staged(char(*YUKI_SPRITE, direction=6), 15, 16))
    add('Chapter 1: Breakfast', 0, 0, director([
        *wait(10),
        *balloon(sis, 1), *selene('Brother! You overslept!'),
        *mom('Good morning, sleepyhead.', 'Come and sit down. Breakfast is getting cold.'),
        *kael('Morning...'),
        *fade_out_slow(30), *goto(K.ASHVEIL_1F, SEAT_KAEL[0], SEAT_KAEL[1], 4, fade=2), *wait(10), *fade_in_slow(40),
        *selene("Yuki's been telling us everything.", 'The market, the prison, the bandits!'),
        *balloon(-1, 6), *kael('...Everything?'),
        *yuki('Most of it.', name='Yuki'),
        *selene('She says the guards had to stop your fight', 'because you were losing.'),
        *balloon(-1, 5), *kael("That's not what happened."),
        *yuki('Mm.', name='Yuki'),
        *selene('So? Brother?', 'Did you get it?'),
        *kael('One silk ribbon.', 'Midnight blue.'),
        cmd(126, [ITEM_RIBBON, 1, 0, 1]), *quest_cmd('complete selene_ribbon'),
        *se('Item3'), *plain('Kael gives Selene the \\C[6]Silk Ribbon\\C[0].'),
        *balloon(sis, 4), *selene("It's... it's actually midnight!", 'Not navy! Not sky blue!'),
        *selene('Thank you, Brother!'),
        *mom('So. You really are going today.'),
        *kael("Yeah. I promised I'd say goodbye properly."),
        *mom("Don't look so solemn about it.", "It's not as if you're leaving forever."),
        *mom("You'll be back the moment you run out of clean clothes.", 'I know you, Kaelen Ashveil.'),
        *balloon(-1, 6), *kael('...Probably.'),
        *selene('Then bring me something back!', 'From every town you visit!'),
        *kael('Every town?'),
        *selene('Every. Single. One.'),
        *kael('...Fine. Every town.'),
        *quest_cmd('start selene_souvenirs'), *se('Book1'),
        *plain('\\C[3]New Quest: Souvenirs for Selene\\C[0]', 'Bring Selene a souvenir from every town you visit.'),
        *mom('Yuki, dear. Look after him for me.'),
        *yuki('I will. Someone has to.', name='Yuki'),
        *balloon(-1, 6), *kael("Alright. Let's go, Yuki."),
        *fade_out_slow(60), *var(V_CH1, 16), cmd(216, [0]),
        *goto(K.ASHVEIL_1F, DOORWAY[0], DOORWAY[1] - 1, 2, fade=2), *wait(20), *fade_in_slow(60),
        *se('Book1'), *plain('\\C[3]Quest Updated\\C[0]', 'The Main Gate is open.',
                             'Set out into the world with Yuki.')], 15, var=V_CH1),
        note='<minimap: hide>')


def upstairs_events(add, mp):
    """Ashveil 2F: Selene is downstairs, waiting for her ribbon (she comes back up once it is handed over), and at
    breakfast on the morning of the goodbye."""
    staged_pages(mp, lambda e: e['name'] == 'Little Sister', 5, 11, lambda base: BLANK())
    sis = next(e for e in mp['events'] if e and e['name'] == 'Little Sister')
    sis['pages'] += [dict(BLANK(), conditions=at(15)), dict(copy.deepcopy(sis['pages'][0]), conditions=at(16))]


def kael_room_events(add, mp):
    """Ashveil 3F: Kael's bed (rest: full HP and MP, any time), and the morning he wakes up beside it (stage 15)."""
    rest = [cmd(101, ['', 0, 0, 2]), cmd(401, ['Your bed. Rest for a while?']),
            cmd(102, [['Rest', 'Not now'], 1, 0, 2, 0]),
            cmd(402, [0, 'Rest']), cmd(221, [], 1), *se('Recovery', i=1), cmd(314, [0, 0], 1), cmd(230, [60], 1),
            cmd(222, [], 1), *plain('Kael feels rested.', i=1), cmd(0, [], 1),
            cmd(402, [1, 'Not now']), cmd(0, [], 1), cmd(404, [])]
    add("Kael's Bed", KAEL_BED[0], KAEL_BED[1], [page(None, priority=1, commands=rest)])
    add('Chapter 1: Morning', 0, 0, director([
        cmd(216, [1]), *wait(30), *fade_in_slow(90), *wait(20),
        *move(-1, T_LEFT), *wait(20), *move(-1, T_DOWN),
        *kael("Alright. Today's the day.", 'Time to start the journey.'),
        *tutorial('Your \\C[6]bed\\C[0] at home lets you rest and fully recover', 'HP and MP, whenever you come back.')],
        15, var=V_CH1), note='<minimap: hide>')


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
        *tutorial('\\C[6]Yuki\\C[0] fights at your side now. Her \\C[6]Frost Iai\\C[0] strikes with \\C[6]Ice\\C[0],',
                  'and her sword arts hit hard: two of you means two kinds of weakness to aim for.',
                  'Check her \\C[6]Equip\\C[0] and \\C[6]Skills\\C[0] from the Menu.'),
        # Formation (NovaFormation): the party order decides the rows
        *tutorial('\\C[6]Formation\\C[0] (in the Menu) sets the party order, and the order sets the rows:',
                  'slots \\C[6]1-2\\C[0] stand in the \\C[6]front row\\C[0], slots \\C[6]3-4\\C[0] in the \\C[6]back row\\C[0].',
                  'Enemies aim at the front row more often.'),
        *tutorial('In the \\C[6]back row\\C[0], melee attacks deal 40% less damage, but physical hits taken',
                  'are 40% weaker too. Bows, crossbows, guns and whips lose nothing back there,',
                  "and a \\C[6]cane\\C[0] like Kael's staff attacks with \\C[6]magic\\C[0] instead."),
        *tutorial('With only the two of you, both stand in the front row for now.',
                  'In battle, the \\C[6]Row\\C[0] command swaps rows with an ally until the fight ends.',
                  'Each card in the Menu shows its row next to the level.'),
        *se('Book1'), *plain('\\C[3]New Quest\\C[0]', 'Take Yuki to \\C[6]Tobin\'s house\\C[0]',
                             'and find out what really happened in the market.')], 9, var=V_CH1),
        note='<minimap: hide>')


# ====================================================================== Lantern Row: Tobin's house, on Ember Lane
# the locked House at (28,43), a few doors east of the Ashveil house. Kael knocks from the doorstep; for the scene he
# stands one step back (28,45) with Yuki beside him, and Greta comes out onto the step (28,44).
TOBIN_DOOR, DOORSTEP, YUKI_STEP = (28, 43), (28, 45), (29, 45)
DOOR_OPEN = [DIR_FIX_OFF, T_DOWN, (L.R_WAIT, 3), T_LEFT, (L.R_WAIT, 3), T_RIGHT, (L.R_WAIT, 3), T_UP]
DOOR_SHUT = [T_RIGHT, (L.R_WAIT, 3), T_LEFT, (L.R_WAIT, 3), T_DOWN]


def greta(*lines): return say('Greta', *lines)


def lantern_row_events(add, mp):
    door = next(e for e in mp['events'] if e and e['name'] == 'House' and (e['x'], e['y']) == TOBIN_DOOR)
    wife = add('Greta', TOBIN_DOOR[0], TOBIN_DOOR[1], on_cue(char(*GRETA, direction=2), 10, 11))
    yuki_ev = add('Yuki', YUKI_STEP[0], YUKI_STEP[1], on_cue(char(*YUKI_SPRITE, direction=8), 10, 11))

    def visit(base):
        return dict(copy.deepcopy(base), list=[
            *fade_out_slow(30), cmd(216, [1]), *goto(K.RESIDENTIAL, DOORSTEP[0], DOORSTEP[1], 8, fade=2),
            *self_on(K.RESIDENTIAL, yuki_ev), *wait(10), *fade_in_slow(40),
            *se('Knock'), *wait(40), *kael("Tobin? It's Kael."), *wait(30),
            *se('Open1'), *move(0, *DOOR_OPEN), *self_on(K.RESIDENTIAL, wife), *wait(5),
            *move(wife, THROUGH_ON, DOWN, THROUGH_OFF),
            *greta('Kael? At this hour?'),
            *kael("Evening, Greta. Sorry it's so late.", 'Is Tobin home?'),
            *greta('You just missed him. He went out a little while ago.'),
            *greta('I watched him from the window...', 'There were men waiting for him at the end of the lane.',
                   "Men I've never seen before."),
            *balloon(-1, 1), *kael('Strangers?', 'Where did he go with them?'),
            *greta("I don't know. He never tells me anymore."),
            *greta("These past months he's been going out at night,", 'again and again. And when he comes home,',
                   "he won't say a word about it."),
            *move(yuki_ev, T_LEFT), *yuki("...Doesn't that sound suspicious to you?", name='Yuki'),
            *kael('......'),
            *wait(30), *balloon(-1, 8),
            *kael('(Five months ago... Tobin never made it home', 'from Briarwood that night.)'),
            *kael('(I never asked him what he was doing', 'on the forest road after dark.)'),
            *move(-1, T_UP), *kael('Greta. I think I know where he went.'),
            *greta('You do?'),
            *kael("Briarwood. I'll bring him home.", 'I did it once already, didn\'t I?'),
            *greta('...Then I\'ll wait at the Main Gate.', 'Just like last time.'),
            *greta('Wait. Take these.', 'Tobin always kept a few for the road.'),
            *se('Item3'), *item(1, 3), *plain('Received 3 \\C[6]Potion\\C[0]!'),
            *kael('Thank you, Greta.'),
            *move(wife, THROUGH_ON, UP, 39, THROUGH_OFF), *se('Close1'), *move(0, *DOOR_SHUT),
            *move(-1, T_RIGHT),
            *yuki('Briarwood?', name='Yuki'),
            *kael('A forest west of the capital.', 'The old cart road runs right through it.'),
            *yuki('And the gate will let us out at night?', name='Yuki'),
            *kael('For a Class 3 mage? It will.'),
            *fade_out_slow(40), *move(yuki_ev, 39), cmd(216, [0]), *var(V_CH1, 11), *plugin('Clock set 21:00'),
            *goto(K.RESIDENTIAL, DOORSTEP[0], DOORSTEP[1] - 1, 2, fade=2), *wait(10), *fade_in_slow(40),
            *se('Book1'), *plain('\\C[3]Quest Updated\\C[0]', 'Go to \\C[6]Briarwood\\C[0] and find Tobin.',
                                 'Leave the capital by the \\C[6]Main Gate\\C[0]: the forest lies',
                                 'just west of the capital on the World Map.')])
    staged_pages(mp, lambda e: e is door, 10, 11, visit)


# ====================================================================== Briarwood: Tobin and the bandits, at night
# the prologue's clearing (prologue.py): the crew sits round a fire where Tobin's cart was wrecked. Kael and Yuki come
# up the road to the clearing's south edge; the bandit who grabs Kael ends up knocked out at (14,11).
FIRE, LEADER_AT, TOBIN_AT = (15, 8), (15, 7), (15, 10)
LACKEY_A, LACKEY_B, LACKEY_C = (13, 9), (17, 10), (18, 8)           # A (Evil 0) grabs Kael; B (Evil 4) and C (Evil 0)
WOOD_ROW = 19                                                       # stepping on this row (stage 11) starts the scene
WOOD_IN, WOOD_STOP = (15, 17), 13                                   # Kael walks up from (15,17) to (15,13)
CRATE_STEP = (19, 7)                                                # below the crate at (19,6)


def knocked_out(ev, img, w=False):
    return move(ev, T_DOWN, (41, img[0], img[1]), 35, 32, w=w)       # collapsed sprite, direction fixed, no walking


def briarwood_events(add, mp):
    add('Campfire', FIRE[0], FIRE[1], staged(char('!Flame', 2), 11, 13, step_anim=True, walk_anim=False),
        note='<light: 4, #ffa040>\n<minimap: hide>')
    hidden = '<minimap: hide>'
    leader = add('Bandit Leader', LEADER_AT[0], LEADER_AT[1], staged(char(*BANDIT_LEADER, direction=2), 11, 13), note=hidden)
    a = add('Bandit', LACKEY_A[0], LACKEY_A[1], staged(char(*BANDIT_A, direction=6), 11, 13), note=hidden)
    b = add('Bandit', LACKEY_B[0], LACKEY_B[1], staged(char(*BANDIT_B, direction=4), 11, 13), note=hidden)
    c = add('Bandit', LACKEY_C[0], LACKEY_C[1], staged(char(*BANDIT_A, direction=4), 11, 13), note=hidden)
    tobin = add('Tobin', TOBIN_AT[0], TOBIN_AT[1], staged(char(*P.TOBIN_SPRITE, direction=8), 11, 13))
    yuki_ev = add('Yuki', WOOD_IN[0], WOOD_IN[1] + 1, on_cue(char(*YUKI_SPRITE, direction=8), 11, 13), note=hidden)
    for x in range(13, 17):                                         # the open road on row 19 (x13..16)
        add('Chapter 1: Briarwood Road %d' % x, x, WOOD_ROW,
            [BLANK(), page(None, trigger=1, priority=0, cond=cond(11, var=V_CH1), commands=var(V_CH1, 12)),
             BLANK(**cond(12, var=V_CH1))])
    walk = WOOD_IN[1] - WOOD_STOP
    gang = (leader, b, c)
    add('Chapter 1: The Bandits', 0, 0, director([
        *fade_out_slow(30), cmd(216, [1]), *goto(P.BRIARWOOD, WOOD_IN[0], WOOD_IN[1], 8, fade=2),
        *self_on(P.BRIARWOOD, yuki_ev), *wait(10), *fade_in_slow(60),
        *npc('Bandit Leader', "Short again, Tobin. That's the third time this month."),
        *npc('Tobin', "I-I'll get the rest. I just need a few more days—"),
        *move(-1, *[UP] * walk, w=False), *move(yuki_ev, THROUGH_ON, *[UP] * walk, RIGHT, UP, THROUGH_OFF, T_UP),
        *kael('Tobin!'),
        *balloon(tobin, 1), *move(tobin, T_DOWN),
        *npc('Tobin', 'Kael? Wh-what are you doing here?'),
        *kael('I could ask you the same thing.', 'What are you doing with these people?'),
        *[x for g in gang + (a,) for x in balloon(g, 1, w=False)], *wait(30),
        *npc('Bandit Leader', 'Tobin, what is this?', 'You led them straight to us?'),
        *move(tobin, T_UP),
        *npc('Tobin', "No! I swear, I don't know why they're here!"),
        *yuki('Your friend seems quite at home with these men.', name='Yuki'),
        *kael('......'),
        *move(c, T_DOWN), *npc('Bandit', 'Hey, kid. Ever heard the saying?', 'Curiosity killed the cat.'),
        *move(tobin, T_DOWN),
        *npc('Tobin', "Wait! Don't hurt them!"), *npc('Tobin', "...At least don't hurt the boy."),
        *balloon(yuki_ev, 6), *yuki('Ouch.', name='Yuki'),
        *npc('Bandit Leader', "Relax, Tobin. We'll only put them to sleep for a while."),
        *move(a, THROUGH_ON, DOWN, DOWN, DOWN, RIGHT, RIGHT, THROUGH_OFF, T_DOWN),
        *npc('Bandit', 'Come quietly now—'),
        *se('Fire2', 90), *anim(a, ANIM_FIRE, w=False), *shake(5, 8, 15), *wait(20),
        *move(a, THROUGH_ON, (14, -1, -1), THROUGH_OFF), *se('Blow3', 90), *knocked_out(a, DOWN_A, w=True),
        *[x for g in gang for x in balloon(g, 1, w=False)], *balloon(tobin, 1),
        *npc('Bandit Leader', 'Why, you little—!'),
        *move(-1, T_RIGHT), *move(yuki_ev, T_LEFT),
        *kael("Yuki, sorry. You don't have to get mixed up in this.", 'Go.'),
        *yuki("Heh. Not a chance. Don't keep all the fun to yourself.",
              'Besides, I have unfinished business with your friend.', name='Yuki'),
        *kael('Suit yourself, then.'),
        *move(-1, T_UP), *move(yuki_ev, T_UP), *move(tobin, THROUGH_ON, LEFT, THROUGH_OFF, T_RIGHT),
        *npc('Bandit Leader', 'Get them!'),
        cmd(301, [0, TROOP_BANDITS, False, False]),
        *script('$gameScreen.startFadeOut(30);'), *wait(30),
        *knocked_out(b, DOWN_B), *knocked_out(c, DOWN_A), *knocked_out(leader, DOWN_LEADER),
        *move(tobin, THROUGH_ON, RIGHT, THROUGH_OFF, T_DOWN), *wait(20), *fade_in_slow(60),
        # Tobin's confession
        *move(-1, UP, UP), *kael('Tobin!'),
        *npc('Tobin', "I'm sorry, Kael..."),
        *npc('Tobin', 'That night in Briarwood, five months ago...', "I wasn't hauling grain."),
        *npc('Tobin', 'It was their cargo. They paid me to bring it', "through the gate. Nobody checks an old carter's cart."),
        *npc('Tobin', 'Then that wolf came out of the dark.', 'The cart, the crates, all of it... gone.'),
        *npc('Tobin', 'And they wanted every coin of it back.', 'With interest.'),
        *kael('So the market...'),
        *npc('Tobin', '...Yes. The young lady was right.'),
        *kael("Why didn't you tell me? I'd have helped you."),
        *npc('Tobin', "You'd just saved my life, lad.", "How could I tell you I'd lied to you the same day?"),
        *kael('......'),
        # Sera's condition, the other way round
        *move(yuki_ev, UP, UP, UP, T_LEFT), *move(tobin, T_RIGHT),
        *yuki('I was told I have to apologize to you.', name='Yuki'),
        *yuki('...But I think it should be the other way around.', name='Yuki'),
        *balloon(tobin, 6), *npc('Tobin', "...I'm sorry I got you thrown in prison, miss."),
        *yuki('Accepted.', name='Yuki'),
        # the crates: the hook to the main story
        *move(yuki_ev, T_UP),
        *yuki("What's in those crates, anyway?", 'They were guarding them like treasure.', name='Yuki'),
        *move(-1, THROUGH_ON, *[RIGHT] * (CRATE_STEP[0] - TOBIN_AT[0]), *[UP] * (TOBIN_AT[1] + 1 - CRATE_STEP[1]),
              THROUGH_OFF, T_UP),
        *se('Open2'), *plain('Kael pries the lid off one of the crates.'),
        *se('Darkness1', 70), *flash([120, 60, 200, 120], 20),
        *plain('Packed in straw: black crystals, cold to the touch.'),
        *balloon(-1, 1), *kael('These are...'),
        *kael("(The same as the shard from the wolf.", "The mana's flowing the wrong way.)"),
        *move(-1, T_LEFT),
        *kael('Where did you get these?'),
        *npc('Bandit Leader', "Ugh... Don't look at me.", 'We just move the crates.'),
        *npc('Bandit Leader', "The client pays well and doesn't give names."),
        *kael('What client?'),
        *npc('Bandit Leader', 'Hooded types. Never once saw their faces.', "Ask all you want, kid. That's all I know."),
        *yuki('Kael. Do you know what those are?', name='Yuki'),
        *kael('...I\'ve seen one before. Right here,', 'five months ago.'),
        # Kael keeps one: two shards now, the wolf's and one from the crates (Isolde will want to see it)
        *move(-1, T_UP), *se('Item3'), *item(P.ITEM_SHARD),
        *plain('Kael wraps one of the crystals in a cloth', 'and slips it into his pocket.',
               'Got another \\C[6]Tainted Shard\\C[0]! (2 in total)'),
        *move(-1, T_LEFT),
        *yuki("You're keeping one?", name='Yuki'),
        *kael('Someone I know will want to see it.', "And I'd rather it didn't go missing on the way to the gate."),
        *kael("Come on. Let's take these three to the gate.", 'The guard can deal with them. And with the crates.'),
        *npc('Tobin', "I'm coming too.", "It's time I told the guard everything."),
        *kael('...Alright.'),
        *fade_out_slow(100), *var(V_CH1, 13), *plugin('Clock set 23:00'),
        *goto(K.CITY_GATE, GATE_ROAD[0], GATE_ROAD[1], 8, fade=2)], 12, var=V_CH1),
        note='<minimap: hide>')


# ====================================================================== playtest: Scene Select
def scenes():
    base = ['v1=10', 'item=%d' % P.ITEM_SHARD]
    goods = ['item=%dx%d' % (i, n) for i, n in LIST]
    party = ['level=3', 'join=%d' % ACTOR_YUKI, 'item=%d' % ITEM_RIBBON, 'cmd=Quest start selene_ribbon',
             'cmd=Quest step selene_ribbon 2']
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
         base + ['v3=9', 'item=%d' % ITEM_RIBBON, 'cmd=Quest step selene_ribbon 2', 'cmd=Clock set 20:30']),
        ("Chapter 1: Tobin's door (Greta)", (K.RESIDENTIAL, TOBIN_DOOR[0], TOBIN_DOOR[1] + 1, 8),
         base + ['v3=10'] + party + ['cmd=Clock set 20:50']),
        ('Chapter 1: Briarwood - Entrance, after Tobin', (P.ENTRANCE, P.ENTRANCE_START[0], P.ENTRANCE_START[1], 8),
         base + ['v3=11'] + party + ['cmd=Clock set 21:20']),
        ('Chapter 1: Briarwood road, after Tobin', (P.BRIARWOOD, WOOD_IN[0], WOOD_ROW + 2, 8),
         base + ['v3=11'] + party + ['item=1x3', 'cmd=Clock set 21:30']),
        ('Chapter 1: home at midnight (Yuki, the letter)', (K.ASHVEIL_1F, DOORWAY[0], DOORWAY[1], 8),
         base + ['v3=14', 'item=%d' % P.ITEM_SHARD] + party + ['cmd=Clock set 23:45']),
        ('Chapter 1: the morning goodbye (wake up on 3F)', (K.ASHVEIL_3F, KAEL_WAKES[0], KAEL_WAKES[1], 2),
         base + ['v3=15', 'item=%d' % P.ITEM_SHARD] + party + ['cmd=Clock set 07:30'])]


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
             "her to Tobin's house. With nowhere else to go, Yuki joins him."),
        step(11, 'Briarwood', 'Find Tobin in Briarwood, west of the capital (Main Gate, then the World Map).',
             "At Tobin's door on Ember Lane, his wife Greta says he went out just before they came, with strangers "
             'waiting for him at the end of the lane. For months he has been going out at night. Kael remembers the '
             'night his cart never came home from Briarwood, and wonders why he never asked.'),
        step(12, 'Briarwood', '',
             'In the clearing where the cart was wrecked, Tobin stands at a campfire with a crew of bandits, short of '
             'money again. When one of them tries to put Kael to sleep, Kael knocks him out, and Yuki refuses to walk '
             'away from the fight.'),
        step(13, 'Main Gate', '',
             'Five months ago Tobin was carrying their crates through the gate when the wolf wrecked his cart, and he '
             'has been paying for the lost cargo ever since, by picking pockets. Yuki was right, and Tobin apologizes '
             'to her. In the crates: black crystals, as cold as the shard from the wolf; Kael keeps one. The bandits only move them, '
             'for hooded clients who give no names.'),
        step(14, 'Ember Lane, Lantern Row', 'Take the Silk Ribbon home to Selene.',
             'At the Main Gate Tobin hands himself and the bandits to the guard, and Greta is waiting for him. It is '
             'almost midnight, and Selene is still waiting for her ribbon.'),
        step(15, 'Ashveil Residence', 'Go down to breakfast.',
             'Mom waited up, and Selene went to bed. Mom sits Yuki down to a bowl of Western stew, nothing like the '
             'stew of Hōrai, and over the table Yuki speaks of her brother Homura, who fled Hōrai and came west; when '
             'she finds him, she will settle what he did. Kael asks her to come with him. Before he sleeps, he writes '
             'to Professor Wyndmere about the crystals.'),
        step(16, 'Ember Lane, Lantern Row', 'Set out into the world from the Main Gate.',
             'Kael oversleeps: by the time he comes down, Yuki is at breakfast with Mom and Selene. Selene gets her '
             'ribbon, midnight blue, and makes her brother promise a souvenir from every town he visits. Mom only '
             'laughs at the goodbye: he will be back the moment he runs out of clean clothes.')], var=V_CH1)


def sub_quests():
    """Selene's errand: started by her (Ashveil 1F), step 2 once the ribbon is bought. Handing it over comes later."""
    from quests import quest, step
    return [quest('selene_ribbon', 'sub', 'A Ribbon for Selene', [
        step(1, 'Market District', "Buy the Silk Ribbon at the Tailor's stall.",
             "Selene wants the midnight-blue silk ribbon from the Tailor's stall, and she paid the %d Z herself. "
             'Not navy. Not sky blue. Midnight.' % RIBBON_PRICE),
        step(2, 'Ember Lane, Lantern Row', 'Bring the ribbon home to Selene.',
             'The ribbon is bought. Now it only has to make it home.'),
        step(3, '', '', 'Delivered the next morning, a little late. Selene says it is exactly the right blue.')], done=3),
        # opened at the goodbye (stage 15); the souvenirs themselves come with the towns
        quest('selene_souvenirs', 'sub', 'Souvenirs for Selene', [
            step(1, 'Every town', 'Bring Selene a souvenir from every town you visit.',
                 'Selene made her brother promise: a souvenir from every town he visits. Every. Single. One.')])]


if __name__ == '__main__':
    if '--save' in sys.argv:
        build_database()
        for mid, fn in ((P.GUILD, guild_events), (K.HARBOR, harbor_events), (K.BAKERS_LANE, bakers_lane_events),
                        (K.CITY_GATE, gate_events), (K.ASHVEIL_1F, home_events), (K.ASHVEIL_2F, upstairs_events), (K.ASHVEIL_3F, kael_room_events),
                        (K.MARKET, market_events), (K.PRISON_CELLS, prison_events), (K.CASTLE_APPROACH, castle_events),
                        (K.RESIDENTIAL, lantern_row_events), (P.BRIARWOOD, briarwood_events)):
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
