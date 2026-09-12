# SPEC-MATCHMAKING-001 - Matchmaking

| Field | Value |
| --- | --- |
| Status | approved |
| Version | 1.0 |
| Owning domain | Matchmaking |
| Canonical implementation | `backend/app/matchmaking/` |
| Historical source | [Sprint 11](../SPRINT-11.md) |
| Canonical vectors | [Matchmaking test vectors](../test-vectors/matchmaking.md) |

This specification is the permanent source of truth for the completed Sprint
11 Matchmaking contract. The Sprint document remains the historical execution
record. If this specification, an accepted ADR, runtime, and tests disagree,
use the [repository conflict process](../architecture/INDEX.md#source-of-truth-and-conflict-resolution);
do not silently select or merge rules.

## Scope

The domain supplies deterministic, structured foundations for matchmaking
people and ordered pairs; validation; Nakshatra pair context; eight
Ashtakoota Kootas; Ashtakoota aggregation; Lagna-only Manglik classification
and comparison; structured compatibility-report composition; and strict
JSON-safe serialization.

All calculations consume supplied sidereal positions or existing Kundali
output. They do not calculate birth charts, mutate inputs, infer marriage
roles, or interpret compatibility. Bride/groom and subject/comparison roles
are explicit wherever a rule is directional.

## Dependencies and governing decisions

- [ADR-002](../architecture/ADR-002-Astrology-Calculation-Standards.md): reuse
  canonical longitude, Rashi, Nakshatra, planet, and house calculations.
- [ADR-003](../architecture/ADR-003-Validation-Standards.md): deterministic,
  localization-ready validation and explicit failure behavior.
- [ADR-004](../architecture/ADR-004-Public-API-Contracts.md): additive,
  backward-compatible public contracts and stable serialization.
- [ADR-005](../architecture/ADR-005-Testing-Standards.md): focused,
  exhaustive, regression, serialization, and mutation-safety coverage.
- Canonical Rashi constants and helpers live in `backend/app/constants/rashi.py`
  and `backend/app/kundali/rashi.py`.
- Canonical Nakshatra constants and longitude lookup live in
  `backend/app/constants/nakshatra.py` and
  `backend/app/astrology/nakshatra.py`.
- Rashi lordship, natural planetary relationships, planet positions, Kundali
  charts, and whole-sign placement remain owned by `backend/app/kundali/`.

Matchmaking must reuse those dependencies and must not keep independent
longitude normalization, Rashi derivation, Nakshatra derivation, lordship,
natural-relationship, planet-position, or house-placement logic.

## Shared conventions

### Versioning, ordering, and ownership

`MATCHMAKING_SCHEMA_VERSION` is `"1.0"`. Public outputs are deterministic
ordered mapping/list snapshots. They remain built-in mutable containers for
backward compatibility but are immutable by public ownership contract: caller
mutation invalidates the snapshot. Each call allocates independent nested
collections.

Stable calculation statuses are `complete` and `invalid`; the generic
foundation result additionally supports `not_evaluated` and `partial`.
Validation/identity objects use `is_valid`. Complete calculations have a
finite score where applicable and no errors. Invalid scored calculations have
`score=None`, deterministic issues, and no partial score.

### Longitude, Rashi, and Nakshatra boundaries

Sidereal longitudes are finite real numbers, with booleans rejected. Existing
utilities normalize all finite values into `[0, 360)`. Thus `360` and `0` are
equivalent, and negative or greater-than-360 values are accepted through the
same normalization. Rashi intervals are half-open 30-degree spans; an exact
cusp belongs to the new Rashi. Nakshatra intervals and Padas use the existing
core half-open lookup without an epsilon or independent rounding rule.

Rashi indexes are one-based `1..12`. Matchmaking Nakshatra indexes are
zero-based `0..26`, Ashwini through Revati. Direct Nakshatra indexes do not
wrap; Pada, when supplied as context, is an integer `1..4`. Abhijit is not
inserted. Kootas whose public calculators accept a Nakshatra pair normalize
names, indexes, and supported person mappings through the shared pair context;
longitude-to-Nakshatra derivation remains a core astrology responsibility.

### Invalid values and exceptions

Low-level numeric classifiers raise `TypeError` for booleans/non-real values
and `ValueError` for NaN/infinity. Low-level category lookups raise
`TypeError` for wrong types and `ValueError` for noncanonical identifiers or
indexes. They never trim, case-fold, alias, wrap, or guess public enum values.
Raw high-level Koota, Ashtakoota, Manglik-classification, and report APIs
return their documented structured `invalid` result for expected raw-input
failures. Strict precomputed composers, category lookups, and serializers raise
`TypeError` or `ValueError` for malformed contracts. Unexpected dependency or
programming exceptions propagate; no layer silently suppresses a failure.

## Foundation, validation, and Nakshatra context

`MatchmakingPerson`, `MatchmakingPair`, and `MatchmakingResult` are JSON-safe
foundation snapshots. Person fields are optional and are not derived. The
person `longitude` field is geographic birth longitude and must never be used
as a sidereal Moon longitude.

Person validation checks exact known fields, ISO date/time, IANA timezone,
latitude `[-90, 90]`, geographic longitude `[-180, 180]`, Pada `1..4`, finite
numbers, and metadata shape. Pair validation preserves person order, validates
both people, and reports duplicate non-empty person IDs. It returns normalized
foundation values and performs no astrology.

Nakshatra identity normalization accepts a canonical name, zero-based index,
or supported person mapping. Pair context preserves `person_a`/`person_b` and
defines:

```text
forward_distance = (index_b - index_a) mod 27
reverse_distance = (index_a - index_b) mod 27
```

Same Nakshatra yields both distances `0`. `same_nakshatra` and `same_pada` are
audit fields, not compatibility judgments.

## Ashtakoota overview

The stable order and maximums are:

| Order | Koota | Domain | Direction | Maximum |
| ---: | --- | --- | --- | ---: |
| 1 | Varna | spiritual/social disposition | subject/comparison | 1.0 |
| 2 | Vashya | `attraction` | bride row/groom column | 2.0 |
| 3 | Tara | `destiny` | both directions, combined | 3.0 |
| 4 | Yoni | `intimacy` | symmetric | 4.0 |
| 5 | Graha Maitri | `mental_compatibility` | directional relationships, symmetric score | 5.0 |
| 6 | Gana | `temperament` | bride row/groom column | 6.0 |
| 7 | Bhakoot | `family_welfare` | symmetric score with directional distances | 7.0 |
| 8 | Nadi | `physiological_compatibility` | symmetric | 8.0 |

### Shared Nakshatra classification table

This table is normative for Yoni, Gana, and Nadi. Yoni sex is traditional
Nakshatra metadata, not a person's sex/gender and not a scoring axis. Pada
does not alter any of these classifications.

| Index | Nakshatra | Yoni | Traditional name | Yoni sex | Gana | Nadi |
| ---: | --- | --- | --- | --- | --- | --- |
| 0 | Ashwini | `horse` | Ashwa | `male` | `deva` | `adi` |
| 1 | Bharani | `elephant` | Gaja | `male` | `manushya` | `madhya` |
| 2 | Krittika | `sheep` | Mesha | `female` | `rakshasa` | `antya` |
| 3 | Rohini | `serpent` | Sarpa | `male` | `manushya` | `antya` |
| 4 | Mrigashira | `serpent` | Sarpa | `female` | `deva` | `madhya` |
| 5 | Ardra | `dog` | Shwana | `female` | `manushya` | `adi` |
| 6 | Punarvasu | `cat` | Marjara | `female` | `deva` | `adi` |
| 7 | Pushya | `sheep` | Mesha | `male` | `deva` | `madhya` |
| 8 | Ashlesha | `cat` | Marjara | `male` | `rakshasa` | `antya` |
| 9 | Magha | `rat` | Mushika | `male` | `rakshasa` | `antya` |
| 10 | Purva Phalguni | `rat` | Mushika | `female` | `manushya` | `madhya` |
| 11 | Uttara Phalguni | `cow` | Gau | `male` | `manushya` | `adi` |
| 12 | Hasta | `buffalo` | Mahisha | `female` | `deva` | `adi` |
| 13 | Chitra | `tiger` | Vyaghra | `female` | `rakshasa` | `madhya` |
| 14 | Swati | `buffalo` | Mahisha | `male` | `deva` | `antya` |
| 15 | Vishakha | `tiger` | Vyaghra | `male` | `rakshasa` | `antya` |
| 16 | Anuradha | `deer` | Mriga | `female` | `deva` | `madhya` |
| 17 | Jyeshtha | `deer` | Mriga | `male` | `rakshasa` | `adi` |
| 18 | Moola | `dog` | Shwana | `male` | `rakshasa` | `adi` |
| 19 | Purva Ashadha | `monkey` | Vanara | `male` | `manushya` | `madhya` |
| 20 | Uttara Ashadha | `mongoose` | Nakula | `male` | `manushya` | `antya` |
| 21 | Shravana | `monkey` | Vanara | `female` | `deva` | `antya` |
| 22 | Dhanishtha | `lion` | Simha | `female` | `rakshasa` | `madhya` |
| 23 | Shatabhisha | `horse` | Ashwa | `female` | `rakshasa` | `adi` |
| 24 | Purva Bhadrapada | `lion` | Simha | `male` | `manushya` | `adi` |
| 25 | Uttara Bhadrapada | `cow` | Gau | `female` | `manushya` | `madhya` |
| 26 | Revati | `elephant` | Gaja | `female` | `deva` | `antya` |

## Varna Koota

Varna maps the Moon Rashi by element: Fire=`kshatriya`, Earth=`vaishya`,
Air=`shudra`, Water=`brahmin`. In Rashi order Mesha through Meena, this repeats
`kshatriya`, `vaishya`, `shudra`, `brahmin`. Ranks are respectively 3, 2, 1,
and 4. The explicit subject/comparison direction scores `1.0` when the
comparison rank is greater than or equal to the subject rank, else `0.0`.
Same Varna scores `1.0`. The pair API requires explicit distinct role keys and
does not infer bride/groom meaning.

## Vashya Koota

Classification is from full Moon Rashi except two exact half-sign splits:

- `chatushpada`: Mesha, Vrishabha, Dhanu degree `>=15`, Makara degree `<15`;
- `manava`: Mithuna, Kanya, Tula, Kumbha, Dhanu degree `<15`;
- `jalachara`: Karka, Meena, Makara degree `>=15`;
- `vanachara`: Simha; and
- `keeta`: Vrishchika.

Exactly `255°` (Dhanu 15°) is `chatushpada`; exactly `285°` (Makara 15°) is
`jalachara`. Rows are bride and columns groom:

| Bride \ Groom | chatushpada | manava | jalachara | vanachara | keeta |
| --- | ---: | ---: | ---: | ---: | ---: |
| chatushpada | 2.0 | 1.0 | 1.0 | 1.5 | 1.0 |
| manava | 1.0 | 2.0 | 1.5 | 0.0 | 1.0 |
| jalachara | 1.0 | 1.5 | 2.0 | 1.0 | 1.0 |
| vanachara | 0.0 | 0.0 | 0.0 | 2.0 | 0.0 |
| keeta | 1.0 | 1.0 | 1.0 | 0.0 | 2.0 |

## Tara Koota

For each direction, count inclusively around the 27-star circle:

```text
inclusive_count = ((destination_index - source_index) mod 27) + 1
tara_number = ((inclusive_count - 1) mod 9) + 1
```

Tara numbers are: 1 `janma` unfavorable; 2 `sampat` favorable; 3 `vipat`
unfavorable; 4 `kshema` favorable; 5 `pratyari` unfavorable; 6 `sadhaka`
favorable; 7 `vadha` unfavorable; 8 `mitra` favorable; 9 `ati_mitra`
favorable. Each favorable bride-to-groom or groom-to-bride direction awards
`1.5`; the final score is the exact sum `0.0`, `1.5`, or `3.0`. Same
Nakshatra is Janma in both directions and scores `0.0`.

## Yoni Koota

Yoni uses the shared 27-star table and the following symmetric matrix. Scores
map to relationships: `4=same`, `3=friendly`, `2=neutral`, `1=enemy`,
`0=sworn_enemy`.

| Bride \ Groom | horse | elephant | sheep | serpent | dog | cat | rat | cow | buffalo | tiger | deer | monkey | mongoose | lion |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| horse | 4 | 2 | 2 | 3 | 2 | 2 | 2 | 1 | 0 | 1 | 3 | 3 | 2 | 1 |
| elephant | 2 | 4 | 3 | 3 | 2 | 2 | 2 | 2 | 3 | 1 | 2 | 3 | 2 | 0 |
| sheep | 2 | 3 | 4 | 2 | 1 | 2 | 1 | 3 | 3 | 1 | 2 | 0 | 3 | 1 |
| serpent | 3 | 3 | 2 | 4 | 2 | 1 | 1 | 1 | 1 | 2 | 2 | 2 | 0 | 2 |
| dog | 2 | 2 | 1 | 2 | 4 | 2 | 1 | 2 | 2 | 1 | 0 | 2 | 1 | 1 |
| cat | 2 | 2 | 2 | 1 | 2 | 4 | 0 | 2 | 2 | 1 | 3 | 3 | 2 | 1 |
| rat | 2 | 2 | 1 | 1 | 1 | 0 | 4 | 2 | 2 | 2 | 2 | 2 | 1 | 2 |
| cow | 1 | 2 | 3 | 1 | 2 | 2 | 2 | 4 | 3 | 0 | 3 | 2 | 2 | 1 |
| buffalo | 0 | 3 | 3 | 1 | 2 | 2 | 2 | 3 | 4 | 1 | 2 | 2 | 2 | 1 |
| tiger | 1 | 1 | 1 | 2 | 1 | 1 | 2 | 0 | 1 | 4 | 1 | 1 | 2 | 1 |
| deer | 3 | 2 | 2 | 2 | 0 | 3 | 2 | 3 | 2 | 1 | 4 | 2 | 2 | 1 |
| monkey | 3 | 3 | 0 | 2 | 2 | 3 | 2 | 2 | 2 | 1 | 2 | 4 | 3 | 2 |
| mongoose | 2 | 2 | 3 | 0 | 1 | 2 | 1 | 2 | 2 | 2 | 2 | 3 | 4 | 2 |
| lion | 1 | 0 | 1 | 2 | 1 | 1 | 2 | 1 | 1 | 1 | 1 | 2 | 2 | 4 |

Same animal, including different Nakshatras, scores `4.0`; same Nakshatra
therefore scores `4.0`. The matrix, not animal inference, is authoritative.

## Graha Maitri Koota

Moon Rashi lords in order are: Mesha=`mars`, Vrishabha=`venus`,
Mithuna=`mercury`, Karka=`moon`, Simha=`sun`, Kanya=`mercury`, Tula=`venus`,
Vrishchika=`mars`, Dhanu=`jupiter`, Makara=`saturn`, Kumbha=`saturn`, and
Meena=`jupiter`.

Only permanent/natural friendship is used. Temporary friendship, Panchadha
Maitri, chart-dependent relations, dignity, strength, and divisional charts
are excluded. Directional permanent relationships are:

| Lord | Friends | Neutrals | Enemies |
| --- | --- | --- | --- |
| sun | moon, mars, jupiter | mercury | venus, saturn |
| moon | sun, mercury | mars, jupiter, venus, saturn | none |
| mars | sun, moon, jupiter | venus, saturn | mercury |
| mercury | sun, venus | mars, jupiter, saturn | moon |
| jupiter | sun, moon, mars | saturn | mercury, venus |
| venus | mercury, saturn | mars, jupiter | sun, moon |
| saturn | mercury, venus | jupiter | sun, moon, mars |

Same lord scores `5.0`. For different lords, the unordered pair of two
directional statuses scores: friend/friend `5.0`, friend/neutral `4.0`,
neutral/neutral `3.0`, friend/enemy `1.0`, neutral/enemy `0.5`, enemy/enemy
`0.0`. The resulting bride-row/groom-column matrix is symmetric:

| Bride \ Groom | sun | moon | mars | mercury | jupiter | venus | saturn |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| sun | 5.0 | 5.0 | 5.0 | 4.0 | 5.0 | 0.0 | 0.0 |
| moon | 5.0 | 5.0 | 4.0 | 1.0 | 4.0 | 0.5 | 0.5 |
| mars | 5.0 | 4.0 | 5.0 | 0.5 | 5.0 | 3.0 | 0.5 |
| mercury | 4.0 | 1.0 | 0.5 | 5.0 | 0.5 | 5.0 | 4.0 |
| jupiter | 5.0 | 4.0 | 5.0 | 0.5 | 5.0 | 0.5 | 3.0 |
| venus | 0.0 | 0.5 | 3.0 | 5.0 | 0.5 | 5.0 | 5.0 |
| saturn | 0.0 | 0.5 | 0.5 | 4.0 | 3.0 | 5.0 | 5.0 |

## Gana Koota

Gana uses the shared 27-star table. Rows are bride and columns groom:

| Bride \ Groom | deva | manushya | rakshasa |
| --- | ---: | ---: | ---: |
| deva | 6.0 | 6.0 | 0.0 |
| manushya | 5.0 | 6.0 | 0.0 |
| rakshasa | 1.0 | 0.0 | 6.0 |

The rule is directional: Deva/Manushya and Manushya/Deva differ, as do
Deva/Rakshasa and Rakshasa/Deva. Same Gana and same Nakshatra score `6.0`.

## Bhakoot Koota

Bhakoot uses full Moon Rashi only; there are no split signs. Inclusive
directional distances are:

```text
bride_to_groom = ((groom_index - bride_index) mod 12) + 1
groom_to_bride = ((bride_index - groom_index) mod 12) + 1
```

The unordered inclusive position pairs are `1/1`, `2/12`, `3/11`, `4/10`,
`5/9`, `6/8`, and `7/7`. Exactly `2/12`, `5/9`, and `6/8` are dosha and score
`0.0`; every other pair scores `7.0`. Same Rashi is `1/1` and scores `7.0`.
The score is symmetric while the two distance fields swap on role reversal.
Rashi-lord friendship and all cancellation/exception rules are excluded.

## Nadi Koota

Nadi uses the shared 27-star table. The symmetric matrix is:

| Bride \ Groom | adi | madhya | antya |
| --- | ---: | ---: | ---: |
| adi | 0.0 | 8.0 | 8.0 |
| madhya | 8.0 | 0.0 | 8.0 |
| antya | 8.0 | 8.0 | 0.0 |

Same Nadi, including the same Nakshatra, has `nadi_dosha=true` and scores
`0.0`; different Nadi scores `8.0`. Pada and all Nadi-dosha cancellation,
Rashi, lordship, Gotra, and other exception rules are excluded.

## Ashtakoota aggregation

`calculate_ashtakoota` accepts explicit keyword-only bride and groom Moon
longitudes and invokes the eight existing calculators exactly once in the
canonical order shown above. `aggregate_ashtakoota_results` accepts exactly
one complete result for each canonical Koota, reorders validated components,
and never recalculates their rules. It rejects missing, duplicate, unexpected,
wrong-type, wrong-order metadata, wrong-maximum, invalid-status, non-JSON-safe,
role-mismatched, or out-of-range components.

`total_score` is `math.fsum` of component scores in canonical order, with no
rounding; `total_maximum_score` is exactly `36.0`. No percentage is produced.
There is no partial aggregate total. Expected input-invalid component results
may be retained for audit with `status=invalid` and `total_score=None`;
unexpected component failures propagate and stop later execution.

## Manglik compatibility foundation

The sole convention is binary, Lagna-only, whole-sign classification. The
house formula reuses canonical one-based Rashi indexes:

```text
mars_house = ((mars_rashi_index - lagna_rashi_index) mod 12) + 1
```

Mars in house `1`, `4`, `7`, `8`, or `12` is `manglik`; Mars in every other
house, including house `2`, is `non_manglik`. Exact sign cusps belong to the
new sign. Moon- and Venus-based evaluation, partial/weighted/severity states,
scores, double-Manglik cancellation, every cancellation or exception,
conjunction, aspect, combustion, retrograde, dignity, strength, lordship,
Navamsha, and all divisional charts are excluded.

Three APIs are deliberately separated:

1. `classify_manglik` classifies raw Lagna and Mars sidereal longitudes.
2. `classify_manglik_from_chart` adapts the existing Kundali mapping, requires
   canonical Lagna and exactly one canonical Mars position, and validates any
   redundant placement rather than coercing or repairing it.
3. `compare_manglik_classifications` strictly compares two complete
   precomputed classifications.

Comparison is symmetric in status but role-preserving in category. The four
pair categories are `both_manglik`, `both_non_manglik`,
`bride_manglik_groom_non_manglik`, and
`bride_non_manglik_groom_manglik`; comparison status is `same_status` for the
first two and `mixed_status` for the latter two. These are technical facts,
not cancellation, scoring, suitability, or advice.

## Compatibility report composition

The report is structured data only. It contains validated Ashtakoota and
Manglik outputs without calculating new rules, combining scores, labeling
compatibility, or interpreting astrology. It has exactly three APIs:

1. `compose_compatibility_report` accepts six keyword-only longitudes (bride
   and groom Moon, Lagna, and Mars), runs Ashtakoota, classifies bride then
   groom Manglik, compares them, and composes only after successful validation.
2. `compose_compatibility_report_from_results` strictly composes one complete
   Ashtakoota aggregate and one complete Manglik comparison.
3. `serialize_compatibility_report` validates and deep-copies one complete
   report to an independent JSON-safe mapping.

The report fields are ordered: `schema_version`, `report_type`, `status`,
`bride`, `groom`, `ashtakoota`, `koota_results`, `manglik`, `validation`,
`errors`, `warnings`, `notes`, `sections`, `metadata`. Report type is
`matchmaking_compatibility_report`; schema is `1.0`. Sections are ordered
`report_metadata`, `input_summary`, `ashtakoota_summary`, `koota_breakdown`,
`manglik_summary`, `validation_status`, `errors`, `warnings`, `notes`.

The strict composer validates types, status, roles, all eight names/order/
maximums/scores, total `36.0`, aggregate sums, Manglik classifications,
reference point, Mars houses, pair/comparison consistency, finite JSON values,
and alias safety. No partial-success report or chart-pair report API exists.
Chart callers classify through the Task 11.13 chart adapter, compare, then use
the precomputed composer. Component exceptions propagate.

No overall label, pass/fail verdict, marriage-suitability judgment,
recommendation, remedy, prediction, narrative, Manglik score, combined
Ashtakoota-plus-Manglik score, or percentage is added. Future API/UI/PDF
consumers may render this stable artifact but are not part of this contract.

## Serialization contract

Canonical serialization validates exact family, exact field presence and
order, canonical identifiers and categories, state-dependent optional values,
duplicated summary consistency, finite numeric values, and independent object
graphs. It returns a fresh built-in `dict`/`list` tree, preserves finite floats
without rounding, and normalizes `-0.0` to `0.0`.

The 19 ordered families are:

```text
matchmaking_person, matchmaking_pair, matchmaking_result,
matchmaking_person_validation, matchmaking_pair_validation,
matchmaking_nakshatra_identity, matchmaking_nakshatra_pair_context,
varna, vashya, tara, yoni, graha_maitri, gana, bhakoot, nadi,
ashtakoota_aggregation, manglik_classification, manglik_compatibility,
matchmaking_compatibility_report
```

Mapping proxies and mapping/list subclasses are accepted only at declared
mapping/list positions and copied to built-ins. Non-string mapping keys,
tuples, sets/frozensets, enums, dataclasses, bytes-like values, date/time
objects, exceptions, callables, arbitrary objects, NaN/infinity, cycles, and
shared mutable aliases are rejected. Values are never stringified, dropped,
repaired, or silently coerced. The layer does not deserialize, migrate schemas,
emit JSON text, persist data, or calculate astrology.

## Public API inventory

All names are additive exports of `backend.app.matchmaking`. The 55 public
callables are grouped below; signatures are contractual.

### Foundation and validation (10)

```python
create_empty_matchmaking_person(person_id="")
create_empty_matchmaking_pair()
create_empty_matchmaking_result(matchmaking_id="")
create_matchmaking_person(*, person_id="", name="", birth_date="",
    birth_time="", latitude=None, longitude=None, timezone="", rashi="",
    nakshatra="", nakshatra_pada=None, lagna="", metadata=None)
create_matchmaking_pair(person_a=None, person_b=None, *, metadata=None)
create_matchmaking_result(*, matchmaking_id="", status="not_evaluated",
    score=None, maximum_score=None, percentage=None, factors=None,
    warnings=None, references=None, notes=None, metadata=None)
validate_matchmaking_person(value)
validate_matchmaking_pair(value)
normalize_matchmaking_nakshatra(value, *, pada=None, source_person_id="")
build_nakshatra_pair_context(pair_or_person_a, person_b=None)
```

### Koota and context helpers (26)

```python
calculate_nakshatra_distance(index_from, index_to)
resolve_varna(value, *, source_person_id="")
calculate_varna_koota(pair, *, subject_role=None, comparison_role=None)
classify_vashya(sidereal_moon_longitude)
get_vashya_score(bride_vashya, groom_vashya)
calculate_vashya_koota(*, bride_moon_longitude=None,
    groom_moon_longitude=None)
calculate_tara_inclusive_count(index_from, index_to)
classify_tara(inclusive_count)
calculate_tara_direction(index_from, index_to, *, source_role,
    destination_role, source_nakshatra="", destination_nakshatra="")
calculate_tara_koota(pair, *, bride_role=None, groom_role=None)
classify_yoni(value, *, pada=None, source_person_id="")
get_yoni_relationship(bride_yoni, groom_yoni)
calculate_yoni_koota(pair, *, bride_role=None, groom_role=None)
classify_graha_maitri_lord(sidereal_moon_longitude)
get_graha_maitri_relationship(bride_lord, groom_lord)
calculate_graha_maitri_koota(*, bride_moon_longitude=None,
    groom_moon_longitude=None)
classify_gana(value, *, pada=None, source_person_id="")
get_gana_relationship(bride_gana, groom_gana)
calculate_gana_koota(pair, *, bride_role=None, groom_role=None)
classify_bhakoot_rashi(sidereal_moon_longitude)
calculate_bhakoot_inclusive_distance(from_rashi_index, to_rashi_index)
get_bhakoot_relationship(bride_rashi_index, groom_rashi_index)
calculate_bhakoot_koota(*, bride_moon_longitude=None,
    groom_moon_longitude=None)
classify_nadi(value, *, pada=None, source_person_id="")
get_nadi_relationship(bride_nadi, groom_nadi)
calculate_nadi_koota(pair, *, bride_role=None, groom_role=None)
```

### Aggregation, Manglik, report, and serialization (19)

```python
calculate_ashtakoota(*, bride_moon_longitude=None,
    groom_moon_longitude=None)
aggregate_ashtakoota_results(results, *, bride_moon_longitude=None,
    groom_moon_longitude=None)
classify_manglik(*, lagna_sidereal_longitude=None,
    mars_sidereal_longitude=None)
classify_manglik_from_chart(*, chart=None)
compare_manglik_classifications(*, bride, groom)
compose_compatibility_report(*, bride_moon_longitude=None,
    groom_moon_longitude=None, bride_lagna_longitude=None,
    groom_lagna_longitude=None, bride_mars_longitude=None,
    groom_mars_longitude=None)
compose_compatibility_report_from_results(*, ashtakoota, manglik)
serialize_compatibility_report(*, report)
serialize_matchmaking_person(*, result)
serialize_matchmaking_pair(*, result)
serialize_matchmaking_result(*, result)
serialize_matchmaking_person_validation(*, result)
serialize_matchmaking_pair_validation(*, result)
serialize_matchmaking_nakshatra_identity(*, result)
serialize_matchmaking_nakshatra_pair_context(*, result)
serialize_koota_result(*, result)
serialize_ashtakoota_result(*, result)
serialize_manglik_classification_result(*, result)
serialize_manglik_compatibility_result(*, result)
```

The package also exports 66 public TypedDict/NamedTuple types and 90 public
constants/type aliases. Their existing names in `__all__` remain compatible;
the inventories below define result families while runtime modules define
nested type details and constants.

## Result-family inventory

Exact top-level fields and order for all 19 serialized families are:

| Family / public type | Exact fields in order |
| --- | --- |
| `matchmaking_person` / `MatchmakingPerson` | `person_id`, `name`, `birth_date`, `birth_time`, `latitude`, `longitude`, `timezone`, `rashi`, `nakshatra`, `nakshatra_pada`, `lagna`, `metadata` |
| `matchmaking_pair` / `MatchmakingPair` | `person_a`, `person_b`, `metadata` |
| `matchmaking_result` / `MatchmakingResult` | `matchmaking_id`, `status`, `score`, `maximum_score`, `percentage`, `factors`, `warnings`, `references`, `notes`, `metadata` |
| `matchmaking_person_validation` / `MatchmakingPersonValidationResult` | `is_valid`, `errors`, `warnings`, `normalized_value`, `metadata` |
| `matchmaking_pair_validation` / `MatchmakingPairValidationResult` | `is_valid`, `errors`, `warnings`, `normalized_value`, `metadata` |
| `matchmaking_nakshatra_identity` / `MatchmakingNakshatraIdentity` | `is_valid`, `name`, `index`, `pada`, `source_person_id`, `errors`, `warnings`, `metadata` |
| `matchmaking_nakshatra_pair_context` / `MatchmakingNakshatraPairContext` | `is_valid`, `person_a`, `person_b`, `forward_distance`, `reverse_distance`, `same_nakshatra`, `same_pada`, `errors`, `warnings`, `metadata` |
| `varna` / `MatchmakingVarnaKootaResult` | `koota`, `status`, `score`, `maximum_score`, `person_a_varna`, `person_b_varna`, `direction`, `factors`, `errors`, `warnings`, `references`, `metadata` |
| `vashya` / `MatchmakingVashyaKootaResult` | `koota`, `compatibility_domain`, `status`, `score`, `maximum_score`, `bride_vashya`, `groom_vashya`, `direction`, `factors`, `errors`, `warnings`, `references`, `metadata` |
| `tara` / `MatchmakingTaraKootaResult` | `koota`, `compatibility_domain`, `status`, `score`, `maximum_score`, `person_a_nakshatra`, `person_b_nakshatra`, `direction`, `bride_to_groom`, `groom_to_bride`, `same_nakshatra`, `same_pada`, `factors`, `errors`, `warnings`, `references`, `metadata` |
| `yoni` / `MatchmakingYoniKootaResult` | `koota`, `compatibility_domain`, `status`, `score`, `maximum_score`, `person_a_nakshatra`, `person_b_nakshatra`, `direction`, `bride_yoni`, `groom_yoni`, `relationship`, `same_nakshatra`, `same_pada`, `same_yoni`, `factors`, `errors`, `warnings`, `references`, `metadata` |
| `graha_maitri` / `MatchmakingGrahaMaitriKootaResult` | `koota`, `compatibility_domain`, `status`, `score`, `maximum_score`, `bride_moon_rashi`, `groom_moon_rashi`, `direction`, `bride_to_groom_relationship`, `groom_to_bride_relationship`, `combined_relationship`, `same_lord`, `factors`, `errors`, `warnings`, `references`, `metadata` |
| `gana` / `MatchmakingGanaKootaResult` | `koota`, `compatibility_domain`, `status`, `score`, `maximum_score`, `person_a_nakshatra`, `person_b_nakshatra`, `direction`, `bride_gana`, `groom_gana`, `relationship`, `same_nakshatra`, `same_pada`, `same_gana`, `factors`, `errors`, `warnings`, `references`, `metadata` |
| `bhakoot` / `MatchmakingBhakootKootaResult` | `koota`, `compatibility_domain`, `status`, `score`, `maximum_score`, `bride_moon_rashi`, `groom_moon_rashi`, `direction`, `bride_to_groom_distance`, `groom_to_bride_distance`, `pair_identifier`, `position_pair`, `relationship`, `same_rashi`, `bhakoot_dosha`, `factors`, `errors`, `warnings`, `references`, `metadata` |
| `nadi` / `MatchmakingNadiKootaResult` | `koota`, `compatibility_domain`, `status`, `score`, `maximum_score`, `person_a_nakshatra`, `person_b_nakshatra`, `direction`, `bride_nadi`, `groom_nadi`, `relationship`, `same_nakshatra`, `same_pada`, `same_nadi`, `nadi_dosha`, `factors`, `errors`, `warnings`, `references`, `metadata` |
| `ashtakoota_aggregation` / `MatchmakingAshtakootaResult` | `calculation`, `status`, `bride_moon_longitude`, `groom_moon_longitude`, `koota_results`, `score_by_koota`, `maximum_score_by_koota`, `total_score`, `total_maximum_score`, `errors`, `warnings`, `references`, `metadata` |
| `manglik_classification` / `ManglikClassificationResult` | `calculation`, `status`, `classification`, `reference_point`, `lagna_sidereal_longitude`, `mars_sidereal_longitude`, `lagna_rashi_index`, `mars_rashi_index`, `mars_house`, `applicable_manglik_houses`, `reason`, `errors`, `warnings`, `references`, `metadata` |
| `manglik_compatibility` / `ManglikCompatibilityResult` | `calculation`, `status`, `bride_manglik`, `groom_manglik`, `bride_classification`, `groom_classification`, `bride_reference_point`, `groom_reference_point`, `bride_mars_house`, `groom_mars_house`, `applicable_manglik_houses`, `pair_classification`, `comparison_status`, `reasons`, `errors`, `warnings`, `references`, `metadata` |
| `matchmaking_compatibility_report` / `MatchmakingCompatibilityReport` | `schema_version`, `report_type`, `status`, `bride`, `groom`, `ashtakoota`, `koota_results`, `manglik`, `validation`, `errors`, `warnings`, `notes`, `sections`, `metadata` |

The 12 public serializer functions are the 11 `serialize_*` functions in the
serialization module plus the existing report serializer. Each validates one
of the families above; `serialize_koota_result` dispatches only by the exact
eight Koota identifiers.

## Backward compatibility

- Existing import paths, names, signatures, keyword-only parameters, TypedDict
  shapes, field order, constants, issue codes, status/category identifiers,
  score sets, and safe-invalid behavior are retained.
- New behavior is additive. No calculator is retrofitted to a frozen
  dataclass, Pydantic model, tuple, or mapping proxy.
- Direct valid calculator output remains JSON-serializable, but only the
  serializer APIs provide strict family validation and independent copying.
- Directional Kootas remain directional when bride/groom inputs are swapped;
  aggregation and reporting do not force symmetry.
- Changes to this approved contract require a focused task, compatibility
  analysis, updated vectors/tests, and a version or explicit supersession note.

## Explicit exclusions

This domain does not provide marriage prediction, pass/fail or suitability
judgments, interpretation, thresholds, advice, remedies, AI narrative, Dasha
analysis, general horoscope interpretation, chart calculation, report prose,
PDF/UI/API transport, persistence, deserialization, or regional-rule merging.
It does not add Koota cancellation, Bhakoot/Nadi exceptions, Manglik
cancellation, temporary planetary friendship, hidden weighting, or an
Ashtakoota-plus-Manglik score.

## Verification and implementation references

- Canonical reviewed examples: [Matchmaking test vectors](../test-vectors/matchmaking.md).
- Runtime: `backend/app/matchmaking/`.
- Automated coverage: `backend/tests/test_matchmaking_*.py`.
- Core Rashi/Nakshatra/Kundali regressions remain required for changes that
  touch reused dependencies.
- Historical implementation and verification record: [Sprint 11](../SPRINT-11.md).

The migration audit compared all 15 runtime modules, all 15 focused test
modules, package exports, Sprint 11, MASTER, ROADMAP, accepted ADRs, and the
documentation indexes. No material accepted-rule conflict was found. The
historical Task 11.8 status line is stale relative to its completed runtime,
tests, Sprint completion heading, and MASTER record; it is retained as
historical text and does not override this approved contract.

## Change history and supersession

| Version | Change |
| --- | --- |
| 1.0 | Migrated and approved the completed Sprint 11 contract without runtime changes. |

This document remains canonical until a later approved specification names
`SPEC-MATCHMAKING-001`, states what it supersedes, and provides migration and
backward-compatibility guidance.
