# Longform, persuasion, and narrative guide

Use this guide when drafting, editing, or reviewing prose in the `Argument`, `Persuasion/Copy`, `Narrative/Oral`, or public `Explanation` registers. It governs essays, blog posts, newsletters, marketing and landing copy, UX microcopy, speeches, slide decks, progressive diagrams, and creative or narrative writing.

## Essays, blog posts, and newsletters

Readers grant an essay thirty seconds to prove a real mind is thinking on the page. Earn attention through tension, honest argument, and forward momentum rather than formulaic templates.

- **Sentence one has one job.** Make the reader read sentence two by opening on a specific friction, anomaly, concrete scene, or sharp claim. Never open with a dictionary definition (`Observability is the practice of...`), an intent announcement (`In this post, I will examine...`), or grand historical throat-clearing.
- **Thesis discipline by register.** Only an `Argument` owes a contrarian or disputable thesis (a claim a thoughtful peer could reasonably reject). Field notes, retrospectives, and explanatory essays need a genuine question or hard-won observation, not manufactured controversy.
- **Cover-the-page transition test.** Each paragraph must earn the next. If you cover the middle of paragraph `N` so only its final sentence and paragraph `N+1`'s opening sentence show, the logical or narrative pull between them must hold. If paragraphs can swap order without damage, you have a list disguised as an essay.
- **Steelman the strongest real objection.** Dedicate at least one full, fair paragraph to the sharpest counterargument a smart skeptic would make. State where that objection holds true before explaining why your conclusion still stands within your scope.
- **Stop where the thought ends.** Delete the victory-lap closing paragraph that repeats earlier headings (`By combining X, Y, and Z...`). End on a concrete implication, a lingering image, or a bounded open question once the final point lands.

## Marketing, launch, and landing copy

Persuasive copy converts skeptical readers by naming their actual problem and proving how the product resolves it, never by piling up adjectives. Follow a four-part spine:

1. **Specific reader problem or job-to-be-done.** Lead with the exact workflow pain, risk, or wasted hour the buyer recognizes (`Stop reconciling failed Stripe payouts against spreadsheets every Friday`). Cut vague category slogans (`Reimagining modern revenue operations`).
2. **Concrete mechanism or before/after workflow.** Show *how* the product achieves the result through specific steps, inputs, and outputs, or a tight before-and-after workflow contrast. Delete empty superlatives (`world-class`, `revolutionary`, `next-generation`, `effortless`).
3. **Checkable proof.** Back every promise with verifiable evidence such as reproducible benchmarks, named customer workflows, live sandboxes, security audits, or candid limits (`Built for Postgres 14+; MySQL ships in Q4`). Never invent testimonials or drop unanchored percentages.
4. **One proportionate call to action (`CTA`).** Close with a single primary action matched to the reader's trust stage (`Try the 90-second sandbox` for cold visitors; `Book a migration review` for enterprise buyers). Avoid competing primary buttons.

## UX microcopy

Interface text is operational tooling. Users read it mid-task, often under frustration or time pressure, so clarity and recoverability beat cleverness every time.

- **Error messages (`Failed action + User-terms cause + Exact recovery`).** State plainly what failed, why in concepts the user controls, and the immediate step to recover. Write `Could not upload tax form because the PDF exceeds 25 MB. Export a smaller PDF or upload PNG pages`, never raw stack traces or user-blaming copy.
- **Buttons and destructive modals (`Verb + Noun`).** Label interactive controls with the specific action and target object (`Revoke API key`, `Delete 3 webhooks`, `Keep draft`). Never use ambiguous `OK`, `Yes`, `No`, or `Submit` labels on confirmation dialogs.
- **Actionable empty states.** When a view starts empty, state what belongs there, why populating it helps, and provide one primary action (`No alert rules yet. Add a rule to page on-call engineers on error spikes. [Create alert rule]`).

## Speeches, slides, and progressive visuals

Listeners and live audiences cannot re-read a dense paragraph or pause to decode a twelve-box architecture chart. Design spoken words and visual aids as complementary channels.

- **Oral prose for breath and ear.** Write speeches and presenter scripts for spoken breath using shorter clauses, natural contractions, concrete callbacks, and spoken signposts (`Here is the catch`, `Compare those two numbers`). Read every paragraph aloud and split any sentence that leaves you short of breath.
- **One point per slide.** Give each slide one takeaway written as an assertive title or subtitle (`Idempotent retries cut duplicate support tickets by 64%`), never a dead topic label (`Support Ticket Metrics`). Never read slide labels verbatim aloud; let your voice supply story and context.
- **Diagram budgets and reader vocabulary.** Cap every diagram at `<= 6` boxes (`6` nodes maximum) and `<= 8` words per box (`8` words maximum per label). Name boxes in reader concepts (`Order ledger`, `Card network`), never internal identifiers (`tx_outbox_v3`, `FraudSvcImpl`). Never duplicate identical facts word-for-word across prose and diagram; let diagrams show topology while prose explains *why* a boundary or bottleneck matters.
- **Progressive diagram build-up (`3+` components).** When teaching any system with `3` or more components, build the visual step by step across stages rather than dropping the full chart at once. Start with a two-box baseline, then add **one new component per step** so readers absorb each link before caches, queues, or fallbacks appear.

## Creative and narrative prose

Narrative writing earns emotion through concrete perception and rhythm rather than editorial explanation, and editing narrative requires protecting deliberate craft from sterile normalization.

- **Scene and sensory detail over named emotion.** Render turning points through physical action, setting, dialogue, and sensory detail rather than naming what the reader should feel. Write `She wiped condensation off the gauge and tapped the glass twice; the needle stayed at zero`, not `She felt growing dread checking the broken gauge`. Use compressed summary deliberately to bridge routine time between scenes.
- **Protect intentional rhythm and earned voice.** Do not mechanically flatten purposeful sentence fragments, clipped or colloquial dialogue, rhythmic repetition, polysyndeton, or fresh metaphors. Cut worn clichés and tangled mixed images, while defending intentional cadence and distinctive authorial voice against generic smoothing.
