---
name: evidence-map
description: Connect claims into one argument - a position, the claims under it, evidence for and against each, and open unknowns - checked locally, then written up for a reader.
metadata:
  tags: [lean]
  output_mode: terminal
---

# Evidence map

Use this skill as `$evidence-map <question> [--ledger <claims-ledger.csv>]`.

Command class: `safe-local`; writes only the map file and the reader document in scope.

A claims ledger says where each claim comes from. An evidence map says how the claims
connect: what supports the answer, what pushes against it, and what is still unknown.
Use it when the relations between claims matter, not for checking one fact.

## Steps

1. Frame one question that evidence could settle, and write the current answer as the
   position.
2. Collect the evidence. Record each source in the claims ledger (claims-ledger skill),
   with an `id` for each row the map cites.
3. Write the map in the form of `references/map-format.md`. It holds one position, the
   claims under it, evidence for each claim, and unknowns that could change the answer.
   Keep it as a working file beside the reader document, or where the user says.
4. Mark every link `supports`, `contradicts`, `qualifies` or `missing`. Keep evidence
   against the position in the map even when the position survives it.
5. Check the map:
   `python3 ${CLAUDE_PLUGIN_ROOT}/skills/evidence-map/scripts/check_map.py <map.md> --ledger <ledger.csv>`
   (Codex: `scripts/check_map.py` in this skill's folder). Fix every "must fix" finding.
6. Write the reader version in the order of `references/map-format.md`: the answer,
   one section per claim, what argues against it, what is still unknown. Use the
   reader-distill and plain-language skills for the document itself.

## Verdict

PASS: the checker passes the map, and the reader version states every contradicting
or qualifying link and every unknown. FAIL: any "must fix" finding, or the reader
version leaves out evidence against the position. INCONCLUSIVE: the evidence cannot
support one position; say so and list what would decide it.

## Refusals

- Never delete or soften evidence against the position to make the map pass.
- Never invent a source, a confidence percentage or a link the sources do not show.
- When sources disagree on a fact, record both and let the user rule (conflict-ledger
  skill); do not pick one silently.
