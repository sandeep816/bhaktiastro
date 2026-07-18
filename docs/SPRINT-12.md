# Sprint 12 - Report Data Model Foundation

Status: Active

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

Status: Specification complete; runtime not started

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

### Runtime implementation requirements

The next implementation task must:

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

The Task 12.1 permanent specification is complete. Runtime code, tests, and
public exports have not started. The next incomplete task is the Task 12.1
runtime implementation against `SPEC-REPORTING-001`; no Task 12.2 scope is
opened by this documentation commit.
