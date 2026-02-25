"""
Logging Middleware for Enterprise DaaS Governance Portal
Automatic request/response logging with timing
"""

import time
import uuid
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import structlog

from app.logging_config import log_api_request


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware to log all API requests with timing and context

    Features:
    - Generates unique request ID for tracing
    - Logs request method, path, and parameters
    - Measures request duration
    - Logs response status code
    - Logs errors and exceptions
    - Adds request ID to response headers
    """

    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.logger = structlog.get_logger(__name__)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request and log details

        Args:
            request: Incoming HTTP request
            call_next: Next middleware/endpoint handler

        Returns:
            HTTP response
        """
        # Generate unique request ID
        request_id = str(uuid.uuid4())

        # Bind request context
        structlog.contextvars.bind_contextvars(
            request_id=request_id,
            method=request.method,
            path=request.url.path,
            client_ip=request.client.host if request.client else "unknown"
        )

        # Start timer
        start_time = time.time()

        # Log request received
        self.logger.debug(
            "request_received",
            method=request.method,
            path=request.url.path,
            query_params=dict(request.query_params)
        )

        try:
            # Add request ID to request state for access in endpoints
            request.state.request_id = request_id

            # Process request
            response = await call_next(request)

            # Calculate duration
            duration_ms = (time.time() - start_time) * 1000

            # Extract user ID if authenticated
            user_id = getattr(request.state, "user_id", None)

            # Log successful request
            log_api_request(
                logger=self.logger,
                method=request.method,
                path=request.url.path,
                status_code=response.status_code,
                duration_ms=duration_ms,
                user_id=user_id
            )

            # Add request ID to response headers
            response.headers["X-Request-ID"] = request_id

            return response

        except Exception as e:
            # Calculate duration
            duration_ms = (time.time() - start_time) * 1000

            # Log error
            self.logger.error(
                "request_failed",
                method=request.method,
                path=request.url.path,
                duration_ms=duration_ms,
                error=str(e),
                error_type=type(e).__name__
            )

            # Re-raise exception for FastAPI error handlers
            raise

        finally:
            # Unbind request context
            structlog.contextvars.unbind_contextvars(
                "request_id",
                "method",
                "path",
                "client_ip"
            )


class DatabaseLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware to log database query statistics

    Note: This is a simple implementation. For production, consider using
    SQLAlchemy events or database-specific logging tools.
    """

    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.logger = structlog.get_logger(__name__)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Track database query count and timing

        Args:
            request: Incoming HTTP request
            call_next: Next middleware/endpoint handler

        Returns:
            HTTP response
        """
        # Track query count (would need SQLAlchemy event listeners for accurate count)
        # This is a placeholder for demonstration

        start_time = time.time()
        response = await call_next(request)
        duration_ms = (time.time() - start_time) * 1000

        # Log database statistics if available
        # In production, this would come from SQLAlchemy event listeners
        if duration_ms > 1000:  # Log slow requests (>1s)
            self.logger.warning(
                "slow_request_detected",
                path=request.url.path,
                duration_ms=duration_ms,
                warning="Request took longer than 1 second"
            )

        return response


class PerformanceLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware to log performance metrics

    Tracks:
    - Request processing time
    - Memory usage changes
    - Slow endpoints
    """

    def __init__(self, app: ASGIApp, slow_request_threshold_ms: float = 1000):
        super().__init__(app)
        self.logger = structlog.get_logger(__name__)
        self.slow_request_threshold_ms = slow_request_threshold_ms

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Monitor request performance

        Args:
            request: Incoming HTTP request
            call_next: Next middleware/endpoint handler

        Returns:
            HTTP response
        """
        start_time = time.time()

        try:
            response = await call_next(request)
            duration_ms = (time.time() - start_time) * 1000

            # Log slow requests
            if duration_ms > self.slow_request_threshold_ms:
                self.logger.warning(
                    "slow_endpoint",
                    method=request.method,
                    path=request.url.path,
                    duration_ms=duration_ms,
                    threshold_ms=self.slow_request_threshold_ms
                )

            # Add timing header
            response.headers["X-Response-Time"] = f"{duration_ms:.2f}ms"

            return response

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000

            self.logger.error(
                "request_exception",
                method=request.method,
                path=request.url.path,
                duration_ms=duration_ms,
                exception=str(e)
            )

            raise
