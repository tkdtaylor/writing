# Task 020: v1.3 Evals, Documentation, and Full Integration Sync

- **Priority:** P1
- **Model tier:** `fast` (`flash` / Gemini 3.8 Flash)
- **Dependencies:** Tasks 017, 018, 019 (Wave 2)
- **Test spec:** `docs/tasks/test-specs/020-v13-evals-readme-and-changelog-sync-test-spec.md`

## Objective

Expand `evals/evals.json` and `evals/trigger-evals.json` to cover all v1.3 workflows and genres, update `README.md`, `AGENTS.md`, `CHANGELOG.md`, and `docs/plans/roadmap.md`, sync `ALL_TELL_LIST_KEYS` in existing test suites, and verify end-to-end `make check` and `make package`.

## Deliverables (exclusive file scope)

- `evals/evals.json`
- `evals/trigger-evals.json`
- `README.md`
- `AGENTS.md`
- `CHANGELOG.md`
- `docs/plans/roadmap.md`
- `tests/test_task_010_memo_samples_and_sync.py`
- `tests/test_task_014_clean_packaging.py`
- `tests/test_task_015_cli_safety_and_models.py`
- `tests/test_task_016_doc_and_diagram_sync.py`
- `tests/test_task_020_v13_evals_and_docs.py`

## Implementation details

1. **Expand `evals/evals.json` (`>= 22` cases) and `evals/trigger-evals.json` (`>= 34` balanced queries) (`REQ-020-01`):**
   - Add 3 behavioral eval cases (`ids` `20`, `21`, `22`) to `evals/evals.json`:
     - Case `20` (`mode=draft`, `medium_fit`): Draft a blameless SRE incident postmortem and Keep-a-Changelog `v2.4.0` release note from incident/deploy notes (separating systemic *Root cause* from *Trigger*, `HH:MM UTC` timeline, owned action items with `[TK: ticket ID]`, and breaking-change migration steps above raw commit subjects).
     - Case `21` (`mode=edit`, `voice_sample_boundary` or `false_positive_restraint`): 3-way edit triage on a rough founder landing-page draft with real voice (`ship`, `stuff`) plus an unsupported `"cuts churn 45%"` claim and stacked negation list (`No setup call, no templates, no spreadsheets`), asserting working voice lines stay locked, stacked negations become concrete workflow steps, and the unsupported claim names its exact `[TK: cohort export]` unlock.
     - Case `22` (`mode=review`, `mode_boundary`): High-stakes RFC review requesting a zero-context cold-reader check plus flagging a drafted PR comment reply that re-explains background the reviewer already wrote (`reply context-rebuilding`), keeping `mode=review` strictly read-only.
   - Add 4 balanced trigger queries (`2` `should_trigger: true` for blameless postmortems and release notes; `2` `should_trigger: false` for automated `git tag` / CI release-workflow YAML scripting and incident log `jq` parsing) to `evals/trigger-evals.json`.
2. **Synchronize `README.md`, `AGENTS.md`, `CHANGELOG.md`, and `docs/plans/roadmap.md` (`REQ-020-02`):**
   - Keep every sentence `<= 35` words (`overloaded_sentences == []`), zero `U+2014` or spaced `--`, single-line continuous paragraphs, and blank lines before lists.
   - Update `README.md` genre table (`postmortems`, `changelogs and release notes`, `3P updates`, `thread reply discipline`), mode overview (`3-way edit triage`, `zero-context cold-reader pass`), anti-slop / `prose_lint.py` summary (`chatbot_artifacts`, `meta_and_strawman_tells`, spaced `--` / en-dash detection), and prior-art acknowledgments (`blader/humanizer` / Wikipedia *Signs of AI Writing*, `anthropics/skills`, `coreyhaines31/marketingskills`, `vidanov/writing-craft-skill`).
   - Update `CHANGELOG.md` `[Unreleased]` and `docs/plans/roadmap.md` (`Tasks 017..020`), and update `AGENTS.md` reference one-liners where relevant.
3. **Sync `ALL_TELL_LIST_KEYS` and verify clean packaging (`REQ-020-03`):**
   - Add `"chatbot_artifacts"` and `"meta_and_strawman_tells"` to `ALL_TELL_LIST_KEYS` in `tests/test_task_010_memo_samples_and_sync.py`, `tests/test_task_014_clean_packaging.py`, `tests/test_task_015_cli_safety_and_models.py`, and `tests/test_task_016_doc_and_diagram_sync.py`.
   - Write `tests/test_task_020_v13_evals_and_docs.py` verifying `TC-020-01`..`TC-020-03`.

## Verification plan

- Move this task file to `docs/tasks/completed/020-v13-evals-readme-and-changelog-sync.md` via `git mv`.
- Run `make check` and `python3 scripts/package_skill.py --check` and confirm exit `0`.
