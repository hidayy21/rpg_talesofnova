//=============================================================================
// NovaTilesetEx.js
//=============================================================================
/*:
 * @plugindesc Any map can use object tiles (B-E and A5 sheets) from every
 * tileset, not only from its own. For maps built by the Nova map scripts.
 * @author Project Nova
 *
 * @param Extra Sheets
 * @type note
 * @desc One sheet per line:  slot: SheetName   or   slot: SheetName @ tilesetId
 * Tile id = 20000 + slot * 1000 + tile number on the sheet. Never renumber a slot.
 * @default "0: Outside_B\n1: Outside_C\n2: Inside_B\n3: Inside_C\n4: Dungeon_B\n5: Dungeon_C\n6: World_B\n7: World_C\n8: SF_Outside_B\n9: SF_Outside_C\n10: SF_Inside_B\n11: SF_Inside_C\n12: Nova_Market_D\n13: Outside_A5\n14: Inside_A5\n15: Dungeon_A5\n16: SF_Outside_A5"
 *
 * @help
 * A map still has one tileset (its floors, walls, water and its own B-E
 * sheets). On top of that, every sheet listed in "Extra Sheets" can be used
 * on any map, whatever its tileset:
 *
 *   tile id = 20000 + slot * 1000 + n
 *
 *   slot  the number in front of the sheet in "Extra Sheets"
 *   n     the tile's number on that sheet, counted like RPG Maker does:
 *         left half of the sheet first (8 columns, top to bottom), then the
 *         right half. B-E sheets have 256 tiles, A5 sheets 128.
 *
 *   e.g. 22049 = slot 2 (Inside_B), tile 49 (a cabinet top).
 *
 * Passability, ladder, bush, counter, damage floor and terrain tags come from
 * the tileset that has that sheet in the database (the first one found), or
 * from the tileset written after "@", e.g.  "2: Inside_B @ 3".
 * Add your own sheets (img/tilesets/<name>.png) with a new slot number; do
 * not renumber or reuse slots, or maps already built will show other tiles.
 *
 * The Nova map scripts place these ids (nova_maplib: L.ext('Inside_B', 49)).
 * The RPG Maker editor cannot show or paint them: such tiles look empty in
 * the editor but appear in the game. Editing events or settings of such a
 * map in the editor is fine; repainting those cells there replaces them.
 *
 * Only the extra sheets a map really uses are loaded. Up to 7 extra sheets
 * on one map draw in exactly the right order; more still works, but tiles
 * of the 8th sheet onward may draw above other tiles of the same layer.
 *
 * Event graphics can use these tiles too (image tileId = an extra id).
 */

(function() {
    'use strict';

    var BASE = 20000, SPAN = 1000;
    var params = PluginManager.parameters('NovaTilesetEx');

    // slot -> { name, from }
    var SHEETS = {};
    var list = String(params['Extra Sheets'] || '');
    try { list = JSON.parse(list); } catch (e) { /* plain text */ }
    String(list).split(/\r?\n/).forEach(function(line) {
        var m = line.match(/^\s*(\d+)\s*:\s*([^@]+?)\s*(?:@\s*(\d+))?\s*$/);
        if (m) SHEETS[Number(m[1])] = { name: m[2], from: m[3] ? Number(m[3]) : 0 };
    });

    function isExtra(tileId) { return tileId >= BASE; }
    function slotOf(tileId) { return Math.floor((tileId - BASE) / SPAN); }
    function localOf(tileId) { return (tileId - BASE) % SPAN; }

    // Same layout RPG Maker uses inside a B-E (or A5) sheet.
    function sheetX(n) { return Math.floor(n / 128) % 2 * 8 + n % 8; }
    function sheetY(n) { return Math.floor(n % 256 / 8) % 16; }

    window.NovaTilesetEx = {
        BASE: BASE, SPAN: SPAN, sheets: SHEETS,
        tileId: function(sheetName, n) {
            for (var slot in SHEETS) if (SHEETS[slot].name === sheetName) return BASE + Number(slot) * SPAN + n;
            return 0;
        }
    };

    //=========================================================================
    // Tile id ranges
    //=========================================================================
    var _isVisibleTile = Tilemap.isVisibleTile;
    Tilemap.isVisibleTile = function(tileId) {
        return isExtra(tileId) ? !!SHEETS[slotOf(tileId)] : _isVisibleTile.call(this, tileId);
    };

    var _isAutotile = Tilemap.isAutotile;
    Tilemap.isAutotile = function(tileId) {
        return !isExtra(tileId) && _isAutotile.call(this, tileId);
    };

    var _Game_Map_autotileType = Game_Map.prototype.autotileType;
    Game_Map.prototype.autotileType = function(x, y, z) {
        return isExtra(this.tileId(x, y, z)) ? -1 : _Game_Map_autotileType.call(this, x, y, z);
    };

    //=========================================================================
    // Flags (passability etc.) for the extra ids
    //=========================================================================
    // Where a sheet's flags live: [tileset flags, first id, tile count].
    function flagSource(sheet) {
        var sets = sheet.from ? [$dataTilesets[sheet.from]] : $dataTilesets;
        for (var i = 0; i < sets.length; i++) {
            var ts = sets[i];
            if (!ts) continue;
            for (var s = 4; s <= 8; s++) {
                if (ts.tilesetNames[s] === sheet.name) {
                    return s === 4 ? [ts.flags, Tilemap.TILE_ID_A5, 128] : [ts.flags, (s - 5) * 256, 256];
                }
            }
        }
        return null;
    }

    function buildFlags(baseFlags) {
        var flags = baseFlags.slice();
        Object.keys(SHEETS).forEach(function(slot) {
            var src = flagSource(SHEETS[slot]);
            if (!src) return;   // unknown: passable, drawn normally
            var first = BASE + Number(slot) * SPAN;
            for (var n = 0; n < src[2]; n++) flags[first + n] = src[0][src[1] + n] || 0;
        });
        return flags;
    }

    var _Game_Map_tilesetFlags = Game_Map.prototype.tilesetFlags;
    Game_Map.prototype.tilesetFlags = function() {
        var tileset = this.tileset();
        if (!tileset) return _Game_Map_tilesetFlags.call(this);
        if (!tileset._novaFlags) tileset._novaFlags = buildFlags(tileset.flags);
        return tileset._novaFlags;
    };

    //=========================================================================
    // Loading: only the extra sheets the current map uses
    //=========================================================================
    var usedCache = { map: null, slots: [] };

    function usedSlots() {
        if (usedCache.map === $dataMap) return usedCache.slots;
        var seen = {};
        var mark = function(id) { if (isExtra(id) && SHEETS[slotOf(id)]) seen[slotOf(id)] = true; };
        if ($dataMap) {
            $dataMap.data.forEach(mark);
            $dataMap.events.forEach(function(ev) {
                if (ev) ev.pages.forEach(function(page) { mark(page.image.tileId); });
            });
        }
        usedCache = { map: $dataMap, slots: Object.keys(seen).map(Number).sort(function(a, b) { return a - b; }) };
        return usedCache.slots;
    }

    // After the map's tiles were changed at run time (NovaMapPainter): reload the sheets it uses and repaint.
    NovaTilesetEx.refreshTilemap = function() {
        usedCache.map = null;
        var scene = SceneManager._scene, spriteset = scene && scene._spriteset;
        if (spriteset instanceof Spriteset_Map) {
            spriteset.loadTileset();
            spriteset._tilemap.refresh();
        }
    };

    Spriteset_Map.prototype.loadTileset = function() {
        this._tileset = $gameMap.tileset();
        if (!this._tileset) return;
        var tilemap = this._tilemap, names = this._tileset.tilesetNames;
        tilemap.bitmaps = [];
        for (var i = 0; i < names.length; i++) tilemap.bitmaps[i] = ImageManager.loadTileset(names[i]);
        tilemap._novaExtraIndex = {};
        usedSlots().forEach(function(slot) {
            tilemap._novaExtraIndex[slot] = tilemap.bitmaps.length;
            tilemap.bitmaps.push(ImageManager.loadTileset(SHEETS[slot].name));
        });
        var newTilesetFlags = $gameMap.tilesetFlags();
        tilemap.refreshTileset();
        if (!tilemap.flags.equals(newTilesetFlags)) tilemap.refresh();
        tilemap.flags = newTilesetFlags;
    };

    //=========================================================================
    // Drawing (canvas and WebGL tilemaps)
    //=========================================================================
    function extraIndex(tilemap, tileId) {
        var map = tilemap._novaExtraIndex;
        return map ? map[slotOf(tileId)] : undefined;
    }

    var _Tilemap_drawNormalTile = Tilemap.prototype._drawNormalTile;
    Tilemap.prototype._drawNormalTile = function(bitmap, tileId, dx, dy) {
        if (!isExtra(tileId)) return _Tilemap_drawNormalTile.apply(this, arguments);
        var index = extraIndex(this, tileId), source = index !== undefined ? this.bitmaps[index] : null;
        if (!source) return;
        var w = this._tileWidth, h = this._tileHeight, n = localOf(tileId);
        bitmap.bltImage(source, sheetX(n) * w, sheetY(n) * h, w, h, dx, dy, w, h);
    };

    // Canvas tilemap: the engine marks a table edge with the virtual id 10000 + (table tile id) and treats
    // every lower tile >= 10000 as one, which would swallow our ids. Same code as rpg_core's
    // Tilemap.prototype._paintTiles except that table edges are only 10000 .. BASE - 1.
    Tilemap.prototype._paintTiles = function(startX, startY, x, y) {
        var tableEdgeVirtualId = 10000;
        var mx = startX + x;
        var my = startY + y;
        var dx = (mx * this._tileWidth).mod(this._layerWidth);
        var dy = (my * this._tileHeight).mod(this._layerHeight);
        var lx = dx / this._tileWidth;
        var ly = dy / this._tileHeight;
        var tileId0 = this._readMapData(mx, my, 0);
        var tileId1 = this._readMapData(mx, my, 1);
        var tileId2 = this._readMapData(mx, my, 2);
        var tileId3 = this._readMapData(mx, my, 3);
        var shadowBits = this._readMapData(mx, my, 4);
        var upperTileId1 = this._readMapData(mx, my - 1, 1);
        var lowerTiles = [];
        var upperTiles = [];

        if (this._isHigherTile(tileId0)) upperTiles.push(tileId0); else lowerTiles.push(tileId0);
        if (this._isHigherTile(tileId1)) upperTiles.push(tileId1); else lowerTiles.push(tileId1);
        lowerTiles.push(-shadowBits);
        if (this._isTableTile(upperTileId1) && !this._isTableTile(tileId1)) {
            if (!Tilemap.isShadowingTile(tileId0)) lowerTiles.push(tableEdgeVirtualId + upperTileId1);
        }
        if (this._isOverpassPosition(mx, my)) {
            upperTiles.push(tileId2);
            upperTiles.push(tileId3);
        } else {
            if (this._isHigherTile(tileId2)) upperTiles.push(tileId2); else lowerTiles.push(tileId2);
            if (this._isHigherTile(tileId3)) upperTiles.push(tileId3); else lowerTiles.push(tileId3);
        }

        var lastLowerTiles = this._readLastTiles(0, lx, ly);
        if (!lowerTiles.equals(lastLowerTiles) || (Tilemap.isTileA1(tileId0) && this._frameUpdated)) {
            this._lowerBitmap.clearRect(dx, dy, this._tileWidth, this._tileHeight);
            for (var i = 0; i < lowerTiles.length; i++) {
                var lowerTileId = lowerTiles[i];
                if (lowerTileId < 0) {
                    this._drawShadow(this._lowerBitmap, shadowBits, dx, dy);
                } else if (lowerTileId >= tableEdgeVirtualId && lowerTileId < BASE) {
                    this._drawTableEdge(this._lowerBitmap, upperTileId1, dx, dy);
                } else {
                    this._drawTile(this._lowerBitmap, lowerTileId, dx, dy);
                }
            }
            this._writeLastTiles(0, lx, ly, lowerTiles);
        }

        var lastUpperTiles = this._readLastTiles(1, lx, ly);
        if (!upperTiles.equals(lastUpperTiles)) {
            this._upperBitmap.clearRect(dx, dy, this._tileWidth, this._tileHeight);
            for (var j = 0; j < upperTiles.length; j++) this._drawTile(this._upperBitmap, upperTiles[j], dx, dy);
            this._writeLastTiles(1, lx, ly, upperTiles);
        }
    };

    if (typeof ShaderTilemap !== 'undefined') {
        var _ShaderTilemap_drawNormalTile = ShaderTilemap.prototype._drawNormalTile;
        ShaderTilemap.prototype._drawNormalTile = function(layer, tileId, dx, dy) {
            if (!isExtra(tileId)) return _ShaderTilemap_drawNormalTile.apply(this, arguments);
            var index = extraIndex(this, tileId);
            if (index === undefined) return;
            var w = this._tileWidth, h = this._tileHeight, n = localOf(tileId);
            layer.addRect(index, sheetX(n) * w, sheetY(n) * h, dx, dy, w, h);
        };
    }

    // Events whose graphic is an extra tile.
    var _Sprite_Character_tilesetBitmap = Sprite_Character.prototype.tilesetBitmap;
    Sprite_Character.prototype.tilesetBitmap = function(tileId) {
        if (!isExtra(tileId)) return _Sprite_Character_tilesetBitmap.call(this, tileId);
        var sheet = SHEETS[slotOf(tileId)];
        return ImageManager.loadTileset(sheet ? sheet.name : '');
    };

    var _Sprite_Character_updateTileFrame = Sprite_Character.prototype.updateTileFrame;
    Sprite_Character.prototype.updateTileFrame = function() {
        if (!isExtra(this._tileId)) return _Sprite_Character_updateTileFrame.call(this);
        var pw = this.patternWidth(), ph = this.patternHeight(), n = localOf(this._tileId);
        this.setFrame(sheetX(n) * pw, sheetY(n) * ph, pw, ph);
    };
})();
