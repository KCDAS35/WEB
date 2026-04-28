# Functional Specification — Jyotish Vedic Astrology Engine

## Calculation Standards

- **Zodiac:** Sidereal (not tropical)
- **Ayanamsha:** Lahiri (Chitrapaksha) — standard for Indian Jyotish
- **House System:** Whole-sign houses (each sign = one house)
- **Grahas calculated:** Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn, Rahu, Ketu
- **Ephemeris:** Swiss Ephemeris (pyswisseph) — offline capable, precision to arcseconds

---

## Phase 1 — Birth Chart (Rashi)

**Input:** Name, birth date, birth time, birth place (or lat/lon/timezone)

**Output:**
- Ascendant (Lagna): sign, degree, nakshatra
- All 9 grahas: sign, degree, house, nakshatra, pada, retrograde status
- House lord for each of the 12 houses
- Dignity status: exalted / own sign / moolatrikona / neutral / debilitated
- Current Vimshottari Dasha (Mahadasha + Antardasha + Pratyantardasha)

**Validation:** Test against Jagannatha Hora software output. Tolerance: < 0.01° for graha positions.

---

## Phase 2 — Divisional Charts

**Navamsha (D-9):**
- Each sign divided into 9 equal parts (3°20' each)
- Planetary placements recalculated for D-9
- Used for: relationship analysis, deeper dharma reading

**Dashamsha (D-10):** Career chart (optional Phase 2 addition)

---

## Phase 3 — Panchanga (Daily Almanac)

Five limbs of the day calculated for any date/location:
1. **Tithi** — Lunar day (1-30), name, lord, quality
2. **Vara** — Day of week with ruling planet
3. **Nakshatra** — Moon's current nakshatra with pada
4. **Yoga** — One of 27 yogas (Sun+Moon longitude combination)
5. **Karana** — Half-tithi (11 karanas, repeating cycle)

Special flags:
- Rahu Kalam (inauspicious period)
- Gulika Kalam
- Abhijit Muhurta (powerful midday window)

---

## Phase 3 — Vimshottari Dasha

120-year planetary period system:
- Sequence: Ketu(7) → Venus(20) → Sun(6) → Moon(10) → Mars(7) → Rahu(18) → Jupiter(16) → Saturn(19) → Mercury(17)
- Starting dasha determined by Moon's nakshatra at birth
- Output: list of all Mahadashas, each with Antardashas, each with Pratyantardashas
- Include: start date, end date, lord, sub-lord

---

## Phase 3 — Muhurta Calculator

**Input:** Event type, date range, location

**Event types:** Marriage, business launch, travel, surgery, housewarming, naming ceremony, foundation event

**Output:** Ranked list of auspicious windows with scores

**Scoring factors:**
- Tithi quality (avoid 4th, 8th, 9th, 12th, 14th, Amavasya for most events)
- Nakshatra quality for event type
- Vara suitability
- Absence of Rahu/Gulika Kalam
- Moon dignity
- Lagna dignity at proposed time

---

## Phase 3 — Kundali Milan (Compatibility)

**Input:** Two birth charts

**Output:** Ashtakoot score (out of 36) with breakdown:

| Koot | Max Points | What it Measures |
|---|---|---|
| Varna | 1 | Spiritual compatibility |
| Vashya | 2 | Mutual attraction |
| Tara | 3 | Destiny/health |
| Yoni | 4 | Physical/intimate compatibility |
| Graha Maitri | 5 | Mental/emotional compatibility |
| Gana | 6 | Temperament match |
| Bhakoot | 7 | Love and prosperity |
| Nadi | 8 | Health and progeny |

Score interpretation: 18+ acceptable, 24+ good, 30+ excellent.

---

## AI Interpretation Layer

After chart calculation, send the structured JSON to an LLM (Claude/Gemini/OpenAI) with a system prompt containing Jyotish interpretive rules.

The LLM generates:
- 3-5 sentence Lagna interpretation
- Moon nakshatra personality description
- Current dasha period meaning
- 1-2 key yogas (combinations) present in the chart

This layer is **separate** from the calculation engine — calculations are always deterministic; interpretation is LLM-generated.

---

## Testing Protocol

1. Use the birth data of a well-known historical figure with verified chart
2. Compare output against Jagannatha Hora (free Windows software, gold standard)
3. Graha positions must match to within 0.01°
4. Dasha start/end dates must match to within 1 day
5. Run test suite before any deployment
