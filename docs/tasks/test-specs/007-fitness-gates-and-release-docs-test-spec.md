# Test Spec 007: Fitness Gate Wiring, Full Open-Source `README.md`, and Release Prep

- **Task:** `docs/tasks/backlog/007-fitness-gates-and-release-docs.md`
- **Test file:** `tests/test_task_007_integration.py`

## Requirements

- **REQ-007-01:** `Makefile` and `docs/spec/fitness-functions.md` wire all six fitness rules (`F-001`..`F-006`: task-state invariant, Mermaid hygiene, Antigravity adapter sync, skill package validation via `validate_skill.py`, prose hygiene check, and sample regression suite) as active targets under `make fitness`, and `make check` exits `0`.
- **REQ-007-02:** `README.md` is a complete open-source landing page matching `tkdtaylor` skill repo conventions: badges, one-sentence value proposition, Mermaid architecture flow, modes and genre coverage overview, cross-harness installation instructions (Claude Code, Google Antigravity, OpenAI Codex, Cursor, GitHub Copilot, Windsurf), slash commands and natural-language triggers, CLI diagnostic usage, calibration sample summary, accurate repo structure tree, prior-art attribution (`addyosmani/clarity` and `cursor/plugins/pstack`), and links to `docs/architecture/overview.md`, `docs/architecture/diagrams.md`, `docs/spec/SPEC.md`, `docs/plans/roadmap.md`, `SECURITY.md`, `CONTRIBUTING.md`, and `LICENSE`.
- **REQ-007-03:** `CHANGELOG.md` documents all Version 1 components under `## [Unreleased]`, and end-to-end integration tests verify `strip_markdown.py` -> `prose_lint.py`, `validate_skill.py`, and `make fitness` across the complete repository.

## Test Cases

| ID | Requirement | Input / Target | Expected Assertion |
|----|-------------|----------------|--------------------|
| `TC-007-01` | `REQ-007-01` | `Makefile` and `docs/spec/fitness-functions.md` | All `F-001`..`F-006` rows in `fitness-functions.md` are `Active`, `Makefile` defines matching `fitness-*` targets, and `make fitness` exits `0` |
| `TC-007-02` | `REQ-007-02` | `README.md` | Contains required sections, cross-harness install blocks, prior-art links to `clarity` and `pstack`, all 4 required `docs/` links, Mermaid diagram passing `check-mermaid.py`, and passes `validate_skill.py` |
| `TC-007-03` | `REQ-007-03` | `CHANGELOG.md` + end-to-end CLI pipeline | `CHANGELOG.md` lists `SKILL.md`, `references/`, `scripts/`, `evals/`, and `samples/`; `strip_markdown.py README.md \| prose_lint.py --raw --json` and `validate_skill.py --json` both exit `0` |
