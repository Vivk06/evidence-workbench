---
name: codex-delegate
description: "Delegate a read-only survey to Codex: write the prompt file, print the codex exec command for the user, then verify the answer."
metadata:
  tags: [lean]
  output_mode: terminal
---

# Codex delegate — print-only

Command class: `safe-local` for the prompt file; running Codex is `user-execution`.
Claude never runs `codex exec` itself, even when asked: it prints the command.

## Steps

1. Pick a kebab-case topic. Write `logs/codex_<topic>_prompt.md` from
   `references/prompt-template.md`. It holds:
   - the question;
   - the exact files, folders or run outputs to read;
   - the answer format, with `path:line` citations;
   - the read-only rules: no edits, tests, verify scripts, solver, MPI or optimizer runs,
     or installs, and no network unless the question needs it.
2. Print exactly one line, with nothing after it:

   `codex exec -s read-only -C "$PWD" -o logs/codex_<topic>.md - <
   logs/codex_<topic>_prompt.md > logs/codex_<topic>.stdout 2>&1`

3. Stop and wait for the user to say it finished.
4. Read `logs/codex_<topic>.md` and treat it as unverified. Check every fact you will use
   against its cited file and line, and mark each `confirmed`, `wrong` or `uncited`. Use
   only confirmed facts, and report the wrong ones to the user.

## Refusals

- Asked to run Codex, or to "just do it yourself with codex": print the command and stop.
- Output file missing or empty: report INCONCLUSIVE with the stdout log path; do not guess
  what Codex would have found.
