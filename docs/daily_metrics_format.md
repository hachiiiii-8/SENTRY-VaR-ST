# Daily evaluation CSV

File: `data/daily_model_metrics_986.csv.gz`

One row per eligible forecast date, model, and VaR level: 986 dates × 12 models × 3 levels (35,496 rows).

| Field | Description |
|---|---|
| `ForecastDate` | ISO date in `test_date_index.csv.gz` |
| `Model` | Model name in Table 1 |
| `Level` | 95, 97.5, or 99 |
| `EligibleN` | Eligible company-day origins on the date (integer) |
| `BreachCount` | Realized breaches (integer) |
| `DailyMeanPinball` | Daily cross-sectional mean pinball loss, in manuscript units |
| `BreachRatePct` | Optional; daily breach rate in percent |
| `DailyMeanVaRPct` | Optional; daily mean VaR in percent |

All models use the same forecast-date and eligible-origin mask. The complete test contains 4,041,318 eligible origins; the 20-date COVID-19 diagnostic contains 81,001.

```bash
python scripts/reproduce_statistics.py --daily data/daily_model_metrics_986.csv.gz
```

Outputs are written to `outputs/`.
