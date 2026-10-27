//=============================================================================
// NovaBattle.js
//=============================================================================
/*:
 * @plugindesc Active Time Battle (ATB) with a Nova-styled battle screen: party
 * cards with faces, HP/MP and ATB gauges, and a turn timeline at the top.
 * @author Project Nova
 *
 * @param ATB Mode
 * @type select
 * @option wait
 * @option active
 * @desc wait: time stops while you choose a command. active: gauges keep filling while you choose.
 * @default wait
 *
 * @param Fill Time
 * @type number
 * @min 30
 * @desc Frames (60 = 1 second) for a battler of average agility to fill its gauge. Also the length of one battle turn.
 * @default 150
 *
 * @help
 * Requires NovaMenu. Place this plugin below NovaMenu and NovaPets.
 *
 * Active Time Battle
 *   Every battler has an ATB gauge that fills over time; higher AGI fills
 *   faster. When a hero's gauge is full they get the command menu, enemies
 *   act as soon as theirs is full. Gauges pause while an action plays out.
 *     wait mode   - time also stops while you are choosing a command
 *     active mode - gauges keep filling while you choose (enemies wait
 *                   their turn until you have picked the command)
 *   Cancel on the first command passes to the next hero who is ready.
 *   Escape is in every hero's command list; a failed escape uses that
 *   hero's turn.
 *
 * Turns, states and buffs
 *   A battle "turn" (for troop events, enemy action conditions and the pet
 *   assist) passes every "Fill Time" frames of running time.
 *   States and buffs count down at the end of each battler's own action,
 *   so "2 turns" means two of that battler's own turns. Guard and other
 *   states a battler puts on itself last until the end of its next turn.
 *
 * Screen
 *   Top:    one slim row with the turn number, whose turn it is, and the
 *           ATB timeline - every battler's icon (heroes cyan, enemies red)
 *           slides along it and acts when it reaches ACT.
 *   Bottom left:  the command list of the hero whose turn it is, two columns,
 *                 as tall as the cards (more than 6 commands scroll); also
 *                 the enemy target list.
 *   Bottom right: a card per hero: the actor's face on the left; name, HP,
 *                 MP, TP and the ATB gauge on the right; states on the face.
 */

(function() {
    'use strict';

    var UI = window.NovaUI;
    if (!UI) {
        console.warn('NovaBattle: NovaMenu must be ON and placed above NovaBattle.');
        return;
    }

    var params = PluginManager.parameters('NovaBattle');
    var ACTIVE = String(params['ATB Mode'] || 'wait').toLowerCase() === 'active';
    var FILL = Math.max(30, Number(params['Fill Time'] || 150));

    var COLOR = UI.COLOR, ctxOf = UI.ctxOf, dirty = UI.dirty, pathPoly = UI.pathPoly, panelShape = UI.panelShape;
    var ENEMY = '#ff7088';
    var TARGET = '#ffd27a';
    var ATB_FILL = ['#eef8ff', '#6f8fb4'];
    var ATB_READY = COLOR.exp;
    var TP_COLORS = ['#ffb070', '#d0602a'];
    var TOP_H = 52;
    var STATUS_H = 150;
    var CMD_X = 12, CMD_W = 230;
    var CARDS_X = CMD_X + CMD_W + 8;

    function statusTop() { return Graphics.boxHeight - STATUS_H - 6; }

    function removeFrom(list, item) {
        var i = list ? list.indexOf(item) : -1;
        if (i >= 0) list.splice(i, 1);
    }

    function slantBar(ctx, x, y, w, h, rate, colors) {
        var k = Math.min(4, h * 0.6);
        ctx.fillStyle = 'rgba(0, 0, 0, 0.6)';
        pathPoly(ctx, [[x + k, y], [x + w, y], [x + w - k, y + h], [x, y + h]]);
        ctx.fill();
        var fw = Math.max(0, Math.min(1, rate)) * w;
        if (fw > 0) {
            var g = ctx.createLinearGradient(x, 0, x + fw, 0);
            g.addColorStop(0, colors[1]);
            g.addColorStop(1, colors[0]);
            ctx.fillStyle = g;
            pathPoly(ctx, [[x + k, y], [x + fw, y], [x + Math.max(0, fw - k), y + h], [x, y + h]]);
            ctx.fill();
        }
    }

    //=========================================================================
    // Battler pictures (face, enemy graphic, or walking sprite for pets)
    //=========================================================================
    var boxCache = {};

    // The part of an enemy image that is not transparent, so small icons are not mostly empty.
    function opaqueBox(bmp, key) {
        if (boxCache[key]) return boxCache[key];
        var w = bmp.width, h = bmp.height, box = { x: 0, y: 0, w: w, h: h };
        try {
            var c = document.createElement('canvas');
            c.width = w; c.height = h;
            var cx = c.getContext('2d');
            cx.drawImage(bmp._canvas || bmp._image, 0, 0);
            var data = cx.getImageData(0, 0, w, h).data;
            var minX = w, minY = h, maxX = -1, maxY = -1;
            for (var py = 0; py < h; py += 2) {
                for (var px = 0; px < w; px += 2) {
                    if (data[(py * w + px) * 4 + 3] > 40) {
                        if (px < minX) minX = px;
                        if (px > maxX) maxX = px;
                        if (py < minY) minY = py;
                        if (py > maxY) maxY = py;
                    }
                }
            }
            if (maxX >= 0) box = { x: minX, y: minY, w: maxX - minX + 2, h: maxY - minY + 2 };
        } catch (e) { /* keep the whole image */ }
        boxCache[key] = box;
        return box;
    }

    function enemyBitmap(enemy) {
        return $gameSystem.isSideView() ? ImageManager.loadSvEnemy(enemy.battlerName(), enemy.battlerHue())
                                        : ImageManager.loadEnemy(enemy.battlerName(), enemy.battlerHue());
    }

    // Draws the picture centred in a square; returns false (and calls onLoad later) if not loaded yet.
    function drawBattlerPicture(ctx, battler, x, y, size, onLoad) {
        var bmp, sx = 0, sy = 0, sw = 0, sh = 0;
        if (battler.isActor() && battler.faceName()) {
            bmp = ImageManager.loadFace(battler.faceName());
            if (bmp.isReady()) {
                var fw = Window_Base._faceWidth, fh = Window_Base._faceHeight, fi = battler.faceIndex();
                sx = fi % 4 * fw; sy = Math.floor(fi / 4) * fh; sw = fw; sh = fh;
            }
        } else if (battler.isActor()) {
            bmp = ImageManager.loadCharacter(battler.characterName());
            if (bmp.isReady()) {
                var big = ImageManager.isBigCharacter(battler.characterName());
                var pw = bmp.width / (big ? 3 : 12), ph = bmp.height / (big ? 4 : 8);
                var ci = big ? 0 : battler.characterIndex();
                sx = ((ci % 4) * 3 + 1) * pw; sy = Math.floor(ci / 4) * 4 * ph; sw = pw; sh = ph;
            }
        } else {
            bmp = enemyBitmap(battler);
            if (bmp.isReady()) {
                var box = opaqueBox(bmp, battler.battlerName() + ':' + battler.battlerHue());
                var side = Math.max(box.w, box.h);
                sx = box.x + (box.w - side) / 2; sy = box.y + (box.h - side) / 2; sw = sh = side;
            }
        }
        if (!bmp || !bmp.isReady() || !bmp.width) {
            if (bmp && onLoad) bmp.addLoadListener(onLoad);
            return false;
        }
        var scale = Math.min(size / sw, size / sh);
        var dw = sw * scale, dh = sh * scale;
        ctx.imageSmoothingEnabled = true;
        if ('imageSmoothingQuality' in ctx) ctx.imageSmoothingQuality = 'high';
        ctx.drawImage(bmp._canvas || bmp._image, sx, sy, sw, sh, x + (size - dw) / 2, y + (size - dh) / 2, dw, dh);
        return true;
    }

    function battlerKey(battler) {
        if (!battler) return '';
        return battler.isActor() ? 'a' + battler.actorId() : 'e' + battler.index();
    }

    //=========================================================================
    // Battlers: per-battler turn end for ATB
    //=========================================================================
    var _Game_Battler_onBattleStart = Game_Battler.prototype.onBattleStart;
    Game_Battler.prototype.onBattleStart = function() {
        _Game_Battler_onBattleStart.call(this);
        this._novaAtb = 0;
        this._novaFresh = null;
    };

    // Remember states/buffs a battler gives itself during its own action, so
    // they are not counted down at the end of that same action (e.g. Guard).
    function markFresh(battler, key) {
        if ($gameParty.inBattle() && BattleManager._subject === battler) {
            battler._novaFresh = battler._novaFresh || {};
            battler._novaFresh[key] = true;
        }
    }

    var _Game_Battler_addState = Game_Battler.prototype.addState;
    Game_Battler.prototype.addState = function(stateId) {
        _Game_Battler_addState.call(this, stateId);
        if (this.isStateAffected(stateId)) markFresh(this, 's' + stateId);
    };

    var _Game_Battler_addBuff = Game_Battler.prototype.addBuff;
    Game_Battler.prototype.addBuff = function(paramId, turns) {
        _Game_Battler_addBuff.call(this, paramId, turns);
        markFresh(this, 'b' + paramId);
    };

    var _Game_Battler_addDebuff = Game_Battler.prototype.addDebuff;
    Game_Battler.prototype.addDebuff = function(paramId, turns) {
        _Game_Battler_addDebuff.call(this, paramId, turns);
        markFresh(this, 'b' + paramId);
    };

    Game_Battler.prototype.novaEndOwnTurn = function() {
        var fresh = this._novaFresh;
        if (fresh && !BattleManager.isForcedTurn()) {
            this._states.forEach(function(id) {
                if (fresh['s' + id] && this._stateTurns[id] > 0) this._stateTurns[id]++;
            }, this);
            for (var i = 0; i < this._buffTurns.length; i++) {
                if (fresh['b' + i] && this._buffTurns[i] > 0) this._buffTurns[i]++;
            }
        }
        this._novaFresh = null;
        this.onTurnEnd();
    };

    //=========================================================================
    // BattleManager: ATB flow
    //   'atb'   gauges fill; ready battlers are queued
    //   'input' a ready hero chooses a command
    //   'turn' / 'action'  the current subject acts (as usual)
    //   'turnEnd'  every FILL frames, for troop events and the turn counter
    //=========================================================================
    BattleManager.novaAverageAgi = function() {
        var alive = this.allBattleMembers().filter(function(b) { return b.isAlive(); });
        if (alive.length === 0) return 1;
        var sum = alive.reduce(function(s, b) { return s + b.agi; }, 0);
        return Math.max(1, sum / alive.length);
    };

    BattleManager.novaInitAtb = function() {
        this._novaInputQueue = [];
        this._novaActQueue = [];
        this._novaTurnTicks = 0;
        this._novaTurnEndPending = false;
        this._novaPetActed = false;
        var avg = this.novaAverageAgi();
        this.allBattleMembers().forEach(function(b) {
            var head = Math.min(0.45, 0.25 * b.agi / avg) + Math.random() * 0.2;
            if (this._preemptive) head = b.isActor() ? 0.85 + Math.random() * 0.14 : Math.random() * 0.15;
            if (this._surprise) head = b.isEnemy() ? 0.85 + Math.random() * 0.14 : Math.random() * 0.15;
            b._novaAtb = b.isAlive() ? head : 0;
        }, this);
    };

    BattleManager.novaIsQueued = function(b) {
        return this._novaInputQueue.contains(b) || this._novaActQueue.contains(b) ||
               this._subject === b || this.actor() === b;
    };

    BattleManager.novaOnReady = function(b) {
        if (b.isActor() && b.canInput()) this._novaInputQueue.push(b);
        else this._novaActQueue.push(b);
    };

    BattleManager.novaTick = function() {
        if (!this._novaInputQueue) return;
        var avg = this.novaAverageAgi();
        this.allBattleMembers().forEach(function(b) {
            if (!b.isAlive()) { b._novaAtb = 0; return; }
            if (b.isActor() && b._actionState === 'done' && this._subject !== b) b.setActionState('undecided');
            var atb = b._novaAtb || 0;
            if (atb < 1) {
                atb = b._novaAtb = Math.min(1, atb + b.agi / avg / FILL);
                if (atb >= 1) this.novaOnReady(b);
            } else if (!this.novaIsQueued(b)) {
                this.novaOnReady(b);
            }
        }, this);
        if (++this._novaTurnTicks >= FILL) {
            this._novaTurnTicks = 0;
            this._novaTurnEndPending = true;
        }
    };

    BattleManager.novaCanAct = function(b) {
        return b.isBattleMember() && b.isAlive();
    };

    BattleManager.updateNovaAtb = function() {
        if (this._novaTurnEndPending) {
            if (!this._novaPetActed && this.novaStartPetAssist && this.novaStartPetAssist()) return;
            this.novaEndTurnCycle();
            return;
        }
        var b;
        while ((b = this._novaActQueue.shift())) {
            if (!this.novaCanAct(b)) continue;
            var resume = b._novaResume;
            b._novaResume = false;
            this.novaStartSubject(b, resume);
            return;
        }
        while ((b = this._novaInputQueue[0])) {
            if (!this.novaCanAct(b)) { this._novaInputQueue.shift(); continue; }
            if (!b.canInput()) {
                this._novaInputQueue.shift();
                this.novaStartSubject(b, false);
                return;
            }
            this.novaStartInput(b);
            return;
        }
        this.novaTick();
    };

    BattleManager.novaStartInput = function(actor) {
        this._phase = 'input';
        actor.makeActions();
        this._actorIndex = -1;
        this.changeActor(actor.index(), 'undecided');
        SoundManager.playCursor();
    };

    BattleManager.novaStartSubject = function(b, keepActions) {
        if (!keepActions) b.makeActions();
        this._subject = b;
        this._phase = 'turn';
        $gameParty.requestMotionRefresh();
    };

    BattleManager.novaFinishSubject = function(subject) {
        subject.onAllActionsEnd();
        subject.novaEndOwnTurn();
        this.refreshStatus();
        this._logWindow.displayAutoAffectedStatus(subject);
        this._logWindow.displayCurrentState(subject);
        this._logWindow.displayRegeneration(subject);
        subject._novaAtb = 0;
        removeFrom(this._novaInputQueue, subject);
        removeFrom(this._novaActQueue, subject);
        this._turnForced = false;
        this._subject = null;
        this._phase = 'atb';
    };

    BattleManager.novaEndTurnCycle = function() {
        this._novaTurnEndPending = false;
        this._phase = 'turnEnd';
    };

    // Battle start: instead of the party command, time starts flowing.
    BattleManager.startInput = function() {
        this.clearActor();
        this.novaInitAtb();
        $gameTroop.increaseTurn();
        this._phase = 'atb';
    };

    var _BattleManager_update = BattleManager.update;
    BattleManager.update = function() {
        if (this._phase === 'atb') {
            if (!this.isBusy() && !this.updateEvent()) this.updateNovaAtb();
        } else {
            _BattleManager_update.call(this);
        }
    };

    var _BattleManager_updateEvent = BattleManager.updateEvent;
    BattleManager.updateEvent = function() {
        if (this._phase === 'atb') {
            if (this.isActionForced()) {
                this.processForcedAction();
                return true;
            }
            return this.updateEventMain();
        }
        return _BattleManager_updateEvent.call(this);
    };

    // Replaces the default (and NovaPets') round-based updateTurn: one subject at a time.
    BattleManager.updateTurn = function() {
        $gameParty.requestMotionRefresh();
        if (this._subject) this.processTurn();
        else this._phase = 'atb';
    };

    BattleManager.processTurn = function() {
        var subject = this._subject;
        var action = subject.currentAction();
        if (action) {
            action.prepare();
            if (action.isValid()) this.startAction();
            subject.removeCurrentAction();
        } else {
            this.novaFinishSubject(subject);
        }
    };

    BattleManager.updateTurnEnd = function() {
        $gameTroop.increaseTurn();
        this._novaPetActed = false;
        this._preemptive = false;
        this._surprise = false;
        this._phase = 'atb';
    };

    // A forced action (troop event) interrupts whoever was acting; they continue afterwards.
    var _BattleManager_processForcedAction = BattleManager.processForcedAction;
    BattleManager.processForcedAction = function() {
        var prev = this._subject;
        if (prev && prev !== this._actionForcedBattler && this._novaActQueue) {
            prev._novaResume = true;
            this._novaActQueue.unshift(prev);
        }
        _BattleManager_processForcedAction.call(this);
    };

    BattleManager.selectNextCommand = function() {
        var actor = this.actor();
        if (!actor) return;
        if (actor.selectNextCommand()) return;
        removeFrom(this._novaInputQueue, actor);
        this.changeActor(-1, 'waiting');
        this.novaStartSubject(actor, true);
    };

    // Cancel on the first command hands the turn to the next hero who is ready.
    BattleManager.selectPreviousCommand = function() {
        var actor = this.actor();
        if (!actor) return;
        if (actor.selectPreviousCommand()) return;
        if (this._novaInputQueue.length > 1) {
            this._novaInputQueue.push(this._novaInputQueue.shift());
            actor.clearActions();
            this.changeActor(-1, 'undecided');
            this.novaStartInput(this._novaInputQueue[0]);
        }
    };

    BattleManager.processEscape = function() {
        $gameParty.performEscape();
        SoundManager.playEscape();
        var success = this._preemptive ? true : (Math.random() < this._escapeRatio);
        if (success) {
            this.displayEscapeSuccessMessage();
            this._escaped = true;
            this.processAbort();
        } else {
            this.displayEscapeFailureMessage();
            this._escapeRatio += 0.1;
            var actor = this.actor();
            if (actor) {
                actor.clearActions();
                actor._novaAtb = 0;
                removeFrom(this._novaInputQueue, actor);
            }
            this.changeActor(-1, 'undecided');
            this._phase = 'atb';
        }
        return success;
    };

    // --- information for the screen
    BattleManager.novaReadyOrder = function() {
        if (!this._novaInputQueue) return [];
        return this._novaInputQueue.concat(this._novaActQueue);
    };

    BattleManager.novaCurrentTurn = function() {
        if (this.isInputting() && this.actor()) return { battler: this.actor(), mode: 'input' };
        var s = this._subject;
        if (s && !this.isBattleEnd()) {
            var pet = this.isNovaPetAssisting && this.isNovaPetAssisting();
            return { battler: s, mode: pet ? 'pet' : (s.isActor() ? 'act' : 'enemy') };
        }
        return null;
    };

    BattleManager.novaNextBattler = function() {
        var queued = this.novaReadyOrder()[0];
        if (queued) return queued;
        var avg = this.novaAverageAgi(), best = null, bestT = Infinity;
        this.allBattleMembers().forEach(function(b) {
            if (!b.isAlive()) return;
            var t = (1 - (b._novaAtb || 0)) / Math.max(0.01, b.agi / avg);
            if (t < bestT) { bestT = t; best = b; }
        });
        return best;
    };

    //=========================================================================
    // Party cards (bottom right): face on the left, name/HP/MP/TP/ATB on the right
    //=========================================================================
    var FACE = 100;

    function Sprite_NovaAtbGauge() { this.initialize.apply(this, arguments); }
    Sprite_NovaAtbGauge.prototype = Object.create(Sprite.prototype);
    Sprite_NovaAtbGauge.prototype.constructor = Sprite_NovaAtbGauge;

    Sprite_NovaAtbGauge.prototype.initialize = function(win, index) {
        Sprite.prototype.initialize.call(this);
        this._win = win;
        this._index = index;
        this._key = '';
        this.bitmap = new Bitmap(8, 18);
    };

    Sprite_NovaAtbGauge.prototype.update = function() {
        Sprite.prototype.update.call(this);
        var win = this._win, actor = $gameParty.battleMembers()[this._index];
        this.visible = !!actor && win.visible && win.isOpen();
        if (!this.visible) return;
        var rect = win.itemRect(this._index), col = win.novaInfoColumn(rect);
        var w = Math.max(8, col.width - 28);
        if (this.bitmap.width !== w) { this.bitmap = new Bitmap(w, 18); this._key = ''; }
        this.x = win.padding + col.x + 28;
        this.y = win.padding + rect.y + rect.height - 25;
        var rate = actor.isAlive() ? Math.min(1, actor._novaAtb || 0) : 0;
        var ready = rate >= 1;
        var pulse = ready ? Math.floor(Graphics.frameCount / 3) % 20 : 0;
        var key = Math.round(rate * w) + ':' + pulse;
        if (key !== this._key) {
            this._key = key;
            this.redraw(rate, ready, pulse);
        }
    };

    Sprite_NovaAtbGauge.prototype.redraw = function(rate, ready, pulse) {
        var b = this.bitmap, ctx = ctxOf(b), w = b.width;
        b.clear();
        ctx.save();
        if (ready) {
            var glow = 0.5 + 0.5 * Math.sin(pulse / 20 * Math.PI * 2);
            ctx.shadowColor = 'rgba(255, 224, 138, ' + (0.35 + 0.65 * glow) + ')';
            ctx.shadowBlur = 8;
        }
        slantBar(ctx, 3, 5, w - 6, 8, rate, ready ? ATB_READY : ATB_FILL);
        ctx.restore();
        dirty(b);
        if (ready) {
            b.fontSize = 12;
            b.textColor = '#fff6d8';
            b.outlineColor = 'rgba(90, 55, 0, 0.95)';
            b.outlineWidth = 3;
            b.drawText('READY', 0, 0, w - 8, 18, 'right');
        }
    };

    var _Window_BattleStatus_initialize = Window_BattleStatus.prototype.initialize;
    Window_BattleStatus.prototype.initialize = function() {
        $gameParty.battleMembers().forEach(function(a) { ImageManager.loadFace(a.faceName()); });
        _Window_BattleStatus_initialize.call(this);
        this.x = CARDS_X;
        this.y = statusTop();
        this.opacity = 0;
        this._novaNoPanel = true;
        for (var i = 0; i < this.maxCols(); i++) this.addChild(new Sprite_NovaAtbGauge(this, i));
    };
    Window_BattleStatus.prototype.windowWidth = function() { return Graphics.boxWidth - CARDS_X - 12; };
    Window_BattleStatus.prototype.windowHeight = function() { return STATUS_H; };
    Window_BattleStatus.prototype.standardPadding = function() { return 6; };
    Window_BattleStatus.prototype.numVisibleRows = function() { return 1; };
    Window_BattleStatus.prototype.maxCols = function() { return Math.max(1, $gameParty.maxBattleMembers()); };
    Window_BattleStatus.prototype.spacing = function() { return 8; };
    Window_BattleStatus.prototype.itemHeight = function() { return this.contentsHeight(); };
    Window_BattleStatus.prototype.updateCursor = function() { this.setCursorRect(0, 0, 0, 0); };
    Window_BattleStatus.prototype.novaLitColor = function() { return COLOR.accent; };
    Window_BattleActor.prototype.novaLitColor = function() { return TARGET; };

    // Fewer heroes than slots: keep the cards centred.
    Window_BattleStatus.prototype.itemRect = function(index) {
        var rect = Window_Selectable.prototype.itemRect.call(this, index);
        var empty = this.maxCols() - this.maxItems();
        if (empty > 0) rect.x += Math.floor(empty * (rect.width + this.spacing()) / 2);
        return rect;
    };

    Window_BattleStatus.prototype.novaFaceRect = function(rect) {
        return { x: rect.x + 7, y: rect.y + Math.floor((rect.height - FACE) / 2), width: FACE, height: FACE };
    };

    Window_BattleStatus.prototype.novaInfoColumn = function(rect) {
        var x = rect.x + 7 + FACE + 10;
        return { x: x, width: rect.x + rect.width - 9 - x };
    };

    Window_BattleStatus.prototype.select = function(index) {
        var changed = index !== this._index;
        Window_Selectable.prototype.select.call(this, index);
        if (changed && this.contents) this.refresh();
    };

    Window_BattleStatus.prototype.drawItem = function(index) {
        var actor = $gameParty.battleMembers()[index];
        if (!actor) return;
        var rect = this.itemRect(index), lit = index === this.index();
        this.novaDrawCard(rect, lit, actor);
        this.novaDrawFace(actor, this.novaFaceRect(rect), lit);
        this.novaDrawInfo(actor, rect);
    };

    Window_BattleStatus.prototype.novaDrawCard = function(rect, lit, actor) {
        var ctx = ctxOf(this.contents), lc = this.novaLitColor();
        var shape = panelShape(rect.x + 1, rect.y + 1, rect.width - 2, rect.height - 2, 12);
        var g = ctx.createLinearGradient(0, rect.y, 0, rect.y + rect.height);
        g.addColorStop(0, COLOR.panelTop);
        g.addColorStop(1, COLOR.panelBottom);
        ctx.save();
        if (lit) { ctx.shadowColor = lc; ctx.shadowBlur = 14; }
        ctx.fillStyle = g;
        pathPoly(ctx, shape);
        ctx.fill();
        ctx.restore();
        if (lit) {
            var hl = ctx.createLinearGradient(0, rect.y, 0, rect.y + rect.height);
            hl.addColorStop(0, lc === TARGET ? 'rgba(255, 210, 122, 0.22)' : 'rgba(98, 214, 255, 0.22)');
            hl.addColorStop(0.7, 'rgba(98, 214, 255, 0)');
            ctx.fillStyle = hl;
            pathPoly(ctx, shape);
            ctx.fill();
        }
        if (actor.isDead()) {
            ctx.fillStyle = 'rgba(120, 0, 24, 0.28)';
            pathPoly(ctx, shape);
            ctx.fill();
        }
        ctx.lineWidth = lit ? 2.5 : 1.5;
        ctx.strokeStyle = lit ? lc : COLOR.frame;
        pathPoly(ctx, shape);
        ctx.stroke();
        // divider between the face box and the info box
        var col = this.novaInfoColumn(rect);
        ctx.fillStyle = COLOR.accentSoft;
        ctx.fillRect(col.x - 5, rect.y + 10, 1, rect.height - 20);
        dirty(this.contents);
    };

    Window_BattleStatus.prototype.novaDrawFace = function(actor, r, lit) {
        var ctx = ctxOf(this.contents);
        var shape = panelShape(r.x, r.y, r.width, r.height, 8);
        ctx.save();
        ctx.fillStyle = 'rgba(8, 18, 40, 0.9)';
        pathPoly(ctx, shape); ctx.fill();
        pathPoly(ctx, shape); ctx.clip();
        if (actor.isDead() && 'filter' in ctx) ctx.filter = 'grayscale(1) brightness(0.55)';
        drawBattlerPicture(ctx, actor, r.x, r.y, r.width, this.refresh.bind(this));
        ctx.restore();
        ctx.lineWidth = lit ? 2 : 1.5;
        ctx.strokeStyle = actor.isDead() ? ENEMY : (lit ? this.novaLitColor() : COLOR.frame);
        pathPoly(ctx, shape); ctx.stroke();
        dirty(this.contents);
        if (actor.isDead()) {
            this.contents.fontSize = 24;
            this.changeTextColor('#ff8a9a');
            this.contents.drawText('K.O.', r.x, r.y + r.height / 2 - 16, r.width, 32, 'center');
        }
        // states along the bottom of the face
        var iconSet = ImageManager.loadSystem('IconSet');
        var iw = Window_Base._iconWidth, ih = Window_Base._iconHeight;
        actor.allIcons().slice(0, 4).forEach(function(icon, i) {
            this.contents.blt(iconSet, icon % 16 * iw, Math.floor(icon / 16) * ih, iw, ih,
                              r.x + 2 + i * 24, r.y + r.height - 24, 22, 22);
        }, this);
        this.resetFontSettings();
    };

    Window_BattleStatus.prototype.novaStatRow = function(x, y, w, label, value, max, colors, crisis) {
        this.contents.fontSize = 14;
        this.changeTextColor(colors[0]);
        this.contents.drawText(label, x, y, 40, 18, 'left');
        var maxText = max === null ? '' : '/' + max;
        this.contents.fontSize = 12;
        var mw = maxText ? this.textWidth(maxText) + 2 : 0;
        this.changeTextColor(COLOR.dim);
        if (maxText) this.contents.drawText(maxText, x, y + 2, w, 18, 'right');
        this.contents.fontSize = 17;
        this.changeTextColor(crisis ? this.crisisColor() : '#ffffff');
        this.contents.drawText(value, x, y, w - mw, 18, 'right');
        slantBar(ctxOf(this.contents), x, y + 18, w, 4, value / Math.max(1, max || 100), colors);
        dirty(this.contents);
    };

    Window_BattleStatus.prototype.novaDrawInfo = function(actor, rect) {
        var col = this.novaInfoColumn(rect), x = col.x, w = col.width;
        var tp = $dataSystem.optDisplayTp;
        this.resetFontSettings();
        this.contents.fontSize = 20;
        this.changeTextColor(actor.isDead() ? '#ff8a9a' : '#ffffff');
        this.contents.drawText(actor.name(), x, rect.y + 2, w, 26, 'left');
        var y = rect.y + 30, step = tp ? 24 : 28;
        this.novaStatRow(x, y, w, TextManager.hpA, actor.hp, actor.mhp, COLOR.hp, actor.isDying());
        this.novaStatRow(x, y + step, w, TextManager.mpA, actor.mp, actor.mmp, COLOR.mp, false);
        if (tp) this.novaStatRow(x, y + step * 2, w, TextManager.tpA, actor.tp, null, TP_COLORS, false);
        this.contents.fontSize = 12;
        this.changeTextColor(COLOR.dim);
        this.contents.drawText('ATB', x, rect.y + rect.height - 25, 28, 18, 'left');
        this.resetFontSettings();
    };

    //=========================================================================
    // Command list (bottom left): slanted bars like the main menu, name tag on
    // top, as tall as the party cards; longer lists scroll.
    //=========================================================================
    var TAG_H = 26;

    var _Window_ActorCommand_initialize = Window_ActorCommand.prototype.initialize;
    Window_ActorCommand.prototype.initialize = function() {
        _Window_ActorCommand_initialize.call(this);
        this.x = CMD_X;
        this.y = statusTop() + TAG_H + 2;
        this.opacity = 0;
        this._novaNoPanel = true;
        this._novaTag = new Sprite(new Bitmap(CMD_W, TAG_H));
        this._novaTag.y = -TAG_H - 2;
        this.addChild(this._novaTag);
    };
    Window_ActorCommand.prototype.windowWidth = function() { return CMD_W; };
    Window_ActorCommand.prototype.windowHeight = function() { return STATUS_H - TAG_H - 2; };
    Window_ActorCommand.prototype.standardPadding = function() { return 4; };
    // Two columns, so the usual six commands all fit in the card height without scrolling.
    Window_ActorCommand.prototype.maxCols = function() { return 2; };
    Window_ActorCommand.prototype.spacing = function() { return 4; };
    Window_ActorCommand.prototype.itemHeight = function() { return 38; };
    Window_ActorCommand.prototype.numVisibleRows = function() {
        return Math.floor((this.windowHeight() - this.standardPadding() * 2) / this.itemHeight());
    };
    Window_ActorCommand.prototype.updateCursor = function() { this.setCursorRect(0, 0, 0, 0); };
    Window_ActorCommand.prototype.drawItem = function(index) {
        var rect = this.itemRect(index);
        var selected = index === this.index();
        var lit = selected && this.active;
        var ctx = ctxOf(this.contents);
        var skew = 7, x = rect.x + 2, y = rect.y + 3, w = rect.width - 4, h = rect.height - 6;
        var g = ctx.createLinearGradient(x, 0, x + w, 0);
        if (selected) {
            g.addColorStop(0, lit ? 'rgba(98, 214, 255, 0.95)' : 'rgba(98, 214, 255, 0.55)');
            g.addColorStop(0.6, lit ? 'rgba(40, 120, 200, 0.6)' : 'rgba(40, 120, 200, 0.3)');
            g.addColorStop(1, 'rgba(20, 60, 120, 0.15)');
        } else {
            g.addColorStop(0, 'rgba(30, 60, 100, 0.8)');
            g.addColorStop(1, 'rgba(20, 40, 80, 0.25)');
        }
        ctx.fillStyle = g;
        pathPoly(ctx, [[x + skew, y], [x + w, y], [x + w - skew, y + h], [x, y + h]]);
        ctx.fill();
        ctx.strokeStyle = selected ? 'rgba(220, 250, 255, 0.9)' : 'rgba(140, 190, 230, 0.35)';
        ctx.lineWidth = 1;
        ctx.beginPath();
        ctx.moveTo(x + skew, y + 0.5); ctx.lineTo(x + w, y + 0.5);
        ctx.moveTo(x, y + h - 0.5); ctx.lineTo(x + w - skew, y + h - 0.5);
        ctx.stroke();
        dirty(this.contents);
        this.changePaintOpacity(this.isCommandEnabled(index));
        this.contents.fontSize = 19;
        this.changeTextColor(selected ? '#ffffff' : '#d6e8f7');
        this.contents.drawText(this.commandName(index), x + skew + 5, rect.y, w - skew * 2 - 8, rect.height, 'left');
        this.changePaintOpacity(true);
        this.resetFontSettings();
    };
    Window_ActorCommand.prototype.select = Window_NovaMenuCommand.prototype.select;
    Window_ActorCommand.prototype.activate = Window_NovaMenuCommand.prototype.activate;
    Window_ActorCommand.prototype.deactivate = Window_NovaMenuCommand.prototype.deactivate;

    var _Window_ActorCommand_makeCommandList = Window_ActorCommand.prototype.makeCommandList;
    Window_ActorCommand.prototype.makeCommandList = function() {
        _Window_ActorCommand_makeCommandList.call(this);
        if (this._actor && BattleManager.canEscape()) this.addCommand(TextManager.escape, 'escape');
    };

    var _Window_ActorCommand_setup = Window_ActorCommand.prototype.setup;
    Window_ActorCommand.prototype.setup = function(actor) {
        var isNew = actor !== this._actor || !this.isOpen();
        _Window_ActorCommand_setup.call(this, actor);
        this.novaDrawTag();
        if (isNew) this.x = CMD_X - 40;
    };

    Window_ActorCommand.prototype.novaDrawTag = function() {
        var b = this._novaTag.bitmap, ctx = ctxOf(b), w = b.width, h = b.height, actor = this._actor;
        b.clear();
        if (!actor) return;
        var g = ctx.createLinearGradient(0, 0, w, 0);
        g.addColorStop(0, 'rgba(98, 214, 255, 0.85)');
        g.addColorStop(0.6, 'rgba(40, 120, 200, 0.45)');
        g.addColorStop(1, 'rgba(20, 60, 120, 0)');
        ctx.fillStyle = g;
        pathPoly(ctx, [[12, 1], [w, 1], [w - 12, h - 1], [0, h - 1]]);
        ctx.fill();
        ctx.fillStyle = 'rgba(255, 255, 255, 0.8)';
        ctx.fillRect(12, 1, w * 0.6, 1);
        dirty(b);
        b.fontSize = 19;
        b.textColor = '#ffffff';
        b.outlineColor = 'rgba(0, 40, 80, 0.85)';
        b.outlineWidth = 4;
        b.drawText(actor.name(), 18, 0, w - 90, h, 'left');
        b.fontSize = 14;
        b.textColor = '#eaf7ff';
        b.drawText(TextManager.levelA + ' ' + actor.level, w - 84, 0, 64, h, 'right');
    };

    var _Window_ActorCommand_update = Window_ActorCommand.prototype.update;
    Window_ActorCommand.prototype.update = function() {
        _Window_ActorCommand_update.call(this);
        if (this.x < CMD_X) this.x = Math.min(CMD_X, this.x + 8);
        this._novaTag.visible = this.isOpen();
    };

    //=========================================================================
    // Target list (in place of the command list): enemy names with a small HP bar
    //=========================================================================
    Window_BattleEnemy.prototype.windowWidth = function() { return CMD_W; };
    Window_BattleEnemy.prototype.windowHeight = function() { return STATUS_H; };
    Window_BattleEnemy.prototype.maxCols = function() { return 1; };
    Window_BattleEnemy.prototype.itemHeight = function() { return 33; };
    Window_BattleEnemy.prototype.drawItem = function(index) {
        var enemy = this._enemies[index];
        if (!enemy) return;
        var rect = this.itemRectForText(index);
        this.resetFontSettings();
        this.contents.fontSize = 20;
        this.changeTextColor('#ffffff');
        this.contents.drawText(enemy.name(), rect.x, rect.y, rect.width - 64, rect.height, 'left');
        slantBar(ctxOf(this.contents), rect.x + rect.width - 56, rect.y + rect.height / 2 - 3, 56, 6,
                 enemy.hp / Math.max(1, enemy.mhp), ['#ff8a8a', '#c0304a']);
        dirty(this.contents);
        this.resetFontSettings();
    };

    //=========================================================================
    // Turn HUD (top, one slim row): turn number, whose turn, ATB timeline
    //=========================================================================
    var ICON = 28;

    function Sprite_NovaTurnIcon() { this.initialize.apply(this, arguments); }
    Sprite_NovaTurnIcon.prototype = Object.create(Sprite.prototype);
    Sprite_NovaTurnIcon.prototype.constructor = Sprite_NovaTurnIcon;

    Sprite_NovaTurnIcon.prototype.initialize = function(battler) {
        Sprite.prototype.initialize.call(this);
        this._battler = battler;
        this._lit = false;
        this.bitmap = new Bitmap(ICON + 4, ICON + 8);
        this.anchor.x = 0.5;
        this.anchor.y = 1;
        this.redraw();
    };

    Sprite_NovaTurnIcon.prototype.setLit = function(lit) {
        if (this._lit === lit) return;
        this._lit = lit;
        this.redraw();
    };

    Sprite_NovaTurnIcon.prototype.redraw = function() {
        var b = this.bitmap, ctx = ctxOf(b), battler = this._battler;
        var color = this._lit ? TARGET : (battler.isActor() ? COLOR.accent : ENEMY);
        var bx = 2, by = 2, size = ICON, cx = bx + size / 2;
        b.clear();
        var shape = panelShape(bx, by, size, size, 6);
        ctx.save();
        ctx.fillStyle = 'rgba(8, 18, 40, 0.92)';
        pathPoly(ctx, shape); ctx.fill();
        pathPoly(ctx, shape); ctx.clip();
        drawBattlerPicture(ctx, battler, bx + 1, by + 1, size - 2, this.redraw.bind(this));
        if (this._lit) {
            ctx.fillStyle = 'rgba(255, 224, 138, 0.18)';
            ctx.fillRect(bx, by, size, size);
        }
        ctx.restore();
        ctx.lineWidth = this._lit ? 3 : 2;
        ctx.strokeStyle = color;
        pathPoly(ctx, shape); ctx.stroke();
        ctx.fillStyle = color;
        pathPoly(ctx, [[cx - 5, by + size], [cx + 5, by + size], [cx, by + size + 5]]);
        ctx.fill();
        dirty(b);
        if (battler.isEnemy() && battler._plural && battler._letter) {
            b.fontSize = 12;
            b.textColor = '#ffffff';
            b.outlineWidth = 3;
            b.outlineColor = 'rgba(0, 0, 0, 0.9)';
            b.drawText(battler._letter, bx, by + size - 15, size - 2, 15, 'right');
        }
    };

    function Sprite_NovaTurnHud() { this.initialize.apply(this, arguments); }
    Sprite_NovaTurnHud.prototype = Object.create(Sprite.prototype);
    Sprite_NovaTurnHud.prototype.constructor = Sprite_NovaTurnHud;

    Sprite_NovaTurnHud.prototype.initialize = function() {
        Sprite.prototype.initialize.call(this);
        this._trackX = 404;
        this._trackW = Graphics.boxWidth - this._trackX - 60;
        this._trackY = 40;
        this._signature = '';
        this._panelKey = '';
        this._litIcon = null;
        this._icons = [];
        this.createBand();
        this.createPanel();
        this.createTrack();
        this._iconLayer = new Sprite();
        this.addChild(this._iconLayer);
        this.opacity = 0;
    };

    Sprite_NovaTurnHud.prototype.createBand = function() {
        var w = Graphics.boxWidth, h = TOP_H + 12, b = new Bitmap(w, h), ctx = ctxOf(b);
        var v = ctx.createLinearGradient(0, 0, 0, h);
        v.addColorStop(0, 'rgba(2, 8, 20, 0.8)');
        v.addColorStop(0.7, 'rgba(2, 8, 20, 0.35)');
        v.addColorStop(1, 'rgba(2, 8, 20, 0)');
        ctx.fillStyle = v;
        ctx.fillRect(0, 0, w, h);
        dirty(b);
        this.addChild(new Sprite(b));
    };

    Sprite_NovaTurnHud.prototype.createPanel = function() {
        this._panel = new Sprite(new Bitmap(340, TOP_H));
        this._panel.x = 12;
        this.addChild(this._panel);
    };

    Sprite_NovaTurnHud.prototype.createTrack = function() {
        var pad = 30, w = this._trackW + pad + 44, h = 16;
        var b = new Bitmap(w, h), ctx = ctxOf(b);
        var x0 = pad, x1 = pad + this._trackW, cy = h / 2;
        ctx.fillStyle = 'rgba(0, 0, 0, 0.65)';
        pathPoly(ctx, [[x0 + 4, cy - 3], [x1, cy - 3], [x1 - 4, cy + 3], [x0, cy + 3]]);
        ctx.fill();
        var g = ctx.createLinearGradient(x0, 0, x1, 0);
        g.addColorStop(0, 'rgba(98, 214, 255, 0.10)');
        g.addColorStop(0.75, 'rgba(98, 214, 255, 0.45)');
        g.addColorStop(1, 'rgba(255, 224, 138, 0.85)');
        ctx.fillStyle = g;
        ctx.fillRect(x0 + 2, cy - 1, this._trackW - 2, 2);
        ctx.fillStyle = 'rgba(200, 230, 255, 0.35)';
        for (var i = 1; i < 10; i++) ctx.fillRect(Math.round(x0 + this._trackW * i / 10), cy - 4, 1, 8);
        ctx.save();
        ctx.shadowColor = 'rgba(255, 224, 138, 0.9)';
        ctx.shadowBlur = 6;
        ctx.fillStyle = '#ffe08a';
        pathPoly(ctx, [[x1, cy - 6], [x1 + 6, cy], [x1, cy + 6], [x1 - 6, cy]]);
        ctx.fill();
        ctx.restore();
        dirty(b);
        b.fontSize = 12;
        b.outlineWidth = 3;
        b.outlineColor = 'rgba(0, 0, 0, 0.9)';
        b.textColor = '#ffe08a';
        b.drawText('ACT', x1 + 9, 0, 36, h, 'left');
        b.textColor = COLOR.dim;
        b.drawText('ATB', 0, 0, pad - 2, h, 'left');
        var s = new Sprite(b);
        s.x = this._trackX - pad;
        s.y = this._trackY - h / 2;
        this.addChild(s);
    };

    Sprite_NovaTurnHud.prototype.update = function() {
        Sprite.prototype.update.call(this);
        var phase = BattleManager._phase;
        var show = phase && phase !== 'init' && !BattleManager.isBattleEnd() &&
                   !$gameParty.isAllDead() && !$gameTroop.isAllDead();
        this.opacity += show ? 20 : -20;
        this.refreshIcons();
        this.updateIcons();
        this.refreshPanel();
    };

    Sprite_NovaTurnHud.prototype.refreshIcons = function() {
        var battlers = BattleManager.allBattleMembers();
        var sig = battlers.map(battlerKey).join(',');
        if (sig === this._signature) return;
        this._signature = sig;
        this._icons.forEach(function(icon) { this._iconLayer.removeChild(icon); }, this);
        this._icons = battlers.map(function(b) {
            var icon = new Sprite_NovaTurnIcon(b);
            icon.x = this.iconTargetX(b, []);
            icon.y = this._trackY - 1;
            icon.opacity = b.isAlive() ? 255 : 0;
            this._iconLayer.addChild(icon);
            return icon;
        }, this);
        this._litIcon = null;
    };

    Sprite_NovaTurnHud.prototype.iconTargetX = function(b, order) {
        var rate = b.isAlive() ? Math.min(1, b._novaAtb || 0) : 0;
        var x = this._trackX + rate * this._trackW;
        var q = order.indexOf(b);
        if (rate >= 1 && q > 0) x -= q * 14;   // several ready: queue them up at the end
        return x;
    };

    Sprite_NovaTurnHud.prototype.updateIcons = function() {
        var cur = BattleManager.novaCurrentTurn();
        var curB = cur ? cur.battler : null;
        var order = BattleManager.novaReadyOrder();
        if (curB) order = [curB].concat(order.filter(function(b) { return b !== curB; }));
        var lit = null;
        this._icons.forEach(function(icon) {
            var b = icon._battler;
            var tx = this.iconTargetX(b, order);
            icon.x += (tx - icon.x) * 0.3;
            if (Math.abs(tx - icon.x) < 0.5) icon.x = tx;
            icon.opacity += b.isAlive() ? 25 : -25;
            icon.setLit(b === curB);
            if (b === curB) lit = icon;
        }, this);
        if (lit && lit !== this._litIcon) {
            this._iconLayer.removeChild(lit);
            this._iconLayer.addChild(lit);   // current battler drawn on top
        }
        this._litIcon = lit;
    };

    Sprite_NovaTurnHud.prototype.refreshPanel = function() {
        var cur = BattleManager.novaCurrentTurn();
        var battler = cur ? cur.battler : (BattleManager._novaInputQueue ? BattleManager.novaNextBattler() : null);
        var mode = cur ? cur.mode : (battler ? 'next' : 'start');
        var key = $gameTroop.turnCount() + '|' + mode + '|' + battlerKey(battler) + '|' + (battler ? battler.name() : '');
        if (key === this._panelKey) return;
        this._panelKey = key;
        this.drawPanel(battler, mode);
    };

    Sprite_NovaTurnHud.prototype.drawPanel = function(battler, mode) {
        var b = this._panel.bitmap, ctx = ctxOf(b), w = b.width;
        b.clear();
        var py = 4, ph = TOP_H - 10;
        var shape = panelShape(1, py, w - 2, ph, 10);
        var g = ctx.createLinearGradient(0, py, 0, py + ph);
        g.addColorStop(0, COLOR.panelTop);
        g.addColorStop(1, COLOR.panelBottom);
        ctx.fillStyle = g;
        pathPoly(ctx, shape); ctx.fill();
        ctx.lineWidth = 1.5;
        ctx.strokeStyle = COLOR.frame;
        pathPoly(ctx, shape); ctx.stroke();
        ctx.fillStyle = COLOR.accentSoft;
        ctx.fillRect(62, py + 7, 1, ph - 14);
        var tone = { input: COLOR.accent, act: COLOR.accent, enemy: ENEMY, pet: TARGET, next: COLOR.frame, start: COLOR.frame }[mode];
        var size = ph - 8, ix = 72, iy = py + 4;
        if (battler) {
            var face = panelShape(ix, iy, size, size, 6);
            ctx.save();
            ctx.fillStyle = 'rgba(8, 18, 40, 0.92)';
            pathPoly(ctx, face); ctx.fill();
            pathPoly(ctx, face); ctx.clip();
            var self = this;
            drawBattlerPicture(ctx, battler, ix + 1, iy + 1, size - 2, function() { self._panelKey = ''; });
            ctx.restore();
            ctx.lineWidth = 2;
            ctx.strokeStyle = tone;
            pathPoly(ctx, face); ctx.stroke();
        }
        dirty(b);
        b.outlineColor = 'rgba(0, 40, 80, 0.8)';
        b.outlineWidth = 4;
        b.fontSize = 11;
        b.textColor = COLOR.dim;
        b.drawText('TURN', 0, py + 2, 62, 14, 'center');
        b.fontSize = 24;
        b.textColor = COLOR.accent;
        b.drawText(Math.max(1, $gameTroop.turnCount()), 0, py + 12, 62, 28, 'center');
        if (!battler) {
            b.fontSize = 18;
            b.textColor = '#ffffff';
            b.drawText('Battle Start', 74, py, w - 86, ph, 'left');
            return;
        }
        var label = {
            input: '▶ YOUR TURN',
            act: 'ACTING',
            enemy: 'ENEMY TURN',
            pet: 'PET ASSIST',
            next: 'NEXT UP'
        }[mode];
        var tx = ix + size + 10, tw = w - tx - 10;
        b.fontSize = 18;
        b.textColor = mode === 'enemy' ? '#ffd0d8' : '#ffffff';
        b.drawText(battler.name(), tx, py + 1, tw, 22, 'left');
        b.fontSize = 13;
        b.textColor = mode === 'next' ? COLOR.dim : tone;
        b.drawText(label, tx, py + 21, tw, 18, 'left');
    };

    //=========================================================================
    // Target marker above the selected enemy / hero
    //=========================================================================
    function Sprite_NovaTarget() { this.initialize.apply(this, arguments); }
    Sprite_NovaTarget.prototype = Object.create(Sprite.prototype);
    Sprite_NovaTarget.prototype.constructor = Sprite_NovaTarget;

    Sprite_NovaTarget.prototype.initialize = function(scene) {
        Sprite.prototype.initialize.call(this);
        this._scene = scene;
        this._key = '';
        this.bitmap = new Bitmap(220, 60);
        this.anchor.x = 0.5;
        this.anchor.y = 1;
        this.visible = false;
    };

    Sprite_NovaTarget.prototype.currentTarget = function() {
        var s = this._scene;
        if (s._enemyWindow.active && s._enemyWindow.visible) return s._enemyWindow.enemy();
        if (s._actorWindow.active && s._actorWindow.visible) return s._actorWindow.actor();
        return null;
    };

    Sprite_NovaTarget.prototype.spriteOf = function(battler) {
        var set = this._scene._spriteset;
        var list = battler.isActor() ? set._actorSprites : set._enemySprites;
        for (var i = 0; i < list.length; i++) if (list[i]._battler === battler) return list[i];
        return null;
    };

    Sprite_NovaTarget.prototype.update = function() {
        Sprite.prototype.update.call(this);
        var target = this.currentTarget();
        var sprite = target ? this.spriteOf(target) : null;
        this.visible = !!sprite;
        if (!sprite) { this._key = ''; return; }
        var field = this._scene._spriteset._battleField;
        var height = target.isActor() ? (sprite._mainSprite ? sprite._mainSprite.height : 64) : sprite.height;
        this.x = field.x + sprite.x;
        this.y = Math.max(TOP_H + 70, field.y + sprite.y - height - 4) + Math.sin(Graphics.frameCount / 8) * 4;
        var key = battlerKey(target) + ':' + target.hp;
        if (key !== this._key) { this._key = key; this.redraw(target); }
    };

    Sprite_NovaTarget.prototype.redraw = function(target) {
        var b = this.bitmap, ctx = ctxOf(b), w = b.width, isEnemy = target.isEnemy();
        var color = isEnemy ? ENEMY : TARGET;
        b.clear();
        b.fontSize = 16;
        var tagW = Math.min(w - 4, Math.max(90, b.measureTextWidth(target.name()) + 28));
        var tx = (w - tagW) / 2, th = isEnemy ? 32 : 24;
        var shape = panelShape(tx, 2, tagW, th, 6);
        ctx.fillStyle = 'rgba(6, 12, 26, 0.88)';
        pathPoly(ctx, shape); ctx.fill();
        ctx.lineWidth = 1.5;
        ctx.strokeStyle = color;
        pathPoly(ctx, shape); ctx.stroke();
        if (isEnemy) slantBar(ctx, tx + 10, 25, tagW - 20, 5, target.hp / Math.max(1, target.mhp), ['#ff8a8a', '#c0304a']);
        ctx.save();
        ctx.shadowColor = color;
        ctx.shadowBlur = 6;
        ctx.fillStyle = color;
        pathPoly(ctx, [[w / 2 - 10, th + 8], [w / 2 + 10, th + 8], [w / 2, th + 22]]);
        ctx.fill();
        ctx.restore();
        dirty(b);
        b.textColor = '#ffffff';
        b.outlineWidth = 3;
        b.outlineColor = 'rgba(0, 0, 0, 0.8)';
        b.drawText(target.name(), tx, 3, tagW, 20, 'center');
    };

    //=========================================================================
    // Scene_Battle layout
    //=========================================================================
    var _Scene_Battle_createDisplayObjects = Scene_Battle.prototype.createDisplayObjects;
    Scene_Battle.prototype.createDisplayObjects = function() {
        _Scene_Battle_createDisplayObjects.call(this);
        this._novaHud = new Sprite_NovaTurnHud();
        this.addChildAt(this._novaHud, this.children.indexOf(this._windowLayer));
        this._novaTarget = new Sprite_NovaTarget(this);
        this.addChild(this._novaTarget);
        var plain = [this._logWindow, this._statusWindow, this._actorWindow, this._actorCommandWindow,
                     this._messageWindow, this._scrollTextWindow].concat(this._messageWindow.subWindows());
        plain.forEach(function(win) { win._novaNoPanel = true; });
    };

    var _Scene_Battle_createLogWindow = Scene_Battle.prototype.createLogWindow;
    Scene_Battle.prototype.createLogWindow = function() {
        _Scene_Battle_createLogWindow.call(this);
        this._logWindow.y = TOP_H;
    };

    var _Scene_Battle_createActorCommandWindow = Scene_Battle.prototype.createActorCommandWindow;
    Scene_Battle.prototype.createActorCommandWindow = function() {
        _Scene_Battle_createActorCommandWindow.call(this);
        this._actorCommandWindow.setHandler('escape', this.commandEscape.bind(this));
    };

    var _Scene_Battle_createHelpWindow = Scene_Battle.prototype.createHelpWindow;
    Scene_Battle.prototype.createHelpWindow = function() {
        _Scene_Battle_createHelpWindow.call(this);
        this._helpWindow.move(12, TOP_H + 2, Graphics.boxWidth - 24, this._helpWindow.height);
        this._helpWindow.createContents();
    };

    Scene_Battle.prototype.novaListRect = function() {
        var y = this._helpWindow.y + this._helpWindow.height + 4;
        return { x: 12, y: y, width: Graphics.boxWidth - 24, height: statusTop() - y - 6 };
    };

    Scene_Battle.prototype.createSkillWindow = function() {
        var r = this.novaListRect();
        this._skillWindow = new Window_BattleSkill(r.x, r.y, r.width, r.height);
        this._skillWindow.setHelpWindow(this._helpWindow);
        this._skillWindow.setHandler('ok',     this.onSkillOk.bind(this));
        this._skillWindow.setHandler('cancel', this.onSkillCancel.bind(this));
        this.addWindow(this._skillWindow);
    };

    Scene_Battle.prototype.createItemWindow = function() {
        var r = this.novaListRect();
        this._itemWindow = new Window_BattleItem(r.x, r.y, r.width, r.height);
        this._itemWindow.setHelpWindow(this._helpWindow);
        this._itemWindow.setHandler('ok',     this.onItemOk.bind(this));
        this._itemWindow.setHandler('cancel', this.onItemCancel.bind(this));
        this.addWindow(this._itemWindow);
    };

    Scene_Battle.prototype.createActorWindow = function() {
        this._actorWindow = new Window_BattleActor(this._statusWindow.x, this._statusWindow.y);
        this._actorWindow.setHandler('ok',     this.onActorOk.bind(this));
        this._actorWindow.setHandler('cancel', this.onActorCancel.bind(this));
        this.addWindow(this._actorWindow);
    };

    Scene_Battle.prototype.createEnemyWindow = function() {
        this._enemyWindow = new Window_BattleEnemy(CMD_X, statusTop());
        this._enemyWindow.setHandler('ok',     this.onEnemyOk.bind(this));
        this._enemyWindow.setHandler('cancel', this.onEnemyCancel.bind(this));
        this.addWindow(this._enemyWindow);
    };

    // The cards stay where they are; nothing slides sideways.
    Scene_Battle.prototype.updateWindowPositions = function() {};

    var _Scene_Battle_update = Scene_Battle.prototype.update;
    Scene_Battle.prototype.update = function() {
        UI.skinWindows(this);
        if (ACTIVE) this.novaUpdateActiveTime();
        _Scene_Battle_update.call(this);
        this._statusWindow.visible = !this._actorWindow.visible;
        this._actorCommandWindow.visible = !this._enemyWindow.visible;   // the target list takes its place
    };

    // Active mode: time keeps running while a command is being chosen.
    Scene_Battle.prototype.novaUpdateActiveTime = function() {
        if (BattleManager.isInputting() && this.isActive() && !this.isBusy() && !BattleManager.isBusy() &&
                !$gameMessage.isBusy() && !$gameTroop.isEventRunning()) {
            BattleManager.novaTick();
        }
    };

    window.Sprite_NovaTurnHud = Sprite_NovaTurnHud;
})();
