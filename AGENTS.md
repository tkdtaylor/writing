# writing: Agent Briefing (Canonical)

This is the **canonical, harness-neutral briefing** for the `writing` repository. Every coding-agent harness loads this file:

- **Codex** auto-loads `AGENTS.md` (this file).
- **Antigravity / Gemini** load it via `GEMINI.md` (a relative symlink to this file).
- **Claude Code** loads `CLAUDE.md`, which imports `@AGENTS.md` and adds Claude-specific subagents, hooks, and slash commands.

Keep this file harness-neutral. Put harness-specific mechanics in `CLAUDE.md` or `.agents/`.

## What this is

`writing` is an open-source, cross-harness **LLM writing skill** for drafting, editing, reviewing, and linting any kind of prose produced with a language model. It combines substance-first editorial principles and provenance safeguards (inspired by `addyosmani/clarity`) with structural clarity, Diataxis mode discipline, narrative decision memos, and anti-slop rules (inspired by `cursor/plugins/pstack`). A token-budgeted mode and genre router keeps runtime context lean.

The product is `SKILL.md`, `commands/write-*.md`, `references/*.md`, zero-dependency Python 3 diagnostic tools in `scripts/`, evaluation benchmarks in `evals/`, and before/after calibration pairs in `samples/`.

## Project structure

```text
SKILL.md                     <- skill entry point (<1,500 words): mode + genre router & 6 safeguards
commands/                    <- optional Claude Code slash commands (/write-draft, /write-edit, /write-review, /write-lint)
references/                  <- on-demand workflow & genre guides (<1,500 words each)
  draft-and-brief.md           co-writing, goal restatement, perspective interview, [TK] markers, provenance
  edit-and-anti-slop.md        3-way edit triage, Leave-it-alone rule, declined-claim unlocks, single-pass anti-slop
  review-rubric.md             read-only critique schema (keep / revise / ask-author / cut), zero-context cold-reader pass
  technical-and-docs.md        Diataxis, STE, Global English, READMEs, RFCs, blameless postmortems, Keep-a-Changelog release notes
  business-and-executive.md    BLUF memos, decision briefs, metric vetting, 3P updates, thread reply discipline
  one-pager-and-six-pager.md   door-type matrix, 5-part one-pagers, 7-part six-pagers, PR/FAQs, appendix contract
  longform-and-persuasion.md   essays, VoC landing copy, claim unlocks, UX microcopy, speeches/slides, narrative
scripts/                     <- zero-dep Python 3 CLIs + repo workflow scripts
  strip_markdown.py            strips Markdown/code/tables/frontmatter to clean reader-visible prose
  prose_lint.py                stylometric, flourish, dash-bypass, chatbot_artifacts & meta_and_strawman_tells diagnostics
  validate_skill.py            enforces word budgets (<=1,500/file, <=10,000 combined), routing, links, and hygiene
  package_skill.py             verifies, archives (dist/), and cleanly installs the runtime skill payload
  start-task.sh / finish-task.sh / check-task-state.sh / verify-worktree-isolation.sh
  check-mermaid.py / sync-agy-skills.py
evals/                       <- JUDGE.md blinded rubric + evals.json + trigger-evals.json
samples/                     <- committed before/after calibration pairs (technical-doc, executive-memo, one-pager)
tests/                       <- Python unittest suite verifying scripts, skill budgets, and task specs
docs/                        <- spec + architecture + roadmap + task backlog (input side)
  spec/                        authoritative current-state snapshot (7 files)
  architecture/                overview.md, C4 diagrams.md, tech-stack.md, decisions/ (ADRs)
  plans/                       roadmap.md, sprints/
  tasks/                       backlog/, active/, completed/, test-specs/coverage-tracker.md
  agent-rules.md               failure-mode retrospectives
training/                    <- (gitignored) raw user samples awaiting distillation
```

## Tech stack

| Layer | Choice |
|-------|--------|
| Skill and reference files | Markdown (GitHub-flavored, continuous-line paragraphs) |
| Diagnostic and validation scripts | Python 3.10+ standard library only (zero third-party runtime dependencies) |
| Test runner | `python3 -m unittest` via `make test` |
| Architectural invariants | `make fitness` (`F-001`..`F-007` across task state, Mermaid, Antigravity sync, skill package, prose hygiene, samples, and clean packaging) |

## Commands

```bash
make lint                                     # syntax-check all Python scripts and tests
make test                                     # run full unittest suite
make package                                  # build deterministic writing-skill.tar.gz and writing.skill in dist/
make fitness                                  # run executable architectural fitness checks (F-001..F-007)
make check                                    # run lint + test + fitness

python3 scripts/prose_lint.py README.md       # run prose diagnostics on a file
python3 scripts/prose_lint.py --profile technical samples/technical-doc.after.md
python3 scripts/prose_lint.py --mode one-pager samples/one-pager.after.md
python3 scripts/validate_skill.py             # validate skill word budgets, links, and prose hygiene
python3 scripts/package_skill.py --check      # verify clean runtime payload purity in a staged directory
python3 scripts/package_skill.py --install-to <dir>  # install only the runtime skill payload cleanly
python3 scripts/sync-agy-skills.py            # regenerate .agents/ adapters after .claude/ changes
```

Note that `prose_lint.py --profile` (alias `--mode`) supports `default`, `technical`, `memo`, `one-pager`, `six-pager`, and `narrative`. It also flags spaced `--` or en-dash (`U+2013`) dash-bypass substitutes, `chatbot_artifacts`, and `meta_and_strawman_tells` without emitting a composite AI score.

## Conventions and house prose rules

Every prose file in this repository is a live demonstration of the skill's standards:

- **No em dashes in prose.** Use a comma, colon, parentheses, or a separate sentence. Do not use em dashes in headings, commit subjects, or table cells either (use `-` or `N/A`).
- **Continuous single-line paragraphs.** Never hard-wrap prose paragraphs at 80 characters with embedded newlines. Use two trailing spaces only for genuine hard line breaks.
- **List spacing.** Always put a blank line between an intro sentence or bold heading and the first `- ` or `1. ` list item.
- **Plain vocabulary.** Prefer plain words (`use`, `help`, `to`) over inflated AI-tell words, and avoid emoji bullets in formal documents. Never use a real client or reader name as a negative example.
- **Token discipline.** Keep `SKILL.md` under 1,500 words, each file in `references/` under 1,500 words, and the combined runtime package at or under 10,000 words.
- **Test-spec-first.** Every task `docs/tasks/backlog/NNN-slug.md` requires a paired `docs/tasks/test-specs/NNN-slug-test-spec.md` with `TC-NNN-XX` markers verified by tests in `tests/`.
- **Keep spec in sync.** Update `docs/spec/` in the same commit whenever externally visible skill routes, scripts, schemas, or fitness gates change.

## Working in this project

1. Read the task file and its paired test spec in `docs/tasks/test-specs/`.
2. Isolate work with `scripts/start-task.sh <NNN> <slug>`. If it outputs `WORKTREE <path>`, run every command inside `<path>`.
3. Implement tests and deliverables until `make check` passes cleanly and every `TC-NNN-XX` marker appears in `tests/`.
4. Move the task file from `backlog/` (or `active/`) to `completed/` with `git mv`.
5. Run `spec-verifier` before promoting `docs/tasks/test-specs/coverage-tracker.md` to verified status, then close the branch and worktree via `scripts/finish-task.sh <NNN> <slug>`.

## Commit rules

- Commit after every logical milestone using conventional prefixes (`feat:`, `fix:`, `docs:`, `test:`, `chore:`, `verify:`, `merge:`) with ASCII hyphens (`-`), never em dashes.
- Never commit directly to `main` once task branches exist unless making a standalone doc or tracker commit tagged `[allow-main]`.
- Never run `git commit --no-verify` or `git checkout -- <path>` over uncommitted changes.
- Do not add `Co-Authored-By` trailers unless explicitly asked.

## Boundaries

### Always

- Keep runtime scripts strictly standard-library Python 3 so the skill installs via clean archive extraction or `package_skill.py --install-to` with zero `pip install` step.
- Keep `.gitattributes` `export-ignore` synchronized so maintainer folders (`.agents/`, `.claude/`, `docs/`, `tests/`, `evals/`, `samples/`) never leak into end-user skill installations.
- Verify `make check` passes and `git status` is clean before declaring any task finished.
- Keep `SKILL.md` routing tables, `commands/write-*.md`, `docs/spec/`, and `README.md` synchronized.

### Ask first

- Adding third-party dependencies or changing repository directory layout.
- Force-pushing, creating external remotes, or modifying `.claude/skill-manifest.json` format.

### Never

- Invent facts, quotes, citations, benchmarks, or anecdotes in skill outputs or samples.
- Emit a single composite "AI detection score" from `prose_lint.py`.
- Edit `.claude/settings.local.json` or commit files inside `training/`.
