from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import stats


def historical_var(returns: pd.Series, confidence: float = 0.99) -> float:
    clean = returns.dropna().to_numpy()
    if clean.size == 0:
        return float("nan")
    return float(np.quantile(clean, 1.0 - confidence))


def historical_es(returns: pd.Series, confidence: float = 0.99) -> float:
    clean = returns.dropna()
    if clean.empty:
        return float("nan")
    var = historical_var(clean, confidence)
    tail = clean[clean <= var]
    return float(tail.mean()) if len(tail) else var


def parametric_var(returns: pd.Series, confidence: float = 0.99) -> float:
    mu = returns.mean()
    sigma = returns.std(ddof=1)
    z = stats.norm.ppf(1.0 - confidence)
    return float(mu + z * sigma)


def parametric_es(returns: pd.Series, confidence: float = 0.99) -> float:
    mu = returns.mean()
    sigma = returns.std(ddof=1)
    alpha = 1.0 - confidence
    z = stats.norm.ppf(alpha)
    return float(mu - sigma * stats.norm.pdf(z) / alpha)


def cornish_fisher_var(returns: pd.Series, confidence: float = 0.99) -> float:
    r = returns.dropna()
    if len(r) < 10:
        return historical_var(r, confidence)
    z = stats.norm.ppf(1.0 - confidence)
    s = stats.skew(r)
    k = stats.kurtosis(r, fisher=True)
    z_cf = z + (z**2 - 1) * s / 6 + (z**3 - 3 * z) * k / 24 - (2 * z**3 - 5 * z) * s**2 / 36
    return float(r.mean() + z_cf * r.std(ddof=1))
