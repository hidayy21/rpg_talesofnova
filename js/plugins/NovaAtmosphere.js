//=============================================================================
// NovaAtmosphere.js
//=============================================================================
/*:
 * @plugindesc Atmosphere on the map: bloom, tilt-shift depth of field, colour
 * grade presets and vignette, sunbeams that follow the clock, drifting fog,
 * and floating pollen, dust or fireflies.
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
 * @param Fog Color
 * @desc Colour of the fog of a map with <fog: N> (map note <fog color: #rrggbb> overrides).
 * @default #d4ddd6
 *
 * @param Particles
 * @type number
 * @desc How many motes float over the map (0 = none).
 * @default 36
 *
 * @param Cinematic
 * @desc Film look (0 = off, 1 = strong): deeper shadows, cool shadows and warm highlights, darker corners, more depth of field. Map note <cinematic: 0.8>.
 * @default 0.75
 *
 * @param Contact Shadows
 * @desc Soft shadow on the ground at the foot of walls, cliffs and furniture (0 = off, 1 = dark). Map note <contact shadows: 0.5>.
 * @default 0.5
 *
 * @param Letterbox
 * @desc Height of each black bar in cutscenes, as a share of the screen (0 = never).
 * @default 0.1
 *
 * @param Auto Letterbox
 * @type boolean
 * @desc Slide the bars in by themselves while an Autorun event runs (a cutscene).
 * @default true
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
 *   <grade: forest>       colour grade preset (below)
 *   <saturation: 0.9>     colour strength on this map (after the preset)
 *   <contrast: 1.1>
 *   <fog: 0.6>            drifting fog over the map (0-1); it follows the
 *                         light: grey-blue and thinner at night
 *   <fog color: #c8d8d0>
 *   <fog bank: x1,y1,x2,y2,N>  a bank of thick mist (N 0-1) lying on that
 *                         rectangle of tiles, soft at the edges, slowly
 *                         drifting; several banks separated by ;
 *   <fog mystery>         the fog breathes: it slowly thickens and thins,
 *                         and a third layer of low wisps drifts across
 *
 *   <cinematic: 0.8>      film look on this map (0 = off)
 *   <contact shadows: 0>  shadows at the foot of walls and things (0 = off)
 *
 * Cinematic: a gentle S-curve (deeper shadows), shadows a touch cool and
 * highlights a touch warm, the four corners darker than the round vignette,
 * and a stronger tilt shift - so the map reads like a frame of film.
 *
 * Contact shadows: every tile that blocks on all sides (walls, cliffs,
 * furniture, tree trunks - not water) casts a soft shadow on the walkable
 * ground round it, mostly toward the bottom of the screen. It sits under the
 * characters and under the upper tiles (canopies, roofs).
 *
 * Letterbox: black bars slide in at the top and bottom while an Autorun event
 * runs (turn off with the Auto Letterbox parameter), or when asked:
 *   Cinema bars on        bars in (stay until "off" or "auto")
 *   Cinema bars off       bars out
 *   Cinema bars auto      back to automatic
 *
 * Grade presets: each tints the shadows and the highlights of the map and
 * sets its colour strength; they blend over a second when you change maps.
 *   warm      sunny town: golden highlights, rich colour
 *   noble     castle and royal streets: clean, slightly cool shadows
 *   coast     harbour and sea: blue shadows, bright air
 *   forest    woods: green-teal shadows, soft highlights
 *   mystic    deep or haunted woods: blue shadows, little colour
 *   interior  lamp-lit rooms: amber shadows, warm whites
 *   gloom     prisons, crypts: cold and nearly grey
 *   arcane    sealed vaults, magic: violet shadows
 *   neutral   none (the plugin's Saturation and Contrast only)
 *
 * Indoor sunbeams (<sunbeams: N> on a map without <outdoor>) are light from
 * the windows: they come with the daylight and are gone at night.
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
    var FOG_COLOR = P['Fog Color'] || '#d4ddd6';
    var CINEMATIC = num('Cinematic', 0.75);
    var CONTACT = num('Contact Shadows', 0.5);
    var LETTERBOX = num('Letterbox', 0.1);
    var AUTO_BARS = P['Auto Letterbox'] !== 'false';

    // name -> shadow tint, highlight tint (multipliers), saturation, contrast
    var GRADES = {
        neutral:  { low: [1, 1, 1],          high: [1, 1, 1],          sat: null, con: null },
        warm:     { low: [1.0, 0.98, 0.95],  high: [1.0, 0.98, 0.93],  sat: 1.1, con: 1.04 },
        noble:    { low: [0.95, 0.97, 1.03], high: [1.0, 0.99, 0.95],  sat: 1.06, con: 1.06 },
        coast:    { low: [0.9, 0.97, 1.06],  high: [0.98, 1.0, 1.0],  sat: 1.1, con: 1.04 },
        forest:   { low: [0.8, 0.94, 0.9],   high: [0.98, 1.03, 0.94], sat: 0.94, con: 1.1 },
        mystic:   { low: [0.62, 0.76, 0.92], high: [0.84, 0.93, 0.98], sat: 0.68, con: 1.14 },
        interior: { low: [1.02, 0.94, 0.84], high: [1.0, 0.96, 0.88], sat: 1.04, con: 1.04 },
        gloom:    { low: [0.88, 0.91, 1.03], high: [0.97, 0.98, 1.02], sat: 0.6, con: 1.12 },
        arcane:   { low: [0.92, 0.82, 1.1],  high: [1.0, 0.95, 1.08],  sat: 0.86, con: 1.08 }
    };
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
    window.NovaAtmosphere = window.NovaAtmosphere || { override: {} };
    function metaNum(key, fallback) {
        var o = window.NovaAtmosphere.override;
        if (o && o[key] !== undefined) return o[key];
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
        'uniform vec3 gradeLow;',
        'uniform vec3 gradeHigh;',
        'uniform float cine;',
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
        '    col *= mix(gradeLow, gradeHigh, smoothstep(0.05, 0.85, dot(col, LUMA)));',
        // cinematic: S-curve, cool shadows / warm highlights
        '    if (cine > 0.0) {',
        '        vec3 sc = clamp(col, 0.0, 1.0);',
        '        col = mix(col, sc * sc * (3.0 - 2.0 * sc), cine * 0.4);',
        '        float l = dot(col, LUMA);',
        '        col *= mix(vec3(1.0), mix(vec3(0.92, 0.97, 1.06), vec3(1.03, 1.0, 0.96), smoothstep(0.15, 0.75, l)), cine);',
        '    }',
        // vignette (round on a wide screen)
        '    vec2 v = (screen - 0.5) * vec2(screenSize.x / screenSize.y, 1.0) * 0.82;',
        '    col *= 1.0 - vignette * smoothstep(0.3, 0.85, length(v));',
        // cinematic corners: darker toward the four corners, a little toward top and bottom
        '    vec2 q = abs(screen - 0.5) * 2.0;',
        '    col *= 1.0 - cine * (0.8 * smoothstep(0.7, 1.42, length(q)) + 0.2 * smoothstep(0.55, 1.0, q.y));',
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
        this.uniforms.gradeLow = new Float32Array([1, 1, 1]);
        this.uniforms.gradeHigh = new Float32Array([1, 1, 1]);
        this.uniforms.cine = 0;
        this._grade = null;
    }
    AtmosphereFilter.prototype = Object.create(PIXI.Filter.prototype);
    AtmosphereFilter.prototype.constructor = AtmosphereFilter;

    function gradeTarget(on) {
        var g = GRADES[String(meta().grade || 'neutral').trim().toLowerCase()] || GRADES.neutral;
        if (!on) return { low: [1, 1, 1], high: [1, 1, 1], sat: 1, con: 1 };
        return { low: g.low, high: g.high, sat: metaNum('saturation', g.sat || SATURATION),
                 con: metaNum('contrast', g.con || CONTRAST) };
    }

    // instant: on a new map (no blend from the last one)
    AtmosphereFilter.prototype.sync = function(instant) {
        var on = enabled(), u = this.uniforms;
        u.bloom = on ? metaNum('bloom', BLOOM) : 0;
        var cine = on ? metaNum('cinematic', CINEMATIC) : 0;
        u.cine = mix(u.cine, cine, instant ? 1 : 0.05);
        u.tilt = on ? metaNum('tilt shift', TILT) * (1 + 0.6 * cine) : 0;
        u.vignette = on ? metaNum('vignette', VIGNETTE) : 0;
        var t = gradeTarget(on), g = this._grade, f = instant || !g ? 1 : 0.05;
        if (!g) g = this._grade = { low: t.low.slice(), high: t.high.slice(), sat: t.sat, con: t.con };
        for (var i = 0; i < 3; i++) {
            g.low[i] = mix(g.low[i], t.low[i], f);
            g.high[i] = mix(g.high[i], t.high[i], f);
            u.gradeLow[i] = g.low[i];
            u.gradeHigh[i] = g.high[i];
        }
        u.saturation = g.sat = mix(g.sat, t.sat, f);
        u.contrast = g.con = mix(g.con, t.con, f);
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
        if (isOutdoor()) return k * beamAt(minutesNow()).s;
        return k * Math.min(1, beamAt(minutesNow()).s / 0.6);      // window light: with the daylight, none at night
    };

    Sprite_NovaSunbeams.prototype.update = function() {
        Sprite.prototype.update.call(this);
        this._time++;
        this._strength = mix(this._strength, this.targetStrength(), 0.04);
        this.visible = this._strength > 0.01;
        if (!this.visible) return;
        var t = minutesNow();
        var c = window.NovaDayNight ? beamAt(t).color : [255, 240, 210];
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
    // Fog: two layers of soft cloud drifting at different speeds, fixed on the
    // map (they scroll with it), coloured by the light of the hour
    //=========================================================================
    var _fogBitmap = null;
    function fogBitmap() {
        if (_fogBitmap) return _fogBitmap;
        var size = 512, bmp = new Bitmap(size, size), ctx = ctxOf(bmp);
        var seed = 11;
        var rand = function() { seed = (seed * 16807) % 2147483647; return (seed - 1) / 2147483646; };
        for (var i = 0; i < 70; i++) {
            var x = rand() * size, y = rand() * size, r = 40 + rand() * 110, a = 0.05 + rand() * 0.12;
            // drawn on every side too, so the sheet tiles without seams
            for (var dx = -1; dx <= 1; dx++) {
                for (var dy = -1; dy <= 1; dy++) {
                    var cx = x + dx * size, cy = y + dy * size;
                    if (cx + r < 0 || cx - r > size || cy + r < 0 || cy - r > size) continue;
                    var g = ctx.createRadialGradient(cx, cy, 0, cx, cy, r);
                    g.addColorStop(0, 'rgba(255,255,255,' + a + ')');
                    g.addColorStop(1, 'rgba(255,255,255,0)');
                    ctx.fillStyle = g;
                    ctx.fillRect(cx - r, cy - r, r * 2, r * 2);
                }
            }
        }
        dirty(bmp);
        return (_fogBitmap = bmp);
    }

    function Sprite_NovaFog() { this.initialize.apply(this, arguments); }
    Sprite_NovaFog.prototype = Object.create(Sprite.prototype);
    Sprite_NovaFog.prototype.constructor = Sprite_NovaFog;

    Sprite_NovaFog.prototype.initialize = function() {
        Sprite.prototype.initialize.call(this);
        this._layers = [{ speed: 0.18, scale: 1.6, weight: 0.65 }, { speed: -0.1, scale: 2.4, weight: 0.5 },
                        { speed: 0.42, scale: 1.0, weight: 0.45, wisp: true }].map(function(d) {
            var s = new TilingSprite(fogBitmap());
            s.move(0, 0, Graphics.width, Graphics.height);
            s._d = d;
            s.scale.x = s.scale.y = 1;
            this.addChild(s);
            return s;
        }, this);
        this._strength = 0;
        this._drift = 0;
    };

    // <fog bank: x1,y1,x2,y2,N; ...>: thick mist lying on those tiles, fixed on the map
    function fogBanks() {
        if (!$dataMap) return [];
        if ($dataMap._novaFogBanks) return $dataMap._novaFogBanks;
        var raw = meta()['fog bank'];
        $dataMap._novaFogBanks = typeof raw !== 'string' ? [] : raw.split(';').map(function(part) {
            var n = part.split(',').map(Number);
            return n.length === 5 && n.every(function(v) { return !isNaN(v); }) ? n : null;
        }).filter(Boolean);
        return $dataMap._novaFogBanks;
    }

    var BANK_PAD = 80;                                            // the mist spills this far past the edge, softly
    function bankBitmap(w, h, seed) {
        var bmp = new Bitmap(w + BANK_PAD * 2, h + BANK_PAD * 2), ctx = ctxOf(bmp);
        var rand = function() { seed = (seed * 16807) % 2147483647; return (seed - 1) / 2147483646; };
        var count = Math.ceil(w * h / 2600);                      // loose clumps with gaps, not one white sheet
        for (var i = 0; i < count; i++) {
            var x = BANK_PAD + rand() * w, y = BANK_PAD + rand() * h, r = 60 + rand() * 90, a = 0.06 + rand() * 0.16;
            var g = ctx.createRadialGradient(x, y, 0, x, y, r);
            g.addColorStop(0, 'rgba(255,255,255,' + a + ')');
            g.addColorStop(1, 'rgba(255,255,255,0)');
            ctx.fillStyle = g;
            ctx.fillRect(x - r, y - r, r * 2, r * 2);
        }
        dirty(bmp);
        return bmp;
    }

    Sprite_NovaFog.prototype.buildBanks = function() {
        var tw = $gameMap.tileWidth(), th = $gameMap.tileHeight();
        this._banks = [];
        fogBanks().forEach(function(b, n) {
            var w = (b[2] - b[0] + 1) * tw, h = (b[3] - b[1] + 1) * th;
            for (var k = 0; k < 2; k++) {                         // two sheets that sway apart and breathe out of step
                var s = new Sprite(bankBitmap(w, h, 101 + n * 31 + k * 7));
                s._mx = b[0] * tw - BANK_PAD;
                s._my = b[1] * th - BANK_PAD;
                s._k = Math.max(0, Math.min(1, b[4]));
                s._phase = n * 1.7 + k * 2.9;
                this._banks.push(s);
                this.addChild(s);
            }
        }, this);
    };

    Sprite_NovaFog.prototype.targetStrength = function() {
        return enabled() ? Math.max(0, Math.min(1, metaNum('fog', 0))) : 0;
    };

    Sprite_NovaFog.prototype.update = function() {
        Sprite.prototype.update.call(this);
        if (!this._banks) this.buildBanks();
        this._strength = mix(this._strength, this.targetStrength(), 0.03);
        this._bankFade = mix(this._bankFade || 0, enabled() ? 1 : 0, 0.03);
        this.visible = this._strength > 0.01 || (this._banks.length > 0 && this._bankFade > 0.01);
        if (!this.visible) return;
        this._drift++;
        var c = hex(meta()['fog color'] || FOG_COLOR) || [212, 221, 214];
        var amb = window.NovaLighting && NovaLighting.ambient ? NovaLighting.ambient() : null;
        var light = 1;
        if (amb) {
            c = [0, 1, 2].map(function(i) { return c[i] * (0.25 + 0.75 * amb[i] / 255); });
            light = 0.55 + 0.45 * (amb[0] + amb[1] + amb[2]) / 765;       // thinner in the dark
        }
        var tint = (Math.round(c[0]) << 16) | (Math.round(c[1]) << 8) | Math.round(c[2]);
        var ox = $gameMap.displayX() * $gameMap.tileWidth(), oy = $gameMap.displayY() * $gameMap.tileHeight();
        var mystery = !!meta()['fog mystery'], t = this._drift;
        this._layers.forEach(function(s, i) {
            var d = s._d;
            s.visible = this._strength > 0.01 && (!d.wisp || mystery);
            if (!s.visible) return;
            s.tint = tint;
            s.origin.x = (ox / d.scale + t * d.speed) % 512;
            s.origin.y = (oy / d.scale + Math.sin(t * 0.002 + i) * 30 + (d.wisp ? Math.sin(t * 0.004) * 60 : 0)) % 512;
            // mystery: each layer swells and fades on its own slow beat, so banks of mist come and go
            var breath = mystery ? 0.7 + 0.3 * Math.sin(t * (0.004 + i * 0.0017) + i * 2.1) : 1;
            s.opacity = 255 * Math.min(1, this._strength * light * d.weight * 1.6 * breath);
        }, this);
        // banks are a shade greyer than the open fog: a heavier, colder mist
        var bankTint = (Math.round(c[0] * 0.86) << 16) | (Math.round(c[1] * 0.86) << 8) | Math.round(c[2] * 0.9);
        this._banks.forEach(function(s) {
            var p = s._phase;
            s.tint = bankTint;
            s.x = s._mx - ox + Math.sin(t * 0.003 + p) * 28;     // drifting slowly to and fro
            s.y = s._my - oy + Math.sin(t * 0.0023 + p * 1.3) * 10;
            var breath = 0.55 + 0.45 * Math.sin(t * 0.005 + p);
            s.opacity = 255 * Math.min(1, s._k * light * breath * this._bankFade * 1.25);
        }, this);
    };

    //=========================================================================
    // Contact shadows: a soft shadow on the walkable ground round every tile that
    // blocks on all four sides. Drawn once per map at a quarter of the tile size
    // (smoothing does the rest), it lives in the tilemap between the lower tiles
    // and the characters.
    //=========================================================================
    var CS = 12;                                   // shadow pixels per tile
    function isSolid(x, y) {
        if (!$gameMap.isValid(x, y)) return false;
        if ($gameMap.isBoatPassable(x, y) || $gameMap.isShipPassable(x, y)) return false;   // water
        var empty = true;
        for (var z = 0; z < 4; z++) if ($gameMap.tileId(x, y, z)) { empty = false; break; }
        if (empty) return false;                   // the void round a dungeon
        return [2, 4, 6, 8].every(function(d) { return !$gameMap.isPassable(x, y, d); });
    }

    function Sprite_NovaContact() { this.initialize.apply(this, arguments); }
    Sprite_NovaContact.prototype = Object.create(Sprite.prototype);
    Sprite_NovaContact.prototype.constructor = Sprite_NovaContact;
    Sprite_NovaContact.prototype.initialize = function() {
        Sprite.prototype.initialize.call(this);
        this.z = 0.5;                              // above the lower tiles (0), below characters (1+)
        this._strength = enabled() ? metaNum('contact shadows', CONTACT) : 0;
        if (this._strength > 0 && $dataMap && $gameMap.tileset()) this.build();
        this.scale.x = $gameMap.tileWidth() / CS;
        this.scale.y = $gameMap.tileHeight() / CS;
    };
    Sprite_NovaContact.prototype.build = function() {
        var w = $gameMap.width(), h = $gameMap.height();
        if (w * h > 40000) return;                 // the world map: skip
        var mask = document.createElement('canvas');
        mask.width = w * CS; mask.height = h * CS;
        var m = mask.getContext('2d'), solid = [], grid = [];
        for (var y = 0; y < h; y++) for (var x = 0; x < w; x++) if ((grid[y * w + x] = isSolid(x, y))) solid.push([x, y]);
        // casters: walls, cliffs and roofs (A3/A4), and things two tiles wide or more. A small single thing (a sign,
        // a pot, a grave) already has its shadow painted in its tile.
        var at = function(x, y) { return x >= 0 && x < w && grid[y * w + x]; };
        m.fillStyle = '#000';
        solid.forEach(function(p) {
            var x = p[0], y = p[1], wall = false;
            for (var z = 0; z < 2; z++) { var t = $gameMap.tileId(x, y, z); if (t >= Tilemap.TILE_ID_A3 && t < Tilemap.TILE_ID_MAX) wall = true; }
            if (wall || at(x - 1, y) || at(x + 1, y)) m.fillRect(x * CS, y * CS, CS, CS);
        });
        if (!solid.length) return;
        var bmp = new Bitmap(w * CS, h * CS);
        bmp.smooth = true;
        var c = ctxOf(bmp);
        // the shadow falls toward the bottom of the screen (light from above and in front): the solid shape moved
        // down half a tile and blurred. No ring all round - round a small thing it would leave a pale square.
        c.save();
        c.filter = 'blur(' + Math.round(CS * 0.3) + 'px)';
        c.globalAlpha = 0.9; c.drawImage(mask, CS * 0.08, CS * 0.5);
        c.filter = 'blur(' + Math.round(CS * 0.5) + 'px)';
        c.globalAlpha = 0.35; c.drawImage(mask, CS * 0.12, CS * 0.7);
        c.restore();
        // only on the ground, never on the thing itself - cut out every solid tile, with soft edges
        var cut = document.createElement('canvas');
        cut.width = mask.width; cut.height = mask.height;
        var k = cut.getContext('2d');
        k.fillStyle = '#000';
        solid.forEach(function(p) { k.fillRect(p[0] * CS + 1, p[1] * CS + 1, CS - 2, CS - 2); });
        c.save();
        c.globalCompositeOperation = 'destination-out';
        c.filter = 'blur(2px)';
        c.drawImage(cut, 0, 0); c.drawImage(cut, 0, 0);
        c.restore();
        dirty(bmp);
        this.bitmap = bmp;
        this.opacity = Math.round(255 * Math.min(1, this._strength * 1.3));
    };
    Sprite_NovaContact.prototype.update = function() {
        Sprite.prototype.update.call(this);
        this.x = Math.round(-$gameMap.displayX() * $gameMap.tileWidth());
        this.y = Math.round(-$gameMap.displayY() * $gameMap.tileHeight());
    };

    //=========================================================================
    // Letterbox: black bars in cutscenes
    //=========================================================================
    function barsWanted() {
        var mode = $gameSystem._novaBars || 'auto';
        if (mode === 'on') return true;
        if (mode === 'off' || !AUTO_BARS) return false;
        var it = $gameMap._interpreter;
        if (!it.isRunning()) return false;
        var ev = it.eventId() > 0 && $gameMap.event(it.eventId());
        return !!(ev && ev._trigger === 3);
    }

    function Sprite_NovaLetterbox() { this.initialize.apply(this, arguments); }
    Sprite_NovaLetterbox.prototype = Object.create(Sprite.prototype);
    Sprite_NovaLetterbox.prototype.constructor = Sprite_NovaLetterbox;
    Sprite_NovaLetterbox.prototype.initialize = function() {
        Sprite.prototype.initialize.call(this);
        var bh = Math.max(1, Math.round(Graphics.height * LETTERBOX));
        this._bh = bh;
        this._t = barsWanted() ? 1 : 0;
        this._top = new Sprite(new Bitmap(Graphics.width, bh));
        this._bottom = new Sprite(new Bitmap(Graphics.width, bh));
        this._top.bitmap.fillAll('#000000'); this._bottom.bitmap.fillAll('#000000');
        this.addChild(this._top); this.addChild(this._bottom);
        this.update();
    };
    Sprite_NovaLetterbox.prototype.update = function() {
        Sprite.prototype.update.call(this);
        if (LETTERBOX <= 0) { this.visible = false; return; }
        var target = barsWanted() ? 1 : 0;
        this._t += Math.max(-0.06, Math.min(0.06, target - this._t));
        var e = this._t * this._t * (3 - 2 * this._t), off = Math.round(this._bh * (1 - e));
        this.visible = this._t > 0.001;
        this._top.y = -off;
        this._bottom.y = Graphics.height - this._bh + off;
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
        this._novaFog = new Sprite_NovaFog();
        this._baseSprite.addChildAt(this._novaFog, idx);
        this._baseSprite.addChildAt(this._novaSunbeams, idx + 1);
        this._baseSprite.addChildAt(this._novaMotes, idx + 2);
        this._novaContact = new Sprite_NovaContact();
        this._tilemap.addChild(this._novaContact);
    };

    var _createUpperLayer = Spriteset_Map.prototype.createUpperLayer;
    Spriteset_Map.prototype.createUpperLayer = function() {
        _createUpperLayer.call(this);
        this._novaLetterbox = new Sprite_NovaLetterbox();
        this.addChild(this._novaLetterbox);
    };

    var _createToneChanger = Spriteset_Map.prototype.createToneChanger;
    Spriteset_Map.prototype.createToneChanger = function() {
        _createToneChanger.call(this);
        if (!Graphics.isWebGL()) return;
        try {
            this._novaAtmosphere = new AtmosphereFilter();
            this._novaAtmosphere.sync(true);
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
        if (command.toLowerCase() === 'cinema' && String(args[0] || '').toLowerCase() === 'bars') {
            var mode = String(args[1] || 'auto').toLowerCase();
            $gameSystem._novaBars = mode === 'on' || mode === 'off' ? mode : 'auto';
            return;
        }
        if (command.toLowerCase() !== 'atmosphere') return;
        $gameSystem._novaAtmosphereOff = String(args[0] || '').toLowerCase() === 'off';
    };
})();
