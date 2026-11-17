---
name: third-party-audit
description: Audit vendored or copied third-party code - inventory, licenses and attribution, pinned revisions, recorded modifications and parity checks for copied code.
metadata:
  tags: [lean]
  output_mode: terminal
---

# Third-party audit

Command class: `read-only`.

## Steps

1. Inventory: `third_party/`, `vendor/`, `external/`, git submodules, copied files with
   foreign headers, and code a header marks as copied from another project.
2. For each component, record these in the format of `references/inventory.md`:
   - the upstream URL, and the pinned revision or version;
   - the license, and where its text is in this repository;
   - the attribution: a `THIRD_PARTY.md` or `NOTICE` entry;
   - local modifications.
3. License fit: the license allows the use (redistribution, modification) and its terms
   are met (notice kept, source offer where required). Flag missing license files, unknown
   licenses and copyleft code linked into differently licensed code.
4. Copied code has a header that names the source path and commit. It also has a parity
   check against the upstream behaviour it copies: a test or a recorded comparison.
5. No secrets, credentials or large binaries arrived with vendored code.

## Verdict

- PASS when every component has its upstream, revision, license, attribution and
  recorded modifications.
- FAIL on a missing or incompatible license, or an unattributed copy.
- INCONCLUSIVE when the upstream or revision cannot be determined.
