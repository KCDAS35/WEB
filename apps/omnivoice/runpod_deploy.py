#!/usr/bin/env python3
"""
TTS Pod Auto-Deploy — OmniVoice + Voxtral + Fish Speech on one pod.

Tries RunPod first (SECURE then COMMUNITY cloud). If nothing is available,
falls back to Vast.ai if VAST_API_KEY is set.

Usage:
  PowerShell:
    $env:RUNPOD_API_KEY="rpa_..."
    $env:VAST_API_KEY="..."          # optional fallback
    python runpod_deploy.py

  Linux/Mac:
    RUNPOD_API_KEY=rpa_... VAST_API_KEY=... python3 runpod_deploy.py

No SSH needed — auto-install runs start_all.sh inside the container.
"""
import json
import os
import sys
import time
import subprocess

RUNPOD_KEY = os.environ.get("RUNPOD_API_KEY", "").strip()
VAST_KEY = os.environ.get("VAST_API_KEY", "").strip()

if not RUNPOD_KEY and not VAST_KEY:
    sys.exit(
        "ERROR: Set at least one API key.\n"
        "  PowerShell:  $env:RUNPOD_API_KEY='rpa_...'\n"
        "               $env:VAST_API_KEY='...'  (optional fallback)\n"
        "  Bash:        export RUNPOD_API_KEY=rpa_...\n"
        "               export VAST_API_KEY=...  (optional fallback)"
    )

BRANCH = "claude/fix-synthesis-performance-tp0Aq"
REPO_URL = "https://github.com/KCDAS35/WEB.git"
IMAGE = "runpod/pytorch:2.4.0-py3.11-cuda12.4.1-devel-ubuntu22.04"

# Boots the container: clone repo, run start_all.sh (launches all three TTS apps).
ONSTART = (
    "bash -c '"
    "cd /workspace && "
    f"(test -d WEB || git clone -b {BRANCH} {REPO_URL} WEB) && "
    f"cd WEB && git fetch && git checkout {BRANCH} && git pull && "
    "chmod +x apps/omnivoice/start_all.sh && "
    "nohup bash apps/omnivoice/start_all.sh > /workspace/start_all.log 2>&1 & "
    "/start.sh"
    "'"
)

RUNPOD_GPUS = [
    "NVIDIA RTX A6000",
    "NVIDIA A40",
    "NVIDIA L40",
    "NVIDIA RTX 4090",
    "NVIDIA RTX A5000",
    "NVIDIA A100 80GB PCIe",
    "NVIDIA A10G",
    "NVIDIA GeForce RTX 3090",
    "NVIDIA GeForce RTX 3090 Ti",
    "NVIDIA L4",
    "NVIDIA Tesla V100-SXM2-32GB",
]

PORTS = "8888/http,8765/http,8766/http,7860/http,22/tcp"


# ── Dependency bootstrapping ─────────────────────────────────────────────────

def _pip(pkg: str) -> None:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", pkg])


def ensure_runpod():
    try:
        import runpod  # noqa: F401
    except ImportError:
        print("Installing runpod SDK...")
        _pip("runpod")


def ensure_requests():
    try:
        import requests  # noqa: F401
    except ImportError:
        print("Installing requests...")
        _pip("requests")


# ── RunPod deploy ────────────────────────────────────────────────────────────

def try_runpod():
    """Return (pod_id, chosen_gpu, urls_dict) or None."""
    if not RUNPOD_KEY:
        return None
    ensure_runpod()
    import runpod
    runpod.api_key = RUNPOD_KEY

    print("\n[RunPod] Finding an available GPU...")
    chosen, pod = None, None
    for cloud_type in ["SECURE", "COMMUNITY"]:
        if pod:
            break
        print(f"   Checking {cloud_type} cloud...")
        for gpu_id in RUNPOD_GPUS:
            try:
                print(f"      {gpu_id}...", end=" ", flush=True)
                pod = runpod.create_pod(
                    name="tts-multi-gpu",
                    image_name=IMAGE,
                    gpu_type_id=gpu_id,
                    cloud_type=cloud_type,
                    gpu_count=1,
                    volume_in_gb=60,
                    container_disk_in_gb=20,
                    ports=PORTS,
                    volume_mount_path="/workspace",
                    docker_args=ONSTART,
                )
                chosen = f"{gpu_id} ({cloud_type})"
                print("OK")
                break
            except Exception:
                print("unavailable")
                continue

    if not pod:
        print("[RunPod] No GPUs available on either cloud.")
        return None

    pod_id = pod["id"]
    print(f"\n[RunPod] Pod {pod_id} created on {chosen}. Waiting for it to run...")
    for i in range(90):
        time.sleep(5)
        info = runpod.get_pod(pod_id)
        if info.get("desiredStatus") == "RUNNING" and info.get("runtime"):
            print("   Pod is running. Services are starting inside the container.")
            break
        print(f"   ...still booting ({i*5}s)   ", end="\r", flush=True)

    urls = {
        "omnivoice":    f"https://{pod_id}-8765.proxy.runpod.net",
        "voxtral":      f"https://{pod_id}-8766.proxy.runpod.net",
        "fish-speech":  f"https://{pod_id}-7860.proxy.runpod.net",
        "jupyter":      f"https://{pod_id}-8888.proxy.runpod.net",
        "dashboard":    f"https://www.runpod.io/console/pods/{pod_id}",
    }
    return pod_id, chosen, urls


# ── Vast.ai fallback ─────────────────────────────────────────────────────────

VAST_BASE = "https://console.vast.ai/api/v0"


def try_vast():
    """Return (instance_id, chosen_gpu, urls_dict) or None."""
    if not VAST_KEY:
        print("[Vast.ai] VAST_API_KEY not set — skipping fallback.")
        return None

    ensure_requests()
    import requests

    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {VAST_KEY}",
    }

    print("\n[Vast.ai] Searching offers...")
    # Minimum 40 GB VRAM, verified + rentable, on-demand, cheapest first.
    query = {
        "verified": {"eq": True},
        "rentable": {"eq": True},
        "gpu_ram":  {"gte": 40000},
        "num_gpus": {"eq": 1},
        "rented":   {"eq": False},
        "type":     "on-demand",
        "order":    [["dph_total", "asc"]],
    }
    try:
        r = requests.get(
            f"{VAST_BASE}/bundles/",
            headers=headers,
            params={"q": json.dumps(query)},
            timeout=30,
        )
        r.raise_for_status()
    except Exception as exc:
        print(f"[Vast.ai] Offer search failed: {exc}")
        return None

    offers = r.json().get("offers", [])
    if not offers:
        print("[Vast.ai] No offers match (40 GB VRAM, verified, rentable).")
        return None

    offer = offers[0]
    ask_id = offer["id"]
    gpu_name = offer.get("gpu_name", "?")
    dph = offer.get("dph_total", "?")
    print(f"[Vast.ai] Picked offer {ask_id}: {gpu_name} @ ${dph}/hr")

    body = {
        "client_id": "me",
        "image":     IMAGE,
        "disk":      60,
        "runtype":   "ssh",
        "onstart":   ONSTART,
        "label":     "tts-multi-gpu",
    }
    try:
        r = requests.put(
            f"{VAST_BASE}/asks/{ask_id}/",
            headers={**headers, "Content-Type": "application/json"},
            data=json.dumps(body),
            timeout=30,
        )
        r.raise_for_status()
    except Exception as exc:
        print(f"[Vast.ai] Create instance failed: {exc}")
        return None

    new_contract = r.json().get("new_contract")
    if not new_contract:
        print(f"[Vast.ai] Unexpected response: {r.text[:200]}")
        return None

    print(f"[Vast.ai] Instance {new_contract} created. Waiting for it to run...")
    for i in range(90):
        time.sleep(5)
        try:
            r = requests.get(
                f"{VAST_BASE}/instances/",
                headers=headers,
                timeout=30,
            )
            inst = next(
                (x for x in r.json().get("instances", []) if x["id"] == new_contract),
                None,
            )
        except Exception:
            inst = None
        if inst and inst.get("actual_status") == "running":
            print("   Instance is running. Services are starting inside the container.")
            break
        print(f"   ...still booting ({i*5}s)   ", end="\r", flush=True)

    # Vast's port mapping: public_ipaddr + ports dict mapping internal → external.
    host = inst.get("public_ipaddr", "?") if inst else "?"
    port_map = inst.get("ports", {}) if inst else {}

    def url_for(internal: str) -> str:
        binding = port_map.get(internal)
        if binding and binding[0].get("HostPort"):
            return f"http://{host}:{binding[0]['HostPort']}"
        return f"http://{host}:??? (port {internal} not yet mapped)"

    urls = {
        "omnivoice":    url_for("8765/tcp"),
        "voxtral":      url_for("8766/tcp"),
        "fish-speech":  url_for("7860/tcp"),
        "jupyter":      url_for("8888/tcp"),
        "dashboard":    f"https://cloud.vast.ai/instances/?q={new_contract}",
    }
    return new_contract, f"{gpu_name} (Vast.ai)", urls


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    print("=" * 55)
    print("  TTS Multi-App Pod Deploy")
    print("  (OmniVoice + Voxtral + Fish Speech)")
    print("=" * 55)

    result = try_runpod() or try_vast()

    if not result:
        print()
        print("No GPUs available on RunPod or Vast.ai right now.")
        print("Wait a few minutes and re-run this script.")
        sys.exit(1)

    pod_id, chosen, urls = result

    print("\nDone!")
    print("=" * 55)
    print(f"  Instance:    {pod_id}")
    print(f"  GPU:         {chosen}")
    print()
    print(f"  OmniVoice:   {urls['omnivoice']}")
    print(f"  Voxtral:     {urls['voxtral']}")
    print(f"  Fish Speech: {urls['fish-speech']}")
    print(f"  Jupyter:     {urls['jupyter']}")
    print(f"  Dashboard:   {urls['dashboard']}")
    print("=" * 55)
    print()
    print("The pod is auto-installing all three services now.")
    print("First run downloads ~12 GB of models — give it 10-15 minutes.")
    print("If a URL shows an error, wait and refresh.")
    print()
    print("To watch install progress, open the dashboard → Web Terminal → run:")
    print("  tail -f /workspace/start_all.log")
    print("  tail -f /workspace/omnivoice.log")
    print("  tail -f /workspace/voxtral.log")
    print("  tail -f /workspace/fish-speech.log")


if __name__ == "__main__":
    main()
