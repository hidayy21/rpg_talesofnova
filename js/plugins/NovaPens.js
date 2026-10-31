//=============================================================================
// NovaPens.js
//=============================================================================
/*:
 * @plugindesc Pens: animals and other events that wander on their own stay
 * inside an area, even when the fence has a gate left open.
 * @author Project Nova
 *
 * @help
 * Event note tag (or a Comment on the active page):
 *
 *   <pen: 1,26,11,29>   the event never steps outside the rectangle from
 *                       x 1, y 26 to x 11, y 29 (both corners included)
 *
 * Works for every kind of movement the event does by itself: Random,
 * Approach, Custom routes and Set Movement Route. An event with Through on
 * ignores its pen, so cutscenes can still walk it anywhere.
 *
 * Used for the horse paddock and the chicken run on Hollow Farm.
 */

(function() {
    'use strict';

    function parsePen(text) {
        var m = /<pen:\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*>/i.exec(text || '');
        if (!m) return null;
        var x1 = Number(m[1]), y1 = Number(m[2]), x2 = Number(m[3]), y2 = Number(m[4]);
        return [Math.min(x1, x2), Math.min(y1, y2), Math.max(x1, x2), Math.max(y1, y2)];
    }

    Game_Event.prototype.pen = function() {
        if (this._penPageIndex !== this._pageIndex) {
            var page = this.page();
            this._penPageIndex = this._pageIndex;
            this._pen = parsePen(this.event().note);
            if (!this._pen && page) {
                var comments = page.list.filter(function(c) { return c.code === 108 || c.code === 408; });
                this._pen = parsePen(comments.map(function(c) { return c.parameters[0]; }).join('\n'));
            }
        }
        return this._pen;
    };

    var _canPass = Game_Event.prototype.canPass;
    Game_Event.prototype.canPass = function(x, y, d) {
        if (!_canPass.call(this, x, y, d)) return false;
        var pen = this.pen();
        if (!pen || this.isThrough()) return true;
        var x2 = $gameMap.roundXWithDirection(x, d);
        var y2 = $gameMap.roundYWithDirection(y, d);
        return x2 >= pen[0] && x2 <= pen[2] && y2 >= pen[1] && y2 <= pen[3];
    };
})();
