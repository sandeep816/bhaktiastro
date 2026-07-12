# Sprint 10A - Prediction Framework Architecture

Sprint 10A defines the architecture for a deterministic-first Prediction
Framework. This sprint completed the reusable framework foundations without
adding real prediction rules or interpretive prose.

The goal is to design a reusable framework that can consume completed
calculation outputs and return structured, JSON-safe facts, reasons, and
intermediate evidence without generating interpretive prose inside the core
engine.

## Sprint Status

Status: Complete.

Sprint 10A is complete as a deterministic, structured Prediction Framework
foundation. Future changes should be handled in Sprint 10B or a new explicitly
requested maintenance task.

## Completed Features

- Prediction Result schema foundation.
- Condition Engine foundation.
- Rule Engine foundation.
- Prediction Context Builder.
- Analyzer Adapter Interfaces.
- Prediction Composer foundation.
- Internal Kundali prediction framework integration.
- Optional Kundali API prediction framework exposure with
  `include_predictions`.
- Validation coverage.
- Regression coverage.

## Sprint Rules

- Predictions must be deterministic first.
- No AI-generated prediction text belongs inside the core engine.
- The core engine should return structured facts, reasons, evidence, and
  confidence metadata.
- A future AI layer may summarize structured output, but it must not mutate or
  recalculate deterministic results.
- All outputs must be JSON-safe.
- No completed calculation engines should be rewritten.
- Do not modify Panchang, Kundali, Varga, Dasha, Strength, Ashtakavarga, or
  Lagna behavior.
- Reuse existing calculation outputs and helper modules.
- Preserve backward compatibility for existing APIs.
- Keep prediction APIs optional and explicitly gated when exposure is requested.

## Architecture Direction

The Prediction Framework lives under `backend/app/prediction/`. It is layered
so deterministic calculation engines remain independent from prediction rules
and report text.

Expected architecture components:

- Rule Engine.
- Condition Engine.
- Prediction Context Builder.
- Planet Analyzer.
- House Analyzer.
- Yoga Analyzer.
- Dasha Adapter.
- Strength Adapter.
- Ashtakavarga Adapter.
- Prediction Composer.
- Report Builder.
- AI Summary Adapter placeholder.

## Component Responsibilities

### Rule Engine

The Rule Engine should evaluate registered deterministic rules against a
prediction context and return structured rule results. Rules should declare
their inputs, conditions, evidence, status, and reasons.

### Condition Engine

The Condition Engine should evaluate reusable boolean or scored conditions such
as planet placement, house ownership, dignity, aspect, dasha state, strength,
or bindu thresholds. Conditions should return JSON-safe outcomes rather than
free-form predictions.

### Prediction Context Builder

The Prediction Context Builder should gather relevant existing outputs into a
single immutable-style context for downstream analyzers. It should reuse
Kundali, Varga, Dasha, Strength, Ashtakavarga, and Special Lagna summaries
without recalculating or mutating them.

### Planet Analyzer

The Planet Analyzer should produce planet-wise structured facts from existing
planet position, dignity, lordship, relationship, combustion, retrograde,
strength, and aspect metadata.

### House Analyzer

The House Analyzer should produce house-wise structured facts from existing
Bhava, lordship, planet placement, and cusp metadata.

### Yoga Analyzer

The Yoga Analyzer should adapt existing deterministic yoga detectors into
prediction-ready evidence structures without changing yoga calculation logic.

### Dasha Adapter

The Dasha Adapter should expose Dasha timeline and current-period outputs as
structured timing context for rules. It should not change Dasha calculations.

### Strength Adapter

The Strength Adapter should expose Shadbala and Ishta/Kashta summaries as
structured strength context for rules. It should not change strength
calculations.

### Ashtakavarga Adapter

The Ashtakavarga Adapter should expose Bhinnashtakavarga and Sarvashtakavarga
summaries as structured bindu context for rules. It should not change
Ashtakavarga calculations.

### Prediction Composer

The Prediction Composer should combine rule results into stable grouped output
sections. It should preserve evidence and reason trails and avoid interpretive
prose until a future reporting layer is explicitly requested.

### Report Builder

The Report Builder should prepare deterministic report-shaped data from
composer output. It should not generate PDF, HTML, or AI-written summaries in
Sprint 10A unless a future task explicitly scopes that work.

### AI Summary Adapter Placeholder

The AI Summary Adapter is a boundary placeholder only. A later layer may use
structured prediction output to produce summaries, but the adapter must remain
outside the deterministic core and must never be required for calculation or
rule evaluation.

## Data Contract Direction

Prediction outputs should be JSON-safe dictionaries or typed models with stable
keys. Future schemas should prefer these fields where applicable:

- `id`
- `category`
- `status`
- `score`
- `confidence`
- `facts`
- `conditions`
- `evidence`
- `reasons`
- `source_components`
- `metadata`

Missing data should be represented with safe status and metadata fields rather
than hard failures unless an existing API validation pattern requires an error.

## Task Breakdown

### Task 10A.1 - Documentation

Goal: Define the Prediction Framework architecture before runtime work begins.

Acceptance checklist:

- [x] Sprint 10A document exists.
- [x] Master document points to Sprint 10A.
- [x] No runtime source code is changed.
- [x] Documentation-only checks are run if the repository defines them.

### Task 10A.2 - Prediction Result Schema Foundation

Goal: Add reusable JSON-safe result schemas for prediction facts, rules,
conditions, evidence, and metadata.

Acceptance checklist:

- [x] Result skeletons are reusable.
- [x] Missing-data results are JSON-safe.
- [x] No prediction text is generated.
- [x] Focused tests cover structure and invalid input behavior.

### Task 10A.3 - Condition Engine Foundation

Goal: Add reusable deterministic condition evaluation helpers.

Acceptance checklist:

- [x] Conditions return structured outcomes.
- [x] Invalid conditions fail safely.
- [x] Existing calculation engines are not modified.
- [x] Focused tests cover true, false, unknown, and invalid states.

### Task 10A.4 - Rule Engine Foundation

Goal: Add reusable rule registration and evaluation foundations.

Acceptance checklist:

- [x] Rules can declare identifiers, categories, inputs, and conditions.
- [x] Rule evaluation returns JSON-safe result structures.
- [x] Missing data produces safe placeholder results.
- [x] Focused tests cover valid and invalid rule evaluation.

### Task 10A.5 - Prediction Context Builder

Goal: Build a reusable context from existing deterministic chart outputs.

Acceptance checklist:

- [x] Context includes available Kundali, Varga, Dasha, Strength,
  Ashtakavarga, and Special Lagna data.
- [x] Missing optional data is represented safely.
- [x] Existing calculations are reused without mutation.
- [x] Focused tests cover complete and partial contexts.

### Task 10A.6 - Analyzer Adapter Interfaces

Goal: Define adapter interfaces for planet, house, yoga, dasha, strength, and
Ashtakavarga analyzers.

Acceptance checklist:

- [x] Adapter interfaces return structured facts.
- [x] Unsupported or missing source data fails safely.
- [x] Completed calculation engines are not rewritten.
- [x] Focused tests cover adapter output shape.

### Task 10A.7 - Prediction Composer Foundation

Goal: Combine deterministic rule and analyzer outputs into grouped prediction
sections.

Acceptance checklist:

- [x] Composer output is JSON-safe.
- [x] Evidence and reasons are preserved.
- [x] No AI-generated prose is emitted.
- [x] Focused tests cover ordering, grouping, and missing data.

### Task 10A.8 - Internal Kundali Integration

Goal: Integrate prediction framework output internally only when safe and
backward-compatible.

Acceptance checklist:

- [x] Integration is optional and internal.
- [x] Existing Kundali chart fields are preserved.
- [x] Missing prediction inputs fail safely.
- [x] Existing Kundali tests continue to pass.

### Task 10A.9 - Optional API Exposure

Goal: Expose prediction framework output only through an explicit opt-in flag
after internal structures are stable.

Acceptance checklist:

- [x] Default API responses remain backward-compatible.
- [x] Prediction output is gated by an explicit flag.
- [x] Response output remains JSON-safe.
- [x] API tests cover enabled and disabled behavior.

### Task 10A.10 - Validation and Regression

Goal: Add broad validation and regression coverage for framework outputs.

Acceptance checklist:

- [x] Invalid contexts, rules, conditions, and adapter inputs are covered.
- [x] JSON serialization safety is covered.
- [x] Backward compatibility for default Kundali/API behavior is covered.
- [x] Full relevant suite passes.

### Task 10A.11 - Documentation Completion

Goal: Complete Sprint 10A documentation after implementation milestones finish.

Acceptance checklist:

- [x] Completed features are listed.
- [x] Known limitations are documented.
- [x] Sprint completion checklist is added.
- [x] Master document points to the next sprint.

## Known Limitations

- No real prediction rules are implemented yet.
- No interpretation text is generated yet.
- AI summary layer is placeholder only.
- Framework output is structured and deterministic only.

## Known Non-Goals

- Predictive interpretation text is not implemented in Sprint 10A.
- AI-generated summaries are not implemented in the core engine.
- Real predictive rule libraries are not implemented in Sprint 10A.
- Report rendering is not implemented in Sprint 10A.
- Public API prediction output remains optional and explicitly gated.
- Existing calculation engines are not rewritten.

## Validation Checklist

For each Sprint 10A implementation milestone:

- [x] Existing Panchang tests pass.
- [x] Existing Kundali tests pass.
- [x] Existing Varga tests pass.
- [x] Existing Dasha tests pass.
- [x] Existing Strength tests pass.
- [x] Existing Ashtakavarga tests pass.
- [x] Existing Lagna tests pass.
- [x] New prediction framework tests cover valid, boundary, and invalid inputs.
- [x] JSON serialization safety is tested for new outputs.
- [x] API tests are added only when API behavior changes.
- [x] Full relevant suite passes before the milestone is marked complete.

## Sprint 10A Completion Checklist

- [x] Prediction Result schema foundation is implemented and tested.
- [x] Condition Engine foundation is implemented and tested.
- [x] Rule Engine foundation is implemented and tested.
- [x] Prediction Context Builder is implemented and tested.
- [x] Analyzer Adapter Interfaces are implemented and tested.
- [x] Prediction Composer foundation is implemented and tested.
- [x] Internal Kundali prediction framework integration is complete.
- [x] Optional Kundali API prediction framework exposure is complete with
      `include_predictions`.
- [x] Validation coverage is added.
- [x] Regression coverage is added.
- [x] Existing runtime behavior remains backward-compatible.
- [x] Framework output remains JSON-safe.
- [x] Real prediction rules and interpretation text remain out of scope.
- [x] Sprint 10A is ready to close.

## Stop Point

Stop after each requested Sprint 10A milestone is complete. Do not move from
framework architecture into prediction rule implementation without a new task.
