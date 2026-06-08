# Scenario definitions

Each YAML file in this folder defines one stress scenario.

Supported fields:

- `name`
- `description`
- `equity_shock`
- `sector_shocks`
- `asset_shocks`
- `vol_multiplier`
- `correlation_uplift`
- `liquidity_haircut`
- `rates_shock_bps`

The CLI can load a single YAML file or a folder of scenario files.