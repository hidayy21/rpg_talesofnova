//=============================================================================
// NovaChapterCard.js
//=============================================================================
/*:
 * @plugindesc Chapter title cards: an animated title in the middle of the
 * screen on black ("Prologue Ends", "Chapter 1 / The Adventure Begins").
 * @author Project Nova
 *
 * @param Duration
 * @type number
 * @desc How long a card stays on screen, in frames (60 = 1 second), fades included.
 * @default 300
 *
 * @param Head Color
 * @desc Colour of the small line above the title (#rrggbb).
 * @default #e8cf8a
 *
 * @help
 * Plugin command:
 *
 *   ChapterCard Chapter 1 | The Adventure Begins
 *   ChapterCard | Prologue Ends
 *
 * Left of "|" is the small line above (may be empty), right of it the big
 * title. The card covers the map with black, the title fades in while its
 * letters draw together and a thin rule grows under it, then everything
 * fades out again. The event waits until the card is gone.
 *
 * The card fades back to black, not to the map: fade the screen out before
 * the card (Fadeout Screen) and in again after it.
 */

(function() {
    'use strict';

    var params = PluginManager.parameters('NovaChapterCard');
    var DURATION = Number(params['Duration'] || 300);
    var HEAD_COLOR = params['Head Color'] || '#e8cf8a';

    var current = null;          // { head, title, frame } while a card is showing

    function ease(t) { t = Math.max(0, Math.min(1, t)); return t * t * (3 - 2 * t); }

    //=========================================================================
    // Sprite
    //=========================================================================
    function Sprite_NovaChapterCard() {
        this.initialize.apply(this, arguments);
    }

    Sprite_NovaChapterCard.prototype = Object.create(Sprite.prototype);
    Sprite_NovaChapterCard.prototype.constructor = Sprite_NovaChapterCard;

    Sprite_NovaChapterCard.prototype.initialize = function() {
        Sprite.prototype.initialize.call(this);
        this.bitmap = new Bitmap(Graphics.width, Graphics.height);
        this.visible = false;
    };

    Sprite_NovaChapterCard.prototype.update = function() {
        Sprite.prototype.update.call(this);
        if (!current) { this.visible = false; return; }
        current.frame++;
        if (current.frame >= DURATION) { current = null; this.visible = false; return; }
        this.visible = true;
        this.redraw(current.frame);
    };

    // spaced letters, centred on cx
    Sprite_NovaChapterCard.prototype.drawSpaced = function(text, cx, y, h, spacing) {
        var b = this.bitmap;
        var widths = text.split('').map(function(ch) { return b.measureTextWidth(ch); });
        var total = widths.reduce(function(a, w) { return a + w; }, 0) + spacing * (text.length - 1);
        var x = cx - total / 2;
        for (var i = 0; i < text.length; i++) {
            b.drawText(text[i], x, y, widths[i] + 4, h, 'left');
            x += widths[i] + spacing;
        }
        return total;
    };

    Sprite_NovaChapterCard.prototype.redraw = function(f) {
        var b = this.bitmap, W = b.width, H = b.height, cx = W / 2, cy = H / 2;
        var fadeOut = 1 - ease((f - (DURATION - 50)) / 50);
        b.clear();
        b.fillRect(0, 0, W, H, '#000000');
        b.fontFace = 'GameFont';
        b.outlineWidth = 0;

        // the thin rule grows from the middle
        var rule = ease((f - 10) / 50) * Math.min(W * 0.42, 460);
        b.paintOpacity = Math.round(200 * fadeOut);
        b.fillRect(cx - rule / 2, cy + 34, rule, 2, HEAD_COLOR);

        // small line above
        if (current.head) {
            b.fontSize = 26;
            b.textColor = HEAD_COLOR;
            b.paintOpacity = Math.round(255 * ease((f - 20) / 40) * fadeOut);
            this.drawSpaced(current.head.toUpperCase(), cx, cy - 64, 32, 6);
        }

        // the title: fades in while its letters draw together
        var t = ease((f - 35) / 70);
        b.fontSize = 56;
        b.textColor = '#ffffff';
        b.paintOpacity = Math.round(255 * t * fadeOut);
        this.drawSpaced(current.title, cx, cy - 32, 64, 2 + 18 * (1 - t));
        b.paintOpacity = 255;
    };

    //=========================================================================
    // Scenes and events
    //=========================================================================
    var _Scene_Map_createDisplayObjects = Scene_Map.prototype.createDisplayObjects;
    Scene_Map.prototype.createDisplayObjects = function() {
        _Scene_Map_createDisplayObjects.call(this);
        this._novaChapterCard = new Sprite_NovaChapterCard();
        this.addChild(this._novaChapterCard);          // above the map, its screen fade and the windows
    };

    var _pluginCommand = Game_Interpreter.prototype.pluginCommand;
    Game_Interpreter.prototype.pluginCommand = function(command, args) {
        _pluginCommand.call(this, command, args);
        if (command !== 'ChapterCard') return;
        var parts = args.join(' ').split('|');
        var head = parts.length > 1 ? parts[0].trim() : '';
        var title = (parts.length > 1 ? parts.slice(1).join('|') : parts[0]).trim();
        current = { head: head, title: title, frame: 0 };
        this.setWaitMode('novaChapterCard');
    };

    var _updateWaitMode = Game_Interpreter.prototype.updateWaitMode;
    Game_Interpreter.prototype.updateWaitMode = function() {
        if (this._waitMode === 'novaChapterCard') {
            if (current) return true;
            this._waitMode = '';
            return false;
        }
        return _updateWaitMode.call(this);
    };
})();
