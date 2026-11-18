# Technical and documentation guide

Use this guide when drafting, editing, or reviewing technical prose in the `Guide`, `Reference`, `Explanation`, or technical `Argument` registers. It governs tutorials, how-to guides, reference manuals, architecture explanations, `README` files, `RFC` and `ADR` proposals, and pull request or change briefings.

## Layer 1: Diataxis mode purity

Technical docs fail most often when they mix reader jobs on the same page. Separate documentation into four Diataxis modes and keep one mode per document or per clearly demarcated section. When a procedure starts lecturing on design history, or a reference table buries a ten-step walkthrough, split the content and link across pages instead of blending modes.

| Mode | Reader posture | Primary job | Rules that keep the mode pure |
|------|----------------|-------------|-------------------------------|
| `Tutorial` | Learning by doing | Build confidence in a newcomer through a safe, repeatable lesson | Deliver a visible result after every step, choose one fixed path, and leave out theory or edge-case branches |
| `How-to` | Working to finish a task | Guide a competent user through a concrete real-world goal | Start from the goal, handle practical conditions, and skip beginner explanations of basic tools |
| `Reference` | Looking up exact facts | Describe machinery accurately so structure mirrors the artifact | State exact signatures, flags, types, defaults, limits, and errors in dry, neutral prose |
| `Explanation` | Seeking deeper context | Clarify architecture, background, constraints, and tradeoffs | Put opinion, historical rationale, and design comparisons here only, never inside step-by-step procedures |

## Layer 2: Developer style

Write for working engineers who scan headings and code blocks first, then read surrounding prose only when a command or boundary needs context.

- **Direct address and active present tense.** Address the reader as `you` (`Run the migration`, `The broker acks the batch`) rather than passive third-person indirection (`Batches are acknowledged`).
- **Conditions before instructions.** Put the `if` or `when` clause first so readers skip irrelevant commands immediately. Write `If your cluster runs Kubernetes 1.29 or earlier, pass --legacy-auth`, never the reverse.
- **Common path first.** Lead with the default production workflow. Move rare flags, legacy workarounds, and troubleshooting to dedicated subsections below the main path.
- **Zero minimizing or polite filler.** Cut `simply`, `easily`, `just`, `obviously`, and `please` from procedures. Nothing feels simple to an operator debugging an outage at 03:00.
- **Descriptive link text.** Name the destination explicitly (`see the OAuth token schema`, never `click here`, `this page`, or bare URLs in running sentences).
- **Sentence-case headings with a point.** Write headings in sentence case that name the action or takeaway (`Verify webhook signatures`, not `Webhook Signature Verification Overview`).
- **List discipline.** Use numbered lists (`1.`, `2.`) only when step order matters. Use unordered bullets (`-`) for non-sequential options, prerequisites, and parameter notes.

## Layer 3: ASD-STE100 procedural clarity

Apply Simplified Technical English (`ASD-STE100`) discipline whenever instructions alter state, configuration, or production traffic.

- **One instruction per sentence.** Give a single action per numbered step unless two actions must happen at the exact same moment.
- **Twenty-word procedural ceiling.** Keep every procedural step at `<= 20` words (`20` words maximum per instruction sentence). Keep surrounding explanatory sentences crisp and concrete.
- **Warnings and prerequisites before the step.** Place data-loss warnings, downtime notices, and required permissions *before* the command they guard, never beneath the code block. For example, place `Warning: Dropping this index blocks writes for 90 seconds` above the SQL command.
- **Observable verification.** Follow state-changing steps with an explicit check showing expected stdout, HTTP status, or query output so the reader confirms success immediately.
- **Strict term consistency.** Pick one noun per concept (`workspace` everywhere, never cycling across `workspace`, `project`, and `environment`) and one verb per operation.

## Layer 4: Global English disambiguation

Eliminate syntactic ambiguity so international readers and machine translators parse every rule the same way on the first read.

- **Pin limiting modifiers.** Place `only`, `not`, `at least`, and `exactly` immediately next to the word they restrict (`Run this script only on the read replica`, not `Only run this script on the read replica`).
- **Unpack dense noun strings.** Break up chains of four or more stacked nouns with prepositions (`cluster node certificate rotation interval` becomes `rotation interval for cluster node certificates`).
- **Ban bare clause-level `this` and `which`.** Never use standalone `this` (`This spikes tail latency`) or `, which` (`The queue fills up, which drops webhooks`) to refer to a whole clause. Supply an explicit noun (`This lock contention spikes tail latency`) or split into two sentences.
- **Spell out ambiguous slashes.** Replace `and/or` and overloaded `/` pairs with explicit phrasing (`A, B, or both`; `client and server timeouts`).
- **Plain international vocabulary.** Replace local idioms, sports metaphors, and Latin shorthand (`e.g.`, `i.e.`) with plain English (`for example`, `that is`).
- **Consistent dialect, exact identifiers.** Stay consistent within one English dialect (`en-US` vs `en-GB` or `en-AU` spelling, punctuation, and date conventions) across a document or repository rather than mixing dialects mid-piece. Never localize or respell literal UI labels, API field names, config keys, CLI flags, or code identifiers (for example, keep `--color` and `organization_id` exact even inside `en-GB` prose).

## Blueprint: README files

A strong `README` proves what the project does and gets a newcomer to a working result in two minutes without pretending to be the entire documentation site.

1. **Plain one-sentence opener.** State what the tool or library is, what problem it solves, and who uses it in sentence one, before badges, slogans, or origin stories.
2. **Prerequisites, install, and copy-paste quickstart.** List exact runtime versions, one verified install command, and a minimal runnable example paired with its literal expected output.
3. **Core usage.** Show the `2` to `3` everyday commands, API calls, or configuration options covering common workflows.
4. **Links out to Diataxis docs.** Point readers to separate `Tutorial`, `How-to`, `Reference`, and `Explanation` pages rather than letting the `README` grow into an unsearchable monolith.

## Blueprint: RFCs and ADRs

Design proposals (`RFC`) and Architecture Decision Records (`ADR`) exist to expose real engineering costs and operational risks before implementation begins.

1. **Concrete problem statement.** Ground the proposal in named incidents, measured latency or cost figures, failure rates, or concrete developer friction. Insert `[TK: incident or benchmark metric]` rather than inventing numbers.
2. **Explicit non-goals and constraints.** List problems this design intentionally leaves unsolved alongside hard boundaries (SLOs, compliance rules, wire compatibility, team capacity).
3. **Honest options and steelmanned objection.** Compare viable alternatives with candid engineering and operational costs, never strawmen padded to lose. Give the strongest real objection from a skeptical reviewer its own subsection and answer it directly.
4. **Recommended design.** Specify component boundaries, schemas or API contracts, state transitions, and failure recovery.
5. **Blast radius, migration, and verification.** Detail affected callers, dual-write or backfill stages, rollback triggers, and objective rollout checks. For compact `ADR` files, use `Status`, `Context`, `Decision`, `Alternatives considered`, and `Consequences`.

## Blueprint: PR and change briefings (< 40 lines)

Keep pull request descriptions and release briefings strictly under `40` lines (`< 40` lines) so reviewers absorb intent, tradeoffs, and risk on a single screen. Link long benchmark outputs, CI logs, or flamegraphs externally instead of pasting walls of text.

- **Why.** Start with the user impact, bug symptom, or system goal rather than describing code edits.
- **What changed.** Summarize behavioral and module-level changes in `2` to `4` crisp bullets without narrating line-by-line diffs.
- **Scope.** Draw a bright line between what lands in this change and what waits for a follow-up PR.
- **Tradeoffs.** Record only rejected approaches a competent reviewer would reasonably ask about, plus the concrete reason they lost.
- **Blast radius.** Identify affected endpoints, migrations, feature flags, backward-compatibility risks, and the exact rollback command.
- **Verification.** List automated tests, reproduction commands, and observed staging checks that prove the change works.
