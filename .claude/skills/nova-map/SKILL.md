---
name: nova-map
description: Build or change a map for Tales of Nova (RPG Maker MV) with the Nova Tools Python map library instead of the stock editor - towns, interiors, forests, dungeons, farms, winter villages. Uses every tile sheet the project has (Outside/Inside/Dungeon/World/SF plus all NovaTilesetEx extra sheets - PM_*, Nova_*, Avy_*, WizardCastle - read live from the project), renders a preview to check the layout, validates links, then saves so the map can be touched up in the Nova Tools Map Editor. Use whenever the user asks to make, design, extend, decorate or fix a map ("buatkan map", "bikin map", "tambah map", "dekor map", "perbaiki map", "map baru", "interior", "dungeon", "hutan", "desa").
---

# Building maps for Tales of Nova

The tools live in `Project Nova_tools/` (run everything from that folder). The user writes Indonesian - reply in
Indonesian; map names, dialogue and code comments stay in English like the rest of the game.

## The library

| File | What it gives you |
|---|---|
| `nova_maplib.py` (`L`) | `MapBuilder`: `rect/cell` paint autotiles on layers 0-1 as `('A2', kind)`, `('A5', n)` or `('ID', tile_id)`; `put(x, y, tile, layer=2/3)` places objects; `render()` preview; `save()` writes `MapXXX.json` + `MapInfos.json`. Events: `page`, `cmd`, `text`, `say`, `transfer`, `door_page`, `exit_page`, `char`, `tile_image`, `common_event`, move-route codes. **`L.ext(sheet, n)`** = tile n of any NovaTilesetEx sheet, usable on every map. |
| `town_kit.py` | `Town` (Outside tileset 2, `<outdoor>` note, widens edge exits on save): `building`, `lamp`, `big_tree`, `tent`, `tall`, `relief`, `door`, `locked_door`, `exit`, `npc`, `critter` (with `<pen>` areas), `obj`, `sign`; named ground/wall/roof/B/C constants; `PROP[...]` = Nova_Market_D props (list in `make_town_tiles.py`); `wander_route`. |
| `interior_kit.py` | `Room` (Inside tileset 3, `<ambient: #hex>` note): `wall_block`, `counter`, `two`, `wide`, `exit_door`, `door` (back-wall door with its dark hole), `locked_door` (text only), `seal_wall_tops` (call last), `keeper`, `npc`, `obj`, `look`; named Inside_B/C furniture (`CHAIR_A` pairs, not `CHAIR`); `choice_shop`. |
| `kingdom.py` (`K`) | Map ids, `NAMES` (editor name, display name) and `ARRIVE` points. Both sides of every link read from here. |
| `data_ids.py` | Shop common events, item ids, inn price. |
| `validate_maps.py` | `check({id: map})` - transfers land on walkable tiles, doorsteps open, no stacked events. |
| `edge_exits.py` | Widens edge exits to the whole open crossing (`Town.save` already runs it). |
| `tile_numbers.py` | `python3 tile_numbers.py <Sheet> ...` -> `_work/tiles_<Sheet>.png`, each tile with its number. |
| `rm-map-forge/` | The user's map generator (browser app; `core.js` also runs in Node): cave and dungeon (rooms & corridors) layouts with walls, faces and shadows. Use it from Python through a small Node script - see `forge_bloodrose_depths.js` + `map_villa_bloodrose_depths.py` for caves and dungeons, `forge_outdoor.py` for everything outdoors (`ForgeMap`: forge tiles underneath, our props/events on top, rooms found again from the floor, stairs on whole wall). Fixed seeds keep the map stable. |
| `forge_outdoor.py` + `forge_outdoor.js` | **rm-map-forge for every outdoor natural map** (forests, wilds, the woods round a village): `forge(names, w, h, seed, ground, road, paths, trees, keep, hill, stairs, patch, overlay, zones)` runs the forge's `outside` generator (noise ground, raised ground with cliffs, roads A*-routed through your points with stairs on cliffs) and packs your trees densely everywhere the road and `keep` cells are not. Returns a `ForgeOutdoor` (a `Town`: sign, npc, door, exit, lamp work; edge exits widened on save) with `is_road`, `has_object`, `is_face`, `clear`, `reach(starts)`. See "Forests, wilds and villages" below; examples `map_hollow_wood.py`, `map_mistveil.py`, `map_lilydale.py`. |
| `Referensi Map/` (project root) | **165 maps from classic RPGs** (DQ, FF4-6, Chrono Trigger, Tales of Phantasia, Secret/Trials of Mana, Golden Sun, Lagoon...), named `Game - Place (type).png` - `(kerajaan)` castles/capitals, `(salju)` snow, `(reruntuhan)` ruins, plain = towns and villages. Study them before laying out any town, village, castle or snow map - see "Reference maps". |
| `game_screenshot.js` | Screenshots from the **running game** (every plugin and shader on) without RPG Maker: `node game_screenshot.js shots.json out_dir` serves the project, runs it in headless Edge (WebGL via SwiftShader) and saves one PNG per `{name, map, x, y, override, switches, bars, message}`. `override` sets NovaAtmosphere tags (e.g. `{"cinematic": 0}` for a before/after). Use it to show the user how a map really looks in game. |
| `atlas.py` | `atlas(tileset, 'A2', range(32), out)` - sample block of every autotile kind of a sheet. |
| `_work/tilenames.txt` | `Sheet:n:Name` for the stock Outside/Inside sheets (search it before opening images). |

Good references for style and helpers: `map_lilydale.py` (village in a forest clearing), `map_hollow_wood.py` / `map_mistveil.py` (forged woods, a misty labyrinth), `map_market.py`, `map_hollow_farm.py`, `map_city_gate.py` (towns),
`map_interiors.py` (rooms), `map_prison.py`, `map_briarwood_entrance.py` (forest/dungeon-ish, chests, crystals),
`map_villa_bloodrose_interiors.py` (a whole castle: hall, wings, rooms behind doors, open side doorways between
maps, a switch-gated door, twin stairs, a balcony, lights on every candle and window), `map_frosthollow.py`
(terraced town on several ground levels).

## Every tile sheet is available - use them

Tilesets (`data/Tilesets.json`), each map picks one with its A1-A5 ground:

| id | Tileset | Use for |
|---|---|---|
| 1 | Overworld | world map only |
| 2 | Outside (+ Nova_Market_D) | towns, roads, farms - `Town` |
| 3 | Inside | rooms - `Room` |
| 4 | Dungeon | caves, crypts, vaults |
| 5 / 6 | SF Outside / SF Inside | sci-fi / ancient-tech (Sealed Vault-like places) |
| 9 | PandaMaru Village | Outside ground + `PM_Town_A3` roofs |
| 10 | PandaMaru Forest | Outside ground + `PM_Hills_A5` cliffs/hills |
| 11 | PandaMaru Interior | Inside ground |
| 12 | PandaMaru Winter | Outside ground + `PM_Town_A3` |
| 13 | Avy Town | Outside ground + `Avy_Town_A3` roofs/walls |
| 14 | Avy Castle | Outside ground + `Avy_Castle_A4` castle walls |
| 15 / 16 | Avy Nature / Avy Palm | `Avy_Nature_A2` / `Avy_Palm_A2` ground (forest floor, beach, palms) |
| 17 / 18 | Avy Landmarks 1 / 2 | Outside ground, big landmark objects (towers, lighthouse, giant tree...) |
| 19 | Avy Ship | `Avy_Ship_A2` decks, ship hulls |
| 20 | Wizard Castle | `WizardCastle_A2/A4` floors and walls (+ Inside_B/C as C/D) - magic academy, mage towers |
| 21 | Medieval Town | Outside (B/C/D as in towns, so `town_kit` works) + `MedievalTown_A2/A3` (mixed: half-timber walls, shingle/slate roofs from the MedievalVillage pack plus Outside/PM/Avy picks - names in `make_medieval_tileset.py` `MED_ROOF`/`MED_WALL`/`MED_GROUND`) + `MedievalVillage_B` in slot E (gables, dormers, chimneys, 2-tall windows/doors). Rebuild with `make_medieval_tileset.py --save`. Used by Lilydale. |

That table is a snapshot: new packs are added with `import_tilesets.py` and become new tilesets. Read the live list
from `data/Tilesets.json` before choosing.

Object sheets: **any map can place tiles from any of them** with `L.ext(name, n)` (passability comes along
automatically, the preview draws them too). The list grows with every import, so **never work from memory - print
the live list** (sheet name and the tileset that holds its passability):

```
python3 -c "import nova_maplib as L; [print(n, t) for n, t in sorted(L.ext_sheets().values())]"
```

As of the last update: the stock `Outside/Inside/Dungeon/World/SF_*` B/C and A5 sheets, `Nova_*` (Market_D,
InsideProps, Houses1/2, Beds, Nature, Farm), `PM_*` (Market, Village1/2, Rome_B, Hills_A5, Nature1-3, Forest,
NobleInterior, Beds, Rooms, Extras, XmasDecoration, Winter1/2, Blockhouse), `Avy_Town_B`-`B4`, `Avy_Castle_B`-`B4`,
`Avy_Nature_B`-`B4`, `Avy_Landmarks_B`-`B8`, `Avy_Ship_B`-`B3`, `WizardCastle_B` - 64 sheets.

Do not stop at the kit constants: the PandaMaru, Nova and Avy sheets have the richer trees, cliffs, houses, market
stalls, noble furniture and winter dressing. Before decorating, go through the live list, pick **every** sheet that
fits the theme (by name first, then by looking), run
`tile_numbers.py` on them and **look at the images** (Read the PNG) to pick tiles by number. Multi-tile objects
(trees, houses, beds) span several numbers: the number printed under a tile is what `L.ext` takes, and the tile
below it is n+8 (B-E sheets are two 8-column halves; the right half starts at 128). Put the upper parts on layer 3 (drawn above the
player, `☆`-flagged tiles) and the base on layer 2, as `Town.big_tree` does. When you settle on a set of tiles for a
theme, give them names in a small dict at the top of the script (or in the kit, if they will be reused) so the
next map can use them by name. Delete the `_work/tiles_*.png` images you generated when done unless the user wants
them kept.

When you hand the map over, say which sheets you looked at and which you used (and, briefly, why the other
fitting ones were left out), so the user can see nothing was skipped.

## Workflow

1. **Plan with the user only what you cannot decide**: where the map sits in the world (which map links to it and on
   which edge/door), size, mood. Everything else - layout, props, NPC lines - is yours to propose.
   Before proposing a layout, open 2-4 maps from `Referensi Map/` that match the place (village, castle town, snow
   town...) and say which you looked at and what general ideas you take from them.
2. **Ids and links**: next free map id = first unused index in `data/MapInfos.json`. Add the constant, `NAMES` entry
   and `ARRIVE` points to `kingdom.py` (or the chapter's own module if it is not part of the capital), and add the
   matching exit/door on the neighbour map (see "Changing existing maps").
3. **Write `map_<name>.py`** in the style of the existing scripts: header comment saying what the map is and its id,
   `sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))` (not the old `D:/...` path), the kit import,
   `W, H`, the builder, then sections - ground, buildings/walls, props, doors, exits, NPCs. BGM/BGS from what exists in
   `audio/` (the RTP set: Town1-2, Field1-2, Castle1-2, Dungeon1-3, Theme*, Ship*; BGS City, River, Sea, Wind, Night,
   Drips, Darkness, Storm1-2, Quake). Map notes the plugins read: `<outdoor>` (night + day/night), `<ambient: #hex>`,
   `<bloom: n>`, `<tilt shift: n>` and the other NovaAtmosphere/NovaLighting tags (see their `@help`). Mood and
   battle background are kept in two tables, not in the map script: add the map to `map_moods.py` (`grade` preset -
   warm, noble, coast, forest, mystic, interior, gloom, arcane - plus `fog`, `sunbeams`, `particles`) and to
   `battlebacks.py` (an `img/battlebacks1` floor + `img/battlebacks2` backdrop), then run both with `--apply` after
   saving the map. End with the
   usual `__main__`: `python3 map_x.py preview.png [--grid]` renders, `--save` writes.
4. **Preview and look**: render to the scratchpad with `--grid`, Read the PNG, fix what looks wrong (floating roofs,
   walls without a top, blocked doorsteps, empty stretches, props on walls, repeated patterns). Iterate until it looks
   like a hand-made RPG Maker map: varied ground (paths, tufts, flowers, A5 detail), clustered props rather than
   scattered singles, every building with door + windows + sign, edges framed (trees, cliffs, walls) so the map does
   not end in nothing. Show the user the final preview.
5. **Validate** before saving:
   ```python
   import json, validate_maps as V, nova_maplib as L
   maps = {i: json.load(open(L.DATA + 'Map%03d.json' % i, encoding='utf8')) for i in ids_of_this_map_and_its_neighbours}
   print(V.check(maps))
   ```
   (validate after saving, or build the dict from `tile_data()` for the new map before saving.)
6. **Save** only when the RPG Maker editor is closed (`tileset_wizard.editor_running()`; if it is open, ask the user
   to close it - the editor overwrites map files and MapInfos.json on its next save). Copy the old `MapXXX.json`
   (if any) to `../../rpg_talesofnova_backups/` (the `<project>_backups` folder next to the game folder) first, then
   `python3 map_x.py --save`.
7. **Hand off**: tell the user to open it in Nova Tools (`Nova Tools.command` / `.bat`, http://localhost:8765) for
   touch-ups, and in the editor only after Nova Tools is done. Commit only when asked (push needs the Bash sandbox
   disabled).

## Reference maps (`Referensi Map/`)

Classic RPG maps kept in the project on purpose as study material. Use them for **general ideas only** - how a
village is framed by forest, how roads lead to a square, where the inn and the church sit, how a castle town steps
up to its keep, how dense props are - then lay out our own plan (never copy a layout, see below). Make thumbnails
into the scratchpad (`PIL.Image.thumbnail((1000, 1000))`) and Read them; many sheets also show the interiors, which
help when planning a building's rooms. There are no forest maps in the folder: for woods, take the framing of the
towns' surroundings (the dense tree walls round FF4's Mist, the forest ring round many DQ/Mana villages).

## Forests, wilds and villages: rm-map-forge (`forge_outdoor.py`)

Any natural outdoor map starts from the forge, not from hand-placed trees:
- **Road**: `paths=[(points, width)]` - a few waypoints from edge to edge; the forge routes between them. Side ways
  (dead ends, a chest, a shrine) are extra paths starting on the main road. The edge cells of the road are the
  exits; read them back with `m.is_road(x, 0)` and line them up with the neighbour (same x, offset kept).
- **Trees**: `Tree(rows, density, band, sheet)` - rows top to bottom, the last row stands on the ground (layer 2),
  the rest go on layer 3. `band=(y0, y1)` limits a kind to rows of the map, so a wood can change as you walk
  (green below, dying above). Densities ~0.2-0.3 per kind give a closed forest; three passes fill the gaps.
  **Every row of a tree is kept off the road and `keep` cells**, because PM_* crowns block: a crown over the road
  would close it.
- **Ground**: `ground`, `patch` (noise patches), `overlay` (layer-1 patches), `zones=[(auto, y0, y1)]` (another ground
  over a band of rows, ragged edge - withering grass). Auto kinds as the forge counts them: `A2(k)` = 16+k, `A4(k)` =
  80+k. Outside_A2: 0 meadow, 1 dirt path (meadow edges), 8 dirt, 9 grass on dirt, 12 dead grass (yellow), 20
  withered grass, 23 moss; **15 'Soil' is empty on this sheet**. Hills: `hill=A4(32)` Ledge A (meadow) with
  `stairs=L.A5 + 27`; a hill top always shows its ledge's grass, so in a withered zone keep hills off or few.
- **Labyrinths** (a misty wood): after forging, close every open cell that is not road or glade with blocking 1x1
  fillers next to the road (dead shrub Outside_B 177, boulders 95/103, Nova_Nature thorns 12/13, stump 92) and
  `BLOCKER` (767) further in - otherwise the gaps between trees are shortcuts through the maze.
- **Villages**: forge only the forest ring - `keep` = the clearing plus every building/field rect with a margin
  (decide those rects before forging), `paths=[]`; then `m.rect(0, 0, W-1, H-1, GRASS)` paints our own ground and
  the village is laid by hand with the `Town` helpers. Cells of the ring no tree fitted get `BLOCKER` with a bush on
  layer 3 drawn over it.
- **Check**: `m.reach(arrivals)` - every door step, NPC neighbour, chest and both exits must be in it.
- Tree groupings checked on renders (PM_Forest): round green 3x3 `(16,17,18)(24,25,26)(32,33,34)`, small round 3x2
  `(40,41,42)(48,49,50)`, pines 2x2 `(112,113)(120,121)` / `(114,115)(122,123)`, big 5x6 rows 3-7/11-15/.../43-47,
  mossy 3x3 `(136..)(144..)(152..)`, mossy 2x3 `(139,140)(147,148)(155,156)`, `(141..)(149..)(157..)`, bare 3x3
  `(176..)(184..)(192..)` and `(181..)(189..)(197..)`, bare 2x3 `(179,180)(187,188)(195,196)`, twigs 3x2
  `(160..)(168..)`, the violet "rose" tree 5x7 `(200-204)...(248-252)`; lilies in water `9`, `10`. Outside_B: big tree
  2x2 `(112,113)(120,121)`. `!Crystal`: index 2 = green (healing), index 0 direction 6 = purple (dark crystal).

## Changing existing maps

Many maps were touched up by hand in the editor / Nova Tools after their script last ran (commits named "Editor
edits: ..."; `git status` may also show uncommitted map edits). **Never re-run `--save` of an existing script
without checking**: diff the script's output against the current `MapXXX.json` first, and if the file has hand
edits, change the JSON directly instead - a short `patch_<what>.py` that loads the map, edits `data` (index =
`(layer * h + y) * w + x`) and `events`, and writes with `L.write_map` (see `patch_harbor_east.py`,
`patch_city_links.py`). If you do regenerate, copy the hand edits into the script's "touch-ups made by hand"
section first (as `map_market.py` does).

## Designing from the story, not from clichés

Read `Story/Story_Plan.md` (and the character profiles in `Story/`) before laying a map out: which chapter uses the
place, what scenes happen there, who lives there. Build the rooms those scenes need, and furnish them from the
people (a daughter who longs to travel gets maps and travel books). Do **not** decorate from stereotypes of the race
or theme - the user rejected a graveyard put in a vampire family's grounds "just because they're vampires".

Castles and big houses - the plan the user expects:
- **Every room that can host a story event is its own map**, entered through a door. Big rooms side by side (hall,
  dining room, music room) are separate maps joined by **open doorways in the side wall** (an exit event on each
  carved border cell - `side_gap` in the villa script), not merged into one map.
- Upper floors have a gallery over the hall and **corridors to the left and right wings**, rooms off them by door.
- Add the house's life even where the player cannot go: servants' rooms, a kitchen, the master's bedchamber as
  **locked doors** with a line of text or a servant's remark.
- A room the story opens later: a door with a locked page plus a page conditioned on a switch. Name the switch in
  `System.json` (load it, change the one name, `json.dumps(..., ensure_ascii=False, separators=(',', ':'))` writes it
  back byte-identical - check that round trip first) and keep its id in `kingdom.py`.
- Never copy the floor plan of a level from another game, even when asked - offer a plan of our own that keeps the
  generic castle ideas (bridge, courtyard, hall with twin stairs, wings, secret passage).

## Pitfalls

- Layer 0/1 hold autotiles (`rect`/`cell`), layers 2/3 hold objects (`put`); layer 1 is for overlays such as fences,
  tables/counters, water edges over ground.
- A3/A4 wall *tops* are passable in the tileset - walls need their face rows, and `edge_exits` treats tops as closed.
  In interiors that means thin partitions and the border can be walked on: `Room.seal_wall_tops()` lays
  `INVISIBLE_WALL` (`L.ext('Avy_Ship_B3', 1)`, the only blank blocking tile in all the sheets) over every top.
- **Doors need the dark hole under them.** A `!Door1` event plays its opening frames over whatever tile is there; with
  no hole the player sees bare wall. `Town.door` and `Room.door` put `DOOR_HOLE` (Outside_B 69; 71 for round-topped
  styles) under the event - any door built by hand must too. `!$Gate1` (3x2 gate) draws its own darkness. Doors that
  never open (`locked_door`) need no hole. The tile below a door must be walkable.
- Exits along an edge: use `Town.exit` with every lane cell; arrivals one tile inside the neighbour's edge.
- Events must not share a tile; NPCs must not stand on the arrival tile of a transfer. Light events (`<light: ...>`
  notes) count too - put a torch's light note on the blocker/prop event that already stands there.
- **`K.ARRIVE` is one dict literal: a repeated key silently replaces the earlier one** (the villa's
  `dining_from_hall` was overridden by the Academy's and sent players to the wrong map). Prefix keys with the place
  (`villa_dining_from_hall`) and check for duplicates after adding links.
- Passability by sheet: every PM_* tile with art is blocked (rugs, stairs, arch tops too - a PM rug blocks the floor,
  a PM stair cannot be climbed: use the WizardCastle_B stair, all rows on layer 2). Every Avy_* tile is passable
  (towers, walls): add blocker events or parapets. Check a tile's flag with
  `validate_maps.flags_for(ts)[L.ext(sheet, n)]` (0x0f bits = blocked, 0x10 = drawn above, passable).
- A thing on a back wall that the player should read (a portrait, a map) goes on the **bottom** face row, so its
  look event is next to the floor.
- Multi-tile objects get cut when a piece is missed or misread (trees, chairs = backrest over seat, canopy beds =
  canopy on layer 3 over the bed, triple windows that look like doubles). Crop the sheet at 1.4-2x with a grid, then
  render a full-size crop of the placed objects and look before saving. Groupings found so far are in the auto-memory
  file `tile-object-groupings.md`.
- `validate_maps.check` does not test reachability: flood-fill from every `K.ARRIVE` point of the map (respecting
  tile flags and priority-1 events) and make sure every NPC, door and look event has a reachable neighbour, and no
  wall top is reachable.
- The preview is daylight: for a dark map also render an approximation (multiply by the `<ambient>` colour, add a
  blurred glow per `<light:>` event) so you and the user judge the real mood.
- Patching a hand-edited map: build the script's map, diff `tile_data()` against the JSON's `data`, and write back
  only the cells you meant to change - never the whole map, never `MapInfos.json`.
- A raw B/C tile number means **that tileset's own** B/C sheet: Inside_B 53 on the Dungeon tileset draws Dungeon_B 53
  (crystals instead of a wine rack). Tiles from any other sheet always go through `L.ext(sheet, n)`.
- `map_moods.py --apply` and `battlebacks.py --apply` rewrite every listed map whose note differs from the table -
  including maps the user has tuned by hand (Map048's fog banks). Run them without `--apply` first and, if a
  hand-edited map is listed, apply the tags to the new maps only (`set_tag` on just those files).
- Re-saving a map from its script drops the mood tags and battle background that the two tables put on it. Make the
  script's `save()` put them back (as `map_villa_bloodrose_depths.save` does), or run the tables again after saving.
- NovaLighting lights some character sheets on its own (`!Flame`, `!Other2` 1/3/5/7, `!Door2`, `!Crystal` - see its
  *Character Lights* parameter), whatever the direction: a cold brazier needs `<light: 0, #000000>`, a blue one its
  own colour. A light that comes on with a page (a brazier lit by the player) goes in a **Comment on that page**
  (`cmd(108, ['<light: ...>'])`), not in the event note.
- Puzzles: events can show any extra-sheet tile (`tile_image(L.ext(...))`); swap a gate or grate by page conditions on
  a switch or a variable (`variableValue` = at least). Flood-fill twice - with the barrier shut (the lever must be
  reachable) and open (everything else must be).
- Windows line endings: write files with `newline=''` as the library does, keep `ensure_ascii=False`.
- **Save order with edge exits**: `Town.save` widens edge exits by opening the neighbour map, so a chain of new maps
  fails on the first save if the next map does not exist yet - save them all, then save them all once more.
- `map_moods.py --apply` re-orders the tags of maps whose note it rewrites (Map048 shows as changed only for that):
  for new maps apply `set_tag` and the battleback to those files only.
- Shell heredocs break on mixed quotes in long Python snippets: write the snippet to a scratchpad file and run it.
