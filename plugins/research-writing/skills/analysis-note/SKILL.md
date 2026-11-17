---
name: analysis-note
description: Write a self-contained analysis note on one problem in plain language for a first-year master's reader, with each fact once, figures for spatial ideas and small hand checks.
metadata:
  tags: [lean]
  output_mode: terminal
---

# Analysis note

Command class: `safe-local`; writes only the note file the user names.

## Rules

- One problem per file; the note stands alone without the code or chat history.
- Plain language for a first-year master's student: define each symbol at first use, no
  internal codes, ticket numbers or project jargon.
- Each fact once; refer back instead of repeating.
- Figures for anything spatial (geometry, fields, meshes, distributions), each with a
  caption that says what to look at.
- Small hand checks: a limiting case, a units check or an order-of-magnitude estimate
  for each key result.
- Follow the project's layout and the reader's needs. Start with the answer unless a
  required format says otherwise. A title page and table of contents are optional.
- Every number cites its source file or run; unverified numbers are marked.
- Prose follows the plain-language skill, and its checker passes the note: full
  sentences, every term defined at first use. The stop-slop skill sets the tone.

The outline is in `references/outline.md`.

## Refusals

Do not state a result the evidence does not support; write what is known, what is not,
and the check that would settle it (INCONCLUSIVE).
