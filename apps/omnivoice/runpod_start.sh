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
