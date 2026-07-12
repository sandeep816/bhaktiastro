# Sprint 10B - Prediction Rules Foundation

Sprint 10B builds on the deterministic Prediction Framework established in Sprint 10A by adding prediction rule foundations, schemas, and library architecture.

## Sprint Status

Status: **In Progress**

Sprint 10B focuses on moving prediction logic out of hardcoded Python execution and into structured, data-driven rules.

## Sprint Goals

- Establish a reusable, declarative astrology Prediction Rule Library.
- Define a standard schema for prediction rules mapping context fields to deterministic outcomes.
- Enable priority-based sorting and condition evaluations.
- Ensure no runtime regressions or changes to astronomical/panchang/chart calculation engines.
- Keep rules clean of free-form prose and AI summaries.

---

## Task Breakdown

### Task 10B.1 - Prediction Rule Library Architecture
Goal: Define the library structure, naming conventions, schemas, compatibility rules, and initialize the directories.

**Status**: In Progress

**Acceptance checklist**:
- [x] Create rule library folder under `backend/app/prediction/prediction_rules/`.
- [x] Create category subdirectories: `career`, `marriage`, `finance`, `health`, `education`, `children`, `spiritual`, `raj_yoga`, `dhana_yoga`, `general`.
- [x] Create architecture documentation `docs/prediction_rules.md`.
- [x] Define naming, versioning, priority, and deterministic rules philosophy.
- [x] Define standard rule schema and compatibility rules.
- [x] Define regression checklist.
- [x] No runtime source code or tests are changed.
- [x] Full existing test suite passes.

---

## Validation Checklist

For each Sprint 10B implementation milestone:
- [ ] Existing Panchang tests pass.
- [ ] Existing Kundali tests pass.
- [ ] Existing Varga tests pass.
- [ ] Existing Dasha tests pass.
- [ ] Existing Strength tests pass.
- [ ] Existing Ashtakavarga tests pass.
- [ ] Existing Lagna tests pass.
- [ ] New prediction framework/rule tests pass.
- [ ] Full suite passes before marking complete.
