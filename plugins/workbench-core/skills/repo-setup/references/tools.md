# Free tools by archetype

Every tool here is free, runs locally, and has no metered usage or rate-limited quota.
Installing and turning a tool on is the owner's step; print these commands, never run
them. Print only the tools that match the repository's archetypes.

| Archetype | Tool | Always-on cost | Where to turn it on |
|---|---|---|---|
| all | session-report plugin | about 75 tokens | everywhere |
| code | pyright-lsp plugin | 0 | one project first; check its messages |
| code | serena (MCP) | its tool descriptions | one project at a time, while on trial |
| code | recov (command line) | 0 | runs the whole suite, so the owner runs it where tests are slow |
| code, physics | graphify (command line) | 0 | named in the profile as `code_graph` |
| research | zotero-mcp (MCP) | its tool descriptions | everywhere; read-only |
| research | markitdown-mcp (MCP) | one tool | everywhere |
| research | pandoc (command line) | 0 | needs no setup |
| research | playwright-mcp (MCP) | its tool descriptions | one project, only while needed |

Plugins per archetype: sim-validity for physics, ml-validity for code with machine
learning signals, and research-writing for research. workbench-core is always on.

## Install the programs once per machine

```bash
uv tool install zotero-mcp-server==0.15.1
uv tool install markitdown-mcp==0.0.1a8
uv tool install -p 3.13 serena-agent==2.1.0
uv tool install pyright==1.1.414
```

uv itself comes from `curl -LsSf https://astral.sh/uv/install.sh | sh`, followed by
`uv tool update-shell` and a new terminal. Playwright needs Node.js 18 or later. Zotero
needs "Allow other applications on this computer to communicate with Zotero" ticked in
its Settings, under Advanced.

## Servers that are on everywhere

```bash
claude mcp add zotero --scope user -e ZOTERO_LOCAL=true -- zotero-mcp
claude mcp add markitdown --scope user -- markitdown-mcp
codex mcp add zotero --env ZOTERO_LOCAL=true -- zotero-mcp
codex mcp add markitdown -- markitdown-mcp
```

Keep Zotero read-only: no `zotero-mcp authorize-local` and no Zotero API key.

## Servers for one project

For Claude Code, run these from the repository's root folder. `--scope project` after
`add` shares a server through `.mcp.json` instead. The command writes that file into the folder it runs in. Claude Code looks for it from
the starting folder upward, so sessions started at the root miss a file in a subfolder:

```bash
claude mcp add serena -- serena start-mcp-server --context claude-code --project "$(pwd)"
claude mcp add playwright -- npx @playwright/mcp@0.0.83
```

For Codex, the same servers go in the repository's `.codex/config.toml`. Codex reads
that file only when the owner has trusted the folder:

```toml
[mcp_servers.serena]
command = "serena"
args = ["start-mcp-server", "--project-from-cwd", "--context=codex"]

[mcp_servers.playwright]
command = "npx"
args = ["@playwright/mcp@0.0.83"]
```

`codex mcp add` has no scope option, so it always turns a server on everywhere.

## Plugins

```bash
claude plugin marketplace add anthropics/claude-plugins-official
claude plugin install pyright-lsp@claude-plugins-official --scope project
claude plugin install session-report@claude-plugins-official --scope user
```
