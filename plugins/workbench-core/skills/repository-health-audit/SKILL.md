---
name: repository-health-audit
description: Produce a read-only, evidence-based repository maintenance and test-health inventory.
metadata:
  tags: [lean]
  output_mode: terminal
---

# Repository health audit

Command class: `read-only`.

Use this skill as `$repository-health-audit <repo> [--lean]`. Require one explicit,
existing repository path and perform a bounded, read-only inventory. Do not alter the
repository, run cleanup, regenerate files, or change test configuration.

Identify the target activation script (normally `<repo>/activate.sh`) and tell the
user to activate it before any project command; never source it. Solver, MPI,
optimizer, full-tier tests, installs, publishing, and deletion are user-executed.

## Inventory

Classify paths as source, tests, fixtures, generated material, vendored/third-party
content, CI entrypoints, build/configuration, documentation, or unknown. Cite the rules
used for each classification, such as ignore files, generation scripts, package metadata,
licenses and CI configuration. Never mistake generated or vendor content for maintainable
source.

Map test entrypoints and selected tests to their production modules, fixtures,
configuration, CI jobs, and unique failure modes. Then report ownership signals,
duplication candidates, stale/generated material, unreachable tests, unsupported
platform assumptions, and maintenance risk. Findings must name paths, evidence,
confidence, impact, and a recommended next action. Findings are not change requests
and do not authorize deleting, moving, or rewriting anything.

Normal mode returns the report in the conversation unless an output path is explicitly
requested. `--lean` returns only the health summary, cited paths, unresolved gaps, and
one next action. If evidence is insufficient, say `INCONCLUSIVE` rather than infer
ownership, staleness, or deletion safety.
