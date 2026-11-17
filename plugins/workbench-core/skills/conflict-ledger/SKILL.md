---
name: conflict-ledger
description: When sources disagree (docs, code, data), batch the conflicts with both sources and a recommended ruling, and keep independent work going.
metadata:
  tags: [lean]
  output_mode: terminal
---

# Conflict ledger

Command class: `safe-local`; writes only `logs/conflicts_<topic>.md` when asked to keep a
file, otherwise prints the ledger.

## When a conflict appears

1. Do not pick a side silently and do not stop all work.
2. Record it in the table in `references/ledger-format.md`:
   - what disagrees;
   - source A and source B, each as `path:line`, or as a command and its output;
   - which source is newer or closer to the running code;
   - the recommended ruling, with its reason.
3. Mark what depends on the ruling. Continue with independent work; park dependent work.
4. Batch: present all open conflicts together at a natural stopping point, not one
   question per conflict.

## Recommending a ruling

Prefer, in this order:

1. what the code does at HEAD, over what a document says it does;
2. measured data, over a stated expectation;
3. the owning document in the authority map, over a copy;
4. the newer dated record, over the older one.

Say when none of these decides it.

## After the user rules

Apply the ruling at the owning source only, then fix or link the copies. Record a
decision (decision-record skill) when the ruling changes a method or interface.

## Refusals

Never change a gate, a threshold or recorded data to make two sources agree. Never
resolve a conflict by deleting one source without the user's ruling.
