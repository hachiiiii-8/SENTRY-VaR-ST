# SENTRY-VaR-ST reproducibility resources

This repository accompanies **SENTRY-VaR-ST: Mention-Level Semantic Transport for Robust VaR Forecasting from Multi-Event Financial News**.

## Current release status

The repository currently contains the non-source-restricted materials that are already available and internally checked:

- the 986 eligible forecast-date index;
- the COVID-19 crash-window daily 95% breach-rate table;
- the crash-window realized 20-day maximum-adverse-excursion summary;
- manuscript-facing summaries for DM-HAC, dependence-aware inference, and daily breach clustering;
- the final numerical semantic transport-cost matrix;
- evaluation helpers and consistency checks;
- a documented summary of the prompt protocol currently available for release.

This is an initial migration, not yet the complete end-to-end reproducibility package requested during review. The complete 986-date per-model daily breach and daily pinball-loss series, verbatim prompts, component cost matrices, and table-reproduction scripts still need to be exported from the authoritative experiment workspace.

## Repository layout

```text
data/             released derived data and the eligible date index
results/          manuscript-facing statistical summaries
scripts/          evaluation helpers and release validation
prompts/          currently verified prompt specification
cost_matrices/    released final semantic cost matrix
docs/             file-to-manuscript mapping and release status
```

## Validation

Create a Python environment and run:

```bash
python -m pip install -r requirements.txt
python scripts/validate_release.py
```

The validation checks date counts, table schemas, confidence-interval containment, COVID-window closure, cross-table maxima, and cost-matrix symmetry.

## Data scope

Copyrighted news text, original market records, identifiable company-day rows, per-origin thresholds, and annotation records are not included in this initial migration. Only derived, non-source-restricted artifacts are stored here.
