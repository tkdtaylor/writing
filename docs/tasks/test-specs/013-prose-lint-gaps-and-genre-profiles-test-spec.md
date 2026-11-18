# Test Spec 013: `prose_lint.py` Detector Gaps and `--profile` Genre Validation

- **Task:** `docs/tasks/backlog/013-prose-lint-gaps-and-genre-profiles.md`
- **Test file:** `tests/test_task_013_lint_gaps_and_profiles.py`

## Requirements

- **REQ-013-01:** `scripts/prose_lint.py` adds three line-numbered detectors under `mechanics_and_tells`: `shorthand_ambiguities` (`and/or` and `<word>(s)` plural shorthand), `exclamation_marks` (prose `!` outside fenced/inline code, double-quoted literals, `!=`/`!==`, `![alt]`, `[!NOTE|TIP|IMPORTANT|WARNING|CAUTION]`, and HTML comments), and `false_agency` (inanimate metrics/data/architecture performing human rhetorical acts like `metrics speak`, `the data tells us`, `the architecture demands`, without flagging normal software actors like `the worker retries`), plus wraps CLI `path.is_file()` in `try ... except OSError:` returning exit `2`.
- **REQ-013-02:** `scripts/prose_lint.py` accepts optional `--profile {default,technical,memo,one-pager,six-pager,narrative}` (with `--mode` alias) on the CLI and `profile: str | None = None` in `analyze_text()`, emitting a `profile_checks` object when a non-default profile is active:
  - `technical`: flags numbered procedural steps exceeding `20` words (`overlong_steps`) and non-ISO dates / 12-hour `AM`/`PM` times (`date_time_issues`).
  - `one-pager` / `six-pager` / `memo`: checks One-Pager word window (`350..550` words) or Six-Pager pre-Appendix body ceiling (`<= 2500` words, stripping `## Appendix` / `## Appendices` onward from body count) and `>= 80%` paragraph prose share (`prose_paragraph_share`, flagging bullet-heavy slide-speak), plus `date_time_issues`.
  - `narrative`: checks `>= 85%` paragraph prose share and flags low sentence-length variation (`body_sentence_cv < 0.30`).
- **REQ-013-03:** `docs/spec/behaviors.md`, `docs/spec/data-model.md`, `docs/spec/interfaces.md`, and `tests/test_task_004_prose_lint.py` are updated in sync, with zero composite score fields and zero false positives across all clean authored repo Markdown files.

## Test Cases

| ID | Requirement | Input / Target | Expected Assertion |
|----|-------------|----------------|--------------------|
| `TC-013-01` | `REQ-013-01` | Fixtures with `and/or`, `file(s)`, prose `!`, `![img]`, `[!NOTE]`, `!=`, `"Great!"`, `metrics speak`, and `the worker retries` + mocked `PermissionError` | Fires `shorthand_ambiguities`, `exclamation_marks`, and `false_agency` only on real violations; `PermissionError` on CLI path returns exit `2` |
| `TC-013-02` | `REQ-013-02` | CLI & API runs with `--profile technical`, `--mode one-pager`, `--profile six-pager`, `--profile memo`, and `--profile narrative` | Enforces `<= 20`-word steps, ISO 8601 / 24h UTC hygiene, `350..550w` One-Pager & `<= 2500w` pre-Appendix Six-Pager budgets, `>= 80%` prose share, and narrative cadence check; `samples/one-pager.after.md` passes `--profile one-pager` |
| `TC-013-03` | `REQ-013-03` | `docs/spec/{behaviors,data-model,interfaces}.md` + clean repo Markdown scan | Spec files document new tell keys and `--profile`/`--mode`; all clean repo Markdown files have `[]` across the 3 new tell keys |
