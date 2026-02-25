# ITIL Integration Concept
## Enterprise DaaS Governance Portal

**Version:** 1.0
**Date:** February 2026

---

## Purpose

This document defines how the Enterprise DaaS Governance Portal integrates with ITIL (Information Technology Infrastructure Library) service management processes to provide seamless governance across the IT service lifecycle.

---

## ITIL Overview

**ITIL Framework:**
ITIL is a set of detailed practices for IT service management (ITSM) that focuses on aligning IT services with business needs.

**Relevant ITIL Processes:**
1. Change Management
2. Release and Deployment Management
3. Configuration Management (CMDB)
4. Incident Management
5. Problem Management
6. Service Asset and Configuration Management (SACM)

---

## Integration Architecture

```
┌─────────────────────────────────────────────────────┐
│         DaaS Governance Portal                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐         │
│  │  Asset   │  │  Change  │  │  Audit   │         │
│  │ Registry │  │   Mgmt   │  │   Logs   │         │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘         │
└───────┼─────────────┼─────────────┼────────────────┘
        │             │             │
        │             │             │
    ┌───▼─────────────▼─────────────▼────┐
    │    Integration Layer (REST API)    │
    │    - Data Sync                     │
    │    - Event Webhooks                │
    │    - Bidirectional Updates         │
    └───┬─────────────┬─────────────┬────┘
        │             │             │
┌───────▼──────┐ ┌────▼─────┐ ┌────▼──────┐
│  ServiceNow  │ │  JIRA    │ │ BMC Remedy│
│  (ITSM)      │ │ Service  │ │ (ITSM)    │
└──────────────┘ │  Desk    │ └───────────┘
                 └──────────┘
```

---

## 1. Change Management Integration

### ITIL Change Management Process

**Purpose:** Control the lifecycle of all changes to minimize disruption

**Standard Change Flow:**
1. Change Request Creation
2. Change Assessment
3. Change Approval
4. Change Implementation
5. Change Review

---

### DaaS Portal Integration Points

#### 1.1 Change Request Creation

**Portal Trigger:**
When user submits change request for a registered asset

**Action:**
1. Portal creates internal change record
2. Portal API calls ServiceNow to create corresponding Change Request
3. Portal stores ServiceNow change ID for tracking

**Data Sync:**
```json
{
  "portal_change_id": "CHG-12345",
  "servicenow_change_id": "CHG0030123",
  "asset_name": "PROD-HR-DW-v1",
  "change_type": "Modify",
  "risk_level": "High",
  "requested_by": "jsmith@company.com",
  "impact_assessment": "Affects HR reporting",
  "implementation_plan": "...",
  "rollback_plan": "..."
}
```

---

#### 1.2 Risk Assessment

**Portal Contribution:**
- Asset criticality (based on lifecycle stage)
- Historical change success rate for asset
- Dependency impact (from asset relationships)

**ServiceNow Receives:**
- Portal-calculated risk score
- Asset metadata context
- Compliance status (compliant assets = lower risk)

**Risk Calculation:**
```python
risk_score = base_risk +
             (lifecycle_weight * 10) +
             (environment_weight * 5) +
             (compliance_penalty * 20)

Where:
  lifecycle_weight: Active=3, Deprecated=5, Draft=1
  environment_weight: PROD=3, QA=2, DEV=1
  compliance_penalty: Non-compliant=1, Compliant=0
```

---

#### 1.3 Approval Workflow

**Bidirectional Sync:**

**Portal → ServiceNow:**
- When Data Steward approves in Portal → Update ServiceNow status

**ServiceNow → Portal:**
- When CAB approves in ServiceNow → Webhook to Portal updates status

**Approval Matrix:**

| Risk Level | Portal Approval | ServiceNow Approval | Final Authority |
|------------|----------------|---------------------|-----------------|
| Low | Auto-approved | Standard Change | Portal |
| Medium | Data Steward | Change Manager | Portal |
| High | Data Steward + EA | CAB (Change Advisory Board) | ServiceNow |
| Critical | CAB + CDO | Emergency CAB | ServiceNow |

---

#### 1.4 Implementation Tracking

**Portal Behavior:**
- Change status updates in real-time from ServiceNow
- Implementation date/time recorded
- Post-implementation validation (did asset metadata update?)

**ServiceNow Receives:**
- Asset verification status (Portal confirms asset updated)
- Governance compliance check (naming still compliant post-change)

---

### Integration Endpoints

**Portal API:**
```
POST   /api/v1/integrations/servicenow/changes
PUT    /api/v1/integrations/servicenow/changes/{id}/status
GET    /api/v1/integrations/servicenow/changes/{id}
```

**ServiceNow Webhook (callback):**
```
POST   https://portal.company.com/api/v1/webhooks/servicenow
{
  "event": "change.approved",
  "change_id": "CHG0030123",
  "portal_change_id": "CHG-12345",
  "status": "Approved",
  "approver": "cab@company.com",
  "timestamp": "2026-02-21T10:30:00Z"
}
```

---

## 2. Configuration Management Database (CMDB) Integration

### ITIL CMDB Concept

**Configuration Item (CI):**
Any component that needs to be managed to deliver IT services

**CI Types:**
- Hardware
- Software
- Applications
- Data Assets ← **Portal Focus**

---

### DaaS Portal as CMDB Data Source

#### 2.1 Asset Sync to CMDB

**Sync Frequency:** Real-time (on asset create/update)

**Mapping:**

| Portal Field | CMDB Field | Notes |
|--------------|------------|-------|
| asset_id | CI_ID | Unique identifier |
| asset_name | CI_Name | Display name |
| domain | CI_Category | Business domain |
| environment | CI_Environment | DEV/QA/PROD |
| lifecycle_stage | CI_Status | Draft/Active/Deprecated/Retired |
| owner_id | CI_Owner | Assigned to |
| documentation_url | CI_Documentation | Link to docs |
| version | CI_Version | Version tracking |

**CMDB CI Class:** `DataAsset`

---

#### 2.2 Relationship Mapping

**Portal Tracks:**
- Asset dependencies (Asset A consumes data from Asset B)
- Asset → Application relationship
- Application → Server relationship

**CMDB Relationship Types:**
- `Depends On`: Asset dependencies
- `Runs On`: Application hosting
- `Hosted By`: Infrastructure relationship

**Example:**
```
PROD-HR-DW-v1 (Data Asset)
  ├── Depends On → PROD-HR-ETL-v2 (Data Asset)
  ├── Runs On → HR Data Platform (Application)
  └── Hosted By → AWS RDS Instance (Infrastructure)
```

---

#### 2.3 CMDB Data Quality

**Portal Contribution to CMDB Quality:**
- **Completeness:** All registered assets have required metadata
- **Accuracy:** Naming convention ensures consistent naming
- **Currency:** Lifecycle updates reflect actual state
- **Ownership:** Every asset has designated owner

**Portal Metrics for CMDB:**
- 100% of Portal assets synced to CMDB
- <5 minute sync latency
- 0 orphaned CIs (all have Portal source)

---

### Integration Endpoints

**Portal → CMDB Sync:**
```
POST   /api/v1/integrations/cmdb/sync
GET    /api/v1/integrations/cmdb/assets/{asset_id}
PUT    /api/v1/integrations/cmdb/assets/{asset_id}
DELETE /api/v1/integrations/cmdb/assets/{asset_id}
```

**CMDB → Portal Reconciliation:**
```
GET    /api/v1/integrations/cmdb/reconcile
Returns: List of Portal assets not in CMDB or vice versa
```

---

## 3. Incident Management Integration

### ITIL Incident Management

**Purpose:** Restore normal service operation as quickly as possible

**Integration Scenario:**
When incident occurs, ServiceNow Incident Management needs context about affected data assets

---

### Portal Contribution to Incident Resolution

#### 3.1 Asset Context in Incidents

**Incident Ticket Enrichment:**
When incident references a data asset (e.g., "PROD-HR-DW-v1 data quality issue"):

**Portal Provides:**
1. Asset metadata (owner, version, documentation)
2. Recent changes (last 30 days)
3. Current lifecycle state
4. Known compliance issues
5. Asset dependencies (what else might be affected)

**API Call from ServiceNow:**
```
GET /api/v1/assets/PROD-HR-DW-v1?context=incident

Response:
{
  "asset_name": "PROD-HR-DW-v1",
  "owner": "jsmith@company.com",
  "documentation_url": "https://docs.company.com/hr-dw",
  "lifecycle_stage": "Active",
  "recent_changes": [
    {
      "change_id": "CHG-12345",
      "date": "2026-02-15",
      "description": "Schema update",
      "status": "Completed"
    }
  ],
  "dependencies": ["PROD-HR-ETL-v2"],
  "compliance_issues": []
}
```

---

#### 3.2 Incident-Driven Governance Actions

**Scenario:** Recurring incidents on deprecated asset

**Portal Action:**
1. Detect pattern: Multiple incidents on PROD-HR-REPORT-v1 (Deprecated)
2. Alert Data Steward: "Asset has 5 incidents in 30 days, accelerate retirement"
3. Create automatic change request: "Urgent retirement due to instability"

**Feedback Loop:**
Incident data informs governance decisions (retire problematic assets faster)

---

## 4. Problem Management Integration

### ITIL Problem Management

**Purpose:** Identify and manage root causes of incidents

---

### Portal Contribution

#### 4.1 Root Cause Analysis Support

**Problem Scenario:**
Recurring data quality issues in Finance domain

**Portal Analysis:**
1. Query all FIN domain assets
2. Check compliance status (non-compliant assets = higher defect rate)
3. Review change history (frequent changes without testing = instability)
4. Identify assets without documentation (knowledge gaps)

**Portal Report for Problem Manager:**
```
Root Cause Indicators:
- 3 of 12 FIN assets non-compliant with naming (25%)
- 2 assets missing documentation
- PROD-FIN-ETL-v2 had 7 changes in 30 days (above threshold)
- No assets in Deprecated state (no planned retirements)

Recommendation:
- Enforce naming compliance for FIN domain
- Require documentation for PROD-FIN-ETL-v2
- Implement change freeze for stabilization
```

---

#### 4.2 Known Error Database (KEDB) Link

**Integration:**
- Portal stores KEDB article links in asset metadata
- ServiceNow KEDB references Portal asset IDs
- Bidirectional linking for knowledge sharing

**Example:**
```
Asset: PROD-HR-DW-v1
Known Issues:
  - KEDB0012345: "Slow query performance during payroll processing"
  - KEDB0012789: "Schema migration rollback procedure"
```

---

## 5. Release and Deployment Management Integration

### ITIL Release Management

**Purpose:** Plan, schedule, and control the build, test, and deployment of releases

---

### Portal Integration

#### 5.1 Release Package Tracking

**Release Package Concept:**
Group of related changes deployed together

**Portal Behavior:**
1. Tag assets with release version (e.g., "R2.0")
2. Track all changes in release
3. Provide release readiness checklist

**Release Readiness Checklist (Portal-Driven):**
```
Release R2.0 Readiness:
✓ All assets naming compliant
✓ All assets have documentation
✓ All change requests approved
✓ No deprecated assets in release
✗ Missing: Rollback plan for PROD-FIN-ETL-v2
```

**Portal Blocks Deployment:**
If readiness checklist incomplete, Portal prevents lifecycle transition to Active

---

#### 5.2 Deployment Verification

**Post-Deployment:**
1. Portal verifies asset metadata updated (version incremented)
2. Portal confirms no new compliance violations introduced
3. Portal logs deployment in audit trail

**ServiceNow Receives:**
- Deployment verification status
- Compliance post-check results
- Audit log reference

---

## 6. Service Asset and Configuration Management (SACM)

### ITIL SACM

**Purpose:** Maintain information about configuration items (CIs) throughout their lifecycle

---

### Portal as SACM Tool for Data Assets

**Portal Capabilities:**
1. **Asset Identification:** Unique asset IDs
2. **Asset Control:** Lifecycle management (Draft → Active → Deprecated → Retired)
3. **Asset Verification:** Compliance checks, naming validation
4. **Asset Accounting:** Total assets, by domain, by environment
5. **Asset Auditing:** Full audit trail of all changes

**SACM Metrics (Portal-Driven):**
- Total CIs managed: 127 data assets
- CI accuracy: 95% naming compliant
- CI completeness: 90% documentation coverage
- CI currency: Updated within 90 days

---

## Integration Technologies

### API-Based Integration

**Protocol:** REST API over HTTPS
**Authentication:** OAuth 2.0 or API Key
**Data Format:** JSON

**Sample Integration Flow:**
```
1. Portal creates asset → Triggers webhook
2. Webhook calls ServiceNow API
3. ServiceNow creates CI in CMDB
4. ServiceNow returns CI ID
5. Portal stores CI ID for reference
```

---

### Event-Driven Integration (Future)

**Message Broker:** Apache Kafka or RabbitMQ
**Event Types:**
- `asset.created`
- `asset.updated`
- `asset.deleted`
- `change.approved`
- `lifecycle.transitioned`

**Benefit:**
Decoupled, asynchronous, scalable integration

---

## Integration Governance

### Data Ownership

| Data Element | Owner | Authoritative Source |
|--------------|-------|---------------------|
| Asset Metadata | Portal | DaaS Governance Portal |
| Change Approval | ServiceNow | ServiceNow Change Management |
| Incident Data | ServiceNow | ServiceNow Incident Management |
| CMDB Relationships | CMDB | ServiceNow CMDB |

---

### Sync Conflict Resolution

**Scenario:** Asset updated in both Portal and CMDB

**Resolution Rule:**
1. Portal is authoritative for data assets
2. Last-write-wins for non-conflicting fields
3. Conflicting updates flagged for manual review

**Audit:**
All sync conflicts logged in integration audit table

---

## Integration Testing

### Test Scenarios

1. **Create Asset in Portal → Verify CI Created in CMDB**
2. **Submit Change in Portal → Verify Change Request in ServiceNow**
3. **Approve Change in ServiceNow → Verify Status Updated in Portal**
4. **Incident References Asset → Portal Provides Context**
5. **Sync Failure → Verify Retry Logic and Error Alerting**

---

## Integration Metrics

### Health Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| API Success Rate | >99% | Per integration call |
| Sync Latency | <5 minutes | Time from Portal update to CMDB sync |
| Integration Uptime | >99.5% | Monthly uptime percentage |
| Conflict Rate | <1% | Conflicts per 1000 syncs |

---

## Benefits of ITIL Integration

### Operational Benefits

1. **Single Source of Truth:** Portal + ServiceNow provide complete view
2. **Reduced Manual Work:** Auto-sync eliminates duplicate data entry
3. **Faster Incident Resolution:** Asset context speeds diagnosis
4. **Better Change Success Rate:** Governance checks prevent bad changes
5. **Audit Readiness:** Integrated audit trail across systems

### Strategic Benefits

1. **Service Quality:** Better managed assets = better service quality
2. **Risk Reduction:** Governance controls reduce operational risk
3. **Compliance:** Integrated audit trail supports regulatory compliance
4. **Cost Efficiency:** Automation reduces manual effort
5. **Business Alignment:** Asset governance tied to service delivery

---

## Future Integration Roadmap

### Phase 1 (Current)
- Basic API integration
- Manual sync triggers
- Change request sync

### Phase 2 (Q3 2026)
- Real-time webhooks
- CMDB full sync
- Incident enrichment

### Phase 3 (Q1 2027)
- Event-driven architecture
- Advanced analytics (incident correlation)
- Predictive problem detection

### Phase 4 (Q3 2027)
- AI-powered insights
- Automated remediation
- Self-service portal integration

---

## Approval

**ITIL Integration Approved By:**
- IT Service Manager: ________________________
- Chief Data Officer: ________________________
- ServiceNow Administrator: ________________________

**Effective Date:** March 1, 2026
**Next Review:** September 1, 2026
