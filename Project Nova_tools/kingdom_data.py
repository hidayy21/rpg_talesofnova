# Database additions for the Royal Kingdom of Nova maps:
#  - food items (fishmonger, bakery, tavern), companion accessories (pet shop)
#  - common events: magic shop, pet shop, fishmonger, bakery, inn (rest), tavern
#  - Nova_Market_D registered as slot D of the Outside tileset, with flags copied from the Inside tileset
#  - Baker's Lane: doors lead into the Bakery / Tavern / Inn, street ends connect to the Plaza and Residential
# Idempotent: re-running updates the same ids instead of appending.
import copy, json, sys
sys.path.insert(0, 'D:/RPG Maker MV/Project Nova_tools')
import data_ids as DI
import kingdom as K
import nova_maplib as L
from make_town_tiles import build as build_props

DATA = L.DATA


def load(n): return json.load(open(DATA + n + '.json', encoding='utf8'))


def save(n, arr):
    with open(DATA + n + '.json', 'w', encoding='utf8', newline='') as f:
        f.write('[\n' + ',\n'.join(json.dumps(x, ensure_ascii=False, separators=(',', ':')) for x in arr) + '\n]')


def put(arr, idx, obj):
    while len(arr) <= idx: arr.append(None)
    obj['id'] = idx
    arr[idx] = obj


def cmd(code, params, indent=0): return {'code': code, 'indent': indent, 'parameters': params}


def main():
    Items, Armors, CE, Tilesets = load('Items'), load('Armors'), load('CommonEvents'), load('Tilesets')
    ITEM_T = copy.deepcopy(Items[1]); ARMOR_T = copy.deepcopy(Armors[4])

    # ---------------------------------------------------------------- food
    def food(idx, name, icon, price, desc, effects, scope=7):
        it = copy.deepcopy(ITEM_T)
        it.update({'name': name, 'iconIndex': icon, 'price': price, 'description': desc, 'effects': effects,
                   'scope': scope, 'occasion': 0, 'animationId': 41, 'consumable': True, 'itypeId': 1, 'note': ''})
        put(Items, idx, it)
    hp = lambda r=0, f=0: {'code': 11, 'dataId': 0, 'value1': r, 'value2': f}
    mp = lambda r=0, f=0: {'code': 12, 'dataId': 0, 'value1': r, 'value2': f}
    food(DI.ITEM_TROUT, 'Grilled Trout', 260, 180, 'Fresh from Saltwind Harbor. Restores 800 HP.', [hp(0, 800)])
    food(DI.ITEM_CHOWDER, 'Seafood Chowder', 211, 420, 'A hot harbor chowder. Restores 25% HP of all allies.', [hp(0.25)], scope=8)
    food(DI.ITEM_EEL, 'Smoked Eel', 272, 260, 'Rich and salty. Restores 120 MP.', [mp(0, 120)])
    food(DI.ITEM_BUN, 'Sweet Bun', 267, 40, 'From the Golden Crust bakery. Restores 250 HP.', [hp(0, 250)])
    food(DI.ITEM_HONEY_BREAD, 'Honey Bread', 266, 150, 'The royal kitchens\' favourite. Restores 500 HP and 40 MP.', [hp(0, 500), mp(0, 40)])

    # ---------------------------------------------------------------- companions (pet shop accessories)
    def companion(idx, name, icon, price, desc, params, traits):
        a = copy.deepcopy(ARMOR_T)
        p = [0] * 8
        for k, v in params.items(): p[['mhp', 'mmp', 'atk', 'def', 'mat', 'mdf', 'agi', 'luk'].index(k)] = v
        a.update({'name': name, 'iconIndex': icon, 'price': price, 'description': desc, 'params': p,
                  'atypeId': 1, 'etypeId': 5, 'traits': [{'code': 22, 'dataId': 1, 'value': 0}] + traits,
                  'note': '<companion>'})
        put(Armors, idx, a)
    xp = lambda i, v: {'code': 22, 'dataId': i, 'value': v}
    companion(DI.PET_CAT, 'Companion: Alley Cat', 135, 3000, 'A clever street cat that warns you of danger.\nAGI +12, Evasion +5%.', {'agi': 12}, [xp(1, 0.05)])
    companion(DI.PET_HOUND, 'Companion: Loyal Hound', 140, 3000, 'A brave hound that bites back.\nATK +12, Counter +6%.', {'atk': 12}, [xp(6, 0.06)])
    companion(DI.PET_OWL, 'Companion: Barn Owl', 149, 3500, 'A wise owl that whispers forgotten words.\nM.Attack +12, MP regen +3%.', {'mat': 12}, [xp(8, 0.03)])
    companion(DI.PET_CHICK, 'Companion: Lucky Chick', 268, 4000, 'A chick that always finds something shiny.\nLUK +20, double item drops.', {'luk': 20},
              [{'code': 64, 'dataId': 5, 'value': 0}])

    # ---------------------------------------------------------------- common events
    def shop_list(goods, purchase_only=False):
        (t0, i0), rest = goods[0], goods[1:]
        return [cmd(302, [t0, i0, 0, 0, purchase_only])] + [cmd(605, [t, i, 0, 0]) for t, i in rest]
    ITEM, WEAPON, ARMOR = 0, 1, 2
    magic = ([(WEAPON, w) for w in (17, 12, 18, 13, 42, 43, 19, 14, 44)] +
             [(ITEM, i) for i in (2, 7, 8, 36)] + [(ARMOR, a) for a in (39, 44, 46, 52, 56)])
    pets = [(ARMOR, a) for a in (DI.PET_CAT, DI.PET_HOUND, DI.PET_OWL, DI.PET_CHICK)]
    fish = [(ITEM, i) for i in (DI.ITEM_TROUT, DI.ITEM_EEL, DI.ITEM_CHOWDER)]
    bakery = [(ITEM, i) for i in (DI.ITEM_BUN, DI.ITEM_HONEY_BREAD, 21)]
    tavern = [(ITEM, i) for i in (21, 33, 34, 35, DI.ITEM_TROUT, DI.ITEM_CHOWDER, 1)]
    P = DI.INN_PRICE
    inn = [
        cmd(101, ['', 0, 0, 2]), cmd(401, ['A room for the night is %d G.' % P]), cmd(401, ['Would you like to rest?']),
        cmd(102, [['Rest (%d G)' % P, 'No thanks'], 1, 0, 2, 0]),
        cmd(402, [0, 'Rest (%d G)' % P]),
        cmd(111, [7, P, 0], 1),
        cmd(125, [1, 0, P], 2),
        cmd(221, [], 2),
        cmd(249, [{'name': 'Inn', 'volume': 90, 'pitch': 100, 'pan': 0}], 2),
        cmd(314, [0, 0], 2),
        cmd(230, [150], 2),
        cmd(222, [], 2),
        cmd(101, ['', 0, 0, 2], 2), cmd(401, ['Good morning! Sleep well?'], 2),
        cmd(0, [], 2),
        cmd(411, [], 1),
        cmd(101, ['', 0, 0, 2], 2), cmd(401, ['Oh dear, you don\'t have enough gold.'], 2),
        cmd(0, [], 2),
        cmd(412, [], 1),
        cmd(0, [], 1),
        cmd(402, [1, 'No thanks']),
        cmd(101, ['', 0, 0, 2], 1), cmd(401, ['Come back any time!'], 1),
        cmd(0, [], 1),
        cmd(404, []),
    ]
    events = {DI.CE_MAGIC: ('Shop: Magic (Starlit Grimoire)', shop_list(magic)),
              DI.CE_PETS: ('Shop: Companions (Whisker & Paw)', shop_list(pets)),
              DI.CE_FISH: ('Shop: Fishmonger', shop_list(fish)),
              DI.CE_BAKERY: ('Shop: Bakery', shop_list(bakery)),
              DI.CE_INN: ('Inn: Silver Swan (%d G)' % P, inn),
              DI.CE_TAVERN: ('Shop: Tavern', shop_list(tavern))}
    for idx, (nm, lst) in events.items():
        put(CE, idx, {'list': lst + [cmd(0, [])], 'name': nm, 'switchId': 1, 'trigger': 0})

    # ---------------------------------------------------------------- tileset: Nova_Market_D in the Outside tileset
    ids, flags = build_props(write=True)
    ts = Tilesets[2]
    ts['tilesetNames'][7] = 'Nova_Market_D'
    for tid, fl in flags.items(): ts['flags'][tid] = fl

    save('Items', Items); save('Armors', Armors); save('CommonEvents', CE); save('Tilesets', Tilesets)
    print('items', len(Items) - 1, 'armors', len(Armors) - 1, 'common events', len(CE) - 1, 'D props', len(ids))


def patch_bakers_lane():
    """Doors of Baker's Lane lead inside; the street ends connect to the Plaza and the Residential Quarter."""
    path = DATA + 'Map002.json'
    m = json.load(open(path, encoding='utf8'))
    ev = {e['name']: e for e in m['events'] if e}
    def set_door(name, target, tx, ty):
        e = ev[name]
        e['pages'] = [L.door_page(target, tx, ty, 8, '!Door1', e['pages'][0]['image']['characterIndex'])]
    set_door('Bakery Door', K.BAKERY, 7, 10)
    set_door('Tavern Door', K.TAVERN, 10, 13)
    set_door('Inn Door', K.INN, 5, 13)
    # remove previous edge exits (re-run safe), then add new ones
    m['events'] = [e if (e is None or not e['name'].startswith('Edge:')) else None for e in m['events']]
    while m['events'] and m['events'][-1] is None and len(m['events']) > 1: m['events'].pop()
    m['note'] = '<outdoor>'          # NovaLighting: follows the night switch
    W = m['width']
    def edge(label, cells, target, tx, ty, d):
        for i, (x, y) in enumerate(cells):
            oy = y - cells[0][1]
            e = {'id': len(m['events']), 'name': 'Edge: %s %d' % (label, i + 1), 'note': '',
                 'pages': [L.exit_page(target, tx, ty + oy if d in (4, 6) else ty, d)], 'x': x, 'y': y}
            m['events'].append(e)
    edge('Plaza (street 1)', [(W - 1, y) for y in range(7, 11)], K.PLAZA, 1, 1, 2)
    edge('Plaza (street 2)', [(W - 1, y) for y in range(17, 21)], K.PLAZA, 1, 1, 2)
    edge('Residential (street 1)', [(0, y) for y in range(7, 11)], K.RESIDENTIAL, 38, 1, 2)
    edge('Residential (street 2)', [(0, y) for y in range(17, 21)], K.RESIDENTIAL, 38, 1, 2)
    with open(path, 'w', encoding='utf8', newline='') as f:
        json.dump(m, f, ensure_ascii=False, separators=(',', ':'))
    infos = json.load(open(DATA + 'MapInfos.json', encoding='utf8'))
    infos[2]['parentId'] = K.PLAZA; infos[2]['name'] = "Nova - Baker's Lane"; infos[2]['order'] = 8
    with open(DATA + 'MapInfos.json', 'w', encoding='utf8', newline='') as f:
        f.write('[\n' + ',\n'.join(json.dumps(x, ensure_ascii=False, separators=(',', ':')) for x in infos) + '\n]')
    print("Baker's Lane patched")


if __name__ == '__main__':
    main()
    patch_bakers_lane()
