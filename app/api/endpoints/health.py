from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException
from app.utils import app_utils
from app.utils.app_utils import logger
from app.models.health_schemas import HealthCheckResponse, HealthCheckError


# Configure router
router = APIRouter()


# Health check endpoint for PDM service
@router.get(
    "/",
    summary="Service Health Check",
    description="Check if the PDM service is healthy and can connect to Neo4j",
    response_model=HealthCheckResponse,
    responses={
        200: {"description": "Service is healthy", "model": HealthCheckResponse},
        503: {"description": "Service is unhealthy", "model": HealthCheckError},
    },
)
async def pdm_health_check() -> HealthCheckResponse:
    """Check if the PDM service is healthy and can connect to Neo4j"""
    try:
        # Test Neo4j connection with a simple query
        test_query = "RETURN 'PDM service healthy' as status"

        # Use app_utils to test connection
        result = await app_utils.execute_cypher_query(
            query=test_query,
            uri=app_utils.neo.uri,
            username=app_utils.neo.username,
            password=app_utils.neo.password,
            database=app_utils.neo.database,
        )

        return HealthCheckResponse(
            status="healthy",
            service="PDM",
            neo4j_connection="active",
            database=app_utils.neo.database,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )

    except Exception as e:
        logger.error(f"PDM health check failed: {str(e)}")
        raise HTTPException(status_code=503, detail=f"PDM service unhealthy: {str(e)}")
