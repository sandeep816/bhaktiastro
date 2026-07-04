# Sprint 8 - Ashtakavarga Engine

Sprint 8 plans the deterministic Ashtakavarga Engine foundation. The goal is
to add reusable, non-interpretive bindu metadata while preserving all existing
Panchang, Kundali, Varga, Dasha, and Strength behavior.

## Sprint Status

Status: Planned.

This sprint is documentation-first until implementation milestones are started
explicitly. Do not add runtime Ashtakavarga code as part of the planning task.

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

- [ ] Sprint 8 document exists.
- [ ] Master document points to Sprint 8.
- [ ] No runtime source code is changed.
- [ ] Documentation-only checks are run if the repository defines them.

## Milestone 8.2 - Ashtakavarga Constants Foundation

Goal: Add reusable constants and foundation utilities.

Planned scope:

- Define supported planets for Ashtakavarga.
- Define bindu value conventions.
- Define JSON-safe result skeletons.
- Add safe validation helpers.

Acceptance checklist:

- [ ] Supported planets can be discovered.
- [ ] Unsupported planets fail safely.
- [ ] Constants and placeholder structures are JSON-safe.
- [ ] Focused tests cover lookup and invalid input behavior.

## Milestone 8.3 - Planet-Wise Bindu Rules Foundation

Goal: Add verified planet-wise bindu rule metadata.

Planned scope:

- Define planet-wise bindu contribution rules only after source verification.
- Keep rule data immutable where practical.
- Add lookup helpers for one planet's bindu rules.
- Preserve missing or unsupported rule states safely.

Acceptance checklist:

- [ ] Planet-wise rule lookup is tested.
- [ ] Unsupported planet lookup fails safely.
- [ ] Source-verification gaps remain explicit.
- [ ] Full relevant suite passes.

## Milestone 8.4 - Bhinnashtakavarga Foundation

Goal: Add foundation-level Bhinnashtakavarga calculation structure.

Planned scope:

- Reuse existing chart planet and house placement metadata.
- Calculate per-planet bindu totals only from verified rules.
- Return house-wise and Rashi-wise bindu data for one planet.
- Keep missing chart data safe and JSON-serializable.

Acceptance checklist:

- [ ] Bhinnashtakavarga output shape is tested.
- [ ] Missing planet and house data fail safely.
- [ ] Bindu totals are numeric and bounded by the chosen rule structure.
- [ ] Full relevant suite passes.

## Milestone 8.5 - Sarvashtakavarga Foundation

Goal: Add aggregate Sarvashtakavarga structure.

Planned scope:

- Aggregate available Bhinnashtakavarga results.
- Return total bindus by house and Rashi.
- Preserve component provenance and missing-data markers.
- Keep output deterministic and non-interpretive.

Acceptance checklist:

- [ ] Sarvashtakavarga output shape is tested.
- [ ] Aggregate totals are calculated from component bindus.
- [ ] Missing components are represented safely.
- [ ] Full relevant suite passes.

## Milestone 8.6 - House-Wise Bindu Summary

Goal: Add reusable house-wise bindu summary helpers.

Planned scope:

- Summarize bindus by one-based house number.
- Reuse existing Bhava and house normalization helpers.
- Avoid interpretation labels or predictive text.
- Keep invalid house data safe.

Acceptance checklist:

- [ ] House-wise summary output is tested.
- [ ] Invalid house numbers are handled safely.
- [ ] Output remains JSON-safe.
- [ ] Full relevant suite passes.

## Milestone 8.7 - Rashi-Wise Bindu Summary

Goal: Add reusable Rashi-wise bindu summary helpers.

Planned scope:

- Summarize bindus by Rashi.
- Reuse existing Rashi metadata and normalization helpers.
- Preserve Rashi index and name metadata when available.
- Keep invalid Rashi data safe.

Acceptance checklist:

- [ ] Rashi-wise summary output is tested.
- [ ] Invalid Rashi values are handled safely.
- [ ] Output remains JSON-safe.
- [ ] Full relevant suite passes.

## Milestone 8.8 - Transit Support Foundation

Goal: Prepare deterministic structures for future Ashtakavarga transit use.

Planned scope:

- Define input contracts for transit planet placement data.
- Reuse already-calculated planet positions when supplied.
- Do not call astronomy calculations directly.
- Return placeholder/support metadata only where rules are not implemented.

Acceptance checklist:

- [ ] Transit support structures are tested.
- [ ] Missing transit data fails safely.
- [ ] No new astronomy calculation path is introduced.
- [ ] Full relevant suite passes.

## Milestone 8.9 - Kundali Internal Integration

Goal: Integrate Ashtakavarga summaries into Kundali assembly internally.

Planned scope:

- Reuse existing Kundali chart data.
- Add optional internal metadata only when safe.
- Do not remove or rename existing Kundali chart fields.
- Preserve default Kundali assembly behavior.

Acceptance checklist:

- [ ] Internal Kundali integration is opt-in or otherwise backward-compatible.
- [ ] Existing Kundali chart tests continue to pass.
- [ ] Missing chart data fails safely.
- [ ] Full relevant suite passes.

## Milestone 8.10 - Optional Kundali/API Exposure

Goal: Expose Ashtakavarga output only after internal structures are stable.

Planned scope:

- Preserve existing default API responses.
- Add explicit opt-in request flags only if they fit existing schema patterns.
- Return Ashtakavarga output only when explicitly requested.
- Keep response models JSON-safe and backward-compatible.

Acceptance checklist:

- [ ] Default API responses remain backward-compatible.
- [ ] Optional Ashtakavarga output is gated by an explicit flag.
- [ ] Invalid requests return validation errors.
- [ ] Existing API tests still pass.
- [ ] Full suite passes.

## Milestone 8.11 - Validation and Regression Coverage

Goal: Add broad validation and regression coverage for Sprint 8 outputs.

Planned scope:

- Validate unsupported planets and invalid chart data.
- Validate invalid Rashi and house metadata.
- Test JSON serialization for all new Ashtakavarga outputs.
- Test Kundali/API backward compatibility when optional exposure exists.

Acceptance checklist:

- [ ] Invalid input cases are covered.
- [ ] JSON-safe outputs are covered.
- [ ] Regression tests cover default Kundali/API behavior.
- [ ] Full relevant suite passes.

## Known Non-Goals

- Predictions are not implemented in Sprint 8.
- Interpretive Ashtakavarga text is not implemented in Sprint 8.
- Remedies are not implemented in Sprint 8.
- UI display is not implemented in Sprint 8.
- External astrology software validation remains manual until trusted reference
  sources and fixtures are documented.

## Validation Checklist

For each Sprint 8 implementation milestone:

- [ ] Existing Panchang tests pass.
- [ ] Existing Kundali tests pass.
- [ ] Existing Varga tests pass.
- [ ] Existing Dasha tests pass.
- [ ] Existing Strength tests pass.
- [ ] New Ashtakavarga unit tests cover valid, boundary, and invalid inputs.
- [ ] JSON serialization safety is tested for new Ashtakavarga outputs.
- [ ] API tests are added only when API behavior changes.
- [ ] Full relevant suite passes before the milestone is marked complete.

## Stop Point

Stop after each requested Sprint 8 milestone is complete. Do not move from
planning into runtime implementation without a new task.
