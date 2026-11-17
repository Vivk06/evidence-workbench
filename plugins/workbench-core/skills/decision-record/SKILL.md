---
name: decision-record
description: Write or amend a design decision record in the repository's style, with Evidence and Rejected options.
metadata:
  tags: [lean]
  output_mode: terminal
---

# Decision record

Command class: `safe-local`; writes only decision files.

## Find the decisions and their style

1. Profile `authority.decisions` (`{path, style}`), read with
   `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/profile.py <root>` (Codex: `../../scripts/profile.py`).
2. Otherwise look for `docs/decisions/`, `docs/adr/`, `adr/`, `decisions.md`; infer the style
   from existing records (numbering, headings, amendment practice).
3. None found: propose `docs/decisions/0001-<slug>.md` in the append-only style and ask.

## Styles

- `append-only`: never edit an accepted record's decision. A new choice gets the next
  number; a change to an existing one is a dated `Amendment` section at its end.
- `current-decision`: the record states one current decision. Rewrite it, and move the
  replaced option to `Rejected options` with the measured reason and the date.

## Content

Use `references/template.md`: context, decision, consequences, `Evidence` (measurements,
`path:line`, logs; required), `Rejected options` (each with the reason it lost). Keep the
numbers a decision depends on, with units and conditions.

## Refusals

- No evidence for the choice: write the record with status `Proposed` and an Evidence
  section that lists what is missing; never mark it accepted.
- Never delete an old record to hide a reversal.
