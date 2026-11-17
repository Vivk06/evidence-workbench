# Multi-fidelity checklist

```
fidelity_id = sha256(case, physics_kind, mesh_sha256, solver_config_hash)
```

| Check | Evidence |
|---|---|
| Fidelity identity | per-sample `fidelity_id`; one id per configuration |
| Duplicates | inode or content hashes of evaluation folders; design-vector hashes |
| Disagreeing repeats | same design, same fidelity, values differing by more than solver tolerance |
| Label admission | status, finiteness and residual criterion per evaluation |
| Exclusion table | sample, fidelity, reason category, evidence path |
| Pooling | training code groups data by `fidelity_id` or models the discrepancy |
| Cost ledger | evaluations by fidelity and status, wall time, core-hours, training time |
| Matched comparison | same design set, budget and stopping rule across compared methods |
