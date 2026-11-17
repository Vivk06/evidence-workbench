# Privacy and redaction rules

- A source scope is mandatory; implicit home-directory and current-directory scans are forbidden.
- Personal data is `deny` by default. `allowlisted` requires explicit source paths and is never inherited.
- Skip credentials, private keys, token files, databases, transcripts, caches, papers, and binary files.
- Redact common API keys, bearer tokens, passwords, private-key blocks, and connection strings.
- Do not write logs, bundles, manifests, settings, or default context files containing source text.
- Lean mode performs no writes. Write mode requires an explicit output path and writes only that path.
