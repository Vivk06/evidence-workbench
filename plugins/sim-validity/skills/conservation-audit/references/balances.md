# Balance formulas

Integral balance of a conserved density `U` with flux `F` and source `S` over the domain
`Ω` with boundary `∂Ω`:

```
d/dt ∫_Ω U dV + ∮_∂Ω F·n dA − ∫_Ω S dV = 0
imbalance      = (U^{n+1} − U^n)·V/Δt + Σ_faces F·n A − Σ_cells S V
relative       = |imbalance| / max_boundary |F·n A|
```

Per quantity:

- mass: inflow − outflow (+ sources such as injection);
- momentum: pressure and viscous boundary forces plus body forces;
- energy: enthalpy fluxes, wall heat flux, work and sources;
- species: fluxes plus reaction sources (sum over species must reproduce mass);
- charge in low-magnetic-Reynolds MHD: `∇·J = 0`, with `J` built on the faces the solver
  uses; compare the divergence of the face current with the potential-equation residual.

Local check: for each cell `c`, `r_c = Σ_faces(c) F·n A − S_c V_c` at steady state;
report `max|r_c|`, the L2 norm and the cells where it peaks.

Consistency ratio: `ratio = reported_quantity / solver_residual_of_same_quantity`, only
when the denominator is above round-off; a band such as `0.99 ≤ ratio ≤ 1.01` is set by
the project.
