# Sprint 15 - Golden Fixture Expansion

Status: In progress - Task 15.1 documentation complete; fixture data and tests
not started

Primary permanent contract:
[SPEC-GOLDEN-FIXTURES-001](specifications/GOLDEN-FIXTURES.md)

## Sprint purpose

Sprint 15 expands independently verified reference coverage without treating
generated snapshots as astronomical truth. Its first task defines what a
golden fixture is, how provenance and tolerances are reviewed, how timezone and
DST cases are represented, and how future fixture data relates to canonical
test vectors and pytest artifacts.

Task 15.1 creates no fixture value, test, validator, runtime behavior, or
calculation change.

## Source-of-truth and sequencing decision

[ROADMAP.md](ROADMAP.md) defines the exact milestone title **Sprint 15 - Golden
Fixture Expansion** after Sprint 14. The repository contained no `SPRINT-15.md`,
Task 15 number, or competing task sequence before this task.

[Sprint 14](SPRINT-14.md) is complete with its sole approved Task 14.1. Runtime
public-contract inventory and contract-test enforcement remain separately
authorized future work under
[SPEC-API-STABILITY-001](specifications/API-STABILITY.md); they were never a
Sprint 14 completion criterion and are not silently opened here.

The legacy `PROJECT_PHASES.md` phase backlog is historical and does not rename
Sprint 15. Its claim that a Jodhpur golden fixture is verified conflicts with
current Accuracy, Validation Plan, fixture tests, and ADR-005 evidence; the
current files remain structural and pending.

## Dependencies

- Completed Sprints 1 through 3 provide Astronomy, Panchang, API, existing
  structural fixtures, and validation documentation.
- Completed Sprint 4 provides the base Kundali output whose future fixture
  structure may be covered.
- The Documentation Architecture Foundation owns source hierarchy and
  canonical test-vector governance.
- ADR-002 owns explicit astronomical conventions and deterministic boundaries.
- ADR-003 owns strict validation and no silent coercion or repair.
- ADR-004 and API Stability own schema and compatibility evolution.
- ADR-005, [Accuracy](ACCURACY.md), and the
  [Validation Plan](VALIDATION_PLAN.md) prohibit invented values and keep
  unverified accuracy tests skipped.

## Roadmap milestone scope

The exact milestone-level areas remain:

- Mumbai fixture;
- London DST fixture;
- New York DST fixture;
- Kundali fixture structure; and
- manual reference documentation.

Task 15.1 governs these areas but implements none of them.

## Approved task sequence

Only Task 15.1 is approved. No runtime fixture task or Task 15.2 number is
authorized by this document.

## Task 15.1 - Golden Fixture Governance and Reference Specification

Status: Complete - documentation only

### Documentation outcome

Task 15.1 approves
[SPEC-GOLDEN-FIXTURES-001](specifications/GOLDEN-FIXTURES.md) version `1.0` as
the permanent source of truth for:

- four closed fixture classifications: `structural`, `regression`,
  `provisional_reference`, and `golden`;
- a strict source/review/activation lifecycle;
- schema `bhaktiastro.golden-fixture` version `1.0` and stable versioned fixture
  identifiers;
- complete location, timezone, time, calendar, configuration, expected-value,
  tolerance, provenance, and review records;
- exact DST treatment for valid, ambiguous, and nonexistent local times;
- per-fixture calculation scope rather than requiring every output;
- future Mumbai, London, New York, and Kundali selection/structure rules without
  dates or values;
- separate human-vector, machine-fixture, pytest, and evidence storage roles;
- strict failure handling and prohibition on regenerating expected data from
  current runtime; and
- future schema, provenance, timezone, tolerance, immutability, and calculation
  regression tests.

### Existing evidence classification

The existing Jodhpur and Delhi Panchang JSON files remain pre-schema
`structural` fixtures with verification status `pending`. They were generated
from current API output, have no independent source/version and comparison
record, lack approved per-field tolerances and reviewer/date evidence, and are
not promoted by this task.

The repository has thirteen accuracy-related skips: one exact structural-
fixture equality test and twelve manual-reference placeholders. They remain
skipped until separately authorized fixture work satisfies the permanent
specification and updates the Validation Plan.

### Completion criteria

Task 15.1 is complete when:

1. Sprint 14 is safely closed without inventing Task 14.2;
2. permanent Golden Fixture governance and Sprint 15 execution ownership are
   approved and indexed;
3. Jodhpur, Delhi, and all manual-reference skips are classified accurately;
4. no expected value, fixture, test, skip state, runtime, public API, or
   calculation changes;
5. cross-document links, anchors, Markdown scope, and diff checks pass; and
6. one focused documentation commit leaves a clean working tree.

## Proposed future sequence - not approved

The following unnumbered order mirrors the ROADMAP and is planning context
only. Each area requires a separately authorized documentation/evidence and
fixture/test task before work begins:

1. source and review a Mumbai non-DST reference fixture;
2. source and review London standard, daylight, and transition cases;
3. source and review New York standard, daylight, and transition cases;
4. approve and populate a base Kundali fixture under the defined structure;
5. complete manual comparison records and activate only qualifying golden
   fixtures.

This list assigns no task numbers, dates, expected values, tolerances, or
implementation authority.

## Explicit exclusions

Task 15.1 does not create or change:

- fixture data, canonical expected values, external evidence, or screenshots;
- runtime code, tests, skipped tests, pytest helpers, or public exports;
- astronomical, Panchang, timezone, DST, Kundali, or API behavior;
- approved numerical tolerances;
- interpretation rules, Reporting adapters, rendering, or user interfaces; or
- Sprint 16 work.

## Stop point

Task 15.1 stops after the documentation commit. No later Sprint 15 task is
approved. The next implementation area is only proposed and must not begin
without a task contract, independent sources, and explicit authorization.
