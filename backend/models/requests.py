from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class PolygonCoordinates(BaseModel):
    coordinates: List[List[List[float]]] = Field(
        ...,
        description="GeoJSON Polygon coordinates [[[lon, lat], ...]]",
    )


class AnalysisRequest(BaseModel):
    location_name: str = Field(..., example="Downtown Commercial District")
    polygon: Optional[PolygonCoordinates] = None
    start_time: Optional[str] = Field(None, example="2026-08-01T00:00:00Z")
    end_time: Optional[str] = Field(None, example="2026-08-07T23:59:59Z")
    use_cache: bool = True


class ComparisonRequest(BaseModel):
    location_a: AnalysisRequest
    location_b: AnalysisRequest


class AiQueryRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=300)
    analysis_context: Optional[Dict[str, Any]] = None
