---
name: application-dossier
description: Build a program or faculty dossier for an application from cited sources - leads, not claims - without inventing positions, deadlines or requirements.
metadata:
  tags: [lean]
  output_mode: terminal
---

# Application dossier

Command class: `safe-local`; writes only the dossier files the user names.

## Content

Use `references/template.md`: program facts (requirements, deadlines, funding, courses),
faculty entries (research directions, recent work, group pages), fit with the
applicant's completed work, open questions. Every fact carries a source URL and access
date and is recorded in the claims ledger (claims-ledger skill).

## Rules

- Faculty fit entries are investigation leads, not claims that a position, funding or
  supervision is available. Say "to confirm" where the source does not state it.
- Lead with the applicant's defensible completed work; label planned or interest areas as
  such.
- Read the program's and faculty's own pages the user names or that you open in this
  session; use no paid or rate-limited service.
- Use the applicant's own profile document as the source for their background when one
  exists (profile `authority` keys in `AGENTS.md`, else ask).

## Refusals

Never invent a faculty fact, a position, a deadline, a requirement or a statistic. A
missing fact is listed under open questions with where to find it.
