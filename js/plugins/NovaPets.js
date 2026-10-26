//=============================================================================
// NovaPets.js
//=============================================================================
/*:
 * @plugindesc Pet companions: one active pet follows the party on the map,
 * jumps into battle to help, and has its own screen in the main menu.
 * @author Project Nova
 *
 * @param Menu Command
 * @desc Name of the main menu command.
 * @default Pets
 *
 * @param Assist Message
 * @desc Shown in the battle log when no skill message is set. %1 = pet name.
 * @default %1 jumps in!
 *
 * @help
 * ---------------------------------------------------------------------------
 * Making a pet
 *   A pet is an ordinary actor in the database that is never added to the
 *   party. Give it a walking sprite (characterName / index), a class for its
 *   stats, and these note tags:
 *
 *     <pet>
 *     <pet skills: 141, 142@12>   skills it may use; @12 = from level 12
 *     <pet assist: 35>            % chance to help at the end of each turn
 *     <pet passive: 58>           while active, every party member gets the
 *                                 params and traits of armor 58 (optional)
 *     <pet sound: Dog>            sound effect when it is chosen (optional)
 *
 *   The actor's Nickname is shown as its title and the Profile as its
 *   description on the Pets screen.
 *
 *   Pets have no EXP of their own: their level always matches the highest
 *   level in the party, so they grow with you. Pet skills normally cost
 *   nothing; set the skill's Occasion to "Battle Screen".
 *
 * In battle
 *   After everyone has acted, the active pet may use one of its skills.
 *   Heals are only used when someone is hurt (on the most hurt ally),
 *   buffs only when they are not already active.
 *
 * Plugin commands
 *   NovaPet add 7          give the party pet actor 7 (first pet becomes active)
 *   NovaPet remove 7       take it away
 *   NovaPet active 7       make pet 7 the one that follows you
 *   NovaPet active none    no pet follows (they wait at home)
 *   NovaPet menu           open the Pets screen
 *
 * Script (e.g. in a Conditional Branch)
 *   $gameParty.hasNovaPet(7)     true when the party owns pet 7
 *   $gameParty.novaActivePet()   the active pet's Game_Actor, or null
 * ---------------------------------------------------------------------------
 */

(function() {
    'use strict';

    var params = PluginManager.parameters('NovaPets');
    var MENU_NAME = String(params['Menu Command'] || 'Pets');
    var ASSIST_MSG = String(params['Assist Message'] || '%1 jumps in!');

    var COLOR = {
        accent: '#62d6ff',
        dim: '#a9c4dc',
        locked: 'rgba(200, 220, 240, 0.4)',
        active: '#ffd27a'
    };

    //=========================================================================
    // Pet data from actor notes
    //=========================================================================
    var NovaPets = {};

    NovaPets.isPet = function(actorId) {
        var data = $dataActors[actorId];
        return !!(data && data.meta.pet);
    };

    // [{ skillId, level }] from <pet skills: 141, 142@12>
    NovaPets.skillList = function(actorId) {
        var data = $dataActors[actorId];
        var raw = data && data.meta['pet skills'];
        if (!raw || raw === true) return [];
        return String(raw).split(',').map(function(part) {
            var m = part.trim().match(/^(\d+)(?:\s*@\s*(\d+))?$/);
            return m ? { skillId: Number(m[1]), level: Number(m[2] || 1) } : null;
        }).filter(function(s) { return s && $dataSkills[s.skillId]; });
    };

    NovaPets.assistChance = function(actorId) {
        var data = $dataActors[actorId];
        var raw = data && data.meta['pet assist'];
        return raw && raw !== true ? Math.max(0, Math.min(100, Number(raw))) : 30;
    };

    // Pets keep pace with the strongest party member.
    NovaPets.syncLevel = function(pet) {
        var top = $gameParty.members().reduce(function(lv, actor) {
            return Math.max(lv, actor.level);
        }, 1);
        if (pet.level !== top) pet.changeLevel(Math.min(top, pet.maxLevel()), false);
    };

    NovaPets.knownSkills = function(pet) {
        return NovaPets.skillList(pet.actorId()).filter(function(s) {
            return pet.level >= s.level;
        }).map(function(s) { return $dataSkills[s.skillId]; });
    };

    // The armor whose params and traits the whole party shares while the pet is out.
    NovaPets.passiveArmor = function(actorId) {
        var data = $dataActors[actorId];
        var id = data && Number(data.meta['pet passive']);
        return id ? $dataArmors[id] || null : null;
    };

    window.NovaPets = NovaPets;

    //=========================================================================
    // Party bonus from the active pet
    //=========================================================================
    Game_Actor.prototype.novaPetBonus = function() {
        if (!$gameParty || NovaPets.isPet(this.actorId())) return null;
        var state = $gameParty._novaPets;
        if (!state || !state.active || !$gameParty._actors.contains(this.actorId())) return null;
        return $gameParty.hasNovaPet(state.active) ? NovaPets.passiveArmor(state.active) : null;
    };

    var _Game_Actor_traitObjects = Game_Actor.prototype.traitObjects;
    Game_Actor.prototype.traitObjects = function() {
        var objects = _Game_Actor_traitObjects.call(this);
        var bonus = this.novaPetBonus();
        if (bonus) objects.push(bonus);
        return objects;
    };

    var _Game_Actor_paramPlus = Game_Actor.prototype.paramPlus;
    Game_Actor.prototype.paramPlus = function(paramId) {
        var value = _Game_Actor_paramPlus.call(this, paramId);
        var bonus = this.novaPetBonus();
        return bonus ? value + bonus.params[paramId] : value;
    };

    //=========================================================================
    // Ownership: $gameParty
    //=========================================================================
    Game_Party.prototype.novaPetState = function() {
        if (!this._novaPets) this._novaPets = { owned: [], active: 0 };
        return this._novaPets;
    };

    Game_Party.prototype.novaPets = function() {
        return this.novaPetState().owned.filter(NovaPets.isPet).map(function(id) {
            return $gameActors.actor(id);
        });
    };

    Game_Party.prototype.hasNovaPet = function(actorId) {
        return this.novaPetState().owned.contains(Number(actorId));
    };

    Game_Party.prototype.novaActivePet = function() {
        var id = this.novaPetState().active;
        return id && this.hasNovaPet(id) && NovaPets.isPet(id) ? $gameActors.actor(id) : null;
    };

    Game_Party.prototype.addNovaPet = function(actorId) {
        actorId = Number(actorId);
        if (!NovaPets.isPet(actorId) || this.hasNovaPet(actorId)) return;
        var state = this.novaPetState();
        state.owned.push(actorId);
        if (!state.active) state.active = actorId;
        $gamePlayer.refresh();
    };

    Game_Party.prototype.removeNovaPet = function(actorId) {
        actorId = Number(actorId);
        var state = this.novaPetState();
        state.owned = state.owned.filter(function(id) { return id !== actorId; });
        if (state.active === actorId) state.active = 0;
        $gamePlayer.refresh();
    };

    Game_Party.prototype.setNovaActivePet = function(actorId) {
        actorId = Number(actorId) || 0;
        if (actorId && !this.hasNovaPet(actorId)) return;
        this.novaPetState().active = actorId;
        $gamePlayer.refresh();
    };

    //=========================================================================
    // Plugin commands
    //=========================================================================
    var _Game_Interpreter_pluginCommand = Game_Interpreter.prototype.pluginCommand;
    Game_Interpreter.prototype.pluginCommand = function(command, args) {
        _Game_Interpreter_pluginCommand.call(this, command, args);
        if (command.toLowerCase() !== 'novapet') return;
        var sub = String(args[0] || '').toLowerCase();
        var id = args[1];
        if (sub === 'add') $gameParty.addNovaPet(id);
        else if (sub === 'remove') $gameParty.removeNovaPet(id);
        else if (sub === 'active') $gameParty.setNovaActivePet(String(id).toLowerCase() === 'none' ? 0 : id);
        else if (sub === 'menu') SceneManager.push(Scene_NovaPets);
    };

    //=========================================================================
    // Map: the active pet walks behind the last visible party member
    //=========================================================================
    function Game_NovaPetFollower() { this.initialize.apply(this, arguments); }
    Game_NovaPetFollower.prototype = Object.create(Game_Follower.prototype);
    Game_NovaPetFollower.prototype.constructor = Game_NovaPetFollower;

    Game_NovaPetFollower.prototype.initialize = function() {
        Game_Follower.prototype.initialize.call(this, -1);
    };
    // Not a party member: anything that asks a follower for its actor gets none.
    Game_NovaPetFollower.prototype.actor = function() { return null; };
    Game_NovaPetFollower.prototype.pet = function() { return $gameParty.novaActivePet(); };
    Game_NovaPetFollower.prototype.isVisible = function() {
        return !!this.pet() && $gamePlayer.followers().isVisible();
    };
    Game_NovaPetFollower.prototype.refresh = function() {
        var pet = this.isVisible() ? this.pet() : null;
        this.setImage(pet ? pet.characterName() : '', pet ? pet.characterIndex() : 0);
    };
    window.Game_NovaPetFollower = Game_NovaPetFollower;  // JsonEx needs it global for save files

    Game_Followers.prototype.novaEnsurePet = function() {
        var has = this._data.some(function(f) { return f instanceof Game_NovaPetFollower; });
        if (!has) {
            var pet = new Game_NovaPetFollower();
            var last = this._data[this._data.length - 1] || $gamePlayer;
            pet.locate(last.x, last.y);
            pet.setDirection(last.direction());
            this._data.push(pet);
        }
    };

    Game_Followers.prototype.novaPetLeader = function() {
        for (var i = this._data.length - 1; i >= 0; i--) {
            var f = this._data[i];
            if (!(f instanceof Game_NovaPetFollower) && f.isVisible()) return f;
        }
        return $gamePlayer;
    };

    var _Game_Followers_initialize = Game_Followers.prototype.initialize;
    Game_Followers.prototype.initialize = function() {
        _Game_Followers_initialize.call(this);
        this._data.push(new Game_NovaPetFollower());
    };

    Game_Followers.prototype.updateMove = function() {
        for (var i = this._data.length - 1; i >= 0; i--) {
            var f = this._data[i];
            var preceding = f instanceof Game_NovaPetFollower ? this.novaPetLeader() :
                            (i > 0 ? this._data[i - 1] : $gamePlayer);
            f.chaseCharacter(preceding);
        }
    };

    // Older save files were made before the pet follower existed.
    var _Scene_Map_onMapLoaded = Scene_Map.prototype.onMapLoaded;
    Scene_Map.prototype.onMapLoaded = function() {
        $gamePlayer.followers().novaEnsurePet();
        _Scene_Map_onMapLoaded.call(this);
    };

    //=========================================================================
    // Battle: the pet acts once after everyone else, if the dice say so
    //=========================================================================
    var _BattleManager_setup = BattleManager.setup;
    BattleManager.setup = function(troopId, canEscape, canLose) {
        _BattleManager_setup.call(this, troopId, canEscape, canLose);
        var pet = $gameParty.novaActivePet();
        if (pet) {
            NovaPets.syncLevel(pet);
            pet.clearStates();
            pet.clearBuffs();
            pet.recoverAll();
        }
    };

    var _BattleManager_startTurn = BattleManager.startTurn;
    BattleManager.startTurn = function() {
        this._novaPetActed = false;
        _BattleManager_startTurn.call(this);
    };

    BattleManager.updateTurn = function() {
        $gameParty.requestMotionRefresh();
        if (!this._subject) {
            this._subject = this.getNextSubject();
        }
        if (this._subject) {
            this.processTurn();
        } else if (!this.novaStartPetAssist()) {
            this.endTurn();
        }
    };

    BattleManager.novaStartPetAssist = function() {
        if (this._novaPetActed) return false;
        this._novaPetActed = true;
        var pet = $gameParty.novaActivePet();
        if (!pet || !pet.isAlive() || $gameParty.isAllDead() || $gameTroop.isAllDead()) return false;
        if (Math.random() * 100 >= NovaPets.assistChance(pet.actorId())) return false;
        var action = NovaPets.chooseAction(pet);
        if (!action) return false;
        pet.clearActions();
        pet._actions.push(action);
        this._subject = pet;
        this._novaPetAssisting = true;
        this.startAction();
        pet.removeCurrentAction();
        return true;
    };

    var _BattleManager_endAction = BattleManager.endAction;
    BattleManager.endAction = function() {
        _BattleManager_endAction.call(this);
        if (this._novaPetAssisting) {
            // The pet has no further actions: drop it so the turn can end cleanly.
            this._novaPetAssisting = false;
            this._subject = null;
        }
    };

    BattleManager.isNovaPetAssisting = function() { return !!this._novaPetAssisting; };

    function hurtRate(actor) { return actor.hp / Math.max(1, actor.mhp); }

    function isHeal(skill) { return skill.damage.type === 3; }
    function isDamage(skill) { return skill.damage.type === 1 || skill.damage.type === 5; }
    function isBuff(skill) {
        return skill.effects.some(function(e) { return e.code === Game_Action.EFFECT_ADD_BUFF; });
    }

    // Pick a sensible skill and target; null if nothing is worth doing.
    NovaPets.chooseAction = function(pet) {
        var allies = $gameParty.aliveMembers();
        var choices = [];
        NovaPets.knownSkills(pet).forEach(function(skill) {
            if (!pet.canUse(skill)) return;
            var action = new Game_Action(pet);
            action.setSkill(skill.id);
            var weight = 0;
            if (action.isForOpponent() && isDamage(skill)) {
                weight = 10;
                action.setTarget(-1);
            } else if (action.isForFriend() && isHeal(skill)) {
                var hurt = allies.filter(function(a) { return hurtRate(a) < 0.6; });
                if (hurt.length === 0) return;
                weight = action.isForAll() ? (hurt.length >= 2 ? 30 : 12) : 25;
                if (!action.isForAll()) {
                    var worst = hurt.reduce(function(a, b) { return hurtRate(a) <= hurtRate(b) ? a : b; });
                    action.setTarget(worst.index());
                }
            } else if (isBuff(skill)) {
                var buffs = skill.effects.filter(function(e) { return e.code === Game_Action.EFFECT_ADD_BUFF; });
                var targets = action.isForFriend() ? allies : [];
                var needed = targets.some(function(a) {
                    return buffs.some(function(e) { return !a.isMaxBuffAffected(e.dataId) && !a.isBuffAffected(e.dataId); });
                });
                if (!needed) return;
                weight = 8;
                action.setTarget(-1);
            } else {
                weight = 4;
                action.setTarget(-1);
            }
            choices.push({ action: action, weight: weight });
        });
        if (choices.length === 0) return null;
        var total = choices.reduce(function(sum, c) { return sum + c.weight; }, 0);
        var roll = Math.random() * total;
        for (var i = 0; i < choices.length; i++) {
            roll -= choices[i].weight;
            if (roll < 0) return choices[i].action;
        }
        return choices[choices.length - 1].action;
    };

    // A short line before the skill message, so it is clear the pet acted.
    var _Window_BattleLog_displayAction = Window_BattleLog.prototype.displayAction;
    Window_BattleLog.prototype.displayAction = function(subject, item) {
        if (BattleManager.isNovaPetAssisting() && !item.message1) {
            this.push('addText', ASSIST_MSG.format(subject.name()));
            return;
        }
        _Window_BattleLog_displayAction.call(this, subject, item);
    };

    // The pet stands at the end of the party line, facing the enemy.
    function Sprite_NovaPet() { this.initialize.apply(this, arguments); }
    Sprite_NovaPet.prototype = Object.create(Sprite.prototype);
    Sprite_NovaPet.prototype.constructor = Sprite_NovaPet;

    Sprite_NovaPet.prototype.initialize = function() {
        Sprite.prototype.initialize.call(this);
        this.anchor.x = 0.5;
        this.anchor.y = 1;
        this._petId = 0;
        this._tick = 0;
        this._hop = 0;
        this._shadow = new Sprite(ImageManager.loadSystem('Shadow1'));
        this._shadow.anchor.x = 0.5;
        this._shadow.anchor.y = 0.5;
        this._shadow.y = -2;
        this._body = new Sprite();
        this._body.anchor.x = 0.5;
        this._body.anchor.y = 1;
        this.addChild(this._shadow);
        this.addChild(this._body);
    };

    // Just behind the party line, between the 2nd and 3rd member: clear of the
    // status window and of heroes stepping forward to act.
    Sprite_NovaPet.prototype.homePosition = function() {
        var a = { setHome: function(x, y) { this._homeX = x; this._homeY = y; } };
        var b = { setHome: a.setHome };
        Sprite_Actor.prototype.setActorHome.call(a, 1);
        Sprite_Actor.prototype.setActorHome.call(b, 2);
        return { x: (a._homeX + b._homeX) / 2 + 72, y: (a._homeY + b._homeY) / 2 + 4 };
    };

    Sprite_NovaPet.prototype.update = function() {
        Sprite.prototype.update.call(this);
        var pet = $gameParty.novaActivePet();
        this.visible = !!pet && pet.isAlive() && $gameSystem.isSideView();
        if (!this.visible) return;
        if (pet.actorId() !== this._petId) {
            this._petId = pet.actorId();
            this._body.bitmap = ImageManager.loadCharacter(pet.characterName());
            this._bigSheet = ImageManager.isBigCharacter(pet.characterName());
            this._charIndex = pet.characterIndex();
        }
        if (BattleManager.isNovaPetAssisting() && BattleManager._subject === pet && this._hop === 0) {
            this._hop = 24;
        }
        this._tick++;
        var home = this.homePosition();
        var lift = 0, step = 0;
        if (this._hop > 0) {
            var t = (24 - this._hop) / 24;
            lift = Math.sin(t * Math.PI) * 22;
            step = Math.sin(t * Math.PI) * 28;
            this._hop--;
        }
        this.x = home.x - step;
        this.y = home.y;
        this._body.y = -lift;
        this.updateFrame();
    };

    Sprite_NovaPet.prototype.updateFrame = function() {
        var bmp = this._body.bitmap;
        if (!bmp || !bmp.isReady()) return;
        var pw = bmp.width / (this._bigSheet ? 3 : 12);
        var ph = bmp.height / (this._bigSheet ? 4 : 8);
        var index = this._bigSheet ? 0 : this._charIndex;
        var pattern = [0, 1, 2, 1][Math.floor(this._tick / 12) % 4];
        var dirRow = 1;  // facing left
        var sx = ((index % 4) * 3 + pattern) * pw;
        var sy = (Math.floor(index / 4) * 4 + dirRow) * ph;
        this._body.setFrame(sx, sy, pw, ph);
    };

    var _Spriteset_Battle_createActors = Spriteset_Battle.prototype.createActors;
    Spriteset_Battle.prototype.createActors = function() {
        _Spriteset_Battle_createActors.call(this);
        this._novaPetSprite = new Sprite_NovaPet();
        this._battleField.addChild(this._novaPetSprite);
    };

    //=========================================================================
    // Main menu command
    //=========================================================================
    var _Window_MenuCommand_addOriginalCommands = Window_MenuCommand.prototype.addOriginalCommands;
    Window_MenuCommand.prototype.addOriginalCommands = function() {
        _Window_MenuCommand_addOriginalCommands.call(this);
        this.addCommand(MENU_NAME, 'novaPets', $gameParty.novaPets().length > 0);
    };

    var _Scene_Menu_createCommandWindow = Scene_Menu.prototype.createCommandWindow;
    Scene_Menu.prototype.createCommandWindow = function() {
        _Scene_Menu_createCommandWindow.call(this);
        this._commandWindow.setHandler('novaPets', function() { SceneManager.push(Scene_NovaPets); });
    };

    //=========================================================================
    // Pets screen
    //=========================================================================
    var HEADER_H = 64;

    function ctxOf(bitmap) { return bitmap._context || bitmap.context; }
    function dirty(bitmap) {
        if (bitmap._setDirty) bitmap._setDirty();
        else if (bitmap._baseTexture) bitmap._baseTexture.update();
    }

    // List of owned pets: OK makes the pet the active one (or sends it home).
    function Window_NovaPetList() { this.initialize.apply(this, arguments); }
    Window_NovaPetList.prototype = Object.create(Window_Selectable.prototype);
    Window_NovaPetList.prototype.constructor = Window_NovaPetList;

    Window_NovaPetList.prototype.initialize = function(x, y, w, h) {
        Window_Selectable.prototype.initialize.call(this, x, y, w, h);
        this.refresh();
        var active = $gameParty.novaActivePet();
        this.select(Math.max(0, active ? this.pets().indexOf(active) : 0));
        this.activate();
    };
    Window_NovaPetList.prototype.pets = function() { return $gameParty.novaPets(); };
    Window_NovaPetList.prototype.maxItems = function() { return this.pets().length; };
    Window_NovaPetList.prototype.itemHeight = function() { return 64; };
    Window_NovaPetList.prototype.pet = function() { return this.pets()[this.index()] || null; };
    Window_NovaPetList.prototype.playOkSound = function() {};   // the scene plays the pet's own sound

    Window_NovaPetList.prototype.drawItem = function(index) {
        var pet = this.pets()[index];
        if (!pet) return;
        var rect = this.itemRect(index);
        var isActive = pet === $gameParty.novaActivePet();
        var bmp = ImageManager.loadCharacter(pet.characterName());
        if (!bmp.isReady()) { bmp.addLoadListener(this.refresh.bind(this)); return; }
        this.drawCharacter(pet.characterName(), pet.characterIndex(), rect.x + 30, rect.y + rect.height - 8);
        this.resetFontSettings();
        this.contents.fontSize = 22;
        this.changeTextColor('#ffffff');
        this.drawText(pet.name(), rect.x + 64, rect.y + 4, rect.width - 64, 'left');
        this.contents.fontSize = 15;
        this.changeTextColor(isActive ? COLOR.active : COLOR.dim);
        this.drawText(isActive ? 'With you' : 'At home', rect.x + 64, rect.y + 30, rect.width - 64, 'left');
        this.resetFontSettings();
    };

    // Details of the selected pet.
    function Window_NovaPetInfo() { this.initialize.apply(this, arguments); }
    Window_NovaPetInfo.prototype = Object.create(Window_Base.prototype);
    Window_NovaPetInfo.prototype.constructor = Window_NovaPetInfo;

    Window_NovaPetInfo.prototype.initialize = function(x, y, w, h) {
        Window_Base.prototype.initialize.call(this, x, y, w, h);
        this._pet = null;
    };

    Window_NovaPetInfo.prototype.setPet = function(pet) {
        if (this._pet === pet) return;
        this._pet = pet;
        this.refresh();
    };

    Window_NovaPetInfo.prototype.drawDivider = function(y) {
        var ctx = ctxOf(this.contents), w = this.contentsWidth();
        var g = ctx.createLinearGradient(0, 0, w, 0);
        g.addColorStop(0, 'rgba(98, 214, 255, 0.55)');
        g.addColorStop(1, 'rgba(98, 214, 255, 0)');
        ctx.fillStyle = g;
        ctx.fillRect(0, y, w, 1.5);
        dirty(this.contents);
    };

    Window_NovaPetInfo.prototype.refresh = function() {
        this.contents.clear();
        var pet = this._pet;
        if (!pet) return;
        NovaPets.syncLevel(pet);
        var w = this.contentsWidth(), textW = w - 200;
        var isActive = pet === $gameParty.novaActivePet();
        this.contents.fontSize = 40;
        this.changeTextColor('#ffffff');
        this.drawText(pet.name(), 4, 0, textW, 'left');
        this.contents.fontSize = 18;
        this.changeTextColor(COLOR.accent);
        this.drawText(pet.nickname(), 6, 50, textW, 'left');
        this.changeTextColor(isActive ? COLOR.active : COLOR.dim);
        this.drawText(isActive ? 'Walking with you' : 'Waiting at home', 6, 78, textW, 'left');

        var y = 124;
        this.contents.fontSize = 18;
        this.changeTextColor(COLOR.dim);
        this.drawText(TextManager.levelA, 6, y, 80, 'left');
        this.drawText('Helps in battle', w / 2, y, w / 2 - 6, 'left');
        this.changeTextColor('#ffffff');
        this.contents.fontSize = 24;
        this.drawText(pet.level, 60, y - 2, 100, 'left');
        this.drawText(NovaPets.assistChance(pet.actorId()) + '%', w / 2, y - 2, w / 2 - 10, 'right');
        this.contents.fontSize = 14;
        this.changeTextColor(COLOR.dim);
        this.drawText('Grows with your strongest hero', 6, y + 28, w / 2, 'left');
        this.drawText('chance each turn', w / 2, y + 28, w / 2 - 10, 'right');

        y += 64;
        this.drawDivider(y);
        y += 12;
        this.contents.fontSize = 16;
        this.changeTextColor(COLOR.accent);
        this.drawText('SKILLS', 6, y, 200, 'left');
        y += 34;
        NovaPets.skillList(pet.actorId()).forEach(function(entry) {
            var skill = $dataSkills[entry.skillId];
            var known = pet.level >= entry.level;
            this.changePaintOpacity(known);
            this.drawIcon(skill.iconIndex, 4, y);
            this.contents.fontSize = 20;
            this.changeTextColor('#ffffff');
            this.drawText(skill.name, 42, y - 2, w / 2, 'left');
            this.contents.fontSize = 15;
            this.changeTextColor(known ? COLOR.dim : COLOR.locked);
            var note = known ? skill.description : 'Learned at level ' + entry.level;
            this.drawText(note, 42, y + 22, w - 46, 'left');
            this.changePaintOpacity(true);
            y += 54;
        }, this);

        var bonus = NovaPets.passiveArmor(pet.actorId());
        if (bonus) {
            y += 4;
            this.drawDivider(y);
            y += 12;
            this.contents.fontSize = 16;
            this.changeTextColor(COLOR.accent);
            this.drawText('PARTY BONUS', 6, y, 300, 'left');
            this.contents.fontSize = 14;
            this.changeTextColor(COLOR.dim);
            this.drawText(isActive ? 'active now' : 'while walking with you', 160, y, w - 166, 'right');
            y += 34;
            this.contents.fontSize = 18;
            String(bonus.description || '').split('\n').forEach(function(line, i) {
                this.changeTextColor(i === 0 ? '#d6e8f7' : '#ffffff');
                this.drawText(line, 6, y, w - 12, 'left');
                y += 26;
            }, this);
        }

        y += 4;
        this.drawDivider(y);
        y += 14;
        this.contents.fontSize = 17;
        this.changeTextColor('#d6e8f7');
        String(pet.profile() || '').split('\n').forEach(function(line) {
            if (y + 26 > this.contentsHeight()) return;
            this.drawText(line, 6, y, w - 12, 'left');
            y += 26;
        }, this);
        this.resetFontSettings();
    };

    // A large walking pet in the top-right of the info panel.
    function Sprite_NovaPetPortrait() { this.initialize.apply(this, arguments); }
    Sprite_NovaPetPortrait.prototype = Object.create(Sprite.prototype);
    Sprite_NovaPetPortrait.prototype.constructor = Sprite_NovaPetPortrait;

    Sprite_NovaPetPortrait.prototype.initialize = function() {
        Sprite.prototype.initialize.call(this);
        this.anchor.x = 0.5;
        this.anchor.y = 1;
        this.scale.x = this.scale.y = 3;
        this._pet = null;
        this._tick = 0;
    };

    Sprite_NovaPetPortrait.prototype.setPet = function(pet) {
        if (this._pet === pet) return;
        this._pet = pet;
        this.bitmap = pet ? ImageManager.loadCharacter(pet.characterName()) : null;
        if (this.bitmap) this.bitmap.smooth = false;
    };

    Sprite_NovaPetPortrait.prototype.update = function() {
        Sprite.prototype.update.call(this);
        this._tick++;
        var pet = this._pet, bmp = this.bitmap;
        if (!pet || !bmp || !bmp.isReady()) return;
        var big = ImageManager.isBigCharacter(pet.characterName());
        var pw = bmp.width / (big ? 3 : 12), ph = bmp.height / (big ? 4 : 8);
        var index = big ? 0 : pet.characterIndex();
        var pattern = [0, 1, 2, 1][Math.floor(this._tick / 12) % 4];
        var dirRow = [0, 1, 3, 2][Math.floor(this._tick / 150) % 4];   // turns around now and then
        this.setFrame(((index % 4) * 3 + pattern) * pw, (Math.floor(index / 4) * 4 + dirRow) * ph, pw, ph);
    };

    function Scene_NovaPets() { this.initialize.apply(this, arguments); }
    Scene_NovaPets.prototype = Object.create(Scene_MenuBase.prototype);
    Scene_NovaPets.prototype.constructor = Scene_NovaPets;

    Scene_NovaPets.prototype.create = function() {
        Scene_MenuBase.prototype.create.call(this);
        var w = Graphics.boxWidth, h = Graphics.boxHeight;
        this.createHeader(w);
        var listW = Math.floor(w * 0.30);
        this._listWindow = new Window_NovaPetList(12, HEADER_H + 4, listW, h - HEADER_H - 16);
        this._listWindow.setHandler('ok', this.onPetOk.bind(this));
        this._listWindow.setHandler('cancel', this.popScene.bind(this));
        this.addWindow(this._listWindow);
        this._infoWindow = new Window_NovaPetInfo(listW + 20, HEADER_H + 4, w - listW - 32, h - HEADER_H - 16);
        this.addWindow(this._infoWindow);
        this._portrait = new Sprite_NovaPetPortrait();
        this._portrait.x = this._infoWindow.x + this._infoWindow.width - 110;
        this._portrait.y = this._infoWindow.y + 170;
        this.addChild(this._portrait);
    };

    Scene_NovaPets.prototype.createHeader = function(w) {
        var head = new Bitmap(w, HEADER_H), ctx = ctxOf(head);
        var g = ctx.createLinearGradient(0, 0, w, 0);
        g.addColorStop(0, 'rgba(98, 214, 255, 0.28)');
        g.addColorStop(0.45, 'rgba(98, 214, 255, 0.06)');
        g.addColorStop(1, 'rgba(98, 214, 255, 0)');
        ctx.fillStyle = g;
        ctx.fillRect(0, 0, w, HEADER_H);
        ctx.fillStyle = COLOR.accent;
        ctx.fillRect(16, HEADER_H - 8, w * 0.42, 2);
        dirty(head);
        head.fontSize = 34; head.textColor = '#eaf7ff'; head.outlineColor = 'rgba(0, 40, 80, 0.8)'; head.outlineWidth = 5;
        head.drawText(MENU_NAME.toUpperCase(), 24, 10, 400, 44, 'left');
        head.fontSize = 18; head.textColor = COLOR.dim; head.outlineWidth = 3;
        head.drawText('OK: take along / send home', w - 420, 18, 400, 30, 'right');
        this.addChild(new Sprite(head));
    };

    Scene_NovaPets.prototype.onPetOk = function() {
        var pet = this._listWindow.pet();
        if (pet) {
            var isActive = pet === $gameParty.novaActivePet();
            $gameParty.setNovaActivePet(isActive ? 0 : pet.actorId());
            if (isActive) SoundManager.playCancel();
            else this.playPetSound(pet);
        }
        this._listWindow.refresh();
        this._infoWindow._pet = null;
        this._listWindow.activate();
    };

    Scene_NovaPets.prototype.playPetSound = function(pet) {
        var name = pet.actor().meta['pet sound'];
        if (name && name !== true) AudioManager.playSe({ name: String(name).trim(), volume: 80, pitch: 100, pan: 0 });
        else SoundManager.playOk();
    };

    Scene_NovaPets.prototype.update = function() {
        Scene_MenuBase.prototype.update.call(this);
        var pet = this._listWindow.pet();
        this._infoWindow.setPet(pet);
        this._portrait.setPet(pet);
    };

    window.Scene_NovaPets = Scene_NovaPets;
})();
