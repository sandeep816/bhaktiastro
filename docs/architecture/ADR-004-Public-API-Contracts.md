# ADR-004: Public API Contracts

- Status: `accepted`
- Adoption reference: Documentation Architecture Foundation after Sprint 11
- Supersedes: None
- Superseded by: None

## Context

Public Python imports and HTTP/structured outputs are consumed across completed
domains. Silent signature, ordering, or container changes can break callers
even when numerical calculations are unchanged.

## Decision

Public changes are additive by default. Stable exports, parameter meaning,
keyword-only contracts where adopted, field identifiers, deterministic order,
and schema versions are preserved. Runtime result snapshots are immutable by
public ownership contract where adopted. Serialization returns fresh,
caller-owned mutable built-in collections when that is the documented boundary.
Removal or incompatible change requires deprecation before removal, an approved
migration plan, and a deliberate version decision. Schema versions change only
for reviewed contract evolution, never automatically.

## Rationale

Explicit compatibility rules let the project evolve without forcing downstream
consumers to inspect implementation details.

## Consequences

- New exports cannot rename or remove existing exports incidentally.
- Mapping/list ordering is contractual when documented.
- Serialization does not mutate runtime results or share mutable paths.
- Deprecation and schema migration are separate reviewed work.

## Alternatives Considered

- Unversioned breaking changes: rejected because consumers cannot coordinate.
- Returning frozen containers everywhere: rejected as a blanket rule because
  it can break existing callers.
- Shallow serialization copies: rejected because nested mutation leaks across
  ownership boundaries.

## Compatibility Impact

This ADR is additive governance only and changes no current public contract.

## Related Specifications

- [Specifications index](../specifications/INDEX.md)
- Reporting specification is planned when Sprint 12 begins.
