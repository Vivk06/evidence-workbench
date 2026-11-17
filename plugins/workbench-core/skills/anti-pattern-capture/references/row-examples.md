# Registry row formats

Table registry:

```
| ID | Symptom | Cause | Fix | Detection | Evidence |
| AP-62 | adjoint gradient flips sign after restart | restart file read before mesh deformation | load restart after deformation | step-sweep FD check on restart | logs/fd_restart.txt:14 |
```

List registry:

```
- Wrong: <wrong pattern>. Right: <right pattern>. Symptom: <observed>. Root cause: <cause>.
  Detection: <check>. Evidence: <path:line>.
```

Rule-style registry (`R<n>-<m>`): add the rule under its section with the next number and
cite the evidence that motivated it.
