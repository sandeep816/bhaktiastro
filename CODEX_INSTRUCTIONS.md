# CODEX_INSTRUCTIONS.md - BhaktiAstro Project Rules

> Source documents read before creating this file:
> - `FEATURES_v3.md` (the available file whose heading is `FEATURES.md`; exact `FEATURES.md` filename was not present)
> - `CALCULATIONS.md`
> - `PROJECT_PHASES.md`

These rules apply to every Codex task in the BhaktiAstro / Vedic Astrology Engine project.

---

## 1. Project Goal

Build a free, open-source, local Python-based Vedic Astrology Engine for Panchang, Kundali, Dasha, Yoga/Dosha, Muhurat, Matchmaking, reports, and future BhaktiRas integration.

The engine must be deterministic, testable, locally runnable, and API-ready. Core calculations must run locally with Python and Swiss Ephemeris / `pyswisseph`; no paid astrology API may be required for calculation.

Primary future surfaces:
- FastAPI REST API under `/api/v1/`
- HTML/PDF reports
- Web UI / PWA
- BhaktiRas.in integration
- Optional AI explanation layer after deterministic results exist

---

## 2. Core Architecture Rules

Maintain strict layer separation:

1. Input layer
   - Date, time, place, latitude, longitude, timezone, ayanamsa, language.

2. Astronomy layer: `backend/app/astronomy/`
   - Pure astronomical calculations only.
   - Julian Day, UTC conversion, Ayanamsa, Swiss Ephemeris setup, planetary positions, rise/set, boundary search helpers.

3. Astrology calculation layer: `backend/app/astrology/`
   - Deterministic Vedic astrology values derived from astronomy output.
   - Tithi, Nakshatra, Yoga, Karana, Vara, Lagna, houses, Dasha, Varga, Panchang, Kundali assembly.

4. Constants layer: `backend/app/constants/`
   - Static domain data only: rashis, planets, nakshatras, tithis, yogas, dashas, dignity tables, language keys.

5. Rules engine layer: `backend/app/rules/`
   - Deterministic rule detection only.
   - Yoga rules, Dosha rules, planet/house rules, matchmaking rules, muhurat filters.

6. Interpretation layer: `backend/app/interpretation/`
   - Textual explanation only.
   - No calculation logic and no mutation of calculated values.

7. Reports layer: `backend/app/reports/`
   - HTML, PDF, Markdown, JSON, DOCX generation from already-calculated data.

8. API layer: `backend/app/api/v1/`
   - Versioned FastAPI routes only.
   - Use Pydantic schemas from `backend/app/schemas/`.

9. Optional AI layer
   - Last-stage explanation only.
   - Must never calculate, correct, override, or infer astrology data.

---

## 3. Calculation Rules

- Swiss Ephemeris / `pyswisseph` is the source for astronomy calculations.
- Default ayanamsa is Lahiri / Chitrapaksha, configurable from settings.
- Always normalize longitudes into the `0 <= longitude < 360` range.
- Timezone must always be explicit. Never assume timezone from date or place unless a dedicated timezone lookup task exists.
- Convert local datetime to UTC before Julian Day and ephemeris calls.
- Use `timezonefinder` / `pytz` or equivalent validated handling for DST cases.
- Ketu is calculated as Rahu + 180 degrees, normalized.
- Whole Sign houses are used for Vedic house placement unless a task explicitly says otherwise.
- Tolerances must follow `CALCULATIONS.md` and the feature roadmap:
  - Planet longitude: 0.05 degrees MVP, 0.01 degrees stable.
  - Sunrise/Sunset: 2 minutes MVP, 1 minute stable.
  - Tithi/Nakshatra/Yoga boundary: 5 minutes MVP, 2 minutes stable.
  - Lagna: 0.25 degrees MVP, 0.1 degrees stable.

---

## 4. Deterministic Calculation First, Interpretation Later

The project must be built in this order:

1. Deterministic astronomy calculations.
2. Deterministic astrology calculations.
3. Deterministic rule detection.
4. Stable JSON/API output.
5. Reports and UI.
6. Interpretation text.
7. Optional AI explanation.

Do not add interpretive text, predictions, remedies, AI summaries, or report prose before the underlying calculation and rule outputs are deterministic, tested, and verified.

---

## 5. AI Rules

- AI must not calculate astrology.
- AI must not calculate planetary positions, tithi, nakshatra, yoga, karana, lagna, houses, dasha, varga, aspects, strengths, doshas, muhurat, or matchmaking values.
- AI must not receive raw degrees unless a future reviewed design explicitly permits it for explanation-only context.
- AI must not override deterministic data.
- AI output must be generated only from already-calculated interpretation-module output.
- Any AI-generated text must be tagged as AI-generated.

---

## 6. Never Guess Astrology Formulas

Never guess astrology formulas.

If a formula, mapping, boundary rule, tradition, or source is not verified:

1. Create a placeholder function only if needed.
2. Add a clear TODO with the required source verification.
3. Add or keep tests skipped with `@pytest.mark.skip(reason="Formula not verified")`.
4. Do not return fake values.
5. Do not mark the feature complete.
6. Do not silently choose one tradition when the docs say traditions vary.

Every calculation should be verified against at least two trusted references where practical:
- Jagannatha Hora
- Astro-Seek
- Drik Panchang
- Trusted printed Panchang or classical source

---

## 7. One Task At A Time

Work on exactly one task/module at a time.

- Complete the current task before starting the next one.
- Run relevant tests before considering a task done.
- Do not bundle unrelated refactors.
- Do not jump ahead to later phases.
- Keep commits scoped: one task = one commit.
- If a requested change spans phases, split it into explicit tasks and finish them sequentially.

---

## 8. Coding Standards

- Use Python 3.11+.
- Prefer simple, typed, deterministic functions.
- Keep calculation functions pure where possible.
- Use Pydantic v2 for API request/response schemas.
- Keep API routes thin; put business logic in astronomy, astrology, rules, or service modules.
- Keep constants in `backend/app/constants/`, not scattered through calculation code.
- Use config values for ayanamsa, ephemeris path, language defaults, tolerances, and app metadata.
- Do not hard-code user-specific paths.
- Do not hard-code Lahiri everywhere; use the configured default and preserve the `ayanamsa` parameter.
- Include Hindi and English output fields where the roadmap requires multilingual readiness.
- Use clear names for degrees:
  - `tropical_longitude`
  - `sidereal_longitude`
  - `degree_in_rashi`
  - `rashi_index`
- Preserve stable JSON structures. Breaking output changes require explicit approval and versioning.
- Hindi comments are allowed when they clarify domain logic.
- Avoid unnecessary abstractions until repeated patterns or phase boundaries justify them.

---

## 9. Testing Rules

No calculation is done without tests.

Required test types:
- Unit tests for helper functions and formulas.
- Boundary tests for degrees, signs, nakshatras, tithis, padas, time boundaries, and date crossings.
- Known-value tests from `CALCULATIONS.md`.
- Integration tests for API endpoints when an API task is implemented.
- Golden fixture tests for verified charts and Panchang outputs.

Required golden fixtures:
- Jodhpur, 20 Apr 1985, 18:10 IST.
- Delhi, 1 Jan 2000, 12:00 IST.
- Mumbai, 15 Jun 1990, 06:30 IST.
- London, 26 Mar 1995, 02:00 BST.
- New York, 1 Nov 2000, 01:30 EST.

Testing expectations:
- Run the narrowest relevant tests while developing.
- Run the full relevant test suite before committing.
- Coverage target for MVP is at least 85%.
- Mark unverified formula tests skipped; never fake passing tests.
- Include edge cases:
  - Midnight birth.
  - Noon birth.
  - Timezone crossing date boundary.
  - DST start/end.
  - Longitude wrapping around 0/360 degrees.
  - Exact rashi/nakshatra/tithi boundaries.

---

## 10. Git Workflow

- One task = one commit.
- Before each commit:
  - Code runs.
  - Relevant tests pass.
  - `CHANGELOG.md` is updated.
  - No unverified calculation is marked done.
  - Generated files are not accidentally committed.
- Do not commit Swiss Ephemeris `.se1` files.
- Do not commit generated reports, PDFs, caches, virtualenvs, or local secrets.
- Do not rewrite or revert user changes unless explicitly asked.
- If the working tree has unrelated changes, leave them alone.

---

## 11. Commit Message Format

Use this format:

```text
feat(phase-X): task description
```

Examples:

```text
feat(phase-0): create project folder structure
feat(phase-1): add julian day calculation with tests
fix(phase-2): correct tithi boundary tolerance
test(phase-5): add jodhpur kundali golden fixture
docs(phase-0): add codex project instructions
```

Use `feat`, `fix`, `test`, `docs`, `refactor`, or `chore` as appropriate.

---

## 12. What Not To Do

- Do not use paid astrology APIs for core calculation.
- Do not mix astronomy, astrology, rules, interpretation, reports, and API concerns.
- Do not let AI calculate astrology.
- Do not guess formulas.
- Do not ship placeholder logic as complete.
- Do not skip tests for implemented calculation logic.
- Do not silently assume timezone, ayanamsa, location, language, or tradition.
- Do not hard-code values that belong in config or constants.
- Do not pass raw planetary data to an AI explanation layer.
- Do not override deterministic calculation output with interpretation or AI.
- Do not add UI/report/prediction features before the underlying deterministic calculation is complete.
- Do not change stable API output shape casually.
- Do not commit generated reports, `.se1` ephemeris files, local env files, caches, or virtualenvs.
- Do not work on multiple phases or modules at once.

---

## 13. Completion Checklist For Any Task

Before calling a task complete:

- [ ] The task scope is one module or one phase task only.
- [ ] The implementation follows the documented layer boundaries.
- [ ] Formula source is verified or clearly marked TODO/skipped.
- [ ] Deterministic calculation is implemented before interpretation.
- [ ] Timezone and UTC handling are explicit where relevant.
- [ ] Tests cover normal and boundary cases.
- [ ] Golden fixture is updated when required.
- [ ] Relevant tests pass.
- [ ] `CHANGELOG.md` is updated for commit-ready changes.
- [ ] No unrelated files were changed.

