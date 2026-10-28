#!/bin/bash
# Mac: double-click to playtest the game without opening the RPG Maker MV editor.
# Uses MV's own playtest runtime (test mode: F9 debug, F5 reloads the game).
cd "$(dirname "$0")/.."
NW="$HOME/Library/Application Support/Steam/steamapps/common/RPG Maker MV/RPG Maker MV.app/Contents/MacOS/nwjs-osx-test/Game.app/Contents/MacOS/nwjs"
if [ ! -x "$NW" ]; then
    echo "MV playtest runtime not found at:"
    echo "  $NW"
    read -p "Press Enter to close"
    exit 1
fi
"$NW" "$PWD" test >/dev/null 2>&1 &
