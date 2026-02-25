"""
Enterprise DaaS Governance Portal - Main Application
FastAPI backend with governance controls, lifecycle management, and compliance tracking
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base
from .api import assets, compliance, strategy, vendors, reports, auth, impact, lineage, schemas, quality, policies, sla, events, webhooks, api_keys, audit_logs, change_requests, tasks, notifications, comments, activity
from . import models, models_extended, models_advanced, models_integrations, models_collaboration, models_itsm
from .middleware.security import (
    RateLimitMiddleware,
    SecurityHeadersMiddleware,
    CSRFProtectionMiddleware
)
from .middleware.logging_middleware import (
    RequestLoggingMiddleware,
    PerformanceLoggingMiddleware
)
from .services.metrics import PrometheusMetricsMiddleware, get_metrics_response
from .logging_config import setup_logging, get_logger
import os

# Configure structured logging
setup_logging(
    log_level=os.getenv("LOG_LEVEL", "INFO"),
    enable_sentry=os.getenv("ENABLE_SENTRY", "false").lower() == "true",
    sentry_dsn=os.getenv("SENTRY_DSN"),
    environment=os.getenv("ENVIRONMENT", "development")
)

# Get logger
logger = get_logger(__name__)

# Create database tables
Base.metadata.create_all(bind=engine)

# Create FastAPI app
app = FastAPI(
    title="Enterprise DaaS Governance Portal",
    description="Enterprise-grade governance platform for Data-as-a-Service operations with strategic DaaS leadership capabilities",
    version="2.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Configure CORS
allowed_origins = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:3000,http://localhost:3001,http://localhost:5173"
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware Stack (added in reverse order - last added executes first)
# Order: Logging → Performance → Security → CSRF → Rate Limiting

# Rate Limiting (outermost - first to check)
if os.getenv('RATE_LIMIT_ENABLED', 'True').lower() == 'true':
    app.add_middleware(
        RateLimitMiddleware,
        requests_per_minute=int(os.getenv('RATE_LIMIT_PER_MINUTE', 60))
    )

# CSRF Protection
app.add_middleware(CSRFProtectionMiddleware)

# Security Headers
app.add_middleware(SecurityHeadersMiddleware)

# Performance Logging (track slow endpoints)
app.add_middleware(
    PerformanceLoggingMiddleware,
    slow_request_threshold_ms=float(os.getenv('SLOW_REQUEST_THRESHOLD_MS', 1000))
)

# Prometheus Metrics (collect metrics for all requests)
app.add_middleware(PrometheusMetricsMiddleware)

# Request Logging (innermost - logs all requests)
app.add_middleware(RequestLoggingMiddleware)

logger.info(
    "application_startup",
    version="2.0.0",
    environment=os.getenv("ENVIRONMENT", "development"),
    cors_origins=allowed_origins,
    rate_limiting_enabled=os.getenv('RATE_LIMIT_ENABLED', 'True').lower() == 'true'
)

# Include routers
app.include_router(auth.router)  # Auth must be first for proper routing
app.include_router(assets.router)
app.include_router(compliance.router)
app.include_router(strategy.router)
app.include_router(vendors.router)
app.include_router(reports.router)
app.include_router(audit_logs.router)  # Audit logs for system-wide activity tracking
app.include_router(change_requests.router)  # ITIL-style change management
app.include_router(impact.router)  # Impact analysis and dependency tracking
app.include_router(lineage.router)  # Data lineage tracking and visualization
app.include_router(schemas.router)  # Schema registry with versioning and compatibility
app.include_router(quality.router)  # Data quality validation and monitoring
app.include_router(policies.router)  # CI/CD policy enforcement and governance automation
app.include_router(sla.router)  # Real-time SLA monitoring and metric collection
app.include_router(events.router)  # Event version control and catalog management
app.include_router(webhooks.router)  # Phase 3: Webhook management for event notifications
app.include_router(api_keys.router)  # Phase 3: API key management for programmatic access
app.include_router(tasks.router)  # Gap Feature: Task assignment and management
app.include_router(notifications.router)  # Gap Feature: In-app notifications
app.include_router(comments.router)  # Gap Feature: Comment system with threading
app.include_router(activity.router)  # Gap Feature: Activity feed and audit trail


@app.get("/")
def root():
    """Root endpoint"""
    return {
        "message": "Enterprise DaaS Governance Portal API",
        "version": "1.0.0",
        "documentation": "/api/docs"
    }


@app.get("/api/v1/health")
def health_check():
    """
    Comprehensive health check endpoint

    Returns detailed system health including:
    - Database connectivity
    - System resources (CPU, memory, disk)
    - External dependencies (Redis, Sentry)
    - Application uptime
    """
    from app.services.health_check import health_check_service
    return health_check_service.get_comprehensive_health()


@app.get("/api/v1/health/ready")
def readiness_check():
    """
    Readiness probe for Kubernetes

    Checks if application is ready to serve traffic.
    Returns 200 if ready, 503 if not ready.
    """
    from app.services.health_check import health_check_service
    from fastapi import Response

    result = health_check_service.get_readiness()

    if result["ready"]:
        return result
    else:
        return Response(content=str(result), status_code=503)


@app.get("/api/v1/health/live")
def liveness_check():
    """
    Liveness probe for Kubernetes

    Checks if application is alive.
    Returns 200 if alive.
    """
    from app.services.health_check import health_check_service
    return health_check_service.get_liveness()


@app.get("/metrics")
def metrics():
    """
    Prometheus metrics endpoint

    Exposes application, database, and business metrics in Prometheus format.
    This endpoint is typically scraped by Prometheus server.

    Returns:
        Response with metrics in Prometheus text format
    """
    return get_metrics_response()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
