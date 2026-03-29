"""ML helpers — IsolationForest + z-score anomaly detection."""
import numpy as np
from sklearn.ensemble import IsolationForest
from scipy import stats


def run_isolation_forest(values: list, contamination: float = 0.1) -> list:
    if len(values) < 4:
        return [False] * len(values)
    arr = np.array(values).reshape(-1, 1)
    preds = IsolationForest(contamination=contamination, random_state=42).fit_predict(arr)
    return [p == -1 for p in preds]


def zscore_anomalies(values: list, threshold: float = 2.5) -> list:
    if len(values) < 3:
        return [False] * len(values)
    return [float(z) > threshold for z in np.abs(stats.zscore(values))]


def flag_cost_spikes(monthly_costs: list, current: float, threshold_pct: float = 20.0) -> bool:
    if not monthly_costs:
        return False
    return current > np.mean(monthly_costs) * (1 + threshold_pct / 100)
