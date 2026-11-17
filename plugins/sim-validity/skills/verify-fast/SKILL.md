---
name: verify-fast
description: Run a repository's own fast checks (tests, linters, manifest validators) without solver, MPI or user-state work, and report PASS or FAIL.
metadata:
  tags: [lean]
  output_mode: terminal
---

# Verify fast

Use this skill as `$verify-fast [<repository>]`.

Command class: `safe-local`. Bounded local checks only: manifests, configuration, unit
and hygiene checks, command availability. No CFD, MPI, optimizer, DAKOTA, campaign,
installation or git index operations, and no writes to the repository or user
configuration.

## Steps

1. Work from the repository root. Source the repository's activation script first; this
   skill never activates a solver environment implicitly.
2. Pick the repository's own fast check, in this order:
   - the command its profile allows (`agent_allowed` in the `AGENTS.md` frontmatter);
   - the one its `AGENTS.md` or README names;
   - an existing `verify.sh`, test runner or manifest validator.
3. If none exists, report `UNAVAILABLE`; never invent a replacement command.

## Output

The entry point used, checks performed, checks skipped and why, evidence paths, and one
`PASS` or `FAIL`. A green fast check says nothing about solver or physics success.

## Refusals

MPI or solver verification, full tiers, optimizer and DAKOTA checks, and installation are
`user-execution`: hand them to the user as one printed command (run-handoff skill).

## Lean mode

With `--lean` or a terminal-only request, follow the lean-output skill: print the result
only, and write no file.
