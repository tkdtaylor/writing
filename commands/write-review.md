---
description: "Run a candid read-only editorial critique with keep, revise, ask-author, and cut passage verdicts"
argument-hint: "<file path or pasted draft, plus optional reader or goal context>"
---

Invoke the `writing` skill ([SKILL.md](../SKILL.md)) with deterministic mode routing:

`mode=review $ARGUMENTS`

Follow `SKILL.md` Step 0 and load `references/review-rubric.md` alongside `references/edit-and-anti-slop.md` and the matching genre guide. Treat this mode as strictly read-only, so do not modify files or output a full rewrite. Deliver a candid piece-level diagnosis followed by passage-level `keep`, `revise`, `ask-author`, and `cut` verdicts that protect earned craft from over-editing.
