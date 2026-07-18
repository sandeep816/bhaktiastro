# Sprint 15 - Golden Fixture Expansion

Status: In progress - Tasks 15.1 through 15.4 documentation complete; one
proposed Mumbai evidence plan exists; sources, expected values, fixture data,
and tests not started

Primary permanent contracts:

- [SPEC-GOLDEN-FIXTURES-001](specifications/GOLDEN-FIXTURES.md)
- [SPEC-GOLDEN-REFERENCE-SOURCES-001](specifications/GOLDEN-REFERENCE-SOURCES.md)

## Sprint purpose

Sprint 15 expands independently verified reference coverage without treating
generated snapshots as astronomical truth. Its first task defines what a
golden fixture is, how provenance and tolerances are reviewed, how timezone and
DST cases are represented, and how future fixture data relates to canonical
test vectors and pytest artifacts.

Task 15.1 creates no fixture value, test, validator, runtime behavior, or
calculation change.

Task 15.2 defines the canonical source categories, trust and independence
model, provenance, review, conflict, lifecycle, and source-record schema that
all future Golden Fixture work must use. It collects no source or fixture data.

Task 15.3 authorizes the exact contract for selecting one future Mumbai case
and preparing its provisional human evidence record. It selects no date,
coordinates, calculation values, source values, or tolerances and creates no
record or fixture.

A separately authorized Task 15.3 execution created the `proposed` and
`pending` [Mumbai TIME_JD evidence plan](test-vectors/golden-fixtures/GF-MUMBAI-20240701-TIME_JD-V1.md)
without sources, expected values, tolerances, machine data, or tests.

Task 15.4 authorizes selection and lineage review of real reference-source
products for that record. It remains separate from source approval,
expected-value acquisition, comparison, tolerance, fixture, and test work.

## Source-of-truth and sequencing decision

[ROADMAP.md](ROADMAP.md) defines the exact milestone title **Sprint 15 - Golden
Fixture Expansion** after Sprint 14. The repository contained no `SPRINT-15.md`,
Task 15 number, or competing task sequence before this task.

[Sprint 14](SPRINT-14.md) is complete with its sole approved Task 14.1. Runtime
public-contract inventory and contract-test enforcement remain separately
authorized future work under
[SPEC-API-STABILITY-001](specifications/API-STABILITY.md); they were never a
Sprint 14 completion criterion and are not silently opened here.

The legacy `PROJECT_PHASES.md` phase backlog is historical and does not rename
Sprint 15. Its claim that a Jodhpur golden fixture is verified conflicts with
current Accuracy, Validation Plan, fixture tests, and ADR-005 evidence; the
current files remain structural and pending.

## Dependencies

- Completed Sprints 1 through 3 provide Astronomy, Panchang, API, existing
  structural fixtures, and validation documentation.
- Completed Sprint 4 provides the base Kundali output whose future fixture
  structure may be covered.
- The Documentation Architecture Foundation owns source hierarchy and
  canonical test-vector governance.
- ADR-002 owns explicit astronomical conventions and deterministic boundaries.
- ADR-003 owns strict validation and no silent coercion or repair.
- ADR-004 and API Stability own schema and compatibility evolution.
- ADR-005, [Accuracy](ACCURACY.md), and the
  [Validation Plan](VALIDATION_PLAN.md) prohibit invented values and keep
  unverified accuracy tests skipped.

## Roadmap milestone scope

The exact milestone-level areas remain:

- Mumbai fixture;
- London DST fixture;
- New York DST fixture;
- Kundali fixture structure; and
- manual reference documentation.

Task 15.1 governs these areas but implements none of them.

## Approved task sequence

Tasks 15.1 through 15.4 are the only approved tasks, and all are documentation-
only and complete. No expected-value collection, fixture, runtime,
test-activation, or Task 15.5 work is authorized by this document. Task 15.4
source-selection execution requires separate explicit authorization under the
boundary below.

## Task 15.1 - Golden Fixture Governance and Reference Specification

Status: Complete - documentation only

### Documentation outcome

Task 15.1 approves
[SPEC-GOLDEN-FIXTURES-001](specifications/GOLDEN-FIXTURES.md) version `1.0` as
the permanent source of truth for:

- four closed fixture classifications: `structural`, `regression`,
  `provisional_reference`, and `golden`;
- a strict source/review/activation lifecycle;
- schema `bhaktiastro.golden-fixture` version `1.0` and stable versioned fixture
  identifiers;
- complete location, timezone, time, calendar, configuration, expected-value,
  tolerance, provenance, and review records;
- exact DST treatment for valid, ambiguous, and nonexistent local times;
- per-fixture calculation scope rather than requiring every output;
- future Mumbai, London, New York, and Kundali selection/structure rules without
  dates or values;
- separate human-vector, machine-fixture, pytest, and evidence storage roles;
- strict failure handling and prohibition on regenerating expected data from
  current runtime; and
- future schema, provenance, timezone, tolerance, immutability, and calculation
  regression tests.

### Existing evidence classification

The existing Jodhpur and Delhi Panchang JSON files remain pre-schema
`structural` fixtures with verification status `pending`. They were generated
from current API output, have no independent source/version and comparison
record, lack approved per-field tolerances and reviewer/date evidence, and are
not promoted by this task.

The repository has thirteen accuracy-related skips: one exact structural-
fixture equality test and twelve manual-reference placeholders. They remain
skipped until separately authorized fixture work satisfies the permanent
specification and updates the Validation Plan.

### Completion criteria

Task 15.1 is complete when:

1. Sprint 14 is safely closed without inventing Task 14.2;
2. permanent Golden Fixture governance and Sprint 15 execution ownership are
   approved and indexed;
3. Jodhpur, Delhi, and all manual-reference skips are classified accurately;
4. no expected value, fixture, test, skip state, runtime, public API, or
   calculation changes;
5. cross-document links, anchors, Markdown scope, and diff checks pass; and
6. one focused documentation commit leaves a clean working tree.

## Task 15.2 - Golden Reference Source Framework

Status: Complete - documentation only

### Documentation outcome

Task 15.2 approves
[SPEC-GOLDEN-REFERENCE-SOURCES-001](specifications/GOLDEN-REFERENCE-SOURCES.md)
version `1.0` as the permanent source of truth for:

- the distinction between repository-owned Golden Fixtures and the external or
  independently prepared Golden References that support them;
- the existing five closed fixture provenance source types, with exact
  acceptance requirements and evaluation of official ephemerides, JPL/NASA,
  Swiss Ephemeris, government observatories, published tables, independent
  software, manual observations, and academic publications;
- four scope-specific trust levels: `primary`, `secondary`, `supporting`, and
  `informational`;
- material independence across publisher, data lineage, engine, operator, and
  the BhaktiAstro implementation under test;
- standard and narrowly reviewed exception routes for minimum independent
  verification;
- complete source provenance, review, disagreement, supersession, and archive
  rules; and
- schema `bhaktiastro.golden-reference-source` version `1.0` without changing
  Golden Fixture schema `1.0`.

### Completion criteria

Task 15.2 is complete when:

1. source categories and trust levels are closed, scope-specific, and not
   assigned automatically by brand;
2. source provenance maps into the existing fixture provenance and review
   fields without changing that schema;
3. independent verification and unresolved-source conflict behavior are exact;
4. no source record, evidence, fixture, expected value, tolerance, test, skip
   state, runtime, public API, or calculation changes;
5. cross-document links, anchors, Markdown scope, and diff checks pass; and
6. one focused documentation commit leaves a clean working tree.

## Task 15.3 - Mumbai Reference Case Selection and Provisional Evidence Record

Status: Complete - documentation authorization only

### Purpose and lifecycle boundary

Task 15.3 defines and authorizes the selection contract for one exact Mumbai
reference case that a later, separately authorized execution task may populate,
independently verify, review, and promote through the Golden Fixture lifecycle.
This task is case-selection and evidence-planning documentation only. It does
not select final inputs where approved authoritative evidence is absent and
does not create the evidence record.

The future human record must use fixture lifecycle `proposed` and human-vector
verification status `pending`. It records `provisional_reference` only as the
intended later fixture classification; that classification cannot be claimed
until the record contains externally sourced candidate values as required by
the canonical contract. These are separate vocabularies. Provisional does not
mean verified, selected does not mean approved, and proposed source candidates
do not establish Golden status. No regression or accuracy test may depend on
the future record while it remains in these states.

### Required case identity

The future record must select and record one internally consistent case with:

- provisional fixture ID `GF-MUMBAI-<YYYYMMDD>-<SCOPE>-V1`, where the local
  civil date and scope token satisfy the canonical identifier contract;
- lifecycle `proposed`, vector verification status `pending`, and intended
  later classification `provisional_reference`, subject to its canonical
  externally sourced candidate-value prerequisite;
- location name, country and recorded country-code standard, finite latitude
  and longitude, coordinate source, coordinate datum when available, and an
  explicit elevation value or justified null decision;
- one local civil date and either one exact local time or an explicitly bounded
  all-day/event scope;
- IANA timezone `Asia/Kolkata`, the UTC offset at the selected instant, the
  timezone-database version used to verify it, and consistent local and UTC
  representations when the case identifies an instant; and
- explicit calendar and time scale.

The canonical Mumbai contract requires the selected modern instant's `+05:30`
offset to be verified from the recorded timezone source. This requirement is
not evidence by itself. Task 15.3 assigns no date, time, coordinates, datum,
elevation, tzdata version, or final fixture ID.

### Narrow scope selection

The later record must choose only the minimum approved Golden Fixture scope
tokens needed for its evidence. It must separately list included outputs,
excluded outputs, the reason each output family is included, and the reason
each excluded family is deferred.

Candidate outputs are Julian Day, ayanamsa, Sun longitude, Moon longitude,
Tithi, Nakshatra, Yoga, Karana, Vara, sunrise, sunset, moonrise, and moonset.
They map into the canonical scopes `julian_day`, `ayanamsa`,
`planetary_positions`, `panchang_elements`, `panchang_boundaries`, and
`rise_set` as applicable. Listing an output here does not include or approve it.
No candidate may be included unless its exact inputs, configuration, sources,
precision, comparison method, and future tolerance-review path can be stated.

### Calculation-configuration plan

Before any expected value is collected, the future record must document:

- ayanamsha system and exact spelling;
- ephemeris engine and version, plus ephemeris files or fallback mode;
- calculation flags, tropical or sidereal frame, geocentric or topocentric
  mode, and coordinate assumptions;
- rise/set model, refraction policy, solar-disc policy, and elevation policy;
- rounding and retained source-precision policy; and
- language/localization policy for source labels and canonical machine values.

These details project into the existing fixture `calculation_config`, source
settings, limitations, and technical notes. They do not add fields to either
canonical schema. Unknown settings remain explicit blockers and are never
inferred from current BhaktiAstro defaults.

### Reference-source plan

The future record must identify at least one proposed `primary` source candidate
and one materially independent `secondary` source candidate for every included
output family. For each candidate it must record:

- proposed canonical source category and scope-specific trust level;
- exact source name, publisher, version, publication or access date, citation,
  calculation engine/data lineage, and relevant settings;
- compatibility of its time, location, frame, ayanamsha, rise/set, precision,
  and output definitions with the selected case; and
- a written lineage assessment covering publisher, underlying dataset,
  calculation engine, operator/transcription path, independence from the other
  candidate, and independence from BhaktiAstro.

Popularity, public accessibility, or a recognizable brand does not approve a
source. Candidate labels remain proposed until separate source records satisfy
`SPEC-GOLDEN-REFERENCE-SOURCES-001`; shared Swiss Ephemeris or other material
lineage cannot be presented as independent corroboration.

### Future provisional evidence record

A later execution task may create:

```text
docs/test-vectors/golden-fixtures/GF-MUMBAI-<YYYYMMDD>-<SCOPE>-V1.md
```

That record must contain case identity, lifecycle and verification states,
calculation configuration, source candidates, source-lineage analysis,
included and excluded outputs with reasons, unresolved questions, reviewer
status, and promotion blockers. It remains a human evidence-planning artifact,
not a machine fixture or enabled-test input. The later task may also update
`docs/test-vectors/INDEX.md`; Task 15.3 creates or changes neither file.

### Promotion gates

No later task may create a machine Golden Fixture until all of these gates are
met and recorded:

1. exact case inputs and stable provisional fixture ID are reviewed and
   approved;
2. complete canonical source records exist for every qualifying source;
3. material independence from BhaktiAstro and between qualifying sources is
   confirmed per output family;
4. candidate expected values are obtained independently rather than copied from
   current runtime output;
5. original observations and all differences are retained and reviewed;
6. comparison modes and tolerances are justified separately for every output;
7. a named reviewer is assigned and the review date is recorded;
8. every unresolved blocker or out-of-policy discrepancy is closed or the
   affected output is removed from scope; and
9. fixture classification, lifecycle, and vector verification status advance
   only through their respective canonical promotion rules.

Passing these planning gates does not itself activate a test. Fixture schema
validation, linked machine data, focused tests, regressions, and `active`
status belong to separately authorized later work.

### Explicit non-goals and file boundary

Task 15.3 includes no runtime implementation, fixture loader or validator,
schema code, machine JSON, expected astronomical value, current-runtime
snapshot, expected-value assertion, tolerance selection or implementation,
source collection, online Panchang transcription, or skipped-test activation.
It does not modify Jodhpur or Delhi fixtures, Accuracy or Validation Plan
status, calculations, APIs, tests, public exports, canonical specifications,
the ROADMAP, or Sprint 16 planning.

The only Task 15.3 file updates are `docs/SPRINT-15.md`, `docs/MASTER.md`, and
`CHANGELOG.md`.

### Completion criteria

Task 15.3 documentation is complete when:

1. this task contract is formally approved with an explicit pre-runtime,
   pre-source, pre-fixture, and pre-Golden boundary;
2. the exact future evidence-record location and required contents are defined;
3. case identity, narrow scope, configuration, source-candidate independence,
   and promotion gates are complete without invented values;
4. `MASTER.md` identifies Task 15.3 as the latest approved Sprint 15 task and
   keeps Sprint 15 in progress;
5. the changelog records authorization without claiming source or fixture
   completion;
6. Markdown links and anchors, changed-file scope, and `git diff --check` pass;
   and
7. one focused documentation commit leaves a clean working tree.

## Task 15.4 - Mumbai Independent Reference Source Selection

Status: Complete - documentation authorization only

### Purpose and scope

Task 15.4 defines and authorizes the source-selection contract for the
[Mumbai TIME_JD evidence plan](test-vectors/golden-fixtures/GF-MUMBAI-20240701-TIME_JD-V1.md).
It selects qualifying products for civil-time/timezone and UTC-conversion
evidence and for Julian Day methodology or independently generated reference
output. Source selection identifies reproducible products and their lineage;
it does not acquire an expected value, approve a source, compare output, or
promote the fixture.

Every source selection must satisfy
[SPEC-GOLDEN-REFERENCE-SOURCES-001](specifications/GOLDEN-REFERENCE-SOURCES.md).
Task 15.4 does not change either canonical Golden specification.

### Required source set and canonical routes

The standard selection route requires:

1. one `trusted_public_standard` source intended as `primary` for IANA
   timezone, civil-time, offset, DST, fold, and UTC-conversion evidence;
2. one materially independent corroborating `primary` or `secondary` source
   for that civil-time evidence when canonical policy requires corroboration;
3. one scope-qualified source intended as `primary` for Julian Day methodology
   or reference output, normally `authoritative_ephemeris`; and
4. one materially independent Julian Day corroborating source intended as
   `primary` or `secondary`, using `published_astronomical_table`,
   `independent_manual_calculation`, or `independent_reference_software` only
   when its scope, reproducibility, precision, and lineage qualify.

The canonical Primary-unavailable route may instead use two materially
independent Secondary sources with a reviewer-approved explanation. The
unique-authority route may use one Primary only with the required reviewed
single-source exception. Neither exception is presumed or approved by Task
15.4. `supporting` and `informational` sources never satisfy the qualifying
minimum.

### Independence requirements

For each output family, the future execution must assess independence across:

- publisher or maintainer;
- underlying timezone database, ephemeris, table, or other dataset;
- calculation engine or formula implementation;
- configuration, operator, transcription, and interface path; and
- relationship to BhaktiAstro, its Python datetime/numeric-offset path,
  `pyswisseph`/Swiss Ephemeris use, repository calculation utilities, and
  existing structural snapshots.

Two web interfaces over the same engine or upstream service count as one
lineage. A Swiss-Ephemeris-derived source is not independent verification of a
BhaktiAstro value derived through the same material Swiss Ephemeris lineage
unless the shared lineage is disclosed and the canonical exception process is
fully satisfied. BhaktiAstro output and the Jodhpur or Delhi snapshots cannot
qualify as source evidence.

### Source-selection record requirements

Each selected product must receive a provisional identifier matching
`GRS-<SOURCE_TOKEN>-V1`, where the token identifies the real product or
publication rather than a planning slot or mutable URL. The Mumbai record must
capture, for every selection:

- source name and publisher or maintainer;
- canonical source category and intended scope-specific trust level;
- exact product, edition, build, database, or engine version;
- publication date when the source publishes one, actual access date, and a
  stable URL or bibliographic citation;
- inspectable methodology, calculation engine or formula, configuration
  options, supported precision, and available outputs;
- upstream data and engine lineage, relationship to BhaktiAstro, and a written
  independence assessment;
- compatibility with the selected case's time, calendar, scale, precision, and
  output meaning;
- known limitations and reproducibility constraints;
- source lifecycle/approval state; and
- reviewer assignment and review state.

Unknown mandatory metadata remains an explicit blocker. It is not replaced by
guessed values, brand reputation, popularity, or public availability.

### Timezone and UTC-conversion evidence

The selected source set must be capable of establishing, for local civil
instant `2024-07-01 12:00:00`:

- IANA identifier `Asia/Kolkata` and the responsible timezone-data product;
- exact tzdata or equivalent ruleset version;
- UTC offset, DST status, fold/ambiguity status, and applicable modern rule;
- consistent conversion from that local instant to UTC; and
- evidence that the selected modern instant is a non-seasonal-DST baseline,
  without generalizing the result to historical dates.

Task 15.4 authorization records neither the final offset nor converted UTC
instant. Those values require separately authorized acquisition from the
selected, versioned sources.

### Julian Day source requirements

Every proposed Julian Day source must explicitly document:

- Gregorian calendar interpretation and reform/proleptic assumptions where
  applicable;
- input time scale and the distinction among local civil time, UTC, UT/UT1,
  TT, and any other scale exposed by the product;
- Julian Date epoch and start-of-day convention, including the noon boundary
  rather than silently assuming a midnight boundary;
- leap-second, DUT1, delta-T, or equivalent handling where relevant;
- numeric precision, source-native rounding, and display rounding;
- conversion formula, table provenance, or engine methodology;
- exact product, engine, table, kernel, or publication version; and
- reproducible inputs, settings, and output extraction.

A label such as “Julian Day” without these semantics is insufficient for
selection.

### Acceptance and rejection criteria

A source may be selected only when its canonical category and intended trust
level are valid for the declared scope; its citation is stable; its methodology
and relevant configuration are inspectable; its version, precision, outputs,
and limitations can be recorded; its lineage is documented; its independence
is acceptable or explicitly routed through a canonical exception; its result
is reproducible; and reviewer status is recorded.

Reject or defer a candidate that:

- exposes no inspectable methodology or hides engine, version, data, or
  configuration;
- supplies only localized Panchang display values without reproducible source
  semantics;
- cannot distinguish local time, UTC, UT/UT1, TT, or its Julian day boundary;
- has unexamined shared lineage with BhaktiAstro or another candidate;
- rounds below the precision required for later comparison;
- cannot be reproduced from recorded inputs and settings; or
- is preferred because its output is closest to BhaktiAstro.

Disagreement is retained for later review; it is never resolved by averaging,
majority vote, convenient source selection, or tolerance widening.

### Future execution boundary

A separately authorized Task 15.4 execution may update only:

- `docs/test-vectors/golden-fixtures/GF-MUMBAI-20240701-TIME_JD-V1.md`; and
- `docs/test-vectors/INDEX.md` when source-status metadata is indexed.

That execution may name real products, assign canonical provisional `GRS-...-V1`
identifiers, document methodology, lineage, compatibility, limitations, and
review state, and resolve source-selection blockers. It may not collect or add
expected Julian Day values, insert final UTC-conversion values without separate
authorization, assign tolerances, mark a source approved without canonical
review, create runtime code or machine fixture data, or alter skipped tests.

### Promotion boundary and explicit exclusions

Completing source selection does not permit classification as `golden`, fixture
approval, vector verification, or regression use. Later separately authorized
tasks remain required for reference-value acquisition, source comparison and
discrepancy review, tolerance justification, named reviewer approval,
lifecycle promotion, machine fixture creation, and regression activation.

Task 15.4 includes no runtime, test, schema, loader, validator, comparison
helper, machine JSON, expected astronomical value, calculated BhaktiAstro
value, final offset or UTC instant, numeric tolerance, fixture promotion,
source approval, skipped-test change, Jodhpur/Delhi change, ROADMAP change, or
Sprint 16 work. The only authorization-task file updates are
`docs/SPRINT-15.md`, `docs/MASTER.md`, and `CHANGELOG.md`.

### Completion criteria

Task 15.4 authorization is complete when:

1. purpose, required source set, canonical verification routes, source-record
   fields, and time/Julian methodology requirements are explicit;
2. independence, acceptance, rejection, and conflict rules are documented;
3. future source-selection execution files and exclusions are exact;
4. `MASTER.md` identifies Task 15.4 as the next and latest approved Sprint 15
   task while keeping Sprint 15 in progress;
5. the changelog records authorization without claiming source selection or
   value acquisition;
6. no runtime, test, fixture JSON, source record, expected value, tolerance, or
   lifecycle change exists;
7. Markdown links and anchors, changed-file scope, and `git diff --check` pass;
   and
8. one focused documentation commit leaves a clean working tree.

## Proposed future sequence - not approved

The following unnumbered order mirrors the ROADMAP and is planning context
only. Tasks 15.3 and 15.4 define the first area's case and source-selection
contracts but do not authorize expected-value collection, machine-fixture, or
test work. Task 15.4 source-selection execution and every later execution area
require separate authorization before work begins:

1. source and review a Mumbai non-DST reference fixture;
2. source and review London standard, daylight, and transition cases;
3. source and review New York standard, daylight, and transition cases;
4. approve and populate a base Kundali fixture under the defined structure;
5. complete manual comparison records and activate only qualifying golden
   fixtures.

This list assigns no task numbers, dates, expected values, tolerances, or
implementation authority.

## Explicit exclusions

Tasks 15.1 through 15.4 do not create or change:

- fixture data, canonical expected values, external evidence, or screenshots;
- source records, source approvals, reference datasets, or tolerance values;
- runtime code, tests, skipped tests, pytest helpers, or public exports;
- astronomical, Panchang, timezone, DST, Kundali, or API behavior;
- approved numerical tolerances;
- interpretation rules, Reporting adapters, rendering, or user interfaces; or
- Sprint 16 work.

## Stop point

Task 15.4 stops after the documentation commit. No source-selection execution,
expected-value collection, machine fixture, test activation, or later Sprint
15 task is approved. Mumbai source selection remains separately gated by the
future execution boundary above.
