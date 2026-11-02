//=============================================================================
// NovaSvEnemy.js
//=============================================================================
/*:
 * @plugindesc Enemies drawn with a side-view actor sheet (animated, mirrored to
 * face the party), and enemies whose stats follow an actor's level.
 * @author Project Nova
 *
 * @help
 * Place below NovaBattle and NovaBreak.
 *
 * Enemy note tags
 *   <sv actor: Actor4_2>   draw the enemy with img/sv_actors/Actor4_2.png:
 *                          it breathes, swings, casts, flinches and falls
 *                          like a party member, mirrored to face right.
 *                          Keep an existing image as the enemy's own battler
 *                          (the Database and the bestiary still use it).
 *   <as class: 2>          with <match level>: the enemy's base stats are
 *   <match level: 1>       this class's stats at actor 1's current level
 *                          (a duel against a future party member, say).
 *
 * The motions follow RPG Maker's own actor rules: attack = swing, magic =
 * spell, other skills = skill, items = item, hit = damage, dodge = evade;
 * at rest it waits, guards, or kneels below 25% HP.
 */

(function() {
    'use strict';

    function tag(enemy, name) {
        var m = enemy.enemy().note.match(new RegExp('<' + name + ':\\s*([^>]+)>', 'i'));
        return m ? m[1].trim() : '';
    }

    // ---------------------------------------------------------------- stats from an actor's level
    var _paramBase = Game_Enemy.prototype.paramBase;
    Game_Enemy.prototype.paramBase = function(paramId) {
        var cls = $dataClasses[Number(tag(this, 'as class'))];
        var actor = $gameActors.actor(Number(tag(this, 'match level')));
        if (cls && actor) return cls.params[paramId][actor.level];
        return _paramBase.call(this, paramId);
    };

    // ---------------------------------------------------------------- motions
    Game_Enemy.prototype.novaSvActor = function() {
        if (this._novaSvActor === undefined) this._novaSvActor = tag(this, 'sv actor');
        return this._novaSvActor;
    };

    var _performAction = Game_Enemy.prototype.performAction;
    Game_Enemy.prototype.performAction = function(action) {
        _performAction.call(this, action);
        if (!this.novaSvActor()) return;
        if (action.isAttack()) this.requestMotion('swing');
        else if (action.isMagicSkill()) this.requestMotion('spell');
        else if (action.isSkill()) this.requestMotion('skill');
        else if (action.isItem()) this.requestMotion('item');
    };

    var _performDamage = Game_Enemy.prototype.performDamage;
    Game_Enemy.prototype.performDamage = function() {
        _performDamage.call(this);
        if (this.novaSvActor()) this.requestMotion('damage');
    };

    var _performEvasion = Game_Enemy.prototype.performEvasion;
    Game_Enemy.prototype.performEvasion = function() {
        _performEvasion.call(this);
        if (this.novaSvActor()) this.requestMotion('evade');
    };

    var _performMagicEvasion = Game_Enemy.prototype.performMagicEvasion;
    Game_Enemy.prototype.performMagicEvasion = function() {
        _performMagicEvasion.call(this);
        if (this.novaSvActor()) this.requestMotion('evade');
    };

    // ---------------------------------------------------------------- the sprite
    var _loadBitmap = Sprite_Enemy.prototype.loadBitmap;
    Sprite_Enemy.prototype.loadBitmap = function(name, hue) {
        var sv = this._enemy.novaSvActor();
        this._novaSv = !!sv;
        this.scale.x = sv ? -1 : 1;
        this._novaMotion = null;
        if (sv) this.bitmap = ImageManager.loadSvActor(sv);
        else _loadBitmap.call(this, name, hue);
    };

    Sprite_Enemy.prototype.novaIdleMotion = function() {
        var e = this._enemy;
        if (e.isDead()) return 'dead';
        if (e.isGuard() || e.isGuardWaiting()) return 'guard';
        if (e.isDying()) return 'dying';
        return 'wait';
    };

    Sprite_Enemy.prototype.novaStartMotion = function(type) {
        var motion = Sprite_Actor.MOTIONS[type];
        if (this._novaMotion === motion) return;
        this._novaMotion = motion;
        this._novaPattern = 0;
        this._novaCount = 0;
    };

    Sprite_Enemy.prototype.novaUpdateMotion = function() {
        var e = this._enemy;
        if (e.isMotionRequested()) {
            this._novaMotion = null;
            this.novaStartMotion(e.motionType());
            e.clearMotion();
        }
        if (!this._novaMotion || this._novaMotion.loop) this.novaStartMotion(this.novaIdleMotion());
        if (++this._novaCount < 12) return;
        this._novaCount = 0;
        if (this._novaMotion.loop) this._novaPattern = (this._novaPattern + 1) % 4;
        else if (this._novaPattern < 2) this._novaPattern++;
        else this._novaMotion = null;
    };

    var _updateFrame = Sprite_Enemy.prototype.updateFrame;
    Sprite_Enemy.prototype.updateFrame = function() {
        if (!this._novaSv) return _updateFrame.call(this);
        Sprite_Battler.prototype.updateFrame.call(this);
        if (!this.bitmap.isReady()) return;
        this.novaUpdateMotion();
        var motion = this._novaMotion || Sprite_Actor.MOTIONS.wait;
        var cw = this.bitmap.width / 9, ch = this.bitmap.height / 6;
        var pattern = this._novaPattern < 3 ? this._novaPattern : 1;
        var cx = Math.floor(motion.index / 6) * 3 + pattern, cy = motion.index % 6;
        var h = this._effectType === 'bossCollapse' ? Math.min(ch, this._effectDuration) : ch;
        this.setFrame(cx * cw, cy * ch, cw, h);
    };

    var _updateStateSprite = Sprite_Enemy.prototype.updateStateSprite;
    Sprite_Enemy.prototype.updateStateSprite = function() {
        _updateStateSprite.call(this);
        this._stateIconSprite.scale.x = this.scale.x;      // the state row reads the right way round
        if (this._novaSv) this._stateIconSprite.y = -Math.round((this.height + 40) * 0.9);
    };
})();
