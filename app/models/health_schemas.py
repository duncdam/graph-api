from pydantic import BaseModel, Field
from datetime import datetime
from typing import Literal


class HealthCheckResponse(BaseModel):
    """Schema for successful health check response"""

    status: Literal["healthy"] = Field(description="Health status of the service")
    service: Literal["PDM"] = Field(description="Name of the service being checked")
    neo4j_connection: Literal["active"] = Field(
        description="Status of Neo4j database connection"
    )
    database: str = Field(description="Name of the Neo4j database being used")
    timestamp: str = Field(description="ISO timestamp when health check was performed")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "service": "PDM",
                "neo4j_connection": "active",
                "database": "neo4j",
                "timestamp": "2024-01-15T10:30:00.123456+00:00",
            }
        }


class HealthCheckError(BaseModel):
    """Schema for health check error response"""

    detail: str = Field(description="Error message describing what went wrong")

    class Config:
        json_schema_extra = {
            "example": {"detail": "PDM service unhealthy: Connection to Neo4j failed"}
        }
