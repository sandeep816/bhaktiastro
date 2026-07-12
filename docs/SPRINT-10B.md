# Sprint 10B - Prediction Rules Foundation

Sprint 10B builds on the deterministic Prediction Framework established in Sprint 10A by adding prediction rule foundations, schemas, and library architecture.

## Sprint Status

Status: **In Progress (Task 10B.8 Complete)**

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

### Task 10B.4 - YAML Rule Loader foundation
Goal: Create a reusable YAML loader to parse, validate, and register rules from files and directories.

**Status**: Complete

**Acceptance checklist**:
- [x] Implement `load_rule`, `load_rules`, and `load_rules_from_yaml` in `loader.py`.
- [x] Integrate schema validation helpers to validate loaded rules.
- [x] Register valid rules automatically.
- [x] Avoid crashing on malformed YAML (collect structured validation errors).
- [x] Support traversing folders recursively to load multiple files.
- [x] Ensure loader outputs remain JSON-safe.
- [x] Add focused tests in `backend/tests/test_prediction_loader.py`.
- [x] Verify all tests pass.

### Task 10B.5 - Career Rule Library foundation
Goal: Implement Career Rule Library foundation with a small validated starter rule set of 5 rules.

**Status**: Complete

**Acceptance checklist**:
- [x] Create career rules directory under `backend/app/prediction/prediction_rules/career/`.
- [x] Add 5 starter rules in `career_rules.yaml` following universal schema and naming conventions (`career.001` through `career.005`).
- [x] Use existing context builder dot-key naming conventions without modification.
- [x] Integrate with registry and generic YAML loader.
- [x] Ensure rules do not contain definitive promises and remain purely astrological indicators.
- [x] Add unit tests in `backend/tests/test_career_rules.py` covering matching and non-matching synthetic contexts.
- [x] Verify all tests pass.

### Task 10B.6 - Marriage Rule Library foundation
Goal: Implement Marriage Rule Library foundation with a small validated starter rule set of 5 rules.

**Status**: Complete

**Acceptance checklist**:
- [x] Create marriage rules directory under `backend/app/prediction/prediction_rules/marriage/`.
- [x] Add 5 starter rules in `marriage_rules.yaml` following universal schema and naming conventions (`marriage.001` through `marriage.005`).
- [x] Use existing context builder dot-key naming conventions without modification.
- [x] Integrate with registry and generic YAML loader.
- [x] Ensure rules do not contain definitive promises and remain purely astrological indicators.
- [x] Add unit tests in `backend/tests/test_marriage_rules.py` covering matching and non-matching synthetic contexts.
- [x] Verify all tests pass.

### Task 10B.7 - Finance Rule Library foundation
Goal: Implement Finance Rule Library foundation with a small validated starter rule set of 5 rules.

**Status**: Complete

**Acceptance checklist**:
- [x] Create finance rules directory under `backend/app/prediction/prediction_rules/finance/`.
- [x] Add 5 starter rules in `finance_rules.yaml` following universal schema and naming conventions (`finance.001` through `finance.005`).
- [x] Use existing context builder dot-key naming conventions without modification.
- [x] Integrate with registry and generic YAML loader.
- [x] Ensure rules do not contain definitive promises and remain purely astrological indicators.
- [x] Add unit tests in `backend/tests/test_finance_rules.py` covering matching and non-matching synthetic contexts.
- [x] Verify all tests pass.

### Task 10B.8 - Health Rule Library foundation
Goal: Implement Health Rule Library foundation with a small validated starter rule set of 5 rules and safety disclaimers.

**Status**: Complete

**Acceptance checklist**:
- [x] Create health rules directory under `backend/app/prediction/prediction_rules/health/`.
- [x] Add 5 starter rules in `health_rules.yaml` following universal schema and naming conventions (`health.001` through `health.005`).
- [x] Integrate standard non-medical disclaimers into results metadata (`not_medical_advice` and `requires_professional_evaluation`).
- [x] Extend the rule engine to merge rule-defined results metadata into the evaluated outcome metadata.
- [x] Use existing context builder dot-key naming conventions without modification.
- [x] Integrate with registry and generic YAML loader.
- [x] Ensure rules do not contain definitive medical diagnoses or predictions.
- [x] Add unit tests in `backend/tests/test_health_rules.py` covering matching, non-matching, and disclaimer metadata validations.
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
