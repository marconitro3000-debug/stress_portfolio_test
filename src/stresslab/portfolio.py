from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
import pandas as pd
import numpy as np


@dataclass(frozen=True)
class Portfolio:
    weights: pd.Series
    sectors: pd.Series | None = None

    _ASSET_COLUMNS = ("asset", "symbol", "ticker", "local symbol", "localsymbol")
    _WEIGHT_COLUMNS = (
        "weight",
        "weight %",
        "weight_pct",
        "portfolio weight",
        "portfolio_weight",
        "market value",
        "market_value",
        "marketvalue",
    )
    _SECTOR_COLUMNS = ("sector", "asset class", "asset_class", "industry")

    @staticmethod
    def _normalize_column_name(name: str) -> str:
        return re.sub(r"\s+", " ", name.strip().lower())

    @classmethod
    def _resolve_column(cls, frame: pd.DataFrame, candidates: tuple[str, ...]) -> str | None:
        normalized_map = {cls._normalize_column_name(column): column for column in frame.columns}
        for candidate in candidates:
            resolved = normalized_map.get(candidate)
            if resolved is not None:
                return resolved
        return None

    @staticmethod
    def _clean_weight_series(series: pd.Series) -> pd.Series:
        cleaned = series.astype(str).str.replace("%", "", regex=False).str.replace(",", "", regex=False).str.strip()
        return pd.to_numeric(cleaned, errors="coerce")

    @classmethod
    def _from_generic_frame(cls, frame: pd.DataFrame, normalize: bool = True) -> "Portfolio":
        if not isinstance(frame, pd.DataFrame):
            raise TypeError("Portfolio input must be a pandas DataFrame")

        asset_column = cls._resolve_column(frame, cls._ASSET_COLUMNS)
        weight_column = cls._resolve_column(frame, cls._WEIGHT_COLUMNS)
        sector_column = cls._resolve_column(frame, cls._SECTOR_COLUMNS)

        required = [name for name, column in (("asset", asset_column), ("weight", weight_column)) if column is None]
        if required:
            raise ValueError(f"Portfolio file missing columns: {sorted(required)}")

        portfolio = frame[[asset_column, weight_column] + ([sector_column] if sector_column else [])].copy()
        portfolio.rename(columns={asset_column: "asset", weight_column: "weight"}, inplace=True)
        if sector_column:
            portfolio.rename(columns={sector_column: "sector"}, inplace=True)

        portfolio["asset"] = portfolio["asset"].astype(str).str.strip()
        if portfolio["asset"].duplicated().any():
            duplicates = portfolio.loc[portfolio["asset"].duplicated(), "asset"].tolist()
            raise ValueError(f"Portfolio contains duplicate assets: {sorted(set(duplicates))}")

        portfolio["weight"] = cls._clean_weight_series(portfolio["weight"])
        if portfolio["weight"].isna().any():
            raise ValueError("Portfolio weights contain missing or invalid values")
        if not np.isfinite(portfolio["weight"].to_numpy()).all():
            raise ValueError("Portfolio weights must be finite numbers")

        weights = portfolio.set_index("asset")["weight"]
        total_weight = float(weights.sum())
        gross_exposure = float(weights.abs().sum())
        if normalize:
            if np.isclose(gross_exposure, 0.0):
                raise ValueError("Portfolio weights cannot all be zero")
            scale = total_weight if np.all(weights >= 0) else gross_exposure
            if np.isclose(scale, 0.0):
                raise ValueError("Portfolio weights cannot all be zero")
            weights = weights / scale
        elif not np.isclose(total_weight, 1.0, atol=1e-6):
            raise ValueError("Portfolio weights must sum to 1.0 when normalization is disabled")

        sectors = None
        if "sector" in portfolio.columns:
            sectors = portfolio.set_index("asset")["sector"].astype(str)
        return cls(weights=weights, sectors=sectors)

    @classmethod
    def from_csv(cls, path: str | Path, normalize: bool = True) -> "Portfolio":
        return cls.from_frame(pd.read_csv(path), normalize=normalize)

    @classmethod
    def from_interactive_brokers_csv(cls, path: str | Path, normalize: bool = True) -> "Portfolio":
        frame = pd.read_csv(path)
        return cls.from_interactive_brokers_frame(frame, normalize=normalize)

    @classmethod
    def from_interactive_brokers_frame(cls, frame: pd.DataFrame, normalize: bool = True) -> "Portfolio":
        if not isinstance(frame, pd.DataFrame):
            raise TypeError("Interactive Brokers input must be a pandas DataFrame")

        asset_column = cls._resolve_column(frame, ("symbol", "local symbol", "localsymbol", "asset", "ticker"))
        if asset_column is None:
            raise ValueError("Interactive Brokers file missing a symbol column")

        weight_column = cls._resolve_column(frame, ("weight %", "weight", "market value", "market_value", "marketvalue", "portfolio weight"))
        if weight_column is None:
            raise ValueError("Interactive Brokers file missing a weight or market value column")

        sector_column = cls._resolve_column(frame, ("sector", "asset class", "asset_class", "industry"))
        selected = frame[[asset_column, weight_column] + ([sector_column] if sector_column else [])].copy()
        selected.rename(columns={asset_column: "asset", weight_column: "weight"}, inplace=True)
        if sector_column:
            selected.rename(columns={sector_column: "sector"}, inplace=True)

        # IB exports can include percentage strings, market values or plain weights.
        if selected["weight"].astype(str).str.contains("%", regex=False).any():
            selected["weight"] = cls._clean_weight_series(selected["weight"]) / 100.0
        else:
            selected["weight"] = cls._clean_weight_series(selected["weight"])

        if "sector" in selected.columns:
            aggregated = selected.groupby("asset", as_index=False).agg(
                weight=("weight", "sum"),
                sector=("sector", lambda values: values.dropna().astype(str).iloc[0] if not values.dropna().empty else "Unknown"),
            )
        else:
            aggregated = selected.groupby("asset", as_index=False).agg(weight=("weight", "sum"))

        return cls.from_frame(aggregated, normalize=normalize)

    @classmethod
    def from_frame(cls, frame: pd.DataFrame, normalize: bool = True) -> "Portfolio":
        return cls._from_generic_frame(frame, normalize=normalize)

    @classmethod
    def from_path(cls, path: str | Path, normalize: bool = True, source: str = "auto") -> "Portfolio":
        source_key = source.lower().strip()
        if source_key not in {"auto", "csv", "ib"}:
            raise ValueError("Portfolio source must be one of: auto, csv, ib")

        if source_key == "csv":
            return cls.from_csv(path, normalize=normalize)
        if source_key == "ib":
            return cls.from_interactive_brokers_csv(path, normalize=normalize)

        frame = pd.read_csv(path)
        ib_hints = {cls._normalize_column_name(column) for column in frame.columns}
        if ib_hints.intersection({"symbol", "weight %", "market value", "asset class", "local symbol"}):
            return cls.from_interactive_brokers_frame(frame, normalize=normalize)
        return cls.from_frame(frame, normalize=normalize)

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
