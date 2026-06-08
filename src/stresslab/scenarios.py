from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import yaml
import pandas as pd
import numpy as np


@dataclass(frozen=True)
class Scenario:
    name: str
    description: str = ""
    equity_shock: float = 0.0
    sector_shocks: dict[str, float] = field(default_factory=dict)
    asset_shocks: dict[str, float] = field(default_factory=dict)
    vol_multiplier: float = 1.0
    correlation_uplift: float = 0.0
    liquidity_haircut: float = 0.0
    rates_shock_bps: float = 0.0

    @classmethod
    def from_dict(cls, data: dict) -> "Scenario":
        return cls(
            name=str(data.get("name", "unnamed_scenario")),
            description=str(data.get("description", "")),
            equity_shock=float(data.get("equity_shock", 0.0)),
            sector_shocks=dict(data.get("sector_shocks", {}) or {}),
            asset_shocks=dict(data.get("asset_shocks", {}) or {}),
            vol_multiplier=float(data.get("vol_multiplier", 1.0)),
            correlation_uplift=float(data.get("correlation_uplift", 0.0)),
            liquidity_haircut=float(data.get("liquidity_haircut", 0.0)),
            rates_shock_bps=float(data.get("rates_shock_bps", 0.0)),
        )


def load_scenarios(path: str | Path) -> list[Scenario]:
    p = Path(path)
    files = sorted(p.glob("*.yaml")) if p.is_dir() else [p]
    scenarios = []
    for file in files:
        with file.open("r", encoding="utf-8") as fh:
            payload = yaml.safe_load(fh) or {}
        scenarios.append(Scenario.from_dict(payload))
    return scenarios


def scenario_asset_shock_vector(scenario: Scenario, assets: list[str], sectors: pd.Series | None = None) -> pd.Series:
    shock = pd.Series(scenario.equity_shock, index=assets, dtype=float)
    if sectors is not None and len(sectors):
        for sector, value in scenario.sector_shocks.items():
            names = sectors[sectors == sector].index.intersection(assets)
            shock.loc[names] += float(value)
    for asset, value in scenario.asset_shocks.items():
        if asset in shock.index:
            shock.loc[asset] += float(value)
    return shock


def apply_scenario_to_returns(returns: pd.DataFrame, scenario: Scenario, sectors: pd.Series | None = None) -> pd.DataFrame:
    stressed = returns.copy().astype(float)
    shock = scenario_asset_shock_vector(scenario, list(stressed.columns), sectors)
    if scenario.vol_multiplier != 1.0:
        demeaned = stressed - stressed.mean()
        stressed = stressed.mean() + demeaned * scenario.vol_multiplier
    # Add one synthetic stressed day at the end for mark-to-market scenario loss.
    stressed_day = pd.DataFrame([shock], index=[stressed.index.max() + pd.Timedelta(days=1)])
    return pd.concat([stressed, stressed_day], axis=0)
