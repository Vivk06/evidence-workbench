---
name: plain-language
description: Write or audit prose a person reads so they can find, understand and use it first time (ISO 24495), with a local checker that gives PASS or FAIL. Use for docs, reports and notes.
metadata:
  tags: [lean]
  output_mode: terminal
---

# Plain language

Use this skill as `$plain-language write|audit <file>`.

Command class: `safe-local`; write mode edits only the file in scope, audit mode edits
nothing.

Plain language means the reader can find what they need, understand it the first time,
and use it. The reader decides whether a text is plain, not the writer. The rules are in
`references/rules.md`; read them before the first draft.

## Modes

- `write`: draft or rewrite a document by the rules. A rewrite starts with a list of
  every fact in the original. At the end, each fact is still there or was cut on purpose.
- `audit`: report each problem as quote, rule, fix. Change nothing.

## Steps

1. Name the reader, what they already know, and what they will do with the text. Ask the
   user only when a wrong guess would waste their time.
2. List the questions this reader needs answered. Plan one part for each, and leave out
   the rest. Keep risks, limits, failures and what nobody checked.
3. Put the answer first. Use headings that state their topic, steps in the order the
   reader does them, and tables only for comparisons.
4. Write in full sentences. Define every term, abbreviation and internal code where it
   first appears, or replace it with a plain description.
5. Run the checker and fix every "must fix" finding. Decide on each "consider" finding:
   fix it, or keep it because this reader needs it.
   `python3 ${CLAUDE_PLUGIN_ROOT}/skills/plain-language/scripts/check.py <file.md>`
   (Codex: `scripts/check.py` in this skill's folder). Add `--json` for a report, or
   pipe text in with `--chat`. A line that contains `plain-language-allow` is skipped.
6. Reread as the reader. Is the answer at the start? Can the reader find each part from
   the headings alone? Is every term known or explained?

The stop-slop skill also applies. Where the two disagree, this skill decides structure
and wording in documents for readers, and stop-slop decides tone. Keep the spelling the
repository already uses.

## Verdict

PASS: the checker reports no "must fix" finding and step 6 finds no gap. FAIL: any
"must fix" finding, or a reader question with no answer in the text. INCONCLUSIVE: the
checker could not run (no Python 3.9 or later); say so, and do step 6 by hand.

## Refusals

- Never add a fact, number or claim the source does not contain, and never make a claim
  more certain than its source. Mark what was checked, inferred or guessed.
- Never drop a risk, limit or failure to make text shorter.
- Do not silence a finding with `plain-language-allow` unless the line quotes text
  that must stay exact; say which lines you marked and why.
