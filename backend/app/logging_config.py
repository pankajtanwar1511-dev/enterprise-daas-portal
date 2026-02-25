"""
Logging Configuration for Enterprise DaaS Governance Portal
Structured logging with structlog and Sentry integration
"""

import os
import sys
import logging
from pathlib import Path
from typing import Any, Dict
import structlog
from structlog.types import Processor
from structlog.stdlib import LoggerFactory


def setup_logging(
    log_level: str = None,
    enable_sentry: bool = None,
    sentry_dsn: str = None,
    environment: str = None
) -> None:
    """
    Configure structured logging with structlog and optional Sentry integration

    Args:
        log_level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        enable_sentry: Enable Sentry error tracking
        sentry_dsn: Sentry DSN for error reporting
        environment: Environment name (development, staging, production)
    """
    # Get configuration from environment if not provided
    log_level = log_level or os.getenv("LOG_LEVEL", "INFO")
    enable_sentry = enable_sentry if enable_sentry is not None else os.getenv("ENABLE_SENTRY", "false").lower() == "true"
    sentry_dsn = sentry_dsn or os.getenv("SENTRY_DSN", "")
    environment = environment or os.getenv("ENVIRONMENT", "development")

    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, log_level.upper())
    )

    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    # Configure processors for structlog
    processors: list[Processor] = [
        # Add log level
        structlog.stdlib.add_log_level,
        # Add timestamp
        structlog.processors.TimeStamper(fmt="iso"),
        # Add logger name
        structlog.stdlib.add_logger_name,
        # Add context
        structlog.contextvars.merge_contextvars,
        # Add stack info for exceptions
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]

    # Development: Pretty console output with colors
    if environment == "development":
        processors.extend([
            structlog.dev.ConsoleRenderer(colors=True)
        ])
    # Production: JSON output for log aggregation
    else:
        processors.extend([
            structlog.processors.dict_tracebacks,
            structlog.processors.JSONRenderer()
        ])

    # Configure structlog
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Initialize Sentry if enabled
    if enable_sentry and sentry_dsn:
        try:
            import sentry_sdk
            from sentry_sdk.integrations.logging import LoggingIntegration
            from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
            from sentry_sdk.integrations.fastapi import FastApiIntegration

            # Configure Sentry logging integration
            sentry_logging = LoggingIntegration(
                level=logging.INFO,  # Capture info and above as breadcrumbs
                event_level=logging.ERROR  # Send errors as events
            )

            sentry_sdk.init(
                dsn=sentry_dsn,
                environment=environment,
                traces_sample_rate=1.0 if environment == "development" else 0.1,
                profiles_sample_rate=1.0 if environment == "development" else 0.1,
                integrations=[
                    sentry_logging,
                    SqlalchemyIntegration(),
                    FastApiIntegration(),
                ],
                # Set release version
                release=os.getenv("APP_VERSION", "unknown"),
                # Send personal data
                send_default_pii=False,
                # Capture local variables in stack traces
                attach_stacktrace=True,
                # Maximum breadcrumbs
                max_breadcrumbs=50,
            )

            logger = structlog.get_logger(__name__)
            logger.info(
                "sentry_initialized",
                environment=environment,
                dsn_configured=bool(sentry_dsn)
            )

        except ImportError:
            logger = structlog.get_logger(__name__)
            logger.warning(
                "sentry_import_failed",
                message="sentry-sdk not installed, Sentry integration disabled"
            )
        except Exception as e:
            logger = structlog.get_logger(__name__)
            logger.error(
                "sentry_initialization_failed",
                error=str(e)
            )

    # Log configuration complete
    logger = structlog.get_logger(__name__)
    logger.info(
        "logging_configured",
        log_level=log_level,
        environment=environment,
        sentry_enabled=enable_sentry and bool(sentry_dsn)
    )


def get_logger(name: str = None) -> structlog.BoundLogger:
    """
    Get a configured logger instance

    Args:
        name: Logger name (usually __name__)

    Returns:
        Configured structlog logger
    """
    return structlog.get_logger(name)


# Request logging context manager
class RequestLogger:
    """Context manager for logging request details"""

    def __init__(self, logger: structlog.BoundLogger, request_id: str):
        self.logger = logger
        self.request_id = request_id

    def __enter__(self):
        structlog.contextvars.bind_contextvars(request_id=self.request_id)
        return self.logger

    def __exit__(self, exc_type, exc_val, exc_tb):
        structlog.contextvars.unbind_contextvars("request_id")


# Utility functions for common logging patterns
def log_api_request(
    logger: structlog.BoundLogger,
    method: str,
    path: str,
    status_code: int,
    duration_ms: float,
    user_id: int = None,
    error: str = None
) -> None:
    """
    Log API request with standardized format

    Args:
        logger: structlog logger instance
        method: HTTP method (GET, POST, etc.)
        path: Request path
        status_code: HTTP status code
        duration_ms: Request duration in milliseconds
        user_id: Authenticated user ID (if any)
        error: Error message (if any)
    """
    log_data = {
        "event": "api_request",
        "method": method,
        "path": path,
        "status_code": status_code,
        "duration_ms": duration_ms,
    }

    if user_id:
        log_data["user_id"] = user_id

    if error:
        log_data["error"] = error

    # Choose log level based on status code
    if status_code >= 500:
        logger.error(**log_data)
    elif status_code >= 400:
        logger.warning(**log_data)
    else:
        logger.info(**log_data)


def log_database_query(
    logger: structlog.BoundLogger,
    query_type: str,
    table: str,
    duration_ms: float,
    rows_affected: int = None,
    error: str = None
) -> None:
    """
    Log database query with standardized format

    Args:
        logger: structlog logger instance
        query_type: Type of query (SELECT, INSERT, UPDATE, DELETE)
        table: Table name
        duration_ms: Query duration in milliseconds
        rows_affected: Number of rows affected
        error: Error message (if any)
    """
    log_data = {
        "event": "database_query",
        "query_type": query_type,
        "table": table,
        "duration_ms": duration_ms,
    }

    if rows_affected is not None:
        log_data["rows_affected"] = rows_affected

    if error:
        log_data["error"] = error
        logger.error(**log_data)
    else:
        logger.debug(**log_data)


def log_background_task(
    logger: structlog.BoundLogger,
    task_name: str,
    status: str,
    duration_ms: float = None,
    error: str = None,
    **kwargs
) -> None:
    """
    Log background task execution

    Args:
        logger: structlog logger instance
        task_name: Name of the background task
        status: Status (started, completed, failed)
        duration_ms: Task duration in milliseconds
        error: Error message (if any)
        **kwargs: Additional context
    """
    log_data = {
        "event": "background_task",
        "task_name": task_name,
        "status": status,
        **kwargs
    }

    if duration_ms:
        log_data["duration_ms"] = duration_ms

    if error:
        log_data["error"] = error
        logger.error(**log_data)
    elif status == "failed":
        logger.error(**log_data)
    elif status == "completed":
        logger.info(**log_data)
    else:
        logger.debug(**log_data)


def log_security_event(
    logger: structlog.BoundLogger,
    event_type: str,
    severity: str,
    user_id: int = None,
    ip_address: str = None,
    details: Dict[str, Any] = None
) -> None:
    """
    Log security-related events

    Args:
        logger: structlog logger instance
        event_type: Type of security event (login_failed, rate_limit_exceeded, etc.)
        severity: Severity level (low, medium, high, critical)
        user_id: User ID involved
        ip_address: IP address involved
        details: Additional details
    """
    log_data = {
        "event": "security_event",
        "event_type": event_type,
        "severity": severity,
    }

    if user_id:
        log_data["user_id"] = user_id

    if ip_address:
        log_data["ip_address"] = ip_address

    if details:
        log_data.update(details)

    # Choose log level based on severity
    if severity in ["high", "critical"]:
        logger.error(**log_data)
    elif severity == "medium":
        logger.warning(**log_data)
    else:
        logger.info(**log_data)
