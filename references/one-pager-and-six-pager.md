# One-Pagers, Six-Pagers, and Working Backwards PR/FAQs

Use this guide when drafting, editing, or reviewing narrative decision memos and product concept documents in the `Decision/Update` or `Argument` registers. Pair it with [references/business-and-executive.md](business-and-executive.md) for epistemic claim tags (`measured`, `inferred`, `open`) and four-part metric vetting.

## Format selection matrix (Door-Type Rule)

Pick the lightest document format that matches the decision's blast radius and reversibility.

| Format | Target Length | Decision Type and Reader Job | Reading Cadence |
|--------|---------------|------------------------------|-----------------|
| `One-Pager` | `350` to `550` words (`<= 1` page) | Reversible **Type 2 (two-way door)** decisions, fast cross-team alignment, or early discovery gate checks | `2` to `3` minute async or pre-meeting scan |
| `Six-Pager` | `1,800` to `2,500` words max body (`10` to `11`pt font) + unbounded `Appendix` | High-cost or irreversible **Type 1 (one-way door)** commitments, multi-team architecture or product bets, and annual or quarterly operational plans (`OP1`) | `15` to `30` minute silent study hall read before live debate |
| `Working Backwards PR/FAQ` | `<= 1` page Press Release + External and Internal FAQs | Pre-code customer value validation working backward from the shipped end state | `10` to `20` minute concept review before staffing |

**Ceiling, never a quota.** Six pages (`~2,500` words) is a strict ceiling, never a padding quota. If verified facts and causal arguments fill `2` to `3` pages, stop at page `3` and mark missing data `[TK: specific measurement]` instead of inflating background prose.

**Quote provenance rule.** Under Safeguard #1, never invent quotes inside operational one-pagers or six-pagers. In a `Working Backwards PR/FAQ`, label any illustrative future customer or executive quote `[Hypothetical PR-FAQ illustration]` or replace it with `[TK: customer quote]`.

## One-Pager 5-section blueprint

A one-pager earns a fast decision on a reversible two-way door without scheduling a thirty-minute readout. Keep total length between `350` and `550` words across five sections:

1. **BLUF / Decision Call:** State the exact yes-or-no call or option pick, your recommended choice, the single decision owner, and the deadline in `3` to `4` sentences.
2. **Problem and Customer/System Baseline:** Keep backstory under `100` words (`< 100` words). Quantify the measured status-quo cost for users or operators and explain why the decision cannot wait.
3. **Scope and Explicit Non-Goals:** Define what this decision changes and list two or three adjacent exclusions so reviewers do not relitigate neighboring roadmaps.
4. **Viable Options and Tradeoffs:** Compare two or three real options, always including `Status Quo`. State build and run cost, external consumer impact, primary failure mode, and why each rejected option loses.
5. **Risks, Kill Switch, and Owned Next Steps:** Name the top operational risk, the concrete rollback trigger or kill switch, and `1` to `2` week dated actions assigned to single owners.

## Six-Pager 7-part narrative blueprint

A six-pager replaces slide pitches for costly Type 1 one-way doors so reviewers read the full causal chain silently in a `15` to `30` minute study hall before debating.

1. **Context and Governing Question:** Frame the customer or system problem and state your recommendation on page `1`. Never structure a memo like a mystery novel that withholds the conclusion until page `6`.
2. **Tenets:** List `3` to `5` numbered tie-breaking principles before introducing the solution. Each tenet must encode a **real sacrifice** between two good properties so a reasonable peer could argue the opposite (`"Keep p99 checkout under 250 ms even when synchronous fraud checks add 15% compute cost"`). Ban zero-cost truisms like `"prioritize security, quality, and velocity"`.
3. **Current State and Candid Lessons Learned:** Separate controllable **input metrics** (levers the team directly operates, such as cache hit ratio or onboarding step count) from lagging **output metrics** (retention, revenue, SLA attainment). Include candid `Lessons Learned` naming what missed target in prior cycles and why.
4. **Goals and Vetted Targets:** State falsifiable targets with exact unit, sample size or time window, baseline, and scope limiter.
5. **Proposed Plan and Causal Mechanism:** Explain how specific engineering, product, or operational changes move controllable input metrics to output targets. Cover sequencing, staffing and run cost, and explicit non-goals.
6. **Alternatives Considered, Hostile Objections, and Risks:** Steelman the `2` strongest competing paths a skeptical Staff Engineer or VP Finance would champion. Prove why those paths lose on tenets or unit economics, and define failure triggers and rollback criteria.
7. **Appendices:** Place unbounded supporting tables, financial models, architecture diagrams, raw benchmark logs, and deep technical Q&A after page `6`.

## Working Backwards PR/FAQ rules

Use a `PR/FAQ` before writing production code to test whether the end state solves an acute customer problem worth the engineering and operational cost.

- **Press Release (`<= 1` page):** Name the target customer persona, the painful current baseline, the concrete capability and measurable outcome, and the first step to adopt it. Mark any illustrative quote `[Hypothetical PR-FAQ illustration]` or `[TK: customer quote]`.
- **External FAQs:** Answer literal customer questions on pricing, migration effort, permissions, failure handling, and exact product limits.
- **Internal FAQs:** Confront hard leadership objections covering unit economics, unit cost at scale, technical bottlenecks, cross-team dependencies, legal or privacy constraints, and explicit kill criteria.

## Prose density, Appendix contract, and anti-failure rules

Narrative memos work because complete sentences force authors to expose their causal logic rather than hiding gaps behind bullet indentation.

- **Enforce `80%+` complete causal prose:** Write at least `80%+` of the memo body as full paragraphs with explicit subjects, verbs, and causal connectors. Reserve bullets strictly for `Tenets`, metric definitions, and dated action items so slide-speak fragments never mask unverified causal arrows.
- **Honor the two-way Appendix contract:** First, pages `1` to `6` must stand alone so a silent study-hall reader can decide without flipping to the `Appendix`. Summarize every essential table or diagram takeaway in one body sentence with an exact citation such as `(see Appendix B, Table 2)`. Second, enforce zero narrative overflow and never dump page `7` of essay prose into `Appendix A` to evade the six-page cap.
- **Cut memo anti-patterns:** Ban `**Bold Pillar:**` disguised listicles posing as narrative prose, and ban tradeoff-denial claims (`without sacrificing`, `without compromising`). Reject strawman options built to lose and diff-narrating `v2` headings (`Updated Capacity Section`) that describe edits instead of the governing claim.
