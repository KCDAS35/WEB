# PlaceinTime Web Services — Session Notes
## Last session: 13 April 2026

---

## MY VISION
> "I intend to be capable of offering the best orientation to web
> presence and communication in the world."

This is a **web services business** serving small/medium businesses,
starting in Lima, Peru. The goal is to give every local business a
professional online presence, reachable via WhatsApp, and grow into a
full-service digital communications agency.

---

## WHAT WAS BUILT THIS SESSION

### Project root: /home/user/WEB  (branch: claude/add-app-launcher-ZR5vj)

| File | Purpose |
|------|---------|
| `index.html` | Main hub — links to AI apps, clients, dashboard, onboarding |
| `dashboard.html` | **Private** client tracker — status, notes, WA links |
| `onboarding.html` | Client intake form (Spanish) — biz info, services, design prefs |
| `sites/veto-solorzano/index.html` | Carpentry landing page |
| `sites/nelson-caballero-dental/index.html` | Dental clinic landing page |
| `sites/edwin-vereau/index.html` | Painting & construction landing page |
| `sites/elsa-ma/index.html` | Shopping & retail landing page |
| `sites/multiservicios-ore/index.html` | Installation & maintenance landing page |

### AI tools also installed (separate from client work)
- `demo/vibevoice_realtime_colab.ipynb` — real-time voice AI (needs Colab T4 GPU)
- `fish-speech/` — TTS submodule (run: `git submodule update --init --recursive`)

---

## THE 5 FIRST CLIENTS

| # | Client | Business | Contact |
|---|--------|----------|---------|
| 1 | Veto Solorzano Perez | **Carpentry** | WA: solorzano |
| 2 | Nelson Caballero Dental | **Dental clinic** — Lince & La Molina | +51 949 269 557 |
| 3 | Edwin Vereau | **Painting & construction** (EIRL, RUC: 20611158018) | WA: 924 497 185 |
| 4 | Elsa Ma | **Shopping & retail** | +51 990 247 354 |
| 5 | Multiservicios "ORE" | **Installation & maintenance** (13 services) | 960 935 502 |

---

## IMMEDIATE NEXT STEPS (pick up here after reboot)

1. **Send onboarding form to each client**
   - Share link: `onboarding.html`
   - They fill in: logo, photos, exact services text, social links, hours
   - Their answers auto-save to localStorage + trigger a mailto

2. **Collect assets from each client via WhatsApp**
   - Logo file (PNG/JPG)
   - 3–5 photos of their work/products
   - Exact business name as they want it displayed

3. **Update each landing page** with real content once assets arrive
   - Replace placeholder text with their actual descriptions
   - Add real logo/photos

4. **Host the sites** — options discussed:
   - Cheapest: GitHub Pages (free, static hosting from this repo)
   - With custom domain: buy `solorzano-carpinteria.com` etc. (~$12/yr)
   - VPS needed only for AI apps (VibeVoice/Fish-Speech), NOT for these static pages

5. **GitHub Pages deployment** (easiest free hosting):
   ```
   # In GitHub repo settings → Pages → Deploy from branch: main
   # Each client site will be at:
   # https://kcdas35.github.io/WEB/sites/veto-solorzano/
   # https://kcdas35.github.io/WEB/sites/nelson-caballero-dental/
   # etc.
   ```

---

## PLANNING & GROWTH IDEAS (to discuss next session)

### Service packages to offer clients:
- **Basic** — 1-page landing page + WhatsApp button ($X/mo)
- **Standard** — Landing page + Google Business Profile setup + 1 social media template
- **Premium** — Full site + SEO + monthly content + analytics

### Tools to consider building next:
- Invoice/quote generator for clients
- WhatsApp message templates for each business type
- Social media post templates (Canva-compatible)
- Google Business Profile setup guide

### Scaling web hosting (for 10–50 clients):
- Static sites (HTML/CSS like these) = **free on GitHub Pages**, no server needed
- Add a backend only when clients need forms, bookings, or e-commerce
- GPU cloud (RunPod/Vast.ai) only needed for AI voice tools, NOT these websites

---

## HOW TO REOPEN EVERYTHING AFTER REBOOT

```bash
# 1. Open terminal and navigate to project
cd /home/user/WEB

# 2. Make sure you're on the right branch
git checkout claude/add-app-launcher-ZR5vj

# 3. Open the hub in browser (if running a local server)
python3 -m http.server 8080
# then visit: http://localhost:8080/index.html

# 4. Or just open index.html directly in Firefox/Chrome
```

---

## IMPORTANT REMINDERS
- All client pages have **"Página web por PlaceinTime Web Services"** in the footer
- Every WhatsApp button has a pre-filled message so clients don't have to type
- The dashboard saves status & notes locally in the browser (localStorage)
- The onboarding form is in **Spanish** (for Lima clients)

---
*Saved by Claude Code — PlaceinTime Web Services*
