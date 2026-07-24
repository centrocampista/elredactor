from fastapi import APIRouter
from app.config import settings
from app.schemas.health import HealthResponse

router = APIRouter(prefix="/health", tags=["health"])


@router.get("", response_model_exclude_none=True, response_model_exclude_unset=True)
async def health() -> HealthResponse:
    environment = settings.environment if settings.is_dev else None
    debug = settings.debug if settings.is_dev else None

    return HealthResponse(status="ok", environment=environment, debug=debug)
