"""
Security headers middleware for TransUnion PDF to JSON API.

Implements OWASP recommended security headers to protect against common web vulnerabilities.
"""

from fastapi import Request
from typing import Callable
import os


async def security_headers_middleware(request: Request, call_next: Callable):
    """
    Add security headers to all HTTP responses.
    
    Headers implemented:
    - X-Content-Type-Options: Prevents MIME type sniffing
    - X-Frame-Options: Prevents clickjacking attacks
    - X-XSS-Protection: Enables browser XSS filter
    - Strict-Transport-Security: Enforces HTTPS connections
    - Content-Security-Policy: Restricts resource loading
    - Referrer-Policy: Controls referrer information
    
    Args:
        request: FastAPI request object
        call_next: Next middleware/route handler
        
    Returns:
        Response with security headers added
    """
    response = await call_next(request)
    
    # Prevent MIME type sniffing
    response.headers["X-Content-Type-Options"] = "nosniff"
    
    # Prevent clickjacking by disallowing iframe embedding
    response.headers["X-Frame-Options"] = "DENY"
    
    # Enable browser XSS protection
    response.headers["X-XSS-Protection"] = "1; mode=block"
    
    # Enforce HTTPS for 1 year (only in production)
    if os.getenv("DEBUG", "0") == "0":
        response.headers["Strict-Transport-Security"] = (
            "max-age=31536000; includeSubDomains; preload"
        )
    
    # Content Security Policy - only allow resources from same origin
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline'; "  # Allow inline scripts for API docs
        "style-src 'self' 'unsafe-inline'; "   # Allow inline styles for API docs
        "img-src 'self' data:; "
        "font-src 'self' data:; "
        "connect-src 'self'; "
        "frame-ancestors 'none'"
    )
    
    # Control referrer information sent to other sites
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    
    # Prevent browsers from performing MIME type sniffing
    response.headers["X-Download-Options"] = "noopen"
    
    # Disable DNS prefetching to prevent privacy leaks
    response.headers["X-DNS-Prefetch-Control"] = "off"
    
    # Remove server identification header
    response.headers["Server"] = "TransUnion Parser API"
    
    return response
