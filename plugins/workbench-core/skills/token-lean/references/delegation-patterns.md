# Delegation patterns for token-lean context management

## Fork: offload research that would pollute coordinator context

```
Agent(
  subagent_type: "fork",
  name: "log-verdict",
  description: "Extract test verdict",
  prompt: "Read /tmp/solver-run.log. Report: pass/fail count, wall time,
           any SEGFAULT or NaN. Under 50 words."
)
```

Use when: the intermediate tool output (file reads, grep results) isn't worth
keeping in the coordinator's context. The fork inherits your full conversation,
so the prompt is a directive, not a briefing.

## Explore: read-only code survey

```
Agent(
  subagent_type: "Explore",
  description: "Find residual definitions",
  prompt: "Find all files in src/ that define or import ResidualCalculator.
           Report file:line pairs. Quick search."
)
```

Use when: you need to locate code but don't need the file contents in your
context. Specify search breadth: "quick", "medium", or "very thorough".

## General-purpose: complex delegated task

```
Agent(
  subagent_type: "general-purpose",
  name: "audit-imports",
  description: "Audit unused imports",
  prompt: "In /home/user/project/src/, find all Python files with unused imports.
           For each, report file path and the unused import names. We're cleaning
           up before a release — the codebase is ~200 files, mostly Flask endpoints.
           Report as a markdown table, under 500 words."
)
```

Use when: the task needs its own multi-step tool chain and the agent won't have
your context. Brief it completely.

## Parallel forks: independent questions in one message

Send multiple Agent calls in a single message when questions are independent:

```
Agent(subagent_type: "fork", name: "check-mesh",
      prompt: "Verify mesh file at cases/bump/mesh.h5 has >10k cells. PASS/FAIL.",
      description: "Mesh cell count")
Agent(subagent_type: "fork", name: "check-bc",
      prompt: "Grep cases/bump/boundary.yaml for 'inlet' and 'outlet' keys. Report present/missing.",
      description: "Boundary condition check")
```

## Background run + grep'd summary (no subagent needed)

```
Bash(command: "make test > /tmp/test-out.txt 2>&1", run_in_background: true)
# ... on completion notification ...
Bash(command: "grep -E '^(PASS|FAIL|ERROR|Ran )' /tmp/test-out.txt | tail -10")
```

Use when: the run produces a file and you only need a filtered verdict.

## Handoff prompt template (for fresh-window continuation)

```markdown
## Phase N+1 handoff

**Authority docs:** implementation_plan.md §Phase-3, CLAUDE.md §anti-patterns
**State:** Phase 2 complete (tag: phase-2-complete). Gate: mesh convergence PASS (L2 < 1e-6).
**Key numbers:** baseline drag Cd = 0.0234 ± 0.0003 (2026-09-15, commit abc1234)
**Carry forward:** do NOT re-derive baseline — use memory `baseline-drag-bump2d.md`
**Next action:** implement adjoint solver wrapper per §Phase-3 step 1
**Anti-patterns from prior phases:** do not modify mesh files (frozen artifact)
```
