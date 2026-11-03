//=============================================================================
// NovaImpact.js
//=============================================================================
/*:
 * @plugindesc Weight for big hits in battle: a short freeze (hit-stop),
 * screen shake and a flash on critical hits, Breaks and charged attacks.
 * @author Project Nova
 *
 * @param Critical Hit-Stop
 * @type number
 * @desc Frames the battle freezes on a critical hit (0 = none).
 * @default 4
 *
 * @param Critical Shake
 * @type number
 * @desc Shake power on a critical hit (0 = none).
 * @default 3
 *
 * @param Break Hit-Stop
 * @type number
 * @default 9
 *
 * @param Break Shake
 * @type number
 * @default 6
 *
 * @param Charged Hit-Stop
 * @type number
 * @desc For a charged enemy skill (NovaCharge) hitting the party.
 * @default 6
 *
 * @param Charged Shake
 * @type number
 * @default 7
 *
 * @help
 * Place below NovaBattle, NovaBreak and NovaCharge.
 *
 * A hit-stop holds the whole battle scene still for a few frames when the
 * hit lands, so it reads as heavy (real frames, whatever the battle speed).
 * Several hits in one action (an all-target skill) freeze only once.
 * The Option "Screen Shake" is not needed: the shake is the battle screen's own.
 */

(function() {
    'use strict';

    var params = PluginManager.parameters('NovaImpact');
    function num(name, def) { var v = params[name]; return v === undefined || v === '' ? def : Number(v); }
    var KIND = {
        crit: { stop: num('Critical Hit-Stop', 4), shake: num('Critical Shake', 3), flash: null },
        brk: { stop: num('Break Hit-Stop', 9), shake: num('Break Shake', 6), flash: [255, 220, 200, 120] },
        charged: { stop: num('Charged Hit-Stop', 6), shake: num('Charged Shake', 7), flash: [255, 120, 60, 90] }
    };
    var RANK = { crit: 1, charged: 2, brk: 3 };

    // The strongest impact of the current action wins; it plays once when the hit lands.
    BattleManager.novaImpact = function(kind) {
        if (!this._novaImpact || RANK[kind] > RANK[this._novaImpact]) this._novaImpact = kind;
    };

    BattleManager.novaTakeImpact = function() {
        var kind = this._novaImpact;
        this._novaImpact = null;
        return kind ? KIND[kind] : null;
    };

    var _apply = Game_Action.prototype.apply;
    Game_Action.prototype.apply = function(target) {
        _apply.call(this, target);
        var r = target.result();
        if (!$gameParty.inBattle() || !r.isHit() || r.hpDamage <= 0) return;
        if (this._novaCharged && target.isActor()) BattleManager.novaImpact('charged');
        else if (r.critical) BattleManager.novaImpact('crit');
    };

    if (Game_Enemy.prototype.novaBreak) {
        var _novaBreak = Game_Enemy.prototype.novaBreak;
        Game_Enemy.prototype.novaBreak = function() {
            _novaBreak.call(this);
            BattleManager.novaImpact('brk');
        };
    }

    var _update = Scene_Battle.prototype.update;
    Scene_Battle.prototype.update = function() {
        var hit = BattleManager.novaTakeImpact();
        if (hit) {
            if (hit.shake) $gameScreen.startShake(hit.shake, 9, Math.max(10, hit.stop * 2));
            if (hit.flash) $gameScreen.startFlash(hit.flash, 14);
            this._novaHitStop = Math.max(this._novaHitStop || 0, hit.stop);
        }
        if (this._novaHitStop > 0) {
            this._novaHitStop--;
            $gameScreen.update();          // the shake and flash carry on through the freeze
            if (this._spriteset) {
                this._spriteset.updateScreenSprites();
                this._spriteset.updatePosition();
            }
            return;
        }
        _update.call(this);
    };
})();
