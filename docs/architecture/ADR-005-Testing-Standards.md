# ADR-005: Testing Standards

- Status: `accepted`
- Adoption reference: Documentation Architecture Foundation after Sprint 11
- Supersedes: None
- Superseded by: None

## Context

Structural correctness, formula boundaries, external astronomical accuracy,
and backward compatibility require different evidence. A passing structural
fixture must not be mistaken for an externally verified astronomical value.

## Decision

Each runtime task adds focused tests, then runs affected dependency regressions
and the full project suite. Tests cover exact boundaries, normalization,
invalid inputs, deterministic repeated calls, stable ordering, JSON safety,
mutation isolation, and public import smoke as applicable. Configured formatting
and compilation checks run before completion. Expected astronomical values are
never fabricated: manually verified and external-reference vectors remain
explicitly unverified or skipped until their sources, tolerance, and review are
recorded.

## Rationale

Layered verification catches local defects without losing system-wide safety
and keeps structural regression data distinct from accuracy evidence.

## Consequences

- Test scope grows with the risk and dependencies of the change.
- Boundary inclusion is tested on both sides of exact transitions.
- Mutable outputs receive independence and non-mutation tests.
- Manual verification status is visible and cannot be inferred from a passing
  structural test.

## Alternatives Considered

- Focused tests only: rejected because integration regressions would escape.
- Full suite only: rejected because failures would be less diagnostic.
- Generated expected astrology values as truth: rejected because implementation
  output cannot independently verify itself.

## Compatibility Impact

This ADR changes no tests or runtime. It standardizes evidence required by
future tasks.

## Related Specifications

- [Test-vector standards](../test-vectors/INDEX.md)
- [Validation plan](../VALIDATION_PLAN.md)
- [Accuracy notes](../ACCURACY.md)
