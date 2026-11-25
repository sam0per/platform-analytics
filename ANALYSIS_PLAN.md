# Analysis plan: churn-model accuracy by region

Written on 2026-11-25, before the orchestrator judged any regional result. Change it only in a reviewed pull request.

## Question

Does the churn model hold up in each of the five customer regions?

## Metric

Test-set accuracy of the churn model, in whole-number percent, for each region.

## Fixed setup

- Data: `customer_model_features` and `customer_activity.region`, as built by `uv run dbt build`.
- Model and split: `fit()` in `checks/accuracy_clean.py`. That is logistic regression, 30% test set, `random_state=42`, stratified on `churned`. One model trains on the 70% training split across all regions. Each region slices the 30% test set.
- Interval: bootstrap of the region's test customers, 2,000 resamples, seed 42, percentile 95% interval.
- Command: `uv run python analysis/region_accuracy.py <region>`. No other split, seed or model.

## Acceptance rule

Accept a regional result only when it reports all three:

1. the accuracy,
2. its 95% interval,
3. n, the number of test customers in the region.

An accepted result has this shape: `<Region>: accuracy NN% (95% CI LL-HH%), n=NNN`.
Reject a result that lacks any of the three. A single number is not a result.
Send a rejected result back to the subagent that produced it, with the rule it broke.

## Decision rule

The model holds in a region when that region's 95% interval contains 71%, the overall accuracy from `uv run check accuracy_clean`.
Decide only when all five regions have an accepted result.
