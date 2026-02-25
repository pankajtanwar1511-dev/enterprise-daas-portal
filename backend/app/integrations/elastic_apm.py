"""
Elastic APM Integration

This module provides Elastic APM instrumentation for the Enterprise DaaS Governance Portal.

Elastic APM is an open-source application performance monitoring system that integrates
with the Elastic Stack (Elasticsearch, Logstash, Kibana).

Usage:
    1. Install: pip install elastic-apm[fastapi]
    2. Set environment variables in .env:
       ELASTIC_APM_SERVICE_NAME=enterprise-daas-portal
       ELASTIC_APM_SECRET_TOKEN=your_secret_token
       ELASTIC_APM_SERVER_URL=http://localhost:8200
       ELASTIC_APM_ENVIRONMENT=production

    3. Integrate in your application:
       from app.integrations.elastic_apm import setup_elastic_apm
       apm = setup_elastic_apm(app)
"""

import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)


def setup_elastic_apm(app) -> Optional[object]:
    """
    Configure Elastic APM for FastAPI application

    This function:
    - Creates an Elastic APM client
    - Adds middleware to trace HTTP requests
    - Configures automatic instrumentation

    Args:
        app: FastAPI application instance

    Returns:
        Client object if successful, None otherwise

    Environment Variables:
        ELASTIC_APM_SERVICE_NAME: Service name (default: enterprise-daas-portal)
        ELASTIC_APM_SECRET_TOKEN: Authentication token for APM server
        ELASTIC_APM_SERVER_URL: APM server URL (default: http://localhost:8200)
        ELASTIC_APM_ENVIRONMENT: Environment name (e.g., production, staging)
        ELASTIC_APM_TRANSACTION_SAMPLE_RATE: Sampling rate 0.0-1.0 (default: 1.0)
        ELASTIC_APM_CAPTURE_BODY: Capture request/response bodies (default: all)
        ELASTIC_APM_CAPTURE_HEADERS: Capture HTTP headers (default: true)

    Example:
        >>> from fastapi import FastAPI
        >>> from app.integrations.elastic_apm import setup_elastic_apm
        >>>
        >>> app = FastAPI()
        >>> apm = setup_elastic_apm(app)
    """
    # Check if Elastic APM is configured
    server_url = os.getenv('ELASTIC_APM_SERVER_URL')
    if not server_url:
        logger.info("Elastic APM is disabled (ELASTIC_APM_SERVER_URL not set)")
        return None

    try:
        from elasticapm.contrib.starlette import make_apm_client, ElasticAPM

        # APM configuration
        apm_config = {
            'SERVICE_NAME': os.getenv('ELASTIC_APM_SERVICE_NAME', 'enterprise-daas-portal'),
            'SECRET_TOKEN': os.getenv('ELASTIC_APM_SECRET_TOKEN'),
            'SERVER_URL': server_url,
            'ENVIRONMENT': os.getenv('ELASTIC_APM_ENVIRONMENT', 'production'),
            'TRANSACTION_SAMPLE_RATE': float(os.getenv('ELASTIC_APM_TRANSACTION_SAMPLE_RATE', '1.0')),
            'CENTRAL_CONFIG': False,
            'CAPTURE_BODY': os.getenv('ELASTIC_APM_CAPTURE_BODY', 'all'),
            'CAPTURE_HEADERS': os.getenv('ELASTIC_APM_CAPTURE_HEADERS', 'true').lower() == 'true',
            'CAPTURE_BODY_MAX_SIZE': 10000,  # 10KB max for body capture
            'TRANSACTION_MAX_SPANS': 500,
            'STACK_TRACE_LIMIT': 50,
        }

        # Create APM client
        apm = make_apm_client(apm_config)

        # Add middleware
        app.add_middleware(ElasticAPM, client=apm)

        logger.info(
            f"Elastic APM configured successfully",
            extra={
                'service': apm_config['SERVICE_NAME'],
                'environment': apm_config['ENVIRONMENT'],
                'server_url': server_url,
                'sample_rate': apm_config['TRANSACTION_SAMPLE_RATE']
            }
        )

        return apm

    except ImportError:
        logger.warning(
            "Elastic APM not available - elastic-apm package not installed. "
            "Install with: pip install elastic-apm[fastapi]"
        )
        return None

    except Exception as e:
        logger.error(f"Failed to configure Elastic APM: {e}", exc_info=True)
        return None


def trace_function(name: Optional[str] = None, span_type: str = "app"):
    """
    Decorator to trace a function with Elastic APM

    Args:
        name: Span name (default: function name)
        span_type: Span type (e.g., app, db, cache, external)

    Example:
        >>> @trace_function(name="fetch_assets", span_type="db")
        >>> def get_assets_from_db(db_session):
        >>>     return db_session.query(Asset).all()
    """
    def decorator(func):
        try:
            from elasticapm import capture_span

            span_name = name or func.__name__

            @capture_span(span_name, span_type=span_type)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)

            return wrapper

        except ImportError:
            # If elastic-apm not installed, return original function
            return func

    return decorator


def add_custom_context(**context):
    """
    Add custom context to the current Elastic APM transaction

    Args:
        **context: Key-value pairs to add as context

    Example:
        >>> add_custom_context(user_id=123, tenant='acme-corp')
    """
    try:
        import elasticapm

        client = elasticapm.get_client()
        if client:
            for key, value in context.items():
                elasticapm.set_custom_context({key: value})

    except ImportError:
        pass  # Elastic APM not installed
    except Exception as e:
        logger.debug(f"Failed to add custom context: {e}")


def add_tags(**tags):
    """
    Add tags to the current Elastic APM transaction

    Args:
        **tags: Key-value pairs to add as tags

    Example:
        >>> add_tags(domain='HR', operation='create')
    """
    try:
        import elasticapm

        for key, value in tags.items():
            elasticapm.tag(**{key: value})

    except ImportError:
        pass  # Elastic APM not installed
    except Exception as e:
        logger.debug(f"Failed to add tags: {e}")


def add_labels(**labels):
    """
    Add labels to the current Elastic APM transaction

    Labels are indexed and can be used for filtering in Kibana.

    Args:
        **labels: Key-value pairs to add as labels

    Example:
        >>> add_labels(status='success', records_processed=100)
    """
    try:
        import elasticapm

        for key, value in labels.items():
            elasticapm.label(**{key: value})

    except ImportError:
        pass  # Elastic APM not installed
    except Exception as e:
        logger.debug(f"Failed to add labels: {e}")


def capture_exception(exception: Exception = None):
    """
    Manually capture an exception in Elastic APM

    Args:
        exception: Exception to capture (if None, captures current exception)

    Example:
        >>> try:
        >>>     risky_operation()
        >>> except Exception as e:
        >>>     capture_exception(e)
        >>>     handle_error()
    """
    try:
        import elasticapm

        client = elasticapm.get_client()
        if client:
            if exception:
                client.capture_exception(exc_info=(type(exception), exception, exception.__traceback__))
            else:
                client.capture_exception()

    except ImportError:
        pass  # Elastic APM not installed
    except Exception as e:
        logger.debug(f"Failed to capture exception: {e}")


def capture_message(message: str, level: str = "info", **context):
    """
    Capture a message in Elastic APM

    Args:
        message: Message text
        level: Log level (debug, info, warning, error, critical)
        **context: Additional context

    Example:
        >>> capture_message("Asset created successfully", level="info", asset_id=123)
    """
    try:
        import elasticapm

        client = elasticapm.get_client()
        if client:
            client.capture_message(message, level=level, custom=context)

    except ImportError:
        pass  # Elastic APM not installed
    except Exception as e:
        logger.debug(f"Failed to capture message: {e}")


def begin_transaction(name: str, transaction_type: str = "request"):
    """
    Manually begin a new transaction

    Args:
        name: Transaction name
        transaction_type: Transaction type (request, task, etc.)

    Returns:
        Transaction object

    Example:
        >>> transaction = begin_transaction("process_batch", "task")
        >>> try:
        >>>     process_data()
        >>> finally:
        >>>     end_transaction()
    """
    try:
        import elasticapm

        client = elasticapm.get_client()
        if client:
            return client.begin_transaction(transaction_type, name=name)

    except ImportError:
        pass  # Elastic APM not installed
    except Exception as e:
        logger.debug(f"Failed to begin transaction: {e}")

    return None


def end_transaction(name: Optional[str] = None, result: Optional[str] = None):
    """
    End the current transaction

    Args:
        name: Transaction name
        result: Transaction result (success, error, etc.)

    Example:
        >>> end_transaction(name="process_batch", result="success")
    """
    try:
        import elasticapm

        client = elasticapm.get_client()
        if client:
            client.end_transaction(name=name, result=result)

    except ImportError:
        pass  # Elastic APM not installed
    except Exception as e:
        logger.debug(f"Failed to end transaction: {e}")


# Usage examples
if __name__ == "__main__":
    """
    Example usage of Elastic APM integration
    """

    from fastapi import FastAPI

    # Create FastAPI app
    app = FastAPI(title="Enterprise DaaS Governance Portal")

    # Setup Elastic APM
    apm = setup_elastic_apm(app)
    if apm:
        print("✓ Elastic APM configured successfully")
    else:
        print("✗ Elastic APM not configured")

    # Example: Custom traced function
    @trace_function(name="database.fetch_assets", span_type="db")
    def fetch_assets():
        """Example function with custom tracing"""
        add_tags(query_type='SELECT', table='assets')
        add_labels(records=42)
        return []

    # Example: Capture custom message
    capture_message("System initialized", level="info", version="2.0.0")

    # Example: Manual transaction
    transaction = begin_transaction("batch_process", "task")
    try:
        # Your processing logic
        add_custom_context(batch_size=100)
        end_transaction(result="success")
    except Exception as e:
        capture_exception(e)
        end_transaction(result="error")
