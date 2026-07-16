# Sprint 11 - Matchmaking Foundation

Sprint 11 establishes deterministic compatibility infrastructure that consumes
reusable birth and Kundali data. It keeps matchmaking calculations separate
from astrology calculation engines and from future API, reporting, and UI
layers.

## Sprint Status

Status: **In Progress (Task 11.2 Complete)**

## Architecture Boundary

```text
Birth details
    -> Kundali calculations
    -> Reusable matchmaking inputs
    -> Deterministic compatibility calculators
    -> Structured matchmaking result
    -> Future API / reports / UI
```

Matchmaking components must consume existing astrology output where available.
They must not mutate or recalculate Kundali data, generate predictions or
advice, call AI or external services, or include presentation formatting.

## Task 11.1 - Matchmaking Foundation Architecture

Status: **Complete**

Task 11.1 provides only:

- JSON-safe person and ordered-pair input structures.
- A stable, unevaluated matchmaking result structure.
- Deterministic empty and populated factories.
- Safe text, numeric, collection, and metadata normalization.
- Public foundation exports and focused contract tests.

No compatibility score, Koota rule, Manglik rule, judgment, interpretation,
remedy, API route, report, or UI behavior is implemented.

## Task 11.2 - Matchmaking Input Validation

Status: **Complete**

Task 11.2 adds deterministic validation over the Task 11.1 person and pair
factories. It provides:

- JSON-safe validation results and localization-ready issue keys.
- Stable issue codes and deterministic issue ordering.
- Optional ISO date, ISO time, and IANA timezone validation.
- Latitude (`-90..90`), longitude (`-180..180`), and Nakshatra Pada (`1..4`)
  boundary validation when those values are supplied.
- Strict unknown-field handling consistent with existing project schemas.
- Ordered nested pair validation and duplicate non-empty person ID detection.
- Normalized Task 11.1 person and pair values without input mutation.

All person fields remain optional. Validation does not calculate missing Rashi,
Nakshatra, Lagna, compatibility factors, or scores. It produces no API errors,
UI messages, interpretations, or judgments.

Compatibility is preserved by leaving Task 11.1 models and factories unchanged
and exposing validation as a separate opt-in layer.

Verification for Task 11.2:

- Matchmaking foundation and validation tests: 60 passed.
- Rashi, Nakshatra, and Kundali regression tests: 51 passed.
- Full suite: 1028 passed, 13 skipped, and 20 subtests passed.

## Deterministic and Compatibility Principles

- Inputs and nested collections are copied rather than mutated or shared.
- Person order is preserved without gender-based assumptions.
- Derived astrology fields remain optional and are never calculated here.
- Non-finite values are converted to JSON-safe values.
- Stable schemas and public imports must remain backward-compatible as the
  sprint grows.
- Calculation completion is explicit; empty results remain `not_evaluated`.

## Provisional Task Sequence

- 11.1 Matchmaking foundation architecture. **Complete.**
- 11.2 Matchmaking input validation. **Complete.**
- 11.3 Nakshatra compatibility foundations.
- 11.4 Varna Koota.
- 11.5 Vashya Koota.
- 11.6 Tara Koota.
- 11.7 Yoni Koota.
- 11.8 Graha Maitri Koota.
- 11.9 Gana Koota.
- 11.10 Bhakoot Koota.
- 11.11 Nadi Koota.
- 11.12 Ashtakoota aggregation.
- 11.13 Manglik compatibility foundation.
- 11.14 Matchmaking summary composer.
- 11.15 Serialization and compatibility hardening.

This sequence is provisional and may be adjusted after repository and source
inspection for each task. Tasks 11.2 onward are not implemented by Task 11.1.

## Non-Goals

- Full matchmaking or Ashtakoota calculation.
- Compatibility labels or final marriage judgments.
- Interpretive prose, marriage advice, remedies, or AI output.
- Changes to completed calculation, prediction, API, report, or UI modules.
