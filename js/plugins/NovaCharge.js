//=============================================================================
// NovaCharge.js
//=============================================================================
/*:
 * @plugindesc Charged enemy attacks: an enemy announces its big skill, winds
 * it up while its ATB gauge fills again, then lets it loose - unless the
 * party Breaks it first.
 * @author Project Nova
 *
 * @param Charge Time
 * @type number
 * @min 10
 * @max 100
 * @desc Percent of a full ATB gauge the wind-up takes (enemy note <charge time: N> overrides).
 * @default 55
 *
 * @param Charged Damage
 * @type number
 * @desc Percent damage of a charged skill that goes off.
 * @default 150
 *
 * @param Exposed Guard Damage
 * @type number
 * @desc Extra Guard a weakness hit takes from an enemy that is charging.
 * @default 1
 *
 * @param Charge Animation
 * @type animation
 * @desc Played on the enemy when it starts charging.
 * @default 51
 *
 * @param Charge Text
 * @desc Battle log when the charge starts. %1 = enemy, %2 = skill.
 * @default %1 is gathering power for %2!
 *
 * @param Interrupt Text
 * @desc Battle log when a Break stops the charge. %1 = enemy, %2 = skill.
 * @default %1's %2 was broken off!
 *
 * @help
 * Place below NovaBattle, NovaBreak and NovaSvEnemy.
 *
 * Enemy note tags
 *   <charge: Ground Pound, Horn Charge>   these skills are charged when this
 *                                         enemy uses them (skill names)
 *   <charge time: 70>                     wind-up length for this enemy
 *
 * Skill note tag
 *   <charge>       every enemy charges this skill (for enemy-only skills)
 *
 * How it plays
 *   When the enemy picks a charged skill it does not use it yet: the log
 *   says what is coming, a warning with the skill name, its target and a
 *   wind-up bar shows over the enemy, and its ATB gauge starts again from
 *   (100 - Charge Time)%. When the gauge is full the skill goes off on the
 *   same target (or another one if that hero has fallen) with Charged
 *   Damage.
 *   While charging the enemy is exposed: every weakness hit takes Exposed
 *   Guard Damage more Guard. If it is Broken - or put to sleep, stunned,
 *   paralysed, anything that stops it from acting - the charge is lost.
 *   Heroes and troop-event forced actions never charge.
 */

(function() {
    'use strict';

    var params = PluginManager.parameters('NovaCharge');
    var CHARGE_TIME = Number(params['Charge Time'] || 55) / 100;
    var CHARGE_RATE = Number(params['Charged Damage'] || 150) / 100;
    var EXPOSED = Number(params['Exposed Guard Damage'] || 0);
    var CHARGE_ANIM = Number(params['Charge Animation'] || 0);
    var CHARGE_TEXT = String(params['Charge Text'] || '%1 is gathering power for %2!');
    var INTERRUPT_TEXT = String(params['Interrupt Text'] || "%1's %2 was broken off!");
    var WARN = '#ff9a4a';

    var UI = window.NovaUI;

    //=========================================================================
    // Which skills an enemy charges
    //=========================================================================
    var chargeCache = {};
    function chargedNames(enemyId) {
        if (!chargeCache[enemyId]) {
            var tag = $dataEnemies[enemyId].meta.charge;
            chargeCache[enemyId] = typeof tag === 'string' ?
                tag.split(',').map(function(s) { return s.trim().toLowerCase(); }) : [];
        }
        return chargeCache[enemyId];
    }

    Game_Enemy.prototype.novaChargesSkill = function(skill) {
        return !!skill && (!!skill.meta.charge || chargedNames(this.enemyId()).contains(skill.name.toLowerCase()));
    };

    Game_Enemy.prototype.novaChargeTime = function() {
        var tag = this.enemy().meta['charge time'];
        return tag ? Math.min(1, Math.max(0.1, Number(tag) / 100)) : CHARGE_TIME;
    };

    Game_Enemy.prototype.novaCharge = function() { return this._novaCharge || null; };

    // 0..1: how far the wind-up has come.
    Game_Enemy.prototype.novaChargeRate = function() {
        var c = this._novaCharge;
        if (!c) return 0;
        return Math.min(1, Math.max(0, ((this._novaAtb || 0) - c.start) / Math.max(0.01, 1 - c.start)));
    };

    var _onBattleStart = Game_Battler.prototype.onBattleStart;
    Game_Battler.prototype.onBattleStart = function() {
        _onBattleStart.call(this);
        this._novaCharge = null;
    };

    function log(text) {
        var win = BattleManager._logWindow;
        if (!win) return;
        win.push('addText', text);
        win.push('wait');
    }

    Game_Enemy.prototype.novaLoseCharge = function(silent) {
        var c = this._novaCharge;
        if (!c) return;
        this._novaCharge = null;
        if (!silent && this.isAlive()) log(INTERRUPT_TEXT.format(this.name(), $dataSkills[c.skillId].name));
    };

    //=========================================================================
    // Starting and releasing a charge
    //=========================================================================
    var _processTurn = BattleManager.processTurn;
    BattleManager.processTurn = function() {
        var subject = this._subject, action = subject && subject.currentAction();
        if (subject && subject.isEnemy() && action && action.isSkill() && !action._novaCharged &&
                !action._forcing && !this.isForcedTurn() && subject.novaChargesSkill(action.item()) &&
                action.isValid()) {
            this.novaStartCharge(subject, action);
            return;
        }
        _processTurn.call(this);
    };

    BattleManager.novaStartCharge = function(enemy, action) {
        if (action.isForOpponent() && action.isForOne() && action._targetIndex < 0) action.decideRandomTarget();
        var target = action.isForOne() ? action.makeTargets()[0] : null;
        enemy._novaCharge = { skillId: action.item().id, targetIndex: action._targetIndex,
                              targetName: target ? target.name() : '', start: 1 - enemy.novaChargeTime() };
        enemy.clearActions();
        if (CHARGE_ANIM) enemy.startAnimation(CHARGE_ANIM, false, 0);
        enemy.requestEffect('whiten');
        log(CHARGE_TEXT.format(enemy.name(), action.item().name));
        this.novaFinishSubject(enemy);
        enemy._novaAtb = enemy._novaCharge.start;
    };

    var _startSubject = BattleManager.novaStartSubject;
    BattleManager.novaStartSubject = function(b, keepActions) {
        var c = b.isEnemy() && !keepActions ? b.novaCharge() : null;
        if (c) {
            b._novaCharge = null;
            if (b.canMove()) {
                var action = new Game_Action(b);
                action.setSkill(c.skillId);
                action.setTarget(c.targetIndex);
                action._novaCharged = true;
                b.clearActions();
                b._actions = [action];
                return _startSubject.call(this, b, true);
            }
        }
        _startSubject.call(this, b, keepActions);
    };

    // Anything that stops the enemy from acting loses the charge.
    var _addState = Game_Battler.prototype.addState;
    Game_Battler.prototype.addState = function(stateId) {
        _addState.call(this, stateId);
        if (this.isEnemy() && this._novaCharge && (!this.canMove() || this.isDead())) {
            this.novaLoseCharge(this.isDead());
        }
    };

    var _makeDamageValue = Game_Action.prototype.makeDamageValue;
    Game_Action.prototype.makeDamageValue = function(target, critical) {
        var value = _makeDamageValue.call(this, target, critical);
        return this._novaCharged ? Math.round(value * CHARGE_RATE) : value;
    };

    //=========================================================================
    // Exposed while charging: weakness hits take more Guard
    //=========================================================================
    var _apply = Game_Action.prototype.apply;
    Game_Action.prototype.apply = function(target) {
        var charging = target.isEnemy() && target._novaCharge && target.novaGuard;
        var before = charging ? target.novaGuard() : 0;
        _apply.call(this, target);
        if (!charging || !EXPOSED || !target._novaCharge || target.isDead() || target.novaIsBroken()) return;
        var after = target.novaGuard();
        if (after >= before || after <= 0) return;
        target._novaGuard = Math.max(0, after - EXPOSED);
        if (target._novaGuard === 0) target.novaBreak();
    };

    //=========================================================================
    // Warning over the enemy: skill name, target, wind-up bar
    //=========================================================================
    var LABEL_W = 240, LABEL_H = 50;

    function Sprite_NovaCharge() { this.initialize.apply(this, arguments); }
    Sprite_NovaCharge.prototype = Object.create(Sprite.prototype);
    Sprite_NovaCharge.prototype.constructor = Sprite_NovaCharge;

    Sprite_NovaCharge.prototype.initialize = function() {
        Sprite.prototype.initialize.call(this);
        this.bitmap = new Bitmap(LABEL_W, LABEL_H);
        this.anchor.x = 0.5;
        this.anchor.y = 0.5;
        this._battler = null;
        this._key = '';
        this._pulse = 0;
    };

    Sprite_NovaCharge.prototype.setup = function(battler) { this._battler = battler; };

    Sprite_NovaCharge.prototype.update = function() {
        Sprite.prototype.update.call(this);
        var b = this._battler, c = b && b.isAlive() ? b.novaCharge() : null;
        this.visible = !!c;
        if (!c) { this._key = ''; return; }
        var rate = b.novaChargeRate();
        var key = c.skillId + ':' + c.targetName + ':' + Math.floor(rate * 40);
        if (key !== this._key) {
            this._key = key;
            this.redraw(c, rate);
        }
        this._pulse = (this._pulse + 1) % 40;
        this.opacity = 190 + Math.round(65 * Math.sin(this._pulse / 40 * Math.PI * 2));
    };

    Sprite_NovaCharge.prototype.redraw = function(c, rate) {
        var b = this.bitmap, w = LABEL_W;
        b.clear();
        var ctx = b._context;
        if (ctx) {                                               // dark plate behind the text
            var g = ctx.createLinearGradient(0, 0, w, 0);
            g.addColorStop(0, 'rgba(20, 8, 4, 0)');
            g.addColorStop(0.2, 'rgba(20, 8, 4, 0.72)');
            g.addColorStop(0.8, 'rgba(20, 8, 4, 0.72)');
            g.addColorStop(1, 'rgba(20, 8, 4, 0)');
            ctx.fillStyle = g;
            ctx.fillRect(0, 2, w, LABEL_H - 4);
        }
        if (UI) UI.titleFont(b, 17); else b.fontSize = 17;
        b.outlineColor = 'rgba(0, 0, 0, 0.95)';
        b.outlineWidth = 4;
        b.textColor = WARN;
        var name = '⚠ ' + $dataSkills[c.skillId].name.toUpperCase();
        b.drawText(name, 0, 3, w, 22, 'center');
        if (UI) UI.bodyFont(b, 12); else b.fontSize = 12;
        b.textColor = '#ffffff';
        b.drawText(c.targetName ? '▸ ' + c.targetName : '▸ Party', 0, 23, w, 14, 'center');
        var bw = 130, bx = (w - bw) / 2, by = LABEL_H - 9;
        b.fillRect(bx - 1, by - 1, bw + 2, 5, 'rgba(0, 0, 0, 0.8)');
        b.gradientFillRect(bx, by, Math.round(bw * rate), 3, '#ffd27a', WARN);
        if (UI) UI.bodyFont(b);
        b._setDirty();
    };

    var _createStateIconSprite = Sprite_Enemy.prototype.createStateIconSprite;
    Sprite_Enemy.prototype.createStateIconSprite = function() {
        _createStateIconSprite.call(this);
        this._novaChargeSprite = new Sprite_NovaCharge();
        this.addChild(this._novaChargeSprite);
    };

    var _setBattler = Sprite_Enemy.prototype.setBattler;
    Sprite_Enemy.prototype.setBattler = function(battler) {
        _setBattler.call(this, battler);
        if (this._novaChargeSprite) this._novaChargeSprite.setup(battler);
    };

    var _updateStateSprite = Sprite_Enemy.prototype.updateStateSprite;
    Sprite_Enemy.prototype.updateStateSprite = function() {
        _updateStateSprite.call(this);
        var s = this._novaChargeSprite;
        if (!s) return;
        s.scale.x = this.scale.x < 0 ? -1 : 1;       // reads the right way round on mirrored side-view enemies
        s.y = -Math.round(Math.min(this.height * 0.5, 220));     // across the body: clear of the log and the plate
    };
})();
