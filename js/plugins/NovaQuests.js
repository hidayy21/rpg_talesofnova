//=============================================================================
// NovaQuests.js
//=============================================================================
/*:
 * @plugindesc Quest log in the main menu: the main story chapters and sub
 * quests, each with its current objective and a summary that grows as the
 * story moves on.
 * @author Project Nova
 *
 * @param Menu Command
 * @desc Name of the main menu command.
 * @default Quests
 *
 * @param Data File
 * @desc The quest list in the data folder (written by Project Nova_tools/quests.py).
 * @default Quests.json
 *
 * @help
 * Place below NovaMenu.
 *
 * The quests live in data/Quests.json (Project Nova_tools/quests.py writes it
 * from the story scripts). Each quest:
 *   { "id": "chapter1", "type": "main" | "sub", "title": "Chapter 1 - ...",
 *     "var": 3,          optional: the quest follows this game variable
 *     "done": 10,        optional: the step at which it counts as completed
 *     "steps": [ { "at": 1, "where": "Briarwood", "goal": "Find Tobin.",
 *                  "text": "A paragraph of the summary." }, ... ] }
 *
 * A quest shows up once its step reaches the first step's "at". Every step
 * reached adds its paragraph to the summary; the latest goal is the current
 * objective and the latest "where" the location under the title.
 *
 * With "var" the step is that variable, so the story events move the quest
 * on by themselves. Without it (sub quests) the step is kept in the save:
 *   Quest start <id>         start the quest (its first step)
 *   Quest step <id> <n>      move it to step n
 *   Quest complete <id>      complete it (step "done")
 *   Quest open               open the quest log
 * Script (conditional branches):  NovaQuests.step('id')  NovaQuests.isActive('id')
 *                                 NovaQuests.isDone('id')
 *
 * Controls: up/down picks a quest, left/right or Q/W switches the tab, OK
 * reads a long summary (up/down scrolls it; the mouse wheel works too).
 */

(function() {
    'use strict';

    var UI = window.NovaUI;
    if (!UI) {
        console.warn('NovaQuests: NovaMenu must be ON and placed above NovaQuests.');
        return;
    }

    var params = PluginManager.parameters('NovaQuests');
    var MENU_NAME = String(params['Menu Command'] || 'Quests');
    var DATA_FILE = String(params['Data File'] || 'Quests.json');
    var COLOR = UI.COLOR;
    var HEADER_H = 64;
    var TAB_H = 58;
    var LINE_H = 30;
    var TABS = [['main', 'Main Story'], ['sub', 'Sub Quests']];
    var GOLD = ['#f6e3a8', '#a7802f'], STEEL = ['#d8e8fb', '#34548f'];

    //=========================================================================
    // Data: data/Quests.json, loaded with the database (an empty list if it is missing)
    //=========================================================================
    window.$dataNovaQuests = null;

    var _loadDatabase = DataManager.loadDatabase;
    DataManager.loadDatabase = function() {
        _loadDatabase.call(this);
        window.$dataNovaQuests = null;
        var xhr = new XMLHttpRequest();
        xhr.open('GET', 'data/' + DATA_FILE);
        xhr.overrideMimeType('application/json');
        xhr.onload = function() {
            try { window.$dataNovaQuests = xhr.status < 400 ? JSON.parse(xhr.responseText) : []; }
            catch (e) { window.$dataNovaQuests = []; }
        };
        xhr.onerror = function() { window.$dataNovaQuests = []; };
        xhr.send();
    };

    var _isDatabaseLoaded = DataManager.isDatabaseLoaded;
    DataManager.isDatabaseLoaded = function() {
        return _isDatabaseLoaded.call(this) && !!window.$dataNovaQuests;
    };

    function allQuests() { return window.$dataNovaQuests || []; }
    function questById(id) { return allQuests().filter(function(q) { return q.id === id; })[0] || null; }

    //=========================================================================
    // Progress: the quest's variable, or the save (sub quests)
    //=========================================================================
    Game_System.prototype.novaQuests = function() { return (this._novaQuests = this._novaQuests || {}); };

    function stepOf(q) { return q.var ? $gameVariables.value(q.var) : ($gameSystem.novaQuests()[q.id] || 0); }
    function setStep(q, n) {
        if (q.var) $gameVariables.setValue(q.var, n);
        else $gameSystem.novaQuests()[q.id] = n;
    }
    function firstStep(q) { return q.steps && q.steps.length ? q.steps[0].at : 1; }
    function isStarted(q) { return stepOf(q) >= firstStep(q); }
    function isDone(q) { return q.done != null && stepOf(q) >= q.done; }
    function reached(q) {
        var n = stepOf(q);
        return (q.steps || []).filter(function(s) { return s.at <= n; });
    }
    function latest(q, key) {
        var steps = reached(q);
        for (var i = steps.length - 1; i >= 0; i--) if (steps[i][key]) return steps[i][key];
        return '';
    }

    // The quests a tab lists: the ones in progress first, then the completed ones; newest first in each.
    function questsOf(type) {
        var shown = allQuests().filter(function(q) { return (q.type || 'sub') === type && isStarted(q); }).reverse();
        return shown.filter(function(q) { return !isDone(q); }).concat(shown.filter(isDone));
    }

    window.NovaQuests = {
        step: function(id) { var q = questById(id); return q ? stepOf(q) : 0; },
        isActive: function(id) { var q = questById(id); return !!q && isStarted(q) && !isDone(q); },
        isDone: function(id) { var q = questById(id); return !!q && isDone(q); }
    };

    var _pluginCommand = Game_Interpreter.prototype.pluginCommand;
    Game_Interpreter.prototype.pluginCommand = function(command, args) {
        _pluginCommand.call(this, command, args);
        if (command !== 'Quest') return;
        var sub = String(args[0] || '').toLowerCase();
        if (sub === 'open') return SceneManager.push(Scene_NovaQuests);
        var q = questById(String(args[1] || ''));
        if (!q) return console.warn('NovaQuests: no quest "' + args[1] + '"');
        if (sub === 'start' && stepOf(q) < firstStep(q)) setStep(q, firstStep(q));
        else if (sub === 'step') setStep(q, Number(args[2] || 0));
        else if (sub === 'complete' && q.done != null) setStep(q, q.done);
    };

    //=========================================================================
    // Main menu command: the first one
    //=========================================================================
    var _addMainCommands = Window_MenuCommand.prototype.addMainCommands;
    Window_MenuCommand.prototype.addMainCommands = function() {
        this.addCommand(MENU_NAME, 'novaQuests', true);
        _addMainCommands.call(this);
    };

    var _createCommandWindow = Scene_Menu.prototype.createCommandWindow;
    Scene_Menu.prototype.createCommandWindow = function() {
        _createCommandWindow.call(this);
        this._commandWindow.setHandler('novaQuests', function() { SceneManager.push(Scene_NovaQuests); });
    };

    //=========================================================================
    // Drawing helpers
    //=========================================================================
    // Gold diamond with "!" for the main story, a steel-blue one for sub quests.
    function drawQuestIcon(bitmap, type, cx, cy, r, dim) {
        var ctx = UI.ctxOf(bitmap), main = type === 'main', c = main ? GOLD : STEEL;
        ctx.save();
        ctx.globalAlpha = dim ? 0.45 : 1;
        UI.pathPoly(ctx, [[cx, cy - r], [cx + r, cy], [cx, cy + r], [cx - r, cy]]);
        var g = ctx.createLinearGradient(0, cy - r, 0, cy + r);
        g.addColorStop(0, c[0]);
        g.addColorStop(1, c[1]);
        ctx.fillStyle = g;
        ctx.fill();
        ctx.lineWidth = 1.5;
        ctx.strokeStyle = COLOR.ink;
        ctx.stroke();
        ctx.fillStyle = COLOR.ink;
        if (main) {
            var bw = Math.max(2, r * 0.2);
            ctx.fillRect(cx - bw / 2, cy - r * 0.5, bw, r * 0.58);
            ctx.fillRect(cx - bw / 2, cy + r * 0.22, bw, bw);
        } else {
            UI.diamond(ctx, cx, cy, r * 0.38, COLOR.ink);
        }
        ctx.restore();
        UI.dirty(bitmap);
    }

    function drawCheck(bitmap, cx, cy, r) {
        var ctx = UI.ctxOf(bitmap);
        ctx.save();
        ctx.lineWidth = 1.5;
        ctx.strokeStyle = 'rgba(156, 192, 236, 0.6)';
        ctx.beginPath();
        ctx.arc(cx, cy, r, 0, Math.PI * 2);
        ctx.stroke();
        ctx.lineWidth = 2.5;
        ctx.strokeStyle = COLOR.accent;
        ctx.beginPath();
        ctx.moveTo(cx - r * 0.45, cy);
        ctx.lineTo(cx - r * 0.1, cy + r * 0.38);
        ctx.lineTo(cx + r * 0.5, cy - r * 0.38);
        ctx.stroke();
        ctx.restore();
        UI.dirty(bitmap);
    }

    // ">>" for a quest in progress.
    function drawChevrons(bitmap, x, cy, color) {
        var ctx = UI.ctxOf(bitmap);
        ctx.save();
        ctx.lineWidth = 2.5;
        ctx.strokeStyle = color;
        [0, 9].forEach(function(dx) {
            ctx.beginPath();
            ctx.moveTo(x + dx, cy - 8);
            ctx.lineTo(x + dx + 7, cy);
            ctx.lineTo(x + dx, cy + 8);
            ctx.stroke();
        });
        ctx.restore();
        UI.dirty(bitmap);
    }

    // A key hint box ("Q", "W").
    function drawKey(bitmap, key, x, cy) {
        var ctx = UI.ctxOf(bitmap);
        ctx.fillStyle = COLOR.ink;
        ctx.fillRect(x, cy - 11, 22, 22);
        ctx.lineWidth = 1;
        ctx.strokeStyle = COLOR.accent;
        ctx.strokeRect(x + 0.5, cy - 10.5, 21, 21);
        UI.dirty(bitmap);
        UI.titleFont(bitmap, 13);
        bitmap.textColor = COLOR.text;
        bitmap.outlineWidth = 0;
        bitmap.drawText(key, x, cy - 11, 22, 22, 'center');
    }

    function divider(bitmap, x, y, w) {
        var ctx = UI.ctxOf(bitmap);
        var g = ctx.createLinearGradient(x, 0, x + w, 0);
        g.addColorStop(0, 'rgba(156, 192, 236, 0.6)');
        g.addColorStop(1, 'rgba(156, 192, 236, 0)');
        ctx.fillStyle = g;
        ctx.fillRect(x + 6, y, w - 6, 1);
        UI.diamond(ctx, x + 4, y + 0.5, 4, COLOR.accent);
        UI.dirty(bitmap);
    }

    // Word wrap in the bitmap's current font; "\n" starts a new line.
    function wrap(bitmap, text, width) {
        var lines = [];
        String(text || '').split('\n').forEach(function(para) {
            var line = '';
            para.split(' ').forEach(function(word) {
                var next = line ? line + ' ' + word : word;
                if (line && bitmap.measureTextWidth(next) > width) {
                    lines.push(line);
                    line = word;
                } else {
                    line = next;
                }
            });
            lines.push(line);
        });
        return lines;
    }

    //=========================================================================
    // List (left): the tabs, then one row per quest
    //=========================================================================
    function Window_NovaQuestList() { this.initialize.apply(this, arguments); }
    Window_NovaQuestList.prototype = Object.create(Window_Selectable.prototype);
    Window_NovaQuestList.prototype.constructor = Window_NovaQuestList;

    Window_NovaQuestList.prototype.initialize = function(x, y, w, h) {
        this._tab = 0;
        this._quests = questsOf(TABS[0][0]);
        Window_Selectable.prototype.initialize.call(this, x, y, w, h);
        this.refresh();
        this.select(this._quests.length ? 0 : -1);
        this.activate();
    };

    Window_NovaQuestList.prototype.standardPadding = function() { return 12; };
    Window_NovaQuestList.prototype.maxItems = function() { return this._quests.length; };
    Window_NovaQuestList.prototype.itemHeight = function() { return 74; };
    Window_NovaQuestList.prototype.quest = function() { return this._quests[this.index()] || null; };
    Window_NovaQuestList.prototype.maxPageRows = function() {
        return Math.floor((this.height - this.padding * 2 - TAB_H) / this.itemHeight());
    };
    Window_NovaQuestList.prototype.itemRect = function(index) {
        var rect = Window_Selectable.prototype.itemRect.call(this, index);
        rect.y += TAB_H;
        return rect;
    };
    // a long summary can be read (focused); a short one has nothing more to show
    Window_NovaQuestList.prototype.isCurrentItemEnabled = function() {
        return !!this.quest() && !!this._infoWindow && this._infoWindow.canScroll();
    };
    Window_NovaQuestList.prototype.updateCursor = function() { this.setCursorRect(0, 0, 0, 0); };
    Window_NovaQuestList.prototype.select = function(index) {
        Window_Selectable.prototype.select.call(this, index);
        if (this.contents) this.refresh();
    };
    Window_NovaQuestList.prototype.activate = function() {
        Window_Selectable.prototype.activate.call(this);
        if (this.contents) this.refresh();
    };
    Window_NovaQuestList.prototype.deactivate = function() {
        Window_Selectable.prototype.deactivate.call(this);
        if (this.contents) this.refresh();
    };

    Window_NovaQuestList.prototype.switchTab = function(dir) {
        this._tab = (this._tab + dir + TABS.length) % TABS.length;
        this._quests = questsOf(TABS[this._tab][0]);
        SoundManager.playCursor();
        this.setTopRow(0);
        this.select(this._quests.length ? 0 : -1);
    };

    // left/right and Q/W switch the tab (also on an empty tab, where the list itself can't move)
    Window_NovaQuestList.prototype.processCursorMove = function() {
        if (this.isOpenAndActive()) {
            if (Input.isTriggered('left') || Input.isTriggered('pageup')) return this.switchTab(-1);
            if (Input.isTriggered('right') || Input.isTriggered('pagedown')) return this.switchTab(1);
        }
        Window_Selectable.prototype.processCursorMove.call(this);
    };

    Window_NovaQuestList.prototype.processTouch = function() {
        if (this.isOpenAndActive() && TouchInput.isTriggered()) {
            var x = this.canvasToLocalX(TouchInput.x) - this.padding;
            var y = this.canvasToLocalY(TouchInput.y) - this.padding;
            if (x >= 0 && x < this.contentsWidth() && y >= 0 && y < TAB_H) {
                var tab = Math.min(TABS.length - 1, Math.floor(x / (this.contentsWidth() / TABS.length)));
                if (tab !== this._tab) this.switchTab(tab - this._tab);
                return;
            }
        }
        Window_Selectable.prototype.processTouch.call(this);
    };

    Window_NovaQuestList.prototype.refresh = function() {
        if (!this.contents) return;
        Window_Selectable.prototype.refresh.call(this);
        this.drawTabs();
        if (this._quests.length === 0) {
            UI.bodyFont(this.contents, 19);
            this.contents.fontItalic = true;
            this.changeTextColor(COLOR.dim);
            var empty = this._tab === 0 ? 'The story has not begun yet.'
                                        : 'No sub quests yet. Keep an ear out around town.';
            this.contents.drawText(empty, 0, TAB_H + 24, this.contentsWidth(), 30, 'center');
            this.resetFontSettings();
        }
    };

    Window_NovaQuestList.prototype.drawTabs = function() {
        var bmp = this.contents, ctx = UI.ctxOf(bmp), w = this.contentsWidth();
        var cy = TAB_H / 2 - 4, keyW = 30, tabW = Math.floor((w - keyW * 2) / TABS.length);
        drawKey(bmp, 'Q', 0, cy);
        drawKey(bmp, 'W', w - 22, cy);
        TABS.forEach(function(tab, i) {
            var on = i === this._tab, x = keyW + i * tabW + 4, tw = tabW - 8, by = TAB_H - 14;
            if (on) {
                var g = ctx.createLinearGradient(0, 4, 0, by);
                g.addColorStop(0, 'rgba(156, 192, 236, 0)');
                g.addColorStop(1, 'rgba(156, 192, 236, 0.3)');
                ctx.fillStyle = g;
                ctx.fillRect(x, 4, tw, by - 4);
            }
            ctx.fillStyle = on ? COLOR.accentLit : 'rgba(156, 192, 236, 0.45)';
            ctx.fillRect(x, by, tw, on ? 3 : 1);
            UI.dirty(bmp);
            UI.titleFont(bmp, 17, on);
            var label = tab[1], lw = bmp.measureTextWidth(label), lx = x + (tw - lw - 28) / 2;
            drawQuestIcon(bmp, tab[0], lx + 10, cy, 10, !on);
            UI.titleFont(bmp, 17, on);
            bmp.textColor = on ? COLOR.accentLit : COLOR.dim;
            bmp.outlineWidth = 3;
            bmp.outlineColor = 'rgba(6, 10, 20, 0.7)';
            bmp.drawText(label, lx + 28, cy - 14, lw + 8, 28, 'left');
        }, this);
        this.resetFontSettings();
    };

    Window_NovaQuestList.prototype.drawItem = function(index) {
        var q = this._quests[index], rect = this.itemRect(index);
        var sel = index === this.index(), lit = sel && this.active, done = isDone(q);
        var bmp = this.contents, ctx = UI.ctxOf(bmp);
        var x = rect.x + 2, y = rect.y + 4, w = rect.width - 4, h = rect.height - 8;
        var g = ctx.createLinearGradient(x, 0, x + w, 0);
        if (sel) {
            g.addColorStop(0, lit ? 'rgba(96, 156, 220, 0.55)' : 'rgba(96, 156, 220, 0.3)');
            g.addColorStop(1, 'rgba(96, 156, 220, 0.06)');
        } else {
            g.addColorStop(0, 'rgba(156, 192, 236, 0.12)');
            g.addColorStop(1, 'rgba(156, 192, 236, 0.03)');
        }
        ctx.fillStyle = g;
        ctx.fillRect(x, y, w, h);
        ctx.lineWidth = 1;
        ctx.strokeStyle = sel ? (lit ? 'rgba(216, 232, 251, 0.8)' : 'rgba(156, 192, 236, 0.5)') : 'rgba(156, 192, 236, 0.18)';
        ctx.strokeRect(x + 0.5, y + 0.5, w - 1, h - 1);
        ctx.fillStyle = done ? 'rgba(156, 192, 236, 0.35)' : (q.type === 'main' ? GOLD[0] : COLOR.accent);
        ctx.fillRect(x, y, 3, h);
        UI.dirty(bmp);

        drawQuestIcon(bmp, q.type, x + 30, y + h / 2, 16, done);
        var tx = x + 58, tw = w - tx - 40;
        UI.titleFont(bmp, 20, sel);
        this.changeTextColor(done ? COLOR.dim : (sel ? COLOR.accentLit : COLOR.text));
        bmp.drawText(q.title, tx, y + 4, tw, 30, 'left');
        UI.bodyFont(bmp, 18);
        this.changeTextColor(COLOR.dim);
        bmp.drawText(done ? 'Completed' : latest(q, 'where'), tx, y + 32, tw, 26, 'left');
        if (done) drawCheck(bmp, x + w - 22, y + h / 2, 11);
        else drawChevrons(bmp, x + w - 30, y + h / 2, lit ? COLOR.accentLit : COLOR.accent);
        this.resetFontSettings();
    };

    Window_NovaQuestList.prototype.updateHelp = function() {};

    //=========================================================================
    // Details (right): title, location, current objective, then the summary (scrolls)
    //=========================================================================
    function Window_NovaQuestInfo() { this.initialize.apply(this, arguments); }
    Window_NovaQuestInfo.prototype = Object.create(Window_Base.prototype);
    Window_NovaQuestInfo.prototype.constructor = Window_NovaQuestInfo;

    Window_NovaQuestInfo.prototype.initialize = function(x, y, w, h) {
        Window_Base.prototype.initialize.call(this, x, y, w, h);
        this._quest = undefined;
        this._scroll = 0;
        this._maxScroll = 0;
        this.deactivate();
    };

    Window_NovaQuestInfo.prototype.standardPadding = function() { return 16; };
    Window_NovaQuestInfo.prototype.canScroll = function() { return this._maxScroll > 0; };
    Window_NovaQuestInfo.prototype.setBackHandler = function(fn) { this._onBack = fn; };

    Window_NovaQuestInfo.prototype.setQuest = function(q) {
        if (this._quest === q) return;
        this._quest = q;
        this._scroll = null;            // set by refresh: the newest text for a quest in progress, the start otherwise
        this.refresh();
    };

    Window_NovaQuestInfo.prototype.activate = function() {
        Window_Base.prototype.activate.call(this);
        this.refresh();
    };
    Window_NovaQuestInfo.prototype.deactivate = function() {
        Window_Base.prototype.deactivate.call(this);
        if (this.contents) this.refresh();
    };

    Window_NovaQuestInfo.prototype.label = function(text, y) {
        UI.titleFont(this.contents, 15);
        this.changeTextColor(COLOR.accent);
        this.contents.drawText(text, 6, y, 300, 24, 'left');
        this.resetFontSettings();
    };

    Window_NovaQuestInfo.prototype.refresh = function() {
        var bmp = this.contents, q = this._quest;
        bmp.clear();
        this._maxScroll = 0;
        if (!q) return;
        var w = this.contentsWidth(), done = isDone(q), y = 0;

        UI.titleFont(bmp, 28);
        this.changeTextColor(COLOR.text);
        bmp.drawText(q.title, 4, y, w - 8, 44, 'left');
        UI.bodyFont(bmp, 19);
        bmp.fontItalic = true;
        this.changeTextColor(COLOR.dim);
        var kind = q.type === 'main' ? 'Main Story' : 'Sub Quest';
        var where = done ? 'Completed' : latest(q, 'where');
        bmp.drawText(kind + (where ? '  ·  ' + where : ''), 6, y + 42, w - 12, 26, 'left');
        bmp.fontItalic = false;
        y += 80;
        divider(bmp, 0, y, w);
        y += 12;

        var goal = done ? '' : latest(q, 'goal');
        if (goal) {
            this.label('CURRENT OBJECTIVE', y);
            y += 30;
            UI.bodyFont(bmp, 21);
            this.changeTextColor(GOLD[0]);
            wrap(bmp, goal, w - 34).forEach(function(line, i) {
                if (i === 0) {
                    UI.diamond(UI.ctxOf(bmp), 12, y + LINE_H / 2, 5, GOLD[0]);
                    UI.dirty(bmp);
                }
                bmp.drawText(line, 28, y, w - 34, LINE_H, 'left');
                y += LINE_H;
            });
            y += 10;
            divider(bmp, 0, y, w);
            y += 12;
        }

        this.label('SUMMARY', y);
        y += 32;
        UI.bodyFont(bmp, 20);
        var lines = [];
        reached(q).forEach(function(step) {
            if (!step.text) return;
            if (lines.length) lines.push('');
            lines = lines.concat(wrap(bmp, step.text, w - 26));
        });
        var rows = Math.max(1, Math.floor((this.contentsHeight() - y) / LINE_H));
        this._maxScroll = Math.max(0, lines.length - rows);
        if (this._scroll === null) this._scroll = done ? 0 : this._maxScroll;
        this._scroll = this._scroll.clamp(0, this._maxScroll);
        this.changeTextColor('#d3deec');
        lines.slice(this._scroll, this._scroll + rows).forEach(function(line, i) {
            bmp.drawText(line, 6, y + i * LINE_H, w - 26, LINE_H, 'left');
        });
        if (this._maxScroll > 0) this.drawScrollBar(w - 6, y, rows * LINE_H, rows, lines.length);
        this.resetFontSettings();
    };

    Window_NovaQuestInfo.prototype.drawScrollBar = function(x, y, h, rows, total) {
        var ctx = UI.ctxOf(this.contents);
        var th = Math.max(24, Math.round(h * rows / total));
        var ty = y + Math.round((h - th) * this._scroll / this._maxScroll);
        ctx.fillStyle = 'rgba(156, 192, 236, 0.18)';
        ctx.fillRect(x, y, 3, h);
        ctx.fillStyle = this.active ? COLOR.accentLit : 'rgba(156, 192, 236, 0.6)';
        ctx.fillRect(x - 1, ty, 5, th);
        UI.dirty(this.contents);
    };

    Window_NovaQuestInfo.prototype.scrollBy = function(dir) {
        var next = (this._scroll + dir).clamp(0, this._maxScroll);
        if (next === this._scroll) return false;
        this._scroll = next;
        this.refresh();
        return true;
    };

    Window_NovaQuestInfo.prototype.update = function() {
        Window_Base.prototype.update.call(this);
        if (this.active && this._activeFrame !== Graphics.frameCount) {
            if (Input.isRepeated('down') && this.scrollBy(1)) SoundManager.playCursor();
            if (Input.isRepeated('up') && this.scrollBy(-1)) SoundManager.playCursor();
            if (Input.isTriggered('ok') || Input.isTriggered('cancel') || TouchInput.isCancelled()) {
                SoundManager.playCancel();
                this.deactivate();
                if (this._onBack) this._onBack();
            }
        }
        if (TouchInput.wheelY && this.isTouchedInside()) this.scrollBy(TouchInput.wheelY > 0 ? 1 : -1);
    };

    Window_NovaQuestInfo.prototype.isTouchedInside = function() {
        var x = this.canvasToLocalX(TouchInput.x), y = this.canvasToLocalY(TouchInput.y);
        return x >= 0 && y >= 0 && x < this.width && y < this.height;
    };

    //=========================================================================
    // Scene
    //=========================================================================
    function Scene_NovaQuests() { this.initialize.apply(this, arguments); }
    Scene_NovaQuests.prototype = Object.create(Scene_MenuBase.prototype);
    Scene_NovaQuests.prototype.constructor = Scene_NovaQuests;

    Scene_NovaQuests.prototype.create = function() {
        Scene_MenuBase.prototype.create.call(this);
        var w = Graphics.boxWidth, h = Graphics.boxHeight, listW = Math.floor(w * 0.42);
        this.createHeader(w);
        this._listWindow = new Window_NovaQuestList(12, HEADER_H + 4, listW, h - HEADER_H - 16);
        this._listWindow.setHandler('ok', this.onQuestOk.bind(this));
        this._listWindow.setHandler('cancel', this.popScene.bind(this));
        this.addWindow(this._listWindow);
        this._infoWindow = new Window_NovaQuestInfo(listW + 20, HEADER_H + 4, w - listW - 32, h - HEADER_H - 16);
        this._infoWindow.setBackHandler(this._listWindow.activate.bind(this._listWindow));
        this._listWindow._infoWindow = this._infoWindow;
        this.addWindow(this._infoWindow);
    };

    Scene_NovaQuests.prototype.createHeader = function(w) {
        var head = new Bitmap(w, HEADER_H);
        UI.drawHeader(head, MENU_NAME.toUpperCase());
        var started = allQuests().filter(isStarted), done = started.filter(isDone).length;
        UI.titleFont(head, 16, false);
        head.textColor = COLOR.dim;
        head.outlineWidth = 3;
        head.drawText('In progress ' + (started.length - done) + '     Completed ' + done, w - 420, 18, 400, 30, 'right');
        this.addChild(new Sprite(head));
    };

    Scene_NovaQuests.prototype.onQuestOk = function() {
        this._infoWindow._activeFrame = Graphics.frameCount;
        this._infoWindow.activate();
    };

    Scene_NovaQuests.prototype.update = function() {
        Scene_MenuBase.prototype.update.call(this);
        this._infoWindow.setQuest(this._listWindow.quest());
    };

    window.Scene_NovaQuests = Scene_NovaQuests;
})();
