---
name: token-lean
description: "Context and token discipline: delegation, fresh-window handoffs, frugal log reading, graph-first search. Use in long sessions, before large reads, or near compaction."
metadata:
  tags: [lean]
  output_mode: terminal
---

# Token lean

Use this skill as `$token-lean`.

Command class: `read-only`. It changes how the session reads, not what it writes.

The rules are ranked by how much context they save. The cheapest context is the context
never loaded. `references/delegation-patterns.md` shows each pattern as a tool call.

## 1. Delegate, and keep raw output out of the main session

Before a large read, a survey or a search in several rounds, decide whether you need the
answer itself or only the conclusion.

| Situation | Pattern |
|---|---|
| Open search: a file scan, a symbol hunt, "where is X" | an Explore agent, which reads only and returns a summary |
| A separate question whose intermediate reads you will not need again | a fork of yourself, which shares your context and cache |
| A task with its own chain of tools: a refactor, a plan, an audit | a general-purpose agent with a complete brief |
| Several separate questions | several agent calls in one message; forks are cheapest here |
| A large read-only survey that Codex can do | the codex-delegate skill: a prompt file and one printed `codex exec -s read-only` line |

Rules for the prompt you give an agent:

- A fork already has your context, so give it a directive: "do X, report Y".
- A fresh agent has none. Brief it like a colleague who just walked in: what, why, what
  has been tried, which files matter and the format you need back.
- Always name the output shape, such as "under 200 words" or "a table of file:line".
- Never delegate understanding. Write prompts that show you understood the problem.

Example of the waste to avoid: reading a 500-line log to find one number. Send an agent
with a grep filter and take back only the number.

## 2. Hand over when the task needs a new session

Continue in the current session while context remains useful. If the user or project
requests a new session, write a short handoff. Name the authority documents, current
state, key numbers and next action. Use the project's handoff format when one exists.
A phase boundary alone does not require a new session.

## 3. Read files and logs frugally

- Logs: read the summary lines and the exit code with `tail`, `grep` or `jq`. Never
  stream a whole solver log or test output. A typical filter is
  `grep -E "^Ran |^OK|FAILED|failures=|errors="`.
- Long runs: run them in the background with output to a file, and read only the verdict.
- Large documents: read the named section, not the whole file. Trust blocks marked as
  known state that must not be derived again.
- Large corpora: prefer the documentation-context skill, and the preview mode of
  research-router, to pulling whole papers into context. Use authority-router to find
  the owning document before any broad search.
- lean-output governs what you print; this skill governs what you read. Both apply.

## 4. Search the code graph first

Query the repository's code graph when it has one, instead of rounds of grep and reads.
The profile's `code_graph` names it, for example `graphify query` over `graphify-out/`,
or a language server. Read papers through their text form (`txt_files/`) rather than the
PDF when both exist. When there is neither, send an Explore agent to find the source
before you read anything.

## 5. Save durable facts to memory

At phase boundaries, offer to save four kinds of fact:

- new numeric baselines, with their date and source;
- root causes;
- decisions, with the options declined;
- quirks of the environment.

Save them to Claude Code's memory, or to the repository's docs when the fact
belongs to the project. Codex keeps its own memory, so project facts belong in the
repository's docs, where both clients see them.

## 6. Compact at natural boundaries

Use `/compact` with a focus instruction at a task boundary, rather than waiting for
automatic compaction in the middle of a task. Write any state that matters to the plan,
the results docs or memory first; the documents are the source of truth. Near the limit,
write the in-flight state, then offer `/compact`. If the user declines, write a
fresh-session handoff prompt instead.

## 7. Codex equivalents

| Claude Code | Codex CLI |
|---|---|
| a fork or general-purpose agent | a sub-agent through Codex's `spawn_agent` tool, with a self-contained brief |
| an Explore agent | `spawn_agent` with a read-only survey brief, or the code graph and targeted `grep` |
| a background run with its output in a file | `... > /tmp/out.txt 2>&1 &`, then read the verdict |
| `/compact` with a focus | fresh-session handoffs |

## Lean mode

With `--lean` or a terminal-only request, follow the lean-output skill: print the advice
only, and write no file.

## Limits

Saving tokens never outranks integrity. Never skip a verification gate, summarize away
the details of a failure, or skip a file the task needs. Reading frugally means reading
the right part, not reading nothing. Never shorten a handoff prompt so far that it stops
being usable. When the evidence is missing, the verdict stays INCONCLUSIVE.
