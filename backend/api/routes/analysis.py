import logging
import time
import traceback
from collections import defaultdict, deque
import pandas as pd
from fastapi import APIRouter, HTTPException, Request

from backend.analytics.anomalies import detect_zscore_anomalies
from backend.analytics.correlation import compute_pearson_correlations
from backend.analytics.persistence import calculate_heat_persistence
from backend.analytics.scoring import calculate_heat_exposure_score
from backend.analytics.statistics import compute_descriptive_stats, determine_heat_intensity
from backend.models.requests import AnalysisRequest
from backend.models.responses import AnalysisResponse
from backend.services.fortyguard import LOCATION_OUTSIDE_COVERAGE, fortyguard_service, is_supported_us_location
from backend.services.gemini import gemini_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix='/api', tags=['Analysis'])
_analysis_requests: defaultdict[str, deque[float]] = defaultdict(deque)
_MAX_ANALYSES_PER_MINUTE = 3


def _check_analysis_rate_limit(client_key: str) -> None:
    now = time.monotonic()
    recent = _analysis_requests[client_key]
    while recent and now - recent[0] >= 60:
        recent.popleft()
    if len(recent) >= _MAX_ANALYSES_PER_MINUTE:
        raise HTTPException(status_code=429, detail='Too many location searches. Please wait before trying again.')
    recent.append(now)


@router.post('/analyze', response_model=AnalysisResponse)
async def run_full_analysis(request: AnalysisRequest, http_request: Request):
    if not is_supported_us_location(request.location_name):
        raise HTTPException(status_code=400, detail=LOCATION_OUTSIDE_COVERAGE)
    _check_analysis_rate_limit(http_request.client.host if http_request.client else 'unknown')

    try:
        polygon_dict = request.polygon.model_dump() if request.polygon else None
        fg_raw = await fortyguard_service.fetch_heat_data(
            location_name=request.location_name,
            polygon=polygon_dict,
            use_cache=request.use_cache,
        )

        observations = fg_raw.get('observations', [])
        if not observations:
            raise HTTPException(status_code=404, detail='No observations returned for specified polygon/time.')

        df = pd.DataFrame(observations)
        stats_map = compute_descriptive_stats(df)
        temp_stats = stats_map.get('temperature')

        if not temp_stats:
            raise HTTPException(status_code=422, detail='Temperature variable missing from dataset.')

        intensity = determine_heat_intensity(temp_stats.max, temp_stats.mean)
        pairs, matrix = compute_pearson_correlations(df)
        anomalies = detect_zscore_anomalies(df, threshold=2.0)
        persistence = calculate_heat_persistence(df, threshold_celsius=35.0)

        humidity_stats = stats_map.get('humidity')
        mean_hum = humidity_stats.mean if humidity_stats else 50.0

        exposure_score = calculate_heat_exposure_score(
            mean_temp=temp_stats.mean,
            max_temp=temp_stats.max,
            persistence_hours=persistence.longest_continuous_hot_spell_hours,
            anomaly_count=len(anomalies),
            mean_humidity=mean_hum,
        )

        start_t = df['timestamp'].min() if 'timestamp' in df.columns else None
        end_t = df['timestamp'].max() if 'timestamp' in df.columns else None

        # Convert all Pydantic models to dictionaries for JSON serialization
        stats_map_dict = {k: v.model_dump() for k, v in stats_map.items()}

        result_payload = {
            'location_name': request.location_name,
            'data_source': 'FORTYGUARD_FALLBACK' if fg_raw.get('_fallback') else ('FORTYGUARD_CACHE' if fg_raw.get('_from_cache') else 'FORTYGUARD_LIVE'),
            'sample_size': len(df),
            'time_bounds': {'start': str(start_t), 'end': str(end_t)},
            'descriptive_statistics': stats_map_dict,
            'heat_intensity': intensity,
            'persistence': persistence.model_dump(),
            'anomalies': [a.model_dump() for a in anomalies],
            'correlations': [p.model_dump() for p in pairs],
            'correlation_matrix': matrix,
            'heat_exposure_score': exposure_score.model_dump(),
            'timeseries_data': observations,
        }

        interpretation = gemini_service.interpret_results(result_payload)
        result_payload['gemini_interpretation'] = interpretation

        return result_payload
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f'Analysis pipeline failed: {str(e)}')
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=502, detail='FortyGuard is temporarily unavailable. Please try again shortly.')
