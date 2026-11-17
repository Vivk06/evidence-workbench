# Workflow options

Start with individual skills. Add a profile when you want the hooks to enforce a
project policy. Your repository's instructions and explicit requests decide git access,
commit format, document layout and when to start a new session.

## Default behavior

New profiles set `git: normal` for git repositories and `git: none` for folders without
git. Normal mode leaves git permissions to the client and repository instructions.
The workbench does not add a test ceiling or a required commit-message path.

Without a profile, hooks do nothing. An invalid profile produces a warning and leaves
hooks off. Hooks help enforce selected policies; they are not a security sandbox.

## Choose stricter policies

Add a `workbench:` block to the YAML frontmatter of your project's `AGENTS.md`.
This example shows optional restrictions. Replace its commands and paths with your own:

```yaml
---
workbench:
  schema: 1
  archetypes: [code]
  git: read-only
  commit_message: logs/commit_<topic>.txt
  test_budget: {max: 40, paths: [tests]}
  frozen_paths: [vendor/]
  user_executed:
    - pattern: '\bmpirun\b'
      why: Cluster runs are submitted by the user
      codex_prefix: [[mpirun]]
---
```

`git: read-only` blocks agent git writes. `frozen_paths` blocks edits to the selected
paths. `user_executed` reserves matching commands for you. `test_budget` adds a reminder
when an edit exceeds your chosen ceiling; it never blocks the edit.

Profiles use a supported subset of YAML. The templates in
[`plugins/workbench-core/profiles/templates/`](../plugins/workbench-core/profiles/templates/)
show minimal profiles. `profile.py <repo>` in that plugin's scripts folder reads a profile.

## Keep your own conventions

The handoff skill follows your commit format and output paths. Its reference format is
an example for repositories without a convention. Request a patch series or a new-session
handoff only when you need one. Phase boundaries do not require restarting a session.

Writing skills follow the document's purpose and the project's style. A title page,
table of contents and a fixed section order are choices, rather than defaults for every note.
The evidence requirements still apply: cite findings, state limits and report missing inputs.

## Optional tools

Repository setup does not inspect personal client settings or recommend extra servers
unless you request the optional tool check. The [tools guide](optional-tools.md) covers
those integrations. Nothing is installed by repo-setup.
