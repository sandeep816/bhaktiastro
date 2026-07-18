# Sprint 11 - Matchmaking Foundation

Sprint 11 establishes deterministic compatibility infrastructure that consumes
reusable birth and Kundali data. It keeps matchmaking calculations separate
from astrology calculation engines and from future API, reporting, and UI
layers.

## Sprint Status

Status: **Complete (Tasks 11.1-11.15 Complete)**

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

## Task 11.10 - Bhakoot Koota

Status: **Complete**

### Purpose, Domain, and Scope

Bhakoot Koota, also called Rashi Koota, represents compatibility of shared
family welfare, domestic continuity, and prosperity through the circular
relationship between the two sidereal Moon Rashis. Its maximum score is `7.0`
points and its stable machine-readable compatibility domain is
`family_welfare`.

Task 11.10 runtime implementation must provide:

- reusable full-Rashi classification from each supplied sidereal Moon
  longitude;
- inclusive circular Rashi distances from bride to groom and from groom to
  bride;
- deterministic identification of the `2/12`, `5/9`, and `6/8` Bhakoot Dosha
  pairs under the single North Indian convention in this section; and
- a structured, immutable-after-construction, JSON-safe result consistent
  with the completed matchmaking Koota architecture.

The calculator must not infer a Moon position from birth details, infer or
swap bride and groom roles, mutate caller data, calculate another Koota,
aggregate Ashtakoota, or produce a compatibility judgement, prediction,
advice, remedy, or cancellation analysis.

### BhaktiAstro Convention Decisions

Task 11.10 uses the North Indian Ashtakoota Bhakoot convention documented by
the Saravali/Maitreya Rashi Koota rule:

- only the full sidereal Moon Rashi of each person is used;
- circular positions are counted inclusively, with the source Rashi as count
  `1`;
- `2/12`, `5/9`, and `6/8` are the only dosha position pairs and score `0.0`;
- `1/1`, `3/11`, `4/10`, and `7/7` are all compatible and score `7.0`;
- the two directional counts are retained for audit, but dosha classification
  and scoring are symmetric under role reversal; and
- no intermediate, partial, averaged, severity-weighted, or direction-specific
  score is permitted.

BhaktiAstro explicitly excludes Rashi-lord friendship, same-lord and
friendly-lord exceptions, odd/even-sign exceptions, auspicious or inauspicious
Shadashtaka subtypes, Nakshatra or Pada exceptions, Navamsha, Graha aspects,
house strength, aggregate-score thresholds, and every other Bhakoot Dosha
cancellation or Parihara rule from Task 11.10. A base dosha pair always scores
`0.0`, even where another tradition would cancel it. A compatible pair always
scores `7.0`. These exclusions are explicit project decisions so the base
North Indian scoring rule is not mixed with optional traditions.

There are no split signs in Bhakoot Koota. Unlike Vashya classification,
degree within a Rashi never changes the Bhakoot identity or score. Rashi lord,
element, modality, Nakshatra, and Pada may be present in reused upstream data
but must not modify the calculation.

### Required Inputs and Reused Rashi Architecture

The public high-level calculator must use explicit keyword-only
`bride_moon_longitude` and `groom_moon_longitude` inputs. Each is the person's
sidereal Moon longitude in degrees. Bride and groom roles are fixed by those
keyword names; the calculator must never infer roles from names, identifiers,
Rashi, argument order outside the keyword contract, or another field.

Runtime implementation must reuse:

- `backend.app.constants.rashi.RASHI_LIST`, `RASHI_COUNT`,
  `RASHI_SPAN_DEGREES`, and `FULL_CIRCLE_DEGREES`;
- `backend.app.kundali.rashi.normalize_longitude`; and
- `backend.app.kundali.rashi.get_rashi` and its canonical one-based Rashi
  indexes and identity fields.

It must not duplicate longitude validation, normalization, Rashi boundaries,
name data, index derivation, or degree-within-Rashi arithmetic. Mesha remains
one-based Rashi index `1` and Meena remains index `12`. Any reusable low-level
distance or relationship helper must consume exact one-based indexes `1..12`;
it must never accept zero-based indexes or wrap an invalid index modulo `12`.

### Moon-Rashi Derivation, Normalization, and Boundaries

For each person, runtime code must first call the canonical longitude
normalizer and then reuse the canonical Rashi lookup. The inherited behavior
is normative:

- finite longitudes are normalized into `[0, 360)` at the existing
  six-decimal `DEGREE_PRECISION`;
- `0°`, `360°`, `-360°`, and other normalized equivalents map consistently to
  Mesha/index `1`;
- finite negative and greater-than-`360°` values map to the same Rashi as
  their normalized equivalents;
- all twelve `30°` Rashi intervals are lower-inclusive and upper-exclusive
  after canonical rounding: exact cusps `0°`, `30°`, ..., `330°` start their
  respective Rashis, while the representable six-decimal value immediately
  below the next cusp remains in the preceding Rashi; and
- booleans and non-real values raise `TypeError`, while `NaN` and either
  infinity raise `ValueError` under the core helper contract.

No Bhakoot-specific epsilon, rounding, cusp correction, alternate ayanamsa,
or sign calculation is allowed. The normalized longitude and complete reused
Rashi identity must be retained in the result for audit. Only the one-based
Rashi index participates in distance and scoring.

### Inclusive Circular Distance Calculation

Both directional counts include the starting Rashi. For exact one-based
indexes `from_index` and `to_index`, the sole normative formula is:

```text
inclusive_distance(from_index, to_index) =
    ((to_index - from_index) mod 12) + 1
```

Therefore each distance is an integer in `1..12`. Runtime must calculate:

```text
bride_to_groom_distance = inclusive_distance(bride_index, groom_index)
groom_to_bride_distance = inclusive_distance(groom_index, bride_index)
```

The counting is not exclusive: adjacent Rashis produce `2` in the forward
direction, not `1`. The possible ordered and canonical unordered position
pairs are exhaustive:

| Groom offset from bride | Bride to groom | Groom to bride | Canonical pair | Classification | Score |
|---:|---:|---:|---|---|---:|
| 0 | 1 | 1 | `1/1` | compatible | 7.0 |
| 1 | 2 | 12 | `2/12` | dosha | 0.0 |
| 2 | 3 | 11 | `3/11` | compatible | 7.0 |
| 3 | 4 | 10 | `4/10` | compatible | 7.0 |
| 4 | 5 | 9 | `5/9` | dosha | 0.0 |
| 5 | 6 | 8 | `6/8` | dosha | 0.0 |
| 6 | 7 | 7 | `7/7` | compatible | 7.0 |
| 7 | 8 | 6 | `6/8` | dosha | 0.0 |
| 8 | 9 | 5 | `5/9` | dosha | 0.0 |
| 9 | 10 | 4 | `4/10` | compatible | 7.0 |
| 10 | 11 | 3 | `3/11` | compatible | 7.0 |
| 11 | 12 | 2 | `2/12` | dosha | 0.0 |

For different Rashis the two directional distances sum to `14`. Same Rashi is
the sole exception and produces `1/1`, not `1/13`, `12/12`, or `0/0`.

### Complete Symmetric Rashi Scoring Table

Rows represent the bride's Moon Rashi and columns represent the groom's Moon
Rashi for audit consistency. The table is symmetric; transposing bride and
groom swaps the two directional counts but never changes the canonical pair,
dosha status, or score.

| Bride \\ Groom | Mesha | Vrishabha | Mithuna | Karka | Simha | Kanya | Tula | Vrishchika | Dhanu | Makara | Kumbha | Meena |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Mesha | 7.0 | 0.0 | 7.0 | 7.0 | 0.0 | 0.0 | 7.0 | 0.0 | 0.0 | 7.0 | 7.0 | 0.0 |
| Vrishabha | 0.0 | 7.0 | 0.0 | 7.0 | 7.0 | 0.0 | 0.0 | 7.0 | 0.0 | 0.0 | 7.0 | 7.0 |
| Mithuna | 7.0 | 0.0 | 7.0 | 0.0 | 7.0 | 7.0 | 0.0 | 0.0 | 7.0 | 0.0 | 0.0 | 7.0 |
| Karka | 7.0 | 7.0 | 0.0 | 7.0 | 0.0 | 7.0 | 7.0 | 0.0 | 0.0 | 7.0 | 0.0 | 0.0 |
| Simha | 0.0 | 7.0 | 7.0 | 0.0 | 7.0 | 0.0 | 7.0 | 7.0 | 0.0 | 0.0 | 7.0 | 0.0 |
| Kanya | 0.0 | 0.0 | 7.0 | 7.0 | 0.0 | 7.0 | 0.0 | 7.0 | 7.0 | 0.0 | 0.0 | 7.0 |
| Tula | 7.0 | 0.0 | 0.0 | 7.0 | 7.0 | 0.0 | 7.0 | 0.0 | 7.0 | 7.0 | 0.0 | 0.0 |
| Vrishchika | 0.0 | 7.0 | 0.0 | 0.0 | 7.0 | 7.0 | 0.0 | 7.0 | 0.0 | 7.0 | 7.0 | 0.0 |
| Dhanu | 0.0 | 0.0 | 7.0 | 0.0 | 0.0 | 7.0 | 7.0 | 0.0 | 7.0 | 0.0 | 7.0 | 7.0 |
| Makara | 7.0 | 0.0 | 0.0 | 7.0 | 0.0 | 0.0 | 7.0 | 7.0 | 0.0 | 7.0 | 0.0 | 7.0 |
| Kumbha | 7.0 | 7.0 | 0.0 | 0.0 | 7.0 | 0.0 | 0.0 | 7.0 | 7.0 | 0.0 | 7.0 | 0.0 |
| Meena | 0.0 | 7.0 | 7.0 | 0.0 | 0.0 | 7.0 | 0.0 | 0.0 | 7.0 | 7.0 | 0.0 | 7.0 |

The table, inclusive-distance formula, and canonical-pair table must always
agree. Runtime should derive or verify the full matrix from one centralized
rule rather than maintain competing sources of truth.

### Same-Rashi, Dosha, and Compatible Behavior

- Every same-Rashi pair has directional distances `1` and `1`, canonical pair
  `1/1`, relationship `compatible`, `bhakoot_dosha = false`, and score `7.0`.
- Every `2/12` pair has canonical pair identifier `2_12`, relationship
  `dosha`, `bhakoot_dosha = true`, and score `0.0`.
- Every `5/9` pair has canonical pair identifier `5_9`, relationship `dosha`,
  `bhakoot_dosha = true`, and score `0.0`.
- Every `6/8` pair has canonical pair identifier `6_8`, relationship `dosha`,
  `bhakoot_dosha = true`, and score `0.0`.
- Every `3/11`, `4/10`, and `7/7` pair is compatible, has no dosha, and scores
  `7.0`; their identifiers are `3_11`, `4_10`, and `7_7` respectively.
- The same-Rashi compatible identifier is `1_1`.

No other distance pair exists. Runtime must perform one exact lookup or rule
evaluation and must not guess, coerce, interpolate, or default an unknown
pair.

### Validation and Invalid Input Behavior

Runtime validation must follow existing Rashi and matchmaking conventions:

- the low-level classifier accepts a finite real longitude and delegates all
  validation and normalization to the reused Rashi utilities;
- a boolean or non-real longitude raises `TypeError`; `NaN` and either
  infinity raise `ValueError`;
- a reusable low-level distance or relationship helper accepts only real
  integer one-based Rashi indexes `1..12`, rejects booleans and non-integral
  values with `TypeError`, and rejects values outside `1..12` with
  `ValueError`;
- it must not accept names, aliases, case variants, zero-based indexes, numeric
  strings, or malformed canonical-pair identifiers in place of exact indexes;
- the high-level calculator treats `None` or an empty value as missing and any
  other invalid longitude as invalid, returning stable localization-ready
  issue codes consistent with the direct-longitude Kootas;
- high-level errors are ordered bride before groom, status is `invalid`, score
  is `None`, and dosha/relationship fields that require two valid identities
  are unset whenever either input is invalid; and
- no partial distance, pair classification, fallback score, warning-only
  downgrade, or swallowed unexpected programming error is permitted.

Expected input failures are safe structured high-level results, while the
strict reusable low-level helpers expose the documented `TypeError` and
`ValueError` exceptions to callers.

### Public Immutable Result Contract

The runtime task must expose stable helpers from
`backend.app.matchmaking.__init__` for:

1. classifying one supplied sidereal Moon longitude into its normalized full
   Moon-Rashi identity;
2. calculating inclusive circular distance between two exact one-based Rashi
   indexes;
3. resolving the complete symmetric Bhakoot relationship for exact bride and
   groom Rashi indexes; and
4. calculating the full Bhakoot Koota result from keyword-only
   `bride_moon_longitude` and `groom_moon_longitude` inputs.

The structured result must expose at least:

- Koota identifier `bhakoot`;
- compatibility domain `family_welfare`;
- status, awarded score, and maximum score `7.0`;
- bride and groom Moon-Rashi identities, each containing input-derived
  normalized sidereal longitude, canonical English/Hindi/Sanskrit names,
  one-based Rashi index, and degree within Rashi;
- explicit bride-row/groom-column direction metadata;
- bride-to-groom and groom-to-bride inclusive distances;
- canonical pair identifier and display position pair;
- relationship identifier `compatible` or `dosha`;
- same-Rashi and Bhakoot-Dosha flags;
- deterministic scoring audit factors;
- stable errors and warnings; and
- references and schema metadata consistent with existing matchmaking Koota
  results, including `directional = false`, `symmetric = true`, Rashi count
  `12`, and index base `1`.

Every returned result, identity, relationship, issue, metadata mapping,
direction mapping, factor list, reference list, error list, and warning list
must be newly allocated. Returned objects must share no mutable defaults or
nested collections and must be treated as immutable after construction. The
calculator must not mutate caller inputs. Repeated equivalent calls must
compare equal before caller mutation, and mutating one returned result must not
affect an earlier or later result.

All output must be strictly JSON-safe: dictionary keys and machine identifiers
are strings; valid scores are finite `0.0` or `7.0`; invalid score is `None`;
no `NaN`, infinity, tuple-only encoding, set, enum instance, dataclass
instance, or other non-JSON value may escape. Output ordering, issue ordering,
factor ordering, and identifiers must be deterministic. No compatibility
label, interpretive paragraph, cancellation claim, advice, remedy, API
response, report formatting, other Koota, or Ashtakoota total belongs in Task
11.10.

### Required Runtime Tests

Task 11.10 runtime implementation is not complete until focused tests cover:

- representative Moon longitudes for all twelve Rashis and every canonical
  one-based index and Rashi identity;
- all twelve exact Rashi lower cusps and values immediately below the next
  cusp at existing six-decimal precision;
- `0°`, `360°`, `-360°`, finite negative, and greater-than-`360°`
  normalization;
- every one of the `12 x 12` bride/groom Rashi pairs, asserting all `144`
  directional count pairs, canonical pair identifiers, dosha flags, and
  scores against the complete table;
- all twelve unordered Rashi pairings in each of the `2/12`, `5/9`, and `6/8`
  classes, each in both role orders (`24` ordered matrix cells per class),
  including wraparound pairs;
- all twelve same-Rashi `1/1` cases, each scoring `7.0`;
- every non-dosha distance class: `1/1`, `3/11`, `4/10`, and `7/7`, in every
  applicable Rashi pair and both role orders where distinct;
- symmetry under role reversal: directional counts swap while canonical pair,
  relationship, dosha flag, and score remain unchanged;
- proof that degree within a Rashi and Rashi lord, element, modality,
  Nakshatra, Pada, and every other Koota do not alter the score;
- booleans, non-real values, missing values, empty values, `NaN`, and both
  infinities for each longitude field;
- strict low-level Rashi-index validation for `1`, `12`, invalid `0`, `13`,
  negatives, booleans, floats, strings, names, aliases, and malformed values;
- deterministic bride-before-groom issue ordering and no partial scoring;
- proof that same/friendly Rashi lords and all documented cancellation
  candidates do not override a base dosha score;
- deterministic output equality, input non-mutation, independent nested
  collections, and strict `json.dumps(..., allow_nan=False)` serialization;
- stable public exports from `backend.app.matchmaking`; and
- regression compatibility with canonical Rashi normalization and lookup,
  Rashi constants, Graha lordship, Kundali calculations, and every completed
  matchmaking module.

### Convention Verification

The selected full-Rashi method, inclusive mutual positions, exact dosha pairs,
and binary `7.0`/`0.0` scoring are documented by:

- [Rasi Koota - Saravali/Maitreya rule](https://saravali.github.io/astrology/koota_rasi.html)
- [Horoscope Matching - Bhakoota Milaan table and rules](https://www.futuresamachar.com/download/horoscope-matching-325.pdf)
- [Ashtakoot System of Matching Horoscopes - Bhakoot position pairs](https://www.astrosaxena.com/asmh2)
- [Comparison of Panchangas - Rashi Koota convention differences](https://www.ghvisweswara.com/wp-content/uploads/2021/11/Comparison_of_Panchangas.pdf)

Some sources add directional exceptions, Rashi-lord friendship, same-lord
cancellation, or other Parihara rules. The explicit base scoring rule and
exclusions in this section are authoritative for BhaktiAstro Task 11.10.

### Completion and Verification

Task 11.10 is runtime-complete. The implementation:

- reuses canonical longitude normalization and full Moon-Rashi lookup without
  duplicating validation, boundaries, names, or index derivation;
- exposes reusable Bhakoot Rashi classification, strict inclusive circular
  distance, complete relationship lookup, the derived symmetric `12 x 12`
  matrix, and the keyword-only bride/groom calculator;
- implements only the documented base North Indian `7.0`/`0.0` scoring rule
  and does not apply Rashi-lord friendship, cancellation, Parihara, split-sign,
  or interpretation rules; and
- returns deterministic JSON-safe results with independent nested collections,
  stable validation issues, directional distance metadata, and scoring audit
  factors.

Verification completed for this task:

- focused Bhakoot Koota tests: `241 passed`;
- complete matchmaking regression layer: `1103 passed`;
- Rashi, Graha lordship, Kundali, and Kundali API regressions: `118 passed`;
  and
- full regression suite: `2071 passed`, `13 skipped`, and `20 subtests passed`.

The skips are the repository's pre-existing manual-reference validation
placeholders. Task 11.10 does not enable or alter them. Work stops here before
Task 11.11.

## Task 11.11 - Nadi Koota

Status: **Complete**

### Purpose, Domain, and Scope

Nadi Koota represents the Ashtakoota compatibility domain traditionally
associated with physiological constitution, hereditary factors, and progeny
health through the Nadi assigned to each person's sidereal Moon Nakshatra. Its
maximum score is `8.0` points and its stable machine-readable compatibility
domain is `physiological_compatibility`.

Task 11.11 runtime implementation must provide:

- reusable Nadi classification from one supplied sidereal Moon Nakshatra;
- deterministic symmetric scoring for explicitly assigned bride and groom
  roles under the single North Indian convention in this section;
- the complete canonical 27-Nakshatra mapping and `3 x 3` scoring matrix; and
- a structured, immutable-after-construction, JSON-safe result consistent
  with the completed matchmaking Koota architecture.

The calculator must not infer gender or marriage roles, calculate a Moon
position from birth details, mutate caller data, calculate another Koota,
apply a cancellation or exception, aggregate Ashtakoota, make a medical claim,
or produce a compatibility judgement, prediction, advice, or remedy.

### BhaktiAstro Convention Decisions

Task 11.11 uses the North Indian Ashtakoota Nadi convention documented by the
Saravali/Maitreya Nadi Koota rule and the Future Samachar Nadi Chakra:

- the canonical 27 Moon Nakshatras are divided into exactly three groups of
  nine: `adi`, `madhya`, and `antya`;
- Adi corresponds to the traditional Vata classification, Madhya to Pitta,
  and Antya to Kapha, but the stable scoring identifiers are only `adi`,
  `madhya`, and `antya`;
- Abhijit is not inserted into the project's 27-Nakshatra sequence;
- same-Nadi pairs receive `0.0` and set Nadi Dosha;
- different-Nadi pairs receive the maximum `8.0` and do not set Nadi Dosha;
- the matrix is symmetric, so role reversal never changes classification or
  score; and
- no intermediate, partial, averaged, severity-weighted, or direction-specific
  score is permitted.

The selected mapping and binary scoring matrix are authoritative. BhaktiAstro
does not derive Nadi by repeating a guessed arithmetic pattern, by Pada, by
Rashi, by Gotra, or by an Ayurvedic questionnaire. Runtime code must perform
one exact canonical mapping lookup and one exact matrix lookup.

### Required Inputs and Reused Nakshatra Architecture

The astrological input for each person is that person's already supplied
sidereal Moon Nakshatra. The high-level calculator must consume an ordered
matchmaking pair plus explicit `bride_role` and `groom_role`, following the
same role contract used by Tara, Yoni, and Gana Koota. It must never infer
bride or groom from `person_a`, `person_b`, names, identifiers, Nakshatra,
Nadi, or call order.

Runtime implementation must reuse:

- `backend.app.constants.nakshatra.NAKSHATRA_LIST`, `NAKSHATRA_COUNT`, and
  `NAKSHATRA_SPAN_DEGREES`;
- `normalize_matchmaking_nakshatra` for canonical names, zero-based indexes,
  supported person structures, Pada preservation, and validation issues; and
- `build_nakshatra_pair_context` for ordered identities, same-Nakshatra and
  same-Pada state, pair normalization, and deterministic issue ordering.

It must not duplicate the canonical Nakshatra list, name normalization, index
validation, pair extraction, role validation conventions, issue mapping, or
Moon-longitude-to-Nakshatra lookup. Ashwini remains zero-based index `0` and
Revati remains index `26`. A direct index is never one-based and is never
wrapped modulo `27`.

### Moon-Nakshatra Derivation, Normalization, and Boundaries

Nadi Koota does not accept a raw Moon longitude as its direct high-level
input. When upstream data starts with a sidereal Moon longitude, the
Nakshatra must be derived first by the existing
`backend.app.astrology.nakshatra.get_nakshatra` helper. Nadi runtime code must
not copy, wrap, round, or reinterpret that derivation.

The reused core helper owns all longitude behavior:

- a finite longitude is normalized into `[0, 360)` at the existing
  six-decimal `BOUNDARY_PRECISION` using the existing core lookup span;
- `0°`, `360°`, `-360°`, and normalized equivalents derive Ashwini/index `0`;
- finite negative and greater-than-`360°` values derive the same Nakshatra as
  their normalized equivalents;
- each core Nakshatra interval is lower-inclusive and upper-exclusive, so a
  value immediately below a canonical lookup cusp remains in the earlier
  Nakshatra and the exact cusp starts the next Nakshatra; and
- a boolean or non-real longitude raises `TypeError`, while `NaN` and either
  infinity raise `ValueError` under the core helper contract.

Runtime tests must obtain cusp expectations from the core constants and
lookup output. They must not calculate a separate approximate span, invent an
epsilon, or introduce Nadi-specific longitude handling. Once a canonical name
or index reaches the matchmaking layer, the shared matchmaking normalizer—not
longitude arithmetic—owns normalization.

### Canonical Nakshatra-to-Nadi Mapping

The stable Nadi identifiers are exactly `adi`, `madhya`, and `antya`. The
mapping follows the canonical zero-based Nakshatra order:

| Index | Canonical Nakshatra | Nadi identifier | Traditional constitution |
|---:|---|---|---|
| 0 | Ashwini | `adi` | Vata |
| 1 | Bharani | `madhya` | Pitta |
| 2 | Krittika | `antya` | Kapha |
| 3 | Rohini | `antya` | Kapha |
| 4 | Mrigashira | `madhya` | Pitta |
| 5 | Ardra | `adi` | Vata |
| 6 | Punarvasu | `adi` | Vata |
| 7 | Pushya | `madhya` | Pitta |
| 8 | Ashlesha | `antya` | Kapha |
| 9 | Magha | `antya` | Kapha |
| 10 | Purva Phalguni | `madhya` | Pitta |
| 11 | Uttara Phalguni | `adi` | Vata |
| 12 | Hasta | `adi` | Vata |
| 13 | Chitra | `madhya` | Pitta |
| 14 | Swati | `antya` | Kapha |
| 15 | Vishakha | `antya` | Kapha |
| 16 | Anuradha | `madhya` | Pitta |
| 17 | Jyeshtha | `adi` | Vata |
| 18 | Moola | `adi` | Vata |
| 19 | Purva Ashadha | `madhya` | Pitta |
| 20 | Uttara Ashadha | `antya` | Kapha |
| 21 | Shravana | `antya` | Kapha |
| 22 | Dhanishtha | `madhya` | Pitta |
| 23 | Shatabhisha | `adi` | Vata |
| 24 | Purva Bhadrapada | `adi` | Vata |
| 25 | Uttara Bhadrapada | `madhya` | Pitta |
| 26 | Revati | `antya` | Kapha |

The mapping is exhaustive and contains exactly nine Nakshatras in each Nadi:

- `adi`: Ashwini, Ardra, Punarvasu, Uttara Phalguni, Hasta, Jyeshtha, Moola,
  Shatabhisha, and Purva Bhadrapada;
- `madhya`: Bharani, Mrigashira, Pushya, Purva Phalguni, Chitra, Anuradha,
  Purva Ashadha, Dhanishtha, and Uttara Bhadrapada; and
- `antya`: Krittika, Rohini, Ashlesha, Magha, Swati, Vishakha, Uttara Ashadha,
  Shravana, and Revati.

Runtime code must centralize this mapping once by canonical zero-based index,
verify complete `0..26` coverage and exactly nine members per Nadi, and must
not maintain separate name lists that can disagree.

### Exact Symmetric Scoring Convention

Rows represent the explicitly assigned bride's Nadi and columns represent the
explicitly assigned groom's Nadi for audit consistency. The matrix is the
complete normative lookup table:

| Bride \\ Groom | `adi` | `madhya` | `antya` |
|---|---:|---:|---:|
| `adi` | 0.0 | 8.0 | 8.0 |
| `madhya` | 8.0 | 0.0 | 8.0 |
| `antya` | 8.0 | 8.0 | 0.0 |

No score outside `{0.0, 8.0}` is valid. The score rule is exactly:

```text
score = 0.0 and nadi_dosha = true   when bride_nadi == groom_nadi
score = 8.0 and nadi_dosha = false  when bride_nadi != groom_nadi
```

The matrix is symmetric. Bride and groom roles remain explicit for identity
and audit output, but they do not make scoring directional. Role reversal must
swap the bride and groom identities while preserving the relationship,
same-Nadi flag, Nadi-Dosha flag, and score. Runtime must not average, rank,
round, infer, or default an unknown category pair.

### Same-Nadi, Different-Nadi, and Same-Nakshatra Behavior

- Every diagonal matrix cell has relationship `same_nadi`, sets
  `same_nadi = true` and `nadi_dosha = true`, and awards `0.0`.
- Same-Nadi scoring applies equally to Adi/Adi, Madhya/Madhya, and Antya/Antya
  and to every pair of Nakshatras within each group.
- Every off-diagonal matrix cell has relationship `different_nadi`, sets
  `same_nadi = false` and `nadi_dosha = false`, and awards `8.0`.
- The same Nakshatra necessarily has the same Nadi and therefore always scores
  `0.0` and sets Nadi Dosha.
- Same Nakshatra with equal Padas, different Padas, or absent Padas has the
  same `0.0` result. Pada is preserved as identity metadata only and never
  changes Nadi classification or scoring.
- Two different Nakshatras in the same Nadi score `0.0`; two Nakshatras in
  different Nadis score `8.0`.

Same-Nakshatra and same-Pada flags from the shared pair context remain audit
metadata only. They never override the canonical mapping or matrix.

### Explicit Exclusion of Cancellation and Exception Rules

Task 11.11 implements raw base Nadi Koota only. BhaktiAstro explicitly excludes
all Nadi Dosha cancellation, Parihara, mitigation, and exception rules,
including rules based on:

- different Padas of the same Nakshatra;
- one Nakshatra spanning different Rashis;
- the same Rashi with different Nakshatras;
- different Rashis, specific Rashi pairs, or Rashi parity;
- same, different, friendly, or mutually related Rashi lords;
- a special list of exempt Nakshatras;
- Gotra, lineage, caste, Varna, or an asserted hereditary relationship;
- Lagna, Navamsha, Graha placement, aspect, dignity, strength, or house state;
- Graha Maitri, Gana, Bhakoot, another Koota, or an aggregate Ashtakoota
  threshold; and
- remedies, practitioner judgement, or any regional cancellation tradition.

Therefore every same-Nadi pair scores `0.0` in Task 11.11, even when one or
more excluded exception conditions would apply elsewhere. Every
different-Nadi pair scores `8.0`. These exclusions are explicit BhaktiAstro
project decisions and prevent the selected North Indian base table from being
mixed with incompletely specified exception traditions.

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
- preserve valid Pada `1..4` as identity metadata but ignore it for Nadi
  classification and scoring;
- reject invalid Pada values through the existing shared issue contract;
- reject missing, unknown, duplicate, or identical bride/groom role
  assignments with stable role issue codes;
- preserve deterministic bride-before-groom issue ordering;
- return status `invalid` and score `None` whenever either identity or role
  assignment is invalid; and
- perform no partial classification, dosha flag, or fallback scoring for an
  invalid pair.

The low-level Nadi relationship lookup must accept only the three exact
canonical lowercase identifiers `adi`, `madhya`, and `antya`. It must raise
`TypeError` when either category is not a string and `ValueError` for empty,
malformed, aliased, case-variant, transliterated, or unknown identifiers,
including `aadi`, `aadya`, `vata`, `pitta`, and `kapha`. It must not case-fold,
guess, coerce, or default a public category input. The high-level calculator
catches expected input validation failures and returns a safe structured
invalid result; unexpected programming errors must not be swallowed.

Core longitude validation remains independently testable: booleans and
non-real inputs raise `TypeError`, and `NaN` and both infinities raise
`ValueError` through `get_nakshatra` before data reaches Nadi Koota.

### Public Immutable Result Contract

The runtime task must expose stable helpers from
`backend.app.matchmaking.__init__` for:

1. classifying one normalized matchmaking Nakshatra identity or supported
   Nakshatra input into its canonical Nadi identity;
2. looking up the symmetric relationship and score for two exact bride and
   groom Nadi identifiers; and
3. calculating the complete Nadi Koota result from an ordered matchmaking pair
   plus explicit `bride_role` and `groom_role`.

The structured result must expose at least:

- Koota identifier `nadi`;
- compatibility domain `physiological_compatibility`;
- status, awarded score, and maximum score `8.0`;
- unchanged `person_a` and `person_b` Nakshatra identities;
- explicit bride and groom role mapping;
- bride Nadi identity with canonical Nakshatra name, zero-based index, optional
  Pada, source person identifier, and canonical Nadi identifier;
- groom Nadi identity with the same fields;
- relationship identifier `same_nadi` or `different_nadi` and deterministic
  bride-row/groom-column matrix audit factors;
- same-Nakshatra, same-Pada, same-Nadi, and Nadi-Dosha flags;
- stable errors and warnings; and
- references and deterministic schema metadata consistent with existing
  matchmaking Koota results, including `directional = false`,
  `symmetric = true`, Nakshatra count `27`, and index base `0`.

Every returned result, identity, relationship, issue, metadata mapping,
direction mapping, factor list, reference list, error list, and warning list
must be newly allocated. Returned objects must share no mutable defaults or
nested collections and must be treated as immutable after construction. The
calculator must not mutate caller inputs. Repeated equivalent calls must
compare equal before caller mutation, and mutating one returned result must not
affect an earlier or later result.

All output must be strictly JSON-safe: dictionary keys and machine identifiers
are strings; valid scores are finite `0.0` or `8.0`; invalid score is `None`;
no `NaN`, infinity, tuple-only encoding, set, enum instance, dataclass
instance, or other non-JSON value may escape. Output ordering, issue ordering,
factor ordering, and identifiers must be deterministic. No interpretation
paragraph, medical conclusion, compatibility label, cancellation claim,
advice, remedy, API response, report formatting, other Koota, or Ashtakoota
total belongs in Task 11.11.

### Required Runtime Tests

Task 11.11 runtime implementation is not complete until focused tests cover:

- all 27 canonical Nakshatras by name and zero-based index, including every
  documented mapping and exactly nine members per Nadi;
- all three exact canonical Nadi identifiers and all nine cells of the
  symmetric `3 x 3` matrix;
- every one of the `27 x 27` ordered bride/groom Nakshatra pairs, asserting all
  `729` identity mappings, relationships, flags, and scores;
- all `243` same-Nadi ordered combinations: `81` Adi/Adi, `81` Madhya/Madhya,
  and `81` Antya/Antya, each scoring `0.0`;
- all `486` different-Nadi ordered combinations: all six off-diagonal Nadi
  category cells with `81` Nakshatra pairs each, all scoring `8.0`;
- all 27 same-Nakshatra cases with equal Pada, different Pada where supplied,
  and absent Pada, proving that every case scores `0.0`;
- representative different-Nakshatra pairs within every same Nadi and every
  ordered different-Nadi category pair;
- role reversal for all 729 pairs, proving that identities swap while
  relationship, same-Nadi state, Nadi-Dosha state, and score remain symmetric;
- all 27 core Moon-longitude Nakshatra lower cusps and values immediately below
  the next cusp at the existing six-decimal precision, classified through the
  reused core lookup rather than duplicated arithmetic;
- `0°`, `360°`, `-360°`, finite negative, and greater-than-`360°` core
  longitude normalization, plus core rejection of booleans, non-real values,
  `NaN`, and both infinities;
- matchmaking index boundaries `0` and `26`, invalid `-1` and `27`, missing
  values, wrong types, malformed names, and unsupported aliases;
- invalid Nadi lookup values, including non-strings, empty strings, case
  variants, whitespace variants, transliterations, Ayurvedic aliases, and
  unknown identifiers;
- missing, unknown, duplicate, and identical bride/groom roles;
- deterministic bride-before-groom issue ordering and no partial score or
  dosha flag;
- proof that Pada, Rashi, Rashi lordship, Gotra, special Nakshatra lists,
  another Koota, and every excluded cancellation condition do not alter the
  base matrix score;
- deterministic output equality, input non-mutation, independent nested
  collections, and strict `json.dumps(..., allow_nan=False)` serialization;
- stable public exports from `backend.app.matchmaking`; and
- regression compatibility with the core Nakshatra lookup, Task 11.3 pair
  context, and every completed matchmaking module.

### Convention Verification

The complete 27-star classification, exact binary matrix, North Indian use,
and existence of excluded exception traditions are documented by:

- [Nadi Koota - Saravali/Maitreya mapping and base rule](https://saravali.github.io/astrology/koota_nadi.html)
- [Nadi Dosha and Married Life - North Indian Nadi Chakra](https://www.futuresamachar.com/en/nadi-dosha-and-married-life-1163)
- [Horoscope Matching - Nadi Guna Milaan table and exception discussion](https://www.futuresamachar.com/download/horoscope-matching-325.pdf)
- [Nadi Koota in Kundli Matching - complete mapping and matrix](https://www.astroyogi.com/blog/nadi-koota-in-kundli-matching.aspx)

Some sources cancel same-Nadi results for different Padas, same or different
Rashis, particular Nakshatras, or Rashi-lord conditions. BhaktiAstro selects
only the common base mapping and symmetric `0.0`/`8.0` matrix above and does
not merge any cancellation or exception into Task 11.11.

### Completion and Verification

Task 11.11 is runtime-complete. The implementation adds the reusable Nadi
classification, strict relationship lookup, symmetric Koota calculator,
public exports, and exhaustive focused coverage without adding cancellation,
exception, aggregate, interpretation, API, report, or UI behavior.

Verification totals recorded for the implementation task:

- focused Nadi Koota suite: `949 passed`;
- complete matchmaking suite: `2052 passed`;
- Nakshatra and Kundali regression suite: `86 passed`; and
- complete project suite: `3020 passed, 13 skipped, 20 subtests passed`.

The skips remain the repository's pre-existing manual-reference validation
placeholders. Task 11.11 does not enable or alter them. Work stops here before
Task 11.12.

## Task 11.12 - Ashtakoota Aggregation

Status: **Complete**

### Purpose and Scope

Task 11.12 adds deterministic orchestration over the eight completed
Ashtakoota calculators. It collects each authoritative Koota result exactly
once, preserves the canonical order, and derives one arithmetic total with a
maximum of `36.0` points.

The aggregator is an orchestration layer only. It must not classify a Varna,
Vashya, Tara, Yoni, Graha Maitri relationship, Gana, Bhakoot pair, or Nadi;
copy a mapping, matrix, category, distance, boundary, or scoring rule from an
individual Koota; independently recalculate a component score; or change a
component result. Each completed Koota calculator remains the only authority
for its own identity, directionality, relationship, score, validation issues,
and maximum score.

Task 11.12 produces no compatibility judgement. It does not implement a
pass/fail threshold, label, grade, recommendation, remedy, Dosha cancellation,
Manglik calculation, Dasha analysis, horoscope interpretation, marriage
prediction, report prose, API route, or UI behavior. Interpretation and
compatibility reporting belong to later tasks.

### Canonical Koota Manifest and Maximum

The stable canonical order and expected public maximums are:

| Position | Koota identifier | Public calculator | Maximum score |
|---:|---|---|---:|
| 1 | `varna` | `calculate_varna_koota` | 1.0 |
| 2 | `vashya` | `calculate_vashya_koota` | 2.0 |
| 3 | `tara` | `calculate_tara_koota` | 3.0 |
| 4 | `yoni` | `calculate_yoni_koota` | 4.0 |
| 5 | `graha_maitri` | `calculate_graha_maitri_koota` | 5.0 |
| 6 | `gana` | `calculate_gana_koota` | 6.0 |
| 7 | `bhakoot` | `calculate_bhakoot_koota` | 7.0 |
| 8 | `nadi` | `calculate_nadi_koota` | 8.0 |

The total maximum is exactly:

```text
1.0 + 2.0 + 3.0 + 4.0 + 5.0 + 6.0 + 7.0 + 8.0 = 36.0
```

Runtime code must define one ordered manifest that refers to the eight
existing public Koota identifiers, maximum-score constants, and calculators.
It must assert at import time that the identifiers are unique, the order is
exactly the table above, and the maximum constants sum to `36.0`. It must not
repeat these values in independent execution, validation, result-order, and
serialization tables that could disagree.

The canonical order is part of the public contract. Input order, dictionary
order, import order, discovery order, and caller-provided precomputed-result
order must never change the emitted order.

### Two Explicitly Separated Public APIs

BhaktiAstro supports both raw orchestration and aggregation of precomputed
results, but only through two separately named APIs with different contracts:

1. `calculate_ashtakoota` accepts keyword-only
   `bride_moon_longitude` and `groom_moon_longitude`, derives only the shared
   adapter identities needed by the heterogeneous existing calculators, calls
   all eight real calculators, and returns the aggregate result.
2. `aggregate_ashtakoota_results` accepts a sequence of exactly eight
   caller-supplied precomputed Koota result mappings plus keyword-only
   `bride_moon_longitude` and `groom_moon_longitude`, strictly revalidates the
   aggregation contract, reorders copies into canonical order, and totals the
   supplied component scores without invoking a Koota calculator.

The raw API must not accept precomputed results. The precomputed API must not
invoke, replace, or silently repair a component calculator. No overloaded
argument, mode flag, type guessing, or mixed raw/precomputed input is allowed.
Both APIs require the two Moon longitudes so every successful aggregate result
has the same stable bride/groom audit fields.

The public signatures are exactly:

```python
def calculate_ashtakoota(
    *,
    bride_moon_longitude: object = None,
    groom_moon_longitude: object = None,
) -> MatchmakingAshtakootaResult: ...

def aggregate_ashtakoota_results(
    results: object,
    *,
    bride_moon_longitude: object = None,
    groom_moon_longitude: object = None,
) -> MatchmakingAshtakootaResult: ...
```

The two keyword names define the marriage roles. No separate role parameter
is accepted by the raw API, and it must never infer roles from names,
identifiers, call order, `person_a`, or `person_b`. An unexpected or
caller-supplied role argument is rejected by the Python signature rather than
guessed.

### Raw Moon-Longitude Orchestration

The raw API accepts finite real sidereal Moon longitudes in degrees. A
geographic birth longitude, including `MatchmakingPerson.longitude`, is not a
Moon longitude and must never be substituted. The API must reuse the existing
Rashi and Nakshatra core helpers to prepare adapters; it must not calculate a
Moon position from birth details.

For valid input, runtime orchestration must:

1. normalize both longitudes through
   `backend.app.kundali.rashi.normalize_longitude` into `[0, 360)`;
2. derive each Moon Rashi through `backend.app.kundali.rashi.get_rashi` and
   each Moon Nakshatra through
   `backend.app.astrology.nakshatra.get_nakshatra`;
3. create one internal ordered adapter pair where `person_a` is the bride and
   `person_b` is the groom, preserving canonical Rashi and Nakshatra data and
   using no unrelated birth or chart field; and
4. call the eight calculators exactly once in canonical manifest order.

The adapter derivation exists only because the completed calculators have two
established input shapes: Varna and the Nakshatra-based Kootas consume an
ordered pair, while Vashya, Graha Maitri, and Bhakoot consume explicitly named
Moon longitudes. It must not derive a component score or duplicate a Koota
rule.

The exact calls are:

- Varna: the adapter pair with `subject_role="person_a"` and
  `comparison_role="person_b"`, so the bride is the documented subject and
  the groom is the documented comparison;
- Vashya: the two named raw Moon-longitude inputs;
- Tara: the adapter pair with bride `person_a` and groom `person_b`;
- Yoni: the same pair and role assignment;
- Graha Maitri: the two named raw Moon-longitude inputs;
- Gana: the adapter pair with bride `person_a` and groom `person_b`;
- Bhakoot: the two named raw Moon-longitude inputs; and
- Nadi: the adapter pair with bride `person_a` and groom `person_b`.

For precomputed validation, the exact emitted `direction` mapping required
from each existing calculator is:

| Koota | Required direction mapping |
|---|---|
| `varna` | `subject_role: person_a`, `comparison_role: person_b` |
| `vashya` | `row_role: bride`, `column_role: groom` |
| `tara` | `bride_role: person_a`, `groom_role: person_b` |
| `yoni` | `bride_role: person_a`, `groom_role: person_b` |
| `graha_maitri` | `row_role: bride`, `column_role: groom` |
| `gana` | `bride_role: person_a`, `groom_role: person_b` |
| `bhakoot` | `row_role: bride`, `column_role: groom` |
| `nadi` | `bride_role: person_a`, `groom_role: person_b` |

The mapping must have these exact key/value pairs. Missing keys, extra keys,
non-string values, reversed roles, identical roles, and alternative aliases
are invalid. This check validates aggregation direction only; it does not
recalculate a component's directional score.

The aggregator must pass the caller's finite values to raw-longitude Kootas;
it must not substitute rounded values. The aggregate audit fields expose the
canonical normalized longitudes. Existing core helpers own all `[0, 360)`,
six-decimal boundary, negative-value, greater-than-`360°`, and exact cusp
behavior.

### Precomputed-Result Aggregation and Revalidation

`aggregate_ashtakoota_results` accepts a non-string sequence, not a mapping keyed
by Koota, because duplicate identifiers must remain detectable. The sequence
may arrive in any order, but it must contain exactly one result for every
canonical Koota and no other result. Runtime must copy and emit the results in
canonical order.

Every supplied component must be revalidated without reimplementing its
astrological rules. The strict structural checks are:

- the outer input is a non-string sequence containing exactly eight items;
- every item is a mapping;
- `koota` is a string and is one exact canonical identifier;
- no Koota identifier is duplicated, missing, or unexpected;
- `status` is exactly `complete`;
- `score` is a finite real number, is not a boolean, and lies inclusively
  between `0.0` and that Koota's expected maximum;
- `maximum_score` is a finite real number, is not a boolean, and exactly
  equals the imported expected maximum for that identifier;
- the result's role/direction metadata matches the canonical bride/groom call
  described above; and
- `errors` and `warnings`, where required by the existing Koota result
  convention, are JSON-safe collections and a complete result has no errors;
  and
- the complete component mapping and every nested value pass strict JSON-safe
  validation with no `NaN`, infinity, non-string key, or unsupported object.

Validation must not reconstruct a score from category, matrix, relationship,
Rashi, Nakshatra, distance, or factor fields. It therefore validates type,
identity, status, direction, finiteness, range, and maximum, but does not claim
to prove the astrological provenance of a caller-supplied result. The caller
is responsible for supplying results calculated for the accompanying Moon
longitudes. This limitation must be explicit and must not be hidden by a
false cross-Koota consistency claim.

Non-mapping component values and wrong field types raise `TypeError`.
Duplicate, missing, unexpected, invalid-status, out-of-range, non-finite,
direction-mismatched, error-bearing, or incorrect-maximum component results
raise `ValueError`. Error messages must identify the offending canonical
Koota or identifier set in deterministic canonical order. No malformed result
is coerced, skipped, defaulted, repaired, or replaced by a calculator call.

### Deterministic Execution and Failure Behavior

For valid raw inputs, all calculators execute once and only once in canonical
order. A structurally valid calculator mapping with status other than
`complete`, a `None` score, or errors makes the aggregate status `invalid` and
the aggregate `total_score` `None`. All eight calculators still execute so the
safe component validation issues remain available in canonical order.

The raw result may retain all eight copied component results and their
component errors for audit, but it must never publish a partial numeric total,
percentage, compatibility label, or success status. `score_by_koota` then
contains all eight canonical keys with `None` for any invalid component and
the validated finite score for each valid component. This diagnostic retention
is not partial aggregation: no aggregate score exists unless every Koota is
complete and valid.

A raw calculator returning a non-mapping, incorrect Koota identifier,
incorrect maximum, invalid score type, non-finite score, out-of-range score,
malformed direction mapping, or non-JSON-safe structure violates a completed
public calculator invariant. The aggregator must raise `TypeError` for a
wrong type and `ValueError` for a wrong value immediately; it must not retain
or serialize the malformed component, continue execution, or downgrade the
programming contract violation to an ordinary invalid astrology input.

Missing Koota results are never allowed in a successful aggregation. The
strict precomputed API raises for a missing item. A raw-input validation
failure occurs before Koota execution and returns a safe aggregate result with
status `invalid`, `total_score=None`, empty component and score collections,
and deterministic bride-before-groom issues. It must not fabricate eight
component results from invalid Moon data.

Expected invalid raw input is represented safely as described above.
Unexpected exceptions raised by `normalize_longitude`, `get_rashi`,
`get_nakshatra`, an individual Koota calculator, manifest validation, copying,
or programming invariants must propagate immediately unchanged. The
aggregator must not catch `Exception`, suppress a failure, substitute an
invalid component, continue after the raising calculator, or return a partial
result. Tests must inject a unique exception into each manifest position and
prove propagation and fail-fast call order.

Aggregate issues reuse `moon_longitude_missing` and
`moon_longitude_invalid` for raw bride/groom input fields. A returned
component that fails aggregation validation adds `koota_result_invalid` at
field `koota_results.<canonical_identifier>` with JSON-safe metadata naming
the failed validation aspect. Input issues are ordered bride then groom;
component issues are ordered by the canonical manifest. These aggregate
issues use the existing `matchmaking.validation.<code>` message-key pattern.
Strict precomputed-input failures raise the documented exceptions and do not
also return issue mappings.

### Exact Score Calculation and Floating-Point Policy

For eight complete validated results:

```text
total_score = math.fsum(component["score"] for component in canonical_order)
total_maximum_score = math.fsum(expected_maximum for canonical_order) = 36.0
```

The total is derived only from the eight returned or supplied component
scores. It is never independently recalculated from Moon longitudes,
classifications, factors, matrices, or relationships. Each component appears
exactly once.

Runtime must use `math.fsum` in canonical order, emit a finite JSON number,
and perform no decimal rounding, integer rounding, display formatting,
clamping, tolerance comparison, or score normalization. Current Koota scores
are integer or half-point values and are exactly representable as binary
floats. Fractional totals such as `16.5` must be preserved exactly as floats.
A successful total must satisfy `0.0 <= total_score <= 36.0`; violation is a
programming error and must raise rather than clamp.

Task 11.12 does not include a `percentage_score` field. A future reporting or
summary task may derive a percentage from the authoritative total, but this
task must not add percentage rounding or presentation policy.

### Zero, Full, Fractional, and Swapped-Input Behavior

- Eight structurally valid precomputed zero scores aggregate to exactly
  `0.0`; zero is a complete result, not a missing or false value.
- Eight structurally valid precomputed maximum scores aggregate to exactly
  `36.0`.
- Any valid mix containing half-point component scores retains the exact
  fractional sum without rounding.
- The raw API returns whatever eight real calculators award. Tests must not
  force a real Moon-longitude pair to produce an astrologically impossible
  synthetic zero or full score; the strict precomputed path provides the
  arithmetic boundary fixtures.
- Swapping the bride and groom Moon-longitude arguments performs a new
  canonical orchestration with roles swapped. The aggregator must not
  transpose, average, cache, or assume equality. Directional Varna, Vashya,
  Tara audit directions, and Gana outputs may change according to their own
  calculators; symmetric Kootas retain only the behavior their calculators
  define. The swapped total is independently summed from the swapped
  component results and may differ.

### Raw Input Validation and Normalization

Both APIs require keyword-only bride and groom Moon longitudes. Validation
follows the existing Rashi utility contract:

- booleans and non-real values are invalid and produce deterministic
  bride-before-groom issues from the raw orchestration API;
- `NaN`, positive infinity, and negative infinity are invalid;
- missing bride or groom values are invalid;
- finite `0°`, `360°`, `-360°`, negative values, and values greater than
  `360°` are accepted and normalized through existing utilities; and
- equivalent normalized inputs must produce identical normalized audit
  longitudes and component scores.

The precomputed API validates its required Moon-longitude audit inputs with
the same type, finiteness, and normalization rules before validating the
component sequence. Invalid audit inputs raise `TypeError` or `ValueError`
because the precomputed helper is a strict low-level aggregation API. It must
not guess which component belonged to which role.

### Public Immutable Result Contract

Task 11.12 follows the existing matchmaking project convention: a typed,
JSON-safe mapping result with newly allocated nested mappings and lists. It
does not introduce a dataclass, tuple result, enum object, Pydantic API model,
or a second serialization architecture. The mapping and all nested values are
immutable after construction by public contract, even though independent
mutable Python containers are used for backward compatibility with existing
Koota results.

The runtime task must export `ASHTAKOOTA_KOOTA_ORDER`,
`ASHTAKOOTA_TOTAL_MAXIMUM_SCORE`, the single ordered internal/public manifest
`ASHTAKOOTA_KOOTA_MANIFEST`, the aggregate issue/result/metadata typed mappings,
`calculate_ashtakoota`, and `aggregate_ashtakoota_results` from
`backend.app.matchmaking`. Existing exports must remain present and unchanged.

The aggregate result exposes exactly these top-level fields:

- `calculation`: stable identifier `ashtakoota_aggregation`;
- `status`: `complete` or `invalid` under the rules above;
- `bride_moon_longitude`: normalized finite longitude, or `None` for invalid
  raw input;
- `groom_moon_longitude`: normalized finite longitude, or `None` for invalid
  raw input;
- `koota_results`: copied full component mappings in canonical order;
- `score_by_koota`: a mapping in canonical order from each Koota identifier to
  its finite score, or to `None` for an invalid retained component;
- `maximum_score_by_koota`: a canonical-order mapping containing exactly
  `1.0` through `8.0` under their documented identifiers;
- `total_score`: the exact `math.fsum` result for eight valid components, or
  `None` when aggregation is invalid;
- `total_maximum_score`: always `36.0`;
- `errors`: stable localization-ready aggregate issues;
- `warnings`: copied component warnings in canonical Koota order, prefixed by
  Koota identifier, with no invented interpretive note;
- `references`: a newly allocated empty list because aggregation adds no new
  astrological rule or source; and
- `metadata`: a newly allocated deterministic mapping.

Metadata exposes at least component name, existing matchmaking schema version,
`deterministic=true`, execution mode `raw_calculators` or
`precomputed_results`, canonical Koota order, expected Koota count `8`,
validated Koota count, total maximum `36.0`, aggregation method `math_fsum`,
`percentage_included=false`, and interpretation/cancellation flags set to
false where the existing metadata convention includes scope flags.

There is no generic compatibility-domain field for the total because the
eight Kootas represent different domains. The complete component results
retain their own domains. The aggregate must not concatenate references,
factors, prose, or domain labels into a new interpretation.

Every result call must deep-copy caller-supplied precomputed results and
allocate independent component lists, score mappings, maximum mappings,
issues, warnings, references, and metadata. It must not mutate caller input or
share a nested collection with the caller, a manifest constant, an individual
calculator result retained elsewhere, an earlier call, or a later call.
Repeated equivalent calls compare equal before caller mutation. Mutating a
returned collection cannot affect another result or any source component.

All output must pass `json.dumps(..., allow_nan=False)`. Keys and identifiers
are strings; scores and longitudes are finite numbers or `None`; no tuple,
set, enum instance, dataclass instance, exception object, callable, `NaN`, or
infinity may escape. Ordering of components, score mappings, maximum mappings,
issues, warnings, references, and metadata is deterministic.

### Excluded Behavior

Task 11.12 explicitly excludes:

- any copied or alternative Koota classification, mapping, matrix, formula,
  boundary, normalization, relationship, cancellation, or scoring rule;
- partial numeric totals, weighted Kootas, dropped low scores, bonus points,
  penalties, overrides, and score caps other than validation against `36.0`;
- compatibility labels, thresholds, grades, pass/fail decisions, prose,
  recommendations, remedies, or marriage predictions;
- Manglik/Kuja Dosha, Dasha compatibility, Gotra, planetary strength,
  Navamsha, transits, horoscope interpretation, or chart synthesis;
- Bhakoot, Nadi, Tara, or other Dosha cancellation and exception rules;
- API, database, report, UI, localization text, analytics, or external-service
  integration; and
- Task 11.13 Manglik compatibility, Task 11.14 Compatibility / Report
  Composition, or Task 11.15 serialization hardening.

### Required Runtime Tests

Task 11.12 runtime implementation is not complete until focused tests cover:

- raw aggregation through all eight real public calculators without replacing
  or duplicating any calculator;
- exact canonical order `varna`, `vashya`, `tara`, `yoni`, `graha_maitri`,
  `gana`, `bhakoot`, `nadi` in execution, results, score mapping, maximum
  mapping, warnings, and metadata;
- exactly one invocation and one included score for every calculator;
- imported component maximums `1.0` through `8.0` and exact total maximum
  `36.0`;
- independent verification that each successful `total_score` equals
  `math.fsum` of the eight emitted component scores;
- a precomputed all-zero fixture producing complete total `0.0`;
- a precomputed all-maximum fixture producing complete total `36.0`;
- a precomputed fractional fixture and at least one real-calculator fractional
  result, proving no rounding;
- representative normalized equivalents including `0°`, `360°`, `-360°`,
  finite negative, and greater-than-`360°` inputs;
- raw rejection of missing values, booleans, non-real values, `NaN`, and both
  infinities with deterministic bride-before-groom issues;
- strict precomputed-input type validation and longitude validation;
- every duplicate Koota identifier, every single missing canonical identifier,
  every unexpected identifier, and combined missing/unexpected sets;
- incorrect individual result types, non-string identifiers, invalid status,
  `None`, boolean, non-real, non-finite, negative, and above-maximum scores;
- every incorrect individual maximum, including boolean and non-finite values;
- missing, malformed, error-bearing, and mismatched role/direction metadata;
- one injected calculator exception at each of the eight manifest positions,
  proving the same exception propagates, later calculators do not run, and no
  partial result is returned;
- one returned invalid result at each manifest position, proving all eight
  audit results remain ordered but `total_score` is `None`;
- swapped bride/groom raw inputs, proving directional components and total are
  taken from the newly executed calculators without forced symmetry;
- deterministic equality across repeated calls, caller-input non-mutation,
  deep-copy isolation, independent mutable collections, and immutable-after-
  construction public-contract expectations;
- strict deterministic JSON serialization with `allow_nan=False` and absence
  of percentage, interpretation, threshold, recommendation, remedy,
  cancellation, Manglik, Dasha, and prediction fields;
- stable public exports for the manifest, total maximum, result types, raw
  orchestrator, and strict precomputed aggregator;
- backward compatibility with every existing Koota public import and direct
  calculator call; and
- focused regressions proving all eight individual calculator suites remain
  unchanged, followed by the complete matchmaking, Rashi, Nakshatra, Kundali,
  and full project suites.

### Completion and Verification

Task 11.12 is runtime-complete. The implementation adds the immutable ordered
manifest, raw Moon-longitude orchestrator, strict precomputed-result
aggregator, structural component validation, exact `math.fsum` total, public
exports, and focused coverage without copying any individual Koota rule or
adding interpretation, cancellation, or future-task behavior.

Verification totals recorded for the implementation task:

- focused Ashtakoota aggregation suite: `140 passed`;
- all eight individual Koota suites: `1966 passed`;
- complete matchmaking suite: `2192 passed`;
- Rashi and Nakshatra regression suite: `33 passed`; and
- complete project suite: `3160 passed, 13 skipped, 20 subtests passed`.

The skips remain the repository's pre-existing manual-reference validation
placeholders. Task 11.12 does not enable or alter them. Work stops here before
Task 11.13.

## Task 11.13 - Manglik Compatibility Foundation

Status: **Complete**

### Purpose and Scope

Task 11.13 defines a deterministic, structured foundation for identifying the
selected BhaktiAstro form of Manglik status for each partner and comparing the
two statuses. It records Mars's whole-sign house from the Lagna and exposes the
facts needed by later compatibility composition without making a marriage
judgement.

This task is separate from the `36.0`-point Ashtakoota total. It must not call,
modify, rerun, append to, or reinterpret Task 11.12. Manglik classification is
not a ninth Koota, does not change an individual Koota score, and does not
change the Ashtakoota maximum.

The foundation produces no prediction, remedy, recommendation, pass/fail
label, compatibility advice, marriage advice, interpretive prose, or AI
narrative. Task 11.14 may compose the structured result with other completed
matchmaking artifacts, but it must not be implemented by Task 11.13.

### BhaktiAstro Convention Decision

Manglik conventions vary by lineage. BhaktiAstro deliberately selects one
narrow, reproducible convention for this foundation:

- use the sidereal whole-sign birth chart;
- evaluate Mars from the Lagna only;
- classify houses `1`, `4`, `7`, `8`, and `12` as Manglik houses;
- do not include house `2`;
- do not evaluate Mars from the Moon or Venus;
- use a binary `manglik` or `non_manglik` classification;
- compare the two binary classifications without awarding points; and
- apply no cancellation, exception, weighting, severity, or interpretation
  rule.

This is a BhaktiAstro project convention, not an attempt to merge every
traditional alternative. Sources describing the selected five-house base rule
include [AstroCalc's Manglik overview](https://astrocalc.in/learn/manglik) and
[ShreeKundli's distinction between the five-house and extended
conventions](https://www.shreekundli.com/vedic-astrology/compatibility/manglik-dosha).
These references provide convention context only. The rules in this section,
including every explicit exclusion, are the sole implementation authority.

### Relationship to Existing Modules

Task 11.13 consumes existing chart facts and must not become another astronomy
engine:

- `backend.app.astronomy.planet_positions` remains authoritative for the
  canonical Mars identity and sidereal planetary longitude;
- `backend.app.kundali.lagna` remains authoritative for the sidereal Lagna;
- `backend.app.kundali.rashi.normalize_longitude` and `get_rashi` remain
  authoritative for longitude normalization and Rashi boundaries;
- `backend.app.kundali.placement.get_planet_house_placement` remains
  authoritative for whole-sign planet placement and one-based house numbers;
- `backend.app.kundali.chart.KundaliChart` remains the established chart
  mapping consumed by the chart adapter; and
- `backend.app.matchmaking.validation` remains authoritative for
  localization-ready issue structure, deterministic validation ordering, and
  non-coercing type/range behavior; and
- the matchmaking foundation remains authoritative for copied JSON-safe
  collections, schema metadata, statuses, and public result style.

Runtime code must call these utilities. It must not copy longitude modulo
logic, Rashi division, planet-name tables, relative-sign arithmetic, or house
placement formulas into the matchmaking package. It must not calculate a
birth chart from date, time, place, timezone, ayanamsa, or ephemeris data.

### Supported Inputs and Separated APIs

Task 11.13 supports three input levels through separately named APIs. No API
may guess the input mode from an overloaded mapping or positional argument.

```python
def classify_manglik(
    *,
    lagna_sidereal_longitude: object = None,
    mars_sidereal_longitude: object = None,
) -> ManglikClassificationResult: ...

def classify_manglik_from_chart(
    *,
    chart: object = None,
) -> ManglikClassificationResult: ...

def compare_manglik_classifications(
    *,
    bride: object,
    groom: object,
) -> ManglikCompatibilityResult: ...
```

`classify_manglik` is the raw identity API. Both keyword-only inputs are
required finite real sidereal longitudes in degrees. It derives the single
person's Lagna Rashi, Mars Rashi, and Mars house with existing utilities.

`classify_manglik_from_chart` is the existing-chart adapter. It accepts a
`KundaliChart`-shaped mapping, not raw birth details. The mapping must contain:

- `lagna`, as a mapping with finite `sidereal_longitude` and a one-based
  integral non-boolean `rashi_index` in `1..12`; and
- `planets`, as a non-string sequence containing exactly one mapping whose
  canonical lowercase `planet` value is `mars`, with a finite
  `sidereal_longitude`.

The Lagna longitude and Rashi index must agree after canonical derivation. If
the Mars mapping contains `rashi_index`, `rashi`, `rashi_degree`,
`house_index`, or `house_number`, each supplied placement field must agree
exactly with the canonical placement derived by existing utilities. Optional
chart sections such as Vargas, Bhavas, Dashas, predictions, or Panchang are
ignored and must not affect the result. The adapter copies required values and
never mutates the chart.

`compare_manglik_classifications` accepts exactly two Task 11.13
classification-result mappings. This is the only precomputed-input API. A
complete comparison requires two complete, valid classifications. The
comparator strictly revalidates the public classification contract, copies
both identities, and returns a structured invalid pair when either supplied
result is invalid or malformed. It does not accept arbitrary planetary-
position lists, caller-supplied boolean flags, category strings, or direct
house numbers as substitutes for a classification result.

A caller holding only longitudes must call `classify_manglik` separately for
each person and then call `compare_manglik_classifications`. Loose precomputed
planet positions and direct `mars_house` input are intentionally unsupported.
This separation prevents stale or inconsistent caller-supplied house numbers
from bypassing canonical chart placement.

A caller holding bride and groom charts must likewise call
`classify_manglik_from_chart` once for each role and pass the two validated
results to `compare_manglik_classifications`. The comparator's explicit
keyword names define the roles. No API infers bride or groom from gender,
names, identifiers, array order, `person_a`, or `person_b`. Task 11.13 defines
no fourth convenience API that accepts two charts; report or composition
orchestration belongs to Task 11.14.

### Longitude, Rashi, and House Derivation

The raw classifier derives placement in this exact order:

1. validate both supplied values as finite real numbers, rejecting booleans;
2. normalize both through the existing longitude utility into `[0, 360)`;
3. derive the one-based Lagna and Mars Rashi indexes with `get_rashi`;
4. call `get_planet_house_placement` with the derived Lagna Rashi index and
   normalized Mars longitude; and
5. use the returned one-based `house_number` as the only classification
   input.

The house system is the existing whole-sign system. Houses are numbered
`1..12` from the Lagna Rashi: the Lagna sign is house `1`, the next Rashi is
house `2`, and so on circularly through house `12`. `house_index`, where
included only as audit data, is zero-based `0..11` and must always equal
`house_number - 1`.

As a conformance identity for one-based Rashi indexes, the existing placement
result must satisfy:

```text
house_number = ((mars_rashi_index - lagna_rashi_index) mod 12) + 1
```

This identity specifies expected behavior and tests; it is not permission to
copy the formula into the matchmaking implementation. Runtime must obtain the
house from `get_planet_house_placement`.

There are no quadrant cusps or degree-based house boundaries. Each Rashi is a
half-open interval beginning at an exact multiple of `30°`; exact normalized
Rashi boundaries belong to the new sign under the existing Rashi utility.
The exact Lagna degree within its Rashi does not move a planet to another
house. Therefore a Mars longitude in the Lagna Rashi is house `1` even when it
is numerically below the Lagna longitude.

Core normalization owns deterministic six-decimal behavior. `0°`, `360°`,
`-360°`, other finite negative values, and values greater than `360°` are
accepted and normalized consistently. Task 11.13 must not add another modulo,
epsilon, tolerance, rounding, or cusp policy.

No public API normalizes a supplied house number modulo `12`. A redundant
chart `house_number` must be an integral non-boolean value in `1..12`; `0`,
`13`, negative values, floats with a fractional part, strings, and booleans
are invalid. A valid but inconsistent redundant house is also invalid rather
than silently replaced.

### Exact Classification Rule

The applicable Manglik-house constant is exactly, and in this stable order:

```text
[1, 4, 7, 8, 12]
```

For a valid person:

```text
classification = "manglik"     if mars_house in {1, 4, 7, 8, 12}
classification = "non_manglik" otherwise
```

All seven other houses, including house `2`, are `non_manglik`. `manglik`
means only that Mars occupies one selected house from the Lagna under this
binary project convention. `non_manglik` means only that it does not. Neither
identifier predicts an event, quantifies harm, or expresses suitability for
marriage.

There is no `partial_manglik`, `low`, `medium`, `high`, percentage, weight,
intensity, severity, or house-specific rank. One supported house cannot be
more Manglik than another. A classification reason code is factual:
`mars_in_manglik_house` or `mars_not_in_manglik_house`.

### Exact Bride/Groom Comparison Rule

Task 11.13 is structured-only and awards no points. It has no `score`,
`awarded_score`, `maximum_score`, threshold, grade, or contribution to the
Ashtakoota total.

The ordered role-preserving comparison table is:

| Bride | Groom | `pair_classification` | `comparison_status` |
|---|---|---|---|
| `manglik` | `manglik` | `both_manglik` | `same_status` |
| `non_manglik` | `non_manglik` | `both_non_manglik` | `same_status` |
| `manglik` | `non_manglik` | `bride_manglik_groom_non_manglik` | `mixed_status` |
| `non_manglik` | `manglik` | `bride_non_manglik_groom_manglik` | `mixed_status` |

The same-versus-mixed comparison is symmetric. Swapping the two complete
identities preserves `same_status` or `mixed_status`, while the role-specific
fields and mixed `pair_classification` transpose. No row has greater authority
than another, and no direction changes a person's classification.

`same_status` is not a synonym for compatible, approved, cancelled, or safe.
`mixed_status` is not a synonym for incompatible, rejected, harmful, or
unsafe. In particular, `both_manglik` records two positive classifications;
it does not apply a double-Manglik or mutual-Manglik cancellation rule.

### Explicitly Excluded Factors and Exceptions

Classification depends only on canonical Mars whole-sign house from the
Lagna. Task 11.13 excludes all of the following as explicit BhaktiAstro
project decisions:

- Moon-based, Venus-based, or combined multiple-reference evaluation;
- house `2` as a Manglik house;
- partial, weighted, cumulative, intensity, or severity classification;
- Mars sign exceptions or Rashi-specific exceptions;
- Mars aspects, aspects to Mars, conjunctions, combustion, retrograde state,
  dignity, strength, Shadbala, functional benefic/malefic status, or age;
- Mars exaltation, debilitation, own sign, friendly sign, enemy sign, or
  sign-lord and house-lord conditions;
- benefic aspects, planetary lordship, conjunction with a benefic, or any
  other mitigating placement;
- mutual Manglik, double-Manglik, same-status, same-Rashi, or partner-chart
  cancellation;
- Navamsha, other divisional charts, Bhava Chalit, non-whole-sign cusps,
  Vargas, Upapada, Dasha, transits, Gotra, or horoscope synthesis; and
- every unnamed Manglik Dosha cancellation, exception, remedy, prediction,
  recommendation, or marriage-advice rule.

Runtime code must not silently add one of these rules because it appears in a
source or another astrology tradition. Adding any excluded rule requires a
later separately specified task with its precedence, inputs, output contract,
and exhaustive tests.

### Validation and Failure Propagation

Expected invalid input is represented by deterministic structured results;
it is never guessed, coerced, or repaired.

Task 11.13 defines exactly four public issue codes:

| Code | Use |
|---|---|
| `manglik_input_missing` | A required raw Lagna/Mars value or required nested chart value is absent. |
| `manglik_input_invalid` | A supplied raw value has an invalid type, is non-finite, or violates its documented range. |
| `manglik_chart_invalid` | The chart shape, Mars cardinality, canonical identity, or redundant placement is malformed or inconsistent. |
| `manglik_classification_invalid` | A precomputed classification violates the Task 11.13 result contract. |

Each issue uses the existing matchmaking validation issue shape and message
key `matchmaking.validation.<code>`. The `field` path, not a new issue code,
identifies Lagna versus Mars, chart nesting, and bride versus groom. No other
issue code or human-language error message is part of this task.

- missing Lagna or Mars longitude produces a field-specific
  `manglik_input_missing` issue;
- booleans, strings, containers, complex numbers, and other non-real values
  produce a field-specific `manglik_input_invalid` issue;
- `NaN`, positive infinity, and negative infinity produce a field-specific
  `manglik_input_invalid` issue;
- a non-mapping chart, malformed `lagna`, non-sequence `planets`, missing or
  duplicate Mars, invalid canonical planet identity, absent required
  longitude, invalid Rashi/house index, or inconsistent redundant placement
  produces `manglik_input_missing`, `manglik_input_invalid`, or
  `manglik_chart_invalid` at the exact offending field path;
- an incomplete, invalid, malformed, wrong-component, wrong-schema, or
  internally inconsistent precomputed classification produces a
  `manglik_classification_invalid` issue; and
- unknown category values are invalid; runtime must not case-fold or alias a
  malformed caller-supplied classification.

Issue codes and message keys follow the existing matchmaking convention and
are ordered deterministically: bride before groom, then outer field order,
then nested field order. Issues contain only stable machine-readable fields
and JSON-safe details; exception objects and localized prose must not escape.

If either classification is invalid, the pair result is `invalid`,
`pair_classification` and `comparison_status` are empty, and there is no
partial comparison. The pair may retain copied invalid bride and groom
classification results for audit. The comparator validates both supplied
classifications in bride-then-groom order so both ordinary contract failures
can be reported deterministically.

Expected `TypeError` and `ValueError` failures raised by the reused core
validators for the documented public fields are translated to the structured
issues above. Unexpected exceptions from chart access, longitude/Rashi/house
utilities, copying, contract invariants, or programming errors propagate
unchanged. Runtime must not catch `Exception`, fabricate a fallback house,
return a partial successful comparison, or suppress a dependency failure.
Python signature errors for positional use of keyword-only parameters or
unknown keyword names remain ordinary `TypeError` exceptions.

### Public Immutable Result Contract

Task 11.13 follows the existing matchmaking result convention: typed,
JSON-safe mapping results with newly allocated nested mappings and lists. It
does not introduce a dataclass, tuple result, enum instance, Pydantic API
response, or a second serialization system. Results and all nested values are
immutable after construction by public contract, while independent mutable
containers preserve compatibility with existing matchmaking results.

`ManglikClassificationResult` exposes exactly:

- `calculation`: `manglik_classification`;
- `status`: `complete` or `invalid`;
- `classification`: `manglik`, `non_manglik`, or an empty string when invalid;
- `reference_point`: `lagna` for valid results, or an empty string when the
  reference cannot be validated;
- `lagna_sidereal_longitude` and `mars_sidereal_longitude`: normalized finite
  values, or `None` when invalid;
- `lagna_rashi_index` and `mars_rashi_index`: one-based indexes, or `None`;
- `mars_house`: one-based `1..12`, or `None`;
- `applicable_manglik_houses`: `[1, 4, 7, 8, 12]` as a fresh list;
- `reason`: one stable factual reason code, or an empty string when invalid;
- `errors`, `warnings`, and `references`: newly allocated lists; and
- `metadata`: a newly allocated deterministic mapping.

`ManglikCompatibilityResult` exposes exactly:

- `calculation`: `manglik_compatibility`;
- `status`: `complete` or `invalid`;
- `bride_manglik` and `groom_manglik`: copied full classification results;
- `bride_classification` and `groom_classification`: the two canonical binary
  identifiers, or empty strings when invalid;
- `bride_reference_point` and `groom_reference_point`: `lagna` for complete
  results;
- `bride_mars_house` and `groom_mars_house`: one-based houses, or `None`;
- `applicable_manglik_houses`: `[1, 4, 7, 8, 12]` as a fresh list;
- `pair_classification`: one exact table identifier, or an empty string;
- `comparison_status`: `same_status`, `mixed_status`, or an empty string;
- `reasons`: the bride's factual classification reason, the groom's factual
  classification reason, then exactly `same_manglik_status` or
  `mixed_manglik_status` for a complete comparison;
- `errors`, `warnings`, and `references`: newly allocated lists; and
- `metadata`: a newly allocated deterministic mapping.

Neither result contains `score`, `maximum_score`, compatibility advice,
interpretation, cancellation, remedy, or prediction fields. Warnings are empty
in this foundation; they are reserved for future explicitly specified
non-fatal contract conditions and must not contain astrological prose.

Metadata contains at least the existing matchmaking schema version,
component identifier, `deterministic=true`, `house_system=whole_sign`,
`house_numbering=one_based`, `reference_points=["lagna"]`,
`applicable_manglik_houses=[1, 4, 7, 8, 12]`,
`classification_mode=binary`, `comparison_mode=structured_only`,
`scoring_included=false`, `severity_included=false`,
`cancellation_rules_included=false`, `divisional_charts_included=false`, and
`ashtakoota_recalculated=false`. The compatibility result also records stable
bride/groom role order and `same_mixed_comparison_symmetric=true`.

Every call deep-copies accepted chart or precomputed values and allocates
independent nested classifications, applicable-house lists, reasons, issues,
warnings, references, and metadata. No result may share a mutable object with
caller input, a module constant, a source chart, an earlier call, or a later
call. Repeated equivalent calls compare equal before caller mutation, and
mutation of one returned collection cannot affect any other result.

All output must pass `json.dumps(..., allow_nan=False)`. Keys and identifiers
are strings; longitudes are finite floats or `None`; house and Rashi indexes
are integers or `None`; no tuple, set, enum instance, dataclass instance,
exception object, callable, `NaN`, or infinity may escape. Key, reason, issue,
warning, reference, applicable-house, and metadata ordering is deterministic.

The runtime task must publicly export `MANGLIK_HOUSES`, the classification and
pair identifiers, the typed issue/result/metadata mappings, and all three
public functions from `backend.app.matchmaking`. It may add new exports only;
every existing Kundali, placement, matchmaking, Koota, and Ashtakoota import
and behavior must remain unchanged.

### Required Runtime Tests

Task 11.13 runtime implementation is not complete until focused tests cover:

- the exact `[1, 4, 7, 8, 12]` constant order and positive classification for
  every one of those houses;
- negative classification for every other house `2`, `3`, `5`, `6`, `9`,
  `10`, and `11`;
- all 12 Lagna Rashis and all 144 Lagna-Rashi/Mars-Rashi combinations,
  independently proving the derived one-based whole-sign house;
- exact `0°`, every `30°` Rashi boundary, values immediately below each
  boundary under core precision, and circular `330°/0°` behavior;
- equivalent normalization for `0°`, `360°`, `-360°`, finite negative values,
  and values greater than `360°` for both Lagna and Mars;
- the sole supported `lagna` reference point and rejection of Moon, Venus,
  combined, or caller-invented reference points in precomputed input;
- all four bride/groom classification rows, including Manglik/Manglik,
  non-Manglik/non-Manglik, and both role orders of mixed status;
- same/mixed symmetry under swapping, plus correct transposition of
  role-specific fields and mixed pair identifiers;
- proof that both-Manglik remains `both_manglik` with no cancellation or
  compatibility judgement;
- chart-adapter success against real-shaped Kundali fixtures and equivalence
  with raw classification for the same canonical longitudes;
- redundant chart placement agreement and rejection of inconsistent
  `rashi_index`, `rashi`, `rashi_degree`, `house_index`, or `house_number`;
- house validation for `1`, `12`, `0`, `13`, negative, fractional, string,
  boolean, and missing values without modulo normalization;
- missing Lagna, missing Mars, duplicate Mars, malformed planet entries,
  invalid canonical planet names, malformed chart context, and non-mapping
  chart input;
- missing raw values, booleans, non-real values, `NaN`, positive infinity,
  and negative infinity for every longitude field;
- malformed, incomplete, invalid-status, wrong-component, unknown-category,
  wrong-house, wrong-reference, and internally inconsistent precomputed
  classification results;
- bride-before-groom deterministic issue order, validation of both ordinary
  invalid precomputed classifications, no partial comparison, and propagation
  of unexpected dependency exceptions;
- repeated deterministic equality, caller-input non-mutation, immutable-after-
  construction public expectations, deep-copy isolation, and independent
  mutable collections for every result path;
- strict `json.dumps(..., allow_nan=False)` serialization and exact absence of
  scoring, severity, interpretation, recommendation, remedy, prediction,
  Ashtakoota, and cancellation fields;
- stable public exports for constants, typed contracts, raw classification,
  chart classification, and precomputed comparison;
- backward compatibility with direct astronomy, Rashi, Lagna, placement,
  Kundali chart, matchmaking foundation, all eight Koota, and Ashtakoota
  public imports and behavior; and
- focused Manglik tests followed by the complete matchmaking, Rashi, Kundali,
  planet-position, house-placement, and full project regression suites.

### Documentation Progress Rules

Task 11.13 runtime completion is recorded only after the runtime module,
focused tests, public exports, and required regression verification are
complete. `docs/MASTER.md` now records Task 11.13 as completed. No progress
entry for Task 11.14 is added by this task.

Task 11.14 remains Compatibility / Report Composition. This task must not be
moved, renamed, replaced, specified, or implemented by Task 11.13.

### Completion and Verification

Task 11.13 is runtime-complete. The implementation adds the documented
Lagna-only raw classifier, existing-Kundali chart adapter, strict precomputed
bride/groom comparator, binary five-house convention, deterministic safe
validation, immutable JSON-safe result contracts, and additive public exports.
It reuses canonical longitude normalization, Rashi derivation, and whole-sign
placement without adding a score, cancellation, interpretation, or Task 11.14
composition behavior.

Verification totals recorded for the implementation task:

- focused Manglik compatibility suite: `273 passed`;
- complete matchmaking suite: `2465 passed`;
- Kundali, Lagna, placement, Rashi, and planet-position regression suite:
  `65 passed`; and
- complete project suite: `3433 passed, 13 skipped, 20 subtests passed`.

The skips remain the repository's pre-existing manual-reference validation
placeholders. Task 11.13 does not enable or alter them. Work stops here before
Task 11.14.

## Task 11.14 - Compatibility / Report Composition

Status: **Complete**

### Purpose and Scope

Task 11.14 defines a deterministic structured report composer over the two
completed compatibility foundations:

- Task 11.12, the eight-Koota Ashtakoota aggregate with maximum `36.0`; and
- Task 11.13, the Lagna-only binary Manglik compatibility result with no
  score.

The composer presents validated calculation artifacts in one stable,
machine-readable mapping suitable for later API, UI, HTML, or PDF consumers.
It does not implement any of those consumers. It is an orchestration and data
composition layer only, not a new calculation, interpretation, or rendering
layer.

Task 11.14 does not alter Task 11.12 or Task 11.13. Ashtakoota remains the
only scored component, its maximum remains exactly `36.0`, and Manglik remains
structured-only. The report has no independent astrology rule and no authority
to change either component.

### BhaktiAstro Project Decisions

The source-of-truth project decisions are:

- the report is structured data only;
- no overall compatibility, suitability, pass/fail, approval, rejection, or
  marriage-outcome label is included;
- report `status` describes only technical completeness and validation;
- no score combines Ashtakoota and Manglik;
- no percentage is included because Task 11.12 does not expose one;
- no partial-success report is allowed;
- invalid raw calculations may be retained for technical audit, but the report
  remains `invalid` and must not be treated as complete;
- strict precomputed or serialization input never returns a repaired report;
- component errors and exceptions are never hidden;
- bride and groom roles are explicit and preserved; and
- stable identifiers and factual component values replace narrative prose.

The composer must not infer compatibility meaning from a high or low
Ashtakoota score, `same_status` or `mixed_status` Manglik metadata, or any
combination of the two.

### Dependency and Architecture Boundary

Runtime implementation must import and orchestrate these existing public
contracts from `backend.app.matchmaking`:

- `calculate_ashtakoota` and `MatchmakingAshtakootaResult`;
- `aggregate_ashtakoota_results` for strict Koota-result revalidation;
- `ASHTAKOOTA_KOOTA_ORDER`, `ASHTAKOOTA_KOOTA_MANIFEST`, and
  `ASHTAKOOTA_TOTAL_MAXIMUM_SCORE`;
- `classify_manglik` and `ManglikClassificationResult`;
- `compare_manglik_classifications` and `ManglikCompatibilityResult`;
- `MANGLIK_HOUSES`, the Manglik classification identifiers, pair identifiers,
  and comparison-status identifiers; and
- `MATCHMAKING_SCHEMA_VERSION`, the existing JSON-safe value convention, and
  matchmaking validation issue structure.

The composer must not import private classification tables, Koota matrices,
planetary relationships, Nakshatra mappings, Rashi mappings, house formulas,
or private result builders. It must not copy or reimplement longitude
normalization, Nakshatra/Rashi derivation, Koota scoring, aggregation totals,
Mars placement, Manglik classification, or bride/groom comparison logic.

Task 11.14 does not accept birth date, time, place, timezone, geographic
longitude, person profiles, or calculate a Kundali. It consumes only the six
explicit sidereal longitudes on the raw path or completed Task 11.12 and 11.13
results on the precomputed path.

### Three Explicitly Separated Public APIs

Task 11.14 defines exactly three keyword-only public APIs:

```python
def compose_compatibility_report(
    *,
    bride_moon_longitude: object = None,
    groom_moon_longitude: object = None,
    bride_lagna_longitude: object = None,
    groom_lagna_longitude: object = None,
    bride_mars_longitude: object = None,
    groom_mars_longitude: object = None,
) -> MatchmakingCompatibilityReport: ...

def compose_compatibility_report_from_results(
    *,
    ashtakoota: object,
    manglik: object,
) -> MatchmakingCompatibilityReport: ...

def serialize_compatibility_report(
    *,
    report: object,
) -> dict[str, MatchmakingJsonValue]: ...
```

No overload, mode flag, positional role input, mixed raw/precomputed call, or
input-shape guessing is permitted. Python rejects positional arguments and
unknown keywords with `TypeError`.

#### Raw-Input Composer

`compose_compatibility_report` is the safe orchestration API. All six inputs
are required finite real sidereal longitudes in degrees; booleans are not
numeric inputs. The names define the roles. Geographic birth longitude must
never be substituted for any of them.

For every call, execution order is exactly:

1. call `calculate_ashtakoota` once with the bride and groom Moon longitudes;
2. call `classify_manglik` once with the bride Lagna and Mars longitudes;
3. call `classify_manglik` once with the groom Lagna and Mars longitudes;
4. call `compare_manglik_classifications` once with the resulting bride and
   groom classifications; and
5. compose copied report sections from those public results.

The composer passes the caller's raw values to the public calculators. It does
not normalize them first, create an alternative pair context, or derive a
Rashi, Nakshatra, house, category, score, total, or Manglik status. Normalized
report input summaries come only from the public component results.

Expected invalid raw values are represented by the existing safe component
results and yield one report with `status="invalid"`. The report retains copied
component facts and issues for audit, but technical validation fails and there
is no partial-success status. A valid Ashtakoota total retained beside an
invalid Manglik result, or vice versa, is component audit data and does not make
the report partially complete.

#### Strict Precomputed Composer

`compose_compatibility_report_from_results` accepts one complete Task 11.12
aggregate and one complete Task 11.13 compatibility mapping. It is a strict
low-level API. It does not accept eight loose Koota results in place of the
aggregate, two loose Manglik classifications in place of the comparison, raw
longitudes, charts, or a previously composed report.

The API revalidates both inputs as described below, copies them, and produces a
complete report. Incorrect types raise `TypeError`; malformed values raise
`ValueError`. It never returns an invalid report for strict caller-supplied
component data, silently drops a component, invokes the raw calculators as a
fallback, or repairs a field.

Its fail-fast validation workflow is exactly:

1. require both keyword arguments and validate the Ashtakoota outer type;
2. validate Ashtakoota JSON safety, mutable aliasing, field order, schema,
   status, Moon audits, Koota identifier order, and outer aggregate fields;
3. call `aggregate_ashtakoota_results` with the supplied Koota results and
   audit longitudes, then compare the authoritative regenerated scores,
   maximums, total, directions, and warnings to the supplied aggregate;
4. validate the Manglik outer type, JSON safety, mutable aliasing, field order,
   schema, status, nested classifications, and role metadata;
5. call `compare_manglik_classifications` with the supplied nested bride and
   groom identities, then compare the regenerated classifications, houses,
   pair category, comparison status, reasons, and metadata to the supplied
   comparison;
6. validate available cross-component schema and role facts; and
7. compose one complete report from independent copies.

Failure at any step raises immediately and later steps do not run.

#### Strict Report Serializer

`serialize_compatibility_report` accepts one complete validated Task 11.14
report. It strictly revalidates the entire report, revalidates the Koota
breakdown through the Task 11.12 strict aggregator, and reconstructs the
Task 11.13 comparison from the report's normalized Lagna/Mars audit fields.
It then returns a deep independent JSON-safe mapping in canonical key and
section order. The report intentionally stores component summaries rather
than duplicate full aggregate/comparison objects. The serializer does not
return a JSON string, write a file, call `json.dumps`, render HTML/PDF, or add
presentation formatting.

Wrong report types raise `TypeError`; malformed, invalid-status, wrong-version,
aliased, or non-JSON-safe reports raise `ValueError`. Serialization never
coerces an unsupported object, converts `NaN` to `None`, drops an unknown
field, fills a missing field, or changes component data.

Its workflow is exactly:

1. require a mapping with the 14 exact top-level fields in canonical order;
2. require complete technical status, exact schema/report identifiers,
   canonical sections/notes, valid metadata, and empty errors;
3. reject non-JSON-safe data and mutable aliasing before copying;
4. pass the report's Koota breakdown and summarized Moon longitudes through
   `aggregate_ashtakoota_results`, then compare its authoritative output to the
   Ashtakoota summary and Koota breakdown, while validating the separately
   preserved source `execution_mode` as either `raw_calculators` or
   `precomputed_results` rather than replacing it with the validator call's
   `precomputed_results` mode;
5. pass the summarized bride/groom Lagna and Mars longitudes through
   `classify_manglik` and `compare_manglik_classifications`, then compare the
   authoritative output to the Manglik summary;
6. revalidate validation counts, prefixed warnings, exclusion flags, field
   order, and every nested JSON-safe value; and
7. construct a new canonical mapping recursively, allocating a new mapping or
   list at every mutable path.

The serializer does not call the raw report composer and does not return the
input mapping itself.

### Chart-Based Composition Decision

Task 11.14 defines no chart-pair report API. A caller with existing Kundali
charts may call `classify_manglik_from_chart` separately for bride and groom,
call `compare_manglik_classifications`, and supply that complete comparison
with a complete Ashtakoota aggregate to the strict precomputed composer.

This task does not infer Moon longitude from a chart, search chart planets,
calculate a Kundali, or combine a chart-shaped API with six raw longitude
arguments. A dedicated chart orchestration convenience API is deferred unless
a later task specifies exact Moon extraction, chart validation, and provenance
requirements. Therefore Task 11.14 runtime tests do not test malformed chart
mappings; Task 11.13 retains sole responsibility for its chart adapter tests.

### Exact Report Composition Workflow

After obtaining or strictly validating the two components, the composer must:

1. verify the Ashtakoota calculation identifier, schema, status, canonical
   Koota order, directions, component count, scores, maximums, total, Moon
   audit longitudes, issues, warnings, and JSON safety;
2. verify the Manglik calculation identifier, schema, status, nested bride and
   groom classifications, roles, reference points, Mars houses, applicable
   houses, pair classification, comparison status, reasons, issues, warnings,
   and JSON safety;
3. preserve bride/groom roles without transposition, averaging, symmetry
   assumptions, or inference from gender or person data;
4. derive the bride and groom input summaries only from normalized component
   audit fields; on the raw path use the two direct classification results so
   valid audit values survive an invalid comparison, and on the strict path use
   the complete comparison's nested classifications;
5. copy the Ashtakoota summary, all eight Koota results, and Manglik summary
   without recalculating any value;
6. copy component issues and warnings into deterministic report-level paths;
7. derive only technical validation counts and complete/invalid report status;
8. allocate all lists and mappings independently; and
9. emit fields and sections in the canonical order below.

No output field may be derived from an astrology table or formula. The only
composer-derived values are report structure, technical status/counts, stable
section identifiers, copied input summaries, and documented exclusion notes.

### Canonical Report Sections and Order

The stable `sections` value is exactly:

```text
[
  "report_metadata",
  "input_summary",
  "ashtakoota_summary",
  "koota_breakdown",
  "manglik_summary",
  "validation_status",
  "errors",
  "warnings",
  "notes"
]
```

The order is part of the public contract. It must not depend on input mapping
order, calculator import order, caller-supplied precomputed order, dictionary
sorting, locale, or score. Every report includes all nine section identifiers,
including empty errors and warnings. A consumer maps them to report fields as
follows:

| Position | Section identifier | Authoritative report field(s) |
|---:|---|---|
| 1 | `report_metadata` | `schema_version`, `report_type`, `metadata` |
| 2 | `input_summary` | `bride`, `groom` |
| 3 | `ashtakoota_summary` | `ashtakoota` |
| 4 | `koota_breakdown` | `koota_results` |
| 5 | `manglik_summary` | `manglik` |
| 6 | `validation_status` | `status`, `validation` |
| 7 | `errors` | `errors` |
| 8 | `warnings` | `warnings` |
| 9 | `notes` | `notes` |

`sections` contains identifiers, not duplicate mutable section payloads. This
avoids two report paths that could diverge after caller mutation.

### Bride and Groom Input Summaries

The `bride` and `groom` mappings each expose exactly:

- `role`: `bride` or `groom`;
- `moon_sidereal_longitude`: the normalized Task 11.12 audit longitude or
  `None` when raw input is invalid;
- `lagna_sidereal_longitude`: the normalized longitude copied from that role's
  Task 11.13 nested classification or `None`;
- `mars_sidereal_longitude`: the normalized longitude copied from that role's
  Task 11.13 nested classification or `None`; and
- `manglik_reference_point`: `lagna` for a complete classification or an empty
  string when invalid.

No name, ID, gender, birth details, geographic coordinate, Rashi, Nakshatra,
Pada, or chart is invented or accepted. On the precomputed path, the composer
can validate role metadata and internal consistency but cannot prove that two
independently supplied components belong to the same real people. This
provenance limitation is explicit and must not be represented as a successful
cross-component identity check.

### Ashtakoota Summary and Koota Breakdown

The `ashtakoota` summary exposes exactly:

- `calculation`: `ashtakoota_aggregation`;
- `status`: copied component status;
- `bride_moon_longitude` and `groom_moon_longitude`: normalized audit values;
- `total_score`: copied exactly, including `0.0` and fractional values, or
  `None` for an invalid raw component;
- `total_maximum_score`: exactly `36.0`;
- `score_by_koota`: a fresh canonical-order mapping;
- `maximum_score_by_koota`: a fresh canonical-order mapping;
- `component_status_by_koota`: a fresh canonical-order mapping derived only by
  copying each Koota result's existing `status`;
- `koota_order`: the canonical eight identifiers;
- `execution_mode`: copied from Task 11.12 metadata; and
- `percentage_included`: always `false` under the current Task 11.12 contract.

There is no `percentage` or `percentage_score` field. The composer must not
calculate `total_score / 36`, round a percentage, or expose display formatting.
If a future aggregation schema adds an authoritative percentage, Task 11.14
requires a separately documented schema revision before including it.

For a complete report, the score, maximum, and component-status mappings each
contain exactly eight canonical entries. For an invalid raw report they copy
the structurally valid Task 11.12 data exactly: an input-validation failure may
have empty Koota results and score/status mappings, while a completed eight-
calculator execution with one or more invalid components may retain all eight
ordered audit results and `None` scores. The composer never fabricates missing
component results or fills an invalid mapping with defaults.

For a complete report, the top-level `koota_results` field is a deep copy of
exactly eight complete Task 11.12 component mappings in this order:

```text
varna, vashya, tara, yoni, graha_maitri, gana, bhakoot, nadi
```

Each result appears exactly once. The composer preserves the entire validated
component mapping, including its classification factors, direction, score,
maximum, errors, warnings, references, and metadata. It must not flatten,
rename, reinterpret, or independently verify an astrological matrix result.
For an invalid raw report, `koota_results` is instead an exact deep copy of the
invalid aggregate's existing zero-or-eight component list. Its section remains
present, but it is not a complete Koota breakdown.

### Manglik Summary

The `manglik` summary exposes exactly:

- `calculation`: `manglik_compatibility`;
- `status`: copied component status;
- `bride_classification` and `groom_classification`;
- `bride_reference_point` and `groom_reference_point`, both `lagna` for a
  complete result;
- `bride_mars_house` and `groom_mars_house`;
- `applicable_manglik_houses`: `[1, 4, 7, 8, 12]` as a fresh list;
- `pair_classification`: one Task 11.13 role-preserving identifier;
- `comparison_status`: `same_status` or `mixed_status`;
- `reasons`: the exact ordered Task 11.13 reason identifiers; and
- `validation_status`: `complete` or `invalid` copied from the component.

The summary has no score, maximum, percentage, severity, compatibility label,
cancellation, prediction, or advice field. `pair_classification` and
`comparison_status` are factual Task 11.13 categories, not suitability
judgements. `both_manglik` is not converted to a cancellation, and
`mixed_status` is not converted to failure.

### Technical Validation, Errors, Warnings, and Notes

The top-level `validation` mapping exposes exactly:

- `status`: `complete` or `invalid`;
- `is_valid`: `true` only when both components are complete and valid;
- `component_statuses`: `{ashtakoota: <status>, manglik: <status>}` in that
  order;
- `validated_components`: `[]`, `['ashtakoota']`, `['manglik']`, or both in
  canonical order, based only on structural validation;
- `expected_component_count`: `2`;
- `validated_component_count`: `0..2`;
- `error_count`; and
- `warning_count`.

Report-level errors copy component issues in this order: all Ashtakoota issues,
then raw bride-classification issues, raw groom-classification issues, and the
Manglik comparison issues. Fields are prefixed `ashtakoota.`,
`manglik.bride.`, `manglik.groom.`, or `manglik.comparison.` while the original
issue code, message key, severity, JSON-safe value, and copied metadata are
preserved. The composer does not deduplicate or suppress a comparison issue
merely because an underlying classification issue also exists. On the strict
path all components are complete, so errors are empty. Report-level warnings
use the same source order. Within a source result, its existing order is
preserved. The composer creates no astrological warning.

`MatchmakingCompatibilityReportIssue` uses the existing issue fields exactly:
`field`, `code`, `message_key`, `severity`, JSON-safe `value`, and newly
allocated JSON-safe `metadata`. Task 11.14 defines no human-language error
field.

The top-level `notes` list is always present and, for schema version `1.0`, is
exactly this ordered list of stable machine-readable identifiers:

```text
[
  "structured_report_only",
  "no_overall_compatibility_label",
  "no_combined_ashtakoota_manglik_score",
  "no_manglik_cancellation",
  "no_prediction_advice_or_remedies"
]
```

These notes document scope; they do not interpret a result. No localized prose
or caller-supplied note is accepted by Task 11.14.

### Strict Precomputed Ashtakoota Validation

Before composing from caller-supplied results, runtime must strictly validate
the outer Task 11.12 mapping and reuse
`aggregate_ashtakoota_results(ashtakoota["koota_results"], ...)` to revalidate
all eight component results. It must not reproduce individual Koota validation
or scoring.

Validation requires:

- a mapping with the exact current Task 11.12 top-level fields in canonical
  order and `calculation="ashtakoota_aggregation"`;
- `status="complete"`, empty errors, JSON-safe warnings/references, and the
  current matchmaking schema version;
- finite normalized bride and groom Moon longitudes;
- exactly eight Koota result mappings in canonical order;
- no duplicate, missing, or unexpected Koota identifier;
- every component status `complete`, exact canonical role/direction metadata,
  finite non-boolean score within its Koota bounds, and exact imported maximum;
- canonical-order score and maximum mappings with exactly one entry per Koota;
- total maximum exactly `36.0` and total score exactly equal to the strict
  reaggregated total with no new rounding or tolerance;
- metadata Koota order, count, validated count, aggregation method,
  percentage flag, interpretation flag, cancellation flag, and execution mode
  consistent with Task 11.12; and
- strict JSON-safe keys and values with no `NaN`, infinity, tuple, set, enum,
  dataclass, exception, callable, or unsupported object.

Wrong Koota input order is invalid even though Task 11.12's strict aggregator
can reorder loose component input. Report composition requires canonical
source order so serialized audit order is never caller-dependent. The strict
reaggregated result validates component rules, directions, bounds, maximums,
and total; the composer compares the supplied aggregate fields to that result
but preserves a valid supplied `raw_calculators` or `precomputed_results`
execution-mode identifier.

### Strict Precomputed Manglik Validation

Runtime must require a mapping with the exact current Task 11.13 compatibility
fields in canonical order. It revalidates the supplied nested bride and groom
classifications by calling `compare_manglik_classifications` and requires the
recomputed public comparison to match every authoritative supplied field.

Validation requires:

- `calculation="manglik_compatibility"`, `status="complete"`, empty errors,
  JSON-safe warnings/references, and the current schema version;
- two complete exact Task 11.13 classification mappings in bride/groom order;
- normalized finite Lagna and Mars longitudes and internally consistent Rashi
  indexes, Mars houses, binary categories, reason identifiers, and metadata;
- `lagna` as the only reference point for both roles;
- Mars houses in `1..12`, with classification consistent with imported
  `MANGLIK_HOUSES` through the public classifier;
- applicable houses exactly `[1, 4, 7, 8, 12]`;
- one exact pair classification, `same_status` or `mixed_status`, and the exact
  ordered reasons returned by the public comparator;
- metadata role order exactly bride then groom, scoring disabled, severity
  disabled, cancellation disabled, divisional charts disabled, and
  Ashtakoota recalculation disabled; and
- strict JSON-safe keys and values with no non-finite or unsupported object.

The composer does not independently classify a house or reconstruct a pair
category. The public Task 11.13 comparator is the authority. Unknown category
aliases, Moon/Venus reference points, house `0`/`13`, house `2` classified as
Manglik, altered reasons, or a mismatched role category are rejected rather
than coerced.

### Cross-Component, Aliasing, and Version Validation

The precomputed composer validates cross-component facts that are actually
available:

- bride/groom role order is preserved in both components;
- Ashtakoota direction metadata retains its documented bride/groom or
  `person_a`/`person_b` mapping;
- Manglik metadata role order is bride then groom; and
- all component schema versions equal `MATCHMAKING_SCHEMA_VERSION`.

It must not claim to match person IDs because neither completed component
contract contains a shared person identifier. It also cannot compare Moon
longitude to Lagna/Mars longitude as identity evidence. A future provenance
contract requires a new version.

Caller-supplied precomputed component trees and serialized report trees must
not contain the same mutable list or mapping object reachable through two
different semantic paths, either within one component or across both
components. Such aliasing raises `ValueError` with deterministic path metadata;
it is not silently broken only during copying. Valid output nevertheless deep
copies every structure so no mutable identity is shared between source input,
summary mappings, Koota breakdown, nested metadata, issue values, prior calls,
or later calls.

Task 11.14 defines `COMPATIBILITY_REPORT_SCHEMA_VERSION` equal to the current
`MATCHMAKING_SCHEMA_VERSION` (`"1.0"`) and stable report type
`matchmaking_compatibility_report`. Both appear at top level and in metadata.
The current strict APIs reject missing, unknown, older, or newer component and
report versions. A future version may add fields only through an explicit
schema revision; version `1.0` fields, identifiers, and ordering must not be
renamed or repurposed.

### Failure and Exception Propagation

The raw composer distinguishes expected invalid inputs from unexpected
failures:

- ordinary missing, boolean, non-real, `NaN`, and infinity values are handled
  by the existing safe calculators and yield an invalid report;
- component issues remain visible with deterministic section-prefixed paths;
- a component mapping with ordinary `status="invalid"` makes the report
  invalid, even if the other component is complete;
- a malformed result returned by a completed public calculator is a
  programming contract violation and raises `TypeError` or `ValueError`; and
- an unexpected exception from any calculator, validator, copying operation,
  or invariant propagates immediately unchanged.

Execution is fail-fast for exceptions. If Ashtakoota raises, no Manglik call is
made. If bride classification raises, groom classification and comparison are
not called. If groom classification raises, comparison is not called. If the
comparator raises, no report is returned. Runtime must not catch `Exception`,
continue after a raised dependency, fabricate a component, suppress an error,
or return a partial report.

For strict precomputed composition and serialization:

- wrong outer/component types, including a non-mapping, raise `TypeError`;
- missing fields, invalid status, invalid total/maximum, wrong count/order,
  duplicate/missing/unexpected Koota, invalid score, malformed Manglik data,
  role mismatch, schema mismatch, aliasing, or non-JSON-safe values raise
  `ValueError`;
- messages identify the component and validation aspect in deterministic
  section/field order; and
- no exception is also converted into a returned invalid report.

### Public Immutable Report Contract

Task 11.14 follows the existing matchmaking typed-mapping convention. It does
not introduce a dataclass, tuple result, Pydantic API schema, report template,
ORM object, or alternate serialization architecture. The public report and all
nested values are immutable after construction by contract, while newly
allocated mutable Python mappings/lists preserve existing caller ergonomics.

`MatchmakingCompatibilityReport` exposes exactly these top-level fields in
this stable order:

1. `schema_version`: `"1.0"`;
2. `report_type`: `matchmaking_compatibility_report`;
3. `status`: `complete` or `invalid`, meaning technical state only;
4. `bride`: the copied normalized input summary;
5. `groom`: the copied normalized input summary;
6. `ashtakoota`: the Ashtakoota summary;
7. `koota_results`: the ordered deep-copied eight-Koota breakdown;
8. `manglik`: the Manglik summary;
9. `validation`: the technical validation summary;
10. `errors`: deterministic copied issues;
11. `warnings`: deterministic copied warnings;
12. `notes`: the five stable scope identifiers;
13. `sections`: the nine canonical section identifiers; and
14. `metadata`: deterministic report metadata.

The report does not embed an additional full `MatchmakingAshtakootaResult` or
`ManglikCompatibilityResult`. `ashtakoota` and `manglik` are the exact
report-level summaries defined above; `koota_results` preserves the full
individual Koota mappings. The serializer reconstitutes strict validation from
these authoritative audit fields without adding a duplicated mutable component
tree.

Metadata exposes at least component `matchmaking_compatibility_report`, schema
version, `deterministic=true`, report type, canonical section order, expected
section count `9`, component order `['ashtakoota', 'manglik']`, expected
component count `2`, validated component count, source calculation identifiers,
`structured_only=true`, `overall_compatibility_label_included=false`,
`combined_score_included=false`, `percentage_included=false`,
`interpretation_included=false`, `recommendations_included=false`,
`remedies_included=false`, and `rendering_included=false`.

Repeated equivalent calls compare equal before caller mutation. Every output
mapping/list, including summaries, Koota results, score mappings, maximum
mappings, component statuses, applicable houses, reasons, issues, warnings,
notes, sections, and metadata, is independently allocated. Mutation of any
returned path cannot affect another path, source component, previous call,
future call, imported constant, or manifest.

Every complete or invalid raw report must pass
`json.dumps(report, allow_nan=False)`. All mapping keys and identifiers are
strings; scores and longitudes are finite numbers or `None`; no tuple, set,
enum instance, dataclass instance, exception object, callable, `NaN`, or
infinity may escape. Serialization preserves canonical key and list order.

The runtime task must add only stable public exports for the report schema/type
constants, section/component order constants, typed issue/summary/metadata/
report mappings, raw composer, strict precomputed composer, and strict mapping
serializer. All existing Task 11.1-11.13 imports and behavior remain unchanged.

### Explicitly Excluded Behavior

Task 11.14 explicitly excludes:

- every new or copied Koota classification, mapping, matrix, boundary,
  direction, formula, score, total, or maximum rule;
- every new or copied Manglik house, reference-point, classification,
  comparison, cancellation, exception, severity, or intensity rule;
- Manglik cancellation, double-Manglik cancellation, and all planetary or
  divisional exceptions;
- a Manglik score, combined Ashtakoota-plus-Manglik score, score adjustment,
  bonus, penalty, weighted total, normalized total, or percentage;
- an overall compatibility label, pass/fail threshold, suitability judgement,
  marriage recommendation, rejection, or advice;
- remedies, predictions, Dasha analysis, Navamsha interpretation, horoscope
  synthesis, Gotra, transit analysis, or AI-generated narrative;
- localization prose, presentation formatting, UI components, charts,
  templates, HTML, PDF generation, or file output;
- FastAPI routes, Pydantic API schemas, database persistence, analytics,
  caching, external services, or network calls;
- chart-pair convenience composition and birth-detail/Kundali calculation; and
- Task 11.15 serialization hardening or any later Sprint task.

The mapping serializer in this task establishes deterministic report copying;
it does not implement the broader cross-module serialization hardening reserved
for Task 11.15.

### Required Runtime Tests

Task 11.14 runtime implementation is not complete until focused tests cover:

- raw composition through the real public Ashtakoota calculator, two real
  Manglik classifiers, and real Manglik comparator, each called exactly once
  in documented order without copied calculation logic;
- strict composition from one real complete Ashtakoota aggregate and one real
  complete Manglik comparison;
- exact top-level field order, nine-section order, two-component order, and
  exact canonical eight-Koota order;
- every Koota included once, all component statuses, individual maximums
  `1.0..8.0`, and total maximum `36.0`;
- a structurally valid precomputed full `36.0` Ashtakoota fixture, all-zero
  `0.0` fixture, and fractional fixture, preserving totals without rounding;
- independent proof that the report total and Koota mappings equal the
  authoritative aggregate rather than a composer calculation;
- explicit absence of percentage and proof that no division by `36.0` occurs;
- all four Manglik pair classifications, both comparison statuses, both role
  orders of mixed status, and exact reason ordering with no score or
  cancellation;
- normalized input summaries for `0°`, `360°`, `-360°`, finite negative, and
  greater-than-`360°` Moon, Lagna, and Mars longitudes;
- every exact `30°` Rashi boundary relevant to raw Lagna/Mars classification;
- missing values, booleans, non-real values, `NaN`, and both infinities for all
  six raw inputs, with deterministic component/role issue ordering;
- one ordinary invalid component while the other is complete, both invalid,
  no partial-success status, and retained audit data without invented values;
- a unique injected exception at each raw dependency call, proving unchanged
  propagation, fail-fast order, and no returned report;
- strict rejection of missing Ashtakoota or Manglik input, wrong outer and
  component types, invalid/incomplete statuses, errors on a complete component,
  and wrong calculation identifiers;
- strict rejection of invalid/non-finite/out-of-range Ashtakoota scores,
  incorrect total, incorrect `36.0` maximum, wrong component maximum, wrong
  Koota count, duplicate/missing/unexpected name, and wrong source order;
- strict rejection of malformed direction metadata, score mappings, maximum
  mappings, component statuses, Koota metadata, and execution metadata;
- strict rejection of malformed Manglik nested classifications, non-binary or
  inconsistent category, Moon/Venus/unknown reference point, invalid Mars
  house, altered applicable houses, wrong pair category, comparison status,
  reasons, role order, or exclusion flags;
- strict rejection of mismatched schema/report versions, wrong report type,
  missing/unexpected/reordered report fields, sections, notes, or metadata;
- strict rejection of `NaN`, infinity, non-string mapping keys, tuples, sets,
  enums, dataclasses, exceptions, callables, unsupported objects, and mutable
  aliasing within or across caller-supplied trees;
- proof that cross-component person identity is not falsely claimed when no
  shared person ID exists;
- strict serializer validation and a canonical deep-copied mapping equal to a
  complete source report before mutation;
- deterministic equality across repeated raw, precomputed, and serialization
  calls; caller-input non-mutation; immutable-after-construction public
  expectations; deep-copy isolation; and independent mutable collections at
  every nested path;
- `json.dumps(..., allow_nan=False)` for complete and invalid raw reports;
- exact absence of overall label, pass/fail, combined score, Manglik score,
  percentage, interpretation, advice, recommendation, remedy, prediction,
  cancellation, UI, PDF, API, and chart-composition fields;
- absence of a public chart-pair composer and no malformed-chart tests beyond
  Task 11.13 regressions;
- stable public exports for constants, typed contracts, both composers, and
  serializer;
- backward compatibility with every Task 11.12 and 11.13 public import and
  direct call; and
- focused report tests followed by complete matchmaking, Ashtakoota, Manglik,
  Rashi, Kundali, and full project regression suites proving existing outputs
  remain unchanged.

### Documentation Progress Rules

Task 11.14 runtime completion is recorded after the three documented APIs,
strict validators, public exports, focused tests, and required regressions are
complete. `docs/MASTER.md` now records Task 11.14 as completed. Task 11.15
remains the next incomplete task and is not begun here.

### Completion and Verification

Task 11.14 is runtime-complete. The implementation adds raw six-longitude
composition, strict composition from completed Ashtakoota and Manglik results,
and strict deterministic report serialization. It preserves canonical report
and Koota ordering, delegates all calculation and revalidation to the existing
Task 11.12 and Task 11.13 public contracts, rejects malformed or aliased strict
inputs, and adds no interpretation, combined score, percentage, cancellation,
recommendation, or rendering behavior.

Verification totals recorded for the implementation task:

- focused Compatibility / Report Composition suite: `95 passed`;
- Ashtakoota and Manglik regression suites: `413 passed`;
- complete matchmaking suite: `2560 passed`;
- Rashi and Kundali regression suite: `102 passed`; and
- complete project suite: `3528 passed, 13 skipped, 20 subtests passed`.

The skips remain the repository's pre-existing manual-reference validation
placeholders. Task 11.14 does not enable or alter them. Work stops here before
Task 11.15.

## Task 11.15 - Serialization and Compatibility Hardening

Status: **Complete**

### Purpose and Scope

Task 11.15 is the final Sprint 11 hardening task. It defines one stable,
deterministic serialization boundary for every completed matchmaking result
family so downstream API, UI, CLI, storage, and report consumers receive
canonical JSON-safe data without learning private Python implementation
details.

The task covers only structural validation, recursive copying, stable schema
identifiers, field ordering, mutation isolation, and compatibility regression.
It does not calculate, reclassify, reinterpret, repair, or migrate astrology
data. Every classification, matrix, direction, score, total, Mars house, and
report fact remains owned by Tasks 11.1 through 11.14.

The covered public families are:

- matchmaking person, ordered pair, generic result envelope, person
  validation, and pair validation;
- Nakshatra identity and ordered pair context;
- Varna, Vashya, Tara, Yoni, Graha Maitri, Gana, Bhakoot, and Nadi Koota
  results;
- Ashtakoota aggregate results;
- Manglik classification and bride/groom comparison results; and
- Compatibility / Report Composition results.

Identity and relationship mappings nested inside these families are validated
and copied as part of their owning result. This task does not expose a second
public serializer for every private or nested helper mapping.

### BhaktiAstro Project Decisions

The source-of-truth hardening decisions are:

- `MATCHMAKING_SCHEMA_VERSION` remains exactly `"1.0"`;
- `COMPATIBILITY_REPORT_SCHEMA_VERSION` remains exactly `"1.0"` and equal to
  `MATCHMAKING_SCHEMA_VERSION`;
- all completed result families participate in the same Sprint 11 schema
  generation, while each retains its existing calculation, component, Koota,
  or report identifier;
- canonical serialization is recursive, strict, validating, and copying; it
  is not equivalent to shallow `dict(result)` conversion;
- existing calculator and factory return values remain built-in mappings and
  lists for backward compatibility, but are immutable after construction by
  public ownership contract;
- the serializer never mutates that runtime snapshot and returns a fresh,
  caller-owned, mutable built-in `dict`/`list` tree;
- no calculator is retrofitted to return `MappingProxyType`, frozen
  dataclasses, tuples, Pydantic models, or another incompatible container;
- unsupported Python values are rejected, not stringified, converted to
  `None`, silently dropped, or repaired;
- tuples, enums, dataclasses, sets, bytes, date/time objects, exceptions,
  callables, and arbitrary objects are rejected;
- ordinary `Mapping` inputs, including mapping proxies or subclasses, are
  accepted only at mapping fields, strictly validated in iteration order, and
  copied to plain built-in dictionaries; they never escape in output;
- `NaN` and positive or negative infinity are rejected at every depth;
- negative floating-point zero is serialized canonically as `0.0`;
- finite integer fields remain integers, finite float fields are emitted as
  floats, and booleans are never accepted as numeric values;
- no numeric score, longitude, percentage, or total is rounded by Task 11.15;
- aliases, deprecated field names, unknown fields, missing fields, reordered
  contractual fields, shared mutable input paths, and cyclic input are rejected;
- empty `errors` and `warnings` lists remain present when defined by the family;
- `None` is permitted only at fields already declared optional by the existing
  public typed contract and only in a state where that contract permits it;
- no deserialization, hydration, schema migration, JSON text generation,
  persistence, or golden-payload migration framework is included; and
- serialization introduces no overall label, verdict, interpretation,
  recommendation, prediction, remedy, or presentation data.

The phrase "immutable runtime result" in this task means that a completed
factory/calculator result is a read-only snapshot by public contract. Python
callers can still mutate the returned built-in collections, as they could
before Task 11.15, but doing so invalidates the snapshot. The strict serializer
detects malformed mutation. Actual container freezing would break existing
callers and is explicitly excluded.

### Selected Serialization Architecture

Runtime implementation adds one small module at the matchmaking serialization
boundary. It contains one internal recursive JSON validator/copier and a small
registry of exact family contracts. It must reuse current public constants,
typed mappings, Koota manifest, strict Ashtakoota aggregation, Manglik
comparison validation, and Compatibility Report serializer rather than copy
astrology logic.

The stable keyword-only public APIs are:

```python
def serialize_matchmaking_person(*, result: object) -> dict[str, MatchmakingJsonValue]: ...
def serialize_matchmaking_pair(*, result: object) -> dict[str, MatchmakingJsonValue]: ...
def serialize_matchmaking_result(*, result: object) -> dict[str, MatchmakingJsonValue]: ...
def serialize_matchmaking_person_validation(*, result: object) -> dict[str, MatchmakingJsonValue]: ...
def serialize_matchmaking_pair_validation(*, result: object) -> dict[str, MatchmakingJsonValue]: ...
def serialize_matchmaking_nakshatra_identity(*, result: object) -> dict[str, MatchmakingJsonValue]: ...
def serialize_matchmaking_nakshatra_pair_context(*, result: object) -> dict[str, MatchmakingJsonValue]: ...
def serialize_koota_result(*, result: object) -> dict[str, MatchmakingJsonValue]: ...
def serialize_ashtakoota_result(*, result: object) -> dict[str, MatchmakingJsonValue]: ...
def serialize_manglik_classification_result(*, result: object) -> dict[str, MatchmakingJsonValue]: ...
def serialize_manglik_compatibility_result(*, result: object) -> dict[str, MatchmakingJsonValue]: ...
```

`serialize_compatibility_report(*, report: object)` remains the sole report
serializer and retains its exact Task 11.14 signature and complete-report-only
semantics. It is hardened through shared internal primitives only when doing so
does not alter its output or exceptions. Task 11.15 must not add an alias taking
`result=` for that function.

`serialize_koota_result` strictly dispatches only by the existing `koota`
identifier and supports all eight exact values. It does not guess a family from
field presence. No generic public `serialize_any`, mode flag, positional API,
or implicit converter is added. Internal registry and recursive helpers remain
private. The constants `MATCHMAKING_SERIALIZATION_SCHEMA_VERSION` and
`MATCHMAKING_SERIALIZATION_FAMILIES` are public, additive exports; the former
equals `MATCHMAKING_SCHEMA_VERSION`, and the latter is an immutable ordered
tuple of the family identifiers documented below.

Direct `json.dumps(runtime_result, allow_nan=False)` remains possible for
unchanged valid calculator output, but it is not the canonical validation and
copying API. Direct `dict(runtime_result)` is shallow and is explicitly not a
supported substitute. These helpers return mappings only. Producing JSON text,
choosing indentation or key sorting, encoding bytes, writing files, and
selecting transport content types belong to callers or later layers.

### Canonical Family Identifiers and Status Values

The ordered `MATCHMAKING_SERIALIZATION_FAMILIES` value is exactly:

```text
matchmaking_person
matchmaking_pair
matchmaking_result
matchmaking_person_validation
matchmaking_pair_validation
matchmaking_nakshatra_identity
matchmaking_nakshatra_pair_context
varna
vashya
tara
yoni
graha_maitri
gana
bhakoot
nadi
ashtakoota_aggregation
manglik_classification
manglik_compatibility
matchmaking_compatibility_report
```

The serializer never renames identifiers. Stable category and status values
are the exact existing exported values:

- foundation result statuses: `not_evaluated`, `partial`, `complete`, and
  `invalid`;
- calculation result statuses: `complete` or `invalid` where the owning result
  defines `status`;
- validation and identity validity: JSON booleans in the existing `is_valid`
  field, not an invented status;
- Varna: `shudra`, `vaishya`, `kshatriya`, `brahmin`;
- Vashya: `chatushpada`, `manava`, `jalachara`, `vanachara`, `keeta`;
- Tara: `janma`, `sampat`, `vipat`, `kshema`, `pratyari`, `sadhaka`, `vadha`,
  `mitra`, `ati_mitra`;
- Yoni categories: `horse`, `elephant`, `sheep`, `serpent`, `dog`, `cat`,
  `rat`, `cow`, `buffalo`, `tiger`, `deer`, `monkey`, `mongoose`, `lion`;
- Yoni sexes: `male`, `female`; Yoni relationships: `same`, `friendly`,
  `neutral`, `enemy`, `sworn_enemy`;
- Graha Maitri lords: `sun`, `moon`, `mars`, `mercury`, `jupiter`, `venus`,
  `saturn`; permanent directional relationships remain `friend`, `neutral`, or
  `enemy`; combined identifiers are `same_lord`, `mutual_friend`,
  `friend_neutral`, `mutual_neutral`, `friend_enemy`, `neutral_enemy`, and
  `mutual_enemy`;
- Gana: `deva`, `manushya`, `rakshasa`; relationships: `same_gana` or
  `mixed_gana`;
- Bhakoot relationship: `compatible` or `dosha`, with existing pair and
  position identifiers unchanged;
- Nadi: `adi`, `madhya`, `antya`; relationships: `same_nadi` or
  `different_nadi`;
- Manglik classification: `manglik`, `non_manglik`; pair classification:
  `both_manglik`, `both_non_manglik`,
  `bride_manglik_groom_non_manglik`, or
  `bride_non_manglik_groom_manglik`; comparison status: `same_status` or
  `mixed_status`; and
- report status: `complete` or `invalid` as a technical status, although the
  existing strict report serializer accepts only `complete`.

Empty-string category placeholders are permitted only in existing invalid
result states. A complete result containing an empty, aliased, differently
cased, or unknown category is malformed. The hardening layer never casefolds,
trims, aliases, translates, or guesses a category or status.

Compatibility-domain identifiers also remain exact: Vashya `attraction`, Tara
`destiny`, Yoni `intimacy`, Graha Maitri `mental_compatibility`, Gana
`temperament`, Bhakoot `family_welfare`, and Nadi
`physiological_compatibility`. Varna retains its existing result shape without
an added compatibility-domain field.

### Canonical Foundation and Context Contracts

The following exact field order is contractual:

| Family | Exact top-level fields in order |
|---|---|
| `matchmaking_person` | `person_id`, `name`, `birth_date`, `birth_time`, `latitude`, `longitude`, `timezone`, `rashi`, `nakshatra`, `nakshatra_pada`, `lagna`, `metadata` |
| `matchmaking_pair` | `person_a`, `person_b`, `metadata` |
| `matchmaking_result` | `matchmaking_id`, `status`, `score`, `maximum_score`, `percentage`, `factors`, `warnings`, `references`, `notes`, `metadata` |
| `matchmaking_person_validation` | `is_valid`, `errors`, `warnings`, `normalized_value`, `metadata` |
| `matchmaking_pair_validation` | `is_valid`, `errors`, `warnings`, `normalized_value`, `metadata` |
| `matchmaking_nakshatra_identity` | `is_valid`, `name`, `index`, `pada`, `source_person_id`, `errors`, `warnings`, `metadata` |
| `matchmaking_nakshatra_pair_context` | `is_valid`, `person_a`, `person_b`, `forward_distance`, `reverse_distance`, `same_nakshatra`, `same_pada`, `errors`, `warnings`, `metadata` |

Nested `person_a`, `person_b`, `normalized_value`, and Nakshatra identity values
must have their own exact owning-family field order. Person and pair metadata
fields remain `component`, `schema_version`, `deterministic`,
`calculation_complete`, `source_components`. Validation metadata remains
`component`, `schema_version`, `deterministic`, `issue_count`. Nakshatra
metadata remains `component`, `schema_version`, `deterministic`,
`nakshatra_count`, `index_base`, `calculation_scope`.

Foundation optional `latitude`, `longitude`, and `nakshatra_pada` may be
`None`. Generic result `score`, `maximum_score`, and `percentage` may be `None`
for unevaluated or partial states. Nakshatra `index` and `pada`, pair distances,
and same-value flags may be `None` only in the invalid/unknown states already
emitted by Task 11.3. Empty factors, warnings, references, notes, errors, and
source-component collections remain arrays rather than `None`.

Task 11.15 does not tighten the permissive Task 11.1 factory normalization or
change its signatures. The serializers validate the resulting canonical
snapshot; they do not rerun factories to repair caller mutations.

### Canonical Individual Koota Contracts

All individual Koota mappings begin with their exact current fields and retain
their existing nested identity, direction, factor, issue, reference, and
metadata structures. Exact top-level field order is:

| Koota | Exact top-level fields in order |
|---|---|
| Varna | `koota`, `status`, `score`, `maximum_score`, `person_a_varna`, `person_b_varna`, `direction`, `factors`, `errors`, `warnings`, `references`, `metadata` |
| Vashya | `koota`, `compatibility_domain`, `status`, `score`, `maximum_score`, `bride_vashya`, `groom_vashya`, `direction`, `factors`, `errors`, `warnings`, `references`, `metadata` |
| Tara | `koota`, `compatibility_domain`, `status`, `score`, `maximum_score`, `person_a_nakshatra`, `person_b_nakshatra`, `direction`, `bride_to_groom`, `groom_to_bride`, `same_nakshatra`, `same_pada`, `factors`, `errors`, `warnings`, `references`, `metadata` |
| Yoni | `koota`, `compatibility_domain`, `status`, `score`, `maximum_score`, `person_a_nakshatra`, `person_b_nakshatra`, `direction`, `bride_yoni`, `groom_yoni`, `relationship`, `same_nakshatra`, `same_pada`, `same_yoni`, `factors`, `errors`, `warnings`, `references`, `metadata` |
| Graha Maitri | `koota`, `compatibility_domain`, `status`, `score`, `maximum_score`, `bride_moon_rashi`, `groom_moon_rashi`, `direction`, `bride_to_groom_relationship`, `groom_to_bride_relationship`, `combined_relationship`, `same_lord`, `factors`, `errors`, `warnings`, `references`, `metadata` |
| Gana | `koota`, `compatibility_domain`, `status`, `score`, `maximum_score`, `person_a_nakshatra`, `person_b_nakshatra`, `direction`, `bride_gana`, `groom_gana`, `relationship`, `same_nakshatra`, `same_pada`, `same_gana`, `factors`, `errors`, `warnings`, `references`, `metadata` |
| Bhakoot | `koota`, `compatibility_domain`, `status`, `score`, `maximum_score`, `bride_moon_rashi`, `groom_moon_rashi`, `direction`, `bride_to_groom_distance`, `groom_to_bride_distance`, `pair_identifier`, `position_pair`, `relationship`, `same_rashi`, `bhakoot_dosha`, `factors`, `errors`, `warnings`, `references`, `metadata` |
| Nadi | `koota`, `compatibility_domain`, `status`, `score`, `maximum_score`, `person_a_nakshatra`, `person_b_nakshatra`, `direction`, `bride_nadi`, `groom_nadi`, `relationship`, `same_nakshatra`, `same_pada`, `same_nadi`, `nadi_dosha`, `factors`, `errors`, `warnings`, `references`, `metadata` |

The `koota` identifiers and exact maximums remain:

```text
varna=1.0, vashya=2.0, tara=3.0, yoni=4.0,
graha_maitri=5.0, gana=6.0, bhakoot=7.0, nadi=8.0
```

For `status="complete"`, `score` must be a finite float from `0.0` through the
exact maximum, errors must be empty, categories must be canonical, direction
must match the owning result contract, and duplicated summary fields must be
internally consistent. For `status="invalid"`, `score` must be `None`, at least
one deterministic error must be present, and existing empty-string/`None`
placeholders are retained. No partial individual Koota score is serialized.

Koota metadata has exact common prefix `component`, `schema_version`,
`deterministic`, `calculation`, `maximum_score`. Remaining exact fields are:

- Varna: `directional`;
- Vashya: `compatibility_domain`, `directional`;
- Tara: `compatibility_domain`, `directional`, `nakshatra_count`, `index_base`;
- Yoni: Tara fields plus `symmetric` before Nakshatra count/index;
- Graha Maitri: `compatibility_domain`, `directional`, `symmetric`,
  `relationship_type`, `rashi_count`, `index_base`;
- Gana: `compatibility_domain`, `directional`, `symmetric`,
  `nakshatra_count`, `index_base`;
- Bhakoot: `compatibility_domain`, `directional`, `symmetric`,
  `relationship_type`, `rashi_count`, `index_base`; and
- Nadi: `compatibility_domain`, `directional`, `symmetric`,
  `nakshatra_count`, `index_base`.

Nested identity and relationship field order remains exactly the order declared
by the existing public TypedDict. The hardening implementation must derive
these contracts from the current public types or centralized structural
constants rather than create alternate astrology-facing models. Factors,
errors, warnings, and references are always fresh arrays; direction and
metadata are fresh mappings.

### Canonical Ashtakoota Aggregate Contract

`serialize_ashtakoota_result` accepts one exact `MatchmakingAshtakootaResult`
mapping with fields in this order:

```text
calculation
status
bride_moon_longitude
groom_moon_longitude
koota_results
score_by_koota
maximum_score_by_koota
total_score
total_maximum_score
errors
warnings
references
metadata
```

`calculation` remains `ashtakoota_aggregation`. A complete result contains
exactly eight complete Koota results in canonical order `varna`, `vashya`,
`tara`, `yoni`, `graha_maitri`, `gana`, `bhakoot`, `nadi`. Score, maximum, and
status-derived mappings preserve that order. Each Koota appears once. The
serializer must reuse `aggregate_ashtakoota_results` for complete component
revalidation and compare the authoritative aggregate to the supplied mapping;
it must preserve a valid source execution mode of `raw_calculators` or
`precomputed_results`.

`total_maximum_score` remains exactly `36.0`. A complete `total_score` is the
exact existing `math.fsum` component total without new rounding. It must equal
the canonical-order component sum and lie in `0.0..36.0`. An invalid raw
aggregate retains its existing zero-or-eight audit components, `None` total,
errors, and validation count; hardening validates structure without inventing
missing components or a partial total.

Aggregate metadata remains exactly `component`, `schema_version`,
`deterministic`, `execution_mode`, `koota_order`, `expected_koota_count`,
`validated_koota_count`, `total_maximum_score`, `aggregation_method`,
`percentage_included`, `interpretation_included`, `cancellation_included`.
`percentage_included` remains false. Serialization does not introduce a
percentage or independently sum or score Kootas.

### Canonical Manglik Contracts

`serialize_manglik_classification_result` accepts fields in this exact order:

```text
calculation, status, classification, reference_point,
lagna_sidereal_longitude, mars_sidereal_longitude,
lagna_rashi_index, mars_rashi_index, mars_house,
applicable_manglik_houses, reason, errors, warnings, references, metadata
```

`calculation` remains `manglik_classification`; reference point remains
`lagna`; applicable houses remain `[1, 4, 7, 8, 12]`; classification remains
binary. Complete classification fields must exactly match a public
`classify_manglik` revalidation from the audited finite longitudes. Invalid
classification retains the exact existing safe placeholders and issues.

`serialize_manglik_compatibility_result` accepts fields in this exact order:

```text
calculation, status, bride_manglik, groom_manglik,
bride_classification, groom_classification,
bride_reference_point, groom_reference_point,
bride_mars_house, groom_mars_house, applicable_manglik_houses,
pair_classification, comparison_status, reasons,
errors, warnings, references, metadata
```

`calculation` remains `manglik_compatibility`. A complete comparison is
revalidated through `compare_manglik_classifications`; all duplicated category,
reference-point, house, applicable-house, pair, comparison-status, reason, and
role fields must equal the authoritative result. An invalid comparison retains
the public safe result shape and does not become complete during serialization.

Classification metadata remains exactly `component`, `schema_version`,
`deterministic`, `calculation`, `house_system`, `house_numbering`,
`reference_points`, `applicable_manglik_houses`, `classification_mode`,
`comparison_mode`, `scoring_included`, `severity_included`,
`cancellation_rules_included`, `divisional_charts_included`,
`ashtakoota_recalculated`. Compatibility metadata adds `role_order` then
`same_mixed_comparison_symmetric`. No score, cancellation, severity, or
interpretation field is added.

### Canonical Compatibility Report Contract

The existing `serialize_compatibility_report` and Task 11.14 contract remain
authoritative. The exact report field order remains:

```text
schema_version, report_type, status, bride, groom, ashtakoota,
koota_results, manglik, validation, errors, warnings, notes, sections, metadata
```

The report type remains `matchmaking_compatibility_report`; schema version
remains `1.0`; accepted serialization status remains `complete`; sections
remain, in order, `report_metadata`, `input_summary`, `ashtakoota_summary`,
`koota_breakdown`, `manglik_summary`, `validation_status`, `errors`, `warnings`,
`notes`. The canonical eight-Koota order, five notes, two component order, all
summaries, metadata, empty errors, and exclusion flags remain unchanged.

Task 11.15 may route its recursive JSON checks and fresh-copy construction
through the shared internal helper only if byte-for-byte-equivalent JSON data,
mapping order, exception types, and Task 11.14 public behavior remain
unchanged. It must not loosen complete-only report serialization, add a second
report schema, or introduce compatibility interpretation.

### Validation Issue, Warning, and Metadata Contract

Every issue mapping has exact fields in order:

```text
field, code, message_key, severity, value, metadata
```

`severity` is `error` or `warning`; `field`, `code`, and `message_key` are
strings; `value` is a recursively validated JSON-safe value or `None`; and
`metadata` is a fresh string-keyed JSON-safe mapping. Existing issue codes,
message keys, prefixes, source ordering, and severity are preserved. The
serializer does not localize messages, turn issues into strings, deduplicate
them, sort them, or discard them.

Errors precede warnings only where their owning contract already places the
arrays that way. Within each list, existing deterministic order is stable.
Empty issue arrays remain `[]`; neither missing arrays nor `None` substitutes
are accepted.

All metadata mappings require exact current fields and order, current
`schema_version`, canonical `component`/`calculation` identifiers, and
`deterministic=true`. Metadata is structural and factual only. Unknown metadata
keys are rejected in schema `1.0`; additive metadata is not silently accepted
under the same family contract merely because a consumer might ignore it.

### Recursive JSON-Safe Copying Rules

Canonical serialized output permits only:

- `None` at explicitly optional fields;
- strings;
- JSON booleans at boolean fields;
- finite built-in integers at integer fields;
- finite built-in floats at float fields;
- newly allocated built-in lists; and
- newly allocated built-in dictionaries with string keys.

Validation occurs before output construction in deterministic depth-first,
field-order traversal. At every depth:

- `NaN`, positive infinity, and negative infinity raise `ValueError`;
- a boolean in an integer or float field raises `TypeError`;
- a non-string mapping key raises `ValueError`;
- tuple, set, frozenset, bytes, bytearray, memoryview, enum instance,
  dataclass instance, date/time/datetime, exception, callable, non-mapping
  custom container, and arbitrary object raise `TypeError`;
- a shared mutable list or mapping reachable by two semantic paths raises
  `ValueError` identifying both deterministic paths;
- a direct or indirect cycle raises `ValueError` identifying the first and
  repeated paths; and
- no `str(value)`, `list(value)`, `dict(value)`, enum `.value`, dataclass
  conversion, or fallback coercion is attempted.

Plain tuples are rejected rather than converted because canonical array fields
are already emitted as lists. Imported immutable tuple constants are never
embedded directly; serializers allocate lists where the result contract uses
arrays. Values implementing `Mapping`, including a mapping proxy or custom
mapping, are accepted only where a mapping is required, must expose the exact
contractual key order, and are copied recursively into plain dictionaries.
Iteration/access exceptions propagate unchanged. List subclasses are accepted
only at list fields and copied to plain lists. Neither custom container type is
preserved in output.

Every call allocates a fresh root and fresh nested collection at every path.
No output path shares a mutable object with the runtime result, another path in
the same output, a previous/future serialization, another calculator result,
or a module-level constant. `json.dumps(serialized, allow_nan=False)` must
succeed without a custom encoder, `default=`, key sorting, or non-standard
number support.

### Numeric, Optional, and Score Rules

Numeric validation is field-specific:

- indexes, counts, ranks, houses, Pada, and distance fields require built-in
  integers and reject booleans;
- longitude, degree, score, maximum, percentage, and total fields require a
  finite real number matching the owning public contract and serialize as
  built-in floats;
- an exact integer supplied at a float field may be normalized to the
  equivalent float only when the existing public result type already accepts
  real numbers; this is the sole numeric type normalization;
- `-0.0` becomes `0.0` recursively, including scores and normalized
  longitudes;
- fractional values are preserved exactly as the finite Python float already
  stored; and
- no decimal quantization, display rounding, percentage calculation, score
  clamping, tolerance comparison, or independently recalculated total is
  introduced.

A complete individual Koota score must be within its exact maximum. Maximums
must equal the imported Koota constants. Ashtakoota totals must equal the
strict aggregate. Manglik has no score. The compatibility report has no
combined score. Foundation percentage retains its existing `0.0..100.0`
factory contract; no other percentage is invented.

Optional fields are neither omitted nor filled with defaults. `None` is
accepted only where the typed family and status allow it; an unexpected null is
malformed. Empty strings retain their documented invalid-placeholder or
optional-text meaning but cannot substitute for a complete identifier.

### Strict Failure and Hardening Behavior

All public serializers are strict and fail before returning any partial copy:

- wrong outer result type, wrong nested collection type, unsupported Python
  object, or boolean-as-number raises `TypeError`;
- missing, unexpected, aliased, deprecated, or reordered fields; wrong
  identifiers, schema version, status, category, score, maximum, total,
  direction, role, metadata, or internal duplicate; non-finite number; cycle;
  or inconsistent result raises `ValueError`;
- deterministic error text identifies the family and first failing field/path;
- no error is returned inside a new serialization result;
- no field is ignored, defaulted, renamed, repaired, or dropped;
- no alias such as `max_score`, `total`, `person1`, or camelCase is supported;
  and
- no deprecated field registry exists in schema `1.0`.

Duplicate Koota identifiers, missing Kootas, unexpected Kootas, or wrong Koota
order are invalid. Invalid categories/statuses are not guessed. Scores below
zero, above maximum, non-finite, boolean, or inconsistent with duplicated
fields are invalid. Incorrect maxima, aggregate total mismatch, altered
Manglik comparison facts, malformed report sections/notes/metadata, and
incorrect validation counts are invalid.

The hardening layer may call existing strict public validators to establish
structural authority. Such calls must be fail-fast and exceptions propagate
unchanged unless this specification assigns `TypeError` or `ValueError` at the
serializer boundary. It must not catch broad `Exception`, invoke a raw
calculator as a fallback, infer a missing score, suppress component failures,
or return partial serialized output.

### Schema Versioning and Backward Compatibility

Every current family uses schema generation `1.0`. Individual Koota mappings
do not add a new top-level schema field in Task 11.15; their exact existing
`metadata.schema_version` remains authoritative. Foundation, context,
validation, aggregate, and Manglik results likewise retain metadata-level
versioning. Only the Compatibility Report continues to expose both top-level
`schema_version` and matching metadata version.

Consumers may rely on exact field names, field order, identifier values,
collection order, issue order, metadata order, and numeric semantics for a
given family/schema version. Stable ordering is intentional even though JSON
objects are semantically unordered in the JSON standard.

Backward-compatible maintenance within `1.0` includes only:

- bug fixes that restore already documented behavior without changing valid
  output;
- additive public Python exports that do not alter prior imports; and
- internal refactoring with identical serialized data, exceptions, and order.

Adding a field to a strict serialized family, changing field order, changing a
field type or nullability, renaming/removing a field, changing an identifier,
category, enum-like value, status, maximum, score meaning, role direction,
section/Koota order, or validation semantics is breaking and requires a
documented schema-version increment. An additive metadata field is also
breaking for this strict `1.0` contract and requires a version increment.

Removal or renaming of existing public exports and calculator parameters is
prohibited. Existing calculator signatures, all eight Koota mappings and
scores, `ASHTAKOOTA_TOTAL_MAXIMUM_SCORE=36.0`, Manglik binary five-house rules,
and Compatibility Report composition semantics remain unchanged. Public
serializer exports are additive only.

Task 11.15 does not read or hydrate stored payloads, so it provides no promise
that an arbitrary historical or future payload can be upgraded. Payloads
produced by the current `1.0` serializers remain deterministic and suitable for
storage, but schema migration and compatibility readers are deferred to a
separately specified future task.

### Explicit Implementation Selections

Task 11.15 includes:

- one small centralized internal recursive JSON validator/copier;
- one centralized internal family-contract registry;
- the family-specific public serializers listed above;
- strict structural and cross-field validation per result family;
- reuse of the existing report serializer and strict component validators;
- additive public schema constants and serializer exports;
- focused contract regression tests with explicit expected mappings; and
- full Sprint 11 backward-compatibility regression.

Task 11.15 does not include:

- a broad rewrite of completed modules;
- stored golden JSON fixture files or snapshot-update tooling;
- a new dependency or schema framework;
- public deserializers, hydrators, generic object converters, migration
  registries, or version negotiation;
- JSON strings, file output, persistence, API/Pydantic schemas, database
  models, UI/PDF rendering, or transport formatting; or
- changes to calculator result construction unless a focused test exposes a
  structural bug that violates an already documented contract.

If implementation reveals such a structural bug, the fix must be minimal,
documented in the changelog and Sprint verification notes, limited to the
affected structural field/copy behavior, and covered by a regression proving
all astrology classifications and scores are unchanged.

### Explicitly Excluded Behavior

Task 11.15 explicitly excludes:

- every astrology formula, classification, table, matrix, boundary, mapping,
  direction, score, maximum, total, cancellation, and exception-rule change;
- Manglik reference-point, house, category, comparison, severity, or
  cancellation changes;
- Ashtakoota execution, Koota order, total, maximum, percentage, or partial
  aggregation changes;
- Compatibility Report sections, composition workflow, score semantics, or
  technical-status changes;
- compatibility labels, pass/fail or suitability judgements, marriage advice,
  recommendations, remedies, predictions, Dasha/Navamsha interpretation, or
  AI narrative;
- API endpoints, authentication, authorization, telemetry, timestamps, UUIDs,
  random values, caches, environment data, database persistence, files,
  network calls, UI, HTML, or PDF generation;
- localization formatting, locale-specific number/text behavior, and
  platform-specific serialization; and
- Sprint 12 Report Data Model work or any later sprint.

### Required Runtime Tests

Task 11.15 runtime implementation is not complete until focused tests cover:

- every listed public serializer and every family identifier;
- all eight Koota serializers through `serialize_koota_result`;
- exact top-level and nested field order for every family;
- exact calculation, component, Koota, report, category, relationship, role,
  status, and schema identifiers;
- canonical eight-Koota order and exact nine-section report order;
- exact Koota maximums `1.0..8.0` and Ashtakoota maximum `36.0`;
- complete and existing invalid result states for each supported family;
- `json.dumps(..., allow_nan=False)` without a custom encoder for every output;
- deterministic equality for repeated equivalent calculations and repeated
  serialization of one unchanged runtime result;
- a fresh root and fresh nested mappings/lists on every serialization call;
- deep mutation isolation from the runtime result, prior/future payloads,
  sibling paths, calculator outputs, and module constants;
- no shared mutable defaults across factory, calculator, invalid-result, and
  serializer calls;
- exact empty error/warning/reference/factor/note collection behavior;
- every permitted optional null and rejection of null at required fields;
- finite integers/floats, integer-to-float normalization only where selected,
  boolean-as-number rejection, fractional score preservation, no new rounding,
  and recursive `-0.0` to `0.0` normalization;
- rejection of `NaN`, both infinities, tuples, sets, frozensets, enums,
  dataclasses, bytes, bytearrays, memoryviews, date/time/datetime, exceptions,
  callables, non-mapping custom containers, and arbitrary objects;
- deterministic conversion of valid mapping proxies, mapping subclasses, and
  list subclasses into independently allocated built-in dictionaries/lists,
  plus rejection when their shape, key order, keys, or nested values are
  malformed;
- rejection of non-string keys, shared mutable paths, direct cycles, indirect
  cycles, and cross-component aliasing with deterministic first-failure paths;
- wrong outer/nested result types, missing fields, unexpected fields, reordered
  fields, unsupported aliases, and deprecated-field attempts;
- invalid statuses, categories, classifications, relationships, roles,
  directions, metadata identifiers, and schema versions;
- invalid score types, negative scores, above-maximum scores, incorrect maxima,
  missing complete scores, and scores present on invalid Kootas;
- duplicate, missing, unexpected, and reordered Kootas; mismatched score/
  maximum mappings; and inconsistent aggregate totals;
- malformed Manglik classification, reference point, houses, binary category,
  pair classification, comparison status, role order, reasons, and exclusion
  metadata;
- malformed report type, version, summaries, sections, notes, Koota breakdown,
  validation counts, errors, warnings, or exclusion metadata;
- proof that serializers do not mutate inputs, invoke astrology tables,
  calculate scores, repair results, suppress failures, or produce JSON text;
- exact public exports, keyword-only signatures, import smoke, and no removed or
  renamed Task 11.1-11.14 export;
- unchanged direct outputs from matchmaking foundation, validation,
  Nakshatra context, all eight Kootas, Ashtakoota, Manglik, and report modules;
- unchanged directional behavior and bride/groom or person_a/person_b role
  ordering;
- unchanged `36.0` Ashtakoota maximum, binary Manglik classification, and
  structured-only Compatibility Report semantics;
- focused serialization tests followed by all matchmaking regressions;
- Kundali, Rashi, Nakshatra, longitude normalization, and placement dependency
  regressions; and
- the complete project suite.

Stored golden JSON files are not required. Tests use explicit expected
field/key tuples and representative complete/invalid mappings so review does
not depend on opaque snapshot regeneration.

### Completion Criteria and Documentation Progress

Task 11.15 runtime completion requires:

- all focused serialization/hardening tests pass;
- the complete matchmaking suite passes;
- Kundali, Rashi, Nakshatra, longitude, and placement regressions pass;
- the complete project suite passes;
- configured formatting and Python compilation checks pass;
- public import smoke and `json.dumps(..., allow_nan=False)` smoke pass;
- `git diff --check` passes;
- no duplicated astrology logic or public-contract regression is introduced;
  and
- runtime verification totals and any narrowly fixed structural bug are
  recorded.

### Completion and Verification

Task 11.15 and Sprint 11 are runtime-complete. The implementation adds the
central strict recursive validator/copier, exact family contract registry,
eleven keyword-only serializers, ordered schema-family constants, and additive
public exports. It preserves every existing calculator and report output while
rejecting malformed field order, identifiers, graph aliasing, cycles,
non-finite numbers, unsupported Python objects, and inconsistent aggregate or
Manglik data. Existing invalid Nadi identity placeholders remain unchanged:
their deterministic issues continue to live on the owning Koota result, while
complete Kootas require valid nested identities.

Verification totals recorded for the implementation task:

- focused serialization and compatibility-hardening suite: `79 passed`;
- complete matchmaking suite: `2639 passed`;
- Kundali, Rashi, Nakshatra, Lagna, placement, and planet-position dependency
  regression suite: `143 passed`; and
- complete project suite: `3607 passed, 13 skipped, 20 subtests passed`.

Black formatting, Python compilation, public import, strict
`json.dumps(..., allow_nan=False)`, and Git diff checks pass. Ruff was not
available and was not added. The skips remain the repository's pre-existing
manual-reference validation placeholders. Work stops here without beginning
Sprint 12.

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
- Bhakoot Koota reuses full Moon-Rashi derivation and inclusive circular
  one-based distance, preserves directional counts, and uses only the symmetric
  base `7.0`/`0.0` rule without cancellation exceptions specified in Task
  11.10.
- Nadi Koota reuses canonical Nakshatra normalization and ordered pair
  context, preserves explicit bride/groom roles, and uses only the symmetric
  base `0.0`/`8.0` matrix without cancellation exceptions specified in Task
  11.11.
- Ashtakoota aggregation orchestrates the eight completed Kootas in canonical
  order, derives its total only from validated component results, and adds no
  interpretation, threshold, cancellation, or replacement scoring rule.
- Manglik compatibility uses only the canonical whole-sign Mars house from the
  Lagna, the five-house binary convention specified in Task 11.13, and a
  structured same/mixed comparison with no score, cancellation, or judgement.
- Compatibility / Report Composition orchestrates only validated Task 11.12
  and Task 11.13 results in canonical section order, preserves component roles
  and scores, and adds no percentage, combined score, interpretation, verdict,
  or rendering behavior.
- Non-finite values are rejected at the strict serialization boundary.
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
- 11.10 Bhakoot Koota. **Complete.**
- 11.11 Nadi Koota. **Complete.**
- 11.12 Ashtakoota aggregation. **Complete.**
- 11.13 Manglik compatibility foundation. **Complete.**
- 11.14 Compatibility / Report Composition. **Complete.**
- 11.15 Serialization and compatibility hardening. **Complete.**

Sprint 11 is complete. This sequence remains the historical implementation
order; no Sprint 12 work is included here.

## Non-Goals

- Full matchmaking or Ashtakoota calculation.
- Compatibility labels or final marriage judgments.
- Interpretive prose, marriage advice, remedies, or AI output.
- Changes to completed calculation, prediction, API, report, or UI modules.
