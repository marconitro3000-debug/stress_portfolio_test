import pandas as pd
import pytest

from stresslab.portfolio import Portfolio


def test_portfolio_normalizes_weights():
    frame = pd.DataFrame({
        "asset": ["A", "B"],
        "weight": [2.0, 1.0],
    })

    portfolio = Portfolio.from_frame(frame)

    assert portfolio.weights.sum() == pytest.approx(1.0)
    assert portfolio.weights["A"] == pytest.approx(2.0 / 3.0)


def test_portfolio_rejects_duplicate_assets():
    frame = pd.DataFrame({
        "asset": ["A", "A"],
        "weight": [0.5, 0.5],
    })

    with pytest.raises(ValueError, match="duplicate assets"):
        Portfolio.from_frame(frame, normalize=False)