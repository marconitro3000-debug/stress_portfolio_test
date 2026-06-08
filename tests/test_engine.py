import numpy as np
import pandas as pd
from stresslab.engine import StressTestEngine


def test_engine_runs_default_scenarios():
    rng = np.random.default_rng(4)
    returns = pd.DataFrame(rng.normal(0, 0.01, (260, 3)), columns=["A", "B", "C"])
    portfolio = pd.DataFrame({"asset": ["A", "B", "C"], "weight": [0.4, 0.4, 0.2], "sector": ["X", "X", "Y"]})
    report = StressTestEngine(returns, portfolio).run_all()
    assert not report.scenario_results.empty
    assert "total_loss" in report.scenario_results.columns
    assert isinstance(report.markdown(), str)
