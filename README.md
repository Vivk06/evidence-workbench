# evidence-workbench

evidence-workbench gives Claude Code and Codex reusable audits for scientific software,
machine learning and research. Each audit reports PASS, FAIL or INCONCLUSIVE and cites
its supporting files or logs.

Use it to review simulation convergence, check experiments for data leakage, or trace
reported numbers to their data. Choose one plugin and use its skills in your project.
Profiles, workflow conventions and extra tools are optional.

## Start with one plugin

For an ML experiment audit in Claude Code, run:

```bash
claude plugin marketplace add Vivk06/evidence-workbench
claude plugin install ml-validity@evidence-workbench --scope user
claude plugin enable ml-validity@evidence-workbench --scope project
```

Then start a session in your project and ask:

```text
/ml-validity:ml-experiment-audit Review the experiment in this repository.
```

For Codex, run:

```bash
codex plugin marketplace add Vivk06/evidence-workbench
codex plugin add workbench-core@evidence-workbench
codex plugin add ml-validity@evidence-workbench
```

Then ask `$ml-experiment-audit` to review your experiment. No repository setup is required.
Your existing coding agent and its usual usage costs still apply.

## Choose what you need

| Plugin | Use it for |
| --- | --- |
| `sim-validity` | simulation convergence, conservation, meshes, gradients and validation |
| `ml-validity` | data leakage, split design, results provenance and copied code |
| `research-writing` | readable documents, evidence maps, citations and prose checks |
| `workbench-core` | repository audits, planning, scoped edits and optional policy hooks |
| `workbench` | an optional bundle that installs all four plugins |

The domain plugins use workbench-core for shared workflow skills. Claude Code installs
that dependency; Codex users add it explicitly. Paper processing needs a separate,
optional plugin. Writing and audits work without it.

## Configure only when needed

Skills follow your repository's instructions. New profiles use normal git permissions
and impose no test ceiling, commit format or session schedule. A profile can reserve
commands for you or protect selected paths. Without a profile, the hooks do nothing.

[Getting started](docs/getting-started.md) covers installation, updates and optional setup.
[Workflow options](docs/workflow.md) explains profiles and stricter policies.

## Limits and maintenance

Most skills are instructions for an agent; selected checks also have local scripts.
A verdict depends on the evidence supplied and the agent's review. Missing evidence
means INCONCLUSIVE. These skills support human review and do not certify a scientific result.

- [Skill catalog](docs/skills.md)
- [Optional paper integration](docs/getting-started.md#optional-paper-processing)
- [Optional tools](docs/optional-tools.md)
- [Maintenance and local checks](docs/maintaining.md)
- [Changelog](CHANGELOG.md)

The plugins use the MIT license. Bundled third-party material keeps its own license
and notices. No extra service is required for the local checks.
