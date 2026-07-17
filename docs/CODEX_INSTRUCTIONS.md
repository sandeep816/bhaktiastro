# BhaktiAstro Codex Instructions

These instructions apply to every Codex task in the BhaktiAstro repository.

## 1. Read Documentation First

Before making any change, read:

* `docs/MASTER.md`
* `docs/ROADMAP.md`
* the current sprint document, such as `docs/SPRINT-11.md`
* any task-runner document explicitly named by the user

Treat repository documentation as the source of truth.

If documentation conflicts with the user prompt, stop and report the conflict before changing code.

## 2. Inspect Before Editing

Before implementation, inspect:

* current Git branch
* Git working-tree status
* recent commits
* existing modules related to the task
* existing tests
* public exports
* reusable constants, models, helpers, and validation structures

Use commands such as:

```bash
git status
git branch --show-current
git log --oneline --decorate -15
```

Do not assume a module is missing without searching for it.

## 3. One Task Per Run

Implement exactly one task per Codex run.

For each run:

1. Identify the first incomplete task in the current sprint.
2. Confirm its documented scope.
3. Implement only that task.
4. Add or update focused tests.
5. Run focused tests.
6. Run relevant regression tests.
7. Run the full test suite.
8. Update documentation.
9. Create one focused commit.
10. Stop.

Do not automatically start the next task.

## 4. Preserve Existing Work

* Do not rewrite completed modules.
* Do not duplicate existing functionality.
* Do not rename public APIs without a documented requirement.
* Preserve backward compatibility.
* Follow the existing project structure.
* Prefer small incremental changes.
* Reuse existing models, schemas, constants, helpers, and factories.
* Do not perform unrelated refactoring.
* Do not apply broad formatting changes.
* Do not remove tests merely to make the suite pass.

## 5. Git Safety

Before implementation:

* The working tree should be clean.
* The current branch must be suitable for the selected task.
* The previous task dependency must already exist in the current branch.

Do not:

* force-push
* rewrite shared history
* amend previous task commits
* rebase shared branches
* merge unrelated branches
* commit unrelated files

Use one focused commit per task.

Preferred branch format:

```text
feature/sprint-<sprint>-<task>-<short-name>
```

Example:

```text
feature/sprint-11-4-varna-koota
```

Preferred commit format:

```text
feat(<scope>): <task-specific summary>
```

Do not push unless the user explicitly asks Codex to push.

## 6. Implementation Standards

All new implementation must:

* be deterministic where calculations are deterministic
* use explicit typing
* remain JSON-safe where structured output is expected
* avoid mutating caller input
* avoid shared mutable defaults
* preserve stable output ordering
* use machine-readable identifiers
* use localization-ready message keys for validation issues
* fail safely for invalid or missing input
* include focused tests
* follow existing repository conventions

Do not introduce a new dependency unless the task explicitly requires it and no existing solution is available.

## 7. Architecture Boundaries

Keep these layers separate:

```text
core calculations
validation and normalization
domain orchestration
serialization
API
UI and presentation
interpretation
```

Do not mix API, UI, report formatting, prediction prose, or interpretation text into deterministic calculation modules.

Do not add future-sprint functionality early.

## 8. Matchmaking Rules

For matchmaking tasks:

* Preserve `person_a` and `person_b` ordering.
* Do not infer gender.
* Do not infer bride or groom roles.
* Do not infer missing astrology values unless the task explicitly requires calculation.
* Reuse existing Rashi and Nakshatra constants.
* Do not duplicate Koota mappings.
* Do not calculate later Kootas early.
* Do not produce a final compatibility judgement unless explicitly required by the current task.
* Do not add remedies or interpretive prose to calculator modules.

## 9. Testing Requirements

Run focused tests first:

```bash
python -m pytest -q <focused-test-files>
```

Then run relevant regression tests.

Finally run the complete suite:

```bash
python -m pytest -q
```

Do not report success unless the required tests actually pass.

If unrelated pre-existing failures occur:

* do not hide them
* do not modify unrelated code
* report the failing tests
* stop if safe verification is impossible

Use only quality tools already configured in the repository.

## 10. Documentation Rules

Update only relevant documentation.

Usually this includes:

* the current sprint document
* `docs/MASTER.md`

Requirements:

* Mark only the completed task as complete.
* Preserve previous task history.
* Record focused and full test results.
* Do not mark future tasks complete.
* Do not mark a sprint complete until every documented sprint task is complete.

## 11. Stop Conditions

Stop before implementation when:

* documentation conflicts
* the task scope is missing or ambiguous
* the working tree contains unrelated changes
* the current branch is unsuitable
* the previous task dependency is missing
* the functionality already exists
* implementation would break a public contract
* repository conventions cannot be determined safely

When stopping, report:

1. What was found
2. Relevant files
3. Why implementation should not continue
4. The smallest safe next action
5. Exact commands where applicable

## 12. Required Final Report

After completing one task, provide:

1. Selected task number and title
2. Repository inspection summary
3. Confirmed scope
4. Implementation summary
5. Files added
6. Files updated
7. Tests added or updated
8. Commands executed
9. Focused test results
10. Regression test results
11. Full test results
12. Backward-compatibility confirmation
13. Documentation changes
14. Commit hash and commit message
15. Exact push command
16. Next incomplete task identified but not implemented

Then stop.