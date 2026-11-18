# Test Spec 017: Edit Input Triage, Cold-Reader Verification, and Humanizer Anti-Slop Rules

- **Task:** `docs/tasks/backlog/017-edit-triage-cold-reader-and-humanizer-rules.md`
- **Verification target:** L5 (`make check` + `validate_skill.py` + `prose_lint.py` zero-tell verification)

## Requirements and Test Cases

### `REQ-017-01`: `SKILL.md` triggers, 3-way edit triage, cold-reader review hook, and dash-bypass mechanics

- **`TC-017-01`**: `SKILL.md` frontmatter `description` includes `postmortems` and `release notes` while preserving `Don't use for...` negative triggers; `mode=edit` references 3-way input triage (`slop/notes`, `real voice`, `point edit`); `mode=review` notes optional zero-context cold-reader verification for high-stakes docs; Step 3 notes sentence-case headings and bans spaced double-hyphen (` -- `) or spaced en-dash (`U+2013`) em-dash substitutes; and `SKILL.md` stays `<= 1,500` words with zero `prose_lint.py` tell or overloaded-sentence hits.

### `REQ-017-02`: `references/edit-and-anti-slop.md` 3-way triage, Leave-It-Alone test, claim unlocks, and `WP:AI` catalog

- **`TC-017-02`**: `references/edit-and-anti-slop.md` defines 3-way input diagnosis (`Slop or rough notes`, `Real author voice present` preserving casual lexical choices like `ship` or `stuff` and locking working lines, and `Point edit`), the `Leave-it-alone` test (reverting edits that are merely different rather than clearer), the `Declined claims name their unlock` rule in Step 1 (`Truth and scope`), and inline-code-wrapped Section 4 catalog entries for spaced dash substitutes (`--` / en-dash), chatbot residue and cutoff disclaimers, meta-document narration and echoed headings, stock `Despite these challenges` closers, phantom strawmen (`arguing with no one`), and stacked negation lists (`No X, no Y, no Z`), staying `<= 1,500` words with zero `prose_lint.py` tells.

### `REQ-017-03`: `references/review-rubric.md` zero-context Cold-Reader pass (`doc-coauthoring` Stage 3)

- **`TC-017-03`**: `references/review-rubric.md` defines a zero-context `Cold-reader pass` section for high-stakes specs, RFCs, Six-Pagers, and onboarding docs (testing standalone comprehension via `3` to `5` realistic reader questions plus unstated assumptions, ambiguities, and contradictions in a fresh subagent or prompt without conversation history), staying `<= 1,500` words and keeping combined runtime words `<= 10,000` with zero `prose_lint.py` tells.
