# PlaceinTime — Project Packages

Agent handoff bundles for the Three of Pentacles collaboration (Claude + Gemini + OpenAI).

Each package contains a HANDOFF.md (start here), specifications in /specs/, and where applicable, skeleton code in /skeleton/.

---

## Projects

### 1. Jagat Sampurna HQ Mission Control
**Path:** `jagat-sampurna-hq/`  
**What it is:** Foundation Operating System for the Jagat Sampurna International Yogi Foundation. Tracks personnel, AI agents, assets, inventory, living beings, spaces, visitors, clients, media, finances, and communications. One dashboard for a single human operator to manage the entire institution.  
**Status:** Fully specified. Skeleton backend and frontend created. Ready for full implementation.  
**Start here:** `jagat-sampurna-hq/HANDOFF.md`

### 2. TTS Suite
**Path:** `tts-suite/`  
**What it is:** Unified text-to-speech platform using OmniVoice (working), VibeVoice (Colab demo), and FishSpeech (submodule). Zero-shot voice cloning in 600+ languages.  
**Status:** OmniVoice prototype working at `/apps/omnivoice/`. Unified API and voice library need to be built.  
**Start here:** `tts-suite/HANDOFF.md`

### 3. Jyotish Vedic Astrology Engine
**Path:** `jyotish-engine/`  
**What it is:** Precise Vedic astrology calculation engine using Swiss Ephemeris (pyswisseph) with Lahiri ayanamsha. Birth charts, dashas, panchanga, muhurta, compatibility matching, and AI-generated interpretations.  
**Status:** Not yet built. Full specifications complete. Ready for implementation.  
**Start here:** `jyotish-engine/HANDOFF.md`

---

## For Incoming Agents (Gemini / OpenAI / Claude)

1. Read this README
2. Pick the project you are assigned to
3. Open that project's HANDOFF.md
4. Read the /specs/ folder
5. Implement starting with the priorities listed in HANDOFF.md
6. Use the existing skeleton code where provided
7. Commit to branch: `claude/package-projects-T8vqa`

## Architecture Consistency Rules

- All backends: Python + FastAPI
- All databases: SQLite (dev) — no external DB server required
- All frontends: Plain HTML5 + Vanilla JS — no npm, no React
- All APIs: RESTful JSON with /docs (Swagger) auto-generated
- All ports: HQ=8000, TTS=8765, Jyotish=8766
