# Test-value rubric

Start from `RETAIN`. A test's value is the behavior it protects, not its line count,
age, simplicity, or current stability.

## Retain

Retain tests that uniquely protect a public or internal contract, parsing or configuration
boundary, historical regression, numerical behavior or tolerance, integration seam, or
failure mode. Also retain a simple test that most directly guards something that could
change. Examples are a default, a serialization format, an invalid input and a boundary
condition.

## Removal candidate

Use `REMOVAL CANDIDATE` only with cited evidence that the test:

- exactly duplicates another maintained behavioral check and has no distinct fixture,
  failure mode, platform, or execution path;
- asserts static boilerplate/defaults with no credible change vector and no contract or
  configuration boundary; or
- is dead or unreachable in the supported test workflow.

Record these for each candidate:

- the maintained test that replaces it, if any;
- the evidence from test discovery and CI;
- its production and fixture dependencies, and your confidence;
- a reversible experiment, such as leaving it out in a separate branch while the
  maintained suite runs.

Never remove, disable, weaken, or rewrite it as part of this audit.

## Inconclusive

Use `INCONCLUSIVE` when discovery, ownership, production linkage, history, fixture
meaning, or execution evidence is missing or conflicting. State exactly what evidence
would resolve the result.
