# PROJECT_PHASES.md — Codex/Cursor Step-by-Step Development Tasks

> **Version:** 2.0
> **Purpose:** इस file को Cursor IDE / VS Code / Codex में use करके project को छोटे-छोटे safe tasks में build करना है।
> **Rule:** एक task complete + test pass होने के बाद ही अगला task करें।
> **Cross-reference:** `FEATURES.md`, `CALCULATIONS.md`, `CURSOR_RULES.md`

---

## ⚡ Working Rules (Commit Rules)

```
एक task = एक commit
हर commit से पहले:
  ✓ code run होता है
  ✓ tests pass होते हैं
  ✓ CHANGELOG.md update हुआ
  ✓ कोई भी calculation बिना test के "done" नहीं है
```

**Commit message format:**
```
feat(phase-X): task description

Examples:
feat(phase-0): create project folder structure
feat(phase-1): add julian day calculation with tests
fix(phase-2): correct tithi boundary tolerance
```

---

# Phase 0 — Project Setup

## Task 0.1 — Create Project Folder

```bash
mkdir vedic-astrology-engine
cd vedic-astrology-engine
git init
```

**Done when:**
- [ ] Folder exists
- [ ] Git initialized

---

## Task 0.2 — Create Virtual Environment

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# Mac/Linux
source .venv/bin/activate

python --version   # must be 3.11+
```

**Done when:**
- [ ] `.venv` created
- [ ] Python 3.11+ active

---

## Task 0.3 — Install Dependencies

```bash
# Core
pip install fastapi uvicorn "pydantic>=2.0" pyswisseph jinja2

# Timezone
pip install timezonefinder pytz

# Database
pip install sqlalchemy

# PDF
pip install weasyprint

# Testing + Dev
pip install pytest pytest-cov httpx black pre-commit

# Freeze
pip freeze > requirements.txt
```

Create `requirements-dev.txt`:
```text
pytest>=8.0
pytest-cov>=5.0
httpx>=0.27
black>=24.0
pre-commit>=3.0
```

**Done when:**
- [ ] `requirements.txt` created
- [ ] `import fastapi` works
- [ ] `import swisseph` works

---

## Task 0.4 — Create Folder Structure

```bash
mkdir -p backend/app/astronomy
mkdir -p backend/app/astrology
mkdir -p backend/app/constants
mkdir -p backend/app/rules
mkdir -p backend/app/interpretation
mkdir -p backend/app/reports/templates
mkdir -p backend/app/api/v1
mkdir -p backend/app/schemas
mkdir -p backend/app/database
mkdir -p backend/tests/fixtures
mkdir -p data/ephe
mkdir -p docs
mkdir -p reports
mkdir -p frontend/templates
mkdir -p frontend/static

# Create __init__.py files
touch backend/__init__.py
touch backend/app/__init__.py
touch backend/app/astronomy/__init__.py
touch backend/app/astrology/__init__.py
touch backend/app/constants/__init__.py
touch backend/app/rules/__init__.py
touch backend/app/interpretation/__init__.py
touch backend/app/reports/__init__.py
touch backend/app/api/__init__.py
touch backend/app/api/v1/__init__.py
touch backend/app/schemas/__init__.py
touch backend/app/database/__init__.py
touch backend/tests/__init__.py
```

**Done when:**
- [ ] All folders exist
- [ ] All `__init__.py` files created

---

## Task 0.5 — Add Swiss Ephemeris Data Files

Download from: https://www.astro.com/ftp/swisseph/ephe/

Place in `data/ephe/`:
```text
seas_18.se1
semo_18.se1
sepl_18.se1
```

**Done when:**
- [ ] Files downloaded and placed in `data/ephe/`
- [ ] Verify: `ls data/ephe/` shows 3 files

---

## Task 0.6 — Create .gitignore

```text
# .gitignore
.venv/
__pycache__/
*.pyc
*.pyo
.pytest_cache/
.coverage
htmlcov/
data/ephe/
reports/
*.pdf
*.log
.env
.DS_Store
```

**Done when:**
- [ ] `.gitignore` created

---

## Task 0.7 — Create Pre-commit Config

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 24.0.0
    hooks:
      - id: black
        language_version: python3.11
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-json
```

```bash
pre-commit install
```

**Done when:**
- [ ] `.pre-commit-config.yaml` created
- [ ] `pre-commit install` successful

---

## Task 0.8 — Create config.py

File: `backend/app/config.py`

```python
import os

# Swiss Ephemeris path
EPHE_PATH = os.path.join(os.path.dirname(__file__), "../../data/ephe")

# Ayanamsa
AYANAMSA_DEFAULT = "lahiri"
AYANAMSA_OPTIONS = ["lahiri", "raman", "kp"]

# Language
DEFAULT_LANGUAGE = "hi"
SUPPORTED_LANGUAGES = ["hi", "en"]

# App
APP_VERSION = "0.1.0"
APP_NAME = "Vedic Astrology Engine"

# Timezone
DEFAULT_TIMEZONE = 5.5  # IST

# Tolerances
TOLERANCE_SUNRISE_MINUTES = 2
TOLERANCE_TITHI_MINUTES = 5
TOLERANCE_NAKSHATRA_MINUTES = 5
TOLERANCE_LAGNA_DEGREES = 0.25
```

**Test:** `from backend.app.config import EPHE_PATH` — no error

**Done when:**
- [ ] `config.py` created
- [ ] Import works without error

---

## Task 0.9 — Create Basic FastAPI App

File: `backend/app/main.py`

```python
from fastapi import FastAPI
from backend.app.config import APP_NAME, APP_VERSION

app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
)

@app.get("/api/v1/health")
def health_check():
    return {
        "status": "ok",
        "app": APP_NAME,
        "version": APP_VERSION,
    }
```

```bash
uvicorn backend.app.main:app --reload
```

**Done when:**
- [ ] Server starts without error
- [ ] `GET /api/v1/health` returns `{"status": "ok"}`
- [ ] `/docs` opens in browser

---

## Task 0.10 — Create CHANGELOG.md

```markdown
# CHANGELOG.md

## [Unreleased]

## [0.0.1] - 2026-06-XX
### Added
- Project folder structure
- Virtual environment setup
- Basic FastAPI health endpoint
- Swiss Ephemeris data files setup
- Pre-commit hooks
```

**Done when:**
- [ ] `CHANGELOG.md` created

---

# Phase 1 — Core Astronomy

> **Goal:** Astronomical foundation layer — pure math, no astrology yet.
> **Reference:** `CALCULATIONS.md` Sections 1–5

---

## Task 1.1 — constants/rashi.py

```python
# 12 Rashis with multilingual names
RASHI_LIST = [
    {"index": 0, "name_en": "Mesha",      "name_hi": "मेष",      "name_sa": "Meṣa"},
    {"index": 1, "name_en": "Vrishabha",  "name_hi": "वृषभ",     "name_sa": "Vṛṣabha"},
    {"index": 2, "name_en": "Mithuna",    "name_hi": "मिथुन",    "name_sa": "Mithuna"},
    {"index": 3, "name_en": "Karka",      "name_hi": "कर्क",     "name_sa": "Karkaṭa"},
    {"index": 4, "name_en": "Simha",      "name_hi": "सिंह",     "name_sa": "Siṃha"},
    {"index": 5, "name_en": "Kanya",      "name_hi": "कन्या",    "name_sa": "Kanyā"},
    {"index": 6, "name_en": "Tula",       "name_hi": "तुला",     "name_sa": "Tulā"},
    {"index": 7, "name_en": "Vrishchika", "name_hi": "वृश्चिक",  "name_sa": "Vṛścika"},
    {"index": 8, "name_en": "Dhanu",      "name_hi": "धनु",      "name_sa": "Dhanus"},
    {"index": 9, "name_en": "Makara",     "name_hi": "मकर",      "name_sa": "Makara"},
    {"index": 10,"name_en": "Kumbha",     "name_hi": "कुम्भ",    "name_sa": "Kumbha"},
    {"index": 11,"name_en": "Meena",      "name_hi": "मीन",      "name_sa": "Mīna"},
]
```

**Test:** `assert len(RASHI_LIST) == 12`

**Done when:**
- [ ] 12 rashis defined
- [ ] Hindi names correct
- [ ] Test passes

---

## Task 1.2 — constants/planets.py

```python
import swisseph as swe

PLANETS = {
    "sun":     {"id": swe.SUN,     "name_en": "Sun",     "name_hi": "सूर्य",  "index": 0},
    "moon":    {"id": swe.MOON,    "name_en": "Moon",    "name_hi": "चन्द्र", "index": 1},
    "mars":    {"id": swe.MARS,    "name_en": "Mars",    "name_hi": "मंगल",   "index": 2},
    "mercury": {"id": swe.MERCURY, "name_en": "Mercury", "name_hi": "बुध",    "index": 3},
    "jupiter": {"id": swe.JUPITER, "name_en": "Jupiter", "name_hi": "गुरु",   "index": 4},
    "venus":   {"id": swe.VENUS,   "name_en": "Venus",   "name_hi": "शुक्र",  "index": 5},
    "saturn":  {"id": swe.SATURN,  "name_en": "Saturn",  "name_hi": "शनि",    "index": 6},
    "rahu":    {"id": swe.MEAN_NODE,"name_en": "Rahu",   "name_hi": "राहु",   "index": 7},
    "ketu":    {"id": None,        "name_en": "Ketu",    "name_hi": "केतु",   "index": 8},
}
# Note: Ketu = Rahu + 180° (calculated, no separate swe ID)
```

**Test:** `assert len(PLANETS) == 9`

**Done when:**
- [ ] 9 planets defined
- [ ] swe IDs correct
- [ ] Test passes

---

## Task 1.3 — astronomy/utils.py

Functions:

```python
def normalize_deg(value: float) -> float:
    """0–360 ke beech normalize karo"""
    return value % 360.0

def deg_to_dms(value: float) -> dict:
    """Decimal degrees → degrees, minutes, seconds"""
    d = int(value)
    m = int((value - d) * 60)
    s = round(((value - d) * 60 - m) * 60, 1)
    return {"degrees": d, "minutes": m, "seconds": s}

def local_datetime_to_utc(date: str, time: str, timezone: float) -> tuple:
    """Local datetime → UTC datetime"""
    # Returns (year, month, day, hour_utc_float)
```

**Tests:**
```python
assert normalize_deg(370.5) == 10.5
assert normalize_deg(-10.0) == 350.0
assert deg_to_dms(6.73) == {"degrees": 6, "minutes": 43, "seconds": 48.0}
```

**Done when:**
- [ ] All 3 functions implemented
- [ ] Tests pass

---

## Task 1.4 — astronomy/julian.py

```python
def calculate_julian_day(date: str, time: str, timezone: float) -> float:
    """
    Input: "1985-04-20", "18:10", 5.5
    Output: Julian Day UT (float)
    Reference: CALCULATIONS.md Section 2
    """
```

**Test:**
```python
jd = calculate_julian_day("1985-04-20", "18:10", 5.5)
assert abs(jd - 2446176.027777) < 0.001
```

**Done when:**
- [ ] Function implemented
- [ ] Known value test passes
- [ ] Edge case: midnight birth tested
- [ ] Edge case: timezone crossing date tested

---

## Task 1.5 — astronomy/ephemeris.py

```python
def set_ephe_path() -> None:
    """Swiss Ephemeris path set karo config se"""

def verify_ephemeris() -> bool:
    """Test: Sun longitude return hoti hai to True"""
```

**Test:**
```python
set_ephe_path()
assert verify_ephemeris() == True
```

**Done when:**
- [ ] Path set without error
- [ ] Sun longitude returns valid float

---

## Task 1.6 — astronomy/ayanamsa.py

```python
def get_ayanamsa(jd_ut: float, mode: str = "lahiri") -> float:
    """
    Lahiri Ayanamsa value return karo
    Reference: CALCULATIONS.md Section 3
    """
```

**Test:**
```python
jd = calculate_julian_day("1985-04-20", "18:10", 5.5)
ayanamsa = get_ayanamsa(jd)
assert 23.0 < ayanamsa < 25.0  # Lahiri ~24° in 1985
```

**Done when:**
- [ ] Lahiri returns float in expected range
- [ ] Mode parameter works (lahiri/raman/kp)
- [ ] Test passes

---

## Task 1.7 — astronomy/planet_positions.py

```python
def get_planet_positions(jd_ut: float, ayanamsa: float) -> list[dict]:
    """
    All 9 planets ki sidereal positions return karo
    Reference: CALCULATIONS.md Section 4
    Output per planet:
      planet, tropical_longitude, sidereal_longitude,
      rashi_index, rashi_name_hi, degree_in_rashi,
      speed, retrograde (bool)
    """
```

**Test:**
```python
positions = get_planet_positions(jd, ayanamsa)
assert len(positions) == 9
sun = next(p for p in positions if p["planet"] == "sun")
assert 0 <= sun["sidereal_longitude"] < 360
assert 0 <= sun["rashi_index"] <= 11
```

**Done when:**
- [ ] All 9 planets output
- [ ] Ketu = Rahu + 180° (verified)
- [ ] Retrograde detection correct
- [ ] Rashi index 0–11 range verified
- [ ] Tests pass

---

## Task 1.8 — astronomy/coordinates.py

```python
def validate_lat_lon(latitude: float, longitude: float) -> bool:
    """Lat -90 to 90, Lon -180 to 180"""

def get_timezone_from_lat_lon(latitude: float, longitude: float) -> float:
    """timezonefinder se UTC offset return karo"""
```

**Done when:**
- [ ] Validation raises error for invalid inputs
- [ ] Jodhpur (26.2389, 73.0243) → 5.5 returns correctly

---

# Phase 2 — Basic Astrology Calculations

> **Goal:** Vedic astrology values from astronomical data.
> **Reference:** `CALCULATIONS.md` Sections 5–9

---

## Task 2.1 — constants/nakshatra.py

27 nakshatras with lord, Hindi name, index.

```python
NAKSHATRA_LIST = [
    {"index": 0,  "name_en": "Ashwini",     "name_hi": "अश्विनी",   "lord": "ketu"},
    {"index": 1,  "name_en": "Bharani",     "name_hi": "भरणी",      "lord": "venus"},
    # ... all 27
]
```

**Test:** `assert len(NAKSHATRA_LIST) == 27`

---

## Task 2.2 — astrology/nakshatra.py

```python
def get_nakshatra(longitude: float) -> dict:
    """
    Moon (or any planet) longitude → Nakshatra
    Formula: index = floor(longitude / 13.333333)
    Pada = floor((longitude % 13.333333) / 3.333333) + 1
    Reference: CALCULATIONS.md Section 5
    """
```

**Tests:** Boundary cases — 0°, 13.33°, 26.66°, 359.99°

**Done when:**
- [ ] Returns nakshatra name, index, pada, lord
- [ ] Pada 1–4 only
- [ ] Boundary tests pass

---

## Task 2.3 — constants/tithi.py

30 tithi names (Shukla 1–15 + Krishna 1–15).

**Test:** `assert len(TITHI_LIST) == 30`

---

## Task 2.4 — astrology/tithi.py

```python
def get_tithi(sun_longitude: float, moon_longitude: float) -> dict:
    """
    angle = normalize(moon - sun)
    tithi = floor(angle / 12) + 1
    paksha: 1–15 = Shukla, 16–30 = Krishna
    Reference: CALCULATIONS.md Section 6
    """
```

**Done when:**
- [ ] Returns tithi number, name, paksha
- [ ] Purnima (15) and Amavasya (30) correct
- [ ] Boundary at 12° multiples tested

---

## Task 2.5 — constants/yoga.py

27 Panchang yogas.

**Test:** `assert len(YOGA_LIST) == 27`

---

## Task 2.6 — astrology/yoga.py

```python
def get_panchang_yoga(sun_longitude: float, moon_longitude: float) -> dict:
    """
    sum = normalize(sun + moon)
    yoga = floor(sum / 13.333333) + 1
    Reference: CALCULATIONS.md Section 7
    """
```

---

## Task 2.7 — constants/karana.py

Fixed 4 + Repeating 7 karanas. Traditional mapping table.

**Note:** Implement from verified source only — no guessing.

---

## Task 2.8 — astrology/karana.py

```python
def get_karana(sun_longitude: float, moon_longitude: float) -> dict:
    """
    angle = normalize(moon - sun)
    karana_index = floor(angle / 6)
    Reference: CALCULATIONS.md Section 8
    """
```

---

## Task 2.9 — astrology/vara.py

```python
def get_vara(local_date: str) -> dict:
    """
    Local date → Vedic weekday
    MVP: civil weekday from date
    Returns: vara name (Hi + En)
    Reference: CALCULATIONS.md Section 9
    """
```

**Test:** `get_vara("1985-04-20")` → "Shanivar" / "शनिवार"

---

# Phase 3 — Lagna and Houses

> **Reference:** `CALCULATIONS.md` Sections 12–13

---

## Task 3.1 — astrology/lagna.py

```python
def calculate_lagna(jd_ut: float, latitude: float, longitude: float, ayanamsa: float) -> dict:
    """
    Swiss Ephemeris houses_ex → ascendant tropical → sidereal
    Reference: CALCULATIONS.md Section 12
    """
```

**Test:** Known birth → expected Lagna rashi within 0.25°

---

## Task 3.2 — astrology/houses.py

```python
def whole_sign_houses(lagna_rashi_index: int) -> list[dict]:
    """
    House 1 = Lagna rashi
    House N = (lagna + N-1) % 12
    """

def get_planet_house(planet_rashi_index: int, lagna_rashi_index: int) -> int:
    """Returns 1–12"""
```

---

# Phase 4 — Panchang API MVP

---

## Task 4.1 — schemas/panchang.py

```python
from pydantic import BaseModel

class PanchangRequest(BaseModel):
    date: str          # "2026-06-01"
    latitude: float
    longitude: float
    timezone: float    # 5.5 for IST
    ayanamsa: str = "lahiri"
    language: str = "hi"

class PanchangResponse(BaseModel):
    date: str
    vara: dict
    tithi: dict
    nakshatra: dict
    yoga: dict
    karana: dict
    meta: dict
```

---

## Task 4.2 — astrology/panchang.py

```python
def calculate_daily_panchang(request: PanchangRequest) -> dict:
    """
    Combines: Julian Day → Planets → Tithi, Nakshatra, Yoga, Karana, Vara
    Returns complete Panchang dict
    """
```

---

## Task 4.3 — api/v1/panchang.py

```python
from fastapi import APIRouter
router = APIRouter()

@router.post("/panchang")
def get_panchang(request: PanchangRequest) -> PanchangResponse:
    ...
```

Register in `main.py`:
```python
app.include_router(router, prefix="/api/v1")
```

---

## Task 4.4 — Integration Test: Panchang API

```python
# tests/test_api_integration.py
from httpx import AsyncClient

async def test_panchang_jodhpur():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/api/v1/panchang", json={
            "date": "1985-04-20",
            "latitude": 26.2389,
            "longitude": 73.0243,
            "timezone": 5.5
        })
    assert response.status_code == 200
    data = response.json()
    assert "tithi" in data
    assert "nakshatra" in data
```

**Done when:**
- [ ] API returns 200
- [ ] Response has all Panchang fields
- [ ] Test passes

---

# Phase 5 — Kundali API MVP

---

## Task 5.1 — schemas/kundali.py

```python
class KundaliRequest(BaseModel):
    name: str
    date: str
    time: str          # "18:10"
    latitude: float
    longitude: float
    timezone: float
    ayanamsa: str = "lahiri"
    language: str = "hi"

class KundaliResponse(BaseModel):
    meta: dict
    birth_details: dict
    planets: list
    houses: list
    lagna: dict
    panchang: dict
```

---

## Task 5.2 — astrology/kundali.py

```python
def calculate_basic_kundali(request: KundaliRequest) -> dict:
    """
    Assembles: Julian → Ayanamsa → Planets → Lagna → Houses → Panchang
    Returns complete Kundali dict
    """
```

---

## Task 5.3 — api/v1/kundali.py

```http
POST /api/v1/kundali
```

---

## Task 5.4 — Golden Fixture: Jodhpur 1985

After verifying output with Jagannatha Hora:

```bash
# Save to:
backend/tests/fixtures/jodhpur_1985_04_20.json
```

Format:
```json
{
  "_meta": {
    "verified_with": "Jagannatha Hora",
    "verified_date": "2026-06-XX",
    "tolerance_deg": 0.05
  },
  "lagna": { "rashi": "Tula", "degree": 12.5 },
  "planets": [ ... ],
  "panchang": { ... }
}
```

**Done when:**
- [ ] API output matches Jagannatha Hora
- [ ] Fixture saved in `tests/fixtures/`

---

# Phase 6 — Boundary Times

> **Reference:** `CALCULATIONS.md` Sections 6–9 (end times)

---

## Task 6.1 — astronomy/search.py

```python
def find_next_boundary(
    func,           # function of JD → value
    jd_start: float,
    target_value: float,
    step_hours: float = 0.5,
    tolerance_minutes: float = 1.0
) -> float:
    """
    Binary search: find JD where func(jd) crosses target_value
    Returns JD of boundary
    """
```

**Test:** Simple linear function boundary test

---

## Task 6.2 — Tithi Start/End Time

Add to `tithi.py`:
```python
def get_tithi_with_times(jd_ut, lat, lon, ayanamsa) -> dict:
    """Returns tithi + start_time + end_time"""
```

**Tolerance:** Within 5 minutes of reference

---

## Task 6.3 — Nakshatra Start/End Time

Same pattern. **Tolerance:** 5 min.

---

## Task 6.4 — Yoga Start/End Time

Same pattern. **Tolerance:** 5 min.

---

## Task 6.5 — Karana Start/End Time

Same pattern. **Tolerance:** 5 min.

---

# Phase 7 — Sunrise, Sunset, Moonrise, Moonset

> **Reference:** `CALCULATIONS.md` Sections 10–11

---

## Task 7.1 — astronomy/rise_set.py

```python
def get_sunrise(jd_ut: float, latitude: float, longitude: float) -> str:
    """Returns "HH:MM" local time. Tolerance: 2 min."""

def get_sunset(jd_ut: float, latitude: float, longitude: float) -> str:
    """Returns "HH:MM" local time."""
```

**Test:** Jodhpur known sunrise date → within 2 min

---

## Task 7.2 — Moonrise / Moonset

```python
def get_moonrise(...) -> str | None:
    """Returns "HH:MM" or None if no moonrise on this date"""

def get_moonset(...) -> str | None:
    """Returns "HH:MM" or None"""
```

---

## Task 7.3 — Update Panchang API

Add to response:
```json
{
  "sunrise": "06:01",
  "sunset": "19:12",
  "moonrise": "21:45",
  "moonset": null
}
```

---

# Phase 8 — Vimshottari Dasha

> **Reference:** `CALCULATIONS.md` Section 14

---

## Task 8.1 — constants/dasha.py

```python
DASHA_SEQUENCE = ["ketu", "venus", "sun", "moon", "mars", "rahu", "jupiter", "saturn", "mercury"]
DASHA_YEARS = {"ketu": 7, "venus": 20, "sun": 6, "moon": 10, "mars": 7,
               "rahu": 18, "jupiter": 16, "saturn": 19, "mercury": 17}
# Total must be 120
assert sum(DASHA_YEARS.values()) == 120
```

---

## Task 8.2 — astrology/dasha.py: Birth Balance

```python
def calculate_birth_dasha_balance(moon_longitude: float) -> dict:
    """
    remaining_fraction = remaining_degrees_in_nakshatra / 13.333333
    balance_years = lord_total_years * remaining_fraction
    Reference: CALCULATIONS.md Section 14
    """
```

---

## Task 8.3 — Mahadasha Timeline

```python
def get_mahadasha_timeline(birth_date: str, moon_longitude: float) -> list[dict]:
    """
    Returns list of Mahadasha periods with start/end dates
    Range: birth-20 years to birth+80 years
    """
```

---

## Task 8.4 — Antardasha Timeline

```python
def get_antardasha_timeline(mahadasha: dict) -> list[dict]:
    """Antardasha periods within a Mahadasha"""

def get_current_dasha(birth_date: str, moon_longitude: float) -> dict:
    """Returns current Mahadasha + Antardasha + start/end dates"""
```

---

# Phase 9 — Varga Charts

> **Reference:** `CALCULATIONS.md` Section 15

---

## Task 9.1 — D9 Navamsha

```python
def calculate_d9(planet_longitude: float) -> dict:
    """
    Navamsha position
    Each Navamsha = 3°20' = 3.333°
    Formula: verified from trusted table only
    """
```

**Test with known values from Jagannatha Hora**

---

## Task 9.2 — D10 Dashamsha

```python
def calculate_d10(planet_longitude: float) -> dict:
    """Dashamsha. Formula from verified table."""
```

---

## Task 9.3 — Varga API

```http
POST /api/v1/varga
```

Response includes D1, D9, D10 for all planets.

---

# Phase 10 — Yoga & Dosha Detection (MVP)

> **Reference:** `CALCULATIONS.md` Section 19, `FEATURES.md` Phase 6

---

## Task 10.1 — rules/yoga_rules.py

Each rule must follow this schema:

```python
YOGA_RULES = [
    {
        "rule_id": "budhaditya_001",
        "name_en": "Budhaditya Yoga",
        "name_hi": "बुधादित्य योग",
        "description_hi": "सूर्य और बुध एक ही घर में",
        "detect": lambda planets, houses: ...,  # returns bool
        "cancellation": "...",
        "confidence": "high",
        "interpretation_template_id": "yoga_budhaditya_v1",
    },
]
```

**MVP Yogas:** Budhaditya, Gajakesari, Chandra Mangal, Panch Mahapurusha (5)

---

## Task 10.2 — rules/dosha_rules.py

Same schema pattern.

**MVP Doshas:** Manglik, Grahan, Guru Chandal, Shrapit, Kaal Sarp (basic)

---

## Task 10.3 — Kundali API Update

Add `yogas` and `doshas` lists to `/api/v1/kundali` response.

---

# Phase 11 — Report MVP

---

## Task 11.1 — Basic Hindi HTML Template

File: `backend/app/reports/templates/basic_kundali.html`

Include:
- Janaм विवरण
- ग्रह स्थिति table
- पंचांग
- दशा

**Test:** Template renders without error with sample data.

---

## Task 11.2 — Report API Endpoint

```http
POST /api/v1/report/basic-kundali
```

Returns: `text/html` response

---

## Task 11.3 — PDF Export

```python
from weasyprint import HTML

def html_to_pdf(html_content: str, output_path: str) -> None:
    HTML(string=html_content).write_pdf(output_path)
```

```http
POST /api/v1/report/basic-kundali?format=pdf
```

**Done when:**
- [ ] PDF file generates without error
- [ ] File opens correctly

---

# Phase 12 — Web UI MVP

---

## Task 12.1 — Kundali Input Form

Page: `/kundali`

Fields:
- Name
- Date (date picker)
- Time
- City (with lat/lon auto-fill)
- Timezone

---

## Task 12.2 — Kundali Result Page

Page: `/kundali/result`

Show:
- Birth details
- Planet positions table
- Panchang
- Basic Dasha

---

## Task 12.3 — Panchang Page

Page: `/panchang`

Show:
- Today's Panchang for user's city
- Tithi, Nakshatra, Yoga, Karana, Vara
- Sunrise/Sunset times

---

# Phase 13 — Backlog (Post-MVP)

> Start only after Phase 0–12 complete and stable.

```
Priority 1 (Next Sprint):
  - Monthly Panchang
  - Festival flags (Ekadashi, Purnima, Amavasya)
  - Shubhata score
  - Rahu Kalam + Gulika Kalam

Priority 2:
  - Muhurat finder
  - Kundali Milan (Matchmaking)
  - Shadbala (Strength)
  - Ashtakavarga

Priority 3:
  - Transit / Gochar
  - Sade Sati detection
  - Detailed PDF report
  - DOCX report

Priority 4:
  - D2, D3, D4, D7... Varga charts
  - Advanced Yoga detection (all 20+)
  - Prediction modules

Priority 5:
  - BhaktiRas integration
  - AI explanation layer (Phase 20)
  - WordPress plugin API
  - Next.js frontend
```

---

# Final MVP Definition

**MVP = Phase 0 through Phase 12 complete**

```
✓ Local FastAPI server runs
✓ GET /api/v1/health → ok
✓ POST /api/v1/panchang → correct Panchang
✓ POST /api/v1/kundali → correct Kundali
✓ POST /api/v1/dasha → correct Dasha
✓ POST /api/v1/varga → D1, D9, D10
✓ POST /api/v1/report/basic-kundali → HTML + PDF
✓ Basic Web UI works
✓ No paid API used
✓ Jodhpur golden fixture verified
✓ All Phase 1–3 tests passing
✓ Coverage ≥ 85%
```