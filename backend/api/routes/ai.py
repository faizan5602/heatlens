import asyncio

from fastapi import APIRouter

from backend.models.requests import AiQueryRequest
from backend.models.responses import AiQueryResponse
from backend.services.gemini import gemini_service

router = APIRouter(prefix='/api/ai', tags=['AI Analyst'])


@router.post('/query', response_model=AiQueryResponse)
async def query_ai_analyst(request: AiQueryRequest):
    answer = await asyncio.to_thread(
        gemini_service.query_analyst,
        request.query.strip(),
        request.analysis_context,
    )
    return {'response': answer}
