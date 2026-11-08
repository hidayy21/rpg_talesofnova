//=============================================================================
// NovaSkillChain.js
//=============================================================================
/*:
 * @plugindesc Skill chains: a skill that can only be used while its user
 * has a certain state, so skills must be used in the right order.
 * @author Project Nova
 *
 * @help
 * Skill note tag
 *   <require state: 43>      usable only while the user has state 43
 *   <require state: 38, 39>  ... one of these states
 *
 * Until then the skill shows greyed out in the list. To open a skill only
 * while a state lasts, give the state an "Add Skill" trait instead.
 *
 *   <sacrifice>              the user falls once the skill is over - every
 *                            state that would keep him standing is cleared
 */

(function() {
    'use strict';

    function requiredStates(skill) {
        var tag = skill && skill.meta && skill.meta['require state'];
        return tag ? String(tag).split(',').map(Number).filter(Boolean) : null;
    }

    function hasRequiredState(battler, skill) {
        var states = requiredStates(skill);
        return !states || states.some(function(id) { return battler.isStateAffected(id); });
    }

    // Game_Actor has its own meetsSkillConditions once NovaUnison is in, so both are wrapped
    [Game_BattlerBase, Game_Actor, Game_Enemy].forEach(function(cls) {
        if (!cls.prototype.hasOwnProperty('meetsSkillConditions')) return;
        var original = cls.prototype.meetsSkillConditions;
        cls.prototype.meetsSkillConditions = function(skill) {
            return original.call(this, skill) && hasRequiredState(this, skill);
        };
    });

    // ---------------------------------------------------------------- sacrifice
    var _useItem = Game_Battler.prototype.useItem;
    Game_Battler.prototype.useItem = function(item) {
        _useItem.call(this, item);
        if (DataManager.isSkill(item) && item.meta.sacrifice) this._novaSacrifice = true;
    };

    var _onAllActionsEnd = Game_Battler.prototype.onAllActionsEnd;
    Game_Battler.prototype.onAllActionsEnd = function() {
        _onAllActionsEnd.call(this);
        if (!this._novaSacrifice) return;
        this._novaSacrifice = false;
        if (this.isDead()) return;
        this.clearStates();                       // not even Hold the Ground keeps him up
        this.addState(this.deathStateId());
        var log = BattleManager._logWindow;
        if (log && this.isDead()) {
            var state = $dataStates[this.deathStateId()];
            log.push('addText', this.name() + (this.isActor() ? state.message1 : state.message2));
            log.push('performCollapse', this);
            log.push('wait');
        }
    };
})();
