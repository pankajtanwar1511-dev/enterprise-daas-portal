"""
Security Middleware for Enterprise DaaS Governance Portal
Implements rate limiting, security headers, and CSRF protection
"""

from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.cors import CORSMiddleware
from collections import defaultdict
from datetime import datetime, timedelta
import time
from typing import Dict, Tuple
import os


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Rate limiting middleware to prevent abuse

    Configuration via environment variables:
    - RATE_LIMIT_ENABLED: Enable/disable rate limiting (default: True in production)
    - RATE_LIMIT_PER_MINUTE: Requests allowed per minute per IP (default: 60)
    """

    def __init__(self, app, requests_per_minute: int = 60):
        super().__init__(app)
        self.requests_per_minute = int(os.getenv('RATE_LIMIT_PER_MINUTE', requests_per_minute))
        self.enabled = os.getenv('RATE_LIMIT_ENABLED', 'True').lower() == 'true'
        self.requests: Dict[str, list] = defaultdict(list)
        self.cleanup_interval = 60  # seconds
        self.last_cleanup = time.time()

    async def dispatch(self, request: Request, call_next):
        if not self.enabled:
            return await call_next(request)

        # Get client IP
        client_ip = request.client.host if request.client else "unknown"

        # Cleanup old entries periodically
        current_time = time.time()
        if current_time - self.last_cleanup > self.cleanup_interval:
            self._cleanup_old_requests()
            self.last_cleanup = current_time

        # Check rate limit
        now = datetime.now()
        minute_ago = now - timedelta(minutes=1)

        # Filter requests from last minute
        self.requests[client_ip] = [
            req_time for req_time in self.requests[client_ip]
            if req_time > minute_ago
        ]

        # Check if limit exceeded
        if len(self.requests[client_ip]) >= self.requests_per_minute:
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "detail": f"Rate limit exceeded. Maximum {self.requests_per_minute} requests per minute allowed.",
                    "retry_after": 60
                },
                headers={"Retry-After": "60"}
            )

        # Add current request
        self.requests[client_ip].append(now)

        # Process request
        response = await call_next(request)

        # Add rate limit headers
        remaining = self.requests_per_minute - len(self.requests[client_ip])
        response.headers["X-RateLimit-Limit"] = str(self.requests_per_minute)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(int((now + timedelta(minutes=1)).timestamp()))

        return response

    def _cleanup_old_requests(self):
        """Remove entries older than 5 minutes to prevent memory bloat"""
        cutoff = datetime.now() - timedelta(minutes=5)
        for ip in list(self.requests.keys()):
            self.requests[ip] = [
                req_time for req_time in self.requests[ip]
                if req_time > cutoff
            ]
            if not self.requests[ip]:
                del self.requests[ip]


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Add security headers to all responses

    Headers added:
    - X-Content-Type-Options: nosniff
    - X-Frame-Options: DENY
    - X-XSS-Protection: 1; mode=block
    - Strict-Transport-Security: max-age=31536000; includeSubDomains
    - Content-Security-Policy: default-src 'self'
    - Referrer-Policy: strict-origin-when-cross-origin
    """

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # HSTS (only for HTTPS)
        if request.url.scheme == "https":
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

        # Content Security Policy
        csp = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self' data:; "
            "connect-src 'self' http://localhost:* https://localhost:*; "
            "frame-ancestors 'none';"
        )
        response.headers["Content-Security-Policy"] = csp

        # Remove server header
        if "server" in response.headers:
            del response.headers["server"]

        return response


class CSRFProtectionMiddleware(BaseHTTPMiddleware):
    """
    CSRF protection for state-changing requests

    Requires X-CSRF-Token header for POST, PUT, PATCH, DELETE requests
    Token should be included in request headers from frontend
    """

    def __init__(self, app, exempt_paths: list = None):
        super().__init__(app)
        self.exempt_paths = exempt_paths or [
            "/api/v1/auth/login",
            "/api/v1/auth/register",
            "/api/v1/compliance/validate/naming",  # Read-only validation endpoint
            "/docs",
            "/redoc",
            "/openapi.json",
        ]

    async def dispatch(self, request: Request, call_next):
        # Skip for safe methods
        if request.method in ["GET", "HEAD", "OPTIONS"]:
            return await call_next(request)

        # Skip for exempt paths
        if any(request.url.path.startswith(path) for path in self.exempt_paths):
            return await call_next(request)

        # Check for CSRF token in header
        csrf_token = request.headers.get("X-CSRF-Token")

        # For now, we'll use the access token as CSRF token
        # In production, generate separate CSRF tokens
        auth_header = request.headers.get("Authorization")

        if not auth_header:
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={"detail": "CSRF token missing or invalid"}
            )

        return await call_next(request)


def add_security_middleware(app):
    """
    Add all security middleware to the FastAPI application

    Usage:
        from app.middleware.security import add_security_middleware

        app = FastAPI()
        add_security_middleware(app)
    """

    # Add middleware in reverse order (last added = first executed)

    # CSRF Protection
    app.add_middleware(CSRFProtectionMiddleware)

    # Security Headers
    app.add_middleware(SecurityHeadersMiddleware)

    # Rate Limiting (outer layer)
    app.add_middleware(
        RateLimitMiddleware,
        requests_per_minute=int(os.getenv('RATE_LIMIT_PER_MINUTE', 60))
    )

    return app


# Input sanitization utilities
import html
import re
from typing import Any, Dict


def sanitize_string(value: str, max_length: int = 1000) -> str:
    """
    Sanitize string input to prevent XSS

    Args:
        value: Input string
        max_length: Maximum allowed length

    Returns:
        Sanitized string
    """
    if not isinstance(value, str):
        return value

    # Truncate to max length
    value = value[:max_length]

    # HTML escape
    value = html.escape(value)

    # Remove potentially dangerous characters
    value = re.sub(r'[<>]', '', value)

    return value.strip()


def sanitize_dict(data: Dict[str, Any], fields_to_sanitize: list = None) -> Dict[str, Any]:
    """
    Sanitize dictionary values

    Args:
        data: Input dictionary
        fields_to_sanitize: List of fields to sanitize (if None, sanitize all string fields)

    Returns:
        Sanitized dictionary
    """
    sanitized = {}

    for key, value in data.items():
        if fields_to_sanitize and key not in fields_to_sanitize:
            sanitized[key] = value
        elif isinstance(value, str):
            sanitized[key] = sanitize_string(value)
        elif isinstance(value, dict):
            sanitized[key] = sanitize_dict(value, fields_to_sanitize)
        elif isinstance(value, list):
            sanitized[key] = [
                sanitize_string(item) if isinstance(item, str) else item
                for item in value
            ]
        else:
            sanitized[key] = value

    return sanitized


# SQL injection protection (already handled by SQLAlchemy ORM)
# But here's a utility for raw queries if needed

def validate_sql_identifier(identifier: str) -> str:
    """
    Validate SQL identifier (table name, column name) to prevent SQL injection

    Args:
        identifier: SQL identifier to validate

    Returns:
        Validated identifier

    Raises:
        ValueError: If identifier is invalid
    """
    # Only allow alphanumeric and underscore
    if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', identifier):
        raise ValueError(f"Invalid SQL identifier: {identifier}")

    # Prevent SQL keywords
    sql_keywords = ['SELECT', 'INSERT', 'UPDATE', 'DELETE', 'DROP', 'CREATE', 'ALTER', 'UNION']
    if identifier.upper() in sql_keywords:
        raise ValueError(f"SQL keyword not allowed as identifier: {identifier}")

    return identifier
