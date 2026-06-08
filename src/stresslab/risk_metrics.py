from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import stats
from .var_es import historical_var, historical_es, parametric_var, parametric_es, cornish_fisher_var

TRADING_DAYS = 252


def annualized_volatility(returns: pd.Series) -> float:
    return float(returns.std(ddof=1) * np.sqrt(TRADING_DAYS))


def cumulative_returns(returns: pd.Series) -> pd.Series:
    return (1.0 + returns.fillna(0.0)).cumprod() - 1.0


def max_drawdown(returns: pd.Series) -> float:
    equity = (1.0 + returns.fillna(0.0)).cumprod()
    peak = equity.cummax()
    dd = equity / peak - 1.0
    return float(dd.min())


def diversification_ratio(weights: pd.Series, covariance: pd.DataFrame) -> float:
    aligned_cov = covariance.loc[weights.index, weights.index]
    asset_vol = np.sqrt(np.diag(aligned_cov))
    weighted_vol = float(np.sum(np.abs(weights.to_numpy()) * asset_vol))
    port_vol = float(np.sqrt(weights.to_numpy() @ aligned_cov.to_numpy() @ weights.to_numpy()))
    return weighted_vol / port_vol if port_vol > 0 else float("nan")


def base_risk_summary(portfolio_returns: pd.Series, confidence: float = 0.99) -> dict[str, float]:
    r = portfolio_returns.dropna()
    return {
        "mean_daily_return": float(r.mean()),
        "annualized_volatility": annualized_volatility(r),
        "historical_var": historical_var(r, confidence),
        "historical_es": historical_es(r, confidence),
        "parametric_var": parametric_var(r, confidence),
        "parametric_es": parametric_es(r, confidence),
        "cornish_fisher_var": cornish_fisher_var(r, confidence),
        "max_drawdown": max_drawdown(r),
        "skewness": float(stats.skew(r)) if len(r) > 2 else float("nan"),
        "excess_kurtosis": float(stats.kurtosis(r, fisher=True)) if len(r) > 3 else float("nan"),
    }
