# Implementation Design

The code is factored into focused modules:

- `portfolio.py`: loading, normalization and portfolio returns;
- `risk_metrics.py` and `var_es.py`: base risk metrics;
- `scenarios.py`: YAML scenario definition and shock vectors;
- `correlation_stress.py`: downside correlation and stressed matrices;
- `tail_risk.py`: Student-t and EVT/POT proxies;
- `liquidity_stress.py`: liquidity-adjusted losses;
- `reverse_stress.py`: breach-threshold stress proxies;
- `network_contagion.py`: correlation network diagnostics;
- `attribution.py`: component and scenario contribution;
- `engine.py`: orchestration;
- `reporting.py`: Markdown report generation.

This separation allows the project to remain readable and extensible.
