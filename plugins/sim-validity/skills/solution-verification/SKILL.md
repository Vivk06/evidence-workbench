---
name: solution-verification
description: Estimate the numerical error of a simulation result from iterative convergence and grid or time-step refinement (observed order, Richardson extrapolation, GCI).
metadata:
  tags: [lean]
  output_mode: terminal
---

# Solution verification — numerical error of one result

Command class: `read-only`. Works from existing results; refinement runs are
`user-execution` and go through the run-handoff skill.

Solution verification estimates how far a computed quantity is from the exact solution
of the discretized equations' continuum limit. It is not validation: it says nothing
about whether the equations model reality (`../validation-comparison/SKILL.md`).

## 1. Iterative convergence (each result first)

Check every run used:

- the residual has dropped to the stated floor;
- the quantity of interest has stopped changing over the last iterations. Its relative
  change is below a tolerance at least ten times smaller than the expected
  discretization error;
- no oscillation is larger than that tolerance;
- all values are finite, and no run reached its iteration cap.

A run that hit its cap is not converged. Adjoint runs: the same tests on the adjoint
residual.

## 2. Grid or time-step convergence

Needs three systematically refined solutions with a constant ratio `r` (ideally
`r ≥ 1.3`) and the same quantity `f` from each, grid 1 finest. Compute, as in
`references/gci.md` (Celik et al. 2008; Roache 1998):

- convergence type from `R = (f2 − f1)/(f3 − f2)`: `0 < R < 1` monotonic; `R < 0`
  oscillatory; `R > 1` divergent;
- observed order `p`, extrapolated value `f_ext`, relative errors `e_a21`, `e_ext21`;
- `GCI_fine = 1.25·e_a21/(r^p − 1)` (three grids) and the asymptotic-range check
  `GCI32 ≈ r^p·GCI21`.

Time-step convergence is the same with `Δt` in place of `h`.

## Verdict

- PASS: the convergence is monotonic, and `p` is within a stated band of the formal
  order. The asymptotic check is within a stated band, and `GCI_fine` is below the
  tolerance the study set in advance.
- FAIL: a stated tolerance exceeded on monotonic data.
- INCONCLUSIVE: fewer than three grids, non-constant or unknown `r`, oscillatory or
  divergent convergence, unconverged iterations, or no tolerance set in advance. Name the
  gap and the run that would close it.

Tolerances come from the repository's profile or its own docs; without them, report the
numbers and INCONCLUSIVE for the pass decision. Cite every value as `path:line` or file
and column.
