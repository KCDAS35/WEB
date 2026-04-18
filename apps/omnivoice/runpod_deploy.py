#!/usr/bin/env python3
"""
OmniVoice RunPod Auto-Deploy (Cross-platform: Windows / Linux / macOS)

Usage:
  PowerShell:  $env:RUNPOD_API_KEY="rpa_..."; python runpod_deploy.py
  Linux/Mac:   RUNPOD_API_KEY=rpa_... python3 runpod_deploy.py

Creates a GPU pod with an auto-install command baked in.
OmniVoice installs and starts automatically — no SSH needed.
"""
import os
import sys
import time
import subprocess

API_KEY = os.environ.get("RUNPOD_API_KEY", "").strip()
if not API_KEY:
    sys.exit(
        "ERROR: Set RUNPOD_API_KEY first.\n"
        "  PowerShell:  $env:RUNPOD_API_KEY='rpa_xxx'\n"
        "  Bash:        export RUNPOD_API_KEY=rpa_xxx"
    )

GPU_PREFERENCE = [
    "NVIDIA RTX A6000",
    "NVIDIA A40",
    "NVIDIA L40",
    "NVIDIA RTX 4090",
    "NVIDIA RTX A5000",
    "NVIDIA A100 80GB PCIe",
]

# This runs inside the pod at startup — installs + launches OmniVoice
AUTO_INSTALL = (
    "bash -c 'export HF_HOME=/workspace/hf-cache TRANSFORMERS_CACHE=/workspace/hf-cache; "
    "mkdir -p /workspace/hf-cache && cd /workspace && "
    "(test -d WEB || git clone -b claude/fix-synthesis-performance-tp0Aq "
    "https://github.com/KCDAS35/WEB.git WEB) && "
    "cd WEB && git fetch && git checkout claude/fix-synthesis-performance-tp0Aq && git pull && "
    "pip install -q fastapi \"uvicorn[standard]\" python-multipart soundfile numpy omnivoice && "
    "cd apps/omnivoice && nohup python3 app.py > /workspace/omnivoice.log 2>&1 & "
    "/start.sh'"
)

def ensure_sdk():
    try:
        import runpod  # noqa
    except ImportError:
        print("Installing runpod SDK...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "runpod"])

ensure_sdk()
import runpod
runpod.api_key = API_KEY

print("=" * 55)
print("  OmniVoice RunPod Auto-Deploy")
print("=" * 55)

print("\n[1/3] Finding an available GPU...")
chosen_gpu, pod = None, None
for gpu_id in GPU_PREFERENCE:
    try:
        print(f"   Trying {gpu_id}...", end=" ", flush=True)
        pod = runpod.create_pod(
            name="omnivoice-gpu",
            image_name="runpod/pytorch:2.4.0-py3.11-cuda12.4.1-devel-ubuntu22.04",
            gpu_type_id=gpu_id,
            cloud_type="SECURE",
            gpu_count=1,
            volume_in_gb=50,
            container_disk_in_gb=20,
            ports="8888/http,8765/http,22/tcp",
            volume_mount_path="/workspace",
            docker_args=AUTO_INSTALL,
        )
        chosen_gpu = gpu_id
        print("OK")
        break
    except Exception as e:
        print(f"unavailable")
        continue

if not pod:
    print("\nNo GPUs currently available. Try again in a few minutes.")
    sys.exit(1)

pod_id = pod["id"]
print(f"\n[2/3] Pod {pod_id} created on {chosen_gpu}")
print("      Waiting for HTTP proxy (1-2 min)...")

# Wait for 8765 HTTP proxy to become routable
for i in range(90):  # up to 7.5 min
    time.sleep(5)
    info = runpod.get_pod(pod_id)
    if info.get("desiredStatus") == "RUNNING" and info.get("runtime"):
        print(f"   Pod running. Install begins inside the container now.")
        break
    print(f"   ...still booting ({i*5}s)   ", end="\r", flush=True)

omnivoice_url = f"https://{pod_id}-8765.proxy.runpod.net"
jupyter_url   = f"https://{pod_id}-8888.proxy.runpod.net"
web_term_url  = f"https://www.runpod.io/console/pods/{pod_id}"

print("\n[3/3] Done!")
print("=" * 55)
print(f"  Pod ID:     {pod_id}")
print(f"  GPU:        {chosen_gpu}")
print()
print(f"  OmniVoice:  {omnivoice_url}")
print(f"  Dashboard:  {web_term_url}")
print("=" * 55)
print()
print("The pod is auto-installing OmniVoice right now.")
print("Give it 5-10 minutes for the first run (downloads ~4 GB model).")
print(f"If the URL shows an error, wait and refresh.")
print()
print("To check install progress, go to the dashboard URL above,")
print("open the Web Terminal, and run:")
print("  tail -f /workspace/omnivoice.log")
