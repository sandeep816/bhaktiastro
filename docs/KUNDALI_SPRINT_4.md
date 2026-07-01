# Sprint 4 Kundali Engine

Sprint 4 establishes the deterministic Kundali Engine foundation. The scope is
calculation and chart metadata only: no predictions, no interpretation text, and
no yoga phala.

## Completed Features

| Area | Status | Notes |
| --- | --- | --- |
| Rashi Engine | Complete | Normalizes longitudes and resolves Rashi metadata. |
| Bhava Foundation | Complete | Provides placeholder whole-sign-style house helpers. |
| Lagna Foundation | Complete | Calculates sidereal Lagna and Lagna Rashi metadata. |
| Kundali Chart Assembly | Complete | Builds internal Lagna, planet, and house chart data. |
| Kundali API Foundation | Complete | Adds `/api/v1/kundali` request and response schemas. |
| Chart Format Foundation | Complete | Keeps chart output structured as nested dict/list data. |
| Planet House Placement | Complete | Adds whole-sign planet house number and index metadata. |
| Graha Lordship | Complete | Maps all 12 Rashis to their classical lords. |
| Exaltation/Debilitation | Complete | Adds reusable dignity status helpers. |
| Mooltrikona | Complete | Adds supported planet Mooltrikona checks. |
| Natural Graha Relationships | Complete | Adds classical natural friend/neutral/enemy mappings. |
| Retrograde Foundation | Complete | Adds speed-based motion status helpers where speed exists. |
| Combustion Foundation | Complete | Adds conservative Sun-distance combustion metadata. |
| Graha Drishti | Complete | Adds house-based aspect foundations. |
| Yoga Framework | Complete | Adds generic yoga result structure and detector registry. |
| Gajakesari Yoga Foundation | Complete | Detects Jupiter in Kendra from Moon. |
| Raja Yoga Foundation | Complete | Detects Kendra/Trikona lord same-house association. |
| Dhana Yoga Foundation | Complete | Detects 2nd/11th lord same-house association. |
| Panch Mahapurusha Yoga Foundation | Complete | Detects supported own/exalted Kendra placements. |
| JSON Export | Complete | Adds reusable JSON-safe Kundali chart export helper. |

## Module Map

Core Kundali modules:

- `backend/app/kundali/rashi.py`
- `backend/app/kundali/bhava.py`
- `backend/app/kundali/lagna.py`
- `backend/app/kundali/placement.py`
- `backend/app/kundali/chart.py`
- `backend/app/kundali/formatter.py`
- `backend/app/kundali/json_export.py`

Graha metadata modules:

- `backend/app/kundali/graha_lordship.py`
- `backend/app/kundali/dignity.py`
- `backend/app/kundali/mooltrikona.py`
- `backend/app/kundali/graha_relationship.py`
- `backend/app/astronomy/retrograde.py`
- `backend/app/kundali/combustion.py`
- `backend/app/kundali/drishti.py`

Yoga foundation modules:

- `backend/app/kundali/yoga_framework.py`
- `backend/app/kundali/gajakesari.py`
- `backend/app/kundali/raja_yoga.py`
- `backend/app/kundali/dhana_yoga.py`
- `backend/app/kundali/panch_mahapurusha.py`

API and schema modules:

- `backend/app/api/v1/kundali.py`
- `backend/app/schemas/kundali.py`

## JSON Export

The reusable JSON export helper lives in `backend/app/kundali/json_export.py`.
It returns JSON-safe nested primitives for Kundali chart data and can add
export-only metadata:

```python
from backend.app.kundali.chart import assemble_kundali_chart
from backend.app.kundali.json_export import export_kundali_chart

chart_data = assemble_kundali_chart(
    1990,
    1,
    1,
    12,
    0,
    0,
    5.5,
    26.9124,
    75.7873,
)

exported = export_kundali_chart(chart_data)
assert exported["metadata"]["engine"] == "kundali"
```

The public Kundali API response remains backward-compatible and does not require
the export-only `metadata` object.

## Yoga Detector Scope

The Sprint 4 yoga detectors intentionally implement foundation-level boolean
rules only:

- Gajakesari Yoga: Jupiter in Kendra from Moon.
- Raja Yoga: Kendra lord and Trikona lord in the same house.
- Dhana Yoga: 2nd lord and 11th lord in the same house.
- Panch Mahapurusha Yogas: Mars, Mercury, Jupiter, Venus, or Saturn in own or
  exaltation sign while placed in a Kendra house.

Each detector returns the generic yoga result structure:

- `yoga_name`
- `is_present`
- `involved_planets`
- `involved_houses`
- `reason`
- `strength`

The `strength` field is a placeholder and is not interpreted in Sprint 4.

## Known Limitations

- No predictions are implemented yet.
- Yoga logic is foundation-level only.
- No interpretation text or phala is generated.
- Advanced house systems are not implemented.
- Divisional charts are not implemented.
- Manual astronomical validation remains separate from this completion checklist.
- The placeholder house foundation is intentionally conservative and may evolve
  after source-verified requirements are added.

## Completion Checklist

- [x] Rashi Engine completed and tested.
- [x] Bhava Foundation completed and tested.
- [x] Lagna Foundation completed and tested.
- [x] Kundali Chart Assembly completed and tested.
- [x] Kundali API Foundation completed and tested.
- [x] Chart Format Foundation completed and tested.
- [x] Planet House Placement completed and tested.
- [x] Graha Lordship completed and tested.
- [x] Exaltation/Debilitation completed and tested.
- [x] Mooltrikona completed and tested.
- [x] Natural Graha Relationships completed and tested.
- [x] Retrograde Foundation completed and tested.
- [x] Combustion Foundation completed and tested.
- [x] Graha Drishti completed and tested.
- [x] Yoga Framework completed and tested.
- [x] Gajakesari Yoga Foundation completed and tested.
- [x] Raja Yoga Foundation completed and tested.
- [x] Dhana Yoga Foundation completed and tested.
- [x] Panch Mahapurusha Yoga Foundation completed and tested.
- [x] JSON Export completed and tested.
- [x] Public API response fields preserved.
- [x] Panchang logic unchanged.
- [x] Astronomical calculations unchanged.
- [x] Full test suite run for Sprint 4 completion.
