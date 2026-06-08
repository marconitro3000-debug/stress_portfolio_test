from __future__ import annotations

import pandas as pd
import numpy as np


def volatility_regime(portfolio_returns: pd.Series, window: int = 21) -> dict[str, float | str]:
    rolling_vol = portfolio_returns.rolling(window).std()
    current = float(rolling_vol.iloc[-1])
    percentile = float((rolling_vol.dropna() <= current).mean()) if rolling_vol.dropna().size else float("nan")
    label = "low"
    if percentile >= 0.8:
        label = "high"
    elif percentile >= 0.5:
        label = "normal"
    return {"current_rolling_vol": current, "vol_percentile": percentile, "regime": label}


def regime_weighted_returns(returns: pd.DataFrame, market_returns: pd.Series, similarity_window: int = 63) -> pd.Series:
    """Simple current-regime weighting: higher weight to periods with similar trailing vol."""
    rolling_vol = market_returns.rolling(similarity_window).std()
    current = rolling_vol.iloc[-1]
    distance = (rolling_vol - current).abs()
    scale = distance.dropna().median()
    if not np.isfinite(scale) or scale <= 0:
        weights = pd.Series(1.0, index=returns.index)
    else:
        weights = np.exp(-distance / scale).reindex(returns.index).fillna(0.0)
    return weights / weights.sum() if weights.sum() > 0 else pd.Series(1 / len(returns), index=returns.index)
