# FNSPID evaluation data

The data directory stores derived records from the main FNSPID evaluation.

| File | Description |
|---|---|
| `test_date_index.csv.gz` | The 986 eligible forecast dates for the 2020–2023 test |
| `covid_daily_breach_95.csv` | Daily 95% cross-sectional breach rates for all twelve models, 14 February–13 March 2020 |
| `covid_mae_distribution.csv` | Distribution of realized 20-day maximum adverse excursion for the same 81,001 eligible origins |

Each date in the COVID-19 breach table has its own `Eligible_N` denominator. Model columns report percentages, calculated over the eligible origins for that date.

The date index can be expanded with:

```bash
python scripts/export_test_date_index.py
```

For full-period statistical recomputation, see the date-level input schema in [docs/daily_metrics_format.md](../docs/daily_metrics_format.md).
