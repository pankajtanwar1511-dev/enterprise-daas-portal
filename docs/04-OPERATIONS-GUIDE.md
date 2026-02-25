# Enterprise DaaS Governance Portal - Operations Guide

**Version:** 3.0
**Last Updated:** February 25, 2026
**Target Audience:** DevOps, SREs, Operations Teams

---

## Table of Contents

1. [Observability & Monitoring](#1-observability--monitoring)
2. [APM Integration](#2-apm-integration)
3. [Security & Compliance](#3-security--compliance)
4. [Incident Response](#4-incident-response)

---

## 1. Observability & Monitoring

### Logging

**Structured Logging Format:**
```json
{
  "timestamp": "2026-02-25T10:30:00Z",
  "level": "INFO",
  "logger": "app.api.assets",
  "message": "Asset created successfully",
  "user_id": 1,
  "asset_id": 15,
  "correlation_id": "abc123"
}
```

**Log Levels:**
- **DEBUG:** Detailed diagnostic information
- **INFO:** General informational messages
- **WARNING:** Warning messages
- **ERROR:** Error events
- **CRITICAL:** Critical failures

**Log Aggregation:**
- CloudWatch Logs (AWS)
- ELK Stack (on-premise)
- Retention: 90 days

### Metrics

**Application Metrics:**
- Request rate (req/sec)
- Response time (P50, P95, P99)
- Error rate (%)
- Active users

**Database Metrics:**
- Connection pool usage
- Query duration
- Slow queries (>1s)
- Transaction rate

**System Metrics:**
- CPU utilization (%)
- Memory usage (%)
- Disk I/O
- Network traffic

### Alerting

**Critical Alerts:**
- API error rate >5%
- Database connection pool exhausted
- Response time P95 >2s
- System CPU >90% for 5min

**Alert Channels:**
- PagerDuty (critical)
- Slack #ops-alerts (warning)
- Email (info)

---

## 2. APM Integration

### DataDog APM

**Installation:**
```bash
# Add to requirements.txt
ddtrace

# Run with DataDog
ddtrace-run uvicorn app.main:app --host 0.0.0.0 --port 8000
```

**Configuration:**
```python
# app/main.py
from ddtrace import tracer, patch_all

patch_all()  # Auto-instrument libraries

@app.middleware("http")
async def add_datadog_trace(request: Request, call_next):
    with tracer.trace("http.request", service="daas-portal"):
        response = await call_next(request)
        return response
```

**Custom Metrics:**
```python
from datadog import statsd

# Increment counter
statsd.increment('assets.created', tags=['environment:prod'])

# Record timing
with statsd.timed('database.query.duration'):
    results = db.query(Asset).all()
```

### New Relic APM

**Installation:**
```bash
# Add to requirements.txt
newrelic

# Generate config
newrelic-admin generate-config YOUR_LICENSE_KEY newrelic.ini

# Run with New Relic
NEW_RELIC_CONFIG_FILE=newrelic.ini newrelic-admin run-program uvicorn app.main:app
```

---

## 3. Security & Compliance

### Security Best Practices

**Authentication:**
- JWT tokens with 24-hour expiration
- Secure password hashing (bcrypt)
- Failed login lockout after 5 attempts

**Authorization:**
- Role-based access control (RBAC)
- Principle of least privilege
- Regular access reviews

**Data Protection:**
- TLS 1.3 encryption in transit
- Encrypted database backups
- PII data classification and handling

**Vulnerability Management:**
- Weekly dependency scans (Snyk, Dependabot)
- Monthly security reviews
- Quarterly penetration testing

### Compliance Requirements

**SOC 2:**
- Complete audit trail (7-year retention)
- Access control documentation
- Change management process
- Incident response plan

**GDPR:**
- Data processing agreements
- Right to erasure implementation
- Data breach notification (72 hours)
- Privacy impact assessments

**Audit Logging:**
- All user actions logged
- Immutable audit trail
- Exportable for external audits
- Tamper-evident storage

---

## 4. Incident Response

### Incident Severity Levels

**P1 - Critical:**
- Complete system outage
- Data breach
- **Response:** Immediate
- **Resolution:** 1 hour

**P2 - High:**
- Partial system outage
- Performance degradation >50%
- **Response:** 15 minutes
- **Resolution:** 4 hours

**P3 - Medium:**
- Non-critical feature broken
- Performance degradation <50%
- **Response:** 1 hour
- **Resolution:** 24 hours

**P4 - Low:**
- Minor bug, no user impact
- **Response:** Next business day
- **Resolution:** 1 week

### Incident Response Process

**1. Detection & Alert**
- Monitoring system triggers alert
- On-call engineer notified

**2. Triage & Assessment**
- Determine severity level
- Assemble response team
- Create incident ticket

**3. Investigation & Diagnosis**
- Review logs and metrics
- Identify root cause
- Document findings

**4. Mitigation & Resolution**
- Implement fix
- Verify resolution
- Monitor for recurrence

**5. Post-Incident Review**
- Root cause analysis (RCA)
- Document lessons learned
- Create prevention action items

### Common Incidents & Solutions

**Database Connection Pool Exhausted:**
```bash
# Immediate: Restart backend service
docker restart backend

# Long-term: Increase pool size
# In database.py:
engine = create_engine(DATABASE_URL, pool_size=20, max_overflow=10)
```

**High API Latency:**
```bash
# Check slow queries
SELECT query, mean_exec_time, calls
FROM pg_stat_statements
WHERE mean_exec_time > 1000
ORDER BY mean_exec_time DESC
LIMIT 10;

# Add missing indexes
CREATE INDEX idx_assets_domain_lifecycle ON assets(domain_id, lifecycle_stage);
```

**Memory Leak:**
```bash
# Monitor memory usage
docker stats backend

# Check for unclosed connections
# Review code for:
# - Database sessions not closed
# - Large objects not garbage collected
# - Circular references
```

### Backup & Recovery

**Backup Schedule:**
- Full backup: Daily at 2 AM
- Incremental: Every 4 hours
- Retention: 30 days

**Recovery Procedures:**

**1. Database Restore:**
```bash
# Stop backend
docker stop backend

# Restore from backup
pg_restore -h localhost -U postgres -d governance_portal -v backup_file.dump

# Start backend
docker start backend
```

**2. Full System Recovery:**
```bash
# Restore database
pg_restore -d governance_portal backup_file.dump

# Restore frontend
aws s3 sync s3://backups/frontend/dist/ s3://prod-frontend/

# Deploy backend
docker pull company/daas-portal:v3.0
docker-compose up -d
```

**Recovery Time Objectives (RTO):**
- P1 Incidents: 1 hour
- Database corruption: 4 hours
- Complete disaster: 8 hours

**Recovery Point Objectives (RPO):**
- Transaction log backups: 15 minutes
- Maximum data loss: 15 minutes

---

**Version:** 3.0  
**Status:** Published  
**Document Owner:** Site Reliability Engineering Team
