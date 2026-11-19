"""Evaluation helpers used by the SENTRY-VaR-ST diagnostic release."""
from __future__ import annotations

from typing import Iterable

import numpy as np
from scipy import stats


def _as_nonempty_1d(values: Iterable[float], name: str) -> np.ndarray:
    array = np.asarray(values, dtype=float)
    if array.ndim != 1 or array.size == 0:
        raise ValueError(f"{name} must be a non-empty one-dimensional array")
    if not np.all(np.isfinite(array)):
        raise ValueError(f"{name} contains non-finite values")
    return array


def breach_rate(loss: Iterable[float], var: Iterable[float]) -> float:
    """Return the realized breach rate in percent."""
    loss_array = _as_nonempty_1d(loss, "loss")
    var_array = _as_nonempty_1d(var, "var")
    if loss_array.shape != var_array.shape:
        raise ValueError("loss and var must have the same shape")
    return float(100.0 * np.mean(loss_array > var_array))


def pinball_loss(loss: Iterable[float], var: Iterable[float], alpha: float) -> float:
    """Return pinball loss on the normalized loss scale, multiplied by 100."""
    loss_array = _as_nonempty_1d(loss, "loss")
    var_array = _as_nonempty_1d(var, "var")
    if loss_array.shape != var_array.shape:
        raise ValueError("loss and var must have the same shape")
    if not 0.0 < alpha < 1.0:
        raise ValueError("alpha must be in (0, 1)")
    residual = loss_array - var_array
    score = np.where(residual >= 0.0, alpha * residual, (alpha - 1.0) * residual)
    return float(100.0 * np.mean(score))


def moving_block_bootstrap_mean_ci(
    daily: Iterable[float],
    block_length: int = 20,
    replications: int = 1000,
    seed: int = 2026,
) -> tuple[float, float]:
    """Return a percentile CI for the mean of a daily series."""
    series = _as_nonempty_1d(daily, "daily")
    if block_length <= 0 or series.size < block_length:
        raise ValueError("block_length must be positive and no larger than the series")
    if replications <= 0:
        raise ValueError("replications must be positive")

    rng = np.random.default_rng(seed)
    starts = np.arange(series.size - block_length + 1)
    number_of_blocks = int(np.ceil(series.size / block_length))
    means = np.empty(replications, dtype=float)
    for index in range(replications):
        sampled_starts = rng.choice(starts, number_of_blocks, replace=True)
        resample = np.concatenate(
            [series[start : start + block_length] for start in sampled_starts]
        )[: series.size]
        means[index] = resample.mean()
    lower, upper = np.quantile(means, [0.025, 0.975])
    return float(lower), float(upper)


def dm_hac(daily_loss_difference: Iterable[float], lag: int = 20) -> tuple[float, float]:
    """Return a Diebold-Mariano statistic with a Bartlett HAC variance estimate."""
    difference = _as_nonempty_1d(daily_loss_difference, "daily_loss_difference")
    if lag < 0 or difference.size <= lag:
        raise ValueError("lag must be non-negative and smaller than the series length")

    centered = difference - difference.mean()
    sample_size = difference.size
    long_run_variance = np.dot(centered, centered) / sample_size
    for offset in range(1, lag + 1):
        weight = 1.0 - offset / (lag + 1.0)
        covariance = np.dot(centered[offset:], centered[:-offset]) / sample_size
        long_run_variance += 2.0 * weight * covariance
    if long_run_variance <= 0.0:
        raise ValueError("estimated long-run variance is not positive")

    statistic = difference.mean() / np.sqrt(long_run_variance / sample_size)
    p_value = 2.0 * stats.norm.sf(abs(statistic))
    return float(statistic), float(p_value)



def tail_recall_at_5pct(
    realized_loss: Iterable[float],
    predicted_var99: Iterable[float],
) -> float:
    """Percentage overlap of the realized and predicted top-5% origin sets.

    Each input position refers to the same eligible company-day origin.
    Ties are resolved by stable input order; the top-set size is ceil(5% of N).
    """
    realized = _as_nonempty_1d(realized_loss, "realized_loss")
    predicted = _as_nonempty_1d(predicted_var99, "predicted_var99")
    if realized.shape != predicted.shape:
        raise ValueError("realized_loss and predicted_var99 must have the same shape")
    top_n = max(1, int(np.ceil(realized.size * 0.05)))
    tie_order = np.arange(realized.size)
    true_top = np.lexsort((tie_order, -realized))[:top_n]
    forecast_top = np.lexsort((tie_order, -predicted))[:top_n]
    return float(100.0 * np.intersect1d(true_top, forecast_top).size / top_n)


def pooled_dq_hc1(
    daily_breach_pct: Iterable[float],
    alpha: float,
    block_length: int = 20,
    lags: int = 2,
) -> tuple[float, float]:
    """Wald test of conditional coverage on non-overlapping breach-rate means.

    Block-average hit deviations are regressed on an intercept and lagged
    deviations. The joint Wald test uses an HC1 covariance estimate.
    Only complete non-overlapping blocks enter this statistic.
    """
    daily = _as_nonempty_1d(daily_breach_pct, "daily_breach_pct")
    if not 0.0 < alpha < 1.0:
        raise ValueError("alpha must be in (0, 1)")
    if np.any((daily < 0.0) | (daily > 100.0)):
        raise ValueError("breach percentages must be between 0 and 100")
    if block_length < 1 or lags < 1:
        raise ValueError("block_length and lags must be positive")

    n_blocks = daily.size // block_length
    if n_blocks - lags <= lags + 2:
        raise ValueError("Insufficient complete blocks for the DQ regression")
    block_rate = daily[:n_blocks * block_length].reshape(
        n_blocks, block_length
    ).mean(axis=1)
    hit = block_rate - 100.0 * (1.0 - alpha)
    response = hit[lags:]
    regressors = np.column_stack(
        [np.ones(response.size)]
        + [hit[lags - j:n_blocks - j] for j in range(1, lags + 1)]
    )
    n, k = regressors.shape
    if np.linalg.matrix_rank(regressors) < k:
        raise ValueError("DQ design matrix is rank deficient")
    beta = np.linalg.lstsq(regressors, response, rcond=None)[0]
    residual = response - regressors @ beta
    inv_xtx = np.linalg.inv(regressors.T @ regressors)
    score = regressors * residual[:, None]
    hc1 = (n / (n - k)) * inv_xtx @ (score.T @ score) @ inv_xtx
    if np.linalg.matrix_rank(hc1) < k:
        raise ValueError("DQ HC1 covariance is rank deficient")
    statistic = float(max(0.0, beta @ np.linalg.solve(hc1, beta)))
    return statistic, float(stats.chi2.sf(statistic, df=k))
