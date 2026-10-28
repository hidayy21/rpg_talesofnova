//=============================================================================
// NovaBattleResult.js
//=============================================================================
/*:
 * @plugindesc Battle Result screen after a victory: EXP, Zen and items won,
 * then every hero's EXP bar filling up with what they earned.
 * @author Project Nova
 *
 * @param Title
 * @default BATTLE RESULT
 *
 * @param Exp Label
 * @default EXP Gained
 *
 * @param Gold Label
 * @default Zen Obtained
 *
 * @param Items Label
 * @default Items Obtained
 *
 * @param Party Title
 * @default PARTY
 *
 * @param Reserve Label
 * @desc Heading over the reserve members (they get EXP too).
 * @default RESERVE
 *
 * @param Level Up Text
 * @default LEVEL UP!
 *
 * @param Exp Icon
 * @type number
 * @default 189
 *
 * @param Items Icon
 * @type number
 * @default 210
 *
 * @param Level Up SE
 * @type file
 * @dir audio/se/
 * @require 1
 * @default Powerup
 *
 * @help
 * Place below NovaMenu and NovaBattle.
 *
 * Replaces the victory messages ("... was victorious!", "... EXP received!",
 * "... found!", level up lines) with one screen over the battlefield:
 *
 *   BATTLE RESULT                 PARTY
 *   EXP Gained       1200         Kael    Lv 5  LEVEL UP!     +1200 EXP
 *   Zen Obtained      340 Z       =========================-----------
 *   Items Obtained                Yuki    Lv 4                +1200 EXP
 *     Potion x2                   ===============---------------------
 *                                 RESERVE
 *                                 Diana   Lv 3                +1200 EXP
 *
 * The totals count up first, then every party member's EXP bar fills from
 * where it was to where it is now, wrapping round on every level gained.
 * Reserve members are listed too (with System > Reserve Members' EXP on
 * they get the same EXP). Skills learned on the way follow "LEVEL UP!".
 *
 * OK / click: the first press skips the counting, the next one closes the
 * screen and leaves the battle. The Zen amount uses the currency unit from
 * the Database (System > Currency).
 */

(function() {
    'use strict';

    var UI = window.NovaUI;
    if (!UI) {
        console.warn('NovaBattleResult: NovaMenu must be ON and placed above NovaBattleResult.');
        return;
    }

    var params = PluginManager.parameters('NovaBattleResult');
    var TITLE = String(params['Title'] || 'BATTLE RESULT');
    var EXP_LABEL = String(params['Exp Label'] || 'EXP Gained');
    var GOLD_LABEL = String(params['Gold Label'] || 'Zen Obtained');
    var ITEMS_LABEL = String(params['Items Label'] || 'Items Obtained');
    var PARTY_TITLE = String(params['Party Title'] || 'PARTY');
    var RESERVE_LABEL = String(params['Reserve Label'] || 'RESERVE');
    var LEVEL_UP = String(params['Level Up Text'] || 'LEVEL UP!');
    var EXP_ICON = Number(params['Exp Icon'] || 0);
    var ITEMS_ICON = Number(params['Items Icon'] || 0);
    var LEVEL_SE = String(params['Level Up SE'] || '');
    var GOLD_ICON = Number(PluginManager.parameters('NovaMenu')['Gold Icon'] || 208);

    var COLOR = UI.COLOR, ctxOf = UI.ctxOf, dirty = UI.dirty, pathPoly = UI.pathPoly, panelShape = UI.panelShape;

    var COUNT_FRAMES = 40;      // the totals count up
    var PARTY_DELAY = 50;       // EXP bars start after the totals
    var MAX_ITEM_LINES = 7;
    var REWARD_W = 500, PARTY_W = 560, GAP = 24, ROW_H = 44, RESERVE_H = 24, HEAD_H = 62;

    function easeOut(t) { return 1 - Math.pow(1 - Math.max(0, Math.min(1, t)), 3); }

    //=========================================================================
    // Rewards: replace the victory messages, remember the before/after
    //=========================================================================
    var _initMembers = BattleManager.initMembers;
    BattleManager.initMembers = function() {
        _initMembers.call(this);
        this._novaResult = null;
    };

    BattleManager.displayVictoryMessage = function() {};
    BattleManager.displayRewards = function() {};

    var _gainRewards = BattleManager.gainRewards;
    BattleManager.gainRewards = function() {
        // reserve members too: they get their share of EXP (System > Reserve Members' EXP)
        var before = $gameParty.allMembers().filter(function(actor) {
            return !(window.NovaPets && NovaPets.isPet(actor.actorId()));
        }).map(function(actor) {
            return { actor: actor, level: actor.level, exp: actor.currentExp(), skills: actor.skills().slice(),
                     reserve: !actor.isBattleMember() };
        });
        this._novaGaining = true;
        try {
            _gainRewards.call(this);
        } finally {
            this._novaGaining = false;
        }
        var rewards = this._rewards;
        this._novaResult = {
            exp: rewards.exp,
            gold: rewards.gold,
            items: groupItems(rewards.items),
            actors: before.map(function(b) {
                var a = b.actor;
                return { actor: a, fromLevel: b.level, fromExp: b.exp, toLevel: a.level, toExp: a.currentExp(),
                         learned: a.findNewSkills(b.skills), reserve: b.reserve };
            }),
            closed: false
        };
    };

    // Level ups show on the result screen, not in the message window.
    var _shouldDisplayLevelUp = Game_Actor.prototype.shouldDisplayLevelUp;
    Game_Actor.prototype.shouldDisplayLevelUp = function() {
        return BattleManager._novaGaining ? false : _shouldDisplayLevelUp.call(this);
    };

    // The battle ends once the result screen is closed.
    var _isBusy = BattleManager.isBusy;
    BattleManager.isBusy = function() {
        return _isBusy.call(this) || (this._phase === 'battleEnd' && !!this._novaResult && !this._novaResult.closed);
    };

    function groupItems(items) {
        var list = [];
        items.forEach(function(item) {
            var entry = list.filter(function(e) { return e.item === item; })[0];
            if (entry) entry.count++;
            else list.push({ item: item, count: 1 });
        });
        return list;
    }

    //=========================================================================
    // Drawing helpers
    //=========================================================================
    function drawPanel(bmp) {
        var w = bmp.width, h = bmp.height, ctx = ctxOf(bmp), c = 14;
        var g = ctx.createLinearGradient(0, 0, 0, h);
        g.addColorStop(0, COLOR.panelTop);
        g.addColorStop(1, COLOR.panelBottom);
        ctx.fillStyle = g;
        pathPoly(ctx, panelShape(1, 1, w - 2, h - 2, c));
        ctx.fill();
        ctx.lineWidth = 1.5;
        ctx.strokeStyle = COLOR.frame;
        pathPoly(ctx, panelShape(1, 1, w - 2, h - 2, c));
        ctx.stroke();
        ctx.lineWidth = 1;
        ctx.strokeStyle = COLOR.frameSoft;
        pathPoly(ctx, panelShape(4, 4, w - 8, h - 8, c - 3));
        ctx.stroke();
        UI.diamond(ctx, w / 2, 1.5, 4, COLOR.frame);
        UI.diamond(ctx, w / 2, h - 1.5, 4, COLOR.frame);
    }

    // Title in Cinzel with a fading steel-blue rule under it.
    function drawTitle(bmp, text) {
        var ctx = ctxOf(bmp), ly = HEAD_H - 12, lw = bmp.width - 48;
        var line = ctx.createLinearGradient(24, 0, 24 + lw, 0);
        line.addColorStop(0, COLOR.accent);
        line.addColorStop(1, 'rgba(156, 192, 236, 0)');
        ctx.fillStyle = line;
        ctx.fillRect(24, ly, lw, 1);
        UI.diamond(ctx, 24, ly + 0.5, 4, COLOR.accent);
        dirty(bmp);
        UI.titleFont(bmp, 26);
        bmp.textColor = COLOR.text;
        bmp.outlineColor = 'rgba(6, 10, 20, 0.85)';
        bmp.outlineWidth = 4;
        bmp.drawText(text, 36, 12, bmp.width - 60, 36, 'left');
    }

    // A row band, like the bars of the reference: blue on the left fading out.
    function drawBand(bmp, x, y, w, h) {
        var ctx = ctxOf(bmp);
        var g = ctx.createLinearGradient(x, 0, x + w, 0);
        g.addColorStop(0, 'rgba(36, 68, 126, 0.55)');
        g.addColorStop(1, 'rgba(36, 68, 126, 0.08)');
        ctx.fillStyle = g;
        ctx.fillRect(x, y, w, h);
        ctx.fillStyle = 'rgba(156, 192, 236, 0.18)';
        ctx.fillRect(x, y + h - 1, w, 1);
        dirty(bmp);
    }

    function text(bmp, str, x, y, w, h, align, color, size, title) {
        if (title) UI.titleFont(bmp, size);
        else UI.bodyFont(bmp, size);
        bmp.textColor = color || COLOR.text;
        bmp.outlineColor = 'rgba(6, 10, 20, 0.8)';
        bmp.outlineWidth = 3;
        bmp.drawText(str, x, y, w, h, align || 'left');
    }

    function drawIcon(bmp, index, x, y, onLoad) {
        if (!index) return;
        var set = ImageManager.loadSystem('IconSet');
        if (!set.isReady()) { set.addLoadListener(onLoad); return; }
        bmp.blt(set, index % 16 * 32, Math.floor(index / 16) * 32, 32, 32, x, y);
    }

    //=========================================================================
    // Sprite_NovaBattleResult: the whole screen, over everything in battle
    //=========================================================================
    function Sprite_NovaBattleResult() { this.initialize.apply(this, arguments); }
    Sprite_NovaBattleResult.prototype = Object.create(Sprite.prototype);
    Sprite_NovaBattleResult.prototype.constructor = Sprite_NovaBattleResult;

    Sprite_NovaBattleResult.prototype.initialize = function() {
        Sprite.prototype.initialize.call(this);
        this._data = null;
        this._phase = 'idle';
        this.visible = false;
    };

    Sprite_NovaBattleResult.prototype.start = function(data) {
        this._data = data;
        this._phase = 'count';
        this._t = 0;
        this._shownLevels = data.actors.map(function(r) { return r.fromLevel; });
        this._flash = data.actors.map(function() { return 0; });
        this._levelled = data.actors.map(function() { return false; });
        var span = data.actors.reduce(function(m, r) { return Math.max(m, r.toLevel - r.fromLevel); }, 0);
        this._partyFrames = Math.min(150, 70 + span * 30);
        this.createLayers();
        this.visible = true;
        this.opacity = 0;
        if (this.parent) this.parent.addChild(this);   // stay on top of anything added since
    };

    Sprite_NovaBattleResult.prototype.createLayers = function() {
        this.removeChildren();
        var dim = new Sprite(new Bitmap(Graphics.width, Graphics.height));
        var ctx = ctxOf(dim.bitmap), g = ctx.createLinearGradient(0, 0, 0, Graphics.height);
        g.addColorStop(0, 'rgba(4, 8, 18, 0.78)');
        g.addColorStop(1, 'rgba(4, 8, 18, 0.62)');
        ctx.fillStyle = g;
        ctx.fillRect(0, 0, Graphics.width, Graphics.height);
        dirty(dim.bitmap);
        this.addChild(dim);

        var data = this._data;
        var itemLines = Math.max(1, Math.min(MAX_ITEM_LINES, data.items.length));
        var rewardH = HEAD_H + 3 * 48 + itemLines * 34 + 24;
        var hasReserve = data.actors.some(function(r) { return r.reserve; });
        var partyH = HEAD_H + Math.max(1, data.actors.length) * ROW_H + (hasReserve ? RESERVE_H : 0) + 12;
        // top left, just under the turn bar, so the party cards below stay clear
        var left = 40, top = 64;

        this._rewardSprite = new Sprite(new Bitmap(REWARD_W, rewardH));
        this._rewardSprite.x = this._rewardX = left;
        this._rewardSprite.y = top;
        this._partySprite = new Sprite(new Bitmap(PARTY_W, partyH));
        this._partySprite.x = this._partyX = left + REWARD_W + GAP;
        this._partySprite.y = top;
        this._partySprite.opacity = 0;
        this._hintSprite = new Sprite(new Bitmap(220, 32));
        this._hintSprite.x = this._partyX + PARTY_W - 220;
        this._hintSprite.y = top + Math.max(rewardH, partyH) + 8;
        this._hintSprite.opacity = 0;
        this.addChild(this._rewardSprite);
        this.addChild(this._partySprite);
        this.addChild(this._hintSprite);
        this.drawHint();
        this._rewardKey = this._partyKey = '';
    };

    Sprite_NovaBattleResult.prototype.update = function() {
        Sprite.prototype.update.call(this);
        if (this._phase === 'idle') {
            var data = BattleManager._novaResult;
            if (data && !data.closed) this.start(data);
            return;
        }
        if (this._phase === 'gone') return;
        if (this._phase === 'out') {
            this.opacity -= 24;
            if (this.opacity <= 0) {
                this._phase = 'gone';
                this.visible = false;
                this._data.closed = true;
            }
            return;
        }
        this.opacity = Math.min(255, this.opacity + 24);
        var slide = 1 - easeOut(this._t / 16);
        this._rewardSprite.x = this._rewardX - 30 * slide;
        var pt = (this._t - PARTY_DELAY + 16) / 16;
        this._partySprite.opacity = 255 * Math.max(0, Math.min(1, pt));
        this._partySprite.x = this._partyX + 30 * (1 - easeOut(pt));
        if (this._phase === 'count') {
            this._t++;
            if (this._t >= this.endFrame()) this.finish();
        } else {
            this._t++;
            this._hintSprite.opacity = 150 + 105 * Math.sin(this._t / 12);
        }
        this.refresh();
        if (this.isTriggered()) {
            if (this._phase === 'count') {
                this._t = this.endFrame();
                this.finish();
                this.refresh();
            } else {
                SoundManager.playOk();
                this._phase = 'out';
            }
        }
    };

    Sprite_NovaBattleResult.prototype.endFrame = function() {
        return PARTY_DELAY + this._partyFrames;
    };

    Sprite_NovaBattleResult.prototype.finish = function() {
        this._phase = 'done';
        this._partySprite.opacity = 255;
        this._partySprite.x = this._partyX;
        this._rewardSprite.x = this._rewardX;
    };

    Sprite_NovaBattleResult.prototype.isTriggered = function() {
        return Input.isTriggered('ok') || Input.isTriggered('cancel') || TouchInput.isTriggered();
    };

    Sprite_NovaBattleResult.prototype.refresh = function() {
        var rate = easeOut(this._t / COUNT_FRAMES);
        var key = String(Math.round(rate * 1000));
        if (key !== this._rewardKey) {
            this._rewardKey = key;
            this.drawRewards(rate);
        }
        var p = easeOut((this._t - PARTY_DELAY) / this._partyFrames);
        var pkey = Math.round(p * 2000) + ':' + this._flash.join(',');
        if (pkey !== this._partyKey) {
            this._partyKey = pkey;
            this.drawParty(p);
        }
        for (var i = 0; i < this._flash.length; i++) if (this._flash[i] > 0) this._flash[i]--;
    };

    Sprite_NovaBattleResult.prototype.redrawLater = function() {
        var self = this;
        return function() { self._rewardKey = self._partyKey = ''; };
    };

    //-------------------------------------------------------------------------
    // Left: totals and items
    //-------------------------------------------------------------------------
    Sprite_NovaBattleResult.prototype.drawRewards = function(rate) {
        var bmp = this._rewardSprite.bitmap, data = this._data, w = bmp.width, later = this.redrawLater();
        bmp.clear();
        drawPanel(bmp);
        drawTitle(bmp, TITLE);
        var x = 20, bw = w - 40, y = HEAD_H + 4;
        var rows = [
            [EXP_LABEL, EXP_ICON, String(Math.round(data.exp * rate))],
            [GOLD_LABEL, GOLD_ICON, Math.round(data.gold * rate) + ' ' + TextManager.currencyUnit]
        ];
        rows.forEach(function(row) {
            drawBand(bmp, x, y, bw, 40);
            text(bmp, row[0], x + 14, y + 2, bw * 0.55, 36, 'left', COLOR.text, 22);
            drawIcon(bmp, row[1], x + bw - 40, y + 4, later);
            text(bmp, row[2], x, y + 2, bw - 50, 36, 'right', COLOR.accentLit, 26, true);
            y += 48;
        });
        drawBand(bmp, x, y, bw, 40);
        text(bmp, ITEMS_LABEL, x + 14, y + 2, bw * 0.6, 36, 'left', COLOR.text, 22);
        drawIcon(bmp, ITEMS_ICON, x + bw - 40, y + 4, later);
        y += 48;
        if (!data.items.length) {
            var ctx = ctxOf(bmp);
            ctx.fillStyle = 'rgba(156, 192, 236, 0.45)';
            ctx.fillRect(x + bw - 160, y + 16, 140, 1);
            dirty(bmp);
            return;
        }
        var shown = data.items.length > MAX_ITEM_LINES ? MAX_ITEM_LINES - 1 : data.items.length;
        var visible = Math.floor(rate * shown + 0.999);   // items appear one by one with the count
        for (var i = 0; i < visible; i++) {
            var e = data.items[i];
            drawIcon(bmp, e.item.iconIndex, x + 22, y + 1, later);
            text(bmp, e.item.name, x + 62, y, bw - 150, 34, 'left', COLOR.text, 22);
            text(bmp, '×' + e.count, x, y, bw - 20, 34, 'right', COLOR.accentLit, 22);
            y += 34;
        }
        if (shown < data.items.length && rate >= 1) {
            text(bmp, '+ ' + (data.items.length - shown) + ' more', x + 62, y, bw - 80, 34, 'left', COLOR.dim, 20);
        }
    };

    //-------------------------------------------------------------------------
    // Right: one row per battle member, the EXP bar filling up
    //-------------------------------------------------------------------------
    // Level and bar fill for an EXP amount between the old and the new total.
    function levelAt(actor, exp, fromLevel, toLevel) {
        var lv = fromLevel;
        while (lv < toLevel && exp >= actor.expForLevel(lv + 1)) lv++;
        if (lv >= actor.maxLevel()) return { level: lv, rate: 1, next: 0, max: true };
        var base = actor.expForLevel(lv), next = actor.expForLevel(lv + 1);
        return { level: lv, rate: (exp - base) / (next - base), next: next - exp, max: false };
    }

    Sprite_NovaBattleResult.prototype.drawParty = function(p) {
        var bmp = this._partySprite.bitmap, w = bmp.width, self = this, actors = this._data.actors;
        var x = 28, bw = w - 56, y = HEAD_H;
        bmp.clear();
        drawPanel(bmp);
        drawTitle(bmp, PARTY_TITLE);
        actors.forEach(function(r, i) {
            var actor = r.actor;
            if (r.reserve && (i === 0 || !actors[i - 1].reserve)) {
                text(bmp, RESERVE_LABEL, x, y, 200, RESERVE_H, 'left', COLOR.dim, 14, true);
                y += RESERVE_H;
            }
            var exp = Math.round(r.fromExp + (r.toExp - r.fromExp) * p);
            var now = levelAt(actor, exp, r.fromLevel, r.toLevel);
            if (now.level > self._shownLevels[i]) {
                self._shownLevels[i] = now.level;
                self._levelled[i] = true;
                self._flash[i] = 24;
                if (LEVEL_SE) AudioManager.playSe({ name: LEVEL_SE, volume: 90, pitch: 100, pan: 0 });
            }
            // one compact row: name, level, LEVEL UP!, +EXP, and a thin bar under them
            //   Kael    Lv 4   LEVEL UP!  Fire           +604 EXP
            //   ==================-----------------------------
            var lvColor = self._flash[i] > 0 && self._flash[i] % 8 < 4 ? '#ffffff'
                        : self._levelled[i] ? COLOR.pending : COLOR.accentLit;
            text(bmp, actor.name(), x, y + 2, 150, 28, 'left', r.reserve ? COLOR.dim : COLOR.text, 18, true);
            text(bmp, TextManager.levelA + ' ' + now.level, x + 150, y + 2, 70, 28, 'left', lvColor, 18, true);
            if (self._levelled[i]) {
                var learned = p >= 1 ? r.learned.map(function(s) { return s.name; }).join(', ') : '';
                text(bmp, LEVEL_UP + (learned ? '  ' + learned : ''), x + 222, y + 4, bw - 222 - 120, 26, 'left', COLOR.pending, 15, true);
            }
            var gained = Math.round((r.toExp - r.fromExp) * Math.min(1, p));
            text(bmp, '+' + gained + ' ' + TextManager.expA, x, y + 2, bw, 28, 'right', COLOR.pending, 18);
            UI.drawBar(ctxOf(bmp), x, y + 32, bw, 6, now.rate, COLOR.exp);
            if (self._flash[i] > 0) {
                var c = ctxOf(bmp);
                c.fillStyle = 'rgba(255, 244, 210, ' + (self._flash[i] / 24 * 0.8) + ')';
                c.fillRect(x + 1, y + 33, bw - 2, 4);
            }
            dirty(bmp);
            y += ROW_H;
        });
    };

    Sprite_NovaBattleResult.prototype.drawHint = function() {
        var bmp = this._hintSprite.bitmap, ctx = ctxOf(bmp);
        UI.diamond(ctx, 120, 16, 4, COLOR.accent);
        dirty(bmp);
        text(bmp, 'Continue', 130, 0, 90, 32, 'right', COLOR.text, 20);
    };

    //=========================================================================
    // Scene_Battle: the screen sits above the windows
    //=========================================================================
    var _createAllWindows = Scene_Battle.prototype.createAllWindows;
    Scene_Battle.prototype.createAllWindows = function() {
        _createAllWindows.call(this);
        this._novaResultSprite = new Sprite_NovaBattleResult();
        this.addChild(this._novaResultSprite);
    };

    window.Sprite_NovaBattleResult = Sprite_NovaBattleResult;
})();
