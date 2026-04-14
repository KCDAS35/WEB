"""
OmniVoice Local App — Windows / Linux
FastAPI backend with chunked long-form TTS synthesis.
The model is loaded once at startup and kept in memory.
"""

import asyncio
import logging
import re
import threading
import time
import uuid
import webbrowser
from pathlib import Path
from typing import Optional

import numpy as np
import soundfile as sf
import torch
import uvicorn
from fastapi import FastAPI, File, Form, UploadFile
from fastapi.responses import FileResponse, HTMLResponse, StreamingResponse

app = FastAPI(title="OmniVoice Local")

JOBS: dict[str, dict] = {}
OUTPUT_DIR = Path(__file__).parent / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)
TEMPLATES_DIR = Path(__file__).parent / "templates"


# ── Model singleton ──────────────────────────────────────────────────────────

_MODEL = None
_MODEL_LOCK = threading.Lock()
MODEL_STATUS: dict = {"state": "loading", "log": []}
# state values: "loading" | "ready" | "error"


def _best_device() -> str:
    if torch.cuda.is_available():
        return "cuda"
    try:
        if torch.backends.mps.is_available():
            return "mps"
    except Exception:
        pass
    return "cpu"


class _LogCapture(logging.Handler):
    """Appends formatted log records to MODEL_STATUS["log"]."""
    def emit(self, record: logging.LogRecord) -> None:
        MODEL_STATUS["log"].append(self.format(record))


def _load_model() -> None:
    global _MODEL
    handler = _LogCapture()
    handler.setFormatter(logging.Formatter("%(message)s"))
    logging.getLogger().addHandler(handler)
    try:
        from omnivoice.models.omnivoice import OmniVoice
        device = _best_device()
        dtype = torch.float16 if device != "cpu" else torch.float32
        MODEL_STATUS["log"].append(
            f"⏳ Loading OmniVoice on {device} — "
            f"first run downloads ~4 GB, this may take a while..."
        )
        _MODEL = OmniVoice.from_pretrained(
            "k2-fsa/OmniVoice", device_map=device, dtype=dtype
        )
        MODEL_STATUS["state"] = "ready"
        MODEL_STATUS["log"].append("✅ Model loaded and ready.")
    except Exception as exc:
        MODEL_STATUS["state"] = "error"
        MODEL_STATUS["log"].append(f"❌ Model load failed: {exc}")
    finally:
        logging.getLogger().removeHandler(handler)


# Start loading in the background immediately
threading.Thread(target=_load_model, daemon=True).start()


# ── Text chunking ────────────────────────────────────────────────────────────

def chunk_text(text: str, max_words: int = 400) -> list[str]:
    """Split text into chunks at sentence boundaries."""
    text = re.sub(r"\s+", " ", text.strip())
    sentences = re.split(r"(?<=[.!?\u2026])\s+", text)
    chunks, current, count = [], [], 0
    for sent in sentences:
        w = len(sent.split())
        if count + w > max_words and current:
            chunks.append(" ".join(current))
            current, count = [sent], w
        else:
            current.append(sent)
            count += w
    if current:
        chunks.append(" ".join(current))
    return chunks


# ── Synthesis worker (runs in a thread) ─────────────────────────────────────

def run_synthesis(
    job_id: str,
    text: str,
    ref_audio_path: Optional[Path],
    instruct: Optional[str],
    max_words: int,
) -> None:
    job = JOBS[job_id]

    def log(msg: str) -> None:
        job["log"].append(msg)

    try:
        # Wait for model to finish loading
        log("⏳ Waiting for model to be ready...")
        while MODEL_STATUS["state"] == "loading":
            if job.get("cancelled"):
                log("🛑 Cancelled.")
                job["status"] = "cancelled"
                return
            time.sleep(0.5)

        if MODEL_STATUS["state"] != "ready":
            last = MODEL_STATUS["log"][-1] if MODEL_STATUS["log"] else "unknown error"
            log(f"❌ Model unavailable: {last}")
            job["status"] = "failed"
            return

        log("✅ Model ready — starting synthesis.")
        chunks = chunk_text(text, max_words)
        total = len(text.split())
        log(f"📝 {total:,} words → {len(chunks)} chunks (max {max_words} words each)")

        wav_files: list[Path] = []
        for i, chunk in enumerate(chunks):
            if job.get("cancelled"):
                log("🛑 Cancelled by user.")
                job["status"] = "cancelled"
                return

            out = OUTPUT_DIR / f"_chunk_{job_id}_{i:04d}.wav"
            log(f"[{i + 1}/{len(chunks)}] Synthesizing {len(chunk.split())} words...")

            t0 = time.monotonic()
            try:
                with _MODEL_LOCK:
                    audios = _MODEL.generate(
                        text=chunk,
                        ref_audio=str(ref_audio_path) if ref_audio_path else None,
                        instruct=instruct,
                    )
                sf.write(str(out), audios[0], _MODEL.sampling_rate)
            except Exception as exc:
                elapsed = time.monotonic() - t0
                log(f"⚠️  Chunk {i + 1} error ({elapsed:.0f}s): {exc}")
                log(f"__PROGRESS__{i + 1}__{len(chunks)}__")
                continue

            elapsed = time.monotonic() - t0
            log(f"✅ Chunk {i + 1} done ({elapsed:.0f}s)")
            wav_files.append(out)
            log(f"__PROGRESS__{i + 1}__{len(chunks)}__")

        if not wav_files:
            log("❌ Nothing synthesized — check errors above.")
            job["status"] = "failed"
            return

        log(f"🔗 Joining {len(wav_files)} audio segments...")
        arrays: list[np.ndarray] = []
        sr = None
        for f in wav_files:
            data, rate = sf.read(str(f))
            sr = rate
            arrays.append(data)
            f.unlink(missing_ok=True)

        final = OUTPUT_DIR / f"output_{job_id}.wav"
        sf.write(str(final), np.concatenate(arrays), sr)

        if ref_audio_path and ref_audio_path.exists():
            ref_audio_path.unlink(missing_ok=True)

        mins = total / 150
        log(f"✅ Done!  Words: {total:,}  |  Estimated length: ~{mins:.1f} min")
        job["output"] = str(final)
        job["status"] = "done"

    except Exception as exc:
        log(f"❌ Unexpected error: {exc}")
        job["status"] = "failed"
    finally:
        job["done"] = True


# ── Routes ───────────────────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
def index() -> str:
    return (TEMPLATES_DIR / "index.html").read_text(encoding="utf-8")


@app.get("/model-status")
def get_model_status():
    return {"state": MODEL_STATUS["state"]}


@app.get("/model-log")
async def model_log_stream():
    """SSE stream of model loading log lines."""
    async def stream():
        sent = 0
        while True:
            while sent < len(MODEL_STATUS["log"]):
                line = MODEL_STATUS["log"][sent].replace("\n", " ")
                yield f"data: {line}\n\n"
                sent += 1
            if MODEL_STATUS["state"] != "loading":
                yield f"data: __MODEL_STATE__{MODEL_STATUS['state']}__\n\n"
                break
            await asyncio.sleep(0.5)
    return StreamingResponse(stream(), media_type="text/event-stream")


@app.post("/synthesize")
async def synthesize(
    text: str = Form(...),
    instruct: str = Form(""),
    max_words: int = Form(400),
    ref_audio: Optional[UploadFile] = File(None),
):
    job_id = uuid.uuid4().hex[:8]
    JOBS[job_id] = {"status": "running", "log": [], "output": None, "done": False}

    ref_path: Optional[Path] = None
    if ref_audio and ref_audio.filename:
        suffix = Path(ref_audio.filename).suffix or ".wav"
        ref_path = OUTPUT_DIR / f"ref_{job_id}{suffix}"
        ref_path.write_bytes(await ref_audio.read())

    threading.Thread(
        target=run_synthesis,
        args=(job_id, text, ref_path, instruct or None, max_words),
        daemon=True,
    ).start()

    return {"job_id": job_id}


@app.get("/progress/{job_id}")
async def progress(job_id: str):
    """Server-Sent Events stream — delivers log lines in real time."""
    async def stream():
        sent = 0
        while True:
            job = JOBS.get(job_id)
            if not job:
                yield "data: ❌ Job not found\n\n"
                break
            while sent < len(job["log"]):
                line = job["log"][sent].replace("\n", " ")
                yield f"data: {line}\n\n"
                sent += 1
            if job["done"]:
                yield f"data: __STATUS__{job['status']}__{job_id}__\n\n"
                break
            await asyncio.sleep(0.4)
    return StreamingResponse(stream(), media_type="text/event-stream")


@app.post("/cancel/{job_id}")
def cancel_job(job_id: str):
    job = JOBS.get(job_id)
    if not job:
        return {"error": "Job not found"}
    job["cancelled"] = True
    return {"ok": True}


@app.get("/download/{job_id}")
def download(job_id: str):
    job = JOBS.get(job_id)
    if not job or not job.get("output"):
        return {"error": "Output not found"}
    return FileResponse(
        job["output"],
        filename="omnivoice_output.wav",
        media_type="audio/wav",
    )


# ── Entry point ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("Starting OmniVoice Local App...")
    print("Opening browser at http://localhost:8765")
    threading.Timer(1.5, lambda: webbrowser.open("http://localhost:8765")).start()
    uvicorn.run(app, host="0.0.0.0", port=8765)
