# Chapter 1 - The Adventure Begins (Story/Chapter1_Scenario.md): the story events after the prologue.
#   python chapter1.py --save           -> write everything (RPG Maker MV must be closed; run prologue.py first)
#
# Story variable 3 "Chapter 1" (the prologue's last scene sets it to 1):
#   1 Class 3 license, free in the Guild     2 leaving the Guild: Yuki lands at the harbor
#   3 back to Kael in Baker's Lane           4 Mom's errand: 2 Honey Bread + 3 Sweet Buns from the market
#   5 errand done (brought home)
# Kael can't leave the capital (Main Gate -> World Map) before the errand is done.
# --save is safe to run again: it replaces its own events (note '<chapter1>') and rebuilds the pages it adds.
import sys, json, copy
import nova_maplib as L
from nova_maplib import page, cmd, say, char
import kingdom as K
import prologue as P
from prologue import (kael, npc, plain, tutorial, var, se, gold, item, balloon, wait, fadein, fadeout, transparent, goto, plugin,
                      move, director, cond, BLANK, UP, DOWN, LEFT, RIGHT, T_UP, T_DOWN, T_LEFT, T_RIGHT)

V_CH1 = P.V_CHAPTER1
TAG = '<chapter1>'
YUKI_SPRITE, YUKI_FACE = ('Actor4', 1), ('Actor4', 1)
MOM_FACE = ('family1', 3)
ITEM_BUN, ITEM_HONEY_BREAD = 49, 50
LIST = ((ITEM_HONEY_BREAD, 2), (ITEM_BUN, 3))   # Mom's list: 2 x 150 + 3 x 40 = 420 Z
ERRAND_GOLD = 450

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


# ====================================================================== Main Gate: not before the errand
def gate_events(add, mp):
    stay = lambda base: page(None, trigger=1, priority=0, commands=kael("Not yet. Mom's errand comes first.") + move(-1, UP))
    staged_pages(mp, lambda e: e['name'].startswith('To World Map'), 1, 5, stay)


# ====================================================================== Ashveil Residence: home to Mom
def home_events(add, mp):
    has_all = ' && '.join('$gameParty.numItems($dataItems[%d]) >= %d' % (i, n) for i, n in LIST)

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
                *var(V_CH1, 5),
                *plain('\\C[3]Errand complete.\\C[0]', 'Kael is free to leave the capital.')]],
            cmd(0, [], 1), cmd(411, [], 0),
            *[dict(c, indent=c['indent'] + 1) for c in
              mom('Did you get everything on my list?', 'Two Honey Bread and three Sweet Buns.',
                  "The Baker's Stall in the market has them.")],
            cmd(0, [], 1), cmd(412, [], 0)])
    staged_pages(mp, lambda e: e['name'] == 'Mother', 4, 5, errand)


# ====================================================================== playtest: Scene Select
def scenes():
    base = ['v1=10', 'item=%d' % P.ITEM_SHARD]
    goods = ['item=%dx%d' % (i, n) for i, n in LIST]
    return [
        ('Chapter 1: the Guild, after the license', (P.GUILD, 26, 7, 8), base + ['v3=1', 'cmd=Clock set 09:10']),
        ('Chapter 1: Yuki arrives at the harbor', (K.HARBOR, HARBOR_VIEW[0], HARBOR_VIEW[1], 2), base + ['v3=2', 'cmd=Clock set 09:15']),
        ("Chapter 1: Mom's list", (K.BAKERS_LANE, TAVERN_STEP[0], TAVERN_STEP[1], 2), base + ['v3=3', 'cmd=Clock set 09:20']),
        ('Chapter 1: home to Mom with the shopping', (K.ASHVEIL_1F, MOM_SPOT[0], MOM_SPOT[1], 8),
         base + ['v3=4'] + goods + ['cmd=Clock set 10:30'])]


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
        step(5, 'Ember Lane, Lantern Row', 'Explore the capital, or set out from the Main Gate.',
             'Mom gets her bread, and Kael promises to say goodbye properly before he leaves.')], var=V_CH1)


if __name__ == '__main__':
    if '--save' in sys.argv:
        build_database()
        for mid, fn in ((P.GUILD, guild_events), (K.HARBOR, harbor_events), (K.BAKERS_LANE, bakers_lane_events),
                        (K.CITY_GATE, gate_events), (K.ASHVEIL_1F, home_events)):
            L.write_map(mid, P.patch_events(mid, fn, tag=TAG))
        import scene_select
        scene_select.register_plugin('NovaChapterCard', 'Chapter title cards: an animated title in the middle of the '
                                     'screen on black ("Prologue Ends", "Chapter 1 / The Adventure Begins").',
                                     {'Duration': '300', 'Head Color': '#e8cf8a'})
        scene_select.register()
        import quests; quests.register()
        print('chapter 1 saved')
