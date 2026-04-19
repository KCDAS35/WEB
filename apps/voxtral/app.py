"""
Voxtral TTS — minimal FastAPI server.

Wraps mistralai/Voxtral-4B-TTS-2603 with a simple /synthesize endpoint.
Attempts the transformers text-to-audio pipeline first; falls back to a
direct AutoModel load if the pipeline task isn't registered yet for Voxtral.
"""

import logging
import threading
import time
import uuid
from pathlib import Path

import soundfile as sf
import torch
import uvicorn
from fastapi import FastAPI, Form
from fastapi.responses import FileResponse, HTMLResponse

MODEL_ID = "mistralai/Voxtral-4B-TTS-2603"
PORT = 8766
OUTPUT_DIR = Path("/tmp/voxtral_out")
OUTPUT_DIR.mkdir(exist_ok=True)

app = FastAPI(title="Voxtral TTS")

_PIPE = None
_MODEL = None
_PROCESSOR = None
MODEL_STATUS: dict = {"state": "loading", "log": []}


def _log(msg: str) -> None:
    MODEL_STATUS["log"].append(msg)
    logging.getLogger("voxtral").info(msg)


def _best_device() -> str:
    if torch.cuda.is_available():
        return "cuda"
    return "cpu"


def _load_model() -> None:
    global _PIPE, _MODEL, _PROCESSOR
    device = _best_device()
    _log(f"Loading {MODEL_ID} on {device}...")

    try:
        from transformers import pipeline
        _PIPE = pipeline("text-to-audio", model=MODEL_ID, device=device)
        MODEL_STATUS["state"] = "ready"
        _log("Pipeline loaded (text-to-audio).")
        return
    except Exception as exc:
        _log(f"Pipeline load failed: {exc}. Trying AutoModel...")

    try:
        from transformers import AutoModel, AutoProcessor
        _PROCESSOR = AutoProcessor.from_pretrained(MODEL_ID)
        _MODEL = AutoModel.from_pretrained(
            MODEL_ID,
            torch_dtype=torch.float16 if device == "cuda" else torch.float32,
        ).to(device)
        _MODEL.eval()
        MODEL_STATUS["state"] = "ready"
        _log("AutoModel loaded. Inference path is experimental.")
    except Exception as exc:
        MODEL_STATUS["state"] = "error"
        _log(f"AutoModel load failed: {exc}")


threading.Thread(target=_load_model, daemon=True).start()


INDEX_HTML = """<!DOCTYPE html>
<html>
<head>
<title>Voxtral TTS</title>
<style>
  body { font-family: -apple-system, system-ui, sans-serif; max-width: 720px;
         margin: 2rem auto; padding: 1rem; color: #222; }
  h1 { margin-top: 0; }
  textarea { width: 100%; padding: .6rem; font-size: 1rem; box-sizing: border-box; }
  button { padding: .6rem 1.2rem; font-size: 1rem; cursor: pointer; margin-top: .6rem; }
  #status { font-size: .9rem; color: #555; }
  #log { background: #f4f4f4; padding: .8rem; font-family: monospace;
         font-size: .85rem; white-space: pre-wrap; margin-top: 1rem;
         max-height: 240px; overflow: auto; }
  audio { width: 100%; margin-top: 1rem; }
</style>
</head>
<body>
<h1>Voxtral TTS</h1>
<p id="status">Checking model...</p>
<textarea id="t" rows="5"
  placeholder="Type text here. The model supports 9 languages."></textarea>
<br>
<button id="go" onclick="synth()">Synthesize</button>
<audio id="a" controls></audio>
<div id="log"></div>
<script>
async function refreshStatus(){
  const r = await fetch('/status');
  const j = await r.json();
  document.getElementById('status').innerText =
    'Model: ' + j.state + (j.error ? ' — ' + j.error : '');
  document.getElementById('log').innerText = (j.log || []).join('\\n');
  document.getElementById('go').disabled = (j.state !== 'ready');
}
refreshStatus(); setInterval(refreshStatus, 2500);
async function synth(){
  const btn = document.getElementById('go');
  btn.disabled = true; btn.innerText = 'Generating...';
  const f = new FormData();
  f.append('text', document.getElementById('t').value);
  const r = await fetch('/synthesize', { method: 'POST', body: f });
  const j = await r.json();
  if (j.error) { alert(j.error); }
  else { document.getElementById('a').src = '/audio/' + j.id + '?t=' + Date.now(); }
  btn.disabled = false; btn.innerText = 'Synthesize';
}
</script>
</body>
</html>"""


@app.get("/", response_class=HTMLResponse)
def index() -> str:
    return INDEX_HTML


@app.get("/status")
def status():
    return {
        "state": MODEL_STATUS["state"],
        "log": MODEL_STATUS["log"][-40:],
    }


@app.post("/synthesize")
def synthesize(text: str = Form(...)):
    if MODEL_STATUS["state"] != "ready":
        return {"error": f"model not ready ({MODEL_STATUS['state']})"}

    job_id = uuid.uuid4().hex[:8]
    out_path = OUTPUT_DIR / f"{job_id}.wav"
    t0 = time.monotonic()

    try:
        if _PIPE is not None:
            result = _PIPE(text)
            audio = result["audio"] if isinstance(result, dict) else result[0]["audio"]
            sr = result.get("sampling_rate", 24000) if isinstance(result, dict) \
                else result[0].get("sampling_rate", 24000)
            sf.write(str(out_path), audio, sr)
        else:
            return {
                "error": "No supported inference path — pipeline unavailable "
                         "and AutoModel generate signature not known. "
                         "Check logs and update voxtral/app.py."
            }
    except Exception as exc:
        return {"error": f"synthesis failed: {exc}"}

    _log(f"Synthesized {job_id} in {time.monotonic() - t0:.1f}s")
    return {"id": job_id}


@app.get("/audio/{job_id}")
def audio(job_id: str):
    path = OUTPUT_DIR / f"{job_id}.wav"
    if not path.exists():
        return {"error": "not found"}
    return FileResponse(str(path), media_type="audio/wav")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=PORT)
