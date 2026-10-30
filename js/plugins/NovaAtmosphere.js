//=============================================================================
// NovaAtmosphere.js
//=============================================================================
/*:
 * @plugindesc Atmosphere on the map: bloom, tilt-shift depth of field, colour
 * grade and vignette, sunbeams that follow the clock, and floating pollen,
 * dust or fireflies.
 * @author Project Nova
 *
 * @param Bloom
 * @desc Glow around bright things: lit paths, lamps, fire (0 = off, 1 = strong). Map note <bloom: 0.5> overrides.
 * @default 0.35
 *
 * @param Bloom Threshold
 * @desc Brightness (0-1) from which pixels start to glow. Lower = more of the map glows.
 * @default 0.62
 *
 * @param Bloom Radius
 * @type number
 * @desc How far the glow spreads, in pixels.
 * @default 14
 *
 * @param Tilt Shift
 * @desc Blur toward the top and bottom of the screen, like a miniature (0 = off, 1 = strong). Map note <tilt shift: 0.5>.
 * @default 0.6
 *
 * @param Tilt Shift Band
 * @desc Height of the sharp band around the middle, as a share of the screen (0-1).
 * @default 0.42
 *
 * @param Vignette
 * @desc Darker corners (0 = off, 1 = strong). Map note <vignette: 0.3>.
 * @default 0.28
 *
 * @param Saturation
 * @desc Colour strength (1 = unchanged, 1.1 = a little richer).
 * @default 1.08
 *
 * @param Contrast
 * @desc 1 = unchanged.
 * @default 1.04
 *
 * @param Sunbeams
 * @desc Strength of the light shafts on outdoor maps (0 = off). Map note <sunbeams: 0.8> also turns them on indoors.
 * @default 0.7
 *
 * @param Sunbeam Times
 * @type note
 * @desc Strength and colour of the sunbeams through the day (HH:MM = strength, #rrggbb). Blended in between.
 * @default "00:00 = 0, #9fb4ff\n05:00 = 0, #ffb37a\n06:00 = 0.8, #ffc48a\n07:30 = 1, #ffe0a8\n10:00 = 0.6, #fff6dc\n14:30 = 0.6, #fff6dc\n16:30 = 1, #ffd08a\n17:45 = 1, #ffa860\n18:45 = 0, #ff8a60"
 *
 * @param Particles
 * @type number
 * @desc How many motes float over the map (0 = none).
 * @default 36
 *
 * @help
 * Place below NovaLighting and NovaDayNight.
 *
 * Bloom, tilt shift, colour and vignette are one shader over the map (not
 * over pictures, windows or the HUD). They need WebGL; on the canvas
 * renderer only sunbeams and particles show. Players can turn everything
 * off with "Visual Effects" in Options (for slow computers).
 *
 * Sunbeams: soft light shafts fixed on outdoor maps (they scroll with the ground). (<outdoor>). With
 * NovaDayNight they follow the clock: golden in the morning, pale at noon,
 * orange at sunset, gone at night; they fall from the left in the morning
 * and from the right in the afternoon.
 *
 * Particles: on outdoor maps pollen by day and fireflies by night. Indoors
 * none, unless the map note asks for them.
 *
 * Map note tags
 *   <bloom: 0.5>          bloom on this map
 *   <tilt shift: 0>       tilt shift on this map (0 = off)
 *   <vignette: 0.4>       vignette on this map
 *   <sunbeams: 0.8>       sunbeams on this map (also indoors: light from windows)
 *   <no sunbeams>
 *   <particles: dust>     pollen, dust, fireflies, embers, snow, auto or none
 *
 * Plugin command
 *   Atmosphere off / on   turn every effect off or on (cutscenes)
 */

(function() {
    'use strict';

    var P = PluginManager.parameters('NovaAtmosphere');
    function num(name, fallback) { var v = Number(P[name]); return P[name] === undefined || P[name] === '' || isNaN(v) ? fallback : v; }
    var BLOOM = num('Bloom', 0.35);
    var THRESHOLD = num('Bloom Threshold', 0.62);
    var BLOOM_RADIUS = num('Bloom Radius', 14);
    var TILT = num('Tilt Shift', 0.6);
    var TILT_BAND = num('Tilt Shift Band', 0.42);
    var VIGNETTE = num('Vignette', 0.28);
    var SATURATION = num('Saturation', 1.08);
    var CONTRAST = num('Contrast', 1.04);
    var SUNBEAMS = num('Sunbeams', 0.7);
    var PARTICLES = num('Particles', 36);
    var NIGHT_SWITCH = Number(PluginManager.parameters('NovaLighting')['Night Switch'] || 0);

    function hex(c) {
        c = String(c || '').trim().replace('#', '');
        var n = parseInt(c, 16);
        return isNaN(n) ? null : [n >> 16 & 255, n >> 8 & 255, n & 255];
    }
    function parseTime(text) {
        var m = String(text || '').match(/(\d+)\s*[:.]\s*(\d+)/);
        return m ? (Number(m[1]) * 60 + Number(m[2])) % 1440 : 0;
    }
    function ctxOf(bitmap) { return bitmap._context || bitmap.context; }
    function dirty(bitmap) {
        if (bitmap._setDirty) bitmap._setDirty();
        else if (bitmap._baseTexture) bitmap._baseTexture.update();
    }
    function mix(a, b, f) { return a + (b - a) * f; }

    // [{ t: minutes, s: strength, color: [r,g,b] }] sorted by time
    var BEAM_TIMES = [];
    (function() {
        var raw = P['Sunbeam Times'] || '';
        try { raw = JSON.parse(raw); } catch (e) { /* plain text */ }
        String(raw).split(/\r?\n/).forEach(function(line) {
            var m = line.match(/^\s*(\d+\s*[:.]\s*\d+)\s*=\s*([\d.]+)\s*,\s*(#?[0-9a-fA-F]{6})/);
            if (m) BEAM_TIMES.push({ t: parseTime(m[1]), s: Number(m[2]), color: hex(m[3]) });
        });
        BEAM_TIMES.sort(function(a, b) { return a.t - b.t; });
        if (!BEAM_TIMES.length) BEAM_TIMES.push({ t: 0, s: 1, color: [255, 246, 220] });
    })();

    function beamAt(t) {
        var K = BEAM_TIMES, a = K[K.length - 1], b = K[0], ta = a.t - 1440, tb = b.t;
        for (var i = 0; i < K.length; i++) {
            if (K[i].t <= t) { a = K[i]; ta = a.t; b = K[(i + 1) % K.length]; tb = b.t + (i + 1 < K.length ? 0 : 1440); }
        }
        var f = tb > ta ? (t - ta) / (tb - ta) : 0;
        return { s: mix(a.s, b.s, f), color: [0, 1, 2].map(function(i) { return mix(a.color[i], b.color[i], f); }) };
    }

    //=========================================================================
    // On / off: Options ("Visual Effects") and the plugin command
    //=========================================================================
    ConfigManager.novaAtmosphere = true;
    var _makeData = ConfigManager.makeData;
    ConfigManager.makeData = function() {
        var config = _makeData.call(this);
        config.novaAtmosphere = this.novaAtmosphere;
        return config;
    };
    var _applyData = ConfigManager.applyData;
    ConfigManager.applyData = function(config) {
        _applyData.call(this, config);
        this.novaAtmosphere = config.novaAtmosphere === undefined ? true : !!config.novaAtmosphere;
    };
    var _addGeneralOptions = Window_Options.prototype.addGeneralOptions;
    Window_Options.prototype.addGeneralOptions = function() {
        _addGeneralOptions.call(this);
        this.addCommand('Visual Effects', 'novaAtmosphere');
    };

    function enabled() { return ConfigManager.novaAtmosphere && !($gameSystem && $gameSystem._novaAtmosphereOff); }

    function meta() { return $dataMap ? $dataMap.meta : {}; }
    function metaNum(key, fallback) {
        var m = meta();
        return m[key] !== undefined && m[key] !== true && !isNaN(Number(m[key])) ? Number(m[key]) : fallback;
    }
    function isOutdoor() { return !!meta().outdoor; }
    function minutesNow() { return window.NovaDayNight ? NovaDayNight.minutes() : 600; }
    function isNight() {
        if (window.NovaDayNight) return NovaDayNight.isNight();
        return NIGHT_SWITCH > 0 && $gameSwitches.value(NIGHT_SWITCH);
    }

    //=========================================================================
    // The shader: bloom, tilt shift, colour grade, vignette in one pass
    //=========================================================================
    var FRAGMENT = [
        'precision mediump float;',
        'varying vec2 vTextureCoord;',
        'uniform sampler2D uSampler;',
        'uniform vec4 filterArea;',
        'uniform vec4 filterClamp;',
        'uniform vec2 screenSize;',
        'uniform float bloom;',
        'uniform float threshold;',
        'uniform float bloomRadius;',
        'uniform float tilt;',
        'uniform float tiltBand;',
        'uniform float vignette;',
        'uniform float saturation;',
        'uniform float contrast;',
        'const vec3 LUMA = vec3(0.299, 0.587, 0.114);',
        'vec3 tap(vec2 uv) { return texture2D(uSampler, clamp(uv, filterClamp.xy, filterClamp.zw)).rgb; }',
        'void main(void) {',
        '    vec4 base = texture2D(uSampler, vTextureCoord);',
        '    vec2 px = 1.0 / filterArea.xy;',
        '    vec2 screen = (vTextureCoord * filterArea.xy + filterArea.zw) / screenSize;',
        '    vec3 col = base.rgb;',
        // tilt shift: a sharp band in the middle, blur growing toward top and bottom
        '    float d = clamp((abs(screen.y - 0.5) - tiltBand * 0.5) / (0.5 - tiltBand * 0.5), 0.0, 1.0);',
        '    float blurR = tilt * 4.5 * d * d;',
        '    if (blurR > 0.3) {',
        '        vec3 acc = col;',
        '        for (int i = 0; i < 16; i++) {',
        '            float fi = float(i);',
        '            float a = fi * 2.39996;',
        '            float r = sqrt((fi + 0.5) / 16.0) * blurR;',
        '            acc += tap(vTextureCoord + vec2(cos(a), sin(a)) * r * px);',
        '        }',
        '        col = acc / 17.0;',
        '    }',
        // bloom: bright pixels around this one, soft threshold
        '    if (bloom > 0.0) {',
        '        vec3 b = vec3(0.0);',
        '        for (int i = 0; i < 24; i++) {',
        '            float fi = float(i);',
        '            float a = fi * 2.39996 + 0.7;',
        '            float r = sqrt((fi + 0.5) / 24.0) * bloomRadius;',
        '            vec3 s = tap(vTextureCoord + vec2(cos(a), sin(a)) * r * px);',
        '            b += s * smoothstep(threshold, threshold + 0.3, dot(s, LUMA));',
        '        }',
        '        col += b / 24.0 * bloom;',
        '    }',
        // colour grade
        '    col = mix(vec3(dot(col, LUMA)), col, saturation);',
        '    col = (col - 0.5) * contrast + 0.5;',
        // vignette (round on a wide screen)
        '    vec2 v = (screen - 0.5) * vec2(screenSize.x / screenSize.y, 1.0) * 0.82;',
        '    col *= 1.0 - vignette * smoothstep(0.3, 0.85, length(v));',
        '    gl_FragColor = vec4(clamp(col, 0.0, 1.0), base.a);',
        '}'
    ].join('\n');

    function AtmosphereFilter() {
        PIXI.Filter.call(this, null, FRAGMENT);
        this.uniforms.screenSize = new Float32Array([Graphics.width, Graphics.height]);
        this.uniforms.threshold = THRESHOLD;
        this.uniforms.bloomRadius = BLOOM_RADIUS;
        this.uniforms.tiltBand = TILT_BAND;
        this.uniforms.saturation = SATURATION;
        this.uniforms.contrast = CONTRAST;
    }
    AtmosphereFilter.prototype = Object.create(PIXI.Filter.prototype);
    AtmosphereFilter.prototype.constructor = AtmosphereFilter;

    AtmosphereFilter.prototype.sync = function() {
        var on = enabled(), u = this.uniforms;
        u.bloom = on ? metaNum('bloom', BLOOM) : 0;
        u.tilt = on ? metaNum('tilt shift', TILT) : 0;
        u.vignette = on ? metaNum('vignette', VIGNETTE) : 0;
        u.saturation = on ? SATURATION : 1;
        u.contrast = on ? CONTRAST : 1;
    };

    //=========================================================================
    // Sunbeams: soft shafts falling across the screen, additive
    //=========================================================================
    var _beamBitmap = null;
    function beamBitmap() {
        if (_beamBitmap) return _beamBitmap;
        var w = 128, h = 512;
        _beamBitmap = new Bitmap(w, h);
        var ctx = ctxOf(_beamBitmap);
        var g = ctx.createLinearGradient(0, 0, w, 0);
        g.addColorStop(0, 'rgba(255,255,255,0)');
        g.addColorStop(0.3, 'rgba(255,255,255,0.55)');
        g.addColorStop(0.5, 'rgba(255,255,255,1)');
        g.addColorStop(0.7, 'rgba(255,255,255,0.55)');
        g.addColorStop(1, 'rgba(255,255,255,0)');
        ctx.fillStyle = g;
        ctx.fillRect(0, 0, w, h);
        // fade in from the top, out toward the bottom
        ctx.globalCompositeOperation = 'destination-in';
        var v = ctx.createLinearGradient(0, 0, 0, h);
        v.addColorStop(0, 'rgba(0,0,0,0)');
        v.addColorStop(0.2, 'rgba(0,0,0,1)');
        v.addColorStop(0.6, 'rgba(0,0,0,0.7)');
        v.addColorStop(1, 'rgba(0,0,0,0)');
        ctx.fillStyle = v;
        ctx.fillRect(0, 0, w, h);
        ctx.globalCompositeOperation = 'source-over';
        dirty(_beamBitmap);
        return _beamBitmap;
    }

    function Sprite_NovaSunbeams() { this.initialize.apply(this, arguments); }
    Sprite_NovaSunbeams.prototype = Object.create(Sprite.prototype);
    Sprite_NovaSunbeams.prototype.constructor = Sprite_NovaSunbeams;

    Sprite_NovaSunbeams.prototype.initialize = function() {
        Sprite.prototype.initialize.call(this);
        this._span = Graphics.width + 1200;
        this._beams = [];
        var seed = 7;                                             // same beams in the same places on every visit
        var rand = function() { seed = (seed * 16807) % 2147483647; return (seed - 1) / 2147483646; };
        for (var i = 0; i < 7; i++) {
            var s = new Sprite(beamBitmap());
            s.anchor.x = 0.5;
            s.anchor.y = 0;
            s.blendMode = Graphics.BLEND_ADD;
            s._baseX = (i + rand() * 0.6) / 7 * this._span;
            s._wide = 0.6 + rand() * 1.4;
            s._long = 1.6 + rand() * 0.7;
            s._phase = rand() * Math.PI * 2;
            s._speed = 0.006 + rand() * 0.008;
            s._weight = 0.5 + rand() * 0.5;
            this._beams.push(s);
            this.addChild(s);
        }
        this._strength = 0;
        this._time = 0;
    };

    Sprite_NovaSunbeams.prototype.targetStrength = function() {
        if (!enabled() || meta()['no sunbeams']) return 0;
        var k = metaNum('sunbeams', isOutdoor() ? SUNBEAMS : 0);
        if (k <= 0) return 0;
        if (!window.NovaDayNight) return isNight() ? 0 : k * 0.8;
        return isOutdoor() ? k * beamAt(minutesNow()).s : k;
    };

    Sprite_NovaSunbeams.prototype.update = function() {
        Sprite.prototype.update.call(this);
        this._time++;
        this._strength = mix(this._strength, this.targetStrength(), 0.04);
        this.visible = this._strength > 0.01;
        if (!this.visible) return;
        var t = minutesNow();
        var c = isOutdoor() && window.NovaDayNight ? beamAt(t).color : [255, 240, 210];
        // morning light from the left, afternoon light from the right
        var angle = isOutdoor() ? Math.max(-0.55, Math.min(0.55, (t - 720) / 360 * 0.5)) : -0.35;
        var tint = (Math.round(c[0]) << 16) | (Math.round(c[1]) << 8) | Math.round(c[2]);
        // each beam is a slanted line fixed on the map: where it crosses the top of the
        // screen moves with the camera, sideways as well as up and down along its slant
        var ox = $gameMap.displayX() * $gameMap.tileWidth(), oy = $gameMap.displayY() * $gameMap.tileHeight();
        var slope = Math.tan(angle), span = this._span;
        this._beams.forEach(function(s) {
            var x = s._baseX - ox - (oy - 80) * slope;
            s.x = ((x % span) + span) % span - 600;
            s.y = -80;
            s.rotation = angle;
            s.scale.x = s._wide;
            s.scale.y = (Graphics.height + 160) / 512 * s._long;
            s.tint = tint;
            var pulse = 0.875 + 0.125 * Math.sin(this._time * s._speed + s._phase);   // breathes between 75% and 100%
            s.opacity = 255 * Math.min(1, this._strength * 0.32 * s._weight * pulse);
        }, this);
    };

    //=========================================================================
    // Particles: pollen, dust, fireflies, embers, snow
    //=========================================================================
    var _moteBitmaps = {};
    function moteBitmap(size, soft) {
        var key = size + '|' + soft;
        if (_moteBitmaps[key]) return _moteBitmaps[key];
        var bmp = new Bitmap(size * 2, size * 2), ctx = ctxOf(bmp);
        var g = ctx.createRadialGradient(size, size, 0, size, size, size);
        g.addColorStop(0, 'rgba(255,255,255,1)');
        g.addColorStop(soft, 'rgba(255,255,255,0.45)');
        g.addColorStop(1, 'rgba(255,255,255,0)');
        ctx.fillStyle = g;
        ctx.fillRect(0, 0, size * 2, size * 2);
        dirty(bmp);
        return (_moteBitmaps[key] = bmp);
    }

    // kind -> how the motes look and move
    var KINDS = {
        pollen:    { color: 0xfff2c0, size: 5, soft: 0.25, alpha: 0.7,  vx: 0.12, vy: -0.05, wander: 0.35, twinkle: 0.04, scale: [0.4, 1.0] },
        dust:      { color: 0xffe8c8, size: 4, soft: 0.3,  alpha: 0.35, vx: 0.03, vy: 0.02,  wander: 0.15, twinkle: 0.02, scale: [0.3, 0.7] },
        fireflies: { color: 0xd8ff7a, size: 9, soft: 0.15, alpha: 0.95, vx: 0,    vy: 0,     wander: 0.6,  twinkle: 0.05, scale: [0.6, 1.1], blink: true },
        embers:    { color: 0xffa040, size: 5, soft: 0.2,  alpha: 0.85, vx: 0.1,  vy: -0.5,  wander: 0.4,  twinkle: 0.12, scale: [0.3, 0.7] },
        snow:      { color: 0xffffff, size: 5, soft: 0.5,  alpha: 0.8,  vx: 0.25, vy: 0.7,   wander: 0.3,  twinkle: 0,    scale: [0.4, 1.0], normal: true }
    };

    function particleKind() {
        if (!enabled() || PARTICLES <= 0) return null;
        var k = String(meta().particles || 'auto').trim().toLowerCase();
        if (k === 'none') return null;
        if (k === 'auto') {
            if (!isOutdoor()) return null;
            return isNight() ? 'fireflies' : 'pollen';
        }
        return KINDS[k] ? k : null;
    }

    function Sprite_NovaMotes() { this.initialize.apply(this, arguments); }
    Sprite_NovaMotes.prototype = Object.create(Sprite.prototype);
    Sprite_NovaMotes.prototype.constructor = Sprite_NovaMotes;

    Sprite_NovaMotes.prototype.initialize = function() {
        Sprite.prototype.initialize.call(this);
        this._kind = null;
        this._fade = 0;
        this._spanX = Graphics.width + 64;
        this._spanY = Graphics.height + 64;
        this._motes = [];
    };

    Sprite_NovaMotes.prototype.build = function(kind) {
        this._motes.forEach(function(m) { this.removeChild(m); }, this);
        this._motes = [];
        this._kind = kind;
        if (!kind) return;
        var K = KINDS[kind], count = kind === 'fireflies' ? Math.round(PARTICLES * 0.6) : PARTICLES;
        for (var i = 0; i < count; i++) {
            var s = new Sprite(moteBitmap(K.size, K.soft));
            s.anchor.x = s.anchor.y = 0.5;
            s.blendMode = K.normal ? Graphics.BLEND_NORMAL : Graphics.BLEND_ADD;
            s.tint = K.color;
            s._wx = Math.random() * this._spanX;                  // position on the map, in pixels
            s._wy = Math.random() * this._spanY;
            s._phase = Math.random() * Math.PI * 2;
            s._depth = K.scale[0] + Math.random() * (K.scale[1] - K.scale[0]);
            s.scale.x = s.scale.y = s._depth;
            this._motes.push(s);
            this.addChild(s);
        }
    };

    Sprite_NovaMotes.prototype.update = function() {
        Sprite.prototype.update.call(this);
        var kind = particleKind();
        if (kind !== this._kind) {
            this._fade -= 0.04;                                   // fade out, then switch kind
            if (this._fade <= 0) { this._fade = 0; this.build(kind); }
        } else if (kind) {
            this._fade = Math.min(1, this._fade + 0.02);
        }
        this.visible = !!this._kind && this._fade > 0;
        if (!this.visible) return;
        var K = KINDS[this._kind], t = Graphics.frameCount;
        var ox = $gameMap.displayX() * $gameMap.tileWidth(), oy = $gameMap.displayY() * $gameMap.tileHeight();
        var sx = this._spanX, sy = this._spanY, fade = this._fade;
        this._motes.forEach(function(s) {
            var p = s._phase;
            s._wx += K.vx * s._depth + Math.sin(t * 0.011 + p) * K.wander * 0.5;
            s._wy += K.vy * s._depth + Math.cos(t * 0.013 + p * 1.7) * K.wander * 0.4;
            s.x = (((s._wx - ox) % sx) + sx) % sx - 32;
            s.y = (((s._wy - oy) % sy) + sy) % sy - 32;
            var a = K.alpha;
            if (K.blink) a *= Math.max(0, Math.sin(t * K.twinkle + p * 3)) * 0.85 + 0.15;
            else if (K.twinkle) a *= 0.6 + 0.4 * Math.sin(t * K.twinkle + p * 5);
            s.opacity = 255 * a * fade * (0.5 + s._depth * 0.5);
        });
    };

    //=========================================================================
    // Hook into the map
    //=========================================================================
    var _createLowerLayer = Spriteset_Map.prototype.createLowerLayer;
    Spriteset_Map.prototype.createLowerLayer = function() {
        _createLowerLayer.call(this);
        this._novaSunbeams = new Sprite_NovaSunbeams();
        this._novaMotes = new Sprite_NovaMotes();
        var idx = this._baseSprite.children.indexOf(this._weather);  // above lights, below weather
        if (idx < 0) idx = this._baseSprite.children.length;
        this._baseSprite.addChildAt(this._novaSunbeams, idx);
        this._baseSprite.addChildAt(this._novaMotes, idx + 1);
    };

    var _createToneChanger = Spriteset_Map.prototype.createToneChanger;
    Spriteset_Map.prototype.createToneChanger = function() {
        _createToneChanger.call(this);
        if (!Graphics.isWebGL()) return;
        try {
            this._novaAtmosphere = new AtmosphereFilter();
            this._novaAtmosphere.sync();
            this._baseSprite.filters = this._baseSprite.filters.concat([this._novaAtmosphere]);
        } catch (e) {
            console.warn('NovaAtmosphere: shader unavailable', e);
            this._novaAtmosphere = null;
        }
    };

    var _update = Spriteset_Map.prototype.update;
    Spriteset_Map.prototype.update = function() {
        _update.call(this);
        if (this._novaAtmosphere) this._novaAtmosphere.sync();
    };

    var _pluginCommand = Game_Interpreter.prototype.pluginCommand;
    Game_Interpreter.prototype.pluginCommand = function(command, args) {
        _pluginCommand.call(this, command, args);
        if (command.toLowerCase() !== 'atmosphere') return;
        $gameSystem._novaAtmosphereOff = String(args[0] || '').toLowerCase() === 'off';
    };
})();
