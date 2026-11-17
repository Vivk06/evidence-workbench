# Getting started

Install the plugin that matches your task. You need Claude Code or Codex with plugin
support. Python 3.9 or later runs the local scripts. You can use the instruction-only
skills without running a script.

## Install one plugin

Add the marketplace once:

```bash
claude plugin marketplace add Vivk06/evidence-workbench
```

Choose one of these Claude Code install commands:

```bash
claude plugin install sim-validity@evidence-workbench --scope user
claude plugin install ml-validity@evidence-workbench --scope user
claude plugin install research-writing@evidence-workbench --scope user
claude plugin install workbench-core@evidence-workbench --scope user
```

Domain plugins start disabled. From your project's root, enable the one you installed:

```bash
claude plugin enable sim-validity@evidence-workbench --scope project
```

Replace `sim-validity` with your choice. Restart the session after installing or enabling.
Claude Code installs the shared workbench-core dependency.

For Codex, add the marketplace and shared plugin once:

```bash
codex plugin marketplace add Vivk06/evidence-workbench
codex plugin add workbench-core@evidence-workbench
```

Then choose the domain plugin:

```bash
codex plugin add sim-validity@evidence-workbench
codex plugin add ml-validity@evidence-workbench
codex plugin add research-writing@evidence-workbench
```

Codex asks you to approve hooks after installation and updates. Hooks have no effect
without a project profile. `bash scripts/print-install.sh --plugin sim-validity` prints
the commands for your choice. `--client claude` or `--client codex` selects one client.

## Use a skill

Start a session in the project you want to review. Claude Code uses
`/<plugin>:<skill>`; Codex uses `$<skill>`. You can also ask in plain words.
The [skill catalog](skills.md) lists the available tasks.

An audit reads existing evidence. Expensive runs and installs are handed to you as
commands. Follow your repository's own environment instructions before running checks.

## Set up an optional profile

Ask for `/workbench-core:repo-setup .` in Claude Code or `$repo-setup .` in Codex.
The skill detects project facts and proposes changes before writing them. Existing
profile values stay as written. Git restrictions, reserved commands and test ceilings
are choices you make; the detected test count does not become a ceiling.

Extra tool discovery is a separate opt-in step. Ask repo-setup to check optional tools
only when you want those integrations. See [workflow options](workflow.md).

## Optional paper processing

Writing skills do not require the research-papers plugin. If you want retrieval or
paper-collection workflows, install the pinned integration separately:

```bash
claude plugin marketplace add ctoth/research-papers-plugin#v4.8.1
claude plugin install research-papers@research-papers-marketplace --scope user
```

For Codex:

```bash
codex plugin marketplace add ctoth/research-papers-plugin --ref v4.8.1
codex plugin add research-papers@research-papers-marketplace
```

`research-router` previews the workflow by default. Downloads, collection changes and
optional knowledge-store work need an explicit request. Review the upstream access
methods before using retrieval. The workbench does not redistribute that plugin.

## Install the whole bundle

Claude Code users who want all four plugins can run:

```bash
claude plugin install workbench@evidence-workbench --scope user
```

Keep `workbench` disabled; it is an install-only bundle. Enable the domain plugins you
need per project. Codex users add each chosen plugin separately.

## Update

Refresh and update the plugins you installed, then restart your client:

```bash
claude plugin marketplace update evidence-workbench
claude plugin update ml-validity@evidence-workbench --scope user
claude plugin update workbench-core@evidence-workbench --scope user
codex plugin marketplace upgrade evidence-workbench
```

Replace `ml-validity` with your installed domain plugin. Keep `--scope user` so the
update reaches the user-level installation. `claude plugin list` shows installed copies.
The [optional tools guide](optional-tools.md) covers separate servers and their updates.
