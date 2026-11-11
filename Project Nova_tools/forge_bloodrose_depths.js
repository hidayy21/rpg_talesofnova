// Generate the three maps under Villa Bloodrose with rm-map-forge: two dungeon levels (rooms & corridors) and the
// cave passage that climbs out to the garden.
// node forge_bloodrose_depths.js <out.json>   (map_villa_bloodrose_depths.py runs it)
const path = require('path');
const C = require(path.join(__dirname, 'rm-map-forge', 'core.js'));

function level(seed, w, h, params, floorAuto, wallAuto, type = 'dungeon') {
  const cfg = C.defaultConfig(type);
  const st = Object.assign({ type, width: w, height: h, seed, paths: [] }, cfg);
  Object.assign(st.params, params);
  const floor = st.terrains.find(t => t.rule.mode === 'floor');
  const wall = st.terrains.find(t => t.rule.mode === 'wall');
  floor.tile = { auto: floorAuto };
  wall.tile = { auto: wallAuto };
  st.objects = [];                       // dressing is placed room by room afterwards
  C.generate(st);
  const built = C.buildData(st);
  return { width: w, height: h, data: Array.from(built.data), cls: Array.from(built.cls) };
}

// Dungeon tileset (4): A2 kinds are auto 16+k, A4 kinds auto 80+k (the top; the face is k+8)
const out = {
  // B1 - the cellars: dark cobbles, warm brick between timber posts
  cellars: level('bloodrose-cellars-7', 46, 36,
    { rooms: 8, roomMin: 5, roomMax: 10, corridor: 2, wallHeight: 2, shadow: true }, 16 + 10, 80 + 22),
  // B2 - the old foundations, older than the house: framed stone slabs, grey ashlar
  foundations: level('bloodrose-foundations-3', 48, 40,
    { rooms: 7, roomMin: 6, roomMax: 12, corridor: 2, wallHeight: 2, shadow: true }, 16 + 30, 80 + 21),
  // the Rose Way - a natural passage winding up from the foundations to the garden: dark soil floor and walls
  roseway: level('rose-way-1', 30, 44, { fill: 0.5, steps: 5, wallHeight: 2, shadow: true }, 16 + 2, 80 + 2, 'cave'),
};
require('fs').writeFileSync(process.argv[2], JSON.stringify(out));
for (const [k, v] of Object.entries(out)) console.log(k, v.width + 'x' + v.height, 'floor cells', v.cls.filter(c => c === 0).length);
