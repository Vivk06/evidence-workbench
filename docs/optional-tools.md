# Optional tools

MCP (Model Context Protocol) servers give the agent extra tools, such as searching your
Zotero library. None of them is required, and every one listed here is free and runs on
your machine. Each server adds its tool descriptions to every session where it is on, so
turn a server on only where you use it. Installing is always your step. An agent only
prints these commands.

| Server | Use it for | Where to turn it on |
|---|---|---|
| Zotero MCP | search your Zotero library, its notes and annotations | everywhere |
| MarkItDown MCP | convert PDF, Word, PowerPoint, Excel and HTML files to Markdown | everywhere |
| Serena | find and edit code by symbol name, through language servers | one code project at a time, while on trial |
| Playwright MCP | read web pages that need JavaScript to show their content | one project, only while you need it |

Set them up in the order of the steps below.

## Step 1: install the programs

Do this once per machine. The programs then exist for your user account; step 2 decides
where Claude Code and Codex use them.

1. Install uv, which installs the Python-based servers:
   `curl -LsSf https://astral.sh/uv/install.sh | sh`
2. Put the programs uv installs on your path: run `uv tool update-shell`, then open a new
   terminal.
3. Install the three Python-based servers:

   ```bash
   uv tool install zotero-mcp-server==0.15.1
   uv tool install markitdown-mcp==0.0.1a8
   uv tool install -p 3.13 serena-agent==2.1.0
   ```

4. For Playwright only, install Node.js 18 or later. `npx` downloads Playwright the first
   time the server starts.
5. For Zotero only: in Zotero 7 or later, open Settings, then Advanced. Tick "Allow other
   applications on this computer to communicate with Zotero". Keep Zotero open while you
   use the server.

## Step 2: choose where each server is on

| Level | Claude Code | Codex |
|---|---|---|
| everywhere | `claude mcp add --scope user ...` | `codex mcp add ...`, which writes `~/.codex/config.toml` |
| one project, for you only | `claude mcp add ...` from the project's root folder | the project's `.codex/config.toml`, kept out of git |
| one project, shared through git | `claude mcp add --scope project ...`, which writes `.mcp.json` | the project's `.codex/config.toml`, committed |

- Codex has no scope option. `codex mcp add` always turns a server on everywhere.
- Codex reads a project's `.codex/config.toml` only when you trust that folder. Codex
  asks the first time you start it in the folder. You can also add
  `[projects."/absolute/path"]` with `trust_level = "trusted"` to `~/.codex/config.toml`.
  In a folder you have not trusted, the project's servers are ignored without a message.
- Claude Code asks you to approve the servers in a project's `.mcp.json` before it starts
  them, because that file comes from git.
- If Claude Code has one server name at several levels, the narrowest level wins: the
  project for you only, then the shared project, then everywhere.
- Run every per-project command from the project's root folder, the folder where you
  start your sessions. `claude mcp add --scope project` writes `.mcp.json` into the
  folder you run it in. Claude Code finds a root `.mcp.json` from any subfolder, but not
  a file that was written inside a subfolder.

## Step 3: turn on the servers you want everywhere

Run these once, from any folder:

```bash
claude mcp add zotero --scope user -e ZOTERO_LOCAL=true -- zotero-mcp
claude mcp add markitdown --scope user -- markitdown-mcp
codex mcp add zotero --env ZOTERO_LOCAL=true -- zotero-mcp
codex mcp add markitdown -- markitdown-mcp
```

Keep Zotero read-only: do not run `zotero-mcp authorize-local`, and do not add a Zotero
API key. MarkItDown talks to the agent through standard input and output. If you ever
start it with `--http`, keep the host as `127.0.0.1` so no other machine can reach it.

## Step 4: turn on the servers you want in one project

For Claude Code, run these from the project's root folder:

```bash
claude mcp add serena -- serena start-mcp-server --context claude-code --project "$(pwd)"
claude mcp add playwright -- npx @playwright/mcp@0.0.83
```

Add `--scope project` after `add` to share a server through the project's `.mcp.json`.
Run it from the root folder too, so the file lands where every session finds it.
To have Serena everywhere instead, use
`claude mcp add --scope user serena -- serena start-mcp-server --context claude-code --project-from-cwd`.

For Codex, create `.codex/config.toml` in the project's root folder with the servers it
needs, then trust the folder as step 2 describes:

```toml
[mcp_servers.serena]
command = "serena"
args = ["start-mcp-server", "--project-from-cwd", "--context=codex"]

[mcp_servers.playwright]
command = "npx"
args = ["@playwright/mcp@0.0.83"]
```

To keep that file to yourself, add the line `.codex/config.toml` to the project's
`.git/info/exclude`. The repo-setup skill writes `.codex/rules/workbench.rules` in the
same folder, and the two files do not conflict.

## Step 5: check the servers

The repo-setup skill checks everything in steps 1 to 4 for one project. In a session at
the project's root folder, ask for `/repo-setup .`. Or run the check yourself from the
project's root folder, with the path of your evidence-workbench clone:

```bash
python3 <evidence-workbench clone>/plugins/workbench-core/scripts/mcp_check.py .
```

The check reads the Claude Code and Codex configuration files for that folder and
`uv tool list`. It starts no server and prints no secret. For each tool that fits the
project, it reports one status:

| Status | Meaning |
|---|---|
| PASS | set up as recommended |
| FAIL | a needed part is missing or unsafe, such as a Zotero entry with an API key |
| OPTIONAL | a per-project tool that is not set up here, which is fine |
| INCONCLUSIVE | a configuration file could not be read |

Each line that is not PASS names the commands that finish it. For Codex's per-project
servers, the check can also write the project's `.codex/config.toml` for you.
`--codex-project serena,playwright --diff` shows the change, and `--apply` writes it.

To check by hand instead:

1. Start a new session. Claude Code and Codex load servers only when a session starts.
2. In Claude Code, run `claude mcp list` from the project folder. It shows every server
   on there, at all levels, and `claude mcp get <name>` shows a server's level. In a
   session, `/mcp` shows whether each server is connected.
3. In Codex, `codex mcp list` shows the servers that are on everywhere. To check a
   project's servers, start Codex in that folder and look for them in its list of tools.
4. Ask each server for one real thing:
   - Zotero: "Find papers in my Zotero library about adjoint methods."
   - MarkItDown: "Convert `docs/spec.pdf` to Markdown."
   - Serena: "Find every caller of `compute_residual`."
   - Playwright: "Open this page and summarize it."

| Problem | Fix |
|---|---|
| "command not found" for `zotero-mcp`, `markitdown-mcp` or `serena` | run `uv tool update-shell`, then open a new terminal |
| Zotero connects but finds nothing | open Zotero, and check the setting from step 1 |
| Serena shows as failed in `/mcp` | add `export MCP_TIMEOUT=60000` to your shell profile, then start a new session |
| A project's servers are missing in Codex | trust the folder, as step 2 describes |
| A server is missing in Claude Code | start the session in the folder where you added it, or add it with `--scope user` |

## Update or remove a server

The versions are pinned, so an update is your decision. To update a Python-based server,
uninstall it and install the new version. The registrations from steps 3 and 4 stay
valid, because they name the program, not its version:

```bash
uv tool uninstall zotero-mcp-server
uv tool install zotero-mcp-server==<new version>
```

To update Playwright, change the version number in its `claude mcp add` command and in the
Codex file. To remove a server, run `claude mcp remove <name>`, which finds it at
whichever level it is on. Also run `codex mcp remove <name>`, or delete its table from the
project's `.codex/config.toml`. Then run `uv tool uninstall <package>`.

## Plugins and command-line tools

pyright-lsp reports Python type errors after each edit, in Claude Code. session-report
shows how many tokens each session spent. Both come from Anthropic's official
marketplace:

```bash
claude plugin marketplace add anthropics/claude-plugins-official
uv tool install pyright==1.1.414
claude plugin install pyright-lsp@claude-plugins-official --scope project
claude plugin install session-report@claude-plugins-official --scope user
```

Skip the first command if `claude plugin marketplace list` already shows
`claude-plugins-official`. The pyright package downloads Node.js the first time it runs,
if Node.js is not installed. Run the pyright-lsp install from the root folder of one
project first, because `--scope project` applies to the folder you run it in. Check its messages
there before you turn it on in others.

Four command-line tools need no setup in Claude Code or Codex. The agent runs them when
they are installed:

- [pandoc](https://pandoc.org) converts between Markdown, LaTeX and Word.
- [graphify](https://github.com/safishamsi/graphify) builds a local map of a repository's
  code. Name it in the profile as `code_graph`.
- [recov](https://github.com/jirikuncar/recov) finds tests that other tests already
  cover. It runs the whole suite, so you run it in repositories with slow tests.
- [Vale](https://vale.sh) checks prose against a style guide. Use it in repositories that
  already have a `.vale.ini` file.

[`manifest/external-plugin-admission.yaml`](../manifest/external-plugin-admission.yaml) lists every tool considered for the workbench,
with its version, license and the reason for the decision.

