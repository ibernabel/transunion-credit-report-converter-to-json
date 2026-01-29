"""
TransUnion PDF to JSON API - Main Application Entry Point.

Production-ready FastAPI service to parse TransUnion Credit Reports into structured JSON.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
import asyncio

from src.api.routes import router
from src.middleware.logging_middleware import logging_middleware, start_metrics_logging
from src.utils.logging_config import api_logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for application startup and shutdown.
    
    Handles:
    - Starting background metrics logging task
    - Logging application lifecycle events
    """
    # Startup
    api_logger.info("Application starting up", extra={"version": app.version})
    
    # Start metrics logging in background
    metrics_task = asyncio.create_task(start_metrics_logging())
    
    yield
    
    # Shutdown
    api_logger.info("Application shutting down")
    metrics_task.cancel()
    try:
        await metrics_task
    except asyncio.CancelledError:
        pass


app = FastAPI(
    title="TransUnion PDF to JSON API",
    description="""
    Production-ready API to parse TransUnion Credit Reports into structured JSON with PII scrubbing.
    
    ## Features
    - PDF credit report parsing
    - Structured JSON output with Pydantic validation
    - PII scrubbing for data privacy
    - Comprehensive logging and monitoring
    - Health check endpoint
    
    ## Usage
    Upload a TransUnion credit report PDF to `/v1/parse` and receive structured JSON data.
    """,
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add logging middleware
app.middleware("http")(logging_middleware)

# Include API routes
app.include_router(router)


@app.get("/")
async def root():
    """
    Root endpoint providing API information and navigation.
    
    Returns:
        dict: API welcome message and endpoint links
    """
    return {
        "message": "Welcome to TransUnion PDF to JSON API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/v1/health",
        "parse_endpoint": "/v1/parse"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

