from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str = "nok"
    environment: str | None
    debug: bool | None
