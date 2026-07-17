# CHANGELOG.md

All notable changes to BhaktiAstro will be documented in this file.

## [Unreleased]

### Added
- Source-of-truth Compatibility / Report Composition orchestration over
  completed Ashtakoota and Manglik results, with separated raw, strict
  precomputed, and serialization APIs, canonical section ordering, immutable
  JSON-safe contracts, strict validation, and exhaustive test specifications
  for Sprint 11.14.
- Deterministic Lagna-only Manglik classification from raw longitudes or an
  existing Kundali chart, plus strict structured comparison of precomputed
  bride/groom classifications using the whole-sign houses `1`, `4`, `7`, `8`,
  and `12` without scoring or cancellation rules.
- Source-of-truth Manglik compatibility foundation using a Lagna-only,
  whole-sign five-house binary convention, separated raw/chart/precomputed
  APIs, structured same/mixed comparison, strict exclusions, validation,
  immutable result contracts, and exhaustive test specifications for Sprint
  11.13.
- Deterministic Ashtakoota aggregation over all eight completed Kootas, with
  canonical execution order, raw Moon-longitude orchestration, strict
  precomputed-result validation, exact `math.fsum` totals, and a fixed `36.0`
  maximum.
- Source-of-truth Ashtakoota aggregation orchestration, canonical eight-Koota
  order, exact `36.0` maximum, raw and strict precomputed-result APIs,
  validation, failure propagation, immutable result-contract, and exhaustive
  test specifications for Sprint 11.12.
- Deterministic Nadi Koota classification and symmetric scoring from supplied
  sidereal Moon Nakshatras, with complete 27-star mapping, exhaustive `27 x
  27` pair coverage, and no cancellation exceptions.
- Source-of-truth Nadi Koota 27-Nakshatra classification, symmetric binary
  scoring matrix, exception exclusions, validation, immutable result-contract,
  boundary, normalization, and exhaustive test specifications for Sprint
  11.11.
- Deterministic Bhakoot Koota full Moon-Rashi classification, inclusive
  circular distance, and symmetric `7.0`/`0.0` scoring with exhaustive
  `12 x 12` Rashi-pair coverage and no cancellation exceptions.
- Source-of-truth Bhakoot Koota full Moon-Rashi derivation, inclusive circular
  distance, symmetric dosha scoring, validation, immutable result-contract,
  cancellation-exclusion, boundary, and exhaustive test specifications for
  Sprint 11.10.
- Deterministic Gana Koota classification and directional scoring from
  supplied sidereal Moon Nakshatras, with complete 27-star mapping and exact
  bride-row/groom-column `3 x 3` matrix coverage.
- Source-of-truth Gana Koota 27-Nakshatra classification, directional
  bride-row/groom-column scoring matrix, validation, immutable result-contract,
  boundary, normalization, and test specifications for Sprint 11.9.
- Deterministic Graha Maitri Koota classification and symmetric scoring from
  supplied sidereal Moon longitudes, reusing canonical Rashi lordship and
  permanent natural planetary relationships with complete `7 x 7` coverage.
- Source-of-truth Graha Maitri Koota Moon-Rashi derivation, permanent
  planetary relationship, symmetric scoring matrix, validation,
  result-contract, and test specifications for Sprint 11.8.
- Deterministic Yoni Koota classification and symmetric scoring from supplied
  sidereal Moon Nakshatras, with complete 27-star mapping and `14 x 14` matrix
  coverage.
- Source-of-truth Yoni Koota 27-Nakshatra classification, Yoni-sex metadata,
  symmetric scoring matrix, validation, result-contract, and test
  specifications for Sprint 11.7.
- Deterministic Tara Koota classification and bidirectional scoring from
  supplied sidereal Moon Nakshatras, with inclusive modulo-9 counting.
- Source-of-truth Tara Koota input, inclusive counting, modulo-9
  classification, bidirectional scoring, validation, result-contract, and test
  specifications for Sprint 11.6.
- Deterministic Vashya Koota classification and directional scoring from
  supplied sidereal Moon longitudes, with split-sign boundary coverage.
- Source-of-truth Vashya Koota classification, boundary, directional scoring,
  validation, result-contract, and test specifications for Sprint 11.5.
- Reusable Prediction Explanation layer for structured result explanations.
- Reusable prediction category discovery, loading, and evaluation service for rule libraries.
- General Personality Prediction Rule Library starter set with validation and composer coverage.
- Sprint 10A Prediction Framework completion documentation and next-sprint pointer.
- Optional Kundali API `include_predictions` flag for empty structured Prediction Framework output.
- Sprint 10A Prediction Framework architecture documentation and current-sprint pointer.
- Sprint 9 Advanced Lagna and Arudha Engine completion documentation and next-sprint pointer.
- Sprint 5 Varga Engine completion documentation and next-sprint pointer.
- Optional Kundali API `include_vargas` flag and response schema support for supported Sprint 5 Varga charts.
- Sprint 4 Kundali Engine documentation and completion checklist.
- Milestone 1 reference validation plan and skipped placeholder accuracy tests.
- Local Panchang smoke script for developer-only API-shaped JSON output.
- Structural Panchang validation fixtures for Jodhpur 1985 and Delhi 2000 with accuracy documentation.
- Panchang API response-shape regression tests for boundary timing fields.
- Karana end-time calculation using Moon-Sun angle boundary search.
- Panchang Yoga end-time calculation using Sun-Moon longitude boundary search.
- Nakshatra end-time calculation using Moon longitude boundary search.
- Tithi end-time calculation using reusable longitude boundary binary search.
- Moonrise and moonset in basic Panchang output, API schema, examples, and docs.
- Moonrise and moonset helpers using Swiss Ephemeris rise/transit calculations.
- Sunrise and sunset in basic Panchang output, API schemas, examples, and docs.
- Sunrise and sunset helpers using Swiss Ephemeris rise/transit calculations.
- Panchang API documentation, Jodhpur request/response examples, and smoke coverage.
- FastAPI Panchang route with request/response schemas and integration tests.
- Pydantic schemas for basic Panchang request validation and response output.
- Basic Panchang assembly from Julian Day, ayanamsa, planets, Tithi, Nakshatra, Yoga, Karana, and Vara.
- Immutable Vara weekday constants and civil-date Vara lookup with tests.
- Deterministic Karana lookup from Sun-Moon sidereal angle with boundary tests.
- Immutable constants for all 11 Karanas with repeating and fixed groups.
- Deterministic Panchang Yoga lookup from Sun-Moon sidereal sum with boundary tests.
- Immutable constants for all 27 Panchang Yogas with degree boundaries.
- Deterministic Tithi lookup from Sun-Moon sidereal angle with boundary tests.
- Immutable constants for all 30 Tithis with paksha and angle boundaries.
- Deterministic Nakshatra lookup from sidereal longitude with Pada boundary tests.
- Immutable constants for all 27 Nakshatras with degree boundaries and tests.
- Planet position engine for Sun through Ketu with sidereal longitudes and unit tests.
- Ayanamsa calculation helper for Lahiri, Raman, and KP modes with unit tests.
- Swiss Ephemeris path loader and verification helper with unit tests.
- Julian Day UT calculation with UTC conversion and unit tests.
- Project folder structure and Python package markers.
- Project metadata and tool configuration in `pyproject.toml`.
- Runtime and development requirements files.
- Git ignore rules for Python, FastAPI, reports, caches, SQLite, and Swiss Ephemeris data.
- Environment example file with local development placeholders.
- Basic application configuration constants.
- Basic logging helper.
- Project README.

### Changed
- Tightened Panchang response schemas to require boundary timing fields and reject undocumented response keys.

## [0.1.0] - TBD

### Planned
- Phase 0 setup completion.
- Initial FastAPI health endpoint.
- Core astronomy foundation.
