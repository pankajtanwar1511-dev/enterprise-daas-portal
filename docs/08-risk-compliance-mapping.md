# Risk & Compliance Mapping
## Enterprise DaaS Governance Portal

**Version:** 1.0
**Date:** February 2026

---

## Purpose

This document maps governance controls in the DaaS Portal to enterprise risk management and regulatory compliance requirements.

---

## Risk Categories

### 1. Operational Risks

| Risk ID | Risk Description | Impact | Likelihood | Mitigation Control | Portal Feature |
|---------|------------------|--------|------------|-------------------|----------------|
| **R-O1** | Unauthorized changes to production assets | High | Medium | Approval workflow enforcement | Change Management Module |
| **R-O2** | Asset naming inconsistency leading to confusion | Medium | High | Automated naming validation | Naming Convention Validator |
| **R-O3** | Loss of asset metadata/documentation | High | Low | Audit trail + backup | Audit Logs + Database backup |
| **R-O4** | Orphaned assets without ownership | Medium | Medium | Mandatory ownership field | Asset Registration (required owner) |
| **R-O5** | Deprecated assets remaining in production | Medium | Medium | Lifecycle alerts | Lifecycle Management alerts |

---

### 2. Compliance Risks

| Risk ID | Risk Description | Regulatory Driver | Mitigation Control | Portal Feature |
|---------|------------------|-------------------|-------------------|----------------|
| **R-C1** | No audit trail for data access/changes | SOX, GDPR | Immutable audit logs | Audit Logs table |
| **R-C2** | Undocumented data assets | SOX 404, ISO 27001 | Documentation requirements | Mandatory doc URLs for Active assets |
| **R-C3** | Unclear data accountability | GDPR Article 5 | Ownership assignment | Asset Owner field (required) |
| **R-C4** | No change approval evidence | SOX, ITIL | Approval workflow tracking | Change Requests with approver signature |
| **R-C5** | Retention policy violations | GDPR, CCPA | Lifecycle management | Retired assets (read-only archive) |

---

### 3. Strategic Risks

| Risk ID | Risk Description | Impact | Mitigation Control | Portal Feature |
|---------|------------------|--------|-------------------|----------------|
| **R-S1** | Lack of executive visibility into data portfolio | High | Executive dashboard | Compliance Dashboard (CDO view) |
| **R-S2** | Uncontrolled asset proliferation | Medium | Asset registration governance | Mandatory registration policy |
| **R-S3** | Inconsistent governance across domains | Medium | Domain steward model | Data Steward role per domain |

---

## Regulatory Compliance Mapping

### SOX (Sarbanes-Oxley Act)

**Applicable Sections:**
- **SOX 302**: Management certification of financial reporting controls
- **SOX 404**: Internal control over financial reporting

**Portal Controls:**

| SOX Requirement | Control Implementation | Evidence |
|-----------------|------------------------|----------|
| Change control for financial systems | Approval workflow for FIN domain assets | `change_requests` table with approver signature |
| Audit trail for data modifications | Immutable audit log | `audit_logs` table (7-year retention) |
| Segregation of duties | RBAC with role-based approvals | User roles (Owner ≠ Approver) |
| Documentation of critical systems | Mandatory documentation URLs | `assets.documentation_url` (required for Active) |

**Audit Evidence Package:**
- Compliance dashboard export
- Audit log report (filtered by FIN domain)
- Change approval report
- Ownership matrix

---

### GDPR (General Data Protection Regulation)

**Applicable Articles:**
- **Article 5**: Data processing principles (accountability)
- **Article 30**: Records of processing activities
- **Article 32**: Security of processing

**Portal Controls:**

| GDPR Requirement | Control Implementation | Evidence |
|------------------|------------------------|----------|
| Data accountability | Asset ownership assignment | 100% ownership coverage |
| Record of processing activities | Asset registry with metadata | Asset summary report |
| Right to be forgotten | Asset retirement process | Lifecycle management (Retired state) |
| Data lineage tracking | Asset relationships + change history | `lifecycle_history` + audit logs |

**Audit Evidence Package:**
- Asset inventory (all HR assets with PII tags)
- Ownership assignment report
- Lifecycle transition history
- Data retention policy documentation

---

### ISO 27001 (Information Security Management)

**Applicable Controls:**
- **A.8.1**: Asset management
- **A.8.2**: Information classification
- **A.12.1**: Change management

**Portal Controls:**

| ISO 27001 Control | Control Implementation | Evidence |
|-------------------|------------------------|----------|
| A.8.1.1 Inventory of assets | Centralized asset registry | Asset count by domain |
| A.8.1.2 Ownership of assets | Mandatory owner field | Ownership report (100% coverage) |
| A.12.1.2 Change management | Risk-based approval workflow | Change approval statistics |

**Audit Evidence Package:**
- Asset registry export
- Change management report
- Role-based access control matrix

---

## Risk Assessment Matrix

### Risk Scoring

**Impact Scale:**
- **Low (1)**: Minimal disruption, <$10K financial impact
- **Medium (2)**: Moderate disruption, $10K-$100K impact
- **High (3)**: Severe disruption, >$100K impact, regulatory penalty

**Likelihood Scale:**
- **Low (1)**: Rare, <5% probability
- **Medium (2)**: Possible, 5-20% probability
- **High (3)**: Likely, >20% probability

**Risk Score = Impact × Likelihood**

### Inherent vs. Residual Risk

| Risk ID | Inherent Risk | Portal Control | Residual Risk | Risk Reduction |
|---------|---------------|----------------|---------------|----------------|
| R-O1 | High (9) | Change approval workflow | Low (2) | 78% reduction |
| R-O2 | High (6) | Naming validator | Low (1) | 83% reduction |
| R-C1 | High (9) | Audit logging | Low (1) | 89% reduction |
| R-C3 | Medium (4) | Mandatory ownership | Low (1) | 75% reduction |

---

## Control Effectiveness Testing

### Monthly Control Testing

| Control | Test Procedure | Expected Result | Frequency |
|---------|----------------|-----------------|-----------|
| Naming validation | Submit non-compliant name | System rejects | Monthly |
| Approval workflow | Submit High risk change | Routes to Data Steward + EA | Monthly |
| Audit logging | Create/update asset | Action logged with user ID | Monthly |
| Ownership enforcement | Create asset without owner | System prevents creation | Monthly |

**Test Owner:** Compliance Officer

**Evidence:** Test execution log with screenshots

---

## Third-Party Audit Readiness

### Annual Audit Preparation

**Pre-Audit Checklist:**
- [ ] Compliance dashboard at >95%
- [ ] All audit logs accessible (7-year retention verified)
- [ ] Ownership 100% assigned
- [ ] Documentation completeness >90%
- [ ] Change approval evidence available
- [ ] Policy documents current and approved

**Audit Evidence Location:**
- Asset inventory: `/api/v1/reports/governance`
- Audit logs: `/api/v1/audit-logs?start_date=YYYY-MM-DD`
- Change history: `/api/v1/reports/changes`
- Compliance metrics: `/api/v1/compliance/metrics`

**Point of Contact:** Compliance Officer (compliance@company.com)

---

## Risk Monitoring

### Continuous Risk Indicators

| Indicator | Threshold | Alert Action |
|-----------|-----------|--------------|
| Compliance rate <90% | Yellow alert | Notify Data Steward |
| Compliance rate <85% | Red alert | Escalate to CDO |
| Audit log gap detected | Critical alert | Immediate investigation |
| Ownership coverage <100% | Yellow alert | Notify domain Data Steward |
| Change approval >48 hours | Yellow alert | Notify approver + escalate |

---

## Incident Response

### Governance Incident Categories

**Category 1: Policy Violation**
- Unauthorized bypass of approval workflow
- Non-compliant asset deployed to production

**Response:**
1. Halt deployment (if possible)
2. Document incident in audit log
3. Notify Data Steward and Compliance Officer
4. Remediate within 24 hours
5. Root cause analysis

---

**Category 2: Audit Log Tampering**
- Attempt to modify/delete audit records

**Response:**
1. **Critical Incident** - Immediate escalation to CDO + CISO
2. Preserve evidence
3. Security investigation
4. Legal review
5. Disciplinary action

---

**Category 3: Compliance Breach**
- External audit finding
- Regulatory violation

**Response:**
1. Immediate executive notification
2. Containment and remediation plan
3. Regulatory reporting (if required)
4. Post-incident review
5. Control enhancement

---

## Compliance Reporting

### Quarterly Compliance Report

**Sections:**
1. Executive Summary (CDO message)
2. Compliance Metrics (vs. targets)
3. Risk Posture (heat map)
4. Audit Findings (status update)
5. Policy Exceptions (approved, pending)
6. Remediation Plans (open items)
7. Next Quarter Focus Areas

**Distribution:** CDO, CIO, Audit Committee, Compliance Officer

---

### Annual Compliance Attestation

**Attestation Statement:**
> "I certify that, to the best of my knowledge, all data and platform assets under my responsibility are registered in the Enterprise DaaS Governance Portal, comply with naming conventions, have designated owners, and are managed according to approved lifecycle policies."

**Required Signatories:**
- All Data Stewards (by domain)
- Asset Owners (for critical/financial assets)
- CDO (enterprise-wide certification)

**Deadline:** January 31 (annually)

---

## Privacy Impact Assessment

### Data Privacy Controls

| Privacy Principle | Portal Implementation | Evidence |
|-------------------|----------------------|----------|
| Data minimization | Asset metadata limited to business-necessary fields | Schema design |
| Purpose limitation | Asset tags indicate data usage (Analytics, Reporting, etc.) | Asset tags field |
| Transparency | Asset documentation describes data processing | Documentation URLs |
| Accountability | Asset ownership clearly assigned | Owner field (100% coverage) |

**PII Handling:**
- Portal does NOT store customer/employee PII
- Portal tracks METADATA about assets that may contain PII
- PII tag applied to relevant assets for discovery

---

## Security Controls

### Application Security

| Control | Implementation | Testing |
|---------|----------------|---------|
| Authentication | JWT-based auth | Quarterly penetration test |
| Authorization | RBAC (4 roles) | Monthly access review |
| Input validation | Pydantic schemas | Automated unit tests |
| SQL injection prevention | Parameterized queries (SQLAlchemy ORM) | Code review + SAST scanning |
| XSS protection | Input sanitization | DAST scanning |

---

### Data Security

| Control | Implementation | Testing |
|---------|----------------|---------|
| Encryption at rest | Database file encryption (future: PostgreSQL TDE) | Quarterly verification |
| Encryption in transit | TLS 1.3 (HTTPS enforced) | SSL Labs scan |
| Backup encryption | Encrypted backups | Restore test (quarterly) |
| Audit log integrity | Append-only table (no deletes) | Monthly integrity check |

---

## Approval

**Risk & Compliance Mapping Approved By:**
- Chief Data Officer: ________________________
- Compliance Officer: ________________________
- Chief Information Security Officer: ________________________
- Internal Audit Lead: ________________________

**Effective Date:** March 1, 2026
**Next Review:** September 1, 2026
