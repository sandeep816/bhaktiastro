# Sprint 6 - Dasha Engine

Sprint 6 built the deterministic Dasha Engine foundation. The implemented
scope calculates source-verified Vimshottari Dasha timelines from existing
birth-chart data without duplicating Panchang, Kundali, Nakshatra, or astronomy
logic.

## Sprint Status

Status: Complete.

Sprint 6 is complete as a deterministic, non-interpretive Dasha foundation.
Predictive interpretation, remedies, and external astrology-software validation
remain outside this sprint.

## Sprint Rules

- Reuse the existing Nakshatra engine.
- Do not duplicate Panchang logic.
- Do not modify Panchang logic.
- Do not modify Kundali, Varga, or planet-position logic.
- Do not change astronomical calculations.
- Keep all outputs JSON-safe.
- Preserve backward compatibility for existing APIs.
- Add Dasha functionality incrementally with focused tests.
- Do not implement predictions, remedies, or interpretation text.
- Never guess Dasha formulas; document any source-verification gap before
  implementation.

## Completed Features

- Vimshottari Dasha constants
- Nakshatra to Mahadasha mapping
- Birth Dasha Balance
- Mahadasha Timeline
- Antardasha Engine
- Pratyantardasha Engine
- Current Dasha Lookup
- Dasha Timeline Builder
- Dasha Pydantic Schemas
- Dasha FastAPI Endpoint
- Validation Coverage
- Regression Coverage

## Implementation Summary

Sprint 6 added reusable Dasha modules under `backend/app/dasha/` and reusable
Vimshottari constants under `backend/app/constants/dasha.py`.

Implemented foundations:

- Classical Vimshottari sequence and Mahadasha durations.
- Nakshatra-to-Dasha-lord lookup for all 27 Nakshatras.
- Birth Dasha balance from Moon longitude and Nakshatra progress.
- JSON-safe Mahadasha timelines covering the full Vimshottari cycle.
- Nested Antardasha and Pratyantardasha period generation.
- Current Dasha lookup using half-open period boundaries.
- Timeline builder that composes Mahadasha, Antardasha, Pratyantardasha, and
  current-Dasha output.
- Dasha request and response schemas.
- `POST /api/v1/dasha` endpoint using existing Panchang output for Moon
  longitude and Nakshatra index.

## API Exposure

The Dasha API endpoint is available at:

```text
POST /api/v1/dasha
```

The endpoint:

- Accepts the Sprint 6 Dasha request schema.
- Uses the existing Panchang calculation path to derive Moon sidereal longitude
  and Nakshatra index.
- Builds Vimshottari Dasha output through the reusable Dasha timeline builder.
- Preserves existing Panchang, Kundali, and Varga API behavior.
- Returns JSON-safe Dasha response data.

## Known Limitations

- No predictive interpretation is implemented yet.
- Only the Vimshottari Dasha system is implemented.
- Remedies are not implemented.
- UI display is not implemented.
- External/manual astrology validation remains separate from automated tests.
- Advanced validation against external astrology software remains a manual
  validation activity until trusted reference fixtures are documented.

## Regression Coverage

Sprint 6 includes focused tests for:

- Vimshottari constants and total cycle duration.
- Nakshatra-to-Mahadasha mapping.
- Birth Dasha balance boundaries and invalid inputs.
- Mahadasha timeline order, duration, coverage, timezone preservation, and
  invalid inputs.
- Antardasha and Pratyantardasha sequence, duration, boundary, timezone, and
  invalid inputs.
- Current Dasha lookup boundaries and missing nested data.
- Dasha timeline builder structure, nested flags, metadata, current lookup, and
  JSON safety.
- Dasha schemas, request validation, response validation, and serialization.
- Dasha FastAPI endpoint routing, valid responses, current-Dasha output, and
  invalid request handling.
- Dasha regression coverage for JSON serialization and stable period ordering.

Existing Panchang, Kundali, and Varga tests remain part of the full regression
suite and are expected to pass unchanged.

## Completion Checklist

- [x] Vimshottari Dasha constants implemented.
- [x] Nakshatra to Mahadasha mapping implemented.
- [x] Birth Dasha Balance implemented.
- [x] Mahadasha Timeline implemented.
- [x] Antardasha Engine implemented.
- [x] Pratyantardasha Engine implemented.
- [x] Current Dasha Lookup implemented.
- [x] Dasha Timeline Builder implemented.
- [x] Dasha Pydantic Schemas implemented.
- [x] Dasha FastAPI Endpoint implemented.
- [x] Validation Coverage added.
- [x] Regression Coverage added.
- [x] Outputs are JSON-safe.
- [x] Existing Panchang behavior remains unchanged.
- [x] Existing Kundali behavior remains unchanged.
- [x] Existing Varga behavior remains unchanged.
- [x] Full test suite passes.

## Stop Point

Sprint 6 Dasha Engine is complete.

Next sprint: Sprint 7 - Planet Strength Engine.
