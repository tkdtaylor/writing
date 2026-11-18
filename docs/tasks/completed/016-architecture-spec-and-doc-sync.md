# Task 016: Architecture, Spec, and Documentation Drift Closure

- **Priority:** P1
- **Model tier:** `fast` (`flash` / Gemini 3.8 Flash)
- **Dependencies:** None (Wave 1)
- **Test spec:** `docs/tasks/test-specs/016-architecture-spec-and-doc-sync-test-spec.md`

## Objective

Close all remaining documentation, diagram, cross-reference, and prose-hygiene drift surfaced by the post-v1.2 repository audit across `docs/architecture/`, `docs/spec/SPEC.md`, `README.md`, `CHANGELOG.md`, `references/draft-and-brief.md`, `CONTRIBUTING.md`, and `docs/tasks/completed/013-prose-lint-gaps-and-genre-profiles.md`.

## Deliverables (exclusive file scope)

- `docs/architecture/overview.md`
- `docs/architecture/diagrams.md`
- `docs/spec/SPEC.md`
- `README.md`
- `CHANGELOG.md`
- `references/draft-and-brief.md`
- `CONTRIBUTING.md`
- `docs/tasks/completed/013-prose-lint-gaps-and-genre-profiles.md`
- `tests/test_task_016_doc_and_diagram_sync.py`

Do not modify files owned by Task 015 (`scripts/package_skill.py`, `scripts/validate_skill.py`, `docs/spec/interfaces.md`, `.claude/*`, `.agents/*`, `CLAUDE.md`) or `docs/tasks/test-specs/coverage-tracker.md`.

## Implementation details

1. **Update `docs/architecture/overview.md` and `docs/architecture/diagrams.md` (`REQ-016-01`):**
   - In `docs/architecture/overview.md`:
     - Include `one-pager-and-six-pager.md` in Principle 2 and the Genre references bullet.
     - Mention the `10,000`-word combined runtime budget in Principle 3.
     - Replace `via git clone or cp` in Principle 5 with filtered release/archive tarballs or `scripts/package_skill.py --install-to` so maintainer `.agents/` folders never leak into end-user skill scan paths.
     - Include `package_skill.py` in the CLI bullet (and mention `F-001`..`F-007`).
     - Add an `## Architecture decisions` section at the bottom with relative Markdown links to `[ADR 001: Register and Genre Routing](decisions/001-register-and-genre-routing.md)` and `[ADR 002: Narrative Memos and Anti-Flourish Rules](decisions/002-narrative-memos-and-anti-flourish-rules.md)`.
   - In `docs/architecture/diagrams.md`:
     - Update `Last updated: 2026-11-18`.
     - Update C4 Level 1 `CLI` label to `CLI["Diagnostic & Packaging CLIs (strip_markdown, prose_lint, validate_skill, package_skill)"]` (quote node labels containing parentheses so `check-mermaid.py` passes cleanly).
     - Add `GenreRouter --> Memo["references/one-pager-and-six-pager.md"]` in C4 Level 2.
     - Verify `python3 scripts/check-mermaid.py` exits `0`.
2. **Sync `docs/spec/SPEC.md`, `README.md`, `CHANGELOG.md`, and `references/draft-and-brief.md` (`REQ-016-02`):**
   - `docs/spec/SPEC.md:18`: Change `F-001`..`F-006` to `F-001`..`F-007`.
   - `CHANGELOG.md:19`: Update "Six active fitness gates (`F-001` through `F-006`)" to "Seven active fitness gates (`F-001` through `F-007`)".
   - `README.md`:
     - Line 77: Update epistemic tags to `measured`, `inferred`, `open` and metric vetting to `unit, sample or runs, baseline, limiter` matching `references/business-and-executive.md`.
     - Lines 95 and 104: Clarify `archive/refs/heads/main.tar.gz` as the filtered `main` archive tarball (keeping the exact `archive/refs/heads/main.tar.gz` URL intact for existing tests).
     - Line 250: Include `configuration` in `#   SPEC.md, behaviors, architecture, data-model, interfaces, configuration, fitness`.
   - `references/draft-and-brief.md`:
     - Line 3: Include `references/one-pager-and-six-pager.md` in the parenthetical list of genre references.
     - Line 47: Note that configured target-repository formatters (`mdformat`, `prettier --prose-wrap always`) take precedence on line wrapping when present.
3. **Clean remaining prose/em-dash nits (`REQ-016-03`):**
   - Split the 39-word sentence on `CONTRIBUTING.md:7` into two crisp sentences on the same single-line list item so `prose_lint.py` reports `overloaded_sentences == []`.
   - Replace both `U+2014` characters in `docs/tasks/completed/013-prose-lint-gaps-and-genre-profiles.md` (lines 37 and 43) with ASCII colons or parentheses.

## Verification plan

- Write `tests/test_task_016_doc_and_diagram_sync.py` verifying `TC-016-01`, `TC-016-02`, and `TC-016-03` (including `prose_lint.py`, `validate_skill.py`, and `check-mermaid.py`).
- Move this task file to `docs/tasks/completed/016-architecture-spec-and-doc-sync.md` via `git mv`.
- Run `make check` and confirm zero errors.
