# Codex prompt template

```markdown
# Question
<one question, answerable from the files below>

# Read
- <path or glob>: <why>
- <run directory>: <which files>

# Answer format
- Markdown, under <N> words.
- Every fact cites `path:line`. Write "not found" rather than guessing.
- End with a list of files you could not read.

# Rules
- Read-only: do not edit, create or delete files.
- Do not run tests, verify scripts, builds, solvers, MPI, optimizers or installers.
- Do not use the network unless the question names a URL.
```

Keep the prompt self-contained: Codex does not see this session.
