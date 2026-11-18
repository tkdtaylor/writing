# Task 022: `v0.1.0` Release Hygiene across `CHANGELOG.md`, `README.md`, `AGENTS.md`, and `roadmap.md`

- **Priority:** P1
- **Model tier:** `fast` (`flash`)
- **Dependencies:** None (Wave 1)
- **Test spec:** `docs/tasks/test-specs/022-v010-release-prep-changelog-and-readme-test-spec.md`

## Objective

Prepare `CHANGELOG.md`, `README.md`, `AGENTS.md`, and `docs/plans/roadmap.md` for cutting the `v0.1.0` public release tag and GitHub Release so `README.md` no longer refers to `v0.1.0` as a future plan, `CHANGELOG.md` cuts `[0.1.0] - 2026-11-18` under `[Unreleased]`, and pinned `v0.1.0` tarball URLs are documented cleanly.

## Deliverables (exclusive file scope)

- `CHANGELOG.md`
- `README.md`
- `AGENTS.md`
- `docs/plans/roadmap.md`
- `tests/test_task_022_v010_release_hygiene.py`

Do not modify files owned by Task 021 (`scripts/*`, `docs/spec/*`, `tests/test_task_004*.py`..`test_task_020*.py`) or `coverage-tracker.md`. Keep every sentence `<= 35` words (`overloaded_sentences == []`), zero `U+2014` or `U+2013`, continuous single-line paragraphs, and blank lines before lists.

## Implementation details

1. **`CHANGELOG.md` (`REQ-022-01`):**
   - Keep `## [Unreleased]` at the top (required by Keep a Changelog and `tests/test_task_007_integration.py:230`).
   - Add `## [0.1.0] - 2026-11-18` right below `## [Unreleased]`, housing the `### Added` bullets (plus a bullet or updated `prose_lint.py` bullet covering `mixed_dialects`, conceptual-enumeration filtering in `--profile technical`, and regex hardening).
   - Add standard bottom reference links (`[Unreleased]: https://github.com/tkdtaylor/writing/compare/v0.1.0...HEAD` and `[0.1.0]: https://github.com/tkdtaylor/writing/releases/tag/v0.1.0`).
2. **`README.md`, `AGENTS.md`, and `docs/plans/roadmap.md` (`REQ-022-02`):**
   - `README.md:7`: Update Status callout to state `Release v0.1.0 is live on main` and point to `docs/plans/roadmap.md` for Milestone 2 corpus calibration (removing `"and v0.1.0 release plans"`).
   - `README.md` install section: Show the pinned `v0.1.0` tag tarball (`https://github.com/tkdtaylor/writing/archive/refs/tags/v0.1.0.tar.gz`) for reproducible installs alongside `https://github.com/tkdtaylor/writing/archive/refs/heads/main.tar.gz` for tracking `main` (be sure to keep `archive/refs/heads/main.tar.gz` present so `test_task_014` and `test_task_016` pass!).
   - `README.md` and `AGENTS.md`: Mention `mixed_dialects` among `prose_lint.py` diagnostics.
   - `docs/plans/roadmap.md`: Mark `## Milestone 1: Version 1 Core Skill and Diagnostic Suite (Completed - v0.1.0)` (adding Tasks `021` and `022`) and mark `## Milestone 2: Corpus Calibration and Iterative Refinement (Active)` (replacing `Tag v0.1.0 public release` with `Cut v0.2.0 release after first corpus calibration sweep`).
3. **Verification (`REQ-022-03`):**
   - Write `tests/test_task_022_v010_release_hygiene.py` verifying `TC-022-01`..`TC-022-03` (note: iterate dynamically over `[k for k, v in rep["mechanics_and_tells"].items() if isinstance(v, list)]` so your test works both before and after Task `021` merges `mixed_dialects`!).
   - Move this task file to `docs/tasks/completed/022-v010-release-prep-changelog-and-readme.md` via `git mv`.
   - Run `make check` and confirm exit `0`.
