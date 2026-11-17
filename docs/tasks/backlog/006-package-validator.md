# Task 006: Skill Package and Prose Hygiene Validator (`validate_skill.py`)

- **Priority:** P1
- **Model tier:** `balanced`
- **Dependencies:** Tasks `001`, `002`, `003`, `004` (Wave 2)
- **Test spec:** `docs/tasks/test-specs/006-package-validator-test-spec.md`

## Objective

Implement `scripts/validate_skill.py` using only the Python 3.10+ standard library to enforce context-window word budgets, routing and relative-link integrity, slash-command `mode=` symmetry, eval JSON schemas, and repository prose hygiene (`B-008` in `docs/spec/behaviors.md`).

## Deliverables (exclusive file scope)

- `scripts/validate_skill.py` (executable, mode `0755`)
- `tests/test_task_006_validate_skill.py`

Do not edit `docs/tasks/test-specs/coverage-tracker.md` or files belonging to other tasks. Use `\u2014` escape sequences rather than literal em dashes in Python code.

## Implementation details

1. **CLI and module contract (`docs/spec/interfaces.md`):**
   - `python3 scripts/validate_skill.py [--root DIR] [--json]`
   - Expose `validate_repo(root: Path) -> dict` returning `{"passed": bool, "checks": [...], "errors": [...], "word_counts": {...}}`.
   - Exit `0` if `passed` is True, `1` if any check fails, `2` on invalid CLI args or missing root directory.
2. **Checks enforced:**
   - **Frontmatter and word budgets (`REQ-006-01`):** `SKILL.md` exists, starts with YAML frontmatter defining `name` and non-empty `description`, and has `<= 1,500` words. Every `references/*.md` file has `<= 1,500` words. Combined words across `SKILL.md` + `references/*.md` is `<= 8,500` words.
   - **Routing and link integrity (`REQ-006-02`):**
     - Every file in `references/*.md` is referenced in `SKILL.md`.
     - Skill runtime scripts (`scripts/strip_markdown.py`, `scripts/prose_lint.py`) are referenced in `SKILL.md`.
     - Every `commands/write-*.md` file defines `description:` frontmatter and a `mode=<token>` token that also appears in `SKILL.md`.
     - Every relative Markdown link `[label](target)` (ignoring `http://`, `https://`, `mailto:`, `file://`, `conversation://`, and `#anchor`-only links, stripping `#fragment` suffixes) in `SKILL.md`, `references/*.md`, `commands/*.md`, `README.md`, `AGENTS.md`, `CLAUDE.md`, `CONTRIBUTING.md`, `SECURITY.md`, and `docs/**/*.md` resolves to an existing file or directory inside `--root`.
   - **Eval schema check (`REQ-006-03`):**
     - If `evals/evals.json` exists, verify valid JSON, `skill_name` matches `SKILL.md` `name`, non-empty `evals` list, unique `id`s, required keys (`id`, `eval_name`, `category`, `mode`, `prompt`, `expected_output`, `assertions`), and all 4 modes + 6 safeguard categories are represented.
     - If `evals/trigger-evals.json` exists, verify valid JSON list with both `should_trigger: true` and `should_trigger: false` entries.
   - **Repository prose hygiene (`REQ-006-04`):**
     - Scan authored Markdown files (`SKILL.md`, `commands/*.md`, `references/*.md`, `README.md`, `AGENTS.md`, `CLAUDE.md`, `CONTRIBUTING.md`, `SECURITY.md`, `CHANGELOG.md`, `docs/spec/*.md`, `docs/architecture/**/*.md`, `docs/plans/**/*.md`, `samples/README.md`, `samples/*.after.md`, `evals/JUDGE.md`) when present. Explicitly exempt managed/third-party/negative-fixture paths (`.claude/`, `.agents/`, `CODE_OF_CONDUCT.md`, `samples/*.before.md`, `docs/tasks/`).
     - Outside fenced code blocks, verify zero `\u2014` characters, zero emoji bullet lines, and zero hard-wrapped multi-line paragraphs (via `strip_markdown.py`).

## Verification plan

- Write `tests/test_task_006_validate_skill.py` covering `TC-006-01` through `TC-006-04` (including running `validate_repo` against the live repository root!).
- Run `make check` and confirm all checks pass cleanly.
