# Business and executive writing guide

Use this guide when drafting, editing, or reviewing workplace and leadership prose in the `Decision/Update`, `Argument`, or operational `Explanation` registers. It covers `BLUF` memos, analytical reports, self-contained decision briefs, epistemic claim tagging, metric vetting, async status updates, and professional emails or chat messages.

## BLUF memos and analytical reports

Busy readers open a memo to learn what changed, what you recommend, and what you need from them, not to replay your research chronology.

- **Lead with the Bottom Line Up Front (`BLUF`).** State the conclusion, recommendation, or required decision in paragraph one (`3` to `4` sentences maximum), naming the decision owner and deadline.
- **Organize by governing takeaways.** Group body sections under assertive takeaway headings (`Regional read replicas cut EU checkout latency by 38%`). Never use vague topic buckets (`Database Investigation`) or chronological diaries (`First we profiled X`).
- **Separate observation from interpretation.** Present verified facts and measurements before explaining why they happened or what the organization should do next.
- **Close with owned actions.** End analytical reports with named owners, concrete deliverables, and review dates instead of vague promises to "keep monitoring the situation."

## Self-contained decision briefs

A decision brief succeeds when an executive or tech lead can make an informed call from the document alone without chasing five linked threads, slide decks, or chat channels.

- **Spend words on the decision, not backstory.** Keep historical background under `100` words (`< 100` words). Put the saved space into option tradeoffs, costs, and failure modes.
- **Consumer impact over internal process narration.** Describe outcomes in customer, user, or operator terms rather than internal code mechanics. Write `"Cardholders complete checkout on the first retry without duplicate holds"`, never `"Refactored PaymentRetryWorker state handlers"`.
- **Order riskiest first.** When a brief covers multiple calls, place the highest-blast-radius, hardest-to-reverse, or costliest decision at the top and routine defaults at the bottom.
- **Anchor option costs against baseline cost.** State the baseline cost of doing nothing (ongoing revenue loss, incident burn, or SLA risk) beside the implementation and maintenance cost of each proposed option.

Format every decision item with five explicit fields:

- **Call.** State the exact yes-or-no question or option choice required, who holds the decision, and the deadline.
- **Recommendation.** Name the recommended option in one direct sentence, followed by viable alternatives comparing each option cost against the status-quo baseline cost.
- **Impact.** Quantify the user, customer, reliability, or financial outcome in external consumer terms rather than internal team effort.
- **Evidence.** Cite vetted measurements, experiments, customer tickets, or incident data supporting the recommendation, marked with epistemic labels.
- **Risk.** Name the primary failure mode, blast radius, reversal cost, and concrete mitigation or kill switch.

## Epistemic labels and metric vetting

Executive trust collapses when rough hunches wear the same prose confidence as production telemetry, or when vanity percentages hide tiny samples.

### Epistemic claim tags

Whenever a memo, postmortem, or brief combines hard telemetry with hypotheses and unknowns, label mixed-certainty statements explicitly:

- **`measured`.** Directly observed in named logs, financial ledgers, controlled experiments, or reproducible benchmarks (`[measured] Checkout p95 latency fell from 480 ms to 290 ms across 180k US-East orders`).
- **`inferred`.** Reasoned from partial signals, proxy metrics, or adjacent incidents where direct instrumentation is absent (`[inferred] Abandonment dropped primarily on mobile Safari based on session-timeout ratios`).
- **`open`.** Unverified assumption or unanswered question that still needs measurement. Pair each item with an owner and check (`[open] Peak Black Friday pool ceiling; load test Friday`), or mark `[TK: verify peak pool ceiling]`.

### Four-part metric vetting checklist

Never publish naked multipliers or unanchored percentages (`"3x faster"`, `"churn fell 14%"`). Every reported business or performance metric must supply four anchors, or else be labeled `inconclusive`:

1. **Unit.** State the exact unit and aggregation (`p99 latency in ms`, `annualized net USD retention`, `failed jobs per 10,000 runs`), never vague nouns like "efficiency" or "stability."
2. **Sample or runs.** Specify the sample size, time window, cohort, or benchmark run count (`N = 24,500 paid signups over 28 days`, `40 cold-start runs on c7g.xlarge`).
3. **Baseline.** Name the exact comparison point (`vs 310 ms on v1.8`, `vs trailing 12-week median before the pricing change`).
4. **Limiter.** State the ceiling, scope boundary, or confounding constraint where the number stops holding (`single-tenant staging dataset; disk I/O caps writes above 4,000/sec`). When samples are tiny or confounded, mark the metric `inconclusive`.

## Async updates, emails, and workplace messages

Respect reader attention in status posts, emails, and chat messages by putting the point at the top and removing social throat-clearing.

- **Ask, deadline, or status in line one.** Put the exact request, deadline, or project health tag (`On track`, `At risk`, `Blocked`) in both the subject line and sentence one (`Action by Thu 16:00 UTC: Approve 30-day log retention cap`).
- **Complete spoken standalone bullets.** Write status bullets as full sentences you could say aloud (`Webhook delivery rose from 97.2% to 99.8% after isolating slow endpoints`). Avoid cryptic fragments (`Webhooks - isolated slow endpoints, metrics up`).
- **Delta-focused async updates.** Cover what changed for users since the last update, what is blocked (naming who can unblock it), and what ships next with dates.
- **Direct register without sycophancy.** Match social formality while cutting hollow flattery (`I hope this finds you well!`) and apologetic hedging (`Just circling back to gently nudge...`). Give one sentence of context, make one clear ask or safe default (`Unless you flag concerns by Friday noon, we will ship Option B`), and stop.
