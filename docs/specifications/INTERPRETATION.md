# SPEC-INTERPRETATION-001 - Interpretation Data Boundary

| Field | Value |
| --- | --- |
| Status | `approved` |
| Specification version | `1.0` |
| Owning domain | Interpretation |
| Related ADRs | [ADR-001](../architecture/ADR-001-Project-Principles.md), [ADR-002](../architecture/ADR-002-Astrology-Calculation-Standards.md), [ADR-003](../architecture/ADR-003-Validation-Standards.md), [ADR-004](../architecture/ADR-004-Public-API-Contracts.md), [ADR-005](../architecture/ADR-005-Testing-Standards.md) |
| Related Sprint task | [Sprint 13, Task 13.1](../SPRINT-13.md#task-131---interpretation-data-boundary-foundation) |
| Implementation status | `not_started` |
| Test-vector status | `pending` |
| Backward compatibility | Additive planned foundation; no existing public contract changes |

This is the permanent source of truth for the Sprint 13.1 Interpretation Data
Boundary Foundation. It defines a strict, domain-neutral representation for
validated interpretive facts derived from already-computed astrology results.
It does not generate interpretation text.

## Purpose and scope

The boundary sits between validated deterministic domain results and future
interpretation rules or narrative consumers:

```text
Astrology calculators
    -> validated domain results
    -> Interpretation Data Boundary
    -> future interpretation rules or narrative layer
    -> Report Data Model or rendering
```

The foundation records which deterministic rule produced a finding, which
validated source fields support or oppose it, which subjects it concerns, and
its technical state. It supports future Kundali, Matchmaking, Panchang, Dasha,
Prediction, Yoga, Dosha, and Transit interpretation without defining any rule
for those domains.

It never calculates astrology, changes or completes a source result, evaluates
a rule, selects a template, generates prose, assigns unsupported certainty, or
renders a report.

## Dependencies and architectural boundaries

- ADR-001 requires one additive foundation without later-task work.
- ADR-002 keeps calculation, classification, interpretation data, narrative,
  reporting, and rendering separate.
- ADR-003 requires strict validation, finite values, explicit trust boundaries,
  and no silent coercion or repair.
- ADR-004 makes public names, signatures, field order, vocabularies, versions,
  ordering, and serialization behavior contractual.
- ADR-005 requires focused structural, invalid-input, mutation, serialization,
  public-import, dependency-regression, and full regression evidence when the
  runtime is implemented.
- [SPEC-REPORTING-001](REPORTING.md) owns generic report documents and remains
  unchanged.
- [SPEC-MATCHMAKING-001](MATCHMAKING.md) owns Matchmaking results and remains
  unchanged.
- Prediction remains `pending migration`; its current contract must be audited
  from [Sprint 10A](../SPRINT-10A.md), [Sprint 10B](../SPRINT-10B.md),
  [prediction_rules.md](../prediction_rules.md), runtime, and tests until a
  permanent Prediction specification is approved.

## Terminology

- **Document**: one complete, incomplete, or invalid interpretation-data
  snapshot.
- **Subject reference**: a caller-owned identity and role, not birth data or a
  Reporting subject.
- **Source**: provenance for one already-computed, validated result family.
- **Evidence**: a stable reference to one source field plus a copied JSON-safe
  observed value and its relationship to a finding.
- **Finding**: a non-narrative result of an explicitly identified deterministic
  interpretation rule.
- **Tendency**: a limited semantic direction supplied by that rule, distinct
  from technical status and certainty.
- **Issue**: a technical error or warning with a stable code and path.

## Selected model hierarchy

Task 13.1 selects eight public immutable runtime models:

1. `InterpretationDocument`
2. `InterpretationSubjectReference`
3. `InterpretationFinding`
4. `InterpretationEvidence`
5. `InterpretationIssue`
6. `InterpretationSource`
7. `InterpretationMetadata`
8. `InterpretationRuleReference`

`InterpretationFactor` is excluded because supporting, opposing, and contextual
facts are represented once as evidence. `InterpretationContext` is excluded
because locale, audience, style, time horizon, and questions belong to later
rule, narrative, localization, or presentation contracts. The root
`interpretation_type` and each finding's `topic` provide only stable machine
classification.

Each selected model is a frozen, slotted dataclass. Nested sequences are
tuples; nested mappings are read-only mapping proxies over newly allocated
dictionaries. Constructors are private and public keyword-only factories
validate and defensively copy all values. Models have same-class structural
equality including sequence and mapping order and are deliberately unhashable
because recursive values may contain mappings.

No selected model subclasses, wraps, or aliases a Prediction, Matchmaking, or
Reporting model. No Pydantic transport model, ORM model, mutable result
dictionary, generic node, or arbitrary dataclass wrapper is part of Task 13.1.

## Inputs and normalization

The foundation accepts only the exact constructor values documented below.
Factories create one model at a time; strict validators and the serializer
accept only completed exact Interpretation model instances. There is no raw
birth-data, chart, longitude, calculator-result, Prediction-result,
Matchmaking-result, Reporting-model, generic mapping-hydration, or arbitrary
object input API.

A future domain adapter must first validate an already-computed result through
its owning contract, then construct explicit `InterpretationSource` and
`InterpretationEvidence` values. The adapter may copy only the declared source
field value and cannot recalculate, normalize, complete, mutate, or retain the
source object.

No semantic input is normalized. Identifiers, versions, domains, statuses,
tendencies, relations, paths, rule references, and roles must already be
canonical. Container inputs are copied into the immutable representation, and
serialization canonicalizes only floating-point `-0.0` to JSON-safe `0.0`.

## Shared values, identifiers, and text

The recursive value vocabulary is exactly:

```text
InterpretationScalar = str | bool | int | finite float | None
InterpretationValue = InterpretationScalar
                      | tuple[InterpretationValue, ...]
                      | read-only ordered mapping[str, InterpretationValue]
InterpretationJsonValue = InterpretationScalar
                          | list[InterpretationJsonValue]
                          | dict[str, InterpretationJsonValue]
```

Factories accept built-in lists or tuples at declared sequence positions and
well-behaved `Mapping` objects at declared mapping positions. They preserve
caller order after validation and allocate an alias-free immutable graph.
Every recursive value-mapping key must be an exact machine identifier.

Machine identifiers are 1 through 128 lowercase ASCII characters and match:

```text
^[a-z][a-z0-9]*(?:[._-][a-z0-9]+)*$
```

Versions match `^[0-9]+\.[0-9]+(?:\.[0-9]+)?$` and are at most 32
characters. Identifiers and versions are never trimmed, case-folded, aliased,
wrapped, defaulted from environment state, or silently normalized.

Human-facing labels preserve casing and internal whitespace but, when
non-empty, cannot have leading or trailing whitespace. They are descriptive
caller data, not generated narrative. No model has summary, explanation,
advice, remedy, prediction-text, template, Markdown, or HTML fields.

Enums, foreign dataclasses, sets, frozensets, bytes-like values, `Decimal`,
date/time objects, exceptions, callables, generators, complex numbers,
arbitrary objects, NaN, and either infinity are rejected. Booleans are
rejected wherever a numeric value is specifically required. Unsupported
values are not stringified, omitted, replaced with null, or repaired. Direct
and indirect cycles and shared mutable input paths are rejected.

## InterpretationMetadata

Metadata is limited technical provenance, not a second content payload.

| Position | Field | Type | Required/default |
| ---: | --- | --- | --- |
| 1 | `schema_id` | identifier string | required |
| 2 | `source_component` | identifier string | required |
| 3 | `source_version` | version string or empty string | default empty |
| 4 | `deterministic` | boolean | default `true`; Task 13.1 requires `true` |
| 5 | `attributes` | ordered mapping of identifier to non-null scalar | default empty |

Attribute values are only strings, booleans, integers, or finite floats.
Nested values and null are forbidden. No factory adds timestamps, UUIDs,
locale, environment, user, host, platform, telemetry, or random values.

When another model receives `metadata=None`, its factory creates an independent
metadata instance with `schema_id="bhaktiastro.interpretation.metadata"`,
`source_component="bhaktiastro.interpretation"`, `source_version="1.0"`,
`deterministic=true`, and empty attributes.

## InterpretationSubjectReference

| Position | Field | Type | Required/default |
| ---: | --- | --- | --- |
| 1 | `subject_id` | identifier string | required; unique in document |
| 2 | `role` | identifier string | required; unique in document |
| 3 | `label` | string | default empty |
| 4 | `metadata` | `InterpretationMetadata` | default fresh metadata |

Documents support zero, one, directional two, or multiple subjects. Sequence
order plus explicit unique roles represents direction; no sex, gender, bride,
groom, person type, or domain meaning is inferred. Findings and evidence refer
to subjects by `subject_id`. They do not copy birth data, `ReportSubject`, or a
domain person object.

## InterpretationSource

| Position | Field | Type | Required/default |
| ---: | --- | --- | --- |
| 1 | `source_id` | identifier string | required; unique in document |
| 2 | `domain` | supported domain identifier | required |
| 3 | `result_family` | identifier string | required |
| 4 | `result_version` | version string or empty string | default empty |
| 5 | `reference` | string | default empty |
| 6 | `metadata` | `InterpretationMetadata` | default fresh metadata |

`reference` is an opaque caller identifier for a validated snapshot. It does
not fetch, persist, verify, or expose that object. `result_family` names the
source contract; `result_version` is present only when that source contract
has an explicit version. Missing source versions are not invented.

The stable `INTERPRETATION_DOMAINS` tuple is exactly:

```text
kundali, matchmaking, panchang, dasha, prediction, yoga, dosha, transit
```

Unknown domains are rejected. Adding or renaming a domain is a vocabulary and
schema review, not permissive metadata.

## InterpretationRuleReference

| Position | Field | Type | Required/default |
| ---: | --- | --- | --- |
| 1 | `rule_id` | versioned interpretation-rule identifier | required |
| 2 | `owner` | component identifier | required |
| 3 | `rule_version` | version string | required |
| 4 | `source_reference` | string | default empty |
| 5 | `metadata` | `InterpretationMetadata` | default fresh metadata |

Rule identifiers use exactly:

```text
<domain>.<owner>.<rule-name>.v<positive-integer>
```

There are exactly four dot-separated segments. The first is one supported
domain; the second and third match `[a-z][a-z0-9_-]*`; the fourth matches
`v[1-9][0-9]*`. The `owner` field must equal the second segment. The owner is
responsible for global uniqueness, source documentation, and meaning.
`rule_version` versions the complete rule definition, and its major number
must equal the final `vN` number. Changing conditions, evidence semantics,
tendency semantics, or outcome meaning requires a new major version and final
`vN` identifier. A nonsemantic source-reference correction may retain the
identifier and use a patch version only when finding behavior cannot change.

Rule IDs are not normalized or silently mapped from Sprint 10 IDs. Supersession
must name the replacement in the owning future rule specification, retain the
old identifier during an announced compatibility period, and never repurpose
an old ID. Rule references are unique by `rule_id` within a document. Multiple
findings may refer to one rule.

## InterpretationEvidence

| Position | Field | Type | Required/default |
| ---: | --- | --- | --- |
| 1 | `evidence_id` | identifier string | required; unique in document |
| 2 | `source_id` | identifier string | required; resolves in document |
| 3 | `source_path` | non-empty tuple of identifier strings or non-negative integers | required |
| 4 | `relation` | evidence relationship | required |
| 5 | `observed_value` | `InterpretationValue` | required; null permitted |
| 6 | `subject_ids` | tuple of subject identifiers | default empty |
| 7 | `metadata` | `InterpretationMetadata` | default fresh metadata |

`INTERPRETATION_EVIDENCE_RELATIONS` is exactly:

```text
supporting, opposing, contextual
```

`supporting` means the owning deterministic rule used the observed fact in
support of its finding; `opposing` means it used the fact against that finding;
`contextual` means the fact is relevant but not directional. These labels do
not calculate the rule outcome or imply good, bad, certainty, or advice.

Evidence copies only the validated value at the declared source path. It must
not embed an entire arbitrary runtime result, use an empty path as a whole-
object escape hatch, retain the source object, or reference a mutable path.
The boundary verifies reference shape and document consistency; a future
domain adapter is responsible for strict source-family validation and for
proving that the path and copied value agree with that source snapshot.

A separate `comparison_value` field is excluded because comparison meaning and
units belong to the owning deterministic rule. A rule that compares two
source fields uses two evidence objects; it does not hide the second value or
the comparison operation in generic boundary metadata.

Subject IDs are unique within one evidence item and resolve in the document.
Their order is semantic and preserved. One evidence object belongs to exactly
one finding because `relation` is finding-specific; sharing an evidence ID
across findings is rejected. Two findings that use the same source field must
create distinct evidence objects with distinct IDs and their own relation.

## InterpretationIssue

| Position | Field | Type | Required/default |
| ---: | --- | --- | --- |
| 1 | `code` | identifier string | required |
| 2 | `message_key` | identifier string | required |
| 3 | `path` | tuple of identifier strings or non-negative integers | default empty |
| 4 | `category` | `error` or `warning` | required |
| 5 | `details` | ordered mapping of identifier to `InterpretationValue` | default empty |

Human-readable exception and issue messages are not a schema contract.
`message_key` is localization-ready but Task 13.1 performs no localization.
Exact duplicate issues in one issue list are rejected. Error lists contain
only errors and warning lists contain only warnings. Caller order is preserved.

## InterpretationFinding

| Position | Field | Type | Required/default |
| ---: | --- | --- | --- |
| 1 | `finding_id` | identifier string | required; unique in document |
| 2 | `rule_id` | rule identifier | required; resolves in document |
| 3 | `domain` | supported domain identifier | required |
| 4 | `topic` | identifier string | required |
| 5 | `category` | identifier string | required |
| 6 | `status` | technical status | default `complete` |
| 7 | `tendency` | semantic tendency | required |
| 8 | `subject_ids` | tuple of subject identifiers | default empty |
| 9 | `evidence_ids` | tuple of evidence identifiers | required for complete finding |
| 10 | `errors` | tuple of error `InterpretationIssue` | default empty |
| 11 | `warnings` | tuple of warning `InterpretationIssue` | default empty |
| 12 | `metadata` | `InterpretationMetadata` | default fresh metadata |

`topic` is a broad machine topic such as a rule-owned life or event area;
`category` is the rule-owned finding kind. This foundation validates their
identifier shape only and assigns no domain meaning.

A complete finding has at least one unique evidence ID, no errors, and only
resolving subject, evidence, and rule references. An incomplete or invalid
finding has at least one error and may have zero evidence when the issue
explicitly records missing evidence. Findings do not contain prose, scores,
strength, probability, recommendations, or embedded source results.

### Tendency decision

Task 13.1 includes `INTERPRETATION_TENDENCIES` exactly as:

```text
supportive, challenging, mixed, neutral, informational
```

- `supportive`: the identified rule classifies its evidence as enabling the
  stated topic; it does not mean morally good, auspicious, or guaranteed.
- `challenging`: the rule classifies its evidence as constraining the topic;
  it does not mean bad, inauspicious, harmful, or certain.
- `mixed`: the rule records both enabling and constraining considerations.
- `neutral`: the rule records neither an enabling nor constraining direction.
- `informational`: the finding is a structured fact for which semantic
  direction is not applicable.

Tendency is supplied by an identified deterministic rule and is never inferred
from status, evidence count, domain labels, or source values by this boundary.
It is not compatibility, marriage suitability, pass/fail, recommendation,
prediction certainty, severity, sentiment, or moral judgment.

### Strength decision

Universal strength is excluded and deferred. Existing domains use different
units, thresholds, and meanings; Task 13.1 defines no categorical strength,
numeric strength, weight, severity, impact, aggregate score, or normalization.
A source's validated strength value may be copied as evidence with its source
path, but it does not become a universal finding strength.

### Confidence decision

Confidence is excluded and deferred. Data completeness is represented by
technical status and issues. Rule applicability belongs to a future
domain-rule contract. Interpretation confidence has no approved deterministic
or probabilistic meaning. Sprint 10 confidence may be referenced as an
observed source value, but it is not copied into or normalized as an
Interpretation confidence field. The boundary never invents, clamps, averages,
or converts confidence.

## InterpretationDocument

The root field order is exact:

| Position | Field | Type | Required/default |
| ---: | --- | --- | --- |
| 1 | `schema_id` | `bhaktiastro.interpretation.document` | factory-owned constant |
| 2 | `schema_version` | `1.0` | factory-owned constant |
| 3 | `interpretation_type` | identifier string | required |
| 4 | `interpretation_version` | version string | required |
| 5 | `interpretation_id` | identifier string | required |
| 6 | `status` | technical status | default `complete` |
| 7 | `subjects` | tuple of `InterpretationSubjectReference` | default empty |
| 8 | `sources` | tuple of `InterpretationSource` | default empty |
| 9 | `rules` | tuple of `InterpretationRuleReference` | default empty |
| 10 | `evidence` | tuple of `InterpretationEvidence` | default empty |
| 11 | `findings` | tuple of `InterpretationFinding` | default empty |
| 12 | `metadata` | `InterpretationMetadata` | default fresh metadata |
| 13 | `errors` | tuple of error `InterpretationIssue` | default empty |
| 14 | `warnings` | tuple of warning `InterpretationIssue` | default empty |

Zero subjects, sources, rules, evidence, and findings form a valid complete
empty snapshot. When content exists, IDs and roles obey their documented
unique scopes and every reference resolves. Caller sequence order is canonical;
the boundary does not sort by rule, domain, tendency, priority, or identifier.

`interpretation_type` identifies the concrete interpretation family;
`interpretation_version` versions that family; `interpretation_id` is a
caller-supplied snapshot identifier. No automatic UUID, timestamp, locale,
language, timezone, report title, question, audience, or style is added.

## Technical status and partial-data policy

`INTERPRETATION_TECHNICAL_STATUSES` is exactly:

```text
complete, incomplete, invalid
```

Status is construction and completeness only. It never means favorable,
unfavorable, compatible, incompatible, auspicious, inauspicious, confident,
important, severe, recommended, or pass/fail.

- `complete`: errors are empty; every finding is complete; every evidence item
  is referenced by at least one finding; every source and rule is referenced;
  empty content is allowed.
- `incomplete`: at least one error is required; no finding is invalid; at least
  one finding is incomplete or a document error identifies omitted whole
  content.
- `invalid`: at least one error is required and represents a structurally valid
  diagnostic snapshot whose trusted content is invalid. It may retain only
  individually valid audit objects.

Finding `complete` requires no errors and at least one evidence reference.
Finding `incomplete` or `invalid` requires at least one error. Any invalid
finding makes the document invalid; any incomplete finding makes it at least
incomplete. Callers state status explicitly. Factories validate consistency
and never derive, promote, downgrade, or repair it.

Partial diagnostic documents are allowed only through explicit `incomplete`
or `invalid` status and deterministic issues. There is no silent partial
success, missing-content omission, partial score, narrative fallback, or
exception suppression. Malformed model input raises before any document is
returned.

## Reference and consistency rules

Strict document validation includes:

- unique subject IDs and roles, source IDs, rule IDs, evidence IDs, and finding
  IDs;
- unique subject and evidence IDs within each referencing tuple;
- finding domains matching their referenced rule-ID domain prefix;
- every finding rule, subject, and evidence reference resolving exactly once;
- every evidence source and subject reference resolving exactly once;
- complete documents having no orphan source or rule objects and every
  evidence object referenced by exactly one finding;
- evidence IDs never being shared by multiple findings, including incomplete
  and invalid diagnostic documents;
- non-empty evidence source paths and non-negative integer path indexes;
- exact status, tendency, domain, evidence-relation, and issue-category
  vocabularies;
- exact model types, field order, schema identifier, and schema version;
- error/warning placement and status consistency;
- finite numbers and boolean-as-number rejection at numeric-only positions;
- permitted null only in an observed value, issue detail, or recursive value;
- unknown fields, malformed identifiers, unsupported values, cycles, aliases,
  and foreign objects; and
- deterministic first failure in canonical root and nested field order.

Wrong model or nested types raise `TypeError`. Correctly typed but invalid
values or relationships raise `ValueError`. Exact exception prose is not
public; exception class and deterministic failing path are contractual.
Unexpected dependency and programming exceptions propagate.

The generic foundation does not validate domain calculations or fetch a source
snapshot. Future adapters must validate source results through their owning
contract before constructing sources and evidence. They must not infer missing
fields, reinterpret a source's status, or silently repair it.

## Relationship to Sprint 10 Prediction

Sprint 10 remains unchanged and is not forcibly migrated. Its Prediction
context, results, rule results, composed output, and structured explanation
objects may become source result families only after a future adapter validates
the exact existing contract. They do not become Interpretation models merely
because they contain fields named evidence, reasons, factors, explanations, or
confidence.

The current Prediction foundations are permissive in places: they may normalize
identifiers, clamp confidence, replace non-finite values, stringify unsupported
objects, or return safe empty output for malformed input. Those behaviors
remain backward-compatible within Sprint 10, but they do not satisfy this
strict boundary's precomputed trust contract. Task 13.1 neither copies those
helpers nor changes them.

Existing Prediction IDs such as `career.001` remain source identifiers; they
are not silently rewritten into versioned Interpretation rule IDs. Existing
Prediction confidence remains source data and is not treated as boundary
confidence. The Sprint 10 explanation layer remains structured output but is
not a narrative generator and is not replaced here.

## Explanation and generation boundary

The layers are deliberately distinct:

1. validated domain results own calculated facts;
2. `InterpretationEvidence` references individual source fields;
3. a versioned deterministic rule owns the non-narrative
   `InterpretationFinding` and its tendency;
4. a future template contract may select approved wording without changing the
   finding;
5. a future narrative or AI-assisted layer may word validated findings only
   under a separately approved contract; and
6. Reporting and rendering may present that output through separately approved
   adapters.

Task 13.1 defines only the data contract at steps 2 and 3. It does not
evaluate the referenced rule or define steps 4 through 6. No later layer may
mutate, recalculate, silently omit, or contradict the source facts, evidence,
rule identity, or finding stored at this boundary.

## Relationship to Sprint 12 Reporting

Interpretation models are not `ReportDocument`, `ReportSection`, or
`ReportBlock` models. Reporting owns already-computed report-shaped content;
Interpretation owns traceable structured findings before future wording and
presentation. A later, separately specified adapter may validate an
`InterpretationDocument` and copy selected facts into approved Reporting block
schemas.

Task 13.1 does not add that adapter, register a new Reporting block kind,
change Reporting serializers, insert Interpretation into a report, generate a
title or note, or render content. The Reporting schema remains
`bhaktiastro.reporting.document` version `1.0` and is not replaced or extended
by this specification.

## Public API plan

Runtime implementation will create additive exports under
`backend.app.interpretation`. It will export the eight models; the
`InterpretationScalar`, `InterpretationValue`, and `InterpretationJsonValue`
aliases; the six constants below; and only these keyword-only functions.

### Construction APIs

```python
create_interpretation_metadata(*, schema_id: object,
    source_component: object, source_version: object = "",
    deterministic: object = True,
    attributes: object = None) -> InterpretationMetadata
create_interpretation_subject_reference(*, subject_id: object, role: object,
    label: object = "", metadata: object = None
    ) -> InterpretationSubjectReference
create_interpretation_source(*, source_id: object, domain: object,
    result_family: object, result_version: object = "",
    reference: object = "", metadata: object = None) -> InterpretationSource
create_interpretation_rule_reference(*, rule_id: object, owner: object,
    rule_version: object, source_reference: object = "",
    metadata: object = None) -> InterpretationRuleReference
create_interpretation_evidence(*, evidence_id: object, source_id: object,
    source_path: object, relation: object, observed_value: object,
    subject_ids: object = (), metadata: object = None
    ) -> InterpretationEvidence
create_interpretation_issue(*, code: object, message_key: object,
    path: object = (), category: object = "error",
    details: object = None) -> InterpretationIssue
create_interpretation_finding(*, finding_id: object, rule_id: object,
    domain: object, topic: object, category: object,
    status: object = "complete", tendency: object,
    subject_ids: object = (), evidence_ids: object = (),
    errors: object = (), warnings: object = (), metadata: object = None
    ) -> InterpretationFinding
create_interpretation_document(*, interpretation_type: object,
    interpretation_version: object, interpretation_id: object,
    status: object = "complete", subjects: object = (),
    sources: object = (), rules: object = (), evidence: object = (),
    findings: object = (), metadata: object = None, errors: object = (),
    warnings: object = ()) -> InterpretationDocument
```

Factories perform complete strict validation and defensive copying and never
return a partially constructed object.

### Strict validation APIs

```python
validate_interpretation_evidence(*, evidence: object
    ) -> InterpretationEvidence
validate_interpretation_finding(*, finding: object
    ) -> InterpretationFinding
validate_interpretation_document(*, document: object
    ) -> InterpretationDocument
```

Validators accept only the exact immutable runtime model, recursively verify
all invariants, and return the same instance on success. They do not hydrate a
mapping, normalize values, or call a factory to repair content.

### Serialization API

```python
serialize_interpretation_document(*, document: object
    ) -> dict[str, InterpretationJsonValue]
```

The serializer accepts only an exact valid document and returns a fresh
mutable built-in dictionary/list tree. There is no generic model serializer,
deserializer, JSON text generator, source adapter, narrative generator,
template selector, remedy generator, AI client, report adapter, repository, or
API endpoint.

## Canonical serialization

Root and nested keys follow the exact documented model field order. Subject,
source, rule, evidence, finding, issue, warning, path, and reference order is
stable caller order after validation. No collection is sorted and no explicit
order integer is added.

Serialization converts frozen models to fresh dictionaries, tuples to fresh
lists, mapping proxies to fresh dictionaries, and values to built-in JSON
scalars and containers. No dataclass, enum, tuple, custom mapping, custom
object, cycle, alias, NaN, or infinity escapes. Empty collections remain empty
collections and are not omitted or converted to null. Integers remain
integers, finite floats remain floats, fractional values are preserved without
rounding, and `-0.0` becomes `0.0`.

Every call returns an equal but deeply independent graph. Mutating serialized
output cannot affect the runtime model, another serialization, another
document, or module constants. Output must pass
`json.dumps(payload, allow_nan=False)` without a custom encoder.

## Schema and compatibility policy

The initial constants are:

```text
INTERPRETATION_SCHEMA_ID = "bhaktiastro.interpretation.document"
INTERPRETATION_SCHEMA_VERSION = "1.0"
INTERPRETATION_TECHNICAL_STATUSES = ("complete", "incomplete", "invalid")
INTERPRETATION_TENDENCIES =
    ("supportive", "challenging", "mixed", "neutral", "informational")
INTERPRETATION_EVIDENCE_RELATIONS =
    ("supporting", "opposing", "contextual")
INTERPRETATION_DOMAINS =
    ("kundali", "matchmaking", "panchang", "dasha", "prediction",
     "yoga", "dosha", "transit")
```

The root schema ID and version are factory-owned. The interpretation family
has its separate caller-provided version. Within schema `1.0`, fixes may
restore documented behavior and additive Python exports may be reviewed
without changing valid output. Adding, removing, renaming, reordering, or
repurposing fields; changing a type, nullability, status, tendency, domain,
evidence relation, identifier rule, ordering, reference, or serialization
meaning is breaking and requires a specification and schema-version decision.

Rule changes follow the rule-ID policy above. Vocabulary additions are schema
changes, not silently accepted strings. Deprecation requires an announced
transition, replacement reference, continued support during the approved
period, and an explicit removal task. Task 13.1 defines no schema negotiation,
migration, compatibility reader, or deserialization.

This plan is additive. It changes no Sprint 10, Matchmaking, Reporting,
Kundali, Panchang, Dasha, Yoga, Dosha, Transit, API, serializer, or public
export. Runtime implementation must preserve those contracts and must not
force existing objects into this hierarchy.

## Explicit exclusions

Task 13.1 excludes:

- astrology, chart, score, Dasha, Yoga, Dosha, transit, prediction, or
  compatibility calculation;
- domain-specific interpretation rules, rule evaluation, missing-result
  inference, source-result mutation, aggregation, or confidence conversion;
- interpretation prose, prediction narrative, summaries, explanations,
  recommendations, remedies, advice, compatibility verdicts, marriage
  suitability judgments, pass/fail labels, or certainty claims;
- AI or language-model calls, prompts, embeddings, retrieval, network access,
  or automatic wording;
- template selection, localization, translation, locale, language, audience,
  style, time-horizon, or question processing;
- Reporting adapters, report composition, HTML, Markdown rendering, PDF,
  email, UI, frontend, image, chart, layout, or Sprint 17 work;
- API endpoints, transport schemas, persistence, databases, ORM models,
  caching, authentication, telemetry, or background jobs;
- Sprint 10 migration or rewrite, Sprint 11 changes, Sprint 12 changes,
  runtime code, tests, public exports, serializers, and any later Sprint 13
  implementation task.

## Required future runtime tests

Runtime implementation is not complete until tests cover:

- all eight exact immutable model types, deliberate unhashability, structural
  equality, exact field order, constants, aliases, and schema version;
- zero-subject, single-subject, directional two-subject, and multi-subject
  documents with unique IDs and roles and stable reference order;
- empty complete documents and populated complete, explicit incomplete, and
  diagnostic invalid documents;
- deterministic source, rule, evidence, finding, error, and warning order;
- each supported domain, technical status, tendency, evidence relation, and
  issue category, plus every unsupported vocabulary case;
- valid versioned rule IDs, malformed IDs, ownership/version mismatch,
  duplicate rule references, and supersession-neutral stability;
- duplicate finding, evidence, source, subject, and role IDs; duplicate IDs in
  reference tuples; missing evidence; empty source paths; malformed subject,
  source, rule, and evidence references; orphan complete-document objects; and
  finding-domain/rule-domain mismatch;
- status/error consistency, complete findings without evidence, malformed
  incomplete/invalid findings, misplaced issues, and duplicate issues;
- every permitted scalar and recursive value, null boundaries, finite numeric
  values, fractional values, and `-0.0` behavior;
- boolean-as-number, NaN, both infinities, complex, `Decimal`, enums, foreign
  dataclasses, sets/frozensets, bytes-like values, date/time values,
  exceptions, callables, generators, custom containers, and arbitrary objects;
- unknown fields, invalid identifiers and versions, leading/trailing
  whitespace, case changes, cycles, and shared mutable paths;
- defensive copying, immutable runtime collections, independent defaults,
  independent documents, serialization mutation isolation, and no source
  mutation;
- exact root and nested serialization order, fresh built-in dictionaries and
  lists, repeated deterministic output, empty collections, and
  `json.dumps(..., allow_nan=False)`;
- exact keyword-only public signatures, exports, and import smoke;
- unchanged Sprint 10 Prediction outputs and APIs, Sprint 12 Reporting models
  and serializer, Sprint 11 Matchmaking behavior, focused dependency
  regressions, and complete project regression; and
- configured formatting, compilation, and diff checks.

Runtime tests use structural synthetic data and must not invent an astrology
interpretation, astronomical expected value, rule outcome, confidence, or
narrative.

## Canonical test-vector plan

No interpretation vector file is created by this documentation task. Future
`docs/test-vectors/interpretation.md` vectors will use the approved vector
format and cover only reviewed structural cases:

- zero-subject interpretation;
- single-subject finding;
- directional two-subject finding;
- multiple evidence references;
- mixed supporting and opposing evidence;
- invalid rule identifier;
- duplicate finding ID;
- missing evidence;
- deterministic serialization; and
- mutation isolation.

Vectors remain `pending` until the immutable models and reviewed structural
expected payloads exist. No astrology rule, interpretation, tendency outcome,
confidence, prose, or independent astronomical value is fabricated here.

## Planned implementation references

Planned additive runtime package: `backend/app/interpretation/`.

Planned focused coverage:

- `backend/tests/test_interpretation_models.py`;
- `backend/tests/test_interpretation_validation.py`;
- `backend/tests/test_interpretation_serialization.py`; and
- `backend/tests/test_interpretation_public_api.py`.

These paths are plans, not runtime artifacts created by this task.

## Change history and supersession

| Version | Change |
| --- | --- |
| `1.0` | Approved the documentation-only Interpretation Data Boundary Foundation contract. |

A future change must identify compatibility impact, update this history, make
an explicit schema decision, and name any superseded contract. This
specification does not supersede Prediction, Matchmaking, or Reporting.
