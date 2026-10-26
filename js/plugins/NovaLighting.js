//=============================================================================
// NovaLighting.js
//=============================================================================
/*:
 * @plugindesc Dynamic lighting: ambient darkness, point lights (lamps, fire,
 * windows, candles), a day/night switch, and soft character shadows that lean
 * away from nearby lights.
 * @author Project Nova
 *
 * @param Night Switch
 * @type switch
 * @desc While ON, maps tagged <outdoor> use the night ambient colour.
 * @default 10
 *
 * @param Night Ambient
 * @desc Ambient colour of outdoor maps at night (#rrggbb). Darker = darker night.
 * @default #2c3658
 *
 * @param Player Light
 * @desc Lantern around the party when the ambient is dark: radius,#color (blank = none).
 * @default 130,#ffd9a8
 *
 * @param Character Shadows
 * @type boolean
 * @desc Soft shadow under the player, followers and NPCs.
 * @default true
 *
 * @param Dynamic Shadows
 * @type boolean
 * @desc Shadows stretch away from nearby lights. Off = soft round shadow everywhere.
 * @default false
 *
 * @param Glow Strength
 * @desc Warm glow added around lights (0 = none, 1 = strong). Map note <glow: 0.4> overrides.
 * @default 0.32
 *
 * @param Shadow Opacity
 * @type number
 * @min 0
 * @max 255
 * @default 150
 *
 * @param Tile Lights
 * @type note
 * @desc One per line: tilesetId: tileId tileId ... = radius, #color [, flicker] [, offsetY]
 * @default "2: 211 = 160, #ffd29a, flicker\n2: 32 33 34 35 36 43 48 = 46, #ffc878, night\n2: 64 72 = 0, #000000\n3: 128 129 130 136 137 138 = 210, #ff9a48, flicker, 30\n3: 131 132 133 139 140 141 = 150, #ff9a48, flicker, 20\n3: 112 = 110, #ff8a40, flicker\n3: 16 17 18 32 33 34 35 37 38 39 = 150, #c8d6ff, , 70"
 *
 * @param Character Lights
 * @type note
 * @desc One per line: characterName : index (or *) = radius, #color [, flicker] [, offsetY]
 * @default "!Flame: 0 1 2 = 130, #ffb060, flicker\n!Flame: 3 4 = 200, #ff9040, flicker\n!Flame: 5 = 170, #7aa8ff, flicker\n!Flame: 6 7 = 90, #fff4c0, flicker\n!Other2: 1 3 5 7 = 190, #ff9a40, flicker\n!Other2: 2 = 110, #a8e0ff\n!Door2: 0 1 = 150, #ff5a6a, flicker\n!Door2: 4 5 6 7 = 120, #b090ff, flicker\n!Crystal: * = 140, #9fd8ff, flicker"
 *
 * @help
 * ---------------------------------------------------------------------------
 * Map note tags
 *   <ambient: #rrggbb>        Constant ambient light (interiors, caves).
 *                             #ffffff = fully lit, #000000 = pitch black.
 *   <outdoor>                 Follows the day/night switch.
 *   <night ambient: #rrggbb>  Night colour for this outdoor map only.
 *   <no player light>         No lantern around the party on this map.
 *   <glow: 0.4>               Strength of the glow around lights on this map.
 *
 * Bright rooms: use a light ambient such as <ambient: #ece6e0>. The room stays
 * almost fully lit and fire, lamps and windows add a warm glow on top.
 *
 * Event note (or a Comment on the active page)
 *   <light: radius, #color>               a light on this event
 *   <light: radius, #color, flicker, -24> flicker + vertical offset (px)
 *   <no shadow>                           no character shadow for this event
 *
 * Plugin commands
 *   NovaLight ambient #rrggbb   override the ambient on every map
 *   NovaLight ambient reset     back to the map's own ambient
 *   NovaLight night on|off      set the Night Switch
 * ---------------------------------------------------------------------------
 * Lights only appear where the ambient is darker than white, so daytime
 * outdoor maps cost nothing. Tiles marked "night" glow only at night.
 */

(function() {
    'use strict';

    var P = PluginManager.parameters('NovaLighting');
    var NIGHT_SWITCH = Number(P['Night Switch'] || 10);
    var NIGHT_COLOR = String(P['Night Ambient'] || '#2c3658');
    var SHADOWS = String(P['Character Shadows'] || 'true') === 'true';
    var SHADOW_OPACITY = Number(P['Shadow Opacity'] || 150);
    var DYNAMIC_SHADOWS = String(P['Dynamic Shadows'] || 'false') === 'true';
    var GLOW = Number(P['Glow Strength'] === undefined ? 0.32 : P['Glow Strength']);
    var SCALE = 0.5;                       // light map is rendered at half resolution (it's all soft gradients)

    function parseNote(s) { try { return JSON.parse(s); } catch (e) { return s || ''; } }
    function hex(c) {
        c = String(c || '').trim().replace('#', '');
        if (c.length === 3) c = c[0] + c[0] + c[1] + c[1] + c[2] + c[2];
        var n = parseInt(c, 16);
        return isNaN(n) ? null : [n >> 16 & 255, n >> 8 & 255, n & 255];
    }
    function parseLight(spec) {
        var p = spec.split(',').map(function(s) { return s.trim(); });
        var r = Number(p[0]); var col = hex(p[1]);
        if (!r || !col) return null;
        var flags = p.slice(2);
        var off = 0;
        flags.forEach(function(f) { if (f && !isNaN(Number(f))) off = Number(f); });
        return { radius: r, color: col, flicker: flags.indexOf('flicker') >= 0, night: flags.indexOf('night') >= 0, offsetY: off };
    }

    var PLAYER_LIGHT = P['Player Light'] ? parseLight(String(P['Player Light'])) : null;

    // tilesetId -> { tileId: light }
    var TILE_LIGHTS = {};
    String(parseNote(P['Tile Lights'])).split(/\r?\n/).forEach(function(line) {
        var m = line.match(/^\s*(\d+)\s*:\s*([\d\s]+)=(.*)$/);
        if (!m) return;
        var light = parseLight(m[3]);
        var ts = TILE_LIGHTS[m[1]] = TILE_LIGHTS[m[1]] || {};
        m[2].trim().split(/\s+/).forEach(function(id) { ts[Number(id)] = light; });   // radius 0 = explicitly none
    });
    // characterName -> { index|'*': light }
    var CHAR_LIGHTS = {};
    String(parseNote(P['Character Lights'])).split(/\r?\n/).forEach(function(line) {
        var m = line.match(/^\s*(.+?)\s*:\s*([\d\s*]+)=(.*)$/);
        if (!m) return;
        var light = parseLight(m[3]);
        var c = CHAR_LIGHTS[m[1]] = CHAR_LIGHTS[m[1]] || {};
        m[2].trim().split(/\s+/).forEach(function(i) { c[i] = light; });
    });

    function isNight() { return NIGHT_SWITCH > 0 && $gameSwitches.value(NIGHT_SWITCH); }

    // ------------------------------------------------------------------ ambient
    function mapAmbient() {
        if ($gameSystem._novaAmbient) return hex($gameSystem._novaAmbient);
        var meta = $dataMap ? $dataMap.meta : {};
        if (meta.ambient) return hex(meta.ambient);
        if (meta.outdoor && isNight()) return hex(meta['night ambient'] || NIGHT_COLOR);
        return null;
    }

    // ------------------------------------------------------------------ light sources
    Game_Event.prototype.novaLight = function() {
        if (this._novaLightPage !== this._pageIndex) {
            this._novaLightPage = this._pageIndex;
            this._novaLight = null;
            var src = this.event().note || '';
            var page = this.page();
            if (page) page.list.forEach(function(c) { if (c.code === 108 || c.code === 408) src += '\n' + c.parameters[0]; });
            var m = src.match(/<light\s*:\s*([^>]+)>/i);
            if (m) this._novaLight = parseLight(m[1]);
            else if (page) {
                var table = CHAR_LIGHTS[this.characterName()];
                if (table) this._novaLight = table[String(this.characterIndex())] || table['*'] || null;
            }
            this._novaNoShadow = /<no shadow>/i.test(src);
        }
        return this._novaLight && this._novaLight.radius ? this._novaLight : null;
    };

    function scanTileLights() {
        var list = [];
        var table = TILE_LIGHTS[String($gameMap.tilesetId())];
        if (!table || !$dataMap) return list;
        var w = $dataMap.width, h = $dataMap.height, data = $dataMap.data;
        for (var z = 0; z < 4; z++) {
            for (var y = 0; y < h; y++) {
                for (var x = 0; x < w; x++) {
                    var light = table[data[(z * h + y) * w + x]];
                    if (light && light.radius) list.push({ x: x, y: y, light: light, seed: (x * 7 + y * 13) % 100 });
                }
            }
        }
        return list;
    }

    // ------------------------------------------------------------------ the light map sprite
    function Sprite_NovaLight() { this.initialize.apply(this, arguments); }
    Sprite_NovaLight.prototype = Object.create(Sprite.prototype);
    Sprite_NovaLight.prototype.constructor = Sprite_NovaLight;

    Sprite_NovaLight.prototype.initialize = function() {
        Sprite.prototype.initialize.call(this);
        this.bitmap = new Bitmap(Math.ceil(Graphics.width * SCALE), Math.ceil(Graphics.height * SCALE));
        this.scale.x = this.scale.y = 1 / SCALE;
        this.blendMode = Graphics.BLEND_MULTIPLY;
        this._tileLights = scanTileLights();
        // additive glow drawn on top: brightens around lights without darkening anything else
        this._glow = new Sprite(new Bitmap(this.bitmap.width, this.bitmap.height));
        this._glow.scale.x = this._glow.scale.y = 1 / SCALE;
        this._glow.blendMode = Graphics.BLEND_ADD;
        this._ambient = null;
        this._current = null;
        this._time = 0;
    };

    Sprite_NovaLight.prototype.update = function() {
        Sprite.prototype.update.call(this);
        this._time++;
        var target = mapAmbient();
        if (!target) target = [255, 255, 255];
        if (!this._current) this._current = target.slice();
        for (var i = 0; i < 3; i++) {          // ease toward the target (day/night fades)
            var d = target[i] - this._current[i];
            this._current[i] = Math.abs(d) < 1 ? target[i] : this._current[i] + d * 0.06;
        }
        var lit = this._current[0] >= 254 && this._current[1] >= 254 && this._current[2] >= 254;
        this.visible = !lit;
        this._glow.visible = !lit;
        NovaLighting.active = !lit;
        NovaLighting.lights = [];
        if (!lit) this.redraw();
    };

    Sprite_NovaLight.prototype.redraw = function() {
        var bmp = this.bitmap, ctx = bmp._context || bmp.context;
        var gb = this._glow.bitmap, gctx = gb._context || gb.context;
        var a = this._current;
        var meta0 = $dataMap ? $dataMap.meta : {};
        this._glowStrength = meta0.glow !== undefined ? Number(meta0.glow) : GLOW;
        gctx.globalCompositeOperation = 'source-over';
        gctx.clearRect(0, 0, gb.width, gb.height);
        gctx.globalCompositeOperation = 'lighter';
        this._gctx = gctx;
        ctx.globalCompositeOperation = 'source-over';
        ctx.fillStyle = 'rgb(' + Math.round(a[0]) + ',' + Math.round(a[1]) + ',' + Math.round(a[2]) + ')';
        ctx.fillRect(0, 0, bmp.width, bmp.height);
        ctx.globalCompositeOperation = 'lighter';
        var tw = $gameMap.tileWidth(), th = $gameMap.tileHeight();
        var night = isNight(), t = this._time, self = this;
        var darkness = 1 - (a[0] + a[1] + a[2]) / 765;

        this._tileLights.forEach(function(L) {
            if (L.light.night && !night) return;
            var sx = ($gameMap.adjustX(L.x) + 0.5) * tw, sy = ($gameMap.adjustY(L.y) + 0.5) * th + L.light.offsetY;
            self.drawLight(ctx, sx, sy, L.light, t + L.seed * 3);
        });
        $gameMap.events().forEach(function(ev) {
            var light = ev.novaLight();
            if (!light || ev._erased || ev.isTransparent()) return;
            self.drawLight(ctx, ev.screenX(), ev.screenY() - 24 + light.offsetY, light, t + ev.eventId() * 11);
        });
        var meta = $dataMap ? $dataMap.meta : {};
        var pl = meta['player light'] ? parseLight(meta['player light']) : PLAYER_LIGHT;
        if (pl && !meta['no player light'] && darkness > 0.35 && !$gamePlayer.isTransparent()) {
            this.drawLight(ctx, $gamePlayer.screenX(), $gamePlayer.screenY() - 24, pl, t);
        }
        if (bmp._setDirty) bmp._setDirty(); else if (bmp._baseTexture) bmp._baseTexture.update();
        if (gb._setDirty) gb._setDirty(); else if (gb._baseTexture) gb._baseTexture.update();
    };

    Sprite_NovaLight.prototype.drawLight = function(ctx, sx, sy, light, t) {
        var r = light.radius;
        if (sx < -r || sy < -r || sx > Graphics.width + r || sy > Graphics.height + r) return;
        NovaLighting.lights.push({ x: sx, y: sy, r: r });
        if (light.flicker) r *= 1 + Math.sin(t * 0.21) * 0.035 + Math.sin(t * 0.53) * 0.025;
        var x = sx * SCALE, y = sy * SCALE, rr = r * SCALE, c = light.color;
        var g = ctx.createRadialGradient(x, y, 0, x, y, rr);
        var rgb = c[0] + ',' + c[1] + ',' + c[2];
        g.addColorStop(0, 'rgba(' + rgb + ',1)');
        g.addColorStop(0.45, 'rgba(' + rgb + ',0.55)');
        g.addColorStop(1, 'rgba(' + rgb + ',0)');
        ctx.fillStyle = g;
        ctx.fillRect(x - rr, y - rr, rr * 2, rr * 2);
        var k = this._glowStrength;
        if (k > 0) {
            var gr = rr * 0.8, gg = this._gctx.createRadialGradient(x, y, 0, x, y, gr);
            gg.addColorStop(0, 'rgba(' + rgb + ',' + k + ')');
            gg.addColorStop(0.5, 'rgba(' + rgb + ',' + (k * 0.35) + ')');
            gg.addColorStop(1, 'rgba(' + rgb + ',0)');
            this._gctx.fillStyle = gg;
            this._gctx.fillRect(x - gr, y - gr, gr * 2, gr * 2);
        }
    };

    var NovaLighting = { active: false, lights: [] };
    window.NovaLighting = NovaLighting;

    // ------------------------------------------------------------------ character shadows
    var _shadowBitmap = null;
    function shadowBitmap() {
        if (!_shadowBitmap) {
            _shadowBitmap = new Bitmap(48, 48);
            var ctx = _shadowBitmap._context || _shadowBitmap.context;
            var g = ctx.createRadialGradient(24, 24, 0, 24, 24, 24);
            g.addColorStop(0, 'rgba(0,0,0,1)');
            g.addColorStop(0.6, 'rgba(0,0,0,0.75)');
            g.addColorStop(1, 'rgba(0,0,0,0)');
            ctx.fillStyle = g;
            ctx.fillRect(0, 0, 48, 48);
            if (_shadowBitmap._setDirty) _shadowBitmap._setDirty();
        }
        return _shadowBitmap;
    }

    function Sprite_NovaShadow() { this.initialize.apply(this, arguments); }
    Sprite_NovaShadow.prototype = Object.create(Sprite.prototype);
    Sprite_NovaShadow.prototype.constructor = Sprite_NovaShadow;

    Sprite_NovaShadow.prototype.initialize = function(charSprite) {
        Sprite.prototype.initialize.call(this, shadowBitmap());
        this._target = charSprite;
        this.anchor.x = this.anchor.y = 0.5;
        this.z = 2;                                   // under characters (3), above lower events (1)
    };

    Sprite_NovaShadow.prototype.update = function() {
        Sprite.prototype.update.call(this);
        var s = this._target, ch = s._character;
        var show = s.visible && ch && !ch.isTransparent() && s.bitmap && s.bitmap.isReady() && !s._tileId &&
                   ch.characterName() && ch.characterName()[0] !== '!' && !(ch instanceof Game_Vehicle) &&
                   !(ch instanceof Game_Event && (ch._novaNoShadow || ch._erased || ch.novaLight())) &&
                   ch._priorityType === 1;
        if (ch instanceof Game_Follower) show = show && ch.isVisible();
        this.visible = !!show;
        if (!show) return;
        var pw = s.patternWidth ? s.patternWidth() : 48;
        var base = Math.max(0.6, Math.min(2.2, pw / 48));
        var jump = ch.jumpHeight ? ch.jumpHeight() : 0;
        var shrink = Math.max(0.4, 1 - jump / 60);
        var x = s.x, y = s.y - 3 + jump;              // the character sprite's y is raised while jumping
        var sx = 0.82 * base * shrink, sy = 0.36 * base * shrink, rot = 0, dx = 0, dy = 0;
        var opacity = SHADOW_OPACITY * (s.opacity / 255);
        // lean away from the strongest nearby light
        if (DYNAMIC_SHADOWS && NovaLighting.active) {
            var best = null, bestW = 0;
            NovaLighting.lights.forEach(function(L) {
                var vx = x - L.x, vy = (y - 12) - L.y, d = Math.sqrt(vx * vx + vy * vy);
                var w = 1 - d / (L.r * 1.15);
                if (w > bestW && d > 4) { bestW = w; best = { vx: vx / d, vy: vy / d }; }
            });
            if (best) {
                rot = Math.atan2(best.vy, best.vx);
                sx = (0.6 + bestW * 0.9) * base * shrink;
                dx = best.vx * 10 * bestW; dy = best.vy * 6 * bestW;
                opacity = Math.min(220, opacity * (1 + bestW * 0.8));
            }
        }
        this.x = x + dx; this.y = y + dy;
        this.rotation = rot;
        this.scale.x = sx; this.scale.y = sy;
        if (rot) { this.scale.y = sy * 0.9; }
        this.opacity = opacity;
    };

    // ------------------------------------------------------------------ hook into the map
    var _createCharacters = Spriteset_Map.prototype.createCharacters;
    Spriteset_Map.prototype.createCharacters = function() {
        _createCharacters.call(this);
        if (!SHADOWS) return;
        this._novaShadows = this._characterSprites.map(function(s) {
            var sh = new Sprite_NovaShadow(s);
            this._tilemap.addChild(sh);
            return sh;
        }, this);
    };

    var _createLowerLayer = Spriteset_Map.prototype.createLowerLayer;
    Spriteset_Map.prototype.createLowerLayer = function() {
        _createLowerLayer.call(this);
        this._novaLight = new Sprite_NovaLight();
        var idx = this._baseSprite.children.indexOf(this._tilemap);
        this._baseSprite.addChildAt(this._novaLight, idx + 1);   // above characters, below weather & pictures
        this._baseSprite.addChildAt(this._novaLight._glow, idx + 2);
    };

    // ------------------------------------------------------------------ plugin commands
    var _pluginCommand = Game_Interpreter.prototype.pluginCommand;
    Game_Interpreter.prototype.pluginCommand = function(command, args) {
        _pluginCommand.call(this, command, args);
        if (command !== 'NovaLight') return;
        var sub = (args[0] || '').toLowerCase();
        if (sub === 'ambient') $gameSystem._novaAmbient = (args[1] || '').toLowerCase() === 'reset' ? null : args[1];
        if (sub === 'night') $gameSwitches.setValue(NIGHT_SWITCH, (args[1] || 'on').toLowerCase() === 'on');
    };
})();
