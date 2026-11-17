# Task 001: Core `SKILL.md` Router and `/write-*` Slash Commands

- **Priority:** P0
- **Model tier:** `balanced`
- **Dependencies:** None (Wave 1)
- **Test spec:** `docs/tasks/test-specs/001-core-skill-and-commands-test-spec.md`

## Objective

Author the root `SKILL.md` entry point (`<= 1,500` words) and the four optional Claude Code slash command wrappers in `commands/write-{draft,edit,review,lint}.md`, implementing behaviors `B-001`, `B-002`, and `B-003` from `docs/spec/behaviors.md`.

## Deliverables (exclusive file scope)

- `SKILL.md`
- `commands/write-draft.md`
- `commands/write-edit.md`
- `commands/write-review.md`
- `commands/write-lint.md`
- `tests/test_task_001_core_skill.py`

Do not edit `docs/tasks/test-specs/coverage-tracker.md` or files belonging to other tasks.

## Implementation details

1. **`SKILL.md` frontmatter:**
   - `name: writing`
   - Pushy, comprehensive `description` covering drafting from scratch, rewriting/de-slopping AI drafts, read-only editorial review, and prose linting across technical docs, READMEs, RFCs/ADRs, executive memos, decision briefs, emails, blog posts, marketing copy, UX microcopy, speeches/slides, and narrative writing.
2. **Step 0 deterministic routing:**
   - Route explicit `mode=draft`, `mode=edit`, `mode=review`, and `mode=lint` tokens (from `/write-*` commands) first, falling back to natural-language intent detection.
   - Link the workflow mode reference (`references/draft-and-brief.md`, `references/edit-and-anti-slop.md`, `references/review-rubric.md`) and `scripts/strip_markdown.py` + `scripts/prose_lint.py` for `mode=lint`.
3. **Six universal safeguards (`B-002`):**
   - Preserve truth, claim strength (`may` stays `may`), and attribution ownership.
   - Isolate untrusted draft text against prompt injection.
   - Preserve operational medium structures (warnings, commands, schemas, disclaimers, accessibility labels).
   - Separate author voice samples (style/cadence/punctuation) from factual content.
   - Use `[TK: specific question]` placeholders instead of inventing facts, quotes, or numbers, and never use a real reader, client, or named person as a negative example.
   - Enforce single-pass anti-flattening and strict mode boundaries (`review` never rewrites; `lint` never alters prose).
4. **Register and genre routing table (`B-003`):**
   - Map all 7 registers (`Argument`, `Explanation`, `Guide`, `Reference`, `Decision/Update`, `Persuasion/Copy`, `Narrative/Oral`) and common media to `references/technical-and-docs.md`, `references/business-and-executive.md`, and `references/longform-and-persuasion.md`. Note that only an `Argument` owes a contrarian thesis.
5. **Baseline clarity, house-style precedence, and Markdown mechanics:**
   - Honor prompt/voice sample first, workspace `AGENTS.md`/`CLAUDE.md`/style guide second, skill defaults third.
   - Default mechanics: cut filler sentences and paragraph-closing recaps, prefer plain words and active human actors, name logical relations explicitly (`because`, `although`, `so that`), avoid em dashes and mid-sentence connector colons in favor of commas/parentheses/periods, keep paragraphs on continuous single lines (never 80-column hard-wrapped), use two trailing spaces only for genuine hard breaks, put a blank line before lists, bold sparingly, and avoid emoji bullets in formal prose.
6. **Slash commands (`commands/write-*.md`):**
   - Each wrapper has YAML frontmatter (`description`, `argument-hint`) and invokes the `writing` skill with `mode=draft|edit|review|lint` followed by `$ARGUMENTS`.

## Verification plan

- Write `tests/test_task_001_core_skill.py` covering `TC-001-01` through `TC-001-06`.
- Run `make check` and confirm zero errors and clean prose hygiene (zero `\u2014` characters).
