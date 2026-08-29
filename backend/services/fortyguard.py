import asyncio
import logging
import re
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Tuple, List

import httpx

from backend.config import settings
from backend.services.cache import cache_service

logger = logging.getLogger(__name__)
LOCATION_OUTSIDE_COVERAGE = 'Location outside FortyGuard coverage area. Please search a supported US district or area.'

_US_LOCATION_TERMS = {
    'alabama', 'alaska', 'arizona', 'arkansas', 'california', 'colorado', 'connecticut',
    'delaware', 'florida', 'georgia', 'hawaii', 'idaho', 'illinois', 'indiana', 'iowa',
    'kansas', 'kentucky', 'louisiana', 'maine', 'maryland', 'massachusetts', 'michigan',
    'minnesota', 'mississippi', 'missouri', 'montana', 'nebraska', 'nevada', 'new hampshire',
    'new jersey', 'new mexico', 'new york', 'north carolina', 'north dakota', 'ohio',
    'oklahoma', 'oregon', 'pennsylvania', 'rhode island', 'south carolina', 'south dakota',
    'tennessee', 'texas', 'utah', 'vermont', 'virginia', 'washington', 'west virginia',
    'wisconsin', 'wyoming', 'district of columbia', 'dc', 'downtown district', 'midtown area',
    'lakeside zone', 'industrial area', 'new york city', 'los angeles', 'chicago', 'houston',
    'phoenix', 'philadelphia', 'san antonio', 'san diego', 'dallas', 'austin', 'seattle',
    'denver', 'boston', 'atlanta', 'miami', 'portland', 'detroit', 'nashville', 'charlotte',
    'baltimore', 'las vegas', 'minneapolis', 'new orleans', 'san francisco', 'washington',
}
_US_STATE_ABBREVIATIONS = {
    'al', 'ak', 'az', 'ar', 'ca', 'co', 'ct', 'de', 'fl', 'ga', 'hi', 'id', 'il', 'in', 'ia',
    'ks', 'ky', 'la', 'me', 'md', 'ma', 'mi', 'mn', 'ms', 'mo', 'mt', 'ne', 'nv', 'nh', 'nj',
    'nm', 'ny', 'nc', 'nd', 'oh', 'ok', 'or', 'pa', 'ri', 'sc', 'sd', 'tn', 'tx', 'ut', 'vt',
    'va', 'wa', 'wv', 'wi', 'wy', 'dc',
}
_US_COUNTRY_MARKERS = {'us', 'usa', 'u s', 'u s a', 'united states', 'united states of america'}
_NON_US_COUNTRY_MARKERS = {
    'canada', 'mexico', 'uk', 'united kingdom', 'england', 'france', 'germany', 'india',
    'australia', 'brazil', 'china', 'japan', 'spain', 'italy',
}

# ── Known US location coordinates for instant geocoding ──────────────────────
_KNOWN_LOCATIONS: Dict[str, Tuple[float, float]] = {
    'downtown district': (40.7128, -74.0060),
    'midtown area': (40.7549, -73.9840),
    'lakeside zone': (41.8781, -87.6298),
    'industrial area': (33.7490, -84.3880),
    'new york': (40.7128, -74.0060),
    'new york city': (40.7128, -74.0060),
    'los angeles': (34.0522, -118.2437),
    'chicago': (41.8781, -87.6298),
    'houston': (29.7604, -95.3698),
    'phoenix': (33.4484, -112.0740),
    'philadelphia': (39.9526, -75.1652),
    'san antonio': (29.4241, -98.4936),
    'san diego': (32.7157, -117.1611),
    'dallas': (32.7767, -96.7970),
    'austin': (30.2672, -97.7431),
    'seattle': (47.6062, -122.3321),
    'denver': (39.7392, -104.9903),
    'boston': (42.3601, -71.0589),
    'atlanta': (33.7490, -84.3880),
    'miami': (25.7617, -80.1918),
    'portland': (45.5152, -122.6784),
    'detroit': (42.3314, -83.0458),
    'nashville': (36.1627, -86.7816),
    'charlotte': (35.2271, -80.8431),
    'baltimore': (39.2904, -76.6122),
    'las vegas': (36.1699, -115.1398),
    'minneapolis': (44.9778, -93.2650),
    'new orleans': (29.9511, -90.0715),
    'san francisco': (37.7749, -122.4194),
    'washington': (38.9072, -77.0369),
    'washington dc': (38.9072, -77.0369),
    'dc': (38.9072, -77.0369),
    'district of columbia': (38.9072, -77.0369),
    'alabama': (32.3182, -86.9023),
    'alaska': (64.2008, -152.4937),
    'arizona': (34.0489, -111.0937),
    'arkansas': (34.7465, -92.2896),
    'california': (36.7783, -119.4179),
    'colorado': (39.5501, -105.7821),
    'connecticut': (41.6032, -73.0877),
    'delaware': (38.9108, -75.5277),
    'florida': (27.6648, -81.5158),
    'georgia': (32.1656, -82.9001),
    'hawaii': (19.8968, -155.5828),
    'idaho': (44.0682, -114.7420),
    'illinois': (40.6331, -89.3985),
    'indiana': (40.2672, -86.1349),
    'iowa': (41.8780, -93.0977),
    'kansas': (39.0119, -98.4842),
    'kentucky': (37.8393, -84.2700),
    'louisiana': (30.9843, -91.9623),
    'maine': (45.2538, -69.4455),
    'maryland': (39.0458, -76.6413),
    'massachusetts': (42.4072, -71.3824),
    'michigan': (44.3148, -85.6024),
    'minnesota': (46.7296, -94.6859),
    'mississippi': (32.3547, -89.3985),
    'missouri': (37.9643, -91.8318),
    'montana': (46.8797, -110.3626),
    'nebraska': (41.4925, -99.9018),
    'nevada': (38.8026, -116.4194),
    'new hampshire': (43.1939, -71.5724),
    'new jersey': (40.0583, -74.4057),
    'new mexico': (34.5199, -105.8701),
    'north carolina': (35.7596, -79.0193),
    'north dakota': (47.5515, -101.0020),
    'ohio': (40.4173, -82.9071),
    'oklahoma': (35.0078, -97.0929),
    'oregon': (43.8041, -120.5542),
    'pennsylvania': (41.2033, -77.1945),
    'rhode island': (41.5801, -71.4774),
    'south carolina': (33.8361, -81.1637),
    'south dakota': (43.9695, -99.9018),
    'tennessee': (35.5175, -86.5804),
    'texas': (31.9686, -99.9018),
    'utah': (39.3210, -111.0937),
    'vermont': (44.5588, -72.5778),
    'virginia': (37.4316, -78.6569),
    'west virginia': (38.5976, -80.4549),
    'wisconsin': (43.7844, -88.7879),
    'wyoming': (43.0760, -107.2903),
}

# In-memory cache for geocoded locations during runtime
_geocode_cache: Dict[str, Tuple[float, float]] = {}


def is_supported_us_location(location_name: str) -> bool:
    normalized = re.sub(r'[^a-z0-9 ]+', ' ', location_name.lower()).strip()
    if not normalized:
        return False
    words = set(normalized.split())
    if any(marker in words if ' ' not in marker else marker in normalized for marker in _NON_US_COUNTRY_MARKERS):
        return False
    if any(marker in words if ' ' not in marker else marker in normalized for marker in _US_COUNTRY_MARKERS):
        return True
    if re.search(r'\b\d{5}(?:\s*[-]\s*\d{4})?\b', normalized):
        return True
    return normalized in _US_LOCATION_TERMS or bool(words & _US_STATE_ABBREVIATIONS) or any(
        term in words for term in _US_LOCATION_TERMS if ' ' not in term
    ) or any(
        term in normalized for term in _US_LOCATION_TERMS if ' ' in term
    )


async def _geocode_location(location_name: str) -> Tuple[float, float]:
    """Convert a location name to (latitude, longitude) using a local lookup
    table first, then falling back to the Nominatim (OpenStreetMap) geocoder."""
    normalized = re.sub(r'[^a-z0-9 ]+', ' ', location_name.lower()).strip()

    # 1. Check the hardcoded table of well-known US locations
    if normalized in _KNOWN_LOCATIONS:
        return _KNOWN_LOCATIONS[normalized]

    # 2. Check the runtime geocode cache
    if normalized in _geocode_cache:
        return _geocode_cache[normalized]

    # 3. Query Nominatim (free, no API key required)
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(
                'https://nominatim.openstreetmap.org/search',
                params={
                    'q': f'{location_name}, United States',
                    'format': 'json',
                    'limit': 1,
                    'countrycodes': 'us',
                },
                headers={'User-Agent': 'HeatLens/1.0'},
            )
            if resp.status_code == 200:
                results = resp.json()
                if results:
                    lat = float(results[0]['lat'])
                    lon = float(results[0]['lon'])
                    _geocode_cache[normalized] = (lat, lon)
                    logger.info('Geocoded "%s" → (%.4f, %.4f)', location_name, lat, lon)
                    return (lat, lon)
    except Exception as exc:
        logger.warning('Nominatim geocoding failed for "%s": %s', location_name, exc)

    # 4. Ultimate fallback — default to NYC so the pipeline can still run
    logger.warning('Could not geocode "%s"; defaulting to NYC coordinates', location_name)
    return (40.7128, -74.0060)


class FortyGuardService:
    def __init__(self):
        self.base_url = settings.FORTYGUARD_BASE_URL.rstrip('/')
        self.api_key = settings.FORTYGUARD_API_KEY
        self.headers = {
            'api-key': self.api_key,
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }

    # ── Async job polling ────────────────────────────────────────────────
    async def _poll_activity(self, client: httpx.AsyncClient, activity_id: str) -> Dict[str, Any]:
        """Poll ``GET /v1/status/{activity_id}`` until the job completes."""
        poll_url = f'{self.base_url}/status/{activity_id}'
        interval = settings.FORTYGUARD_POLL_INTERVAL_SEC
        last_error = None

        for attempt in range(settings.FORTYGUARD_MAX_POLL_ATTEMPTS):
            await asyncio.sleep(interval)
            try:
                resp = await client.get(poll_url, headers=self.headers, timeout=15.0)
                if resp.status_code != 200:
                    last_error = f'HTTP {resp.status_code}'
                    logger.debug('Poll attempt %d returned HTTP %d; will retry', attempt + 1, resp.status_code)
                    continue

                body = resp.json()
                # The status API wraps the payload: { "data": { "status": "...", "result": {...} } }
                data = body.get('data', body)
                status = str(data.get('status', '')).strip().lower()

                # Accept multiple status variations
                if status in ('completed', 'complete', 'success', 'done'):
                    result = data.get('result', data)
                    logger.info('FortyGuard activity %s completed', activity_id)
                    return result
                elif status in ('failed', 'error'):
                    error_detail = data.get('error', body.get('message', 'Unknown error'))
                    raise RuntimeError(f'FortyGuard job {activity_id} failed: {error_detail}')
                else:
                    # Job still processing; log status and continue polling
                    logger.debug('Poll attempt %d: status=%s', attempt + 1, status)
            except Exception as exc:
                last_error = str(exc)
                logger.debug('Poll attempt %d error: %s; will retry', attempt + 1, exc)

            # Moderate backoff (max 6 seconds between retries)
            interval = min(6.0, interval * 1.1)

        error_msg = f'FortyGuard activity {activity_id} polling timed out after {settings.FORTYGUARD_MAX_POLL_ATTEMPTS} attempts'
        if last_error:
            error_msg += f' (last error: {last_error})'
        logger.error(error_msg)
        raise TimeoutError(error_msg)

    # ── Main data-fetch entry point ──────────────────────────────────────
    async def fetch_heat_data(self, location_name: str, polygon: Dict[str, Any], use_cache: bool = True) -> Dict[str, Any]:
        """Fetch environmental heat data from the FortyGuard ``/env_params``
        endpoint.  Falls back to synthetic data on any failure so the
        analytics pipeline can always complete."""
        if not is_supported_us_location(location_name):
            raise ValueError(LOCATION_OUTSIDE_COVERAGE)

        # Geocode the human-readable location name to lat/lon
        lat, lon = await _geocode_location(location_name)

        endpoint = '/env_params'

        # Build the date_time block — request a full single-day snapshot
        today = datetime.utcnow().strftime('%Y-%m-%d')

        payload = {
            'latitude': lat,
            'longitude': lon,
            'temperature': 30.0,
            'date_time': {
                'start_date': today,
                'filter_type': 3,  # 3 = Single Day → 24 hourly values
            },
            'analysis': [
                'heat_index_celsius',
                'apparent_temperature_celsius',
                'relative_humidity_percent',
                'solar_irradiance',
            ],
        }

        if use_cache:
            cached = cache_service.get(endpoint, 'POST', payload)
            if cached:
                cached['_from_cache'] = True
                return cached

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.post(
                    f'{self.base_url}{endpoint}',
                    json=payload,
                    headers=self.headers,
                )
                body = resp.json()

                if resp.status_code in (200, 202):
                    # Extract the activity_id (may be top-level or nested)
                    activity_id = (
                        body.get('activity_id')
                        or body.get('data', {}).get('activity_id')
                    )

                    if activity_id:
                        # Asynchronous job — poll until finished
                        result = await self._poll_activity(client, activity_id)
                    else:
                        # Synchronous / direct result
                        result = body.get('data', {}).get('result', body)
                else:
                    raise RuntimeError(f'FortyGuard API Error [{resp.status_code}]: {resp.text}')

            normalized = self.normalize_response(result, location_name, lat, lon)
            cache_service.set(endpoint, 'POST', payload, normalized)
            normalized['_from_cache'] = False
            return normalized
        except Exception as error:
            logger.warning('FortyGuard unavailable for %s; using fallback data: %s', location_name, error)
            data = self._generate_fallback_sensor_data(location_name)
            data['_from_cache'] = False
            data['_fallback'] = True
            return data

    # ── Response normalization ───────────────────────────────────────────
    def normalize_response(self, raw_data: Dict[str, Any], location_name: str = '', lat: float = 0.0, lon: float = 0.0) -> Dict[str, Any]:
        """Convert the FortyGuard ``env_params`` response (parameter arrays
        keyed by name) into the flat ``observations`` list that the analytics
        pipeline expects.  Falls back to legacy parsing if the response
        doesn't match the expected structure."""
        
        # Handle the locations array format (newer FortyGuard API)
        locations = raw_data.get('locations', [])
        if locations and isinstance(locations, list):
            # Extract from the first location in the array
            location_data = locations[0]
            parameters = location_data.get('parameters', {})
            metadata = raw_data.get('metadata', {})
            # Use coordinates from the location data if available
            if 'lat' in location_data:
                lat = location_data['lat']
            if 'lon' in location_data:
                lon = location_data['lon']
        else:
            # Fall back to flat parameters structure
            parameters = raw_data.get('parameters', {})
            metadata = raw_data.get('metadata', {})

        # If there is no 'parameters' dict this might be a legacy/direct
        # response — fall through to the old normalizer.
        if not parameters:
            return self._normalize_legacy_response(raw_data)

        # ── Extract individual parameter arrays ──────────────────────────
        heat_index_arr = parameters.get('heat_index_celsius', [])
        apparent_temp_arr = parameters.get('apparent_temperature_celsius', [])
        humidity_arr = parameters.get('relative_humidity_percent', [])
        solar_raw = parameters.get('solar_irradiance', [])

        # solar_irradiance may arrive as an object with GHI/DNI/DHI keys
        if isinstance(solar_raw, dict):
            solar_arr: List = solar_raw.get('ghi', solar_raw.get('GHI', []))
        elif isinstance(solar_raw, list):
            solar_arr = solar_raw
        else:
            solar_arr = []

        # ── Timestamps ───────────────────────────────────────────────────
        timestamps: List[str] = metadata.get('timestamps', [])
        n_points = max(
            len(timestamps),
            len(heat_index_arr),
            len(apparent_temp_arr),
            len(humidity_arr),
            len(solar_arr),
            1,  # guarantee at least the loop structure
        )

        # Synthesize timestamps when the API doesn't include them
        if not timestamps:
            base_dt = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            timestamps = [(base_dt + timedelta(hours=i)).isoformat() for i in range(n_points)]

        # ── Build observation rows ───────────────────────────────────────
        def _safe_float(arr: list, idx: int) -> Optional[float]:
            if idx < len(arr) and arr[idx] is not None:
                return float(arr[idx])
            return None

        observations: List[Dict[str, Any]] = []
        for i in range(n_points):
            temp = _safe_float(apparent_temp_arr, i)
            observations.append({
                'timestamp': timestamps[i] if i < len(timestamps) else None,
                'temperature': temp,
                'humidity': _safe_float(humidity_arr, i),
                'heat_index': _safe_float(heat_index_arr, i),
                'apparent_temperature': temp,
                'solar_irradiance': _safe_float(solar_arr, i),
            })

        return {
            'metadata': {
                'location': location_name,
                'latitude': lat,
                'longitude': lon,
                **metadata,
            },
            'observations': observations,
        }

    def _normalize_legacy_response(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle responses that already arrive as a list of observation
        objects (e.g. direct / cached data)."""
        raw_series = raw_data.get('observations', raw_data.get('data', []))
        standardized_series = []

        for item in raw_series:
            standardized_series.append({
                'timestamp': item.get('timestamp', item.get('datetime')),
                'temperature': float(item.get('temperature', item.get('temp', 0.0))),
                'humidity': float(item.get('humidity', item.get('rh', 0.0))) if item.get('humidity') is not None else None,
                'heat_index': float(item.get('heat_index', item.get('hi', 0.0))) if item.get('heat_index') is not None else None,
                'apparent_temperature': float(item.get('apparent_temperature', item.get('feels_like', 0.0))) if item.get('apparent_temperature') is not None else None,
                'solar_irradiance': float(item.get('solar_irradiance', item.get('solar', 0.0))) if item.get('solar_irradiance') is not None else None,
            })

        return {
            'metadata': raw_data.get('metadata', {}),
            'observations': standardized_series,
        }

    # ── Fallback synthetic data (unchanged) ──────────────────────────────
    def _generate_fallback_sensor_data(self, location_name: str) -> Dict[str, Any]:
        import numpy as np
        import pandas as pd

        dates = pd.date_range(start='2026-08-01', periods=96, freq='1h')
        base_temp = 33.0 + 5.0 * np.sin(np.linspace(0, 8 * np.pi, 96))
        noise = np.random.normal(0, 1.2, 96)
        temps = base_temp + noise
        temps[40:48] += 6.5

        observations = []
        for i, dt in enumerate(dates):
            t = float(round(temps[i], 2))
            h = float(round(max(20.0, min(90.0, 65.0 - (t - 30.0) * 1.5 + np.random.normal(0, 2))), 2))
            hi = float(round(t + (h / 100.0) * 3.5, 2))
            observations.append({
                'timestamp': dt.isoformat(),
                'temperature': t,
                'humidity': h,
                'heat_index': hi,
                'apparent_temperature': float(round(t + 1.2, 2)),
                'solar_irradiance': float(round(max(0.0, 800.0 * np.sin(i % 24 / 24.0 * np.pi)), 1)),
            })

        return {
            'metadata': {'location': location_name, 'mode': 'STATION_NORMALIZED'},
            'observations': observations,
        }


fortyguard_service = FortyGuardService()
