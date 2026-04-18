#!/usr/bin/env bash
# OmniVoice — RunPod Install Script
# Run once after pod restart: bash /workspace/WEB/apps/omnivoice/install_runpod.sh

set -e

echo "========================================"
echo "  OmniVoice RunPod Installer"
echo "========================================"

# ── 1. Verify GPU ────────────────────────────────────────────────────────────
echo ""
echo "[ 1/5 ] Checking GPU..."
nvidia-smi --query-gpu=name,memory.total --format=csv,noheader || {
    echo "ERROR: nvidia-smi not found. Stop the pod, start it fresh, and retry."
    exit 1
}

# ── 2. Update code from git ──────────────────────────────────────────────────
echo ""
echo "[ 2/5 ] Updating code..."
cd /workspace/WEB
git fetch origin
git checkout claude/fix-synthesis-performance-tp0Aq
git pull origin claude/fix-synthesis-performance-tp0Aq
echo "Code up to date."

# ── 3. Set HuggingFace cache to persistent volume ───────────────────────────
echo ""
echo "[ 3/5 ] Configuring HuggingFace cache..."
export HF_HOME=/workspace/hf-cache
export TRANSFORMERS_CACHE=/workspace/hf-cache
mkdir -p /workspace/hf-cache

# Persist env vars for future sessions
grep -q "HF_HOME" /root/.bashrc || cat >> /root/.bashrc << 'EOF'
export HF_HOME=/workspace/hf-cache
export TRANSFORMERS_CACHE=/workspace/hf-cache
EOF
echo "HF cache → /workspace/hf-cache"

# ── 4. Install Python dependencies ──────────────────────────────────────────
echo ""
echo "[ 4/5 ] Installing dependencies..."
pip install --upgrade pip --quiet
pip install \
    "fastapi>=0.111.0" \
    "uvicorn[standard]>=0.29.0" \
    "python-multipart>=0.0.9" \
    "soundfile>=0.12.1" \
    "numpy>=1.26.0" \
    omnivoice \
    --quiet
echo "Dependencies installed."

# ── 5. Create start script ───────────────────────────────────────────────────
echo ""
echo "[ 5/5 ] Creating start script..."
cat > /workspace/start_omnivoice.sh << 'EOF'
#!/usr/bin/env bash
export HF_HOME=/workspace/hf-cache
export TRANSFORMERS_CACHE=/workspace/hf-cache
cd /workspace/WEB/apps/omnivoice
echo "Starting OmniVoice on port 8765..."
echo "Model will download ~4GB on first run — watch the banner in the UI."
python3 app.py
EOF
chmod +x /workspace/start_omnivoice.sh

echo ""
echo "========================================"
echo "  Install complete!"
echo "========================================"
echo ""
echo "To start OmniVoice:"
echo "  bash /workspace/start_omnivoice.sh"
echo ""
echo "Then open the RunPod HTTP link for port 8765 in your browser."
echo ""
