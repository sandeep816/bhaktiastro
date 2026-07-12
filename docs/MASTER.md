# BhaktiAstro Master Working Document

This document is the Codex working brief for the BhaktiAstro repository. Use it
to keep each task scoped, testable, and aligned with the deterministic-first
project rules.

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

## Current Sprint

Current sprint: Sprint 10B - Prediction Rules Foundation.

Primary sprint document: `docs/SPRINT-10B.md`.

Sprint 10B goal:

- Add deterministic, data-driven prediction rule foundations on top of the
  completed Sprint 10A framework.
- Keep rules structured, testable, and free of generated interpretation text.
- Keep AI-generated summaries outside the core prediction engine.
- Reuse existing Panchang, Kundali, Varga, Dasha, Strength, Ashtakavarga, and
  special Lagna foundations.
- Preserve backward compatibility for all existing APIs.

Completed tasks:
- **Task 10B.1**: Initialize Prediction Rule Library architecture and folders (docs/prediction_rules.md).
- **Task 10B.2**: Implement reusable General Prediction Rule schema and validation helpers (backend/app/prediction/schema.py).
- **Task 10B.3**: Implement reusable Prediction Rule Registry (backend/app/prediction/registry.py).
- **Task 10B.4**: Implement YAML Rule Loader foundation (backend/app/prediction/loader.py).
- **Task 10B.5**: Implement Career Rule Library foundation with a small validated starter rule set (backend/app/prediction/prediction_rules/career/career_rules.yaml).
- **Task 10B.6**: Implement Marriage Rule Library foundation with a small validated starter rule set (backend/app/prediction/prediction_rules/marriage/marriage_rules.yaml).
- **Task 10B.7**: Implement Finance Rule Library foundation with a small validated starter rule set (backend/app/prediction/prediction_rules/finance/finance_rules.yaml).
- **Task 10B.8**: Implement Health Rule Library foundation with a small validated starter rule set (backend/app/prediction/prediction_rules/health/health_rules.yaml).
- **Task 10B.9**: Implement Education Rule Library foundation with a small validated starter rule set (backend/app/prediction/prediction_rules/education/education_rules.yaml).

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
