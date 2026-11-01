# The quest log (NovaQuests): every story script's quests, written to data/Quests.json. A main story chapter follows
# its story variable, so each step's 'at' is a stage of that variable; a sub quest without 'var' keeps its step in the
# save (plugin commands "Quest start/step/complete <id>"). prologue.py and chapter1.py call register() after --save.
#   python quests.py          -> rewrite data/Quests.json only (safe while RPG Maker MV is open)
import json
import nova_maplib as L

SUB_QUESTS = []     # sub quests: quest('id', 'sub', 'Title', [step(...), ...], done=n)


def step(at, where, goal, text):
    """One step: reached when the quest's step is at least `at`. `text` joins the summary, `goal` becomes the current
    objective and `where` the location under the title (both stay from the last step that has one)."""
    return {'at': at, 'where': where, 'goal': goal, 'text': text}


def quest(qid, kind, title, steps, var=None, done=None):
    q = {'id': qid, 'type': kind, 'title': title, 'steps': steps}
    if var: q['var'] = var
    if done is not None: q['done'] = done
    return q


def register():
    import prologue, chapter1
    import scene_select
    rows = [prologue.quest(), chapter1.quest()] + SUB_QUESTS
    with open(L.DATA + 'Quests.json', 'w', encoding='utf8', newline='') as f:
        json.dump(rows, f, ensure_ascii=False, indent=1)
    scene_select.register_plugin('NovaQuests', 'Quest log in the main menu: the main story chapters and sub quests, '
                                 'each with its current objective and a summary that grows as the story moves on.',
                                 {'Menu Command': 'Quests', 'Data File': 'Quests.json'})


if __name__ == '__main__':
    register()
    print('quests written')
