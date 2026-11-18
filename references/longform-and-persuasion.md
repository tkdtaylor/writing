# Longform, persuasion, and narrative guide

Use this guide for prose in the `Argument`, `Persuasion/Copy`, `Narrative/Oral`, or public `Explanation` registers. It governs essays, blog posts, newsletters, marketing and landing copy, UX microcopy, speeches, slide decks, progressive diagrams, and creative narrative.

## Essays, blog posts, and newsletters

Readers grant an essay thirty seconds to prove a real mind is thinking on the page. Earn attention through tension, honest argument, and momentum rather than templates.

- **Sentence one has one job.** Make the reader read sentence two by opening on a specific friction, anomaly, scene, or sharp claim. Never open with a dictionary definition (`Observability is the practice of...`), an intent announcement (`In this post, I will examine...`), or historical throat-clearing.
- **Thesis discipline by register.** Only an `Argument` owes a contrarian or disputable thesis a thoughtful peer could reject. Field notes, retrospectives, and explanatory essays need a genuine question or hard-won observation, not manufactured controversy.
- **Cover-the-page transition test.** Each paragraph must earn the next. Cover paragraph `N` except its last sentence and paragraph `N+1`'s first sentence, and check that the pull holds. If paragraphs swap order without damage, you have a list disguised as an essay.
- **Steelman the strongest real objection.** Dedicate at least one fair paragraph to the sharpest counterargument a smart skeptic would make. State where it holds true before explaining why your conclusion still stands within scope.
- **Stop where the thought ends.** Delete the victory-lap closing paragraph repeating earlier headings (`By combining X, Y, and Z...`). End on a concrete implication, lingering image, or bounded open question.

## Marketing, launch, and landing copy

Persuasive copy converts skeptical readers by naming their actual problem and proving how the product resolves it, never by piling up adjectives. Follow a four-part spine:

1. **Specific reader problem or job-to-be-done.** Lead with the workflow pain, risk, or wasted hour the buyer recognizes (`Stop reconciling failed Stripe payouts against spreadsheets every Friday`), never vague slogans (`Reimagining modern revenue operations`).
2. **Concrete mechanism or before/after workflow.** Show *how* the product works via specific inputs, steps, and outputs, or a before-and-after contrast. Cut empty superlatives (`world-class`, `revolutionary`, `next-generation`, `effortless`).
3. **Checkable proof.** Back promises with reproducible benchmarks, named workflows, live sandboxes, audits, or candid limits (`Built for Postgres 14+; MySQL ships in Q4`), never invented quotes or unanchored percentages.
4. **One proportionate call to action (`CTA`).** Close with one primary action matched to trust stage (`Try the 90-second sandbox` for cold visitors; `Book a migration review` for enterprise buyers).

Pair that spine with three copywriting guardrails:

- **Voice-of-Customer (`VoC`) language over internal jargon.** Mirror exact buyer phrases from support tickets, sales calls, and user interviews instead of internal engineering terms or invented category labels.
- **Positive workflow statements and punch rationing.** State what happens in the workflow instead of stacked negation lists (`No setup call, no templates, no spreadsheets`). Ration punchy fragments or triads to `1` to `2` moments per page so stacked tricks never read as synthetic.
- **Proof tags (`claim-unlock`) over silent cuts.** When proof cannot back an ambitious claim, draft the closest verifiable statement and name the exact evidence (`[TK: 90-day cohort export]`) needed to `unlock` the stronger version.

## UX microcopy

Interface text is operational tooling read mid-task under time pressure, so clarity and recoverability beat cleverness.

- **Error messages (`Failed action + User-terms cause + Exact recovery`).** State what failed, why in user-controlled terms, and how to recover (`Could not upload tax form because the PDF exceeds 25 MB. Export a smaller PDF or upload PNG pages`), never stack traces or blame.
- **Buttons and destructive modals (`Verb + Noun`).** Label controls with the action and target (`Revoke API key`, `Delete 3 webhooks`, `Keep draft`), never ambiguous `OK`, `Yes`, `No`, or `Submit` dialog buttons.
- **Actionable empty states.** State what belongs in the empty view, why it helps, and give one primary action (`No alert rules yet. Add a rule to page on-call engineers on error spikes. [Create alert rule]`).

## Speeches, slides, and progressive visuals

Live audiences cannot re-read dense prose or decode a twelve-box chart. Design spoken words and visuals as complementary channels.

- **Oral prose for breath and ear.** Write scripts for spoken breath using shorter clauses, contractions, callbacks, and signposts (`Here is the catch`, `Compare those two numbers`). Read aloud and split any sentence that leaves you breathless.
- **One point per slide.** Give each slide one assertive title takeaway (`Idempotent retries cut duplicate support tickets by 64%`), never a dead topic label (`Support Ticket Metrics`), and never read slides verbatim aloud.
- **Diagram budgets and reader vocabulary.** Cap diagrams at `<= 6` boxes (`6` nodes max) and `<= 8` words per box (`8` words max). Name boxes in reader concepts (`Order ledger`, `Card network`), never internal IDs (`tx_outbox_v3`), and avoid duplicating prose facts verbatim.
- **Progressive diagram build-up (`3+` components).** Build systems with `3` or more components across stages rather than dropping the full chart at once. Start with a two-box baseline and add **one new component per step**.

## Creative and narrative prose

Narrative prose earns emotion through perception and rhythm rather than explanation, and editing it requires protecting craft from sterile smoothing.

- **Scene and sensory detail over named emotion.** Render turning points through action, setting, dialogue, and sensory detail rather than naming feelings. Write `She wiped condensation off the gauge and tapped the glass twice; the needle stayed at zero`, not `She felt growing dread`. Use compressed summary to bridge routine time.
- **Protect intentional rhythm and earned voice.** Never flatten purposeful sentence fragments, colloquial dialogue, rhythmic repetition, polysyndeton, or fresh metaphors. Cut worn clichés and mixed images while defending authorial cadence.
