# SENTRY-VaR-ST reproducibility resources

This repository accompanies **SENTRY-VaR-ST: Mention-Level Semantic Transport for Robust VaR Forecasting from Multi-Event Financial News**.

## Scope

The release is limited to the headline FNSPID main experiment and the temporal diagnostics requested during review. It does not include ablation studies, sensitivity analyses, semantic-backbone controls, the Astock external evaluation, or other secondary experiments.

The intended reproducibility scope covers:

- the purged 2020--2023 FNSPID test protocol;
- the twelve headline models at the 95%, 97.5%, and 99% VaR levels;
- pooled breach rates and daily breach-rate series;
- daily mean pinball-loss series and DM-HAC tests;
- dependence-aware bootstrap and DQ diagnostics;
- the COVID-19 crash-window diagnostic;
- the exact prompts used by the main semantic pipeline;
- the final semantic transport-cost matrix used by the main experiment.

## Current release status

The repository currently contains:

- the 986 eligible forecast-date index;
- the COVID-19 crash-window daily 95% breach-rate table;
- the crash-window realized 20-day maximum-adverse-excursion summary;
- manuscript-facing summaries for DM-HAC, dependence-aware inference, and daily breach clustering;
- the final numerical semantic transport-cost matrix;
- evaluation helpers, consistency checks, and GitHub Actions validation;
- a verified summary of the prompt protocol.

The complete 986-date per-model daily breach and daily pinball-loss series, the exact main-experiment prompts, and one end-to-end statistical reproduction script still need to be exported from the authoritative experiment workspace.

## Repository layout

```text
data/             main-experiment derived data and the eligible date index
results/          manuscript-facing main statistical summaries
scripts/          evaluation helpers and release validation
prompts/          main-experiment prompt materials
cost_matrices/    final main-experiment semantic cost matrix
docs/             file mapping and release status
```

## Validation

```bash
python -m pip install -r requirements.txt
python scripts/validate_release.py
```

The validation checks date counts, table schemas, confidence-interval containment, COVID-window closure, cross-table maxima, and cost-matrix symmetry.

## Data scope

Copyrighted news text, original market records, identifiable company-day rows, per-origin thresholds, and annotation records are not redistributed. The repository contains only non-source-restricted materials needed for the main-experiment statistical release.
