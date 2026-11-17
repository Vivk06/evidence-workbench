---
name: test-value-audit
description: Keep a test suite small and meaningful - audit size against a budget, flag low-value, unrealistic, duplicate and overlapping tests, and consolidate them with evidence.
metadata:
  tags: [lean]
  output_mode: terminal
---

# Test value audit

Use this skill as `$test-value-audit <repo> [--lean]`. Require one explicit, existing
repository path.

Command class: `read-only` for the audit; consolidating tests is `safe-local` and needs
the user's approval of the plan first. Identify the target's activation (profile or
`activate.sh`) and direct the user to activate it before any project command. Running a
full suite that is expensive, solver, MPI, optimizer, installs, publishing and any
deletion remain user-executed.

## 1. Measure

Run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/audit_tests.py <repo> [--paths <dirs>] [--budget N]`
(Codex: `../../scripts/audit_tests.py` from this skill's folder). It reads test files as
syntax trees and never runs them. Budget and paths come from the profile's `test_budget`
when present; otherwise ask for a budget or report size only. It lists no-assertion,
always-true, existence-only, mock-only, private-patch, type-misuse, sleep and
oversized-parametrize tests, exact duplicates, and same-shape groups that differ only in
constants. Each finding is a lead to check, not a verdict (`references/smells.md`).

## 2. Classify

Read [the test-value rubric](references/test-value-rubric.md). Classify each reviewed test
as `RETAIN`, `MERGE`, `REMOVAL CANDIDATE`, or `INCONCLUSIVE`, citing the test, the
behaviour it protects and the evidence. Apply the realistic-path rule: a test must name a
caller, input and failure that can happen in supported use. A test is a removal candidate
when it does one of three things:

- it forces private state that no caller can reach;
- it feeds inputs that the public interface rejects earlier;
- it guards a failure that is impossible or very unlikely.

Do not call a test low value because it is simple or stable.

## 3. Consolidate (after approval)

- Same-shape groups and overlapping tests become one table-driven test with one row per
  distinct case and a failure message that names the row.
- Exact duplicates and unrealistic tests are removed only with the user's approval; keep
  every distinct check, numerical tolerance and regression guard.
- Prove nothing was lost: the suite passes, and every removed assertion is covered by a
  named remaining test.
- Bring the suite within budget; record the before and after counts.

## 4. Before adding a test

Name the realistic failure it catches, and check that no existing test covers it. Prefer
a new row in an existing table to a new test. No tests that only check
formatting or non-emptiness, and no tests added just for a fix unless the task asks.

## Refusals

Never weaken, skip or delete a test to make a change pass. A removal candidate is a
review item, not permission. Normal mode reports in the conversation; `--lean` returns
only classifications, cited evidence, gaps and one next action.
