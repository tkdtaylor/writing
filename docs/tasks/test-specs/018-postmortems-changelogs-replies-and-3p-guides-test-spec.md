# Test Spec 018: Blameless Postmortems, Changelogs, 3P Updates, and Reply Discipline

- **Task:** `docs/tasks/backlog/018-postmortems-changelogs-replies-and-3p-guides.md`
- **Verification target:** L5 (`make check` + `validate_skill.py` + `prose_lint.py` zero-tell verification)

## Requirements and Test Cases

### `REQ-018-01`: Blameless incident postmortems and Keep-a-Changelog release notes in `references/technical-and-docs.md`

- **`TC-018-01`**: `references/technical-and-docs.md` adds actionable blueprints for **Blameless incident postmortems** (quantified user/SLO impact and UTC window up front, `HH:MM UTC` detection-to-mitigation timeline, explicit separation of systemic *Root cause* from proximate *Trigger*, systemic controls over human blame, and owned *Action items* with tracking tickets or `[TK: ticket ID]`) and **Changelogs and release notes** (written for human upgraders rather than raw `git log` dumps, surfacing breaking changes and migration steps first under `Added`, `Changed`, `Deprecated`, `Removed`, `Fixed`, and `Security`), while keeping `references/technical-and-docs.md` `<= 1,500` words with zero `prose_lint.py` tells or overloaded (`> 35`-word) sentences.

### `REQ-018-02`: 3P team updates and thread reply discipline in `references/business-and-executive.md`

- **`TC-018-02`**: `references/business-and-executive.md` adds **3P updates** (`Progress`, `Plans`, `Problems` naming concrete blockers, owners, and escalation asks) and **Thread and reply discipline** (leading replies in PR comments, Slack threads, and emails with the decision or answer plus the single new fact the reader lacks rather than rebuilding shared problem context and burying the call at the end), staying `<= 1,500` words with zero `prose_lint.py` tells or overloaded sentences.

### `REQ-018-03`: Voice-of-Customer phrasing, negation-list discipline, and punch rationing in `references/longform-and-persuasion.md`

- **`TC-018-03`**: `references/longform-and-persuasion.md` updates `Marketing, launch, and landing copy` with customer-language mirroring (Voice-of-Customer phrasing from tickets/interviews over internal jargon), positive workflow statements over stacked negation lists (`No X, no Y, no Z`), rationing punchy rhythmic devices to `1` to `2` moments per page, and pairing declined unverified claims with the exact proof `[TK: ...]` that would unlock them, keeping all reference budgets `<= 1,500` words and combined runtime words `<= 10,000`.
