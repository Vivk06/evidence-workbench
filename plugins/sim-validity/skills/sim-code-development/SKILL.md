---
name: sim-code-development
description: Plan and implement a scoped change to simulation code with characterization before the change, a before log, proportional verification and frozen interfaces respected.
metadata:
  tags: [lean]
  output_mode: terminal
---

# Simulation code development

Use this skill as `$sim-code-development <repo> [--lean]`. Require one explicit,
existing repository path; do not infer a project from the working directory or search
outside that path.

Command class: `safe-local` for reading, planning and editing the scoped files. Solver,
MPI, optimizer, full-tier test, install, publish, and any destructive operation are
user-executed.

Treat the target repository as user-owned. Find its activation step and tell the user to
run it before any project command. Look first for `activation` in the `workbench:` block
of `AGENTS.md`, then for `activate.sh` or `.venv`, then in its docs. Never source it
yourself. Frozen interfaces come from the profile's `frozen_paths` or the repository's own
"do not edit" list; they change only through its decision route.

## Workflow

1. State the requested outcome and change boundary. Inventory the nearest ownership
   guidance, build/test entrypoints, affected source, call sites, configuration and
   numerical/physics contracts. Cite every path used.
2. Make a small implementation plan: intended files, preserved contracts, behavior
   to characterize, risks, and the narrowest verification tier. Do not broaden a
   change merely because adjacent cleanup looks attractive.
3. Characterize before changing. When behavior must be preserved and the tests do not
   cover it, propose a characterization test. Or ask the user to capture a log of the
   affected case before the change (run-handoff skill), to compare against afterwards.
   Preserve observable behavior, including error handling, parsing, configuration
   defaults, numerical tolerances, and restart/provenance formats.
4. Implement only after the user has authorized the scoped target change. Never
   weaken, delete, skip, or rewrite tests just to make a change pass. Report an
   existing failure separately from a regression introduced by the change.
5. Verify in proportion to risk. A change to parameters only needs the affected test
   module. A numerical change needs the before-and-after comparison and the relevant
   method: code-verification, solution-verification or conservation-audit. Run only
   bounded local checks; hand expensive verification to the user with exact commands and
   the evidence requested. Summarize the changed paths, the tests run and not run, the
   evidence, the remaining risk and one next action.

## Report contract

Normal mode reports in the conversation by default; write a file only when the user
explicitly requests an output path. `--lean` returns only: decision, cited paths,
unresolved gaps, and one next action. A plan, command, or green exit status is not
evidence that a simulation result is valid; without the evidence the verdict is
INCONCLUSIVE.
