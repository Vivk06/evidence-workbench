# ML experiment checklist

| Check | How to test, free and local |
|---|---|
| Split overlap | hash each sample's identifying content; intersect the train, validation and test hash sets |
| Group leakage | for the grouping key, check each group appears in one split only |
| Near-duplicates | compare normalised inputs (rounded features, perceptual image hashes, configuration hashes) across splits |
| Fit scope | find every `.fit`/`fit_transform` call and the data it receives |
| Early stopping | the stopping criterion reads validation data, never test data |
| Seeds | list seeds in configs and logs; compute mean and standard deviation of the reported metric |
| Exclusions | count rows dropped between raw data and training data; each has a reason |
| Labels | the label column and its transformation are identical across compared runs |
| Metric tolerance | the acceptance threshold appears in a document dated before the test evaluation |

Report table: check, evidence, finding, verdict.
