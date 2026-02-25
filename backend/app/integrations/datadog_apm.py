"""
DataDog APM Integration

This module provides DataDog APM instrumentation for the Enterprise DaaS Governance Portal.

Usage:
    1. Install: pip install ddtrace
    2. Set environment variables in .env:
       DD_SERVICE=enterprise-daas-portal
       DD_ENV=production
       DD_VERSION=2.0.0
       DD_AGENT_HOST=localhost
       DD_AGENT_PORT=8126
       DD_TRACE_ENABLED=true

    3. Option A - Auto-instrumentation (Recommended):
       ddtrace-run uvicorn app.main:app --host 0.0.0.0 --port 8000

    4. Option B - Manual integration:
       from app.integrations.datadog_apm import setup_datadog_apm
       setup_datadog_apm(app)
"""

import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)


def setup_datadog_apm(app) -> bool:
    """
    Configure DataDog APM for FastAPI application

    This function:
    - Enables auto-instrumentation for common libraries (requests, SQLAlchemy, etc.)
    - Configures the DataDog tracer
    - Adds FastAPI-specific tracing

    Args:
        app: FastAPI application instance

    Returns:
        bool: True if DataDog was successfully configured, False otherwise

    Environment Variables:
        DD_SERVICE: Service name (default: enterprise-daas-portal)
        DD_ENV: Environment name (e.g., production, staging)
        DD_VERSION: Application version
        DD_AGENT_HOST: DataDog agent hostname (default: localhost)
        DD_AGENT_PORT: DataDog agent port (default: 8126)
        DD_TRACE_ENABLED: Enable/disable tracing (default: false)
        DD_LOGS_INJECTION: Inject trace IDs into logs (default: true)
        DD_PROFILING_ENABLED: Enable profiling (default: false)
        DD_RUNTIME_METRICS_ENABLED: Enable runtime metrics (default: true)

    Example:
        >>> from fastapi import FastAPI
        >>> from app.integrations.datadog_apm import setup_datadog_apm
        >>>
        >>> app = FastAPI()
        >>> setup_datadog_apm(app)
    """
    # Check if DataDog tracing is enabled
    if not os.getenv('DD_TRACE_ENABLED', 'false').lower() == 'true':
        logger.info("DataDog APM is disabled (DD_TRACE_ENABLED=false)")
        return False

    try:
        from ddtrace import tracer, patch_all
        from ddtrace.contrib.fastapi import get_traced_app

        # Auto-instrument common libraries
        patch_all()
        logger.info("DataDog: Patched common libraries for auto-instrumentation")

        # Configure tracer
        tracer.configure(
            hostname=os.getenv('DD_AGENT_HOST', 'localhost'),
            port=int(os.getenv('DD_AGENT_PORT', 8126)),
            enabled=True,
        )

        # Get service configuration
        service_name = os.getenv('DD_SERVICE', 'enterprise-daas-portal')
        environment = os.getenv('DD_ENV', 'development')
        version = os.getenv('DD_VERSION', '2.0.0')

        # Enable FastAPI tracing
        get_traced_app(
            app,
            service_name=service_name,
            distributed_tracing=True
        )

        logger.info(
            f"DataDog APM configured successfully",
            extra={
                'service': service_name,
                'env': environment,
                'version': version,
                'agent': f"{os.getenv('DD_AGENT_HOST', 'localhost')}:{os.getenv('DD_AGENT_PORT', 8126)}"
            }
        )

        return True

    except ImportError:
        logger.warning(
            "DataDog APM not available - ddtrace package not installed. "
            "Install with: pip install ddtrace"
        )
        return False

    except Exception as e:
        logger.error(f"Failed to configure DataDog APM: {e}", exc_info=True)
        return False


def trace_function(name: Optional[str] = None, service: Optional[str] = None, resource: Optional[str] = None):
    """
    Decorator to trace a function with DataDog APM

    Args:
        name: Span operation name (default: function name)
        service: Service name for the span
        resource: Resource name for the span

    Example:
        >>> @trace_function(name="fetch_assets", service="database")
        >>> def get_assets_from_db(db_session):
        >>>     return db_session.query(Asset).all()
    """
    def decorator(func):
        try:
            from ddtrace import tracer

            span_name = name or func.__name__
            span_service = service or os.getenv('DD_SERVICE', 'enterprise-daas-portal')
            span_resource = resource or func.__name__

            def wrapper(*args, **kwargs):
                with tracer.trace(span_name, service=span_service, resource=span_resource) as span:
                    # Add custom tags
                    span.set_tag('function', func.__name__)
                    span.set_tag('module', func.__module__)

                    try:
                        result = func(*args, **kwargs)
                        span.set_tag('status', 'success')
                        return result
                    except Exception as e:
                        span.set_tag('status', 'error')
                        span.set_tag('error.type', type(e).__name__)
                        span.set_tag('error.message', str(e))
                        raise

            return wrapper

        except ImportError:
            # If ddtrace not installed, return original function
            return func

    return decorator


def add_custom_tags(**tags):
    """
    Add custom tags to the current DataDog span

    Args:
        **tags: Key-value pairs to add as tags

    Example:
        >>> add_custom_tags(user_id=123, tenant='acme-corp')
    """
    try:
        from ddtrace import tracer

        span = tracer.current_span()
        if span:
            for key, value in tags.items():
                span.set_tag(key, value)

    except ImportError:
        pass  # DataDog not installed
    except Exception as e:
        logger.debug(f"Failed to add custom tags: {e}")


def record_custom_metric(name: str, value: float, tags: Optional[dict] = None):
    """
    Record a custom metric with DataDog

    Args:
        name: Metric name
        value: Metric value
        tags: Optional tags dictionary

    Example:
        >>> record_custom_metric('assets.created', 1, {'domain': 'HR'})
    """
    try:
        from ddtrace import tracer

        span = tracer.current_span()
        if span:
            span.set_metric(name, value)

            if tags:
                for key, val in tags.items():
                    span.set_tag(key, val)

    except ImportError:
        pass  # DataDog not installed
    except Exception as e:
        logger.debug(f"Failed to record custom metric: {e}")


# Usage examples
if __name__ == "__main__":
    """
    Example usage of DataDog APM integration
    """

    from fastapi import FastAPI

    # Create FastAPI app
    app = FastAPI(title="Enterprise DaaS Governance Portal")

    # Setup DataDog APM
    if setup_datadog_apm(app):
        print("✓ DataDog APM configured successfully")
    else:
        print("✗ DataDog APM not configured")

    # Example: Custom traced function
    @trace_function(name="database.fetch_assets", service="postgres")
    def fetch_assets():
        """Example function with custom tracing"""
        # Your database logic
        add_custom_tags(query_type='SELECT', table='assets')
        return []

    # Example: Record custom metric
    record_custom_metric('custom.assets.count', 42, {'domain': 'HR'})
