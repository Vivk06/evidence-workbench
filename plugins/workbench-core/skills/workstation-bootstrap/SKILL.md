---
name: workstation-bootstrap
description: Check that this machine can work on a repository - activation script, interpreters, CLIs and plugins it needs - without installing or running anything expensive.
metadata:
  tags: [lean]
  output_mode: terminal
---

# Workstation bootstrap

Use this skill as `$workstation-bootstrap [<repository>]`.

Command class: `read-only`.

## Steps

1. Read the repository's profile with `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/profile.py <repo>`
   (Codex: `../../scripts/profile.py` from this skill's folder). Without a profile, read
   its `AGENTS.md`, README and environment files (`environment.yml`, `requirements*.txt`,
   `pyproject.toml`, `activate.sh`).
2. Check the activation script exists; run environment checks only inside it.
3. Check each named interpreter and CLI with `command -v <tool>` and `<tool> --version`.
4. Check the plugins the repository expects with `claude plugin list` or
   `codex plugin list`.

## Output

A table of requirement, found version or path, and `ok`, `missing` or `unknown`, each with
the file that declared it. List missing items with the install command for the user.

## Refusals

Installing, activating a new environment, logging in, and solver, MPI, optimizer or
campaign runs are `user-execution`: print the command and stop. Never read credentials.

## Lean mode

With `--lean` or a terminal-only request, follow the lean-output skill: print the table
only, and write no file.
