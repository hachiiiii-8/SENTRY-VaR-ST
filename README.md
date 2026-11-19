# SENTRY-VaR-ST

**Mention-Level Semantic Transport for Robust VaR Forecasting from Multi-Event Financial News**

This repository provides the evaluation resources for the main FNSPID experiment in the SENTRY-VaR-ST study.

## Method overview

SENTRY-VaR-ST forecasts company-day Value-at-Risk (VaR) for the largest adverse price movement over a future trading horizon. It represents both concurrent financial-news events and uncertainty in the attribution of individual event mentions.

The main pipeline is:

1. **Atomic mentions:** Split each available masked news title into independent event propositions.
2. **Semantic attribution:** Apply three Qwen3-14B semantic readings, normalize the conditional likelihoods of ten fixed event labels, and calibrate mention-level posteriors.
3. **Transport sets:** Aggregate the observed multi-event composition, then assign mention-specific uncertainty budgets over a financial-event transport-cost matrix.
4. **Risk channels:** Condition monotone loss-distribution channels on market history and the observed event composition.
5. **Robust VaR:** Reweight the channels over admissible semantic compositions, invert the worst-case breach curve, and apply the global calibration-year residual correction.

## Main evaluation protocol

| Item | Protocol |
|---|---|
| Dataset | FNSPID, U.S. equities |
| Model fitting | 2007–2017 |
| Validation and model selection | 2018 |
| Residual calibration | 2019 |
| Final test | 2020–2023 |
| Forecast target | Future 20-trading-day maximum adverse excursion |
| Confidence levels | 95%, 97.5%, and 99% |
| Main comparisons | SENTRY-VaR-ST and 11 baselines |
| Eligible test dates | 986 |
| Eligible test company-day origins | 4,041,318 |

Forecast origins require a complete future target window within their chronological block. The main results use the same eligible origins and global one-sided residual-correction protocol for all models.

## Evaluation measures

- **Breach rate (BR):** Fraction of eligible company-day realized losses exceeding the calibrated VaR threshold. Pooled BR uses the total eligible-origin count.
- **Absolute breach gap:** Absolute deviation of BR from the nominal exceedance rate, in percentage points.
- **Pinball loss:** Quantile score, evaluated on the normalized loss scale and reported in the manuscript's percentage-point units.
- **Mean VaR:** Average calibrated risk threshold, reported in percent and interpreted together with coverage and pinball loss.
- **Tail Recall@5%:** Overlap between the most severe 5% of realized losses and the 5% ranked highest by predicted 99% VaR.

Temporal inference uses daily cross-sectional metrics: a 20-lag HAC estimator for Diebold–Mariano tests, a 20-date moving-block bootstrap (1,000 replications) for breach-rate intervals, and a non-overlapping 20-date representation for the DQ diagnostic. The raw daily breach-rate series is used for dispersion, stress maxima, and autocorrelation.

## Files

| Directory | Contents |
|---|---|
| [data](data/) | Eligible forecast-date index and COVID-19 crash-window daily diagnostics |
| [results](results/) | Main results: Table 1, Table 2 DM-HAC, Table 18, and Table 19 |
| [scripts](scripts/) | Evaluation helpers, consistency checks, and statistical recomputation |
| [prompts](prompts/) | Atomic-decomposition prompt and three semantic-reading prompts |
| [cost_matrices](cost_matrices/) | Final numerical 10 × 10 semantic transport-cost matrix |
| [docs](docs/) | Data schema and manuscript-to-file mapping |

The COVID-19 table covers forecast dates from **14 February to 13 March 2020**, with 81,001 eligible origins. The corresponding realized 20-day adverse-excursion distribution is in `data/covid_mae_distribution.csv`.

## Installation and validation

Use Python 3.11 or a compatible environment:

```bash
python -m pip install -r requirements.txt
python scripts/validate_release.py
```

The validator checks the 986-date index, the published summary-table structure, the COVID-19 window counts and peak consistency, and the transport-cost matrix.

To export the date index as an uncompressed CSV:

```bash
python scripts/export_test_date_index.py
```

## Statistical recomputation

The recomputation script accepts a date-level evaluation export, with one row per **date × model × confidence level**. The file format is described in [docs/daily_metrics_format.md](docs/daily_metrics_format.md).

```bash
python scripts/reproduce_statistics.py --daily data/daily_model_metrics_986.csv.gz
```

The script generates pooled breach/pinball statistics, daily breach summaries, DM-HAC comparisons, moving-block intervals, and COVID-window cross-checks. Results and comparisons with the published tables are written to `outputs/`.

Bootstrap configuration can be set through command-line arguments. The optional `--dq-preview` evaluates a separate two-lag HC1 block-mean diagnostic.

## Result-to-paper mapping

See [docs/manuscript_mapping.md](docs/manuscript_mapping.md) for the corresponding manuscript and reviewer-response tables.
