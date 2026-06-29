# CALCULATIONS.md — Vedic Astrology Engine: Calculation Reference

> **Version:** 2.0
> **Purpose:** हर calculation का mathematical आधार, input/output, formula, Swiss Ephemeris usage, और validation method।
> **Rule:** Codex/Cursor इसी document को follow करे। Formula verify नहीं हुआ = placeholder + TODO।
> **Cross-reference:** `FEATURES.md`, `PROJECT_PHASES.md`

---

## 0. Global Calculation Rules

| Rule | Detail |
|---|---|
| Engine | सभी calculations Swiss Ephemeris / `pyswisseph` से |
| Ayanamsa | Default: Lahiri / Chitrapaksha |
| Longitude range | हमेशा 0°–360° normalized |
| Timezone | हमेशा explicit input — assume नहीं |
| UTC conversion | हर calculation से पहले होगा |
| AI layer | कोई calculation नहीं करेगा |
| Do Not Guess | Formula verify नहीं = placeholder + TODO + `@pytest.mark.skip` |

---

## 1. Common Helper Functions

### 1.1 Normalize Degrees

```python
def normalize_deg(value: float) -> float:
    """0–360 ke beech normalize karo"""
    return value % 360.0
```

**Tests:**
```python
assert normalize_deg(370.5) == 10.5
assert normalize_deg(-10.0) == 350.0
assert normalize_deg(0.0) == 0.0
assert normalize_deg(360.0) == 0.0
```

### 1.2 Degree to Rashi

```python
def deg_to_rashi(longitude: float) -> tuple[int, float]:
    """
    Returns: (rashi_index 0-11, degree_within_rashi 0-30)
    """
    rashi_index = int(longitude // 30)
    degree_in_rashi = longitude % 30.0
    return rashi_index, degree_in_rashi
```

**Rashi Index Mapping:**
```
0=Mesha  1=Vrishabha  2=Mithuna  3=Karka   4=Simha    5=Kanya
6=Tula   7=Vrishchika 8=Dhanu    9=Makara  10=Kumbha  11=Meena
```

### 1.3 Degree to DMS

```python
def deg_to_dms(value: float) -> dict:
    """Decimal degrees → degrees/minutes/seconds dict"""
    d = int(value)
    m = int((value - d) * 60)
    s = round(((value - d) * 60 - m) * 60, 1)
    return {"degrees": d, "minutes": m, "seconds": s}
```

**Test:**
```python
assert deg_to_dms(6.73) == {"degrees": 6, "minutes": 43, "seconds": 48.0}
assert deg_to_dms(0.0) == {"degrees": 0, "minutes": 0, "seconds": 0.0}
```

### 1.4 Local Datetime to UTC

```python
def local_datetime_to_utc(date: str, time: str, timezone: float) -> tuple:
    """
    Input:  "1985-04-20", "18:10", 5.5
    Output: (year, month, day, hour_utc_float)
    hour_utc_float = hour + minute/60 - timezone
    """
```

**Edge Cases:**
- Birth at 00:30 IST → previous UTC day
- DST locations (use `timezonefinder` for auto-detect)
- timezone = 5.5 (IST) = +5 hours 30 minutes

---

## 2. Julian Day

### Formula

```python
import swisseph as swe

def calculate_julian_day(date: str, time: str, timezone: float) -> float:
    """
    1. Local → UTC
    2. swe.julday(year, month, day, hour_utc)
    3. Return Julian Day UT
    """
    year, month, day, hour_utc = local_datetime_to_utc(date, time, timezone)
    jd_ut = swe.julday(year, month, day, hour_utc)
    return jd_ut
```

### Known Test Values

```python
# Jodhpur, 20 Apr 1985, 18:10 IST
jd = calculate_julian_day("1985-04-20", "18:10", 5.5)
assert abs(jd - 2446176.027777) < 0.001

# Delhi, 1 Jan 2000, 12:00 IST
jd2 = calculate_julian_day("2000-01-01", "12:00", 5.5)
assert abs(jd2 - 2451545.270833) < 0.001
```

### Output

```json
{ "julian_day_ut": 2446176.027777 }
```

### Edge Cases to Test

- [ ] Birth at midnight (00:00)
- [ ] Birth at exactly noon
- [ ] DST location (London, New York)
- [ ] Timezone crossing date boundary (00:30 IST = previous day 19:00 UTC)

---

## 3. Ayanamsa

### Swiss Ephemeris Setup

```python
import swisseph as swe

def get_ayanamsa(jd_ut: float, mode: str = "lahiri") -> float:
    """
    Supported modes: lahiri, raman, kp
    Returns: ayanamsa value in degrees (float)
    """
    if mode == "lahiri":
        swe.set_sid_mode(swe.SIDM_LAHIRI)
    elif mode == "raman":
        swe.set_sid_mode(swe.SIDM_RAMAN)
    elif mode == "kp":
        swe.set_sid_mode(swe.SIDM_KRISHNAMURTI)
    else:
        raise ValueError(f"Unknown ayanamsa mode: {mode}")

    return swe.get_ayanamsa_ut(jd_ut)
```

### Expected Range

| Year | Lahiri Ayanamsa (approx) |
|---|---|
| 1900 | ~22.5° |
| 1950 | ~23.2° |
| 1985 | ~23.7° |
| 2000 | ~23.9° |
| 2026 | ~24.3° |

### Output

```json
{
  "ayanamsa_name": "lahiri",
  "ayanamsa_value": 23.72
}
```

### Test

```python
jd = calculate_julian_day("1985-04-20", "18:10", 5.5)
ayanamsa = get_ayanamsa(jd, "lahiri")
assert 23.0 < ayanamsa < 24.5  # Expected range for 1985
```

---

## 4. Planetary Positions

### Planets and Swiss Ephemeris IDs

```python
import swisseph as swe

PLANET_SWE_IDS = {
    "sun":     swe.SUN,       # 0
    "moon":    swe.MOON,      # 1
    "mars":    swe.MARS,      # 4
    "mercury": swe.MERCURY,   # 2
    "jupiter": swe.JUPITER,   # 5
    "venus":   swe.VENUS,     # 3
    "saturn":  swe.SATURN,    # 6
    "rahu":    swe.MEAN_NODE, # 10 (Mean Node = Rahu)
    # Ketu: calculated as Rahu + 180°
}
```

### Calculation

```python
def get_planet_positions(jd_ut: float, ayanamsa: float) -> list[dict]:
    flags = swe.FLG_SWIEPH | swe.FLG_SPEED

    results = []
    for planet_name, swe_id in PLANET_SWE_IDS.items():
        data, _ = swe.calc_ut(jd_ut, swe_id, flags)
        tropical_lon = data[0]
        speed = data[3]

        sidereal_lon = normalize_deg(tropical_lon - ayanamsa)
        rashi_index, degree_in_rashi = deg_to_rashi(sidereal_lon)
        retrograde = speed < 0

        results.append({
            "planet": planet_name,
            "tropical_longitude": round(tropical_lon, 6),
            "sidereal_longitude": round(sidereal_lon, 6),
            "rashi_index": rashi_index,
            "degree_in_rashi": round(degree_in_rashi, 4),
            "dms": deg_to_dms(degree_in_rashi),
            "speed": round(speed, 6),
            "retrograde": retrograde,
        })

    # Ketu = Rahu + 180°
    rahu = next(p for p in results if p["planet"] == "rahu")
    ketu_lon = normalize_deg(rahu["sidereal_longitude"] + 180.0)
    ketu_rashi, ketu_deg = deg_to_rashi(ketu_lon)
    results.append({
        "planet": "ketu",
        "sidereal_longitude": round(ketu_lon, 6),
        "rashi_index": ketu_rashi,
        "degree_in_rashi": round(ketu_deg, 4),
        "dms": deg_to_dms(ketu_deg),
        "retrograde": True,  # Ketu is always considered retrograde
    })

    return results
```

### Output per Planet

```json
{
  "planet": "sun",
  "tropical_longitude": 30.45,
  "sidereal_longitude": 6.73,
  "rashi_index": 0,
  "degree_in_rashi": 6.73,
  "dms": {"degrees": 6, "minutes": 43, "seconds": 48.0},
  "speed": 0.983,
  "retrograde": false
}
```

### Retrograde Rule

```
retrograde = True  if speed < 0
retrograde = False if speed >= 0
Note: Sun and Moon are NEVER retrograde.
Note: Rahu/Ketu are always retrograde (mean node moves backward).
```

### Tolerance

| Comparison | Tolerance |
|---|---:|
| Planet longitude vs Jagannatha Hora | 0.05° MVP |
| Planet longitude vs Jagannatha Hora | 0.01° Stable |

---

## 5. Nakshatra and Pada

### Formula

```
Each Nakshatra span = 360° / 27 = 13°20' = 13.333333°
Each Pada span     = 13.333333° / 4 = 3°20' = 3.333333°

Nakshatra Index = floor(longitude / 13.333333)   → 0–26
Pada            = floor((longitude % 13.333333) / 3.333333) + 1  → 1–4
```

### Implementation

```python
NAKSHATRA_SPAN = 360.0 / 27   # 13.333333...
PADA_SPAN = NAKSHATRA_SPAN / 4 # 3.333333...

def get_nakshatra(longitude: float) -> dict:
    """Input: Moon longitude (or any planet longitude)"""
    lon = normalize_deg(longitude)
    index = int(lon // NAKSHATRA_SPAN)
    remainder = lon % NAKSHATRA_SPAN
    pada = int(remainder // PADA_SPAN) + 1

    nakshatra = NAKSHATRA_LIST[index]
    return {
        "nakshatra": nakshatra["name_en"],
        "nakshatra_hi": nakshatra["name_hi"],
        "index": index,
        "pada": pada,
        "lord": nakshatra["lord"],
    }
```

### 27 Nakshatras with Lords

```
Index | Name        | Lord
------+-------------+-------
0     | Ashwini     | Ketu
1     | Bharani     | Venus
2     | Krittika    | Sun
3     | Rohini      | Moon
4     | Mrigashira  | Mars
5     | Ardra       | Rahu
6     | Punarvasu   | Jupiter
7     | Pushya      | Saturn
8     | Ashlesha    | Mercury
9     | Magha       | Ketu
10    | Purva Phalguni | Venus
11    | Uttara Phalguni | Sun
12    | Hasta       | Moon
13    | Chitra      | Mars
14    | Swati       | Rahu
15    | Vishakha    | Jupiter
16    | Anuradha    | Saturn
17    | Jyeshtha    | Mercury
18    | Moola       | Ketu
19    | Purva Ashadha | Venus
20    | Uttara Ashadha | Sun
21    | Shravana    | Moon
22    | Dhanishtha  | Mars
23    | Shatabhisha | Rahu
24    | Purva Bhadrapada | Jupiter
25    | Uttara Bhadrapada | Saturn
26    | Revati      | Mercury
```

### Boundary Tests

```python
assert get_nakshatra(0.0)["index"] == 0       # Ashwini start
assert get_nakshatra(13.333)["index"] == 0    # Still Ashwini
assert get_nakshatra(13.334)["index"] == 1    # Bharani starts
assert get_nakshatra(359.99)["index"] == 26   # Revati
```

### Output

```json
{
  "nakshatra": "Ashwini",
  "nakshatra_hi": "अश्विनी",
  "index": 0,
  "pada": 1,
  "lord": "ketu"
}
```

---

## 6. Tithi

### Formula

```
angle = normalize(Moon_longitude - Sun_longitude)
tithi_number = floor(angle / 12) + 1    → 1–30
```

### Paksha

```
tithi 1–15  = Shukla Paksha (शुक्ल पक्ष)
tithi 16–30 = Krishna Paksha (कृष्ण पक्ष)
tithi 15    = Purnima (पूर्णिमा)
tithi 30    = Amavasya (अमावस्या)
```

### Implementation

```python
TITHI_SPAN = 12.0  # degrees per tithi

def get_tithi(sun_longitude: float, moon_longitude: float) -> dict:
    angle = normalize_deg(moon_longitude - sun_longitude)
    tithi_number = int(angle // TITHI_SPAN) + 1
    paksha = "shukla" if tithi_number <= 15 else "krishna"

    return {
        "tithi_number": tithi_number,
        "tithi_name": TITHI_LIST[tithi_number - 1]["name_en"],
        "tithi_name_hi": TITHI_LIST[tithi_number - 1]["name_hi"],
        "paksha": paksha,
        "angle": round(angle, 4),
    }
```

### 30 Tithi Names

```
Shukla Paksha:
1=Pratipada  2=Dwitiya   3=Tritiya    4=Chaturthi  5=Panchami
6=Shashthi   7=Saptami   8=Ashtami    9=Navami     10=Dashami
11=Ekadashi  12=Dwadashi 13=Trayodashi 14=Chaturdashi 15=Purnima

Krishna Paksha:
16=Pratipada 17=Dwitiya  18=Tritiya   19=Chaturthi  20=Panchami
21=Shashthi  22=Saptami  23=Ashtami   24=Navami     25=Dashami
26=Ekadashi  27=Dwadashi 28=Trayodashi 29=Chaturdashi 30=Amavasya
```

### Boundary Time

```
Tithi boundary = every 12° multiple of (Moon - Sun) angle
Use binary search (astronomy/search.py) to find exact JD
Tolerance: 5 min MVP → 2 min stable
```

### Output

```json
{
  "tithi_number": 2,
  "tithi_name": "Dwitiya",
  "tithi_name_hi": "द्वितीया",
  "paksha": "shukla",
  "angle": 14.5,
  "end_time": "21:34"
}
```

---

## 7. Panchang Yoga

### Formula

```
sum = normalize(Sun_longitude + Moon_longitude)
yoga_number = floor(sum / 13.333333) + 1    → 1–27
```

### 27 Yoga Names

```
1=Vishkamba  2=Priti      3=Ayushman   4=Saubhagya  5=Shobhan
6=Atiganda   7=Sukarman   8=Dhriti     9=Shoola    10=Ganda
11=Vriddhi  12=Dhruva    13=Vyaghata  14=Harshana  15=Vajra
16=Siddhi   17=Vyatipata 18=Variyan   19=Parigha   20=Shiva
21=Siddha   22=Sadhya    23=Shubha    24=Shukla    25=Brahma
26=Indra    27=Vaidhriti
```

Note: Vishkamba, Atiganda, Shoola, Ganda, Vyaghata, Vajra, Vyatipata, Parigha, Vaidhriti are inauspicious.

### Output

```json
{
  "yoga_number": 5,
  "yoga_name": "Shobhan",
  "yoga_name_hi": "शोभन",
  "auspicious": true,
  "end_time": "14:22"
}
```

---

## 8. Karana

### Formula

```
angle = normalize(Moon_longitude - Sun_longitude)
karana_sequence_index = floor(angle / 6)    → 0–59
```

### Karana Mapping

```
Total half-tithis in lunar month = 60

Special fixed karanas (appear once each at specific positions):
Position 0:  Kimstughna (fixed)
Position 57: Shakuni (fixed)
Position 58: Chatushpada (fixed)
Position 59: Naga (fixed)

Repeating cycle (positions 1–56, 8 per cycle × 7 cycles):
Bava, Balava, Kaulava, Taitila, Gara, Vanija, Vishti (×8)
```

> ⚠️ **Karana sequence needs traditional table verification before implementation.**
> Use only verified printed Panchang source. Mark as TODO until verified.

### Output

```json
{
  "karana_name": "Bava",
  "karana_name_hi": "बव",
  "type": "repeating",
  "auspicious": true,
  "end_time": "09:45"
}
```

---

## 9. Vara (Weekday)

### MVP Formula

```python
import datetime

VARA_NAMES = {
    0: {"en": "Somavar",   "hi": "सोमवार",   "lord": "moon"},    # Monday
    1: {"en": "Mangalvar", "hi": "मंगलवार",  "lord": "mars"},
    2: {"en": "Budhavar",  "hi": "बुधवार",   "lord": "mercury"},
    3: {"en": "Guruvar",   "hi": "गुरुवार",  "lord": "jupiter"},
    4: {"en": "Shukravar", "hi": "शुक्रवार", "lord": "venus"},
    5: {"en": "Shanivar",  "hi": "शनिवार",   "lord": "saturn"},
    6: {"en": "Ravivar",   "hi": "रविवार",   "lord": "sun"},     # Sunday
}

def get_vara(local_date: str) -> dict:
    """MVP: civil weekday. Future: Vedic day from sunrise."""
    d = datetime.date.fromisoformat(local_date)
    return VARA_NAMES[d.weekday()]
```

**Test:** `get_vara("1985-04-20")` → Shanivar (Saturday) ✓

**Future:** Vedic Vara = from sunrise to next sunrise (different from civil day after midnight)

---

## 10. Sunrise and Sunset

### Swiss Ephemeris Method

```python
import swisseph as swe

def get_sunrise(jd_ut: float, latitude: float, longitude: float, timezone: float) -> str:
    """
    Returns sunrise time as "HH:MM" local time
    """
    rsmi = swe.CALC_RISE | swe.BIT_DISC_CENTER
    result = swe.rise_trans(
        jd_ut - 0.5,       # search from half-day before
        swe.SUN,
        longitude, latitude,
        rsmi=rsmi
    )
    jd_rise = result[1][0]
    # Convert JD to local time string
    return jd_to_local_time(jd_rise, timezone)

def get_sunset(jd_ut: float, latitude: float, longitude: float, timezone: float) -> str:
    rsmi = swe.CALC_SET | swe.BIT_DISC_CENTER
    result = swe.rise_trans(
        jd_ut - 0.5,
        swe.SUN,
        longitude, latitude,
        rsmi=rsmi
    )
    jd_set = result[1][0]
    return jd_to_local_time(jd_set, timezone)
```

### Accuracy Target

| Phase | Tolerance |
|---|---|
| MVP | ± 2 minutes |
| Stable | ± 1 minute |

### Validation Source

Compare with: Drik Panchang, Time and Date website

### Output

```json
{
  "sunrise": "06:01",
  "sunset": "19:12"
}
```

---

## 11. Moonrise and Moonset

### Same method as Sunrise — use Moon ID

```python
def get_moonrise(jd_ut: float, latitude: float, longitude: float, timezone: float) -> str | None:
    """Returns "HH:MM" or None if no moonrise on this date"""

def get_moonset(jd_ut: float, latitude: float, longitude: float, timezone: float) -> str | None:
    """Returns "HH:MM" or None"""
```

### Edge Cases

- Moonrise may not occur on some dates (polar regions, some lunar phases)
- Moonset may fall next day
- Return `None` with reason string if no event

```json
{
  "moonrise": "21:45",
  "moonset": null,
  "moonset_note": "Sets after midnight"
}
```

---

## 12. Lagna / Ascendant

### Swiss Ephemeris

```python
def calculate_lagna(jd_ut: float, latitude: float, longitude: float, ayanamsa: float) -> dict:
    """
    Swiss Ephemeris houses_ex → tropical ascendant → sidereal
    House system: 'P' = Placidus (for swe.houses_ex)
    But for Vedic interpretation: use Whole Sign houses separately
    """
    cusps, ascmc = swe.houses_ex(
        jd_ut, latitude, longitude,
        b'P',              # House system (doesn't affect Lagna)
        swe.FLG_SIDEREAL   # Sidereal mode
    )
    ascendant_sidereal = normalize_deg(ascmc[0])
    rashi_index, degree_in_rashi = deg_to_rashi(ascendant_sidereal)

    return {
        "ascendant_longitude": round(ascendant_sidereal, 4),
        "rashi_index": rashi_index,
        "rashi_name_en": RASHI_LIST[rashi_index]["name_en"],
        "rashi_name_hi": RASHI_LIST[rashi_index]["name_hi"],
        "degree_in_rashi": round(degree_in_rashi, 4),
        "dms": deg_to_dms(degree_in_rashi),
    }
```

### Important Notes

- Lagna changes approximately every 2 hours
- At exact degree boundaries, be careful of rounding
- Test with known birth data from Jagannatha Hora

### Tolerance

| Phase | Tolerance |
|---|---|
| MVP | ± 0.25° |
| Stable | ± 0.1° |

---

## 13. Houses (Bhava)

### Whole Sign House Method (Vedic Standard)

```python
def whole_sign_houses(lagna_rashi_index: int) -> list[dict]:
    """
    House 1 = Lagna rashi
    House N = (lagna_rashi_index + N - 1) % 12
    Returns list of 12 houses with rashi assignments
    """
    houses = []
    for i in range(12):
        rashi_idx = (lagna_rashi_index + i) % 12
        houses.append({
            "house": i + 1,
            "rashi_index": rashi_idx,
            "rashi_name_en": RASHI_LIST[rashi_idx]["name_en"],
            "rashi_name_hi": RASHI_LIST[rashi_idx]["name_hi"],
        })
    return houses

def get_planet_house(planet_rashi_index: int, lagna_rashi_index: int) -> int:
    """Returns house number 1–12"""
    return ((planet_rashi_index - lagna_rashi_index) % 12) + 1
```

### Example (Tula Lagna)

```
Lagna = Tula (6)
House 1 = Tula    House 2 = Vrishchika  House 3 = Dhanu
House 4 = Makara  House 5 = Kumbha      House 6 = Meena
House 7 = Mesha   House 8 = Vrishabha   House 9 = Mithuna
House 10 = Karka  House 11 = Simha      House 12 = Kanya
```

---

## 14. Vimshottari Dasha

### Basis

Birth Moon Nakshatra determines starting Dasha.

### Nakshatra Lord Sequence (Dasha Order)

```python
DASHA_SEQUENCE = [
    "ketu",    # 7 years
    "venus",   # 20 years
    "sun",     # 6 years
    "moon",    # 10 years
    "mars",    # 7 years
    "rahu",    # 18 years
    "jupiter", # 16 years
    "saturn",  # 19 years
    "mercury", # 17 years
]
# Total = 120 years

DASHA_YEARS = {
    "ketu": 7, "venus": 20, "sun": 6, "moon": 10, "mars": 7,
    "rahu": 18, "jupiter": 16, "saturn": 19, "mercury": 17
}
assert sum(DASHA_YEARS.values()) == 120
```

### Birth Dasha Balance

```python
def calculate_birth_dasha_balance(moon_longitude: float) -> dict:
    """
    1. Find birth nakshatra
    2. Find degrees remaining in birth nakshatra
    3. remaining_fraction = remaining_degrees / 13.333333
    4. balance_years = dasha_lord_years * remaining_fraction
    """
    nak = get_nakshatra(moon_longitude)
    degrees_in_nakshatra = moon_longitude % NAKSHATRA_SPAN
    remaining_degrees = NAKSHATRA_SPAN - degrees_in_nakshatra
    remaining_fraction = remaining_degrees / NAKSHATRA_SPAN

    lord = nak["lord"]
    balance_years = DASHA_YEARS[lord] * remaining_fraction

    return {
        "birth_nakshatra": nak["nakshatra"],
        "birth_nakshatra_lord": lord,
        "dasha_balance_years": round(balance_years, 4),
    }
```

### Mahadasha Timeline

```python
from datetime import date, timedelta

def get_mahadasha_timeline(birth_date: str, moon_longitude: float) -> list[dict]:
    """
    Starting from birth, generate all Mahadasha periods
    """
    balance = calculate_birth_dasha_balance(moon_longitude)
    lord = balance["birth_nakshatra_lord"]
    balance_years = balance["dasha_balance_years"]

    # Find starting position in DASHA_SEQUENCE
    start_idx = DASHA_SEQUENCE.index(lord)

    timeline = []
    current_date = date.fromisoformat(birth_date)

    # First dasha: only the remaining balance years
    end_date = add_years(current_date, balance_years)
    timeline.append({
        "lord": lord,
        "start": str(current_date),
        "end": str(end_date),
        "years": round(balance_years, 4),
    })
    current_date = end_date

    # Remaining dashas in full cycles
    for i in range(1, 9 * 3):  # Enough for 3 full cycles
        next_idx = (start_idx + i) % 9
        next_lord = DASHA_SEQUENCE[next_idx]
        years = DASHA_YEARS[next_lord]
        end_date = add_years(current_date, years)
        timeline.append({
            "lord": next_lord,
            "start": str(current_date),
            "end": str(end_date),
            "years": years,
        })
        current_date = end_date

    return timeline
```

---

## 15. Divisional Charts / Varga

### General Rule

```
⚠️ Every varga formula must be verified from a trusted printed source.
   Do NOT implement from guesswork.
   If formula uncertain: placeholder + TODO + pytest.mark.skip
```

### Priority Order

D1 → D9 → D10 → D2 → D3 → D4 → D7 → D12 → others

### D9 Navamsha Formula

```
Each Navamsha = 3°20' = 3.333°
Navamsha index within sign = floor(degree_in_rashi / 3.333333)

Starting rashi by element:
- Fire signs (Mesha, Simha, Dhanu): start from Mesha (0)
- Earth signs (Vrishabha, Kanya, Makara): start from Makara (9)
- Air signs (Mithuna, Tula, Kumbha): start from Tula (6)
- Water signs (Karka, Vrishchika, Meena): start from Karka (3)

D9 rashi = (starting_rashi + navamsha_index) % 12
```

> ⚠️ Verify D9 formula output against Jagannatha Hora for at least 5 known charts before marking complete.

### D10 Dashamsha Formula

```
Each Dashamsha = 3°
Dashamsha index = floor(degree_in_rashi / 3)

Starting point:
- Odd signs: start from same sign (Mesha for Mesha, etc.)
- Even signs: start from 9th sign from it

D10 rashi = (starting_rashi + dashamsha_index) % 12
```

> ⚠️ Verify D10 formula — traditions differ. Mark TODO until verified with reference.

---

## 16. Planet Dignity

### Data Required (store in constants/dignity.py)

```python
EXALTATION = {
    "sun":     {"sign": 0, "degree": 10},   # Mesha 10°
    "moon":    {"sign": 1, "degree": 3},    # Vrishabha 3°
    "mars":    {"sign": 9, "degree": 28},   # Makara 28°
    "mercury": {"sign": 5, "degree": 15},   # Kanya 15°
    "jupiter": {"sign": 3, "degree": 5},    # Karka 5°
    "venus":   {"sign": 11, "degree": 27},  # Meena 27°
    "saturn":  {"sign": 6, "degree": 20},   # Tula 20°
    "rahu":    {"sign": 1, "degree": 20},   # Vrishabha 20° (tradition varies)
    "ketu":    {"sign": 7, "degree": 20},   # Vrishchika 20° (tradition varies)
}

DEBILITATION = {
    "sun":     {"sign": 6},    # Tula
    "moon":    {"sign": 7},    # Vrishchika
    "mars":    {"sign": 3},    # Karka
    "mercury": {"sign": 11},   # Meena
    "jupiter": {"sign": 9},    # Makara
    "venus":   {"sign": 5},    # Kanya
    "saturn":  {"sign": 0},    # Mesha
    "rahu":    {"sign": 7},    # Vrishchika (tradition varies)
    "ketu":    {"sign": 1},    # Vrishabha (tradition varies)
}

OWN_SIGNS = {
    "sun":     [4],         # Simha
    "moon":    [3],         # Karka
    "mars":    [0, 7],      # Mesha, Vrishchika
    "mercury": [2, 5],      # Mithuna, Kanya
    "jupiter": [8, 11],     # Dhanu, Meena
    "venus":   [1, 6],      # Vrishabha, Tula
    "saturn":  [9, 10],     # Makara, Kumbha
}

MOOLTRIKONA = {
    "sun":     {"sign": 4,  "from_deg": 0,  "to_deg": 20},  # Simha 0-20°
    "moon":    {"sign": 1,  "from_deg": 4,  "to_deg": 30},  # Vrishabha 4-30°
    "mars":    {"sign": 0,  "from_deg": 0,  "to_deg": 12},  # Mesha 0-12°
    "mercury": {"sign": 2,  "from_deg": 16, "to_deg": 20},  # Mithuna 16-20°
    "jupiter": {"sign": 8,  "from_deg": 0,  "to_deg": 10},  # Dhanu 0-10°
    "venus":   {"sign": 6,  "from_deg": 0,  "to_deg": 15},  # Tula 0-15°
    "saturn":  {"sign": 10, "from_deg": 0,  "to_deg": 20},  # Kumbha 0-20°
}
```

### Dignity Detection Priority

```
Exalted → Mooltrikona → Own Sign → Friendly → Neutral → Enemy → Debilitated
```

### Output

```json
{
  "planet": "sun",
  "dignity": "exalted",
  "dignity_hi": "उच्च",
  "strength_hint": "strong"
}
```

---

## 17. Combustion (Asta)

### Definition

Planet is combust when within orb of Sun (too close to Sun).

### Orbs (to be verified from authoritative source)

```python
# ⚠️ These orbs need verification before use
COMBUSTION_ORBS = {
    "moon":    12.0,   # degrees
    "mars":    17.0,
    "mercury": 14.0,   # 12° if retrograde
    "jupiter": 11.0,
    "venus":   10.0,   # 8° if retrograde
    "saturn":  15.0,
}
# Note: Rahu/Ketu do not get combust
# Note: Orbs vary by tradition — mark source used
```

> ⚠️ Add source reference when implementing. Mark TODO until verified.

---

## 18. Aspects / Drishti

### Parashari Aspects

```python
PLANET_ASPECTS = {
    # All planets aspect 7th house from their position
    "default": [7],
    # Special aspects:
    "mars":    [7, 4, 8],    # 4th and 8th additionally
    "jupiter": [7, 5, 9],    # 5th and 9th additionally
    "saturn":  [7, 3, 10],   # 3rd and 10th additionally
    "rahu":    [7, 5, 9],    # Tradition varies — configurable
    "ketu":    [7, 5, 9],    # Tradition varies — configurable
}
```

### Aspect Detection

```python
def get_planet_aspects(planet_house: int) -> list[int]:
    """Returns list of house numbers aspected by planet in given house"""
    # house numbers are 1-12
```

---

## 19. Yoga and Dosha Rules

### Rule Schema (Mandatory)

Every rule in `rules/yoga_rules.py` and `rules/dosha_rules.py` must follow:

```python
{
    "rule_id": "budhaditya_001",          # Unique ID
    "name_en": "Budhaditya Yoga",
    "name_hi": "बुधादित्य योग",
    "name_sa": "Budhāditya Yoga",
    "description_hi": "सूर्य और बुध एक ही भाव में",
    "detect": callable,                    # func(planets, houses) → bool
    "cancellation_conditions": [],         # list of cancellation rules
    "confidence": "high",                  # high / medium / low
    "interpretation_template_id": "...",   # points to interpretation/yogas.py
    "source_reference": "Brihat Parashara Hora Shastra Ch. XX",
}
```

### MVP Yoga Formulas

```python
# Budhaditya Yoga
def detect_budhaditya(planets, houses):
    """Sun and Mercury in same house"""
    sun_house = get_house(planets, "sun")
    mercury_house = get_house(planets, "mercury")
    return sun_house == mercury_house

# Gajakesari Yoga
def detect_gajakesari(planets, houses):
    """Jupiter in kendra (1,4,7,10) from Moon"""
    moon_house = get_house(planets, "moon")
    jupiter_house = get_house(planets, "jupiter")
    diff = (jupiter_house - moon_house) % 12
    return diff in [0, 3, 6, 9]  # Same or kendra

# Manglik Dosha
def detect_manglik(planets, houses):
    """Mars in 1, 2, 4, 7, 8, 12 from Lagna"""
    mars_house = get_house(planets, "mars")
    return mars_house in [1, 2, 4, 7, 8, 12]
```

---

## 20. Rahu Kalam, Gulika Kalam, Yamaganda

### Rahu Kalam (Day-wise)

```python
# Rahu Kalam position by weekday (1=Monday...7=Sunday)
# Divide day (sunrise to sunset) into 8 equal parts
# Rahu Kalam = specific part by day

RAHU_KALAM_SEGMENT = {
    "ravivar":  8,   # 8th segment (last)
    "somavar":  2,   # 2nd segment
    "mangalvar": 7,
    "budhavar": 5,
    "guruvar":  6,
    "shukravar": 4,
    "shanivar": 3,
}
# Each segment = (sunset_time - sunrise_time) / 8
```

> ⚠️ Verify segment order from multiple printed Panchang sources before implementation.

---

## 21. Validation Strategy

### Per Calculation

| Step | Action |
|---|---|
| 1 | Unit test with known input → expected output |
| 2 | Compare with Jagannatha Hora (free software) |
| 3 | Compare with Astro-Seek or Drik Panchang |
| 4 | Add to golden fixture JSON |
| 5 | Set tolerance threshold |

### Golden Fixtures Required

| Location | Date | Time | TZ | Purpose |
|---|---|---|---|---|
| Jodhpur | 20 Apr 1985 | 18:10 | +5.5 | Primary (Sandeep) |
| Delhi | 1 Jan 2000 | 12:00 | +5.5 | Standard IST |
| Mumbai | 15 Jun 1990 | 06:30 | +5.5 | Morning birth |
| London | 26 Mar 1995 | 02:00 | BST | DST start |
| New York | 1 Nov 2000 | 01:30 | EST | DST end |

### Tolerance Standards

| Calculation | MVP Tolerance | Stable Tolerance |
|---|---:|---:|
| Planet longitude | 0.05° | 0.01° |
| Sunrise/Sunset | 2 min | 1 min |
| Tithi end time | 5 min | 2 min |
| Nakshatra end time | 5 min | 2 min |
| Yoga end time | 5 min | 2 min |
| Lagna | 0.25° | 0.1° |
| Dasha balance | 1 day | 0 days |

---

## 22. Do Not Guess Rule

```
IF formula is not verified from authoritative source:
  → Create placeholder function
  → Add # TODO: verify formula source
  → Add @pytest.mark.skip(reason="Formula not verified")
  → Do NOT return fake/guessed values
  → Do NOT ship as complete

Example:
  @pytest.mark.skip(reason="D60 formula needs verification")
  def test_d60_shashtiamsha():
      pass
```

---

## 23. Accuracy Checklist (per Feature)

Before marking any calculation module as complete:

- [ ] Formula from verified source (book title / URL noted in code)
- [ ] At least 2 trusted reference tools compared
- [ ] Timezone handling correct (IST = +5:30 = +5.5)
- [ ] Latitude/Longitude in correct format
- [ ] DST handled for international locations
- [ ] Sunrise/Sunset within 2 min tolerance
- [ ] Tithi/Nakshatra boundary within 5 min tolerance
- [ ] Lagna within 0.25° tolerance
- [ ] Unit tests written and passing
- [ ] Golden fixture saved with `_meta.verified_with` field
- [ ] Edge cases covered: midnight birth, boundary crossings