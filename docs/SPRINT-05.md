# Sprint 5 - Divisional Charts / Varga Engine

Sprint 5 builds the reusable Divisional Charts Engine. The goal is to support
Varga charts without duplicating Kundali, Rashi, or planet-position logic.

## Sprint Status

Status: Complete.

Sprint 5 delivered reusable Varga infrastructure, source-longitude-preserving
Varga calculations, internal Kundali integration, and optional Kundali API
exposure through `include_vargas`.

## Sprint Rules

- Do not modify Panchang logic.
- Do not modify planet position calculations.
- Do not duplicate Rashi lookup logic.
- Do not change existing Kundali API response behavior.
- Reuse existing Kundali chart data and Rashi helpers.
- Add one Varga milestone at a time.
- Keep unimplemented Vargas as explicit placeholders.
- Do not implement predictions or interpretation text.

## Completed Architecture

The Varga Engine lives under `backend/app/kundali/`. It consumes existing
chart-shaped data and does not call Swiss Ephemeris or Panchang logic directly.

Completed reusable concepts:

- Varga definition registry
- Varga number normalization
- Generic Varga position calculation entrypoint
- Generic Varga chart builder
- Source longitude preservation
- Rashi metadata reuse
- JSON-safe nested dict/list output
- Internal Kundali chart integration
- Optional Kundali API exposure

The framework consumes:

- `lagna.sidereal_longitude`
- `planets[].sidereal_longitude`
- existing Rashi helpers from `backend/app/kundali/rashi.py`

## Milestone 5.1 - Varga Framework Foundation

Goal: Add reusable infrastructure for all Vargas.

Completed helpers:

- `normalize_varga_number()`
- `calculate_varga_position()`
- `build_varga_chart()`

Acceptance checklist:

- [x] Registered Varga definitions can be discovered.
- [x] Invalid Varga numbers fail safely.
- [x] Varga chart output is JSON-safe nested dict/list data.
- [x] Existing Kundali behavior remains backward-compatible.
- [x] Full test suite passes.

## Milestone 5.2 - D9 Navamsa

Goal: Implement D9 Navamsa.

Completed scope:

- Calculate Navamsa Rashi from sidereal longitude.
- Preserve source longitude.
- Return Varga Rashi metadata using existing Rashi helpers.
- Build D9 chart from existing Kundali chart data.

Acceptance checklist:

- [x] Movable sign start rule is tested.
- [x] Fixed sign start rule is tested.
- [x] Dual sign start rule is tested.
- [x] Boundary and wrap-around cases are tested.
- [x] Missing metadata is handled safely.
- [x] Full test suite passes.

## Milestone 5.3 - D2 Hora

Goal: Add source-verified Hora calculation.

Completed scope:

- Parashari Sun/Moon Hora convention.
- Odd/even sign half-rashi rules.
- Boundary handling at 15 degrees.
- Planet-shaped input support.

Acceptance checklist:

- [x] Formula convention is documented in code/tests.
- [x] Odd/even sign rules are tested.
- [x] Boundary cases are tested.
- [x] Full test suite passes.

## Milestone 5.4 - D3 Drekkana

Goal: Add source-verified Drekkana calculation.

Completed scope:

- Three 10-degree divisions per Rashi.
- 1st/5th/9th Rashi mapping rule.
- Boundary and wrap-around handling.

Acceptance checklist:

- [x] Three divisions per Rashi are tested.
- [x] Boundary cases are tested.
- [x] Wrap-around cases are tested.
- [x] Full test suite passes.

## Milestone 5.5 - D7 Saptamsa

Goal: Add source-verified Saptamsa calculation.

Completed scope:

- Sevenfold Rashi division.
- Odd/even sign start rules.
- Boundary and wrap-around handling.

Acceptance checklist:

- [x] Odd sign calculation is tested.
- [x] Even sign calculation is tested.
- [x] Boundary cases are tested.
- [x] Full test suite passes.

## Milestone 5.6 - D10 Dasamsa

Goal: Add source-verified Dasamsa calculation.

Completed scope:

- Tenfold Rashi division.
- Odd/even sign start rules used by the supported convention.
- Boundary and wrap-around handling.

Acceptance checklist:

- [x] Supported convention is documented in code/tests.
- [x] Representative signs are tested.
- [x] Boundary cases are tested.
- [x] Full test suite passes.

## Additional Completed Vargas

Sprint 5 also completed the remaining requested Varga calculations:

- D12 Dwadashamsa
- D16 Shodasamsa
- D20 Vimshamsa
- D24 Siddhamsa
- D27 Bhamsa
- D30 Trimsamsa
- D40 Khavedamsa
- D45 Akshavedamsa
- D60 Shastiamsa

Each completed Varga preserves source longitude, returns calculated Rashi
metadata using existing helpers, and has focused tests for representative rules,
boundaries, invalid input, and chart output where applicable.

## Kundali Integration

Completed integration points:

- Internal Kundali assembly can include Varga charts with
  `include_vargas=True`.
- Public Kundali API accepts optional `include_vargas: bool = false`.
- When `include_vargas` is omitted or false, the public Kundali response keeps
  the existing `lagna`, `planets`, and `houses` top-level shape.
- When `include_vargas` is true, the API returns supported charts:
  `D2`, `D3`, `D7`, `D9`, `D10`, `D12`, `D16`, `D20`, `D24`, `D27`, `D30`,
  `D40`, `D45`, and `D60`.
- D9 Navamsa is present in the API response when Varga output is enabled.

## Known Limitations

- Varga interpretation is not implemented.
- Predictions are not implemented.
- Remedies, report text, and user-facing explanatory interpretations are not
  implemented.
- Advanced validation against external astrology software remains manual.
- Automated tests cover deterministic structure, boundary behavior, and
  regression safety; golden-value validation remains separate until trusted
  external references are documented.

## Regression Coverage

Sprint 5 regression coverage includes:

- Add focused unit tests for the formula.
- Add invalid-input tests.
- Add boundary tests.
- Add chart-builder tests when chart output changes.
- Run existing Kundali tests.
- Run Kundali API tests when API exposure changed.
- Run Panchang API tests to confirm no Panchang behavior changed.
- Run the full suite before completion.

Panchang logic and planet-position logic were not modified during Sprint 5.

## Completion Checklist

- [x] Varga foundation implemented.
- [x] D2 Hora implemented.
- [x] D3 Drekkana implemented.
- [x] D7 Saptamsa implemented.
- [x] D9 Navamsa implemented.
- [x] D10 Dasamsa implemented.
- [x] D12 Dwadashamsa implemented.
- [x] D16 Shodasamsa implemented.
- [x] D20 Vimshamsa implemented.
- [x] D24 Siddhamsa implemented.
- [x] D27 Bhamsa implemented.
- [x] D30 Trimsamsa implemented.
- [x] D40 Khavedamsa implemented.
- [x] D45 Akshavedamsa implemented.
- [x] D60 Shastiamsa implemented.
- [x] Varga charts integrated internally into Kundali assembly.
- [x] Varga charts exposed through Kundali API only when `include_vargas` is
  true.
- [x] Default Kundali API response remains backward-compatible.
- [x] Known limitations are documented.
- [x] Full test suite passes.

## Stop Point

Sprint 5 is complete. Stop before Sprint 6 unless a new task explicitly starts
the Dasha Engine work.
