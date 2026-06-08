# Data templates

Use these CSV contracts when running the project.

## `sample_portfolio.csv`

- `asset`: ticker or asset identifier.
- `weight`: portfolio weight.
- `sector`: optional sector label for attribution.

Rules:

- No duplicate assets.
- No missing weights.
- Weights are normalized automatically by default.
- Disable normalization only if weights already sum to $1.0$.

## `sample_returns.csv`

- First column should contain dates.
- Remaining columns should match the asset tickers in the portfolio.
- Values must be returns, not prices.

## Tip

If you only have prices, convert them to returns before running the stress test.