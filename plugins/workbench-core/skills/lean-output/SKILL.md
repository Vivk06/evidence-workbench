---
name: lean-output
description: Keep reports short, cited and terminal-only - verdict, evidence, gaps, next command - with no files written. Other skills use it for --lean.
metadata:
  tags: [lean]
  output_mode: terminal
---

# Lean output

Use this skill as `$lean-output`, or through another skill's `--lean` mode.

Command class: `read-only`.

Return the decision, evidence paths with line anchors, unresolved gaps, and one next
action. Use explicit sources only; never scan a home directory or copy personal data.

## Contract

Applies when the user selects `--lean` or asks for a lean, preview, diagnostic, or
terminal-only result:

- Print only a concise headline, evidence bullets, a PASS/FAIL/INCONCLUSIVE
  verdict, and a copy-pasteable next command.
- Do not create reports, graphs, plots, screenshots, caches, scratchpads, JSON
  outputs, project files, exports, or saved memory. Do not rebuild graph data or
  persist reflections. Use `/tmp` only for unavoidable tool internals and clean
  them before returning when safe.
- Stream progress for work taking more than a few seconds, include elapsed time
  when useful, and say when detail is intentionally omitted. Use explicit
  `--verbose` for long raw output. Missing evidence must remain FAIL or
  INCONCLUSIVE; it must not be hidden.
- Normal mode may create an artifact only when the user explicitly requests that
  artifact or supplies an explicit write/normal override.

If image generation or editing is requested in lean mode, pause before invoking
the image tool and ask exactly:

> What output size do you want? Please provide pixel dimensions or a target class
> such as thumbnail, slide, web image, print, or high-resolution figure. Also
> specify aspect ratio, format, and whether transparency is required.

After the user answers, image generation may go ahead as the one allowed bitmap. Report
its output path, dimensions, format and approximate file size.
