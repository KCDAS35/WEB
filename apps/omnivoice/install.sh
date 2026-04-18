#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

echo
echo " ========================================="
echo "  OmniVoice Local App — First-Time Setup"
echo " ========================================="
echo

if ! command -v python3 >/dev/null 2>&1; then
    echo " ERROR: python3 not found."
    echo " Install it first:  sudo apt install python3 python3-venv python3-pip"
    exit 1
fi

if ! python3 -c "import venv" >/dev/null 2>&1; then
    echo " ERROR: python3-venv is not installed."
    echo " Install it first:  sudo apt install python3-venv"
    exit 1
fi

echo " [1/4] Creating virtual environment..."
python3 -m venv venv

echo " [2/4] Activating environment..."
# shellcheck disable=SC1091
source venv/bin/activate

echo " [3/4] Installing dependencies..."
pip install --upgrade pip -q
pip install -r requirements.txt

echo " [4/4] Done!"
echo
echo " The OmniVoice model (~4 GB) will download automatically"
echo " the first time you run the app and generate audio."
echo
echo " Run  ./start.sh  to launch the app."
echo
