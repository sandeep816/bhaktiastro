# Canonical Test Vectors

This directory is the human-readable home for reviewed domain examples,
boundaries, invalid inputs, regression cases, and externally verified
astronomical values. Vectors demonstrate an approved specification; they do not
replace formulas, Sprint progress, runtime tests, or implementation code.

## Domain Catalogue

| Domain | Canonical vectors | Status | Owning specification |
| --- | --- | --- | --- |
| Matchmaking | [matchmaking.md](matchmaking.md) | verified structural/domain-contract vectors | [SPEC-MATCHMAKING-001](../specifications/MATCHMAKING.md) |

No vector marked `verified` is thereby claimed to be independent astronomical
ephemeris validation. Each vector's source, assumptions, and linked test define
the scope of verification.

## Vector Categories

- `normative`: a minimal example required by an approved specification;
- `regression`: a reviewed case preserving behavior associated with a fixed
  defect or compatibility contract;
- `edge_boundary`: exact transition points and values immediately around them;
- `invalid_input`: deterministic rejection or structured-invalid behavior;
- `manual_astronomical`: a value checked manually against trusted references;
- `external_reference`: a value and tolerance traceable to an identified
  external source.

A vector may list more than one category when the purposes are explicit. A
structural runtime fixture is not automatically a manually verified or
external-reference vector.

## Verification Status Vocabulary

The vocabulary follows the existing [Validation Plan](../VALIDATION_PLAN.md):

- `pending`: recorded but not manually accepted;
- `in_review`: comparison or contract review is underway;
- `verified`: accepted against the stated specification or trusted references;
- `failed`: differs beyond its accepted contract or tolerance and requires
  investigation.

Verification status is independent from vector category and automated-test
status. A linked test can pass while an astronomical vector remains `pending`
if it verifies only structure.

## Canonical Vector Format

Each vector uses a stable identifier and records:

```text
Vector identifier: TV-<DOMAIN>-<CATEGORY>-NNN
Domain: <domain>
Category: <one or more registered categories>
Purpose: <behavior demonstrated>
Inputs: <complete ordered inputs>
Assumptions: <ayanamsa, timezone, reference point, convention, or none>
Expected result: <reviewed structured result; never guessed>
Tolerance: <numeric/time tolerance where applicable, otherwise exact>
Reference source: <approved specification and any external sources>
Verification status: pending | in_review | verified | failed
Linked automated test: <repository test path and test name, or none>
Notes: <limitations, provenance, or discrepancy reference>
```

Use machine-readable values and units. Long vectors may use tables or fenced
JSON after this metadata, but the metadata remains visible and complete.

## Naming and Organization

- Vector identifiers use `TV-<DOMAIN>-<CATEGORY>-NNN` and do not change if the
  file moves.
- Domain names and category tokens use uppercase ASCII with underscores in the
  identifier, for example `TV-MATCHMAKING-EDGE_BOUNDARY-001`.
- Future domain vector files use uppercase domain filenames unless a reviewed
  domain task selects a directory layout.
- Headings begin with the vector identifier, followed by a concise title.
- Automated tests reference the vector identifier in a test name, docstring,
  comment, parameter ID, or fixture metadata where practical.

## Relationship to Specifications and Tests

Approved domain specifications own rules; canonical vectors provide reviewed
examples; automated tests execute those examples where practical. A normative
vector must link to its specification. A regression vector must link to the
automated test or explain why automation is unavailable. External-reference
and manual astronomical vectors must state source, assumptions, reviewer
evidence, and tolerance before becoming `verified`.

When a vector, test, specification, or runtime output conflicts, do not update
one merely to make the disagreement disappear. Use the focused conflict process
in the [architecture index](../architecture/INDEX.md#source-of-truth-and-conflict-resolution).

## Prohibition on Invented Values

Never derive a supposedly independent expected astronomical value from the
same runtime implementation under test. Never fabricate a longitude, event
time, score, tolerance, or source. Keep unverified values `pending`, retain
skipped accuracy tests where required, and follow the existing
[Accuracy](../ACCURACY.md) and [Validation Plan](../VALIDATION_PLAN.md)
policies before accepting a value as verified.
