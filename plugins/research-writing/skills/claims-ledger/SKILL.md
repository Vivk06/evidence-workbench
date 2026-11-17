---
name: claims-ledger
description: Keep every factual claim in a document traceable to a source URL and access date in a CSV ledger, and check claims against their sources before use.
metadata:
  tags: [lean]
  output_mode: terminal
---

# Claims ledger

Command class: `safe-local`; writes only the ledger file and the document in scope.

## Ledger

Keep one CSV per project or document set, with the columns in
`references/ledger-format.md`: `claim, source_url, access_date, status, used_in`. An
optional first column, `id`, names the rows an evidence map cites (evidence-map skill).

Use the profile's `claims_ledger` path when the repository has one, in the `workbench:`
block of `AGENTS.md`. Otherwise use `claims-ledger.csv` beside the document, or the
location the user names.

## Steps

1. Extract each factual claim from the document: names, numbers, dates, positions,
   requirements, quotations, rankings.
2. Match it to a ledger row or add one. A row needs a source the user supplied or a page
   you opened in this session; record the URL and today's date.
3. Status is one of four values:
   - `verified`: the source states it now;
   - `unverified`: no source yet;
   - `contradicted`: the source says otherwise;
   - `stale`: checked longer ago than the project's refresh period, 90 days by default.
4. In the document, every claim either cites its ledger row or is marked for the user as
   unverified. Never present an unverified or contradicted claim as fact.

Checks open the source page directly; they use no paid or rate-limited service.

## Refusals

- Never invent a source, a quote, a date, a position or a requirement. A claim without a
  source stays `unverified` and the document says so.
- Do not silently update a claim to match a new source: record the contradiction and let
  the user rule (conflict-ledger skill).
