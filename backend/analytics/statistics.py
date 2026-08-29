import numpy as np
import pandas as pd
from typing import Dict

from backend.models.responses import DescriptiveStats


def compute_descriptive_stats(df: pd.DataFrame) -> Dict[str, DescriptiveStats]:
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    stats_map = {}

    for col in numeric_cols:
        series = df[col].dropna()
        if len(series) == 0:
            continue

        stats_map[col] = DescriptiveStats(
            count=int(len(series)),
            mean=float(round(series.mean(), 2)),
            std=float(round(series.std(), 2)) if len(series) > 1 else 0.0,
            min=float(round(series.min(), 2)),
            p25=float(round(series.quantile(0.25), 2)),
            median=float(round(series.median(), 2)),
            p75=float(round(series.quantile(0.75), 2)),
            max=float(round(series.max(), 2)),
            variance=float(round(series.var(), 2)) if len(series) > 1 else 0.0,
        )

    return stats_map


def determine_heat_intensity(max_temp: float, mean_temp: float) -> str:
    if max_temp >= 40.0 or mean_temp >= 36.0:
        return 'EXTREME'
    if max_temp >= 36.0 or mean_temp >= 32.0:
        return 'HIGH'
    if max_temp >= 31.0 or mean_temp >= 27.0:
        return 'MODERATE'
    return 'LOW'
