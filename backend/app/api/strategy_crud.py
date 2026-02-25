"""
CRUD Operations for Strategic Management
"""
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from datetime import date
from .. import models_extended as models


# Pydantic Schemas
class BusinessGoalCreate(BaseModel):
    goal_name: str
    description: Optional[str] = None
    owner_id: int
    target_date: Optional[date] = None
    status: str = "Active"
    kpi_metric: Optional[str] = None
    current_value: Optional[float] = None
    target_value: Optional[float] = None
    priority: Optional[str] = "Medium"


class BusinessGoalUpdate(BaseModel):
    goal_name: Optional[str] = None
    description: Optional[str] = None
    owner_id: Optional[int] = None
    target_date: Optional[date] = None
    status: Optional[str] = None
    kpi_metric: Optional[str] = None
    current_value: Optional[float] = None
    target_value: Optional[float] = None
    priority: Optional[str] = None


class StrategicInitiativeCreate(BaseModel):
    initiative_name: str
    description: Optional[str] = None
    business_goal_id: Optional[int] = None
    initiative_lead_id: Optional[int] = None
    budget_allocated: Optional[float] = None
    budget_spent: float = 0.0
    start_date: Optional[date] = None
    target_date: Optional[date] = None
    status: str = "Planning"
    expected_roi: Optional[float] = None
    stakeholder_count: int = 0


class StrategicInitiativeUpdate(BaseModel):
    initiative_name: Optional[str] = None
    description: Optional[str] = None
    business_goal_id: Optional[int] = None
    initiative_lead_id: Optional[int] = None
    budget_allocated: Optional[float] = None
    budget_spent: Optional[float] = None
    start_date: Optional[date] = None
    target_date: Optional[date] = None
    status: Optional[str] = None
    expected_roi: Optional[float] = None
    stakeholder_count: Optional[int] = None


# Business Goals CRUD
def create_business_goal(goal_data: BusinessGoalCreate, db: Session):
    """Create a new business goal"""
    new_goal = models.BusinessGoal(**goal_data.model_dump())
    db.add(new_goal)
    db.commit()
    db.refresh(new_goal)
    return new_goal


def get_business_goal(goal_id: int, db: Session):
    """Get business goal by ID"""
    goal = db.query(models.BusinessGoal).filter(models.BusinessGoal.goal_id == goal_id).first()
    if not goal:
        raise HTTPException(status_code=404, detail="Business goal not found")
    return goal


def update_business_goal(goal_id: int, goal_update: BusinessGoalUpdate, db: Session):
    """Update business goal"""
    goal = get_business_goal(goal_id, db)

    update_data = goal_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(goal, field, value)

    db.commit()
    db.refresh(goal)
    return goal


def delete_business_goal(goal_id: int, db: Session):
    """Delete business goal"""
    goal = get_business_goal(goal_id, db)
    db.delete(goal)
    db.commit()
    return None


# Strategic Initiatives CRUD
def create_strategic_initiative(initiative_data: StrategicInitiativeCreate, db: Session):
    """Create a new strategic initiative"""
    new_initiative = models.StrategicInitiative(**initiative_data.model_dump())
    db.add(new_initiative)
    db.commit()
    db.refresh(new_initiative)
    return new_initiative


def get_strategic_initiative(initiative_id: int, db: Session):
    """Get strategic initiative by ID"""
    initiative = db.query(models.StrategicInitiative).filter(
        models.StrategicInitiative.initiative_id == initiative_id
    ).first()
    if not initiative:
        raise HTTPException(status_code=404, detail="Strategic initiative not found")
    return initiative


def update_strategic_initiative(initiative_id: int, initiative_update: StrategicInitiativeUpdate, db: Session):
    """Update strategic initiative"""
    initiative = get_strategic_initiative(initiative_id, db)

    update_data = initiative_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(initiative, field, value)

    db.commit()
    db.refresh(initiative)
    return initiative


def delete_strategic_initiative(initiative_id: int, db: Session):
    """Delete strategic initiative"""
    initiative = get_strategic_initiative(initiative_id, db)
    db.delete(initiative)
    db.commit()
    return None
