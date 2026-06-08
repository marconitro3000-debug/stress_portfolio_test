from __future__ import annotations

import numpy as np
import pandas as pd


def component_risk_contribution(weights: pd.Series, covariance: pd.DataFrame) -> pd.Series:
    cov = covariance.loc[weights.index, weights.index]
    w = weights.to_numpy()
    sigma = float(np.sqrt(w @ cov.to_numpy() @ w))
    if sigma <= 0:
        return pd.Series(0.0, index=weights.index)
    marginal = cov.to_numpy() @ w / sigma
    component = w * marginal
    return pd.Series(component, index=weights.index).sort_values(key=np.abs, ascending=False)


def scenario_loss_contribution(weights: pd.Series, asset_shocks: pd.Series) -> pd.Series:
    aligned = asset_shocks.loc[weights.index]
    return (weights * aligned).sort_values(key=np.abs, ascending=False)


def sector_loss_contribution(weights: pd.Series, asset_shocks: pd.Series, sectors: pd.Series | None) -> pd.Series:
    contrib = scenario_loss_contribution(weights, asset_shocks)
    if sectors is None or sectors.empty:
        return pd.Series(dtype=float)
    return contrib.groupby(sectors.loc[contrib.index]).sum().sort_values(key=np.abs, ascending=False)
