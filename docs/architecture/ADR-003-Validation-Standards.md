# ADR-003: Validation Standards

- Status: `accepted`
- Adoption reference: Documentation Architecture Foundation after Sprint 11
- Supersedes: None
- Superseded by: None

## Context

BhaktiAstro accepts both raw user inputs and precomputed structured results.
Treating those trust boundaries as interchangeable can silently coerce bad data
or conceal an inconsistent calculation result.

## Decision

Validation is strict, deterministic, and appropriate to its trust boundary.
Raw-input validation may normalize only behavior explicitly declared by the
owning contract. Strict precomputed-result validation checks exact types,
identifiers, ordering, ranges, metadata, and cross-field consistency without
silent coercion, guessing, or repair. Booleans are rejected as numbers where a
numeric contract applies. `NaN` and infinity are rejected. Errors use stable
machine-readable codes and deterministic ordering. Validated runtime results
are immutable by ownership contract where adopted, even when backward
compatibility requires built-in mutable containers.

## Rationale

Explicit trust boundaries let friendly raw APIs coexist with strict composition
and serialization without allowing malformed results to appear authoritative.

## Consequences

- Raw and precomputed APIs remain clearly separated.
- Validation failures propagate unless the owning contract defines a structured
  invalid result.
- Callers cannot rely on undocumented trimming, case folding, defaulting, or
  field repair.
- Mutation of a validated snapshot invalidates that snapshot.

## Alternatives Considered

- Universal permissive coercion: rejected because malformed values become
  indistinguishable from intentional inputs.
- Silent repair of precomputed results: rejected because provenance is lost.
- Exception suppression: rejected because partial success can masquerade as a
  valid result.

## Compatibility Impact

This ADR formalizes current validation practice and does not tighten an
existing API by itself. Contract changes require a focused task.

## Related Specifications

- [Specifications index](../specifications/INDEX.md)
- [Test-vector standards](../test-vectors/INDEX.md)
