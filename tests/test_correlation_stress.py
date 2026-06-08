import numpy as np
import pandas as pd
from stresslab.correlation_stress import stress_correlation, correlation_uplift


def test_stress_correlation_psd_like_diagonal():
    corr = pd.DataFrame([[1.0, 0.2], [0.2, 1.0]], columns=["A", "B"], index=["A", "B"])
    stressed = stress_correlation(corr, 0.5)
    assert np.allclose(np.diag(stressed), 1.0)
    assert stressed.loc["A", "B"] > corr.loc["A", "B"]


def test_correlation_uplift_returns_keys():
    rng = np.random.default_rng(0)
    r = pd.DataFrame(rng.normal(0, 0.01, (200, 4)))
    out = correlation_uplift(r)
    assert "uplift" in out
