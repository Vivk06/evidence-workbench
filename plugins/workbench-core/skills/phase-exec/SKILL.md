---
name: phase-exec
description: Execute one phase of an implementation plan with precondition gates, a scope contract, user-owned heavy runs, verification and optional handoffs. Use for "Execute Phase N".
metadata:
  tags: [lean]
  output_mode: terminal
---

# Phase exec

Use this skill as `$phase-exec <plan> <phase>`.

Command class: `safe-local` for the phase's own edits and checks; heavy runs, installs,
commits and pushes are `user-execution` and go to the user.

## Before you start

1. Check that the previous phase passed. The evidence is its recorded gate result in the
   plan, its named gate test, or its tag when the project uses phase tags. Never start a
   phase whose predecessor did not pass, and never redo a completed phase.
2. Read the authority documents in this order:
   - the project's `AGENTS.md` or `CLAUDE.md`, and its anti-pattern registry;
   - the repository profile, when one exists;
   - frozen interface and contract documents;
   - the whole phase section of the plan.
3. State the scope contract: the files to create, the files to change, and the files
   NOT touched. The plan's exclusion list and frozen files bind you, unless a documented
   correction or a deviation the user approved applies.

## Work the phase

- Follow the phase steps exactly. Reread the phase text at each step instead of working
  from memory.
- If the source code proves the plan wrong, record the deviation and its evidence in the
  plan or results document. Never deviate silently.
- Decide ambiguities the user does not need to rule on, record the ruling and continue.
  Collect the ones that need the user (conflict-ledger skill).
- Solver, optimizer, training, MPI and campaign runs belong to the user. Hand over one
  complete command per run with the run-handoff skill, and read the evidence afterwards.
  Never rerun a command the user ran.
- A long local test suite may run in the background, with a filter that keeps only its
  summary, while other safe work continues.

## Completion contract

Before you report a step or gate as passed, name the command that proves it. Run it again
in this session, and read its full output and exit code. Only then state the result,
with the evidence. A gate that did not run is reported as not run, never as passed.

At wrap-up:

1. Run every verification gate and report PASS or FAIL against its stated criterion.
   Record shortfalls as Open Issues. Never relax a gate to make it pass.
2. Change only the phase's Documentation Update Diff, and remove stale references the
   phase created.
3. Add new failure modes to the project's anti-pattern registry (anti-pattern-capture
   skill).
4. Follow the project's commit and handoff convention. Use the handoff skill when a
   handoff is requested. Follow the project's tag policy when it has one.
5. Continue in the current session unless the user or project requires a new one.
   Record facts needed by the next phase in the project's existing documents.

## Refusals

Refuse to start a phase whose predecessor did not pass. Never commit, push or tag for the
user unless the user or the repository's instructions delegate it.
