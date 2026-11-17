---
name: run-handoff
description: Compose one command for an expensive run (solver, MPI, training, sweep) for the user to execute, and list the evidence to bring back.
metadata:
  tags: [lean]
  output_mode: terminal
---

# Run handoff — one command, then evidence

Command class: `read-only` (it composes text). The run itself is `user-execution`:
never start it, in the foreground or background, and never re-run a run the user owns.

## Compose the command

Gather, from the profile when the repository has one
(`python3 ${CLAUDE_PLUGIN_ROOT}/scripts/profile.py <root>`; Codex: `../../scripts/profile.py`
from this skill's folder), otherwise from the repository's own docs and scripts:

- Activation: profile `activation`, else `python` prefix, else what the repository
  documents (`activate.sh`, `.venv`, `conda activate`, module loads). If none is found, ask.
- Prefix: profile `run_handoff.prefix` (e.g. core binding) or the documented launcher.
- Output location: profile `run_handoff.output` or the repository's run-directory
  convention; name a fresh, specific path. Never point at an existing run.
- Log capture: if the run writes its own log, do not add `tee` (profile
  `run_handoff.tee: false`); otherwise append `2>&1 | tee logs/run_<topic>.log`.

Write it as one line runnable from the repository root, absolute or root-relative paths
only, no placeholders left (ask for any value you cannot determine). See
`references/run-command.md` for the shape and checks.

## Evidence to bring back

List what the user returns, or where you will read it:

- the log path;
- the status or summary files;
- the convergence or metric files;
- the run folder.

State the gate each one feeds. A zero exit code establishes nothing about convergence,
accuracy, mesh validity or physical plausibility; the verdict comes from the evidence.

## After the run

Read only the evidence listed, frugally (tail, grep, summary files). Report PASS, FAIL or
INCONCLUSIVE per gate with a `path:line` or value for each. Missing evidence is
INCONCLUSIVE.
