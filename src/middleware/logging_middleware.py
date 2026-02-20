"""
Logging middleware for CreditGraph Parser API.

Provides request/response logging with timing information and system metrics monitoring.
"""

from fastapi import Request
from typing import Callable
import time
import asyncio
from src.utils.logging_config import api_logger, log_system_metrics


async def logging_middleware(request: Request, call_next: Callable):
    """
    Middleware to log request and response information.

    Args:
        request: FastAPI request object
        call_next: Next middleware/route handler

    Returns:
        Response object
    """
    start_time = time.time()

    # Log request
    api_logger.info(
        "Incoming request",
        extra={
            'method': request.method,
            'url': str(request.url),
            'client_host': request.client.host if request.client else None,
            'user_agent': request.headers.get('user-agent', 'unknown')
        }
    )

    # Process request
    try:
        response = await call_next(request)
        process_time = time.time() - start_time

        # Log response
        api_logger.info(
            "Request completed",
            extra={
                'method': request.method,
                'url': str(request.url),
                'status_code': response.status_code,
                'process_time': f"{process_time:.3f}s"
            }
        )

        return response

    except Exception as e:
        process_time = time.time() - start_time

        # Log error
        api_logger.error(
            "Request failed",
            extra={
                'method': request.method,
                'url': str(request.url),
                'error': str(e),
                'error_type': type(e).__name__,
                'process_time': f"{process_time:.3f}s"
            }
        )
        raise


async def start_metrics_logging():
    """
    Background task to periodically log system metrics.

    Logs system metrics (CPU, memory, disk usage) every 60 seconds.
    """
    while True:
        log_system_metrics()
        await asyncio.sleep(60)  # Log metrics every minute
