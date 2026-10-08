# DESIGN.md - Enterprise DaaS Governance Portal

**Version:** 3.0
**Last Updated:** 2026-02-26
**Status:** Living Document - Always Update After ANY Change

---

## 🔴 CRITICAL: Single Source of Truth

**This document is the MASTER REFERENCE for the entire application.**

**Golden Rule:**
> PostgreSQL Database Schema = Source of Truth
> All changes MUST update this document FIRST, then update code.

**Before ANY Change:**
1. Read this document
2. Plan the change across ALL layers (DB → Model → API → Frontend)
3. Update this document
4. Then update code
5. Verify end-to-end
6. Update this document with actual implementation details

---

## Table of Contents

1. [System Overview](#system-overview)
2. [Architecture Layers](#architecture-layers)
3. [Database Schema Reference](#database-schema-reference)
4. [Backend Models Mapping](#backend-models-mapping)
5. [API Endpoints Catalog](#api-endpoints-catalog)
6. [Frontend Components Mapping](#frontend-components-mapping)
7. [Data Flow Diagrams](#data-flow-diagrams)
8. [Change Management Process](#change-management-process)
9. [Known Issues & Fixes](#known-issues--fixes)
10. [Testing Strategy](#testing-strategy)

---

## System Overview

### Technology Stack

**Frontend:**
- React 18.2.0
- Material-UI 5.14.18
- Vite 5.0.2
- Axios 1.6.2

**Backend:**
- FastAPI 0.109.2
- SQLAlchemy 2.0.25
- PostgreSQL 14+
- Alembic (migrations)

**Deployment:**
- Frontend: http://localhost:5173
- Backend: http://localhost:8000
- Database: postgresql://localhost:5432/governance_portal

### Discovery Statistics

- **Database Tables:** 44
- **Backend Models:** 44
- **API Endpoints:** 191
- **Frontend Components:** 41

---

## Architecture Layers

### Layer 1: Database (PostgreSQL)
- **Location:** PostgreSQL server
- **Migration Tool:** Alembic
- **Schema Files:** `/backend/alembic/versions/`

### Layer 2: Backend Models (SQLAlchemy ORM)
- **Location:** `/backend/app/models*.py`
- **Files:**
  - `models.py` - Core models (9 tables)
  - `models_extended.py` - Strategic models (11 tables)
  - `models_advanced.py` - Governance/quality models
  - `models_integrations.py` - Integration models (webhooks, events)
  - `models_itsm.py` - ITSM integration models
  - `models_collaboration.py` - Tasks, notifications, comments

### Layer 3: API Layer (FastAPI)
- **Location:** `/backend/app/api/`
- **Files:** 23 API modules
- **Base URL:** `http://localhost:8000/api/v1`

### Layer 4: Frontend (React)
- **Location:** `/frontend/src/components/`
- **Directories:** 33 component directories
- **Components:** 41 JSX files

---

## Database Schema Reference

### Core Tables (9 tables) - Primary Business Data

| Table | Purpose | Row Count | Model | API Endpoint | Frontend |
|-------|---------|-----------|-------|--------------|----------|
| **assets** | Data/platform assets | 5 | Asset | /assets | AssetRegistry/ |
| **domains** | Business domains (HR, FIN, etc) | 6 | Domain | /domains | AssetRegistry/ |
| **users** | User accounts | 5 | User | /auth/me | Login, UserManagement/ |
| **roles** | User roles (Admin, Viewer, etc) | 4 | Role | /roles | UserManagement/ |
| **change_requests** | ITIL change management | 20 | ChangeRequest | /change-requests | ChangeRequests/ |
| **compliance_violations** | Compliance issues | 25 | ComplianceViolation | /compliance/violations | ComplianceDashboard/ |
| **audit_logs** | Immutable audit trail | 100 | AuditLog | /audit-logs | AuditLogs/ |
| **lifecycle_history** | Asset state transitions | ? | LifecycleHistory | /assets/{id}/history | AssetRegistry/ |
| **compliance_metrics** | Time-series metrics | ? | ComplianceMetric | /compliance/metrics | ComplianceDashboard/ |

### Strategic Tables (11 tables) - Business Goals & Planning

| Table | Purpose | Row Count | Model | API Endpoint | Frontend |
|-------|---------|-----------|-------|--------------|----------|
| **business_goals** | Strategic objectives | 3 | BusinessGoal | /strategy/goals | StrategyDashboard/ |
| **strategic_initiatives** | DaaS projects | 2 | StrategicInitiative | /strategy/initiatives | StrategyDashboard/ |
| **initiative_deliverables** | Project deliverables | ? | InitiativeDeliverable | /initiatives/{id}/deliverables | StrategyDashboard/ |
| **vendors** | Vendor/partner info | 3 | Vendor | /vendors | VendorManagement/ |
| **vendor_slas** | Service level agreements | ? | VendorSLA | /vendors/{id}/slas | VendorManagement/ |
| **stakeholders** | Business stakeholders | ? | Stakeholder | /stakeholders | StakeholderManagement/ |
| **stakeholder_data_needs** | Data requirements | ? | StakeholderDataNeed | /stakeholders/{id}/needs | StakeholderManagement/ |
| **business_use_cases** | Use case documentation | ? | BusinessUseCase | /use-cases | UseCases/ |
| **budget_allocations** | Budget tracking | ? | BudgetAllocation | /budget | BudgetTracking/ |
| **asset_business_alignment** | Asset-to-goal mapping | ? | AssetBusinessAlignment | (join table) | - |
| **asset_vendor_mapping** | Asset-to-vendor mapping | ? | AssetVendorMapping | (join table) | - |

### Governance & Quality Tables (10 tables)

| Table | Purpose | Row Count | Model | API Endpoint | Frontend |
|-------|---------|-----------|-------|--------------|----------|
| **governance_policies** | Governance policy rules | 15 | GovernancePolicy | /governance/policies | GovernancePolicies/ |
| **policy_validations** | Policy check results | 100 | PolicyValidation | /governance/validations | GovernancePolicies/ |
| **data_quality_rules** | DQ rule definitions | ? | DataQualityRule | /quality/rules | DataQuality/ |
| **quality_check_runs** | DQ check execution logs | ? | QualityCheckRun | /quality/runs | DataQuality/ |
| **data_lineage_nodes** | Lineage graph nodes | ? | DataLineageNode | /lineage/nodes | DataLineage/ |
| **data_lineage_edges** | Lineage graph edges | ? | DataLineageEdge | /lineage/edges | DataLineage/ |
| **impact_analysis_runs** | Impact analysis results | ? | ImpactAnalysisRun | /impact/runs | ImpactAnalysis/ |
| **schema_registry** | Schema versioning | ? | SchemaRegistryEntry | /schemas | SchemaRegistry/ |
| **schema_validations** | Schema validation results | ? | SchemaValidation | /schemas/validations | SchemaRegistry/ |
| **sla_monitoring** | SLA metrics tracking | ? | SLAMonitoring | /sla/monitoring | SLADashboard/ |
| **sla_violations** | SLA breach records | ? | SLAViolation | /sla/violations | SLADashboard/ |
| **value_delivered_metrics** | ROI tracking | ? | ValueDeliveredMetric | /strategy/value | StrategyDashboard/ |

### Integration Tables (10 tables)

| Table | Purpose | Row Count | Model | API Endpoint | Frontend |
|-------|---------|-----------|-------|--------------|----------|
| **webhooks** | Webhook configurations | 15 | Webhook | /webhooks | Webhooks/ |
| **webhook_deliveries** | Webhook delivery logs | 100 | WebhookDelivery | /webhooks/{id}/deliveries | Webhooks/ |
| **api_keys** | API key management | ? | APIKey | /api-keys | APIKeys/ |
| **integration_logs** | Integration event logs | ? | IntegrationLog | /integrations/logs | IntegrationLogs/ |
| **import_jobs** | Bulk import tracking | ? | ImportJob | /import/jobs | BulkImport/ |
| **itsm_configurations** | ITSM system configs | ? | ITSMConfiguration | /itsm/config | ITSMIntegration/ |
| **itsm_record_mappings** | ITSM record mappings | ? | ITSMRecordMapping | /itsm/mappings | ITSMIntegration/ |
| **itsm_sync_logs** | ITSM sync logs | ? | ITSMSyncLog | /itsm/sync-logs | ITSMIntegration/ |
| **event_catalog** (future) | Event catalog | - | EventDefinition | /events | EventCatalog/ |

### Collaboration Tables (4 tables)

| Table | Purpose | Row Count | Model | API Endpoint | Frontend |
|-------|---------|-----------|-------|--------------|----------|
| **tasks** | Task management | 50 | Task | /tasks | TaskManagement/ |
| **notifications** | In-app notifications | 100 | Notification | /notifications | NotificationCenter/ |
| **comments** | Comments/discussions | 75 | Comment | /comments/{entity_type}/{id} | CommentSection/ |
| **activity_logs** | Activity feed | 200 | ActivityLog | /activity | ActivityFeed/ |

---

## Backend Models Mapping

### File: models.py (Core Models)

```python
# 9 Core Models
class Role(Base)
class User(Base)
class Domain(Base)
class Asset(Base)
class LifecycleHistory(Base)
class ChangeRequest(Base)
class ComplianceViolation(Base)
class AuditLog(Base)
class ComplianceMetric(Base)
```

### File: models_extended.py (Strategic Models)

```python
# 11 Strategic Models
class BusinessGoal(Base)
class StrategicInitiative(Base)
class InitiativeDeliverable(Base)
class Vendor(Base)
class VendorSLA(Base)
class Stakeholder(Base)
class StakeholderDataNeed(Base)
class BusinessUseCase(Base)
class BudgetAllocation(Base)
class AssetBusinessAlignment(Base)
class AssetVendorMapping(Base)
```

### File: models_advanced.py (Governance & Quality)

```python
# 12 Governance/Quality Models
class GovernancePolicy(Base)
class PolicyValidation(Base)
class DataQualityRule(Base)
class QualityCheckRun(Base)
class DataLineageNode(Base)
class DataLineageEdge(Base)
class ImpactAnalysisRun(Base)
class SchemaRegistryEntry(Base)
class SchemaValidation(Base)
class SLAMonitoring(Base)
class SLAViolation(Base)
class ValueDeliveredMetric(Base)
```

### File: models_integrations.py (Integration Models)

```python
# 6 Integration Models
class Webhook(Base)
class WebhookDelivery(Base)
class APIKey(Base)
class IntegrationLog(Base)
class ImportJob(Base)
class EventDefinition(Base)  # Future
```

### File: models_itsm.py (ITSM Models)

```python
# 3 ITSM Models
class ITSMConfiguration(Base)
class ITSMRecordMapping(Base)
class ITSMSyncLog(Base)
```

### File: models_collaboration.py (Collaboration Models)

```python
# 4 Collaboration Models
class Task(Base)
class Notification(Base)
class Comment(Base)
class ActivityLog(Base)
```

**Total Models: 44**

---

## API Endpoints Catalog

### Core Business APIs (6 modules)

#### `/api/v1/assets` - Asset Management
- `GET /assets` - List all assets
- `GET /assets/{id}` - Get asset by ID
- `POST /assets` - Create new asset
- `PUT /assets/{id}` - Update asset
- `DELETE /assets/{id}` - Delete asset
- `GET /assets/{id}/history` - Get lifecycle history

#### `/api/v1/change-requests` - Change Management
- `GET /change-requests` - List all change requests
- `GET /change-requests/{id}` - Get change request details
- `POST /change-requests` - Create change request
- `PUT /change-requests/{id}` - Update change request
- `POST /change-requests/{id}/approve` - Approve change
- `POST /change-requests/{id}/reject` - Reject change

#### `/api/v1/compliance` - Compliance Management
- `GET /compliance/metrics` - Get compliance KPIs
- `GET /compliance/violations` - List violations
- `POST /compliance/validate/naming` - Validate asset name
- `GET /compliance/domains` - Get approved domains

#### `/api/v1/audit-logs` - Audit Trail
- `GET /audit-logs` - List audit logs
- `GET /audit-logs?user_id={id}` - Filter by user
- `GET /audit-logs?entity_type={type}` - Filter by entity

#### `/api/v1/auth` - Authentication
- `POST /auth/login` - User login
- `POST /auth/logout` - User logout
- `GET /auth/me` - Get current user

#### `/api/v1/domains` - Domain Management
- `GET /domains` - List all domains
- `POST /domains` - Create domain

### Strategic Planning APIs (3 modules)

#### `/api/v1/strategy` - Strategic Planning
- `GET /strategy/summary` - Executive summary
- `GET /strategy/goals` - List business goals
- `POST /strategy/goals` - Create business goal
- `GET /strategy/initiatives` - List strategic initiatives
- `POST /strategy/initiatives` - Create initiative
- `GET /strategy/roi` - ROI metrics
- `GET /strategy/value` - Value delivered metrics

#### `/api/v1/vendors` - Vendor Management
- `GET /vendors` - List vendors
- `GET /vendors/{id}` - Get vendor details
- `POST /vendors` - Create vendor
- `GET /vendors/{id}/slas` - Get vendor SLAs
- `POST /vendors/{id}/slas` - Create SLA

#### `/api/v1/stakeholders` - Stakeholder Management
- `GET /stakeholders` - List stakeholders
- `POST /stakeholders` - Create stakeholder
- `GET /stakeholders/{id}/needs` - Get data needs

### Governance & Quality APIs (5 modules)

#### `/api/v1/governance` - Governance Policies
- `GET /governance/policies` - List policies
- `POST /governance/policies` - Create policy
- `GET /governance/validations` - List validations
- `POST /governance/validate` - Run validation

#### `/api/v1/quality` - Data Quality
- `GET /quality/rules` - List DQ rules
- `POST /quality/rules` - Create DQ rule
- `GET /quality/runs` - List check runs
- `POST /quality/check` - Run DQ check

#### `/api/v1/lineage` - Data Lineage
- `GET /lineage/nodes` - List lineage nodes
- `GET /lineage/edges` - List lineage edges
- `GET /lineage/graph?asset_id={id}` - Get lineage graph

#### `/api/v1/impact` - Impact Analysis
- `POST /impact/analyze` - Run impact analysis
- `GET /impact/runs` - List analysis runs

#### `/api/v1/schemas` - Schema Registry
- `GET /schemas` - List registered schemas
- `POST /schemas` - Register new schema
- `GET /schemas/validations` - List validations

### Integration APIs (4 modules)

#### `/api/v1/webhooks` - Webhook Management
- `GET /webhooks` - List webhooks
- `POST /webhooks` - Create webhook
- `GET /webhooks/{id}` - Get webhook details
- `PUT /webhooks/{id}` - Update webhook
- `DELETE /webhooks/{id}` - Delete webhook
- `POST /webhooks/{id}/test` - Test webhook
- `GET /webhooks/{id}/deliveries` - Get delivery logs
- `GET /webhooks/{id}/secret` - Get webhook secret

#### `/api/v1/api-keys` - API Key Management
- `GET /api-keys` - List API keys
- `POST /api-keys` - Create API key
- `DELETE /api-keys/{id}` - Revoke API key

#### `/api/v1/import` - Bulk Import
- `POST /import/jobs` - Start import job
- `GET /import/jobs` - List import jobs
- `GET /import/jobs/{id}` - Get job status

#### `/api/v1/itsm` - ITSM Integration
- `GET /itsm/config` - Get ITSM config
- `POST /itsm/sync` - Trigger sync
- `GET /itsm/sync-logs` - Get sync logs

### Collaboration APIs (4 modules)

#### `/api/v1/tasks` - Task Management
- `GET /tasks` - List tasks
- `POST /tasks` - Create task
- `PUT /tasks/{id}` - Update task
- `DELETE /tasks/{id}` - Delete task

#### `/api/v1/notifications` - Notifications
- `GET /notifications` - List notifications
- `PUT /notifications/{id}/read` - Mark as read
- `DELETE /notifications/{id}` - Delete notification

#### `/api/v1/comments` - Comments
- `GET /comments/{entity_type}/{entity_id}` - Get comments
- `POST /comments` - Create comment
- `PUT /comments/{id}` - Update comment
- `DELETE /comments/{id}` - Delete comment

#### `/api/v1/activity` - Activity Feed
- `GET /activity` - Get activity feed
- `GET /activity?user_id={id}` - Filter by user

**Total Endpoints: 191**

---

## Frontend Components Mapping

### Core Business Components (6 directories)

1. **AssetRegistry/** - Asset CRUD operations
2. **ChangeRequests/** - Change request management
3. **ComplianceDashboard/** - Compliance metrics & violations
4. **AuditLogs/** - Audit trail viewer
5. **Dashboard/** - Main overview dashboard
6. **NamingValidator/** - Real-time naming validation

### Strategic Planning Components (3 directories)

7. **StrategyDashboard/** - Strategic goals & ROI
8. **VendorManagement/** - Vendor & SLA management
9. **StakeholderManagement/** - Stakeholder data needs

### Governance & Quality Components (6 directories)

10. **GovernancePolicies/** - Policy management
11. **DataQuality/** - DQ rules & runs
12. **DataLineage/** - Lineage visualization
13. **ImpactAnalysis/** - Impact analysis dashboard
14. **SchemaRegistry/** - Schema versioning
15. **SLADashboard/** - SLA monitoring

### Integration Components (6 directories)

16. **Webhooks/** - Webhook configuration
17. **EventCatalog/** - Event catalog viewer
18. **IntegrationLogs/** - Integration event logs
19. **BulkImport/** - Bulk import UI
20. **ITSMIntegration/** - ITSM sync management
21. **APIKeys/** - API key management

### Collaboration Components (4 directories)

22. **TaskManagement/** - Task tracking
23. **NotificationCenter/** - Notification panel
24. **CommentSection/** - Comment threads
25. **ActivityFeed/** - Activity stream

### Reporting Components (3 directories)

26. **ManagementReports/** - Executive reports
27. **PPTGenerator/** - PowerPoint export
28. **BudgetTracking/** - Budget dashboard

### Other Components (4 directories)

29. **Login/** - Authentication UI
30. **UserManagement/** - User administration
31. **TeamDashboard/** - Team collaboration
32. **UseCases/** - Use case documentation
33. **ComplianceReports/** - Compliance reporting

**Total Component Directories: 33**

---

## Data Flow Diagrams

### User Creates Asset Flow

```
[Frontend]            [API]                 [Database]
   |                    |                       |
   | POST /assets       |                       |
   |------------------->|                       |
   |                    | Validate naming       |
   |                    | (NamingValidator)     |
   |                    |                       |
   |                    | INSERT INTO assets    |
   |                    |---------------------->|
   |                    |                       | ✓
   |                    | INSERT lifecycle_history
   |                    |---------------------->|
   |                    |                       | ✓
   |                    | INSERT audit_log      |
   |                    |---------------------->|
   |                    |                       | ✓
   |                    | Trigger webhook       |
   |                    | (if configured)       |
   |                    |                       |
   | <-- 201 Created ---|                       |
   |                    |                       |
```

### Compliance Violation Detection Flow

```
[Scheduler]          [API]                  [Database]
   |                   |                        |
   | Cron trigger      |                        |
   |------------------>|                        |
   |                   | SELECT all assets      |
   |                   |----------------------->|
   |                   |<------ assets[]        |
   |                   |                        |
   |                   | For each asset:        |
   |                   |   Validate naming      |
   |                   |   Check policies       |
   |                   |                        |
   |                   | INSERT violations      |
   |                   |----------------------->|
   |                   |                        | ✓
   |                   | Trigger notifications  |
   |                   |----------------------->|
   |                   |                        | ✓
```

---

## Change Management Process

### ⚠️ CRITICAL: Follow This Process for ALL Changes

#### Step 1: Plan the Change
1. Identify which layers are affected (Database / Model / API / Frontend)
2. Read current state in this DESIGN.md
3. Document planned changes in this file
4. Get approval if needed

#### Step 2: Update Database (if needed)
```bash
# Create migration
cd backend
alembic revision --autogenerate -m "description of change"

# Review migration file
# Edit if needed

# Apply migration
alembic upgrade head

# Update this DESIGN.md with new schema
```

#### Step 3: Update Backend Models (if needed)
```python
# Update models*.py files to match database
# Run verification:
python verify_models.py  # (create this script)
```

#### Step 4: Update API Endpoints (if needed)
```python
# Update app/api/*.py files
# Update schemas.py for request/response models
# Test endpoint:
curl -X GET http://localhost:8000/api/v1/endpoint
```

#### Step 5: Update Frontend (if needed)
```javascript
// Update components/*.jsx files
// Update API calls in services/
// Test in browser
```

#### Step 6: Update Seed Scripts (if needed)
```python
# Update seed_data.py
# Update seed_missing_data.py
# Update seed_remaining_tools.py
# Test seeding:
python seed_data.py
```

#### Step 7: Update This Document
```markdown
# Update DESIGN.md with:
- New table schemas
- New API endpoints
- New components
- New data flows
```

#### Step 8: End-to-End Testing
```bash
# Test full flow:
1. Backend starts without errors
2. Frontend loads without errors
3. API returns data
4. Frontend displays data
5. CRUD operations work
```

---

## Known Issues & Fixes

### Issue 1: Tasks API Returns 500 Error
- **Status:** 🔴 BROKEN
- **Symptom:** GET /api/v1/tasks returns 500 error
- **Root Cause:** Model/schema mismatch
- **Fix:** Phase 2 - Verify Task model matches tasks table

### Issue 2: Activity Logs API Returns 500 Error
- **Status:** 🔴 BROKEN
- **Symptom:** GET /api/v1/activity returns 500 error
- **Root Cause:** Model/schema mismatch
- **Fix:** Phase 2 - Verify ActivityLog model matches activity_logs table

### Issue 3: Missing Stakeholders Endpoint
- **Status:** 🟡 NOT IMPLEMENTED
- **Symptom:** GET /api/v1/stakeholders returns 404
- **Root Cause:** API endpoint not created yet
- **Fix:** Phase 3 - Create stakeholders.py API module

### Issue 4: Missing Budget Allocations Endpoint
- **Status:** 🟡 NOT IMPLEMENTED
- **Symptom:** GET /api/v1/budget returns 404
- **Root Cause:** API endpoint not created yet
- **Fix:** Phase 3 - Create budget.py API module

### Issue 5: Governance Policies Wrong Endpoint
- **Status:** 🟡 WRONG URL
- **Symptom:** GET /api/v1/governance/policies may not exist
- **Root Cause:** Endpoint URL mismatch
- **Fix:** Phase 3 - Verify correct endpoint path

---

## Testing Strategy

### Unit Tests (Backend)
```bash
cd backend
pytest tests/unit/ -v
```

### Integration Tests (Backend)
```bash
cd backend
pytest tests/integration/ -v
```

### API Tests (Automated)
```bash
python /tmp/test_endpoints.py
```

### Frontend Tests
```bash
cd frontend
npm run test
```

### End-to-End Tests
```bash
# Manual testing checklist
# 1. Start backend
# 2. Start frontend
# 3. Test each page
# 4. Verify data displays correctly
```

---

## Maintenance Schedule

### Daily
- Review any runtime errors
- Check audit logs for issues

### Weekly
- Update this document if ANY changes were made
- Run full test suite
- Review API endpoint health

### Monthly
- Review all unmapped tables
- Plan new feature implementations
- Update architecture diagrams

---

## Document Change Log

| Date | Version | Changes | Updated By |
|------|---------|---------|------------|
| 2026-02-26 | 3.0 | Initial comprehensive design document | Claude |

---

**END OF DESIGN.MD**

**Remember: THIS IS THE SOURCE OF TRUTH - UPDATE IT ALWAYS!**
