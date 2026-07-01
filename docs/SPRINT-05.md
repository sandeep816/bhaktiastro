# Sprint 5 - Divisional Charts / Varga Engine

Sprint 5 builds the reusable Divisional Charts Engine. The goal is to support
Varga charts without duplicating Kundali, Rashi, or planet-position logic.

## Sprint Rules

- Do not modify Panchang logic.
- Do not modify planet position calculations.
- Do not duplicate Rashi lookup logic.
- Do not change existing Kundali API response behavior.
- Reuse existing Kundali chart data and Rashi helpers.
- Add one Varga milestone at a time.
- Keep unimplemented Vargas as explicit placeholders.
- Do not implement predictions or interpretation text.

## Architecture Direction

The Varga Engine should live under `backend/app/kundali/` unless a future
architecture review moves divisional charts into a separate package.

Expected reusable concepts:

- Varga definition registry
- Varga number normalization
- Generic Varga position calculation entrypoint
- Generic Varga chart builder
- Source longitude preservation
- Rashi metadata reuse
- Placeholder support for future Vargas

The Varga framework should consume existing chart-shaped data:

- `lagna.sidereal_longitude`
- `planets[].sidereal_longitude`
- existing Rashi helpers from `backend/app/kundali/rashi.py`

It should not call Swiss Ephemeris directly.

## Milestone 5.1 - Varga Framework Foundation

Goal: Add reusable infrastructure for all future Vargas.

Required helpers:

- `normalize_varga_number()`
- `calculate_varga_position()`
- `build_varga_chart()`

Acceptance checklist:

- [ ] Registered Varga definitions can be discovered.
- [ ] Invalid Varga numbers fail safely.
- [ ] Placeholder Vargas are registered but not falsely calculated.
- [ ] Varga chart output is JSON-safe nested dict/list data.
- [ ] Existing Kundali tests remain unchanged.
- [ ] Full test suite passes.

## Milestone 5.2 - D9 Navamsa

Goal: Implement D9 as the first fully supported Varga.

Scope:

- Calculate Navamsa Rashi from sidereal longitude.
- Preserve source longitude.
- Return Varga Rashi metadata using existing Rashi helpers.
- Build D9 chart from existing Kundali chart data.

Acceptance checklist:

- [ ] Movable sign start rule is tested.
- [ ] Fixed sign start rule is tested.
- [ ] Dual sign start rule is tested.
- [ ] Boundary and wrap-around cases are tested.
- [ ] Missing metadata is handled safely.
- [ ] Full test suite passes.

## Milestone 5.3 - D2 Hora

Goal: Add source-verified Hora calculation.

Before implementation:

- Verify the exact Hora tradition to support.
- Document whether the project uses Parashara-style Sun/Moon Hora or another
  convention.
- Add skipped tests if source verification is incomplete.

Acceptance checklist:

- [ ] Formula source is documented.
- [ ] Odd/even sign rules are tested.
- [ ] Boundary cases are tested.
- [ ] Placeholder is replaced only after verification.
- [ ] Full test suite passes.

## Milestone 5.4 - D3 Drekkana

Goal: Add source-verified Drekkana calculation.

Before implementation:

- Verify the Drekkana sign mapping tradition.
- Confirm handling for each 10-degree division.

Acceptance checklist:

- [ ] Three divisions per Rashi are tested.
- [ ] Boundary cases are tested.
- [ ] All 12 Rashis are covered by focused tests.
- [ ] Full test suite passes.

## Milestone 5.5 - D7 Saptamsa

Goal: Add source-verified Saptamsa calculation.

Before implementation:

- Verify odd/even sign start rules.
- Confirm the exact sevenfold division boundaries.

Acceptance checklist:

- [ ] Odd sign calculation is tested.
- [ ] Even sign calculation is tested.
- [ ] Boundary cases are tested.
- [ ] Full test suite passes.

## Milestone 5.6 - D10 Dasamsa

Goal: Add source-verified Dasamsa calculation.

Before implementation:

- Verify movable/fixed/dual or odd/even rules used by the chosen tradition.
- Document the supported convention.

Acceptance checklist:

- [ ] Formula source is documented.
- [ ] Representative signs are tested.
- [ ] Boundary cases are tested.
- [ ] Full test suite passes.

## Remaining Varga Placeholders

Keep these registered as placeholders until their formulas are verified and
their own milestone is requested:

- D12 Dvadasamsa
- D16 Shodasamsa
- D20 Vimsamsa
- D24 Chaturvimsamsa
- D27 Saptavimsamsa
- D30 Trimsamsa
- D40 Khavedamsa
- D45 Akshavedamsa
- D60 Shashtiamsa

Do not return fake Varga placements for placeholders. Placeholder Vargas should
fail clearly or return an explicit unsupported state, depending on the local
framework convention.

## Testing Plan

For each Varga milestone:

- Add focused unit tests for the formula.
- Add invalid-input tests.
- Add boundary tests.
- Add chart-builder tests when chart output changes.
- Run existing Kundali tests.
- Run the full suite before completion.

Do not modify Panchang tests unless Panchang behavior is intentionally changed
by a future task.

## Stop Point

Stop after the requested Varga milestone is complete. Do not continue from D9
to D2, or from D2 to D3, without a new user instruction.
