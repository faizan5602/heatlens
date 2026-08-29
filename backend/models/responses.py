from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field


class DescriptiveStats(BaseModel):
    count: int
    mean: float
    std: float
    min: float
    p25: float
    median: float
    p75: float
    max: float
    variance: float


class CorrelationPair(BaseModel):
    variable_x: str
    variable_y: str
    coefficient: float
    sample_size: int
    direction: str
    strength: str


class AnomalyPoint(BaseModel):
    timestamp: str
    variable: str
    observed_value: float
    baseline_mean: float
    z_score: float
    deviation: float


class HeatPersistence(BaseModel):
    threshold_celsius: float
    duration_hours_above_threshold: float
    longest_continuous_hot_spell_hours: float
    pct_observations_above_threshold: float
    status: str


class ExposureBreakdown(BaseModel):
    intensity_component: float
    persistence_component: float
    anomaly_component: float
    environmental_component: float


class HeatExposureScore(BaseModel):
    overall_score: int
    classification: str
    breakdown: ExposureBreakdown


class AnalysisResponse(BaseModel):
    location_name: str
    data_source: str
    sample_size: int
    time_bounds: Dict[str, Optional[str]]
    descriptive_statistics: Dict[str, DescriptiveStats]
    heat_intensity: str
    persistence: HeatPersistence
    anomalies: List[AnomalyPoint]
    correlations: List[CorrelationPair]
    correlation_matrix: Dict[str, Dict[str, float]]
    heat_exposure_score: HeatExposureScore
    gemini_interpretation: str
    timeseries_data: List[Dict[str, Any]]


class AiQueryResponse(BaseModel):
    response: str
