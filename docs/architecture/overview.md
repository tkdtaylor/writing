# Architecture Overview

`writing` is a text-first skill and standard-library Python diagnostic toolkit. It teaches coding and chat agents how to draft, rewrite, critique, and lint prose across any genre without flattening human voice or inventing facts.

## Design principles

1. **Substance before surface.** Most weak LLM writing fails because it lacks a concrete reader, actor, mechanism, or primary source, not merely because it picked a cliché word. Every workflow checks truth, reader job, and concrete anchors before polishing sentences.
2. **Mode and register separation.** Rules that make an API reference or incident runbook crisp (literal nouns, zero figurative language, 20-word procedural steps) ruin an essay, keynote, or landing page. `SKILL.md` enforces universal safeguards and clean mechanics first. It then loads only the matching workflow mode (`references/draft-and-brief.md`, `edit-and-anti-slop.md`, `review-rubric.md`) and genre guide (`technical-and-docs.md`, `business-and-executive.md`, `one-pager-and-six-pager.md`, `longform-and-persuasion.md`).
3. **Token-budgeted progressive disclosure.** `SKILL.md` stays under 1,500 words, each reference stays under 1,500 words, and the combined runtime catalog stays at or under 10,000 words so agents pay minimal context overhead per turn.
4. **Diagnostics without a gameable score.** The stripper in `scripts/strip_markdown.py` isolates reader-visible prose from Markdown syntax before linting. Next, `scripts/prose_lint.py` reports structural, lexical, and flourish signals (cadence CV, MATTR-50, 3-gram repeats, anchor ratios, and line-numbered tells) without a composite "AI detector" number.
5. **Zero-dependency portability.** All runtime scripts use the Python 3.10+ standard library only. Users install the clean runtime payload into Claude Code, Antigravity, Codex, Cursor, Copilot, or Windsurf from filtered release or archive tarballs or `scripts/package_skill.py --install-to`. Maintainer `.agents/` folders never leak into end-user skill scan paths.

## Component tour

- **Entry router (`SKILL.md` + `commands/write-*.md`).** Routes explicit `mode=` tokens (`draft`, `edit`, `review`, `lint`) or natural-language requests, applies the six shared safeguards, and selects the right reference files.
- **Workflow references (`references/{draft-and-brief,edit-and-anti-slop,review-rubric}.md`).** Define step-by-step procedures for briefing before drafting and running a single deliberate edit pass with contextual diagnostic tests. In review mode, `review-rubric.md` specifies candid read-only critiques with `keep`, `revise`, `ask-author`, and `cut` verdicts.
- **Genre references (`references/technical-and-docs.md`, `business-and-executive.md`, `one-pager-and-six-pager.md`, `longform-and-persuasion.md`).** Cover technical docs, READMEs, RFCs/ADRs, PR briefings, BLUF memos, decision briefs, narrative one-pagers and six-pagers, PR/FAQs, emails, essays, copy, UX microcopy, speeches, diagrams, and creative narrative.
- **CLI diagnostics, validator, and packager (`scripts/{strip_markdown,prose_lint,validate_skill,package_skill}.py`).** Provide deterministic prose inspection for `mode=lint`, clean runtime staging via `package_skill.py`, and CI-ready fitness gates (`F-001`..`F-007`) for `make fitness`.
- **Evaluation and samples (`evals/` + `samples/`).** Encode 4 hard gates and 6 scored dimensions in `evals/JUDGE.md`. Behavioral cases live in `evals/evals.json`, trigger queries live in `evals/trigger-evals.json`, and calibrated before/after pairs live in `samples/`.

## Architecture decisions

- [ADR 001: Register and Genre Routing](decisions/001-register-and-genre-routing.md) separates the six universal safeguards and workflow modes from register-specific genre guides.
- [ADR 002: Narrative Memos and Anti-Flourish Rules](decisions/002-narrative-memos-and-anti-flourish-rules.md) splits standalone one-pager, six-pager, and PR/FAQ blueprints into `references/one-pager-and-six-pager.md` and defines discourse-level anti-flourish rules.
