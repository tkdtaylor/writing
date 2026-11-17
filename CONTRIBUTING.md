# Contributing to writing

Thanks for considering a contribution. `writing` uses an agent-driven, test-spec-first workflow, and every change to the skill or its diagnostic tooling follows the conventions in [AGENTS.md](AGENTS.md).

## Ground rules

1. **Practice what the skill teaches.** Every Markdown file in this repository must follow the skill's own prose and formatting rules: no em dashes in prose, single-line continuous paragraphs (never hard-wrapped at 80 columns), a blank line before lists, plain words, and zero AI-tell filler.
2. **Respect token budgets.** `SKILL.md` and `references/*.md` load into an agent's context window. Keep `SKILL.md` under 1,500 words and each reference file under 1,500 words, verified by `python3 scripts/validate_skill.py`.
3. **Test-spec-first tasks.** Non-trivial changes pair a task file (`docs/tasks/backlog/NNN-slug.md`) with a test spec (`docs/tasks/test-specs/NNN-slug-test-spec.md`) and unit tests under `tests/`. Run `make check` before opening a pull request.
4. **Keep specs and routing synchronized.** Adding or renaming a reference file, slash command, or script requires updating `SKILL.md`, `docs/spec/`, and `README.md` in the same commit.
5. **One concern per pull request.** Small, reviewable changes over multi-topic bundles.
6. **DCO sign-off.** Commit with `git commit -s`. By signing off, you agree your contribution is licensed under this repository's MIT license and [Code of Conduct](CODE_OF_CONDUCT.md).

## Security issues

Please do **not** open public issues for vulnerabilities. Follow [SECURITY.md](SECURITY.md).

## License

`writing` is MIT-licensed. See [LICENSE](LICENSE).
