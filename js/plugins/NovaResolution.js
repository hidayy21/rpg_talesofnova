//=============================================================================
// NovaResolution.js
//=============================================================================
/*:
 * @plugindesc Keeps the default 816x624 assets looking right at a larger
 * screen size (title, battlebacks, battle positions).
 * @author Project Nova
 *
 * @param Design Width
 * @type number
 * @desc Screen width the troops/battlers were laid out for (RPG Maker MV default 816).
 * @default 816
 *
 * @param Design Height
 * @type number
 * @desc Screen height the troops/battlers were laid out for (RPG Maker MV default 624).
 * @default 624
 *
 * @help
 * Set the real screen size in Community_Basic (e.g. 1280x720), then:
 *  - Title images are scaled to cover the whole screen (kept centred).
 *  - Battlebacks are scaled to cover the screen instead of tiling,
 *    aligned to the bottom in side-view battles.
 *  - Enemies keep the layout from the Troops editor at the same distance
 *    from the bottom of the screen. Horizontally they are centred in
 *    front view; in side view they keep their distance from the left edge.
 *  - Side-view party members keep their place on the right-hand side.
 * Has no effect when the screen is 816x624.
 */

(function() {
    'use strict';

    var params = PluginManager.parameters('NovaResolution');
    var BASE_W = Number(params['Design Width'] || 816);
    var BASE_H = Number(params['Design Height'] || 624);

    function offsetX() { return (Graphics.boxWidth - BASE_W) / 2; }
    function offsetBottom() { return Graphics.boxHeight - BASE_H; }

    function coverScreen(sprite, alignBottom) {
        var bmp = sprite.bitmap;
        if (!bmp || !bmp.width) return;
        var scale = Math.max(Graphics.width / bmp.width, Graphics.height / bmp.height, 1);
        sprite.scale.x = sprite.scale.y = scale;
        sprite.anchor.x = 0.5;
        sprite.anchor.y = alignBottom ? 1 : 0.5;
        sprite.x = Graphics.width / 2;
        sprite.y = alignBottom ? Graphics.height : Graphics.height / 2;
    }

    // ---------------------------------------------------------------- title
    var _Scene_Title_createBackground = Scene_Title.prototype.createBackground;
    Scene_Title.prototype.createBackground = function() {
        _Scene_Title_createBackground.call(this);
        [this._backSprite1, this._backSprite2].forEach(function(sprite) {
            if (sprite && sprite.bitmap) sprite.bitmap.addLoadListener(function() { coverScreen(sprite, false); });
        });
    };

    // ---------------------------------------------------------------- battlebacks
    Spriteset_Battle.prototype.createBattleback = function() {
        this._back1Sprite = new Sprite(this.battleback1Bitmap());
        this._back2Sprite = new Sprite(this.battleback2Bitmap());
        this._battleField.addChild(this._back1Sprite);
        this._battleField.addChild(this._back2Sprite);
    };

    Spriteset_Battle.prototype.updateBattleback = function() {
        if (this._battlebackLocated) return;
        var b1 = this._back1Sprite.bitmap, b2 = this._back2Sprite.bitmap;
        if ((b1 && !b1.isReady()) || (b2 && !b2.isReady())) return;
        this.locateBattleback();
        this._battlebackLocated = true;
    };

    Spriteset_Battle.prototype.locateBattleback = function() {
        var sideView = $gameSystem.isSideView();
        var fx = this._battleField.x, fy = this._battleField.y;
        [this._back1Sprite, this._back2Sprite].forEach(function(sprite) {
            coverScreen(sprite, sideView);
            sprite.x -= fx;
            sprite.y -= fy;
        });
    };

    // ---------------------------------------------------------------- battle positions
    // Side view: enemies keep their distance from the left edge, as the party does from
    // the right one, so the wider screen opens up the gap between the two sides.
    var _Game_Enemy_screenX = Game_Enemy.prototype.screenX;
    Game_Enemy.prototype.screenX = function() {
        return _Game_Enemy_screenX.call(this) + ($gameSystem.isSideView() ? 0 : offsetX());
    };
    var _Game_Enemy_screenY = Game_Enemy.prototype.screenY;
    Game_Enemy.prototype.screenY = function() {
        return _Game_Enemy_screenY.call(this) + offsetBottom();
    };

    var _Sprite_Actor_setActorHome = Sprite_Actor.prototype.setActorHome;
    Sprite_Actor.prototype.setActorHome = function(index) {
        _Sprite_Actor_setActorHome.call(this, index);
        this.setHome(this._homeX + (Graphics.boxWidth - BASE_W), this._homeY + offsetBottom());
    };
})();
