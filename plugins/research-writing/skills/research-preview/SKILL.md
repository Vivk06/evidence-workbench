---
name: research-preview
description: Preview explicitly scoped documentation sources with citations and no writes.
metadata:
  tags: [lean]
  output_mode: terminal
---

# Research preview

Use this skill as `$research-preview <sources> <question>`.

Command class: `read-only`. Inventory and preview only: no context files, plugin
installs, paper retrieval, corpus changes or user-configuration writes.

## Inputs

Explicit source paths and a bounded question. Personal data, home-directory scans,
credentials, databases, papers and caches are read only when the user allowlists each
path.

## Steps

Use the repository's own documentation search when it has one; otherwise a bounded
search such as
`rg -n --glob 'README*' --glob 'docs/**' --glob '*AGENTS.md' --glob '*CLAUDE.md' '<terms>' <source>`.

## Output

A short source-ranked preview: paths with line anchors, scope, unresolved gaps, and the
statement `no write performed`.

## Refusals

Installation, network retrieval, corpus writes and personal-data access go to the user as
one exact command with an explicit output path. Paper work routes through the
research-router skill.

## Lean mode

With `--lean` or a terminal-only request, follow the lean-output skill: print the
preview only, and write no file.
