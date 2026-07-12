# Sprint 10B - Prediction Rules Foundation

Sprint 10B builds on the deterministic Prediction Framework established in Sprint 10A by adding prediction rule foundations, schemas, and library architecture.

## Sprint Status

Status: **In Progress (Task 10B.3 Complete)**

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

**Status**: Complete

**Acceptance checklist**:
- [x] Create rule library folder under `backend/app/prediction/prediction_rules/`.
- [x] Create category subdirectories: `career`, `marriage`, `finance`, `health`, `education`, `children`, `spiritual`, `raj_yoga`, `dhana_yoga`, `general`.
- [x] Create architecture documentation `docs/prediction_rules.md`.
- [x] Define naming, versioning, priority, and deterministic rules philosophy.
- [x] Define standard rule schema and compatibility rules.
- [x] Define regression checklist.
- [x] No runtime source code or tests are changed.
- [x] Full existing test suite passes.

### Task 10B.2 - Universal Prediction Rule Schema
Goal: Define the reusable schema, TypedDict, Pydantic model, and implement validation helpers.

**Status**: Complete

**Acceptance checklist**:
- [x] Create universal rule schema structure (`schema.py`).
- [x] Support TypedDict `PredictionRule` and Pydantic model `PredictionRuleModel`.
- [x] Implement validation helpers: `validate_rule`, `validate_rule_id`, `validate_priority`, `validate_category`.
- [x] Enforce: id must be unique string, priority must be integer, category/conditions/result required.
- [x] Ensure JSON-safe serialization.
- [x] Add unit tests in `backend/tests/test_prediction_schema.py`.
- [x] Verify all tests pass.

### Task 10B.3 - Prediction Rule Registry
Goal: Create a reusable in-memory registry to collect, validate, and retrieve prediction rules.

**Status**: Complete

**Acceptance checklist**:
- [x] Implement `register_rule`, `register_rules`, `get_registered_rules`, and `clear_rule_registry` in `registry.py`.
- [x] Prevent duplicate rule IDs across registrations.
- [x] Support filtering of retrieved rules by category.
- [x] Return deep copies of rules to prevent external mutation of registry state.
- [x] Ensure registry outputs remain JSON-safe.
- [x] Add focused tests in `backend/tests/test_prediction_registry.py`.
- [x] Verify all tests pass.

---

## Validation Checklist

For each Sprint 10B implementation milestone:
- [x] Existing Panchang tests pass.
- [x] Existing Kundali tests pass.
- [x] Existing Varga tests pass.
- [x] Existing Dasha tests pass.
- [x] Existing Strength tests pass.
- [x] Existing Ashtakavarga tests pass.
- [x] Existing Lagna tests pass.
- [x] New prediction framework/rule tests pass.
- [x] Full suite passes before marking complete.
