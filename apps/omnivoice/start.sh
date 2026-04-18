#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

echo
echo " ================================"
echo "  OmniVoice Local — Starting..."
echo " ================================"
echo

if [ ! -f venv/bin/activate ]; then
    echo " Virtual environment not found."
    echo " Please run  ./install.sh  first."
    exit 1
fi

# shellcheck disable=SC1091
source venv/bin/activate

echo " Opening browser at http://localhost:8765"
echo " Press Ctrl+C to stop the server."
echo

# Try to open the browser in the background on common Linux setups.
( sleep 1.5 && (xdg-open http://localhost:8765 >/dev/null 2>&1 || true) ) &

python app.py
