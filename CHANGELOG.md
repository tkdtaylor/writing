# Changelog

All notable changes to `writing` are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Added

- Core skill router in [SKILL.md](SKILL.md) under the 1,500-word context budget. Defines deterministic `mode=` routing (`draft`, `edit`, `review`, `lint`), six universal safeguards, seven-register genre classification, and baseline prose mechanics.
- Optional Claude Code slash commands in `commands/` ([commands/write-draft.md](commands/write-draft.md), [commands/write-edit.md](commands/write-edit.md), [commands/write-review.md](commands/write-review.md), and [commands/write-lint.md](commands/write-lint.md)).
- Workflow mode guides in `references/` ([references/draft-and-brief.md](references/draft-and-brief.md), [references/edit-and-anti-slop.md](references/edit-and-anti-slop.md), and [references/review-rubric.md](references/review-rubric.md)). Covers goal restatement, perspective interviews, `[TK]` markers, provenance notes, single-pass editing, and read-only `keep` / `revise` / `ask-author` / `cut` critiques.
- Genre and register guides in `references/` ([references/technical-and-docs.md](references/technical-and-docs.md), [references/business-and-executive.md](references/business-and-executive.md), [references/one-pager-and-six-pager.md](references/one-pager-and-six-pager.md), and [references/longform-and-persuasion.md](references/longform-and-persuasion.md)). Covers Diataxis modes, ASD-STE100, Global English, READMEs, RFCs/ADRs, PR briefings, BLUF memos, decision briefs, metric vetting, essays, UX microcopy, speeches, and narrative prose.
- Narrative decision-memo blueprints in [references/one-pager-and-six-pager.md](references/one-pager-and-six-pager.md). Defines Type 1 vs Type 2 door selection, 5-section One-Pagers, 7-part Six-Pagers with sacrifice-bearing tenets, Working Backwards `PR/FAQs`, and the two-way Appendix contract.
- Zero-dependency Python 3 CLIs in `scripts/` (`scripts/strip_markdown.py`, `scripts/prose_lint.py`, and `scripts/validate_skill.py`). Enforces the `10,000`-word combined runtime budget and reports cadence variation, `MATTR-50` diversity, concrete-anchor ratios, and line-numbered mechanical and flourish tells without a composite AI score.
- Expanded anti-flourish guidance in [references/edit-and-anti-slop.md](references/edit-and-anti-slop.md) and detectors in `scripts/prose_lint.py` (`participial_tail_puffery`, `copula_avoidance`, `rhetorical_qa_pivots`, `performative_fragments`, `nominalizations_per_100w`, split negative parallelisms, and unanchored `without sacrificing` claims).
- Evaluation benchmark suite in `evals/` ([evals/JUDGE.md](evals/JUDGE.md), `evals/evals.json`, and `evals/trigger-evals.json`). Includes committed calibration pairs in `samples/` ([samples/README.md](samples/README.md), `samples/technical-doc.{before,after}.md`, `samples/executive-memo.{before,after}.md`, and `samples/one-pager.{before,after}.md`).
- Six active fitness gates (`F-001` through `F-006`) in `Makefile` and [docs/spec/fitness-functions.md](docs/spec/fitness-functions.md). Ships the full open-source [README.md](README.md), MIT license, governance policies, cross-harness agent briefings (`AGENTS.md`, `CLAUDE.md`, `GEMINI.md`), and Antigravity `.agents/` adapters.
- Negative `Don't use for...` scope triggers in [SKILL.md](SKILL.md), single-dialect consistency with literal identifier preservation ([SKILL.md](SKILL.md), [references/technical-and-docs.md](references/technical-and-docs.md)), and workspace prose-formatter precedence ([docs/spec/configuration.md](docs/spec/configuration.md)).
- Baseline tell detectors (`shorthand_ambiguities`, `exclamation_marks`, `false_agency`), `OSError`-safe exit code `2` CLI handling across `scripts/*.py`, and `--profile` / `--mode` (`technical`, `memo`, `one-pager`, `six-pager`, `narrative`) genre validation in `scripts/prose_lint.py`.
- Clean skill packaging and end-user install hygiene via `.gitattributes` `export-ignore`, `scripts/package_skill.py` (`--check`, `--output-dir`, `--install-to`, `--clean`, `--json`), `make package`, and active fitness gate `F-007` (`make fitness-clean-package`).

