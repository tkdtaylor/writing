# Task 014: Clean Skill Packaging and End-User Install Hygiene

- **Priority:** P1
- **Model tier:** `deep` (`pro`)
- **Dependencies:** Tasks `011`, `012`, `013` (Wave 2)
- **Test spec:** `docs/tasks/test-specs/014-clean-skill-packaging-and-install-hygiene-test-spec.md`

## Objective

Keep maintainer scaffolding (`.agents/`, `.claude/`, `docs/`, `tests/`, `evals/`, `samples/`) cleanly separated from end-user skill installations via `.gitattributes` `export-ignore`, a zero-dependency `scripts/package_skill.py` packager/installer, a new `F-007` fitness gate, and updated `README.md` installation instructions.

## Deliverables (exclusive file scope)

- `.gitattributes`
- `.gitignore`
- `scripts/package_skill.py` (executable, mode `0755`)
- `Makefile`
- `docs/spec/architecture.md`
- `docs/spec/fitness-functions.md`
- `docs/spec/interfaces.md`
- `README.md`
- `AGENTS.md`
- `CHANGELOG.md`
- `docs/plans/roadmap.md`
- `tests/test_task_007_integration.py`
- `tests/test_task_014_clean_packaging.py`

Do not edit `docs/tasks/test-specs/coverage-tracker.md` on the task branch.

## Implementation details

1. **`.gitattributes` (`export-ignore`):**
   - Mark `.agents`, `.claude`, `docs`, `tests`, `evals`, `samples`, `artifacts`, `Makefile`, `README.md`, `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `SECURITY.md`, `CHANGELOG.md`, `.gitignore`, `.gitattributes`, `scripts/check-task-state.sh`, `scripts/start-task.sh`, `scripts/finish-task.sh`, `scripts/verify-worktree-isolation.sh`, `scripts/check-mermaid.py`, `scripts/sync-agy-skills.py`, and `scripts/package_skill.py` as `export-ignore`.
   - Result: `git archive` and GitHub's `archive/refs/heads/main.tar.gz` (and release tarballs) contain **only** the self-contained skill payload: `SKILL.md`, `LICENSE`, `commands/write-*.md`, `references/*.md`, and `scripts/{strip_markdown,prose_lint,validate_skill}.py` (zero `.agents/skills/*` maintainer adapters and zero broken repo-only links).
2. **`scripts/package_skill.py` (mode `0755`, Python 3 stdlib only, `OSError`-safe exit `2`):**
   - Canonical runtime payload manifest: `SKILL.md`, `LICENSE`, `commands/write-*.md`, `references/*.md`, `scripts/strip_markdown.py`, `scripts/prose_lint.py`, `scripts/validate_skill.py`.
   - CLI options:
     - `--root DIR` (default repo root)
     - `--output-dir DIR` (writes `writing-skill.tar.gz` and `writing.skill` zip archive into `DIR`, e.g. `dist/`)
     - `--install-to DIR` (cleanly installs only the runtime payload into `DIR`, e.g. `~/.gemini/config/skills/writing` or `.agents/skills/writing`, removing any stale non-payload files only if `--clean` is passed or writing cleanly into target dir without touching `.agents/`/`.claude/` from source)
     - `--check` (stages the runtime payload into a `TemporaryDirectory`, asserts exactly `1` `SKILL.md` file exists in the staged tree, asserts `.agents`, `.claude`, `docs`, and `tests` are absent, and runs `validate_skill.validate_repo(staged_dir)` asserting `passed == True`!)
     - `--json` (optional structured summary)
   - Add `dist/` to `.gitignore`.
3. **`Makefile` and `docs/spec/`:**
   - Add `package` (`python3 scripts/package_skill.py --output-dir dist`) and `fitness-clean-package` (`F-007`: runs `python3 scripts/package_skill.py --check`) to `Makefile`, wiring `fitness-clean-package` into `fitness:`.
   - Update `docs/spec/fitness-functions.md` (`F-007` `Active`), `docs/spec/architecture.md`, and `docs/spec/interfaces.md`.
4. **Update `README.md`, `AGENTS.md`, `CHANGELOG.md`, `docs/plans/roadmap.md`, and `tests/test_task_007_integration.py`:**
   - In `README.md` (`## Installing across harnesses`), provide clean copy-pasteable install commands that **never** place `.agents/skills/*` maintainer skills into recursive skill directories:
     - Direct GitHub archive one-liner (`curl -fsSL https://github.com/tkdtaylor/writing/archive/refs/heads/main.tar.gz | tar -xz --strip-components=1 -C <skill-dir>`) which leverages `.gitattributes` `export-ignore`!
     - Local checkout installer (`python3 scripts/package_skill.py --install-to <skill-dir>`).
     - Note clearly why full `git clone` into recursive skill folders (like `~/.gemini/config/skills/` or `.agents/skills/`) is avoided (because this repo uses `.agents/skills/` for its own maintainer workflow roles), while contributors working on the repo itself clone normally.
   - Document `--profile` / `--mode` (`technical`, `one-pager`, `six-pager`, `memo`, `narrative`) in `README.md` CLI examples and `AGENTS.md`, and update `CHANGELOG.md` and `tests/test_task_007_integration.py` (including the 3 new `mechanics_and_tells` keys).
   - Ensure zero `\u2014`, zero emoji bullets, continuous single-line paragraphs, blank lines before lists, and `Findings: none` in `prose_lint.py` across `README.md`, `AGENTS.md`, and `CHANGELOG.md`!

## Verification plan

- Write `tests/test_task_014_clean_packaging.py` covering `TC-014-01`..`TC-014-03`.
- Run `make check` and `make package`, confirming exit `0` and clean `git status`.
