# ADR-002: Astrology Calculation Standards

- Status: `accepted`
- Adoption reference: Documentation Architecture Foundation after Sprint 11
- Supersedes: None
- Superseded by: None

## Context

Astrology calculations share longitude, sign, Nakshatra, house, time, and chart
foundations. Hidden normalization or interpretive output inside calculators can
produce inconsistent boundaries and make deterministic verification difficult.

## Decision

Calculation modules must use explicit documented normalization, deterministic
boundary rules, finite numeric inputs, and named reference points. They reuse
canonical astronomical, Rashi, Nakshatra, house, and chart utilities rather
than reproduce them. Calculation and classification remain separate from API,
serialization, presentation, narrative interpretation, recommendations, and
remedies. Any convention choice belongs in an approved domain specification,
not in this cross-domain ADR.

## Rationale

Centralized primitives and explicit reference frames prevent subtle differences
between domains and keep calculation output auditable.

## Consequences

- Boundary ownership and interval inclusion must be documented.
- Missing or non-finite inputs do not enter formula execution.
- A calculation result contains structured facts, not hidden interpretation.
- Domain-specific formulas and tables remain outside this ADR.

## Alternatives Considered

- Calculator-local normalization: rejected because equivalent inputs could
  diverge.
- Presentation-aware calculators: rejected because output consumers would
  control calculation semantics.
- Implicit reference points: rejected because the same placement can mean
  different things under different frames.

## Compatibility Impact

This ADR records established boundaries and changes no calculation.

## Related Specifications

- [Specifications index](../specifications/INDEX.md)
- Panchang, Kundali, Dasha, Matchmaking, Yogas, Doshas, and Transits are pending
  or planned domain specifications.
