---
name: plan-forge
description: Generate or revise a phased implementation plan (plan_inputs.md, PLANNER_SPEC.md, plan) - bootstrap, populate, generate, feasibility review, or versioned revision.
metadata:
  tags: [lean]
  output_mode: terminal
---

# Plan forge

Use this skill as `$plan-forge <stage>`.

Command class: `safe-local`: it writes only the planning files named below.

Use the stage that matches the request. Never run a later stage unasked.

## Bootstrap

For a new project without `PLANNER_SPEC.md`, create the planning files from the canonical
specification the user has. Create `plan_inputs.md` with these sections: Aim, Project
Overview, Current State, Knowledge Base, Constraints & Environment, and Prior Art /
Baselines. Leave Aim empty unless the user supplies it.

## Populate `plan_inputs.md`

1. Read the project's authority documents in this order:
   - `AGENTS.md` or `CLAUDE.md`, and the repository profile when one exists;
   - code-graph outputs, through their query interface, when present;
   - knowledge, interface and results documents;
   - the text forms of papers (`txt_files/`) instead of the PDFs, when both exist.
2. Fill every section except Aim. Aim belongs to the user and is locked: copy the user's
   wording exactly, and never broaden or paraphrase it.
3. Record numerical baselines with their dates and sources. Check that every Knowledge
   Base path exists before you write it down.

## Generate a plan

Read `PLANNER_SPEC.md`, `plan_inputs.md` and every Knowledge Base file they list. Write to
the file name the user gives. Follow the specification's eight sections, and its nine
subsections for each phase.

- Gates are binary and runnable. Never use a qualitative claim such as "it converged".
- Every phase names excluded files and a rollback. Include a new-session prompt only
  when the user or project requests it. Follow the project's existing plan format.

Plan quality (methods in `references/borrowed-methods.md`):

- Open with a Global Constraints block: project-wide limits copied word for word, binding
  on every phase.
- Add a Review Focus list. It names the inputs or failure modes the aim implies but no
  gate exercises, and assigns each to the phase that owns the code.
- Give each phase Interfaces: what it consumes from earlier phases and what it produces
  for later ones, with exact names and signatures.
- No placeholder steps, such as "TBD" or "handle edge cases". A step that decides nothing
  is a defect. Review the plan and fix such steps in place.
- Size phases sensibly. Split only where a reviewer could reject one part and accept its
  neighbour. Fold setup and documentation into the phase that needs them.

## Advisory pass or revision

For an advisory pass:

- Check every referenced file, function and signature in the source code, not only in
  instruction files.
- Check claims about libraries and solvers against their installed or frozen
  documentation.
- Add missing references, and test whether the run budget is realistic.
- Present risks as options. Never silently change a locked decision.

For a versioned revision, renumber the phases from one and remove completed or stale
material. Note that the earlier content stays in git history.

## Refusals

Planning is bounded local work. Never launch solver, MPI, optimizer, campaign,
installation, commit, push or tag operations; hand those actions to the user.
