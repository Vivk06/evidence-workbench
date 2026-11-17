---
name: research-router
description: Route paper retrieval, reading, research, citation checks, reconciliation, and optional propstore work to the installed research-papers plugin.
argument-hint: "[preview|normal] <research request>"
disable-model-invocation: false
metadata:
  tags: [lean]
  output_mode: terminal
---

# Research router: $ARGUMENTS

Command class: `read-only` in preview mode; normal mode hands writes to the
research-papers plugin only after the guard below.

Use the optional `research-papers@research-papers-marketplace` plugin for paper
processing. Install it separately from `ctoth/research-papers-plugin` at `v4.8.1`.
Writing and audit skills work without it.

If the plugin is absent, report the missing
integration and offer its install commands. Do not call an unavailable skill.
This skill routes requests; it does not reimplement paper processing.

## Default mode: preview

Treat an invocation as `preview` unless the user explicitly selects `normal` mode.
Preview is terminal-only and must not:

- download or retrieve papers;
- write `papers/`, `reports/`, page images, metadata, indexes, or prompts;
- mutate a paper collection or propstore store;
- invoke `pks`;
- install or enable a plugin, skill, MCP server, or access backend.

Preview may summarize the requested workflow, identify the relevant skill and report
unresolved inputs. It may also show the canonical collection path, from the repository's
profile, its docs or the research-papers plugin's own configuration. Require explicit
identifiers, paths, and questions; never scan a home directory or personal-data corpus
implicitly.

## Routing table

| Work | Claude Code | Codex CLI |
|---|---|---|
| Retrieve one paper | `/research-papers:paper-retriever <identifier>` | `$paper-retriever <identifier>` |
| Read a paper | `/research-papers:paper-reader <path/to/paper.pdf>` | `$paper-reader <path/to/paper.pdf>` |
| Research a topic | `/research-papers:research <topic>` | `$research <topic>` |
| Verify citations | `/research-papers:verify-citations <draft.md> [--papers-dir papers/]` | `$verify-citations <draft.md> [--papers-dir papers/]` |
| Reconcile a paper/collection | `/research-papers:reconcile <paper-dir> or --all` | `$reconcile <paper-dir> or --all` |
| Lint a paper/collection | `/research-papers:lint-paper <paper-dir> or --all` | `$lint-paper <paper-dir> or --all` |
| Process one paper | `/research-papers:paper-process <identifier> [--light]` | `$paper-process <identifier> [--light]` |
| Ingest a collection | `/research-papers:ingest-collection <papers-dir> [--knowledge-dir <path>]` | `$ingest-collection <papers-dir> [--knowledge-dir <path>]` |
| Tag papers | `/research-papers:tag-papers <paper-dir> or --all` | `$tag-papers <paper-dir> or --all` |

The plugin's skill files are authoritative for behavior and argument handling. The
router must not replace their documented sequence with ad hoc shell commands.

## Normal-mode guard

Before handing a normal-mode request to the plugin, confirm all of the following:

1. The user explicitly selected normal mode or explicitly requested the write action.
2. The target is the canonical collection or a user-supplied output path.
3. Retrieval, collection mutation, propstore use, paywalled access, and installation
   are each authorized when applicable.
4. The request names one paper, one bounded collection path, or one bounded draft.

`paper-process` and `ingest-collection` are composite write workflows. `--light`
still retrieves and writes notes-layer artifacts; it only skips propstore steps.
`lint-paper` is read-only. `research` writes a report by its upstream contract.

## Propstore boundary

Some routes are optional. They need an explicit user request and a working `pks`
installation. They are `paper-process` without `--light`, `ingest-collection`, and the
source, claims, context, predicate, rule and promotion skills those two invoke. Never test
`pks` or initialize a knowledge store during a preview.

## Installation boundary

Hand the install commands to the user only after approval. The first is
`claude plugin marketplace add ctoth/research-papers-plugin#v4.8.1`, followed by the
plugin install.
They are `user-execution` actions and must not be run by this skill automatically.

## Preview response

Return a compact plan containing the selected route, client invocation form, target
path, required authorization, and unresolved gaps. End preview responses with:
`Preview only: no paper download, collection mutation, pks invocation, installation,
or file write performed.`

## Lean mode

With `--lean` or a terminal-only request, follow the lean-output skill: no retrieval,
`pks`, graph rebuild or write; print a bounded plan or verdict only. Explicit normal mode
still permits only the requested, authorized artifact.
