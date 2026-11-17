# Changelog

All notable changes to `writing` are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Added

- Core skill router in [SKILL.md](SKILL.md) under the 1,500-word context budget. Defines deterministic `mode=` routing (`draft`, `edit`, `review`, `lint`), six universal safeguards, seven-register genre classification, and baseline prose mechanics.
- Optional Claude Code slash commands in `commands/` ([commands/write-draft.md](commands/write-draft.md), [commands/write-edit.md](commands/write-edit.md), [commands/write-review.md](commands/write-review.md), and [commands/write-lint.md](commands/write-lint.md)).
- Workflow mode guides in `references/` ([references/draft-and-brief.md](references/draft-and-brief.md), [references/edit-and-anti-slop.md](references/edit-and-anti-slop.md), and [references/review-rubric.md](references/review-rubric.md)). Covers goal restatement, perspective interviews, `[TK]` markers, provenance notes, single-pass editing, and read-only `keep` / `revise` / `ask-author` / `cut` critiques.
- Genre and register guides in `references/` ([references/technical-and-docs.md](references/technical-and-docs.md), [references/business-and-executive.md](references/business-and-executive.md), and [references/longform-and-persuasion.md](references/longform-and-persuasion.md)). Covers Diataxis modes, ASD-STE100, Global English, READMEs, RFCs/ADRs, PR briefings, BLUF memos, decision briefs, metric vetting, essays, UX microcopy, speeches, and narrative prose.
- Zero-dependency Python 3 CLIs in `scripts/` (`scripts/strip_markdown.py`, `scripts/prose_lint.py`, and `scripts/validate_skill.py`). Reports cadence variation, `MATTR-50` diversity, concrete-anchor ratios, line-numbered mechanical tells, word budgets, link integrity, and prose hygiene without a composite AI detector score.
- Evaluation benchmark suite in `evals/` ([evals/JUDGE.md](evals/JUDGE.md), `evals/evals.json`, and `evals/trigger-evals.json`) plus calibration pairs in `samples/` ([samples/README.md](samples/README.md), `samples/technical-doc.{before,after}.md`, and `samples/executive-memo.{before,after}.md`).
- Six active fitness gates (`F-001` through `F-006`) in `Makefile` and [docs/spec/fitness-functions.md](docs/spec/fitness-functions.md). Ships the full open-source [README.md](README.md), MIT license, governance policies, cross-harness agent briefings (`AGENTS.md`, `CLAUDE.md`, `GEMINI.md`), and Antigravity `.agents/` adapters.
