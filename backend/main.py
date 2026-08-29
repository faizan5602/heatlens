from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.routes import ai, analysis
from backend.config import settings

app = FastAPI(
    title='HeatLens Analytics API',
    description='Hyperlocal Heat Intelligence Platform — FortyGuard Hackathon 2026',
    version='1.0.0',
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

app.include_router(analysis.router)
app.include_router(ai.router)


@app.get('/health')
def health_check():
    return {
        'status': 'healthy',
        'environment': settings.ENVIRONMENT,
        'cache_directory': str(settings.CACHE_DIR),
    }


if __name__ == '__main__':
    import uvicorn

    uvicorn.run(
        'backend.main:app',
        host=settings.HOST,
        port=settings.PORT,
        reload=True if settings.ENVIRONMENT == 'development' else False,
    )
