# Test Spec 002: Workflow Mode References

- **Task:** `docs/tasks/backlog/002-workflow-mode-references.md`
- **Test file:** `tests/test_task_002_workflow_refs.py`

## Requirements

- **REQ-002-01:** `references/draft-and-brief.md` exists (`<= 1500` words) and covers goal/reader restatement, primary-source brief deepening, targeted perspective interviews (capped at `<= 5` questions), `[TK: ...]` placeholders, and external provenance notes (`Author material`, `Model contribution`, `Open [TK] items`).
- **REQ-002-02:** `references/edit-and-anti-slop.md` exists (`<= 1500` words) and covers the 5-step single-pass edit order (`Truth and scope`, `Substance`, `Structure`, `Sentences`, `Craft restoration`), the 4 contextual diagnostic tests (`Importance-without-mechanism`, `Flatten`, `Relation`, `Paragraph swap`), and structural/lexical anti-slop rules (em dashes, mid-sentence connector colons, bold-label restatements, synonym cycling, false `from X to Y` scales, inflated style verbs, tech buzz-nouns, framing theater, mirror sentences).
- **REQ-002-03:** `references/review-rubric.md` exists (`<= 1500` words) and enforces read-only review behavior, candor over sycophancy, `Piece-level diagnosis` (`Job`, `Substance`, `Trust`, `Structure`, `Voice`, `Ending`, `Top fixes`), and `Passage-level findings` with all 4 verdicts (`keep`, `revise`, `ask-author`, `cut`).
- **REQ-002-04:** All three workflow reference files obey prose hygiene: zero `\u2014` characters in prose, zero emoji bullets, and zero hard-wrapped multi-line prose paragraphs.

## Test Cases

| ID | Requirement | Input / Target | Expected Assertion |
|----|-------------|----------------|--------------------|
| `TC-002-01` | `REQ-002-01` | `references/draft-and-brief.md` | Exists, `350 <= word_count <= 1500`, documents restatement, primary sources, perspective interview, `[TK`, and provenance sections |
| `TC-002-02` | `REQ-002-02` | `references/edit-and-anti-slop.md` | Exists, `450 <= word_count <= 1500`, documents 5-step pass, all 4 diagnostic tests, connector colons, synonym cycling, false scales, and single-pass stop rule |
| `TC-002-03` | `REQ-002-03` | `references/review-rubric.md` | Exists, `300 <= word_count <= 1500`, enforces read-only constraint, candor rule, piece-level fields, and `keep` / `revise` / `ask-author` / `cut` verdicts |
| `TC-002-04` | `REQ-002-04` | All 3 workflow reference files | Zero `\u2014` characters outside fenced code blocks, zero emoji bullets, and paragraphs are continuous lines |
