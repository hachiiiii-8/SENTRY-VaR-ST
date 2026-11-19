# Main FNSPID results

Results are stored as numerical CSV tables corresponding to the manuscript.

| File | Contents |
|---|---|
| `table1_headline_results.csv` | BR, pinball, mean VaR at three confidence levels, plus Tail Recall@5%, for twelve models |
| `table2_dm_hac.csv` | SENTRY versus CQR, KL-DRO, and matched market-only; DM statistics and two-sided p-values at three levels and their cross-level mean |
| `table18_dependence_inference.csv` | Pooled BR, 95% moving-block confidence intervals, and pooled-DQ p-values |
| `table19_daily_summary.csv` | Pooled BR alongside raw-daily standard deviation, 95th percentile, maximum, and lag-1 autocorrelation |

**Statistical units:** Pooled BR is calculated across eligible company-day origins. Table 19's SD, P95, maximum, and autocorrelation describe the raw daily cross-sectional breach-rate series. DM-HAC tests use 986 date-level mean pinball-loss differences with a 20-lag HAC standard error.

The moving-block intervals use contiguous 20-date blocks and resample all firms within a sampled date together. DQ inference is reported separately for non-overlapping 20-date means.

[Manuscript table mapping](../docs/manuscript_mapping.md)
