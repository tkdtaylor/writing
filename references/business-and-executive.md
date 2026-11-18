# Business and executive writing guide

Use this guide for workplace prose in the `Decision/Update`, `Argument`, or operational `Explanation` registers (`BLUF` memos, analytical reports, decision briefs, epistemic tags, metric vetting, 3P updates, emails, and thread replies). For standalone **one-pagers** (reversible Type 2 two-way doors), **six-pagers** (irreversible Type 1 one-way doors read in silent study halls), and **Working Backwards PR/FAQs**, load [references/one-pager-and-six-pager.md](one-pager-and-six-pager.md) alongside the epistemic and metric rules below.

## BLUF memos and analytical reports

Busy readers open a memo to learn what changed, what you recommend, and what you need, not to replay your research diary.

- **Lead with the Bottom Line Up Front (`BLUF`).** State the conclusion, recommendation, or call in paragraph one (`3` to `4` sentences max), naming the owner and deadline.
- **Organize by governing takeaways.** Group body sections under assertive takeaway headings (`Regional read replicas cut EU checkout latency by 38%`), never vague topic buckets (`Database Investigation`) or diaries (`First we profiled X`).
- **Separate observation from interpretation.** Present verified facts and measurements before explaining why they happened or what to do next.
- **Close with owned actions.** End reports with named owners, deliverables, and review dates instead of promises to `"keep monitoring."`

## Self-contained decision briefs

A decision brief lets a leader make an informed call from the page alone without chasing linked threads, decks, or chats. Use the five-field schema below for compact multi-item briefs, or switch to the one-pager or six-pager blueprints in [references/one-pager-and-six-pager.md](one-pager-and-six-pager.md) for narrative proposals.

- **Spend words on the decision, not backstory.** Keep historical background under `100` words (`< 100` words) and spend space on option tradeoffs, costs, and failure modes.
- **Consumer impact over internal process narration.** Describe outcomes in customer, user, or operator terms (`"Cardholders complete checkout on the first retry without duplicate holds"`, never `"Refactored PaymentRetryWorker state handlers"`).
- **Order riskiest first.** Place the highest-blast-radius, hardest-to-reverse, or costliest call at the top and routine defaults at the bottom.
- **Anchor option costs against baseline cost.** State the baseline cost of doing nothing (revenue loss, incident burn, or SLA risk) beside each option's build and maintenance cost.

Format every decision item with five explicit fields:

- **Call.** State the exact yes-or-no question or option choice, decision owner, and deadline.
- **Recommendation.** Name the recommended option in one sentence, then compare viable alternatives against the status-quo baseline cost.
- **Impact.** Quantify user, customer, reliability, or financial outcomes in external consumer terms.
- **Evidence.** Cite vetted measurements, experiments, tickets, or incident data marked with epistemic labels.
- **Risk.** Name the primary failure mode, blast radius, reversal cost, and mitigation or kill switch.

## Epistemic labels and metric vetting

Executive trust collapses when hunches wear telemetry confidence, or when vanity percentages hide tiny samples.

### Epistemic claim tags

Label mixed-certainty statements explicitly across memos, postmortems, and briefs:

- **`measured`.** Observed in named logs, ledgers, controlled experiments, or reproducible benchmarks (`[measured] Checkout p95 latency fell from 480 ms to 290 ms across 180k US-East orders`).
- **`inferred`.** Reasoned from partial signals, proxies, or adjacent incidents lacking direct telemetry (`[inferred] Abandonment dropped on mobile Safari based on session-timeout ratios`).
- **`open`.** Unverified assumption or question needing measurement. Pair each item with an owner and check (`[open] Peak Black Friday pool ceiling; load test Friday`), or mark `[TK: verify peak pool ceiling]`.

### Four-part metric vetting checklist

Never publish naked multipliers or unanchored percentages (`"3x faster"`, `"churn fell 14%"`). Every business or performance metric needs four anchors, or an `inconclusive` label:

1. **Unit.** State exact unit and aggregation (`p99 latency in ms`, `annualized net USD retention`, `failed jobs per 10,000 runs`), never vague nouns like `"efficiency."`
2. **Sample or runs.** Specify sample size, window, cohort, or run count (`N = 24,500 paid signups over 28 days`, `40 cold-start runs on c7g.xlarge`).
3. **Baseline.** Name the exact comparison point (`vs 310 ms on v1.8`, `vs trailing 12-week median`).
4. **Limiter.** State the ceiling, scope boundary, or confounder where the number stops holding (`single-tenant staging; disk I/O caps writes above 4,000/sec`). Mark tiny or confounded samples `inconclusive`.

## Async updates, emails, and workplace messages

Respect reader attention in status posts, emails, and chat messages by putting the point first and cutting throat-clearing.

- **Ask, deadline, or status in line one.** Put the request, deadline, or health tag (`On track`, `At risk`, `Blocked`) in the subject line and sentence one (`Action by Thu 16:00 UTC: Approve 30-day log retention cap`).
- **Complete spoken standalone bullets.** Write status bullets as full spoken sentences (`Webhook delivery rose from 97.2% to 99.8% after isolating slow endpoints`), never cryptic fragments (`Webhooks - isolated slow endpoints, metrics up`).
- **3P team updates (`Progress`, `Plans`, `Problems`).** Structure recurring status posts around shipped user-visible outcomes (`Progress`), dated next milestones (`Plans`), and concrete risks (`Problems`) naming the exact blocker, owner, and escalation ask.
- **Thread and reply discipline (`No context-rebuilding`).** In email threads, Slack or chat replies, and PR comments where the reader already knows the background, put the decision, answer, or next step in line one. Add only the single new fact or link they lack, and never restate their problem or bury the answer at the end.
- **Direct register without sycophancy.** Match social formality while cutting hollow flattery (`I hope this finds you well!`) and hedging (`Just circling back to gently nudge...`). Give one sentence of context, state one ask or safe default (`Unless you flag concerns by Friday noon, we will ship Option B`), and stop.
