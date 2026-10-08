# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Enterprise DaaS Governance Portal** - Executive-grade governance platform for Data-as-a-Service operations with strategic leadership capabilities.

This is a full-stack web application that enables enterprise organizations to:
- Register and manage data/platform assets with lifecycle tracking
- Enforce naming conventions and compliance policies automatically
- Track strategic business goals, ROI, and vendor relationships
- Generate executive-level reports and board presentations
- Manage budgets, SLAs, and stakeholder data needs

**Current Status:** Functional prototype (v2.0) → Production-ready product (v3.0)

---

## ⚠️ CRITICAL: Design Document - Read This First!

**Before making ANY changes to this codebase, you MUST:**

1. **Read `/DESIGN.md`** - The MASTER design document (Single Source of Truth)
2. Follow the change management process outlined in DESIGN.md
3. Update DESIGN.md BEFORE and AFTER making changes

### Why This Matters:

This project previously suffered from **cascading failures** where:
- ❌ Changing one component broke others
- ❌ Database schema didn't match models
- ❌ Models didn't match API expectations
- ❌ APIs didn't match frontend needs
- ❌ Seed scripts used outdated field names

### The Solution:

**DESIGN.md = Single Source of Truth**

All changes MUST follow this flow:
```
1. Read DESIGN.md (understand current state)
2. Plan change across ALL layers (DB → Model → API → Frontend)
3. Update DESIGN.md with planned changes
4. Implement changes in code
5. Test end-to-end
6. Update DESIGN.md with actual implementation
```

**Golden Rules:**
- ✅ PostgreSQL schema = Ultimate source of truth
- ✅ NEVER change models without migration
- ✅ NEVER change APIs without updating frontend
- ✅ ALWAYS update DESIGN.md after ANY change
- ✅ ALWAYS test end-to-end after changes

### Quick Reference:

| What You Need | Where to Look |
|--------------|---------------|
| Database schemas | `DESIGN.md` - Section 3 |
| Model definitions | `DESIGN.md` - Section 4 |
| API endpoints | `DESIGN.md` - Section 5 |
| Frontend components | `DESIGN.md` - Section 6 |
| Change process | `DESIGN.md` - Section 8 |
| Known issues | `DESIGN.md` - Section 9 |

**If you violate this process, you WILL break the application!**

---

## Essential Commands

### Backend Setup & Development

```bash
# Navigate to backend
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up PostgreSQL database (production)
# First, create the database:
sudo -u postgres createdb governance_portal

# Create .env file (if not exists)
echo "DATABASE_URL=postgresql://user:password@localhost/governance_portal" > .env
echo "SECRET_KEY=your-secret-key-change-in-production" >> .env

# Initialize Alembic migrations (if not already done)
alembic init migrations

# Create migration
alembic revision --autogenerate -m "initial schema"

# Apply migrations
alembic upgrade head

# Seed database with sample data
python seed_data.py

# Run backend server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Or with specific log level
uvicorn app.main:app --reload --log-level info
```

Backend will be available at: `http://localhost:8000`
API Documentation: `http://localhost:8000/api/docs`

### Frontend Setup & Development

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Lint code
npm run lint
```

Frontend will be available at: `http://localhost:5173` (Vite) or `http://localhost:3000`

### Database Operations

```bash
# Create a new migration after model changes
cd backend
alembic revision --autogenerate -m "description of changes"

# Apply migrations
alembic upgrade head

# Rollback last migration
alembic downgrade -1

# Rollback to specific version
alembic downgrade <revision_id>

# View migration history
alembic history

# View current version
alembic current

# Reset database (DEVELOPMENT ONLY)
dropdb governance_portal && createdb governance_portal
alembic upgrade head
python seed_data.py
```

## Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────┐
│           Enterprise DaaS Governance Portal             │
│                                                         │
│  ┌────────────────────────────────────────────────┐   │
│  │  React Frontend (Vite + Material-UI)           │   │
│  │  - 11 modules (Dashboard, Assets, Strategy,    │   │
│  │    Vendors, Reports, Compliance, etc.)         │   │
│  └──────────────────┬─────────────────────────────┘   │
│                     │ REST API (HTTPS)                 │
│  ┌──────────────────▼─────────────────────────────┐   │
│  │  FastAPI Backend                               │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐    │   │
│  │  │ Assets   │  │ Strategy │  │ Vendors  │    │   │
│  │  │   API    │  │   API    │  │   API    │    │   │
│  │  └──────────┘  └──────────┘  └──────────┘    │   │
│  │  ┌──────────┐  ┌──────────┐                  │   │
│  │  │Compliance│  │ Reports  │                  │   │
│  │  │   API    │  │   API    │                  │   │
│  │  └──────────┘  └──────────┘                  │   │
│  └──────────────────┬─────────────────────────────┘   │
│                     │ SQLAlchemy ORM                   │
│  ┌──────────────────▼─────────────────────────────┐   │
│  │  PostgreSQL Database                           │   │
│  │  - 20 tables (9 core + 11 extended)            │   │
│  │  - Assets, Users, Domains, Vendors, Goals      │   │
│  │  - Strategic Initiatives, Budget, SLAs         │   │
│  └────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

### Core Components

**Backend (FastAPI)**
- `app/main.py` - FastAPI application entry point, CORS config, router registration
- `app/database.py` - SQLAlchemy database connection and session management
- `app/models.py` - Core ORM models (9 tables): Role, User, Domain, Asset, LifecycleHistory, ChangeRequest, ComplianceViolation, AuditLog, ComplianceMetric
- `app/models_extended.py` - Strategic ORM models (11 tables): BusinessGoal, StrategicInitiative, Vendor, VendorSLA, Stakeholder, BudgetAllocation, etc.
- `app/schemas.py` - Pydantic schemas for request/response validation
- `app/api/` - API route modules:
  - `assets.py` - Asset CRUD operations
  - `compliance.py` - Compliance metrics and validation
  - `strategy.py` - Strategic goals and initiatives
  - `vendors.py` - Vendor and SLA management
  - `reports.py` - Executive reports and analytics
- `app/services/naming_validator.py` - Naming convention validation service

**Frontend (React)**
- `src/App.jsx` - Main application component with routing
- `src/components/` - UI components organized by module:
  - `Dashboard/` - Overview dashboard
  - `AssetRegistry/` - Asset management UI
  - `NamingValidator/` - Real-time naming validation
  - `ComplianceDashboard/` - Compliance metrics and violations
  - `StrategyDashboard/` - Strategic goals and ROI tracking
  - `VendorManagement/` - Vendor and SLA management
  - `ManagementReports/` - Executive reports

**Database Schema**
- Core tables: roles, users, domains, assets, lifecycle_history, change_requests, compliance_violations, audit_logs, compliance_metrics
- Strategic tables: business_goals, strategic_initiatives, initiative_deliverables, vendors, vendor_slas, stakeholders, stakeholder_data_needs, business_use_cases, budget_allocations
- Mapping tables: asset_business_alignment, asset_vendor_mapping

### Technology Stack

**Frontend:**
- React 18.2.0
- Material-UI 5.14.18
- React Router DOM 6.20.0
- Axios 1.6.2 (HTTP client)
- Recharts 2.10.3 (data visualization)
- Vite 5.0.2 (build tool)

**Backend:**
- FastAPI 0.109.2
- Uvicorn 0.27.1 (ASGI server)
- SQLAlchemy 2.0.25 (ORM)
- Pydantic 2.6.1 (validation)
- Python-Jose 3.3.0 (JWT tokens)
- Passlib 1.7.4 (password hashing)
- Alembic (migrations - to be added)
- PostgreSQL (via psycopg2-binary - to be added)

## Development Notes

### Current State vs. Target State

| Aspect | Current (Prototype) | Target (Production) |
|--------|-------------------|-------------------|
| **Data** | Mock/hardcoded data in API responses | Real PostgreSQL database queries |
| **Authentication** | None (no login) | JWT + SSO (Azure AD) |
| **CRUD Operations** | View only (GET endpoints) | Full Create/Edit/Delete |
| **Charts** | Static mock data | Real-time from database |
| **Export** | None | PDF, Excel, CSV |
| **Notifications** | None | Email + Slack + In-app |
| **Integrations** | None | ServiceNow, Jira, Slack |

### Immediate Priorities (Phase 1)

1. **Database Integration:**
   - Set up PostgreSQL database
   - Create Alembic migrations for all tables
   - Connect API endpoints to database via SQLAlchemy
   - Implement real SELECT, INSERT, UPDATE, DELETE operations

2. **Authentication:**
   - JWT token generation and validation
   - Login/logout endpoints
   - Password hashing (bcrypt)
   - Protected routes (frontend)
   - Role-based access control

3. **CRUD Operations:**
   - Assets: Create, read, update, delete
   - Vendors: Create, read, update, add SLAs
   - Business Goals: Create, read, update
   - Strategic Initiatives: Create, read, update

4. **Form Implementation:**
   - Asset creation/edit forms with validation
   - Vendor management forms
   - Business goal forms
   - Real-time naming validation

### Naming Convention Standard

**Format:** `{ENV}-{DOMAIN}-{SYSTEM}-{VERSION}`

**Components:**
- **ENV**: DEV, QA, UAT, PROD
- **DOMAIN**: HR, FIN, OPS, SALES, IT, DATA
- **SYSTEM**: 2-10 alphanumeric characters (descriptive)
- **VERSION**: v{major} or v{major}.{minor} (e.g., v1, v2.1)

**Valid Examples:**
- `PROD-HR-DW-v1` (HR Data Warehouse Production)
- `QA-FIN-ETL-v2.3` (Finance ETL QA)
- `DEV-SALES-API-v1.0` (Sales API Development)

**Invalid Examples:**
- `production-hr-dw` (wrong format, lowercase, missing version)
- `PROD-UNKNOWN-DW-v1` (invalid domain code)
- `PROD-HR-DW-1.0` (missing 'v' prefix on version)

### Database Models

**Core Models (models.py):**
- `Role` - User roles (Admin, DataSteward, AssetOwner, Viewer)
- `User` - User accounts with authentication
- `Domain` - Business domains (HR, FIN, OPS, etc.)
- `Asset` - Data/platform assets with lifecycle
- `LifecycleHistory` - Asset state transition tracking
- `ChangeRequest` - ITIL-style change management
- `ComplianceViolation` - Compliance issues tracking
- `AuditLog` - Immutable audit trail
- `ComplianceMetric` - Time-series compliance metrics

**Extended Models (models_extended.py):**
- `BusinessGoal` - Strategic business objectives
- `StrategicInitiative` - DaaS projects and programs
- `InitiativeDeliverable` - Project deliverables
- `Vendor` - Vendor/partner information
- `VendorSLA` - Service level agreements
- `Stakeholder` - Business stakeholders
- `StakeholderDataNeed` - Data requirements
- `BusinessUseCase` - Use case documentation
- `BudgetAllocation` - Budget tracking
- `AssetBusinessAlignment` - Asset-to-goal mapping
- `AssetVendorMapping` - Asset-to-vendor mapping

### API Endpoint Structure

**Assets API (`/api/v1/assets`):**
- `GET /api/v1/assets` - List all assets (with filtering)
- `GET /api/v1/assets/{id}` - Get asset by ID
- `POST /api/v1/assets` - Create new asset
- `PUT /api/v1/assets/{id}` - Update asset
- `DELETE /api/v1/assets/{id}` - Delete asset (soft delete)

**Compliance API (`/api/v1/compliance`):**
- `GET /api/v1/compliance/metrics` - Get compliance KPIs
- `GET /api/v1/compliance/violations` - List violations
- `POST /api/v1/compliance/validate/naming` - Validate asset name
- `GET /api/v1/compliance/domains` - Get approved domains

**Strategy API (`/api/v1/strategy`):**
- `GET /api/v1/strategy/summary` - Executive summary
- `GET /api/v1/strategy/goals` - List business goals
- `GET /api/v1/strategy/initiatives` - List strategic initiatives
- `GET /api/v1/strategy/roi` - ROI metrics

**Vendors API (`/api/v1/vendors`):**
- `GET /api/v1/vendors` - List vendors
- `GET /api/v1/vendors/{id}` - Get vendor details
- `GET /api/v1/vendors/{id}/slas` - Get vendor SLAs
- `POST /api/v1/vendors` - Create vendor

**Reports API (`/api/v1/reports`):**
- `GET /api/v1/reports/executive-summary` - Executive summary
- `GET /api/v1/reports/governance-summary` - Governance report
- `GET /api/v1/reports/compliance-report` - Compliance report

### Adding New Features

**When adding new API endpoints:**
1. Define Pydantic schemas in `schemas.py` (request/response models)
2. Add SQLAlchemy models in `models.py` or `models_extended.py`
3. Create Alembic migration: `alembic revision --autogenerate -m "add xyz"`
4. Implement API routes in appropriate `app/api/*.py` file
5. Use dependency injection for database sessions: `db: Session = Depends(get_db)`
6. Add authentication if needed: `current_user: User = Depends(get_current_user)`
7. Update seed data in `seed_data.py` if needed

**When adding new UI components:**
1. Create component in `frontend/src/components/{Module}/`
2. Use Material-UI components for consistency
3. Use Axios for API calls
4. Add route in `App.jsx` if needed
5. Add menu item in navigation sidebar if needed
6. Follow existing patterns for loading states, error handling

### Code Style & Conventions

**Backend (Python):**
- Follow PEP 8 style guide
- Use type hints for function parameters and returns
- Use Pydantic models for data validation
- Use async/await for I/O operations where possible
- Log errors with proper context
- Use dependency injection pattern

**Frontend (JavaScript/React):**
- Use functional components with hooks
- Use camelCase for variables and functions
- Use PascalCase for component names
- Destructure props in function parameters
- Use Material-UI sx prop for styling
- Keep components focused and single-purpose

### Authentication Flow

**Backend:**
1. User submits credentials to `/api/v1/auth/login`
2. Server validates credentials, hashes password check
3. Server generates JWT token with user info
4. Returns token + user data

**Frontend:**
1. Store JWT token in localStorage
2. Add token to Authorization header for all API calls
3. Redirect to login if token expires (401 response)
4. Clear token on logout

**Protected Routes:**
- Use `get_current_user` dependency on backend
- Use `ProtectedRoute` wrapper component on frontend
- Check user role for authorization (RBAC)

### Database Seeding

The `seed_data.py` script creates sample data for development:
- 4 Roles: Admin, DataSteward, AssetOwner, Viewer
- 4+ Users with hashed passwords
- 6 Domains: HR, FIN, OPS, SALES, IT, DATA
- 5+ Assets (mix of compliant and non-compliant)
- Sample change requests, violations, goals, vendors

Run after database setup: `python seed_data.py`

### Common Pitfalls

1. **Database Sessions:** Always use `Depends(get_db)` for session management, never create sessions manually
2. **Password Hashing:** Always hash passwords with bcrypt before storing
3. **CORS:** Frontend and backend on different ports require CORS configuration
4. **Environment Variables:** Use `.env` file for secrets, never commit to git
5. **Migrations:** Always create migration before modifying production database
6. **Foreign Keys:** Ensure referenced records exist before creating relationships
7. **Validation:** Validate on both client (user experience) and server (security)
8. **Error Handling:** Return proper HTTP status codes and error messages

### Testing Strategy

**Manual Testing:**
1. Test CRUD operations via API docs (`/api/docs`)
2. Test forms in UI for validation and error handling
3. Test authentication flow (login, logout, protected routes)
4. Test data persistence across server restarts

**Future Testing:**
- Unit tests for business logic
- Integration tests for API endpoints
- E2E tests with Playwright/Cypress
- Load testing for performance

### Deployment

**Development:**
- Backend: `uvicorn app.main:app --reload`
- Frontend: `npm run dev`

**Production:**
- Backend: Containerize with Docker, deploy to AWS ECS/Fargate
- Frontend: Build static files (`npm run build`), deploy to S3 + CloudFront
- Database: RDS PostgreSQL with Multi-AZ
- Caching: Redis (ElastiCache)
- Monitoring: CloudWatch

### Environment Variables

Create `.env` file in backend directory:

```bash
# Database
DATABASE_URL=postgresql://username:password@localhost:5432/governance_portal

# Security
SECRET_KEY=your-secret-key-change-in-production-min-32-chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# CORS (optional)
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173

# Email (future)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@company.com
SMTP_PASSWORD=your-app-password
```

### File Structure

```
enterprise-daas-portal/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI app entry point
│   │   ├── database.py          # Database connection
│   │   ├── models.py            # Core SQLAlchemy models
│   │   ├── models_extended.py   # Strategic models
│   │   ├── schemas.py           # Pydantic schemas
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── assets.py        # Asset CRUD endpoints
│   │   │   ├── compliance.py    # Compliance endpoints
│   │   │   ├── strategy.py      # Strategy endpoints
│   │   │   ├── vendors.py       # Vendor endpoints
│   │   │   └── reports.py       # Report endpoints
│   │   ├── services/
│   │   │   └── naming_validator.py
│   │   └── utils/
│   ├── migrations/              # Alembic migrations (to be created)
│   ├── .env                     # Environment variables (create this)
│   ├── alembic.ini              # Alembic config (to be created)
│   ├── requirements.txt         # Python dependencies
│   ├── seed_data.py             # Database seeding script
│   └── governance_portal.db     # SQLite DB (prototype only)
├── frontend/
│   ├── src/
│   │   ├── main.jsx
│   │   ├── App.jsx              # Main app with routing
│   │   ├── components/
│   │   │   ├── Dashboard/
│   │   │   ├── AssetRegistry/
│   │   │   ├── NamingValidator/
│   │   │   ├── ComplianceDashboard/
│   │   │   ├── StrategyDashboard/
│   │   │   ├── VendorManagement/
│   │   │   └── ManagementReports/
│   │   ├── services/            # API service functions
│   │   ├── styles/
│   │   └── utils/
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   └── .env                     # Frontend env vars (if needed)
├── docs/
│   ├── 01-product-vision.md
│   ├── 02-functional-architecture.md
│   ├── 03-technical-architecture.md
│   ├── 04-database-schema.md
│   ├── 05-naming-convention-standard.md
│   ├── 06-governance-model.md
│   ├── 07-kpi-framework.md
│   ├── 08-risk-compliance-mapping.md
│   ├── 09-ui-ux-guidelines.md
│   ├── 10-itil-integration.md
│   ├── 11-product-roadmap.md
│   └── 12-quick-implementation-guide.md
├── database/
│   └── init.sql                 # SQL initialization (reference)
├── CLAUDE.md                    # This file
└── README.md                    # Project overview
```

### Key Dependencies to Add

**Backend (add to requirements.txt):**
```
alembic==1.13.1
psycopg2-binary==2.9.9
python-dotenv==1.0.0
```

**Frontend (add to package.json):**
```json
{
  "@tanstack/react-query": "^5.17.0",
  "react-hot-toast": "^2.4.1",
  "react-hook-form": "^7.49.3"
}
```

## Quick Start (Fresh Setup)

```bash
# 1. Clone and navigate to project
cd enterprise-daas-portal

# 2. Backend setup
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 3. Database setup (PostgreSQL)
sudo -u postgres createdb governance_portal
echo "DATABASE_URL=postgresql://postgres:password@localhost/governance_portal" > .env
echo "SECRET_KEY=$(openssl rand -hex 32)" >> .env

# 4. Run migrations and seed data
alembic upgrade head
python seed_data.py

# 5. Start backend (in terminal 1)
uvicorn app.main:app --reload

# 6. Frontend setup (in terminal 2)
cd ../frontend
npm install
npm run dev

# 7. Access application
# Frontend: http://localhost:5173
# Backend API docs: http://localhost:8000/api/docs
```

## Support

For questions or issues:
- Check documentation in `/docs` folder
- Review API documentation at `/api/docs` when backend is running
- Check this CLAUDE.md file for development guidelines

---

**Version:** 2.0
**Last Updated:** February 2026
**Status:** Active Development - Phase 1 (Core Functionality)
