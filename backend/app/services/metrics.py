"""
Prometheus Metrics Collection for Enterprise DaaS Governance Portal
Exposes application and business metrics for monitoring
"""

import os
import time
from typing import Callable
from prometheus_client import (
    Counter,
    Histogram,
    Gauge,
    Info,
    generate_latest,
    CONTENT_TYPE_LATEST,
    CollectorRegistry,
    REGISTRY
)
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import structlog

from app.logging_config import get_logger

logger = get_logger(__name__)

# Create custom registry (optional - use REGISTRY for default)
# metrics_registry = CollectorRegistry()

# ==================== Application Metrics ====================

# Request metrics
http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status_code']
)

http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request latency in seconds',
    ['method', 'endpoint'],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1.0, 2.5, 5.0, 7.5, 10.0)
)

http_request_size_bytes = Histogram(
    'http_request_size_bytes',
    'HTTP request size in bytes',
    ['method', 'endpoint']
)

http_response_size_bytes = Histogram(
    'http_response_size_bytes',
    'HTTP response size in bytes',
    ['method', 'endpoint']
)

# Active connections
http_requests_in_progress = Gauge(
    'http_requests_in_progress',
    'Number of HTTP requests currently being processed',
    ['method', 'endpoint']
)

# ==================== Database Metrics ====================

database_queries_total = Counter(
    'database_queries_total',
    'Total database queries',
    ['query_type', 'table']
)

database_query_duration_seconds = Histogram(
    'database_query_duration_seconds',
    'Database query duration in seconds',
    ['query_type', 'table']
)

database_connections_active = Gauge(
    'database_connections_active',
    'Number of active database connections'
)

database_connection_pool_size = Gauge(
    'database_connection_pool_size',
    'Database connection pool size'
)

# ==================== Business Metrics ====================

# Asset metrics
assets_total = Gauge(
    'assets_total',
    'Total number of assets',
    ['environment', 'domain']
)

assets_compliance_rate = Gauge(
    'assets_compliance_rate',
    'Asset naming compliance rate (0-1)',
    ['domain']
)

assets_by_lifecycle_stage = Gauge(
    'assets_by_lifecycle_stage',
    'Number of assets by lifecycle stage',
    ['lifecycle_stage']
)

# User activity
user_login_total = Counter(
    'user_login_total',
    'Total user logins',
    ['status']  # success, failed
)

user_active_sessions = Gauge(
    'user_active_sessions',
    'Number of active user sessions'
)

# Change requests
change_requests_total = Counter(
    'change_requests_total',
    'Total change requests',
    ['type', 'status']
)

change_requests_pending = Gauge(
    'change_requests_pending',
    'Number of pending change requests',
    ['risk_level']
)

# Compliance violations
compliance_violations_total = Counter(
    'compliance_violations_total',
    'Total compliance violations',
    ['violation_type', 'severity']
)

compliance_violations_open = Gauge(
    'compliance_violations_open',
    'Number of open compliance violations',
    ['severity']
)

# ==================== System Metrics ====================

application_info = Info(
    'application',
    'Application information'
)

# Set application info
application_info.info({
    'name': 'Enterprise DaaS Governance Portal',
    'version': os.getenv('APP_VERSION', '2.0.0'),
    'environment': os.getenv('ENVIRONMENT', 'development')
})


class PrometheusMetricsMiddleware(BaseHTTPMiddleware):
    """
    Middleware to collect HTTP request/response metrics for Prometheus

    Collects:
    - Request count by method, endpoint, status
    - Request duration (histogram)
    - Request/response sizes
    - In-progress requests (gauge)
    """

    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.logger = logger

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Collect metrics for each request

        Args:
            request: Incoming HTTP request
            call_next: Next middleware/endpoint handler

        Returns:
            HTTP response
        """
        # Skip metrics endpoint itself
        if request.url.path == "/metrics":
            return await call_next(request)

        method = request.method
        # Use path template if available, otherwise use path
        endpoint = request.url.path

        # Increment in-progress counter
        http_requests_in_progress.labels(method=method, endpoint=endpoint).inc()

        # Measure request size
        request_size = int(request.headers.get("content-length", 0))
        if request_size > 0:
            http_request_size_bytes.labels(method=method, endpoint=endpoint).observe(request_size)

        # Start timer
        start_time = time.time()

        try:
            # Process request
            response = await call_next(request)

            # Measure duration
            duration = time.time() - start_time

            # Record metrics
            status_code = response.status_code
            http_requests_total.labels(
                method=method,
                endpoint=endpoint,
                status_code=status_code
            ).inc()

            http_request_duration_seconds.labels(
                method=method,
                endpoint=endpoint
            ).observe(duration)

            # Measure response size
            response_size = int(response.headers.get("content-length", 0))
            if response_size > 0:
                http_response_size_bytes.labels(method=method, endpoint=endpoint).observe(response_size)

            return response

        except Exception as e:
            # Record error
            duration = time.time() - start_time
            http_requests_total.labels(
                method=method,
                endpoint=endpoint,
                status_code=500
            ).inc()

            http_request_duration_seconds.labels(
                method=method,
                endpoint=endpoint
            ).observe(duration)

            # Re-raise
            raise

        finally:
            # Decrement in-progress counter
            http_requests_in_progress.labels(method=method, endpoint=endpoint).dec()


def collect_business_metrics(db_session):
    """
    Collect business metrics from database

    This function should be called periodically (e.g., every 60 seconds)
    by a background task or scheduled job.

    Args:
        db_session: SQLAlchemy database session
    """
    try:
        from app.models import Asset, ChangeRequest, ComplianceViolation, Domain

        # Asset metrics
        total_assets = db_session.query(Asset).count()
        compliant_assets = db_session.query(Asset).filter(Asset.naming_compliant == True).count()

        if total_assets > 0:
            compliance_rate = compliant_assets / total_assets
            assets_compliance_rate.labels(domain="all").set(compliance_rate)

        # Assets by environment and domain
        # (This would require joining with Domain table for actual domain names)

        # Assets by lifecycle stage
        from sqlalchemy import func
        lifecycle_counts = db_session.query(
            Asset.lifecycle_stage,
            func.count(Asset.asset_id)
        ).group_by(Asset.lifecycle_stage).all()

        for stage, count in lifecycle_counts:
            if stage:
                assets_by_lifecycle_stage.labels(lifecycle_stage=stage).set(count)

        # Change request metrics
        pending_changes = db_session.query(ChangeRequest).filter(
            ChangeRequest.status == "Pending"
        ).count()

        # Compliance violations
        open_violations = db_session.query(ComplianceViolation).filter(
            ComplianceViolation.status == "open"
        ).count()

        logger.debug(
            "business_metrics_collected",
            total_assets=total_assets,
            compliant_assets=compliant_assets,
            pending_changes=pending_changes,
            open_violations=open_violations
        )

    except Exception as e:
        logger.error("business_metrics_collection_failed", error=str(e))


def collect_database_metrics(db_engine):
    """
    Collect database metrics

    Args:
        db_engine: SQLAlchemy engine
    """
    try:
        pool = db_engine.pool

        # Connection pool metrics
        database_connection_pool_size.set(pool.size())
        database_connections_active.set(pool.checkedout())

    except Exception as e:
        logger.error("database_metrics_collection_failed", error=str(e))


def get_metrics_response() -> Response:
    """
    Generate Prometheus metrics response

    Returns:
        Response with Prometheus metrics in text format
    """
    metrics = generate_latest(REGISTRY)
    return Response(content=metrics, media_type=CONTENT_TYPE_LATEST)


# ==================== Utility Functions ====================

def increment_login_counter(success: bool):
    """Increment user login counter"""
    status = "success" if success else "failed"
    user_login_total.labels(status=status).inc()


def record_database_query(query_type: str, table: str, duration_seconds: float):
    """Record database query metrics"""
    database_queries_total.labels(query_type=query_type, table=table).inc()
    database_query_duration_seconds.labels(query_type=query_type, table=table).observe(duration_seconds)


def increment_change_request(change_type: str, status: str):
    """Increment change request counter"""
    change_requests_total.labels(type=change_type, status=status).inc()


def increment_compliance_violation(violation_type: str, severity: str):
    """Increment compliance violation counter"""
    compliance_violations_total.labels(violation_type=violation_type, severity=severity).inc()


def set_pending_change_requests(count: int, risk_level: str):
    """Set pending change requests gauge"""
    change_requests_pending.labels(risk_level=risk_level).set(count)


def set_open_violations(count: int, severity: str):
    """Set open violations gauge"""
    compliance_violations_open.labels(severity=severity).set(count)
