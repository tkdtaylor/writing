# Tech Stack

| Layer | Technology | Rationale |
|-------|------------|-----------|
| Skill instructions | GitHub-Flavored Markdown + YAML frontmatter | Native format across Claude Code, Antigravity, Codex, Cursor, and Copilot |
| Diagnostic and validation CLIs | Python 3.10+ (`stdlib` only) | Runs out of the box on macOS and Linux with zero virtual-environment setup |
| Automated tests | `unittest` (`python3 -m unittest`) | Built into Python standard library; fast execution in worktrees and CI |
| Diagram validation | `scripts/check-mermaid.py` | Prevents GitHub Mermaid parser hazards without Node/headless browser deps |
| Cross-harness sync | `scripts/sync-agy-skills.py` | Keeps `.agents/` workspace skills and custom subagents aligned with `.claude/` |
| License | MIT | Frictionless copying of prompts, templates, slash commands, and samples |
