# Evidence map format

The node and link types follow GitHub's build-evidence-map skill
(https://github.com/github/awesome-copilot, MIT). This plugin keeps them in a Markdown
table instead of JSON, so that a person can read the working file too.

## The map (a working file)

```markdown
<!-- working file: conclusions in docs/solver-choice.md -->
# Evidence map: which linear solver should the adjoint use?

| ID | Kind | Statement | Links | Source |
|---|---|---|---|---|
| P1 | position | Use GMRES with an ILU(0) preconditioner for the adjoint | | |
| C1 | claim | GMRES converges on every case we ran | supports P1 | |
| C2 | claim | ILU(0) fits in memory on the fine mesh | supports P1 | |
| E1 | evidence | All 12 cases reached a residual drop of 1e-8 | supports C1 | logs/adjoint-sweep.csv:2 |
| E2 | evidence | Case 7 needed 3 restarts at the default restart length | qualifies C1 | logs/case07.log:880 |
| E3 | evidence | Peak memory was 41 GB of 64 GB on the fine mesh | supports C2 | ledger:L4 |
| U1 | unknown | Behaviour at angles of attack above 12 degrees | missing C1 | |
```

| Column | Content |
|---|---|
| ID | short and stable: `P1` for the position, `C` claims, `E` evidence, `U` unknowns |
| Kind | `position` (exactly one: the current answer), `claim`, `evidence`, `unknown` |
| Statement | one sentence; evidence states one source faithfully |
| Links | comma-separated `<type> <ID>`; types are `supports`, `contradicts`, `qualifies`, `missing` |
| Source | evidence only: `ledger:<id>` (a claims-ledger row), a URL with its access date, or `path:line` |

Rules the checker enforces:

- Claims link to the position or to another claim; evidence links to claims or the
  position; nothing links to evidence or an unknown.
- Every claim has evidence, a sub-claim or an unknown bearing on it, and every node has
  a chain of links that reaches the position.
- Only unknowns use `missing`. Evidence citing a ledger row marked `contradicted` is
  never used as support.

Topical similarity is not support. A different scope, date or population qualifies a
claim; it does not automatically contradict it. Express uncertainty with an unknown or a
narrower claim, never with an invented percentage.

## The reader version

The reader document carries the argument as prose, in this order:

1. The position, as the answer.
2. One section per claim. The heading states the claim; the text gives its evidence
   with sources.
3. "What argues against this": every `contradicts` and `qualifies` link, and why the
   position survives it, or how it narrows the position.
4. "What we do not know yet": every unknown, and the check that would settle it.
