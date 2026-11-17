# Patch series through a shadow repository

Use when one task should land as several commits. The user's repository is never written.

1. Shadow: `git clone --quiet <repo> /tmp/<topic>-shadow` and copy the working-tree
   changes in (or apply `git diff` from the user's tree with `git apply`).
2. In the shadow, stage and commit each logical change with its own message file
   (`logs/commit_NN_<topic>.txt` in the user's repository, in the format of
   `commit-format.md`).
3. Export: `git -C /tmp/<topic>-shadow format-patch -o <repo>/logs/patches <base>..HEAD`,
   renaming to `NN_<topic>.patch`.
4. Dry-run on a scratch clone: `git clone --quiet <repo> /tmp/<topic>-check`. Then, for
   each patch in order, run `git apply --cached <patch> && git commit -F <message>`. The
   series must apply cleanly, and the final tree must equal the shadow's.
5. Hand the user one line per patch: `git apply --cached logs/patches/01_<topic>.patch &&
   git commit -F logs/commit_01_<topic>.txt`.
6. Delete `/tmp/<topic>-shadow` and `/tmp/<topic>-check` after the dry run passes.

If a patch fails to apply, regenerate the series from the shadow; never edit a patch file
by hand.
