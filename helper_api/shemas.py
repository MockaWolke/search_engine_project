from pydantic import BaseModel


class HealthCheck(BaseModel):
    """Response model to validate and return when performing a health check."""

    status: str = "OK"


class Query(BaseModel):
    text: str


class ReloadTextQuery(BaseModel):
    url: str
    timeout: int = 10  # Default timeout value
