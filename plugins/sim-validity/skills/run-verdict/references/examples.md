# Gate families with example thresholds

Worked examples of how projects structure run gates. The numbers are illustrations from
real studies; a project sets its own in its profile or docs.

## Lettered gate families (environment, mesh, conservation, validation, field)

| Family | What it checks | Example gate |
|---|---|---|
| E environment | toolchain present, sources compile, static checks | every case compiles; event order passes a static check |
| M mesh admission | levels, wall placement, layer resolution, refinement behaviour | `lmax ≤ MAXLEVEL`; walls at their nominal position within 1e-12; at least 5 cells across each boundary layer |
| G conservation and health | discrete divergence, consistency ratio, finite values, solver caps, wall fluxes | `divJ ≤ TOLERANCE`; `0.99 ≤ divJ/resa ≤ 1.01` when `resa > 1e-14`; no NaN; multigrid iterations below the cap |
| V validation against analytic solutions | named quantities compared with closed-form results | steady value within 1 %; time constant within 5 %; observed order `p ≥ 1.5` (nominal 2) over three levels |
| F field-specific | imposed fields stay consistent after adaptation | imposed field re-evaluated after refinement within 1e-14 |

A machine-readable log line per event (for example `#tag i= t= dt= residual= divergence=`)
makes these gates checkable by script.

## Tiered gates by cost

| Tier | When | Example |
|---|---|---|
| A | every change, minutes | micro-timings of hot kernels |
| B | every change | output hashes of a short reference run must match for changes meant to be exact |
| C | checkpoints | full serial quality and wall-time run |
| D | checkpoints | study-scale runs |

Outcome-changing changes are judged against quality bands instead of hashes, with a veto
on any key metric dropping below a stated floor.
