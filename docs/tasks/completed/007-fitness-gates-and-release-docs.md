# Task 007: Fitness Gate Wiring, Full Open-Source `README.md`, and Release Prep

- **Priority:** P1
- **Model tier:** `balanced`
- **Dependencies:** Tasks `005`, `006` (Wave 3 final integration)
- **Test spec:** `docs/tasks/test-specs/007-fitness-gates-and-release-docs-test-spec.md`

## Objective

Wire all six executable fitness functions (`F-001`..`F-006`) into `Makefile` and `docs/spec/fitness-functions.md`, author the complete open-source `README.md` matching `tkdtaylor` skill repositories, update `CHANGELOG.md`, and verify end-to-end integration.

## Deliverables (exclusive file scope)

- `Makefile`
- `docs/spec/fitness-functions.md`
- `README.md`
- `CHANGELOG.md`
- `tests/test_task_007_integration.py`

Do not edit `docs/tasks/test-specs/coverage-tracker.md` on the task branch (the orchestrator updates it after verification).

## Implementation details

1. **Fitness gates (`Makefile` + `docs/spec/fitness-functions.md`):**
   - Wire `fitness-task-state` (`F-001`), `fitness-mermaid` (`F-002`), `fitness-agy-sync` (`F-003`), `fitness-skill-package` (`F-004`, running `python3 scripts/validate_skill.py`), `fitness-prose-hygiene` (`F-005`, verified via `python3 scripts/validate_skill.py`), and `fitness-samples` (`F-006`, running `python3 -m unittest tests.test_task_005_evals_and_samples`) as prerequisites of `fitness` in `Makefile`.
   - Mark all `F-001`..`F-006` rows `Active` in `docs/spec/fitness-functions.md`.
2. **Full open-source `README.md`:**
   - Badges: MIT license badge (`[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)`) and GitHub last-commit badge (`[![Last commit](https://img.shields.io/github/last-commit/tkdtaylor/writing)](https://github.com/tkdtaylor/writing/commits)`).
   - Crisp one-sentence value proposition + `> **Status.**` callout linking `docs/plans/roadmap.md`.
   - **What it does:** Explain the core philosophy (substance before surface, reader-load reduction, mode + genre separation so runbook rules do not flatten essays and essay advice does not weaken docs, non-composite prose linting).
   - **Architecture Mermaid diagram:** Quoted node labels passing `scripts/check-mermaid.py`.
   - **Workflow modes and slash commands:** Table of `draft` (`/write-draft`), `edit` (`/write-edit`), `review` (`/write-review`), and `lint` (`/write-lint`) plus natural-language trigger examples.
   - **Genres and registers covered:** Technical docs (Diataxis, STE, Global English, READMEs, RFCs/ADRs, PR briefs), Business & executive (BLUF memos, self-contained decision briefs, metric vetting, emails), and Longform & persuasion (essays, landing copy, UX microcopy, speeches/slides, progressive diagrams, creative narrative).
   - **Installing across harnesses:** Copy-pasteable commands for **Claude Code** (`git clone https://github.com/tkdtaylor/writing.git ~/.claude/skills/writing` + optional `commands/write-*.md`), **Google Antigravity** (`~/.gemini/config/skills/writing/` or `.agents/skills/writing/`), **OpenAI Codex** (`~/.codex/skills/writing/` or `.agents/skills/writing/`), and **Cursor / GitHub Copilot / Windsurf** (`.cursor/rules/`, `.github/skills/writing/`, `.windsurfrules`).
   - **Diagnostic CLI usage:** Examples of `scripts/prose_lint.py`, `scripts/strip_markdown.py`, and `scripts/validate_skill.py`.
   - **Calibration samples and adding your own:** Overview of `samples/` and `training/inbox/`.
   - **Repository structure tree:** Accurate tree matching every live directory and file.
   - **Prior art and inspiration:** Explicit, respectful credit to Addy Osmani's [`clarity`](https://github.com/addyosmani/clarity) and Lauren Tan's [`pstack`](https://github.com/cursor/plugins/tree/main/pstack), noting that all files in `writing` are clean-room authored under MIT.
   - **Documentation, Security, Sponsorship, and License:** Links to `docs/architecture/overview.md`, `docs/architecture/diagrams.md`, `docs/spec/SPEC.md`, `docs/plans/roadmap.md`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `SECURITY.md`, `https://github.com/sponsors/tkdtaylor`, and `LICENSE` (explaining why MIT was chosen, matching `create-project`).
3. **`CHANGELOG.md` and `tests/test_task_007_integration.py`:**
   - Record all Version 1 additions under `## [Unreleased]`.
   - Write `tests/test_task_007_integration.py` covering `TC-007-01` through `TC-007-03`.

## Verification plan

- Run `make check` (including `make lint`, `make test`, and `make fitness` with all 6 fitness checks active) and verify exit code `0`.
