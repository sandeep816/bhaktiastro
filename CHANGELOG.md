# CHANGELOG.md

All notable changes to BhaktiAstro will be documented in this file.

## [Unreleased]

### Added
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
