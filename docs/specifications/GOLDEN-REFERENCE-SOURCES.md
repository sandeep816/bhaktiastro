# SPEC-GOLDEN-REFERENCE-SOURCES-001 - Golden Reference Source Framework

| Field | Value |
| --- | --- |
| Status | `approved` |
| Specification version | `1.0` |
| Owning domain | Cross-domain astronomical reference governance |
| Related ADRs | [ADR-001](../architecture/ADR-001-Project-Principles.md), [ADR-002](../architecture/ADR-002-Astrology-Calculation-Standards.md), [ADR-003](../architecture/ADR-003-Validation-Standards.md), [ADR-004](../architecture/ADR-004-Public-API-Contracts.md), [ADR-005](../architecture/ADR-005-Testing-Standards.md) |
| Related specifications | [SPEC-GOLDEN-FIXTURES-001](GOLDEN-FIXTURES.md), [SPEC-API-STABILITY-001](API-STABILITY.md) |
| Related Sprint task | [Sprint 15, Task 15.2](../SPRINT-15.md#task-152---golden-reference-source-framework) |
| Implementation status | Documentation framework complete; reference collection not started |
| Reference-data status | No schema `1.0` source record exists |
| Compatibility status | Documentation-only and additive; fixture schema `1.0`, data, tests, calculations, and APIs unchanged |

## Purpose and scope

A **Golden Reference Source** is a versioned, scope-bounded, provenance-complete
source whose authority, reproducibility, independence, limitations, and review
state have been evaluated under this specification. It supplies or corroborates
candidate expected values, time context, or calculation configuration for a
future Golden Fixture.

A **Golden Fixture** is the repository-owned, deterministic input and expected-
output artifact governed by
[SPEC-GOLDEN-FIXTURES-001](GOLDEN-FIXTURES.md). A Golden Reference is evidence;
a Golden Fixture is a reviewed test artifact built from evidence. Approval of a
reference does not approve any fixture, expected value, tolerance, calculation,
or test. A fixture becomes `golden` only after satisfying the complete fixture
qualification and review contract.

This framework defines accepted source categories, scope-specific trust levels,
provenance, independence, review, disagreement handling, lifecycle, and source-
record versioning. It creates no reference record or astronomical dataset.

## Authority and relationship to fixture governance

- ADR-001 requires this source decision to remain independently reviewable and
  documentation-first.
- ADR-002 requires explicit calculation settings, reference frames, time
  assumptions, and source-verified conventions.
- ADR-003 prohibits guessed metadata, silent coercion, and repair of malformed
  precomputed evidence.
- ADR-004 and API Stability protect exact identifiers, versions, field order,
  vocabularies, and compatibility behavior.
- ADR-005 separates independent accuracy evidence from structural snapshots and
  generated runtime output.
- Accuracy and the Validation Plan require trusted external comparison and keep
  unverified exact-value tests skipped.

`SPEC-GOLDEN-FIXTURES-001` continues to own fixture classification, lifecycle,
schema `bhaktiastro.golden-fixture` version `1.0`, expected values, tolerances,
storage, and activation. This specification owns the qualification of sources
referenced by fixture provenance. It refines, but does not add to or rename, the
fixture schema's closed `source_type` vocabulary.

If a future task finds these contracts inconsistent, it must use the documented
conflict-resolution process and approve an explicit version decision. It must
not silently reinterpret either specification.

## Source versus evidence artifact

A source is the identified publisher, dataset, software release, standard,
table, calculation record, or other origin being assessed. An evidence artifact
is a retained citation, export, screenshot, checksum, worksheet, or note that
demonstrates what the source showed at a particular version and configuration.

An evidence artifact does not become an independent source merely because it is
stored separately. Two websites, applications, or screenshots backed by the
same engine and data lineage are not automatically two sources. BhaktiAstro
output, a copy of that output, or a screenshot of that output is never an
independent Golden Reference.

## Canonical accepted source categories

The canonical category vocabulary is exactly the existing fixture
`source_type` vocabulary:

```text
authoritative_ephemeris
independent_reference_software
published_astronomical_table
trusted_public_standard
independent_manual_calculation
```

Categories describe the source form and ownership. They do not assign trust by
themselves. One source record has exactly one category for one declared scope.
If a publisher offers products in different categories, each product/version
receives a separate source record.

| Category | Acceptance requirements | Trust limits |
| --- | --- | --- |
| `authoritative_ephemeris` | Direct, versioned ephemeris or official astronomical product from its responsible institution; exact product/kernel/edition, time scale, coordinate frame, and access path are recorded. | May qualify as `primary` only for the product's declared scope. Institutional reputation does not extend authority beyond that scope. |
| `independent_reference_software` | Identified software/build, calculation engine and data files, complete settings, output precision, and reproducible input are recorded; its engine/data lineage is known. | At most `secondary`. It is only independent when its material calculation chain is independent from BhaktiAstro and from the other selected source. |
| `published_astronomical_table` | Stable publication/edition with identifiable author or publisher, publication date, method or convention, units, precision, and reproducible table location is recorded. | At most `secondary`. A table copied from an unknown upstream source is `informational`, not qualifying evidence. |
| `trusted_public_standard` | Versioned standard or official database governing timezones, UTC offsets, calendars, units, or another declared non-astronomical context; responsible publisher and effective version/date are recorded. | May be `primary` only for the standard's own context. It cannot establish an astronomical longitude or event by itself. |
| `independent_manual_calculation` | Reproducible worksheet or calculation record identifies author, formula/source, inputs, units, intermediate steps, precision, date, and independent review. | At most `secondary` and never the sole qualifying source. Undocumented mental arithmetic or observation is not accepted. |

Unsupported category strings are invalid. A new category requires an explicit
schema-vocabulary and compatibility decision.

## Evaluation of common candidate labels

Named institutions, products, or publication forms are evaluated as follows;
none is automatically approved by name alone.

| Candidate label | Framework decision |
| --- | --- |
| Official Astronomical Ephemeris | Accepted as `authoritative_ephemeris` only when the record cites the direct responsible publisher and exact product/version, not a repost or derived calculator. |
| JPL or NASA | A direct JPL/NASA ephemeris product may be `authoritative_ephemeris`; the exact DE release/kernel, interface or publication, time scale, frame, and settings are required. A generic NASA/JPL webpage is not automatically a qualifying source. |
| Swiss Ephemeris | Accepted as `independent_reference_software` with exact library/build, ephemeris files, flags, ayanamsa, node mode, frame, and settings. It is not independent verification when BhaktiAstro or the comparison source uses the same Swiss Ephemeris calculation/data chain. |
| Government Observatory | Its direct official ephemeris may be `authoritative_ephemeris`; its timezone or civil-time publication may be `trusted_public_standard`; other material is classified by the actual product, not the institution name. |
| Published Astronomical Tables | Accepted as `published_astronomical_table` when edition, page/table identifier, conventions, precision, and publisher are reproducible. Unattributed or republished tables are not accepted. |
| Independently Verified Software | Accepted as `independent_reference_software` only after engine/data lineage, version, configuration, and independence are demonstrated. Multiple frontends over one engine count as one lineage. |
| Manual Observation | Not an accepted standalone source category in schema `1.0`. Instrumented observations may be retained as `supporting` evidence with method, calibration, conditions, uncertainty, observer, and timestamp, but cannot establish a calculated Golden value alone. |
| Academic Publications | A reproducible value table may be `published_astronomical_table`. An algorithm paper without case values is supporting method evidence. Citation or peer review alone does not make a paper a qualifying numerical reference. |

Commercial astrology applications, public Panchang websites, and printed
Panchangs may be evaluated as `independent_reference_software` or
`published_astronomical_table` when their exact version/edition, settings,
precision, and lineage are available. If those facts are unavailable, they are
`supporting` or `informational` and cannot silently count as independent
qualifying sources.

## Closed trust-level model

Trust is assigned per source version and declared scope, never globally to a
brand or publisher. The closed vocabulary is:

| Trust level | Exact meaning |
| --- | --- |
| `primary` | Direct authoritative producer for the declared data or standard, with complete version/configuration provenance. Eligible to anchor Golden verification within that scope. |
| `secondary` | Reproducible and technically credible independent implementation, publication, or manual calculation suitable to corroborate a Primary or, under an approved exception, another independent Secondary. |
| `supporting` | Useful for configuration, method, context, precision, or discrepancy analysis but insufficient to establish the referenced expected value. |
| `informational` | Useful for discovery only; incomplete provenance, uncertain lineage, or non-reproducible behavior prevents verification use. |

Trust is not transitive. A Secondary derived from a Primary is not independent
of that Primary merely because it presents the value differently. A source can
be Primary for timezone offsets and Supporting for planetary longitude. Such
different scopes require distinct source records or an explicitly bounded
scope that cannot be misread.

Only `primary` and `secondary` records can appear in an expected-value record's
qualifying `source_ids`. `supporting` records may be linked in provenance or
review notes for context. `informational` records cannot support approval.

## Independence model

Independence is evaluated for each expected-output family across:

1. publisher or responsible institution;
2. underlying ephemeris, table, standard, or observational dataset;
3. calculation engine or algorithm implementation;
4. configuration and operator/transcription path; and
5. relationship to the BhaktiAstro implementation under test.

Two records do not count as independent when a material error could be shared
because they use the same engine, copied table, upstream dataset without an
independent calculation, API backend, or transcribed result. Shared upstream
data does not always invalidate corroboration, but the reviewer must record the
shared lineage and cannot claim implementation independence.

BhaktiAstro-generated output may be compared during investigation but never
counts toward the independent-source minimum.

## Minimum verification before Golden qualification

Every expected-output family in a future Golden Fixture must satisfy exactly
one of these routes:

1. **Standard route:** one approved Primary plus one approved, materially
   independent Primary or Secondary;
2. **Primary-unavailable exception:** two approved, materially independent
   Secondary sources plus a reviewer-approved written explanation that no
   suitable Primary is practical for this scope; or
3. **Unique-authority exception:** one approved Primary when it is the unique
   authoritative producer for that scope and the fixture review contains the
   required `single_source_exception` explaining why independent corroboration
   is not practical.

Supporting and Informational sources never satisfy the minimum. Two Secondary
sources sharing a material engine or data lineage count as one. One source used
twice with different settings counts as one source, though both settings may be
useful for investigation.

The named fixture reviewer must verify category, trust, independence, version,
settings, and source-record status before approving the route. A source owner
or evidence collector may prepare the record but may not be its sole approver.
All unresolved differences remain visible. Source approval alone does not
approve a tolerance or the fixture.

## Reference-source schema

Future canonical source records use:

```text
GOLDEN_REFERENCE_SOURCE_SCHEMA_ID = "bhaktiastro.golden-reference-source"
GOLDEN_REFERENCE_SOURCE_SCHEMA_VERSION = "1.0"
```

The exact top-level field order is:

| Position | Field | Contract |
| ---: | --- | --- |
| 1 | `schema_id` | Exact identifier above |
| 2 | `schema_version` | Exact supported version above |
| 3 | `reference_id` | Stable source/version identifier |
| 4 | `source_type` | One canonical accepted source category |
| 5 | `trust_level` | One closed trust level |
| 6 | `lifecycle_status` | One closed source lifecycle status |
| 7 | `source_name` | Exact product, publication, database, or calculation-record name |
| 8 | `publisher_or_owner` | Responsible institution, publisher, or named calculator |
| 9 | `source_version` | Exact release, edition, build, kernel, database, or record revision |
| 10 | `publication_date` | ISO `YYYY-MM-DD` release/publication date |
| 11 | `calculation_engine` | Exact engine/algorithm name or `not_applicable` |
| 12 | `calculation_engine_version` | Exact version or `not_applicable` |
| 13 | `timezone_database_version` | Exact tzdata/database version or `not_applicable` |
| 14 | `url_or_publication_reference` | Stable URL, DOI, ISBN/page, archive, or bibliographic reference |
| 15 | `access_or_reference_date` | ISO `YYYY-MM-DD` date on which the evidence was obtained |
| 16 | `scope` | Non-empty ordered unique subset of the Golden Fixture calculation-scope vocabulary |
| 17 | `calculation_settings` | Ordered, source-native configuration and assumptions |
| 18 | `evidence_references` | Non-empty ordered retained citations or lawful evidence paths |
| 19 | `limitations` | Ordered known precision, lineage, access, historical, and scope limits |
| 20 | `review` | Exact source verification and approval record |
| 21 | `supersedes` | Empty string or exact prior reference ID |

`not_applicable` is permitted only for `calculation_engine`,
`calculation_engine_version`, or `timezone_database_version` when that field
truly cannot affect the declared scope, and the reason is stated in
`limitations`. Unknown required metadata is not replaced with
`not_applicable`; it blocks `verified` and `approved`. Publication, access, and
review dates are ISO dates and are never guessed from the current environment.

`review` has exact order:

```text
reviewer
review_date
comparison_method
comparison_reference_ids
independence_assessment
observed_disagreements
unresolved_issues
decision
notes
```

The decision is `pending`, `approved`, or `rejected`. `proposed`, `collected`,
`verified`, and `in_review` require `pending`; `approved` requires `approved`;
`rejected` requires `rejected`; `superseded` preserves its prior `approved`
decision; and `archived` preserves its last decision with the archive reason in
`notes`. All strings and collections are deterministic and JSON-safe; unknown
fields, wrong order, unsupported vocabulary, duplicate IDs, malformed
references, non-finite numbers, and inconsistent cross-fields are invalid.
Task 15.2 creates no serializer or validator.

## Stable reference identifiers

Reference IDs use:

```text
GRS-<SOURCE_TOKEN>-V<N>
```

The exact pattern is:

```text
^GRS-[A-Z0-9]+(?:_[A-Z0-9]+)*-V[1-9][0-9]*$
```

`SOURCE_TOKEN` identifies the product or publication, not a mutable URL.
`V<N>` is the repository reference-record revision and is separate from the
upstream source version. IDs are repository-global and never reused.

A change to source identity, upstream version, trust, scope, lineage,
calculation meaning, or evidence creates a new reference revision and links
`supersedes`. A prose correction that cannot affect qualification may retain
the ID only when review notes record it. Superseded, archived, and rejected IDs
remain reserved.

## Mapping into Golden Fixture provenance

This framework does not add fields to fixture schema `1.0`. Every future
Golden Fixture records the required source information through the existing
ten-field `provenance` items and separate fixture `review` object:

| Required information | Fixture schema `1.0` location |
| --- | --- |
| Source name | Provenance publication/software/standard/service name |
| Source version | Provenance exact edition/build/database/source version |
| Publication date | Provenance bibliographic citation and linked source record |
| Calculation engine | Provenance calculation settings and assumptions |
| Timezone database version | Provenance calculation settings and assumptions, plus fixture location/time records |
| URL or publication reference | Provenance URL or bibliographic citation |
| Reviewer | Fixture `review.reviewer` |
| Review date | Fixture `review.review_date` |
| Comparison method | Fixture `review.comparison_method` |

The provenance `source_id` resolves to the approved source record's
`reference_id`, or to a fixture-local alias that records that exact reference
ID without ambiguity. The human reference review links the complete source
record. Duplication in fixture provenance is an intentional audit projection,
not a competing source definition.

## Source lifecycle

The closed lifecycle vocabulary is:

| Status | Meaning |
| --- | --- |
| `proposed` | Candidate identity and intended scope are recorded; evidence may be incomplete. |
| `collected` | Required provenance and evidence artifacts are present but authenticity, reproducibility, trust, and independence are not fully reviewed. |
| `verified` | Identity, version, settings, evidence, and reproducibility have been checked; approval for Golden use is still pending. |
| `in_review` | A named reviewer is resolving trust, independence, limitations, or disagreements. |
| `approved` | Scope, category, trust, provenance, independence assessment, and review satisfy this framework; eligible for future fixture qualification. |
| `superseded` | A named later reference revision replaces this version; existing historical fixtures may retain it, but new fixtures use the replacement. |
| `archived` | Retained for audit but unavailable, withdrawn, obsolete without an approved replacement, or unsuitable for new fixtures. |
| `rejected` | Failed provenance, reproducibility, independence, or trust review; rejection reason is retained. |

Normal progression is `proposed` to `collected` to `verified` to `in_review` to
`approved`. Review may return the record to an earlier state or reject it.
Only `approved` sources may qualify a new Golden Fixture. `superseded` sources
remain valid historical evidence only for fixtures that already cite them.

Source lifecycle is independent from Golden Fixture lifecycle, canonical test-
vector verification status, and automated-test status. Source `approved` does
not imply fixture `golden` or `active`, vector `verified`, or a passing test.

## Provenance and review requirements

For every source, the collector records the exact schema fields above and:

- preserves the source's original units, precision, labels, and values before
  any normalized comparison;
- records all settings affecting time, frame, coordinates, ayanamsa, node mode,
  refraction, house system, or calculation scope;
- identifies upstream engine and dataset lineage where known;
- records access restrictions, rolling-data behavior, historical limitations,
  and evidence-retention constraints;
- uses a stable citation and lawful evidence reference rather than relying on
  a transient screenshot alone; and
- records why the assigned category and trust level are valid for the declared
  scope.

The reviewer independently checks source identity, version, configuration,
reproducibility, scope, trust level, independence, and linked evidence. Blank,
`TBD`, guessed, or internally inconsistent required metadata prevents approval.
Publication, access, and review dates describe different events and are not
substituted for one another.

## Conflict and disagreement resolution

When trusted sources disagree:

1. keep every original observation and place affected records or fixture work
   in `in_review`;
2. verify that date/time, UTC conversion, timezone/tzdata, coordinates,
   calendar, time scale, reference frame, ephemeris, ayanamsa, node mode,
   refraction, precision, and output definition are equivalent;
3. identify shared engines, datasets, copied values, and operator or
   transcription errors;
4. compare each value only under the future fixture's separately approved
   comparison policy; this framework supplies no tolerance value;
5. have a named reviewer record the evidence, differences, scope decision, and
   resolution; and
6. approve only when every material disagreement is explained or removed from
   the proposed fixture scope.

Trust level is evidence for review, not an automatic winner. Do not average
sources, majority-vote correlated sources, choose the value closest to current
BhaktiAstro output, widen a tolerance, or overwrite inconvenient evidence.

If the disagreement reveals different valid conventions, the fixture must
declare one already approved convention and exclude the other from that scope.
If a convention is not approved, escalate to the owning domain specification
or ADR before fixture work continues. If disagreement remains unresolved, no
Golden Fixture is approved; the candidate stays provisional, narrows scope, or
is rejected.

## Source replacement and monitoring

A source is re-reviewed when its publisher, upstream dataset, engine, release,
URL behavior, access method, timezone database, calculation defaults, precision,
or correction notice changes. New upstream versions do not silently update an
approved record.

Use `superseded` when an approved replacement record exists and names the old
record. Use `archived` when the record is retained but has no approved
replacement or is no longer eligible for new work. Existing fixtures are not
rewritten silently; any effect on expected values, settings, or provenance
requires fixture review and, where required, a new fixture revision.

## Schema and compatibility policy

Schema ID, schema version, exact fields/order, category, trust and lifecycle
vocabularies, identifier syntax, and validation meaning follow
[SPEC-API-STABILITY-001](API-STABILITY.md).

- Schema `1.0` is strict and accepts no unknown field or implicit default.
- Renaming, removing, reordering, or retyping a field, changing identifier
  meaning, or changing a closed vocabulary is breaking.
- A minor schema version is allowed only when a future reader explicitly
  supports an additive extension while preserving all old behavior. Strict
  `1.0` readers do not accept undeclared additions automatically.
- An incompatible change requires a new major schema version, coexistence and
  migration plan, updated specifications, and focused future tests.
- Unsupported schema IDs and versions are rejected without upgrade, downgrade,
  nearest-version fallback, or silent migration.
- Source-record revision `V<N>` and source-schema version are independent.

Version 1.0 is documentation-only. It changes no fixture schema, fixture data,
runtime schema, serializer, API, vocabulary, test, or calculation.

## Future documentation and validation expectations

A separately authorized source-collection task must validate:

- exact schema ID/version, field order, nested review order, and JSON safety;
- unique well-formed reference IDs and valid supersession links;
- every accepted category, trust level, and lifecycle status;
- source version, publication/access/review dates, engine, tzdata, citation,
  configuration, evidence, and limitations;
- scope-specific category and trust eligibility;
- independence from BhaktiAstro and between selected sources;
- same-engine, shared-data, copied-table, and shared-backend rejection cases;
- the standard, Primary-unavailable, and unique-authority verification routes;
- source conflict, unresolved disagreement, archive, supersession, and
  rejection behavior; and
- deterministic records with no guessed, non-finite, aliased, or unsupported
  values.

This list defines future documentation/data validation expectations only. Task
15.2 adds no runtime validation or test.

## Explicit exclusions

Task 15.2 includes no:

- source record, fixture, expected value, tolerance value, astronomical table,
  ephemeris file, dataset, screenshot, or external evidence;
- Mumbai, London, New York, Kundali, Jodhpur, or Delhi fixture work;
- runtime module, validator, serializer, public export, API, dependency, or
  network integration;
- test creation/change, pytest helper, skip activation, or validation-status
  promotion;
- calculation, normalization, timezone conversion, DST, ephemeris, Panchang,
  or Kundali behavior change;
- source scraping, paid-service integration, account creation, download, or
  redistribution of restricted material;
- approved numeric, angular, time, event-boundary, or rounding tolerance; or
- Sprint 16 work.

## Validation checklist

Task 15.2 approval requires:

- consistency with ADR-001 through ADR-005;
- consistency with Golden Fixture schema `1.0`, API Stability, Accuracy, the
  Validation Plan, and canonical test-vector governance;
- explicit evaluation of each requested source category without brand-based
  approval;
- exact trust, independence, provenance, conflict, lifecycle, and versioning
  rules;
- cross-document link and anchor validation;
- Markdown-only scope and no runtime, test, fixture, skip, or ROADMAP change;
- `git diff --check` and focused staged-diff review; and
- clean working tree after one focused documentation commit.

## Change history and supersession

| Version | Change |
| --- | --- |
| `1.0` | Approved the Golden Reference Source Framework, accepted categories, trust and independence model, provenance, review, disagreement, lifecycle, and schema contracts without collecting source or fixture data. |

A future revision must identify compatibility impact, update this history, and
name any superseded specification or schema. No source is approved merely by
appearing as an example in this specification.
