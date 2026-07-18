# Canonical Matchmaking Test Vectors

These vectors demonstrate [SPEC-MATCHMAKING-001](../specifications/MATCHMAKING.md).
They are structural and deterministic domain-contract examples, not
independently verified astronomical ephemeris observations. `verified` means
accepted against the specification and linked automated tests.

## TV-MATCHMAKING-NORMATIVE-001 - Varna scoring

- Vector identifier: `TV-MATCHMAKING-NORMATIVE-001`
- Domain: Matchmaking / Varna
- Category: `normative`
- Purpose: Demonstrate the directional Varna rank rule.
- Inputs: pair `person_a.rashi="Mesha"`, `person_b.rashi="Meena"`;
  `subject_role="person_a"`, `comparison_role="person_b"`.
- Assumptions: canonical one-based Rashi-to-Varna mapping.
- Expected result: subject `kshatriya`, comparison `brahmin`, `score=1.0`,
  `maximum_score=1.0`, `status="complete"`.
- Tolerance: exact.
- Reference source: [Varna Koota](../specifications/MATCHMAKING.md#varna-koota).
- Verification status: `verified`.
- Linked automated test: `backend/tests/test_matchmaking_varna.py::test_valid_scoring_condition_returns_one`.
- Notes: Swapping the role assignment can change the score; no bride/groom
  role is inferred.

## TV-MATCHMAKING-NORMATIVE-002 - Vashya directional matrix

- Vector identifier: `TV-MATCHMAKING-NORMATIVE-002`
- Domain: Matchmaking / Vashya
- Category: `normative`
- Purpose: Demonstrate an asymmetric bride-row/groom-column score.
- Inputs: `bride_moon_longitude=0.0`, `groom_moon_longitude=120.0` degrees.
- Assumptions: sidereal longitudes; canonical normalization and Rashi lookup.
- Expected result: bride `chatushpada`, groom `vanachara`, `score=1.5`,
  `maximum_score=2.0`; swapped inputs score `0.0`.
- Tolerance: exact.
- Reference source: [Vashya Koota](../specifications/MATCHMAKING.md#vashya-koota).
- Verification status: `verified`.
- Linked automated test: `backend/tests/test_matchmaking_vashya.py::test_directional_asymmetric_pair_uses_bride_row`.
- Notes: Direction metadata is bride row and groom column.

## TV-MATCHMAKING-NORMATIVE-003 - Tara bidirectional score

- Vector identifier: `TV-MATCHMAKING-NORMATIVE-003`
- Domain: Matchmaking / Tara
- Category: `normative`
- Purpose: Demonstrate inclusive circular counting and a fractional result.
- Inputs: pair indexes `person_a=0` (Ashwini), `person_b=2` (Krittika);
  bride=`person_a`, groom=`person_b`.
- Assumptions: zero-based 27-Nakshatra sequence.
- Expected result: bride-to-groom count `3`, `vipat`, `0.0`; groom-to-bride
  count `26`, `mitra`, `1.5`; final `score=1.5`, `maximum_score=3.0`.
- Tolerance: exact.
- Reference source: [Tara Koota](../specifications/MATCHMAKING.md#tara-koota).
- Verification status: `verified`.
- Linked automated test: `backend/tests/test_matchmaking_tara.py::test_all_valid_final_scores`.
- Notes: Same Nakshatra would be Janma in both directions and score zero.

## TV-MATCHMAKING-NORMATIVE-004 - Yoni neutral pair

- Vector identifier: `TV-MATCHMAKING-NORMATIVE-004`
- Domain: Matchmaking / Yoni
- Category: `normative`
- Purpose: Demonstrate mapping plus symmetric matrix lookup.
- Inputs: Ashwini/index `0` as bride; Krittika/index `2` as groom.
- Assumptions: canonical 27-star mapping; Pada absent.
- Expected result: bride horse/male, groom sheep/female,
  `relationship="neutral"`, `score=2.0`, `maximum_score=4.0`; swapping roles
  preserves relationship and score.
- Tolerance: exact.
- Reference source: [Yoni Koota](../specifications/MATCHMAKING.md#yoni-koota).
- Verification status: `verified`.
- Linked automated test: `backend/tests/test_matchmaking_yoni.py::test_every_scoring_matrix_cell_and_relationship`.
- Notes: Yoni sex is metadata and does not alter scoring.

## TV-MATCHMAKING-NORMATIVE-005 - Graha Maitri neutral lords

- Vector identifier: `TV-MATCHMAKING-NORMATIVE-005`
- Domain: Matchmaking / Graha Maitri
- Category: `normative`
- Purpose: Demonstrate permanent relationship combination.
- Inputs: bride Moon `0.0` (Mesha/Mars); groom Moon `30.0`
  (Vrishabha/Venus).
- Assumptions: only natural/permanent relationships.
- Expected result: both directional relationships neutral,
  `combined_relationship="mutual_neutral"`, `score=3.0`,
  `maximum_score=5.0`.
- Tolerance: exact.
- Reference source: [Graha Maitri](../specifications/MATCHMAKING.md#graha-maitri-koota).
- Verification status: `verified`.
- Linked automated test: `backend/tests/test_matchmaking_graha_maitri.py::test_every_scoring_matrix_cell`.
- Notes: No temporary or chart-dependent relationship is consulted.

## TV-MATCHMAKING-NORMATIVE-006 - Gana directional score

- Vector identifier: `TV-MATCHMAKING-NORMATIVE-006`
- Domain: Matchmaking / Gana
- Category: `normative`
- Purpose: Demonstrate directional mixed-Gana scoring.
- Inputs: Ashwini/index `0` bride; Bharani/index `1` groom.
- Assumptions: zero-based canonical Nakshatra mapping.
- Expected result: Deva bride/Manushya groom scores `6.0`; swapped role
  assignment scores `5.0`; maximum is `6.0`.
- Tolerance: exact.
- Reference source: [Gana Koota](../specifications/MATCHMAKING.md#gana-koota).
- Verification status: `verified`.
- Linked automated test: `backend/tests/test_matchmaking_gana.py::test_directional_asymmetric_pairs_transpose_exactly`.
- Notes: Person ordering remains unchanged while role assignment changes.

## TV-MATCHMAKING-NORMATIVE-007 - Bhakoot 2/12 dosha

- Vector identifier: `TV-MATCHMAKING-NORMATIVE-007`
- Domain: Matchmaking / Bhakoot
- Category: `normative`
- Purpose: Demonstrate a dosha pair and directional distance metadata.
- Inputs: bride Moon `0.0` (Mesha), groom Moon `30.0` (Vrishabha).
- Assumptions: full Rashi and inclusive circular counting.
- Expected result: bride-to-groom `2`, groom-to-bride `12`, position `2/12`,
  `relationship="dosha"`, `bhakoot_dosha=true`, `score=0.0`, maximum `7.0`.
- Tolerance: exact.
- Reference source: [Bhakoot Koota](../specifications/MATCHMAKING.md#bhakoot-koota).
- Verification status: `verified`.
- Linked automated test: `backend/tests/test_matchmaking_bhakoot.py::test_all_144_rashi_pairs_match_documented_matrix_and_distances`.
- Notes: Role reversal swaps distances but not the score.

## TV-MATCHMAKING-NORMATIVE-008 - Nadi different-category score

- Vector identifier: `TV-MATCHMAKING-NORMATIVE-008`
- Domain: Matchmaking / Nadi
- Category: `normative`
- Purpose: Demonstrate the symmetric binary Nadi rule.
- Inputs: Ashwini/index `0` bride; Krittika/index `2` groom.
- Assumptions: Pada absent and irrelevant.
- Expected result: bride `adi`, groom `antya`,
  `relationship="different_nadi"`, `same_nadi=false`, `nadi_dosha=false`,
  `score=8.0`, maximum `8.0`.
- Tolerance: exact.
- Reference source: [Nadi Koota](../specifications/MATCHMAKING.md#nadi-koota).
- Verification status: `verified`.
- Linked automated test: `backend/tests/test_matchmaking_nadi.py::test_all_729_ordered_nakshatra_pairs_follow_exact_symmetric_rule`.
- Notes: Swapping roles preserves the score.

## TV-MATCHMAKING-NORMATIVE-009 - Real fractional aggregate

- Vector identifier: `TV-MATCHMAKING-NORMATIVE-009`
- Domain: Matchmaking / Ashtakoota aggregation
- Category: `normative`
- Purpose: Demonstrate all eight real calculators and exact fractional total.
- Inputs: bride Moon `0.0`, groom Moon `30.0` degrees.
- Assumptions: raw aggregate API; canonical execution order.
- Expected result: scores `{varna:0.0, vashya:2.0, tara:1.5, yoni:2.0,
  graha_maitri:3.0, gana:0.0, bhakoot:0.0, nadi:8.0}`; ordered total
  `16.5`; total maximum `36.0`; no percentage.
- Tolerance: exact.
- Reference source: [Ashtakoota aggregation](../specifications/MATCHMAKING.md#ashtakoota-aggregation).
- Verification status: `verified`.
- Linked automated test: `backend/tests/test_matchmaking_ashtakoota.py::test_fractional_scores_are_preserved_without_rounding`.
- Notes: Total is `math.fsum` of component scores.

## TV-MATCHMAKING-NORMATIVE-010 - Full aggregate

- Vector identifier: `TV-MATCHMAKING-NORMATIVE-010`
- Domain: Matchmaking / Ashtakoota aggregation
- Category: `normative`
- Purpose: Demonstrate the exact upper bound with validated components.
- Inputs: one complete precomputed component for each canonical Koota with
  scores `1,2,3,4,5,6,7,8` and matching maximums.
- Assumptions: every component otherwise retains a valid real result contract.
- Expected result: `status="complete"`, `total_score=36.0`,
  `total_maximum_score=36.0`, canonical eight-Koota order.
- Tolerance: exact.
- Reference source: [Ashtakoota aggregation](../specifications/MATCHMAKING.md#ashtakoota-aggregation).
- Verification status: `verified`.
- Linked automated test: `backend/tests/test_matchmaking_ashtakoota.py::test_precomputed_all_maximum_scores_total_thirty_six`.
- Notes: The aggregator does not recalculate component rules.

## TV-MATCHMAKING-NORMATIVE-011 - Zero aggregate

- Vector identifier: `TV-MATCHMAKING-NORMATIVE-011`
- Domain: Matchmaking / Ashtakoota aggregation
- Category: `normative`
- Purpose: Demonstrate the accepted lower bound for validated components.
- Inputs: one complete precomputed component per Koota, each score `0.0`, with
  each canonical maximum retained.
- Assumptions: component structures are otherwise valid.
- Expected result: `status="complete"`, `total_score=0.0`,
  `total_maximum_score=36.0`.
- Tolerance: exact.
- Reference source: [Ashtakoota aggregation](../specifications/MATCHMAKING.md#ashtakoota-aggregation).
- Verification status: `verified`.
- Linked automated test: `backend/tests/test_matchmaking_ashtakoota.py::test_precomputed_all_zero_scores_total_zero`.
- Notes: Zero is a technical score, not a marriage judgment.

## TV-MATCHMAKING-NORMATIVE-012 - All Manglik houses

- Vector identifier: `TV-MATCHMAKING-NORMATIVE-012`
- Domain: Matchmaking / Manglik classification
- Category: `normative`
- Purpose: Cover every supported and excluded whole-sign house.
- Inputs: Lagna longitude `1.0`; Mars longitude `(house-1)*30+1` for each
  house `1..12`.
- Assumptions: Lagna-only whole-sign house placement.
- Expected result: houses `1,4,7,8,12` classify `manglik` with reason
  `mars_in_manglik_house`; houses `2,3,5,6,9,10,11` classify `non_manglik`
  with reason `mars_not_in_manglik_house`.
- Tolerance: exact.
- Reference source: [Manglik foundation](../specifications/MATCHMAKING.md#manglik-compatibility-foundation).
- Verification status: `verified`.
- Linked automated test: `backend/tests/test_matchmaking_manglik.py::test_every_supported_house_is_manglik` and `::test_every_other_house_is_non_manglik`.
- Notes: House 2 is explicitly excluded.

## TV-MATCHMAKING-NORMATIVE-013 - Four Manglik comparisons

- Vector identifier: `TV-MATCHMAKING-NORMATIVE-013`
- Domain: Matchmaking / Manglik comparison
- Category: `normative`
- Purpose: Cover every role-preserving binary comparison.
- Inputs: complete classifications with bride/groom Mars houses `(1,4)`,
  `(2,3)`, `(1,2)`, and `(2,1)`.
- Assumptions: shared applicable houses `[1,4,7,8,12]` and Lagna reference.
- Expected result: respectively `both_manglik/same_status`,
  `both_non_manglik/same_status`,
  `bride_manglik_groom_non_manglik/mixed_status`, and
  `bride_non_manglik_groom_manglik/mixed_status`.
- Tolerance: exact.
- Reference source: [Manglik foundation](../specifications/MATCHMAKING.md#manglik-compatibility-foundation).
- Verification status: `verified`.
- Linked automated test: `backend/tests/test_matchmaking_manglik.py::test_every_documented_bride_groom_comparison`.
- Notes: No score, cancellation, or suitability judgment is produced.

## TV-MATCHMAKING-EDGE_BOUNDARY-001 - Split-sign cusps

- Vector identifier: `TV-MATCHMAKING-EDGE_BOUNDARY-001`
- Domain: Matchmaking / Vashya
- Category: `edge_boundary`
- Purpose: Fix the Dhanu and Makara 15-degree decisions.
- Inputs: longitudes `254.999999`, `255.0`, `284.999999`, `285.0` degrees.
- Assumptions: finite sidereal longitude and canonical Rashi lookup.
- Expected result: respectively `manava`, `chatushpada`, `chatushpada`,
  `jalachara`.
- Tolerance: exact at supplied precision.
- Reference source: [Vashya Koota](../specifications/MATCHMAKING.md#vashya-koota).
- Verification status: `verified`.
- Linked automated test: `backend/tests/test_matchmaking_vashya.py::test_split_sign_boundaries_are_exact`.
- Notes: No fuzzy epsilon is applied.

## TV-MATCHMAKING-EDGE_BOUNDARY-002 - Longitude normalization

- Vector identifier: `TV-MATCHMAKING-EDGE_BOUNDARY-002`
- Domain: Matchmaking / shared longitude contract
- Category: `edge_boundary`, `regression`
- Purpose: Demonstrate equivalent finite normalized values.
- Inputs: raw Manglik `(lagna,mars)` pairs `(360,360)`, `(-360,-30)`,
  `(721,750)`, `(-1,361)`.
- Assumptions: canonical longitude normalization.
- Expected result: normalized pairs `(0,0)`, `(0,330)`, `(1,30)`, `(359,1)`.
- Tolerance: exact.
- Reference source: [Shared boundaries](../specifications/MATCHMAKING.md#longitude-rashi-and-nakshatra-boundaries).
- Verification status: `verified`.
- Linked automated test: `backend/tests/test_matchmaking_manglik.py::test_raw_longitudes_reuse_canonical_normalization`.
- Notes: Matchmaking does not own a second normalizer.

## TV-MATCHMAKING-EDGE_BOUNDARY-003 - Rashi cusp and whole-sign house

- Vector identifier: `TV-MATCHMAKING-EDGE_BOUNDARY-003`
- Domain: Matchmaking / Manglik
- Category: `edge_boundary`
- Purpose: Show that exact Rashi cusps belong to the new sign.
- Inputs: equal Lagna and Mars at each longitude `0,30,...,330` degrees.
- Assumptions: one-based Rashi index and whole-sign placement.
- Expected result: equal canonical Rashi indexes, `mars_house=1`,
  `classification="manglik"` at every cusp.
- Tolerance: exact.
- Reference source: [Manglik foundation](../specifications/MATCHMAKING.md#manglik-compatibility-foundation).
- Verification status: `verified`.
- Linked automated test: `backend/tests/test_matchmaking_manglik.py::test_exact_rashi_boundaries_belong_to_new_sign`.
- Notes: Degrees within the same sign do not create a different house.

## TV-MATCHMAKING-INVALID_INPUT-001 - Invalid numeric inputs

- Vector identifier: `TV-MATCHMAKING-INVALID_INPUT-001`
- Domain: Matchmaking / validation
- Category: `invalid_input`
- Purpose: Fix boolean, wrong-type, and non-finite behavior.
- Inputs: each required longitude replaced in turn by `None`, boolean,
  string, NaN, positive infinity, or negative infinity as applicable.
- Assumptions: use the owning low- or high-level public API.
- Expected result: low-level classifier raises `TypeError` for boolean/non-real
  and `ValueError` for non-finite real; high-level calculator/report returns
  deterministic `status="invalid"`, no partial score, and JSON-safe issues.
- Tolerance: exact exception class or exact structured-invalid state.
- Reference source: [Invalid values](../specifications/MATCHMAKING.md#invalid-values-and-exceptions).
- Verification status: `verified`.
- Linked automated test: `backend/tests/test_matchmaking_vashya.py::test_classification_rejects_non_real_values`, `backend/tests/test_matchmaking_manglik.py::test_raw_classification_rejects_non_finite_values`, and `backend/tests/test_matchmaking_compatibility_report.py::test_invalid_raw_inputs_return_json_safe_invalid_reports`.
- Notes: Booleans are never numeric longitudes.

## TV-MATCHMAKING-INVALID_INPUT-002 - Invalid aggregate components

- Vector identifier: `TV-MATCHMAKING-INVALID_INPUT-002`
- Domain: Matchmaking / Ashtakoota aggregation
- Category: `invalid_input`, `regression`
- Purpose: Demonstrate strict precomputed-result validation.
- Inputs: separately omit a Koota, duplicate one, add an unexpected name,
  alter a maximum, use an invalid status/score, or mismatch direction.
- Assumptions: precomputed aggregation API.
- Expected result: `ValueError`; no total and no component recalculation.
- Tolerance: exact exception class.
- Reference source: [Ashtakoota aggregation](../specifications/MATCHMAKING.md#ashtakoota-aggregation).
- Verification status: `verified`.
- Linked automated test: `backend/tests/test_matchmaking_ashtakoota.py::test_each_missing_precomputed_koota_is_rejected`, `::test_each_duplicate_precomputed_koota_is_rejected`, and `::test_each_incorrect_component_maximum_is_rejected`.
- Notes: Unexpected calculator exceptions also propagate fail-fast.

## TV-MATCHMAKING-NORMATIVE-014 - Structured compatibility report

- Vector identifier: `TV-MATCHMAKING-NORMATIVE-014`
- Domain: Matchmaking / report composition
- Category: `normative`
- Purpose: Demonstrate raw six-longitude orchestration and canonical order.
- Inputs: bride/groom Moon `(0,30)`, Lagna `(1,1)`, Mars `(1,31)` degrees.
- Assumptions: all values are sidereal; raw report API.
- Expected result: complete schema `1.0` report, canonical nine sections and
  eight Kootas, Ashtakoota total `16.5/36.0`, bride Manglik house 1, groom
  non-Manglik house 2, pair `bride_manglik_groom_non_manglik`, comparison
  `mixed_status`, and no combined score or percentage.
- Tolerance: exact.
- Reference source: [Compatibility report](../specifications/MATCHMAKING.md#compatibility-report-composition).
- Verification status: `verified`.
- Linked automated test: `backend/tests/test_matchmaking_compatibility_report.py::test_raw_composition_uses_real_components_and_canonical_order`.
- Notes: Dependency order is Ashtakoota, bride classification, groom
  classification, then comparison.

## TV-MATCHMAKING-INVALID_INPUT-003 - Malformed report inputs

- Vector identifier: `TV-MATCHMAKING-INVALID_INPUT-003`
- Domain: Matchmaking / report composition
- Category: `invalid_input`, `regression`
- Purpose: Demonstrate strict precomputed report validation.
- Inputs: wrong outer type; malformed aggregate total/order/count; malformed
  Manglik category/reference/house; non-finite or aliased nested value.
- Assumptions: strict precomputed composer or report serializer.
- Expected result: `TypeError` for wrong outer types and `ValueError` for
  malformed contracts; no partial report and no silent repair.
- Tolerance: exact exception class.
- Reference source: [Compatibility report](../specifications/MATCHMAKING.md#compatibility-report-composition).
- Verification status: `verified`.
- Linked automated test: `backend/tests/test_matchmaking_compatibility_report.py::test_strict_composer_rejects_wrong_outer_types`, `::test_strict_composer_rejects_malformed_ashtakoota`, and `::test_strict_composer_rejects_malformed_manglik`.
- Notes: Component exceptions are not converted into successful reports.

## TV-MATCHMAKING-NORMATIVE-015 - Independent strict serialization

- Vector identifier: `TV-MATCHMAKING-NORMATIVE-015`
- Domain: Matchmaking / serialization
- Category: `normative`, `regression`
- Purpose: Demonstrate equal JSON data with independent mutable output.
- Inputs: any valid complete family result, serialized twice with its owning
  keyword-only serializer.
- Assumptions: exact family field shape and order.
- Expected result: both mappings equal the source by JSON value, contain only
  built-in dict/list/scalars, share no mutable paths with source or each other,
  and pass `json.dumps(..., allow_nan=False)`.
- Tolerance: exact.
- Reference source: [Serialization](../specifications/MATCHMAKING.md#serialization-contract).
- Verification status: `verified`.
- Linked automated test: `backend/tests/test_matchmaking_serialization.py::test_repeated_serialization_allocates_every_mutable_path_independently`.
- Notes: Source snapshots are not mutated.

## TV-MATCHMAKING-INVALID_INPUT-004 - Rejected serialization values

- Vector identifier: `TV-MATCHMAKING-INVALID_INPUT-004`
- Domain: Matchmaking / serialization
- Category: `invalid_input`, `regression`
- Purpose: Demonstrate strict recursive JSON safety and graph ownership.
- Inputs: inject in turn NaN/infinity, tuple, set, enum, dataclass,
  bytes-like value, date/time, exception, callable, arbitrary object,
  non-string key, direct/indirect cycle, or shared mutable alias.
- Assumptions: injection occurs at a field otherwise valid for its family.
- Expected result: deterministic `TypeError` or `ValueError` according to the
  malformed value; no stringification, dropping, or repair.
- Tolerance: exact exception class.
- Reference source: [Serialization](../specifications/MATCHMAKING.md#serialization-contract).
- Verification status: `verified`.
- Linked automated test: `backend/tests/test_matchmaking_serialization.py::test_non_json_python_values_are_rejected`, `::test_non_finite_values_are_rejected_at_any_depth`, `::test_direct_and_indirect_cycles_are_rejected`, and `::test_shared_mutable_paths_and_cross_component_aliases_are_rejected`.
- Notes: `-0.0` is the sole numeric canonicalization and becomes `0.0`.

## Coverage summary

The 22 vectors include one canonical example for each Koota, full/fractional/
zero aggregates, all Manglik houses and four comparisons, normalization and
cusps, invalid numerics and component contracts, report ordering, and strict
serialization. Exhaustive matrices and populations remain executable in the
linked tests: Vashya `5x5`, Yoni `14x14`, Graha Maitri `7x7`, Gana `3x3`,
Bhakoot all `144` Rashi pairs, Nadi all `729` Nakshatra pairs, and all 27
Nakshatra mappings.
