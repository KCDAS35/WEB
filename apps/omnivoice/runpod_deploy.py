#!/usr/bin/env python3
"""
OmniVoice RunPod Auto-Deploy
Run from Alienware:  python3 runpod_deploy.py

Deploys a GPU pod, installs OmniVoice, returns a clickable URL.
"""
import os
import sys
import time
import json
import subprocess

API_KEY = os.environ.get("RUNPOD_API_KEY", "").strip()
SSH_KEY = os.path.expanduser("~/.ssh/id_ed25519")

if not API_KEY:
    sys.exit("ERROR: set RUNPOD_API_KEY env var first.\n"
             "  export RUNPOD_API_KEY=rpa_xxxxxxxxxxxx")

# Preferred GPU order: cheapest-capable first
GPU_PREFERENCE = [
    "NVIDIA RTX A6000",      # 48GB, ~$0.49/hr
    "NVIDIA A40",            # 48GB, ~$0.39/hr
    "NVIDIA L40",            # 48GB
    "NVIDIA RTX 4090",       # 24GB
    "NVIDIA RTX A5000",      # 24GB
    "NVIDIA A100 80GB PCIe", # 80GB, expensive
]

def ensure_sdk():
    try:
        import runpod  # noqa
    except ImportError:
        print("Installing runpod SDK...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "runpod"])

ensure_sdk()
import runpod
runpod.api_key = API_KEY

print("━" * 50)
print("  OmniVoice RunPod Auto-Deploy")
print("━" * 50)

print("\n[1/5] Finding available GPU...")
chosen_gpu = None
pod = None
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
        )
        chosen_gpu = gpu_id
        print("OK")
        break
    except Exception as e:
        print(f"unavailable ({str(e)[:60]})")
        continue

if not pod:
    print("\nNo GPUs available right now. Try again in a few minutes.")
    sys.exit(1)

print(f"\n[2/5] Pod created: {pod['id']} on {chosen_gpu}")
print("      Waiting for it to boot...")

# Wait for pod to be ready (status RUNNING + has public IP/port)
pod_info = None
for i in range(60):  # up to 5 minutes
    time.sleep(5)
    pod_info = runpod.get_pod(pod["id"])
    if pod_info.get("desiredStatus") == "RUNNING" and pod_info.get("runtime"):
        ports = pod_info["runtime"].get("ports", [])
        if any(p.get("privatePort") == 22 for p in ports):
            break
    print(f"   …still booting ({i*5}s)", end="\r", flush=True)

print(f"\n[3/5] Pod is running")

# Extract SSH connection info
ssh_port = None
ssh_ip = None
http_url_8765 = None
for p in pod_info["runtime"]["ports"]:
    if p.get("privatePort") == 22 and p.get("isIpPublic"):
        ssh_ip = p["ip"]
        ssh_port = p["publicPort"]
    if p.get("privatePort") == 8765:
        http_url_8765 = f"https://{pod['id']}-8765.proxy.runpod.net"

if not ssh_ip:
    print("SSH port not exposed yet. Pod ID:", pod["id"])
    print("Use the RunPod web terminal and run the install script manually.")
    sys.exit(1)

print(f"      SSH: root@{ssh_ip}:{ssh_port}")

print("\n[4/5] Running install script on the pod...")
install_cmd = """
set -e
echo '>>> GPU check:'
nvidia-smi --query-gpu=name,memory.total --format=csv,noheader
echo '>>> Cloning repo:'
rm -rf /workspace/WEB
git clone -b claude/fix-synthesis-performance-tp0Aq https://github.com/KCDAS35/WEB.git /workspace/WEB
echo '>>> Running installer:'
bash /workspace/WEB/apps/omnivoice/install_runpod.sh
echo '>>> Starting OmniVoice in background:'
cd /workspace/WEB/apps/omnivoice
nohup python3 app.py > /workspace/omnivoice.log 2>&1 &
sleep 3
echo '>>> All done. Log: /workspace/omnivoice.log'
"""

ssh_args = [
    "ssh",
    "-o", "StrictHostKeyChecking=no",
    "-o", "UserKnownHostsFile=/dev/null",
    "-i", SSH_KEY,
    "-p", str(ssh_port),
    f"root@{ssh_ip}",
    install_cmd,
]

result = subprocess.run(ssh_args)
if result.returncode != 0:
    print(f"\nInstall returned exit code {result.returncode} — check the pod's web terminal.")

print("\n[5/5] Done!")
print("━" * 50)
print(f"  Pod ID:    {pod['id']}")
print(f"  GPU:       {chosen_gpu}")
print(f"  OmniVoice: {http_url_8765}")
print("━" * 50)
print("\nModel will download ~4GB on first request. Watch the banner in the UI.")
print("If the URL isn't ready yet, wait 30 seconds and refresh.")
