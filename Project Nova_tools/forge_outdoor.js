// Outdoor layouts (forests, wilds, the ground round a village) with rm-map-forge's 'outside' generator: noise ground,
// raised ground with cliffs, roads routed along given points (stairs where they cross a cliff), and trees scattered
// densely everywhere the road and the kept cells are not. forge_outdoor.py builds the config and runs this.
//   node forge_outdoor.js <config.json> <out.json>
// config: { seed, width, height, params: {...outside params},
//           ground, patch: {auto, threshold, scale} | null, overlay: {...} | null, road, water: 0..1, waterAuto,
//           hill: autoKind | null, stairs: tileId,
//           paths: [{points: [[x, y], ...], width}], keep: [[x, y], ...],
//           objects: [{tiles: [[id, ...], ...], density, band: [y0, y1] | null}] }
// auto kinds as rm-map-forge numbers them: A1 k, A2 16 + k, A4 80 + k.
const fs = require('fs'), path = require('path');
const C = require(path.join(__dirname, 'rm-map-forge', 'core.js'));
const cfg = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));

const st = Object.assign({ type: 'outside', width: cfg.width, height: cfg.height, seed: cfg.seed, paths: [] },
                         C.defaultConfig('outside'));
Object.assign(st.params, { roads: 0 }, cfg.params || {});
const [water, grass, dirt, bush, road] = st.terrains;
water.tile = { auto: cfg.waterAuto || 0 };
grass.tile = { auto: cfg.ground };
road.tile = { auto: cfg.road };
if (cfg.water > 0) grass.rule.min = cfg.water; else { water.rule.min = -1; grass.rule.min = 0; }
if (cfg.patch) { dirt.tile = { auto: cfg.patch.auto }; dirt.rule.threshold = cfg.patch.threshold; dirt.rule.scale = cfg.patch.scale; dirt.rule.biome = ''; }
else dirt.rule.threshold = 2;
if (cfg.overlay) { bush.tile = { auto: cfg.overlay.auto }; bush.rule.threshold = cfg.overlay.threshold; bush.rule.scale = cfg.overlay.scale; bush.rule.biome = ''; }
else bush.rule.threshold = 2;
if (cfg.hill != null) st.hill.tile = { auto: cfg.hill }; else st.params.hills = 0;
st.stairs.tile = cfg.stairs ? { id: cfg.stairs } : null;
st.paths = (cfg.paths || []).map((p, k) => ({ id: 'p' + k, name: 'road ' + k, terrain: road.id, stairs: 0,
                                             width: p.width || 1, gap: 0, points: p.points }));
st.objects = [];                                   // our own scatter below
// zones: a second ground over a band of rows (e.g. grass withering toward the top of a wood), with a ragged edge
const zones = (cfg.zones || []).map((z, k) => {
  const t = { id: 'zone' + k, name: 'zone ' + k, color: '#888', tile: { auto: z.auto }, overlay: false, base: null,
              block: false, region: 0, rule: { mode: 'patch', parent: grass.id, threshold: 2, scale: 10 } };
  st.terrains.push(t);
  return Object.assign({ ti: st.terrains.length - 1 }, z);
});
C.generate(st);
if (zones.length) {
  const zr = C.makeRng(cfg.seed + '|zones'), gi = st.terrains.indexOf(grass), nz = C.makeNoise2D(zr);
  for (let y = 0; y < st.height; y++) for (let x = 0; x < st.width; x++) {
    const i = y * st.width + x;
    if (st.grid[i] !== gi) continue;
    for (const z of zones) {
      const e = Math.round((nz(x * 0.13, y * 0.13) + 0.5 * nz(x * 0.4 + 50, y * 0.4)) * (z.edge || 5));
      if (y >= z.y0 - e && y <= z.y1 + e) { st.grid[i] = z.ti; break; }
    }
  }
}

const W = st.width, H = st.height, N = W * H;
const keep = new Uint8Array(N);
for (const [x, y] of cfg.keep || []) if (x >= 0 && y >= 0 && x < W && y < H) keep[y * W + x] = 1;
const route = st.routes, face = st.cliff, level = st.level;
const isRoad = i => !!(route && (route.terrain[i] >= 0 || route.stairs[i]));
const isWater = i => st.terrains[st.grid[i]] === water;
// every cell of a tree must stay off the road, the kept cells, cliff faces and water, and on one ground level:
// the crowns of these trees block too, so a crown hanging over the road would close it
let anchorLevel = 0;
const block = (i, isBase) => {
  if (isRoad(i) || keep[i] || (face && face[i]) || isWater(i)) return true;
  return level && level[i] !== anchorLevel;
};
const rng = C.makeRng(cfg.seed + '|trees');
const order = Array.from({ length: N }, (_, i) => i);
for (let i = N - 1; i > 0; i--) { const j = Math.floor(rng() * (i + 1)); [order[i], order[j]] = [order[j], order[i]]; }
for (const pass of [0, 1, 2]) {                       // a second pass fills what the first left open
  for (const i of order) {
    const x = i % W, y = Math.floor(i / W);
    anchorLevel = level ? level[i] : 0;
    for (const o of cfg.objects) {
      if (o.band && (y < o.band[0] || y > o.band[1])) continue;
      if (rng() >= o.density * (pass ? 0.7 : 1)) continue;
      if (C.canPlace(st, o.tiles, x, y, -1, block)) { C.placeObject(st, o.tiles, x, y); break; }
    }
  }
}
const built = C.buildData(st);
fs.writeFileSync(process.argv[3], JSON.stringify({
  width: W, height: H, data: Array.from(built.data),
  road: Array.from({ length: N }, (_, i) => (isRoad(i) ? 1 : 0)),
  face: face ? Array.from(face) : [], level: level ? Array.from(level) : [],
  own: Array.from({ length: N }, (_, i) => (st.own2[i] || st.own3[i] ? 1 : 0)),
}));
