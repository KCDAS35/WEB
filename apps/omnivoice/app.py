"""
OmniVoice Local App — Windows
FastAPI backend with chunked long-form TTS synthesis.

Three synthesis backends:
  • local_persistent — model loaded once into this process, reused across
    every chunk and every job. Huge speedup vs spawning a subprocess per
    chunk (which reloads the model each time).
  • remote           — POST chunks to a Colab relay URL (GPU in the cloud).
    Fastest option on machines without a strong local GPU.
  • local_cli        — legacy path: run `omnivoice-infer` per chunk. Kept
    as a fallback when the Python API cannot be imported.
"""

import asyncio
import io
import os
import re
import subprocess
import threading
import uuid
import webbrowser
from pathlib import Path
from typing import Optional

import numpy as np
import requests
import soundfile as sf
import uvicorn
from fastapi import FastAPI, File, Form, UploadFile
from fastapi.responses import FileResponse, HTMLResponse, StreamingResponse

app = FastAPI(title="OmniVoice Local")

JOBS: dict[str, dict] = {}
OUTPUT_DIR = Path(__file__).parent / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)
TEMPLATES_DIR = Path(__file__).parent / "templates"

# Shared state for the persistent in-process model.
_MODEL_LOCK = threading.Lock()
_MODEL: dict = {"obj": None, "synth": None, "error": None}


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


# ── Persistent in-process model ──────────────────────────────────────────────

def _load_persistent_model() -> tuple[object, callable]:
    """Import omnivoice and return (model, synth_fn).

    synth_fn(text, ref_audio, instruct, out_path) writes a WAV to out_path.

    Tries the known import shapes of the k2-fsa/OmniVoice package. If none
    match the installed version, raises ImportError with a clear message so
    the caller can fall back to the CLI backend.
    """

    import importlib

    attempts = [
        # (module path, class name, from_pretrained-style method)
        ("omnivoice", "OmniVoice", "from_pretrained"),
        ("omnivoice.inference", "OmniVoice", "from_pretrained"),
        ("omnivoice.inference", "Inferencer", "from_pretrained"),
        ("omnivoice.model", "OmniVoice", "from_pretrained"),
    ]

    last_err: Optional[Exception] = None
    for mod_path, cls_name, factory in attempts:
        try:
            mod = importlib.import_module(mod_path)
            cls = getattr(mod, cls_name)
            model = getattr(cls, factory)("k2-fsa/OmniVoice")
            break
        except Exception as exc:
            last_err = exc
            continue
    else:
        raise ImportError(
            "Could not locate the OmniVoice Python API. Tried: "
            + ", ".join(f"{m}.{c}" for m, c, _ in attempts)
            + f". Last error: {last_err!r}. "
            "Use the 'local_cli' or 'remote' backend instead, or adjust "
            "apps/omnivoice/app.py:_load_persistent_model to match the "
            "installed package."
        )

    def synth(text: str, ref_audio: Optional[str], instruct: Optional[str],
              out_path: str) -> None:
        kwargs = {"text": text}
        if ref_audio:
            kwargs["ref_audio"] = ref_audio
        if instruct:
            kwargs["instruct"] = instruct

        for method_name in ("synthesize", "generate", "infer", "tts", "__call__"):
            fn = getattr(model, method_name, None)
            if fn is None:
                continue
            try:
                result = fn(**kwargs, output=out_path)
            except TypeError:
                result = fn(**kwargs)
                if isinstance(result, tuple) and len(result) == 2:
                    audio, sr = result
                    sf.write(out_path, np.asarray(audio), int(sr))
                elif hasattr(result, "audio") and hasattr(result, "sample_rate"):
                    sf.write(out_path, np.asarray(result.audio), int(result.sample_rate))
                else:
                    raise RuntimeError(
                        f"Unknown return type from {method_name}: {type(result)}"
                    )
            return

        raise RuntimeError("Loaded OmniVoice model exposes no known synth method.")

    return model, synth


def _ensure_persistent_model(log) -> Optional[callable]:
    """Load the model once, memoized. Returns synth_fn, or None on failure."""
    with _MODEL_LOCK:
        if _MODEL["synth"] is not None:
            return _MODEL["synth"]
        if _MODEL["error"] is not None:
            log(f"⚠️  Persistent model unavailable: {_MODEL['error']}")
            return None

        log("⏳ Loading OmniVoice model into memory (first run only)...")
        try:
            model, synth = _load_persistent_model()
            _MODEL["obj"] = model
            _MODEL["synth"] = synth
            log("✅ Model loaded — subsequent chunks will be fast.")
            return synth
        except Exception as exc:
            _MODEL["error"] = str(exc)
            log(f"⚠️  Failed to load persistent model: {exc}")
            return None


# ── Backend implementations ─────────────────────────────────────────────────

def _synth_cli(chunk: str, ref: Optional[Path], instruct: Optional[str],
               out: Path) -> tuple[bool, str]:
    cmd = [
        "omnivoice-infer",
        "--model", "k2-fsa/OmniVoice",
        "--text", chunk,
        "--output", str(out),
    ]
    if ref:
        cmd += ["--ref_audio", str(ref)]
    if instruct:
        cmd += ["--instruct", instruct]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        return False, result.stderr[:300]
    return True, ""


def _synth_persistent(synth, chunk: str, ref: Optional[Path],
                      instruct: Optional[str], out: Path) -> tuple[bool, str]:
    try:
        synth(chunk, str(ref) if ref else None, instruct or None, str(out))
        return True, ""
    except Exception as exc:
        return False, str(exc)[:300]


def _synth_remote(url: str, chunk: str, ref: Optional[Path],
                  instruct: Optional[str], out: Path) -> tuple[bool, str]:
    try:
        files = {}
        data = {"text": chunk}
        if instruct:
            data["instruct"] = instruct
        if ref and ref.exists():
            files["ref_audio"] = (ref.name, ref.read_bytes(), "audio/wav")

        endpoint = url.rstrip("/") + "/tts"
        r = requests.post(endpoint, data=data, files=files or None, timeout=600)
        if r.status_code != 200:
            return False, f"HTTP {r.status_code}: {r.text[:200]}"
        out.write_bytes(r.content)
        return True, ""
    except Exception as exc:
        return False, str(exc)[:300]


# ── Synthesis worker (runs in a thread) ─────────────────────────────────────

def run_synthesis(
    job_id: str,
    text: str,
    ref_audio_path: Optional[Path],
    instruct: Optional[str],
    max_words: int,
    backend: str,
    remote_url: str,
) -> None:
    job = JOBS[job_id]

    def log(msg: str) -> None:
        job["log"].append(msg)

    try:
        chunks = chunk_text(text, max_words)
        total = len(text.split())
        log(f"📝 {total:,} words → {len(chunks)} chunks (max {max_words} words each)")
        log(f"🔧 Backend: {backend}")

        # Resolve the per-chunk synth function for the selected backend.
        persistent_synth = None
        if backend == "local_persistent":
            persistent_synth = _ensure_persistent_model(log)
            if persistent_synth is None:
                log("↩️  Falling back to local_cli backend.")
                backend = "local_cli"
        elif backend == "remote":
            if not remote_url:
                log("❌ Remote backend selected but no URL was provided.")
                job["status"] = "failed"
                return
            log(f"🌐 Remote relay: {remote_url}")

        wav_files: list[Path] = []
        for i, chunk in enumerate(chunks):
            out = OUTPUT_DIR / f"_chunk_{job_id}_{i:04d}.wav"
            log(f"[{i + 1}/{len(chunks)}] Synthesizing {len(chunk.split())} words...")

            if backend == "local_persistent":
                ok, err = _synth_persistent(persistent_synth, chunk, ref_audio_path,
                                            instruct, out)
            elif backend == "remote":
                ok, err = _synth_remote(remote_url, chunk, ref_audio_path,
                                        instruct, out)
            else:
                ok, err = _synth_cli(chunk, ref_audio_path, instruct, out)

            if not ok:
                log(f"⚠️  Chunk {i + 1} failed — {err}")
            else:
                log(f"✅ Chunk {i + 1} done")
                wav_files.append(out)

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

        mins = total / 150  # ~150 words per minute spoken
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


@app.post("/synthesize")
async def synthesize(
    text: str = Form(...),
    instruct: str = Form(""),
    max_words: int = Form(400),
    backend: str = Form("local_persistent"),
    remote_url: str = Form(""),
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
        args=(job_id, text, ref_path, instruct or None, max_words,
              backend, remote_url.strip()),
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
