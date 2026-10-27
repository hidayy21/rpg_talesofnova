//=============================================================================
// NovaFormation.js
//=============================================================================
/*:
 * @plugindesc Front and back row: the first two party slots stand in front,
 * the rest behind. Enemies aim at the front; the back row trades melee power
 * for safety; canes cast from the back.
 * @author Project Nova
 *
 * @param Front Target Weight
 * @type number
 * @desc How likely a front-row hero is picked by a single-target enemy attack, against Back Target Weight. 65/35 = 65% front with a 2/2 party.
 * @default 65
 *
 * @param Back Target Weight
 * @type number
 * @default 35
 *
 * @param Back Row Penalty
 * @type number
 * @max 100
 * @desc Percent less damage for melee attacks from the back row, and percent less physical damage taken there.
 * @default 40
 *
 * @param Ranged Weapon Types
 * @desc Weapon type ids that hit at full power from the back row (comma separated).
 * @default 5, 7, 8, 9
 *
 * @param Cane Weapon Types
 * @desc Weapon type ids whose Attack becomes a magic attack in the back row.
 * @default 6
 *
 * @param Magic Attack Skill
 * @type skill
 * @desc Skill used by the Attack command of a cane wielder in the back row.
 * @default 167
 *
 * @param Row Skill
 * @type skill
 * @desc Skill used by the Row command (swaps rows with the chosen ally).
 * @default 168
 *
 * @param Row Command
 * @desc Name of the battle command.
 * @default Row
 *
 * @help
 * Place below NovaMenu, NovaBattle and NovaPets.
 *
 * Rows
 *   Party slots 1-2 (Formation in the main menu) are the FRONT row, slots
 *   3-4 the BACK row. The menu cards show the row in big letters next to
 *   the level, the battle cards in a small tag. On the battlefield the two
 *   rows are parallel slanted lines, the front row closer to the enemies:
 *             F1 ------ B1        top lane:    slots 1 and 3
 *                 F2 ------ B2    bottom lane: slots 2 and 4
 *   The active pet (NovaPets) stands in the middle, between the rows.
 *
 * Front row
 *   Single-target and random enemy attacks pick a front-row hero more
 *   often (Front/Back Target Weight). Target Rate (Provoke, Allure) still
 *   multiplies on top, so a provoking hero stays the favourite.
 *
 * Back row
 *   - Melee physical attacks and skills deal 40% less damage
 *     (Bow, Crossbow, Gun and Whip are ranged: no penalty).
 *   - Physical damage taken is 40% lower. Magic is not affected.
 *   - A hero holding a cane attacks with magic instead (M.ATK against
 *     M.DEF, the Magic Attack Skill). The command is still "Attack":
 *     the row and the weapon decide which kind of hit it is.
 *
 * Row command
 *   Swaps rows with an ally in the other row and uses the turn. The swap
 *   lasts until the battle ends; after that the Formation order counts again.
 */

(function() {
    'use strict';

    var UI = window.NovaUI;
    var params = PluginManager.parameters('NovaFormation');
    function idList(text) {
        return String(text || '').split(',').map(Number).filter(function(n) { return n > 0; });
    }
    var FRONT_SLOTS = 2;
    var FRONT_WEIGHT = Number(params['Front Target Weight'] || 65);
    var BACK_WEIGHT = Number(params['Back Target Weight'] || 35);
    var BACK_RATE = 1 - Number(params['Back Row Penalty'] || 40) / 100;
    var RANGED = idList(params['Ranged Weapon Types'] || '5, 7, 8, 9');
    var CANES = idList(params['Cane Weapon Types'] || '6');
    var MAGIC_ATTACK = Number(params['Magic Attack Skill'] || 167);
    var ROW_SKILL = Number(params['Row Skill'] || 168);
    var ROW_NAME = String(params['Row Command'] || 'Row');
    // Battle spots in the default 816x624 layout (NovaResolution shifts them):
    // two lanes; each lane further down sits a little further right (depth)
    var FRONT_X = 548, BACK_X = 728, TOP_Y = 342, LANE_Y = 80, LANE_X = 40;
    var FRONT_RGB = [232, 149, 92], BACK_RGB = [143, 180, 217];
    var FRONT_COLOR = rgba(FRONT_RGB, 1), BACK_COLOR = rgba(BACK_RGB, 1);

    function rgba(rgb, a) { return 'rgba(' + rgb.join(', ') + ', ' + a + ')'; }

    //=========================================================================
    // Rows
    //=========================================================================
    Game_BattlerBase.prototype.isBackRow = function() { return false; };

    // _novaRow is only set by the Row command and only lasts for the battle.
    Game_Actor.prototype.isBackRow = function() {
        if (!this.isBattleMember()) return false;
        if (this._novaRow && $gameParty.inBattle()) return this._novaRow === 'back';
        return this.index() >= FRONT_SLOTS;
    };

    // Lane 0 = top, 1 = bottom: the order within the row in the Formation
    // (slot 1 and 3 on top, slot 2 and 4 below).
    // _novaLane, like _novaRow, is only set by the Row command for the battle.
    Game_Actor.prototype.novaLane = function() {
        if (this._novaLane != null && $gameParty.inBattle()) return this._novaLane;
        var index = this.index();
        return index < FRONT_SLOTS ? index : index - FRONT_SLOTS;
    };

    // The two heroes trade both their row and their lane on the battlefield.
    Game_Actor.prototype.novaSwapRow = function(other) {
        var myRow = this.isBackRow() ? 'back' : 'front', myLane = this.novaLane();
        this._novaRow = other.isBackRow() ? 'back' : 'front';
        this._novaLane = other.novaLane();
        other._novaRow = myRow;
        other._novaLane = myLane;
    };

    var _Game_Actor_onBattleEnd = Game_Actor.prototype.onBattleEnd;
    Game_Actor.prototype.onBattleEnd = function() {
        _Game_Actor_onBattleEnd.call(this);
        this._novaRow = null;
        this._novaLane = null;
    };

    Game_Actor.prototype.novaHasWeaponType = function(types) {
        return this.weapons().some(function(w) { return types.contains(w.wtypeId); });
    };

    Game_Actor.prototype.novaCanChangeRow = function() {
        return this.novaRowPartners().length > 0;
    };

    Game_Actor.prototype.novaRowPartners = function() {
        var back = this.isBackRow();
        return $gameParty.aliveMembers().filter(function(m) {
            return m !== this && m.isBackRow() !== back;
        }, this);
    };

    //=========================================================================
    // Enemies aim at the front row
    //=========================================================================
    function targetWeight(member) {
        return member.tgr * (member.isBackRow() ? BACK_WEIGHT : FRONT_WEIGHT);
    }

    Game_Party.prototype.randomTarget = function() {
        var members = this.aliveMembers();
        var rand = Math.random() * members.reduce(function(sum, m) { return sum + targetWeight(m); }, 0);
        var target = null;
        members.forEach(function(m) {
            rand -= targetWeight(m);
            if (rand <= 0 && !target) target = m;
        });
        return target;
    };

    //=========================================================================
    // Back row: weaker melee, less physical damage taken, canes cast
    //=========================================================================
    var _makeDamageValue = Game_Action.prototype.makeDamageValue;
    Game_Action.prototype.makeDamageValue = function(target, critical) {
        var value = _makeDamageValue.call(this, target, critical);
        if (value > 0 && this.isPhysical()) {
            var subject = this.subject();
            if (subject.isBackRow() && !subject.novaHasWeaponType(RANGED)) value *= BACK_RATE;
            if (target.isBackRow()) value *= BACK_RATE;
            value = Math.round(value);
        }
        return value;
    };

    var _attackSkillId = Game_Actor.prototype.attackSkillId;
    Game_Actor.prototype.attackSkillId = function() {
        if ($gameParty.inBattle() && $dataSkills[MAGIC_ATTACK] && this.isBackRow() &&
                this.novaHasWeaponType(CANES)) {
            return MAGIC_ATTACK;
        }
        return _attackSkillId.call(this);
    };

    //=========================================================================
    // Row command
    //=========================================================================
    function isRowAction(action) {
        return !!action && action.item() === $dataSkills[ROW_SKILL];
    }

    var _applyItemUserEffect = Game_Action.prototype.applyItemUserEffect;
    Game_Action.prototype.applyItemUserEffect = function(target) {
        _applyItemUserEffect.call(this, target);
        var subject = this.subject();
        if (isRowAction(this) && subject.isActor() && target !== subject && target.isActor()) {
            subject.novaSwapRow(target);
            target.result().success = true;
            BattleManager.refreshStatus();
        }
    };

    var _addGuardCommand = Window_ActorCommand.prototype.addGuardCommand;
    Window_ActorCommand.prototype.addGuardCommand = function() {
        _addGuardCommand.call(this);
        if ($dataSkills[ROW_SKILL]) this.addCommand(ROW_NAME, 'novaRow', this._actor.novaCanChangeRow());
    };

    var _createActorCommandWindow = Scene_Battle.prototype.createActorCommandWindow;
    Scene_Battle.prototype.createActorCommandWindow = function() {
        _createActorCommandWindow.call(this);
        this._actorCommandWindow.setHandler('novaRow', this.commandNovaRow.bind(this));
    };

    Scene_Battle.prototype.commandNovaRow = function() {
        var actor = BattleManager.actor();
        BattleManager.inputtingAction().setSkill(ROW_SKILL);
        this.selectActorSelection();
        var partner = actor.novaRowPartners()[0];
        if (partner) this._actorWindow.select(partner.index());
    };

    var _onActorCancel = Scene_Battle.prototype.onActorCancel;
    Scene_Battle.prototype.onActorCancel = function() {
        _onActorCancel.call(this);
        if (this._actorCommandWindow.currentSymbol() === 'novaRow') this._actorCommandWindow.activate();
    };

    // While picking a Row partner only allies in the other row can be chosen.
    var _isCurrentItemEnabled = Window_BattleActor.prototype.isCurrentItemEnabled;
    Window_BattleActor.prototype.isCurrentItemEnabled = function() {
        var actor = BattleManager.actor();
        if (actor && isRowAction(BattleManager.inputtingAction())) {
            return actor.novaRowPartners().contains($gameParty.battleMembers()[this.index()]);
        }
        return _isCurrentItemEnabled.call(this);
    };

    //=========================================================================
    // Battle sprites: two slanted rows, the front row closer to the enemies
    //=========================================================================
    var _setActorHome = Sprite_Actor.prototype.setActorHome;
    Sprite_Actor.prototype.setActorHome = function(index) {
        _setActorHome.call(this, index);
        if (!this._actor) return;   // NovaPets measures the default spots with a bare object
        // keep whatever offset NovaResolution added to the default spot (600 + 32i, 280 + 48i)
        var dx = this._homeX - (600 + index * 32), dy = this._homeY - (280 + index * 48);
        this._novaBack = this._actor.isBackRow();
        this._novaLaneShown = this._actor.novaLane();
        var lane = this._novaLaneShown;
        this.setHome((this._novaBack ? BACK_X : FRONT_X) + lane * LANE_X + dx, TOP_Y + lane * LANE_Y + dy);
    };

    // The active pet stands in the middle, between the rows and between the lanes:
    //   F1 ---- B1
    //        P
    //       F2 ---- B2
    if (window.Sprite_NovaPet) {
        Sprite_NovaPet.prototype.homePosition = function() {
            var spot = { setHome: function(x, y) { this._homeX = x; this._homeY = y; } };
            Sprite_Actor.prototype.setActorHome.call(spot, 0);   // default spot 0 + NovaResolution's offset
            var dx = spot._homeX - 600, dy = spot._homeY - 280;
            return { x: (FRONT_X + BACK_X + LANE_X) / 2 + dx, y: TOP_Y + LANE_Y / 2 + 4 + dy };
        };
    }

    // After a row swap, walk from the old spot to the new one.
    var _Sprite_Actor_update = Sprite_Actor.prototype.update;
    Sprite_Actor.prototype.update = function() {
        _Sprite_Actor_update.call(this);
        var actor = this._actor;
        if (actor && this._novaBack !== undefined &&
                (actor.isBackRow() !== this._novaBack || actor.novaLane() !== this._novaLaneShown)) {
            var oldX = this._homeX, oldY = this._homeY;
            this.setActorHome(this._actor.index());
            this._offsetX += oldX - this._homeX;
            this._offsetY += oldY - this._homeY;
        }
    };

    //=========================================================================
    // Row on the battle cards (small tag) and the main menu cards (big text)
    //=========================================================================
    var _novaDrawInfo = Window_BattleStatus.prototype.novaDrawInfo;
    Window_BattleStatus.prototype.novaDrawInfo = function(actor, rect) {
        _novaDrawInfo.call(this, actor, rect);
        if (!actor.isBattleMember()) return;
        var col = this.novaInfoColumn(rect), back = actor.isBackRow();
        UI.titleFont(this.contents, 11);
        this.changeTextColor(back ? BACK_COLOR : FRONT_COLOR);
        this.contents.drawText(back ? 'BACK' : 'FRONT', col.x + col.width - 60, rect.y + 6, 60, 18, 'right');
        this.resetFontSettings();
    };

    var _drawCardInfo = Window_NovaMenuStatus.prototype.drawCardInfo;
    Window_NovaMenuStatus.prototype.drawCardInfo = function(actor, rect) {
        _drawCardInfo.call(this, actor, rect);
        if (!actor.isBattleMember()) return;
        // big, on the Level line (right side) - the bottom of the card is the walking sprite's
        var back = actor.isBackRow(), rgb = back ? BACK_RGB : FRONT_RGB;
        var x = rect.x + 12, w = rect.width - 24, y = rect.y + this.portraitHeight(rect) - 40;
        UI.titleFont(this.contents, 25);
        this.contents.outlineColor = 'rgba(0, 0, 0, 0.85)';
        this.contents.outlineWidth = 4;
        this.changeTextColor(rgba(rgb, 1));
        this.contents.drawText(back ? 'BACK' : 'FRONT', x, y, w, 40, 'right');
        this.resetFontSettings();
    };
})();
