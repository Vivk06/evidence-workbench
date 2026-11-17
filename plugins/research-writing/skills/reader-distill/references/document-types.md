# Document types

Choose one type per reader document. Mixing types in one document is the most common
reason a document is hard to use.

The four types come from the Diátaxis framework by
Daniele Procida (https://diataxis.fr). The decision document comes from Barbara Minto's
pyramid principle. Its gate and tests are adapted from
https://github.com/millwright-labs/minto-pyramid-skill (MIT, Copyright (c) 2026
Millwright Labs). This file restates both in its own words.

## Pick the type

Ask two questions. Does the text help the reader act, or help them understand? Is the
reader learning, or applying what they know?

| The reader wants to | Type | Shape |
|---|---|---|
| learn by doing, guided | tutorial | numbered steps with a visible result after each; little explanation |
| finish a task they already understand | how-to guide | goal in the title, steps in order, each state change followed by "Expected:" and, where failure is realistic, "If not:" |
| look up exact facts | reference | structure mirrors the thing described; tables and lists; no opinion |
| understand why | explanation | running prose: context, reasons, alternatives, limits |
| accept a conclusion or decide something | decision document | the pyramid below |

Background belongs in an explanation, not inside a how-to guide. Opinion belongs in an
explanation or a decision document, never in a reference. When a source mixes types,
split it into the documents each part belongs to and link them.

## The decision document (answer first)

Use it only when the reader must accept a judgment or decide something. Examples are a
recommendation, a verdict, an analysis with a conclusion, or an update that asks for
something. Do not use it for a timeline, a procedure, a tutorial, notes or a
description. In those, the order of events or steps is the right order.

Shape:

1. Context: one or two sentences the reader already accepts, and the problem that
   raises the question. Never longer than the answer.
2. The answer in one sentence.
3. The reasons that support it: as many as the logic needs, not a fixed three. Each
   reason answers the question the answer raises, and all reasons are the same kind of
   idea, ordered by deduction, time, structure or importance.
4. The evidence under each reason, with its source.
5. A closing section for risks, limits, open questions and next steps. A risk that
   could change the decision goes beside the answer instead.

Tests to run on a draft:

- Buried answer: where does the conclusion first appear, and how many words come
  before it? If the sources support no single conclusion, say so; do not pick one.
- Reason audit: do any reasons overlap, is one really evidence for another, and is a
  reason missing?
- "So what?": every sentence supports a reason or the answer, or sits in the closing
  section. List what you cut so nothing that matters goes with it.

## Rules for every type

- Never add a fact, number or claim the sources do not contain, including arithmetic
  on their numbers that they do not show. Sharpen wording, never strength.
- A user may share their own draft without asking for a rewrite. Then describe the
  problem in one sentence and offer the restructure. Do not hand back the rewrite.
- An analysis note starts with its answer unless the project's required format says
  otherwise. A separate title page and contents are optional.
