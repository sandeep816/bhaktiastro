# GF-MUMBAI-20240701-TIME_JD-V1 - Mumbai Time and Julian Day Evidence Plan

## Record identity

| Field | Value |
| --- | --- |
| Provisional fixture ID | `GF-MUMBAI-20240701-TIME_JD-V1` |
| Record title | Mumbai Time and Julian Day Evidence Plan |
| Owning task | [Sprint 15, Task 15.3](../../SPRINT-15.md#task-153---mumbai-reference-case-selection-and-provisional-evidence-record) |
| Source-selection task | [Sprint 15, Task 15.4](../../SPRINT-15.md#task-154---mumbai-independent-reference-source-selection) |
| Fixture schema relationship | Human planning record aligned with `bhaktiastro.golden-fixture` version `1.0`; not a machine-schema instance |
| Source schema relationship | Three selected provisional source products aligned with `bhaktiastro.golden-reference-source` version `1.0`; no canonical source record exists and no source is approved |
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
- identifies provisional reference-source products but does not approve them;
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

## Selected provisional reference-source products

Task 15.4 selects the following real products as **provisional candidates**.
Selection assigns a stable proposed identity and a scope-specific category and
trust intention; it is not source-schema approval, source lifecycle promotion,
expected-value acquisition, or fixture verification. Every source lifecycle
remains `proposed`, every review decision remains `pending`, and the reviewer
is unassigned.

| Provisional source ID | Product | Canonical category | Intended trust | Declared scope | Independence status |
| --- | --- | --- | --- | --- | --- |
| `GRS-IANA_TZDB_2024B-V1` | IANA Time Zone Database release 2024b | `trusted_public_standard` | `primary` | `timezone_validation` | Confirmed relative to BhaktiAstro's numeric-offset implementation; it is the upstream data lineage for any 2024b-based `zoneinfo` check and does not independently corroborate itself |
| `GRS-IAU_SOFA_CALENDAR-V1` | IAU SOFA Time Scale and Calendar Tools, software version 18, document revision 1.63 | `authoritative_ephemeris` | `primary` | `julian_day` | Provisionally acceptable relative to BhaktiAstro; reviewer confirmation of implementation lineage remains required |
| `GRS-USNO_JULIAN_DATE-V1` | USNO Julian Date Converter with official conversion-method FAQ | `independent_reference_software` | `secondary` | `julian_day` | Unresolved relative to both SOFA and BhaktiAstro because the live converter's exact backend version and implementation lineage are not published on the cited pages |

`authoritative_ephemeris` is used for the SOFA selection only in the canonical
category's scope-bounded sense of a direct, versioned official astronomical
product from its responsible institution. SOFA supplies authoritative
astronomical standards, algorithms, and time/calendar procedures, not a
celestial-position ephemeris for this case. The assignment does not extend
Primary trust beyond Gregorian-calendar, time-scale, and Julian Date
methodology.

`independent_reference_software` is a better fit than
`published_astronomical_table` for the USNO selection because the proposed
product is an interactive converter. Its official FAQ and the cited 1990
*Almanac for Computers* formula provide method evidence, but they do not turn
the live converter into a versioned table or disclose its exact backend.

### `GRS-IANA_TZDB_2024B-V1` - IANA Time Zone Database 2024b

| Field | Selected evidence or status |
| --- | --- |
| Source name | Time Zone Database release 2024b |
| Publisher or maintainer | Internet Assigned Numbers Authority (IANA); the maintenance procedure is described by IETF BCP 175 / RFC 6557 |
| Canonical category | `trusted_public_standard` |
| Intended trust level | `primary` for `timezone_validation` only |
| Product/version | `tzdb-2024b` |
| Publication date | `2024-09-04`, from the official IANA release history |
| Access date | `2026-08-03` |
| Stable citations | [IANA Time Zone Database](https://www.iana.org/time-zones); [IANA 2024b release directory](https://data.iana.org/time-zones/tzdb-2024b/); [IANA release history](https://www.iana.org/time-zones/releases); [RFC 6557](https://datatracker.ietf.org/doc/html/rfc6557) |
| Applicable data files | Release-pinned `asia`, `tzdata.zi`, `zone1970.tab`, `backward`, `version`, and `NEWS`; the 2024b `asia` source contains the `Asia/Kolkata` zone |
| Calculation engine | TZDB 2024b reference code and compiled zone data; no implementation was executed in this task |
| Timezone database version | `2024b` |
| Methodology | Machine-readable zone and rule records used with the TZDB reference implementation to determine local-time rules and offsets; RFC 6557 describes maintenance governance but is not the offset dataset |
| Relevant configuration | Exact release 2024b, zone `Asia/Kolkata`, Gregorian local civil instant selected by this record; later acquisition must record the tool and command used to evaluate the release |
| Precision | Rule data can represent offsets and transitions at its source resolution; no offset, instant, or comparison precision is extracted or approved here |
| Available outputs | Zone identity and versioned civil-time rules capable of supporting later offset, DST, fold, and UTC-conversion evidence |
| Source lineage | Direct IANA release data maintained under the TZDB process; not derived from BhaktiAstro |
| Relationship to BhaktiAstro | BhaktiAstro currently accepts a caller-supplied numeric offset and does not perform an IANA-zone conversion. Python `zoneinfo` loaded from TZDB 2024b would be an execution path over this same source, not an independent source |
| Independence assessment | **Confirmed** as external primary standard evidence relative to BhaktiAstro's current numeric-offset calculation path; **unresolved** for the required second timezone source because no independent corroborating product is selected |
| Compatibility assessment | Compatible in identity and modern-date scope: release 2024b explicitly contains `Asia/Kolkata`; exact offset, DST, fold, and UTC conversion remain unacquired |
| Limitations | The selected release is pinned rather than current; this record does not generalize its modern rule to historical Mumbai; RFC 6557 supplies governance only; no second independent timezone source is selected |
| Selection status | Selected provisional candidate |
| Source lifecycle / approval | `proposed`; not approved |
| Reviewer status | Unassigned; review decision `pending` |

### Unfilled independent timezone corroboration slot

The standard verification route still requires a materially independent
`primary` or `secondary` corroborator for the selected instant unless a
canonical exception is later reviewed and approved. Python `zoneinfo` using
TZDB 2024b, another packaging of the same TZDB release, or a web interface
backed only by TZDB 2024b would share the IANA data lineage and cannot fill this
slot merely by producing the same conversion. No product is selected for this
slot, and `MUM-TIME-003` remains open.

### `GRS-IAU_SOFA_CALENDAR-V1` - IAU SOFA Time Scale and Calendar Tools

| Field | Selected evidence or status |
| --- | --- |
| Source name | SOFA Time Scale and Calendar Tools, Fortran edition |
| Publisher or maintainer | International Astronomical Union Standards of Fundamental Astronomy (IAU SOFA) Board; distributed through the IAU SOFA Center |
| Canonical category | `authoritative_ephemeris`, scope-bounded to the canonical category's official astronomical-product route |
| Intended trust level | `primary` for `julian_day` methodology only |
| Product/version | Cookbook software version 18, document revision 1.63 |
| Publication date | `2023-05-31`, printed in the selected official cookbook |
| Access date | `2026-08-03` |
| Stable citations | [IAU SOFA service](https://www.iausofa.org/); [SOFA cookbooks](https://www.iausofa.org/cookbooks); [SOFA Time Scale and Calendar Tools, Fortran PDF](https://www.iausofa.org/s/sofa_ts_f.pdf) |
| Calculation engine | IAU SOFA Fortran calendar and time-scale routine set, software version 18 |
| Timezone database version | `not_applicable`; SOFA is selected for Julian/calendar methodology, not civil-zone rules |
| Methodology | Documented SOFA calendar and time-scale routines, including Gregorian calendar conversion, two-part Julian Date representation, UTC leap-second treatment, and explicit transformations among UTC, UT1, TAI, TT, TCG, TDB, and TCB |
| Relevant configuration | Gregorian calendar; exact future input time scale must be declared; two-part date representation must be preserved until any separately authorized output extraction; DUT1 or delta-T inputs are caller responsibilities where the selected transformation requires them |
| Precision | Two-part Julian Date representation is designed to preserve time resolution; the cookbook documents precision and warning behavior by routine, but this task assigns no comparison tolerance |
| Available outputs | Reproducible methodology and routines for calendar-to-Julian conversion and supported time-scale transformations; no Mumbai output is acquired here |
| Source lineage | Official IAU SOFA algorithms and code; the selected cookbook is tied to SOFA software version 18 and is separate from the later SOFA library issue advertised by the website |
| Relationship to BhaktiAstro | BhaktiAstro calls `swisseph.julday`; no repository code calls SOFA. The products have different publishers and implementations, but final reviewer evidence must confirm there is no material copied implementation path |
| Independence assessment | **Provisionally acceptable** relative to BhaktiAstro; not yet reviewer-confirmed. SOFA does not depend on Swiss Ephemeris in the cited product materials |
| Compatibility assessment | Methodologically compatible with the selected modern Gregorian case, subject to later exact alignment of UTC versus UT1 semantics, leap-second handling, date representation, and retained precision |
| Limitations | The selected cookbook is version 18/revision 1.63 while the SOFA site separately identifies library issue 2023-10-11 as the nineteenth release; future execution must pin the code release used for any generated value and must not conflate UTC quasi-JD with UT1 JD |
| Selection status | Selected provisional candidate |
| Source lifecycle / approval | `proposed`; not approved |
| Reviewer status | Unassigned; review decision `pending` |

### `GRS-USNO_JULIAN_DATE-V1` - USNO Julian Date resources

| Field | Selected evidence or status |
| --- | --- |
| Source name | U.S. Naval Observatory Julian Date Converter, supported by the FAQ “Converting Between Julian Dates and Gregorian Calendar Dates” |
| Publisher or maintainer | U.S. Naval Observatory, Astronomical Applications Department |
| Canonical category | `independent_reference_software` |
| Intended trust level | `secondary` for `julian_day` |
| Product/version | **Unresolved:** the official pages expose no converter release/build or backend version |
| Publication date | **Unresolved:** the official pages expose no page or converter publication date; the FAQ attributes one formula to the 1990 edition of the discontinued *Almanac for Computers*, which is method provenance rather than the live converter's publication date |
| Access date | `2026-08-03` |
| Stable citations | [USNO Julian Date Converter](https://aa.usno.navy.mil/data/JulianDate); [USNO Julian/Gregorian conversion FAQ](https://aa.usno.navy.mil/faq/JD_formula) |
| Calculation engine | **Unresolved:** the live converter backend and build are not disclosed on the cited pages |
| Timezone database version | `not_applicable`; the selected product accepts UT1 and is not a local-civil timezone converter |
| Methodology | The converter accepts Gregorian calendar input with UT1. The FAQ defines Julian Date from Greenwich mean noon, gives a Gregorian-to-JD formula for 1801-2099, attributes it to the 1990 *Almanac for Computers*, and supplies separate sample code based on Fliegel and van Flandern algorithms |
| Relevant configuration | Gregorian calendar, UT1 input, noon-based Julian day convention; later use must establish which documented method the live converter executes and align the exact independently established instant |
| Precision | The converter accepts fractional seconds and displays a finite decimal result; the page discusses approximate double-precision capability, but the backend precision and output-rounding contract are not versioned and no tolerance is assigned |
| Available outputs | Interactive calendar-to-Julian and Julian-to-calendar conversion plus published definitions and formula documentation; no Mumbai output is acquired here |
| Source lineage | Official USNO web product and documentation; exact live backend, software version, and relationship between the converter and published formulas are unresolved |
| Relationship to SOFA | Different published product and interface, but possible shared standard formula heritage is not enough to establish material algorithm independence; the live backend is undisclosed |
| Relationship to BhaktiAstro | Different publisher and no stated Swiss Ephemeris dependency, but the undisclosed converter implementation prevents confirmed implementation independence from `swisseph.julday` |
| Independence assessment | **Unresolved** relative to both IAU SOFA and BhaktiAstro |
| Compatibility assessment | Definitions align at a high level with Gregorian calendar, UT1, and the noon boundary; exact UTC-to-UT1 treatment, backend method, retained precision, and rounding compatibility remain unresolved |
| Limitations | No product version, publication date, backend implementation, API contract, or independent lineage evidence is published on the cited pages; the FAQ formula has a stated date range and must not be generalized outside it |
| Selection status | Selected provisional candidate; not yet qualifying as the independent corroborator |
| Source lifecycle / approval | `proposed`; not approved |
| Reviewer status | Unassigned; review decision `pending` |

A candidate is not approved merely because it is official, public, or easy to
access. Selection retains unknown metadata explicitly, and no source may enter
a qualifying fixture `source_ids` list until its source record and canonical
review are complete.

## Source-lineage analysis

The following repository observations and official product descriptions are
lineage evidence only; they are not expected-value or accuracy evidence:

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

### Required pairwise lineage decisions

1. **IANA TZDB versus Python `zoneinfo`:** IANA TZDB 2024b is the selected
   upstream standard. A Python `zoneinfo` execution loaded from that release is
   a reproducible consumer path, not a materially independent second source.
   Python's library code may independently exercise parsing and conversion, but
   it cannot independently verify a defect shared in the 2024b rule data.
2. **SOFA versus BhaktiAstro Julian Date:** the selected SOFA product is
   maintained by IAU SOFA and documents its own calendar/time-scale routines;
   BhaktiAstro calls Swiss Ephemeris through `pyswisseph`. Publisher and
   implementation paths differ, so independence is provisionally acceptable,
   but reviewer confirmation of the exact executed SOFA and Swiss code lineage
   remains required.
3. **USNO versus SOFA:** the organizations and interfaces differ. The USNO FAQ
   publishes definitions and algorithms, while SOFA publishes its own routines,
   but the live USNO converter does not disclose its backend or version.
   Material algorithm independence is therefore unresolved.
4. **USNO versus BhaktiAstro:** USNO does not state that its converter uses
   Swiss Ephemeris, and BhaktiAstro does not call USNO. The absence of a
   disclosed USNO backend nevertheless prevents confirmed implementation
   independence, so this relationship remains unresolved.
5. **Swiss Ephemeris dependency:** BhaktiAstro depends on `pyswisseph` and
   `swisseph.julday`. The cited IANA, SOFA, and USNO materials state no Swiss
   Ephemeris dependency. This supports separation for IANA and SOFA; it is not
   enough to resolve USNO's undisclosed backend.
6. **Two-source verification:** the current timezone set does not satisfy the
   standard route because it has no independent corroborator. The Julian set
   names two products, but it also does not yet satisfy the route because USNO
   independence, version, reproducibility, and source approval remain
   unresolved. Product count alone is not independent verification.

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

- No UTC conversion value or final UTC instant has been acquired or approved.
- No value may be copied from current BhaktiAstro output.
- No BhaktiAstro output has been copied into this record.
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
| Source selection | Three provisional candidates selected; independent timezone corroboration remains unfilled |
| Source approval | Not approved; all selected source lifecycles remain `proposed` and review decisions remain `pending` |
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
| `MUM-TIME-002` | IANA TZDB 2024b is selected, but offset, DST status, fold, and UTC instant remain unacquired and unverified | `timezone_validation` and case instant | Source-native evaluation of the exact local instant plus canonical review | `trusted_public_standard` | Reviewer unassigned; source approval pending | Open; product/version selection alone does not resolve the value and review blocker |
| `MUM-TIME-003` | Independent timezone corroboration is not selected | `timezone_validation` | Reproducible independent conversion with disclosed lineage | `independent_reference_software` or `published_astronomical_table` | Unassigned | Open |
| `MUM-JD-001` | A scope-bounded Primary Julian methodology product is selected | `julian_day` | IAU SOFA Time Scale and Calendar Tools version 18, document revision 1.63 | `authoritative_ephemeris` | Reviewer unassigned; source approval pending | Resolved for product selection by `GRS-IAU_SOFA_CALENDAR-V1`; canonical source-record verification and approval remain required |
| `MUM-JD-002` | USNO is selected provisionally, but its version, backend lineage, reproducibility, and material independence are unresolved | `julian_day` | Product/version and backend evidence sufficient to establish an independent reproducible path | `independent_reference_software` | Reviewer unassigned; source approval pending | Open; `GRS-USNO_JULIAN_DATE-V1` does not yet qualify as independent corroboration |
| `MUM-LINEAGE-001` | Pairwise lineage is documented, but timezone corroboration is absent and USNO independence remains unresolved | All candidate outputs | Reviewer-confirmed publisher, dataset, engine, operator, and BhaktiAstro lineage analysis | Any qualifying category after selection | Reviewer unassigned | Open; SOFA/BhaktiAstro is only provisionally acceptable |
| `MUM-CONFIG-001` | SOFA and USNO conventions are documented, but exact UTC/UT1 treatment and executed-method alignment are incomplete | `julian_day` | Configuration comparison across both qualifying sources and BhaktiAstro | Qualifying source records plus review | Reviewer unassigned | Open |
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
Three source products are selected as provisional candidates, but every source
lifecycle remains `proposed`, every review decision remains `pending`, and no
source is approved. No UTC-conversion value or Julian Date value has been
acquired or approved, no BhaktiAstro output has been copied, no numeric
tolerance has been assigned, and no regression assertion is permitted. No
fixture, reviewer, machine data, or automated test is approved by this record.
