# Portfolio Stress Lab: Technical Note

Open the paper-style notebook version at [notebooks/00_paper_walkthrough.ipynb](../notebooks/00_paper_walkthrough.ipynb) for a step-by-step walkthrough with the same structure.

## Abstract

This project implements a reproducible portfolio stress testing workflow that accepts a user portfolio, aligns it with historical returns, runs scenario shocks, estimates tail risk and produces an audit-style report. The design goal is practical usability: a user can swap in their own CSV files, or an Interactive Brokers export, and obtain a consistent stress analysis without changing the code.

## 1. Problem Statement

The core problem is to measure how a portfolio behaves under adverse market conditions. A single point estimate of volatility is not enough for this task. A usable workflow needs to combine:

- baseline risk measurement,
- scenario-based shocks,
- tail-risk estimation,
- correlation stress,
- liquidity adjustments,
- reverse stress thresholds,
- and portfolio attribution.

The repo is organized to make those steps explicit and reproducible.

## 2. Data Inputs

The workflow accepts two main inputs.

### 2.1 Portfolio file

The portfolio can be loaded from a generic CSV or from an Interactive Brokers export.

Required information:

- asset identifier or symbol,
- weight or market value,
- optional sector or asset-class label.

The loader normalizes weights by default and validates duplicate assets, missing values and malformed weights.

### 2.2 Historical returns

The returns file must contain:

- a date index,
- one column per asset,
- daily returns rather than prices.

If the user only has prices, they should convert them to returns before running the analysis.

## 3. Methodology

The analysis follows a fixed sequence.

### Step 1: Load and normalize the portfolio

The portfolio loader standardizes the input schema and builds a weight vector. For long-only portfolios, weights are normalized to one. For other portfolios, gross exposure handling is explicit.

### Step 2: Align returns to holdings

The return matrix is aligned to the portfolio universe. This ensures the analysis is run only on assets present in both the holdings and the historical data.

### Step 3: Compute base risk

The base case includes:

- annualized volatility,
- historical VaR,
- historical Expected Shortfall,
- parametric VaR / ES,
- Cornish-Fisher VaR,
- and max drawdown.

These metrics establish the starting risk profile before any stress scenario is applied.

### Step 4: Apply stress scenarios

The engine evaluates named stress scenarios such as equity crash, correlation breakdown, volatility spike, liquidity crisis and stagflation shock. Each scenario can alter:

- asset-level shocks,
- sector shocks,
- volatility scaling,
- correlation uplift,
- and liquidity haircut assumptions.

### Step 5: Estimate attribution and concentration

The report decomposes portfolio risk and scenario losses by asset and sector. It also adds concentration and network-style diagnostics so that users can see whether the portfolio depends too heavily on a small set of risk drivers.

### Step 6: Run reverse stress checks

Reverse stress testing estimates the shock needed to breach a target loss threshold. This helps answer questions like:

- what kind of move would produce a 10% loss,
- or how much correlation breakage would destroy diversification.

## 4. Implementation Notes

The codebase separates the workflow into small modules:

- `portfolio.py` handles input loading and validation,
- `risk_metrics.py` and `var_es.py` compute base risk,
- `scenarios.py` defines and loads stress cases,
- `correlation_stress.py` models correlation deterioration,
- `tail_risk.py` estimates tail metrics,
- `liquidity_stress.py` adjusts losses for market impact,
- `reverse_stress.py` provides breach-threshold proxies,
- `network_contagion.py` adds concentration diagnostics,
- `attribution.py` produces component and sector contributions,
- `engine.py` orchestrates the full workflow,
- `reporting.py` generates the final Markdown output.

This structure keeps the workflow readable and makes the report easy to extend.

## 5. Reproducible Workflow

The default user flow is:

```bash
python scripts/run_stress_test.py \
  --returns data/sample_returns.csv \
  --portfolio data/sample_portfolio.csv \
  --scenarios scenarios \
  --output reports/example_stress_report.md
```

For Interactive Brokers exports:

```bash
stresslab-stress \
  --portfolio data/ib_portfolio_template.csv \
  --portfolio-source ib \
  --returns data/sample_returns.csv \
  --output reports/example_stress_report.md
```

## 6. Interpretation of Results

The report is intended to read like a compact research note rather than a raw debug dump. It explains:

- the base risk posture,
- which scenarios drive the worst losses,
- which assets or sectors dominate contributions,
- whether the portfolio is vulnerable to correlation breakdown,
- and which assumptions would trigger a critical loss.

That makes the project easier to present as a research artifact.

## 7. Limitations

The project uses historical data and stylized stress assumptions. As a result:

- scenario losses are approximations,
- the reverse stress checks are proxies rather than optimization-based solutions,
- liquidity and network diagnostics are simplified,
- and the outputs should be interpreted as research estimates.

## 8. Conclusion

The repo demonstrates a full stress-testing workflow that is simple enough to run from CSV files but structured enough to support research-style presentation. It is suitable for personal exploration, interview discussion and iterative extension.
