# Sprint 13 - Interpretation Data Boundary

Status: Complete

Primary permanent contract:
[SPEC-INTERPRETATION-001](specifications/INTERPRETATION.md)

## Sprint purpose

Sprint 13 establishes a strict domain-neutral boundary between validated,
already-computed astrology results and future human-readable interpretation.
It begins with an immutable structured finding and evidence contract. It does
not calculate astrology, generate prose, render reports, or call AI systems.

## Sequencing decision

[ROADMAP.md](ROADMAP.md) defines the exact milestone title **Sprint 13 -
Interpretation Data Boundary** and places it immediately after completed
Sprint 12. Sprint 12 contains only completed Task 12.1; no approved Task 12.2
exists. The repository audit found no existing Sprint 13 task number or
materially different active scope.

The legacy `PROJECT_PHASES.md` Phase 13 backlog is historical and superseded
for current milestone sequencing by ROADMAP and MASTER. It does not rename or
authorize this Sprint.

## Dependencies

- [Architecture decisions](architecture/INDEX.md) govern separation,
  validation, compatibility, and testing.
- [Sprint 10A](SPRINT-10A.md), [Sprint 10B](SPRINT-10B.md), and the existing
  Prediction runtime provide historical structured-result evidence but remain
  unchanged and are not forcibly migrated.
- [SPEC-MATCHMAKING-001](specifications/MATCHMAKING.md) remains the completed
  Sprint 11 domain contract.
- [SPEC-REPORTING-001](specifications/REPORTING.md) and completed
  [Sprint 12](SPRINT-12.md) remain the report-model contract and runtime.
- Interpretation may later feed a separately specified Reporting adapter, but
  Task 13.1 implements neither that adapter nor rendering.

## Task sequence

Only Task 13.1 is approved. No Task 13.2 or later Sprint 13 task is named or
authorized by this document.

## Task 13.1 - Interpretation Data Boundary Foundation

Status: Complete

### Documentation outcome

Task 13.1 approves
[SPEC-INTERPRETATION-001](specifications/INTERPRETATION.md) as the permanent
source of truth for:

- eight strict immutable models for documents, subject references, findings,
  evidence, issues, sources, metadata, and versioned rule references;
- technical `complete`, `incomplete`, and `invalid` states with explicit
  diagnostic partial-data behavior and no silent partial success;
- domain-neutral findings with a separate limited tendency vocabulary;
- stable evidence references to validated source fields without embedding
  arbitrary runtime results;
- explicit deferral of universal strength and confidence;
- deterministic ordering, strict validation, fresh JSON-safe serialization,
  schema `bhaktiastro.interpretation.document` version `1.0`, and an additive
  future public API plan; and
- complete separation from calculation, rule evaluation, narrative, AI,
  Reporting adaptation, rendering, persistence, and transport.

Detailed fields, vocabularies, validation, serialization, tests, versioning,
and exclusions live only in the permanent specification.

### Runtime status

The approved foundation is implemented under `backend/app/interpretation/`
with the exact eight immutable models, six vocabularies/constants, eight
keyword-only factories, three strict validators, one root serializer, and the
documented additive public exports. Runtime values use tuples and mapping
proxies; serialization returns deterministic, deeply independent built-in
dictionary/list trees compatible with `json.dumps(..., allow_nan=False)`.

Focused coverage lives in:

- `backend/tests/test_interpretation_models.py`;
- `backend/tests/test_interpretation_validation.py`;
- `backend/tests/test_interpretation_serialization.py`; and
- `backend/tests/test_interpretation_public_api.py`.

Verification at completion:

- focused Interpretation suite: `83 passed`;
- Reporting regression suite: `72 passed`;
- Prediction regression suite: `111 passed`;
- Matchmaking regression suite: `2639 passed`;
- complete project suite: `3762 passed, 13 skipped, 20 subtests passed`;
- the 13 skips remain the documented manual astronomical-reference cases;
- Python compilation, public import, and strict JSON serialization smoke checks
  passed;
- Black formatting checks passed using the existing project environment; and
- Ruff was unavailable and was not installed.

### Runtime completion criteria

The completed runtime task:

1. implemented only the approved models, constants, factories, validators, and
   root serializer;
2. preserved every Sprint 10, Sprint 11, Sprint 12, domain, serializer, API,
   and public import contract;
3. added the focused model, validation, serialization, mutation, ordering,
   import, and dependency-regression tests required by the specification;
4. passed focused tests, Sprint 10, Reporting, Matchmaking, and full regressions,
   plus configured formatting, compilation, import, and diff checks; and
5. updated this execution status only after the implementation contract was
   complete.

## Stop point

Task 13.1 and Sprint 13 are complete. No Task 13.2 is documented or opened by
this implementation. Stop without creating domain adapters or rule libraries,
generating interpretation or prediction text, adapting findings to Reporting,
rendering content, or assigning a later task number without a new approved
request. The next roadmap milestone is Sprint 14 - API Versioning and Stability.
