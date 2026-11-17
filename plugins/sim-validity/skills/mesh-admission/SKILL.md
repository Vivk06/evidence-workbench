---
name: mesh-admission
description: Admit an existing mesh only when structural, quality, orientation, resolution and provenance evidence passes.
metadata:
  tags: [lean]
  output_mode: terminal
---

# Mesh admission

Use this skill as `$mesh-admission <mesh> [--report <json>] [--provenance <json>]`.

Command class: `read-only`. Never rewrite, repair, reorient, convert or regenerate a mesh.

## Checklist (Knupp 2001; turbulence-model wall guidance)

Work through `references/checklist.md`:

- positive volumes and consistent orientation;
- quality: skewness, aspect ratio, non-orthogonality, minimum angle or scaled Jacobian;
- boundary markers, complete and named as the solver expects;
- wall resolution: `y+` for wall-resolved or wall-function models, and cells across
  boundary or Hartmann-type layers;
- refinement-level limits for adaptive meshes;
- hash and provenance.

Thresholds come from
the repository's profile or docs; `references/examples.md` shows typical ones.

## Checker

For SU2 native or Gmsh 2.2 ASCII meshes, run
`python3 ${CLAUDE_PLUGIN_ROOT}/skills/mesh-admission/scripts/check.py --mesh <absolute-path>
[--report <json>] [--provenance <json>]` (Codex: `scripts/check.py` in this skill's
folder). It parses headers, counts markers and elements, computes a SHA-256, and reads
declared quality reports. It does not apply to other formats or to octree/AMR meshes
built at run time: there, apply the checklist to the solver's own mesh diagnostics.

When the repository's profile or docs declare its own validator, use exactly that one.
First confirm that it overwrites no mesh and creates no case. Without one, there is no
solver-specific fallback beyond `sha256sum <mesh>`.

## Verdict

PASS, FAIL or INCONCLUSIVE per criterion, with the source path and measured value:
dimension, markers, orientation, quality statistics, wall spacing when declared, hash
and provenance. Missing required evidence is INCONCLUSIVE; an explicit failed gate, an
inverted or reoriented mesh, or non-finite quality is FAIL. A solver exit code or
orientation message alone never admits a mesh.

## Refusals

Mesh generation, SU2, Gmsh or MPI validation, and any validator that writes case outputs
go to the user as one printed command (run-handoff skill).

## Lean mode

With `--lean` or a terminal-only request, follow the lean-output skill: print the
verdict and evidence only, and write no file.
