# Mesh admission checklist

Source for quality measures: Knupp, "Algebraic mesh quality metrics", SIAM J. Sci.
Comput. 23 (2001) 193–218.

| Item | Evidence | Fails when |
|---|---|---|
| Volumes and orientation | mesher or solver report | any non-positive volume; reorientation applied silently |
| Quality | min scaled Jacobian, max skewness, max aspect ratio, max non-orthogonality | beyond the project threshold, or non-finite |
| Markers | marker list compared with the solver configuration | a boundary in the config has no marker, or the reverse |
| Wall resolution | first-cell height, `y+` estimate or post-run `y+` | `y+` outside the model's range (about 1 for wall-resolved, 30–300 for wall functions) |
| Layer resolution | cells across a physical layer (boundary, shear, Hartmann) | fewer than the project minimum |
| Adaptive limits | max and min refinement level, cell count | level above the cap; walls not at the floor level |
| Provenance | source geometry, generator and version, SHA-256 | missing, or hash mismatch |
