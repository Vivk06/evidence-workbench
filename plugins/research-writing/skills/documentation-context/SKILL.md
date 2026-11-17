---
name: documentation-context
description: Build cited documentation context from an explicit corpus or bounded repository search.
metadata:
  tags: [lean]
  output_mode: terminal
---

# Documentation context

Use this skill as `$documentation-context corpus|repo-search ...`.

Command class: `read-only`; terminal output unless the user passes `--write <path>`.

## Modes

- `corpus`: a cited function context from user-approved documentation paths:
  `bash ${CLAUDE_PLUGIN_ROOT}/skills/documentation-context/scripts/documentation-context.sh corpus --sources <paths> --function <question> --lean`
- `repo-search`: a bounded context packet from one explicit repository root:
  `bash ${CLAUDE_PLUGIN_ROOT}/skills/documentation-context/scripts/documentation-context.sh repo-search --repo <root> --question <question> --lean`

Codex: `scripts/documentation-context.sh` in this skill's folder. Packets follow
`references/context-schema.md`; privacy rules are in
`references/privacy-and-redaction.md`; defaults in `docs-context/`.

## Refusals

Never infer a source root, scan `$HOME`, read personal data, run tests, edit source or
create artifacts. Personal data is read only when every path is passed with
`--personal-data allowlisted`. `--write` needs an explicit output path and writes only
that path. A question the sources cannot answer is reported as an unresolved question,
never filled in.

## Lean mode

With `--lean` or a terminal-only request, follow the lean-output skill: print the packet
only, and write no file.
