# Architecture Overview

`writing` is a text-first skill and standard-library Python diagnostic toolkit that teaches coding and chat agents how to draft, rewrite, critique, and lint prose across any genre without flattening human voice or inventing facts.

## Design principles

1. **Substance before surface.** Most weak LLM writing fails because it lacks a concrete reader, actor, mechanism, or primary source, not merely because it picked a cliché word. Every workflow checks truth, reader job, and concrete anchors before polishing sentences.
2. **Mode and register separation.** Rules that make an API reference or incident runbook crisp (literal nouns, zero figurative language, 20-word procedural steps) ruin an essay, keynote, or landing page. `SKILL.md` enforces universal safeguards and clean mechanics, then loads only the matching workflow mode (`references/draft-and-brief.md`, `edit-and-anti-slop.md`, `review-rubric.md`) and genre guide (`technical-and-docs.md`, `business-and-executive.md`, `longform-and-persuasion.md`).
3. **Token-budgeted progressive disclosure.** `SKILL.md` stays under 1,500 words, and each reference stays under 1,500 words so agents pay minimal context overhead per turn.
4. **Diagnostics without a gameable score.** `scripts/strip_markdown.py` isolates reader-visible prose from Markdown syntax, and `scripts/prose_lint.py` reports specific structural and lexical signals (cadence CV, MATTR-50, 3-gram repeats, anchor vs hedge/booster ratios, em dashes, mid-sentence connector colons, bold-label restatements, inflated style verbs) without collapsing them into a composite "AI detector" number.
5. **Zero-dependency portability.** All runtime scripts use the Python 3.10+ standard library only so users can install the skill into Claude Code, Antigravity, Codex, Cursor, Copilot, or Windsurf via `git clone` or `cp`.

## Component tour

- **Entry router (`SKILL.md` + `commands/write-*.md`):** Routes explicit `mode=` tokens (`draft`, `edit`, `review`, `lint`) or natural-language requests, applies the six shared safeguards, and selects the right reference files.
- **Workflow references (`references/{draft-and-brief,edit-and-anti-slop,review-rubric}.md`):** Define step-by-step procedures for interviewing/briefing before drafting, running a single deliberate edit pass with contextual diagnostic tests, and delivering candid read-only critiques with `keep`, `revise`, `ask-author`, and `cut` verdicts.
- **Genre references (`references/{technical-and-docs,business-and-executive,longform-and-persuasion}.md`):** Provide actionable structural rules for technical documentation, READMEs, RFCs/ADRs, PR briefings, BLUF memos, decision briefs, emails, essays, marketing copy, UX microcopy, speeches/slides, progressive diagrams, and creative narrative.
- **CLI diagnostics and validator (`scripts/{strip_markdown,prose_lint,validate_skill}.py`):** Provide deterministic prose inspection for `mode=lint` and CI-ready package validation for `make fitness`.
- **Evaluation and samples (`evals/` + `samples/`):** Encode 4 hard gates and 6 scored dimensions in `evals/JUDGE.md`, behavioral prompts in `evals/evals.json`, trigger queries in `evals/trigger-evals.json`, and calibrated before/after documents in `samples/`.
