# Low-value test patterns

Detected statically by `scripts/audit_tests.py`; each is a lead for review.

| Finding | Severity | Why it matters | Usual fix |
|---|---|---|---|
| no-assertion | high | the test passes whatever the code does | assert on the result, or remove |
| tautology | high | `assert True`, `assert x == x` | assert on behaviour, or remove |
| duplicate | high | same body as another test | remove one |
| trivial-only | review | only `is not None`, `isinstance`, `len(x) > 0` | assert on the value that matters |
| mock-only | review | proves a call happened, not that the result is right | assert on the output or state |
| private-patch | review | forces a private state; a real caller may never reach it | test through the public path, or remove |
| type-misuse | review | expects TypeError/AttributeError from misuse | keep only if a realistic caller can pass that input |
| sleep | review | slow and timing-dependent | wait on a condition or inject a clock |
| large-parametrize | review | many cases, few distinct behaviours | keep one case per behaviour or boundary |
| same shape | merge | tests differ only in constants | one table-driven test |

Methods borrowed, not installed (all free):

- recov (https://github.com/jirikuncar/recov, MIT, at 9f9af9c): a test whose per-test
  coverage is contained in other tests' coverage is redundant. It runs the whole suite
  with coverage contexts, so in expensive repositories that run is user-executed.
- pytest-smell (https://github.com/maxpacs98/disertation; PyPI lists MIT) and the TEMPY and
  PyNose test-smell catalogues: empty tests, redundant assertions, sleepy tests.
- Beagle llm-artifacts-detection test criteria
  (https://github.com/existential-birds/beagle, Apache-2.0, at d1a7489): repeated setup,
  tests of library behaviour instead of project code, mocks at the wrong boundary.
