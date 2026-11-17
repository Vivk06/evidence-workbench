# Method of manufactured solutions

Sources:

- Salari and Knupp, "Code verification by the method of manufactured solutions", Sandia
  report SAND2000-1444 (2000).
- Roy, "Review of code and solution verification procedures for computational
  simulation", Journal of Computational Physics 205 (2005), pages 131 to 156.
- Oberkampf and Roy, *Verification and Validation in Scientific Computing* (2010),
  chapters 5 and 6.

Choosing the field:

- smooth, with all derivatives the operator uses non-zero and of similar magnitude;
- trigonometric or exponential terms with incommensurate wavenumbers avoid accidental
  cancellation;
- for positivity-constrained variables, keep the field inside the physical range.

Error norms over `N` cells with exact `u_e`:

```
L2   = sqrt( (1/N) Σ (u_i − u_e,i)^2 )         (volume-weighted for non-uniform grids)
L∞   = max |u_i − u_e,i|
p    = ln(E_2h / E_h) / ln 2                     (ratio-2 refinement)
```

Coverage table to report: each term and each boundary type against the grids where it is
active, with its observed order. A term missing from the table is unverified.

Short symbolic source derivation (local, free):

```python
import sympy as sp
x, y, t = sp.symbols("x y t")
u = sp.sin(2*x) * sp.exp(-y) + sp.cos(3*y)   # manufactured field
nu = sp.Rational(1, 100)
S = sp.diff(u, t) + u*sp.diff(u, x) - nu*(sp.diff(u, x, 2) + sp.diff(u, y, 2))
print(sp.simplify(S))
```
