# Naming Convention Standard
## Enterprise DaaS Governance Portal

**Version:** 1.0
**Date:** February 2026
**Classification:** Enterprise Standard - Mandatory Compliance

---

## Purpose

This document defines the enterprise-wide naming convention standard for all data and platform assets. Compliance with this standard is **mandatory** for all assets registered in the DaaS Governance Portal.

---

## Standard Format

### Primary Format

```
{ENV}-{DOMAIN}-{SYSTEM}-{VERSION}
```

### Component Definitions

| Component | Description | Valid Values | Example |
|-----------|-------------|--------------|---------|
| **ENV** | Environment identifier | DEV, QA, UAT, PROD | PROD |
| **DOMAIN** | Business domain code | HR, FIN, OPS, SALES, IT, DATA | FIN |
| **SYSTEM** | System/asset identifier | Alphanumeric, 2-10 chars | DW |
| **VERSION** | Version number | v{major} or v{major}.{minor} | v1, v2.1 |

---

## Detailed Component Rules

### 1. ENV (Environment)

**Purpose:** Identifies the operational environment of the asset.

**Allowed Values:**

| Code | Full Name | Description | Examples |
|------|-----------|-------------|----------|
| **DEV** | Development | Development and sandbox environments | DEV-HR-DW-v1 |
| **QA** | Quality Assurance | Testing and quality validation | QA-FIN-ETL-v2 |
| **UAT** | User Acceptance Testing | Pre-production user validation | UAT-OPS-API-v1 |
| **PROD** | Production | Live production systems | PROD-SALES-CRM-v3 |

**Rules:**
- Must be uppercase
- No abbreviations other than those listed
- Cannot use: PRODUCTION, TEST, STAGE, LOCAL

---

### 2. DOMAIN (Business Domain)

**Purpose:** Categorizes assets by business functional area.

**Approved Domains:**

| Code | Domain Name | Description | Data Steward |
|------|-------------|-------------|--------------|
| **HR** | Human Resources | Employee, payroll, workforce data | HR Data Steward |
| **FIN** | Finance | Financial transactions, accounting | Finance Data Steward |
| **OPS** | Operations | Logistics, supply chain, operations | Operations Data Steward |
| **SALES** | Sales | Sales, CRM, customer data | Sales Data Steward |
| **IT** | Information Technology | IT systems, infrastructure | IT Data Steward |
| **DATA** | Data Platform | Data platform, pipelines, warehouses | CDO Office |

**Rules:**
- Must be uppercase
- Only approved domains allowed (see `domains` table)
- New domains require CDO approval
- Domain codes must be 2-10 characters

**How to Request New Domain:**
1. Submit request to Data Governance Council
2. Provide business justification
3. Assign Data Steward
4. Await CDO approval
5. Domain added to approved list

---

### 3. SYSTEM (System Identifier)

**Purpose:** Unique identifier for the specific asset or system.

**Rules:**
- Length: 2-10 characters
- Characters: Alphanumeric only (A-Z, 0-9)
- Case: Uppercase preferred
- No special characters (no hyphens, underscores, spaces)
- Must be descriptive but concise

**Recommended System Codes:**

| Type | Recommended Code | Example |
|------|------------------|---------|
| Data Warehouse | DW | PROD-HR-DW-v1 |
| ETL Pipeline | ETL | PROD-FIN-ETL-v2 |
| API | API | QA-OPS-API-v1 |
| Dashboard | DASH | PROD-SALES-DASH-v1 |
| Database | DB | DEV-IT-DB-v3 |
| Data Lake | LAKE | PROD-DATA-LAKE-v1 |
| Report | RPT | PROD-HR-RPT-v1 |
| Model | MDL | QA-FIN-MDL-v2 |

**Good Examples:**
- `DW` (Data Warehouse)
- `ETL` (Extract-Transform-Load)
- `API` (Application Interface)
- `CRM` (Customer Relationship Management)

**Bad Examples:**
- `DATA-WAREHOUSE` (contains hyphen)
- `D` (too short)
- `VERYLONG SYSTEM` (too long, contains space)

---

### 4. VERSION (Version Number)

**Purpose:** Tracks asset version for change management and lineage.

**Format:**
```
v{major}.{minor}
```

**Rules:**
- Must start with lowercase 'v'
- Major version: Integer (1, 2, 3...)
- Minor version: Optional, integer (0, 1, 2...)
- Separator: Period (.)

**Versioning Strategy:**

| Change Type | Version Impact | Example |
|-------------|----------------|---------|
| **Breaking Change** | Increment major version | v1.0 → v2.0 |
| **New Feature** | Increment minor version | v1.0 → v1.1 |
| **Bug Fix** | Increment minor version | v1.1 → v1.2 |
| **Initial Release** | Start at v1 or v1.0 | v1 or v1.0 |

**Valid Examples:**
- `v1`
- `v2.0`
- `v3.14`
- `v10.5`

**Invalid Examples:**
- `V1` (uppercase V)
- `1.0` (missing 'v')
- `v1.0.0` (three-part version not supported)
- `version1` (full word)

---

## Complete Examples

### Compliant Names

| Asset Name | ENV | DOMAIN | SYSTEM | VERSION | Description |
|------------|-----|--------|--------|---------|-------------|
| `PROD-HR-DW-v1` | PROD | HR | DW | v1 | HR Data Warehouse Production |
| `QA-FIN-ETL-v2.3` | QA | FIN | ETL | v2.3 | Finance ETL Pipeline QA |
| `DEV-SALES-API-v1.0` | DEV | SALES | API | v1.0 | Sales API Development |
| `UAT-OPS-DASH-v3` | UAT | OPS | DASH | v3 | Operations Dashboard UAT |
| `PROD-DATA-LAKE-v1.5` | PROD | DATA | LAKE | v1.5 | Enterprise Data Lake |

### Non-Compliant Names (with Violations)

| Asset Name | Violations | Correct Form |
|------------|-----------|--------------|
| `production-hr-dw` | Lowercase env, missing version | `PROD-HR-DW-v1` |
| `PROD-UNKNOWN-DW-v1` | Invalid domain | `PROD-{ApprovedDomain}-DW-v1` |
| `PRD-HR-DW-v1` | Invalid env abbreviation | `PROD-HR-DW-v1` |
| `PROD-HR-DATA_WAREHOUSE-v1` | Invalid system (underscore) | `PROD-HR-DW-v1` |
| `PROD-HR-DW-1.0` | Missing 'v' prefix | `PROD-HR-DW-v1.0` |
| `PROD-HR-D-v1` | System too short (<2 chars) | `PROD-HR-DW-v1` |

---

## Validation Rules

The system validates asset names using the following logic:

### Rule 1: Format Structure
```
Pattern: ^(DEV|QA|UAT|PROD)-([A-Z]{2,10})-([A-Z0-9]{2,10})-v(\d+(\.\d+)?)$
```

### Rule 2: Component Count
- Must have exactly 4 components separated by hyphens
- No leading/trailing hyphens
- No consecutive hyphens

### Rule 3: Environment Validation
- Must be one of: DEV, QA, UAT, PROD
- Case-sensitive (must be uppercase)

### Rule 4: Domain Validation
- Must exist in `domains` table
- Must be active (`is_active = TRUE`)

### Rule 5: System Validation
- Length: 2-10 characters
- Characters: A-Z, 0-9 only
- No special characters

### Rule 6: Version Validation
- Must start with 'v'
- Format: v{integer} or v{integer}.{integer}
- No three-part versions (v1.0.0 not allowed)

### Rule 7: Uniqueness
- Asset name must be globally unique across all environments
- Duplicate names rejected

---

## Validation Messages

### Error Messages

| Violation | Error Message | Suggested Fix |
|-----------|---------------|---------------|
| Invalid format | "Format must be ENV-DOMAIN-SYSTEM-VERSION" | Use correct delimiter structure |
| Invalid environment | "Invalid environment: {value}. Must be DEV, QA, UAT, or PROD" | Use approved environment code |
| Invalid domain | "Domain '{value}' not approved. See approved domains list" | Select from approved domains |
| System too short | "System name must be 2-10 characters" | Use descriptive system code |
| Invalid characters | "System name contains invalid characters. Use A-Z, 0-9 only" | Remove special characters |
| Invalid version | "Version must be in format v{major}.{minor}" | Add 'v' prefix and use integer versions |
| Duplicate name | "Asset name already exists" | Use different name or version |

---

## Governance and Compliance

### Compliance Requirements

1. **All New Assets:** Must comply with naming standard before registration
2. **Existing Assets:** Must be remediated within 90 days
3. **Exceptions:** Require CDO written approval (rare)

### Compliance Metrics

- **Target:** >95% naming compliance
- **Measurement:** Daily automated validation
- **Reporting:** Weekly compliance dashboard review

### Exception Process

In rare cases where the standard cannot be applied:

1. Submit exception request to Data Governance Council
2. Provide business justification
3. Propose alternative naming approach
4. Obtain CDO approval
5. Document exception in asset metadata

**Note:** Exceptions are discouraged and should be rare (<1% of assets).

---

## Naming Convention Change Process

This standard may evolve. Changes follow this process:

1. **Proposal:** Submit change proposal to Data Governance Council
2. **Impact Assessment:** Evaluate impact on existing assets
3. **Approval:** Requires CDO approval
4. **Communication:** 30-day notice to all stakeholders
5. **Implementation:** Phased rollout with migration plan
6. **Version Control:** Document version history

**Current Version:** 1.0
**Next Review Date:** August 2026

---

## Tools and Automation

### Automated Validation

- **Pre-Registration:** Name validated before asset creation
- **Bulk Validation:** Existing assets scanned daily
- **Violation Alerts:** Owners notified of non-compliance

### Validation API

```bash
POST /api/v1/validate/naming
{
  "asset_name": "PROD-HR-DW-v1"
}

Response:
{
  "valid": true,
  "violations": [],
  "suggestions": []
}
```

---

## FAQ

### Q: Can I use lowercase in asset names?
**A:** No. All components must be uppercase except the 'v' in version.

### Q: What if my system name naturally contains spaces?
**A:** Remove spaces and use camelCase abbreviation or acronym. Example: "Data Warehouse" → "DW"

### Q: Can I have multiple versions in different environments?
**A:** Yes. PROD-HR-DW-v1 and QA-HR-DW-v2 are both valid.

### Q: How do I version a breaking change?
**A:** Increment the major version: v1 → v2

### Q: What if I need a new domain?
**A:** Submit request to Data Governance Council with business justification.

### Q: Can I use TEST instead of QA?
**A:** No. Only DEV, QA, UAT, PROD are allowed.

---

## Approval

**Approved By:**
- Chief Data Officer: ________________________
- Data Governance Council Chair: ________________________
- Enterprise Architecture Lead: ________________________

**Effective Date:** March 1, 2026
**Next Review:** August 1, 2026
