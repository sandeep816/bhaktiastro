# ADR-001: Project Principles

- Status: `accepted`
- Adoption reference: Documentation Architecture Foundation after Sprint 11
- Supersedes: None
- Superseded by: None

## Context

BhaktiAstro contains interdependent astronomical, chart, prediction, and
matchmaking domains. Broad changes or duplicated helpers would make formulas
and public contracts difficult to verify.

## Decision

Work proceeds through small incremental tasks with one focused commit. Reuse
existing modules, constants, validation, and calculation utilities. Do not
duplicate functionality, perform unrelated refactors, or begin later work
early. Preserve backward compatibility and deterministic behavior. Use a
documentation-first workflow when a task introduces or chooses a domain
contract, and keep implementation, verification, and progress updates scoped
to that contract.

## Rationale

Small, explicit changes make astrology decisions reviewable, regressions easier
to isolate, and repository history useful as an audit trail.

## Consequences

- A large feature is split into independently reviewable tasks.
- Existing behavior is inspected before new abstractions are added.
- One task stops before the next task begins.
- Intentional breaking changes require an approved decision and migration plan.

## Alternatives Considered

- Broad domain rewrites: rejected because they obscure formula and contract
  changes.
- Copying helpers into each feature: rejected because rules would diverge.
- Combining multiple tasks in one commit: rejected because review and rollback
  become ambiguous.

## Compatibility Impact

This ADR formalizes existing practice and changes no runtime or public API.

## Related Specifications

- [Specifications index](../specifications/INDEX.md)
- Domain specifications are pending gradual migration.
