# Borrowed planning methods

Adapted from obra/superpowers (MIT, Copyright (c) 2025 Jesse Vincent), revision
`2ce8aa15d05bd57213e6f746f953aafb7ded7a8b`, file `skills/writing-plans/SKILL.md`. Ideas
only; wording is this repository's.

- Global Constraints: the aim's project-wide requirements (version floors, dependency
  limits, naming rules, platform requirements), one line each, values verbatim. Every
  phase implicitly includes them.
- Review Focus: the few inputs or failure modes that are most likely to hurt a user and
  that no gate exercises. Each line names the input and the expected behaviour. It is
  assigned to the phase that owns the code, and that phase adds a gate for it. An empty
  list means the check was done and found none.
- Interfaces per phase: "Consumes" lists the exact names and signatures from earlier
  phases. "Produces" lists what later phases rely on. A fresh session executing one phase
  learns the neighbouring names here.
- A step is done when exactly one reasonable thing can be written from it. Steps that
  decide nothing ("TBD", "add appropriate validation") are defects; so are steps that
  over-specify bodies the signature already determines.
- Self-review before handing the plan over: every aim requirement maps to a phase; every
  Review Focus line has a gate; no placeholders; fix inline.
- Right-sizing: a phase is the smallest unit with its own gate that a reviewer could
  reject independently.
