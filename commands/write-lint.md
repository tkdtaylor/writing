---
description: "Inspect Markdown or plain-text prose for cadence, substance ratios, and mechanical tells without altering text"
argument-hint: "<file path(s) or pasted text>"
---

Invoke the `writing` skill ([SKILL.md](../SKILL.md)) with deterministic mode routing:

`mode=lint $ARGUMENTS`

Follow `SKILL.md` Step 0 and run `scripts/strip_markdown.py` and `scripts/prose_lint.py` on the target files or input text. Report cadence metrics, lexical diversity, concrete anchor vs hedge and booster ratios, and line-numbered mechanical tells in plain language. Never alter source files or collapse diagnostics into a single composite AI detection score.
