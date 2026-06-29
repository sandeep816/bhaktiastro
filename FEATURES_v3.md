# FEATURES.md — Vedic Astrology Engine: Complete Feature Roadmap

> **Version:** 4.0
> **Last Updated:** June 2026
> **Author:** Sandeep Sharma
> **Project:** Vedic Astrology Engine — Open Source / BhaktiRas Integration Ready
> **Cross-reference:** `CALCULATIONS.md`, `PROJECT_PHASES.md`, `CURSOR_RULES.md`

---

## 🎯 Project Goal

एक **free/open-source, local Python-based Vedic Astrology Engine** बनाना — जिसमें Panchang, Kundali, Dasha, Yoga/Dosha, Muhurat, और Matchmaking शामिल हों।

यह engine भविष्य में **REST API, Website, PWA, और BhaktiRas.in** जैसे platforms में integrate हो सके।

---

## 0. Core Principles — Non-Negotiable Rules

ये rules पूरे project में हर phase, हर module, हर commit पर लागू होंगे।

### 0.1 Architecture Rules

| Rule | Detail |
|---|---|
| No paid API | Core calculation हमेशा local Python (pyswisseph) से होगी |
| Layer separation | Astronomy → Astrology → Rules → Interpretation — कभी mix नहीं |
| AI = explanation only | AI केवल already-calculated data explain करेगा, calculate नहीं |
| AI no override | Raw planet data AI को directly pass नहीं होगा |
| Modular design | Future: mobile app, SaaS, API, WordPress plugin — सब possible रहे |

### 0.2 Development Rules

- **एक बार में केवल एक module।** Tests pass होने के बाद ही अगला शुरू करें।
- **Accuracy first.** UI, PDF, reports बाद में।
- **हर feature के साथ test cases** mandatory हैं।
- **हर calculation को कम से कम 2 trusted references से verify करें।**
  - Jagannatha Hora (free software)
  - Astro-Seek.com
  - Drik Panchang
  - Printed regional Panchang
- **Golden fixtures बनाओ** — known-correct JSON जिनसे future regressions पकड़ें।
- **Do Not Guess Rule** — formula verify नहीं हुआ तो placeholder + TODO + skip marker।

### 0.3 Quality Rules

- Timezone हमेशा explicit — assume नहीं होगा।
- DST international locations के लिए handle होगा।
- API versioning Day 1 से — `/api/v1/` format mandatory।
- `CHANGELOG.md` हर commit के साथ update होगा।
- Code में Hindi comments allowed हैं जहाँ domain logic explain करनी हो।

### 0.4 Output Rules

- JSON output structure stable रहेगा — breaking changes केवल major version bump पर।
- Output Hindi + English दोनों में future-ready।
- PDF/HTML report और raw JSON हमेशा available।

---

## 1. Architecture Overview

```
┌─────────────────────────────────────────────────────┐
│                   INPUT LAYER                        │
│   Date / Time / Location / Ayanamsa / Language      │
└────────────────────┬────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────┐
│               ASTRONOMY LAYER                        │
│   Julian Day · Ayanamsa · Planet Positions           │
│   Sunrise/Sunset · Coordinates · Rise/Set            │
│   backend/app/astronomy/                             │
└────────────────────┬────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────┐
│            ASTROLOGY CALCULATION LAYER               │
│   Nakshatra · Tithi · Yoga · Karana · Vara           │
│   Lagna · Houses · Dasha · Varga · Panchang          │
│   backend/app/astrology/                             │
└────────────────────┬────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────┐
│               RULES ENGINE LAYER                     │
│   Yoga Rules · Dosha Rules · Planet Rules            │
│   Marriage Rules · Career Rules · Remedy Rules       │
│   backend/app/rules/                                 │
└────────────────────┬────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────┐
│            INTERPRETATION ENGINE LAYER               │
│   Planet Interpretations · House Meanings            │
│   Dasha Explanations · Yoga/Dosha Text               │
│   backend/app/interpretation/                        │
└────────────────────┬────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────┐
│               REPORT ENGINE LAYER                    │
│   HTML · PDF · Markdown · JSON · DOCX                │
│   backend/app/reports/                               │
└────────────────────┬────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────┐
│                  REST API LAYER                      │
│   FastAPI /api/v1/* endpoints                        │
│   backend/app/api/v1/                                │
└────────────────────┬────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────┐
│             PRESENTATION LAYER                       │
│   Web UI (Jinja2) · PWA · BhaktiRas Integration     │
│   Future: Next.js · React Native · WordPress Plugin  │
└────────────────────┬────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────┐
│          OPTIONAL AI ASSISTANT LAYER                 │
│   Claude API — Hindi explanation only                │
│   NO calculations · NO data modification             │
└─────────────────────────────────────────────────────┘
```

---

## 2. Technical Stack

### 2.1 Backend

| Component | Technology | Notes |
|---|---|---|
| Language | Python 3.11+ | |
| Framework | FastAPI | Auto /docs included |
| Validation | Pydantic v2 | |
| Ephemeris | pyswisseph | Swiss Ephemeris wrapper |
| Timezone | timezonefinder + pytz | DST-aware |
| Database | SQLite → PostgreSQL | Local MVP → Production |
| ORM | SQLAlchemy | |
| Templates | Jinja2 | Server-side rendering |
| PDF | WeasyPrint | HTML → PDF |
| Testing | Pytest + pytest-cov | |

### 2.2 Frontend (MVP)

| Component | Technology |
|---|---|
| UI | HTML + Bootstrap 5 |
| Templates | Jinja2 |
| Charts | Chart.js / SVG |

### 2.3 Future Frontend

- **Next.js 15** — BhaktiRas.in integration
- **Astro** — Static Panchang pages (SEO)
- **PWA** — Offline Panchang
- **React Native** — Mobile app

### 2.4 Deployment Path

```
Local → Docker → VPS (Hetzner/DigitalOcean) → Cloudflare CDN → API Server
```

---

## 3. Folder Structure

```text
vedic-astrology-engine/
│
├── backend/
│   ├── app/
│   │   ├── main.py                        ← FastAPI entry point
│   │   ├── config.py                      ← EPHE_PATH, env vars, constants
│   │   │
│   │   ├── astronomy/                     ← Pure astronomical calculations
│   │   │   ├── julian.py                  ← Julian Day Number
│   │   │   ├── ephemeris.py               ← Swiss Ephe setup + verify
│   │   │   ├── ayanamsa.py                ← Lahiri / Raman / KP
│   │   │   ├── planet_positions.py        ← Tropical + Sidereal longitudes
│   │   │   ├── coordinates.py             ← Lat/Lon validation, TZ lookup
│   │   │   ├── rise_set.py                ← Sunrise, Sunset, Moonrise, Moonset
│   │   │   ├── search.py                  ← Binary search for boundary times
│   │   │   └── utils.py                   ← normalize_deg, deg_to_dms, UTC convert
│   │   │
│   │   ├── astrology/                     ← Vedic astrology derived calculations
│   │   │   ├── nakshatra.py               ← Nakshatra + Pada
│   │   │   ├── tithi.py                   ← Tithi + boundaries
│   │   │   ├── yoga.py                    ← Panchang Yoga
│   │   │   ├── karana.py                  ← Karana
│   │   │   ├── vara.py                    ← Vedic weekday
│   │   │   ├── lagna.py                   ← Ascendant
│   │   │   ├── houses.py                  ← Whole Sign Houses
│   │   │   ├── dasha.py                   ← Vimshottari Dasha
│   │   │   ├── varga.py                   ← Divisional charts D1–D60
│   │   │   ├── aspects.py                 ← Parashari Drishti
│   │   │   ├── dignity.py                 ← Planet dignity + combustion
│   │   │   ├── strengths.py               ← Shadbala
│   │   │   ├── ashtakavarga.py            ← Ashtakavarga
│   │   │   ├── transit.py                 ← Gochar + Sade Sati
│   │   │   ├── matching.py                ← Kundali Milan
│   │   │   ├── muhurat.py                 ← Muhurat finder
│   │   │   ├── panchang.py                ← Daily Panchang assembler
│   │   │   └── kundali.py                 ← Kundali assembler
│   │   │
│   │   ├── constants/                     ← Static data, names, mappings
│   │   │   ├── planets.py                 ← Planet IDs + names (Hi/En/Sa)
│   │   │   ├── rashi.py                   ← 12 signs (Hi/En/Sa)
│   │   │   ├── nakshatra.py               ← 27 nakshatras + lords
│   │   │   ├── tithi.py                   ← 30 tithi names
│   │   │   ├── yoga.py                    ← 27 Panchang yogas
│   │   │   ├── karana.py                  ← Karana sequence + types
│   │   │   ├── dasha.py                   ← Dasha lords + years
│   │   │   ├── varga.py                   ← Divisional chart formulas
│   │   │   ├── dignity.py                 ← Exaltation, debilitation, friendship
│   │   │   └── languages.py               ← i18n string keys
│   │   │
│   │   ├── rules/                         ← Deterministic logic
│   │   │   ├── yoga_rules.py              ← Yoga detection (rule id + formula)
│   │   │   ├── dosha_rules.py             ← Dosha detection
│   │   │   ├── planet_rules.py            ← Planet-house rules
│   │   │   ├── house_rules.py             ← House significations
│   │   │   ├── dasha_rules.py             ← Dasha interpretation triggers
│   │   │   ├── marriage_rules.py          ← Marriage indicators
│   │   │   ├── career_rules.py            ← Career indicators
│   │   │   ├── health_rules.py            ← Health indicators
│   │   │   └── remedy_rules.py            ← Remedy mapping
│   │   │
│   │   ├── interpretation/                ← Text output (not calculation)
│   │   │   ├── planets.py
│   │   │   ├── houses.py
│   │   │   ├── dashas.py
│   │   │   ├── yogas.py
│   │   │   ├── doshas.py
│   │   │   └── remedies.py
│   │   │
│   │   ├── reports/                       ← Report generation
│   │   │   ├── basic_kundali.py
│   │   │   ├── detailed_kundali.py
│   │   │   ├── panchang_report.py
│   │   │   └── templates/                 ← Jinja2 HTML templates
│   │   │
│   │   ├── schemas/                       ← Pydantic request/response models
│   │   │   ├── kundali.py
│   │   │   ├── panchang.py
│   │   │   ├── dasha.py
│   │   │   ├── varga.py
│   │   │   ├── matching.py
│   │   │   └── muhurat.py
│   │   │
│   │   ├── api/
│   │   │   └── v1/                        ← All routes versioned
│   │   │       ├── health.py
│   │   │       ├── kundali.py
│   │   │       ├── panchang.py
│   │   │       ├── dasha.py
│   │   │       ├── varga.py
│   │   │       ├── matchmaking.py
│   │   │       ├── muhurat.py
│   │   │       ├── transit.py
│   │   │       └── report.py
│   │   │
│   │   └── database/
│   │       ├── models.py
│   │       ├── crud.py
│   │       └── session.py
│   │
│   ├── tests/
│   │   ├── fixtures/
│   │   │   ├── jodhpur_1985_04_20.json    ← Primary golden fixture
│   │   │   ├── delhi_2000_01_01.json
│   │   │   ├── mumbai_1990_06_15.json
│   │   │   ├── london_1995_03_26.json     ← DST test case
│   │   │   └── newyork_2000_11_01.json    ← DST test case
│   │   ├── test_julian.py
│   │   ├── test_ayanamsa.py
│   │   ├── test_planets.py
│   │   ├── test_nakshatra.py
│   │   ├── test_tithi.py
│   │   ├── test_yoga.py
│   │   ├── test_karana.py
│   │   ├── test_lagna.py
│   │   ├── test_houses.py
│   │   ├── test_panchang.py
│   │   ├── test_dasha.py
│   │   └── test_api_integration.py
│   │
│   ├── requirements.txt
│   ├── requirements-dev.txt
│   └── README.md
│
├── data/
│   └── ephe/                              ← Swiss Ephemeris .se1 files (NOT in git)
│
├── frontend/
│   ├── templates/
│   └── static/
│
├── docs/
│   ├── API.md
│   ├── CALCULATIONS.md                    ← Math formulas reference
│   └── ACCURACY.md
│
├── reports/                               ← Generated output (NOT in git)
├── README.md
├── FEATURES.md                            ← This file
├── CHANGELOG.md
├── CURSOR_RULES.md                        ← AI coding assistant rules
├── docker-compose.yml
├── .pre-commit-config.yaml
└── .gitignore
```

---

## 4. Swiss Ephemeris Setup (Day 0 — सबसे पहले)

> ⚠️ यह step Phase 0 में होना चाहिए। बिना इसके कोई calculation संभव नहीं।

```text
data/
└── ephe/
    ├── seas_18.se1      ← Main ephemeris
    ├── semo_18.se1      ← Moon
    └── sepl_18.se1      ← Planets
```

Download: https://www.astro.com/ftp/swisseph/ephe/

```python
# backend/app/config.py
import os

EPHE_PATH = os.path.join(os.path.dirname(__file__), "../../data/ephe")
AYANAMSA_DEFAULT = "lahiri"
DEFAULT_LANGUAGE = "hi"
APP_VERSION = "0.1.0"
```

**Verify:**
```bash
python -c "import swisseph as swe; swe.set_ephe_path('data/ephe'); print(swe.calc_ut(2460000, swe.SUN))"
```

---

## 5. Phase-wise Feature Plan

### Phase 0 — Project Setup
*See:* `PROJECT_PHASES.md` Phase 0

- Folder structure
- Virtual environment
- Dependencies install
- Swiss Ephemeris setup
- Health check endpoint

### Phase 1 — Core Astronomy (MVP Foundation)
*See:* `PROJECT_PHASES.md` Phase 1–3, `CALCULATIONS.md` Sections 1–5

- Julian Day calculation
- Lahiri Ayanamsa
- Planetary longitudes (Sun–Ketu)
- Retrograde + speed detection
- Nakshatra + Pada
- Tithi
- Panchang Yoga
- Karana
- Vara
- Lagna (Ascendant)
- Whole Sign Houses
- Planet dignity basics

### Phase 2 — Panchang API
*See:* `PROJECT_PHASES.md` Phase 4, 6, 7, `CALCULATIONS.md` Sections 6–11

**Core Panchang:**
- Tithi, Nakshatra, Yoga, Karana, Vara — with start/end boundary times
- Paksha, Maas, Ritu, Ayan
- Vikram Samvat, Shaka Samvat
- Chandra Rashi (daily Moon sign)

**Time Events:**
- Sunrise, Sunset (accuracy: 2 min MVP → 1 min stable)
- Moonrise, Moonset (with null handling)

**Kaal periods:**
- Rahu Kalam, Gulika Kalam, Yamaganda

**Muhurat periods:**
- Brahma Muhurat, Abhijit Muhurat, Amrit Kalam

**Inauspicious:**
- Dur Muhurat, Varjyam

**Festival Flags:**
- Ekadashi, Pradosh, Amavasya, Purnima, Chaturthi, Ashtami

**Day Quality:**
- Shubhata score (1–10)
- Auspicious/Inauspicious summary

### Phase 3 — Kundali API
*See:* `PROJECT_PHASES.md` Phase 5, `CALCULATIONS.md` Sections 12–13, 16–17

- All planet positions (DMS format)
- Retrograde, combustion, speed status
- Planet dignity (exalted/debilitated/own/mooltrikona/friend/enemy/neutral)
- House placement + lordship
- Lagna, Moon sign, Sun sign
- Birth Nakshatra, Pada, Tithi, Yoga, Karana, Vara
- Planet aspects (Parashari Drishti)
- Basic Bhava analysis

### Phase 4 — Vimshottari Dasha
*See:* `PROJECT_PHASES.md` Phase 8, `CALCULATIONS.md` Section 14

- Birth dasha balance from Moon Nakshatra
- Mahadasha timeline (−20 to +50 years)
- Antardasha timeline
- Pratyantardasha (current period)
- Current running dasha detection
- Dasha lord dignity at birth

**Future:** Yogini, Ashtottari, Kalachakra, Chara, Narayana Dasha

### Phase 5 — Divisional Charts / Varga
*See:* `PROJECT_PHASES.md` Phase 9, `CALCULATIONS.md` Section 15

Build in this priority order:

| Priority | Chart | Domain |
|---|---|---|
| 1 | D1 Rashi | Birth chart (already in Phase 3) |
| 2 | D9 Navamsha | Marriage, Dharma, Soul |
| 3 | D10 Dashamsha | Career |
| 4 | D2 Hora | Wealth |
| 5 | D3 Drekkana | Siblings |
| 6 | D4 Chaturthamsha | Property |
| 7 | D7 Saptamsha | Children |
| 8 | D12 Dwadashamsha | Parents |
| 9 | D16 Shodashamsha | Vehicles |
| 10 | D20 Vimshamsha | Spirituality |
| Later | D24, D27, D30, D40, D45, D60 | As verified |

> ⚠️ D60 (Shashtiamsha) Phase 7 (Shadbala) के complete होने के बाद implement करें।

### Phase 6 — Yoga & Dosha Detection
*See:* `PROJECT_PHASES.md` Phase 10, `CALCULATIONS.md` Section 19

**Every yoga rule must have:**
- `rule_id` (unique string)
- `name_en` / `name_hi` / `name_sa`
- Detection formula (deterministic)
- Cancellation conditions
- `interpretation_template_id`
- Confidence level

**Yoga Groups:**

| Group | Yogas |
|---|---|
| Sun-Moon | Budhaditya, Gajakesari, Chandra Mangal, Amala |
| Panch Mahapurusha | Ruchaka, Bhadra, Hamsa, Malavya, Shasha |
| Raj & Dhan | Raj Yoga, Dhan Yoga, Vipreet Raj, Neech Bhanga, Lakshmi, Saraswati, Dharma Karmadhipati, Parivartan, Adhi |
| Sun-related | Vesi, Vasi, Ubhayachari |
| Moon-related | Sunapha, Anapha, Durudhara, Kemadruma, Kahala |

**Doshas:**

| Dosha | Detection Rule |
|---|---|
| Manglik | Mars in houses 1,2,4,7,8,12 from Lagna |
| Kaal Sarp | All planets within Rahu–Ketu axis |
| Pitra | Sun+Rahu conjunction OR 9th house affliction |
| Grahan | Sun/Moon conjunct Rahu or Ketu |
| Guru Chandal | Jupiter conjunct Rahu/Ketu |
| Shrapit | Saturn + Rahu conjunction |
| Kemadruma | No planets in 2nd/12th from Moon |
| Nadi | Same Nadi (Milan) |
| Bhakoot | 6-8 or 12-2 Moon sign pattern (Milan) |
| Gana | Dev/Manav/Rakshasa mismatch (Milan) |
| Rajju | Same Rajju group (Milan) |

### Phase 7 — Shadbala (Strength Calculations)
*Dependency: Phase 5 (D9 Navamsha required)*

| Bala Component | Notes |
|---|---|
| Sthana Bala | Position strength |
| Dig Bala | D9 required |
| Kala Bala | Time-based |
| Cheshta Bala | Retrograde bonus |
| Naisargika Bala | Sun strongest, Saturn weakest |
| Drik Bala | Aspectual |

- Ishta Bala + Kashta Bala
- Bhava Bala (house strength)
- Normalized score 1–100

### Phase 8 — Ashtakavarga

- Bhinna Ashtakavarga (7 planet charts)
- Sarvashtakavarga (combined)
- Planet-wise + House-wise bindu count
- Transit support from Ashtakavarga

### Phase 9 — Transit / Gochar

- Current + Daily + Monthly transit
- Saturn, Jupiter, Rahu/Ketu, Mars transit
- Sade Sati: detection, phase (rise/peak/setting)
- Dhaiya detection
- Transit over natal Moon/Lagna/planets
- Ashtakavarga-based transit quality

### Phase 10 — Matchmaking / Kundali Milan

**Ashtakoota Guna Milan:**

| Koota | Points | Domain |
|---|---|---|
| Varna | 1 | Spiritual |
| Vashya | 2 | Attraction |
| Tara | 3 | Destiny |
| Yoni | 4 | Physical |
| Graha Maitri | 5 | Mental |
| Gana | 6 | Nature |
| Bhakoot | 7 | Family |
| Nadi | 8 | Progeny |
| **Total** | **36** | |

Additional: Manglik check, Vedha check, Rajju check, Compatibility summary

### Phase 11 — Muhurat

**Types:** Marriage, Griha Pravesh, Business, Vehicle, Property, Naamkaran, Mundan, Upanayan, Travel, Daily Shubh

**Filtering logic:**
```
Shubh Tithi + Shubh Nakshatra + Shubh Vara
+ No Rahu Kalam + No Gulika + Shubh Yoga + Valid Karana
= Shubh Muhurat ✓
```

### Phase 12 — Predictions

Life areas (rule-based templates, not AI):
- Personality, Career, Business, Finance, Marriage, Children, Education, Health, Property, Vehicle, Foreign Travel/Settlement, Spirituality, Legal, Government Job, Family, Social Status

### Phase 13 — Remedies

| Category | Examples |
|---|---|
| Mantra | Planet + Beej mantras |
| Daan | Planet-wise, day-wise items |
| Vrat | Weekday fasting |
| Temple | Deity-wise visit |
| Gemstone | Rashi/Planet ratna |
| Rudraksha | Mukhi by planet |
| Yantra | Planet yantras |
| Lifestyle | Routine + direction + color |

Mapping: Planet-wise / Dosha-wise / Dasha-wise

### Phase 14 — Report Generation

| Report | Format |
|---|---|
| Basic Kundali | HTML, PDF |
| Detailed Kundali | HTML, PDF, JSON |
| Career Report | HTML, PDF |
| Marriage Report | HTML, PDF |
| Panchang Report | HTML, PDF |
| Matchmaking Report | HTML, PDF |
| Muhurat Report | HTML, PDF |
| Yearly Report | HTML, PDF |

Formats: HTML · PDF (WeasyPrint) · Markdown · JSON · DOCX
Languages: Hindi (primary) · English · Future: Gujarati, Marathi, Tamil...

### Phase 15 — Web App (MVP UI)

Pages: Home, Kundali form, Panchang (daily/monthly), Kundali result, Dasha timeline, Matchmaking, Muhurat finder, Report download, Dashboard

### Phase 16 — REST API (Versioned)

```http
GET  /api/v1/health
POST /api/v1/panchang
POST /api/v1/panchang/monthly
POST /api/v1/kundali
POST /api/v1/dasha
POST /api/v1/varga
POST /api/v1/matchmaking
POST /api/v1/muhurat
POST /api/v1/transit
POST /api/v1/report
GET  /api/v1/cities?q=jodhpur
```

**Standard Input:**
```json
{
  "name": "Sandeep Sharma",
  "date": "1985-04-20",
  "time": "18:10",
  "place": "Jodhpur, Rajasthan, India",
  "latitude": 26.2389,
  "longitude": 73.0243,
  "timezone": 5.5,
  "ayanamsa": "lahiri",
  "language": "hi"
}
```

**Standard Output:**
```json
{
  "meta": {
    "version": "1.0",
    "ayanamsa": "lahiri",
    "ayanamsa_value": 24.11,
    "language": "hi",
    "generated_at": "2026-06-01T10:00:00Z",
    "calculation_time_ms": 45
  },
  "birth_details": {},
  "panchang": {},
  "planets": [],
  "houses": [],
  "charts": { "D1": {}, "D9": {} },
  "dashas": { "mahadasha": {}, "antardasha": {}, "pratyantardasha": {} },
  "yogas": [],
  "doshas": [],
  "strengths": {},
  "interpretation": {}
}
```

**Error Response:**
```json
{
  "error": true,
  "code": "INVALID_DATE",
  "message": "Date format must be YYYY-MM-DD",
  "message_hi": "तारीख का format YYYY-MM-DD होना चाहिए"
}
```

### Phase 17 — Database

**Tables:**

| Table | Purpose |
|---|---|
| users | User accounts |
| birth_profiles | Saved birth details |
| saved_kundalis | Calculated + stored |
| panchang_cache | Pre-calculated Panchang |
| cities | City → lat/lng/tz lookup |
| timezone_cache | TZ + DST rules |
| reports | Generated files |
| interpretation_templates | Rule-based text (Hi + En) |
| yoga_rules | Yoga detection rules |
| dosha_rules | Dosha detection rules |
| muhurat_rules | Muhurat filter rules |
| remedy_map | Dosha/Dasha → Remedy |

### Phase 18 — Admin Panel

Manage: Users, Reports, Cities, Interpretation templates, Remedies, Yoga/Dosha rules, Content translations, PDF templates

### Phase 19 — Developer Tools

- CLI: `python -m vedic_engine panchang --date 2026-06-01 --city jodhpur`
- pip-installable Python package
- Docker + docker-compose
- API docs (FastAPI auto-generated)
- GitHub Actions CI/CD
- Example Jupyter notebooks

### Phase 20 — AI Layer (Last)

> ⚠️ **Critical Rules:**
> - AI कभी planetary positions calculate नहीं करेगा
> - Raw degrees AI को pass नहीं होंगे
> - AI केवल `interpretation/` module का output receive करेगा
> - AI data override नहीं करेगा
> - All AI output "AI-generated" tag के साथ आएगा

**Features:** Hindi explanation, Kundali Q&A, Report summarizer, Life area analysis, BhaktiRas devotional integration

---

## 6. Advanced Feature Backlog (Post-MVP)

### Panchang Expansion
Choghadiya, Daily Hora, Tarabalam, Chandrabalam, Panchaka, Bhadra, Anandadi Yoga, Gowri Panchang, Hindu festival engine, Solar/Lunar eclipse calculation, Ekadashi/Pradosh/Sankashti calendars

### Advanced Vedic Systems
Jaimini (Chara Karaka, Arudha, Upapada, Jaimini aspects), Tajika/Varshaphala (Annual chart, Muntha, Sahams), KP Astrology (Sub-lord, Cuspal), Lal Kitab remedies, Nadi-style interpretation

### Future Adjacent Modules
Numerology, Vastu, Palmistry, Gemstone recommendation system, Devotional content personalization (BhaktiRas)

---

## 7. Accuracy & Testing Standards

### Tolerance Table

| Calculation | MVP | Stable |
|---|---:|---:|
| Planet longitude | 0.05° | 0.01° |
| Sunrise/Sunset | 2 min | 1 min |
| Tithi end time | 5 min | 2 min |
| Nakshatra end time | 5 min | 2 min |
| Lagna | 0.25° | 0.1° |

### Golden Fixtures Required

| Location | Date | Time | Purpose |
|---|---|---|---|
| Jodhpur | 20 Apr 1985 | 18:10 IST | Primary |
| Delhi | 1 Jan 2000 | 12:00 IST | Standard |
| Mumbai | 15 Jun 1990 | 06:30 IST | Morning birth |
| London | 26 Mar 1995 | 02:00 BST | DST case |
| New York | 1 Nov 2000 | 01:30 EST | DST end case |

### Accuracy Checklist (per feature)

- [ ] 2+ trusted references verified
- [ ] Timezone handling correct
- [ ] DST handled (international locations)
- [ ] Sunrise/Sunset within 2 min tolerance
- [ ] Tithi boundary within 5 min tolerance
- [ ] Nakshatra boundary within 5 min tolerance
- [ ] Lagna change at boundary tested
- [ ] Unit tests written + passing
- [ ] Golden fixture saved

---

## 8. CHANGELOG

```
## [Unreleased]
- FEATURES v4.0 — architecture diagram, layer separation, advanced backlog

## [0.2.0] - TBD
- Full Panchang module with festival flags + Shubhata score

## [0.1.0] - TBD
- Phase 0–1 complete: Julian, Ayanamsa, Planet positions, Basic Panchang API
```

---

## 9. Notes & Reminders

1. `data/ephe/` folder `.gitignore` में डालो — `.se1` files large हैं।
2. `reports/` folder भी `.gitignore` में डालो।
3. Lahiri Ayanamsa config से आए — code में hard-code नहीं।
4. `ayanamsa` parameter Day 1 से रखो — KP/Raman future में आएंगे।
5. BhaktiRas के लिए `"language": "hi"` parameter हमेशा support करो।
6. `docker-compose.yml` Day 1 से बनाओ, भले ही empty हो।
7. `CHANGELOG.md` हर commit के साथ update करो।
8. Formula verify नहीं हुआ = placeholder + TODO + test skip — कभी guess नहीं।

---

*यह एक living document है। हर phase complete होने पर update करें।*