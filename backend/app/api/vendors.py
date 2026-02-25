"""
Vendor Management & Budget Tracking API Routes
Aligned with: Manage vendor relationships and budget for DaaS initiatives
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import date, datetime
from ..database import get_db
from .. import models_extended as models
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1/vendors", tags=["Vendor Management"])


# Pydantic Schemas for Vendors
class VendorCreate(BaseModel):
    vendor_name: str
    vendor_type: str
    contact_name: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    status: str = "Active"
    contract_start: Optional[date] = None
    contract_end: Optional[date] = None
    annual_cost: Optional[float] = None
    payment_terms: Optional[str] = None
    performance_rating: Optional[int] = None
    notes: Optional[str] = None


class VendorUpdate(BaseModel):
    vendor_name: Optional[str] = None
    vendor_type: Optional[str] = None
    contact_name: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    status: Optional[str] = None
    contract_start: Optional[date] = None
    contract_end: Optional[date] = None
    annual_cost: Optional[float] = None
    payment_terms: Optional[str] = None
    performance_rating: Optional[int] = None
    notes: Optional[str] = None


class VendorSLACreate(BaseModel):
    vendor_id: int
    sla_metric: str
    target_value: str
    current_value: Optional[str] = None
    status: str = "Met"
    measurement_period: str = "Monthly"
    last_measured: Optional[date] = None


@router.get("/dashboard")
def get_vendor_dashboard(db: Session = Depends(get_db)):
    """
    Vendor management dashboard
    Demonstrates vendor relationship and budget management capabilities
    """

    # Vendor Summary
    total_vendors = db.query(func.count(models.Vendor.vendor_id)).scalar() or 0
    active_vendors = db.query(func.count(models.Vendor.vendor_id)).filter(
        models.Vendor.status == "Active"
    ).scalar() or 0

    # Cost Summary
    total_annual_cost = db.query(func.sum(models.Vendor.annual_cost)).scalar() or 0

    # SLA Performance
    sla_metrics = db.query(
        models.VendorSLA.status,
        func.count(models.VendorSLA.sla_id)
    ).group_by(models.VendorSLA.status).all()

    return {
        "vendor_summary": {
            "total_vendors": total_vendors,
            "active_vendors": active_vendors,
            "vendor_types": {
                "cloud_providers": 3,
                "software_vendors": 5,
                "consulting": 2,
                "managed_services": 4
            }
        },
        "cost_management": {
            "total_annual_cost": round(total_annual_cost, 2),
            "monthly_average": round(total_annual_cost / 12, 2),
            "cost_optimization_opportunities": "$450K",
            "cost_trend": "-8.5%"  # Cost reduction YoY
        },
        "sla_performance": {
            "by_status": {status: count for status, count in sla_metrics},
            "overall_compliance": "94.5%",
            "at_risk_count": 2,
            "breached_count": 1
        },
        "vendor_performance": {
            "average_rating": 4.2,
            "top_performers": 8,
            "needs_attention": 2
        }
    }


@router.get("/list")
def list_vendors(db: Session = Depends(get_db)):
    """List all vendors with key metrics"""
    vendors = db.query(models.Vendor).all()

    return {
        "vendors": [
            {
                "vendor_id": v.vendor_id,
                "vendor_name": v.vendor_name,
                "vendor_type": v.vendor_type,
                "status": v.status,
                "annual_cost": v.annual_cost,
                "performance_rating": v.performance_rating,
                "contract_start": v.contract_start.isoformat() if v.contract_start else None,
                "contract_end": v.contract_end.isoformat() if v.contract_end else None,
                "contact_email": v.contact_email
            }
            for v in vendors
        ]
    }


@router.get("/sla-tracking")
def get_sla_tracking(db: Session = Depends(get_db)):
    """
    Track vendor SLAs
    Critical for managing vendor performance
    """
    return {
        "sla_summary": {
            "total_slas": 28,
            "met": 26,
            "at_risk": 1,
            "breached": 1,
            "compliance_rate": "92.9%"
        },
        "critical_slas": [
            {
                "vendor_name": "AWS China",
                "metric": "Uptime",
                "target": "99.95%",
                "current": "99.97%",
                "status": "Met"
            },
            {
                "vendor_name": "Databricks",
                "metric": "Query Response Time",
                "target": "< 500ms",
                "current": "480ms",
                "status": "Met"
            },
            {
                "vendor_name": "Snowflake",
                "metric": "Support Response",
                "target": "< 2 hours",
                "current": "2.5 hours",
                "status": "At Risk"
            }
        ]
    }


@router.get("/budget-tracking")
def get_budget_tracking(db: Session = Depends(get_db)):
    """
    Budget tracking and allocation
    Demonstrates financial management of DaaS initiatives
    """

    # Get budget allocations
    allocations = db.query(models.BudgetAllocation).all()

    return {
        "budget_overview": {
            "fiscal_year": 2026,
            "total_allocated": 5500000,
            "total_spent": 3200000,
            "utilization_rate": 58.2,
            "forecasted_year_end": 5100000,
            "variance": -400000,  # Under budget
            "variance_percentage": -7.3
        },
        "by_category": [
            {
                "category": "Cloud Infrastructure",
                "allocated": 2000000,
                "spent": 1150000,
                "forecast": 1900000,
                "variance": -100000
            },
            {
                "category": "Software Licenses",
                "allocated": 1500000,
                "spent": 900000,
                "forecast": 1400000,
                "variance": -100000
            },
            {
                "category": "Professional Services",
                "allocated": 1200000,
                "spent": 750000,
                "forecast": 1100000,
                "variance": -100000
            },
            {
                "category": "Personnel",
                "allocated": 800000,
                "spent": 400000,
                "forecast": 800000,
                "variance": 0
            }
        ],
        "by_domain": [
            {
                "domain": "Finance",
                "allocated": 1800000,
                "spent": 1100000,
                "utilization": 61.1
            },
            {
                "domain": "HR",
                "allocated": 1200000,
                "spent": 650000,
                "utilization": 54.2
            },
            {
                "domain": "Operations",
                "allocated": 1500000,
                "spent": 900000,
                "utilization": 60.0
            },
            {
                "domain": "Sales",
                "allocated": 1000000,
                "spent": 550000,
                "utilization": 55.0
            }
        ],
        "cost_optimization": {
            "opportunities_identified": 6,
            "potential_savings": 450000,
            "recommendations": [
                "Consolidate redundant cloud storage - Save $120K",
                "Negotiate volume discount with Snowflake - Save $100K",
                "Right-size compute instances - Save $80K",
                "Eliminate unused licenses - Save $150K"
            ]
        }
    }


@router.get("/contract-renewals")
def get_contract_renewals(db: Session = Depends(get_db)):
    """Track upcoming contract renewals"""
    today = date.today()

    # Get vendors with contracts expiring soon
    vendors = db.query(models.Vendor).filter(
        models.Vendor.contract_end.isnot(None),
        models.Vendor.status == "Active"
    ).all()

    upcoming = []
    expiring_30 = 0
    expiring_90 = 0
    expiring_180 = 0
    total_value = 0

    for v in vendors:
        days_until = (v.contract_end - today).days
        if days_until > 0 and days_until <= 180:
            upcoming.append({
                "vendor_name": v.vendor_name,
                "contract_value": v.annual_cost or 0,
                "renewal_date": v.contract_end.isoformat(),
                "days_until_renewal": days_until,
                "action_required": "Review and negotiate" if days_until <= 90 else "Monitor",
                "priority": "High" if days_until <= 60 else "Medium" if days_until <= 120 else "Low"
            })
            total_value += (v.annual_cost or 0)

            if days_until <= 30:
                expiring_30 += 1
            elif days_until <= 90:
                expiring_90 += 1
            elif days_until <= 180:
                expiring_180 += 1

    return {
        "upcoming_renewals": sorted(upcoming, key=lambda x: x["days_until_renewal"]),
        "summary": {
            "contracts_expiring_30_days": expiring_30,
            "contracts_expiring_90_days": expiring_90,
            "contracts_expiring_180_days": expiring_180,
            "total_renewal_value": total_value
        }
    }


# CRUD Operations for Vendors

@router.post("/", status_code=status.HTTP_201_CREATED)
def create_vendor(vendor: VendorCreate, db: Session = Depends(get_db)):
    """Create a new vendor"""
    new_vendor = models.Vendor(**vendor.model_dump())
    db.add(new_vendor)
    db.commit()
    db.refresh(new_vendor)
    return {
        "vendor_id": new_vendor.vendor_id,
        "vendor_name": new_vendor.vendor_name,
        "status": new_vendor.status,
        "message": "Vendor created successfully"
    }


@router.get("/{vendor_id}")
def get_vendor(vendor_id: int, db: Session = Depends(get_db)):
    """Get vendor by ID with SLAs"""
    vendor = db.query(models.Vendor).filter(models.Vendor.vendor_id == vendor_id).first()
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")

    # Get SLAs for this vendor
    slas = db.query(models.VendorSLA).filter(models.VendorSLA.vendor_id == vendor_id).all()

    return {
        "vendor_id": vendor.vendor_id,
        "vendor_name": vendor.vendor_name,
        "vendor_type": vendor.vendor_type,
        "contact_name": vendor.contact_name,
        "contact_email": vendor.contact_email,
        "contact_phone": vendor.contact_phone,
        "status": vendor.status,
        "contract_start": vendor.contract_start.isoformat() if vendor.contract_start else None,
        "contract_end": vendor.contract_end.isoformat() if vendor.contract_end else None,
        "annual_cost": vendor.annual_cost,
        "payment_terms": vendor.payment_terms,
        "performance_rating": vendor.performance_rating,
        "notes": vendor.notes,
        "slas": [
            {
                "sla_id": sla.sla_id,
                "sla_metric": sla.sla_metric,
                "target_value": sla.target_value,
                "current_value": sla.current_value,
                "status": sla.status,
                "measurement_period": sla.measurement_period,
                "last_measured": sla.last_measured.isoformat() if sla.last_measured else None
            }
            for sla in slas
        ]
    }


@router.put("/{vendor_id}")
def update_vendor(vendor_id: int, vendor_update: VendorUpdate, db: Session = Depends(get_db)):
    """Update vendor"""
    vendor = db.query(models.Vendor).filter(models.Vendor.vendor_id == vendor_id).first()
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")

    # Update fields
    update_data = vendor_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(vendor, field, value)

    db.commit()
    db.refresh(vendor)

    return {
        "vendor_id": vendor.vendor_id,
        "vendor_name": vendor.vendor_name,
        "status": vendor.status,
        "message": "Vendor updated successfully"
    }


@router.delete("/{vendor_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_vendor(vendor_id: int, db: Session = Depends(get_db)):
    """Delete vendor"""
    vendor = db.query(models.Vendor).filter(models.Vendor.vendor_id == vendor_id).first()
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")

    db.delete(vendor)
    db.commit()
    return None


# SLA Management

@router.post("/slas", status_code=status.HTTP_201_CREATED)
def create_sla(sla: VendorSLACreate, db: Session = Depends(get_db)):
    """Create a new vendor SLA"""
    # Verify vendor exists
    vendor = db.query(models.Vendor).filter(models.Vendor.vendor_id == sla.vendor_id).first()
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")

    new_sla = models.VendorSLA(**sla.model_dump())
    db.add(new_sla)
    db.commit()
    db.refresh(new_sla)

    return {
        "sla_id": new_sla.sla_id,
        "vendor_id": new_sla.vendor_id,
        "sla_metric": new_sla.sla_metric,
        "status": new_sla.status,
        "message": "SLA created successfully"
    }


@router.get("/{vendor_id}/slas")
def get_vendor_slas(vendor_id: int, db: Session = Depends(get_db)):
    """Get all SLAs for a vendor"""
    vendor = db.query(models.Vendor).filter(models.Vendor.vendor_id == vendor_id).first()
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")

    slas = db.query(models.VendorSLA).filter(models.VendorSLA.vendor_id == vendor_id).all()

    return {
        "vendor_name": vendor.vendor_name,
        "slas": [
            {
                "sla_id": sla.sla_id,
                "sla_metric": sla.sla_metric,
                "target_value": sla.target_value,
                "current_value": sla.current_value,
                "status": sla.status,
                "measurement_period": sla.measurement_period,
                "last_measured": sla.last_measured.isoformat() if sla.last_measured else None
            }
            for sla in slas
        ]
    }
