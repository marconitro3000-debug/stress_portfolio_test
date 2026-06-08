# Portfolio Stress Lab

Institutional-style portfolio stress testing project for evaluating downside risk under adverse market scenarios.

This repo is designed as an applied project, not a generic package. You load a portfolio and return history, run stress scenarios, and generate an audit-style report.

## What it does

- Base portfolio risk: volatility, VaR, Expected Shortfall, max drawdown, skew, kurtosis.
- Scenario stress testing: equity crash, volatility spike, correlation breakdown, liquidity crisis, sector shocks.
- Reverse stress testing: find the shock required to breach a target loss.
- Risk attribution: component risk contribution and scenario loss contribution.
- Tail risk: historical and parametric VaR/ES, Student-t style approximation, EVT/POT proxy.
- Correlation stress: downside correlation uplift and diversification failure.
- Network fragility: correlation network centrality and cluster concentration proxy.
- Institutional Markdown reporting.

## Quickstart

```bash
pip install -e ".[dev]"
python scripts/run_stress_test.py \
  --returns data/sample_returns.csv \
  --portfolio data/sample_portfolio.csv \
  --scenarios scenarios \
  --output reports/example_stress_report.md
```

Or from Python:

```python
import pandas as pd
from stresslab.engine import StressTestEngine

returns = pd.read_csv("data/sample_returns.csv", index_col=0, parse_dates=True)
portfolio = pd.read_csv("data/sample_portfolio.csv")

engine = StressTestEngine(returns=returns, portfolio=portfolio)
report = engine.run_all()
print(report.summary())
report.to_markdown("reports/stress_report.md")
```

## Project structure

```text
portfolio-stress-lab/
├── scripts/run_stress_test.py
├── configs/
├── data/
├── scenarios/
├── src/stresslab/
│   ├── engine.py
│   ├── portfolio.py
│   ├── risk_metrics.py
│   ├── var_es.py
│   ├── scenarios.py
│   ├── correlation_stress.py
│   ├── liquidity_stress.py
│   ├── tail_risk.py
│   ├── reverse_stress.py
│   ├── attribution.py
# Portfolio Stress Lab

Institutional-style portfolio stress testing project for evaluating downside risk under adverse market scenarios.

## Highlights

- Base portfolio risk: volatility, VaR, Expected Shortfall, max drawdown, skew and kurtosis.
- Scenario stress testing: equity crash, volatility spike, correlation breakdown, liquidity crisis and sector shocks.
- Reverse stress testing: approximate loss threshold and correlation-breakpoint analysis.
- Risk attribution: component risk contribution, sector exposure and scenario loss attribution.
- Tail risk: historical, parametric and Cornish-Fisher VaR/ES plus EVT-style proxy.
- Portfolio diagnostics: concentration, correlation fragility and network centrality.
- Professional outputs: Markdown report, optional chart export and notebook walkthrough.

## Quickstart

```bash
pip install -e ".[dev,notebooks]"
python scripts/run_stress_test.py \
  --returns data/sample_returns.csv \
  --portfolio data/sample_portfolio.csv \
  --scenarios scenarios \
  --output reports/example_stress_report.md \
  --figure-output reports/scenario_losses.png
```

You can also use the installed command:

```bash
stresslab-stress --config configs/portfolio_config.yaml --output reports/example_stress_report.md
```

## Inputs

### Portfolio CSV

Required columns:

- `asset`
- `weight`
- `sector` (optional)

Weights are normalized automatically by default.

### Returns CSV

- First column: dates.
- Remaining columns: asset tickers.
- Values: daily returns, not prices.

## Outputs

- Markdown report with base risk and scenario tables.
- Optional scenario-loss chart in PNG format.
- Notebook-friendly result objects for further analysis.

## Notebook

Open `notebooks/01_end_to_end_stress_lab.ipynb` for the full workflow.

## Project structure

```text
portfolio-stress-lab/
├── configs/
├── data/
├── notebooks/
├── reports/
├── scenarios/
├── scripts/
├── src/stresslab/
└── tests/
```

## CV positioning

Built an institutional-style portfolio stress testing project that evaluates downside risk through scenario analysis, tail-risk modelling, reverse stress testing, network fragility and risk attribution, producing audit-ready portfolio risk reports.
