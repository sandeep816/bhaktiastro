# BhaktiAstro Roadmap

This roadmap keeps future work ordered and incremental. Each sprint should be
completed, tested, and documented before the next sprint begins.

## Sprint 1 - Astronomy Foundation

Goal: Establish deterministic local astronomy helpers.

- Julian Day UT
- UTC conversion foundations
- Swiss Ephemeris setup
- Ayanamsa helpers
- Planet position foundation
- Longitude normalization and boundary safety

## Sprint 2 - Panchang Calculation Foundation

Goal: Build deterministic Panchang elements from astronomy output.

- Tithi
- Nakshatra
- Panchang Yoga
- Karana
- Vara
- Boundary search foundations
- Rise/set foundations

## Sprint 3 - Panchang API and Validation Foundation

Goal: Stabilize Panchang API output and validation practices.

- Panchang assembly
- FastAPI Panchang route
- Pydantic request/response schemas
- Example request/response files
- Smoke script
- Structural fixtures
- Accuracy and validation documentation

## Sprint 4 - Kundali Engine Foundation

Goal: Build the base Kundali chart and safe foundational metadata.

- Rashi Engine
- Bhava Foundation
- Lagna Foundation
- Kundali Chart Assembly
- Kundali API Foundation
- Planet House Placement
- Graha Lordship
- Dignity and Mooltrikona metadata
- Natural Graha Relationships
- Retrograde and Combustion foundations
- Graha Drishti
- Yoga Framework and first safe yoga detectors
- JSON Export

## Sprint 5 - Divisional Charts / Varga Engine

Goal: Build reusable divisional chart infrastructure.

- Generic Varga framework
- D9 Navamsa
- D2 Hora
- D3 Drekkana
- D7 Saptamsa
- D10 Dasamsa
- Remaining Vargas as future incremental tasks

## Sprint 6 - Dasha Engine Foundation

Goal: Build deterministic Dasha infrastructure.

- Nakshatra-based birth data inputs
- Vimshottari Dasha foundation
- Mahadasha timeline structure
- Antardasha framework
- Safe date boundary handling

## Sprint 7 - House and Chart Strength Foundations

Goal: Add reusable non-interpretive strength metadata.

- House category helpers
- Kendra/Trikona/Dusthana/Upachaya groupings
- Planet placement summaries
- Safe strength placeholder structure
- No predictions

## Sprint 8 - Expanded Yoga Detector Foundation

Goal: Extend deterministic yoga detection carefully.

- Registry-driven yoga detectors
- Additional source-verified yoga rules
- Negative and missing-data safety tests
- No interpretation text

## Sprint 9 - Dosha Detector Foundation

Goal: Add safe, source-verified dosha rule infrastructure.

- Generic dosha result structure
- Manglik foundation if verified
- Kala Sarpa foundation if verified
- Missing-data safety handling
- No remedies or predictions

## Sprint 10 - Muhurat Foundation

Goal: Build reusable deterministic filters for Muhurat.

- Panchang element filter framework
- Weekday and lunar-day filters
- Nakshatra filter foundations
- Safe result structure
- No advice text

## Sprint 11 - Matchmaking Foundation

Goal: Add deterministic compatibility infrastructure.

- Profile input structure
- Guna matching framework
- Source-verified Koota helpers
- Safe score structure
- No marriage predictions

## Sprint 12 - Report Data Model Foundation

Goal: Prepare deterministic data for future reports.

- Report payload schema
- Stable section ordering
- JSON export conventions
- No PDF generation yet

## Sprint 13 - Interpretation Data Boundary

Goal: Define safe boundaries between calculations and text.

- Interpretation input contracts
- Deterministic summary fields
- No AI calculations
- No mutation of calculation output

## Sprint 14 - API Versioning and Stability

Goal: Harden public API contracts.

- Versioning conventions
- Response compatibility checks
- Error response consistency
- Schema documentation updates

## Sprint 15 - Golden Fixture Expansion

Goal: Expand verified reference coverage.

- Mumbai fixture
- London DST fixture
- New York DST fixture
- Kundali fixture structure
- Manual reference documentation

## Sprint 16 - Performance and Caching Foundation

Goal: Improve repeated calculation ergonomics safely.

- Pure-function cache candidates
- Ephemeris setup reuse review
- No result mutation
- Benchmark-oriented tests where useful

## Sprint 17 - Report Rendering Foundation

Goal: Add report generation from already-calculated data.

- HTML report skeleton
- PDF-ready structure
- Section templates
- No new astrology calculations

## Sprint 18 - UI / PWA Foundation

Goal: Build a user-facing surface over stable APIs.

- Basic form flows
- Panchang display
- Kundali display
- Error states
- No calculation in frontend

## Sprint 19 - BhaktiRas Integration Foundation

Goal: Prepare integration boundaries for BhaktiRas.

- API client contract
- Authentication placeholder if required
- Content handoff rules
- No astrology recalculation outside engine

## Sprint 20 - Production Readiness Review

Goal: Review reliability, security, documentation, and deployment readiness.

- Full regression review
- API documentation review
- Accuracy documentation review
- Deployment checklist
- Security and secrets checklist
