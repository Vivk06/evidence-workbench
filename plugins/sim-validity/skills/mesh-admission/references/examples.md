# Example mesh thresholds

Illustrations from real studies; a project sets its own.

- Adaptive octree magnetohydrodynamics case:
  - `lmax ≤ MAXLEVEL`, and walls at their nominal position within 1e-12;
  - at least 5 cells across each exponential layer, with thicknesses `δ_H = 1/Ha` for
    Hartmann layers and `δ_side = sqrt(a/Ha)` for side layers;
  - adaptive runs keep wall cells at the floor level and use fewer cells than the static
    mesh.
- Anisotropic tetrahedral adaptation: reject a change that drops the conforming-element
  share below 71 % or the mean quality below 0.25 on the reference case.
- External-aerodynamics RANS: first-cell `y+ ≈ 1` for low-Reynolds turbulence models.
