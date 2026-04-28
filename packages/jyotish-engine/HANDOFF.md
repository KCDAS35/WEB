# HANDOFF: Jyotish Vedic Astrology Engine

## Project Identity

**Project Name:** Jyotish — Vedic Astrological Computation Engine  
**Type:** Astrology calculation API + optional web interface  
**Owner:** PlaceinTime / Jagat Sampurna International Yogi Foundation  
**Status:** Not yet built — specifications complete, ready for implementation

---

## Vision

A precise, classical Jyotish (Vedic/Hindu astrology) computation engine that can:
- Calculate birth charts (Janma Kundali / Rashi chart)
- Compute planetary positions using the sidereal zodiac (Lahiri ayanamsha)
- Generate Navamsha (D-9) and other divisional charts
- Calculate Vimshottari Dasha periods (major/minor/sub periods)
- Determine Muhurta (auspicious timing) for events
- Produce Panchanga (daily almanac: tithi, vara, nakshatra, yoga, karana)
- Assess compatibility (Kundali Milan / Ashtakoot matching)
- Offer plain-language interpretations of key placements

---

## Why This Matters

The Foundation is rooted in yogic and Vedic tradition. A precise Jyotish engine serves:
- Personal consultations with clients
- Muhurta selection for Foundation events
- Daily Panchanga for practitioners
- Educational content for the Foundation's library and media productions

---

## Technical Approach

**Recommended core library:** `flatlib` (Python) or `pyswisseph` (Swiss Ephemeris bindings)  
- `pyswisseph` is the gold standard for precision — same engine used by professional Jyotish software
- Lahiri ayanamsha (standard for Jyotish) supported natively

**Architecture:**
- Python backend with FastAPI
- Calculations done server-side using Swiss Ephemeris
- JSON API output — easy for any agent or frontend to consume
- Optional web interface for human operators

**No paid APIs needed** — Swiss Ephemeris is open source and works offline.

---

## Core Features (Priority Order)

### Phase 1 — Core Calculations
1. **Birth Chart (Rashi)** — All 9 grahas placed in signs and houses
2. **Ascendant (Lagna)** — Calculated from birth time and location
3. **Nakshatra** — For each graha, plus Moon nakshatra (Janma Nakshatra)
4. **Vimshottari Dasha** — Full period sequence from birth

### Phase 2 — Extended Charts
5. **Navamsha (D-9)** — Divisional chart for deeper analysis
6. **Ashtakavarga** — Bindhu (point) system for transits
7. **Panchanga** — Daily almanac

### Phase 3 — Applied Jyotish
8. **Muhurta** — Auspicious timing calculator
9. **Kundali Milan** — Compatibility matching (Ashtakoot, 36-point system)
10. **Transits** — Current planetary positions overlaid on natal chart
11. **Plain-language report** — AI-generated interpretation (Claude/Gemini)

---

## Data Models

### Birth Data (Input)
```json
{
  "name": "Ravi Kumar",
  "birth_date": "1985-03-15",
  "birth_time": "14:32:00",
  "birth_place": "Delhi, India",
  "latitude": 28.6139,
  "longitude": 77.2090,
  "timezone": "Asia/Kolkata",
  "ayanamsha": "lahiri"
}
```

### Chart (Output)
```json
{
  "lagna": { "sign": "Scorpio", "degree": 12.4, "house": 1 },
  "grahas": {
    "Sun":     { "sign": "Pisces",  "degree": 0.8,  "house": 5, "nakshatra": "Uttara Bhadrapada", "pada": 2 },
    "Moon":    { "sign": "Cancer",  "degree": 22.1, "house": 9, "nakshatra": "Ashlesha",           "pada": 4 },
    "Mars":    { "sign": "Capricorn","degree": 8.3, "house": 3, "nakshatra": "Uttara Ashadha",     "pada": 1 },
    "Mercury": { ... },
    "Jupiter": { ... },
    "Venus":   { ... },
    "Saturn":  { ... },
    "Rahu":    { ... },
    "Ketu":    { ... }
  },
  "dasha": {
    "mahadasha": { "lord": "Jupiter", "start": "2020-01-10", "end": "2036-01-10" },
    "antardasha": { "lord": "Saturn",  "start": "2024-05-01", "end": "2026-08-15" }
  }
}
```

---

## API Endpoints

```
POST /chart
  body: birth_data
  returns: full rashi chart with all grahas and lagna

POST /dasha
  body: birth_data
  returns: full Vimshottari Dasha sequence (120 years)

POST /navamsha
  body: birth_data
  returns: D-9 chart

POST /panchanga
  body: { date, latitude, longitude, timezone }
  returns: tithi, vara, nakshatra, yoga, karana

POST /muhurta
  body: { event_type, date_range_start, date_range_end, location }
  returns: list of auspicious windows ranked by quality

POST /compatibility
  body: { person1: birth_data, person2: birth_data }
  returns: Ashtakoot score (out of 36) with breakdown

POST /report
  body: birth_data
  returns: AI-generated plain-language interpretation of the chart
```

---

## Setup Instructions (For Implementing Agent)

```bash
pip install pyswisseph fastapi uvicorn geopy timezonefinder
# Download Swiss Ephemeris data files:
# https://www.astro.com/swisseph/ephe/ — download SE1 files to ./ephe/
```

**Minimal working example:**
```python
import swisseph as swe
swe.set_ephe_path('./ephe')
swe.set_sid_mode(swe.SIDM_LAHIRI)  # Lahiri ayanamsha for Jyotish

jd = swe.julday(1985, 3, 15, 14.533)  # Julian Day for birth datetime
sun_pos = swe.calc_ut(jd, swe.SUN, swe.FLG_SIDEREAL)
print(f"Sun sidereal longitude: {sun_pos[0][0]:.4f}°")
```

---

## Handoff Instructions

1. Read this HANDOFF.md
2. Read `/specs/functional-spec.md` for all calculation details
3. Read `/specs/api-spec.md` for endpoint signatures
4. Install `pyswisseph` and download ephemeris data files
5. Start with Phase 1: birth chart + dasha only
6. Build the FastAPI wrapper around it
7. Test with known charts (verify against established Jyotish software like Jagannatha Hora)
8. Add Phase 2 and 3 features progressively

---

## Integration with Foundation

- The HQ Mission Control can store client birth data and retrieve their charts on demand
- The Media Production Hub can schedule astrologically auspicious recording dates via Muhurta
- The Foundation's daily Panchanga can be posted automatically each morning (Comms Agent)
- AI agents (Claude/Gemini/OpenAI) generate the interpretive text from the raw chart JSON
