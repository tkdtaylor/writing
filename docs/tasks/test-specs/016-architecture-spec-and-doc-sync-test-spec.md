# Test Spec 016: Architecture, Spec, and Documentation Drift Closure

- **Task:** `docs/tasks/backlog/016-architecture-spec-and-doc-sync.md`
- **Verification target:** L5 (`make check` + `check-mermaid.py` + `prose_lint.py` zero-tell verification)

## Requirements and Test Cases

### `REQ-016-01`: Architecture overview, C4 diagrams, and ADR discoverability

- **`TC-016-01`**: `docs/architecture/overview.md` replaces raw `git clone` install guidance with clean archive / `package_skill.py --install-to` installation, references `one-pager-and-six-pager.md`, `package_skill.py`, and the `10,000`-word combined runtime cap, and links both `001-register-and-genre-routing.md` and `002-narrative-memos-and-anti-flourish-rules.md`; `docs/architecture/diagrams.md` includes `references/one-pager-and-six-pager.md` under `GenreRouter` and `validate_skill.py` + `package_skill.py` in Level 1 `CLI`, and `python3 scripts/check-mermaid.py` exits `0`.

### `REQ-016-02`: Spec index, `README.md`, `CHANGELOG.md`, and `references/draft-and-brief.md` alignment

- **`TC-016-02`**: `docs/spec/SPEC.md` and `CHANGELOG.md` cite all seven active fitness gates (`F-001`..`F-007`); `README.md` matches `references/business-and-executive.md` epistemic tags (`measured`, `inferred`, `open`) and 4-part metric vetting (`unit`, `sample or runs`, `baseline`, `limiter`) and lists `configuration.md` in the `docs/spec/` tree comment; and `references/draft-and-brief.md` includes `references/one-pager-and-six-pager.md` in its genre reference list and notes workspace prose-formatter precedence while staying within the `<= 1,500` per-file and `<= 10,000` combined word caps.

### `REQ-016-03`: Repository-wide prose hygiene across `CONTRIBUTING.md` and completed task files

- **`TC-016-03`**: `CONTRIBUTING.md` triggers zero `overloaded_sentences` and zero `mechanics_and_tells` hits in `prose_lint.py`, `docs/tasks/completed/013-prose-lint-gaps-and-genre-profiles.md` contains zero `U+2014` characters, and `make check` passes cleanly.
