/* RM Map Forge — antarmuka editor. */
(() => {
  'use strict';
  const C = window.RMCore;
  const $ = s => document.querySelector(s);
  const cv = $('#mapCanvas');
  const ctx = cv.getContext('2d');
  const ZOOMS = [8, 12, 16, 20, 24, 32, 48];

  // ---------------------------------------------------------------------------
  // Utilitas
  // ---------------------------------------------------------------------------
  function el(tag, props, ...kids) {
    const e = document.createElement(tag);
    if (props) {
      for (const [k, v] of Object.entries(props)) {
        if (v == null || v === false) continue;
        if (k === 'class') e.className = v;
        else if (k === 'style') e.style.cssText = v;
        else if (k.startsWith('on') && typeof v === 'function') e.addEventListener(k.slice(2), v);
        else if (k in e) e[k] = v;
        else e.setAttribute(k, v === true ? '' : v);
      }
    }
    for (const c of kids.flat()) {
      if (c == null || c === false) continue;
      e.append(c.nodeType ? c : document.createTextNode(String(c)));
    }
    return e;
  }
  const clamp = (v, lo, hi) => Math.max(lo, Math.min(hi, v));
  const pad3 = n => String(n).padStart(3, '0');
  const randomSeed = () => Math.random().toString(36).slice(2, 8);
  const stop = e => e.stopPropagation();

  function toast(msg, kind = 'info', ms = 4500) {
    const t = el('div', { class: 'toast ' + kind }, msg);
    $('#toasts').append(t);
    setTimeout(() => t.remove(), ms);
  }
  function download(name, text) {
    const url = URL.createObjectURL(new Blob([text], { type: 'application/json' }));
    const a = el('a', { href: url, download: name });
    document.body.append(a);
    a.click();
    a.remove();
    setTimeout(() => URL.revokeObjectURL(url), 2000);
  }
  function shade(hex, f) {
    const n = parseInt(hex.slice(1), 16);
    const ch = s => clamp(Math.round(((n >> s) & 255) * f), 0, 255);
    return `rgb(${ch(16)},${ch(8)},${ch(0)})`;
  }
  function randomColor() {
    const h = Math.floor(Math.random() * 360), s = 0.45, l = 0.5;
    const a = s * Math.min(l, 1 - l);
    const f = k => { const c = (k + h / 30) % 12; return Math.round(255 * (l - a * Math.max(-1, Math.min(c - 3, 9 - c, 1)))); };
    return '#' + [f(0), f(8), f(4)].map(v => v.toString(16).padStart(2, '0')).join('');
  }

  // ---------------------------------------------------------------------------
  // State
  // ---------------------------------------------------------------------------
  const S = {
    type: 'overworld', width: 80, height: 60, seed: '',
    configs: {}, grid: null, deco: null, deco3: null, own2: null, own3: null, built: null,
    level: null, biome: null, paths: [], cliff: null, routes: null,
    tool: 'terrain', terrainSel: 0, objectSel: 0, biomeSel: 0, pathSel: 0, levelSel: 1,
    radius: 2, zoom: 16, showGrid: false, showBiome: false,
    undo: [], redo: [], open: new Set(),
  };
  const P = {
    fs: null, name: '', tilesets: null, mapInfos: null, system: null, engine: '',
    tilesetId: 0, names: null, images: new Array(9).fill(null), labels: new Array(9).fill(null), tileSize: 48,
  };
  const tileCache = new Map();
  const cfg = () => S.configs[S.type];
  const st = () => ({
    type: S.type, width: S.width, height: S.height, seed: S.seed,
    params: cfg().params, terrains: cfg().terrains, objects: cfg().objects, grid: S.grid,
    deco: S.deco, deco3: S.deco3, own2: S.own2, own3: S.own3,
    biomes: cfg().biomes, hill: cfg().hill, stairs: cfg().stairs,
    level: S.level, biome: S.biome, paths: S.paths, cliff: S.cliff, routes: S.routes,
  });
  /** Hitung ulang tebing & rute jalan, lalu gambar ulang. */
  function prepAndRender() {
    const s = st();
    C.prepare(s);
    S.cliff = s.cliff;
    S.routes = s.routes;
    rebuild();
    renderAll();
  }
  const clonePaths = ps => JSON.parse(JSON.stringify(ps || []));
  for (const t of C.TYPES) S.configs[t] = C.defaultConfig(t);
  const OBJ_LAYERS = ['deco', 'deco3', 'own2', 'own3'];
  const maxObjHeight = () => cfg().objects.reduce((m, o) => Math.max(m, (C.objTiles(o) || [[]]).length), 1);
  const hasHills = () => S.type === 'outside';
  const hasPaths = () => !C.isWallType(S.type);

  // ---------------------------------------------------------------------------
  // Tile & gambar
  // ---------------------------------------------------------------------------
  function getTile(id) {
    if (!id) return null;
    if (tileCache.has(id)) return tileCache.get(id);
    const c = makeTile(id);
    tileCache.set(id, c);
    return c;
  }
  function makeTile(id) {
    const src = C.tileSource(id);
    if (!src) return null;
    const img = P.images[src.set];
    if (!img) return null;
    const ts = P.tileSize, h = ts / 2;
    const c = document.createElement('canvas');
    c.width = c.height = ts;
    const g = c.getContext('2d');
    if (src.quads) {
      for (let q = 0; q < 4; q++) {
        const sx = src.quads[q][0] * h, sy = src.quads[q][1] * h;
        if (sx + h > img.width || sy + h > img.height) return null;
        g.drawImage(img, sx, sy, h, h, (q % 2) * h, Math.floor(q / 2) * h, h, h);
      }
    } else {
      const sx = src.sx * ts, sy = src.sy * ts;
      if (sx + ts > img.width || sy + ts > img.height) return null;
      g.drawImage(img, sx, sy, ts, ts, 0, 0, ts, ts);
    }
    return c;
  }
  const specTileId = tile => !tile ? 0 : tile.auto != null ? C.autoId(tile.auto, C.thumbShape(tile.auto)) : tile.id;
  const labelOf = tile => {
    if (!tile) return '';
    const set = C.setOfTile(tile), lab = P.labels[set];
    return (lab && lab[C.labelIndex(tile)]) || '';
  };
  function makeThumb(tile, color) {
    const c = el('canvas', { width: 32, height: 32, class: 'thumb' });
    const g = c.getContext('2d');
    g.imageSmoothingEnabled = false;
    const t = P.fs && tile ? getTile(specTileId(tile)) : null;
    if (t) {
      g.drawImage(t, 0, 0, 32, 32);
    } else {
      g.fillStyle = color || '#444';
      g.fillRect(0, 0, 32, 32);
    }
    const name = labelOf(tile);
    c.title = (name ? name + ' — ' : '') + 'klik untuk memilih tile';
    return c;
  }

  // ---------------------------------------------------------------------------
  // Generate, bangun data, render
  // ---------------------------------------------------------------------------
  function rebuild() { S.built = C.buildData(st()); }

  function generateMap(opts = {}) {
    S.width = clamp(parseInt($('#mapW').value, 10) || C.DEFAULT_SIZE[S.type][0], 10, 256);
    S.height = clamp(parseInt($('#mapH').value, 10) || C.DEFAULT_SIZE[S.type][1], 10, 256);
    $('#mapW').value = S.width;
    $('#mapH').value = S.height;
    S.seed = $('#seed').value.trim() || randomSeed();
    $('#seed').value = S.seed;
    if (S.grid && !opts.noUndo) pushUndo();
    const s = st();
    C.generate(s);
    S.grid = s.grid;
    for (const k of OBJ_LAYERS) S[k] = s[k];
    Object.assign(S, { level: s.level, biome: s.biome, paths: s.paths, cliff: s.cliff, routes: s.routes });
    S.pathSel = Math.min(S.pathSel, Math.max(0, S.paths.length - 1));
    $('#ruleHint').hidden = true;
    rebuild();
    renderAll();
    renderPathList();
  }

  function renderAll() {
    if (!S.built) return;
    cv.width = S.width * S.zoom;
    cv.height = S.height * S.zoom;
    renderRegion(0, 0, S.width - 1, S.height - 1);
    if (S.tool === 'path') drawWaypoints();
  }

  function drawWaypoints() {
    const z = S.zoom;
    S.paths.forEach((p, k) => {
      const sel = k === S.pathSel;
      const pts = p.points || [];
      ctx.lineWidth = sel ? 3 : 2;
      ctx.strokeStyle = sel ? '#4f8cff' : 'rgba(255,255,255,0.55)';
      ctx.beginPath();
      pts.forEach(([x, y], n) => {
        const cx = x * z + z / 2, cy = y * z + z / 2;
        n ? ctx.lineTo(cx, cy) : ctx.moveTo(cx, cy);
      });
      ctx.stroke();
      pts.forEach(([x, y], n) => {
        const cx = x * z + z / 2, cy = y * z + z / 2, r = Math.max(7, z * 0.4);
        ctx.fillStyle = sel ? '#4f8cff' : '#6b7280';
        ctx.strokeStyle = '#fff';
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.arc(cx, cy, r, 0, Math.PI * 2);
        ctx.fill();
        ctx.stroke();
        ctx.fillStyle = '#fff';
        ctx.font = `bold ${Math.round(r * 1.1)}px Segoe UI, sans-serif`;
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(String(n + 1), cx, cy + 1);
      });
    });
  }

  function renderRegion(x0, y0, x1, y1) {
    const W = S.width, H = S.height, N = W * H, z = S.zoom;
    x0 = Math.max(0, x0); y0 = Math.max(0, y0); x1 = Math.min(W - 1, x1); y1 = Math.min(H - 1, y1);
    const d = S.built.data, cls = S.built.cls, T = cfg().terrains;
    const wallType = C.isWallType(S.type);
    const F = wallType ? C.roleIdx(T, 'floor') : 0, Wl = wallType ? C.roleIdx(T, 'wall') : 0;
    const faceColor = wallType ? shade(T[Wl].color, 1.45) : null;
    const biomeTint = (S.tool === 'biome' || S.showBiome) && cfg().biomes.length > 1
      ? cfg().biomes.map(b => b.color + '66') : null;
    const hz = z / 2;
    ctx.imageSmoothingEnabled = false;
    for (let y = y0; y <= y1; y++) {
      for (let x = x0; x <= x1; x++) {
        const i = y * W + x, px = x * z, py = y * z;
        let t, color;
        if (wallType) {
          t = cls[i] === 0 ? T[F] : T[Wl];
          color = cls[i] === 1 ? faceColor : t.color;
        } else {
          const ti = S.routes && S.routes.terrain[i] >= 0 ? S.routes.terrain[i] : S.grid[i];
          t = T[ti];
          const L = S.level ? S.level[i] : 0;
          color = S.cliff && S.cliff[i] ? '#7a5a3a' : L ? shade(t.color, 1 + 0.16 * L) : t.color;
        }
        let drawn = false;
        if (P.fs && t.tile) {
          ctx.fillStyle = '#000';
          ctx.fillRect(px, py, z, z);
          const a = getTile(d[i]);
          if (a) { ctx.drawImage(a, px, py, z, z); drawn = true; }
          const b = d[N + i] ? getTile(d[N + i]) : null;
          if (b) { ctx.drawImage(b, px, py, z, z); drawn = true; }
        }
        if (!drawn) {
          ctx.fillStyle = color;
          ctx.fillRect(px, py, z, z);
        }
        const sh = d[4 * N + i];
        if (sh) {
          ctx.fillStyle = 'rgba(0,0,0,0.5)';
          for (let q = 0; q < 4; q++) if (sh & (1 << q)) ctx.fillRect(px + (q % 2) * hz, py + (q >> 1) * hz, hz, hz);
        }
        for (let zl = 2; zl <= 3; zl++) {
          const o = d[zl * N + i];
          if (!o) continue;
          const ot = P.fs ? getTile(o) : null;
          if (ot) ctx.drawImage(ot, px, py, z, z);
          else {
            ctx.fillStyle = zl === 2 ? '#ffd166' : '#ffe9a8';
            ctx.strokeStyle = '#000';
            ctx.beginPath();
            ctx.arc(px + hz, py + hz, Math.max(2, z * 0.22), 0, Math.PI * 2);
            ctx.fill();
            ctx.stroke();
          }
        }
        if (biomeTint && S.biome) {
          ctx.fillStyle = biomeTint[S.biome[i]] || 'transparent';
          ctx.fillRect(px, py, z, z);
        }
      }
    }
    if (S.showGrid && z >= 8) {
      ctx.strokeStyle = 'rgba(255,255,255,0.13)';
      ctx.lineWidth = 1;
      ctx.beginPath();
      for (let x = x0; x <= x1 + 1; x++) { ctx.moveTo(x * z + 0.5, y0 * z); ctx.lineTo(x * z + 0.5, (y1 + 1) * z); }
      for (let y = y0; y <= y1 + 1; y++) { ctx.moveTo(x0 * z, y * z + 0.5); ctx.lineTo((x1 + 1) * z, y * z + 0.5); }
      ctx.stroke();
    }
  }

  function fitZoom() {
    const vp = $('#viewport');
    const aw = vp.clientWidth - 40, ah = vp.clientHeight - 40;
    let z = ZOOMS[0];
    for (const c of ZOOMS) if (S.width * c <= aw && S.height * c <= ah) z = c;
    S.zoom = z;
    $('#zoom').value = z;
    renderAll();
  }

  // ---------------------------------------------------------------------------
  // Undo / redo
  // ---------------------------------------------------------------------------
  const snapshot = () => {
    const snap = { type: S.type, width: S.width, height: S.height, grid: S.grid.slice() };
    for (const k of OBJ_LAYERS) snap[k] = S[k].slice();
    snap.level = S.level.slice();
    snap.biome = S.biome.slice();
    snap.paths = clonePaths(S.paths);
    return snap;
  };
  function pushUndo() {
    if (!S.grid) return;
    S.undo.push(snapshot());
    if (S.undo.length > 80) S.undo.shift();
    S.redo.length = 0;
    syncUndo();
  }
  function restore(s) {
    const typeChanged = s.type !== S.type;
    Object.assign(S, { type: s.type, width: s.width, height: s.height, grid: s.grid });
    for (const k of OBJ_LAYERS) S[k] = s[k];
    Object.assign(S, { level: s.level, biome: s.biome, paths: s.paths });
    S.pathSel = Math.min(S.pathSel, Math.max(0, S.paths.length - 1));
    if (typeChanged) syncTypeUI();
    $('#mapW').value = S.width;
    $('#mapH').value = S.height;
    prepAndRender();
    renderPathList();
  }
  function undo() { if (!S.undo.length) return; S.redo.push(snapshot()); restore(S.undo.pop()); syncUndo(); }
  function redo() { if (!S.redo.length) return; S.undo.push(snapshot()); restore(S.redo.pop()); syncUndo(); }
  function clearHistory() { S.undo.length = 0; S.redo.length = 0; syncUndo(); }
  function syncUndo() {
    $('#btnUndo').disabled = !S.undo.length;
    $('#btnRedo').disabled = !S.redo.length;
  }

  // ---------------------------------------------------------------------------
  // Panel generator
  // ---------------------------------------------------------------------------
  function rangeRow(label, value, min, max, step, onChange, fmt) {
    const show = el('span', null, fmt(value));
    const input = el('input', {
      type: 'range', min, max, step, value,
      oninput: e => { show.textContent = fmt(+e.target.value); },
      onchange: e => onChange(+e.target.value),
    });
    return el('div', { class: 'param' }, el('div', { class: 'lbl' }, el('span', null, label), show), input);
  }

  function renderParams() {
    const box = $('#paramBox');
    box.innerHTML = '';
    const p = cfg().params;
    for (const d of C.PARAM_DEFS[S.type]) {
      if (d.type === 'check') {
        box.append(el('label', { class: 'check' },
          el('input', { type: 'checkbox', checked: !!p[d.key], onchange: e => { p[d.key] = e.target.checked; savePreset(); prepAndRender(); } }),
          d.label));
        continue;
      }
      const fmt = v => (d.step < 1 ? Number(v).toFixed(2) : String(v));
      box.append(rangeRow(d.label, p[d.key], d.min, d.max, d.step, v => { p[d.key] = v; savePreset(); generateMap(); }, fmt));
    }
  }

  function syncTypeUI() {
    $('#mapType').value = S.type;
    $('#btnAddTerrain').hidden = C.isWallType(S.type);
    S.terrainSel = Math.min(S.terrainSel, cfg().terrains.length - 1);
    S.objectSel = Math.min(S.objectSel, Math.max(0, cfg().objects.length - 1));
    renderParams();
    renderHillBox();
    renderTerrainList();
    renderBiomeList();
    renderPathList();
    renderObjectList();
    $('#pathPanel').hidden = !hasPaths();
    for (const b of document.querySelectorAll('#toolSeg button')) {
      if (b.dataset.tool === 'level') b.hidden = !hasHills();
      if (b.dataset.tool === 'path') b.hidden = !hasPaths();
    }
    if ((S.tool === 'level' && !hasHills()) || (S.tool === 'path' && !hasPaths())) S.tool = 'terrain';
    syncToolButtons();
  }

  // ---------------------------------------------------------------------------
  // Tebing & tangga
  // ---------------------------------------------------------------------------
  function renderHillBox() {
    const box = $('#hillBox');
    box.innerHTML = '';
    const c = cfg();
    if (!hasHills() || !c.hill) return;
    const row = (label, thumb, extra) => el('div', { class: 'tile-row' }, thumb, el('div', { class: 'grow' }, el('div', null, label), extra));
    const hillThumb = makeThumb(c.hill.tile, '#8b6b45');
    hillThumb.addEventListener('click', () => openPicker('wall', c.hill.tile, t => { c.hill.tile = t; savePreset(); renderHillBox(); prepAndRender(); }));
    const stairThumb = makeThumb(c.stairs && c.stairs.tile, '#b08a5a');
    stairThumb.addEventListener('click', () => openPicker('stairs', c.stairs && c.stairs.tile, t => {
      c.stairs = c.stairs || { tile: null };
      c.stairs.tile = t;
      savePreset();
      renderHillBox();
      prepAndRender();
    }));
    box.append(el('h3', null, 'Bukit bertebing'),
      row('Atap tebing (dinding otomatis)', hillThumb,
        el('span', { class: 'muted small' }, labelOf(c.hill.tile) || (P.fs ? 'klik gambar untuk memilih' : 'buka proyek untuk memilih'))),
      row('Tangga di tebing', stairThumb, el('span', { class: 'muted small' }, labelOf(c.stairs && c.stairs.tile) || '—')),
      el('label', null, 'Tanah dasar di atas bukit',
        terrainSelect(c.hill.base, id => { c.hill.base = id; savePreset(); prepAndRender(); }, null, t => !t.block && !t.overlay && t.rule.mode !== 'path')));
  }

  // ---------------------------------------------------------------------------
  // Biome
  // ---------------------------------------------------------------------------
  function renderBiomeList() {
    const box = $('#biomeList');
    box.innerHTML = '';
    const B = cfg().biomes;
    B.forEach((b, i) => {
      const active = S.tool === 'biome' && S.biomeSel === i;
      const color = el('input', { type: 'color', value: b.color, title: 'Warna penanda biome', onclick: stop, onchange: e => { b.color = e.target.value; savePreset(); renderAll(); } });
      const name = el('input', { class: 'name', value: b.name, onclick: stop, onchange: e => { b.name = e.target.value; savePreset(); renderObjectList(); renderTerrainList(); } });
      const del = B.length > 1 ? el('button', { title: 'Hapus biome', onclick: e => { stop(e); deleteBiome(i); } }, '✕') : null;
      const head = el('div', { class: 'item-head', onclick: () => { S.tool = 'biome'; S.biomeSel = i; syncTools(); } }, color, name, del);
      const body = el('div', { class: 'item-body' },
        rangeRow('Porsi area (saat Generate)', b.share == null ? 1 : b.share, 0.1, 3, 0.1, v => { b.share = v; savePreset(); generateMap(); }, v => Number(v).toFixed(1)));
      box.append(el('div', { class: 'item' + (active ? ' active' : '') }, head, body));
    });
    $('#showBiome').checked = S.showBiome;
  }
  function addBiome() {
    const B = cfg().biomes;
    B.push({ id: C.uid(), name: 'Biome ' + (B.length + 1), color: randomColor(), share: 1 });
    savePreset();
    S.biomeSel = B.length - 1;
    S.tool = 'biome';
    syncTools();
    toast('Biome baru ditambahkan. Lukis di peta, atau klik Generate agar terbagi otomatis.', 'info');
  }
  function deleteBiome(i) {
    const B = cfg().biomes;
    const gone = B[i];
    if (!confirm(`Hapus biome "${gone.name}"? Objek/terrain yang terikat padanya akan berlaku di semua biome.`)) return;
    B.splice(i, 1);
    for (let k = 0; k < S.biome.length; k++) { if (S.biome[k] === i) S.biome[k] = 0; else if (S.biome[k] > i) S.biome[k]--; }
    for (const o of cfg().objects) if (o.biome === gone.id) o.biome = '';
    for (const t of cfg().terrains) if (t.rule.biome === gone.id) t.rule.biome = '';
    S.biomeSel = Math.min(S.biomeSel, B.length - 1);
    clearHistory();
    savePreset();
    renderBiomeList();
    renderObjectList();
    renderAll();
  }
  function biomeSelect(selected, onChange) {
    const s = el('select', { onchange: e => onChange(e.target.value), onclick: stop }, el('option', { value: '' }, 'Semua biome'));
    for (const b of cfg().biomes) s.append(el('option', { value: b.id }, b.name));
    s.value = selected || '';
    return s;
  }

  // ---------------------------------------------------------------------------
  // Jalan & titik arah
  // ---------------------------------------------------------------------------
  function renderPathList() {
    const box = $('#pathList');
    if (!box) return;
    box.innerHTML = '';
    if (!hasPaths()) return;
    if (!S.paths.length) box.append(el('p', { class: 'hint' }, 'Belum ada jalan. Klik "+ Jalan baru", lalu klik peta untuk menaruh titik arah.'));
    S.paths.forEach((p, i) => {
      const active = S.tool === 'path' && S.pathSel === i;
      const touch = () => { p.auto = false; };
      const name = el('input', { class: 'name', value: p.name, onclick: stop, onchange: e => { p.name = e.target.value; touch(); } });
      const tag = el('span', { class: 'tag', title: p.auto ? 'Dibuat otomatis; akan diganti saat Generate kecuali Anda mengubahnya' : 'Jalan manual; tetap ada saat Generate' }, p.auto ? 'otomatis' : `${(p.points || []).length} titik`);
      const del = el('button', { title: 'Hapus jalan', onclick: e => { stop(e); pushUndo(); S.paths.splice(i, 1); S.pathSel = Math.max(0, Math.min(S.pathSel, S.paths.length - 1)); prepAndRender(); renderPathList(); } }, '✕');
      const head = el('div', { class: 'item-head', onclick: () => { S.tool = 'path'; S.pathSel = i; syncTools(); } }, name, tag, del);
      const stairTile = p.stairs ? { id: p.stairs } : null;
      const stairThumb = makeThumb(stairTile || (cfg().stairs && cfg().stairs.tile), '#b08a5a');
      stairThumb.addEventListener('click', e => { stop(e); openPicker('stairs', stairTile, t => { p.stairs = t ? t.id : 0; touch(); prepAndRender(); renderPathList(); }); });
      const body = el('div', { class: 'item-body' },
        el('label', null, 'Tile jalan', terrainSelect(p.terrain, id => { p.terrain = id; touch(); prepAndRender(); }, null, t => !t.block)),
        el('div', { class: 'tile-row' }, stairThumb, el('div', { class: 'grow' }, el('div', null, 'Tangga'),
          el('span', { class: 'muted small' }, p.stairs ? labelOf(stairTile) || 'khusus' : 'pakai tangga bawaan'))),
        rangeRow('Lebar', p.width || 1, 1, 3, 1, v => { p.width = v; touch(); prepAndRender(); }, String),
        rangeRow('Peluang celah', p.gap || 0, 0, 0.5, 0.01, v => { p.gap = v; touch(); prepAndRender(); }, v => Math.round(v * 100) + '%'),
        el('div', { class: 'row2' },
          el('button', { class: 'subtle', onclick: e => { stop(e); S.tool = 'path'; S.pathSel = i; syncTools(); toast('Klik peta untuk menambah titik arah.', 'info'); } }, '+ Titik arah'),
          el('button', { class: 'subtle', onclick: e => { stop(e); if (!p.points.length) return; pushUndo(); p.points.pop(); touch(); prepAndRender(); renderPathList(); } }, 'Hapus titik terakhir')));
      box.append(el('div', { class: 'item' + (active ? ' active' : '') }, head, body));
    });
  }
  function addPath() {
    const pathT = cfg().terrains.find(t => t.rule.mode === 'path') || cfg().terrains.find(t => !t.block);
    S.paths.push({ id: C.uid(), name: 'Jalan ' + (S.paths.length + 1), auto: false, terrain: pathT ? pathT.id : '', stairs: 0, width: 1, gap: 0, points: [] });
    S.pathSel = S.paths.length - 1;
    S.tool = 'path';
    syncTools();
    toast('Klik peta untuk menaruh titik arah (minimal 2). Jalan dicari otomatis dan memakai tangga di tebing.', 'info', 7000);
  }
  function addWaypoint(c) {
    if (!S.paths.length) addPath();
    const p = S.paths[S.pathSel];
    pushUndo();
    p.points.push([c.x, c.y]);
    p.auto = false;
    prepAndRender();
    renderPathList();
    if (p.points.length >= 2 && !S.routes.terrain.some(v => v >= 0) && !S.routes.stairs.some(Boolean)) {
      toast('Rute belum ditemukan. Pastikan titik tidak di air, dan tebing punya jalur naik.', 'warn');
    }
  }

  // ---------------------------------------------------------------------------
  // Panel terrain
  // ---------------------------------------------------------------------------
  function rulesChanged() {
    $('#ruleHint').hidden = false;
    savePreset();
  }
  function lookChanged() {
    savePreset();
    rebuild();
    renderAll();
    renderTerrainList();
  }
  function terrainSelect(selected, onChange, excludeId, filter) {
    const s = el('select', { onchange: e => onChange(e.target.value), onclick: stop });
    for (const t of cfg().terrains) {
      if (t.id === excludeId || (filter && !filter(t))) continue;
      s.append(el('option', { value: t.id }, t.name));
    }
    s.value = selected || '';
    return s;
  }

  function renderTerrainList() {
    const box = $('#terrainList');
    box.innerHTML = '';
    const T = cfg().terrains, wallType = C.isWallType(S.type);
    T.forEach((t, i) => {
      const active = S.tool === 'terrain' && S.terrainSel === i;
      const thumb = makeThumb(t.tile, t.color);
      thumb.addEventListener('click', e => {
        stop(e);
        const kind = wallType ? (t.rule.mode === 'wall' ? 'wall' : 'floor') : 'terrain';
        openPicker(kind, t.tile, tile => { t.tile = tile; lookChanged(); });
      });
      const color = el('input', { type: 'color', value: t.color, title: 'Warna pratinjau', onclick: stop, onchange: e => { t.color = e.target.value; lookChanged(); } });
      const name = el('input', { class: 'name', value: t.name, onclick: stop, onchange: e => { t.name = e.target.value; savePreset(); renderObjectList(); } });
      let tag = null;
      if (wallType) tag = el('span', { class: 'tag' }, t.rule.mode === 'wall' ? 'dinding' : 'lantai');
      else if (t.rule.mode === 'path') tag = el('span', { class: 'tag' }, 'jalan');
      else if (t.overlay) tag = el('span', { class: 'tag', title: 'Digambar di lapisan atas' }, 'overlay');
      const warn = P.fs && !t.tile ? el('span', { class: 'tag warn', title: 'Belum ada tile, jadi akan kosong saat diekspor' }, 'tanpa tile') : null;
      const gear = el('button', { title: 'Pengaturan', onclick: e => { stop(e); S.open.has(t.id) ? S.open.delete(t.id) : S.open.add(t.id); renderTerrainList(); } }, S.open.has(t.id) ? '▴' : '▾');
      const del = wallType ? null : el('button', { title: 'Hapus terrain', onclick: e => { stop(e); deleteTerrain(i); } }, '✕');
      const head = el('div', { class: 'item-head', onclick: () => { S.tool = 'terrain'; S.terrainSel = i; syncTools(); } }, thumb, color, name, tag, warn, gear, del);
      const item = el('div', { class: 'item' + (active ? ' active' : '') }, head);
      if (S.open.has(t.id)) item.append(terrainBody(t));
      box.append(item);
    });
  }

  function terrainBody(t) {
    const T = cfg().terrains, wallType = C.isWallType(S.type);
    const body = el('div', { class: 'item-body' });
    if (!wallType) {
      const mode = el('select', {
        onchange: e => {
          const m = e.target.value;
          const firstHeight = T.find(o => o !== t && o.rule.mode === 'height') || T.find(o => o !== t);
          if (m === 'height') t.rule = { mode: 'height', min: 0.5 };
          else if (m === 'patch') t.rule = { mode: 'patch', parent: firstHeight ? firstHeight.id : null, threshold: 0.65, scale: 12 };
          else t.rule = { mode: 'path' };
          rulesChanged();
          renderTerrainList();
        },
      },
      el('option', { value: 'height' }, 'Pita ketinggian'),
      el('option', { value: 'patch' }, 'Petak di atas terrain lain'),
      el('option', { value: 'path' }, 'Jalan (menghubungkan titik)'));
      mode.value = t.rule.mode;
      body.append(el('label', null, 'Cara muncul', mode));
      if (t.rule.mode === 'height') {
        body.append(rangeRow('Mulai dari ketinggian (persentil)', t.rule.min, 0, 1, 0.01,
          v => { t.rule.min = v; rulesChanged(); }, v => Math.round(v * 100) + '%'));
      } else if (t.rule.mode === 'patch') {
        body.append(el('label', null, 'Muncul di atas', terrainSelect(t.rule.parent, id => { t.rule.parent = id; rulesChanged(); }, t.id)));
        body.append(rangeRow('Ambang (makin tinggi makin jarang)', t.rule.threshold, 0.3, 0.95, 0.01,
          v => { t.rule.threshold = v; rulesChanged(); }, v => v.toFixed(2)));
        body.append(rangeRow('Ukuran petak', t.rule.scale || 12, 3, 60, 1, v => { t.rule.scale = v; rulesChanged(); }, String));
        body.append(el('label', null, 'Hanya di biome', biomeSelect(t.rule.biome, id => { t.rule.biome = id; rulesChanged(); })));
      } else {
        body.append(el('p', { class: 'hint' }, 'Jumlah dan lebar jalan diatur di panel Generator.'));
      }
      const ov = el('input', {
        type: 'checkbox', checked: t.overlay,
        onchange: e => {
          t.overlay = e.target.checked;
          if (t.overlay && !t.base) { const b = T.find(o => o !== t && !o.overlay); t.base = b ? b.id : null; }
          lookChanged();
        },
      });
      body.append(el('label', { class: 'check', title: 'Untuk tile transparan (hutan, bukit, semak) yang ditaruh di lapisan atas, di atas tanah' }, ov, 'Lapisan atas (overlay)'));
      if (t.overlay) {
        body.append(el('label', null, 'Tanah di bawahnya', terrainSelect(t.base, id => { t.base = id; lookChanged(); }, t.id, o => !o.overlay)));
      }
      body.append(el('label', { class: 'check' },
        el('input', { type: 'checkbox', checked: t.block, onchange: e => { t.block = e.target.checked; rulesChanged(); } }),
        'Tidak bisa dilewati jalan'));
    }
    body.append(el('label', null, 'Region ID (0–255, mis. untuk encounter)',
      el('input', { type: 'number', min: 0, max: 255, value: t.region | 0, onchange: e => { t.region = clamp(parseInt(e.target.value, 10) || 0, 0, 255); e.target.value = t.region; lookChanged(); } })));
    return body;
  }

  function addTerrain() {
    const T = cfg().terrains;
    const parent = T.find(o => o.rule.mode === 'height' && !o.block) || T[0];
    T.push({
      id: C.uid(), name: 'Terrain baru', color: randomColor(), tile: null, overlay: false, base: null, block: false, region: 0,
      rule: { mode: 'patch', parent: parent ? parent.id : null, threshold: 0.75, scale: 10 },
    });
    S.open.add(T[T.length - 1].id);
    rulesChanged();
    renderTerrainList();
  }

  function deleteTerrain(i) {
    const T = cfg().terrains;
    if (T.length <= 1) return;
    const gone = T[i];
    if (!confirm(`Hapus terrain "${gone.name}"? Sel yang memakainya akan diganti.`)) return;
    const repl = (gone.overlay && gone.base && T.find(o => o.id === gone.base)) ||
      T.find(o => o !== gone && o.rule.mode === 'height') || T.find(o => o !== gone);
    T.splice(i, 1);
    const ri = T.indexOf(repl);
    for (let k = 0; k < S.grid.length; k++) {
      if (S.grid[k] === i) S.grid[k] = ri;
      else if (S.grid[k] > i) S.grid[k]--;
    }
    for (const t of T) {
      if (t.rule.parent === gone.id) t.rule.parent = repl.id;
      if (t.base === gone.id) { t.base = null; t.overlay = false; }
    }
    for (const o of cfg().objects) if (o.terrain === gone.id) o.terrain = repl.id;
    S.terrainSel = Math.min(S.terrainSel, T.length - 1);
    clearHistory();
    savePreset();
    prepAndRender();
    renderTerrainList();
    renderObjectList();
  }

  // ---------------------------------------------------------------------------
  // Panel objek
  // ---------------------------------------------------------------------------
  function renderObjectList() {
    const box = $('#objectList');
    box.innerHTML = '';
    const O = cfg().objects;
    if (!O.length) box.append(el('p', { class: 'hint' }, 'Belum ada objek. Tambahkan pohon, batu, dan lain-lain dari tileset B–E.'));
    O.forEach((o, i) => {
      const active = S.tool === 'object' && S.objectSel === i;
      const tiles = C.objTiles(o);
      const thumb = makeObjThumb(tiles);
      thumb.addEventListener('click', e => {
        stop(e);
        openPicker('object', tiles, t => {
          o.tiles = t;
          delete o.tileId;
          rescatter(false);
          renderObjectList();
        });
      });
      const name = el('input', { class: 'name', value: o.name, onclick: stop, onchange: e => { o.name = e.target.value; savePreset(); } });
      const size = tiles ? el('span', { class: 'tag', title: 'Ukuran objek (lebar × tinggi tile)' }, `${tiles[0].length}×${tiles.length}`) : null;
      const warn = P.fs && !tiles ? el('span', { class: 'tag warn' }, 'tanpa tile') : null;
      const del = el('button', {
        title: 'Hapus objek dari daftar',
        onclick: e => {
          stop(e);
          O.splice(i, 1);
          S.objectSel = Math.min(S.objectSel, Math.max(0, O.length - 1));
          rescatter(false);
          renderObjectList();
        },
      }, '✕');
      const head = el('div', { class: 'item-head', onclick: () => { S.tool = 'object'; S.objectSel = i; syncTools(); } }, thumb, name, size, warn, del);
      const body = el('div', { class: 'item-body' },
        el('div', { class: 'row2' },
          el('label', null, 'Di atas', anyTerrainSelect(o.terrain, id => { o.terrain = id; rescatter(false); })),
          el('label', null, 'Biome', biomeSelect(o.biome, id => { o.biome = id; rescatter(false); }))),
        rangeRow('Kepadatan', o.density, 0, 0.5, 0.005, v => { o.density = v; rescatter(false); }, v => (v * 100).toFixed(1) + '%'),
        joinRow(o, tiles));
      box.append(el('div', { class: 'item' + (active ? ' active' : '') }, head, body));
    });
  }

  function rescatter(fresh) {
    pushUndo();
    const s = st();
    C.scatterObjects(s, C.makeRng(S.seed + '|objek' + (fresh ? '|' + Date.now() : '')));
    savePreset();
    rebuild();
    renderAll();
  }

  function addObject() {
    const T = cfg().terrains;
    const wallType = C.isWallType(S.type);
    const target = wallType ? T[C.roleIdx(T, 'floor')] : (T.find(t => t.rule.mode === 'height' && !t.block) || T[0]);
    cfg().objects.push({ id: C.uid(), name: 'Objek baru', tiles: null, terrain: target.id, density: 0.02 });
    savePreset();
    renderObjectList();
    if (P.fs) {
      const o = cfg().objects[cfg().objects.length - 1];
      openPicker('object', null, t => { o.tiles = t; rescatter(false); renderObjectList(); });
    }
  }

  function anyTerrainSelect(selected, onChange) {
    const s = terrainSelect(selected, onChange);
    s.prepend(el('option', { value: '' }, 'Semua daratan'));
    s.value = selected || '';
    return s;
  }

  /** Varian rapat: dipakai otomatis saat pucuk objek menimpa alas objek lain (hutan lebat). */
  function joinRow(o, tiles) {
    if (!tiles || tiles.length < 2) return null;
    const thumb = makeObjThumb(o.join);
    thumb.title = 'Varian rapat: dipakai saat pohon saling tumpuk. Ukurannya harus sama dengan objek.';
    thumb.addEventListener('click', e => {
      stop(e);
      openPicker('object', o.join, t => {
        if (t && (t.length !== tiles.length || t[0].length !== tiles[0].length)) {
          toast(`Ukuran varian rapat harus ${tiles[0].length}×${tiles.length} tile.`, 'warn');
          return;
        }
        o.join = t;
        rescatter(false);
        renderObjectList();
      });
    });
    const clear = o.join ? el('button', { class: 'subtle', onclick: e => { stop(e); o.join = null; rescatter(false); renderObjectList(); } }, 'Hapus') : null;
    return el('div', { class: 'tile-row' }, thumb, el('div', { class: 'grow' }, el('div', null, 'Varian rapat (opsional)'),
      el('span', { class: 'muted small' }, o.join ? 'aktif saat pohon bertumpuk' : 'tidak ada')), clear);
  }

  /** Gambar mini objek multi-tile, diskalakan agar muat 32×32. */
  function makeObjThumb(tiles) {
    const c = el('canvas', { width: 32, height: 32, class: 'thumb' });
    const g = c.getContext('2d');
    g.imageSmoothingEnabled = false;
    g.fillStyle = '#2a2e37';
    g.fillRect(0, 0, 32, 32);
    if (tiles && P.fs) {
      const h = tiles.length, w = tiles[0].length;
      const cell = Math.floor(32 / Math.max(w, h));
      const ox = Math.floor((32 - cell * w) / 2), oy = Math.floor((32 - cell * h) / 2);
      tiles.forEach((row, r) => row.forEach((id, k) => {
        const t = id ? getTile(id) : null;
        if (t) g.drawImage(t, ox + k * cell, oy + r * cell, cell, cell);
      }));
    }
    c.title = 'Klik untuk memilih tile objek (klik satu bagian = objek utuh terpilih otomatis)';
    return c;
  }

  // ---------------------------------------------------------------------------
  // Pemilih tile
  // ---------------------------------------------------------------------------
  const PICK_TABS = {
    terrain: [[0, 'A1 · Air'], [1, 'A2 · Tanah'], [3, 'A4 · Atap'], [4, 'A5']],
    floor: [[1, 'A2 · Lantai'], [4, 'A5'], [0, 'A1 · Air']],
    wall: [[3, 'A4 · Atap dinding']],
    object: [[5, 'B'], [6, 'C'], [7, 'D'], [8, 'E'], [4, 'A5']],
    stairs: [[4, 'A5'], [5, 'B'], [6, 'C'], [7, 'D'], [8, 'E']],
  };
  const range = (a, b) => Array.from({ length: b - a }, (_, i) => a + i);

  function openPicker(kind, current, onPick) {
    if (!P.fs) { toast('Buka proyek RPG Maker dulu untuk memilih tile dari tileset.', 'warn'); return; }
    const tabs = PICK_TABS[kind].filter(([s]) => P.images[s]);
    if (!tabs.length) { toast('Tileset ini tidak punya gambar yang cocok untuk pilihan ini.', 'warn'); return; }
    const dlg = $('#pickerDlg');
    const isObj = kind === 'object';
    $('#pickerTitle').textContent = isObj ? 'Pilih objek (klik = objek utuh, Shift+klik = 1 tile, seret = area)'
      : kind === 'wall' ? 'Pilih atap dinding/tebing (sisinya otomatis)'
      : kind === 'stairs' ? 'Pilih tile tangga' : 'Pilih tile terrain';
    let curSet = -1;
    if (isObj && current) {
      const first = current.flat().find(Boolean);
      if (first) curSet = C.setOfTile({ id: first });
    } else if (current) {
      curSet = C.setOfTile(current);
    }
    let active = tabs.some(([s]) => s === curSet) ? curSet : tabs[0][0];
    const pick = tile => { dlg.close(); onPick(tile); };
    const draw = () => {
      const tb = $('#pickerTabs');
      tb.innerHTML = '';
      for (const [s, label] of tabs) {
        tb.append(el('button', { class: s === active ? 'on' : '', onclick: () => { active = s; draw(); } }, `${label} (${P.names[s]})`));
      }
      if (isObj) renderObjectSheet(active, current, pick);
      else renderPickerBody(active, current, pick);
    };
    $('#pickerNone').onclick = () => pick(null);
    $('#pickerNone').hidden = isObj;
    $('#pickerUse').hidden = !isObj;
    draw();
    dlg.showModal();
  }

  // --- Deteksi transparansi untuk memilih objek multi-tile utuh ---
  const alphaCache = new Map();
  function alphaOf(set) {
    if (alphaCache.has(set)) return alphaCache.get(set);
    const img = P.images[set];
    const c = document.createElement('canvas');
    c.width = img.width;
    c.height = img.height;
    const g = c.getContext('2d', { willReadFrequently: true });
    g.drawImage(img, 0, 0);
    const a = { w: img.width, h: img.height, d: g.getImageData(0, 0, img.width, img.height).data };
    alphaCache.set(set, a);
    return a;
  }
  const opaqueAt = (a, x, y) => a.d[(y * a.w + x) * 4 + 3] > 16;
  /** Porsi piksel tidak transparan pada sebuah tile (0..1). */
  function tileCoverage(set, col, row) {
    const a = alphaOf(set), ts = P.tileSize;
    let n = 0, total = 0;
    for (let y = row * ts; y < (row + 1) * ts; y += 2) {
      for (let x = col * ts; x < (col + 1) * ts; x += 2) { total++; if (opaqueAt(a, x, y)) n++; }
    }
    return n / total;
  }
  const tileIsEmpty = (set, col, row) => tileCoverage(set, col, row) < 0.005;
  /** Dua tile bersebelahan dianggap satu objek bila piksel di tepi pertemuannya sama-sama tidak transparan. */
  function tilesJoined(set, c1, r1, c2, r2) {
    const a = alphaOf(set), ts = P.tileSize;
    let n = 0;
    for (let k = 0; k < ts; k++) {
      if (r2 > r1) { if (opaqueAt(a, c1 * ts + k, r2 * ts - 1) && opaqueAt(a, c1 * ts + k, r2 * ts)) n++; }
      else if (opaqueAt(a, c2 * ts - 1, r1 * ts + k) && opaqueAt(a, c2 * ts, r1 * ts + k)) n++;
    }
    return n >= Math.max(2, ts * 0.12);
  }
  function smartSelect(set, col, row, cols, rows) {
    if (tileIsEmpty(set, col, row)) return null;
    // Tile yang tertutup penuh (mis. penyambung daun hutan) tidak ikut terseret, kecuali titik awalnya sendiri juga penuh
    const solidStart = tileCoverage(set, col, row) > 0.97;
    const half = set >= 5 ? (col < 8 ? [0, 7] : [8, cols - 1]) : [0, cols - 1];
    // Nama tile dari file .txt tileset: objek berbeda yang kebetulan bersentuhan (mis. bongkahan es di atas pilar) tidak digabung
    const nameAt = (c, r) => labelOf({ id: C.normalTileId(set, c, r) });
    const seen = new Set([col + ',' + row]);
    const queue = [[col, row]];
    let c0 = col, c1 = col, r0 = row, r1 = row;
    while (queue.length) {
      const [c, r] = queue.shift();
      const nbs = [[c, r - 1, c, r - 1, c, r], [c, r + 1, c, r, c, r + 1], [c - 1, r, c - 1, r, c, r], [c + 1, r, c, r, c + 1, r]];
      for (const [nc, nr, ac, ar, bc, br] of nbs) {
        if (nc < half[0] || nc > half[1] || nr < 0 || nr >= rows || seen.has(nc + ',' + nr)) continue;
        if (Math.max(c1, nc) - Math.min(c0, nc) >= 6 || Math.max(r1, nr) - Math.min(r0, nr) >= 6) continue;
        if (tileIsEmpty(set, nc, nr) || !tilesJoined(set, ac, ar, bc, br)) continue;
        if (!solidStart && tileCoverage(set, nc, nr) > 0.97) continue;
        const na = nameAt(ac, ar), nb = nameAt(bc, br);
        if (na && nb && na !== nb) continue;
        seen.add(nc + ',' + nr);
        queue.push([nc, nr]);
        c0 = Math.min(c0, nc); c1 = Math.max(c1, nc); r0 = Math.min(r0, nr); r1 = Math.max(r1, nr);
      }
    }
    return { c0, r0, c1, r1 };
  }

  function renderObjectSheet(set, current, pick) {
    const body = $('#pickerBody'), hover = $('#pickerHover'), use = $('#pickerUse');
    body.innerHTML = '';
    const img = P.images[set], ts = P.tileSize, cell = 32;
    const cols = Math.floor(img.width / ts), rows = Math.floor(img.height / ts);
    const c = el('canvas', { width: cols * cell, height: rows * cell });
    const g = c.getContext('2d');
    let sel = null, dragFrom = null, moved = false;
    if (current) {
      const pos = current.flat().filter(Boolean).map(id => C.tileSource(id)).filter(s => s && s.set === set);
      if (pos.length) {
        sel = { c0: Math.min(...pos.map(p => p.sx)), r0: Math.min(...pos.map(p => p.sy)), c1: Math.max(...pos.map(p => p.sx)), r1: Math.max(...pos.map(p => p.sy)) };
      }
    }
    const describe = () => {
      if (!sel) { use.disabled = true; hover.textContent = 'Klik bagian mana saja dari objek.'; return; }
      use.disabled = false;
      const name = labelOf({ id: C.normalTileId(set, sel.c0, sel.r1) });
      hover.textContent = `${name || 'Objek'} — ${sel.c1 - sel.c0 + 1}×${sel.r1 - sel.r0 + 1} tile. Salah tebak? Shift+klik = 1 tile, seret = pilih area.`;
    };
    const redraw = () => {
      g.imageSmoothingEnabled = false;
      g.clearRect(0, 0, c.width, c.height);
      g.drawImage(img, 0, 0, cols * ts, rows * ts, 0, 0, cols * cell, rows * cell);
      if (!sel) return;
      g.fillStyle = 'rgba(79,140,255,0.18)';
      g.fillRect(sel.c0 * cell, sel.r0 * cell, (sel.c1 - sel.c0 + 1) * cell, (sel.r1 - sel.r0 + 1) * cell);
      g.strokeStyle = '#f0b44c';
      g.lineWidth = 3;
      g.strokeRect(sel.c0 * cell + 1.5, sel.r0 * cell + 1.5, (sel.c1 - sel.c0 + 1) * cell - 3, (sel.r1 - sel.r0 + 1) * cell - 3);
    };
    const cellOf = e => {
      const r = c.getBoundingClientRect();
      return [clamp(Math.floor((e.clientX - r.left) / cell), 0, cols - 1), clamp(Math.floor((e.clientY - r.top) / cell), 0, rows - 1)];
    };
    const build = () => {
      const tiles = [];
      for (let r = sel.r0; r <= sel.r1; r++) {
        const row = [];
        for (let k = sel.c0; k <= sel.c1; k++) {
          const id = C.normalTileId(set, k, r);
          row.push(id > 0 && !tileIsEmpty(set, k, r) ? id : 0);
        }
        tiles.push(row);
      }
      while (tiles.length > 1 && tiles[tiles.length - 1].every(v => !v)) tiles.pop();
      while (tiles.length > 1 && tiles[0].every(v => !v)) tiles.shift();
      return tiles.some(r => r.some(Boolean)) ? tiles : null;
    };
    const commit = () => {
      if (!sel) return;
      const tiles = build();
      if (!tiles) { toast('Area yang dipilih kosong (transparan).', 'warn'); return; }
      pick(tiles);
    };
    c.addEventListener('mousedown', e => { dragFrom = cellOf(e); moved = false; });
    c.addEventListener('mousemove', e => {
      if (!dragFrom) return;
      const [k, r] = cellOf(e);
      if (k === dragFrom[0] && r === dragFrom[1] && !moved) return;
      moved = true;
      sel = { c0: Math.min(k, dragFrom[0]), r0: Math.min(r, dragFrom[1]), c1: Math.max(k, dragFrom[0]), r1: Math.max(r, dragFrom[1]) };
      redraw();
      describe();
    });
    c.addEventListener('mouseup', e => {
      if (!dragFrom) return;
      if (!moved) {
        const [k, r] = cellOf(e);
        // Shift+klik = tepat satu tile, tanpa deteksi otomatis
        sel = e.shiftKey ? (tileIsEmpty(set, k, r) ? null : { c0: k, r0: r, c1: k, r1: r }) : smartSelect(set, k, r, cols, rows);
        if (!sel) toast('Tile itu kosong (transparan).', 'warn');
      }
      dragFrom = null;
      redraw();
      describe();
    });
    c.addEventListener('dblclick', commit);
    use.onclick = commit;
    redraw();
    describe();
    body.append(el('div', { class: 'sheet-wrap' }, c));
  }

  function renderPickerBody(set, current, pick) {
    const body = $('#pickerBody'), hover = $('#pickerHover');
    body.innerHTML = '';
    hover.textContent = '';
    if (set <= 3) {
      const kinds = set === 0 ? [0, 1, 2, 3, 4, 6, 8, 10, 12, 14]
        : set === 1 ? range(16, 48)
        : set === 2 ? range(48, 80)
        : range(80, 128).filter(C.isWallTopKind);
      const grid = el('div', { class: 'kind-grid' });
      for (const k of kinds) {
        const t = getTile(C.autoId(k, C.thumbShape(k)));
        if (!t) continue;
        const c = el('canvas', { width: 48, height: 48 });
        const g = c.getContext('2d');
        g.imageSmoothingEnabled = false;
        g.drawImage(t, 0, 0, 48, 48);
        if (current && current.auto === k) c.classList.add('sel');
        c.title = labelOf({ auto: k }) || 'Autotile ' + k;
        c.addEventListener('mouseenter', () => { hover.textContent = c.title; });
        c.addEventListener('click', () => pick({ auto: k }));
        grid.append(c);
      }
      body.append(grid);
      return;
    }
    const img = P.images[set], ts = P.tileSize, cell = 32;
    const cols = Math.floor(img.width / ts), rows = Math.floor(img.height / ts);
    const c = el('canvas', { width: cols * cell, height: rows * cell });
    const g = c.getContext('2d');
    g.imageSmoothingEnabled = false;
    g.drawImage(img, 0, 0, cols * ts, rows * ts, 0, 0, cols * cell, rows * cell);
    if (current && current.id != null && C.setOfTile(current) === set) {
      const src = C.tileSource(current.id);
      g.strokeStyle = '#f0b44c';
      g.lineWidth = 3;
      g.strokeRect(src.sx * cell + 1.5, src.sy * cell + 1.5, cell - 3, cell - 3);
    }
    const idAt = e => {
      const r = c.getBoundingClientRect();
      const col = Math.floor((e.clientX - r.left) / cell), row = Math.floor((e.clientY - r.top) / cell);
      if (col < 0 || row < 0 || col >= cols || row >= rows) return -1;
      return C.normalTileId(set, col, row);
    };
    c.addEventListener('mousemove', e => {
      const id = idAt(e);
      hover.textContent = id > 0 ? `${labelOf({ id }) || 'Tile'} (ID ${id})` : '';
    });
    c.addEventListener('click', e => {
      const id = idAt(e);
      if (id <= 0) { toast('Tile pertama di lembar B kosong (transparan). Pilih tile lain.', 'warn'); return; }
      pick({ id });
    });
    body.append(el('div', { class: 'sheet-wrap' }, c));
  }

  // ---------------------------------------------------------------------------
  // Kuas & kanvas
  // ---------------------------------------------------------------------------
  function syncToolButtons() {
    for (const b of document.querySelectorAll('#toolSeg button')) b.classList.toggle('on', b.dataset.tool === S.tool);
    $('#levelWrap').hidden = S.tool !== 'level';
  }
  function syncTools() {
    syncToolButtons();
    renderTerrainList();
    renderBiomeList();
    renderPathList();
    renderObjectList();
    renderAll();
  }
  function setRadius(r) {
    S.radius = clamp(r, 1, 12);
    $('#radius').value = S.radius;
    $('#radiusVal').textContent = S.radius;
  }
  function cellAt(e) {
    const r = cv.getBoundingClientRect();
    const x = Math.floor((e.clientX - r.left) / S.zoom), y = Math.floor((e.clientY - r.top) / S.zoom);
    if (x < 0 || y < 0 || x >= S.width || y >= S.height) return null;
    return { x, y };
  }
  function linePoints(a, b) {
    const pts = [];
    let x = a.x, y = a.y;
    const dx = Math.abs(b.x - x), dy = -Math.abs(b.y - y), sx = x < b.x ? 1 : -1, sy = y < b.y ? 1 : -1;
    let err = dx + dy;
    for (;;) {
      pts.push({ x, y });
      if (x === b.x && y === b.y) break;
      const e2 = 2 * err;
      if (e2 >= dy) { err += dy; x += sx; }
      if (e2 <= dx) { err += dx; y += sy; }
    }
    return pts;
  }

  let painting = false, last = null, lastPlaced = null;
  function applyAt(p, box) {
    const W = S.width, H = S.height;
    const mark = (x, y) => { box[0] = Math.min(box[0], x); box[1] = Math.min(box[1], y); box[2] = Math.max(box[2], x); box[3] = Math.max(box[3], y); };
    const s = st();
    const clearAt = i => { const b = C.removeObjectsAt(s, i); if (b) { mark(b[0], b[1]); mark(b[2], b[3]); } };
    if (S.tool === 'object') {
      const o = cfg().objects[S.objectSel];
      if (!o) return;
      const tiles = C.objTiles(o);
      if (!tiles) { toast('Objek ini belum punya tile.', 'warn'); painting = false; return; }
      if (lastPlaced && Math.abs(lastPlaced.x - p.x) < tiles[0].length && Math.abs(lastPlaced.y - p.y) < tiles.length) return;
      // Kosongkan area tujuan, lalu taruh objek utuh (alas kiri-bawah di sel yang diklik)
      for (let r = 0; r < tiles.length; r++) for (let k = 0; k < tiles[r].length; k++) {
        const x = p.x + k, y = p.y - (tiles.length - 1) + r;
        if (tiles[r][k] && x >= 0 && y >= 0 && x < W && y < H) clearAt(y * W + x);
      }
      if (!C.canPlace(s, tiles, p.x, p.y, -1, C.objectBlocker(s, false))) return;
      C.placeObject(s, tiles, p.x, p.y);
      lastPlaced = p;
      mark(p.x, p.y - tiles.length + 1);
      mark(p.x + tiles[0].length - 1, p.y);
      return;
    }
    const r = S.radius - 1;
    for (let dy = -r; dy <= r; dy++) {
      for (let dx = -r; dx <= r; dx++) {
        if (dx * dx + dy * dy > r * r + r) continue;
        const x = p.x + dx, y = p.y + dy;
        if (x < 0 || y < 0 || x >= W || y >= H) continue;
        const i = y * W + x;
        if (S.tool === 'biome') { S.biome[i] = S.biomeSel; mark(x, y); continue; }
        if (S.tool === 'level') { if (S.level[i] === S.levelSel) continue; S.level[i] = S.levelSel; }
        clearAt(i);
        if (S.tool === 'terrain') S.grid[i] = S.terrainSel;
        mark(x, y);
      }
    }
  }
  function strokeTo(c) {
    const box = [Infinity, Infinity, -Infinity, -Infinity];
    for (const p of linePoints(last || c, c)) applyAt(p, box);
    last = c;
    if (box[0] === Infinity) return;
    if (S.tool === 'level' || S.tool === 'terrain') S.cliff = C.classifyCliffs(st());
    if (S.tool === 'object' || S.tool === 'erase' || S.tool === 'terrain' || S.tool === 'level') C.refreshJoins(st());
    rebuild();
    const pad = Math.max(C.isWallType(S.type) ? (cfg().params.wallHeight | 0) + 2 : (cfg().params.cliffHeight | 0) + 2, maxObjHeight() + 1);
    renderRegion(box[0] - pad, box[1] - pad, box[2] + pad, box[3] + pad);
  }
  function showHover(c) {
    const info = $('#hoverInfo');
    if (!c) { info.textContent = ''; return; }
    const i = c.y * S.width + c.x, T = cfg().terrains;
    let txt = `${c.x}, ${c.y} · `;
    if (C.isWallType(S.type)) txt += ['lantai', 'sisi dinding', 'atap dinding'][S.built.cls[i]];
    else {
      txt += T[S.grid[i]].name;
      if (S.routes && S.routes.stairs[i]) txt += ' · tangga';
      else if (S.cliff && S.cliff[i]) txt += ' · tebing';
      else if (S.routes && S.routes.terrain[i] >= 0) txt += ' · jalan';
      if (S.level && S.level[i]) txt += ` · tingkat ${S.level[i]}`;
    }
    const B = cfg().biomes;
    if (B.length > 1 && S.biome) txt += ` · ${B[S.biome[i]] ? B[S.biome[i]].name : ''}`;
    const anchor = S.own2[i] || S.own3[i];
    if (anchor) {
      const base = S.deco[anchor - 1];
      const o = cfg().objects.find(o => { const t = C.objTiles(o); return t && t[t.length - 1][0] === base; });
      txt += ` · ${o ? o.name : 'objek'}`;
    }
    info.textContent = txt;
  }

  cv.addEventListener('pointerdown', e => {
    if (e.button !== 0) return;
    const c = cellAt(e);
    if (!c) return;
    if (S.tool === 'path') { addWaypoint(c); return; }
    cv.setPointerCapture(e.pointerId);
    pushUndo();
    painting = true;
    last = null;
    lastPlaced = null;
    strokeTo(c);
  });
  cv.addEventListener('pointermove', e => {
    const c = cellAt(e);
    showHover(c);
    if (painting && c) strokeTo(c);
  });
  cv.addEventListener('pointerleave', () => showHover(null));
  window.addEventListener('pointerup', () => {
    const wasPainting = painting;
    painting = false;
    last = null;
    // Rute jalan bisa berubah karena terrain/tingkat baru: hitung ulang setelah goresan selesai
    if (wasPainting && (S.tool === 'terrain' || S.tool === 'level')) prepAndRender();
  });

  // ---------------------------------------------------------------------------
  // Proyek RPG Maker
  // ---------------------------------------------------------------------------
  function fsFromHandle(dir) {
    return {
      name: dir.name, writable: true,
      async handle(path, create) {
        const parts = path.split('/');
        let d = dir;
        for (const p of parts.slice(0, -1)) d = await d.getDirectoryHandle(p, { create });
        return d.getFileHandle(parts[parts.length - 1], { create });
      },
      async exists(path) { try { await this.handle(path, false); return true; } catch { return false; } },
      async readBlob(path) { return (await this.handle(path, false)).getFile(); },
      async readText(path) { return (await this.readBlob(path)).text(); },
      async writeText(path, text) {
        const fh = await this.handle(path, true);
        const w = await fh.createWritable();
        await w.write(text);
        await w.close();
      },
    };
  }
  function fsFromFiles(files) {
    const map = new Map();
    let name = '';
    for (const f of files) {
      const parts = f.webkitRelativePath.split('/');
      name = name || parts[0];
      map.set(parts.slice(1).join('/'), f);
    }
    return {
      name, writable: false,
      async exists(p) { return map.has(p); },
      async readBlob(p) { const f = map.get(p); if (!f) throw new Error('Tidak ditemukan: ' + p); return f; },
      async readText(p) { return (await this.readBlob(p)).text(); },
      async writeText() { throw new Error('Mode baca saja'); },
    };
  }
  function fsFromUrl(base) {
    base = base.replace(/\/?$/, '/');
    const get = url => new Promise((res, rej) => {
      const x = new XMLHttpRequest();
      x.open('GET', url);
      x.responseType = 'blob';
      x.onload = () => ((x.status === 200 || x.status === 0) && x.response ? res(x.response) : rej(new Error(url)));
      x.onerror = () => rej(new Error('Tidak ditemukan: ' + url));
      x.send();
    });
    return {
      name: decodeURIComponent(base.split('/').filter(Boolean).pop()), writable: false,
      async exists(p) { try { await get(base + p); return true; } catch { return false; } },
      readBlob: p => get(base + p),
      async readText(p) { return (await get(base + p)).text(); },
      async writeText() { throw new Error('Mode baca saja'); },
    };
  }
  function pickDirFallback() {
    return new Promise(res => {
      const inp = $('#dirInput');
      inp.value = '';
      inp.onchange = () => res(inp.files.length ? fsFromFiles(inp.files) : null);
      inp.click();
    });
  }

  async function openProject() {
    try {
      let fs = null;
      if (window.showDirectoryPicker) {
        try {
          fs = fsFromHandle(await window.showDirectoryPicker({ id: 'rm-project', mode: 'readwrite' }));
        } catch (e) {
          if (e.name === 'AbortError') return;
          if (e.name !== 'SecurityError' && e.name !== 'TypeError') throw e;
        }
      }
      if (!fs) fs = await pickDirFallback();
      if (!fs) return;
      await loadProject(fs);
    } catch (e) {
      console.error(e);
      toast('Gagal membuka proyek: ' + e.message, 'error', 9000);
    }
  }

  async function loadProject(fs) {
    if (!(await fs.exists('data/Tilesets.json'))) {
      throw new Error('folder ini bukan proyek RPG Maker MV/MZ (tidak ada data/Tilesets.json). Pilih folder utama proyek.');
    }
    const tilesets = JSON.parse(await fs.readText('data/Tilesets.json'));
    let mapInfos = [null];
    try { mapInfos = JSON.parse(await fs.readText('data/MapInfos.json')); } catch { /* proyek baru */ }
    let system = null;
    try { system = JSON.parse(await fs.readText('data/System.json')); } catch { /* opsional */ }
    Object.assign(P, { fs, name: fs.name, tilesets, mapInfos, system });
    P.engine = (await fs.exists('game.rmmzproject')) ? 'MZ' : (await fs.exists('Game.rpgproject')) ? 'MV' : (system && 'advanced' in system ? 'MZ' : 'MV');
    const sel = $('#tilesetSelect');
    sel.innerHTML = '';
    tilesets.forEach((t, id) => { if (t) sel.append(el('option', { value: id }, `${pad3(id)}: ${t.name || '(tanpa nama)'}`)); });
    $('#tilesetWrap').hidden = false;
    $('#projectLabel').textContent = `${P.name} · RPG Maker ${P.engine}${fs.writable ? '' : ' · baca saja'}`;
    $('#projectLabel').classList.remove('muted');
    $('#noProjectNote').hidden = true;
    const first = tilesets.findIndex(t => t);
    await selectTileset(suggestTileset(S.type) ?? first);
    toast(`Proyek "${P.name}" dimuat.`, 'ok');
    if (!fs.writable) {
      toast('Browser ini tidak bisa menulis langsung ke folder. Saat ekspor, file akan diunduh untuk Anda salin ke folder data proyek. Pakai Chrome atau Edge agar bisa menulis langsung.', 'warn', 10000);
    }
  }

  function suggestTileset(type) {
    if (!P.tilesets) return null;
    const hint = C.TYPE_TILESET_HINT[type];
    const i = P.tilesets.findIndex(t => t && t.tilesetNames && t.tilesetNames.includes(hint));
    return i > 0 ? i : null;
  }

  const presetKey = type => `rmforge:v1:${type}:${(P.names || []).join(',')}`;
  function savePreset() {
    if (!P.fs || !P.names) return;
    try { localStorage.setItem(presetKey(S.type), JSON.stringify(cfg())); } catch { /* penyimpanan tidak tersedia */ }
  }
  function loadPreset(type) {
    try {
      const v = JSON.parse(localStorage.getItem(presetKey(type)) || 'null');
      return v && Array.isArray(v.terrains) && v.terrains.length && v.params ? C.upgradeConfig(type, v) : null;
    } catch { return null; }
  }

  /** keepCurrent: jangan ubah konfigurasi tipe peta yang sedang dibuka (dipakai saat memuat file kerja). */
  async function selectTileset(id, keepCurrent = false) {
    const ts = P.tilesets && P.tilesets[id];
    if (!ts) return;
    P.tilesetId = +id;
    $('#tilesetSelect').value = id;
    P.names = ts.tilesetNames.slice();
    P.images = new Array(9).fill(null);
    P.labels = new Array(9).fill(null);
    tileCache.clear();
    alphaCache.clear();
    const missing = [];
    await Promise.all(P.names.map(async (name, k) => {
      if (!name) return;
      try {
        P.images[k] = await createImageBitmap(await P.fs.readBlob(`img/tilesets/${name}.png`));
      } catch { missing.push(name + '.png'); }
      try {
        const txt = await P.fs.readText(`img/tilesets/${name}.txt`);
        P.labels[k] = txt.replace(/^﻿/, '').split(/\r?\n/).map(l => l.split('|')[0].trim());
      } catch { /* label opsional */ }
    }));
    const guess = P.images[1] ? P.images[1].width / 16 : P.images[5] ? P.images[5].width / 16 : 48;
    P.tileSize = (P.system && P.system.tileSize) || Math.round(guess) || 48;
    if (missing.length) toast('Gambar tileset tidak ditemukan: ' + missing.join(', '), 'warn', 8000);

    let currentReplaced = false;
    const objBefore = JSON.stringify(cfg().objects.map(o => C.objTiles(o)));
    for (const type of C.TYPES) {
      if (keepCurrent && type === S.type) continue;
      const saved = loadPreset(type);
      if (saved) {
        S.configs[type] = saved;
        if (type === S.type) currentReplaced = true;
      } else {
        const c = S.configs[type];
        for (const t of c.terrains) t.tile = null;
        for (const o of c.objects) { o.tiles = null; o.join = null; delete o.tileId; }
        if (c.hill) c.hill.tile = null;
        if (c.stairs) c.stairs.tile = null;
        C.applyPresets(c, P.names, P.labels);
      }
    }
    syncTypeUI();
    if (currentReplaced) {
      clearHistory();
      generateMap({ noUndo: true });
    } else {
      // Tile objek berubah: sebar ulang supaya ID dari tileset sebelumnya tidak tertinggal
      if (!keepCurrent && JSON.stringify(cfg().objects.map(o => C.objTiles(o))) !== objBefore) {
        C.scatterObjects(st(), C.makeRng(S.seed + '|objek'));
      }
      prepAndRender();
    }
  }

  // ---------------------------------------------------------------------------
  // Ekspor
  // ---------------------------------------------------------------------------
  const mapPath = id => `data/Map${pad3(id)}.json`;
  function mapOptions(select, withRoot) {
    select.innerHTML = '';
    if (withRoot) select.append(el('option', { value: 0 }, '(paling atas)'));
    const list = (P.mapInfos || []).filter(Boolean).sort((a, b) => (a.order || 0) - (b.order || 0));
    for (const m of list) select.append(el('option', { value: m.id }, `${pad3(m.id)}: ${m.name}`));
    return list.length;
  }
  function syncExportMode() {
    const isNew = $('#exMode').value === 'new';
    $('#exNameRow').hidden = !isNew;
    $('#exParentRow').hidden = !isNew;
    $('#exTargetRow').hidden = isNew;
  }
  function openExport() {
    if (!P.fs) { toast('Buka proyek RPG Maker dulu, lalu pilih tilesetnya.', 'warn'); return; }
    const T = cfg().terrains;
    const used = new Set(S.grid);
    const missing = T.filter((t, i) => !t.tile && (C.isWallType(S.type) || used.has(i))).map(t => t.name);
    mapOptions($('#exParent'), true);
    const n = mapOptions($('#exTarget'), false);
    $('#exMode').querySelector('option[value=overwrite]').disabled = !n;
    $('#exMode').value = 'new';
    $('#exName').value = `${C.TYPE_LABEL[S.type].split(' (')[0]} ${S.seed}`;
    const ts = P.tilesets[P.tilesetId];
    const info = [`Ukuran ${S.width}×${S.height}, tileset ${pad3(P.tilesetId)}: ${ts.name}.`];
    if (missing.length) info.push(`Terrain tanpa tile (akan kosong): ${missing.join(', ')}.`);
    if (!P.fs.writable) info.push('Mode baca saja: file akan diunduh untuk disalin manual ke folder data.');
    $('#exInfo').textContent = info.join(' ');
    syncExportMode();
    $('#exportDlg').showModal();
  }
  async function doExport() {
    const fs = P.fs, mode = $('#exMode').value;
    const infos = (P.mapInfos || [null]).slice();
    let id, base = null;
    if (mode === 'new') {
      id = Math.max(1, infos.length);
      while (id < 1000 && (infos[id] || (await fs.exists(mapPath(id))))) id++;
      if (id >= 1000) throw new Error('nomor peta sudah penuh (maksimal 999).');
      const name = $('#exName').value.trim() || 'MAP' + pad3(id);
      const order = infos.reduce((m, x) => (x ? Math.max(m, x.order || 0) : m), 0) + 1;
      while (infos.length <= id) infos.push(null);
      infos[id] = { id, expanded: false, name, order, parentId: +$('#exParent').value || 0, scrollX: 0, scrollY: 0 };
    } else {
      id = +$('#exTarget').value;
      if (!id) throw new Error('pilih peta yang akan ditimpa.');
      const target = infos[id];
      if (!confirm(`Timpa isi peta ${pad3(id)}: ${target ? target.name : ''}?\nEvent, BGM, dan pengaturan peta tetap dipertahankan; tile diganti.`)) return false;
      try { base = JSON.parse(await fs.readText(mapPath(id))); } catch { base = null; }
    }
    const mapText = JSON.stringify(C.makeMapJson(S.built, P.tilesetId, base));
    const infoText = '[\n' + infos.map(x => JSON.stringify(x)).join(',\n') + '\n]';
    if (fs.writable) {
      await fs.writeText(mapPath(id), mapText);
      if (mode === 'new') await fs.writeText('data/MapInfos.json', infoText);
      toast(`Berhasil: ${mapPath(id)} ditulis. Buka proyeknya di RPG Maker untuk melihat peta.`, 'ok', 9000);
    } else {
      download(`Map${pad3(id)}.json`, mapText);
      if (mode === 'new') download('MapInfos.json', infoText);
      toast('File diunduh. Salin ke folder "data" proyek Anda (timpa MapInfos.json yang lama).', 'warn', 12000);
    }
    P.mapInfos = infos;
    return true;
  }

  // ---------------------------------------------------------------------------
  // Simpan / muat kerja
  // ---------------------------------------------------------------------------
  function saveWork() {
    const data = {
      app: 'rm-map-forge', version: 1,
      type: S.type, width: S.width, height: S.height, seed: S.seed,
      config: cfg(), tilesetId: P.fs ? P.tilesetId : null, tilesetNames: P.names,
      grid: Array.from(S.grid), deco: Array.from(S.deco), deco3: Array.from(S.deco3),
      own2: Array.from(S.own2), own3: Array.from(S.own3),
      level: Array.from(S.level), biome: Array.from(S.biome), paths: S.paths,
    };
    download(`peta-${S.type}-${S.seed}.json`, JSON.stringify(data));
  }
  async function loadWork(file) {
    const d = JSON.parse(await file.text());
    if (d.app !== 'rm-map-forge' || !C.TYPES.includes(d.type)) throw new Error('bukan file kerja RM Map Forge.');
    const N = d.width * d.height;
    if (!Array.isArray(d.grid) || d.grid.length !== N || !Array.isArray(d.deco) || d.deco.length !== N) throw new Error('data peta rusak.');
    S.type = d.type;
    S.configs[d.type] = C.upgradeConfig(d.type, d.config);
    S.width = d.width;
    S.height = d.height;
    S.seed = d.seed;
    S.grid = Uint8Array.from(d.grid);
    const lay = C.makeObjectLayers(N);
    lay.deco.set(d.deco);
    if (Array.isArray(d.deco3) && d.deco3.length === N) lay.deco3.set(d.deco3);
    if (Array.isArray(d.own2) && d.own2.length === N) lay.own2.set(d.own2);
    else d.deco.forEach((v, k) => { if (v) lay.own2[k] = k + 1; }); // file versi lama: tiap objek 1 tile
    if (Array.isArray(d.own3) && d.own3.length === N) lay.own3.set(d.own3);
    for (const k of OBJ_LAYERS) S[k] = lay[k];
    S.level = new Uint8Array(N);
    if (Array.isArray(d.level) && d.level.length === N) S.level.set(d.level);
    S.biome = new Uint8Array(N);
    if (Array.isArray(d.biome) && d.biome.length === N) S.biome.set(d.biome);
    S.paths = Array.isArray(d.paths) ? d.paths : [];
    $('#mapW').value = S.width;
    $('#mapH').value = S.height;
    $('#seed').value = S.seed;
    clearHistory();
    if (P.fs && d.tilesetId && P.tilesets[d.tilesetId]) await selectTileset(d.tilesetId, true);
    syncTypeUI();
    prepAndRender();
    fitZoom();
    toast('File kerja dimuat.', 'ok');
  }

  // ---------------------------------------------------------------------------
  // Pasang event UI
  // ---------------------------------------------------------------------------
  function initUI() {
    const mt = $('#mapType');
    for (const t of C.TYPES) mt.append(el('option', { value: t }, C.TYPE_LABEL[t]));
    const zm = $('#zoom');
    for (const z of ZOOMS) zm.append(el('option', { value: z }, z + ' px'));

    mt.addEventListener('change', async e => {
      pushUndo();
      S.type = e.target.value;
      const [w, h] = C.DEFAULT_SIZE[S.type];
      $('#mapW').value = w;
      $('#mapH').value = h;
      S.terrainSel = 0;
      S.objectSel = 0;
      S.paths = [];
      syncTypeUI();
      generateMap({ noUndo: true }); // grid baru dulu, agar indeks terrain cocok dengan tipe baru
      const sug = suggestTileset(S.type);
      if (P.fs && sug != null && sug !== P.tilesetId) await selectTileset(sug);
      fitZoom();
    });
    $('#btnGenerate').addEventListener('click', () => generateMap());
    $('#btnDice').addEventListener('click', () => { $('#seed').value = randomSeed(); generateMap(); });
    $('#seed').addEventListener('keydown', e => { if (e.key === 'Enter') generateMap(); });
    for (const id of ['#mapW', '#mapH']) $(id).addEventListener('change', () => { generateMap(); fitZoom(); });
    $('#btnAddTerrain').addEventListener('click', addTerrain);
    $('#btnAddBiome').addEventListener('click', addBiome);
    $('#btnAddPath').addEventListener('click', addPath);
    $('#showBiome').addEventListener('change', e => { S.showBiome = e.target.checked; renderAll(); });
    $('#levelSel').addEventListener('change', e => { S.levelSel = +e.target.value; });
    $('#btnAddObject').addEventListener('click', addObject);
    $('#btnScatter').addEventListener('click', () => rescatter(true));
    $('#btnUndo').addEventListener('click', undo);
    $('#btnRedo').addEventListener('click', redo);
    $('#btnOpenProject').addEventListener('click', openProject);
    $('#tilesetSelect').addEventListener('change', e => selectTileset(+e.target.value));
    $('#btnSaveWork').addEventListener('click', saveWork);
    $('#btnLoadWork').addEventListener('click', () => { $('#workInput').value = ''; $('#workInput').click(); });
    $('#workInput').addEventListener('change', e => {
      const f = e.target.files[0];
      if (f) loadWork(f).catch(err => toast('Gagal memuat: ' + err.message, 'error', 8000));
    });
    $('#btnExport').addEventListener('click', openExport);
    $('#exMode').addEventListener('change', syncExportMode);
    $('#exGo').addEventListener('click', async () => {
      const btn = $('#exGo');
      btn.disabled = true;
      try {
        if (await doExport()) $('#exportDlg').close();
      } catch (e) {
        console.error(e);
        toast('Ekspor gagal: ' + e.message, 'error', 9000);
      } finally {
        btn.disabled = false;
      }
    });
    for (const b of document.querySelectorAll('[data-close]')) b.addEventListener('click', () => b.closest('dialog').close());
    for (const b of document.querySelectorAll('#toolSeg button')) {
      b.addEventListener('click', () => { S.tool = b.dataset.tool; syncTools(); });
    }
    $('#radius').addEventListener('input', e => setRadius(+e.target.value));
    $('#zoom').addEventListener('change', e => { S.zoom = +e.target.value; renderAll(); });
    $('#showGrid').addEventListener('change', e => { S.showGrid = e.target.checked; renderAll(); });
    window.addEventListener('beforeunload', e => { if (S.undo.length) { e.preventDefault(); e.returnValue = ''; } });
    document.addEventListener('keydown', e => {
      const t = e.target;
      const typing = (t.tagName === 'INPUT' && !['range', 'checkbox', 'color'].includes(t.type)) || t.tagName === 'SELECT' || t.tagName === 'TEXTAREA';
      if (typing) return;
      const k = e.key.toLowerCase();
      if ((e.ctrlKey || e.metaKey) && k === 'z') { e.preventDefault(); e.shiftKey ? redo() : undo(); }
      else if ((e.ctrlKey || e.metaKey) && k === 'y') { e.preventDefault(); redo(); }
      else if (k === '[') setRadius(S.radius - 1);
      else if (k === ']') setRadius(S.radius + 1);
    });
  }

  // ---------------------------------------------------------------------------
  // Mulai
  // ---------------------------------------------------------------------------
  initUI();
  const qs = new URLSearchParams(location.search);
  if (C.TYPES.includes(qs.get('type'))) S.type = qs.get('type');
  const [w0, h0] = C.DEFAULT_SIZE[S.type];
  $('#mapW').value = w0;
  $('#mapH').value = h0;
  $('#seed').value = qs.get('seed') || randomSeed();
  setRadius(S.radius);
  syncTypeUI();
  syncUndo();
  generateMap({ noUndo: true });
  fitZoom();
  if (qs.get('project')) {
    loadProject(fsFromUrl(qs.get('project'))).then(fitZoom).catch(e => toast('Gagal membuka proyek: ' + e.message, 'error', 9000));
  }
  window.addEventListener('resize', () => { if (S.built) renderAll(); });
})();
