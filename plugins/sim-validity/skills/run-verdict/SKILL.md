---
name: run-verdict
description: Decide whether an existing simulation run is valid from cited artifacts and the project's gates; never execute or mutate a run.
metadata:
  tags: [lean]
  output_mode: terminal
---

# Run verdict

Use this skill as `$run-verdict <run-directory> [<baseline>]`.

Command class: `read-only`. Require an explicit run directory. Reruns, promotion,
cleanup, plotting, and artifact writing are handed to the user as user-execution actions.

## Gates

Take the gate definitions from the repository. Use `authority.gates` in the `workbench:`
block of its `AGENTS.md` frontmatter when there is one. Otherwise use its test matrix,
gate methodology or verification docs. Without gate definitions, report the evidence
found and INCONCLUSIVE for validity. Gate families that work for most codes, with
example thresholds, are in `references/examples.md`; the general methods are the
solution-verification, conservation-audit, solver-health and validation-comparison skills.

## Collect

Run `python3 ${CLAUDE_PLUGIN_ROOT}/skills/run-verdict/scripts/collect.py
--run-dir <absolute-path> [--baseline <file>]` (Codex: `scripts/collect.py` in this
skill's folder). It reads only the named directory and prints JSON. It recognises
`status.json`, `provenance.json`/`manifest.json`, `resolved_config.json`/`config.json`,
`history.csv`/`history.json`, `solver.log`/`run.log` and `gates.json`
(`{"gate": {"pass": true, ...}}`). When the run uses other names, map each artifact by
hand and say so.

Collect and cite status/exit state, resolved configuration, provenance, objective or
history, residual evidence, and physics/mesh gate artifacts. A converged solver is
not a valid run without quantitative physics gates. Compare only against a supplied
baseline or a baseline explicitly recorded in an artifact; otherwise report
“evidence unavailable”. Every PASS or FAIL field must name an artifact and value.

## Verdict

- `PASS` only when every required artifact is present and every gate passes with a cited
  value.
- `FAIL` when a present gate fails.
- `INCONCLUSIVE` when required evidence or gate definitions are missing or ambiguous.

Keep pre-existing failures separate from regressions. Prepared commands and suggested
next actions are not completed evidence. An exit code establishes nothing about
convergence or physical validity.

## Lean mode

With `--lean` or a terminal-only request, follow the lean-output skill: print the
verdict and evidence only, and write no file.
