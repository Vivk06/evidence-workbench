---
name: solver-health
description: Check a run's numerical health - non-finite values, iteration caps, CFL and time-step limits, positivity and bounds, clipping, multiple solutions, and unsteady statistics.
metadata:
  tags: [lean]
  output_mode: terminal
---

# Solver health

Command class: `read-only`; reads logs and outputs frugally (tail, grep, summaries).

A run can exit 0 and still be unhealthy; an exit code establishes nothing. Work
through `references/checklist.md` and cite each finding as `path:line` or file and field.

## Checks

1. Non-finite values: NaN or Inf in fields, residuals, forces or histories.
2. Iteration caps: nonlinear or linear solver hitting its maximum iterations; a capped
   linear solve inside a converging outer loop still corrupts the update.
3. Stability limits: CFL or time step at its limit, automatic reductions, restarts.
4. Positivity and bounds: density, pressure, temperature, turbulence quantities and
   volume fractions inside their physical ranges; count clipping or limiter events.
5. Multiple solutions: repeated runs or restarts of the same input landing on different
   converged states (hysteresis, branches). That is a finding to report, never something
   to average away.
6. Unsteady runs: initial transient removed, stationarity of the sampled window, sample
   length against the slowest period, confidence intervals on means (`references/checklist.md`).

## Verdict

- PASS: every applicable check clean, each with its evidence.
- FAIL: any non-finite value, a cap reached on the reported state, a bound violated
  without the code's documented treatment, or unreported multiple solutions.
- INCONCLUSIVE: logs or outputs needed for a check are missing; name them.
