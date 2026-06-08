# Portfolio Stress Lab

[![Python](https://img.shields.io/badge/Python-3.11%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![GitHub repo](https://img.shields.io/badge/GitHub-stress__portfolio__test-black)](https://github.com/marconitro3000-debug/stress_portfolio_test)

Institutional-style portfolio stress testing project for evaluating downside risk under adverse market scenarios.

## Overview

This repo is designed as an applied project, not a generic package. You load a portfolio and return history, run stress scenarios, and generate an audit-style report.

## What it does

- Base portfolio risk: volatility, VaR, Expected Shortfall, max drawdown, skew and kurtosis.
- Scenario stress testing: equity crash, volatility spike, correlation breakdown, liquidity crisis and sector shocks.
- Reverse stress testing: find the shock required to breach a target loss.
- Risk attribution: component risk contribution, sector exposure and scenario loss contribution.
- Tail risk: historical and parametric VaR/ES, Student-t style approximation and EVT/POT proxy.
- Correlation stress: downside correlation uplift and diversification failure.
- Network fragility: correlation network centrality and cluster concentration proxy.
- Professional Markdown reporting and a notebook walkthrough.

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
