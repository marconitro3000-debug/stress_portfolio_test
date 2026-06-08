from __future__ import annotations

from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt


def plot_scenario_losses(scenario_results: pd.DataFrame, output: str | Path) -> None:
    ax = scenario_results["total_loss"].sort_values().plot(kind="bar", title="Scenario Losses")
    ax.set_ylabel("Estimated loss")
    plt.tight_layout()
    Path(output).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output)
    plt.close()
