# Architecture Decision Records

This directory records accepted cross-cutting decisions for BhaktiAstro. ADRs
explain why the project follows a durable architectural rule. They do not own
domain formulas, scoring tables, API examples, test fixtures, or Sprint status.

## ADR Register

| ADR | Status | Summary |
| --- | --- | --- |
| [ADR-001: Project Principles](ADR-001-Project-Principles.md) | accepted | Incremental, deterministic, reusable, backward-compatible delivery. |
| [ADR-002: Astrology Calculation Standards](ADR-002-Astrology-Calculation-Standards.md) | accepted | Cross-domain normalization, boundary, reference-point, and layer rules. |
| [ADR-003: Validation Standards](ADR-003-Validation-Standards.md) | accepted | Strict deterministic validation without silent coercion or repair. |
| [ADR-004: Public API Contracts](ADR-004-Public-API-Contracts.md) | accepted | Additive evolution, stable exports, ordering, serialization, and deprecation. |
| [ADR-005: Testing Standards](ADR-005-Testing-Standards.md) | accepted | Focused, boundary, invalid-input, regression, and verification practices. |

These ADRs document practices already established by completed work. Their
adoption reference is the Documentation Architecture Foundation completed
after Sprint 11 and before Sprint 12.

## ADR Status Vocabulary

- `proposed`: under review and not yet binding;
- `accepted`: approved and binding for affected work;
- `superseded`: replaced by a named later ADR;
- `deprecated`: retained for compatibility or history but discouraged for new
  work.

Status terms are lowercase in registers and metadata. Historical prose may use
ordinary capitalization, but it must not imply a different state.

Sprint task status uses a separate execution vocabulary:

- `not_started`: scope may be planned, but work has not begun;
- `specification_complete`: the task contract is approved but runtime work is
  not complete;
- `in_progress`: authorized task work is underway;
- `blocked`: work cannot proceed until a named dependency or decision is
  resolved; and
- `complete`: all task-specific completion criteria are satisfied.

Historical Sprint status wording is preserved. New Sprint documents should map
their displayed status unambiguously to this vocabulary. ADR, specification,
test-vector verification, and Sprint execution statuses are not interchangeable.

## Standard ADR Format

Every ADR uses a stable identifier `ADR-NNN` and contains:

1. title and identifier;
2. status;
3. stable adoption reference;
4. context;
5. decision;
6. rationale;
7. consequences;
8. alternatives considered;
9. compatibility impact;
10. related specifications; and
11. `Supersedes` and `Superseded by` references.

Use `None` when a relationship is absent. ADR identifiers do not change if a
file moves. Filenames use `ADR-NNN-Title-In-Title-Case.md`.

## Proposal and Supersession Process

Create one focused documentation task for a proposed decision. The task must
identify affected specifications, APIs, tests, and compatibility constraints.
Review changes before marking the ADR `accepted`. A later decision does not
rewrite the old ADR: it names the old identifier in `Supersedes`, changes the
old ADR to `superseded`, and links both directions. Deprecation likewise keeps
the record and explains the supported transition.

Domain behavior belongs in [domain specifications](../specifications/INDEX.md).
Concrete examples and boundary cases belong in [test vectors](../test-vectors/INDEX.md).

## Documentation Responsibilities

- [MASTER.md](../MASTER.md) is concise navigation and current status.
- [ROADMAP.md](../ROADMAP.md) owns milestone sequence and high-level scope.
- Sprint documents own execution history, task progress, dependencies, and
  completion criteria.
- Accepted ADRs own cross-cutting architectural decisions.
- Approved domain specifications own permanent domain behavior.
- Canonical test vectors own reviewed human-readable examples and boundaries.
- Runtime modules and automated tests implement and verify approved contracts;
  they do not silently redefine them.
- Runtime implementation details stay with source code, module documentation,
  and automated tests. Specifications link to those locations instead of
  copying implementation internals into governance documents.

## Source-of-Truth and Conflict Resolution

The authority order is:

1. accepted ADRs for cross-cutting architecture;
2. approved domain specifications for permanent domain behavior;
3. canonical normative test vectors for reviewed examples of that behavior;
4. active Sprint specifications for approved work not yet migrated to a
   permanent specification;
5. automated tests as executable verification;
6. runtime implementation as the shipped behavior;
7. `MASTER.md` and `ROADMAP.md` for navigation, status, and sequencing only.

Historical completed Sprint documents remain evidence of the decision context.
For a domain still marked `pending migration`, its completed Sprint contract,
tests, and runtime must be audited together before a permanent specification is
approved. None may be silently selected merely because it is convenient.

When any layer disagrees:

- do not silently resolve, repair, or suppress the discrepancy;
- do not change runtime solely to match an unreviewed document;
- do not edit documentation solely to hide an implementation defect;
- record and resolve the discrepancy through one focused task and, when the
  decision is architectural, an ADR;
- update the owning specification, canonical vectors, tests, and runtime as
  explicitly authorized by that task; and
- preserve historical Sprint and superseded ADR records.

Permanent rules are migrated, not copied. Temporary duplication is allowed
only while migration is in progress and must include reciprocal links, an
ownership note, and an explicit `canonical`, `provisional`, `historical`, or
`pending migration` label.
