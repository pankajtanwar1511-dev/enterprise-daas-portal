# KPI Framework
## Enterprise DaaS Governance Portal

**Version:** 1.0
**Date:** February 2026

---

## Purpose

This document defines the Key Performance Indicator (KPI) framework for measuring the effectiveness and maturity of the Enterprise DaaS Governance Portal and overall governance program.

---

## KPI Categories

1. **Compliance KPIs** - Measure adherence to governance policies
2. **Operational KPIs** - Measure process efficiency
3. **Strategic KPIs** - Measure business value and maturity
4. **Quality KPIs** - Measure data and metadata quality

---

## Compliance KPIs

### KPI-C1: Asset Naming Compliance Rate

**Definition:** Percentage of assets compliant with naming convention standard

**Formula:**
```
Compliance Rate = (Compliant Assets / Total Assets) × 100
```

**Target:** ≥ 95%
**Measurement Frequency:** Daily (reported weekly)
**Data Source:** `assets` table, `naming_compliant` field

**Thresholds:**
- 🟢 Green: ≥95%
- 🟡 Yellow: 85-94%
- 🔴 Red: <85%

**Owner:** Data Governance Council

---

### KPI-C2: Asset Registration Coverage

**Definition:** Percentage of production assets registered in governance portal

**Formula:**
```
Coverage = (Registered Assets / Total Production Assets) × 100
```

**Target:** 100%
**Measurement Frequency:** Monthly
**Data Source:** Cross-reference with CMDB/infrastructure inventory

**Thresholds:**
- 🟢 Green: ≥98%
- 🟡 Yellow: 90-97%
- 🔴 Red: <90%

**Owner:** Data Stewards

---

### KPI-C3: Documentation Completeness

**Definition:** Percentage of Active assets with valid documentation URLs

**Formula:**
```
Doc Completeness = (Assets with Docs / Active Assets) × 100
```

**Target:** ≥ 90%
**Measurement Frequency:** Weekly
**Data Source:** `assets` table, `documentation_url` field

**Thresholds:**
- 🟢 Green: ≥90%
- 🟡 Yellow: 75-89%
- 🔴 Red: <75%

**Owner:** Asset Owners (measured by domain)

---

### KPI-C4: Ownership Assignment

**Definition:** Percentage of assets with assigned and active owners

**Formula:**
```
Ownership Rate = (Assets with Owner / Total Assets) × 100
```

**Target:** 100%
**Measurement Frequency:** Weekly
**Data Source:** `assets` table, `owner_id` field

**Thresholds:**
- 🟢 Green: 100%
- 🟡 Yellow: 95-99%
- 🔴 Red: <95%

**Owner:** Data Stewards

---

### KPI-C5: Compliance Violation Resolution Time

**Definition:** Average time to resolve compliance violations

**Formula:**
```
Avg Resolution Time = Σ(resolved_at - detected_at) / Count(Resolved Violations)
```

**Target:** ≤ 48 hours
**Measurement Frequency:** Weekly
**Data Source:** `compliance_violations` table

**Thresholds:**
- 🟢 Green: ≤48 hours
- 🟡 Yellow: 48-72 hours
- 🔴 Red: >72 hours

**Owner:** Asset Owners (by domain)

---

## Operational KPIs

### KPI-O1: Change Approval Cycle Time

**Definition:** Average time from change request submission to approval/rejection

**Formula:**
```
Avg Cycle Time = Σ(approved_at - requested_at) / Count(Changes)
```

**Target:** ≤ 24 hours (Medium risk)
**Measurement Frequency:** Weekly
**Data Source:** `change_requests` table

**Breakdown by Risk Level:**
- Low: Immediate (auto-approved)
- Medium: ≤24 hours
- High: ≤48 hours
- Critical: ≤5 business days

**Thresholds:**
- 🟢 Green: Within target
- 🟡 Yellow: 1.5× target
- 🔴 Red: >2× target

**Owner:** Data Stewards

---

### KPI-O2: Change Approval Rate

**Definition:** Percentage of change requests approved vs. rejected

**Formula:**
```
Approval Rate = (Approved Changes / Total Changes Processed) × 100
```

**Target:** 80-90% (balance between control and enablement)
**Measurement Frequency:** Monthly
**Data Source:** `change_requests` table

**Thresholds:**
- 🟢 Green: 80-90%
- 🟡 Yellow: 70-79% or 91-95%
- 🔴 Red: <70% or >95% (too permissive)

**Owner:** Data Governance Council

---

### KPI-O3: Asset Registration Time

**Definition:** Average time to complete asset registration

**Formula:**
```
Avg Registration Time = User-reported metric (survey)
```

**Target:** ≤ 5 minutes
**Measurement Frequency:** Quarterly (user survey)
**Data Source:** User feedback survey

**Thresholds:**
- 🟢 Green: ≤5 minutes
- 🟡 Yellow: 5-10 minutes
- 🔴 Red: >10 minutes

**Owner:** Platform Administrator

---

### KPI-O4: Lifecycle Transition Compliance

**Definition:** Percentage of valid lifecycle transitions (no illegal state changes)

**Formula:**
```
Valid Transitions = (Valid Transitions / Total Transitions) × 100
```

**Target:** 100% (system-enforced)
**Measurement Frequency:** Monthly (validation)
**Data Source:** `lifecycle_history` table

**Thresholds:**
- 🟢 Green: 100%
- 🔴 Red: <100% (indicates system bypass or error)

**Owner:** Platform Administrator

---

## Strategic KPIs

### KPI-S1: Governance Maturity Score

**Definition:** Overall governance maturity level (1-5 scale)

**Measurement:** Quarterly maturity assessment using CMMI framework

**Scoring:**
- Level 1 (Initial): Ad-hoc, reactive, manual
- Level 2 (Managed): Basic processes, some automation
- Level 3 (Defined): Documented, enforced, automated
- Level 4 (Measured): Metrics-driven, optimized
- Level 5 (Optimized): Industry-leading, predictive

**Current:** Level 2
**Target:** Level 3 by Q4 2026
**Measurement Frequency:** Quarterly
**Owner:** CDO

---

### KPI-S2: Audit Finding Reduction

**Definition:** Year-over-year reduction in data governance audit findings

**Formula:**
```
Reduction = ((Prior Year Findings - Current Year Findings) / Prior Year Findings) × 100
```

**Target:** -60% YoY
**Measurement Frequency:** Annual
**Data Source:** External audit reports

**Thresholds:**
- 🟢 Green: ≥50% reduction
- 🟡 Yellow: 25-49% reduction
- 🔴 Red: <25% reduction

**Owner:** Compliance Officer

---

### KPI-S3: Asset Portfolio Growth Rate

**Definition:** Month-over-month growth in registered assets

**Formula:**
```
Growth Rate = ((Current Month Assets - Prior Month Assets) / Prior Month Assets) × 100
```

**Target:** Stable growth aligned with business expansion
**Measurement Frequency:** Monthly
**Data Source:** `assets` table

**Interpretation:**
- Healthy growth: 2-5% MoM
- Concerning spike: >15% MoM (may indicate lack of governance controls)
- Decline: <0% (investigate asset retirements)

**Owner:** Data Governance Council

---

### KPI-S4: Operational Risk Score

**Definition:** Risk score based on non-compliance, deprecated assets, and pending changes

**Formula:**
```
Risk Score = (Non-Compliant Assets × 3) + (Deprecated >180 days × 5) + (High Risk Pending Changes × 2)
```

**Target:** ≤ 50
**Measurement Frequency:** Weekly
**Data Source:** Aggregated from multiple tables

**Thresholds:**
- 🟢 Green: ≤50
- 🟡 Yellow: 51-100
- 🔴 Red: >100

**Owner:** CDO

---

## Quality KPIs

### KPI-Q1: Metadata Completeness

**Definition:** Percentage of required metadata fields populated

**Formula:**
```
Completeness = (Populated Fields / Total Required Fields) × 100
```

**Required Fields:**
- Asset Name, Domain, Environment, Owner, Version, Lifecycle, Description

**Target:** ≥ 95%
**Measurement Frequency:** Weekly
**Data Source:** `assets` table

**Thresholds:**
- 🟢 Green: ≥95%
- 🟡 Yellow: 85-94%
- 🔴 Red: <85%

**Owner:** Asset Owners

---

### KPI-Q2: Documentation Currency

**Definition:** Percentage of documentation links updated within last 90 days

**Formula:**
```
Currency = (Docs Updated <90 days / Total Active Assets) × 100
```

**Target:** ≥ 80%
**Measurement Frequency:** Monthly
**Data Source:** `assets` table, `updated_at` field

**Thresholds:**
- 🟢 Green: ≥80%
- 🟡 Yellow: 60-79%
- 🔴 Red: <60%

**Owner:** Asset Owners

---

## KPI Dashboard

### Executive Dashboard (CDO View)

**Refresh Rate:** Daily

**Widgets:**
1. Governance Maturity Score (current level + trend)
2. Overall Compliance Rate (with sparkline)
3. Operational Risk Score
4. Asset Portfolio Growth (6-month trend)
5. Audit Finding Reduction (YoY comparison)
6. Top 5 Non-Compliant Domains

---

### Operational Dashboard (Data Steward View)

**Refresh Rate:** Real-time

**Widgets:**
1. Domain Compliance Rate (by domain)
2. Pending Change Approvals (count + aging)
3. Compliance Violations (by severity)
4. Change Approval Cycle Time (trend)
5. Ownership Assignment Rate
6. Documentation Completeness

---

### Tactical Dashboard (Asset Owner View)

**Refresh Rate:** Hourly

**Widgets:**
1. My Assets (total count)
2. My Compliance Status (violations to resolve)
3. My Pending Changes (status)
4. My Assets Needing Attention (deprecated, missing docs)

---

## Reporting Schedule

| Report | Audience | Frequency | Delivery |
|--------|----------|-----------|----------|
| **Executive Scorecard** | CDO, CIO | Monthly | Email PDF |
| **Governance Metrics Report** | Governance Council | Monthly | Portal + Email |
| **Domain Compliance Report** | Data Stewards | Weekly | Email |
| **Asset Owner Scorecard** | Asset Owners | Weekly | Email digest |
| **Quarterly Business Review** | Executive Leadership | Quarterly | Presentation |
| **Annual Governance Report** | Board, Audit Committee | Annual | Formal report |

---

## KPI Trends and Alerts

### Trend Analysis

**Automated Alerts:**
- Compliance rate drops >5% week-over-week → Alert Data Steward
- Change approval time >2× target → Alert Governance Council
- Risk score >100 → Escalate to CDO
- Audit findings increase YoY → Immediate executive review

**Trend Indicators:**
- ↑ Improving
- → Stable
- ↓ Declining

**Trend Visualization:**
- Sparklines (7-day, 30-day, 90-day)
- Month-over-month comparison
- Year-over-year comparison

---

## KPI Data Quality

### Data Validation

All KPI calculations validated:
- Daily automated calculation
- Cross-reference with source systems
- Manual spot checks (monthly)
- Audit trail for all changes

### Data Lineage

```
Source Data → ETL Process → Metrics Calculation → Dashboard Display
     ↓              ↓               ↓                    ↓
  Assets DB     Python Script   metrics_table      React UI
```

---

## KPI Improvement Targets

### 12-Month Roadmap

| KPI | Current (Feb 2026) | Q2 2026 Target | Q4 2026 Target |
|-----|-------------------|----------------|----------------|
| Naming Compliance | 85% | 90% | 95% |
| Asset Coverage | 92% | 95% | 100% |
| Documentation Completeness | 75% | 85% | 90% |
| Change Approval Time | 36 hours | 30 hours | 24 hours |
| Governance Maturity | Level 2 | Level 2.5 | Level 3 |

---

## Continuous Monitoring

### Real-Time Metrics

- Compliance Rate (updated hourly)
- Pending Approvals (updated every 15 minutes)
- Active Violations (real-time)

### Batch Metrics

- Maturity Score (quarterly calculation)
- Audit Findings (annual)
- Growth Rate (monthly)

---

## Approval

**KPI Framework Approved By:**
- Chief Data Officer: ________________________
- Data Governance Council: ________________________
- Analytics Lead: ________________________

**Effective Date:** March 1, 2026
**Next Review:** September 1, 2026
