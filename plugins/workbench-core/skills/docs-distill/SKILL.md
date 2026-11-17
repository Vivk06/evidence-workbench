---
name: docs-distill
description: "Rewrite docs to the current state without losing facts: move facts to their owners, keep gate numbers, list what was removed."
metadata:
  tags: [lean]
  output_mode: terminal
---

# Docs distill — distill, never drop

Command class: `safe-local`; edits only the documentation named in scope.

Documentation states current operation; history lives in version control. Shortening is
allowed only after every fact has a home.

## Five-step review

1. Inventory: list each fact in the document (claims, numbers, rules, procedures, links).
2. Owner: for each fact, name its owning document (authority map; profile
   `authority` when present). Facts owned elsewhere become links.
3. Move, then shorten: copy facts that have no owner yet into their owning document
   first; only then cut them from the source.
4. Drop only a fact that is false at HEAD, superseded, duplicated at its owner, or
   narrative with no current fact. Check "false at HEAD" against the code or data.
5. Verify numbers: every number a gate depends on survives, with units, conditions and a
   link to its evidence.

Write prose by the stop-slop rules when that skill is available: lead with the fact, name
the file, no filler. When the reader is a person, use the reader-distill
skill if the research-writing plugin is on. It adds document types, answers first and a
plain-language check.

## Output

- The rewritten documents.
- A `Removed, and where it went` list: each removed fact and its new owner, or the reason
  it was dropped (false at HEAD, superseded by X, duplicate of Y).
- Conflicts found on the way go to the conflict-ledger skill, not into a silent choice.

## Long distillations

For work across several turns or sessions, keep a ledger in `logs/distill_<topic>.md`, in
the `references/ledger.md` format. It has one row per source section with its status, so
the next session continues instead of rereading.

## Refusals

Never drop a number a gate depends on, or the only copy of a fact, even when asked to
shorten: keep it, or move it to an owning document you name and link. Say why.
