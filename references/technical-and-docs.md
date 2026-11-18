# Technical and documentation guide

Use this guide for technical prose in the `Guide`, `Reference`, `Explanation`, or technical `Argument` registers. It covers tutorials, how-to guides, reference manuals, architecture explanations, `README` files, `RFC` and `ADR` proposals, PR briefings, incident postmortems, and changelogs or release notes.

## Layer 1: Diataxis mode purity

Technical docs fail when they mix reader jobs on one page. Separate docs into four Diataxis modes and keep one mode per document or section. When a procedure lectures on design history or a reference table buries a walkthrough, split and link across pages.

| Mode | Reader posture | Primary job | Rules that keep the mode pure |
|------|----------------|-------------|-------------------------------|
| `Tutorial` | Learning by doing | Build newcomer confidence via a repeatable lesson | Show a visible result every step, pick one fixed path, and omit theory or edge cases |
| `How-to` | Finishing a task | Guide a competent user to a concrete goal | Start from the goal, handle practical conditions, and skip basic tool lessons |
| `Reference` | Looking up facts | Describe machinery so structure mirrors the artifact | State exact signatures, flags, types, defaults, limits, and errors in neutral prose |
| `Explanation` | Seeking context | Clarify architecture, background, and tradeoffs | Keep opinion, rationale, and design comparisons here, never inside procedures |

## Layer 2: Developer style

Write for engineers who scan headings and code blocks first, reading prose only when a command or boundary needs context.

- **Direct address and active present tense.** Address the reader as `you` (`Run the migration`, `The broker acks the batch`) instead of passive indirection (`Batches are acknowledged`).
- **Conditions before instructions.** Lead with the `if` or `when` clause so readers skip irrelevant commands (`If your cluster runs Kubernetes 1.29 or earlier, pass --legacy-auth`).
- **Common path first.** Lead with the default production workflow. Move rare flags, workarounds, and troubleshooting to subsections below.
- **Zero minimizing or polite filler.** Cut `simply`, `easily`, `just`, `obviously`, and `please` from procedures. Nothing feels simple during an outage at 03:00.
- **Descriptive link text.** Name the destination (`see the OAuth token schema`, never `click here`, `this page`, or bare URLs).
- **Sentence-case headings with a point.** Write sentence-case headings naming the action or takeaway (`Verify webhook signatures`, not `Webhook Signature Verification Overview`).
- **List discipline.** Use numbered lists (`1.`, `2.`) only for ordered steps, and unordered bullets (`-`) for unordered options or notes.

## Layer 3: ASD-STE100 procedural clarity

Apply Simplified Technical English (`ASD-STE100`) whenever instructions alter state, configuration, or production traffic.

- **One instruction per sentence.** Give one action per step unless two actions must happen together.
- **Twenty-word procedural ceiling.** Keep every procedural step `<= 20` words (`20`-word max) and surrounding prose crisp.
- **Warnings and prerequisites before the step.** Place data-loss warnings, downtime notices, and permissions *before* the command they guard, never below the code block (`Warning: Dropping this index blocks writes for 90 seconds`).
- **Observable verification.** Follow state-changing steps with an explicit check showing expected stdout, HTTP status, or query output.
- **Strict term consistency.** Pick one noun per concept (`workspace`, never cycling across `workspace`, `project`, and `environment`) and one verb per action.

## Layer 4: Global English disambiguation

Eliminate syntactic ambiguity so international readers and machine translators parse every rule identically.

- **Pin limiting modifiers.** Place `only`, `not`, `at least`, and `exactly` next to the restricted word (`Run this script only on the read replica`, not `Only run this script on the read replica`).
- **Unpack dense noun strings.** Break up four or more stacked nouns with prepositions (`cluster node certificate rotation interval` becomes `rotation interval for cluster node certificates`).
- **Ban bare clause-level `this` and `which`.** Never use bare `this` (`This spikes tail latency`) or `, which` (`The queue fills up, which drops webhooks`) for a whole clause. Add an explicit noun (`This lock contention spikes tail latency`) or split sentences.
- **Spell out ambiguous slashes.** Replace `and/or` and overloaded `/` pairs with explicit words (`A, B, or both`; `client and server timeouts`).
- **Plain international vocabulary.** Replace local idioms, sports metaphors, and Latin shorthand (`e.g.`, `i.e.`) with plain English (`for example`, `that is`).
- **Consistent dialect, exact identifiers.** Keep one English dialect (`en-US` vs `en-GB` or `en-AU` spelling, punctuation, and dates) across a document or repo rather than mixing dialects. Never localize or respell literal UI labels, API field names, config keys, CLI flags, or code identifiers (keep `--color` and `organization_id` exact inside `en-GB` prose).

## Blueprint: README files

A strong `README` proves what the project does and gets a newcomer to a working result in two minutes.

1. **Plain one-sentence opener.** State what the tool is, what problem it solves, and who uses it in sentence one, before badges or slogans.
2. **Prerequisites, install, and copy-paste quickstart.** List runtime versions, one verified install command, and a runnable example with literal expected output.
3. **Core usage.** Show the `2` to `3` everyday commands, API calls, or config options.
4. **Links out to Diataxis docs.** Link to separate `Tutorial`, `How-to`, `Reference`, and `Explanation` pages rather than growing a monolith.

## Blueprint: RFCs and ADRs

Design proposals (`RFC`) and Architecture Decision Records (`ADR`) expose engineering costs and operational risks before coding starts.

1. **Concrete problem statement.** Ground the proposal in named incidents, latency or cost figures, failure rates, or developer friction (`[TK: incident or benchmark metric]`, never invented numbers).
2. **Explicit non-goals and constraints.** List problems left unsolved alongside hard boundaries (SLOs, compliance, wire compatibility, team capacity).
3. **Honest options and steelmanned objection.** Compare viable alternatives with candid costs, never strawmen. Give the strongest skeptical objection its own subsection and answer it directly.
4. **Recommended design.** Specify component boundaries, schemas or API contracts, state transitions, and failure recovery.
5. **Blast radius, migration, and verification.** Detail affected callers, backfill stages, rollback triggers, and rollout checks. Compact `ADR` files use `Status`, `Context`, `Decision`, `Alternatives considered`, and `Consequences`.

## Blueprint: PR and change briefings (< 40 lines)

Keep pull request descriptions and release briefings under `40` lines (`< 40` lines) so reviewers grasp intent, tradeoffs, and risk on one screen. Link long logs or flamegraphs externally.

- **Why.** Lead with user impact, bug symptom, or system goal rather than code edits.
- **What changed.** Summarize behavioral and module changes in `2` to `4` bullets without narrating diffs.
- **Scope.** Separate what lands now from what waits for a follow-up PR.
- **Tradeoffs.** Record only rejected options a reviewer would ask about, plus why they lost.
- **Blast radius.** Name affected endpoints, migrations, feature flags, compatibility risks, and the rollback command.
- **Verification.** List automated tests, repro commands, and staging checks proving the change works.

## Blueprint: Blameless incident postmortems

Incident postmortems turn production failures into durable engineering fixes without scapegoating operators.

- **Impact and UTC window up front.** Open with the user-visible symptom, quantified failed requests or revenue and SLO burn, exact `YYYY-MM-DD HH:MM UTC` start-to-recovery window, and incident severity.
- **Root cause vs trigger.** Separate the latent systemic weakness (*Root cause*, such as missing connection-pool timeouts) from the proximate event (*Trigger*, such as a routine traffic spike or config deploy).
- **UTC detection and mitigation timeline.** List chronological `HH:MM UTC` milestones covering first symptom, alert fire, on-call engagement, mitigation applied, and full service recovery.
- **Systemic controls over human blame.** Never blame an individual operator (`engineer ran wrong command`). Ask why tooling, permissions, or canaries allowed the action to cause harm. Close with owned **Action items** naming `Owner`, `Systemic fix`, and tracking ticket or `[TK: ticket ID]`.

## Blueprint: Changelogs and release notes

Release notes help human upgraders decide whether and how to adopt a version safely.

- **Human upgraders over raw commit logs.** Never dump `git log` subjects (`fix lint`, `refactor worker`). Describe observable user, API, or operator outcomes instead of internal file moves.
- **Breaking changes and migration path first.** Surface incompatible flag, schema, or API changes at the top with exact before-and-after upgrade commands.
- **Keep-a-Changelog buckets and ISO dates.** Group entries under `Added`, `Changed`, `Deprecated`, `Removed`, `Fixed`, and `Security` beneath `YYYY-MM-DD` version headings.
