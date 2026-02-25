"""
DaaS Strategy API Routes
Aligned with DaaS Strategy role: Business goals, strategic initiatives, ROI tracking
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..database import get_db
from .. import models_extended as models
from typing import List, Dict, Any
from .strategy_crud import (
    BusinessGoalCreate, BusinessGoalUpdate,
    StrategicInitiativeCreate, StrategicInitiativeUpdate,
    create_business_goal, get_business_goal, update_business_goal, delete_business_goal,
    create_strategic_initiative, get_strategic_initiative,
    update_strategic_initiative, delete_strategic_initiative
)

router = APIRouter(prefix="/api/v1/strategy", tags=["DaaS Strategy"])


@router.get("/dashboard")
def get_strategy_dashboard(db: Session = Depends(get_db)):
    """
    Get strategic dashboard overview for DaaS leadership
    Demonstrates ability to define and drive DaaS strategy
    """

    # Business Goals Summary
    total_goals = db.query(func.count(models.BusinessGoal.goal_id)).scalar() or 0
    active_goals = db.query(func.count(models.BusinessGoal.goal_id)).filter(
        models.BusinessGoal.status == "Active"
    ).scalar() or 0

    # Strategic Initiatives Summary
    total_initiatives = db.query(func.count(models.StrategicInitiative.initiative_id)).scalar() or 0
    initiatives_by_status = db.query(
        models.StrategicInitiative.status,
        func.count(models.StrategicInitiative.initiative_id)
    ).group_by(models.StrategicInitiative.status).all()

    # Budget Summary
    total_budget = db.query(func.sum(models.StrategicInitiative.budget_allocated)).scalar() or 0
    total_spent = db.query(func.sum(models.StrategicInitiative.budget_spent)).scalar() or 0
    budget_utilization = (total_spent / total_budget * 100) if total_budget > 0 else 0

    # Asset Alignment
    aligned_assets = db.query(func.count(models.AssetBusinessAlignment.alignment_id)).scalar() or 0

    # ROI Summary
    total_expected_roi = db.query(func.sum(models.StrategicInitiative.expected_roi)).scalar() or 0

    return {
        "business_goals": {
            "total": total_goals,
            "active": active_goals,
            "achievement_rate": 75  # Demo value
        },
        "strategic_initiatives": {
            "total": total_initiatives,
            "by_status": {status: count for status, count in initiatives_by_status},
            "on_track": 8,  # Demo value
            "at_risk": 2    # Demo value
        },
        "budget": {
            "total_allocated": round(total_budget, 2),
            "total_spent": round(total_spent, 2),
            "utilization_percentage": round(budget_utilization, 2),
            "remaining": round(total_budget - total_spent, 2)
        },
        "asset_alignment": {
            "total_assets_aligned": aligned_assets,
            "alignment_coverage": 85  # Demo percentage
        },
        "roi_metrics": {
            "total_expected_roi": round(total_expected_roi, 2),
            "roi_percentage": 250  # Demo: 250% ROI
        }
    }


@router.get("/business-goals")
def list_business_goals(db: Session = Depends(get_db)):
    """List all business goals with progress tracking"""
    goals = db.query(models.BusinessGoal).all()

    return {
        "goals": [
            {
                "goal_id": g.goal_id,
                "goal_name": g.goal_name,
                "description": g.description,
                "status": g.status,
                "priority": g.priority,
                "kpi_metric": g.kpi_metric,
                "current_value": g.current_value,
                "target_value": g.target_value,
                "progress_percentage": (g.current_value / g.target_value * 100) if g.target_value else 0,
                "target_date": g.target_date.isoformat() if g.target_date else None
            }
            for g in goals
        ]
    }


@router.get("/strategic-initiatives")
def list_strategic_initiatives(db: Session = Depends(get_db)):
    """
    List strategic DaaS initiatives
    Demonstrates cross-functional leadership and delivery
    """
    initiatives = db.query(models.StrategicInitiative).all()

    return {
        "initiatives": [
            {
                "initiative_id": i.initiative_id,
                "initiative_name": i.initiative_name,
                "description": i.description,
                "status": i.status,
                "budget_allocated": i.budget_allocated,
                "budget_spent": i.budget_spent,
                "budget_utilization": (i.budget_spent / i.budget_allocated * 100) if i.budget_allocated else 0,
                "expected_roi": i.expected_roi,
                "start_date": i.start_date.isoformat() if i.start_date else None,
                "target_date": i.target_date.isoformat() if i.target_date else None,
                "stakeholder_count": i.stakeholder_count
            }
            for i in initiatives
        ]
    }


@router.get("/asset-business-alignment")
def get_asset_business_alignment(db: Session = Depends(get_db)):
    """
    Show how data assets align with business goals
    Critical for demonstrating strategic value delivery
    """
    # This would join assets with business goals through alignment table
    # For now, return structure
    return {
        "alignments": [
            {
                "asset_name": "PROD-HR-DW-v1",
                "business_goal": "Improve HR decision-making speed",
                "contribution_level": "Critical",
                "value_delivered": "Reduced reporting time by 60%"
            },
            {
                "asset_name": "PROD-FIN-ETL-v2",
                "business_goal": "Automate financial reporting",
                "contribution_level": "High",
                "value_delivered": "Automated 15 manual processes"
            }
        ],
        "summary": {
            "total_alignments": 12,
            "critical_alignments": 5,
            "high_alignments": 4,
            "medium_alignments": 3
        }
    }


@router.get("/value-delivered")
def get_value_delivered_metrics(db: Session = Depends(get_db)):
    """
    Track value delivered through DaaS initiatives
    Key for demonstrating strategic impact
    """
    return {
        "overall_metrics": {
            "time_to_insight_reduction": "65%",
            "cost_savings_annual": "$2.3M",
            "processes_automated": 45,
            "stakeholder_satisfaction": "4.2/5.0",
            "data_quality_improvement": "78%"
        },
        "by_domain": [
            {
                "domain": "Finance",
                "value_delivered": "$850K cost savings",
                "key_achievement": "Automated month-end close process"
            },
            {
                "domain": "HR",
                "value_delivered": "60% faster hiring decisions",
                "key_achievement": "Real-time talent analytics"
            },
            {
                "domain": "Operations",
                "value_delivered": "40% inventory optimization",
                "key_achievement": "Predictive supply chain analytics"
            }
        ]
    }


# CRUD Operations for Business Goals

@router.post("/business-goals/", status_code=status.HTTP_201_CREATED)
def create_goal(goal: BusinessGoalCreate, db: Session = Depends(get_db)):
    """Create a new business goal"""
    new_goal = create_business_goal(goal, db)
    return {
        "goal_id": new_goal.goal_id,
        "goal_name": new_goal.goal_name,
        "status": new_goal.status,
        "message": "Business goal created successfully"
    }


@router.get("/business-goals/{goal_id}")
def get_goal(goal_id: int, db: Session = Depends(get_db)):
    """Get business goal by ID"""
    goal = get_business_goal(goal_id, db)
    return {
        "goal_id": goal.goal_id,
        "goal_name": goal.goal_name,
        "description": goal.description,
        "status": goal.status,
        "priority": goal.priority,
        "kpi_metric": goal.kpi_metric,
        "current_value": goal.current_value,
        "target_value": goal.target_value,
        "target_date": goal.target_date.isoformat() if goal.target_date else None
    }


@router.put("/business-goals/{goal_id}")
def update_goal(goal_id: int, goal_update: BusinessGoalUpdate, db: Session = Depends(get_db)):
    """Update business goal"""
    updated_goal = update_business_goal(goal_id, goal_update, db)
    return {
        "goal_id": updated_goal.goal_id,
        "goal_name": updated_goal.goal_name,
        "status": updated_goal.status,
        "message": "Business goal updated successfully"
    }


@router.delete("/business-goals/{goal_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_goal(goal_id: int, db: Session = Depends(get_db)):
    """Delete business goal"""
    delete_business_goal(goal_id, db)
    return None


# CRUD Operations for Strategic Initiatives

@router.post("/strategic-initiatives/", status_code=status.HTTP_201_CREATED)
def create_initiative(initiative: StrategicInitiativeCreate, db: Session = Depends(get_db)):
    """Create a new strategic initiative"""
    new_initiative = create_strategic_initiative(initiative, db)
    return {
        "initiative_id": new_initiative.initiative_id,
        "initiative_name": new_initiative.initiative_name,
        "status": new_initiative.status,
        "message": "Strategic initiative created successfully"
    }


@router.get("/strategic-initiatives/{initiative_id}")
def get_initiative(initiative_id: int, db: Session = Depends(get_db)):
    """Get strategic initiative by ID"""
    initiative = get_strategic_initiative(initiative_id, db)
    return {
        "initiative_id": initiative.initiative_id,
        "initiative_name": initiative.initiative_name,
        "description": initiative.description,
        "status": initiative.status,
        "budget_allocated": initiative.budget_allocated,
        "budget_spent": initiative.budget_spent,
        "expected_roi": initiative.expected_roi,
        "start_date": initiative.start_date.isoformat() if initiative.start_date else None,
        "target_date": initiative.target_date.isoformat() if initiative.target_date else None,
        "stakeholder_count": initiative.stakeholder_count
    }


@router.put("/strategic-initiatives/{initiative_id}")
def update_initiative(
    initiative_id: int,
    initiative_update: StrategicInitiativeUpdate,
    db: Session = Depends(get_db)
):
    """Update strategic initiative"""
    updated_initiative = update_strategic_initiative(initiative_id, initiative_update, db)
    return {
        "initiative_id": updated_initiative.initiative_id,
        "initiative_name": updated_initiative.initiative_name,
        "status": updated_initiative.status,
        "message": "Strategic initiative updated successfully"
    }


@router.delete("/strategic-initiatives/{initiative_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_initiative(initiative_id: int, db: Session = Depends(get_db)):
    """Delete strategic initiative"""
    delete_strategic_initiative(initiative_id, db)
    return None
