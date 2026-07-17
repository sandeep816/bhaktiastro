# Sprint 11 - Matchmaking Foundation

Sprint 11 establishes deterministic compatibility infrastructure that consumes
reusable birth and Kundali data. It keeps matchmaking calculations separate
from astrology calculation engines and from future API, reporting, and UI
layers.

## Sprint Status

Status: **In Progress (Task 11.5 Complete)**

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

Status: **Complete**

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

Task 11.5 implements the specified classification, strict category lookup, and
directional Koota result as an opt-in matchmaking module. It leaves Tasks 11.1
through 11.4 unchanged and does not calculate later Kootas or aggregate an
Ashtakoota score.

Verification for Task 11.5:

- Focused Vashya Koota tests: 74 passed.
- Matchmaking foundation, validation, Nakshatra, Varna, and Vashya tests:
  183 passed.
- Rashi and relevant Kundali regression tests: 64 passed.
- Full suite: 1151 passed, 13 skipped, and 20 subtests passed.

## Task 11.6 - Tara Koota

Status: **Specification Complete; Runtime Not Implemented**

### Purpose and Scope

Tara Koota, also called Dina Koota, represents destiny, wellbeing, fortune,
and birth-star harmony in the standard North Indian Ashtakoota convention. Its
maximum score is `3.0` points and its stable machine-readable compatibility
domain is `destiny`.

Task 11.6 runtime implementation must provide:

- deterministic Tara classification from two supplied sidereal Moon
  Nakshatras;
- inclusive circular Nakshatra counting in both directions;
- the canonical modulo-9 Tara classification defined below;
- independent bride-to-groom and groom-to-bride directional scores; and
- a structured, JSON-safe Tara Koota result consistent with the existing
  matchmaking Koota architecture.

The caller must explicitly identify which ordered person is the bride and
which is the groom. The calculator must not infer gender or marriage role from
`person_a`, `person_b`, names, identifiers, or input order. It must not derive
a missing Moon longitude or Nakshatra from birth details.

### Primary Inputs and Reused Nakshatra Logic

The astrological input for each person is the already supplied sidereal Moon
Nakshatra. Nakshatra Pada is not used by Tara Koota and must not change the
score.

Runtime implementation must reuse:

- `backend.app.constants.nakshatra.NAKSHATRA_LIST` and `NAKSHATRA_COUNT`;
- `normalize_matchmaking_nakshatra` for canonical names, zero-based indexes,
  person identifiers, and validation issues;
- `build_nakshatra_pair_context` for ordered identities, circular distances,
  same-Nakshatra state, and deterministic issue ordering; and
- `calculate_nakshatra_distance` for zero-based circular distance.

It must not duplicate the canonical Nakshatra list, name normalization, index
validation, pair extraction, circular-distance calculation, or issue mapping.
Ashwini remains index `0` and Revati remains index `26`.

### Inclusive Circular Counting

Tara counting includes both the starting Nakshatra and the destination
Nakshatra. For valid zero-based indexes:

```text
inclusive_count(from, to)
    = calculate_nakshatra_distance(from, to) + 1
```

The inclusive count is always an integer from `1` through `27`:

- the same Nakshatra has distance `0` and inclusive count `1`;
- adjacent Nakshatras have inclusive count `2`;
- wrap-around from Revati (`26`) to Ashwini (`0`) has inclusive count `2`;
- Ashwini (`0`) to Revati (`26`) has inclusive count `27`; and
- no valid calculation may produce count `0` or a count above `27`.

### Modulo-9 Tara Calculation

Each inclusive count maps to one Tara number from `1` through `9`:

```text
tara_number = ((inclusive_count - 1) mod 9) + 1
```

This is equivalent to dividing the inclusive count by `9`, using remainders
`1..8` directly, and treating remainder `0` as Tara number `9`. Runtime code
must use one centralized calculation and must not maintain a 27-pair lookup
table.

### Nine Canonical Tara Classifications

The stable machine-readable identifiers, cycle positions, and scoring natures
are:

| Tara number | Inclusive counts | Identifier | Display name | Nature |
|---:|---|---|---|---|
| 1 | 1, 10, 19 | `janma` | Janma | unfavorable |
| 2 | 2, 11, 20 | `sampat` | Sampat | favorable |
| 3 | 3, 12, 21 | `vipat` | Vipat | unfavorable |
| 4 | 4, 13, 22 | `kshema` | Kshema | favorable |
| 5 | 5, 14, 23 | `pratyari` | Pratyari | unfavorable |
| 6 | 6, 15, 24 | `sadhaka` | Sadhaka | favorable |
| 7 | 7, 16, 25 | `vadha` | Vadha | unfavorable |
| 8 | 8, 17, 26 | `mitra` | Mitra | favorable |
| 9 | 9, 18, 27 | `ati_mitra` | Ati Mitra / Parama Mitra | favorable |

The favorable Tara numbers are exactly `{2, 4, 6, 8, 9}`. The unfavorable
Tara numbers are exactly `{1, 3, 5, 7}`. These sets are the BhaktiAstro
canonical Task 11.6 scoring convention and must not be inferred from odd/even
parity, because Tara number `9` is favorable.

### Directional Calculation

Tara Koota requires both directions and preserves explicit role assignment:

1. **Bride to groom:** count inclusively forward from the bride's Nakshatra to
   the groom's Nakshatra.
2. **Groom to bride:** count inclusively forward from the groom's Nakshatra to
   the bride's Nakshatra.

Each directional result must expose:

- source role and destination role;
- source and destination canonical Nakshatra identities and zero-based
  indexes;
- zero-based circular distance;
- inclusive count;
- Tara number;
- canonical Tara identifier and display name;
- favorable boolean; and
- awarded directional score.

The existing `person_a` and `person_b` order must remain unchanged even when
the caller assigns `person_b` as bride and `person_a` as groom. Reversing the
explicit roles swaps the directional calculations; no role is inferred.

### Directional and Final Score

Each direction contributes independently:

```text
directional_score = 1.5 if tara_number in {2, 4, 6, 8, 9} else 0.0
final_score = bride_to_groom_score + groom_to_bride_score
```

Therefore the only valid final scores are:

- `3.0` when both directions are favorable;
- `1.5` when exactly one direction is favorable; and
- `0.0` when neither direction is favorable.

The final score must not be averaged, rounded to an integer, weighted by Pada,
or changed by another Koota. Task 11.6 does not implement Tara Dosha
cancellation, remedies, exceptions based on Rashi/Nadi/Bhakoot, or final
compatibility judgement.

### Same-Nakshatra Handling

For the BhaktiAstro base North Indian convention, equal Nakshatra indexes do
not receive a special scoring override:

- each circular distance is `0`;
- each inclusive count is `1`;
- each direction is Tara number `1`, identifier `janma`;
- each direction is unfavorable and awards `0.0`; and
- the final Tara Koota score is `0.0` out of `3.0`.

Same or different Pada does not change this result. Alternative traditions
that treat same-Nakshatra Janma Tara as favorable or apply cancellation rules
are explicitly outside Task 11.6 and must not be added silently.

### Boundary Examples

These examples use zero-based Nakshatra indexes and explicit bride-to-groom
direction:

| Bride index | Groom index | Distance | Inclusive count | Tara | Directional score |
|---:|---:|---:|---:|---|---:|
| 0 | 0 | 0 | 1 | `janma` | 0.0 |
| 0 | 1 | 1 | 2 | `sampat` | 1.5 |
| 26 | 0 | 1 | 2 | `sampat` | 1.5 |
| 0 | 8 | 8 | 9 | `ati_mitra` | 1.5 |
| 0 | 9 | 9 | 10 | `janma` | 0.0 |
| 0 | 26 | 26 | 27 | `ati_mitra` | 1.5 |

The `9`, `18`, and `27` inclusive-count boundaries must all map to Tara number
`9`, never `0`. Counts `10` and `19` restart the cycle at `janma`.

### Validation Rules

Runtime validation must follow the existing Nakshatra and matchmaking
conventions:

- accept canonical Nakshatra names, zero-based indexes `0..26`, and supported
  person or pair structures already handled by the shared Nakshatra helpers;
- reject booleans as numeric indexes;
- report missing Nakshatra, unknown name, invalid type, and indexes outside
  `0..26` with the existing stable localization-ready issue codes;
- ignore Pada for scoring while preserving valid supplied identity metadata;
- reject missing, unknown, duplicate, or identical bride/groom role
  assignments with stable direction/role issue codes;
- preserve deterministic bride-before-groom issue ordering;
- return status `invalid` and score `None` whenever either Nakshatra or the
  explicit role assignment is invalid; and
- perform no partial score when the input is invalid.

Low-level helpers must not silently clamp, wrap, case-guess unsupported enum
identifiers, or convert one-based Nakshatra indexes. Unexpected programming
errors must not be swallowed.

### Public Result Contract

The runtime task must expose stable helpers from
`backend.app.matchmaking.__init__` for:

1. converting a valid circular distance or inclusive count into the canonical
   Tara classification;
2. calculating one directional Tara result from valid canonical Nakshatra
   identities or indexes; and
3. calculating a complete Tara Koota result from an ordered matchmaking pair
   plus explicit `bride_role` and `groom_role`.

The structured Koota result must expose at least:

- Koota identifier `tara`;
- compatibility domain `destiny`;
- status;
- awarded score and maximum score `3.0`;
- unchanged `person_a` and `person_b` Nakshatra identities;
- explicit bride and groom role mapping;
- bride-to-groom and groom-to-bride directional results;
- same-Nakshatra and same-Pada flags from the reused pair context;
- deterministic factors sufficient to audit both counts and their sum;
- stable errors and warnings;
- references and deterministic schema metadata consistent with existing
  matchmaking results.

Each returned object and nested collection must be newly allocated, must not
share mutable defaults, and must be treated as immutable after construction.
The calculator must not mutate caller inputs. Output ordering and identifiers
must be stable and strictly JSON-safe. No prediction, interpretation, advice,
remedy, API response, report, UI formatting, other Koota score, or Ashtakoota
aggregation belongs in Task 11.6.

### Required Runtime Tests

Task 11.6 implementation is not complete until focused tests cover:

- all 27 inclusive counts and their repeating modulo-9 classifications;
- all nine canonical Tara identifiers, names, numbers, and favorable flags;
- favorable set `{2, 4, 6, 8, 9}` and unfavorable set `{1, 3, 5, 7}`;
- same, adjacent, first, last, and circular wrap-around Nakshatra indexes;
- modulo boundaries at counts `9`, `10`, `18`, `19`, and `27`;
- bride-to-groom and groom-to-bride direction independently;
- final scores `0.0`, `1.5`, and `3.0` with known index pairs;
- explicit role reversal while preserving `person_a` and `person_b` order;
- same Nakshatra with same Pada, different Pada, and no Pada, all scoring
  `0.0` under the documented base convention;
- canonical names and zero-based indexes producing equivalent results;
- missing, unknown, wrong-type, boolean, negative, and index `27` inputs;
- missing, unknown, duplicate, and identical bride/groom roles;
- deterministic issue ordering, output equality, input non-mutation,
  independent nested collections, and strict JSON serialization;
- stable public exports from `backend.app.matchmaking`; and
- regression compatibility with Task 11.3 Nakshatra context and all completed
  matchmaking modules.

### Convention Verification

The inclusive count, modulo-9 cycle, favorable positions, bidirectional
scoring, and `3.0`/`1.5`/`0.0` totals follow the North Indian Ashtakoota
convention documented by:

- [Comparison of Panchangas](https://www.ghvisweswara.com/wp-content/uploads/2021/11/Comparison_of_Panchangas.pdf)
- [Tara Koota: Health and Fortune by Nakshatra](https://astromedha.in/insights/vedic/tara-koota)

Where sources or regional traditions differ on Janma Tara or same-Nakshatra
exceptions, the explicit BhaktiAstro rule in this section is authoritative.

### Documentation Completion Rules

This documentation milestone defines the Task 11.6 source of truth only. It
does not add runtime code or tests and does not mark Task 11.6 implementation
complete.

When the runtime task is completed, update only the relevant sections of:

- `docs/SPRINT-11.md` to mark Task 11.6 complete and record focused,
  matchmaking regression, Nakshatra regression, and full-suite results;
- `docs/MASTER.md` to add Task 11.6 to completed Sprint 11 tasks; and
- `CHANGELOG.md` to record the runtime capability.

Do not mark Task 11.7 or Sprint 11 complete during Task 11.6.

## Deterministic and Compatibility Principles

- Inputs and nested collections are copied rather than mutated or shared.
- Person order is preserved without gender-based assumptions.
- Derived astrology fields remain optional and are never calculated here.
- Nakshatra pair context uses zero-based indexes and circular distance only;
  it does not assign compatibility meaning.
- Varna Koota uses one-based Rashi indexes and requires explicit scoring
  direction; it does not infer gender or final compatibility.
- Vashya Koota uses supplied sidereal Moon longitudes, explicit bride and groom
  roles, split-sign boundaries, and the directional matrix specified in Task
  11.5; it does not infer roles or calculate Moon positions.
- Tara Koota will reuse zero-based Nakshatra pair context, inclusive circular
  counts, the modulo-9 cycle, and explicit bride/groom roles specified in Task
  11.6; its runtime implementation remains pending.
- Non-finite values are converted to JSON-safe values.
- Stable schemas and public imports must remain backward-compatible as the
  sprint grows.
- Calculation completion is explicit; empty results remain `not_evaluated`.

## Provisional Task Sequence

- 11.1 Matchmaking foundation architecture. **Complete.**
- 11.2 Matchmaking input validation. **Complete.**
- 11.3 Nakshatra compatibility foundations. **Complete.**
- 11.4 Varna Koota. **Complete.**
- 11.5 Vashya Koota. **Complete.**
- 11.6 Tara Koota. **Specification complete; runtime pending.**
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
