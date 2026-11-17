---
name: inspect-run
description: Inspect an existing run's status and evidence without mutation or restart.
metadata:
  tags: [lean]
  output_mode: terminal
---

# Inspect run

Use this skill as `$inspect-run <run-directory>`.

Command class: `read-only`. Never edit, promote, clean, delete, restart or archive a run.

## Inputs

An explicit run directory, a run ID the repository's profile or docs can resolve, or a
repository-local output root. The path must exist inside the repository or its declared
archive. Run roots and parsers come from the repository's profile (`AGENTS.md`
frontmatter) or docs; without them, ask for the path.

## Steps

1. List files with a bounded listing, e.g. `find <run> -maxdepth 2 -type f | sort`.
2. Read provenance, configuration and status markers; compare timestamps and hashes
   when present.
3. Read bounded log tails only, e.g. `tail -n 80 <log>`.
4. Use only commands that exist in the repository; never invent a parser.

## Output

Report these:

- the resolved run path, and the status and provenance files found;
- the configuration identity and the final lines of the log;
- objective or history evidence, and the evidence that is missing;
- the next file to inspect.

Write `evidence unavailable` for an absent field. Never infer success from an
exit status or a convergence-looking log line.

## Refusals

Some actions go to the user as one printed command, through the run-handoff skill:
reruns, promotion and post-processing that writes files. So do solver, MPI and optimizer
runs, and archive or cleanup actions.

## Lean mode

With `--lean` or a terminal-only request, follow the lean-output skill: print the
evidence and next step only, and write no file.
