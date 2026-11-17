---
name: authority-router
description: Find the document that owns a fact, rule or decision via the authority map, profile or code graph before broad search.
metadata:
  tags: [lean]
  output_mode: terminal
---

# Authority router

Command class: `read-only`.

Each fact has one owning document; others link to it. Answer from the owner, and edit
facts only there.

## Find the owner

1. Profile `authority` map, read with
   `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/profile.py <root>` (Codex: `../../scripts/profile.py`):
   keys such as `decisions`, `anti_patterns`, `gates`, `status`, `roadmap`.
2. An authority or "where things live" table in `AGENTS.md`, `CLAUDE.md`, `README.md` or a
   docs index.
3. For code facts: the profile's `code_graph` tool when set (e.g. a graph query), else
   symbol search (`rg`, LSP) over the source, not over docs.
4. Only then a bounded search of the docs tree.

Without a profile, start at step 2; the router works the same in any repository.

## Answer

Give the owning document as `path` and section, the fact with a `path:line` citation, and
how the owner was found (map, table, graph or search). If copies elsewhere disagree with
the owner, list them for the conflict-ledger skill. If two documents both claim to own the
fact, that is itself a conflict: report it, do not choose.

## Refusals

No owner found: say so, name the best candidate and why, and do not present a copy as the
authority.
