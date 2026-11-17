# Solver-health checklist

| Check | Where to look | Bad sign |
|---|---|---|
| Non-finite | residual history, force history, field summaries | `nan`, `inf`, `-nan` anywhere |
| Nonlinear cap | final iteration count compared with the maximum | equal to the maximum |
| Linear cap | linear-solver iterations per step | at the maximum on many steps |
| CFL / Δt | adaptive CFL log, time-step history | pinned at the minimum, repeated cuts |
| Positivity | min density, pressure, temperature, turbulence variables | negative or clipped values |
| Bounds | volume fraction, mass fraction | outside [0, 1] |
| Clipping | limiter or clipping counters | growing counts late in the run |
| Multiple solutions | repeats, restarts, continuation runs | same input, different converged value |

Unsteady statistics:

- discard the initial transient; show the discarded window;
- stationarity: compare means of the first and second halves of the sampled window;
- sample over many periods of the slowest relevant frequency;
- confidence interval of a mean from `N_eff` effective samples:
  `mean ± t·σ/sqrt(N_eff)`, with `N_eff = N/(2τ_int)` from the integral time scale `τ_int`
  of the autocorrelation;
- phase averaging only for periodic flows with a known phase reference.
