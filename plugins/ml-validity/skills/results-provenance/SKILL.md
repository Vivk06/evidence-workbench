---
name: results-provenance
description: Trace every reported number in tables, figures and READMEs back to a data file and the script that generated it, regenerate marked result blocks, and flag protocol differences.
metadata:
  tags: [lean]
  output_mode: terminal
---

# Results provenance

Command class: `read-only` for tracing. Running a table or figure script is `safe-local`
when it reads committed result files and writes only the marked block it owns. Otherwise
it is `user-execution`.

## Steps

1. Inventory reported numbers: tables, figure captions, README result blocks, papers and
   reports.
2. For each number, find its source row (CSV, JSON, log) and the generating script; record
   them in the format of `references/provenance-table.md`.
3. Regenerate the marked blocks with the repository's own script, and compare the result
   with the committed text. Any difference is a finding. A marked block is, for example,
   the text between `<!-- results:start -->` and `<!-- results:end -->`.
4. Flag protocol differences between numbers placed side by side: different splits, noise
   or augmentation protocols, metric definitions, checkpoints or units.
5. Flag the same quantity reported with different values, and numbers that are upper
   bounds or oracle settings presented without that caveat.

## Verdict

- PASS when every reported number traces to a source and a script, and regenerated
  blocks match.
- FAIL on a mismatch or an unflagged protocol difference.
- INCONCLUSIVE when a number has no source you can find. List it.

## Refusals

Never edit a reported number to match a source, or the reverse, without the user's
ruling (conflict-ledger skill).
