//=============================================================================
// NovaMenu.js
//=============================================================================
/*:
 * @plugindesc Final Fantasy-style main menu: command list on the left and tall
 * portrait cards for the party on the right. Medieval blue look (Cinzel titles).
 * @author Project Nova
 *
 * @param Portrait Prefix
 * @desc Portrait file in img/pictures is <prefix><Actor Name>.png unless the actor note says otherwise.
 * @default Portrait_
 *
 * @param Visible Cards
 * @type number
 * @min 1
 * @desc How many party cards are shown side by side (more members scroll by page).
 * @default 4
 *
 * @param Title Text
 * @desc Heading shown at the top-left of the menu.
 * @default MAIN MENU
 *
 * @param Gold Icon
 * @type number
 * @desc Icon index shown next to the gold amount.
 * @default 208
 *
 * @help
 * Portraits
 *   Put a portrait (any size, about 3:4) in img/pictures named
 *   Portrait_<Actor Name>.png, e.g. Portrait_Kael.png.
 *   To use a different file, write in the actor's note:  <portrait:FileName>
 *   Without a portrait the card falls back to the actor's face graphic.
 *
 * The bottom of each card shows the actor's side-view battler, animated.
 * Commands are the standard menu commands, so other plugins that add
 * commands keep working.
 */

(function() {
    'use strict';

    var params = PluginManager.parameters('NovaMenu');
    var PREFIX = String(params['Portrait Prefix'] || 'Portrait_');
    var VISIBLE = Math.max(1, Number(params['Visible Cards'] || 4));
    var TITLE = String(params['Title Text'] || 'MAIN MENU');
    var GOLD_ICON = Number(params['Gold Icon'] || 208);

    // Medieval blue: night-blue panels, steel-blue and silver trim, Cinzel titles.
    var COLOR = {
        accent: '#9cc0ec',                      // steel blue: trim, highlights
        accentLit: '#d8e8fb',                   // silver: whatever is selected
        accentSoft: 'rgba(156, 192, 236, 0.35)',
        frame: '#6f93c9',
        frameSoft: 'rgba(185, 212, 245, 0.22)',
        panelTop: 'rgba(26, 36, 64, 0.94)',
        panelBottom: 'rgba(12, 18, 34, 0.96)',
        ink: '#0b1120',
        barBack: '#060a14',
        banner: ['#24447e', '#16294f'],
        pending: '#e8cf8f',
        text: '#eaf0f8',
        dim: '#9fb1c9',
        hp: ['#8fc27f', '#3f7a3a'],
        mp: ['#8fb0e0', '#34548f'],
        exp: ['#e8cf8f', '#a7802f']
    };
    var TITLE_FONT = 'NovaTitle';   // Cinzel, see fonts/gamefont.css; body text is GameFont (Alegreya Sans)
    var HEADER_H = 64;
    var FOOTER_H = 48;

    //=========================================================================
    // Fonts
    //=========================================================================
    // MV's font string has no weight; Cinzel is a variable font, so 'bold' picks its bold.
    var _makeFontNameText = Bitmap.prototype._makeFontNameText;
    Bitmap.prototype._makeFontNameText = function() {
        return (this.fontBold ? 'bold ' : '') + _makeFontNameText.call(this);
    };

    function titleFont(bitmap, size, bold) {
        bitmap.fontFace = TITLE_FONT;
        bitmap.fontSize = size;
        bitmap.fontBold = bold !== false;
    }

    function bodyFont(bitmap, size) {
        bitmap.fontFace = 'GameFont';
        bitmap.fontBold = false;
        if (size) bitmap.fontSize = size;
    }

    var _Window_Base_resetFontSettings = Window_Base.prototype.resetFontSettings;
    Window_Base.prototype.resetFontSettings = function() {
        _Window_Base_resetFontSettings.call(this);
        this.contents.fontBold = false;
        this.contents.fontItalic = false;
    };

    Window_Base.prototype.normalColor = function() { return COLOR.text; };
    Window_Base.prototype.systemColor = function() { return COLOR.accent; };
    Window_Base.prototype.hpGaugeColor1 = function() { return COLOR.hp[1]; };
    Window_Base.prototype.hpGaugeColor2 = function() { return COLOR.hp[0]; };
    Window_Base.prototype.mpGaugeColor1 = function() { return COLOR.mp[1]; };
    Window_Base.prototype.mpGaugeColor2 = function() { return COLOR.mp[0]; };
    Window_Base.prototype.gaugeBackColor = function() { return COLOR.barBack; };

    // Wait for the title font too (at most a few seconds, then fall back).
    var _Scene_Boot_isGameFontLoaded = Scene_Boot.prototype.isGameFontLoaded;
    Scene_Boot.prototype.isGameFontLoaded = function() {
        if (!this._novaFontRequested) {
            this._novaFontRequested = true;
            Graphics._createFontLoader(TITLE_FONT);
        }
        return _Scene_Boot_isGameFontLoaded.call(this) &&
               (Graphics.isFontLoaded(TITLE_FONT) || Date.now() - this._startDate > 5000);
    };

    function portraitName(actor) {
        var meta = actor.actor().meta.portrait;
        return meta ? String(meta).trim() : PREFIX + actor.name();
    }

    function ctxOf(bitmap) { return bitmap._context || bitmap.context; }
    function dirty(bitmap) {
        if (bitmap._setDirty) bitmap._setDirty();
        else if (bitmap._baseTexture) bitmap._baseTexture.update();
    }

    // Bevelled shapes drawn straight on the canvas.
    function pathPoly(ctx, pts) {
        ctx.beginPath();
        ctx.moveTo(pts[0][0], pts[0][1]);
        for (var i = 1; i < pts.length; i++) ctx.lineTo(pts[i][0], pts[i][1]);
        ctx.closePath();
    }

    // The small diamond used as an ornament and as the selection marker.
    function diamond(ctx, cx, cy, r, color) {
        pathPoly(ctx, [[cx, cy - r], [cx + r, cy], [cx, cy + r], [cx - r, cy]]);
        ctx.fillStyle = color;
        ctx.fill();
    }

    // A straight gauge with a thin steel-blue rim.
    function drawBar(ctx, x, y, w, h, rate, colors) {
        ctx.fillStyle = COLOR.barBack;
        ctx.fillRect(x, y, w, h);
        var fw = Math.max(0, Math.min(1, rate)) * (w - 2);
        if (fw > 0) {
            var g = ctx.createLinearGradient(x, 0, x + fw, 0);
            g.addColorStop(0, colors[1]);
            g.addColorStop(1, colors[0]);
            ctx.fillStyle = g;
            ctx.fillRect(x + 1, y + 1, fw, h - 2);
        }
        ctx.strokeStyle = 'rgba(156, 192, 236, 0.45)';
        ctx.lineWidth = 1;
        ctx.strokeRect(x + 0.5, y + 0.5, w - 1, h - 1);
    }

    // Header band shared by the menu screens: title in Cinzel over a blue band.
    function drawHeader(bmp, title) {
        var w = bmp.width, ctx = ctxOf(bmp), ly = HEADER_H - 8, lw = w * 0.42;
        var g = ctx.createLinearGradient(0, 0, w, 0);
        g.addColorStop(0, 'rgba(36, 68, 126, 0.55)');
        g.addColorStop(0.5, 'rgba(36, 68, 126, 0.12)');
        g.addColorStop(1, 'rgba(36, 68, 126, 0)');
        ctx.fillStyle = g;
        ctx.fillRect(0, 0, w, HEADER_H);
        var line = ctx.createLinearGradient(16, 0, 16 + lw, 0);
        line.addColorStop(0, COLOR.accent);
        line.addColorStop(1, 'rgba(156, 192, 236, 0)');
        ctx.fillStyle = line;
        ctx.fillRect(16, ly, lw, 1);
        diamond(ctx, 16, ly + 0.5, 4, COLOR.accent);
        dirty(bmp);
        titleFont(bmp, 30);
        bmp.textColor = COLOR.text;
        bmp.outlineColor = 'rgba(6, 10, 20, 0.85)';
        bmp.outlineWidth = 4;
        bmp.drawText(title, 28, 10, w * 0.6, 44, 'left');
        bodyFont(bmp);
    }

    //=========================================================================
    // Scene_Menu
    //=========================================================================
    var _Scene_Menu_create = Scene_Menu.prototype.create;
    Scene_Menu.prototype.create = function() {
        _Scene_Menu_create.call(this);
        this.createNovaBackdrop();
        this.createNovaHeader();
        this.createNovaFooter();
        $gameParty.members().forEach(function(actor) {
            if (pictureExists(portraitName(actor))) ImageManager.loadPicture(portraitName(actor));
            ImageManager.loadSvActor(actor.battlerName());
            ImageManager.loadFace(actor.faceName());
        });
    };

    Scene_Menu.prototype.createGoldWindow = function() {
        // Gold lives in the header and footer instead.
        this._goldWindow = new Window_Gold(0, 0);
        this._goldWindow.visible = false;
    };

    Scene_Menu.prototype.createCommandWindow = function() {
        this._commandWindow = new Window_NovaMenuCommand(16, HEADER_H + 16);
        this._commandWindow.setHandler('item', this.commandItem.bind(this));
        this._commandWindow.setHandler('skill', this.commandPersonal.bind(this));
        this._commandWindow.setHandler('equip', this.commandPersonal.bind(this));
        this._commandWindow.setHandler('status', this.commandPersonal.bind(this));
        this._commandWindow.setHandler('formation', this.commandFormation.bind(this));
        this._commandWindow.setHandler('options', this.commandOptions.bind(this));
        this._commandWindow.setHandler('save', this.commandSave.bind(this));
        this._commandWindow.setHandler('gameEnd', this.commandGameEnd.bind(this));
        this._commandWindow.setHandler('cancel', this.popScene.bind(this));
        this.addWindow(this._commandWindow);
    };

    Scene_Menu.prototype.createStatusWindow = function() {
        var x = this._commandWindow.x + this._commandWindow.width + 8;
        this._statusWindow = new Window_NovaMenuStatus(x, HEADER_H);
        this._statusWindow.reserveFaceImages();
        this.addWindow(this._statusWindow);
    };

    Scene_Menu.prototype.createNovaBackdrop = function() {
        var bmp = new Bitmap(Graphics.boxWidth, Graphics.boxHeight);
        drawBackdrop(bmp);
        this._novaBackdrop = new Sprite(bmp);
        this.addChildAt(this._novaBackdrop, this.children.indexOf(this._windowLayer));
    };

    Scene_Menu.prototype.createNovaHeader = function() {
        var w = Graphics.boxWidth;
        var bmp = new Bitmap(w, HEADER_H);
        drawHeader(bmp, TITLE);
        this._novaHeader = new Sprite(bmp);
        this.addChild(this._novaHeader);

        this._novaGold = new Sprite(new Bitmap(260, HEADER_H));
        this._novaGold.x = w - 270;
        this.addChild(this._novaGold);
        this.refreshNovaGold();
    };

    Scene_Menu.prototype.refreshNovaGold = function() {
        var bmp = this._novaGold.bitmap;
        bmp.clear();
        var ctx = ctxOf(bmp);
        ctx.fillStyle = 'rgba(12, 18, 34, 0.85)';
        ctx.fillRect(18, 14, 236, 36);
        ctx.strokeStyle = COLOR.frame;
        ctx.lineWidth = 1;
        ctx.strokeRect(18.5, 14.5, 235, 35);
        diamond(ctx, 18.5, 32, 4, COLOR.accent);
        diamond(ctx, 253.5, 32, 4, COLOR.accent);
        dirty(bmp);
        var iconSet = ImageManager.loadSystem('IconSet');
        var iw = Window_Base._iconWidth, ih = Window_Base._iconHeight;
        bmp.blt(iconSet, GOLD_ICON % 16 * iw, Math.floor(GOLD_ICON / 16) * ih, iw, ih, 36, 16);
        titleFont(bmp, 21);   // Cinzel's figures: Alegreya's old-style 0 reads like an o
        bmp.textColor = COLOR.text;
        bmp.outlineColor = 'rgba(6, 10, 20, 0.8)';
        bmp.outlineWidth = 4;
        bmp.drawText($gameParty.gold() + ' ' + TextManager.currencyUnit, 70, 14, 166, 36, 'right');
    };

    Scene_Menu.prototype.createNovaFooter = function() {
        var w = Graphics.boxWidth;
        this._novaFooter = new Sprite(new Bitmap(w, FOOTER_H));
        this._novaFooter.y = Graphics.boxHeight - FOOTER_H;
        this.addChild(this._novaFooter);
        this._novaFooterSecond = -1;
        this.refreshNovaFooter();
    };

    Scene_Menu.prototype.refreshNovaFooter = function() {
        var bmp = this._novaFooter.bitmap, w = bmp.width;
        bmp.clear();
        var ctx = ctxOf(bmp);
        var g = ctx.createLinearGradient(0, 0, w, 0);
        g.addColorStop(0, 'rgba(0, 0, 0, 0.75)');
        g.addColorStop(1, 'rgba(0, 0, 0, 0.25)');
        ctx.fillStyle = g;
        ctx.fillRect(0, 8, w, FOOTER_H - 8);
        ctx.fillStyle = COLOR.accentSoft;
        ctx.fillRect(0, 8, w, 1);
        dirty(bmp);
        var where = $gameMap.displayName() || ($dataMapInfos[$gameMap.mapId()] || {}).name || '';
        bmp.outlineWidth = 3;
        titleFont(bmp, 15);
        bmp.textColor = COLOR.dim;
        bmp.drawText('TIME', 20, 12, 60, 32, 'left');
        bmp.drawText('LOCATION', w - 380, 12, 110, 32, 'left');
        bodyFont(bmp, 20);
        bmp.textColor = COLOR.text;
        bmp.drawText($gameSystem.playtimeText(), 74, 12, 120, 32, 'left');
        bmp.drawText(where, w - 270, 12, 256, 32, 'left');
    };

    var _Scene_Menu_update = Scene_Menu.prototype.update;
    Scene_Menu.prototype.update = function() {
        _Scene_Menu_update.call(this);
        var sec = $gameSystem.playtime();
        if (sec !== this._novaFooterSecond) {
            this._novaFooterSecond = sec;
            this.refreshNovaFooter();
        }
    };

    //=========================================================================
    // Window_NovaMenuCommand - straight rows, a diamond marks the selection
    //=========================================================================
    function Window_NovaMenuCommand() { this.initialize.apply(this, arguments); }
    Window_NovaMenuCommand.prototype = Object.create(Window_MenuCommand.prototype);
    Window_NovaMenuCommand.prototype.constructor = Window_NovaMenuCommand;

    Window_NovaMenuCommand.prototype.initialize = function(x, y) {
        Window_MenuCommand.prototype.initialize.call(this, x, y);
        this.opacity = 0;
        this._novaPulse = 0;
    };
    Window_NovaMenuCommand.prototype.windowWidth = function() {
        return Math.max(190, Math.min(240, Math.floor(Graphics.boxWidth * 0.24)));
    };
    Window_NovaMenuCommand.prototype.standardPadding = function() { return 8; };
    Window_NovaMenuCommand.prototype.itemHeight = function() { return 46; };
    // fittingHeight() assumes lineHeight-sized rows; these bars are taller.
    Window_NovaMenuCommand.prototype.windowHeight = function() {
        return this.numVisibleRows() * this.itemHeight() + this.standardPadding() * 2;
    };
    Window_NovaMenuCommand.prototype.numVisibleRows = function() {
        var room = Math.floor((Graphics.boxHeight - HEADER_H - FOOTER_H - 32) / this.itemHeight());
        return Math.min(this.maxItems(), room);
    };
    Window_NovaMenuCommand.prototype.updateCursor = function() { this.setCursorRect(0, 0, 0, 0); };
    Window_NovaMenuCommand.prototype.select = function(index) {
        Window_MenuCommand.prototype.select.call(this, index);
        if (this.contents) this.refresh();
    };
    Window_NovaMenuCommand.prototype.activate = function() {
        Window_MenuCommand.prototype.activate.call(this);
        if (this.contents) this.refresh();
    };
    Window_NovaMenuCommand.prototype.deactivate = function() {
        Window_MenuCommand.prototype.deactivate.call(this);
        if (this.contents) this.refresh();
    };

    Window_NovaMenuCommand.prototype.drawItem = function(index) {
        var rect = this.itemRect(index);
        var selected = index === this.index();
        var lit = selected && this.active;
        var ctx = ctxOf(this.contents);
        var x = rect.x + 6, y = rect.y + 5, w = rect.width - 10, h = rect.height - 10;
        if (selected) {
            var g = ctx.createLinearGradient(x, 0, x + w, 0);
            g.addColorStop(0, lit ? 'rgba(156, 192, 236, 0.36)' : 'rgba(156, 192, 236, 0.18)');
            g.addColorStop(1, 'rgba(156, 192, 236, 0)');
            ctx.fillStyle = g;
            ctx.fillRect(x, y, w, h);
            ctx.fillStyle = lit ? 'rgba(156, 192, 236, 0.75)' : 'rgba(156, 192, 236, 0.45)';
            ctx.fillRect(x, y + h - 1, w, 1);
            diamond(ctx, x + 13, y + h / 2, 5, lit ? COLOR.accentLit : COLOR.accent);
        } else {
            ctx.fillStyle = 'rgba(156, 192, 236, 0.16)';
            ctx.fillRect(x, y + h - 1, w, 1);
        }
        dirty(this.contents);

        titleFont(this.contents, 20, selected);
        this.changeTextColor(selected ? COLOR.accentLit : '#d3deec');
        this.changePaintOpacity(this.isCommandEnabled(index));
        this.contents.drawText(this.commandName(index), x + 28, rect.y, w - 32, rect.height, 'left');
        this.changePaintOpacity(true);
        this.resetFontSettings();
    };

    //=========================================================================
    // Window_NovaMenuStatus - portrait cards
    //=========================================================================
    function Window_NovaMenuStatus() { this.initialize.apply(this, arguments); }
    Window_NovaMenuStatus.prototype = Object.create(Window_MenuStatus.prototype);
    Window_NovaMenuStatus.prototype.constructor = Window_NovaMenuStatus;

    Window_NovaMenuStatus.prototype.initialize = function(x, y) {
        this._novaX = x;
        this._battlers = [];
        this._animTick = 0;
        Window_MenuStatus.prototype.initialize.call(this, x, y);
        this.opacity = 0;
    };
    Window_NovaMenuStatus.prototype.windowWidth = function() { return Graphics.boxWidth - this._novaX - 8; };
    Window_NovaMenuStatus.prototype.windowHeight = function() { return Graphics.boxHeight - HEADER_H - FOOTER_H; };
    Window_NovaMenuStatus.prototype.standardPadding = function() { return 10; };
    Window_NovaMenuStatus.prototype.maxCols = function() { return VISIBLE; };
    Window_NovaMenuStatus.prototype.spacing = function() { return 8; };
    Window_NovaMenuStatus.prototype.itemHeight = function() { return this.height - this.padding * 2; };
    Window_NovaMenuStatus.prototype.numVisibleRows = function() { return 1; };
    Window_NovaMenuStatus.prototype.updateCursor = function() { this.setCursorRect(0, 0, 0, 0); };
    Window_NovaMenuStatus.prototype.select = function(index) {
        Window_MenuStatus.prototype.select.call(this, index);
        if (this.contents) this.refresh();
    };
    Window_NovaMenuStatus.prototype.activate = function() {
        Window_MenuStatus.prototype.activate.call(this);
        if (this.contents) this.refresh();
    };
    Window_NovaMenuStatus.prototype.deactivate = function() {
        Window_MenuStatus.prototype.deactivate.call(this);
        if (this.contents) this.refresh();
    };
    Window_NovaMenuStatus.prototype.refresh = function() {
        Window_MenuStatus.prototype.refresh.call(this);
        this.rebuildBattlers();
    };

    Window_NovaMenuStatus.prototype.drawItem = function(index) {
        var actor = $gameParty.members()[index];
        if (!actor) return;
        var rect = this.itemRect(index);
        if (rect.y < 0 || rect.y >= this.contentsHeight()) return;  // other page
        var selected = this.active && index === this.index();
        var pending = index === this._pendingIndex;
        this.drawCardFrame(rect, selected, pending, actor.isBattleMember());
        this.drawPortrait(actor, rect);
        this.drawCardInfo(actor, rect);
    };

    Window_NovaMenuStatus.prototype.cardShape = function(rect) {
        var x = rect.x + 1, y = rect.y + 1, w = rect.width - 2, h = rect.height - 2, c = 14;
        return [[x + c, y], [x + w - c, y], [x + w, y + c], [x + w, y + h - c], [x + w - c, y + h],
                [x + c, y + h], [x, y + h - c], [x, y + c]];
    };

    Window_NovaMenuStatus.prototype.drawCardFrame = function(rect, selected, pending, active) {
        var ctx = ctxOf(this.contents);
        var shape = this.cardShape(rect);
        var g = ctx.createLinearGradient(0, rect.y, 0, rect.y + rect.height);
        g.addColorStop(0, COLOR.panelTop);
        g.addColorStop(1, COLOR.panelBottom);
        var edge = pending ? COLOR.pending : (selected ? COLOR.accentLit : COLOR.frame);
        ctx.save();
        if (selected) { ctx.shadowColor = COLOR.accent; ctx.shadowBlur = 14; }
        ctx.fillStyle = g;
        pathPoly(ctx, shape);
        ctx.fill();
        ctx.restore();
        ctx.lineWidth = selected ? 2.5 : 1.5;
        ctx.strokeStyle = edge;
        pathPoly(ctx, shape);
        ctx.stroke();
        // inner hairline
        ctx.lineWidth = 1;
        ctx.strokeStyle = COLOR.frameSoft;
        var inner = this.cardShape({ x: rect.x + 4, y: rect.y + 4, width: rect.width - 8, height: rect.height - 8 });
        pathPoly(ctx, inner);
        ctx.stroke();
        // diamonds on the top and bottom edge
        var cx = rect.x + rect.width / 2;
        diamond(ctx, cx, rect.y + 1.5, 5, edge);
        diamond(ctx, cx, rect.y + rect.height - 1.5, 5, edge);
        if (!active) {
            ctx.fillStyle = 'rgba(0, 0, 0, 0.35)';
            pathPoly(ctx, shape);
            ctx.fill();
        }
        dirty(this.contents);
    };

    Window_NovaMenuStatus.prototype.portraitHeight = function(rect) { return Math.floor(rect.height * 0.5); };

    Window_NovaMenuStatus.prototype.drawPortrait = function(actor, rect) {
        var ph = this.portraitHeight(rect);
        var px = rect.x + 5, py = rect.y + 5, pw = rect.width - 10;
        var name = portraitName(actor);
        var pic = pictureExists(name) ? ImageManager.loadPicture(name) : null;
        var ctx = ctxOf(this.contents);
        ctx.save();
        pathPoly(ctx, this.cardShape({ x: px - 1, y: py - 1, width: pw + 2, height: ph + 40 }));
        ctx.clip();
        // Cover the area but never enlarge: upscaling is what makes small art blurry.
        // Large art (e.g. high-res illustrations) is reduced with high-quality smoothing.
        var src, sx0 = 0, sy0 = 0, sw0, sh0;
        if (pic && pic.isReady() && pic.width > 0) {
            src = pic._canvas || pic._image; sw0 = pic.width; sh0 = pic.height;
        } else {
            var face = ImageManager.loadFace(actor.faceName());
            var fw = Window_Base._faceWidth, fh = Window_Base._faceHeight, fi = actor.faceIndex();
            src = face._canvas || face._image; sx0 = fi % 4 * fw; sy0 = Math.floor(fi / 4) * fh; sw0 = fw; sh0 = fh;
        }
        var scale = Math.min(1, Math.max(pw / sw0, ph / sh0));
        var dw = Math.round(sw0 * scale), dh = Math.round(sh0 * scale);
        var dx = px + Math.round((pw - dw) / 2);
        ctx.imageSmoothingEnabled = scale < 1;
        if ('imageSmoothingQuality' in ctx) ctx.imageSmoothingQuality = 'high';
        ctx.drawImage(src, sx0, sy0, sw0, sh0, dx, py, dw, dh);
        ctx.imageSmoothingEnabled = true;
        // fade the portrait into the card body
        var g = ctx.createLinearGradient(0, py + ph * 0.62, 0, py + ph);
        g.addColorStop(0, 'rgba(14, 20, 38, 0)');
        g.addColorStop(1, 'rgba(14, 20, 38, 0.97)');
        ctx.fillStyle = g;
        ctx.fillRect(px, py + ph * 0.62, pw, ph * 0.38 + 1);
        ctx.restore();
        dirty(this.contents);
    };

    Window_NovaMenuStatus.prototype.drawGaugeBar = function(x, y, w, rate, colors) {
        drawBar(ctxOf(this.contents), x, y, w, 7, rate, colors);
        dirty(this.contents);
    };

    Window_NovaMenuStatus.prototype.drawCardInfo = function(actor, rect) {
        var x = rect.x + 12, w = rect.width - 24;
        var y = rect.y + this.portraitHeight(rect) - 34;
        var lh = 26;
        this.resetFontSettings();

        // Level
        titleFont(this.contents, 15, false);
        this.changeTextColor(COLOR.dim);
        this.contents.drawText(TextManager.levelA, x, y, 40, 30, 'left');
        titleFont(this.contents, 32);
        this.changeTextColor(COLOR.accent);
        this.contents.drawText(actor.level, x + 26, y - 6, 70, 40, 'left');
        y += 30;

        // Name + class
        titleFont(this.contents, 22);
        this.changeTextColor(COLOR.text);
        this.contents.drawText(actor.name(), x, y, w, lh, 'left');
        y += lh - 2;
        bodyFont(this.contents, 16);
        this.contents.fontItalic = true;
        this.changeTextColor(COLOR.dim);
        this.contents.drawText(actor.currentClass().name, x, y, w, 20, 'left');
        this.contents.fontItalic = false;
        y += 22;

        // EXP to next level
        this.contents.fontSize = 15;
        this.changeTextColor(COLOR.dim);
        this.contents.drawText('Next', x, y, w, 20, 'left');
        this.changeTextColor(COLOR.text);
        this.contents.fontSize = 15;
        var next = actor.isMaxLevel() ? 'MAX' : actor.nextRequiredExp() + ' EXP';
        this.contents.drawText(next, x + 36, y, w - 36, 20, 'right');
        y += 20;
        var expRate = 1;
        if (!actor.isMaxLevel()) {
            var cur = actor.currentLevelExp(), nxt = actor.nextLevelExp();
            expRate = (actor.currentExp() - cur) / Math.max(1, nxt - cur);
        }
        this.drawGaugeBar(x, y + 2, w, expRate, COLOR.exp);
        y += 16;

        // HP / MP
        this.drawStatRow(x, y, w, TextManager.hpA, actor.hp, actor.mhp, COLOR.hp, actor.hp < actor.mhp / 4);
        y += 36;
        this.drawStatRow(x, y, w, TextManager.mpA, actor.mp, actor.mmp, COLOR.mp, false);
        y += 38;

        // Weapon
        var weapon = actor.weapons()[0];
        if (weapon) {
            this.contents.fontSize = 16;
            this.drawIcon(weapon.iconIndex, x - 2, y);
            this.changeTextColor(COLOR.text);
            this.contents.drawText(weapon.name, x + 32, y + 2, w - 32, 28, 'left');
        }
        y += 34;

        // States
        var icons = actor.allIcons().slice(0, Math.floor(w / Window_Base._iconWidth));
        for (var i = 0; i < icons.length; i++) this.drawIcon(icons[i], x + i * Window_Base._iconWidth, y);
        this.resetFontSettings();
    };

    Window_NovaMenuStatus.prototype.drawStatRow = function(x, y, w, label, value, max, colors, crisis) {
        titleFont(this.contents, 15);
        this.changeTextColor(colors[0]);
        this.contents.drawText(label, x, y, 40, 22, 'left');
        var maxText = '/' + max;
        bodyFont(this.contents, 14);
        var mw = this.textWidth(maxText);
        this.changeTextColor(COLOR.dim);
        this.contents.drawText(maxText, x, y + 3, w, 22, 'right');
        this.contents.fontSize = 21;
        this.changeTextColor(crisis ? this.crisisColor() : COLOR.text);
        this.contents.drawText(value, x, y, w - mw - 2, 22, 'right');
        this.drawGaugeBar(x, y + 24, w, value / Math.max(1, max), colors);
    };

    // Animated side-view battlers at the bottom of each visible card.
    Window_NovaMenuStatus.prototype.rebuildBattlers = function() {
        var self = this;
        this._battlers.forEach(function(s) { self.removeChild(s); });
        this._battlers = [];
        var members = $gameParty.members();
        var top = this.topIndex(), count = this.maxPageItems();
        for (var i = top; i < Math.min(members.length, top + count); i++) {
            var actor = members[i];
            var rect = this.itemRect(i);
            var sprite = new Sprite(ImageManager.loadSvActor(actor.battlerName()));
            sprite.anchor.x = 0.5;
            sprite.anchor.y = 1;
            sprite.x = this.padding + rect.x + rect.width / 2;
            sprite.y = this.padding + rect.y + rect.height - 6;
            sprite._novaActor = actor;
            sprite.opacity = actor.isBattleMember() ? 255 : 150;
            this._battlers.push(sprite);
            this.addChild(sprite);
        }
        this.updateBattlerFrames();
    };

    Window_NovaMenuStatus.prototype.updateBattlerFrames = function() {
        var pattern = [0, 1, 2, 1][Math.floor(this._animTick / 10) % 4];
        this._battlers.forEach(function(sprite) {
            var actor = sprite._novaActor;
            // 0 = walk: the generator's "wait" frames are identical, so walking is what reads as alive
            var motion = actor.isDead() ? 17 : (actor.isDying() ? 14 : (actor.isStateAffected(10) ? 16 : 0));
            var bmp = sprite.bitmap;
            if (!bmp || !bmp.isReady()) return;
            var cw = bmp.width / 9, ch = bmp.height / 6;
            var p = motion === 17 ? 2 : pattern;
            sprite.setFrame((Math.floor(motion / 6) * 3 + p) * cw, (motion % 6) * ch, cw, ch);
        });
    };

    Window_NovaMenuStatus.prototype.update = function() {
        Window_MenuStatus.prototype.update.call(this);
        this._animTick++;
        if (this._animTick % 10 === 0) this.updateBattlerFrames();
    };

    //=========================================================================
    // Shared look for every menu screen (Item, Skill, Equip, Options, Save, Shop ...)
    //=========================================================================
    function pictureExists(name) {
        try {
            if (typeof require === 'function') {
                var path = require('path');
                var base = path.dirname(process.mainModule.filename);
                return require('fs').existsSync(path.join(base, 'img/pictures', name + '.png'));
            }
        } catch (e) { /* browser build: assume it exists */ }
        return true;
    }

    // Night blue over the map, darker towards the edges.
    function drawBackdrop(bmp) {
        var w = bmp.width, h = bmp.height, ctx = ctxOf(bmp);
        var g = ctx.createLinearGradient(0, 0, 0, h);
        g.addColorStop(0, 'rgba(10, 16, 32, 0.93)');
        g.addColorStop(0.5, 'rgba(18, 28, 54, 0.84)');
        g.addColorStop(1, 'rgba(6, 10, 20, 0.95)');
        ctx.fillStyle = g;
        ctx.fillRect(0, 0, w, h);
        var v = ctx.createRadialGradient(w / 2, h * 0.45, h * 0.25, w / 2, h * 0.45, w * 0.75);
        v.addColorStop(0, 'rgba(0, 0, 0, 0)');
        v.addColorStop(1, 'rgba(0, 0, 0, 0.45)');
        ctx.fillStyle = v;
        ctx.fillRect(0, 0, w, h);
        dirty(bmp);
    }

    function panelShape(x, y, w, h, c) {
        return [[x + c, y], [x + w - c, y], [x + w, y + c], [x + w, y + h - c], [x + w - c, y + h],
                [x + c, y + h], [x, y + h - c], [x, y + c]];
    }

    // A night-blue card with a steel-blue rim drawn behind a window (the window's own frame/back are hidden).
    function Sprite_NovaPanel() { this.initialize.apply(this, arguments); }
    Sprite_NovaPanel.prototype = Object.create(Sprite.prototype);
    Sprite_NovaPanel.prototype.constructor = Sprite_NovaPanel;
    Sprite_NovaPanel.prototype.initialize = function(win) {
        Sprite.prototype.initialize.call(this);
        this._win = win;
        this._w = this._h = 0;
    };
    Sprite_NovaPanel.prototype.redraw = function(w, h) {
        this._w = w; this._h = h;
        this.bitmap = new Bitmap(Math.max(1, w), Math.max(1, h));
        var ctx = ctxOf(this.bitmap), c = Math.min(14, Math.floor(Math.min(w, h) / 4));
        var g = ctx.createLinearGradient(0, 0, 0, h);
        g.addColorStop(0, COLOR.panelTop);
        g.addColorStop(1, COLOR.panelBottom);
        ctx.fillStyle = g;
        pathPoly(ctx, panelShape(1, 1, w - 2, h - 2, c));
        ctx.fill();
        ctx.lineWidth = 1.5;
        ctx.strokeStyle = COLOR.frame;
        pathPoly(ctx, panelShape(1, 1, w - 2, h - 2, c));
        ctx.stroke();
        ctx.lineWidth = 1;
        ctx.strokeStyle = COLOR.frameSoft;
        pathPoly(ctx, panelShape(4, 4, w - 8, h - 8, Math.max(2, c - 3)));
        ctx.stroke();
        if (w > 120) {
            diamond(ctx, w / 2, 1.5, 4, COLOR.frame);
            diamond(ctx, w / 2, h - 1.5, 4, COLOR.frame);
        }
        dirty(this.bitmap);
    };
    Sprite_NovaPanel.prototype.update = function() {
        Sprite.prototype.update.call(this);
        var win = this._win;
        if (win.width !== this._w || win.height !== this._h) this.redraw(win.width, win.height);
        var open = win.openness / 255;
        this.visible = win.visible && open > 0 && !!win.parent;
        this.x = win.x;
        this.y = win.y + win.height * (1 - open) / 2;
        this.scale.y = open;
    };

    function skinWindows(scene) {
        if (!scene._windowLayer) return;
        if (!scene._novaPanelLayer) {
            scene._novaPanelLayer = new Sprite();
            scene.addChildAt(scene._novaPanelLayer, scene.children.indexOf(scene._windowLayer));
        }
        scene._windowLayer.children.forEach(function(win) {
            if (!(win instanceof Window) || win._novaSkinned || win._novaNoPanel) return;
            win._novaSkinned = true;
            if (win.opacity === 0 && win.backOpacity === 0) return;
            if (win instanceof Window_NovaMenuCommand || win instanceof Window_NovaMenuStatus) return;
            win.opacity = 0;
            scene._novaPanelLayer.addChild(new Sprite_NovaPanel(win));
        });
    }

    var _MenuBase_createBackground = Scene_MenuBase.prototype.createBackground;
    Scene_MenuBase.prototype.createBackground = function() {
        _MenuBase_createBackground.call(this);
        if (this instanceof Scene_Menu) return;            // Scene_Menu draws its own
        var bmp = new Bitmap(Graphics.width, Graphics.height);
        drawBackdrop(bmp);
        this._novaBackdropSprite = new Sprite(bmp);
        this.addChild(this._novaBackdropSprite);
    };

    var _MenuBase_update = Scene_MenuBase.prototype.update;
    Scene_MenuBase.prototype.update = function() {
        skinWindows(this);                                  // also catches windows created later
        _MenuBase_update.call(this);
    };

    //=========================================================================
    // Status screen: full-body portrait on the left, details on the right,
    // left/right (or Q/W, or the on-screen arrows) to change character.
    //=========================================================================
    var FULL_PREFIX = 'Full_';

    function Window_NovaStatus() { this.initialize.apply(this, arguments); }
    Window_NovaStatus.prototype = Object.create(Window_Status.prototype);
    Window_NovaStatus.prototype.constructor = Window_NovaStatus;

    Window_NovaStatus.prototype.initialize = function(x, y, w, h) {
        Window_Selectable.prototype.initialize.call(this, x, y, w, h);
        this._actor = null;
        this.refresh();
        this.activate();
    };
    // shared drawing helpers from the menu cards
    Window_NovaStatus.prototype.drawGaugeBar = Window_NovaMenuStatus.prototype.drawGaugeBar;
    Window_NovaStatus.prototype.drawStatRow = Window_NovaMenuStatus.prototype.drawStatRow;

    Window_NovaStatus.prototype.processHandling = function() {
        Window_Status.prototype.processHandling.call(this);
        if (!this.isOpenAndActive()) return;
        if (Input.isRepeated('right') && this.isHandled('pagedown')) this.processPagedown();
        else if (Input.isRepeated('left') && this.isHandled('pageup')) this.processPageup();
    };

    Window_NovaStatus.prototype.refresh = function() {
        this.contents.clear();
        var a = this._actor;
        if (!a) return;
        var w = this.contentsWidth(), lh = this.lineHeight();
        // face image in a small framed box, name block beside it
        var FS = 96, fx = 2, fy = 2, tx = FS + 18;
        this.drawNovaFace(a, fx, fy, FS);
        titleFont(this.contents, 36);
        this.changeTextColor(COLOR.text);
        this.contents.drawText(a.name(), tx, 0, w * 0.5, 52, 'left');
        bodyFont(this.contents, 18);
        this.contents.fontItalic = true;
        this.changeTextColor(COLOR.accent);
        this.contents.drawText(a.nickname(), tx + 2, 46, w * 0.45, 26, 'left');
        this.contents.fontItalic = false;
        this.changeTextColor(COLOR.dim);
        this.contents.drawText(a.currentClass().name, tx + 2, 70, w * 0.45, 26, 'left');
        // level
        titleFont(this.contents, 18, false);
        this.contents.drawText(TextManager.levelA, w - 170, 8, 50, 30, 'left');
        titleFont(this.contents, 44);
        this.changeTextColor(COLOR.accent);
        this.contents.drawText(a.level, w - 130, -4, 126, 60, 'right');
        bodyFont(this.contents, 16);
        this.changeTextColor(COLOR.dim);
        var next = a.isMaxLevel() ? 'MAX' : a.nextRequiredExp() + ' EXP';
        this.contents.drawText('Next', w - 250, 60, 80, 22, 'left');
        this.changeTextColor(COLOR.text);
        this.contents.drawText(next, w - 200, 60, 196, 22, 'right');
        var rate = 1;
        if (!a.isMaxLevel()) rate = (a.currentExp() - a.currentLevelExp()) / Math.max(1, a.nextLevelExp() - a.currentLevelExp());
        this.drawGaugeBar(w - 250, 86, 246, rate, COLOR.exp);

        var y = 110;
        this.drawDivider(y); y += 12;
        // HP / MP
        var half = Math.floor((w - 24) / 2);
        this.drawStatRow(4, y, half, TextManager.hpA, a.hp, a.mhp, COLOR.hp, a.isDying());
        this.drawStatRow(half + 20, y, half, TextManager.mpA, a.mp, a.mmp, COLOR.mp, false);
        y += 44;
        this.drawDivider(y); y += 12;
        // parameters (left) and equipment (right)
        titleFont(this.contents, 16);
        this.changeTextColor(COLOR.accent);
        this.contents.drawText('PARAMETERS', 4, y, half, 24, 'left');
        this.contents.drawText('EQUIPMENT', half + 20, y, half, 24, 'left');
        bodyFont(this.contents);
        y += 28;
        var py = y;
        for (var i = 2; i < 8; i++) {
            this.contents.fontSize = 19;
            this.changeTextColor(COLOR.dim);
            this.contents.drawText(TextManager.param(i), 8, py, 160, 30, 'left');
            this.changeTextColor(COLOR.text);
            this.contents.fontSize = 22;
            this.contents.drawText(a.param(i), 8, py, half - 16, 30, 'right');
            var ctx = ctxOf(this.contents);
            ctx.fillStyle = 'rgba(156, 192, 236, 0.15)';
            ctx.fillRect(8, py + 30, half - 16, 1);
            py += 34;
        }
        var ey = y, slots = a.equipSlots(), equips = a.equips();
        for (var k = 0; k < slots.length; k++) {
            titleFont(this.contents, 13, false);
            this.changeTextColor(COLOR.dim);
            this.contents.drawText($dataSystem.equipTypes[slots[k]], half + 24, ey, 120, 16, 'left');
            bodyFont(this.contents);
            var item = equips[k];
            if (item) {
                this.drawIcon(item.iconIndex, half + 22, ey + 14);
                this.contents.fontSize = 19;
                this.changeTextColor(COLOR.text);
                this.contents.drawText(item.name, half + 58, ey + 16, half - 40, 28, 'left');
            } else {
                this.contents.fontSize = 19;
                this.changeTextColor('rgba(200, 215, 235, 0.35)');
                this.contents.drawText('-----', half + 58, ey + 16, half - 40, 28, 'left');
            }
            ey += 46;
        }
        y = Math.max(py, ey) + 6;
        this.drawDivider(y); y += 14;
        // profile
        this.contents.fontSize = 19;
        this.changeTextColor('#d3deec');
        var lines = String(a.profile() || '').split('\n');
        for (var n = 0; n < lines.length && y + 26 <= this.contentsHeight(); n++) {
            this.contents.drawText(lines[n], 6, y, w - 12, 26, 'left');
            y += 26;
        }
        this.resetFontSettings();
    };

    Window_NovaStatus.prototype.drawNovaFace = function(actor, x, y, size) {
        var ctx = ctxOf(this.contents), c = 8;
        var shape = panelShape(x, y, size, size, c);
        ctx.save();
        ctx.fillStyle = COLOR.ink;
        pathPoly(ctx, shape); ctx.fill();
        pathPoly(ctx, shape); ctx.clip();
        var bmp = ImageManager.loadFace(actor.faceName());
        if (bmp.isReady()) {
            var fw = Window_Base._faceWidth, fh = Window_Base._faceHeight, i = actor.faceIndex();
            ctx.imageSmoothingEnabled = true;
            if ('imageSmoothingQuality' in ctx) ctx.imageSmoothingQuality = 'high';
            ctx.drawImage(bmp._canvas || bmp._image, i % 4 * fw, Math.floor(i / 4) * fh, fw, fh, x, y, size, size);
        } else {
            bmp.addLoadListener(this.refresh.bind(this));
        }
        ctx.restore();
        ctx.lineWidth = 1.5;
        ctx.strokeStyle = COLOR.frame;
        pathPoly(ctx, shape); ctx.stroke();
        dirty(this.contents);
    };

    Window_NovaStatus.prototype.drawDivider = function(y) {
        var ctx = ctxOf(this.contents), w = this.contentsWidth();
        var g = ctx.createLinearGradient(0, 0, w, 0);
        g.addColorStop(0, 'rgba(156, 192, 236, 0.6)');
        g.addColorStop(1, 'rgba(156, 192, 236, 0)');
        ctx.fillStyle = g;
        ctx.fillRect(6, y, w - 6, 1);
        diamond(ctx, 4, y + 0.5, 4, COLOR.accent);
        dirty(this.contents);
    };

    Scene_Status.prototype.create = function() {
        Scene_MenuBase.prototype.create.call(this);
        var w = Graphics.boxWidth, h = Graphics.boxHeight;
        // header
        var head = new Bitmap(w, HEADER_H);
        drawHeader(head, 'STATUS');
        head.fontSize = 18; head.textColor = COLOR.dim; head.outlineWidth = 3;
        head.drawText('◀  ▶   Change character', w - 360, 18, 340, 30, 'right');
        // portrait area (left) and details (right)
        var split = Math.floor(w * 0.40);
        this._novaGlow = new Sprite(new Bitmap(split, h - HEADER_H));
        this._novaGlow.y = HEADER_H;
        this.addChild(this._novaGlow);
        this._novaPortrait = new Sprite();
        this._novaPortrait.anchor.x = 0.5; this._novaPortrait.anchor.y = 1;
        this._novaPortraitHome = { x: Math.floor(split / 2), y: h - 4 };
        this.addChild(this._novaPortrait);
        this.addChild(new Sprite(head));
        this._statusWindow = new Window_NovaStatus(split, HEADER_H + 4, w - split - 12, h - HEADER_H - 16);
        this._statusWindow.setHandler('cancel', this.popScene.bind(this));
        this._statusWindow.setHandler('pagedown', this.nextActor.bind(this));
        this._statusWindow.setHandler('pageup', this.previousActor.bind(this));
        this.addWindow(this._statusWindow);
        // on-screen arrows
        this._novaArrows = [];
        [['◀', 18, -1], ['▶', split - 54, 1]].forEach(function(spec) {
            var b = new Bitmap(40, 60);
            b.fontSize = 40; b.textColor = COLOR.accentLit; b.outlineColor = 'rgba(11, 17, 32, 0.9)'; b.outlineWidth = 6;
            b.drawText(spec[0], 0, 0, 40, 60, 'center');
            var s = new Sprite(b);
            s.x = spec[1]; s.y = Math.floor(h / 2) - 30; s._dir = spec[2]; s.opacity = 200;
            this.addChild(s);
            this._novaArrows.push(s);
        }, this);
        this._novaSlide = 0;
    };

    Scene_Status.prototype.refreshActor = function() {
        var actor = this.actor();
        this._statusWindow.setActor(actor);
        this.refreshNovaPortrait(actor);
    };

    Scene_Status.prototype.nextActor = function() { this._novaDir = 1; Scene_MenuBase.prototype.nextActor.call(this); };
    Scene_Status.prototype.previousActor = function() { this._novaDir = -1; Scene_MenuBase.prototype.previousActor.call(this); };

    Scene_Status.prototype.refreshNovaPortrait = function(actor) {
        var name = FULL_PREFIX + actor.name();
        var sprite = this._novaPortrait, home = this._novaPortraitHome, scene = this;
        if (!pictureExists(name)) name = portraitName(actor);
        if (!pictureExists(name)) { sprite.bitmap = null; return; }
        var bmp = ImageManager.loadPicture(name);
        bmp.addLoadListener(function() {
            sprite.bitmap = bmp;
            var maxH = Graphics.boxHeight - HEADER_H - 8, maxW = home.x * 2 - 70;
            var s = Math.min(1, maxH / bmp.height, maxW / bmp.width);
            sprite.scale.x = sprite.scale.y = s;
            sprite.y = home.y;
            scene._novaSlide = scene._novaDir ? 14 : 0;
            sprite.x = home.x + (scene._novaDir || 0) * 60;
            sprite.opacity = scene._novaDir ? 0 : 255;
        });
        this.drawNovaGlow(actor);
    };

    Scene_Status.prototype.drawNovaGlow = function(actor) {
        var b = this._novaGlow.bitmap, ctx = ctxOf(b);
        b.clear();
        var tint = { 1: '170,90,255', 2: '120,200,255', 3: '240,150,220', 4: '120,200,110', 5: '255,210,120', 6: '255,110,60' }[actor.actorId()] || '120,200,255';
        var cx = b.width / 2, cy = b.height * 0.45;
        var g = ctx.createRadialGradient(cx, cy, 0, cx, cy, b.width * 0.62);
        g.addColorStop(0, 'rgba(' + tint + ',0.42)');
        g.addColorStop(0.6, 'rgba(' + tint + ',0.10)');
        g.addColorStop(1, 'rgba(' + tint + ',0)');
        ctx.fillStyle = g;
        ctx.fillRect(0, 0, b.width, b.height);
        dirty(b);
    };

    var _Scene_Status_update = Scene_Status.prototype.update;
    Scene_Status.prototype.update = function() {
        _Scene_Status_update.call(this);
        var sprite = this._novaPortrait, home = this._novaPortraitHome;
        if (this._novaSlide > 0) {
            this._novaSlide--;
            sprite.x += (home.x - sprite.x) * 0.3;
            sprite.opacity = Math.min(255, sprite.opacity + 24);
            if (this._novaSlide === 0) { sprite.x = home.x; sprite.opacity = 255; }
        }
        // touch / click on the arrows
        if (TouchInput.isTriggered() && this._statusWindow.active) {
            this._novaArrows.forEach(function(a) {
                if (TouchInput.x >= a.x && TouchInput.x < a.x + 40 && TouchInput.y >= a.y && TouchInput.y < a.y + 60) {
                    SoundManager.playCursor();
                    if (a._dir > 0) this.nextActor(); else this.previousActor();
                }
            }, this);
        }
        this._novaArrows.forEach(function(a) { a.opacity = 160 + Math.round(Math.sin(Graphics.frameCount / 15) * 60); });
    };

    //=========================================================================
    // Skills: one "Skill" entry with every skill type the actor has, instead
    // of one entry per type (NovaBattle does the same for the battle command)
    //=========================================================================
    Window_SkillType.prototype.makeCommandList = function() {
        if (this._actor && this._actor.addedSkillTypes().length > 0) {
            this.addCommand(TextManager.skill, 'skill', true, 'all');
        }
    };

    var _Window_SkillList_includes = Window_SkillList.prototype.includes;
    Window_SkillList.prototype.includes = function(item) {
        if (this._stypeId === 'all') {
            return !!item && !!this._actor && this._actor.addedSkillTypes().contains(item.stypeId);
        }
        return _Window_SkillList_includes.call(this, item);
    };

    window.Window_NovaMenuCommand = Window_NovaMenuCommand;
    window.Window_NovaMenuStatus = Window_NovaMenuStatus;
    window.Window_NovaStatus = Window_NovaStatus;

    // Shared look for other Nova plugins (e.g. NovaBattle).
    window.NovaUI = {
        COLOR: COLOR,
        ctxOf: ctxOf,
        dirty: dirty,
        pathPoly: pathPoly,
        panelShape: panelShape,
        diamond: diamond,
        drawBar: drawBar,
        drawHeader: drawHeader,
        titleFont: titleFont,
        bodyFont: bodyFont,
        skinWindows: skinWindows
    };
})();
