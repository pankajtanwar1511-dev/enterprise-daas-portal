# Enterprise DaaS Governance Portal - Technical Guide

**Version:** 3.0
**Last Updated:** February 25, 2026
**Status:** Production-Ready
**Target Audience:** Developers, Architects, Technical Leads

---

## Table of Contents

1. [System Architecture](#1-system-architecture)
2. [Technology Stack](#2-technology-stack)
3. [Database Design](#3-database-design)
4. [API Documentation](#4-api-documentation)
5. [Authentication & Authorization](#5-authentication--authorization)
6. [ITSM Integration](#6-itsm-integration)
7. [Implementation Guide](#7-implementation-guide)
8. [Deployment Architecture](#8-deployment-architecture)

---

## 1. System Architecture

### 1.1 High-Level Architecture

```
┌───────────────────────────────────────────────────────────────┐
│                    User Layer (Web Browser)                   │
│                   React SPA (Port 5173/3000)                  │
└────────────────────────┬──────────────────────────────────────┘
                         │ HTTPS/REST
┌────────────────────────▼──────────────────────────────────────┐
│                     API Gateway Layer                          │
│                   FastAPI Backend (Port 8000)                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐     │
│  │  Assets  │  │ Strategy │  │ Vendors  │  │ Reports  │     │
│  │   API    │  │   API    │  │   API    │  │   API    │     │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘     │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐     │
│  │  Tasks   │  │ Comments │  │ Activity │  │ Notifs   │     │
│  │   API    │  │   API    │  │   API    │  │   API    │     │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘     │
└────────────────────────┬──────────────────────────────────────┘
                         │ SQLAlchemy ORM
┌────────────────────────▼──────────────────────────────────────┐
│                   Data Persistence Layer                       │
│              PostgreSQL Database (Port 5432)                   │
│     27 Tables: Core (9) + Extended (11) + Collaboration (7)   │
└────────────────────────┬──────────────────────────────────────┘
                         │
┌────────────────────────▼──────────────────────────────────────┐
│                  External Integrations                         │
│   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│   │  ServiceNow │  │     Jira    │  │    Slack    │         │
│   │ Change Mgmt │  │  Epic/Story │  │ Webhooks    │         │
│   └─────────────┘  └─────────────┘  └─────────────┘         │
└───────────────────────────────────────────────────────────────┘
```

### 1.2 Component Breakdown

#### Frontend (React)
- **Framework:** React 18.2.0 with Vite 5.0.2
- **UI Library:** Material-UI 5.14.18
- **Routing:** React Router DOM 6.20.0
- **HTTP Client:** Axios 1.6.2
- **Charts:** Recharts 2.10.3
- **State Management:** React Hooks (useState, useEffect, useContext)

#### Backend (FastAPI)
- **Framework:** FastAPI 0.109.2
- **ASGI Server:** Uvicorn 0.27.1
- **ORM:** SQLAlchemy 2.0.25
- **Validation:** Pydantic 2.6.1
- **Authentication:** Python-Jose 3.3.0 (JWT)
- **Password Hashing:** Passlib 1.7.4 (bcrypt)

#### Database (PostgreSQL)
- **Version:** PostgreSQL 14+
- **Driver:** psycopg2-binary 2.9.9
- **Migrations:** Alembic 1.13.1
- **Connection Pooling:** SQLAlchemy pool

### 1.3 Request Flow

**Typical API Request:**
```
1. Browser → HTTP Request → Backend API
   ├─ Headers: Authorization: Bearer <JWT_TOKEN>
   ├─ Method: GET /api/v1/assets?domain=HR
   └─ Body: (none for GET)

2. Backend API → Auth Middleware
   ├─ Verify JWT token
   ├─ Extract user_id from token
   └─ Load user from database

3. Backend API → Route Handler
   ├─ Validate query parameters (Pydantic)
   ├─ Check authorization (user role)
   └─ Execute business logic

4. Business Logic → Database Query
   ├─ Construct SQLAlchemy query
   ├─ Apply filters (domain, owner, lifecycle)
   └─ Execute query with pagination

5. Database → Return Results
   ├─ Fetch rows from PostgreSQL
   └─ Convert to Python objects

6. Backend API → Serialize Response
   ├─ Convert to Pydantic schemas
   ├─ Format as JSON
   └─ Add response headers

7. Browser ← HTTP Response ← Backend API
   ├─ Status: 200 OK
   ├─ Body: JSON array of assets
   └─ Headers: Content-Type: application/json
```

### 1.4 Security Architecture

**Security Layers:**

```
┌──────────────────────────────────────────────┐
│ Layer 1: Network Security                   │
│ - HTTPS/TLS encryption                       │
│ - CORS policy (allowed origins)              │
│ - Rate limiting (100 req/min per IP)        │
└──────────────────┬───────────────────────────┘
                   │
┌──────────────────▼───────────────────────────┐
│ Layer 2: Authentication                      │
│ - JWT token validation                       │
│ - Token expiration (24 hours)                │
│ - Refresh token mechanism                    │
└──────────────────┬───────────────────────────┘
                   │
┌──────────────────▼───────────────────────────┐
│ Layer 3: Authorization                       │
│ - Role-based access control (RBAC)           │
│ - Resource ownership checks                  │
│ - Domain-level permissions                   │
└──────────────────┬───────────────────────────┘
                   │
┌──────────────────▼───────────────────────────┐
│ Layer 4: Data Security                       │
│ - Password hashing (bcrypt)                  │
│ - SQL injection prevention (ORM)             │
│ - Input validation (Pydantic)                │
│ - Output sanitization                        │
└──────────────────────────────────────────────┘
```

---

## 2. Technology Stack

### 2.1 Frontend Stack

| Technology | Version | Purpose |
|------------|---------|---------|
| **React** | 18.2.0 | UI framework |
| **Vite** | 5.0.2 | Build tool and dev server |
| **Material-UI** | 5.14.18 | Component library |
| **React Router** | 6.20.0 | Client-side routing |
| **Axios** | 1.6.2 | HTTP client for API calls |
| **Recharts** | 2.10.3 | Data visualization |
| **ESLint** | 8.55.0 | Code linting |
| **PPTXGenJS** | 3.12.0 | PowerPoint generation |

**Frontend File Structure:**
```
frontend/
├── src/
│   ├── main.jsx                 # Entry point
│   ├── App.jsx                  # Root component with routing
│   ├── components/
│   │   ├── Dashboard/           # Overview dashboard
│   │   ├── AssetRegistry/       # Asset management
│   │   ├── NamingValidator/     # Name validation
│   │   ├── ComplianceDashboard/ # Compliance metrics
│   │   ├── StrategyDashboard/   # Business goals & initiatives
│   │   ├── VendorManagement/    # Vendor & SLA management
│   │   ├── ManagementReports/   # Executive reports
│   │   ├── TaskManagement/      # Task assignment
│   │   ├── NotificationCenter/  # In-app notifications
│   │   ├── CommentSection/      # Threaded comments
│   │   ├── ActivityFeed/        # Activity timeline
│   │   └── TeamDashboard/       # Personalized dashboard
│   ├── services/                # API service functions
│   ├── styles/                  # Global styles
│   └── utils/                   # Helper functions
├── public/
│   └── index.html
├── package.json
├── vite.config.js
└── .env
```

### 2.2 Backend Stack

| Technology | Version | Purpose |
|------------|---------|---------|
| **FastAPI** | 0.109.2 | Web framework |
| **Uvicorn** | 0.27.1 | ASGI server |
| **SQLAlchemy** | 2.0.25 | ORM for database |
| **Alembic** | 1.13.1 | Database migrations |
| **Pydantic** | 2.6.1 | Data validation |
| **Python-Jose** | 3.3.0 | JWT token handling |
| **Passlib** | 1.7.4 | Password hashing |
| **psycopg2** | 2.9.9 | PostgreSQL driver |
| **Requests** | 2.31.0 | HTTP client for integrations |
| **Python-dotenv** | 1.0.0 | Environment variable management |

**Backend File Structure:**
```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI app entry point
│   ├── database.py                # Database connection & session
│   ├── models.py                  # Core ORM models (9 tables)
│   ├── models_extended.py         # Strategic models (11 tables)
│   ├── models_collaboration.py    # Collaboration models (7 tables)
│   ├── models_itsm.py             # ITSM integration models
│   ├── schemas.py                 # Pydantic schemas
│   ├── schemas_collaboration.py   # Collaboration schemas
│   ├── api/
│   │   ├── __init__.py
│   │   ├── auth.py                # Authentication endpoints
│   │   ├── assets.py              # Asset CRUD
│   │   ├── compliance.py          # Compliance metrics
│   │   ├── strategy.py            # Goals & initiatives
│   │   ├── vendors.py             # Vendor management
│   │   ├── reports.py             # Executive reports
│   │   ├── tasks.py               # Task management
│   │   ├── notifications.py       # Notification system
│   │   ├── comments.py            # Comment system
│   │   └── activity.py            # Activity feed
│   ├── services/
│   │   ├── naming_validator.py    # Naming convention validation
│   │   ├── slack_notifier.py      # Slack integration
│   │   ├── servicenow_integration.py  # ServiceNow integration
│   │   └── jira_integration.py    # Jira integration
│   └── utils/
│       └── logger.py              # Structured logging
├── migrations/                     # Alembic migrations
│   └── versions/
├── tests/
│   ├── unit/
│   ├── integration/
│   └── e2e/
├── .env
├── requirements.txt
└── alembic.ini
```

### 2.3 Database Stack

| Technology | Version | Purpose |
|------------|---------|---------|
| **PostgreSQL** | 14+ | Relational database |
| **pgAdmin** | 4 | Database administration |
| **pg_stat_statements** | - | Query performance monitoring |
| **Connection Pooling** | SQLAlchemy | Connection management |

---

## 3. Database Design

### 3.1 Schema Overview

**Database:** `governance_portal`

**Total Tables:** 27
- **Core Tables:** 9 (auth, assets, compliance, audit)
- **Extended Tables:** 11 (strategy, vendors, budget)
- **Collaboration Tables:** 7 (tasks, notifications, comments, activity)

### 3.2 Core Tables (9)

#### 3.2.1 roles
**Purpose:** Define user roles for RBAC

```sql
CREATE TABLE roles (
    role_id SERIAL PRIMARY KEY,
    role_name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    permissions JSON,
    created_at TIMESTAMP DEFAULT NOW()
);
```

**Sample Data:**
| role_id | role_name | description |
|---------|-----------|-------------|
| 1 | Admin | Full system access |
| 2 | DataSteward | Manage assets in assigned domains |
| 3 | AssetOwner | Manage owned assets |
| 4 | Viewer | Read-only access |

#### 3.2.2 users
**Purpose:** Store user accounts and authentication

```sql
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    role_id INTEGER REFERENCES roles(role_id),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    last_login TIMESTAMP
);
```

**Indexes:**
- `idx_users_username` on `username`
- `idx_users_email` on `email`
- `idx_users_role` on `role_id`

#### 3.2.3 domains
**Purpose:** Business domains (HR, Finance, etc.)

```sql
CREATE TABLE domains (
    domain_id SERIAL PRIMARY KEY,
    domain_name VARCHAR(100) UNIQUE NOT NULL,
    domain_code VARCHAR(10) UNIQUE NOT NULL,
    description TEXT,
    owner_id INTEGER REFERENCES users(user_id),
    created_at TIMESTAMP DEFAULT NOW()
);
```

**Sample Data:**
| domain_id | domain_code | domain_name | owner_id |
|-----------|-------------|-------------|----------|
| 1 | HR | Human Resources | 2 |
| 2 | FIN | Finance | 3 |
| 3 | OPS | Operations | 4 |

#### 3.2.4 assets
**Purpose:** Central asset registry

```sql
CREATE TABLE assets (
    asset_id SERIAL PRIMARY KEY,
    asset_name VARCHAR(255) UNIQUE NOT NULL,
    domain_id INTEGER REFERENCES domains(domain_id),
    owner_id INTEGER REFERENCES users(user_id),
    environment VARCHAR(20) CHECK (environment IN ('DEV', 'QA', 'UAT', 'PROD')),
    version VARCHAR(50),
    lifecycle_stage VARCHAR(50) DEFAULT 'Active',
    description TEXT,
    documentation_url TEXT,
    business_justification TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

**Indexes:**
- `idx_assets_name` on `asset_name`
- `idx_assets_domain` on `domain_id`
- `idx_assets_owner` on `owner_id`
- `idx_assets_lifecycle` on `lifecycle_stage`
- `idx_assets_created` on `created_at DESC`

**Constraints:**
- `asset_name` must match naming convention (checked in application)
- `owner_id` cannot be NULL
- `domain_id` cannot be NULL

#### 3.2.5 lifecycle_history
**Purpose:** Track asset lifecycle state changes

```sql
CREATE TABLE lifecycle_history (
    history_id SERIAL PRIMARY KEY,
    asset_id INTEGER REFERENCES assets(asset_id) ON DELETE CASCADE,
    previous_stage VARCHAR(50),
    new_stage VARCHAR(50) NOT NULL,
    changed_by INTEGER REFERENCES users(user_id),
    changed_at TIMESTAMP DEFAULT NOW(),
    reason TEXT
);
```

**Indexes:**
- `idx_lifecycle_asset` on `asset_id`
- `idx_lifecycle_date` on `changed_at DESC`

#### 3.2.6 change_requests
**Purpose:** ITIL-compliant change management

```sql
CREATE TABLE change_requests (
    change_request_id SERIAL PRIMARY KEY,
    asset_id INTEGER REFERENCES assets(asset_id),
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    change_type VARCHAR(50) CHECK (change_type IN ('Upgrade', 'Configuration', 'Decommission', 'Other')),
    priority VARCHAR(20) CHECK (priority IN ('Low', 'Medium', 'High', 'Critical')) DEFAULT 'Medium',
    risk_level VARCHAR(20) CHECK (risk_level IN ('Low', 'Medium', 'High')) DEFAULT 'Medium',
    status VARCHAR(50) DEFAULT 'Submitted',
    requested_by INTEGER REFERENCES users(user_id),
    approved_by INTEGER REFERENCES users(user_id),
    implemented_by INTEGER REFERENCES users(user_id),
    planned_start TIMESTAMP,
    planned_end TIMESTAMP,
    actual_start TIMESTAMP,
    actual_end TIMESTAMP,
    rollback_plan TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

**Status Flow:**
```
Submitted → PendingApproval → Approved/Rejected → Implemented → Closed
```

**Indexes:**
- `idx_cr_asset` on `asset_id`
- `idx_cr_status` on `status`
- `idx_cr_requester` on `requested_by`
- `idx_cr_created` on `created_at DESC`

#### 3.2.7 compliance_violations
**Purpose:** Track policy violations

```sql
CREATE TABLE compliance_violations (
    violation_id SERIAL PRIMARY KEY,
    asset_id INTEGER REFERENCES assets(asset_id),
    violation_type VARCHAR(100) NOT NULL,
    severity VARCHAR(20) CHECK (severity IN ('Low', 'Medium', 'High', 'Critical')) DEFAULT 'Medium',
    description TEXT NOT NULL,
    detected_at TIMESTAMP DEFAULT NOW(),
    resolved_at TIMESTAMP,
    resolved_by INTEGER REFERENCES users(user_id),
    status VARCHAR(50) DEFAULT 'Open' CHECK (status IN ('Open', 'InProgress', 'Resolved', 'Ignored')),
    resolution_notes TEXT
);
```

**Indexes:**
- `idx_violation_asset` on `asset_id`
- `idx_violation_status` on `status`
- `idx_violation_severity` on `severity`
- `idx_violation_detected` on `detected_at DESC`

#### 3.2.8 audit_logs
**Purpose:** Immutable audit trail

```sql
CREATE TABLE audit_logs (
    log_id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(user_id),
    action VARCHAR(100) NOT NULL,
    entity_type VARCHAR(50) NOT NULL,
    entity_id INTEGER,
    old_value TEXT,
    new_value TEXT,
    ip_address VARCHAR(45),
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

**Characteristics:**
- Insert-only (no UPDATE or DELETE allowed)
- Partitioned by month for performance
- Indexed on `created_at` for time-range queries

**Indexes:**
- `idx_audit_user` on `user_id`
- `idx_audit_entity` on `entity_type, entity_id`
- `idx_audit_created` on `created_at DESC`

#### 3.2.9 compliance_metrics
**Purpose:** Time-series compliance tracking

```sql
CREATE TABLE compliance_metrics (
    metric_id SERIAL PRIMARY KEY,
    metric_date DATE NOT NULL,
    total_assets INTEGER NOT NULL,
    compliant_assets INTEGER NOT NULL,
    violations_detected INTEGER DEFAULT 0,
    violations_resolved INTEGER DEFAULT 0,
    naming_compliance_rate DECIMAL(5,2),
    documentation_coverage DECIMAL(5,2),
    created_at TIMESTAMP DEFAULT NOW()
);
```

**Indexes:**
- `idx_metric_date` on `metric_date DESC`

**Calculation:**
```sql
-- Daily compliance snapshot
INSERT INTO compliance_metrics (metric_date, total_assets, compliant_assets, naming_compliance_rate)
SELECT
    CURRENT_DATE,
    COUNT(*),
    COUNT(*) FILTER (WHERE is_naming_compliant = TRUE),
    (COUNT(*) FILTER (WHERE is_naming_compliant = TRUE)::DECIMAL / COUNT(*) * 100)
FROM assets
WHERE lifecycle_stage = 'Active';
```

### 3.3 Extended Tables (11)

#### 3.3.1 business_goals
**Purpose:** Strategic business objectives

```sql
CREATE TABLE business_goals (
    goal_id SERIAL PRIMARY KEY,
    goal_name VARCHAR(255) NOT NULL,
    description TEXT,
    goal_type VARCHAR(50) CHECK (goal_type IN ('Revenue', 'Cost', 'Efficiency', 'Quality', 'Risk', 'Other')),
    target_value DECIMAL(15,2),
    current_value DECIMAL(15,2),
    measurement_unit VARCHAR(50),
    start_date DATE,
    target_date DATE,
    status VARCHAR(50) DEFAULT 'Active',
    owner_id INTEGER REFERENCES users(user_id),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

#### 3.3.2 strategic_initiatives
**Purpose:** Multi-year programs and projects

```sql
CREATE TABLE strategic_initiatives (
    initiative_id SERIAL PRIMARY KEY,
    initiative_name VARCHAR(255) NOT NULL,
    description TEXT,
    start_date DATE,
    end_date DATE,
    budget DECIMAL(15,2),
    spent DECIMAL(15,2) DEFAULT 0,
    expected_roi DECIMAL(15,2),
    status VARCHAR(50) DEFAULT 'Planning',
    priority VARCHAR(20) CHECK (priority IN ('Low', 'Medium', 'High', 'Critical')) DEFAULT 'Medium',
    owner_id INTEGER REFERENCES users(user_id),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

#### 3.3.3 initiative_deliverables
**Purpose:** Track project deliverables

```sql
CREATE TABLE initiative_deliverables (
    deliverable_id SERIAL PRIMARY KEY,
    initiative_id INTEGER REFERENCES strategic_initiatives(initiative_id) ON DELETE CASCADE,
    deliverable_name VARCHAR(255) NOT NULL,
    description TEXT,
    due_date DATE,
    completion_date DATE,
    status VARCHAR(50) DEFAULT 'Planned',
    created_at TIMESTAMP DEFAULT NOW()
);
```

#### 3.3.4 vendors
**Purpose:** Vendor/partner management

```sql
CREATE TABLE vendors (
    vendor_id SERIAL PRIMARY KEY,
    vendor_name VARCHAR(255) NOT NULL,
    vendor_type VARCHAR(100) CHECK (vendor_type IN ('Cloud Provider', 'Software Vendor', 'Consulting', 'Other')),
    contact_name VARCHAR(255),
    contact_email VARCHAR(255),
    contact_phone VARCHAR(50),
    contract_start DATE,
    contract_end DATE,
    contract_value DECIMAL(15,2),
    renewal_date DATE,
    status VARCHAR(50) DEFAULT 'Active',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

#### 3.3.5 vendor_slas
**Purpose:** SLA tracking per vendor

```sql
CREATE TABLE vendor_slas (
    sla_id SERIAL PRIMARY KEY,
    vendor_id INTEGER REFERENCES vendors(vendor_id) ON DELETE CASCADE,
    sla_name VARCHAR(255) NOT NULL,
    sla_type VARCHAR(100),
    target_value DECIMAL(10,4),
    actual_value DECIMAL(10,4),
    measurement_period VARCHAR(50) DEFAULT 'Monthly',
    last_measured DATE,
    status VARCHAR(50) DEFAULT 'Active',
    breach_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW()
);
```

#### 3.3.6 stakeholders
**Purpose:** Business stakeholder tracking

```sql
CREATE TABLE stakeholders (
    stakeholder_id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    role VARCHAR(255),
    department VARCHAR(100),
    email VARCHAR(255),
    phone VARCHAR(50),
    influence_level VARCHAR(20) CHECK (influence_level IN ('Low', 'Medium', 'High')) DEFAULT 'Medium',
    interest_level VARCHAR(20) CHECK (interest_level IN ('Low', 'Medium', 'High')) DEFAULT 'Medium',
    created_at TIMESTAMP DEFAULT NOW()
);
```

#### 3.3.7 stakeholder_data_needs
**Purpose:** Track stakeholder data requirements

```sql
CREATE TABLE stakeholder_data_needs (
    need_id SERIAL PRIMARY KEY,
    stakeholder_id INTEGER REFERENCES stakeholders(stakeholder_id) ON DELETE CASCADE,
    need_description TEXT NOT NULL,
    priority VARCHAR(20) CHECK (priority IN ('Low', 'Medium', 'High', 'Critical')) DEFAULT 'Medium',
    frequency VARCHAR(50),
    status VARCHAR(50) DEFAULT 'Requested',
    created_at TIMESTAMP DEFAULT NOW()
);
```

#### 3.3.8 business_use_cases
**Purpose:** Document business use cases

```sql
CREATE TABLE business_use_cases (
    use_case_id SERIAL PRIMARY KEY,
    use_case_name VARCHAR(255) NOT NULL,
    description TEXT,
    business_value TEXT,
    stakeholder_id INTEGER REFERENCES stakeholders(stakeholder_id),
    status VARCHAR(50) DEFAULT 'Draft',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

#### 3.3.9 budget_allocations
**Purpose:** Track budget allocations

```sql
CREATE TABLE budget_allocations (
    allocation_id SERIAL PRIMARY KEY,
    initiative_id INTEGER REFERENCES strategic_initiatives(initiative_id) ON DELETE CASCADE,
    fiscal_year INTEGER NOT NULL,
    quarter INTEGER CHECK (quarter IN (1, 2, 3, 4)),
    allocated_amount DECIMAL(15,2) NOT NULL,
    spent_amount DECIMAL(15,2) DEFAULT 0,
    category VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW()
);
```

#### 3.3.10 asset_business_alignment
**Purpose:** Link assets to business goals

```sql
CREATE TABLE asset_business_alignment (
    alignment_id SERIAL PRIMARY KEY,
    asset_id INTEGER REFERENCES assets(asset_id) ON DELETE CASCADE,
    goal_id INTEGER REFERENCES business_goals(goal_id) ON DELETE CASCADE,
    contribution_level VARCHAR(20) CHECK (contribution_level IN ('Low', 'Medium', 'High')) DEFAULT 'Medium',
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(asset_id, goal_id)
);
```

#### 3.3.11 asset_vendor_mapping
**Purpose:** Link assets to vendors

```sql
CREATE TABLE asset_vendor_mapping (
    mapping_id SERIAL PRIMARY KEY,
    asset_id INTEGER REFERENCES assets(asset_id) ON DELETE CASCADE,
    vendor_id INTEGER REFERENCES vendors(vendor_id) ON DELETE CASCADE,
    service_type VARCHAR(100),
    monthly_cost DECIMAL(15,2),
    start_date DATE,
    end_date DATE,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(asset_id, vendor_id)
);
```

### 3.4 Collaboration Tables (7)

#### 3.4.1 tasks
**Purpose:** Task assignment and tracking

```sql
CREATE TABLE tasks (
    task_id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    assigned_to INTEGER REFERENCES users(user_id),
    created_by INTEGER REFERENCES users(user_id) NOT NULL,
    initiative_id INTEGER REFERENCES strategic_initiatives(initiative_id),
    priority VARCHAR(20) CHECK (priority IN ('Low', 'Medium', 'High', 'Critical')) DEFAULT 'Medium',
    status VARCHAR(50) DEFAULT 'Todo',
    due_date DATE,
    start_date DATE,
    completed_date DATE,
    estimated_hours INTEGER,
    tags TEXT[],
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

**Status Values:** Todo, InProgress, InReview, Blocked, Done, Cancelled

**Indexes:**
- `idx_task_assignee` on `assigned_to`
- `idx_task_status` on `status`
- `idx_task_due` on `due_date`

#### 3.4.2 notifications
**Purpose:** In-app notification system

```sql
CREATE TABLE notifications (
    notification_id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(user_id) ON DELETE CASCADE,
    type VARCHAR(50) NOT NULL,
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    priority VARCHAR(20) CHECK (priority IN ('Low', 'Medium', 'High', 'Critical')) DEFAULT 'Medium',
    read BOOLEAN DEFAULT FALSE NOT NULL,
    read_at TIMESTAMP,
    link TEXT,
    entity_type VARCHAR(50),
    entity_id INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);
```

**Notification Types:**
- TaskAssigned, TaskUpdated, TaskCompleted
- ChangeRequestSubmitted, ChangeRequestApproved, ChangeRequestRejected
- CommentMention, CommentReply
- SLABreach, ComplianceViolation

**Indexes:**
- `idx_notif_user` on `user_id`
- `idx_notif_read` on `read, user_id`
- `idx_notif_created` on `created_at DESC`

#### 3.4.3 comments
**Purpose:** Threaded comment system

```sql
CREATE TABLE comments (
    comment_id SERIAL PRIMARY KEY,
    entity_type VARCHAR(50) NOT NULL,
    entity_id INTEGER NOT NULL,
    parent_comment_id INTEGER REFERENCES comments(comment_id) ON DELETE CASCADE,
    user_id INTEGER REFERENCES users(user_id) NOT NULL,
    comment_text TEXT NOT NULL,
    mentioned_users TEXT,
    edited BOOLEAN DEFAULT FALSE,
    deleted BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

**Entity Types:** asset, change_request, initiative, task, vendor

**Indexes:**
- `idx_comment_entity` on `entity_type, entity_id`
- `idx_comment_parent` on `parent_comment_id`
- `idx_comment_user` on `user_id`
- `idx_comment_created` on `created_at DESC`

#### 3.4.4 activity_logs
**Purpose:** User activity feed

```sql
CREATE TABLE activity_logs (
    activity_id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(user_id),
    action VARCHAR(100) NOT NULL,
    entity_type VARCHAR(50) NOT NULL,
    entity_id INTEGER,
    entity_name VARCHAR(255),
    description TEXT,
    meta_data TEXT,  -- Changed from 'metadata' (reserved keyword)
    created_at TIMESTAMP DEFAULT NOW()
);
```

**Actions:** created, updated, deleted, approved, rejected, commented, completed, assigned

**Indexes:**
- `idx_activity_user` on `user_id`
- `idx_activity_entity` on `entity_type, entity_id`
- `idx_activity_created` on `created_at DESC`

#### 3.4.5 itsm_configurations
**Purpose:** ITSM integration settings

```sql
CREATE TABLE itsm_configurations (
    config_id SERIAL PRIMARY KEY,
    system_type VARCHAR(50) CHECK (system_type IN ('ServiceNow', 'Jira', 'Slack')) NOT NULL,
    system_name VARCHAR(100) NOT NULL,
    base_url TEXT NOT NULL,
    api_key TEXT,
    username VARCHAR(100),
    webhook_url TEXT,
    sync_direction VARCHAR(50) DEFAULT 'Bidirectional',
    sync_enabled BOOLEAN DEFAULT TRUE,
    field_mappings JSON,
    last_sync TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

#### 3.4.6 itsm_record_mappings
**Purpose:** Map portal entities to ITSM records

```sql
CREATE TABLE itsm_record_mappings (
    mapping_id SERIAL PRIMARY KEY,
    config_id INTEGER REFERENCES itsm_configurations(config_id) ON DELETE CASCADE,
    entity_type VARCHAR(50) NOT NULL,
    entity_id INTEGER NOT NULL,
    itsm_record_type VARCHAR(100),
    itsm_record_id VARCHAR(100) NOT NULL,
    sync_status VARCHAR(50) DEFAULT 'Synced',
    last_synced TIMESTAMP,
    portal_version INTEGER DEFAULT 1,
    itsm_version INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(config_id, entity_type, entity_id)
);
```

#### 3.4.7 itsm_sync_logs
**Purpose:** Track ITSM sync operations

```sql
CREATE TABLE itsm_sync_logs (
    log_id SERIAL PRIMARY KEY,
    config_id INTEGER REFERENCES itsm_configurations(config_id) ON DELETE CASCADE,
    mapping_id INTEGER REFERENCES itsm_record_mappings(mapping_id),
    sync_direction VARCHAR(20) CHECK (sync_direction IN ('ToITSM', 'FromITSM', 'Bidirectional')),
    sync_status VARCHAR(50) CHECK (sync_status IN ('Success', 'Failed', 'Conflict')) NOT NULL,
    error_message TEXT,
    records_synced INTEGER DEFAULT 0,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### 3.5 Database Relationships

**Entity Relationship Diagram (ERD):**

```
users ──┬─── assets (owner_id)
        ├─── domains (owner_id)
        ├─── business_goals (owner_id)
        ├─── strategic_initiatives (owner_id)
        ├─── tasks (assigned_to, created_by)
        ├─── notifications (user_id)
        ├─── comments (user_id)
        └─── activity_logs (user_id)

assets ─┬─── lifecycle_history (asset_id)
        ├─── change_requests (asset_id)
        ├─── compliance_violations (asset_id)
        ├─── asset_business_alignment (asset_id)
        └─── asset_vendor_mapping (asset_id)

vendors ┬─── vendor_slas (vendor_id)
        └─── asset_vendor_mapping (vendor_id)

strategic_initiatives ─┬─── initiative_deliverables (initiative_id)
                       ├─── budget_allocations (initiative_id)
                       └─── tasks (initiative_id)

business_goals ──── asset_business_alignment (goal_id)

stakeholders ─┬─── stakeholder_data_needs (stakeholder_id)
              └─── business_use_cases (stakeholder_id)

comments ──── comments (parent_comment_id) [self-referencing]

itsm_configurations ─┬─── itsm_record_mappings (config_id)
                     └─── itsm_sync_logs (config_id)

itsm_record_mappings ──── itsm_sync_logs (mapping_id)
```

### 3.6 Database Indexes Strategy

**Index Types:**
1. **Primary Key Indexes** (automatic)
2. **Foreign Key Indexes** (created explicitly)
3. **Search Indexes** (for frequently searched columns)
4. **Composite Indexes** (for multi-column queries)
5. **Partial Indexes** (for filtered queries)

**Example Composite Indexes:**
```sql
-- Fast queries on active assets by domain
CREATE INDEX idx_assets_active_domain
ON assets(domain_id, lifecycle_stage)
WHERE lifecycle_stage = 'Active';

-- Fast queries on unread notifications per user
CREATE INDEX idx_notifications_unread_user
ON notifications(user_id, created_at DESC)
WHERE read = FALSE;

-- Fast queries on open violations by severity
CREATE INDEX idx_violations_open_severity
ON compliance_violations(severity, detected_at DESC)
WHERE status = 'Open';
```

### 3.7 Database Backup Strategy

**Backup Schedule:**
- **Full Backup:** Daily at 2:00 AM UTC (retained for 30 days)
- **Incremental Backup:** Every 4 hours (retained for 7 days)
- **Transaction Log Backup:** Every 15 minutes (retained for 2 days)

**Backup Commands:**
```bash
# Full backup
pg_dump -h localhost -U postgres -F c -b -v -f "governance_portal_$(date +%Y%m%d).backup" governance_portal

# Restore from backup
pg_restore -h localhost -U postgres -d governance_portal -v "governance_portal_20260225.backup"
```

---

## 4. API Documentation

### 4.1 API Base URL

**Local Development:**
```
http://localhost:8000/api/v1
```

**Production:**
```
https://api.governance.company.com/api/v1
```

### 4.2 Authentication

All API endpoints (except `/auth/login` and `/auth/register`) require authentication via JWT token.

**Login:**
```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "username": "admin",
  "password": "password123"
}

Response:
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "user_id": 1,
    "username": "admin",
    "email": "admin@company.com",
    "role": "Admin"
  }
}
```

**Using Token:**
```http
GET /api/v1/assets
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### 4.3 Asset Management API

#### GET /api/v1/assets
**Purpose:** List all assets with filtering

**Query Parameters:**
- `domain_id` (int): Filter by domain
- `owner_id` (int): Filter by owner
- `environment` (str): Filter by environment (DEV, QA, UAT, PROD)
- `lifecycle_stage` (str): Filter by lifecycle
- `skip` (int): Pagination offset (default: 0)
- `limit` (int): Pagination limit (default: 100, max: 500)

**Example:**
```http
GET /api/v1/assets?domain_id=1&environment=PROD&limit=50
Authorization: Bearer {token}

Response: 200 OK
[
  {
    "asset_id": 1,
    "asset_name": "PROD-HR-DW-v1",
    "domain": {
      "domain_id": 1,
      "domain_code": "HR",
      "domain_name": "Human Resources"
    },
    "owner": {
      "user_id": 2,
      "username": "sarah",
      "full_name": "Sarah Johnson"
    },
    "environment": "PROD",
    "version": "v1",
    "lifecycle_stage": "Active",
    "description": "HR data warehouse for employee analytics",
    "documentation_url": "https://docs.company.com/hr-dw",
    "created_at": "2026-01-15T10:30:00Z",
    "updated_at": "2026-02-10T14:20:00Z"
  },
  ...
]
```

#### POST /api/v1/assets
**Purpose:** Create new asset

**Request Body:**
```json
{
  "asset_name": "PROD-FIN-ETL-v2",
  "domain_id": 2,
  "owner_id": 3,
  "environment": "PROD",
  "version": "v2.0",
  "lifecycle_stage": "Active",
  "description": "Finance ETL pipeline for quarterly reporting",
  "documentation_url": "https://docs.company.com/fin-etl",
  "business_justification": "Supports quarterly financial reporting to board"
}
```

**Response:**
```json
{
  "asset_id": 15,
  "asset_name": "PROD-FIN-ETL-v2",
  "message": "Asset created successfully"
}
```

#### PUT /api/v1/assets/{asset_id}
**Purpose:** Update existing asset

**Request Body:** (same as POST, all fields optional)

**Response:** 200 OK with updated asset

#### DELETE /api/v1/assets/{asset_id}
**Purpose:** Soft delete asset (marks as Decommissioned)

**Response:** 200 OK

### 4.4 Compliance API

#### GET /api/v1/compliance/metrics
**Purpose:** Get compliance KPIs

**Response:**
```json
{
  "total_assets": 523,
  "naming_compliance_rate": 96.5,
  "compliant_assets": 504,
  "non_compliant_assets": 19,
  "documentation_coverage": 94.3,
  "assets_with_documentation": 493,
  "violations": {
    "total": 18,
    "critical": 3,
    "high": 5,
    "medium": 7,
    "low": 3
  },
  "avg_remediation_time_days": 18
}
```

#### GET /api/v1/compliance/violations
**Purpose:** List compliance violations

**Query Parameters:**
- `status` (str): Open, InProgress, Resolved, Ignored
- `severity` (str): Low, Medium, High, Critical
- `asset_id` (int): Filter by asset

**Response:**
```json
[
  {
    "violation_id": 1,
    "asset": {
      "asset_id": 45,
      "asset_name": "production-sales-etl"
    },
    "violation_type": "Naming Convention",
    "severity": "High",
    "description": "Asset name does not follow standard format",
    "detected_at": "2026-02-20T08:00:00Z",
    "status": "Open",
    "suggested_fix": "PROD-SALES-ETL-v1"
  },
  ...
]
```

#### POST /api/v1/compliance/validate/naming
**Purpose:** Validate asset name against naming standard

**Request Body:**
```json
{
  "asset_name": "PROD-HR-DW-v1"
}
```

**Response:**
```json
{
  "is_valid": true,
  "errors": [],
  "suggestions": null
}
```

**Invalid Example Response:**
```json
{
  "is_valid": false,
  "errors": [
    "Environment must be DEV, QA, UAT, or PROD",
    "Missing version",
    "Must use uppercase"
  ],
  "suggestions": "Did you mean: PROD-HR-DW-v1?"
}
```

### 4.5 Strategy API

#### GET /api/v1/strategy/summary
**Purpose:** Executive summary of strategic metrics

**Response:**
```json
{
  "total_goals": 12,
  "active_initiatives": 5,
  "total_budget": 15000000.00,
  "spent_budget": 5400000.00,
  "budget_utilization": 36.0,
  "on_track_initiatives": 4,
  "at_risk_initiatives": 1,
  "avg_roi": 215.5
}
```

#### GET /api/v1/strategy/goals
**Purpose:** List business goals

**Response:**
```json
[
  {
    "goal_id": 1,
    "goal_name": "Reduce infrastructure costs by 40%",
    "goal_type": "Cost",
    "target_value": 40.0,
    "current_value": 25.0,
    "measurement_unit": "Percentage",
    "progress": 62.5,
    "status": "On Track",
    "owner": {
      "user_id": 1,
      "full_name": "John Smith"
    },
    "linked_assets_count": 15,
    "target_date": "2027-12-31"
  },
  ...
]
```

#### GET /api/v1/strategy/initiatives
**Purpose:** List strategic initiatives

**Query Parameters:**
- `status` (str): Planning, InProgress, OnHold, Completed, Cancelled
- `owner_id` (int): Filter by owner

**Response:**
```json
[
  {
    "initiative_id": 1,
    "initiative_name": "Data Platform Modernization",
    "description": "Migrate legacy data warehouse to cloud-native platform",
    "start_date": "2026-01-01",
    "end_date": "2027-12-31",
    "budget": 5000000.00,
    "spent": 1200000.00,
    "budget_utilization": 24.0,
    "expected_roi": 15000000.00,
    "status": "InProgress",
    "priority": "High",
    "progress": 25.0,
    "deliverables_count": 8,
    "completed_deliverables": 2,
    "owner": {
      "user_id": 1,
      "full_name": "John Smith"
    }
  },
  ...
]
```

### 4.6 Task Management API

#### GET /api/v1/tasks
**Purpose:** List tasks

**Query Parameters:**
- `status` (str): Todo, InProgress, InReview, Blocked, Done, Cancelled
- `priority` (str): Low, Medium, High, Critical
- `assigned_to` (int): Filter by assignee
- `overdue` (bool): Show only overdue tasks

**Response:**
```json
[
  {
    "task_id": 1,
    "title": "Audit Finance domain data quality",
    "description": "Review all finance assets for data quality issues",
    "priority": "High",
    "status": "InProgress",
    "assigned_to": {
      "user_id": 3,
      "full_name": "Sarah Johnson"
    },
    "created_by": {
      "user_id": 2,
      "full_name": "Mike Chen"
    },
    "due_date": "2026-03-31",
    "is_overdue": false,
    "tags": ["audit", "data-quality", "finance"],
    "created_at": "2026-02-15T10:00:00Z"
  },
  ...
]
```

#### POST /api/v1/tasks
**Purpose:** Create task

**Request Body:**
```json
{
  "title": "Review vendor SLA compliance",
  "description": "Quarterly SLA review for all critical vendors",
  "assigned_to": 4,
  "priority": "Medium",
  "due_date": "2026-04-30",
  "tags": ["vendors", "sla", "quarterly-review"]
}
```

**Response:** 201 Created with task object

### 4.7 Notification API

#### GET /api/v1/notifications
**Purpose:** Get user notifications

**Query Parameters:**
- `read` (bool): Filter by read status
- `limit` (int): Max results (default: 20)

**Response:**
```json
[
  {
    "notification_id": 1,
    "type": "TaskAssigned",
    "title": "New task assigned",
    "message": "Mike Chen assigned you a task: 'Audit Finance domain data quality'",
    "priority": "High",
    "read": false,
    "link": "/tasks/1",
    "entity_type": "task",
    "entity_id": 1,
    "created_at": "2026-02-25T09:30:00Z"
  },
  ...
]
```

#### GET /api/v1/notifications/unread-count
**Purpose:** Get unread notification count

**Response:**
```json
{
  "unread_count": 5
}
```

#### POST /api/v1/notifications/{notification_id}/read
**Purpose:** Mark notification as read

**Response:** 200 OK

#### POST /api/v1/notifications/read-all
**Purpose:** Mark all notifications as read

**Response:**
```json
{
  "updated_count": 5
}
```

### 4.8 Comment API

#### GET /api/v1/comments
**Purpose:** Get comments for entity

**Query Parameters:**
- `entity_type` (str): asset, change_request, initiative, task, vendor
- `entity_id` (int): Entity ID
- `include_replies` (bool): Include nested replies (default: false)

**Response:**
```json
[
  {
    "comment_id": 1,
    "entity_type": "asset",
    "entity_id": 15,
    "user": {
      "user_id": 2,
      "full_name": "Mike Chen"
    },
    "comment_text": "This asset needs documentation update @sarah",
    "mentioned_users": [3],
    "edited": false,
    "deleted": false,
    "replies": [
      {
        "comment_id": 2,
        "parent_comment_id": 1,
        "user": {
          "user_id": 3,
          "full_name": "Sarah Johnson"
        },
        "comment_text": "I'll update the docs by end of week",
        "created_at": "2026-02-25T10:15:00Z"
      }
    ],
    "created_at": "2026-02-25T10:00:00Z"
  },
  ...
]
```

#### POST /api/v1/comments
**Purpose:** Create comment

**Request Body:**
```json
{
  "entity_type": "asset",
  "entity_id": 15,
  "comment_text": "This asset needs documentation update @sarah",
  "parent_comment_id": null,
  "mentioned_users": [3]
}
```

**Response:** 201 Created with comment object

### 4.9 Activity Feed API

#### GET /api/v1/activity
**Purpose:** Get activity feed

**Query Parameters:**
- `entity_type` (str): Filter by entity type
- `user_id` (int): Filter by user
- `action` (str): Filter by action (created, updated, deleted, etc.)
- `days` (int): Show activities from last N days
- `limit` (int): Max results (default: 50, max: 200)

**Response:**
```json
[
  {
    "activity_id": 1,
    "user": {
      "user_id": 2,
      "full_name": "Mike Chen"
    },
    "action": "created",
    "entity_type": "asset",
    "entity_id": 15,
    "entity_name": "PROD-FIN-ETL-v2",
    "description": "Mike Chen created asset PROD-FIN-ETL-v2",
    "created_at": "2026-02-25T09:00:00Z"
  },
  ...
]
```

### 4.10 Error Responses

**Standard Error Format:**
```json
{
  "detail": "Asset not found",
  "status_code": 404,
  "error_type": "NotFound"
}
```

**HTTP Status Codes:**
- `200 OK` - Success
- `201 Created` - Resource created
- `400 Bad Request` - Invalid input
- `401 Unauthorized` - Missing or invalid token
- `403 Forbidden` - Insufficient permissions
- `404 Not Found` - Resource not found
- `422 Unprocessable Entity` - Validation error
- `500 Internal Server Error` - Server error

---

## 5. Authentication & Authorization

### 5.1 JWT Authentication

**Token Structure:**
```json
{
  "sub": "admin",
  "user_id": 1,
  "role": "Admin",
  "exp": 1709049600
}
```

**Token Lifetime:** 24 hours (configurable via `ACCESS_TOKEN_EXPIRE_MINUTES`)

**Token Generation:**
```python
from jose import jwt
from datetime import datetime, timedelta

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=1440)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
```

**Token Validation:**
```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt

security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("user_id")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = db.query(User).filter(User.user_id == user_id).first()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user
```

### 5.2 Role-Based Access Control (RBAC)

**Roles:**
1. **Admin** - Full system access
2. **DataSteward** - Manage assets in assigned domains
3. **AssetOwner** - Manage owned assets only
4. **Viewer** - Read-only access

**Permission Matrix:**

| Action | Admin | DataSteward | AssetOwner | Viewer |
|--------|-------|-------------|------------|--------|
| **Assets** |
| View All Assets | ✅ | ✅ | ✅ | ✅ |
| Create Asset | ✅ | ✅ | ❌ | ❌ |
| Edit Any Asset | ✅ | ✅ (domain) | ❌ | ❌ |
| Edit Own Asset | ✅ | ✅ | ✅ | ❌ |
| Delete Asset | ✅ | ❌ | ❌ | ❌ |
| **Change Requests** |
| Submit CR | ✅ | ✅ | ✅ | ❌ |
| Approve CR | ✅ | ✅ | ❌ | ❌ |
| **Vendors** |
| View Vendors | ✅ | ✅ | ✅ | ✅ |
| Manage Vendors | ✅ | ✅ | ❌ | ❌ |
| **Strategy** |
| View Goals/Initiatives | ✅ | ✅ | ✅ | ✅ |
| Manage Goals/Initiatives | ✅ | ❌ | ❌ | ❌ |
| **Users** |
| View Users | ✅ | ✅ | ✅ | ✅ |
| Manage Users | ✅ | ❌ | ❌ | ❌ |
| **Tasks** |
| View All Tasks | ✅ | ✅ | ❌ | ❌ |
| View Assigned Tasks | ✅ | ✅ | ✅ | ✅ |
| Create Task | ✅ | ✅ | ❌ | ❌ |
| Edit Any Task | ✅ | ✅ | ❌ | ❌ |
| Edit Own Task | ✅ | ✅ | ✅ | ❌ |

**Authorization Decorator:**
```python
from functools import wraps
from fastapi import HTTPException, status

def require_role(allowed_roles: list):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, current_user: User = None, **kwargs):
            if current_user.role.role_name not in allowed_roles:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Insufficient permissions. Required roles: {allowed_roles}"
                )
            return await func(*args, current_user=current_user, **kwargs)
        return wrapper
    return decorator

# Usage:
@router.delete("/assets/{asset_id}")
@require_role(["Admin"])
def delete_asset(asset_id: int, current_user: User = Depends(get_current_user)):
    # Only admins can delete assets
    ...
```

### 5.3 Password Security

**Password Hashing:**
```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)
```

**Password Requirements:**
- Minimum length: 8 characters
- Must contain: uppercase, lowercase, number, special character
- Cannot be same as username or email
- Password history: Cannot reuse last 5 passwords

---

## 6. ITSM Integration

### 6.1 ServiceNow Integration

**Purpose:** Bidirectional sync with ServiceNow Change Management and CMDB

**Configuration:**
```python
# backend/app/services/servicenow_integration.py

class ServiceNowIntegration:
    def __init__(self, base_url: str, username: str, password: str):
        self.base_url = base_url
        self.auth = (username, password)
        self.headers = {"Content-Type": "application/json"}

    def sync_change_request_to_servicenow(self, change_request: ChangeRequest):
        """Push change request from portal to ServiceNow"""
        servicenow_data = self._map_change_request_to_servicenow(change_request)

        # Check if mapping exists (update) or create new
        mapping = db.query(ITSMRecordMapping).filter(
            ITSMRecordMapping.entity_type == "change_request",
            ITSMRecordMapping.entity_id == change_request.change_request_id
        ).first()

        if mapping:
            # Update existing CR in ServiceNow
            response = self.client.update_change_request(mapping.itsm_record_id, servicenow_data)
        else:
            # Create new CR in ServiceNow
            response = self.client.create_change_request(servicenow_data)
            # Store mapping
            mapping = ITSMRecordMapping(
                config_id=self.config_id,
                entity_type="change_request",
                entity_id=change_request.change_request_id,
                itsm_record_type="change_request",
                itsm_record_id=response["result"]["sys_id"],
                sync_status="Synced"
            )
            db.add(mapping)
            db.commit()

        return response

    def _map_change_request_to_servicenow(self, cr: ChangeRequest):
        """Map portal CR fields to ServiceNow fields"""
        return {
            "short_description": cr.title,
            "description": cr.description,
            "type": self._map_change_type(cr.change_type),
            "priority": self._map_priority(cr.priority),
            "risk": self._map_risk_level(cr.risk_level),
            "state": self._map_status(cr.status),
            "requested_by": cr.requester.email,
            "start_date": cr.planned_start.isoformat() if cr.planned_start else None,
            "end_date": cr.planned_end.isoformat() if cr.planned_end else None,
            "backout_plan": cr.rollback_plan,
            "u_portal_id": cr.change_request_id  # Custom field in ServiceNow
        }
```

**Sync Directions:**
1. **Portal → ServiceNow** (ToITSM)
   - User submits CR in portal → Automatically create in ServiceNow
   - Portal CR approved → Update ServiceNow CR state

2. **ServiceNow → Portal** (FromITSM)
   - ServiceNow CR approved → Update portal CR status
   - ServiceNow CR implemented → Sync completion details to portal

3. **Bidirectional** (default)
   - Changes in either system sync to the other
   - Conflict resolution based on version numbers

**Conflict Resolution:**
```python
def resolve_conflict(portal_cr: ChangeRequest, servicenow_cr: dict):
    """Resolve conflicts when both systems have updates"""
    portal_version = portal_cr.version
    servicenow_version = servicenow_cr["sys_mod_count"]

    if portal_version > servicenow_version:
        # Portal wins - push to ServiceNow
        return "ToITSM"
    elif servicenow_version > portal_version:
        # ServiceNow wins - pull from ServiceNow
        return "FromITSM"
    else:
        # Same version - check timestamps
        portal_updated = portal_cr.updated_at
        servicenow_updated = datetime.fromisoformat(servicenow_cr["sys_updated_on"])
        return "ToITSM" if portal_updated > servicenow_updated else "FromITSM"
```

### 6.2 Jira Integration

**Purpose:** Create Jira epics and stories from strategic initiatives

**Configuration:**
```python
# backend/app/services/jira_integration.py

class JiraIntegration:
    def __init__(self, base_url: str, email: str, api_token: str):
        self.base_url = base_url
        self.auth = (email, api_token)
        self.headers = {"Content-Type": "application/json"}

    def create_epic_from_initiative(self, initiative: StrategicInitiative, project_key: str):
        """Create Jira epic from strategic initiative"""
        epic_data = {
            "fields": {
                "project": {"key": project_key},
                "summary": initiative.initiative_name,
                "description": initiative.description,
                "issuetype": {"name": "Epic"},
                "priority": {"name": self._map_priority(initiative.priority)},
                "labels": ["daas-portal", f"initiative-{initiative.initiative_id}"],
                "customfield_10011": initiative.initiative_name,  # Epic Name field
                "duedate": initiative.end_date.isoformat() if initiative.end_date else None
            }
        }

        response = self.client.create_epic(epic_data)
        epic_key = response["key"]
        epic_id = response["id"]

        # Store mapping
        mapping = ITSMRecordMapping(
            config_id=self.config_id,
            entity_type="initiative",
            entity_id=initiative.initiative_id,
            itsm_record_type="epic",
            itsm_record_id=epic_id,
            sync_status="Synced"
        )
        db.add(mapping)

        # Create stories for deliverables
        for deliverable in initiative.deliverables:
            self.create_story_from_deliverable(deliverable, epic_key, project_key)

        db.commit()
        return response

    def create_story_from_deliverable(self, deliverable: InitiativeDeliverable, epic_key: str, project_key: str):
        """Create Jira story from deliverable"""
        story_data = {
            "fields": {
                "project": {"key": project_key},
                "summary": deliverable.deliverable_name,
                "description": deliverable.description,
                "issuetype": {"name": "Story"},
                "parent": {"key": epic_key},
                "labels": ["daas-portal", f"deliverable-{deliverable.deliverable_id}"],
                "duedate": deliverable.due_date.isoformat() if deliverable.due_date else None
            }
        }

        response = self.client.create_story(story_data)

        # Store mapping
        mapping = ITSMRecordMapping(
            config_id=self.config_id,
            entity_type="deliverable",
            entity_id=deliverable.deliverable_id,
            itsm_record_type="story",
            itsm_record_id=response["id"],
            sync_status="Synced"
        )
        db.add(mapping)
        db.commit()

        return response
```

**Status Sync:**
- Portal initiative status → Jira epic status
- Jira story status → Portal deliverable status

**Status Mapping:**
| Portal Status | Jira Status |
|---------------|-------------|
| Planning | To Do |
| InProgress | In Progress |
| OnHold | On Hold |
| Completed | Done |
| Cancelled | Cancelled |

### 6.3 Slack Integration

**Purpose:** Send rich formatted notifications to Slack channels

**Configuration:**
```python
# backend/app/services/slack_notifier.py

class SlackNotifier:
    def __init__(self, webhook_url: str, default_channel: str = "#data-governance"):
        self.webhook_url = webhook_url
        self.default_channel = default_channel

    def send_notification(
        self,
        title: str,
        message: str,
        notification_type: SlackNotificationType,
        priority: SlackNotificationPriority,
        link: str = None,
        channel: str = None
    ):
        """Send formatted notification to Slack"""
        color = self._get_color(priority)
        icon = self._get_icon(notification_type)

        payload = {
            "channel": channel or self.default_channel,
            "username": "DaaS Governance Portal",
            "icon_emoji": ":bar_chart:",
            "attachments": [
                {
                    "color": color,
                    "blocks": [
                        {
                            "type": "header",
                            "text": {
                                "type": "plain_text",
                                "text": f"{icon} {title}",
                                "emoji": True
                            }
                        },
                        {
                            "type": "section",
                            "text": {
                                "type": "mrkdwn",
                                "text": message
                            }
                        }
                    ]
                }
            ]
        }

        if link:
            payload["attachments"][0]["blocks"].append({
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "View in Portal"
                        },
                        "url": link,
                        "style": "primary"
                    }
                ]
            })

        response = requests.post(self.webhook_url, json=payload)
        return response.status_code == 200
```

**Notification Types:**
- **TaskAssigned:** 📋 "New task assigned to you"
- **ChangeRequestApproved:** ✅ "Your change request has been approved"
- **SLABreach:** ⚠️ "Vendor SLA breach detected"
- **ComplianceViolation:** 🚨 "Compliance violation detected"

**Example Slack Message:**
```
┌────────────────────────────────────────────┐
│ 🚨 Compliance Violation Detected           │
├────────────────────────────────────────────┤
│ Asset: production-sales-etl                │
│ Issue: Naming convention violation         │
│ Severity: High                             │
│ Action Required: Rename to PROD-SALES-ETL-v1│
│                                            │
│ [View in Portal]                           │
└────────────────────────────────────────────┘
```

---

## 7. Implementation Guide

### 7.1 Local Development Setup

**Prerequisites:**
- Python 3.10+
- Node.js 18+
- PostgreSQL 14+
- Git

**Step 1: Clone Repository**
```bash
git clone https://github.com/company/enterprise-daas-portal.git
cd enterprise-daas-portal
```

**Step 2: Backend Setup**
```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create PostgreSQL database
sudo -u postgres createdb governance_portal

# Create .env file
cat > .env <<EOF
DATABASE_URL=postgresql://postgres:password@localhost/governance_portal
SECRET_KEY=$(openssl rand -hex 32)
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
EOF

# Initialize database with Alembic
alembic upgrade head

# Seed sample data
python seed_data.py

# Start backend server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Step 3: Frontend Setup**
```bash
cd ../frontend

# Install dependencies
npm install

# Start dev server
npm run dev
```

**Step 4: Access Application**
- Frontend: http://localhost:5173
- Backend API Docs: http://localhost:8000/api/docs
- Default Login: username=`admin`, password=`admin123`

### 7.2 Database Migrations

**Create Migration:**
```bash
cd backend
alembic revision --autogenerate -m "description of changes"
```

**Apply Migration:**
```bash
alembic upgrade head
```

**Rollback Migration:**
```bash
alembic downgrade -1  # Rollback 1 version
alembic downgrade <revision_id>  # Rollback to specific version
```

**View Migration History:**
```bash
alembic history
alembic current
```

### 7.3 Testing

**Run Tests:**
```bash
cd backend
pytest tests/ -v
```

**Run with Coverage:**
```bash
pytest tests/ --cov=app --cov-report=html
```

**Test Categories:**
- Unit tests: `tests/unit/`
- Integration tests: `tests/integration/`
- E2E tests: `tests/e2e/`

### 7.4 Code Quality

**Backend Linting:**
```bash
cd backend
flake8 app/
black app/
```

**Frontend Linting:**
```bash
cd frontend
npm run lint
npm run lint:fix
```

---

## 8. Deployment Architecture

### 8.1 Production Architecture (AWS)

```
┌─────────────────────────────────────────────────────┐
│                   Amazon CloudFront                  │
│          (CDN for frontend static files)             │
└────────────────┬────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────┐
│              Amazon S3 (Frontend)                    │
│         React SPA static files (dist/)               │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│         Application Load Balancer (ALB)              │
│              HTTPS/TLS Termination                   │
└────────────────┬────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────┐
│          Amazon ECS/Fargate (Backend)                │
│   ┌──────────────┐        ┌──────────────┐          │
│   │   FastAPI    │        │   FastAPI    │          │
│   │   Instance 1 │        │   Instance 2 │          │
│   └──────┬───────┘        └──────┬───────┘          │
│          │                       │                   │
│          └───────────┬───────────┘                   │
└────────────────────────┼─────────────────────────────┘
                         │
┌────────────────────────▼─────────────────────────────┐
│              Amazon RDS PostgreSQL                    │
│               (Multi-AZ Deployment)                   │
│                                                       │
│   Primary ───────────> Standby                       │
│   (us-east-1a)         (us-east-1b)                  │
│                                                       │
│   Read Replica (optional for reporting)              │
└───────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────┐
│          Amazon ElastiCache (Redis)                   │
│            Session & API Response Caching             │
└───────────────────────────────────────────────────────┘
```

### 8.2 Container Configuration

**Dockerfile (Backend):**
```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**docker-compose.yml (Local Development):**
```yaml
version: '3.8'

services:
  postgres:
    image: postgres:14
    environment:
      POSTGRES_DB: governance_portal
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://postgres:password@postgres/governance_portal
      SECRET_KEY: your-secret-key-here
    depends_on:
      - postgres
    volumes:
      - ./backend:/app

  frontend:
    build: ./frontend
    ports:
      - "5173:5173"
    volumes:
      - ./frontend:/app
      - /app/node_modules

volumes:
  postgres_data:
```

### 8.3 Environment Variables

**Backend (.env):**
```bash
# Database
DATABASE_URL=postgresql://user:pass@hostname:5432/governance_portal

# Security
SECRET_KEY=your-secret-key-min-32-chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# CORS
ALLOWED_ORIGINS=https://portal.company.com,http://localhost:5173

# ITSM Integrations
SERVICENOW_URL=https://company.service-now.com
SERVICENOW_USERNAME=api_user
SERVICENOW_PASSWORD=password

JIRA_URL=https://company.atlassian.net
JIRA_EMAIL=api@company.com
JIRA_API_TOKEN=token

SLACK_WEBHOOK_URL=https://hooks.slack.com/services/xxx/yyy/zzz
SLACK_CHANNEL=#data-governance

# AWS (for production)
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=xxx
AWS_SECRET_ACCESS_KEY=yyy
```

### 8.4 Scaling Strategy

**Horizontal Scaling:**
- Backend: ECS auto-scaling based on CPU/memory (2-10 instances)
- Database: Read replicas for reporting queries
- Caching: Redis cluster for session management

**Vertical Scaling:**
- Backend: Start with t3.medium, scale to t3.large if needed
- Database: Start with db.t3.medium, scale to db.m5.large for production
- Redis: Start with cache.t3.micro, scale to cache.m5.large

**Performance Targets:**
- API Response Time: <500ms (P95)
- Page Load Time: <2 seconds (P95)
- Concurrent Users: 200+
- Database Connections: Pool of 20-50

### 8.5 Docker Deployment

**Quick Start:**
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down
```

**Database Management in Docker:**
```bash
# Run migrations
docker-compose exec backend alembic upgrade head

# Seed database
docker-compose exec backend python seed_data.py

# Access PostgreSQL
docker-compose exec postgres psql -U postgres -d governance_portal

# Backup database
docker-compose exec postgres pg_dump -U postgres governance_portal > backup_$(date +%Y%m%d).sql

# Restore database
docker-compose exec -T postgres psql -U postgres -d governance_portal < backup.sql
```

**Docker Troubleshooting:**

**Issue: Backend won't start**
```bash
# Check logs
docker-compose logs backend

# Common causes:
# 1. Database not ready - wait 10 seconds and retry
# 2. Port already in use - stop conflicting service
# 3. Missing .env file - create backend/.env

# Restart backend
docker-compose restart backend
```

**Issue: Database connection error**
```bash
# Test connectivity
docker-compose exec backend ping postgres

# Check database is running
docker-compose ps postgres

# Verify connection string
docker-compose exec backend env | grep DATABASE_URL
```

**Issue: Frontend shows 404**
```bash
# Rebuild frontend
docker-compose build frontend
docker-compose up -d frontend

# Check nginx config (if using nginx)
docker-compose exec frontend cat /etc/nginx/conf.d/default.conf
```

**Production Docker Deployment:**

**Step 1: Build Images**
```bash
# Build backend
docker build -t company/daas-portal-backend:v3.0 ./backend

# Build frontend
docker build -t company/daas-portal-frontend:v3.0 ./frontend

# Tag as latest
docker tag company/daas-portal-backend:v3.0 company/daas-portal-backend:latest
docker tag company/daas-portal-frontend:v3.0 company/daas-portal-frontend:latest
```

**Step 2: Push to Registry**
```bash
# Push to Docker Hub or AWS ECR
docker push company/daas-portal-backend:v3.0
docker push company/daas-portal-frontend:v3.0
```

**Step 3: Deploy to Server**
```bash
# On production server
docker pull company/daas-portal-backend:v3.0
docker pull company/daas-portal-frontend:v3.0

# Update docker-compose.yml to use production images
# Start services
docker-compose -f docker-compose.prod.yml up -d
```

**Step 4: SSL with Nginx**
```yaml
# docker-compose.prod.yml - add nginx service
nginx:
  image: nginx:alpine
  ports:
    - "80:80"
    - "443:443"
  volumes:
    - ./nginx.conf:/etc/nginx/nginx.conf
    - ./ssl:/etc/nginx/ssl
  depends_on:
    - backend
    - frontend
```

**Health Checks:**
```yaml
# Add to docker-compose.yml
services:
  backend:
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
```

---

**Document Version:** 3.0
**Last Updated:** February 25, 2026
**Next Review Date:** May 25, 2026
**Document Owner:** Chief Technology Officer
**Status:** Published
