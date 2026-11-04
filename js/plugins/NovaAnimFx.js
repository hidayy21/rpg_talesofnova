//=============================================================================
// NovaAnimFx.js
//=============================================================================
/*:
 * @plugindesc Battle animations from the animation DLCs: per-animation frame
 * rate, full-screen fit, crisp pixel sheets and a cast circle under the caster.
 * @author Project Nova
 *
 * @param Design Width
 * @type number
 * @desc Screen width full-screen animations were drawn for (RPG Maker MV default 816).
 * @default 816
 *
 * @param Design Height
 * @type number
 * @desc Screen height full-screen animations were drawn for (RPG Maker MV default 624).
 * @default 624
 *
 * @param Pixel Sheet Prefix
 * @desc Animation sheets whose file name starts with this are drawn without
 * smoothing, so pixel art stays sharp when scaled. Empty = off.
 * @default Px_
 *
 * @param Cast Overlap
 * @type number
 * @desc Frames before the end of the cast circle at which the skill's own
 * animation starts (the two overlap a little).
 * @default 10
 *
 * @help
 * Tags in the animation's NAME (Database > Animations), in square brackets:
 *   [30fps]   plays the animation at 30 frames per second (also 20fps,
 *             60fps...). RPG Maker MV plays at 15. The Thaumaturgy sheets
 *             come in 30 and 60 FPS versions; without the tag they play in
 *             slow motion.
 *   [fit]     a Screen animation is scaled to cover the real screen, for
 *             full-screen effects drawn at 816x624.
 *   e.g.  "Thaum: Inferno [30fps fit]"
 * Flash and sound timings stay on their frames, so they follow the new speed.
 *
 * Skill or item note:
 *   <cast animation: 152>   plays animation 152 on the user first (a magic
 *                           circle), then the skill's animation on the targets
 *   <cast wait: 20>         frames to wait before the skill's animation
 *                           (default: the cast's length minus Cast Overlap)
 *
 * Plugin commands: none.
 */

(function() {
    'use strict';

    var params = PluginManager.parameters('NovaAnimFx');
    var BASE_W = Number(params['Design Width'] || 816);
    var BASE_H = Number(params['Design Height'] || 624);
    var PIXEL_PREFIX = String(params['Pixel Sheet Prefix'] || '');
    var CAST_OVERLAP = Number(params['Cast Overlap'] || 10);

    // ---------------------------------------------------------------- name tags
    function tags(animation) {
        if (!animation._novaFx) {
            var fx = { rate: 0, fit: false };
            var m, re = /\[([^\]]*)\]/g;
            while ((m = re.exec(animation.name || ''))) {
                m[1].split(/[\s,]+/).forEach(function(word) {
                    var fps = /^(\d+)fps$/i.exec(word);
                    if (fps) fx.rate = Math.max(1, Math.round(60 / Number(fps[1])));
                    if (/^fit$/i.test(word)) fx.fit = true;
                });
            }
            animation._novaFx = fx;
        }
        return animation._novaFx;
    }

    function animationRate(animation) {
        return tags(animation).rate || 4;
    }

    // ---------------------------------------------------------------- frame rate and fit
    var _setupRate = Sprite_Animation.prototype.setupRate;
    Sprite_Animation.prototype.setupRate = function() {
        _setupRate.call(this);
        if (tags(this._animation).rate) this._rate = tags(this._animation).rate;
    };

    var _updatePosition = Sprite_Animation.prototype.updatePosition;
    Sprite_Animation.prototype.updatePosition = function() {
        _updatePosition.call(this);
        if (this._animation.position === 3 && tags(this._animation).fit && this.parent) {
            var w = this.parent.width || Graphics.boxWidth, h = this.parent.height || Graphics.boxHeight;
            this.scale.x = this.scale.y = Math.max(w / BASE_W, h / BASE_H, 1);
        }
    };

    // ---------------------------------------------------------------- crisp pixel sheets
    var _loadBitmaps = Sprite_Animation.prototype.loadBitmaps;
    Sprite_Animation.prototype.loadBitmaps = function() {
        _loadBitmaps.call(this);
        if (!PIXEL_PREFIX) return;
        var a = this._animation;
        if (a.animation1Name.indexOf(PIXEL_PREFIX) === 0) this._bitmap1.smooth = false;
        if (a.animation2Name.indexOf(PIXEL_PREFIX) === 0) this._bitmap2.smooth = false;
    };

    // ---------------------------------------------------------------- cast circle
    function castAnimationId(item) {
        var tag = item && item.meta && item.meta['cast animation'];
        return tag ? Number(tag) : 0;
    }

    function castWait(item, animation) {
        var tag = item.meta['cast wait'];
        if (tag !== undefined) return Number(tag);
        return Math.max(0, animation.frames.length * animationRate(animation) - CAST_OVERLAP);
    }

    // The cast plays on the user, then showAnimation runs again (front of the queue) once the wait is over.
    var _showAnimation = Window_BattleLog.prototype.showAnimation;
    Window_BattleLog.prototype.showAnimation = function(subject, targets, animationId) {
        var action = BattleManager._action;
        var item = action && action.subject() === subject ? action.item() : null;
        var castId = castAnimationId(item);
        var cast = castId && $dataAnimations[castId];
        if (cast && !this._novaCastDone) {
            this._novaCastDone = true;
            subject.startAnimation(castId, false, 0);
            this._methods.unshift({ name: 'showAnimation', params: [subject, targets, animationId] });
            this._waitCount = castWait(item, cast);
            return;
        }
        this._novaCastDone = false;
        _showAnimation.call(this, subject, targets, animationId);
    };
})();
