---
name: repo-setup
description: Set up any repository for the workbench - detect its type, propose its AGENTS.md profile, project plugins and Codex rules as one diff, and write only after the owner approves.
metadata:
  tags: [lean]
  output_mode: terminal
---

# Repo setup

Use this skill as `$repo-setup <repo>`. Works for any repository, with or without git,
an `AGENTS.md` or an existing profile.

Command class: `read-only` until the owner approves; writing the approved files is
`safe-local`. Never commit, push or install anything; print those commands.

## Steps

1. Detect: `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/detect_repo.py <repo>` (Codex:
   `../../scripts/detect_repo.py` from this skill's folder). It reads files only and prints
   the archetypes, signals, environment, tests, authority documents, warnings and the
   proposal. An existing profile is kept as written; detection only adds facts it lacks.
2. Review detected facts and any policy choices the user wants. New git repositories
   use `git: normal`. Do not turn test counts into ceilings or impose commit formats.
   Reserved commands, frozen paths and stricter git policies are explicit choices.
3. Show one diff: `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/detect_repo.py <repo> --diff`. It
   covers three files:
   - `AGENTS.md`: frontmatter added or replaced, or a new file;
   - `.claude/settings.json`: project `enabledPlugins`, and allow rules for
     `agent_allowed` commands;
   - `.codex/rules/workbench.rules`: reserved commands that have a `codex_prefix`.
4. After the owner approves the diff: run the same command with `--apply`, or apply
   the edited version with Edit. Then rerun `--diff`; it prints `no changes`.
5. Report each warning the detection found, with its fix. Examples are a `CLAUDE.md`
   that hides `AGENTS.md`, a stale "Claude does not read AGENTS.md" line, and references
   to renamed skills. Propose those edits in the same diff style; never apply them unasked.
6. Print the commands for the owner to run:
   - the plugin enable lines for this repository;
   - the Codex `codex plugin add` lines;
   - optional tools only when the user requested them (`references/tools.md`).
7. Only if the user asks, check the MCP servers and tool plugins:
   `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/mcp_check.py <repo>` (Codex:
   `../../scripts/mcp_check.py`). It reports PASS, FAIL, OPTIONAL or INCONCLUSIVE for
   each tool that fits the repository's archetypes, and the commands that finish each
   gap. It reads the Claude Code and Codex configuration files for this folder and
   `uv tool list`. It starts no server and prints no environment values.
8. To add per-project servers for Codex, show
   `mcp_check.py <repo> --codex-project <names> --diff`. Run it with `--apply` only after
   the owner approves, then remind the owner to trust the folder in Codex. Run step 7
   again; it reports PASS for each tool that is fully set up.

## Refusals

Never write before approval, never overwrite an existing profile's values, and never
guess reserved commands or frozen paths: ask. Never edit the owner's own Claude Code or
Codex configuration; print those commands instead. Never advise approving or trusting a
server that a repository file defines until the owner has seen what it runs. The check
lists each such server with its program. If detection fails or a file it would
change is not valid (for example malformed JSON), report it and stop.
