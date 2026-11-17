---
name: reader-distill
description: Turn scattered agent notes, logs and part-written docs into a few readable documents, answer first and in full sentences, keeping every fact and showing where each one went.
metadata:
  tags: [lean]
  output_mode: terminal
---

# Reader distill

Use this skill as `$reader-distill <sources> [--reader <who>] [--out <path>]`.

Command class: `safe-local`; writes only the reader documents and the fact map in scope,
and the working-file marker on sources the agent wrote.

Agents keep many working files: notes, logs, ledgers, handoffs. A person needs a few
reader documents instead, each answering one question for one reader. This skill moves
facts from the first kind to the second and loses none on the way.

## Steps

1. Inventory the sources the user names (files or folders; never a home directory):
   `python3 ${CLAUDE_PLUGIN_ROOT}/skills/reader-distill/scripts/doc_inventory.py <paths>`
   (Codex: `scripts/doc_inventory.py` in this skill's folder). It lists reader documents
   and working files, and flags documents that are mostly fragments or fail the
   plain-language checker.
2. Name the reader and the questions they need answered. Plan as few documents as
   answer them, and prefer extending an existing reader document to adding a new one.
3. List every fact in the sources in a fact map (`references/fact-map.md`), with its
   `path:line`. Claims that need a source go to the claims-ledger skill; claims that
   support or contradict each other go to the evidence-map skill.
4. Pick each document's type (`references/document-types.md`): tutorial, how-to guide,
   reference, explanation, or a decision document that leads with its answer.
5. Write the outline first: title, then headings that state their topic, with the
   answer or result first. Show it to the user when the document is new or merges more
   than one source.
6. Write by the plain-language skill: full sentences, every term and internal code
   defined where it first appears, each fact once, numbers with units and sources.
7. Fill in "Went to" for every fact-map row. Add the working-file marker to each source
   the agent wrote. List sources with no remaining use and the command to remove them.
8. Check: run the plain-language checker on each reader document, then reread it as its
   reader against the questions from step 2. When the user asks, also test it with a
   fresh subagent that sees nothing but the document; that costs model time.

## Output

The reader documents; the fact-map rows that say `dropped` or `stays in`; the checker
verdict for each document; the removal commands for the user.

## Verdict

PASS: every fact-map row has a destination, every reader question has an answer, and
the checker passes each document. FAIL: a fact with no destination, a question with no
answer, or a must-fix finding. INCONCLUSIVE: a source could not be read; name it.

## Refusals

- Never drop a number a result depends on, a risk, a failure, or the only copy of a fact.
- Never add a fact or make a claim stronger than its source.
- Never delete, move or rewrite a source the user wrote; offer the change instead.
- Never reorder a timeline, procedure or tutorial into answer-first form.
