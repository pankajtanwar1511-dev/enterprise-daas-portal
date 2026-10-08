# Enterprise DaaS Portal - CRUD Implementation Plan

**Created:** February 26, 2026
**Status:** IN PROGRESS
**Target:** Full CRUD functionality for all core features

---

## 📊 Implementation Status

| # | Feature | Priority | Status | Pattern | Estimated Time |
|---|---------|----------|--------|---------|----------------|
| ✅ 1 | Value Delivered Metrics | Done | Complete | Dialog Form | - |
| ✅ 2 | Vendor Management | Done | Complete | 3-Tab Dialog | - |
| ✅ 3 | Asset Registry | Done | Complete | Multi-step Form | - |
| 🔄 4 | Change Requests | HIGH | In Progress | Dialog Form | 45 min |
| 🔄 5 | Strategic Initiatives | HIGH | In Progress | Wizard | 60 min |
| 🔄 6 | Business Goals | HIGH | In Progress | Dialog Form | 45 min |
| 🔄 7 | Stakeholder Management | HIGH | In Progress | New Page + Dialog | 60 min |
| 🔄 8 | Business Use Cases | HIGH | In Progress | New Page + Dialog | 60 min |
| ⏳ 9 | Compliance Policies | MEDIUM | Pending | Dialog Form | 45 min |
| ⏳ 10 | Data Quality Rules | MEDIUM | Pending | Dialog + Builder | 60 min |
| ⏳ 11 | SLA Definitions | MEDIUM | Pending | Dialog Form | 45 min |

**Total Estimated Time:** 7-8 hours (will implement core features in 30-minute session)

---

## 🎯 Implementation Sequence

### Session 1: Core Operations (30 minutes)
1. ✅ Change Requests CRUD
2. ✅ Business Goals CRUD
3. ✅ Strategic Initiatives CRUD (simplified version)

### Session 2: Stakeholder Features (Future)
4. Stakeholder Management (new page)
5. Business Use Cases (new page)
6. Stakeholder Data Needs integration

### Session 3: Configuration Management (Future)
7. Compliance Policies CRUD
8. Data Quality Rules CRUD
9. SLA Definitions CRUD

---

## 📋 Implementation Checklist Per Feature

For each feature, complete:

- [ ] **Backend Verification**
  - [ ] Check API endpoints exist (GET, POST, PUT, DELETE)
  - [ ] Verify Pydantic schemas exist
  - [ ] Test endpoints with curl
  - [ ] Create missing endpoints if needed

- [ ] **Frontend Components**
  - [ ] Create FormDialog component
  - [ ] Update Dashboard component with:
    - [ ] "Add New" button
    - [ ] Table with data
    - [ ] Edit/Delete action buttons
    - [ ] Delete confirmation dialog
  - [ ] Integrate FormDialog into Dashboard
  - [ ] Add handlers (add, edit, delete, save)

- [ ] **Testing**
  - [ ] Test create new record
  - [ ] Test edit existing record
  - [ ] Test delete record
  - [ ] Test validation errors
  - [ ] Test data refresh after operations

- [ ] **Documentation**
  - [ ] Add to USER_GUIDE.md
  - [ ] Document workflow
  - [ ] Add examples

---

## 🛠️ Technical Patterns

### Pattern A: Dialog Form (Simple)
**Use for:** 3-8 fields, single entity
**Components needed:**
- `XFormDialog.jsx` - Form dialog component
- Update existing dashboard with CRUD handlers
- Material-UI components: Dialog, TextField, Select, Button

**Example:** Value Metrics, Business Goals

### Pattern B: Dialog Form (Tabbed)
**Use for:** 10-15 fields, logical groupings
**Components needed:**
- `XFormDialog.jsx` with Tabs
- Multiple TabPanels for grouping
- Sub-components for complex fields (e.g., SLA list)

**Example:** Vendor Management

### Pattern C: Multi-step Wizard
**Use for:** Complex entities with dependencies
**Components needed:**
- Stepper component
- Multiple step components
- Progress tracking
- Validation per step

**Example:** Strategic Initiatives (full version)

---

## 🔐 Access Control Matrix

| Feature | Viewer | Asset Owner | Data Steward | Admin |
|---------|--------|-------------|--------------|-------|
| Change Requests | View | Create/Edit own | Approve | Full |
| Strategic Initiatives | View | View | View | Full |
| Business Goals | View | View | View | Full |
| Vendors | View | View | Full | Full |
| Stakeholders | View | View | Full | Full |
| Policies | View | View | View | Full |
| Quality Rules | View | View | Full | Full |
| SLAs | View | View | View | Full |

---

## 📝 Field Definitions

### Change Requests
```typescript
{
  change_request_id: number (auto)
  asset_id: number (required, dropdown)
  change_type: string (required, dropdown: Migration, Schema Change, Access Change, Decommission)
  description: string (required, textarea)
  business_justification: string (required, textarea)
  requested_by: number (auto, current user)
  target_date: date (optional)
  status: string (auto: "Pending Approval")
  approval_status: string (Pending, Approved, Rejected)
  approved_by: number (optional)
  approved_at: datetime (optional)
  implementation_notes: string (optional, textarea)
  created_at: datetime (auto)
}
```

### Business Goals
```typescript
{
  goal_id: number (auto)
  goal_name: string (required)
  description: text (required)
  owner_id: number (required, user dropdown)
  target_date: date (optional)
  status: string (Active, Completed, Deferred)
  kpi_metric: string (optional)
  current_value: float (optional)
  target_value: float (optional)
  priority: string (High, Medium, Low)
  success_criteria: text (optional)
  expected_roi: float (optional)
  investment_amount: float (optional)
  completion_percentage: number (0-100)
}
```

### Strategic Initiatives
```typescript
{
  initiative_id: number (auto)
  initiative_name: string (required)
  description: text (required)
  business_goal_id: number (optional, dropdown)
  initiative_lead_id: number (required, user dropdown)
  budget_allocated: float (required)
  budget_spent: float (default: 0)
  start_date: date (required)
  target_date: date (required)
  status: string (Planning, In Progress, Completed, On Hold, At Risk)
  expected_roi: float (optional)
  stakeholder_count: number (default: 0)
  completion_percentage: number (0-100)
}
```

---

## 🚀 Deployment Notes

### Environment Variables
No new environment variables needed for CRUD features.

### Database Migrations
All tables already exist in database schema. No migrations needed.

### API Routes
All routes follow pattern: `/api/v1/{resource}/{id}`
- GET `/api/v1/{resource}` - List all
- GET `/api/v1/{resource}/{id}` - Get by ID
- POST `/api/v1/{resource}` - Create new
- PUT `/api/v1/{resource}/{id}` - Update
- DELETE `/api/v1/{resource}/{id}` - Delete

---

## ✅ Success Criteria

For each feature:
1. ✅ User can create new records via form dialog
2. ✅ User can edit existing records
3. ✅ User can delete records with confirmation
4. ✅ Validation works correctly
5. ✅ Data refreshes automatically after operations
6. ✅ Error messages are user-friendly
7. ✅ Form is accessible (keyboard navigation, screen readers)
8. ✅ Documentation is complete

---

## 🐛 Known Issues & Limitations

### Current Limitations:
- No role-based access control enforcement (UI shows all buttons to all users)
- No audit logging for CRUD operations (backend logs only)
- No bulk operations (must edit one at a time)
- No undo functionality
- No draft saving (must complete form)

### Future Enhancements:
- Add role-based button visibility
- Add audit trail UI
- Add bulk edit capabilities
- Add draft/autosave functionality
- Add import/export for bulk data
- Add version history for changes

---

## 📚 References

- Material-UI Documentation: https://mui.com/
- FastAPI Documentation: https://fastapi.tiangolo.com/
- Project Architecture: `/docs/03-technical-architecture.md`
- Database Schema: `/docs/04-database-schema.md`
- API Documentation: http://localhost:8000/api/docs

---

**Last Updated:** February 26, 2026
**Implemented By:** Claude Code AI Assistant
