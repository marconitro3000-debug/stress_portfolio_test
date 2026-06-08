import numpy as np
import pandas as pd
from stresslab.risk_metrics import base_risk_summary, max_drawdown


def test_base_risk_summary_keys():
    r = pd.Series(np.random.default_rng(1).normal(0, 0.01, 300))
    metrics = base_risk_summary(r)
    assert "historical_var" in metrics
    assert "historical_es" in metrics
    assert metrics["annualized_volatility"] > 0


def test_max_drawdown_negative_or_zero():
    r = pd.Series([0.01, -0.05, 0.02, -0.01])
    assert max_drawdown(r) <= 0
