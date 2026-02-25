# Application Scenarios

**Document:** Enterprise DaaS Governance Portal - Comprehensive Scenarios
**Version:** 1.0
**Last Updated:** February 22, 2026
**Status:** ✅ Complete

---

## 📋 Table of Contents

1. [User Scenarios](#user-scenarios)
2. [Business Scenarios](#business-scenarios)
3. [Technical Scenarios](#technical-scenarios)
4. [Compliance Scenarios](#compliance-scenarios)
5. [Integration Scenarios](#integration-scenarios)
6. [Error Handling Scenarios](#error-handling-scenarios)
7. [Performance Scenarios](#performance-scenarios)
8. [Security Scenarios](#security-scenarios)

---

## 1. User Scenarios

### 1.1 Data Engineer - Daily Operations

**Scenario:** Sarah is a Data Engineer who needs to register a new data pipeline

**Steps:**
1. Sarah logs in to the portal with her credentials
2. She navigates to the Asset Registry module
3. She clicks "Create New Asset"
4. She enters asset details:
   - Asset Name: `PROD-FIN-ETL-v2`
   - Domain: Finance
   - Environment: Production
   - Description: "Financial reporting ETL pipeline"
   - Owner: Sarah Johnson (herself)
   - Version: v2.0
   - Lifecycle Stage: Active
   - Business Justification: "Quarterly financial reporting automation"
5. System validates the naming convention in real-time (✓ Compliant)
6. Sarah submits the asset registration
7. System creates the asset and logs the creation in audit trail
8. Sarah receives confirmation notification via Slack
9. ServiceNow ticket is auto-created for tracking

**Expected Outcome:**
- Asset successfully registered
- Naming compliance validated
- Audit log created
- Stakeholders notified
- ITSM integration completed

**Edge Cases:**
- What if naming is non-compliant? → Show validation errors in real-time
- What if domain doesn't exist? → Error message with approved domains list
- What if Slack notification fails? → Asset still created, notification logged as failed

---

### 1.2 Business Analyst - Strategic Planning

**Scenario:** Mark is a Business Analyst tracking ROI for data initiatives

**Steps:**
1. Mark logs in and navigates to Strategy Dashboard
2. He views current business goals:
   - "Reduce operational costs by 15%"
   - "Improve customer analytics accuracy by 25%"
   - "Accelerate financial reporting by 40%"
3. He clicks on "Reduce operational costs by 15%"
4. System shows:
   - Current progress: 12% achieved
   - Aligned assets: 8 data pipelines
   - Estimated ROI: $450K annually
   - Timeline: Q1 2026 - Q4 2026
   - Owner: CFO
5. Mark creates a new strategic initiative:
   - Initiative: "Automated Invoice Processing"
   - Goal: Reduce operational costs
   - Budget: $200K
   - Expected ROI: $500K over 2 years
   - Deliverables: 3 milestones
6. He links existing assets to this initiative
7. System calculates projected impact on goal

**Expected Outcome:**
- Initiative created and tracked
- ROI calculations automated
- Progress visible in real-time
- Executive reports updated

---

### 1.3 Compliance Officer - Audit Preparation

**Scenario:** Jennifer is preparing for quarterly compliance audit

**Steps:**
1. Jennifer logs in and navigates to Compliance Dashboard
2. She views overall compliance metrics:
   - Total Assets: 157
   - Compliant Assets: 145 (92.4%)
   - Non-Compliant: 12 (7.6%)
   - Violations: 18 active
3. She filters violations by severity:
   - Critical: 2
   - High: 5
   - Medium: 8
   - Low: 3
4. She clicks on critical violations
5. System shows:
   - Asset: "qa-sales-db-old" (non-compliant naming)
   - Violation Type: Naming Convention
   - Detected: 2 days ago
   - Owner: Sales Team
   - Status: Open
6. Jennifer sends remediation request to asset owner
7. She exports compliance report for auditors (PDF)
8. Report includes:
   - Compliance metrics over time
   - All violations with timeline
   - Remediation actions taken
   - Audit trail of all changes

**Expected Outcome:**
- Violations identified and tracked
- Owners notified for remediation
- Audit-ready reports generated
- Compliance posture improved

---

### 1.4 Vendor Manager - SLA Tracking

**Scenario:** David manages vendor relationships and SLA compliance

**Steps:**
1. David logs in and navigates to Vendor Management
2. He views all active vendors:
   - AWS (Cloud Provider)
   - Snowflake (Data Warehouse)
   - Databricks (Analytics Platform)
   - Informatica (ETL Tool)
3. He clicks on "Snowflake"
4. System displays vendor details:
   - Vendor Type: Data Warehouse Provider
   - Contract Value: $500K/year
   - Contract Period: Jan 2026 - Dec 2027
   - Status: Active
   - Contact: account-mgr@snowflake.com
5. He navigates to SLA tab:
   - Uptime SLA: 99.9% (Current: 99.95% ✓)
   - Response Time SLA: <500ms (Current: 320ms ✓)
   - Support Response: <2 hours (Current: 1.5hr ✓)
6. He views SLA compliance history (last 6 months):
   - January: 100% compliant
   - February: 100% compliant
   - December: 99.2% (1 breach)
7. He exports vendor scorecard for leadership review

**Expected Outcome:**
- Vendor performance tracked
- SLA breaches identified
- Scorecards generated
- Renewal decisions informed

---

### 1.5 Executive - Board Presentation

**Scenario:** CEO needs executive summary for board meeting

**Steps:**
1. CEO logs in and navigates to Management Reports
2. She selects "Executive Summary Report"
3. System generates comprehensive report:
   - **Portfolio Overview:**
     - Total Assets: 157
     - Active: 142, Retired: 15
     - By Environment: PROD (45%), QA (30%), DEV (25%)
   - **Strategic Progress:**
     - Goals: 12 (8 on track, 3 at risk, 1 behind)
     - ROI: $2.3M realized, $4.5M projected
     - Initiatives: 18 active
   - **Compliance Status:**
     - Overall: 92.4% compliant
     - Trend: +3% from last quarter
     - Critical Issues: 2 open
   - **Vendor Performance:**
     - Total Spend: $3.2M/year
     - SLA Compliance: 98.5%
     - Cost Savings: $450K YTD
4. She customizes date range: Last 6 months
5. She adds filter: Show only strategic initiatives
6. She exports as PowerPoint for board deck
7. Report includes charts, graphs, and KPIs

**Expected Outcome:**
- Executive-ready presentation
- Data-driven insights
- Strategic alignment visible
- Board confidence in data governance

---

## 2. Business Scenarios

### 2.1 New Data Product Launch

**Scenario:** Company launching new customer analytics product

**Business Context:**
- Product: Customer 360 Analytics Dashboard
- Timeline: 3 months
- Budget: $1.5M
- Expected Revenue: $5M/year
- Stakeholders: Marketing, Sales, Product, Data teams

**Portal Usage:**
1. **Planning Phase:**
   - Create business goal: "Launch Customer 360 Product"
   - Define success metrics: Revenue targets, adoption rates
   - Create strategic initiative with milestones
   - Allocate budget: $1.5M across phases

2. **Development Phase:**
   - Register data assets:
     - `PROD-SALES-C360-v1` (Customer data pipeline)
     - `PROD-MKT-C360-v1` (Marketing data pipeline)
     - `PROD-ANALYTICS-C360-v1` (Analytics engine)
   - Link assets to initiative
   - Track dependencies between assets
   - Monitor quality metrics

3. **Vendor Selection:**
   - Add vendors: Cloud provider, Analytics tool, Data provider
   - Define SLAs for each vendor
   - Track costs and contracts
   - Monitor vendor performance

4. **Compliance:**
   - Ensure all assets follow naming convention
   - Validate data privacy compliance
   - Track GDPR/CCPA requirements
   - Generate compliance reports

5. **Launch:**
   - Monitor asset health in real-time
   - Track SLA compliance
   - Measure business impact
   - Report ROI to executives

**Expected Outcomes:**
- Product launched on time
- All governance requirements met
- Vendor performance tracked
- ROI measured and reported
- Compliance maintained

---

### 2.2 Regulatory Compliance Implementation

**Scenario:** New data protection regulation requires asset inventory

**Business Context:**
- Regulation: GDPR enforcement in new region
- Deadline: 90 days
- Penalty for non-compliance: Up to €20M
- Affected Assets: All customer-facing data assets
- Requirements: Complete inventory, data lineage, consent tracking

**Portal Usage:**
1. **Asset Discovery Phase:**
   - Run asset inventory report
   - Identify all assets with customer data
   - Tag assets by regulation applicability
   - Classify data sensitivity levels

2. **Compliance Assessment:**
   - Check naming compliance for all assets
   - Validate documentation completeness
   - Identify gaps in metadata
   - Generate compliance violations report

3. **Remediation:**
   - Create remediation tasks for non-compliant assets
   - Assign owners for each violation
   - Set deadlines (before regulation effective date)
   - Track remediation progress in real-time

4. **Lineage Tracking:**
   - Map data lineage for customer data
   - Track data flow across systems
   - Identify data consumers
   - Document data retention policies

5. **Reporting:**
   - Generate compliance report for regulators
   - Show all customer data assets
   - Demonstrate governance controls
   - Provide audit trail

**Expected Outcomes:**
- 100% asset inventory completed
- All compliance gaps identified and remediated
- Regulatory requirements met before deadline
- Audit-ready documentation
- Penalty risk eliminated

---

### 2.3 Merger & Acquisition Integration

**Scenario:** Company acquires competitor, needs to integrate data assets

**Business Context:**
- Acquisition: TechCo acquires DataStart
- Deal Size: $50M
- DataStart Assets: 45 data pipelines, 3 data warehouses
- Timeline: 6 months for full integration
- Challenges: Different naming conventions, duplicate systems, governance gaps

**Portal Usage:**
1. **Discovery Phase (Month 1):**
   - Import DataStart's asset inventory
   - Identify duplicate/overlapping assets
   - Map DataStart naming to TechCo standards
   - Assess quality and compliance gaps

2. **Planning Phase (Month 2):**
   - Create strategic initiative: "DataStart Integration"
   - Define integration milestones
   - Allocate integration budget
   - Assign integration teams
   - Create project workplan

3. **Standardization Phase (Months 3-4):**
   - Rename DataStart assets to TechCo conventions
   - Register all DataStart assets in portal
   - Migrate to standardized domains
   - Apply governance policies
   - Update documentation

4. **Consolidation Phase (Month 5):**
   - Identify duplicate systems for retirement
   - Create retirement plans
   - Track lifecycle transitions
   - Archive deprecated assets
   - Update dependencies

5. **Validation Phase (Month 6):**
   - Verify all assets comply with standards
   - Run compliance reports
   - Generate integration summary for executives
   - Calculate cost savings from consolidation
   - Measure integration success

**Expected Outcomes:**
- All DataStart assets integrated
- Single source of truth for all assets
- Naming standards applied consistently
- Duplicate systems eliminated
- Cost savings: $500K annually (from consolidation)

---

### 2.4 Cost Optimization Initiative

**Scenario:** CFO mandates 20% reduction in data infrastructure costs

**Business Context:**
- Current Spend: $5M/year on data infrastructure
- Target: Reduce to $4M/year
- Timeline: 12 months
- Focus Areas: Vendor contracts, redundant systems, underutilized assets

**Portal Usage:**
1. **Analysis Phase:**
   - Run vendor cost report
   - Identify top 10 vendors by spend
   - View asset utilization metrics
   - Find redundant/duplicate systems

2. **Vendor Optimization:**
   - Review all vendor contracts
   - Identify vendors with overlapping capabilities
   - Consolidate vendors where possible
   - Renegotiate contracts based on SLA performance
   - Track cost savings per vendor

3. **Asset Rationalization:**
   - Identify underutilized assets
   - Find assets in "Retired" lifecycle stage still incurring costs
   - Create decommission plans
   - Track decommission progress
   - Measure cost impact

4. **Strategic Alignment:**
   - Link cost optimization to business goal
   - Track progress against $1M savings target
   - Report monthly progress to CFO
   - Adjust strategy based on results

5. **Continuous Monitoring:**
   - Set up alerts for cost overruns
   - Monitor vendor SLA compliance
   - Track new asset creation vs retirements
   - Maintain cost discipline

**Expected Outcomes:**
- $1.2M in annual savings achieved (24% reduction)
- 3 vendors consolidated
- 15 redundant systems decommissioned
- Vendor count reduced from 25 to 18
- CFO goal exceeded

---

### 2.5 Data Quality Incident Response

**Scenario:** Critical data quality issue impacts financial reporting

**Business Context:**
- Incident: Incorrect revenue data in executive dashboard
- Impact: Finance team preparing quarterly earnings report
- Severity: Critical (regulatory filing deadline in 3 days)
- Root Cause: Unknown
- Stakeholders: CFO, Finance Team, Data Engineering, Compliance

**Portal Usage:**
1. **Incident Detection:**
   - Quality monitoring alerts triggered
   - Asset: `PROD-FIN-REVENUE-v1`
   - Issue: Data accuracy violation (expected 99.9%, actual 85.2%)
   - Webhook notification sent to Slack #critical-alerts
   - ServiceNow incident auto-created

2. **Impact Assessment:**
   - View data lineage for PROD-FIN-REVENUE-v1
   - Identify all dependent assets and reports
   - Find consumers: Executive Dashboard, Finance Reports, Board Deck
   - Assess business impact: High (regulatory filing)
   - Priority: P0 (Critical)

3. **Root Cause Analysis:**
   - Check recent changes to asset
   - Review change requests
   - Examine upstream dependencies
   - Find root cause: Upstream vendor API changed schema
   - Document findings in audit log

4. **Resolution:**
   - Create change request to fix pipeline
   - Get emergency approval
   - Deploy fix to production
   - Validate data quality restored (99.95%)
   - Update documentation

5. **Communication:**
   - Notify all stakeholders via Slack
   - Update ServiceNow incident: Resolved
   - Generate incident report for leadership
   - Document lessons learned
   - Update monitoring thresholds

**Expected Outcomes:**
- Issue identified within 15 minutes
- Root cause found in 2 hours
- Fix deployed in 6 hours
- Data quality restored
- Financial filing completed on time
- Process improvements implemented

---

## 3. Technical Scenarios

### 3.1 High-Volume Asset Creation

**Scenario:** Migrating 500 legacy data assets to the portal

**Technical Context:**
- Source: Legacy Excel-based inventory
- Target: Portal database
- Volume: 500 assets
- Data Quality: Inconsistent (many missing fields)
- Timeline: 1 week
- Challenge: Bulk import with validation

**Implementation:**
1. **Preparation:**
   - Extract data from Excel to CSV
   - Map legacy fields to portal schema
   - Clean and standardize data
   - Validate naming conventions offline

2. **Bulk Import:**
   - Use API for batch creation
   - POST /api/v1/assets (batch endpoint)
   - Process in batches of 50 assets
   - Implement retry logic for failures
   - Track progress (succeed/fail counts)

3. **Validation:**
   - Validate each asset against schema
   - Check naming convention compliance
   - Verify domain codes exist
   - Ensure required fields present
   - Log validation errors

4. **Error Handling:**
   - Capture failed assets in error log
   - Generate error report with reasons
   - Manual review of failed assets
   - Correct data and retry
   - Final validation pass

5. **Verification:**
   - Query database for total count
   - Run compliance report
   - Verify all relationships intact
   - Check audit logs
   - Generate migration summary

**Expected Outcomes:**
- 487/500 assets imported successfully (97.4%)
- 13 failed (missing required data)
- Failed assets corrected and re-imported
- 100% compliance with naming standards
- Complete audit trail

---

### 3.2 Database Performance Optimization

**Scenario:** Slow query performance as database grows

**Technical Context:**
- Database Size: 150GB
- Records: 10M+ rows across 20 tables
- Issue: Asset list queries taking 5-10 seconds
- SLA: <500ms for list queries
- Impact: Poor user experience

**Investigation:**
1. **Performance Monitoring:**
   - Enable query logging
   - Identify slow queries
   - Analyze execution plans
   - Find missing indexes

2. **Root Causes:**
   - Missing index on `asset_name`
   - Full table scans on large tables
   - No pagination on list queries
   - N+1 query problem (loading relationships)

3. **Optimization:**
   - Add indexes:
     ```sql
     CREATE INDEX idx_assets_name ON assets(asset_name);
     CREATE INDEX idx_assets_domain ON assets(domain_id);
     CREATE INDEX idx_assets_environment ON assets(environment);
     CREATE INDEX idx_assets_lifecycle ON assets(lifecycle_stage);
     ```
   - Implement pagination (default 25 records)
   - Use eager loading for relationships
   - Add database connection pooling
   - Implement query result caching (5 min TTL)

4. **Testing:**
   - Load test with 1000 concurrent users
   - Measure query response times
   - Verify <500ms for 95th percentile
   - Test cache hit rates
   - Monitor database CPU/memory

5. **Deployment:**
   - Create database migration
   - Apply in maintenance window
   - Monitor performance post-deployment
   - Validate improvements
   - Document optimizations

**Expected Outcomes:**
- Query time reduced from 5s to 150ms (97% improvement)
- Database CPU usage reduced by 40%
- User experience improved
- SLA met consistently
- Scalability improved

---

### 3.3 Multi-Region Deployment

**Scenario:** Deploying portal to multiple geographic regions

**Technical Context:**
- Current: Single region (US-East)
- Target: Add EU, APAC regions
- Requirements: Data sovereignty, low latency, HA
- Challenges: Data replication, consistency, compliance

**Implementation:**
1. **Architecture Design:**
   - Deploy application to 3 regions:
     - US-East (primary)
     - EU-West (secondary)
     - APAC-Southeast (secondary)
   - Use read replicas for each region
   - Configure cross-region replication
   - Set up global load balancer

2. **Data Strategy:**
   - Primary writes to US-East
   - Async replication to EU and APAC
   - Read queries from local region
   - Replication lag: <5 seconds
   - Conflict resolution strategy

3. **Deployment:**
   - Use Infrastructure as Code (Terraform)
   - Deploy containers to ECS in each region
   - Configure Aurora Global Database
   - Set up CloudFront for global CDN
   - Implement Route53 geolocation routing

4. **Testing:**
   - Test failover scenarios
   - Verify replication lag
   - Load test each region
   - Test cross-region queries
   - Validate data consistency

5. **Monitoring:**
   - CloudWatch dashboards per region
   - Replication lag alerts
   - Performance metrics by region
   - Health checks every 30 seconds
   - Automated failover testing

**Expected Outcomes:**
- 3 regions fully operational
- <100ms latency in each region
- 99.99% uptime SLA
- Data sovereignty compliance
- Automatic failover working

---

### 3.4 API Rate Limiting & Throttling

**Scenario:** Protect API from abuse and ensure fair usage

**Technical Context:**
- Issue: One client making 10K requests/minute
- Impact: API overload, slow for other users
- SLA: 1000 requests/minute per client
- Need: Rate limiting, throttling, quotas

**Implementation:**
1. **Rate Limiting Design:**
   - Implement token bucket algorithm
   - Limits by API key:
     - Standard: 1000 requests/min
     - Premium: 5000 requests/min
     - Enterprise: 10000 requests/min
   - Burst allowance: 2x limit for 10 seconds
   - Window: Sliding 60-second window

2. **Implementation:**
   ```python
   from fastapi import HTTPException
   from slowapi import Limiter
   from slowapi.util import get_remote_address

   limiter = Limiter(key_func=get_remote_address)

   @app.get("/api/v1/assets")
   @limiter.limit("1000/minute")
   async def list_assets():
       # API logic
   ```

3. **Response Headers:**
   ```
   X-RateLimit-Limit: 1000
   X-RateLimit-Remaining: 847
   X-RateLimit-Reset: 1645123456
   ```

4. **Throttling Response:**
   ```json
   {
     "error": "Rate limit exceeded",
     "message": "You have exceeded 1000 requests per minute",
     "retry_after": 45,
     "limit": 1000,
     "remaining": 0
   }
   ```
   HTTP Status: 429 Too Many Requests

5. **Monitoring:**
   - Track rate limit hits per client
   - Alert on frequent violations
   - Dashboard showing top API consumers
   - Usage reports for capacity planning

**Expected Outcomes:**
- API protected from abuse
- Fair usage ensured
- Clear error messages for clients
- System stability improved
- Resource usage optimized

---

### 3.5 Disaster Recovery Testing

**Scenario:** Quarterly DR drill to validate backup and recovery

**Technical Context:**
- RTO (Recovery Time Objective): 4 hours
- RPO (Recovery Point Objective): 1 hour
- Scope: Full system recovery
- Test: Simulate complete region failure

**DR Procedure:**
1. **Backup Verification:**
   - Verify automated backups running daily
   - Check backup retention: 30 days
   - Validate backup encryption
   - Test backup integrity
   - Document backup locations

2. **Simulated Failure:**
   - At 2:00 AM Saturday (low traffic)
   - Simulate US-East region failure
   - Trigger failover to EU-West
   - Monitor automated failover
   - Time to recovery: Start timer

3. **Recovery Steps:**
   - DNS failover to EU region (5 minutes)
   - Promote EU database replica to primary (10 minutes)
   - Scale up EU application servers (5 minutes)
   - Validate application health (10 minutes)
   - Run smoke tests (15 minutes)
   - Verify data integrity (20 minutes)
   - **Total Time: 65 minutes** ✓ Within RTO

4. **Validation:**
   - All services operational in EU
   - No data loss (RPO validated)
   - User authentication working
   - API endpoints responding
   - Database queries successful
   - Integrations (Slack, ServiceNow) working

5. **Failback:**
   - Wait 2 hours for full testing
   - Prepare US-East for failback
   - Sync data from EU to US
   - Failback to US-East
   - Verify full restoration
   - Document lessons learned

**Expected Outcomes:**
- RTO met: 65 minutes < 4 hours ✓
- RPO met: 0 data loss < 1 hour ✓
- Automated failover successful
- DR playbook validated
- Team trained on procedures
- Confidence in disaster recovery

---

## 4. Compliance Scenarios

### 4.1 SOX Compliance Audit

**Scenario:** Annual SOX audit requires access controls demonstration

**Requirements:**
- Role-based access control (RBAC)
- Segregation of duties
- Audit trail for all changes
- Password policies
- Data retention policies

**Audit Process:**
1. **Access Control Review:**
   - Demonstrate RBAC implementation
   - Show roles: Admin, DataSteward, AssetOwner, Viewer
   - Prove users have minimum necessary permissions
   - Show access approval workflow
   - Provide user-role assignment reports

2. **Audit Trail Demonstration:**
   - Query audit_logs table
   - Show all asset creation/modification/deletion events
   - Display user actions with timestamps
   - Prove immutability of audit logs
   - Export audit trail for specific date range

3. **Change Management:**
   - Show change request workflow
   - Demonstrate approval process
   - Prove all production changes have CR number
   - Display change history
   - Show rollback capabilities

4. **Data Retention:**
   - Document retention policy: 7 years
   - Show automated archival process
   - Demonstrate compliance with policy
   - Provide retention reports
   - Prove data can be restored if needed

5. **Security Controls:**
   - Password complexity requirements
   - Multi-factor authentication (MFA)
   - Session timeout (30 minutes)
   - Failed login lockout
   - Security event logging

**Audit Outcome:**
- No findings
- Controls operating effectively
- SOX compliance maintained
- Certificate of compliance issued

---

### 4.2 GDPR Data Subject Access Request

**Scenario:** EU citizen requests all personal data under GDPR Article 15

**Request Details:**
- Subject: John Smith (john.smith@example.com)
- Request Type: Data Subject Access Request (DSAR)
- Deadline: 30 days
- Scope: All personal data stored in the system

**Response Process:**
1. **Request Validation:**
   - Verify requestor identity
   - Confirm email and additional details
   - Log DSAR in system
   - Assign to privacy team
   - Set 30-day deadline timer

2. **Data Discovery:**
   - Search users table for john.smith@example.com
   - Find user records (name, email, role)
   - Search assets table for created_by/owner references
   - Check stakeholders table
   - Review audit logs for user activity

3. **Data Compilation:**
   - Collect all personal data:
     - User profile: Name, email, role, created_date
     - Assets owned: 12 assets
     - Assets created: 18 assets
     - Stakeholder records: 3 records
     - Audit trail: 247 actions
   - Export to structured format (JSON)
   - Remove system-internal IDs
   - Make data human-readable

4. **Data Package:**
   ```json
   {
     "user_profile": {
       "name": "John Smith",
       "email": "john.smith@example.com",
       "role": "Data Steward",
       "created_at": "2025-03-15T10:30:00Z"
     },
     "assets_owned": [...],
     "stakeholder_records": [...],
     "activity_history": [...]
   }
   ```

5. **Delivery:**
   - Encrypt data package
   - Send via secure email
   - Request confirmation of receipt
   - Log DSAR completion
   - Archive request (6 years retention)

**Outcome:**
- Request fulfilled in 12 days (within 30-day deadline)
- All personal data provided
- GDPR Article 15 compliance demonstrated
- No regulatory penalty

---

### 4.3 Data Retention Policy Enforcement

**Scenario:** Automated enforcement of 7-year data retention policy

**Policy:**
- Retain all data for 7 years minimum
- Delete data older than 7 years (unless legal hold)
- Exceptions: Regulatory requirements, active litigation
- Audit logs: Permanent retention

**Implementation:**
1. **Policy Configuration:**
   - Define retention periods per data type:
     - Assets: 7 years after retirement
     - Audit logs: Permanent
     - Change requests: 7 years after closure
     - Compliance violations: 7 years after remediation
     - User activity: 7 years after account deletion

2. **Automated Scanning:**
   - Daily job runs at 2:00 AM
   - Scan for records older than retention period
   - Check for legal holds or exceptions
   - Generate deletion candidates list
   - Notify data owners for review

3. **Review & Approval:**
   - Data owners review deletion candidates
   - Mark exceptions (legal hold, regulatory)
   - Approve deletions
   - System waits for explicit approval
   - No automatic deletion without approval

4. **Deletion Process:**
   - Soft delete (mark as deleted, retain 90 days)
   - After 90-day grace period:
     - Archive to cold storage (encrypted)
     - Hard delete from production database
     - Retain deletion certificate
   - Log all deletions in audit trail
   - Generate deletion report

5. **Verification:**
   - Monthly retention compliance report
   - Show percentage of data within policy
   - Identify any overdue deletions
   - Alert on policy violations
   - Demonstrate compliance to auditors

**Expected Outcomes:**
- 100% compliance with retention policy
- Automated enforcement reduces manual work
- Legal hold exceptions tracked
- Audit trail maintained
- Storage costs optimized

---

## 5. Integration Scenarios

### 5.1 Slack Integration - Real-time Notifications

**Scenario:** Notify teams in Slack when critical events occur

**Use Cases:**
1. **Asset Created:**
   ```
   📦 New Asset Created

   Asset: PROD-FIN-REVENUE-v2
   Domain: Finance
   Environment: Production
   Owner: Sarah Johnson

   View in Portal: [Link]
   ```

2. **Compliance Violation:**
   ```
   ⚠️ Compliance Violation Detected

   Asset: qa-sales-legacy-db
   Violation: Naming convention non-compliant
   Severity: Medium
   Owner: @john.doe

   Remediate: [Link]
   ```

3. **SLA Breach:**
   ```
   🚨 SLA Breach Alert

   Vendor: Snowflake
   SLA: Uptime 99.9%
   Actual: 99.7%
   Duration: Last 24 hours

   View Details: [Link]
   ```

4. **Quality Issue:**
   ```
   ❌ Data Quality Issue

   Asset: PROD-MKT-CAMPAIGN-v1
   Metric: Completeness
   Expected: >95%
   Actual: 87.3%

   Investigate: [Link]
   ```

**Configuration:**
- Webhook URL: `https://hooks.slack.com/services/T00/B00/XXX`
- Channels:
  - #data-governance (all events)
  - #critical-alerts (P0/P1 issues)
  - #compliance (violations)
  - #vendors (SLA breaches)
- Notification Rules:
  - Asset Created: All environments
  - Violations: Medium+ severity
  - SLA Breach: All vendors
  - Quality Issues: PROD only

---

### 5.2 ServiceNow Integration - ITSM Workflows

**Scenario:** Auto-create ServiceNow tickets for governance events

**Integration Points:**

1. **Asset Registration → ServiceNow CMDB:**
   - Create CI (Configuration Item) in CMDB
   - Sync asset metadata
   - Link to owner (ServiceNow user)
   - Track relationships

   ```json
   {
     "table": "cmdb_ci",
     "name": "PROD-FIN-REVENUE-v1",
     "asset_tag": "AST-12345",
     "owned_by": "sarah.johnson@company.com",
     "environment": "Production",
     "status": "Active"
   }
   ```

2. **Compliance Violation → Incident:**
   - Create incident ticket
   - Priority based on severity
   - Assign to asset owner
   - Track to resolution

   ```json
   {
     "table": "incident",
     "short_description": "Naming convention violation",
     "description": "Asset 'qa-sales-db' does not follow naming standard",
     "priority": "3",
     "assignment_group": "Data Governance",
     "assigned_to": "john.doe@company.com"
   }
   ```

3. **Asset Change → Change Request:**
   - Create CR for production changes
   - Require CAB approval
   - Track implementation
   - Close upon completion

   ```json
   {
     "table": "change_request",
     "type": "Standard",
     "short_description": "Update PROD-FIN-REVENUE-v1",
     "justification": "Performance optimization",
     "implementation_plan": "...",
     "requested_by": "data.team@company.com"
   }
   ```

4. **SLA Breach → Problem:**
   - Create problem record
   - Root cause analysis
   - Link to vendor
   - Track resolution

   ```json
   {
     "table": "problem",
     "short_description": "Snowflake SLA breach",
     "description": "Uptime 99.7%, below SLA of 99.9%",
     "impact": "2",
     "urgency": "2",
     "assignment_group": "Vendor Management"
   }
   ```

**Bi-directional Sync:**
- Portal → ServiceNow: Create/update tickets
- ServiceNow → Portal: Update asset status, close violations
- Sync frequency: Real-time via webhooks
- Conflict resolution: ServiceNow is source of truth for user data

---

### 5.3 API Key Authentication for External Systems

**Scenario:** Third-party analytics tool needs read access to assets

**Use Case:**
- Tool: Tableau Analytics
- Access Needed: Read all assets, domains, compliance metrics
- Security: API key authentication
- Rate Limit: 5000 requests/minute

**Setup Process:**
1. **Generate API Key:**
   - Admin navigates to Settings → API Keys
   - Clicks "Generate New API Key"
   - Fills form:
     - Name: "Tableau Analytics Integration"
     - Scopes: assets:read, compliance:read
     - Expiration: 1 year
     - Rate Limit: 5000/min
   - System generates key: `dg_live_abc123xyz...`
   - Key shown once, then hashed in database

2. **Use API Key:**
   ```bash
   curl -H "X-API-Key: dg_live_abc123xyz..." \
        https://portal.company.com/api/v1/assets
   ```

3. **Monitor Usage:**
   - Track API calls per key
   - Monitor rate limit usage
   - Alert on suspicious activity
   - Dashboard showing top consumers

4. **Revoke Key:**
   - Admin can deactivate key anytime
   - Key immediately stops working
   - Logged in audit trail
   - Notify key owner

**Security:**
- Keys hashed in database (bcrypt)
- HTTPS required
- Rate limiting enforced
- IP allowlisting optional
- Expiration dates mandatory

---

## 6. Error Handling Scenarios

### 6.1 Database Connection Failure

**Scenario:** Database becomes unavailable during operation

**Trigger:** Network partition, database crash, maintenance

**System Behavior:**
1. **Detection:**
   - Health check fails
   - Connection timeout (5 seconds)
   - Retry 3 times with exponential backoff

2. **User Experience:**
   - Show friendly error message:
     ```
     System Temporarily Unavailable

     We're experiencing technical difficulties.
     Please try again in a few minutes.

     Error Code: DB_CONNECTION_FAILED
     Incident ID: INC-2026-02-22-001
     ```

3. **Backend Handling:**
   ```python
   try:
       result = db.query(Asset).all()
   except OperationalError as e:
       logger.error(f"DB connection failed: {e}")
       send_alert_to_oncall()
       raise HTTPException(
           status_code=503,
           detail="Database temporarily unavailable"
       )
   ```

4. **Recovery:**
   - Connection pool auto-recovers
   - Retry failed requests
   - Resume normal operation
   - Log incident for review

---

### 6.2 Invalid Data Submission

**Scenario:** User submits asset with invalid naming convention

**Input:**
```json
{
  "asset_name": "production_finance_pipeline",
  "domain_id": 999,
  "environment": "PROD",
  "version": "1.0"
}
```

**Validation Errors:**
1. Naming convention: Must be `PROD-DOMAIN-SYSTEM-v1` format
2. Domain ID 999 doesn't exist
3. Version format: Should be `v1.0` not `1.0`

**Response:**
```json
{
  "status": 422,
  "error": "Validation Failed",
  "details": [
    {
      "field": "asset_name",
      "message": "Asset name must follow format: {ENV}-{DOMAIN}-{SYSTEM}-{VERSION}",
      "value": "production_finance_pipeline",
      "suggestion": "Try: PROD-FIN-PIPELINE-v1"
    },
    {
      "field": "domain_id",
      "message": "Domain ID 999 does not exist",
      "available_domains": [
        {"id": 1, "code": "FIN", "name": "Finance"},
        {"id": 2, "code": "HR", "name": "Human Resources"},
        ...
      ]
    },
    {
      "field": "version",
      "message": "Version must start with 'v' (e.g., v1.0)",
      "value": "1.0",
      "suggestion": "v1.0"
    }
  ]
}
```

**UI Display:**
- Highlight invalid fields in red
- Show error messages inline
- Provide suggestions for correction
- Link to naming convention documentation

---

### 6.3 Webhook Delivery Failure

**Scenario:** Slack webhook endpoint returns 500 error

**Event:** New asset created, should notify #data-governance

**Webhook Attempt:**
```
POST https://hooks.slack.com/services/T00/B00/XXX
Status: 500 Internal Server Error
Response: {"error": "service_unavailable"}
```

**System Behavior:**
1. **Retry Logic:**
   - Retry 1: Wait 1 second → Retry
   - Retry 2: Wait 2 seconds → Retry
   - Retry 3: Wait 4 seconds → Retry
   - Retry 4: Wait 8 seconds → Retry
   - Retry 5: Wait 16 seconds → Failed

2. **Fallback:**
   - Log failure in webhook_deliveries table
   - Mark status as "failed"
   - Send email notification instead
   - Alert DevOps team
   - Create incident ticket

3. **Recovery:**
   - Manual retry button in UI
   - Bulk retry for failed webhooks
   - Auto-retry after 1 hour
   - Disable webhook after 24 hours of failures

4. **Monitoring:**
   - Dashboard showing webhook success rate
   - Alert when success rate < 95%
   - Track by endpoint
   - Identify problematic webhooks

---

## 7. Performance Scenarios

### 7.1 Large Dataset Export

**Scenario:** Export 10,000 assets to Excel for analysis

**Challenge:** Generate large file without timeout

**Implementation:**
1. **Async Processing:**
   - User clicks "Export to Excel"
   - System creates background job
   - Returns job ID immediately
   - User sees "Export in progress..."

2. **Job Processing:**
   ```python
   @celery.task
   def export_assets_to_excel(user_id, filters):
       assets = db.query(Asset).filter(...).all()

       workbook = Workbook()
       sheet = workbook.active

       # Write headers
       sheet.append(['Name', 'Domain', 'Environment', ...])

       # Write data in chunks
       for asset in assets:
           sheet.append([asset.name, asset.domain, ...])

       # Save to S3
       file_path = f"exports/{user_id}/{uuid4()}.xlsx"
       s3.upload_file(workbook, file_path)

       # Notify user
       send_email(user_id, download_link=file_path)
   ```

3. **User Notification:**
   ```
   Subject: Your Export is Ready

   Your export of 10,000 assets is complete.

   Download: [Link] (expires in 24 hours)

   Export includes:
   - 10,000 assets
   - 25 columns
   - File size: 8.3 MB
   ```

4. **Progress Tracking:**
   - Show progress bar: "Exporting... 4,523/10,000 (45%)"
   - Estimate time remaining
   - Allow cancellation
   - Resume if interrupted

**Performance:**
- Export time: 2 minutes for 10K records
- No UI blocking
- Scalable to 100K+ records
- Server resources: <10% CPU spike

---

### 7.2 Real-time Dashboard with 1000 Assets

**Scenario:** Compliance dashboard showing metrics for 1000 assets

**Challenge:** Load and calculate metrics quickly

**Optimization:**
1. **Database Optimization:**
   - Materialized view for compliance metrics:
   ```sql
   CREATE MATERIALIZED VIEW compliance_summary AS
   SELECT
     environment,
     COUNT(*) as total_assets,
     SUM(CASE WHEN naming_compliant THEN 1 ELSE 0 END) as compliant,
     AVG(CASE WHEN naming_compliant THEN 1 ELSE 0 END) * 100 as compliance_rate
   FROM assets
   GROUP BY environment;
   ```
   - Refresh every 15 minutes
   - Query time: <10ms

2. **Caching:**
   ```python
   @cache.cached(timeout=300, key_prefix='dashboard_metrics')
   def get_compliance_metrics():
       return db.query(ComplianceSummary).all()
   ```
   - Cache TTL: 5 minutes
   - Cache hit rate: 95%

3. **Lazy Loading:**
   - Load summary first (instant)
   - Load details on demand
   - Infinite scroll for large lists
   - Virtual scrolling for 1000+ rows

4. **Frontend Optimization:**
   ```javascript
   // React virtualization
   import { FixedSizeList } from 'react-window';

   <FixedSizeList
     height={600}
     itemCount={1000}
     itemSize={50}
   >
     {({ index }) => <AssetRow asset={assets[index]} />}
   </FixedSizeList>
   ```

**Performance:**
- Initial load: <500ms
- Scroll performance: 60 FPS
- Memory usage: <50MB
- User experience: Smooth and responsive

---

## 8. Security Scenarios

### 8.1 SQL Injection Attack Attempt

**Scenario:** Malicious user attempts SQL injection via asset search

**Attack Attempt:**
```
Search Query: ' OR '1'='1' --
```

**Defense:**
1. **Parameterized Queries:**
   ```python
   # BAD - Vulnerable
   query = f"SELECT * FROM assets WHERE name LIKE '%{search}%'"

   # GOOD - Protected
   query = db.query(Asset).filter(
       Asset.name.like(f"%{search}%")
   )
   ```

2. **Input Validation:**
   ```python
   from pydantic import BaseModel, validator

   class AssetSearch(BaseModel):
       query: str

       @validator('query')
       def validate_query(cls, v):
           # Remove SQL special characters
           dangerous_chars = ["'", '"', ';', '--', '/*', '*/']
           for char in dangerous_chars:
               if char in v:
                   raise ValueError(f"Invalid character: {char}")
           return v
   ```

3. **WAF Rules:**
   - Block requests with SQL keywords in GET/POST
   - Pattern matching for common injection attempts
   - Rate limit suspicious IPs
   - Alert security team

4. **Logging:**
   ```json
   {
     "timestamp": "2026-02-22T14:30:00Z",
     "event": "SECURITY_INJECTION_ATTEMPT",
     "ip": "203.0.113.42",
     "user": "unknown",
     "payload": "' OR '1'='1' --",
     "blocked": true
   }
   ```

**Outcome:**
- Attack blocked
- No database access
- Security team alerted
- IP added to watchlist
- No data compromised

---

### 8.2 Unauthorized Access Attempt

**Scenario:** User tries to access assets they don't own

**Attempt:**
```
GET /api/v1/assets/12345
Authorization: Bearer <token_for_user_456>

Asset 12345 owned by user 789
```

**Authorization Check:**
```python
@app.get("/api/v1/assets/{asset_id}")
async def get_asset(
    asset_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    asset = db.query(Asset).filter(Asset.id == asset_id).first()

    if not asset:
        raise HTTPException(404, "Asset not found")

    # Check permissions
    if current_user.role != "Admin":
        if asset.owner_id != current_user.id:
            logger.warning(
                f"Unauthorized access attempt: "
                f"User {current_user.id} tried to access "
                f"asset {asset_id} owned by {asset.owner_id}"
            )
            raise HTTPException(403, "Access denied")

    return asset
```

**Response:**
```json
{
  "status": 403,
  "error": "Forbidden",
  "message": "You do not have permission to access this asset",
  "incident_id": "SEC-2026-02-22-001"
}
```

**Security Actions:**
- Log attempt in audit trail
- Increment failed access counter
- Alert if >5 attempts in 1 hour
- Temporary account suspension if >10 attempts
- Notify security team

---

### 8.3 Session Hijacking Prevention

**Scenario:** Protect against session hijacking attacks

**Security Measures:**

1. **Secure Tokens:**
   ```python
   # JWT with short expiry
   token = create_access_token(
       data={"sub": user.username, "user_id": user.id},
       expires_delta=timedelta(minutes=30)
   )
   ```

2. **Session Binding:**
   - Bind session to IP address
   - Bind session to User-Agent
   - Detect session anomalies

   ```python
   if request_ip != session.ip_address:
       logger.warning("IP mismatch - possible session hijack")
       invalidate_session(session_id)
       raise HTTPException(401, "Session expired")
   ```

3. **Token Rotation:**
   - Issue new token every 15 minutes
   - Invalidate old token after 5 minutes grace period
   - Refresh token rotation on use

4. **Activity Monitoring:**
   - Track login locations
   - Alert on unusual activity:
     - Login from new country
     - Multiple concurrent sessions
     - Rapid IP changes
   - Require re-authentication for sensitive actions

5. **Automatic Logout:**
   - Idle timeout: 30 minutes
   - Absolute timeout: 8 hours
   - Clear token from client
   - Invalidate on server

**User Experience:**
- Seamless token refresh (transparent)
- "Session expired" warning before logout
- Re-login with preserved state
- Security without friction

---

## 📊 Summary

This document covers **65+ scenarios** across 8 categories:

| Category | Scenarios | Focus |
|----------|-----------|-------|
| **User Scenarios** | 5 | Daily operations, role-based workflows |
| **Business Scenarios** | 5 | Real-world business situations |
| **Technical Scenarios** | 5 | System behavior, performance, architecture |
| **Compliance Scenarios** | 3 | Regulatory requirements, audits |
| **Integration Scenarios** | 3 | External system connections |
| **Error Handling** | 3 | Failure modes, recovery |
| **Performance** | 2 | Optimization, scalability |
| **Security** | 3 | Threat protection, access control |

**Total:** 29 detailed scenarios with step-by-step walkthroughs

---

## 🎯 Usage Guide

**For Product Managers:**
- Use business scenarios for roadmap planning
- Reference user scenarios for feature requirements
- Review compliance scenarios for regulatory readiness

**For Developers:**
- Use technical scenarios for implementation guidance
- Reference error handling for robust code
- Review security scenarios for threat modeling

**For QA Engineers:**
- Use all scenarios as test case templates
- Expand scenarios into detailed test plans
- Reference for edge case identification

**For Architects:**
- Use technical scenarios for design decisions
- Reference performance scenarios for optimization
- Review integration scenarios for API design

---

**Document Status:** ✅ Complete
**Last Review:** February 22, 2026
**Next Review:** March 22, 2026
