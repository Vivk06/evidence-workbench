# Example commit message format

Use the repository's own convention when one exists. This format is optional.

```
<component>: <completed change in plain words>

Why
<the problem or need, in two to five lines>

Changed
- <path or component>: <what changed and why it matters>

Removed, and where it went
- <removed thing>: <where its facts or behaviour now live, or why it was dropped>
  (write "Nothing removed." when nothing was)

Verified
- <exact command>: <result, with numbers>
- <check not run here>: not run; the user runs <command>
```

Rules:

- Subject: the component and the finished change. A component is a package, plugin,
  module or document set. No phase number, counter, ticket label, "WIP", "misc" or commit
  SHA.
- `Removed, and where it went` makes deletions auditable: every dropped file, rule,
  option or fact names its new owner.
- `Verified` cites evidence produced in this session. Exit status alone is not evidence
  of physical or numerical correctness.
- Wrap body lines at about 80 characters.
