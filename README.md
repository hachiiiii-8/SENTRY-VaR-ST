# SENTRY-VaR-ST

Reproducibility resources for **SENTRY-VaR-ST: Mention-Level Semantic Transport for Robust VaR Forecasting from Multi-Event Financial News**.

## Main experiment

The materials describe the FNSPID 2020–2023 headline evaluation, covering twelve forecasting models and the 95%, 97.5%, and 99% VaR levels.

## Repository contents

- `data/`: the 986-date eligible forecast-origin index, COVID-19 daily breach rates, and realized-loss summary.
- `results/`: manuscript results for Table 1, DM-HAC tests in Table 2, dependence-aware inference in Table 18, and daily breach statistics in Table 19.
- `scripts/`: evaluation functions, statistical recomputation, release validation, and date-index export.
- `prompts/`: atomic-decomposition and three semantic-reading prompts.
- `cost_matrices/`: the numerical transport-cost matrix for the headline semantic model.
- `docs/`: mapping between the repository files and manuscript tables, plus daily-export field definitions.

## Validate the release

```bash
python -m pip install -r requirements.txt
python scripts/validate_release.py
```

To expand the forecast-date index into a CSV:

```bash
python scripts/export_test_date_index.py
```

The validation checks date ordering and counts, summary schemas, interval containment, COVID-window counts and maxima, and the numerical matrix structure.

## Recompute headline evaluation diagnostics

Pooled breach and pinball statistics, daily summaries, DM-HAC tests, and block-bootstrap intervals can be recomputed from the date-level input specified in `docs/daily_metrics_format.md`:

```bash
python scripts/reproduce_statistics.py --daily data/daily_model_metrics_986.csv.gz
```

The script writes recomputed headline statistics and crosschecks against manuscript tables to `outputs/`. Bootstrap and DQ parameters are configurable through the script's command-line options.

## Data provenance

The released tables and date index are derived from the FNSPID evaluation protocol described in the manuscript. Source-data access follows the terms of the respective dataset providers.
