# Architecture Catalog

Tabular C4 component catalog paired with [docs/architecture/diagrams.md](../architecture/diagrams.md).

| Element | Path | Type | Responsibility |
|---------|------|------|----------------|
| Core Skill Router | `SKILL.md` | Markdown skill | Frontmatter trigger, Step 0 `mode=` router, 6 universal safeguards, register/genre routing table, core prose hygiene |
| Slash Command Wrappers | `commands/write-{draft,edit,review,lint}.md` | Markdown commands | Deterministic `mode=<token> $ARGUMENTS` entry points for Claude Code |
| Draft Reference | `references/draft-and-brief.md` | Markdown reference | Goal restatement, primary-source brief deepening, perspective interview, `[TK]` markers, provenance note |
| Edit Reference | `references/edit-and-anti-slop.md` | Markdown reference | 5-step single-pass rewrite workflow, 4 contextual diagnostic tests, anti-slop catalog, craft restoration |
| Review Reference | `references/review-rubric.md` | Markdown reference | Read-only critique contract, candor rule, piece-level diagnosis, `keep`/`revise`/`ask-author`/`cut` passage verdicts |
| Technical Genre Guide | `references/technical-and-docs.md` | Markdown reference | Diataxis mode purity, developer style, ASD-STE100, Global English, READMEs, RFCs/ADRs, PR briefings |
| Business Genre Guide | `references/business-and-executive.md` | Markdown reference | BLUF memos, self-contained decision briefs, epistemic tags, metric vetting, status updates, emails |
| Narrative Memo Guide | `references/one-pager-and-six-pager.md` | Markdown reference | Door-type format selection, 5-part one-pagers, 7-part six-pagers, Working Backwards PR/FAQs, two-way appendix contract |
| Longform Genre Guide | `references/longform-and-persuasion.md` | Markdown reference | Essays, landing/launch copy, UX microcopy, speeches/slides, progressive diagrams, creative narrative |
| Markdown Stripper | `scripts/strip_markdown.py` | Python 3 CLI/module | Strips Markdown/code/tables/frontmatter into clean reader-visible prose blocks and heading lists |
| Prose Linter | `scripts/prose_lint.py` | Python 3 CLI/module | Computes cadence, lexical diversity, anchor/posture ratios, and mechanical, lexical, and flourish tell locations |
| Skill Package Validator | `scripts/validate_skill.py` | Python 3 CLI/module | Enforces word budgets (`<= 1,500` per file, `<= 10,000` combined), routing completeness, relative links, eval schemas, and repo prose hygiene |
| Evaluation Suite | `evals/evals.json`, `evals/trigger-evals.json`, `evals/JUDGE.md` | JSON + Markdown | Behavioral test cases, trigger optimization queries, and blinded 4-gate + 6-dimension judge rubric |
| Calibration Samples | `samples/*` | Markdown fixtures | Paired `.before.md` and `.after.md` documents verifying defect reduction and factual preservation |
| Antigravity Adapters | `.agents/` + `scripts/sync-agy-skills.py` | Markdown + Python 3 | Workspace hooks, skills, and custom subagent adapters derived from `.claude/` |
