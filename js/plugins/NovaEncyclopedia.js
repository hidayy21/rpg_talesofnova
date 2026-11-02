//=============================================================================
// NovaEncyclopedia.js
//=============================================================================
/*:
 * @plugindesc Encyclopedia in the main menu: Characters (people met on the
 * journey), the Bestiary and Items (everything the party has found).
 * @author Project Nova
 *
 * @param Menu Command
 * @desc Name of the main menu command.
 * @default Encyclopedia
 *
 * @param Data File
 * @desc The character list in the data folder (written by Project Nova_tools/encyclopedia.py).
 * @default Characters.json
 *
 * @param Unknown Name
 * @desc Shown for characters and items not met or found yet.
 * @default ??????
 *
 * @help
 * Place below NovaMenu and NovaBestiary. Turn NovaBestiary's own "Show In
 * Menu" off: the Bestiary opens from here.
 *
 * Characters (data/Characters.json, from Project Nova_tools/encyclopedia.py)
 *   { "id": "kael", "name": "Kaelen Ashveil", "group": "Party",
 *     "title": "Class 3 Mage", "face": ["Actor4", 0], "picture": "Full_Kael",
 *     "facts": [["Age", "19"], ...],
 *     "unlock": { "var": 3, "at": 8 },      met when variable 3 >= 8
 *               { "switch": 12 } | { "always": true } | null (command only)
 *     "text": [ { "text": "A paragraph." },
 *               { "text": "Revealed later.", "unlock": { "var": 3, "at": 10 } } ] }
 *   "picture" is a full-body image in img/pictures (optional; otherwise the
 *   face is shown large). Once met, a character stays met.
 *
 * Items: every item, weapon and armor in the Database (with a name, and
 * without <book:no> in its note) shows up once the party has had one.
 *
 * Plugin commands
 *   Encyclopedia open             open the Encyclopedia
 *   Encyclopedia meet kael        mark a character as met
 *   Encyclopedia complete         meet everyone, find every item (testing)
 */

(function() {
    'use strict';

    var UI = window.NovaUI;
    if (!UI) {
        console.warn('NovaEncyclopedia: NovaMenu must be ON and placed above NovaEncyclopedia.');
        return;
    }

    var params = PluginManager.parameters('NovaEncyclopedia');
    var MENU_NAME = String(params['Menu Command'] || 'Encyclopedia');
    var DATA_FILE = String(params['Data File'] || 'Characters.json');
    var UNKNOWN = String(params['Unknown Name'] || '??????');
    var COLOR = UI.COLOR;
    var HEADER_H = 64, TAB_H = 58, LINE_H = 30;

    //=========================================================================
    // Data: data/Characters.json, loaded with the database (an empty list if it is missing)
    //=========================================================================
    window.$dataNovaCharacters = null;

    var _loadDatabase = DataManager.loadDatabase;
    DataManager.loadDatabase = function() {
        _loadDatabase.call(this);
        window.$dataNovaCharacters = null;
        var xhr = new XMLHttpRequest();
        xhr.open('GET', 'data/' + DATA_FILE);
        xhr.overrideMimeType('application/json');
        xhr.onload = function() {
            try { window.$dataNovaCharacters = xhr.status < 400 ? JSON.parse(xhr.responseText) : []; }
            catch (e) { window.$dataNovaCharacters = []; }
        };
        xhr.onerror = function() { window.$dataNovaCharacters = []; };
        xhr.send();
    };

    var _isDatabaseLoaded = DataManager.isDatabaseLoaded;
    DataManager.isDatabaseLoaded = function() {
        return _isDatabaseLoaded.call(this) && !!window.$dataNovaCharacters;
    };

    //=========================================================================
    // What the party knows
    //=========================================================================
    Game_System.prototype.novaCodex = function() {
        return (this._novaCodex = this._novaCodex || { met: {}, found: {} });
    };

    function condMet(c) {
        if (!c) return false;
        if (c.always) return true;
        if (c['var']) return $gameVariables.value(c['var']) >= (c.at || 0);
        if (c['switch']) return $gameSwitches.value(c['switch']);
        return false;
    }

    function characters() { return window.$dataNovaCharacters || []; }
    function isMet(ch) {
        var met = $gameSystem.novaCodex().met;
        if (!met[ch.id] && condMet(ch.unlock)) met[ch.id] = true;
        return !!met[ch.id];
    }
    function paragraphs(ch) {
        return (ch.text || []).filter(function(p) { return !p.unlock || condMet(p.unlock); })
                              .map(function(p) { return p.text; });
    }

    // Items: kind 'item' | 'key' | 'weapon' | 'armor'
    function kindOf(item) {
        if (DataManager.isWeapon(item)) return 'weapon';
        if (DataManager.isArmor(item)) return 'armor';
        return item.itypeId === 2 ? 'key' : 'item';
    }
    function keyOf(item) { return (DataManager.isWeapon(item) ? 'w' : DataManager.isArmor(item) ? 'a' : 'i') + item.id; }
    function listed(item) {
        if (!item || !item.name || /^[-=*]/.test(item.name) || item.meta.book === 'no') return false;
        return !DataManager.isItem(item) || item.itypeId <= 2;       // hidden item types A/B stay out
    }
    function itemsOf(kind) {
        var db = kind === 'weapon' ? $dataWeapons : kind === 'armor' ? $dataArmors : $dataItems;
        return db.filter(function(it) { return listed(it) && kindOf(it) === kind; });
    }
    function isFound(item) { return !!$gameSystem.novaCodex().found[keyOf(item)]; }
    function markFound(item) { if (item && listed(item)) $gameSystem.novaCodex().found[keyOf(item)] = true; }

    var _gainItem = Game_Party.prototype.gainItem;
    Game_Party.prototype.gainItem = function(item, amount, includeEquip) {
        _gainItem.call(this, item, amount, includeEquip);
        if (item && amount > 0) markFound(item);
    };

    // what the party already carries counts as found too (older saves, starting equipment)
    function backfill() {
        $gameParty.allItems().forEach(markFound);
        $gameParty.members().forEach(function(a) { a.equips().forEach(markFound); });
    }

    function bookEnemies() {
        return $dataEnemies.filter(function(e) { return e && e.name && e.meta.book !== 'no'; });
    }

    var TABS = [['item', 'Items'], ['weapon', 'Weapons'], ['armor', 'Armor'], ['key', 'Key Items']];

    function counts() {
        var chars = characters(), items = [];
        TABS.forEach(function(t) { items = items.concat(itemsOf(t[0])); });
        var enemies = bookEnemies(), seen = 0;
        if ($gameSystem.novaBookSeen) enemies.forEach(function(e) { if ($gameSystem.novaBookSeen(e.id)) seen++; });
        return {
            chars: [chars.filter(isMet).length, chars.length],
            enemies: [seen, enemies.length],
            items: [items.filter(isFound).length, items.length]
        };
    }

    var _pluginCommand = Game_Interpreter.prototype.pluginCommand;
    Game_Interpreter.prototype.pluginCommand = function(command, args) {
        _pluginCommand.call(this, command, args);
        if (command !== 'Encyclopedia') return;
        var codex = $gameSystem.novaCodex();
        switch (String(args[0] || '').toLowerCase()) {
        case 'open':
            SceneManager.push(Scene_NovaEncyclopedia);
            break;
        case 'meet':
            if (args[1]) codex.met[String(args[1]).toLowerCase()] = true;
            break;
        case 'complete':
            characters().forEach(function(ch) { codex.met[ch.id] = true; });
            TABS.forEach(function(t) { itemsOf(t[0]).forEach(markFound); });
            break;
        }
    };

    //=========================================================================
    // Main menu command (where the Bestiary used to be)
    //=========================================================================
    var _addOriginalCommands = Window_MenuCommand.prototype.addOriginalCommands;
    Window_MenuCommand.prototype.addOriginalCommands = function() {
        _addOriginalCommands.call(this);
        this.addCommand(MENU_NAME, 'novaEncyclopedia', true);
    };

    var _createCommandWindow = Scene_Menu.prototype.createCommandWindow;
    Scene_Menu.prototype.createCommandWindow = function() {
        _createCommandWindow.call(this);
        this._commandWindow.setHandler('novaEncyclopedia', function() { SceneManager.push(Scene_NovaEncyclopedia); });
    };

    //=========================================================================
    // Drawing helpers
    //=========================================================================
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

    function label(bitmap, text, x, y, w) {
        UI.titleFont(bitmap, 15);
        bitmap.textColor = COLOR.accent;
        bitmap.outlineWidth = 3;
        bitmap.outlineColor = 'rgba(6, 10, 20, 0.7)';
        bitmap.drawText(text, x, y, w, 24, 'left');
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

    // A face (144x144 cell) scaled into a square; redraws the window once the sheet has loaded.
    function drawFace(win, name, index, x, y, size) {
        var bmp = ImageManager.loadFace(name);
        if (!bmp.isReady()) {
            if (!win._novaWaiting) {
                win._novaWaiting = true;
                bmp.addLoadListener(function() { win._novaWaiting = false; win.refresh(); });
            }
            return;
        }
        var fw = Window_Base._faceWidth, fh = Window_Base._faceHeight;
        win.contents.blt(bmp, index % 4 * fw, Math.floor(index / 4) * fh, fw, fh, x, y, size, size);
    }

    function drawFrame(bitmap, x, y, w, h, lit) {
        var ctx = UI.ctxOf(bitmap);
        ctx.lineWidth = 1;
        ctx.strokeStyle = lit ? 'rgba(216, 232, 251, 0.8)' : 'rgba(156, 192, 236, 0.45)';
        ctx.strokeRect(x + 0.5, y + 0.5, w - 1, h - 1);
        UI.dirty(bitmap);
    }

    // A dark diamond with "?" for someone not met yet.
    function drawUnknown(bitmap, cx, cy, r) {
        var ctx = UI.ctxOf(bitmap);
        UI.pathPoly(ctx, [[cx, cy - r], [cx + r, cy], [cx, cy + r], [cx - r, cy]]);
        ctx.fillStyle = COLOR.ink;
        ctx.fill();
        ctx.lineWidth = 1.5;
        ctx.strokeStyle = 'rgba(156, 192, 236, 0.5)';
        ctx.stroke();
        UI.dirty(bitmap);
        UI.titleFont(bitmap, Math.round(r * 0.9));
        bitmap.textColor = COLOR.dim;
        bitmap.outlineWidth = 0;
        bitmap.drawText('?', cx - r, cy - r, r * 2, r * 2, 'center');
    }

    function drawRow(bitmap, rect, sel, lit) {
        var ctx = UI.ctxOf(bitmap), x = rect.x + 2, y = rect.y + 3, w = rect.width - 4, h = rect.height - 6;
        var g = ctx.createLinearGradient(x, 0, x + w, 0);
        if (sel) {
            g.addColorStop(0, lit ? 'rgba(96, 156, 220, 0.55)' : 'rgba(96, 156, 220, 0.3)');
            g.addColorStop(1, 'rgba(96, 156, 220, 0.06)');
        } else {
            g.addColorStop(0, 'rgba(156, 192, 236, 0.10)');
            g.addColorStop(1, 'rgba(156, 192, 236, 0.02)');
        }
        ctx.fillStyle = g;
        ctx.fillRect(x, y, w, h);
        UI.dirty(bitmap);
        drawFrame(bitmap, x, y, w, h, sel && lit);
        return { x: x, y: y, w: w, h: h };
    }

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

    function drawIconScaled(bitmap, index, x, y, size) {
        var set = ImageManager.loadSystem('IconSet'), iw = Window_Base._iconWidth, ih = Window_Base._iconHeight;
        bitmap.blt(set, index % 16 * iw, Math.floor(index / 16) * ih, iw, ih, x, y, size, size);
    }

    function header(scene, title, right) {
        var w = Graphics.boxWidth, head = new Bitmap(w, HEADER_H);
        UI.drawHeader(head, title.toUpperCase());
        if (right) {
            UI.titleFont(head, 16, false);
            head.textColor = COLOR.dim;
            head.outlineWidth = 3;
            head.drawText(right, w - 420, 18, 400, 30, 'right');
        }
        scene.addChild(new Sprite(head));
    }

    //=========================================================================
    // A details window that scrolls its text (OK on the list to read, up/down, OK/cancel back)
    //=========================================================================
    function Window_NovaCodexInfo() { this.initialize.apply(this, arguments); }
    Window_NovaCodexInfo.prototype = Object.create(Window_Base.prototype);
    Window_NovaCodexInfo.prototype.constructor = Window_NovaCodexInfo;

    Window_NovaCodexInfo.prototype.initialize = function(x, y, w, h) {
        Window_Base.prototype.initialize.call(this, x, y, w, h);
        this._entry = undefined;
        this._scroll = 0;
        this._maxScroll = 0;
        this.deactivate();
    };

    Window_NovaCodexInfo.prototype.standardPadding = function() { return 16; };
    Window_NovaCodexInfo.prototype.canScroll = function() { return this._maxScroll > 0; };
    Window_NovaCodexInfo.prototype.setBackHandler = function(fn) { this._onBack = fn; };

    Window_NovaCodexInfo.prototype.setEntry = function(entry) {
        if (this._entry === entry) return;
        this._entry = entry;
        this._scroll = 0;
        this.refresh();
    };

    Window_NovaCodexInfo.prototype.activate = function() {
        Window_Base.prototype.activate.call(this);
        this.refresh();
    };
    Window_NovaCodexInfo.prototype.deactivate = function() {
        Window_Base.prototype.deactivate.call(this);
        if (this.contents) this.refresh();
    };

    // The scrolling text block from y down, `width` wide: returns nothing, sets _maxScroll.
    Window_NovaCodexInfo.prototype.drawBody = function(lines, x, y, width) {
        var rows = Math.max(1, Math.floor((this.contentsHeight() - y) / LINE_H));
        this._maxScroll = Math.max(0, lines.length - rows);
        this._scroll = this._scroll.clamp(0, this._maxScroll);
        this.changeTextColor('#d3deec');
        lines.slice(this._scroll, this._scroll + rows).forEach(function(line, i) {
            this.contents.drawText(line, x, y + i * LINE_H, width, LINE_H, 'left');
        }, this);
        if (this._maxScroll > 0) this.drawScrollBar(x + width + 8, y, rows * LINE_H, rows, lines.length);
    };

    Window_NovaCodexInfo.prototype.drawScrollBar = function(x, y, h, rows, total) {
        var ctx = UI.ctxOf(this.contents);
        var th = Math.max(24, Math.round(h * rows / total));
        var ty = y + Math.round((h - th) * this._scroll / this._maxScroll);
        ctx.fillStyle = 'rgba(156, 192, 236, 0.18)';
        ctx.fillRect(x, y, 3, h);
        ctx.fillStyle = this.active ? COLOR.accentLit : 'rgba(156, 192, 236, 0.6)';
        ctx.fillRect(x - 1, ty, 5, th);
        UI.dirty(this.contents);
    };

    Window_NovaCodexInfo.prototype.scrollBy = function(dir) {
        var next = (this._scroll + dir).clamp(0, this._maxScroll);
        if (next === this._scroll) return false;
        this._scroll = next;
        this.refresh();
        return true;
    };

    Window_NovaCodexInfo.prototype.update = function() {
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

    Window_NovaCodexInfo.prototype.isTouchedInside = function() {
        var x = this.canvasToLocalX(TouchInput.x), y = this.canvasToLocalY(TouchInput.y);
        return x >= 0 && y >= 0 && x < this.width && y < this.height;
    };

    // A list whose OK reads a long text in the details window.
    function readable(ListClass) {
        ListClass.prototype.isCurrentItemEnabled = function() {
            return !!this._infoWindow && this._infoWindow.canScroll();
        };
        ListClass.prototype.updateHelp = function() {};
        ListClass.prototype.updateCursor = function() { this.setCursorRect(0, 0, 0, 0); };
        ['select', 'activate', 'deactivate'].forEach(function(fn) {
            ListClass.prototype[fn] = function() {
                Window_Selectable.prototype[fn].apply(this, arguments);
                if (this.contents) this.refresh();
            };
        });
    }

    function readScene(scene) {
        scene._infoWindow.setBackHandler(scene._listWindow.activate.bind(scene._listWindow));
        scene._listWindow._infoWindow = scene._infoWindow;
        scene._listWindow.setHandler('ok', function() {
            scene._infoWindow._activeFrame = Graphics.frameCount;
            scene._infoWindow.activate();
        });
        scene._listWindow.setHandler('cancel', scene.popScene.bind(scene));
    }

    //=========================================================================
    // Hub: three cards
    //=========================================================================
    var SECTIONS = [
        { key: 'chars', name: 'Characters', icon: 82, blurb: 'The people met on the journey.', verb: 'Met' },
        { key: 'enemies', name: 'Bestiary', icon: 5, blurb: 'Every creature faced in battle.', verb: 'Met' },
        { key: 'items', name: 'Items', icon: 176, blurb: 'Everything the party has found.', verb: 'Found' }
    ];

    function Window_NovaCodexHub() { this.initialize.apply(this, arguments); }
    Window_NovaCodexHub.prototype = Object.create(Window_Selectable.prototype);
    Window_NovaCodexHub.prototype.constructor = Window_NovaCodexHub;

    Window_NovaCodexHub.prototype.initialize = function(x, y, w, h) {
        this._counts = counts();
        Window_Selectable.prototype.initialize.call(this, x, y, w, h);
        this._novaNoPanel = true;
        this.opacity = 0;
        this.refresh();
        this.select(0);
        this.activate();
    };

    Window_NovaCodexHub.prototype.maxItems = function() { return SECTIONS.length; };
    Window_NovaCodexHub.prototype.maxCols = function() { return SECTIONS.length; };
    Window_NovaCodexHub.prototype.spacing = function() { return 24; };
    Window_NovaCodexHub.prototype.itemHeight = function() { return this.contentsHeight(); };
    Window_NovaCodexHub.prototype.updateCursor = function() { this.setCursorRect(0, 0, 0, 0); };
    Window_NovaCodexHub.prototype.select = function(index) {
        Window_Selectable.prototype.select.call(this, index);
        if (this.contents) this.refresh();
    };

    Window_NovaCodexHub.prototype.drawItem = function(index) {
        var s = SECTIONS[index], rect = this.itemRect(index), sel = index === this.index();
        var bmp = this.contents, ctx = UI.ctxOf(bmp);
        var x = rect.x, y = rect.y, w = rect.width, h = rect.height, cx = x + w / 2;
        UI.pathPoly(ctx, UI.panelShape(x + 1, y + 1, w - 2, h - 2, 14));
        var g = ctx.createLinearGradient(0, y, 0, y + h);
        g.addColorStop(0, sel ? 'rgba(46, 78, 136, 0.96)' : COLOR.panelTop);
        g.addColorStop(1, COLOR.panelBottom);
        ctx.fillStyle = g;
        ctx.fill();
        ctx.lineWidth = sel ? 2 : 1;
        ctx.strokeStyle = sel ? COLOR.accentLit : COLOR.frame;
        ctx.stroke();
        // emblem: a diamond with the section's icon
        var ey = y + h * 0.3, r = Math.min(64, w * 0.24);
        UI.pathPoly(ctx, [[cx, ey - r], [cx + r, ey], [cx, ey + r], [cx - r, ey]]);
        var eg = ctx.createLinearGradient(0, ey - r, 0, ey + r);
        eg.addColorStop(0, sel ? 'rgba(156, 192, 236, 0.45)' : 'rgba(156, 192, 236, 0.2)');
        eg.addColorStop(1, 'rgba(11, 17, 32, 0.9)');
        ctx.fillStyle = eg;
        ctx.fill();
        ctx.lineWidth = 1.5;
        ctx.strokeStyle = sel ? COLOR.accentLit : COLOR.accent;
        ctx.stroke();
        UI.dirty(bmp);
        drawIconScaled(bmp, s.icon, cx - 32, ey - 32, 64);

        UI.titleFont(bmp, 26, sel);
        bmp.textColor = sel ? COLOR.accentLit : COLOR.text;
        bmp.outlineWidth = 3;
        bmp.outlineColor = 'rgba(6, 10, 20, 0.7)';
        bmp.drawText(s.name, x, y + h * 0.55, w, 40, 'center');
        divider(bmp, x + w * 0.2, y + h * 0.55 + 46, w * 0.6);
        var c = this._counts[s.key];
        UI.titleFont(bmp, 18, false);
        bmp.textColor = COLOR.pending;
        bmp.drawText(s.verb + '  ' + c[0] + ' / ' + c[1], x, y + h * 0.55 + 58, w, 30, 'center');
        UI.bodyFont(bmp, 19);
        bmp.fontItalic = true;
        bmp.textColor = COLOR.dim;
        bmp.drawText(s.blurb, x + 12, y + h * 0.55 + 96, w - 24, 28, 'center');
        bmp.fontItalic = false;
        this.resetFontSettings();
    };

    Window_NovaCodexHub.prototype.refreshCounts = function() {
        this._counts = counts();
        this.refresh();
    };

    function Scene_NovaEncyclopedia() { this.initialize.apply(this, arguments); }
    Scene_NovaEncyclopedia.prototype = Object.create(Scene_MenuBase.prototype);
    Scene_NovaEncyclopedia.prototype.constructor = Scene_NovaEncyclopedia;

    Scene_NovaEncyclopedia.prototype.create = function() {
        Scene_MenuBase.prototype.create.call(this);
        backfill();
        var w = Graphics.boxWidth, h = Graphics.boxHeight, cardH = Math.min(420, h - HEADER_H - 80);
        header(this, MENU_NAME);
        this._hub = new Window_NovaCodexHub(24, HEADER_H + Math.floor((h - HEADER_H - cardH) / 2) - 18, w - 48, cardH + 36);
        this._hub.select(Scene_NovaEncyclopedia.lastIndex || 0);      // back from a section: still on it
        this._hub.setHandler('ok', this.onOpen.bind(this));
        this._hub.setHandler('cancel', function() {
            Scene_NovaEncyclopedia.lastIndex = 0;
            this.popScene();
        }.bind(this));
        this.addWindow(this._hub);
    };

    Scene_NovaEncyclopedia.prototype.start = function() {
        Scene_MenuBase.prototype.start.call(this);
        this._hub.refreshCounts();
        this._hub.activate();
    };

    Scene_NovaEncyclopedia.prototype.onOpen = function() {
        Scene_NovaEncyclopedia.lastIndex = this._hub.index();
        var key = SECTIONS[this._hub.index()].key;
        if (key === 'chars') SceneManager.push(Scene_NovaCharacters);
        else if (key === 'items') SceneManager.push(Scene_NovaItems);
        else if (window.Scene_NovaBestiary) SceneManager.push(window.Scene_NovaBestiary);
        else this._hub.activate();
    };

    //=========================================================================
    // Characters
    //=========================================================================
    function Window_NovaCharList() { this.initialize.apply(this, arguments); }
    Window_NovaCharList.prototype = Object.create(Window_Selectable.prototype);
    Window_NovaCharList.prototype.constructor = Window_NovaCharList;
    readable(Window_NovaCharList);

    Window_NovaCharList.prototype.initialize = function(x, y, w, h) {
        this._chars = characters();
        Window_Selectable.prototype.initialize.call(this, x, y, w, h);
        this.refresh();
        this.select(this._chars.length ? 0 : -1);
        this.activate();
    };

    Window_NovaCharList.prototype.standardPadding = function() { return 12; };
    Window_NovaCharList.prototype.maxItems = function() { return this._chars.length; };
    Window_NovaCharList.prototype.itemHeight = function() { return 64; };
    Window_NovaCharList.prototype.entry = function() { return this._chars[this.index()] || null; };

    Window_NovaCharList.prototype.drawItem = function(index) {
        var ch = this._chars[index], sel = index === this.index(), met = isMet(ch);
        var r = drawRow(this.contents, this.itemRect(index), sel, this.active), bmp = this.contents;
        var fs = r.h - 8;
        if (met && ch.face) {
            drawFace(this, ch.face[0], ch.face[1], r.x + 4, r.y + 4, fs);
            drawFrame(bmp, r.x + 4, r.y + 4, fs, fs, false);
        } else {
            drawUnknown(bmp, r.x + 4 + fs / 2, r.y + r.h / 2, fs / 2 - 4);
        }
        var tx = r.x + fs + 14, tw = r.w - fs - 20;
        UI.titleFont(bmp, 18, sel);
        this.changeTextColor(met ? (sel ? COLOR.accentLit : COLOR.text) : COLOR.dim);
        bmp.drawText(met ? ch.name : UNKNOWN, tx, r.y + 2, tw, 28, 'left');
        UI.bodyFont(bmp, 16);
        this.changeTextColor(COLOR.dim);
        bmp.drawText(ch.group || '', tx, r.y + 28, tw, 24, 'left');
        this.resetFontSettings();
    };

    function Window_NovaCharInfo() { this.initialize.apply(this, arguments); }
    Window_NovaCharInfo.prototype = Object.create(Window_NovaCodexInfo.prototype);
    Window_NovaCharInfo.prototype.constructor = Window_NovaCharInfo;

    // with a full-body picture the text keeps to the left; the picture is a sprite of the scene
    Window_NovaCharInfo.prototype.textWidth = function(ch) {
        return this.contentsWidth() - (ch && ch.picture ? Math.floor(this.contentsWidth() * 0.36) : 0) - 16;
    };

    Window_NovaCharInfo.prototype.refresh = function() {
        var bmp = this.contents, ch = this._entry;
        bmp.clear();
        this._maxScroll = 0;
        if (!ch) return;
        var met = isMet(ch), w = this.textWidth(ch), y = 0;
        var faceBig = met && !ch.picture && ch.face ? 120 : 0, nameW = w - (faceBig ? faceBig + 16 : 0);
        UI.titleFont(bmp, 30);
        this.changeTextColor(met ? COLOR.text : COLOR.dim);
        bmp.drawText(met ? ch.name : UNKNOWN, 4, y, nameW, 44, 'left');
        UI.bodyFont(bmp, 19);
        bmp.fontItalic = true;
        this.changeTextColor(COLOR.dim);
        bmp.drawText(met ? [ch.title, ch.group].filter(Boolean).join('  ·  ') : (ch.group || '') + '  ·  Not met yet',
                     6, y + 42, nameW, 26, 'left');
        bmp.fontItalic = false;
        if (faceBig) {
            drawFace(this, ch.face[0], ch.face[1], this.contentsWidth() - faceBig - 8, 4, faceBig);
            drawFrame(bmp, this.contentsWidth() - faceBig - 8, 4, faceBig, faceBig, true);
        }
        if (!met) return;
        y += 80;
        var facts = ch.facts || [];
        if (facts.length) {
            divider(bmp, 0, y, nameW);
            y += 12;
            facts.forEach(function(f) {
                label(bmp, f[0].toUpperCase(), 6, y + 3, 130);
                UI.bodyFont(bmp, 19);
                this.changeTextColor(COLOR.text);
                bmp.drawText(f[1], 140, y, nameW - 140, 30, 'left');
                y += 30;
            }, this);
            y += 8;
        }
        y = Math.max(y, faceBig ? faceBig + 16 : 0);
        divider(bmp, 0, y, w);
        y += 14;
        UI.bodyFont(bmp, 20);
        var lines = [];
        paragraphs(ch).forEach(function(t) {
            if (lines.length) lines.push('');
            lines = lines.concat(wrap(bmp, t, w - 12));
        });
        this.drawBody(lines, 6, y, w - 12);
        this.resetFontSettings();
    };

    function Scene_NovaCharacters() { this.initialize.apply(this, arguments); }
    Scene_NovaCharacters.prototype = Object.create(Scene_MenuBase.prototype);
    Scene_NovaCharacters.prototype.constructor = Scene_NovaCharacters;

    Scene_NovaCharacters.prototype.create = function() {
        Scene_MenuBase.prototype.create.call(this);
        var w = Graphics.boxWidth, h = Graphics.boxHeight, listW = Math.floor(w * 0.30), c = counts().chars;
        header(this, 'Characters', 'Met ' + c[0] + ' / ' + c[1]);
        this._listWindow = new Window_NovaCharList(12, HEADER_H + 4, listW, h - HEADER_H - 16);
        this.addWindow(this._listWindow);
        this._infoWindow = new Window_NovaCharInfo(listW + 20, HEADER_H + 4, w - listW - 32, h - HEADER_H - 16);
        this.addWindow(this._infoWindow);
        readScene(this);
        this._picture = new Sprite();
        this._picture.anchor.x = 0.5;
        this._picture.anchor.y = 1;
        var info = this._infoWindow;
        this._pictureBox = { x: info.x + info.width - info.width * 0.19 - 8, y: info.y + info.height - 14,
                             w: info.width * 0.36, h: info.height - 28 };
        this.addChild(this._picture);
    };

    Scene_NovaCharacters.prototype.update = function() {
        Scene_MenuBase.prototype.update.call(this);
        var ch = this._listWindow.entry();
        this._infoWindow.setEntry(ch);
        if (ch !== this._shown) {
            this._shown = ch;
            this.refreshPicture(ch);
        }
    };

    Scene_NovaCharacters.prototype.refreshPicture = function(ch) {
        var sprite = this._picture, box = this._pictureBox;
        sprite.bitmap = null;
        if (!ch || !ch.picture || !isMet(ch)) return;
        var bmp = ImageManager.loadPicture(ch.picture);
        bmp.addLoadListener(function() {
            if (this._shown !== ch) return;
            sprite.bitmap = bmp;
            var s = Math.min(1, box.w / bmp.width, box.h / bmp.height);
            sprite.scale.x = sprite.scale.y = s;
            sprite.x = box.x;
            sprite.y = box.y;
        }.bind(this));
    };

    //=========================================================================
    // Items: tabs (Items, Weapons, Armor, Key Items), list, details
    //=========================================================================
    function Window_NovaItemList() { this.initialize.apply(this, arguments); }
    Window_NovaItemList.prototype = Object.create(Window_Selectable.prototype);
    Window_NovaItemList.prototype.constructor = Window_NovaItemList;
    readable(Window_NovaItemList);

    Window_NovaItemList.prototype.initialize = function(x, y, w, h) {
        this._tab = 0;
        this._items = itemsOf(TABS[0][0]);
        Window_Selectable.prototype.initialize.call(this, x, y, w, h);
        this.refresh();
        this.select(this._items.length ? 0 : -1);
        this.activate();
    };

    Window_NovaItemList.prototype.standardPadding = function() { return 12; };
    Window_NovaItemList.prototype.maxItems = function() { return this._items.length; };
    Window_NovaItemList.prototype.itemHeight = function() { return 44; };
    Window_NovaItemList.prototype.entry = function() { return this._items[this.index()] || null; };
    Window_NovaItemList.prototype.maxPageRows = function() {
        return Math.floor((this.height - this.padding * 2 - TAB_H) / this.itemHeight());
    };
    Window_NovaItemList.prototype.itemRect = function(index) {
        var rect = Window_Selectable.prototype.itemRect.call(this, index);
        rect.y += TAB_H;
        return rect;
    };

    Window_NovaItemList.prototype.switchTab = function(dir) {
        this._tab = (this._tab + dir + TABS.length) % TABS.length;
        this._items = itemsOf(TABS[this._tab][0]);
        SoundManager.playCursor();
        this.setTopRow(0);
        this.select(this._items.length ? 0 : -1);
    };

    Window_NovaItemList.prototype.processCursorMove = function() {
        if (this.isOpenAndActive()) {
            if (Input.isTriggered('left') || Input.isTriggered('pageup')) return this.switchTab(-1);
            if (Input.isTriggered('right') || Input.isTriggered('pagedown')) return this.switchTab(1);
        }
        Window_Selectable.prototype.processCursorMove.call(this);
    };

    Window_NovaItemList.prototype.processTouch = function() {
        if (this.isOpenAndActive() && TouchInput.isTriggered()) {
            var x = this.canvasToLocalX(TouchInput.x) - this.padding;
            var y = this.canvasToLocalY(TouchInput.y) - this.padding;
            if (x >= 30 && x < this.contentsWidth() - 30 && y >= 0 && y < TAB_H) {
                var tab = Math.min(TABS.length - 1, Math.floor((x - 30) / ((this.contentsWidth() - 60) / TABS.length)));
                if (tab !== this._tab) this.switchTab(tab - this._tab);
                return;
            }
        }
        Window_Selectable.prototype.processTouch.call(this);
    };

    Window_NovaItemList.prototype.refresh = function() {
        if (!this.contents) return;
        Window_Selectable.prototype.refresh.call(this);
        this.drawTabs();
        if (this._items.length === 0) {
            UI.bodyFont(this.contents, 19);
            this.contents.fontItalic = true;
            this.changeTextColor(COLOR.dim);
            this.contents.drawText('Nothing here yet.', 0, TAB_H + 24, this.contentsWidth(), 30, 'center');
            this.resetFontSettings();
        }
    };

    Window_NovaItemList.prototype.drawTabs = function() {
        var bmp = this.contents, ctx = UI.ctxOf(bmp), w = this.contentsWidth();
        var cy = TAB_H / 2 - 4, keyW = 30, tabW = (w - keyW * 2) / TABS.length;
        drawKey(bmp, 'Q', 0, cy);
        drawKey(bmp, 'W', w - 22, cy);
        TABS.forEach(function(tab, i) {
            var on = i === this._tab, x = keyW + i * tabW + 2, tw = tabW - 4, by = TAB_H - 14;
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
            UI.titleFont(bmp, 14, on);
            bmp.textColor = on ? COLOR.accentLit : COLOR.dim;
            bmp.outlineWidth = 3;
            bmp.outlineColor = 'rgba(6, 10, 20, 0.7)';
            bmp.drawText(tab[1], x, cy - 14, tw, 28, 'center');
        }, this);
        this.resetFontSettings();
    };

    Window_NovaItemList.prototype.drawItem = function(index) {
        var it = this._items[index], sel = index === this.index(), found = isFound(it);
        var r = drawRow(this.contents, this.itemRect(index), sel, this.active), bmp = this.contents;
        if (found) this.drawIcon(it.iconIndex, r.x + 6, r.y + (r.h - 32) / 2);
        else drawUnknown(bmp, r.x + 22, r.y + r.h / 2, 13);
        UI.bodyFont(bmp, 19);
        this.changeTextColor(found ? (sel ? COLOR.accentLit : COLOR.text) : COLOR.dim);
        bmp.drawText(found ? it.name : UNKNOWN, r.x + 46, r.y, r.w - 100, r.h, 'left');
        if (found) {
            var n = $gameParty.numItems(it);
            UI.bodyFont(bmp, 16);
            this.changeTextColor(COLOR.dim);
            if (n > 0) bmp.drawText('×' + n, r.x, r.y, r.w - 10, r.h, 'right');
        }
        this.resetFontSettings();
    };

    function Window_NovaItemInfo() { this.initialize.apply(this, arguments); }
    Window_NovaItemInfo.prototype = Object.create(Window_NovaCodexInfo.prototype);
    Window_NovaItemInfo.prototype.constructor = Window_NovaItemInfo;

    function typeName(it) {
        if (DataManager.isWeapon(it)) return $dataSystem.weaponTypes[it.wtypeId] || 'Weapon';
        if (DataManager.isArmor(it)) {
            var a = $dataSystem.armorTypes[it.atypeId], slot = $dataSystem.equipTypes[it.etypeId];
            return [a, slot].filter(Boolean).join('  ·  ') || 'Armor';
        }
        return it.itypeId === 2 ? 'Key Item' : (it.consumable ? 'Consumable' : 'Item');
    }

    function effectLines(it) {
        var out = [];
        (it.effects || []).forEach(function(e) {
            var what = e.code === 11 ? TextManager.hpA : e.code === 12 ? TextManager.mpA : e.code === 13 ? TextManager.tpA : '';
            if (what) {
                var parts = [];
                if (e.value1) parts.push(Math.round(e.value1 * 100) + '%');
                if (e.value2) parts.push(e.value2);
                if (parts.length) out.push(['Restores', parts.join(' + ') + ' ' + what]);
            }
            if (e.code === 22 && $dataStates[e.dataId]) out.push(['Cures', $dataStates[e.dataId].name]);
            if (e.code === 42) out.push(['Raises', TextManager.param(e.dataId) + ' +' + e.value1]);
        });
        return out;
    }

    Window_NovaItemInfo.prototype.refresh = function() {
        var bmp = this.contents, it = this._entry;
        bmp.clear();
        this._maxScroll = 0;
        if (!it) return;
        var found = isFound(it), w = this.contentsWidth(), y = 0;
        // the icon, twice the size, in a frame
        var box = 72;
        UI.pathPoly(UI.ctxOf(bmp), UI.panelShape(4, 4, box, box, 8));
        UI.ctxOf(bmp).fillStyle = COLOR.ink;
        UI.ctxOf(bmp).fill();
        UI.dirty(bmp);
        drawFrame(bmp, 4, 4, box, box, found);
        if (found) drawIconScaled(bmp, it.iconIndex, 4 + (box - 64) / 2, 4 + (box - 64) / 2, 64);
        else drawUnknown(bmp, 4 + box / 2, 4 + box / 2, 24);
        var tx = box + 22;
        UI.titleFont(bmp, 28);
        this.changeTextColor(found ? COLOR.text : COLOR.dim);
        bmp.drawText(found ? it.name : UNKNOWN, tx, y, w - tx, 44, 'left');
        UI.bodyFont(bmp, 19);
        bmp.fontItalic = true;
        this.changeTextColor(COLOR.dim);
        bmp.drawText(found ? typeName(it) : 'Not found yet', tx + 2, y + 42, w - tx, 26, 'left');
        bmp.fontItalic = false;
        if (!found) return;
        y = box + 18;

        var rows = [];
        if (DataManager.isWeapon(it) || DataManager.isArmor(it)) {
            it.params.forEach(function(v, i) { if (v) rows.push([TextManager.param(i), (v > 0 ? '+' : '') + v]); });
        } else {
            rows = effectLines(it);
            var when = ['Anytime', 'In battle', 'From the menu', 'Never'][it.occasion];
            if (it.itypeId !== 2 && when) rows.push(['Use', when]);
        }
        rows.push(['Value', it.price ? it.price + ' ' + TextManager.currencyUnit : 'Priceless']);
        rows.push(['Carried', String($gameParty.numItems(it))]);
        divider(bmp, 0, y, w);
        y += 12;
        var colW = Math.floor((w - 12) / 2);
        rows.forEach(function(row, i) {
            var cx = 6 + (i % 2) * colW, cy = y + Math.floor(i / 2) * 30;
            label(bmp, row[0].toUpperCase(), cx, cy + 3, 120);
            UI.bodyFont(bmp, 19);
            this.changeTextColor(COLOR.text);
            bmp.drawText(row[1], cx + 124, cy, colW - 130, 30, 'left');
        }, this);
        y += Math.ceil(rows.length / 2) * 30 + 10;
        divider(bmp, 0, y, w);
        y += 14;
        UI.bodyFont(bmp, 20);
        this.drawBody(wrap(bmp, String(it.description || '').replace(/\n/g, ' '), w - 24), 6, y, w - 24);
        this.resetFontSettings();
    };

    function Scene_NovaItems() { this.initialize.apply(this, arguments); }
    Scene_NovaItems.prototype = Object.create(Scene_MenuBase.prototype);
    Scene_NovaItems.prototype.constructor = Scene_NovaItems;

    Scene_NovaItems.prototype.create = function() {
        Scene_MenuBase.prototype.create.call(this);
        backfill();
        var w = Graphics.boxWidth, h = Graphics.boxHeight, listW = Math.floor(w * 0.40), c = counts().items;
        header(this, 'Items', 'Found ' + c[0] + ' / ' + c[1]);
        this._listWindow = new Window_NovaItemList(12, HEADER_H + 4, listW, h - HEADER_H - 16);
        this.addWindow(this._listWindow);
        this._infoWindow = new Window_NovaItemInfo(listW + 20, HEADER_H + 4, w - listW - 32, h - HEADER_H - 16);
        this.addWindow(this._infoWindow);
        readScene(this);
    };

    Scene_NovaItems.prototype.update = function() {
        Scene_MenuBase.prototype.update.call(this);
        this._infoWindow.setEntry(this._listWindow.entry());
    };

    window.Scene_NovaEncyclopedia = Scene_NovaEncyclopedia;
    window.Scene_NovaCharacters = Scene_NovaCharacters;
    window.Scene_NovaItems = Scene_NovaItems;
})();
