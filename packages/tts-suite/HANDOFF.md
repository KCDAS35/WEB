# HANDOFF: TTS Suite — PlaceinTime Voice Engine

## Project Identity

**Project Name:** PlaceinTime TTS Suite  
**Codename:** OmniVoice / VibeVoice / FishVoice  
**Type:** Text-to-Speech Application Suite  
**Owner:** PlaceinTime Web Services  
**Status:** OmniVoice — Working prototype. VibeVoice — Colab demo. FishVoice — Submodule (uninitialized).

---

## What This Is

A suite of three complementary TTS tools for voice synthesis, real-time voice interaction, and zero-shot voice cloning. Together they form a full voice production pipeline for the Foundation and its clients.

| Tool | Technology | Capability | Status |
|---|---|---|---|
| **OmniVoice** | k2-fsa/OmniVoice | Zero-shot voice cloning, 600+ languages, long-form synthesis | Working |
| **VibeVoice** | Custom real-time TTS | Real-time streaming voice synthesis | Colab demo |
| **FishSpeech** | FishAudio/fish-speech | High-quality open-source TTS | Submodule (needs init) |

---

## OmniVoice — Current Implementation

**Location:** `/apps/omnivoice/`  
**Entry point:** `app.py`  
**Port:** 8765  
**Tech:** FastAPI + OmniVoice model

**What it does:**
- Accepts text input via web UI
- Chunks long text into 400-word segments for synthesis
- Synthesizes each chunk using OmniVoice model
- Concatenates audio segments into a final `.wav` file
- Plays back audio in the browser

**Key files:**
- `app.py` — FastAPI backend, synthesis logic
- `templates/index.html` — Web UI
- `requirements.txt` — Dependencies
- `install.bat` / `start.bat` — Windows launcher scripts

**To run:**
```bash
pip install -r requirements.txt
python app.py
# Browser opens at http://localhost:8765
```

---

## VibeVoice — Colab Demo

**Location:** `/demo/vibevoice_realtime_colab.ipynb`  
**Requirements:** Google Colab with T4 GPU  
**Capability:** Real-time streaming voice synthesis

**To run:** Open in Google Colab, select T4 GPU runtime, run all cells.

---

## FishSpeech — Submodule

**Location:** `/fish-speech/` (empty — submodule not initialized)  
**Source:** https://github.com/fishaudio/fish-speech  
**Capability:** High-quality open-source TTS engine

**To initialize:**
```bash
git submodule update --init --recursive
cd fish-speech
pip install -e .
```

---

## What Needs to Be Built

1. **Unified TTS API** — Single FastAPI endpoint that routes to any of the three engines
2. **Voice library** — Store and retrieve reference voice samples for cloning
3. **Job queue** — Handle long synthesis jobs asynchronously (Celery or background tasks)
4. **Voice profiles** — Named voice presets (e.g., "Foundation Narrator", "Client Welcome")
5. **Output storage** — Organized output folder with metadata (who requested, timestamp, engine used)
6. **Web UI upgrade** — Select engine, voice profile, language; download or stream result
7. **HQ Integration** — Media Agent in HQ Mission Control can trigger synthesis jobs

---

## API Design (To Be Implemented)

```
POST /synthesize
  body: { text, engine, voice_profile, language }
  returns: { job_id, status }

GET  /jobs/{job_id}
  returns: { status, audio_url, duration }

GET  /voices
  returns: list of stored voice profiles

POST /voices
  body: { name, reference_audio (upload) }

GET  /engines
  returns: available engines and their status
```

---

## Handoff Instructions

1. Read `HANDOFF.md` (this file)
2. Review `/specs/functional-spec.md` for full feature requirements
3. Review existing code in `/apps/omnivoice/app.py` — this is your starting point
4. Build the unified API on top of the existing OmniVoice backend
5. Add FishSpeech as a second engine once submodule is initialized
6. Keep the frontend as simple HTML/JS — no build tools required
7. Target platform: Linux (Foundation hardware) with optional Windows support

---

## Operator Use Cases

- "Read this blog post aloud in the Foundation's voice."
- "Create a welcome message for new clients in Spanish."
- "Generate a narration track for today's video presentation."
- "Clone the director's voice and synthesize the weekly announcement."
