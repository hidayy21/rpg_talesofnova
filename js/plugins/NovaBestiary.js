//=============================================================================
// NovaBestiary.js
//=============================================================================
/*:
 * @plugindesc Bestiary in the main menu: every enemy met, its weaknesses as
 * the party discovers them, and what it drops once defeated.
 * @author Project Nova
 *
 * @param Menu Command
 * @desc Name of the main menu command.
 * @default Bestiary
 *
 * @param Unknown Name
 * @desc Shown for enemies not met yet.
 * @default ??????
 *
 * @help
 * Place below NovaMenu and NovaBreak.
 *
 * The list holds every enemy in the database; the ones not met yet show as
 * "??????". An enemy counts as met when it appears in battle.
 *   - Met:      name, picture, Guard, weaknesses (each one shows once the
 *               party has hit it - see NovaBreak), description
 *   - Defeated: also max HP, EXP, gold and drops
 *
 * Enemy note tags (the same as RPG Maker's EnemyBook)
 *   <desc1:A giant bat that hunts at dusk.>   description, line 1
 *   <desc2:Weak to arrows.>                   description, line 2
 *   <book:no>                                 leave this enemy out
 *
 * Plugin commands
 *   Bestiary open        open the Bestiary
 *   Bestiary complete    mark every enemy as met and defeated (testing)
 *   Bestiary clear       forget everything
 */

(function() {
    'use strict';

    var UI = window.NovaUI;
    if (!UI) {
        console.warn('NovaBestiary: NovaMenu must be ON and placed above NovaBestiary.');
        return;
    }

    var params = PluginManager.parameters('NovaBestiary');
    var MENU_NAME = String(params['Menu Command'] || 'Bestiary');
    var UNKNOWN = String(params['Unknown Name'] || '??????');
    var COLOR = UI.COLOR;
    var HEADER_H = 64;

    function bookEnemies() {
        return $dataEnemies.filter(function(e) { return e && e.name && e.meta.book !== 'no'; });
    }

    //=========================================================================
    // What the party knows
    //=========================================================================
    Game_System.prototype.novaBook = function() {
        return (this._novaBook = this._novaBook || { seen: {}, defeated: {} });
    };
    Game_System.prototype.novaBookSeen = function(id) { return !!this.novaBook().seen[id]; };
    Game_System.prototype.novaBookDefeated = function(id) { return this.novaBook().defeated[id] || 0; };

    function markSeen(enemy) {
        if (!enemy.isHidden()) $gameSystem.novaBook().seen[enemy.enemyId()] = true;
    }

    var _onBattleStart = Game_Enemy.prototype.onBattleStart;
    Game_Enemy.prototype.onBattleStart = function() {
        _onBattleStart.call(this);
        markSeen(this);
    };

    var _appear = Game_Enemy.prototype.appear;
    Game_Enemy.prototype.appear = function() {
        _appear.call(this);
        markSeen(this);
    };

    var _die = Game_Enemy.prototype.die;
    Game_Enemy.prototype.die = function() {
        _die.call(this);
        var book = $gameSystem.novaBook(), id = this.enemyId();
        book.seen[id] = true;
        book.defeated[id] = (book.defeated[id] || 0) + 1;
    };

    var _pluginCommand = Game_Interpreter.prototype.pluginCommand;
    Game_Interpreter.prototype.pluginCommand = function(command, args) {
        _pluginCommand.call(this, command, args);
        if (command !== 'Bestiary') return;
        var book = $gameSystem.novaBook();
        switch (String(args[0] || '').toLowerCase()) {
        case 'open':
            SceneManager.push(Scene_NovaBestiary);
            break;
        case 'complete':
            bookEnemies().forEach(function(e) {
                book.seen[e.id] = true;
                book.defeated[e.id] = Math.max(1, book.defeated[e.id] || 0);
            });
            break;
        case 'clear':
            $gameSystem._novaBook = null;
            break;
        }
    };

    //=========================================================================
    // Main menu command
    //=========================================================================
    var _addOriginalCommands = Window_MenuCommand.prototype.addOriginalCommands;
    Window_MenuCommand.prototype.addOriginalCommands = function() {
        _addOriginalCommands.call(this);
        this.addCommand(MENU_NAME, 'novaBestiary', true);
    };

    var _createCommandWindow = Scene_Menu.prototype.createCommandWindow;
    Scene_Menu.prototype.createCommandWindow = function() {
        _createCommandWindow.call(this);
        this._commandWindow.setHandler('novaBestiary', function() { SceneManager.push(Scene_NovaBestiary); });
    };

    //=========================================================================
    // List (left): number and name, "??????" for enemies not met
    //=========================================================================
    function Window_NovaBookList() { this.initialize.apply(this, arguments); }
    Window_NovaBookList.prototype = Object.create(Window_Selectable.prototype);
    Window_NovaBookList.prototype.constructor = Window_NovaBookList;

    Window_NovaBookList.prototype.initialize = function(x, y, w, h) {
        this._enemies = bookEnemies();
        Window_Selectable.prototype.initialize.call(this, x, y, w, h);
        this.refresh();
        this.select(0);
        this.activate();
    };

    Window_NovaBookList.prototype.maxItems = function() { return this._enemies.length; };
    Window_NovaBookList.prototype.itemHeight = function() { return 40; };
    Window_NovaBookList.prototype.enemy = function() { return this._enemies[this.index()] || null; };

    Window_NovaBookList.prototype.drawItem = function(index) {
        var enemy = this._enemies[index], rect = this.itemRectForText(index);
        var seen = $gameSystem.novaBookSeen(enemy.id);
        this.resetFontSettings();
        this.contents.fontSize = 16;
        this.changeTextColor(COLOR.dim);
        this.contents.drawText(String(index + 1).padZero(3), rect.x, rect.y, 44, rect.height, 'left');
        UI.titleFont(this.contents, 18, seen);
        this.changeTextColor(seen ? COLOR.text : COLOR.dim);
        this.contents.drawText(seen ? enemy.name : UNKNOWN, rect.x + 48, rect.y, rect.width - 76, rect.height, 'left');
        if ($gameSystem.novaBookDefeated(enemy.id) > 0) {
            UI.diamond(UI.ctxOf(this.contents), rect.x + rect.width - 10, rect.y + rect.height / 2, 5, COLOR.accent);
            UI.dirty(this.contents);
        }
        this.resetFontSettings();
    };

    Window_NovaBookList.prototype.updateHelp = function() {};

    //=========================================================================
    // Details (right)
    //=========================================================================
    function Window_NovaBookInfo() { this.initialize.apply(this, arguments); }
    Window_NovaBookInfo.prototype = Object.create(Window_Base.prototype);
    Window_NovaBookInfo.prototype.constructor = Window_NovaBookInfo;

    Window_NovaBookInfo.prototype.initialize = function(x, y, w, h) {
        Window_Base.prototype.initialize.call(this, x, y, w, h);
        this._enemy = null;
    };

    Window_NovaBookInfo.prototype.setEnemy = function(enemy) {
        if (this._enemy === enemy) return;
        this._enemy = enemy;
        this.refresh();
    };

    Window_NovaBookInfo.prototype.drawDivider = function(y, w) {
        var ctx = UI.ctxOf(this.contents);
        var g = ctx.createLinearGradient(0, 0, w, 0);
        g.addColorStop(0, 'rgba(156, 192, 236, 0.6)');
        g.addColorStop(1, 'rgba(156, 192, 236, 0)');
        ctx.fillStyle = g;
        ctx.fillRect(6, y, w - 6, 1);
        UI.diamond(ctx, 4, y + 0.5, 4, COLOR.accent);
        UI.dirty(this.contents);
    };

    Window_NovaBookInfo.prototype.label = function(text, x, y, w) {
        UI.titleFont(this.contents, 15);
        this.changeTextColor(COLOR.accent);
        this.contents.drawText(text, x, y, w, 24, 'left');
        this.resetFontSettings();
    };

    Window_NovaBookInfo.prototype.refresh = function() {
        this.contents.clear();
        var e = this._enemy;
        if (!e) return;
        var w = this.contentsWidth(), textW = Math.floor(w * 0.55);
        var seen = $gameSystem.novaBookSeen(e.id), defeated = $gameSystem.novaBookDefeated(e.id);
        UI.titleFont(this.contents, 34);
        this.changeTextColor(seen ? COLOR.text : COLOR.dim);
        this.contents.drawText(seen ? e.name : UNKNOWN, 4, 0, textW, 48, 'left');
        this.resetFontSettings();
        this.contents.fontSize = 18;
        this.contents.fontItalic = true;
        this.changeTextColor(COLOR.dim);
        var sub = !seen ? 'Not met yet' : (defeated ? 'Defeated ' + defeated + (defeated === 1 ? ' time' : ' times') : 'Met, not defeated yet');
        this.contents.drawText(sub, 6, 46, textW, 26, 'left');
        this.contents.fontItalic = false;
        if (!seen) return;

        var y = 86;
        this.drawDivider(y, textW);
        y += 14;
        y = this.drawGuard(e, 6, y, textW);
        y += 10;
        this.drawDivider(y, textW);
        y += 14;
        y = this.drawRewards(e, defeated, 6, y, textW);

        // description along the bottom, full width
        var lines = [e.meta.desc1, e.meta.desc2].filter(function(t) { return t && t !== true; });
        if (lines.length) {
            var dy = this.contentsHeight() - lines.length * 28 - 18;
            this.drawDivider(dy, w);
            this.contents.fontSize = 19;
            this.changeTextColor('#d3deec');
            lines.forEach(function(t, i) { this.contents.drawText(t, 6, dy + 12 + i * 28, w - 12, 28, 'left'); }, this);
        }
        this.resetFontSettings();
    };

    Window_NovaBookInfo.prototype.drawGuard = function(e, x, y, w) {
        var NB = window.NovaBreak;
        this.label('GUARD', x, y, 120);
        this.label('WEAKNESSES', x + 120, y, w - 120);
        y += 30;
        if (!NB) {
            this.changeTextColor(COLOR.dim);
            this.contents.drawText('-', x, y, 100, 30, 'left');
            return y + 34;
        }
        var guard = e.meta.guard === undefined ? Number(PluginManager.parameters('NovaBreak')['Default Guard'] || 3) : Number(e.meta.guard);
        var ctx = UI.ctxOf(this.contents), cx = x + 16, cy = y + 16;
        UI.pathPoly(ctx, [[cx, cy - 16], [cx + 16, cy], [cx, cy + 16], [cx - 16, cy]]);
        ctx.fillStyle = COLOR.ink;
        ctx.fill();
        ctx.lineWidth = 1.5;
        ctx.strokeStyle = COLOR.accent;
        ctx.stroke();
        UI.dirty(this.contents);
        UI.titleFont(this.contents, 17);
        this.changeTextColor(COLOR.text);
        this.contents.drawText(guard, cx - 16, cy - 16, 32, 32, 'center');
        this.resetFontSettings();
        var weak = NB.weaknessesOf(e.id), self = this;
        if (weak.length === 0) {
            this.contents.fontSize = 18;
            this.changeTextColor(COLOR.dim);
            this.contents.drawText('None', x + 120, y, 120, 32, 'left');
        }
        weak.forEach(function(k, i) {
            NB.drawWeakIcon(self.contents, e.id, k, x + 120 + i * 36, y, 32, function() { self.refresh(); });
        });
        this.resetFontSettings();
        var found = weak.filter(function(k) { return $gameSystem.novaWeakSeen(e.id, k); }).length;
        if (weak.length > found) {
            this.contents.fontSize = 15;
            this.changeTextColor(COLOR.dim);
            this.contents.drawText('Hit it with the right element or weapon to find out.', x + 120, y + 36, w - 120, 22, 'left');
        }
        return y + 62;
    };

    Window_NovaBookInfo.prototype.drawRewards = function(e, defeated, x, y, w) {
        if (!defeated) {
            this.contents.fontSize = 17;
            this.changeTextColor(COLOR.dim);
            this.contents.drawText('Defeat it to learn its strength and spoils.', x, y, w, 28, 'left');
            return y + 32;
        }
        var stats = [[TextManager.param(0), e.params[0]], [TextManager.exp, e.exp], [TextManager.currencyUnit, e.gold]];
        var colW = Math.floor(w / 3);
        stats.forEach(function(s, i) {
            UI.titleFont(this.contents, 13, false);
            this.changeTextColor(COLOR.dim);
            this.contents.drawText(s[0], x + i * colW, y, colW - 8, 20, 'left');
            UI.bodyFont(this.contents, 24);
            this.changeTextColor(COLOR.text);
            this.contents.drawText(s[1], x + i * colW, y + 18, colW - 8, 30, 'left');
        }, this);
        this.resetFontSettings();
        y += 58;
        this.label('DROPS', x, y, w);
        y += 30;
        var drops = e.dropItems.filter(function(d) { return d.kind > 0 && d.dataId > 0; });
        if (drops.length === 0) {
            this.contents.fontSize = 18;
            this.changeTextColor(COLOR.dim);
            this.contents.drawText('Nothing', x, y, w, 30, 'left');
            return y + 32;
        }
        drops.forEach(function(d) {
            var item = [null, $dataItems, $dataWeapons, $dataArmors][d.kind][d.dataId];
            if (!item) return;
            this.drawIcon(item.iconIndex, x, y);
            this.contents.fontSize = 19;
            this.changeTextColor(COLOR.text);
            this.contents.drawText(item.name, x + 38, y, w - 110, 32, 'left');
            this.contents.fontSize = 15;
            this.changeTextColor(COLOR.dim);
            this.contents.drawText('1/' + d.denominator, x + 38, y, w - 44, 32, 'right');
            y += 36;
        }, this);
        return y;
    };

    //=========================================================================
    // Scene
    //=========================================================================
    function Scene_NovaBestiary() { this.initialize.apply(this, arguments); }
    Scene_NovaBestiary.prototype = Object.create(Scene_MenuBase.prototype);
    Scene_NovaBestiary.prototype.constructor = Scene_NovaBestiary;

    Scene_NovaBestiary.prototype.create = function() {
        Scene_MenuBase.prototype.create.call(this);
        var w = Graphics.boxWidth, h = Graphics.boxHeight, listW = Math.floor(w * 0.30);
        this.createHeader(w);
        this._listWindow = new Window_NovaBookList(12, HEADER_H + 4, listW, h - HEADER_H - 16);
        this._listWindow.setHandler('cancel', this.popScene.bind(this));
        this.addWindow(this._listWindow);
        this._infoWindow = new Window_NovaBookInfo(listW + 20, HEADER_H + 4, w - listW - 32, h - HEADER_H - 16);
        this.addWindow(this._infoWindow);
        // the enemy's picture, top right of the details
        this._picture = new Sprite();
        this._picture.anchor.x = 0.5;
        this._picture.anchor.y = 1;
        this._pictureBox = { x: this._infoWindow.x + this._infoWindow.width * 0.78, y: this._infoWindow.y + 330,
                             w: this._infoWindow.width * 0.40, h: 290 };
        this.addChild(this._picture);
    };

    Scene_NovaBestiary.prototype.createHeader = function(w) {
        var head = new Bitmap(w, HEADER_H);
        UI.drawHeader(head, MENU_NAME.toUpperCase());
        var all = bookEnemies(), seen = 0, beaten = 0;
        all.forEach(function(e) {
            if ($gameSystem.novaBookSeen(e.id)) seen++;
            if ($gameSystem.novaBookDefeated(e.id)) beaten++;
        });
        UI.titleFont(head, 16, false);
        head.textColor = COLOR.dim;
        head.outlineWidth = 3;
        head.drawText('Met ' + seen + ' / ' + all.length + '     Defeated ' + beaten, w - 420, 18, 400, 30, 'right');
        this.addChild(new Sprite(head));
    };

    Scene_NovaBestiary.prototype.update = function() {
        Scene_MenuBase.prototype.update.call(this);
        var enemy = this._listWindow.enemy();
        this._infoWindow.setEnemy(enemy);
        if (enemy !== this._shown) {
            this._shown = enemy;
            this.refreshPicture(enemy);
        }
    };

    Scene_NovaBestiary.prototype.refreshPicture = function(enemy) {
        var sprite = this._picture, box = this._pictureBox;
        sprite.bitmap = null;
        if (!enemy || !$gameSystem.novaBookSeen(enemy.id)) return;
        var bmp = $gameSystem.isSideView() ? ImageManager.loadSvEnemy(enemy.battlerName, enemy.battlerHue)
                                           : ImageManager.loadEnemy(enemy.battlerName, enemy.battlerHue);
        bmp.addLoadListener(function() {
            if (this._shown !== enemy) return;
            sprite.bitmap = bmp;
            var s = Math.min(1.5, box.w / bmp.width, box.h / bmp.height);
            sprite.scale.x = sprite.scale.y = s;
            sprite.x = box.x;
            sprite.y = box.y;
        }.bind(this));
    };

    window.Scene_NovaBestiary = Scene_NovaBestiary;
})();
