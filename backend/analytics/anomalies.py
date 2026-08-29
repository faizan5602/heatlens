from typing import List

import numpy as np
import pandas as pd
from scipy import stats

from backend.models.responses import AnomalyPoint


def detect_zscore_anomalies(df: pd.DataFrame, threshold: float = 2.0) -> List[AnomalyPoint]:
    anomalies: List[AnomalyPoint] = []
    if 'temperature' not in df.columns or len(df) < 10:
        return anomalies

    series = df['temperature'].dropna()
    mean_val = float(series.mean())
    z_scores = stats.zscore(series)

    for idx, (original_idx, value) in enumerate(series.items()):
        z = float(z_scores[idx])
        if abs(z) >= threshold:
            timestamp = str(df.loc[original_idx, 'timestamp']) if 'timestamp' in df.columns else f'Point {original_idx}'
            anomalies.append(AnomalyPoint(
                timestamp=timestamp,
                variable='temperature',
                observed_value=float(round(value, 2)),
                baseline_mean=float(round(mean_val, 2)),
                z_score=float(round(z, 2)),
                deviation=float(round(value - mean_val, 2)),
            ))

    return anomalies
