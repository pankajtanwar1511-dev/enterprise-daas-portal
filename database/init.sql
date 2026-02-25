-- Enterprise DaaS Governance Portal
-- Database Initialization Script
-- Version: 1.0
-- Date: February 2026

-- ============================================================
-- TABLE CREATION
-- ============================================================

-- Roles table
CREATE TABLE IF NOT EXISTS roles (
    role_id INTEGER PRIMARY KEY AUTOINCREMENT,
    role_name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    permissions TEXT, -- JSON array of permissions
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Users table
CREATE TABLE IF NOT EXISTS users (
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

-- Domains table
CREATE TABLE IF NOT EXISTS domains (
    domain_id INTEGER PRIMARY KEY AUTOINCREMENT,
    domain_code VARCHAR(10) NOT NULL UNIQUE,
    domain_name VARCHAR(100) NOT NULL,
    description TEXT,
    data_steward_id INTEGER,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (data_steward_id) REFERENCES users(user_id)
);

-- Assets table
CREATE TABLE IF NOT EXISTS assets (
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

-- Lifecycle history table
CREATE TABLE IF NOT EXISTS lifecycle_history (
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

-- Change requests table
CREATE TABLE IF NOT EXISTS change_requests (
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

-- Compliance violations table
CREATE TABLE IF NOT EXISTS compliance_violations (
    violation_id INTEGER PRIMARY KEY AUTOINCREMENT,
    asset_id INTEGER NOT NULL,
    violation_type VARCHAR(50) NOT NULL,
    severity VARCHAR(20) NOT NULL CHECK (severity IN ('Low', 'Medium', 'High')),
    description TEXT NOT NULL,
    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP,
    resolved_by INTEGER,
    resolution_notes TEXT,
    FOREIGN KEY (asset_id) REFERENCES assets(asset_id) ON DELETE CASCADE,
    FOREIGN KEY (resolved_by) REFERENCES users(user_id)
);

-- Audit logs table
CREATE TABLE IF NOT EXISTS audit_logs (
    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    action VARCHAR(50) NOT NULL,
    entity_type VARCHAR(50) NOT NULL,
    entity_id INTEGER NOT NULL,
    old_value TEXT,
    new_value TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ip_address VARCHAR(45),
    user_agent TEXT,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- Compliance metrics table
CREATE TABLE IF NOT EXISTS compliance_metrics (
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

-- ============================================================
-- INDEXES
-- ============================================================

CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role_id);

CREATE INDEX IF NOT EXISTS idx_assets_name ON assets(asset_name);
CREATE INDEX IF NOT EXISTS idx_assets_domain ON assets(domain_id);
CREATE INDEX IF NOT EXISTS idx_assets_lifecycle ON assets(lifecycle_stage);
CREATE INDEX IF NOT EXISTS idx_assets_environment ON assets(environment);
CREATE INDEX IF NOT EXISTS idx_assets_owner ON assets(owner_id);
CREATE INDEX IF NOT EXISTS idx_assets_compliant ON assets(naming_compliant);

CREATE INDEX IF NOT EXISTS idx_lifecycle_asset ON lifecycle_history(asset_id);
CREATE INDEX IF NOT EXISTS idx_lifecycle_date ON lifecycle_history(changed_at);

CREATE INDEX IF NOT EXISTS idx_changes_asset ON change_requests(asset_id);
CREATE INDEX IF NOT EXISTS idx_changes_status ON change_requests(approval_status);
CREATE INDEX IF NOT EXISTS idx_changes_risk ON change_requests(risk_level);

CREATE INDEX IF NOT EXISTS idx_violations_asset ON compliance_violations(asset_id);
CREATE INDEX IF NOT EXISTS idx_violations_type ON compliance_violations(violation_type);

CREATE INDEX IF NOT EXISTS idx_audit_user ON audit_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON audit_logs(timestamp);
CREATE INDEX IF NOT EXISTS idx_audit_entity ON audit_logs(entity_type, entity_id);

CREATE INDEX IF NOT EXISTS idx_metrics_date ON compliance_metrics(metric_date);

-- ============================================================
-- VIEWS
-- ============================================================

CREATE VIEW IF NOT EXISTS v_asset_summary AS
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

CREATE VIEW IF NOT EXISTS v_compliance_dashboard AS
SELECT
    COUNT(*) AS total_assets,
    SUM(CASE WHEN naming_compliant = 1 THEN 1 ELSE 0 END) AS compliant_assets,
    ROUND(100.0 * SUM(CASE WHEN naming_compliant = 1 THEN 1 ELSE 0 END) / COUNT(*), 2) AS compliance_rate,
    SUM(CASE WHEN documentation_url IS NULL OR documentation_url = '' THEN 1 ELSE 0 END) AS missing_documentation,
    SUM(CASE WHEN lifecycle_stage = 'Deprecated' THEN 1 ELSE 0 END) AS deprecated_count
FROM assets;

CREATE VIEW IF NOT EXISTS v_change_summary AS
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

-- ============================================================
-- SEED DATA
-- ============================================================

-- Insert default roles
INSERT INTO roles (role_name, description, permissions) VALUES
    ('Admin', 'Full system access', '["*"]'),
    ('DataSteward', 'Governance and approval authority', '["asset:*", "change:approve", "compliance:view"]'),
    ('AssetOwner', 'Manage owned assets', '["asset:create", "asset:update", "asset:view"]'),
    ('Viewer', 'Read-only access', '["asset:view", "compliance:view"]');

-- Insert default users
-- Password for all demo users: "demo123" (hashed with bcrypt)
INSERT INTO users (username, email, password_hash, first_name, last_name, role_id, is_active) VALUES
    ('admin', 'admin@company.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYbJVlPGNuS', 'System', 'Admin', 1, TRUE),
    ('jsmith', 'jsmith@company.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYbJVlPGNuS', 'John', 'Smith', 2, TRUE),
    ('mjohnson', 'mjohnson@company.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYbJVlPGNuS', 'Mary', 'Johnson', 3, TRUE),
    ('rdavis', 'rdavis@company.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYbJVlPGNuS', 'Robert', 'Davis', 4, TRUE);

-- Insert business domains
INSERT INTO domains (domain_code, domain_name, description, data_steward_id, is_active) VALUES
    ('HR', 'Human Resources', 'Employee and workforce management data', 2, TRUE),
    ('FIN', 'Finance', 'Financial transactions and accounting data', 2, TRUE),
    ('OPS', 'Operations', 'Operational and logistics data', 2, TRUE),
    ('SALES', 'Sales', 'Sales and customer relationship data', 2, TRUE),
    ('IT', 'Information Technology', 'IT infrastructure and systems data', 2, TRUE),
    ('DATA', 'Data Platform', 'Enterprise data platform assets', 2, TRUE);

-- Insert sample assets
INSERT INTO assets (asset_name, domain_id, environment, owner_id, version, lifecycle_stage,
                    documentation_url, description, business_justification, naming_compliant, created_by)
VALUES
    ('PROD-HR-DW-v1', 1, 'PROD', 3, 'v1.0', 'Active',
     'https://docs.company.com/hr-dw', 'HR Data Warehouse - central repository for employee data',
     'Centralize HR data for reporting and analytics', TRUE, 1),

    ('PROD-FIN-ETL-v2', 2, 'PROD', 3, 'v2.1', 'Active',
     'https://docs.company.com/fin-etl', 'Finance ETL Pipeline - daily transaction processing',
     'Automate financial data ingestion from source systems', TRUE, 1),

    ('QA-OPS-API-v1', 3, 'QA', 3, 'v1.3', 'Active',
     'https://docs.company.com/ops-api', 'Operations API - logistics data access layer',
     'Provide unified API for operations data', TRUE, 1),

    ('DEV-SALES-CRM-v3', 4, 'DEV', 3, 'v3.0', 'Draft',
     '', 'Sales CRM Integration - Salesforce connector',
     'Integrate Salesforce data into enterprise DW', TRUE, 1),

    ('PROD-DATA-LAKE-v1', 6, 'PROD', 3, 'v1.5', 'Active',
     'https://docs.company.com/data-lake', 'Enterprise Data Lake - S3-based storage',
     'Scalable storage for all enterprise data assets', TRUE, 1),

    ('PROD-HR-REPORT-v1', 1, 'PROD', 3, 'v1.0', 'Deprecated',
     'https://docs.company.com/hr-report', 'HR Reporting System (Legacy)',
     'Legacy reporting - being replaced by new BI platform', TRUE, 1),

    ('production-finance-system', 2, 'PROD', 3, 'v1', 'Active',
     '', 'Non-compliant naming example',
     'Demonstrates naming violation', FALSE, 1);

-- Insert lifecycle history
INSERT INTO lifecycle_history (asset_id, from_state, to_state, changed_by, change_reason) VALUES
    (1, 'Draft', 'Active', 1, 'Passed UAT and security review, approved for production deployment'),
    (2, 'Draft', 'Active', 1, 'Initial production release'),
    (2, 'Active', 'Active', 1, 'Version upgrade from v2.0 to v2.1'),
    (6, 'Active', 'Deprecated', 2, 'System being replaced by modern BI platform, sunset date: 2026-06-30');

-- Insert sample change requests
INSERT INTO change_requests (title, description, asset_id, change_type, risk_level,
                              impact_assessment, rollback_plan, requested_by, approval_status,
                              approver_id, status, release_version)
VALUES
    ('Deploy HR DW to Production', 'Initial production deployment of HR Data Warehouse',
     1, 'Deploy', 'High',
     'Affects all HR reporting dashboards and analytics. Estimated 2-hour downtime.',
     'Restore from backup and revert DNS to old system.',
     3, 'Approved', 2, 'Completed', 'R1.0'),

    ('Upgrade FIN ETL Pipeline', 'Upgrade to v2.1 with improved error handling',
     2, 'Modify', 'Medium',
     'Minor performance improvement, no downtime expected.',
     'Rollback deployment using blue-green switch.',
     3, 'Approved', 2, 'Completed', 'R1.1'),

    ('Decommission Legacy HR Reports', 'Retire old reporting system',
     6, 'Decommission', 'Medium',
     'Users migrated to new BI platform. No active users remaining.',
     'N/A - read-only archive will remain available.',
     3, 'Pending', NULL, 'Submitted', NULL);

-- Insert compliance violations
INSERT INTO compliance_violations (asset_id, violation_type, severity, description) VALUES
    (7, 'Naming', 'High', 'Asset name does not comply with standard format ENV-DOMAIN-SYSTEM-VERSION'),
    (4, 'Documentation', 'Medium', 'Missing documentation URL - required for Active lifecycle state'),
    (7, 'Documentation', 'Medium', 'No documentation provided');

-- Insert sample audit logs
INSERT INTO audit_logs (user_id, action, entity_type, entity_id, old_value, new_value, ip_address)
VALUES
    (1, 'CREATE', 'Asset', 1, NULL, '{"asset_name":"PROD-HR-DW-v1","lifecycle_stage":"Draft"}', '10.0.1.15'),
    (1, 'UPDATE', 'Asset', 1, '{"lifecycle_stage":"Draft"}', '{"lifecycle_stage":"Active"}', '10.0.1.15'),
    (2, 'APPROVE', 'Change', 1, '{"approval_status":"Pending"}', '{"approval_status":"Approved"}', '10.0.1.22');

-- Insert initial compliance metrics
INSERT INTO compliance_metrics (metric_date, total_assets, compliant_assets, compliance_rate,
                                 missing_documentation, version_conflicts, pending_changes)
VALUES
    (DATE('now'), 7, 6, 85.71, 2, 0, 1);

-- ============================================================
-- VERIFICATION QUERIES
-- ============================================================

-- Uncomment to verify installation:
-- SELECT 'Total Users:', COUNT(*) FROM users;
-- SELECT 'Total Assets:', COUNT(*) FROM assets;
-- SELECT 'Total Domains:', COUNT(*) FROM domains;
-- SELECT 'Compliance Rate:', compliance_rate || '%' FROM v_compliance_dashboard;

-- ============================================================
-- END OF INITIALIZATION SCRIPT
-- ============================================================
