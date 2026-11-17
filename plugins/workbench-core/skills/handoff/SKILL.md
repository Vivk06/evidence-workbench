---
name: handoff
description: Write the commit message file, patch series and next-session pointer when a step is done and the user commits or continues it.
metadata:
  tags: [lean]
  output_mode: terminal
---

# Handoff — commit message, patches, next-session pointer

Command class: `safe-local`. Writes only the handoff files named below and, for a patch
series, a private shadow repository under `/tmp`. In the user's repository, the user
commits, pushes, tags and runs `git rm` and `git mv`. The agent does these only when the
user or the repository's instructions hand them over.

## Inputs

- Repository root and a short kebab-case topic. Ask for the topic if none is given.
- Profile, when the repository has one: `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/profile.py <root>`
  (Codex: `../../scripts/profile.py` from this skill's folder). Use its `commit_message` and
  `patches` paths when set. Without a profile, follow the repository's output paths
  and commit convention. If none exists, offer the example in `references/commit-format.md`.
  Create message files or a patch series only when requested or required by the project.

## Steps

1. Read the actual diff (`git diff`, `git diff --stat`, untracked files). Describe only
   what the diff shows; name pre-existing failures separately from regressions.
2. Draft the requested commit message in the repository's format. State what changed,
   why and what was checked. A prepared command is not evidence. Save the message only
   when the task or project calls for a message file.
3. If a patch series is requested: build the series in a shadow repository and dry-run it on a
   scratch clone, as in `references/patch-series.md`. Never hand-edit a patch.
4. Print the user's commands, one per line, no trailing comments, nothing to run
   before them that the agent has not stated.
5. If a new-session handoff is requested, write a short next-session pointer.
   It names the authority docs by path and section, the HEAD to confirm and the one step
   in scope. It also names what is out of scope, the gate and the wrap-up outputs. Point
   to documents; do not explain them.

## Not a git repository

Skip steps 1 and 3. List the changed files from the session's own record. Write the
message file anyway if the user wants a change log, and say that no git command applies.

## Refusals

Do not commit or push to make the handoff "complete". Never claim a step is verified when
its gate did not run in this session. List it under Verified as `not run`, with the
command the user should run.
