import pandas as pd

from backend.models.responses import HeatPersistence


def calculate_heat_persistence(df: pd.DataFrame, threshold_celsius: float = 35.0) -> HeatPersistence:
    if 'temperature' not in df.columns or df.empty:
        return HeatPersistence(
            threshold_celsius=threshold_celsius,
            duration_hours_above_threshold=0.0,
            longest_continuous_hot_spell_hours=0.0,
            pct_observations_above_threshold=0.0,
            status='UNAVAILABLE_INSUFFICIENT_DATA',
        )

    hot_mask = df['temperature'] >= threshold_celsius
    total_hot_obs = hot_mask.sum()
    pct = (total_hot_obs / len(df)) * 100.0

    longest_streak = 0
    current_streak = 0
    for val in hot_mask:
        if val:
            current_streak += 1
            longest_streak = max(longest_streak, current_streak)
        else:
            current_streak = 0

    return HeatPersistence(
        threshold_celsius=threshold_celsius,
        duration_hours_above_threshold=float(total_hot_obs),
        longest_continuous_hot_spell_hours=float(longest_streak),
        pct_observations_above_threshold=float(round(pct, 2)),
        status='CALCULATED',
    )
