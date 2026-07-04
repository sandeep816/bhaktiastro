# Sprint 9 - Advanced Lagna and Arudha Engine

Sprint 9 completed the deterministic Advanced Lagna and Arudha Engine
foundation. The sprint added reusable, non-interpretive special Lagna metadata
while preserving all existing Panchang, Kundali, Varga, Dasha, Strength, and
Ashtakavarga behavior.

## Sprint Status

Status: Complete.

Sprint 9 is complete. Future changes should be handled in a new sprint or a
new explicitly requested maintenance task.

## Completed Features

- Arudha Lagna foundation.
- Upapada Lagna foundation.
- Hora Lagna foundation.
- Ghati Lagna foundation.
- Bhava Madhya / cusp foundation.
- Special Lagna Summary Builder.
- Internal Kundali Special Lagna integration.
- Optional Kundali API Special Lagna exposure with `include_special_lagnas`.
- Validation coverage.
- Regression coverage.

## Sprint Rules

- Reuse existing Lagna, Bhava, Rashi, house placement, and lordship helpers.
- Do not duplicate astronomical calculations.
- Do not modify Panchang logic.
- Do not modify completed Kundali, Varga, Dasha, Strength, or Ashtakavarga
  behavior.
- Do not change planet-position calculations.
- Keep all outputs JSON-safe.
- Preserve backward compatibility for existing APIs.
- Add Advanced Lagna and Arudha functionality incrementally with focused tests.
- Do not implement predictions, remedies, or interpretation text.
- Never guess special Lagna formulas. If a formula is unverified, document the
  verification gap before implementation.

## Architecture Direction

The Advanced Lagna and Arudha Engine should live under `backend/app/` in a
location consistent with existing Kundali domain structure, with final placement
chosen during the first implementation milestone after inspecting local package
boundaries.

Expected reusable concepts:

- Arudha Lagna result structure.
- Upapada Lagna result structure.
- Hora Lagna result structure.
- Ghati Lagna result structure.
- Bhava Madhya / cusp result structure.
- Special Lagna summary structure.
- JSON-safe export-ready data.
- Optional Kundali/API exposure only after internal structures are stable.

The engine should consume existing deterministic data:

- Lagna metadata from existing Kundali output.
- Rashi metadata from existing Rashi helpers.
- Bhava and house placement metadata from existing Kundali helpers.
- Rashi lordship metadata from existing lordship helpers.
- Planet placements from existing Kundali chart data when required.
- Existing API opt-in patterns when exposure is requested.

It should not call Swiss Ephemeris directly unless a future milestone explicitly
requires a reviewed astronomy integration.

## Milestone 9.1 - Sprint 9 Documentation Foundation

Goal: Add the Advanced Lagna and Arudha sprint plan before runtime work begins.

Planned scope:

- Define sprint rules and non-goals.
- Define implementation milestones.
- Document validation and regression expectations.
- Preserve existing runtime behavior.

Acceptance checklist:

- [x] Sprint 9 document exists.
- [x] Master document points to Sprint 9 during Sprint 9.
- [x] No runtime source code is changed by the planning milestone.
- [x] Documentation-only checks are run if the repository defines them.

## Milestone 9.2 - Arudha Constants and Foundation Utilities

Goal: Add reusable constants and foundation utilities for special Lagna work.

Planned scope:

- Define supported special Lagna types.
- Define JSON-safe result skeletons.
- Add safe validation helpers.
- Reuse existing Rashi and Bhava normalization helpers.

Acceptance checklist:

- [x] Supported special Lagna structures can be discovered through the summary.
- [x] Unsupported or incomplete special Lagna inputs fail safely.
- [x] Placeholder and missing-data structures are JSON-safe.
- [x] Focused tests cover lookup and invalid input behavior.

## Milestone 9.3 - Arudha Lagna Foundation

Goal: Add deterministic Arudha Lagna foundation structure.

Planned scope:

- Reuse Lagna Rashi, house, and lordship metadata.
- Calculate Arudha Lagna only from verified source rules.
- Return Rashi and house metadata when available.
- Preserve missing-data markers safely.

Acceptance checklist:

- [x] Arudha Lagna output shape is tested.
- [x] Required Lagna/lordship data is validated.
- [x] Missing data fails safely.
- [x] Full relevant suite passes.

## Milestone 9.4 - Upapada Lagna Foundation

Goal: Add deterministic Upapada Lagna foundation structure.

Planned scope:

- Reuse twelfth-house, lordship, and placement metadata.
- Calculate Upapada Lagna only from verified source rules.
- Return Rashi and house metadata when available.
- Preserve missing-data markers safely.

Acceptance checklist:

- [x] Upapada Lagna output shape is tested.
- [x] Required house/lordship data is validated.
- [x] Missing data fails safely.
- [x] Full relevant suite passes.

## Milestone 9.5 - Hora Lagna Foundation

Goal: Add deterministic Hora Lagna foundation structure.

Planned scope:

- Reuse existing birth time, Lagna, Rashi, and Bhava helpers when available.
- Avoid duplicate astronomical calculations.
- Return placeholder metadata until formula verification is complete if needed.
- Preserve JSON-safe output.

Acceptance checklist:

- [x] Hora Lagna output shape is tested.
- [x] Time input validation is covered.
- [x] Missing data fails safely.
- [x] Full relevant suite passes.

## Milestone 9.6 - Ghati Lagna Foundation

Goal: Add deterministic Ghati Lagna foundation structure.

Planned scope:

- Reuse existing time and Lagna metadata when available.
- Avoid duplicate astronomical calculations.
- Return placeholder metadata until formula verification is complete if needed.
- Preserve JSON-safe output.

Acceptance checklist:

- [x] Ghati Lagna output shape is tested.
- [x] Time input validation is covered.
- [x] Missing data fails safely.
- [x] Full relevant suite passes.

## Milestone 9.7 - Bhava Madhya / Cusp Foundation

Goal: Add reusable Bhava Madhya / cusp foundation metadata.

Planned scope:

- Reuse existing Bhava and house helpers.
- Preserve existing placeholder house behavior.
- Add deterministic cusp result structures only where safely supported.
- Keep output non-interpretive.

Acceptance checklist:

- [x] Bhava Madhya / cusp output shape is tested.
- [x] Invalid house data is handled safely.
- [x] Existing Kundali house behavior remains unchanged.
- [x] Full relevant suite passes.

## Milestone 9.8 - Special Lagna Summary Builder

Goal: Add a reusable summary builder for supported special Lagna outputs.

Planned scope:

- Compose available Arudha, Upapada, Hora, Ghati, and cusp foundations.
- Preserve component provenance and missing-data markers.
- Keep output deterministic, JSON-safe, and non-interpretive.
- Do not expose the summary through public APIs yet.

Acceptance checklist:

- [x] Summary output shape is tested.
- [x] Missing components are represented safely.
- [x] Output remains JSON-safe.
- [x] Full relevant suite passes.

## Milestone 9.9 - Kundali Internal Integration

Goal: Integrate special Lagna summaries into Kundali assembly internally.

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

## Milestone 9.10 - Optional Kundali/API Exposure

Goal: Expose special Lagna output only after internal structures are stable.

Planned scope:

- Preserve existing default API responses.
- Add explicit opt-in request flags only if they fit existing schema patterns.
- Return special Lagna output only when explicitly requested.
- Keep response models JSON-safe and backward-compatible.

Acceptance checklist:

- [x] Default API responses remain backward-compatible.
- [x] Optional special Lagna output is gated by an explicit flag.
- [x] Invalid requests return validation errors.
- [x] Existing API tests still pass.
- [x] Full suite passes.

## Milestone 9.11 - Validation and Regression Coverage

Goal: Add broad validation and regression coverage for Sprint 9 outputs.

Planned scope:

- Validate unsupported special Lagna types and invalid chart data.
- Validate invalid Rashi, Bhava, and house metadata.
- Test JSON serialization for all new special Lagna outputs.
- Test Kundali/API backward compatibility when optional exposure exists.

Acceptance checklist:

- [x] Invalid input cases are covered.
- [x] JSON-safe outputs are covered.
- [x] Regression tests cover default Kundali/API behavior.
- [x] Full relevant suite passes.

## Known Limitations

- Foundation-level special Lagna calculations only.
- Advanced house systems are not implemented yet.
- Manual/external astrology validation remains separate.
- Predictive interpretation is not included in this sprint.

## Known Non-Goals

- Predictions are not implemented in Sprint 9.
- Predictive interpretation is not implemented in Sprint 9.
- Interpretive special Lagna text is not implemented in Sprint 9.
- Remedies are not implemented in Sprint 9.
- UI display is not implemented in Sprint 9.
- Advanced house systems are not implemented in Sprint 9.
- Manual/external astrology validation remains separate from automated
  structural tests.
- External astrology software validation remains manual until trusted reference
  sources and fixtures are documented.

## Validation Checklist

For each Sprint 9 implementation milestone:

- [x] Existing Panchang tests pass.
- [x] Existing Kundali tests pass.
- [x] Existing Varga tests pass.
- [x] Existing Dasha tests pass.
- [x] Existing Strength tests pass.
- [x] Existing Ashtakavarga tests pass.
- [x] New special Lagna unit tests cover valid, boundary, and invalid inputs.
- [x] JSON serialization safety is tested for new outputs.
- [x] API tests are added only when API behavior changes.
- [x] Full relevant suite passes before the milestone is marked complete.

## Sprint 9 Completion Checklist

- [x] Arudha Lagna foundation is implemented and tested.
- [x] Upapada Lagna foundation is implemented and tested.
- [x] Hora Lagna foundation is implemented and tested.
- [x] Ghati Lagna foundation is implemented and tested.
- [x] Bhava Madhya / cusp foundation is implemented and tested.
- [x] Special Lagna Summary Builder is implemented and tested.
- [x] Internal Kundali Special Lagna integration is complete.
- [x] Optional Kundali API Special Lagna exposure is complete.
- [x] Validation coverage is added.
- [x] Regression coverage is added.
- [x] Existing runtime behavior remains backward-compatible.
- [x] Full test suite passes.

## Stop Point

Stop after each requested Sprint 9 milestone is complete. Do not move from
planning into runtime implementation without a new task.
