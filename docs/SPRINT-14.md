# Sprint 14 - API Versioning and Stability

Status: Complete

Primary permanent contract:
[SPEC-API-STABILITY-001](specifications/API-STABILITY.md)

## Sprint purpose

Sprint 14 establishes conservative, explicit compatibility governance for
BhaktiAstro public contracts. It defines what is public, how changes are
classified, how Python APIs and serialized schemas remain stable, how
deprecation and breaking changes are governed, and which future contract tests
must enforce those promises.

It changes no runtime behavior. It does not create a compatibility library,
change a calculation, alter an export, revise a schema, or begin release
automation.

## Source-of-truth and sequencing decision

[ROADMAP.md](ROADMAP.md) defines the exact milestone title **Sprint 14 - API
Versioning and Stability** and places it after completed Sprint 13. Sprint 13
contains only completed Task 13.1; no Task 13.2 exists.

The repository audit found no pre-existing Sprint 14 task sequence or
conflicting current title. Historical phase labels do not rename or authorize
this Sprint. The accepted source-of-truth hierarchy and conflict-resolution
process in the [architecture index](architecture/INDEX.md) remain controlling.

## Dependencies

- [ADR-001](architecture/ADR-001-Project-Principles.md) requires incremental,
  additive module evolution and an approved migration for breaking changes.
- [ADR-002](architecture/ADR-002-Astrology-Calculation-Standards.md) continues
  to own deterministic calculation and normalization rules; Task 14.1 changes
  none of them.
- [ADR-003](architecture/ADR-003-Validation-Standards.md) requires strict trust
  boundaries without silent coercion or repair.
- [ADR-004](architecture/ADR-004-Public-API-Contracts.md) owns public names,
  signatures, model shapes, immutable ownership, serializer behavior,
  deprecation, and schema-version decisions.
- [ADR-005](architecture/ADR-005-Testing-Standards.md) requires focused
  contract and regression evidence.
- [SPEC-MATCHMAKING-001](specifications/MATCHMAKING.md),
  [SPEC-REPORTING-001](specifications/REPORTING.md), and
  [SPEC-INTERPRETATION-001](specifications/INTERPRETATION.md) own their current
  approved public contracts and schema families.
- Completed Sprint records and existing tests/runtime remain authoritative for
  domains whose permanent migration is pending; Task 14.1 does not rewrite
  them.

## Task sequence

Task 14.1 is the sole approved and completed Sprint 14 task. No Task 14.2 is
assigned. Runtime inventory, compatibility tooling, warnings, shims, and
contract tests remain separately authorized future work rather than Sprint 14
completion criteria.

## Task 14.1 - API Versioning and Stability Foundation

Status: Complete - documentation only

### Documentation outcome

Task 14.1 approves
[SPEC-API-STABILITY-001](specifications/API-STABILITY.md) version 1.0 as the
permanent source of truth for:

- the exact public/private contract boundary;
- the compatibility categories `additive_compatible`,
  `contract_clarification`, `deprecated_supported`, `breaking`, and
  `internal_only`;
- stability of Python imports, exports, signatures, strict models, factories,
  validators, serializers, schemas, vocabularies, identifiers, errors, and
  deterministic ordering;
- deliberate schema-version evolution without silent upgrade, downgrade,
  fallback, negotiation, or repair;
- a minimum deprecation window of two subsequent published project releases
  and 90 calendar days, whichever ends later;
- explicit breaking-change review, migration, version, documentation,
  changelog, and test requirements;
- distinct responsibilities for project/package, application, schema,
  artifact/domain, and rule versions;
- a future public-contract inventory record and contract-test plan; and
- domain-by-domain application without retroactive migration or behavioral
  change.

The complete rules live only in the permanent specification.

### Current contract baseline

Task 14.1 records, but does not modify, these canonical emitted schema
versions:

- Matchmaking: `bhaktiastro.matchmaking` version `1.0`;
- Reporting: `bhaktiastro.reporting.document` version `1.0`; and
- Interpretation: `bhaktiastro.interpretation.document` version `1.0`.

The project/package version and the application's configured default version
are currently `0.1.0`, but remain independently owned by project metadata and
application configuration. No version value is changed by this task.

### Validation and review requirements

The documentation task must verify:

1. Sprint 13 completion and Sprint 14 milestone sequencing;
2. all accepted ADRs and the documentation source-of-truth hierarchy;
3. current approved Matchmaking, Reporting, and Interpretation contracts;
4. actual package exports, exact model/serializer commitments, schema
   identifiers and versions, and existing contract-test conventions;
5. pending-migration treatment for Kundali, Panchang, Dasha, and Prediction;
6. cross-document links, headings, and specification-index registration;
7. Markdown-only scope and absence of runtime/test/public-export changes;
8. `git diff --check`, staged diff review, and clean working tree after commit.

### Explicit exclusions

Task 14.1 does not:

- implement runtime code, tests, warnings, aliases, shims, registries, or
  release tooling;
- change any public import, callable, model, schema, vocabulary, identifier,
  serializer, validation behavior, error, or ordering contract;
- change Kundali, Panchang, Dasha, Prediction, Matchmaking, Reporting, or
  Interpretation behavior;
- define REST URL versioning, persistence migration, PyPI publishing, package
  installation, or deployment policy; or
- begin an unnamed Task 14.2.

## Stop point

Task 14.1 and Sprint 14 are complete. The approved permanent governance
contract and navigation updates are committed, and no additional approved
completion criterion remains. No Task 14.2 is created merely to close the
Sprint.

Future public-contract inventory, runtime enforcement, compatibility tooling,
warnings, shims, and contract tests remain deferred until separately defined
and authorized. Their deferral does not imply implementation and is not a
Sprint 14 blocker. The sequencing gate is released for Sprint 15 - Golden
Fixture Expansion without beginning any of that future API-stability work.
