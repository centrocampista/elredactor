from fastapi import FastAPI
from .config import settings
app = FastAPI(
    title="El Redactor",
    version="0.1.0",
    docs_url="/docs" if not settings.is_prod else None,
    redoc_url="/redoc" if not settings.is_prod else None,
    openapi_url="/openapi.json" if not settings.is_prod else None,
)

@app.get('/health')
async def health() -> dict:
    response = {'status':'ok'}
    if settings.is_dev:
        response['environment'] = settings.environment
        response['debug'] = settings.debug
    return response