from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd
import yaml

from .engine import StressTestEngine
from .plotting import plot_scenario_losses


def _load_config(path: str | Path | None) -> dict:
    if not path:
        return {}
    config_path = Path(path)
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")
    with config_path.open("r", encoding="utf-8") as fh:
        payload = yaml.safe_load(fh) or {}
    if not isinstance(payload, dict):
        raise ValueError("Config file must contain a mapping")
    return payload


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run a professional portfolio stress test.")
    parser.add_argument("--config", default=None, help="Optional YAML config with run settings.")
    parser.add_argument("--returns", default=None, help="CSV with dates as index and assets as columns.")
    parser.add_argument("--portfolio", default=None, help="CSV with asset, weight and optional sector columns.")
    parser.add_argument("--scenarios", default=None, help="Folder or YAML file with stress scenarios.")
    parser.add_argument("--output", default=None, help="Markdown report output path.")
    parser.add_argument("--figure-output", default=None, help="Optional PNG bar chart for scenario losses.")
    parser.add_argument("--confidence", type=float, default=None, help="VaR/ES confidence level.")
    parser.add_argument("--normalize-weights", dest="normalize_weights", action="store_true", default=None, help="Normalize portfolio weights automatically.")
    parser.add_argument("--no-normalize-weights", dest="normalize_weights", action="store_false", help="Require portfolio weights to already sum to 1.0.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    config = _load_config(args.config)
    returns_path = args.returns or config.get("returns_path")
    portfolio_path = args.portfolio or config.get("portfolio_path")
    scenarios_path = args.scenarios or config.get("scenarios_path")
    output_path = args.output or config.get("output_markdown") or "reports/stress_report.md"
    figure_output = args.figure_output or config.get("figure_output")
    confidence = args.confidence if args.confidence is not None else float(config.get("confidence_level", 0.99))
    normalize_weights = args.normalize_weights if args.normalize_weights is not None else bool(config.get("normalize_weights", True))

    if not returns_path or not portfolio_path:
        parser.error("Both --returns and --portfolio are required, either directly or via --config.")

    returns = pd.read_csv(returns_path, index_col=0, parse_dates=True)
    portfolio = pd.read_csv(portfolio_path)

    engine = StressTestEngine(returns=returns, portfolio=portfolio, confidence_level=confidence, normalize_weights=normalize_weights)
    report = engine.run_all(scenarios=scenarios_path)
    report.to_markdown(output_path)

    if figure_output:
        plot_scenario_losses(report.scenario_results, figure_output)

    print(report.summary())
    print(f"Report written to {output_path}")
    if figure_output:
        print(f"Scenario chart written to {figure_output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())