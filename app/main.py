from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.api.routes import router as api_router
from app.api.endpoints import get_auth
from app.utils.database import db_manager
from app.config.settings import app_settings, Environment


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await db_manager.connect()
    yield
    # Shutdown
    await db_manager.disconnect()


app = FastAPI(
    title=app_settings.api_title,
    description=app_settings.api_description,
    version=app_settings.api_version,
    lifespan=lifespan,
    docs_url=app_settings.docs_url if not app_settings.is_production else None,
    redoc_url=app_settings.redoc_url if not app_settings.is_production else None,
    openapi_url=app_settings.openapi_url if not app_settings.is_production else None,
    debug=app_settings.debug,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=app_settings.cors_origins,
    allow_credentials=app_settings.cors_credentials,
    allow_methods=app_settings.cors_methods,
    allow_headers=app_settings.cors_headers,
)

# Include the API router
app.include_router(api_router, prefix="/api/v1")


@app.get("/")
async def root():
    return {
        "message": "Graph API with PostgreSQL Token Authentication",
        "version": "1.0.0",
        "api_docs": "/docs",
        "api_base": "/api/v1",
        "auth_endpoints": {
            "validate": "/auth/validate",
            "me": "/auth/me",
            "test_auth": "/auth/test-auth",
            "tokens": "/auth/tokens",
            "generate": "/auth/generate",
        },
        "authentication": {
            "type": "Bearer Token (Database-stored)",
            "header": "Authorization: Bearer <your-access-token>",
            "token_format": "mapi_xxxxxxxxxxxx",
        },
    }
