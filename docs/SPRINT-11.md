# Sprint 11 - Matchmaking Foundation

Sprint 11 establishes deterministic compatibility infrastructure that consumes
reusable birth and Kundali data. It keeps matchmaking calculations separate
from astrology calculation engines and from future API, reporting, and UI
layers.

## Sprint Status

Status: **In Progress (Tasks 11.1-11.9 Complete)**

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

Status: **Complete**

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

### Completion and Verification

Task 11.6 implements the specified inclusive count, modulo-9 classification,
directional results, and final score as an opt-in matchmaking module. It reuses
the Task 11.3 Nakshatra pair context and distance helper, leaves Tasks 11.1
through 11.5 unchanged, and does not calculate later Kootas or aggregate an
Ashtakoota score.

Verification for Task 11.6:

- Focused Tara Koota tests: 79 passed.
- Matchmaking foundation, validation, Nakshatra, Varna, Vashya, and Tara
  tests: 262 passed.
- Core and matchmaking Nakshatra regression tests: 41 passed.
- Full suite: 1230 passed, 13 skipped, and 20 subtests passed.

## Task 11.7 - Yoni Koota

Status: **Complete**

### Purpose, Domain, and Scope

Yoni Koota represents instinctive, physical, and intimate compatibility in
the North Indian Ashtakoota system. Its maximum score is `4.0` points and its
stable machine-readable compatibility domain is `intimacy`.

Task 11.7 runtime implementation must provide:

- reusable Yoni classification from one supplied sidereal Moon Nakshatra;
- deterministic scoring of the two classified Yonis using the single
  BhaktiAstro convention defined below;
- the complete canonical Nakshatra mapping and `14 x 14` scoring matrix; and
- a structured, JSON-safe result consistent with the Varna, Vashya, and Tara
  Koota architecture.

The caller must explicitly identify which ordered person is the bride and
which is the groom. The calculator must not infer gender or marriage role from
`person_a`, `person_b`, a Nakshatra's Yoni sex, names, identifiers, or input
order. It must not derive a missing Moon longitude or Nakshatra from birth
details, mutate supplied data, calculate another Koota, aggregate Ashtakoota,
or produce a compatibility judgement, prediction, advice, or remedy.

### BhaktiAstro Convention Decision

Task 11.7 uses one explicitly selected North Indian Ashtakoota convention:

- the 27 canonical Moon Nakshatras map to the 14 Yoni animals and Yoni-sex
  classifications in the table below;
- Abhijit is not inserted into the project's 27-Nakshatra sequence;
- scoring is the symmetric animal-pair table below, with scores `4`, `3`, `2`,
  `1`, and `0` for same, friendly, neutral, enemy, and sworn-enemy pairs;
- Yoni sex is classification metadata attached to the Nakshatra, not the
  person's sex or gender and not an additional scoring axis; and
- any same-animal pair receives `4.0`, regardless of whether its two
  Nakshatras have opposite or equal Yoni-sex classifications.

This is the authoritative BhaktiAstro project decision. Runtime code must not
blend in regional Yoni Porutham rules, a 28-star Abhijit table, alternative
male/female assignments, directional sex-polarity adjustments, special
same-Nakshatra deductions, or cancellation rules from another tradition.

### Primary Inputs and Reused Nakshatra Logic

The astrological input for each person is the already supplied sidereal Moon
Nakshatra. Nakshatra Pada is not used by Yoni Koota and must not change the
classification or score.

Runtime implementation must reuse:

- `backend.app.constants.nakshatra.NAKSHATRA_LIST` and `NAKSHATRA_COUNT`;
- `normalize_matchmaking_nakshatra` for canonical names, zero-based indexes,
  supported person structures, Pada preservation, and validation issues; and
- `build_nakshatra_pair_context` for ordered identities, same-Nakshatra and
  same-Pada state, role-independent pair normalization, and deterministic
  issue ordering.

It must not duplicate the canonical Nakshatra list, Moon-longitude-to-
Nakshatra lookup, name normalization, index validation, pair extraction, or
issue mapping. Ashwini remains zero-based index `0`, Revati remains index `26`,
and a direct index input is never one-based.

### Canonical Nakshatra-to-Yoni Mapping

The stable animal identifiers are `horse`, `elephant`, `sheep`, `serpent`,
`dog`, `cat`, `rat`, `cow`, `buffalo`, `tiger`, `deer`, `monkey`, `mongoose`,
and `lion`. The stable Yoni-sex identifiers are `male` and `female`.

| Index | Canonical Nakshatra | Yoni identifier | Traditional name | Yoni sex |
|---:|---|---|---|---|
| 0 | Ashwini | `horse` | Ashwa | `male` |
| 1 | Bharani | `elephant` | Gaja | `male` |
| 2 | Krittika | `sheep` | Mesha | `female` |
| 3 | Rohini | `serpent` | Sarpa | `male` |
| 4 | Mrigashira | `serpent` | Sarpa | `female` |
| 5 | Ardra | `dog` | Shwana | `female` |
| 6 | Punarvasu | `cat` | Marjara | `female` |
| 7 | Pushya | `sheep` | Mesha | `male` |
| 8 | Ashlesha | `cat` | Marjara | `male` |
| 9 | Magha | `rat` | Mushika | `male` |
| 10 | Purva Phalguni | `rat` | Mushika | `female` |
| 11 | Uttara Phalguni | `cow` | Gau | `male` |
| 12 | Hasta | `buffalo` | Mahisha | `female` |
| 13 | Chitra | `tiger` | Vyaghra | `female` |
| 14 | Swati | `buffalo` | Mahisha | `male` |
| 15 | Vishakha | `tiger` | Vyaghra | `male` |
| 16 | Anuradha | `deer` | Mriga | `female` |
| 17 | Jyeshtha | `deer` | Mriga | `male` |
| 18 | Moola | `dog` | Shwana | `male` |
| 19 | Purva Ashadha | `monkey` | Vanara | `male` |
| 20 | Uttara Ashadha | `mongoose` | Nakula | `male` |
| 21 | Shravana | `monkey` | Vanara | `female` |
| 22 | Dhanishtha | `lion` | Simha | `female` |
| 23 | Shatabhisha | `horse` | Ashwa | `female` |
| 24 | Purva Bhadrapada | `lion` | Simha | `male` |
| 25 | Uttara Bhadrapada | `cow` | Gau | `female` |
| 26 | Revati | `elephant` | Gaja | `female` |

`sheep` is the canonical English identifier for Mesha in Task 11.7; `goat`
and `ram` are not accepted aliases. `deer` is the canonical identifier for
Mriga; `hare` and `rabbit` are not accepted aliases. Mongoose has only Uttara
Ashadha in the 27-Nakshatra foundation because its traditional counterpart,
Abhijit, belongs to the excluded 28-star variant. Runtime code must not invent
a second mongoose Nakshatra or change Uttara Ashadha's Yoni sex.

### Symmetric Scoring and Relationship Classes

Yoni Koota preserves explicit bride and groom roles in its result, but the
BhaktiAstro scoring convention is symmetric. Rows below represent the bride's
Yoni and columns represent the groom's Yoni; the matrix equals its transpose,
so reversing the roles must preserve the relationship and awarded score.

| Relationship identifier | Meaning | Score |
|---|---|---:|
| `same` | Same Yoni animal | 4.0 |
| `friendly` | Friendly Yoni animals | 3.0 |
| `neutral` | Neutral Yoni animals | 2.0 |
| `enemy` | Enemy Yoni animals | 1.0 |
| `sworn_enemy` | Sworn-enemy / bitter-enemy Yoni animals | 0.0 |

The relationship identifier is determined only by the exact matrix score.
Runtime code must centralize the following table once and must not infer
relationships from zoology, predator/prey assumptions, Yoni sex, or other
Kootas.

| Bride \\ Groom | `horse` | `elephant` | `sheep` | `serpent` | `dog` | `cat` | `rat` | `cow` | `buffalo` | `tiger` | `deer` | `monkey` | `mongoose` | `lion` |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `horse` | 4 | 2 | 2 | 3 | 2 | 2 | 2 | 1 | 0 | 1 | 3 | 3 | 2 | 1 |
| `elephant` | 2 | 4 | 3 | 3 | 2 | 2 | 2 | 2 | 3 | 1 | 2 | 3 | 2 | 0 |
| `sheep` | 2 | 3 | 4 | 2 | 1 | 2 | 1 | 3 | 3 | 1 | 2 | 0 | 3 | 1 |
| `serpent` | 3 | 3 | 2 | 4 | 2 | 1 | 1 | 1 | 1 | 2 | 2 | 2 | 0 | 2 |
| `dog` | 2 | 2 | 1 | 2 | 4 | 2 | 1 | 2 | 2 | 1 | 0 | 2 | 1 | 1 |
| `cat` | 2 | 2 | 2 | 1 | 2 | 4 | 0 | 2 | 2 | 1 | 3 | 3 | 2 | 1 |
| `rat` | 2 | 2 | 1 | 1 | 1 | 0 | 4 | 2 | 2 | 2 | 2 | 2 | 1 | 2 |
| `cow` | 1 | 2 | 3 | 1 | 2 | 2 | 2 | 4 | 3 | 0 | 3 | 2 | 2 | 1 |
| `buffalo` | 0 | 3 | 3 | 1 | 2 | 2 | 2 | 3 | 4 | 1 | 2 | 2 | 2 | 1 |
| `tiger` | 1 | 1 | 1 | 2 | 1 | 1 | 2 | 0 | 1 | 4 | 1 | 1 | 2 | 1 |
| `deer` | 3 | 2 | 2 | 2 | 0 | 3 | 2 | 3 | 2 | 1 | 4 | 2 | 2 | 1 |
| `monkey` | 3 | 3 | 0 | 2 | 2 | 3 | 2 | 2 | 2 | 1 | 2 | 4 | 3 | 2 |
| `mongoose` | 2 | 2 | 3 | 0 | 1 | 2 | 1 | 2 | 2 | 2 | 2 | 3 | 4 | 2 |
| `lion` | 1 | 0 | 1 | 2 | 1 | 1 | 2 | 1 | 1 | 1 | 1 | 2 | 2 | 4 |

The seven `sworn_enemy` pairs are exactly:

- `horse` / `buffalo`;
- `elephant` / `lion`;
- `sheep` / `monkey`;
- `serpent` / `mongoose`;
- `dog` / `deer`;
- `cat` / `rat`; and
- `cow` / `tiger`.

Both orders of each pair score `0.0`. All other non-diagonal relationships,
including every friendly, neutral, and enemy pair, are defined exclusively by
the complete matrix and must not be filled by a fallback default.

### Same-Yoni and Same-Nakshatra Behavior

- Every diagonal matrix cell is relationship `same` and awards the maximum
  `4.0` points.
- Two different Nakshatras assigned to the same animal also receive `4.0`.
- The Yoni-sex combination does not raise or lower the matrix score.
- The same Nakshatra has the same animal and therefore receives `4.0`, whether
  the supplied Padas are equal, different, or absent.
- Same-Nakshatra and same-Pada flags from the shared pair context remain audit
  metadata only; there is no special override or cancellation.
- Uttara Ashadha paired with itself is same mongoose and receives `4.0`, even
  though both classifications necessarily expose Yoni sex `male`.

### Boundary and Normalization Rules

- Canonical names and zero-based indexes `0..26` must normalize through the
  existing matchmaking Nakshatra helper and produce identical classifications.
- Index `0` is Ashwini/horse; index `26` is Revati/elephant. Indexes must not
  wrap: `-1` and `27` are invalid.
- Booleans are not numeric Nakshatra indexes.
- Pada, when supplied, must follow the shared integer range `1..4`; it is
  preserved but ignored by Yoni classification and scoring.
- Yoni Koota does not accept a raw Moon longitude as its direct input. When an
  upstream astrology component derives the sidereal Moon Nakshatra from
  longitude, that component owns `[0, 360)` normalization and all Nakshatra
  cusp behavior. Task 11.7 must consume the resulting canonical Nakshatra and
  must not duplicate or reinterpret longitude boundaries.
- No Abhijit insertion, one-based conversion, modulo wrapping, case-folded
  enum guessing, animal aliasing, or fuzzy boundary is permitted.

### Validation and Invalid Input Behavior

Runtime validation must follow the shared Nakshatra and matchmaking
conventions:

- accept canonical Nakshatra names, zero-based indexes `0..26`, and supported
  person or pair structures handled by the existing normalization helpers;
- reject missing Nakshatra, unknown names, wrong types, booleans, negative
  indexes, and indexes greater than `26` with existing stable,
  localization-ready issue codes;
- reject missing, unknown, duplicate, or identical bride/groom role
  assignments with stable role issue codes;
- preserve deterministic bride-before-groom issue ordering;
- return status `invalid` and score `None` whenever either identity or role
  assignment is invalid; and
- perform no partial classification result or fallback score for an invalid
  pair.

The low-level animal score lookup must raise `TypeError` when either category
is not a string and `ValueError` when either string is empty, malformed, an
alias, or not one of the 14 canonical identifiers. It must not silently guess,
case-fold, or default an unknown enum/category. The high-level calculator must
catch expected input validation failures and return the safe structured
invalid result; unexpected programming errors must not be swallowed.

### Public Result Contract

The runtime task must expose stable helpers from
`backend.app.matchmaking.__init__` for:

1. classifying one normalized matchmaking Nakshatra identity or supported
   Nakshatra input into its canonical animal and Yoni-sex identity;
2. looking up the symmetric relationship and score for two canonical Yoni
   animal identifiers; and
3. calculating the complete Yoni Koota result from an ordered matchmaking pair
   plus explicit `bride_role` and `groom_role`.

The structured result must expose at least:

- Koota identifier `yoni`;
- compatibility domain `intimacy`;
- status;
- awarded score and maximum score `4.0`;
- unchanged `person_a` and `person_b` Nakshatra identities;
- explicit bride and groom role mapping;
- bride Yoni identity with canonical Nakshatra name, zero-based index, animal
  identifier, traditional animal name, and Yoni sex;
- groom Yoni identity with the same fields;
- relationship identifier and deterministic matrix row/column audit factors;
- same-Nakshatra, same-Pada, and same-Yoni flags;
- stable errors and warnings; and
- references and deterministic schema metadata consistent with existing
  matchmaking Koota results.

Each returned object and nested collection must be newly allocated, must not
share mutable defaults, and must be treated as immutable after construction.
The calculator must not mutate caller inputs. Output ordering and identifiers
must be stable and strictly JSON-safe. Role reversal must swap the bride/groom
identity fields but preserve the symmetric relationship and score.

### Required Runtime Tests

Task 11.7 runtime implementation is not complete until focused tests cover:

- all 27 Nakshatras by canonical name and zero-based index, including every
  documented animal and Yoni-sex classification;
- all 14 canonical animal identifiers and both Yoni-sex identifiers;
- every one of the `14 x 14` scoring matrix cells, including matrix symmetry;
- every relationship class: `same`, `friendly`, `neutral`, `enemy`, and
  `sworn_enemy`;
- both orders of all seven sworn-enemy pairs;
- representative friendly, neutral, and enemy pairs in both role orders;
- same-Yoni pairs, including every diagonal animal and different-Nakshatra
  male/female counterparts, all scoring `4.0`;
- same Nakshatra with same Pada, different Pada, and no Pada, all scoring
  `4.0`, including Uttara Ashadha/mongoose;
- explicit bride/groom role reversal while preserving `person_a` and
  `person_b` order and the symmetric score;
- index boundaries `0` and `26`, invalid `-1` and `27`, booleans, missing
  values, wrong types, malformed names, and unsupported aliases;
- invalid animal lookup values, including non-strings, empty strings,
  case variants, and unknown identifiers;
- no score dependence on Pada or Yoni sex and no Abhijit/28-star insertion;
- deterministic issue ordering, output equality, input non-mutation,
  independent nested collections, and strict JSON serialization;
- stable public exports from `backend.app.matchmaking`; and
- regression compatibility with Task 11.3 Nakshatra context and every
  completed matchmaking module.

### Convention Verification

The 27-star animal and Yoni-sex assignments, the seven sworn-enemy pairs, and
the selected scoring table are documented by the following North Indian
Ashtakoota references:

- [Yoni Koota - Saravali](https://saravali.github.io/astrology/koota_yoni.html)
- [Horoscope Matching, Yoni Koota table](https://www.futuresamachar.com/download/horoscope-matching-325.pdf)
- [Comparison of Panchangas](https://www.ghvisweswara.com/wp-content/uploads/2021/11/Comparison_of_Panchangas.pdf)

Where those sources discuss a 28-star form or other traditions use different
sex assignments or scoring modifiers, the explicit BhaktiAstro decisions and
complete tables in this section are authoritative.

### Completion and Verification

Task 11.7 implements the specified 27-Nakshatra classification, Yoni-sex
metadata, strict category relationship lookup, complete symmetric scoring
matrix, and structured Koota result as an opt-in matchmaking module. It reuses
the Task 11.3 Nakshatra normalization and pair context, leaves Tasks 11.1
through 11.6 unchanged, and does not calculate later Kootas or aggregate an
Ashtakoota score.

Verification for Task 11.7:

- Focused Yoni Koota tests: 288 passed.
- Matchmaking foundation, validation, Nakshatra, Varna, Vashya, Tara, and Yoni
  tests: 550 passed.
- Core and matchmaking Nakshatra regression tests: 41 passed.
- Full suite: 1518 passed, 13 skipped, and 20 subtests passed.

## Task 11.8 - Graha Maitri Koota

Status: **Specification Complete; Runtime Not Implemented**

### Purpose, Domain, and Scope

Graha Maitri Koota, also called Rasyadhipati Maitri, represents mental,
intellectual, and emotional affinity through the natural relationship between
the lords of the bride's and groom's sidereal Moon Rashis. Its maximum score
is `5.0` points and its stable machine-readable compatibility domain is
`mental_compatibility`.

Task 11.8 runtime implementation must provide:

- reusable Moon-Rashi and Rashi-lord classification from one supplied
  sidereal Moon longitude;
- both directional natural relationships between the two Moon-sign lords;
- deterministic combined scoring under the single BhaktiAstro convention
  defined below; and
- a structured, JSON-safe result consistent with the completed matchmaking
  Koota architecture.

The calculator must not calculate birth-chart planetary positions, use a
geographic longitude as a Moon longitude, infer bride/groom roles, mutate
supplied data, calculate another Koota, aggregate Ashtakoota, or produce a
compatibility judgement, prediction, advice, or remedy.

### BhaktiAstro Convention Decisions

Task 11.8 uses one explicitly selected North Indian Ashtakoota convention:

- only the **natural/permanent relationship** (`Naisargika Maitri`) between
  the two classical Moon-Rashi lords is used;
- the relationship is evaluated in both directions because natural planetary
  friendship is not universally reciprocal;
- the two directional statuses are combined using the exact score table and
  complete `7 x 7` matrix below;
- equal lords always receive the maximum `5.0` points as a special case;
- the final score is symmetric even when the two directional natural
  relationships differ; and
- only Sun, Moon, Mars, Mercury, Jupiter, Venus, and Saturn can occur because
  the canonical twelve Rashis have no Rahu or Ketu lordship.

Temporary (`Tatkalika`) friendship is not used. Compound or five-fold
friendship (`Panchadha Maitri`) is not used. Runtime code must not inspect the
current houses, conjunctions, relative planetary positions, Lagna, Navamsha,
transits, Dashas, planetary strength, dignity, or functional benefic/malefic
status. It must not add Lagna/Navamsha score overrides, Bhakoot cancellation,
Maha-Nakshatra exceptions, or regional variants.

These choices are authoritative BhaktiAstro project decisions. They prevent a
fixed Moon-sign-lord Koota from silently changing with chart placements or
from blending incompatible relationship systems.

### Required Inputs and Reused Moon-Rashi Logic

The only astrological input for each person is that person's finite sidereal
Moon longitude in degrees. The high-level calculator must receive the bride
and groom values through explicitly named inputs; it must not infer roles from
`person_a`, `person_b`, a name, identifier, or call order. The existing
`MatchmakingPerson.longitude` field is a geographic birth longitude and must
never be treated as the Moon longitude.

Runtime implementation must reuse:

- `backend.app.kundali.rashi.normalize_longitude` for normalization into
  `[0, 360)`;
- `backend.app.kundali.rashi.get_rashi` for the canonical one-based Rashi,
  names, lord metadata, and degree within the Rashi;
- `backend.app.constants.rashi.RASHI_LIST`, `RASHI_COUNT`, and existing Rashi
  boundaries;
- `backend.app.kundali.graha_lordship.get_rashi_lord` or
  `get_rashi_lord_by_index` for lord resolution; and
- `backend.app.kundali.graha_relationship.NATURAL_RELATIONSHIPS` and
  `get_natural_relationship` for directional natural friendship.

It must not duplicate longitude normalization, Rashi calculation, the Rashi
list, Rashi lordship, or the natural planetary relationship table.

### Moon Rashi Derivation and Boundaries

For each valid input:

1. Normalize the supplied sidereal Moon longitude with the existing Rashi
   engine into `[0, 360)`.
2. Derive the one-based Rashi index and degree within the Rashi using
   `get_rashi`.
3. Resolve the Rashi's canonical lord through the existing lordship helper.
4. Normalize the emitted lord identifier to the existing lowercase project
   keys: `sun`, `moon`, `mars`, `mercury`, `jupiter`, `venus`, or `saturn`.

All Rashi cusps follow the existing half-open intervals: the lower boundary is
included and the upper boundary is excluded. Therefore `0°` is Mesha,
`29.999999°` remains Mesha at existing precision, `30°` is Vrishabha,
`359.999999°` remains Meena, and `360°` normalizes to `0°`/Mesha. Finite
negative and greater-than-`360°` values must produce the same identity as
their normalized equivalents. Runtime code must not introduce an epsilon,
fuzzy cusp, independent rounding rule, or a second longitude normalizer.

### Canonical Rashi-to-Lord Mapping

This table documents the required result of the reused Rashi constants and
lordship helper. Runtime code must not maintain a second independent mapping.

| Index | English Rashi | Sanskrit Rashi | Canonical lord |
|---:|---|---|---|
| 1 | Aries | Mesha | `mars` |
| 2 | Taurus | Vrishabha | `venus` |
| 3 | Gemini | Mithuna | `mercury` |
| 4 | Cancer | Karka | `moon` |
| 5 | Leo | Simha | `sun` |
| 6 | Virgo | Kanya | `mercury` |
| 7 | Libra | Tula | `venus` |
| 8 | Scorpio | Vrishchika | `mars` |
| 9 | Sagittarius | Dhanu | `jupiter` |
| 10 | Capricorn | Makara | `saturn` |
| 11 | Aquarius | Kumbha | `saturn` |
| 12 | Pisces | Meena | `jupiter` |

Sun and Moon each rule one Rashi. Mars, Mercury, Jupiter, Venus, and Saturn
each rule two. Rahu, Ketu, Uranus, Neptune, Pluto, alternative co-lords, and
modern rulerships are outside Task 11.8.

### Canonical Natural/Permanent Relationships

The relationship from a row lord toward another lord is directional. The
following tables are the required existing `NATURAL_RELATIONSHIPS` values:

| Lord | Natural friends | Natural neutrals | Natural enemies |
|---|---|---|---|
| `sun` | `moon`, `mars`, `jupiter` | `mercury` | `venus`, `saturn` |
| `moon` | `sun`, `mercury` | `mars`, `jupiter`, `venus`, `saturn` | none |
| `mars` | `sun`, `moon`, `jupiter` | `venus`, `saturn` | `mercury` |
| `mercury` | `sun`, `venus` | `mars`, `jupiter`, `saturn` | `moon` |
| `jupiter` | `sun`, `moon`, `mars` | `saturn` | `mercury`, `venus` |
| `venus` | `mercury`, `saturn` | `mars`, `jupiter` | `sun`, `moon` |
| `saturn` | `mercury`, `venus` | `jupiter` | `sun`, `moon`, `mars` |

A lord is intentionally absent from its own friend/neutral/enemy groups.
Equal lords use the explicit same-lord rule before calling the natural
relationship helper; an `unsupported` self-relationship must never lower or
invalidate a same-lord match.

The complete directional status table is:

| From \\ Toward | `sun` | `moon` | `mars` | `mercury` | `jupiter` | `venus` | `saturn` |
|---|---|---|---|---|---|---|---|
| `sun` | same | friend | friend | neutral | friend | enemy | enemy |
| `moon` | friend | same | neutral | friend | neutral | neutral | neutral |
| `mars` | friend | friend | same | enemy | friend | neutral | neutral |
| `mercury` | friend | enemy | neutral | same | neutral | friend | neutral |
| `jupiter` | friend | friend | friend | enemy | same | enemy | neutral |
| `venus` | enemy | enemy | neutral | friend | neutral | same | friend |
| `saturn` | enemy | enemy | enemy | friend | neutral | friend | same |

### Combined Relationship and Score Rules

For different lords, obtain both directional natural statuses and combine
them without bride/groom weighting or averaging:

| Combined identifier | Directional status pair, in either order | Score |
|---|---|---:|
| `mutual_friend` | friend + friend | 5.0 |
| `friend_neutral` | friend + neutral | 4.0 |
| `mutual_neutral` | neutral + neutral | 3.0 |
| `friend_enemy` | friend + enemy | 1.0 |
| `neutral_enemy` | neutral + enemy | 0.5 |
| `mutual_enemy` | enemy + enemy | 0.0 |

Equal lords use combined identifier `same_lord` and score `5.0`. No other
score is valid. In particular, the selected convention gives `1.0` for a
friend/enemy pair and `0.5` for a neutral/enemy pair. Traditions that assign
`2.0` and `1.0` to those combinations are not used by Task 11.8.

### Complete Bride-Lord / Groom-Lord Scoring Matrix

Rows represent the bride's Moon-sign lord and columns represent the groom's
Moon-sign lord. Although the row-to-column and column-to-row natural statuses
may differ, the combined score matrix is symmetric and equals its transpose.

| Bride \\ Groom | `sun` | `moon` | `mars` | `mercury` | `jupiter` | `venus` | `saturn` |
|---|---:|---:|---:|---:|---:|---:|---:|
| `sun` | 5.0 | 5.0 | 5.0 | 4.0 | 5.0 | 0.0 | 0.0 |
| `moon` | 5.0 | 5.0 | 4.0 | 1.0 | 4.0 | 0.5 | 0.5 |
| `mars` | 5.0 | 4.0 | 5.0 | 0.5 | 5.0 | 3.0 | 0.5 |
| `mercury` | 4.0 | 1.0 | 0.5 | 5.0 | 0.5 | 5.0 | 4.0 |
| `jupiter` | 5.0 | 4.0 | 5.0 | 0.5 | 5.0 | 0.5 | 3.0 |
| `venus` | 0.0 | 0.5 | 3.0 | 5.0 | 0.5 | 5.0 | 5.0 |
| `saturn` | 0.0 | 0.5 | 0.5 | 4.0 | 3.0 | 5.0 | 5.0 |

The matrix is normative as an audit table. Runtime code should derive it from
the existing directional natural-relationship table plus the centralized
combined-score rules instead of hard-coding a second source of planetary
friendship. It must not fill unknown pairs with a default score.

### Directionality, Symmetry, and Same-Lord Behavior

- The bride-to-groom status is the bride lord's natural view of the groom
  lord.
- The groom-to-bride status is the groom lord's natural view of the bride
  lord.
- Role reversal swaps those two statuses and the row/column audit fields but
  preserves the combined identifier and score.
- Same-lord pairs always return `same_lord` and `5.0`, including different
  Rashis with a shared lord.
- The different-Rashi same-lord pairs are Mesha/Vrishchika, Vrishabha/Tula,
  Mithuna/Kanya, Dhanu/Meena, and Makara/Kumbha, in either role order.
- Same Rashi also necessarily has the same lord and receives `5.0`; degree
  within the Rashi does not change the score.
- One-sided friendship is not promoted to mutual friendship: friend/neutral
  scores `4.0`, friend/enemy scores `1.0`, and neutral/enemy scores `0.5`.

### Validation and Invalid Input Behavior

Low-level Moon-Rashi classification must preserve the existing Rashi utility
contract:

- raise `TypeError` when a longitude is a boolean or is not a real number;
- raise `ValueError` when a longitude is `NaN`, positive infinity, or negative
  infinity; and
- accept all other finite numeric values and normalize them through the
  existing utility.

The low-level lord relationship lookup must:

- accept only the seven canonical lowercase lord identifiers;
- raise `TypeError` when either lord is not a string;
- raise `ValueError` for empty, malformed, aliased, unsupported, or non-
  canonical identifiers, including Rahu and Ketu; and
- never case-fold, guess, or default a public enum/category input.

The high-level calculator must follow the safe-result convention used by the
completed Kootas: catch expected input validation failures, return status
`invalid` with score `None`, emit stable localization-ready issue codes in
deterministic bride-before-groom order, and perform no partial score.
Unexpected programming errors must not be swallowed.

### Public Result Contract

The runtime task must expose stable helpers from
`backend.app.matchmaking.__init__` for:

1. classifying one finite sidereal Moon longitude into its canonical Moon
   Rashi and lord identity;
2. looking up the two directional natural relationships, combined identifier,
   and score for two canonical lord identifiers; and
3. calculating the complete Graha Maitri Koota result from explicitly named
   bride and groom sidereal Moon longitudes.

The structured result must expose at least:

- Koota identifier `graha_maitri`;
- compatibility domain `mental_compatibility`;
- status;
- awarded score and maximum score `5.0`;
- bride Moon-Rashi identity with normalized longitude, canonical Rashi names,
  one-based Rashi index, degree within the Rashi, and canonical lord;
- groom Moon-Rashi identity with the same fields;
- explicit bride-row/groom-column audit metadata;
- bride-to-groom and groom-to-bride natural relationship statuses;
- combined relationship identifier and same-lord flag;
- deterministic factors sufficient to audit the score lookup;
- stable errors and warnings; and
- references and schema metadata consistent with existing matchmaking Koota
  results.

Each returned object and nested collection must be newly allocated, must not
share mutable defaults, and must be treated as immutable after construction.
The calculator must not mutate caller inputs. Output ordering and identifiers
must be stable and strictly JSON-safe. No interpretation paragraph, advice,
remedy, API response, report formatting, other Koota, or Ashtakoota
aggregation belongs in Task 11.8.

### Required Runtime Tests

Task 11.8 runtime implementation is not complete until focused tests cover:

- representative Moon longitudes for all twelve Rashis and every documented
  Rashi-to-lord assignment;
- all twelve exact Rashi lower cusps and values immediately below the next
  cusp at the existing six-decimal precision;
- `0°`, `360°`, finite negative, and greater-than-`360°` normalization;
- every natural friend, neutral, and enemy entry for all seven classical
  lords;
- every one of the `7 x 7` scoring matrix cells and matrix symmetry;
- all combined identifiers and scores: `same_lord`/`5.0`,
  `mutual_friend`/`5.0`, `friend_neutral`/`4.0`,
  `mutual_neutral`/`3.0`, `friend_enemy`/`1.0`,
  `neutral_enemy`/`0.5`, and `mutual_enemy`/`0.0`;
- same-lord maximum scores for all seven lords, including all five
  different-Rashi shared-lord pairs in both role orders;
- asymmetric natural relationships such as Sun/Mercury, Moon/Mercury, and
  Moon/Venus, verifying that role reversal swaps directional statuses but not
  the combined score;
- proof that degree within one Rashi does not change its lord or score;
- booleans, non-numeric values, missing values, `NaN`, and both infinities;
- empty, malformed, case-variant, aliased, Rahu, Ketu, and unknown lord
  identifiers;
- deterministic bride-before-groom issue ordering and no partial scoring;
- no dependence on temporary positions, Panchadha Maitri, Lagna, Navamsha,
  Pada, Nakshatra, Bhava, dignity, strength, or another Koota;
- deterministic output equality, input non-mutation, independent nested
  collections, and strict JSON serialization;
- stable public exports from `backend.app.matchmaking`; and
- regression compatibility with the existing Rashi, Graha lordship, Graha
  relationship, Kundali, and completed matchmaking foundations.

### Convention Verification

The selected natural-relationship method, `5.0`/`4.0`/`3.0`/`1.0`/`0.5`/`0.0`
combination rules, and complete seven-lord matrix are documented by:

- [Horoscope Matching - Natural Graha Maitri Guna Milaan Table](https://www.futuresamachar.com/download/horoscope-matching-325.pdf)
- [Ashtakoota Gun Milan - Graha Maitri scoring rules](https://www.rashisetu.com/blog/ashtakoota-gun-milan-explained)
- [Comparison of Panchangas - Graha Maitra Koota](https://www.ghvisweswara.com/wp-content/uploads/2021/11/Comparison_of_Panchangas.pdf)

Where other sources assign different intermediate points or add chart-based
exceptions, the explicit BhaktiAstro decisions and tables in this section are
authoritative.

### Completion and Verification

Task 11.8 is runtime-complete. The implementation:

- reuses the canonical longitude normalizer, Rashi lookup, Rashi lordship, and
  natural/permanent Graha relationship helpers;
- exposes reusable Moon-Rashi lord classification, strict two-lord
  relationship lookup, the derived symmetric audit matrix, and the keyword-only
  bride/groom Koota calculator from `backend.app.matchmaking`;
- implements only the documented permanent relationship convention and does
  not introduce temporary friendship, Panchadha Maitri, or chart-dependent
  overrides; and
- returns deterministic JSON-safe results with independent nested collections,
  stable validation issues, and complete score-audit fields.

Verification completed for this task:

- focused Graha Maitri tests: `167 passed`;
- complete matchmaking regression layer: `717 passed`;
- Rashi, lordship, relationship, Kundali, and Kundali API regressions:
  `124 passed`; and
- full regression suite: `1685 passed`, `13 skipped`, and `20 subtests passed`.

The skips are the repository's pre-existing manual-reference validation
placeholders. Task 11.8 does not enable or alter them. Work stops here before
Task 11.9.

## Task 11.9 - Gana Koota

Status: **Complete**

### Purpose, Domain, and Scope

Gana Koota represents compatibility of temperament, disposition, and
day-to-day behavioural nature through the Gana assigned to each person's
sidereal Moon Nakshatra. Its maximum score is `6.0` points and its stable
machine-readable compatibility domain is `temperament`.

Task 11.9 runtime implementation must provide:

- reusable Gana classification from one supplied sidereal Moon Nakshatra;
- deterministic directional scoring for explicitly assigned bride and groom
  roles under the single BhaktiAstro convention below;
- the complete canonical 27-Nakshatra mapping and `3 x 3` scoring matrix; and
- a structured, immutable-after-construction, JSON-safe result consistent
  with the completed matchmaking Koota architecture.

The calculator must not infer gender or marriage roles, calculate a Moon
position from birth details, mutate supplied data, calculate another Koota,
apply a cancellation rule, aggregate Ashtakoota, or produce a compatibility
judgement, prediction, advice, or remedy.

### BhaktiAstro Convention Decisions

Task 11.9 uses the directional North Indian Ashtakoota Gana convention
documented by the Saravali/Maitreya table:

- the canonical 27 Moon Nakshatras are divided into exactly three groups of
  nine: `deva`, `manushya`, and `rakshasa`;
- Abhijit is not inserted into the project's 27-Nakshatra sequence;
- rows represent the explicitly assigned bride's Gana and columns represent
  the explicitly assigned groom's Gana;
- the exact directional matrix in this section is authoritative;
- every same-Gana pair receives the maximum `6.0` points; and
- Pada, Nakshatra lord, Rashi, Lagna, Navamsha, Graha Maitri, and the other
  Kootas do not modify the base Gana score.

The selected matrix is intentionally directional. BhaktiAstro does not use a
symmetrized table that assigns a single score to an unordered mixed-Gana pair,
does not average the two role orders, and does not transpose a source table
silently. Gana Dosha cancellation based on Nakshatra distance, Rashi lords,
Graha Maitri, Vashya, Tara, Yoni, Nadi, Navamsha, or another regional rule is
outside Task 11.9. These choices are explicit BhaktiAstro project decisions
and prevent incompatible traditions from being combined.

### Required Inputs and Reused Nakshatra Architecture

The astrological input for each person is that person's already supplied
sidereal Moon Nakshatra. The high-level calculator must consume an ordered
matchmaking pair plus explicit `bride_role` and `groom_role`, following the
same role contract used by Tara and Yoni Koota. It must never infer bride or
groom from `person_a`, `person_b`, names, identifiers, Gana, or call order.

Runtime implementation must reuse:

- `backend.app.constants.nakshatra.NAKSHATRA_LIST`, `NAKSHATRA_COUNT`, and
  `NAKSHATRA_SPAN_DEGREES`;
- `normalize_matchmaking_nakshatra` for canonical names, zero-based indexes,
  supported person structures, Pada preservation, and validation issues; and
- `build_nakshatra_pair_context` for ordered identities, same-Nakshatra and
  same-Pada state, pair normalization, and deterministic issue ordering.

It must not duplicate the canonical Nakshatra list, name normalization, index
validation, pair extraction, issue mapping, or Moon-longitude-to-Nakshatra
lookup. Ashwini remains zero-based index `0` and Revati remains index `26`.
Direct index input is never one-based and is never wrapped modulo `27`.

### Moon-Longitude Derivation and Nakshatra Boundaries

Gana Koota does not accept a raw Moon longitude as its direct high-level
input. When upstream data starts with a finite sidereal Moon longitude, the
Nakshatra must be derived by the existing
`backend.app.astrology.nakshatra.get_nakshatra` helper before it is supplied
to the matchmaking layer. Gana runtime code must not copy or reinterpret that
derivation.

The reused core helper owns all longitude behavior:

- longitude is normalized into `[0, 360)` at the existing six-decimal
  `BOUNDARY_PRECISION`;
- `0°` and normalized equivalents such as `360°` derive Ashwini/index `0`;
- finite negative and greater-than-`360°` values derive the same Nakshatra as
  their normalized equivalents;
- each core Nakshatra interval is lower-inclusive and upper-exclusive, so a
  value immediately below a cusp remains in the earlier Nakshatra and the
  exact canonical cusp starts the next Nakshatra; and
- a boolean or non-real longitude raises `TypeError`, while `NaN` and either
  infinity raise `ValueError` under the core helper contract.

Runtime tests must use the existing core constants and lookup output for cusp
expectations; they must not calculate an independent approximate boundary or
introduce an epsilon. Once a canonical name or index reaches Gana Koota, the
shared matchmaking normalizer—not longitude arithmetic—owns normalization.

### Canonical Nakshatra-to-Gana Mapping

The stable category identifiers are exactly `deva`, `manushya`, and
`rakshasa`. The mapping follows the canonical zero-based Nakshatra order:

| Index | Canonical Nakshatra | Gana identifier |
|---:|---|---|
| 0 | Ashwini | `deva` |
| 1 | Bharani | `manushya` |
| 2 | Krittika | `rakshasa` |
| 3 | Rohini | `manushya` |
| 4 | Mrigashira | `deva` |
| 5 | Ardra | `manushya` |
| 6 | Punarvasu | `deva` |
| 7 | Pushya | `deva` |
| 8 | Ashlesha | `rakshasa` |
| 9 | Magha | `rakshasa` |
| 10 | Purva Phalguni | `manushya` |
| 11 | Uttara Phalguni | `manushya` |
| 12 | Hasta | `deva` |
| 13 | Chitra | `rakshasa` |
| 14 | Swati | `deva` |
| 15 | Vishakha | `rakshasa` |
| 16 | Anuradha | `deva` |
| 17 | Jyeshtha | `rakshasa` |
| 18 | Moola | `rakshasa` |
| 19 | Purva Ashadha | `manushya` |
| 20 | Uttara Ashadha | `manushya` |
| 21 | Shravana | `deva` |
| 22 | Dhanishtha | `rakshasa` |
| 23 | Shatabhisha | `rakshasa` |
| 24 | Purva Bhadrapada | `manushya` |
| 25 | Uttara Bhadrapada | `manushya` |
| 26 | Revati | `deva` |

The mapping is exhaustive and contains exactly nine Nakshatras in each Gana:

- `deva`: Ashwini, Mrigashira, Punarvasu, Pushya, Hasta, Swati, Anuradha,
  Shravana, and Revati;
- `manushya`: Bharani, Rohini, Ardra, Purva Phalguni, Uttara Phalguni, Purva
  Ashadha, Uttara Ashadha, Purva Bhadrapada, and Uttara Bhadrapada; and
- `rakshasa`: Krittika, Ashlesha, Magha, Chitra, Vishakha, Jyeshtha, Moola,
  Dhanishtha, and Shatabhisha.

Runtime code must centralize this mapping once by canonical zero-based index.
It must verify complete `0..26` coverage and must not maintain separate lists
that can disagree.

### Directional Bride-Row / Groom-Column Scoring

Rows are the bride's Gana and columns are the groom's Gana. The following
matrix is the complete normative lookup table:

| Bride \\ Groom | `deva` | `manushya` | `rakshasa` |
|---|---:|---:|---:|
| `deva` | 6.0 | 6.0 | 0.0 |
| `manushya` | 5.0 | 6.0 | 0.0 |
| `rakshasa` | 1.0 | 0.0 | 6.0 |

No score outside `{0.0, 1.0, 5.0, 6.0}` is valid. Runtime code must preserve
the row and column roles, perform one exact lookup, and must not average,
round, rank, infer, or fill an unknown pair with a default.

The directional asymmetries are normative:

- bride `deva` / groom `manushya` scores `6.0`, while bride `manushya` /
  groom `deva` scores `5.0`; and
- bride `deva` / groom `rakshasa` scores `0.0`, while bride `rakshasa` /
  groom `deva` scores `1.0`.

Both bride `manushya` / groom `rakshasa` and bride `rakshasa` / groom
`manushya` score `0.0`. Role reversal must transpose the audit lookup and may
change the score only for the two documented asymmetric category pairs.

### Same-Gana, Mixed-Gana, and Same-Nakshatra Behavior

- Every diagonal matrix cell is `same_gana` and awards `6.0` points.
- Same-Gana maximum scoring applies to `deva`, `manushya`, and `rakshasa`
  without an exception based on the particular Nakshatras or Padas.
- Mixed Ganas use only the exact directional matrix; no mixed pair is promoted
  to same-Gana and no outside cancellation modifies its base score.
- The same Nakshatra necessarily has the same Gana and therefore receives
  `6.0`, whether the supplied Padas are equal, different, or absent.
- Same-Nakshatra and same-Pada flags from the shared pair context remain audit
  metadata only and do not trigger a special override.
- Two different Nakshatras in the same Gana also receive `6.0`.

The stable relationship identifier must be `same_gana` for diagonal cells and
`mixed_gana` for off-diagonal cells. The exact bride and groom Gana fields
and matrix audit factor remain the source of the particular mixed score.

### Validation and Invalid Input Behavior

Runtime validation must follow the shared Nakshatra and matchmaking
conventions:

- accept canonical Nakshatra names, zero-based indexes `0..26`, and supported
  person or pair structures handled by the existing normalization helpers;
- accept all canonical English, Hindi, and Sanskrit names already supported
  by `normalize_matchmaking_nakshatra`, with its existing whitespace and case
  normalization behavior;
- reject missing Nakshatra, unknown names, wrong types, booleans, negative
  indexes, and indexes greater than `26` with existing stable,
  localization-ready issue codes;
- preserve valid Pada `1..4` as identity metadata but ignore it for Gana
  classification and scoring;
- reject invalid Pada values through the existing shared issue contract;
- reject missing, unknown, duplicate, or identical bride/groom role
  assignments with stable role issue codes;
- preserve deterministic bride-before-groom issue ordering;
- return status `invalid` and score `None` whenever either identity or role
  assignment is invalid; and
- perform no partial classification or fallback scoring for an invalid pair.

The low-level Gana score lookup must accept only the three exact canonical
lowercase category identifiers. It must raise `TypeError` when either category
is not a string and `ValueError` for empty, malformed, aliased, case-variant,
or unknown identifiers. It must not case-fold, guess, coerce, or default a
public enum/category input. The high-level calculator catches expected input
validation failures and returns a safe structured invalid result; unexpected
programming errors must not be swallowed.

### Public Immutable Result Contract

The runtime task must expose stable helpers from
`backend.app.matchmaking.__init__` for:

1. classifying one normalized matchmaking Nakshatra identity or supported
   Nakshatra input into its canonical Gana identity;
2. looking up the directional score for two exact bride and groom Gana
   identifiers; and
3. calculating the complete Gana Koota result from an ordered matchmaking pair
   plus explicit `bride_role` and `groom_role`.

The structured result must expose at least:

- Koota identifier `gana`;
- compatibility domain `temperament`;
- status;
- awarded score and maximum score `6.0`;
- unchanged `person_a` and `person_b` Nakshatra identities;
- explicit bride and groom role mapping;
- bride Gana identity with canonical Nakshatra name, zero-based index, optional
  Pada, source person identifier, and canonical Gana identifier;
- groom Gana identity with the same fields;
- relationship identifier, explicit bride-row/groom-column direction, and
  deterministic matrix audit factors;
- same-Nakshatra, same-Pada, and same-Gana flags;
- stable errors and warnings; and
- references and deterministic schema metadata consistent with existing
  matchmaking Koota results.

Every returned result, identity, issue, metadata mapping, factor list,
reference list, error list, and warning list must be newly allocated. Returned
objects must share no mutable defaults or nested collections and must be
treated as immutable after construction. The calculator must not mutate caller
inputs. Repeated equivalent calls must compare equal before caller mutation,
and mutating one returned result must not affect a later or earlier result.

All output must be strictly JSON-safe: dictionary keys and machine identifiers
are strings; scores are finite numbers or `None` for invalid results; no
`NaN`, infinity, tuple-only encoding, set, enum instance, dataclass instance,
or other non-JSON value may escape. Output ordering, issue ordering, factor
ordering, and identifiers must be deterministic. No interpretation paragraph,
compatibility label, advice, remedy, API response, report formatting, other
Koota, or Ashtakoota total belongs in Task 11.9.

### Required Runtime Tests

Task 11.9 runtime implementation is not complete until focused tests cover:

- all 27 canonical Nakshatras by name and zero-based index, including every
  documented mapping and exactly nine members per Gana;
- all three canonical Gana identifiers;
- every one of the `3 x 3` bride-row/groom-column matrix cells;
- same-Gana maximum scores for all three diagonal categories and for
  representative different-Nakshatra pairs in each Gana;
- both role orders of the asymmetric Deva/Manushya and Deva/Rakshasa pairs,
  proving that role reversal transposes the lookup;
- both role orders of the zero-score Manushya/Rakshasa pair;
- same Nakshatra with equal Pada, different Pada, and absent Pada, all scoring
  `6.0`;
- all 27 core Moon-longitude Nakshatra lower cusps and values immediately below
  the next cusp at the existing six-decimal precision, classified through the
  reused core lookup rather than duplicated arithmetic;
- `0°`, `360°`, finite negative, and greater-than-`360°` core longitude
  normalization, plus core rejection of booleans, non-real values, `NaN`, and
  both infinities;
- matchmaking index boundaries `0` and `26`, invalid `-1` and `27`, missing
  values, wrong types, malformed names, and unsupported aliases;
- invalid Gana lookup values, including non-strings, empty strings, case
  variants, aliases, and unknown identifiers;
- missing, unknown, duplicate, and identical bride/groom roles;
- deterministic bride-before-groom issue ordering and no partial score;
- proof that Pada, Nakshatra lord, Rashi, and every other Koota do not alter
  the base matrix score;
- deterministic output equality, input non-mutation, independent nested
  collections, and strict `json.dumps(..., allow_nan=False)` serialization;
- stable public exports from `backend.app.matchmaking`; and
- regression compatibility with the core Nakshatra lookup, Task 11.3 pair
  context, and every completed matchmaking module.

### Convention Verification

The 27-star classification, selected directional matrix, and documented
convention differences are covered by:

- [Gana Koota - Saravali/Maitreya table](https://saravali.github.io/astrology/koota_gana.html)
- [Gana Koota in Kundli Matching - directional bride/groom table](https://www.astroyogi.com/blog/gana-koota-in-kundli-matching.aspx)
- [Horoscope Matching - Gana classification and scoring discussion](https://www.futuresamachar.com/download/horoscope-matching-325.pdf)
- [Comparison of Panchangas - Gana Koota convention comparison](https://www.ghvisweswara.com/wp-content/uploads/2021/11/Comparison_of_Panchangas.pdf)

Some sources transpose bride and groom, use a symmetric `5` or `1` for both
orders of a mixed pair, or apply cancellation and exception rules. BhaktiAstro
selects the exact Saravali/Maitreya bride-row/groom-column matrix above and
does not merge those alternatives into Task 11.9.

### Completion and Verification

Task 11.9 is runtime-complete. The implementation:

- reuses canonical Nakshatra constants, shared Nakshatra normalization, and
  ordered pair-context construction without accepting or recalculating Moon
  longitude;
- exposes reusable Gana classification, strict directional category lookup,
  and the ordered-pair calculator with explicit bride and groom roles;
- implements the complete 27-Nakshatra mapping and exact directional
  bride-row/groom-column `3 x 3` matrix; and
- returns deterministic JSON-safe results with independent nested collections,
  stable validation issues, and matrix audit factors.

Verification completed for this task:

- focused Gana Koota tests: `145 passed`;
- complete matchmaking regression layer: `862 passed`;
- core and matchmaking Nakshatra regressions: `41 passed`; and
- full regression suite: `1830 passed`, `13 skipped`, and `20 subtests passed`.

The skips are the repository's pre-existing manual-reference validation
placeholders. Task 11.9 does not enable or alter them. Work stops here before
Task 11.10.

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
- Tara Koota reuses zero-based Nakshatra pair context, inclusive circular
  counts, the modulo-9 cycle, and explicit bride/groom roles specified in Task
  11.6; it does not infer roles or derive missing Nakshatras.
- Yoni Koota reuses zero-based Nakshatra identities, the canonical 27-star
  mapping, explicit bride/groom roles, and the symmetric matrix specified in
  Task 11.7; Yoni sex is metadata and does not alter the score.
- Graha Maitri Koota reuses Moon-Rashi derivation, Rashi lordship, and
  natural planetary relationships; only permanent friendship and the
  symmetric score rules specified in Task 11.8 apply.
- Gana Koota reuses the canonical 27-Nakshatra identity and ordered pair
  context, requires explicit bride/groom roles, and uses only the directional
  matrix specified in Task 11.9.
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
- 11.6 Tara Koota. **Complete.**
- 11.7 Yoni Koota. **Complete.**
- 11.8 Graha Maitri Koota. **Complete.**
- 11.9 Gana Koota. **Complete.**
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
