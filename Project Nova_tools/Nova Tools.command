#!/bin/bash
# Mac: double-click to open Nova Tools (Map Editor, Tileset Wizard, Character)
cd "$(dirname "$0")"
# Use the first Python that has Pillow and numpy (conda's, Homebrew's or the system one)
for PY in python3 /opt/miniconda3/bin/python3 /opt/anaconda3/bin/python3 /opt/homebrew/bin/python3 /usr/local/bin/python3 /usr/bin/python3; do
    if command -v "$PY" >/dev/null 2>&1 && "$PY" -c "import PIL, numpy" >/dev/null 2>&1; then
        "$PY" nova_tools.py
        exit
    fi
done
echo "Nova Tools needs Python 3 with Pillow and numpy. Install them with:  python3 -m pip install pillow numpy"
read -p "Press Enter to close"
