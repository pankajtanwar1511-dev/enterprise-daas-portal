# Observability & Monitoring

## Overview

The Enterprise DaaS Governance Portal includes comprehensive observability features for production monitoring, debugging, and performance optimization.

## 📊 Components

### 1. **Structured Logging**
- Production-ready logging with [structlog](https://www.structlog.org/)
- JSON output for log aggregation (ELK, Splunk, CloudWatch)
- Request ID tracking across entire request lifecycle
- Security event logging
- Integration with Sentry for error tracking

**Documentation:** [Logging Configuration](../../backend/app/logging_config.py)

**Features:**
- ✅ Colorful console output in development
- ✅ JSON logs in production
- ✅ Request/response logging middleware
- ✅ Performance logging (slow request detection)
- ✅ Database query logging
- ✅ Sentry integration

### 2. **Health Checks**
- Comprehensive system health monitoring
- Kubernetes-ready probes (liveness, readiness)
- Database connectivity checks
- System resource monitoring (CPU, memory, disk)
- External dependency checks

**Endpoints:**
- `GET /api/v1/health` - Comprehensive health status
- `GET /api/v1/health/ready` - Readiness probe (503 if not ready)
- `GET /api/v1/health/live` - Liveness probe

**Documentation:** [Health Check Service](../../backend/app/services/health_check.py)

### 3. **Prometheus Metrics**
- HTTP request metrics (count, latency, sizes)
- Database query metrics
- Business metrics (assets, compliance, violations)
- Connection pool monitoring
- System metrics

**Endpoint:**
- `GET /metrics` - Prometheus metrics in text format

**Documentation:** [Metrics Service](../../backend/app/services/metrics.py)

**Available Metrics:**
```
# Application Metrics
http_requests_total
http_request_duration_seconds
http_request_size_bytes
http_response_size_bytes
http_requests_in_progress

# Database Metrics
database_queries_total
database_query_duration_seconds
database_connections_active
database_connection_pool_size

# Business Metrics
assets_total
assets_compliance_rate
assets_by_lifecycle_stage
change_requests_total
compliance_violations_total
```

### 4. **APM Integration** (Optional)
- DataDog APM
- New Relic
- AWS X-Ray
- Elastic APM
- Dynatrace

**Documentation:** [APM Integration Guide](APM_INTEGRATION_GUIDE.md)

---

## 🚀 Quick Start

### 1. Basic Setup (Logging + Health + Metrics)

These features are already integrated and work out of the box:

```bash
# Start the application
cd backend
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

**Test the endpoints:**

```bash
# Health check
curl http://localhost:8000/api/v1/health | jq

# Readiness probe
curl http://localhost:8000/api/v1/health/ready

# Liveness probe
curl http://localhost:8000/api/v1/health/live

# Prometheus metrics
curl http://localhost:8000/metrics
```

### 2. Configure Logging

**Development (.env.development):**
```bash
LOG_LEVEL=DEBUG
ENVIRONMENT=development
SLOW_REQUEST_THRESHOLD_MS=1000
ENABLE_SENTRY=False
```

**Production (.env.production):**
```bash
LOG_LEVEL=INFO
ENVIRONMENT=production
SLOW_REQUEST_THRESHOLD_MS=500
ENABLE_SENTRY=True
SENTRY_DSN=https://your-sentry-dsn@sentry.io/project-id
```

### 3. Set Up Prometheus (Optional)

**Install Prometheus:**

```bash
# macOS
brew install prometheus

# Linux
wget https://github.com/prometheus/prometheus/releases/download/v2.48.0/prometheus-2.48.0.linux-amd64.tar.gz
tar xvf prometheus-2.48.0.linux-amd64.tar.gz
cd prometheus-2.48.0.linux-amd64
```

**Configure Prometheus (prometheus.yml):**

```yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'enterprise-daas-portal'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/metrics'
```

**Start Prometheus:**

```bash
./prometheus --config.file=prometheus.yml
```

Access Prometheus UI: `http://localhost:9090`

### 4. Set Up Grafana (Optional)

**Install Grafana:**

```bash
# macOS
brew install grafana

# Linux
sudo apt-get install -y grafana
```

**Start Grafana:**

```bash
# macOS
brew services start grafana

# Linux
sudo systemctl start grafana-server
```

Access Grafana: `http://localhost:3000` (admin/admin)

**Add Prometheus Data Source:**
1. Go to Configuration → Data Sources
2. Add Prometheus data source
3. URL: `http://localhost:9090`
4. Save & Test

**Import Dashboard:**
- Use ID 12159 for FastAPI monitoring
- Or create custom dashboards with our metrics

### 5. Set Up APM (Optional)

See [APM Integration Guide](APM_INTEGRATION_GUIDE.md) for detailed instructions.

**Quick setup for DataDog:**

```bash
# Install DataDog agent
pip install ddtrace

# Configure environment
export DD_SERVICE=enterprise-daas-portal
export DD_ENV=production
export DD_TRACE_ENABLED=true

# Run with auto-instrumentation
ddtrace-run uvicorn app.main:app --host 0.0.0.0 --port 8000
```

---

## 📈 Monitoring Strategy

### Development Environment
- ✅ Structured logging (console, colorful)
- ✅ Health checks
- ✅ Prometheus metrics
- ❌ Sentry (disabled)
- ❌ APM (optional)

### Staging Environment
- ✅ Structured logging (JSON)
- ✅ Health checks
- ✅ Prometheus metrics
- ✅ Sentry error tracking
- ✅ APM with 50% sampling

### Production Environment
- ✅ Structured logging (JSON)
- ✅ Health checks
- ✅ Prometheus metrics
- ✅ Sentry error tracking
- ✅ APM with 10% sampling
- ✅ Alerting and dashboards

---

## 🔍 Key Metrics to Monitor

### Application Performance
- **Request rate**: `rate(http_requests_total[5m])`
- **Error rate**: `rate(http_requests_total{status_code=~"5.."}[5m])`
- **Latency (P95)**: `histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))`
- **Latency (P99)**: `histogram_quantile(0.99, rate(http_request_duration_seconds_bucket[5m]))`

### Database Performance
- **Query rate**: `rate(database_queries_total[5m])`
- **Query duration**: `histogram_quantile(0.95, rate(database_query_duration_seconds_bucket[5m]))`
- **Connection pool usage**: `database_connections_active / database_connection_pool_size`

### Business Metrics
- **Asset compliance rate**: `assets_compliance_rate`
- **Total assets**: `assets_total`
- **Open violations**: `compliance_violations_open`
- **Pending change requests**: `change_requests_pending`

### System Health
- **CPU usage**: `process_cpu_seconds_total`
- **Memory usage**: `process_resident_memory_bytes`
- **Open file descriptors**: `process_open_fds`

---

## 🚨 Alerting Rules

### Prometheus Alert Rules (alerts.yml)

```yaml
groups:
  - name: application
    rules:
      # High error rate
      - alert: HighErrorRate
        expr: rate(http_requests_total{status_code=~"5.."}[5m]) > 0.05
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High error rate detected"
          description: "Error rate is {{ $value }} (threshold: 0.05)"

      # High latency
      - alert: HighLatency
        expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 1.0
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High request latency detected"
          description: "P95 latency is {{ $value }}s (threshold: 1.0s)"

      # Low compliance rate
      - alert: LowComplianceRate
        expr: assets_compliance_rate < 0.8
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "Asset compliance rate is low"
          description: "Compliance rate is {{ $value }} (threshold: 0.8)"

      # Database connection pool exhaustion
      - alert: DatabasePoolExhaustion
        expr: database_connections_active / database_connection_pool_size > 0.9
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Database connection pool nearly exhausted"
          description: "Pool usage is {{ $value }} (threshold: 0.9)"
```

---

## 📊 Sample Grafana Dashboard Queries

### Request Rate Panel
```promql
rate(http_requests_total[5m])
```

### Error Rate Panel
```promql
sum(rate(http_requests_total{status_code=~"5.."}[5m])) / sum(rate(http_requests_total[5m]))
```

### Latency Percentiles Panel
```promql
histogram_quantile(0.50, rate(http_request_duration_seconds_bucket[5m]))
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))
histogram_quantile(0.99, rate(http_request_duration_seconds_bucket[5m]))
```

### Database Query Performance Panel
```promql
rate(database_queries_total[5m])
histogram_quantile(0.95, rate(database_query_duration_seconds_bucket[5m]))
```

### Asset Compliance Panel
```promql
assets_compliance_rate{domain="all"}
```

---

## 🐛 Troubleshooting

### Logs Not Appearing

**Issue:** Logs not showing in console

**Solution:**
```bash
# Check log level
echo $LOG_LEVEL

# Set to DEBUG
export LOG_LEVEL=DEBUG

# Restart application
```

### Prometheus Metrics Not Updating

**Issue:** Metrics showing stale data

**Solution:**
```bash
# Check metrics endpoint
curl http://localhost:8000/metrics

# Verify Prometheus scraping
# Check Prometheus UI → Status → Targets
```

### Health Check Failing

**Issue:** `/api/v1/health` returns unhealthy

**Solution:**
```bash
# Check database connectivity
psql -h localhost -U daas_admin -d governance_portal

# Check system resources
df -h  # Disk space
free -m  # Memory
top  # CPU
```

### Sentry Not Capturing Errors

**Issue:** Errors not appearing in Sentry

**Solution:**
```bash
# Verify Sentry configuration
echo $ENABLE_SENTRY  # Should be "true"
echo $SENTRY_DSN  # Should be set

# Test Sentry integration
python -c "
import sentry_sdk
sentry_sdk.init(dsn='$SENTRY_DSN')
sentry_sdk.capture_message('Test message')
print('Test event sent to Sentry')
"
```

---

## 📚 Additional Resources

### Documentation
- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)
- [structlog Documentation](https://www.structlog.org/)
- [Sentry Documentation](https://docs.sentry.io/)

### Dashboards
- [FastAPI Grafana Dashboard](https://grafana.com/grafana/dashboards/12159)
- [Python Prometheus Dashboard](https://grafana.com/grafana/dashboards/10045)

### Best Practices
- [Google SRE Book - Monitoring](https://sre.google/sre-book/monitoring-distributed-systems/)
- [The Four Golden Signals](https://sre.google/sre-book/monitoring-distributed-systems/#xref_monitoring_golden-signals)
- [RED Method](https://www.weave.works/blog/the-red-method-key-metrics-for-microservices-architecture/)

---

## 🎯 Performance Targets

### SLIs (Service Level Indicators)
- **Availability**: 99.9% (< 43 minutes downtime/month)
- **Latency (P95)**: < 500ms
- **Latency (P99)**: < 1000ms
- **Error rate**: < 0.1%

### SLOs (Service Level Objectives)
- 95% of requests complete in < 500ms
- 99% of requests complete in < 1000ms
- Error rate below 0.1%
- No more than 43 minutes downtime per month

---

## 🔐 Security Considerations

### Sensitive Data in Logs
Never log:
- Passwords
- API keys
- Authentication tokens
- Personal identifiable information (PII)
- Credit card numbers

### Metrics Security
- Expose `/metrics` endpoint only to monitoring systems
- Use authentication/authorization for metrics access in production
- Consider using mutual TLS for Prometheus scraping

### APM Data Privacy
- Configure APM to redact sensitive fields
- Disable request/response body capture for sensitive endpoints
- Use sampling to reduce data volume

---

**Version:** 1.0
**Last Updated:** February 2026
**Status:** Production Ready
