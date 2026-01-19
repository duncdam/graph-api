from fastapi import APIRouter
from app.api.endpoints import get_pdm, get_info, health, get_auth


api_router = APIRouter()

# Include auth routes
api_router.include_router(get_auth.router, prefix="/auth", tags=["authentication"])


# Include all sub-routers
api_router.include_router(get_pdm.router, prefix="/pdm", tags=["PDM"])
api_router.include_router(get_info.router, prefix="/info", tags=["Info"])
api_router.include_router(health.router, prefix="/health", tags=["Health"])


# Root endpoint for the API
@api_router.get("/")
async def api_root():
    return {
        "message": "Graph API v1",
        "services": {
            "pdm": {
                "description": "Patient Data Management",
                "endpoints": [
                    "/pdm/golden/{patient_id}",
                    "/pdm/golden/{patient_id}/summary",
                    "/pdm/golden/{patient_id}/type/{data_type}",
                    "/pdm/golden/{patient_id}/types",
                    "/pdm/health",
                ],
            },
            "info": {
                "description": "Medical Code Information Service",
                "endpoints": [
                    "/info/medications/{patient_id}",
                    "/info/conditions/{patient_id}",
                    "/info/procedures/{patient_id}",
                    "/info/observations/{patient_id}",
                    "/info/allergies/{patient_id}",
                    "/info/immunizations/{patient_id}",
                    "/info/providers/{patient_id}",
                    "/info/clinical-notes/{patient_id}",
                    "/info/encounters/{patient_id}",
                    "/info/",
                ],
                "supported_data_types": [
                    "medications",
                    "conditions",
                    "procedures",
                    "observations",
                    "allergies",
                    "immunizations",
                    "providers",
                    "clinical_notes",
                    "encounters",
                ],
            },
            "health": {
                "description": "Health Check Service",
                "endpoints": ["/health/"],
            },
        },
        "documentation": "/docs",
        "available_endpoints": {
            "patient_data_management": {
                "base_path": "/pdm",
                "endpoints": [
                    "GET /pdm/golden/{patient_id} - Get comprehensive patient data",
                    "GET /pdm/golden/{patient_id}/summary - Get patient data summary",
                    "GET /pdm/golden/{patient_id}/type/{data_type} - Get specific data type",
                    "GET /pdm/golden/{patient_id}/types - Get available data types",
                    "GET /pdm/health - PDM service health check",
                ],
            },
            "medical_codes": {
                "base_path": "/info",
                "endpoints": [
                    "GET /info/medications/{patient_id} - Get patient medications with codes",
                    "GET /info/conditions/{patient_id} - Get patient conditions with codes",
                    "GET /info/procedures/{patient_id} - Get patient procedures with codes",
                    "GET /info/observations/{patient_id} - Get patient observations with codes",
                    "GET /info/allergies/{patient_id} - Get patient allergies with codes",
                    "GET /info/immunizations/{patient_id} - Get patient immunizations with codes",
                    "GET /info/providers/{patient_id} - Get patient healthcare providers",
                    "GET /info/clinical-notes/{patient_id} - Get patient clinical notes",
                    "GET /info/encounters/{patient_id} - Get patient encounters/visits",
                    "GET /info/ - Medical code service information",
                ],
            },
            "health_monitoring": {
                "base_path": "/health",
                "endpoints": ["GET /health/ - API health status"],
            },
        },
        "response_formats": {
            "success": {
                "patient_id": "string",
                "data_type": "string",
                "data": "array",
                "count": "integer",
            },
            "error": {
                "error": "string",
                "patient_id": "string (optional)",
                "status_code": "integer",
                "endpoint": "string (optional)",
            },
        },
    }


# Export the router
router = api_router
