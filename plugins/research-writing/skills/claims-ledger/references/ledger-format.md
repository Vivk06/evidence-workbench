# Ledger format

```csv
id,claim,source_url,access_date,status,used_in
L1,"Program requires two recommendation letters",https://example.edu/admissions,2026-10-25,verified,sop.tex:12
L2,"Lab works on adjoint-based optimization",https://example.edu/lab/research,2026-10-25,verified,faculty-fit.md:30
L3,"Application deadline is 15 December",,,unverified,timeline.md:4
```

The `id` column is optional. Add it when an evidence map cites rows as `ledger:<id>`;
an id never changes and is never reused.

- One claim per row, quoted exactly as used.
- `used_in` lists `path:line` for every place the claim appears.
- Keep rows when a claim leaves a document; change `used_in`, do not delete history.
