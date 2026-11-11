/*
 * RM Map Forge — inti logika (tanpa DOM).
 * Format tile, autotile, generator peta, dan konversi ke MapXXX.json RPG Maker MV/MZ.
 */
(function (root) {
  'use strict';

  // ---------------------------------------------------------------------------
  // Tile ID RPG Maker MV/MZ
  // ---------------------------------------------------------------------------
  const ID = { B: 0, C: 256, D: 512, E: 768, A5: 1536, A1: 2048, A2: 2816, A3: 4352, A4: 5888, MAX: 8192 };
  const AUTO = 100000; // penanda kode internal untuk autotile (AUTO + kind)
  const LVL = 1000;    // kode autotile per tingkat bukit: AUTO + tingkat*LVL + kind

  // Posisi seperempat-tile [qx, qy] (satuan setengah tile) untuk tiap bentuk autotile.
  // Urutan seperempat: kiri-atas, kanan-atas, kiri-bawah, kanan-bawah.
  const FLOOR_TABLE = [
    [[2,4],[1,4],[2,3],[1,3]], [[2,0],[1,4],[2,3],[1,3]], [[2,4],[3,0],[2,3],[1,3]], [[2,0],[3,0],[2,3],[1,3]],
    [[2,4],[1,4],[2,3],[3,1]], [[2,0],[1,4],[2,3],[3,1]], [[2,4],[3,0],[2,3],[3,1]], [[2,0],[3,0],[2,3],[3,1]],
    [[2,4],[1,4],[2,1],[1,3]], [[2,0],[1,4],[2,1],[1,3]], [[2,4],[3,0],[2,1],[1,3]], [[2,0],[3,0],[2,1],[1,3]],
    [[2,4],[1,4],[2,1],[3,1]], [[2,0],[1,4],[2,1],[3,1]], [[2,4],[3,0],[2,1],[3,1]], [[2,0],[3,0],[2,1],[3,1]],
    [[0,4],[1,4],[0,3],[1,3]], [[0,4],[3,0],[0,3],[1,3]], [[0,4],[1,4],[0,3],[3,1]], [[0,4],[3,0],[0,3],[3,1]],
    [[2,2],[1,2],[2,3],[1,3]], [[2,2],[1,2],[2,3],[3,1]], [[2,2],[1,2],[2,1],[1,3]], [[2,2],[1,2],[2,1],[3,1]],
    [[2,4],[3,4],[2,3],[3,3]], [[2,4],[3,4],[2,1],[3,3]], [[2,0],[3,4],[2,3],[3,3]], [[2,0],[3,4],[2,1],[3,3]],
    [[2,4],[1,4],[2,5],[1,5]], [[2,0],[1,4],[2,5],[1,5]], [[2,4],[3,0],[2,5],[1,5]], [[2,0],[3,0],[2,5],[1,5]],
    [[0,4],[3,4],[0,3],[3,3]], [[2,2],[1,2],[2,5],[1,5]], [[0,2],[1,2],[0,3],[1,3]], [[0,2],[1,2],[0,3],[3,1]],
    [[2,2],[3,2],[2,3],[3,3]], [[2,2],[3,2],[2,1],[3,3]], [[2,4],[3,4],[2,5],[3,5]], [[2,0],[3,4],[2,5],[3,5]],
    [[0,4],[1,4],[0,5],[1,5]], [[0,4],[3,0],[0,5],[1,5]], [[0,2],[3,2],[0,3],[3,3]], [[0,2],[1,2],[0,5],[1,5]],
    [[0,4],[3,4],[0,5],[3,5]], [[2,2],[3,2],[2,5],[3,5]], [[0,2],[3,2],[0,5],[3,5]], [[0,0],[1,0],[0,1],[1,1]],
  ];
  const WALL_TABLE = [
    [[2,2],[1,2],[2,1],[1,1]], [[0,2],[1,2],[0,1],[1,1]], [[2,0],[1,0],[2,1],[1,1]], [[0,0],[1,0],[0,1],[1,1]],
    [[2,2],[3,2],[2,1],[3,1]], [[0,2],[3,2],[0,1],[3,1]], [[2,0],[3,0],[2,1],[3,1]], [[0,0],[3,0],[0,1],[3,1]],
    [[2,2],[1,2],[2,3],[1,3]], [[0,2],[1,2],[0,3],[1,3]], [[2,0],[1,0],[2,3],[1,3]], [[0,0],[1,0],[0,3],[1,3]],
    [[2,2],[3,2],[2,3],[3,3]], [[0,2],[3,2],[0,3],[3,3]], [[2,0],[3,0],[2,3],[3,3]], [[0,0],[3,0],[0,3],[3,3]],
  ];
  const WATERFALL_TABLE = [
    [[2,0],[1,0],[2,1],[1,1]], [[0,0],[1,0],[0,1],[1,1]], [[2,0],[3,0],[2,1],[3,1]], [[0,0],[3,0],[0,1],[3,1]],
  ];

  // Bit tetangga: N=1 E=2 S=4 W=8 NE=16 SE=32 SW=64 NW=128  ->  indeks bentuk FLOOR_TABLE
  const FLOOR_SHAPE = (function () {
    const lookup = new Map();
    for (let i = 0; i < 47; i++) {
      const key = FLOOR_TABLE[i].map(q => q.join(',')).join('|');
      if (!lookup.has(key)) lookup.set(key, i);
    }
    const out = new Uint8Array(256);
    for (let m = 0; m < 256; m++) {
      const n = m & 1, e = m & 2, s = m & 4, w = m & 8, ne = m & 16, se = m & 32, sw = m & 64, nw = m & 128;
      const q = [
        (n && w && !nw) ? [2, 0] : [w ? 2 : 0, n ? 4 : 2],
        (n && e && !ne) ? [3, 0] : [e ? 1 : 3, n ? 4 : 2],
        (s && w && !sw) ? [2, 1] : [w ? 2 : 0, s ? 3 : 5],
        (s && e && !se) ? [3, 1] : [e ? 1 : 3, s ? 3 : 5],
      ];
      const key = q.map(v => v.join(',')).join('|');
      if (!lookup.has(key)) throw new Error('Kombinasi autotile tidak dikenal: ' + m);
      out[m] = lookup.get(key);
    }
    return out;
  })();

  const kindOf = id => Math.floor((id - ID.A1) / 48);
  const autoId = (kind, shape) => ID.A1 + kind * 48 + shape;
  const isWaterfallKind = k => k >= 4 && k < 16 && k % 2 === 1;
  const usesWallTable = k => (k >= 48 && k < 80) || (k >= 80 && k < 128 && Math.floor(k / 8) % 2 === 1);
  const isWallTopKind = k => k >= 80 && k < 128 && Math.floor(k / 8) % 2 === 0;
  const thumbShape = k => usesWallTable(k) ? 15 : isWaterfallKind(k) ? 3 : 47;

  /** Bentuk autotile berdasar tetangga. same(dx, dy) -> true bila tetangga sejenis. */
  function shapeFor(kind, same) {
    if (usesWallTable(kind)) {
      return (same(-1, 0) ? 0 : 1) | (same(0, -1) ? 0 : 2) | (same(1, 0) ? 0 : 4) | (same(0, 1) ? 0 : 8);
    }
    if (isWaterfallKind(kind)) return (same(-1, 0) ? 0 : 1) | (same(1, 0) ? 0 : 2);
    let m = 0;
    if (same(0, -1)) m |= 1;
    if (same(1, 0)) m |= 2;
    if (same(0, 1)) m |= 4;
    if (same(-1, 0)) m |= 8;
    if (same(1, -1)) m |= 16;
    if (same(1, 1)) m |= 32;
    if (same(-1, 1)) m |= 64;
    if (same(-1, -1)) m |= 128;
    return FLOOR_SHAPE[m];
  }

  /**
   * Bentuk sisi dinding A4 sesuai perilaku editor RPG Maker:
   * tepi kiri/kanan mengikuti atap di atas kolom dinding, bukan hanya tetangga langsung.
   * at(x, y) -> kode sel (OOB mengembalikan null). code = kode sel ini. isTop(code) -> true bila atap A4.
   */
  function wallSideShape(at, x, y, code, isTop) {
    let yt = y - 1;
    while (at(x, yt) === code) yt--;
    const topHere = at(x, yt);
    const sameH = dx => {
      const n = at(x + dx, y);
      if (n === null) return false;
      if (isTop(n)) return true;
      return n === code && at(x + dx, yt) === topHere;
    };
    const sameV = dy => at(x, y + dy) === code;
    return (sameH(-1) ? 0 : 1) | (sameV(-1) ? 0 : 2) | (sameH(1) ? 0 : 4) | (sameV(1) ? 0 : 8);
  }

  /**
   * Sumber gambar sebuah tile (frame animasi pertama).
   * set: indeks gambar di tilesetNames (0=A1 .. 4=A5, 5=B .. 8=E)
   * Autotile -> quads: 4 x [qx, qy] dalam satuan setengah tile. Tile biasa -> sx, sy dalam satuan tile.
   */
  function tileSource(tileId) {
    if (tileId >= ID.A1 && tileId < ID.MAX) {
      const kind = kindOf(tileId), shape = (tileId - ID.A1) % 48;
      const tx = kind % 8, ty = Math.floor(kind / 8);
      let set, bx = 0, by = 0, table = FLOOR_TABLE;
      if (kind < 16) {
        set = 0;
        if (kind === 0) { bx = 0; by = 0; }
        else if (kind === 1) { bx = 0; by = 3; }
        else if (kind === 2) { bx = 6; by = 0; }
        else if (kind === 3) { bx = 6; by = 3; }
        else {
          bx = Math.floor(tx / 4) * 8;
          by = ty * 6 + (Math.floor(tx / 2) % 2) * 3;
          if (kind % 2 === 1) { bx += 6; table = WATERFALL_TABLE; }
        }
      } else if (kind < 48) {
        set = 1; bx = tx * 2; by = (ty - 2) * 3;
      } else if (kind < 80) {
        set = 2; bx = tx * 2; by = (ty - 6) * 2; table = WALL_TABLE;
      } else {
        set = 3; bx = tx * 2; by = Math.floor((ty - 10) * 2.5 + (ty % 2 === 1 ? 0.5 : 0));
        if (ty % 2 === 1) table = WALL_TABLE;
      }
      const t = table[shape];
      if (!t) return null;
      return { set, quads: t.map(([qx, qy]) => [bx * 2 + qx, by * 2 + qy]) };
    }
    if (tileId > 0 && tileId < ID.A1) {
      const set = tileId >= ID.A5 ? 4 : 5 + Math.floor(tileId / 256);
      return {
        set,
        sx: (Math.floor(tileId / 128) % 2) * 8 + (tileId % 8),
        sy: Math.floor((tileId % 256) / 8) % 16,
      };
    }
    return null;
  }

  /** Tile biasa dari posisi kolom/baris pada lembar gambar (set 4=A5, 5..8=B..E). */
  function normalTileId(set, col, row) {
    if (set === 4) return col < 8 ? ID.A5 + row * 8 + col : -1;
    const base = (set - 5) * 256;
    return base + (col >= 8 ? 128 : 0) + row * 8 + (col % 8);
  }

  /** Indeks baris pada file label .txt (format "English|日本語") untuk sebuah tile. */
  function labelIndex(tile) {
    if (!tile) return -1;
    if (tile.auto != null) {
      const k = tile.auto;
      if (k < 16) return k;
      if (k < 48) return k - 16;
      if (k < 80) return k - 48;
      return k - 80;
    }
    if (tile.id >= ID.A5) return tile.id - ID.A5;
    return tile.id % 256;
  }
  function setOfTile(tile) {
    if (!tile) return -1;
    if (tile.auto != null) return tile.auto < 16 ? 0 : tile.auto < 48 ? 1 : tile.auto < 80 ? 2 : 3;
    return tile.id >= ID.A5 ? 4 : 5 + Math.floor(tile.id / 256);
  }
  /** Ubah indeks label pada suatu set menjadi tile. */
  function tileFromIndex(set, idx) {
    if (set === 0) return { auto: idx };
    if (set === 1) return { auto: 16 + idx };
    if (set === 2) return { auto: 48 + idx };
    if (set === 3) return { auto: 80 + idx };
    if (set === 4) return { id: ID.A5 + idx };
    return { id: (set - 5) * 256 + idx };
  }

  // ---------------------------------------------------------------------------
  // Angka acak ber-seed & noise
  // ---------------------------------------------------------------------------
  function hashString(str) {
    let h = 1779033703 ^ str.length;
    for (let i = 0; i < str.length; i++) {
      h = Math.imul(h ^ str.charCodeAt(i), 3432918353);
      h = (h << 13) | (h >>> 19);
    }
    h = Math.imul(h ^ (h >>> 16), 2246822507);
    h = Math.imul(h ^ (h >>> 13), 3266489909);
    return (h ^ (h >>> 16)) >>> 0;
  }
  function makeRng(seed) {
    let a = hashString(String(seed));
    const r = function () {
      a = (a + 0x6D2B79F5) | 0;
      let t = Math.imul(a ^ (a >>> 15), 1 | a);
      t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
    r.int = (lo, hi) => (hi <= lo ? lo : lo + Math.floor(r() * (hi - lo + 1)));
    return r;
  }

  /** Simplex noise 2D (algoritma publik Stefan Gustavson), hasil kira-kira -1..1. */
  function makeNoise2D(rand) {
    const p = new Uint8Array(256);
    for (let i = 0; i < 256; i++) p[i] = i;
    for (let i = 255; i > 0; i--) {
      const j = Math.floor(rand() * (i + 1));
      const t = p[i]; p[i] = p[j]; p[j] = t;
    }
    const perm = new Uint8Array(512);
    for (let i = 0; i < 512; i++) perm[i] = p[i & 255];
    const GX = [1, -1, 1, -1, 1, -1, 0, 0], GY = [1, 1, -1, -1, 0, 0, 1, -1];
    const F2 = 0.5 * (Math.sqrt(3) - 1), G2 = (3 - Math.sqrt(3)) / 6;
    const corner = (g, x, y) => {
      let t = 0.5 - x * x - y * y;
      if (t < 0) return 0;
      t *= t;
      return t * t * (GX[g] * x + GY[g] * y);
    };
    return function (xin, yin) {
      const s = (xin + yin) * F2;
      const i = Math.floor(xin + s), j = Math.floor(yin + s);
      const t = (i + j) * G2;
      const x0 = xin - (i - t), y0 = yin - (j - t);
      const i1 = x0 > y0 ? 1 : 0, j1 = x0 > y0 ? 0 : 1;
      const x1 = x0 - i1 + G2, y1 = y0 - j1 + G2;
      const x2 = x0 - 1 + 2 * G2, y2 = y0 - 1 + 2 * G2;
      const ii = i & 255, jj = j & 255;
      return 70 * (
        corner(perm[ii + perm[jj]] & 7, x0, y0) +
        corner(perm[ii + i1 + perm[jj + j1]] & 7, x1, y1) +
        corner(perm[ii + 1 + perm[jj + 1]] & 7, x2, y2)
      );
    };
  }
  function fbm(noise, x, y, octaves) {
    let amp = 1, freq = 1, sum = 0, norm = 0;
    for (let o = 0; o < octaves; o++) {
      sum += amp * noise(x * freq, y * freq);
      norm += amp;
      amp *= 0.5;
      freq *= 2;
    }
    return sum / norm;
  }
  function normalize(arr) {
    let lo = Infinity, hi = -Infinity;
    for (let i = 0; i < arr.length; i++) { if (arr[i] < lo) lo = arr[i]; if (arr[i] > hi) hi = arr[i]; }
    const d = hi - lo || 1;
    for (let i = 0; i < arr.length; i++) arr[i] = (arr[i] - lo) / d;
  }

  // ---------------------------------------------------------------------------
  // Konfigurasi bawaan
  // ---------------------------------------------------------------------------
  const TYPES = ['overworld', 'outside', 'cave', 'dungeon'];
  const TYPE_LABEL = {
    overworld: 'Overworld (pulau/benua)',
    outside: 'Luar ruangan (padang, hutan)',
    cave: 'Gua (organik)',
    dungeon: 'Dungeon (ruangan & lorong)',
  };
  const isWallType = type => type === 'cave' || type === 'dungeon';
  const DEFAULT_SIZE = { overworld: [80, 60], outside: [50, 40], cave: [50, 40], dungeon: [60, 45] };
  // Tileset bawaan (RTP) yang cocok untuk tiap tipe — dicari berdasar nama file gambar.
  const TYPE_TILESET_HINT = { overworld: 'World_A2', outside: 'Outside_A2', cave: 'Dungeon_A2', dungeon: 'Dungeon_A2' };

  const PARAM_DEFS = {
    overworld: [
      { key: 'scale', label: 'Ukuran benua', min: 10, max: 120, step: 1, def: 45 },
      { key: 'octaves', label: 'Detail garis pantai', min: 1, max: 7, step: 1, def: 5 },
      { key: 'island', label: 'Efek pulau (tepi jadi laut)', min: 0, max: 1, step: 0.05, def: 0.6 },
      { key: 'smooth', label: 'Penghalusan', min: 0, max: 4, step: 1, def: 2 },
      { key: 'roads', label: 'Jalan otomatis', min: 0, max: 12, step: 1, def: 0 },
      { key: 'roadWidth', label: 'Lebar jalan', min: 1, max: 3, step: 1, def: 1 },
      { key: 'biomeScale', label: 'Ukuran biome', min: 6, max: 120, step: 1, def: 30 },
    ],
    outside: [
      { key: 'scale', label: 'Ukuran fitur', min: 6, max: 80, step: 1, def: 20 },
      { key: 'octaves', label: 'Detail', min: 1, max: 6, step: 1, def: 4 },
      { key: 'island', label: 'Efek pulau', min: 0, max: 1, step: 0.05, def: 0 },
      { key: 'smooth', label: 'Penghalusan', min: 0, max: 4, step: 1, def: 2 },
      { key: 'hills', label: 'Luas bukit bertebing', min: 0, max: 0.7, step: 0.05, def: 0.3 },
      { key: 'hillLevels', label: 'Jumlah tingkat bukit', min: 1, max: 3, step: 1, def: 2 },
      { key: 'hillScale', label: 'Ukuran bukit', min: 6, max: 60, step: 1, def: 16 },
      { key: 'cliffHeight', label: 'Tinggi tebing (tile)', min: 1, max: 3, step: 1, def: 2 },
      { key: 'roads', label: 'Jalan otomatis', min: 0, max: 12, step: 1, def: 3 },
      { key: 'roadWidth', label: 'Lebar jalan', min: 1, max: 3, step: 1, def: 1 },
      { key: 'biomeScale', label: 'Ukuran biome', min: 6, max: 80, step: 1, def: 18 },
      { key: 'shadow', label: 'Bayangan tebing', type: 'check', def: true },
    ],
    cave: [
      { key: 'fill', label: 'Kepadatan dinding', min: 0.35, max: 0.6, step: 0.01, def: 0.47 },
      { key: 'steps', label: 'Langkah penghalusan', min: 1, max: 8, step: 1, def: 5 },
      { key: 'wallHeight', label: 'Tinggi dinding (tile)', min: 1, max: 3, step: 1, def: 2 },
      { key: 'biomeScale', label: 'Ukuran biome', min: 6, max: 80, step: 1, def: 16 },
      { key: 'shadow', label: 'Bayangan dinding', type: 'check', def: true },
    ],
    dungeon: [
      { key: 'rooms', label: 'Jumlah ruangan', min: 2, max: 40, step: 1, def: 10 },
      { key: 'roomMin', label: 'Ruangan terkecil', min: 3, max: 12, step: 1, def: 5 },
      { key: 'roomMax', label: 'Ruangan terbesar', min: 4, max: 20, step: 1, def: 10 },
      { key: 'corridor', label: 'Lebar lorong', min: 1, max: 3, step: 1, def: 1 },
      { key: 'wallHeight', label: 'Tinggi dinding (tile)', min: 1, max: 3, step: 1, def: 2 },
      { key: 'biomeScale', label: 'Ukuran biome', min: 6, max: 80, step: 1, def: 16 },
      { key: 'shadow', label: 'Bayangan dinding', type: 'check', def: true },
    ],
  };

  let uidCounter = 0;
  const uid = () => 't' + Date.now().toString(36) + (uidCounter++).toString(36) + Math.floor(Math.random() * 1e4).toString(36);

  // preset: {file, idx, name} -> dicocokkan ke tileset proyek saat dimuat
  function terrain(name, color, rule, extra) {
    return Object.assign({ id: uid(), name, color, tile: null, overlay: false, base: null, block: false, region: 0, rule }, extra || {});
  }
  // Objek = blok tile (baris atas -> bawah). Baris terakhir adalah alas yang menapak di terrain.
  // join = varian rapat (dipakai otomatis saat pucuk objek menimpa alas objek lain, mis. hutan lebat)
  function obj(name, terrainId, density, file, idxTiles, biome, joinIdx) {
    return {
      id: uid(), name, tiles: null, join: null, terrain: terrainId, density, biome: biome || '',
      preset: { file, tiles: idxTiles, join: joinIdx || null },
    };
  }
  const biomeDef = (name, color, share) => ({ id: uid(), name, color, share });
  /** Matriks tile objek; mendukung format lama {tileId}. */
  function objTiles(o) {
    if (o.tiles && o.tiles.length && o.tiles[0].length && o.tiles.some(r => r.some(Boolean))) return o.tiles;
    if (o.tileId) return [[o.tileId]];
    return null;
  }

  function defaultConfig(type) {
    const params = {};
    for (const d of PARAM_DEFS[type]) params[d.key] = d.def;
    let terrains = [], objects = [], biomes = [biomeDef('Umum', '#9aa1ad', 1)], hill = null, stairs = null;
    if (type === 'overworld') {
      const sea = terrain('Laut', '#2f7fc1', { mode: 'height', min: 0.2 }, { block: true, preset: { file: 'World_A1', idx: 0, name: 'Sea' } });
      // Tepi laut dalam transparan -> harus ditumpuk di atas laut biasa
      const deep = terrain('Laut Dalam', '#1d4e89', { mode: 'height', min: 0 }, { block: true, overlay: true, base: sea.id, preset: { file: 'World_A1', idx: 1, name: 'Deep Sea' } });
      const grass = terrain('Padang Rumput', '#6bb04a', { mode: 'height', min: 0.45 }, { preset: { file: 'World_A2', idx: 0, name: 'Grassland A' } });
      const desert = terrain('Gurun', '#e0c47a', { mode: 'patch', parent: grass.id, threshold: 0.8, scale: 30 }, { preset: { file: 'World_A2', idx: 16, name: 'Desert A' } });
      const forest = terrain('Hutan', '#2e7d32', { mode: 'patch', parent: grass.id, threshold: 0.55, scale: 14 }, { overlay: true, base: grass.id, preset: { file: 'World_A2', idx: 4, name: 'Forest' } });
      const hill = terrain('Bukit', '#9c8a5a', { mode: 'height', min: 0.8 }, { overlay: true, base: grass.id, preset: { file: 'World_A2', idx: 6, name: 'Hill (Grass)' } });
      const mount = terrain('Gunung', '#7a6e66', { mode: 'height', min: 0.9 }, { overlay: true, base: grass.id, block: true, preset: { file: 'World_A2', idx: 7, name: 'Mountain (Dirt)' } });
      const road = terrain('Jalan', '#c9a66b', { mode: 'path' }, { preset: { file: 'World_A2', idx: 13, name: 'Road (Dirt)' } });
      terrains = [deep, sea, grass, desert, forest, hill, mount, road];
    } else if (type === 'outside') {
      const meadow = biomeDef('Padang', '#e3c24f', 1);
      const forestB = biomeDef('Hutan Lebat', '#2f9e5b', 0.8);
      biomes = [meadow, forestB];
      const water = terrain('Air', '#3b82c4', { mode: 'height', min: 0 }, { block: true, preset: { file: 'Outside_A1', idx: 0, name: 'Water A (Meadow)' } });
      const grass = terrain('Rumput', '#6fbf4b', { mode: 'height', min: 0.14 }, { preset: { file: 'Outside_A2', idx: 0, name: 'Meadow' } });
      const dirt = terrain('Tanah', '#a77b4f', { mode: 'patch', parent: grass.id, threshold: 0.74, scale: 10, biome: meadow.id }, { preset: { file: 'Outside_A2', idx: 1, name: 'Dirt (Meadow)' } });
      const bush = terrain('Semak', '#3f8f3a', { mode: 'patch', parent: grass.id, threshold: 0.6, scale: 7, biome: forestB.id }, { overlay: true, base: grass.id, preset: { file: 'Outside_A2', idx: 4, name: 'Bush' } });
      const road = terrain('Jalan', '#c9a66b', { mode: 'path' }, { preset: { file: 'Outside_A2', idx: 2, name: 'Road (Meadow)' } });
      terrains = [water, grass, dirt, bush, road];
      hill = { tile: null, base: grass.id, preset: { file: 'Outside_A4', idx: 32, name: 'Ledge A (Meadow)' } };
      stairs = { tile: null, preset: { file: 'Outside_A5', idx: 27, name: 'Stairs (Meadow)' } };
      const TREE = [[93], [101]], TREE_J = [[94], [101]], BIG = [[112, 113], [120, 121]], BIG_J = null;
      objects = [
        obj('Pohon besar (hutan)', '', 0.08, 'Outside_B', BIG, forestB.id, BIG_J),
        obj('Pohon (hutan)', '', 0.45, 'Outside_B', TREE, forestB.id, TREE_J),
        obj('Semak bulat (hutan)', '', 0.05, 'Outside_B', [[102]], forestB.id),
        obj('Pohon besar', grass.id, 0.006, 'Outside_B', BIG, meadow.id, BIG_J),
        obj('Pohon', grass.id, 0.02, 'Outside_B', TREE, meadow.id, TREE_J),
        obj('Semak bulat', grass.id, 0.01, 'Outside_B', [[102]], meadow.id),
        obj('Tunggul', grass.id, 0.004, 'Outside_B', [[92]], meadow.id),
        obj('Rumput liar', grass.id, 0.04, 'Outside_B', [[88]]),
        obj('Bunga', grass.id, 0.02, 'Outside_B', [[96]], meadow.id),
        obj('Batu', dirt.id, 0.03, 'Outside_B', [[95]]),
      ];
    } else if (type === 'cave') {
      const floor = terrain('Lantai Gua', '#8d7b68', { mode: 'floor' }, { preset: { file: 'Dungeon_A2', idx: 0, name: 'Ground A (Dirt Cave)' } });
      const wall = terrain('Dinding Gua', '#3d3530', { mode: 'wall' }, { preset: { file: 'Dungeon_A4', idx: 0, name: 'Wall A (Dirt Cave)' } });
      terrains = [floor, wall];
      objects = [
        obj('Batu tinggi', floor.id, 0.008, 'Dungeon_B', [[64], [72]]),
        obj('Kerikil', floor.id, 0.03, 'Dungeon_B', [[48]]),
        obj('Batu besar', floor.id, 0.012, 'Dungeon_B', [[56]]),
      ];
    } else {
      const floor = terrain('Lantai', '#9a9a8c', { mode: 'floor' }, { preset: { file: 'Dungeon_A5', idx: 32, name: 'Cobblestones A' } });
      const wall = terrain('Dinding', '#4a4a58', { mode: 'wall' }, { preset: { file: 'Dungeon_A4', idx: 16, name: 'Wall I (Stone)' } });
      terrains = [floor, wall];
      objects = [
        obj('Pilar batu', floor.id, 0.008, 'Dungeon_B', [[80], [88]]),
        obj('Reruntuhan', floor.id, 0.015, 'Dungeon_B', [[104]]),
        obj('Kerikil', floor.id, 0.02, 'Dungeon_B', [[49]]),
      ];
    }
    return { params, terrains, objects, biomes, hill, stairs };
  }

  /** Lengkapi konfigurasi lama (preset tersimpan / file kerja) dengan kunci baru. */
  function upgradeConfig(type, c) {
    const def = defaultConfig(type);
    if (!c || !Array.isArray(c.terrains)) return def;
    c.params = Object.assign({}, def.params, c.params || {});
    if (!Array.isArray(c.objects)) c.objects = [];
    if (!Array.isArray(c.biomes) || !c.biomes.length) c.biomes = def.biomes;
    if (c.hill === undefined) c.hill = def.hill;
    if (c.stairs === undefined) c.stairs = def.stairs;
    for (const o of c.objects) { if (o.biome === undefined) o.biome = ''; if (o.join === undefined) o.join = null; }
    return c;
  }

  /**
   * Isi tile kosong dari preset bila tileset proyek memuat file gambar yang cocok.
   * tilesetNames: 9 nama gambar; labels: array (per set) berisi daftar nama label atau null.
   */
  function applyPresets(cfg, tilesetNames, labels) {
    let changed = 0;
    const resolve = preset => {
      if (!preset) return null;
      const set = tilesetNames.indexOf(preset.file);
      if (set < 0) return null;
      let idx = preset.idx;
      const lab = labels && labels[set];
      if (lab && preset.name) {
        const found = lab.indexOf(preset.name);
        if (found >= 0) idx = found;
      }
      // Hanya bagian atap (baris genap) A4 yang dipakai untuk dinding
      if (set === 3 && Math.floor((80 + idx) / 8) % 2 === 1) idx -= 8;
      return tileFromIndex(set, idx);
    };
    for (const key of ['hill', 'stairs']) {
      const c = cfg[key];
      if (c && !c.tile) {
        const tile = resolve(c.preset);
        if (tile) { c.tile = tile; changed++; }
      }
    }
    for (const t of cfg.terrains) {
      if (!t.tile) {
        const tile = resolve(t.preset);
        if (tile) { t.tile = tile; changed++; }
      }
    }
    for (const o of cfg.objects) {
      if (objTiles(o) || !o.preset) continue;
      const set = tilesetNames.indexOf(o.preset.file);
      if (set < 4) continue;
      if (o.preset.tiles) {
        const conv = m => m.map(row => row.map(idx => (idx ? tileFromIndex(set, idx).id : 0)));
        o.tiles = conv(o.preset.tiles);
        o.join = o.preset.join ? conv(o.preset.join) : null;
        changed++;
      } else {
        const tile = resolve(o.preset);
        if (tile && tile.id) { o.tiles = [[tile.id]]; changed++; }
      }
    }
    return changed;
  }

  // ---------------------------------------------------------------------------
  // Generator
  // ---------------------------------------------------------------------------
  /** Hilangkan petak tipis/tunggal yang membuat autotile RPG Maker tampak rusak. */
  function smoothGrid(grid, W, H, passes) {
    for (let p = 0; p < passes; p++) {
      const out = grid.slice();
      const tally = new Map();
      for (let y = 0; y < H; y++) {
        for (let x = 0; x < W; x++) {
          const i = y * W + x, c = grid[i];
          let same = 0;
          tally.clear();
          for (let dy = -1; dy <= 1; dy++) {
            for (let dx = -1; dx <= 1; dx++) {
              if (!dx && !dy) continue;
              const nx = x + dx, ny = y + dy;
              if (nx < 0 || ny < 0 || nx >= W || ny >= H) continue;
              const v = grid[ny * W + nx];
              if (v === c) same++;
              tally.set(v, (tally.get(v) || 0) + 1);
            }
          }
          if (same < 3) {
            let best = c, bc = -1;
            for (const [v, n] of tally) if (n > bc) { bc = n; best = v; }
            out[i] = best;
          }
        }
      }
      grid.set(out);
    }
  }

  class MinHeap {
    constructor() { this.k = []; this.v = []; }
    get size() { return this.k.length; }
    push(key, val) {
      const k = this.k, v = this.v;
      let i = k.length;
      k.push(key); v.push(val);
      while (i > 0) {
        const p = (i - 1) >> 1;
        if (k[p] <= key) break;
        k[i] = k[p]; v[i] = v[p]; i = p;
      }
      k[i] = key; v[i] = val;
    }
    pop() {
      const k = this.k, v = this.v;
      const top = v[0];
      const lk = k.pop(), lv = v.pop();
      if (k.length) {
        let i = 0;
        const n = k.length;
        for (;;) {
          let c = 2 * i + 1;
          if (c >= n) break;
          if (c + 1 < n && k[c + 1] < k[c]) c++;
          if (k[c] >= lk) break;
          k[i] = k[c]; v[i] = v[c]; i = c;
        }
        k[i] = lk; v[i] = lv;
      }
      return top;
    }
  }

  /** A* 4 arah. cost(from, to) -> biaya langkah (Infinity = tidak boleh). */
  function astar(W, H, start, goal, cost, minCost) {
    const N = W * H;
    const g = new Float64Array(N).fill(Infinity);
    const from = new Int32Array(N).fill(-1);
    const gx = goal % W, gy = Math.floor(goal / W);
    const heap = new MinHeap();
    g[start] = 0;
    heap.push(0, start);
    const D = [[1, 0], [-1, 0], [0, 1], [0, -1]];
    while (heap.size) {
      const cur = heap.pop();
      if (cur === goal) break;
      const cx = cur % W, cy = Math.floor(cur / W);
      for (const [dx, dy] of D) {
        const nx = cx + dx, ny = cy + dy;
        if (nx < 0 || ny < 0 || nx >= W || ny >= H) continue;
        const ni = ny * W + nx;
        const c = cost(cur, ni);
        if (!isFinite(c)) continue;
        const ng = g[cur] + c;
        if (ng < g[ni]) {
          g[ni] = ng;
          from[ni] = cur;
          heap.push(ng + (Math.abs(nx - gx) + Math.abs(ny - gy)) * minCost, ni);
        }
      }
    }
    if (!isFinite(g[goal])) return null;
    const path = [];
    for (let c = goal; c !== -1; c = from[c]) path.push(c);
    return path;
  }

  function genTerrain(st, rng) {
    const { width: W, height: H, params: P, terrains: T } = st;
    const N = W * H;
    const grid = new Uint8Array(N);
    const noise = makeNoise2D(rng);
    const elev = new Float32Array(N);
    const f = 1 / Math.max(2, P.scale);
    const ox = rng() * 1000, oy = rng() * 1000;
    for (let y = 0; y < H; y++) {
      for (let x = 0; x < W; x++) {
        elev[y * W + x] = fbm(noise, x * f + ox, y * f + oy, P.octaves | 0 || 1);
      }
    }
    normalize(elev);
    if (P.island > 0) {
      for (let y = 0; y < H; y++) {
        for (let x = 0; x < W; x++) {
          const dx = ((x + 0.5) / W) * 2 - 1, dy = ((y + 0.5) / H) * 2 - 1;
          const d = 0.5 * Math.max(Math.abs(dx), Math.abs(dy)) + 0.5 * Math.sqrt(dx * dx + dy * dy) / Math.SQRT2;
          elev[y * W + x] -= P.island * d * d * 1.6;
        }
      }
      normalize(elev);
    }
    // Ubah ke persentil: ambang 0.3 = 30% area terendah.
    const order = Array.from({ length: N }, (_, i) => i).sort((a, b) => elev[a] - elev[b]);
    for (let r = 0; r < N; r++) elev[order[r]] = r / Math.max(1, N - 1);
    const heights = T.map((t, i) => ({ t, i })).filter(o => o.t.rule.mode === 'height')
      .sort((a, b) => a.t.rule.min - b.t.rule.min);
    if (heights.length) {
      for (let i = 0; i < N; i++) {
        let k = heights[0].i;
        for (const h of heights) if (elev[i] >= h.t.rule.min) k = h.i;
        grid[i] = k;
      }
    }
    smoothGrid(grid, W, H, P.smooth | 0);

    T.forEach((t, ti) => {
      if (t.rule.mode !== 'patch') return;
      const pi = T.findIndex(o => o.id === t.rule.parent);
      const nz = makeNoise2D(rng);
      const pf = 1 / Math.max(2, t.rule.scale || 12);
      const px = rng() * 1000, py = rng() * 1000;
      if (pi < 0) return;
      const m = new Float32Array(N);
      for (let y = 0; y < H; y++) for (let x = 0; x < W; x++) m[y * W + x] = fbm(nz, x * pf + px, y * pf + py, 3);
      normalize(m);
      const thr = t.rule.threshold == null ? 0.6 : t.rule.threshold;
      const bi = t.rule.biome && st.biomes ? st.biomes.findIndex(b => b.id === t.rule.biome) : -1;
      for (let i = 0; i < N; i++) {
        if (grid[i] === pi && m[i] >= thr && (bi < 0 || !st.biome || st.biome[i] === bi)) grid[i] = ti;
      }
    });
    smoothGrid(grid, W, H, Math.min(1, P.smooth | 0));
    return grid;
  }

  /** Peta biome: tiap sel ikut biome dengan nilai noise (+ bobot porsi) tertinggi. */
  function genBiomes(st, rng) {
    const { width: W, height: H, params: P } = st;
    const B = st.biomes || [];
    const out = new Uint8Array(W * H);
    if (B.length < 2) return out;
    const f = 1 / Math.max(2, P.biomeScale || 18);
    const fields = B.map(b => ({ n: makeNoise2D(rng), ox: rng() * 1000, oy: rng() * 1000, w: Math.log(Math.max(0.05, b.share == null ? 1 : b.share)) * 0.25 }));
    for (let y = 0; y < H; y++) {
      for (let x = 0; x < W; x++) {
        let best = 0, bv = -Infinity;
        fields.forEach((fd, k) => {
          const v = fbm(fd.n, x * f + fd.ox, y * f + fd.oy, 3) + fd.w;
          if (v > bv) { bv = v; best = k; }
        });
        out[y * W + x] = best;
      }
    }
    smoothGrid(out, W, H, 1);
    return out;
  }

  /** Tingkat bukit (0 = tanah biasa). Dataran terlalu tipis diratakan agar tebing tetap punya atap. */
  function genLevels(st, rng) {
    const { width: W, height: H, params: P, terrains: T, grid } = st;
    const N = W * H;
    const level = new Uint8Array(N);
    if (!(P.hills > 0) || !st.hill) return level;
    const noise = makeNoise2D(rng);
    const f = 1 / Math.max(2, P.hillScale || 16);
    const ox = rng() * 1000, oy = rng() * 1000;
    const h = new Float32Array(N);
    for (let y = 0; y < H; y++) for (let x = 0; x < W; x++) h[y * W + x] = fbm(noise, x * f + ox, y * f + oy, 4);
    const order = Array.from({ length: N }, (_, i) => i).sort((a, b) => h[a] - h[b]);
    for (let r = 0; r < N; r++) h[order[r]] = r / Math.max(1, N - 1);
    const maxL = Math.max(1, Math.min(3, P.hillLevels | 0));
    const start = 1 - P.hills, step = P.hills / maxL;
    for (let i = 0; i < N; i++) {
      if (T[grid[i]].block || h[i] < start) continue;
      level[i] = Math.min(maxL, 1 + Math.floor((h[i] - start) / step));
    }
    smoothGrid(level, W, H, 3);
    for (let i = 0; i < N; i++) if (T[grid[i]].block) level[i] = 0;
    fixLevelThickness(level, W, H, Math.max(1, P.cliffHeight | 0), maxL);
    return level;
  }

  function fixLevelThickness(level, W, H, cliffH, maxL) {
    const minV = cliffH + 3, minH = 3;
    for (let L = maxL; L >= 1; L--) {
      for (let x = 0; x < W; x++) {
        let y = 0;
        while (y < H) {
          if (level[y * W + x] < L) { y++; continue; }
          let y2 = y;
          while (y2 < H && level[y2 * W + x] >= L) y2++;
          if (y2 - y < minV && y2 < H) for (let k = y; k < y2; k++) level[k * W + x] = L - 1;
          y = y2;
        }
      }
      for (let y = 0; y < H; y++) {
        let x = 0;
        while (x < W) {
          if (level[y * W + x] < L) { x++; continue; }
          let x2 = x;
          while (x2 < W && level[y * W + x2] >= L) x2++;
          if (x2 - x < minH) for (let k = x; k < x2; k++) level[y * W + k] = L - 1;
          x = x2;
        }
      }
    }
  }

  /** Sel tebing: bagian dataran yang berada tepat di atas tanah yang lebih rendah. */
  function classifyCliffs(st) {
    const { width: W, height: H, params: P, level } = st;
    if (!level || isWallType(st.type)) return null;
    const ch = Math.max(1, (P.cliffHeight | 0) || 2);
    const face = new Uint8Array(W * H);
    for (let y = 0; y < H; y++) {
      for (let x = 0; x < W; x++) {
        const i = y * W + x, L = level[i];
        if (!L) continue;
        for (let k = 1; k <= ch; k++) {
          const ny = y + k;
          if (ny >= H) break;
          const l2 = level[ny * W + x];
          if (l2 < L) { face[i] = 1; break; }
          if (l2 > L) break;
        }
      }
    }
    return face;
  }

  /** Jalan otomatis: titik acak dihubungkan ke titik terdekat sebelumnya. */
  function genAutoPaths(st, rng) {
    const { width: W, height: H, params: P, terrains: T, grid } = st;
    const pathT = T.find(t => t.rule.mode === 'path');
    if (!pathT || !(P.roads > 0)) return [];
    const face = classifyCliffs(st);
    const cand = [];
    for (let i = 0; i < W * H; i++) {
      const x = i % W, y = Math.floor(i / W);
      if (x > 1 && y > 1 && x < W - 2 && y < H - 2 && !T[grid[i]].block && !(face && face[i])) cand.push(i);
    }
    if (cand.length < 2) return [];
    const want = (P.roads | 0) + 1, minDist = Math.min(W, H) / 4;
    const pts = [];
    for (let tries = 0; pts.length < want && tries < want * 60; tries++) {
      const c = cand[Math.floor(rng() * cand.length)];
      const cx = c % W, cy = Math.floor(c / W);
      if (pts.every(p => Math.hypot(p % W - cx, Math.floor(p / W) - cy) >= minDist)) pts.push(c);
    }
    const out = [];
    for (let k = 1; k < pts.length; k++) {
      let best = pts[0], bd = Infinity;
      for (let j = 0; j < k; j++) {
        const d = Math.hypot(pts[j] % W - pts[k] % W, Math.floor(pts[j] / W) - Math.floor(pts[k] / W));
        if (d < bd) { bd = d; best = pts[j]; }
      }
      out.push({
        id: 'auto' + k, name: 'Jalan otomatis ' + k, auto: true, terrain: pathT.id, stairs: 0,
        width: Math.max(1, P.roadWidth | 0), gap: 0,
        points: [[pts[k] % W, Math.floor(pts[k] / W)], [best % W, Math.floor(best / W)]],
      });
    }
    return out;
  }

  /**
   * Rute semua jalan (A* antar titik arah). Jalan hanya boleh berpindah tingkat lewat dinding tebing
   * secara vertikal; sel tebing yang dilewati menjadi tangga.
   */
  function routePaths(st) {
    const { width: W, height: H, terrains: T, grid, level } = st;
    const N = W * H;
    const terr = new Int16Array(N).fill(-1);
    const stairs = new Uint16Array(N);
    const paths = st.paths || [];
    if (!paths.length || isWallType(st.type)) return { terrain: terr, stairs };
    const face = st.cliff;
    const L = i => (level ? level[i] : 0);
    const F = i => (face ? face[i] : 0);
    const blocked = i => T[grid[i]] && T[grid[i]].block;
    const defPath = T.findIndex(t => t.rule.mode === 'path');
    const defStairs = st.stairs && st.stairs.tile && st.stairs.tile.id ? st.stairs.tile.id : 0;
    for (const p of paths) {
      let ti = p.terrain ? T.findIndex(t => t.id === p.terrain) : -1;
      if (ti < 0) ti = defPath;
      if (ti < 0) continue;
      const stairId = p.stairs || defStairs;
      const pts = (p.points || []).filter(([x, y]) => x >= 0 && y >= 0 && x < W && y < H).map(([x, y]) => y * W + x);
      if (pts.length < 2) continue;
      const cost = (a, b) => {
        if (blocked(b)) return Infinity;
        if (Math.abs(a - b) === 1) {
          if (F(a) || F(b) || L(a) !== L(b)) return Infinity;
        } else if (!F(a) && !F(b) && L(a) !== L(b)) {
          return Infinity;
        }
        if (terr[b] === ti) return 0.4;
        return F(b) ? 3 : 1;
      };
      const cells = [];
      for (let k = 1; k < pts.length; k++) {
        const r = astar(W, H, pts[k - 1], pts[k], cost, 0.4);
        if (r) for (const c of r) cells.push(c);
      }
      const w = Math.max(1, Math.min(3, p.width | 0 || 1));
      const rng = makeRng('jalan|' + p.id);
      for (const c of cells) {
        const cx = c % W, cy = Math.floor(c / W), onFace = F(c);
        if (!onFace && p.gap > 0 && rng() < p.gap) continue;
        for (let dy = 0; dy < (onFace ? 1 : w); dy++) {
          for (let dx = 0; dx < w; dx++) {
            const nx = cx + dx, ny = cy + dy;
            if (nx >= W || ny >= H) continue;
            const j = ny * W + nx;
            if (F(j)) { if (onFace && stairId) stairs[j] = stairId; continue; }
            if (onFace || blocked(j) || L(j) !== L(c)) continue;
            terr[j] = ti;
          }
        }
      }
    }
    return { terrain: terr, stairs };
  }

  /** Hitung ulang data turunan (tebing & rute jalan). */
  function prepare(st) {
    st.cliff = classifyCliffs(st);
    st.routes = routePaths(st);
    return st;
  }

  function roleIdx(T, role) {
    const i = T.findIndex(t => t.rule.mode === role);
    return i < 0 ? (role === 'floor' ? 0 : 1) : i;
  }

  function keepLargestFloor(isWall, W, H) {
    const N = W * H, label = new Int32Array(N).fill(-1);
    let best = -1, bestSize = 0, id = 0;
    const stack = [];
    for (let s = 0; s < N; s++) {
      if (isWall[s] || label[s] >= 0) continue;
      let size = 0;
      stack.push(s); label[s] = id;
      while (stack.length) {
        const c = stack.pop(); size++;
        const x = c % W, y = Math.floor(c / W);
        const nb = [x > 0 ? c - 1 : -1, x < W - 1 ? c + 1 : -1, y > 0 ? c - W : -1, y < H - 1 ? c + W : -1];
        for (const n of nb) if (n >= 0 && !isWall[n] && label[n] < 0) { label[n] = id; stack.push(n); }
      }
      if (size > bestSize) { bestSize = size; best = id; }
      id++;
    }
    for (let i = 0; i < N; i++) if (!isWall[i] && label[i] !== best) isWall[i] = 1;
  }

  function genCave(st, rng) {
    const { width: W, height: H, params: P, terrains: T } = st;
    const N = W * H;
    const top = (P.wallHeight | 0) + 1;
    const inside = (x, y) => x >= 1 && x < W - 1 && y >= top && y < H - 1;
    let wall = new Uint8Array(N);
    for (let y = 0; y < H; y++) for (let x = 0; x < W; x++) wall[y * W + x] = (!inside(x, y) || rng() < P.fill) ? 1 : 0;
    for (let s = 0; s < (P.steps | 0); s++) {
      const next = new Uint8Array(N);
      for (let y = 0; y < H; y++) {
        for (let x = 0; x < W; x++) {
          const i = y * W + x;
          if (!inside(x, y)) { next[i] = 1; continue; }
          let c = 0;
          for (let dy = -1; dy <= 1; dy++) for (let dx = -1; dx <= 1; dx++) {
            if (!dx && !dy) continue;
            const nx = x + dx, ny = y + dy;
            if (nx < 0 || ny < 0 || nx >= W || ny >= H || wall[ny * W + nx]) c++;
          }
          next[i] = c >= 5 ? 1 : c <= 3 ? 0 : wall[i];
        }
      }
      wall = next;
    }
    keepLargestFloor(wall, W, H);
    const F = roleIdx(T, 'floor'), Wl = roleIdx(T, 'wall');
    const grid = new Uint8Array(N);
    for (let i = 0; i < N; i++) grid[i] = wall[i] ? Wl : F;
    return grid;
  }

  function genDungeon(st, rng) {
    const { width: W, height: H, params: P, terrains: T } = st;
    const N = W * H;
    const top = (P.wallHeight | 0) + 2;
    const floor = new Uint8Array(N);
    const rooms = [];
    const rMin = Math.max(3, P.roomMin | 0), rMax = Math.max(rMin, P.roomMax | 0);
    const pad = (P.wallHeight | 0) + 2;
    for (let a = 0; a < P.rooms * 20 && rooms.length < P.rooms; a++) {
      const w = rng.int(rMin, rMax);
      const h = rng.int(Math.max(3, rMin - 1), Math.max(3, rMax - 2));
      if (w > W - 4 || h > H - top - 2) continue;
      const x = rng.int(2, W - w - 2), y = rng.int(top, H - h - 2);
      if (rooms.some(r => x < r.x + r.w + pad && x + w + pad > r.x && y < r.y + r.h + pad && y + h + pad > r.y)) continue;
      rooms.push({ x, y, w, h });
    }
    const carve = (x, y) => {
      if (x >= 1 && x < W - 1 && y >= top && y < H - 1) floor[y * W + x] = 1;
    };
    for (const r of rooms) for (let y = r.y; y < r.y + r.h; y++) for (let x = r.x; x < r.x + r.w; x++) carve(x, y);
    const cw = Math.max(1, P.corridor | 0);
    const hline = (x1, x2, y) => { for (let x = Math.min(x1, x2); x <= Math.max(x1, x2) + cw - 1; x++) for (let k = 0; k < cw; k++) carve(x, y + k); };
    const vline = (y1, y2, x) => { for (let y = Math.min(y1, y2); y <= Math.max(y1, y2) + cw - 1; y++) for (let k = 0; k < cw; k++) carve(x + k, y); };
    const center = r => [r.x + Math.floor((r.w - cw) / 2), r.y + Math.floor((r.h - cw) / 2)];
    for (let k = 1; k < rooms.length; k++) {
      const [ax, ay] = center(rooms[k]);
      let best = null, bd = Infinity;
      for (let j = 0; j < k; j++) {
        const [bx, by] = center(rooms[j]);
        const d = Math.abs(ax - bx) + Math.abs(ay - by);
        if (d < bd) { bd = d; best = [bx, by]; }
      }
      const [bx, by] = best;
      if (rng() < 0.5) { hline(ax, bx, ay); vline(ay, by, bx); }
      else { vline(ay, by, ax); hline(ax, bx, by); }
    }
    const F = roleIdx(T, 'floor'), Wl = roleIdx(T, 'wall');
    const grid = new Uint8Array(N);
    for (let i = 0; i < N; i++) grid[i] = floor[i] ? F : Wl;
    return grid;
  }

  /**
   * Lapisan objek: alas (baris bawah) di lapisan 3 (z=2), bagian atas di lapisan 4 (z=3),
   * sehingga daun pohon depan boleh menutupi batang pohon di belakangnya.
   * own2/own3 menyimpan (indeks jangkar + 1) pemilik tiap sel agar objek selalu dihapus utuh.
   */
  function makeObjectLayers(N) {
    return { deco: new Uint16Array(N), deco3: new Uint16Array(N), own2: new Int32Array(N), own3: new Int32Array(N) };
  }

  /** Fungsi (i, isAlas) -> true bila sel tidak boleh ditempati objek. */
  function objectBlocker(st, forScatter) {
    if (isWallType(st.type)) {
      const cls = classifyWalls(st);
      return i => cls[i] !== 0;
    }
    const face = st.cliff, r = st.routes, T = st.terrains, grid = st.grid;
    return (i, isBase) => isBase && !!((face && face[i]) || (r && r.stairs[i]) ||
      (forScatter && ((r && r.terrain[i] >= 0) || (T[grid[i]] && T[grid[i]].block))));
  }

  /** Bisakah objek ditaruh dengan alas kiri-bawah di (x, y)? ti = terrain wajib untuk alas (-1 = bebas). */
  function canPlace(st, tiles, x, y, ti, block) {
    const { width: W, height: H, grid, own2, own3, terrains: T } = st;
    const h = tiles.length, w = tiles[0].length;
    for (let r = 0; r < h; r++) {
      for (let c = 0; c < w; c++) {
        if (!tiles[r][c]) continue;
        const cx = x + c, cy = y - (h - 1) + r;
        if (cx < 0 || cy < 0 || cx >= W || cy >= H) return false;
        const i = cy * W + cx;
        if (block && block(i, r === h - 1)) return false;
        if (r === h - 1) {
          if (own2[i]) return false;
          if (ti >= 0 && grid[i] !== ti) return false;
        } else if (own3[i]) {
          return false;
        }
      }
    }
    return true;
  }

  function placeObject(st, tiles, x, y) {
    const W = st.width, h = tiles.length, anchor = y * W + x + 1;
    for (let r = 0; r < h; r++) {
      for (let c = 0; c < tiles[r].length; c++) {
        if (!tiles[r][c]) continue;
        const i = (y - (h - 1) + r) * W + x + c;
        if (r === h - 1) { st.deco[i] = tiles[r][c]; st.own2[i] = anchor; }
        else { st.deco3[i] = tiles[r][c]; st.own3[i] = anchor; }
      }
    }
  }

  /** Hapus utuh semua objek yang menyentuh sel i. Mengembalikan kotak sel yang berubah, atau null. */
  function removeObjectsAt(st, i) {
    const anchors = new Set();
    if (st.own2[i]) anchors.add(st.own2[i]);
    if (st.own3[i]) anchors.add(st.own3[i]);
    if (!anchors.size) return null;
    const W = st.width;
    const box = [Infinity, Infinity, -Infinity, -Infinity];
    for (const a of anchors) {
      const ax = (a - 1) % W, ay = Math.floor((a - 1) / W);
      // Jangkar = sel kiri-bawah, jadi objek berada di atas & kanannya
      for (let y = Math.max(0, ay - 12); y <= ay; y++) {
        for (let x = ax; x <= Math.min(W - 1, ax + 12); x++) {
          const k = y * W + x;
          let hit = false;
          if (st.own2[k] === a) { st.own2[k] = 0; st.deco[k] = 0; hit = true; }
          if (st.own3[k] === a) { st.own3[k] = 0; st.deco3[k] = 0; hit = true; }
          if (hit) { box[0] = Math.min(box[0], x); box[1] = Math.min(box[1], y); box[2] = Math.max(box[2], x); box[3] = Math.max(box[3], y); }
        }
      }
    }
    return box;
  }

  function scatterObjects(st, rng) {
    const { width: W, height: H, objects, terrains: T } = st;
    st.deco.fill(0); st.deco3.fill(0); st.own2.fill(0); st.own3.fill(0);
    const B = st.biomes || [];
    const list = objects
      .map(o => ({ o, tiles: objTiles(o), ti: o.terrain ? T.findIndex(t => t.id === o.terrain) : -1, bi: o.biome ? B.findIndex(b => b.id === o.biome) : -1 }))
      .filter(e => e.tiles && (e.ti >= 0 || !e.o.terrain) && e.o.density > 0);
    if (!list.length) return;
    const block = objectBlocker(st, true);
    const N = W * H;
    const order = new Int32Array(N);
    for (let i = 0; i < N; i++) order[i] = i;
    for (let i = N - 1; i > 0; i--) { const j = Math.floor(rng() * (i + 1)); const t = order[i]; order[i] = order[j]; order[j] = t; }
    for (let k = 0; k < N; k++) {
      const i = order[k], x = i % W, y = Math.floor(i / W);
      for (const e of list) {
        if (rng() >= e.o.density) continue;
        if (e.bi >= 0 && st.biome && st.biome[i] !== e.bi) continue;
        if (canPlace(st, e.tiles, x, y, e.ti, block)) { placeObject(st, e.tiles, x, y); break; }
      }
    }
    refreshJoins(st);
  }

  /**
   * Hutan rapat: objek yang pucuknya menimpa alas objek lain memakai varian rapat (join),
   * dan kembali ke bentuk biasa bila tidak lagi bertumpuk.
   */
  function refreshJoins(st) {
    const W = st.width;
    const kinds = (st.objects || []).map(o => ({ t: objTiles(o), j: o.join })).filter(e =>
      e.t && e.j && e.j.length === e.t.length && e.j[0].length === e.t[0].length);
    if (!kinds.length) return;
    const anchors = new Set();
    for (let i = 0; i < st.own2.length; i++) { if (st.own2[i]) anchors.add(st.own2[i]); if (st.own3[i]) anchors.add(st.own3[i]); }
    for (const a of anchors) {
      const ax = (a - 1) % W, ay = Math.floor((a - 1) / W);
      for (const e of kinds) {
        const h = e.t.length, w = e.t[0].length;
        let fits = true, overlap = false;
        for (let r = 0; r < h && fits; r++) {
          for (let c = 0; c < w; c++) {
            if (!e.t[r][c]) continue;
            const x = ax + c, y = ay - (h - 1) + r;
            if (x >= W || y < 0) { fits = false; break; }
            const i = y * W + x, base = r === h - 1;
            const own = base ? st.own2[i] : st.own3[i], v = base ? st.deco[i] : st.deco3[i];
            if (own !== a || (v !== e.t[r][c] && v !== e.j[r][c])) { fits = false; break; }
            if (!base && st.own2[i] && st.own2[i] !== a) overlap = true;
          }
        }
        if (!fits) continue;
        const want = overlap ? e.j : e.t;
        for (let r = 0; r < h; r++) {
          for (let c = 0; c < w; c++) {
            if (!e.t[r][c]) continue;
            const i = (ay - (h - 1) + r) * W + ax + c;
            if (r === h - 1) st.deco[i] = want[r][c] || e.t[r][c];
            else st.deco3[i] = want[r][c] || e.t[r][c];
          }
        }
        break;
      }
    }
  }

  function generate(st) {
    const rng = makeRng(st.seed + '|' + st.type + '|' + st.width + 'x' + st.height);
    const N = st.width * st.height;
    st.biome = genBiomes(st, makeRng(st.seed + '|biome'));
    let grid;
    if (st.type === 'cave') grid = genCave(st, rng);
    else if (st.type === 'dungeon') grid = genDungeon(st, rng);
    else grid = genTerrain(st, rng);
    st.grid = grid;
    st.level = st.type === 'outside' ? genLevels(st, makeRng(st.seed + '|bukit')) : new Uint8Array(N);
    const manual = (st.paths || []).filter(p => !p.auto);
    st.paths = isWallType(st.type) ? [] : manual.concat(genAutoPaths(st, makeRng(st.seed + '|jalan')));
    prepare(st);
    Object.assign(st, makeObjectLayers(N));
    scatterObjects(st, makeRng(st.seed + '|objek'));
    return st;
  }

  // ---------------------------------------------------------------------------
  // Konversi ke data tile RPG Maker (6 lapisan)
  // ---------------------------------------------------------------------------
  const codeOf = t => (!t || !t.tile) ? -1 : (t.tile.auto != null ? AUTO + t.tile.auto : t.tile.id);

  /** 0 = lantai, 1 = muka dinding, 2 = atap/plafon dinding */
  function classifyWalls(st) {
    const { width: W, height: H, params: P, terrains: T, grid } = st;
    const F = roleIdx(T, 'floor');
    const hgt = Math.max(1, P.wallHeight | 0);
    const cls = new Uint8Array(W * H);
    for (let y = 0; y < H; y++) {
      for (let x = 0; x < W; x++) {
        const i = y * W + x;
        if (grid[i] === F) { cls[i] = 0; continue; }
        cls[i] = 2;
        for (let k = 1; k <= hgt; k++) {
          const ny = y + k;
          if (ny >= H) break;
          if (grid[ny * W + x] === F) { cls[i] = 1; break; }
        }
      }
    }
    return cls;
  }

  function resolveBase(T, t) {
    let cur = t, guard = 0;
    while (cur && cur.overlay && cur.base && guard++ < 8) cur = T.find(o => o.id === cur.base);
    return cur && !cur.overlay ? cur : null;
  }

  function buildData(st) {
    const { width: W, height: H, terrains: T, grid, deco, deco3, params: P } = st;
    const N = W * H;
    const data = new Uint16Array(N * 6);
    const lvl = !isWallType(st.type) && st.level && st.level.some(Boolean) ? st.level : null;
    const codes = [new Int32Array(N).fill(-1), new Int32Array(N).fill(-1)];
    let cls = null;
    if (isWallType(st.type)) {
      const F = roleIdx(T, 'floor'), Wl = roleIdx(T, 'wall');
      cls = classifyWalls(st);
      const fc = codeOf(T[F]), wc = codeOf(T[Wl]);
      const faceCode = wc >= AUTO && isWallTopKind(wc - AUTO) ? wc + 8 : wc;
      for (let i = 0; i < N; i++) codes[0][i] = cls[i] === 0 ? fc : cls[i] === 1 ? faceCode : wc;
    } else {
      const baseCode = T.map(t => (t.overlay && t.base ? codeOf(resolveBase(T, t)) : codeOf(t)));
      const topCode = T.map(t => (t.overlay && t.base ? codeOf(t) : -1));
      const route = st.routes, face = st.cliff;
      const hillCode = st.hill && st.hill.tile && st.hill.tile.auto != null && isWallTopKind(st.hill.tile.auto) ? AUTO + st.hill.tile.auto : -1;
      const hillBase = st.hill ? st.hill.base : null;
      const enc = (v, l) => (v >= AUTO ? v + l * LVL : v);
      for (let i = 0; i < N; i++) {
        const ti = route && route.terrain[i] >= 0 ? route.terrain[i] : grid[i];
        const t = T[ti], l = lvl ? lvl[i] : 0;
        if (face && face[i]) {
          const sid = route ? route.stairs[i] : 0;
          codes[0][i] = sid || (hillCode >= 0 ? enc(hillCode + 8, l) : enc(baseCode[ti], l));
          continue;
        }
        if (l > 0 && hillCode >= 0) {
          codes[0][i] = enc(hillCode, l);
          if (t.overlay && t.base) codes[1][i] = enc(codeOf(t), l);
          else if (t.rule.mode === 'path') codes[1][i] = enc(codeOf(t), l);
          else if (t.id !== hillBase && !t.block) codes[1][i] = -2 - ti; // diputuskan setelah tahu tepi dataran
          continue;
        }
        codes[0][i] = enc(baseCode[ti], l);
        codes[1][i] = enc(topCode[ti], l);
      }
      // Tanah lain (bukan rumput dasar bukit) di atas dataran hanya di bagian dalam, agar bibir tebing tetap terlihat
      for (let y = 0; y < H; y++) {
        for (let x = 0; x < W; x++) {
          const i = y * W + x, v = codes[1][i];
          if (v > -2) continue;
          let inner = true;
          for (let dy = -1; dy <= 1 && inner; dy++) {
            for (let dx = -1; dx <= 1; dx++) {
              const nx = x + dx, ny = y + dy;
              if (nx < 0 || ny < 0 || nx >= W || ny >= H) continue;
              const j = ny * W + nx;
              if (lvl[j] !== lvl[i] || (face && face[j])) { inner = false; break; }
            }
          }
          codes[1][i] = inner ? enc(codeOf(T[-2 - v]), lvl[i]) : -1;
        }
      }
    }
    const isTopCode = v => v >= AUTO && isWallTopKind((v - AUTO) % LVL);
    for (let z = 0; z < 2; z++) {
      const c = codes[z];
      const at = (x, y) => (x < 0 || y < 0 || x >= W || y >= H) ? null : c[y * W + x];
      for (let y = 0; y < H; y++) {
        for (let x = 0; x < W; x++) {
          const i = y * W + x, v = c[i];
          if (v < 0) continue;
          if (v >= AUTO) {
            const k = (v - AUTO) % LVL;
            if (k >= 80 && usesWallTable(k)) {
              data[z * N + i] = autoId(k, wallSideShape(at, x, y, v, isTopCode));
              continue;
            }
            const myL = lvl ? lvl[i] : 0;
            const same = (dx, dy) => {
              const nx = x + dx, ny = y + dy;
              if (nx < 0 || ny < 0 || nx >= W || ny >= H) return true;
              const j = ny * W + nx;
              // Tanah di kaki tebing menyatu dengan dataran yang lebih tinggi (tanpa garis tepi)
              if (z === 0 && lvl && lvl[j] > myL) return true;
              return c[j] === v;
            };
            data[z * N + i] = autoId(k, shapeFor(k, same));
          } else {
            data[z * N + i] = v;
          }
        }
      }
    }
    for (let i = 0; i < N; i++) {
      data[2 * N + i] = deco[i];
      data[3 * N + i] = deco3 ? deco3[i] : 0;
      data[5 * N + i] = (T[grid[i]] && T[grid[i]].region) | 0;
    }
    if (cls && P.shadow) {
      for (let y = 0; y < H; y++) for (let x = 1; x < W; x++) {
        const i = y * W + x;
        if (cls[i] === 0 && cls[i - 1] !== 0) data[4 * N + i] = 5; // bayangan separuh kiri
      }
    }
    const face = !isWallType(st.type) ? st.cliff : null;
    if (lvl && P.shadow) {
      for (let y = 0; y < H; y++) for (let x = 1; x < W; x++) {
        const i = y * W + x;
        if (face && face[i]) continue;
        if ((face && face[i - 1]) || lvl[i - 1] > lvl[i]) data[4 * N + i] = 5;
      }
    }
    return { data, cls, face, level: lvl, width: W, height: H };
  }

  function makeMapJson(built, tilesetId, base) {
    const map = base ? JSON.parse(JSON.stringify(base)) : {
      autoplayBgm: false, autoplayBgs: false, battleback1Name: '', battleback2Name: '',
      bgm: { name: '', pan: 0, pitch: 100, volume: 90 }, bgs: { name: '', pan: 0, pitch: 100, volume: 90 },
      disableDashing: false, displayName: '', encounterList: [], encounterStep: 30, note: '',
      parallaxLoopX: false, parallaxLoopY: false, parallaxName: '', parallaxShow: true, parallaxSx: 0, parallaxSy: 0,
      scrollType: 0, specifyBattleback: false, events: [],
    };
    map.tilesetId = tilesetId;
    map.width = built.width;
    map.height = built.height;
    map.data = Array.from(built.data);
    if (!Array.isArray(map.events)) map.events = [];
    return map;
  }

  const api = {
    ID, AUTO, FLOOR_TABLE, WALL_TABLE, FLOOR_SHAPE, TYPES, TYPE_LABEL, PARAM_DEFS, DEFAULT_SIZE, TYPE_TILESET_HINT,
    kindOf, autoId, usesWallTable, isWallTopKind, isWaterfallKind, thumbShape, shapeFor, wallSideShape, tileSource, normalTileId,
    labelIndex, setOfTile, tileFromIndex,
    makeRng, makeNoise2D, isWallType, uid, defaultConfig, applyPresets,
    generate, scatterObjects, buildData, objTiles, canPlace, placeObject, removeObjectsAt, makeObjectLayers,
    prepare, classifyCliffs, routePaths, refreshJoins, objectBlocker, upgradeConfig, fixLevelThickness, LVL, classifyWalls, makeMapJson, roleIdx,
  };
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  else root.RMCore = api;
})(typeof window !== 'undefined' ? window : globalThis);
