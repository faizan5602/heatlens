from typing import Dict, List, Tuple

import numpy as np
import pandas as pd
from scipy import stats

from backend.models.responses import CorrelationPair


def compute_pearson_correlations(df: pd.DataFrame) -> Tuple[List[CorrelationPair], Dict[str, Dict[str, float]]]:
    numeric_df = df.select_dtypes(include=[np.number]).dropna(how='all')
    valid_cols = [c for c in numeric_df.columns if numeric_df[c].nunique() > 1]

    pairs: List[CorrelationPair] = []
    matrix: Dict[str, Dict[str, float]] = {c: {} for c in valid_cols}

    for i, col1 in enumerate(valid_cols):
        for j, col2 in enumerate(valid_cols):
            if i == j:
                matrix[col1][col2] = 1.0
                continue

            sub = numeric_df[[col1, col2]].dropna()
            if len(sub) < 5:
                matrix[col1][col2] = 0.0
                continue

            r, _ = stats.pearsonr(sub[col1], sub[col2])
            r_val = float(round(r, 2))
            matrix[col1][col2] = r_val

            if i < j:
                abs_r = abs(r_val)
                strength = 'very strong' if abs_r >= 0.8 else 'strong' if abs_r >= 0.6 else 'moderate' if abs_r >= 0.4 else 'weak'
                direction = 'positive' if r_val >= 0 else 'negative'

                pairs.append(CorrelationPair(
                    variable_x=col1,
                    variable_y=col2,
                    coefficient=r_val,
                    sample_size=len(sub),
                    direction=direction,
                    strength=strength,
                ))

    return pairs, matrix
