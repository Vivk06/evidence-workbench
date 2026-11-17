---
name: derivative-audit
description: Audit adjoint or AD gradients against finite-difference or complex-step evidence - step sweeps, cold starts, per-row bands, configuration parity and parameterization limits.
metadata:
  tags: [lean]
  output_mode: terminal
---

# Derivative audit

Use this skill as `$derivative-audit <evidence-directory>`.

Command class: `read-only`. It never launches primal, adjoint, finite-difference, MPI or
optimizer work, and never writes into a run folder. Verification runs go to the user as
one exact command through the run-handoff skill, and the audit waits for the log.

## Method (Martins & Ning 2021; Squire & Trapp 1998)

Follow `references/method.md`:

1. Reference derivative: a central finite difference or complex step on the same
   functional, from cold starts. Each perturbed solve converges from the same initial
   state, and none starts warm from the baseline.
2. Step sweep: errors across several step sizes show the truncation branch, the plateau
   and the round-off branch; use a step on the plateau. One FD pair is not a sweep.
3. Per-row bands set in advance; a comparison without a band is a report, not evidence.
4. Configuration parity: primal and adjoint use the same mesh, markers, reference values,
   freestream and solver settings; the adjoint residual is converged.
5. Parameterization limits: report rows that finite differences cannot verify as
   limitations, never as passes. Examples are tangential or chordwise shape modes that
   only reparameterize the surface. Projection terms the gradient needs must be present,
   such as an angle-of-attack correction.

Bands come from the repository's profile or docs; when none exist, report the errors and
INCONCLUSIVE for the pass decision. `references/examples.md` shows bands from one study.

## Checker

`python3 ${CLAUDE_PLUGIN_ROOT}/skills/derivative-audit/scripts/audit.py --evidence <json>
[--profile <name>]` reads an evidence file and reports the bands it was given (Codex:
`scripts/audit.py` in this skill's folder). The file has the keys `cold_start`,
`independent_adjoint`, `config_parity`, `provenance` and `rows`. Each row has `name`,
`relative_error`, `band`, `projection_terms` and `tangential`.

Without an evidence file, inspect existing files only:
`find <dir> -maxdepth 2 -type f | sort` and
`grep -R -n -E 'derivative|adjoint|finite.?difference|cold.?start|tolerance' <dir>`.

## Verdict

`PASS` only if every required row and gate is present and passes; `FAIL` for an explicit
failed gate; otherwise `INCONCLUSIVE` with cited gaps. Keep three states apart: a
prepared command, available evidence, and completed evidence. A converged solver is not
a valid derivative without quantitative agreement.

## Lean mode

With `--lean` or a terminal-only request, follow the lean-output skill: print the
verdict and evidence only, and write no file.
