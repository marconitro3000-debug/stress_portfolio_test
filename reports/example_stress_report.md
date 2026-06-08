# Portfolio Stress Test Report

## Executive Summary

- Base annualized volatility: 24.07%
- Historical VaR 99%: -3.62%
- Historical Expected Shortfall 99%: -4.11%
- Max historical drawdown: -66.10%

## Scenario Results

| scenario              |   direct_loss |   vol_corr_loss_proxy |   liquidity_haircut |   total_loss |   vol_multiplier |   correlation_uplift |
|:----------------------|--------------:|----------------------:|--------------------:|-------------:|-----------------:|---------------------:|
| equity_crash          |       -0.2200 |               -0.0719 |              0.0050 |      -0.2250 |           1.8000 |               0.2500 |
| sector_tech_shock     |       -0.1675 |               -0.0611 |              0.0100 |      -0.1775 |           1.6000 |               0.1500 |
| stagflation_shock     |       -0.1500 |               -0.0775 |              0.0150 |      -0.1650 |           1.9000 |               0.3000 |
| liquidity_crisis      |       -0.1200 |               -0.0833 |              0.0350 |      -0.1550 |           2.0000 |               0.3500 |
| correlation_breakdown |       -0.0800 |               -0.0661 |              0.0100 |      -0.0900 |           1.5000 |               0.5000 |

## Main Risk Contributions

| asset   |   risk_contribution |
|:--------|--------------------:|
| NVDA    |              0.0042 |
| AAPL    |              0.0037 |
| MSFT    |              0.0032 |
| JPM     |              0.0026 |
| XOM     |              0.0015 |
| GLD     |              0.0002 |
| TLT     |             -0.0002 |

## Sector Exposure

| sector     |   weight |
|:-----------|---------:|
| Technology |   0.5500 |
| Financials |   0.1500 |
| Bonds      |   0.1000 |
| Energy     |   0.1000 |
| Gold       |   0.1000 |

## Correlation Diagnostics

- average_correlation: 0.2073
- downside_average_correlation: -0.0011
- uplift: -0.2083
- uplift_ratio: -0.0053
- diversification_ratio: 1.4543
- current_rolling_vol: 0.0154
- vol_percentile: 0.6182
- regime: normal

## Reverse Stress Tests

- uniform_equity_shock_for_10pct_loss: -0.1000
- correlation_uplift_proxy_for_10pct_loss: 0.4444

## Network Diagnostics

- weighted_cluster_concentration: 0.1833
- avg_high_corr_edges: 0.8571
- systemic_concentration_score: 0.2121

## Warnings

- Historical Expected Shortfall is materially negative at the selected confidence level.
- At least one stress scenario breaches a 10% estimated loss threshold.

## Methodology Notes

This report uses historical returns, scenario shocks, turnover/liquidity haircuts, downside correlation diagnostics, reverse stress proxies and component risk attribution. Outputs are research estimates and not investment advice.