# BhaktiAstro Master Working Document

This document is the Codex working brief for the BhaktiAstro repository. Use it
to keep each task scoped, testable, and aligned with the deterministic-first
project rules.

## Documentation Navigation

`MASTER.md` is the concise project navigation and current-status entry point.
It does not own detailed astrology formulas, exhaustive validation rules, or
permanent calculator contracts.

- Milestone sequence and high-level scope: [ROADMAP.md](ROADMAP.md)
- Cross-cutting decisions: [Architecture index](architecture/INDEX.md)
- Permanent domain contracts and migration status:
  [Specifications index](specifications/INDEX.md)
- Reviewed examples and boundary cases:
  [Test-vector index](test-vectors/INDEX.md)
- Most recently completed Sprint execution record: [SPRINT-11.md](SPRINT-11.md)

Current product status: Sprint 11 is complete. The Documentation Architecture
Foundation gate is complete. Sprint 12 and Task 12.1 have not started; there is
no active product Sprint task.

## Project Rules

- Work on one task or milestone at a time.
- Do not rewrite completed modules.
- Do not duplicate existing functionality.
- Preserve backward compatibility.
- Follow the existing project structure.
- Prefer reusable modules over one-off logic.
- Keep changes incremental and reviewable.
- Do not modify Panchang logic unless the task explicitly targets Panchang.
- Do not modify astronomical calculations unless the task explicitly targets
  astronomy.
- Do not implement predictions before deterministic calculation foundations are
  complete.
- Do not add interpretation text before deterministic rule outputs are stable.
- Never guess astrology formulas. If a formula is unverified, add a placeholder
  or skipped test and document the verification need.

## Completed Milestones

- Sprint 1: Panchang and astronomy foundations.
- Sprint 2: Panchang element foundations and boundary timing.
- Sprint 3: Panchang API, fixtures, validation, and smoke coverage.
- Sprint 4: Kundali Engine foundation.
- Sprint 5: Divisional Charts / Varga Engine.
- Sprint 6: Dasha Engine.
- Sprint 7: Planet Strength Engine.
- Sprint 8: Ashtakavarga Engine.
- Sprint 9: Advanced Lagna and Arudha Engine.
- Sprint 10A: Prediction Framework Architecture.
- Sprint 10B: Prediction Rules Foundation.
- Sprint 11: Matchmaking Foundation.

Sprint 4 completed:

- Rashi Engine
- Bhava Foundation
- Lagna Foundation
- Kundali Chart Assembly
- Kundali API Foundation
- Chart Format Foundation
- Planet House Placement
- Graha Lordship
- Exaltation and Debilitation
- Mooltrikona
- Natural Graha Relationships
- Retrograde Foundation
- Combustion Foundation
- Graha Drishti
- Yoga Framework
- Gajakesari Yoga Foundation
- Raja Yoga Foundation
- Dhana Yoga Foundation
- Panch Mahapurusha Yoga Foundation
- Kundali JSON Export
- Sprint 4 documentation and completion checklist

Sprint 5 completed:

- Varga Framework Foundation
- D2 Hora
- D3 Drekkana
- D7 Saptamsa
- D9 Navamsa
- D10 Dasamsa
- D12 Dwadashamsa
- D16 Shodasamsa
- D20 Vimshamsa
- D24 Siddhamsa
- D27 Bhamsa
- D30 Trimsamsa
- D40 Khavedamsa
- D45 Akshavedamsa
- D60 Shastiamsa
- Internal Kundali Varga integration
- Optional Kundali API Varga exposure with `include_vargas`
- Sprint 5 documentation and completion checklist

Sprint 6 completed:

- Vimshottari Dasha constants
- Nakshatra to Mahadasha mapping
- Birth Dasha Balance
- Mahadasha Timeline
- Antardasha Engine
- Pratyantardasha Engine
- Current Dasha Lookup
- Dasha Timeline Builder
- Dasha Pydantic Schemas
- Dasha FastAPI Endpoint
- Validation Coverage
- Regression Coverage
- Sprint 6 documentation and completion checklist

Sprint 7 completed:

- Shadbala Foundation Utilities
- Sthana Bala Foundation
- Dig Bala Foundation
- Kala Bala Foundation
- Chesta Bala Foundation
- Naisargika Bala Foundation
- Drik Bala Foundation
- Shadbala Aggregator Foundation
- Ishta/Kashta Bala Foundation
- Planet Strength Summary Builder
- Internal Kundali Strength Integration
- Optional Kundali API Strength Exposure with `include_strength`
- Validation Coverage
- Regression Coverage
- Sprint 7 documentation and completion checklist

Sprint 8 completed:

- Ashtakavarga Foundation Constants
- Bhinnashtakavarga Rule Table
- Bhinnashtakavarga Calculation Foundation
- Sarvashtakavarga Calculation Foundation
- Ashtakavarga Summary Builder
- Internal Kundali Ashtakavarga Integration
- Optional Kundali API Ashtakavarga Exposure with `include_ashtakavarga`
- Validation Coverage
- Regression Coverage
- Sprint 8 documentation and completion checklist

Sprint 9 completed:

- Arudha Lagna Foundation
- Upapada Lagna Foundation
- Hora Lagna Foundation
- Ghati Lagna Foundation
- Bhava Madhya / Cusp Foundation
- Special Lagna Summary Builder
- Internal Kundali Special Lagna Integration
- Optional Kundali API Special Lagna Exposure with `include_special_lagnas`
- Validation Coverage
- Regression Coverage
- Sprint 9 documentation and completion checklist

Sprint 10A completed:

- Prediction Result Schema Foundation
- Condition Engine Foundation
- Rule Engine Foundation
- Prediction Context Builder
- Analyzer Adapter Interfaces
- Prediction Composer Foundation
- Internal Kundali Prediction Framework Integration
- Optional Kundali API Prediction Framework Exposure with `include_predictions`
- Validation Coverage
- Regression Coverage
- Sprint 10A documentation and completion checklist

Sprint 10B completed:

- Prediction Rule Library architecture and documentation
- General Prediction Rule schema and validation helpers
- Prediction Rule Registry
- YAML Rule Loader foundation
- Career, Marriage, Finance, Health, Education, Children, Spirituality, and
  Personality rule library foundations
- Prediction category loader and evaluator integration
- Reusable structured Prediction Explanation layer
- Validation and regression coverage
- Sprint 10B documentation through Task 10B.14

## Current Sprint

Current sprint: Sprint 11 - Matchmaking Foundation. **Complete.**

Primary sprint document: `docs/SPRINT-11.md`.

Sprint 11 goal:

- Add reusable input and result schemas for future deterministic matchmaking.
- Consume existing birth and Kundali data without recalculating or mutating it.
- Keep compatibility calculations separate from prediction, API, report, and
  UI layers.
- Preserve backward compatibility for completed modules and existing APIs.

Completed tasks:
- **Task 11.1**: Initialize Matchmaking Foundation Architecture with JSON-safe
  person, pair, result, and metadata schemas and factories.
- **Task 11.2**: Add deterministic person and pair input validation with stable
  issue codes, normalized outputs, boundary checks, and duplicate ID detection.
- **Task 11.3**: Add Nakshatra identity and ordered pair-context foundations
  with zero-based indexes, circular distances, stable issue codes, and no Koota
  scoring or compatibility judgement.
- **Task 11.4**: Implement deterministic Varna Koota with one-based Rashi
  indexes, centralized Varna mapping/ranks, explicit scoring direction, and no
  final compatibility judgement.
- **Task 11.5**: Implement deterministic Vashya Koota from supplied sidereal
  Moon longitudes with reused Rashi normalization, split-sign classification,
  strict category validation, and explicit bride-row/groom-column scoring.
- **Task 11.6**: Implement deterministic Tara Koota with reused zero-based
  Nakshatra pair context, inclusive circular counting, modulo-9
  classification, explicit bidirectional roles, and `0.0`/`1.5`/`3.0` scoring.
- **Task 11.7**: Implement deterministic Yoni Koota with reused Nakshatra
  normalization, the canonical 27-star animal and Yoni-sex mapping, strict
  category validation, and the complete symmetric `14 x 14` scoring matrix.
- **Task 11.8**: Implement deterministic Graha Maitri Koota with reused
  Moon-Rashi derivation, Rashi lordship, permanent natural relationships,
  strict lord validation, and the complete symmetric `7 x 7` scoring matrix.
- **Task 11.9**: Implement deterministic Gana Koota with reused Nakshatra
  normalization and pair context, complete 27-star classification, strict
  category validation, and directional bride-row/groom-column scoring.
- **Task 11.10**: Implement deterministic Bhakoot Koota with reused full
  Moon-Rashi derivation, inclusive circular directional distances, the
  complete symmetric `12 x 12` base scoring convention, and no cancellation
  exceptions.
- **Task 11.11**: Implement deterministic Nadi Koota with reused Nakshatra
  normalization and pair context, complete 27-star classification, strict
  category validation, symmetric `0.0`/`8.0` scoring, and no cancellation
  exceptions.
- **Task 11.12**: Implement deterministic Ashtakoota aggregation over all eight
  completed Kootas with canonical ordering, raw and strict precomputed-result
  APIs, exact `math.fsum` totals, a fixed `36.0` maximum, and no partial score
  or interpretation behavior.
- **Task 11.13**: Implement deterministic Lagna-only Manglik classification
  and structured bride/groom status comparison using canonical whole-sign
  house placement, the binary five-house convention, strict chart and
  precomputed-result validation, and no score, cancellation, or marriage
  judgement.
- **Task 11.14**: Implement deterministic structured compatibility report
  composition through separated raw, strict precomputed, and serialization
  APIs, reusing completed Ashtakoota and Manglik results without adding a
  combined score, interpretation, verdict, recommendation, or rendering.
- **Task 11.15**: Harden serialization for every Sprint 11 matchmaking result
  family with strict recursive JSON validation and copying, exact schema and
  field-order enforcement, mutation isolation, additive public serializers,
  and full compatibility regression coverage.

Sprint 11 is complete. The next roadmap milestone is Sprint 12 - Report Data
Model Foundation; it is not begun by Task 11.15.

Before Sprint 12 begins, the Documentation Architecture Foundation establishes
ADRs, permanent-specification governance, and canonical test-vector standards.
The next documentation task is migration of the completed Matchmaking contract
to `docs/specifications/MATCHMAKING.md`; it does not start Sprint 12.

## Next Task Instructions

For each new Codex task:

1. Read this file.
2. Read the current sprint document.
3. Inspect the existing implementation before editing.
4. Add a reusable module only if one does not already exist.
5. Keep the change limited to the requested milestone.
6. Add or update focused tests only for the requested behavior.
7. Run the narrowest relevant tests while developing.
8. Run the full relevant suite before finishing code tasks.
9. Stop after the requested task is complete.

For documentation-only tasks:

- Do not modify source code.
- Do not modify tests.
- Run docs tooling only if the repository already defines it.
- Do not run runtime tests unless explicitly requested or required by the task.

## Stop Point Rules

Stop immediately after the current milestone is complete.

Do not continue into the next roadmap item without a new user instruction. Do
not add predictions, interpretation text, reports, UI, or API changes unless
they are part of the active task.

If a task reveals missing source verification:

- Document the gap.
- Add a placeholder only if required for structure.
- Keep tests skipped or focused on safe behavior.
- Do not mark the formula complete.

## Testing Rules

- No calculation is complete without focused tests.
- Use boundary tests for signs, degrees, wrapping, and invalid inputs.
- Preserve existing API response fields.
- Run relevant API tests when an API contract is touched.
- Run Panchang tests when Panchang behavior is touched.
- Run the full suite before finishing calculation or API milestones.
- Do not fake passing tests for unverified formulas.

Current known manual-validation policy:

- Manual astronomical validation remains separate from automated structural
  tests.
- Golden-value tests must stay skipped until values are verified against trusted
  references.

## Commit Message Rules

One task equals one commit.

Commit format:

```text
<type>(sprint-N): short task description
```

Recommended types:

- `feat`
- `fix`
- `test`
- `docs`
- `refactor`
- `chore`

Examples:

```text
docs(sprint-5): add varga roadmap
feat(sprint-5): add navamsa foundation
test(sprint-5): cover invalid varga numbers
fix(sprint-4): preserve kundali response shape
```

Before committing:

- Relevant tests pass, or docs-only tooling has been checked if available.
- `CHANGELOG.md` is updated when the task changes user-visible behavior or
  project documentation.
- No unrelated files are included.
- No generated files, local secrets, virtualenvs, caches, or Swiss Ephemeris
  data files are included.
