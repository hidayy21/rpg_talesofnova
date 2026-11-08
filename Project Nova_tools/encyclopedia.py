# The Encyclopedia's characters (NovaEncyclopedia): everyone Kael meets, written to data/Characters.json.
# A character opens once its 'unlock' is reached (a story variable at a stage); None = only the plugin command
# "Encyclopedia meet <id>" opens it (people not met in the game yet). A paragraph with its own 'unlock' joins later.
# The texts are what Kael knows: no spoilers from the Story Bible. face None = no face sheet yet (Ignatius, Valeria).
#   python encyclopedia.py          -> rewrite data/Characters.json (safe while RPG Maker MV is open)
import json
import nova_maplib as L

V_PROLOGUE, V_CH1 = 1, 3
GRETA_FACE = None                  # no face sheet yet (sprite People4 7)


def at(var, stage): return {'var': var, 'at': stage}
ALWAYS = {'always': True}


def char(cid, name, group, title, face, unlock, facts, *text, picture=None):
    """text: paragraphs, either a string or (string, unlock) for one revealed later."""
    paras = [{'text': t} if isinstance(t, str) else {'text': t[0], 'unlock': t[1]} for t in text]
    c = {'id': cid, 'name': name, 'group': group, 'title': title, 'face': list(face) if face else None, 'unlock': unlock,
         'facts': [list(f) for f in facts], 'text': paras}
    if picture: c['picture'] = picture
    return c


CHARACTERS = [
    # ---------------------------------------------------------------- the party
    char('kael', 'Kaelen Ashveil', 'Party', 'Class 3 Mage', ('Actor4', 0), ALWAYS,
         [('Age', '19'), ('From', 'Nova, the Royal Capital'), ('Magic', 'Shadow and Fire')],
         'Kael to everyone who knows him. One of the best graduates of his year at the Royal Magic Academy of Nova, '
         'and a licensed mage ever since. His dream is simple: to become the number one mage in the world.',
         'Most mages need two years to climb a class. Kael set himself one, and made it: Class 3, five months after '
         'his teacher told him to go and see the world.',
         'The third of the four Ashveil children. Like all of them he carries two bloodlines, Shadow from his '
         "father's side and Fire from his mother's, and he chose to make Shadow his own.",
         picture='Full_Kael'),
    char('yuki', 'Ryuzetsu Yuki', 'Party', 'Ronin of Hōrai', ('Actor4', 1), at(V_CH1, 8),
         [('Age', '19'), ('From', 'Hōrai, on the Eastern Continent'), ('Weapon', 'Katana')],
         'A swordswoman who crossed the sea on the Morning Gull, six weeks from home. She says she is looking for '
         'someone, and not much more than that.',
         'Kael met her the hard way: her sword drawn on Tobin in the middle of the market, sure she had seen him '
         'picking pockets. It ended in a duel, the city guard, and one shared prison cell.',
         ("Out of the cell and with nowhere else to go, she agreed to come with Kael and see the truth about Tobin "
          'for herself. Laid back, quick with her blade and quicker with a dry remark.', at(V_CH1, 10)),
         picture='Full_Yuki'),
    char('mira', 'Mirabelle Moonvale', 'Party', 'Apprentice of Stars', ('Actor4', 6), None,
         [('Age', '18'), ('Family', 'House Moonvale')],
         'A cheerful prodigy of the Royal Academy, born to House Moonvale, a forgotten and sidelined family of mages.',
         picture='Full_Mira'),
    char('roland', 'Roland Talonheart', 'Party', 'The Lion', ('Actor4', 4), None,
         [('Age', '32'), ('Rank', 'Knight Commander')],
         'A loyal knight commander sworn to protect the Royal Kingdom of Nova. He stands firm where others would '
         'fall.', picture='Full_Roland'),
    char('ley', 'Leyfric Carlson', 'Party', 'Phantom Soldier', ('Actor4', 3), None,
         [('Age', '21'), ('Rank', 'Foot Soldier'), ('Weapon', 'Spear')],
         'Ley to the few who remember his name. An ordinary foot soldier, and has been since he was seventeen, when a '
         'friend talked him into joining. Quiet, plain, easy to forget: people often notice him only once he speaks.',
         'He likes to joke, but his voice is so soft that nobody hears it. Then someone else tells the same joke, '
         'louder, and gets the laugh.',
         'When the village he was posted to was attacked, the captain fell and the line broke. One foot soldier did '
         'not: Ley held his ground against an enemy general, and was the only one of them still breathing.',
         picture='Full_Ley'),

    # ---------------------------------------------------------------- the Ashveil family
    char('vivienne', 'Vivienne Ashveil', 'Ashveil Family', 'Mother', ('family1', 3), at(V_CH1, 3),
         [('Age', '48'), ('Home', 'Ember Lane, Lantern Row'), ('Born', 'House Dracoheart')],
         "Kael's mother, and the one who keeps the Ashveil house running while its people come and go. She writes "
         'shopping lists, counts the buns, and knows exactly which shop her son will slip into on the way home.',
         'Born a Dracoheart, one of the great magical families of Nova. She left the clan to marry Cassius Ashveil.'),
    char('seraphine', 'Seraphine Ashveil', 'Ashveil Family', 'Knight Commander', ('family1', 1), at(V_CH1, 8),
         [('Age', '25'), ('Rank', 'Commander of the Royal Army'), ('Magic', 'Fire, with a sword')],
         "Sera to her family. Kael's older sister and the second Ashveil child, a knight of the Royal Kingdom. She "
         'became a commander at twenty-three, one of the youngest ever.',
         "Strict, and at her strictest with her little brother. Still, when Kael landed in a cell, it was Sera's word "
         "that got him out, and on Kael's word, Yuki too."),
    char('selene', 'Selene Ashveil', 'Ashveil Family', 'Little Sister', ('family1', 0), at(V_CH1, 5),
         [('Age', '15'), ('Family', 'Youngest of the four'), ('Magic', 'Shadow, like Kael')],
         'The youngest Ashveil, black-haired like Kael and, like him, drawn to Shadow. She has her brother wrapped '
         'around her finger, and she knows it.',
         'Wants a souvenir from every town Kael visits. Wanted a midnight-blue silk ribbon first. Not navy. Midnight.'),
    char('kaine', 'Kaine Ashveil', 'Ashveil Family', 'Eldest Brother', ('family1', 2), None,
         [('Age', '27'), ('Magic', 'Fire')],
         'The eldest of the Ashveil children, red-haired and Fire to the bone. He chose the open sea over the court, '
         'and is rarely home.'),
    char('cassius', 'Cassius Ashveil', 'Ashveil Family', 'Father', ('family1', 4), None,
         [('Age', '51'), ('Serves', 'The Royal Kingdom of Nova')],
         "Kael's father, one of the strongest men in the kingdom. He works for the crown, often far from home and "
         'often alone. Even his children do not know the details.'),

    # ---------------------------------------------------------------- House Dracoheart
    char('ignatius', 'Ignatius Dracoheart', 'House Dracoheart', 'Ignatius the Hero', None, None,
         [('Age', '69'), ('Rank', 'Head of House Dracoheart')],
         "Kael's grandfather on his mother's side. Once called the Sword of Nova, now the Hero, for his part in "
         "Nova's victory over the Arulustus Empire sixteen years ago."),
    char('valeria', 'Valeria Dracoheart', 'House Dracoheart', 'The Fire Empress', None, None,
         [('Age', '44'), ('Rank', 'Royal Mage')],
         "Kael's aunt, his mother's younger sister, and a Royal Mage of the Royal Magic Council. She once taught Fire "
         'to Kaine, Sera and Kael.'),

    # ---------------------------------------------------------------- the capital
    char('isolde', 'Isolde Wyndmere', 'Royal Capital of Nova', "Kael's Teacher", ('family1', 5), at(V_PROLOGUE, 5),
         [('Age', '38'), ('Once', 'Teacher at the Royal Magic Academy')],
         'One of the strongest mages of the Western Continent, and Kael\'s favourite teacher at the Academy. Since she '
         'retired she is rarely seen in public; when she is, the room gathers around her.',
         ('On a night walk outside the capital she showed Kael something wrong in the flow of mana, and left him '
          'with a few words: "Go, see the world. You will find that we are small."', at(V_PROLOGUE, 8))),
    char('tobin', 'Tobin', 'Royal Capital of Nova', 'Carter', ('People1', 4), at(V_PROLOGUE, 1),
         [('Work', 'Carts goods to and from the capital')],
         'A carter from the capital. His cart was wrecked by monsters on the Briarwood road, and Kael, sent by the '
         'Guild, found him hiding in the bushes with a twisted ankle.',
         ('Five months later, a swordswoman knocked him down in the market and called him a thief. He swears he '
          'is not.', at(V_CH1, 7)),
         ('He was lying. The night his cart was wrecked he was carrying crates for a bandit crew, and he had been '
          'picking pockets ever since to pay for the cargo he lost. He walked the bandits to the gate himself.',
          at(V_CH1, 13))),
    char('greta', 'Greta', 'Royal Capital of Nova', "Tobin's wife", GRETA_FACE, at(V_CH1, 11),
         [('Home', 'Ember Lane, Lantern Row')],
         "Tobin's wife, a few doors down from the Ashveil house. When Tobin went missing in Briarwood she filled half "
         "the Guild's request board and waited at the Main Gate from dawn.",
         ('Five months later she waited at the gate again, the night Kael and Yuki went after Tobin a second time.',
          at(V_CH1, 13))),
    char('mara', 'Captain Mara', 'Royal Capital of Nova', 'Captain of the Morning Gull', ('People2', 3), at(V_CH1, 2),
         [('Ship', 'The Morning Gull'), ('Port', 'Saltwind Harbor')],
         'Captain of the Morning Gull, which crosses the sea between the Eastern Continent and Saltwind Harbor. '
         'Six weeks at sea have not dulled her tongue.'),
]


def register():
    with open(L.DATA + 'Characters.json', 'w', encoding='utf8', newline='') as f:
        json.dump(CHARACTERS, f, ensure_ascii=False, indent=1)
    import scene_select
    scene_select.register_plugin('NovaEncyclopedia', 'Encyclopedia in the main menu: Characters (people met on the '
                                 'journey), the Bestiary and Items (everything the party has found).',
                                 {'Menu Command': 'Encyclopedia', 'Data File': 'Characters.json', 'Unknown Name': '??????'})


if __name__ == '__main__':
    register()
    print('%d characters written' % len(CHARACTERS))
