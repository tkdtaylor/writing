# Agent Rules and Retrospectives

This log captures project-specific failure modes and process rules surfaced at session start by `inject-retros.py`.

## Failure modes

### Parallel tasks editing shared tracker or spec files collide on merge

- **Symptom:** Parallel worktrees edit `docs/tasks/test-specs/coverage-tracker.md` or the same `docs/spec/*.md` file concurrently, producing merge conflicts when `scripts/finish-task.sh` runs.
- **Rule:** In parallel waves, executors skip editing `coverage-tracker.md` on task branches and write unit tests into task-scoped files (`tests/test_task_NNN_*.py`). The orchestrator updates `coverage-tracker.md` once per wave on `main` after `finish-task.sh` merges succeed.

### Prose hygiene regressions inside skill documentation

- **Symptom:** Contributors or agents introduce em dashes, 80-column hard-wrapped paragraphs, emoji bullets, or AI-tell filler into `SKILL.md`, `references/`, or `docs/`.
- **Rule:** Every Markdown file in this repo (except intentional `.before.md` negative fixtures) must avoid prose em dashes, keep paragraphs on single continuous lines, place a blank line before lists, and pass `python3 scripts/validate_skill.py`.
