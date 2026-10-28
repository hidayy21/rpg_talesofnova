//=============================================================================
// NovaDayNight.js
//=============================================================================
/*:
 * @plugindesc Day and night: an in-game clock that runs on the map, outdoor
 * maps going from dawn to day, sunset and night, lamps lighting up, and a
 * clock HUD with a turning sky dial.
 * @author Project Nova
 *
 * @param Day Length
 * @type number
 * @decimals 1
 * @min 1
 * @desc Real minutes for one whole in-game day (24 hours). 40 = one in-game hour every 100 seconds.
 * @default 40
 *
 * @param Start Time
 * @desc Time of day when a new game starts (HH:MM).
 * @default 08:00
 *
 * @param Clock Step
 * @type number
 * @min 1
 * @desc The HUD shows the time in steps of this many in-game minutes (10 = 07:40, 07:50 ...).
 * @default 10
 *
 * @param Lights On
 * @desc From this time the Night Switch of NovaLighting turns ON: lamps and windows light up.
 * @default 18:00
 *
 * @param Lights Off
 * @desc From this time the Night Switch turns OFF again.
 * @default 06:00
 *
 * @param Sky Colors
 * @type note
 * @desc Ambient colour of outdoor maps through the day (HH:MM = #rrggbb, or "night" for the map's night colour). Blended in between.
 * @default "00:00 = night\n04:30 = night\n05:30 = #6c6fa8\n06:30 = #e3b5a4\n08:00 = #fff6ea\n10:00 = #ffffff\n15:30 = #ffffff\n16:30 = #fff0da\n17:30 = #ffbb7a\n18:30 = #b97a86\n19:30 = night"
 *
 * @param Pause During Events
 * @type boolean
 * @desc The clock stops while an event runs or a message is open on the map.
 * @default true
 *
 * @param Stop Switch
 * @type switch
 * @desc While this switch is ON the clock stops and the HUD hides (cutscenes). 0: none.
 * @default 0
 *
 * @param Hour Variable
 * @type variable
 * @desc Kept equal to the hour (0-23), for event conditions. 0: none.
 * @default 0
 *
 * @param Minute Variable
 * @type variable
 * @default 0
 *
 * @param Day Variable
 * @type variable
 * @desc Kept equal to the day number (1, 2, 3 ...). 0: none.
 * @default 0
 *
 * @param Show HUD
 * @type boolean
 * @default true
 *
 * @help
 * Place below NovaMenu and NovaLighting.
 *
 * The clock
 *   Time only passes on the map: not in menus, battles, or (with Pause
 *   During Events) while an event runs. One day lasts Day Length real
 *   minutes. The clock is saved with the game.
 *
 * Outdoor maps (<outdoor> in the map note, see NovaLighting)
 *   take their light from Sky Colors: blue dawn, warm morning, full
 *   daylight, orange sunset, dusk, then the night colour. Between Lights On
 *   and Lights Off the Night Switch is ON, so lamps, windows and every
 *   event page that checks that switch follow the clock. Interiors keep
 *   their own <ambient>.
 *
 * HUD (bottom left of the map screen)
 *   A sky dial turning with the day (sun, sunset, moon), the time, the part
 *   of the day and the day number. It fades while a message is open.
 *
 * Plugin commands
 *   Clock set 18:30        set the time (same day)
 *   Clock add 2            add hours (decimals allowed: 0.5 = 30 minutes)
 *   Clock sleep 07:00      move on to the next 07:00 (the next morning: inns)
 *   Clock stop / start     stop or restart the clock
 *   Clock hud hide / show  hide or show the HUD
 *
 * Script (conditions, damage formulas ...)
 *   NovaDayNight.hour()  NovaDayNight.minute()  NovaDayNight.day()
 *   NovaDayNight.phase()   'Dawn', 'Morning', 'Noon', 'Afternoon', 'Evening', 'Night'
 *   NovaDayNight.isNight()
 */

(function() {
    'use strict';

    var params = PluginManager.parameters('NovaDayNight');
    var DAY_FRAMES = Math.max(1, Number(params['Day Length'] || 40)) * 60 * 60;
    var STEP = Math.max(1, Number(params['Clock Step'] || 10));
    var PAUSE_EVENTS = String(params['Pause During Events'] || 'true') === 'true';
    var STOP_SWITCH = Number(params['Stop Switch'] || 0);
    var HOUR_VAR = Number(params['Hour Variable'] || 0);
    var MINUTE_VAR = Number(params['Minute Variable'] || 0);
    var DAY_VAR = Number(params['Day Variable'] || 0);
    var SHOW_HUD = String(params['Show HUD'] || 'true') === 'true';
    var NIGHT_SWITCH = Number(PluginManager.parameters('NovaLighting')['Night Switch'] || 0);

    function parseTime(text, fallback) {
        var m = String(text || '').match(/(\d+)\s*[:.]\s*(\d+)/);
        return m ? (Number(m[1]) * 60 + Number(m[2])) % 1440 : fallback;
    }
    var START = parseTime(params['Start Time'], 480);
    var LIGHTS_ON = parseTime(params['Lights On'], 1080);
    var LIGHTS_OFF = parseTime(params['Lights Off'], 360);

    function hex(c) {
        c = String(c || '').trim().replace('#', '');
        var n = parseInt(c, 16);
        return isNaN(n) ? null : [n >> 16 & 255, n >> 8 & 255, n & 255];
    }

    // [{ t: minutes, color: [r,g,b] | 'night' }] sorted by time
    var SKY = [];
    (function() {
        var raw = params['Sky Colors'] || '';
        try { raw = JSON.parse(raw); } catch (e) { /* plain text */ }
        String(raw).split(/\r?\n/).forEach(function(line) {
            var m = line.match(/^\s*(\d+\s*[:.]\s*\d+)\s*=\s*(\S+)/);
            if (!m) return;
            var color = m[2].toLowerCase() === 'night' ? 'night' : hex(m[2]);
            if (color) SKY.push({ t: parseTime(m[1], 0), color: color });
        });
        SKY.sort(function(a, b) { return a.t - b.t; });
        if (!SKY.length) SKY.push({ t: 0, color: [255, 255, 255] });
    })();

    var PHASES = [[270, 'Dawn'], [360, 'Morning'], [660, 'Noon'], [840, 'Afternoon'], [1020, 'Evening'], [1140, 'Night']];

    //=========================================================================
    // The clock: minutes since midnight (fractional) and the day number
    //=========================================================================
    function clock() {
        var c = $gameSystem._novaClock;
        if (!c) c = $gameSystem._novaClock = { minutes: START, day: 1, stopped: false, hudHidden: false };
        return c;
    }

    var NovaDayNight = {};
    NovaDayNight.minutes = function() { return $gameSystem ? clock().minutes : START; };
    NovaDayNight.hour = function() { return Math.floor(this.minutes() / 60); };
    NovaDayNight.minute = function() { return Math.floor(this.minutes() % 60); };
    NovaDayNight.day = function() { return $gameSystem ? clock().day : 1; };
    NovaDayNight.isNight = function() { return isLightsTime(this.minutes()); };
    NovaDayNight.phase = function(minutes) {
        var t = minutes === undefined ? this.minutes() : minutes, name = PHASES[PHASES.length - 1][1];
        for (var i = 0; i < PHASES.length; i++) if (t >= PHASES[i][0]) name = PHASES[i][1];
        return t < PHASES[0][0] ? 'Night' : name;
    };

    // "07:40" in Clock Step steps
    NovaDayNight.timeText = function() {
        var t = Math.floor(this.minutes() / STEP) * STEP;
        return pad(Math.floor(t / 60)) + ':' + pad(t % 60);
    };
    function pad(n) { return (n < 10 ? '0' : '') + n; }

    function isLightsTime(t) {
        return LIGHTS_ON > LIGHTS_OFF ? (t >= LIGHTS_ON || t < LIGHTS_OFF) : (t >= LIGHTS_ON && t < LIGHTS_OFF);
    }

    NovaDayNight.set = function(minutes, nextDayIfPast) {
        var c = clock(), m = ((minutes % 1440) + 1440) % 1440;
        if (nextDayIfPast && m <= c.minutes) c.day++;
        c.minutes = m;
        this.sync();
    };

    NovaDayNight.add = function(minutes) {
        var c = clock(), t = c.minutes + minutes;
        c.day += Math.floor(t / 1440);
        c.minutes = ((t % 1440) + 1440) % 1440;
        this.sync();
    };

    // Night Switch and the optional variables follow the clock (written only when they change).
    NovaDayNight.sync = function() {
        var night = this.isNight();
        if (NIGHT_SWITCH && $gameSwitches.value(NIGHT_SWITCH) !== night) $gameSwitches.setValue(NIGHT_SWITCH, night);
        if (HOUR_VAR && $gameVariables.value(HOUR_VAR) !== this.hour()) $gameVariables.setValue(HOUR_VAR, this.hour());
        if (MINUTE_VAR && $gameVariables.value(MINUTE_VAR) !== this.minute()) $gameVariables.setValue(MINUTE_VAR, this.minute());
        if (DAY_VAR && $gameVariables.value(DAY_VAR) !== this.day()) $gameVariables.setValue(DAY_VAR, this.day());
    };

    NovaDayNight.isStopped = function() {
        return clock().stopped || (STOP_SWITCH > 0 && $gameSwitches.value(STOP_SWITCH));
    };

    // Ambient colour for an outdoor map now; nightColor is that map's night colour.
    NovaDayNight.ambient = function(nightColor, minutes) {
        var t = minutes === undefined ? this.minutes() : minutes;
        var night = nightColor || [44, 54, 88];
        var col = function(k) { return k.color === 'night' ? night : k.color; };
        var a = SKY[SKY.length - 1], b = SKY[0], ta = a.t - 1440, tb = b.t;
        for (var i = 0; i < SKY.length; i++) {
            if (SKY[i].t <= t) { a = SKY[i]; ta = a.t; b = SKY[(i + 1) % SKY.length]; tb = b.t + (i + 1 < SKY.length ? 0 : 1440); }
        }
        var f = tb > ta ? (t - ta) / (tb - ta) : 0, ca = col(a), cb = col(b);
        return [0, 1, 2].map(function(i) { return Math.round(ca[i] + (cb[i] - ca[i]) * f); });
    };

    // The clock runs on the map only.
    var _Scene_Map_update = Scene_Map.prototype.update;
    Scene_Map.prototype.update = function() {
        _Scene_Map_update.call(this);
        if (!this.isActive() || NovaDayNight.isStopped()) return;
        if (PAUSE_EVENTS && ($gameMap.isEventRunning() || $gameMessage.isBusy())) return;
        NovaDayNight.add(1440 / DAY_FRAMES);
    };

    // Right time of day as soon as a map (or a loaded save) starts.
    var _Scene_Map_start = Scene_Map.prototype.start;
    Scene_Map.prototype.start = function() {
        _Scene_Map_start.call(this);
        NovaDayNight.sync();
    };

    //=========================================================================
    // Sprite_NovaClockHud: sky dial + time, bottom left
    //=========================================================================
    var UI = window.NovaUI;
    var COLOR = UI ? UI.COLOR : { frame: '#6f93c9', accent: '#9cc0ec', accentLit: '#d8e8fb', pending: '#e8cf8f',
                                  text: '#eaf0f8', dim: '#9fb1c9', panelTop: 'rgba(26, 36, 64, 0.94)',
                                  panelBottom: 'rgba(12, 18, 34, 0.96)' };
    var HUD_W = 218, HUD_H = 80, DIAL_R = 31, MARGIN = 12;

    function ctxOf(bitmap) { return bitmap._context || bitmap.context; }
    function dirty(bitmap) {
        if (bitmap._setDirty) bitmap._setDirty();
        else if (bitmap._baseTexture) bitmap._baseTexture.update();
    }
    function rgb(c, a) { return 'rgba(' + c[0] + ',' + c[1] + ',' + c[2] + ',' + (a === undefined ? 1 : a) + ')'; }

    // Sky colour for the dial: the ambient, but brighter so day reads as blue sky.
    function skyAt(t) {
        var sun = Math.cos((t - 720) / 1440 * Math.PI * 2);          // 1 at noon, -1 at midnight
        var day = [104, 170, 232], dusk = [236, 128, 70], night = [18, 26, 58];
        var amb = NovaDayNight.ambient(night, t);
        var warm = amb[0] - amb[2];                                   // > 0 around sunset / sunrise
        var base = sun > 0 ? day : night;
        var mix = function(p, q, f) { return [0, 1, 2].map(function(i) { return p[i] + (q[i] - p[i]) * f; }); };
        var c = sun > -0.15 ? mix(night, day, Math.min(1, (sun + 0.15) / 0.6)) : base;
        if (warm > 30) c = mix(c, dusk, Math.min(1, (warm - 30) / 110));
        return c.map(Math.round);
    }

    function Sprite_NovaClockHud() { this.initialize.apply(this, arguments); }
    Sprite_NovaClockHud.prototype = Object.create(Sprite.prototype);
    Sprite_NovaClockHud.prototype.constructor = Sprite_NovaClockHud;

    Sprite_NovaClockHud.prototype.initialize = function() {
        Sprite.prototype.initialize.call(this);
        this.x = MARGIN;
        this.y = Graphics.boxHeight - HUD_H - MARGIN;
        this._panel = new Sprite(new Bitmap(HUD_W, HUD_H));
        this._dial = new Sprite(new Bitmap(DIAL_R * 2 + 4, DIAL_R * 2 + 4));
        this._dial.anchor.x = this._dial.anchor.y = 0.5;
        this._dial.x = 12 + DIAL_R;
        this._dial.y = HUD_H / 2;
        this._ring = new Sprite(new Bitmap(DIAL_R * 2 + 14, DIAL_R * 2 + 16));
        this._ring.x = this._dial.x - DIAL_R - 7;
        this._ring.y = this._dial.y - DIAL_R - 9;
        this._text = new Sprite(new Bitmap(HUD_W - 90, HUD_H));
        this._text.x = 86;
        this.addChild(this._panel);
        this.addChild(this._dial);
        this.addChild(this._ring);
        this.addChild(this._text);
        this._key = '';
        this.opacity = 0;
        this.drawPanel();
        this.drawDial();
        this.drawRing();
    };

    Sprite_NovaClockHud.prototype.drawPanel = function() {
        var bmp = this._panel.bitmap, ctx = ctxOf(bmp), w = HUD_W, h = HUD_H, c = 10;
        var pts = UI ? UI.panelShape(1, 1, w - 2, h - 2, c) : [[1, 1], [w - 1, 1], [w - 1, h - 1], [1, h - 1]];
        var path = function() {
            ctx.beginPath();
            ctx.moveTo(pts[0][0], pts[0][1]);
            for (var i = 1; i < pts.length; i++) ctx.lineTo(pts[i][0], pts[i][1]);
            ctx.closePath();
        };
        var g = ctx.createLinearGradient(0, 0, 0, h);
        g.addColorStop(0, COLOR.panelTop);
        g.addColorStop(1, COLOR.panelBottom);
        ctx.fillStyle = g;
        path();
        ctx.fill();
        ctx.lineWidth = 1.5;
        ctx.strokeStyle = COLOR.frame;
        path();
        ctx.stroke();
        dirty(bmp);
    };

    // The dial: the whole day around a disc, midnight at the bottom; it turns
    // so that the time now sits under the pointer at the top.
    Sprite_NovaClockHud.prototype.drawDial = function() {
        var bmp = this._dial.bitmap, ctx = ctxOf(bmp), cx = bmp.width / 2, cy = bmp.height / 2, r = DIAL_R;
        for (var deg = 0; deg < 360; deg += 2) {
            var t = deg / 360 * 1440, a0 = (deg - 90) / 180 * Math.PI, a1 = (deg + 2.5 - 90) / 180 * Math.PI;
            ctx.beginPath();
            ctx.moveTo(cx, cy);
            ctx.arc(cx, cy, r, a0, a1);
            ctx.closePath();
            ctx.fillStyle = rgb(skyAt((t + 720) % 1440));
            ctx.fill();
        }
        // stars on the night half (around the bottom of the disc = midnight)
        ctx.fillStyle = 'rgba(255, 255, 240, 0.85)';
        [[-0.55, 0.45], [-0.2, 0.7], [0.15, 0.5], [0.45, 0.62], [0.05, 0.82], [-0.4, 0.2], [0.6, 0.3]].forEach(function(s) {
            ctx.fillRect(cx + s[0] * r, cy + s[1] * r, 1.5, 1.5);
        });
        // the sun at noon (top), the moon at midnight (bottom)
        var g = ctx.createRadialGradient(cx, cy - r * 0.55, 1, cx, cy - r * 0.55, r * 0.34);
        g.addColorStop(0, '#fff8d0');
        g.addColorStop(0.6, '#ffd860');
        g.addColorStop(1, 'rgba(255, 200, 80, 0)');
        ctx.fillStyle = g;
        ctx.beginPath();
        ctx.arc(cx, cy - r * 0.55, r * 0.34, 0, Math.PI * 2);
        ctx.fill();
        ctx.fillStyle = '#eef0ff';
        ctx.beginPath();
        ctx.arc(cx, cy + r * 0.55, r * 0.2, 0, Math.PI * 2);
        ctx.fill();
        ctx.fillStyle = rgb(skyAt(0));
        ctx.beginPath();
        ctx.arc(cx + r * 0.09, cy + r * 0.5, r * 0.17, 0, Math.PI * 2);
        ctx.fill();
        dirty(bmp);
    };

    // Rim and the fixed pointer over the dial.
    Sprite_NovaClockHud.prototype.drawRing = function() {
        var bmp = this._ring.bitmap, ctx = ctxOf(bmp), cx = bmp.width / 2, cy = DIAL_R + 9;
        ctx.lineWidth = 2;
        ctx.strokeStyle = COLOR.frame;
        ctx.beginPath();
        ctx.arc(cx, cy, DIAL_R + 1, 0, Math.PI * 2);
        ctx.stroke();
        ctx.lineWidth = 1;
        ctx.strokeStyle = 'rgba(6, 10, 20, 0.8)';
        ctx.beginPath();
        ctx.arc(cx, cy, DIAL_R - 0.5, 0, Math.PI * 2);
        ctx.stroke();
        ctx.beginPath();
        ctx.moveTo(cx - 6, 1);
        ctx.lineTo(cx + 6, 1);
        ctx.lineTo(cx, 11);
        ctx.closePath();
        ctx.fillStyle = COLOR.pending;
        ctx.fill();
        ctx.strokeStyle = 'rgba(6, 10, 20, 0.9)';
        ctx.stroke();
        dirty(bmp);
    };

    Sprite_NovaClockHud.prototype.drawText = function() {
        var bmp = this._text.bitmap;
        bmp.clear();
        bmp.outlineColor = 'rgba(6, 10, 20, 0.85)';
        bmp.outlineWidth = 3;
        if (UI) UI.titleFont(bmp, 26);
        bmp.textColor = COLOR.text;
        bmp.drawText(NovaDayNight.timeText(), 0, 8, bmp.width - 8, 34, 'left');
        if (UI) UI.titleFont(bmp, 14);
        else bmp.fontSize = 14;
        bmp.textColor = NovaDayNight.isNight() ? COLOR.accent : COLOR.pending;
        bmp.drawText(NovaDayNight.phase(), 0, 42, bmp.width - 8, 24, 'left');
        bmp.textColor = COLOR.dim;
        bmp.drawText('Day ' + NovaDayNight.day(), 0, 42, bmp.width - 10, 24, 'right');
        if (UI) UI.bodyFont(bmp);
    };

    Sprite_NovaClockHud.prototype.update = function() {
        Sprite.prototype.update.call(this);
        var c = clock();
        var shown = SHOW_HUD && !c.hudHidden && !(STOP_SWITCH > 0 && $gameSwitches.value(STOP_SWITCH));
        var target = !shown || $gameMessage.isBusy() ? 0 : 235;
        if (shown && target) {
            var px = $gamePlayer.screenX(), py = $gamePlayer.screenY();
            if (px < this.x + HUD_W + 24 && py > this.y - 8) target = 80;   // walking under it
        }
        this.opacity += Math.max(-20, Math.min(20, target - this.opacity));
        this._dial.rotation = -(NovaDayNight.minutes() - 720) / 1440 * Math.PI * 2;   // noon is drawn at the top
        var key = NovaDayNight.timeText() + '|' + NovaDayNight.day();
        if (key !== this._key) {
            this._key = key;
            this.drawText();
        }
    };

    var _createAllWindows = Scene_Map.prototype.createAllWindows;
    Scene_Map.prototype.createAllWindows = function() {
        this._novaClockHud = new Sprite_NovaClockHud();
        this.addChildAt(this._novaClockHud, this.children.indexOf(this._windowLayer));
        _createAllWindows.call(this);
    };

    //=========================================================================
    // Plugin commands
    //=========================================================================
    var _pluginCommand = Game_Interpreter.prototype.pluginCommand;
    Game_Interpreter.prototype.pluginCommand = function(command, args) {
        _pluginCommand.call(this, command, args);
        if (command.toLowerCase() !== 'clock') return;
        var sub = String(args[0] || '').toLowerCase(), arg = args.slice(1).join(' ');
        if (sub === 'set') NovaDayNight.set(parseTime(arg, NovaDayNight.minutes()), false);
        else if (sub === 'sleep') NovaDayNight.set(parseTime(arg, 420), true);
        else if (sub === 'add') NovaDayNight.add(Number(args[1] || 0) * 60);
        else if (sub === 'stop') clock().stopped = true;
        else if (sub === 'start') clock().stopped = false;
        else if (sub === 'hud') clock().hudHidden = String(args[1] || '').toLowerCase() === 'hide';
    };

    window.NovaDayNight = NovaDayNight;
    window.Sprite_NovaClockHud = Sprite_NovaClockHud;
})();
