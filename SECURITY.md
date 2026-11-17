# Security Policy

## Supported versions

`writing` has not yet cut a tagged release. Only the current `main` branch receives security fixes.

| Version | Security fixes |
|---------|---------------|
| `main` | Yes |

## Reporting a vulnerability

**Please do not open a public GitHub issue for security vulnerabilities.**

### Option 1: GitHub private vulnerability reporting (preferred)

Use GitHub's built-in private advisory flow: <https://github.com/tkdtaylor/writing/security/advisories/new>

### Option 2: Email

Send a report to <tools@taylorguard.me> with a description, reproduction steps, the commit you observed it on, and your severity assessment.

## Response expectations

- **Acknowledgement:** within 7 days. **Status update:** within 30 days.
- **Fix shipped:** within 90 days for confirmed vulnerabilities (critical issues target 14 days).

## Scope

**In scope:** anything the skill or its scripts do that weakens a user's workspace, including diagnostic scripts (`scripts/*.py`) that execute unexpected commands or traverse unintended paths, prompt-injection failures where instructions embedded in untrusted source drafts alter agent tool behavior, or repository configurations that grant broader permissions than documented.

**Out of scope:** vulnerabilities in third-party harnesses or upstream tools (report those upstream), and findings requiring an already-compromised host.
