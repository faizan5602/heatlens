from backend.models.responses import HeatExposureScore, ExposureBreakdown


def calculate_heat_exposure_score(
    mean_temp: float,
    max_temp: float,
    persistence_hours: float,
    anomaly_count: int,
    mean_humidity: float,
) -> HeatExposureScore:
    """
    Deterministically computes 0-100 score based on 4 standardized weighted metrics:
    1. Intensity (40%): Driven by max & mean temp.
    2. Persistence (30%): Continuous hours > threshold.
    3. Anomaly Severity (15%): Statistical outlier frequency.
    4. Environmental Compound (15%): Humidity interaction factor.
    """
    intensity_raw = ((mean_temp - 20.0) / 25.0) * 50.0 + ((max_temp - 25.0) / 20.0) * 50.0
    intensity_comp = max(0.0, min(100.0, intensity_raw))

    persistence_comp = max(0.0, min(100.0, (persistence_hours / 24.0) * 100.0))

    anomaly_comp = max(0.0, min(100.0, anomaly_count * 20.0))

    env_comp = max(0.0, min(100.0, (mean_humidity / 80.0) * 100.0 if mean_humidity else 50.0))

    final_score = int(round(
        (intensity_comp * 0.40) +
        (persistence_comp * 0.30) +
        (anomaly_comp * 0.15) +
        (env_comp * 0.15)
    ))

    final_score = max(0, min(100, final_score))

    classification = (
        'EXTREME EXPOSURE' if final_score >= 80 else
        'HIGH EXPOSURE' if final_score >= 60 else
        'MODERATE EXPOSURE' if final_score >= 45 else
        'LOW EXPOSURE'
    )

    return HeatExposureScore(
        overall_score=final_score,
        classification=classification,
        breakdown=ExposureBreakdown(
            intensity_component=float(round(intensity_comp, 1)),
            persistence_component=float(round(persistence_comp, 1)),
            anomaly_component=float(round(anomaly_comp, 1)),
            environmental_component=float(round(env_comp, 1)),
        ),
    )
