"""Validate the currently released SENTRY-VaR-ST derived artifacts."""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
RESULTS = ROOT / "results"
COSTS = ROOT / "cost_matrices"


def require_columns(frame: pd.DataFrame, required: set[str], name: str) -> None:
    missing = required.difference(frame.columns)
    if missing:
        raise AssertionError(f"{name} is missing columns: {sorted(missing)}")


def main() -> None:
    date_index = pd.read_csv(DATA / "test_date_index.csv")
    require_columns(date_index, {"ForecastDate", "Year"}, "test_date_index.csv")
    assert len(date_index) == 986
    assert date_index["ForecastDate"].is_unique
    assert pd.to_datetime(date_index["ForecastDate"]).is_monotonic_increasing

    dm = pd.read_csv(RESULTS / "table2_dm_hac.csv")
    require_columns(dm, {"Comparator", "Level", "Dates", "HACLag", "DMStatistic"}, "table2_dm_hac.csv")
    assert set(dm["Dates"]) == {986}
    assert set(dm["HACLag"]) == {20}

    table18 = pd.read_csv(RESULTS / "table18_dependence_inference.csv")
    assert set(table18["Dates"]) == {986}
    for level in ("95", "97_5", "99"):
        lower = table18[f"CI{level}_Lower"]
        point = table18[f"BR{level}"]
        upper = table18[f"CI{level}_Upper"]
        assert np.all(lower <= point)
        assert np.all(point <= upper)

    table19 = pd.read_csv(RESULTS / "table19_daily_summary.csv")
    require_columns(
        table19,
        {"Model", "Level", "Dates", "PooledBR", "SD", "P95", "Maximum", "RawDailyRho1"},
        "table19_daily_summary.csv",
    )
    assert set(table19["Dates"]) == {986}
    assert np.all(table19["SD"] >= 0.0)
    assert np.all(table19["P95"] <= table19["Maximum"])
    assert np.all(table19["RawDailyRho1"].between(-1.0, 1.0))

    covid = pd.read_csv(DATA / "covid_daily_breach_95.csv")
    assert len(covid) == 20
    assert covid["Date"].is_unique
    assert int(covid["Eligible_N"].sum()) == 81001

    mae = pd.read_csv(DATA / "covid_mae_distribution.csv")
    assert len(mae) == 1
    assert int(mae.loc[0, "EligibleOrigins"]) == int(covid["Eligible_N"].sum())
    assert mae.loc[0, "Median"] <= mae.loc[0, "P90"] <= mae.loc[0, "P95"] <= mae.loc[0, "Maximum"]

    model_mapping = {
        "Matched Market-Only VaR": "Matched Market-Only VaR",
        "CQR-Quantile": "CQR-Quantile",
        "Mention-level KL-DRO VaR": "Mention-level KL-DRO VaR",
        "SENTRY-VaR-ST": "SENTRY-VaR-ST",
    }
    for table_model, covid_column in model_mapping.items():
        row = table19[(table19["Model"] == table_model) & (table19["Level"] == "95%")]
        assert len(row) == 1
        released_maximum = float(row.iloc[0]["Maximum"])
        covid_maximum = float(covid[covid_column].max())
        assert np.isclose(released_maximum, covid_maximum, atol=5e-4)

    cost = pd.read_csv(COSTS / "final_semantic_transport_cost.csv", index_col=0).to_numpy(float)
    assert cost.shape[0] == cost.shape[1]
    assert np.allclose(cost, cost.T)
    assert np.allclose(np.diag(cost), 0.0)
    assert np.all(cost >= 0.0)

    print("Current release validation passed.")
    print("Note: full 986-date daily model series are not part of this initial migration.")


if __name__ == "__main__":
    main()
