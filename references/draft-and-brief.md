# Workflow Reference: Draft and Brief (`mode=draft`)

Use this reference when authoring new prose from scratch, rough notes, outlines, diffs, logs, or transcripts. Apply the six universal safeguards in `SKILL.md` first. Pair this workflow with the matching genre reference (`references/technical-and-docs.md`, `references/business-and-executive.md`, `references/one-pager-and-six-pager.md`, or `references/longform-and-persuasion.md`).

## 1. Goal and reader restatement

Before drafting any multi-paragraph or high-stakes piece, align on the brief in 2 to 3 plain sentences covering three concrete points:

- **Pictured reader.** Name a specific role and situation rather than a demographic label. Prefer "an on-call backend engineer diagnosing a webhook signature failure at 2 a.m." or "a VP of Infrastructure deciding whether to fund a queue migration before Q4 freeze" over "developers" or "leadership."
- **Job-to-be-done.** State the exact action, decision, or mental model the reader walks away with after finishing the piece.
- **Core claim or outcome.** State the central decision call, task outcome, or thesis in plain language. Only an `Argument` register piece owes a debatable or contrarian thesis; `Guide`, `Reference`, and `Explanation` pieces owe task completion, exact lookup accuracy, or causal clarity instead.

For short transactional outputs where context is already complete (such as a two-sentence status reply or a single UI error message), hold these three points silently rather than printing preamble ahead of a tiny deliverable.

## 2. Primary-source brief deepening

Generic AI prose usually starts upstream when a model expands thin summary bullets into plausible-sounding filler. Whenever primary artifacts exist, read or request them before drafting:

- **Engineering and technical inputs.** Git diffs, pull requests, commit messages, schemas, CLI `--help` output, configuration files, incident timelines, and test assertions.
- **Quantitative inputs.** Raw metric tables, latency percentiles (`p50`, `p95`, `p99`), sample sizes, measurement windows, baseline comparisons, and cost breakdowns.
- **Human and operational inputs.** Customer tickets, interview transcripts, rough author voice notes, postmortem logs, and exact user phrasing.

Scan primary material for **practitioner blind spots** by asking what an experienced domain practitioner would question immediately without prompting. Look for failure modes, rollback paths, operational limits, migration toil, data-loss risks, cost ceilings, and ownership boundaries. Address those realities directly in the draft or mark them as explicit `[TK: ...]` questions instead of papering over gaps with smooth abstractions.

## 3. Targeted perspective interview (`<= 5` questions)

When asked to write original point-of-view prose (such as an essay, strategy memo, RFC argument, postmortem reflection, or keynote) and the prompt lacks concrete substance or stance, **pause before drafting**. Ask **up to 5 concrete questions** in a single turn rather than launching an open-ended interview or generating a bland placeholder draft.

Choose only the questions still unanswered from these five angles:

1. **Trigger.** What specific event, failure, measurement, or disagreement made this worth writing right now?
2. **Strongest counterargument.** Who smart and reasonable disagrees with you on this, and what is their strongest real point?
3. **Concrete proof.** What 1 to 2 real examples, incidents, code changes, or hard numbers anchor your argument?
4. **Honest caveats.** Where does your recommendation break down, cost too much, or stop applying?
5. **Skipped clichés.** What standard advice on this topic should we skip because your reader already knows it or you think it fails in practice?

**Hard stop against filler.** Never draft generic filler paragraphs while waiting for answers, and never invent personal anecdotes, war stories, client names, quotes, or benchmark figures to make a thin prompt look complete. If the author explicitly requests an immediate rough structure before answering questions, draft a tight skeleton strictly from supplied facts and place `[TK: ...]` markers wherever author substance belongs.

## 4. Co-writing rules and `[TK: ...]` placeholders

Once source material and perspective are clear, build the draft with these guardrails:

- **Start from the author's concrete phrases.** Preserve vivid rough notes, domain nouns, and exact causal observations from the author's input instead of translating them into sterile corporate phrasing.
- **Respect the voice sample boundary.** When an author supplies past writing as a voice reference, match sentence cadence, paragraph rhythm, formality, contraction rate, and punctuation habits. Import zero facts, names, dates, or events from that sample.
- **Insert `[TK: specific question]` over fabrication.** When a metric, baseline, date, owner, command flag, citation, or quote is missing, place an inline `[TK: specific question]` marker at the point of need (such as `[TK: insert p95 latency and sample size]`). Avoid vague markers like `[TBD]` that hide what needs checking.
- **Use neutral negative examples.** When illustrating an error, anti-pattern, or bad workflow, use neutral fictionalized entities (`example-corp`, "a billing worker," "a team shipping weekly releases"). Never cast a real client, colleague, reader, or named individual as a negative example.
- **Write clean structure on the first pass.** Lead sections with the point or action, keep one governing idea per paragraph, name actors and causal links (`because`, `although`, `when`, `if`, `so that`), and repeat one consistent noun per concept. Keep each paragraph on one continuous line unless a configured target-repository formatter (`mdformat`, `prettier --prose-wrap always`, `.editorconfig`, or `markdownlint`) takes precedence on line wrapping. Put a blank line before lists, avoid em dashes (`U+2014`) and mid-sentence connector colons, and stop cleanly once the final point lands.

## 5. External provenance note

When delivering a substantive draft, append a short **Provenance** note **outside** the document body (separated clearly below the draft so the author can copy the deliverable cleanly without leftover metadata). Always separate provenance into three exact labels:

- `Author material`: Concrete claims, phrases, examples, measurements, diffs, or decisions drawn directly from the author's inputs.
- `Model contribution`: Structural ordering, section framing, transitions, genre conventions, or explanatory synthesis added during drafting.
- `Open [TK] items`: Every unresolved `[TK: ...]` placeholder in the draft that the author must verify, fill in, or cut before publishing.
