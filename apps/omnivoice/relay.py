"""
OmniVoice Relay — standalone FastAPI server.

Runs on any GPU box (RunPod, Colab, a home workstation) and exposes a
single endpoint that the local OmniVoice app can POST chunks to:

    POST /tts
        form fields: text (required), instruct (optional),
                     ref_audio (optional file upload)
        returns:     audio/wav bytes

The model is loaded **once** at startup and kept resident in GPU
memory for the lifetime of the process, so every chunk runs at real
GPU speed. Same code path is used in demo/omnivoice_colab.ipynb
Step 5 — there is only one relay implementation to maintain.

Usage:
    python relay.py                 # listen on 0.0.0.0:8002
    python relay.py --port 9000
    HOST=127.0.0.1 python relay.py
"""

from __future__ import annotations

import argparse
import importlib
import os
import subprocess
import tempfile
from typing import Optional

import numpy as np
import soundfile as sf
from fastapi import FastAPI, File, Form, UploadFile
from fastapi.responses import Response


_API_ATTEMPTS = [
    ("omnivoice", "OmniVoice"),
    ("omnivoice.inference", "OmniVoice"),
    ("omnivoice.inference", "Inferencer"),
    ("omnivoice.model", "OmniVoice"),
]


def _load_model():
    """Return (model, 'python') if the Python API is importable, else
    (None, 'cli') so the relay falls back to the omnivoice-infer CLI."""
    for mod_path, cls_name in _API_ATTEMPTS:
        try:
            mod = importlib.import_module(mod_path)
            cls = getattr(mod, cls_name)
            model = cls.from_pretrained("k2-fsa/OmniVoice")
            print(f"[relay] loaded via {mod_path}.{cls_name}")
            return model, "python"
        except Exception:
            continue
    print("[relay] Python API not found — falling back to omnivoice-infer CLI")
    return None, "cli"


def _synth_python(model, text: str, ref_audio: Optional[str],
                  instruct: Optional[str], out_path: str) -> None:
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
            fn(**kwargs, output=out_path)
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


def _synth_cli(text: str, ref_audio: Optional[str],
               instruct: Optional[str], out_path: str) -> None:
    cmd = [
        "omnivoice-infer",
        "--model", "k2-fsa/OmniVoice",
        "--text", text,
        "--output", out_path,
    ]
    if ref_audio:
        cmd += ["--ref_audio", ref_audio]
    if instruct:
        cmd += ["--instruct", instruct]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(r.stderr[:400])


def build_app() -> FastAPI:
    print("[relay] loading OmniVoice model (one-time)...")
    model, mode = _load_model()

    app = FastAPI(title="OmniVoice Relay")

    @app.get("/")
    def health():
        return {"ok": True, "mode": mode}

    @app.post("/tts")
    async def tts(
        text: str = Form(...),
        instruct: str = Form(""),
        ref_audio: Optional[UploadFile] = File(None),
    ):
        ref_path: Optional[str] = None
        if ref_audio and ref_audio.filename:
            suf = os.path.splitext(ref_audio.filename)[1] or ".wav"
            tf = tempfile.NamedTemporaryFile(delete=False, suffix=suf)
            tf.write(await ref_audio.read())
            tf.close()
            ref_path = tf.name

        out = tempfile.NamedTemporaryFile(delete=False, suffix=".wav").name
        try:
            if mode == "python":
                _synth_python(model, text, ref_path, instruct or None, out)
            else:
                _synth_cli(text, ref_path, instruct or None, out)
            data = open(out, "rb").read()
        finally:
            for p in (ref_path, out):
                if p and os.path.exists(p):
                    try:
                        os.remove(p)
                    except OSError:
                        pass

        return Response(content=data, media_type="audio/wav")

    return app


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default=os.environ.get("HOST", "0.0.0.0"))
    parser.add_argument("--port", type=int,
                        default=int(os.environ.get("PORT", "8002")))
    args = parser.parse_args()

    import uvicorn
    uvicorn.run(build_app(), host=args.host, port=args.port, log_level="info")


if __name__ == "__main__":
    main()
