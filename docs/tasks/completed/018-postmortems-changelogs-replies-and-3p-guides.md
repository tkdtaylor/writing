# Task 018: Blameless Postmortems, Changelogs, 3P Updates, and Reply Discipline

- **Priority:** P0
- **Model tier:** `balanced` (`inherit` / Gemini 4 Carbon High)
- **Dependencies:** None (Wave 1)
- **Test spec:** `docs/tasks/test-specs/018-postmortems-changelogs-replies-and-3p-guides-test-spec.md`

## Objective

Add concrete blueprints for blameless incident postmortems (Google SRE style) and user-facing changelogs / release notes (Keep a Changelog style) to `references/technical-and-docs.md`, add 3P updates and no-context-rebuilding thread reply rules to `references/business-and-executive.md`, and add Voice-of-Customer phrasing, stacked-negation avoidance, punch rationing, and claim-unlock rules to `references/longform-and-persuasion.md`.

## Deliverables (exclusive file scope)

- `references/technical-and-docs.md`
- `references/business-and-executive.md`
- `references/longform-and-persuasion.md`
- `tests/test_task_018_genre_expansions.py`

Do not modify files owned by Tasks 017, 019, or 020 (`SKILL.md`, `references/{edit-and-anti-slop,review-rubric,draft-and-brief,one-pager-and-six-pager}.md`, `scripts/*`, `docs/spec/*`, `evals/*`, `README.md`, `CHANGELOG.md`, or `coverage-tracker.md`).

## Implementation details

1. **`references/technical-and-docs.md` (`REQ-018-01`, currently `1,299 / 1,500` words - tighten ~30 words where redundant while preserving every existing requirement asserted in `test_task_003`, `test_task_012`, etc., and keep final word count `<= 1,470` words with every sentence `<= 35` words):**
   - Update the opening sentence on line 3 to include incident postmortems and changelogs / release notes.
   - Add `## Blueprint: Blameless incident postmortems`:
     - **Impact and UTC window up front:** Open with user-visible symptom, affected requests or revenue/SLO burn, start-to-recovery `YYYY-MM-DD HH:MM UTC` window, and severity.
     - **Root cause vs trigger:** Separate the latent systemic vulnerability (*Root cause*, such as missing connection-pool timeouts) from the proximate event (*Trigger*, such as a routine traffic spike or config deploy).
     - **UTC detection and mitigation timeline:** List timestamped `HH:MM UTC` milestones covering first symptom, alert fire, human engagement, mitigation, and full recovery.
     - **Systemic controls over human blame:** Never blame an individual operator (`engineer ran wrong command`). Ask why tooling, permissions, or canaries allowed the action to cause harm, and end with owned **Action items** (`Owner`, `Systemic fix`, and tracking ticket or `[TK: ticket ID]`).
   - Add `## Blueprint: Changelogs and release notes`:
     - **Write for human upgraders, never dump `git log`:** Describe observable user, API, or operator impact rather than internal refactors or raw commit subjects.
     - **Breaking changes and migration path first:** Put incompatible flag, schema, or API changes at the top with exact before/after upgrade commands.
     - **Standard Keep-a-Changelog buckets:** Group entries under `Added`, `Changed`, `Deprecated`, `Removed`, `Fixed`, and `Security` using ISO `YYYY-MM-DD` release dates.
2. **`references/business-and-executive.md` (`REQ-018-02`, keep `<= 1,200` words and every sentence `<= 35` words):**
   - Under `## Async updates, emails, and workplace messages`, add:
     - **3P team updates (`Progress`, `Plans`, `Problems`):** Keep recurring status updates scannable across three bullets or subheadings: shipped user-visible outcomes (`Progress`), dated next milestones (`Plans`), and concrete risks (`Problems`) naming the exact blocker, owner, and escalation ask.
     - **Thread and reply discipline (`No context-rebuilding`):** In email threads, chat replies, and PR review comments where the other person already knows the background, put the decision, answer, or proposed next step in line one plus only the single new fact or link they lack. Never restate the problem they just described or bury the answer in the final paragraph.
3. **`references/longform-and-persuasion.md` (`REQ-018-03`, keep `<= 1,180` words and every sentence `<= 35` words):**
   - Under `## Marketing, launch, and landing copy`, incorporate:
     - **Voice-of-Customer (`VoC`) language over internal jargon:** Mirror exact buyer phrases from support tickets, sales calls, and user interviews instead of internal engineering or category labels.
     - **Positive workflow statements and punch rationing:** State what actually happens instead of stacked negation lists (`` `No setup call, no templates, no spreadsheets` ``), and ration punchy fragments or triads to `1` to `2` moments per page so stacked stylistic tricks do not read as AI-generated.
     - **Claim unlocks over silent cuts:** When source proof cannot support an ambitious claim, offer the closest verifiable claim and name the exact evidence `[TK: ...]` that would unlock the stronger version.

## Verification plan

- Write `tests/test_task_018_genre_expansions.py` verifying `TC-018-01`..`TC-018-03` (including `validate_skill.validate_repo` word budgets and `prose_lint.analyze_text` zero tells + zero `overloaded_sentences` across all 3 touched files; wrap any example anti-patterns inside inline backticks `` `...` ``!).
- Move this task file to `docs/tasks/completed/018-postmortems-changelogs-replies-and-3p-guides.md` via `git mv`.
- Run `make check` and confirm exit `0`.
