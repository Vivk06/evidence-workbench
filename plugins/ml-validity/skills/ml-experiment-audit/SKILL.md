---
name: ml-experiment-audit
description: Audit an ML experiment for leakage, split design, test-set discipline, preprocessing fit scope, seed variance, exclusions and label definitions before trusting its metrics.
metadata:
  tags: [lean]
  output_mode: terminal
---

# ML experiment audit

Command class: `read-only`. Training and evaluation runs are `user-execution` and
go through the run-handoff skill.

Work through `references/checklist.md` and cite each finding as `path:line`, a data file
and column, or a log line.

## Checks

1. Leakage: no sample, duplicate or alias of a sample is in more than one split. No
   feature comes from the target or from future information. No test data feeds
   normalisation, feature selection or early stopping.
2. Split design: grouped splits when samples share a source (subject, repeat, trajectory,
   simulation family, near-duplicate); the grouping key is stated.
3. Test-set discipline: the test set is fixed before model selection, and evaluated once
   per reported model. Choices made after looking at test results are reported as such.
4. Fit scope: scalers, PCA, imputers, feature selection and hyperparameters see training
   (and validation) data only.
5. Seeds and variance: results cover at least three seeds or folds, with their spread.
   A gain from one seed that is smaller than the seed spread is not a gain.
6. Exclusions: every excluded or failed sample is in an exclusion table with its reason;
   failures are never encoded as extreme label values.
7. Labels and metrics: each comparison uses one label definition. The metric and the
   acceptance tolerance are fixed before the test set is evaluated. Baselines are
   trained and evaluated under the same protocol.

## Verdict

- PASS when every applicable check holds with evidence.
- FAIL on leakage, a test set used for selection, or mismatched protocols.
- INCONCLUSIVE when split files, seeds or preprocessing code that a check needs are
  missing. Name them.
