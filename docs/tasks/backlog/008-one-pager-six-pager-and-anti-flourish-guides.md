# Task 008: One-Pager, Six-Pager, and Anti-Flourish Skill Guides

- **Priority:** P0
- **Model tier:** `balanced`
- **Dependencies:** None (Wave 1)
- **Test spec:** `docs/tasks/test-specs/008-one-pager-six-pager-and-anti-flourish-guides-test-spec.md`

## Objective

Add comprehensive support for authoring, editing, and reviewing **One-Pagers**, **Six-Pagers**, and **Working Backwards PR/FAQs**, and upgrade `SKILL.md` and `references/edit-and-anti-slop.md` with empirical 2025-2026 anti-flourish rules.

## Deliverables (exclusive file scope)

- `references/one-pager-and-six-pager.md`
- `SKILL.md`
- `references/business-and-executive.md`
- `references/edit-and-anti-slop.md`
- `docs/architecture/decisions/002-narrative-memos-and-anti-flourish-rules.md`
- `tests/test_task_008_memos_and_flourish.py`

Do not edit `docs/tasks/test-specs/coverage-tracker.md` or files owned by Task 009 (`scripts/*`, `docs/spec/*`). Keep total whitespace-split words across `SKILL.md` + all 7 `references/*.md` `<= 8,500` words so `validate_skill.py` passes inside this isolated worktree even before Task 009 merges!

## Implementation details

1. **Create `references/one-pager-and-six-pager.md` (`~950` to `1,100` words, `<= 1,500`):**
   - **Format selection matrix (Door-Type Rule):**
     - *One-Pager (`350` to `550` words, `<= 1` page):* Reversible **Type 2 (two-way door)** decisions, fast cross-team alignment, or early discovery gate checks read in `2` to `3` minutes.
     - *Six-Pager (`1,800` to `2,500` words max body at `10` to `11`pt font + unbounded `Appendix`):* High-cost or hard-to-reverse **Type 1 (one-way door)** commitments, multi-team architecture/product bets, or annual/quarterly operational plans (`OP1`) read silently in a `15` to `30` minute study hall before debate. Six pages is a strict **ceiling, never a quota**: if validated inputs only fill `2` to `3` pages, stop there and mark missing data `[TK: ...]` instead of padding.
     - *Working Backwards PR/FAQ (`<= 1`-page Press Release + External/Internal FAQs):* Pre-code customer value validation from the end state backward. Under Safeguard #1, label any illustrative future quote `[Hypothetical PR-FAQ illustration]` or `[TK: customer quote]`, and **never** invent quotes inside operational one-pagers or six-pagers.
   - **One-Pager 5-section blueprint:** (1) `BLUF / Decision Call` (`3` to `4` sentences: exact call, recommended pick, owner, deadline), (2) `Problem and Customer/System Baseline` (`< 100` words, measured status-quo cost, why now), (3) `Scope and Explicit Non-Goals` (`2` to `3` adjacent exclusions), (4) `Viable Options and Tradeoffs` (`2` to `3` options including Status Quo, build/run cost, consumer impact, failure mode, why rejected options lose), (5) `Risks, Kill Switch, and Owned Next Steps` (`1` to `2` week dated single-owner actions).
   - **Six-Pager 7-part narrative blueprint:** (1) `Context and Governing Question` (state recommendation on page 1, never a mystery novel), (2) `Tenets` (`3` to `5` numbered tie-breakers before the solution; each must encode a **real sacrifice** between two good properties so a reasonable peer could argue the opposite, banning zero-cost truisms like `"prioritize security, quality, and velocity"`), (3) `Current State and Candid Lessons Learned` (separate controllable **input metrics** from lagging **output metrics**, plus what missed target previously and why), (4) `Goals and Vetted Targets` (unit, sample/window, baseline, limiter), (5) `Proposed Plan and Causal Mechanism` (how interventions move inputs to outputs, sequencing, cost, non-goals), (6) `Alternatives Considered, Hostile Objections, and Risks` (steelman the `2` strongest competing paths a Staff Engineer or VP Finance would champion, prove why they lose on tenets/economics, name failure triggers and rollback criteria), (7) `Appendices` (unbounded tables, models, diagrams, deep Q&A).
   - **Prose density, Two-Way Appendix Contract, and Anti-Failure Rules:** Require `80%+` complete causal prose paragraphs (bullets reserved strictly for Tenets, metric definitions, and action items so slide-speak never hides unverified causal arrows). Enforce the two-way Appendix contract: (a) pages `1` to `6` stand alone so a silent-study-hall reader can decide without flipping to the Appendix, summarizing each critical table/diagram takeaway in one body sentence citing `(see Appendix B, Table 2)`; (b) zero narrative overflow (never dump page 7 of essay prose into Appendix A). Ban `**Bold Pillar:**` disguised listicles, tradeoff-denial (`without sacrificing`), strawman options, and diff-narrating v2 headings.
2. **Update `SKILL.md` and `references/business-and-executive.md`:**
   - Include `one-pagers`, `six-pagers`, and `PR/FAQs` in `SKILL.md` frontmatter description and Step 2 routing table (`Decision/Update` and `Argument` rows linking `references/one-pager-and-six-pager.md`), and cross-link from `references/business-and-executive.md`.
   - In `SKILL.md` Step 3 punctuation mechanics, warn against the **comma-splice overcorrection trap**: when avoiding prose em dashes (`U+2014`) and mid-sentence connector colons, pick the exact syntactic tool the thought needs (`because`/`although` clauses, parentheses `(...)` for brief genuine asides, or periods) rather than flattening everything into monotonous comma chains, and cut ornamental LLM flourish. Tighten wording slightly so `SKILL.md` stays crisp (`~1,150` to `1,250` words).
3. **Upgrade `references/edit-and-anti-slop.md` (`<= 1,450` words):**
   - Tighten any verbose sentences and expand Section 4 to cover the empirical 2025-2026 flourish and discourse tells (wrapping literal tell examples in inline backticks, zero prose `\u2014`):
     - Punctuation overcorrection trap (use explicit connectors, parentheses `(...)` for real brief asides, or periods instead of flat comma splices when removing `U+2014`).
     - Trailing participial `-ing` puffery clauses (`, highlighting...`, `, underscoring...`, `, ensuring...`, `, fostering...`, `, showcasing...`, `, paving the way for...` tacked onto facts to fake significance; delete or turn real effects into finite verbs with numbers).
     - Copula avoidance (`serves as a`, `stands as a`, `functions as a`, `marks a`, `boasts` instead of plain `is`, `are`, `has`).
     - Self-posed rhetorical Q&A pivots (`The result? Faster builds.`, `The catch?`, `Why does this matter?`) and performative mic-drop fragments (`Full stop.`, `Simple as that.`, `And maybe that's the point.`).
     - Metaphorical flourish verbs (`unleash`, `harness`, `reimagine`, `ignite`, `weave`, `illuminate`, `unpack`) and evaluative magic adverbs (`quietly`, `genuinely`, `deeply`, `remarkably`).
     - Expanded negative parallelisms & corrective frames (two-sentence `This isn't X. It's Y.`, `less like X and more like Y`, `rather than merely/simply`, tripled `Not X. Not Y. Z.`).
     - Tradeoff-denial clauses (`without sacrificing`, `without compromising`), prepositional nominalization chains (`the implementation of`), paragraph-closing tie-backs (`Together, these...`, `Ultimately, this...`), and vague plural attributions (`Experts argue`, `Industry reports suggest`).
4. **Record ADR 002** in `docs/architecture/decisions/002-narrative-memos-and-anti-flourish-rules.md` documenting why `one-pager-and-six-pager.md` is split out as a dedicated reference and summarizing the empirical anti-flourish additions.

## Verification plan

- Write `tests/test_task_008_memos_and_flourish.py` covering `TC-008-01` through `TC-008-04`.
- Run `python3 scripts/validate_skill.py`, `python3 scripts/prose_lint.py SKILL.md references/*.md`, and `make check`, verifying zero errors and `combined_runtime <= 8500`.
