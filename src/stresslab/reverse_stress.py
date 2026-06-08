from __future__ import annotations

import pandas as pd


def shock_to_breach_loss(weights: pd.Series, target_loss: float, shock_assets: list[str] | None = None) -> float:
    """Uniform shock required on selected assets to reach target portfolio loss."""
    if shock_assets is None:
        exposure = float(weights.sum())
    else:
        exposure = float(weights.loc[shock_assets].sum())
    if abs(exposure) < 1e-12:
        return float("nan")
    return float(target_loss / exposure)


def correlation_to_breach_loss(base_loss: float, stressed_loss: float, target_loss: float, base_uplift: float = 0.0, max_uplift: float = 1.0) -> float:
    """Linear interpolation proxy for required correlation uplift."""
    if abs(stressed_loss - base_loss) < 1e-12:
        return float("nan")
    ratio = (target_loss - base_loss) / (stressed_loss - base_loss)
    return float(base_uplift + ratio * (max_uplift - base_uplift))
