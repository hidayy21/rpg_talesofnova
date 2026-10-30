//=============================================================================
// NovaMinimap.js
//=============================================================================
/*:
 * @plugindesc Minimap in the corner of the map screen: the map's own tiles in
 * miniature, the player, people and the doors/exits.
 * @author Project Nova
 *
 * @param Width
 * @type number
 * @desc Width of the map area in pixels (the frame adds a little).
 * @default 150
 *
 * @param Height
 * @type number
 * @default 104
 *
 * @param Position
 * @type select
 * @option top right
 * @option top left
 * @option bottom right
 * @option bottom left
 * @default top right
 *
 * @param Max Cell
 * @type number
 * @desc Largest size of one map tile on the minimap, in pixels. Small maps stop growing here.
 * @default 6
 *
 * @param Min Cell
 * @type number
 * @desc Smallest size of one map tile. Maps that do not fit at this size scroll with the player.
 * @default 5
 *
 * @param Toggle Key
 * @type number
 * @desc Key code that shows/hides the minimap (77 = M). 0: no key.
 * @default 77
 *
 * @param Hide Switch
 * @type switch
 * @desc While this switch is ON the minimap is hidden (cutscenes). 0: none.
 * @default 0
 *
 * @param Show Map Name
 * @type boolean
 * @default false
 *
 * @param Opacity
 * @type number
 * @min 0
 * @max 255
 * @desc How solid the minimap is (255 = fully solid). It fades further while the player walks under it.
 * @default 150
 *
 * @help
 * Place below NovaMenu and NovaTilesetEx.
 *
 * The minimap is drawn from the map itself: every tile is shrunk to one
 * colour (tiles above blend over the ground), and cells nobody can walk on
 * are shaded darker. On top of it:
 *   gold diamond   the player, pointing where they face
 *   light dots     people (events with a character graphic)
 *   blue squares   exits (events with a Transfer Player command)
 *
 * Small maps show whole and centred; big ones scroll with the player.
 * The minimap fades while a message is open, and turns see-through when
 * the player walks under it.
 *
 * Map note tags
 *   <minimap: off>        no minimap on this map (interiors, cutscene maps)
 *
 * Event note tags (or a comment on the active page)
 *   <minimap: hide>       never shown on the minimap
 *   <minimap: exit>       shown as an exit even without a Transfer command
 *   <minimap: npc>        shown as a person even without a graphic
 *
 * Plugin commands
 *   Minimap show          show it again (after Minimap hide or the key)
 *   Minimap hide          hide it
 *   Minimap refresh       redraw the tiles (after changing tiles by script)
 */

(function() {
    'use strict';

    var params = PluginManager.parameters('NovaMinimap');
    var MAP_W = Number(params['Width'] || 150);
    var MAP_H = Number(params['Height'] || 104);
    var POSITION = String(params['Position'] || 'top right');
    var MAX_CELL = Number(params['Max Cell'] || 6);
    var MIN_CELL = Number(params['Min Cell'] || 5);
    var TOGGLE_KEY = Number(params['Toggle Key'] || 0);
    var HIDE_SWITCH = Number(params['Hide Switch'] || 0);
    var SHOW_NAME = String(params['Show Map Name'] || 'false') === 'true';
    var OPACITY = Number(params['Opacity'] || 150);

    var UI = window.NovaUI;
    var COLOR = UI ? UI.COLOR : { frame: '#6f93c9', frameSoft: 'rgba(185, 212, 245, 0.22)', accent: '#9cc0ec',
                                  accentLit: '#d8e8fb', pending: '#e8cf8f', text: '#eaf0f8',
                                  panelTop: 'rgba(26, 36, 64, 0.94)', panelBottom: 'rgba(12, 18, 34, 0.96)' };
    var PAD = 2, NAME_H = SHOW_NAME ? 24 : 0, MARGIN = 12;
    var EMPTY = [14, 20, 34];                       // under the tiles: night blue

    if (TOGGLE_KEY) Input.keyMapper[TOGGLE_KEY] = 'novaMinimap';

    function ctxOf(bitmap) { return bitmap._context || bitmap.context; }
    function dirty(bitmap) {
        if (bitmap._setDirty) bitmap._setDirty();
        else if (bitmap._baseTexture) bitmap._baseTexture.update();
    }

    //=========================================================================
    // Tile colours: each tile shrunk to its average colour and coverage
    //=========================================================================
    var EX = window.NovaTilesetEx;
    var EX_BASE = EX ? EX.BASE : Infinity, EX_SPAN = EX ? EX.SPAN : 1000;

    // Where a tile's picture is: [sheet name, x, y] in tile units, or null.
    // Autotiles use the top-left tile of their block, the one RPG Maker shows in the palette.
    function tileSource(tileId, names) {
        if (tileId >= EX_BASE) {
            var sheet = EX.sheets[Math.floor((tileId - EX_BASE) / EX_SPAN)], n = (tileId - EX_BASE) % EX_SPAN;
            return sheet ? [sheet.name, Math.floor(n / 128) % 2 * 8 + n % 8, Math.floor(n % 256 / 8) % 16] : null;
        }
        if (Tilemap.isAutotile(tileId)) {
            var kind = Tilemap.getAutotileKind(tileId), tx = kind % 8, ty = Math.floor(kind / 8), set, bx, by;
            if (Tilemap.isTileA1(tileId)) {
                set = 0;
                if (kind === 0) { bx = 0; by = 0; }
                else if (kind === 1) { bx = 0; by = 3; }
                else if (kind === 2) { bx = 6; by = 0; }
                else if (kind === 3) { bx = 6; by = 3; }
                else {
                    bx = Math.floor(tx / 4) * 8 + (kind % 2 === 0 ? 0 : 6);
                    by = ty * 6 + Math.floor(tx / 2) % 2 * 3;
                }
            } else if (Tilemap.isTileA2(tileId)) { set = 1; bx = tx * 2; by = (ty - 2) * 3; }
            else if (Tilemap.isTileA3(tileId)) { set = 2; bx = tx * 2; by = (ty - 6) * 2; }
            else { set = 3; bx = tx * 2; by = Math.floor((ty - 10) * 2.5 + (ty % 2 === 1 ? 0.5 : 0)); }
            return names[set] ? [names[set], bx, by] : null;
        }
        var setNumber = Tilemap.isTileA5(tileId) ? 4 : 5 + Math.floor(tileId / 256);
        return names[setNumber] ? [names[setNumber], Math.floor(tileId / 128) % 2 * 8 + tileId % 8,
                                   Math.floor(tileId % 256 / 8) % 16] : null;
    }

    var colorCache = {};
    var probe = null;
    function tileColor(src, bitmap) {
        var key = src.join(':');
        if (colorCache[key]) return colorCache[key];
        if (!probe) {
            probe = document.createElement('canvas');
            probe.width = probe.height = 6;
        }
        var tw = $gameMap.tileWidth(), th = $gameMap.tileHeight();
        var ctx = probe.getContext('2d');
        ctx.clearRect(0, 0, 6, 6);
        ctx.imageSmoothingEnabled = true;
        ctx.drawImage(bitmap._canvas || bitmap._image, src[1] * tw, src[2] * th, tw, th, 0, 0, 6, 6);
        var px = ctx.getImageData(0, 0, 6, 6).data, r = 0, g = 0, b = 0, a = 0;
        for (var i = 0; i < px.length; i += 4) {
            var w = px[i + 3];
            r += px[i] * w; g += px[i + 1] * w; b += px[i + 2] * w; a += w;
        }
        var c = a > 0 ? [r / a, g / a, b / a, a / (36 * 255)] : [0, 0, 0, 0];
        return (colorCache[key] = c);
    }

    //=========================================================================
    // The map in miniature: one pixel per tile (drawn scaled up later)
    //=========================================================================
    var NovaMinimap = {};

    NovaMinimap.sheetsReady = function(names) {
        return names.every(function(name) { return ImageManager.loadTileset(name).isReady(); });
    };

    NovaMinimap.neededSheets = function() {
        var names = $gameMap.tileset() ? $gameMap.tileset().tilesetNames : [];
        var w = $dataMap.width, h = $dataMap.height, data = $dataMap.data, seen = {}, out = [];
        for (var z = 0; z < 4; z++) {
            for (var i = 0; i < w * h; i++) {
                var id = data[z * w * h + i];
                if (!id) continue;
                var src = tileSource(id, names);
                if (src && !seen[src[0]]) { seen[src[0]] = true; out.push(src[0]); }
            }
        }
        return out;
    };

    // Returns a canvas of width x height pixels, or null while sheets are loading.
    NovaMinimap.buildCanvas = function() {
        var names = $gameMap.tileset() ? $gameMap.tileset().tilesetNames : [];
        var sheets = this.neededSheets();
        if (!this.sheetsReady(sheets)) return null;
        var w = $dataMap.width, h = $dataMap.height, data = $dataMap.data;
        var canvas = document.createElement('canvas');
        canvas.width = w;
        canvas.height = h;
        var ctx = canvas.getContext('2d'), img = ctx.createImageData(w, h), out = img.data, readable = true;
        for (var y = 0; y < h; y++) {
            for (var x = 0; x < w; x++) {
                var c = EMPTY.slice();
                for (var z = 0; z < 4; z++) {
                    var id = data[(z * h + y) * w + x];
                    if (!id) continue;
                    var src = tileSource(id, names);
                    if (!src) continue;
                    var tc = null;
                    if (readable) {
                        try {
                            tc = tileColor(src, ImageManager.loadTileset(src[0]));
                        } catch (e) {
                            readable = false;   // canvas tainted (opened from file:// in a browser)
                        }
                    }
                    if (!tc) continue;
                    var a = Math.min(1, tc[3] * (z < 2 ? 1.3 : 1.0));
                    c[0] += (tc[0] - c[0]) * a; c[1] += (tc[1] - c[1]) * a; c[2] += (tc[2] - c[2]) * a;
                }
                if (!readable) c = [92, 112, 92];
                var open = $gameMap.isPassable(x, y, 2) || $gameMap.isPassable(x, y, 4) ||
                           $gameMap.isPassable(x, y, 6) || $gameMap.isPassable(x, y, 8);
                var k = open ? 1.08 : 0.55;
                var o = (y * w + x) * 4;
                out[o] = Math.min(255, c[0] * k); out[o + 1] = Math.min(255, c[1] * k); out[o + 2] = Math.min(255, c[2] * k);
                out[o + 3] = 255;
            }
        }
        ctx.putImageData(img, 0, 0);
        return canvas;
    };

    // How an event shows: 'exit', 'npc' or null.
    function eventTag(ev) {
        var data = ev.event(), note = data.meta && data.meta.minimap;
        var page = ev.page();
        if (page) {
            page.list.forEach(function(cmd) {
                var m = (cmd.code === 108 || cmd.code === 408) && /<minimap:\s*(\w+)>/i.exec(cmd.parameters[0]);
                if (m) note = m[1];
            });
        }
        return note ? String(note).trim().toLowerCase() : '';
    }

    function eventKind(ev) {
        if (ev._erased || !ev.page()) return null;
        var tag = eventTag(ev);
        if (tag === 'hide') return null;
        if (tag === 'exit') return 'exit';
        if (tag === 'npc') return 'npc';
        if (ev.list().some(function(cmd) { return cmd.code === 201; })) return 'exit';
        var name = ev.characterName();
        if (name && ev.tileId() === 0 && name.charAt(0) !== '!' && !ev.isTransparent()) return 'npc';
        return null;
    }

    //=========================================================================
    // Sprite_NovaMinimap
    //=========================================================================
    function Sprite_NovaMinimap() { this.initialize.apply(this, arguments); }
    Sprite_NovaMinimap.prototype = Object.create(Sprite.prototype);
    Sprite_NovaMinimap.prototype.constructor = Sprite_NovaMinimap;

    Sprite_NovaMinimap.prototype.initialize = function() {
        Sprite.prototype.initialize.call(this);
        this._frameSprite = new Sprite(new Bitmap(MAP_W + PAD * 2, MAP_H + PAD * 2 + NAME_H));
        this._mapSprite = new Sprite(new Bitmap(MAP_W, MAP_H));
        this._mapSprite.x = this._mapSprite.y = PAD;
        this.addChild(this._frameSprite);
        this.addChild(this._mapSprite);
        this._canvas = null;
        this._mapId = -1;
        this._tick = 0;
        this._alpha = 0;
        var w = MAP_W + PAD * 2, h = MAP_H + PAD * 2 + NAME_H;
        this.x = POSITION.indexOf('right') >= 0 ? Graphics.boxWidth - w - MARGIN : MARGIN;
        this.y = POSITION.indexOf('bottom') >= 0 ? Graphics.boxHeight - h - MARGIN : MARGIN;
        this.opacity = 0;
        this.drawFrame();
    };

    Sprite_NovaMinimap.prototype.drawFrame = function() {
        // a plain box: dark fill and a thin light border
        var bmp = this._frameSprite.bitmap, ctx = ctxOf(bmp), w = bmp.width, h = bmp.height;
        ctx.fillStyle = 'rgba(10, 14, 24, 0.85)';
        ctx.fillRect(0, 0, w, h);
        ctx.strokeStyle = 'rgba(234, 240, 248, 0.45)';
        ctx.lineWidth = 1;
        ctx.strokeRect(0.5, 0.5, w - 1, h - 1);
        dirty(bmp);
    };

    Sprite_NovaMinimap.prototype.path = function(ctx, pts) {
        ctx.beginPath();
        ctx.moveTo(pts[0][0], pts[0][1]);
        for (var i = 1; i < pts.length; i++) ctx.lineTo(pts[i][0], pts[i][1]);
        ctx.closePath();
    };

    Sprite_NovaMinimap.prototype.drawName = function() {
        if (!SHOW_NAME) return;
        var bmp = this._frameSprite.bitmap, y = PAD + MAP_H + 1;
        bmp.clear();
        this.drawFrame();
        if (UI) UI.titleFont(bmp, 14);
        else bmp.fontSize = 14;
        bmp.textColor = COLOR.text;
        bmp.outlineColor = 'rgba(6, 10, 20, 0.85)';
        bmp.outlineWidth = 3;
        bmp.drawText($gameMap.displayName() || '', PAD, y, MAP_W, NAME_H, 'center');
        if (UI) UI.bodyFont(bmp);
    };

    Sprite_NovaMinimap.prototype.isEnabled = function() {
        if (!$dataMap || !$gameSystem || $gameSystem._novaMinimapHidden) return false;
        if (HIDE_SWITCH && $gameSwitches.value(HIDE_SWITCH)) return false;
        var tag = $dataMap.meta && $dataMap.meta.minimap;
        return !(tag && String(tag).trim().toLowerCase() === 'off');
    };

    Sprite_NovaMinimap.prototype.update = function() {
        Sprite.prototype.update.call(this);
        if (TOGGLE_KEY && Input.isTriggered('novaMinimap') && !$gameMessage.isBusy()) {
            $gameSystem._novaMinimapHidden = !$gameSystem._novaMinimapHidden;
            SoundManager.playCursor();
        }
        var enabled = this.isEnabled();
        if (enabled && (this._mapId !== $gameMap.mapId() || NovaMinimap._dirty)) {
            this._mapId = $gameMap.mapId();
            NovaMinimap._dirty = false;
            this._canvas = null;
            this.drawName();
        }
        if (enabled && !this._canvas) this._canvas = NovaMinimap.buildCanvas();
        this.updateOpacity(enabled && !!this._canvas);
        if (this.opacity > 0 && this._canvas) this.redraw();
    };

    Sprite_NovaMinimap.prototype.updateOpacity = function(shown) {
        var target = 0;
        if (shown) {
            target = $gameMessage.isBusy() ? 0 : OPACITY;
            var px = $gamePlayer.screenX(), py = $gamePlayer.screenY() - 24;
            var w = this._frameSprite.width, h = this._frameSprite.height;
            if (px > this.x - 24 && px < this.x + w + 24 && py > this.y - 24 && py < this.y + h + 48) target = Math.min(OPACITY, 50);
        }
        this.opacity += Math.max(-20, Math.min(20, target - this.opacity));
    };

    // Cell size and the top-left map tile shown (fractional while scrolling).
    Sprite_NovaMinimap.prototype.view = function() {
        var mw = $dataMap.width, mh = $dataMap.height;
        var cell = Math.max(MIN_CELL, Math.min(MAX_CELL, Math.floor(Math.min(MAP_W / mw, MAP_H / mh))));
        var vw = MAP_W / cell, vh = MAP_H / cell;
        var px = $gamePlayer._realX + 0.5, py = $gamePlayer._realY + 0.5;
        var ox = mw <= vw ? (mw - vw) / 2 : Math.max(0, Math.min(mw - vw, px - vw / 2));
        var oy = mh <= vh ? (mh - vh) / 2 : Math.max(0, Math.min(mh - vh, py - vh / 2));
        return { cell: cell, ox: ox, oy: oy };
    };

    Sprite_NovaMinimap.prototype.redraw = function() {
        var bmp = this._mapSprite.bitmap, ctx = ctxOf(bmp), v = this.view(), cell = v.cell;
        var mw = $dataMap.width, mh = $dataMap.height;
        ctx.fillStyle = 'rgb(' + EMPTY.join(',') + ')';
        ctx.fillRect(0, 0, MAP_W, MAP_H);
        ctx.imageSmoothingEnabled = false;
        ctx.drawImage(this._canvas, 0, 0, mw, mh, -v.ox * cell, -v.oy * cell, mw * cell, mh * cell);
        var toX = function(x) { return (x + 0.5 - v.ox) * cell; };
        var toY = function(y) { return (y + 0.5 - v.oy) * cell; };
        var r = Math.max(2, cell * 0.55);
        $gameMap.events().forEach(function(ev) {
            var kind = eventKind(ev);
            if (!kind) return;
            var x = toX(ev._realX), y = toY(ev._realY);
            if (x < -r || y < -r || x > MAP_W + r || y > MAP_H + r) return;
            if (kind === 'exit') {
                ctx.fillStyle = '#7fb8ff';
                ctx.fillRect(x - r, y - r, r * 2, r * 2);
                ctx.strokeStyle = 'rgba(6, 10, 20, 0.9)';
                ctx.lineWidth = 1;
                ctx.strokeRect(x - r + 0.5, y - r + 0.5, r * 2 - 1, r * 2 - 1);
            } else {
                ctx.fillStyle = 'rgba(6, 10, 20, 0.85)';
                ctx.beginPath();
                ctx.arc(x, y, r * 0.85 + 1, 0, Math.PI * 2);
                ctx.fill();
                ctx.fillStyle = '#f2ead8';
                ctx.beginPath();
                ctx.arc(x, y, r * 0.85, 0, Math.PI * 2);
                ctx.fill();
            }
        });
        this.drawPlayer(ctx, toX($gamePlayer._realX), toY($gamePlayer._realY), Math.max(5, cell * 1.35));
        dirty(bmp);
    };

    // A gold arrowhead pointing where the player faces.
    Sprite_NovaMinimap.prototype.drawPlayer = function(ctx, x, y, s) {
        var angle = { 2: Math.PI / 2, 4: Math.PI, 6: 0, 8: -Math.PI / 2 }[$gamePlayer.direction()] || 0;
        var pts = [[s, 0], [-s * 0.7, -s * 0.75], [-s * 0.3, 0], [-s * 0.7, s * 0.75]].map(function(p) {
            return [x + p[0] * Math.cos(angle) - p[1] * Math.sin(angle), y + p[0] * Math.sin(angle) + p[1] * Math.cos(angle)];
        });
        this.path(ctx, pts);
        ctx.fillStyle = COLOR.pending;
        ctx.fill();
        ctx.strokeStyle = 'rgba(6, 10, 20, 0.95)';
        ctx.lineWidth = 1.5;
        ctx.stroke();
    };

    //=========================================================================
    // Scene_Map: above the map and its lighting, below the windows
    //=========================================================================
    var _createAllWindows = Scene_Map.prototype.createAllWindows;
    Scene_Map.prototype.createAllWindows = function() {
        this._novaMinimap = new Sprite_NovaMinimap();
        this.addChildAt(this._novaMinimap, this.children.indexOf(this._windowLayer));
        _createAllWindows.call(this);
    };

    // Tiles changed by NovaMapPainter (or anything else that refreshes the tilemap).
    if (EX && EX.refreshTilemap) {
        var _refreshTilemap = EX.refreshTilemap;
        EX.refreshTilemap = function() {
            NovaMinimap._dirty = true;
            return _refreshTilemap.apply(this, arguments);
        };
    }

    var _pluginCommand = Game_Interpreter.prototype.pluginCommand;
    Game_Interpreter.prototype.pluginCommand = function(command, args) {
        _pluginCommand.call(this, command, args);
        if (command.toLowerCase() !== 'minimap') return;
        var sub = String(args[0] || '').toLowerCase();
        if (sub === 'show') $gameSystem._novaMinimapHidden = false;
        else if (sub === 'hide') $gameSystem._novaMinimapHidden = true;
        else if (sub === 'refresh') NovaMinimap._dirty = true;
    };

    window.NovaMinimap = NovaMinimap;
})();
