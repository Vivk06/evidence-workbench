# Fact map and working files

## Working-file marker

A working file is anything an agent keeps for itself: notes, logs, ledgers, handoffs,
plans in progress. Its first line names the reader document that holds its conclusions:

```markdown
<!-- working file: conclusions in docs/mesh-study.md -->
```

The path is relative to the repository root, or to the working file's folder. A reader
never needs to open a working file.
The inventory script counts working files apart from reader documents, and flags a
marker that points to a document that does not exist. CSV ledgers are working files by
their type and need no marker.

## Fact map

Keep the fact map while you work, in `logs/distill_<topic>.md` (itself a working file)
or in the location the user names. One row per fact in the sources:

```markdown
<!-- working file: conclusions in docs/mesh-study.md -->
# Fact map: mesh study

| Fact | Source | Went to |
|---|---|---|
| Fine mesh has 2.1 million cells | notes/run-03.md:4 | docs/mesh-study.md, "Results" |
| Medium-mesh drag changed 0.8% from coarse | notes/run-02.md:12 | docs/mesh-study.md, "Results" |
| Tried 3 layer counts before settling on 30 | notes/run-01.md:20 | dropped: method history the reader does not need |
| Wall distance check not yet run | handoff.md:7 | docs/mesh-study.md, "Open questions" |
```

"Went to" is one of:

- a reader document and section;
- `stays in <working file>`: the reader does not need it, and the working file keeps it;
- `dropped: <reason>`, for one of four reasons:
  - the fact is false for the current code or data;
  - a named source supersedes it;
  - it duplicates a named row;
  - it is method history with no current fact.

Never drop a number a result depends on, a risk, a limit, a failure, or the only copy of a
fact. At the end, the user sees the table rows that say `dropped` or `stays in`.

## Removing sources

The distillation never deletes or moves a source. When a working file has no remaining
use, list it with the command the user runs, one per line, for example
`git rm notes/run-01.md`.
