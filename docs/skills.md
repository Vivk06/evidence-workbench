# Skill catalog

In Claude Code, type `/<skill>` or `/<plugin>:<skill>`. In Codex, type `$<skill>`. You can
also ask in plain words, and the agent picks the skill from its description. Skills read
only the paths you give them. They hand anything expensive, or anything outside the
repository, to you.

## workbench-core

| Skill | What it does |
|---|---|
| `repo-setup` | finds a repository's facts and proposes its profile and settings as one change |
| `plan-forge` | writes or revises a plan in phases |
| `phase-exec` | carries out one phase of a plan, with its checks and a handoff |
| `surgical-edit` | makes the smallest edit, within a stated limit on what it may change |
| `handoff` | writes the commit message file, a patch series and a short note for the next session |
| `run-handoff` | gives you one complete command for an expensive run, and names the evidence to bring back |
| `codex-delegate` | writes a prompt file and prints one read-only `codex exec` command, then checks what Codex cites |
| `test-value-audit` | measures the test suite against its budget and finds low-value and duplicate tests |
| `repository-health-audit` | lists structure, tests, generated and copied-in code, and maintenance risks |
| `decision-record` | adds or amends a decision in the repository's own format |
| `anti-pattern-capture` | records a known mistake with a stable ID |
| `conflict-ledger` | lists sources that disagree, with both citations and a recommended ruling |
| `docs-distill` | rewrites documents to the current state without losing facts |
| `authority-router` | finds the document that owns a fact before searching widely |
| `workstation-bootstrap` | checks that this machine has the tools a repository needs |
| `token-lean` | keeps long sessions within the amount of text the model can hold at once |
| `lean-output` | short, cited reports in the terminal, with no files written |

## sim-validity

| Skill | What it does |
|---|---|
| `run-verdict` | decides whether a finished run is valid against the project's checks |
| `inspect-run` | reads a run's status, origin and log ends without changing it |
| `solution-verification` | checks convergence as the mesh and iterations are refined, and estimates the remaining error |
| `code-verification` | compares the code with exact or manufactured solutions and checks its order of accuracy |
| `conservation-audit` | checks that mass, momentum and energy balance, globally and cell by cell |
| `solver-health` | looks for non-finite values, limiters, time-step limits and other signs of a sick solver |
| `validation-comparison` | compares simulation with experiment, including both uncertainties (the V&V 20 standard of the American Society of Mechanical Engineers) |
| `mesh-admission` | admits a mesh on quality, orientation, resolution and origin |
| `derivative-audit` | checks adjoint or automatic-differentiation gradients against finite differences |
| `sim-code-development` | scopes a solver change, keeps existing behavior and verifies it in proportion |
| `verify-fast` | runs the repository's own fast checks and reports PASS or FAIL |

## ml-validity

| Skill | What it does |
|---|---|
| `ml-experiment-audit` | checks for leakage, grouped splits, a frozen test set, seeds and labels |
| `results-provenance` | traces every reported number to its data and script |
| `third-party-audit` | checks copied-in code for licenses, attribution, versions and matching results |
| `multifidelity-data-audit` | keeps data of different fidelity apart and compares only matching cases |

## research-writing

| Skill | What it does |
|---|---|
| `reader-distill` | turns scattered agent notes and logs into a few readable documents, keeping every fact |
| `plain-language` | writes or checks prose by the ISO 24495 plain-language rules, with a local PASS or FAIL checker |
| `evidence-map` | connects claims into one argument: the answer, its claims, evidence for and against, and unknowns |
| `claims-ledger` | traces every factual claim to a source and the date it was read |
| `latex-check` | hands you the build command, then reads the log for errors and missing references |
| `analysis-note` | writes a self-contained note on one problem for a first-year master's student |
| `application-dossier` | builds program and faculty dossiers from cited sources |
| `documentation-context` | collects cited context from named sources or a bounded repository search |
| `research-preview` | previews named sources with line numbers and writes nothing |
| `research-router` | sends paper retrieval and reading to the `research-papers` plugin |
| `stop-slop` | removes AI writing habits from prose (included unchanged, MIT, by Hardik Pandya) |

The three reader skills work together. Agents keep working files, such as notes, logs and
ledgers. `reader-distill` moves their facts into a few documents for people, and
`plain-language` checks each one. `evidence-map` shows how the claims behind a conclusion
connect.

A working file starts with `<!-- working file: conclusions in <path> -->`, so a reader
knows they never need to open it. The plain-language checker is adapted from
[auxesis/plain-language-skill](https://github.com/auxesis/plain-language-skill)
(Apache-2.0). The checker's NOTICE file lists the changes.

