"""
Budget API
Endpoints for budget allocation tracking and financial summaries
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from decimal import Decimal

from ..database import get_db
from ..models_extended import BudgetAllocation
from ..models import Domain

router = APIRouter(prefix="/api/v1/budget", tags=["budget"])


@router.get("/allocations", response_model=List[dict])
def get_budget_allocations(
    fiscal_year: Optional[int] = Query(None, description="Filter by fiscal year"),
    domain_id: Optional[int] = Query(None, description="Filter by domain"),
    category: Optional[str] = Query(None, description="Filter by category"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """
    Get budget allocations

    Returns budget allocation records with:
    - Fiscal year
    - Domain
    - Category (infrastructure, platform, tools, etc.)
    - Allocated vs spent amounts
    - Variance and forecasts

    No authentication required for read access.
    """
    query = db.query(BudgetAllocation)

    if fiscal_year:
        query = query.filter(BudgetAllocation.fiscal_year == fiscal_year)
    if domain_id:
        query = query.filter(BudgetAllocation.domain_id == domain_id)
    if category:
        query = query.filter(BudgetAllocation.category == category)

    allocations = query.offset(skip).limit(limit).all()

    return [
        {
            "budget_id": b.budget_id,
            "fiscal_year": b.fiscal_year,
            "domain_id": b.domain_id,
            "category": b.category,
            "allocated_amount": float(b.allocated_amount) if b.allocated_amount else 0.0,
            "spent_amount": float(b.spent_amount) if b.spent_amount else 0.0,
            "forecasted_spend": float(b.forecasted_spend) if b.forecasted_spend else 0.0,
            "variance": float(b.allocated_amount - b.spent_amount) if b.allocated_amount and b.spent_amount else 0.0,
            "utilization_pct": float((b.spent_amount / b.allocated_amount * 100)) if b.allocated_amount and b.spent_amount and b.allocated_amount > 0 else 0.0,
            "notes": b.notes,
            "created_at": b.created_at.isoformat() if b.created_at else None
        }
        for b in allocations
    ]


@router.get("/summary", response_model=dict)
def get_budget_summary(
    fiscal_year: Optional[int] = Query(None, description="Fiscal year (defaults to all)"),
    db: Session = Depends(get_db)
):
    """
    Get budget summary with aggregated metrics

    Returns:
    - Total allocated budget
    - Total spent
    - Total forecasted spend
    - Overall utilization percentage
    - Breakdown by domain and category

    No authentication required for read access.
    """
    query = db.query(BudgetAllocation)

    if fiscal_year:
        query = query.filter(BudgetAllocation.fiscal_year == fiscal_year)

    allocations = query.all()

    if not allocations:
        return {
            "fiscal_year": fiscal_year,
            "total_allocated": 0.0,
            "total_spent": 0.0,
            "total_forecasted": 0.0,
            "overall_variance": 0.0,
            "utilization_pct": 0.0,
            "by_category": [],
            "by_domain": [],
            "record_count": 0
        }

    # Calculate totals
    total_allocated = sum(float(b.allocated_amount or 0) for b in allocations)
    total_spent = sum(float(b.spent_amount or 0) for b in allocations)
    total_forecasted = sum(float(b.forecasted_spend or 0) for b in allocations)
    overall_variance = total_allocated - total_spent
    utilization_pct = (total_spent / total_allocated * 100) if total_allocated > 0 else 0.0

    # Group by category
    by_category = {}
    for b in allocations:
        cat = b.category or "Uncategorized"
        if cat not in by_category:
            by_category[cat] = {
                "category": cat,
                "allocated": 0.0,
                "spent": 0.0,
                "forecasted": 0.0
            }
        by_category[cat]["allocated"] += float(b.allocated_amount or 0)
        by_category[cat]["spent"] += float(b.spent_amount or 0)
        by_category[cat]["forecasted"] += float(b.forecasted_spend or 0)

    # Group by domain
    by_domain = {}
    for b in allocations:
        domain_id = b.domain_id
        if domain_id not in by_domain:
            domain = db.query(Domain).filter(Domain.domain_id == domain_id).first()
            domain_name = domain.domain_name if domain else f"Domain {domain_id}"
            by_domain[domain_id] = {
                "domain_id": domain_id,
                "domain_name": domain_name,
                "allocated": 0.0,
                "spent": 0.0,
                "forecasted": 0.0
            }
        by_domain[domain_id]["allocated"] += float(b.allocated_amount or 0)
        by_domain[domain_id]["spent"] += float(b.spent_amount or 0)
        by_domain[domain_id]["forecasted"] += float(b.forecasted_spend or 0)

    return {
        "fiscal_year": fiscal_year if fiscal_year else "All Years",
        "total_allocated": round(total_allocated, 2),
        "total_spent": round(total_spent, 2),
        "total_forecasted": round(total_forecasted, 2),
        "overall_variance": round(overall_variance, 2),
        "utilization_pct": round(utilization_pct, 2),
        "by_category": list(by_category.values()),
        "by_domain": list(by_domain.values()),
        "record_count": len(allocations)
    }
