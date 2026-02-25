# Application Performance Monitoring (APM) Integration Guide

## Overview

This guide demonstrates how to integrate popular Application Performance Monitoring (APM) solutions with the Enterprise DaaS Governance Portal. APM tools provide:

- **Distributed Tracing**: Track requests across microservices
- **Performance Profiling**: Identify slow database queries and bottlenecks
- **Error Tracking**: Capture and analyze exceptions
- **Real-time Metrics**: Monitor application health and performance
- **User Experience Monitoring**: Track frontend performance

## Supported APM Solutions

1. [DataDog APM](#datadog-apm) - Comprehensive APM with infrastructure monitoring
2. [New Relic](#new-relic) - Full-stack observability platform
3. [AWS X-Ray](#aws-x-ray) - Distributed tracing for AWS applications
4. [Elastic APM](#elastic-apm) - Open-source APM with Elasticsearch
5. [Dynatrace](#dynatrace) - AI-powered full-stack monitoring

---

## DataDog APM

### Installation

```bash
# Install DataDog APM client
pip install ddtrace==2.3.0

# Add to requirements.txt
echo "ddtrace==2.3.0" >> backend/requirements.txt
```

### Configuration

**Environment Variables (.env.production):**

```bash
# DataDog Configuration
DD_SERVICE=enterprise-daas-portal
DD_ENV=production
DD_VERSION=2.0.0
DD_AGENT_HOST=localhost
DD_AGENT_PORT=8126
DD_TRACE_ENABLED=true
DD_LOGS_INJECTION=true
DD_PROFILING_ENABLED=true
DD_RUNTIME_METRICS_ENABLED=true

# DataDog API Key (for direct API submission)
DD_API_KEY=your_datadog_api_key
```

### Integration

**Method 1: Auto-instrumentation (Recommended)**

```bash
# Run with ddtrace-run wrapper
ddtrace-run uvicorn app.main:app --host 0.0.0.0 --port 8000

# In systemd service file:
ExecStart=/path/to/venv/bin/ddtrace-run uvicorn app.main:app --host 0.0.0.0 --port 8000
```

**Method 2: Manual instrumentation**

Create `backend/app/integrations/datadog_apm.py`:

```python
"""
DataDog APM Integration
"""
import os
from ddtrace import tracer, patch_all
from ddtrace.contrib.fastapi import get_traced_app

def setup_datadog_apm(app):
    """
    Configure DataDog APM for FastAPI application

    Args:
        app: FastAPI application instance
    """
    # Enable auto-instrumentation for common libraries
    patch_all()

    # Configure tracer
    tracer.configure(
        hostname=os.getenv('DD_AGENT_HOST', 'localhost'),
        port=int(os.getenv('DD_AGENT_PORT', 8126)),
        enabled=os.getenv('DD_TRACE_ENABLED', 'false').lower() == 'true',
    )

    # Trace FastAPI application
    traced_app = get_traced_app(
        app,
        service_name=os.getenv('DD_SERVICE', 'enterprise-daas-portal'),
        distributed_tracing=True
    )

    return traced_app
```

Update `backend/app/main.py`:

```python
from app.integrations.datadog_apm import setup_datadog_apm
import os

# Create FastAPI app
app = FastAPI(...)

# Enable DataDog APM if configured
if os.getenv('DD_TRACE_ENABLED', 'false').lower() == 'true':
    app = setup_datadog_apm(app)
```

### Custom Instrumentation

```python
from ddtrace import tracer

@tracer.wrap(service="database", resource="fetch_assets")
def fetch_assets_from_db(db_session):
    """Custom traced function"""
    with tracer.trace("database.query", service="postgres") as span:
        span.set_tag("query.type", "SELECT")
        span.set_tag("query.table", "assets")

        assets = db_session.query(Asset).all()

        span.set_metric("query.rows", len(assets))
        return assets
```

### DataDog Dashboard

Access your traces at: `https://app.datadoghq.com/apm/traces`

**Key Metrics to Monitor:**
- `trace.fastapi.request` - Request traces
- `trace.fastapi.request.duration` - Request latency
- `trace.sqlalchemy.query` - Database queries
- `runtime.python.cpu.time` - CPU usage
- `runtime.python.mem.rss` - Memory usage

---

## New Relic

### Installation

```bash
# Install New Relic APM agent
pip install newrelic==9.5.0

# Add to requirements.txt
echo "newrelic==9.5.0" >> backend/requirements.txt
```

### Configuration

**Generate configuration file:**

```bash
# Generate newrelic.ini
newrelic-admin generate-config YOUR_LICENSE_KEY newrelic.ini
```

**Edit `newrelic.ini`:**

```ini
[newrelic]
license_key = YOUR_LICENSE_KEY
app_name = Enterprise DaaS Governance Portal

# Logging
log_file = /var/log/newrelic/python-agent.log
log_level = info

# Distributed Tracing
distributed_tracing.enabled = true

# Transaction Tracer
transaction_tracer.enabled = true
transaction_tracer.transaction_threshold = apdex_f
transaction_tracer.record_sql = obfuscated

# Slow SQL
transaction_tracer.explain_enabled = true
transaction_tracer.explain_threshold = 0.5

# Error Collector
error_collector.enabled = true
error_collector.ignore_status_codes = 404
```

### Integration

**Method 1: Using newrelic-admin wrapper**

```bash
# Run with newrelic-admin
NEW_RELIC_CONFIG_FILE=newrelic.ini newrelic-admin run-program uvicorn app.main:app --host 0.0.0.0 --port 8000

# In systemd service:
Environment="NEW_RELIC_CONFIG_FILE=/path/to/newrelic.ini"
ExecStart=/path/to/venv/bin/newrelic-admin run-program uvicorn app.main:app
```

**Method 2: Manual initialization**

Create `backend/app/integrations/newrelic_apm.py`:

```python
"""
New Relic APM Integration
"""
import os
import newrelic.agent

def setup_newrelic_apm():
    """Initialize New Relic APM"""
    config_file = os.getenv('NEW_RELIC_CONFIG_FILE', 'newrelic.ini')

    if os.path.exists(config_file):
        newrelic.agent.initialize(config_file)
        return True
    return False
```

Update `backend/app/main.py`:

```python
from app.integrations.newrelic_apm import setup_newrelic_apm

# Initialize New Relic before creating FastAPI app
setup_newrelic_apm()

app = FastAPI(...)
```

### Custom Instrumentation

```python
import newrelic.agent

@newrelic.agent.background_task()
def process_compliance_check():
    """Background task with custom instrumentation"""
    with newrelic.agent.FunctionTrace('compliance_validation'):
        # Your compliance logic
        pass

# Add custom attributes to transactions
newrelic.agent.add_custom_attribute('user_id', user.id)
newrelic.agent.add_custom_attribute('tenant', user.organization)

# Record custom metrics
newrelic.agent.record_custom_metric('Custom/Assets/Created', 1)
```

### New Relic Dashboard

Access your application at: `https://one.newrelic.com/`

---

## AWS X-Ray

### Installation

```bash
# Install AWS X-Ray SDK
pip install aws-xray-sdk==2.12.0

# Add to requirements.txt
echo "aws-xray-sdk==2.12.0" >> backend/requirements.txt
```

### Configuration

**Environment Variables:**

```bash
AWS_XRAY_TRACING_NAME=enterprise-daas-portal
AWS_XRAY_DAEMON_ADDRESS=127.0.0.1:2000
AWS_XRAY_CONTEXT_MISSING=LOG_ERROR
```

### Integration

Create `backend/app/integrations/xray_apm.py`:

```python
"""
AWS X-Ray APM Integration
"""
import os
from aws_xray_sdk.core import xray_recorder, patch_all
from aws_xray_sdk.ext.flask.middleware import XRayMiddleware

def setup_xray_apm(app):
    """
    Configure AWS X-Ray for FastAPI application

    Args:
        app: FastAPI application instance
    """
    # Configure X-Ray recorder
    xray_recorder.configure(
        service=os.getenv('AWS_XRAY_TRACING_NAME', 'enterprise-daas-portal'),
        daemon_address=os.getenv('AWS_XRAY_DAEMON_ADDRESS', '127.0.0.1:2000'),
        context_missing=os.getenv('AWS_XRAY_CONTEXT_MISSING', 'LOG_ERROR')
    )

    # Auto-instrument common libraries
    patch_all()

    return app
```

**Middleware Implementation:**

```python
from aws_xray_sdk.core import xray_recorder
from starlette.middleware.base import BaseHTTPMiddleware

class XRayMiddleware(BaseHTTPMiddleware):
    """AWS X-Ray middleware for FastAPI"""

    async def dispatch(self, request, call_next):
        # Start X-Ray segment
        segment = xray_recorder.begin_segment('fastapi-request')

        try:
            # Add request metadata
            segment.put_http_meta('url', str(request.url))
            segment.put_http_meta('method', request.method)
            segment.put_http_meta('user_agent', request.headers.get('user-agent'))

            # Process request
            response = await call_next(request)

            # Add response metadata
            segment.put_http_meta('status', response.status_code)

            return response

        except Exception as e:
            # Record exception
            segment.put_annotation('error', True)
            segment.put_metadata('exception', str(e))
            raise

        finally:
            xray_recorder.end_segment()

# Add to main.py
app.add_middleware(XRayMiddleware)
```

### Custom Subsegments

```python
from aws_xray_sdk.core import xray_recorder

@xray_recorder.capture('fetch_assets')
def fetch_assets(db_session):
    """Automatically traced function"""
    return db_session.query(Asset).all()

# Manual subsegment
def process_compliance():
    subsegment = xray_recorder.begin_subsegment('compliance_check')
    try:
        # Your logic
        subsegment.put_annotation('compliant', True)
        subsegment.put_metadata('rules_checked', ['naming', 'lifecycle'])
    finally:
        xray_recorder.end_subsegment()
```

### AWS X-Ray Console

Access traces at: `https://console.aws.amazon.com/xray/`

---

## Elastic APM

### Installation

```bash
# Install Elastic APM agent
pip install elastic-apm[fastapi]==6.19.0

# Add to requirements.txt
echo "elastic-apm[fastapi]==6.19.0" >> backend/requirements.txt
```

### Configuration

**Environment Variables:**

```bash
ELASTIC_APM_SERVICE_NAME=enterprise-daas-portal
ELASTIC_APM_SECRET_TOKEN=your_secret_token
ELASTIC_APM_SERVER_URL=http://localhost:8200
ELASTIC_APM_ENVIRONMENT=production
ELASTIC_APM_TRANSACTION_SAMPLE_RATE=1.0
```

### Integration

Create `backend/app/integrations/elastic_apm.py`:

```python
"""
Elastic APM Integration
"""
import os
from elasticapm import Client
from elasticapm.contrib.starlette import make_apm_client, ElasticAPM

def setup_elastic_apm(app):
    """
    Configure Elastic APM for FastAPI application

    Args:
        app: FastAPI application instance
    """
    apm_config = {
        'SERVICE_NAME': os.getenv('ELASTIC_APM_SERVICE_NAME', 'enterprise-daas-portal'),
        'SECRET_TOKEN': os.getenv('ELASTIC_APM_SECRET_TOKEN'),
        'SERVER_URL': os.getenv('ELASTIC_APM_SERVER_URL', 'http://localhost:8200'),
        'ENVIRONMENT': os.getenv('ELASTIC_APM_ENVIRONMENT', 'production'),
        'TRANSACTION_SAMPLE_RATE': float(os.getenv('ELASTIC_APM_TRANSACTION_SAMPLE_RATE', '1.0')),
        'CENTRAL_CONFIG': False,
        'CAPTURE_BODY': 'all',
        'CAPTURE_HEADERS': True,
    }

    # Create APM client
    apm = make_apm_client(apm_config)

    # Add middleware
    app.add_middleware(ElasticAPM, client=apm)

    return apm
```

Update `backend/app/main.py`:

```python
from app.integrations.elastic_apm import setup_elastic_apm
import os

# Create FastAPI app
app = FastAPI(...)

# Enable Elastic APM if configured
if os.getenv('ELASTIC_APM_SERVER_URL'):
    apm = setup_elastic_apm(app)
```

### Custom Spans

```python
from elasticapm import capture_span

@capture_span('database.query')
def fetch_assets(db_session):
    """Automatically traced function"""
    return db_session.query(Asset).all()

# Manual span
import elasticapm

def process_data():
    client = elasticapm.get_client()

    with elasticapm.capture_span('data_processing'):
        # Your processing logic
        elasticapm.tag(operation='transform')
        elasticapm.label(records=100)
```

### Elastic APM Dashboard

Access APM at: `http://localhost:5601/app/apm` (Kibana)

---

## Dynatrace

### Installation

```bash
# Install Dynatrace OneAgent
# Download from Dynatrace portal and install on host

# Python auto-instrumentation
pip install oneagent-sdk==1.5.0

# Add to requirements.txt
echo "oneagent-sdk==1.5.0" >> backend/requirements.txt
```

### Configuration

**Environment Variables:**

```bash
DT_TENANT=your_tenant_id
DT_API_TOKEN=your_api_token
DT_CONNECTION_POINT=https://your_tenant.live.dynatrace.com/communication
```

### Integration

The Dynatrace OneAgent automatically instruments Python applications. No code changes required for basic monitoring.

For custom instrumentation:

```python
import oneagent

def setup_dynatrace():
    """Initialize Dynatrace SDK"""
    sdk = oneagent.get_sdk()
    sdk.initialize()
    return sdk

# Custom tracing
sdk = setup_dynatrace()

def fetch_assets():
    with sdk.trace_incoming_remote_call('fetch_assets', 'HTTP', 'http://localhost/assets'):
        # Your logic
        pass
```

---

## Comparison Matrix

| Feature | DataDog | New Relic | AWS X-Ray | Elastic APM | Dynatrace |
|---------|---------|-----------|-----------|-------------|-----------|
| **Distributed Tracing** | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Auto-instrumentation** | ✅ | ✅ | ⚠️ Partial | ✅ | ✅ |
| **Database Profiling** | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Infrastructure Monitoring** | ✅ | ✅ | ❌ | ⚠️ Via Beats | ✅ |
| **Log Management** | ✅ | ✅ | ⚠️ Via CloudWatch | ✅ | ✅ |
| **Real User Monitoring** | ✅ | ✅ | ❌ | ✅ | ✅ |
| **Custom Metrics** | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Alerting** | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Open Source** | ❌ | ❌ | ❌ | ✅ | ❌ |
| **Free Tier** | ✅ | ✅ | ✅ | ✅ (self-hosted) | ✅ |
| **Best For** | All-in-one | Enterprise | AWS-native | Open-source | AI-powered |

---

## Recommendations

### Development Environment
- **Elastic APM** - Free, self-hosted, integrates with local ELK stack
- Use Prometheus + Grafana for metrics visualization

### Staging Environment
- Enable APM with sampling rate of 0.5 (50% of transactions)
- Use DataDog or New Relic free tier

### Production Environment
- **DataDog APM** (Recommended) - Best balance of features and cost
- **AWS X-Ray** - If running on AWS infrastructure
- **Dynatrace** - For large enterprises requiring AI-powered monitoring

### Cost-Effective Setup
1. Prometheus for metrics (free, self-hosted)
2. Elastic APM for tracing (free, self-hosted)
3. Grafana for visualization (free, self-hosted)
4. Sentry for error tracking (already integrated)

---

## Testing APM Integration

### 1. Generate Test Traffic

```bash
# Load testing with hey
hey -n 1000 -c 10 http://localhost:8000/api/v1/assets

# Stress test with locust
pip install locust
locust -f tests/load/locustfile.py --host=http://localhost:8000
```

### 2. Verify Traces

Check that traces appear in your APM dashboard:
- HTTP requests are tracked
- Database queries are visible
- Errors are captured
- Custom spans appear

### 3. Performance Baseline

Establish performance baselines:
- P50 latency: < 100ms
- P95 latency: < 500ms
- P99 latency: < 1000ms
- Error rate: < 0.1%

---

## Best Practices

### 1. Sampling Strategy

```python
# Production: Sample 10% of successful requests, 100% of errors
TRANSACTION_SAMPLE_RATE = 0.1  # 10%
ERROR_SAMPLE_RATE = 1.0  # 100%
```

### 2. Custom Tags

Always add relevant business context:

```python
# Add user context
span.set_tag('user.id', user.id)
span.set_tag('user.role', user.role)

# Add business context
span.set_tag('tenant.id', tenant.id)
span.set_tag('asset.type', asset_type)
```

### 3. Sensitive Data

Never log sensitive data in traces:

```python
# ❌ Bad
span.set_tag('password', password)
span.set_tag('api_key', api_key)

# ✅ Good
span.set_tag('password', '***REDACTED***')
span.set_tag('api_key_length', len(api_key))
```

### 4. Performance Impact

- APM adds 1-5% overhead - acceptable for production
- Use sampling to reduce overhead
- Disable in high-throughput scenarios if needed

---

## Troubleshooting

### Common Issues

**1. No traces appearing**
- Check agent connectivity: `curl http://localhost:8126/info` (DataDog)
- Verify API keys/tokens
- Check firewall rules

**2. High overhead**
- Reduce sampling rate
- Disable profiling in production
- Check for instrumentation conflicts

**3. Missing database queries**
- Verify SQLAlchemy instrumentation is enabled
- Check database driver compatibility
- Review span filtering configuration

### Debug Mode

Enable debug logging:

```python
# DataDog
import ddtrace
ddtrace.tracer.log.setLevel('DEBUG')

# New Relic
# In newrelic.ini:
log_level = debug

# Elastic APM
ELASTIC_APM_DEBUG = true
```

---

## Next Steps

1. Choose an APM solution based on your infrastructure
2. Set up APM in staging environment first
3. Test with production-like traffic
4. Gradually roll out to production with low sampling rate
5. Increase sampling as you validate performance impact
6. Create custom dashboards for key business metrics
7. Set up alerting for SLO violations

## Support

For APM integration questions:
- Review vendor documentation
- Check community forums
- Contact support (paid plans)
- Consult with DevOps team

---

**Document Version:** 1.0
**Last Updated:** February 2026
**Maintained By:** Enterprise DaaS Governance Team
