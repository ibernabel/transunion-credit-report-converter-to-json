"""
CreditGraph Parser API - Main Application Entry Point.

Production-ready FastAPI service to parse credit reports into structured JSON using CreditGraph AI patterns.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import os

from src.api.routes import router
from src.middleware.logging_middleware import logging_middleware, start_metrics_logging
from src.middleware.security_headers import security_headers_middleware
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
    title="CreditGraph Parser API",
    description="""
    Production-ready API to parse credit reports into structured JSON with CreditGraph AI patterns and PII scrubbing.
    
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

# Configure CORS - restrict origins in production
allowed_origins = os.getenv(
    "ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:5173")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins.split(","),
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
    max_age=600,  # Cache preflight requests for 10 minutes
)

# Add security headers middleware
app.middleware("http")(security_headers_middleware)

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
        "message": "Welcome to CreditGraph Parser API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/v1/health",
        "parse_endpoint": "/v1/parse"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
