//=============================================================================
// NovaBreak.js
//=============================================================================
/*:
 * @plugindesc Guard and Break: hitting an enemy's weakness wears down its
 * Guard; at zero it is Broken. TP comes from playing well and powers Empower.
 * @author Project Nova
 *
 * @param Default Guard
 * @type number
 * @desc Guard of an enemy without a <guard: N> tag. 0 = cannot be broken.
 * @default 3
 *
 * @param Broken State
 * @type state
 * @desc State added on Break (cannot act, takes more damage, lasts until its next turn).
 * @default 35
 *
 * @param Weakness TP
 * @type number
 * @desc TP the attacker gains for each hit on a weakness.
 * @default 8
 *
 * @param Break TP
 * @type number
 * @desc TP the attacker gains for breaking an enemy.
 * @default 25
 *
 * @param Damage TP Rate
 * @type number
 * @desc Percent of RPG Maker's usual TP for taking damage.
 * @default 50
 *
 * @param Empower Name
 * @desc Battle command name.
 * @default Empower
 *
 * @param Empowered Label
 * @desc Command name while the next action is empowered.
 * @default Empowered
 *
 * @param Empower Cost
 * @type number
 * @default 25
 *
 * @param Empower Rate
 * @type number
 * @desc Percent damage / healing of an empowered action.
 * @default 150
 *
 * @param Break Animation
 * @type animation
 * @default 21
 *
 * @param Empower Animation
 * @type animation
 * @default 52
 *
 * @param Weakness Critical
 * @type boolean
 * @desc Every hit on an enemy's weakness is a critical hit (spells too).
 * @default true
 *
 * @param Critical Damage
 * @type number
 * @desc Damage of a critical hit in percent (RPG Maker's own is 300). Counts for every critical.
 * @default 150
 *
 * @param Critical Text
 * @desc Shown over the damage number of a critical hit. Empty: none.
 * @default CRITICAL!
 *
 * @help
 * Place below NovaMenu, NovaBattle and NovaFormation.
 *
 * Enemy note tags
 *   <guard: 5>          Guard points (otherwise "Default Guard")
 *   <weak: Fire, Bow>   weaknesses: element names and weapon type names
 *                       from the Database (Types tab), comma separated
 *   Elements the enemy takes more than 100% damage from (Traits) count as
 *   weaknesses too.
 *
 * Guard and Break
 *   A plate under each enemy shows its HP (a bar, no numbers), its Guard
 *   and its weaknesses. Over its head every state, buff and debuff shows at
 *   once, with the turns left. Weaknesses
 *   show as "?" until the party has hit them once (remembered in the save).
 *   Every hit on a weakness takes 1 Guard (2 when empowered) and gives the
 *   attacker TP. At 0 Guard the enemy is Broken: its ATB gauge drops to
 *   zero, it skips its next turn and takes 50% more damage (the Broken
 *   state's traits). When that turn has passed its Guard is full again.
 *   Weapon type weaknesses count for physical actions of the hero holding
 *   the weapon. A skill whose formula picks the target's weakest element
 *   (Math.max(b.elementRate(2), b.elementRate(9)) ...) hits with each
 *   element it names, so it breaks a target weak to any of them.
 *
 * TP
 *   Heroes gain TP by hitting weaknesses and breaking enemies; taking
 *   damage gives less TP than usual (Damage TP Rate).
 *
 * Empower
 *   Battle command, costs 25 TP and does not use the turn: the hero's next
 *   action deals 50% more damage or healing (and takes 2 Guard per hit).
 *   The TP comes back if the turn is passed on, or the battle ends first.
 *
 * Critical hits
 *   A hit on a weakness is always critical, physical or magic (Weakness
 *   Critical). A critical hit does 150% damage instead of RPG Maker's 300%
 *   (Critical Damage) and shows "CRITICAL!" over its number. Ordinary
 *   critical hits (the CRI rate, skills with Critical on) still happen too.
 */

(function() {
    'use strict';

    var UI = window.NovaUI;
    if (!UI) {
        console.warn('NovaBreak: NovaMenu must be ON and placed above NovaBreak.');
        return;
    }

    var params = PluginManager.parameters('NovaBreak');
    var DEFAULT_GUARD = Number(params['Default Guard'] || 3);
    var BROKEN = Number(params['Broken State'] || 35);
    var WEAK_TP = Number(params['Weakness TP'] || 8);
    var BREAK_TP = Number(params['Break TP'] || 25);
    var DAMAGE_TP_RATE = Number(params['Damage TP Rate'] || 50) / 100;
    var EMPOWER_NAME = String(params['Empower Name'] || 'Empower');
    var EMPOWERED_LABEL = String(params['Empowered Label'] || 'Empowered');
    var EMPOWER_COST = Number(params['Empower Cost'] || 25);
    var EMPOWER_RATE = Number(params['Empower Rate'] || 150) / 100;
    var BREAK_ANIM = Number(params['Break Animation'] || 21);
    var EMPOWER_ANIM = Number(params['Empower Animation'] || 52);
    var WEAK_CRITICAL = String(params['Weakness Critical'] || 'true') === 'true';
    var CRIT_RATE = Number(params['Critical Damage'] || 150) / 100;
    var CRIT_TEXT = params['Critical Text'] === undefined ? 'CRITICAL!' : String(params['Critical Text']);

    var COLOR = UI.COLOR, ctxOf = UI.ctxOf, dirty = UI.dirty, pathPoly = UI.pathPoly;
    var BREAK_COLOR = '#ff7088';
    // IconSet icons for the elements (Physical, Fire ... Darkness, Void)
    var ELEMENT_ICONS = { 1: 76, 2: 64, 3: 65, 4: 66, 5: 67, 6: 68, 7: 69, 8: 70, 9: 71, 10: 72 };

    //=========================================================================
    // Weaknesses: keys 'e<elementId>' and 'w<weaponTypeId>'
    //=========================================================================
    function findIndex(list, name) {
        name = name.trim().toLowerCase();
        for (var i = 1; i < list.length; i++) {
            if (list[i] && list[i].toLowerCase() === name) return i;
        }
        return 0;
    }

    var weakCache = {};
    function weaknessesOf(enemyId) {
        if (weakCache[enemyId]) return weakCache[enemyId];
        var data = $dataEnemies[enemyId], keys = [];
        data.traits.forEach(function(t) {
            if (t.code === Game_BattlerBase.TRAIT_ELEMENT_RATE && t.value > 1) keys.push('e' + t.dataId);
        });
        String(data.meta.weak || '').split(',').forEach(function(name) {
            if (!name.trim()) return;
            var e = findIndex($dataSystem.elements, name), w = findIndex($dataSystem.weaponTypes, name);
            if (e) keys.push('e' + e);
            else if (w) keys.push('w' + w);
            else console.warn('NovaBreak: unknown weakness "' + name.trim() + '" on enemy ' + enemyId);
        });
        keys = keys.filter(function(k, i) { return keys.indexOf(k) === i; });
        return (weakCache[enemyId] = keys);
    }

    function weaponTypeIcon(wtypeId) {
        for (var i = 1; i < $dataWeapons.length; i++) {
            if ($dataWeapons[i] && $dataWeapons[i].wtypeId === wtypeId) return $dataWeapons[i].iconIndex;
        }
        return 95 + wtypeId;
    }

    function iconOf(key) {
        var id = Number(key.slice(1));
        return key[0] === 'e' ? (ELEMENT_ICONS[id] || 72) : weaponTypeIcon(id);
    }

    // What an action hits with: its element(s) and, for a hero's physical action, the weapon types.
    // A formula that picks the target's weakest element, like
    //   ... * Math.max(b.elementRate(8), b.elementRate(9))
    // hits with every element it names.
    function hitKeys(action) {
        var subject = action.subject(), item = action.item(), keys = [];
        var elementId = item.damage.elementId;
        if (elementId < 0) {
            subject.attackElements().forEach(function(id) { keys.push('e' + id); });
        } else if (elementId > 0) {
            keys.push('e' + elementId);
        }
        var re = /b\.elementRate\((\d+)\)/g, m;
        while ((m = re.exec(item.damage.formula))) keys.push('e' + m[1]);
        if (subject.isActor() && action.isPhysical()) {
            subject.weapons().forEach(function(w) { keys.push('w' + w.wtypeId); });
        }
        return keys;
    }

    Game_System.prototype.novaWeakSeen = function(enemyId, key) {
        var seen = this._novaWeakSeen = this._novaWeakSeen || {};
        return !!(seen[enemyId] && seen[enemyId][key]);
    };

    Game_System.prototype.novaRevealWeak = function(enemyId, key) {
        var seen = this._novaWeakSeen = this._novaWeakSeen || {};
        seen[enemyId] = seen[enemyId] || {};
        seen[enemyId][key] = true;
    };

    //=========================================================================
    // Guard
    //=========================================================================
    Game_Enemy.prototype.novaMaxGuard = function() {
        var tag = this.enemy().meta.guard;
        return tag === undefined ? DEFAULT_GUARD : Math.max(0, Number(tag) || 0);
    };

    Game_Enemy.prototype.novaGuard = function() {
        if (this._novaGuard === undefined) this._novaGuard = this.novaMaxGuard();
        return this._novaGuard;
    };

    Game_Enemy.prototype.novaIsBroken = function() {
        return this.isStateAffected(BROKEN);
    };

    // Guard comes back when the Broken state wears off.
    var _removeState = Game_Battler.prototype.removeState;
    Game_Battler.prototype.removeState = function(stateId) {
        var wasBroken = stateId === BROKEN && this.isStateAffected(BROKEN);
        _removeState.call(this, stateId);
        if (wasBroken && this.isEnemy()) this._novaGuard = this.novaMaxGuard();
    };

    Game_Enemy.prototype.novaBreak = function() {
        this._novaGuard = 0;
        this.addState(BROKEN);
        if (BREAK_ANIM) this.startAnimation(BREAK_ANIM, false, 0);
        // thrown back to the start of the ATB track
        this._novaAtb = 0;
        [BattleManager._novaActQueue, BattleManager._novaInputQueue].forEach(function(queue) {
            var i = queue ? queue.indexOf(this) : -1;
            if (i >= 0) queue.splice(i, 1);
        }, this);
    };

    var _apply = Game_Action.prototype.apply;
    Game_Action.prototype.apply = function(target) {
        _apply.call(this, target);
        if (!target.isEnemy() || !target.result().isHit() || !this.isHpEffect() || this.isRecover()) return;
        var weak = weaknessesOf(target.enemyId());
        var hits = hitKeys(this).filter(function(k) { return weak.contains(k); });
        if (hits.length === 0) return;
        hits.forEach(function(k) { $gameSystem.novaRevealWeak(target.enemyId(), k); });
        if (target.novaIsBroken() || target.novaMaxGuard() === 0 || target.isDead()) return;
        var subject = this.subject();
        target._novaGuard = Math.max(0, target.novaGuard() - (this._novaEmpowered ? 2 : 1));
        if (subject.isActor()) subject.gainSilentTp(WEAK_TP);
        if (target._novaGuard === 0) {
            target.novaBreak();
            if (subject.isActor()) subject.gainSilentTp(BREAK_TP);
        }
    };

    //=========================================================================
    // Critical hits: a weakness hit is always critical
    //=========================================================================
    Game_Action.prototype.novaHitsWeakness = function(target) {
        if (!target.isEnemy() || !this.isHpEffect() || this.isRecover()) return false;
        var weak = weaknessesOf(target.enemyId());
        return hitKeys(this).some(function(k) { return weak.contains(k); });
    };

    var _itemCri = Game_Action.prototype.itemCri;
    Game_Action.prototype.itemCri = function(target) {
        if (WEAK_CRITICAL && this.novaHitsWeakness(target)) return 1;
        return _itemCri.call(this, target);
    };

    Game_Action.prototype.applyCritical = function(damage) {
        return damage * CRIT_RATE;
    };

    // "CRITICAL!" over the number; it stays put while the digits bounce.
    var _setupCriticalEffect = Sprite_Damage.prototype.setupCriticalEffect;
    Sprite_Damage.prototype.setupCriticalEffect = function() {
        _setupCriticalEffect.call(this);
        if (!CRIT_TEXT) return;
        var bmp = new Bitmap(200, 32);
        UI.titleFont(bmp, 20);
        bmp.textColor = '#ffe08a';
        bmp.outlineColor = 'rgba(70, 12, 18, 0.95)';
        bmp.outlineWidth = 4;
        bmp.drawText(CRIT_TEXT, 0, 0, 200, 32, 'center');
        var label = new Sprite(bmp);
        label.anchor.x = 0.5;
        label.anchor.y = 1;
        label.y = -this.digitHeight() - 2;
        label._novaCritLabel = true;
        this.addChild(label);
    };

    var _updateChild = Sprite_Damage.prototype.updateChild;
    Sprite_Damage.prototype.updateChild = function(sprite) {
        if (!sprite._novaCritLabel) _updateChild.call(this, sprite);
    };

    //=========================================================================
    // TP
    //=========================================================================
    Game_Battler.prototype.chargeTpByDamage = function(damageRate) {
        this.gainSilentTp(Math.floor(50 * damageRate * this.tcr * DAMAGE_TP_RATE));
    };

    //=========================================================================
    // Empower
    //=========================================================================
    Game_Actor.prototype.novaCanEmpower = function() {
        return !this._novaEmpower && this.tp >= EMPOWER_COST;
    };

    // Clearing the actions without acting (turn passed on, failed escape,
    // battle end) gives the TP back.
    var _clearActions = Game_Actor.prototype.clearActions;
    Game_Actor.prototype.clearActions = function() {
        if (this._novaEmpower) {
            this._novaEmpower = false;
            this.gainSilentTp(EMPOWER_COST);
        }
        _clearActions.call(this);
    };

    var _startAction = BattleManager.startAction;
    BattleManager.startAction = function() {
        var subject = this._subject, action = subject && subject.currentAction();
        if (action && subject._novaEmpower) {
            action._novaEmpowered = true;
            subject._novaEmpower = false;
        }
        _startAction.call(this);
    };

    var _makeDamageValue = Game_Action.prototype.makeDamageValue;
    Game_Action.prototype.makeDamageValue = function(target, critical) {
        var value = _makeDamageValue.call(this, target, critical);
        return this._novaEmpowered ? Math.round(value * EMPOWER_RATE) : value;
    };

    var _addSkillCommands = Window_ActorCommand.prototype.addSkillCommands;
    Window_ActorCommand.prototype.addSkillCommands = function() {
        _addSkillCommands.call(this);
        var name = this._actor._novaEmpower ? EMPOWERED_LABEL : EMPOWER_NAME;
        this.addCommand(name, 'novaEmpower', this._actor.novaCanEmpower());
    };

    var _createActorCommandWindow = Scene_Battle.prototype.createActorCommandWindow;
    Scene_Battle.prototype.createActorCommandWindow = function() {
        _createActorCommandWindow.call(this);
        this._actorCommandWindow.setHandler('novaEmpower', this.commandNovaEmpower.bind(this));
    };

    Scene_Battle.prototype.commandNovaEmpower = function() {
        var actor = BattleManager.actor();
        actor.gainSilentTp(-EMPOWER_COST);
        actor._novaEmpower = true;
        if (EMPOWER_ANIM) actor.startAnimation(EMPOWER_ANIM, false, 0);
        BattleManager.refreshStatus();
        this._actorCommandWindow.refresh();
        this._actorCommandWindow.activate();
    };

    //=========================================================================
    // Plate under each enemy: an HP bar (no numbers), then its Guard in a
    // diamond and its weaknesses
    //=========================================================================
    var PLATE_W = 240, PLATE_H = 44, ICON = 22, HP_W = 100;
    var ENEMY_HP = ['#ff8a8a', '#c0304a'];

    function Sprite_NovaGuard() { this.initialize.apply(this, arguments); }
    Sprite_NovaGuard.prototype = Object.create(Sprite.prototype);
    Sprite_NovaGuard.prototype.constructor = Sprite_NovaGuard;

    Sprite_NovaGuard.prototype.initialize = function(enemySprite) {
        Sprite.prototype.initialize.call(this);
        this._enemySprite = enemySprite;
        this._key = '';
        this.bitmap = new Bitmap(PLATE_W, PLATE_H);
        this.anchor.x = 0.5;
    };

    Sprite_NovaGuard.prototype.update = function() {
        Sprite.prototype.update.call(this);
        var sprite = this._enemySprite, enemy = sprite._enemy;
        this.visible = !!enemy && enemy.isAlive() && !enemy.isHidden() && sprite.opacity > 0 && $gameParty.inBattle();
        if (!this.visible) return;
        this.x = sprite.x;
        this.y = Math.min(sprite.y + 4, Graphics.boxHeight - 156 - PLATE_H - 2);   // stays above the party cards
        var weak = weaknessesOf(enemy.enemyId());
        var key = Math.ceil(enemy.hpRate() * HP_W) + '|' + enemy.novaGuard() + '|' + enemy.novaIsBroken() + '|' +
                  weak.map(function(k) { return $gameSystem.novaWeakSeen(enemy.enemyId(), k) ? k : '?'; }).join(',');
        if (key !== this._key) {
            this._key = key;
            this.redraw(enemy, weak);
        }
        this.opacity = enemy.novaIsBroken() ? 190 + Math.round(Math.sin(Graphics.frameCount / 6) * 60) : 255;
    };

    Sprite_NovaGuard.prototype.redraw = function(enemy, weak) {
        var b = this.bitmap, ctx = ctxOf(b), broken = enemy.novaIsBroken();
        b.clear();
        UI.drawBar(ctx, (PLATE_W - HP_W) / 2, 1, HP_W, 7, enemy.hpRate(), ENEMY_HP);
        dirty(b);
        if (enemy.novaMaxGuard() > 0) this.drawGuardRow(b, enemy, weak, broken, 12);
        UI.bodyFont(b);
    };

    Sprite_NovaGuard.prototype.drawGuardRow = function(b, enemy, weak, broken, top) {
        var ctx = ctxOf(b), rh = PLATE_H - top, cy = top + rh / 2;
        var rowW = broken ? 30 + 70 : 30 + weak.length * (ICON + 3);
        var x0 = Math.floor((PLATE_W - rowW) / 2);
        // guard diamond
        pathPoly(ctx, [[x0 + 14, top + 1], [x0 + 27, cy], [x0 + 14, PLATE_H - 1], [x0 + 1, cy]]);
        ctx.fillStyle = COLOR.ink;
        ctx.fill();
        ctx.lineWidth = 1.5;
        ctx.strokeStyle = broken ? BREAK_COLOR : COLOR.accent;
        ctx.stroke();
        dirty(b);
        b.outlineColor = 'rgba(0, 0, 0, 0.85)';
        b.outlineWidth = 3;
        UI.titleFont(b, 14);
        b.textColor = broken ? BREAK_COLOR : COLOR.text;
        b.drawText(broken ? '0' : enemy.novaGuard(), x0 + 1, top, 27, rh, 'center');
        if (broken) {
            b.textColor = '#ffb3be';
            b.drawText('BROKEN', x0 + 32, top, 70, rh, 'left');
            return;
        }
        var self = this;
        weak.forEach(function(k, i) {
            drawWeakIcon(b, enemy.enemyId(), k, x0 + 30 + i * (ICON + 3), cy - ICON / 2, ICON, function() { self._key = ''; });
        });
    };

    // A weakness in a small box: its icon once found, "?" before.
    function drawWeakIcon(b, enemyId, key, x, y, size, onLoad) {
        var ctx = ctxOf(b);
        ctx.fillStyle = 'rgba(11, 17, 32, 0.85)';
        ctx.fillRect(x, y, size, size);
        ctx.strokeStyle = 'rgba(156, 192, 236, 0.5)';
        ctx.lineWidth = 1;
        ctx.strokeRect(x + 0.5, y + 0.5, size - 1, size - 1);
        dirty(b);
        if ($gameSystem.novaWeakSeen(enemyId, key)) {
            var iconSet = ImageManager.loadSystem('IconSet');
            if (!iconSet.isReady()) { if (onLoad) iconSet.addLoadListener(onLoad); return; }
            var icon = iconOf(key), iw = Window_Base._iconWidth, ih = Window_Base._iconHeight;
            b.blt(iconSet, icon % 16 * iw, Math.floor(icon / 16) * ih, iw, ih, x + 1, y + 1, size - 2, size - 2);
        } else {
            UI.titleFont(b, Math.round(size * 0.6));
            b.textColor = COLOR.dim;
            b.outlineWidth = 3;
            b.drawText('?', x, y, size, size, 'center');
        }
    }

    var _createEnemies = Spriteset_Battle.prototype.createEnemies;
    Spriteset_Battle.prototype.createEnemies = function() {
        _createEnemies.call(this);
        this._novaGuardPlates = this._enemySprites.map(function(sprite) {
            var plate = new Sprite_NovaGuard(sprite);
            this._battleField.addChild(plate);
            return plate;
        }, this);
    };

    //=========================================================================
    // Over each enemy's head: every state, buff and debuff at once, with the
    // turns left (instead of RPG Maker's single icon that cycles)
    //=========================================================================
    var ROW_MAX = 6, ROW_ICON = 24;

    function Sprite_NovaStateRow() { this.initialize.apply(this, arguments); }
    Sprite_NovaStateRow.prototype = Object.create(Sprite.prototype);
    Sprite_NovaStateRow.prototype.constructor = Sprite_NovaStateRow;

    Sprite_NovaStateRow.prototype.initialize = function() {
        Sprite.prototype.initialize.call(this);
        this._battler = null;
        this._key = '';
        this.bitmap = new Bitmap(ROW_MAX * (ROW_ICON + 2), ROW_ICON + 2);
        this.anchor.x = 0.5;
        this.anchor.y = 0.5;
    };

    Sprite_NovaStateRow.prototype.setup = function(battler) {
        this._battler = battler;
        this._key = '';
    };

    function stateEntries(battler) {
        var list = [];
        battler.states().forEach(function(s) {
            if (s.iconIndex > 0) list.push({ icon: s.iconIndex, turns: s.autoRemovalTiming > 0 ? battler._stateTurns[s.id] : 0 });
        });
        for (var i = 0; i < battler._buffs.length; i++) {
            if (battler._buffs[i] !== 0) list.push({ icon: battler.buffIconIndex(battler._buffs[i], i), turns: battler._buffTurns[i] });
        }
        return list.slice(0, ROW_MAX);
    }

    Sprite_NovaStateRow.prototype.update = function() {
        Sprite.prototype.update.call(this);
        var battler = this._battler;
        var list = battler && battler.isAlive() ? stateEntries(battler) : [];
        var key = list.map(function(e) { return e.icon + ':' + e.turns; }).join(',');
        if (key !== this._key) {
            this._key = key;
            this.redraw(list);
        }
    };

    Sprite_NovaStateRow.prototype.redraw = function(list) {
        var b = this.bitmap, iconSet = ImageManager.loadSystem('IconSet');
        b.clear();
        if (!iconSet.isReady()) { iconSet.addLoadListener(function() { this._key = ''; }.bind(this)); return; }
        var iw = Window_Base._iconWidth, ih = Window_Base._iconHeight, step = ROW_ICON + 2;
        var x0 = Math.floor((b.width - list.length * step) / 2);
        UI.titleFont(b, 11);
        b.textColor = '#ffffff';
        b.outlineColor = 'rgba(0, 0, 0, 0.95)';
        b.outlineWidth = 3;
        list.forEach(function(e, i) {
            var x = x0 + i * step;
            b.blt(iconSet, e.icon % 16 * iw, Math.floor(e.icon / 16) * ih, iw, ih, x + 1, 1, ROW_ICON, ROW_ICON);
            if (e.turns > 0) b.drawText(e.turns, x, ROW_ICON - 12, ROW_ICON + 1, 14, 'right');
        });
        UI.bodyFont(b);
    };

    Sprite_Enemy.prototype.createStateIconSprite = function() {
        this._stateIconSprite = new Sprite_NovaStateRow();
        this.addChild(this._stateIconSprite);
    };

    // Shared with the Bestiary (NovaBestiary).
    window.NovaBreak = { weaknessesOf: weaknessesOf, iconOf: iconOf, drawWeakIcon: drawWeakIcon };
    window.Sprite_NovaGuard = Sprite_NovaGuard;
})();
