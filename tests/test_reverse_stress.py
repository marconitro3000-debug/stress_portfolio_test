import pandas as pd
from stresslab.reverse_stress import shock_to_breach_loss


def test_shock_to_breach_loss():
    weights = pd.Series({"A": 0.5, "B": 0.5})
    shock = shock_to_breach_loss(weights, -0.1)
    assert abs(shock + 0.1) < 1e-12
