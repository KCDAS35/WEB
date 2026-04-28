# Functional Specification — PlaceinTime TTS Suite

## Goal

A unified text-to-speech platform that any operator can use without technical knowledge:
1. Paste text → select voice → click synthesize → download or play audio
2. AI agents can call the API programmatically for automated narration

---

## Module 1 — Synthesis Interface

**Inputs:**
- Text (paste or upload .txt file)
- Engine selection: OmniVoice | FishSpeech | VibeVoice
- Voice profile (from saved library) or upload a new reference audio
- Language (auto-detect or manual select)
- Output format: WAV | MP3

**Behavior:**
- Text over 400 words is automatically chunked and concatenated
- Progress bar shown during synthesis
- Output file named: `{date}_{voice_profile}_{first_5_words}.wav`
- Output saved to `/outputs/` folder

---

## Module 2 — Voice Library

- Store named voice profiles (reference audio clips)
- Each profile: name, language, sample audio, date added
- Used for consistent branding (e.g., "Foundation Narrator EN", "Foundation Narrator ES")
- Upload new voice: record or upload 10-30 second audio clip

---

## Module 3 — Job Queue

- Long synthesis jobs (10+ minutes of audio) run in background
- Operator sees: job ID, status (queued/running/complete), estimated time
- Notification when complete (browser notification or dashboard alert)
- Failed jobs show error reason

---

## Module 4 — Output Library

- All synthesized files listed with metadata
- Filterable by date, voice, engine, language
- Playback in browser
- Download link
- Delete option

---

## Module 5 — Settings

- Default engine
- Default voice profile
- Output folder path
- API keys for cloud TTS engines (optional future expansion)

---

## Engine Status Indicators

Dashboard tile shows each engine:
- Green: installed and ready
- Yellow: installed but GPU not available (CPU fallback — slower)
- Red: not installed
- Gray: not configured

---

## Operator Use Cases

1. **Content narration:** Paste a blog post, select "Foundation EN" voice, synthesize, download
2. **Client welcome message:** Paste script in Spanish, select "ES Female" voice, synthesize
3. **Video narration:** Upload script .txt, synthesize, output synced to video production
4. **Automated morning announcement:** Comms Agent sends daily text to API, publishes result
