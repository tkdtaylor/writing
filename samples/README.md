# Calibration Samples (`samples/`)

Paired `.before.md` and `.after.md` documents calibrate the `writing` skill (`mode=edit`, `mode=review`, `mode=lint`) alongside [`scripts/prose_lint.py`](../scripts/prose_lint.py).

## Committed pairs

Each pair holds domain facts fixed while contrasting model-generated prose habits against clean practitioner writing:

- **Technical guide** (`technical-doc`: [original](technical-doc.before.md) and [revised](technical-doc.after.md)). Rewrites a mode-mixed webhook overview with buried warnings into a pure Diataxis `How-to` guide using `<= 20`-word steps and `openssl` plus `curl` checks.
- **Executive brief** (`executive-memo`: [before](executive-memo.before.md) and [after](executive-memo.after.md)). Converts a chronological `Q3` search diary with naked `"3x"` claims and a buried budget ask into a self-contained `BLUF` decision brief with vetted metrics and epistemic tags.

Negative `.before.md` fixtures deliberately include prose em dashes, emoji bullets, bold restatements, connector colons, stock AI-tell words, buzz-nouns, framing theater, mirror pivots, and false scales. Package checks in `scripts/validate_skill.py` exempt `samples/*.before.md` so detectors have realistic targets, while enforcing zero-tell hygiene on `samples/*.after.md` and `samples/README.md`.

## Running diagnostics on a pair

Invoke the diagnostic CLI from the repository root to compare any pair side by side:

```bash
python3 scripts/prose_lint.py samples/technical-doc.before.md samples/technical-doc.after.md
python3 scripts/prose_lint.py --json samples/executive-memo.before.md samples/executive-memo.after.md
```

## Local distillation inbox (`training/inbox/`)

Place raw personal drafts, team memos, or rough samples inside `training/inbox/` when distilling local voice notes or preparing new benchmarks. Git ignores the entire `training/` directory so private manuscripts, internal metrics, and client names never enter version control. Promote a pair into `samples/` only after stripping confidential data, replacing real names with neutral fictional roles, and confirming clean linter output on the `.after.md` file.
