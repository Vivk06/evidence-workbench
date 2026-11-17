# Grid convergence index procedure

After Celik, Ghia, Roache, Freitas, Coleman and Raad, "Procedure for estimation and
reporting of uncertainty due to discretization in CFD applications", J. Fluids Eng.
130 (2008) 078001; Roache, *Verification and Validation in Computational Science and
Engineering* (1998).

Grids 1 (finest), 2, 3. Representative cell size `h = ((1/N) Σ ΔV_i)^(1/D)` for `N`
cells of volume `ΔV_i` in `D` dimensions. Ratios `r21 = h2/h1`, `r32 = h3/h2`.

```
ε21 = f2 − f1          ε32 = f3 − f2          s = sign(ε32/ε21)
R   = ε21/ε32          (0<R<1 monotonic, R<0 oscillatory, R>1 divergent)

constant r:   p = ln(ε32/ε21) / ln r
general r:    p = |ln|ε32/ε21| + q(p)| / ln r21
              q(p) = ln( (r21^p − s) / (r32^p − s) )      (solve by fixed-point iteration)

f_ext21  = (r21^p f1 − f2) / (r21^p − 1)
e_a21    = |(f1 − f2)/f1|
e_ext21  = |(f_ext21 − f1)/f_ext21|
GCI21    = Fs · e_a21 / (r21^p − 1)        Fs = 1.25 (three or more grids), 3.0 (two grids)
GCI32    = Fs · e_a32 / (r32^p − 1)
asymptotic range:  GCI32 / (r21^p · GCI21) ≈ 1
```

Notes:

- Report `f1`, `f_ext21`, `p`, `e_a21`, `e_ext21`, `GCI21` and the asymptotic ratio.
- A `p` far from the formal order has one of two causes. The grids are not in the
  asymptotic range, or a lower-order error dominates, such as one from boundaries,
  limiters or switches. Refine further
  before trusting the GCI.
- Oscillatory convergence: Celik et al. suggest an oscillation-range bound; treat it as
  an uncertainty statement, not a verified error estimate.
- Use quantities that converge smoothly (integrated forces, fluxes); point values near
  discontinuities or limiter activity often do not.
