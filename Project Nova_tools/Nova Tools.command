#!/bin/bash
# Mac: double-click to open Nova Tools (Map Editor + Tileset Wizard)
cd "$(dirname "$0")"
# Use the first Python that has Pillow (conda's, Homebrew's or the system one)
for PY in python3 /opt/miniconda3/bin/python3 /opt/anaconda3/bin/python3 /opt/homebrew/bin/python3 /usr/local/bin/python3 /usr/bin/python3; do
    if command -v "$PY" >/dev/null 2>&1 && "$PY" -c "import PIL" >/dev/null 2>&1; then
        "$PY" nova_tools.py
        exit
    fi
done
echo "Nova Tools needs Python 3 with Pillow. Install it with:  python3 -m pip install pillow"
read -p "Press Enter to close"
