# Database Schema
## Enterprise DaaS Governance Portal

**Version:** 2.0
**Date:** February 2026

---

## Schema Overview

The database schema is designed to support:
- Asset lifecycle management with full audit trail
- Naming convention enforcement
- Change management workflow
- Compliance tracking and reporting
- Role-based access control
- **Strategic DaaS initiatives and business goal alignment** (v2.0)
- **Vendor management and SLA tracking** (v2.0)
- **Budget tracking and financial management** (v2.0)
- **Stakeholder engagement and data needs tracking** (v2.0)
- **Executive reporting and governance maturity assessment** (v2.0)

**Database Engine:** SQLite 3.44+ (prototype), PostgreSQL 15+ (production)

**Schema Statistics:**
- **Total Tables:** 20 (9 core + 11 strategic)
- **Total Indexes:** 45+
- **Total Views:** 3
- **Foreign Key Relationships:** 25+

---

## Entity Relationship Diagram

```
┌─────────────┐         ┌─────────────┐         ┌─────────────┐
│   domains   │         │    users    │         │    roles    │
│─────────────│         │─────────────│         │─────────────│
│ domain_id PK│         │ user_id  PK │         │ role_id  PK │
│ name        │         │ username    │         │ role_name   │
│ description │         │ email       │         │ permissions │
│ active      │         │ role_id  FK │◀────────┤ description │
└──────┬──────┘         │ created_at  │         └─────────────┘
       │                └──────┬──────┘
       │                       │
       │                       │ owner_id
       │                       │
       │                       ▼
       │                ┌─────────────────────┐
       │ domain_id      │       assets        │
       └───────────────▶│─────────────────────│
                        │ asset_id         PK │
                        │ asset_name          │
                        │ domain_id        FK │
                        │ environment         │
                        │ owner_id         FK │
                        │ version             │
                        │ lifecycle_stage     │
                        │ documentation_url   │
                        │ description         │
                        │ naming_compliant    │
                        │ created_at          │
                        │ updated_at          │
                        └──────┬──────────────┘
                               │
            ┌──────────────────┼──────────────────┐
            │                  │                  │
            ▼                  ▼                  ▼
   ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
   │lifecycle_history│ │ change_requests │ │compliance_viol. │
   │─────────────────│ │─────────────────│ │─────────────────│
   │ history_id   PK │ │ change_id    PK │ │ violation_id PK │
   │ asset_id     FK │ │ asset_id     FK │ │ asset_id     FK │
   │ from_state      │ │ title           │ │ violation_type  │
   │ to_state        │ │ risk_level      │ │ severity        │
   │ changed_by   FK │ │ status          │ │ detected_at     │
   │ reason          │ │ requested_by FK │ │ resolved_at     │
   │ changed_at      │ │ approved_by  FK │ │ details         │
   └─────────────────┘ │ requested_at    │ └─────────────────┘
                       └─────────────────┘

                        ┌─────────────────┐
                        │   audit_logs    │
                        │─────────────────│
                        │ log_id       PK │
                        │ user_id      FK │
                        │ action          │
                        │ entity_type     │
                        │ entity_id       │
                        │ old_value       │
                        │ new_value       │
                        │ timestamp       │
                        │ ip_address      │
                        └─────────────────┘
```

---

## Table Definitions

### 1. users

**Purpose:** Store user accounts and authentication information.

```sql
CREATE TABLE users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(100) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    role_id INTEGER NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    FOREIGN KEY (role_id) REFERENCES roles(role_id)
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role_id);
```

**Sample Data:**
```sql
INSERT INTO users (username, email, password_hash, first_name, last_name, role_id)
VALUES
    ('admin', 'admin@company.com', '$2b$12$...', 'System', 'Admin', 1),
    ('jdoe', 'jdoe@company.com', '$2b$12$...', 'John', 'Doe', 2);
```

---

### 2. roles

**Purpose:** Define user roles and permissions.

```sql
CREATE TABLE roles (
    role_id INTEGER PRIMARY KEY AUTOINCREMENT,
    role_name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    permissions TEXT, -- JSON array of permissions
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Sample Data:**
```sql
INSERT INTO roles (role_name, description, permissions) VALUES
    ('Admin', 'Full system access', '["*"]'),
    ('DataSteward', 'Governance and approval authority', '["asset:*", "change:approve", "compliance:view"]'),
    ('AssetOwner', 'Manage owned assets', '["asset:create", "asset:update", "asset:view"]'),
    ('Viewer', 'Read-only access', '["asset:view", "compliance:view"]');
```

---

### 3. domains

**Purpose:** Define approved business domains for naming convention.

```sql
CREATE TABLE domains (
    domain_id INTEGER PRIMARY KEY AUTOINCREMENT,
    domain_code VARCHAR(10) NOT NULL UNIQUE, -- e.g., HR, FIN
    domain_name VARCHAR(100) NOT NULL,
    description TEXT,
    data_steward_id INTEGER,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (data_steward_id) REFERENCES users(user_id)
);
```

**Sample Data:**
```sql
INSERT INTO domains (domain_code, domain_name, description, is_active) VALUES
    ('HR', 'Human Resources', 'Employee and workforce management data', TRUE),
    ('FIN', 'Finance', 'Financial transactions and accounting data', TRUE),
    ('OPS', 'Operations', 'Operational and logistics data', TRUE),
    ('SALES', 'Sales', 'Sales and customer relationship data', TRUE),
    ('IT', 'Information Technology', 'IT infrastructure and systems data', TRUE),
    ('DATA', 'Data Platform', 'Enterprise data platform assets', TRUE);
```

---

### 4. assets

**Purpose:** Core table storing all registered data and platform assets.

```sql
CREATE TABLE assets (
    asset_id INTEGER PRIMARY KEY AUTOINCREMENT,
    asset_name VARCHAR(255) NOT NULL UNIQUE,
    domain_id INTEGER NOT NULL,
    environment VARCHAR(10) NOT NULL CHECK (environment IN ('DEV', 'QA', 'PROD', 'UAT')),
    owner_id INTEGER NOT NULL,
    version VARCHAR(20) NOT NULL,
    lifecycle_stage VARCHAR(20) NOT NULL CHECK (lifecycle_stage IN ('Draft', 'Active', 'Deprecated', 'Retired')),
    documentation_url VARCHAR(500),
    description TEXT,
    business_justification TEXT,
    tags TEXT, -- JSON array
    naming_compliant BOOLEAN DEFAULT FALSE,
    compliance_check_date TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_by INTEGER,
    FOREIGN KEY (domain_id) REFERENCES domains(domain_id),
    FOREIGN KEY (owner_id) REFERENCES users(user_id),
    FOREIGN KEY (created_by) REFERENCES users(user_id),
    FOREIGN KEY (updated_by) REFERENCES users(user_id)
);

CREATE INDEX idx_assets_name ON assets(asset_name);
CREATE INDEX idx_assets_domain ON assets(domain_id);
CREATE INDEX idx_assets_lifecycle ON assets(lifecycle_stage);
CREATE INDEX idx_assets_environment ON assets(environment);
CREATE INDEX idx_assets_owner ON assets(owner_id);
CREATE INDEX idx_assets_compliant ON assets(naming_compliant);
```

**Sample Data:**
```sql
INSERT INTO assets (asset_name, domain_id, environment, owner_id, version, lifecycle_stage,
                    documentation_url, description, naming_compliant, created_by)
VALUES
    ('PROD-HR-DW-v1', 1, 'PROD', 2, 'v1.0', 'Active',
     'https://docs.company.com/hr-dw', 'HR Data Warehouse', TRUE, 1),
    ('QA-FIN-ETL-v2', 2, 'QA', 2, 'v2.1', 'Active',
     'https://docs.company.com/fin-etl', 'Finance ETL Pipeline', TRUE, 1);
```

---

### 5. lifecycle_history

**Purpose:** Track all lifecycle state transitions for audit trail.

```sql
CREATE TABLE lifecycle_history (
    history_id INTEGER PRIMARY KEY AUTOINCREMENT,
    asset_id INTEGER NOT NULL,
    from_state VARCHAR(20),
    to_state VARCHAR(20) NOT NULL,
    changed_by INTEGER NOT NULL,
    change_reason TEXT NOT NULL,
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (asset_id) REFERENCES assets(asset_id) ON DELETE CASCADE,
    FOREIGN KEY (changed_by) REFERENCES users(user_id)
);

CREATE INDEX idx_lifecycle_asset ON lifecycle_history(asset_id);
CREATE INDEX idx_lifecycle_date ON lifecycle_history(changed_at);
```

**Sample Data:**
```sql
INSERT INTO lifecycle_history (asset_id, from_state, to_state, changed_by, change_reason)
VALUES
    (1, 'Draft', 'Active', 1, 'Passed UAT, ready for production'),
    (2, 'Active', 'Deprecated', 1, 'Replaced by v3.0 pipeline');
```

---

### 6. change_requests

**Purpose:** Track change management requests linked to assets.

```sql
CREATE TABLE change_requests (
    change_id INTEGER PRIMARY KEY AUTOINCREMENT,
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    asset_id INTEGER NOT NULL,
    change_type VARCHAR(50) NOT NULL CHECK (change_type IN ('Modify', 'Deploy', 'Decommission', 'Config')),
    risk_level VARCHAR(20) NOT NULL CHECK (risk_level IN ('Low', 'Medium', 'High', 'Critical')),
    impact_assessment TEXT,
    rollback_plan TEXT,
    requested_by INTEGER NOT NULL,
    requested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    approval_status VARCHAR(20) DEFAULT 'Pending' CHECK (approval_status IN ('Pending', 'Approved', 'Rejected')),
    approver_id INTEGER,
    approved_at TIMESTAMP,
    approval_comments TEXT,
    implementation_date TIMESTAMP,
    status VARCHAR(20) DEFAULT 'Submitted' CHECK (status IN ('Submitted', 'InProgress', 'Completed', 'RolledBack')),
    release_version VARCHAR(50),
    FOREIGN KEY (asset_id) REFERENCES assets(asset_id),
    FOREIGN KEY (requested_by) REFERENCES users(user_id),
    FOREIGN KEY (approver_id) REFERENCES users(user_id)
);

CREATE INDEX idx_changes_asset ON change_requests(asset_id);
CREATE INDEX idx_changes_status ON change_requests(approval_status);
CREATE INDEX idx_changes_risk ON change_requests(risk_level);
```

**Sample Data:**
```sql
INSERT INTO change_requests (title, description, asset_id, change_type, risk_level,
                              impact_assessment, requested_by, approval_status)
VALUES
    ('Deploy HR DW to Production', 'Initial production deployment', 1, 'Deploy', 'High',
     'Affects all HR reporting dashboards', 2, 'Approved');
```

---

### 7. compliance_violations

**Purpose:** Track naming convention and policy violations.

```sql
CREATE TABLE compliance_violations (
    violation_id INTEGER PRIMARY KEY AUTOINCREMENT,
    asset_id INTEGER NOT NULL,
    violation_type VARCHAR(50) NOT NULL, -- 'Naming', 'Documentation', 'Ownership', 'Lifecycle'
    severity VARCHAR(20) NOT NULL CHECK (severity IN ('Low', 'Medium', 'High')),
    description TEXT NOT NULL,
    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP,
    resolved_by INTEGER,
    resolution_notes TEXT,
    FOREIGN KEY (asset_id) REFERENCES assets(asset_id) ON DELETE CASCADE,
    FOREIGN KEY (resolved_by) REFERENCES users(user_id)
);

CREATE INDEX idx_violations_asset ON compliance_violations(asset_id);
CREATE INDEX idx_violations_type ON compliance_violations(violation_type);
CREATE INDEX idx_violations_unresolved ON compliance_violations(resolved_at) WHERE resolved_at IS NULL;
```

**Sample Data:**
```sql
INSERT INTO compliance_violations (asset_id, violation_type, severity, description)
VALUES
    (2, 'Documentation', 'Medium', 'Missing documentation URL');
```

---

### 8. audit_logs

**Purpose:** Immutable audit trail of all system actions.

```sql
CREATE TABLE audit_logs (
    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    action VARCHAR(50) NOT NULL, -- 'CREATE', 'UPDATE', 'DELETE', 'APPROVE', 'TRANSITION'
    entity_type VARCHAR(50) NOT NULL, -- 'Asset', 'Change', 'User'
    entity_id INTEGER NOT NULL,
    old_value TEXT, -- JSON snapshot
    new_value TEXT, -- JSON snapshot
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ip_address VARCHAR(45),
    user_agent TEXT,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE INDEX idx_audit_user ON audit_logs(user_id);
CREATE INDEX idx_audit_timestamp ON audit_logs(timestamp);
CREATE INDEX idx_audit_entity ON audit_logs(entity_type, entity_id);
```

---

### 9. compliance_metrics

**Purpose:** Pre-calculated compliance metrics for dashboard performance.

```sql
CREATE TABLE compliance_metrics (
    metric_id INTEGER PRIMARY KEY AUTOINCREMENT,
    metric_date DATE NOT NULL,
    total_assets INTEGER DEFAULT 0,
    compliant_assets INTEGER DEFAULT 0,
    compliance_rate DECIMAL(5,2) DEFAULT 0.00,
    missing_documentation INTEGER DEFAULT 0,
    version_conflicts INTEGER DEFAULT 0,
    pending_changes INTEGER DEFAULT 0,
    calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_metrics_date ON compliance_metrics(metric_date);
```

---

### 10. business_goals

**Purpose:** Track strategic business goals aligned with DaaS initiatives.

```sql
CREATE TABLE business_goals (
    goal_id INTEGER PRIMARY KEY AUTOINCREMENT,
    goal_name VARCHAR(255) NOT NULL,
    description TEXT,
    strategic_priority VARCHAR(20) CHECK (strategic_priority IN ('High', 'Medium', 'Low')),
    target_completion_date DATE,
    achievement_status VARCHAR(50) DEFAULT 'Not Started'
        CHECK (achievement_status IN ('Not Started', 'In Progress', 'Achieved', 'At Risk')),
    owner_id INTEGER,
    expected_value DECIMAL(15,2), -- Financial value or impact
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (owner_id) REFERENCES users(user_id)
);

CREATE INDEX idx_goals_status ON business_goals(achievement_status);
CREATE INDEX idx_goals_priority ON business_goals(strategic_priority);
```

---

### 11. strategic_initiatives

**Purpose:** Track DaaS strategic initiatives and projects.

```sql
CREATE TABLE strategic_initiatives (
    initiative_id INTEGER PRIMARY KEY AUTOINCREMENT,
    initiative_name VARCHAR(255) NOT NULL,
    description TEXT,
    goal_id INTEGER,
    status VARCHAR(50) DEFAULT 'Planning'
        CHECK (status IN ('Planning', 'In Progress', 'Completed', 'On Hold')),
    risk_level VARCHAR(20) CHECK (risk_level IN ('Low', 'Medium', 'High')),
    budget_allocated DECIMAL(15,2),
    budget_spent DECIMAL(15,2) DEFAULT 0,
    expected_roi DECIMAL(15,2),
    start_date DATE,
    end_date DATE,
    owner_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (goal_id) REFERENCES business_goals(goal_id),
    FOREIGN KEY (owner_id) REFERENCES users(user_id)
);

CREATE INDEX idx_initiatives_status ON strategic_initiatives(status);
CREATE INDEX idx_initiatives_goal ON strategic_initiatives(goal_id);
```

---

### 12. initiative_deliverables

**Purpose:** Track deliverables for strategic initiatives.

```sql
CREATE TABLE initiative_deliverables (
    deliverable_id INTEGER PRIMARY KEY AUTOINCREMENT,
    initiative_id INTEGER NOT NULL,
    deliverable_name VARCHAR(255) NOT NULL,
    description TEXT,
    due_date DATE,
    completion_status VARCHAR(50) DEFAULT 'Pending'
        CHECK (completion_status IN ('Pending', 'In Progress', 'Completed', 'Blocked')),
    completion_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (initiative_id) REFERENCES strategic_initiatives(initiative_id) ON DELETE CASCADE
);

CREATE INDEX idx_deliverables_initiative ON initiative_deliverables(initiative_id);
CREATE INDEX idx_deliverables_status ON initiative_deliverables(completion_status);
```

---

### 13. asset_business_alignment

**Purpose:** Link data assets to business goals and use cases.

```sql
CREATE TABLE asset_business_alignment (
    alignment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    asset_id INTEGER NOT NULL,
    goal_id INTEGER NOT NULL,
    use_case_description TEXT,
    business_value TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER,
    FOREIGN KEY (asset_id) REFERENCES assets(asset_id) ON DELETE CASCADE,
    FOREIGN KEY (goal_id) REFERENCES business_goals(goal_id) ON DELETE CASCADE,
    FOREIGN KEY (created_by) REFERENCES users(user_id)
);

CREATE INDEX idx_alignment_asset ON asset_business_alignment(asset_id);
CREATE INDEX idx_alignment_goal ON asset_business_alignment(goal_id);
```

---

### 14. vendors

**Purpose:** Manage vendor relationships for DaaS services.

```sql
CREATE TABLE vendors (
    vendor_id INTEGER PRIMARY KEY AUTOINCREMENT,
    vendor_name VARCHAR(255) NOT NULL UNIQUE,
    vendor_type VARCHAR(100)
        CHECK (vendor_type IN ('Cloud Provider', 'Software', 'Consulting', 'Managed Services')),
    status VARCHAR(50) DEFAULT 'Active'
        CHECK (status IN ('Active', 'Inactive', 'Under Review')),
    contract_start_date DATE,
    contract_end_date DATE,
    annual_cost DECIMAL(15,2),
    primary_contact VARCHAR(255),
    contact_email VARCHAR(255),
    performance_score DECIMAL(3,1), -- 0.0 to 5.0
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_vendors_status ON vendors(status);
CREATE INDEX idx_vendors_type ON vendors(vendor_type);
```

---

### 15. vendor_slas

**Purpose:** Track SLA metrics and performance per vendor.

```sql
CREATE TABLE vendor_slas (
    sla_id INTEGER PRIMARY KEY AUTOINCREMENT,
    vendor_id INTEGER NOT NULL,
    metric VARCHAR(100) NOT NULL, -- 'Uptime', 'Response Time', 'Data Quality'
    target VARCHAR(100), -- e.g., '99.9%', '< 2 hours'
    current_value VARCHAR(100),
    status VARCHAR(50) DEFAULT 'Met'
        CHECK (status IN ('Met', 'At Risk', 'Breached')),
    measurement_period VARCHAR(50), -- 'Monthly', 'Quarterly'
    last_measured_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (vendor_id) REFERENCES vendors(vendor_id) ON DELETE CASCADE
);

CREATE INDEX idx_slas_vendor ON vendor_slas(vendor_id);
CREATE INDEX idx_slas_status ON vendor_slas(status);
```

---

### 16. asset_vendor_mapping

**Purpose:** Link assets to vendor services.

```sql
CREATE TABLE asset_vendor_mapping (
    mapping_id INTEGER PRIMARY KEY AUTOINCREMENT,
    asset_id INTEGER NOT NULL,
    vendor_id INTEGER NOT NULL,
    service_description TEXT,
    annual_cost DECIMAL(15,2),
    contract_reference VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (asset_id) REFERENCES assets(asset_id) ON DELETE CASCADE,
    FOREIGN KEY (vendor_id) REFERENCES vendors(vendor_id) ON DELETE CASCADE
);

CREATE INDEX idx_asset_vendor_asset ON asset_vendor_mapping(asset_id);
CREATE INDEX idx_asset_vendor_vendor ON asset_vendor_mapping(vendor_id);
```

---

### 17. stakeholders

**Purpose:** Track business stakeholders and their engagement.

```sql
CREATE TABLE stakeholders (
    stakeholder_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(255) NOT NULL,
    department VARCHAR(100),
    role VARCHAR(100),
    contact_email VARCHAR(255) UNIQUE,
    engagement_level VARCHAR(50)
        CHECK (engagement_level IN ('High', 'Medium', 'Low')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_stakeholders_department ON stakeholders(department);
CREATE INDEX idx_stakeholders_engagement ON stakeholders(engagement_level);
```

---

### 18. stakeholder_data_needs

**Purpose:** Track data needs identified by stakeholders.

```sql
CREATE TABLE stakeholder_data_needs (
    need_id INTEGER PRIMARY KEY AUTOINCREMENT,
    stakeholder_id INTEGER NOT NULL,
    data_need_description TEXT NOT NULL,
    status VARCHAR(50) DEFAULT 'Identified'
        CHECK (status IN ('Identified', 'In Progress', 'Fulfilled', 'Blocked')),
    priority VARCHAR(20) CHECK (priority IN ('High', 'Medium', 'Low')),
    fulfillment_date DATE,
    use_case_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (stakeholder_id) REFERENCES stakeholders(stakeholder_id) ON DELETE CASCADE,
    FOREIGN KEY (use_case_id) REFERENCES business_use_cases(use_case_id)
);

CREATE INDEX idx_needs_stakeholder ON stakeholder_data_needs(stakeholder_id);
CREATE INDEX idx_needs_status ON stakeholder_data_needs(status);
```

---

### 19. business_use_cases

**Purpose:** Track business use cases supported by data assets.

```sql
CREATE TABLE business_use_cases (
    use_case_id INTEGER PRIMARY KEY AUTOINCREMENT,
    use_case_name VARCHAR(255) NOT NULL,
    description TEXT,
    domain_id INTEGER,
    business_value TEXT,
    stakeholder_id INTEGER,
    status VARCHAR(50) DEFAULT 'Active'
        CHECK (status IN ('Active', 'In Development', 'Retired')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (domain_id) REFERENCES domains(domain_id),
    FOREIGN KEY (stakeholder_id) REFERENCES stakeholders(stakeholder_id)
);

CREATE INDEX idx_use_cases_domain ON business_use_cases(domain_id);
CREATE INDEX idx_use_cases_status ON business_use_cases(status);
```

---

### 20. budget_allocations

**Purpose:** Track budget allocation and spending by category and domain.

```sql
CREATE TABLE budget_allocations (
    budget_id INTEGER PRIMARY KEY AUTOINCREMENT,
    fiscal_year INTEGER NOT NULL,
    category VARCHAR(100) NOT NULL
        CHECK (category IN ('Infrastructure', 'Licenses', 'Consulting', 'Training', 'Cloud Services')),
    domain_id INTEGER,
    allocated DECIMAL(15,2) NOT NULL,
    spent DECIMAL(15,2) DEFAULT 0,
    forecast DECIMAL(15,2),
    variance DECIMAL(15,2) GENERATED ALWAYS AS (allocated - spent) STORED,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (domain_id) REFERENCES domains(domain_id)
);

CREATE INDEX idx_budget_year ON budget_allocations(fiscal_year);
CREATE INDEX idx_budget_category ON budget_allocations(category);
CREATE INDEX idx_budget_domain ON budget_allocations(domain_id);
```

---

## Views

### v_asset_summary

**Purpose:** Simplified view for asset listing with owner and domain names.

```sql
CREATE VIEW v_asset_summary AS
SELECT
    a.asset_id,
    a.asset_name,
    a.environment,
    a.lifecycle_stage,
    a.naming_compliant,
    d.domain_name,
    u.username AS owner_name,
    u.email AS owner_email,
    a.created_at,
    a.updated_at
FROM assets a
JOIN domains d ON a.domain_id = d.domain_id
JOIN users u ON a.owner_id = u.user_id;
```

### v_compliance_dashboard

**Purpose:** Real-time compliance metrics for dashboard.

```sql
CREATE VIEW v_compliance_dashboard AS
SELECT
    COUNT(*) AS total_assets,
    SUM(CASE WHEN naming_compliant = TRUE THEN 1 ELSE 0 END) AS compliant_assets,
    ROUND(100.0 * SUM(CASE WHEN naming_compliant = TRUE THEN 1 ELSE 0 END) / COUNT(*), 2) AS compliance_rate,
    SUM(CASE WHEN documentation_url IS NULL OR documentation_url = '' THEN 1 ELSE 0 END) AS missing_documentation,
    SUM(CASE WHEN lifecycle_stage = 'Deprecated' THEN 1 ELSE 0 END) AS deprecated_count
FROM assets;
```

### v_change_summary

**Purpose:** Change request summary with asset and user details.

```sql
CREATE VIEW v_change_summary AS
SELECT
    c.change_id,
    c.title,
    c.change_type,
    c.risk_level,
    c.approval_status,
    c.status,
    a.asset_name,
    u1.username AS requested_by_name,
    u2.username AS approver_name,
    c.requested_at,
    c.approved_at
FROM change_requests c
JOIN assets a ON c.asset_id = a.asset_id
JOIN users u1 ON c.requested_by = u1.user_id
LEFT JOIN users u2 ON c.approver_id = u2.user_id;
```

---

## Data Integrity Constraints

### Referential Integrity
- All foreign keys enforce ON DELETE restrictions
- Cascade deletes for child records (lifecycle_history, compliance_violations)
- Prevent orphaned records

### Business Rules
1. **Unique Asset Names**: Asset names must be globally unique
2. **Valid Lifecycle Transitions**: Enforced at application layer
3. **Mandatory Owner**: Every asset must have an assigned owner
4. **Environment Validation**: Only DEV, QA, PROD, UAT allowed
5. **Naming Compliance**: Validated before insert/update

---

## Database Initialization Script

See `/database/init.sql` for complete initialization script with:
- Table creation
- Index creation
- View creation
- Sample data insertion
- Default users and roles

---

## Migration Strategy

### Phase 1: SQLite (Prototype)
- Embedded database, zero configuration
- File-based: `governance_portal.db`
- Suitable for development and demo

### Phase 2: PostgreSQL (Production)
- Scalable, ACID-compliant
- Advanced features: JSON columns, full-text search
- Migration tools: Alembic for schema versioning

---

## Approval

**Database Architect:** ________________________
**DBA Team Lead:** ________________________
**Approval Date:** _____________
