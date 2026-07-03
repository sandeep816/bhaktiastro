# Sprint 6 - Dasha Engine

Sprint 6 builds the deterministic Dasha Engine foundation. The goal is to
calculate source-verified Dasha timelines from existing birth-chart data
without duplicating Panchang, Kundali, Nakshatra, or astronomy logic.

## Sprint Status

Status: Planned.

This sprint is documentation-first until implementation milestones are started
explicitly. Do not add runtime Dasha code as part of the planning task.

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

## Architecture Direction

The Dasha Engine should live under `backend/app/` in a location consistent with
the existing domain structure, with final placement chosen during the first
implementation milestone after inspecting local package boundaries.

Expected reusable concepts:

- Dasha system registry, starting with Vimshottari.
- Nakshatra-based birth input adapter.
- Starting Mahadasha calculation from Moon Nakshatra.
- Balance of Dasha at birth.
- Mahadasha period model.
- Antardasha period model.
- Pratyantardasha period model.
- Timeline generation helpers.
- Current Dasha lookup helper.
- JSON-safe export-ready nested data.

The Dasha framework should consume existing deterministic data:

- Moon sidereal longitude from existing planet-position or chart output.
- Existing Nakshatra lookup helpers from `backend/app/astrology/nakshatra.py`.
- Existing date/time conversion helpers where needed.

It should not call Swiss Ephemeris directly unless a future milestone explicitly
requires a reviewed astronomy integration.

## Milestone 6.1 - Dasha Framework Foundation

Goal: Add reusable Dasha infrastructure without calculating predictions.

Planned scope:

- Define JSON-safe Dasha result shapes.
- Define Vimshottari Dasha period constants after source verification.
- Add safe validation for supported Dasha systems.
- Add timeline-friendly date boundary conventions.
- Add focused tests for registry and validation behavior.

Acceptance checklist:

- [ ] Supported Dasha systems can be discovered.
- [ ] Unsupported Dasha systems fail safely.
- [ ] Period constants are source-verified before use.
- [ ] Output structures are JSON-safe.
- [ ] Existing Panchang, Kundali, and Varga behavior remains unchanged.
- [ ] Full relevant suite passes.

## Milestone 6.2 - Vimshottari Dasha Foundation

Goal: Implement the deterministic Vimshottari Dasha foundation.

Planned scope:

- Use the existing Nakshatra engine to identify the birth Nakshatra.
- Map the Nakshatra lord to the starting Mahadasha.
- Preserve source Moon longitude and Nakshatra metadata.
- Validate boundary behavior at Nakshatra and Pada transitions.

Acceptance checklist:

- [ ] Nakshatra-based starting Mahadasha is tested.
- [ ] Nakshatra boundary cases are tested.
- [ ] Missing Moon longitude fails safely.
- [ ] Existing Nakshatra tests remain unchanged.
- [ ] Full relevant suite passes.

## Milestone 6.3 - Balance of Dasha at Birth

Goal: Calculate the remaining balance of the starting Mahadasha at birth.

Planned scope:

- Calculate elapsed fraction within the birth Nakshatra.
- Convert remaining Nakshatra fraction into Mahadasha balance.
- Return elapsed, remaining, and total period metadata.
- Keep date calculations deterministic and timezone-safe.

Acceptance checklist:

- [ ] Beginning-of-Nakshatra balance is tested.
- [ ] Middle-of-Nakshatra balance is tested.
- [ ] End-of-Nakshatra balance is tested.
- [ ] Fraction and date-boundary rounding are tested.
- [ ] Full relevant suite passes.

## Milestone 6.4 - Mahadasha Timeline

Goal: Build a deterministic Mahadasha timeline from the birth Dasha balance.

Planned scope:

- Generate ordered Mahadasha periods.
- Preserve start and end datetimes.
- Carry Dasha lord and duration metadata.
- Keep timeline output JSON-safe and stable.

Acceptance checklist:

- [ ] Timeline starts with the birth Mahadasha balance.
- [ ] Subsequent Mahadashas follow Vimshottari order.
- [ ] Period boundaries do not overlap.
- [ ] Total generated duration is tested.
- [ ] Full relevant suite passes.

## Milestone 6.5 - Antardasha

Goal: Add Antardasha generation inside Mahadasha periods.

Planned scope:

- Generate nested Antardasha periods.
- Preserve parent Mahadasha metadata.
- Use source-verified proportional duration rules.
- Keep nested output JSON-safe.

Acceptance checklist:

- [ ] Antardasha order is tested.
- [ ] Antardasha durations are tested.
- [ ] Parent-child boundaries are tested.
- [ ] Missing parent period data fails safely.
- [ ] Full relevant suite passes.

## Milestone 6.6 - Pratyantardasha

Goal: Add Pratyantardasha generation inside Antardasha periods.

Planned scope:

- Generate nested Pratyantardasha periods.
- Preserve Mahadasha and Antardasha parent metadata.
- Use source-verified proportional duration rules.
- Keep deeply nested output bounded and JSON-safe.

Acceptance checklist:

- [ ] Pratyantardasha order is tested.
- [ ] Pratyantardasha durations are tested.
- [ ] Nested period boundaries are tested.
- [ ] Missing parent period data fails safely.
- [ ] Full relevant suite passes.

## Milestone 6.7 - Current Dasha Lookup

Goal: Add a deterministic lookup for active Dasha periods at a target datetime.

Planned scope:

- Find active Mahadasha for a target datetime.
- Find active Antardasha when nested data is available.
- Find active Pratyantardasha when nested data is available.
- Return a stable JSON-safe current-Dasha summary.

Acceptance checklist:

- [ ] Lookup at period start is tested.
- [ ] Lookup inside period range is tested.
- [ ] Lookup at period end boundary is tested.
- [ ] Out-of-range targets fail safely or return an explicit empty state.
- [ ] Full relevant suite passes.

## Milestone 6.8 - Optional API Exposure

Goal: Expose Dasha data only when the internal engine and schemas are stable.

Planned scope:

- Preserve existing Panchang and Kundali API behavior by default.
- Add opt-in request flags only if they fit existing request schema patterns.
- Return Dasha output only when explicitly requested or through a separate safe
  endpoint.
- Document response shape before public exposure.

Acceptance checklist:

- [ ] Default API responses remain backward-compatible.
- [ ] Optional Dasha output is gated by an explicit flag or safe endpoint.
- [ ] Invalid Dasha requests return validation errors.
- [ ] Panchang API tests still pass.
- [ ] Kundali API tests still pass.
- [ ] Full suite passes.

## Known Non-Goals

- Predictions are not implemented in Sprint 6.
- Interpretive Dasha text is not implemented in Sprint 6.
- Remedies are not implemented in Sprint 6.
- UI display is not implemented in Sprint 6.
- External astrology software validation remains manual until trusted reference
  sources and fixtures are documented.

## Regression Checklist

For each Sprint 6 implementation milestone:

- [ ] Existing Panchang tests pass.
- [ ] Existing Kundali tests pass.
- [ ] Existing Varga tests pass.
- [ ] New Dasha unit tests cover valid, boundary, and invalid inputs.
- [ ] JSON serialization safety is tested for new Dasha outputs.
- [ ] API tests are added only when API behavior changes.
- [ ] Full relevant suite passes before the milestone is marked complete.

## Stop Point

Stop after each requested Sprint 6 milestone is complete. Do not move from
framework planning into runtime implementation without a new task.
