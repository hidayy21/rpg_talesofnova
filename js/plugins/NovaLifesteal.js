//=============================================================================
// NovaLifesteal.js
//=============================================================================
/*:
 * @plugindesc Lifesteal: physical hits heal the attacker for a share of the
 * damage dealt. Set with a note tag on actors, classes, gear, states, enemies.
 * @author Project Nova
 *
 * @help
 * Note tag (Actor, Class, Weapon, Armor, State or Enemy):
 *
 *   <lifesteal: 10>    physical HP damage heals the user for 10% of the
 *                      damage actually dealt
 *
 * Every tag the battler has adds up (class 10 + weapon 5 + state 25 = 40%).
 * Only physical hits count (normal attacks, counterattacks and physical
 * skills). Skills whose damage type is already "HP Drain" are skipped so
 * they don't drain twice.
 *
 * Used by the Succubus class (Lysandre).
 */

(function() {
    'use strict';

    function tagValue(obj) {
        if (!obj || !obj.meta || obj.meta.lifesteal === undefined) return 0;
        return Number(obj.meta.lifesteal) || 0;
    }

    Game_BattlerBase.prototype.lifestealRate = function() {
        return this.traitObjects().reduce(function(sum, obj) {
            return sum + tagValue(obj);
        }, 0) / 100;
    };

    var _executeHpDamage = Game_Action.prototype.executeHpDamage;
    Game_Action.prototype.executeHpDamage = function(target, value) {
        var dealt = Math.min(target.hp, value);
        _executeHpDamage.call(this, target, value);
        var subject = this.subject();
        if (dealt <= 0 || !this.isPhysical() || this.isDrain() || subject === target) return;
        var heal = Math.floor(dealt * subject.lifestealRate());
        if (heal > 0 && subject.isAlive()) {
            subject.clearResult();
            subject.gainHp(heal);
            subject.startDamagePopup();
        }
    };
})();
