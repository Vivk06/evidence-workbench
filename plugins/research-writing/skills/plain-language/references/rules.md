# Plain-language rules

These rules apply to every text a person reads: documents, reports, notes, plans, pull
request text, commit messages and code comments. In clause references, "1:" means
ISO 24495-1:2023 (plain language) and "3:" means ISO 24495-3:2026 (technical and
scientific writing). Adapted from https://github.com/auxesis/plain-language-skill
(Apache-2.0); the checker's NOTICE file in `scripts/` lists what changed.

## Content

- Give the reader what they need and nothing else. Never leave out risks, failures,
  limits, or what you did not check. (1: 5.1.6)
- Describe the result, not how you reached it. Leave out first versions, false starts
  and fixed mistakes, unless the reader needs them to trust the result. (1: 5.1.6)

## Order and structure

- Answer first: the result, the conclusion, or the decision you need. Reasons and
  detail come after. (1: 5.2.2 a)
- Put steps in the order the reader does them, and a warning before its step. (1: 5.2.2 c, e)
- Use headings in long text, numbered lists for steps and tables for comparisons. A
  short answer needs none of them. (1: 5.2.3, 5.2.4)
- Make each heading a short statement of its topic, never a question. Do not use a line
  of bold text as a heading, and do not skip a heading level. (1: 5.2.4)
- Make every item fit its heading. A fact you still need to check is a question; put it
  under a heading for questions and write it as one. (1: 5.2.4)
- Move background, method detail and references to the end. (1: 5.2.5)

## Terms

- Explain every term the reader has not used. That includes names invented while
  working, files and tools the reader has not seen, and issue numbers. It also includes
  internal codes, such as rule or decision numbers, and labels such as "option B". (1: 5.3.2 c, f)
- Define a term in a clause where it first appears, or replace it with a plain
  description. Spell out an abbreviation the first time. (1: 5.3.2 d, e)
- Use one word for one thing, and the reader's own word for it. (1: 5.3.2 g, h)

## Words and sentences

- Write literally: no metaphors, idioms or clichés. Give things literal verbs: a file
  contains, a table lists, a check reports. (1: 5.3.2 a, b)
- Choose the short, common word: "use", not "utilise"; "start", not "initiate". (1: 5.3.2)
- Write words, not symbols: "becomes", not an arrow; "about", not "~"; "times", not "×".
  Commands, paths and code stay exact, in code formatting. (1: 5.3.2 d)
- Write complete sentences in the order "who does what", in the active voice. A status
  line is a sentence too: "I am reading the log", not "Reading log". (1: 5.3.3 a to c)
- One idea per sentence, 25 words at most, and vary the length. (1: 5.3.4 a, c)
- Start a sentence with the name of its subject, not "it", "they" or "this". (1: 5.3.3 a)
- Do not interrupt a sentence with a long aside in dashes or brackets. (1: 5.3.3 a)
- One topic per paragraph, stated in its first sentence, five sentences at most. (1: 5.3.5)
- Cut filler: "very", "just", "it is worth noting that", recaps and praise. (1: 5.3.4 b)

## Numbers, evidence and certainty

- Give each number its unit and what it is compared with. Put at most two numbers in a
  sentence; use a table for more. (3: 5.3.2 g, 5.3.5 f)
- When a number changed, say what changed it. (3: 5.1.5 k)
- Make every table row the same kind of thing; parts must add up to their total. (3: 5.3.6)
- Say how you know: what you checked, inferred or guessed. "The test passed when I ran
  it" is a different claim from "the test should pass". (3: 5.3.2 e)
- Never make a claim more certain than its source. Use one hedge per claim, tied to the
  evidence: "two of five runs failed", not "it sometimes fails". (3: 5.1.6, 5.3.3 f)
- Say where each claim comes from: file and line, command, link or document. (3: 5.3.2 a, c)
- Complete every comparison: faster than what? (3: 5.3.3 i)

## Tone

- Be direct and respectful. No flattery, blame or "obviously". Use inclusive terms, such
  as "allowlist" and "they" for a person whose pronouns you do not know. (1: 5.3.7)
