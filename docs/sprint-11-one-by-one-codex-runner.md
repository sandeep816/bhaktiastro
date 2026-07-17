# BhaktiAstro — Sprint 11 One-by-One Codex Runner

Use this same prompt every time you want Codex to execute the next Sprint 11 task.

---

You are working on the BhaktiAstro repository.

## Objective

Find and implement exactly **one next incomplete Sprint 11 task**.

Do not ask the user to provide the next task number when it can be determined from repository documentation.

## Source of Truth

Read these files first:

- `CODEX_INSTRUCTIONS.md`
- `docs/MASTER.md`
- `docs/ROADMAP.md`
- `docs/SPRINT-11.md`

Then inspect:

- `backend/app/matchmaking/`
- relevant files under `backend/app/constants/`
- relevant files under `backend/app/astrology/`
- relevant files under `backend/app/kundali/`
- existing matchmaking tests
- recent Git history

Repository documentation and completed implementation are the source of truth.

## Current Sprint

Sprint 11 — Matchmaking Foundation

Expected roadmap currently includes:

- 11.1 Matchmaking foundation architecture
- 11.2 Matchmaking input validation
- 11.3 Nakshatra compatibility foundation
- 11.4 Varna Koota
- 11.5 Vashya Koota
- 11.6 Tara Koota
- 11.7 Yoni Koota
- 11.8 Graha Maitri Koota
- 11.9 Gana Koota
- 11.10 Bhakoot Koota
- 11.11 Nadi Koota
- 11.12 Ashtakoota aggregation
- 11.13 Manglik compatibility foundation
- 11.14 Matchmaking summary composer
- 11.15 Serialization and compatibility hardening

If `docs/SPRINT-11.md` defines a different sequence, follow the repository document instead of this list.

## Mandatory Execution Rule

Implement exactly **one task per run**:

1. Detect the first incomplete Sprint 11 task.
2. Confirm its documented scope.
3. Implement only that task.
4. Add or update focused tests.
5. Run focused tests.
6. Run relevant regression tests.
7. Run the full test suite.
8. Update Sprint documentation.
9. Commit the completed task.
10. Stop.

Never continue automatically to the following task in the same run.

## Git Safety

Start by running:

```bash
git status
git branch --show-current
git log --oneline --decorate -15
```

Rules:

- The working tree must be clean before beginning.
- Do not rewrite or amend previous task commits.
- Do not force-push.
- Do not rebase shared branches.
- Do not merge unrelated branches.
- One task must produce one focused commit.
- Do not push unless the user explicitly instructed you to push.
- If the current branch is unsuitable, stop before editing and provide the exact branch commands the user should run.
- Prefer a branch name in this form:

```text
feature/sprint-11-<task-number>-<short-task-name>
```

Example:

```text
feature/sprint-11-4-varna-koota
```

If the previous task is not available in the current branch or `main`, stop and report the dependency instead of recreating it.

## Architecture Rules

- Inspect existing code before adding files.
- Do not redesign completed architecture.
- Do not rewrite completed modules.
- Do not duplicate constants, mappings, schemas, normalization, validation, or calculators.
- Preserve backward compatibility.
- Keep changes small and incremental.
- Reuse existing matchmaking foundation types and result structures.
- Reuse core Rashi and Nakshatra constants.
- Keep deterministic calculations independent from API, UI, reports, and prose.
- Do not add AI-generated output.
- Do not add remedies.
- Do not infer gender, bride/groom roles, or person ordering.
- Preserve `person_a` and `person_b` order.
- Do not implement later Kootas or aggregation early.
- Do not perform unrelated formatting or refactoring.

## Task Inspection

Before editing, report briefly:

1. The next incomplete task number and title
2. Its exact documented goal
3. Existing reusable modules
4. Files expected to change
5. Backward-compatibility risks
6. Focused tests to add or update

If the task is missing, ambiguous, conflicts with existing implementation, or requires breaking a public contract, stop and report the smallest safe next action.

## Implementation Standards

For the selected task:

- Follow the precise scope in `docs/SPRINT-11.md`.
- Use existing typing and normalization conventions.
- Keep output JSON-safe.
- Keep calculations deterministic.
- Do not mutate caller inputs.
- Avoid shared mutable defaults.
- Handle invalid and missing values safely.
- Use stable machine-readable identifiers.
- Use localization-ready message keys where validation issues are needed.
- Do not include user-facing interpretive paragraphs.
- Preserve deterministic output ordering.
- Export only stable public helpers from `backend/app/matchmaking/__init__.py`.

## Testing

Determine focused test files from the selected task.

Always run:

```bash
python -m pytest -q <focused matchmaking test files>
```

Then run relevant core regression tests, such as Rashi or Nakshatra tests when applicable.

Finally run:

```bash
python -m pytest -q
```

Use only quality tools already configured in the repository.

Do not hide failing tests.

If failures are unrelated and pre-existing, stop and report them clearly.

## Documentation

Update only the relevant sections of:

- `docs/SPRINT-11.md`
- `docs/MASTER.md`

Requirements:

- Mark only the implemented task complete.
- Record focused and full test results.
- Keep previous task history intact.
- Do not mark the next task complete.
- Do not mark Sprint 11 complete unless every documented Sprint 11 task is complete.

## Commit

After all required tests pass, create one commit using the repository’s existing style.

Preferred pattern:

```text
feat(matchmaking): <task-specific summary>
```

Do not combine unrelated changes.

## Stop Conditions

Stop without implementation when:

- the working tree is not clean
- the current branch is unsuitable
- the previous task dependency is missing
- Sprint documentation conflicts
- the selected task is already complete
- the task scope is undefined
- existing architecture already implements the same functionality
- a breaking change would be required
- an unrelated test failure blocks safe verification

When stopping, provide exact commands or the smallest corrective action.

## Final Response Format

After completing one task, provide:

1. Selected task
2. Repository inspection summary
3. Implementation summary
4. Files added
5. Files updated
6. Tests added or updated
7. Commands executed
8. Focused test results
9. Regression test results
10. Full test results
11. Backward-compatibility confirmation
12. Documentation changes
13. Commit hash and message
14. Exact push command
15. Next incomplete task identified, but **not implemented**

Then stop.
