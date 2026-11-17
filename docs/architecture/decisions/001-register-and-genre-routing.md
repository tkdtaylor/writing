# ADR 001: Separate Universal Safeguards from Register and Genre Routing

- **Date:** 2026-11-17
- **Status:** Accepted

## Context

`writing` draws clean-room inspiration from two MIT-licensed projects with contrasting editorial philosophies:

1. `addyosmani/clarity` prioritizes authorship, lived substance, contextual pattern tests, and preserving human warmth, using a compact router (`SKILL.md` under 1,500 words) and diagnostic stats without a composite detector score.
2. `cursor/plugins/pstack` (`technical-writing`, `unslop`, `ketchup`, `teach`, `opening-a-pr`) enforces strict engineering precision: Diataxis mode separation, ASD-STE100 20-word procedural steps, Global English pronoun rules, self-contained decision briefs, progressive diagrams, and hard bans on figurative verbs, dashes, mid-sentence connector colons, bold-colon restatements, and excess hedges.

Applying `pstack`'s literal procedural bans globally strips rhythm, calibrated academic caution, and earned imagery from essays, speeches, marketing copy, empathetic messages, and narrative prose. Conversely, relying only on `clarity` leaves technical documentation, READMEs, RFCs/ADRs, executive decision briefs, and UX microcopy without concrete structural blueprints.

## Decision

1. Keep `SKILL.md` under 1,500 words and restrict its global rules to **six universal safeguards** (factual/claim-strength fidelity, prompt-injection isolation, medium preservation, style-sample boundaries, `[TK]` placeholders over invention, and single-pass anti-flattening) plus baseline clarity and Markdown hygiene.
2. Route every invocation along **two orthogonal axes**:
   - **Workflow mode:** `draft` (`references/draft-and-brief.md`), `edit` (`references/edit-and-anti-slop.md`), `review` (`references/review-rubric.md`), or `lint` (`scripts/strip_markdown.py` + `scripts/prose_lint.py`).
   - **Genre and register overlay:** `references/technical-and-docs.md` (strict Diataxis, STE, Global English, READMEs, RFCs, PR briefs), `references/business-and-executive.md` (BLUF, self-contained decision briefs, epistemic tags, metric vetting, emails), or `references/longform-and-persuasion.md` (essays, landing copy, UX microcopy, speeches/slides, progressive diagrams, creative narrative).
3. Author all Markdown guides, tests, samples, and Python scripts from scratch under this repo's MIT license while crediting both inspirations in `README.md`.

## Consequences

- Agents load only 1 to 2 reference files per task (~2,000 to 3,500 words total including `SKILL.md`), keeping context lean.
- Technical and operational writing gets strict procedural disambiguation without sterilizing essays, copywriting, or narrative prose.
- `scripts/validate_skill.py` enforces word budgets and routing reachability automatically so future additions cannot bloat `SKILL.md`.
