# Technical Architecture
## Enterprise DaaS Governance Portal

**Version:** 2.0
**Date:** February 2026

---

## Architecture Overview

The Enterprise DaaS Governance Portal follows a **modern three-tier architecture** with clear separation of concerns, RESTful API design, and cloud-ready deployment patterns.

**Version 2.0 Enhancements:**
- Strategic DaaS leadership capabilities (business goal alignment, ROI tracking)
- Vendor management and SLA tracking
- Comprehensive budget management by category/domain
- Executive-level reporting (CMMI maturity, board presentations)
- Stakeholder engagement and data needs tracking

```
┌──────────────────────────────────────────────────────────────┐
│                     PRESENTATION LAYER                        │
│                    (React 18 Frontend)                        │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐            │
│  │ Dashboard  │  │   Asset    │  │  Change    │  ...        │
│  │            │  │  Registry  │  │ Management │            │
│  └────────────┘  └────────────┘  └────────────┘            │
└──────────────────────────┬───────────────────────────────────┘
                           │ HTTPS / REST API
┌──────────────────────────┴───────────────────────────────────┐
│                    APPLICATION LAYER                          │
│                   (FastAPI Backend)                           │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐            │
│  │ Asset API  │  │ Change API │  │ Report API │  ...        │
│  └─────┬──────┘  └─────┬──────┘  └─────┬──────┘            │
│        │                │                │                    │
│  ┌─────┴────────────────┴────────────────┴──────┐           │
│  │         BUSINESS LOGIC LAYER                  │           │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐   │           │
│  │  │  Naming  │  │Lifecycle │  │Governance│   │           │
│  │  │Validator │  │ Manager  │  │  Engine  │   │           │
│  │  └──────────┘  └──────────┘  └──────────┘   │           │
│  └───────────────────────┬──────────────────────┘           │
└──────────────────────────┼───────────────────────────────────┘
                           │ ORM (SQLAlchemy)
┌──────────────────────────┴───────────────────────────────────┐
│                      DATA LAYER                               │
│                   (SQLite Database)                           │
│  ┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐            │
│  │ Assets │  │Changes │  │ Audit  │  │ Users  │  ...        │
│  └────────┘  └────────┘  └────────┘  └────────┘            │
└──────────────────────────────────────────────────────────────┘
```

---

## Technology Stack

### Frontend

| Component | Technology | Version | Justification |
|-----------|-----------|---------|---------------|
| **Framework** | React | 18.2+ | Industry standard, component-based, large ecosystem |
| **Language** | JavaScript/TypeScript | ES2022 | Type safety, better IDE support |
| **UI Library** | Material-UI (MUI) | 5.14+ | Enterprise-grade components, accessibility |
| **State Management** | React Context API + Hooks | Built-in | Sufficient for prototype, simpler than Redux |
| **HTTP Client** | Axios | 1.6+ | Promise-based, interceptor support |
| **Routing** | React Router | 6.20+ | Declarative routing, nested routes |
| **Charts** | Recharts | 2.10+ | React-native charts, simple API |
| **Forms** | React Hook Form | 7.49+ | Performant, validation support |
| **Testing** | Jest + React Testing Library | Latest | Standard React testing tools |

### Backend

| Component | Technology | Version | Justification |
|-----------|-----------|---------|---------------|
| **Framework** | FastAPI | 0.109+ | High performance, auto-documentation, async support |
| **Language** | Python | 3.11+ | Readable, extensive libraries, enterprise adoption |
| **ORM** | SQLAlchemy | 2.0+ | Mature ORM, supports multiple databases |
| **Database** | SQLite | 3.44+ | Embedded, zero-config, sufficient for prototype |
| **Validation** | Pydantic | 2.5+ | Type validation, built into FastAPI |
| **Authentication** | JWT (python-jose) | 3.3+ | Stateless, scalable authentication |
| **Testing** | Pytest | 7.4+ | Feature-rich, plugin ecosystem |
| **API Documentation** | OpenAPI/Swagger | Auto-generated | Built into FastAPI |

### Infrastructure

| Component | Technology | Justification |
|-----------|-----------|---------------|
| **Web Server** | Uvicorn | ASGI server for FastAPI |
| **Reverse Proxy** | Nginx (production) | Load balancing, SSL termination |
| **Containerization** | Docker | Environment consistency, easy deployment |
| **CI/CD** | GitHub Actions | Automated testing, deployment |

---

## System Architecture Patterns

### 1. API-First Design
- Frontend communicates exclusively via REST API
- Backend exposes OpenAPI specification
- API versioning strategy: `/api/v1/`

### 2. Layered Architecture

**Presentation Layer (React):**
- Responsible for: UI rendering, user interaction, client-side validation
- Does NOT contain: Business logic, direct database access

**Application Layer (FastAPI):**
- Responsible for: Request handling, response formatting, authentication
- Does NOT contain: UI logic, database queries

**Business Logic Layer:**
- Responsible for: Naming validation, lifecycle enforcement, governance rules
- Does NOT contain: HTTP concerns, database implementation

**Data Layer (SQLAlchemy):**
- Responsible for: Data persistence, query optimization, transactions
- Does NOT contain: Business rules, presentation logic

### 3. Dependency Injection
- Services injected into API routes
- Database sessions managed via dependency injection
- Testable, mockable components

### 4. Repository Pattern
- Database access abstracted behind repository interfaces
- Swappable database implementations
- Simplified testing with in-memory repositories

---

## API Design

### RESTful Endpoints

**Asset Management**
```
GET    /api/v1/assets                    # List all assets
GET    /api/v1/assets/{id}               # Get asset by ID
POST   /api/v1/assets                    # Create new asset
PUT    /api/v1/assets/{id}               # Update asset
DELETE /api/v1/assets/{id}               # Delete asset
GET    /api/v1/assets/search?q={query}   # Search assets
```

**Naming Validation**
```
POST   /api/v1/validate/naming           # Validate asset name
GET    /api/v1/validate/domains          # Get approved domains
POST   /api/v1/validate/bulk             # Bulk validate existing assets
```

**Lifecycle Management**
```
GET    /api/v1/lifecycle/states          # Get all lifecycle states
POST   /api/v1/lifecycle/transition      # Transition asset state
GET    /api/v1/lifecycle/history/{id}    # Get state history
```

**Change Management**
```
GET    /api/v1/changes                   # List change requests
POST   /api/v1/changes                   # Create change request
PUT    /api/v1/changes/{id}/approve      # Approve change
PUT    /api/v1/changes/{id}/reject       # Reject change
```

**Compliance Dashboard**
```
GET    /api/v1/compliance/metrics        # Get compliance KPIs
GET    /api/v1/compliance/violations     # List violations
GET    /api/v1/compliance/trends         # Get trend data
```

**Reporting**
```
GET    /api/v1/reports/governance        # Governance summary
GET    /api/v1/reports/compliance        # Compliance report
GET    /api/v1/reports/lifecycle         # Lifecycle report
POST   /api/v1/reports/generate          # Generate custom report
```

**DaaS Strategy (v2.0)**
```
GET    /api/v1/strategy/dashboard        # Strategic dashboard overview
GET    /api/v1/strategy/business-goals   # List business goals
POST   /api/v1/strategy/business-goals   # Create business goal
GET    /api/v1/strategy/initiatives      # List strategic initiatives
POST   /api/v1/strategy/initiatives      # Create initiative
GET    /api/v1/strategy/value-delivered  # Value delivered by domain
GET    /api/v1/strategy/asset-alignment  # Asset-business goal alignment
```

**Vendor Management (v2.0)**
```
GET    /api/v1/vendors/dashboard         # Vendor dashboard overview
GET    /api/v1/vendors                   # List all vendors
POST   /api/v1/vendors                   # Create vendor
PUT    /api/v1/vendors/{id}              # Update vendor
GET    /api/v1/vendors/sla-tracking      # SLA performance tracking
POST   /api/v1/vendors/{id}/slas         # Add SLA metric
GET    /api/v1/vendors/budget-tracking   # Budget by category/domain
GET    /api/v1/vendors/contract-renewals # Upcoming contract renewals
```

**Management Reports (v2.0)**
```
GET    /api/v1/reports/executive-summary     # Executive summary (C-level)
GET    /api/v1/reports/governance-maturity   # CMMI maturity assessment
GET    /api/v1/reports/board-presentation    # Board-level presentation data
GET    /api/v1/reports/stakeholder-engagement # Stakeholder metrics
```

### API Response Format

**Success Response:**
```json
{
  "status": "success",
  "data": {
    "asset_id": 123,
    "asset_name": "PROD-FIN-DW-v1"
  },
  "message": "Asset created successfully"
}
```

**Error Response:**
```json
{
  "status": "error",
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Asset name does not comply with naming convention",
    "details": [
      "Invalid environment prefix: PRD (expected PROD)"
    ]
  }
}
```

### API Authentication

- **Method:** JWT (JSON Web Token)
- **Flow:**
  1. User logs in: `POST /api/v1/auth/login`
  2. Server returns JWT token
  3. Client includes token in header: `Authorization: Bearer {token}`
  4. Server validates token on each request

---

## Data Flow

### Example: Asset Registration Flow

```
User (Frontend)
    │
    │ 1. Fill asset form
    │
    ▼
React Component
    │
    │ 2. Submit form data
    │
    ▼
Axios HTTP Client
    │
    │ 3. POST /api/v1/assets
    │
    ▼
FastAPI Route Handler
    │
    │ 4. Validate request (Pydantic)
    │
    ▼
Naming Validator Service
    │
    │ 5. Check naming convention
    │
    ▼ (If valid)
Asset Repository
    │
    │ 6. Save to database
    │
    ▼
SQLAlchemy ORM
    │
    │ 7. INSERT INTO assets
    │
    ▼
SQLite Database
    │
    │ 8. Return saved asset
    │
    ▼
FastAPI Response
    │
    │ 9. JSON response
    │
    ▼
React Component
    │
    │ 10. Update UI / Show success message
    │
    ▼
User (Frontend)
```

---

## Security Architecture

### Authentication & Authorization

**1. User Authentication**
- JWT-based stateless authentication
- Token expiry: 24 hours
- Refresh token mechanism
- Secure password hashing (bcrypt)

**2. Role-Based Access Control (RBAC)**
- Roles: Admin, DataSteward, AssetOwner, Viewer
- Permissions enforced at API level
- Fine-grained permissions per endpoint

**3. API Security**
- CORS configured for specific origins
- Rate limiting (100 requests/minute per user)
- Input validation on all endpoints
- SQL injection prevention (parameterized queries)
- XSS protection (input sanitization)

**4. Data Security**
- Sensitive data encrypted at rest
- HTTPS enforced (TLS 1.3)
- Audit logs for all data access
- No sensitive data in logs

### Security Headers

```python
# Implemented in FastAPI middleware
{
  "X-Content-Type-Options": "nosniff",
  "X-Frame-Options": "DENY",
  "X-XSS-Protection": "1; mode=block",
  "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
  "Content-Security-Policy": "default-src 'self'"
}
```

---

## Database Architecture

### Database Schema (Logical)

See `04-database-schema.md` for detailed schema.

**Core Tables (v1.0):**
- `assets` - Core asset metadata
- `domains` - Approved business domains
- `users` - User accounts and roles
- `lifecycle_history` - State transition tracking
- `change_requests` - Change management records
- `audit_logs` - Complete audit trail
- `compliance_violations` - Non-compliance tracking

**Strategic Tables (v2.0):**
- `business_goals` - Strategic business goals
- `strategic_initiatives` - DaaS projects and initiatives
- `asset_business_alignment` - Asset-to-goal mapping
- `vendors` - Vendor profiles and contracts
- `vendor_slas` - SLA metrics and performance
- `budget_allocations` - Budget tracking by category
- `stakeholders` - Business stakeholders
- `stakeholder_data_needs` - Data needs tracking
- `business_use_cases` - Use case management

### Database Indexing Strategy

```sql
-- Performance-critical indexes
CREATE INDEX idx_assets_name ON assets(asset_name);
CREATE INDEX idx_assets_domain ON assets(domain_id);
CREATE INDEX idx_assets_lifecycle ON assets(lifecycle_stage);
CREATE INDEX idx_assets_environment ON assets(environment);
CREATE INDEX idx_changes_status ON change_requests(approval_status);
CREATE INDEX idx_audit_timestamp ON audit_logs(timestamp);
```

### Database Transactions

- All write operations wrapped in transactions
- Rollback on validation failure
- Optimistic locking for concurrent updates

---

## Deployment Architecture

### Development Environment

```
┌─────────────────────────────────────┐
│  Developer Workstation              │
│  ┌───────────┐    ┌───────────┐   │
│  │  React    │    │  FastAPI  │   │
│  │  (npm)    │    │  (uvicorn)│   │
│  │ :3000     │───▶│  :8000    │   │
│  └───────────┘    └─────┬─────┘   │
│                          │          │
│                    ┌─────▼─────┐   │
│                    │  SQLite   │   │
│                    │  (local)  │   │
│                    └───────────┘   │
└─────────────────────────────────────┘
```

### Production Environment (Future)

```
┌─────────────────────────────────────────────┐
│              Cloud Infrastructure            │
│                                              │
│  ┌──────────┐     ┌──────────────┐         │
│  │  CDN     │────▶│  S3 Static   │         │
│  │(CloudFront)    │  (React App) │         │
│  └──────────┘     └──────────────┘         │
│       │                                      │
│       │                                      │
│  ┌────▼──────────────────────────┐         │
│  │   Load Balancer (ALB)          │         │
│  └────┬──────────────────────┬───┘         │
│       │                      │              │
│  ┌────▼──────┐         ┌────▼──────┐      │
│  │  FastAPI  │         │  FastAPI  │      │
│  │  Instance │         │  Instance │      │
│  │  (ECS)    │         │  (ECS)    │      │
│  └────┬──────┘         └────┬──────┘      │
│       │                      │              │
│       └──────────┬───────────┘              │
│                  │                          │
│            ┌─────▼─────┐                   │
│            │   RDS     │                   │
│            │ PostgreSQL│                   │
│            └───────────┘                   │
└─────────────────────────────────────────────┘
```

---

## Performance Considerations

### Frontend Optimization

1. **Code Splitting**: Lazy load components per route
2. **Memoization**: Use `React.memo()` for expensive components
3. **Virtual Scrolling**: For large asset lists (1000+ items)
4. **Caching**: Cache API responses (1 minute TTL)
5. **Compression**: Gzip assets in production

### Backend Optimization

1. **Database Connection Pooling**: Max 10 connections
2. **Query Optimization**: Eager loading for relationships
3. **Caching**: Redis for frequently accessed data (future)
4. **Async Operations**: Use FastAPI async routes
5. **Pagination**: Default 50 items per page

### Scalability Targets

- **Concurrent Users**: 100+
- **Assets**: 10,000+
- **API Response Time**: <200ms (p95)
- **Page Load Time**: <2 seconds

---

## Testing Strategy

### Frontend Testing

```
Unit Tests (Jest)
├── Components (isolated)
├── Utility functions
└── Custom hooks

Integration Tests (React Testing Library)
├── User flows
├── Form submissions
└── API integration (mocked)

E2E Tests (Cypress) - Future
├── Critical user journeys
└── Cross-browser compatibility
```

### Backend Testing

```
Unit Tests (Pytest)
├── Business logic (naming validator)
├── Utility functions
└── Data models

Integration Tests (Pytest)
├── API endpoints
├── Database operations
└── Authentication flow

Contract Tests (Pact) - Future
├── API schema validation
└── Frontend-backend contract
```

### Test Coverage Target

- **Unit Tests**: >80% coverage
- **Integration Tests**: Critical paths covered
- **E2E Tests**: Top 10 user flows

---

## Monitoring & Observability

### Logging

```python
# Structured logging format
{
  "timestamp": "2026-02-21T10:30:00Z",
  "level": "INFO",
  "service": "governance-portal",
  "module": "asset_api",
  "message": "Asset created",
  "user_id": "12345",
  "asset_id": "67890",
  "trace_id": "abc-123-def"
}
```

### Metrics (Future)

- **Application**: Request rate, error rate, latency
- **Business**: Assets registered/day, compliance rate, changes approved
- **Infrastructure**: CPU, memory, disk usage

### Health Checks

```
GET /api/v1/health
{
  "status": "healthy",
  "database": "connected",
  "version": "1.0.0",
  "uptime": "24h 15m"
}
```

---

## Disaster Recovery

### Backup Strategy

- **Database**: Daily automated backups
- **Retention**: 30 days
- **Restore Time Objective (RTO)**: <4 hours
- **Recovery Point Objective (RPO)**: <24 hours

### Data Integrity

- Foreign key constraints enforced
- Referential integrity maintained
- Audit log immutability

---

## Future Technical Enhancements

1. **Migration to PostgreSQL** for production scale
2. **Redis caching** for improved performance
3. **Elasticsearch** for advanced search
4. **Kubernetes** deployment for auto-scaling
5. **GraphQL API** for flexible data querying
6. **Real-time notifications** via WebSockets
7. **Advanced analytics** with Apache Superset

---

## Approval

**Technical Review:**
- Solution Architect: ________________________
- Lead Backend Engineer: ________________________
- Lead Frontend Engineer: ________________________
- Security Architect: ________________________

**Approval Date:** _____________
