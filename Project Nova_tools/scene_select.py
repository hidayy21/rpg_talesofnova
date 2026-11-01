# The Scene Select list on the title screen (NovaSceneSelect, playtest only): every story script's checkpoints, in
# story order, written into the plugin's entry in js/plugins.js. prologue.py and chapter1.py call register() after
# --save, so the list always matches the maps.
#   python scene_select.py          -> rewrite the list only
import json
import nova_maplib as L


def register():
    import prologue, chapter1
    rows = prologue.scenes() + chapter1.scenes()
    text = '\n'.join('%s = %d, %d, %d, %d' % ((label,) + spot) + ''.join(' ; ' + s for s in settings)
                     for label, spot, settings in rows)
    path = L.PROJ + 'js/plugins.js'
    src = open(path, encoding='utf8').read()
    head, body = src.split('var $plugins =', 1)
    plugins = json.loads(body.strip().rstrip(';'))
    entry = next((p for p in plugins if p['name'] == 'NovaSceneSelect'), None)
    if not entry:
        entry = {'name': 'NovaSceneSelect', 'status': True, 'description': 'Playtest only: "Scene Select" on the title '
                 'screen jumps straight to a story scene, with its variables, switches, items and clock set.', 'parameters': {}}
        plugins.append(entry)
    entry['parameters']['Scenes'] = json.dumps(text, ensure_ascii=False)
    j = lambda v: json.dumps(v, ensure_ascii=False, separators=(',', ':'))
    with open(path, 'w', encoding='utf8', newline='') as f:
        f.write(head + 'var $plugins =\n[\n' + ',\n'.join(j(p) for p in plugins) + '\n];\n')


def register_plugin(name, description, parameters=None):
    """Add a plugin to js/plugins.js (at the end) unless it is already there."""
    path = L.PROJ + 'js/plugins.js'
    src = open(path, encoding='utf8').read()
    head, body = src.split('var $plugins =', 1)
    plugins = json.loads(body.strip().rstrip(';'))
    if any(p['name'] == name for p in plugins): return
    plugins.append({'name': name, 'status': True, 'description': description, 'parameters': parameters or {}})
    j = lambda v: json.dumps(v, ensure_ascii=False, separators=(',', ':'))
    with open(path, 'w', encoding='utf8', newline='') as f:
        f.write(head + 'var $plugins =\n[\n' + ',\n'.join(j(p) for p in plugins) + '\n];\n')


if __name__ == '__main__':
    register()
    print('scene list written')
