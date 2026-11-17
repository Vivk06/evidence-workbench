<!-- working file: conclusions in solver-choice.md -->
# Evidence map: which linear solver should the adjoint use?

| ID | Kind | Statement | Links | Source |
|---|---|---|---|---|
| P1 | position | Use GMRES with an ILU(0) preconditioner for the adjoint | | |
| C1 | claim | GMRES converges on every case we ran | supports P1 | |
| C2 | claim | ILU(0) fits in memory on the fine mesh | supports P1 | |
| E1 | evidence | All 12 cases reached a residual drop of 1e-8 | supports C1 | logs/adjoint-sweep.csv:2 |
| E2 | evidence | Case 7 needed 3 restarts at the default restart length | qualifies C1 | logs/case07.log:880 |
| E3 | evidence | Peak memory was 41 GB of 64 GB on the fine mesh | supports C2 | ledger:L1 |
| U1 | unknown | Behaviour at angles of attack above 12 degrees | missing C1 | |
