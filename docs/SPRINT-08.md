# Sprint 8 - Ashtakavarga Engine

Sprint 8 documents the completed deterministic Ashtakavarga Engine foundation.
The goal was to add reusable, non-interpretive bindu metadata while preserving
all existing Panchang, Kundali, Varga, Dasha, and Strength behavior.

## Sprint Status

Status: Complete.

Sprint 8 completed the deterministic Ashtakavarga Engine foundation. Runtime
work is limited to reusable, non-interpretive calculation structures and
optional Kundali metadata/API exposure.

Completed Sprint 8 features:

- Ashtakavarga foundation constants.
- Bhinnashtakavarga rule table.
- Bhinnashtakavarga calculation foundation.
- Sarvashtakavarga calculation foundation.
- Ashtakavarga Summary Builder.
- Internal Kundali Ashtakavarga integration.
- Optional Kundali API Ashtakavarga exposure with `include_ashtakavarga`.
- Validation coverage.
- Regression coverage.

## Sprint Rules

- Reuse existing Kundali chart, planet placement, Rashi, Bhava, and house
  helpers.
- Do not duplicate astronomical calculations.
- Do not modify Panchang logic.
- Do not modify Kundali, Varga, Dasha, or Strength behavior.
- Do not change planet-position calculations.
- Keep all outputs JSON-safe.
- Preserve backward compatibility for existing APIs.
- Add Ashtakavarga functionality incrementally with focused tests.
- Do not implement predictions, remedies, or interpretation text.
- Never guess Ashtakavarga rules. If a rule is unverified, document the
  verification gap before implementation.

## Architecture Direction

The Ashtakavarga Engine should live under `backend/app/` in a location
consistent with the existing domain structure, with final placement chosen
during the first implementation milestone after inspecting local package
boundaries.

Expected reusable concepts:

- Ashtakavarga constants and supported planet registry.
- Planet-wise bindu rule containers.
- Bhinnashtakavarga result structure.
- Sarvashtakavarga result structure.
- House-wise bindu summary.
- Rashi-wise bindu summary.
- Transit support foundation.
- JSON-safe export-ready data.
- Optional Kundali/API exposure only after internal structures are stable.

The Ashtakavarga Engine should consume existing deterministic data:

- Planet positions from the existing planet-position and Kundali output.
- Rashi metadata from existing Rashi helpers.
- Bhava and house placement metadata from existing Kundali helpers.
- Existing normalized planet keys and chart structures.
- Existing API opt-in patterns when exposure is requested.

It should not call Swiss Ephemeris directly unless a future milestone
explicitly requires a reviewed astronomy integration.

## Milestone 8.1 - Sprint 8 Documentation Foundation

Goal: Add the Ashtakavarga sprint plan before runtime work begins.

Planned scope:

- Define sprint rules and non-goals.
- Define implementation milestones.
- Document validation and regression expectations.
- Preserve existing runtime behavior.

Acceptance checklist:

- [x] Sprint 8 document exists.
- [x] Master document points to Sprint 8.
- [x] No runtime source code is changed.
- [x] Documentation-only checks are run if the repository defines them.

## Milestone 8.2 - Ashtakavarga Constants Foundation

Goal: Add reusable constants and foundation utilities.

Planned scope:

- Define supported planets for Ashtakavarga.
- Define bindu value conventions.
- Define JSON-safe result skeletons.
- Add safe validation helpers.

Acceptance checklist:

- [x] Supported planets can be discovered.
- [x] Unsupported planets fail safely.
- [x] Constants and placeholder structures are JSON-safe.
- [x] Focused tests cover lookup and invalid input behavior.

## Milestone 8.3 - Planet-Wise Bindu Rules Foundation

Goal: Add verified planet-wise bindu rule metadata.

Planned scope:

- Define planet-wise bindu contribution rules only after source verification.
- Keep rule data immutable where practical.
- Add lookup helpers for one planet's bindu rules.
- Preserve missing or unsupported rule states safely.

Acceptance checklist:

- [x] Planet-wise rule lookup is tested.
- [x] Unsupported planet lookup fails safely.
- [x] Source-verification gaps remain explicit.
- [x] Full relevant suite passes.

## Milestone 8.4 - Bhinnashtakavarga Foundation

Goal: Add foundation-level Bhinnashtakavarga calculation structure.

Planned scope:

- Reuse existing chart planet and house placement metadata.
- Calculate per-planet bindu totals only from verified rules.
- Return house-wise and Rashi-wise bindu data for one planet.
- Keep missing chart data safe and JSON-serializable.

Acceptance checklist:

- [x] Bhinnashtakavarga output shape is tested.
- [x] Missing planet and house data fail safely.
- [x] Bindu totals are numeric and bounded by the chosen rule structure.
- [x] Full relevant suite passes.

## Milestone 8.5 - Sarvashtakavarga Foundation

Goal: Add aggregate Sarvashtakavarga structure.

Planned scope:

- Aggregate available Bhinnashtakavarga results.
- Return total bindus by house and Rashi.
- Preserve component provenance and missing-data markers.
- Keep output deterministic and non-interpretive.

Acceptance checklist:

- [x] Sarvashtakavarga output shape is tested.
- [x] Aggregate totals are calculated from component bindus.
- [x] Missing components are represented safely.
- [x] Full relevant suite passes.

## Milestone 8.6 - House-Wise Bindu Summary

Goal: Add reusable Ashtakavarga Summary Builder with house-wise ranking.

Planned scope:

- Summarize Sarvashtakavarga bindus by one-based house number.
- Build strongest/weakest house metadata.
- Build deterministic house ranking.
- Reuse existing Bhava and house normalization helpers.
- Avoid interpretation labels or predictive text.
- Keep invalid house data safe.

Acceptance checklist:

- [x] House-wise summary output is tested.
- [x] Invalid house numbers are handled safely.
- [x] Output remains JSON-safe.
- [x] Full relevant suite passes.

## Milestone 8.7 - Kundali Internal Integration

Goal: Integrate Ashtakavarga summaries into Kundali assembly internally.

Planned scope:

- Reuse existing Kundali chart data.
- Add optional internal metadata only when safe.
- Do not remove or rename existing Kundali chart fields.
- Preserve default Kundali assembly behavior.

Acceptance checklist:

- [x] Internal Kundali integration is opt-in and backward-compatible.
- [x] Existing Kundali chart tests continue to pass.
- [x] Missing chart data fails safely.
- [x] Full relevant suite passes.

## Milestone 8.8 - Optional Kundali/API Exposure

Goal: Expose Ashtakavarga output only after internal structures are stable.

Planned scope:

- Preserve existing default API responses.
- Add explicit opt-in request flags only if they fit existing schema patterns.
- Return Ashtakavarga output only when explicitly requested.
- Keep response models JSON-safe and backward-compatible.

Acceptance checklist:

- [x] Default API responses remain backward-compatible.
- [x] Optional Ashtakavarga output is gated by `include_ashtakavarga`.
- [x] Invalid requests return validation errors.
- [x] Existing API tests still pass.
- [x] Full suite passes.

## Milestone 8.9 - Validation and Regression Coverage

Goal: Add broad validation and regression coverage for Sprint 8 outputs.

Planned scope:

- Validate unsupported planets and invalid chart data.
- Validate invalid house metadata.
- Test JSON serialization for all new Ashtakavarga outputs.
- Test Kundali/API backward compatibility when optional exposure exists.

Acceptance checklist:

- [x] Invalid input cases are covered.
- [x] JSON-safe outputs are covered.
- [x] Regression tests cover default Kundali/API behavior.
- [x] Full relevant suite passes.

## Deferred Sprint 8 Ideas

The following items remain outside the completed Sprint 8 scope and can be
planned in future milestones if needed:

- Rashi-wise bindu summary.
- Transit support foundation.
- Transit-based Ashtakavarga interpretation.
- Full classical/manual validation fixtures.

## Known Non-Goals

- Foundation-level Ashtakavarga only.
- Full classical validation remains manual.
- Transit-based Ashtakavarga interpretation is not implemented yet.
- Predictive interpretation is not included in this sprint.
- Predictions are not implemented in Sprint 8.
- Interpretive Ashtakavarga text is not implemented in Sprint 8.
- Remedies are not implemented in Sprint 8.
- UI display is not implemented in Sprint 8.
- External astrology software validation remains manual until trusted reference
  sources and fixtures are documented.

## Validation Checklist

For each Sprint 8 implementation milestone:

- [x] Existing Panchang tests pass.
- [x] Existing Kundali tests pass.
- [x] Existing Varga tests pass.
- [x] Existing Dasha tests pass.
- [x] Existing Strength tests pass.
- [x] New Ashtakavarga unit tests cover valid, boundary, and invalid inputs.
- [x] JSON serialization safety is tested for new Ashtakavarga outputs.
- [x] API tests are added only when API behavior changes.
- [x] Full relevant suite passes before the milestone is marked complete.

## Sprint 8 Completion Checklist

- [x] Ashtakavarga foundation constants are implemented.
- [x] Bhinnashtakavarga rule table is implemented.
- [x] Bhinnashtakavarga calculation foundation is implemented.
- [x] Sarvashtakavarga calculation foundation is implemented.
- [x] Ashtakavarga Summary Builder is implemented.
- [x] Internal Kundali Ashtakavarga integration is implemented.
- [x] Optional Kundali API Ashtakavarga exposure is implemented with
      `include_ashtakavarga`.
- [x] Validation coverage is added.
- [x] Regression coverage is added.
- [x] Existing API behavior remains backward-compatible.
- [x] Outputs remain JSON-safe.
- [x] Predictive interpretation remains out of scope.
- [x] Sprint 8 is ready to close.

## Stop Point

Stop after each requested Sprint 8 milestone is complete. Do not move from
planning into runtime implementation without a new task.
