# Testing & Analytics Guide

## 📊 System Analytics Dashboard

**Location:** `/home/pankaj/enterprise-daas-portal/backend/system_analytics.py`

**Run comprehensive system analytics:**
```bash
cd /home/pankaj/enterprise-daas-portal/backend
source venv/bin/activate
python system_analytics.py
```

**Features:**
- ✅ System health checks (database, schema, authentication)
- ✅ Executive summary dashboard
- ✅ Database statistics (all tables)
- ✅ Asset analytics (by environment, lifecycle, compliance)
- ✅ Phase 3 integration metrics (webhooks, API keys, deliveries)
- ✅ Strategic business metrics (goals, budgets)
- ✅ User activity tracking
- ✅ Recent activity logs (last 24 hours)

---

## 🧪 Available Test Scripts

### 1. **Phase 1: CRUD Operations Test**
```bash
cd /home/pankaj/enterprise-daas-portal/backend
./test_crud_complete.sh
```

**Tests:**
- ✅ Authentication (login/logout)
- ✅ CREATE assets with naming validation
- ✅ READ assets (list and detail)
- ✅ UPDATE assets
- ✅ DELETE assets
- ✅ Verification of changes

### 2. **Phase 3: Enterprise Integration Test**
```bash
cd /home/pankaj/enterprise-daas-portal/backend
./test_phase3.sh
```

**Tests:**
- ✅ Webhook creation and management
- ✅ Webhook listing
- ✅ API key generation
- ✅ API key authentication
- ✅ API key listing

### 3. **Individual Test Scripts**
```bash
# Test asset creation only
./test_create.sh

# Run all tests
./test_crud_complete.sh
./test_phase3.sh
```

---

## 📈 Current System Metrics (Live Data)

Based on latest analytics run:

### System Health: ✅ ALL SYSTEMS OPERATIONAL

**Database:**
- ✅ Connection: Healthy
- ✅ Schema: All tables present
- ✅ Data Integrity: Verified

**Core Data:**
- 📦 Assets: 5 (80.0% compliant)
- 👥 Users: 5 active users
- 🏢 Domains: 6
- 🎯 Business Goals: 3
- 💼 Vendors: 3

**Phase 3 Integration:**
- 🔔 Webhooks: 1 active
- 🔑 API Keys: 1 active
- 📊 Total API Usage: 0 calls (just created)

### Asset Distribution

**By Environment:**
| Environment | Count |
|-------------|-------|
| PROD        | 3     |
| QA          | 1     |
| DEV         | 1     |

**By Lifecycle:**
| Stage      | Count |
|------------|-------|
| Active     | 4     |
| Draft      | 1     |

**Compliance:**
- ✅ Compliant: 4 assets (80%)
- ⚠️ Non-Compliant: 1 asset (20%)
- 📋 Violations: 1 recorded

---

## 🔍 API Testing Tools

### Using curl

**1. Login and Get Token:**
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=demo123"
```

**2. List Assets:**
```bash
curl -X GET http://localhost:8000/api/v1/assets/ \
  -H "Authorization: Bearer <TOKEN>"
```

**3. Create Webhook:**
```bash
curl -X POST http://localhost:8000/api/v1/webhooks/ \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Webhook",
    "url": "https://webhook.site/test",
    "events": ["asset.created"],
    "retry_count": 3,
    "timeout_seconds": 10
  }'
```

**4. Generate API Key:**
```bash
curl -X POST http://localhost:8000/api/v1/api-keys/ \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "key_name": "Test Key",
    "expires_in_days": 30,
    "rate_limit_per_hour": 1000
  }'
```

### Using API Documentation

**Interactive API Docs:** http://localhost:8000/api/docs

Features:
- Try all endpoints interactively
- View request/response schemas
- Test authentication
- Explore all API capabilities

---

## 📊 Real-Time Monitoring

### Database Queries

**Connect to database:**
```bash
cd /home/pankaj/enterprise-daas-portal/backend
source venv/bin/activate
python
```

```python
from app.database import SessionLocal
from app import models
from app.models_integrations import *

db = SessionLocal()

# Get statistics
print(f"Assets: {db.query(models.Asset).count()}")
print(f"Webhooks: {db.query(Webhook).count()}")
print(f"API Keys: {db.query(APIKey).count()}")

# Get recent activity
recent_assets = db.query(models.Asset).order_by(models.Asset.created_at.desc()).limit(5).all()
for asset in recent_assets:
    print(f"- {asset.asset_name} ({asset.environment})")

db.close()
```

### View Logs

**Backend logs:**
```bash
tail -f /tmp/backend.log
```

**Integration logs:**
```python
from app.models_integrations import IntegrationLog

logs = db.query(IntegrationLog).order_by(IntegrationLog.created_at.desc()).limit(10).all()
for log in logs:
    print(f"{log.integration_type}: {log.operation} - {log.status}")
```

---

## 🎯 Key Performance Indicators (KPIs)

### Asset Governance
- **Compliance Rate:** 80.0% (Target: 100%)
- **Total Assets:** 5
- **Active Assets:** 4
- **Lifecycle Stages:** 2 (Active, Draft)

### Integration Performance
- **Webhook Success Rate:** N/A (no deliveries yet)
- **API Key Usage:** 0 calls
- **Active Integrations:** 2 (1 webhook, 1 API key)

### Strategic Goals
- **Goals Tracked:** 3
- **Initiatives In Progress:** 2
- **Vendor Partnerships:** 3

---

## 🚀 Quick Commands

```bash
# Run all analytics
python system_analytics.py

# Test Phase 1 (CRUD)
./test_crud_complete.sh

# Test Phase 3 (Integrations)
./test_phase3.sh

# View API documentation
open http://localhost:8000/api/docs
# (or visit in browser)

# Check backend status
curl http://localhost:8000/api/v1/health

# View database
sqlite3 governance_portal.db ".tables"
```

---

## 📝 Test Credentials

**Admin User:**
- Username: `admin`
- Password: `demo123`
- Role: Admin (full access)

**Other Test Users:**
- `jsmith` / `demo123` (DataSteward)
- `mjohnson` / `demo123` (AssetOwner)
- `rdavis` / `demo123` (Viewer)

---

## 🔬 Advanced Analytics

### Custom Queries

**Asset compliance by domain:**
```python
from sqlalchemy import func

results = db.query(
    models.Domain.domain_code,
    func.count(models.Asset.asset_id).label('total'),
    func.sum(func.cast(models.Asset.naming_compliant, int)).label('compliant')
).join(models.Asset).group_by(models.Domain.domain_code).all()

for row in results:
    print(f"{row[0]}: {row[2]}/{row[1]} compliant")
```

**Webhook delivery statistics:**
```python
from sqlalchemy import func

stats = db.query(
    func.count(WebhookDelivery.delivery_id).label('total'),
    func.sum(func.cast(WebhookDelivery.success, int)).label('success')
).first()

print(f"Success rate: {stats.success}/{stats.total}")
```

---

## 📧 Generated Reports

**Executive Summary** - Run anytime:
```bash
python system_analytics.py | grep -A 30 "EXECUTIVE SUMMARY"
```

**Asset Analytics** - Quick view:
```bash
python system_analytics.py | grep -A 20 "ASSET ANALYTICS"
```

**Integration Metrics** - Phase 3 data:
```bash
python system_analytics.py | grep -A 15 "INTEGRATION ANALYTICS"
```

---

## ✅ Verification Checklist

### System Verification
- [x] Database connectivity
- [x] All tables created
- [x] Sample data loaded
- [x] Authentication working
- [x] CRUD operations functional

### Phase 1 Verification
- [x] Asset creation with validation
- [x] Asset retrieval (list/detail)
- [x] Asset updates
- [x] Asset deletion
- [x] JWT authentication

### Phase 3 Verification
- [x] Webhook creation
- [x] Webhook management
- [x] API key generation
- [x] API key authentication
- [x] Integration logging

---

## 🎓 Next Steps

1. **Monitor System Health:**
   - Run `python system_analytics.py` daily
   - Check compliance rates
   - Review integration metrics

2. **Test Integrations:**
   - Create webhooks for your endpoints
   - Generate API keys for automation
   - Monitor delivery success rates

3. **Expand Analytics:**
   - Add custom metrics
   - Create scheduled reports
   - Set up alerting thresholds

---

**All testing and analytics tools are operational and ready to use!** 🎉
