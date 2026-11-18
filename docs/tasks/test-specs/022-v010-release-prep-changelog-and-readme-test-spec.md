# Test Spec 022: `v0.1.0` Release Hygiene across `CHANGELOG.md`, `README.md`, `AGENTS.md`, and `roadmap.md`

- **Task:** `docs/tasks/backlog/022-v010-release-prep-changelog-and-readme.md`
- **Verification target:** L5 (`make check` + `validate_skill.py` + `prose_lint.py --profile technical README.md` / zero-tell verification)

## Requirements and Test Cases

### `REQ-022-01`: `CHANGELOG.md` cuts `[0.1.0] - 2026-11-18` while preserving `[Unreleased]`

- **`TC-022-01`**: `CHANGELOG.md` retains `## [Unreleased]` at the top (Keep a Changelog 1.1.0) followed by `## [0.1.0] - 2026-11-18` documenting the `v0.1.0` release (including `mixed_dialects` and technical-profile refinements) and bottom version links, with zero `prose_lint.py` tells or overloaded (`> 35`-word) sentences.

### `REQ-022-02`: `README.md`, `AGENTS.md`, and `docs/plans/roadmap.md` reflect shipped `v0.1.0` and stable tag tarballs

- **`TC-022-02`**: `README.md` status banner reflects `v0.1.0` shipped (no longer framing `v0.1.0` as an unshipped future plan), install instructions surface the pinned `v0.1.0` tag tarball (`archive/refs/tags/v0.1.0.tar.gz`) alongside `archive/refs/heads/main.tar.gz`, `README.md` and `AGENTS.md` note `mixed_dialects`, and `docs/plans/roadmap.md` marks Milestone 1 (`v0.1.0`, `Tasks 001..022`) `Completed` and Milestone 2 `Active`.

### `REQ-022-03`: Zero prose-lint tells and clean package validation

- **`TC-022-03`**: `README.md`, `AGENTS.md`, `CHANGELOG.md`, and `docs/plans/roadmap.md` contain zero `U+2014` or `U+2013` characters, zero `prose_lint.py` tell list hits, and zero `overloaded_sentences`, and `make check` + `package_skill.py --check` exit `0`.
