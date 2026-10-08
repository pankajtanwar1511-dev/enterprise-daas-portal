# Database Seeding - Clean Structure

## Overview

This directory previously contained **14 different seed scripts** totaling over 270KB of code, which caused:
- Data inconsistencies (e.g., tasks starting from ID 11 instead of 1)
- Confusion about which scripts to run
- Difficulty maintaining data integrity

## Current Structure (SIMPLIFIED)

### Active Script
- **`fix_tasks_sequence.py`** - Fixes tasks table to start from ID 1
  - Deletes existing tasks
  - Resets sequence to 1
  - Creates 50 tasks with proper IDs

### Archive
- **`seed_scripts_archive/`** - Contains all 14 old seed scripts for reference
  - These are NO LONGER USED
  - Kept for historical reference only

## Database Status

**Current State:** 29 tables populated, 15 tables empty

**Tables WITH Data (29):**
- activity_logs (200), api_keys (20), assets (5), audit_logs (100)
- budget_allocations (3), business_goals (3), change_requests (20)
- comments (75), compliance_violations (25), data_lineage_edges (24)
- data_lineage_nodes (32), data_quality_rules (20), domains (6)
- governance_policies (15), integration_logs (150), notifications (100)
- policy_validations (100), quality_check_runs (50), roles (4)
- schema_registry (25), sla_monitoring (60), stakeholders (3)
- strategic_initiatives (2), tasks (50), users (5), vendor_slas (3)
- vendors (3), webhook_deliveries (100), webhooks (15)

**Tables EMPTY (15):**
- asset_business_alignment, asset_vendor_mapping, business_use_cases
- compliance_metrics, impact_analysis_runs, import_jobs
- initiative_deliverables, itsm_configurations, itsm_record_mappings
- itsm_sync_logs, lifecycle_history, schema_validations
- sla_violations, stakeholder_data_needs, value_delivered_metrics

## Usage

### Fix Tasks Table
```bash
cd /home/pankaj/enterprise-daas-portal/backend
source venv/bin/activate
python3 fix_tasks_sequence.py
```

### Future Approach

**For new seed data needs:**
1. Create focused, single-purpose scripts
2. Name clearly: `seed_{table_name}.py`
3. Include verification and rollback logic
4. Document what data is created and why

**Example:**
```python
#!/usr/bin/env python3
"""
Seed Lifecycle History Data
Creates lifecycle transition records for existing assets.
"""
# Clear documentation
# Single responsibility
# Proper error handling
# Verification step
```

## Data Consistency Rules

1. **Primary Keys:** Always start from 1
2. **Foreign Keys:** Verify referenced records exist before creating
3. **Sequences:** Reset sequence after bulk operations
4. **Verification:** Always verify min/max IDs and counts after seeding

## Historical Issues Fixed

### Issue 1: Tasks Starting from ID 11
**Problem:** Tasks table had IDs 11-60 instead of 1-50
**Root Cause:** Multiple seed scripts running out of order
**Fix:** `fix_tasks_sequence.py` resets sequence and recreates from ID 1
**Status:** ✅ FIXED (2026-02-26)

### Issue 2: 14 Conflicting Seed Scripts
**Problem:** 14 different seed scripts caused confusion and conflicts
**Root Cause:** Incremental additions without consolidation
**Fix:** Archived all old scripts, created focused fix scripts
**Status:** ✅ FIXED (2026-02-26)

## Testing After Seeding

```bash
# Verify task IDs
psql -d governance_portal -c "SELECT MIN(task_id), MAX(task_id), COUNT(*) FROM tasks;"

# Test API endpoint
curl http://localhost:8000/api/v1/tasks/1 | python3 -m json.tool

# Run comprehensive tests
python3 /tmp/test_all_apis.py
```

## Maintenance

- **Do NOT** create multiple seed scripts for the same table
- **Do NOT** seed data in migration files (use separate seed scripts)
- **Do NOT** rely on auto-increment IDs without verifying
- **DO** verify foreign key relationships before seeding
- **DO** reset sequences after bulk operations
- **DO** include verification steps in seed scripts

---

**Last Updated:** 2026-02-26
**Status:** Active - Simplified Structure
**Contact:** See CLAUDE.md for development guidelines
