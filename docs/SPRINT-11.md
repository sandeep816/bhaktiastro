# Sprint 11 - Matchmaking Foundation

Sprint 11 establishes deterministic compatibility infrastructure that consumes
reusable birth and Kundali data. It keeps matchmaking calculations separate
from astrology calculation engines and from future API, reporting, and UI
layers.

## Sprint Status

Status: **In Progress (Task 11.4 Complete)**

## Architecture Boundary

```text
Birth details
    -> Kundali calculations
    -> Reusable matchmaking inputs
    -> Deterministic compatibility calculators
    -> Structured matchmaking result
    -> Future API / reports / UI
```

Matchmaking components must consume existing astrology output where available.
They must not mutate or recalculate Kundali data, generate predictions or
advice, call AI or external services, or include presentation formatting.

## Task 11.1 - Matchmaking Foundation Architecture

Status: **Complete**

Task 11.1 provides only:

- JSON-safe person and ordered-pair input structures.
- A stable, unevaluated matchmaking result structure.
- Deterministic empty and populated factories.
- Safe text, numeric, collection, and metadata normalization.
- Public foundation exports and focused contract tests.

No compatibility score, Koota rule, Manglik rule, judgment, interpretation,
remedy, API route, report, or UI behavior is implemented.

## Task 11.2 - Matchmaking Input Validation

Status: **Complete**

Task 11.2 adds deterministic validation over the Task 11.1 person and pair
factories. It provides:

- JSON-safe validation results and localization-ready issue keys.
- Stable issue codes and deterministic issue ordering.
- Optional ISO date, ISO time, and IANA timezone validation.
- Latitude (`-90..90`), longitude (`-180..180`), and Nakshatra Pada (`1..4`)
  boundary validation when those values are supplied.
- Strict unknown-field handling consistent with existing project schemas.
- Ordered nested pair validation and duplicate non-empty person ID detection.
- Normalized Task 11.1 person and pair values without input mutation.

All person fields remain optional. Validation does not calculate missing Rashi,
Nakshatra, Lagna, compatibility factors, or scores. It produces no API errors,
UI messages, interpretations, or judgments.

Compatibility is preserved by leaving Task 11.1 models and factories unchanged
and exposing validation as a separate opt-in layer.

Verification for Task 11.2:

- Matchmaking foundation and validation tests: 60 passed.
- Rashi, Nakshatra, and Kundali regression tests: 51 passed.
- Full suite: 1028 passed, 13 skipped, and 20 subtests passed.

## Task 11.3 - Nakshatra Compatibility Foundation

Status: **Complete**

Task 11.3 adds a reusable Nakshatra pair-context foundation for future
matchmaking calculators. It provides:

- Canonical Nakshatra identity normalization from supplied names, indexes, or
  matchmaking person structures.
- Reuse of `backend.app.constants.nakshatra.NAKSHATRA_LIST` without a second
  Nakshatra list.
- Zero-based Nakshatra indexes matching the core project convention:
  Ashwini is index `0` and Revati is index `26`.
- Optional Pada preservation and validation for values `1..4`.
- Deterministic circular distances for ordered pairs:
  `forward_distance = (index_b - index_a) mod 27` and
  `reverse_distance = (index_a - index_b) mod 27`.
- Same-Nakshatra distance behavior where the forward and reverse distances are
  both `0`.
- Stable, localization-ready issue codes for missing or invalid Nakshatra data.
- JSON-safe output that preserves `person_a` and `person_b` ordering without
  mutating inputs.

Task 11.3 does not calculate Moon longitude, derive Nakshatra from birth data,
assign Koota points, calculate Tara/Yoni/Gana/Nadi/Bhakoot/Graha Maitri, produce
compatibility labels, or generate interpretation text.

Compatibility is preserved by adding Nakshatra context helpers as an opt-in
matchmaking module and leaving Task 11.1 and Task 11.2 public contracts
unchanged.

Verification for Task 11.3:

- Matchmaking foundation, validation, and Nakshatra tests: 86 passed.
- Core Nakshatra regression tests: 15 passed.
- Full suite: 1054 passed, 13 skipped, and 20 subtests passed.

## Task 11.4 - Varna Koota

Status: **Complete**

Task 11.4 adds deterministic Varna Koota scoring from already supplied Rashi
data. It provides:

- Reuse of `backend.app.constants.rashi.RASHI_LIST` without a second Rashi
  list.
- One-based Rashi indexes matching the core project convention:
  Aries/Mesha is index `1` and Pisces/Meena is index `12`.
- A centralized element-based deterministic Varna mapping:
  - Water signs (`Karka`, `Vrishchika`, `Meena`) -> `brahmin`
  - Fire signs (`Mesha`, `Simha`, `Dhanu`) -> `kshatriya`
  - Earth signs (`Vrishabha`, `Kanya`, `Makara`) -> `vaishya`
  - Air signs (`Mithuna`, `Tula`, `Kumbha`) -> `shudra`
- Stable Varna ranks: `shudra = 1`, `vaishya = 2`, `kshatriya = 3`,
  `brahmin = 4`.
- Explicit directional scoring only. Callers must provide `subject_role` and
  `comparison_role`; no gender, bride, groom, or marriage role is inferred.
- Maximum score `1`. The score is `1` when the comparison role's Varna rank is
  greater than or equal to the subject role's Varna rank, otherwise `0`.
- Safe invalid results for missing Rashi, unknown Rashi, out-of-range indexes,
  missing direction, or invalid roles.
- JSON-safe structured output with no compatibility judgement or prose.

Task 11.4 does not calculate Moon sign, derive Rashi from birth data, calculate
any other Koota, aggregate Ashtakoota, infer roles, produce final matchmaking
judgement, or generate advice/remedy/interpretation text.

Compatibility is preserved by adding Varna helpers as an opt-in matchmaking
module and leaving Tasks 11.1 through 11.3 public contracts unchanged.

Verification for Task 11.4:

- Matchmaking foundation, validation, Nakshatra, and Varna tests: 109 passed.
- Core Rashi regression tests: 18 passed.
- Full suite: 1077 passed, 13 skipped, and 20 subtests passed.

## Task 11.5 - Vashya Koota

Status: **Specification Complete; Runtime Not Implemented**

### Purpose and Scope

Vashya Koota represents attraction, influence, and relational control. Its
maximum score is `2.0` points and its stable machine-readable compatibility
domain is `attraction`.

Task 11.5 runtime implementation must provide:

- reusable Vashya classification from one supplied sidereal Moon longitude;
- directional bride-row/groom-column scoring from two supplied sidereal Moon
  longitudes;
- the centralized category mapping and scoring matrix defined below; and
- a structured, JSON-safe result consistent with the Task 11.4 Varna Koota
  architecture.

The caller must supply the bride and groom roles explicitly. The calculator
must not infer gender, marriage role, or role direction from `person_a`,
`person_b`, names, identifiers, or input ordering. It must not calculate a Moon
longitude from birth data or mutate supplied Kundali or matchmaking data.

### Primary Input and Reused Rashi Logic

The only astrological value used to classify one person is that person's
sidereal Moon longitude in degrees. A geographic birth longitude, including
the existing `MatchmakingPerson.longitude` field, is not a Moon longitude and
must never be used as a substitute.

Runtime implementation must reuse `backend.app.kundali.rashi`:

- `normalize_longitude` for normalization into `[0, 360)`;
- `get_rashi` or the existing `get_rashi_index` and `get_rashi_degree` helpers
  to derive the one-based Rashi and degree within that Rashi; and
- `backend.app.constants.rashi.RASHI_LIST` and related constants for canonical
  Rashi identity and boundaries.

It must not duplicate longitude normalization, Rashi calculation logic, or the
canonical Rashi list. Classification uses the canonical precision produced by
the reused Rashi utilities so floating-point behavior remains deterministic.

### Canonical Vashya Categories

The stable machine-readable category identifiers are:

- `chatushpada`
- `manava`
- `jalachara`
- `vanachara`
- `keeta`

Every normalized sidereal Moon longitude maps to exactly one category:

| Vashya | Rashi and intra-Rashi range |
|---|---|
| `chatushpada` | Mesha; Vrishabha; Dhanu from `15°00′00″` through the end of the sign; Makara from `0°00′00″` through values strictly below `15°00′00″` |
| `manava` | Mithuna; Kanya; Tula; Kumbha; Dhanu from `0°00′00″` through values strictly below `15°00′00″` |
| `jalachara` | Karka; Meena; Makara from `15°00′00″` through the end of the sign |
| `vanachara` | Simha |
| `keeta` | Vrishchika |

The classification is exhaustive for all twelve Rashis. The two split-sign
rules are normative and take precedence over any whole-sign shortcut.

### Boundary Rules

- Dhanu at exactly `15°00′00″` within the sign is `chatushpada`.
- Makara at exactly `15°00′00″` within the sign is `jalachara`.
- Values below `15°00′00″`, at the canonical precision of the reused
  Rashi utilities, remain in the first-half category: `manava` for Dhanu and
  `chatushpada` for Makara.
- Global longitude `0°` is Mesha and therefore `chatushpada`.
- Normalized equivalents, including `360°`, negative values, and values
  greater than `360°`, must produce the same category as their normalized
  value in `[0, 360)`.
- Implementations must compare the canonical intra-Rashi degree against
  `15.0`; they must not introduce an independent epsilon or fuzzy boundary.

Examples of the split boundaries at the existing six-decimal Rashi precision:

| Sidereal Moon longitude | Derived position | Vashya |
|---:|---|---|
| `254.999999°` | Dhanu `14.999999°` | `manava` |
| `255.0°` | Dhanu `15.0°` | `chatushpada` |
| `284.999999°` | Makara `14.999999°` | `chatushpada` |
| `285.0°` | Makara `15.0°` | `jalachara` |

### Directional Scoring

Vashya scoring is directional. Rows represent the explicitly supplied bride's
Vashya and columns represent the explicitly supplied groom's Vashya. Reversing
the roles must transpose the lookup and may change the awarded score.

| Bride \ Groom | `chatushpada` | `manava` | `jalachara` | `vanachara` | `keeta` |
|---|---:|---:|---:|---:|---:|
| `chatushpada` | 2.0 | 1.0 | 1.0 | 1.5 | 1.0 |
| `manava` | 1.0 | 2.0 | 1.5 | 0.0 | 1.0 |
| `jalachara` | 1.0 | 1.5 | 2.0 | 1.0 | 1.0 |
| `vanachara` | 0.0 | 0.0 | 0.0 | 2.0 | 0.0 |
| `keeta` | 1.0 | 1.0 | 1.0 | 0.0 | 2.0 |

This matrix is the BhaktiAstro canonical Sprint 11.5 convention. Runtime code
must centralize it once, preserve row/column order, and must not symmetrize,
average, reinterpret, or silently substitute values. Same-category pairs
always receive the maximum `2.0` points.

### Public Contract

The runtime task must expose stable helpers from
`backend.app.matchmaking.__init__` for:

1. classifying a finite sidereal Moon longitude into a canonical Vashya
   identity;
2. looking up the directional score for explicit bride and groom category
   identifiers; and
3. calculating the structured Vashya Koota result from explicitly identified
   bride and groom sidereal Moon longitudes.

The structured result must expose at least:

- Koota identifier `vashya`;
- compatibility domain `attraction`;
- status;
- awarded score;
- maximum score `2.0`;
- bride Vashya identity, including normalized Moon longitude, Rashi,
  one-based Rashi index, intra-Rashi degree, and category;
- groom Vashya identity with the same fields;
- explicit direction metadata identifying the bride row and groom column;
- deterministic factors sufficient to audit the matrix lookup;
- stable errors and warnings;
- references and deterministic schema metadata consistent with the existing
  matchmaking result conventions.

Each returned object and nested collection must be newly allocated, must not
share mutable defaults, and must be treated as immutable after construction.
The calculator must not mutate caller inputs. Output ordering and
machine-readable identifiers must be stable and JSON-safe. No compatibility
judgement, interpretive paragraph, advice, remedy, API response, report, or UI
formatting belongs in this task.

### Validation and Exceptions

Low-level classification must preserve the existing Rashi utility contract:

- raise `TypeError` when a longitude is a boolean or is not a real number;
- raise `ValueError` when a longitude is `NaN`, positive infinity, or negative
  infinity; and
- accept finite negative and greater-than-`360` numeric longitudes and
  normalize them through the existing utility.

The category score lookup must:

- raise `TypeError` when either category is not a string; and
- raise `ValueError` when either string is empty, malformed, or is not one of
  the five canonical identifiers.

It must not case-fold, alias, or guess malformed category values. The
high-level structured Koota calculator must follow the existing Varna Koota
safe-result convention: it catches expected input validation failures, returns
status `invalid` with score `None`, and emits stable localization-ready issue
codes in deterministic bride-before-groom order. Unexpected programming errors
must not be swallowed.

### Required Runtime Tests

Task 11.5 implementation is not complete until focused tests cover:

- representative longitudes for all twelve Rashis and all five categories;
- Dhanu and Makara immediately below, exactly at, and immediately above their
  `15°` split boundaries;
- `0°`, `360°`, negative, and greater-than-`360°` normalization;
- every cell of the complete `5 x 5` bride-row/groom-column scoring matrix;
- directional asymmetric pairs, including both role orders;
- same-category maximum scores for all five categories;
- booleans, non-numeric values, `NaN`, and both infinities;
- empty, malformed, and unknown category values;
- deterministic output, input non-mutation, independent nested collections,
  and strict JSON serialization;
- stable public imports from `backend.app.matchmaking`; and
- compatibility with the Task 11.1 foundation plus regression coverage for
  existing matchmaking, Rashi, and Kundali behavior.

This documentation milestone defines the source of truth only. It does not add
runtime code or tests and does not mark Task 11.5 implementation complete.

## Deterministic and Compatibility Principles

- Inputs and nested collections are copied rather than mutated or shared.
- Person order is preserved without gender-based assumptions.
- Derived astrology fields remain optional and are never calculated here.
- Nakshatra pair context uses zero-based indexes and circular distance only;
  it does not assign compatibility meaning.
- Varna Koota uses one-based Rashi indexes and requires explicit scoring
  direction; it does not infer gender or final compatibility.
- Vashya Koota will use supplied sidereal Moon longitudes, explicit bride and
  groom roles, split-sign boundaries, and the directional matrix specified in
  Task 11.5; its runtime implementation remains pending.
- Non-finite values are converted to JSON-safe values.
- Stable schemas and public imports must remain backward-compatible as the
  sprint grows.
- Calculation completion is explicit; empty results remain `not_evaluated`.

## Provisional Task Sequence

- 11.1 Matchmaking foundation architecture. **Complete.**
- 11.2 Matchmaking input validation. **Complete.**
- 11.3 Nakshatra compatibility foundations. **Complete.**
- 11.4 Varna Koota. **Complete.**
- 11.5 Vashya Koota. **Specification complete; runtime pending.**
- 11.6 Tara Koota.
- 11.7 Yoni Koota.
- 11.8 Graha Maitri Koota.
- 11.9 Gana Koota.
- 11.10 Bhakoot Koota.
- 11.11 Nadi Koota.
- 11.12 Ashtakoota aggregation.
- 11.13 Manglik compatibility foundation.
- 11.14 Matchmaking summary composer.
- 11.15 Serialization and compatibility hardening.

This sequence is provisional and may be adjusted after repository and source
inspection for each task. Tasks 11.2 onward are not implemented by Task 11.1.

## Non-Goals

- Full matchmaking or Ashtakoota calculation.
- Compatibility labels or final marriage judgments.
- Interpretive prose, marriage advice, remedies, or AI output.
- Changes to completed calculation, prediction, API, report, or UI modules.
