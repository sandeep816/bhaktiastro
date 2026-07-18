# Sprint 12 - Report Data Model Foundation

Status: Complete

Primary permanent contract:
[SPEC-REPORTING-001](specifications/REPORTING.md)

## Sprint purpose

Sprint 12 establishes a domain-neutral, calculation-free foundation for
representing deterministic structured reports. It begins with the immutable
model and serialization contract in Task 12.1. Domain adapters, report-family
composition, rendering, interpretation, and delivery remain later work.

Sprint 11 is complete and remains governed by
[SPEC-MATCHMAKING-001](specifications/MATCHMAKING.md). This Sprint does not
migrate, wrap, or change any Sprint 11 result.

## Source-of-truth and sequencing decision

The current [Roadmap](ROADMAP.md) and [Master working document](MASTER.md)
consistently define **Sprint 12 - Report Data Model Foundation** and
**Task 12.1 - Report Data Model Foundation**. They own current navigation and
milestone sequencing under the accepted
[documentation hierarchy](architecture/INDEX.md#source-of-truth-and-conflict-resolution).

`PROJECT_PHASES.md` is a historical Phase-based planning artifact. Its
“Phase 12 - Web UI MVP” and “Task 12.1 - Kundali Input Form” labels are
superseded for current Sprint numbering and execution; they do not rename this
Sprint or authorize Kundali Input Form work. The historical text is retained,
with a narrow ownership note in that document rather than a broad rewrite.

## Task 12.1 - Report Data Model Foundation

Status: Complete

### Documentation outcome

Task 12.1 approves
[SPEC-REPORTING-001](specifications/REPORTING.md) as the permanent source of
truth for:

- eight immutable domain-neutral models: `ReportDocument`, `ReportSubject`,
  `ReportSection`, `ReportBlock`, `ReportField`, `ReportIssue`,
  `ReportMetadata`, and `ReportSource`;
- a single discriminated `ReportBlock` with seven closed, strictly validated
  payload kinds;
- the technical statuses `complete`, `incomplete`, and `invalid`;
- explicit diagnostic partial-report behavior without silent partial success;
- stable caller order for subjects, sections, blocks, fields, sources, issues,
  warnings, and notes;
- strict finite, JSON-safe value validation and fresh mutable serialization;
- Reporting schema identifier `bhaktiastro.reporting.document` and schema
  version `1.0`; and
- a future additive `backend.app.reporting` API made only of explicit
  factories, strict validators, and one document serializer.

The detailed field order, block payload contracts, validation behavior,
versioning rules, public signatures, test requirements, and exclusions live
only in the permanent specification.

### Approved runtime implementation requirements

The runtime implementation was required to:

1. implement only the approved Reporting models, constants, factories,
   validators, and serializer;
2. preserve all existing public APIs and direct domain result contracts;
3. add focused model, validation, serialization, mutation-safety, ordering,
   import, and backward-compatibility tests required by the specification;
4. run focused tests and the complete regression suite plus configured
   formatting, compilation, import, and diff checks;
5. update this execution record, `MASTER.md`, and `CHANGELOG.md` only after the
   runtime contract is complete; and
6. stop without beginning any later Sprint task.

### Runtime outcome

Task 12.1 implements the approved contract in `backend/app/reporting/` with:

- the eight frozen, slotted, deliberately unhashable model types;
- immutable tuple and mapping-proxy nested ownership;
- the exact seven closed block kinds and payload schemas;
- eight keyword-only factories, three strict runtime-model validators, and one
  canonical document serializer;
- strict identifier, version, status, issue, duplicate, finite-number, cycle,
  alias, and kind-specific payload validation;
- fresh deterministic JSON-safe serialization with exact field order and deep
  mutation isolation; and
- explicit package exports without importing or changing Matchmaking.

Focused coverage lives in:

- `backend/tests/test_reporting_models.py`;
- `backend/tests/test_reporting_validation.py`;
- `backend/tests/test_reporting_serialization.py`; and
- `backend/tests/test_reporting_public_api.py`.

Verification at completion:

- focused Reporting suite: `72 passed`;
- complete Matchmaking regression suite: `2639 passed`;
- complete project suite: `3679 passed, 13 skipped, 20 subtests passed`;
- the 13 skips remain the documented manual astronomical-reference cases;
- Reporting import, JSON serialization, and Python compilation smoke checks
  passed;
- Black formatting checks passed using the existing project environment; and
- Ruff was unavailable and was not installed.

### Explicit exclusions

Task 12.1 does not include:

- astrology calculation, domain-specific composition, interpretation,
  prediction, recommendation, scoring, or result mutation;
- Matchmaking, Kundali, Panchang, Dasha, Prediction, Yoga, Dosha, Transit, or
  other domain adapters;
- HTML, Markdown, PDF, UI, email, image, chart, template, or layout rendering;
- API endpoints, persistence, ORM models, transport schemas, localization,
  telemetry, or network behavior;
- migration of any Sprint 11 result into the new model; or
- Task 12.2 or another later task.

## Current stop point

Task 12.1 and Sprint 12 are complete. No Task 12.2 is documented or opened by
this implementation. The next incomplete roadmap milestone is Sprint 13 -
Interpretation Data Boundary; its detailed task specification is not defined
or implemented here.
