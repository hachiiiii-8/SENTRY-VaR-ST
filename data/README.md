# Main-experiment evaluation data

- `test_date_index.csv.gz`: the 986 eligible forecast dates used by the FNSPID temporal diagnostics.
- `covid_daily_breach_95.csv`: daily cross-sectional 95% breach rates for the 20 crash-window forecast dates.
- `covid_mae_distribution.csv`: the realized 20-day maximum adverse excursion summary for the same 81,001 eligible origins.

Convert the date index to an uncompressed CSV with:

```bash
python scripts/export_test_date_index.py
```
