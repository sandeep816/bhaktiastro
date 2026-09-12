# SPEC-API-STABILITY-001 - API Versioning and Stability

| Metadata | Value |
| --- | --- |
| Status | approved |
| Specification version | 1.0 |
| Owning domain | cross-cutting public API stability |
| Governing ADRs | [ADR-001](../architecture/ADR-001-Project-Principles.md), [ADR-002](../architecture/ADR-002-Astrology-Calculation-Standards.md), [ADR-003](../architecture/ADR-003-Validation-Standards.md), [ADR-004](../architecture/ADR-004-Public-API-Contracts.md), [ADR-005](../architecture/ADR-005-Testing-Standards.md) |
| Sprint owner | [Sprint 14, Task 14.1](../SPRINT-14.md#task-141---api-versioning-and-stability-foundation) |
| Implementation status | documentation foundation complete; automated inventory and contract-test enforcement not started |
| Compatibility impact | governance-only; no runtime, schema, vocabulary, identifier, serializer, or export change |

## Purpose

This specification is the permanent source of truth for deciding whether a
BhaktiAstro public-contract change is compatible, deprecated, or breaking. It
defines the stability boundary shared by Python packages, immutable models,
validators, serializers, schema identifiers and versions, machine-readable
vocabularies, stable identifiers, errors, and deterministic ordering.

The policy protects existing callers without freezing private implementation.
It does not declare every importable object public, turn historical behavior
into a supported contract, or replace the owning domain specification.

## Authority and conflict handling

The repository source-of-truth hierarchy in the
[architecture index](../architecture/INDEX.md#source-of-truth-and-conflict-resolution)
applies. This specification interprets the accepted ADRs across domains. An
approved owning-domain specification may make a stricter commitment and must
be followed. It may not silently weaken this policy.

For domains whose permanent specification is still pending migration, current
Sprint records, automated tests, runtime behavior, and documented consumer
paths are audited in hierarchy order. This policy does not retroactively
normalize conflicting legacy behavior. A discrepancy is recorded and resolved
in a focused migration or compatibility task.

## Scope

The compatibility surface includes, when public under the definition below:

- Python package and module import paths, exported names, aliases, callable
  signatures, parameter kinds, defaults, accepted values, return types, and
  documented side effects;
- immutable or mutable model types, exact field names and field order,
  constructors, factories, validators, equality and ownership behavior;
- serializer entry points, exact output keys, key order, value types, null
  behavior, collection order, mutation isolation, and JSON-safety guarantees;
- schema identifiers, schema-version fields, schema registries, supported
  versions, and rejection of unsupported versions;
- documented status, category, issue-code, relationship, block-kind, and other
  machine-readable vocabularies;
- rule identifiers, schema identifiers, component identifiers, report types,
  and documented public constant values;
- exception classes, structured issue contracts, validation/failure order,
  and fail-fast versus aggregated-failure behavior; and
- deterministic ordering of fields, results, findings, evidence, issues,
  sections, blocks, Kootas, or other public collections where the owning
  contract declares order significant.

HTTP route-version design, package publication, database migrations, and
release automation are explicitly outside this task. Existing documented
request and response models remain compatibility-relevant even though this
specification does not version REST paths.

## Public and private contract boundary

An object or behavior is public when at least one of these conditions holds:

1. its exact name is listed in a package's explicit `__all__`;
2. an approved permanent specification declares its module path, name, value,
   shape, signature, behavior, or serialization contract public;
3. an active or completed authoritative Sprint contract explicitly promises it
   to callers and no later approved source supersedes that promise; or
4. an application transport contract explicitly exposes it as a documented
   request or response field, status, identifier, or error shape.

A package-level re-export without `__all__` is public only when an authoritative
document or established public-contract test also identifies that path as
supported. Merely being importable, introspectable, or referenced by an
internal test does not by itself create a permanent public promise.

Private surface includes underscore-prefixed names, implementation helpers,
internal module paths, local constants, caches, test utilities, incidental
imports, and undocumented intermediate representations. Private changes are
still subject to regression testing when they affect public behavior.

The membership of a public `__all__` is contractual. Its order is contractual
only when the owning specification or an existing contract test explicitly
requires order. This distinction preserves stricter Reporting commitments
without inventing a universal order promise for older packages.

## Compatibility categories

Every proposed contract change must receive exactly one category before it is
implemented:

| Category | Meaning |
| --- | --- |
| `additive_compatible` | Adds an independently usable public capability while every previously valid call, import, result, error, and ordering guarantee remains unchanged. |
| `contract_clarification` | Changes documentation or restores already-approved behavior without changing any valid supported input or observable output. |
| `deprecated_supported` | Keeps the old contract fully operational while identifying a replacement and a future, separately approved removal path. |
| `breaking` | Removes, renames, reorders, narrows, repurposes, or observably changes any previously valid public contract. |
| `internal_only` | Changes no public import, input, output, error, identifier, schema, ownership, or deterministic behavior. |

These labels are documentation-governance terms, not new runtime constants or
serialized vocabulary.

A bug fix is not automatically compatible. If it changes behavior accepted by
the current public contract, it is breaking or requires a versioned migration.
Changing only undocumented invalid-input behavior may be a contract
clarification after focused tests prove all valid behavior is unchanged.

An additive Python export does not imply an additive serialized-schema change.
Strict serializers treat an added key as a shape change unless the owning
schema explicitly defines extensible fields and reader behavior.

## Python public API policy

### Imports and exports

- Existing public module paths and exported names remain importable.
- Adding a new independent export is `additive_compatible` when importing it
  has no new side effect and existing exports remain unchanged.
- Renaming or moving a public name is breaking unless the old path remains a
  supported alias throughout deprecation.
- A type or constant alias should re-export the same object. A callable wrapper
  is not a transparent alias when it changes identity, introspection,
  signature, exception behavior, or side effects.
- Removing a public export, or removing it from contractual `__all__`
  membership, is breaking.

### Callable signatures

The following are contractual when documented or exported: parameter names,
parameter kinds, positional order, keyword-only behavior, required/optional
state, default values, accepted runtime types, role meaning, and return type.

- A new required parameter is breaking.
- A new optional parameter is compatible only when it is keyword-only, its
  default preserves every old call's behavior and output, and it does not
  change validation precedence or serialization.
- Adding a positional parameter is not the default compatibility path because
  it can alter positional binding and introspection.
- Renaming a keyword, changing positional to keyword-only or the reverse,
  changing a default, or reordering positional parameters is breaking.
- Widening accepted input is compatible only after review proves old valid and
  invalid behavior, failure order, and output are unaffected. Narrowing input
  is breaking.
- Changing return representation, mutability, aliasing, exception class, or
  documented side effect is breaking.

Keyword-only parameter declaration order is preserved when an owning contract
or public test treats the inspected signature as exact.

## Model, factory, and validator compatibility

For an immutable dataclass or similarly strict model, the declared model type,
field names, field order, required/default state, field types, nullability,
equality behavior, hashability, slots behavior, and nested ownership are part
of the contract when documented.

- Adding, removing, renaming, retyping, or reordering a strict model field is
  breaking even when a new field has a default. It changes construction,
  introspection, equality, pattern matching, or serialization.
- Changing tuple ownership to list ownership, mapping proxy to mutable mapping,
  or independent copies to shared aliases is breaking.
- A new model or factory is additive when independent of existing shapes.
- A factory's normalization, duplicate handling, validation order, and result
  type follow the callable and error policies in this document.
- A validator may become stricter only for values already invalid under the
  approved contract. Rejecting a previously valid value is breaking.
- Adding an optional input field to a mapping or transport model is compatible
  only when old callers and exact old outputs remain unchanged and the owning
  extra-field policy permits it. Adding an emitted output field is a serialized
  shape change.

## Serializer and JSON contract stability

When an owning contract defines exact serialization, consumers may rely on:

- serializer name and signature;
- schema identifier and supported schema version;
- exact root and nested keys and their order;
- exact scalar, mapping, and list value types;
- required, optional, omitted, and null behavior;
- deterministic collection order;
- finite numeric and strict JSON-safe behavior;
- rejection rather than silent coercion or repair; and
- fresh mutable output with no tuple, mapping proxy, custom runtime object,
  cycle, shared mutable alias, or source-model alias where promised.

Within such a schema, adding or removing a key, reordering keys, changing a
value type or null rule, changing list order, changing identifier spelling, or
weakening mutation isolation is breaking. A serializer must not emit a newer
shape while retaining an older schema version.

Formatting differences produced by external JSON encoders, such as whitespace,
are not contractual unless a future byte-level format explicitly says so.

## Version responsibilities

BhaktiAstro keeps these version concepts separate:

| Version | Responsibility |
| --- | --- |
| Project/package version | Identifies a released code distribution. Project metadata currently declares `0.1.0`; a domain serializer does not own or select it. |
| Application/deployment version | Identifies the running application build/configuration. Application configuration currently defaults to `0.1.0`; it may differ by deployment and does not select a data schema. |
| Schema identifier | Permanently names one serialized contract family and is never reused for another meaning. |
| Schema version | Identifies an exact supported revision of that schema family. |
| Artifact/domain version | Caller- or producer-owned version such as Reporting `report_version` or Interpretation `interpretation_version`; it does not replace `schema_version`. |
| Rule version | Versions deterministic rule semantics under the owning domain and does not select package or document schema behavior. |

Changing one version does not silently change another. Task 14.1 defines no
release cadence, package publishing workflow, dependency-resolution promise,
or deployment mechanism.

## Schema versioning policy

### Current registry

The approved current families are:

| Schema family | Identifier | Canonical emitted version | Owner |
| --- | --- | --- | --- |
| Matchmaking result families | `bhaktiastro.matchmaking` | `1.0` | [SPEC-MATCHMAKING-001](MATCHMAKING.md) |
| Reporting document | `bhaktiastro.reporting.document` | `1.0` | [SPEC-REPORTING-001](REPORTING.md) |
| Interpretation document | `bhaktiastro.interpretation.document` | `1.0` | [SPEC-INTERPRETATION-001](INTERPRETATION.md) |

The Matchmaking compatibility report uses the Matchmaking schema version. Its
`report_type` distinguishes the result family; it does not create a fourth
schema version. Reporting `report_version` and Interpretation
`interpretation_version` remain separate artifact versions.

### Version form and meaning

New canonical schema versions default to numeric `MAJOR.MINOR`. Existing
family-specific validators and accepted version grammars remain unchanged
until a focused migration approves a change.

- Increment `MAJOR` for an incompatible shape, identifier, vocabulary,
  validation, ordering, or semantic change.
- Increment `MINOR` only for a genuinely backward-compatible schema extension
  whose owning contract already defines how older readers tolerate the new
  data. The current strict `1.0` Matchmaking, Reporting, and Interpretation
  serializers do not permit undeclared keys, so a new emitted key is not
  automatically a minor change.
- A schema `PATCH` component is not a universal BhaktiAstro emission policy.
  It may be used only when the owning approved schema explicitly defines it.
  Code-only bug fixes that preserve an exact schema normally keep the schema
  version and use the project/package release version instead.

The existing artifact-version validators that allow two or three numeric
components remain valid; this policy does not narrow them.

### Coexistence and unsupported versions

A producer, serializer, or validator supports only exact versions explicitly
registered and documented by its owning family. Unsupported versions must be
rejected deterministically: wrong runtime type raises `TypeError`, while a
well-typed unsupported value raises `ValueError`, unless the established owning
contract already specifies a stricter error class.

A new major schema must have an explicit coexistence plan: a distinct
serializer/validator entry point or an explicit keyword-only version selector,
a documented old-version path, migration guidance, and contract tests for both
versions. Existing version support remains through the deprecation window.

There is no silent upgrade, downgrade, nearest-version fallback, version
negotiation, automatic migration, or unknown-field repair. This task does not
implement deserializers or a schema registry service.

## Vocabulary compatibility

Machine-readable strings are public when an owning contract declares a closed
or stable vocabulary. This includes statuses, issue codes, category names,
block kinds, Koota names, comparison values, and relationship identifiers.

- Existing values retain spelling, case, meaning, and role.
- Renaming, removing, merging, splitting, or repurposing a value is breaking.
- Adding a value to a closed vocabulary is breaking because exhaustive callers
  may reject it. It requires an owning schema/version decision.
- Adding a value to an explicitly extensible vocabulary may be additive only
  when unknown-value behavior was already documented and tested.
- Display text, translations, and prose are not substitutes for stable
  machine-readable values.

## Identifier stability

Schema identifiers, report types, component names, calculation names, public
constant values, issue codes, and versioned rule identifiers are never reused
for a different semantic meaning.

Interpretation rule IDs retain their approved versioned form. A semantic rule
change that alters conditions, evidence, tendency, or outcome uses the owning
rule-version policy rather than silently rewriting an existing rule ID.

Instance identifiers supplied by callers, such as subject, source, evidence,
or finding IDs, are not framework-generated stable values. Their documented
syntax, uniqueness scope, reference behavior, and validation remain
contractual; the caller-chosen literal values do not become global framework
constants.

## Deprecation policy

Deprecation preserves support; it does not authorize removal. Before a public
contract is deprecated, one focused change must record:

1. the exact old import, callable, field, vocabulary value, identifier, or
   schema version;
2. the supported replacement and migration steps;
3. the first project/package release carrying the deprecation;
4. the earliest removal release and date;
5. documentation, changelog, and contract-test coverage for old and new paths;
   and
6. any runtime-warning plan, which requires separate implementation authority.

The minimum support window is **two subsequent published project releases and
90 calendar days, whichever ends later**. If no release cadence exists or no
subsequent releases are published, the removal window has not completed.

During the window, the old contract must retain its documented signature,
behavior, errors, ordering, and output. Warnings must not corrupt serialized
data or alter return values. Task 14.1 does not add warnings.

Removal requires a separately approved breaking-change task, migration notes,
updated inventory, contract tests, changelog entry, and an explicit
project/package version decision. Before project version `1.0`, a three-part
version does not by itself promise full semantic-version compatibility; after
`1.0`, breaking public Python changes require a major package-version change.
No public API may be silently removed.

## Breaking-change policy

A breaking change is allowed only when all of the following exist before
merge:

- a concrete necessity that cannot be satisfied additively;
- affected public-contract inventory entries and consumer impact;
- an approved owning specification or ADR update;
- schema, package, rule, or artifact version decisions as applicable;
- deprecation-window outcome or a documented exceptional migration decision;
- old/new examples and deterministic migration instructions;
- focused contract, regression, and unsupported-version tests; and
- explicit changelog language naming the break.

An emergency security or correctness exception still requires an approved
decision and clear migration record; it is not a license for an undocumented
break. Neither this specification nor Sprint 14.1 approves a current breaking
change.

## Error-contract stability

The exception class is stable where the owning contract distinguishes caller
type errors from invalid values. Exact human-readable exception text is not
stable unless an approved specification explicitly declares it machine-read or
an established contract test requires the exact message.

Structured error and issue contracts preserve documented:

- issue code/category vocabulary;
- path representation and role attribution;
- field and issue ordering;
- validation precedence and deterministic first failure;
- fail-fast versus multi-issue aggregation;
- safe-invalid result versus raised-exception behavior; and
- propagation of unexpected component failures.

Changing between `TypeError` and `ValueError`, changing a documented issue
code/path, silently suppressing an exception, switching between fail-fast and
aggregation, or reordering deterministic validation failures is breaking.
Internal traceback frames and undocumented helper messages are not public.

## Deterministic ordering policy

Order is contractual when an owning specification defines it, a serializer
emits exact ordered fields, or caller order is expressly preserved. Such order
includes root and nested field order, canonical Koota order, report section and
block order, finding/evidence/source order, and issue/failure order.

Reordering a contractual sequence is breaking even if its values are
unchanged. Implementations must not depend on set iteration, unordered source
discovery, locale-sensitive sorting, object identity, hash randomization, or
timestamps to produce contractual order.

Mappings used only for lookup do not gain a public iteration-order promise
unless the owning contract exposes or serializes that order.

## Cross-domain application

- **Kundali, Panchang, and Dasha:** permanent specification migration is
  pending. Existing documented endpoints, public module imports, request and
  response fields, option flags, validation behavior, and regression-tested
  outputs remain protected pending focused inventory.
- **Prediction:** the explicit `backend.app.prediction` export surface and
  structured rule/result contracts remain protected. Historical tolerant rule
  loading is not silently replaced by the strict new-schema defaults; its
  permanent migration must resolve that behavior explicitly.
- **Matchmaking:** `SPEC-MATCHMAKING-001` owns its exact exports, keyword-only
  calculators, result-family fields and order, `1.0` schema, identifiers,
  vocabularies, issue behavior, immutable ownership, and serializers.
- **Reporting:** `SPEC-REPORTING-001` owns its exact `backend.app.reporting`
  exports, frozen model fields/order, factories, validators, schema ID/version,
  and fresh deterministic serializer.
- **Interpretation:** `SPEC-INTERPRETATION-001` owns its exact
  `backend.app.interpretation` exports, frozen model fields/order, closed
  vocabularies, versioned rule references, schema ID/version, validators, and
  fresh deterministic serializer.

No domain is forced into Reporting or Interpretation models by this policy.
No completed output is migrated, wrapped, or recalculated.

## Public-contract inventory plan

The approved specifications are the current detailed inventories for
Matchmaking, Reporting, and Interpretation. Pending-migration domains retain
their existing sources until audited. A later authorized inventory artifact
must record one row per public contract with these fields:

1. stable inventory ID;
2. owning domain and approved source;
3. public import/module path or transport path;
4. exported name and contract kind;
5. signature or exact shape reference;
6. schema identifier/version, if any;
7. vocabulary and stable-identifier references;
8. ordering, error, ownership, and mutation guarantees;
9. first supported project/package version;
10. compatibility state and deprecation metadata;
11. focused contract-test location; and
12. replacement/supersession reference, if any.

The inventory must distinguish verified public contracts from audit-pending
legacy candidates. It must not infer stability merely from filesystem
discovery.

## Required future contract tests

Runtime enforcement is a later, separately authorized task. It must use
focused tests appropriate to each public family, including:

- exact import paths, export membership, aliases, and import smoke;
- exact callable signatures, parameter kinds/defaults, and keyword-only rules;
- exact model field order, types/defaults, immutability, equality, and nested
  ownership;
- exact serializer keys/order/types, finite JSON safety, deterministic repeated
  calls, deep-copy output, cycle/alias rejection, and mutation isolation;
- exact current schema identifiers and versions plus deterministic rejection of
  unsupported versions;
- closed vocabulary, identifier, issue-code, status, and rule-version checks;
- exception classes, documented validation order, issue order, and failure
  propagation;
- coexistence tests for every supported deprecated and replacement contract;
- regression tests for Kundali, Panchang, Dasha, Prediction, Matchmaking,
  Reporting, and Interpretation; and
- a check that the public-contract inventory contains no duplicate IDs,
  dangling owners, or untested removal.

Contract tests must assert meaningful structure rather than brittle private
implementation. Exact exception messages are asserted only when explicitly
public. No runtime test is added by Task 14.1.

## Backward-compatibility rules for this specification

Version 1.0 adds governance documentation only. It changes no accepted input,
calculation, return value, export, schema, vocabulary, identifier, serializer,
exception, or ordering behavior.

Future revisions to this specification classify themselves under this policy.
Clarifications may retain specification version 1.0 when they change no
requirement. A new compatible requirement increments the specification minor
version. A policy change that weakens an existing public guarantee requires a
new major specification version, an explicit supersession record, and an
approved migration.

## Explicit exclusions

Sprint 14.1 does not implement or define:

- runtime modules, validators, warnings, registries, compatibility shims, or
  automated contract tests;
- new public exports, aliases, endpoints, request/response fields, models,
  serializers, schemas, schema values, vocabularies, or identifiers;
- astrology calculations, changed formulas, interpretation, predictions,
  remedies, recommendations, AI, or narrative generation;
- Reporting or Interpretation adapters, rendering, templates, UI, PDF, email,
  persistence, telemetry, or network behavior;
- PyPI publication, dependency pinning, changelog automation, Git tagging,
  deployment, release cadence, or package installer policy;
- REST URL-version strategy, protocol negotiation, database schema migration,
  or stored-data migration;
- deserialization, automatic schema conversion, silent upgrade/downgrade, or a
  schema-registry service; or
- broad retroactive migration of historical Sprint documents or pending
  Kundali, Panchang, Dasha, Prediction, Yoga, Dosha, or Transit specifications.

## Validation checklist

Approval of version 1.0 requires:

- consistency with ADR-001 through ADR-005;
- consistency with current Matchmaking, Reporting, and Interpretation public
  contracts and schema versions;
- explicit separation of package, application, schema, artifact, and rule
  versions;
- explicit compatibility, deprecation, breaking, error, and ordering rules;
- valid links to owning specifications and Sprint 14;
- Markdown-only scope with no runtime, test, or export changes;
- `git diff --check`, staged-diff review, and a clean tree after the focused
  documentation commit.

## Implementation and change history

- Version 1.0: approved by Sprint 14 Task 14.1 as the documentation-only API
  stability foundation. Automated inventory and contract-test enforcement are
  not implemented and no later Sprint 14 task is authorized.
