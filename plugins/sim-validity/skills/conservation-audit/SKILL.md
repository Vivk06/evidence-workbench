---
name: conservation-audit
description: Check that a simulation conserves what it should - global and local balances of mass, momentum, energy, charge or species, and consistency between computed and reported fluxes.
metadata:
  tags: [lean]
  output_mode: terminal
---

# Conservation audit

Command class: `read-only`; works from existing outputs and logs.

A conservative scheme balances each conserved quantity to round-off at convergence; a
non-conservative one balances only to truncation error. Know which the code claims before
setting a tolerance (LeVeque, *Finite Volume Methods for Hyperbolic Problems*, 2002).

## Checks

1. Global balance per conserved quantity over the domain (`references/balances.md`):
   storage change plus net boundary flux minus sources. Report the imbalance relative
   to the largest boundary flux.
2. Local balance: the discrete divergence of the flux in each cell, as maximum and norm;
   locate the worst cells (boundaries, interfaces, refinement levels, hanging nodes).
3. Consistency ratio: compare the flux used in the update with the flux the code reports
   or post-processes. An example is a reported divergence divided by the solver's own
   residual. A ratio far from 1 means the diagnostic and the solver disagree, whatever
   the absolute value.
4. Boundary conditions: walls with no-penetration or insulating conditions carry zero
   normal flux; check it.

## Tolerances

Set the tolerance by what the solver can achieve. For a converged steady run, that is
about the iterative residual level. For round-off, it is above `N·ε_machine` scaled by
the flux magnitude.
Take the project's own tolerance from its profile or docs when present.

## Verdict

- PASS: every listed balance within its tolerance, with values cited.
- FAIL: an imbalance above tolerance on an iteratively converged run, or a consistency
  ratio outside its band.
- INCONCLUSIVE: missing flux outputs, unconverged run, or no tolerance; name what to
  output. Never loosen a tolerance to pass.
