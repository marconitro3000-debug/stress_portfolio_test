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


def test_ib_portfolio_loader_uses_weight_percent_and_sector():
    frame = pd.DataFrame({
        "Symbol": ["AAPL", "AAPL", "MSFT"],
        "Weight %": [10, 5, 85],
        "Asset Class": ["Technology", "Technology", "Technology"],
    })

    portfolio = Portfolio.from_interactive_brokers_frame(frame)

    assert portfolio.weights.sum() == pytest.approx(1.0)
    assert portfolio.weights["AAPL"] == pytest.approx(0.15)
    assert portfolio.sectors is not None
    assert portfolio.sectors["AAPL"] == "Technology"


def test_portfolio_auto_detects_ib_style_frame():
    frame = pd.DataFrame({
        "Symbol": ["AAPL", "MSFT"],
        "Market Value": [20000, 80000],
        "Asset Class": ["Technology", "Technology"],
    })

    portfolio = Portfolio.from_interactive_brokers_frame(frame)

    assert portfolio.weights.sum() == pytest.approx(1.0)


def test_portfolio_auto_detects_ib_style_csv(tmp_path):
    frame = pd.DataFrame({
        "Symbol": ["AAPL", "MSFT"],
        "Market Value": [20000, 80000],
        "Asset Class": ["Technology", "Technology"],
    })
    file_path = tmp_path / "ib_export.csv"
    frame.to_csv(file_path, index=False)

    portfolio = Portfolio.from_path(file_path, source="auto")

    assert portfolio.weights.sum() == pytest.approx(1.0)