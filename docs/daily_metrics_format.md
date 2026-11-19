# Daily main-experiment export format

The evaluation table has one row for each eligible forecast date, model, and VaR level. The FNSPID main protocol has 986 dates, twelve headline models, and three confidence levels.

## Columns

| Name | Type | Meaning |
|---|---|---|
| `ForecastDate` | ISO date | Eligible date in the frozen test index |
| `Model` | string | Exact model name from Table 1 |
| `Level` | number | 95, 97.5, or 99 |
| `EligibleN` | integer | Firms with a valid target and prediction on this date |
| `BreachCount` | integer | Firm-day targets exceeding the calibrated VaR |
| `DailyMeanPinball` | float | Mean daily cross-sectional pinball score in manuscript units |
| `BreachRatePct` | float (optional) | 100 × BreachCount / EligibleN |
| `DailyMeanVaRPct` | float (optional) | Daily mean calibrated VaR in percentage units |

**Grain:** `ForecastDate × Model × Level`. All headline models use the common eligible-date and origin mask.

Store the original date-level results at `data/daily_model_metrics_986.csv.gz` as gzip-compressed CSV. The statistical script uses the source counts and daily loss means to recompute pooled and date-level quantities.

## Checks

The test index has 986 dates. The manuscript reports 4,041,318 eligible company-day origins across the 2020–2023 test block, and 81,001 origins on the twenty COVID-19 diagnostic dates.

The minimum source fields are `ForecastDate, Model, Level, EligibleN, BreachCount, DailyMeanPinball`.

## Recompute

```bash
python scripts/reproduce_statistics.py --daily data/daily_model_metrics_986.csv.gz
```

The command writes recomputed tables and differences from manuscript summaries into `outputs/`. The exact bootstrap seed and pooled-DQ regression formulation can be supplied with its command-line options after checking the original statistics configuration.
