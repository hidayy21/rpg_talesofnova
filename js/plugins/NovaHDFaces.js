//=============================================================================
// NovaHDFaces.js
//=============================================================================
/*:
 * @plugindesc Draws faces from a high-resolution copy of a face sheet
 * (e.g. Actor4_HD.png) for sharper faces everywhere.
 * @author Project Nova
 *
 * @param HD Sheets
 * @desc Face sheets that have an HD copy, comma separated (e.g. Actor4, People1).
 * @default Actor4
 *
 * @param HD Suffix
 * @desc The HD copy is img/faces/<sheet><suffix>.png
 * @default _HD
 *
 * @help
 * Keep using the normal face sheet in the database (e.g. Actor4). For each
 * sheet listed in "HD Sheets", put a larger copy with the same 4x2 layout in
 * img/faces named <sheet>_HD.png (any size, e.g. 2912x1440). Whenever the game
 * draws a face from that sheet - messages, menu, status - it is taken from the
 * HD copy and reduced with high-quality smoothing. Until the HD copy has
 * loaded, the normal sheet is used.
 */

(function() {
    'use strict';

    var params = PluginManager.parameters('NovaHDFaces');
    var SUFFIX = String(params['HD Suffix'] || '_HD');
    var SHEETS = String(params['HD Sheets'] || 'Actor4').split(',')
        .map(function(s) { return s.trim(); }).filter(Boolean);

    // Only use an HD copy that really exists, so a stale plugin entry can never break face loading.
    var exists = {};
    function hdFileExists(faceName) {
        if (!(faceName in exists)) {
            exists[faceName] = false;
            try {
                if (typeof require === 'function') {
                    var path = require('path');
                    var base = path.dirname(process.mainModule.filename);
                    exists[faceName] = require('fs').existsSync(path.join(base, 'img/faces', faceName + SUFFIX + '.png'));
                }
            } catch (e) { exists[faceName] = false; }
        }
        return exists[faceName];
    }
    function hasHd(faceName) { return SHEETS.indexOf(faceName) >= 0 && hdFileExists(faceName); }

    // Load the HD copy whenever the normal sheet is requested, so it is ready in time.
    var _loadFace = ImageManager.loadFace;
    ImageManager.loadFace = function(filename, hue) {
        if (hasHd(filename)) _loadFace.call(this, filename + SUFFIX, hue);
        return _loadFace.apply(this, arguments);
    };
    if (ImageManager.reserveFace) {
        var _reserveFace = ImageManager.reserveFace;
        ImageManager.reserveFace = function(filename, hue, reservationId) {
            if (hasHd(filename)) _reserveFace.call(this, filename + SUFFIX, hue, reservationId);
            return _reserveFace.apply(this, arguments);
        };
    }

    var _drawFace = Window_Base.prototype.drawFace;
    Window_Base.prototype.drawFace = function(faceName, faceIndex, x, y, width, height) {
        if (!hasHd(faceName)) return _drawFace.apply(this, arguments);
        var hd = ImageManager.loadFace(faceName + SUFFIX);
        if (!hd.isReady() || !hd.width) return _drawFace.apply(this, arguments);

        // Same geometry as the default drawFace, mapped onto the HD cell.
        width = width || Window_Base._faceWidth;
        height = height || Window_Base._faceHeight;
        var pw = Window_Base._faceWidth, ph = Window_Base._faceHeight;
        var sw = Math.min(width, pw), sh = Math.min(height, ph);
        var dx = Math.floor(x + Math.max(width - pw, 0) / 2);
        var dy = Math.floor(y + Math.max(height - ph, 0) / 2);
        var cw = hd.width / 4, ch = hd.height / 2;
        var kx = cw / pw, ky = ch / ph;
        var sx = faceIndex % 4 * cw + (pw - sw) / 2 * kx;
        var sy = Math.floor(faceIndex / 4) * ch + (ph - sh) / 2 * ky;

        var ctx = this.contents._context || this.contents.context;
        ctx.save();
        ctx.imageSmoothingEnabled = true;
        if ('imageSmoothingQuality' in ctx) ctx.imageSmoothingQuality = 'high';
        ctx.globalAlpha = this.contents.paintOpacity / 255;
        ctx.drawImage(hd._canvas || hd._image, sx, sy, sw * kx, sh * ky, dx, dy, sw, sh);
        ctx.restore();
        if (this.contents._setDirty) this.contents._setDirty();
    };
})();
