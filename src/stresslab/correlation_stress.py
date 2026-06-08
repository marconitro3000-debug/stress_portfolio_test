from __future__ import annotations

import numpy as np
import pandas as pd


def nearest_correlation(matrix: np.ndarray, eps: float = 1e-8) -> np.ndarray:
    sym = (matrix + matrix.T) / 2
    vals, vecs = np.linalg.eigh(sym)
    vals = np.clip(vals, eps, None)
    repaired = (vecs * vals) @ vecs.T
    d = np.sqrt(np.diag(repaired))
    return repaired / np.outer(d, d)


def stress_correlation(corr: pd.DataFrame, uplift: float) -> pd.DataFrame:
    arr = corr.to_numpy().copy()
    off_diag = ~np.eye(arr.shape[0], dtype=bool)
    arr[off_diag] = arr[off_diag] + uplift * (1.0 - arr[off_diag])
    arr = np.clip(arr, -0.99, 0.99)
    np.fill_diagonal(arr, 1.0)
    arr = nearest_correlation(arr)
    return pd.DataFrame(arr, index=corr.index, columns=corr.columns)


def downside_correlation(returns: pd.DataFrame, market_returns: pd.Series | None = None, quantile: float = 0.2) -> pd.DataFrame:
    if market_returns is None:
        market_returns = returns.mean(axis=1)
    threshold = market_returns.quantile(quantile)
    downside = returns.loc[market_returns <= threshold]
    if len(downside) < 5:
        return returns.corr()
    return downside.corr()


def correlation_uplift(returns: pd.DataFrame, quantile: float = 0.2) -> dict[str, float]:
    normal = returns.corr()
    down = downside_correlation(returns, quantile=quantile)
    mask = ~np.eye(len(normal), dtype=bool)
    normal_avg = float(normal.to_numpy()[mask].mean())
    down_avg = float(down.to_numpy()[mask].mean())
    return {
        "average_correlation": normal_avg,
        "downside_average_correlation": down_avg,
        "uplift": down_avg - normal_avg,
        "uplift_ratio": down_avg / normal_avg if abs(normal_avg) > 1e-12 else float("nan"),
    }


def covariance_from_vol_corr(vol: pd.Series, corr: pd.DataFrame) -> pd.DataFrame:
    v = vol.loc[corr.index].to_numpy()
    cov = corr.to_numpy() * np.outer(v, v)
    return pd.DataFrame(cov, index=corr.index, columns=corr.columns)
