# Derivative verification method

Sources: Martins & Ning, *Engineering Design Optimization* (2021), ch. 6; Squire &
Trapp, "Using complex variables to estimate derivatives of real functions", SIAM Review
40 (1998) 110–112.

```
forward FD     f'(x) ≈ (f(x + h) − f(x)) / h                 error O(h) + O(ε/h)
central FD     f'(x) ≈ (f(x + h) − f(x − h)) / (2h)          error O(h²) + O(ε/h)
complex step   f'(x) ≈ Im f(x + i h) / h                     error O(h²), no subtraction
relative error = |g_adj − g_ref| / max(|g_ref|, floor)
```

- Step sweep: evaluate at `h = 10^-k` for several `k`; plot or tabulate the difference to
  the adjoint. The usable step lies on the plateau between truncation (large `h`) and
  round-off or solver-tolerance noise (small `h`). The functional's own convergence
  tolerance sets a noise floor: `h` must make `f(x+h) − f(x)` well above it.
- Cold starts: each perturbed solve starts from the same initial condition and converges
  fully; warm starts and within-solve drift mimic agreement or noise.
- Repeated evaluations of the same point that differ by more than the noise floor are a
  finding (possible multiple solutions), not noise to average.
- Complex step needs a code that propagates complex numbers through every operation.
- On a converged state, automatic-differentiation and discrete adjoints should match a
  complex-step reference to near machine precision. Looser agreement points to
  unconverged residuals or missing terms.
