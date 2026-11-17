# Example derivative bands

From one discrete-adjoint shape-optimization study; a project sets its own in its profile
or docs.

- Angle-of-attack row: relative error `≤ 1e-4`.
- Shape rows: `≤ max(1e-3, 2e-3·C_r)` capped at 1.0, where `C_r` is the measured cold-start
  repeatability of the functional; a flat `5e-2` when `C_r` has not been measured. Rows
  above the cap are reported as not verifiable.
- Tangential two-dimensional shape modes: not FD-verifiable; reported as limitations.
- An angle-of-attack projection term must be present in shape gradients evaluated at
  fixed lift.
