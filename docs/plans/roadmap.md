# Roadmap

## Milestone 1: Version 1 Core Skill and Diagnostic Suite (Active)

Build a generic, cross-harness open-source LLM writing skill with deterministic workflow modes, register-aware genre guides, zero-dependency Python 3 diagnostics, evaluation rubrics, and calibration samples.

- **Task 001:** Core `SKILL.md` entry point (<1,500 words) and optional Claude Code slash commands (`commands/write-*.md`).
- **Task 002:** Workflow mode references (`draft-and-brief.md`, `edit-and-anti-slop.md`, `review-rubric.md`).
- **Task 003:** Genre and register references (`technical-and-docs.md`, `business-and-executive.md`, `longform-and-persuasion.md`).
- **Task 004:** Zero-dependency `scripts/strip_markdown.py` and `scripts/prose_lint.py` CLI analyzers.
- **Task 005:** Evaluation suite (`evals/evals.json`, `evals/trigger-evals.json`, `evals/JUDGE.md`) and `samples/` before/after pairs.
- **Task 006:** Package validator (`scripts/validate_skill.py`) checking word budgets, link integrity, mode symmetry, and prose hygiene.
- **Task 007:** Executable fitness gates (`F-001`..`F-006`), full open-source `README.md`, and `CHANGELOG.md` release preparation.
- **Task 008:** Narrative memo reference (`references/one-pager-and-six-pager.md`) for One-Pagers, Six-Pagers, and Working Backwards `PR/FAQs`, plus comma-splice overcorrection and anti-flourish guidance.
- **Task 009:** Expanded flourish detectors in `scripts/prose_lint.py` (`participial_tail_puffery`, `copula_avoidance`, `rhetorical_qa_pivots`, `performative_fragments`, `nominalizations_per_100w`) and the `10,000`-word combined runtime budget in `scripts/validate_skill.py`.
- **Task 010:** Narrative `samples/one-pager.{before,after}.md` calibration pair, expanded memo and anti-flourish eval suites (`evals/evals.json`, `evals/trigger-evals.json`), and repository documentation sync.
- **Task 011:** Hardened `OSError` exit code `2` handling in `scripts/validate_skill.py` and `scripts/strip_markdown.py` with `TemporaryDirectory` test isolation.
- **Task 012:** Negative `Don't use for...` trigger boundaries in `SKILL.md`, single-dialect consistency with literal identifier preservation, and workspace prose-formatter precedence.
- **Task 013:** Baseline prose-lint tell detectors (`shorthand_ambiguities`, `exclamation_marks`, `false_agency`), `OSError` CLI guards, and `--profile` / `--mode` genre validation (`technical`, `memo`, `one-pager`, `six-pager`, `narrative`).
- **Task 014:** Clean skill packaging and end-user install hygiene via `.gitattributes` `export-ignore`, `scripts/package_skill.py`, `make package`, and `F-007`.


## Milestone 2: Corpus Calibration and Iterative Refinement (Planned)

- Ingest real-world user writing samples via `training/inbox/` to sharpen anti-slop rules, false-positive exclusions, and genre templates.
- Run blinded A/B evaluation sweeps using `evals/JUDGE.md` and `skill-creator` description optimization.
- Tag `v0.1.0` public release.
