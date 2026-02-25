"""
Enterprise DaaS Governance Portal - Main Application
FastAPI backend with governance controls, lifecycle management, and compliance tracking
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base
from .api import assets, compliance, strategy, vendors, reports, auth, impact, lineage, schemas, quality, policies, sla, events, webhooks, api_keys, audit_logs, change_requests
from . import models, models_extended, models_advanced, models_integrations
from .middleware.security import (
    RateLimitMiddleware,
    SecurityHeadersMiddleware,
    CSRFProtectionMiddleware
)
import os

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

# Security Middleware (added in reverse order - last added executes first)
# CSRF Protection
app.add_middleware(CSRFProtectionMiddleware)

# Security Headers
app.add_middleware(SecurityHeadersMiddleware)

# Rate Limiting (optional - can be disabled via env var)
if os.getenv('RATE_LIMIT_ENABLED', 'True').lower() == 'true':
    app.add_middleware(
        RateLimitMiddleware,
        requests_per_minute=int(os.getenv('RATE_LIMIT_PER_MINUTE', 60))
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
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "governance-portal",
        "version": "1.0.0"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
