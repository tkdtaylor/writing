# Test Spec 014: Clean Skill Packaging and End-User Install Hygiene

- **Task:** `docs/tasks/backlog/014-clean-skill-packaging-and-install-hygiene.md`
- **Test file:** `tests/test_task_014_clean_packaging.py`

## Requirements

- **REQ-014-01:** `.gitattributes` marks maintainer and repository-level paths (`.agents`, `.claude`, `docs`, `tests`, `evals`, `samples`, `artifacts`, `Makefile`, `README.md`, `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `SECURITY.md`, `CHANGELOG.md`, `.gitignore`, `.gitattributes`, and maintainer scripts `scripts/*.sh`, `scripts/check-mermaid.py`, `scripts/sync-agy-skills.py`, `scripts/package_skill.py`) with `export-ignore`, so `git archive` outputs only the self-contained skill payload (`SKILL.md`, `LICENSE`, `commands/write-*.md`, `references/*.md`, and `scripts/{strip_markdown,prose_lint,validate_skill}.py`) with zero nested `SKILL.md` files and zero broken links.
- **REQ-014-02:** `scripts/package_skill.py` (mode `0755`, Python 3 stdlib only) supports `--output-dir DIR` (producing deterministic `writing-skill.tar.gz` and `writing.skill` zip archives), `--install-to DIR` (copying only the clean skill payload into a target directory without `.agents/`, `.claude/`, `docs/`, or `tests/`), `--check` (verifying staged payload purity + `validate_skill.py` pass), and `OSError`-safe CLI error handling (`exit 2`).
- **REQ-014-03:** `Makefile` adds `package` and `fitness-clean-package` (`F-007`), `docs/spec/{architecture,fitness-functions,interfaces}.md` and `.gitignore` (`dist/`) are updated, and `README.md`, `AGENTS.md`, `CHANGELOG.md`, and `docs/plans/roadmap.md` document clean end-user installation so recursive skill scanners never ingest maintainer `.agents/skills/*` roles.

## Test Cases

| ID | Requirement | Input / Target | Expected Assertion |
|----|-------------|----------------|--------------------|
| `TC-014-01` | `REQ-014-01` | `.gitattributes` + `git archive --format=tar HEAD` | Archive contains `SKILL.md`, `commands/write-*.md`, `references/*.md`, and the 3 runtime scripts, and excludes `.agents/`, `.claude/`, `docs/`, `tests/`, `evals/`, and `samples/`, with exactly 1 `SKILL.md` |
| `TC-014-02` | `REQ-014-02` | `scripts/package_skill.py` (`--output-dir`, `--install-to`, `--check`) | Produces valid `.tar.gz` and `.skill` archives, installs clean payload to temp dir passing `validate_skill.py --root`, excludes `.agents/` and `.claude/`, and exits `0` on `--check` |
| `TC-014-03` | `REQ-014-03` | `Makefile`, `fitness-functions.md`, `README.md`, `CHANGELOG.md`, and `make fitness` | `F-007` is `Active` and wired in `Makefile`; `README.md` documents clean archive/`--install-to` installation and warns against recursive `.agents/skills/` pollution; `make fitness` exits `0` |
