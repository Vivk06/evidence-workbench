---
name: validation-comparison
description: Compare simulation with experiment or benchmark data using the comparison error E = S - D against the validation uncertainty, within the validated domain (ASME V&V 20).
metadata:
  tags: [lean]
  output_mode: terminal
---

# Validation comparison

Command class: `read-only`.

Validation asks whether the model equations represent reality for the intended use. It
needs verified numbers first: code verification and a numerical uncertainty from
solution verification (`../solution-verification/SKILL.md`). Never call a verification
result a validation (Oberkampf & Roy 2010; AIAA G-077-1998).

## Method (ASME V&V 20-2009, `references/vv20.md`)

1. For each validation quantity: simulation value `S`, data value `D`, comparison error
   `E = S − D`.
2. Uncertainties: numerical `u_num` (from solution verification), input `u_input`
   (propagated parameter and boundary-condition uncertainty), data `u_D` (experimental).
3. Validation uncertainty `u_val = sqrt(u_num² + u_input² + u_D²)`.
4. The model error lies in about `E ± u_val` (state the coverage). If `|E| ≤ u_val`, the
   model error is within the noise of the comparison; if `|E| ≫ u_val`, `E` estimates the
   model error.

## Rules

- Data used to calibrate or tune a model cannot validate it; keep calibration and
  validation sets separate and say which is which.
- Claims stay inside the validated domain (parameter ranges, regimes, geometry class).
- Compare like with like: same quantity definition, location, averaging and units.

## Verdict

- PASS: `|E|` within the accuracy requirement stated in advance, with `u_val` small enough
  to make that statement meaningful.
- FAIL: `|E|` exceeds the requirement by more than `u_val`.
- INCONCLUSIVE: a missing uncertainty component, no stated requirement, data used for
  calibration, or a quantity outside the validated domain.
