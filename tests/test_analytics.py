import pandas as pd

from backend.analytics.scoring import calculate_heat_exposure_score
from backend.analytics.statistics import compute_descriptive_stats
from backend.services.gemini import GeminiService


def test_descriptive_stats_computation():
    df = pd.DataFrame({'temperature': [30.0, 32.0, 34.0, 36.0, 38.0]})
    stats = compute_descriptive_stats(df)
    assert stats['temperature'].mean == 34.0
    assert stats['temperature'].max == 38.0


def test_deterministic_exposure_score():
    score = calculate_heat_exposure_score(
        mean_temp=35.0,
        max_temp=41.0,
        persistence_hours=12.0,
        anomaly_count=2,
        mean_humidity=60.0,
    )
    assert 0 <= score.overall_score <= 100
    assert score.classification in ['EXTREME EXPOSURE', 'HIGH EXPOSURE']


def test_ai_fallback_answers_correlation_question():
    context = {
        'correlations': [{
            'variable_x': 'humidity',
            'variable_y': 'temperature',
            'coefficient': 0.72,
            'sample_size': 24,
            'direction': 'positive',
            'strength': 'strong',
        }],
    }

    answer = GeminiService._analyst_fallback('Is humidity correlated with heat?', context)

    assert '0.72' in answer
    assert '24 observations' in answer
    assert 'not causation' in answer


def test_ai_fallback_reports_missing_correlation():
    answer = GeminiService._analyst_fallback(
        'Is humidity correlated with heat?',
        {'correlations': []},
    )

    assert answer == 'No humidity correlation was included in the calculated analysis context.'


def test_gemini_rotates_to_next_client_on_rate_limit():
    class RateLimitError(Exception):
        code = 429

    class FakeModels:
        def __init__(self, response=None, error=None):
            self.response = response
            self.error = error

        def generate_content(self, **kwargs):
            if self.error:
                raise self.error
            return self.response

    class FakeClient:
        def __init__(self, models):
            self.models = models

    service = GeminiService.__new__(GeminiService)
    service._clients = [
        FakeClient(FakeModels(error=RateLimitError())),
        FakeClient(FakeModels(response='second-key-response')),
    ]
    service._active_client_index = 0
    service._client_lock = __import__('threading').Lock()
    service.client = service._clients[0]

    response = service._generate_content(prompt='test', config=None)

    assert response == 'second-key-response'
    assert service.client is service._clients[1]
