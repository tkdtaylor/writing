# ADR 002: Dedicated Narrative Memo Guide and Empirical Anti-Flourish Rules

- **Date:** 2026-11-18
- **Status:** Accepted

## Context

Workplace decision writing spans two distinct operating cadences:

1. Everyday operational communication (`BLUF` memos, compact five-field decision items, async updates, and emails) fits cleanly in `references/business-and-executive.md` alongside epistemic claim tags and four-part metric vetting.
2. High-leverage narrative proposals cover `One-Pagers` (reversible Type 2 two-way doors), `Six-Pagers` (costly Type 1 one-way doors read in silent study halls), and `Working Backwards PR/FAQs`. Those formats require multi-part blueprints, sacrifice-bearing `Tenets`, `80%+` complete causal prose, a two-way `Appendix` contract, and quote-provenance safeguards.

Crowding both formats into the general business guide would breach its `1,500`-word cap and force routine email turns to load study-hall six-pager rules. Meanwhile, 2025-2026 LLM drafts exhibit recurring discourse flourishes and a punctuation overcorrection trap where writers removing prose em dashes (`U+2014`) flatten distinct clauses into monotonous comma splices.

## Decision

1. Create `references/one-pager-and-six-pager.md` (`<= 1,500` words) and route `one-pager`, `six-pager`, and `PR/FAQ` requests to it from `SKILL.md` (`Argument` and `Decision/Update` rows) and the executive guide.
2. Specify the Door-Type matrix, the 5-section One-Pager blueprint (`350` to `550` words), and the 7-part Six-Pager blueprint (`<= 2,500`-word ceiling, sacrifice-bearing `Tenets`, input vs output metrics, candid `Lessons Learned`, steelmanned objections, and `Appendices`). Require PR/FAQ quote labels (`[Hypothetical PR-FAQ illustration]` or `[TK: customer quote]`), `80%+` causal prose, and the two-way Appendix contract.
3. Update `SKILL.md` Step 3 and `references/edit-and-anti-slop.md` Section 4 to prevent comma-splice flattening by choosing explicit causal or concessive clauses, parentheses `(...)` for brief genuine asides, or periods. Document 2025-2026 flourish tells including trailing `-ing` puffery clauses, copula avoidance, rhetorical Q&A pivots, mic-drop fragments, flourish verbs, magic adverbs, expanded negative parallelisms, tradeoff denial, nominalizations, tie-backs, and vague attributions.

## Consequences

- Routine workplace turns load `references/business-and-executive.md` alone, while narrative memo turns load `references/one-pager-and-six-pager.md` on demand within per-file and combined runtime budgets.
- Safeguard #1 holds across `PR/FAQs` by labeling illustrative future quotes and banning fabricated quotes in operational memos.
- Editing guidance clears modern discourse-level slop without flattening natural sentence variety into comma chains.
