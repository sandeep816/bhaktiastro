# SPEC-REPORTING-001 - Report Data Model Foundation

| Field | Value |
| --- | --- |
| Status | `approved` |
| Specification version | `1.0` |
| Owning domain | Reporting |
| Related ADRs | [ADR-001](../architecture/ADR-001-Project-Principles.md), [ADR-002](../architecture/ADR-002-Astrology-Calculation-Standards.md), [ADR-003](../architecture/ADR-003-Validation-Standards.md), [ADR-004](../architecture/ADR-004-Public-API-Contracts.md), [ADR-005](../architecture/ADR-005-Testing-Standards.md) |
| Related Sprint task | [Sprint 12, Task 12.1](../SPRINT-12.md#task-121---report-data-model-foundation) |
| Implementation status | `not_started` |
| Test-vector status | `pending` |
| Backward compatibility | Additive foundation; no existing public contract changes |

This is the permanent source of truth for the Sprint 12.1 Report Data Model
Foundation. It defines a future runtime contract; approval does not mean that
runtime code, tests, adapters, renderers, or domain reports exist.

## Scope

The Reporting foundation models already-computed structured information as
small, reusable, domain-neutral report objects. It provides stable identity,
zero or more ordered subjects, zero or more ordered sections, typed content
blocks, technical states, provenance, metadata, issues, notes, and strict
serialization.

Future Kundali, Matchmaking, Panchang, Dasha, Prediction, Yoga, Dosha,
Transit, and other adapters may construct these models. Task 12.1 does not
implement those adapters or define their payload semantics.

The foundation is calculation-free, rendering-free, and interpretation-free.
It never derives astrology, normalizes birth data, scores results, creates
narrative, or changes a source result.

## Dependencies and architectural boundaries

- ADR-001 requires one small additive foundation with no future-task work.
- ADR-002 keeps calculation, orchestration, serialization, presentation, and
  interpretation separate.
- ADR-003 requires strict trust boundaries, deterministic failure, finite
  numbers, and no silent coercion or repair.
- ADR-004 makes public names, signatures, field order, status vocabulary,
  identifiers, versions, and serialization behavior contractual.
- ADR-005 requires focused model, boundary, invalid-input, ordering,
  mutation-safety, serialization, import, Matchmaking-regression, and full
  regression evidence during runtime implementation.

The completed [Matchmaking specification](MATCHMAKING.md) remains canonical
for Sprint 11. Its typed mappings and serializers are architectural evidence,
not base classes for Reporting. No current Matchmaking result is automatically
a Reporting model.

## Terminology

- **Document**: one complete, incomplete, or invalid technical report snapshot.
- **Subject**: one caller-identified entity in an ordered report role.
- **Section**: an ordered semantic grouping of blocks.
- **Block**: one tagged, strictly validated unit of report content.
- **Field**: a stable identifier, display label, and already-computed value.
- **Issue**: a technical error or warning with a stable code and path.
- **Source**: optional provenance for already-computed input or content.
- **Metadata**: deterministic, schema-identified technical attributes.
- **Status**: technical construction/completeness state only.

## Selected model hierarchy

Task 12.1 selects eight public immutable runtime models:

1. `ReportDocument`
2. `ReportSubject`
3. `ReportSection`
4. `ReportBlock`
5. `ReportField`
6. `ReportIssue`
7. `ReportMetadata`
8. `ReportSource`

Each is a frozen, slotted dataclass. Nested sequences are tuples. Nested
mappings are read-only mapping proxies over newly allocated dictionaries.
Constructors are private to the module; public factory functions perform full
validation and defensive copying.

Models use same-class structural equality, including tuple order and mapping
iteration order. They are deliberately unhashable because recursive report
values can contain mappings. Equality does not perform astrology, normalize
identifiers, sort content, or ignore metadata.

`ReportValue` is a public recursive type alias, not a ninth model. No generic
`ReportNode`, recursive subsection, arbitrary dataclass wrapper, Pydantic API
model, ORM model, or mutable dictionary result is part of Task 12.1.

## Shared runtime representation

| Concept | Constructor input | Immutable runtime | Serialized output |
| --- | --- | --- | --- |
| Ordered sequence | non-string `Sequence` using list or tuple | tuple | list |
| Ordered mapping | `Mapping` with exact string keys | mapping proxy over fresh dict | fresh dict |
| Scalar | string, boolean, integer, finite float, or permitted null | same scalar; `-0.0` becomes `0.0` | same JSON scalar |
| Model | exact Reporting model | frozen model | ordered dict defined by that model |

Factories copy every accepted container recursively. No caller-owned mutable
container or nested path is retained. Mutable defaults are prohibited. No two
models or sibling paths share a mutable object.

## Report value contract

The recursive public value vocabulary is exactly:

```text
ReportScalar = str | bool | int | finite float | None
ReportValue = ReportScalar | tuple[ReportValue, ...]
              | read-only ordered mapping[str, ReportValue]
ReportJsonValue = ReportScalar | list[ReportJsonValue]
                  | dict[str, ReportJsonValue]
```

`ReportJsonValue` exists only at the serialization ownership boundary; runtime
models never retain its mutable list or dictionary containers.

Constructor inputs may use built-in lists or tuples for sequences and any
well-behaved `Mapping`, including a mapping proxy or mapping subclass, where a
mapping is declared. The factory validates and copies them. Mapping keys must
be exact valid identifiers unless a kind-specific payload explicitly declares
another fixed key. Mapping and sequence iteration order is preserved.

Enums, dataclass instances other than the exact expected Reporting model,
sets, frozensets, bytes, bytearray, memoryview, `Decimal`, date/time/datetime,
exceptions, callables, generators, custom non-mapping containers, complex
numbers, arbitrary objects, NaN, and either infinity are rejected. Booleans
are rejected wherever an integer or float is specifically required. Unsupported
values are never stringified, omitted, replaced with null, or otherwise
repaired.

Null is allowed only at an explicitly nullable block value, table cell,
subject input-summary value, issue-detail value, or list item. It is forbidden
for identifiers, versions, labels, titles, statuses, metadata structural
fields, numeric score fields, and model collections.

Direct and indirect cycles are rejected. A mutable input list or mapping
reachable through two semantic paths is rejected rather than silently
de-aliased. Immutable scalar reuse is harmless. Runtime construction produces
an alias-free immutable graph.

## Identifier and text standards

All machine identifiers use lowercase ASCII and match:

```text
^[a-z][a-z0-9]*(?:[._-][a-z0-9]+)*$
```

They are 1 through 128 characters. This applies to `report_type`, `report_id`,
`subject_id`, `role`, `section_id`, `block_id`, `block_kind`, `field_id`,
`source_id`, `source_type`, `issue_code`, metadata keys, and schema
identifiers. Message keys use the same syntax and should be dot-separated.

Schema and report versions match `^[0-9]+\.[0-9]+(?:\.[0-9]+)?$` and are at
most 32 characters. No identifier or version is trimmed, case-folded,
slugified, aliased, or silently normalized. Leading/trailing whitespace,
empty strings, uppercase, invalid characters, and over-length values are
rejected.

Human-facing `title`, `label`, `text`, and `note` values preserve casing and
internal whitespace. Required display text must be non-empty and must not have
leading/trailing whitespace. The foundation does not translate or localize it.

## ReportMetadata

`ReportMetadata` is a limited dedicated model, not an arbitrary recursive
dictionary.

| Position | Field | Type | Required/default |
| ---: | --- | --- | --- |
| 1 | `schema_id` | identifier string | required |
| 2 | `source_component` | identifier string | required |
| 3 | `source_version` | version string or empty string | default empty |
| 4 | `deterministic` | boolean | default `true`; Task 12.1 requires `true` |
| 5 | `attributes` | ordered mapping of identifier to non-null scalar | default empty |

Top-level unknown fields are rejected. Attribute keys are unique, preserve
caller order, and follow the identifier rule. Attribute values are only
string, boolean, integer, or finite float; null and nested containers are not
allowed. This prevents metadata from becoming a second content payload.

No factory adds timestamps, UUIDs, paths, usernames, hostnames, environment
variables, process data, telemetry, random values, locale, or platform facts.

Where another Reporting model declares `metadata=None`, its factory creates a
new `ReportMetadata` with exactly:

```text
schema_id = "bhaktiastro.reporting.metadata"
source_component = "bhaktiastro.reporting"
source_version = "1.0"
deterministic = true
attributes = {}
```

This is factory-owned deterministic provenance, not inferred environment
data. Each model receives an independently allocated immutable metadata value;
there is no shared mutable default.

## ReportSource

Provenance is included as an optional ordered document-level sequence. It is
factual metadata only and performs no fetching, verification, persistence, or
citation rendering.

| Position | Field | Type | Required/default |
| ---: | --- | --- | --- |
| 1 | `source_id` | identifier string | required; unique in document |
| 2 | `source_type` | identifier string | required |
| 3 | `reference` | string | default empty |
| 4 | `version` | version string or empty string | default empty |
| 5 | `note` | string | default empty |

`reference` is an opaque caller-provided identifier or URI string. The
foundation does not validate external availability or trust. Empty optional
strings remain empty rather than null.

## ReportIssue

Issues are domain-neutral and localization-ready.

| Position | Field | Type | Required/default |
| ---: | --- | --- | --- |
| 1 | `code` | identifier string | required |
| 2 | `message_key` | identifier string | required |
| 3 | `path` | tuple of identifier strings or non-negative integers | default empty |
| 4 | `category` | `error` or `warning` | required |
| 5 | `details` | ordered mapping of identifier to `ReportValue` | default empty |

Human-readable error messages are not a public contract. A later localization
consumer may resolve `message_key`; Task 12.1 does not.

Issue order is caller sequence order for explicitly supplied issues and
canonical field traversal for validator-generated failures. An exact duplicate
issue is rejected. The same code may occur at different paths. Errors lists
contain only `category="error"`; warnings lists contain only
`category="warning"`. Notes remain ordered strings and do not reuse this model.

## ReportField

`ReportField` is used by `key_value` blocks and other built-in payload schemas.

| Position | Field | Type | Required/default |
| ---: | --- | --- | --- |
| 1 | `field_id` | identifier string | required; unique within its block |
| 2 | `label` | non-empty string | required |
| 3 | `value` | `ReportValue` | required; null allowed |
| 4 | `unit` | identifier string or empty string | default empty |
| 5 | `metadata` | `ReportMetadata` | default fresh foundation metadata |

The value is copied, never calculated or formatted. A unit is a stable token,
not localized display text.

## ReportSubject

| Position | Field | Type | Required/default |
| ---: | --- | --- | --- |
| 1 | `subject_id` | identifier string | required; unique in document |
| 2 | `role` | identifier string | required; unique in document |
| 3 | `label` | string | default empty |
| 4 | `input_schema` | schema identifier or empty string | default empty |
| 5 | `input_summary` | ordered mapping to `ReportValue` | default empty |
| 6 | `metadata` | `ReportMetadata` | default fresh foundation metadata |

Zero-, one-, two-, and multi-subject reports are supported. Direction is
represented by caller sequence order plus explicit unique roles; no gender or
role is inferred. Subject IDs and roles must both be unique. One subject entry
cannot represent multiple roles, and duplicate IDs are not permitted under
different roles.

When `input_summary` is non-empty, `input_schema` is required. An empty
summary may use an empty schema. The foundation validates only generic value
safety; a future adapter owns its named input schema. Generic subjects do not
contain birth data, astrology fields, or normalization logic. An adapter may
copy already-normalized facts into its schema-identified summary.

## ReportSection

| Position | Field | Type | Required/default |
| ---: | --- | --- | --- |
| 1 | `section_id` | identifier string | required; unique in document |
| 2 | `title` | non-empty string | required |
| 3 | `status` | technical status | default `complete` |
| 4 | `blocks` | tuple of `ReportBlock` | default empty |
| 5 | `errors` | tuple of error `ReportIssue` | default empty |
| 6 | `warnings` | tuple of warning `ReportIssue` | default empty |
| 7 | `notes` | tuple of non-empty strings | default empty |
| 8 | `metadata` | `ReportMetadata` | default fresh foundation metadata |

Section order is only its position in `ReportDocument.sections`. There is no
`order` field. Empty sections are valid, including a complete section whose
domain result has no items. Sections cannot contain subsections. Recursive
section nesting and an explicit order integer are excluded.

Block IDs are unique within their section. Section IDs are unique within the
document. A block ID may repeat in another section because its full path is
`section_id/block_id`.

## ReportBlock and selected block architecture

Task 12.1 chooses one immutable `ReportBlock` model with a strict `kind`
discriminator and kind-specific payload schema. It does not choose multiple
block subclasses or an unrestricted arbitrary payload.

| Position | Field | Type | Required/default |
| ---: | --- | --- | --- |
| 1 | `block_id` | identifier string | required |
| 2 | `kind` | one exact block-kind identifier | required |
| 3 | `title` | string | default empty |
| 4 | `payload_schema` | exact schema identifier | required |
| 5 | `payload` | immutable ordered mapping | required |
| 6 | `metadata` | `ReportMetadata` | default fresh foundation metadata |

The stable `REPORT_BLOCK_KINDS` tuple is exactly:

```text
key_value, score, status, list, table, note, reference
```

`summary` is represented by a section and `key_value` content; it is not a
duplicate block kind. `structured` is deferred because Task 12.1 has no
domain-schema registry capable of validating arbitrary payload semantics.

### Built-in payload contracts

Payload keys and their order are exact:

| Kind | Required `payload_schema` | Exact payload fields | Rules |
| --- | --- | --- | --- |
| `key_value` | `report.block.key_value.v1` | `fields` | Non-empty tuple of `ReportField`; unique field IDs; caller order preserved. |
| `score` | `report.block.score.v1` | `score`, `maximum_score`, `unit` | Finite non-boolean numbers; `maximum_score > 0`; `0 <= score <= maximum_score`; non-empty unit identifier. No calculation or rounding. |
| `status` | `report.block.status.v1` | `status_id`, `label` | Valid identifier and non-empty label. This may copy a domain status but must not be confused with technical model status. |
| `list` | `report.block.list.v1` | `items` | Tuple of `ReportValue`; may be empty; order preserved. |
| `table` | `report.block.table.v1` | `columns`, `rows` | Columns are exact mappings `column_id`, `label`, `unit`; IDs unique; each row is a tuple of scalar values with exactly the column count. Empty rows allowed. |
| `note` | `report.block.note.v1` | `text` | One required non-empty caller-provided string; no generated narrative. |
| `reference` | `report.block.reference.v1` | `source_id` | One source identifier that must resolve in the containing document. |

Unknown kinds, schemas, payload fields, missing fields, reordered fields, and
kind/schema mismatches are rejected. `note` stores already-provided text; it
does not authorize interpretation or generation. `table` is semantic tabular
data, not styling. No block contains HTML, Markdown, CSS, template directives,
rendering hints, column widths, colors, pagination, or layout instructions.

## ReportDocument

The canonical root fields are exact and ordered:

| Position | Field | Type | Required/default |
| ---: | --- | --- | --- |
| 1 | `schema_id` | `bhaktiastro.reporting.document` | factory-owned constant |
| 2 | `schema_version` | `1.0` | factory-owned constant |
| 3 | `report_type` | identifier string | required |
| 4 | `report_version` | version string | required; report-family version |
| 5 | `report_id` | identifier string | required; caller-provided |
| 6 | `title` | non-empty string | required |
| 7 | `status` | technical status | default `complete` |
| 8 | `subjects` | tuple of `ReportSubject` | default empty |
| 9 | `sections` | tuple of `ReportSection` | default empty |
| 10 | `sources` | tuple of `ReportSource` | default empty |
| 11 | `metadata` | `ReportMetadata` | default fresh foundation metadata |
| 12 | `errors` | tuple of error `ReportIssue` | default empty |
| 13 | `warnings` | tuple of warning `ReportIssue` | default empty |
| 14 | `notes` | tuple of non-empty strings | default empty |

`schema_id` identifies this generic contract; `report_type` identifies a
family; `report_id` identifies one caller-defined document; `report_version`
versions the family contract; and `schema_version` versions this generic
foundation. They are separate and cannot substitute for one another.

Zero subjects and zero sections are valid. A title and caller-supplied report
ID are required even for a zero-subject document. Unknown root fields are
rejected. There is no automatic UUID, timestamp, locale, language, timezone,
environment metadata, or generated title. Null is not a missing-field marker.

Subject IDs, subject roles, section IDs, and source IDs are unique in their
document. Every reference block must name exactly one supplied source.

## Technical status contract

`REPORT_TECHNICAL_STATUSES` is exactly:

```text
complete, incomplete, invalid
```

These values describe construction/completeness only. They never mean
horoscope quality, compatibility, auspiciousness, prediction confidence,
marriage suitability, severity, recommendation, or pass/fail.

Status consistency is strict:

- `complete`: errors are empty and every section is `complete`; warnings and
  empty content are allowed.
- `incomplete`: at least one error is required; no section may be `invalid`;
  at least one section is `incomplete`, or the document error explicitly
  identifies omitted whole content such as an absent section.
- `invalid`: at least one error is required; it represents a structurally
  valid diagnostic snapshot whose trusted content is invalid. It may retain
  only individually valid audit blocks and sections.

Section `complete` requires no errors. Section `incomplete` or `invalid`
requires at least one error. A document is `invalid` if any included section
is `invalid`; it is at least `incomplete` if any section is `incomplete`.
Callers provide the status explicitly; factories validate consistency and do
not silently promote, downgrade, or derive it.

Warnings never change status. Missing/malformed content is never silently
omitted. A caller may explicitly construct an incomplete or invalid diagnostic
document only from structurally valid models plus deterministic issues.
Malformed models, malformed blocks, and inconsistent statuses are rejected
before construction. This is explicit partial reporting, not partial success.

## Public API plan

Runtime implementation will create `backend.app.reporting` and export the
eight models named above; the `ReportScalar`, `ReportValue`, and
`ReportJsonValue` type aliases; `REPORT_SCHEMA_ID`, `REPORT_SCHEMA_VERSION`,
`REPORT_TECHNICAL_STATUSES`, and `REPORT_BLOCK_KINDS`; and these 12
keyword-only functions. Existing package exports remain unchanged.

### Construction APIs (8)

```python
create_report_metadata(*, schema_id: object, source_component: object,
    source_version: object = "", deterministic: object = True,
    attributes: object = None) -> ReportMetadata
create_report_source(*, source_id: object, source_type: object,
    reference: object = "", version: object = "",
    note: object = "") -> ReportSource
create_report_issue(*, code: object, message_key: object,
    path: object = (), category: object = "error",
    details: object = None) -> ReportIssue
create_report_field(*, field_id: object, label: object, value: object,
    unit: object = "", metadata: object = None) -> ReportField
create_report_subject(*, subject_id: object, role: object,
    label: object = "", input_schema: object = "",
    input_summary: object = None, metadata: object = None) -> ReportSubject
create_report_block(*, block_id: object, kind: object, title: object = "",
    payload_schema: object, payload: object,
    metadata: object = None) -> ReportBlock
create_report_section(*, section_id: object, title: object,
    status: object = "complete", blocks: object = (), errors: object = (),
    warnings: object = (), notes: object = (),
    metadata: object = None) -> ReportSection
create_report_document(*, report_type: object, report_version: object,
    report_id: object, title: object, status: object = "complete",
    subjects: object = (), sections: object = (), sources: object = (),
    metadata: object = None, errors: object = (), warnings: object = (),
    notes: object = ()) -> ReportDocument
```

Factories accept raw constructor values, perform full strict validation,
defensively copy them into immutable models, and return no partially
constructed object. They do not accept unknown keyword arguments.

### Strict validation APIs (3)

```python
validate_report_block(*, block: object) -> ReportBlock
validate_report_section(*, section: object) -> ReportSection
validate_report_document(*, report: object) -> ReportDocument
```

Validators accept only the exact completed runtime model type, recursively
check all invariants, and return the same immutable instance on success. They
do not hydrate mappings, call factories to repair content, or accept a generic
dictionary that resembles a model.

### Serialization API (1)

```python
serialize_report_document(*, report: object) -> dict[str, ReportJsonValue]
```

The serializer accepts only an exact valid `ReportDocument`, calls strict
validation, and returns a fresh mutable built-in mapping/list tree. There is
no generic `serialize_report_model`, JSON-string generator, renderer, writer,
or deserializer.

All APIs are deterministic, do not mutate inputs, and fail fast in canonical
field order. A wrong outer/nested type raises `TypeError`; a correctly typed
but invalid value, identifier, duplicate, order, status, schema, payload, or
cross-field relationship raises `ValueError`. Exact human-readable exception
text is not a public contract; exception class, first failing field/path, and
stable issue codes are.

## Strict validation contract

Runtime validation must cover:

- exact model and nested types;
- required, missing, unexpected, and reordered fields at mapping payloads;
- required non-empty text and identifiers;
- identifier/version syntax without normalization;
- duplicate subject IDs, roles, section IDs, source IDs, block IDs within a
  section, field IDs within a block, column IDs, and exact duplicate issues;
- status vocabulary and report/section/error consistency;
- allowed block kinds, exact payload schemas, exact payload field order, and
  kind-specific types/ranges;
- reference blocks resolving to document sources;
- metadata top-level shape, scalar-only attributes, and deterministic flag;
- issue code, key, path, category, details, list placement, and order;
- schema version exactly `1.0`;
- finite integer/float handling, boolean-as-number rejection, and no rounding;
- null only at explicitly permitted value positions;
- unsupported objects, mappings, sequences, custom values, cycles, and shared
  mutable aliases; and
- structurally valid complete, incomplete, and invalid snapshots.

Validation does not calculate source data or prove a domain-specific payload.
Future adapters must validate their own source result and map it into one of
the built-in block schemas. There is no generic mapping hydration or
deserialization trust boundary in Task 12.1.

## Canonical serialization

Serialized root field order is the exact 14-field `ReportDocument` order.
Nested model field order is the exact order documented in each model table.
Subjects, sections, blocks, fields, columns, rows, sources, issues, warnings,
and notes preserve caller sequence order after validation. Metadata and value
mappings preserve validated insertion order. Consumers may rely on this order
for schema `1.0`; no sort changes semantic order and no explicit order integer
exists.

Serialization recursively converts:

- frozen models to fresh dictionaries;
- tuples to fresh lists;
- mapping proxies to fresh dictionaries; and
- valid scalars to their JSON equivalents.

No enum, dataclass object, tuple, set, bytes, custom mapping, custom object,
cycle, alias, NaN, or infinity escapes. Empty tuples/mappings become empty
lists/dicts and are never omitted or converted to null. Integers remain
integers, finite floats remain floats, fractional values are unchanged, and
`-0.0` is canonicalized to `0.0`. Null is retained only where permitted.

Every call returns an equal but deeply independent tree. Mutating one
serialization cannot affect the runtime document, another serialization,
another report, or module constants. The result must pass
`json.dumps(payload, allow_nan=False)` without a custom encoder.

Direct JSON text generation, indentation, key sorting, file writing, content
type selection, persistence, and schema migration are excluded.

## Schema identifiers and versioning

The initial constants are:

```text
REPORT_SCHEMA_ID = "bhaktiastro.reporting.document"
REPORT_SCHEMA_VERSION = "1.0"
REPORT_TECHNICAL_STATUSES = ("complete", "incomplete", "invalid")
REPORT_BLOCK_KINDS =
    ("key_value", "score", "status", "list", "table", "note", "reference")
```

`ReportDocument.schema_id` is always `REPORT_SCHEMA_ID`, and
`ReportDocument.schema_version` is always `REPORT_SCHEMA_VERSION`.
`report_version` is separate and caller-provided for the concrete report
family. Built-in block payload schema IDs are versioned independently but are
part of the foundation schema contract.

Within schema `1.0`, bug fixes may restore documented behavior and additive
Python exports may be introduced without changing valid output. Adding,
removing, renaming, reordering, or changing a model field; changing type,
nullability, status vocabulary, block kind, payload schema, identifier rule,
ordering, or serialization semantics; or repurposing a field is breaking and
requires an explicit specification and schema-version decision.

Report-family evolution uses `report_version` and cannot silently redefine
the generic schema. Deprecated exports or block kinds require an announced
transition and remain supported until a separately approved removal. Task
12.1 includes no schema negotiation, compatibility reader, deserialization,
or migration framework.

The existing Matchmaking schema remains `1.0` in its own namespace. Reporting
schema `1.0` does not replace, alias, or imply compatibility with it.

## Relationship to existing and future domains

### Sprint 11 Matchmaking

- Sprint 11 and `SPEC-MATCHMAKING-001` remain unchanged.
- `backend/app/matchmaking/compatibility_report.py` is not rewritten.
- Sprint 11 serializers are not replaced or wrapped.
- No Matchmaking object automatically becomes a `ReportDocument`.
- No Matchmaking adapter or compatibility report migration is included.
- A later adapter may validate a Matchmaking result through its owning
  serializer and copy facts into this model under a separate contract.

### Other domains

Kundali, Panchang, Dasha, Prediction, Yoga, Dosha, Transit, and future domains
retain their existing result contracts. Task 12.1 defines no subject schema,
section sequence, block payload, title, interpretation, or report composer for
them. Future focused tasks may add adapters that consume already-computed
validated results and use this foundation without recalculation or mutation.

## Backward compatibility

Task 12.1 is additive. Runtime implementation must not remove, rename, wrap,
or change existing Matchmaking, Kundali, Panchang, Dasha, Prediction, Yoga,
Dosha, Transit, schema, validation, serialization, API, or public export
behavior. It must not change the Sprint 11 Compatibility Report schema or
serializer. The Reporting package will be opt-in and independently versioned.

## Explicit exclusions

Task 12.1 excludes:

- astrology calculation, longitude/Rashi/Nakshatra/house placement, scores,
  compatibility judgments, Dashas, predictions, remedies, interpretation,
  AI-generated text, or source-result mutation;
- Kundali, Matchmaking, Panchang, Dasha, Prediction, Yoga, Dosha, Transit, or
  other domain report families and adapters;
- arbitrary `structured` blocks, custom block registration, report templates,
  plugin systems, or unrestricted payload dictionaries;
- HTML, Markdown, PDF, email, image/chart generation, UI components, CSS,
  rendering, formatting, pagination, or Sprint 17 work;
- API endpoints, Pydantic transport schemas, database/ORM models, persistence,
  caching, authentication, authorization, telemetry, logging frameworks, or
  network access;
- localization and translation engines, locale-dependent formatting,
  language/timezone defaults, automatic timestamps, UUIDs, randomness, or
  environment-derived metadata;
- generic dictionary hydration, deserialization, JSON text generation,
  schema negotiation, or schema migration; and
- Task 12.2 or any later Sprint task.

## Required runtime tests

The runtime task is not complete until tests cover:

- all eight runtime models, exact immutable types, structural equality,
  deliberate unhashability, exact field order, constants, and schema version;
- zero-, one-, directional two-, and multi-subject reports with deterministic
  order, unique IDs, and unique roles;
- zero sections, empty complete sections, ordered sections, ordered blocks,
  every block kind, and exact kind-specific payload schema;
- valid complete, explicitly incomplete, and diagnostic invalid reports;
  status/error inconsistencies and malformed incomplete reports;
- exact issue and warning ordering, categories, paths, details, duplicate
  rejection, and notes separation;
- identifier/version rules, empty required strings, whitespace, invalid
  characters/casing, unknown fields, and all duplicate scopes;
- metadata validation, scalar attributes, source order, reference resolution,
  and prohibition on environment metadata generation;
- string, boolean, finite integer, finite float, fractional, and permitted
  null values; boolean-as-number, NaN, both infinities, complex numbers,
  `Decimal`, and invalid null rejection;
- constructor list/tuple and mapping/mapping-proxy handling; runtime tuple and
  mapping-proxy representation; set, frozenset, bytes-like, enum, foreign
  dataclass, datetime, exception, callable, generator, and custom-object
  rejection;
- direct/indirect cycles and shared mutable alias rejection;
- defensive copying, no shared mutable defaults, no shared report paths,
  immutable nested collections, and independent reports;
- exact serialized root/nested field order, fresh dict/list output, deep
  mutation isolation, repeated deterministic serialization, empty collection
  behavior, integer/float preservation, fractional preservation, and `-0.0`;
- `json.dumps(..., allow_nan=False)` without a custom encoder;
- exact public exports, keyword-only signatures, and import smoke;
- unchanged Matchmaking direct results and serialization, focused Matchmaking
  regressions, and complete project regression; and
- configured formatting and Python compilation checks.

Runtime tests must not invent astronomical values because this foundation
contains no astronomy.

## Canonical test-vector plan

No populated vector file is created by this documentation task. Future
`docs/test-vectors/reporting.md` vectors will use the approved vector format
and cover:

- zero-subject report;
- single-subject report;
- directional two-subject report;
- ordered sections and blocks;
- explicit incomplete report;
- invalid and duplicate identifiers;
- invalid technical status;
- non-finite and unsupported values;
- cyclic data;
- deterministic serialization; and
- mutation isolation.

Until reviewed expected models and runtime tests exist, Reporting vectors
remain `pending`; no expected payload is fabricated here.

## Implementation references

Planned runtime package: `backend/app/reporting/`.

Architectural reference implementations inspected for this contract include:

- `backend/app/matchmaking/compatibility_report.py`;
- `backend/app/matchmaking/serialization.py`;
- `backend/app/matchmaking/validation.py`;
- `backend/app/prediction/result.py`;
- `backend/app/prediction/schema.py`; and
- strict Pydantic response models under `backend/app/schemas/`.

These remain unchanged and are not imported as Reporting domain models unless
the runtime task explicitly identifies a safe general helper.

## Change history and supersession

| Version | Change |
| --- | --- |
| `1.0` | Approved the Report Data Model Foundation contract before runtime implementation. |

A future specification may change this contract only through a focused task
that identifies compatibility impact, updates this history, specifies a schema
version decision, and links any superseding document. This specification does
not supersede the Sprint 11 Matchmaking report contract.
