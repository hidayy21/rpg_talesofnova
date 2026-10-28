@echo off
rem Windows: double-click to playtest the game without opening the RPG Maker MV editor.
rem Uses MV's own playtest runtime (test mode: F9 debug, F5 reloads the game).
cd /d "%~dp0.."
set "NW="
for %%P in (
    "%ProgramFiles(x86)%\Steam\steamapps\common\RPG Maker MV\nwjs-win-test\Game.exe"
    "%ProgramFiles%\Steam\steamapps\common\RPG Maker MV\nwjs-win-test\Game.exe"
    "%ProgramFiles(x86)%\KADOKAWA\RPGMV\nwjs-win-test\Game.exe"
    "%ProgramFiles%\KADOKAWA\RPGMV\nwjs-win-test\Game.exe"
) do if not defined NW if exist %%P set "NW=%%~P"
if not defined NW (
    echo MV playtest runtime ^(nwjs-win-test\Game.exe^) not found.
    echo Edit Playtest.bat and add the path of your RPG Maker MV folder.
    pause
    exit /b 1
)
start "" "%NW%" "%CD%" test
