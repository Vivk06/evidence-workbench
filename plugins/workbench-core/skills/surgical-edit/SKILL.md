---
name: surgical-edit
description: Make minimal targeted edits under an explicit blast-radius contract and audit the diff. Use for one-line changes, threshold tuning, or edits limited by a files-not-touched list.
metadata:
  tags: [lean]
  output_mode: terminal
---

# Surgical edit

Use this skill as `$surgical-edit <request>`.

Command class: `safe-local`.

Before editing, state the exact files and functions or lines permitted to
change, plus everything explicitly excluded. Every changed line must trace
directly to the request. If justification requires an additional “and,” split
that work into a separate request.

When the repository has a profile, exclude everything under its `frozen_paths` and
`read_only_paths`. Those paths change only through the repository's decision route. Read
the profile with `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/profile.py <root>` (Codex:
`../../scripts/profile.py` from this skill's folder). If the profile says
`main_agent_edits_code: false`, dispatch the edit to the `surgical-editor` agent with a
per-file contract instead of editing in the main session. Without a profile, honour any
frozen or do-not-edit list the repository documents.

For a bug fix, establish the root cause before proposing the edit.

Make only the requested change. A one-line change is one line. Match local
style and leave adjacent stale comments or pre-existing dead code untouched;
mention them instead. Do not add speculative abstractions, flags,
configurability, or cleanup. Remove only imports or variables made unused by
your own edit.

After editing, run `git diff --stat` and compare it with the contract. Any file
outside the contract is a scope violation: revert it or obtain explicit
approval. Choose verification in proportion to risk:

- A change to a parameter or threshold only needs at most the affected test module.
- A logic change needs the affected module, and may run the full suite in the background.
- A requirement for identical output needs a comparison with the fixture output, not only
  a passing test.

Report changed file and line, deliberately untouched material, the verification
verdict, and a status: `DONE`, `DONE_WITH_CONCERNS` (done, with doubts named),
`BLOCKED` or `NEEDS_CONTEXT`.

## Refusals

Do not commit, push, or broaden the task without user authorization. A change that
needs a frozen or read-only path stops at `BLOCKED` and names the decision route.
