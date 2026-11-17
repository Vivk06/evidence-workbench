---
name: anti-pattern-capture
description: Add a failure mode to the repository's anti-pattern registry with a new stable ID and evidence, once its root cause is known.
metadata:
  tags: [lean]
  output_mode: terminal
---

# Anti-pattern capture

Command class: `safe-local`; writes only the registry file.

## Find the registry

1. Profile `authority.anti_patterns` (`{path, id}`), read with
   `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/profile.py <root>` (Codex: `../../scripts/profile.py`).
2. Otherwise search the repository: files named like `anti_patterns.md`, `ANTIPATTERNS`,
   `pitfalls`, or an "Anti-pattern registry" section in `AGENTS.md`/`CLAUDE.md`.
3. None found: show the row and ask where it belongs; offer an `AGENTS.md` section.

## Write the row

- ID: follow the registry's own scheme (`AP-N`, `A-xx`, `R<n>-<m>`, …). Take the next
  number after the highest existing one; never reuse or renumber an ID, even a retired one.
- Fill the fields in the registry's own column order:
  - symptom: what was observed;
  - cause: the root cause, not the trigger;
  - fix: the right pattern;
  - detection: the check or test that catches it;
  - evidence: a `path:line`, log path or commit.
- Match the registry's existing format exactly (table row, list item or section).
- One failure mode per row. If an existing row covers it, add the new evidence to that
  row instead of a duplicate.

## Refusals

- No established root cause or no evidence: do not add a row; report INCONCLUSIVE and
  what evidence would settle it.
- Do not rewrite or delete other rows.

`references/row-examples.md` shows the three common formats.
