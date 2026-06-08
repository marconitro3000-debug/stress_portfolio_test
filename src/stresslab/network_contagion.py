from __future__ import annotations

import numpy as np
import pandas as pd


def correlation_network_centrality(returns: pd.DataFrame, threshold: float = 0.4) -> pd.Series:
    corr = returns.corr().abs().fillna(0.0)
    np.fill_diagonal(corr.values, 0.0)
    adjacency = corr.where(corr >= threshold, 0.0)
    centrality = adjacency.sum(axis=1) / max(len(adjacency) - 1, 1)
    return centrality.sort_values(ascending=False)


def systemic_concentration_score(weights: pd.Series, centrality: pd.Series) -> float:
    aligned = centrality.reindex(weights.index).fillna(0.0)
    return float((weights.abs() * aligned).sum())


def cluster_concentration_proxy(returns: pd.DataFrame, weights: pd.Series, threshold: float = 0.6) -> dict[str, float]:
    corr = returns.loc[:, weights.index].corr().abs().fillna(0.0)
    np.fill_diagonal(corr.values, 0.0)
    high_edges = (corr >= threshold).sum(axis=1)
    weighted_cluster = float((weights.abs() * high_edges).sum() / max(len(weights) - 1, 1))
    return {"weighted_cluster_concentration": weighted_cluster, "avg_high_corr_edges": float(high_edges.mean())}
