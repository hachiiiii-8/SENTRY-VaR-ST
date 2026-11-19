"""Recompute FNSPID headline evaluation statistics from genuine date-level exports.

The daily metrics input has one row per date, model, and VaR confidence level.
The DQ regression and bootstrap seed are configurable for author verification.
This script never reconstructs unobserved model outputs from manuscript tables.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import chi2

from evaluation_helpers import dm_hac

ROOT = Path(__file__).resolve().parents[1]
LEVELS = (95.0, 97.5, 99.0)
PROPOSED = "SENTRY-VaR-ST"
COMPARATORS = (
    "CQR-Quantile",
    "Mention-level KL-DRO VaR",
    "Matched Market-Only VaR",
)
TABLE19_MODELS = (*COMPARATORS, PROPOSED)
REQUIRED = (
    "ForecastDate", "Model", "Level", "EligibleN", "BreachCount", "DailyMeanPinball"
)


def load_daily(path: Path) -> pd.DataFrame:
    frame = pd.read_csv(path)
    missing = sorted(set(REQUIRED) - set(frame.columns))
    if missing:
        raise ValueError(f"Daily metrics file lacks columns: {missing}")
    frame = frame.copy()
    frame["ForecastDate"] = pd.to_datetime(frame["ForecastDate"], errors="raise")
    frame["Level"] = (
        frame["Level"].astype(str).str.replace("%", "", regex=False)
        .str.replace("_", ".", regex=False).astype(float)
    )
    if not set(frame["Level"]).issubset(LEVELS):
        raise ValueError("VaR levels must be 95, 97.5, and 99.")
    numeric = ("EligibleN", "BreachCount", "DailyMeanPinball")
    for column in numeric:
        frame[column] = pd.to_numeric(frame[column], errors="raise")
        if not np.isfinite(frame[column]).all():
            raise ValueError(f"Non-finite {column}")
    if frame.duplicated(["ForecastDate", "Model", "Level"]).any():
        raise ValueError("Duplicate date/model/level rows")
    if ((frame["EligibleN"] <= 0) | (frame["BreachCount"] < 0)
            | (frame["BreachCount"] > frame["EligibleN"])
            | (frame["DailyMeanPinball"] < 0)).any():
        raise ValueError("Counts or losses outside the valid range")
    for column in ("EligibleN", "BreachCount"):
        if not np.allclose(frame[column], np.round(frame[column]), atol=1e-8):
            raise ValueError(f"{column} contains noninteger values")
        frame[column] = frame[column].astype(np.int64)

    names = pd.read_csv(ROOT / "results/table1_headline_results.csv")["Model"].tolist()
    days = pd.read_csv(ROOT / "data/test_date_index.csv.gz")
    official_dates = pd.to_datetime(days["ForecastDate"])
    if len(official_dates) != 986 or not official_dates.is_unique:
        raise ValueError("Expected 986 distinct eligible forecast dates")
    observed_dates = frame["ForecastDate"].drop_duplicates().sort_values()
    if not observed_dates.reset_index(drop=True).equals(
        official_dates.sort_values().reset_index(drop=True)
    ):
        raise ValueError("Daily metrics do not match the eligible date index")
    if set(frame["Model"]) != set(names):
        raise ValueError("Model set differs from headline Table 1")
    if len(frame) != 986 * len(names) * 3:
        raise ValueError("Incomplete date/model/level grid")
    shared_n = frame.groupby("ForecastDate")["EligibleN"].nunique()
    if (shared_n != 1).any():
        raise ValueError("Eligible origin counts vary across models or levels on a date")
    total_n = (frame[frame["Model"] == PROPOSED]
               .query("Level == 95.0")["EligibleN"].sum())
    if int(total_n) != 4_041_318:
        raise ValueError("Overall eligible-origin count differs from Table 8")
    frame["BreachRatePct"] = 100.0 * frame["BreachCount"] / frame["EligibleN"]
    if "BreachRatePct" in pd.read_csv(path, nrows=1).columns:
        supplied = pd.to_numeric(pd.read_csv(path)["BreachRatePct"], errors="coerce")
        if not np.allclose(frame["BreachRatePct"], supplied, atol=0.00051):
            raise ValueError("Supplied breach rates do not match breach counts")
    return frame.sort_values(["ForecastDate", "Model", "Level"]).reset_index(drop=True)


def summarize_headline(frame: pd.DataFrame) -> pd.DataFrame:
    grouped = frame.groupby(["Model", "Level"], sort=False)
    rows = []
    for (name, level), data in grouped:
        n = int(data["EligibleN"].sum())
        row = {
            "Model": name, "Level": level, "EligibleN": n,
            "PooledBRPct": 100.0 * data["BreachCount"].sum() / n,
            "PooledMeanPinball": np.average(
                data["DailyMeanPinball"], weights=data["EligibleN"]
            ),
        }
        if "DailyMeanVaRPct" in data.columns:
            if data["DailyMeanVaRPct"].isna().any():
                raise ValueError("DailyMeanVaRPct cannot be partially missing")
            row["PooledMeanVaRPct"] = np.average(
                data["DailyMeanVaRPct"], weights=data["EligibleN"]
            )
        rows.append(row)
    return pd.DataFrame(rows)


def summarize_daily(frame: pd.DataFrame) -> pd.DataFrame:
    rows = []
    subset = frame[frame["Model"].isin(TABLE19_MODELS)]
    for (name, level), x in subset.groupby(["Model", "Level"], sort=False):
        x = x.sort_values("ForecastDate")
        daily = x["BreachRatePct"].to_numpy()
        n = x["EligibleN"].to_numpy()
        k = x["BreachCount"].to_numpy()
        rows.append({
            "Model": name, "Level": level, "Dates": len(x),
            "PooledBR": 100 * k.sum() / n.sum(),
            "SD": daily.std(ddof=1),
            "P95": np.percentile(daily, 95),
            "Maximum": daily.max(),
            "RawDailyRho1": np.corrcoef(daily[1:], daily[:-1])[0, 1]
        })
    return pd.DataFrame(rows)


def bootstrap_pooled_ci(
    breaches: np.ndarray, eligible: np.ndarray, *,
    block_length: int, replications: int, seed: int
) -> tuple[float, float]:
    """Resample contiguous DATE blocks and recompute pooled firm-day BR."""
    length = len(breaches)
    starts = np.arange(length - block_length + 1)
    blocks = int(np.ceil(length / block_length))
    rng = np.random.default_rng(seed)
    samples = np.empty(replications, dtype=float)
    for j in range(replications):
        selected = rng.choice(starts, size=blocks, replace=True)
        indices = np.concatenate(
            [np.arange(s, s + block_length) for s in selected]
        )[:length]
        samples[j] = 100.0 * breaches[indices].sum() / eligible[indices].sum()
    return tuple(float(v) for v in np.quantile(samples, [0.025, 0.975]))


def dq_test_nonoverlap(
    daily_pct: np.ndarray, alpha: float, *, block: int = 20, lag: int = 2
) -> tuple[float, float]:
    """Proposed two-lag pooled-DQ regression: HC1 Wald for intercept and lagged hits.

    Verify the precise design matrix against the archived experiment script.
    """
    blocks = np.asarray([
        np.mean(daily_pct[i:i + block])
        for i in range(0, len(daily_pct) - block + 1, block)
    ])
    hits = blocks - 100.0 * (1 - alpha)
    if len(hits) <= lag + 4:
        raise ValueError("Insufficient non-overlapping blocks for DQ regression")
    y = hits[lag:]
    X = np.column_stack(
        [np.ones(len(y))] + [hits[lag-j:len(hits)-j] for j in range(1, lag+1)]
    )
    beta = np.linalg.lstsq(X, y, rcond=None)[0]
    residual = y - X @ beta
    n, k = X.shape
    inv_xx = np.linalg.pinv(X.T @ X)
    middle = X.T @ (X * (residual ** 2)[:, None])
    cov_hc1 = n / (n - k) * (inv_xx @ middle @ inv_xx)
    statistic = float(max(0.0, beta @ np.linalg.pinv(cov_hc1) @ beta))
    return statistic, float(chi2.sf(statistic, df=k))


def summarize_dependence(
    frame: pd.DataFrame, *, seed: int, block: int, repetitions: int, dq_lags: int
) -> pd.DataFrame:
    rows = []
    for name, x in frame.groupby("Model", sort=False):
        result = {"Model": name, "Dates": 986}
        for level, tag in ((95.0, "95"), (97.5, "97_5"), (99.0, "99")):
            level_frame = x[x["Level"] == level].sort_values("ForecastDate")
            n = level_frame["EligibleN"].to_numpy()
            k = level_frame["BreachCount"].to_numpy()
            rates = 100 * k / n
            low, high = bootstrap_pooled_ci(
                k, n, block_length=block, replications=repetitions, seed=seed
            )
            dq_stat, dq_p = dq_test_nonoverlap(
                rates, level / 100, block=block, lag=dq_lags
            )
            result.update({
                f"BR{tag}": 100 * k.sum() / n.sum(),
                f"CI{tag}_Lower": low, f"CI{tag}_Upper": high,
                f"DQstat{tag}": dq_stat, f"DQp{tag}": dq_p,
            })
        rows.append(result)
    return pd.DataFrame(rows)


def summarize_dm(frame: pd.DataFrame, hac_lag: int) -> pd.DataFrame:
    pivot = frame.pivot(
        index="ForecastDate", columns=["Model", "Level"],
        values="DailyMeanPinball"
    ).sort_index()
    rows = []
    for comparator in COMPARATORS:
        differential = []
        for level in LEVELS:
            delta = (pivot[(PROPOSED, level)] - pivot[(comparator, level)])
            differential.append(delta.to_numpy())
            stat, p = dm_hac(delta, lag=hac_lag)
            rows.append({
                "Comparator": comparator, "Level": level,
                "Dates": len(delta), "HACLag": hac_lag,
                "MeanDifference": float(delta.mean()),
                "DMStatistic": stat, "PValueTwoSided": p,
            })
        cross = np.mean(differential, axis=0)
        stat, p = dm_hac(cross, lag=hac_lag)
        rows.append({
            "Comparator": comparator, "Level": "Mean",
            "Dates": len(cross), "HACLag": hac_lag,
            "MeanDifference": float(cross.mean()),
            "DMStatistic": stat, "PValueTwoSided": p,
        })
    return pd.DataFrame(rows)


def compare_released(recomputed: pd.DataFrame, reference: pd.DataFrame,
                     *, join_on: list[str], columns: list[str], label: str,
                     tolerance: float = 0.00051) -> pd.DataFrame:
    merged = recomputed.merge(reference, on=join_on, suffixes=("_calc", "_paper"),
                              validate="one_to_one", how="inner")
    output = []
    for _, row in merged.iterrows():
        item = {key: row[key] for key in join_on}
        for col in columns:
            a, b = row.get(col + "_calc"), row.get(col + "_paper")
            if pd.isna(a) or pd.isna(b):
                continue
            output.append({
                "Source": label, **item, "Metric": col,
                "Recomputed": a, "Published": b,
                "Difference": float(a-b),
                "WithinReportingTolerance": bool(abs(a-b) <= tolerance),
            })
    return pd.DataFrame(output)


def covid_comparison(frame: pd.DataFrame) -> pd.DataFrame:
    covid = pd.read_csv(ROOT / "data/covid_daily_breach_95.csv")
    observed = frame[(frame["Level"] == 95.0) &
                     frame["ForecastDate"].between("2020-02-14", "2020-03-13")]
    if observed["ForecastDate"].nunique() != 20:
        raise ValueError("COVID-19 comparison expects 20 forecast dates")
    if int(observed[observed["Model"] == PROPOSED]["EligibleN"].sum()) != 81_001:
        raise ValueError("COVID-19 eligible counts differ from the manuscript")
    rec = observed.pivot(index="ForecastDate", columns="Model", values="BreachRatePct")
    ref = covid.set_index(pd.to_datetime(covid["Date"]))
    out = []
    for model in rec.columns:
        if model not in ref.columns:
            raise ValueError(f"COVID-19 reference has no column: {model}")
        for date, value in rec[model].items():
            reported = float(ref.loc[date, model])
            out.append({
                "Date": date.date().isoformat(), "Model": model,
                "Recomputed": float(value), "Published": reported,
                "Difference": float(value - reported),
                "WithinReportingTolerance": bool(abs(value-reported) <= .00051),
            })
    return pd.DataFrame(out)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--daily", type=Path,
                        default=ROOT/"data"/"daily_model_metrics_986.csv.gz")
    parser.add_argument("--output", type=Path, default=ROOT/"outputs")
    parser.add_argument("--seed", type=int, default=2026,
                        help="Candidate bootstrap seed; confirm against frozen run")
    parser.add_argument("--blocks", type=int, default=20)
    parser.add_argument("--repetitions", type=int, default=1000)
    parser.add_argument("--dq-lags", type=int, default=2)
    parser.add_argument("--hac-lag", type=int, default=20)
    args = parser.parse_args()

    if not args.daily.is_file():
        parser.error(f"Daily model export not found: {args.daily}")
    args.output.mkdir(parents=True, exist_ok=True)
    daily = load_daily(args.daily)
    headline = summarize_headline(daily)
    dm = summarize_dm(daily, args.hac_lag)
    dependence = summarize_dependence(
        daily, seed=args.seed, block=args.blocks,
        repetitions=args.repetitions, dq_lags=args.dq_lags
    )
    summary = summarize_daily(daily)
    covid = covid_comparison(daily)
    for filename, result in (
        ("table1_recomputed_core.csv", headline),
        ("table2_dm_recomputed.csv", dm),
        ("table18_recomputed.csv", dependence),
        ("table19_recomputed.csv", summary),
        ("covid_crosscheck.csv", covid),
    ):
        result.to_csv(args.output / filename, index=False, float_format="%.9f")

    # Preserve published results as immutable reference values.
    reference = pd.read_csv(ROOT/"results"/"table19_daily_summary.csv")
    summary["Level"] = summary["Level"].map(lambda n: f"{n:g}%")
    report = compare_released(
        summary, reference, join_on=["Model", "Level"],
        columns=["PooledBR", "SD", "P95", "Maximum", "RawDailyRho1"],
        label="Table 19",
    )
    report.to_csv(args.output/"table19_comparison.csv", index=False)

    # Also compare headline BR/pinball and the published HAC and inference statistics.
    table1 = pd.read_csv(ROOT/"results"/"table1_headline_results.csv")
    core_comparisons = []
    for _, r in headline.iterrows():
        pub = table1[table1["Model"] == r["Model"]]
        if len(pub) != 1:
            continue
        level_tag = {95.0: "95", 97.5: "97_5", 99.0: "99"}[r["Level"]]
        for field, expected_col in (
            ("PooledBRPct", f"BR{level_tag}Pct"),
            ("PooledMeanPinball", f"Pinball{level_tag}")
        ):
            expected = float(pub.iloc[0][expected_col])
            calc = float(r[field])
            core_comparisons.append({
                "Model": r["Model"], "Level": r["Level"], "Metric": field,
                "Recomputed": calc, "Published": expected, "Difference": calc-expected,
                "WithinReportingTolerance": abs(calc-expected) <= 0.0051,
            })
    pd.DataFrame(core_comparisons).to_csv(
        args.output/"table1_core_comparison.csv", index=False
    )

    published_dm = pd.read_csv(ROOT/"results"/"table2_dm_hac.csv")
    dm_copy = dm.copy()
    dm_copy["Level"] = dm_copy["Level"].astype(str).str.replace(".0", "", regex=False)
    dm_comparison = compare_released(
        dm_copy, published_dm, join_on=["Comparator", "Level"],
        columns=["MeanDifference", "DMStatistic", "PValueTwoSided"],
        label="Table 2", tolerance=0.00051
    )
    dm_comparison.to_csv(args.output/"table2_comparison.csv", index=False)

    published_dep = pd.read_csv(ROOT/"results"/"table18_dependence_inference.csv")
    dep_compare = compare_released(
        dependence, published_dep, join_on=["Model"],
        columns=[f"{prefix}{tag}" for tag in ("95", "97_5", "99")
                 for prefix in ("BR", "CI") if prefix == "BR"],
        label="Table 18 pooled BR", tolerance=0.0051,
    )
    dep_compare.to_csv(args.output/"table18_pooled_comparison.csv", index=False)

    print(f"Computed main-experiment statistics in {args.output}")
    for label, item in (("Table 1", pd.DataFrame(core_comparisons)),
                        ("Table 2", dm_comparison), ("Table 19", report)):
        print(f"{label}: {int(item['WithinReportingTolerance'].sum())}/"
              f"{len(item)} point comparisons within display tolerance")


if __name__ == "__main__":
    main()
