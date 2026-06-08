from __future__ import annotations

import pandas as pd


def liquidity_adjusted_loss(weights: pd.Series, base_loss: float, liquidity_haircut: float) -> float:
    gross_exposure = float(weights.abs().sum())
    return float(base_loss - abs(liquidity_haircut) * gross_exposure)


def liquidation_cost(weights: pd.Series, haircut_by_asset: pd.Series | None = None, default_haircut: float = 0.0) -> pd.Series:
    if haircut_by_asset is None:
        haircut_by_asset = pd.Series(default_haircut, index=weights.index)
    else:
        haircut_by_asset = haircut_by_asset.reindex(weights.index).fillna(default_haircut)
    return -(weights.abs() * haircut_by_asset).sort_values(ascending=True)
