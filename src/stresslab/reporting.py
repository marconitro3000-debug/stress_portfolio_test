from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import math
import pandas as pd


@dataclass
class StressReport:
    base_metrics: dict[str, float]
    scenario_results: pd.DataFrame
    risk_contributions: pd.Series
    sector_exposure: pd.Series
    correlation_diagnostics: dict[str, float]
    reverse_stress: dict[str, float]
    network_diagnostics: dict[str, float]
    warnings: list[str] = field(default_factory=list)

    def summary(self) -> str:
        worst = self.scenario_results.sort_values("total_loss").head(1)
        worst_name = worst.index[0] if len(worst) else "N/A"
        worst_loss = float(worst["total_loss"].iloc[0]) if len(worst) else float("nan")
        return (
            "Portfolio Stress Test Summary\n"
            f"Base annualized volatility: {self.base_metrics.get('annualized_volatility', float('nan')):.2%}\n"
            f"Base VaR 99%: {self.base_metrics.get('historical_var', float('nan')):.2%}\n"
            f"Base ES 99%: {self.base_metrics.get('historical_es', float('nan')):.2%}\n"
            f"Worst scenario: {worst_name} ({worst_loss:.2%})\n"
        )

    def to_markdown(self, path: str | Path) -> None:
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        Path(path).write_text(self.markdown(), encoding="utf-8")

    @staticmethod
    def _format_value(value: object) -> str:
        if pd.isna(value):
            return ""
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            if math.isfinite(float(value)):
                return f"{float(value):.4f}"
            return str(value)
        return str(value)

    @classmethod
    def _table_to_markdown(cls, data: pd.DataFrame | pd.Series) -> str:
        frame = data.to_frame() if isinstance(data, pd.Series) else data.copy()
        if frame.empty:
            return "No data available."
        frame = frame.reset_index()
        headers = [str(column) for column in frame.columns]
        lines = ["| " + " | ".join(headers) + " |"]
        lines.append("| " + " | ".join(["---"] * len(headers)) + " |")
        for row in frame.itertuples(index=False):
            lines.append("| " + " | ".join(cls._format_value(value) for value in row) + " |")
        return "\n".join(lines)

    def markdown(self) -> str:
        worst = self.scenario_results.sort_values("total_loss").head(1)
        worst_name = worst.index[0] if len(worst) else "N/A"
        worst_loss = float(worst["total_loss"].iloc[0]) if len(worst) else float("nan")
        worst_loss_text = f"{worst_loss:.2%}" if pd.notna(worst_loss) else "n/a"

        lines = [
            "# Portfolio Stress Test Report",
            "",
            "## Executive Summary",
            "",
            f"- Base annualized volatility: {self.base_metrics.get('annualized_volatility', float('nan')):.2%}",
            f"- Historical VaR 99%: {self.base_metrics.get('historical_var', float('nan')):.2%}",
            f"- Historical Expected Shortfall 99%: {self.base_metrics.get('historical_es', float('nan')):.2%}",
            f"- Max historical drawdown: {self.base_metrics.get('max_drawdown', float('nan')):.2%}",
            "",
            "## Narrative Overview",
            "",
            (
                f"This portfolio shows an annualized volatility of {self.base_metrics.get('annualized_volatility', float('nan')):.2%}, "
                f"with historical VaR 99% near {self.base_metrics.get('historical_var', float('nan')):.2%} and Expected Shortfall 99% near {self.base_metrics.get('historical_es', float('nan')):.2%}. "
                f"The worst modeled scenario is {worst_name}, with an estimated loss of {worst_loss_text}."
            ),
            "",
            "The report combines base risk, scenario stress, attribution, correlation fragility and reverse-stress diagnostics to highlight where the portfolio is most vulnerable.",
            "",
            "## Scenario Results",
            "",
            self._table_to_markdown(self.scenario_results),
            "",
            "## Main Risk Contributions",
            "",
            self._table_to_markdown(self.risk_contributions.head(10).to_frame("risk_contribution")),
            "",
            "## Sector Exposure",
            "",
            self._table_to_markdown(self.sector_exposure.to_frame("weight")) if len(self.sector_exposure) else "No sector data provided.",
            "",
            "## Correlation Diagnostics",
            "",
        ]
        for k, v in self.correlation_diagnostics.items():
            lines.append(f"- {k}: {v:.4f}" if isinstance(v, (int, float)) else f"- {k}: {v}")
        lines += ["", "## Reverse Stress Tests", ""]
        for k, v in self.reverse_stress.items():
            lines.append(f"- {k}: {v:.4f}" if isinstance(v, (int, float)) else f"- {k}: {v}")
        lines += ["", "## Network Diagnostics", ""]
        for k, v in self.network_diagnostics.items():
            lines.append(f"- {k}: {v:.4f}" if isinstance(v, (int, float)) else f"- {k}: {v}")
        lines += ["", "## Warnings", ""]
        lines += [f"- {w}" for w in self.warnings] if self.warnings else ["No critical warnings triggered."]
        lines += ["", "## Methodology Notes", "", "This report uses historical returns, scenario shocks, turnover/liquidity haircuts, downside correlation diagnostics, reverse stress proxies and component risk attribution. Outputs are research estimates and not investment advice."]
        return "\n".join(lines)
