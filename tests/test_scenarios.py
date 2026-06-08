import pandas as pd
from stresslab.scenarios import Scenario, scenario_asset_shock_vector


def test_scenario_sector_shocks():
    s = Scenario(name="tech", equity_shock=-0.05, sector_shocks={"Tech": -0.2})
    sectors = pd.Series({"A": "Tech", "B": "Energy"})
    shock = scenario_asset_shock_vector(s, ["A", "B"], sectors)
    assert shock["A"] == -0.25
    assert shock["B"] == -0.05
