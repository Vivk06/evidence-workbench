# Ledger format

| # | Conflict | Source A | Source B | Recommended ruling | Blocks |
|---|---|---|---|---|---|
| 1 | wall-spacing target | docs/mesh.md:40 says 1e-6 | configs/run.toml:12 sets 5e-6 | config is what ran; update the doc unless the run was wrong | mesh-admission verdict |

Columns: a short name; each source as `path:line` with the conflicting value; the ruling
and why; the work that waits on it ("none" if independent).
