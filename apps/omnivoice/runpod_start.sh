#!/usr/bin/env bash
# One-command launch for OmniVoice relay on a RunPod pod.
# Usage (on the pod, after cloning this repo):
#   bash apps/omnivoice/runpod_start.sh
#
# Env vars you can set:
#   PORT        — relay port (default 8002). Must be exposed in the pod's
#                 "HTTP Ports" / "TCP Ports" settings to get a public URL.
#   TUNNEL=cf   — also spawn a cloudflared tunnel and print the public URL
#                 (useful when the pod has no inbound HTTP proxy configured).

set -e
cd "$(dirname "$0")"

PORT="${PORT:-8002}"

# Reuse an existing venv if one is present (the local install.sh creates one).
# On a fresh pod, install into the system Python.
if [ -f venv/bin/activate ]; then
    echo "[runpod] activating existing venv"
    # shellcheck disable=SC1091
    source venv/bin/activate
else
    echo "[runpod] installing dependencies into system Python"
fi

python -m pip install --upgrade pip -q

# omnivoice 0.1.4 imports `torch.nn.attention`, which only exists in
# PyTorch >= 2.5. RunPod's PyTorch 2.4.1 template is too old, so upgrade
# torch/torchaudio against the CUDA 12.4 wheels before installing omnivoice.
echo "[runpod] ensuring torch >= 2.5 (cu124) for omnivoice.torch.nn.attention import"
python -m pip install --upgrade \
    "torch>=2.5" "torchaudio>=2.5" \
    --index-url https://download.pytorch.org/whl/cu124

# omnivoice 0.1.4 imports HiggsAudioV2TokenizerModel from transformers.
# That class was added around transformers 4.57 and reorganized/removed
# in the 5.x line, so pin to the last 4.x release that still ships it.
# transformers 4.57 also requires huggingface-hub < 1.0, whereas the
# RunPod base ships 1.11 — downgrade hub in lockstep.
echo "[runpod] pinning transformers==4.57.1 and huggingface-hub<1.0"
python -m pip install --force-reinstall --no-deps \
    "transformers==4.57.1" "huggingface-hub>=0.34,<1.0"

python -m pip install -r requirements.txt

if [ "${TUNNEL:-}" = "cf" ]; then
    if ! command -v cloudflared >/dev/null 2>&1; then
        echo "[runpod] downloading cloudflared..."
        wget -q https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 \
            -O /tmp/cloudflared && chmod +x /tmp/cloudflared
        CF=/tmp/cloudflared
    else
        CF=cloudflared
    fi
    echo "[runpod] starting relay in background on port $PORT..."
    python relay.py --port "$PORT" &
    sleep 4
    echo "[runpod] starting cloudflared tunnel — watch for the https://*.trycloudflare.com URL below"
    "$CF" tunnel --url "http://localhost:$PORT" --no-autoupdate
else
    echo "[runpod] starting relay on 0.0.0.0:$PORT"
    echo "[runpod] Expose port $PORT in your RunPod settings, then paste the pod's public URL"
    echo "[runpod] into the local app's 'Remote URL' field."
    exec python relay.py --port "$PORT"
fi
