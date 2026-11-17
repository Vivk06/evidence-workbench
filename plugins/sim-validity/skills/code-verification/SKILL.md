---
name: code-verification
description: Verify that a solver solves its equations correctly with manufactured or analytic solutions and observed-versus-formal order of accuracy on every term and boundary.
metadata:
  tags: [lean]
  output_mode: terminal
---

# Code verification — is the equation solved right

Command class: `read-only` for planning and reading results; MMS or analytic runs are
`user-execution` (run-handoff skill).

Code verification shows the discretization converges to the exact solution of the
equations at the formal order. It precedes solution verification and validation and is
never replaced by them (Roache 1998; Oberkampf & Roy 2010).

## Method of manufactured solutions (MMS)

As in `references/mms.md` (Salari & Knupp 2000; Roy 2005):

1. Choose a smooth analytic field with non-trivial derivatives everywhere. It must
   exercise every term: convection, diffusion, source, time derivative and coupling.
2. Derive the source term symbolically, for example with a short local SymPy script, and
   add it.
3. Impose boundary values from the manufactured field; cover every boundary-condition
   type the code uses.
4. Run at least three systematically refined grids; compute discrete error norms
   (L2 and L∞) against the field.
5. Observed order `p = ln(E_coarse/E_fine)/ln r` per norm and variable.

## Analytic-solution gates

Where a closed-form or series solution exists, compare named quantities in stated norms,
within stated bands. Also check how the code's inputs map to the analytic parameters
after non-dimensionalisation. `../run-verdict/references/examples.md` shows a family of
gates for this.

## Verdict

- PASS: observed order approaches the formal order on the finest pairs for every term
  and boundary type tested, within a band set in advance.
- FAIL: order clearly below formal on monotonic data, or error not decreasing.
- INCONCLUSIVE: fewer than three grids, a term or boundary type not exercised, solutions
  not iteratively converged, or no band set in advance. Name the missing coverage.

Bands and formal orders come from the repository's profile or docs; otherwise report the
numbers and INCONCLUSIVE for the pass decision.
