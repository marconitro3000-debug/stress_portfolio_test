from __future__ import annotations

from dataclasses import dataclass
import pandas as pd
import numpy as np


@dataclass(frozen=True)
class Portfolio:
    weights: pd.Series
    sectors: pd.Series | None = None

    @classmethod
    def from_frame(cls, frame: pd.DataFrame, normalize: bool = True) -> "Portfolio":
        required = {"asset", "weight"}
        missing = required.difference(frame.columns)
        if missing:
            raise ValueError(f"Portfolio file missing columns: {sorted(missing)}")
        if frame["asset"].duplicated().any():
            duplicates = frame.loc[frame["asset"].duplicated(), "asset"].tolist()
            raise ValueError(f"Portfolio contains duplicate assets: {sorted(set(duplicates))}")

        weights = frame.set_index("asset")["weight"].astype(float)
        if weights.isna().any():
            raise ValueError("Portfolio weights contain missing values")
        if not np.isfinite(weights.to_numpy()).all():
            raise ValueError("Portfolio weights must be finite numbers")

        total_weight = float(weights.sum())
        gross_exposure = float(weights.abs().sum())
        if normalize:
            scale = total_weight if np.all(weights >= 0) else gross_exposure
            if np.isclose(scale, 0.0):
                raise ValueError("Portfolio weights cannot all be zero")
            weights = weights / scale
        elif not np.isclose(total_weight, 1.0, atol=1e-6):
            raise ValueError("Portfolio weights must sum to 1.0 when normalization is disabled")

        sectors = None
        if "sector" in frame.columns:
            sectors = frame.set_index("asset")["sector"].astype(str)
        return cls(weights=weights, sectors=sectors)

    def align_returns(self, returns: pd.DataFrame) -> pd.DataFrame:
        missing = set(self.weights.index) - set(returns.columns)
        if missing:
            raise ValueError(f"Returns missing portfolio assets: {sorted(missing)}")
        return returns.loc[:, self.weights.index].astype(float).dropna(how="all")

    def portfolio_returns(self, returns: pd.DataFrame) -> pd.Series:
        aligned = self.align_returns(returns).fillna(0.0)
        return aligned @ self.weights

    def sector_exposure(self) -> pd.Series:
        if self.sectors is None:
            return pd.Series(dtype=float)
        return self.weights.groupby(self.sectors).sum().sort_values(key=np.abs, ascending=False)
