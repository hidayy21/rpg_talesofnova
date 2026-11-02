//=============================================================================
// NovaSceneSelect.js
//=============================================================================
/*:
 * @plugindesc Playtest only: "Scene Select" on the title screen jumps straight
 * to a story scene, with its variables, switches, items and clock set.
 * @author Project Nova
 *
 * @param Scenes
 * @type note
 * @desc One scene per line. See the help. Written by prologue.py for the Prologue.
 * @default ""
 *
 * @help
 * Only in playtest (started from the editor or Playtest.bat).
 *
 * On the title screen choose "Scene Select", then a scene: a new game starts
 * right there. One line per scene in the Scenes parameter:
 *
 *   Label = map, x, y, direction ; setting ; setting ...
 *
 * Settings:
 *   v1=4                 variable 1 = 4
 *   s11=on               switch 11 ON (off: OFF)
 *   item=51              gain item 51 (item=1x3: three of item 1)
 *   gold=120             gain 120 gold
 *   done=Event Name      self switch A ON for the events with this name on
 *                        the target map (cutscenes that already happened)
 *   cmd=Clock set 17:00  any plugin command
 *   tint=-51,-17,68,34   screen tone (red, green, blue, gray)
 *
 * Example:
 *   Guild: Isolde = 12, 10, 14, 8 ; v1=5 ; item=51 ; cmd=Clock set 17:30
 */

(function() {
    'use strict';

    if (!Utils.isNwjs() || !Utils.isOptionValid('test')) return;

    var raw = PluginManager.parameters('NovaSceneSelect')['Scenes'] || '';
    try { if (raw.charAt(0) === '"') raw = JSON.parse(raw); } catch (e) { }

    var SCENES = raw.split(/\r?\n/).map(function(line) {
        var m = /^\s*(.+?)\s*=\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*(;.*)?$/.exec(line);
        if (!m) return null;
        var settings = (m[6] || '').split(';').map(function(s) { return s.trim(); }).filter(Boolean);
        return { label: m[1], map: +m[2], x: +m[3], y: +m[4], d: +m[5], settings: settings };
    }).filter(Boolean);
    if (!SCENES.length) return;

    var pendingDone = null;      // [mapId, [event names]] waiting for that map to load

    function start(scene) {
        DataManager.setupNewGame();
        var done = [];
        scene.settings.forEach(function(s) {
            var kv = /^(\w+?)(\d*)\s*=\s*(.*)$/.exec(s);
            if (!kv) return;
            var key = kv[1], id = +kv[2], val = kv[3].trim();
            if (key === 'v') $gameVariables.setValue(id, Number(val));
            else if (key === 's') $gameSwitches.setValue(id, /^(on|true|1)$/i.test(val));
            else if (key === 'item') {
                var it = /^(\d+)(?:\s*x\s*(\d+))?$/i.exec(val);
                if (it) $gameParty.gainItem($dataItems[+it[1]], it[2] ? +it[2] : 1);
            }
            else if (key === 'gold') $gameParty.gainGold(Number(val));
            else if (key === 'done') done.push(val);
            else if (key === 'cmd') {
                var args = val.split(/\s+/);
                new Game_Interpreter().pluginCommand(args.shift(), args);
            }
            else if (key === 'tint') $gameScreen.startTint(val.split(',').map(Number), 0);
        });
        pendingDone = done.length ? [scene.map, done] : null;
        $gamePlayer.reserveTransfer(scene.map, scene.x, scene.y, scene.d, 0);
    }

    // self switches can only be found by event name once the target map is loaded
    var _Game_Map_setup = Game_Map.prototype.setup;
    Game_Map.prototype.setup = function(mapId) {
        _Game_Map_setup.call(this, mapId);
        if (!pendingDone || pendingDone[0] !== mapId) return;
        var names = pendingDone[1];
        pendingDone = null;
        $dataMap.events.forEach(function(ev) {
            if (ev && names.indexOf(ev.name) >= 0) $gameSelfSwitches.setValue([mapId, ev.id, 'A'], true);
        });
        this.requestRefresh();
    };

    //=========================================================================
    // Title screen
    //=========================================================================
    function Window_NovaScenes() {
        this.initialize.apply(this, arguments);
    }

    Window_NovaScenes.prototype = Object.create(Window_Command.prototype);
    Window_NovaScenes.prototype.constructor = Window_NovaScenes;

    Window_NovaScenes.prototype.initialize = function() {
        Window_Command.prototype.initialize.call(this, 0, 0);
        this.x = (Graphics.boxWidth - this.width) / 2;
        this.y = (Graphics.boxHeight - this.height) / 2;
        this.openness = 0;
        this.deactivate();
    };

    Window_NovaScenes.prototype.windowWidth = function() { return 520; };
    Window_NovaScenes.prototype.numVisibleRows = function() { return Math.min(SCENES.length, 10); };

    Window_NovaScenes.prototype.makeCommandList = function() {
        SCENES.forEach(function(s) { this.addCommand(s.label, 'scene'); }, this);
    };

    var _Window_TitleCommand_makeCommandList = Window_TitleCommand.prototype.makeCommandList;
    Window_TitleCommand.prototype.makeCommandList = function() {
        _Window_TitleCommand_makeCommandList.call(this);
        this.addCommand('Scene Select', 'novaScenes');
    };

    var _Scene_Title_createCommandWindow = Scene_Title.prototype.createCommandWindow;
    Scene_Title.prototype.createCommandWindow = function() {
        _Scene_Title_createCommandWindow.call(this);
        this._commandWindow.setHandler('novaScenes', this.commandNovaScenes.bind(this));
        this._novaScenes = new Window_NovaScenes();
        this._novaScenes.setHandler('scene', this.onNovaScene.bind(this));
        this._novaScenes.setHandler('cancel', this.onNovaScenesCancel.bind(this));
        this.addWindow(this._novaScenes);
    };

    Scene_Title.prototype.commandNovaScenes = function() {
        this._commandWindow.close();
        this._novaScenes.open();
        this._novaScenes.activate();
    };

    Scene_Title.prototype.onNovaScenesCancel = function() {
        this._novaScenes.close();
        this._commandWindow.open();
        this._commandWindow.activate();
    };

    Scene_Title.prototype.onNovaScene = function() {
        start(SCENES[this._novaScenes.index()]);
        this._novaScenes.close();
        this.fadeOutAll();
        SceneManager.goto(Scene_Map);
    };
})();
