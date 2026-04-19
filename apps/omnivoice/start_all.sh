#!/usr/bin/env bash
# start_all.sh — brings up OmniVoice, Voxtral, and Fish Speech on one pod.
# Run by AUTO_INSTALL in runpod_deploy.py after the repo is checked out.
#
# Services:
#   OmniVoice    → port 8765   (foreground)
#   Voxtral      → port 8766   (background)
#   Fish Speech  → port 7860   (background, Gradio webui)
#
# Logs land in /workspace/*.log so they survive pod restarts on MooseFS.

set -u

export HF_HOME=/workspace/hf-cache
export TRANSFORMERS_CACHE=/workspace/hf-cache
mkdir -p /workspace/hf-cache

REPO=/workspace/WEB
cd "$REPO"

echo "==> Installing shared Python dependencies..."
pip install -q \
    fastapi "uvicorn[standard]" python-multipart \
    soundfile numpy \
    transformers accelerate huggingface_hub \
    omnivoice

echo "==> Pre-downloading Voxtral weights (background)..."
nohup python3 -c "
from huggingface_hub import snapshot_download
snapshot_download('mistralai/Voxtral-4B-TTS-2603', cache_dir='/workspace/hf-cache')
" > /workspace/voxtral-download.log 2>&1 &

echo "==> Cloning + installing Fish Speech (background)..."
(
  cd /workspace
  [ -d fish-speech ] || git clone https://github.com/fishaudio/fish-speech.git
  cd fish-speech
  pip install -e . --quiet
  # fish-speech gradio ui lives at tools/run_webui.py or tools.webui
  nohup python3 -m tools.webui \
      --listen 0.0.0.0:7860 \
      > /workspace/fish-speech.log 2>&1 &
) > /workspace/fish-speech-install.log 2>&1 &

echo "==> Launching Voxtral server on :8766 (background)..."
nohup python3 "$REPO/apps/voxtral/app.py" \
    > /workspace/voxtral.log 2>&1 &

echo "==> Launching OmniVoice on :8765 (foreground)..."
cd "$REPO/apps/omnivoice"
exec python3 app.py
