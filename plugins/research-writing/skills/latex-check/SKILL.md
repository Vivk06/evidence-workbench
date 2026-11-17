---
name: latex-check
description: Check a LaTeX document by handing the build command to the user and then parsing the log for errors, undefined references and citations, and box warnings.
metadata:
  tags: [lean]
  output_mode: terminal
---

# LaTeX check

Command class: `read-only` for the log; the build is handed to the user unless the
user or the repository's instructions let the agent build locally.

## Steps

1. Find the main file (`\documentclass`) and the build the repository documents
   (`latexmk`, a Makefile target, a script). Print one command, for example
   `latexmk -pdf -interaction=nonstopmode -file-line-error main.tex`.
2. After the build, read the `.log` frugally with the patterns in
   `references/log-patterns.md`, and the `.blg` for BibTeX or biber. Look for:
   - errors, with file and line;
   - undefined references and citations, and labels defined more than once;
   - missing files and figures;
   - overfull and underfull boxes above the project's badness threshold.
3. Optional and free: `chktex <file>` for style lints when it is installed.
4. Report each finding with `file:line` and the fix; group repeated warnings.

## Verdict

PASS: no errors, no undefined references or citations, no multiply defined labels. FAIL:
any of those. INCONCLUSIVE: no log for the current sources (the build did not run or the
log predates the last edit). Box warnings are listed, not a failure, unless the project
says otherwise.

## Refusals

Do not silence warnings with `\hbadness`, `\nonstopmode` tricks or deleted citations to
reach PASS.
