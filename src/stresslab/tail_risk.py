from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import stats
from .var_es import historical_var, historical_es


def student_t_var_es(returns: pd.Series, confidence: float = 0.99, df: float = 5.0) -> dict[str, float]:
    r = returns.dropna()
    mu = r.mean()
    sigma = r.std(ddof=1)
    alpha = 1 - confidence
    q = stats.t.ppf(alpha, df)
    var = mu + sigma * q
    # Left-tail ES for standardized t distribution.
    es_std = -((df + q**2) / (df - 1)) * stats.t.pdf(q, df) / alpha
    es = mu + sigma * es_std
    return {"student_t_var": float(var), "student_t_es": float(es)}


def evt_pot_proxy(returns: pd.Series, confidence: float = 0.99, threshold_quantile: float = 0.1) -> dict[str, float]:
    losses = -returns.dropna()
    if len(losses) < 50:
        return {"evt_var": -historical_var(returns, confidence), "evt_es": -historical_es(returns, confidence)}
    threshold = losses.quantile(1 - threshold_quantile)
    exceedances = losses[losses > threshold] - threshold
    if len(exceedances) < 10:
        return {"evt_var": -historical_var(returns, confidence), "evt_es": -historical_es(returns, confidence)}
    shape, loc, scale = stats.genpareto.fit(exceedances, floc=0)
    p_exceed = len(exceedances) / len(losses)
    tail_prob = 1 - confidence
    if abs(shape) < 1e-8:
        var_loss = threshold + scale * np.log(p_exceed / tail_prob)
    else:
        var_loss = threshold + scale / shape * ((p_exceed / tail_prob) ** shape - 1)
    es_loss = (var_loss + scale - shape * threshold) / (1 - shape) if shape < 1 else float("inf")
    return {"evt_var": float(-var_loss), "evt_es": float(-es_loss), "gpd_shape": float(shape)}
