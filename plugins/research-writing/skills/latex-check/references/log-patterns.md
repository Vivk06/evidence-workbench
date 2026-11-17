# Log patterns

| Finding | Pattern (grep -nE) |
|---|---|
| Error with file:line | `^[^:]+:[0-9]+: ` (with `-file-line-error`) or `^! ` |
| Undefined reference | `LaTeX Warning: Reference .* undefined` |
| Undefined citation | `(LaTeX|Package natbib) Warning: Citation .* undefined` |
| Multiply defined label | `LaTeX Warning: Label .* multiply defined` |
| Rerun needed | `Rerun to get (cross-references|citations) right` |
| Missing file | `File .* not found` |
| Overfull box | `^Overfull \\[hv]box \(([0-9.]+)pt too` |
| Underfull box | `^Underfull \\[hv]box \(badness ([0-9]+)\)` |
| BibTeX problems | `^Warning--` and `^I couldn't open` in `.blg` |

`grep -nE '<pattern>' main.log | head -50` keeps output bounded.
