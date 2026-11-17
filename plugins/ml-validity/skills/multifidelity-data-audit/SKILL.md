---
name: multifidelity-data-audit
description: Audit multi-fidelity simulation datasets and surrogate studies - fidelity identity from config hashes, duplicate evaluations, no pooling across fidelities, matched comparisons and a full cost ledger.
metadata:
  tags: [lean]
  output_mode: terminal
---

# Multi-fidelity data audit

Command class: `read-only`.

## Checks (`references/checklist.md`)

1. Fidelity identity: a hash of what makes a sample its fidelity defines its level, not
   a folder name. The hash covers the case, physics model, mesh hash and solver settings.
2. Duplicates: remove hard-linked or copied evaluation folders, and repeated evaluations
   of one design, before counting or splitting. Repeats that disagree are a finding.
   Never average them or absorb them into a noise term.
3. Labels come only from evaluations that finished, are finite and met their convergence
   criteria. Failures go to an exclusion table, never into the data as extreme values.
4. No pooling: never mix data from different fidelities as one source, unless the method
   includes a model of the discrepancy.
5. Matched comparisons: a claim about speed-up or accuracy compares methods on the same
   designs, budget and stopping rule. The cost ledger counts every evaluation, including
   failed and discarded ones, and the training cost.
6. Claims: a surrogate prediction is reported as a prediction, never as a high-fidelity
   result; synthetic data is labelled.

## Verdict

- PASS when every check holds with evidence.
- FAIL on pooling, unmatched comparisons, or surrogate output reported as simulation.
- INCONCLUSIVE when hashes, logs or the cost ledger are missing.
