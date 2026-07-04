# Sprint 7 - Planet Strength Engine

Sprint 7 plans the deterministic Planet Strength Engine foundation. The goal is
to add reusable, non-interpretive strength metadata for planets while preserving
all existing Panchang, Kundali, Varga, and Dasha behavior.

## Sprint Status

Status: Completed.

Sprint 7 implementation is complete. The sprint delivered reusable,
foundation-level Planet Strength infrastructure, internal Kundali integration,
optional Kundali API exposure, and validation/regression coverage.

## Completed Features

- Shadbala foundation utilities.
- Sthana Bala foundation.
- Dig Bala foundation.
- Kala Bala foundation.
- Chesta Bala foundation.
- Naisargika Bala foundation.
- Drik Bala foundation.
- Shadbala aggregator foundation.
- Ishta/Kashta Bala foundation.
- Planet Strength Summary Builder.
- Internal Kundali strength integration.
- Optional Kundali API strength exposure with `include_strength`.
- Strength validation coverage.
- Strength regression coverage.

## Sprint Rules

- Reuse existing Kundali, Rashi, Bhava, dignity, retrograde, and drishti
  helpers.
- Do not duplicate astronomical calculations.
- Do not modify Panchang logic.
- Do not modify Kundali, Varga, or Dasha behavior.
- Do not change planet-position calculations.
- Keep all outputs JSON-safe.
- Preserve backward compatibility for existing APIs.
- Add strength functionality incrementally with focused tests.
- Do not implement predictions, remedies, or interpretation text.
- Never guess strength formulas. If a formula is unverified, document the
  verification gap before implementation.

## Architecture Direction

The Planet Strength Engine should live under `backend/app/` in a location
consistent with the existing domain structure, with final placement chosen
during the first implementation milestone after inspecting local package
boundaries.

Expected reusable concepts:

- Strength constants and supported planet registry.
- Shadbala result structure.
- Sthana Bala component foundation.
- Dig Bala component foundation.
- Kala Bala component foundation.
- Chesta Bala component foundation.
- Naisargika Bala component foundation.
- Drik Bala component foundation.
- Ishta/Kashta foundation.
- Planet strength summary.
- JSON-safe export-ready data.
- Optional API exposure only after internal structures are stable.

The Planet Strength Engine should consume existing deterministic data:

- Planet positions from the existing planet-position and Kundali output.
- Rashi metadata from existing Rashi helpers.
- Bhava and house placement metadata from existing Kundali helpers.
- Dignity and Mooltrikona metadata from existing Kundali helpers.
- Retrograde metadata from existing astronomy/Kundali helpers.
- Drishti metadata from existing Kundali helpers.

It should not call Swiss Ephemeris directly unless a future milestone
explicitly requires a reviewed astronomy integration.

## Milestone 7.1 - Strength Framework Foundation

Goal: Add reusable Planet Strength infrastructure without calculating
predictions.

Planned scope:

- Define JSON-safe strength result shapes.
- Define supported planet validation.
- Define component keys for Shadbala and related strength outputs.
- Add safe placeholder structures for source-verified future formulas.
- Add focused tests for registry and validation behavior.

Acceptance checklist:

- [ ] Supported planets can be discovered.
- [ ] Unsupported planets fail safely.
- [ ] Strength output structures are JSON-safe.
- [ ] Existing Panchang, Kundali, Varga, and Dasha behavior remains unchanged.
- [ ] Full relevant suite passes.

## Milestone 7.2 - Shadbala Foundation

Goal: Add the top-level Shadbala structure and aggregation boundary.

Planned scope:

- Define Shadbala component containers.
- Preserve component-level source metadata.
- Add aggregation placeholders only where formulas are verified.
- Keep output deterministic and non-interpretive.

Acceptance checklist:

- [ ] Shadbala output shape is tested.
- [ ] Missing component data fails safely.
- [ ] No interpretation text is emitted.
- [ ] Full relevant suite passes.

## Milestone 7.3 - Sthana Bala Foundation

Goal: Add source-verified Sthana Bala component infrastructure.

Planned scope:

- Reuse existing Rashi and dignity helpers.
- Reuse existing house placement metadata where applicable.
- Keep partial or unverified subcomponents explicit and safe.
- Add boundary tests for signs and missing planet data.

Acceptance checklist:

- [ ] Sthana Bala component output is tested.
- [ ] Rashi/dignity reuse is verified.
- [ ] Unsupported or missing inputs fail safely.
- [ ] Full relevant suite passes.

## Milestone 7.4 - Dig Bala Foundation

Goal: Add source-verified Dig Bala component infrastructure.

Planned scope:

- Reuse existing Bhava and house placement helpers.
- Define directional strength input contracts.
- Keep calculations deterministic and JSON-safe.
- Add focused tests for house-boundary behavior.

Acceptance checklist:

- [ ] Dig Bala component output is tested.
- [ ] House placement reuse is verified.
- [ ] Boundary and missing-data cases are tested.
- [ ] Full relevant suite passes.

## Milestone 7.5 - Kala Bala Foundation

Goal: Add source-verified Kala Bala component infrastructure.

Planned scope:

- Reuse existing date/time metadata where applicable.
- Do not duplicate Panchang logic.
- Document any source-verification gaps before implementation.
- Add focused tests for valid, boundary, and invalid inputs.

Acceptance checklist:

- [ ] Kala Bala component output is tested.
- [ ] Panchang behavior remains unchanged.
- [ ] Source-verification gaps are documented.
- [ ] Full relevant suite passes.

## Milestone 7.6 - Chesta Bala Foundation

Goal: Add source-verified Chesta Bala component infrastructure.

Planned scope:

- Reuse existing retrograde and motion-status helpers.
- Do not duplicate planet-position calculations.
- Keep speed and motion metadata JSON-safe.
- Add focused tests for retrograde/direct/stationary inputs where supported.

Acceptance checklist:

- [ ] Chesta Bala component output is tested.
- [ ] Retrograde helper reuse is verified.
- [ ] Unsupported or missing speed data fails safely.
- [ ] Full relevant suite passes.

## Milestone 7.7 - Naisargika Bala Foundation

Goal: Add source-verified Naisargika Bala constants and lookup helpers.

Planned scope:

- Define natural strength constants only after source verification.
- Add lookup helpers for supported planets.
- Keep constants immutable.
- Add focused tests for order, lookup, invalid inputs, and JSON safety.

Acceptance checklist:

- [ ] Naisargika Bala constants are source-verified.
- [ ] Lookup helpers are tested.
- [ ] Invalid planet lookup fails safely.
- [ ] Full relevant suite passes.

## Milestone 7.8 - Drik Bala Foundation

Goal: Add source-verified Drik Bala component infrastructure.

Planned scope:

- Reuse existing Graha Drishti helpers.
- Do not duplicate aspect calculations.
- Preserve parent planet and aspect metadata.
- Add focused tests for supported, unsupported, and missing aspect data.

Acceptance checklist:

- [ ] Drik Bala component output is tested.
- [ ] Drishti helper reuse is verified.
- [ ] Missing aspect data fails safely.
- [ ] Full relevant suite passes.

## Milestone 7.9 - Ishta/Kashta Foundation

Goal: Add source-verified Ishta and Kashta strength infrastructure.

Planned scope:

- Define input contracts for required strength components.
- Calculate only verified deterministic fields.
- Keep output non-interpretive and prediction-free.
- Add focused tests for valid, partial, and missing component inputs.

Acceptance checklist:

- [ ] Ishta/Kashta output shape is tested.
- [ ] Missing component data fails safely.
- [ ] No prediction or interpretation text is emitted.
- [ ] Full relevant suite passes.

## Milestone 7.10 - Planet Strength Summary

Goal: Add a reusable summary structure over verified strength components.

Planned scope:

- Compose available strength components without mutating source data.
- Preserve component provenance and missing-data markers.
- Keep summary output JSON-safe.
- Add focused regression tests for stable structure.

Acceptance checklist:

- [ ] Summary output is tested.
- [ ] Missing components are represented safely.
- [ ] JSON serialization is tested.
- [ ] Full relevant suite passes.

## Milestone 7.11 - Optional API Exposure

Goal: Expose Planet Strength data only when internal structures are stable.

Planned scope:

- Preserve existing Panchang, Kundali, Varga, and Dasha API behavior by
  default.
- Add opt-in request flags only if they fit existing request schema patterns.
- Return strength output only when explicitly requested or through a separate
  safe endpoint.
- Document response shape before public exposure.

Acceptance checklist:

- [ ] Default API responses remain backward-compatible.
- [ ] Optional strength output is gated by an explicit flag or safe endpoint.
- [ ] Invalid strength requests return validation errors.
- [ ] Existing API tests still pass.
- [ ] Full suite passes.

## Known Non-Goals

- Predictions are not implemented in Sprint 7.
- Interpretive strength text is not implemented in Sprint 7.
- Remedies are not implemented in Sprint 7.
- UI display is not implemented in Sprint 7.
- External astrology software validation remains manual until trusted reference
  sources and fixtures are documented.

## Known Limitations

- Sprint 7 implements foundation-level scoring only.
- Full classical Shadbala precision is not implemented yet.
- Manual and external astrology validation remains separate from automated
  structural tests.
- Predictive interpretation is not included in this sprint.

## Regression Checklist

For each Sprint 7 implementation milestone:

- [x] Existing Panchang tests pass.
- [x] Existing Kundali tests pass.
- [x] Existing Varga tests pass.
- [x] Existing Dasha tests pass.
- [x] New strength unit tests cover valid, boundary, and invalid inputs.
- [x] JSON serialization safety is tested for new strength outputs.
- [x] API tests are added only when API behavior changes.
- [x] Full relevant suite passes before the milestone is marked complete.

## Sprint 7 Completion Checklist

- [x] Shadbala constants and component registry are implemented.
- [x] All six foundation Shadbala components are implemented.
- [x] Shadbala aggregator foundation is implemented.
- [x] Ishta/Kashta Bala foundation is implemented.
- [x] Planet Strength Summary Builder is implemented.
- [x] Kundali chart assembly can include internal strength metadata.
- [x] Kundali API exposes strength summary only through `include_strength`.
- [x] Default Kundali API responses remain backward-compatible.
- [x] Validation and regression coverage is present.
- [x] JSON-safe strength output is covered by tests.
- [x] No Panchang, Varga, or Dasha behavior was changed.
- [x] Sprint 7 documentation is complete.

## Stop Point

Sprint 7 Planet Strength Engine is complete.

Next sprint: Sprint 8 - Ashtakavarga Engine.
