# Principles

The workbench helps an agent support its conclusions with evidence. Project instructions
and explicit user requests decide workflow policy.

## Cite the evidence

Report PASS, FAIL or INCONCLUSIVE for an audit. Cite the file, data column or log line
behind the result. Missing evidence means INCONCLUSIVE. Distinguish local script results
from an agent's judgment. Never weaken a check to make a result pass.

A successful solver exit does not establish convergence, conservation or agreement with
an experiment. Use the project's numerical and physical checks.

## Keep changes bounded

Read only the project and sources named by the user. Make changes needed by the task,
respect frozen paths and keep unrelated files intact. Expensive runs, installation and
publishing need explicit authorization. A prepared command is not evidence of a run.

## Inherit project policy

Use the project's permissions, commit format, document style and test policy. Profiles
can add restrictions; they are optional. New profiles do not invent a test ceiling or
require read-only git. Session restarts, patch series and fixed handoff formats are
available when the user or project needs them.

## Keep documents useful

Give each fact an owning document and link to it from elsewhere. Write for the intended
reader, state limits and preserve source attribution. Move current facts before cutting
a document. History belongs in git; public exports must exclude private history.

## Keep integrations optional

Local audits and writing work without a paper-processing plugin or extra servers.
Install outside tools only on request. Retain bundled material's licenses and notices.
Source data, paper collections, personal settings and transcripts stay outside plugins.
