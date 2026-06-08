from __future__ import annotations

from pathlib import Path
import pandas as pd
import numpy as np

from .portfolio import Portfolio
from .risk_metrics import base_risk_summary, diversification_ratio
from .scenarios import Scenario, load_scenarios, scenario_asset_shock_vector
from .correlation_stress import correlation_uplift, stress_correlation, covariance_from_vol_corr
from .attribution import component_risk_contribution, scenario_loss_contribution, sector_loss_contribution
from .liquidity_stress import liquidity_adjusted_loss
from .tail_risk import student_t_var_es, evt_pot_proxy
from .reverse_stress import shock_to_breach_loss, correlation_to_breach_loss
from .network_contagion import correlation_network_centrality, systemic_concentration_score, cluster_concentration_proxy
from .regime import volatility_regime
from .reporting import StressReport


class StressTestEngine:
    def __init__(self, returns: pd.DataFrame, portfolio: pd.DataFrame | Portfolio, confidence_level: float = 0.99, normalize_weights: bool = True):
        self.returns = returns.sort_index().astype(float)
        self.portfolio = portfolio if isinstance(portfolio, Portfolio) else Portfolio.from_frame(portfolio, normalize=normalize_weights)
        self.returns = self.portfolio.align_returns(self.returns)
        self.confidence_level = confidence_level
        self.portfolio_returns = self.portfolio.portfolio_returns(self.returns)

    def run_all(self, scenarios: list[Scenario] | str | Path | None = None, target_loss: float = -0.10) -> StressReport:
        if scenarios is None:
            scenarios = self.default_scenarios()
        elif isinstance(scenarios, (str, Path)):
            scenarios = load_scenarios(scenarios)

        base = base_risk_summary(self.portfolio_returns, self.confidence_level)
        base.update(student_t_var_es(self.portfolio_returns, self.confidence_level))
        base.update(evt_pot_proxy(self.portfolio_returns, self.confidence_level))

        scenario_rows = []
        corr = self.returns.corr().fillna(0.0)
        vols = self.returns.std(ddof=1).fillna(0.0)
        base_cov = self.returns.cov().fillna(0.0)
        base_risk_contrib = component_risk_contribution(self.portfolio.weights, base_cov)

        for scenario in scenarios:
            asset_shock = scenario_asset_shock_vector(scenario, list(self.portfolio.weights.index), self.portfolio.sectors)
            direct_loss = float((self.portfolio.weights * asset_shock).sum())

            stressed_corr = stress_correlation(corr, scenario.correlation_uplift) if scenario.correlation_uplift else corr
            stressed_vol = vols * scenario.vol_multiplier
            stressed_cov = covariance_from_vol_corr(stressed_vol, stressed_corr)
            stressed_sigma_daily = float(np.sqrt(self.portfolio.weights.to_numpy() @ stressed_cov.to_numpy() @ self.portfolio.weights.to_numpy()))
            corr_loss_proxy = -2.33 * stressed_sigma_daily
            total_loss = min(direct_loss, corr_loss_proxy) if scenario.correlation_uplift or scenario.vol_multiplier != 1 else direct_loss
            total_loss = liquidity_adjusted_loss(self.portfolio.weights, total_loss, scenario.liquidity_haircut)
            scenario_rows.append({
                "scenario": scenario.name,
                "direct_loss": direct_loss,
                "vol_corr_loss_proxy": corr_loss_proxy,
                "liquidity_haircut": scenario.liquidity_haircut,
                "total_loss": total_loss,
                "vol_multiplier": scenario.vol_multiplier,
                "correlation_uplift": scenario.correlation_uplift,
            })

        scenario_df = pd.DataFrame(scenario_rows).set_index("scenario").sort_values("total_loss")
        corr_diag = correlation_uplift(self.returns)
        corr_diag["diversification_ratio"] = diversification_ratio(self.portfolio.weights, base_cov)
        corr_diag.update(volatility_regime(self.portfolio_returns))

        centrality = correlation_network_centrality(self.returns)
        network_diag = cluster_concentration_proxy(self.returns, self.portfolio.weights)
        network_diag["systemic_concentration_score"] = systemic_concentration_score(self.portfolio.weights, centrality)

        # Reverse stress proxies.
        reverse = {
            "uniform_equity_shock_for_10pct_loss": shock_to_breach_loss(self.portfolio.weights, target_loss),
        }
        if not scenario_df.empty:
            best_stressed = float(scenario_df["total_loss"].min())
            reverse["correlation_uplift_proxy_for_10pct_loss"] = correlation_to_breach_loss(0.0, best_stressed, target_loss)

        warnings = self._warnings(base, scenario_df, corr_diag, network_diag)
        return StressReport(
            base_metrics=base,
            scenario_results=scenario_df,
            risk_contributions=base_risk_contrib,
            sector_exposure=self.portfolio.sector_exposure(),
            correlation_diagnostics=corr_diag,
            reverse_stress=reverse,
            network_diagnostics=network_diag,
            warnings=warnings,
        )

    def default_scenarios(self) -> list[Scenario]:
        return [
            Scenario(name="equity_crash", description="Broad equity market crash", equity_shock=-0.20, vol_multiplier=1.8, correlation_uplift=0.20),
            Scenario(name="correlation_breakdown", description="Diversification failure", equity_shock=-0.08, vol_multiplier=1.5, correlation_uplift=0.45),
            Scenario(name="volatility_spike", description="Volatility shock", equity_shock=-0.05, vol_multiplier=2.5, correlation_uplift=0.20),
            Scenario(name="liquidity_crisis", description="Forced liquidation haircut", equity_shock=-0.10, vol_multiplier=2.0, correlation_uplift=0.30, liquidity_haircut=0.03),
            Scenario(name="stagflation_shock", description="Equities down, rates/credit shock proxy", equity_shock=-0.15, vol_multiplier=1.8, correlation_uplift=0.25, liquidity_haircut=0.01),
        ]

    def _warnings(self, base: dict, scenario_df: pd.DataFrame, corr_diag: dict, network_diag: dict) -> list[str]:
        warnings = []
        if base.get("historical_es", 0) < -0.04:
            warnings.append("Historical Expected Shortfall is materially negative at the selected confidence level.")
        if corr_diag.get("uplift", 0) > 0.15:
            warnings.append("Downside correlation uplift is high; diversification may fail during selloffs.")
        if corr_diag.get("diversification_ratio", 99) < 1.4:
            warnings.append("Diversification ratio is low; portfolio may be concentrated in common risk drivers.")
        if not scenario_df.empty and scenario_df["total_loss"].min() < -0.10:
            warnings.append("At least one stress scenario breaches a 10% estimated loss threshold.")
        if network_diag.get("systemic_concentration_score", 0) > 0.4:
            warnings.append("Portfolio is exposed to high-centrality assets in the correlation network.")
        return warnings


def run_stress_test(returns: pd.DataFrame, portfolio: pd.DataFrame | Portfolio, scenarios: list[Scenario] | str | Path | None = None, confidence_level: float = 0.99, normalize_weights: bool = True) -> StressReport:
    return StressTestEngine(returns=returns, portfolio=portfolio, confidence_level=confidence_level, normalize_weights=normalize_weights).run_all(scenarios=scenarios)
