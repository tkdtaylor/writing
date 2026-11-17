# Task 002: Workflow Mode References (`draft`, `edit`, `review`)

- **Priority:** P0
- **Model tier:** `balanced`
- **Dependencies:** None (Wave 1)
- **Test spec:** `docs/tasks/test-specs/002-workflow-mode-references-test-spec.md`

## Objective

Author the three workflow mode reference guides (`<= 1,500` words each) under `references/`, implementing behaviors `B-004`, `B-005`, and `B-006` from `docs/spec/behaviors.md`.

## Deliverables (exclusive file scope)

- `references/draft-and-brief.md`
- `references/edit-and-anti-slop.md`
- `references/review-rubric.md`
- `tests/test_task_002_workflow_refs.py`

Do not edit `docs/tasks/test-specs/coverage-tracker.md` or files belonging to other tasks.

## Implementation details

1. **`references/draft-and-brief.md` (`mode=draft`):**
   - **Goal and reader restatement:** State the specific pictured reader, the job the piece performs for them, and the core claim or outcome in 2 to 3 plain sentences before drafting long pieces.
   - **Primary-source brief deepening:** Prefer raw primary inputs (diffs, logs, transcripts, measurements, schemas, user notes) over pre-digested summaries; identify what a domain practitioner would address unasked.
   - **Targeted perspective interview:** When drafting original point-of-view prose with thin inputs, pause and ask up to 5 concrete questions (what triggered this now, who disagrees and their strongest real point, 1 to 2 real examples or numbers, honest caveats, and what standard advice to skip). Never draft generic filler while waiting.
   - **Drafting rules and provenance:** Build from the author's concrete phrases, insert `[TK: specific question]` wherever facts or metrics are missing, and emit a brief external provenance block (`Author material`, `Model contribution`, `Open [TK] items`) outside the document body.
2. **`references/edit-and-anti-slop.md` (`mode=edit`):**
   - **Pre-edit inventory:** List factual claims, causal strength (`may`, `can`, `correlates`), attributions, links, and operational elements to protect.
   - **Strict 5-step single-pass order:** (1) Truth and scope, (2) Substance and concrete mechanisms, (3) Structure and mode purity, (4) Sentences and anti-slop mechanics, (5) Craft restoration (concrete image, clear stance, varied sentence cadence, human warmth where appropriate, clean stop when the thought ends). Stop after one deliberate pass so repeated smoothing does not flatten voice.
   - **Four contextual diagnostic tests:**
     - *Importance-without-mechanism test:* Strip emphasis words; does the sentence name an actor, mechanism, number, or limit?
     - *Flatten test:* Remove rhetorical cadence (`not just X, it's Y`, triads, chiasmus); does a substantive claim remain?
     - *Relation test:* Replace dashes, mid-sentence colons, or sentence adjacency with `because`, `although`, `when`, `if`, or `so that`; if doing so invents a link, cut or clarify.
     - *Paragraph swap test:* Could this sentence appear unchanged in another project's docs or another person's post?
   - **Mechanical and lexical anti-slop catalog:** Cover em dashes and mid-sentence connector colons, bold-label restatement bullets (`**Speed:** Speed improved...`), synonym cycling ("one name per thing; repeat it"), false `from X to Y` scales, throat-clearing openers, paragraph-closing summary sentences, inflated style verbs, abstract tech buzz-nouns (`substrate`, `flywheel`, `scaffolding`, `paradigm`, `nexus`), framing/pacing theater (`here is where it gets interesting`, `the key insight`), prompt-rubric echoing, and mirror sentences. Keep examples concise and wrap literal tell words in inline code spans, avoiding any prose `\u2014` character (refer to `em dash (U+2014)` instead).
3. **`references/review-rubric.md` (`mode=review`):**
   - **Read-only contract and candor rule:** Never rewrite the document or modify files. Push back plainly when a thesis is empty, a section mixes modes, or an addition weakens reader focus.
   - **Output schema:** `Piece-level diagnosis` (`Job`, `Substance`, `Trust`, `Structure`, `Voice`, `Ending`, `Top fixes`) followed by `Passage-level findings` using four verdicts: `keep` (explicitly defending earned stylistic choices or intentional rule-breaking), `revise` (specific defect + concrete direction without rewriting the whole piece), `ask-author` (missing facts/numbers only the author knows), and `cut` (redundant or empty passage).

## Verification plan

- Write `tests/test_task_002_workflow_refs.py` covering `TC-002-01` through `TC-002-04`.
- Run `make check` and confirm all tests pass and prose hygiene holds.
