@AGENTS.md

# Claude Code Layer

This file layers Claude Code mechanics on top of [AGENTS.md](AGENTS.md). Keep shared rules in `AGENTS.md`.

## Commands (host)

```bash
claude .                                      # start Claude Code in this project
```

## Subagents

Configured under `.claude/agents/` with `# model-tier:` comments mapped to `opus` (deep), `sonnet` (balanced), and `inherit` (fast):

- **task-executor** (`sonnet`, `fast` / `balanced`): executes a single backlog task in branch or worktree isolation under TDD.
- **spec-verifier** (`sonnet`, `balanced`): verifies every `TC-NNN-XX` assertion in a task's test spec before closure.
- **code-reviewer** (`sonnet`, `balanced`): multi-perspective review of scripts and Markdown changes.
- **architect** (`opus`, `deep`): design review, ADR drafting, spec drift audit, and fitness-function design.
- **security-auditor** (`opus`, `deep`): reviews CLI scripts and untrusted-draft prompt-injection boundaries.
- **docs-writer** (`inherit`, `fast`), **qa** (`sonnet`, `balanced`), **task-planner** (`sonnet`, `balanced`): optional specialist roles.

## Backlog runner commands

- `/backlog-run [--local]`: sequential supervised execution of `docs/tasks/backlog/`.
- `/backlog-run-parallel [--local]`: parallel worktree supervised execution.
- `/backlog-autopilot [--local]`: sequential autonomous execution.
- `/backlog-autopilot-parallel [--local]`: parallel worktree autonomous execution.
- `/autopilot [--local] [goal]`: plans missing tasks from `docs/plans/roadmap.md`, executes on an integration branch.

## Hook profiles

Hooks in `.claude/settings.json` are gated by `CLAUDE_HOOK_PROFILE` (`minimal`, `standard`, `strict`; default `standard`) and `CLAUDE_DISABLED_HOOKS`.

## Related projects

Read-only sibling repositories (do not modify from this repo):

- `https://github.com/tkdtaylor/create-project`: source of workflow templates, hooks, and open-source skill conventions.
- `https://github.com/tkdtaylor/dep-scan`: source of `.agents/` Antigravity adapter scripts (`sync-agy-skills.py`, `check-mermaid.py`).

## Recommended tooling

### Skills

- **skill-creator**: run evaluation loops or description optimization against `evals/evals.json` and `evals/trigger-evals.json`.
- **create-project**: run `/cp-sync` to pull upstream hook/agent updates or `/cp-fix-drift` to audit spec and README alignment.
- **code-scanner**: scan scripts and skill packaging before public release tags.
