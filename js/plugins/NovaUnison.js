//=============================================================================
// NovaUnison.js
//=============================================================================
/*:
 * @plugindesc Unison skills: two or more heroes pay MP together for one
 * strong skill, and all of their ATB gauges start over.
 * @author Project Nova
 *
 * @help
 * Place below NovaBattle.
 *
 * Skill note tags
 *   <unison: 1, 3>     the heroes (actor IDs) who take part; whoever of
 *                      them uses it, the others are the partners
 *   <unison mp: 20>    MP each partner pays (default: the skill's MP cost);
 *                      the partner's MP Cost Rate applies, as for any skill
 *
 * Every hero in the list should learn the skill (Class > Learnings), so
 * any of them can start it. It can only be used in battle when every
 * partner is in the battle party, alive, able to move and has the MP.
 * The user pays the skill's normal costs, each partner pays its MP, and
 * the ATB gauges of all of them go back to zero.
 *
 * In the skill list a unison skill shows "+ <partner>" before its cost.
 *
 * In damage formulas, a.novaUnisonPartners() is the list of partners, e.g.
 *   300 + a.mat * 2.5 + a.novaUnisonPartners()[0].mat * 2.5 - b.mdf * 2
 */

(function() {
    'use strict';

    function unisonIds(skill) {
        if (!skill || !skill.meta || !skill.meta.unison) return null;
        return String(skill.meta.unison).split(',').map(Number).filter(function(n) { return n > 0; });
    }

    // like a skill's own MP cost, it follows the partner's MP Cost Rate
    function partnerMp(skill, partner) {
        var tag = skill.meta['unison mp'];
        return Math.floor((tag === undefined ? skill.mpCost : Number(tag) || 0) * partner.mcr);
    }

    Game_Actor.prototype.novaUnisonPartners = function(skill) {
        // in a damage formula: the action being carried out (already off the actor's list)
        var running = BattleManager._action;
        if (!skill && running && running.subject() === this) skill = running.item();
        if (!skill && this.currentAction()) skill = this.currentAction().item();
        var ids = unisonIds(skill);
        if (!ids) return [];
        var me = this.actorId();
        return ids.filter(function(id) { return id !== me; }).map(function(id) { return $gameActors.actor(id); });
    };

    Game_Actor.prototype.novaUnisonReady = function(skill) {
        if (!unisonIds(skill)) return true;
        if (!$gameParty.inBattle()) return false;
        return this.novaUnisonPartners(skill).every(function(p) {
            return p && p.isBattleMember() && p.isAlive() && p.canMove() && p.mp >= partnerMp(skill, p);
        });
    };

    var _meetsSkillConditions = Game_Actor.prototype.meetsSkillConditions;
    Game_Actor.prototype.meetsSkillConditions = function(skill) {
        return _meetsSkillConditions.call(this, skill) && this.novaUnisonReady(skill);
    };

    // The partners pay, strike a casting pose, and lose their ATB progress.
    var _paySkillCost = Game_Actor.prototype.paySkillCost;
    Game_Actor.prototype.paySkillCost = function(skill) {
        _paySkillCost.call(this, skill);
        if (!unisonIds(skill) || !$gameParty.inBattle()) return;
        this.novaUnisonPartners(skill).forEach(function(p) {
            p.gainMp(-partnerMp(skill, p));
            p.requestMotion('spell');
            p._novaAtb = 0;
            [BattleManager._novaInputQueue, BattleManager._novaActQueue].forEach(function(queue) {
                var i = queue ? queue.indexOf(p) : -1;
                if (i >= 0) queue.splice(i, 1);
            });
            if (p.isInputting()) p.setActionState('undecided');
        });
        BattleManager.refreshStatus();
    };

    // In the skill list: "+ Mira" before the cost, so it is clear whose MP it takes too.
    var _drawItem = Window_SkillList.prototype.drawItem;
    Window_SkillList.prototype.drawItem = function(index) {
        _drawItem.call(this, index);
        var skill = this._data[index], UI = window.NovaUI;
        if (!this._actor || !unisonIds(skill)) return;
        var rect = this.itemRect(index);
        var names = this._actor.novaUnisonPartners(skill).map(function(p) { return p.name(); });
        this.changePaintOpacity(this.isEnabled(skill));
        if (UI) UI.titleFont(this.contents, 13);
        else this.contents.fontSize = 14;
        this.changeTextColor(UI ? UI.COLOR.accent : this.systemColor());
        this.contents.drawText('+ ' + names.join(' & '), rect.x, rect.y,
                               rect.width - this.textPadding() - this.costWidth() - 10, rect.height, 'right');
        this.resetFontSettings();
        this.changePaintOpacity(true);
    };

    // "Kael & Mira unleash Twilight Eclipse!"
    var _displayAction = Window_BattleLog.prototype.displayAction;
    Window_BattleLog.prototype.displayAction = function(subject, item) {
        var ids = subject.isActor() && DataManager.isSkill(item) ? unisonIds(item) : null;
        if (!ids) return _displayAction.call(this, subject, item);
        var names = [subject.name()].concat(subject.novaUnisonPartners(item).map(function(p) { return p.name(); }));
        this.push('addText', names.join(' & ') + ' unleash ' + item.name + '!');
    };
})();
