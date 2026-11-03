---
name: nova-map
description: Build or change a map for Tales of Nova (RPG Maker MV) with the Nova Tools Python map library instead of the stock editor - towns, interiors, forests, dungeons, farms, winter villages. Uses every tile sheet the project has (Outside/Inside/Dungeon/World/SF plus all NovaTilesetEx extra sheets - PM_*, Nova_*), renders a preview to check the layout, validates links, then saves so the map can be touched up in the Nova Tools Map Editor. Use whenever the user asks to make, design, extend, decorate or fix a map ("buatkan map", "bikin map", "tambah map", "dekor map", "perbaiki map", "map baru", "interior", "dungeon", "hutan", "desa").
---

# Building maps for Tales of Nova

The tools live in `Project Nova_tools/` (run everything from that folder). The user writes Indonesian - reply in
Indonesian; map names, dialogue and code comments stay in English like the rest of the game.

## The library

| File | What it gives you |
|---|---|
| `nova_maplib.py` (`L`) | `MapBuilder`: `rect/cell` paint autotiles on layers 0-1 as `('A2', kind)`, `('A5', n)` or `('ID', tile_id)`; `put(x, y, tile, layer=2/3)` places objects; `render()` preview; `save()` writes `MapXXX.json` + `MapInfos.json`. Events: `page`, `cmd`, `text`, `say`, `transfer`, `door_page`, `exit_page`, `char`, `tile_image`, `common_event`, move-route codes. **`L.ext(sheet, n)`** = tile n of any NovaTilesetEx sheet, usable on every map. |
| `town_kit.py` | `Town` (Outside tileset 2, `<outdoor>` note, widens edge exits on save): `building`, `lamp`, `big_tree`, `tent`, `tall`, `relief`, `door`, `locked_door`, `exit`, `npc`, `critter` (with `<pen>` areas), `obj`, `sign`; named ground/wall/roof/B/C constants; `PROP[...]` = Nova_Market_D props (list in `make_town_tiles.py`); `wander_route`. |
| `interior_kit.py` | `Room` (Inside tileset 3, `<ambient: #hex>` note): `wall_block`, `counter`, `two`, `wide`, `exit_door`, `keeper`, `npc`, `obj`, `look`; named Inside_B/C furniture; `choice_shop`. |
| `kingdom.py` (`K`) | Map ids, `NAMES` (editor name, display name) and `ARRIVE` points. Both sides of every link read from here. |
| `data_ids.py` | Shop common events, item ids, inn price. |
| `validate_maps.py` | `check({id: map})` - transfers land on walkable tiles, doorsteps open, no stacked events. |
| `edge_exits.py` | Widens edge exits to the whole open crossing (`Town.save` already runs it). |
| `tile_numbers.py` | `python3 tile_numbers.py <Sheet> ...` -> `_work/tiles_<Sheet>.png`, each tile with its number. |
| `atlas.py` | `atlas(tileset, 'A2', range(32), out)` - sample block of every autotile kind of a sheet. |
| `_work/tilenames.txt` | `Sheet:n:Name` for the stock Outside/Inside sheets (search it before opening images). |

Good references for style and helpers: `map_market.py`, `map_hollow_farm.py`, `map_city_gate.py` (towns),
`map_interiors.py` (rooms), `map_prison.py`, `map_briarwood_entrance.py` (forest/dungeon-ish, chests, crystals).

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

Object sheets: **any map can place tiles from any of these** with `L.ext(name, n)` (slot list = NovaTilesetEx
"Extra Sheets" in `js/plugins.js`; passability comes along automatically, the preview draws them too):
`Outside_B/C`, `Inside_B/C`, `Dungeon_B/C`, `World_B/C`, `SF_Outside_B/C`, `SF_Inside_B/C`, `Nova_Market_D`,
`Outside_A5`, `Inside_A5`, `Dungeon_A5`, `SF_Outside_A5`, `Nova_InsideProps`, `Nova_Houses1`, `Nova_Houses2`,
`Nova_Beds`, `Nova_Nature`, `Nova_Farm`, `PM_Market`, `PM_Village1`, `PM_Village2`, `PM_Rome_B`, `PM_Hills_A5`,
`PM_Nature1-3`, `PM_Forest`, `PM_NobleInterior`, `PM_Beds`, `PM_Rooms`, `PM_Extras`, `PM_XmasDecoration`,
`PM_Winter1/2`, `PM_Blockhouse`.

Do not stop at the kit constants: the PandaMaru and Nova sheets have the richer trees, cliffs, houses, market
stalls, noble furniture and winter dressing. Before decorating, list the sheets that fit the theme, run
`tile_numbers.py` on them and **look at the images** (Read the PNG) to pick tiles by number. Multi-tile objects
(trees, houses, beds) span several numbers: the number printed under a tile is what `L.ext` takes, and the tile
below it is n+8 (B-E sheets are two 8-column halves; the right half starts at 128). Put the upper parts on layer 3 (drawn above the
player, `☆`-flagged tiles) and the base on layer 2, as `Town.big_tree` does. When you settle on a set of tiles for a
theme, give them names in a small dict at the top of the script (or in the kit, if they will be reused) so the
next map can use them by name. Delete the `_work/tiles_*.png` images you generated when done unless the user wants
them kept.

## Workflow

1. **Plan with the user only what you cannot decide**: where the map sits in the world (which map links to it and on
   which edge/door), size, mood. Everything else - layout, props, NPC lines - is yours to propose.
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

## Changing existing maps

Many maps were touched up by hand in the editor / Nova Tools after their script last ran (commits named "Editor
edits: ..."; `git status` may also show uncommitted map edits). **Never re-run `--save` of an existing script
without checking**: diff the script's output against the current `MapXXX.json` first, and if the file has hand
edits, change the JSON directly instead - a short `patch_<what>.py` that loads the map, edits `data` (index =
`(layer * h + y) * w + x`) and `events`, and writes with `L.write_map` (see `patch_harbor_east.py`,
`patch_city_links.py`). If you do regenerate, copy the hand edits into the script's "touch-ups made by hand"
section first (as `map_market.py` does).

## Pitfalls

- Layer 0/1 hold autotiles (`rect`/`cell`), layers 2/3 hold objects (`put`); layer 1 is for overlays such as fences,
  tables/counters, water edges over ground.
- A3/A4 wall *tops* are passable in the tileset - walls need their face rows, and `edge_exits` treats tops as closed.
- Doors: `Town.door` also places the dark door hole; the tile below a door must be walkable.
- Exits along an edge: use `Town.exit` with every lane cell; arrivals one tile inside the neighbour's edge.
- Events must not share a tile; NPCs must not stand on the arrival tile of a transfer.
- Windows line endings: write files with `newline=''` as the library does, keep `ensure_ascii=False`.
