export interface DescriptiveStats {
  count: number;
  mean: number;
  std: number;
  min: number;
  p25: number;
  median: number;
  p75: number;
  max: number;
  variance: number;
}

export interface CorrelationPair {
  variable_x: string;
  variable_y: string;
  coefficient: number;
  sample_size: number;
  direction: string;
  strength: string;
}

export interface AnomalyPoint {
  timestamp: string;
  variable: string;
  observed_value: number;
  baseline_mean: number;
  z_score: number;
  deviation: number;
}

export interface HeatPersistence {
  threshold_celsius: number;
  duration_hours_above_threshold: number;
  longest_continuous_hot_spell_hours: number;
  pct_observations_above_threshold: number;
  status: string;
}

export interface ExposureBreakdown {
  intensity_component: number;
  persistence_component: number;
  anomaly_component: number;
  environmental_component: number;
}

export interface HeatExposureScore {
  overall_score: number;
  classification: string;
  breakdown: ExposureBreakdown;
}

export interface AnalysisResponse {
  location_name: string;
  data_source: string;
  sample_size: number;
  time_bounds: { start?: string; end?: string };
  descriptive_statistics: Record<string, DescriptiveStats>;
  heat_intensity: string;
  persistence: HeatPersistence;
  anomalies: AnomalyPoint[];
  correlations: CorrelationPair[];
  correlation_matrix: Record<string, Record<string, number>>;
  heat_exposure_score: HeatExposureScore;
  gemini_interpretation: string;
  timeseries_data: Array<Record<string, any>>;
}
