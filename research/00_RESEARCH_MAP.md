# Research Map

Portfolio Stress Lab is structured around institutional stress testing practice:

1. Base risk: volatility, VaR, Expected Shortfall and drawdown.
2. Scenario design: historical, parametric and reverse stress tests.
3. Correlation breakdown: diversification failure in selloffs.
4. Tail dependence: ES, EVT/POT proxy and Student-t stress.
5. Liquidity stress: liquidation haircuts and cost-adjusted losses.
6. Network fragility: correlation network centrality and cluster concentration.
7. Regime conditioning: current volatility state and similar historical periods.
8. Reporting: audit-style Markdown report with assumptions, warnings and limitations.

The project is deliberately implemented as an applied repo rather than a pure library: the default workflow is `run_stress_test.py -> stress report`.
