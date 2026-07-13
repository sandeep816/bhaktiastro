# BhaktiAstro Prediction Rule Library Architecture

This document defines the architecture, design patterns, schema contracts, and governance rules for the BhaktiAstro **Prediction Rule Library**.

The Rule Library houses all astrology prediction rules as structured, declarative data definitions (typically JSON files) rather than hardcoded Python logic. This ensures that prediction conditions are transparent, reusable, and easy to maintain without altering the core execution engines.

---

## 1. Rule Library Philosophy

All rules in the library adhere to a **deterministic-first, data-driven philosophy**:

1. **No Hardcoded Logic**: Rules define criteria declaratively using fields and operators supported by the `Condition Engine`.
2. **Deterministic Inputs Only**: Rules only query verified astronomical calculations, Panchang elements, divisional charts (Vargas), dashas, house details, and planet strengths.
3. **No Interpretive Prose**: Rules return structured match states, facts, evidence, and reasons. Free-form text generation or AI summaries must stay strictly outside the rule evaluation loop.
4. **Traceability**: Every rule evaluation includes the exact conditions that matched or failed, providing a clear audit trail for the end-user.

---

## 2. Directory & Rule Organization

Rules are organized into subdirectories by their primary life/astrological domain under `backend/app/prediction/prediction_rules/`:

```text
prediction_rules/
├── career/        # Profession, status, government jobs, business
├── marriage/      # Relationship timing, spouse characteristics, compatibility
├── finance/       # Wealth, assets, income, financial stability
├── health/        # Physical strength, disease indications, recovery
├── education/     # Academic fields, success in studies, exams
├── children/      # Offspring, family growth
├── personality/   # Broad, non-diagnostic personality tendencies
├── spiritual/     # Spiritual inclination, meditation, renunciation
├── raj_yoga/      # Power, authority, and status-defining yogas
├── dhana_yoga/    # Wealth-creating yogas and combinations
└── general/       # Generic chart features and uncategorized foundations
```

### Naming Conventions
- **Filename Pattern**: `<category>_<subcategory>_<rule_identifier>.json` (e.g., `career_profession_government_job.json` or `marriage_timing_delay_saturn.json`).
- **File Format**: Lowercase snake_case exclusively.
- **Rule ID**: Must exactly match the filename without the `.json` extension (e.g., `career_profession_government_job`).

---

## 3. Rule Versioning

To ensure stability across client updates, rules are versioned using a dual-versioning system:

1. **Rule Schema Version (`schema_version`)**:
   - Tracks the version of the rule engine schema itself.
   - Initial version is `1`.
   - Increments when new structural fields or new condition engine operators are introduced.
2. **Rule Definition Version (`rule_version`)**:
   - Uses semantic versioning (`major.minor.patch`, e.g., `1.0.0`) inside the rule metadata.
   - **Patch**: Text changes or description updates.
   - **Minor**: Weight or priority changes.
   - **Major**: Condition changes that alter the rule matching logic.

---

## 4. Standard Rule Schema

All rules must conform to the following schema:

```json
{
  "id": "career_profession_government_job",
  "category": "career",
  "title": "Government Job Indication",
  "priority": 150,
  "schema_version": 1,
  "rule_version": "1.0.0",
  "conditions": {
    "operator": "all_of",
    "conditions": [
      {
        "field": "planets.sun.house",
        "operator": "equals",
        "value": 10
      },
      {
        "field": "planets.sun.dignity.is_exalted",
        "operator": "equals",
        "value": true
      }
    ]
  },
  "result": {
    "status": "present",
    "supporting_factors": [
      "Sun is placed in the 10th house",
      "Sun is exalted"
    ],
    "challenging_factors": [],
    "metadata": {
      "source_text": "Brihat Parashara Hora Shastra",
      "chapter": 24,
      "sloka": 12
    }
  }
}
```

### Schema Details
- **`id`** (`str`, required): The unique key of the rule (lowercase snake_case).
- **`category`** (`str`, required): One of the defined domain folders (e.g., `career`).
- **`title`** (`str`, required): User-friendly display title of the rule.
- **`priority`** (`int`, required): Numeric precedence for ordering rule evaluation (default: `100`).
- **`schema_version`** (`int`, required): Schema compatibility number.
- **`rule_version`** (`str`, required): Semantic version of this rule definition.
- **`conditions`** (`dict`, required): Map of conditions evaluated by the Condition Engine. Can use `all_of`, `any_of`, or direct field evaluations.
- **`result`** (`dict`, required): Expected structure returned when the rule is present. Contains facts, factors, and metadata.

---

## 5. Priorities and Ordering

Rules are evaluated in order of priority, from highest to lowest. This helps compose reports where higher-impact rules (e.g., Raj Yogas) take precedence over general house placements.

| Priority Range | Classification | Purpose / Use Case |
|---|---|---|
| **500+** | Critical | Core planetary strengths/weaknesses (e.g., Neechbhanga Raja Yoga) |
| **300 - 499**| High | Specific major yogas (e.g., Gajakesari Yoga, Panch Mahapurusha Yogas) |
| **100 - 299**| Medium | Standard house/planet combinations (e.g., Sun in 10th) |
| **0 - 99** | Low / General | Baseline rules, generic bhava analysis |

---

## 6. Future Compatibility Rules

To prevent breaking changes as the platform grows, we establish the following compatibility guidelines:

> [!IMPORTANT]
> - **Schema Evolution**: The engine must remain backward-compatible with older `schema_version` rules. If a schema version is deprecated, a converter must be registered to upgrade old rules on load.
> - **Unknown Fields**: The Rule Engine must ignore unrecognized fields in the rule definitions rather than throwing runtime errors.
> - **Safe Defending**: If a rule references a context field that does not exist (e.g., a special Lagna not computed for a partial chart), the condition engine must evaluate that condition as `not_exists` or `unknown` safely instead of crashing.
> - **Deterministic Operator Gating**: Only operators registered in `backend/app/prediction/conditions.py` (e.g., `equals`, `contains`, `exists`) can be used. New operators require a core code change and a `schema_version` increment.

---

## 7. Regression Checklist

Before committing any new rules or rule engine modifications, run through this checklist:

- [ ] **Schema Validation**: The rule file passes schema checks (does not contain syntax errors, missing fields, or incorrect types).
- [ ] **No Side Effects**: The rule evaluation does not mutate the chart data or prediction context.
- [ ] **Context-Safe**: The rule handles missing context variables gracefully (fails the condition cleanly without throwing exceptions).
- [ ] **Performance Check**: The rule does not cause exponential backtracking (avoid deeply nested conditions where possible).
- [ ] **Test Coverage**: Existing test suite passes with the rule files registered:
  ```bash
  pytest backend/tests/
  ```
- [ ] **JSON Serialization**: Rule output remains fully JSON-safe and serializable.
