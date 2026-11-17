# Maintaining the workbench

This guide covers the repository's layout, its checks and its releases. It also lists
the Claude Code and Codex facts the plugins depend on. The rules for agents working here are
in [`AGENTS.md`](../AGENTS.md). The shared principles are in [principles.md](principles.md).

## Layout

| Path | What it contains |
| --- | --- |
| `.claude-plugin/marketplace.json` | the marketplace: the five plugins and the old name `cfd-plugin` mapped to `workbench` |
| `plugins/<name>/` | one plugin each: `.claude-plugin/plugin.json` and `skills/`; workbench-core also has `hooks/`, `scripts/`, `profiles/templates/` and `agents/` |
| `manifest/policy.yaml` | the three command classes and the rules for keeping data |
| `manifest/external-plugin-admission.yaml` | every outside tool considered, with its decision; anything not listed is rejected, and only free tools qualify |
| `scripts/` | `check.sh` (all checks), `verify.sh` (static checks), `validate-manifest.py`, `print-install.sh` and `prepare-public.py` |
| `hooks/pre-push` | runs `scripts/check.sh` before each push, once `git config core.hooksPath hooks` is set |
| `tests/` | the test suite, at most 20 tests, and `fixtures/` with sample repositories, profiles, run logs and texts |
| `docs/` | this guide, getting started, the skill catalog, workflow choices and optional tools |
| `logs/` | the commit message file for the change in progress |

## Checks

`bash scripts/check.sh` runs every check. The checks run locally without model calls or paid services.
Install Python 3.9 or later and pytest before running them. Claude Code validation
runs when the `claude` command is available.

1. `scripts/verify.sh` checks the required files, the policy manifest and the admission
   file. It checks that Codex can still load the marketplace. Each `plugin.json` must have
   the version in `VERSION`, the MIT license and the root `LICENSE`. It also checks skill
   frontmatter, scans tracked files for secrets, and runs `claude plugin validate --strict`
   when `claude` is installed.
2. `pytest tests` covers the guard and profiles, the checkers' verdicts on fixtures,
   repository detection and the skill contracts. It also covers the plugin inventory and
   generality: shipped plugins name no owner repository and cite no internal codes.
3. `audit_tests.py . --check` keeps the suite within its budget.

Public source hosting and catalog submission are separate steps. Use ordinary plugin
validation for this marketplace; catalog-specific validation applies only to a catalog submission.

## Add or change a skill

- Put each skill in its own folder, `plugins/<plugin>/skills/<name>/`, with a `SKILL.md`.
  Detail goes in `references/`, and scripts go in `scripts/`.
- Keep the body under about 60 lines, and the description under 200 characters. Claude
  Code loads every description in every session.
- The body states `Command class: \`read-only\`` (or `safe-local` or `user-execution`). It
  has a `## Refusals` section or an INCONCLUSIVE path.
- The skill works in any repository without a profile. If it reads a profile, it says
  what it does without one.
- Shipped text names no owner repository and cites no `D` or `R` codes. An installed
  plugin carries no copy of these docs, so state the rule itself.
- Call scripts as `${CLAUDE_PLUGIN_ROOT}/...` for Claude Code. For Codex, give the path
  relative to the skill folder, because Codex does not fill in that variable.
- Run the plain-language checker on the new text, and fix every must-fix finding:
  `python3 plugins/research-writing/skills/plain-language/scripts/check.py <file>`.
- Add the skill to `tests/test_skill_contracts.py`, `tests/test_inventory.py`, the skill catalog
  table and `CHANGELOG.md`.

## Release

1. Bump `VERSION` and the version in every `plugins/*/.claude-plugin/plugin.json`. Add a
   `CHANGELOG.md` section.
2. Run `bash scripts/check.sh`.
3. Merge the branch into `main`. Fetch first, because a clone that has never fetched the
   branch cannot merge it:

   ```bash
   git fetch origin main <branch>
   git checkout main
   git merge --ff-only origin/main
   git merge --ff-only origin/<branch>
   cat VERSION
   git push origin main
   ```

4. Tag only when `cat VERSION` prints the new version. Otherwise the tag command finds the
   old version's tags and stops:

   ```bash
   for p in workbench-core sim-validity ml-validity research-writing workbench; do claude plugin tag plugins/$p --push; done
   ```

   Tags are named `<plugin>--v<version>`; `--dry-run` shows them without creating them.
   Never pass `--force`, which moves an existing tag.
5. Users update with the commands in [getting started](getting-started.md#update).

## Platform facts the plugins depend on

These facts were checked on 2026-10-25 against Claude Code 2.1.310 and the Codex source.
These are recorded compatibility observations, rather than a guarantee for later clients.
Recheck the affected behavior when changing client integration.

### Claude Code

- Component paths in `plugin.json` start with `./` and stay inside the plugin. A `..` in
  a path is an error.
- Claude Code does not load a `CLAUDE.md` at a plugin's root, and `validate` warns about
  one.
- Set `version` only in `plugin.json`, not also in the marketplace entry.
- `defaultEnabled: false` keeps a plugin installed but turned off. A plugin that an
  enabled plugin depends on is turned on anyway. That is why `workbench` stays off:
  turning it on would turn on all four plugins in every repository.
- Paper processing is installed separately. This marketplace declares no external
  plugin dependency.
- The marketplace's `renames` list only grows. Use it for any later plugin rename.
- A PreToolUse hook receives `tool_name` and `tool_input`. The input holds `command` for
  `Bash`, `file_path` for `Edit` and `Write`, and `notebook_path` for `NotebookEdit`.
- The guard blocks a call with `hookSpecificOutput.permissionDecision: "deny"` and a
  reason that the agent sees.
- A hook command written as a shell string must put `"${CLAUDE_PLUGIN_ROOT}"` in double
  quotation marks.
- Claude Code 2.1.277 and later reads `AGENTS.md`, but only when there is no `CLAUDE.md`,
  `.claude/CLAUDE.md` or `CLAUDE.local.md` in the working folder or above.
- Background updates of a private marketplace are off by default. They use the git
  credential helper or `ssh-agent`; a `GITHUB_TOKEN` alone does not work.

### Codex

- Codex reads `.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json` when
  there is no `.codex-plugin/` or `.agents/plugins/` file. `validate-manifest.py` fails
  if such a file appears, because Codex would read it instead of the Claude file.
- A local plugin source must start with `./`. Codex has no `github` source object and no
  dependencies, so each plugin needs its own `codex plugin add` command.
- Plugin hooks use the same `hooks/hooks.json`. The shell tool is `Bash`.
- Codex sends edits as `apply_patch`, with the patch text in `tool_input.command`. The
  `*** Add File:`, `*** Update File:` and `*** Delete File:` lines name the target paths.
- Codex sets `CLAUDE_PLUGIN_ROOT` but not `CLAUDE_PROJECT_DIR`. The guard uses the `cwd`
  field from its input instead.
- Plugin hooks run only after the user approves them, and again after each plugin update.
- Exec-policy rules, `prefix_rule(..., decision="forbidden")` in `<repo>/.codex/rules/`,
  back up the guard. `repo-setup` writes them from each `user_executed` entry's
  `codex_prefix`.

### MCP servers

The optional tools guide depends on these facts. They were checked on 2026-10-27 against
`claude mcp --help` in Claude Code 2.1.311 and the Codex source at commit `6fe77fc`.

- `claude mcp add` has three scopes:
  - `local`, the default: this folder, for you only;
  - `project`: `.mcp.json` at the project root, shared through git;
  - `user`: every folder.

  Claude Code asks before it starts a server from `.mcp.json`.
- `claude mcp remove <name>` without `--scope` removes the server from whichever scope
  holds it.
- `codex mcp add` writes only to `~/.codex/config.toml`, so the server is on everywhere.
  It takes `--env KEY=VALUE` and the command after `--`.
- Codex also reads `mcp_servers` tables from a project's `.codex/config.toml`, but only
  when the folder is trusted (`trust_level = "trusted"` under `[projects."<path>"]`).
  An untrusted folder's project file is ignored. Codex looks upward from the starting folder to the project root, which `.git` marks.
  A session started in a subfolder still finds the root's `.codex/config.toml`.
- `claude mcp add --scope project` writes `.mcp.json` into the folder it runs in, not
  the git root. Claude Code finds a root `.mcp.json` from a subfolder, but a session
  started at the root does not see a `.mcp.json` written in a subfolder. Tested on
  2026-10-27 with Claude Code 2.1.311 in a scratch git repository.

The pinned versions appear in `docs/optional-tools.md` and in
`plugins/workbench-core/skills/repo-setup/references/tools.md`, which installed plugins
carry. `scripts/verify.sh` fails when the two disagree, so change both together.
