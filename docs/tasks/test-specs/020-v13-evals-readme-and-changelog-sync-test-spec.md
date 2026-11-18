# Test Spec 020: v1.3 Evals, Documentation, and Full Integration Sync

- **Task:** `docs/tasks/backlog/020-v13-evals-readme-and-changelog-sync.md`
- **Verification target:** L5 (`make check` + `make package` + `validate_skill.py` + `prose_lint.py`)

## Requirements and Test Cases

### `REQ-020-01`: Expanded `evals/evals.json` and `evals/trigger-evals.json` coverage

- **`TC-020-01`**: `evals/evals.json` (`>= 22` cases) adds behavioral evals covering (a) blameless incident postmortem and Keep-a-Changelog release note authoring (`mode=draft`), (b) 3-way edit triage preserving real author voice and naming the evidence `[TK: ...]` unlock for declined claims (`mode=edit`), and (c) zero-context cold-reader review plus thread reply without context-rebuilding (`mode=review` / `mode=edit`); `evals/trigger-evals.json` (`>= 34` balanced queries, 50/50 `true`/`false`) adds postmortem/release-note positive queries and near-miss git/release-automation negative queries; and `validate_skill.py` passes cleanly.

### `REQ-020-02`: `README.md`, `AGENTS.md`, `CHANGELOG.md`, and `roadmap.md` synchronization

- **`TC-020-02`**: `README.md`, `AGENTS.md`, `CHANGELOG.md`, and `docs/plans/roadmap.md` document the v1.3 additions (3-way edit triage and `Leave-it-alone` rule, declined-claim unlocks, zero-context cold-reader pass, blameless postmortems and Keep-a-Changelog release notes, 3P updates and thread reply discipline, and `prose_lint.py` dash-bypass, `chatbot_artifacts`, and `meta_and_strawman_tells` detectors) with zero `prose_lint.py` tell or overloaded-sentence hits.

### `REQ-020-03`: Test-suite `ALL_TELL_LIST_KEYS` synchronization and clean package gate

- **`TC-020-03`**: `ALL_TELL_LIST_KEYS` in `tests/` includes `chatbot_artifacts` and `meta_and_strawman_tells`, `make check` (`lint` + `test` + `F-001`..`F-007`) and `package_skill.py --check` exit `0`, and combined runtime words remain `<= 10,000`.
