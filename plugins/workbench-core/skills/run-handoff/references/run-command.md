# Run command shape

```
<activation> && <prefix> <launcher> <program> <config> <output option> [2>&1 | tee logs/run_<topic>.log]
```

Checks before printing:

1. One line; no trailing comment; copy-pasteable from the repository root.
2. Every path exists or is the new output path you named.
3. The output path is new; a run is never removed or overwritten until archived and
   verified by the user's own procedure.
4. Resource numbers (ranks, threads, GPUs) are stated, not left to defaults the user
   cannot see. Rank or thread count is provenance, never a cause of a result.
5. `tee` only when the run does not write its own log.

Then list: expected duration if known, the files to bring back, and the gate each feeds.
