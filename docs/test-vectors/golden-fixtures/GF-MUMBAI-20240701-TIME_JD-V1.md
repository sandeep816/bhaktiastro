# GF-MUMBAI-20240701-TIME_JD-V1 - Mumbai Time and Julian Day Evidence Plan

## Record identity

| Field | Value |
| --- | --- |
| Provisional fixture ID | `GF-MUMBAI-20240701-TIME_JD-V1` |
| Record title | Mumbai Time and Julian Day Evidence Plan |
| Owning task | [Sprint 15, Task 15.3](../../SPRINT-15.md#task-153---mumbai-reference-case-selection-and-provisional-evidence-record) |
| Fixture schema relationship | Human planning record aligned with `bhaktiastro.golden-fixture` version `1.0`; not a machine-schema instance |
| Source schema relationship | Candidate-source plan aligned with `bhaktiastro.golden-reference-source` version `1.0`; no source record exists |
| Artifact type | Provisional case-selection and evidence-planning record |
| Current fixture classification | Not assigned; `provisional_reference` is only the intended later classification after externally sourced candidate values exist |
| Fixture lifecycle | `proposed` |
| Vector verification | `pending` |
| Machine fixture path | None; creation is blocked |
| Linked automated test | None; regression use is prohibited |
| Record creation date | Not recorded because the current canonical vector format defines no record-creation field; Git history is the audit record |
| Last updated | Not recorded for the same reason; reviewed revisions must remain visible in Git history |

The identifier reserves this exact local date and candidate scope. If the date,
time interpretation, or scope changes, later work must allocate a new fixture
revision or identifier according to
[Golden Fixture governance](../../specifications/GOLDEN-FIXTURES.md#stable-fixture-identifiers).

## Purpose and authority boundary

This record selects and bounds one future Mumbai reference case. It is a plan
for independently sourcing and reviewing a narrow time-context and Julian Day
case; it is not the evidence that performs that review.

This record:

- contains no approved or candidate expected astronomical values;
- is not a regression fixture and cannot be consumed by runtime tests;
- is not evidence of BhaktiAstro accuracy;
- does not qualify as fixture classification `provisional_reference` until
  externally sourced candidate values are present; and
- cannot advance beyond `proposed` or `pending` through documentation alone.

The controlling contracts are
[SPEC-GOLDEN-FIXTURES-001](../../specifications/GOLDEN-FIXTURES.md) and
[SPEC-GOLDEN-REFERENCE-SOURCES-001](../../specifications/GOLDEN-REFERENCE-SOURCES.md).

## Selected case

`Unresolved` below is a blocking state, not a value placeholder.

| Field | Selection or status |
| --- | --- |
| Location label | Mumbai, India |
| Country code | Unresolved: the exact code and standard must be confirmed from an accepted `trusted_public_standard` source before machine-fixture qualification |
| Local civil date | `2024-07-01` |
| Local wall time | `12:00:00` |
| Case type | Proposed `valid_instant`; validity remains blocked on timezone-source verification |
| IANA timezone | Intended `Asia/Kolkata`, as required by the approved Mumbai fixture contract |
| UTC offset | Unresolved: the canonical contract anticipates the modern Mumbai offset, but an exact value may be recorded only from a versioned `trusted_public_standard` source |
| UTC instant | Unresolved because the UTC offset and tzdata version are not yet independently established |
| DST status | Unresolved: this is intended as a non-seasonal-DST baseline, but the selected instant requires versioned timezone evidence |
| Fold | Unresolved until the selected local instant is validated against the recorded timezone source |
| Calendar | Selected Gregorian civil calendar for this modern civil-date case |
| Time scale | Proposed UTC conversion followed by Julian Day UT comparison; the reference source must document its exact UTC/UT treatment |
| Latitude | Unresolved: no approved repository evidence establishes a Mumbai reference coordinate and precision |
| Longitude | Unresolved for the same reason |
| Coordinate datum | Unresolved: must be supplied with the coordinate source |
| Coordinate source | Unresolved: requires an accepted public standard, government geospatial source, or equivalently reviewable publication |
| Elevation decision | Selected as null for the candidate `timezone_validation` and `julian_day` scopes because neither uses elevation; scope expansion requires a sourced elevation decision |

## Case-selection rationale

Mumbai supplies the western-coast Indian location required by the Sprint 15
roadmap and is geographically distinct from the existing Jodhpur and Delhi
structural snapshots. The date `2024-07-01` is a modern, neutral civil date
chosen independently of any BhaktiAstro output, festival, Panchang identity, or
expected astronomical result. Local noon avoids midnight and civil-date edge
conditions while retaining one exact instant.

The case is intended to become a modern non-seasonal-DST baseline only after a
versioned timezone authority confirms the offset and DST state for this exact
instant. Nothing here asserts that modern Mumbai timezone behavior applies to
historical dates.

The candidate validates only local-time context and Julian Day conversion. It
does not validate Mumbai coordinates, rise/set behavior, planetary positions,
Panchang identities, boundary times, or a complete Panchang response. It is
independent of the Jodhpur and Delhi structural snapshots because it uses a new
case identity and date, copies none of their values, and creates no structural
or runtime-output snapshot.

## Proposed validation scope

The filename summary token `TIME_JD` represents the ordered candidate Golden
Fixture scopes `timezone_validation` and `julian_day` only.

### Candidate included outputs

| Scope | Candidate output | Reason for inclusion | Required evidence | Required configuration alignment | Expected value now |
| --- | --- | --- | --- | --- | --- |
| `timezone_validation` | IANA zone identity, offset at the selected instant, DST/fold status, and local/UTC consistency | Establish the time input before any calculation is compared | Versioned timezone authority plus an independent reproducible check | Same local instant, IANA zone, tzdata version, calendar, offset semantics, and fold handling | Absent |
| `julian_day` | UTC instant used by the calculation and Julian Day UT | Exercise the smallest deterministic astronomy boundary without planetary or location-dependent output | Qualifying authoritative Julian Day reference plus materially independent corroboration | Same UTC instant, Gregorian calendar, time-scale definition, day-start convention, and retained precision | Absent |

### Explicitly excluded outputs

The following are outside this record and cannot be inferred from a later
time/Julian agreement:

- complete Panchang request or response structures;
- Vara or other civil/astrological labels;
- Kundali, Lagna, house, Varga, Dasha, matchmaking, reporting, interpretation,
  or prediction output; and
- any runtime schema, serialization, or API compatibility assertion.

### Deferred outputs

| Deferred output | Reason for deferral |
| --- | --- |
| Ayanamsha | Requires a selected convention, engine/version, source lineage, and independent values |
| Sun and Moon longitudes | Require ephemeris, frame, flags, source precision, and independent non-BhaktiAstro evidence |
| Tithi, Nakshatra, Yoga, and Karana | Depend on independently verified longitudes, conventions, category boundaries, and event definitions |
| Vara | Its intended civil-day or sunrise-based definition must be selected and sourced before inclusion |
| Sunrise and sunset | Require approved coordinates, elevation policy, rise/set model, refraction and disc policies, and independent event values |
| Moonrise and moonset | Require the same location/model evidence plus lunar no-event and date-assignment conventions |
| Panchang boundary times | Require independently sourced event definitions, search semantics, time scale, and per-output comparison policy |

Any scope expansion changes the fixture meaning and requires a separately
reviewed identifier/revision decision.

## Calculation configuration register

The status vocabulary in this register is exactly `selected`, `proposed`,
`unresolved`, or `not applicable`. BhaktiAstro implementation details are
lineage observations, not reference truth.

| Configuration field | Status | Planned value or blocking explanation |
| --- | --- | --- |
| Ayanamsha system | `not applicable` | No sidereal or derived Panchang output is included |
| Ephemeris engine | `proposed` | BhaktiAstro's comparison side calls Swiss Ephemeris for Julian Day; the qualifying reference path must be independently selected |
| Engine version | `unresolved` | The repository pins `pyswisseph==2.10.3.2`, but the executed wrapper/library build and independent reference version must be captured later |
| Ephemeris data files or fallback mode | `not applicable` | Julian calendar conversion should not require position files; this must not be generalized to deferred ephemeris or rise/set scopes |
| Calculation flags | `not applicable` | The current Julian helper calls `swe.julday` rather than a flagged position calculation |
| Tropical versus sidereal frame | `not applicable` | No longitude is included |
| Geocentric versus topocentric mode | `not applicable` | No location-dependent astronomical output is included |
| Coordinate assumptions | `not applicable` | Coordinates remain required identity blockers but are not inputs to either candidate output |
| Node mode | `not applicable` | No lunar node or planetary output is included |
| Rise/set model | `not applicable` | Every rise/set output is deferred |
| Refraction policy | `not applicable` | Every rise/set output is deferred |
| Solar-disc policy | `not applicable` | Every rise/set output is deferred |
| Elevation policy | `selected` | Null for the narrow candidate scopes; scope expansion requires new review |
| Calendar | `selected` | Gregorian civil calendar |
| Time scale | `proposed` | Versioned timezone conversion to UTC followed by source-aligned Julian Day UT; exact UTC/UT semantics remain a blocker |
| Rounding policy | `proposed` | Preserve source-native unrounded values and compare before display rounding |
| Serialization precision | `unresolved` | Must be derived from qualifying source precision and the owning runtime contract without truncating evidence |
| Language/localization policy | `selected` | Stable English machine identifiers; preserve source-native labels in evidence, with no localized expected output in scope |

## Reference-source candidate plan

No qualifying source has been selected. Canonical source IDs cannot yet be
allocated because `GRS-<SOURCE_TOKEN>-V1` must identify a real product or
publication, not an invented planning label. Each slot below therefore records
the required ID pattern and selection criteria without pretending that a
source exists.

### Primary candidate slot - timezone context

| Field | Requirement or status |
| --- | --- |
| Provisional source identifier | Unassigned; must become `GRS-<TIMEZONE_PRODUCT>-V1` after product selection |
| Source category | Required `trusted_public_standard` |
| Intended trust level | Proposed `primary` for timezone context only |
| Source name | Unresolved; select the direct responsible timezone database or official standard product |
| Publisher or maintainer | Unresolved with source selection |
| Version | Unresolved; an exact database release is mandatory |
| Publication date | Unresolved; must come from the selected source record |
| Access date | Unresolved; must record the actual later evidence-collection date |
| Citation | Unresolved; stable product/version citation required |
| Engine or methodology | Versioned timezone rules for `Asia/Kolkata` |
| Configuration compatibility | Must establish the selected local instant, offset, DST state, fold, calendar, and UTC conversion |
| Expected outputs available | Not assessed; no values collected |
| Lineage relationship to BhaktiAstro | Must be direct standard evidence rather than BhaktiAstro or host-environment output |
| Independence assessment | Not performed |
| Approval state | Candidate slot only; not approved |

### Independent secondary candidate slot - timezone context

| Field | Requirement or status |
| --- | --- |
| Provisional source identifier | Unassigned; must become `GRS-<INDEPENDENT_TIME_PRODUCT>-V1` after selection |
| Source category | Required `independent_reference_software` or `published_astronomical_table`, as applicable |
| Intended trust level | Proposed `secondary` |
| Source name | Unresolved; must be reproducible and materially independent of BhaktiAstro's conversion path |
| Publisher or maintainer | Unresolved with source selection |
| Version | Unresolved and mandatory |
| Publication date | Unresolved and mandatory |
| Access date | Unresolved until evidence is collected |
| Citation | Unresolved; stable citation required |
| Engine or methodology | Must expose timezone-data lineage and local/UTC conversion method |
| Configuration compatibility | Must use the same selected instant and declared timezone database or explain version differences |
| Expected outputs available | Not assessed; no values collected |
| Lineage relationship to BhaktiAstro | Shared host timezone output alone is insufficient |
| Independence assessment | Not performed |
| Approval state | Candidate slot only; not approved |

### Primary candidate slot - Julian Day

| Field | Requirement or status |
| --- | --- |
| Provisional source identifier | Unassigned; must become `GRS-<JULIAN_PRODUCT>-V1` after selection |
| Source category | Required `authoritative_ephemeris` or another category shown by review to be Primary for this scope |
| Intended trust level | Proposed `primary` for Julian Day only |
| Source name | Unresolved; select a direct versioned authoritative product with a reproducible case |
| Publisher or maintainer | Unresolved with source selection |
| Version | Unresolved and mandatory |
| Publication date | Unresolved and mandatory |
| Access date | Unresolved until evidence is collected |
| Citation | Unresolved; direct product or publication citation required |
| Engine or methodology | Must define calendar, time scale, epoch/day-start convention, and precision |
| Configuration compatibility | Must accept or publish the exact independently established UTC instant under compatible UTC/UT semantics |
| Expected outputs available | Not assessed; no values collected |
| Lineage relationship to BhaktiAstro | Must not derive the expected value from BhaktiAstro output |
| Independence assessment | Not performed |
| Approval state | Candidate slot only; not approved |

### Independent secondary candidate slot - Julian Day

| Field | Requirement or status |
| --- | --- |
| Provisional source identifier | Unassigned; must become `GRS-<INDEPENDENT_JULIAN_PRODUCT>-V1` after selection |
| Source category | Required `published_astronomical_table`, `independent_manual_calculation`, or qualifying `independent_reference_software` |
| Intended trust level | Proposed `secondary` |
| Source name | Unresolved; select only after its engine/data lineage is known |
| Publisher or maintainer | Unresolved with source selection |
| Version | Unresolved and mandatory |
| Publication date | Unresolved and mandatory |
| Access date | Unresolved until evidence is collected |
| Citation | Unresolved; stable citation or reproducible worksheet reference required |
| Engine or methodology | Must independently reproduce Julian Day from documented inputs and intermediate steps |
| Configuration compatibility | Must match calendar, time scale, instant, day-start convention, and precision |
| Expected outputs available | Not assessed; no values collected |
| Lineage relationship to BhaktiAstro | A Swiss Ephemeris frontend may share BhaktiAstro's material lineage and must not be presumed independent |
| Independence assessment | Not performed |
| Approval state | Candidate slot only; not approved |

A candidate is not approved merely because it is popular, public, or easy to
access. Shared Swiss Ephemeris lineage may fail the independence requirement,
and two interfaces over one underlying engine do not constitute independent
verification.

## Source-lineage analysis

The following observations come only from repository code and dependency
declarations; they are not accuracy evidence:

- `requirements.txt` pins `pyswisseph==2.10.3.2`.
- `backend/app/astronomy/julian.py` converts a caller-supplied numeric UTC
  offset into a UTC datetime, then calls `swisseph.julday` with
  `swisseph.GREG_CAL`.
- the Panchang request accepts a numeric `timezone_offset`; it does not accept
  or validate an IANA timezone identifier or tzdata version;
- `backend/app/config.py` names `Asia/Kolkata` as an environment-overridable
  default, but that default is not proof of the selected instant's offset or
  DST state;
- the Panchang request exposes Lahiri ayanamsha and a language preference, but
  the Panchang route does not forward either field to the basic calculator;
- the configured `data/ephe` directory exists but contains no files in this
  checkout; behavior that depends on Swiss Ephemeris fallback data must be
  captured before ephemeris-dependent scope is considered;
- rise/set code uses Swiss Ephemeris, `FLG_SWIEPH`, disc-centre mode, a
  zero-altitude geoposition, and a numeric timezone offset; it is excluded here
  because refraction, fallback, coordinate, elevation, and event-definition
  compatibility are not independently established; and
- Julian Day is returned as a float without an explicit domain rounding step,
  while other astronomy outputs apply their own rounding. Source precision and
  serialization precision therefore require separate review.

Before any source is approved, review must establish the exact timezone-data
lineage, active Swiss wrapper/library build, UTC/UT semantics, Gregorian
calendar convention, Julian Day methodology and precision, shared engine/data
lineage, and reproducibility of every selected source. Deferred scopes also
require ayanamsha, ephemeris/fallback, flags, coordinate mode, rise/set model,
rounding, and serialization alignment.

## Expected-value boundary

No expected astronomical value is authorized or present in this task. In
particular, this record contains no Julian Day, planetary longitude, ayanamsha,
Panchang identity, boundary time, or rise/set value.

- No value may be copied from current BhaktiAstro output.
- No placeholder number may be treated as a reference value.
- Expected values must be acquired in a later separately approved task.
- Acquisition must preserve each source's original units, precision,
  configuration, and observed value before normalization.
- All source differences must be retained and reviewed before any comparison
  tolerance is assigned.

The selected civil date and local wall time are inputs, not expected
astronomical results.

## Proposed future comparison method

The future review may use exact comparison for categorical identities, timezone
identifier, offset, fold, and other discrete fields when their sources and
definitions align. Numeric fields require field-specific comparison modes and
tolerances justified only after source precision and agreement are known.
Angular outputs in a future expanded scope require shortest-distance,
wrap-aware comparison across the longitude boundary. Time comparisons require
an explicit time scale, IANA timezone and version, local/UTC consistency, and
documented event definition.

Review must not average conflicting sources, use majority vote as truth, widen
a tolerance to make a test pass, or prefer the source closest to BhaktiAstro
output. This record assigns no numeric tolerance.

## Reviewer and approval status

| Field | Status |
| --- | --- |
| Reviewer | Unassigned; no approved reviewer is named by repository evidence |
| Review date | Not scheduled |
| Fixture approval | Not approved |
| Source approval | Not approved; no source selected |
| Expected values | Not collected |
| Regression eligibility | Prohibited |
| Machine fixture eligibility | Blocked |

## Promotion gates

Every gate is currently blocked:

- [ ] exact case inputs are reviewed and approved;
- [ ] qualifying canonical source records are complete;
- [ ] source independence from BhaktiAstro and between qualifying sources is
      confirmed per candidate output;
- [ ] expected values are independently obtained with source-native precision;
- [ ] calculation and time-configuration compatibility is established;
- [ ] original observations and every difference are retained and reviewed;
- [ ] comparison modes and per-output tolerances are justified;
- [ ] a named reviewer is assigned;
- [ ] the review date is recorded;
- [ ] every blocker and out-of-policy discrepancy is resolved or the affected
      output is removed; and
- [ ] fixture classification, fixture lifecycle, source lifecycle, and vector
      verification advance only under their canonical specifications.

Machine data and test activation require additional separately authorized
fixture-schema, provenance, test, and regression gates even after this list is
complete.

## Blocker register

| Blocker ID | Description | Affected field or output | Required evidence | Permitted source category | Owner or reviewer state | Resolution status |
| --- | --- | --- | --- | --- | --- | --- |
| `MUM-TIME-001` | Country-code standard and exact code are not confirmed | Country code | Versioned country-code standard | `trusted_public_standard` | Unassigned | Open |
| `MUM-GEO-001` | Reference latitude, longitude, precision, datum, and source are absent | Location identity | Direct geospatial standard or reproducible published coordinates | `trusted_public_standard` or `published_astronomical_table` | Unassigned | Open |
| `MUM-TIME-002` | Timezone database version, offset, DST status, fold, and UTC instant are unverified | `timezone_validation` and case instant | Versioned timezone authority for the exact local instant | `trusted_public_standard` | Unassigned | Open |
| `MUM-TIME-003` | Independent timezone corroboration is not selected | `timezone_validation` | Reproducible independent conversion with disclosed lineage | `independent_reference_software` or `published_astronomical_table` | Unassigned | Open |
| `MUM-JD-001` | Primary Julian Day source is not selected | `julian_day` | Direct versioned authoritative product defining calendar, time scale, and precision | `authoritative_ephemeris` | Unassigned | Open |
| `MUM-JD-002` | Independent Julian Day corroboration is not selected | `julian_day` | Independent reproducible publication, worksheet, or software path | `published_astronomical_table`, `independent_manual_calculation`, or `independent_reference_software` | Unassigned | Open |
| `MUM-LINEAGE-001` | Source independence and shared Swiss/data lineage are not assessed | All candidate outputs | Written publisher, dataset, engine, operator, and BhaktiAstro lineage analysis | Any qualifying category after selection | Reviewer unassigned | Open |
| `MUM-CONFIG-001` | Exact UTC/UT treatment and Julian Day convention are not aligned | `julian_day` | Configuration comparison across both qualifying sources and BhaktiAstro | Qualifying source records plus review | Reviewer unassigned | Open |
| `MUM-CONFIG-002` | Active Swiss build and serialization precision are not captured | Comparison-side configuration | Reproducible environment record and owning-contract review | Supporting implementation evidence; not a qualifying expected-value source | Reviewer unassigned | Open |
| `MUM-VALUE-001` | No independently sourced timezone or Julian expected values exist | All candidate outputs | Original source observations with versions, settings, units, and precision | Approved `primary` and materially independent `secondary` sources | Unassigned | Open |
| `MUM-COMPARE-001` | Differences and per-output comparison policies are absent | All candidate outputs | Side-by-side observation record and reviewer-justified comparison policy | Qualifying source records plus review | Reviewer unassigned | Open |
| `MUM-REVIEW-001` | Reviewer and review date are absent | Entire record | Named accountable reviewer and actual review date | Repository review process | Reviewer unassigned | Open |
| `MUM-PROMOTE-001` | Classification, source, fixture, and test activation gates are incomplete | Fixture eligibility | Completed canonical promotion workflow and separate execution authorization | Canonical specifications | Reviewer unassigned | Open |

## Explicit non-goals

This record does not authorize runtime implementation, machine JSON, fixture
schema code, loader or validator code, current-output snapshots, expected-value
assertions, tolerance implementation, regression activation, skipped-test
changes, Jodhpur or Delhi changes, accuracy claims, Validation Plan status
changes, or Sprint 16 work. It also changes no calculation, dependency,
configuration, API, public export, or existing fixture.

## Current disposition

Fixture lifecycle remains `proposed`; vector verification remains `pending`.
No source, expected value, tolerance, reviewer, machine fixture, or automated
test is approved by this record.
