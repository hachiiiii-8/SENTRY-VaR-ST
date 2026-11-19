# SENTRY-VaR-ST

Evaluation materials for **SENTRY-VaR-ST: Mention-Level Semantic Transport for Robust VaR Forecasting from Multi-Event Financial News**.

The main FNSPID experiment covers 2020–2023, twelve models, and the 95%, 97.5%, and 99% VaR levels.

## Contents

- `data/`: eligible forecast-date index and COVID-19 diagnostics.
- `results/`: Tables 1, 2 (DM-HAC), 18, and 19.
- `scripts/`: statistical evaluation and validation.
- `prompts/`: atomic decomposition and three semantic readings.
- `cost_matrices/`: main semantic transport-cost matrix.
- `docs/`: table mapping and daily-data schema.

## Usage

```bash
python -m pip install -r requirements.txt
python scripts/validate_release.py
```

To recompute the main statistics from a date-level export (format: `docs/daily_metrics_format.md`):

```bash
python scripts/reproduce_statistics.py --daily data/daily_model_metrics_986.csv.gz
```
