//=============================================================================
// NovaMapPainter.js
//=============================================================================
/*:
 * @plugindesc Playtest only: paint object tiles from every sheet (also other
 * tilesets') straight onto the running map, then save it to the map file.
 * @author Project Nova
 *
 * @param Toggle Key
 * @type number
 * @desc Key code that opens and closes the painter on the map (118 = F7).
 * @default 118
 *
 * @help
 * Only in playtest (started from the editor). Place below NovaTilesetEx.
 *
 * On any map press F7. The game pauses and a palette opens at the bottom with
 * the map's own B-E/A5 sheets first, then every sheet from NovaTilesetEx.
 *
 *   Palette   click a tile, or drag over several tiles (furniture)
 *   Map       left click / drag: paint      right click: erase
 *   Q / W     previous / next sheet          mouse wheel: scroll palette
 *   Arrows    move the camera                H: hide / show the palette
 *   B / E     pen / eraser                   Ctrl+Z: undo
 *   Ctrl+S    save to data/MapXXX.json        F7: close the painter
 *
 * Layer "Auto" works like the editor: an empty cell gets the tile on layer 2,
 * otherwise it goes on layer 3. A5 tiles go on the ground layer.
 * Tiles from the map's own tileset show in the RPG Maker editor; tiles from
 * other sheets (NovaTilesetEx) only show in the game.
 *
 * Saving writes only the tile layers of the map file and keeps a copy of the
 * old file in "<project>_backups/map_painter". If the RPG Maker editor is
 * open, reopen the project there before saving that map from the editor,
 * or the editor writes its older copy back.
 */

(function() {
    'use strict';

    if (!Utils.isNwjs() || !Utils.isOptionValid('test')) return;

    var params = PluginManager.parameters('NovaMapPainter');
    var TOGGLE_KEY = Number(params['Toggle Key'] || 118);
    var T = 48;
    var PANEL_H = 286, BAR_H = 34, PAL_X = 16, INFO_X = 800;
    var COLOR = { panel: 'rgba(7, 16, 31, 0.94)', line: '#2b4a72', accent: '#62d6ff', dim: '#93acc8',
                  on: 'rgba(22, 119, 184, 0.95)', warn: '#ffb35c', bad: '#ff7088' };

    var NovaMapPainter = window.NovaMapPainter = {};

    // Project data file path (also right in test harnesses that load the game through <base href>).
    NovaMapPainter.dataFile = function(name) {
        var p = decodeURIComponent(new URL('data/' + name, document.baseURI).pathname);
        return /^\/[A-Za-z]:/.test(p) ? p.slice(1) : p;
    };

    function ctxOf(bitmap) { return bitmap._context || bitmap.context; }
    function dirty(bitmap) { if (bitmap._setDirty) bitmap._setDirty(); else if (bitmap._baseTexture) bitmap._baseTexture.update(); }

    // RPG Maker numbering inside a B-E / A5 sheet
    function num(half, col, row) { return half * 128 + row * 8 + col; }
    function cellOf(n) { return { half: Math.floor(n / 128), col: n % 8, row: Math.floor((n % 128) / 8) }; }

    //=========================================================================
    // Keys (raw, the game's own input is paused while painting)
    //=========================================================================
    var keys = [];
    document.addEventListener('keydown', function(e) {
        if (!(SceneManager._scene instanceof Scene_Map)) return;
        if (e.keyCode === TOGGLE_KEY) { keys.push('toggle'); e.preventDefault(); return; }
        var p = SceneManager._scene._novaPainter;
        if (!p) return;
        if (e.ctrlKey && e.keyCode === 90) keys.push('undo');
        else if (e.ctrlKey && e.keyCode === 83) keys.push('save');
        else if (e.keyCode === 72) keys.push('hide');
        else if (e.keyCode === 66) keys.push('pen');
        else if (e.keyCode === 69) keys.push('eraser');
        else return;
        e.preventDefault();
    });

    var mouse = { x: -1, y: -1 };
    document.addEventListener('mousemove', function(e) {
        mouse.x = Graphics.pageToCanvasX(e.pageX);
        mouse.y = Graphics.pageToCanvasY(e.pageY);
    });

    //=========================================================================
    // Scene_Map: pause the game while the painter is open
    //=========================================================================
    var _Scene_Map_update = Scene_Map.prototype.update;
    Scene_Map.prototype.update = function() {
        while (keys.length) {
            var k = keys.shift();
            if (k === 'toggle') this.novaTogglePainter();
            else if (this._novaPainter) this._novaPainter.command(k);
        }
        if (this._novaPainter) {
            this._novaPainter.update();
            Scene_Base.prototype.update.call(this);   // sprites and tilemap keep drawing
            return;
        }
        _Scene_Map_update.call(this);
    };

    Scene_Map.prototype.novaTogglePainter = function() {
        if (this._novaPainter) {
            if (this._novaPainter.tryClose()) {
                this.removeChild(this._novaPainter.root);
                this._novaPainter = null;
                $gamePlayer.center($gamePlayer.x, $gamePlayer.y);
            }
        } else if (this.isActive() && !$gameMessage.isBusy() && $dataMap) {
            this._novaPainter = new Painter(this);
            this.addChild(this._novaPainter.root);
        }
    };

    //=========================================================================
    // Painter
    //=========================================================================
    function Painter(scene) {
        this.scene = scene;
        this.sheets = this.makeSheets();
        this.sheetIndex = 0;
        this.scroll = 0;
        this.sel = { n: 1, w: 1, h: 1 };
        this.tool = 'pen';
        this.layer = 'auto';
        this.visible = true;
        this.undo = [];
        this.stroke = null;
        this.palDrag = null;
        this.unsaved = false;
        this.closeWarned = false;
        this.toastText = '';
        this.toastTime = 0;
        this.hoverKey = '';
        this.createSprites();
        this.openSheet(0);
        this.toast('Painter aktif - game dijeda. F7 untuk keluar.');
    }

    // The map's own sheets first (normal ids, visible in the editor), then the NovaTilesetEx sheets.
    Painter.prototype.makeSheets = function() {
        var ts = $gameMap.tileset(), list = [], own = {};
        [5, 6, 7, 8, 4].forEach(function(s) {
            var name = ts.tilesetNames[s];
            if (!name) return;
            own[name] = true;
            list.push({ name: name, own: true, a5: s === 4,
                        id: s === 4 ? function(n) { return Tilemap.TILE_ID_A5 + n; } : function(n) { return (s - 5) * 256 + n; } });
        });
        var ex = window.NovaTilesetEx;
        if (ex) Object.keys(ex.sheets).map(Number).sort(function(a, b) { return a - b; }).forEach(function(slot) {
            var name = ex.sheets[slot].name;
            if (own[name]) return;
            list.push({ name: name, own: false, a5: /_A5$/.test(name),
                        id: function(n) { return ex.BASE + slot * ex.SPAN + n; } });
        });
        list.forEach(function(s) { s.bitmap = ImageManager.loadTileset(s.name); });
        return list;
    };

    Painter.prototype.panelY = function() { return Graphics.boxHeight - PANEL_H; };
    Painter.prototype.viewH = function() { return PANEL_H - BAR_H - 10; };
    Painter.prototype.sheet = function() { return this.sheets[this.sheetIndex]; };

    Painter.prototype.createSprites = function() {
        var w = Graphics.boxWidth;
        this.root = new Sprite();
        this.cursor = new Sprite(new Bitmap(T * 8, T * 8));
        this.root.addChild(this.cursor);
        this.panel = new Sprite();
        this.root.addChild(this.panel);
        var bg = new Bitmap(w, PANEL_H), ctx = ctxOf(bg);
        ctx.fillStyle = COLOR.panel; ctx.fillRect(0, 0, w, PANEL_H);
        ctx.fillStyle = COLOR.accent; ctx.fillRect(0, 0, w, 2);
        ctx.fillStyle = COLOR.line; ctx.fillRect(INFO_X - 12, BAR_H + 6, 1, PANEL_H - BAR_H - 12);
        dirty(bg);
        this.panel.addChild(new Sprite(bg));
        this.bar = new Sprite(new Bitmap(w, BAR_H));
        this.panel.addChild(this.bar);
        this.palette = new Sprite();
        this.palette.x = PAL_X; this.palette.y = BAR_H + 6;
        this.panel.addChild(this.palette);
        this.palGrid = new Sprite(new Bitmap(T * 16, this.viewH()));
        this.palGrid.x = PAL_X; this.palGrid.y = BAR_H + 6;
        this.panel.addChild(this.palGrid);
        this.info = new Sprite(new Bitmap(w - INFO_X - 12, PANEL_H - BAR_H - 8));
        this.info.x = INFO_X; this.info.y = BAR_H + 6;
        this.panel.addChild(this.info);
        this.toastSprite = new Sprite(new Bitmap(w, 40));
        this.root.addChild(this.toastSprite);
    };

    Painter.prototype.openSheet = function(i) {
        this.sheetIndex = (i + this.sheets.length) % this.sheets.length;
        this.scroll = 0;
        this.sel = { n: this.sheet().a5 ? 0 : 1, w: 1, h: 1 };
        this.palette.bitmap = this.sheet().bitmap;
        this.gridReady = false;
        this.infoDirty = true;
        this.drawBar();
        this.layout();
    };

    //------------------------------------------------------------------ drawing
    Painter.prototype.drawBar = function() {
        var b = this.bar.bitmap, ctx = ctxOf(b), s = this.sheet(), x = 12, self = this;
        b.clear();
        this.buttons = [];
        b.fontSize = 16; b.outlineWidth = 3; b.outlineColor = 'rgba(0,0,0,0.6)';
        function button(label, w, action, on) {
            ctx.fillStyle = on ? COLOR.on : 'rgba(19, 40, 74, 0.95)';
            ctx.fillRect(x, 5, w, BAR_H - 10);
            ctx.strokeStyle = on ? COLOR.accent : COLOR.line;
            ctx.strokeRect(x + 0.5, 5.5, w - 1, BAR_H - 11);
            dirty(b);
            b.textColor = '#ffffff';
            b.drawText(label, x, 5, w, BAR_H - 10, 'center');
            self.buttons.push({ x: x, w: w, action: action });
            x += w + 6;
        }
        function label(text, w, color) {
            b.textColor = color || COLOR.dim;
            b.drawText(text, x, 5, w, BAR_H - 10, 'left');
            x += w;
        }
        button('◀', 30, 'prev');
        label((this.sheetIndex + 1) + '/' + this.sheets.length + '  ' + s.name + (s.own ? '' : '  +'), 250, s.own ? '#ffffff' : COLOR.accent);
        button('▶', 30, 'next');
        x += 10; label('Layer', 50);
        button('Auto', 54, 'layer:auto', this.layer === 'auto');
        button('2', 30, 'layer:2', this.layer === '2');
        button('3', 30, 'layer:3', this.layer === '3');
        x += 10;
        button('Pena (B)', 86, 'pen', this.tool === 'pen');
        button('Hapus (E)', 92, 'eraser', this.tool === 'eraser');
        x += 10;
        button('Undo', 62, 'undo');
        button(this.unsaved ? 'Simpan*' : 'Simpan', 82, 'save', this.unsaved);
        button('Keluar', 72, 'toggle');
    };

    Painter.prototype.drawGrid = function() {
        var b = this.palGrid.bitmap, ctx = ctxOf(b), bmp = this.sheet().bitmap;
        b.clear();
        if (!bmp.isReady()) { b.drawText('Memuat...', 0, 0, 300, 40, 'left'); return; }
        var w = bmp.width, h = this.viewH(), off = this.scroll % T;
        ctx.strokeStyle = 'rgba(255,255,255,0.12)';
        for (var x = 0; x <= w; x += T) { ctx.beginPath(); ctx.moveTo(x + 0.5, 0); ctx.lineTo(x + 0.5, h); ctx.stroke(); }
        for (var y = -off; y <= h; y += T) { ctx.beginPath(); ctx.moveTo(0, y + 0.5); ctx.lineTo(w, y + 0.5); ctx.stroke(); }
        if (w > 8 * T) { ctx.strokeStyle = 'rgba(98,214,255,0.6)'; ctx.beginPath(); ctx.moveTo(8 * T + 0.5, 0); ctx.lineTo(8 * T + 0.5, h); ctx.stroke(); }
        var r = this.palDrag ? this.dragSel() : this.sel, c = cellOf(r.n);
        var sx = (c.half * 8 + c.col) * T, sy = c.row * T - this.scroll;
        ctx.fillStyle = 'rgba(98,214,255,0.25)';
        ctx.fillRect(sx, sy, r.w * T, r.h * T);
        ctx.lineWidth = 3; ctx.strokeStyle = COLOR.accent;
        ctx.strokeRect(sx + 1.5, sy + 1.5, r.w * T - 3, r.h * T - 3);
        ctx.lineWidth = 1;
        dirty(b);
    };

    Painter.prototype.layout = function() {
        var py = this.panelY(), bmp = this.sheet().bitmap;
        this.panel.y = this.visible ? py : Graphics.boxHeight;
        this.panel.visible = this.visible;
        if (bmp.isReady()) {
            var maxScroll = Math.max(0, bmp.height - this.viewH());
            this.scroll = Math.max(0, Math.min(this.scroll, maxScroll));
            this.palette.setFrame(0, this.scroll, bmp.width, Math.min(this.viewH(), bmp.height));
        }
        this.drawGrid();
        this.drawGhost();
    };

    // The selected tiles, half transparent, under the mouse.
    Painter.prototype.drawGhost = function() {
        var b = this.cursor.bitmap, ctx = ctxOf(b), r = this.sel, bmp = this.sheet().bitmap;
        b.clear();
        var w = this.tool === 'eraser' ? 1 : r.w, h = this.tool === 'eraser' ? 1 : r.h;
        if (this.tool === 'pen' && bmp.isReady()) {
            b.paintOpacity = 170;
            var c = cellOf(r.n);
            for (var j = 0; j < h; j++) for (var i = 0; i < w; i++) {
                var n = num(c.half, c.col + i, c.row + j), cc = cellOf(n);
                b.blt(bmp, (cc.half * 8 + cc.col) * T, cc.row * T, T, T, i * T, j * T);
            }
            b.paintOpacity = 255;
        }
        ctx.lineWidth = 2;
        ctx.strokeStyle = this.tool === 'eraser' ? COLOR.bad : COLOR.accent;
        ctx.strokeRect(1, 1, w * T - 2, h * T - 2);
        dirty(b);
    };

    Painter.prototype.drawInfo = function(mx, my) {
        var b = this.info.bitmap, self = this;
        b.clear();
        b.fontSize = 16; b.outlineWidth = 3;
        var line = 0;
        function text(t, color) { b.textColor = color || '#ffffff'; b.drawText(t, 0, line * 22, b.width, 22, 'left'); line++; }
        var s = this.sheet(), first = s.id(this.sel.n), flags = $gameMap.tilesetFlags();
        text('Pilihan: ' + s.name + ' #' + this.sel.n + (this.sel.w * this.sel.h > 1 ? '  (' + this.sel.w + 'x' + this.sel.h + ')' : '') +
             '   ' + this.flagMark(flags[first]), COLOR.accent);
        text(s.own ? 'Dari tileset map ini (terlihat di editor)' : 'Sheet tambahan (hanya terlihat di game)', COLOR.dim);
        line++;
        if (mx !== null) {
            text('Map ' + $gameMap.mapId() + '  sel (' + mx + ', ' + my + ')');
            ['Lantai 0', 'Lantai 1', 'Layer 2', 'Layer 3'].forEach(function(name, z) {
                text('  ' + name + ': ' + self.describe($gameMap.tileId(mx, my, z)), COLOR.dim);
            });
            text('  Bisa dilewati: ' + ($gameMap.isPassable(mx, my, 2) ? 'ya' : 'tidak'), COLOR.dim);
        } else {
            text('Arahkan mouse ke map untuk info sel.', COLOR.dim);
        }
        line++;
        text('Klik kiri: lukis   Klik kanan: hapus   Ctrl+Z: undo   Ctrl+S: simpan', COLOR.dim);
    };

    Painter.prototype.flagMark = function(f) {
        f = f || 0;
        return (f & 0x10) ? '☆ di atas karakter' : ((f & 0x0f) === 0x0f ? '✕ menghalangi' : '○ bisa dilewati');
    };

    Painter.prototype.describe = function(id) {
        if (!id) return '-';
        var ex = window.NovaTilesetEx;
        if (ex && id >= ex.BASE) {
            var sheet = ex.sheets[Math.floor((id - ex.BASE) / ex.SPAN)];
            return (sheet ? sheet.name : '?') + ' #' + ((id - ex.BASE) % ex.SPAN) + ' +';
        }
        var names = $gameMap.tileset().tilesetNames;
        if (id < 1024) return names[5 + Math.floor(id / 256)] + ' #' + (id % 256);
        if (id >= Tilemap.TILE_ID_A5 && id < Tilemap.TILE_ID_A1) return names[4] + ' #' + (id - Tilemap.TILE_ID_A5);
        return 'autotile ' + id;
    };

    Painter.prototype.toast = function(text, color) {
        var b = this.toastSprite.bitmap;
        b.clear();
        b.fontSize = 20; b.outlineWidth = 4; b.outlineColor = 'rgba(0,0,0,0.85)';
        b.textColor = color || '#ffffff';
        b.drawText(text, 0, 6, b.width, 30, 'center');
        this.toastSprite.y = (this.visible ? this.panelY() : Graphics.boxHeight) - 44;   // clear of the map name at the top
        this.toastSprite.opacity = 255;
        this.toastTime = 240;
    };

    //------------------------------------------------------------------ input
    Painter.prototype.command = function(k) {
        if (k === 'undo') this.undoStroke();
        else if (k === 'save') this.save();
        else if (k === 'hide') { this.visible = !this.visible; this.layout(); }
        else if (k === 'pen' || k === 'eraser') { this.tool = k; this.drawBar(); this.drawGhost(); }
        else if (k === 'prev') this.openSheet(this.sheetIndex - 1);
        else if (k === 'next') this.openSheet(this.sheetIndex + 1);
        else if (k === 'toggle') keys.push('toggle');
        else if (k.indexOf('layer:') === 0) { this.layer = k.slice(6); this.drawBar(); }
    };

    Painter.prototype.mapCell = function(x, y) {
        return { x: Math.floor($gameMap.canvasToMapX(x)), y: Math.floor($gameMap.canvasToMapY(y)) };
    };

    Painter.prototype.inPanel = function(y) { return this.visible && y >= this.panelY(); };

    Painter.prototype.paletteCell = function(x, y) {
        var bmp = this.sheet().bitmap;
        var cx = Math.floor((x - PAL_X) / T), cy = Math.floor((y - this.panelY() - BAR_H - 6 + this.scroll) / T);
        if (!bmp.isReady() || cx < 0 || cx >= bmp.width / T || cy < 0 || cy >= bmp.height / T) return null;
        return { x: cx, y: cy };
    };

    Painter.prototype.dragSel = function() {
        var a = this.palDrag.a, b = this.palDrag.b, half = Math.floor(a.x / 8);
        var bx = Math.max(half * 8, Math.min(b.x, half * 8 + 7));
        var x0 = Math.min(a.x, bx), x1 = Math.max(a.x, bx), y0 = Math.min(a.y, b.y), y1 = Math.max(a.y, b.y);
        return { n: num(half, x0 - half * 8, y0), w: x1 - x0 + 1, h: y1 - y0 + 1 };
    };

    Painter.prototype.update = function() {
        var self = this;
        if (this.toastTime > 0 && --this.toastTime < 60) this.toastSprite.opacity = this.toastTime * 4;
        if (!this.gridReady && this.sheet().bitmap.isReady()) { this.gridReady = true; this.layout(); }
        if (Input.isTriggered('pageup')) this.openSheet(this.sheetIndex - 1);
        if (Input.isTriggered('pagedown')) this.openSheet(this.sheetIndex + 1);
        ['up', 'down', 'left', 'right'].forEach(function(d) {
            if (Input.isRepeated(d)) {
                if (d === 'up') $gameMap.scrollUp(1); else if (d === 'down') $gameMap.scrollDown(1);
                else if (d === 'left') $gameMap.scrollLeft(1); else $gameMap.scrollRight(1);
                self.hoverKey = '';
            }
        });

        var wheel = TouchInput.wheelY;
        if (wheel) {
            if (this.inPanel(mouse.y)) { this.scroll += wheel > 0 ? T : -T; this.layout(); }
            else if (wheel > 0) $gameMap.scrollDown(1); else $gameMap.scrollUp(1);
        }

        if (TouchInput.isTriggered()) this.onPress(TouchInput.x, TouchInput.y);
        else if (TouchInput.isPressed()) this.onDrag(TouchInput.x, TouchInput.y);
        if (TouchInput.isReleased()) this.onRelease();
        if (TouchInput.isCancelled() && !this.inPanel(TouchInput.y)) {
            var c = this.mapCell(TouchInput.x, TouchInput.y);
            this.stroke = [];
            this.eraseAt(c.x, c.y);
            this.endStroke();
        }

        // cursor and info
        var over = mouse.x >= 0 && !this.inPanel(mouse.y);
        var cell = over ? this.mapCell(mouse.x, mouse.y) : null;
        this.cursor.visible = over;
        if (cell) {
            this.cursor.x = Math.round($gameMap.adjustX(cell.x) * T);
            this.cursor.y = Math.round($gameMap.adjustY(cell.y) * T);
        }
        var key = cell ? cell.x + ',' + cell.y + ':' + $gameMap.displayX() + ',' + $gameMap.displayY() : '-';
        if (key !== this.hoverKey || this.infoDirty) {
            this.hoverKey = key;
            this.infoDirty = false;
            this.drawInfo(cell && $gameMap.isValid(cell.x, cell.y) ? cell.x : null, cell ? cell.y : null);
        }
    };

    Painter.prototype.onPress = function(x, y) {
        if (this.inPanel(y)) {
            if (y < this.panelY() + BAR_H) {
                var px = x;
                var btn = this.buttons.filter(function(b) { return px >= b.x && px < b.x + b.w; })[0];
                if (btn) { SoundManager.playCursor(); this.command(btn.action); }
                return;
            }
            var c = this.paletteCell(x, y);
            if (c) { this.palDrag = { a: c, b: c }; this.drawGrid(); }
            return;
        }
        var m = this.mapCell(x, y);
        this.stroke = [];
        this.strokeStart = m;
        this.lastCell = m;
        this.applyAt(m.x, m.y);
    };

    Painter.prototype.onDrag = function(x, y) {
        if (this.palDrag) {
            var c = this.paletteCell(x, Math.max(y, this.panelY() + BAR_H + 6));
            if (c) { this.palDrag.b = c; this.drawGrid(); }
            return;
        }
        if (!this.stroke || this.inPanel(y)) return;
        var m = this.mapCell(x, y);
        if (m.x === this.lastCell.x && m.y === this.lastCell.y) return;
        this.lastCell = m;
        var w = this.tool === 'eraser' ? 1 : this.sel.w, h = this.tool === 'eraser' ? 1 : this.sel.h;
        var dx = m.x - this.strokeStart.x, dy = m.y - this.strokeStart.y;
        // big stamps repeat on their own grid while dragging, like the editor's pen
        if (dx % w === 0 && dy % h === 0) this.applyAt(m.x, m.y);
    };

    Painter.prototype.onRelease = function() {
        if (this.palDrag) {
            this.sel = this.dragSel();
            this.palDrag = null;
            this.tool = 'pen';
            this.drawBar(); this.drawGrid(); this.drawGhost();
            this.infoDirty = true;
        }
        if (this.stroke) this.endStroke();
    };

    //------------------------------------------------------------------ editing
    Painter.prototype.index = function(x, y, z) { return (z * $dataMap.height + y) * $dataMap.width + x; };

    Painter.prototype.setTile = function(x, y, z, id) {
        if (!$gameMap.isValid(x, y)) return;
        var i = this.index(x, y, z), old = $dataMap.data[i];
        if (old === id) return;
        $dataMap.data[i] = id;
        this.stroke.push([i, old, id]);
    };

    Painter.prototype.applyAt = function(x, y) {
        if (this.tool === 'eraser') { this.eraseAt(x, y); return; }
        var s = this.sheet(), c = cellOf(this.sel.n);
        for (var j = 0; j < this.sel.h; j++) for (var i = 0; i < this.sel.w; i++) {
            var id = s.id(num(c.half, c.col + i, c.row + j));
            if (s.a5) { this.setTile(x + i, y + j, 0, id); continue; }
            var z = this.layer === '3' ? 3 : 2;
            if (this.layer === 'auto') {
                var under = $dataMap.data[this.index(x + i, y + j, 2)];
                z = (!under || under === id) ? 2 : 3;
            }
            this.setTile(x + i, y + j, z, id);
        }
        this.refreshMap();
    };

    Painter.prototype.eraseAt = function(x, y) {
        if (!$gameMap.isValid(x, y)) return;
        var top = $dataMap.data[this.index(x, y, 3)] ? 3 : 2;
        this.setTile(x, y, top, 0);
        this.refreshMap();
    };

    Painter.prototype.endStroke = function() {
        if (this.stroke && this.stroke.length) {
            this.undo.push(this.stroke);
            if (this.undo.length > 200) this.undo.shift();
            this.markUnsaved(true);
        }
        this.stroke = null;
    };

    Painter.prototype.undoStroke = function() {
        var stroke = this.undo.pop();
        if (!stroke) { this.toast('Tidak ada yang bisa di-undo.', COLOR.dim); return; }
        for (var k = stroke.length - 1; k >= 0; k--) $dataMap.data[stroke[k][0]] = stroke[k][1];
        this.refreshMap();
        this.markUnsaved(true);
        this.toast('Undo');
    };

    Painter.prototype.markUnsaved = function(v) {
        if (this.unsaved !== v) { this.unsaved = v; this.drawBar(); }
        this.closeWarned = false;
        this.infoDirty = true;
    };

    Painter.prototype.refreshMap = function() {
        if (window.NovaTilesetEx && NovaTilesetEx.refreshTilemap) NovaTilesetEx.refreshTilemap();
        else this.scene._spriteset._tilemap.refresh();
    };

    //------------------------------------------------------------------ save
    function stamp() {
        var d = new Date(), p = function(n) { return (n < 10 ? '0' : '') + n; };
        return d.getFullYear() + p(d.getMonth() + 1) + p(d.getDate()) + '_' + p(d.getHours()) + p(d.getMinutes()) + p(d.getSeconds());
    }

    function mkdirs(fs, path, dir) {
        if (fs.existsSync(dir)) return;
        mkdirs(fs, path, path.dirname(dir));
        fs.mkdirSync(dir);
    }

    // Same layout the RPG Maker editor writes: settings on one line, then data, then one event per line.
    function editorJson(map) {
        var head = {};
        Object.keys(map).forEach(function(k) { if (k !== 'data' && k !== 'events') head[k] = map[k]; });
        return '{\n' + JSON.stringify(head).slice(1, -1) + ',\n"data":' + JSON.stringify(map.data) +
               ',\n"events":[\n' + map.events.map(function(e) { return JSON.stringify(e); }).join(',\n') + '\n]\n}';
    }

    function editorOpen() {
        try {
            return require('child_process').execSync('tasklist /FI "IMAGENAME eq RPGMV.exe" /NH', { encoding: 'utf8' }).indexOf('RPGMV.exe') >= 0;
        } catch (e) { return false; }
    }

    Painter.prototype.save = function() {
        var fs = require('fs'), path = require('path');
        var name = 'Map' + $gameMap.mapId().padZero(3) + '.json';
        var file = NovaMapPainter.dataFile(name);
        try {
            var original = fs.readFileSync(file, 'utf8');
            var map = JSON.parse(original);
            if (map.width !== $dataMap.width || map.height !== $dataMap.height) {
                this.toast('Ukuran map di file berbeda (diubah di editor?). Tidak disimpan.', COLOR.bad);
                return;
            }
            var proj = path.dirname(path.dirname(file));
            var backups = path.join(path.dirname(proj), path.basename(proj) + '_backups', 'map_painter');
            mkdirs(fs, path, backups);
            fs.writeFileSync(path.join(backups, name.replace('.json', '_' + stamp() + '.json')), original);
            map.data = $dataMap.data.slice();
            fs.writeFileSync(file, editorJson(map));
        } catch (e) {
            this.toast('Gagal menyimpan: ' + e.message, COLOR.bad);
            return;
        }
        this.markUnsaved(false);
        if (editorOpen()) this.toast('Tersimpan. Editor terbuka: buka ulang project sebelum menyimpan map ini dari editor.', COLOR.warn);
        else this.toast('Tersimpan ke data/' + name);
    };

    Painter.prototype.tryClose = function() {
        if (this.unsaved && !this.closeWarned) {
            this.closeWarned = true;
            this.toast('Ada perubahan yang belum disimpan (Ctrl+S). Tekan F7 lagi untuk keluar tanpa menyimpan.', COLOR.warn);
            return false;
        }
        return true;
    };
})();
