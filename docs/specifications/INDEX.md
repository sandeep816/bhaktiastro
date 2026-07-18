# Domain Specifications

This directory is the canonical home for permanent astrology and domain
behavior after that behavior is migrated and approved. Specifications own
inputs, normalization, formulas, output contracts, validation, boundaries,
serialization, compatibility, and explicit exclusions. They do not own Sprint
progress, branch instructions, implementation chronology, or broad
cross-cutting architecture decisions.

Completed Sprint documents remain preserved as historical execution records
while approved permanent specifications own migrated domain contracts.

## Planned Specification Register

| Identifier | Planned document | Migration state | Current source material |
| --- | --- | --- | --- |
| `SPEC-MATCHMAKING-001` | [MATCHMAKING.md](MATCHMAKING.md) | migrated; approved version 1.0 | [Sprint 11](../SPRINT-11.md) and completed runtime/tests |
| `SPEC-KUNDALI-001` | `KUNDALI.md` | pending migration | [Sprint 4](../KUNDALI_SPRINT_4.md) and later Kundali integrations |
| `SPEC-DASHA-001` | `DASHA.md` | pending migration | [Sprint 6](../SPRINT-06.md) |
| `SPEC-PANCHANG-001` | `PANCHANG.md` | pending migration | Sprints 1-3, [API](../API.md), and [accuracy notes](../ACCURACY.md) |
| `SPEC-PREDICTION-001` | `PREDICTION.md` | pending migration | [Sprint 10A](../SPRINT-10A.md), [Sprint 10B](../SPRINT-10B.md), and [rule architecture](../prediction_rules.md) |
| `SPEC-YOGAS-001` | `YOGAS.md` | pending migration | Kundali and prediction Sprint records |
| `SPEC-DOSHAS-001` | `DOSHAS.md` | pending migration | Domain implementations and completed Sprint records |
| `SPEC-TRANSITS-001` | `TRANSITS.md` | planned; no approved migration task | [Roadmap](../ROADMAP.md) |
| `SPEC-REPORTING-001` | [REPORTING.md](REPORTING.md) | approved version 1.0; runtime implemented | [Sprint 12](../SPRINT-12.md) |
| `SPEC-INTERPRETATION-001` | [INTERPRETATION.md](INTERPRETATION.md) | approved version 1.0; runtime implemented | [Sprint 13](../SPRINT-13.md) |
| `SPEC-API-STABILITY-001` | [API-STABILITY.md](API-STABILITY.md) | approved version 1.0; documentation foundation complete | [Sprint 14](../SPRINT-14.md) |
| `SPEC-GOLDEN-FIXTURES-001` | [GOLDEN-FIXTURES.md](GOLDEN-FIXTURES.md) | approved version 1.0; governance complete; fixture data not started | [Sprint 15](../SPRINT-15.md) |
| `SPEC-GOLDEN-REFERENCE-SOURCES-001` | [GOLDEN-REFERENCE-SOURCES.md](GOLDEN-REFERENCE-SOURCES.md) | approved version 1.0; source framework complete; source records not started | [Sprint 15](../SPRINT-15.md) |

`pending migration` means no permanent specification is approved yet. It does
not make this index a substitute for the current Sprint, runtime, or tests.
The Matchmaking migration is complete. Reporting version 1.0 is approved and
implemented as the Sprint 12 foundation. Interpretation version 1.0 is
approved and implemented as the Sprint 13 foundation. API Stability version
1.0 is the approved cross-cutting Sprint 14 documentation foundation; its
separately authorized future inventory and contract-test enforcement are not
started. Golden Fixture Governance version 1.0 is the approved Sprint 15
documentation foundation; no golden fixture data exists yet.
Golden Reference Source Framework version 1.0 defines the approved source,
trust, independence, provenance, and review contract; no source record or
reference dataset exists yet.

## Initial Migration Inventory

The audit establishing this index found intentional historical mixing that will
be separated gradually:

- `KUNDALI_SPRINT_4.md` combines completion history, module references, API
  behavior, Yoga rules, limitations, and validation evidence;
- `SPRINT-05.md` through `SPRINT-09.md` combine milestone progress with durable
  calculation, architecture, API, boundary, and regression decisions;
- `SPRINT-10A.md`, `SPRINT-10B.md`, and `prediction_rules.md` split Prediction
  architecture and permanent rule contracts across execution and domain files;
- `SPRINT-11.md` is the most complete source for Matchmaking but combines task
  history with permanent mappings, matrices, validation, serialization, and
  exhaustive test requirements; and
- `API.md`, `ACCURACY.md`, and `VALIDATION_PLAN.md` already serve durable
  focused purposes and must be linked or migrated carefully rather than
  absorbed wholesale.

All remain preserved and authoritative only according to the
[source-of-truth policy](../architecture/INDEX.md#source-of-truth-and-conflict-resolution)
until their focused migration tasks are complete.

## Specification Status Vocabulary

- `draft`: being assembled and not yet canonical;
- `approved`: reviewed and canonical for its declared scope;
- `deprecated`: still supported or retained, but not preferred for new work;
- `superseded`: replaced by a named later specification or version.

Migration state is tracked separately as `pending migration`, `in migration`,
or `migrated`. Ownership notes may label text `canonical`, `provisional`, or
`historical`. These terms must not be substituted for specification status.

## Standard Specification Format

Every specification begins with its stable identifier, title, status, version
or supersession reference, and owning domain. It then contains:

1. scope;
2. dependencies;
3. terminology;
4. inputs;
5. normalization;
6. calculation rules;
7. output contract;
8. validation rules;
9. boundary behavior;
10. serialization behavior;
11. backward compatibility;
12. explicit exclusions;
13. canonical test-vector references;
14. implementation references; and
15. change history and supersession policy.

Unknown or unverified behavior is labeled explicitly; it is never filled with
a guessed formula or example.

## Naming and Cross-Reference Standards

- Specification identifiers use `SPEC-<DOMAIN>-NNN`, remain stable if files
  move, and appear in the first heading or metadata block.
- Domain filenames use uppercase domain names such as `MATCHMAKING.md`.
- Sprint tasks are referenced as `Task 11.15` and linked to the corresponding
  heading, for example [Task 11.15](../SPRINT-11.md#task-1115---serialization-and-compatibility-hardening).
- ADRs are referenced by stable `ADR-NNN` identifiers.
- Test vectors are referenced by stable vector identifiers defined in the
  [test-vector index](../test-vectors/INDEX.md).
- Relative Markdown links are preferred for repository documents.

## Ownership and Update Rules

An approved specification is changed only through a focused documentation or
runtime task that states compatibility impact. Cross-cutting choices must link
to the governing [ADR](../architecture/INDEX.md). Examples must link to
canonical vectors rather than being copied throughout multiple documents.

New permanent rules are written once in the owning approved specification.
Sprint documents link to that rule. Existing Sprint text may remain during
migration because it is historical; temporary duplication requires reciprocal
links, an ownership note, and an explicit migration label. Historical Sprint
records are not retroactively rewritten to appear as if the new architecture
existed at the time.

## Gradual Migration Policy

The initial order is:

1. Matchmaking;
2. Kundali;
3. Dasha;
4. Panchang;
5. Prediction;
6. Yogas;
7. Doshas; and
8. Transits.

This order starts with the recently completed, fully documented Matchmaking
contract, then follows its main chart dependencies. Reporting is now an
approved, independently governed Sprint 12 foundation and does not alter that
domain-migration order. API Stability is a cross-cutting approved Sprint 14
contract. Golden Fixture Governance and Golden Reference Source Governance are
cross-domain approved Sprint 15 contracts. None alters the migration order.

Each migration is one focused task that must:

1. inspect current runtime implementation;
2. inspect automated tests and existing vectors or fixtures;
3. inspect all relevant Sprint specifications and supporting documents;
4. identify the actually accepted contract and record discrepancies;
5. create or update one permanent domain specification;
6. add references to canonical test vectors without inventing expected values;
7. replace duplicated Sprint details with links only when safe, while
   preserving historical records; and
8. avoid runtime changes unless a separate runtime bug-fix task is approved.

If documents, tests, and runtime disagree, follow the conflict process in the
[architecture index](../architecture/INDEX.md#source-of-truth-and-conflict-resolution).
