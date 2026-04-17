#!/usr/bin/env bash
set -e

echo
echo " ================================"
echo "  OmniVoice Local — Starting..."
echo " ================================"
echo

cd "$(dirname "$0")"

if [ ! -f venv/bin/activate ]; then
    echo " Virtual environment not found."
    echo " Please run ./install.sh first."
    exit 1
fi

# shellcheck disable=SC1091
source venv/bin/activate
echo " Opening browser at http://localhost:8765"
echo " Press Ctrl+C to stop the server."
echo
python app.py
